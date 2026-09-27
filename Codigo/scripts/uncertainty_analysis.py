"""Caracterización del pipeline avanzado (ensamble consciente de la incertidumbre).

Dos análisis, 100% locales sobre datos ya en disco:
  A) Taxonomía de errores CONSCIENTE DEL NIVEL: grounding simple forzado vs pipeline
     de 3 niveles, pareado sobre las mismas imágenes.
  B) Análisis por clase: a qué nivel se rutea cada clase diagnóstica (foco melanoma).

Ajuste metodológico: `error_taxonomy.classify_error` marca "contradiccion" cuando el
reporte menciona >=2 clases, pero el reporte diferencial menciona 2 candidatos POR DISEÑO.
Para el nivel diferencial se reclasifica como `ok_diferencial` si el gt está entre las
clases mencionadas, y `dx_incorrecto` si no lo está.

Uso:
    python scripts/uncertainty_analysis.py                    # Mini-VLM (default)
    python scripts/uncertainty_analysis.py --model llava_med  # 2do generador
    python scripts/uncertainty_analysis.py --anchor les       # cascada re-anclada (split por lesión)
"""

import argparse
import csv
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.error_taxonomy import (
    CLASS_RE,
    THINK_RE,
    _is_repetition,
    classify_error,
)
from src.evaluation.clinical_ner import _normalize_label

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/raw/HAM10000")
REPORTS = Path("outputs/generated_reports/mini_vlm")
TIER_CSV = Path("outputs/uncertainty/uncertainty_3tier.csv")
OUT = Path("outputs/results/uncertainty_analysis.json")

DX_TO_FULL = {
    "mel": "melanoma", "nv": "nevus", "bcc": "basal cell carcinoma",
    "akiec": "actinic keratosis", "bkl": "benign keratosis",
    "df": "dermatofibroma", "vasc": "vascular lesion",
}
GRAVE = {"dx_incorrecto", "repeticion"}  # errores graves (mejoras.md item 4)


def build_label_map() -> dict:
    df = pd.read_csv(DATA_DIR / "HAM10000_metadata")
    return {r["image_id"]: DX_TO_FULL.get(r["dx"], r["dx"]) for _, r in df.iterrows()}


def load_reports(cond: str) -> dict:
    out = {}
    for jf in (REPORTS / cond).glob("*.json"):
        d = json.loads(jf.read_text(encoding="utf-8"))
        iid = Path(d.get("image_id", jf.stem)).stem.replace("_report", "")
        out[iid] = THINK_RE.sub("", d.get("report", "") or "").strip()
    return out


def mentioned(text: str) -> set:
    t = (text or "").lower()
    return {c for c, rx in CLASS_RE.items() if rx.search(t)}


def classify_differential(report: str, gt: str) -> str:
    """Taxonomía adaptada al nivel diferencial: mencionar 2 candidatos es correcto."""
    text = (report or "").lower().strip()
    if _is_repetition(text):
        return "repeticion"
    if len(text.split()) < 12:
        return "insuficiente"
    ment = mentioned(text)
    gt_c = _normalize_label(gt) if gt else ""
    if not ment:
        return "otros"
    if gt_c in ment:
        return "ok_diferencial" if len(ment) >= 2 else "ok"
    return "dx_incorrecto"


