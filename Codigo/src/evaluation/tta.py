"""Test-time augmentation para clasificadores de Fase 1.

Implementa promediado de softmax sobre múltiples vistas de cada imagen
en evaluación. Versión actual soporta horizontal flip (2 vistas).
``5-crop`` queda preparado vía la signatura pero se implementaría en
una segunda iteración.
"""

from typing import Iterable, Optional

import numpy as np
import torch


def evaluate_with_tta(
    model,
    dataloader,
    device: torch.device,
    dtype: torch.dtype,
    num_classes: int,
    tta_modes: Iterable[str] = ("original", "hflip"),
) -> tuple[list[int], list[int], np.ndarray]:
    """Evalúa el modelo promediando softmax sobre las vistas TTA solicitadas.

    Args:
        tta_modes: subset de {"original", "hflip"}. ``("original",)``
            equivale a una pasada normal sin TTA.

    Returns:
        (y_pred, y_true, y_prob) — mismo formato que ``evaluate_on_split``.
    """
    modes = tuple(tta_modes)
    if not modes:
        raise ValueError("tta_modes no puede estar vacío")
    for m in modes:
        if m not in {"original", "hflip"}:
            raise ValueError(f"TTA mode no soportado: {m}")

    model.eval()
    all_preds: list[int] = []
    all_labels: list[int] = []
    all_probs: list[np.ndarray] = []
    use_amp = dtype in (torch.float16, torch.bfloat16) and device.type == "cuda"

    with torch.no_grad():
        for batch in dataloader:
            images = batch["image"].to(device, non_blocking=True)
            labels = batch["label"]

            probs_sum: Optional[torch.Tensor] = None
            for view in _make_views(images, modes):
                with torch.amp.autocast("cuda", dtype=dtype, enabled=use_amp):
                    outputs = model(view)
                probs = torch.softmax(outputs, dim=1).float()
                probs_sum = probs if probs_sum is None else probs_sum + probs

            probs_avg = probs_sum / len(modes)
            preds = probs_avg.argmax(dim=1).cpu().tolist()

            all_preds.extend(preds)
            all_labels.extend(labels.tolist())
            all_probs.append(probs_avg.cpu().numpy())

    return all_preds, all_labels, np.concatenate(all_probs, axis=0)


def _make_views(images: torch.Tensor, modes: tuple[str, ...]):
    for mode in modes:
        if mode == "original":
            yield images
        elif mode == "hflip":
            yield torch.flip(images, dims=[-1])
