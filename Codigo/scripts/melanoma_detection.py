"""B1 + D1 (plan cierre agosto) — Evaluación clínica de detección de melanoma.

Responde la pregunta del tutor: "¿qué tan bien detecta el sistema el melanoma?" — más allá de las 7
clases. Sobre las probabilidades ya guardadas de los clasificadores (MEL = índice 0):

  - Binario MELANOMA-vs-resto: score = P(MEL).
  - Jerárquico MALIGNO-vs-benigno: maligno = {MEL, BCC, AKIEC} (índices 0,2,3), score = suma de sus probs.
  - Suite clínica: AUC-ROC, PR-AUC, sensibilidad, especificidad, VPN, tasa de falsos negativos (FN) de
    melanoma, y macro-AUC one-vs-rest (7 clases).
  - Punto de operación: por argmax, por Youden (J), y optimizado para sensibilidad a especificidad objetivo
    (clínicamente: minimizar FN de melanoma).
  - Ensamble de clasificadores (voto suave) para el mejor punto.

100% local, sin GPU. Uso:
    python scripts/melanoma_detection.py
"""

import argparse
import json
import logging
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# HAM order: MEL, NV, BCC, AKIEC, BKL, DF, VASC
MEL = 0
MALIGNANT = [0, 2, 3]  # MEL, BCC, AKIEC (pre)maligno
# Probs con TTA (config de despliegue). Test + validación (umbral se fija en VAL y se aplica a TEST).
SOURCES = {
    "Swin-Tiny (TTA)": "outputs/results/classifier_ensemble/swin_tiny_tta_predictions.json",
    "ConvNeXt-Tiny (TTA)": "outputs/results/classifier_ensemble/convnext_tiny_tta_predictions.json",
}
VAL_SOURCES = {
    "Swin-Tiny (TTA)": "outputs/results/classifier_ensemble/swin_tiny_tta_val_predictions.json",
    "ConvNeXt-Tiny (TTA)": "outputs/results/classifier_ensemble/convnext_tiny_tta_val_predictions.json",
}


