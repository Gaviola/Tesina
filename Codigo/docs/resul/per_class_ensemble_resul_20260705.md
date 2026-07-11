# Resultado — Análisis por clase del ensamble (P0.3)

**Fecha:** 2026-07-05 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P0.3) · **Sin jobs SLURM** (local).
**Feedback:** #12 — "MiniVLM mejora con grounding, ¿en qué clases?".

## Diseño
- Diagnostic Consistency y Clinical Entity Recall **por clase gt** (report-only, `<think>` eliminado),
  por condición de grounding (baseline / DermLIP 0.38 / Swin 0.80 / oracle) y modelo (LLaVA-Med, Mini-VLM).
- **Insumos:** `outputs/generated_reports/{llava_med,mini_vlm}/full_{baseline,dermlip,swin,oracle}/`
  (400 imgs × 4 condiciones × 2 modelos). Métrica NER determinística (diccionario + sinónimos).
- **Código:** `src/evaluation/clinical_ner.py` (`diagnostic_consistency_flags` por-reporte) +
  `scripts/per_class_ensemble.py`. **Salida:** `outputs/results/per_class/` (summary JSON, heatmap PNG,
  `ensemble_consistency_{model}.json` para P0.2).

## Resultados — Diagnostic Consistency por clase (n por celda)

**Mini-VLM:**
| clase | baseline | DermLIP | Swin | oracle |
|-------|:-:|:-:|:-:|:-:|
| melanoma (26) | 0.35 | 0.81 | 0.85 | 1.00 |
| nevus (279) | 0.23 | 0.42 | 0.85 | 1.00 |
| basal cell carcinoma (25) | 0.08 | 0.44 | 0.76 | 1.00 |
| actinic keratosis (12) | 0.00 | 0.58 | 0.83 | 1.00 |
| benign keratosis (43) | 0.07 | 0.67 | 0.77 | 1.00 |
| dermatofibroma (6) | 0.00 | 0.17 | 0.50 | 1.00 |
| vascular lesion (9) | 0.22 | 0.89 | 1.00 | 1.00 |
| **global (400)** | **0.20** | **0.48** | **0.83** | **1.00** |

**LLaVA-Med:**
| clase | baseline | DermLIP | Swin | oracle |
|-------|:-:|:-:|:-:|:-:|
| melanoma (26) | 0.85 | 0.69 | 0.65 | 0.81 |
| nevus (279) | 0.62 | 0.43 | 0.77 | 0.89 |
| basal cell carcinoma (25) | 0.32 | 0.32 | 0.60 | 0.84 |
| actinic keratosis (12) | 0.25 | 0.17 | 0.25 | 0.42 |
| benign keratosis (43) | 0.60 | 0.51 | 0.49 | 0.67 |
| dermatofibroma (6) | 0.00 | 0.17 | 0.50 | 1.00 |
| vascular lesion (9) | 0.67 | 0.78 | 0.89 | 0.89 |
| **global (400)** | **0.59** | **0.45** | **0.70** | **0.84** |

Ver `per_class_consistency_heatmap.png`. (Global coincide con la tabla T4 del documento.)

## Análisis (responde la pregunta del tutor)
1. **El grounding ayuda MÁS en las clases minoritarias donde el modelo sin grounding nunca nombraba el
   dx.** En Mini-VLM: AKIEC 0.00→0.83, BKL 0.07→0.77, BCC 0.08→0.76 (con Swin). El baseline de Mini-VLM
   estaba en ~0 para casi todas menos melanoma → el grounding rescata clase por clase.
2. **Mini-VLM se beneficia de forma casi uniforme** (su baseline era pésimo → mucho margen): con Swin
   todas las clases quedan 0.76–1.00. LLaVA-Med, que ya tenía sesgo a nombrar melanoma/nevus, gana sobre
   todo en las **minoritarias** (BCC 0.32→0.84, DF 0.00→1.00 con oracle).
3. **Un clasificador débil (DermLIP 0.38) DAÑA justo las clases donde el generador ya era bueno:** en
   LLaVA-Med, melanoma 0.85→0.69 y nevus 0.62→0.43 con grounding DermLIP — al inyectar un dx equivocado,
   el modelo se compromete con el error y deja de mencionar el dx correcto. Es la contracara, ahora
   resuelta por clase, del hallazgo "clasificador débil puede empeorar".
4. **Melanoma en LLaVA-Med:** ni el oracle (0.81) supera al baseline (0.85) — LLaVA ya sobre-menciona
   melanoma, así que el grounding no aporta ahí (techo por sesgo previo).
5. *Cautela de n:* dermatofibroma (n=6), vascular (n=9), AKIEC (n=12) tienen pocas muestras en el
   subconjunto de 400; las tendencias son indicativas.

## Cierre de P0.2 (ensamble) — significancia estadística
Con los arrays de consistencia por-reporte (Mini-VLM):
`baseline 0.198 [0.160,0.237] < DermLIP 0.485 [0.437,0.535] < Swin 0.830 [0.790,0.868] < oracle 1.000`.
**McNemar: todos los pares p < 1e-16** → la **propagación monótona** (mejor clasificador → mejor
consistencia) es significativa en **cada** escalón, con IC no solapados. (Guardado en
`outputs/results/statistical_tests_ensemble_{mini,llava}.json`.)

## Conclusión (veredicto)
**CUMPLE.** El análisis por clase responde la pregunta del tutor con datos segregados: el grounding
rescata sobre todo las clases minoritarias colapsadas, Mini-VLM gana uniformemente y un clasificador
débil daña las clases fuertes del generador. Cierra además la parte de ensamble de P0.2 (propagación
significativa). Se integra a `experimentacion.tex` (heatmap + tabla por clase en la sección de ensamble).
