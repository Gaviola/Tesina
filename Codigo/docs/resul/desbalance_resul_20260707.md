# Resultado — Manejo explícito del desbalance (P2.2)

**Fecha:** 2026-07-07 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.2) · **Jobs TOKO 96860–96863.**
**Feedback:** #21 — probar Focal/class-balanced/balanced-softmax para mostrar que el problema no es solo el desbalance de HAM.

## Diseño
Cuatro entrenamientos de **Swin-Tiny**, mismo recipe `modern` y HPs, **variando solo la loss** (eval con TTA):
- **CE-plano** (`--class-weights none`, sin manejo del desbalance) — baseline naive.
- **CE + class-weights** (pesos inversos a la frecuencia).
- **Focal Loss** (γ=2).
- **Balanced Softmax**.

Código: `BalancedSoftmaxLoss` en `src/training/losses.py`; flags `--class-weights`, `--balanced-softmax`
en `train_classifier.py`; aliases `imb_swin_*` en `toko/submit.py`.

## Resultados (test HAM10000, n=1503, con TTA)

| Variante | Acc | F1-w | Sens.\ macro | Sens.\ por clase (MEL,NV,BCC,AKIEC,BKL,DF,VASC) |
|----------|:-:|:-:|:-:|:-:|
| **CE-plano (sin manejo)** | **0.923** | **0.923** | **0.887** | 0.78, 0.97, 0.96, 0.80, 0.81, 0.94, 0.95 |
| CE + class-weights | 0.795 | 0.816 | 0.809 | 0.83, 0.79, 0.83, 0.82, 0.73, 0.71, 0.95 |
| Focal γ=2 | 0.820 | 0.843 | 0.857 | 0.74, 0.82, 0.95, 0.82, 0.84, 0.88, 0.95 |
| Balanced Softmax | 0.856 | 0.872 | 0.857 | 0.74, 0.88, 0.95, 0.86, 0.80, 0.82, 0.95 |

## Análisis
1. **El manejo explícito del desbalance NO ayuda; incluso puede empeorar.** El baseline **CE-plano** —sin
   ningún manejo del desbalance— es el **mejor** en las tres métricas (sens.\ macro $0.887$), con buena
   sensibilidad en \emph{todas} las clases, incluidas las minoritarias (BCC $0.96$, DF $0.94$, VASC
   $0.95$; el mínimo es melanoma $0.78$).
2. **Las class-weights degradan** (sens.\ macro $0.887\to0.809$, acc $0.923\to0.795$): sobre-corrigen,
   empujando las predicciones lejos de la clase mayoritaria más de lo conveniente. Focal y
   Balanced-Softmax quedan intermedios ($0.857$), tampoco superan al CE-plano.
3. **Interpretación:** el Swin con el recipe \emph{modern} (RandAugment, etc.) ya aprende buenas
   representaciones de las clases minoritarias \emph{sin} manejo del desbalance. Es decir, para el
   clasificador supervisado el desbalance de HAM \textbf{no es el cuello de botella}.

## Conclusión (veredicto)
**CUMPLE.** Confirma que el desbalance de HAM10000 no es el problema para el clasificador supervisado: el
CE-plano ya alcanza sens.\ macro $0.887$ y el manejo explícito no mejora (o empeora). Refuerza que el
\emph{colapso de los VLM generales no es un problema de desbalance} sino de dominio/objetivo (ver
`project_vlm_collapse_domain_not_imbalance`). Se integra a `experimentacion.tex` (Sección de re-diagnóstico
/ discusión del desbalance). *(Nota: el CE-plano supera al Swin con class-weights reportado antes;
conviene mencionarlo.)*
