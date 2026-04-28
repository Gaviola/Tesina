"""Métricas de clasificación para Fase 1.

Métricas: Accuracy, AUC-ROC (macro), F1-Score ponderado, Sensibilidad, Especificidad.
"""

import logging

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


def evaluate_classification(
    y_true: list[int],
    y_pred: list[int],
    y_prob: np.ndarray | None = None,
    class_names: list[str] | None = None,
) -> dict:
    """Calcula métricas de clasificación completas.

    Args:
        y_true: Etiquetas verdaderas.
        y_pred: Predicciones del modelo.
        y_prob: Probabilidades por clase (N, num_classes) para AUC-ROC.
        class_names: Nombres de las clases.

    Returns:
        Dict con accuracy, f1_weighted, auc_roc_macro, sensitivity, specificity,
        confusion_matrix, y classification_report.
    """
    results = {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }

    # AUC-ROC (requiere probabilidades)
    if y_prob is not None:
        try:
            present_classes = sorted(set(y_true))
            n_classes = y_prob.shape[1] if y_prob.ndim == 2 else None
            if n_classes is not None and len(present_classes) < n_classes:
                # Restringir a clases efectivamente presentes en y_true.
                y_prob_restricted = y_prob[:, present_classes]
                # Renormalizar para que las filas sumen 1.
                y_prob_restricted = y_prob_restricted / y_prob_restricted.sum(
                    axis=1, keepdims=True
                ).clip(min=1e-12)
                results["auc_roc_macro"] = roc_auc_score(
                    y_true, y_prob_restricted, multi_class="ovr", average="macro",
                    labels=present_classes,
                )
            else:
                results["auc_roc_macro"] = roc_auc_score(
                    y_true, y_prob, multi_class="ovr", average="macro"
                )
        except (ValueError, IndexError) as e:
            logger.warning("AUC-ROC no calculable: %s", e)
            results["auc_roc_macro"] = None
    else:
        results["auc_roc_macro"] = None

    # Sensibilidad y especificidad por clase
    cm = confusion_matrix(y_true, y_pred)
    results["confusion_matrix"] = cm.tolist()

    sensitivities = []
    specificities = []
    for i in range(cm.shape[0]):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        tn = cm.sum() - tp - fn - fp

        sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        sensitivities.append(sens)
        specificities.append(spec)

    results["sensitivity_per_class"] = sensitivities
    results["specificity_per_class"] = specificities
    results["sensitivity_macro"] = np.mean(sensitivities)
    results["specificity_macro"] = np.mean(specificities)

    # Report detallado
    target_names = class_names if class_names else None
    results["classification_report"] = classification_report(
        y_true, y_pred, target_names=target_names, zero_division=0, output_dict=True
    )

    return results
