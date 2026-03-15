import logging
import time
from typing import Any, Optional

import torch
import torch.nn as nn
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader

from src.utils.io import save_checkpoint
from src.utils.logging import format_duration, log_gpu_memory, log_metrics

try:
    from tqdm import tqdm as _tqdm
    _TQDM_AVAILABLE = True
except ImportError:
    _TQDM_AVAILABLE = False

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
        total_loss    = torch.zeros(1, device=self.device)
        num_batches   = 0
        total_batches = len(self.train_loader)
        log_interval  = max(10, total_batches // 5)
        epoch_start   = time.perf_counter()

        self.optimizer.zero_grad()

        train_iter = _tqdm(
            self.train_loader,
            desc=f"Epoch {epoch}/{self.max_epochs} [train]",
            unit="batch", leave=False, dynamic_ncols=True,
        ) if _TQDM_AVAILABLE else self.train_loader
        batch_start = time.perf_counter()

        for batch_idx, batch in enumerate(train_iter):
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

            total_loss  += loss.detach() * self.gradient_accumulation_steps
            num_batches += 1

            if _TQDM_AVAILABLE:
                elapsed_b = time.perf_counter() - batch_start
                sps = (num_batches * images.size(0)) / max(elapsed_b, 1e-6)
                train_iter.set_postfix(
                    loss=f"{total_loss.item() / num_batches:.4f}",
                    sps=f"{sps:.1f}",
                    ordered=True,
                )

            if (batch_idx + 1) % log_interval == 0:
                elapsed   = time.perf_counter() - epoch_start
                done      = batch_idx + 1
                eta_epoch = (elapsed / done) * (total_batches - done)
                logger.info(
                    "  Epoch %d | Batch %d/%d | Loss: %.4f | Transcurrido: %s | ETA: %s",
                    epoch, done, total_batches,
                    total_loss.item() / num_batches,
                    format_duration(elapsed),
                    format_duration(eta_epoch),
                )

        if _TQDM_AVAILABLE:
            train_iter.close()

        avg_loss   = total_loss.item() / max(num_batches, 1)
        train_time = time.perf_counter() - epoch_start
        return {"train_loss": avg_loss, "train_time": train_time}

    @torch.no_grad()
    def validate(self, epoch: int) -> dict:
        """Ejecuta validación."""
        self.model.eval()
        total_loss     = torch.zeros(1, device=self.device)
        total          = 0
        all_preds_gpu  = []
        all_labels_gpu = []
        val_start      = time.perf_counter()

        val_iter = _tqdm(
            self.val_loader,
            desc=f"Epoch {epoch}/{self.max_epochs} [val]  ",
            unit="batch", leave=False, dynamic_ncols=True,
        ) if _TQDM_AVAILABLE else self.val_loader

        for batch in val_iter:
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

            if _TQDM_AVAILABLE:
                val_iter.set_postfix(
                    loss=f"{total_loss.item() / len(all_preds_gpu):.4f}", ordered=True,
                )

        if _TQDM_AVAILABLE:
            val_iter.close()

        # Sincronización GPU→CPU única al final de la época
        all_preds  = torch.cat(all_preds_gpu).cpu().tolist()
        all_labels = torch.cat(all_labels_gpu).cpu().tolist()
        correct    = sum(p == l for p, l in zip(all_preds, all_labels))

        num_batches = len(self.val_loader)
        val_f1      = f1_score(all_labels, all_preds, average="weighted", zero_division=0)
        val_time    = time.perf_counter() - val_start
        return {
            "val_loss":     total_loss.item() / max(num_batches, 1),
            "val_accuracy": correct / max(total, 1),
            "val_f1":       val_f1,
            "val_time":     val_time,
        }

    def fit(self) -> dict:
        """Ejecuta el loop de entrenamiento completo."""
        self.model.to(self.device)
        best_metrics  = {}
        best_val_loss = float("inf")
        fit_start     = time.perf_counter()
        epoch_times   = []

        logger.info(
            "=== Configuración del entrenamiento ===\n"
            "  Épocas        : %d\n"
            "  Train batches : %d | Val batches: %d\n"
            "  Grad accum    : %d\n"
            "  Dispositivo   : %s | dtype: %s\n"
            "  Checkpoint    : %s",
            self.max_epochs,
            len(self.train_loader), len(self.val_loader),
            self.gradient_accumulation_steps,
            self.device, self.dtype,
            self.checkpoint_dir,
        )

        for epoch in range(1, self.max_epochs + 1):
            train_metrics = self.train_epoch(epoch)
            val_metrics   = self.validate(epoch)

            if self.scheduler is not None:
                self.scheduler.step()

            metrics = {**train_metrics, **val_metrics, "epoch": epoch}
            epoch_times.append(train_metrics["train_time"] + val_metrics["val_time"])
            avg_epoch_t   = sum(epoch_times) / len(epoch_times)
            eta_remaining = avg_epoch_t * (self.max_epochs - epoch)

            logger.info(
                "Epoch %d/%d — train_loss: %.4f | val_loss: %.4f | "
                "val_acc: %.4f | val_f1: %.4f | [train: %s, val: %s] | ETA: %s",
                epoch, self.max_epochs,
                metrics["train_loss"], metrics["val_loss"],
                metrics["val_accuracy"], metrics["val_f1"],
                format_duration(metrics["train_time"]),
                format_duration(metrics["val_time"]),
                format_duration(eta_remaining),
            )
            log_metrics(metrics, step=epoch)
            log_gpu_memory(logger, prefix=f"Epoch {epoch}/{self.max_epochs} | ")

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

            if metrics["val_loss"] < best_val_loss:
                best_val_loss = metrics["val_loss"]
                best_metrics  = metrics

        total_time  = time.perf_counter() - fit_start
        avg_epoch_t = sum(epoch_times) / max(len(epoch_times), 1)
        logger.info(
            "=== Resumen de entrenamiento ===\n"
            "  Tiempo total      : %s\n"
            "  Épocas completadas: %d / %d\n"
            "  Tiempo por época  : %s (promedio)\n"
            "  Mejor época       : %s\n"
            "  Mejor val_loss    : %.4f | val_acc: %.4f | val_f1: %.4f",
            format_duration(total_time),
            len(epoch_times), self.max_epochs,
            format_duration(avg_epoch_t),
            best_metrics.get("epoch", "?"),
            best_metrics.get("val_loss", float("nan")),
            best_metrics.get("val_accuracy", float("nan")),
            best_metrics.get("val_f1", float("nan")),
        )
        logger.info(
            "Entrenamiento finalizado en %s (%d épocas)",
            format_duration(total_time), epoch,
        )
        return best_metrics
