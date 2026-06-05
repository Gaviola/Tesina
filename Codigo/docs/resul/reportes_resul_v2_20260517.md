# Generación de Reportes — Resultados v2 (Stage 2 v2: epochs=10 + fix A2)

**Fecha de envío de jobs (iteración 1):** 2026-05-17
**Fecha de re-envío (iteración 2, reordenando datasets):** 2026-05-25
**Fecha de análisis (aproximación sobre reportes parciales):** 2026-06-02
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:**
- 1154213 (LLaVA-Med v2 it1) — FAILED por timeout 48h, 2600/22004 procesados (solo MM-SkinQA).
- 1154214 (Mini-VLM v2 it1) — FAILED por timeout 48h, 7120/22004 procesados (solo MM-SkinQA).
- **1154471 (LLaVA-Med v2 it2)** — FAILED por timeout 48h **de nuevo**, murió DENTRO de HAM10000 (2587/10015). SkinCoT nunca alcanzado.
- **1154472 (Mini-VLM v2 it2)** — FAILED por timeout 48h **de nuevo**, murió DENTRO de HAM10000 (6855/10015). SkinCoT nunca alcanzado.

**Checkpoints:** `outputs/checkpoints/stage2_{llava_med,mini_vlm}_v2/best_model.pt`
**Estado:** *Iteración cerrada con APROXIMACIÓN. La generación v2 nunca completó HAM10000 (jobs timeout × 2) y dejó SkinCoT en 0 reportes — ver §2.3 (causa raíz). El número de gating (`diagnostic_consistency` HAM10000) se obtuvo igual reconstruyendo `gt_label` localmente sobre el prefijo generado (estadísticamente representativo, ver §4.0). Veredicto en §8: **NO cumple gating**.*

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

### 2.3 Causa raíz del timeout (it.2 también falló) — diagnóstico 2026-06-02

Los re-envíos 1154471/1154472 **volvieron a hacer timeout a las 48h** (`State: FAILED ...
CANCELLED DUE to SIGNAL Terminated`), esta vez **muriendo todavía dentro de HAM10000**:

| Job | Modelo | HAM10000 generados | SkinCoT | MM-SkinQA |
|-----|--------|--------------------|---------|-----------|
| 1154471 | LLaVA-Med | 2587 / **10015** | **0** | 2601 (resto de it.1) |
| 1154472 | Mini-VLM | 6855 / **10015** | **0** | 7129 (resto de it.1) |

**El "fix de orden invertido" trató el síntoma, no la causa.** La causa real:

1. El SLURM corre `generate_report.py --images_dir data/processed/HAM10000`, que itera **las
   10015 imágenes completas**, NO el split de test. El plan asumió "HAM ≈1.5k" → error de ~7×.
2. Throughput de generación: LLaVA-Med ≈ **1,1 min/imagen** (`max_tokens=512`, una imagen por
   vez, sin batch). 10015 × 1,1 min ≈ **7,6 días** → imposible en la ventana de 48h. Mini-VLM es
   más rápido (~0,4 min/img) pero tampoco termina 10015. Por eso **ninguno llega a SkinCoT**.
3. **Regresión adicional:** el SLURM v2 omitió `--label_csv` para HAM, así que los reportes v2
   tienen `gt_label` vacío (en v1 venía poblado por una versión vieja del script). Se reconstruyó
   localmente con `scripts/enrich_reports.py` (mapeo `image_id → dx → nombre completo`).

**Implicancia para v3:** el paso de generación del plan v3 usa el mismo script con el mismo bug.
Los fixes de scope (HAM→test split, re-agregar `--label_csv`, recortar MM-SkinQA, evaluar
`max_tokens` 512→256) deben bakearse en v3 o la generación v3 falla idéntico.

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

## 4. Resultados v2 (aproximación sobre reportes parciales)

### 4.0 Validez de la aproximación

HAM10000 y MM-SkinQA quedaron **parciales** (HAM nunca completó; ver §2.3). Los reportes
existentes son un **prefijo por orden de ISIC-id**. Como HAM10000 no está ordenado por clase,
el prefijo conserva la distribución diagnóstica del dataset completo, lo que hace la
aproximación estadísticamente sólida:

| Clase | Full HAM | Prefijo LLaVA (n=2587) | Prefijo Mini (n=6855) |
|-------|----------|------------------------|------------------------|
| nevus | 66.9% | 68.8% | 69.0% |
| benign keratosis | 11.0% | 11.4% | 10.9% |
| melanoma | 11.1% | 8.3% | 8.4% |
| basal cell carcinoma | 5.1% | 4.8% | 5.3% |
| actinic keratosis | 3.3% | 3.9% | 3.8% |
| vascular lesion | 1.4% | 1.6% | 1.3% |
| dermatofibroma | 1.1% | 1.1% | 1.2% |

Desvío máximo ~3 pp (melanoma, levemente subrepresentado). Para el gating (`diagnostic_consistency`
sobre HAM, dominado por nevus) el prefijo es representativo. **SkinCoT v2 = 0 reportes → N/A.**

Comandos usados:
```bash
python scripts/mendieta/sync_down.py --reports
# reconstruir gt_label en los reportes v2 (reusa DX_TO_FULL de enrich_reports.py)
python scripts/evaluate_reports.py --model llava_med --level 2 --dataset v2/HAM10000 --output_dir outputs/results/llava_med/v2/approx
python scripts/evaluate_reports.py --model llava_med --level 1 --dataset v2/mmskin    --output_dir outputs/results/llava_med/v2/approx
# (y el combo mini_vlm)
```

### 4.1 Nivel 1 (métricas automáticas) — MM-SkinQA

