"""P0.2 (plan julio-agosto) — Significancia estadística de las comparaciones.

- Intervalos de confianza bootstrap (95%) para accuracy, F1-weighted y sensibilidad macro.
- Test de McNemar (exacto) por pares, sobre aciertos pareados en las mismas muestras.

Sobre los *_predictions.json de clasificadores (Swin vs DermLIP vs Mini-VLM vs LLaVA-Med).
Opcionalmente, sobre consistencia diagnóstica por-reporte del ensamble (Baseline/Grounding/Oracle)
si se pasa --consistency_json (arrays 0/1 por condición; se genera en P0.3).

100% local, sin cluster. Uso:
    python scripts/statistical_tests.py
    python scripts/statistical_tests.py --n_boot 5000
    # Modelos finales (split por lesión) — alinea por image_ids cuando el JSON los trae:
    python scripts/statistical_tests.py --models "Swin-Tiny=outputs/results/X_predictions.json" \
        "DermLIP (ZS)=outputs/results/dermlip/dermlip_zeroshot_vit-b-16_predictions.json" --output ...
"""

import argparse
import itertools
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy.stats import binomtest, wilcoxon
from sklearn.metrics import accuracy_score, f1_score, recall_score

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MODELS = {
    "Swin-Tiny": "outputs/results/classifiers/modern_v3/swin_tiny_modern_v3_predictions.json",
    "DermLIP (ZS)": "outputs/results/dermlip/dermlip_zeroshot_vit-b-16_predictions.json",
    "Mini-VLM (ZS)": "outputs/results/first_iteration/mini_vlm_predictions.json",
    "LLaVA-Med (ZS)": "outputs/results/first_iteration/llava_med_predictions.json",
}

METRICS = {
    "accuracy": lambda yt, yp: accuracy_score(yt, yp),
    "f1_weighted": lambda yt, yp: f1_score(yt, yp, average="weighted", zero_division=0),
    "sens_macro": lambda yt, yp: recall_score(yt, yp, average="macro", zero_division=0),
    "f1_macro": lambda yt, yp: f1_score(yt, yp, average="macro", zero_division=0),
}

_META = Path("data/raw/HAM10000/HAM10000_metadata")
_SPLITS = Path("data/splits/ham10000_splits.json")


def _canonical_test_ids() -> list:
    """Orden en que HAM10000Dataset recorre el test (metadata filtrada): el de los clasificadores."""
    import pandas as pd
    raw = pd.read_csv(_META)
    test = set(json.loads(_SPLITS.read_text(encoding="utf-8"))["test"])
    return [i for i in raw.image_id if i in test]


