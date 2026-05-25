# RFCs arquitectónicos — DermVLM

**Fecha de creación:** 2026-05-25
**Origen:** revisión de arquitectura completa del repo (`Codigo/src/` + `Codigo/scripts/`).

Cada RFC propone una refactorización siguiendo el principio de "deep modules" de Ousterhout: interfaces pequeñas que esconden implementaciones grandes, con testabilidad como objetivo de primer orden.

| # | Tema | Categoría de dependencia | Impacto estimado |
|---|------|--------------------------|------------------|
| [01](01_clusters_plan_20260525.md) | Consolidación de gestión de clústeres (Mendieta + TOKO) | 3 — Remoto pero propio (puertos y adaptadores) | ≈1600 líneas ahorradas, tests end-to-end posibles sin SSH |
| [02](02_trainer_plan_20260525.md) | Refactor del entrenador y pipeline two-stage VLM | 1 — In-process | ≈1100 líneas ahorradas, tests unitarios sin GPU |
| [03](03_bootstrap_plan_20260525.md) | Bootstrap centralizado para scripts | 1 — In-process | ≈280 líneas ahorradas, smoke-tests <100ms |
| [04](04_data_plan_20260525.md) | Carga de datasets, splits e image store | 2 — Local-substitutable | Tests del retry NFS y del versionado de splits |
| [05](05_vlm_loader_plan_20260525.md) | Loader VLM con puertos y adaptadores | 4 — True external (Mock) | Mata el bug de inferencia de LoRA por shape, CI sin GPU |
| [06](06_metrics_plan_20260525.md) | Capa de evaluación con puertos para NER + BERTScore | 4 — True external (Mock) | Elimina errores silenciosos, CI sin descargas de modelos |

## Orden sugerido de implementación

Pensando en bloqueos mutuos y retorno por esfuerzo:

1. **RFC 03 (Bootstrap)** — independiente, riesgo bajo, valor inmediato en todos los scripts. Es la base sobre la que descansan los demás refactors.
2. **RFC 04 (Datasets)** — independiente, alto valor de testabilidad. Habilita probar el retry NFS y el versionado sin tocar el cluster.
3. **RFC 05 (VLM Loader)** — independiente, **arregla un bug latente** (LoRA r por shape). Habilita CI para el flujo VLM.
4. **RFC 06 (Metrics)** — depende parcialmente de 05 (los adaptadores fake comparten filosofía). Habilita CI completo para evaluación.
5. **RFC 02 (Trainer)** — el más invasivo, pero también el de mayor consolidación de código. Beneficia de tener 03/04/05 ya en su lugar.
6. **RFC 01 (Clusters)** — independiente del resto del código Python, pero el cambio operativo más visible. Se puede hacer en paralelo a cualquiera de los anteriores.

## Validación recomendada por RFC

**¿Local o en cluster?** La mayoría se valida sin enviar jobs nuevos: alcanza con los artefactos de v1 ya descargados en `outputs/` y correr el código refactorizado contra ellos en la GPU local (RTX 4070 12GB). Detalle:

| RFC | Cluster | Estrategia local |
|---|---|---|
| 03 Bootstrap | no | tests in-memory + `test_mode=True`; no hay paridad numérica que medir |
| 04 Datasets | no | `__len__`/`__getitem__` sobre splits ya bajados; comparar IDs y `class_weights` contra v1 |
| 05 VLM Loader | no | cargar checkpoint LoRA de v1 con el puerto nuevo, generar N reportes con `temperature=0`, comparar texto contra `outputs/generated_reports/<model>/v1/*.json` |
| 06 Metrics | no | re-correr `evaluate_reports.py` con el código nuevo sobre `predictions_v1.json` y comparar contra `metrics_v1.json` ya descargado |
| 02 Trainer | **sí** para paridad bit-exact de Stage 2 VLM (8-12 hs en A30) | clasificadores: paridad completa local en RTX 4070 (~30 min); VLM: tests unitarios + 1-epoch smoke (loss del primer epoch coincide con v1) |
| 01 Clusters | una verificación de humo (no de cómputo) | tests con `RecordingTransport`; después una integración manual: `submit --dry-run` + `monitor` + `sync_down --logs` contra cluster real |

**Reglas comunes de paridad:**

- Mismo `seed=42`, mismos splits (`splits_version="v1"`).
- BLEU/ROUGE/METEOR/CIDEr deben coincidir bit-exact entre v1 y código refactorizado.
- BERTScore puede variar levemente entre CPU y GPU por orden de operaciones — fijar el `device` al mismo que produjo v1.
- Para VLM generation, `temperature=0` (greedy) garantiza salidas reproducibles texto-a-texto.

## Sincronización con clústeres (aplica a todos los RFCs)

El repo está **replicado en cada clúster** (Mendieta y TOKO) bajo el `remote_root` definido en `scripts/<cluster>/config.py`. Cualquier cambio que altere la estructura local debe propagarse antes de enviar el siguiente job:

- **Renames o nuevos módulos en `src/`**: ejecutar `python scripts/mendieta/sync_up.py` y `python scripts/toko/sync_up.py` antes del próximo `submit`.
- **Archivos borrados**: en Mendieta usar `sync_up.py --delete` para eliminar huérfanos remotos; TOKO regenera el scratch en cada job, no requiere `--delete`.
- **Cambios en `configs/`**: igual, requieren `sync_up`.
- **Cambios solo en `docs/` o `notebooks/`**: no requieren sync (no se ejecutan en cluster), pero conviene incluirlos en el próximo `sync_up` rutinario para mantener el repo remoto coherente.
- **`outputs/` y `data/`**: siempre se sincronizan con sus scripts dedicados (`sync_down`, `sync_data`); nunca con `sync_up`.

Cuando se mergea un RFC que toca rutas (`src/training/api.py` nuevo, `src/data/_split_loader.py` nuevo, etc.), el primer `submit` post-merge **debe** ir precedido de `sync_up`. Documentar el commit hash en `docs/ejecuciones.md` y el `sync_up` correspondiente como pasos separados.

## No hacer

- **No** implementar los 6 RFCs en una sola PR. Mergear de a uno, validando paridad.
- **No** combinar el refactor con cambios de modelo o de hiperparámetros (cero variables movidas a la vez).
- **No** abrir un RFC sin antes haber escrito al menos los tests de borde planteados en la sección "Testing".
