# Clasificación VLM — Resultados v3 (Stage 2 v2: epochs=10)

**Fecha de envío de jobs:** 2026-05-17
**Fecha de análisis:** 2026-05-25
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:** 1154209 (LLaVA-Med FT lik), 1154210 (Mini-VLM FT lik), 1154211 (LLaVA-Med FT CoT), 1154212 (Mini-VLM FT CoT)
**Dataset:** HAM10000 Test Set (n=1503, 7 clases)
**Checkpoints:** `outputs/checkpoints/stage2_{llava_med,mini_vlm}_v2/best_model.pt` (10 epochs, lr=2.495e-5, lora_r=64)
**Estado:** **Completado** — 4/4 jobs COMPLETED, exit code 0

---

## 1. Motivación

El Stage 2 original (v1) usó `epochs=3` por restricción de tiempo. El sweep de HPs ([reportes_mejoras_v2_plan_20260510.md](../ideas/reportes_mejoras_v2_plan_20260510.md))
encontró que `val_loss` seguía descendiendo en la época 5/5 del trial t04 (mejor configuración). Stage 2 v2 re-entrena con `epochs=10` y los mismos HPs del t04, esperando capturar mejor convergencia y traducirse en mejoras en clasificación VLM (likelihood + CoT) y generación.

Este documento cubre la clasificación; el de generación es [reportes_resul_v2_20260517.md](reportes_resul_v2_20260517.md).

---

## 2. Diseño experimental

Solo se re-corren los 4 jobs FT (los ZS no cambian, ya que el checkpoint Stage 2 no afecta inferencia zero-shot):

| Job ID  | Modelo    | Método     | ZS/FT  | Wall-clock | Estado SLURM |
|---------|-----------|------------|--------|------------|--------------|
| 1154209 | LLaVA-Med | likelihood | FT v2  | 7h 56min   | COMPLETED    |
| 1154210 | Mini-VLM  | likelihood | FT v2  | 8h 45min   | COMPLETED    |
| 1154211 | LLaVA-Med | CoT        | FT v2  | 10h 54min  | COMPLETED    |
| 1154212 | Mini-VLM  | CoT        | FT v2  | 8h 58min   | COMPLETED    |

Output: `outputs/results/{model}/v2/{model}_{method}_finetuned_{predictions,test_results}.json`
(post-mv aplicado por los scripts SLURM `slurm/mendieta/v2/vlm_classify_*_ft.sh`).

---

## 3. Baseline de comparación y criterios de éxito

Resultados de la iteración v2 (Stage 2 v1, epochs=3, documentados en
[vlm_clasificacion_resul_v2_20260510.md](vlm_clasificacion_resul_v2_20260510.md)):

| Modelo    | Método      | Acc    | F1-w  | Sens. macro | Notas                              |
|-----------|-------------|--------|-------|-------------|-------------------------------------|
| LLaVA-Med | FT lik (v1) | 0.1344 | 0.098 | 0.163       | Re-envío post-fix LoRA rank        |
| LLaVA-Med | FT CoT (v1) | 0.0812 | 0.029 | 0.119       | 456 UNKNOWN (CoT format failure)   |
| Mini-VLM  | FT lik (v1) | 0.6660 | 0.536 | 0.142       | **Class collapse hacia NV**        |
| Mini-VLM  | FT CoT (v1) | 0.1153 | 0.040 | 0.141       | —                                   |

**Criterios de éxito** (definidos antes del análisis, ver [ejecuciones.md](../ejecuciones.md) y discusión `grill-me` 2026-05-25):

1. **Primario / gating:** romper class collapse, i.e. `sens_macro > 1/7 ≈ 0.143` para al menos un modelo competitivo (LLaVA-Med FT lik o Mini-VLM FT lik). Criterio **obligatorio** para considerar cierre de Fase 2.
2. **Secundario:** mejorar F1-weighted respecto al mismo modelo+método en v1.
3. **Contextual:** acercarse al SOTA (Swin-Tiny v4: F1=0.882) dentro de un margen razonable (~8pp).

---

