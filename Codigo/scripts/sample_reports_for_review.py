"""E (plan cierre agosto) — Muestra estratificada de reportes para revisión clínica.

Selecciona ~30 reportes generados, estratificados por clase diagnóstica (7 de HAM) y condición del
ensamble (baseline / grounding-Swin / oracle), para que un/a especialista los evalúe con la rúbrica
(`docs/rubrica_validacion_clinica.md`). Exporta un CSV listo para calificar (columnas C1–C5, G vacías).

Local. Uso:
    python scripts/sample_reports_for_review.py --model mini_vlm --per_class 4
"""

import argparse
import csv
import glob
import json
import logging
import os
from collections import defaultdict
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="E Muestra para revisión clínica")
    parser.add_argument("--model", default="mini_vlm")
    parser.add_argument("--conditions", nargs="+", default=["full_baseline", "full_swin", "full_oracle"])
    parser.add_argument("--per_class", type=int, default=4, help="Reportes objetivo por clase (aprox).")
    parser.add_argument("--gt_csv", default="outputs/full_dx_oracle.csv")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="outputs/review/muestra_revision_clinica.csv")
    args = parser.parse_args()

    gt = {r.image_id: r.diagnosis for r in pd.read_csv(args.gt_csv).itertuples()}
    # Indexar reportes por (clase, condición)
    by_class = defaultdict(list)
    for cond in args.conditions:
        for f in glob.glob(f"outputs/generated_reports/{args.model}/{cond}/*.json"):
            d = json.load(open(f, encoding="utf-8"))
            iid = os.path.splitext(d.get("image_id", ""))[0]
            g = gt.get(iid) or d.get("gt_label")
            rep = (d.get("report") or "").strip()
            if g and rep:
                by_class[g].append({"image_id": iid, "gt": g, "condition": cond, "report": rep})

    import random
    random.seed(args.seed)
    rows = []
    for g, items in sorted(by_class.items()):
        random.shuffle(items)
        # repartir per_class entre condiciones disponibles
        picked, seen_cond = [], defaultdict(int)
        for it in items:
            if len(picked) >= args.per_class:
                break
            if seen_cond[it["condition"]] < max(1, args.per_class // len(args.conditions) + 1):
                picked.append(it); seen_cond[it["condition"]] += 1
        rows.extend(picked)

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "image_id", "gt", "condition", "report",
                    "C1_correccion", "C2_seguridad", "C3_completitud",
                    "C4_ahorro_tiempo", "C5_utilidad", "G_veredicto", "comentarios"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["image_id"], r["gt"], r["condition"], r["report"],
                        "", "", "", "", "", "", ""])
    logger.info("Muestra: %s (%d reportes, %d clases)", out, len(rows), len(by_class))
    from collections import Counter
    logger.info("Por clase: %s", dict(Counter(r["gt"] for r in rows)))
    logger.info("Por condición: %s", dict(Counter(r["condition"] for r in rows)))


if __name__ == "__main__":
    main()
