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
            "attn_implementation": "flash_attention_2",
        }

        if device_map == "auto" and torch.cuda.is_available():
            max_mem_gb = max(1, int(free_gb * 0.9))
            kwargs["max_memory"] = {0: f"{max_mem_gb}GiB", "cpu": "16GiB"}

        if self.quantize:
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                # Excluir el proyector multimodal de la cuantización para que
                # sus parámetros sean entrenables en float durante Stage 1.
                llm_int8_skip_modules=["multi_modal_projector"],
            )

        attn_impl = kwargs["attn_implementation"]
        try:
            self.model = LlavaForConditionalGeneration.from_pretrained(self.model_name, **kwargs)
        except Exception:
            # Fallback 1: sdpa (PyTorch nativo, disponible en todas las plataformas)
            attn_impl = "sdpa"
            kwargs["attn_implementation"] = attn_impl
            try:
                self.model = LlavaForConditionalGeneration.from_pretrained(self.model_name, **kwargs)
            except Exception:
                # Fallback 2: eager (O(n²) en memoria, siempre funciona)
                attn_impl = "eager"
                kwargs["attn_implementation"] = attn_impl
                self.model = LlavaForConditionalGeneration.from_pretrained(self.model_name, **kwargs)
        logger.info("LLaVA-Med: usando atención '%s'", attn_impl)
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

        inputs = self.processor(
            images=images,
            text=prompts,
            return_tensors="pt",
            padding=True,
        ).to(self.model.device)

        output_ids = self.model.generate(
            **inputs,
            max_new_tokens=max_tok,
            do_sample=False,
            pad_token_id=self.processor.tokenizer.pad_token_id,
        )

        # Decodificar solo los tokens generados (excluir el input)
        input_len = inputs["input_ids"].shape[1]
        generated_ids = output_ids[:, input_len:]
        return self.processor.batch_decode(generated_ids, skip_special_tokens=True)

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
        )["pixel_values"].to(self.model.device)

        outputs = self.model(
            pixel_values=pixel_values,
            input_ids=input_ids.to(self.model.device),
            attention_mask=attention_mask.to(self.model.device),
            labels=labels.to(self.model.device),
        )
        return {"loss": outputs.loss}
