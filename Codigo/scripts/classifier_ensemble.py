"""P5.1 — Ensamble de clasificadores por voto suave (promedio de probabilidades).

Combina los ``y_prob`` ya guardados de los clasificadores modern_v3 (mismo test HAM, n=1503,
filas alineadas: y_true idéntico) y evalúa si el ensamble supera al mejor individual (Swin).
Métrica clave: sensibilidad macro (= balanced accuracy = recall macro).

100% local, no requiere GPU ni cluster.

Uso:
    python scripts/classifier_ensemble.py
"""

import argparse
import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

MODELS = {
    "swin": "outputs/results/classifiers/modern_v3/swin_tiny_modern_v3_predictions.json",
    "convnext": "outputs/results/classifiers/modern_v3/convnext_tiny_modern_v3_predictions.json",
    "densenet": "outputs/results/classifiers/modern_v3/densenet_modern_v3_predictions.json",
    "vit": "outputs/results/classifiers/modern_v3/vit_modern_v3_predictions.json",
}


def _metrics(y_true, y_prob):
    y_pred = np.asarray(y_prob).argmax(axis=1)
    return {
        "acc": accuracy_score(y_true, y_pred),
        "f1_w": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "sens_macro": balanced_accuracy_score(y_true, y_pred),
    }


def main():
    parser = argparse.ArgumentParser(description="P5.1 Ensamble de clasificadores (voto suave)")
    parser.add_argument("--output_dir", type=str, default="outputs/results/classifier_ensemble")
    args = parser.parse_args()

    probs, y_true = {}, None
    for name, path in MODELS.items():
        p = Path(path)
        if not p.exists():
            logger.warning("SKIP %s: no existe %s", name, path)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        yt = d["y_true"]
        if y_true is None:
            y_true = yt
        elif yt != y_true:
            logger.error("y_true de %s no coincide con el resto. Abortando.", name)
            return
        probs[name] = np.asarray(d["y_prob"], dtype=float)

    y_true = np.asarray(y_true)
    logger.info("Clasificadores cargados: %s (n=%d)", list(probs), len(y_true))

    rows = []
    # Individuales
    for name, pr in probs.items():
        m = _metrics(y_true, pr)
        rows.append({"combo": name, "n_models": 1, **m})

    # Ensambles: todas las combinaciones de >=2 (priorizando las que incluyen swin)
    names = list(probs)
    for k in range(2, len(names) + 1):
        for combo in combinations(names, k):
            avg = np.mean([probs[n] for n in combo], axis=0)
            m = _metrics(y_true, avg)
            rows.append({"combo": "+".join(combo), "n_models": k, **m})

    rows.sort(key=lambda r: r["sens_macro"], reverse=True)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ensemble_results.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    best_indiv = max((r for r in rows if r["n_models"] == 1), key=lambda r: r["sens_macro"])
    print(f"\n=== Ensamble de clasificadores (n={len(y_true)}) ===")
    print(f"{'Combo':<32} {'#':>2} {'Acc':>6} {'F1-w':>6} {'Sens.macro':>10}")
    for r in rows:
        flag = "  <- mejor individual" if r["combo"] == best_indiv["combo"] else ""
        print(f"{r['combo']:<32} {r['n_models']:>2} {r['acc']:>6.3f} {r['f1_w']:>6.3f} "
              f"{r['sens_macro']:>10.3f}{flag}")

    best = rows[0]
    print(f"\nMejor global: {best['combo']} (sens_macro={best['sens_macro']:.3f}) "
          f"vs mejor individual {best_indiv['combo']} ({best_indiv['sens_macro']:.3f}) "
          f"-> Δ={best['sens_macro']-best_indiv['sens_macro']:+.3f}")


if __name__ == "__main__":
    main()
