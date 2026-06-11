# Plan: Ensamble en cascada — clasificador → generador de reportes (grounding)

**Fecha:** 2026-06-05
**Cluster:** generación en Mendieta (donde viven los checkpoints Stage 2); pilot local previo.
**Modelos:** clasificador (Swin-Tiny supervisado / DermLIP ZS) + VLM generativo (LLaVA-Med / Mini-VLM)
**Referencias:**
- [dermlip_clasificacion_resul_20260605.md](../resul/dermlip_clasificacion_resul_20260605.md) (DermLIP rompe el collapse, sens_macro 0.51)
- [reportes_resul_v2_20260517.md §4-5](../resul/reportes_resul_v2_20260517.md) (la generación v2 hedea: diagnostic_consistency regresa a 0.63)
- SOTA con precedente de ensamble: *Ensemble DL + LLM-Assisted Reporting*, *SkinSavvy2*, *Knowledge-Distilled Report Generation* (en `Docs/estado_del_arte/resumen_papers.tex`)

---

## 1. Motivación

Encontramos **dos fallos independientes**:
1. **Clasificación:** los VLM generativos colapsan (sens_macro ≈ 0.14). DermLIP (ZS, 0.51) y los CNN
   supervisados (Swin F1 0.88) sí discriminan.
2. **Generación:** el VLM produce reportes ricos pero **hedea el diagnóstico** (estilo CoT,
   diagnostic_consistency 0.63, regresó vs v1) — no se compromete.

**Idea (cascada):** desacoplar las dos tareas y combinarlas. El **clasificador fuerte** decide el
diagnóstico; el **VLM generativo** redacta el reporte **condicionado (grounded)** a ese diagnóstico.
Una sola intervención arregla ambos problemas:
- el diagnóstico lo da el clasificador confiable (no el VLM colapsado), y
- al inyectar el dx en el prompt, el reporte **se compromete** → la diagnostic_consistency debería
  subir fuerte (cota superior ≈ accuracy del clasificador).

No es un modelo fusionado: son dos modelos independientes orquestados, interfaz **texto puro**
(máxima compatibilidad, sin entrenamiento conjunto). Costo de hardware extra ~nulo (el clasificador
es despreciable vs el VLM 7B; se corre en cascada, cada modelo por separado).

---

## 2. Diseño experimental

Generación de reportes sobre **HAM10000 test split** (~1500 imgs; usar los fixes de scope ya
definidos: test split + `--label_csv` + `max_tokens` 256, ver
[plan v3 §2.4](reportes_mejoras_v3_class_weights_plan_20260525.md)). Se compara la
`diagnostic_consistency` (y recall, Nivel 1) bajo 4 condiciones de grounding:

| Condición | Diagnóstico inyectado en el prompt | Rol |
|-----------|-------------------------------------|-----|
| **(0) baseline** | ninguno (`"Describe this skin lesion."`) | el actual (hedea, 0.63) |
| **(A) oracle** | gt_label de HAM (dx real) | **cota superior** del grounding |
| **(B) Swin** | predicción de Swin-Tiny (F1 0.88) | grounding realista fuerte |
| **(C) DermLIP** | predicción de DermLIP ZS (sens 0.51) | grounding derm-especializado ZS |

- **(A) oracle** mide cuánto sube la consistency si el dx es perfecto → aísla el efecto del grounding
  del efecto de los errores del clasificador.
- **(B) vs (C)** mide cuánto del oracle se recupera con un clasificador real (Swin debería acercarse
  más al oracle por su mayor accuracy).
- **Métrica de propagación de error:** medir además la tasa "grounded-pero-incorrecto" (reportes que
  se comprometen con un dx errado del clasificador) — el riesgo clínico del enfoque.

### 2.1 Prompt de grounding
```
"The most likely diagnosis for this skin lesion is {dx}. Write a structured clinical report
 describing the lesion's morphology, dermatoscopic features and findings consistent with this
 diagnosis."
```
Variante a evaluar: inyectar **top-k + confianza** del clasificador (en vez de solo top-1) para que
el VLM exprese incertidumbre cuando el clasificador duda — mitiga la propagación de error. Empezar
con top-1.

### 2.2 Modelos
- Generador: **LLaVA-Med** (mejor recall, 0.82) como principal; Mini-VLM secundario.
- Checkpoint: el **Stage 2 v2** existente (no re-entrenar) — el grounding es solo de inferencia.

---

## 3. Criterios de éxito

1. **Primario:** `diagnostic_consistency` con grounding realista (B/C) **>> baseline 0.63**.
   Meta: **≥ 0.75** en al menos una combinación (idealmente acercarse al oracle).
2. **Oracle (A):** debe ser alto (>0.85) — valida que el mecanismo de grounding funciona; si el oracle
   no sube, el prompt de grounding está mal y hay que rediseñarlo.
