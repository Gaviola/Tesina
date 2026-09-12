"""Consolida los resultados del split disjunto por lesión (plan split_lesion_semillas_plan_20260912).

Opera sobre lo que haya en outputs/results/ (se puede correr con resultados parciales) y produce, en un
único JSON + salida por consola, todos los números que alimentan el documento:

  1. Selección SOLO en validación: para cada modelo y cada variante de pérdida, ranking de los trials por
     F1 ponderado en val (mismo criterio que el checkpoint). El test se muestra al lado, sin intervenir.
  2. Ganador por modelo (entre las dos pérdidas, también por val) y sus semillas: media ± desvío en test.
  3. Legacy (DenseNet/ViT) y réplica del cuadro de desbalance.
  4. Detección de melanoma (umbral esp>=0.85 fijado en val) del ganador de cada modelo y de su ensamble.
  5. Calibración (sin calibrar / TS / vector scaling, ajustados en val).
  6. Ruteo de 3 niveles con el Swin nuevo + kNN-DermLIP del split por lesión.

Uso:
    python scripts/lesion_split_report.py
"""

import glob
import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, recall_score, roc_auc_score

from scripts.melanoma_detection import _task_report
from scripts.posthoc_calibration import fit as calib_fit
from scripts.posthoc_calibration import metrics as calib_metrics

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RES = Path("outputs/results")
OUT = RES / "lesion_split_report.json"
CLASSES = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
FULL = {"MEL": "melanoma", "NV": "nevus", "BCC": "basal cell carcinoma", "AKIEC": "actinic keratosis",
        "BKL": "benign keratosis", "DF": "dermatofibroma", "VASC": "vascular lesion"}
LABELS = list(range(len(CLASSES)))
RUN_RE = re.compile(r"^(?P<model>swin_tiny|convnext_tiny)_sweep_(?P<trial>t\d\d)_les(?P<cw>_cwnone)?(?:_s(?P<seed>\d+))?$")


