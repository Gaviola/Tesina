"""P0.1 (plan julio-agosto) — Calibración de clasificadores.

Calcula ECE, MCE y Brier score, y dibuja reliability diagrams, sobre los
``*_predictions.json`` que ya contienen ``y_prob``. Responde la pregunta del
tutor: "cuando el modelo dice 99% de confianza, ¿realmente acierta el 99%?".

100% local, no requiere GPU ni cluster (opera sobre probabilidades ya guardadas).

Uso:
    python scripts/evaluate_calibration.py
    python scripts/evaluate_calibration.py --pred_glob "outputs/results/**/otro_*_predictions.json"
    python scripts/evaluate_calibration.py --n_bins 15
"""

import argparse
import glob
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.classification import evaluate_calibration

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_GLOBS = [
    "outputs/results/classifiers/modern_v3/*_predictions.json",
    "outputs/results/dermlip/*_predictions.json",
]


def _model_label(path: Path, data: dict) -> str:
    name = data.get("run_name") or data.get("model") or path.stem.replace("_predictions", "")
    return str(name)


def _plot_reliability(ax, curve: list[dict], label: str, ece: float, brier: float):
    centers, accs, confs, counts = [], [], [], []
    for b in curve:
        c = 0.5 * (b["bin_lower"] + b["bin_upper"])
        centers.append(c)
        counts.append(b["count"])
        accs.append(b["accuracy"] if b["accuracy"] is not None else np.nan)
        confs.append(b["avg_confidence"] if b["avg_confidence"] is not None else np.nan)
    centers = np.array(centers)
    accs = np.array(accs, dtype=float)
    width = (curve[0]["bin_upper"] - curve[0]["bin_lower"]) * 0.9

    ax.plot([0, 1], [0, 1], "--", color="gray", lw=1, label="calibración perfecta")
    ax.bar(centers, accs, width=width, color="#1565C0", alpha=0.75, edgecolor="white",
           label="exactitud observada")
    # Gap (confianza - exactitud) sombreado sobre cada barra presente
    for c, a, cf in zip(centers, accs, confs):
        if np.isnan(a) or cf is None or np.isnan(cf):
            continue
        lo, hi = min(a, cf), max(a, cf)
        ax.bar(c, hi - lo, bottom=lo, width=width, color="#C62828", alpha=0.30,
               edgecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Confianza (prob. máx.)")
    ax.set_ylabel("Exactitud")
    ax.set_title(f"{label}\nECE={ece:.3f}  Brier={brier:.3f}", fontsize=10)
    ax.legend(fontsize=7, loc="upper left")


def main():
    parser = argparse.ArgumentParser(description="P0.1 Calibración de clasificadores")
    parser.add_argument("--pred_glob", nargs="+", default=None,
                        help="Globs de *_predictions.json (default: modern_v3 + dermlip)")
    parser.add_argument("--n_bins", type=int, default=10)
    parser.add_argument("--output_dir", type=str, default="outputs/results/calibration")
    args = parser.parse_args()

    globs = args.pred_glob or DEFAULT_GLOBS
    paths = sorted({Path(p) for g in globs for p in glob.glob(g, recursive=True)})
    if not paths:
        logger.error("No se encontraron predicciones con los globs: %s", globs)
        return

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if "y_prob" not in data or not data["y_prob"]:
            logger.warning("SKIP %s: sin 'y_prob' (necesita re-eval guardando probabilidades)",
                           path.name)
            continue
        y_true = data["y_true"]
        y_prob = np.asarray(data["y_prob"], dtype=float)
        label = _model_label(path, data)
        cal = evaluate_calibration(y_true, y_prob, n_bins=args.n_bins)
        acc = float((y_prob.argmax(axis=1) == np.asarray(y_true)).mean())
        cal.update({"label": label, "accuracy": acc, "source": str(path)})
        summary.append(cal)
        logger.info("%-28s acc=%.3f  ECE=%.3f  MCE=%.3f  Brier=%.3f  (n=%d)",
                    label, acc, cal["ece"], cal["mce"], cal["brier"], cal["n_samples"])

    if not summary:
        logger.error("Ningún archivo tenía 'y_prob'. Nada que calibrar.")
        return

    # Reliability diagrams (grid)
    ncols = 2
    nrows = (len(summary) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4.2 * nrows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for i, s in enumerate(summary):
        ax = axes[i // ncols][i % ncols]
        ax.axis("on")
        _plot_reliability(ax, s["reliability_curve"], s["label"], s["ece"], s["brier"])
    fig.suptitle("Reliability diagrams — HAM10000 (rojo = brecha confianza-exactitud)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    png = out_dir / "reliability_diagrams.png"
    fig.savefig(png, dpi=150)
    logger.info("Figura guardada en %s", png)

    out_json = out_dir / "calibration_summary.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resumen guardado en %s", out_json)

    # Tabla resumen a stdout
    print("\n=== Calibración (n_bins=%d) ===" % args.n_bins)
    print(f"{'Modelo':<28} {'Acc':>6} {'ECE':>7} {'MCE':>7} {'Brier':>7}")
    for s in sorted(summary, key=lambda x: x["ece"]):
        print(f"{s['label']:<28} {s['accuracy']:>6.3f} {s['ece']:>7.3f} "
              f"{s['mce']:>7.3f} {s['brier']:>7.3f}")


if __name__ == "__main__":
    main()
