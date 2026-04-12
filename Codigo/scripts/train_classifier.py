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
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.collators import ClassificationCollator
from src.data.ham10000 import HAM10000Dataset
from src.data.transforms import get_train_transforms, get_val_transforms
from src.evaluation.classification import evaluate_classification
from src.models.factory import build_model
from src.training.callbacks import CheckpointCallback, EarlyStopping
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
    parser.add_argument("--model", type=str, required=True, choices=["densenet", "vit"])
    parser.add_argument("--data-dir", type=str, default="data", dest="data_dir")
    parser.add_argument("--output-dir", type=str, default="outputs", dest="output_dir")
    parser.add_argument("--splits-file", type=str, default=None, dest="splits_file")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=None, dest="batch_size")
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=0.01, dest="weight_decay")
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num-workers", type=int, default=None, dest="num_workers")
    parser.add_argument("--scheduler", type=str, default="CosineAnnealingLR",
                        choices=["CosineAnnealingLR", "none"])
    parser.add_argument("--label-smoothing", type=float, default=0.0, dest="label_smoothing")
    freeze_group = parser.add_mutually_exclusive_group()
    freeze_group.add_argument("--freeze-backbone", action="store_true", default=True,
                              dest="freeze_backbone")
    freeze_group.add_argument("--no-freeze-backbone", action="store_false",
                              dest="freeze_backbone")
    args = parser.parse_args()

    script_start = time.perf_counter()

    # 1. Reproducibilidad
    set_seed(args.seed)

    if args.num_workers is None:
        args.num_workers = get_num_workers()

    # 2. Logger
    log_dir = str(Path(args.output_dir) / "logs")
    run_name = f"train_{args.model}"
    setup_logger(
        name=run_name,
        log_dir=log_dir,
        use_wandb=args.wandb,
        wandb_project="dermvlm",
        wandb_config=vars(args),
    )
    logger.info("Iniciando entrenamiento de %s", args.model)

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
    with log_time("Cargando datasets HAM10000", logger):
        train_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="train",
            transform=get_train_transforms(224),
            splits_file=splits_file,
        )
        val_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="val",
            transform=get_val_transforms(224),
            splits_file=splits_file,
        )
        test_dataset = HAM10000Dataset(
            root_dir=data_root,
            split="test",
            transform=get_val_transforms(224),
            splits_file=splits_file,
        )
    logger.info(
        "Datasets cargados - train: %d, val: %d, test: %d",
        len(train_dataset), len(val_dataset), len(test_dataset),
    )

    # 6. DataLoaders
    batch_size = args.batch_size
    if batch_size is None:
        batch_size = 32 if args.model == "densenet" else 16
    pin_memory = device.type == "cuda"
    use_persistent = args.num_workers > 0
    prefetch = 2 if use_persistent else None
    collator = ClassificationCollator()
    logger.info("DataLoader workers: %d | persistent: %s", args.num_workers, use_persistent)
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        collate_fn=collator, num_workers=args.num_workers, pin_memory=pin_memory,
        persistent_workers=use_persistent, prefetch_factor=prefetch,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=collator, num_workers=args.num_workers, pin_memory=pin_memory,
        persistent_workers=use_persistent, prefetch_factor=prefetch,
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=collator, num_workers=args.num_workers, pin_memory=pin_memory,
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

    # 8. Optimizer, scheduler, criterion
    optimizer = AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )
    if args.scheduler == "CosineAnnealingLR":
        scheduler = CosineAnnealingLR(optimizer, T_max=args.epochs)
    else:
        scheduler = None

    class_weights = compute_class_weights(train_dataset, num_classes).to(device)
    logger.info("Class weights: %s", class_weights.tolist())
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=args.label_smoothing)

    # 9. Callbacks
    checkpoint_dir = str(Path(args.output_dir) / "checkpoints" / args.model)
    callbacks = [
        EarlyStopping(patience=args.patience, monitor="val_f1", mode="max"),
        CheckpointCallback(monitor="val_f1", mode="max"),
    ]

    # 10. Trainer
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

    # 11. Evaluación en test set
    eval_start = time.perf_counter()
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
            "accuracy": test_results["accuracy"],
            "f1_weighted": test_results["f1_weighted"],
            "auc_roc_macro": test_results["auc_roc_macro"],
            "sensitivity_macro": test_results["sensitivity_macro"],
            "specificity_macro": test_results["specificity_macro"],
            "sensitivity_per_class": test_results["sensitivity_per_class"],
            "specificity_per_class": test_results["specificity_per_class"],
            "confusion_matrix": test_results["confusion_matrix"],
        },
        str(results_dir / f"{args.model}_test_results.json"),
    )

    # Guardar predicciones para evaluate_classify.py
    predictions = {
        "model": args.model,
        "y_true": y_true,
        "y_pred": y_pred,
        "y_prob": y_prob.tolist(),
        "class_names": class_names,
    }
    save_results(predictions, str(results_dir / f"{args.model}_predictions.json"))

    logger.info("Resultados guardados en %s", results_dir)
    logger.info("Ejecución total: %s", format_duration(time.perf_counter() - script_start))


if __name__ == "__main__":
    main()
