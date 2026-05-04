"""Fase 1: Clasificacion con VLMs sobre HAM10000.

Tres metodos soportados via --method:
  - generate   (default): prompt de clasificacion -> generate autoregresivo
                -> regex parse. Metodo original, propenso a colapso de clase.
  - likelihood: scoring teacher-forced de P(clase | imagen, prompt) por cada
                clase y prompt. Ensemble de 4 prompts (2 abiertos + 2 cerrados),
                3 sinonimos por clase agregados por max, length-normalized.
                Evita el colapso de clase por construccion.
  - cot:        Chain-of-Thought estructurado: el modelo razona sobre features
                ABCDE, lista diferenciales y concluye con "Final diagnosis: [CLASS]".
                Usa generate autoregresivo con COT_PROMPT y parser dedicado que
                extrae la etiqueta del campo "Final diagnosis:".

Uso:
    python scripts/train_vlm_classify.py --model llava_med --method generate
    python scripts/train_vlm_classify.py --model mini_vlm --method likelihood
    python scripts/train_vlm_classify.py --model llava_med --method cot
    python scripts/train_vlm_classify.py --model llava_med --method likelihood \\
        --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.collators import VLMCollator
from src.data.ham10000 import HAM10000_CLASSES, HAM10000_LABEL_MAP, HAM10000Dataset
from src.evaluation.vlm_scoring import CLASS_SYNONYMS, COT_PROMPT, PROMPT_TEMPLATES, score_image
from src.models.factory import build_model
from src.training.lora_config import apply_lora, get_lora_config
from src.utils.device import check_vram, get_device, get_training_dtype, get_vram_gb
from src.utils.io import load_checkpoint, save_results
from src.utils.logging import format_duration, log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = (
    "Classify this dermoscopic image into one of the following categories: "
    "MEL, NV, BCC, AKIEC, BKL, DF, VASC. "
    "Respond with only the category label."
)

# Set de labels válidos en mayúsculas para parsing robusto
_VALID_LABELS = {name.upper() for name in HAM10000_CLASSES}


def parse_vlm_response(response: str) -> str:
    """Extrae la etiqueta de clasificación de la respuesta del VLM.

    Busca una de las 7 categorías válidas en la respuesta. Si no encuentra
    ninguna, retorna "UNKNOWN".
    """
    text = response.strip().upper()

    # Intento 1: respuesta exacta
    if text in _VALID_LABELS:
        return text

    # Intento 2: buscar la primera aparición de un label válido
    for label in HAM10000_CLASSES:
        if re.search(rf'\b{label}\b', text):
            return label

    return "UNKNOWN"


def parse_cot_response(response: str) -> str:
    """Extrae la etiqueta del campo 'Final diagnosis:' en respuestas CoT.

    Busca la linea con 'Final diagnosis:' y extrae el codigo de clase.
    Si el campo no existe o no contiene un label valido, cae en
    parse_vlm_response() como fallback para capturar cualquier mencion.
    """
    # Buscar "Final diagnosis: <LABEL>" (case-insensitive, con variantes de formato)
    match = re.search(
        r'Final\s+diagnosis\s*:\s*\[?([A-Za-z /]+)\]?',
        response, re.IGNORECASE,
    )
    if match:
        candidate = match.group(1).strip().upper()
        # Verificar match exacto primero
        if candidate in _VALID_LABELS:
            return candidate
        # Buscar label valido dentro del candidato (e.g. "MEL (melanoma)")
        for label in HAM10000_CLASSES:
            if re.search(rf'\b{label}\b', candidate):
                return label

    # Fallback: buscar en toda la respuesta
    return parse_vlm_response(response)


def run_likelihood_eval(args, model, test_dataset, is_finetuned, script_start):
    """Evalua clasificacion via likelihood scoring en lugar de generate.

    Itera por imagen (score_image trabaja 1 imagen a la vez) y computa
    log P(clase | imagen, prompt) para cada prompt del ensemble y cada
    clase. El argmax sobre las 7 clases nunca es UNKNOWN por construccion.

    Guarda:
      - {model}_likelihood[_finetuned]_predictions.json: matriz completa
        de log-probs, predicciones por prompt, prediccion ensemble.
      - {model}_likelihood[_finetuned]_test_results.json: metricas
        (accuracy ensemble + por-prompt, F1, sens/spec).
    """
    from src.evaluation.classification import evaluate_classification

    prompts = PROMPT_TEMPLATES
    prompt_keys = list(prompts.keys())
    num_prompts = len(prompt_keys)
    num_classes = len(HAM10000_CLASSES)

    total_images = len(test_dataset)
    limit = args.dry_run_batches if args.dry_run else total_images

    if args.dry_run:
        logger.info("=== MODO DRY-RUN (likelihood): procesando %d imagenes ===", limit)
    logger.info(
        "Likelihood scoring: %d imagenes x %d prompts x %d clases x sinonimos",
        limit, num_prompts, num_classes,
    )
    logger.info("Prompts ensemble: %s", prompt_keys)

    inference_start = time.perf_counter()

    all_y_true: list[int] = []
    all_y_pred: list[int] = []                       # ensemble argmax
    all_y_pred_per_prompt: list[list[int]] = []      # shape: (N, num_prompts)
    all_logp_matrix: list[list[list[float]]] = []    # shape: (N, num_prompts, num_classes)
    all_image_ids: list[str] = []

    per_syn_dump: list = [] if args.keep_synonym_details else None

    for idx in range(limit):
        sample = test_dataset[idx]
        image = sample["image"]
        label = int(sample["label"])
        image_id = sample.get("image_id", "")

        scored = score_image(
            vlm=model,
            vlm_name=args.model,
            image=image,
            class_codes=HAM10000_CLASSES,
            prompts=prompts,
            length_normalize=True,
            keep_synonym_details=args.keep_synonym_details,
        )

        all_y_true.append(label)
        all_y_pred.append(HAM10000_LABEL_MAP[scored["pred_ensemble"]])
        all_y_pred_per_prompt.append(
            [HAM10000_LABEL_MAP[p] for p in scored["pred_per_prompt"]]
        )
        all_logp_matrix.append(scored["logp_per_prompt_class"])
        all_image_ids.append(image_id)

        if args.keep_synonym_details:
            per_syn_dump.append(scored["per_synonym_details"])

        if (idx + 1) % 25 == 0 or (idx + 1) == limit:
            elapsed = time.perf_counter() - inference_start
            images_per_sec = (idx + 1) / max(elapsed, 0.001)
            remaining = limit - (idx + 1)
            eta = elapsed / max(idx + 1, 1) * remaining
            logger.info(
                "Progreso: %d/%d imagenes [%.2f img/s, ETA: %s]",
                idx + 1, limit, images_per_sec, format_duration(eta),
            )

    inference_time = time.perf_counter() - inference_start
    logger.info("Likelihood scoring completado en %s", format_duration(inference_time))

    # --- Resumen dry-run ---
    if args.dry_run:
        if torch.cuda.is_available():
            peak_mb = torch.cuda.max_memory_allocated() / (1024**2)
            total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
            headroom_mb = total_vram_mb - peak_mb
        else:
            peak_mb = total_vram_mb = headroom_mb = 0

        images_done = len(all_y_true)
        images_per_sec = images_done / max(inference_time, 0.001)
        est_total_secs = inference_time / max(images_done, 1) * total_images

        # Distribucion de predicciones ensemble
        pred_counts = {cls: 0 for cls in HAM10000_CLASSES}
        for p in all_y_pred:
            pred_counts[HAM10000_CLASSES[p]] += 1
        dominant_cls = max(pred_counts, key=pred_counts.get)
        dominant_pct = 100 * pred_counts[dominant_cls] / max(images_done, 1)

        sample_n = min(5, len(all_y_true))
        sample_lines = []
        for i in range(sample_n):
            true_label = HAM10000_CLASSES[all_y_true[i]]
            pred_ens = HAM10000_CLASSES[all_y_pred[i]]
            per_prompt = [HAM10000_CLASSES[p] for p in all_y_pred_per_prompt[i]]
            sample_lines.append(
                f"    [{i}] true={true_label} pred_ensemble={pred_ens} "
                f"per_prompt={dict(zip(prompt_keys, per_prompt))}"
            )

        status = "OK"
        warnings = []
        if dominant_pct > 80:
            warnings.append(
                f"prediccion dominante {dominant_cls} = {dominant_pct:.0f}% "
                f"(posible colapso aun con likelihood)"
            )
        if 0 < headroom_mb < 500:
            warnings.append(f"headroom VRAM bajo ({headroom_mb:.0f} MB)")
        if warnings:
            status = "ADVERTENCIA - " + "; ".join(warnings)

        logger.info(
            "\n=== RESUMEN DRY-RUN (likelihood %s) ===\n"
            "  VRAM pico           : %.0f MB / %.0f MB\n"
            "  VRAM headroom       : %.0f MB\n"
            "  Imagenes procesadas : %d / %d\n"
            "  Velocidad           : %.2f img/s\n"
            "  Distribucion preds  : %s\n"
            "  Est. tiempo total   : %s (%d imagenes)\n"
            "  Primeras muestras   :\n%s\n"
            "  Estado              : %s",
            args.model,
            peak_mb, total_vram_mb,
            headroom_mb,
            images_done, total_images,
            images_per_sec,
            pred_counts,
            format_duration(est_total_secs), total_images,
            "\n".join(sample_lines),
            status,
        )
        logger.info("Ejecucion total: %s", format_duration(time.perf_counter() - script_start))
        sys.exit(0)

    # --- Guardar resultados ---
    results_dir = Path(args.output_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_likelihood_finetuned" if is_finetuned else "_likelihood"

    predictions = {
        "model": args.model,
        "finetuned": is_finetuned,
        "method": "likelihood",
        "length_normalized": True,
        "prompts": prompts,
        "class_names": HAM10000_CLASSES,
        "class_synonyms": CLASS_SYNONYMS,
        "image_ids": all_image_ids,
        "y_true": all_y_true,
        "y_pred": all_y_pred,
        "y_pred_per_prompt": all_y_pred_per_prompt,
        "logp_matrix": all_logp_matrix,
        "unknown_count": 0,
    }
    if args.keep_synonym_details:
        predictions["per_synonym_details"] = per_syn_dump
    pred_path = results_dir / f"{args.model}{suffix}_predictions.json"
    save_results(predictions, str(pred_path))
    logger.info("Predicciones likelihood guardadas en %s", pred_path)

    # --- Metricas ---
    total = len(all_y_true)
    ensemble_results = evaluate_classification(
        all_y_true, all_y_pred, class_names=HAM10000_CLASSES,
    )

    mode_label = f"{args.model} (likelihood, fine-tuned)" if is_finetuned else f"{args.model} (likelihood)"
    logger.info("=== Resultados %s ===", mode_label)
    logger.info("Accuracy (ensemble)     : %.4f", ensemble_results["accuracy"])
    logger.info("F1 weighted (ensemble)  : %.4f", ensemble_results["f1_weighted"])
    logger.info("Sens. macro (ensemble)  : %.4f", ensemble_results["sensitivity_macro"])
    logger.info("Spec. macro (ensemble)  : %.4f", ensemble_results["specificity_macro"])

    # Accuracy por prompt individual
    per_prompt_accuracy = {}
    for pi, pk in enumerate(prompt_keys):
        y_pred_p = [row[pi] for row in all_y_pred_per_prompt]
        correct = sum(1 for yt, yp in zip(all_y_true, y_pred_p) if yt == yp)
        per_prompt_accuracy[pk] = correct / max(total, 1)
        logger.info("Accuracy prompt %s      : %.4f", pk, per_prompt_accuracy[pk])

    metrics_path = results_dir / f"{args.model}{suffix}_test_results.json"
    save_results(
        {
            "model": args.model,
            "finetuned": is_finetuned,
            "method": "likelihood",
            "prompts": prompts,
            "accuracy": ensemble_results["accuracy"],
            "f1_weighted": ensemble_results["f1_weighted"],
            "auc_roc_macro": ensemble_results["auc_roc_macro"],
            "sensitivity_macro": ensemble_results["sensitivity_macro"],
            "specificity_macro": ensemble_results["specificity_macro"],
            "sensitivity_per_class": ensemble_results.get("sensitivity_per_class", []),
            "specificity_per_class": ensemble_results.get("specificity_per_class", []),
            "confusion_matrix": ensemble_results["confusion_matrix"],
            "per_prompt_accuracy": per_prompt_accuracy,
            "unknown_count": 0,
            "total_samples": total,
            "valid_samples": total,
        },
        str(metrics_path),
    )
    logger.info("Metricas guardadas en %s", metrics_path)
    logger.info("Ejecucion total: %s", format_duration(time.perf_counter() - script_start))


def run_cot_eval(args, model, test_loader, test_dataset, is_finetuned, script_start):
    """Evalua clasificacion via Chain-of-Thought estructurado.

    Usa COT_PROMPT para forzar al VLM a razonar sobre features dermoscopicas
    (asimetria, bordes, colores, estructuras) antes de emitir un diagnostico.
    El parser extrae la etiqueta del campo "Final diagnosis:" y cae en
    parse_vlm_response() como fallback si el campo no existe.

    Guarda:
      - {model}_cot[_finetuned]_predictions.json: respuestas crudas + parseo.
      - {model}_cot[_finetuned]_test_results.json: accuracy, F1, sens/spec.
    """
    from src.evaluation.classification import evaluate_classification

    total_images = len(test_dataset)
    limit_batches = args.dry_run_batches if args.dry_run else None

    # CoT genera respuestas largas: necesita mas tokens que generate clasico
    max_new_tokens = max(args.max_new_tokens, 200)

    if args.dry_run:
        logger.info("=== MODO DRY-RUN (cot): procesando %d batches ===", args.dry_run_batches)
    logger.info("CoT scoring: %d imagenes, max_new_tokens=%d", total_images, max_new_tokens)
    logger.info("COT_PROMPT: %s", COT_PROMPT[:120] + "...")

    all_image_ids: list[str] = []
    all_y_true: list[int] = []
    all_y_pred: list[int] = []
    all_responses: list[str] = []
    unknown_count = 0

    inference_start = time.perf_counter()
    with torch.no_grad():
        for batch_idx, batch in enumerate(test_loader):
            images = batch["image"]
            labels = batch["label"].tolist()
            metadata = batch.get("metadata", [{}] * len(labels))
            bs = len(images)

            prompts = [COT_PROMPT] * bs
            responses = model.generate(images, prompts, max_new_tokens=max_new_tokens)

            for i, response in enumerate(responses):
                parsed = parse_cot_response(response)
                pred_idx = HAM10000_LABEL_MAP.get(parsed, -1)
                if parsed == "UNKNOWN":
                    unknown_count += 1

                image_id = metadata[i].get("dx", "") if isinstance(metadata[i], dict) else ""
                all_image_ids.append(image_id)
                all_y_true.append(labels[i])
                all_y_pred.append(pred_idx)
                all_responses.append(response.strip())

            if (batch_idx + 1) % 10 == 0:
                elapsed = time.perf_counter() - inference_start
                images_done = (batch_idx + 1) * bs
                images_per_sec = images_done / max(elapsed, 0.001)
                remaining = len(test_loader) - (batch_idx + 1)
                eta = elapsed / (batch_idx + 1) * remaining
                logger.info(
                    "Progreso: %d/%d batches (unknown: %d) [%.1f img/s, ETA: %s]",
                    batch_idx + 1, len(test_loader), unknown_count,
                    images_per_sec, format_duration(eta),
                )

            if args.dry_run and (batch_idx + 1) >= args.dry_run_batches:
                logger.info("Dry-run: %d batches procesados, finalizando.", args.dry_run_batches)
                break

    inference_time = time.perf_counter() - inference_start
    logger.info("CoT inferencia completada en %s", format_duration(inference_time))

    if args.dry_run:
        images_done = len(all_y_true)
        images_per_sec = images_done / max(inference_time, 0.001)

        if torch.cuda.is_available():
            peak_mb = torch.cuda.max_memory_allocated() / (1024**2)
            total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
            headroom_mb = total_vram_mb - peak_mb
        else:
            peak_mb = total_vram_mb = headroom_mb = 0

        sample_n = min(5, len(all_responses))
        sample_lines = []
        for i in range(sample_n):
            parsed = parse_cot_response(all_responses[i])
            true_label = HAM10000_CLASSES[all_y_true[i]] if all_y_true[i] < len(HAM10000_CLASSES) else "?"
            # Mostrar las primeras 120 chars para ver si el formato CoT se genera bien
            sample_lines.append(
                f"    [{i}] true={true_label} parsed={parsed} raw={all_responses[i][:120]!r}"
            )

        total_batches = len(test_loader)
        est_total_secs = inference_time / max(args.dry_run_batches, 1) * total_batches
        unknown_pct = 100 * unknown_count / max(images_done, 1)

        warnings = []
        if unknown_pct > 50:
            warnings.append(f">50% sin 'Final diagnosis:' ({unknown_pct:.0f}%) — revisar formato CoT")
        if 0 < headroom_mb < 500:
            warnings.append(f"headroom VRAM bajo ({headroom_mb:.0f} MB)")
        status = "ADVERTENCIA — " + "; ".join(warnings) if warnings else "OK"

        logger.info(
            "\n=== RESUMEN DRY-RUN (CoT %s) ===\n"
            "  VRAM pico          : %.0f MB / %.0f MB\n"
            "  VRAM headroom      : %.0f MB\n"
            "  Imagenes procesadas: %d / %d\n"
            "  Velocidad          : %.2f img/s\n"
            "  UNKNOWN            : %d (%.1f%%)\n"
            "  Est. tiempo total  : %s (%d batches)\n"
            "  Primeras respuestas:\n%s\n"
            "  Estado             : %s",
            args.model,
            peak_mb, total_vram_mb,
            headroom_mb,
            images_done, total_images,
            images_per_sec,
            unknown_count, unknown_pct,
            format_duration(est_total_secs), total_batches,
            "\n".join(sample_lines),
            status,
        )
        logger.info("Ejecucion total: %s", format_duration(time.perf_counter() - script_start))
        sys.exit(0)

    # --- Guardar resultados ---
    total = len(all_y_true)
    logger.info(
        "CoT completado: %d imagenes, %d UNKNOWN (%.1f%%)",
        total, unknown_count, 100 * unknown_count / max(total, 1),
    )

    results_dir = Path(args.output_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_cot_finetuned" if is_finetuned else "_cot"

    predictions = {
        "model": args.model,
        "finetuned": is_finetuned,
        "method": "cot",
        "cot_prompt": COT_PROMPT,
        "class_names": HAM10000_CLASSES,
        "image_ids": all_image_ids,
        "y_true": all_y_true,
        "y_pred": all_y_pred,
        "responses": all_responses,
        "unknown_count": unknown_count,
    }
    pred_path = results_dir / f"{args.model}{suffix}_predictions.json"
    save_results(predictions, str(pred_path))
    logger.info("Predicciones CoT guardadas en %s", pred_path)

    # --- Metricas ---
    valid_indices = [i for i, p in enumerate(all_y_pred) if p >= 0]
    if valid_indices:
        y_true_valid = [all_y_true[i] for i in valid_indices]
        y_pred_valid = [all_y_pred[i] for i in valid_indices]
        results = evaluate_classification(y_true_valid, y_pred_valid, class_names=HAM10000_CLASSES)

        mode_label = f"{args.model} (CoT, fine-tuned)" if is_finetuned else f"{args.model} (CoT)"
        logger.info("=== Resultados %s (excluyendo %d UNKNOWN) ===", mode_label, unknown_count)
        logger.info("Accuracy      : %.4f", results["accuracy"])
        logger.info("F1 weighted   : %.4f", results["f1_weighted"])
        logger.info("Sens. macro   : %.4f", results["sensitivity_macro"])
        logger.info("Spec. macro   : %.4f", results["specificity_macro"])

        metrics_path = results_dir / f"{args.model}{suffix}_test_results.json"
        save_results(
            {
                "model": args.model,
                "finetuned": is_finetuned,
                "method": "cot",
                "accuracy": results["accuracy"],
                "f1_weighted": results["f1_weighted"],
                "auc_roc_macro": results["auc_roc_macro"],
                "sensitivity_macro": results["sensitivity_macro"],
                "specificity_macro": results["specificity_macro"],
                "sensitivity_per_class": results.get("sensitivity_per_class", []),
                "specificity_per_class": results.get("specificity_per_class", []),
                "confusion_matrix": results["confusion_matrix"],
                "unknown_count": unknown_count,
                "total_samples": total,
                "valid_samples": len(valid_indices),
            },
            str(metrics_path),
        )
        logger.info("Metricas CoT guardadas en %s", metrics_path)
    else:
        logger.warning("Todas las respuestas CoT fueron UNKNOWN. No se pueden calcular metricas.")

    logger.info("Ejecucion total: %s", format_duration(time.perf_counter() - script_start))


def main():
    parser = argparse.ArgumentParser(description="F1: Clasificacion con VLMs (generate, likelihood o cot)")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--method", type=str, default="generate",
                        choices=["generate", "likelihood", "cot"],
                        help="generate: prompt + autoregresivo + regex parse. "
                             "likelihood: teacher-forced scoring P(clase|imagen,prompt) "
                             "con ensemble de 4 prompts, sinonimos y length-normalization. "
                             "cot: Chain-of-Thought estructurado con formato Features/"
                             "Differential/Final diagnosis; parser extrae la etiqueta "
                             "del campo 'Final diagnosis:'.")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--splits_file", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_new_tokens", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--quantize", action="store_true", help="Forzar cuantización 4-bit del LLM")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Verificación: procesa N batches, reporta VRAM, velocidad y respuestas parseadas.")
    parser.add_argument("--dry-run-batches", type=int, default=10, dest="dry_run_batches",
                        help="Número de batches a procesar en modo dry-run (default: 10).")
    parser.add_argument("--checkpoint", type=str, default=None,
                        help="Ruta al checkpoint fine-tuneado (best_model.pt). "
                             "Carga LoRA config del mismo directorio y restaura pesos.")
    parser.add_argument("--keep_synonym_details", action="store_true",
                        help="(likelihood) Guardar log-probs por sinonimo en el JSON. "
                             "Util para debug, triplica el tamano del archivo.")
    args = parser.parse_args()

    if args.dry_run:
        args.wandb = False

    script_start = time.perf_counter()

    # 1. Reproducibilidad
    set_seed(args.seed)

    # 2. Logger
    log_dir = str(Path(args.output_dir) / "logs")
    run_name = f"vlm_classify_{args.model}"
    setup_logger(
        name=run_name,
        log_dir=log_dir,
        use_wandb=args.wandb,
        wandb_project="dermvlm",
        wandb_config=vars(args),
    )
    mode_str = "fine-tuned" if args.checkpoint else "zero-shot"
    logger.info("Iniciando clasificación %s con %s", mode_str, args.model)

    # 3. Device
    device = get_device()
    dtype = get_training_dtype()
    logger.info("Dispositivo: %s | dtype: %s", device, dtype)

    # 4. Verificar VRAM y decidir cuantización
    vram_requirements = {"llava_med": 14.0, "mini_vlm": 10.0}
    required_gb = vram_requirements[args.model]
    use_quantize = args.quantize

    if not use_quantize and not check_vram(required_gb, args.model):
        vram = get_vram_gb()
        if vram > 0:
            logger.info("Activando cuantización 4-bit automáticamente para %s", args.model)
            use_quantize = True
        else:
            logger.error("No se detectó GPU. No se puede ejecutar inferencia VLM")
            sys.exit(1)

    if use_quantize:
        logger.info("Cuantización 4-bit habilitada para el LLM")

    # 5. Cargar modelo VLM
    # Ambos modelos usan device_map="auto" — no se requiere .to(device) manual
    is_finetuned = args.checkpoint is not None
    with log_time("Cargando modelo %s%s" % (args.model, " (4-bit)" if use_quantize else ""), logger):
        model = build_model({"name": args.model, "quantize": use_quantize})
        model.load_components()

        if is_finetuned:
            ckpt_dir = Path(args.checkpoint).parent
            lora_cfg_path = ckpt_dir / "lora_config.json"
            if not lora_cfg_path.exists():
                logger.error("lora_config.json no encontrado en %s", ckpt_dir)
                sys.exit(1)
            with open(lora_cfg_path, encoding="utf-8") as f:
                lora_params = json.load(f)
            lora_config = get_lora_config(**lora_params)
            model.model = apply_lora(model.model, lora_config)
            load_checkpoint(args.checkpoint, model=model, device="cpu")
            logger.info(
                "Checkpoint fine-tuneado cargado: %s (LoRA r=%d, alpha=%d)",
                args.checkpoint, lora_params["r"], lora_params["lora_alpha"],
            )

        model.eval()

    # Loguear VRAM usada post-carga
    if torch.cuda.is_available():
        vram_used = torch.cuda.memory_allocated() / (1024**3)
        vram_total = get_vram_gb()
        logger.info("VRAM post-carga: %.1fGB / %.1fGB (%.0f%%)", vram_used, vram_total, 100 * vram_used / vram_total)

    # 6. Cargar HAM10000 test split
    splits_file = args.splits_file
    if splits_file is None:
        splits_file = str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    if not Path(splits_file).exists():
        logger.error("Archivo de splits no encontrado: %s", splits_file)
        logger.error("Ejecutar primero: python scripts/prepare_data.py")
        sys.exit(1)

    data_root = str(Path(args.data_dir) / "processed" / "HAM10000")
    test_dataset = HAM10000Dataset(
        root_dir=data_root,
        split="test",
        splits_file=splits_file,
        return_pil=True,  # VLMs necesitan PIL Images (el processor aplica sus propias transforms)
    )
    logger.info("Test set cargado: %d imágenes", len(test_dataset))

    # Ajustar batch_size según el modelo
    batch_size = args.batch_size
    if args.model == "mini_vlm" and batch_size > 1:
        # Phi procesa cada imagen secuencialmente (chat template por imagen)
        batch_size = 1
        logger.info("Batch size forzado a 1 para mini_vlm (Phi procesa secuencialmente)")
    elif use_quantize and batch_size > 1:
        batch_size = 1
        logger.info("Batch size reducido a 1 por cuantización activa (VRAM limitada)")

    collator = VLMCollator()
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=collator, num_workers=args.num_workers,
    )

    # 6a. Rutas alternativas: evitan el colapso de clase del metodo generate.
    if args.method == "likelihood":
        run_likelihood_eval(
            args=args,
            model=model,
            test_dataset=test_dataset,
            is_finetuned=is_finetuned,
            script_start=script_start,
        )
        return

    if args.method == "cot":
        run_cot_eval(
            args=args,
            model=model,
            test_loader=test_loader,
            test_dataset=test_dataset,
            is_finetuned=is_finetuned,
            script_start=script_start,
        )
        return

    # 6. Inferencia zero-shot
    all_image_ids = []
    all_y_true = []
    all_y_pred = []
    all_responses = []
    unknown_count = 0

    if args.dry_run:
        logger.info("=== MODO DRY-RUN: procesando %d batches ===", args.dry_run_batches)
    logger.info("Ejecutando inferencia zero-shot en %d batches...", len(test_loader))
    inference_start = time.perf_counter()
    with torch.no_grad():
        for batch_idx, batch in enumerate(test_loader):
            # PIL Images: no mover a device (el processor las convierte internamente)
            images = batch["image"]
            labels = batch["label"].tolist()
            metadata = batch.get("metadata", [{}] * len(labels))
            batch_size = len(images)

            # Generar respuestas (el modelo maneja dtype internamente con device_map="auto")
            prompts = [CLASSIFICATION_PROMPT] * batch_size
            responses = model.generate(
                images, prompts, max_new_tokens=args.max_new_tokens,
            )

            # Parsear respuestas
            for i, response in enumerate(responses):
                parsed_label = parse_vlm_response(response)
                pred_idx = HAM10000_LABEL_MAP.get(parsed_label, -1)

                if parsed_label == "UNKNOWN":
                    unknown_count += 1

                image_id = metadata[i].get("dx", "") if isinstance(metadata[i], dict) else ""
                all_image_ids.append(image_id)
                all_y_true.append(labels[i])
                all_y_pred.append(pred_idx)
                all_responses.append(response.strip())

            # Loguear progreso cada 10 batches
            if (batch_idx + 1) % 10 == 0:
                elapsed = time.perf_counter() - inference_start
                images_done = (batch_idx + 1) * batch_size
                images_per_sec = images_done / elapsed
                remaining = len(test_loader) - (batch_idx + 1)
                eta = elapsed / (batch_idx + 1) * remaining
                logger.info(
                    "Progreso: %d/%d batches (unknown: %d) [%.1f img/s, ETA: %s]",
                    batch_idx + 1, len(test_loader), unknown_count,
                    images_per_sec, format_duration(eta),
                )

            # Dry-run: cortar después de N batches
            if args.dry_run and (batch_idx + 1) >= args.dry_run_batches:
                logger.info("Dry-run: %d batches procesados, finalizando.", args.dry_run_batches)
                break

    inference_time = time.perf_counter() - inference_start
    logger.info("Inferencia completada en %s", format_duration(inference_time))

    # --- Resumen dry-run ---
    if args.dry_run:
        images_done = len(all_y_true)
        images_per_sec = images_done / max(inference_time, 0.001)

        # VRAM
        if torch.cuda.is_available():
            peak_mb = torch.cuda.max_memory_allocated() / (1024**2)
            total_vram_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
            headroom_mb = total_vram_mb - peak_mb
        else:
            peak_mb = total_vram_mb = headroom_mb = 0

        # Primeras respuestas parseadas
        sample_n = min(5, len(all_responses))
        sample_lines = []
        for i in range(sample_n):
            parsed = parse_vlm_response(all_responses[i])
            true_label = HAM10000_CLASSES[all_y_true[i]] if all_y_true[i] < len(HAM10000_CLASSES) else "?"
            sample_lines.append(
                f"    [{i}] true={true_label} parsed={parsed} raw={all_responses[i][:80]!r}"
            )

        # Extrapolación
        total_batches = len(test_loader)
        est_total_secs = inference_time / max(args.dry_run_batches, 1) * total_batches

        # Estado
        unknown_pct = 100 * unknown_count / max(images_done, 1)
        status = "OK"
        warnings = []
        if unknown_pct > 50:
            warnings.append(f">50% respuestas UNKNOWN ({unknown_pct:.0f}%) — revisar prompt/parsing")
        if 0 < headroom_mb < 500:
            warnings.append(f"headroom VRAM bajo ({headroom_mb:.0f} MB)")
        if warnings:
            status = "ADVERTENCIA — " + "; ".join(warnings)

        logger.info(
            "\n=== RESUMEN DRY-RUN (clasificación %s) ===\n"
            "  VRAM pico          : %.0f MB / %.0f MB\n"
            "  VRAM headroom      : %.0f MB\n"
            "  Imágenes procesadas: %d / %d\n"
            "  Velocidad          : %.2f img/s\n"
            "  UNKNOWN            : %d (%.1f%%)\n"
            "  Est. tiempo total  : %s (%d batches)\n"
            "  Primeras respuestas:\n%s\n"
            "  Estado             : %s",
            args.model,
            peak_mb, total_vram_mb,
            headroom_mb,
            images_done, len(test_dataset),
            images_per_sec,
            unknown_count, unknown_pct,
            format_duration(est_total_secs), total_batches,
            "\n".join(sample_lines),
            status,
        )
        logger.info("Ejecución total: %s", format_duration(time.perf_counter() - script_start))
        sys.exit(0)

    # 7. Resultados
    total = len(all_y_true)
    logger.info("Inferencia completada: %d imágenes, %d respuestas no parseables (%.1f%%)",
                total, unknown_count, 100 * unknown_count / max(total, 1))

    # 8. Guardar predicciones
    results_dir = Path(args.output_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_finetuned" if is_finetuned else ""

    predictions = {
        "model": args.model,
        "finetuned": is_finetuned,
        "y_true": all_y_true,
        "y_pred": all_y_pred,
        "y_prob": None,  # VLMs no generan probabilidades por clase
        "class_names": HAM10000_CLASSES,
        "responses": all_responses,
        "unknown_count": unknown_count,
    }
    pred_filename = f"{args.model}{suffix}_predictions.json"
    save_results(predictions, str(results_dir / pred_filename))
    logger.info("Predicciones guardadas en %s", results_dir / pred_filename)

    # 9. Evaluación rápida
    from src.evaluation.classification import evaluate_classification  # noqa: E402

    # Filtrar predicciones UNKNOWN para métricas válidas
    valid_indices = [i for i, p in enumerate(all_y_pred) if p >= 0]
    if valid_indices:
        y_true_valid = [all_y_true[i] for i in valid_indices]
        y_pred_valid = [all_y_pred[i] for i in valid_indices]
        results = evaluate_classification(y_true_valid, y_pred_valid, class_names=HAM10000_CLASSES)

        mode_label = f"{args.model} (fine-tuned)" if is_finetuned else args.model
        logger.info("=== Resultados %s (excluyendo %d UNKNOWN) ===", mode_label, unknown_count)
        logger.info("Accuracy: %.4f", results["accuracy"])
        logger.info("F1 (weighted): %.4f", results["f1_weighted"])
        logger.info("Sensibilidad (macro): %.4f", results["sensitivity_macro"])
        logger.info("Especificidad (macro): %.4f", results["specificity_macro"])

        # Guardar métricas
        metrics_filename = f"{args.model}{suffix}_test_results.json"
        save_results(
            {
                "model": args.model,
                "finetuned": is_finetuned,
                "accuracy": results["accuracy"],
                "f1_weighted": results["f1_weighted"],
                "auc_roc_macro": results["auc_roc_macro"],
                "sensitivity_macro": results["sensitivity_macro"],
                "specificity_macro": results["specificity_macro"],
                "sensitivity_per_class": results.get("sensitivity_per_class", []),
                "specificity_per_class": results.get("specificity_per_class", []),
                "confusion_matrix": results["confusion_matrix"],
                "unknown_count": unknown_count,
                "total_samples": total,
                "valid_samples": len(valid_indices),
            },
            str(results_dir / metrics_filename),
        )
    else:
        logger.warning("Todas las respuestas fueron UNKNOWN. No se pueden calcular métricas.")

    logger.info("Ejecución total: %s", format_duration(time.perf_counter() - script_start))


if __name__ == "__main__":
    main()
