# RFC 05 — Loader VLM con puertos y adaptadores

**Fecha:** 2026-05-25
**Estado:** Propuesta arquitectónica
**Alcance:** `Codigo/src/models/vlm_base.py`, `llava_med.py`, `mini_vlm.py`, `factory.py`, y los callers en `train_vlm_*.py` y `generate_report.py`

## Problema

La capa VLM tiene tres síntomas concretos:

1. **Acoplamiento del loader a `src/utils/device.py`.** Tanto `llava_med.py:load_components()` como `mini_vlm.py:load_components()` llaman a `get_free_vram_gb()` para decidir 4-bit / 8-bit / fp16 / bf16 y arman `device_map`. Esto cruza la frontera modelo → utils y no es testeable sin GPU.

2. **`VLMBase` demasiado abstracto.** Los scripts importan concretos (`from src.models.llava_med import LLaVAMed`) en vez de usar `factory.create(name)`, porque `VLMBase.encode_image()` es `NotImplementedError` y no se sabe qué métodos están disponibles. El factory es declarativo pero los call-sites no lo respetan.

3. **Bug latente en detección de LoRA.** `generate_report.py:78-94` deduce el rango `r` del LoRA inspeccionando shapes de tensores porque no se escribe metadata al guardar el checkpoint. Si la shape se interpreta mal, se carga un LoRA con rango incorrecto y la generación silenciosamente degrada.

4. **Templating duplicado.** Cada script ensambla el chat template inline. LLaVA-Med usa `<image>\nUSER: ... ASSISTANT:`; Mini-VLM usa el chat template de Phi-3.5. Duplicado en 3-4 archivos.

5. **No hay tests.** Cualquier cambio requiere ejecutar en cluster con descarga de pesos (≈14 GB LLaVA-Med, ≈8 GB Mini-VLM).

## Interfaz propuesta

**Puertos y adaptadores** (categoría 4 — true external mock). El puerto es la interfaz pública; un adaptador HF para producción, uno fake para tests.

```python
# Codigo/src/models/ports.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
import torch

@dataclass(frozen=True)
class LoadSpec:
    model_id: str                              # "microsoft/llava-med-v1.5-mistral-7b"
    dtype: torch.dtype = torch.bfloat16
    quantization: str | None = None            # "4bit" | "8bit" | None | "auto"
    device_map: str | dict = "auto"
    lora_checkpoint: Path | None = None

@dataclass(frozen=True)
class LoraSpec:
    r: int
    alpha: int
    dropout: float
    target_modules: tuple[str, ...]

@dataclass
class LoadedVLM:
    model: torch.nn.Module
    processor: Any                             # opaco para callers
    metadata: dict                             # {family, vram_mb, lora: LoraSpec|None, prompt_template}

@runtime_checkable
class VLMPort(Protocol):
    family: str                                # "llava_med" | "mini_vlm"

    def load(self, spec: LoadSpec) -> LoadedVLM: ...
    def prepare_inputs(self, vlm: LoadedVLM, image, prompt: str) -> dict: ...
    def generate(self, vlm: LoadedVLM, inputs: dict, **gen_kwargs) -> str: ...
    def forward_train(self, vlm: LoadedVLM, batch: dict) -> torch.Tensor: ...

    def attach_lora(self, vlm: LoadedVLM, lora: LoraSpec) -> LoadedVLM: ...
    def save_lora(self, vlm: LoadedVLM, out_dir: Path) -> None: ...   # escribe lora_config.json
    def load_lora(self, vlm: LoadedVLM, ckpt_dir: Path) -> LoadedVLM: ...  # lee metadata, NO sniffing
```

### Ejemplo de uso

```python
# scripts/generate_report.py
from src.models.factory import get_vlm_port
from src.models.ports import LoadSpec

port = get_vlm_port(cfg.model.name)            # devuelve HFVLMAdapter por defecto
vlm = port.load(LoadSpec(
    model_id=cfg.model.repo,
    quantization="4bit" if cfg.low_vram else None,
    lora_checkpoint=cfg.ckpt,
))

for image, prompt in samples:
    inputs = port.prepare_inputs(vlm, image, prompt)
    report = port.generate(vlm, inputs, max_new_tokens=256)
```

```python
# tests/test_generate_report.py
def test_lora_metadata_roundtrip(tmp_path):
    port = FakeVLMAdapter()
    vlm = port.load(LoadSpec(model_id="fake"))
    vlm = port.attach_lora(vlm, LoraSpec(r=16, alpha=32, dropout=0.0,
                                          target_modules=("q_proj", "v_proj")))
    port.save_lora(vlm, tmp_path)

    fresh = port.load(LoadSpec(model_id="fake"))
    fresh = port.load_lora(fresh, tmp_path)
    assert fresh.metadata["lora"] == vlm.metadata["lora"]   # sin shape sniffing
```

### Complejidad que oculta

- **VRAM probe + decisión de quantization** → dentro de `HFVLMAdapter.load()` cuando `spec.quantization == "auto"`. Los scripts ya no importan `get_free_vram_gb`.
- **`device_map` para 4080 16GB vs A30 24GB** → adaptador.
- **Chat templates por familia** → registro interno (`PROMPT_TEMPLATES[family]`), no en el script.
- **PEFT wiring** → `attach_lora` + `save_lora` (escribe `lora_config.json` con `(r, alpha, dropout, target_modules)`) + `load_lora` (lee metadata, **mata el bug de shape inference**).
- **`processor()` plumbing** → `prepare_inputs`.

## Estrategia de dependencias

**Categoría 4 — True external (Mock).** HuggingFace Hub y `transformers` son terceros que no controlamos.

