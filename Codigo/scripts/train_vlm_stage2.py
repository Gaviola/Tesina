"""Fase 2: Etapa 2 - Ajuste de instrucciones con LoRA y MM-Skin VQA.

Aplica LoRA al LLM y entrena con los pares VQA de MM-Skin (~27k pares).
Usa MMSkinVQADataset para expandir imágenes → pares individuales (pregunta, respuesta).

Uso:
    python scripts/train_vlm_stage2.py --model llava_med
    python scripts/train_vlm_stage2.py --model mini_vlm --checkpoint outputs/checkpoints/stage1_mini_vlm/best_model.pt
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from torch.utils.data import DataLoader

from src.data.mmskin import MMSkinDataset
from src.models.factory import build_model
from src.training.two_stage import MMSkinVQADataset, VLMOOMError, VLMTrainCollator, run_stage2
from src.utils.device import (
    check_training_dependencies, check_vram, get_free_vram_gb, get_num_workers, get_vram_gb,
)
from src.utils.io import load_checkpoint, save_results
from src.utils.logging import log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

_VRAM_REQUIRED = {"llava_med": 14.0, "mini_vlm": 10.0}


def _build_dataloaders(train_dataset, val_dataset, collator, batch_size: int, num_workers: int):
    """Construye DataLoaders para train y val con el batch size dado.

    Separado en función para permitir reconstrucción con batch size reducido
    en caso de OOM durante el entrenamiento.
    """
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collator,
        num_workers=num_workers,
        pin_memory=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        collate_fn=collator,
        num_workers=num_workers,
        pin_memory=False,
    )
    return train_loader, val_loader


def main():
    parser = argparse.ArgumentParser(description="F2: Ajuste de instrucciones (Stage 2)")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--checkpoint", type=str, default=None, help="Checkpoint de Stage 1")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--grad_accum", type=int, default=8)
    parser.add_argument("--lora_r", type=int, default=64)
    parser.add_argument("--lora_alpha", type=int, default=128)
    parser.add_argument("--lora_dropout", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num_workers", type=int, default=None)
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Verificación local: carga modelo, aplica LoRA, procesa N batches, "
             "reporta VRAM y tiempos. No entrena el modelo completo.",
    )
    parser.add_argument(
        "--dry-run-batches", type=int, default=10, dest="dry_run_batches",
        help="Número de batches a procesar en modo dry-run (default: 10).",
    )
    args = parser.parse_args()

    # Dry-run: desactivar wandb
    if args.dry_run:
        args.wandb = False

    set_seed(args.seed)

    run_name = f"stage2_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(args.output_dir)

    setup_logger(
        run_name,
        log_dir=str(output_dir / "logs"),
        use_wandb=args.wandb,
        wandb_project="dermvlm-phase2",
        wandb_config=vars(args),
    )
    logger.info("=== Stage 2: Ajuste de instrucciones con LoRA ===")
    logger.info(
        "Modelo: %s | Épocas: %d | LR: %.0e | LoRA r=%d",
        args.model, args.epochs, args.lr, args.lora_r,
    )

    # --- VRAM check ---
    check_vram(_VRAM_REQUIRED[args.model], args.model)
    vram = get_vram_gb()
    quantize = vram < _VRAM_REQUIRED[args.model]
    if quantize:
        logger.info(
            "VRAM insuficiente (%.1f GB). Activando cuantización 4-bit.", vram
        )

    # --- Pre-flight: verificar dependencias antes de cargar modelo ---
    dep_status = check_training_dependencies(args.model, quantize)
    if quantize and not dep_status["bitsandbytes"]:
        logger.warning(
            "Pre-flight: bitsandbytes no disponible. Desactivando cuantización."
        )
        quantize = False

    # --- Modelo ---
    model = build_model({"name": args.model, "quantize": quantize})
    with log_time(f"Cargando {args.model}", logger):
        model.load_components()

    from src.utils.logging import log_gpu_memory
    log_gpu_memory(logger, prefix="Post-carga modelo | ")
    free_vram = get_free_vram_gb()
    logger.info("Modelo %s cargado | VRAM libre: %.2f GB", args.model, free_vram)
    if free_vram < 1.0:
        logger.warning(
            "VRAM libre muy baja (%.2f GB) tras cargar el modelo. "
            "Es probable que ocurra OOM durante el entrenamiento.",
            free_vram,
        )

    # --- Cargar checkpoint Stage 1 (opcional) ---
    if args.checkpoint:
        ckpt_path = Path(args.checkpoint)
        if not ckpt_path.exists():
            logger.error("Checkpoint no encontrado: %s", args.checkpoint)
            sys.exit(1)
        ckpt = load_checkpoint(str(ckpt_path), model=model)
        logger.info(
            "Checkpoint Stage 1 cargado desde %s (época %d)",
            args.checkpoint, ckpt.get("epoch", "?"),
        )
    else:
        logger.info("Sin checkpoint de Stage 1 — entrenando desde pesos preentrenados.")

    # --- Dataset MM-Skin (VQA mode → expandido) ---
    data_dir = Path(args.data_dir)
    mmskin_dir = data_dir / "processed" / "MM-SkinQA"
    if not mmskin_dir.exists():
        logger.error(
            "Directorio MM-Skin no encontrado: %s\n"
            "Ejecuta: python scripts/prepare_data.py --data_dir %s",
            mmskin_dir, args.data_dir,
        )
        sys.exit(1)

    # Buscar splits en data/splits/ o local
    splits_candidates = [
        data_dir / "splits" / "mmskin_splits.json",
        mmskin_dir / "splits_mmskin.json",
    ]
    splits_file_path = next((p for p in splits_candidates if p.exists()), None)
    if splits_file_path is None:
        logger.error(
            "Splits no encontrados. Ejecuta prepare_data.py o train_vlm_stage1.py primero."
        )
        sys.exit(1)
    splits_file = str(splits_file_path)

    train_base = MMSkinDataset(
        root_dir=str(mmskin_dir), split="train",
        transform=None, splits_file=splits_file, mode="vqa",
    )
    val_base = MMSkinDataset(
        root_dir=str(mmskin_dir), split="val",
        transform=None, splits_file=splits_file, mode="vqa",
    )

    train_dataset = MMSkinVQADataset(train_base)
    val_dataset = MMSkinVQADataset(val_base)
    logger.info(
        "Dataset MM-Skin VQA expandido — Train: %d pares | Val: %d pares",
        len(train_dataset), len(val_dataset),
    )

    # --- Collator y DataLoaders ---
    collator = VLMTrainCollator(
        processor=model.processor,
        model_type=args.model,
        max_length=2048,
        mode="vqa",
    )
    num_workers = args.num_workers if args.num_workers is not None else get_num_workers()

    # --- Configuración ---
    checkpoint_dir = str(output_dir / "checkpoints" / f"stage2_{args.model}")
    cfg = {
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": args.batch_size,
        "gradient_accumulation_steps": args.grad_accum,
        "checkpoint_dir": checkpoint_dir,
        "early_stopping_patience": 3,
        "lora": {
            "r": args.lora_r,
            "alpha": args.lora_alpha,
            "dropout": args.lora_dropout,
            "target_modules": ["q_proj", "v_proj"],
        },
    }

    # --- Entrenamiento con retry por OOM ---
    import torch
    current_batch_size = args.batch_size
    grad_accum = args.grad_accum
    max_batches = args.dry_run_batches if args.dry_run else None
    train_loader, val_loader = _build_dataloaders(
        train_dataset, val_dataset, collator, current_batch_size, num_workers
    )

    if args.dry_run:
        logger.info(
            "=== MODO DRY-RUN: procesando %d batches para validar el pipeline ===",
            args.dry_run_batches,
        )

    metrics = None
    while True:
        cfg["batch_size"] = current_batch_size
        cfg["gradient_accumulation_steps"] = grad_accum
        logger.info(
            "Iniciando entrenamiento | batch_size=%d | grad_accum=%d | batch efectivo=%d",
            current_batch_size, grad_accum, current_batch_size * grad_accum,
        )
        try:
            with log_time(f"Stage 2 {args.model}", logger):
                metrics = run_stage2(
                    model, train_loader, val_loader, cfg,
                    max_batches=max_batches,
                )
            break
        except VLMOOMError as e:
            torch.cuda.empty_cache()
            logger.warning("VLMOOMError capturado: %s", e)
            if current_batch_size <= 1:
                logger.error(
                    "OOM con batch_size=1 y gradient checkpointing activo. "
                    "Imposible continuar el entrenamiento en este hardware. "
                    "VRAM total: %.1f GB. Considera cuantización 4-bit o un nodo con más VRAM.",
                    get_vram_gb(),
                )
                sys.exit(1)
            prev_bs = current_batch_size
            current_batch_size = max(1, current_batch_size // 2)
            grad_accum = grad_accum * 2
            logger.warning(
                "Reduciendo batch_size: %d → %d | grad_accum: %d → %d "
                "(batch efectivo mantenido en ~%d)",
                prev_bs, current_batch_size,
                grad_accum // 2, grad_accum,
                current_batch_size * grad_accum,
            )
            train_loader, val_loader = _build_dataloaders(
                train_dataset, val_dataset, collator, current_batch_size, num_workers
            )

    # --- Dry-run: salir sin guardar resultados ---
    if args.dry_run:
        logger.info("=== Dry-run completado exitosamente ===")
        sys.exit(0)

    # --- Guardar resultados ---
    results_path = str(output_dir / "results" / f"stage2_{args.model}_metrics.json")
    save_results(metrics, results_path)
    logger.info("Métricas Stage 2 guardadas en %s", results_path)
    logger.info(
        "Stage 2 finalizado | Best epoch: %d | Best val_loss: %.4f",
        metrics["best_epoch"],
        min(metrics["val_loss"]) if metrics["val_loss"] else float("nan"),
    )


if __name__ == "__main__":
    main()