def main():
    global REPORTS, OUT
    parser = argparse.ArgumentParser(description="Taxonomía consciente del nivel + ruteo por clase")
    parser.add_argument("--model", default="mini_vlm", choices=["mini_vlm", "llava_med"])
    parser.add_argument("--anchor", default="v3", choices=["v3", "les"],
                        help="v3 (partición aleatoria) o les: brazos *_les + uncertainty_3tier_les.csv")
    args = parser.parse_args()
    REPORTS = Path("outputs/generated_reports") / args.model
    suffix = "_les" if args.anchor == "les" else ""
    stem = "uncertainty_analysis" if args.model == "mini_vlm" else f"uncertainty_analysis_{args.model}"
    OUT = OUT.with_name(f"{stem}{suffix}.json")
    tier_csv = TIER_CSV.with_name(f"uncertainty_3tier{suffix}.csv")
    logger.info("Generador: %s | anclaje: %s", args.model, args.anchor)

    labels = build_label_map()
    tiers = {r["image_id"]: r["tier"] for r in csv.DictReader(open(tier_csv))}
    swin = load_reports(f"full_swin{suffix}")
    diff = load_reports(f"full_differential{suffix}")
    logger.info("tiers=%d  full_swin=%d  full_differential=%d", len(tiers), len(swin), len(diff))

    res = {}

    # ---------- A) Taxonomía consciente del nivel ----------
    simple, advanced = Counter(), Counter()
    non_derived = [i for i, t in tiers.items() if t != "abstention"]
    for iid in non_derived:
        gt = labels.get(iid, "")
        rep_s = swin.get(iid)
        if rep_s is None:
            continue
        simple[classify_error(rep_s, gt)] += 1
        if tiers[iid] == "differential" and iid in diff:
            advanced[classify_differential(diff[iid], gt)] += 1
        else:
            advanced[classify_error(rep_s, gt)] += 1

    n = sum(simple.values())
    abst = [i for i, t in tiers.items() if t == "abstention"]
    simple_abst = Counter(classify_error(swin[i], labels.get(i, "")) for i in abst if i in swin)

    def rate(c, k):
        tot = sum(c.values())
        return (c.get(k, 0) / tot) if tot else 0.0

    res["taxonomia"] = {
        "n_no_derivadas": n,
        "grounding_simple": dict(simple),
        "pipeline_avanzado": dict(advanced),
        "dx_incorrecto_simple": rate(simple, "dx_incorrecto"),
        "dx_incorrecto_avanzado": rate(advanced, "dx_incorrecto"),
        "graves_simple": sum(simple.get(k, 0) for k in GRAVE) / n if n else 0,
        "graves_avanzado": sum(advanced.get(k, 0) for k in GRAVE) / n if n else 0,
        "abstenidas": {
            "n": len(abst),
            "taxonomia_bajo_grounding_simple": dict(simple_abst),
            "dx_incorrecto_evitados": simple_abst.get("dx_incorrecto", 0),
            "graves_evitados": sum(simple_abst.get(k, 0) for k in GRAVE),
        },
    }

    # ---------- B) Análisis por clase ----------
    per_class = defaultdict(Counter)
    for iid, t in tiers.items():
        per_class[labels.get(iid, "?")][t] += 1
    by_class = {}
    for cls, c in per_class.items():
        tot = sum(c.values())
        by_class[cls] = {
            "n": tot,
            "afirmativo": c.get("affirmative", 0),
            "diferencial": c.get("differential", 0),
            "abstencion": c.get("abstention", 0),
            "pct_afirmativo": c.get("affirmative", 0) / tot,
            "pct_diferencial": c.get("differential", 0) / tot,
            "pct_abstencion": c.get("abstention", 0) / tot,
        }
    res["por_clase"] = by_class

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------- Reporte ----------
    print("\n=== A) Taxonomía de errores (n=%d no derivadas) ===" % n)
    cats = sorted(set(simple) | set(advanced))
    print(f"{'categoria':18s} {'simple':>12s} {'avanzado':>12s}")
    for k in cats:
        print(f"{k:18s} {simple.get(k,0):5d} ({rate(simple,k):5.1%}) {advanced.get(k,0):5d} ({rate(advanced,k):5.1%})")
    print(f"\ndx_incorrecto: {rate(simple,'dx_incorrecto'):.1%} -> {rate(advanced,'dx_incorrecto'):.1%}")
    print(f"graves (dx_incorrecto+repeticion): {res['taxonomia']['graves_simple']:.1%} -> {res['taxonomia']['graves_avanzado']:.1%}")
    a = res["taxonomia"]["abstenidas"]
    print(f"\nAbstenidas (n={a['n']}): bajo grounding simple habrian sido {dict(simple_abst)}")
    print(f"  -> dx_incorrecto evitados por derivar: {a['dx_incorrecto_evitados']}")

    print("\n=== B) Ruteo por clase ===")
    print(f"{'clase':22s} {'n':>5s} {'afirm':>12s} {'difer':>12s} {'abst':>12s}")
    for cls, d in sorted(by_class.items(), key=lambda x: -x[1]["n"]):
        print(f"{cls:22s} {d['n']:5d} {d['afirmativo']:4d} ({d['pct_afirmativo']:5.1%}) "
              f"{d['diferencial']:4d} ({d['pct_diferencial']:5.1%}) {d['abstencion']:4d} ({d['pct_abstencion']:5.1%})")
    logger.info("Guardado en %s", OUT)


if __name__ == "__main__":
    main()
