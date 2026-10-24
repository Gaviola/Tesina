from peft import LoraConfig, TaskType, get_peft_model


def get_lora_config(
    r: int = 64,
    lora_alpha: int = 128,
    lora_dropout: float = 0.05,
    target_modules: list[str] | None = None,
    task_type: TaskType = TaskType.CAUSAL_LM,
) -> LoraConfig:
    """Crea configuración LoRA centralizada para los VLMs.

    Args:
        r: Rango de LoRA. Valores típicos: 16, 32, 64, 128.
        lora_alpha: Factor de escala. Típicamente 2*r.
        lora_dropout: Dropout en capas LoRA.
        target_modules: Módulos donde aplicar LoRA.
            Default: todas las capas lineales de atención y FFN.
        task_type: Tipo de tarea PEFT.

    Returns:
        LoraConfig configurado.
    """
    if target_modules is None:
        target_modules = [
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ]

    return LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
        task_type=task_type,
        bias="none",
    )


## Prefijo que deja un modelo envuelto dos veces por get_peft_model: el reintento por OOM de la etapa 2 de
## Mini-VLM v3 (job 1179985) reusó el modelo ya envuelto y guardó las claves como
## ``model.base_model.model.base_model.model.…``. Los adaptadores son uno solo; solo cambia el nombre.
_DOUBLE_WRAP = "base_model.model.base_model.model."


def normalize_peft_keys(state_dict: dict, expected_keys: set[str]) -> dict:
    """Colapsa el prefijo PEFT repetido en las claves que no existen en el modelo."""
    out = {}
    for key, value in state_dict.items():
        new_key = key
        while new_key not in expected_keys and _DOUBLE_WRAP in new_key:
            new_key = new_key.replace(_DOUBLE_WRAP, "base_model.model.", 1)
        out[new_key] = value
    return out


def load_finetuned_state_dict(model, state_dict: dict, strict: bool = True):
    """Carga un checkpoint de la etapa 2 sobre un modelo ya envuelto con ``apply_lora``.

    Normaliza el prefijo PEFT repetido y, a diferencia de ``load_state_dict(strict=False)``, falla si algún
    adaptador LoRA del modelo queda sin cargar (antes eso pasaba en silencio y se generaba con el modelo base).
    Con ``strict=False`` tolera otras claves faltantes o sobrantes y solo las cuenta.
    """
    expected = set(model.state_dict().keys())
    result = model.load_state_dict(normalize_peft_keys(state_dict, expected), strict=False)
    missing_lora = [k for k in result.missing_keys if "lora_" in k]
    if missing_lora or (strict and (result.missing_keys or result.unexpected_keys)):
        raise RuntimeError(
            f"Checkpoint incompatible: {len(missing_lora)} adaptadores LoRA sin cargar, "
            f"{len(result.missing_keys)} claves faltantes y {len(result.unexpected_keys)} sobrantes "
            f"(p. ej. {(missing_lora or result.missing_keys or result.unexpected_keys)[:2]})"
        )
    return result


def apply_lora(model, lora_config: LoraConfig):
    """Aplica LoRA a un modelo y retorna el modelo PEFT.

    Args:
        model: Modelo base (e.g., LLaMA-2, Phi-3).
        lora_config: Configuración LoRA.

    Returns:
        Modelo con adaptadores LoRA aplicados.
    """
    return get_peft_model(model, lora_config)