## 4. Resultados v2

### 4.1 Tabla comparativa v1 vs v2 (HAM10000 test, n=1503)

| Modelo    | Método  | Acc v1 | F1-w v1 | Sens v1 | Acc v2     | F1-w v2    | Sens v2    | Δ F1-w     | Δ Sens     |
|-----------|---------|--------|---------|---------|------------|------------|------------|------------|------------|
| LLaVA-Med | FT lik  | 0.134  | 0.098   | 0.163   | **0.179**  | **0.198**  | 0.137      | **+0.100** | **−0.026** |
| LLaVA-Med | FT CoT  | 0.081  | 0.029   | 0.119   | 0.168      | 0.059      | **0.179**  | +0.030     | **+0.060** |
| Mini-VLM  | FT lik  | 0.666  | 0.536   | 0.142   | 0.660      | 0.532      | 0.141      | −0.004     | −0.001     |
| Mini-VLM  | FT CoT  | 0.115  | 0.040   | 0.141   | 0.111      | 0.026      | 0.145      | −0.014     | +0.004     |

**Lectura rápida:**
- **LLaVA-Med FT lik:** F1 sube +0.100 absoluto (+102% relativo) y acc +0.045. Mejora numérica clara, pero `sens_macro` **baja** de 0.163 a 0.137 (debajo de 1/7).
- **LLaVA-Med FT CoT:** sens_macro 0.179 (rompe el umbral), pero la métrica está contaminada por `UNKNOWN=1223/1503` (81%): solo 280 muestras válidas.
- **Mini-VLM FT lik:** prácticamente sin cambios (Δacc=−0.006, Δsens=−0.001). Stage 2 v2 **no rompe el class collapse** del v1.
- **Mini-VLM FT CoT:** estanco; sens_macro 0.145 ≈ 1/7 (marginal).

### 4.2 Sensitivity per class — ¿qué clases predice cada combo?

LLaVA-Med FT lik v2 (sens por clase):

| mel   | nv    | bcc   | akiec | bkl   | df    | vasc  |
|-------|-------|-------|-------|-------|-------|-------|
| 0.563 | 0.164 | 0.078 | 0.000 | 0.006 | 0.059 | 0.091 |

Distribución de predicciones razonablemente diversa (no colapsa a una sola clase) pero con sesgo fuerte a `mel` y muy baja sensitivity en clases minoritarias (akiec, bkl, df, vasc). El sens_macro baja porque se "ahoga" en las clases donde acierta ≈0%.

Mini-VLM FT lik v2 (sens por clase):

| mel   | nv    | bcc   | akiec | bkl   | df    | vasc  |
|-------|-------|-------|-------|-------|-------|-------|
| 0.000 | 0.986 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

**Class collapse perfecto** hacia NV (clase mayoritaria, 66.9% del test set). Idéntico patrón a v1.

Mini-VLM FT CoT v2 (sens por clase):

| mel   | nv    | bcc   | akiec | bkl   | df    | vasc  |
|-------|-------|-------|-------|-------|-------|-------|
| 0.976 | 0.001 | 0.039 | 0.000 | 0.000 | 0.000 | 0.000 |

Class collapse, esta vez hacia `mel`. El modelo se "convenció" de que casi todo es melanoma. El cambio de patrón (NV→MEL) entre lik y CoT sugiere que la dirección del collapse depende de cómo se construya el output, no del aprendizaje real de discriminación.

LLaVA-Med FT CoT v2 (sens por clase, sobre 280 válidos):

| mel   | nv    | bcc   | akiec | bkl   | df    | vasc  |
|-------|-------|-------|-------|-------|-------|-------|
| 0.894 | 0.000 | 0.357 | 0.000 | 0.000 | 0.000 | 0.000 |

Predice solo `mel` o `bcc` cuando logra producir un diagnóstico válido. El sens_macro "alto" es engañoso porque solo 18.6% del test set generó output parseable.

### 4.3 Accuracy por prompt — método likelihood

