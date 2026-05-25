# RFC 03 — Bootstrap centralizado para scripts de entrenamiento y evaluación

**Fecha:** 2026-05-25
**Estado:** Propuesta arquitectónica
**Alcance:** scripts `train_*.py`, `generate_report.py`, `evaluate_*.py`

## Problema

Cada uno de los siete scripts ejecutables (`train_classifier.py`, `train_vlm_stage1.py`, `train_vlm_stage2.py`, `train_vlm_classify.py`, `generate_report.py`, `evaluate_reports.py`, `evaluate_classify.py`) duplica ≈80 líneas de prelude antes de hacer cualquier trabajo real:

- Inyección de `sys.path` para resolver `from src.`.
- Carga y `resolve` de Hydra/OmegaConf, merging de `overrides`.
- `set_seed(42)` sobre `random`, `numpy`, `torch`, `cuda`, `PYTHONHASHSEED`.
- Detección de device y dtype (`bf16` si SM ≥ 8.0, `fp32` si no).
- Creación del directorio de salida versionado `outputs/results/{model}/v{N}/`.
- Logger dual (consola + archivo, formato español).
- `check_training_dependencies()` (bitsandbytes, peft, transformers).
- `wandb.init(mode="offline", dir="outputs/wandb/")` con `cfg` snapshot.
- Dump del config a `out_dir/config.yaml` + `pip freeze` + git SHA.

Consecuencias:

- Cada cambio en la política de versionado o seeding requiere editar 7 archivos.
- Los smoke-tests no pueden correrse sin tocar `outputs/` real.
- wandb dispara siempre, incluso en runs de debug local.
- Cuando un script falla mid-run, ni siempre se llama `wandb.finish()` ni se escribe traceback al disco.

## Interfaz propuesta

Híbrido de "minimal" y "common-case": un único context manager con `Tracker` inyectable y flag `test_mode`.

```python
# Codigo/src/utils/bootstrap.py
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Literal, Protocol, Callable
import logging
import torch
from omegaconf import DictConfig

Role = Literal[
    "train_cls", "train_vlm_s1", "train_vlm_s2", "train_vlm_cls",
    "gen_report", "eval_report", "eval_cls"
]

class Tracker(Protocol):
    def log(self, data: dict, step: int | None = None) -> None: ...
    def finish(self, status: str = "ok") -> None: ...

@dataclass(frozen=True)
class RunContext:
    cfg: DictConfig
    device: torch.device
    dtype: torch.dtype
    out_dir: Path
    logger: logging.Logger
    tracker: Tracker
    seed: int
    role: Role

@contextmanager
def bootstrap(
    config_name: str,
    *,
    role: Role,
    overrides: list[str] | None = None,
    seed: int = 42,
    test_mode: bool = False,
    tracker_factory: Callable[[DictConfig, Path], Tracker] | None = None,
) -> Iterator[RunContext]: ...
```

### Ejemplo de uso

```python
# scripts/train_classifier.py — 6 líneas reales
from src.utils.bootstrap import bootstrap

with bootstrap("classifier_swin_v4", role="train_cls") as ctx:
    model = build_classifier(ctx.cfg).to(ctx.device, dtype=ctx.dtype)
    train_classifier(ctx.cfg, model, ctx)
```

```python
# Smoke-test local (sin wandb, sin tocar outputs/):
with bootstrap("classifier_swin_v4", role="train_cls", test_mode=True) as ctx:
    ...
```

```python
# Eval con overrides:
with bootstrap("eval_reports", role="eval_report",
               overrides=["dataset=hiba"]) as ctx:
    ...
```

### Complejidad que oculta

- `sys.path` injection desde `__file__`.
- `OmegaConf.load` + `.resolve()` + merge de overrides.
- `set_seed` completo (5 fuentes de aleatoriedad).
- Detección bf16 vs fp32 vía `torch.cuda.get_device_capability()`.
- Versionado `v{N}` por role/modelo (escanea existentes, `max + 1`).
- Logger dual con encoding UTF-8 y formato español.
- wandb offline init + dump de config + git SHA + `pip freeze` → `out_dir/env.txt`.
- Teardown: `tracker.finish()`, flush de handlers; on exception, escribe traceback a `out_dir/CRASH.txt` antes de relanzar.

## Estrategia de dependencias

