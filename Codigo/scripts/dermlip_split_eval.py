"""Re-ajuste de los componentes DermLIP entrenados sobre HAM (kNN, linear-probe, SVM-RBF) por split.

Los componentes sin entrenamiento sobre HAM (DermLIP zero-shot) no se ven afectados por el leakage lesión-nivel,
pero el kNN (recuperación del RAG y del ruteo de 3 niveles), el linear-probe y el SVM-RBF sí: se ajustan sobre
embeddings de train y, con el split por imagen, una foto de test puede recuperar como vecino otra foto de su
misma lesión. Este script:

  1. Cachea una sola vez los embeddings DermLIP (L2-normalizados) de las 10015 imágenes.
  2. Para cada split (original por imagen / disjunto por lesión) re-ajusta los tres clasificadores con el MISMO
     protocolo de los scripts originales y evalúa sobre el test (idéntico en ambos splits).
  3. Escribe el contexto kNN del split por lesión (`outputs/rag/rag_context_les.csv`, mismo formato) para
     recomputar el ruteo.

La corrida con el split original sirve de control: debe reproducir los números del documento.

Uso:
    python scripts/dermlip_split_eval.py
"""

import csv
import json
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

META = Path("data/raw/HAM10000/HAM10000_metadata")
IMG_DIR = Path("data/processed/HAM10000")
CACHE = Path("outputs/embeddings/dermlip_vitb16_ham10000.npz")
SPLITS = {"original": Path("data/splits/ham10000_splits.json"),
          "lesion": Path("data/splits/ham10000_splits_lesion.json")}
OUT = Path("outputs/results/dermlip/dermlip_split_eval.json")
CLASSES = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
DX_FULL = {"MEL": "melanoma", "NV": "nevus", "BCC": "basal cell carcinoma", "AKIEC": "actinic keratosis",
           "BKL": "benign keratosis", "DF": "dermatofibroma", "VASC": "vascular lesion"}


@torch.no_grad()
def embed_all(meta: pd.DataFrame) -> tuple[list, np.ndarray]:
    if CACHE.exists():
        z = np.load(CACHE, allow_pickle=True)
        return z["ids"].tolist(), z["X"]
    from src.models.dermlip import DermLIPClassifier
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = DermLIPClassifier(checkpoint="vit-b-16", device=device)
    ids, chunks, batch = meta.image_id.tolist(), [], 128
    for i in range(0, len(ids), batch):
        pils = [Image.open(IMG_DIR / f"{iid}.jpg").convert("RGB") for iid in ids[i:i + batch]]
        chunks.append(model.embed_images(pils).numpy())
        if (i // batch) % 10 == 0:
            logger.info("  embebidas %d/%d", min(i + batch, len(ids)), len(ids))
    X = np.concatenate(chunks)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE, ids=np.array(ids), X=X)
    return ids, X


def score(y, p) -> dict:
    labels = list(range(len(CLASSES)))
    return {"acc": accuracy_score(y, p),
            "f1_weighted": f1_score(y, p, labels=labels, average="weighted", zero_division=0),
            "f1_macro": f1_score(y, p, labels=labels, average="macro", zero_division=0),
            "sens_macro": recall_score(y, p, labels=labels, average="macro", zero_division=0),
            "recall_mel": recall_score(y, p, labels=[0], average="macro", zero_division=0)}


def main():
    set_seed(42)
    meta = pd.read_csv(META)
    meta["y"] = meta.dx.str.upper().map({c: i for i, c in enumerate(CLASSES)})
    ids, X = embed_all(meta)
    row = {iid: i for i, iid in enumerate(ids)}
    info = meta.set_index("image_id")

    res = {}
    for split_name, path in SPLITS.items():
        sp = json.loads(path.read_text(encoding="utf-8"))
        # Mismo orden que HAM10000Dataset (metadata filtrada) para que el kNN desempate igual que el original.
        tr_ids = [i for i in meta.image_id if i in set(sp["train"])]
        te_ids = [i for i in meta.image_id if i in set(sp["test"])]
        Xtr, Xte = X[[row[i] for i in tr_ids]], X[[row[i] for i in te_ids]]
        ytr, yte = info.loc[tr_ids, "y"].values, info.loc[te_ids, "y"].values

        # kNN k=3 (coseno, voto mayoritario; empates -> el vecino más similar), como build_rag_index.py
        sims = Xte @ Xtr.T
        top = np.argpartition(-sims, 3, axis=1)[:, :3]
        knn_pred, rows = [], []
        for i in range(len(te_ids)):
            idx = top[i][np.argsort(-sims[i, top[i]])]
            dxs = [DX_FULL[CLASSES[ytr[j]]] for j in idx]
            vote = Counter(dxs).most_common(1)[0][0]
            knn_pred.append(CLASSES.index([k for k, v in DX_FULL.items() if v == vote][0]))
            locs = [str(info.loc[tr_ids[j], "localization"]) for j in idx]
            ctx = "; ".join(f"{d} ({l})" if l and l != "nan" else d for d, l in zip(dxs, locs))
            rows.append([te_ids[i], f"Retrieved visually similar dermatoscopic cases were diagnosed as: {ctx}.", vote])

        lp = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced", n_jobs=-1).fit(Xtr, ytr)
        scaler = StandardScaler().fit(Xtr)
        svm = SVC(C=10, kernel="rbf", class_weight="balanced").fit(scaler.transform(Xtr), ytr)

        res[split_name] = {"n_train": len(tr_ids), "n_test": len(te_ids),
                           "kNN (k=3)": score(yte, knn_pred),
                           "linear-probe (LogReg)": score(yte, lp.predict(Xte)),
                           "SVM-RBF": score(yte, svm.predict(scaler.transform(Xte)))}
        if split_name == "lesion":
            out_csv = Path("outputs/rag/rag_context_les.csv")
            with out_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["image_id", "rag_context", "rag_knn_dx"])
                w.writerows(rows)
            logger.info("Contexto kNN del split por lesión: %s", out_csv)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'split':9s} {'modelo':22s} {'acc':>6s} {'f1w':>6s} {'f1m':>6s} {'sensM':>6s} {'recMEL':>6s}")
    for split_name, r in res.items():
        for name in ["kNN (k=3)", "linear-probe (LogReg)", "SVM-RBF"]:
            m = r[name]
            print(f"{split_name:9s} {name:22s} {m['acc']:.3f} {m['f1_weighted']:.3f} {m['f1_macro']:.3f} "
                  f"{m['sens_macro']:.3f} {m['recall_mel']:.3f}")
    logger.info("Guardado en %s", OUT)


if __name__ == "__main__":
    main()
