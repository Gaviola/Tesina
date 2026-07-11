# Plan Julio–Agosto 2026 — Extensión de experimentación

**Fecha:** 2026-07-05
**Origen:** feedback del tutor de tesina (`Codigo/docs/feedback_20260705.md`), sobre el documento
de resultados parciales `Docs/experimentacion/experimentacion.tex`.
**Objetivo:** extender la experimentación ~2 meses, priorizando por (1) importancia para el fin de la
tesina y (2) dificultad dado el estado actual del proyecto. **No se espera implementar todo**: la lista
está ordenada para tapar los huecos más importantes primero.

---

## 0. Marco y ancla

- **Ancla (contribución central):** el **ensamble en cascada** (clasificador especializado → generador
  con *grounding*) es la **contribución metodológica**; "**la especialización de dominio importa más
  que la arquitectura general, a bajo costo de cómputo**" es el **hallazgo transversal**. Todo lo que
  profundice el ensamble o refuerce "especialización a bajo costo" sube de prioridad.
- **Presupuesto de cómputo:** ~**6 olas de Mendieta** (A30, cola 5-7 días; para VLM/generación) +
  **TOKO** (RTX 4080, cola corta; solo clasificadores). Jobs en paralelo permitidos, cuidando no
  saturar la cola de terceros. Estimación conservadora a propósito.
- **Regla de oro:** casi toda la **profundidad de análisis es LOCAL** sobre artefactos que **ya
  existen** —los `*_predictions.json` de clasificadores tienen `y_prob`, y hay **~38k reportes
  generados** en `outputs/generated_reports/`—. El cluster se reserva **solo** para lo caro y
  especializado (SkinVL, ablaciones de generación).

---

## 1. Principios operativos (documentación por tarea/ola)

> **Recordatorio permanente (pedido explícito del tutorando):** cada vez que se completa una tarea o
> una "ola" de cluster, se sigue el flujo de tres documentos de siempre, para no perder el orden:

1. **`Codigo/docs/ejecuciones.md`** — registrar toda corrida de cluster (job IDs, cluster, link a este
   plan, comando de submit, link al resul doc). Más reciente primero.
2. **`Codigo/docs/resul/<topico>_resul_<vN>_<YYYYMMDD>.md`** — resultado + análisis con **veredicto
   binario** (cumple / no cumple criterio → siguiente paso).
3. **Actualizar los `.tex`** afectados: `Docs/experimentacion/experimentacion.tex` (documento principal)
   y `Docs/tabla_resultados_sota/tablas_comparativas_sota_v32.tex` (tablas SOTA).

Además: versionar iteraciones (`v3/`, `v4/` en `outputs/` y `slurm/`), nunca sobreescribir; escribir un
plan corto en `Codigo/docs/ideas/` antes de cada ola nueva que lo amerite.

---

## 1.bis Estado de tareas

Leyenda: ✅ completa · 🔄 en curso · ⬜ pendiente. Se marca al cerrar cada tarea/ola con link al resul.

| Tarea | Estado | Resultado |
|-------|:------:|-----------|
| P0.1 Calibración | ✅ | [calibracion_resul_20260705.md](resul/calibracion_resul_20260705.md) |
| P0.2 Tests estadísticos | ✅ | [tests_estadisticos_resul_20260705.md](resul/tests_estadisticos_resul_20260705.md) (ensamble cerrado con P0.3) |
| P0.3 Análisis por clase (ensamble) | ✅ | [per_class_ensemble_resul_20260705.md](resul/per_class_ensemble_resul_20260705.md) |
| P0.4 Comparación de costo | ✅ | [costo_resul_20260705.md](resul/costo_resul_20260705.md) |
| P0.5 Taxonomía de errores | ✅ | [error_taxonomy_resul_20260705.md](resul/error_taxonomy_resul_20260705.md) |
| P0.6 Escritura (reframe/DermLIP/caveat/ejemplos) | ✅ | integrado en `Docs/experimentacion/experimentacion.tex` (21 págs): calibración, tests, por-clase, costo, taxonomía + DermLIP en profundidad + caveat |
| P1.1 SkinVL generación (+ ZS clasif) | ✅ | [skinvl_resul_20260707.md](resul/skinvl_resul_20260707.md) — grounded ≈ Mini, **no hedea**, pero terse; fidelidad = clasificador |
| P1.2 Ablación imagen-vs-dx | ✅ | oracle 1.00 vs sin-imagen 0.97 → **la imagen aporta ~nada** dado el dx ([skinvl_resul](resul/skinvl_resul_20260707.md)) |
| P1.3 Ablación dx-erróneo | ✅ | wrong_dx cons 0.11 → SkinVL se compromete con el dx errado ([skinvl_resul](resul/skinvl_resul_20260707.md)) |
| P2.1 Plantilla clínica | ✅ | [plantilla_resul_20260707.md](resul/plantilla_resul_20260707.md) |
| P2.2 Desbalance (Focal/balanced) | ✅ | [desbalance_resul_20260707.md](resul/desbalance_resul_20260707.md) — CE-plano (sens 0.887) mejor que weighted/focal/balsoftmax → no es desbalance |
| P2.3 Clásicos sobre embeddings | ✅ | [embeddings_resul_20260707.md](resul/embeddings_resul_20260707.md) (SVM/DermLIP≈Swin FT; integrado al `.tex`) |
| P2.4 Robustez por perturbación | ✅ | [robustez_resul_20260707.md](resul/robustez_resul_20260707.md) (Swin+ConvNeXt; integrado al `.tex`) |
| P2.5 Interpretabilidad | ✅ | [interpretabilidad_resul_20260707.md](resul/interpretabilidad_resul_20260707.md) (Grad-CAM Swin + saliencia DermLIP; integrado al `.tex`) |
| P3 Multi-candidato / PanDerm / cross-dataset / dermatólogo | ⬜ | — |

