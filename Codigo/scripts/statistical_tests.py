"""P0.2 (plan julio-agosto) — Significancia estadística de las comparaciones.

- Intervalos de confianza bootstrap (95%) para accuracy, F1-weighted y sensibilidad macro.
- Test de McNemar (exacto) por pares, sobre aciertos pareados en las mismas muestras.

Sobre los *_predictions.json de clasificadores (Swin vs DermLIP vs Mini-VLM vs LLaVA-Med).
Opcionalmente, sobre consistencia diagnóstica por-reporte del ensamble (Baseline/Grounding/Oracle)
si se pasa --consistency_json (arrays 0/1 por condición; se genera en P0.3).

100% local, sin cluster. Uso:
    python scripts/statistical_tests.py
    python scripts/statistical_tests.py --n_boot 5000
"""

import argparse
import itertools
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from scipy.stats import binomtest
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
}


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
    loaded = {}
    for name, path in models.items():
        p = Path(path)
        if not p.exists():
            logger.warning("SKIP %s: no existe %s", name, path)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        loaded[name] = {"y_true": np.asarray(d["y_true"]), "y_pred": np.asarray(d["y_pred"])}
    return loaded


def main():
    parser = argparse.ArgumentParser(description="P0.2 Tests estadísticos")
    parser.add_argument("--n_boot", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--consistency_json", type=str, default=None,
                        help="JSON {condicion: [0/1 por reporte]} para el ensamble (P0.3).")
    parser.add_argument("--output", type=str, default="outputs/results/statistical_tests.json")
    args = parser.parse_args()

    result = {"bootstrap_ci": {}, "mcnemar": {}}

    # --- Clasificadores ---
    models = _load(DEFAULT_MODELS)
    if models:
        ref_name = next(iter(models))
        ref_yt = models[ref_name]["y_true"]

        print("\n=== IC bootstrap 95%% (n_boot=%d) - clasificadores ===" % args.n_boot)
        print(f"{'Modelo':<16} {'accuracy':>22} {'f1_weighted':>22} {'sens_macro':>22}")
        for name, m in models.items():
            row = {}
            cells = []
            for mk, fn in METRICS.items():
                pt, lo, hi = bootstrap_ci(m["y_true"], m["y_pred"], fn, args.n_boot, args.seed)
                row[mk] = {"point": pt, "ci95": [lo, hi]}
                cells.append(f"{pt:.3f} [{lo:.3f},{hi:.3f}]")
            result["bootstrap_ci"][name] = row
            print(f"{name:<16} {cells[0]:>22} {cells[1]:>22} {cells[2]:>22}")

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
        else:
            logger.warning("Condiciones del ensamble con distinta longitud: McNemar omitido.")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
