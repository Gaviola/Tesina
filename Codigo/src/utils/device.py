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


def get_gpu_info() -> dict:
    """Retorna información de la GPU disponible."""
    if not torch.cuda.is_available():
        return {"available": False}
    return {
        "available": True,
        "name": torch.cuda.get_device_name(0),
        "capability": torch.cuda.get_device_capability(0),
        "memory_total_gb": torch.cuda.get_device_properties(0).total_mem / (1024**3),
        "dtype": str(get_training_dtype()),
    }