| Modelo    | ZS/FT     | O1    | O2    | C1    | C2    |
|-----------|-----------|-------|-------|-------|-------|
| LLaVA-Med | FT (v1)   | n/a   | n/a   | n/a   | n/a   |
| LLaVA-Med | FT (v2)   | 0.192 | 0.159 | 0.200 | 0.203 |
| Mini-VLM  | FT (v1)   | 0.536 | 0.110 | 0.371 | 0.570 |
| Mini-VLM  | FT (v2)   | 0.329 | 0.116 | 0.113 | 0.181 |

**Observaciones:**
- LLaVA-Med v2 muestra valores parecidos en los 4 prompts (0.16–0.20), señal de que el ensemble likelihood está activo y no degenera a un único prompt.
- Mini-VLM v2 **regresiona** respecto a v1 en los prompts cerrados (C1 0.371→0.113, C2 0.570→0.181). Sin embargo el `accuracy` global (computado por ensemble) baja solo 0.006: el ensemble compensa la degradación per-prompt, pero al costo de un class collapse más pronunciado.

### 4.4 Tasa UNKNOWN — método CoT

| Modelo    | ZS/FT      | UNKNOWN  | %       |
|-----------|------------|----------|---------|
| LLaVA-Med | ZS (v2)    | 223/1503 | 14.8%   |
| LLaVA-Med | FT (v1)    | 456/1503 | 30.3%   |
| LLaVA-Med | FT (v2)    | **1223/1503** | **81.4%** |
| Mini-VLM  | ZS (v2)    | 7/1503   | 0.5%    |
| Mini-VLM  | FT (v1)    | 20/1503  | 1.3%    |
| Mini-VLM  | FT (v2)    | 1/1502   | 0.07%   |

**Regresión crítica en LLaVA-Med FT CoT v2:** la tasa de UNKNOWN sube de 30% (v1) a 81% (v2). El modelo, tras 10 epochs de Stage 2, parece haber "olvidado" cómo seguir el formato `Final diagnosis: <label>`. Es una forma de catastrophic forgetting sobre el formato estructurado.

---

## 5. Análisis

### 5.1 ¿Stage 2 v2 ayudó? Respuesta corta: **no para el criterio gating**

- **F1-weighted mejora solo en LLaVA-Med FT lik** (+0.100). En los otros 3 combos baja o queda igual.
- **Sens macro no rompe el class collapse** en ningún modelo competitivo:
  - LLaVA-Med FT lik: sens_macro **baja** (0.163→0.137), debajo del threshold 1/7.
  - Mini-VLM FT lik: sens_macro inalterado (0.142→0.141), perfect collapse a NV persiste.
- **Las "mejoras" de sens_macro en los combos CoT son artefactos**:
  - LLaVA-Med FT CoT: sens_macro 0.179 está calculado sobre 280 samples válidos (81% UNKNOWN). En la práctica no se puede confiar en esa métrica.
  - Mini-VLM FT CoT: collapse cambia de NV (v1) a MEL (v2). El sens_macro 0.145 está apenas marginal y refleja otro tipo de degeneración, no aprendizaje discriminativo.

### 5.2 Diagnóstico técnico: por qué Stage 2 v2 no resuelve el problema

El plan v2 atacaba **convergencia** (epochs=3→10). Los datos actuales sugieren que el cuello de botella no era convergencia sino **objective + imbalance**:

- El dataset de Stage 2 (SkinCaRe / SkinCAP / SkinCoT) tiene una distribución de diagnósticos sesgada hacia NV y MEL. Los pares imagen-texto de entrenamiento favorecen estas clases por frecuencia.
- LoRA con loss de cross-entropy plano amplifica la distribución de entrenamiento. Más epochs solo afianzan el sesgo aprendido en las primeras épocas.
- La evidencia: Mini-VLM v2 colapsa **más** que v1 hacia NV (sens NV 0.986 vs ~0.97 de v1), no menos.

### 5.3 Comparación contra SOTA

Mejor clasificador supervisado en este trabajo (Swin-Tiny sweep v4): F1=0.882, Acc=0.827.
Mejor VLM v2 en este trabajo: Mini-VLM FT lik v2 con F1=0.532, Acc=0.660.

