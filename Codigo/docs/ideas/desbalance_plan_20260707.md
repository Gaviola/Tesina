# Plan — P2.2 Manejo explícito del desbalance (TOKO)

**Fecha:** 2026-07-07 · **Plan maestro:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.2) · **Feedback:** #21.
**Cluster:** TOKO (RTX 4080, cola corta). En paralelo a SkinVL (Mendieta).

## Motivación
El tutor pide probar manejo explícito del desbalance para mostrar que **el problema no es solo el
desbalance de HAM10000**. El mejor Swin actual (`modern_v3`) ya usa **CE + class-weights** y logra
sens.\ macro 0.87 (buena discriminación en minoritarias). Se comparan variantes de loss para ver si el
manejo del desbalance mueve la aguja o si el clasificador ya es robusto.

## Diseño
Cuatro entrenamientos de **Swin-Tiny**, mismo recipe `modern` y HPs, **variando solo la loss**:
- `swin_imb_ce` — CE plano, **sin** manejo (`--focal-gamma 0 --class-weights none`). Baseline naive.
- `swin_imb_weighted` — CE + class-weights inversas (`--class-weights auto`). (= config de v3.)
- `swin_imb_focal` — Focal Loss γ=2 (`--focal-gamma 2.0 --class-weights auto`).
- `swin_imb_balsoftmax` — Balanced Softmax (`--balanced-softmax`).

Código: `src/training/losses.py` (nuevo `BalancedSoftmaxLoss` + `build_loss` extendido);
`scripts/train_classifier.py` (flags `--class-weights {auto,none}`, `--balanced-softmax`); aliases en
`scripts/toko/submit.py` (`imb_swin_*`). SLURM reusado: `slurm/toko/train_classifier.sh` (parametrizado).

## Criterio de éxito (veredicto)
Comparar **sens.\ macro** (y F1, por clase) de las 4 variantes. Hipótesis: diferencias chicas → el
clasificador ya maneja el desbalance; el colapso de los VLM no es un problema de desbalance sino de
dominio/objetivo (refuerza [[project_vlm_collapse_domain_not_imbalance]]). Focal probablemente degrade
minoritarias (ya observado en v3).

## Sincronización con clústeres
`sync_up` a TOKO (código con losses + flags + aliases). Submit `imb_swin_{ce,weighted,focal,balsoftmax}`.
TOKO scratch no persistente → `sync_down` de results/predictions al terminar (rápido). Evaluar local
(calibración/tests reusables). Documentar en resul + `ejecuciones.md`.
