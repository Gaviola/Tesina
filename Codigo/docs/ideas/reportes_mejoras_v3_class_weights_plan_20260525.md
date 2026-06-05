> ## ⛔ PLAN ANULADO (2026-06-03) — premisa falsificada
> El pilar de este plan (**class-balanced sampling** para romper el class collapse) asumía que
> el dataset de Stage 2 está sesgado a NV/MEL. **Es falso:** SkinCoT (Stage 2) son 23 clases
> DermNet balanceadas (NV/MEL en puesto 9, 3.6%) y SkinCAP (Stage 1) son 179 clases sin sesgo NV.
> Además **el colapso existe en zero-shot** (precede al fine-tuning) y **cada combo colapsa a una
> clase arbitraria distinta** (MEL/VASC/NV/MEL) → no es frecuencia, es incapacidad de discriminar
> dermatoscopía. Ver re-diagnóstico en
> [vlm_clasificacion_resul_v3 §5.4](../resul/vlm_clasificacion_resul_v3_20260517.md).
>
> **No ejecutar.** El class collapse es una limitación de dominio (clínica→dermatoscopía), no de
> balance. Lo que sobrevive del análisis de generación (hedging CoT, fixes de scope §2.4) se
> evaluará por separado si se decide una iteración de *solo generación*. Documento conservado como
> registro del razonamiento.

# Plan: Mejoras de Stage 2 — v3 (class-balanced sampling + commitment-line + fixes de generación)

**Fecha:** 2026-05-25
**Revisión:** 2026-06-02 (tras análisis gen v2 → decisión Camino B; se agrega intervención de
estilo *commitment-line* y fixes de scope de generación)
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Modelos:** LLaVA-Med 7B + LoRA, Mini-VLM (Phi-3.5-vision) + LoRA
**Referencias:**
- [vlm_clasificacion_resul_v3_20260517.md](../resul/vlm_clasificacion_resul_v3_20260517.md) (veredicto v2: no rompe class collapse)
- [reportes_resul_v2_20260517.md](../resul/reportes_resul_v2_20260517.md) (veredicto gen v2: NO cumple gating; consistency regresa −0.084/−0.124; §2.3 causa raíz del timeout)
- [reportes_mejoras_v2_plan_20260510.md](reportes_mejoras_v2_plan_20260510.md) (plan v2 cuyo objetivo se incumple)

---

## 1. Contexto y diagnóstico

La iteración v2 (Stage 2 con `epochs=10` en lugar de 3) **no rompe el class collapse**:

| Modelo+método           | sens_macro v1 → v2 | Veredicto                         |
|-------------------------|--------------------|-----------------------------------|
| LLaVA-Med FT lik        | 0.163 → 0.137      | **Empeora** (sigue debajo de 1/7) |
| Mini-VLM FT lik         | 0.142 → 0.141      | Persistencia del NV-collapse      |
| LLaVA-Med FT CoT        | 0.119 → 0.179      | Engañoso: 81% UNKNOWN             |
| Mini-VLM FT CoT         | 0.141 → 0.145      | Marginal, ahora colapsa a MEL     |

Diagnóstico (ver §5.2 del resul doc v3): el problema **no es convergencia** (más epochs no ayuda), sino **imbalance + objective**:

- SkinCaRe (~7k pares imagen-texto) tiene una distribución sesgada hacia NV y MEL.
- La loss autoregressive de cross-entropy plana amplifica la distribución de entrenamiento.
- Más epochs solo afianzan el sesgo aprendido.

**Hipótesis v3:** re-balancear lo que ve el modelo durante Stage 2 (clase efectiva uniforme) debería romper el class collapse, a costa potencial de leve degradación en accuracy global.

### 1.1 Segundo frente: la generación v2 también falla gating (análisis 2026-06-02)

