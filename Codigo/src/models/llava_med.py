import logging
from typing import Union

import torch

from src.models.vlm_base import VLMBase
from src.utils.device import get_training_dtype, get_free_vram_gb

logger = logging.getLogger(__name__)


class LLaVAMed(VLMBase):
    """LLaVA-Med v1.5 con Mistral-7B (modelo preentrenado completo).

    Usa LlavaForConditionalGeneration de HuggingFace, que incluye
    vision encoder (CLIP ViT-L/14), MLP de proyección entrenada y LLM (Mistral-7B)
    en un solo checkpoint.

    VRAM estimada: ~14 GB (bf16) / ~5 GB (4-bit NF4).
    """

    MODEL_NAME = "chaoyinshe/llava-med-v1.5-mistral-7b-hf"
    VRAM_REQUIRED_GB = 14.0

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        quantize: bool = False,
        max_new_tokens: int = 512,
    ):
        super().__init__()
        self.model_name = model_name
        self.quantize = quantize
        self.max_new_tokens = max_new_tokens
        self.model = None   # LlavaForConditionalGeneration
        self.processor = None

    def load_components(self):
        """Carga el modelo completo desde HuggingFace.

        Con quantize=True carga el LLM en 4-bit NF4 (bitsandbytes).
        Usa device_map='cuda:0' cuando hay VRAM suficiente, o 'auto' con límite explícito si la GPU está parcialmente ocupada.
        """
        from transformers import AutoProcessor, BitsAndBytesConfig, LlavaForConditionalGeneration

        dtype = get_training_dtype()
        free_gb = get_free_vram_gb()

        # Con cuantización 4-bit, el modelo necesita ~40% de la VRAM original.
        # Evitar device_map="auto" (CPU offloading) cuando el modelo cuantizado
        # cabe en GPU — el offloading ralentiza el entrenamiento drásticamente.
        effective_required = self.VRAM_REQUIRED_GB if not self.quantize else self.VRAM_REQUIRED_GB * 0.4
        if free_gb >= effective_required or not torch.cuda.is_available():
            device_map = "cuda:0"
        else:
            device_map = "auto"

        kwargs = {
            "torch_dtype": dtype,
            "device_map": device_map,
            "low_cpu_mem_usage": True,
            # sdpa (Scaled Dot Product Attention) está integrado en PyTorch 2.0+
            # y auto-despacha a FlashAttention-2 o memory-efficient kernels cuando
            # están disponibles, sin requerir instalación de paquetes externos.
            "attn_implementation": "sdpa",
        }

        if device_map == "auto" and torch.cuda.is_available():
            max_mem_gb = max(1, int(free_gb * 0.9))
            kwargs["max_memory"] = {0: f"{max_mem_gb}GiB", "cpu": "16GiB"}

        if self.quantize:
            # Verificar que bitsandbytes está disponible y funcional
            try:
                import bitsandbytes as _bnb
                _bnb_ok = getattr(_bnb, "cextension", None) is not None and _bnb.cextension.lib is not None
            except ImportError:
                _bnb_ok = False
            if not _bnb_ok:
                logger.warning(
                    "bitsandbytes no disponible o CUDA backend incompatible. "
                    "Desactivando cuantización — modelo se cargará en %s.", dtype,
                )
                self.quantize = False

        if self.quantize:
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=dtype,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                # Excluir el proyector y vision encoder de la cuantización:
                # - Proyector: sus parámetros deben ser entrenables en float (Stage 1).
                # - Vision tower: CLIP ViT-L/14 cuantizado produce embeddings
                #   numéricos inestables que causan NaN en el loss.
                # El prefijo "model." es necesario porque LlavaForConditionalGeneration
                # envuelve LlavaModel como .model.
                llm_int8_skip_modules=[
                    "model.multi_modal_projector",
                    "model.vision_tower",
                ],
            )

        # Cadena de carga con fallbacks para atención y cuantización.
        # 1) sdpa → eager (si sdpa no disponible)
        # 2) Si falla por bitsandbytes/cuantización, reintentar sin cuantización.
        attn_options = ["sdpa", "eager"]
        last_exc = None
        for attn_impl in attn_options:
            kwargs["attn_implementation"] = attn_impl
            try:
                self.model = LlavaForConditionalGeneration.from_pretrained(self.model_name, **kwargs)
                last_exc = None
                break
            except Exception as exc:
                last_exc = exc
                exc_str = str(exc).lower()
                # Error de bitsandbytes/cuantización: reintentar sin cuantización
                if any(kw in exc_str for kw in ("bitsandbytes", "libcusparse", "bnb", "quantiz", "cquantize")):
                    logger.warning(
                        "Error de cuantización al cargar %s con atención '%s': %s. "
                        "Reintentando sin cuantización...",
                        self.model_name, attn_impl, exc,
                    )
                    kwargs.pop("quantization_config", None)
                    self.quantize = False
                    try:
                        self.model = LlavaForConditionalGeneration.from_pretrained(self.model_name, **kwargs)
                        last_exc = None
                        break
                    except Exception as exc2:
                        last_exc = exc2
                        continue
                logger.info("Atención '%s' no disponible: %s. Probando siguiente...", attn_impl, exc)
        if last_exc is not None:
            raise RuntimeError(
                f"No se pudo cargar {self.model_name} con ninguna configuración. "
                f"Último error: {last_exc}"
            ) from last_exc
        logger.info("LLaVA-Med: usando atención '%s', cuantización=%s", kwargs["attn_implementation"], self.quantize)
        self.model.eval()

        try:
            self.processor = AutoProcessor.from_pretrained(self.model_name)
        except Exception as exc:
            logger.warning(
                "Error cargando AutoProcessor: %s. "
                "Construyendo LlavaProcessor manualmente con tokenizer lento...",
                exc,
            )
            from transformers import AutoTokenizer, CLIPImageProcessor, LlavaProcessor
            image_processor = CLIPImageProcessor.from_pretrained(self.model_name)
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, use_fast=False
            )
            self.processor = LlavaProcessor(
                image_processor=image_processor, tokenizer=tokenizer
            )
        self.processor.tokenizer.padding_side = "left"
        if self.processor.tokenizer.pad_token is None:
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token

    @torch.no_grad()
    def generate(
        self,
        images: Union[torch.Tensor, list],
        prompts: list[str],
        max_new_tokens: int = None,
        **kwargs,
    ) -> list[str]:
        """Genera texto dado imágenes y prompts.

        Args:
            images: Lista de PIL Images o Tensor (B, C, H, W).
            prompts: Lista de prompts textuales.
            max_new_tokens: Máximo de tokens a generar.

        Returns:
            Lista de textos generados (sin el prompt de entrada).
        """
        max_tok = max_new_tokens or self.max_new_tokens
        results = []

        for img, prompt in zip(images, prompts):
            text = f"[INST] <image>\n{prompt} [/INST]"
            inputs = self.processor(
                images=img,
                text=text,
                return_tensors="pt",
            ).to(self.model.device)

            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_tok,
                do_sample=False,
                pad_token_id=self.processor.tokenizer.pad_token_id,
                **kwargs,
            )

            input_len = inputs["input_ids"].shape[1]
            generated_ids = output_ids[:, input_len:]
            results.append(
                self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            )

        return results

    def forward(
        self,
        images: Union[torch.Tensor, list],
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor,
        image_sizes: torch.Tensor = None,
    ) -> dict:
        """Forward pass para fine-tuning en Fase 2 (generación de reportes).

        Args:
            images: Lista de PIL Images o Tensor (B, C, H, W).
            input_ids: Tokens de entrada (B, seq_len).
            attention_mask: Máscara de atención (B, seq_len).
            labels: Tokens target (B, seq_len).

        Returns:
            Dict con al menos "loss".
        """
        pixel_values = self.processor.image_processor(
            images=images,
            return_tensors="pt",
        )["pixel_values"].to(device=self.model.device, dtype=self.model.dtype)

        outputs = self.model(
            pixel_values=pixel_values,
            input_ids=input_ids.to(self.model.device),
            attention_mask=attention_mask.to(self.model.device),
            labels=labels.to(self.model.device),
        )
        return {"loss": outputs.loss}
