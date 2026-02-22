from abc import ABC, abstractmethod

import torch
import torch.nn as nn


class VLMBase(nn.Module, ABC):
    """Clase abstracta base para Vision-Language Models.

    Define la interfaz común para LLaVA-Med y Mini-VLM:
    - encode_image: extrae features visuales
    - generate: genera texto dado una imagen + prompt
    - forward: forward pass para entrenamiento
    """

    @abstractmethod
    def encode_image(self, images: torch.Tensor) -> torch.Tensor:
        """Codifica imágenes en embeddings visuales.

        Args:
            images: Tensor (B, C, H, W).

        Returns:
            Embeddings visuales (B, num_patches, hidden_dim).
        """
        ...

    @abstractmethod
    def generate(
        self,
        images: torch.Tensor,
        prompts: list[str],
        max_new_tokens: int = 512,
        **kwargs,
    ) -> list[str]:
        """Genera texto dado imágenes y prompts.

        Args:
            images: Tensor (B, C, H, W).
            prompts: Lista de prompts textuales.
            max_new_tokens: Máximo de tokens a generar.

        Returns:
            Lista de textos generados.
        """
        ...

    @abstractmethod
    def forward(
        self,
        images: torch.Tensor,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: torch.Tensor,
    ) -> dict:
        """Forward pass para entrenamiento.

        Args:
            images: Tensor (B, C, H, W).
            input_ids: Tokens de entrada (B, seq_len).
            attention_mask: Máscara de atención (B, seq_len).
            labels: Tokens target (B, seq_len).

        Returns:
            Dict con al menos "loss".
        """
        ...
