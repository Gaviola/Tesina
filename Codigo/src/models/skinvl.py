"""SkinVL-MM: VLM derm-especializado para generación (P1.1, plan julio-agosto).

SkinVL-MM (`zwq803/SkinVL-MM`) es LLaVA-Med v1.5 (Mistral-7B) fine-tuneado sobre MM-Skin.
Comparte arquitectura EXACTA con nuestro LLaVAMed (LlavaForConditionalGeneration), por lo
que el wrapper es un subclass fino: solo cambia el checkpoint. Hereda generate()/forward().

IMPORTANTE — formato del checkpoint:
    El repo `zwq803/SkinVL-MM` viene en formato ORIGINAL de LLaVA-Med
    (`LlavaMistralForCausalLM`, model_type=llava_mistral), NO en formato HF
    (`LlavaForConditionalGeneration`). Hay que convertirlo a HF UNA vez (local, sin GPU)
    y apuntar MODEL_NAME al path resultante. Ver:
    `Codigo/docs/ideas/skinvl_ensemble_plan_20260705.md`.
"""

from src.models.llava_med import LLaVAMed


class SkinVL(LLaVAMed):
    """LLaVA-Med v1.5 derm-especializado (MM-Skin). Runtime idéntico a LLaVAMed."""

    # Path local del checkpoint YA CONVERTIDO a formato HF (ver idea doc). En el cluster
    # se resuelve desde el cache HF offline. Ajustar si se usa otra ubicación.
    MODEL_NAME = "data/checkpoints/skinvl-mm-hf"
    VRAM_REQUIRED_GB = 14.0

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        quantize: bool = False,
        max_new_tokens: int = 512,
    ):
        super().__init__(
            model_name=model_name,
            quantize=quantize,
            max_new_tokens=max_new_tokens,
        )
