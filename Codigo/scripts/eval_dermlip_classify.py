"""F1: Clasificación zero-shot con DermLIP (VL classifier derm-especializado).

DermLIP es CLIP-style: clasifica por similitud coseno imagen-texto sobre las 7
clases de HAM10000. NO genera texto. Este script corre la eval ZS y guarda
predicciones + métricas en el MISMO schema que train_vlm_classify.py para
comparar directamente contra LLaVA-Med/Mini-VLM y los CNN supervisados.

Corre local (ViT-B/16 ~150M) en minutos. No requiere cluster.

Uso:
    python scripts/eval_dermlip_classify.py --checkpoint vit-b-16
    python scripts/eval_dermlip_classify.py --checkpoint panderm --eval-dataset skincap_clinical
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch

from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.evaluation.classification import evaluate_classification
from src.models.dermlip import DermLIPClassifier
from src.utils.io import save_results
from src.utils.logging import format_duration, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

# Nombres de clase para los prompts ZS, EN EL ORDEN de HAM10000_CLASSES
# (MEL, NV, BCC, AKIEC, BKL, DF, VASC) para que argmax mapee al índice correcto.
HAM_PROMPT_NAMES = [
    "melanoma",
    "melanocytic nevus",
    "basal cell carcinoma",
    "actinic keratosis",
    "benign keratosis",
    "dermatofibroma",
    "vascular lesion",
]


def _load_dataset(args):
    if args.eval_dataset == "skincap_clinical":
        from src.data.skincare import SkinCAPClassificationDataset
        ds = SkinCAPClassificationDataset(
            root_dir=str(Path(args.data_dir) / "raw" / "skincare"),
            splits_file=None, split=None,
        )
        logger.info("Test SkinCAP-clínica (7 clases HAM): %d imágenes | %s",
                    len(ds), ds.class_distribution())
        return ds
    splits_file = args.splits_file or str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    ds = HAM10000Dataset(
        root_dir=str(Path(args.data_dir) / "processed" / "HAM10000"),
        split="test", splits_file=splits_file, return_pil=True,
    )
    logger.info("Test HAM10000 (dermatoscopía): %d imágenes", len(ds))
    return ds


def main():
    parser = argparse.ArgumentParser(description="F1: Clasificación ZS con DermLIP")
    parser.add_argument("--checkpoint", type=str, default="vit-b-16",
                        help="Alias (vit-b-16 | panderm) o string hf-hub:... directo")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--splits_file", type=str, default=None)
    parser.add_argument("--eval-dataset", type=str, default="ham10000",
                        choices=["ham10000", "skincap_clinical"], dest="eval_dataset")
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    setup_logger("eval_dermlip", log_dir=str(Path(args.output_dir) / "logs"))
    logger.info("=== DermLIP clasificación zero-shot (%s) ===", args.checkpoint)

    if not torch.cuda.is_available():
        logger.warning("Sin GPU: la inferencia DermLIP será lenta pero funciona en CPU.")

    model = DermLIPClassifier(checkpoint=args.checkpoint)
    test_dataset = _load_dataset(args)

    all_y_true, all_y_pred, all_image_ids = [], [], []
    t0 = time.perf_counter()
    n = len(test_dataset)
    batch_imgs, batch_labels, batch_ids = [], [], []

    def _flush():
        if not batch_imgs:
            return
        logits = model.zero_shot_logits(batch_imgs, HAM_PROMPT_NAMES)
        preds = logits.argmax(dim=1).tolist()
        all_y_pred.extend(preds)
        all_y_true.extend(batch_labels)
        all_image_ids.extend(batch_ids)
        batch_imgs.clear(); batch_labels.clear(); batch_ids.clear()

    for idx in range(n):
        sample = test_dataset[idx]
        batch_imgs.append(sample["image"])
        batch_labels.append(int(sample["label"]))
        batch_ids.append(sample.get("image_id", ""))
        if len(batch_imgs) >= args.batch_size:
            _flush()
            if (idx + 1) % (args.batch_size * 5) == 0:
                logger.info("Progreso: %d/%d", idx + 1, n)
    _flush()

    elapsed = time.perf_counter() - t0
    logger.info("Inferencia completada en %s (%d imágenes)", format_duration(elapsed), n)

    results = evaluate_classification(all_y_true, all_y_pred, class_names=HAM10000_CLASSES)
    logger.info("=== Resultados DermLIP (%s, %s) ===", args.checkpoint, args.eval_dataset)
    logger.info("Accuracy        : %.4f", results["accuracy"])
    logger.info("F1 weighted     : %.4f", results["f1_weighted"])
    logger.info("Sens. macro     : %.4f", results["sensitivity_macro"])
    logger.info("Spec. macro     : %.4f", results["specificity_macro"])

    ckpt_tag = args.checkpoint.replace("hf-hub:", "").replace("/", "_")
    suffix = f"_zeroshot_{ckpt_tag}"
    if args.eval_dataset == "skincap_clinical":
        suffix += "_clinical"
    results_dir = Path(args.output_dir) / "results" / "dermlip"
    results_dir.mkdir(parents=True, exist_ok=True)

    save_results({
        "model": "dermlip",
        "checkpoint": args.checkpoint,
        "finetuned": False,
        "method": "clip_zeroshot",
        "eval_dataset": args.eval_dataset,
        "class_names": HAM10000_CLASSES,
        "prompt_names": HAM_PROMPT_NAMES,
        "image_ids": all_image_ids,
        "y_true": all_y_true,
        "y_pred": all_y_pred,
    }, str(results_dir / f"dermlip{suffix}_predictions.json"))

    save_results({
        "model": "dermlip",
        "checkpoint": args.checkpoint,
        "method": "clip_zeroshot",
        "eval_dataset": args.eval_dataset,
        "accuracy": results["accuracy"],
        "f1_weighted": results["f1_weighted"],
        "auc_roc_macro": results.get("auc_roc_macro"),
        "sensitivity_macro": results["sensitivity_macro"],
        "specificity_macro": results["specificity_macro"],
        "sensitivity_per_class": results.get("sensitivity_per_class", []),
        "confusion_matrix": results["confusion_matrix"],
        "total_samples": n,
    }, str(results_dir / f"dermlip{suffix}_test_results.json"))

    logger.info("Guardado en %s", results_dir)


if __name__ == "__main__":
    main()