def bootstrap_ci(y_true, y_pred, metric_fn, n_boot=2000, seed=42, alpha=0.05):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    n = len(y_true)
    rng = np.random.default_rng(seed)
    point = metric_fn(y_true, y_pred)
    stats = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        stats[b] = metric_fn(y_true[idx], y_pred[idx])
    lo, hi = np.percentile(stats, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(point), float(lo), float(hi)


def paired_bootstrap_diff(y_true, pred_a, pred_b, metric_fn, n_boot=2000, seed=42, alpha=0.05):
    """Bootstrap PAREADO de la diferencia metric(A) - metric(B) sobre las MISMAS imágenes.
    Correcto para F1-macro / sensibilidad-macro (donde McNemar no aplica): remuestrea índices de
    imagen y recomputa la diferencia. Devuelve (diff puntual, lo, hi, p_two_sided)."""
    y_true = np.asarray(y_true); pred_a = np.asarray(pred_a); pred_b = np.asarray(pred_b)
    n = len(y_true); rng = np.random.default_rng(seed)
    point = metric_fn(y_true, pred_a) - metric_fn(y_true, pred_b)
    diffs = np.empty(n_boot)
    for b in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[b] = metric_fn(y_true[idx], pred_a[idx]) - metric_fn(y_true[idx], pred_b[idx])
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    # p aproximado (dos colas): fracción de remuestreos que cruzan 0.
    p = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
    return float(point), float(lo), float(hi), float(min(p, 1.0))


def paired_bootstrap_diff_flags(flags_a, flags_b, n_boot=2000, seed=42, alpha=0.05):
    """Bootstrap pareado de la diferencia de MEDIAS entre dos vectores binarios pareados
    (p.ej. diagnostic consistency por reporte entre dos condiciones sobre las mismas imágenes)."""
    a = np.asarray(flags_a, dtype=float); b = np.asarray(flags_b, dtype=float)
    n = len(a); rng = np.random.default_rng(seed)
    point = a.mean() - b.mean()
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        diffs[i] = a[idx].mean() - b[idx].mean()
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    p = 2 * min((diffs <= 0).mean(), (diffs >= 0).mean())
    return float(point), float(lo), float(hi), float(min(p, 1.0))


def mcnemar_exact(correct_a, correct_b):
    """McNemar exacto (binomial two-sided) sobre pares discordantes."""
    a = np.asarray(correct_a, dtype=bool)
    b = np.asarray(correct_b, dtype=bool)
    n01 = int(np.sum(a & ~b))   # A acierta, B falla
    n10 = int(np.sum(~a & b))   # A falla, B acierta
    n_disc = n01 + n10
    if n_disc == 0:
        return {"n_a_only": 0, "n_b_only": 0, "p_value": 1.0}
    p = binomtest(min(n01, n10), n_disc, 0.5, alternative="two-sided").pvalue
    return {"n_a_only": n01, "n_b_only": n10, "p_value": float(p)}


def _load(models: dict) -> dict:
    """Carga predicciones; si el JSON trae image_ids, las reordena al orden canónico del test para que
    McNemar / bootstrap pareado comparen la MISMA imagen entre modelos."""
    loaded, canon = {}, None
    for name, path in models.items():
        p = Path(path)
        if not p.exists():
            logger.warning("SKIP %s: no existe %s", name, path)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        yt, yp = np.asarray(d["y_true"]), np.asarray(d["y_pred"])
        if d.get("image_ids"):
            canon = canon or _canonical_test_ids()
            pos = {iid: i for i, iid in enumerate(d["image_ids"])}
            if all(i in pos for i in canon):
                idx = [pos[i] for i in canon]
                yt, yp = yt[idx], yp[idx]
        loaded[name] = {"y_true": yt, "y_pred": yp}
    return loaded


def main():
    parser = argparse.ArgumentParser(description="P0.2 Tests estadísticos")
    parser.add_argument("--n_boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--consistency_json", type=str, default=None,
                        help="JSON {condicion: [0/1 por reporte]} para el ensamble (P0.3).")
    parser.add_argument("--output", type=str, default="outputs/results/statistical_tests.json")
    parser.add_argument("--models", nargs="*", default=None,
                        help='Sobrescribe los modelos: "NOMBRE=ruta_predictions.json" (el primero es la referencia).')
    args = parser.parse_args()

    result = {"bootstrap_ci": {}, "mcnemar": {}}

    # --- Clasificadores ---
    model_paths = DEFAULT_MODELS
    if args.models:
        model_paths = dict(item.split("=", 1) for item in args.models)
    models = _load(model_paths)
    if models:
        ref_name = next(iter(models))
        ref_yt = models[ref_name]["y_true"]

        print("\n=== IC bootstrap 95%% (n_boot=%d) - clasificadores ===" % args.n_boot)
        print(f"{'Modelo':<16} {'accuracy':>22} {'f1_weighted':>22} {'sens_macro':>22} {'f1_macro':>22}")
        for name, m in models.items():
            row = {}
            cells = []
            for mk, fn in METRICS.items():
                pt, lo, hi = bootstrap_ci(m["y_true"], m["y_pred"], fn, args.n_boot, args.seed)
                row[mk] = {"point": pt, "ci95": [lo, hi]}
                cells.append(f"{pt:.3f} [{lo:.3f},{hi:.3f}]")
            result["bootstrap_ci"][name] = row
            print(f"{name:<16} {cells[0]:>22} {cells[1]:>22} {cells[2]:>22} {cells[3]:>22}")

        # McNemar por pares (solo modelos alineados = misma secuencia y_true)
        aligned = {n: m for n, m in models.items()
                   if len(m["y_true"]) == len(ref_yt) and np.array_equal(m["y_true"], ref_yt)}
        not_aligned = [n for n in models if n not in aligned]
        if not_aligned:
            logger.warning("McNemar omite (y_true no coincide con %s): %s", ref_name, not_aligned)
        print("\n=== McNemar exacto (p-value) - clasificadores pareados (n=%d) ===" % len(ref_yt))
        for a, b in itertools.combinations(aligned, 2):
            ca = (aligned[a]["y_pred"] == aligned[a]["y_true"])
            cb = (aligned[b]["y_pred"] == aligned[b]["y_true"])
            mc = mcnemar_exact(ca, cb)
            result["mcnemar"][f"{a} vs {b}"] = mc
            sig = "***" if mc["p_value"] < 0.001 else ("**" if mc["p_value"] < 0.01 else ("*" if mc["p_value"] < 0.05 else "ns"))
            print(f"  {a:<16} vs {b:<16}  p={mc['p_value']:.2e} {sig:>3}  "
                  f"(solo {a}={mc['n_a_only']}, solo {b}={mc['n_b_only']})")

        # Bootstrap PAREADO de la diferencia en F1-macro y sensibilidad-macro (McNemar NO aplica a
        # estas métricas; el tutor lo señaló). CI 95% de la diferencia sobre las mismas imágenes.
        f1_macro = lambda yt, yp: f1_score(yt, yp, average="macro", zero_division=0)
        sens_macro = lambda yt, yp: recall_score(yt, yp, average="macro", zero_division=0)
        print("\n=== Bootstrap pareado (CI 95%%) - diferencia en F1-macro y Sens-macro (n=%d) ===" % len(ref_yt))
        result["paired_bootstrap_diff"] = {}
        for a, b in itertools.combinations(aligned, 2):
            yt = np.asarray(aligned[a]["y_true"])
            pa = np.asarray(aligned[a]["y_pred"]); pb = np.asarray(aligned[b]["y_pred"])
            row = {}
            for mname, fn in [("f1_macro", f1_macro), ("sens_macro", sens_macro)]:
                d, lo, hi, p = paired_bootstrap_diff(yt, pa, pb, fn, args.n_boot, args.seed)
                row[mname] = {"diff": d, "ci95": [lo, hi], "p": p}
                sig = "*" if (lo > 0 or hi < 0) else "ns"
                print(f"  {a:<14} vs {b:<14} Δ{mname:<10} {d:+.3f} [{lo:+.3f},{hi:+.3f}] {sig}")
            result["paired_bootstrap_diff"][f"{a} vs {b}"] = row

        # Wilcoxon de rangos con signo sobre el recall POR CLASE (7 pares por par de modelos).
        # Complementa a McNemar (por-muestra global) con un test de si un modelo mejora la
        # discriminación de forma sistemática CLASE a CLASE.
        print("\n=== Wilcoxon (rangos con signo) - recall por clase, clasificadores pareados ===")
        result["wilcoxon_perclass"] = {}
        for a, b in itertools.combinations(aligned, 2):
            ra = recall_score(aligned[a]["y_true"], aligned[a]["y_pred"], average=None, zero_division=0)
            rb = recall_score(aligned[b]["y_true"], aligned[b]["y_pred"], average=None, zero_division=0)
            diff = np.asarray(ra) - np.asarray(rb)
            if np.all(diff == 0):
                w = {"statistic": None, "p_value": 1.0, "median_diff": 0.0, "n_classes": len(diff)}
            else:
                stat, p = wilcoxon(ra, rb, zero_method="wilcox")
                w = {"statistic": float(stat), "p_value": float(p),
                     "median_diff": float(np.median(diff)), "n_classes": int(len(diff))}
            result["wilcoxon_perclass"][f"{a} vs {b}"] = w
            sig = "*" if w["p_value"] < 0.05 else "ns"
            print(f"  {a:<16} vs {b:<16}  p={w['p_value']:.3f} {sig:>3}  "
                  f"(mediana Δrecall {a}-{b}={w['median_diff']:+.3f}, n_clases={w['n_classes']})")

    # --- Ensamble (opcional, requiere consistencia por-reporte de P0.3) ---
    if args.consistency_json:
        cons = json.loads(Path(args.consistency_json).read_text(encoding="utf-8"))
        result["ensemble_bootstrap"] = {}
        result["ensemble_mcnemar"] = {}
        print("\n=== IC bootstrap 95%% - consistencia diagnostica (ensamble) ===")
        rng = np.random.default_rng(args.seed)
        for cond, arr in cons.items():
            arr = np.asarray(arr, dtype=float)
            n = len(arr)
            pt = float(arr.mean())
            bs = np.array([arr[rng.integers(0, n, n)].mean() for _ in range(args.n_boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            result["ensemble_bootstrap"][cond] = {"point": pt, "ci95": [float(lo), float(hi)], "n": n}
            print(f"  {cond:<24} {pt:.3f} [{lo:.3f},{hi:.3f}]  (n={n})")
        lengths = {len(v) for v in cons.values()}
        if len(lengths) == 1:
            print("\n=== McNemar exacto - ensamble (pareado por reporte) ===")
            for a, b in itertools.combinations(cons, 2):
                mc = mcnemar_exact(cons[a], cons[b])
                result["ensemble_mcnemar"][f"{a} vs {b}"] = mc
                print(f"  {a:<20} vs {b:<20}  p={mc['p_value']:.2e}")
            # Bootstrap pareado de la diferencia de consistencia entre condiciones (lo correcto
            # para métricas de generación sobre las mismas imágenes; el tutor lo pidió).
            print("\n=== Bootstrap pareado (CI 95%%) - Δ consistencia entre condiciones ===")
            result["ensemble_paired_bootstrap"] = {}
            for a, b in itertools.combinations(cons, 2):
                d, lo, hi, p = paired_bootstrap_diff_flags(cons[a], cons[b], args.n_boot, args.seed)
                sig = "*" if (lo > 0 or hi < 0) else "ns"
                result["ensemble_paired_bootstrap"][f"{a} vs {b}"] = {"diff": d, "ci95": [lo, hi], "p": p}
                print(f"  {a:<18} vs {b:<18} Δ={d:+.3f} [{lo:+.3f},{hi:+.3f}] {sig}")
        else:
            logger.warning("Condiciones del ensamble con distinta longitud: McNemar omitido.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
