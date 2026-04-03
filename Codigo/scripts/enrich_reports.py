"""Enriquece reportes generados con gt_label desde metadata HAM10000.

Los JSONs generados por generate_report.py tienen gt_label vacío.
Este script cruza image_id con el metadata para poblar el diagnóstico real.

Uso:
    python scripts/enrich_reports.py
    python scripts/enrich_reports.py --data_dir data/raw/HAM10000 --reports_dir outputs/generated_reports
"""

import argparse
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.io import load_results, save_results
from src.utils.logging import setup_logger

logger = logging.getLogger(__name__)

# Mapeo de abreviaciones HAM10000 a nombres completos
# (requerido por _DIAGNOSIS_SYNONYMS en src/evaluation/clinical_ner.py)
DX_TO_FULL = {
    "mel": "melanoma",
    "nv": "nevus",
    "bcc": "basal cell carcinoma",
    "akiec": "actinic keratosis",
    "bkl": "benign keratosis",
    "df": "dermatofibroma",
    "vasc": "vascular lesion",
}


def _build_label_map(data_dir: Path) -> dict[str, str]:
    """Construye mapeo {image_id: full_diagnosis} desde metadata CSVs."""
    import pandas as pd

    label_map = {}

    # Cargar metadata principal (con o sin extensión .csv)
    for name in ["HAM10000_metadata.csv", "HAM10000_metadata"]:
        meta_path = data_dir / name
        if meta_path.exists():
            df = pd.read_csv(meta_path)
            for _, row in df.iterrows():
                dx_full = DX_TO_FULL.get(row["dx"], row["dx"])
                label_map[row["image_id"]] = dx_full
            logger.info("Metadata principal cargada: %d entradas desde %s", len(df), name)
            break
    else:
        logger.warning("No se encontró HAM10000_metadata en %s", data_dir)

    # Cargar test ground truth
    gt_path = data_dir / "ISIC2018_Task3_Test_GroundTruth.csv"
    if gt_path.exists():
        df_test = pd.read_csv(gt_path)
        count_before = len(label_map)
        for _, row in df_test.iterrows():
            dx_full = DX_TO_FULL.get(row["dx"], row["dx"])
            label_map[row["image_id"]] = dx_full
        logger.info(
            "Test ground truth cargado: %d entradas nuevas desde %s",
            len(label_map) - count_before, gt_path.name,
        )

    logger.info("Mapeo total: %d image_id -> diagnostico", len(label_map))
    return label_map


def _enrich_directory(reports_dir: Path, label_map: dict[str, str]) -> tuple[int, int]:
    """Enriquece todos los JSONs en un directorio. Retorna (enriquecidos, no_encontrados)."""
    json_files = sorted(reports_dir.glob("*.json"))
    if not json_files:
        logger.warning("Sin archivos JSON en %s", reports_dir)
        return 0, 0

    enriched = 0
    not_found = 0
    label_dist = Counter()

    for json_path in json_files:
        data = load_results(str(json_path))

        # Extraer image_id sin extensión
        image_id = data.get("image_id", "")
        image_id_clean = Path(image_id).stem  # ISIC_0024306.jpg -> ISIC_0024306

        gt_label = label_map.get(image_id_clean, "")
        if gt_label:
            data["gt_label"] = gt_label
            save_results(data, str(json_path))
            enriched += 1
            label_dist[gt_label] += 1
        else:
            not_found += 1

    if label_dist:
        logger.info("Distribución de labels en %s:", reports_dir.name)
        for label, count in sorted(label_dist.items(), key=lambda x: -x[1]):
            logger.info("  %-25s: %d", label, count)

    return enriched, not_found


def main():
    parser = argparse.ArgumentParser(description="Enriquece reportes con gt_label de HAM10000")
    parser.add_argument("--data_dir", type=str, default="data/raw/HAM10000")
    parser.add_argument("--reports_dir", type=str, default="outputs/generated_reports")
    args = parser.parse_args()

    setup_logger("enrich_reports")
    logger.info("=== Enriquecimiento de reportes con gt_label ===")

    data_dir = Path(args.data_dir)
    reports_dir = Path(args.reports_dir)

    if not data_dir.exists():
        logger.error("Directorio de datos no encontrado: %s", data_dir)
        sys.exit(1)

    label_map = _build_label_map(data_dir)
    if not label_map:
        logger.error("No se pudo construir el mapeo de labels. Verificá los archivos de metadata.")
        sys.exit(1)

    total_enriched = 0
    total_not_found = 0

    # Recorrer subdirectorios: {model}/HAM10000/
    for model_dir in sorted(reports_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        ham_dir = model_dir / "HAM10000"
        if ham_dir.exists():
            logger.info("Procesando %s ...", ham_dir)
            enriched, not_found = _enrich_directory(ham_dir, label_map)
            total_enriched += enriched
            total_not_found += not_found
            logger.info(
                "  %s: %d enriquecidos, %d no encontrados",
                model_dir.name, enriched, not_found,
            )

    logger.info("=== Resumen ===")
    logger.info("Total enriquecidos: %d", total_enriched)
    logger.info("Total no encontrados: %d", total_not_found)


if __name__ == "__main__":
    main()
