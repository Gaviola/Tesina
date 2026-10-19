"""Fase 2: Evaluación de reportes generados (3 niveles).

Nivel 1: Métricas automáticas con referencia (BLEU-4, ROUGE-L, BERTScore, METEOR, CIDEr).
Nivel 2: Entidades clínicas sin referencia (NER).
Nivel 3: Evaluación cualitativa — genera CSV para revisión manual.

Formato esperado de cada JSON en --reports_dir:
    {
        "image_id": "img001.png",
        "report": "This dermatoscopic image shows...",
        "reference": "...",      (requerido para Nivel 1)
        "gt_label": "melanoma",  (opcional para Nivel 2)
        "model": "llava_med"
    }

Uso:
    python scripts/evaluate_reports.py --model llava_med --level 1
    python scripts/evaluate_reports.py --model llava_med --level 2
    python scripts/evaluate_reports.py --model llava_med --level 3
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.io import load_results, save_results
from src.utils.logging import log_time, setup_logger

logger = logging.getLogger(__name__)


def _load_reports(reports_dir: str, model_filter: str = None) -> list[dict]:
    """Carga todos los reportes JSON del directorio."""
    dir_path = Path(reports_dir)
    if not dir_path.exists():
        logger.error("Directorio de reportes no encontrado: %s", reports_dir)
        sys.exit(1)

    report_files = sorted(dir_path.glob("*.json"))
    if not report_files:
        logger.error("No se encontraron archivos JSON en %s", reports_dir)
        sys.exit(1)

    all_reports = []
    for f in report_files:
        try:
            data = load_results(str(f))
            if isinstance(data, list):
                all_reports.extend(data)
            elif isinstance(data, dict):
                all_reports.append(data)
        except Exception as e:
            logger.warning("No se pudo leer %s: %s", f.name, e)

    if model_filter:
        filtered = [r for r in all_reports if r.get("model", "") == model_filter]
        if filtered:
            all_reports = filtered
        else:
            logger.warning(
                "No se encontraron reportes con model='%s'. Usando todos (%d).",
                model_filter, len(all_reports),
            )

    logger.info("Reportes cargados: %d", len(all_reports))
    return all_reports


def _level1(reports: list[dict], model: str, output_dir: Path):
    """Nivel 1: métricas automáticas con referencia."""
    from src.evaluation.generation import evaluate_generation

    predictions = [r["report"] for r in reports if r.get("report")]
    references = [r.get("reference", "") for r in reports if r.get("report")]

    # «nan» es una fila sin descripción guardada como texto por versiones anteriores de generate_report.py.
    def _has_ref(ref: str) -> bool:
        return bool(ref and ref.strip() and ref.strip().lower() != "nan")

    if not any(_has_ref(ref) for ref in references):
        logger.error(
            "Nivel 1 requiere referencias en los reportes. "
            "Asegúrate de que los JSON tengan la clave 'reference'."
        )
        sys.exit(1)

    # Usar solo reportes que tengan referencia
    pairs = [(p, r) for p, r in zip(predictions, references) if _has_ref(r)]
    if len(pairs) < len(predictions):
        logger.warning(
            "%d/%d reportes tienen referencia y serán evaluados.",
            len(pairs), len(predictions),
        )
    predictions = [p for p, _ in pairs]
    references = [r for _, r in pairs]

    logger.info("Calculando métricas Nivel 1 para %d pares...", len(predictions))
    with log_time("Métricas Nivel 1", logger):
        metrics = evaluate_generation(predictions, references)

    output_path = output_dir / f"level1_{model}_results.json"
    save_results(metrics, str(output_path))

    logger.info("=== Resultados Nivel 1 (%s) ===", model)
    for name, val in metrics.items():
        logger.info("  %-16s: %.4f", name, val)
    logger.info("Guardado en %s", output_path)


def _level2(reports: list[dict], model: str, output_dir: Path):
    """Nivel 2: NER clínico sin referencia."""
    from src.evaluation.clinical_ner import evaluate_clinical_entities

    predictions = [r["report"] for r in reports if r.get("report")]
    gt_labels = [r.get("gt_label") for r in reports if r.get("report")]

    # Solo pasar gt_labels si hay al menos uno no-vacío
    gt_labels_clean = [l for l in gt_labels if l and str(l).strip()]
    gt_labels_arg = gt_labels if gt_labels_clean else None

    if not gt_labels_clean:
        logger.info("Sin gt_labels en reportes. Se calculará solo clinical_entity_recall.")

    logger.info("Calculando métricas Nivel 2 (NER) para %d reportes...", len(predictions))
    with log_time("Métricas Nivel 2", logger):
        metrics = evaluate_clinical_entities(predictions, ground_truth_labels=gt_labels_arg)

    # Serializar: per_report puede tener entidades complejas
    # Convertir para guardar como JSON limpio
    summary = {
        "clinical_entity_recall": metrics["clinical_entity_recall"],
        "backend": metrics["backend"],
    }
    if "diagnostic_consistency" in metrics:
        summary["diagnostic_consistency"] = metrics["diagnostic_consistency"]

    # Agregar estadísticas por reporte (sin entidades completas para compacidad)
    summary["per_report_recall"] = [r["recall"] for r in metrics["per_report"]]

    output_path = output_dir / f"level2_{model}_results.json"
    save_results(summary, str(output_path))

    logger.info("=== Resultados Nivel 2 (%s) ===", model)
    logger.info("  %-28s: %.4f", "clinical_entity_recall", metrics["clinical_entity_recall"])
    if "diagnostic_consistency" in metrics:
        logger.info("  %-28s: %.4f", "diagnostic_consistency", metrics["diagnostic_consistency"])
    logger.info("  %-28s: %s", "backend NER", metrics["backend"])
    logger.info("Guardado en %s", output_path)


def _level3(reports: list[dict], model: str, output_dir: Path):
    """Nivel 3: genera CSV para revisión manual."""
    rows = [
        {
            "image_id": r.get("image_id", ""),
            "model": r.get("model", model),
            "generated_report": r.get("report", ""),
            "reference": r.get("reference", ""),
            "gt_label": r.get("gt_label", ""),
            "evaluator_score": "",
            "evaluator_comments": "",
        }
        for r in reports if r.get("report")
    ]

    output_path = output_dir / f"level3_{model}_manual_review.csv"
    save_results(rows, str(output_path))
    logger.info(
        "CSV para revisión manual generado: %s (%d reportes)",
        output_path, len(rows),
    )
    logger.info(
        "Instrucciones: rellena 'evaluator_score' (1-5) y 'evaluator_comments' "
        "para cada reporte y guarda el archivo."
    )


def main():
    parser = argparse.ArgumentParser(description="F2: Evaluación de reportes generados")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--level", type=int, required=True, choices=[1, 2, 3])
    parser.add_argument("--reports_dir", type=str, default="outputs/generated_reports")
    parser.add_argument("--dataset", type=str, default="HAM10000",
                        help="Subdirectorio del dataset dentro de reports_dir/model/")
    parser.add_argument("--output_dir", type=str, default="outputs/results")
    parser.add_argument("--strip-reasoning", action="store_true", dest="strip_reasoning",
                        help="Elimina los bloques <think>...</think> del reporte antes de evaluar "
                             "(mide el REPORTE comprometido, no el razonamiento). Ver ensamble_resul.")
    args = parser.parse_args()

    setup_logger("evaluate_reports")
    logger.info("=== Evaluación Nivel %d — modelo: %s%s ===", args.level, args.model,
                " (report-only)" if args.strip_reasoning else "")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Construir ruta: reports_dir/model/dataset/
    reports_path = Path(args.reports_dir) / args.model / args.dataset
    reports = _load_reports(str(reports_path), model_filter=args.model)

    if args.strip_reasoning:
        import re as _re
        _TAG = _re.compile(r"<think>.*?(?:</think>|$)", _re.DOTALL)
        for r in reports:
            if r.get("report"):
                r["report"] = _TAG.sub(" ", r["report"]).strip()
        logger.info("Razonamiento <think> eliminado de %d reportes (report-only).", len(reports))

    if args.level == 1:
        _level1(reports, args.model, output_dir)
    elif args.level == 2:
        _level2(reports, args.model, output_dir)
    elif args.level == 3:
        _level3(reports, args.model, output_dir)


if __name__ == "__main__":
    main()
