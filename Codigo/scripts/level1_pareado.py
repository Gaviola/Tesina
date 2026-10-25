"""Nivel 1 pareado en la prueba de SkinCoT: Mini-VLM v2 (principal), Mini-VLM v3 (control) y LLaVA-Med v2.

Evalúa las cinco métricas de ``evaluate_generation`` solo sobre las imágenes en que los tres generadores escriben un
reporte no vacío después de quitar los bloques ``<think>`` y que tienen referencia, para comparar sobre los mismos
pares (``evaluate_reports.py --level 1`` usa los pares de cada generador por separado). 100 % local, CPU.

Uso:
    python scripts/level1_pareado.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.ensemble_bootstrap import THINK_RE
from src.evaluation.generation import evaluate_generation

ROOT = Path("outputs/generated_reports")
CONDS = {"mini_v2": ROOT / "mini_vlm/v2/skincot_test", "mini_v3": ROOT / "mini_vlm/v3/skincot_test",
         "llava_v2": ROOT / "llava_med/v2/skincot_test"}
OUT = Path("outputs/results/level1_test/skincot_test_mini_v2/level1_pareado_mini_v2_v3_llava_v2.json")


def load(path: Path) -> dict:
    """image_id -> (reporte sin <think>, referencia)."""
    out = {}
    for f in path.glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[d["image_id"]] = (THINK_RE.sub("", d.get("report") or "").strip(), str(d.get("reference") or "").strip())
    return out


def main():
    if OUT.exists():
        sys.exit(f"{OUT} ya existe; no se sobrescribe")
    data = {k: load(p) for k, p in CONDS.items()}
    ids = sorted(i for i in set.intersection(*(set(d) for d in data.values()))
                 if all(data[k][i][0] for k in data)
                 and data["mini_v2"][i][1] and data["mini_v2"][i][1].lower() != "nan")
    res = {"n": len(ids)}
    for k, d in data.items():
        res[k] = evaluate_generation([d[i][0] for i in ids], [data["mini_v2"][i][1] for i in ids])
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
