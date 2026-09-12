"""Split de HAM10000 disjunto por lesión, con el conjunto de test IDÉNTICO al original.

Motivo (feedback tutor 2026-09-12): el split original es estratificado por imagen; el 36% de las imágenes de
test comparte `lesion_id` con train (HAM10000 no publica id de paciente; la lesión es la agrupación más fina
disponible). Mantener el test fijo preserva la comparabilidad con todo lo que ya se evaluó sobre esas 1503
imágenes (VLMs, DermLIP, generación de reportes, ruteo); solo cambian train y val:

  1. Se descartan de train/val las imágenes cuya lesión aparece en test (son fotos de lesiones de test).
  2. El resto se reparte en train/val con StratifiedGroupKFold (grupos = lesion_id, estratos = dx), tomando
     como val el fold cuya distribución de clases más se parece a la global.

Salida: data/splits/ham10000_splits_lesion.json (+ verificación de solapamiento cero).

Uso:
    python scripts/make_lesion_disjoint_split.py
"""

import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

META = Path("data/raw/HAM10000/HAM10000_metadata")
SRC = Path("data/splits/ham10000_splits.json")
DST = Path("data/splits/ham10000_splits_lesion.json")
N_FOLDS = 6  # val ~ 1/6 del pool (similar al 15% original)
SEED = 42


def main():
    meta = pd.read_csv(META)
    orig = json.loads(SRC.read_text(encoding="utf-8"))
    test_ids = orig["test"]
    test_lesions = set(meta[meta.image_id.isin(set(test_ids))].lesion_id)

    pool = meta[~meta.image_id.isin(set(test_ids))]
    dropped = pool[pool.lesion_id.isin(test_lesions)]
    pool = pool[~pool.lesion_id.isin(test_lesions)].reset_index(drop=True)
    logger.info("Descartadas %d imágenes de train/val por pertenecer a lesiones de test", len(dropped))

    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    global_dist = pool.dx.value_counts(normalize=True).sort_index()
    best, best_err = None, np.inf
    for tr_idx, va_idx in sgkf.split(pool, pool.dx, groups=pool.lesion_id):
        err = (pool.iloc[va_idx].dx.value_counts(normalize=True).sort_index() - global_dist).abs().sum()
        if err < best_err:
            best, best_err = (tr_idx, va_idx), err
    tr, va = pool.iloc[best[0]], pool.iloc[best[1]]

    splits = {"train": tr.image_id.tolist(), "val": va.image_id.tolist(), "test": list(test_ids)}
    les = {k: set(meta[meta.image_id.isin(set(v))].lesion_id) for k, v in splits.items()}
    overlaps = {"train-test": len(les["train"] & les["test"]), "val-test": len(les["val"] & les["test"]),
                "train-val": len(les["train"] & les["val"])}
    assert all(v == 0 for v in overlaps.values()), overlaps

    DST.write_text(json.dumps(splits, indent=2), encoding="utf-8")
    dist = pd.DataFrame({k: meta[meta.image_id.isin(set(v))].dx.value_counts() for k, v in splits.items()})
    logger.info("train=%d val=%d test=%d (descartadas=%d) | solapamiento de lesiones: %s",
                len(tr), len(va), len(test_ids), len(dropped), overlaps)
    print(dist.to_string())
    logger.info("Guardado en %s", DST)


if __name__ == "__main__":
    main()
