"""Calibración post-hoc de clasificadores, ajustada en VALIDACIÓN y evaluada en test (feedback 2026-09-12).

El documento mostró ECE alto y probabilidades sub-confiadas. Este script prueba dos correcciones estándar
(Guo et al., 2017) sobre las probabilidades ya guardadas (`*_val_predictions.json` / `*_predictions.json`):

  - Temperature scaling (TS): un único escalar T, logits/T. No cambia el argmax (exactitud intacta).
  - Vector scaling (VS): temperatura y sesgo POR CLASE, logits*w + b. Puede cambiar el argmax. Se incluye
    porque los pesos por clase de la pérdida desplazan los priors de cada clase de forma distinta, algo que
    un único T no puede corregir.

Como logits se usa log(p): el softmax es invariante a un corrimiento por fila, así que log(p) recupera los
logits salvo una constante (válido también para probabilidades promediadas con TTA, como aproximación).

Uso:
    python scripts/posthoc_calibration.py --pairs NAME=VAL_JSON,TEST_JSON [NAME=VAL_JSON,TEST_JSON ...]
    python scripts/posthoc_calibration.py --glob-lesion      # todos los *_les*_val_predictions.json
"""

import argparse
import glob
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from sklearn.metrics import accuracy_score, recall_score

from src.evaluation.classification import brier_score_multiclass, expected_calibration_error

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OUT = Path("outputs/results/calibration/posthoc_calibration.json")


def _logits(p):
    return torch.tensor(np.log(np.clip(np.asarray(p, float), 1e-12, 1.0)), dtype=torch.float64)


def fit(val_prob, y_val, method: str):
    z, y = _logits(val_prob), torch.tensor(np.asarray(y_val), dtype=torch.long)
    k = z.shape[1]
    if method == "ts":
        params = [torch.zeros(1, dtype=torch.float64, requires_grad=True)]
        transform = lambda x, p: x / torch.exp(p[0])
    else:  # vector scaling
        params = [torch.zeros(k, dtype=torch.float64, requires_grad=True),
                  torch.zeros(k, dtype=torch.float64, requires_grad=True)]
        transform = lambda x, p: x * torch.exp(p[0]) + p[1]
    opt = torch.optim.LBFGS(params, lr=0.1, max_iter=500)
    ce = torch.nn.CrossEntropyLoss()

    def closure():
        opt.zero_grad()
        loss = ce(transform(z, params), y)
        if method == "vs":  # regularización suave para no sobreajustar la val chica
            loss = loss + 1e-3 * sum((q ** 2).sum() for q in params)
        loss.backward()
        return loss

    opt.step(closure)
    frozen = [q.detach() for q in params]
    return lambda prob: torch.softmax(transform(_logits(prob), frozen), dim=1).numpy(), frozen


def metrics(y, prob) -> dict:
    y = np.asarray(y); prob = np.asarray(prob)
    pred = prob.argmax(1)
    ece, mce = expected_calibration_error(y, prob)
    nll = float(-np.mean(np.log(np.clip(prob[np.arange(len(y)), y], 1e-12, 1))))
    return {"ece": ece, "mce": mce, "brier": brier_score_multiclass(y, prob), "nll": nll,
            "acc": accuracy_score(y, pred),
            "sens_macro": recall_score(y, pred, labels=list(range(prob.shape[1])), average="macro", zero_division=0),
            "conf_media": float(prob.max(1).mean())}


def main():
    parser = argparse.ArgumentParser(description="Calibración post-hoc (TS / vector scaling) ajustada en val")
    parser.add_argument("--pairs", nargs="*", default=[], help="NAME=VAL_JSON,TEST_JSON")
    parser.add_argument("--glob-lesion", action="store_true")
    parser.add_argument("--output", default=str(OUT))
    args = parser.parse_args()

    pairs = {}
    for item in args.pairs:
        name, files = item.split("=", 1)
        pairs[name] = tuple(files.split(","))
    if args.glob_lesion:
        for vf in sorted(glob.glob("outputs/results/*_les*_val_predictions.json")):
            pairs[Path(vf).name.replace("_val_predictions.json", "")] = (vf, vf.replace("_val_predictions", "_predictions"))

    res = {}
    for name, (vf, tf) in pairs.items():
        v, t = json.loads(Path(vf).read_text()), json.loads(Path(tf).read_text())
        r = {"sin_calibrar": metrics(t["y_true"], t["y_prob"])}
        for method in ["ts", "vs"]:
            apply, params = fit(v["y_prob"], v["y_true"], method)
            r[method] = metrics(t["y_true"], apply(t["y_prob"]))
            if method == "ts":
                r[method]["T"] = float(torch.exp(params[0]).item())
        res[name] = r
        logger.info("%s listo", name)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{'modelo':40s} {'método':12s} {'ECE':>6s} {'MCE':>6s} {'Brier':>6s} {'NLL':>6s} {'acc':>6s} {'sensM':>6s} {'conf':>6s}")
    for name, r in res.items():
        for method, label in [("sin_calibrar", "sin calibrar"), ("ts", f"TS (T={r['ts']['T']:.2f})"), ("vs", "vector sc.")]:
            m = r[method]
            print(f"{name[:40]:40s} {label:12s} {m['ece']:.3f} {m['mce']:.3f} {m['brier']:.3f} {m['nll']:.3f} "
                  f"{m['acc']:.3f} {m['sens_macro']:.3f} {m['conf_media']:.3f}")
    logger.info("Guardado en %s", args.output)


if __name__ == "__main__":
    main()
