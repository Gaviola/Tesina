# Plan — Caracterización del pipeline avanzado (taxonomía de errores + análisis por clase)

**Fecha:** 2026-09-08 · **Cómputo:** 100 % local (CPU), sin cluster · **Datos:** ya en disco.

## Motivación

El ensamble consciente de la incertidumbre (ruteo de 3 niveles) es la contribución más fuerte del trabajo,
pero está caracterizado solo por un número agregado (*diagnostic consistency* 0.822 → 0.940). El pipeline
en cascada "normal" sí recibió taxonomía de errores y análisis por clase. Esa asimetría es la objeción
natural de un evaluador. Además, la afirmación de que el ruteo es **más seguro** hoy se apoya en la
consistencia, no en la distribución de **tipos de error** —que es el criterio clínico (C2 de la rúbrica:
"afirmaciones peligrosas").

## Preguntas

1. ¿El ruteo reduce los errores **graves** (`dx_incorrecto`) respecto del *grounding* simple forzado?
2. ¿Qué clases caen en cada nivel? En particular: ¿el sistema **abstiene o da diferencial en melanoma**
   (deseable si hay duda real) o lo afirma a ciegas?

## Diseño

- **Datos:** `outputs/uncertainty/uncertainty_3tier.csv` (1503 imágenes con su nivel),
  `outputs/generated_reports/mini_vlm/full_swin` (grounding simple, 1503) y `.../full_differential`
  (reportes diferenciales, 334). Etiquetas de `data/raw/HAM10000`.
- **Sistema avanzado (reconstruido):** nivel afirmativo → reporte de `full_swin`; nivel diferencial →
  reporte de `full_differential`; nivel abstención → **sin reporte** (derivado).
- **Taxonomía consciente del nivel (ajuste metodológico necesario):** `classify_error` marca
  "contradicción" cuando el texto menciona ≥2 clases, pero el reporte diferencial **menciona 2 candidatos
  por diseño**. Para el nivel diferencial se reclasifica: si menciona los candidatos ruteados y el gt está
  entre ellos → `ok_diferencial` (comportamiento correcto); si el gt no está → `dx_incorrecto`. Las
  categorías `repeticion` e `insuficiente` se mantienen. Esto se explicita en el resul y en el documento.
- **Comparación pareada** sobre las mismas 1445 imágenes no derivadas, más el tratamiento aparte de las 58
  abstenidas (bajo el sistema avanzado no generan reporte → sus errores potenciales se evitan).

## Criterios de éxito

- **Cumple** si la tasa de `dx_incorrecto` del pipeline avanzado es **menor** que la del *grounding* simple
  sobre las mismas imágenes (y menor aún si se cuentan las abstenidas como errores evitados).
- El análisis por clase **cumple** si permite afirmar algo concreto sobre melanoma (p. ej. que el ruteo no
  afirma melanoma a ciegas), sea a favor o en contra.

## Salidas

- `outputs/results/uncertainty_analysis.json` + tablas para el `.tex`.
- `docs/resul/analisis_pipeline_avanzado_resul_20260908.md` con veredicto binario.

## Sincronización con clústeres

**No aplica:** todo el análisis es local sobre reportes y CSV ya descargados. No requiere `sync_up`,
`sync_down` ni jobs SLURM. No se genera texto nuevo (no hay inferencia de VLM).
