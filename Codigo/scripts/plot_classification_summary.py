"""Figura resumen de clasificación por enfoque (VLM general → DermLIP → supervisado).

Reemplaza a ``F1_clasificacion.png`` del documento de experimentación, que se armó a mano con los
números de la partición por imagen y rotulaba como «gen ZS» barras que eran de *likelihood scoring*.
Acá todo sale de los JSON:

  - LLaVA-Med / Mini-VLM: *likelihood scoring* zero-shot (``{model}/v1/*_likelihood_predictions.json``).
  - DermLIP zero-shot: ``dermlip/dermlip_zeroshot_vit-b-16_predictions.json`` (no depende de la partición).
  - DermLIP *linear probe*: ``dermlip/dermlip_split_eval.json`` (re-ajustado sobre el train por lesión).
  - Swin-Tiny y ConvNeXt-Tiny: ganadores de la partición por lesión, media ± sd de 3 semillas
    (``lesion_split_report.json``).

Métricas: exactitud, F1 macro y sensibilidad macro (la línea punteada es el azar, 1/7). Colores de la
paleta Okabe–Ito, distinguibles también en escala de grises por la trama.

100% local. Uso:
    python scripts/plot_classification_summary.py
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, recall_score

R = Path("outputs/results")
METRICS = [("acc", "Exactitud"), ("f1_macro", "F1 macro"), ("sens_macro", "Sensibilidad macro")]
COLORS = ["#999999", "#0072B2", "#E69F00"]  # Okabe–Ito (gris, azul, naranja)
HATCHES = ["", "//", ".."]


def _from_preds(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    y = np.asarray(d["y_true"])
    p = np.asarray(d["y_pred"]) if "y_pred" in d else np.asarray(d["y_prob"]).argmax(1)
    return {"acc": (accuracy_score(y, p), 0.0),
            "f1_macro": (f1_score(y, p, average="macro", zero_division=0), 0.0),
            "sens_macro": (recall_score(y, p, average="macro", zero_division=0), 0.0)}


def collect():
    rows = {}
    rows["LLaVA-Med\n(ZS, likelihood)"] = _from_preds(R / "llava_med/v1/llava_med_likelihood_predictions.json")
    rows["Mini-VLM\n(ZS, likelihood)"] = _from_preds(R / "mini_vlm/v1/mini_vlm_likelihood_predictions.json")
    rows["DermLIP\n(zero-shot)"] = _from_preds(R / "dermlip/dermlip_zeroshot_vit-b-16_predictions.json")
    lp = json.loads((R / "dermlip/dermlip_split_eval.json").read_text(encoding="utf-8"))["lesion"]["linear-probe (LogReg)"]
    rows["DermLIP\n(linear probe)"] = {k: (lp[k], 0.0) for k, _ in METRICS}
    win = json.loads((R / "lesion_split_report.json").read_text(encoding="utf-8"))["ganadores"]
    for key, name in (("convnext_tiny", "ConvNeXt-Tiny\n(supervisado)"), ("swin_tiny", "Swin-Tiny\n(supervisado)")):
        ms = win[key]["test_media_std"]
        rows[name] = {k: (ms[k]["mean"], ms[k]["std"]) for k, _ in METRICS}
    return rows


def main():
    parser = argparse.ArgumentParser(description="Figura resumen de clasificación por enfoque")
    parser.add_argument("--output", default="outputs/results/classification_summary_les.png")
    args = parser.parse_args()

    rows = collect()
    names = list(rows)
    x = np.arange(len(names)); w = 0.26
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for i, ((key, label), color, hatch) in enumerate(zip(METRICS, COLORS, HATCHES)):
        vals = [rows[n][key][0] for n in names]
        errs = [rows[n][key][1] for n in names]
        ax.bar(x + (i - 1) * w, vals, w, color=color, hatch=hatch, edgecolor="black", linewidth=0.5,
               label=label)
        has_sd = [j for j, e in enumerate(errs) if e]  # solo los modelos con varias semillas
        ax.errorbar(x[has_sd] + (i - 1) * w, [vals[j] for j in has_sd], yerr=[errs[j] for j in has_sd],
                    fmt="none", ecolor="black", capsize=3, lw=1)
    ax.axhline(1 / 7, ls="--", color="gray", lw=1)
    ax.text(-0.45, 1 / 7 + 0.015, "azar (1/7)", color="gray", fontsize=8, ha="left")
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9)
    ax.set_ylim(0, 1); ax.set_ylabel("Métrica (test HAM10000, n = 1503)")
    ax.legend(ncol=3, fontsize=9, loc="upper left")
    ax.set_title("Clasificación por enfoque — partición disjunta por lesión\n"
                 "(supervisados: media ± desvío de 3 semillas)", fontsize=11)
    fig.tight_layout()
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    (out.with_suffix(".json")).write_text(
        json.dumps({n.replace("\n", " "): {k: v[0] for k, v in r.items()} for n, r in rows.items()},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    for n in names:
        print(f"{n.replace(chr(10), ' '):34s}" + "  ".join(f"{k} {rows[n][k][0]:.3f}" for k, _ in METRICS))
    print("Figura:", out)


if __name__ == "__main__":
    main()
