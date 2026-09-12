"""Auditoría de leakage lesión-nivel en el split de HAM10000 (feedback tutor 2026-09-12).

El split original (`prepare_data.py::generate_splits_ham10000`) es estratificado POR IMAGEN, no agrupado
por `lesion_id`: HAM10000 tiene 10015 imágenes de 7470 lesiones, así que distintas fotos de una misma
lesión pueden caer en train y test. Este script cuantifica cuánto infla eso los resultados SIN re-entrenar,
re-evaluando las predicciones ya guardadas sobre dos subconjuntos del test:

  - limpio : imágenes cuya lesión NO aparece en train ni en val.
  - fugado : imágenes cuya lesión SÍ aparece en train.

Cubre clasificadores supervisados, VLMs (likelihood), DermLIP ZS, kNN-DermLIP (recuperación), detección de
melanoma (umbrales fijados en val), el ruteo de 3 niveles y la diagnostic consistency de los reportes.
Además calcula macro-F1 para todas las filas de tab:clasificacion. 100% local, CPU.

Uso:
    python scripts/leakage_analysis.py
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    recall_score,
    roc_auc_score,
)

from src.evaluation.clinical_ner import diagnostic_consistency_flags

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

META = Path("data/raw/HAM10000/HAM10000_metadata")
SPLITS = Path("data/splits/ham10000_splits.json")
RES = Path("outputs/results")
OUT = RES / "leakage_analysis.json"

CLASSES = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
FULL = {"MEL": "melanoma", "NV": "nevus", "BCC": "basal cell carcinoma", "AKIEC": "actinic keratosis",
        "BKL": "benign keratosis", "DF": "dermatofibroma", "VASC": "vascular lesion"}
FULL_TO_IDX = {v: CLASSES.index(k) for k, v in FULL.items()}

# Filas de tab:clasificacion (+ variantes relevantes para el cuadro de protocolos).
CLASSIFIER_PREDS = {
    "DenseNet121 (legacy)": RES / "densenet_legacy_predictions.json",
    "ViT-B/16 (legacy)": RES / "vit_legacy_predictions.json",
    "ConvNeXt-Tiny (sweep t06, elegido por test)": RES / "convnext_tiny_sweep_t06_predictions.json",
    "ConvNeXt-Tiny (sweep t09, elegido por val)": RES / "convnext_tiny_sweep_t09_predictions.json",
    "Swin-Tiny (sweep t08, headline)": RES / "swin_tiny_sweep_t08_predictions.json",
    "Swin-Tiny (CE simple, tab:desbalance)": RES / "swin_imb_ce_predictions.json",
    "Swin-Tiny (modern_v3, TTA)": RES / "classifier_ensemble/swin_tiny_tta_predictions.json",
    "ConvNeXt-Tiny (modern_v3, TTA)": RES / "classifier_ensemble/convnext_tiny_tta_predictions.json",
}
ID_PREDS = {
    "LLaVA-Med likelihood (ZS)": RES / "llava_med/v1/llava_med_likelihood_predictions.json",
    "Mini-VLM likelihood (ZS)": RES / "mini_vlm/v1/mini_vlm_likelihood_predictions.json",
    "LLaVA-Med likelihood (FT)": RES / "llava_med/v2/llava_med_likelihood_finetuned_predictions.json",
    "Mini-VLM likelihood (FT)": RES / "mini_vlm/v2/mini_vlm_likelihood_finetuned_predictions.json",
    "DermLIP (zero-shot)": RES / "dermlip/dermlip_zeroshot_vit-b-16_predictions.json",
}


def test_frame() -> pd.DataFrame:
    """Test en el MISMO orden que las predicciones (metadata filtrada, no el orden del json de splits)."""
    raw = pd.read_csv(META)
    splits = json.loads(SPLITS.read_text(encoding="utf-8"))
    les = {k: set(raw[raw.image_id.isin(set(v))].lesion_id) for k, v in splits.items()}
    t = raw[raw.image_id.isin(set(splits["test"]))].copy().reset_index(drop=True)
    t["y"] = t.dx.str.upper().map({c: i for i, c in enumerate(CLASSES)})
    t["in_train"] = t.lesion_id.isin(les["train"])
    t["clean"] = ~t.lesion_id.isin(les["train"] | les["val"])
    return t


def metrics(y, p, prob=None) -> dict:
    labels = list(range(len(CLASSES)))
    out = {
        "n": int(len(y)),
        "acc": accuracy_score(y, p),
        "f1_weighted": f1_score(y, p, labels=labels, average="weighted", zero_division=0),
        "f1_macro": f1_score(y, p, labels=labels, average="macro", zero_division=0),
        "sens_macro": recall_score(y, p, labels=labels, average="macro", zero_division=0),
        "recall_per_class": dict(zip(CLASSES, recall_score(y, p, labels=labels, average=None,
                                                           zero_division=0).tolist())),
    }
    if prob is not None:
        mel = (np.asarray(y) == 0).astype(int)
        out["auc_mel"] = roc_auc_score(mel, prob[:, 0])
    return out


def by_subset(t: pd.DataFrame, y, p, prob=None) -> dict:
    y, p = np.asarray(y), np.asarray(p)
    res = {}
    for name, mask in [("todo", np.ones(len(t), bool)), ("limpio", t.clean.values),
                       ("fugado", t.in_train.values)]:
        res[name] = metrics(y[mask], p[mask], None if prob is None else prob[mask])
    return res


def bootstrap_ci(values: np.ndarray, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    means = [values[rng.integers(0, len(values), len(values))].mean() for _ in range(n_boot)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def load_reports(model: str, cond: str) -> dict:
    out = {}
    for f in (Path("outputs/generated_reports") / model / cond).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[Path(d["image_id"]).stem] = d["report"]
    return out


def main():
    t = test_frame()
    ids = t.image_id.tolist()
    res = {"split": {
        "n_test": len(t), "fugado_train": int(t.in_train.sum()), "limpio": int(t.clean.sum()),
        "fugado_por_clase": t.groupby("dx").in_train.agg(["sum", "count"]).to_dict("index"),
    }}
    logger.info("test=%d  fugado(train)=%d  limpio=%d", len(t), t.in_train.sum(), t.clean.sum())

    # ---- Clasificadores y VLMs ----
    res["clasificacion"] = {}
    for name, f in CLASSIFIER_PREDS.items():
        d = json.loads(f.read_text(encoding="utf-8"))
        assert (np.asarray(d["y_true"]) == t.y.values).all(), f"orden desalineado: {f}"
        prob = np.asarray(d["y_prob"]) if d.get("y_prob") else None
        res["clasificacion"][name] = by_subset(t, d["y_true"], d["y_pred"], prob)
    for name, f in ID_PREDS.items():
        d = json.loads(f.read_text(encoding="utf-8"))
        pos = {iid: i for i, iid in enumerate(d["image_ids"])}
        idx = [pos[i] for i in ids]
        yp = np.asarray(d["y_pred"])[idx]
        assert (np.asarray(d["y_true"])[idx] == t.y.values).all(), f"etiquetas desalineadas: {f}"
        res["clasificacion"][name] = by_subset(t, t.y.values, yp)

    # ---- CSVs del pipeline: Swin single-view (ancla), kNN-DermLIP, ruteo ----
    def csv_pred(path, col):
        m = pd.read_csv(path).set_index("image_id")[col].map(FULL_TO_IDX)
        return m.reindex(ids).values

    swin_sv = csv_pred("outputs/full_dx_swin.csv", "diagnosis")
    knn = csv_pred("outputs/rag/rag_context.csv", "rag_knn_dx")
    res["clasificacion"]["Swin-Tiny (single-view, ancla del ensamble)"] = by_subset(t, t.y.values, swin_sv)
    res["clasificacion"]["kNN-DermLIP (recuperación, k=3)"] = by_subset(t, t.y.values, knn)

    tiers = pd.read_csv("outputs/uncertainty/uncertainty_3tier.csv").set_index("image_id").reindex(ids)
    routing = {}
    for name, mask in [("todo", np.ones(len(t), bool)), ("limpio", t.clean.values), ("fugado", t.in_train.values)]:
        sub = tiers[mask]; y = t.y.values[mask]; s = swin_sv[mask]; k = knn[mask]
        r = {"n": int(mask.sum())}
        for tier in ["affirmative", "differential", "abstention"]:
            m = (sub.tier == tier).values
            cov = (s[m] == y[m]) if tier == "affirmative" else ((s[m] == y[m]) | (k[m] == y[m]))
            r[tier] = {"n": int(m.sum()), "pct": float(m.mean()), "cobertura": float(cov.mean()) if m.any() else None}
        nd = (sub.tier != "abstention").values
        cov_nd = np.where((sub.tier == "affirmative").values, s == y, (s == y) | (k == y))[nd]
        r["cobertura_no_derivados"] = float(cov_nd.mean())
        routing[name] = r
    res["ruteo_3_niveles"] = routing

    # ---- Detección de melanoma con umbrales fijados en val ----
    mel_json = json.loads((RES / "melanoma/melanoma_detection.json").read_text(encoding="utf-8"))
    probs = {
        "Swin-Tiny (TTA)": np.asarray(json.loads((RES / "classifier_ensemble/swin_tiny_tta_predictions.json")
                                                 .read_text())["y_prob"]),
        "ConvNeXt-Tiny (TTA)": np.asarray(json.loads((RES / "classifier_ensemble/convnext_tiny_tta_predictions.json")
                                                     .read_text())["y_prob"]),
    }
    probs["Ensamble (voto suave)"] = (probs["Swin-Tiny (TTA)"] + probs["ConvNeXt-Tiny (TTA)"]) / 2
    res["melanoma"] = {}
    for name, pr in probs.items():
        thr = mel_json[name]["melanoma"]["op_spec85"]["thr"]
        out = {}
        for sub, mask in [("todo", np.ones(len(t), bool)), ("limpio", t.clean.values), ("fugado", t.in_train.values)]:
            y = (t.y.values[mask] == 0).astype(int); s = pr[mask, 0]; pred = (s >= thr).astype(int)
            tp = int(((pred == 1) & (y == 1)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
            tn = int(((pred == 0) & (y == 0)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
            out[sub] = {"n": int(mask.sum()), "n_mel": int(y.sum()), "auc_roc": roc_auc_score(y, s),
                        "pr_auc": average_precision_score(y, s), "sens_esp85": tp / max(tp + fn, 1),
                        "espec": tn / max(tn + fp, 1)}
        res["melanoma"][name] = out

    # ---- Diagnostic consistency de los reportes (ensamble + pipeline avanzado) ----
    labels_full = [FULL[c] for c in t.dx.str.upper()]
    lab = dict(zip(ids, labels_full))
    res["generacion"] = {}
    for model in ["mini_vlm", "llava_med"]:
        g = {}
        conds = {c: load_reports(model, c) for c in ["full_baseline", "full_dermlip", "full_swin", "full_oracle",
                                                      "full_differential"]}
        for cond in ["full_baseline", "full_dermlip", "full_swin", "full_oracle"]:
            rep = conds[cond]
            flags = np.asarray(diagnostic_consistency_flags([rep.get(i, "") for i in ids], labels_full), float)
            have = np.asarray([i in rep for i in ids])
            g[cond] = {sub: {"n": int((mask & have).sum()), "consistency": float(flags[mask & have].mean())}
                       for sub, mask in [("todo", np.ones(len(t), bool)), ("limpio", t.clean.values),
                                         ("fugado", t.in_train.values)]}
        if len(conds["full_differential"]) > 0:
            tier = tiers.tier.values
            nd = tier != "abstention"
            rep_adv = [conds["full_differential"].get(i, "") if tr == "differential" else conds["full_swin"].get(i, "")
                       for i, tr in zip(ids, tier)]
            f_adv = np.asarray(diagnostic_consistency_flags(rep_adv, labels_full), float)
            f_sim = np.asarray(diagnostic_consistency_flags([conds["full_swin"].get(i, "") for i in ids],
                                                            labels_full), float)
            e2e = {}
            for sub, mask in [("todo", np.ones(len(t), bool)), ("limpio", t.clean.values), ("fugado", t.in_train.values)]:
                m = mask & nd
                diff = f_adv[m] - f_sim[m]
                lo, hi = bootstrap_ci(diff)
                e2e[sub] = {"n": int(m.sum()), "grounding_simple": float(f_sim[m].mean()),
                            "pipeline_avanzado": float(f_adv[m].mean()), "delta": float(diff.mean()),
                            "ci95": [lo, hi]}
            g["pipeline_avanzado_e2e"] = e2e
        res["generacion"][model] = g
    _ = lab

    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---- Reporte ----
    print(f"\n=== Split: {res['split']['fugado_train']}/{len(t)} test con lesión en train; limpio={res['split']['limpio']} ===")
    print(f"\n{'modelo':52s} {'sub':7s} {'n':>5s} {'acc':>6s} {'f1w':>6s} {'f1m':>6s} {'sensM':>6s} {'recMEL':>6s}")
    for name, r in res["clasificacion"].items():
        for sub in ["todo", "limpio", "fugado"]:
            m = r[sub]
            print(f"{name[:52]:52s} {sub:7s} {m['n']:5d} {m['acc']:.3f} {m['f1_weighted']:.3f} {m['f1_macro']:.3f} "
                  f"{m['sens_macro']:.3f} {m['recall_per_class']['MEL']:.3f}")
    print("\n=== Melanoma (umbral esp>=85 fijado en val) ===")
    for name, r in res["melanoma"].items():
        for sub, m in r.items():
            print(f"  {name:24s} {sub:7s} n={m['n']:4d} mel={m['n_mel']:3d} AUC={m['auc_roc']:.3f} "
                  f"PR={m['pr_auc']:.3f} sens={m['sens_esp85']:.3f} espec={m['espec']:.3f}")
    print("\n=== Ruteo 3 niveles ===")
    for sub, r in routing.items():
        print(f"  {sub:7s} n={r['n']} " + " ".join(f"{k}={r[k]['pct']:.1%}/cov={r[k]['cobertura']:.3f}"
                                                    for k in ["affirmative", "differential", "abstention"])
              + f"  cov_no_derivados={r['cobertura_no_derivados']:.3f}")
    print("\n=== Diagnostic consistency ===")
    for model, g in res["generacion"].items():
        for cond, r in g.items():
            if cond == "pipeline_avanzado_e2e":
                for sub, m in r.items():
                    print(f"  {model:9s} e2e {sub:7s} n={m['n']} simple={m['grounding_simple']:.3f} "
                          f"avanzado={m['pipeline_avanzado']:.3f} delta={m['delta']:+.3f} [{m['ci95'][0]:+.3f},{m['ci95'][1]:+.3f}]")
            else:
                print(f"  {model:9s} {cond:14s} " + " ".join(f"{s}={r[s]['consistency']:.3f}(n={r[s]['n']})"
                                                         for s in ["todo", "limpio", "fugado"]))
    logger.info("Guardado en %s", OUT)


if __name__ == "__main__":
    main()
