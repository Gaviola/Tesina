from typing import Any, Optional

import numpy as np
import torch
import torch.nn.functional as F


class ClassificationCollator:
    """Collator para batches de clasificación (imagen + label)."""

    def __call__(self, batch: list[dict]) -> dict[str, Any]:
        images = torch.stack([sample["image"] for sample in batch])
        labels = torch.tensor([sample["label"] for sample in batch], dtype=torch.long)

        result = {"image": images, "label": labels}

        # Incluir metadata si está disponible
        if "metadata" in batch[0]:
            result["metadata"] = [sample["metadata"] for sample in batch]

        return result


class MixupCutmixCollator:
    """Collator que aplica MixUp y/o CutMix a nivel batch.

    Envuelve a un collator base. Con probabilidad ``mixup_prob`` aplica
    MixUp (alpha=mixup_alpha), con probabilidad ``1 - mixup_prob`` aplica
    CutMix (alpha=cutmix_alpha). Si una de las dos alphas es 0, siempre se
    aplica la otra. Si ambas son 0, no aplica nada (passthrough).

    Devuelve además del ``label`` original (índices, para métricas) un
    ``target`` softmax-compatible (B, C, float) con la mezcla aplicada.
    El loss debe leer ``target`` cuando esté presente; ``label`` queda
    para evaluar accuracy/F1 con la clase mayoritaria.
    """

    def __init__(
        self,
        num_classes: int,
        mixup_alpha: float = 0.0,
        cutmix_alpha: float = 0.0,
        mixup_prob: float = 0.5,
        base_collator: Optional[ClassificationCollator] = None,
        rng_seed: Optional[int] = None,
    ):
        if mixup_alpha < 0 or cutmix_alpha < 0:
            raise ValueError("alphas deben ser >= 0")
        if not 0 <= mixup_prob <= 1:
            raise ValueError("mixup_prob debe estar en [0, 1]")
        self.num_classes = num_classes
        self.mixup_alpha = mixup_alpha
        self.cutmix_alpha = cutmix_alpha
        self.mixup_prob = mixup_prob
        self.base = base_collator or ClassificationCollator()
        self._rng = np.random.default_rng(rng_seed)

    def __call__(self, batch: list[dict]) -> dict[str, Any]:
        result = self.base(batch)

        if self.mixup_alpha == 0 and self.cutmix_alpha == 0:
            return result
        if result["image"].size(0) < 2:
            return result  # batch demasiado chico para mezclar

        use_mixup = self._choose_mode()
        if use_mixup is None:
            return result  # ambas alphas en 0

        images = result["image"]
        labels = result["label"]

        if use_mixup:
            mixed_images, target = _mixup(images, labels, self.num_classes, self.mixup_alpha, self._rng)
        else:
            mixed_images, target = _cutmix(images, labels, self.num_classes, self.cutmix_alpha, self._rng)

        result["image"] = mixed_images
        result["target"] = target
        return result

    def _choose_mode(self) -> Optional[bool]:
        """True = mixup, False = cutmix, None = no aplicar."""
        if self.mixup_alpha > 0 and self.cutmix_alpha > 0:
            return bool(self._rng.random() < self.mixup_prob)
        if self.mixup_alpha > 0:
            return True
        if self.cutmix_alpha > 0:
            return False
        return None


def _mixup(images: torch.Tensor, labels: torch.Tensor, num_classes: int,
           alpha: float, rng: np.random.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    lam = float(rng.beta(alpha, alpha))
    perm = torch.randperm(images.size(0))
    mixed = lam * images + (1.0 - lam) * images[perm]
    one_hot = F.one_hot(labels, num_classes).float()
    target = lam * one_hot + (1.0 - lam) * one_hot[perm]
    return mixed, target


def _cutmix(images: torch.Tensor, labels: torch.Tensor, num_classes: int,
            alpha: float, rng: np.random.Generator) -> tuple[torch.Tensor, torch.Tensor]:
    lam = float(rng.beta(alpha, alpha))
    perm = torch.randperm(images.size(0))

    H, W = images.shape[-2:]
    cut_rat = float(np.sqrt(1.0 - lam))
    cut_w = int(W * cut_rat)
    cut_h = int(H * cut_rat)
    cx = int(rng.integers(0, W))
    cy = int(rng.integers(0, H))
    x1 = max(cx - cut_w // 2, 0)
    y1 = max(cy - cut_h // 2, 0)
    x2 = min(cx + cut_w // 2, W)
    y2 = min(cy + cut_h // 2, H)

    mixed = images.clone()
    mixed[..., y1:y2, x1:x2] = images[perm, ..., y1:y2, x1:x2]

    # lam efectivo según área real del recorte
    lam_eff = 1.0 - ((x2 - x1) * (y2 - y1) / float(W * H))
    one_hot = F.one_hot(labels, num_classes).float()
    target = lam_eff * one_hot + (1.0 - lam_eff) * one_hot[perm]
    return mixed, target


class VLMCollator:
    """Collator para batches multimodales (imagen + texto).

    Soporta tanto tensores como PIL Images. Cuando las imágenes son PIL,
    se devuelven como lista (el processor del VLM se encarga del preprocesado).
    Cuando son tensores, se apilan en un batch tensor.
    """

    def __call__(self, batch: list[dict]) -> dict[str, Any]:
        images = [sample["image"] for sample in batch]
        if isinstance(images[0], torch.Tensor):
            images = torch.stack(images)

        result = {"image": images}

        if "text" in batch[0]:
            result["text"] = [sample["text"] for sample in batch]

        if "label" in batch[0]:
            result["label"] = torch.tensor(
                [sample["label"] for sample in batch], dtype=torch.long
            )

        if "metadata" in batch[0]:
            result["metadata"] = [sample["metadata"] for sample in batch]

        return result
