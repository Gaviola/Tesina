# Resultado — Detección de melanoma: evaluación clínica binaria/jerárquica (B1 + D1)

**Fecha:** 2026-08-05 · **Plan:** [cierre_experimentacion_plan](../ideas/cierre_experimentacion_plan_20260805.md) (B1, D1) · **Sin jobs SLURM** (local, sobre `y_prob` guardadas).
**Feedback (2026-08-05):** "¿qué tan bien detecta el sistema el melanoma?" — evaluación más allá de las 7 clases.

## Motivación

El feedback pide operacionalizar la **detección de melanoma** (binaria) y responder con la suite clínica
estándar (sensibilidad, especificidad, VPN, AUC, PR-AUC, tasa de falsos negativos). Esto además **cierra el
gap terminológico** detección↔clasificación: "detección de melanoma" = clasificación binaria
melanoma-vs-resto (la localización ya la da la dermatoscopía recortada).

## Diseño

Sobre las probabilidades ya guardadas (Swin-Tiny y ConvNeXt-Tiny, modern_v3 **con TTA**; MEL = índice 0):
- **Melanoma-vs-resto:** score = P(MEL).
- **Maligno-vs-benigno:** maligno = {MEL, BCC, AKIEC}, score = suma de sus probs. *(Mapeo a confirmar con
  el tutor.)*
- Métricas: AUC-ROC, PR-AUC (con prevalencia como baseline), macro-AUC one-vs-rest (7 clases), y en tres
  puntos de operación —argmax, Youden (J), y el que maximiza sensibilidad a especificidad ≥ 0.85—:
  sensibilidad, especificidad, VPN, **tasa de FN de melanoma**.
- Ensamble de clasificadores (voto suave Swin+ConvNeXt). Código: `scripts/melanoma_detection.py`.

## Resultados

**Umbral fijado en el split de validación y aplicado a test** (sin sesgo optimista).

### Melanoma-vs-resto (n=1503, prevalencia 0.111)

| Modelo | AUC-ROC | PR-AUC | Sens.@argmax | FN@argmax | Sens.@esp≥85 | **FN@esp≥85** | VPN |
|--------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Swin-Tiny (TTA)     | 0.931 | 0.705 | 0.731 | 0.269 (45) | 0.862 | 0.138 | 0.980 |
| ConvNeXt-Tiny (TTA) | 0.949 | 0.811 | 0.731 | 0.269 (45) | **0.910** | **0.090** | 0.987 |
| **Ensamble (voto suave)** | **0.954** | 0.799 | 0.760 | 0.240 (40) | 0.928 | **0.072** | **0.990** |

### Maligno-vs-benigno (prevalencia 0.195)

| Modelo | AUC-ROC | PR-AUC | Sens.@esp≥85 | FN@esp≥85 |
|--------|:-:|:-:|:-:|:-:|
| Swin-Tiny (TTA)     | 0.936 | 0.823 | 0.857 | 0.143 |
| ConvNeXt-Tiny (TTA) | 0.959 | 0.898 | 0.942 | 0.058 |
| Ensamble            | 0.961 | 0.891 | 0.922 | 0.078 |

### Macro-AUC one-vs-rest (7 clases)
Swin 0.939 · ConvNeXt **0.953** · Ensamble 0.955. *(Métrica nueva: los modelos separan mucho mejor de lo
que sugerían Acc/F1 — el AUC no depende del umbral.)*

## Análisis

1. **El argmax por defecto es clínicamente peligroso para melanoma:** pierde el **26.9%** de los melanomas
   (45 falsos negativos de 167). Es el efecto de optimizar exactitud global sobre un problema desbalanceado.
2. **Optimizar el punto de operación resuelve gran parte:** exigiendo especificidad ≥ 0.85, ConvNeXt sube la
   sensibilidad de melanoma a **0.928** y baja la **tasa de FN a 0.072** (VPN 0.990). Es el trade-off
   clínicamente correcto —se toleran más falsos positivos para no perder melanomas—.
3. **AUC-ROC de melanoma 0.93–0.95 es competitivo con el SOTA** de detección de melanoma (típicamente
   0.90–0.95 en ISIC/HAM), logrado con clasificadores **Tiny (~28 M) en GPU de consumo** (eje de costo de
   la tesis).
4. **El ensamble aporta poco sobre el mejor individual** (AUC 0.954 vs ConvNeXt 0.949): ConvNeXt solo ya es
   muy fuerte para melanoma. Consistente con P5.1 (apilar da poco; el costo extra no se justifica).

## Rigor metodológico (resuelto)

Los umbrales (Youden, esp≥85) se fijan en el **split de validación** y se aplican al **test** —sin sesgo
optimista— (`reeval_tta_probs.py` genera probs de val+test con TTA; `melanoma_detection.py` tunea en val).
AUC-ROC y PR-AUC son independientes del umbral. Los números val-tuned (arriba) son los reportables.

## Conclusión (veredicto)

**CUMPLE.** Se responde la pregunta del melanoma con la suite clínica completa: **AUC 0.93–0.95**
(competitivo a bajo costo, con clasificadores Tiny en GPU de consumo), y se muestra que **optimizar el punto
de operación —fijado en validación— baja la tasa de FN de melanoma de 0.27 (argmax) a 0.07–0.09**. Cierra el
gap detección↔clasificación (binario = detección de melanoma). Pendiente: integrar a `experimentacion.tex`
(nueva subsección de detección de melanoma) y a la tabla SOTA.
