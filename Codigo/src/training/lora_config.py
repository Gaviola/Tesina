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
        target_modules: Módulos donde aplicar LoRA. Default: ["q_proj", "v_proj"].
        task_type: Tipo de tarea PEFT.

    Returns:
        LoraConfig configurado.
    """
    if target_modules is None:
        target_modules = ["q_proj", "v_proj"]

    return LoraConfig(
        r=r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=target_modules,
        task_type=task_type,
        bias="none",
    )


def apply_lora(model, lora_config: LoraConfig):
    """Aplica LoRA a un modelo y retorna el modelo PEFT.

    Args:
        model: Modelo base (e.g., LLaMA-2, Phi-3).
        lora_config: Configuración LoRA.

    Returns:
        Modelo con adaptadores LoRA aplicados.
    """
    return get_peft_model(model, lora_config)