**Categoría 1 — In-process** con I/O liviano (archivos en `out_dir`).

El único seam externo relevante es `Tracker`. La implementación de producción wrappea `wandb.Run`; la de tests es `NullTracker` (no-ops).

```python
class _WandbTracker:
    def __init__(self, cfg: DictConfig, out_dir: Path):
        import wandb
        self._run = wandb.init(
            mode="offline",
            dir=str(out_dir.parent.parent / "wandb"),
            project=cfg.wandb.project, name=out_dir.name,
            config=OmegaConf.to_container(cfg, resolve=True),
        )
    def log(self, data, step=None): self._run.log(data, step=step)
    def finish(self, status="ok"): self._run.finish(exit_code=0 if status == "ok" else 1)

class _NullTracker:
    def log(self, data, step=None): pass
    def finish(self, status="ok"): pass
```

`test_mode=True` corto-circuita:

- `out_dir = Path(tempfile.mkdtemp(prefix="tesina_test_"))`
- `tracker_factory = lambda *_: _NullTracker()`
- skip de `pip freeze`, git SHA, snapshot del config.
- corre en <100 ms.

Se descarta la propuesta "max flexibility" (SetupPipeline + 4 Protocols + Registry). DDP, TensorBoard, MLflow y Slack son hipotéticos. Cuando aparezcan, agregar un `Tracker` adicional o un parámetro `extra_init` puntual.

## Estrategia de testing

**Nuevos tests** (todos in-process, sin GPU, sin red):

- `bootstrap("classifier_swin_v4", role="train_cls", test_mode=True)` produce un `RunContext` con `out_dir` en tmp, `tracker` no-op, `seed=0`.
- Detección de dtype: con `torch.cuda` mockeado a `(8, 0)` retorna `bfloat16`; con `(7, 5)` retorna `float32`.
- Versionado: poblar `outputs/results/swin/v1`, `v2` → `bootstrap()` crea `v3`.
- En path de excepción: el manager escribe `CRASH.txt` y llama `tracker.finish(status="error")`.
- `overrides=["data.batch_size=8"]` se ve reflejado en `ctx.cfg.data.batch_size`.
- Snapshot del config se persiste a `out_dir/config.yaml`.

**Tests viejos a borrar:** ninguno.

**Necesidades de entorno:** sólo `pytest` + `pytest-tmp_path`. wandb no se instala en CI.

## Recomendaciones de implementación

Lo que el módulo `bootstrap` debe **poseer**:

- Política completa de seeding y reproducibilidad.
- Versionado de output dir.
- Política de logger (formato, sinks, niveles).
- Decisión de qué `Tracker` instanciar.
- Snapshot del entorno (config, git, pip).
- Teardown ordenado (incluso en excepción).

Lo que debe **ocultar**:

- Detalles internos de `wandb.init`.
- Cálculo de SM capability.
- Construcción del file handler.

Lo que debe **exponer**:

- `bootstrap(config_name, *, role, ...) -> RunContext`.
- `RunContext` como dataclass inmutable (frozen).
- `Tracker` Protocol para casos donde se quiera inyectar uno custom.

**Migración recomendada:**

1. Crear `src/utils/bootstrap.py` y migrar `train_classifier.py` primero. Comparar bit-exact contra una corrida v1.
2. Migrar los tres scripts VLM.
3. Migrar los tres scripts de evaluación (`gen_report`, `eval_report`, `eval_cls`).
4. Eliminar el código duplicado: `set_seed`, `_setup_logger`, `_next_iteration_dir` quedan sólo como helpers internos del módulo.
5. Documentar uso en `docs/USAGE.md`.

**Líneas estimadas ahorradas:** ≈ 7 × 80 − 200 (módulo nuevo) − 80 (tests) = **≈ 280 líneas netas**, pero el beneficio principal es consistencia y testabilidad, no LOC.

## Sincronización con clústeres

Introduce `src/utils/bootstrap.py` nuevo y reduce el código de los 7 scripts ejecutables. Antes del primer `submit`:

1. `python scripts/mendieta/sync_up.py` y `python scripts/toko/sync_up.py`.
2. La validación es **100% local** (`test_mode=True` corre en <100 ms). No hace falta enviar un job para verificar el refactor; alcanza con que los tests pasen y con un smoke run local de cada script reemplazado.
