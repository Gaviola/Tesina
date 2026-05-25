# Generación de Reportes — Resultados v2 (Stage 2 v2: epochs=10 + fix A2)

**Fecha de envío de jobs (iteración 1):** 2026-05-17
**Fecha de re-envío (iteración 2, reordenando datasets):** 2026-05-25
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:**
- 1154213 (LLaVA-Med v2 it1) — FAILED por timeout 48h, 2600/22004 procesados (solo MM-SkinQA).
- 1154214 (Mini-VLM v2 it1) — FAILED por timeout 48h, 7120/22004 procesados (solo MM-SkinQA).
- **1154471 (LLaVA-Med v2 it2)** — re-envío con orden ham→skincare→mmskin. *En cola/ejecución.*
- **1154472 (Mini-VLM v2 it2)** — re-envío con orden ham→skincare→mmskin. *En cola/ejecución.*

**Checkpoints:** `outputs/checkpoints/stage2_{llava_med,mini_vlm}_v2/best_model.pt`
**Estado:** *Parcial — solo MM-SkinQA tiene reportes generados (incompletos); HAM10000 y SkinCoT pendientes hasta que terminen los re-envíos 1154471/1154472.*

---

## 1. Motivación

Iteración v2 con dos cambios respecto a la baseline v1 (documentada en
[reportes_resul_v1_20260503.md](reportes_resul_v1_20260503.md)):

1. **Stage 2 v2 (epochs=10 vs 3):** mejor convergencia esperada según el sweep t04.
2. **Fix A1 (`scripts/generate_report.py`):** el `REPORT_PROMPT` ahora coincide con la
   instrucción del Stage 2 ("Describe this skin lesion."). En v1 había mismatch.
3. **Fix A2 (`src/evaluation/clinical_ner.py`):** `_DIAGNOSIS_SYNONYMS` ampliado con
   etiquetas SkinCaRe + normalización folder-names en `_normalize_label()`.

Para aislar el efecto del re-entrenamiento del fix de evaluación, se ejecutó una
**re-evaluación local del baseline v1 con el código nuevo** (sección 3). La comparación
honesta es: v1 re-evaluado vs v2.

---

## 2. Diseño experimental

### Iteración 1 (envío 2026-05-17): orden original mmskin → ham10000 → skincare

| Job ID  | Modelo    | Datasets enqueued                     | Tiempo SLURM máx |
|---------|-----------|----------------------------------------|------------------|
| 1154213 | LLaVA-Med | mmskin + HAM10000 + SkinCoT (orden 1) | 2 días           |
| 1154214 | Mini-VLM  | mmskin + HAM10000 + SkinCoT (orden 1) | 2 días           |

Ambos jobs hicieron timeout en 48h. **Solo se procesó MM-SkinQA** (parcialmente) en cada uno:

| Job | Reportes MM-SkinQA | Reportes HAM10000 | Reportes SkinCoT |
|-----|--------------------|--------------------|-------------------|
| 1154213 | 2600/22004 (11.8%) | **0**              | **0**             |
| 1154214 | 7120/22004 (32.4%) | **0**              | **0**             |

Sin reportes HAM10000 no se puede evaluar `diagnostic_consistency` (la métrica gating de la iteración). Esto motiva la **iteración 2**.

### Iteración 2 (re-envío 2026-05-25): orden invertido ham10000 → skincare → mmskin

Cambio en `slurm/mendieta/v2/generate_reports_{llava,mini}.sh`: se reordenaron los bloques `if [[ "$DATASETS" == ...` para procesar primero los datasets críticos (HAM10000 ≈1.5k y SkinCoT ≈1.5k imágenes) antes de empezar MM-SkinQA (~22k). El resume defensivo de `generate_report.py` salta los reportes MM-SkinQA ya escritos por la iteración 1.

| Job ID  | Modelo    | Datasets (orden)                 | Tiempo SLURM máx |
|---------|-----------|----------------------------------|------------------|
| 1154471 | LLaVA-Med | HAM10000 → SkinCoT → MM-SkinQA | 2 días           |
| 1154472 | Mini-VLM  | HAM10000 → SkinCoT → MM-SkinQA | 2 días           |

**Protocolo:** los scripts escriben `outputs/generated_reports/{model}/v2/{dataset}/{ISIC_id}_report.json`
de a uno. Si la iteración 2 también hace timeout, se garantiza que al menos HAM10000 + SkinCoT estarán completos antes de seguir con MM-SkinQA en una iteración 3.

Output esperado:
- `outputs/generated_reports/llava_med/v2/{HAM10000,skincare,mmskin}/*.json`
- `outputs/generated_reports/mini_vlm/v2/{HAM10000,skincare,mmskin}/*.json`

---

