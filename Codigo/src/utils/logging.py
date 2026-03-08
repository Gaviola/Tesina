import logging
import sys
import time
from contextlib import contextmanager
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
    """Configura el root logger con salida a consola, archivo opcional y wandb opcional.

    Configura el root logger para que todos los módulos que usen
    logging.getLogger(__name__) hereden los handlers (consola + archivo).

    Args:
        name: Nombre de la ejecución (usado para el archivo de log y wandb).
        log_dir: Directorio para guardar el archivo de log. Si None, no se guarda archivo.
        level: Nivel de logging (default: INFO).
        use_wandb: Si True, inicializa wandb run.
        wandb_project: Nombre del proyecto wandb.
        wandb_entity: Entidad/equipo de wandb.
        wandb_config: Diccionario de configuración para wandb.

    Returns:
        Root logger configurado.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_dir is not None:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path / f"{name}.log")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Wandb
    if use_wandb and wandb is not None:
        wandb.init(
            project=wandb_project or "dermvlm",
            entity=wandb_entity,
            config=wandb_config or {},
            name=name,
        )
        root_logger.info("wandb inicializado: %s/%s", wandb_project, name)
    elif use_wandb and wandb is None:
        root_logger.warning("wandb no instalado, se omite tracking remoto")

    return root_logger


def log_metrics(metrics: dict, step: Optional[int] = None):
    """Loguea métricas a wandb si está activo."""
    if wandb is not None and wandb.run is not None:
        wandb.log(metrics, step=step)


def format_duration(seconds: float) -> str:
    """Formatea segundos en string legible: '12.34s', '1m 23.4s', '1h 23m 45s'."""
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {secs:.1f}s"
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {secs:.0f}s"


@contextmanager
def log_time(description: str, logger_instance: Optional[logging.Logger] = None):
    """Context manager que loguea duración de un bloque de código.

    Usage:
        with log_time("Cargando datos", logger):
            load_data()
        # Logs: "Cargando datos..."
        # Logs: "Cargando datos completado en 12.34s"
    """
    log = logger_instance or logging.getLogger()
    log.info("%s...", description)
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    log.info("%s completado en %s", description, format_duration(elapsed))
