import os

import torch


def get_device() -> torch.device:
    """Selecciona el dispositivo disponible (CUDA > CPU)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_training_dtype() -> torch.dtype:
    """Selecciona dtype óptimo según la GPU disponible.

    - Ampere+ (SM >= 8.0): bf16 (Tensor Cores 3ra gen)
    - Pascal y anteriores: fp32 (sin Tensor Cores)
    - Sin GPU: fp32
    """
    if not torch.cuda.is_available():
        return torch.float32
    capability = torch.cuda.get_device_capability()
    if capability[0] >= 8:  # Ampere+ (A30, RTX 4070)
        return torch.bfloat16
    else:  # Pascal (Titan Xp) y anteriores
        return torch.float32


def get_num_workers() -> int:
    """Retorna número óptimo de workers para DataLoader según el hardware disponible.

    - En clusters SLURM: usa SLURM_CPUS_PER_TASK menos 1 para el proceso principal.
    - En local: usa cpu_count() // 2, mínimo 4 y máximo 8.
    """
    slurm_cpus = os.environ.get("SLURM_CPUS_PER_TASK")
    if slurm_cpus is not None:
        return max(1, int(slurm_cpus) - 1)
    cpu_count = os.cpu_count() or 1
    return min(8, max(4, cpu_count // 2))


def get_vram_gb() -> float:
    """Retorna la VRAM total de la GPU en GB. Retorna 0 si no hay GPU."""
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.get_device_properties(0).total_memory / (1024**3)


def check_vram(required_gb: float, model_name: str = "") -> bool:
    """Verifica si la VRAM disponible es suficiente para el modelo.

    Args:
        required_gb: VRAM requerida en GB.
        model_name: Nombre del modelo (para mensajes de log).

    Returns:
        True si hay suficiente VRAM, False si no.
    """
    import logging

    logger = logging.getLogger(__name__)
    vram = get_vram_gb()

    if vram == 0:
        logger.warning("No se detectó GPU. El modelo %s requiere %.1fGB de VRAM", model_name, required_gb)
        return False

    if vram < required_gb:
        logger.warning(
            "VRAM insuficiente para %s: %.1fGB disponible, %.1fGB requerida. "
            "Se recomienda cuantización 4-bit (--quantize)",
            model_name, vram, required_gb,
        )
        return False

    logger.info("VRAM verificada: %.1fGB disponible, %.1fGB requerida para %s", vram, required_gb, model_name)
    return True


def get_gpu_info() -> dict:
    """Retorna información de la GPU disponible."""
    if not torch.cuda.is_available():
        return {"available": False}
    return {
        "available": True,
        "name": torch.cuda.get_device_name(0),
        "capability": torch.cuda.get_device_capability(0),
        "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
        "dtype": str(get_training_dtype()),
    }
