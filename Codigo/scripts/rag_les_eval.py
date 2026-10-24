"""Evalúa los brazos RAG con el índice de la partición por lesión (plan rag_les_plan_20261003).

Métrica oficial de la cascada: consistencia diagnóstica solo sobre el reporte (sin bloques <think>) y
*matcher* estricto, con *bootstrap* pareado (2000 remuestreos, semilla 42) sobre las mismas imágenes.

Comparaciones del plan:
  - full_rag_les vs full_baseline (no anclar), vs full_swin_les (grounding con Swin por lesión) y vs la
    línea base mecánica del kNN (imprimir el voto de los vecinos, sin generador).
  - full_swin_rag_les vs full_swin_les (¿la recuperación agrega sobre el clasificador?) y vs imprimir el
    diagnóstico de Swin sin generador.
Además, la consistencia exclusiva (nombra la clase verdadera y ninguna otra de las siete, para detectar
ganancias que vienen de nombrar varias clases) y, por clase verdadera, la consistencia de cada brazo.

100% local, CPU. Se corre desde ``Codigo/`` (donde están ``outputs/`` y ``data/``):
    python scripts/rag_les_eval.py
"""

import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.statistical_tests import paired_bootstrap_diff_flags
from src.evaluation.clinical_ner import CLASS_RE, diagnostic_consistency_flags

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/raw/HAM10000")
REPORTS_DIR = Path("outputs/generated_reports/mini_vlm")
RAG_CSV = Path("outputs/rag/rag_context_les.csv")
OUTPUT = Path("outputs/results/rag_les_eval.json")
THINK_RE = re.compile(r"<think>.*?(?:</think>|$)", re.DOTALL | re.IGNORECASE)

DX_TO_FULL = {
    "mel": "melanoma", "nv": "nevus", "bcc": "basal cell carcinoma",
    "akiec": "actinic keratosis", "bkl": "benign keratosis",
    "df": "dermatofibroma", "vasc": "vascular lesion",
}
ARMS = ["full_baseline", "full_swin_les", "full_rag_les", "full_swin_rag_les"]
PAIRS = [
    ("full_rag_les", "full_baseline"),
    ("full_rag_les", "full_swin_les"),
    ("full_rag_les", "knn_sin_generador"),
    ("full_swin_rag_les", "full_swin_les"),
    ("full_swin_rag_les", "swin_sin_generador"),
]
SWIN_CSV = Path("outputs/full_dx_swin_les.csv")


def label_map() -> dict:
    out = {}
    for path in (DATA_DIR / "HAM10000_metadata", DATA_DIR / "ISIC2018_Task3_Test_GroundTruth.csv"):
        if path.exists():
            for _, row in pd.read_csv(path).iterrows():
                out[row["image_id"]] = DX_TO_FULL.get(row["dx"], row["dx"])
    return out


def load(name: str) -> dict:
    out = {}
    for f in (REPORTS_DIR / name).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[Path(d["image_id"]).stem] = THINK_RE.sub("", d["report"] or "").strip()
    return out


def main():
    labels = label_map()
    conds = {name: load(name) for name in ARMS}
    for name, c in conds.items():
        logger.info("%-18s %d reportes", name, len(c))
    knn = pd.read_csv(RAG_CSV).set_index("image_id")["rag_knn_dx"].to_dict()
    conds["knn_sin_generador"] = {i: f"Diagnosis: {dx}." for i, dx in knn.items()}
    swin = pd.read_csv(SWIN_CSV).set_index("image_id")["diagnosis"].to_dict()
    conds["swin_sin_generador"] = {i: f"Diagnosis: {dx}." for i, dx in swin.items()}

    ids = sorted(set.intersection(*(set(c) for c in conds.values())) & set(labels))
    y = [labels[i] for i in ids]
    logger.info("n común = %d", len(ids))
    flags = {name: diagnostic_consistency_flags([c[i] for i in ids], y, strict=True) for name, c in conds.items()}

    def n_classes(text: str) -> int:
        t = (text or "").lower()
        return sum(bool(rx.search(t)) for rx in CLASS_RE.values())

    # Consistencia exclusiva: nombra la clase verdadera y ninguna otra de las siete.
    exclusive = {name: [int(f and n_classes(c[i]) == 1) for f, i in zip(flags[name], ids)]
                 for name, c in conds.items()}

    result = {"n": len(ids), "metric": "consistencia diagnóstica, solo reporte, matcher estricto",
              "consistencia": {}, "consistencia_exclusiva": {}, "comparaciones": {}, "por_clase": {}}
    print(f"\n=== RAG por lesión — Mini-VLM, n={len(ids)} ===")
    for name, f in flags.items():
        result["consistencia"][name] = sum(f) / len(f)
        result["consistencia_exclusiva"][name] = sum(exclusive[name]) / len(f)
        print(f"  {name:<20} {sum(f) / len(f):.3f}  exclusiva {sum(exclusive[name]) / len(f):.3f}")
    print("\n  Bootstrap pareado (2000, semilla 42): consistencia | exclusiva")
    for a, b in PAIRS:
        d, lo, hi, p = paired_bootstrap_diff_flags(flags[a], flags[b], n_boot=2000, seed=42)
        de, loe, hie, pe = paired_bootstrap_diff_flags(exclusive[a], exclusive[b], n_boot=2000, seed=42)
        result["comparaciones"][f"{a} vs {b}"] = {"diff": d, "ci95": [lo, hi], "p": p,
                                                  "diff_exclusiva": de, "ci95_exclusiva": [loe, hie], "p_exclusiva": pe}
        print(f"  {a:<18} vs {b:<18} Δ={d:+.3f} [{lo:+.3f}, {hi:+.3f}] | Δexcl={de:+.3f} [{loe:+.3f}, {hie:+.3f}]")

    print("\n  Por clase verdadera")
    df = pd.DataFrame({"y": y, **{k: v for k, v in flags.items()}})
    for cls, g in df.groupby("y"):
        row = {k: float(g[k].mean()) for k in flags}
        row["n"] = int(len(g))
        result["por_clase"][cls] = row
        print(f"  {cls:<22} n={len(g):<5} " + " ".join(f"{k[:12]}={row[k]:.3f}" for k in flags))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", OUTPUT)


if __name__ == "__main__":
    main()
