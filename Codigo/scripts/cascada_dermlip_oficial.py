"""Cascada con DermLIP sin ajuste (protocolo oficial) como fuente del diagnóstico, con la métrica oficial.

Mide la consistencia diagnóstica del brazo ``full_dermlip_oficial`` (solo el reporte, matcher estricto, como
``ensemble_bootstrap.py --report_only --strict``) y la compara, con bootstrap pareado, con la generación sin anclaje
y con la cascada con Swin-Tiny (``full_swin_les``). Informa además la exactitud de DermLIP sobre las mismas imágenes y
la proporción de reportes que nombran el diagnóstico recibido. 100 % local, CPU.

Salida: ``outputs/results/cascada_dermlip_oficial_<modelo>.json`` (lo lee ``figuras_cap5.py``).

Uso:
    python scripts/cascada_dermlip_oficial.py --model mini_vlm
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.ensemble_bootstrap import THINK_RE, build_label_map
from scripts.statistical_tests import paired_bootstrap_diff_flags
from src.evaluation.clinical_ner import diagnostic_consistency_flags

DX_CSV = Path("outputs/full_dx_dermlip_oficial.csv")


def load_condition(model: str, name: str) -> dict:
    """image_id (sin .jpg) -> reporte sin bloques <think>."""
    out = {}
    for f in (Path("outputs/generated_reports") / model / name).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        out[Path(d["image_id"]).stem] = THINK_RE.sub("", d["report"] or "").strip()
    return out


def main():
    parser = argparse.ArgumentParser(description="Cascada con DermLIP oficial (métrica oficial)")
    parser.add_argument("--model", required=True, choices=["mini_vlm", "llava_med", "skinvl"])
    args = parser.parse_args()

    label_map = build_label_map()
    dermlip_dx = dict(zip(pd.read_csv(DX_CSV).image_id, pd.read_csv(DX_CSV).diagnosis))
    conds = {n: load_condition(args.model, n) for n in ["full_baseline", "full_dermlip_oficial", "full_swin_les"]}
    ids = sorted(i for i in set.intersection(*(set(c) for c in conds.values())) if i in label_map)
    labels = [label_map[i] for i in ids]
    flags = {n: diagnostic_consistency_flags([c[i] for i in ids], labels, strict=True) for n, c in conds.items()}
    # ¿El reporte nombra el diagnóstico que recibió de DermLIP?
    copia = diagnostic_consistency_flags([conds["full_dermlip_oficial"][i] for i in ids],
                                         [dermlip_dx[i] for i in ids], strict=True)
    acierto = [int(dermlip_dx[i] == label_map[i]) for i in ids]

    res = {"model": args.model, "report_only": True, "strict": True, "n": len(ids),
           "exactitud_dermlip": sum(acierto) / len(ids),
           "nombra_dx_recibido": sum(copia) / len(ids),
           "consistencia": sum(flags["full_dermlip_oficial"]) / len(ids),
           "consistencia_referencia": {n: sum(f) / len(ids) for n, f in flags.items()},
           "diferencias": {}}
    for a, b in [("full_dermlip_oficial", "full_baseline"), ("full_swin_les", "full_dermlip_oficial")]:
        d, lo, hi, p = paired_bootstrap_diff_flags(flags[a], flags[b], n_boot=2000, seed=42)
        res["diferencias"][f"{a} - {b}"] = {"diff": d, "ci95": [lo, hi], "p": p}
    # Consistencia según si DermLIP acertó, para ver si el generador copia el diagnóstico
    for k, nombre in [(1, "dermlip_correcto"), (0, "dermlip_incorrecto")]:
        sel = [f for f, a in zip(flags["full_dermlip_oficial"], acierto) if a == k]
        res[f"consistencia_{nombre}"] = {"n": len(sel), "consistencia": sum(sel) / len(sel) if sel else None}

    out = Path(f"outputs/results/cascada_dermlip_oficial_{args.model}.json")
    if out.exists():
        sys.exit(f"{out} ya existe; no se sobrescribe")
    out.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
