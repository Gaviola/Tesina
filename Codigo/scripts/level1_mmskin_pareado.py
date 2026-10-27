"""Nivel 1 pareado en la prueba de MM-Skin: Mini-VLM v2 frente a LLaVA-Med v2 sobre los mismos pares.

Los reportes de Mini-VLM vienen de la corrida sobre el archivo completo (``mini_vlm/v2/mmskin``, cortada por tiempo) y
los de LLaVA-Med de la corrida dedicada a la prueba (``llava_med/v2/mmskin_test``). Se evalúan las cinco métricas de
``evaluate_generation`` solo sobre las imágenes de la prueba de ``mmskin_splits.json`` en que ambos tienen reporte no
vacío después de quitar ``<think>`` y referencia real (sin «nan»). Para BERTScore se agrega el IC del 95 % de la
diferencia Mini − LLaVA por bootstrap pareado (2 000 remuestreos, semilla 42) sobre los F1 por par. 100 % local.
Plan: docs/ideas/level1_mmskin_pareado_plan_20261025.md.

Uso:
    python scripts/level1_mmskin_pareado.py
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ensemble_bootstrap import THINK_RE
from src.evaluation.generation import evaluate_generation

ROOT = Path("outputs/generated_reports")
CONDS = {"mini_v2": ROOT / "mini_vlm/v2/mmskin", "llava_v2": ROOT / "llava_med/v2/mmskin_test"}
SPLITS = Path("data/splits/mmskin_splits.json")
OUT = Path("outputs/results/level1_test/mmskin_test/level1_pareado_mini_v2_llava_v2.json")


def has_ref(ref: str) -> bool:
    return bool(ref) and ref.lower() != "nan"


def load(path: Path) -> dict:
    """nombre de imagen -> (reporte sin <think>, referencia)."""
    out = {}
    for f in path.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[Path(d["image_id"]).name] = (THINK_RE.sub("", d.get("report") or "").strip(),
                                         str(d.get("reference") or "").strip())
    return out


def bertscore_por_par(preds: list[str], refs: list[str]) -> np.ndarray:
    import evaluate
    res = evaluate.load("bertscore").compute(predictions=preds, references=refs,
                                             model_type="distilbert-base-uncased", lang="en", batch_size=32)
    return np.asarray(res["f1"])


def main():
    if OUT.exists():
        sys.exit(f"{OUT} ya existe; no se sobrescribe")
    test = {Path(x).name for x in json.loads(SPLITS.read_text(encoding="utf-8"))["test"]}
    data = {k: load(p) for k, p in CONDS.items()}
    ids = sorted(i for i in test & set.intersection(*(set(d) for d in data.values()))
                 if all(data[k][i][0] for k in data) and has_ref(data["llava_v2"][i][1]))
    refs = [data["llava_v2"][i][1] for i in ids]
    res = {"n": len(ids)}
    f1 = {}
    for k, d in data.items():
        preds = [d[i][0] for i in ids]
        res[k] = evaluate_generation(preds, refs)
        f1[k] = bertscore_por_par(preds, refs)
    diff = f1["mini_v2"] - f1["llava_v2"]
    rng = np.random.default_rng(42)
    boot = [diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(2000)]
    res["bertscore_dif_mini_menos_llava"] = {"media": float(diff.mean()),
                                             "ic95": [float(np.percentile(boot, 2.5)),
                                                      float(np.percentile(boot, 97.5))]}
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
