"""Pipeline de entrenamiento en 2 etapas para VLMs.

Etapa 1 (Alineamiento): Entrena solo el MLP de proyección con MM-Skin captions.
Etapa 2 (Instrucciones): Aplica LoRA al LLM y entrena con MM-Skin VQA.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any

import torch
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import Dataset

from src.models.llava_med import LLaVAMed
from src.training.callbacks import CheckpointCallback, EarlyStopping
from src.training.lora_config import apply_lora, get_lora_config
from src.utils.device import get_device, get_training_dtype
from src.utils.logging import format_duration, log_gpu_memory, log_metrics

try:
    from tqdm import tqdm as _tqdm
    _TQDM_AVAILABLE = True
except ImportError:
    _TQDM_AVAILABLE = False

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataset wrapper
# ---------------------------------------------------------------------------

class MMSkinVQADataset(Dataset):
    """Wrapper que expande los pares QA de MMSkinDataset en samples individuales.

    MMSkinDataset retorna un item por imagen con múltiples QA pairs.
    Este wrapper expande los pares para que cada par sea un item de entrenamiento.
    Resultado: ~27,259 items (imagen, pregunta, respuesta) desde ~11,002 imágenes.
    """

    def __init__(self, base_dataset):
        """
        Args:
            base_dataset: MMSkinDataset instanciado con mode="vqa".
        """
        self.base = base_dataset
        self.index = []  # [(dataset_idx, qa_idx), ...]
        for i, sample in enumerate(base_dataset.samples):
            for j in range(len(sample["qa_pairs"])):
                self.index.append((i, j))
        logger.info(
            "MMSkinVQADataset: %d pares QA desde %d imágenes",
            len(self.index), len(base_dataset.samples),
        )

    def __len__(self):
        return len(self.index)

    def __getitem__(self, idx: int) -> dict:
        ds_idx, qa_idx = self.index[idx]
        base_item = self.base[ds_idx]
        qa = self.base.samples[ds_idx]["qa_pairs"][qa_idx]
        return {
            "image": base_item["image"],   # PIL Image (transform=None)
            "text": qa["question"],        # pregunta (instrucción)
            "answer": qa["answer"],        # respuesta (target)
            "label": -1,
            "metadata": base_item["metadata"],
        }


# ---------------------------------------------------------------------------
# Collator de entrenamiento
# ---------------------------------------------------------------------------

class VLMTrainCollator:
    """Collator para entrenamiento de VLMs con MM-Skin.

    Tokeniza imágenes + texto y construye labels con -100 en posiciones de prompt.
    Solo se computa loss sobre los tokens de respuesta.

    Args:
        processor: Processor del VLM (LlavaProcessor o AutoProcessor de Phi).
        model_type: "llava_med" | "mini_vlm".
        max_length: Longitud máxima de secuencia (tokens).
        mode: "caption" (Stage 1) | "vqa" (Stage 2).
    """

    CAPTION_INSTRUCTION = "Describe this skin lesion."

    def __init__(self, processor, model_type: str, max_length: int = 2048, mode: str = "caption"):
        self.processor = processor
        self.model_type = model_type
        self.max_length = max_length
        self.mode = mode

    def _get_tokenizer(self):
        if hasattr(self.processor, "tokenizer"):
            return self.processor.tokenizer
        return self.processor

    def _process_llava_med(self, images, instructions, responses):
        tokenizer = self._get_tokenizer()
        orig_padding_side = tokenizer.padding_side
        tokenizer.padding_side = "right"  # right-pad para training

        try:
            full_texts = [
                f"USER: <image>\n{inst}\nASSISTANT: {resp}"
                for inst, resp in zip(instructions, responses)
            ]

            encoding = self.processor(
                images=images,
                text=full_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length,
            )

            input_ids = encoding["input_ids"]
            attention_mask = encoding["attention_mask"]
            labels = input_ids.clone()

            for i, response in enumerate(responses):
                # Tokenizar solo la respuesta para determinar n_response_tokens
                response_ids = tokenizer.encode(response, add_special_tokens=False)
                n_response = len(response_ids)
                seq_len = int(attention_mask[i].sum().item())

                # Maskear todo excepto los últimos n_response tokens no-padding
                mask_until = seq_len - n_response
                if mask_until > 0:
                    labels[i, :mask_until] = -100
                labels[i, seq_len:] = -100  # maskear padding

        finally:
            tokenizer.padding_side = orig_padding_side

        return {
            "image": images,
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels,
        }

    def _process_mini_vlm(self, images, instructions, responses):
        tokenizer = self._get_tokenizer()

        all_input_ids = []
        all_attention_masks = []
        all_pixel_values = []
        all_n_responses = []

        for img, inst, resp in zip(images, instructions, responses):
            messages = [{"role": "user", "content": f"<|image_1|>\n{inst}"}]
            prompt_text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
            full_text = prompt_text + resp + "<|end|>"

            enc = self.processor(
                full_text,
                [img],
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
            )
            all_input_ids.append(enc["input_ids"][0])
            all_attention_masks.append(enc["attention_mask"][0])
            if "pixel_values" in enc and enc["pixel_values"] is not None:
                all_pixel_values.append(enc["pixel_values"][0])

            resp_ids = tokenizer.encode(resp, add_special_tokens=False)
            all_n_responses.append(len(resp_ids))

        # Padding manual (right-padded)
        max_len = max(ids.shape[0] for ids in all_input_ids)
        pad_id = (
            tokenizer.pad_token_id
            if tokenizer.pad_token_id is not None
            else tokenizer.eos_token_id
        )

        padded_input_ids = torch.full((len(all_input_ids), max_len), pad_id, dtype=torch.long)
        padded_attention_mask = torch.zeros((len(all_input_ids), max_len), dtype=torch.long)
        labels = torch.full((len(all_input_ids), max_len), -100, dtype=torch.long)

        for i, (ids, mask, n_resp) in enumerate(
            zip(all_input_ids, all_attention_masks, all_n_responses)
        ):
            seq_len = ids.shape[0]
            padded_input_ids[i, :seq_len] = ids
            padded_attention_mask[i, :seq_len] = mask
            # Solo computar loss sobre tokens de respuesta
            start = seq_len - n_resp
            if start < seq_len:
                labels[i, start:seq_len] = ids[start:seq_len]

        pixel_values = torch.stack(all_pixel_values) if all_pixel_values else None

        return {
            # Para MiniVLM.forward(): images recibe tensor si isinstance(images, Tensor)
            "image": pixel_values if pixel_values is not None else images,
            "input_ids": padded_input_ids,
            "attention_mask": padded_attention_mask,
            "labels": labels,
        }

    def __call__(self, batch: list[dict]) -> dict:
        images = [sample["image"] for sample in batch]

        if self.mode == "caption":
            instructions = [self.CAPTION_INSTRUCTION] * len(batch)
            responses = [str(sample.get("text") or "") for sample in batch]
        else:  # vqa
            instructions = [str(sample.get("text") or "") for sample in batch]
            responses = [str(sample.get("answer") or "") for sample in batch]

        if self.model_type == "llava_med":
            return self._process_llava_med(images, instructions, responses)
        else:
            return self._process_mini_vlm(images, instructions, responses)


# ---------------------------------------------------------------------------
# Helpers de congelamiento
# ---------------------------------------------------------------------------

def _get_model_type(model) -> str:
    return "llava_med" if isinstance(model, LLaVAMed) else "mini_vlm"


def _count_trainable_params(model) -> tuple[int, int]:
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    return trainable, total


def _get_llava_vision_tower(hf_model):
    """Resuelve el módulo vision tower en LlavaForConditionalGeneration.

    Distintas versiones de transformers / checkpoints exponen el encoder
    bajo nombres distintos. Prueba los candidatos más comunes antes de hacer
    una búsqueda por nombre de módulo.
    """
    for attr in ("vision_tower", "vision_model"):
        if hasattr(hf_model, attr):
            return getattr(hf_model, attr)
    # Algunos checkpoints anidan el modelo: hf_model.model.vision_tower
    inner = getattr(hf_model, "model", None)
    if inner is not None:
        for attr in ("vision_tower", "vision_model"):
            if hasattr(inner, attr):
                return getattr(inner, attr)
    # Fallback: buscar el primer submódulo cuyo nombre contenga "vision_tower"
    for name, module in hf_model.named_modules():
        if "vision_tower" in name and module is not hf_model:
            return module
    raise AttributeError(
        f"No se encontró el vision tower en {type(hf_model).__name__}. "
        "Atributos disponibles: " + ", ".join(n for n, _ in hf_model.named_children())
    )


def _get_llava_language_model(hf_model):
    """Resuelve el módulo LLM en LlavaForConditionalGeneration."""
    for attr in ("language_model", "lm", "text_model", "model"):
        candidate = getattr(hf_model, attr, None)
        if candidate is not None and candidate is not hf_model:
            # Descartar el wrapper 'model' si a su vez es otro LlavaModel — en ese
            # caso preferimos buscar más adentro para no congelar el proyector también.
            # Pero si no hay otro candidato, lo usamos como fallback al final.
            if attr != "model":
                return candidate
    # Fallback: hf_model.model (p.ej. LlavaModel que contiene el LLM y vision tower)
    inner = getattr(hf_model, "model", None)
    if inner is not None:
        for attr in ("language_model", "lm", "text_model"):
            candidate = getattr(inner, attr, None)
            if candidate is not None:
                return candidate
    # Último recurso: buscar por nombre de módulo
    for name, module in hf_model.named_modules():
        if any(k in name for k in ("language_model", "text_model")) and module is not hf_model:
            return module
    raise AttributeError(
        f"No se encontró el language model en {type(hf_model).__name__}. "
        "Atributos disponibles: " + ", ".join(n for n, _ in hf_model.named_children())
    )


def _get_llava_projector(hf_model):
    """Resuelve el módulo de proyección multimodal en LlavaForConditionalGeneration."""
    for attr in ("multi_modal_projector", "mm_projector", "vision_projector",
                 "connector", "img_projection", "image_projection"):
        candidate = getattr(hf_model, attr, None)
        if candidate is not None:
            return candidate
    inner = getattr(hf_model, "model", None)
    if inner is not None:
        for attr in ("multi_modal_projector", "mm_projector", "vision_projector",
                     "connector", "img_projection"):
            candidate = getattr(inner, attr, None)
            if candidate is not None:
                return candidate
    for name, module in hf_model.named_modules():
        if any(k in name for k in ("projector", "mm_proj", "img_proj")) and module is not hf_model:
            return module
    raise AttributeError(
        f"No se encontró el proyector multimodal en {type(hf_model).__name__}. "
        "Atributos disponibles: " + ", ".join(n for n, _ in hf_model.named_children())
    )


def _is_quantized(hf_model) -> bool:
    """Detecta si el modelo fue cargado con cuantización 4-bit u 8-bit (bitsandbytes)."""
    return (
        getattr(hf_model, "is_loaded_in_4bit", False)
        or getattr(hf_model, "is_loaded_in_8bit", False)
    )


def _freeze_for_stage1(model, model_type: str):
    """Stage 1: Congela vision encoder + LLM, descongela solo MLP de proyección.

    Con cuantización 4-bit (QLoRA), los pesos son Params4bit (uint8) y no admiten
    requires_grad=True. En ese caso se llama a prepare_model_for_kbit_training y
    solo se descongela los parámetros float del proyector (biases, layer norms).
    """
    hf_model = model.model

    if model_type == "llava_med":
        if _is_quantized(hf_model):
            from peft import prepare_model_for_kbit_training
            model.model = prepare_model_for_kbit_training(
                hf_model,
                use_gradient_checkpointing=True,
                gradient_checkpointing_kwargs={"use_reentrant": False},
            )
            hf_model = model.model
            projector = _get_llava_projector(hf_model)
            n_unfrozen = 0
            for p in projector.parameters():
                if p.dtype in (torch.float32, torch.float16, torch.bfloat16):
                    p.requires_grad = True
                    n_unfrozen += 1
            if n_unfrozen == 0:
                logger.warning(
                    "Stage 1 (cuantizado): el proyector no tiene parámetros float "
                    "entrenables. Considera aumentar VRAM para entrenar sin cuantización."
                )
        else:
            vision_tower = _get_llava_vision_tower(hf_model)
            for p in vision_tower.parameters():
                p.requires_grad = False
            language_model = _get_llava_language_model(hf_model)
            for p in language_model.parameters():
                p.requires_grad = False
            projector = _get_llava_projector(hf_model)
            for p in projector.parameters():
                p.requires_grad = True
    else:  # mini_vlm
        if _is_quantized(hf_model):
            from peft import prepare_model_for_kbit_training
            model.model = prepare_model_for_kbit_training(
                hf_model,
                use_gradient_checkpointing=True,
                gradient_checkpointing_kwargs={"use_reentrant": False},
            )
            hf_model = model.model
            n_unfrozen = 0
            for name, module in hf_model.named_modules():
                if any(k in name for k in ("img_projection", "image_projection", "vision_embed_tokens")):
                    for p in module.parameters():
                        if p.dtype in (torch.float32, torch.float16, torch.bfloat16):
                            p.requires_grad = True
                            n_unfrozen += 1
            if n_unfrozen == 0:
                logger.warning(
                    "Stage 1 (cuantizado, mini_vlm): sin parámetros float en proyección. "
                    "Considera aumentar VRAM."
                )
        else:
            for p in hf_model.parameters():
                p.requires_grad = False
            projection_found = False
            for name, module in hf_model.named_modules():
                if any(k in name for k in ("img_projection", "image_projection", "vision_embed_tokens")):
                    for p in module.parameters():
                        p.requires_grad = True
                    projection_found = True
            if not projection_found:
                logger.warning(
                    "Mini-VLM: no se encontraron capas de proyección de imagen. "
                    "Entrenando modelo completo como fallback."
                )
                for p in hf_model.parameters():
                    p.requires_grad = True

    trainable, total = _count_trainable_params(model)
    logger.info(
        "Stage 1 — Parámetros entrenables: %d / %d (%.2f%%)",
        trainable, total, 100.0 * trainable / max(total, 1),
    )


def _freeze_vision_encoder(model, model_type: str):
    """Stage 2: Congela solo el vision encoder (LLM queda disponible para LoRA)."""
    hf_model = model.model

    if model_type == "llava_med":
        vision_tower = _get_llava_vision_tower(hf_model)
        for p in vision_tower.parameters():
            p.requires_grad = False
    else:  # mini_vlm
        for name, module in hf_model.named_modules():
            if any(k in name for k in ("vision_model", "img_projection", "image_projection")):
                for p in module.parameters():
                    p.requires_grad = False

    trainable, total = _count_trainable_params(model)
    logger.info(
        "Stage 2 (pre-LoRA) — Parámetros entrenables: %d / %d (%.2f%%)",
        trainable, total, 100.0 * trainable / max(total, 1),
    )


# ---------------------------------------------------------------------------
# Loop de entrenamiento
# ---------------------------------------------------------------------------

def _train_vlm_loop(
    model,
    train_loader,
    val_loader,
    optimizer,
    scheduler,
    cfg: dict,
    callbacks: list,
    dtype: torch.dtype,
) -> dict:
    """Loop de entrenamiento compartido para Stage 1 y Stage 2."""
    device = get_device()
    epochs     = cfg.get("epochs", 1)
    grad_accum = cfg.get("gradient_accumulation_steps", 1)
    batch_size = cfg.get("batch_size", 1)
    checkpoint_dir = cfg.get("checkpoint_dir", "outputs/checkpoints")
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

    use_autocast   = (dtype != torch.float32) and torch.cuda.is_available()
    history        = {"train_loss": [], "val_loss": []}
    best_epoch     = 1
    epoch_times    = []
    training_start = time.perf_counter()

    for epoch in range(1, epochs + 1):
        epoch_start = time.perf_counter()

        # ---- Entrenamiento ----
        model.train()
        optimizer.zero_grad(set_to_none=True)
        train_loss_sum = 0.0
        n_batches = 0

        train_iter = _tqdm(
            train_loader,
            desc=f"Época {epoch}/{epochs} [train]",
            unit="batch", leave=False, dynamic_ncols=True,
        ) if _TQDM_AVAILABLE else train_loader

        batch_start = time.perf_counter()
        for batch_idx, batch in enumerate(train_iter):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)
            images         = batch["image"]
            if isinstance(images, torch.Tensor):
                images = images.to(device)

            with torch.amp.autocast("cuda", dtype=dtype, enabled=use_autocast):
                output = model(images, input_ids, attention_mask, labels)
                loss   = output["loss"] / grad_accum

            loss.backward()

            if (batch_idx + 1) % grad_accum == 0:
                torch.nn.utils.clip_grad_norm_(
                    [p for p in model.parameters() if p.requires_grad],
                    max_norm=1.0,
                )
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad(set_to_none=True)

            train_loss_sum += loss.item() * grad_accum
            n_batches += 1

            if _TQDM_AVAILABLE:
                elapsed_b = time.perf_counter() - batch_start
                sps = (n_batches * batch_size) / max(elapsed_b, 1e-6)
                train_iter.set_postfix(
                    loss=f"{train_loss_sum / n_batches:.4f}",
                    sps=f"{sps:.1f}",
                    ordered=True,
                )

            if batch_idx % 50 == 0:
                elapsed   = time.perf_counter() - epoch_start
                done      = batch_idx + 1
                remaining = len(train_loader) - done
                eta_epoch = (elapsed / done) * remaining if done > 0 else 0.0
                logger.info(
                    "Época %d/%d | Batch %d/%d | Loss: %.4f | "
                    "Transcurrido: %s | ETA época: %s",
                    epoch, epochs, batch_idx, len(train_loader),
                    train_loss_sum / n_batches,
                    format_duration(elapsed),
                    format_duration(eta_epoch),
                )

        if _TQDM_AVAILABLE:
            train_iter.close()
        avg_train_loss = train_loss_sum / max(n_batches, 1)

        # ---- Validación ----
        model.eval()
        val_loss_sum = 0.0
        n_val = 0

        val_iter = _tqdm(
            val_loader,
            desc=f"Época {epoch}/{epochs} [val]  ",
            unit="batch", leave=False, dynamic_ncols=True,
        ) if _TQDM_AVAILABLE else val_loader

        with torch.no_grad():
            for batch in val_iter:
                input_ids      = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels         = batch["labels"].to(device)
                images         = batch["image"]
                if isinstance(images, torch.Tensor):
                    images = images.to(device)
                with torch.amp.autocast("cuda", dtype=dtype, enabled=use_autocast):
                    output = model(images, input_ids, attention_mask, labels)
                val_loss_sum += output["loss"].item()
                n_val += 1
                if _TQDM_AVAILABLE:
                    val_iter.set_postfix(
                        loss=f"{val_loss_sum / n_val:.4f}", ordered=True,
                    )

        if _TQDM_AVAILABLE:
            val_iter.close()
        avg_val_loss = val_loss_sum / max(n_val, 1)

        epoch_elapsed = time.perf_counter() - epoch_start
        epoch_times.append(epoch_elapsed)
        avg_epoch_t   = sum(epoch_times) / len(epoch_times)
        eta_remaining = avg_epoch_t * (epochs - epoch)

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)

        metrics = {"epoch": epoch, "train_loss": avg_train_loss, "val_loss": avg_val_loss}
        log_metrics(metrics, step=epoch)
        logger.info(
            "Época %d/%d completada | Train Loss: %.4f | Val Loss: %.4f | "
            "Tiempo: %s | ETA restante: %s",
            epoch, epochs, avg_train_loss, avg_val_loss,
            format_duration(epoch_elapsed),
            format_duration(eta_remaining),
        )
        log_gpu_memory(logger, prefix=f"Época {epoch}/{epochs} | ")

        # ---- Callbacks ----
        stop = False
        for cb in callbacks:
            result = cb(
                epoch=epoch, metrics=metrics, model=model,
                optimizer=optimizer, checkpoint_dir=checkpoint_dir,
            )
            if result.get("stop", False):
                logger.info("Entrenamiento detenido por callback en época %d", epoch)
                stop = True
                break

        if stop:
            break

        if avg_val_loss == min(history["val_loss"]):
            best_epoch = epoch

    # ---- Resumen final ----
    total_time  = time.perf_counter() - training_start
    avg_epoch_t = sum(epoch_times) / max(len(epoch_times), 1)
    best_val    = min(history["val_loss"]) if history["val_loss"] else float("nan")
    logger.info(
        "=== Resumen de entrenamiento ===\n"
        "  Tiempo total       : %s\n"
        "  Épocas completadas : %d / %d\n"
        "  Tiempo por época   : %s (promedio)\n"
        "  Mejor época        : %d\n"
        "  Mejor val_loss     : %.4f",
        format_duration(total_time),
        len(epoch_times), epochs,
        format_duration(avg_epoch_t),
        best_epoch, best_val,
    )

    return {
        "train_loss":       history["train_loss"],
        "val_loss":         history["val_loss"],
        "best_epoch":       best_epoch,
        "final_train_loss": history["train_loss"][-1] if history["train_loss"] else None,
        "final_val_loss":   history["val_loss"][-1]   if history["val_loss"]   else None,
    }


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def run_stage1(model, train_loader, val_loader, cfg: dict[str, Any]) -> dict:
    """Etapa 1: Alineamiento visual-textual.

    Congela vision encoder y LLM, entrena solo MLP de proyección.
    Usa MM-Skin captions (~11k pares imagen-texto) como datos de entrenamiento.

    Args:
        model: VLM (LLaVA-Med o Mini-VLM) con componentes cargados.
        train_loader: DataLoader con pares imagen-caption (MM-Skin caption mode).
        val_loader: DataLoader de validación.
        cfg: Dict con claves: epochs, lr, gradient_accumulation_steps, checkpoint_dir.

    Returns:
        Dict con train_loss (lista), val_loss (lista), best_epoch, stage=1.
    """
    model_type = _get_model_type(model)
    logger.info("Iniciando Stage 1 — modelo: %s", model_type)

    _freeze_for_stage1(model, model_type)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    if not trainable_params:
        raise RuntimeError("Stage 1: no hay parámetros entrenables tras el congelamiento.")

    logger.info(
        "=== Configuración Stage 1 ===\n"
        "  Modelo        : %s\n"
        "  Épocas        : %d\n"
        "  LR            : %.2e\n"
        "  Grad accum    : %d\n"
        "  Train batches : %d | Val batches: %d",
        model_type,
        cfg.get("epochs", 1),
        cfg.get("lr", 2e-3),
        cfg.get("gradient_accumulation_steps", 1),
        len(train_loader),
        len(val_loader),
    )

    optimizer = torch.optim.AdamW(trainable_params, lr=cfg.get("lr", 2e-3), weight_decay=0.0)

    epochs = cfg.get("epochs", 1)
    grad_accum = cfg.get("gradient_accumulation_steps", 1)
    total_steps = max(1, epochs * len(train_loader) // grad_accum)
    scheduler = CosineAnnealingLR(optimizer, T_max=total_steps)

    callbacks = [CheckpointCallback(monitor="val_loss", mode="min")]

    dtype = get_training_dtype()
    metrics = _train_vlm_loop(
        model, train_loader, val_loader, optimizer, scheduler, cfg, callbacks, dtype,
    )

    logger.info(
        "Stage 1 completado | Best epoch: %d | Best val_loss: %.4f",
        metrics["best_epoch"],
        min(metrics["val_loss"]) if metrics["val_loss"] else float("nan"),
    )
    return {**metrics, "stage": 1}


def run_stage2(model, train_loader, val_loader, cfg: dict[str, Any]) -> dict:
    """Etapa 2: Ajuste de instrucciones con LoRA.

    Aplica LoRA al LLM y entrena con MM-Skin VQA (~27k pares instrucción-respuesta).

    Args:
        model: VLM con MLP alineado (de stage1, opcional).
        train_loader: DataLoader con pares QA expandidos (MMSkinVQADataset).
        val_loader: DataLoader de validación.
        cfg: Dict con claves: epochs, lr, gradient_accumulation_steps, checkpoint_dir,
             lora (dict con r, alpha, dropout, target_modules), early_stopping_patience.

    Returns:
        Dict con train_loss, val_loss, best_epoch, lora_config, stage=2.
    """
    model_type = _get_model_type(model)
    logger.info("Iniciando Stage 2 — modelo: %s", model_type)

    _freeze_vision_encoder(model, model_type)

    if _is_quantized(model.model):
        from peft import prepare_model_for_kbit_training
        model.model = prepare_model_for_kbit_training(
            model.model,
            use_gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
        )
        logger.info("Stage 2 (cuantizado): prepare_model_for_kbit_training aplicado.")

    lora_cfg = cfg.get("lora", {})
    lora_config_params = {
        "r": lora_cfg.get("r", 64),
        "lora_alpha": lora_cfg.get("alpha", 128),
        "lora_dropout": lora_cfg.get("dropout", 0.05),
        "target_modules": lora_cfg.get("target_modules", ["q_proj", "v_proj"]),
    }
    lora_config = get_lora_config(**lora_config_params)

    model.model = apply_lora(model.model, lora_config)
    if hasattr(model.model, "print_trainable_parameters"):
        model.model.print_trainable_parameters()

    logger.info(
        "=== Configuración Stage 2 ===\n"
        "  Modelo        : %s\n"
        "  Épocas        : %d\n"
        "  LR            : %.2e\n"
        "  Grad accum    : %d\n"
        "  LoRA r/alpha  : %d / %d\n"
        "  Train batches : %d | Val batches: %d",
        model_type,
        cfg.get("epochs", 1),
        cfg.get("lr", 2e-5),
        cfg.get("gradient_accumulation_steps", 1),
        lora_config_params["r"],
        lora_config_params["lora_alpha"],
        len(train_loader),
        len(val_loader),
    )

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=cfg.get("lr", 2e-5), weight_decay=0.01)

    callbacks = [
        EarlyStopping(patience=cfg.get("early_stopping_patience", 3), monitor="val_loss"),
        CheckpointCallback(monitor="val_loss", mode="min"),
    ]

    dtype = get_training_dtype()
    metrics = _train_vlm_loop(
        model, train_loader, val_loader, optimizer, None, cfg, callbacks, dtype,
    )

    # Guardar lora_config junto al checkpoint para restaurar en inferencia
    checkpoint_dir = cfg.get("checkpoint_dir", "outputs/checkpoints")
    lora_info_path = Path(checkpoint_dir) / "lora_config.json"
    with open(lora_info_path, "w", encoding="utf-8") as f:
        json.dump(lora_config_params, f, indent=2)
    logger.info("LoRA config guardada en %s", lora_info_path)

    logger.info(
        "Stage 2 completado | Best epoch: %d | Best val_loss: %.4f",
        metrics["best_epoch"],
        min(metrics["val_loss"]) if metrics["val_loss"] else float("nan"),
    )
    return {**metrics, "stage": 2, "lora_config": lora_config_params}