---

## 2. Backlog priorizado (importancia × dificultad)

### P0 — Alta importancia / barato · **LOCAL, arranca YA en paralelo a las olas**

#### P0.1 · Calibración (ECE, Brier, Reliability Diagram) — *feedback #8*
- **Por qué:** responde "¿cuándo el clasificador dice 99% de confianza, realmente acierta?" — crítico en
  medicina; detecta overfit de confianza.
- **Archivos:** crear `scripts/evaluate_calibration.py`; agregar `expected_calibration_error`,
  `brier_score`, `reliability_curve` a `src/evaluation/classification.py`.
- **Insumos:** `outputs/results/classifiers/modern_v3/*_predictions.json` (Swin/ConvNeXt/ViT, con
  `y_prob`); para DermLIP guardar probabilidades desde `scripts/eval_dermlip_classify.py` /
  `eval_dermlip_linearprobe.py`.
- **Éxito:** ECE + Brier + reliability diagram para **Swin y DermLIP** (mínimo). Salida en
  `outputs/results/calibration/`.

#### P0.2 · Tests estadísticos (bootstrap IC 95%, McNemar) — *feedback #2*
- **Por qué:** rigor mínimo esperable; da intervalos de confianza y significancia a las comparaciones.
- **Archivos:** crear `scripts/statistical_tests.py`.
- **Insumos:** predictions JSONs (clasificadores) + consistencia por-reporte del ensamble
  (`outputs/generated_reports/**` evaluados con `scripts/evaluate_reports.py`).
- **Éxito:** IC bootstrap + McNemar para **Swin vs DermLIP vs MiniVLM** y **Baseline vs Grounding vs
  Oracle**.

#### P0.3 · Análisis por clase del ensamble — *feedback #12*
- **Por qué:** "MiniVLM mejora mucho con grounding, ¿en qué clases?" — profundiza LA contribución;
  responde preguntas clínicas segregadas.
- **Archivos:** modificar `scripts/evaluate_reports.py` + `src/evaluation/clinical_ner.py` para agregar
  `diagnostic_consistency` y `clinical_entity_recall` **por clase gt**.
- **Insumos:** `outputs/generated_reports/{llava_med,mini_vlm}/**` + etiquetas HAM (`src/data/ham10000.py`).
- **Éxito:** tabla (7 clases × condición de grounding) por modelo; identificar qué clases gana el
  grounding y cuáles no.

#### P0.4 · Comparación de costo computacional — *feedback #9*
- **Por qué:** es **el eje "costo" de la tesina** (hardware específico vs modelos grandes).
- **Archivos:** crear `scripts/measure_cost.py`; instanciar vía `src/models/factory.py`.
- **Métricas:** parámetros, VRAM, latencia/imagen, tokens/s (VLMs), medidas en RTX 4070 local +
  estimación A30/4080.
- **Éxito:** tabla costo (params/latencia/mem) vs desempeño para clasificadores, VLMs y DermLIP.

