import logging
from pathlib import Path

import torch

from src.utils.io import save_checkpoint

logger = logging.getLogger(__name__)


class EarlyStopping:
    """Early stopping basado en una métrica de validación.

    Detiene el entrenamiento si la métrica no mejora durante `patience` épocas.
    """

    def __init__(self, patience: int = 5, monitor: str = "val_loss", mode: str = "min"):
        self.patience = patience
        self.monitor = monitor
        self.mode = mode
        self.counter = 0
        self.best_value = float("inf") if mode == "min" else float("-inf")

    def _is_improvement(self, value: float) -> bool:
        if self.mode == "min":
            return value < self.best_value
        return value > self.best_value

    def __call__(self, epoch, metrics, model, optimizer, checkpoint_dir) -> dict:
        value = metrics.get(self.monitor)
        if value is None:
            return {}

        if self._is_improvement(value):
            self.best_value = value
            self.counter = 0
        else:
            self.counter += 1
            logger.info(
                "EarlyStopping: %s no mejoró por %d épocas (mejor: %.4f, actual: %.4f)",
                self.monitor, self.counter, self.best_value, value,
            )

        if self.counter >= self.patience:
            logger.info("EarlyStopping activado tras %d épocas sin mejora", self.patience)
            return {"stop": True}

        return {}


class CheckpointCallback:
    """Guarda checkpoint del mejor modelo según una métrica.

    Guarda en `checkpoint_dir/best_model.pt` cada vez que la métrica mejora.
    """

    def __init__(self, monitor: str = "val_loss", mode: str = "min"):
        self.monitor = monitor
        self.mode = mode
        self.best_value = float("inf") if mode == "min" else float("-inf")

    def _is_improvement(self, value: float) -> bool:
        if self.mode == "min":
            return value < self.best_value
        return value > self.best_value

    def __call__(self, epoch, metrics, model, optimizer, checkpoint_dir) -> dict:
        value = metrics.get(self.monitor)
        if value is None:
            return {}

        if self._is_improvement(value):
            self.best_value = value
            path = Path(checkpoint_dir) / "best_model.pt"
            save_checkpoint(model, optimizer, epoch, str(path), metrics=metrics)
            logger.info(
                "Checkpoint guardado: %s mejoró a %.4f (epoch %d)",
                self.monitor, value, epoch,
            )

        return {}
