"""Builders de schedulers para entrenamiento de Fase 1.

Soporta scheduler base (CosineAnnealingLR / ninguno) con un warmup
lineal opcional al inicio. Para warmup_epochs=0 el comportamiento es
bit-a-bit idéntico al previo a esta utilidad (CosineAnnealingLR plano
o None).
"""

from typing import Any, Optional

import torch
from torch.optim import Optimizer
from torch.optim.lr_scheduler import CosineAnnealingLR, LinearLR, SequentialLR


def build_scheduler(
    name: str,
    optimizer: Optimizer,
    total_epochs: int,
    warmup_epochs: int = 0,
    warmup_start_factor: float = 0.1,
) -> Optional[Any]:
    """Construye scheduler combinado warmup + base.

    Args:
        name: ``"CosineAnnealingLR"`` o ``"none"``.
        optimizer: optimizador a programar.
        total_epochs: épocas totales del entrenamiento.
        warmup_epochs: épocas de warmup lineal al inicio
            (0 = sin warmup, comportamiento legacy).
        warmup_start_factor: factor de lr al inicio del warmup
            (1.0 desactiva el warmup efectivo).

    Returns:
        Scheduler de PyTorch, o ``None`` si ``name == "none"`` y sin warmup.
    """
    if warmup_epochs < 0:
        raise ValueError(f"warmup_epochs debe ser >= 0, recibido {warmup_epochs}")
    if warmup_epochs >= total_epochs:
        raise ValueError(
            f"warmup_epochs ({warmup_epochs}) debe ser menor que total_epochs ({total_epochs})"
        )

    base = _build_base(name, optimizer, total_epochs - warmup_epochs)

    if warmup_epochs == 0:
        return base

    warmup = LinearLR(
        optimizer,
        start_factor=warmup_start_factor,
        end_factor=1.0,
        total_iters=warmup_epochs,
    )

    if base is None:
        return warmup

    return SequentialLR(
        optimizer,
        schedulers=[warmup, base],
        milestones=[warmup_epochs],
    )


def _build_base(name: str, optimizer: Optimizer, t_max: int) -> Optional[Any]:
    if name == "CosineAnnealingLR":
        return CosineAnnealingLR(optimizer, T_max=t_max)
    if name == "none":
        return None
    raise ValueError(f"Scheduler '{name}' no soportado. Usar 'CosineAnnealingLR' o 'none'.")
