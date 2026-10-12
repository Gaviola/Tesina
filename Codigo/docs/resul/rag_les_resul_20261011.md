# Resultado — RAG con el índice de la partición por lesión

**Fecha:** 2026-10-11 · **Plan:** [rag_les_plan](../ideas/rag_les_plan_20261003.md) · **Job Mendieta:** 1179315
(alias `rag_les`, `slurm/mendieta/v4/rag_les_mini_vlm.sh`; COMPLETED, exit 0, 21 h 03 min) · **Antecedentes:**
[rag_resul](rag_resul_20260719.md) (índice con fuga, n = 400) y
[revision_experimentacion](revision_experimentacion_20261003.md) §2.4 y §5.

Fuentes: `outputs/generated_reports/mini_vlm/{full_rag_les,full_swin_rag_les}/` (1503 + 1503 reportes, bajados
el 2026-10-11 con `sync_down.py --reports`), `outputs/results/rag_les_eval.json`, generado con
`scripts/rag_les_eval.py` (local, CPU). Log: `outputs/slurm_logs/mini_vlm/1179315.out`.

## 1. Motivación

Los brazos RAG de julio (`full_rag`, `full_swin_rag`, n = 400) usaban `rag_context.csv`, construido sobre la
partición por imagen: en los casos de test cuya lesión estaba en train/val, los vecinos podían ser fotos de la
misma lesión. Además `full_swin_rag` estaba anclado al Swin v3. El autor decidió regenerar (2026-10-03) en vez
de reportar sobre el subconjunto limpio.

## 2. Diseño

- Generador Mini-VLM (`stage2_mini_vlm_v2`), decodificación voraz, 384 tokens, semilla 42; test completo
  (n = 1503), igual que el resto de la tabla de la cascada.
- Índice `rag_context_les.csv`: *embeddings* DermLIP, k = 3, solo imágenes de entrenamiento de la partición por
  lesión. El voto kNN acierta 0.781 en el test (0.831 con el índice con fuga).
- Brazos: `full_rag_les` (contexto de los vecinos, sin diagnóstico) y `full_swin_rag_les` (ancla Swin por lesión
  + contexto, plantilla *noreasoning*).
- Métrica oficial: consistencia diagnóstica solo sobre el reporte, *matcher* estricto; *bootstrap* pareado
  (2000, semilla 42). Se agrega la **consistencia exclusiva** (nombra la clase verdadera y ninguna otra de las
  siete) para separar las ganancias que vienen de nombrar más de una clase.
- Líneas base mecánicas (sin generador): imprimir el voto kNN y imprimir el diagnóstico de Swin.

## 3. Resultados (n = 1503)

| Brazo | Consistencia | Exclusiva |
|---|---|---|
| Sin anclaje (`full_baseline`) | 0.163 | 0.045 |
| RAG solo (`full_rag_les`) | 0.669 | 0.500 |
| Voto kNN impreso, sin generador | 0.781 | 0.781 |
| *Grounding* Swin (`full_swin_les`) | 0.849 | 0.757 |
| Swin impreso, sin generador | 0.847 | 0.847 |
| Swin + RAG (`full_swin_rag_les`) | **0.862** | 0.792 |

| Comparación | Δ consistencia [IC 95 %] | Δ exclusiva [IC 95 %] |
|---|---|---|
| RAG solo − sin anclaje | +0.506 [+0.476, +0.534] | +0.455 [+0.428, +0.482] |
| RAG solo − *grounding* Swin | −0.180 [−0.206, −0.155] | −0.257 [−0.287, −0.226] |
| RAG solo − voto kNN impreso | −0.112 [−0.134, −0.089] | −0.281 [−0.307, −0.255] |
| Swin + RAG − *grounding* Swin | +0.013 [+0.007, +0.019] | +0.035 [+0.017, +0.053] |
| Swin + RAG − Swin impreso | +0.015 [+0.009, +0.021] | −0.055 [−0.067, −0.043] |

Por clase (consistencia): RAG solo queda por debajo del *grounding* Swin en todas las clases salvo VASC (0.909
frente a 0.818, n = 22), con la mayor caída en BKL (0.345 frente a 0.770) y DF (0.353 frente a 0.647). Swin + RAG
iguala o supera a Swin en todas salvo VASC (0.773 frente a 0.818); la mayor ganancia es MEL (0.737 frente a
0.695, n = 167).

## 4. Análisis

1. **La recuperación sola rescata frente a no anclar, pero no reemplaza al clasificador.** +0.506 sobre no
   anclar, −0.180 frente al *grounding* con Swin, ambos con IC que no cruzan 0. Es la lectura que el plan
   anticipaba como confirmación.
2. **Con RAG solo el generador pierde información respecto de los propios vecinos.** Imprimir el voto kNN da
   0.781 y el generador que recibe ese contexto llega a 0.669 (−0.112), y en consistencia exclusiva cae a la
   mitad de los casos. Cuando los vecinos no coinciden, el generador no elige el voto mayoritario de forma
   confiable, y nombra varias clases o una distinta. La recuperación aporta como evidencia, no como decisión.
3. **Swin + RAG mejora apenas sobre el *grounding* con Swin, y la mejora viene de nombrar más candidatos.**
   +0.013 en consistencia frente al *grounding* y +0.015 frente a imprimir Swin, pero −0.055 en consistencia
   exclusiva frente a Swin impreso: el reporte suma la clase de los vecinos cuando difiere del ancla. Es el
   mismo mecanismo que la revisión encontró en el diferencial (§2.1: el pipeline avanzado no supera la
   cobertura mecánica del par de candidatos). Frente al *grounding* Swin, Swin + RAG es más exclusivo (+0.035):
   el contexto de los vecinos reduce las menciones de diagnósticos alternativos que el *grounding* solo produce.
4. **Cambio respecto de julio.** Con el índice con fuga, el ancla v3 y el *matcher* anterior (n = 400), el RAG
   solo quedaba a −0.070 del *grounding* Swin (0.760 frente a 0.830) y el resul de julio lo leía como «≈
   clasificador». Con el índice por lesión, el ancla nueva y la métrica oficial, la distancia es −0.180 en el
   test completo: esa lectura no se sostiene. Swin + RAG sobre Swin da +0.013 en ambos casos. La cobertura de
   entidades clínicas de los brazos nuevos no se calculó (requiere el NER local de `evaluate_reports.py`).

## 5. Conclusión (veredicto)

**CUMPLE.** El job completó los 2 × 1503 reportes y las dos preguntas del plan quedan respondidas con IC: (1) la
recuperación sin clasificador rescata frente a no anclar (+0.506) pero queda por debajo del *grounding* con Swin
(−0.180) y del voto kNN impreso (−0.112); (2) sumar RAG al *grounding* con Swin agrega +0.013, atribuible a
nombrar la clase de los vecinos además de la del ancla (consistencia exclusiva −0.055 frente a Swin impreso).
Estos brazos reemplazan a `full_rag` y `full_swin_rag` (índice con fuga) en la tabla de la cascada; los de julio
quedan solo como antecedente. No hace falta otra iteración.
