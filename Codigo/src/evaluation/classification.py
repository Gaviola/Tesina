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
            # Normalizar siempre: TTA averaging en bf16 puede producir filas que no suman 1.0
            y_prob_norm = y_prob / y_prob.sum(axis=1, keepdims=True).clip(min=1e-12)
            present_classes = sorted(set(y_true))
            n_classes = y_prob_norm.shape[1] if y_prob_norm.ndim == 2 else None
            if n_classes is not None and len(present_classes) < n_classes:
                # Restringir a clases efectivamente presentes en y_true.
                y_prob_restricted = y_prob_norm[:, present_classes]
                y_prob_restricted = y_prob_restricted / y_prob_restricted.sum(
                    axis=1, keepdims=True
                ).clip(min=1e-12)
                results["auc_roc_macro"] = roc_auc_score(
                    y_true, y_prob_restricted, multi_class="ovr", average="macro",
                    labels=present_classes,
                )
            else:
                results["auc_roc_macro"] = roc_auc_score(
                    y_true, y_prob_norm, multi_class="ovr", average="macro"
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


# ---------------------------------------------------------------------------
# Calibración (P0.1 — plan julio-agosto): ¿cuando el modelo dice 99% de
# confianza, realmente acierta el 99%? Todas operan sobre y_prob (N, num_classes).
# ---------------------------------------------------------------------------
def _confidence_and_correct(y_true, y_prob):
    """Devuelve (confianza=max prob, correcto=1/0) por muestra, con y_prob normalizado."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True).clip(min=1e-12)
    conf = y_prob.max(axis=1)
    correct = (y_prob.argmax(axis=1) == y_true).astype(float)
    return conf, correct


def reliability_curve(y_true, y_prob, n_bins: int = 10) -> list[dict]:
    """Datos para el reliability diagram: por bin de confianza, confianza media,
    exactitud observada y conteo."""
    conf, correct = _confidence_and_correct(y_true, y_prob)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(conf, edges[1:-1], right=False)
    out = []
    for b in range(n_bins):
        mask = idx == b
        count = int(mask.sum())
        out.append({
            "bin_lower": float(edges[b]),
            "bin_upper": float(edges[b + 1]),
            "count": count,
            "avg_confidence": float(conf[mask].mean()) if count else None,
            "accuracy": float(correct[mask].mean()) if count else None,
        })
    return out


def expected_calibration_error(y_true, y_prob, n_bins: int = 10) -> tuple[float, float]:
    """ECE (promedio ponderado del gap |exactitud - confianza|) y MCE (gap máximo)."""
    conf, correct = _confidence_and_correct(y_true, y_prob)
    n = len(conf)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.digitize(conf, edges[1:-1], right=False)
    ece, mce = 0.0, 0.0
    for b in range(n_bins):
        mask = idx == b
        m = int(mask.sum())
        if m == 0:
            continue
        gap = abs(correct[mask].mean() - conf[mask].mean())
        ece += (m / n) * gap
        mce = max(mce, gap)
    return float(ece), float(mce)


def brier_score_multiclass(y_true, y_prob) -> float:
    """Brier multiclase: media de la suma de cuadrados (prob - onehot). Rango [0, 2]."""
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob, dtype=float)
    y_prob = y_prob / y_prob.sum(axis=1, keepdims=True).clip(min=1e-12)
    n, k = y_prob.shape
    onehot = np.zeros((n, k))
    onehot[np.arange(n), y_true] = 1.0
    return float(np.mean(np.sum((y_prob - onehot) ** 2, axis=1)))


def evaluate_calibration(y_true, y_prob, n_bins: int = 10) -> dict:
    """Resumen de calibración: ECE, MCE, Brier y curva de fiabilidad."""
    ece, mce = expected_calibration_error(y_true, y_prob, n_bins)
    return {
        "ece": ece,
        "mce": mce,
        "brier": brier_score_multiclass(y_true, y_prob),
        "n_bins": n_bins,
        "n_samples": int(len(y_true)),
        "reliability_curve": reliability_curve(y_true, y_prob, n_bins),
    }
