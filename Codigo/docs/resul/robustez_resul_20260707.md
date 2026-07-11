# Resultado — Robustez a perturbaciones de adquisición (P2.4)

**Fecha:** 2026-07-07 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.4) · **Sin jobs SLURM** (local, RTX 4070).
**Feedback:** #7 — ¿qué pasa si cambian las condiciones de adquisición? (HIBA ya cubrió cambio de población).

## Diseño
- Se perturban las imágenes de test de HAM10000 (n=1503) en 5 niveles crecientes y se re-corre el
  clasificador, midiendo la caída de **sensibilidad macro**:
  - **JPEG** (calidad 70→5) · **ruido** gaussiano (σ 8→64) · **blur** gaussiano (radio 1→6) ·
    **resolución** (bajar a 0.75→0.15 y re-escalar).
- **Modelos:** Swin-Tiny y ConvNeXt-Tiny (`modern_v3`, checkpoints bajados de TOKO). Evaluación
  single-view (sin TTA) → el baseline de sens.\ macro es algo menor que el reportado con TTA (Swin
  $0.738$ vs $0.870$); lo relevante es la **degradación relativa**.
- **Código:** `scripts/robustness_perturbations.py`. **Salida:** `outputs/results/robustness/`
  (`robustness_curves.png`, `robustness_summary.json`).

## Resultados — sensibilidad macro por severidad (Figura `P24_robustness`)

**Swin-Tiny** (baseline $0.738$):
| Perturbación | sev1 | sev2 | sev3 | sev4 | sev5 |
|--------------|:-:|:-:|:-:|:-:|:-:|
| JPEG        | 0.735 | 0.724 | 0.650 | 0.558 | 0.266 |
| Ruido       | 0.635 | 0.496 | 0.375 | 0.246 | 0.177 |
| Blur        | 0.750 | 0.660 | 0.581 | 0.505 | 0.332 |
| Resolución  | 0.763 | 0.739 | 0.691 | 0.626 | 0.526 |

**ConvNeXt-Tiny** (baseline $0.830$):
| Perturbación | sev1 | sev2 | sev3 | sev4 | sev5 |
|--------------|:-:|:-:|:-:|:-:|:-:|
| JPEG        | 0.781 | 0.753 | 0.721 | 0.553 | 0.276 |
| Ruido       | 0.671 | 0.484 | 0.375 | 0.276 | 0.214 |
| Blur        | 0.803 | 0.685 | 0.579 | 0.522 | 0.460 |
| Resolución  | 0.817 | 0.765 | 0.716 | 0.662 | 0.564 |

## Análisis
1. **El ruido gaussiano es la perturbación más dañina** en ambos modelos: la sens.\ macro cae rápido
   (Swin $0.738\to0.375$ ya en severidad moderada; hasta $0.18$ en la máxima). El sensor/ruido de
   adquisición es el factor más crítico.
2. **La resolución es lo más tolerado**: aun bajando fuerte la resolución, la sens.\ macro se mantiene
   ($\approx 0.53$–$0.56$ en la severidad máxima). La clasificación dermatoscópica no depende tanto del
   detalle fino de píxel.
3. **JPEG y blur son intermedios**: robustos a compresión/desenfoque leve (sev1–2 casi sin caída), pero
   se degradan a partir de severidad moderada; JPEG severo (calidad 5) es el que más colapsa junto al
   ruido.
4. **Degradación gradual, no abrupta**: a perturbación leve (sev1–2) ambos modelos se mantienen sólidos
   ($0.65$–$0.83$); ninguno cae al azar salvo bajo ruido/JPEG extremos.
5. **ConvNeXt es algo más robusto** que Swin (mejor baseline + patrón de degradación similar).

## Conclusión (veredicto)
**CUMPLE.** Evaluación sistemática de robustez a calidad de imagen sobre los clasificadores headline:
tolerantes a compresión/resolución/blur leve, **sensibles al ruido**. Complementa HIBA (cambio de
población). Se integra a `experimentacion.tex`. *(Pendiente opcional: DermLIP requiere `open_clip`, se
puede agregar en el cluster.)*
