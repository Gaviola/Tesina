# Plan — Nivel 1 pareado de Mini-VLM v2 y LLaVA-Med v2 en la prueba de MM-Skin (25/10/2026)

## Motivación

Revisión del autor del Cap. 5 (25/10): `tab:res_gen_nivel1` compara a los dos generadores en MM-Skin sobre pares
distintos, y el texto dice que la diferencia «no se interpreta». Las dos filas vienen de corridas distintas:

- LLaVA-Med v2: corrida dedicada a la prueba (`generated_reports/llava_med/v2/mmskin_test`, 1 650 imágenes, 1 414 pares
  con referencia).
- Mini-VLM v2: corrida vieja sobre el archivo completo (`generated_reports/mini_vlm/v2/mmskin`, 7 129 reportes, cortada
  por tiempo), filtrada a la prueba en `level1_mmskin_recalc.json` (1 107 imágenes, 1 022 pares).

Verificado el 25/10: las 1 107 imágenes de Mini-VLM están todas dentro de las 1 650 de LLaVA-Med, así que se puede
comparar sobre los mismos pares sin generar nada.

## Experimento

`scripts/level1_mmskin_pareado.py` (nuevo, local, CPU): toma las imágenes de la partición de prueba de
`mmskin_splits.json` en que ambos generadores tienen reporte no vacío después de quitar `<think>` y referencia real
(sin «nan»), y calcula las cinco métricas de `evaluate_generation` con la misma referencia para los dos. Para BERTScore
agrega el IC del 95 % por *bootstrap* pareado (2 000 remuestreos, semilla 42) de la diferencia Mini − LLaVA, sobre los
F1 por par. Salida `outputs/results/level1_test/mmskin_test/level1_pareado_mini_v2_llava_v2.json` (no existe; el
script no sobrescribe).

## Hipótesis y veredicto

- H1: sobre los mismos pares, el BERTScore de Mini-VLM sigue por encima del de LLaVA-Med (0.713 frente a 0.669 sin
  parear). CUMPLE si n ≥ 1 000 y el IC de la diferencia excluye el cero; si no, el texto dice que no se distinguen.

## Sincronización con clústeres

No aplica: todo es local sobre reportes ya bajados. No se sube nada a Mendieta ni a TOKO.
