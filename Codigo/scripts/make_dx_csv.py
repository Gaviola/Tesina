"""Genera el CSV de grounding (image_id,diagnosis,disease) a partir de un archivo de predicciones.

El CSV es la entrada de `generate_report.py --diagnosis_source` y de los scripts de incertidumbre,
así que hay que regenerarlo cada vez que cambia el clasificador que ancla la cascada. Antes se
producía a mano, lo que dejaba los reportes anclados en un modelo sin registro de cuál era.

100% local, sin cluster. Uso:
    python scripts/make_dx_csv.py \
        --predictions outputs/results/swin_tiny_sweep_t06_les_cwnone_predictions.json \
        --output outputs/full_dx_swin_les.csv
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Abreviatura de HAM10000 -> nombre clínico, en el mismo vocabulario que full_dx_oracle.csv.
FULL = {
    "MEL": "melanoma",
    "NV": "nevus",
    "BCC": "basal cell carcinoma",
    "AKIEC": "actinic keratosis",
    "BKL": "benign keratosis",
    "DF": "dermatofibroma",
    "VASC": "vascular lesion",
}


def main():
    parser = argparse.ArgumentParser(description="CSV de grounding desde un archivo de predicciones")
    parser.add_argument("--predictions", required=True,
                        help="JSON con y_pred, class_names e image_ids (lo escribe train_classifier.py)")
    parser.add_argument("--output", required=True, help="CSV de salida")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescribir el CSV si ya existe (por defecto falla, para no perder "
                             "el anclaje de reportes ya generados)")
    args = parser.parse_args()

    out = Path(args.output)
    if out.exists() and not args.force:
        logger.error("%s ya existe. Los reportes generados con ese CSV quedarían sin trazabilidad; "
                     "usar otro nombre o --force si es lo que se quiere.", out)
        return 1

    d = json.loads(Path(args.predictions).read_text(encoding="utf-8"))
    faltan = [k for k in ("y_pred", "class_names", "image_ids") if k not in d]
    if faltan:
        logger.error("El archivo de predicciones no tiene %s. Las corridas viejas no guardaban "
                     "image_ids: hay que re-evaluar el checkpoint para obtenerlos.", faltan)
        return 1

    names = d["class_names"]
    desconocidas = sorted({n for n in names if n not in FULL})
    if desconocidas:
        logger.error("Clases sin nombre clínico asignado: %s", desconocidas)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["image_id", "diagnosis", "disease"])
        for image_id, pred in zip(d["image_ids"], d["y_pred"]):
            dx = FULL[names[int(pred)]]
            writer.writerow([image_id, dx, dx])

    logger.info("%d filas escritas en %s (run: %s)", len(d["y_pred"]), out, d.get("run_name", "?"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
