"""Fase 2: Etapa 1 - Alineamiento visual-textual con SkinCaRe SkinCAP.

Entrena solo el MLP de proyección con pares imagen-caption de SkinCAP (~4k).
Vision encoder y LLM permanecen congelados.

Uso:
    python scripts/train_vlm_stage1.py --model llava_med
    python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1 --lr 2e-3
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from torch.utils.data import DataLoader

from src.data.skincare import SkinCaReDataset
from src.models.factory import build_model
from src.training.two_stage import VLMOOMError, VLMTrainCollator, run_stage1
from src.utils.device import (
    check_training_dependencies, check_vram, estimate_vlm_batch_size,
    get_free_vram_gb, get_num_workers, get_vram_gb,
)
from src.utils.io import save_results
from src.utils.logging import log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

_VRAM_REQUIRED = {"llava_med": 14.0, "mini_vlm": 12.0}
_VRAM_TRAIN_MARGIN = 4.0  # GB adicionales para optimizer, gradientes y activaciones


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
    parser = argparse.ArgumentParser(description="F2: Alineamiento visual-textual (Stage 1)")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--run-name", type=str, default=None, dest="run_name",
                        help="Nombre del run para wandb y sufijo del directorio de checkpoint. "
                             "Si no se pasa, se genera automáticamente con timestamp.")
    parser.add_argument("--num_workers", type=int, default=None)
    parser.add_argument(
        "--num_crops", type=int, default=1,
        help="Override num_crops para Phi-3.5 (default: 1 para Stage 1, reduce VRAM). "
             "Usar 4 para Stage 2 o evaluación con resolución completa.",
    )
    parser.add_argument(
        "--grad_accum", type=int, default=1,
        help="Gradient accumulation steps explícito (default: 1). "
             "Se multiplica con el auto-ajuste por VRAM si batch_size excede la estimación segura.",
    )
    parser.add_argument(
        "--early_stopping_patience", type=int, default=0,
        help="Épocas sin mejora en val_loss antes de detener (0 = desactivado).",
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run",
        help="Verificación local: carga modelo, procesa N batches, reporta VRAM y tiempos. "
             "No entrena el modelo completo.",
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

    run_name = args.run_name or f"stage1_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = Path(args.output_dir)
    log_dir = output_dir / "logs"

    setup_logger(
        run_name,
        log_dir=str(log_dir),
        use_wandb=args.wandb,
        wandb_project="dermvlm-phase2",
        wandb_config=vars(args),
    )
    logger.info("=== Stage 1: Alineamiento visual-textual ===")
    logger.info(
        "Modelo: %s | Épocas: %d | LR: %.0e | Grad accum: %d | ES patience: %d",
        args.model, args.epochs, args.lr, args.grad_accum, args.early_stopping_patience,
    )

    # --- VRAM check (usar VRAM libre, no total, para detectar GPU compartida) ---
    check_vram(_VRAM_REQUIRED[args.model], args.model)
    free_vram = get_free_vram_gb()
    quantize = free_vram < (_VRAM_REQUIRED[args.model] + _VRAM_TRAIN_MARGIN)
    if quantize:
        logger.info(
            "VRAM libre insuficiente para entrenamiento (%.1f GB < %.1f GB modelo + %.1f GB margen). "
            "Activando cuantización 4-bit.",
            free_vram, _VRAM_REQUIRED[args.model], _VRAM_TRAIN_MARGIN,
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
    load_kwargs = {}
    if args.model == "mini_vlm" and args.num_crops is not None:
        load_kwargs["num_crops"] = args.num_crops
    with log_time(f"Cargando {args.model}", logger):
        model.load_components(**load_kwargs)

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

    # --- Auto-estimación de batch size ---
    num_crops_effective = args.num_crops if args.model == "mini_vlm" else 4
    per_sample_est = 2.5 if args.model == "llava_med" else 2.0
    grad_ckpt_expected = free_vram < (args.batch_size * per_sample_est + 1.0)
    suggested_bs = estimate_vlm_batch_size(
        model_type=args.model,
        free_vram_gb=free_vram,
        num_crops=num_crops_effective,
        grad_checkpointing=grad_ckpt_expected,
    )
    if args.batch_size > suggested_bs:
        logger.warning(
            "Batch size solicitado (%d) excede estimación segura (%d) "
            "para %.2f GB de VRAM libre. Reduciendo a %d y ajustando grad_accum.",
            args.batch_size, suggested_bs, free_vram, suggested_bs,
        )
        effective_batch_size = suggested_bs
        effective_grad_accum = max(1, args.batch_size // suggested_bs) * args.grad_accum
    else:
        effective_batch_size = args.batch_size
        effective_grad_accum = args.grad_accum

    # --- Dataset SkinCaRe SkinCAP (Stage 1: alineamiento visual-textual) ---
    data_dir = Path(args.data_dir)
    skincare_dir = data_dir / "raw" / "skincare"
    if not skincare_dir.exists():
        logger.error(
            "Directorio SkinCaRe no encontrado: %s\n"
            "Descargá el dataset con: python scripts/prepare_data.py --download-skincare --data_dir %s",
            skincare_dir, args.data_dir,
        )
        sys.exit(1)

    splits_candidates = [
        data_dir / "splits" / "skincare_skincap_splits.json",
        skincare_dir / "skincare_skincap_splits.json",
    ]
    splits_file = next((str(p) for p in splits_candidates if p.exists()), None)
    if splits_file is None:
        logger.error(
            "Splits de SkinCAP no encontrados. Ejecutá: python scripts/prepare_data.py --data_dir %s",
            args.data_dir,
        )
        sys.exit(1)

    train_dataset = SkinCaReDataset(
        root_dir=str(skincare_dir), split="train",
        transform=None, splits_file=splits_file, subset="skincap",
    )
    val_dataset = SkinCaReDataset(
        root_dir=str(skincare_dir), split="val",
        transform=None, splits_file=splits_file, subset="skincap",
    )
    logger.info("Dataset SkinCAP — Train: %d | Val: %d", len(train_dataset), len(val_dataset))

    # --- Collator y DataLoaders ---
    collator = VLMTrainCollator(
        processor=model.processor,
        model_type=args.model,
        max_length=2048,
        mode="caption",
    )
    num_workers = args.num_workers if args.num_workers is not None else get_num_workers()

    # --- Configuración ---
    ckpt_subdir = f"stage1_{args.model}_{args.run_name}" if args.run_name else f"stage1_{args.model}"
    checkpoint_dir = str(output_dir / "checkpoints" / ckpt_subdir)
    cfg = {
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": effective_batch_size,
        "gradient_accumulation_steps": effective_grad_accum,
        "checkpoint_dir": checkpoint_dir,
        "early_stopping_patience": args.early_stopping_patience,
    }

    # --- Entrenamiento con retry por OOM ---
    import torch
    current_batch_size = effective_batch_size
    grad_accum = effective_grad_accum
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
            with log_time(f"Stage 1 {args.model}", logger):
                metrics = run_stage1(
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
    results_path = str(output_dir / "results" / args.model / "stage1_metrics.json")
    save_results(metrics, results_path)
    logger.info("Métricas Stage 1 guardadas en %s", results_path)

    # --- Guardar hiperparámetros junto al checkpoint (para reproducibilidad del sweep) ---
    if args.run_name:
        import json as _json
        sweep_cfg_path = Path(checkpoint_dir) / "sweep_config.json"
        sweep_cfg = {k: v for k, v in vars(args).items() if k not in ("wandb", "dry_run", "dry_run_batches")}
        sweep_cfg["best_val_loss"] = min(metrics["val_loss"]) if metrics["val_loss"] else None
        sweep_cfg["best_epoch"] = metrics["best_epoch"]
        with open(sweep_cfg_path, "w", encoding="utf-8") as f:
            _json.dump(sweep_cfg, f, indent=2)
        logger.info("Hiperparámetros del sweep guardados en %s", sweep_cfg_path)
    logger.info(
        "Stage 1 finalizado | Best epoch: %d | Best val_loss: %.4f",
        metrics["best_epoch"],
        min(metrics["val_loss"]) if metrics["val_loss"] else float("nan"),
    )


if __name__ == "__main__":
    main()
