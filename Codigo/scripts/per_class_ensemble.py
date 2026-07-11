"""P0.3 (plan julio-agosto) — Análisis POR CLASE del ensamble.

Responde: "MiniVLM mejora con grounding, ¿en qué clases?". Calcula Diagnostic Consistency
y Clinical Entity Recall (report-only) por clase gt, para cada condición de grounding
(baseline / DermLIP / Swin / oracle) y modelo (LLaVA-Med, Mini-VLM).

Además exporta los arrays de consistencia POR REPORTE (alineados por image_id) para los
tests estadísticos del ensamble (P0.2, `statistical_tests.py --consistency_json`).

100% local (los reportes ya están en outputs/generated_reports/). Uso:
    python scripts/per_class_ensemble.py
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.clinical_ner import (
    _compute_entity_recall,
    _extract_dict_entities,
    diagnostic_consistency_flags,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HAM_CLASSES = ["melanoma", "nevus", "basal cell carcinoma", "actinic keratosis",
               "benign keratosis", "dermatofibroma", "vascular lesion"]
COND_LABEL = {"full_baseline": "baseline", "full_dermlip": "DermLIP (0.38)",
              "full_swin": "Swin (0.80)", "full_oracle": "oracle (gt)"}
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_reasoning(t: str) -> str:
    return THINK_RE.sub("", t or "").strip()


def _load_condition(cond_dir: Path, strip: bool) -> dict:
    """image_id -> {report, gt_label} para todos los .json de una condición."""
    out = {}
    for jf in cond_dir.glob("*.json"):
        d = json.loads(jf.read_text(encoding="utf-8"))
        rep = _strip_reasoning(d.get("report", "")) if strip else d.get("report", "")
        out[d.get("image_id", jf.stem)] = {"report": rep, "gt_label": d.get("gt_label", "")}
    return out


def _heatmap(ax, matrix, classes, conditions, title, show_ylabels=True):
    im = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(conditions)))
    ax.set_xticklabels(conditions, rotation=30, ha="right", fontsize=8)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes if show_ylabels else [""] * len(classes), fontsize=8)
    for i in range(len(classes)):
        for j in range(len(conditions)):
            v = matrix[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                        color="black")
    ax.set_title(title, fontsize=10)
    return im


def main():
    parser = argparse.ArgumentParser(description="P0.3 Análisis por clase del ensamble")
    parser.add_argument("--reports_root", type=str, default="outputs/generated_reports")
    parser.add_argument("--models", nargs="+", default=["llava_med", "mini_vlm"])
    parser.add_argument("--conditions", nargs="+",
                        default=["full_baseline", "full_dermlip", "full_swin", "full_oracle"])
    parser.add_argument("--no_strip_reasoning", action="store_true",
                        help="No eliminar <think>...</think> (por defecto se elimina: report-only).")
    parser.add_argument("--output_dir", type=str, default="outputs/results/per_class")
    args = parser.parse_args()

    strip = not args.no_strip_reasoning
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    root = Path(args.reports_root)

    summary = {}
    fig, axes = plt.subplots(1, len(args.models), figsize=(5.5 * len(args.models), 4.5), squeeze=False)
    im = None

    for mi, model in enumerate(args.models):
        conds = {}
        for cond in args.conditions:
            cdir = root / model / cond
            if not cdir.exists():
                logger.warning("SKIP %s/%s: no existe", model, cond)
                continue
            conds[cond] = _load_condition(cdir, strip)
        if not conds:
            continue

        # image_ids comunes a todas las condiciones (para arrays alineados)
        common = sorted(set.intersection(*[set(c.keys()) for c in conds.values()]))
        logger.info("%s: %d image_ids comunes a %d condiciones", model, len(common), len(conds))

        # Consistencia por-reporte alineada (para P0.2) + recall
        cons_arrays = {}      # condición -> [0/1] alineado a `common`
        per_class = defaultdict(dict)  # clase -> condición -> {consistency, recall, n}
        for cond, data in conds.items():
            reports = [data[i]["report"] for i in common]
            gts = [data[i]["gt_label"] for i in common]
            flags = diagnostic_consistency_flags(reports, gts)
            recalls = [_compute_entity_recall(_extract_dict_entities(r)) for r in reports]
            cons_arrays[COND_LABEL.get(cond, cond)] = flags

            by_cls = defaultdict(lambda: {"cons": [], "rec": []})
            for gt, fl, rc in zip(gts, flags, recalls):
                by_cls[gt]["cons"].append(fl)
                by_cls[gt]["rec"].append(rc)
            for cls, v in by_cls.items():
                per_class[cls][cond] = {
                    "consistency": float(np.mean(v["cons"])),
                    "recall": float(np.mean(v["rec"])),
                    "n": len(v["cons"]),
                }
            # global
            per_class["_overall"][cond] = {
                "consistency": float(np.mean(flags)),
                "recall": float(np.mean(recalls)),
                "n": len(flags),
            }

        summary[model] = {k: dict(v) for k, v in per_class.items()}

        # Exportar arrays de consistencia por-reporte para P0.2
        cons_path = out_dir / f"ensemble_consistency_{model}.json"
        cons_path.write_text(json.dumps(cons_arrays, ensure_ascii=False), encoding="utf-8")

        # Tabla a stdout
        present = [c for c in args.conditions if c in conds]
        print(f"\n=== {model} — Diagnostic Consistency por clase (report-only, n por celda) ===")
        header = "clase".ljust(22) + "".join(COND_LABEL.get(c, c).ljust(16) for c in present)
        print(header)
        for cls in HAM_CLASSES + ["_overall"]:
            if cls not in per_class:
                continue
            row = cls.ljust(22)
            for c in present:
                cell = per_class[cls].get(c)
                row += (f"{cell['consistency']:.2f} (n={cell['n']})".ljust(16)) if cell else "-".ljust(16)
            print(row)

        # Heatmap (consistency por clase × condición)
        mat = np.full((len(HAM_CLASSES), len(present)), np.nan)
        for i, cls in enumerate(HAM_CLASSES):
            for j, c in enumerate(present):
                cell = per_class.get(cls, {}).get(c)
                if cell:
                    mat[i, j] = cell["consistency"]
        im = _heatmap(axes[0][mi], mat, HAM_CLASSES, [COND_LABEL.get(c, c) for c in present],
                      f"{model} - consistency por clase", show_ylabels=(mi == 0))

    if im is not None:
        fig.colorbar(im, ax=axes, fraction=0.025, pad=0.02, label="Diagnostic Consistency")
    fig.suptitle("Ensamble: consistencia diagnóstica por clase y condición de grounding", fontsize=12)
    png = out_dir / "per_class_consistency_heatmap.png"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    logger.info("Figura: %s", png)

    (out_dir / "per_class_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resumen: %s", out_dir / "per_class_summary.json")
    logger.info("Arrays de consistencia por-reporte (para P0.2): %s/ensemble_consistency_*.json", out_dir)


if __name__ == "__main__":
    main()
