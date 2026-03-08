import logging
import time
from typing import Any, Optional

import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

from src.utils.io import save_checkpoint
from src.utils.logging import format_duration, log_metrics

logger = logging.getLogger(__name__)


class Trainer:
    """Loop de entrenamiento genérico para clasificadores y VLMs.

    Soporta:
    - Train/val epochs con logging
    - Callbacks (early stopping, checkpointing)
    - Gradient accumulation
    - Mixed precision (AMP)
    - Wandb logging
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        scheduler: Optional[Any] = None,
        device: torch.device = torch.device("cpu"),
        dtype: torch.dtype = torch.float32,
        gradient_accumulation_steps: int = 1,
        max_epochs: int = 30,
        callbacks: Optional[list] = None,
        checkpoint_dir: str = "outputs/checkpoints",
    ):
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.scheduler = scheduler
        self.device = device
        self.dtype = dtype
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.max_epochs = max_epochs
        self.callbacks = callbacks or []
        self.checkpoint_dir = checkpoint_dir

        self.use_amp = dtype in (torch.float16, torch.bfloat16) and device.type == "cuda"
        self.scaler = torch.amp.GradScaler("cuda") if self.use_amp and dtype == torch.float16 else None

    def train_epoch(self, epoch: int) -> dict:
        """Ejecuta una época de entrenamiento."""
        self.model.train()
        total_loss = torch.zeros(1, device=self.device)
        num_batches = 0
        total_batches = len(self.train_loader)
        log_interval = max(10, total_batches // 5)
        epoch_start = time.perf_counter()

        self.optimizer.zero_grad()

        for batch_idx, batch in enumerate(self.train_loader):
            images = batch["image"].to(self.device, non_blocking=True)
            labels = batch["label"].to(self.device, non_blocking=True)

            with torch.amp.autocast("cuda", dtype=self.dtype, enabled=self.use_amp):
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss = loss / self.gradient_accumulation_steps

            if self.scaler is not None:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()

            if (batch_idx + 1) % self.gradient_accumulation_steps == 0:
                if self.scaler is not None:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()
                self.optimizer.zero_grad()

            total_loss += loss.detach() * self.gradient_accumulation_steps
            num_batches += 1

            if (batch_idx + 1) % log_interval == 0:
                avg_so_far = total_loss.item() / num_batches
                logger.info(
                    "  Batch %d/%d - loss: %.4f",
                    batch_idx + 1, total_batches, avg_so_far,
                )

        avg_loss = total_loss.item() / max(num_batches, 1)
        train_time = time.perf_counter() - epoch_start
        return {"train_loss": avg_loss, "train_time": train_time}

    @torch.no_grad()
    def validate(self, epoch: int) -> dict:
        """Ejecuta validación."""
        self.model.eval()
        total_loss = torch.zeros(1, device=self.device)
        total = 0
        all_preds_gpu = []
        all_labels_gpu = []
        val_start = time.perf_counter()

        for batch in self.val_loader:
            images = batch["image"].to(self.device, non_blocking=True)
            labels = batch["label"].to(self.device, non_blocking=True)

            with torch.amp.autocast("cuda", dtype=self.dtype, enabled=self.use_amp):
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)

            total_loss += loss
            preds = outputs.argmax(dim=1)
            all_preds_gpu.append(preds)
            all_labels_gpu.append(labels)
            total += labels.size(0)

        # Sincronización GPU→CPU única al final de la época
        all_preds = torch.cat(all_preds_gpu).cpu().tolist()
        all_labels = torch.cat(all_labels_gpu).cpu().tolist()
        correct = sum(p == l for p, l in zip(all_preds, all_labels))

        num_batches = len(self.val_loader)
        val_f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        val_time = time.perf_counter() - val_start
        return {
            "val_loss": total_loss.item() / max(num_batches, 1),
            "val_accuracy": correct / max(total, 1),
            "val_f1": val_f1,
            "val_time": val_time,
        }

    def fit(self) -> dict:
        """Ejecuta el loop de entrenamiento completo."""
        self.model.to(self.device)
        best_metrics = {}
        fit_start = time.perf_counter()

        for epoch in range(1, self.max_epochs + 1):
            train_metrics = self.train_epoch(epoch)
            val_metrics = self.validate(epoch)

            if self.scheduler is not None:
                self.scheduler.step()

            metrics = {**train_metrics, **val_metrics, "epoch": epoch}
            logger.info(
                "Epoch %d/%d - train_loss: %.4f - val_loss: %.4f - val_acc: %.4f - val_f1: %.4f [train: %s, val: %s]",
                epoch, self.max_epochs,
                metrics["train_loss"], metrics["val_loss"], metrics["val_accuracy"],
                metrics["val_f1"],
                format_duration(metrics["train_time"]),
                format_duration(metrics["val_time"]),
            )
            log_metrics(metrics, step=epoch)

            # Ejecutar callbacks
            stop = False
            for callback in self.callbacks:
                result = callback(epoch, metrics, self.model, self.optimizer, self.checkpoint_dir)
                if result and result.get("stop", False):
                    stop = True
                    break

            if stop:
                logger.info("Entrenamiento detenido por callback en epoch %d", epoch)
                break

            best_metrics = metrics

        total_time = time.perf_counter() - fit_start
        logger.info("Entrenamiento finalizado en %s (%d épocas)", format_duration(total_time), epoch)
        return best_metrics
