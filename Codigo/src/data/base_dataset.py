from abc import ABC, abstractmethod
from typing import Any, Optional

from torch.utils.data import Dataset


class BaseDataset(Dataset, ABC):
    """Clase abstracta base para todos los datasets del proyecto.

    Todos los datasets deben devolver un diccionario con al menos:
    - "image": tensor de la imagen (C, H, W)
    - "label": int con la etiqueta de clase (o -1 si no aplica)

    Opcionalmente:
    - "text": str con texto asociado (descripciones, reportes)
    - "metadata": dict con información adicional
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform: Optional[Any] = None,
    ):
        """
        Args:
            root_dir: Directorio raíz del dataset procesado.
            split: Partición a usar ("train", "val", "test").
            transform: Transformaciones de torchvision a aplicar.
        """
        self.root_dir = root_dir
        self.split = split
        self.transform = transform
        self.samples = []
        self._load_data()

    @abstractmethod
    def _load_data(self):
        """Carga la lista de samples según el split. Debe poblar self.samples."""
        ...

    @abstractmethod
    def __getitem__(self, idx: int) -> dict:
        """Retorna un sample como diccionario."""
        ...

    def __len__(self) -> int:
        return len(self.samples)

    @abstractmethod
    def get_class_names(self) -> list[str]:
        """Retorna la lista de nombres de clases."""
        ...

    def get_class_weights(self):
        """Calcula pesos inversos a la frecuencia de cada clase para CrossEntropyLoss."""
        import torch

        labels = [s["label"] for s in self.samples if "label" in s]
        if not labels:
            return None
        class_counts = {}
        for label in labels:
            class_counts[label] = class_counts.get(label, 0) + 1
        total = len(labels)
        num_classes = max(labels) + 1
        weights = torch.zeros(num_classes)
        for cls_id, count in class_counts.items():
            weights[cls_id] = total / (num_classes * count)
        return weights
