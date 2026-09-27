"""S6/E1 — IC bootstrap pareado para tab:ensamble y tab:incertidumbre_e2e.

Reusa `paired_bootstrap_diff_flags` (statistical_tests.py) y
`diagnostic_consistency_flags` (clinical_ner.py) sobre los reportes ya
generados en outputs/generated_reports/mini_vlm/{full_*}. 100% local, CPU.

Con ``--anchor les`` usa los brazos re-anclados al Swin del split disjunto por lesión
(``full_swin_les``, ``full_differential_les``, ``uncertainty_3tier_les.csv``), agrega la comparación
anclaje viejo vs nuevo y guarda en ``ensemble_bootstrap[_<modelo>]_les.json``. SkinVL no tiene brazo
diferencial: para él solo se calcula la parte de tab:ensamble.

Uso:
    python scripts/ensemble_bootstrap.py                    # Mini-VLM (default)
    python scripts/ensemble_bootstrap.py --model llava_med  # 2do generador
    python scripts/ensemble_bootstrap.py --model skinvl --anchor les
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from scripts.statistical_tests import paired_bootstrap_diff_flags
from src.evaluation.clinical_ner import diagnostic_consistency_flags

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = Path("data/raw/HAM10000")
REPORTS_DIR = Path("outputs/generated_reports/mini_vlm")  # sobreescrito por --model
UNCERTAINTY_DIR = Path("outputs/uncertainty")
OUTPUT = Path("outputs/results/ensemble_bootstrap.json")

DX_TO_FULL = {
    "mel": "melanoma", "nv": "nevus", "bcc": "basal cell carcinoma",
    "akiec": "actinic keratosis", "bkl": "benign keratosis",
    "df": "dermatofibroma", "vasc": "vascular lesion",
}


def build_label_map() -> dict:
    label_map = {}
    df = pd.read_csv(DATA_DIR / "HAM10000_metadata")
    for _, row in df.iterrows():
        label_map[row["image_id"]] = DX_TO_FULL.get(row["dx"], row["dx"])
    gt_path = DATA_DIR / "ISIC2018_Task3_Test_GroundTruth.csv"
    if gt_path.exists():
        df_test = pd.read_csv(gt_path)
        for _, row in df_test.iterrows():
            label_map[row["image_id"]] = DX_TO_FULL.get(row["dx"], row["dx"])
    return label_map


def load_condition(name: str) -> dict:
    """image_id (sin .jpg) -> report text."""
    out = {}
    for f in (REPORTS_DIR / name).glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        img_id = Path(d["image_id"]).stem
        out[img_id] = d["report"]
    return out


def flags_for(cond: dict, label_map: dict, ids: list) -> list:
    reports = [cond[i] for i in ids]
    labels = [label_map[i] for i in ids]
    return diagnostic_consistency_flags(reports, labels)


def main():
    global REPORTS_DIR, OUTPUT
    parser = argparse.ArgumentParser(description="IC bootstrap pareado (ensamble + pipeline avanzado)")
    parser.add_argument("--model", default="mini_vlm", choices=["mini_vlm", "llava_med", "skinvl"])
    parser.add_argument("--anchor", default="v3", choices=["v3", "les"],
                        help="Clasificador que ancla la cascada: v3 (partición aleatoria) o les "
                             "(split disjunto por lesión).")
    args = parser.parse_args()
    REPORTS_DIR = Path("outputs/generated_reports") / args.model
    stem = "ensemble_bootstrap" if args.model == "mini_vlm" else f"ensemble_bootstrap_{args.model}"
    suffix = "_les" if args.anchor == "les" else ""
    OUTPUT = OUTPUT.with_name(f"{stem}{suffix}.json")
    swin_cond, diff_cond = f"full_swin{suffix}", f"full_differential{suffix}"
    tier_csv = UNCERTAINTY_DIR / f"uncertainty_3tier{suffix}.csv"
    logger.info("Generador: %s | anclaje: %s", args.model, args.anchor)

    label_map = build_label_map()
    conds = {name: load_condition(name) for name in
              ["full_baseline", "full_dermlip", swin_cond, "full_oracle"]}
    common_ids = sorted(set.intersection(*(set(c) for c in conds.values())))
    common_ids = [i for i in common_ids if i in label_map]
    logger.info("tab:ensamble — n=%d imágenes con las 4 condiciones + gt_label", len(common_ids))

    result = {"anchor": args.anchor, "n": len(common_ids), "consistencia": {},
              "tab_ensamble": {}, "tab_incertidumbre_e2e": {}}

    if args.anchor == "les" and (REPORTS_DIR / "full_swin").exists():
        conds["full_swin"] = load_condition("full_swin")  # anclaje v3, para medir el cambio
    flags = {name: flags_for(c, label_map, common_ids) for name, c in conds.items()}
    pairs = [(swin_cond, "full_oracle"), ("full_dermlip", swin_cond),
             ("full_baseline", swin_cond)]
    if args.anchor == "les" and "full_swin" in conds:
        pairs.append((swin_cond, "full_swin"))
    print("\n=== tab:ensamble — bootstrap pareado (%s, n=%d, n_boot=2000) ===" % (args.model, len(common_ids)))
    for a, b in pairs:
        d, lo, hi, p = paired_bootstrap_diff_flags(flags[a], flags[b], n_boot=2000, seed=42)
        result["tab_ensamble"][f"{a} vs {b}"] = {"diff": d, "ci95": [lo, hi], "p": p}
        print(f"  {a:<14} vs {b:<14}  Delta={d:+.3f} [{lo:+.3f},{hi:+.3f}]  p={p:.4f}")
    for name in conds:
        pt = sum(flags[name]) / len(flags[name])
        boot_ci = paired_bootstrap_diff_flags(flags[name], [0] * len(flags[name]), n_boot=2000, seed=42)
        result["consistencia"][name] = pt
        print(f"  point {name:<14} consistency={pt:.3f}")

    if not (REPORTS_DIR / diff_cond).exists():
        logger.warning("Sin brazo %s: se omite tab:incertidumbre_e2e", diff_cond)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Guardado en %s", OUTPUT)
        return

    # --- tab:incertidumbre_e2e: pipeline avanzado vs grounding simple, n=1445 no-abstenidos ---
    tier = pd.read_csv(tier_csv)
    affirmative_ids = set(tier[tier.tier == "affirmative"].image_id)
    differential_ids = set(tier[tier.tier == "differential"].image_id)
    non_abstained = affirmative_ids | differential_ids
    logger.info("no-abstenidos (afirmativo+diferencial) = %d", len(non_abstained))

    swin_reports = load_condition(swin_cond)
    diff_reports = load_condition(diff_cond)

    ids_e2e = sorted(i for i in non_abstained if i in label_map
                      and i in swin_reports)
    labels_e2e = [label_map[i] for i in ids_e2e]

    # Pipeline avanzado: afirmativo -> reutiliza full_swin; diferencial -> full_differential
    pipeline_reports = []
    grounding_reports = []
    for i in ids_e2e:
        grounding_reports.append(swin_reports[i])
        if i in affirmative_ids:
            pipeline_reports.append(swin_reports[i])
        else:
            pipeline_reports.append(diff_reports.get(i, ""))

    missing_diff = sum(1 for i in ids_e2e if i in differential_ids and i not in diff_reports)
    if missing_diff:
        logger.warning("%d imágenes diferenciales sin reporte full_differential", missing_diff)

    pipeline_flags = diagnostic_consistency_flags(pipeline_reports, labels_e2e)
    grounding_flags = diagnostic_consistency_flags(grounding_reports, labels_e2e)

    print("\n=== tab:incertidumbre_e2e — bootstrap pareado (n=%d) ===" % len(ids_e2e))
    print(f"  Pipeline avanzado consistency = {sum(pipeline_flags)/len(pipeline_flags):.3f}")
    print(f"  Grounding simple  consistency = {sum(grounding_flags)/len(grounding_flags):.3f}")
    d, lo, hi, p = paired_bootstrap_diff_flags(pipeline_flags, grounding_flags, n_boot=2000, seed=42)
    result["tab_incertidumbre_e2e"]["pipeline_vs_grounding_simple"] = {
        "diff": d, "ci95": [lo, hi], "p": p, "n": len(ids_e2e),
    }
    print(f"  Delta = {d:+.3f} [{lo:+.3f},{hi:+.3f}]  p={p:.4f}")

    # Subconjunto diferencial (n=334): diferencial vs grounding forzado
    diff_ids = sorted(i for i in differential_ids if i in label_map and i in diff_reports and i in swin_reports)
    labels_d = [label_map[i] for i in diff_ids]
    diff_flags = diagnostic_consistency_flags([diff_reports[i] for i in diff_ids], labels_d)
    forced_flags = diagnostic_consistency_flags([swin_reports[i] for i in diff_ids], labels_d)
    d2, lo2, hi2, p2 = paired_bootstrap_diff_flags(diff_flags, forced_flags, n_boot=2000, seed=42)
    result["tab_incertidumbre_e2e"]["differential_subset"] = {
        "diff": d2, "ci95": [lo2, hi2], "p": p2, "n": len(diff_ids),
    }
    print("\n=== Subconjunto diferencial (n=%d) ===" % len(diff_ids))
    print(f"  Diferencial      consistency = {sum(diff_flags)/len(diff_flags):.3f}")
    print(f"  Forzado (Swin)   consistency = {sum(forced_flags)/len(forced_flags):.3f}")
    print(f"  Delta = {d2:+.3f} [{lo2:+.3f},{hi2:+.3f}]  p={p2:.4f}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", OUTPUT)


if __name__ == "__main__":
    main()
