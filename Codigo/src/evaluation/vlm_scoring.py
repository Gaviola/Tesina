"""Clasificacion closed-world de VLMs via likelihood scoring.

Problema que resuelve
---------------------
Forzar a un VLM generativo a responder con una etiqueta discreta (e.g. "MEL")
mediante `generate(do_sample=False)` + regex parse produce un colapso a una
unica clase: el modelo converge a la respuesta mas probable a priori para
todo input. Este modulo evita el colapso reemplazando la generacion por
likelihood scoring: para cada imagen y cada una de las 7 clases de HAM10000
se calcula P(clase | imagen, prompt) via teacher-forcing y se elige el
argmax.

Caracteristicas
---------------
- Length normalization: divide log-prob por numero de tokens de la clase
  para evitar bias hacia clases con nombres cortos (e.g. "DF" vs
  "melanocytic nevus").
- Multi-sinonimo: cada clase se scorea con 3 sinonimos clinicos; la clase
  recibe el maximo log-prob entre sus sinonimos. Corrige variacion de
  tokenizacion y permite al modelo "elegir" la forma que mejor conoce.
- Ensemble de 4 prompts: 2 abiertos + 2 cerrados. El score final por clase
  es la media de log-probs length-normalized sobre los 4 prompts. Permite
  medir (i) accuracy por prompt individual, (ii) delta abierto-vs-cerrado,
  (iii) ensemble.

API principal
-------------
- CLASS_SYNONYMS: dict[str, list[str]]
- PROMPT_TEMPLATES: dict[str, str]
- score_image(vlm, vlm_name, image, class_codes, prompts, length_normalize)
  -> dict con logp_per_prompt_class, ensemble_score_per_class,
     pred_per_prompt, pred_ensemble, per_synonym_details.
"""
from __future__ import annotations

import logging
from typing import Optional

import torch
import torch.nn.functional as F

logger = logging.getLogger(__name__)


## Sinonimos clinicos por clase HAM10000. Tomados del diccionario usado en
## src/evaluation/clinical_ner.py y enriquecidos con formas alternativas
## comunes en reportes dermatoscopicos. Cada sinonimo se scorea por
## separado y el score de la clase es el maximo entre sinonimos.
CLASS_SYNONYMS: dict[str, list[str]] = {
    "MEL":   ["melanoma", "malignant melanoma", "MEL"],
    "NV":    ["melanocytic nevus", "nevus", "mole"],
    "BCC":   ["basal cell carcinoma", "basal cell", "BCC"],
    "AKIEC": ["actinic keratosis", "intraepithelial carcinoma", "AKIEC"],
    "BKL":   ["benign keratosis", "seborrheic keratosis", "solar lentigo"],
    "DF":    ["dermatofibroma", "fibrous histiocytoma", "DF"],
    "VASC":  ["vascular lesion", "angioma", "VASC"],
}


## Prompts scoreados como ensemble. O1/O2 son abiertos (sin mencionar
## clases), C1/C2 son cerrados (listan las 7 clases). El formato de C1/C2
## esta diseñado para que la completion esperada sea el nombre de la clase
## inmediatamente despues del prefijo.
PROMPT_TEMPLATES: dict[str, str] = {
    "O1": "What is the most likely diagnosis for this dermoscopic image?",
    "O2": "Identify the type of skin lesion shown in this image.",
    "C1": (
        "Given this dermoscopic image, the diagnosis among melanoma, "
        "melanocytic nevus, basal cell carcinoma, actinic keratosis, "
        "benign keratosis, dermatofibroma, or vascular lesion is"
    ),
    "C2": (
        "Select the correct diagnosis from: melanoma, melanocytic nevus, "
        "basal cell carcinoma, actinic keratosis, benign keratosis, "
        "dermatofibroma, vascular lesion. Answer:"
    ),
}


def _build_prefix(vlm_name: str, processor, prompt_text: str) -> str:
    """Construye el prefijo con chat template para cada familia de VLM.

    El prefijo termina justo antes de donde iria la respuesta del modelo,
    de modo que la completion (nombre de clase) se concatena directamente.
    """
    if vlm_name == "llava_med":
        # Template [INST] ... [/INST] con espacio trailing para que el
        # primer token de la completion no se pegue al "]".
        return f"[INST] <image>\n{prompt_text} [/INST] "
    if vlm_name == "mini_vlm":
        messages = [{"role": "user", "content": f"<|image_1|>\n{prompt_text}"}]
        return processor.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
    raise ValueError(f"VLM desconocido: {vlm_name}")


def _process_inputs(vlm_name: str, processor, image, full_text: str):
    """Aplica el processor multimodal correcto segun el modelo.

    LLaVA-Med: processor(images=, text=) - firma estandar HF.
    Mini-VLM:  processor(text, [image]) - firma custom de Phi-3.5-vision.
    """
    if vlm_name == "llava_med":
        return processor(images=image, text=full_text, return_tensors="pt")
    if vlm_name == "mini_vlm":
        return processor(full_text, [image], return_tensors="pt")
    raise ValueError(f"VLM desconocido: {vlm_name}")