## 3. Baseline v1 corregido (re-evaluado con fix A2)

Reportes v1 originalmente generados el 2026-05-03 (jobs antiguos),
re-evaluados localmente el 2026-05-17 usando `scripts/evaluate_reports.py` con el
`clinical_ner.py` actualizado.

**Comando ejecutado:**
```bash
python scripts/evaluate_reports.py --model llava_med --dataset v1/HAM10000 --level 2 \
    --output_dir outputs/results/llava_med/v1/reeval
# (y permutaciones de modelo × dataset × level)
```

### 3.1 Nivel 1 (métricas automáticas con referencia) — v1 re-evaluado

CIDEr extraído del JSON; BLEU/ROUGE/METEOR/BERTScore presentes en los archivos
`outputs/results/{model}/v1/reeval/level1_{model}_results.json` (no listados aquí
por brevedad — consultar el JSON).

| Modelo | Dataset | CIDEr (v1 re-eval) |
|--------|---------|---------------------|
| LLaVA-Med | MM-SkinQA | 0.0103 |
| LLaVA-Med | SkinCoT | 0.0115 |
| Mini-VLM | MM-SkinQA | 0.0069 |
| Mini-VLM | SkinCoT | 0.0388 |

### 3.2 Nivel 2 (NER clínico) — v1 re-evaluado con fix A2

| Modelo | Dataset | Clinical Entity Recall | Diagnostic Consistency |
|--------|---------|------------------------|------------------------|
| LLaVA-Med | HAM10000 | 0.4569 | **0.7179** (era 0.7147 antes) |
| LLaVA-Med | MM-SkinQA | 0.5333 | — (sin gt_label) |
| LLaVA-Med | SkinCoT | 0.3709 | **0.2038** (era ~0% pre-fix) |
| Mini-VLM | HAM10000 | 0.6068 | **0.3527** (era 0.3134 antes) |
| Mini-VLM | MM-SkinQA | 0.3844 | — (sin gt_label) |
| Mini-VLM | SkinCoT | 0.5661 | **0.3401** (era ~0% pre-fix) |

**Hallazgo principal del fix A2:** Diagnostic consistency en SkinCoT pasa de ≈0% a
0.20 (LLaVA-Med) y 0.34 (Mini-VLM). El bug pre-fix era que `clinical_ner.py` no
reconocía los folder-names de SkinCAP (`mel`, `nv`, `bcc`, etc.) sin normalización,
y `_DIAGNOSIS_SYNONYMS` no incluía las etiquetas que SkinCaRe usa internamente.

Diagnostic consistency en HAM10000 también mejora ligeramente para ambos modelos
(LLaVA: 0.7147→0.7179; Mini-VLM: 0.3134→0.3527), confirmando que el fix amplía
la cobertura de sinónimos.

---

## 4. Resultados v2 *(pendiente — completar tras descarga)*

### 4.1 Nivel 1 (métricas automáticas)

> **[COMPLETAR cuando terminen jobs 1154213/1154214 y se descarguen reportes]**
>
> ```bash
> python scripts/mendieta/sync_down.py --reports
> python scripts/evaluate_reports.py --model llava_med --dataset v2/mmskin --level 1 \
>     --output_dir outputs/results/llava_med/v2
> # repetir para los 4 combos (model × {mmskin, skincare})
> ```

| Modelo | Dataset | CIDEr v1 (re-eval) | CIDEr v2 | Δ | BLEU-4 v2 | ROUGE-L v2 | METEOR v2 | BERTScore v2 |
|--------|---------|---------------------|----------|---|----------|------------|-----------|--------------|
| LLaVA-Med | MM-SkinQA | 0.0103 | *pend* | — | *pend* | *pend* | *pend* | *pend* |
| LLaVA-Med | SkinCoT | 0.0115 | *pend* | — | *pend* | *pend* | *pend* | *pend* |
| Mini-VLM | MM-SkinQA | 0.0069 | *pend* | — | *pend* | *pend* | *pend* | *pend* |
| Mini-VLM | SkinCoT | 0.0388 | *pend* | — | *pend* | *pend* | *pend* | *pend* |

### 4.2 Nivel 2 (NER clínico)

> **[COMPLETAR]**

| Modelo | Dataset | Recall v1 (re-eval) | Recall v2 | Δ | Consistency v1 (re-eval) | Consistency v2 | Δ |
|--------|---------|---------------------|-----------|---|--------------------------|----------------|---|
| LLaVA-Med | HAM10000 | 0.4569 | *pend* | — | 0.7179 | *pend* | — |
| LLaVA-Med | MM-SkinQA | 0.5333 | *pend* | — | — | — | — |
| LLaVA-Med | SkinCoT | 0.3709 | *pend* | — | 0.2038 | *pend* | — |
| Mini-VLM | HAM10000 | 0.6068 | *pend* | — | 0.3527 | *pend* | — |
| Mini-VLM | MM-SkinQA | 0.3844 | *pend* | — | — | — | — |
| Mini-VLM | SkinCoT | 0.5661 | *pend* | — | 0.3401 | *pend* | — |