3. **No degradar la calidad:** `clinical_entity_recall` y Nivel 1 (BLEU/ROUGE) no deben caer respecto
   al baseline (vigilar "templating"/reportes genéricos). Inspección manual de 20 reportes.
4. **Veredicto binario:**
   - Cumple → el ensamble en cascada es la solución de Fase 2 (clasificación + generación). Se
     formaliza como contribución.
   - No cumple (ni el oracle sube) → el problema de generación no es de commitment sino de otra cosa;
     re-diagnosticar.

---

## 4. Plan de ejecución

### Paso 0 — Pilot local (de-risk barato)
Antes de cualquier cluster: generar ~50-100 reportes HAM **localmente** (RTX 4070, LLaVA-Med
cuantizado) bajo **(0) baseline vs (A) oracle**. Si el oracle sube la consistency notablemente, el
mecanismo funciona y se justifica la corrida completa. ~pocas horas.

### Paso 1 — Código
- `scripts/generate_report.py`: agregar `--diagnosis_source <csv/json>` (mapa image_id → dx predicho)
  + `--grounded_prompt` (template §2.1). Si se pasa, el prompt por-imagen inyecta el dx. Sin el flag,
  comportamiento actual intacto.
- Reusar las predicciones ya existentes:
  - DermLIP: `outputs/results/dermlip/dermlip_zeroshot_vit-b-16_predictions.json`.
  - Swin: predicciones de F1 (`outputs/results/...`); si solo hay métricas, re-generar predicciones.
  - gt: del metadata de HAM (oracle).
- Un helper que convierta cada fuente a `{image_id: dx_full}` (reusar `DX_TO_FULL` de `enrich_reports.py`).

### Paso 2 — Evaluación
Para cada condición (0/A/B/C): generar sobre HAM test → `evaluate_reports.py --level 2` →
diagnostic_consistency + recall. Tabla comparativa.

### Paso 3 — Documentación
Plan (este), `ejecuciones.md`, `docs/resul/ensamble_resul_<fecha>.md` con la tabla 4-condiciones +
veredicto + tasa de propagación de error.

---

## 5. Estimación de costo

| Fase | Dónde | Tiempo |
|------|-------|--------|
| Pilot (baseline vs oracle, ~100 imgs) | Local | ~2-4 h |
| Generación completa 4 condiciones × HAM test (~1500) | Mendieta | ~1-2 días/cond. (test split, max_tokens 256) |
| Clasificación (DermLIP/Swin) | ya hecha / local | — |

La clasificación ya está; el costo es solo la generación (que se haría igual en Fase 2).

---

## 6. Sincronización con clústeres

- **Pilot local:** no requiere cluster. Valida el mecanismo antes de gastar cola.
- **Predicciones del clasificador:** se generan **local** (DermLIP) o ya están (Swin). Se **suben** con
  `sync_up` como input de la generación (van en `outputs/results/`, que NO se sincroniza por defecto
  → subir el JSON de diagnósticos explícitamente o incluirlo en el repo de inputs).
- **Generación en Mendieta:** `sync_up` del código (`generate_report.py` modificado + nuevos SLURM)
  **sin `--delete`**. El checkpoint Stage 2 v2 ya está en Mendieta. `sync_down --reports` al volver.
- **Validación local vs cluster:** el pilot local valida el prompt y el pipeline antes del envío. La
  fuente de diagnósticos (CSV) debe existir idéntica local y en cluster.

---

## 7. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Propagación de error (clasificador errado → reporte confiadamente errado) | Media-Alta | Medir tasa "grounded-incorrecto"; variante top-k+confianza; grounding solo si confianza alta |
| Grounding → "templating" (reportes genéricos, recall ↓) | Media | Criterio 3 (guardia de recall) + inspección manual de 20 |
| El oracle no sube la consistency (prompt mal diseñado) | Baja | El pilot lo detecta barato antes del cluster |
| "Es un sistema de 2 modelos, no un VLM end-to-end" | — | Enmarcarlo como **sistema híbrido** (patrón en el SOTA); el modelo fusionado (encoder derm + LLM) es dirección aparte (SkinVL/DermatoLlama) |

---

## 8. Archivos a crear / modificar

| Archivo | Cambio |
|---------|--------|
| `scripts/generate_report.py` | `--diagnosis_source` + `--grounded_prompt` (inyección de dx por imagen) |
| `scripts/` (helper) | conversión predicciones → `{image_id: dx_full}` (reusa `DX_TO_FULL`) |
| `slurm/mendieta/` | scripts de generación grounded (4 condiciones) |
| `scripts/mendieta/submit.py` | aliases |
| `docs/ejecuciones.md` | entrada |
| `docs/resul/ensamble_resul_<fecha>.md` | resultados + veredicto |
| (al cerrar) `Docs/tabla_resultados_sota/*.tex`, `CLAUDE.md` | si el ensamble se adopta como contribución |

---

