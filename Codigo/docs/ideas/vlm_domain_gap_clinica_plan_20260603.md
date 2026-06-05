# Plan: Confirmación afirmativa del domain gap VLM (dermatoscopía vs foto clínica)

**Fecha:** 2026-06-03
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Modelos:** LLaVA-Med 7B, Mini-VLM (Phi-3.5-vision) — **zero-shot** (sin fine-tuning)
**Referencias:**
- [vlm_clasificacion_resul_v3 §5.4](../resul/vlm_clasificacion_resul_v3_20260517.md) (re-diagnóstico: collapse es domain gap, no imbalance)
- Memoria: `project_vlm_collapse_domain_not_imbalance`

---

## 1. Motivación

El re-diagnóstico (§5.4) concluyó que el class collapse de los VLMs en HAM10000 es una **limitación
de dominio**: los VLMs están entrenados en foto clínica/texto, no en dermatoscopía. La evidencia
actual es **circunstancial** (collapse en zero-shot, datos de training no sesgados, collapse arbitrario
por combo, CNN supervisado F1=0.88 en la misma HAM). Falta la **evidencia afirmativa**:

> **Hipótesis:** el VLM discrimina mejor las 7 clases sobre **foto clínica** (su dominio) que sobre
> **dermatoscopía** (HAM). Si `sens_macro_clínica >> sens_macro_HAM`, el domain gap queda demostrado
> y el collapse se convierte en un hallazgo de tesis sólido en vez de un "el VLM es malo".

Esto cierra el argumento central de la tesis: *clasificadores supervisados >> VLMs en diagnóstico
dermatoscópico, **porque** los VLMs no transfieren de foto clínica a dermatoscopía.*

---

## 2. Diseño experimental

**Comparación apples-to-apples:** misma pregunta de 7 clases (`score_image` con `HAM10000_CLASSES`
y `CLASS_SYNONYMS` **sin tocar**), mismo método (likelihood), mismo modelo en **zero-shot**; lo único
que cambia es el **dominio de las imágenes** (foto clínica SkinCAP vs dermatoscopía HAM).

- **Zero-shot únicamente.** SkinCAP se usó en Stage 1 (alineación), así que evaluar el modelo
  *fine-tuneado* sobre SkinCAP sería circular. ZS = modelo base, sin training → comparación limpia.
- **Método: likelihood** (el más robusto; CoT opcional como secundario).
- **Baseline de comparación ya disponible:** `sens_macro` ZS sobre HAM (de v1):
  LLaVA lik 0.157, Mini lik 0.181 (≈ 1/7 = azar).

### 2.1 Construcción del test set clínico (SkinCAP → 7 clases HAM)

Mapeo curado fino→HAM (include-list explícita, NO substring, para evitar falsos positivos como
`epidermal-nevus` que NO es nv melanocítico):

| Clase HAM | Etiquetas SkinCAP incluidas | ~n |
|-----------|------------------------------|----|
| nv (nevus) | `melanocytic-nevi` | 118 |
| mel (melanoma) | `melanoma`, `melanoma-in-situ`, `melanoma-acral-lentiginous`, ... | ~92 |
| bcc | `basal cell carcinoma` (+ variantes morpheiform, solid cystic, ...) | ~115 |
| akiec | `actinic-keratosis`, `actinic keratosis`, `squamous-cell-carcinoma-in-situ` (Bowen) | ~85 |
| bkl | `seborrheic-keratosis`(+irritated), `benign-keratosis` | ~114 |
| df | `dermatofibroma` | 34 |
| vasc | `angioma`, `pyogenic-granuloma`, `hemangioma`, `lymphangioma` | ~76 |

**Exclusiones:** SCC invasivo (no hay clase HAM equivalente), nevus no melanocíticos
(`epidermal-nevus`, `nevus-lipomatosus`, etc.), y cualquier etiqueta ambigua. Total estimado
~630 imágenes clínicas, ≥30 por clase → `sens_macro` estable.

### 2.2 Cambios de código (mínimos)

1. **Adaptador de dataset** `SkinCAPClassificationDataset` (o función en `src/data/skincare.py`):
   carga las imágenes de SkinCAP cuyo `disease` esté en el include-list, devuelve
   `{"image", "label": HAM10000_LABEL_MAP[mapped]}`. Reusa `SkinCaReDataset(subset="skincap")`
   + un dict de mapeo.
2. **Flag en `scripts/train_vlm_classify.py`:** `--eval-dataset {ham10000,skincap_clinical}`
   (default `ham10000`, no rompe nada). Si `skincap_clinical`, usa el adaptador; el resto del
   pipeline (`score_image`, `class_codes=HAM10000_CLASSES`) **queda igual**.
3. **SLURM** `slurm/mendieta/v1/vlm_classify_{llava,mini}_clinical.sh`: clon del ZS likelihood
   con `--eval-dataset skincap_clinical`, output a `outputs/results/{model}/clinical/`.

### 2.3 Sanity check local (sin GPU)

