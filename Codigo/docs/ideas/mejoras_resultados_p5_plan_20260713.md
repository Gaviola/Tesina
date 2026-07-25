# Plan — P5: Mejorar resultados (clasificación + reportes) + huecos del feedback

**Fecha:** 2026-07-13 · **Origen:** pedido del usuario (mejorar métricas de clasificación y calidad de
reportes) + huecos de [feedback_20260705.md](../feedback_20260705.md) no atacados (RAG, ensamble consciente
de incertidumbre, Wilcoxon). Complementa [plan-julio-agosto.md](../plan-julio-agosto.md).

## Motivación

La ronda anterior (P0–P4) cubrió casi todo el feedback. Quedan tres huecos explícitos (RAG, incertidumbre,
Wilcoxon) y dos metas nuevas del usuario: **subir las métricas de clasificación** y **mejorar la calidad de
los reportes**. Este plan agrupa cinco tareas, priorizadas por costo/dependencia (locales primero).

Recordar el objetivo de la tesina: no usar un supermodelo, sino una **estructura eficiente** que en hardware
modesto se acerque a los modelos grandes. Toda mejora se juzga también por su costo.

## Tareas

### P5.1 — Ensamble de clasificadores (LOCAL, sin cluster) · mejora clasificación · ✅ HECHO
> **Resultado:** Swin+ConvNeXt (TTA) sens. macro 0.846 vs mejor individual 0.827 (Δ+0.019, 2× costo).
> Ver [resul](../resul/mejoras_p5_local_resul_20260713.md).

- **Idea:** voto suave (promedio de probabilidades) de Swin + ConvNeXt (+DenseNet +ViT), sobre los
  `y_prob` ya guardados (`modern_v3`, n=1503, mismo test). Opcional: sumar DermLIP-probe (requiere re-correr
  DermLIP guardando `y_prob`).
- **Criterio de éxito:** sens_macro y F1-w del ensamble > mejor individual (Swin 0.887 / 0.882).
- **Código:** `scripts/classifier_ensemble.py`. **Salida:** `outputs/results/classifier_ensemble/`.

### P5.2 — Test de Wilcoxon (LOCAL) · hueco feedback · ✅ HECHO
> **Resultado:** Wilcoxon por clase agregado; Swin domina clase-a-clase (p<0.05), VLMs generales
> indistinguibles entre sí (p=1.0). Ver [resul](../resul/mejoras_p5_local_resul_20260713.md).

- **Idea:** completar el trío bootstrap+McNemar+**Wilcoxon** que pedía el feedback. Wilcoxon de rangos con
  signo sobre una métrica pareada por muestra o por clase (p.ej. acierto por clase entre dos modelos, o
  consistency por reporte baseline vs grounding).
- **Código:** extender `scripts/statistical_tests.py` con Wilcoxon. **Salida:** actualizar
  `resul/tests_estadisticos_*`.

### P5.3 — RAG / generación basada en casos similares (CLUSTER) · mejora reportes · ✅ HECHO (job 1160552)
> **Resultado:** RAG-only consistency 0.20→0.76 (≈ clasificador) + entity recall 0.91 (el más alto); apilar
> RAG sobre el clasificador aporta poco. kNN-dx (DermLIP) acc 0.831. Ver
> [rag_resul](../resul/rag_resul_20260719.md). Integrado a `experimentacion.tex` §RAG.

- **Idea:** con los embeddings **DermLIP** de HAM-train (ya tenemos el encoder), para cada imagen de test
  recuperar los k=3 vecinos más cercanos del train + su dx y morfología, e inyectarlos como contexto en el
  prompt del generador ("casos similares muestran: …"). Reduce alucinación y aporta morfología concreta.
- **Diseño:** (1) construir índice de embeddings train (local, `scripts/build_dermlip_index.py`); (2) función
  de retrieval; (3) nueva variante de prompt RAG en `generate_report.py`; (4) correr generación en cluster
  (Mini-VLM, n=400) comparando baseline vs grounding-oracle vs **RAG** vs **grounding+RAG**.
- **Criterio:** RAG mejora `clinical_entity_recall` y/o baja alucinaciones (taxonomía) sin degradar
  consistency; grounding+RAG ≥ grounding.

### P5.4 — Generación consciente de la incertidumbre (CLUSTER) · mejora reportes
- **Idea:** calibrar el clasificador (temperature scaling en el split de **validación**), y pasar al
  generador el **top-k dx + probabilidades**: si la confianza calibrada supera un umbral → reporte
  definitivo (grounding actual); si no → prompt que pide un **diagnóstico diferencial** con los candidatos.
- **Diseño:** (1) temp scaling local sobre `y_prob` de validación (`scripts/temperature_scaling.py`);
  (2) generar CSV top-k por imagen; (3) variantes de prompt "definitivo" / "diferencial" en
  `generate_report.py`; (4) correr en cluster (Mini-VLM, n=400).
- **Criterio:** en imágenes de baja confianza, el reporte diferencial menciona el dx correcto entre sus
  candidatos con mayor recall que el grounding forzado (que propaga el error, ver P4.1).

### P5.5 — Fix de repetición en el decoding (CLUSTER, barato) · mejora reportes · ⚠️ DIFERIDO a LLaVA-Med
> `repetition_penalty`/`no_repeat_ngram_size` crashean Mini-VLM (Phi-3.5): sus input_ids llevan tokens de
> imagen fuera del rango del vocabulario y el logits-processor de repetición hace gather fuera de límites
> (CUDA device-side assert). En LLaVA-Med el image token (32000) está dentro del vocab (32064) → seguro.
> Pendiente: probarlo en LLaVA-Med sobre una condición existente (p.ej. grounding-swin) y medir si baja la
> repetición. El código ya soporta los flags (`--repetition_penalty/--no_repeat_ngram_size`).
- **Idea:** agregar `repetition_penalty` / `no_repeat_ngram_size` al `generate` para eliminar el artefacto de
  repetición (Fig. ej_rep). Se pliega a las corridas de P5.3/P5.4 (mismo job) para no gastar cola extra.
- **Criterio:** desaparece la degeneración por repetición sin bajar consistency.

## Orden de ejecución
1. **P5.1 + P5.2** (locales, resultado inmediato sobre datos existentes).
2. **P5.5** (cambio de código barato, se valida junto con P5.3/P5.4).
3. **P5.3 RAG** y **P5.4 incertidumbre** (construir infra local → 1-2 jobs de generación en Mendieta/TOKO).

## Sincronización con clústeres
- P5.1/P5.2 son **100% locales** (operan sobre `y_prob`/reportes ya descargados): no requieren cluster.
- P5.3/P5.4/P5.5 requieren `sync_up.py` de los cambios de `generate_report.py`, los nuevos scripts de índice
  RAG / top-k, y los CSV auxiliares (top-k, retrieval). Usar `sync_up.py` (no `--delete`, para no borrar
  checkpoints/datos remotos). Los CSV de retrieval/top-k se generan **local** y se suben con el código.
- Validar la carga y un smoke de 5 imágenes **antes** de lanzar la corrida de 400 (evitar quemar cola).
- Bajada: `sync_down.py --reports` (o tar+scp targeted de las carpetas nuevas), luego evaluar local.
- Todo submit queda en `outputs/jobs_log.txt` (auto por `submit.py`) y se registra en `ejecuciones.md`.
