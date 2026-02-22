"""Fase 1: Evaluación de clasificación.

Genera tabla comparativa: DenseNet vs ViT vs LLaVA-Med vs Mini-VLM.

Uso:
    python scripts/evaluate_classify.py --results_dir outputs/results
    python scripts/evaluate_classify.py --results_dir outputs/results --models densenet vit
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.ham10000 import HAM10000_CLASSES
from src.evaluation.classification import evaluate_classification
from src.evaluation.report_builder import build_comparison_table
from src.utils.io import load_results, save_results
from src.utils.logging import setup_logger

logger = logging.getLogger(__name__)

ALL_MODELS = ["densenet", "vit", "llava_med", "mini_vlm"]
COMPARISON_METRICS = [
    "accuracy",
    "f1_weighted",
    "auc_roc_macro",
    "sensitivity_macro",
    "specificity_macro",
]


def main():
    parser = argparse.ArgumentParser(description="F1: Evaluación de clasificación")
    parser.add_argument("--results_dir", type=str, default="outputs/results")
    parser.add_argument("--output", type=str, default="outputs/results/phase1_comparison.csv")
    parser.add_argument("--models", nargs="+", default=None,
                        help="Modelos a incluir (default: todos los disponibles)")
    args = parser.parse_args()

    setup_logger(name="evaluate_classify", log_dir=str(Path(args.results_dir).parent / "logs"))
    logger.info("Evaluación comparativa Fase 1")

    results_dir = Path(args.results_dir)
    models_to_eval = args.models or ALL_MODELS

    # 1. Cargar predicciones de cada modelo disponible
    all_results = {}
    for model_name in models_to_eval:
        pred_file = results_dir / f"{model_name}_predictions.json"
        if not pred_file.exists():
            logger.warning("No se encontraron predicciones para %s en %s. Omitiendo.", model_name, pred_file)
            continue

        logger.info("Cargando predicciones de %s...", model_name)
        predictions = load_results(str(pred_file))

        y_true = predictions["y_true"]
        y_pred = predictions["y_pred"]
        y_prob = predictions.get("y_prob")
        class_names = predictions.get("class_names", HAM10000_CLASSES)

        # Filtrar predicciones inválidas (UNKNOWN = -1 para VLMs)
        valid_indices = [i for i in range(len(y_pred)) if y_pred[i] >= 0]
        if len(valid_indices) < len(y_pred):
            logger.info(
                "%s: %d/%d predicciones válidas (%.1f%% unknown)",
                model_name,
                len(valid_indices),
                len(y_pred),
                100 * (1 - len(valid_indices) / len(y_pred)),
            )
            y_true_valid = [y_true[i] for i in valid_indices]
            y_pred_valid = [y_pred[i] for i in valid_indices]
            y_prob_valid = (
                np.array([y_prob[i] for i in valid_indices])
                if y_prob is not None
                else None
            )
        else:
            y_true_valid = y_true
            y_pred_valid = y_pred
            y_prob_valid = np.array(y_prob) if y_prob is not None else None

        # Computar métricas
        metrics = evaluate_classification(
            y_true_valid, y_pred_valid, y_prob_valid, class_names
        )
        all_results[model_name] = metrics

        # Log detallado por modelo
        logger.info("=== %s ===", model_name)
        logger.info("  Accuracy:            %.4f", metrics["accuracy"])
        logger.info("  F1 (weighted):       %.4f", metrics["f1_weighted"])
        logger.info("  AUC-ROC (macro):     %s", metrics["auc_roc_macro"])
        logger.info("  Sensibilidad (macro):%.4f", metrics["sensitivity_macro"])
        logger.info("  Especificidad (macro):%.4f", metrics["specificity_macro"])

        # Log por clase
        for i, cls_name in enumerate(class_names):
            logger.info(
                "  %s - Sens: %.4f, Espec: %.4f",
                cls_name,
                metrics["sensitivity_per_class"][i],
                metrics["specificity_per_class"][i],
            )

        # Guardar resultados individuales detallados
        save_results(
            {
                "model": model_name,
                "accuracy": metrics["accuracy"],
                "f1_weighted": metrics["f1_weighted"],
                "auc_roc_macro": metrics["auc_roc_macro"],
                "sensitivity_macro": metrics["sensitivity_macro"],
                "specificity_macro": metrics["specificity_macro"],
                "sensitivity_per_class": metrics["sensitivity_per_class"],
                "specificity_per_class": metrics["specificity_per_class"],
                "confusion_matrix": metrics["confusion_matrix"],
                "classification_report": metrics["classification_report"],
            },
            str(results_dir / f"{model_name}_test_results.json"),
        )

    # 2. Generar tabla comparativa
    if not all_results:
        logger.error("No se encontraron resultados para ningún modelo.")
        sys.exit(1)

    logger.info("Generando tabla comparativa con %d modelos...", len(all_results))
    comparison_data = {}
    for model_name, metrics in all_results.items():
        comparison_data[model_name] = {
            metric: metrics.get(metric) for metric in COMPARISON_METRICS
        }

    output_path = args.output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df = build_comparison_table(comparison_data, COMPARISON_METRICS, output_path)

    logger.info("=== Tabla Comparativa Fase 1 ===")
    logger.info("\n%s", df.to_string(index=False))
    logger.info("Tabla guardada en %s", output_path)


if __name__ == "__main__":
    main()
