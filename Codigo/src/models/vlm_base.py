from abc import ABC, abstractmethod
from typing import Union

import torch
import torch.nn as nn
from PIL import Image


class VLMBase(nn.Module, ABC):
    """Clase abstracta base para Vision-Language Models.

    Soporta tanto modelos con componentes separados (vision encoder + projection + LLM)
    como modelos integrados (LlavaForConditionalGeneration, Phi-3-vision, etc.).

    Interfaz obligatoria:
    - load_components: carga pesos desde HuggingFace
    - generate: genera texto dado imágenes + prompts
    - forward: forward pass para entrenamiento (Fase 2)
    """

    @abstractmethod
    def load_components(self):
        """Carga el modelo y processor desde HuggingFace."""
        ...

    def encode_image(self, images: torch.Tensor) -> torch.Tensor:
        """Codifica imágenes en embeddings visuales.

        Opcional en modelos integrados (lo hacen internamente en generate/forward).

        Args:
            images: Tensor (B, C, H, W).

        Returns:
            Embeddings visuales (B, num_patches, hidden_dim).
        """
        raise NotImplementedError(
            "encode_image() no aplica a modelos VLM integrados. "
            "Usar generate() o forward() directamente."
        )

    @abstractmethod
    def generate(
        self,
        images: Union[torch.Tensor, list],
        prompts: list[str],
        max_new_tokens: int = 512,
        **kwargs,
    ) -> list[str]:
        """Genera texto dado imágenes y prompts.

        Args:
            images: Tensor (B, C, H, W) o lista de PIL Images.
            prompts: Lista de prompts textuales.
            max_new_tokens: Máximo de tokens a generar.

        Returns:
            Lista de textos generados.
        """
        ...

    @abstractmethod
    def forward(
        self,
        images: Union[torch.Tensor, list],
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor,
    ) -> dict:
        """Forward pass para entrenamiento (Fase 2).

        Args:
            images: Tensor (B, C, H, W) o lista de PIL Images.
            input_ids: Tokens de entrada (B, seq_len).
            attention_mask: Máscara de atención (B, seq_len).
            labels: Tokens target (B, seq_len).

        Returns:
            Dict con al menos "loss".
        """
        ...