#### P0.5 · Taxonomía de errores + frecuencias — *feedback #14*
- **Por qué:** el tutor sugiere que puede ser **aporte metodológico** (la literatura casi no lo hace).
- **Archivos:** crear `scripts/error_taxonomy.py`; apoyarse en el diccionario clínico de
  `src/evaluation/clinical_ner.py`.
- **Categorías:** dx incorrecto · hedging/ambigüedad · contradicción descripción-dx · alucinación
  clínica · repetición/degeneración · descripción morfológica insuficiente · otros.
- **Insumos:** `outputs/generated_reports/**` (todas las condiciones).
- **Éxito:** distribución de errores por modelo/condición; **cuáles desaparecen con grounding y cuáles
  persisten con clasificador preciso**.

#### P0.6 · Escritura (reframe + profundidad) — *feedback #1,#3,#10,#15*
- **Por qué:** reposiciona el ensamble como contribución y agrega la profundidad pedida; costo cero.
- **Archivos:** `Docs/experimentacion/experimentacion.tex`.
- **Contenido:** (a) reframe de la sección de ensamble ("clasificar y generar son tareas distintas → se
  propone un pipeline → se valida"); (b) **discusión conceptual de DermLIP** (entrenamiento contrastivo,
  alineamiento visión-texto, preentrenamiento Derm1M, ontología clínica → por qué discrimina); (c) frase
  **caveat**: "*Aunque Diagnostic Consistency refleja mejor la utilidad clínica que las métricas
  léxicas, sigue siendo una métrica automática y no reemplaza la evaluación de especialistas*"; (d)
  ejemplos cualitativos reporte generado vs referencia.

---

### P1 — Alta importancia / caro · **la apuesta de cluster (Mendieta)**

#### P1.1 · SkinVL — especialización en generación (+ SkinVL-clasificador ZS gratis) — *feedback #17,#22,#19*
- **Por qué:** **la prueba más importante de generación**. Si un generador derm-especializado (SkinVL-MM
  = LLaVA-Med-v1.5 + LoRA sobre MM-Skin) hedge menos / alucina menos / sube consistencia, se confirma que
  la especialización también importa en generación (no solo en clasificación).
- **Archivos:** crear `src/models/skinvl.py` (o reusar `src/models/llava_med.py` + aplicar el adapter
  LoRA), registrar en `src/models/factory.py`; crear `slurm/mendieta/v3/generate_reports_skinvl.sh`
  (espejo de `slurm/mendieta/ensemble_full_llava.sh`). Pre-descargar el checkpoint HF (`zwq803/SkinVL-MM`)
  al cache del cluster (nodos offline).
