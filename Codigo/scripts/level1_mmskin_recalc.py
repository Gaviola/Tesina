"""Recalcula el Nivel 1 de MM-Skin (v2) sin las referencias «nan» y por subconjunto.

Los reportes v2 de MM-Skin (``outputs/generated_reports/{model}/v2/mmskin``) se generaron sobre el archivo completo,
en orden, hasta el límite de tiempo, y 539 (Mini-VLM) / 175 (LLaVA-Med) tienen como referencia la cadena «nan»
(filas de ``caption.csv`` sin descripción) que entraban en las métricas. Ver
``docs/resul/verificaciones_cap03_resul_20261011.md``.

Calcula, para cada generador, BLEU-4, ROUGE-L, METEOR, CIDEr y BERTScore (``evaluate_generation``) sobre:
  - ``validas``: todos los reportes con referencia real;
  - ``test``: los de la partición de prueba de ``mmskin_splits.json``;
  - ``comunes``: las imágenes con referencia real que ambos generadores alcanzaron (comparación pareada).
Los bloques ``<think>`` se quitan del reporte antes de medir (métrica oficial: solo el reporte).

Local (BERTScore usa la GPU si hay). Se corre desde ``Codigo/``:
    python scripts/level1_mmskin_recalc.py
"""

import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.evaluation.generation import evaluate_generation

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPORTS = Path("outputs/generated_reports")
SPLITS = Path("data/splits/mmskin_splits.json")
OUTPUT = Path("outputs/results/level1_mmskin_recalc.json")
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
MODELS = ["mini_vlm", "llava_med"]


def has_ref(ref) -> bool:
    return isinstance(ref, str) and ref.strip() != "" and ref.strip().lower() != "nan"


def load(model: str) -> dict:
    out = {}
    for f in (REPORTS / model / "v2" / "mmskin").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        rep = THINK_RE.sub("", d.get("report") or "").strip()
        name = Path(d["image_id"]).name
        out[name] = {"report": rep, "reference": d.get("reference", "")}
    return out


def main():
    test_ids = set(json.loads(SPLITS.read_text(encoding="utf-8"))["test"])
    data = {m: load(m) for m in MODELS}
    valid = {m: {k for k, v in d.items() if v["report"] and has_ref(v["reference"])} for m, d in data.items()}
    common = set.intersection(*valid.values())
    result = {}
    for m in MODELS:
        logger.info("%s: %d reportes, %d con referencia real (%d «nan» o vacías)",
                    m, len(data[m]), len(valid[m]), len(data[m]) - len(valid[m]))
        result[m] = {"n_total": len(data[m])}
        for name, ids in (("validas", valid[m]), ("test", valid[m] & test_ids), ("comunes", common)):
            ids = sorted(ids)
            if not ids:
                continue
            preds = [data[m][i]["report"] for i in ids]
            refs = [data[m][i]["reference"] for i in ids]
            metrics = evaluate_generation(preds, refs)
            result[m][name] = {"n": len(ids), **{k: float(v) for k, v in metrics.items()
                                                  if isinstance(v, (int, float))}}
            logger.info("  %-8s n=%-5d %s", name, len(ids),
                        " ".join(f"{k}={v:.4f}" for k, v in result[m][name].items() if k != "n"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", OUTPUT)


if __name__ == "__main__":
    main()
