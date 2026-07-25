# Plan — Desbalance en más modelos (ConvNeXt + DenseNet) · mejora #2 (2.ª tanda mejoras.md)

**Fecha:** 2026-07-21 · **Origen:** `mejoras.md` #1 — la sección "El desbalance tampoco limita al
clasificador supervisado" solo usa **Swin-Tiny**; expandir a más modelos para que la conclusión no dependa
de una sola arquitectura. Complementa [P2.2](../resul/desbalance_resul_20260707.md).

## Motivación

P2.2 mostró, **solo sobre Swin-Tiny**, que el manejo explícito del desbalance (class-weights / Focal /
Balanced Softmax) no mejora a la CE-plano (sens. macro 0.887 el mejor). Para robustecer esa conclusión se
replica el experimento en dos arquitecturas más, cubriendo tres familias: **Swin** (transformer, ya hecho),
**ConvNeXt-Tiny** (CNN moderno) y **DenseNet121** (CNN clásico).

## Diseño

Por cada modelo (ConvNeXt-Tiny, DenseNet121), cuatro entrenamientos con el **mismo recipe `modern` y HPs**,
variando **solo la pérdida** (idéntico a P2.2 sobre Swin):
- **CE-plano** — `--focal-gamma 0 --class-weights none`
- **CE + class-weights** — `--focal-gamma 0 --class-weights auto`
- **Focal Loss (γ=2)** — `--focal-gamma 2.0 --class-weights auto`
- **Balanced Softmax** — `--balanced-softmax`

- **Cluster:** se planeó TOKO (RTX 4080, cola corta) pero **TOKO estaba caído** (timeout SSH puerto 22) al
  momento de lanzar → se corrió en **Mendieta** (A30, cola 5-7 días). 8 jobs (2 modelos × 4 pérdidas),
  **jobs 1161112–1161119 (enviados)**.
- **Aliases nuevos** en `scripts/toko/submit.py` Y `scripts/mendieta/submit.py`:
  `imb_convnext_{ce,weighted,focal,balsoftmax}`, `imb_densenet_{...}`; grupo `imb_all_extra`.
- **Evaluación:** test HAM10000 (n=1503) con TTA, sens. macro / F1-w / acc, igual que P2.2.

## Criterio de éxito

Confirmar (o refutar) que **el manejo del desbalance no mejora a la CE-plano** también en ConvNeXt y
DenseNet. Si el patrón se repite en las tres arquitecturas, la conclusión "el desbalance no es el cuello de
botella del clasificador" queda sólida y no atada a Swin.

## Sincronización con clústeres

- `python scripts/toko/sync_up.py` (código con los aliases nuevos; `losses.py` y flags ya están).
- Los pesos torchvision de ConvNeXt/DenseNet deben estar pre-descargados en el cache de TOKO (ya se usaron
  en las corridas `cls_*_modern`).
- `python scripts/toko/submit.py imb_all_extra` (grupo de 8) o individuales.
- Al volver: `sync_down.py` de métricas → tabla en el resul → integrar a `experimentacion.tex` (extender
  el Cuadro de desbalance a las 3 arquitecturas).
