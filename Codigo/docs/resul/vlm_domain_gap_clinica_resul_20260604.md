# Domain Gap VLM — Resultados (clasificación ZS: foto clínica vs dermatoscopía)

**Fecha de envío:** 2026-06-03
**Fecha de análisis:** 2026-06-04
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)
**Jobs SLURM:** 1155373 (LLaVA-Med ZS clínica), 1155374 (Mini-VLM ZS clínica) — ambos COMPLETED.
**Plan:** [vlm_domain_gap_clinica_plan_20260603.md](../ideas/vlm_domain_gap_clinica_plan_20260603.md)

---

## 1. Motivación

El re-diagnóstico del class collapse ([vlm_clasificacion_resul_v3 §5.4](vlm_clasificacion_resul_v3_20260517.md))
hipotetizó un **domain gap**: los VLMs (entrenados en foto clínica/texto) no transferirían a
**dermatoscopía** (HAM10000). Este experimento busca la **confirmación afirmativa**:

> **Hipótesis:** el VLM discrimina mejor las 7 clases sobre **foto clínica** (su dominio) que sobre
> dermatoscopía. Si `sens_macro_clínica >> sens_macro_HAM`, el domain gap queda probado.

---

## 2. Diseño

Comparación apples-to-apples: **misma** pregunta de 7 clases (`score_image` con `HAM10000_CLASSES`),
**mismo** método (likelihood), **mismo** modelo en **zero-shot**; lo único que cambia es el dominio.

- **Test set clínico:** SkinCAP mapeado a las 7 clases HAM vía `SKINCAP_TO_HAM` (mapeo curado,
  listas explícitas). **n=624 imágenes**, distribución: NV 173, BCC 115, MEL 92, BKL 88, AKIEC 64,
  VASC 58, DF 34 (todas ≥34).
- **Zero-shot** para evitar circularidad (SkinCAP se usó en Stage 1).
- **Baseline:** `sens_macro` ZS sobre HAM (de v1): LLaVA 0.157, Mini 0.181.

---

## 3. Resultados

| Modelo | Dominio | n | accuracy | f1_w | **sens_macro** | clases predichas |
|--------|---------|---|----------|------|----------------|------------------|
| LLaVA-Med | HAM (dermatoscopía) | 1503 | — | — | **0.157** | — |
| LLaVA-Med | **SkinCAP (clínica)** | 624 | 0.071 | 0.047 | **0.106** (Δ **−0.051**) | 6/7 |
| Mini-VLM | HAM (dermatoscopía) | 1503 | — | — | **0.181** | — |
| Mini-VLM | **SkinCAP (clínica)** | 624 | 0.181 | 0.153 | **0.176** (Δ **−0.005**) | 4/7 |

### 3.1 Patrón de colapso por dominio

| Modelo | Colapsa en HAM (dermatoscopía) | Colapsa en clínica |
|--------|--------------------------------|--------------------|
| LLaVA-Med | NV/MEL | **DF 42%**, BCC 22%, MEL 19% |
| Mini-VLM | NV 99% | **DF 63%**, NV 33% |

Sens per-class (clínica) — alta solo en la clase "spameada":
- LLaVA: DF 0.412, MEL 0.13, BCC 0.113, VASC 0.086, **NV 0, AKIEC 0, BKL 0**.
- Mini: DF 0.647, NV 0.468, AKIEC 0.062, BCC 0.052, **MEL 0, BKL 0, VASC 0**.

---

## 4. Análisis

1. **El domain gap NO se confirma.** La foto clínica **no** es mejor que la dermatoscopía: ambos
   modelos siguen ≈ azar (1/7 = 0.143) en clínica, y LLaVA es incluso *peor* (−0.051). Δ ≈ 0 / negativo.
2. **El colapso persiste en clínica** (predice solo 4-6 de 7 clases).
3. **Hallazgo más fuerte — el blanco del colapso cambia con el dominio:** HAM → NV/MEL; clínica → **DF**.
   El *mismo* modelo colapsa a clases **completamente distintas y arbitrarias** según el dominio. Si
   usara el contenido de la imagen, el blanco no cambiaría así. → **La predicción está guiada por
   artefactos del prompt/likelihood scoring, no por la imagen.**

**Conclusión revisada:** la limitación **no es específica de dermatoscopía**. Es una **incapacidad
general** de estos VLMs (zero-shot, likelihood) para la **clasificación dermatológica de grano fino
de 7 clases en cualquier dominio**. Colapsan a una constante dependiente del prompt/dominio. Los CNN
supervisados (Swin-Tiny F1=0.88) siguen siendo necesarios para esta tarea.

Esto **refina** el §5.4 del resul de clasificación (que apuntaba a "domain gap dermatoscopía" como
causa probable): la causa es más general.

---

## 5. Caveats

- **No prueba el VLM en su taxonomía clínica nativa.** El experimento evalúa la tarea fina de 7 clases
  HAM sobre imágenes clínicas. NO testea si el VLM discrimina su taxonomía ancha nativa (23 clases
  DermNet, ej. acné vs psoriasis vs eczema), que podría ser mejor. Para la comparación central de la
  tesis (diagnóstico 7-clases), el veredicto igual es claro.
- **Dificultad intrínseca:** distinguir melanoma/nevus/BCC en **foto clínica** (sin magnificación
  dermatoscópica) es genuinamente difícil incluso para dermatólogos. El "clínica también ≈ azar" en
  parte refleja eso. Pero no rescata la hipótesis del domain gap: el VLM no mejora en clínica.
- **Método:** solo likelihood scoring (el más robusto). No se corrió CoT clínica.
- **Mapeo SkinCAP→7:** curado pero con ambigüedad inherente (variantes finas agrupadas).

---

## 6. Veredicto y siguiente paso

**Veredicto: domain gap NO confirmado. Reenmarcado a limitación general de grano fino.**

| Criterio (plan §3) | Resultado |
|--------------------|-----------|
| sens_macro clínica ≥ 0.30 | **NO** (0.106 / 0.176) |
| clínica ≥ +0.10 vs HAM ZS | **NO** (−0.051 / −0.005) |
| no colapsa a una clase | **NO** (colapsa a DF) |

**Conclusión de tesis (clasificación VLM):** los VLMs evaluados no resuelven la clasificación
dermatológica de 7 clases — ni en dermatoscopía ni en foto clínica —, colapsando a una clase
arbitraria dependiente del prompt/dominio. Es una limitación de capacidad de grano fino, no un
domain gap. **Cierra la línea de clasificación VLM de la tesis** con un resultado negativo sólido y
bien evidenciado; la contribución de los VLMs queda del lado de la **generación de reportes**, no de
la clasificación.

**No se planifica más iteración de clasificación VLM.** El collapse está explicado y documentado.

---

## 7. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `outputs/results/{model}_likelihood_clinical_predictions.json` | Predicciones ZS clínica |
| `outputs/results/{model}_likelihood_clinical_test_results.json` | Métricas ZS clínica |
| `src/data/skincare.py` (`SkinCAPClassificationDataset`, `SKINCAP_TO_HAM`) | Adaptador + mapeo |
| `scripts/train_vlm_classify.py` (`--eval-dataset`) | Flag de dominio |
| `slurm/mendieta/vlm_classify_{llava,mini}_clinical.sh` | SLURM ZS clínica |
| [vlm_clasificacion_resul_v3 §5.4](vlm_clasificacion_resul_v3_20260517.md) | Re-diagnóstico (refinado por este doc) |
