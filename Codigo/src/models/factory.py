from typing import Any

import torch.nn as nn

from src.models.classifiers import DenseNet121Classifier, ViTClassifier
from src.models.llava_med import LLaVAMed
from src.models.mini_vlm import MiniVLM

MODEL_REGISTRY: dict[str, type[nn.Module]] = {
    "densenet": DenseNet121Classifier,
    "vit": ViTClassifier,
    "llava_med": LLaVAMed,
    "mini_vlm": MiniVLM,
}


def build_model(cfg: dict[str, Any]) -> nn.Module:
    """Instancia un modelo a partir de configuración.

    Args:
        cfg: Diccionario de configuración con al menos "name" y parámetros del modelo.
             Ejemplo: {"name": "densenet", "num_classes": 7, "pretrained": True}

    Returns:
        Modelo instanciado.
    """
    name = cfg.get("name")
    if name not in MODEL_REGISTRY:
        raise ValueError(
            f"Modelo '{name}' no registrado. Disponibles: {list(MODEL_REGISTRY.keys())}"
        )

    model_cls = MODEL_REGISTRY[name]

    # Extraer kwargs del modelo (excluir "name")
    kwargs = {k: v for k, v in cfg.items() if k != "name"}

    return model_cls(**kwargs)


def register_model(name: str, model_cls: type[nn.Module]):
    """Registra un nuevo modelo en el registry."""
    MODEL_REGISTRY[name] = model_cls
