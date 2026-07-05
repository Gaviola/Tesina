# Resumen de experimentos y resultados (abril–junio 2026)

**Fecha:** 2026-06-10
**Alcance:** síntesis de toda la campaña experimental de los últimos ~2 meses, con los resultados
clave y la conclusión que se desprende. Registro detallado en [ejecuciones.md](ejecuciones.md) y los
docs de [resul/](resul/).

---

## 1. Objetivo del trabajo

Comparar **clasificadores tradicionales (CNN/ViT) vs VLMs** en diagnóstico de lesiones de piel
(HAM10000, 7 clases dermatoscópicas), y luego usar VLMs para **generar reportes clínicos**. Dos
líneas: **(F1) clasificación** y **(F2) generación de reportes**.

---

## 2. Línea de CLASIFICACIÓN

### 2.1 Clasificadores supervisados (baseline fuerte)
Sweep de recipes modernas (TOKO). Mejor modelo: **Swin-Tiny (F1=0.882, Acc=0.827)**; ViT-B/16 0.862,
ConvNeXt-Tiny 0.861, DenseNet121 0.852. Evaluación OOD en HIBA documentada (trade-off in-dist vs OOD).

### 2.2 VLMs generativos en clasificación → COLAPSO
LLaVA-Med 7B y Mini-VLM evaluados en zero-shot, likelihood scoring, CoT, y fine-tuned (Stage 2 v1 y
v2, epochs=10). **En todas las variantes colapsan** (sens_macro ≈ 0.12–0.18 ≈ azar 1/7):

| Modelo / método | sens_macro | F1 |
|-----------------|-----------|-----|
| LLaVA-Med likelihood ZS | 0.157 | 0.028 |
| Mini-VLM likelihood ZS | 0.181 | 0.268 |
| LLaVA-Med FT lik v2 (Stage 2, 10 ep) | 0.137 | 0.198 |
| Mini-VLM FT lik v2 | 0.141 | 0.532 |

### 2.3 Re-diagnóstico del colapso (hallazgo importante)
La hipótesis inicial (imbalance de entrenamiento → plan v3 de class weights) **se falsificó** al
verificarla contra los datos:
- El colapso **existe en zero-shot** (antes del fine-tuning).
- Los datos de entrenamiento (SkinCoT 23 clases, SkinCAP 179) **NO** están sesgados a NV/MEL.
- Cada combo colapsa a una clase **arbitraria distinta** (LLaVA lik→MEL, CoT→VASC; Mini lik→NV, CoT→MEL)
  → no es frecuencia, es incapacidad de discriminar.
- Experimento de "domain gap" (evaluar en foto clínica SkinCAP): **NO confirmado** — la clínica
  tampoco discrimina (sens_macro 0.106/0.176 ≈ azar), y colapsa a otra clase (DF).

**Conclusión 2.3:** el colapso **no es imbalance ni domain gap dermatoscópico**, sino una
**incapacidad general de los VLMs médicos generales para la clasificación dermatológica de grano fino**
(predicción guiada por artefactos del prompt, no por la imagen). El plan v3 (class weights) fue anulado.

### 2.4 DermLIP — un VL model derm-especializado SÍ resuelve la clasificación
Se agregó **DermLIP** (CLIP-style, pre-entrenado en Derm1M; `src/models/dermlip.py`, ~150M, libre).
Rompe el colapso:

| Enfoque (HAM test) | sens_macro | Acc | F1 |
|--------------------|-----------|-----|-----|
| VLM general (LLaVA/Mini) | ~0.14 | — | 0.03–0.53 |
| **DermLIP zero-shot** | **0.510** | 0.377 | 0.424 |
| **DermLIP linear-probe** (encoder congelado + LR) | **0.739** | 0.741 | **0.762** |
| Swin-Tiny supervisado | — | 0.827 | **0.882** |

DermLIP discrimina también en foto clínica (sens_macro 0.454) → la especialización de dominio es el
factor decisivo, no la modalidad de imagen.

---

## 3. Línea de GENERACIÓN DE REPORTES

### 3.1 Generación v1 / v2 → reportes ricos pero que "hedean"
Fine-tuning en 2 etapas (Stage 1 SkinCAP + Stage 2 SkinCoT), inferencia sobre HAM/MM-SkinQA/SkinCoT.
Métricas Nivel 2 (NER clínico) en HAM10000:

| | diagnostic_consistency | clinical_entity_recall |
|---|---|---|
| LLaVA-Med v1 → v2 | 0.72 → **0.63** | 0.46 → **0.82** |
| Mini-VLM v1 → v2 | 0.35 → **0.23** | 0.61 → 0.55 |

El recall sube (reportes más ricos) pero la `diagnostic_consistency` **regresa**: el modelo enumera
diferenciales sin comprometerse (estilo Chain-of-Thought heredado de SkinCoT). Nivel 1 (BLEU/CIDEr)
plano y ≈0. *(La generación v2 además sufrió problemas de scope/timeout — se evaluó por aproximación.)*