def _load(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return np.asarray(d["y_true"]), np.asarray(d["y_prob"], dtype=float)


def _binary_metrics(y_bin, score, thr):
    """Sens, esp, VPN, FN a un umbral dado."""
    pred = (score >= thr).astype(int)
    tp = int(((pred == 1) & (y_bin == 1)).sum()); fn = int(((pred == 0) & (y_bin == 1)).sum())
    tn = int(((pred == 0) & (y_bin == 0)).sum()); fp = int(((pred == 1) & (y_bin == 0)).sum())
    sens = tp / max(tp + fn, 1); spec = tn / max(tn + fp, 1)
    npv = tn / max(tn + fn, 1); fn_rate = fn / max(tp + fn, 1)
    return {"thr": round(float(thr), 3), "sens": round(sens, 3), "spec": round(spec, 3),
            "npv": round(npv, 3), "fn_rate": round(fn_rate, 3), "tp": tp, "fn": fn, "fp": fp, "tn": tn}


def _thr_at_spec(y_bin, score, target_spec):
    """Menor umbral que alcanza especificidad >= objetivo (maximiza sensibilidad a esa esp)."""
    fpr, tpr, thr = roc_curve(y_bin, score)
    spec = 1 - fpr
    ok = np.where(spec >= target_spec)[0]
    return float(thr[ok[np.argmax(tpr[ok])]]) if len(ok) else 0.5


def _youden(y_bin, score):
    fpr, tpr, thr = roc_curve(y_bin, score)
    return float(thr[np.argmax(tpr - fpr)])


def _macro_auc_ovr(y_true, prob):
    aucs = []
    for c in range(prob.shape[1]):
        yb = (y_true == c).astype(int)
        if yb.sum() and yb.sum() < len(yb):
            aucs.append(roc_auc_score(yb, prob[:, c]))
    return float(np.mean(aucs))


def _score(prob, positive_idx):
    return prob[:, positive_idx].sum(axis=1) if len(positive_idx) > 1 else prob[:, positive_idx[0]]


def _task_report(name, y_true, prob, positive_idx, y_val=None, prob_val=None):
    """Reporte binario. Si se pasan datos de VALIDACIÓN, los umbrales (Youden, esp>=85) se fijan en
    val y se aplican a test (sin sesgo optimista). AUC/PR-AUC son sobre test (no dependen del umbral)."""
    y_bin = np.isin(y_true, positive_idx).astype(int)
    score = _score(prob, positive_idx)
    auc = roc_auc_score(y_bin, score); prauc = average_precision_score(y_bin, score)
    base = y_bin.mean()
    argmax_pos = np.isin(prob.argmax(1), positive_idx).astype(int)
    op_argmax = _binary_metrics(y_bin, argmax_pos.astype(float), 0.5)

    # Fuente para fijar el umbral: val si está, si no test (ilustrativo).
    if y_val is not None:
        yv = np.isin(y_val, positive_idx).astype(int); sv = _score(prob_val, positive_idx)
        thr_src = "val"
    else:
        yv, sv, thr_src = y_bin, score, "test"
    thr_y = _youden(yv, sv); thr_s = _thr_at_spec(yv, sv, 0.85)
    op_youden = _binary_metrics(y_bin, score, thr_y)   # evaluado SIEMPRE en test
    op_spec85 = _binary_metrics(y_bin, score, thr_s)
    logger.info("[%s] %s | AUC=%.3f PR-AUC=%.3f (prev=%.3f) [umbral fijado en %s]",
                name, _TASK[tuple(positive_idx)], auc, prauc, base, thr_src)
    logger.info("    argmax : sens=%.3f esp=%.3f VPN=%.3f FN=%.3f (FN=%d)",
                op_argmax["sens"], op_argmax["spec"], op_argmax["npv"], op_argmax["fn_rate"], op_argmax["fn"])
    logger.info("    Youden : sens=%.3f esp=%.3f VPN=%.3f FN=%.3f (thr=%.2f)",
                op_youden["sens"], op_youden["spec"], op_youden["npv"], op_youden["fn_rate"], op_youden["thr"])
    logger.info("    esp>=85: sens=%.3f esp=%.3f VPN=%.3f FN=%.3f (thr=%.2f)",
                op_spec85["sens"], op_spec85["spec"], op_spec85["npv"], op_spec85["fn_rate"], op_spec85["thr"])
    return {"task": _TASK[tuple(positive_idx)], "auc_roc": round(auc, 3), "pr_auc": round(prauc, 3),
            "prevalence": round(float(base), 3), "threshold_fit_on": thr_src,
            "op_argmax": op_argmax, "op_youden": op_youden, "op_spec85": op_spec85}


_TASK = {(0,): "melanoma-vs-resto", (0, 2, 3): "maligno-vs-benigno"}


def main():
    parser = argparse.ArgumentParser(description="B1+D1 Detección de melanoma")
    parser.add_argument("--out", default="outputs/results/melanoma/melanoma_detection.json")
    args = parser.parse_args()

    probs = {}; probs_val = {}; y_ref = None; y_val = None
    for name, path in SOURCES.items():
        if not Path(path).exists():
            logger.warning("SKIP %s (%s)", name, path); continue
        yt, pr = _load(path)
        if y_ref is None: y_ref = yt
        elif not np.array_equal(yt, y_ref):
            logger.error("y_true de %s no coincide", name); return
        probs[name] = pr
        vpath = VAL_SOURCES.get(name)
        if vpath and Path(vpath).exists():
            yv, pv = _load(vpath)
            if y_val is None: y_val = yv
            probs_val[name] = pv
    if y_val is None:
        logger.warning("Sin probs de validación: los umbrales se fijan en TEST (ilustrativo).")

    results = {}
    for name, pr in probs.items():
        pv = probs_val.get(name)
        logger.info("=== %s (macro-AUC OvR = %.3f) ===", name, _macro_auc_ovr(y_ref, pr))
        results[name] = {
            "macro_auc_ovr": round(_macro_auc_ovr(y_ref, pr), 3),
            "melanoma": _task_report(name, y_ref, pr, [MEL], y_val if pv is not None else None, pv),
            "maligno": _task_report(name, y_ref, pr, MALIGNANT, y_val if pv is not None else None, pv),
        }

    # Ensamble de clasificadores (voto suave)
    if len(probs) >= 2:
        ens = np.mean(list(probs.values()), axis=0)
        ens_val = np.mean(list(probs_val.values()), axis=0) if len(probs_val) == len(probs) else None
        logger.info("=== ENSAMBLE voto suave (%s) | macro-AUC OvR = %.3f ===",
                    "+".join(probs), _macro_auc_ovr(y_ref, ens))
        results["Ensamble (voto suave)"] = {
            "macro_auc_ovr": round(_macro_auc_ovr(y_ref, ens), 3),
            "melanoma": _task_report("Ensamble", y_ref, ens, [MEL], y_val if ens_val is not None else None, ens_val),
            "maligno": _task_report("Ensamble", y_ref, ens, MALIGNANT, y_val if ens_val is not None else None, ens_val),
        }

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
