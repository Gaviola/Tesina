"""P0.5 (plan julio-agosto) — Taxonomía de errores de los reportes generados.

Clasifica cada reporte (report-only) en su tipo de error PRINCIPAL mediante reglas
determinísticas, y agrega la distribución por modelo × condición de grounding. Responde:
¿qué errores desaparecen con el grounding y cuáles persisten aun con un clasificador preciso?

Categorías (prioridad de asignación):
  repeticion  -> degeneración / texto repetido
  contradiccion -> nombra >=2 diagnósticos distintos
  dx_incorrecto -> no menciona el dx correcto pero sí otro
  hedging     -> lenguaje de incertidumbre / diferencial
  insuficiente-> reporte muy corto o sin contenido morfológico
  otros       -> no encaja (p.ej. sin dx pero adecuado)
  ok          -> menciona el dx correcto, sin banderas

(La alucinación clínica no se detecta por reglas de forma fiable; se omite como categoría propia.)

100% local sobre outputs/generated_reports/. Uso:
    python scripts/error_taxonomy.py
"""

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.evaluation.clinical_ner import (
    _compute_entity_recall,
    _extract_dict_entities,
    _normalize_label,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# Términos DISTINTIVOS por clase HAM (word-boundary; evita falsos por substring como "mel").
CLASS_TERMS = {
    "melanoma": [r"melanoma"],
    "nevus": [r"nevus", r"nevi", r"\bmole\b"],
    "basal cell carcinoma": [r"basal cell", r"\bbcc\b", r"basalioma"],
    "actinic keratosis": [r"actinic kerato", r"solar kerato", r"\bakiec\b"],
    "benign keratosis": [r"benign kerato", r"seborrh\w+ kerato", r"\bbkl\b"],
    "dermatofibroma": [r"dermatofibroma"],
    # "vascular lesion" completo, no "vascular" suelto (evita matchear el feature dermoscópico
    # "vascular pattern/structures", que describe morfología, no el diagnóstico).
    "vascular lesion": [r"vascular lesion", r"hemangioma", r"angioma", r"pyogenic granuloma"],
}
CLASS_RE = {c: re.compile("|".join(pats), re.IGNORECASE) for c, pats in CLASS_TERMS.items()}

HEDGE_MARKERS = [
    "may be", "might be", "could be", "possibly", "cannot be determined",
    "cannot determine", "differential diagnosis", "suggestive of", "consistent with",
    "rule out", "uncertain", "further evaluation", "further examination",
    "appears to be", "likely represents", "either ", "unclear", "difficult to",
]

CATEGORIES = ["ok", "hedging", "dx_incorrecto", "contradiccion", "repeticion", "insuficiente", "otros"]
CAT_COLOR = {
    "ok": "#4CAF50", "hedging": "#FB8C00", "dx_incorrecto": "#C62828",
    "contradiccion": "#8E24AA", "repeticion": "#5D4037", "insuficiente": "#90A4AE",
    "otros": "#455A64",
}


def _mentioned_classes(text_lower: str) -> set:
    return {c for c, rx in CLASS_RE.items() if rx.search(text_lower)}


def _is_repetition(text_lower: str) -> bool:
    toks = text_lower.split()
    if len(toks) < 20:
        return False
    uniq_ratio = len(set(toks)) / len(toks)
    grams = Counter(tuple(toks[i:i + 4]) for i in range(len(toks) - 3))
    max_gram = max(grams.values()) if grams else 0
    return uniq_ratio < 0.40 or max_gram >= 4


def _is_hedging(text_lower: str) -> bool:
    return any(h in text_lower for h in HEDGE_MARKERS)


def classify_error(report: str, gt_label: str) -> str:
    text = (report or "").lower().strip()
    toks = text.split()
    recall = _compute_entity_recall(_extract_dict_entities(report or ""))
    mentioned = _mentioned_classes(text)
    gt_c = _normalize_label(gt_label) if gt_label else ""
    gt_ment = gt_c in mentioned
    others = mentioned - {gt_c}

    # Prioridad de asignación
    if _is_repetition(text):
        return "repeticion"
    if len(toks) < 12 or (recall < 0.10 and not gt_ment):
        return "insuficiente"
    if len(mentioned) >= 2:
        return "contradiccion"
    if not gt_ment and others:
        return "dx_incorrecto"
    if _is_hedging(text):
        return "hedging"
    if gt_ment:
        return "ok"
    return "otros"  # adecuado en largo pero sin dx claro


_LABEL_MAP = None


def _gt_from_metadata(image_id: str) -> str:
    """gt_label desde la metadata de HAM10000. Los reportes del re-anclaje (``*_les``) se generaron
    sin ``--label_csv`` y traen gt_label vacío; sin este respaldo todo cae en dx_incorrecto."""
    global _LABEL_MAP
    if _LABEL_MAP is None:
        from scripts.ensemble_bootstrap import build_label_map
        _LABEL_MAP = build_label_map()
    return _LABEL_MAP.get(Path(image_id).stem, "")


def _load_condition(cond_dir: Path) -> list[dict]:
    out = []
    for jf in cond_dir.glob("*.json"):
        d = json.loads(jf.read_text(encoding="utf-8"))
        rep = THINK_RE.sub("", d.get("report", "") or "").strip()
        gt = d.get("gt_label", "") or _gt_from_metadata(d.get("image_id", jf.stem.replace("_report", "")))
        out.append({"report": rep, "gt_label": gt})
    return out


def main():
    parser = argparse.ArgumentParser(description="P0.5 Taxonomía de errores")
    parser.add_argument("--reports_root", type=str, default="outputs/generated_reports")
    parser.add_argument("--models", nargs="+", default=["llava_med", "mini_vlm"])
    parser.add_argument("--conditions", nargs="+",
                        default=["full_baseline", "full_dermlip", "full_swin", "full_oracle"])
    parser.add_argument("--output_dir", type=str, default="outputs/results/error_taxonomy")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    root = Path(args.reports_root)

    summary = {}
    fig, axes = plt.subplots(1, len(args.models), figsize=(6 * len(args.models), 4.5), squeeze=False)

    for mi, model in enumerate(args.models):
        summary[model] = {}
        present = []
        dist_by_cond = {}
        for cond in args.conditions:
            cdir = root / model / cond
            if not cdir.exists():
                continue
            reports = _load_condition(cdir)
            counts = Counter(classify_error(r["report"], r["gt_label"]) for r in reports)
            n = sum(counts.values())
            dist = {c: counts.get(c, 0) / n for c in CATEGORIES}
            summary[model][cond] = {"n": n, "counts": dict(counts), "fraction": dist}
            dist_by_cond[cond] = dist
            present.append(cond)

        # Tabla a stdout
        print(f"\n=== {model} - distribución de errores (fracción; report-only) ===")
        print("categoría".ljust(15) + "".join(c.replace("full_", "").ljust(11) for c in present))
        for cat in CATEGORIES:
            row = cat.ljust(15)
            for c in present:
                row += f"{dist_by_cond[c][cat]:.2f}".ljust(11)
            print(row)

        # Barras apiladas por condición
        ax = axes[0][mi]
        bottoms = np.zeros(len(present))
        x = np.arange(len(present))
        for cat in CATEGORIES:
            vals = np.array([dist_by_cond[c][cat] for c in present])
            ax.bar(x, vals, bottom=bottoms, label=cat, color=CAT_COLOR[cat])
            bottoms += vals
        ax.set_xticks(x)
        ax.set_xticklabels([c.replace("full_", "") for c in present], rotation=20, ha="right", fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_title(f"{model}", fontsize=10)
        if mi == 0:
            ax.set_ylabel("fracción de reportes")

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(CATEGORIES), fontsize=8,
               bbox_to_anchor=(0.5, -0.04))
    fig.suptitle("Taxonomía de errores por condición de grounding", fontsize=12)
    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    png = out_dir / "error_taxonomy.png"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    logger.info("Figura: %s", png)

    (out_dir / "error_taxonomy_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resumen: %s", out_dir / "error_taxonomy_summary.json")


if __name__ == "__main__":
    main()
