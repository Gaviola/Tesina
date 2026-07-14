"""P5.3 — Índice de recuperación (RAG) con embeddings DermLIP.

Para cada imagen de test de HAM10000 recupera los k casos de TRAIN visualmente más similares
(coseno sobre embeddings DermLIP) y arma un contexto de "casos similares" (sus diagnósticos +
localización) para inyectar en el prompt del generador. También guarda el voto mayoritario de los
vecinos (kNN dx) para comparar RAG-context vs grounding-clasificador.

Se corre LOCAL (DermLIP es liviano). Salida: outputs/rag/rag_context.csv (image_id, rag_context,
rag_knn_dx) — el job de generación la lee como un CSV de contexto, sin necesitar DermLIP en el cluster.

Uso:
    python scripts/build_rag_index.py --k 3
"""

import argparse
import csv
import logging
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.ham10000 import HAM10000Dataset
from src.utils.device import get_device
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# HAM dx (abrev.) -> nombre clínico completo (igual formato que full_dx_oracle.csv).
DX_FULL = {
    "MEL": "melanoma", "NV": "nevus", "BCC": "basal cell carcinoma",
    "AKIEC": "actinic keratosis", "BKL": "benign keratosis",
    "DF": "dermatofibroma", "VASC": "vascular lesion",
}


@torch.no_grad()
def _embed(samples, device, batch=64):
    """Embeddings DermLIP L2-normalizados de una lista de samples (con image_path)."""
    from PIL import Image
    from src.models.dermlip import DermLIPClassifier
    m = DermLIPClassifier(checkpoint="vit-b-16", device=device)
    embs = []
    for i in range(0, len(samples), batch):
        pils = [Image.open(s["image_path"]).convert("RGB") for s in samples[i:i + batch]]
        e = m.embed_images(pils).float().cpu().numpy()
        embs.append(e)
        if (i // batch) % 10 == 0:
            logger.info("  embebidas %d/%d", min(i + batch, len(samples)), len(samples))
    X = np.concatenate(embs, axis=0)
    X /= (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def main():
    parser = argparse.ArgumentParser(description="P5.3 Índice RAG (DermLIP)")
    parser.add_argument("--k", type=int, default=3, help="Vecinos a recuperar por imagen.")
    parser.add_argument("--data-dir", type=str, default="data")
    parser.add_argument("--output", type=str, default="outputs/rag/rag_context.csv")
    args = parser.parse_args()

    set_seed(42)
    device = get_device()
    splits = str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    root = str(Path(args.data_dir) / "processed" / "HAM10000")
    train = HAM10000Dataset(root_dir=root, split="train", transform=None, splits_file=splits)
    test = HAM10000Dataset(root_dir=root, split="test", transform=None, splits_file=splits)
    logger.info("Train=%d Test=%d | device=%s", len(train.samples), len(test.samples), device)

    logger.info("Extrayendo embeddings DermLIP de TRAIN ...")
    Xtr = _embed(train.samples, device)
    logger.info("Extrayendo embeddings DermLIP de TEST ...")
    Xte = _embed(test.samples, device)

    tr_dx = [DX_FULL.get(s["dx"], s["dx"].lower()) for s in train.samples]
    tr_loc = [str(s.get("localization") or "") for s in train.samples]

    # Similitud coseno (embeddings ya normalizados) -> top-k por fila.
    sims = Xte @ Xtr.T  # (n_test, n_train)
    topk = np.argpartition(-sims, args.k, axis=1)[:, :args.k]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "rag_context", "rag_knn_dx"])
        for i, s in enumerate(test.samples):
            idxs = topk[i]
            # Ordenar los k por similitud desc.
            idxs = idxs[np.argsort(-sims[i, idxs])]
            dxs = [tr_dx[j] for j in idxs]
            locs = [tr_loc[j] for j in idxs]
            parts = []
            for dx, loc in zip(dxs, locs):
                parts.append(f"{dx} ({loc})" if loc and loc != "nan" else dx)
            context = ("Retrieved visually similar dermatoscopic cases were diagnosed as: "
                       + "; ".join(parts) + ".")
            knn_dx = Counter(dxs).most_common(1)[0][0]
            w.writerow([s["image_id"], context, knn_dx])

    logger.info("Guardado %s (n=%d, k=%d)", out, len(test.samples), args.k)
    # Sanity: accuracy del kNN-dx vs gt (referencia, no es el objetivo).
    from collections import Counter as C
    correct = sum(1 for i, s in enumerate(test.samples)
                  if Counter([tr_dx[j] for j in topk[i]]).most_common(1)[0][0]
                  == DX_FULL.get(s["dx"], s["dx"].lower()))
    logger.info("kNN-dx accuracy (referencia) = %.3f", correct / len(test.samples))


if __name__ == "__main__":
    main()