| Modelo | Dataset | CIDEr v1 (re-eval) | CIDEr v2 | Δ | BLEU-4 v2 | ROUGE-L v2 | METEOR v2 | BERTScore v2 |
|--------|---------|---------------------|----------|---|----------|------------|-----------|--------------|
| LLaVA-Med | MM-SkinQA (n=2601) | 0.0103 | 0.0098 | −0.0005 | 0.0008 | 0.0312 | 0.0810 | 0.6580 |
| Mini-VLM | MM-SkinQA (n=7129) | 0.0069 | 0.0078 | +0.0009 | 0.0015 | 0.0536 | 0.1036 | 0.6991 |
| LLaVA-Med | SkinCoT | 0.0115 | *N/A (0 reportes)* | — | — | — | — | — |
| Mini-VLM | SkinCoT | 0.0388 | *N/A (0 reportes)* | — | — | — | — | — |

BLEU-4/CIDEr planos y ~0 en ambos: los reportes no calzan léxicamente con los captions de
MM-SkinQA. BERTScore ~0.66–0.70 es el piso semántico (no discrimina calidad). **Sin mejora
v1→v2 en Nivel 1.**

### 4.2 Nivel 2 (NER clínico) — HAM10000

| Modelo | Dataset | Recall v1 (re-eval) | Recall v2 | Δ | Consistency v1 (re-eval) | Consistency v2 | Δ |
|--------|---------|---------------------|-----------|---|--------------------------|----------------|---|
| LLaVA-Med | HAM10000 (n=2587) | 0.4569 | **0.8242** | **+0.367** | 0.7179 | **0.6336** | **−0.084** |
| Mini-VLM | HAM10000 (n=6855) | 0.6068 | **0.5463** | −0.061 | 0.3527 | **0.2289** | **−0.124** |
| LLaVA-Med | SkinCoT | 0.3709 | *N/A* | — | 0.2038 | *N/A* | — |
| Mini-VLM | SkinCoT | 0.5661 | *N/A* | — | 0.3401 | *N/A* | — |

Backend NER: `none` (diccionario dermatológico; SciSpaCy no instalado) — mismo backend que la
re-eval v1, comparación consistente.

---

## 5. Análisis

1. **Métricas automáticas (Nivel 1): sin cambio.** BLEU-4/CIDEr siguen ~0 en v2. Los 10 epochs
   no acercaron los reportes al estilo de los captions de referencia.
2. **Diagnostic consistency (gating) REGRESA en ambos modelos:** LLaVA 0.72→0.63 (−0.084),
   Mini 0.35→0.23 (−0.124). Los 10 epochs + fix A1 **no mejoraron** la fidelidad diagnóstica;
   la empeoraron. **No cumple el criterio de éxito (consistency ↑ vs v1).**
3. **Clinical entity recall: divergente.** LLaVA salta fuerte (0.46→0.82) pero Mini baja
   (0.61→0.55). El salto de LLaVA es atribuible mayormente al **fix A1** (prompt correcto
   "Describe this skin lesion." → reportes más descriptivos), no a los epochs.
4. **Trade-off clave (recall ↑ pero consistency ↓ en LLaVA):** los reportes v2 son más ricos y
   verbosos (estilo "structured approach" / razonamiento CoT, visible en inspección del sample)
   pero **comprometen menos el diagnóstico correcto** — enumeran diferenciales en vez de afirmar.
   El "templating" anticipado en el plan v2 se manifestó como hedging diagnóstico.
5. **Caveat:** el delta v1→v2 mezcla dos cambios (10 epochs + fix A1), no aísla los epochs. Pero
   la dirección del gating es inequívoca: empeora.
6. **Consistencia con clasificación:** v2 falla gating en *ambos* frentes — clasificación
   (class collapse) y generación (consistency regresa). **NOTA (2026-06-03):** la hipótesis de
   causa raíz compartida (imbalance NV/MEL) fue **refutada** — ver
   [vlm_clasificacion_resul_v3 §5.4](vlm_clasificacion_resul_v3_20260517.md). El collapse de
   clasificación es zero-shot y de dominio (dermatoscopía); la regresión de consistency de
   generación es estilo CoT (hedging), un problema distinto. No comparten causa.

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

**Veredicto: NO CUMPLE GATING (cerrado con aproximación, 2026-06-02).**

El criterio de éxito (`diagnostic_consistency` HAM10000 ↑ vs v1 re-evaluado) **no se cumple**:
regresa −0.084 (LLaVA) y −0.124 (Mini). Los 10 epochs + fix A1 no rompieron nada a favor; los
reportes son más verbosos pero diagnósticamente menos comprometidos. Nivel 1 plano.

El número de gating se obtuvo por **aproximación** (reconstrucción de `gt_label` sobre el prefijo
representativo, §4.0) sin necesidad de re-correr generación — los jobs habían fallado por timeout
(§2.3) pero el dato existía en los reportes parciales.

**Decisión (2026-06-02): Camino B — pivotear a v3 sin re-correr v2.** Como (a) ya tenemos el
número de gating de v2 y (b) confirma que v2 falla, no se justifica quemar cola re-corriendo v2
solo para refinar un baseline negativo (SkinCoT v2 es métrica secundaria, no gating). Se va
directo al [plan v3 de class-balanced sampling](../ideas/reportes_mejoras_v3_class_weights_plan_20260525.md),
**bakeando los fixes de scope de generación de §2.3** (HAM→test split, re-agregar `--label_csv`,
recortar MM-SkinQA, evaluar `max_tokens` 512→256) para que la generación v3 sí complete los 3
datasets. El v2-aproximado de este doc es el baseline contra el cual se comparará v3.

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
