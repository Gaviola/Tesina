# RFC 02 — Refactor del entrenador y pipeline two-stage VLM

**Fecha:** 2026-05-25
**Estado:** Propuesta arquitectónica
**Alcance:** `Codigo/src/training/`, scripts `train_classifier.py`, `train_vlm_stage{1,2}.py`, `train_vlm_classify.py`

## Problema

El módulo `src/training/` es el cuello de botella más profundo del repo:

- `trainer.py` (304 líneas): `Trainer` con constructor de 12+ argumentos, no inyectable; testearlo requiere armar dataloaders y modelos completos.
- `two_stage.py` (**1456 líneas**): re-implementa el loop de entrenamiento (AMP, grad accum, val) en vez de reusar `Trainer`. Las decisiones específicas por etapa (qué capas congelar, qué loss, qué guardar en el checkpoint, política de recovery por OOM) están enterradas dentro de `run_stage1()` / `run_stage2()`.
- Las transiciones Stage1 → Stage2 (cargar `best_model.pt` de Stage1, agregar LoRA sobre el LLM, redefinir grupos de optimización) las orquestan los scripts manualmente.
- No hay tests unitarios. Un bug de freezing en Stage2 sólo se descubre tras un job de 8-12 hs en cluster.

Acoplamientos críticos:

- `Trainer` y `two_stage` duplican la lógica de `autocast` + `GradScaler` + grad accumulation.
- El "payload" del checkpoint varía por etapa (state_dict completo / sólo proyección / sólo adaptadores LoRA + proyección) pero `CheckpointCallback` no lo sabe; cada etapa lo serializa a mano.
- `VLMOOMError` + reintento con batch reducido vive como caso especial dentro de `two_stage.py`, no reutilizable.

## Interfaz propuesta

Híbrido de "minimal" (un único `train(spec)`) y "common-case" (wrappers por flujo) — el camino feliz es trivial, el avanzado existe sin romper la API.

```python
# Codigo/src/training/api.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal, Protocol
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

Mode = Literal["classifier", "vlm_stage1", "vlm_stage2"]

class LossFn(Protocol):
    def __call__(self, model: nn.Module, batch: dict) -> torch.Tensor: ...

@dataclass
class TrainSpec:
    mode: Mode
    model: nn.Module
    train_loader: DataLoader
    val_loader: DataLoader
    loss_fn: LossFn
    max_epochs: int
    out_dir: Path                              # outputs/checkpoints/<run_name>/
    lr: float = 1e-4
    grad_accum: int = 1
    amp_dtype: torch.dtype | None = torch.bfloat16
    init_from: Path | None = None              # checkpoint Stage1 para Stage2
    extra: dict = field(default_factory=dict)  # lora_r, freeze_pattern, etc.

@dataclass
class TrainResult:
    best_ckpt: Path
    best_metric: float
    history: list[dict]

def train(spec: TrainSpec) -> TrainResult: ...   # seam de bajo nivel

# Wrappers de alto nivel — los scripts usan estos
def train_classifier(cfg) -> TrainResult: ...
def train_vlm_two_stage(cfg, *, skip_stage1: bool = False,
                        stage1_ckpt: Path | None = None) -> TrainResult: ...
```

### Ejemplo de uso

Los cuatro scripts colapsan a ≈10 líneas:

```python
# scripts/train_vlm.py
import hydra
from src.training.api import train_vlm_two_stage

@hydra.main(config_path="../configs", config_name="vlm_mini")
def main(cfg):
    train_vlm_two_stage(cfg)

if __name__ == "__main__":
    main()
```

`train_vlm_two_stage` internamente:

1. Llama `train(TrainSpec(mode="vlm_stage1", ...))`.
2. Captura `result.best_ckpt`.
3. Construye `TrainSpec(mode="vlm_stage2", init_from=result.best_ckpt, extra={"lora_r": cfg.lora.r, ...})`.
4. Vuelve a llamar `train(...)`.

Para una ablación atípica (Stage1 solo, o Stage2 reentrenado), el script usa `train(TrainSpec(...))` directo. Para experimentos exóticos (Stage3, schedule custom de freezing) queda la opción de heredar de `Trainer` o agregar un nuevo `Mode`.

### Complejidad que oculta

- Autocast + GradScaler.
- Gradient accumulation.
- Recovery por OOM (`VLMOOMError`): reintenta una vez con `batch_size //= 2` y `grad_accum *= 2`, loggea fallback a wandb.
- Congelamiento de capas por modo (Stage1: sólo proyección; Stage2: LoRA en LLM + proyección).
- Payload del checkpoint por modo (state_dict / projection_only / adapters + projection).
- Versionado del directorio (`stage{1,2}_{model}_v{N}/` con `N = max(existentes) + 1`).
- Resume defensivo (lee `last.pt` si existe).