def load(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return np.asarray(d["y_true"]), np.asarray(d["y_pred"]), np.asarray(d["y_prob"], float), d.get("image_ids")


def cls_metrics(y, p, prob=None) -> dict:
    out = {"acc": accuracy_score(y, p),
           "f1_weighted": f1_score(y, p, labels=LABELS, average="weighted", zero_division=0),
           "f1_macro": f1_score(y, p, labels=LABELS, average="macro", zero_division=0),
           "sens_macro": recall_score(y, p, labels=LABELS, average="macro", zero_division=0),
           "recall_mel": recall_score(y, p, labels=[0], average="macro", zero_division=0)}
    if prob is not None:
        out["auc_macro_ovr"] = float(np.mean([roc_auc_score((y == c).astype(int), prob[:, c]) for c in LABELS]))
    return out


def mean_std(rows: list) -> dict:
    keys = rows[0].keys()
    return {k: {"mean": float(np.mean([r[k] for r in rows])), "std": float(np.std([r[k] for r in rows], ddof=1))
                if len(rows) > 1 else 0.0} for k in keys}


def main():
    report = {}

    # ---------- 1-2. Barrido y selección en validación ----------
    runs = {}
    for vf in glob.glob(str(RES / "*_sweep_t??_les*_val_predictions.json")):
        name = Path(vf).name.replace("_val_predictions.json", "")
        m = RUN_RE.match(name)
        tf = RES / f"{name}_predictions.json"
        if not m or not tf.exists():
            continue
        yv, pv, prv, _ = load(vf)
        yt, pt, prt, _ = load(tf)
        runs[name] = {**m.groupdict(), "cw": "none" if m["cw"] else "auto", "seed": int(m["seed"] or 42),
                      "val": cls_metrics(yv, pv), "test": cls_metrics(yt, pt, prt), "val_file": vf, "test_file": str(tf)}
    report["sweep"] = {k: {kk: vv for kk, vv in v.items() if kk not in ("val_file", "test_file")} for k, v in runs.items()}

    winners = {}
    for model in ["swin_tiny", "convnext_tiny"]:
        cands = {k: v for k, v in runs.items() if v["model"] == model and v["seed"] == 42}
        if not cands:
            continue
        print(f"\n=== {model}: ranking por F1 ponderado en VAL (seed 42) ===")
        print(f"{'run':38s} {'val_f1w':>7s} {'val_sM':>6s} | {'test_acc':>8s} {'f1w':>6s} {'f1m':>6s} {'sensM':>6s}")
        for k, v in sorted(cands.items(), key=lambda kv: -kv[1]["val"]["f1_weighted"]):
            print(f"{k:38s} {v['val']['f1_weighted']:.4f} {v['val']['sens_macro']:.3f} | "
                  f"{v['test']['acc']:.4f} {v['test']['f1_weighted']:.3f} {v['test']['f1_macro']:.3f} {v['test']['sens_macro']:.3f}")
        best = max(cands, key=lambda k: cands[k]["val"]["f1_weighted"])
        b = cands[best]
        seeds = {k: v for k, v in runs.items()
                 if v["model"] == model and v["trial"] == b["trial"] and v["cw"] == b["cw"]}
        winners[model] = {"run": best, "trial": b["trial"], "cw": b["cw"], "n_trials_val": len(cands),
                          "seeds": sorted(v["seed"] for v in seeds.values()),
                          "test_por_semilla": {k: v["test"] for k, v in seeds.items()},
                          "test_media_std": mean_std([v["test"] for v in seeds.values()]),
                          "val_media_std": mean_std([v["val"] for v in seeds.values()]),
                          "files": {k: (v["val_file"], v["test_file"]) for k, v in seeds.items()}}
        ms = winners[model]["test_media_std"]
        print(f"GANADOR {model}: {best} (cw={b['cw']}), semillas={winners[model]['seeds']} -> test "
              + " ".join(f"{k}={ms[k]['mean']:.3f}±{ms[k]['std']:.3f}" for k in ["acc", "f1_weighted", "f1_macro", "sens_macro", "recall_mel"]))
    report["ganadores"] = {m: {k: v for k, v in w.items() if k != "files"} for m, w in winners.items()}

    # ---------- 3. Legacy + desbalance ----------
    extra = {}
    for f in sorted(glob.glob(str(RES / "*_les_predictions.json"))):
        name = Path(f).name.replace("_predictions.json", "")
        if RUN_RE.match(name):
            continue
        y, p, pr, _ = load(f)
        extra[name] = cls_metrics(y, p, pr)
    report["legacy_y_desbalance"] = extra
    if extra:
        print(f"\n=== Legacy y desbalance (split por lesión) ===")
        for k, m in extra.items():
            print(f"{k:34s} acc={m['acc']:.3f} f1w={m['f1_weighted']:.3f} f1m={m['f1_macro']:.3f} sensM={m['sens_macro']:.3f}")

    # ---------- 4. Melanoma ----------
    if winners:
        mel = {}
        probs_t, probs_v = {}, {}
        for model, w in winners.items():
            vf, tf = w["files"][w["run"]]
            yv, _, pv, _ = load(vf); yt, _, pt, _ = load(tf)
            probs_t[model], probs_v[model] = pt, pv
            mel[model] = {"melanoma": _task_report(model, yt, pt, [0], yv, pv),
                          "maligno": _task_report(model, yt, pt, [0, 2, 3], yv, pv)}
        if len(winners) == 2:
            pt = (probs_t["swin_tiny"] + probs_t["convnext_tiny"]) / 2
            pv = (probs_v["swin_tiny"] + probs_v["convnext_tiny"]) / 2
            mel["ensamble"] = {"melanoma": _task_report("ensamble", yt, pt, [0], yv, pv),
                               "maligno": _task_report("ensamble", yt, pt, [0, 2, 3], yv, pv)}
        report["melanoma"] = mel

    # ---------- 5. Calibración ----------
    if winners:
        cal = {}
        for model, w in winners.items():
            vf, tf = w["files"][w["run"]]
            yv, _, pv, _ = load(vf); yt, _, pt, _ = load(tf)
            r = {"sin_calibrar": calib_metrics(yt, pt)}
            for method in ["ts", "vs"]:
                apply, params = calib_fit(pv, yv, method)
                r[method] = calib_metrics(yt, apply(pt))
                if method == "ts":
                    r[method]["T"] = float(np.exp(params[0].item()))
            cal[model] = r
        report["calibracion"] = cal
        print("\n=== Calibración (ganadores, seed 42) ===")
        for model, r in cal.items():
            for meth, m in r.items():
                print(f"  {model:14s} {meth:12s} ECE={m['ece']:.3f} MCE={m['mce']:.3f} Brier={m['brier']:.3f} "
                      f"acc={m['acc']:.3f} sensM={m['sens_macro']:.3f} conf={m['conf_media']:.3f}")

    # ---------- 6. Ruteo con Swin nuevo + kNN del split por lesión ----------
    knn_csv = Path("outputs/rag/rag_context_les.csv")
    if "swin_tiny" in winners and knn_csv.exists():
        vf, tf = winners["swin_tiny"]["files"][winners["swin_tiny"]["run"]]
        yt, pt, _, ids = load(tf)
        rag = pd.read_csv(knn_csv).set_index("image_id")
        swin_dx = np.array([FULL[CLASSES[c]] for c in pt]); gt = np.array([FULL[CLASSES[c]] for c in yt])
        knn = rag.loc[ids, "rag_knn_dx"].values
        neigh = rag.loc[ids, "rag_context"].str.extract(r"diagnosed as:\s*(.+)\.$")[0].str.split(";")
        n_distinct = neigh.apply(lambda xs: len({re.sub(r"\s*\(.*\)$", "", x).strip() for x in xs})).values
        tier = np.where(swin_dx == knn, "affirmative", np.where(n_distinct >= 3, "abstention", "differential"))
        cov = np.where(tier == "affirmative", swin_dx == gt, (swin_dx == gt) | (knn == gt))
        r = {t: {"n": int((tier == t).sum()), "pct": float((tier == t).mean()), "cobertura": float(cov[tier == t].mean())}
             for t in ["affirmative", "differential", "abstention"]}
        r["cobertura_no_derivados"] = float(cov[tier != "abstention"].mean())
        r["acc_swin"] = float((swin_dx == gt).mean())
        per_class = pd.crosstab(pd.Series(gt, name="gt"), pd.Series(tier, name="tier"), normalize="index")
        r["por_clase"] = per_class.round(3).to_dict("index")
        report["ruteo"] = r
        print("\n=== Ruteo 3 niveles (Swin ganador + kNN split por lesión) ===")
        print("  " + " ".join(f"{t}={r[t]['pct']:.1%}/cov={r[t]['cobertura']:.3f}" for t in ["affirmative", "differential", "abstention"])
              + f"  cov_no_derivados={r['cobertura_no_derivados']:.3f}  acc_swin={r['acc_swin']:.3f}")
        print(per_class.round(3).to_string())

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    logger.info("Guardado en %s", OUT)


if __name__ == "__main__":
    main()
