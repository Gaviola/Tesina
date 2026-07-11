# Resultado — Taxonomía de errores (P0.5)

**Fecha:** 2026-07-05 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P0.5) · **Sin jobs SLURM** (local).
**Feedback:** #14 — sistematizar el análisis de errores en una taxonomía + frecuencias (posible aporte metodológico).

## Diseño
- Cada reporte (report-only, `<think>` eliminado) se clasifica en su **error principal** con reglas
  determinísticas, por modelo × condición de grounding.
- **Categorías (prioridad):** repeticion · contradiccion (≥2 dx nombrados: diferencial/conflicto) ·
  dx_incorrecto (no menciona el dx correcto pero sí otro) · hedging (lenguaje de incertidumbre) ·
  insuficiente (muy corto / sin morfología) · otros · **ok** (menciona el dx correcto, sin banderas).
- La **alucinación** clínica no se detecta por reglas de forma fiable → se omite como categoría propia.
- **Código:** `scripts/error_taxonomy.py` (usa el diccionario de `src/evaluation/clinical_ner.py`).
  **Salida:** `outputs/results/error_taxonomy/` (summary JSON + `error_taxonomy.png`, barras apiladas).

## Resultados (fracción de reportes)

**LLaVA-Med:**
| categoría | baseline | DermLIP | Swin | oracle |
|-----------|:-:|:-:|:-:|:-:|
| ok | 0.00 | 0.17 | 0.35 | **0.45** |
| hedging | 0.27 | 0.08 | 0.16 | 0.20 |
| dx_incorrecto | 0.09 | **0.48** | 0.10 | **0.00** |
| contradiccion | 0.62 | 0.12 | 0.22 | 0.21 |
| repeticion | 0.01 | 0.01 | 0.00 | 0.00 |
| insuficiente | 0.01 | 0.01 | 0.01 | 0.01 |
| otros | 0.00 | 0.13 | 0.14 | 0.12 |

**Mini-VLM:**
| categoría | baseline | DermLIP | Swin | oracle |
|-----------|:-:|:-:|:-:|:-:|
| ok | 0.00 | 0.16 | 0.38 | **0.45** |
| hedging | 0.40 | 0.16 | 0.35 | **0.43** |
| dx_incorrecto | 0.30 | **0.60** | 0.17 | **0.00** |
| contradiccion | 0.18 | 0.07 | 0.09 | 0.11 |
| repeticion | 0.03 | 0.01 | 0.01 | 0.01 |
| insuficiente | 0.07 | 0.00 | 0.00 | 0.00 |

## Análisis (responde las preguntas abiertas del tutor)
1. **Qué elimina el grounding bueno:** `dx_incorrecto` cae a **0.00** con el oracle (de 0.09/0.30) y
   `contradiccion` (diferencial no comprometido) baja fuerte en LLaVA (0.62→0.21). El `ok` (reporte
   limpio y comprometido) **crece monótonamente** con la calidad del clasificador (0.00 → 0.45).
2. **Qué INTRODUCE el grounding malo (propagación de error, cuantificada):** con un clasificador débil
   (DermLIP 0.38), `dx_incorrecto` **se dispara** — LLaVA 0.09→**0.48**, Mini 0.30→**0.60**. Un mal
   clasificador no solo no ayuda: mete diagnósticos equivocados que el generador adopta. Es el hallazgo
   "clasificador débil puede empeorar", ahora a nivel de tipo de error.
3. **Qué PERSISTE aun con clasificador perfecto:** el `hedging` no desaparece con el oracle (Mini 0.43,
   LLaVA 0.20). Aun cuando se le entrega el dx correcto, el modelo sigue usando lenguaje de incertidumbre
   ("consistent with", "appears to be"). Es el error residual que el grounding no resuelve → límite del
   enfoque y motivación para el prompt *noreasoning* / futuros ajustes.
4. **repeticion e insuficiente** son marginales (1–7% en baseline → ~0 con grounding).

## Cautelas
- Reglas heurísticas y determinísticas (reproducibles, pero aproximadas). `contradiccion` = "≥2
  diagnósticos nombrados" (proxy de diferencial/contradicción, no distingue ambos). Alucinación no
  detectada por separado. Report-only (400 imgs × 4 condiciones × 2 modelos).

## Conclusión (veredicto)
**CUMPLE.** La taxonomía convierte el análisis cualitativo de errores en un resultado cuantitativo y
estructurado: el grounding bueno elimina dx_incorrecto y contradicción, el grounding malo propaga
dx_incorrecto, y el hedging persiste aun con dx perfecto. Es un aporte metodológico (la literatura suele
quedarse en métricas automáticas). Se integra a `experimentacion.tex` (figura + tabla + discusión de
errores en la sección de ensamble).
