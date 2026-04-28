"""Fase 1: Entrenamiento de clasificadores (DenseNet121 / ViT-B/16).

Uso:
    python scripts/train_classifier.py --model densenet --config configs/phase1_classification.yaml
    python scripts/train_classifier.py --model vit --config configs/phase1_classification.yaml
"""

import argparse
import logging
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.collators import ClassificationCollator, MixupCutmixCollator
from src.data.ham10000 import HAM10000Dataset
from src.data.hiba import HIBADataset
from src.data.transforms import get_train_transforms, get_val_transforms
from src.evaluation.classification import evaluate_classification
from src.evaluation.tta import evaluate_with_tta
from src.models.factory import build_model
from src.training.callbacks import CheckpointCallback, EarlyStopping
from src.training.losses import build_loss
from src.training.optim_groups import (
    freeze_backbone,
    get_head_params,
    get_llrd_groups,
    unfreeze_all,
)
from src.training.recipes import RECIPES, get_recipe
from src.training.schedulers import build_scheduler
from src.training.trainer import Trainer
from src.utils.device import get_device, get_num_workers, get_training_dtype
from src.utils.io import save_results
from src.utils.logging import format_duration, log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)


def compute_class_weights(dataset: HAM10000Dataset, num_classes: int = 7) -> torch.Tensor:
    """Calcula pesos inversamente proporcionales a la frecuencia de cada clase."""
    label_counts = Counter(sample["label"] for sample in dataset.samples)
    total = sum(label_counts.values())
    weights = []
    for i in range(num_classes):
        count = label_counts.get(i, 1)
        weights.append(total / (num_classes * count))
    return torch.tensor(weights, dtype=torch.float32)


def evaluate_on_split(model, dataloader, device, dtype, num_classes):
    """Evalúa el modelo en un split y retorna predicciones, labels y probabilidades."""
    model.eval()
    all_preds = []
    all_labels = []
    all_probs = []
    use_amp = dtype in (torch.float16, torch.bfloat16) and device.type == "cuda"

    with torch.no_grad():
        for batch in dataloader:
            images = batch["image"].to(device)
            labels = batch["label"]

            with torch.amp.autocast("cuda", dtype=dtype, enabled=use_amp):
                outputs = model(images)

            probs = torch.softmax(outputs, dim=1).float().cpu().numpy()
            preds = outputs.argmax(dim=1).cpu().tolist()

            all_preds.extend(preds)
            all_labels.extend(labels.tolist())
            all_probs.append(probs)

    all_probs = np.concatenate(all_probs, axis=0)
    return all_preds, all_labels, all_probs


