"""Derivados del Cap. 5 con la métrica oficial de la cascada (solo el reporte, matcher estricto).

Reúne en un JSON las cifras del capítulo de generación que no estaban calculadas con la métrica oficial o
que no existían como archivo: generación sin anclaje (consistencia exclusiva, reportes distintos, longitud,
bloques <think>), taxonomía de fallas con las categorías de la Tabla 2.x (separando las reservas con y sin
diagnóstico), ablaciones sin imagen y con diagnóstico equivocado, sensibilidad por clase del ancla frente a la
consistencia por clase, ruteo (acierto de Swin y del kNN por nivel, errores compartidos, melanoma) y el
efecto de un vecino equivocado en la recuperación. 100 % local, CPU.

Uso:
    python scripts/cap5_derivados.py   # -> outputs/results/cap5_derivados.json
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.ensemble_bootstrap import build_label_map
from scripts.statistical_tests import paired_bootstrap_diff_flags
from src.evaluation.clinical_ner import (
    CLASS_RE,
    _compute_entity_recall,
    _extract_dict_entities,
    diagnostic_consistency_flags,
)
from scripts.error_taxonomy import _is_hedging, _is_repetition

ROOT = Path("outputs/generated_reports")
OUT = Path("outputs/results/cap5_derivados.json")
THINK_RE = re.compile(r"<think>.*?(?:</think>|$)", re.DOTALL | re.IGNORECASE)
GENERADORES = ["mini_vlm", "llava_med", "skinvl"]
CLASES = ["melanoma", "nevus", "basal cell carcinoma", "actinic keratosis", "benign keratosis",
          "dermatofibroma", "vascular lesion"]


def cargar(modelo: str, brazo: str) -> dict:
    """image_id -> (reporte sin <think>, texto crudo)."""
    out = {}
    for f in (ROOT / modelo / brazo).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        crudo = d.get("report") or ""
        out[Path(d["image_id"]).stem] = (THINK_RE.sub("", crudo).strip(), crudo)
    return out


def clases_nombradas(texto: str) -> set:
    t = texto.lower()
    return {c for c, rx in CLASS_RE.items() if rx.search(t)}


def falla(reporte: str, gt: str) -> str:
    """Falla principal con las categorías del marco (diagnóstico incorrecto, contradicción, hedging,
    repetición, texto insuficiente). A diferencia de error_taxonomy.py, una expresión de reserva junto al
    diagnóstico correcto y sin otra clase cuenta como diagnóstico correcto («consistent with nevus»)."""
    t = reporte.lower().strip()
    nombradas = clases_nombradas(t)
    recall = _compute_entity_recall(_extract_dict_entities(reporte))
    if _is_repetition(t):
        return "repeticion"
    if len(t.split()) < 12 or (recall < 0.10 and gt not in nombradas):
        return "insuficiente"
    if len(nombradas) >= 2:
        return "contradiccion"
    if nombradas and gt not in nombradas:
        return "dx_incorrecto"
    if gt in nombradas:
        return "correcto_con_reserva" if _is_hedging(t) else "correcto"
    return "hedging" if _is_hedging(t) else "sin_diagnostico"


def resumen_brazo(rep: dict, ids: list, lab: dict) -> dict:
    textos = [rep[i][0] for i in ids]
    gts = [lab[i] for i in ids]
    flags = diagnostic_consistency_flags(textos, gts, strict=True)
    excl = [int(clases_nombradas(t) == {g}) for t, g in zip(textos, gts)]
    palabras = sorted(len(t.split()) for t in textos)
    conteo = Counter(textos)
    fallas = Counter(falla(t, g) for t, g in zip(textos, gts))
    return {
        "n": len(ids),
        "consistencia": sum(flags) / len(ids),
        "consistencia_exclusiva": sum(excl) / len(ids),
        "clases_nombradas_media": sum(len(clases_nombradas(t)) for t in textos) / len(ids),
        "reportes_distintos": len(conteo),
        "fraccion_texto_mas_comun": conteo.most_common(1)[0][1] / len(ids),
        "texto_mas_comun": conteo.most_common(1)[0][0][:200],
        "mediana_palabras": palabras[len(palabras) // 2],
        "con_think": sum("<think>" in rep[i][1].lower() for i in ids),
        "vacios": sum(not t for t in textos),
        "cobertura_entidades": sum(_compute_entity_recall(_extract_dict_entities(t)) for t in textos) / len(ids),
        "fallas": {k: v / len(ids) for k, v in fallas.items()},
    }


def jaccard_intraclase(rep: dict, ids: list, lab: dict) -> float:
    """Media de la similitud de Jaccard entre pares de reportes de una misma clase (por clase, luego media)."""
    import itertools
    import random
    rnd = random.Random(42)
    medias = []
    for c in CLASES:
        cs = [set(rep[i][0].lower().split()) for i in ids if lab[i] == c]
        pares = list(itertools.combinations(range(len(cs)), 2))
        if not pares:
            continue
        pares = rnd.sample(pares, min(2000, len(pares)))
        medias.append(sum(len(cs[a] & cs[b]) / max(len(cs[a] | cs[b]), 1) for a, b in pares) / len(pares))
    return sum(medias) / len(medias)


def main():
    lab = build_label_map()
    res = {"sin_anclaje": {}, "fallas": {}, "ablaciones": {}, "por_clase": {}, "ruteo": {}, "recuperacion": {}}

    # 1. Generación sin anclaje y fallas por fuente de diagnóstico
    for m in GENERADORES:
        res["fallas"][m] = {}
        for brazo in ["full_baseline", "full_swin_les", "full_oracle"]:
            rep = cargar(m, brazo)
            ids = sorted(i for i in rep if i in lab)
            r = resumen_brazo(rep, ids, lab)
            res["fallas"][m][brazo] = r
            if brazo == "full_baseline":
                res["sin_anclaje"][m] = r

    # 2. Ablaciones: oracle con imagen, sin imagen y diagnóstico equivocado, sobre las mismas imágenes
    for m in GENERADORES:
        conds = {b: cargar(m, b) for b in ["full_oracle", "full_oracle_noimage", "full_wrong_swap"]}
        ids = sorted(set.intersection(*(set(c) for c in conds.values())) & set(lab))
        fl = {b: diagnostic_consistency_flags([c[i][0] for i in ids], [lab[i] for i in ids], strict=True)
              for b, c in conds.items()}
        d, lo, hi, p = paired_bootstrap_diff_flags(fl["full_oracle_noimage"], fl["full_oracle"], n_boot=2000, seed=42)
        res["ablaciones"][m] = {
            "n": len(ids),
            **{b: sum(f) / len(ids) for b, f in fl.items()},
            "sin_imagen_menos_con_imagen": {"diff": d, "ci95": [lo, hi], "p": p},
            "reportes_distintos": {b: len({c[i][0] for i in ids}) for b, c in conds.items()},
            "jaccard_intraclase": {b: jaccard_intraclase(c, ids, lab) for b, c in conds.items()
                                   if b != "full_wrong_swap"},
            "cobertura_entidades": {b: sum(_compute_entity_recall(_extract_dict_entities(c[i][0])) for i in ids)
                                    / len(ids) for b, c in conds.items()},
        }
        # make_wrong_dx.py escribe «melanocytic nevus»; el matcher estricto lo llama «nevus»
        swap = pd.read_csv("outputs/full_dx_wrong_swap.csv").set_index("image_id").diagnosis.replace(
            {"melanocytic nevus": "nevus"})
        rep_swap = conds["full_wrong_swap"]
        res["ablaciones"][m]["nombra_dx_equivocado"] = sum(
            bool(CLASS_RE[swap[i]].search(rep_swap[i][0].lower())) for i in ids) / len(ids)

    # 3. Por clase: sensibilidad del ancla (Swin, semilla 42) frente a la consistencia de la cascada
    swin = pd.read_csv("outputs/full_dx_swin_les.csv").set_index("image_id").diagnosis
    ids_test = sorted(i for i in swin.index if i in lab)
    res["por_clase"]["sensibilidad_swin"] = {
        c: sum(swin[i] == c for i in ids_test if lab[i] == c) / sum(lab[i] == c for i in ids_test) for c in CLASES}
    res["por_clase"]["n"] = {c: sum(lab[i] == c for i in ids_test) for c in CLASES}
    res["por_clase"]["exactitud_swin"] = sum(swin[i] == lab[i] for i in ids_test) / len(ids_test)
    for m in GENERADORES:
        rep = cargar(m, "full_swin_les")
        res["por_clase"][m] = {}
        for c in CLASES:
            ids_c = [i for i in ids_test if lab[i] == c and i in rep]
            fl = diagnostic_consistency_flags([rep[i][0] for i in ids_c], [c] * len(ids_c), strict=True)
            res["por_clase"][m][c] = sum(fl) / len(ids_c)
        # Copia del ancla: consistencia cuando el ancla acierta y cuando se equivoca
        ok = [i for i in ids_test if swin[i] == lab[i] and i in rep]
        mal = [i for i in ids_test if swin[i] != lab[i] and i in rep]
        f_ok = diagnostic_consistency_flags([rep[i][0] for i in ok], [lab[i] for i in ok], strict=True)
        f_mal = diagnostic_consistency_flags([rep[i][0] for i in mal], [lab[i] for i in mal], strict=True)
        f_ancla = diagnostic_consistency_flags([rep[i][0] for i in ids_test], [swin[i] for i in ids_test], strict=True)
        res["por_clase"][m]["_ancla_correcta"] = {"n": len(ok), "consistencia": sum(f_ok) / len(ok)}
        res["por_clase"][m]["_ancla_equivocada"] = {"n": len(mal), "consistencia": sum(f_mal) / len(mal)}
        res["por_clase"][m]["_nombra_el_ancla"] = sum(f_ancla) / len(ids_test)

    # 4. Ruteo: acierto por nivel, errores compartidos, melanoma
    t = pd.read_csv("outputs/uncertainty/uncertainty_3tier_les.csv")
    knn = pd.read_csv("outputs/rag/rag_context_les.csv").set_index("image_id").rag_knn_dx
    t["swin"] = t.image_id.map(swin)
    t["y"] = t.image_id.map(lab)
    t["knn"] = t.image_id.map(knn)
    t["swin_ok"] = t["swin"] == t["y"]
    t["knn_ok"] = t["knn"] == t["y"]
    t["par_ok"] = t.swin_ok | t.knn_ok
    niveles = {}
    for nivel, g in t.groupby("tier"):
        niveles[nivel] = {"n": len(g), "swin": g.swin_ok.mean(), "knn": g.knn_ok.mean(), "par": g.par_ok.mean(),
                          "swin_aciertos": int(g.swin_ok.sum())}
    afirm = t[t.tier == "affirmative"]
    mel = t[t.y == "melanoma"]
    mel_af_mal = mel[(mel.tier == "affirmative") & ~mel.swin_ok]
    dif_mel = mel[mel.tier == "differential"]
    res["ruteo"] = {
        "niveles": niveles,
        "errores_swin": int((~t.swin_ok).sum()),
        "errores_swin_en_afirmativo": int((~afirm.swin_ok).sum()),
        "por_clase": {c: {nv: int(((t.y == c) & (t.tier == nv)).sum()) for nv in
                          ["affirmative", "differential", "abstention"]} for c in CLASES},
        "melanoma_afirmado_con_error": {"n": len(mel_af_mal), "como": dict(Counter(mel_af_mal.swin))},
        "melanoma_diferencial_pares": dict(Counter(dif_mel.apply(lambda r: " / ".join(sorted([r.swin, r.knn])),
                                                                 axis=1))),
        "melanoma_diferencial_par_ok": float(dif_mel.par_ok.mean()),
    }

    # 5. Recuperación: qué pasa cuando el vecino contradice al ancla
    swin_rep = cargar("mini_vlm", "full_swin_les")
    srag = cargar("mini_vlm", "full_swin_rag_les")
    rag = cargar("mini_vlm", "full_rag_les")
    grupos = {"swin_ok_knn_mal": (t.swin_ok & ~t.knn_ok), "swin_mal_knn_ok": (~t.swin_ok & t.knn_ok),
              "ambos_ok": (t.swin_ok & t.knn_ok), "ambos_mal": (~t.swin_ok & ~t.knn_ok)}
    for nombre, mask in grupos.items():
        ids = [i for i in t[mask].image_id if i in swin_rep and i in srag and i in rag]
        gts = [lab[i] for i in ids]
        f_s = diagnostic_consistency_flags([swin_rep[i][0] for i in ids], gts, strict=True)
        f_sr = diagnostic_consistency_flags([srag[i][0] for i in ids], gts, strict=True)
        f_r = diagnostic_consistency_flags([rag[i][0] for i in ids], gts, strict=True)
        d, lo, hi, p = paired_bootstrap_diff_flags(f_sr, f_s, n_boot=2000, seed=42)
        res["recuperacion"][nombre] = {"n": len(ids), "swin": sum(f_s) / len(ids), "swin_rag": sum(f_sr) / len(ids),
                                       "rag": sum(f_r) / len(ids),
                                       "swin_rag_menos_swin": {"diff": d, "ci95": [lo, hi], "p": p}}

    # 6. Comparación pareada entre generadores (mismas imágenes y mismo diagnóstico inyectado)
    res["entre_generadores"] = {}
    for brazo in ["full_swin_les", "full_oracle"]:
        reps = {m: cargar(m, brazo) for m in GENERADORES}
        ids = sorted(set.intersection(*(set(r) for r in reps.values())) & set(lab))
        fl = {m: diagnostic_consistency_flags([reps[m][i][0] for i in ids], [lab[i] for i in ids], strict=True)
              for m in GENERADORES}
        for a, b in [("mini_vlm", "llava_med"), ("mini_vlm", "skinvl")]:
            d, lo, hi, p = paired_bootstrap_diff_flags(fl[a], fl[b], n_boot=2000, seed=42)
            res["entre_generadores"][f"{brazo}: {a} - {b}"] = {"n": len(ids), "diff": d, "ci95": [lo, hi], "p": p}

    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Guardado en {OUT}")


if __name__ == "__main__":
    main()