## 9. Actualización 2026-06-06 — resultado pilot 1 + re-pilot de prompt + extensiones

### 9.1 Pilot 1 (job 1155834): grounding ayuda pero el prompt "soft" es débil
Sobre 100 imgs HAM (LLaVA v2), baseline vs oracle (gt):

| Cond. | diag_consistency | recall |
|-------|------------------|--------|
| baseline | 0.480 | 0.653 |
| oracle (soft) | 0.600 | 0.857 |

El oracle (dx correcto) solo llega a 0.60 — el reporte menciona el dx dado en **61/100** casos →
el modelo **ignora el dx ~40%** (prior CoT `<think>` + `max_tokens=256` trunca). El mecanismo es
válido (consistency ≈ tasa de mención); falta **forzar el commitment**.

### 9.2 Re-pilot de prompt (job 1156019): 3 variantes que fuerzan commitment
`GROUNDED_TEMPLATES` en `generate_report.py` + flag `--grounded_variant`. Variantes oracle sobre las
mismas 100 imgs, `max_tokens=384`:
- **dxfirst:** el dx primero, como apertura obligada del reporte.
- **conclude:** conclusión obligada con línea exacta `'Most likely diagnosis: {dx}.'`.
- **confirmed:** dx confirmado, nombrarlo explícito, sin listar diferenciales.

Criterio: la mejor variante debe llevar el **oracle a ~0.85+** (valida el mecanismo). La ganadora se
usa en la corrida completa de 4 condiciones.

### 9.3 Extensiones de evaluación (post-pilot)
1. **Nivel 1 (BLEU/ROUGE/BERTScore/METEOR/CIDEr) vs referencias de SkinCoT.** HAM **no tiene** reportes
   de referencia (solo dx) → el Nivel 1 del ensamble se evalúa sobre **SkinCoT test split** (que sí
   tiene narrativas CoT de referencia). Grounding sobre SkinCoT: oracle = dx de SkinCoT (folder class);
   clasificador real = DermLIP ZS sobre las clases de SkinCoT (o el supersep). Mide si el grounding
   mejora/mantiene la calidad lingüística, no solo la consistency.
2. **Segundo generador: Mini-VLM.** Repetir el grounding (mejor variante) con Mini-VLM para comparar
   ambos VLM bajo el mismo esquema de ensamble.

### 9.4 Idea: fine-tune "grounding-aware" (si el prompt no alcanza)
El grounding actual es **solo inferencia** (prompt sobre el checkpoint v2). Si las variantes de prompt
no llevan el oracle lo suficientemente alto, el siguiente lever es **re-entrenar Stage 2 para que el
modelo APRENDA a comprometerse**: instrucción de entrenamiento con el dx inyectado + targets que
enuncian el dx (≈ la vieja idea "commitment-line"). Esto enseña al modelo a no ignorar el dx, en vez
de forzarlo por prompt. Costo: un re-entrenamiento LoRA (Mendieta). Se decide según el re-pilot:
- prompt alcanza (~0.85) → no hace falta fine-tune; ir a corrida completa.
- prompt no alcanza → plan de fine-tune grounding-aware (nuevo doc `ideas/`).

**Orden sugerido:** re-pilot prompt (9.2) → corrida completa 4 cond. con la mejor variante + Nivel 1
SkinCoT (9.3) → Mini-VLM (9.3) → fine-tune grounding-aware solo si hace falta (9.4).

### 9.5 Diferenciar REPORTE vs RAZONAMIENTO (hallazgo 2026-06-07)

**Problema detectado** (ver [ensamble_resul_20260607 §2](../resul/ensamble_resul_20260607.md)): SkinCoT
bundlea razonamiento (`<think>...</think>` + prosa) y reporte; entrenamos/evaluamos sobre el texto
completo. La `diagnostic_consistency` está **inflada por menciones dentro del razonamiento**: en el
oracle, sacar `<think>` baja la consistency **0.60 → 0.30** (63% del texto es razonamiento). El
"reporte comprometido" acierta el dx ~30%, no 60%.

**Decisiones:**
1. **Evaluar el reporte, no el texto completo.** Ajustar `evaluate_reports`/`clinical_ner` para medir
   sobre la sección de reporte (mismo criterio en generación y referencia). El re-pilot se evalúa en
   **full Y report-only**.
2. **Salida estructurada** `Reasoning + Report` (no solo strippear `<think>`, porque el razonamiento
   también aparece como prosa suelta).
3. **Prompt vs fine-tune (decisión basada en datos):** prompt primero (re-pilot mide el techo);
   **fine-tune grounding-aware solo si el prompt se estanca**. El fine-tune requiere curar targets
   estructurados desde SkinCoT (que no los tiene) — costo de datos a evaluar. Regla: prompt para
   descubrir el techo barato, fine-tune para romperlo si hace falta. (Detalle en el resul doc §3.)
