"""Fase 1: Clasificación zero-shot vía prompt con VLMs.

Uso:
    python scripts/train_vlm_classify.py --model llava_med
    python scripts/train_vlm_classify.py --model mini_vlm
"""

import argparse
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
from src.models.factory import build_model
from src.utils.device import check_vram, get_device, get_training_dtype, get_vram_gb
from src.utils.io import save_results
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


def main():
    parser = argparse.ArgumentParser(description="F1: Clasificación zero-shot con VLMs")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--splits_file", type=str, default=None)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_new_tokens", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--wandb", action="store_true")
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--quantize", action="store_true", help="Forzar cuantización 4-bit del LLM")
    args = parser.parse_args()

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
    logger.info("Iniciando clasificación zero-shot con %s", args.model)

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
    with log_time("Cargando modelo %s%s" % (args.model, " (4-bit)" if use_quantize else ""), logger):
        model = build_model({"name": args.model, "quantize": use_quantize})
        model.load_components()
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

    data_root = str(Path(args.data_dir) / "raw" / "ham10000")
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
        # Phi-3-vision procesa cada imagen secuencialmente (chat template por imagen)
        batch_size = 1
        logger.info("Batch size forzado a 1 para mini_vlm (Phi-3-vision procesa secuencialmente)")
    elif use_quantize and batch_size > 1:
        batch_size = 1
        logger.info("Batch size reducido a 1 por cuantización activa (VRAM limitada)")

    collator = VLMCollator()
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        collate_fn=collator, num_workers=args.num_workers,
    )

    # 6. Inferencia zero-shot
    all_image_ids = []
    all_y_true = []
    all_y_pred = []
    all_responses = []
    unknown_count = 0

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

    inference_time = time.perf_counter() - inference_start
    logger.info("Inferencia completada en %s", format_duration(inference_time))

    # 7. Resultados
    total = len(all_y_true)
    logger.info("Inferencia completada: %d imágenes, %d respuestas no parseables (%.1f%%)",
                total, unknown_count, 100 * unknown_count / max(total, 1))

    # 8. Guardar predicciones
    results_dir = Path(args.output_dir) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    predictions = {
        "model": args.model,
        "y_true": all_y_true,
        "y_pred": all_y_pred,
        "y_prob": None,  # VLMs no generan probabilidades por clase
        "class_names": HAM10000_CLASSES,
        "responses": all_responses,
        "unknown_count": unknown_count,
    }
    save_results(predictions, str(results_dir / f"{args.model}_predictions.json"))
    logger.info("Predicciones guardadas en %s", results_dir / f"{args.model}_predictions.json")

    # 9. Evaluación rápida
    from src.evaluation.classification import evaluate_classification  # noqa: E402

    # Filtrar predicciones UNKNOWN para métricas válidas
    valid_indices = [i for i, p in enumerate(all_y_pred) if p >= 0]
    if valid_indices:
        y_true_valid = [all_y_true[i] for i in valid_indices]
        y_pred_valid = [all_y_pred[i] for i in valid_indices]
        results = evaluate_classification(y_true_valid, y_pred_valid, class_names=HAM10000_CLASSES)

        logger.info("=== Resultados %s (excluyendo %d UNKNOWN) ===", args.model, unknown_count)
        logger.info("Accuracy: %.4f", results["accuracy"])
        logger.info("F1 (weighted): %.4f", results["f1_weighted"])
        logger.info("Sensibilidad (macro): %.4f", results["sensitivity_macro"])
        logger.info("Especificidad (macro): %.4f", results["specificity_macro"])

        # Guardar métricas
        save_results(
            {
                "model": args.model,
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
            str(results_dir / f"{args.model}_test_results.json"),
        )
    else:
        logger.warning("Todas las respuestas fueron UNKNOWN. No se pueden calcular métricas.")

    logger.info("Ejecución total: %s", format_duration(time.perf_counter() - script_start))


if __name__ == "__main__":
    main()
