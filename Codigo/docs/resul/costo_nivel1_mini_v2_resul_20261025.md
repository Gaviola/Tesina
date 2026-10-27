# Resultado — Nivel 1 de Mini-VLM v2 en SkinCoT y memoria medida de los generadores

**Fecha:** 2026-10-25 · **Jobs:** Mendieta `short` 1183331–1183334 (Nivel 1, los cuatro en `TIMEOUT` a la hora),
reanudaciones 1183424–1183427 (`COMPLETED`, ~24 min), memoria 1183335–1183337 (`COMPLETED`) · **Plan:**
[costo_nivel1_mini_v2_plan](../ideas/costo_nivel1_mini_v2_plan_20261024.md)

## Qué se corrió

- Nivel 1: 457/457 reportes de Mini-VLM v2 sobre la prueba de SkinCoT, bajados por `tar` a
  `outputs/generated_reports/mini_vlm/v2/skincot_test/`. Ninguno abre `<think>`. Evaluación local; el `.venv` no tenía
  `rouge-score` ni `bert-score` (están en `requirements.txt`) y se instalaron. Con eso, la reevaluación de v3 reproduce
  sus cifras del 24/10 (BERTScore 0.781).
- Nivel 1 pareado (mismos 349 pares con reporte no vacío en v2, v3 y LLaVA-Med v2): `scripts/level1_pareado.py` (nuevo).
- Memoria: `scripts/measure_vlm_memory.py`, `max_memory_allocated` en GiB al cargar y durante 20 reportes de la cascada.

```
Codigo/.venv/Scripts/python.exe scripts/evaluate_reports.py --model mini_vlm --level 1 --dataset v2/skincot_test --strip-reasoning --output_dir outputs/results/level1_test/skincot_test_mini_v2
Codigo/.venv/Scripts/python.exe scripts/level1_pareado.py
```

La salida va a `level1_test/skincot_test_mini_v2/` para no sobrescribir `level1_test/skincot_test/level1_mini_vlm_results.json` (v3).

## Resultados

Nivel 1 en SkinCoT:

| Generador | Pares | BLEU-4 | ROUGE-L | METEOR | CIDEr | BERTScore |
|---|---|---|---|---|---|---|
| Mini-VLM v2 | 425 | 0.044 | 0.152 | 0.253 | 0.038 | 0.770 |
| LLaVA-Med v2 | 426 | 0.102 | 0.191 | 0.329 | 0.054 | 0.797 |
| *Pareado, n = 349:* v2 / v3 / LLaVA-Med | | 0.044 / 0.065 / 0.102 | 0.152 / 0.145 / 0.191 | 0.254 / 0.235 / 0.330 | 0.038 / 0.040 / 0.053 | 0.770 / 0.781 / 0.797 |

Memoria (A30, bf16):

| Generador | Parámetros | Carga (GiB) | Pico en generación (GiB) |
|---|---|---|---|
| Mini-VLM v2 | 4 152 912 896 | 7.75 | 8.64 |
| LLaVA-Med v2 | 7 600 297 984 | 14.22 | 14.52 |
| SkinVL | 7 566 743 552 | 14.10 | 14.38 |

## Lectura

- Mini-VLM v2 queda por debajo de LLaVA-Med en las cinco métricas de SkinCoT: su modelo de lenguaje no se ajusta y no
  reproduce las frases de las referencias.
- Frente a v3 (control), el parecido cambia poco y en sentidos opuestos (v3 mejor en BLEU-4, CIDEr y BERTScore; v2 en
  ROUGE-L y METEOR); v3 además deja 80/457 reportes vacíos. La configuración principal se mantiene.
- Mini-VLM entra en una GPU de 12 GB también durante la generación; LLaVA-Med y SkinVL la superan ya al cargar.

## Uso en la tesina

Fila nueva en `tab:res_gen_nivel1` y párrafo en `sec:res_gen_nivel1` (reemplaza el `\pendiente`); párrafo del control
en `sec:res_gen_control_mini` con el Nivel 1 pareado; `tab:res_costo_generadores` con parámetros y memoria medidos.

## Veredicto

**CUMPLE.** H1: 425 pares (≥ 420) y BERTScore 0.770 ∈ [0.75, 0.82], sin `<think>`. H2: los tres jobs terminaron, la
carga coincide con la estimación y la generación suma menos de 1 GiB (0.89 / 0.30 / 0.28); Mini-VLM queda en 8.64 GiB,
por debajo de 12 GB.
