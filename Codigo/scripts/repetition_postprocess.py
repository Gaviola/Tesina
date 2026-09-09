"""Mitigacion post-hoc de la degeneracion por repeticion en reportes generados.

El ruteo de 3 niveles amplifica el artefacto de repeticion: los reportes del nivel
DIFERENCIAL degeneran mucho mas que los afirmativos (enumerar dos candidatos favorece
el bucle de texto). Este script mide cuanto de ese artefacto es recuperable SIN
regenerar, aplicando dos operaciones conservadoras sobre el texto ya producido:

  1. Deduplicacion de oraciones: se elimina toda oracion cuya forma normalizada ya
     aparecio antes en el reporte (conserva la primera aparicion).
  2. Corte del bucle final: si tras la deduplicacion el texto sigue siendo periodico,
     se trunca en el punto donde comienza la repeticion de n-gramas.

Ninguna operacion agrega texto ni cambia el diagnostico enunciado: solo elimina
material redundante posterior. Se verifica explicitamente que la mencion del gt se
preserve.

Uso:
    python scripts/repetition_postprocess.py
"""

import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.error_taxonomy import CLASS_RE, THINK_RE, _is_repetition
from scripts.uncertainty_analysis import DX_TO_FULL, classify_differential

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/raw/HAM10000")
REPORTS = Path("outputs/generated_reports/mini_vlm/full_differential")
OUT = Path("outputs/results/repetition_postprocess.json")

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def dedup_sentences(text: str) -> str:
    seen, keep = set(), []
    for sent in SENT_SPLIT.split(text):
        k = _norm(sent)
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        keep.append(sent.strip())
    return " ".join(keep)


def trim_loop(text: str, n: int = 5) -> str:
    """Trunca donde empieza un bucle de n-gramas (la 2a aparicion consecutiva)."""
    toks = text.split()
    if len(toks) < 2 * n:
        return text
    seen = {}
    for i in range(len(toks) - n + 1):
        g = tuple(toks[i:i + n])
        if g in seen and i - seen[g] <= n * 3:   # reaparece cerca => bucle
            return " ".join(toks[:i]).rstrip(" ,;") + "."
        seen.setdefault(g, i)
    return text


def clean(text: str) -> str:
    return trim_loop(dedup_sentences(text))


def main():
    df = pd.read_csv(DATA_DIR / "HAM10000_metadata")
    labels = {r["image_id"]: DX_TO_FULL.get(r["dx"], r["dx"]) for _, r in df.iterrows()}

    before, after = Counter(), Counter()
    n = rep_before = rep_after = 0
    gt_lost = 0
    len_before = len_after = 0

    for jf in sorted(REPORTS.glob("*.json")):
        d = json.loads(jf.read_text(encoding="utf-8"))
        iid = Path(d.get("image_id", jf.stem)).stem.replace("_report", "")
        gt = labels.get(iid, "")
        raw = THINK_RE.sub("", d.get("report", "") or "").strip()
        fixed = clean(raw)

        n += 1
        len_before += len(raw.split())
        len_after += len(fixed.split())
        rb, ra = _is_repetition(raw.lower()), _is_repetition(fixed.lower())
        rep_before += rb
        rep_after += ra
        before[classify_differential(raw, gt)] += 1
        after[classify_differential(fixed, gt)] += 1

        # control: la mencion del gt no debe perderse por el recorte
        gt_in_raw = any(rx.search(raw.lower()) for c, rx in CLASS_RE.items() if c == gt)
        gt_in_fix = any(rx.search(fixed.lower()) for c, rx in CLASS_RE.items() if c == gt)
        if gt_in_raw and not gt_in_fix:
            gt_lost += 1

    res = {
        "n": n,
        "repeticion_antes": rep_before, "repeticion_despues": rep_after,
        "pct_antes": rep_before / n, "pct_despues": rep_after / n,
        "taxonomia_antes": dict(before), "taxonomia_despues": dict(after),
        "long_media_antes": len_before / n, "long_media_despues": len_after / n,
        "gt_perdidos_por_recorte": gt_lost,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== Repeticion en el nivel diferencial (n={n}) ===")
    print(f"  con repeticion: {rep_before} ({rep_before/n:.1%})  ->  {rep_after} ({rep_after/n:.1%})")
    print(f"  longitud media: {len_before/n:.0f}  ->  {len_after/n:.0f} palabras")
    print(f"  menciones del gt perdidas por el recorte: {gt_lost}")
    print("\n=== Taxonomia del nivel diferencial ===")
    for k in sorted(set(before) | set(after)):
        print(f"  {k:18s} {before.get(k,0):4d} -> {after.get(k,0):4d}")
    logger.info("Guardado en %s", OUT)


if __name__ == "__main__":
    main()
