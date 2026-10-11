"""P0.1 (plan julio-agosto) — Calibración de clasificadores.

Calcula ECE, MCE y Brier score, y dibuja reliability diagrams, sobre los
``*_predictions.json`` que ya contienen ``y_prob``. Responde la pregunta del
tutor: "cuando el modelo dice 99% de confianza, ¿realmente acierta el 99%?".

100% local, no requiere GPU ni cluster (opera sobre probabilidades ya guardadas).

Uso:
    python scripts/evaluate_calibration.py
    python scripts/evaluate_calibration.py --pred_glob "outputs/results/**/otro_*_predictions.json"
    python scripts/evaluate_calibration.py --n_bins 15
    # Con histograma de confianza y etiquetas legibles (partición por lesión):
    python scripts/evaluate_calibration.py --hist \
        --pred_glob outputs/results/swin_tiny_sweep_t06_les_cwnone_predictions.json ... \
        --labels "swin_tiny_sweep_t06_les_cwnone=Swin-Tiny" --output_dir outputs/results/calibration_les
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
    parser.add_argument("--hist", action="store_true",
                        help="Agrega debajo el histograma de confianza: muestra en qué bins se concentran "
                             "las predicciones, que es lo que pondera el ECE.")
    parser.add_argument("--labels", nargs="*", default=[],
                        help='Etiquetas "RUN=Etiqueta", con RUN = nombre del archivo sin _predictions.json.')
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
        run = path.name.replace("_predictions.json", "")
        label = dict(x.split("=", 1) for x in args.labels).get(run) or _model_label(path, data)
        cal = evaluate_calibration(y_true, y_prob, n_bins=args.n_bins)
        acc = float((y_prob.argmax(axis=1) == np.asarray(y_true)).mean())
        cal.update({"label": label, "accuracy": acc, "source": str(path)})
        summary.append(cal)
        logger.info("%-28s acc=%.3f  ECE=%.3f  MCE=%.3f  Brier=%.3f  (n=%d)",
                    label, acc, cal["ece"], cal["mce"], cal["brier"], cal["n_samples"])

    if not summary:
        logger.error("Ningún archivo tenía 'y_prob'. Nada que calibrar.")
        return

    # Reliability diagram: un solo panel, una curva por modelo (exactitud vs confianza).
    # Las curvas POR ENCIMA de la diagonal indican sub-confianza; por debajo, sobre-confianza.
    if args.hist:
        fig, (ax, axh) = plt.subplots(2, 1, figsize=(6.8, 8.2), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 1.3]})
    else:
        fig, ax = plt.subplots(figsize=(6.8, 5.8))
    ax.plot([0, 1], [0, 1], "--", color="gray", lw=1.2, label="calibración perfecta")
    ax.fill_between([0, 1], [0, 1], [1, 1], color="#1565C0", alpha=0.05)
    ax.fill_between([0, 1], [0, 0], [0, 1], color="#C62828", alpha=0.05)
    ax.text(0.03, 0.9, "sub-confianza", color="#1565C0", fontsize=9)
    ax.text(0.40, 0.04, "sobre-confianza", color="#C62828", fontsize=9)
    for s in sorted(summary, key=lambda x: x["ece"]):
        xs = [b["avg_confidence"] for b in s["reliability_curve"] if b["count"]]
        ys = [b["accuracy"] for b in s["reliability_curve"] if b["count"]]
        ax.plot(xs, ys, marker="o", ms=4, lw=1.6, label=f"{s['label']}  (ECE={s['ece']:.2f})")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel("Confianza media del modelo (probabilidad máxima)")
    ax.set_ylabel("Exactitud observada")
    ax.set_title("Reliability diagram — HAM10000\n(curvas por encima de la diagonal = el modelo subestima su certeza)")
    ax.legend(fontsize=8, loc="lower right")
    if args.hist:
        width = 1.0 / args.n_bins
        curves = sorted(summary, key=lambda x: x["ece"])
        bar_w = width / (len(curves) + 1)
        for i, s in enumerate(curves):
            n = sum(b["count"] for b in s["reliability_curve"])
            lefts = [j * width + (i + 0.5) * bar_w for j in range(len(s["reliability_curve"]))]
            axh.bar(lefts, [b["count"] / n for b in s["reliability_curve"]], width=bar_w,
                    color=ax.lines[i + 1].get_color(), align="edge")
        axh.set_ylabel("Fracción de\npredicciones")
        axh.set_xlabel("Confianza media del modelo (probabilidad máxima)")
        ax.set_xlabel("")
    fig.tight_layout()
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
