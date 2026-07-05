# Ensamble cascada — Resultados (pilot 1 + hallazgo reporte vs razonamiento)

**Fecha:** 2026-06-07
**Estado:** preliminar (pilot 1 analizado; re-pilot de prompt job 1156019 pendiente).
**Plan:** [ensamble_clasificador_generador_plan_20260605.md](../ideas/ensamble_clasificador_generador_plan_20260605.md)

---

## 1. Pilot 1 (job 1155834): grounding "soft", baseline vs oracle

100 imgs HAM, LLaVA-Med Stage 2 v2, grounding oracle (gt) con prompt "soft".

| Condición | diag_consistency | clinical_entity_recall |
|-----------|------------------|------------------------|
| (0) baseline (`"Describe this skin lesion."`) | 0.480 | 0.653 |
| (A) oracle soft (gt en el prompt) | 0.600 | 0.857 |
| **Δ grounding** | **+0.120** | **+0.204** |

El grounding ayuda, pero el oracle (dx correcto) solo llega a 0.60 — NO al >0.85 esperado. El reporte
menciona el dx dado en solo 61/100 casos → el modelo **ignora el dx ~40%**. Motivó el re-pilot de
prompt (job 1156019, 3 variantes que fuerzan commitment).

---

## 2. HALLAZGO clave: no diferenciamos "reporte" de "razonamiento"

SkinCoT (datos de entrenamiento) son narrativas CoT con **1-4 bloques `<think>...</think>`
intercalados con prosa**, sin un "reporte" delimitado. Entrenamos Stage 2 sobre el texto **completo**
→ el modelo emite razonamiento + hedging. Y la evaluación **NO separa** reporte de razonamiento:
- Nivel 1: la referencia se strippea (`_strip_cot`) pero el reporte generado **no** → comparación
  inconsistente.
- Nivel 2: `diagnostic_consistency`/recall se calculan sobre el texto **completo** (incluye el
  razonamiento con hedging).

### 2.1 Cuantificación (sobre los reportes del pilot 1)

| Condición | consistency (texto completo) | consistency (sin `<think>`) | % reportes con `<think>` | % del texto en `<think>` |
|-----------|------------------------------|------------------------------|--------------------------|--------------------------|
| baseline | 0.480 | 0.470 | 1% | ~0% |
| **oracle** | **0.600** | **0.300** | **91%** | **63%** |

**Interpretación:** en el oracle, el 63% del texto está dentro de `<think>`, y al sacar el
razonamiento la consistency cae **0.60 → 0.30**. → El modelo menciona el diagnóstico **mayormente en
el razonamiento, no en un reporte comprometido**. La métrica sobre texto completo está **inflada por
las menciones dentro del razonamiento**. El "reporte real" (comprometido) acierta el dx ~30%, no 60%.

**Matiz:** strippear `<think>` no es suficiente como "extracción de reporte" — el razonamiento también
aparece como **prosa suelta** (en baseline, 1% usa el tag pero igual razona en prosa). El fix limpio
es una **salida estructurada** con el reporte explícitamente delimitado, no solo borrar tags.

---

## 2.5 Re-pilot (job 1156019): variantes de prompt, evaluadas full Y report-only

3 variantes oracle que fuerzan commitment, 100 imgs HAM, `max_tokens=384`. **Report-only = sin
`<think>`** (la métrica correcta para el deliverable):

| Variante | cons **full** | cons **report-only** | recall | % texto en `<think>` |
|----------|---------------|----------------------|--------|----------------------|
| dxfirst | 0.900 | 0.430 | 0.957 | 78% |
| conclude | **0.970** | 0.570 | 0.960 | 72% |
| confirmed | 0.930 | 0.700 | 0.933 | 53% |
| **noreasoning** (v3, job 1156506) | **0.860** | **0.850** | 0.793 | **1%** |
| *(soft, pilot 1)* | *0.600* | *0.300* | *0.857* | *63%* |

