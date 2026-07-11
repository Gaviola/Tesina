"""P2.1 (plan julio-agosto) — Baseline de generación por PLANTILLA clínica.

Pipeline de costo cero para generar el reporte: clasificador -> dx -> plantilla con
morfología típica de la clase. Sin VLM generativo. Responde: ¿hace falta un VLM pesado,
o una plantilla trivial sobre el clasificador ya iguala su fidelidad diagnóstica?

Se evalúa con el MISMO NER (diagnostic consistency + clinical entity recall) que los VLM,
sobre las MISMAS imágenes (se reusa image_id/gt/grounded_dx de los reportes ya generados),
y se compara contra LLaVA-Med y Mini-VLM.

100% local, sin GPU. Uso:
    python scripts/generate_template_report.py
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

from src.evaluation.clinical_ner import (
    _compute_entity_recall,
    _extract_dict_entities,
    _normalize_label,
    diagnostic_consistency_flags,
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# Morfología típica por clase (canónica). Canned pero clase-específica; contiene términos
# dermatológicos que el recall detecta (pigmentation, border, color, telangiectasia, scaling...).
MORPHOLOGY = {
    "melanoma": "an asymmetric pigmented lesion with irregular borders, colour variegation and areas of regression",
    "nevus": "a symmetric, well-circumscribed pigmented lesion with a regular pigment network and uniform colour",
    "basal cell carcinoma": "a pearly papule with arborizing telangiectasia and possible ulceration",
    "actinic keratosis": "an erythematous scaly macule with surface keratosis on sun-damaged skin",
    "benign keratosis": "a well-demarcated verrucous plaque with a keratotic scaling surface and milia-like cysts",
    "dermatofibroma": "a firm pigmented papule with a central white area and a peripheral pigment network",
    "vascular lesion": "a well-demarcated red to purple lesion with vascular lacunes",
}


def _template_report(dx: str) -> str:
    canon = _normalize_label(dx)
    morph = MORPHOLOGY.get(canon, "typical dermatoscopic features")
    return (f"Diagnosis: the lesion is consistent with {dx}. On examination it shows {morph}. "
            f"This appearance supports the diagnosis of {dx}.")


def _load_reports(cond_dir: Path) -> list[dict]:
    out = []
    for jf in cond_dir.glob("*.json"):
        d = json.loads(jf.read_text(encoding="utf-8"))
        out.append({
            "image_id": d.get("image_id", jf.stem),
            "gt_label": d.get("gt_label", ""),
            "grounded_dx": d.get("grounded_dx", ""),
            "report": THINK_RE.sub("", d.get("report", "") or "").strip(),
        })
    return out


def _metrics(reports: list[str], gts: list[str]) -> tuple[float, float]:
    cons = float(np.mean(diagnostic_consistency_flags(reports, gts))) if reports else 0.0
    rec = float(np.mean([_compute_entity_recall(_extract_dict_entities(r)) for r in reports])) if reports else 0.0
    return cons, rec


def main():
    parser = argparse.ArgumentParser(description="P2.1 Baseline por plantilla clínica")
    parser.add_argument("--reports_root", type=str, default="outputs/generated_reports")
    parser.add_argument("--conditions", nargs="+", default=["full_swin", "full_oracle"])
    parser.add_argument("--vlm_models", nargs="+", default=["llava_med", "mini_vlm"])
    parser.add_argument("--dx_source_model", type=str, default="llava_med",
                        help="Modelo cuyos reportes se leen para obtener image_id/gt/grounded_dx.")
    parser.add_argument("--output", type=str, default="outputs/results/template/template_summary.json")
    args = parser.parse_args()

    root = Path(args.reports_root)
    summary = {}

    print(f"\n{'Condición':<14}{'Sistema':<16}{'Consistency':>12}{'Recall':>10}")
    for cond in args.conditions:
        src = root / args.dx_source_model / cond
        if not src.exists():
            logger.warning("SKIP %s: no existe %s", cond, src)
            continue
        data = _load_reports(src)
        gts = [d["gt_label"] for d in data]

        # Plantilla: reporte generado desde grounded_dx (dx del clasificador / gt en oracle).
        templates = [_template_report(d["grounded_dx"] or d["gt_label"]) for d in data]
        t_cons, t_rec = _metrics(templates, gts)
        summary.setdefault(cond, {})["template"] = {"consistency": t_cons, "recall": t_rec, "n": len(data)}
        print(f"{cond:<14}{'plantilla':<16}{t_cons:>12.3f}{t_rec:>10.3f}")

        # VLMs sobre las mismas imágenes.
        for m in args.vlm_models:
            mdir = root / m / cond
            if not mdir.exists():
                continue
            mdata = _load_reports(mdir)
            m_cons, m_rec = _metrics([d["report"] for d in mdata], [d["gt_label"] for d in mdata])
            summary[cond][m] = {"consistency": m_cons, "recall": m_rec, "n": len(mdata)}
            print(f"{'':<14}{m:<16}{m_cons:>12.3f}{m_rec:>10.3f}")
        print()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
