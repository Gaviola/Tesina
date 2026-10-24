"""Cifras derivadas de DermLIP zero-shot con el protocolo oficial (resul/dermlip_zs_protocolo_resul_20261024.md).

Recalcula lo que en la tesina dependía de las predicciones zero-shot anteriores, sin sobrescribir nada:
Holm sobre los 21 pares de statistical_tests_les_v3.json, DermLIP en los subconjuntos del control de fuga (misma lógica
que leakage_analysis.py) y la distribución de sus predicciones. Salida: outputs/results/dermlip/dermlip_oficial_derivados.json.

Uso (desde Codigo/):
    ../.venv/Scripts/python.exe scripts/dermlip_oficial_derivados.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from densenet_vit_moderna_report import holm  # noqa: E402
from leakage_analysis import CLASSES, by_subset, test_frame  # noqa: E402

RES = Path("outputs/results")
OUT = RES / "dermlip" / "dermlip_oficial_derivados.json"


def main():
    st = json.loads((RES / "statistical_tests_les_v3.json").read_text(encoding="utf-8"))
    h = holm({k: v["p_value"] for k, v in st["mcnemar"].items()})
    res = {"holm_v3": {"n_pares": len(h), "sig_holm": sum(v["significativo"] for v in h.values()), "pares": h}}
    print(f"Holm v3: {res['holm_v3']['sig_holm']} de {len(h)} pares significativos")
    for k, v in h.items():
        if "DermLIP" in k:
            mc = st["mcnemar"][k]
            print(f"  {k}: p = {mc['p_value']:.3g} ({mc['n_a_only']} / {mc['n_b_only']}), umbral {v['umbral']:.4f}, "
                  f"sig {v['significativo']}")

    t = test_frame()
    fugas = {}
    for et, f in (("anterior", "dermlip_zeroshot_vit-b-16_predictions.json"),
                  ("oficial", "dermlip_zeroshot_vit-b-16_oficial_predictions.json")):
        d = json.loads((RES / "dermlip" / f).read_text(encoding="utf-8"))
        assert (d["y_true"] == t.y.values).all(), f
        fugas[et] = by_subset(t, d["y_true"], d["y_pred"])
        print(f"Fuga, DermLIP {et}: todo {fugas[et]['todo']['sens_macro']:.3f}, "
              f"limpio {fugas[et]['limpio']['sens_macro']:.3f}, fugado {fugas[et]['fugado']['sens_macro']:.3f}")
    res["fuga"] = fugas

    for et, f in (("ham10000", "dermlip_zeroshot_vit-b-16_oficial_predictions.json"),
                  ("skincap", "dermlip_zeroshot_vit-b-16_oficial_clinical_predictions.json")):
        d = json.loads((RES / "dermlip" / f).read_text(encoding="utf-8"))
        c = Counter(d["y_pred"])
        k, v = c.most_common(1)[0]
        res[f"mas_predicha_{et}"] = [CLASSES[k], v / len(d["y_pred"])]
        print(f"Más predicha {et}: {CLASSES[k]} ({v / len(d['y_pred']):.3f})")

    assert not OUT.exists(), f"{OUT} ya existe: no se sobrescribe"
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"Guardado en {OUT}")


if __name__ == "__main__":
    main()