- **Insumos:** `outputs/full_dx_{oracle,swin,dermlip}.csv` (mismos CSV de grounding, model-agnostic).
- **Corridas:** baseline + grounding *noreasoning* en HAM (Nivel 2) + SkinCoT/MM-Skin (Nivel 1). **Extra
  casi gratis:** SkinVL como **clasificador ZS** en la misma ola (cubre parte de *feedback #19*).
- **Riesgo:** integración del LoRA (ya nos pasó que una variante DermLIP no cargaba). **Validar carga
  local antes de enviar.** Fallback: P2.1 (plantilla).
- **Éxito:** consistencia/recall de SkinVL vs LLaVA-Med/Mini-VLM; veredicto sobre si la especialización
  se traslada a generación.

#### P1.2 · Ablación imagen-vs-dx (flagship) — *feedback #4,#5*
- **Por qué:** "¿cuánto conocimiento visual se sigue usando una vez conocido el diagnóstico?" — la
  pregunta que el tutor marca como más interesante.
- **Archivos:** modificar `scripts/generate_report.py` (flag `--no_image` → imagen en blanco/None +
  prompt solo-dx). **Se bundlea como condición extra** en la ola de generación (no es ola nueva).
- **Éxito:** Δ de Diagnostic Consistency con imagen vs sin imagen, dado el mismo dx.

#### P1.3 · Ablación dx-erróneo (robustez del generador) — *feedback #13*
- **Por qué:** mide si el generador "se compromete" con el error del clasificador.
- **Archivos:** crear `scripts/make_wrong_dx.py` (CSV de dx perturbados: swap a clase confundible /
  usar los errores del clasificador débil); correr con
  `scripts/generate_report.py --diagnosis_source outputs/wrong_dx.csv`. **Bundleado** en la misma ola.
- **Éxito:** caída de consistencia/aparición de contradicciones con dx incorrecto vs correcto.

> **Nota de costo:** P1.2 y P1.3 **no cuestan olas nuevas** — son `output_dir`/condiciones extra dentro
> de los jobs `slurm/mendieta/ensemble_full_*.sh` y de la ola de SkinVL. Juntas arman la historia:
> *perturbación → cuánto se degrada el clasificador (P2.4) → qué hace el generador con dx malo (P1.3)*.

---

### P2 — Media importancia / barato-medio

#### P2.1 · Baseline de generación por plantilla clínica — *feedback #23*
- **Por qué:** **baseline de costo** fuerte + **fallback de SkinVL**. Si una plantilla barata sobre el
  clasificador ya da alta consistencia, cuestiona si hace falta un VLM generativo pesado.
- **Archivos:** crear `scripts/generate_template_report.py`; usa predicciones del clasificador
  (`outputs/results/...`) + atributos morfológicos (conceptos DermLIP `src/models/dermlip.py` /
  diccionario `src/evaluation/clinical_ner.py`) → plantilla. **Local.** Evaluar con
  `scripts/evaluate_reports.py`.
- **Éxito:** consistencia de la plantilla vs VLMs (¿cuánto agrega el VLM sobre un baseline trivial?).

#### P2.2 · Manejo explícito del desbalance — *feedback #21*
- **Por qué:** cierra el "¿y si es solo el desbalance de HAM10000?" — si Focal/balanced no mueve la
  aguja, refuerza que el problema no es el desbalance.
- **Archivos:** `src/training/losses.py` **ya existe** → agregar Focal / class-balanced / balanced-softmax;
  exponer en `configs/` + `scripts/train_classifier.py`; SLURM en `slurm/toko/`.
- **Cluster:** **TOKO** (barato, ~1 ola corta).
- **Éxito:** Δ métricas de Swin con vs sin manejo de desbalance.

#### P2.3 · Modelos clásicos sobre embeddings — *feedback #20*
- **Por qué:** del ancla de costo: si un SVM sobre buenos embeddings ya separa las clases, es la
  representación —no el fine-tuning pesado— lo que importa.
- **Archivos:** crear `scripts/embeddings_classical.py`; extraer embeddings de DermLIP
  (`src/models/dermlip.py`) y Swin; entrenar SVM/RF/XGBoost (sklearn). **Local.**
- **Éxito:** F1/sens de clásicos sobre embeddings vs fine-tuning completo.

#### P2.4 · Robustez por perturbación (clasificador) — *feedback #7*
- **Por qué:** "¿qué pasa si cambian las condiciones de adquisición?" HIBA ya cubre cambio de población;
  falta calidad de imagen.
- **Archivos:** agregar perturbaciones (JPEG, ruido gaussiano, blur, bajada de resolución; oclusión
  opcional) a `src/data/transforms.py`; crear `scripts/robustness_perturbations.py`; re-inferencia
  **local** de Swin/DermLIP.
- **Alcance:** solo clasificador (la generación se cubre por propagación + P1.3). Cero cluster.
- **Éxito:** curva de robustez (Δacc/Δsens por severidad) para Swin y DermLIP.

#### P2.5 · Interpretabilidad — *feedback #11*
- **Por qué:** mostrar que el modelo observa regiones clínicas relevantes (no mejora resultados, pero es
  muy mostrable y lo pidió explícito para Swin/DermLIP).
- **Archivos:** crear `scripts/interpretability.py` (Grad-CAM para Swin; attention maps / rollout para
  DermLIP); análisis en `notebooks/`. **Local** (modelos chicos en RTX 4070).
- **Éxito:** mapas de saliencia/atención sobre ejemplos representativos.

---

### P3 — Stretch / oportunista / afuera

- **Multi-candidato + incertidumbre (liviano)** — *#16*: top-2 dx + probabilidades en el prompt, como
  condición extra oportunista en `scripts/generate_report.py` si sobra GPU en una ola.
- **PanDerm/otro foundation como clasificador propio** — *#19*: solo si sobra una ola tarde (nueva
  entrada en `src/models/` + `factory.py`). Los números publicados ya están en la tabla SOTA.
- **1 evaluación cross-dataset extra** — *#6*: Swin/DermLIP sobre otro set derm mapeable a 7 clases,
  local. (No se construye dataset unificado: mezcla modalidades/taxonomías.)
