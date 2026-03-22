import os

import torch


def get_device() -> torch.device:
    """Selecciona el dispositivo disponible (CUDA > CPU)."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_training_dtype() -> torch.dtype:
    """Selecciona dtype óptimo según la GPU disponible.

    - Ampere+/Ada+ (SM >= 8.0): bf16 (Tensor Cores)
    - Pre-Ampere (SM < 8.0): fp32 (sin Tensor Cores)
    - Sin GPU: fp32
    """
    if not torch.cuda.is_available():
        return torch.float32
    capability = torch.cuda.get_device_capability()
    if capability[0] >= 8:  # Ampere+/Ada+ (A30, RTX 4070, RTX 4080)
        return torch.bfloat16
    else:  # Pre-Ampere (SM < 8.0)
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


def get_free_vram_gb() -> float:
    """Retorna la VRAM libre actual de la GPU en GB. Retorna 0 si no hay GPU.

    Usa torch.cuda.mem_get_info() que consulta al driver CUDA la memoria
    realmente disponible, incluyendo lo no reservado por PyTorch.
    Más preciso que memory_reserved() para detectar OOM inminentes.
    """
    if not torch.cuda.is_available():
        return 0.0
    try:
        free_bytes, _ = torch.cuda.mem_get_info(0)
        return free_bytes / (1024 ** 3)
    except Exception:
        return 0.0


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


def estimate_vlm_batch_size(
    model_type: str,
    free_vram_gb: float,
    num_crops: int = 4,
    grad_checkpointing: bool = True,
) -> int:
    """Estima un batch size seguro para entrenamiento de VLMs según VRAM libre.

    Heurística basada en mediciones empíricas:
    - Mini-VLM (Phi-3.5-vision): cada muestra con num_crops+1 crops de 336x336,
      seq_len=2048, bf16, con gradient checkpointing: ~0.8-1.2 GB por muestra.
    - LLaVA-Med: ~1.5 GB por muestra (bf16, con grad ckpt).

    Args:
        model_type: "mini_vlm" o "llava_med".
        free_vram_gb: VRAM libre en GB tras cargar el modelo.
        num_crops: Número de crops del procesador de Phi-3.5 (default 4).
        grad_checkpointing: Si gradient checkpointing está activo.

    Returns:
        Batch size estimado (mínimo 1, máximo 16).
    """
    if free_vram_gb <= 0:
        return 1

    if model_type == "mini_vlm":
        # Phi-3.5-vision: pixel_values son (batch, num_crops+1, 3, 336, 336)
        per_sample_gb = 0.8 if grad_checkpointing else 1.8
        # Escalar con num_crops (normalizado a 5 crops totales como referencia)
        total_crops = num_crops + 1
        per_sample_gb *= total_crops / 5
    else:  # llava_med
        per_sample_gb = 1.5 if grad_checkpointing else 2.5

    # Dejar 0.5 GB de margen para estados del optimizador y fragmentación
    usable_vram = max(0, free_vram_gb - 0.5)
    batch_size = int(usable_vram / per_sample_gb)

    return max(1, min(16, batch_size))


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


def check_training_dependencies(model_type: str, quantize: bool) -> dict:
    """Verificación pre-flight de dependencias para entrenamiento de VLMs.

    Comprueba que las librerías requeridas están instaladas y funcionales
    ANTES de intentar cargar el modelo, para detectar errores temprano.

    Args:
        model_type: "llava_med" o "mini_vlm".
        quantize: Si se planea usar cuantización 4-bit.

    Returns:
        Dict con claves:
        - bitsandbytes (bool): disponible y funcional
        - sdpa (bool): scaled_dot_product_attention disponible
        - warnings (list[str]): problemas detectados
    """
    import logging

    logger = logging.getLogger(__name__)
    result = {"bitsandbytes": False, "sdpa": False, "warnings": []}

    # --- sdpa (PyTorch 2.0+) ---
    result["sdpa"] = hasattr(torch.nn.functional, "scaled_dot_product_attention")
    if not result["sdpa"]:
        result["warnings"].append(
            "torch.nn.functional.scaled_dot_product_attention no disponible. "
            "Se requiere PyTorch >= 2.0."
        )

    # --- bitsandbytes (solo si se necesita cuantización) ---
    if quantize:
        try:
            import bitsandbytes as bnb
            if getattr(bnb, "cextension", None) is not None and bnb.cextension.lib is not None:
                result["bitsandbytes"] = True
            else:
                result["warnings"].append(
                    "bitsandbytes importado pero CUDA backend no funcional "
                    "(lib es None). Verificar compatibilidad CUDA."
                )
        except ImportError:
            result["warnings"].append(
                "bitsandbytes no instalado. Cuantización 4-bit no disponible."
            )
        except Exception as exc:
            result["warnings"].append(
                f"Error al verificar bitsandbytes: {exc}"
            )
    else:
        result["bitsandbytes"] = True  # No se necesita

    # --- Info de entorno ---
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        capability = torch.cuda.get_device_capability(0)
        cuda_version = torch.version.cuda or "desconocida"
        logger.info(
            "Pre-flight: GPU=%s (SM %d.%d) | CUDA=%s | PyTorch=%s | "
            "sdpa=%s | bitsandbytes=%s | cuantización=%s",
            gpu_name, capability[0], capability[1], cuda_version,
            torch.__version__, result["sdpa"], result["bitsandbytes"], quantize,
        )
    else:
        logger.info("Pre-flight: sin GPU detectada")

    for warn in result["warnings"]:
        logger.warning("Pre-flight: %s", warn)

    return result
