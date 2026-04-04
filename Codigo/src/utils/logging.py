import logging
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import torch

try:
    import wandb
except ImportError:
    wandb = None

try:
    from tqdm import tqdm as _tqdm
    _TQDM_AVAILABLE = True
except ImportError:
    _TQDM_AVAILABLE = False


class TqdmLoggingHandler(logging.StreamHandler):
    """StreamHandler que usa tqdm.write() para no corromper barras de progreso.

    Cuando tqdm dibuja una barra en la consola, cualquier escritura directa a
    stdout rompe visualmente la barra. tqdm.write() pausa la barra, imprime la
    línea y la reanuda correctamente. El file handler no se ve afectado.
    """

    def __init__(self):
        super().__init__(sys.stdout)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            if _TQDM_AVAILABLE:
                _tqdm.write(msg)
            else:
                sys.stdout.write(msg + self.terminator)
                self.flush()
        except Exception:
            self.handleError(record)


def setup_logger(
    name: str,
    log_dir: Optional[str] = None,
    level: int = logging.INFO,
    use_wandb: bool = False,
    wandb_project: Optional[str] = None,
    wandb_entity: Optional[str] = None,
    wandb_config: Optional[dict] = None,
    wandb_mode: str = "offline",
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
        wandb_mode: Modo de wandb: "offline" (default, para clusters sin internet),
                    "online" (requiere conexión), "disabled" (sin tracking).
                    En modo offline los runs se guardan localmente y se sincronizan
                    después con `wandb sync <run_dir>`.

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

    # Console handler (usa tqdm.write para no romper barras de progreso)
    console_handler = TqdmLoggingHandler()
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
            mode=wandb_mode,
        )
        root_logger.info(
            "wandb inicializado: proyecto=%s | run=%s | modo=%s",
            wandb_project, name, wandb_mode,
        )
        if wandb_mode == "offline":
            root_logger.info(
                "wandb offline: runs guardados en %s — sincronizar después con: wandb sync %s",
                wandb.run.dir,
                str(Path(wandb.run.dir).parent),
            )
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


def log_gpu_memory(
    logger_instance: Optional[logging.Logger] = None,
    prefix: str = "",
) -> dict:
    """Loguea uso de VRAM si CUDA está disponible.

    Args:
        logger_instance: Logger a usar. Si None, usa el root logger.
        prefix: Prefijo para el mensaje (e.g., "Época 2/5 | ").

    Returns:
        Dict con allocated_mb y reserved_mb (0.0 si no hay CUDA).
    """
    log = logger_instance or logging.getLogger()
    if not torch.cuda.is_available():
        return {"allocated_mb": 0.0, "reserved_mb": 0.0}
    allocated_mb = torch.cuda.memory_allocated() / 1024 ** 2
    reserved_mb  = torch.cuda.memory_reserved()  / 1024 ** 2
    log.info(
        "%sVRAM: %.0f MB asignada / %.0f MB reservada",
        prefix, allocated_mb, reserved_mb,
    )
    mem = {"vram_allocated_mb": allocated_mb, "vram_reserved_mb": reserved_mb}
    if wandb is not None and wandb.run is not None:
        wandb.log(mem)
    return {"allocated_mb": allocated_mb, "reserved_mb": reserved_mb}


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
