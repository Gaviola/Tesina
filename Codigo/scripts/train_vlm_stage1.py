"""Fase 2: Etapa 1 - Alineamiento visual-textual con MM-Skin captions.

Entrena solo el MLP de proyección con pares imagen-caption de MM-Skin (~11k).
Vision encoder y LLM permanecen congelados.

Uso:
    python scripts/train_vlm_stage1.py --model llava_med
    python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1 --lr 2e-3
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from torch.utils.data import DataLoader

from src.data.mmskin import MMSkinDataset
from src.models.factory import build_model
from src.training.two_stage import VLMOOMError, VLMTrainCollator, run_stage1
from src.utils.device import (
    check_vram, estimate_vlm_batch_size, get_free_vram_gb, get_num_workers, get_vram_gb,
)
from src.utils.io import save_results
from src.utils.logging import log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

_VRAM_REQUIRED = {"llava_med": 14.0, "mini_vlm": 10.0}


def _find_or_create_splits(data_dir: Path, mmskin_dir: Path, all_names: list[str], seed: int) -> str:
    """Busca el archivo de splits de MM-Skin o lo crea si no existe.

    Orden de búsqueda:
    1. data/splits/mmskin_splits.json  (creado por prepare_data.py, splits 70/15/15)
    2. data/processed/MM-SkinQA/splits_mmskin.json  (fallback local)
    Si ninguno existe, crea el splits en data/splits/ con distribución 70/15/15.
    """
    import random

    candidates = [
        data_dir / "splits" / "mmskin_splits.json",
        mmskin_dir / "splits_mmskin.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            logger.info("Usando splits existentes: %s", candidate)
            return str(candidate)

    # Crear splits 70/15/15 en data/splits/
    splits_path = data_dir / "splits" / "mmskin_splits.json"
    splits_path.parent.mkdir(parents=True, exist_ok=True)

    set_seed(seed)
    shuffled = all_names[:]
    random.shuffle(shuffled)

    n = len(shuffled)
    n_train = int(0.70 * n)
    n_val = int(0.15 * n)

    splits = {
        "train": shuffled[:n_train],
        "val": shuffled[n_train:n_train + n_val],
        "test": shuffled[n_train + n_val:],
    }
    with open(splits_path, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)
    logger.info(
        "Splits creados: train=%d, val=%d, test=%d → %s",
        len(splits["train"]), len(splits["val"]), len(splits["test"]), splits_path,
    )
    return str(splits_path)


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
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num_workers", type=int, default=None)
    parser.add_argument(
        "--num_crops", type=int, default=1,
        help="Override num_crops para Phi-3.5 (default: 1 para Stage 1, reduce VRAM). "
             "Usar 4 para Stage 2 o evaluación con resolución completa.",
    )
    args = parser.parse_args()

    set_seed(args.seed)

    run_name = f"stage1_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
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
    logger.info("Modelo: %s | Épocas: %d | LR: %.0e", args.model, args.epochs, args.lr)

    # --- VRAM check (usar VRAM libre, no total, para detectar GPU compartida) ---
    check_vram(_VRAM_REQUIRED[args.model], args.model)
    free_vram = get_free_vram_gb()
    quantize = free_vram < _VRAM_REQUIRED[args.model]
    if quantize:
        logger.info("VRAM libre insuficiente (%.1f GB < %.1f GB requeridos). Activando cuantización 4-bit.",
                    free_vram, _VRAM_REQUIRED[args.model])

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
        effective_grad_accum = max(1, args.batch_size // suggested_bs)
    else:
        effective_batch_size = args.batch_size
        effective_grad_accum = 1

    # --- Dataset MM-Skin (caption mode) ---
    data_dir = Path(args.data_dir)
    mmskin_dir = data_dir / "processed" / "MM-SkinQA"
    if not mmskin_dir.exists():
        logger.error(
            "Directorio MM-Skin no encontrado: %s\n"
            "Ejecuta: python scripts/prepare_data.py --data_dir %s",
            mmskin_dir, args.data_dir,
        )
        sys.exit(1)

    # Resolver splits file (de prepare_data.py o crear uno nuevo)
    probe_ds = MMSkinDataset(root_dir=str(mmskin_dir), split="train", transform=None, mode="caption")
    all_image_names = [s["image_id"] for s in probe_ds.samples]
    splits_file = _find_or_create_splits(data_dir, mmskin_dir, all_image_names, args.seed)

    train_dataset = MMSkinDataset(
        root_dir=str(mmskin_dir), split="train",
        transform=None, splits_file=splits_file, mode="caption",
    )
    val_dataset = MMSkinDataset(
        root_dir=str(mmskin_dir), split="val",
        transform=None, splits_file=splits_file, mode="caption",
    )
    logger.info("Dataset MM-Skin caption — Train: %d | Val: %d", len(train_dataset), len(val_dataset))

    # --- Collator y DataLoaders ---
    collator = VLMTrainCollator(
        processor=model.processor,
        model_type=args.model,
        max_length=2048,
        mode="caption",
    )
    num_workers = args.num_workers if args.num_workers is not None else get_num_workers()

    # --- Configuración ---
    checkpoint_dir = str(output_dir / "checkpoints" / f"stage1_{args.model}")
    cfg = {
        "epochs": args.epochs,
        "lr": args.lr,
        "batch_size": effective_batch_size,
        "gradient_accumulation_steps": effective_grad_accum,
        "checkpoint_dir": checkpoint_dir,
    }

    # --- Entrenamiento con retry por OOM ---
    import torch
    current_batch_size = effective_batch_size
    grad_accum = effective_grad_accum
    train_loader, val_loader = _build_dataloaders(
        train_dataset, val_dataset, collator, current_batch_size, num_workers
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
                metrics = run_stage1(model, train_loader, val_loader, cfg)
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

    # --- Guardar resultados ---
    results_path = str(output_dir / "results" / f"stage1_{args.model}_metrics.json")
    save_results(metrics, results_path)
    logger.info("Métricas Stage 1 guardadas en %s", results_path)
    logger.info(
        "Stage 1 finalizado | Best epoch: %d | Best val_loss: %.4f",
        metrics["best_epoch"],
        min(metrics["val_loss"]) if metrics["val_loss"] else float("nan"),
    )


if __name__ == "__main__":
    main()
