"""Métricas de clasificación para Fase 1.

Métricas: Accuracy, AUC-ROC (macro), F1-Score ponderado, Sensibilidad, Especificidad.
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)


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
            results["auc_roc_macro"] = roc_auc_score(
                y_true, y_prob, multi_class="ovr", average="macro"
            )
        except ValueError:
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
