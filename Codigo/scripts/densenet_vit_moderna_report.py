"""DenseNet121 y ViT-B/16 con la receta moderna (split por lesión) frente a los ganadores del barrido.

Plan: docs/ideas/densenet_vit_moderna_plan_20261012.md (TOKO jobs 99007–99012).

1. Media ± desvío de 10 semillas (42 a 51) en test y en validación para los cuatro modelos con la receta moderna, con las mismas
   métricas que lesion_split_report.py (acc, F1 ponderado, F1 macro, sens. macro, recall MEL, AUC macro).
2. Receta anterior (legacy, semilla 42, vista única) frente a la moderna (semilla 42 y media) por modelo.
3. Corrección de Holm sobre los 21 pares de McNemar de statistical_tests_les_v2.json (que ya usa las corridas
   modernas de DenseNet121 y ViT-B/16) y comparación con la familia anterior (statistical_tests_les.json, legacy).

100 % local. Uso (desde Codigo/):
    python scripts/densenet_vit_moderna_report.py
Salida: outputs/results/densenet_vit_moderna_report.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.lesion_split_report import cls_metrics, load, mean_std

RES = Path("outputs/results")
OUT = RES / "densenet_vit_moderna_report.json"
RUNS = {
    "Swin-Tiny": "swin_tiny_sweep_t06_les_cwnone",
    "ConvNeXt-Tiny": "convnext_tiny_sweep_t02_les_cwnone",
    "DenseNet121": "densenet_sweep_t02_les_cwnone",
    "ViT-B/16": "vit_sweep_t06_les_cwnone",
}
LEGACY = {"DenseNet121": "densenet_legacy_les", "ViT-B/16": "vit_legacy_les"}
KEYS = ["acc", "f1_weighted", "f1_macro", "sens_macro", "recall_mel", "auc_macro_ovr"]


def holm(ps: dict, alpha: float = 0.05) -> dict:
    """Holm–Bonferroni: rechaza en orden creciente mientras p_(k) <= alpha / (m - k + 1)."""
    order = sorted(ps, key=ps.get)
    m, out, stop = len(order), {}, False
    for k, key in enumerate(order, start=1):
        thr = alpha / (m - k + 1)
        stop = stop or ps[key] > thr
        out[key] = {"p": ps[key], "umbral": thr, "significativo": not stop}
    return out


SEMILLAS = tuple(range(42, 52))  # plan supervisados_diez_ejecuciones_plan_20261103


def run_metrics(run: str, split: str = "") -> dict:
    yt, pt, prt, _ = load(RES / f"{run}_{split}predictions.json")
    return cls_metrics(yt, pt, prt)


def main():
    report = {"semillas": {}, "media_std": {}, "val_media_std": {}, "legacy_vs_moderna": {}, "holm": {}}

    print(f"{'modelo':14s} " + " ".join(f"{k:>15s}" for k in KEYS))
    for name, base in RUNS.items():
        rows = {s: run_metrics(base if s == 42 else f"{base}_s{s}") for s in SEMILLAS}
        report["semillas"][name] = rows
        ms = mean_std(list(rows.values()))
        report["media_std"][name] = ms
        print(f"{name:14s} " + " ".join(f"{ms[k]['mean']:.3f} ± {ms[k]['std']:.3f}" for k in KEYS))
        val = [run_metrics(base if s == 42 else f"{base}_s{s}", "val_") for s in SEMILLAS]
        report["val_media_std"][name] = mean_std(val)

    print(f"\nValidación (media ± sd, {len(SEMILLAS)} semillas)")
    for name, ms in report["val_media_std"].items():
        print(f"{name:14s} " + " ".join(f"{ms[k]['mean']:.3f} ± {ms[k]['std']:.3f}" for k in KEYS))

    print("\nReceta anterior (s42, vista única) → moderna (s42 | media)")
    for name, run in LEGACY.items():
        leg = run_metrics(run)
        mod42 = report["semillas"][name][42]
        mod = report["media_std"][name]
        report["legacy_vs_moderna"][name] = {
            "legacy": leg, "moderna_s42": mod42,
            "delta_s42": {k: mod42[k] - leg[k] for k in KEYS},
            "delta_media": {k: mod[k]["mean"] - leg[k] for k in KEYS},
        }
        print(f"{name:14s} " + " ".join(f"{k}: {leg[k]:.3f}→{mod42[k]:.3f}|{mod[k]['mean']:.3f}" for k in KEYS))

    for tag, path in [("moderna", RES / "statistical_tests_les_v2.json"), ("anterior", RES / "statistical_tests_les.json")]:
        mc = json.loads(path.read_text(encoding="utf-8"))["mcnemar"]
        h = holm({k: v["p_value"] for k, v in mc.items()})
        report["holm"][tag] = {"fuente": str(path), "n_pares": len(h),
                               "sig_sin_correccion": sum(v["p_value"] < 0.05 for v in mc.values()),
                               "sig_holm": sum(v["significativo"] for v in h.values()), "pares": h}
        print(f"\nHolm ({tag}, {len(h)} pares): sin corrección {report['holm'][tag]['sig_sin_correccion']}, "
              f"con Holm {report['holm'][tag]['sig_holm']}")
        for k, v in h.items():
            if v["p"] > 1e-6:
                print(f"  {k:36s} p={v['p']:.4f} umbral={v['umbral']:.4f} {'*' if v['significativo'] else 'ns'}")

    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en {OUT}")


if __name__ == "__main__":
    main()
