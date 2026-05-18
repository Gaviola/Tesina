# Clasificación VLM — Resultados v3 (Stage 2 v2: epochs=10)

**Fecha de envío de jobs:** 2026-05-17
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:** 1154209 (LLaVA-Med FT lik), 1154210 (Mini-VLM FT lik), 1154211 (LLaVA-Med FT CoT), 1154212 (Mini-VLM FT CoT)
**Dataset:** HAM10000 Test Set (n=1503, 7 clases)
**Checkpoints:** `outputs/checkpoints/stage2_{llava_med,mini_vlm}_v2/best_model.pt` (10 epochs, lr=2.495e-5, lora_r=64)
**Estado:** *Pendiente — jobs en cola Mendieta, espera estimada 5-7 días*

---

## 1. Motivación

El Stage 2 original (v1) usó `epochs=3` por restricción de tiempo. El sweep de HPs ([reportes_mejoras_v2_plan_20260510.md](../ideas/reportes_mejoras_v2_plan_20260510.md))
encontró que `val_loss` seguía descendiendo en la época 5/5 del trial t04 (mejor configuración). Stage 2 v2 re-entrena con `epochs=10` y los mismos HPs del t04, esperando capturar mejor convergencia y traducirse en mejoras en clasificación VLM (likelihood + CoT) y generación.

Este documento cubre la clasificación; el de generación es [reportes_resul_v2_20260517.md](reportes_resul_v2_20260517.md).

---

## 2. Diseño experimental

Solo se re-corren los 4 jobs FT (los ZS no cambian, ya que el checkpoint Stage 2 no afecta inferencia zero-shot):

| Job ID | Modelo | Método | ZS/FT | Notas |
|--------|--------|--------|-------|-------|
| 1154209 | LLaVA-Med | likelihood | FT v2 | Stage 2 v2 ckpt |
| 1154210 | Mini-VLM | likelihood | FT v2 | Stage 2 v2 ckpt |
| 1154211 | LLaVA-Med | CoT | FT v2 | Stage 2 v2 ckpt |
| 1154212 | Mini-VLM | CoT | FT v2 | Stage 2 v2 ckpt |

Tiempo estimado por job: ~4-6h. Cola Mendieta: 5-7 días al momento de envío.

Output esperado: `outputs/results/{model}/v2/` (post-mv aplicado por los scripts SLURM `slurm/mendieta/v2/vlm_classify_*_ft.sh`).

---

## 3. Baseline de comparación

Resultados de la iteración v2 (Stage 2 v1, epochs=3, documentados en
[vlm_clasificacion_resul_v2_20260510.md](vlm_clasificacion_resul_v2_20260510.md)):

| Modelo | Método | Acc | F1-w | Sens. macro | Notas |
|--------|--------|-----|------|------------|-------|
| LLaVA-Med | FT lik (v1) | 0.1344 | 0.098 | 0.163 | Re-envío post-fix LoRA rank |
| LLaVA-Med | FT CoT (v1) | 0.0812 | 0.029 | 0.119 | 456 UNKNOWN (CoT format failure) |
| Mini-VLM | FT lik (v1) | **0.6660** | **0.536** | 0.142 | Class collapse hacia NV |
| Mini-VLM | FT CoT (v1) | 0.1153 | 0.040 | 0.141 | — |

**Criterios de éxito** para considerar v2 prometedor (criterio definido en [ejecuciones.md](../ejecuciones.md)):

- Mejorar **F1-weighted** respecto al mismo modelo+método en v1.
- Subir **sensitivity macro** por encima de 1/7 (≈0.143) = romper el class collapse hacia NV.

---

## 4. Resultados v2 *(pendiente — completar tras descarga)*

### 4.1 Tabla comparativa v1 vs v2

> **[COMPLETAR cuando terminen jobs 1154209–1154212]**
>
> Descargar con: `python scripts/mendieta/sync_down.py --results`
> Archivos esperados (post-mv automático del SLURM):
> - `outputs/results/llava_med/v2/llava_med_likelihood_finetuned_predictions.json`
> - `outputs/results/llava_med/v2/llava_med_likelihood_finetuned_test_results.json`
> - `outputs/results/llava_med/v2/llava_med_cot_finetuned_predictions.json`
> - `outputs/results/llava_med/v2/llava_med_cot_finetuned_test_results.json`
> - `outputs/results/mini_vlm/v2/mini_vlm_likelihood_finetuned_predictions.json`
> - `outputs/results/mini_vlm/v2/mini_vlm_likelihood_finetuned_test_results.json`
> - `outputs/results/mini_vlm/v2/mini_vlm_cot_finetuned_predictions.json`
> - `outputs/results/mini_vlm/v2/mini_vlm_cot_finetuned_test_results.json`

