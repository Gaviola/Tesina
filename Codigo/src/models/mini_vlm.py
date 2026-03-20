import logging
from typing import Union

import torch

from src.models.vlm_base import VLMBase
from src.utils.device import get_training_dtype, get_free_vram_gb

logger = logging.getLogger(__name__)

import transformers
from transformers.cache_utils import DynamicCache

# --- Patch para compatibilidad de Phi-3.5-vision ---
# En transformers >= 4.41.0 se modificó la API de DynamicCache.
# Inyectamos dinámicamente las propiedades legacy que el código de Microsoft requiere.

if not hasattr(DynamicCache, "seen_tokens"):
    DynamicCache.seen_tokens = property(lambda self: self.get_seq_length())

if not hasattr(DynamicCache, "get_max_length"):
    # El modelo tiene una ventana de contexto de 128k
    DynamicCache.get_max_length = lambda self, *args, **kwargs: 131072

if not hasattr(DynamicCache, "get_usable_length"):
    def _get_usable_length(self, new_seq_length=None, layer_idx=None, *args, **kwargs):
        # Intentar obtener la longitud de la capa específica, fallback a la general
        try:
            return self.get_seq_length(layer_idx)
        except Exception:
            return self.get_seq_length()

    DynamicCache.get_usable_length = _get_usable_length

if not hasattr(DynamicCache, "from_legacy_cache"):
    @classmethod
    def _from_legacy_cache(cls, past_key_values=None):
        """Convierte el formato legacy (tupla de tuplas) a DynamicCache."""
        cache = cls()
        if past_key_values is not None:
            for layer_idx, (key, value) in enumerate(past_key_values):
                cache.update(key, value, layer_idx)
        return cache

    DynamicCache.from_legacy_cache = _from_legacy_cache

class MiniVLM(VLMBase):
    """Phi-3.5-vision-instruct: VLM integrado de Microsoft.

    Modelo más ligero que LLaVA-Med. Incluye vision encoder (CLIP ViT-L/14),
    proyección (img_projection) y LLM (Phi-3.5-mini) en un solo checkpoint
    preentrenado. A diferencia de LLaVA-Med, no tiene un MLP de proyección
    separado como componente de alto nivel — la proyección está integrada
    dentro de vision_embed_tokens.

    Componentes entrenables en Stage 1: img_projection, glb_GN, sub_GN (~10-20M params).
    Componentes entrenables en Stage 2: img_projection + LoRA en LLM.

    VRAM estimada: ~8-10 GB (bf16) / ~4-5 GB (4-bit NF4).
    """

    MODEL_NAME = "microsoft/Phi-3.5-vision-instruct"
    VRAM_REQUIRED_GB = 10.0

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
        self.model = None
        self.processor = None

    def load_components(self, num_crops: int = None):
        """Carga el modelo completo desde HuggingFace.

        Phi requiere trust_remote_code=True.
        Intenta flash_attention_2, luego sdpa, fallback a 'eager'.
        Con quantize=True carga en 4-bit NF4 (bitsandbytes).

        Args:
            num_crops: Override para num_crops del procesador de imágenes.
                Si None, usa el default del modelo (4). Reducir para
                ahorrar VRAM en Stage 1 (e.g., num_crops=1 → 2 crops totales).

        Nota — Warnings conocidos del código remoto de Phi-3.5-vision:
        1. TypeError en logging: transformers.modeling_attn_mask_utils llama
           logger.warning_once(msg, FutureWarning) sin placeholder %s. Es un
           bug interno de transformers, no afecta funcionalidad.
        2. DeprecationWarning de AttentionMaskConverter: el código remoto de
           Microsoft (modeling_phi3_v.py) importa de modeling_attn_mask_utils
           que está deprecated. No podemos corregirlo (es código upstream).
           No afecta funcionalidad en las versiones actuales de transformers.
        """
        from transformers import AutoModelForCausalLM, AutoProcessor, BitsAndBytesConfig

        dtype = get_training_dtype()
        free_gb = get_free_vram_gb()

        # Si hay VRAM suficiente, colocar todo en GPU; sino device_map="auto" con límite
        if free_gb >= self.VRAM_REQUIRED_GB or not torch.cuda.is_available():
            device_map = "cuda:0"
        else:
            device_map = "auto"

        kwargs = {
            "device_map": device_map,
            "trust_remote_code": True,
            "torch_dtype": dtype,
            "low_cpu_mem_usage": True,
            "_attn_implementation": "flash_attention_2",
        }

        if device_map == "auto" and torch.cuda.is_available():
            max_mem_gb = max(1, int(free_gb * 0.9))
            kwargs["max_memory"] = {0: f"{max_mem_gb}GiB", "cpu": "16GiB"}

        if self.quantize:
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
            )

        attn_impl = kwargs["_attn_implementation"]
        try:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
        except Exception:
            # Fallback 1: sdpa (PyTorch nativo, disponible en todas las plataformas)
            attn_impl = "sdpa"
            kwargs["_attn_implementation"] = attn_impl
            try:
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
            except Exception:
                # Fallback 2: eager (O(n²) en memoria, siempre funciona)
                attn_impl = "eager"
                kwargs["_attn_implementation"] = attn_impl
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name, **kwargs)
        logger.info("Mini-VLM: usando atención '%s'", attn_impl)

        self.model.eval()
        self.processor = AutoProcessor.from_pretrained(
            self.model_name, trust_remote_code=True
        )

        if num_crops is not None and hasattr(self.processor, "image_processor"):
            original = getattr(self.processor.image_processor, "num_crops", None)
            self.processor.image_processor.num_crops = num_crops
            logger.info(
                "Mini-VLM: num_crops ajustado de %s a %d para reducir uso de VRAM.",
                original, num_crops,
            )

    @torch.no_grad()
    def generate(
        self,
        images: Union[torch.Tensor, list],
        prompts: list[str],
        max_new_tokens: int = None,
        **kwargs,
    ) -> list[str]:
        """Genera texto dado imágenes y prompts.

        Phi requiere chat template con <|image_1|> en el prompt.
        Procesa cada imagen por separado (batch_size=1 por limitación del chat template).

        Args:
            images: Lista de PIL Images.
            prompts: Lista de prompts textuales.
            max_new_tokens: Máximo de tokens a generar.

        Returns:
            Lista de textos generados.
        """
        max_tok = max_new_tokens or self.max_new_tokens
        results = []

        for img, prompt in zip(images, prompts):
            messages = [{"role": "user", "content": f"<|image_1|>\n{prompt}"}]
            text = self.processor.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
            inputs = self.processor(text, [img], return_tensors="pt").to(self.model.device)

            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_tok,
                do_sample=False,
                eos_token_id=self.processor.tokenizer.eos_token_id,
            )

            # Decodificar solo los tokens generados (excluir el input)
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
        """Forward pass para fine-tuning con LoRA en Fase 2 (generación de reportes).

        Args:
            images: Tensor de pixel values (B, num_crops, C, H, W) o lista de PIL Images.
            input_ids: Tokens de entrada (B, seq_len).
            attention_mask: Máscara de atención (B, seq_len).
            labels: Tokens target (B, seq_len).
            image_sizes: Tamaños originales de las imágenes (B, 2) — requerido por Phi-3.5.

        Returns:
            Dict con al menos "loss".
        """
        kwargs = dict(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels,
            pixel_values=images if isinstance(images, torch.Tensor) else None,
        )
        if image_sizes is not None:
            kwargs["image_sizes"] = image_sizes
        outputs = self.model(**kwargs)
        return {"loss": outputs.loss}
