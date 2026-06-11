"""Parcha retroactivamente los reportes generados: corrige gt_label y referencia CoT.

Problemas corregidos:
  1. gt_label vacío en reportes de skincare: se deriva del CSV de SkinCAP o del
     nombre de la carpeta padre en el directorio de imágenes SkinCoT.
  2. reference contiene CoT completo en reportes de skincare: se eliminan los
     bloques <think>...</think> conservando solo el resumen final.

Los reportes de mmskin y HAM10000 no se modifican (gt_label y reference ya son
correctos o vacíos intencionalmente).

Uso:
    python scripts/fix_reports.py \\
        --label_csv data/raw/skincare/SkinCAP/skincap_v240623.csv \\
        --skincot_images_dir data/raw/skincare/SkinCoT/images \\
        --reports_dir outputs/generated_reports
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.logging import setup_logger

logger = logging.getLogger(__name__)

_COT_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def _strip_cot(text: str) -> str:
    return _COT_TAG_RE.sub("", text).strip()


def _build_label_lookup(label_csv: Path) -> dict[str, str]:
    """Carga mapeo filename → disease desde el CSV de SkinCAP."""
    import pandas as pd
    df = pd.read_csv(label_csv)
    id_col = "skincap_file_path" if "skincap_file_path" in df.columns else "image_id"
    lookup: dict[str, str] = {}
    for _, row in df.iterrows():
        img_id = Path(str(row.get(id_col, ""))).name
        label = str(row.get("disease", "")).strip()
        if img_id and label:
            lookup[img_id] = label
    logger.info("Label lookup cargado desde CSV: %d entradas", len(lookup))
    return lookup


def _build_skincot_lookup(skincot_images_dir: Path) -> dict[str, str]:
    """Escanea <skincot_images_dir>/<clase>/<imagen> y mapea filename → clase."""
    lookup: dict[str, str] = {}
    for class_dir in skincot_images_dir.iterdir():
        if not class_dir.is_dir():
            continue
        for img_file in class_dir.iterdir():
            if img_file.suffix.lower() in _IMAGE_EXTENSIONS:
                lookup[img_file.name] = class_dir.name
    logger.info("SkinCoT folder lookup construido: %d entradas", len(lookup))
    return lookup


def _fix_skincare_reports(
    skincare_dir: Path,
    csv_lookup: dict[str, str],
    skincot_lookup: dict[str, str],
) -> tuple[int, int, int]:
    """
    Recorre todos los JSON en skincare_dir y aplica las correcciones.
    Devuelve (total, label_fixed, reference_fixed).
    """
    report_files = sorted(skincare_dir.glob("*_report.json"))
    total = len(report_files)
    label_fixed = 0
    reference_fixed = 0

    for report_path in report_files:
        try:
            with open(report_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("No se pudo leer %s: %s", report_path.name, e)
            continue

        changed = False
        image_id = data.get("image_id", report_path.stem.replace("_report", ""))

        # --- Corregir gt_label ---
        if not data.get("gt_label"):
            label = csv_lookup.get(image_id) or skincot_lookup.get(image_id, "")
            if label:
                data["gt_label"] = label
                label_fixed += 1
                changed = True

        # --- Corregir reference (strip CoT) ---
        ref = data.get("reference", "")
        if ref and "<think>" in ref:
            data["reference"] = _strip_cot(ref)
            reference_fixed += 1
            changed = True

        if changed:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    return total, label_fixed, reference_fixed


def main():
    parser = argparse.ArgumentParser(description="Parchea reportes generados existentes")
    parser.add_argument(
        "--reports_dir", type=str, default="outputs/generated_reports",
        help="Directorio raíz con los reportes generados (contiene llava_med/, mini_vlm/)",
    )
    parser.add_argument(
        "--label_csv", type=str,
        default="data/raw/skincare/SkinCAP/skincap_v240623.csv",
        help="CSV de SkinCAP con columnas skincap_file_path y disease",
    )
    parser.add_argument(
        "--skincot_images_dir", type=str,
        default="data/raw/skincare/SkinCoT/images",
        help="Directorio con subcarpetas por clase de SkinCoT",
    )
    args = parser.parse_args()

    setup_logger("fix_reports")

    reports_dir = Path(args.reports_dir)
    label_csv = Path(args.label_csv)
    skincot_images_dir = Path(args.skincot_images_dir)

    if not reports_dir.exists():
        logger.error("Directorio de reportes no encontrado: %s", reports_dir)
        sys.exit(1)

    # Construir lookups
    csv_lookup: dict[str, str] = {}
    if label_csv.exists():
        csv_lookup = _build_label_lookup(label_csv)
    else:
        logger.warning("Label CSV no encontrado: %s. Solo se usará lookup de carpetas.", label_csv)

    skincot_lookup: dict[str, str] = {}
    if skincot_images_dir.exists():
        skincot_lookup = _build_skincot_lookup(skincot_images_dir)
    else:
        logger.warning(
            "Directorio SkinCoT no encontrado: %s. Solo se usará lookup de CSV.", skincot_images_dir
        )

    if not csv_lookup and not skincot_lookup:
        logger.error("No hay fuentes de labels disponibles. Abortando.")
        sys.exit(1)

    # Procesar reportes de skincare para cada modelo
    total_all = label_all = ref_all = 0
    for model_dir in sorted(reports_dir.iterdir()):
        if not model_dir.is_dir():
            continue
        skincare_dir = model_dir / "skincare"
        if not skincare_dir.exists():
            continue

        logger.info("Procesando %s/skincare ...", model_dir.name)
        total, label_fixed, reference_fixed = _fix_skincare_reports(
            skincare_dir, csv_lookup, skincot_lookup
        )
        logger.info(
            "  %s: %d reportes | %d gt_label corregidos | %d referencias CoT limpiadas",
            model_dir.name, total, label_fixed, reference_fixed,
        )
        total_all += total
        label_all += label_fixed
        ref_all += reference_fixed

    logger.info(
        "Finalizado. Total: %d reportes | %d gt_label | %d referencias CoT",
        total_all, label_all, ref_all,
    )


if __name__ == "__main__":
    main()
