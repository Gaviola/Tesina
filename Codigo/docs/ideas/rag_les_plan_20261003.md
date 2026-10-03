# Plan — RAG con el índice de la partición por lesión

**Fecha:** 2026-10-03
**Origen:** [revision_experimentacion](../resul/revision_experimentacion_20261003.md) §2.4. Los brazos
`full_rag` y `full_swin_rag` (Mini-VLM, n = 400, julio) usan `outputs/rag/rag_context.csv`, construido sobre la
partición por imagen: en los casos de test cuya lesión estaba en train/val los vecinos recuperados pueden ser
fotos de la misma lesión (voto kNN 0.790 con ese índice frente a 0.667 con el índice por lesión). Además
`full_swin_rag` está anclado al Swin v3.
**Decisión del autor (2026-10-03):** regenerar en lugar de reportar sobre el subconjunto limpio.

## Hipótesis / pregunta

Con un índice sin fuga y el ancla nueva: (1) ¿cuánto rescata la recuperación sola (RAG sin clasificador)
frente a no anclar y frente al *grounding* con Swin?; (2) ¿sumar RAG al *grounding* con Swin agrega algo?

## Diseño

- **Generador:** Mini-VLM (`stage2_mini_vlm_v2`), mismo que los brazos v3, misma decodificación
  (`--max_tokens 384 --seed 42`). Sin `repetition_penalty` (crashea en Mini-VLM, ver script v3).
- **Brazos (n = 1503, test completo** para alinear con el resto de la tabla de la cascada; v3 usaba 400):
  1. `full_rag_les`: `--rag_context_csv outputs/rag/rag_context_les.csv --rag` (sin diagnóstico).
  2. `full_swin_rag_les`: `--diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt
     --grounded_variant noreasoning --rag_context_csv outputs/rag/rag_context_les.csv`.
- **Índice:** `rag_context_les.csv` (embeddings DermLIP, k = 3, solo train de la partición por lesión;
  verificado en la revisión: sin imágenes ni lesiones de test, se reproduce al 100 %).
- **Comparaciones** (métrica oficial: solo reporte + *matcher* estricto, *bootstrap* pareado 2000):
  `full_rag_les` vs `full_baseline`, vs `full_swin_les` y vs el voto kNN impreso sin generador (línea base
  mecánica); `full_swin_rag_les` vs `full_swin_les`.

## Criterios de éxito / interpretación

- **Completo:** 2 × 1503 reportes, job sin errores (`run_arm` verifica conteos).
- **Lectura:** si RAG solo queda por debajo del *grounding* con Swin con IC que no cruza 0, se confirma que
  la recuperación rescata frente a no anclar pero no reemplaza al clasificador. Si Swin + RAG no supera a
  Swin, la recuperación no agrega sobre el clasificador. Cualquier resultado es reportable; no hay
  resultado «esperado» que condicione la conclusión.

## Sincronización con clústeres

- No hay jobs corriendo en Mendieta. `generate_report.py` remoto es idéntico al local (md5 sin CRLF).
- Se suben por `scp` solo el `.sh` nuevo y `outputs/rag/rag_context_les.csv` (no existe en remoto);
  `full_dx_swin_les.csv` ya está. No hace falta `sync_up` ni `--delete`.
- **Validación local:** `bash -n` del script; el generador no se prueba localmente (no se cargan VLMs sin
  GPU).

## Costo estimado

Mini-VLM generó 1751 reportes en 8 h (job 1177953) → ~14 h para 3006. Límite del job: 2 días. Cola de
Mendieta: 6–10 días según el autor.
