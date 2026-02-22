import json
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import torch


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    epoch: int,
    path: str,
    metrics: Optional[dict] = None,
    **extra,
):
    """Guarda checkpoint del modelo con estado del optimizer y métricas.

    Args:
        model: Modelo a guardar.
        optimizer: Optimizer a guardar.
        epoch: Época actual.
        path: Ruta del archivo .pt.
        metrics: Métricas del checkpoint (e.g., val_loss, val_f1).
        **extra: Datos adicionales a guardar.
    """
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    state = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "metrics": metrics or {},
        **extra,
    }
    torch.save(state, checkpoint_path)


def load_checkpoint(
    path: str,
    model: Optional[torch.nn.Module] = None,
    optimizer: Optional[torch.optim.Optimizer] = None,
    device: str = "cpu",
) -> dict:
    """Carga checkpoint y opcionalmente restaura modelo y optimizer.

    Args:
        path: Ruta del archivo .pt.
        model: Si se pasa, se restaura el state_dict.
        optimizer: Si se pasa, se restaura el state_dict.
        device: Dispositivo donde cargar los tensores.

    Returns:
        Diccionario con toda la información del checkpoint.
    """
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    if model is not None:
        model.load_state_dict(checkpoint["model_state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    return checkpoint


def save_results(data: Any, path: str):
    """Guarda resultados como CSV (si es DataFrame/dict) o JSON.

    Args:
        data: DataFrame, dict, o lista de dicts.
        path: Ruta del archivo de salida (.csv o .json).
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix == ".csv":
        if isinstance(data, pd.DataFrame):
            data.to_csv(output_path, index=False)
        elif isinstance(data, (dict, list)):
            pd.DataFrame(data).to_csv(output_path, index=False)
    elif output_path.suffix == ".json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        raise ValueError(f"Formato no soportado: {output_path.suffix}. Usar .csv o .json")


def load_results(path: str) -> Any:
    """Carga resultados desde CSV o JSON."""
    filepath = Path(path)
    if filepath.suffix == ".csv":
        return pd.read_csv(filepath)
    elif filepath.suffix == ".json":
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Formato no soportado: {filepath.suffix}")
