import os
import random

import numpy as np
import torch


def set_seed(seed: int = 42):
    """Establece semillas para reproducibilidad en todas las fuentes de aleatoriedad.

    Configura determinismo según la GPU disponible:
    - Ampere+ (SM >= 8.0): activa CUBLAS_WORKSPACE_CONFIG y deterministic algorithms
    - Pascal y anteriores: solo seeds básicas (no soporta determinismo completo)
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True

    if torch.cuda.is_available():
        capability = torch.cuda.get_device_capability()
        if capability[0] >= 8:
            os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            try:
                torch.use_deterministic_algorithms(True)
            except RuntimeError:
                # Algunas ops (scatter_add, interpolación) no tienen implementación determinística
                torch.use_deterministic_algorithms(True, warn_only=True)
