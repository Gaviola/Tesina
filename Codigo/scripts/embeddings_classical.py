"""P2.3 (plan julio-agosto) — Clasificadores clásicos sobre embeddings.

¿La representación ya separa las clases, o hace falta fine-tunear un modelo pesado? Se extraen
embeddings de dos representaciones —DermLIP (derm-especializada) y Swin-ImageNet (genérica,
congelada)— y se entrenan clasificadores clásicos (SVM, Random Forest, Logistic Regression)
sobre HAM10000. No se espera superar a Swin fine-tuneado, sino ver si la representación separa.

Local (RTX 4070). Uso:
    python scripts/embeddings_classical.py
    python scripts/embeddings_classical.py --limit-train 4000
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
import torchvision.models as tvm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.data.ham10000 import HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@torch.no_grad()
def _extract_dermlip(pils, device, batch=64):
    from src.models.dermlip import DermLIPClassifier
    m = DermLIPClassifier(checkpoint="vit-b-16", device=device)
    embs = []
    for i in range(0, len(pils), batch):
        embs.append(m.embed_images(pils[i:i + batch]).float().cpu().numpy())
    return np.concatenate(embs, 0)


@torch.no_grad()
def _extract_swin_imagenet(pils, device, batch=64):
    """Swin-Tiny ImageNet congelado (torchvision), features pre-head (768-dim)."""
    import torch.nn as nn
    m = tvm.swin_t(weights=tvm.Swin_T_Weights.IMAGENET1K_V1).to(device).eval()
    m.head = nn.Identity()
    tf = get_val_transforms(size=224, center_crop=False)
    embs = []
    buf = []
    for im in pils:
        buf.append(tf(im.convert("RGB")))
        if len(buf) == batch:
            embs.append(m(torch.stack(buf).to(device)).cpu().numpy())
            buf = []
    if buf:
        embs.append(m(torch.stack(buf).to(device)).cpu().numpy())
    return np.concatenate(embs, 0)


EXTRACTORS = {
    "DermLIP (ViT-B/16)": _extract_dermlip,
    "Swin-ImageNet (frozen)": _extract_swin_imagenet,
}


def _classical(Xtr, ytr, Xte, yte):
    scaler = StandardScaler().fit(Xtr)
    Xtr, Xte = scaler.transform(Xtr), scaler.transform(Xte)
    clfs = {
        "SVM (RBF)": SVC(C=10, kernel="rbf", class_weight="balanced"),
        "RandomForest": RandomForestClassifier(n_estimators=300, class_weight="balanced", n_jobs=-1, random_state=42),
        "LogReg": LogisticRegression(max_iter=3000, class_weight="balanced", n_jobs=-1),
    }
    out = {}
    for name, clf in clfs.items():
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)
        out[name] = {
            "acc": float(accuracy_score(yte, pred)),
            "f1_weighted": float(f1_score(yte, pred, average="weighted", zero_division=0)),
            "sens_macro": float(recall_score(yte, pred, average="macro", zero_division=0)),
        }
    return out


def _load_split(split, data_dir, limit=None):
    splits = str(Path(data_dir) / "splits" / "ham10000_splits.json")
    ds = HAM10000Dataset(root_dir=str(Path(data_dir) / "processed" / "HAM10000"),
                         split=split, splits_file=splits, return_pil=True)
    n = len(ds) if limit is None else min(limit, len(ds))
    pils = [ds[i]["image"].convert("RGB") for i in range(n)]
    labels = np.array([int(ds[i]["label"]) for i in range(n)])
    return pils, labels


def main():
    parser = argparse.ArgumentParser(description="P2.3 Clásicos sobre embeddings")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--limit-train", type=int, default=None, dest="limit_train")
    parser.add_argument("--output", type=str, default="outputs/results/embeddings/embeddings_classical.json")
    args = parser.parse_args()

    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    logger.info("Cargando splits de HAM...")
    tr_pils, ytr = _load_split("train", args.data_dir, args.limit_train)
    te_pils, yte = _load_split("test", args.data_dir)
    logger.info("Train=%d  Test=%d", len(tr_pils), len(te_pils))

    summary = {}
    print(f"\n{'Representación':<26}{'Clasificador':<16}{'Acc':>7}{'F1-w':>8}{'Sens.macro':>12}")
    for rep, extractor in EXTRACTORS.items():
        logger.info("Extrayendo embeddings: %s ...", rep)
        Xtr = extractor(tr_pils, device)
        Xte = extractor(te_pils, device)
        logger.info("  dim=%d", Xtr.shape[1])
        res = _classical(Xtr, ytr, Xte, yte)
        summary[rep] = res
        for clf, m in res.items():
            print(f"{rep:<26}{clf:<16}{m['acc']:>7.3f}{m['f1_weighted']:>8.3f}{m['sens_macro']:>12.3f}")
        print()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
