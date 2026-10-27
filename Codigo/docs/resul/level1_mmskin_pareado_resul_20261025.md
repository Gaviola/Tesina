# Resultado — Nivel 1 pareado de Mini-VLM v2 y LLaVA-Med v2 en la prueba de MM-Skin

**Fecha:** 2026-10-25 · **Jobs:** ninguno (local, CPU) · **Plan:**
[level1_mmskin_pareado_plan](../ideas/level1_mmskin_pareado_plan_20261025.md)

## Qué se corrió

`scripts/level1_mmskin_pareado.py` (nuevo) sobre los reportes ya bajados de `mini_vlm/v2/mmskin` (corrida sobre el
archivo completo) y `llava_med/v2/mmskin_test`. Pares comunes de la prueba con reporte no vacío sin `<think>` y
referencia real: 1 022 (todos los de Mini-VLM; las 1 107 imágenes de prueba que alcanzó están dentro de las 1 650 de
LLaVA-Med).

```
Codigo/.venv/Scripts/python.exe -X utf8 scripts/level1_mmskin_pareado.py
```

Salida: `outputs/results/level1_test/mmskin_test/level1_pareado_mini_v2_llava_v2.json`.

## Resultados (n = 1 022)

| Generador | BLEU-4 | ROUGE-L | METEOR | CIDEr | BERTScore |
|---|---|---|---|---|---|
| Mini-VLM v2 | 0.002 | 0.057 | 0.112 | 0.009 | 0.713 |
| LLaVA-Med v2 | 0.001 | 0.040 | 0.094 | 0.010 | 0.674 |

BERTScore Mini − LLaVA: +0.039 [+0.038, +0.041] (bootstrap pareado, 2 000 remuestreos, semilla 42).

## Lectura

- Sobre los mismos pares, Mini-VLM supera a LLaVA-Med en BERTScore, ROUGE-L y METEOR; BLEU-4 y CIDEr son casi nulos
  en ambos. LLaVA-Med sobre los 1 022 queda igual que sobre sus 1 414 (BERTScore 0.674 frente a 0.669), así que el
  subconjunto no sesga la comparación.
- Al revés que en SkinCoT, donde LLaVA-Med reproduce las frases de las referencias con que se ajustó.

## Uso en la tesina

`tab:res_gen_nivel1`: la fila de LLaVA-Med en MM-Skin pasa a los 1 022 pares comunes, y 5.1 deja de decir que la
diferencia «no se interpreta».

## Veredicto

H1 **CUMPLE**: n = 1 022 ≥ 1 000 y el IC de la diferencia de BERTScore excluye el cero.
