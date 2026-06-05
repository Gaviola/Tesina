"""F1: DermLIP linear-probe sobre HAM10000 (comparación justa vs CNN supervisados).

Protocolo estándar de linear-probe: congelar el encoder de imagen de DermLIP,
cachear los embeddings de train/test, y entrenar un clasificador lineal
(LogisticRegression) encima. Aísla la calidad del encoder derm-especializado dado
entrenamiento supervisado, en igualdad de condiciones con los CNN.

Cachear embeddings (CPU OK, ViT-B/16) + LR es barato — no requiere GPU ni cluster.

Uso:
    python scripts/eval_dermlip_linearprobe.py --checkpoint vit-b-16
"""

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.evaluation.classification import evaluate_classification
from src.models.dermlip import DermLIPClassifier
from src.utils.io import save_results
from src.utils.logging import format_duration, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)


def _embed_split(model, dataset, batch_size: int):
    """Devuelve (X embeddings [N,D], y labels [N])."""
    X, y = [], []
    buf_imgs, buf_lbls = [], []

    def _flush():
        if buf_imgs:
            X.append(model.embed_images(buf_imgs).numpy())
            y.extend(buf_lbls)
            buf_imgs.clear(); buf_lbls.clear()

    n = len(dataset)
    for idx in range(n):
        s = dataset[idx]
        buf_imgs.append(s["image"]); buf_lbls.append(int(s["label"]))
        if len(buf_imgs) >= batch_size:
            _flush()
            if (idx + 1) % (batch_size * 10) == 0:
                logger.info("  embedding %d/%d", idx + 1, n)
    _flush()
    return np.concatenate(X, axis=0), np.array(y)


def main():
    parser = argparse.ArgumentParser(description="F1: DermLIP linear-probe en HAM")
    parser.add_argument("--checkpoint", type=str, default="vit-b-16")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--splits_file", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    set_seed(args.seed)
    setup_logger("dermlip_linearprobe", log_dir=str(Path(args.output_dir) / "logs"))
    logger.info("=== DermLIP linear-probe (%s) ===", args.checkpoint)

    from sklearn.linear_model import LogisticRegression

    splits_file = args.splits_file or str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    root = str(Path(args.data_dir) / "processed" / "HAM10000")
    train_ds = HAM10000Dataset(root_dir=root, split="train", splits_file=splits_file, return_pil=True)
    test_ds = HAM10000Dataset(root_dir=root, split="test", splits_file=splits_file, return_pil=True)
    logger.info("Train: %d | Test: %d", len(train_ds), len(test_ds))

    model = DermLIPClassifier(checkpoint=args.checkpoint)

    t0 = time.perf_counter()
    logger.info("Cacheando embeddings de train...")
    Xtr, ytr = _embed_split(model, train_ds, args.batch_size)
    logger.info("Cacheando embeddings de test...")
    Xte, yte = _embed_split(model, test_ds, args.batch_size)
    logger.info("Embeddings listos en %s (dim=%d)", format_duration(time.perf_counter() - t0), Xtr.shape[1])

    # Linear-probe: LogisticRegression con balanceo de clases (HAM desbalanceado).
    clf = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced", n_jobs=-1)
    clf.fit(Xtr, ytr)
    ypred = clf.predict(Xte).tolist()

    results = evaluate_classification(yte.tolist(), ypred, class_names=HAM10000_CLASSES)
    logger.info("=== DermLIP linear-probe — resultados ===")
    logger.info("Accuracy        : %.4f", results["accuracy"])
    logger.info("F1 weighted     : %.4f", results["f1_weighted"])
    logger.info("Sens. macro     : %.4f", results["sensitivity_macro"])
    logger.info("Spec. macro     : %.4f", results["specificity_macro"])

    ckpt_tag = args.checkpoint.replace("hf-hub:", "").replace("/", "_")
    results_dir = Path(args.output_dir) / "results" / "dermlip"
    results_dir.mkdir(parents=True, exist_ok=True)
    save_results({
        "model": "dermlip", "checkpoint": args.checkpoint, "method": "linear_probe",
        "accuracy": results["accuracy"], "f1_weighted": results["f1_weighted"],
        "auc_roc_macro": results.get("auc_roc_macro"),
        "sensitivity_macro": results["sensitivity_macro"],
        "specificity_macro": results["specificity_macro"],
        "sensitivity_per_class": results.get("sensitivity_per_class", []),
        "confusion_matrix": results["confusion_matrix"],
        "n_train": int(len(ytr)), "n_test": int(len(yte)),
    }, str(results_dir / f"dermlip_linearprobe_{ckpt_tag}_test_results.json"))
    logger.info("Guardado en %s", results_dir)


if __name__ == "__main__":
    main()