| Modelo | Método | Acc v1 | F1-w v1 | Acc v2 | F1-w v2 | Δ Acc | Δ F1-w |
|--------|--------|--------|---------|--------|---------|-------|--------|
| LLaVA-Med | FT lik | 0.134 | 0.098 | *pendiente* | *pendiente* | — | — |
| LLaVA-Med | FT CoT | 0.081 | 0.029 | *pendiente* | *pendiente* | — | — |
| Mini-VLM | FT lik | 0.666 | 0.536 | *pendiente* | *pendiente* | — | — |
| Mini-VLM | FT CoT | 0.115 | 0.040 | *pendiente* | *pendiente* | — | — |

### 4.2 Sensitivity macro — ¿se rompe el class collapse?

> **[COMPLETAR]** Mini-VLM FT lik v1 tenía sens_macro=0.142 (NV-collapse). Si v2 sube esto >0.30, indica clasificación discriminativa real.

### 4.3 Accuracy por prompt — ensemble likelihood

> **[COMPLETAR]** Comparar O1/O2/C1/C2 accuracy entre v1 y v2 para detectar si el prompt O2 (degenerado en v1) mejora con más epochs.

### 4.4 Tasa UNKNOWN — método CoT

> **[COMPLETAR]** LLaVA-Med FT CoT v1 tenía 456/1503 UNKNOWN (30%). Verificar si v2 mejora el seguimiento del formato "Final diagnosis:".

---

## 5. Análisis *(pendiente)*

> **[COMPLETAR tras resultados]** Cubrir:
> 1. ¿v2 supera a v1 en F1/Acc para los 4 combos?
> 2. ¿Se mantiene el class collapse de Mini-VLM FT lik (sens_macro ≈ 1/7)? Si sí, v2 también heredó el prior NV de SkinCaRe.
> 3. ¿LLaVA-Med FT mejora ahora que tiene 10 epochs vs 3? El re-entrenamiento del Stage 2 podría haber permitido al modelo aprender más allá del nivel superficial.
> 4. Comparar con el mejor clasificador supervisado (Swin-Tiny sweep v4, F1=0.882). El gap VLM-clasificador es la métrica clave de Fase 2.

---

## 6. Decisión sobre actualización de SOTA tabla

> **[COMPLETAR tras análisis]**
>
> Aplicar criterio prometedor: si v2 supera a v1 (F1-w o sens_macro) para algún combo, agregar fila en Tabla 1 SOTA con sufijo "(Stage 2 v2, LoRA)". Si todos los combos empeoran o empatan, documentar resultado nulo y no tocar SOTA.

---

## 7. Caveats

- **Cola Mendieta:** 5-7 días al momento de envío. Estado en `python scripts/mendieta/monitor.py`.
- **Checkpoint v2 path:** `outputs/checkpoints/stage2_{model}_v2/best_model.pt` (renombrado desde `stage2_{model}_{model}_s2_v2/` que era el path generado por `train_vlm_stage2.py` con `--run-name {model}_s2_v2`).
- **SLURM scripts:** `slurm/mendieta/v2/vlm_classify_{llava,mini}_ft.sh` (folder `v2/` indica versión, sin sufijo `_v2` en el nombre del archivo).
- **ZS no se re-corre:** los métodos ZS no usan el checkpoint Stage 2; los resultados ZS de la iteración v2 (documento `_resul_v2_`) son válidos sin cambios.

---

## 8. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `outputs/results/{model}/v2/*` | Resultados v2 *(pendiente)* |
| `outputs/results/{model}/v1/{model}_{method}_finetuned_test_results.json` | Baseline v1 |
| `slurm/mendieta/v2/vlm_classify_{model}_ft.sh` | SLURM v2 con post-mv a `results/{model}/v2/` |
| `outputs/checkpoints/stage2_{model}_v2/best_model.pt` | Checkpoint Stage 2 v2 (cluster) |
| [ejecuciones.md](../ejecuciones.md) | Registro cronológico de envíos |
| [reportes_mejoras_v2_plan_20260510.md](../ideas/reportes_mejoras_v2_plan_20260510.md) | Plan original del Stage 2 v2 |
