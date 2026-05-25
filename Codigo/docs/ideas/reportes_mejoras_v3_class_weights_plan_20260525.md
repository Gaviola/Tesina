# Plan: Mejoras de Stage 2 — v3 (class-balanced sampling + focal loss opcional)

**Fecha:** 2026-05-25
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Modelos:** LLaVA-Med 7B + LoRA, Mini-VLM (Phi-3.5-vision) + LoRA
**Referencias:**
- [vlm_clasificacion_resul_v3_20260517.md](../resul/vlm_clasificacion_resul_v3_20260517.md) (veredicto v2: no rompe class collapse)
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

### 2.2 Opción complementaria — focal loss sobre tokens de respuesta

Más invasivo y de impacto incierto en VLMs autoregressive. **Postergar a v3.1** si v3 (solo sampler) no rompe el collapse.

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

### 2.3 Lo que NO cambia respecto a v2

- **Stage 1:** no se re-entrena. Se reutiliza `outputs/checkpoints/stage1_{model}/best_model.pt`.
- **HPs:** se mantienen los del t04 (lr=2.495e-5, lora_r=64, lora_alpha=64, dropout=0.0).
- **Epochs:** 10 (como en v2). El sampler hace que cada época rote por más samples minoritarios; reducir epochs corre el riesgo de no converger al nuevo balance.
- **Datasets de Stage 2:** SkinCaRe (SkinCAP + SkinCoT) sin agregar MM-Skin (B1 sigue descartado).

---

## 3. Criterios de éxito v3

**Idénticos a v2, con el threshold endurecido en el gating:**

1. **Primario / gating (obligatorio para cierre F2):** romper class collapse, `sens_macro > 1/7 ≈ 0.143` en al menos un modelo competitivo (LLaVA-Med FT lik o Mini-VLM FT lik). Ideal: `sens_macro > 0.25` (indicaría discriminación real, no marginal).
2. **Secundario:** mejorar F1-weighted vs v2 en al menos un combo. Aceptamos que accuracy global puede **bajar** ligeramente (es esperado al re-balancear); lo importante es F1.
3. **Diagnostic consistency en HAM10000:** mejorar ≥ +0.03 absoluto vs v2 (cuando los reportes v2 lleguen y se evalúen).

**Veredicto binario al final:**
- Cumple gating → cerrar Fase 2 con análisis comparativo v1/v2/v3.
- No cumple gating → diagnóstico técnico documentado en resul v3 y considerar opciones más radicales (v4: focal loss, o cambio de dataset).

---

## 4. Plan de ejecución

### Paso 1 — Implementación local

1. Inspeccionar `src/data/skincare.py` (o equivalente) para entender cómo se exponen las labels diagnósticas.
2. Agregar `class_freq` y `WeightedRandomSampler` en la función que arma `train_loader` para Stage 2 en `src/training/two_stage.py`.
3. Agregar flag CLI `--class-balanced-sampler` en `scripts/train_vlm_stage2.py` (default False para no romper compat con v1/v2).
4. **Sanity check:** correr 1 época con `batch_size=2, n_samples=20` localmente (RTX 4070) verificando que cada batch contiene clases diversas (logging del histograma de labels por batch durante las primeras 5 iteraciones).

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

### Paso 4 — Re-generación de reportes con Stage 2 v3

Mismo patrón: `slurm/mendieta/v3/generate_reports_{llava,mini}.sh` apuntando al checkpoint v3 y output `outputs/generated_reports/{model}/v3/{dataset}/`. **Conservar el orden invertido `ham→skincare→mmskin` aplicado en v2 it.2** para garantizar HAM10000+SkinCoT.

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
| Generate v3 (2 jobs)    | 2      | 48h (timeout) | 1-2 días       | 2-4 días         |
| **Total iteración v3**  | **8**  | —             | —              | **~10 días**     |

---

## 6. Riesgos y mitigaciones

| Riesgo                                                  | Probabilidad | Mitigación                                          |
|---------------------------------------------------------|--------------|------------------------------------------------------|
| Sampler rebalanceado degrada calidad lingüística general | Media        | Inspección manual de 20 reportes v3 vs v2          |
| Class freq mapping (SkinCaRe→7 clases HAM) incorrecto    | Media        | Auditar histograma antes de lanzar Stage 2 v3      |
| El collapse persiste (objective issue real, no sampling) | Alta-Media   | Plan v4 con focal loss preparado                   |
| Cola Mendieta se llena antes de Stage 2 v3              | Baja         | Stage 2 puede correr también en TOKO (RTX 4080 16GB) si VRAM alcanza con QLoRA |
| Re-entrenar invalida métricas baseline                  | Baja         | Mantener checkpoints v1/v2/v3 separados; comparar in-place en resul docs |

---

## 7. Decisión: ejecutar ahora vs esperar resultados de gen v2

Los re-envíos 1154471/1154472 (gen v2 con orden invertido) están en cola y volverán en 5-7 días. **No bloquean el inicio del plan v3:**

- La conclusión del veredicto clasificación v3 ya es clara: el class collapse no se rompió.
- La iteración v3 ataca la causa raíz independientemente del estado de la generación v2.
- Cuando lleguen los reportes v2, su diagnostic_consistency se usará como baseline para comparar contra los reportes v3 (no como gating de la decisión de iterar).

**Recomendación: iniciar paso 1 (implementación local) inmediatamente.**

---

## 8. Archivos a crear / modificar

| Archivo                                                | Cambio          |
|--------------------------------------------------------|-----------------|
| `src/training/two_stage.py`                            | Agregar WeightedRandomSampler opcional |
| `src/data/skincare.py` (o equivalente)                 | Exponer label diagnóstica + class_freq dict |
| `scripts/train_vlm_stage2.py`                          | Flag CLI `--class-balanced-sampler` |
| `slurm/mendieta/v3/train_vlm_s2.sh` (LLaVA)            | Nuevo |
| `slurm/mendieta/v3/train_vlm_s2_mini.sh`               | Nuevo |
| `slurm/mendieta/v3/vlm_classify_{llava,mini}_ft.sh`    | Nuevo, apunta a ckpt v3 |
| `slurm/mendieta/v3/generate_reports_{llava,mini}.sh`   | Nuevo, orden ham→skincare→mmskin |
| `scripts/mendieta/submit.py`                            | Aliases `_v3` |
| `docs/ejecuciones.md`                                  | Entrada con submits |
| `docs/resul/vlm_clasificacion_resul_v4_<fecha>.md`     | Crear cuando termine clasificación v3 |
| `docs/resul/reportes_resul_v3_<fecha>.md`              | Crear cuando termine generación v3 |
