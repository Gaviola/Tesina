import logging
import sys
from pathlib import Path
from typing import Optional

try:
    import wandb
except ImportError:
    wandb = None


def setup_logger(
    name: str,
    log_dir: Optional[str] = None,
    level: int = logging.INFO,
    use_wandb: bool = False,
    wandb_project: Optional[str] = None,
    wandb_entity: Optional[str] = None,
    wandb_config: Optional[dict] = None,
) -> logging.Logger:
    """Configura un logger con salida a consola, archivo opcional y wandb opcional.

    Args:
        name: Nombre del logger.
        log_dir: Directorio para guardar el archivo de log. Si None, no se guarda archivo.
        level: Nivel de logging (default: INFO).
        use_wandb: Si True, inicializa wandb run.
        wandb_project: Nombre del proyecto wandb.
        wandb_entity: Entidad/equipo de wandb.
        wandb_config: Diccionario de configuración para wandb.

    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_dir is not None:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path / f"{name}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Wandb
    if use_wandb and wandb is not None:
        wandb.init(
            project=wandb_project or "dermvlm",
            entity=wandb_entity,
            config=wandb_config or {},
            name=name,
        )
        logger.info("wandb inicializado: %s/%s", wandb_project, name)
    elif use_wandb and wandb is None:
        logger.warning("wandb no instalado, se omite tracking remoto")

    return logger


def log_metrics(metrics: dict, step: Optional[int] = None):
    """Loguea métricas a wandb si está activo."""
    if wandb is not None and wandb.run is not None:
        wandb.log(metrics, step=step)
