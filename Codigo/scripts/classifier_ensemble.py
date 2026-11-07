"""P5.1 — Ensamble de clasificadores por voto suave (promedio de probabilidades).

Combina los ``y_prob`` ya guardados de los clasificadores (mismo test HAM, n=1503) y evalúa si el
ensamble supera al mejor individual. Métrica clave: sensibilidad macro (= balanced accuracy); se
reporta también F1 macro, el criterio de selección del barrido.

Dos juegos de modelos (``--preset``):
  - ``v3``: los modern_v3 de la partición aleatoria (con fuga entre particiones). Resultado original.
  - ``les``: los ganadores del split disjunto por lesión (Swin t06, ConvNeXt t02; DenseNet y ViT solo
    existen con la receta legacy). Swin y ConvNeXt tienen semillas 42 a 51: el par Swin+ConvNeXt se
    evalúa también por semilla (media ± sd).

100% local, no requiere GPU ni cluster.

Uso:
    python scripts/classifier_ensemble.py                 # v3 (resultado original)
    python scripts/classifier_ensemble.py --preset les    # split por lesión
"""

import argparse
import json
import logging
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PRESETS = {}
PRESETS["v3"] = {
    "swin": "outputs/results/classifiers/modern_v3/swin_tiny_modern_v3_predictions.json",
    "convnext": "outputs/results/classifiers/modern_v3/convnext_tiny_modern_v3_predictions.json",
    "densenet": "outputs/results/classifiers/modern_v3/densenet_modern_v3_predictions.json",
    "vit": "outputs/results/classifiers/modern_v3/vit_modern_v3_predictions.json",
}
PRESETS["les"] = {
    "swin": "outputs/results/swin_tiny_sweep_t06_les_cwnone_predictions.json",
    "convnext": "outputs/results/convnext_tiny_sweep_t02_les_cwnone_predictions.json",
    "densenet": "outputs/results/densenet_legacy_les_predictions.json",
    "vit": "outputs/results/vit_legacy_les_predictions.json",
}
# Semillas extra del preset les (solo Swin y ConvNeXt las tienen).
LES_SEEDS = {
    "swin": "outputs/results/swin_tiny_sweep_t06_les_cwnone_s{seed}_predictions.json",
    "convnext": "outputs/results/convnext_tiny_sweep_t02_les_cwnone_s{seed}_predictions.json",
}
DEFAULT_OUTPUT = {"v3": "outputs/results/classifier_ensemble",
                  "les": "outputs/results/classifier_ensemble_les"}


