# Resultado — Cascada con DermLIP oficial como fuente del diagnóstico

**Fecha:** 2026-10-25 · **Jobs:** Mendieta `short` 1183274–1183301 (28 tramos, todos `COMPLETED`, 30–43 min cada uno)
· **Plan:** [cascada_dermlip_oficial_plan](../ideas/cascada_dermlip_oficial_plan_20261024.md)

## Qué se corrió

Brazo `full_dermlip_oficial` (diagnóstico de `outputs/full_dx_dermlip_oficial.csv`, DermLIP zero-shot con el
protocolo oficial, exactitud 0.716 en la prueba) para los tres generadores, con los argumentos de `full_swin_les`.
Reportes bajados por `tar` sobre ssh a `outputs/generated_reports/<modelo>/full_dermlip_oficial/` (1 503 por
generador; CSV local y remoto con el mismo md5). Métrica oficial (solo el reporte, matcher estricto) e IC por
bootstrap pareado (2 000, semilla 42) con `scripts/cascada_dermlip_oficial.py` (nuevo) →
`outputs/results/cascada_dermlip_oficial_<modelo>.json`.

```
Codigo/.venv/Scripts/python.exe scripts/cascada_dermlip_oficial.py --model mini_vlm   # ídem llava_med, skinvl
```

## Resultados (n = 1 503)

| Generador | Sin anclaje | DermLIP anterior | **DermLIP oficial** | Swin-Tiny | Nombra el dx recibido | Swin − DermLIP oficial | DermLIP oficial − sin anclaje |
|---|---|---|---|---|---|---|---|
| Mini-VLM | 0.163 | 0.391 | **0.717** | 0.849 | 0.999 | +0.132 [+0.107, +0.158] | +0.554 [+0.525, +0.582] |
| LLaVA-Med | 0.582 | 0.340 | **0.641** | 0.745 | 0.849 | +0.104 [+0.081, +0.126] | +0.059 [+0.024, +0.092] |
| SkinVL | 0.001 | 0.377 | **0.716** | 0.846 | 0.999 | +0.130 [+0.106, +0.156] | +0.715 [+0.691, +0.738] |

Consistencia según si DermLIP acierta (1 076 imágenes) o no (427): Mini-VLM 0.999 / 0.005, SkinVL 1.000 / 0.000,
LLaVA-Med 0.872 / 0.059.

## Lectura

- Mini-VLM y SkinVL transcriben el diagnóstico de DermLIP igual que el de Swin-Tiny: la consistencia es la exactitud de
  la fuente (0.716), como con Swin (0.847). La fidelidad del reporte la fija la fuente, ajustada o no.
- LLaVA-Med sigue omitiendo el diagnóstico recibido en ~1 de cada 7 reportes, por eso con DermLIP apenas supera a la
  generación sin anclaje.
- Swin-Tiny supera a DermLIP oficial en ~0.13 con los tres generadores: el *pipeline* ancla en el clasificador ajustado.

## Uso en la tesina

Columna «DermLIP» de `tab:res_gen_cascada`, puntos verdes de `fig:res_gen_cascada` (`figuras_cap5.py`) y dos
párrafos en `sec:res_gen_fuentes` (reemplazan el `\pendiente`).

## Veredicto

**CUMPLE.** Los tres generadores completaron las 1 503 imágenes y la consistencia quedó entre la de `full_dermlip`
anterior y la de `full_swin_les` en los tres (Mini-VLM 0.391 < 0.717 < 0.849; LLaVA-Med 0.340 < 0.641 < 0.745;
SkinVL 0.377 < 0.716 < 0.846).