Gap VLM vs supervisor en F1: **0.350 absoluto (~40% relativo)**. El gap es enorme y el sens_macro 0.141 muestra que la accuracy 0.660 es engañosa (NV-prior + dataset desbalanceado).

Mejor VLM SOTA (Skin-R1, FT+RL): Acc=0.879. Gap del Mini-VLM v2: ~22pp. Muy por encima del margen aceptable de 8pp.

### 5.4 CORRECCIÓN del §5.2 — re-diagnóstico (2026-06-03)

> **El diagnóstico de §5.2 ("imbalance + objective") es INCORRECTO. La premisa nunca se
> verificó contra los datos.** Re-diagnóstico al planificar v3:

**Evidencia 1 — los datos de entrenamiento NO están sesgados a NV/MEL** (medido sobre los datasets reales):
- **Stage 2 (SkinCoT, 2136 train):** 23 clases tipo DermNet, balanceadas ~6:1. La carpeta
  *"Melanoma Skin Cancer Nevi and Moles"* es **puesto 9 (76 samples, 3.6%)**, no domina.
- **Stage 1 (SkinCAP, 2492 train):** 179 clases, `melanocytic-nevi` top con **83 (3.3%)**, cola larga.
- → La afirmación de §5.2 ("SkinCaRe sesgada hacia NV y MEL ... NV es la clase más frecuente") es **falsa**.

**Evidencia 2 — el colapso existe en ZERO-SHOT, antes del fine-tuning:** sens_macro ZS = LLaVA lik
0.157, Mini lik 0.181, LLaVA CoT 0.143, Mini CoT 0.124 (todos ≈ 1/7). El FT no lo causa ni lo cambia
→ no puede ser un sesgo aprendido de SkinCoT.

**Evidencia 3 — cada combo colapsa a una clase ARBITRARIA distinta** (de las predicciones v2):
LLaVA lik→MEL 59%, LLaVA CoT→VASC 81%, Mini lik→NV 99%, Mini CoT→MEL 97%. Si fuera sesgo de
frecuencia, todos colapsarían a la misma clase. No lo hacen → el colapso depende del prompt/scoring,
no del contenido de la imagen.

**Evidencia 4 — los CNN supervisados sobre la MISMA HAM dermatoscópica dan F1=0.88** → HAM es
discriminable; el fallo es específico del VLM.

**Diagnóstico correcto:** el class collapse es una **limitación de capacidad de los VLMs** para la
clasificación dermatológica de grano fino. No es corregible por re-balanceo de Stage 2. El plan v3
(class-balanced sampling) queda **anulado** por esta premisa falsificada.

> **REFINAMIENTO (2026-06-04):** se testeó afirmativamente la hipótesis de "domain gap dermatoscopía"
> evaluando el VLM ZS sobre **foto clínica** (SkinCAP→7 clases HAM). **El domain gap NO se confirmó:**
> la clínica tampoco discrimina (sens_macro 0.106 LLaVA / 0.176 Mini, ≈ azar, incluso *peor* que HAM),
> y el modelo **colapsa a una clase distinta según el dominio** (HAM→NV/MEL, clínica→DF). Conclusión
> refinada: **no es un domain gap específico de dermatoscopía, sino una incapacidad general de grano
> fino** — la predicción está guiada por artefactos del prompt/likelihood, no por la imagen. Ver
> [vlm_domain_gap_clinica_resul_20260604.md](vlm_domain_gap_clinica_resul_20260604.md).

---

## 6. Decisión sobre actualización de tabla SOTA

Se agregan filas v2 a la Tabla 1 (sección "Este trabajo — VLMs likelihood/CoT"):

- `(c.lik.ft.v2)` LLaVA-Med 7B (Stage 2 v2) — F1=0.198, Acc=0.179, Sens=0.137
- `(c.cot.ft.v2)` LLaVA-Med 7B (Stage 2 v2) — F1=0.059, Acc=0.168, Sens=0.179 ± `UNKNOWN=81%`
- `(d.lik.ft.v2)` Mini-VLM (Stage 2 v2) — F1=0.532, Acc=0.660, Sens=0.141
- `(d.cot.ft.v2)` Mini-VLM (Stage 2 v2) — F1=0.026, Acc=0.111, Sens=0.145