def _metrics(y_true, y_prob):
    y_pred = np.asarray(y_prob).argmax(axis=1)
    return {
        "acc": accuracy_score(y_true, y_pred),
        "f1_w": f1_score(y_true, y_pred, average="weighted", zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "sens_macro": balanced_accuracy_score(y_true, y_pred),
    }


def _load(path, ref_ids=None):
    """Carga y_true/y_prob; si hay image_ids, reordena las filas según ``ref_ids``."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    y_true, y_prob = np.asarray(d["y_true"]), np.asarray(d["y_prob"], dtype=float)
    ids = d.get("image_ids")
    if ref_ids is not None and ids is not None and ids != ref_ids:
        order = [ids.index(i) for i in ref_ids]
        y_true, y_prob = y_true[order], y_prob[order]
    return y_true, y_prob, ids


def _seed_pairs(y_true_ref, ref_ids):
    """Swin+ConvNeXt por semilla (42 = corrida base) para el preset les."""
    per_seed = {}
        for seed in range(42, 52):
        probs = {}
        for name, tmpl in LES_SEEDS.items():
            path = PRESETS["les"][name] if seed == 42 else tmpl.format(seed=seed)
            yt, pr, _ = _load(path, ref_ids)
            assert (yt == y_true_ref).all(), f"y_true no coincide: {path}"
            probs[name] = pr
        per_seed[seed] = {
            "swin": _metrics(y_true_ref, probs["swin"]),
            "convnext": _metrics(y_true_ref, probs["convnext"]),
            "swin+convnext": _metrics(y_true_ref, (probs["swin"] + probs["convnext"]) / 2),
        }
    summary = {}
    for combo in ("swin", "convnext", "swin+convnext"):
        summary[combo] = {
            k: {"mean": float(np.mean([per_seed[sd][combo][k] for sd in per_seed])),
                "sd": float(np.std([per_seed[sd][combo][k] for sd in per_seed], ddof=1))}
            for k in per_seed[42][combo]
        }
    return {"por_semilla": per_seed, "resumen": summary}


def main():
    parser = argparse.ArgumentParser(description="P5.1 Ensamble de clasificadores (voto suave)")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="v3")
    parser.add_argument("--output_dir", type=str, default=None,
                        help="Default: outputs/results/classifier_ensemble[_les]")
    args = parser.parse_args()
    output_dir = args.output_dir or DEFAULT_OUTPUT[args.preset]

    probs, y_true, ref_ids = {}, None, None
    for name, path in PRESETS[args.preset].items():
        if not Path(path).exists():
            logger.warning("SKIP %s: no existe %s", name, path)
            continue
        yt, pr, ids = _load(path, ref_ids)
        if y_true is None:
            y_true, ref_ids = yt, ids
        elif not (yt == y_true).all():
            logger.error("y_true de %s no coincide con el resto. Abortando.", name)
            return
        probs[name] = pr

    logger.info("Clasificadores cargados: %s (n=%d)", list(probs), len(y_true))

    rows = []
    # Individuales
    for name, pr in probs.items():
        m = _metrics(y_true, pr)
        rows.append({"combo": name, "n_models": 1, **m})

    # Ensambles: todas las combinaciones de >=2 (priorizando las que incluyen swin)
    names = list(probs)
    for k in range(2, len(names) + 1):
        for combo in combinations(names, k):
            avg = np.mean([probs[n] for n in combo], axis=0)
            m = _metrics(y_true, avg)
            rows.append({"combo": "+".join(combo), "n_models": k, **m})

    rows.sort(key=lambda r: r["sens_macro"], reverse=True)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ensemble_results.json").write_text(
        json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    seeds = None
    if args.preset == "les":
        seeds = _seed_pairs(y_true, ref_ids)
        (out_dir / "ensemble_seeds.json").write_text(
            json.dumps(seeds, indent=2, ensure_ascii=False), encoding="utf-8")

    best_indiv = max((r for r in rows if r["n_models"] == 1), key=lambda r: r["sens_macro"])
    print(f"\n=== Ensamble de clasificadores (n={len(y_true)}) ===")
    print(f"{'Combo':<32} {'#':>2} {'Acc':>6} {'F1-w':>6} {'F1-m':>6} {'Sens.macro':>10}")
    for r in rows:
        flag = "  <- mejor individual" if r["combo"] == best_indiv["combo"] else ""
        print(f"{r['combo']:<32} {r['n_models']:>2} {r['acc']:>6.3f} {r['f1_w']:>6.3f} "
              f"{r['f1_macro']:>6.3f} {r['sens_macro']:>10.3f}{flag}")

    best = rows[0]
    print(f"\nMejor global: {best['combo']} (sens_macro={best['sens_macro']:.3f}) "
          f"vs mejor individual {best_indiv['combo']} ({best_indiv['sens_macro']:.3f}) "
          f"-> Δ={best['sens_macro']-best_indiv['sens_macro']:+.3f}")
    if seeds:
        print("\nSwin+ConvNeXt por semilla (media ± sd sobre las semillas 42 a 51):")
        for combo, m in seeds["resumen"].items():
            print(f"  {combo:<14} " + "  ".join(
                f"{k} {v['mean']:.3f}±{v['sd']:.3f}" for k, v in m.items()))


if __name__ == "__main__":
    main()
