"""Pérdidas para clasificación de Fase 1.

Incluye Focal Loss multi-clase con soporte de:
- pesos por clase (mismo formato que ``nn.CrossEntropyLoss(weight=...)``),
- label smoothing,
- targets duros (LongTensor de índices) o suaves (FloatTensor B×C, p.ej. mixup/cutmix).

Cuando ``gamma=0.0`` la pérdida es numéricamente equivalente a
``CrossEntropyLoss(weight, label_smoothing)``.
"""

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalLoss(nn.Module):
    """Focal Loss multi-clase.

    Definición: FL(p_t) = -alpha_t * (1 - p_t)**gamma * log(p_t)

    Para targets duros usa ``F.one_hot`` internamente. Para targets suaves
    (mixup/cutmix) opera directamente sobre la matriz de probabilidades.

    Args:
        gamma: factor focal. 0.0 → equivalente a CE.
        weight: pesos por clase, tensor de tamaño C. None = sin pesos.
        label_smoothing: ε en [0, 1). Aplicado solo a targets duros.
        reduction: ``"mean"`` | ``"sum"`` | ``"none"``.
    """

    def __init__(
        self,
        gamma: float = 0.0,
        weight: Optional[torch.Tensor] = None,
        label_smoothing: float = 0.0,
        reduction: str = "mean",
    ):
        super().__init__()
        if gamma < 0:
            raise ValueError(f"gamma debe ser >= 0, recibido {gamma}")
        if not 0 <= label_smoothing < 1:
            raise ValueError(f"label_smoothing debe estar en [0, 1), recibido {label_smoothing}")
        if reduction not in {"mean", "sum", "none"}:
            raise ValueError(f"reduction debe ser mean|sum|none, recibido {reduction}")

        self.gamma = gamma
        self.label_smoothing = label_smoothing
        self.reduction = reduction
        self.register_buffer("weight", weight, persistent=False)

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        num_classes = logits.size(-1)

        if target.ndim == 1 or target.dtype in (torch.long, torch.int64, torch.int32):
            # Hard targets: índices de clase
            target_oh = F.one_hot(target.long(), num_classes).to(dtype=logits.dtype)
            if self.label_smoothing > 0:
                target_oh = target_oh * (1 - self.label_smoothing) + self.label_smoothing / num_classes
        else:
            # Soft targets: ya son una distribución sobre clases (mixup/cutmix)
            target_oh = target.to(dtype=logits.dtype)

        log_probs = F.log_softmax(logits, dim=-1)
        probs = log_probs.exp()

        # Focal modulation: (1 - p_t)^gamma. p_t = sum(probs * target_oh) por sample.
        if self.gamma > 0:
            focal_weight = (1.0 - probs).clamp(min=1e-7).pow(self.gamma)
            per_class_loss = -focal_weight * log_probs * target_oh
        else:
            per_class_loss = -log_probs * target_oh

        if self.weight is not None:
            per_class_loss = per_class_loss * self.weight.view(1, -1)

        per_sample_loss = per_class_loss.sum(dim=-1)

        if self.reduction == "mean":
            if self.weight is not None:
                # Promedio ponderado por la suma de pesos correspondientes al target
                norm = (target_oh * self.weight.view(1, -1)).sum(dim=-1)
                return per_sample_loss.sum() / norm.sum().clamp(min=1e-8)
            return per_sample_loss.mean()
        if self.reduction == "sum":
            return per_sample_loss.sum()
        return per_sample_loss


class BalancedSoftmaxLoss(nn.Module):
    """Balanced Softmax (Ren et al., NeurIPS 2020).

    Ajusta los logits sumando ``log(prior_de_clase)`` antes de la cross-entropy, de modo que
    el entrenamiento compensa el desbalance sin re-pesar la pérdida. No usa pesos por clase.

    Args:
        class_counts: tensor de tamaño C con la cantidad de muestras por clase (train).
        label_smoothing: ε en [0, 1).
    """

    def __init__(self, class_counts: torch.Tensor, label_smoothing: float = 0.0):
        super().__init__()
        counts = class_counts.float()
        prior = counts / counts.sum().clamp(min=1e-8)
        self.register_buffer("log_prior", prior.clamp(min=1e-8).log(), persistent=False)
        self.label_smoothing = label_smoothing

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        adjusted = logits + self.log_prior.view(1, -1)
        return F.cross_entropy(adjusted, target.long(), label_smoothing=self.label_smoothing)


def build_loss(
    focal_gamma: float,
    class_weights: Optional[torch.Tensor],
    label_smoothing: float,
    balanced_softmax: bool = False,
    class_counts: Optional[torch.Tensor] = None,
) -> nn.Module:
    """Factory de loss para clasificación.

    - ``balanced_softmax=True`` → BalancedSoftmaxLoss (ignora focal/pesos; requiere class_counts).
    - ``focal_gamma > 0`` → FocalLoss.
    - en otro caso → ``nn.CrossEntropyLoss`` (soporta soft targets nativamente).
    """
    if balanced_softmax:
        if class_counts is None:
            raise ValueError("balanced_softmax=True requiere class_counts")
        return BalancedSoftmaxLoss(class_counts, label_smoothing=label_smoothing)
    if focal_gamma > 0:
        return FocalLoss(
            gamma=focal_gamma,
            weight=class_weights,
            label_smoothing=label_smoothing,
        )
    return nn.CrossEntropyLoss(
        weight=class_weights,
        label_smoothing=label_smoothing,
    )
