"""Clinical Entity Matching para Fase 2, Nivel 2.

Pipeline dual NER con SciSpaCy para evaluar reportes generados sin referencia:
1. en_ner_bionlp13cg_md: entidades anatómicas/patológicas
2. en_core_sci_md: fallback biomédico general
3. Diccionario custom dermatológico (siempre activo)
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Criterios ABCDE y términos dermatológicos para diccionario custom
DERMATOLOGY_TERMS = {
    "abcde": ["asymmetry", "border", "color", "diameter", "evolution"],
    "lesion_types": [
        "melanoma", "nevus", "basal cell carcinoma", "actinic keratosis",
        "benign keratosis", "dermatofibroma", "vascular lesion",
        "papule", "nodule", "macule", "plaque", "patch",
    ],
    "clinical_features": [
        "pigmentation", "ulceration", "scaling", "erythema",
        "telangiectasia", "regression", "dermoscopic",
    ],
}

# Sinónimos para consistency check de diagnósticos.
# Incluye tanto etiquetas HAM10000 (clases cortas) como nombres de carpeta de
# SkinCoT (ej. "Melanoma") y SkinCaRe (ej. "Eczema Photos", "Psoriasis Images").
# La función _normalize_label() convierte folder-names a clave canónica antes
# de buscar en este dict.
_DIAGNOSIS_SYNONYMS = {
    "melanoma": ["melanoma", "mel"],
    "nevus": ["nevus", "nv", "mole", "benign nevus", "melanocytic nevus", "melanocytic nevi"],
    "basal cell carcinoma": ["basal cell carcinoma", "bcc", "basalioma"],
    "actinic keratosis": ["actinic keratosis", "akiec", "solar keratosis", "actinic keratoses"],
    "benign keratosis": ["benign keratosis", "bkl", "seborrheic keratosis", "seborrhoeic keratosis",
                         "keratosis", "seborrheic keratoses"],
    "dermatofibroma": ["dermatofibroma", "df"],
    "vascular lesion": ["vascular lesion", "vasc", "hemangioma", "angioma", "vascular"],
    # SkinCaRe / SkinCoT folder-name labels (normalized)
    "eczema": ["eczema", "atopic dermatitis", "dermatitis"],
    "psoriasis": ["psoriasis"],
    "tinea ringworm candidiasis": ["tinea", "ringworm", "candidiasis", "fungal infection",
                                   "dermatophytosis"],
    "chickenpox": ["chickenpox", "varicella"],
    "nail fungus": ["nail fungus", "onychomycosis"],
    "warts molluscum": ["warts", "molluscum", "verruca", "papillomavirus"],
    "seborrheic keratoses": ["seborrheic keratosis", "seborrhoeic keratosis", "keratosis",
                             "bkl", "benign keratosis"],
    "acne": ["acne", "comedone", "papule", "pustule"],
    "rosacea": ["rosacea"],
    "contact dermatitis": ["contact dermatitis", "allergic dermatitis", "dermatitis"],
    "alopecia areata": ["alopecia", "hair loss"],
    "urticaria hives": ["urticaria", "hives", "wheals"],
    "squamous cell carcinoma": ["squamous cell carcinoma", "scc"],
    "light diseases": ["photosensitivity", "light eruption", "porphyria"],
    "lupus": ["lupus", "systemic lupus", "discoid lupus"],
    "cellulitis impetigo": ["cellulitis", "impetigo", "bacterial"],
}

# Mapeo de folder-names de SkinCaRe a clave canónica del dict.
# Necesario porque gt_label viene del nombre de carpeta del dataset.
_FOLDER_TO_CANONICAL = {
    "eczema photos": "eczema",
    "psoriasis pictures lichen planus and related diseases": "psoriasis",
    "tinea ringworm candidiasis and other fungal infections": "tinea ringworm candidiasis",
    "chicken pox": "chickenpox",
    "nail fungus": "nail fungus",
    "warts molluscum and other viral infections": "warts molluscum",
    "seborrheic keratoses and other benign tumors": "seborrheic keratoses",
    "acne and rosacea photos": "acne",
    "acne": "acne",
    "rosacea": "rosacea",
    "atopic dermatitis photos": "eczema",
    "exanthems and drug eruptions": "contact dermatitis",
    "hair loss photos alopecia and other hair diseases": "alopecia areata",
    "urticaria hives": "urticaria hives",
    "light diseases and disorders of pigmentation": "light diseases",
    "lupus and other connective tissue diseases": "lupus",
    "cellulitis impetigo and other bacterial infections": "cellulitis impetigo",
    "systemic disease": "lupus",
    "scabies lyme disease and other infestations and bites": "contact dermatitis",
    "vascular tumors": "vascular lesion",
    # HAM10000 folder names (SkinCoT uses HAM class names directly)
    "melanoma": "melanoma",
    "melanocytic nevi": "nevus",
    "basal cell carcinoma": "basal cell carcinoma",
    "actinic keratosis": "actinic keratosis",
    "benign keratosis-like lesions": "benign keratosis",
    "dermatofibroma": "dermatofibroma",
    "vascular lesions": "vascular lesion",
}


def _normalize_label(label: str) -> str:
    """Normaliza un gt_label (posiblemente folder-name) a clave canónica del dict."""
    key = label.lower().strip()
    return _FOLDER_TO_CANONICAL.get(key, key)


# ---------------------------------------------------------------------------
# Carga de pipeline NER
# ---------------------------------------------------------------------------

def _load_spacy_pipeline():
    """Intenta cargar en orden: bionlp13cg → core_sci → None."""
    for model_name in ("en_ner_bionlp13cg_md", "en_core_sci_md"):
        try:
            import spacy
            nlp = spacy.load(model_name)
            logger.info("Pipeline SciSpaCy cargado: %s", model_name)
            return nlp, model_name.split("_")[2]  # "bionlp" o "scimed"
        except Exception:
            continue
    logger.warning(
        "SciSpaCy no disponible. Usando solo diccionario dermatológico. "
        "Instalar con: pip install scispacy && pip install <scispacy_model_url>"
    )
    return None, "none"


# ---------------------------------------------------------------------------
# Extracción de entidades
# ---------------------------------------------------------------------------

def _extract_dict_entities(text: str) -> list[dict]:
    """Extrae entidades del diccionario dermatológico con regex."""
    text_lower = text.lower()
    entities = []
    seen_spans = set()

    for category, terms in DERMATOLOGY_TERMS.items():
        for term in terms:
            pattern = r"\b" + re.escape(term) + r"\b"
            for match in re.finditer(pattern, text_lower):
                span = (match.start(), match.end())
                if span not in seen_spans:
                    seen_spans.add(span)
                    entities.append({
                        "text": term,
                        "label": category,
                        "start": match.start(),
                        "end": match.end(),
                        "source": "dictionary",
                    })
    return entities


def _extract_spacy_entities(text: str, nlp) -> list[dict]:
    """Extrae entidades médicas con SciSpaCy."""
    try:
        doc = nlp(text)
        return [
            {
                "text": ent.text.lower(),
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy",
            }
            for ent in doc.ents
        ]
    except Exception as e:
        logger.warning("SciSpaCy falló en extracción: %s", e)
        return []


def _extract_entities(text: str, nlp) -> list[dict]:
    """Combina entidades SciSpaCy + diccionario, deduplicando por span."""
    dict_entities = _extract_dict_entities(text)
    spacy_entities = _extract_spacy_entities(text, nlp) if nlp is not None else []

    # Deduplicar: si un span ya está cubierto por diccionario, descartar SciSpaCy
    dict_spans = {(e["start"], e["end"]) for e in dict_entities}
    unique_spacy = [e for e in spacy_entities if (e["start"], e["end"]) not in dict_spans]

    return dict_entities + unique_spacy


# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

def _compute_entity_recall(entities: list[dict]) -> float:
    """Fracción de categorías de DERMATOLOGY_TERMS cubiertas en el reporte."""
    covered = set()
    for ent in entities:
        if ent["source"] == "dictionary":
            covered.add(ent["label"])
    return len(covered) / max(len(DERMATOLOGY_TERMS), 1)


def _compute_diagnostic_consistency(
    reports: list[str],
    gt_labels: list[str],
) -> float:
    """Fracción de reportes donde el diagnóstico GT (o sinónimo) está mencionado."""
    if len(reports) != len(gt_labels):
        raise ValueError(
            f"reports ({len(reports)}) y gt_labels ({len(gt_labels)}) "
            "deben tener el mismo tamaño."
        )

    matches = 0
    for report, label in zip(reports, gt_labels):
        report_lower = report.lower()
        canonical = _normalize_label(label) if label else ""
        synonyms = _DIAGNOSIS_SYNONYMS.get(canonical, [canonical])
        if any(syn in report_lower for syn in synonyms if syn):
            matches += 1

    return matches / max(len(reports), 1)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def evaluate_clinical_entities(
    generated_reports: list[str],
    ground_truth_labels: Optional[list[str]] = None,
) -> dict:
    """Evalúa reportes generados usando NER clínico (sin referencia textual).

    Métricas calculadas:
    - clinical_entity_recall: fracción de categorías de DERMATOLOGY_TERMS presentes.
    - diagnostic_consistency: alineación con etiquetas de diagnóstico (si se proveen).

    Args:
        generated_reports: Reportes generados por el VLM.
        ground_truth_labels: Etiquetas de diagnóstico (p.ej. "melanoma", "nevus").
            Si se pasa, se calcula diagnostic_consistency.

    Returns:
        Dict con clinical_entity_recall, backend, per_report y opcionalmente
        diagnostic_consistency.

    Raises:
        ValueError: Si ground_truth_labels se pasa con distinto tamaño que generated_reports.
    """
    if not generated_reports:
        return {
            "clinical_entity_recall": 0.0,
            "backend": "none",
            "per_report": [],
        }

    if ground_truth_labels is not None and len(ground_truth_labels) != len(generated_reports):
        raise ValueError(
            f"ground_truth_labels ({len(ground_truth_labels)}) y generated_reports "
            f"({len(generated_reports)}) deben tener el mismo tamaño."
        )

    nlp, backend = _load_spacy_pipeline()

    per_report = []
    for report in generated_reports:
        if not report or not report.strip():
            per_report.append({"entities": [], "recall": 0.0})
            continue
        entities = _extract_entities(report, nlp)
        recall = _compute_entity_recall(entities)
        per_report.append({"entities": entities, "recall": recall})

    mean_recall = sum(r["recall"] for r in per_report) / max(len(per_report), 1)

    output = {
        "clinical_entity_recall": mean_recall,
        "backend": backend,
        "per_report": per_report,
    }

    if ground_truth_labels is not None:
        consistency = _compute_diagnostic_consistency(generated_reports, ground_truth_labels)
        output["diagnostic_consistency"] = consistency
        logger.info(
            "Clinical Entity Recall: %.4f | Diagnostic Consistency: %.4f",
            mean_recall, consistency,
        )
    else:
        logger.info("Clinical Entity Recall: %.4f", mean_recall)

    return output
