from typing import Any

import torch


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