def main():
    parser = argparse.ArgumentParser(description="F1: Entrenamiento de clasificadores")
    parser.add_argument("--model", type=str, required=True,
                        choices=["densenet", "vit", "convnext_tiny", "swin_tiny"])
    parser.add_argument("--run-name", type=str, default=None, dest="run_name",
                        help="Sufijo para output files y checkpoint dir. Default = --model. "
                             "Útil cuando se corre el mismo modelo con recipes distintos "
                             "(ej: --run-name densenet_modern vs --run-name densenet_legacy).")
    parser.add_argument("--data-dir", type=str, default="data", dest="data_dir")
    parser.add_argument("--output-dir", type=str, default="outputs", dest="output_dir")
    parser.add_argument("--splits-file", type=str, default=None, dest="splits_file")
    parser.add_argument("--epochs", type=int, default=None,
                        help="Override de epochs del recipe (legacy=30, modern=40).")
    parser.add_argument("--batch-size", type=int, default=None, dest="batch_size")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=None, dest="weight_decay",
                        help="Override de weight_decay del recipe (legacy=0.01, modern=0.05).")
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num-workers", type=int, default=None, dest="num_workers")
    parser.add_argument("--scheduler", type=str, default="CosineAnnealingLR",
                        choices=["CosineAnnealingLR", "none"])
    parser.add_argument("--recipe", type=str, default="legacy",
                        choices=list(RECIPES),
                        help="Preset de hiperparámetros. 'legacy' reproduce el comportamiento "
                             "previo a las mejoras de Fase 1; 'modern' activa el pack completo. "
                             "Las flags individuales sobreescriben los defaults del recipe.")
    parser.add_argument("--label-smoothing", type=float, default=None, dest="label_smoothing",
                        help="Override de label_smoothing del recipe.")
    parser.add_argument("--warmup-epochs", type=int, default=None, dest="warmup_epochs",
                        help="Override de warmup_epochs del recipe.")
    # Augmentations (Fase 2)
    aug_group = parser.add_mutually_exclusive_group()
    aug_group.add_argument("--randaugment", action="store_const", const=True,
                           default=None, dest="randaugment")
    aug_group.add_argument("--no-randaugment", action="store_const", const=False,
                           dest="randaugment")
    parser.add_argument("--randaugment-n", type=int, default=None, dest="randaugment_n")
    parser.add_argument("--randaugment-m", type=int, default=None, dest="randaugment_m")
    parser.add_argument("--random-erasing", type=float, default=None, dest="random_erasing",
                        help="Probabilidad de RandomErasing. 0 = off.")
    rrc_group = parser.add_mutually_exclusive_group()
    rrc_group.add_argument("--random-resized-crop", action="store_const", const=True,
                           default=None, dest="random_resized_crop")
    rrc_group.add_argument("--no-random-resized-crop", action="store_const", const=False,
                           dest="random_resized_crop")
    parser.add_argument("--rrc-scale-min", type=float, default=None, dest="rrc_scale_min")
    # MixUp / CutMix (Fase 2)
    parser.add_argument("--mixup-alpha", type=float, default=None, dest="mixup_alpha",
                        help="Alpha de la beta dist para MixUp. 0 = off.")
    parser.add_argument("--cutmix-alpha", type=float, default=None, dest="cutmix_alpha",
                        help="Alpha de la beta dist para CutMix. 0 = off.")
    parser.add_argument("--mixup-prob", type=float, default=None, dest="mixup_prob",
                        help="P(mixup) cuando ambas alphas > 0. 1-p para cutmix.")
    # Loss (Fase 2)
    parser.add_argument("--focal-gamma", type=float, default=None, dest="focal_gamma",
                        help="Gamma de Focal Loss. 0 = CrossEntropy estándar.")
    # Fase 3: two-stage + LLRD + TTA + HIBA
    ts_group = parser.add_mutually_exclusive_group()
    ts_group.add_argument("--two-stage", action="store_const", const=True,
                          default=None, dest="two_stage")
    ts_group.add_argument("--no-two-stage", action="store_const", const=False,
                          dest="two_stage")
    parser.add_argument("--llrd", type=float, default=None, dest="llrd",
                        help="Layer-wise LR decay factor (0,1]. 1.0 = LLRD off.")
    tta_group = parser.add_mutually_exclusive_group()
    tta_group.add_argument("--tta", action="store_const", const=True,
                           default=None, dest="tta")
    tta_group.add_argument("--no-tta", action="store_const", const=False,
                           dest="tta")
    parser.add_argument("--eval-hiba", action="store_true", dest="eval_hiba",
                        help="Tras eval en HAM10000 test, eval cross-dataset en HIBA.")
    parser.add_argument("--hiba-data-dir", type=str, default=None, dest="hiba_data_dir",
                        help="Directorio raíz de HIBA. Default: <data-dir>/processed/HIBA.")
    freeze_group = parser.add_mutually_exclusive_group()
    freeze_group.add_argument("--freeze-backbone", action="store_true", default=True,
                              dest="freeze_backbone")
    freeze_group.add_argument("--no-freeze-backbone", action="store_false",
                              dest="freeze_backbone")
    args = parser.parse_args()

    # Resolver recipe + overrides CLI. CLI > recipe.
    recipe = get_recipe(args.recipe)
    if args.epochs is None:
        args.epochs = recipe.epochs
    if args.weight_decay is None:
        args.weight_decay = 0.01 if recipe.weight_decay is None else recipe.weight_decay
    if args.label_smoothing is None:
        args.label_smoothing = recipe.label_smoothing
    if args.warmup_epochs is None:
        args.warmup_epochs = recipe.warmup_epochs
    # Fase 2 fields
    if args.randaugment is None:
        args.randaugment = recipe.randaugment
    if args.randaugment_n is None:
        args.randaugment_n = recipe.randaugment_n
    if args.randaugment_m is None:
        args.randaugment_m = recipe.randaugment_m
    if args.random_erasing is None:
        args.random_erasing = recipe.random_erasing
    if args.random_resized_crop is None:
        args.random_resized_crop = recipe.random_resized_crop
    if args.rrc_scale_min is None:
        args.rrc_scale_min = recipe.rrc_scale_min
    if args.mixup_alpha is None:
        args.mixup_alpha = recipe.mixup_alpha
    if args.cutmix_alpha is None:
        args.cutmix_alpha = recipe.cutmix_alpha
    if args.mixup_prob is None:
        args.mixup_prob = recipe.mixup_prob
    if args.focal_gamma is None:
        args.focal_gamma = recipe.focal_gamma
    # Fase 3 fields
    if args.two_stage is None:
        args.two_stage = recipe.two_stage
    if args.llrd is None:
        args.llrd = recipe.llrd
    if args.tta is None:
        args.tta = recipe.tta
    if args.run_name is None:
        args.run_name = args.model

    script_start = time.perf_counter()

    # 1. Reproducibilidad
    set_seed(args.seed)

    if args.num_workers is None:
        args.num_workers = get_num_workers()

    # 2. Logger
    log_dir = str(Path(args.output_dir) / "logs")
    setup_logger(
        name=f"train_{args.run_name}",
        log_dir=log_dir,
        use_wandb=args.wandb,
        wandb_project="dermvlm",
        wandb_config=vars(args),
    )
    logger.info("Iniciando entrenamiento de %s (run_name=%s)", args.model, args.run_name)
    logger.info(
        "Recipe: %s | epochs=%d | label_smoothing=%.3f | warmup_epochs=%d | weight_decay=%.4f",
        args.recipe, args.epochs, args.label_smoothing, args.warmup_epochs, args.weight_decay,
    )
    logger.info(
        "Augs: randaugment=%s (n=%d, m=%d) | random_erasing=%.2f | rrc=%s (scale_min=%.2f)",
        args.randaugment, args.randaugment_n, args.randaugment_m,
        args.random_erasing, args.random_resized_crop, args.rrc_scale_min,
    )
    logger.info(
        "Mixup/CutMix: mixup_alpha=%.2f | cutmix_alpha=%.2f | mixup_prob=%.2f | focal_gamma=%.2f",
        args.mixup_alpha, args.cutmix_alpha, args.mixup_prob, args.focal_gamma,
    )
    logger.info(
        "Procedure: two_stage=%s | llrd=%.3f | tta=%s | eval_hiba=%s",
        args.two_stage, args.llrd, args.tta, args.eval_hiba,
    )

    # 3. Device y dtype
    device = get_device()
    dtype = get_training_dtype()
    logger.info("Dispositivo: %s | dtype: %s", device, dtype)

    # 4. Splits
    splits_file = args.splits_file
    if splits_file is None:
        splits_file = str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    if not Path(splits_file).exists():
        logger.error("Archivo de splits no encontrado: %s", splits_file)
        logger.error("Ejecutar primero: python scripts/prepare_data.py")
        sys.exit(1)
    logger.info("Usando splits: %s", splits_file)

    # 5. Datasets
    data_root = str(Path(args.data_dir) / "processed" / "HAM10000")
    train_tfm = get_train_transforms(
        size=224,
        randaugment=args.randaugment,
        randaugment_n=args.randaugment_n,
        randaugment_m=args.randaugment_m,
        random_erasing=args.random_erasing,
        random_resized_crop=args.random_resized_crop,
        rrc_scale_min=args.rrc_scale_min,
    )
    # En modern (RandomResizedCrop activo) usamos también center-crop en val/test
    # para alinear el campo visual.
    val_tfm = get_val_transforms(size=224, center_crop=args.random_resized_crop)
    with log_time("Cargando datasets HAM10000", logger):
        train_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="train",
            transform=train_tfm,
            splits_file=splits_file,
        )
        val_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="val",
            transform=val_tfm,
            splits_file=splits_file,
        )
        test_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="test",
            transform=val_tfm,
            splits_file=splits_file,
        )
    logger.info(
        "Datasets cargados - train: %d, val: %d, test: %d",
        len(train_dataset), len(val_dataset), len(test_dataset),
    )

    # 6. DataLoaders
    batch_size = args.batch_size
    if batch_size is None:
        # Defaults: DenseNet/ConvNeXt = 32 (CNN, menor footprint), ViT/Swin = 16 (transformers).
        batch_size = 32 if args.model in ("densenet", "convnext_tiny") else 16
    pin_memory = device.type == "cuda"
    use_persistent = args.num_workers > 0
    prefetch = 2 if use_persistent else None
    base_collator = ClassificationCollator()
    if args.mixup_alpha > 0 or args.cutmix_alpha > 0:
        train_collator = MixupCutmixCollator(
            num_classes=7,
            mixup_alpha=args.mixup_alpha,
            cutmix_alpha=args.cutmix_alpha,
            mixup_prob=args.mixup_prob,
            base_collator=base_collator,
            rng_seed=args.seed,
        )
        logger.info("Train collator: MixupCutmix (alphas=%.2f/%.2f, p=%.2f)",
                    args.mixup_alpha, args.cutmix_alpha, args.mixup_prob)
    else:
        train_collator = base_collator
    logger.info("DataLoader workers: %d | persistent: %s", args.num_workers, use_persistent)
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        collate_fn=train_collator, num_workers=args.num_workers, pin_memory=pin_memory,
        persistent_workers=use_persistent, prefetch_factor=prefetch,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=base_collator, num_workers=args.num_workers, pin_memory=pin_memory,
        persistent_workers=use_persistent, prefetch_factor=prefetch,
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=base_collator, num_workers=args.num_workers, pin_memory=pin_memory,
        persistent_workers=use_persistent, prefetch_factor=prefetch,
    )

    # 7. Modelo
    num_classes = 7
    with log_time("Construyendo modelo %s" % args.model, logger):
        model = build_model({
            "name": args.model,
            "num_classes": num_classes,
            "pretrained": True,
            "freeze_backbone": args.freeze_backbone,
        })
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    logger.info("Modelo: %s | Parámetros: %d total, %d entrenables", args.model, total_params, trainable)

    # 8. Loss (compartido entre stages)
    class_weights = compute_class_weights(train_dataset, num_classes).to(device)
    logger.info("Class weights: %s", class_weights.tolist())
    criterion = build_loss(
        focal_gamma=args.focal_gamma,
        class_weights=class_weights,
        label_smoothing=args.label_smoothing,
    )
    logger.info("Loss: %s", type(criterion).__name__)

    # 9. Callbacks (estado compartido entre stages)
    checkpoint_dir = str(Path(args.output_dir) / "checkpoints" / args.run_name)
    callbacks = [
        EarlyStopping(patience=args.patience, monitor="val_f1", mode="max"),
        CheckpointCallback(monitor="val_f1", mode="max"),
    ]

    # 10. Orquestación: single-stage o two-stage
    if args.two_stage:
        if args.epochs < 2:
            logger.error("two_stage requiere epochs >= 2 (recibido %d)", args.epochs)
            sys.exit(1)

        logger.info("=== Stage 1: head-only training (1 epoch) ===")
        freeze_backbone(model, args.model)
        head_params = get_head_params(model, args.model)
        opt_s1 = AdamW(head_params, lr=args.lr, weight_decay=args.weight_decay)
        trainer_s1 = Trainer(
            model=model,
            optimizer=opt_s1,
            criterion=criterion,
            train_loader=train_loader,
            val_loader=val_loader,
            scheduler=None,
            device=device,
            dtype=dtype,
            max_epochs=1,
            callbacks=callbacks,
            checkpoint_dir=checkpoint_dir,
        )
        trainer_s1.fit()

        logger.info("=== Stage 2: full fine-tune con LLRD=%.3f ===", args.llrd)
        unfreeze_all(model)
        groups = get_llrd_groups(
            model, args.model,
            base_lr=args.lr,
            weight_decay=args.weight_decay,
            decay=args.llrd,
        )
        for g in groups:
            logger.info("  group %-12s n_params=%d lr=%.2e", g["name"], len(g["params"]), g["lr"])
        opt_s2 = AdamW(groups)
        warmup_s2 = min(args.warmup_epochs, max(0, args.epochs - 2))
        sched_s2 = build_scheduler(
            name=args.scheduler,
            optimizer=opt_s2,
            total_epochs=args.epochs - 1,
            warmup_epochs=warmup_s2,
        )
        trainer_s2 = Trainer(
            model=model,
            optimizer=opt_s2,
            criterion=criterion,
            train_loader=train_loader,
            val_loader=val_loader,
            scheduler=sched_s2,
            device=device,
            dtype=dtype,
            max_epochs=args.epochs,
            callbacks=callbacks,
            checkpoint_dir=checkpoint_dir,
        )
        best_metrics = trainer_s2.fit(start_epoch=1)
    else:
        optimizer = AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=args.lr,
            weight_decay=args.weight_decay,
        )
        scheduler = build_scheduler(
            name=args.scheduler,
            optimizer=optimizer,
            total_epochs=args.epochs,
            warmup_epochs=args.warmup_epochs,
        )
        trainer = Trainer(
            model=model,
            optimizer=optimizer,
            criterion=criterion,
            train_loader=train_loader,
            val_loader=val_loader,
            scheduler=scheduler,
            device=device,
            dtype=dtype,
            max_epochs=args.epochs,
            callbacks=callbacks,
            checkpoint_dir=checkpoint_dir,
        )
        logger.info("Iniciando entrenamiento por %d épocas", args.epochs)
        best_metrics = trainer.fit()
    logger.info("Entrenamiento finalizado. Mejores métricas: %s", best_metrics)

    # 11. Evaluación en HAM10000 test set
    eval_start = time.perf_counter()
    if args.tta:
        logger.info("Evaluando en test set con TTA (h-flip)...")
        y_pred, y_true, y_prob = evaluate_with_tta(
            model, test_loader, device, dtype, num_classes,
            tta_modes=("original", "hflip"),
        )
    else:
        logger.info("Evaluando en test set...")
        y_pred, y_true, y_prob = evaluate_on_split(model, test_loader, device, dtype, num_classes)
    logger.info("Evaluación en test set completada en %s", format_duration(time.perf_counter() - eval_start))

    class_names = train_dataset.get_class_names()
    test_results = evaluate_classification(y_true, y_pred, y_prob, class_names)
    logger.info("=== Resultados en Test ===")
    logger.info("Accuracy: %.4f", test_results["accuracy"])
    logger.info("F1 (weighted): %.4f", test_results["f1_weighted"])
    logger.info("AUC-ROC (macro): %s", test_results["auc_roc_macro"])
    logger.info("Sensibilidad (macro): %.4f", test_results["sensitivity_macro"])
    logger.info("Especificidad (macro): %.4f", test_results["specificity_macro"])

    # 12. Guardar resultados
    results_dir = Path(args.output_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Guardar métricas
    save_results(
        {
            "model": args.model,
            "run_name": args.run_name,
            "recipe": args.recipe,
            "accuracy": test_results["accuracy"],
            "f1_weighted": test_results["f1_weighted"],
            "auc_roc_macro": test_results["auc_roc_macro"],
            "sensitivity_macro": test_results["sensitivity_macro"],
            "specificity_macro": test_results["specificity_macro"],
            "sensitivity_per_class": test_results["sensitivity_per_class"],
            "specificity_per_class": test_results["specificity_per_class"],
            "confusion_matrix": test_results["confusion_matrix"],
        },
        str(results_dir / f"{args.run_name}_test_results.json"),
    )

    # Guardar predicciones para evaluate_classify.py
    predictions = {
        "model": args.model,
        "run_name": args.run_name,
        "y_true": y_true,
        "y_pred": y_pred,
        "y_prob": y_prob.tolist(),
        "class_names": class_names,
    }
    save_results(predictions, str(results_dir / f"{args.run_name}_predictions.json"))

    # 13. Evaluación cross-dataset en HIBA (OOD)
    if args.eval_hiba:
        hiba_root = args.hiba_data_dir
        if hiba_root is None:
            for candidate in [
                Path(args.data_dir) / "processed" / "HIBA",
                Path(args.data_dir) / "raw" / "HIBA",
            ]:
                if (candidate / "metadata.csv").exists():
                    hiba_root = str(candidate)
                    break
        if hiba_root is None or not (Path(hiba_root) / "metadata.csv").exists():
            logger.error("HIBA metadata.csv no encontrado. Skipping eval HIBA.")
        else:
            logger.info("Cargando HIBA para eval OOD: %s", hiba_root)
            hiba_dataset = HIBADataset(
                root_dir=hiba_root,
                split="train",  # ignorado cuando no hay splits_file
                transform=val_tfm,
                ham10000_mapping=True,
            )
            logger.info("HIBA: %d muestras tras mapeo a 7-clase HAM10000", len(hiba_dataset))
            hiba_loader = DataLoader(
                hiba_dataset, batch_size=batch_size, shuffle=False,
                collate_fn=base_collator, num_workers=args.num_workers, pin_memory=pin_memory,
                persistent_workers=use_persistent, prefetch_factor=prefetch,
            )
            hiba_eval_start = time.perf_counter()
            if args.tta:
                logger.info("Evaluando HIBA con TTA (h-flip)...")
                y_pred_h, y_true_h, y_prob_h = evaluate_with_tta(
                    model, hiba_loader, device, dtype, num_classes,
                    tta_modes=("original", "hflip"),
                )
            else:
                logger.info("Evaluando HIBA...")
                y_pred_h, y_true_h, y_prob_h = evaluate_on_split(
                    model, hiba_loader, device, dtype, num_classes,
                )
            logger.info(
                "Evaluación HIBA completada en %s",
                format_duration(time.perf_counter() - hiba_eval_start),
            )

            hiba_results = evaluate_classification(y_true_h, y_pred_h, y_prob_h, class_names)
            logger.info("=== Resultados en HIBA (OOD) ===")
            logger.info("Accuracy: %.4f", hiba_results["accuracy"])
            logger.info("F1 (weighted): %.4f", hiba_results["f1_weighted"])
            logger.info("AUC-ROC (macro): %s", hiba_results["auc_roc_macro"])
            logger.info("Sensibilidad (macro): %.4f", hiba_results["sensitivity_macro"])
            logger.info("Especificidad (macro): %.4f", hiba_results["specificity_macro"])

            save_results(
                {
                    "model": args.model,
                    "run_name": args.run_name,
                    "recipe": args.recipe,
                    "dataset": "HIBA",
                    "tta": args.tta,
                    "n_samples": len(hiba_dataset),
                    "accuracy": hiba_results["accuracy"],
                    "f1_weighted": hiba_results["f1_weighted"],
                    "auc_roc_macro": hiba_results["auc_roc_macro"],
                    "sensitivity_macro": hiba_results["sensitivity_macro"],
                    "specificity_macro": hiba_results["specificity_macro"],
                    "sensitivity_per_class": hiba_results["sensitivity_per_class"],
                    "specificity_per_class": hiba_results["specificity_per_class"],
                    "confusion_matrix": hiba_results["confusion_matrix"],
                },
                str(results_dir / f"{args.run_name}_test_results_hiba.json"),
            )
            save_results(
                {
                    "model": args.model,
                    "run_name": args.run_name,
                    "dataset": "HIBA",
                    "y_true": y_true_h,
                    "y_pred": y_pred_h,
                    "y_prob": y_prob_h.tolist(),
                    "class_names": class_names,
                },
                str(results_dir / f"{args.run_name}_predictions_hiba.json"),
            )

    logger.info("Resultados guardados en %s", results_dir)
    logger.info("Ejecución total: %s", format_duration(time.perf_counter() - script_start))


if __name__ == "__main__":
    main()