Las filas v1 se mantienen (no se sobreescriben). El nota al pie debe explicitar que v2 **no rompe el class collapse** del v1.

---

## 7. Caveats

- **Comparabilidad limpia:** v1 y v2 usan el mismo dataset, splits, prompts (O1/O2/C1/C2 inalterados) y código de evaluación. El único cambio entre runs es `epochs=3→10` y el checkpoint Stage 2.
- **No se re-ejecutaron jobs ZS:** los métodos ZS no usan el checkpoint Stage 2. Los resultados ZS se siguen leyendo desde `outputs/results/{model}/v1/*` (no varían entre iteraciones de v1 y v2).
- **LLaVA-Med FT CoT con 81% UNKNOWN:** el dato `sens_macro=0.179` se reporta tal cual sale del script pero **no es comparable** con los otros combos por la alta tasa de UNKNOWN.

---

## 8. Conclusión y siguiente paso

**Veredicto: NO CUMPLE criterio gating.**

| Criterio                                                  | Resultado    |
|-----------------------------------------------------------|--------------|
| Romper class collapse (sens_macro > 0.143) en LLaVA-Med FT lik | **NO** (0.137) |
| Romper class collapse (sens_macro > 0.143) en Mini-VLM FT lik | **NO** (0.141) |
| Mejorar F1-weighted vs v1 en al menos un combo competitivo | **SÍ** (LLaVA-Med FT lik: +0.100) |
| Gap vs SOTA ≤ 8pp                                          | **NO** (gap ~22pp) |

Stage 2 v2 (epochs=10) **no es suficiente** para alcanzar el criterio mínimo de cierre de Fase 2 (class collapse roto).

> **NOTA (2026-06-03):** la causa de §5.2 ("imbalance + objective") fue **refutada** — ver §5.4.
> El colapso es zero-shot y los datos de entrenamiento no están sesgados a NV/MEL. Es una
> limitación de dominio (dermatoscopía) del VLM, no de convergencia ni de balance.

**Siguiente paso (revisado 2026-06-03): NO iterar v3 (class weights).** El re-diagnóstico (§5.4)
anula la premisa de v3. Re-enmarcar el class collapse como hallazgo (domain gap clínica→dermatoscopía)
y, si se quiere confirmar afirmativamente, evaluar el VLM en un test set de foto clínica (su dominio).
El plan [reportes_mejoras_v3_class_weights_plan](../ideas/reportes_mejoras_v3_class_weights_plan_20260525.md)
queda **EN PAUSA / anulado** (ver encabezado del plan).

---

## 9. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `outputs/results/{model}/v2/{model}_{lik,cot}_finetuned_test_results.json` | Métricas v2 |
| `outputs/results/{model}/v2/{model}_{lik,cot}_finetuned_predictions.json` | Predicciones por imagen v2 |
| `outputs/results/{model}/v1/{model}_{lik,cot}_finetuned_test_results.json` | Baseline v1 |
| `outputs/slurm_logs/{model}/115420{9,10,11,12}.{out,err}` | Logs SLURM v2 |
| `slurm/mendieta/v2/vlm_classify_{model}_ft.sh` | SLURM v2 con post-mv a `results/{model}/v2/` |
| `outputs/checkpoints/stage2_{model}_v2/best_model.pt` | Checkpoint Stage 2 v2 (cluster) |
| [ejecuciones.md](../ejecuciones.md) | Registro cronológico de envíos |
| [reportes_mejoras_v2_plan_20260510.md](../ideas/reportes_mejoras_v2_plan_20260510.md) | Plan original del Stage 2 v2 |
| [reportes_mejoras_v3_class_weights_plan_20260525.md](../ideas/reportes_mejoras_v3_class_weights_plan_20260525.md) | Plan v3 (class weights / focal loss) |