**`noreasoning` (prohibir explícitamente el razonamiento) GANA y alcanza el criterio:** report-only
**0.850** (full y report-only coinciden → ya no hay razonamiento que sacar, 1%). El recall baja a 0.79
(reportes más concisos, menos enumeración) — trade-off deseable (comprometido + limpio). **El prompt
ALCANZÓ; no hace falta fine-tune para el commitment.**

**Hallazgos:**
1. **Report-only reordena las variantes:** por full text ganaría `conclude` (0.97), pero su reporte
   comprometido solo acierta 0.57 (72% es razonamiento). El verdadero mejor reporte es **`confirmed`**
   (report-only 0.70, y el que menos razonamiento vuelca: 53%). El "no listes diferenciales" es el lever.
2. **El prompt fuerte funciona mucho:** `confirmed` más que duplica el report-only vs soft (0.30→0.70).
3. **Pero el prompt tiene techo:** aún con el dx correcto (oracle) y el mejor prompt, el reporte
   comprometido acierta 0.70 y el modelo todavía vuelca ~53% a `<think>` (inspección: a veces produce
   un reporte limpio, a veces cae en razonamiento con drift pese a la instrucción). El prior CoT del
   fine-tuning persiste.
4. **Implicancia para el ensamble real:** oracle (dx perfecto) → 0.70 report-only. Un clasificador real
   (DermLIP/Swin, imperfecto) propagaría error → el techo realista del ensamble *por prompt* es menor.

1. **Para la tesis, el deliverable es el REPORTE** (el CoT es agregado). → Hay que **medir el reporte
   comprometido**, no el texto completo con razonamiento. Las métricas Nivel 1/2 deben aplicarse sobre
   la sección de reporte, con el mismo criterio en generación y referencia.
2. **Estructurar la salida:** `Reasoning: <CoT, opcional>` + `Report: <hallazgos + Diagnosis + DDx>`,
   para que reporte y razonamiento sean separables por construcción.
3. **Prompt vs fine-tune para lograr esa estructura — decisión basada en datos:**
   - **Prompt primero** (barato, ya en vuelo): el re-pilot (job 1156019) mide el techo del prompt.
     Variantes `conclude`/`confirmed` empujan el commitment **fuera** del razonamiento.
   - **Fine-tune grounding-aware** solo si el prompt se estanca: re-train Stage 2 con targets
     estructurados `Reasoning/Report`. Más robusto y mejor artefacto de tesis, pero requiere **curar
     los targets estructurados** desde SkinCoT (que no los tiene) — costo de datos no trivial.
   - Regla: prompt para descubrir el techo barato; fine-tune para romperlo solo si hace falta.

---

## 4. Veredicto (preliminar) y siguiente paso

**RESUELTO — el prompt alcanzó (2026-06-10).** La variante **`noreasoning`** (prohibir explícitamente
el razonamiento) logra **report-only 0.85** con oracle y **elimina el `<think>` (1%)**. La métrica
correcta es **report-only**; el ganador es `noreasoning`. **No hace falta fine-tune grounding-aware
para el commitment** — el prior CoT se vence por prompt si se prohíbe explícito.

**Siguiente paso:**
1. **Corrida completa de 4 condiciones** con el prompt `noreasoning`: baseline / oracle (gt) / **Swin**
   (F1 0.88) / **DermLIP** (ZS) — sobre HAM test → mide el ensamble **realista** (cuánto del oracle 0.85
   recupera un clasificador real; el gap = costo de propagación de error).
2. **Nivel 1 (BLEU/ROUGE/BERTScore/METEOR/CIDEr) sobre SkinCoT** (que sí tiene referencias), evaluando
   el reporte (no el razonamiento).
3. **Segundo generador: Mini-VLM** con el mismo esquema.
4. Bakear `--strip-reasoning` / separación reporte-razonamiento en `evaluate_reports` (ya validado
   manualmente acá) para automatizar el report-only.