- Instanciar el adaptador y loggear el histograma de las 7 clases → confirmar conteos ≥30 y que el
  mapeo no incluye basura. Esto se valida **localmente antes de enviar** (no requiere GPU).

---

## 3. Criterios de éxito

1. **Primario (confirma domain gap):** `sens_macro_clínica ≥ 0.30` **y** `≥ +0.10` absoluto sobre
   `sens_macro_HAM` ZS, en al menos un modelo. Indicaría discriminación real en el dominio clínico
   que se pierde en dermatoscopía.
2. **Secundario:** la distribución de predicciones en clínica NO colapsa a una sola clase (a
   diferencia de HAM, donde colapsa a una clase arbitraria por combo).

**Veredicto binario:**
- Cumple → domain gap **confirmado afirmativamente**; se documenta como hallazgo central. Cierra el
  análisis de clasificación VLM de la tesis.
- No cumple (clínica también ≈ azar) → el VLM es malo en derm *fina* en general, no solo dermatoscopía.
  Igual es honesto y reenmarca la conclusión (el VLM no resuelve clasificación dermatológica de grano
  fino, punto). Se documenta el negativo.

---

## 4. Plan de ejecución

1. **Local:** implementar adaptador + flag (§2.2 pasos 1-2). Sanity check §2.3. Commit.
2. **Sync up** (ver §6).
3. **Submit:** 2 jobs ZS likelihood clínica (LLaVA, Mini). Cola Mendieta corta (ZS, ~630 imgs, sin
   training → pocas horas por job).
4. **Sync down** results. Evaluar `sens_macro` clínica vs HAM con `evaluate_classify.py` /
   las métricas que ya emite `run_likelihood_eval`.
5. **Documentar:** `docs/resul/vlm_domain_gap_clinica_resul_<fecha>.md` con la tabla
   clínica-vs-dermatoscopía + veredicto. Actualizar `ejecuciones.md` y, si confirma, integrarlo
   al §5.4 del resul de clasificación como evidencia afirmativa.

---

## 5. Estimación de costo

| Fase | Jobs | Tiempo/job | Cola | Total |
|------|------|-----------|------|-------|
| ZS likelihood clínica | 2 | ~2-4 h (630 imgs, ZS) | 1-2 días | ~2-3 días |

Muy barato comparado con cualquier retraining. Sin riesgo de timeout.

---

## 6. Sincronización con clústeres

- **Datos:** SkinCAP ya está en el cluster (`data/raw/skincare/`) porque Stage 1 lo usó. **Verificar**
  con `ssh ... ls data/raw/skincare/SkinCAP` antes de enviar; si falta, `sync_up` de datos o re-descarga.
- **Código nuevo** (adaptador + flag + SLURM): subir con `python scripts/mendieta/sync_up.py`.
  No requiere `--delete` (solo agrega archivos, no renombra/elimina rutas existentes).
- **Splits:** el adaptador usa `data/splits/skincare_skincap_splits.json` (ya existe local y en
  cluster). Para una eval ZS se puede usar **todo SkinCAP** (no solo test) ya que el modelo es base
  y no hubo training específico — decidir en implementación si filtrar a split=test o usar todos.
- **Validación local vs cluster:** correr el sanity check §2.3 **localmente** (sin GPU) para confirmar
  el mapeo y los conteos ANTES de `sync_up` + submit. La inferencia VLM (GPU) va solo en cluster.
- **Bajada:** `python scripts/mendieta/sync_down.py` (results JSON, livianos). No hace falta
  `--reports` ni `--checkpoints`.

---

## 7. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| El experimento NO confirma (clínica ≈ azar) | Media | Es un resultado honesto igual; reenmarca a "VLM malo en derm fina". Documentar el negativo. |
| Mapeo SkinCAP→7 clases ambiguo (SCC, nevus no melanocítico) | Media | Include-list curada explícita (§2.1); excluir ambiguos; auditar histograma en sanity check. |
| ¿SkinCAP es realmente foto clínica y no dermatoscopía? | Baja | SkinCAP deriva de fuentes clínicas (DermNet-like). Verificar inspeccionando 5-10 imágenes localmente. |
| n por clase chico (df=34) | Baja | sens_macro tolera ~30/clase; reportar con cuidado df/vasc. |
| Circularidad (SkinCAP en Stage 1) | Nula | Solo zero-shot (modelo base, sin training). |

---

## 8. Archivos a crear / modificar

| Archivo | Cambio |
|---------|--------|
| `src/data/skincare.py` (o nuevo) | Adaptador `SkinCAPClassificationDataset` + dict de mapeo SkinCAP→HAM |
| `scripts/train_vlm_classify.py` | Flag `--eval-dataset {ham10000,skincap_clinical}` |
| `slurm/mendieta/v1/vlm_classify_{llava,mini}_clinical.sh` | Nuevos (ZS likelihood, `--eval-dataset skincap_clinical`) |
| `scripts/mendieta/submit.py` | Aliases `classify_{llava,mini}_clinical` |
| `docs/ejecuciones.md` | Entrada con submits |
| `docs/resul/vlm_domain_gap_clinica_resul_<fecha>.md` | Crear al volver los resultados |