- **Validación por dermatólogo** — *#18*: **al final**, si se consigue especialista. Preparar rúbrica
  (claridad, utilidad clínica, coherencia descripción-dx, completitud morfológica, ayuda a la decisión)
  y muestreo n≈20-30. **Sin garantía** de conseguir gente → no bloquea el resto.
- **Afuera:** RAG/generación por casos similares (#24, infra cara); ensamble uncertainty-aware completo
  (build grande); merge de datasets (metodológicamente sucio).

---

## 3. Secuenciación (respeta cola de 5 días + paralelismo local)

| Semana | Cluster (olas) | Local (en paralelo) |
|--------|----------------|---------------------|
| **0-1** | **Ola 1 Mendieta:** SkinVL + ensamble con P1.2 y P1.3 bundleadas (palo largo: integración + cola). **TOKO:** P2.2 desbalance. | **Todo P0** (calibración, tests, por-clase, costo, taxonomía) sobre artefactos existentes. Preparar P2.1 plantilla (fallback). |
| **2-3** | Analizar Ola 1. Si SkinVL no carga → plantilla pasa a primaria; **Ola 2** con fix. | P0.6 escritura (DermLIP, caveat, ejemplos); P2.3 clásicos-embeddings; P2.5 interpretabilidad. |
| **4-5** | **Ola 2/3:** fixes / multi-candidato (#16) / PanDerm stretch. | P2.4 robustez perturbación; integrar todo en `experimentacion.tex` + tablas SOTA. |
| **6-7** | Buffer de reruns (conservador). | Validación dermatólogo si se consiguió; escritura y pulido final. |

**Primera acción concreta:** lanzar la Ola 1 (SkinVL) lo antes posible —es el palo largo por cola +
riesgo de integración— y **arrancar P0 el mismo día** (no depende del cluster).

---

## 4. Sincronización con clústeres

- **Antes de cada ola:** `python scripts/mendieta/sync_up.py` (código + wrapper SkinVL + CSVs de dx /
  wrong_dx). Usar `--delete` para limpiar huérfanos remotos cuando corresponda.
- **SkinVL (nodos offline):** pre-descargar `zwq803/SkinVL-MM` local → subir a `~/.cache/huggingface`
  del cluster (patrón offline, `HF_HUB_OFFLINE=1`). **Validar carga local del checkpoint antes de
  enviar el job** (evita quemar una ola de 5 días por un error de formato).
- **Al volver:** `sync_down.py --logs <jobids>` + `sync_down.py --reports` (los reportes pueden ser GBs).
- **Resume defensivo:** `generate_report.py` saltea reportes ya escritos; ante timeout, inspeccionar el
  log y re-enviar.
- **TOKO** solo para P2.2 (clasificadores). Mendieta para todo lo VLM/generación.

---

## 5. Mapa feedback → tarea (trazabilidad de los 24 ítems)

| Ítem feedback | Tarea | Estado/prioridad |
|---|---|---|
| #1 ejemplos reportes | P0.6 | P0 |
| #2 tests estadísticos | P0.2 | P0 |
| #3 ensamble como contribución | P0.6 (reframe) | P0 |
| #4/#5 aporte de la imagen / ¿imágenes o algoritmos? | P1.2 + (costo/robustez/calibración transversal) | P1 |
| #6 datasets unificados | P3 (sin merge; HIBA+DermLIP + eval extra opcional) | P3 |
| #7 robustez adquisición | P2.4 (HIBA ya cubre población) | P2 |
| #8 calibración | P0.1 | P0 |
| #9 costo | P0.4 | P0 |
| #10 caveat métricas | P0.6 | P0 |
| #11 interpretabilidad | P2.5 | P2 |
| #12 análisis por clase | P0.3 | P0 |
| #13 ablaciones ensamble | P1.2 + P1.3 (+ multi-candidato P3) | P1 |
| #14 taxonomía de errores | P0.5 | P0 |
| #15 DermLIP en profundidad | P0.6 | P0 |
| #16 uncertainty-aware | P3 liviano (completo afuera) | P3 |
| #17/#22 VLM derm-especializado generación | P1.1 (SkinVL) | P1 |
| #18 dermatólogo | P3 (cierre, sin garantía) | P3 |
| #19 foundation clasificación | P1.1 (SkinVL-ZS) + DermLIP hecho + publicados; PanDerm P3 | P1/P3 |
| #20 clásicos sobre embeddings | P2.3 | P2 |
| #21 desbalance | P2.2 | P2 |
| #23 plantilla clínica | P2.1 | P2 |
| #24 RAG | Afuera | — |