@torch.no_grad()
def _score_completion(
    vlm_name: str,
    model,
    processor,
    image,
    prefix_text: str,
    completion_text: str,
) -> tuple[float, int]:
    """Calcula log P(completion | prefix, image) via teacher-forcing.

    Retorna (sum_log_probs, num_completion_tokens). La normalizacion por
    longitud la hace el caller para permitir agregaciones diferentes.

    Metodo:
      1. Tokeniza `completion_text` solo (sin special tokens) para saber
         cuantos tokens ocupa la completion exactamente.
      2. Procesa `prefix + completion` con el processor (expande tokens de
         imagen internamente).
      3. Forward pass sin labels; extrae logits.
      4. Suma log_softmax(logits[t-1])[input_ids[t]] para los ultimos
         `completion_len` tokens.
    """
    completion_ids = processor.tokenizer(
        completion_text, add_special_tokens=False, return_tensors="pt",
    )["input_ids"][0]
    completion_len = int(completion_ids.shape[0])
    if completion_len == 0:
        return float("-inf"), 0

    full_text = prefix_text + completion_text
    inputs = _process_inputs(vlm_name, processor, image, full_text).to(model.device)

    # use_cache=False: scoring teacher-forced hace un unico forward, no
    # necesita KV cache. Ademas evita el AttributeError de Phi-3.5-vision
    # cuando transformers moderno no expone to_legacy_cache().
    outputs = model(**inputs, use_cache=False)
    logits = outputs.logits  # (1, L, V)

    merged_ids = inputs["input_ids"][0]
    merged_len = int(merged_ids.shape[0])
    prefix_len = merged_len - completion_len
    if prefix_len < 1:
        # Caso patologico: prefix vacio tras tokenizar. Evita indexar fuera de rango.
        return float("-inf"), 0

    log_probs = F.log_softmax(logits[0].float(), dim=-1)  # (L, V) en float32
    # logits[t-1] predice input_ids[t]. Para los tokens de completion
    # ([prefix_len, merged_len)) usamos logits en [prefix_len-1, merged_len-1).
    target_log_probs = log_probs[prefix_len - 1:merged_len - 1]
    target_ids = merged_ids[prefix_len:merged_len]
    selected = target_log_probs.gather(1, target_ids.unsqueeze(1)).squeeze(1)
    return float(selected.sum().item()), completion_len


def score_class(
    vlm,
    vlm_name: str,
    image,
    prompt_text: str,
    class_code: str,
    length_normalize: bool = True,
    synonyms: Optional[dict[str, list[str]]] = None,
) -> tuple[float, dict]:
    """Score de una clase bajo un prompt. Agrega sinonimos por maximo.

    Returns:
        (best_score, per_synonym_dict).
        per_synonym_dict[synonym] = {"sum_logp", "num_tokens", "score"}.
    """
    synonyms = synonyms or CLASS_SYNONYMS
    prefix = _build_prefix(vlm_name, vlm.processor, prompt_text)

    per_syn = {}
    for syn in synonyms[class_code]:
        total, n_tok = _score_completion(
            vlm_name, vlm.model, vlm.processor, image, prefix, syn,
        )
        score = total / max(n_tok, 1) if length_normalize else total
        per_syn[syn] = {"sum_logp": total, "num_tokens": n_tok, "score": score}

    best = max(per_syn.values(), key=lambda d: d["score"])["score"]
    return best, per_syn


def score_image(
    vlm,
    vlm_name: str,
    image,
    class_codes: list[str],
    prompts: Optional[dict[str, str]] = None,
    length_normalize: bool = True,
    keep_synonym_details: bool = False,
) -> dict:
    """Score completo para una imagen: todas las clases x todos los prompts.

    Args:
        vlm: Instancia de LLaVAMed o MiniVLM (VLMBase) con load_components() ya llamado.
        vlm_name: "llava_med" o "mini_vlm".
        image: PIL.Image.
        class_codes: Lista ordenada de codigos de clase (e.g. HAM10000_CLASSES).
        prompts: Dict prompt_id -> texto. Default PROMPT_TEMPLATES.
        length_normalize: Si True, divide log-prob por numero de tokens.
        keep_synonym_details: Si True, incluye los log-probs por sinonimo en
            la salida (~21 floats x 4 prompts por imagen). Util para debug
            pero multiplica el tamano del JSON por ~3.

    Returns:
        dict con:
          - "prompts": {id: texto}
          - "class_codes": [...]
          - "logp_per_prompt_class": 2D list (num_prompts x num_classes),
            length-normalized si aplica.
          - "ensemble_score_per_class": list (num_classes), media sobre prompts.
          - "pred_per_prompt": list[str] (num_prompts), argmax por prompt.
          - "pred_ensemble": str, argmax del ensemble.
          - "per_synonym_details" (opcional): dict[prompt_id][class_code][syn] -> stats.
    """
    prompts = prompts or PROMPT_TEMPLATES
    prompt_keys = list(prompts.keys())
    num_prompts = len(prompt_keys)
    num_classes = len(class_codes)

    logp_matrix: list[list[float]] = []
    pred_per_prompt: list[str] = []
    per_syn_details: dict = {}

    for pk in prompt_keys:
        prompt_text = prompts[pk]
        row: list[float] = []
        per_syn_details[pk] = {}
        for cc in class_codes:
            best, per_syn = score_class(
                vlm, vlm_name, image, prompt_text, cc, length_normalize,
            )
            row.append(best)
            if keep_synonym_details:
                per_syn_details[pk][cc] = per_syn
        logp_matrix.append(row)
        pred_idx = max(range(num_classes), key=lambda i: row[i])
        pred_per_prompt.append(class_codes[pred_idx])

    ensemble_score = [
        sum(logp_matrix[p][c] for p in range(num_prompts)) / num_prompts
        for c in range(num_classes)
    ]
    pred_ensemble_idx = max(range(num_classes), key=lambda i: ensemble_score[i])

    result = {
        "prompts": prompts,
        "class_codes": class_codes,
        "logp_per_prompt_class": logp_matrix,
        "ensemble_score_per_class": ensemble_score,
        "pred_per_prompt": pred_per_prompt,
        "pred_ensemble": class_codes[pred_ensemble_idx],
    }
    if keep_synonym_details:
        result["per_synonym_details"] = per_syn_details
    return result