---

## 5. Análisis *(pendiente)*

> **[COMPLETAR tras resultados]** Cubrir:
> 1. ¿Los 10 epochs del Stage 2 v2 mejoran las métricas automáticas (BLEU/ROUGE) vs v1?
> 2. ¿Diagnostic consistency en HAM10000 mejora? Eso sería evidencia de que el modelo aprendió mejor a mencionar el diagnóstico correcto.
> 3. ¿Clinical entity recall sube en MM-SkinQA y SkinCoT? Indicaría reportes morfológicamente más ricos.
> 4. **Trade-off esperado:** más epochs → mejor fit al estilo SkinCaRe, pero también más riesgo de "templating" (reportes genéricos). Inspección manual de un sample (Nivel 3) puede detectar esto.

---

## 6. Caveats

- **Timeout 2 días por job en Mendieta:** los 3 datasets pueden no completarse en una sola corrida.
  Si terminan parcialmente, re-enviar (resume defensivo en `generate_report.py`). Registrar
  re-envíos abajo.
- **Cola Mendieta:** 5-7 días al momento de envío.
- **No tocar reportes v1:** quedaron en `outputs/generated_reports/{model}/v1/`. La re-evaluación de §3 se hizo sobre esos archivos sin regenerar.
- **Fix A1 afecta v2 (no v1):** el `REPORT_PROMPT` corregido se aplica solo a los nuevos
  reportes v2. Los v1 fueron generados con el prompt viejo. Esto es una diferencia "real"
  entre v1 y v2 además del checkpoint.

---

## 7. Bitácora de re-envíos

> Formato: `<fecha> <job_id> <modelo> <datasets pendientes> <razón>`

- **2026-05-25**: jobs 1154471 (LLaVA-Med) y 1154472 (Mini-VLM) — re-envío de gen v2 con
  **orden invertido** (HAM10000 → SkinCoT → MM-SkinQA). Razón: los jobs originales
  (1154213/1154214) hicieron timeout procesando solo MM-SkinQA y dejaron HAM10000 + SkinCoT
  en 0 reportes, impidiendo evaluar `diagnostic_consistency` (criterio gating). Cambio
  aplicado en `slurm/mendieta/v2/generate_reports_{llava,mini}.sh`. Resume defensivo
  preservará los reportes parciales de MM-SkinQA ya generados.

## 8. Estado del análisis y siguiente paso

**Veredicto: PARCIAL — pendiente de los re-envíos 1154471/1154472.**

El análisis de éxito definido en §3 (ver criterios en
[vlm_clasificacion_resul_v3_20260517.md §3](vlm_clasificacion_resul_v3_20260517.md))
requiere `diagnostic_consistency` en HAM10000 ≥ +0.03 vs v1 re-evaluado. Ese número
no existe aún. La conclusión binaria se completa cuando vuelvan los re-envíos
(cola Mendieta + ejecución estimada: 5-7 días).

**No bloquea el plan v3 de clasificación:** el diagnóstico técnico de §5.2 del resul
doc de clasificación (imbalance + objective como causa raíz) es independiente de la
calidad de los reportes generados. El [plan v3 de class weights](../ideas/reportes_mejoras_v3_class_weights_plan_20260525.md)
se inicia ahora; la evaluación de generación v2 (cuando llegue) servirá como baseline
para comparar contra v3.

---

## 9. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `outputs/generated_reports/{model}/v2/*` | Reportes generados v2 *(pendiente)* |
| `outputs/generated_reports/{model}/v1/*` | Baseline v1 (intacto) |
| `outputs/results/{model}/v1/reeval/level{1,2}_{model}_results.json` | Re-eval v1 con fix A2 |
| `outputs/results/{model}/v2/level{1,2}_{model}_results.json` | Métricas v2 *(pendiente)* |
| `slurm/mendieta/v2/generate_reports_{llava,mini}.sh` | SLURM v2 |
| `outputs/checkpoints/stage2_{model}_v2/best_model.pt` | Checkpoint Stage 2 v2 (cluster) |
| [reportes_resul_v1_20260503.md](reportes_resul_v1_20260503.md) | Baseline v1 (pre-fix) |
| [reportes_mejoras_v2_plan_20260510.md](../ideas/reportes_mejoras_v2_plan_20260510.md) | Plan original |
| [ejecuciones.md](../ejecuciones.md) | Registro cronológico de envíos |
