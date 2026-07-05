# Plan: Consolidación (documento LaTeX) + refinamientos + extensión

**Fecha:** 2026-06-18
**Contexto:** el arco experimental está esencialmente completo (clasificación + generación). Ahora:
(a) consolidar todo en un documento LaTeX detallado, y (b) correr en paralelo refinamientos +
extensión para aprovechar la cola del cluster.

---

## 1. Consolidación — deliverables para el documento LaTeX

Insumos: `docs/resumen_experimentos_20260610.md` (síntesis) + `docs/resul/*` (números) + tablas SOTA.

### 1.1 Cuadros (tablas LaTeX)
- **T1 — Clasificación HAM:** supervisados (DenseNet/ViT/ConvNeXt/Swin) vs VLM general (LLaVA/Mini,
  ZS/lik/CoT/FT) vs **DermLIP** (ZS/linear-probe). Métricas: Acc, F1, sens_macro.
- **T2 — DermLIP por dominio:** HAM (dermatoscopía) vs SkinCAP (clínica), ZS y linear-probe.
- **T3 — Generación v1/v2:** diagnostic_consistency + recall (mostrar la regresión + hedging).
- **T4 — Ensamble (resultado central):** diagnostic_consistency report-only por condición
  (baseline/DermLIP/Swin/oracle) × {LLaVA, Mini}.
- **T5 — Ensamble Nivel 1 SkinCoT:** BLEU/METEOR/CIDEr + consistency, baseline vs oracle (trade-off).
- → Generadas en `docs/consolidacion/tablas.tex` (listas para `\input`).

### 1.2 Figuras
- **F1** — sens_macro por enfoque de clasificación (VLM general ≈ azar vs DermLIP vs supervisado).
- **F2** — consistency report-only por condición de grounding × modelo (propagación del clasificador).
- **F3** — trade-off SkinCoT: consistency (↑) vs BLEU (↓) baseline→oracle.
- → PNGs en `docs/consolidacion/figuras/` (matplotlib).

### 1.3 Esquemas
- Diagrama del **ensamble cascada** (clasificador → generador grounded) — describir para hacerlo en
  TikZ/draw.io.
- Diagrama de los **3 tipos de modelo** (CNN/ViT supervisado · VLM generativo · VL classifier CLIP).

### 1.4 Selección de samples (ejemplos cualitativos, Nivel 3)
- Reporte **baseline (hedging)** vs **grounded-noreasoning (comprometido)** para la misma imagen.
- Caso de **propagación de error** (clasificador erra → reporte se compromete con el dx errado).
- Caso DermLIP acierta donde el VLM general colapsa (clasificación).
- → Extraídos de `outputs/generated_reports/` y `outputs/results/`.

---

## 2. Refinamientos (en paralelo — cluster)

- **Test split completo (1503):** jobs 1157589/1157590 (LLaVA/Mini, ensamble 4 cond. sin --limit,
  resume defensivo). Números definitivos para T4. **En ejecución.**
- **Evaluación cualitativa (Nivel 3):** local, sobre los reportes ya generados (parte de §1.4).
- *(Ablaciones LoRA r / QLoRA: opcionales, Fase 3 — baja prioridad dado el alcance ya cubierto.)*

---

## 3. Extensión mayor — SkinVL (tercer generador derm-especializado)

**Modelo:** `zwq803/SkinVL-MM` (HF) — LLaVA-Med-v1.5-7B + LoRA sobre MM-Skin (3 modalidades, ~10k
pares + 27k VQA). Derm-especializado para generación/VQA.

**Motivación:** completar la comparación de generación con un VLM **derm-especializado** (vs LLaVA-Med/
Mini-VLM generales). Probar el mismo esquema de ensamble (grounding noreasoning) con SkinVL.

**Pasos:**
1. Verificar formato del checkpoint (LoRA sobre LLaVA-Med v1.5 vs full). Descargar local.
2. Wrapper: si es LoRA sobre LLaVA-Med, reusar `llava_med.py` + aplicar el adapter; si es full,
   wrapper nuevo. Registrar en factory.
3. Pre-descargar + subir al cache HF del cluster (nodos offline).
4. Correr: clasificación ZS (¿discrimina como DermLIP?) + generación ensamble (grounding).
5. Documentar en resul + tablas SOTA.

**Estado:** disponibilidad confirmada (HF). Integración pendiente (no es launch inmediato).

### Sincronización con clústeres
- Refinamiento: `sync_up` ya hecho; resume defensivo. `sync_down --reports` al volver.
- SkinVL: pre-descargar pesos local → subir a `~/.cache/huggingface` del cluster (patrón offline) +
  `sync_up` del wrapper. Validar carga local antes de enviar.

---

## 4. Orden sugerido
1. **Ahora (local):** generar T1–T5 (tablas LaTeX) + F1–F3 (figuras) + selección de samples → entregar
   primer batch para el documento LaTeX.
2. **En paralelo (cluster):** full test split (corriendo) → refinar T4 cuando vuelva.
3. **Después:** integrar SkinVL (extensión) → ampliar la comparación de generación.
