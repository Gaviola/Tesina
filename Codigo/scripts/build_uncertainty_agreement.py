"""P5.4 — CSV de incertidumbre por ACUERDO entre clasificadores (Swin vs kNN-DermLIP).

La confianza softmax calibrada resultó un mal ruteador (no monótona; el Swin es sub-confiado sobre
todo en la clase mayoritaria fácil). Señal mucho mejor: el ACUERDO entre dos clasificadores
especializados baratos —Swin (supervisado) y el kNN sobre embeddings DermLIP (recuperación, P5.3)—.
Cuando coinciden, aciertan el 94%; cuando no, el gt está en {Swin,kNN} el 88%.

Regla: coinciden -> confiado (reporte definitivo con ese dx); difieren -> inseguro (reporte
diferencial con los dos candidatos). Salida: outputs/uncertainty/uncertainty.csv (mismas columnas que
consume generate_report.py --uncertainty).

Local. Uso: python scripts/build_uncertainty_agreement.py
"""

import argparse
import csv
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="P5.4 CSV incertidumbre por acuerdo Swin/kNN")
    parser.add_argument("--swin_csv", default="outputs/full_dx_swin.csv")
    parser.add_argument("--rag_csv", default="outputs/rag/rag_context.csv")
    parser.add_argument("--gt_csv", default="outputs/full_dx_oracle.csv")
    parser.add_argument("--output", default="outputs/uncertainty/uncertainty.csv")
    args = parser.parse_args()

    swin = {r.image_id: r.diagnosis for r in pd.read_csv(args.swin_csv).itertuples()}
    knn = {r.image_id: r.rag_knn_dx for r in pd.read_csv(args.rag_csv).itertuples()}
    gt = {r.image_id: r.diagnosis for r in pd.read_csv(args.gt_csv).itertuples()}

    ids = [i for i in swin if i in knn]
    n_conf = n_correct_conf = n_unc = n_unc_gt_in = 0
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "unc_dx", "unc_candidates", "unc_conf", "unc_confident"])
        for iid in ids:
            s, k = swin[iid], knn[iid]
            confident = int(s == k)
            if confident:
                cands = s
                n_conf += 1
                if gt.get(iid) == s:
                    n_correct_conf += 1
            else:
                cands = f"{s}; {k}"
                n_unc += 1
                if gt.get(iid) in (s, k):
                    n_unc_gt_in += 1
            w.writerow([iid, s, cands, "1.0" if confident else "0.5", confident])

    logger.info("CSV: %s (n=%d)", out, len(ids))
    logger.info("Confiados (acuerdo): %d (%.0f%%), exactitud %.3f", n_conf,
                100 * n_conf / len(ids), n_correct_conf / max(n_conf, 1))
    logger.info("Inseguros (desacuerdo): %d (%.0f%%), gt en {Swin,kNN} %.3f", n_unc,
                100 * n_unc / len(ids), n_unc_gt_in / max(n_unc, 1))


if __name__ == "__main__":
    main()
