"""Desempeño en HIBA separado por modalidad (dermoscópica frente a clínica).

HIBA mezcla 1 270 imágenes dermoscópicas y 346 clínicas (`image_type` en `metadata.csv`). Las predicciones
`*_predictions_hiba.json` no guardan el id de imagen, pero `HIBADataset` recorre `metadata.csv` en orden y no
descarta ninguna fila (las 1 616 tienen imagen y diagnóstico mapeable), así que se alinean por posición. El
script lo verifica comparando `y_true` con las etiquetas mapeadas del metadato.

100% local, sin GPU. Uso:
    python scripts/hiba_por_modalidad.py
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import recall_score

from src.data.ham10000 import HAM10000_LABEL_MAP
from src.data.hiba import HIBA_TO_HAM10000

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

METADATA = Path("data/raw/HIBA/metadata.csv")
SOURCES = {
    "Swin-Tiny t06_les_cwnone": "outputs/results/swin_tiny_sweep_t06_les_cwnone_hiba_predictions_hiba.json",
    "ConvNeXt-Tiny t02_les_cwnone": "outputs/results/convnext_tiny_sweep_t02_les_cwnone_hiba_predictions_hiba.json",
}


def _metrics(y_true, y_pred):
    return {
        "n": int(len(y_true)),
        "acc": float((y_true == y_pred).mean()),
        "sens_macro": float(recall_score(y_true, y_pred, average="macro", labels=np.unique(y_true),
                                         zero_division=0)),
    }


def main():
    parser = argparse.ArgumentParser(description="HIBA por modalidad")
    parser.add_argument("--out", default="outputs/results/hiba_por_modalidad.json")
    args = parser.parse_args()

    md = pd.read_csv(METADATA)
    labels = md["diagnosis"].map(lambda d: HAM10000_LABEL_MAP[HIBA_TO_HAM10000[d]]).to_numpy()
    dermo = md["image_type"].astype(str).str.startswith("dermoscopic").to_numpy()

    report = {}
    for name, path in SOURCES.items():
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        y_true, y_pred = np.asarray(d["y_true"]), np.asarray(d["y_pred"])
        if len(y_true) != len(labels) or not (y_true == labels).all():
            raise ValueError(f"{name}: las predicciones no se alinean con {METADATA}")
        report[name] = {
            "total": _metrics(y_true, y_pred),
            "dermoscopica": _metrics(y_true[dermo], y_pred[dermo]),
            "clinica": _metrics(y_true[~dermo], y_pred[~dermo]),
        }
        for part, m in report[name].items():
            logger.info("%-30s %-12s n=%4d acc=%.3f sensM=%.3f", name, part, m["n"], m["acc"], m["sens_macro"])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", args.out)


if __name__ == "__main__":
    main()
