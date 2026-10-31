"""D2 (plan cierre agosto) — Router de 3 niveles del ensamble consciente de la incertidumbre.

Implementa el marco del tutor (afirmativo / diferencial / abstención-derivación) pero alimentado por la
señal que SÍ separa (acuerdo entre clasificadores + consenso de la recuperación), no por la softmax cruda.

Señales:
  - Swin dx (clasificador supervisado, outputs/full_dx_swin.csv).
  - kNN-DermLIP: voto y los 3 vecinos recuperados (outputs/rag/rag_context.csv).

Ruteo:
  - AFIRMATIVO : Swin == voto kNN  (coinciden → alta confianza; acc ~0.94 en test).
  - ABSTENCIÓN : Swin != voto kNN Y los 3 vecinos son TODOS distintos (sin consenso → máxima
                 ambigüedad → derivar a un especialista).
  - DIFERENCIAL: Swin != voto kNN pero hay consenso parcial → reporte diferencial con {Swin, kNN}.

Salida: outputs/uncertainty/uncertainty_3tier.csv (image_id, tier, unc_dx, unc_candidates) + métricas de
cobertura por nivel (¿el gt está en lo que el sistema presenta?). Local.
"""

import argparse
import csv
import logging
import re
from collections import Counter
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

_NEIGH_RE = re.compile(r"diagnosed as:\s*(.+)\.$")


def _parse_neighbors(context: str):
    """Extrae los diagnósticos de los k vecinos del string de contexto RAG."""
    m = _NEIGH_RE.search(context.strip())
    if not m:
        return []
    parts = [p.strip() for p in m.group(1).split(";")]
    return [re.sub(r"\s*\(.*\)$", "", p).strip() for p in parts]  # quita "(localización)"


def main():
    parser = argparse.ArgumentParser(description="D2 Router de incertidumbre de 3 niveles")
    parser.add_argument("--swin_csv", default="outputs/full_dx_swin.csv")
    parser.add_argument("--rag_csv", default="outputs/rag/rag_context.csv")
    parser.add_argument("--gt_csv", default="outputs/full_dx_oracle.csv")
    parser.add_argument("--output", default="outputs/uncertainty/uncertainty_3tier.csv")
    args = parser.parse_args()

    swin = {r.image_id: r.diagnosis for r in pd.read_csv(args.swin_csv).itertuples()}
    gt = {r.image_id: r.diagnosis for r in pd.read_csv(args.gt_csv).itertuples()}
    rag = pd.read_csv(args.rag_csv)
    knn = {r.image_id: r.rag_knn_dx for r in rag.itertuples()}
    neigh = {r.image_id: _parse_neighbors(r.rag_context) for r in rag.itertuples()}

    ids = [i for i in swin if i in knn]
    counts = Counter(); cover = Counter(); total = Counter()
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "tier", "unc_dx", "unc_candidates"])
        for iid in ids:
            s, k = swin[iid], knn[iid]
            ns = neigh.get(iid, [])
            n_distinct = len(set(ns)) if ns else 3
            g = gt.get(iid)
            if s == k:
                tier, dx, cands = "affirmative", s, s
                covered = (g == s)
            elif n_distinct >= 3:
                tier, dx, cands = "abstention", "", f"{s}; {k}"
                covered = (g in (s, k))  # informativo: ¿estaba entre los candidatos que se descartan?
            else:
                tier, dx, cands = "differential", s, f"{s}; {k}"
                covered = (g in (s, k))
            w.writerow([iid, tier, dx, cands])
            counts[tier] += 1; total[tier] += 1
            if covered:
                cover[tier] += 1

    # CSV solo-diferenciales, compatible con generate_report.py --uncertainty (unc_confident=0 → plantilla
    # diferencial). Sirve como --only_ids_csv para restringir la generación a esas imágenes. El nombre sale del de
    # --output (uncertainty_3tier_les.csv -> uncertainty_differential_les.csv), para no pisar el de otra partición.
    diff_out = out.with_name(out.name.replace("3tier", "differential"))
    if diff_out == out:
        diff_out = out.with_name(f"{out.stem}_differential.csv")
    with out.open("r", encoding="utf-8") as fin, diff_out.open("w", newline="", encoding="utf-8") as fo:
        r = csv.DictReader(fin); w2 = csv.writer(fo)
        w2.writerow(["image_id", "unc_dx", "unc_candidates", "unc_conf", "unc_confident"])
        for row in r:
            if row["tier"] == "differential":
                w2.writerow([row["image_id"], row["unc_dx"], row["unc_candidates"], "0.5", "0"])
    logger.info("CSV diferenciales: %s", diff_out)

    n = len(ids)
    logger.info("CSV: %s (n=%d)", out, n)
    for tier in ["affirmative", "differential", "abstention"]:
        c = counts[tier]
        cov = cover[tier] / max(c, 1)
        metric = "acc(gt=Swin)" if tier == "affirmative" else "gt in {Swin,kNN}"
        logger.info("  %-12s: %4d (%.0f%%)  %s = %.3f", tier, c, 100 * c / n, metric, cov)
    # Cobertura efectiva del sistema (afirmativo acierta + diferencial contiene el gt):
    eff = cover["affirmative"] + cover["differential"]
    denom = counts["affirmative"] + counts["differential"]
    logger.info("Cobertura del gt en lo PRESENTADO (afirm.+difer., sin abstenidos): %.3f (%d/%d)",
                eff / max(denom, 1), eff, denom)


if __name__ == "__main__":
    main()