### 3.2 Hallazgo metodológico: reporte vs razonamiento
SkinCoT bundlea razonamiento (`<think>`) + reporte; entrenamos/evaluamos sobre el texto completo. La
`diagnostic_consistency` está **inflada por menciones dentro del razonamiento**: al separar, la
consistency del reporte comprometido es mucho menor (en grounding "soft": full 0.60 vs **report-only
0.30**). → **Hay que medir el reporte, no el razonamiento.**

### 3.3 Paradigma nuevo: ENSAMBLE en cascada (clasificador → generador con grounding)
Desacoplar las tareas: un **clasificador fuerte** decide el diagnóstico y el **generador** escribe el
reporte **condicionado (grounded)** a ese dx. Iteración de prompt (oracle = dx correcto, report-only):

| Prompt de grounding | consistency report-only | % razonamiento |
|---------------------|-------------------------|----------------|
| soft | 0.30 | 63% |
| confirmed (sin diferenciales) | 0.70 | 53% |
| **noreasoning** (prohíbe el razonamiento) | **0.85** | **1%** |

**El grounding + prohibir el razonamiento recupera el commitment** (report-only 0.30 → 0.85 con dx
correcto), sin fine-tune.

**Corrida completa (2026-06-18) — diagnostic_consistency report-only, HAM:**

| grounding (clasif. acc) | LLaVA | Mini-VLM |
|-------------------------|-------|----------|
| baseline (sin grounding) | 0.595 | 0.198 |
| DermLIP ZS (0.38) | 0.445 | 0.485 |
| Swin supervisado (0.80) | 0.703 | 0.830 |
| oracle (gt, 1.0) | 0.845 | 1.000 |

- **El ensamble funciona y la calidad del clasificador propaga monótonamente.** Con un clasificador
  fuerte (Swin): Mini 0.20→0.83, LLaVA 0.60→0.70.
- **Un clasificador débil puede empeorar** (DermLIP ZS en LLaVA: 0.445 < baseline 0.595) → costo de
  propagación de error. Receta óptima: **Swin + generador con prompt noreasoning**.
- **SkinCoT (Nivel 1):** grounding ↑ consistency (0.39→0.57) pero ↓ léxico (BLEU 0.10→0.04) — el
  reporte conciso comprometido calza menos con la referencia CoT verbosa (trade-off de estilo, no de
  calidad). → para reportes, **Nivel 2 (fidelidad diagnóstica) es la métrica principal**.

---

## 4. CONCLUSIÓN

De los resultados de estos 2 meses se desprende una historia coherente y, sobre todo, **honesta**:

1. **En clasificación dermatoscópica, los VLMs médicos generales no compiten.** LLaVA-Med y Mini-VLM
   colapsan (sens_macro ≈ azar) en toda variante (ZS/likelihood/CoT/fine-tuned), y se demostró que
   **no es por imbalance ni por dermatoscopía específicamente, sino una limitación general de grano
   fino**. Los clasificadores supervisados (Swin-Tiny F1=0.882) son muy superiores.

2. **La especialización de dominio es lo que importa, no la "modalidad VLM".** Un VL model
   derm-especializado (DermLIP) **rompe el colapso** incluso zero-shot (sens_macro 0.51) y con un
   simple linear-probe se acerca al supervisado (F1 0.76 vs 0.88). → La frase de tesis: *VLM médico
   general → colapsa; VL model derm-especializado → discrimina; supervisado → mejor accuracy.*

3. **El valor de los VLMs generativos está en la generación de reportes, no en clasificar.** Generan
   texto clínico rico, pero por sí solos **no se comprometen con un diagnóstico** (hedging CoT).

4. **El ensamble en cascada es la vía prometedora para reportes confiables:** combinar un clasificador
   fuerte (que decide el dx) con un generador *grounded* que **debe** afirmar ese dx y no razonar
   eleva la fidelidad del reporte de forma drástica (report-only 0.30 → 0.85). Es un sistema híbrido,
   alineado con el SOTA (ensemble DL+LLM).

5. **Aporte metodológico:** en evaluación de reportes hay que **diferenciar el reporte del
   razonamiento**; métricas sobre el texto completo sobreestiman la fidelidad diagnóstica.

**En síntesis:** para *diagnosticar* conviene un modelo especializado (supervisado o VL derm-específico);
para *reportar*, un VLM generativo **anclado a un clasificador**. Ningún VLM general resuelve solo
ambas tareas; el ensamble de modelos especializados sí cubre el objetivo de la tesis (detección +
generación de reportes).

---

## 5. Estado actual y próximos pasos

- **En ejecución (Mendieta):** corrida completa del ensamble (4 condiciones × LLaVA/Mini sobre HAM) +
  Nivel 1 sobre SkinCoT (jobs 1156723/1156724/1156725).
- **Al volver:** tabla final baseline/oracle/Swin/DermLIP × {LLaVA, Mini} (report-only) + métricas
  léxicas SkinCoT → cuantifica el costo de propagación de error del clasificador real.
- **Pendiente/opcional:** fine-tune "grounding-aware" (solo si el prompt no alcanzara — ya alcanzó),
  agregar un VLM generativo derm-especializado (SkinVL/DermatoLlama), ablaciones (Fase 3).
