# Generación de Reportes — Resultados v2 (Stage 2 v2: epochs=10 + fix A2)

**Fecha de envío de jobs:** 2026-05-17
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:** 1154213 (LLaVA-Med v2), 1154214 (Mini-VLM v2)
**Datasets:** MM-SkinQA, HAM10000, SkinCoT (los 3 procesados por el mismo job, en ese orden)
**Checkpoints:** `outputs/checkpoints/stage2_{llava_med,mini_vlm}_v2/best_model.pt`
**Estado:** *Pendiente — jobs en cola Mendieta, espera estimada 5-7 días*

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

| Job ID | Modelo | Datasets | Tiempo SLURM máx |
|--------|--------|----------|------------------|
| 1154213 | LLaVA-Med | MM-SkinQA + HAM10000 + SkinCoT | 2 días |
| 1154214 | Mini-VLM | MM-SkinQA + HAM10000 + SkinCoT | 2 días |

**Protocolo si timeout:** los scripts `slurm/mendieta/v2/generate_reports_{model}.sh`
escriben en `outputs/generated_reports/{model}/v2/{dataset}/{ISIC_id}_report.json`
de a uno. `generate_report.py` tiene resume defensivo (skip de reportes ya existentes).
**Si el job se interrumpe por SLURM time-limit (48h), re-enviar el mismo job (`submit.py gen_{model}_v2`) y continuará donde quedó.** Documentar las re-enviadas en este archivo.

Output esperado:
- `outputs/generated_reports/llava_med/v2/{HAM10000,mmskin,skincare}/*.json`
- `outputs/generated_reports/mini_vlm/v2/{HAM10000,mmskin,skincare}/*.json`

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

## 7. Bitácora de re-envíos *(actualizar si hay timeouts)*

> Formato: `<fecha> <job_id> <modelo> <datasets pendientes> <razón>`

(Sin entradas aún.)

---

## 8. Archivos de referencia

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