## Estrategia de dependencias

**Categoría 1 — In-process.** Sin puertos externos: todo es PyTorch puro.

No hace falta DI ni adaptadores. La estrategia de testing es directa:

- **Test "smoke"**: `nn.Linear(8, 4)` + `TensorDataset` de 16 samples + `loss_fn=lambda m,b: m(b["x"]).pow(2).mean()`. Corre en CPU en <2s.
- **Recipe especial** `recipes.small` para VLM: un VLM mínimo (CLIP-ViT-Tiny + Phi-3-mini-quantized) que cabe en 4GB y verifica el end-to-end Stage1→Stage2 en <60s.

## Estrategia de testing

**Nuevos tests de borde a escribir** (todos in-process, sin GPU):

- `train(TrainSpec(mode="classifier", ...))` retorna `best_ckpt` existente y `best_metric` mejora monotónicamente en early stop.
- `train(mode="vlm_stage1")` guarda **sólo** los pesos de proyección en el checkpoint (assert sobre keys del `state_dict`).
- `train(mode="vlm_stage2", init_from=<ckpt_stage1>)` carga la proyección y guarda adapters + proyección.
- `train_vlm_two_stage(cfg)` produce dos directorios versionados consistentes y el segundo checkpoint contiene referencia al primero.
- Recovery por OOM: simular `torch.cuda.OutOfMemoryError` con un hook → verificar que reintenta con batch/accum ajustados y loggea evento.
- Versionado: si existe `v1/` y `v2/`, el nuevo run crea `v3/`.

**Tests viejos a borrar:** ninguno (no había).

**Necesidades de entorno:** ninguna. Toda la batería corre en CI sin GPU.

## Recomendaciones de implementación

Lo que `src/training/api.py` debe **poseer**:

- Selección de modo y dispatch a `_runner_<mode>`.
- Recovery por OOM y AMP scaler.
- Versionado automático de `out_dir`.
- Resume desde `last.pt`.
- Política de checkpoint payload por modo.

Lo que debe **ocultar**:

- Detalles de PEFT/LoRA wiring.
- Construcción de optimizer groups por modo.
- Bookkeeping de scheduler, métricas, callbacks.

Lo que debe **exponer**:

- `train(spec)` como seam canónico.
- `train_classifier(cfg)` y `train_vlm_two_stage(cfg)` como atajos para los scripts.
- `Trainer` y `run_stage1/2` permanecen públicos durante una etapa de transición (deprecation warnings).

**Migración recomendada:**

1. Crear `src/training/api.py` con `train()` y los wrappers. Implementar `_runner_classifier` reutilizando `Trainer` actual.
2. Implementar `_runner_vlm_stage1` y `_runner_vlm_stage2` extrayendo lógica de `two_stage.py`. Aislar el OOM recovery en un decorator `@with_oom_retry`.
3. Migrar `train_classifier.py` primero (sin riesgo). Validar paridad numérica contra una corrida v1.
4. Migrar `train_vlm_stage1.py` y `train_vlm_stage2.py` a `train_vlm_two_stage`.
5. Borrar `two_stage.py` y reducir `trainer.py` a ≈150 líneas (sólo el loop genérico, sin OOM ni stage-specific).
6. Mantener `Trainer` exportado en `__init__.py` con `DeprecationWarning` por una iteración.

**Líneas estimadas ahorradas:** ≈1100 (de ≈1900 entre `trainer.py` + `two_stage.py` a ≈800 incluyendo `api.py` + tests).

## Sincronización con clústeres

Este refactor introduce un módulo nuevo (`src/training/api.py`) y elimina `two_stage.py`. **Antes** del primer `submit` con el código nuevo:

1. `python scripts/mendieta/sync_up.py --delete` (Mendieta tiene NFS persistente; sin `--delete` quedaría `two_stage.py` huérfano y los scripts viejos podrían seguir importándolo).
2. `python scripts/toko/sync_up.py` (TOKO regenera el scratch, no requiere `--delete`).
3. Registrar el commit hash y el sync en `docs/ejecuciones.md`.

Paridad bit-exact de Stage 2 requiere cluster (≈10 hs en A30); paridad de clasificador y smoke de 1 epoch del Stage 2 se hacen en RTX 4070 local.