5. **Vigilar el recall** (bajó a 0.79 con noreasoning): inspección manual de que los reportes concisos
   no pierdan hallazgos clínicos importantes.

---

## 6. Corrida completa (2026-06-18) — jobs 1156723/1156724/1156725

Prompt fijo `noreasoning`. 4 condiciones × {LLaVA, Mini} sobre HAM test (400 imgs, report-only) +
Nivel 1 sobre SkinCoT (457, con referencias).

### 6.1 HAM — diagnostic_consistency (report-only) por condición y modelo

| Condición (grounding) | clasif. acc | **LLaVA** | **Mini-VLM** |
|-----------------------|-------------|-----------|--------------|
| baseline (sin grounding) | — | 0.595 | 0.198 |
| DermLIP ZS | 0.38 | 0.445 | 0.485 |
| Swin (supervisado) | 0.80 | 0.703 | 0.830 |
| oracle (gt) | 1.00 | 0.845 | **1.000** |

Recall (report-only) se mantiene ~0.74–0.79 en todas; `<think>` 0–4% (noreasoning funcionó).

**Hallazgos:**
1. **El ensamble funciona y la calidad del clasificador propaga monótonamente** (oracle > Swin >
   DermLIP > baseline). Con **Swin** (F1 0.88): LLaVA 0.595→0.703, **Mini 0.198→0.830**.
2. **Un clasificador débil puede empeorar:** DermLIP ZS (acc 0.38) en LLaVA da 0.445 < baseline 0.595
   → groundear con un dx equivocado hace que el reporte se comprometa con el error. El clasificador
   debe ser suficientemente bueno (costo de propagación de error, concreto).
3. **Mini-VLM obedece el grounding perfecto (oracle 1.000)** pese a su baseline pésima (0.198) — su
   prior CoT es débil, sigue la instrucción al pie. LLaVA oracle 0.845 (prior CoT algo más fuerte).
4. **Receta práctica óptima:** Swin (mejor clasificador) + generador con prompt noreasoning.

### 6.2 SkinCoT — Nivel 1 (léxico vs referencias) + Nivel 2

| Condición | BLEU-4 | METEOR | CIDEr | consistency (Nivel 2) |
|-----------|--------|--------|-------|------------------------|
| baseline | 0.102 | 0.330 | 0.054 | 0.392 |
| oracle (noreasoning) | 0.040 | 0.209 | 0.038 | **0.567** |

**Trade-off central:** grounding+noreasoning **↑ consistency (0.39→0.57)** pero **↓ similitud léxica**
(BLEU 0.10→0.04). El reporte conciso y comprometido calza menos con la referencia CoT verbosa de
SkinCoT — es un trade-off de **estilo/longitud**, no de calidad clínica (un reporte que afirma el dx
es más útil aunque se parezca menos al texto de referencia verboso).

### 6.3 Veredicto de la corrida completa

- **El ensamble cascada (clasificador → generador grounded noreasoning) es la solución para reportes
  comprometidos.** Con un clasificador fuerte (Swin) la consistency del reporte sube sustancialmente
  (Mini +0.63, LLaVA +0.11) sin perder riqueza.
- **El clasificador importa:** un débil (DermLIP ZS) puede ser peor que no groundear.
- **Las métricas léxicas (Nivel 1) penalizan la concisión** → para la tesis hay que reportar Nivel 2
  (fidelidad diagnóstica) como métrica principal del reporte, y Nivel 1 con el caveat del trade-off.

---

## 5. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `outputs/generated_reports/llava_med/pilot_{baseline,oracle}/` | Reportes pilot 1 |
| `scripts/generate_report.py` (`GROUNDED_TEMPLATES`, `_strip_cot`) | Grounding + strip de razonamiento |
| `src/evaluation/clinical_ner.py` | Métricas Nivel 2 (sobre texto completo — a ajustar) |
| [ensamble_..._plan §9](../ideas/ensamble_clasificador_generador_plan_20260605.md) | Plan + extensiones |