- **Puerto:** `VLMPort` (definido arriba).
- **Adaptador de producción:** `HFVLMAdapter(family)`:
  ```python
  class HFVLMAdapter:
      def __init__(self, family: str):
          self._family = family
          self._template = PROMPT_TEMPLATES[family]
      def load(self, spec):
          bnb = _build_bnb_config(spec.quantization)
          model = AutoModelForVision2Seq.from_pretrained(
              spec.model_id, quantization_config=bnb,
              device_map=spec.device_map, torch_dtype=spec.dtype,
          )
          processor = AutoProcessor.from_pretrained(spec.model_id)
          meta = {"family": self._family,
                  "vram_mb": _measure_vram(model),
                  "lora": None,
                  "prompt_template": self._template.name}
          loaded = LoadedVLM(model, processor, meta)
          if spec.lora_checkpoint:
              loaded = self.load_lora(loaded, spec.lora_checkpoint)
          return loaded
      def save_lora(self, vlm, out_dir):
          vlm.model.save_pretrained(out_dir)   # PEFT escribe los pesos
          (out_dir / "lora_config.json").write_text(
              json.dumps(asdict(vlm.metadata["lora"])))
      def load_lora(self, vlm, ckpt_dir):
          spec = LoraSpec(**json.loads((ckpt_dir / "lora_config.json").read_text()))
          vlm.model = PeftModel.from_pretrained(vlm.model, ckpt_dir)
          vlm.metadata["lora"] = spec
          return vlm
      # prepare_inputs, generate, forward_train, attach_lora análogos
  ```
- **Adaptador de tests:** `FakeVLMAdapter` con un `nn.Sequential(nn.Linear(8,8), nn.Linear(8,8))`, `processor` no-op que devuelve `{"input_ids": torch.zeros(1, 4)}`, `generate` retorna `"FAKE_REPORT"`. Implementa `attach_lora/save_lora/load_lora` con el mismo formato `lora_config.json`.

Se descarta la propuesta "max flexibility" (registries de templates + quants + adapter merging) — overengineered para 2 VLMs. Si en el futuro entra Qwen-VL o MedGemma, se suma una `family` al adaptador.

## Estrategia de testing

**Nuevos tests** (todos con `FakeVLMAdapter`, sin GPU, sin red):

- `load(LoadSpec(model_id="fake"))` retorna `LoadedVLM` con `metadata["family"] == "fake"`.
- `attach_lora` → `save_lora(tmp_path)` → `load_lora(tmp_path)` reconstruye `LoraSpec` idéntico (sin shape inference). **Regresión del bug de `generate_report.py:78-94`.**
- `prepare_inputs` para LLaVA-Med vs Mini-VLM inserta el `<image>` token en la posición correcta del template.
- `forward_train(vlm, batch)` retorna un tensor con `requires_grad=True`.
- `LoadSpec.quantization == "auto"` con VRAM probe mockeado a 12 GB selecciona `"4bit"`, con 24 GB selecciona `None`.

**Tests viejos a borrar:** ninguno (no había).

**Necesidades de entorno:** `pytest` + `torch` CPU-only. Sin transformers ni HF.

## Recomendaciones de implementación

Lo que el módulo `models/` debe **poseer**:

- Templates por familia (un dict por familia).
- Política de quantization auto.
- Metadata de LoRA (incluido el `lora_config.json` durable).
- Mapeo `family → adaptador`.

Lo que debe **ocultar**:

- Llamados a `from_pretrained`, `AutoProcessor`, `PeftModel`.
- Detalles de `bitsandbytes`.
- Inspección de shape de tensores.

Lo que debe **exponer**:

- `VLMPort` como interfaz pública.
- `LoadSpec`, `LoraSpec`, `LoadedVLM` como tipos de datos.
- `get_vlm_port(name)` como factory.

**Migración recomendada:**

1. Crear `src/models/ports.py` con los tipos.
2. Implementar `HFVLMAdapter` reutilizando el código de `llava_med.py`/`mini_vlm.py`.
3. Implementar `FakeVLMAdapter` + escribir los tests de regresión del LoRA bug.
4. Migrar `generate_report.py` al puerto. Validar paridad numérica contra una corrida v1.
5. Migrar `train_vlm_stage1.py` y `train_vlm_stage2.py`.
6. Cuando todos los callers usen el puerto, borrar `VLMBase`, `LLaVAMed`, `MiniVLM` y dejar sólo `HFVLMAdapter`.
7. **Antes del paso 4**, agregar a `train_vlm_stage2.py` la escritura de `lora_config.json` para garantizar que los checkpoints existentes funcionen en transición.

**Líneas estimadas ahorradas:** ≈100, pero el beneficio principal es **mata el bug latente de LoRA** y habilita CI sin GPU.

## Sincronización con clústeres

Reemplaza `llava_med.py` y `mini_vlm.py` por adaptadores y agrega `src/models/ports.py`. Antes del primer `submit`:

1. `python scripts/mendieta/sync_up.py --delete` (los archivos viejos no deben quedar como huérfanos: si `train_vlm_stage2.py` los importa por reflex, falla en silencio).
2. `python scripts/toko/sync_up.py`.
3. **Antes** del paso 4 de la migración, agregar la escritura de `lora_config.json` y re-correr una iteración de Stage 2 en cluster para que los checkpoints futuros lo tengan. Los checkpoints v1 existentes no lo tienen — agregar un fallback que infiera por shape **solo** si falta el JSON, con `warnings.warn`.
4. Validación de la regresión del bug LoRA: **100% local** con `FakeVLMAdapter` + el checkpoint LoRA v1 ya descargado. No requiere cluster.
