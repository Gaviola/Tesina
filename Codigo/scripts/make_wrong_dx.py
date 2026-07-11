"""P1.3 (plan julio-agosto) — Genera CSVs de diagnóstico ERRÓNEO para la ablación de
robustez del generador ("¿el generador se compromete con un dx incorrecto del clasificador?").

Toma un CSV de grounding (columnas image_id,diagnosis) y produce otro con el dx sustituido:
  - modo `swap`   : a la clase clínicamente confundible (determinístico).
  - modo `random` : a una clase distinta al azar (seeded, reproducible).

100% local, sin cluster. El CSV resultante se pasa a generate_report.py con --diagnosis_source.

Uso:
    python scripts/make_wrong_dx.py --input outputs/full_dx_oracle.csv \
        --output outputs/full_dx_wrong_swap.csv --mode swap
"""

import argparse
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Pares clínicamente confundibles (nombre completo, en minúscula). Determinístico.
CONFUSABLE = {
    "melanoma": "melanocytic nevus",
    "melanocytic nevus": "melanoma",
    "benign keratosis": "melanoma",
    "basal cell carcinoma": "melanocytic nevus",
    "actinic keratosis": "benign keratosis",
    "dermatofibroma": "melanocytic nevus",
    "vascular lesion": "melanoma",
}


def _wrong_swap(dx: str, all_dx: list[str]) -> str:
    key = dx.strip().lower()
    if key in CONFUSABLE:
        return CONFUSABLE[key]
    # Fallback: primera clase distinta encontrada.
    for cand in all_dx:
        if cand.strip().lower() != key:
            return cand
    return dx


def main():
    parser = argparse.ArgumentParser(description="P1.3 Generar CSV de dx erróneo")
    parser.add_argument("--input", type=str, required=True, help="CSV grounding image_id,diagnosis")
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--mode", choices=["swap", "random"], default="swap")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    in_path = Path(args.input)
    rows = list(csv.DictReader(in_path.open(encoding="utf-8")))
    if not rows or "diagnosis" not in rows[0]:
        raise SystemExit(f"El CSV {in_path} debe tener columnas image_id,diagnosis")

    vocab = sorted({r["diagnosis"] for r in rows})
    out_rows, changed = [], 0
    for r in rows:
        dx = r["diagnosis"]
        if args.mode == "swap":
            new_dx = _wrong_swap(dx, vocab)
        else:  # random
            others = [d for d in vocab if d.strip().lower() != dx.strip().lower()]
            new_dx = rng.choice(others) if others else dx
        changed += int(new_dx.strip().lower() != dx.strip().lower())
        out_rows.append({"image_id": r["image_id"], "diagnosis": new_dx})

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["image_id", "diagnosis"])
        w.writeheader()
        w.writerows(out_rows)

    print(f"[make_wrong_dx] modo={args.mode}  {changed}/{len(rows)} dx modificados -> {out_path}")


if __name__ == "__main__":
    main()
