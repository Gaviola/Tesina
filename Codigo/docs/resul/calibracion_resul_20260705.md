# Resultado — Calibración de clasificadores (P0.1)

**Fecha:** 2026-07-05 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P0.1) · **Sin jobs SLURM** (100% local).
**Feedback:** #8 — "¿cuándo el clasificador dice 99% de confianza, realmente acierta el 99%?"

## Motivación
El tutor plantea que un modelo con ~0.80 de accuracy podría estar sobre-ajustando la *confianza*
(ej.: cuando predice 99%, solo acierta 75%), lo cual en medicina es peligroso. Se miden métricas de
calibración —**ECE**, **MCE**, **Brier score**— y se dibujan **reliability diagrams**.

## Diseño
- **Insumos:** `outputs/results/classifiers/modern_v3/*_predictions.json` (ya contienen `y_prob`, test
  HAM10000 n=1503). Sin re-inferencia.
- **Código:** funciones `expected_calibration_error`, `brier_score_multiclass`, `reliability_curve`,
  `evaluate_calibration` en `src/evaluation/classification.py`; script `scripts/evaluate_calibration.py`.
- **Salida:** `outputs/results/calibration/calibration_summary.json` + `reliability_diagrams.png`.
- 10 bins de confianza (prob. máx.).

## Resultados

| Modelo | Acc | ECE ↓ | MCE ↓ | Brier ↓ |
|--------|-----|-------|-------|---------|
| DenseNet121  | 0.590 | **0.188** | 0.289 | 0.606 |
| ViT-B/16     | 0.668 | 0.273 | 0.397 | 0.623 |
| Swin-Tiny    | 0.795 | 0.380 | 0.595 | 0.575 |
| ConvNeXt-Tiny| 0.819 | 0.393 | 0.598 | 0.555 |

*(ECE/MCE en [0,1]; Brier multiclase en [0,2]. Ver `reliability_diagrams.png`.)*

## Análisis
1. **Todos los clasificadores están mal calibrados** (ECE 0.19–0.39). Ninguno es confiable como
   estimador de certeza "tal cual".
2. **La dirección del error es la contraria a la hipótesis del tutor: no hay sobre-confianza, hay
   SUB-confianza.** Swin tiene confianza media **0.42** (mediana 0.31) pero accuracy **0.795**: cuando el
   modelo "dice 30%", en realidad acierta ~80%. En el reliability diagram las barras de exactitud quedan
   **por encima** de la diagonal en los bins de confianza baja. Es la miscalibración "segura" (el modelo
   casi nunca grita 99%: solo 4/1503 casos con conf ≥ 0.99), pero igual es un problema: la probabilidad
   cruda **subestima** la certeza real.
3. **A mayor accuracy, peor calibración:** ConvNeXt (0.819) y Swin (0.795) —los mejores— son los más
   miscalibrados (ECE ~0.39); DenseNet (0.590) es el mejor calibrado (ECE 0.19). Los mejores modelos
   producen distribuciones **más difusas**.
4. **Causa probable:** el *recipe* moderno (TTA-averaging sobre múltiples vistas + RandAugment +
   regularización) aplana el softmax; el promedio de softmaxes reduce el pico de confianza.

## Implicancias para el plan
- **Uncertainty-aware grounding (P3, feedback #16):** la confianza cruda del clasificador **no** sirve
  directamente para modular el reporte del generador; habría que **calibrar primero** (temperature
  scaling). Este resultado justifica ese paso.
- La sub-confianza es "segura" en términos clínicos (no afirma falsamente 99%), pero conviene reportarla
  como limitación honesta.

## Pendiente
- **DermLIP:** `eval_dermlip_classify.py` ya fue modificado para guardar `y_prob` (softmax de logits);
  falta **re-correr local** (ViT-B/16 ~150M, minutos) para tener su calibración. Comando:
  `python scripts/eval_dermlip_classify.py --checkpoint vit-b-16`.
- **Temperature scaling (opcional):** requiere probs del split de **validación** (no test, para no filtrar);
  mostraría que la miscalibración es trivialmente corregible con un solo parámetro T.

## Conclusión (veredicto)
**CUMPLE** — Calibración medida y graficada para los 4 clasificadores supervisados. Hallazgo con matiz
honesto y relevante para la tesina: **los clasificadores no son sobre-confiados sino SUB-confiados, y los
más precisos son los peor calibrados**. Se integra a `experimentacion.tex` (sección de clasificación,
como análisis de robustez de las probabilidades). Próximo: re-correr DermLIP para completar la tabla.