El análisis aproximado de gen v2 ([reportes_resul_v2 §4-§8](../resul/reportes_resul_v2_20260517.md))
muestra que `diagnostic_consistency` en HAM10000 **regresa** vs v1: LLaVA 0.72→0.63 (−0.084),
Mini 0.35→0.23 (−0.124). El recall de LLaVA sube fuerte (0.46→0.82) **mientras** la consistency
baja → diagnóstico: los reportes v2 son verbosos en estilo **CoT** (heredado de los targets de
SkinCoT: *"To analyze the case, I will follow a structured approach... 1. High-Level Decision...
2. Narrowing Down..."*) y **enumeran diferenciales sin comprometer un diagnóstico**. Para un nevus
benigno el modelo gasta párrafos hipotetizando melanoma.

**Dos causas, dos intervenciones (v3 ataca ambas en un solo run):**
- **(a) imbalance** → modelo sesgado a clases mayoritarias (NV/MEL). Mecanismo de ambos fallos
  (clasificación *y* generación). → **class-balanced sampling** (§2.1).
- **(b) estilo CoT sin commitment** → aunque acierte la clase, no la afirma. → **commitment-line**
  en los targets (§2.2).

**Sinergia (clave para la atribución):** las dos intervenciones son complementarias, no redundantes.
La commitment-line sola, sin arreglar clasificación, haría que el modelo *afirme el diagnóstico
equivocado* (colapsa a NV) → no sube consistency en minoritarias. El balanceo solo, sin
commitment-line, mejora *qué* clase infiere pero el estilo CoT puede seguir sin afirmarla. Juntas:
balanceo arregla **cuál** diagnóstico, commitment-line arregla **que lo afirme**. Este es el relato
de atribución para la tesis (decisión 2026-06-02 de sumar estilo a v3, aceptando que v3 deja de ser
experimento de una sola variable).

**Decisión Camino B:** no se re-corre la generación v2 (su número de gating ya existe y falla);
se pivotea directo a v3 con los fixes de scope de generación bakeados (§2.4).

---

## 2. Diseño de la intervención

### 2.1 Cambio principal — Weighted sampling sobre SkinCaRe

**Archivo a modificar:** `src/training/two_stage.py` (función que construye el `DataLoader` de Stage 2) y/o `src/data/skincare.py` (donde se carga el dataset).

**Mecanismo:** sustituir el `RandomSampler` default por un `WeightedRandomSampler` con pesos por sample inversamente proporcionales a la frecuencia de su clase diagnóstica:

```python
from torch.utils.data import WeightedRandomSampler

# class_freq[c] = nº de samples con label diagnóstico c en SkinCaRe
weights_per_sample = [1.0 / class_freq[sample["label"]] for sample in dataset]
sampler = WeightedRandomSampler(
    weights=weights_per_sample,
    num_samples=len(dataset),
    replacement=True,
)
train_loader = DataLoader(dataset, batch_size=..., sampler=sampler, ...)
```

**Consideraciones de implementación:**

1. **Mapeo sample→clase diagnóstica:** SkinCaRe (SkinCAP + SkinCoT) tiene su diagnóstico en metadata. Verificar que `BaseDataset.__getitem__` exponga `label` o `metadata["diagnosis"]`. Si no existe, agregar al cargar el dataset.
2. **Granularidad:** la implementación más simple usa las 7 clases canónicas HAM10000 (mel/nv/bcc/akiec/bkl/df/vasc). SkinCaRe tiene 15+ diagnósticos — agruparlos al supersep HAM10000 (ya hay mapping en `clinical_ner.py:_DIAGNOSIS_SYNONYMS`).
3. **Validación:** mantener el split de val sin re-balanceo (`val_loader` usa sampler default). Re-balancear val invalida la comparación con val_loss de v1/v2.

### 2.2 Commitment-line en los targets de Stage 2 (intervención de estilo — INCLUIDA en v3)

**Objetivo:** que el modelo **afirme** un diagnóstico al final del reporte, en vez de enumerar
diferenciales sin comprometerse (causa (b) de §1.1).

**Mecanismo:** durante la construcción de los targets de Stage 2, append una frase de cierre
comprometida a cada `response`:

```python
# en el armado de targets de Stage 2 (src/data/skincare.py / two_stage.py)
COMMIT_TEMPLATE = "\n\nMost likely diagnosis: {dx}."
response = response.rstrip() + COMMIT_TEMPLATE.format(dx=sample_diagnosis_full)
```

donde `sample_diagnosis_full` es el diagnóstico en nombre completo (mel→melanoma, etc.), **el mismo
mapeo por-sample que el class-balanced sampler de §2.1 ya necesita** → comparten infraestructura
(una sola fuente de verdad para la etiqueta diagnóstica del sample).

**Consideraciones:**
1. **Reutiliza** el `DX_TO_FULL` / mapeo de `enrich_reports.py` y el `class_freq` de §2.1.
2. **No re-cura los reportes** (no es la opción 3 de "targets concisos"): preserva el cuerpo
   descriptivo (mantiene el recall alto de LLaVA) y solo agrega la línea de commitment al final.
3. **Espejo en inferencia:** la consistency se mide por NER sobre el texto generado; como el modelo
   aprende a emitir la línea, no hace falta cambiar `REPORT_PROMPT`. (Opcional: si en inspección la
   línea no aparece, reforzar el prompt — ver §2.4.)
4. **No es teaching-to-the-metric trivial:** la línea solo sube consistency si el diagnóstico
   afirmado es **correcto**, lo cual depende de que el modelo discrimine la clase → ahí entra el
   balanceo (§2.1). Ver sinergia en §1.1.

### 2.3 Opción postergada a v3.1 — focal loss sobre tokens de respuesta

Más invasivo y de impacto incierto en VLMs autoregressive. **Postergar a v3.1** si v3 (sampler +
commitment-line) no rompe el collapse.

Esquema: en lugar de la loss CE de HuggingFace, computar manualmente focal loss sobre los tokens que tienen `label != -100` (i.e., tokens del response, no del prompt):

```python
# pseudo-código en two_stage.py
logits = output.logits  # [B, L, V]
mask = (labels != -100)
ce = F.cross_entropy(logits[mask], labels[mask], reduction='none')
p_t = torch.exp(-ce)  # confidence of correct class
focal = (1 - p_t).pow(gamma) * ce
loss = focal.mean()
```

Con `gamma=2`. No es exactamente "class weights" sino "weighted by difficulty", pero ataca el mismo efecto: tokens fáciles (NV en contexto NV-saturado) reciben menos peso.

### 2.4 Fixes de scope de generación (bakeados en el paso de generación v3)

La generación v2 nunca completó por iterar las 10015 imgs de HAM (no el test split) a ~1,1 min/img
([reportes_resul_v2 §2.3](../resul/reportes_resul_v2_20260517.md)). Fixes obligatorios para que la
generación v3 complete los 3 datasets en 48h:

1. **Split-filtering unificado:** agregar a `scripts/generate_report.py` los args `--splits_file`
   + `--split test` para generar **solo sobre el test split** de cada dataset (los JSON ya existen:
   `data/splits/{ham10000,skincare_skincot,mmskin}_splits.json`). HAM pasa de 10015 → ~1500 imgs.
   Metodológicamente correcto (held-out test).
2. **Re-agregar `--label_csv`** para HAM en el SLURM (regresión que dejó `gt_label` vacío en v2).
   Apuntar al metadata; o reusar el `enrich_reports.py` post-hoc como fallback.
3. **`max_tokens` 512 → 256:** mitad de tiempo de generación; además acota el preámbulo CoT
   verboso (complementa la commitment-line de §2.2). Riesgo: truncar detalle → vigilar recall.
4. **MM-SkinQA acotado a su test split** (vía punto 1), no las 22k completas.

### 2.5 Lo que NO cambia respecto a v2

- **Stage 1:** no se re-entrena. Se reutiliza `outputs/checkpoints/stage1_{model}/best_model.pt`.
- **HPs:** se mantienen los del t04 (lr=2.495e-5, lora_r=64, lora_alpha=64, dropout=0.0).
- **Epochs:** 10 (como en v2). El sampler hace que cada época rote por más samples minoritarios; reducir epochs corre el riesgo de no converger al nuevo balance.
- **Datasets de Stage 2:** SkinCaRe (SkinCAP + SkinCoT) sin agregar MM-Skin (B1 sigue descartado).

---

## 3. Criterios de éxito v3

**Dos frentes con baseline v2 ya conocido (de los resul docs):**

1. **Gating clasificación (obligatorio para cierre F2):** romper class collapse,
   `sens_macro > 1/7 ≈ 0.143` en al menos un modelo competitivo (LLaVA-Med FT lik o Mini-VLM FT lik).
   Ideal: `sens_macro > 0.25` (discriminación real, no marginal). *Baseline v2: 0.137 (LLaVA lik),
   0.141 (Mini lik) — ambos por debajo de 1/7.*
2. **Secundario clasificación:** mejorar F1-weighted vs v2 en ≥1 combo. Accuracy global puede
   **bajar** levemente (esperado al re-balancear); lo importante es F1.
3. **Gating generación (ahora atacado directamente por la commitment-line):** `diagnostic_consistency`
   en HAM10000 **≥ +0.03 absoluto vs v2**. *Baseline v2 (aproximado, prefijo representativo):
   **LLaVA 0.634, Mini 0.229** → meta v3: ≥0.66 / ≥0.26.* Idealmente recuperar y superar v1
   (LLaVA 0.718, Mini 0.353) sin perder el recall ganado (LLaVA 0.82).
4. **Guardia de recall:** el `clinical_entity_recall` de LLaVA no debe caer por debajo de ~0.70
   (era 0.82 en v2) — detecta si `max_tokens=256` o la commitment-line empobrecen el reporte.

**Veredicto binario al final:**
- Cumple gating (1 y 3) → cerrar Fase 2 con análisis comparativo v1/v2/v3.
- Cumple solo (1) y NO (3) → confirma causa (b) dominante en generación; documentar y evaluar v3.1
  (focal loss / re-curado de targets).
- No cumple (1) → la causa raíz no es imbalance; opciones más radicales (v4: cambio de dataset/objetivo).

---

## 4. Plan de ejecución

### Paso 1 — Implementación local

1. Inspeccionar `src/data/skincare.py` (o equivalente) para entender cómo se exponen las labels diagnósticas. **Fuente única de la etiqueta diagnóstica por-sample** (la usan §2.1 y §2.2).
2. Agregar `class_freq` y `WeightedRandomSampler` en la función que arma `train_loader` para Stage 2 en `src/training/two_stage.py`.
3. **Commitment-line (§2.2):** en el armado de targets de Stage 2, append `"\n\nMost likely diagnosis: {dx_full}."` a cada `response`, con `dx_full` del mapeo `DX_TO_FULL` (reusar de `enrich_reports.py`). Flag CLI `--commit-line` (default False).
4. Agregar flag CLI `--class-balanced-sampler` en `scripts/train_vlm_stage2.py` (default False para no romper compat con v1/v2).
5. **Sanity check sampler:** correr 1 época con `batch_size=2, n_samples=20` localmente (RTX 4070) verificando que cada batch contiene clases diversas (histograma de labels por batch en las primeras 5 iteraciones).
6. **Sanity check commitment-line:** imprimir 3 targets ya tokenizados y confirmar que la línea de cierre aparece con el diagnóstico correcto.

### Paso 2 — Script SLURM v3

Crear `slurm/mendieta/v3/train_vlm_s2_{llava,mini}.sh` clonando v2 + agregando flag:

```bash
${PYTHON} scripts/train_vlm_stage2.py \
    --model llava_med \
    --epochs 10 \
    --class-balanced-sampler \
    --run-name s2_v3 \
    ...
```

Output: `outputs/checkpoints/stage2_{model}_v3/best_model.pt`.

Agregar aliases en `scripts/mendieta/submit.py`:
- `mini_s2_v3` → `slurm/mendieta/v3/train_vlm_s2_mini.sh`
- `llava_s2_v3` → `slurm/mendieta/v3/train_vlm_s2.sh`
- `all_s2_v3` → grupo

### Paso 3 — Re-evaluación de clasificación con Stage 2 v3

Reutilizar `slurm/mendieta/v2/vlm_classify_{model}_ft.sh` parametrizando el checkpoint:
- Crear v3 que apunte a `outputs/checkpoints/stage2_{model}_v3/best_model.pt` y guarde en `outputs/results/{model}/v3/`.

Aliases: `classify_{llava,mini}_ft_{lik,cot}_v3`, `all_classify_lik_v3`, `all_classify_cot_v3`.

### Paso 4 — Re-generación de reportes con Stage 2 v3 (con fixes de scope §2.4)

**Primero, modificar `scripts/generate_report.py`:** agregar `--splits_file` + `--split test` que
filtren las imágenes del `--images_dir` a los ids del split (los JSON ya existen en `data/splits/`).
Luego `slurm/mendieta/v3/generate_reports_{llava,mini}.sh` apuntando al checkpoint v3, con:

```bash
${PYTHON} scripts/generate_report.py \
    --model llava_med --checkpoint outputs/checkpoints/stage2_llava_med_v3/best_model.pt \
    --images_dir data/processed/HAM10000 \
    --splits_file data/splits/ham10000_splits.json --split test \
    --label_csv data/processed/HAM10000/HAM10000_metadata \
    --output_dir outputs/generated_reports/llava_med/v3/HAM10000 \
    --max_tokens 256 --seed 42
# SkinCoT: --splits_file data/splits/skincare_skincot_splits.json --split test
# MM-SkinQA: --splits_file data/splits/mmskin_splits.json --split test
```

Output: `outputs/generated_reports/{model}/v3/{dataset}/`. Con el split-filtering los 3 datasets
entran cómodos en 48h (HAM ~1500, no 10015), así que el orden ya no es crítico — igual conservar
`ham→skincare→mmskin` por las dudas. **Validación pre-lanzamiento:** correr el split-filtering
localmente con `--image`/dry-run para confirmar que selecciona ~1500 ids de HAM.

> **De-risk opcional (barato):** antes de v3, testear la commitment-line vía prompt sobre el
> checkpoint **v2** en ~200 imgs de HAM test (~4h cluster) para estimar cuánto recupera la
> consistency. Si el prompt-only ya recupera mucho, refuerza la apuesta por la commitment-line.

### Paso 5 — Documentación

- Plan: este archivo.
- Submit: registrar en `docs/ejecuciones.md` con fecha + job IDs.
- Análisis: crear `docs/resul/vlm_clasificacion_resul_v4_<fecha>.md` y `docs/resul/reportes_resul_v3_<fecha>.md` cuando lleguen los resultados.

---

## 5. Estimación de costo

| Fase                    | Jobs   | Tiempo por job | Cola Mendieta | Total wall-clock | 
|-------------------------|--------|---------------|----------------|------------------|
| Stage 2 v3 (training)   | 2      | ~18-24h       | 1-3 días       | 3-5 días         |
| Classify v3 (4 jobs FT) | 4      | 8-11h c/u     | 1-2 días       | 2-3 días         |
| Generate v3 (2 jobs)    | 2      | ~1 día (test split, no 10015) | 1-2 días | 2-3 días |
| **Total iteración v3**  | **8**  | —             | —              | **~10 días**     |

---

## 6. Riesgos y mitigaciones

| Riesgo                                                  | Probabilidad | Mitigación                                          |
|---------------------------------------------------------|--------------|------------------------------------------------------|
| Sampler rebalanceado degrada calidad lingüística general | Media        | Inspección manual de 20 reportes v3 vs v2          |
| Class freq mapping (SkinCaRe→7 clases HAM) incorrecto    | Media        | Auditar histograma antes de lanzar Stage 2 v3      |
| El collapse persiste (objective issue real, no sampling) | Alta-Media   | Plan v3.1 con focal loss preparado (§2.3)          |
| Commitment-line: el modelo afirma diag. equivocado (clasif. sigue mal) → consistency no sube | Media | Es justo la señal de que falta el balanceo; las 2 intervenciones son sinérgicas (§1.1) |
| Commitment-line se lee como "teaching-to-the-metric" | Baja-Media | Documentar que solo sube consistency si el diag. afirmado es correcto (depende de visión, no del template) |
| `max_tokens=256` empobrece reportes → recall ↓ | Media | Guardia de recall en §3 (criterio 4); inspección manual de 20 reportes v3 |
| Cola Mendieta se llena antes de Stage 2 v3              | Baja         | Stage 2 puede correr también en TOKO (RTX 4080 16GB) si VRAM alcanza con QLoRA |
| Re-entrenar invalida métricas baseline                  | Baja         | Mantener checkpoints v1/v2/v3 separados; comparar in-place en resul docs |

---

## 7. Estado de gen v2 — RESUELTO (2026-06-02, Camino B)

Los re-envíos 1154471/1154472 terminaron (timeout × 2, nunca completaron HAM; §2.3 del resul doc).
El número de gating de gen v2 se obtuvo por **aproximación** sobre el prefijo representativo:
**diagnostic_consistency v2 = LLaVA 0.634, Mini 0.229** (regresa vs v1 → no cumple gating).

**Decisión Camino B:** no re-correr v2; pivotear a v3 con los fixes de §2.4 bakeados. El
v2-aproximado es el baseline contra el cual se compara v3 (§3). Iniciar Paso 1 (implementación
local: sampler §2.1 + commitment-line §2.2 + split-filtering §2.4) inmediatamente.

---

## 8. Archivos a crear / modificar

| Archivo                                                | Cambio          |
|--------------------------------------------------------|-----------------|
| `src/training/two_stage.py`                            | WeightedRandomSampler opcional + commitment-line en armado de targets |
| `src/data/skincare.py` (o equivalente)                 | Exponer label diagnóstica por-sample (fuente única) + class_freq dict |
| `scripts/train_vlm_stage2.py`                          | Flags CLI `--class-balanced-sampler` y `--commit-line` |
| `scripts/generate_report.py`                           | Args `--splits_file` + `--split` (filtrar a test split); re-uso `--label_csv` |
| `slurm/mendieta/v3/train_vlm_s2.sh` (LLaVA)            | Nuevo (sampler + commit-line) |
| `slurm/mendieta/v3/train_vlm_s2_mini.sh`               | Nuevo (sampler + commit-line) |
| `slurm/mendieta/v3/vlm_classify_{llava,mini}_ft.sh`    | Nuevo, apunta a ckpt v3 |
| `slurm/mendieta/v3/generate_reports_{llava,mini}.sh`   | Nuevo: test split + `--label_csv` + `max_tokens 256` |
| `scripts/mendieta/submit.py`                            | Aliases `_v3` |
| `docs/ejecuciones.md`                                  | Entrada con submits |
| `docs/resul/vlm_clasificacion_resul_v4_<fecha>.md`     | Crear cuando termine clasificación v3 |
| `docs/resul/reportes_resul_v3_<fecha>.md`              | Crear cuando termine generación v3 |
