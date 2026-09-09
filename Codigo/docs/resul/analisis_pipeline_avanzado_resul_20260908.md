# Resultado — Caracterización del pipeline avanzado (taxonomía de errores + ruteo por clase)

**Fecha:** 2026-09-08 · **Plan:** [analisis_pipeline_avanzado_plan](../ideas/analisis_pipeline_avanzado_plan_20260908.md)
· **Cómputo:** local, sin cluster · **Script:** `scripts/uncertainty_analysis.py` ·
**Salida:** `outputs/results/uncertainty_analysis.json`

## Motivación

El ensamble consciente de la incertidumbre estaba caracterizado solo por la *diagnostic consistency*
agregada (0.822 → 0.940), mientras que el pipeline en cascada simple sí tenía taxonomía de errores y
análisis por clase. Se cierra esa asimetría y se responde si el ruteo es efectivamente **más seguro**.

## Ajuste metodológico

`error_taxonomy.classify_error` clasifica como `contradiccion` cualquier reporte que mencione ≥2 clases.
El reporte **diferencial menciona dos candidatos por diseño**, así que aplicarle esa regla lo penalizaría
incorrectamente. Para el nivel diferencial se usa una regla adaptada: si el gt está entre las clases
mencionadas → `ok_diferencial`; si no está → `dx_incorrecto`. `repeticion` e `insuficiente` se mantienen.

## A) Taxonomía de errores (1445 imágenes no derivadas, pareadas)

| Categoría | Grounding simple | Pipeline avanzado |
|---|---|---|
| ok | 555 (38.4 %) | 498 (34.5 %) |
| ok_diferencial | — | 240 (16.6 %) |
| hedging | 491 (34.0 %) | 436 (30.2 %) |
| **dx_incorrecto** | **275 (19.0 %)** | **95 (6.6 %)** |
| contradicción | 120 (8.3 %) | 114 (7.9 %) |
| repetición | 4 (0.3 %) | 62 (4.3 %) |

**Sobre las 58 abstenidas:** bajo *grounding* simple habrían producido 26 reportes con `dx_incorrecto`
(45 % de ese subconjunto). Al derivarlas, el sistema avanzado **no emite reporte** y esos 26 errores
peligrosos se evitan por completo.

**Cohorte completa (1503):** la tasa de `dx_incorrecto` cae de **20.0 %** (301/1503) a **6.3 %** (95/1503),
una **reducción del 68 % (3.2×)**.

**Contrapartida honesta:** la `repeticion` **empeora** (0.3 % → 4.3 %, 62 casos). Los reportes diferenciales
degeneran más que los afirmativos —enumerar dos candidatos favorece el bucle de texto—. Es el mismo artefacto
ya declarado como limitación, pero el ruteo lo **amplifica**; conviene decirlo explícitamente.

## B) Ruteo por clase diagnóstica (1503)

| Clase | n | Afirmativo | Diferencial | Abstención |
|---|---|---|---|---|
| nevus | 1006 | 818 (81.3 %) | 175 (17.4 %) | 13 (1.3 %) |
| melanoma | 167 | 88 (52.7 %) | 67 (40.1 %) | 12 (7.2 %) |
| benign keratosis | 165 | 96 (58.2 %) | 52 (31.5 %) | 17 (10.3 %) |
| basal cell carcinoma | 77 | 56 (72.7 %) | 17 (22.1 %) | 4 (5.2 %) |
| actinic keratosis | 49 | 27 (55.1 %) | 17 (34.7 %) | 5 (10.2 %) |
| vascular lesion | 22 | 20 (90.9 %) | 1 (4.5 %) | 1 (4.5 %) |
| dermatofibroma | 17 | 6 (35.3 %) | 5 (29.4 %) | 6 (35.3 %) |

**El ruteo es consciente del riesgo, sin haber sido diseñado para serlo.** El sistema afirma con confianza
donde la tarea es fácil y benigna (nevus 81 %, lesión vascular 91 %, ambas de morfología distintiva) y se
vuelve **notablemente más cauto en melanoma**: solo el 52.7 % se afirma, mientras que el 47.3 % restante se
enuncia como diferencial (40.1 %) o se deriva (7.2 %). Es decir, **el sistema no afirma melanoma a ciegas**:
ante duda pone el melanoma sobre la mesa junto al otro candidato o pide criterio humano. Dermatofibroma
—la clase más rara (n=17)— es la de mayor abstención (35.3 %), coherente con su escasez.

## Conclusión (veredicto)

**CUMPLE en ambos criterios.** (1) El ruteo reduce los errores graves: `dx_incorrecto` cae 19.0 % → 6.6 %
sobre las no derivadas y 20.0 % → 6.3 % sobre la cohorte completa (3.2×), con 26 errores peligrosos
adicionales evitados por abstención. (2) El análisis por clase permite una afirmación clínica concreta y
favorable sobre melanoma (52.7 % afirmativo vs 81.3 % en nevus). La contrapartida es el aumento de
repetición (0.3 % → 4.3 %), que debe declararse.

Esto eleva la contribución de "mejora un número agregado" a "reduce específicamente el tipo de error
clínicamente peligroso y modula su cautela según el riesgo de la clase".

## Aplicado al documento

`sec:incertidumbre`: nueva tabla de taxonomía comparada + tabla/párrafo de ruteo por clase, con la
contrapartida de repetición explicitada.

---

## Addendum — ¿Es la repetición mitigable sin regenerar? (2026-09-08)

**Script:** `scripts/repetition_postprocess.py` · **Salida:** `outputs/results/repetition_postprocess.json`

Dado que el ruteo amplifica la repetición (0.3 % → 4.3 % global; **59/334 = 17.7 %** dentro del nivel
diferencial), se probó si el artefacto es recuperable **post-hoc**, sin regenerar: deduplicación de
oraciones repetidas + truncado del bucle final de n-gramas (operaciones conservadoras: solo eliminan
material redundante posterior, nunca agregan texto ni cambian el diagnóstico enunciado).

| Métrica | Antes | Después |
|---|---|---|
| Reportes con repetición | 59 (17.7 %) | 48 (14.4 %) |
| Longitud media | 212 palabras | 208 palabras |
| `ok_diferencial` | 240 | 244 |
| Menciones del gt perdidas por el recorte | — | 2 |
| Reportes que caen en `otros` | 0 | 6 |

**Veredicto: NO CUMPLE — el post-proceso no es una mitigación viable.** Solo recupera **11 de 59**
reportes afectados (19 %), y lo hace a costa de perder 2 menciones del diagnóstico verdadero y degradar
6 reportes a `otros`. La longitud media apenas baja (212 → 208), lo que revela la causa: **la repetición
no es un bucle final recortable sino degeneración pervasiva a lo largo de todo el texto** (baja proporción
de tokens únicos), por lo que ni la deduplicación de oraciones ni el truncado del bucle la resuelven.

**Implicancia:** el artefacto requiere una intervención del lado del **decodificado**
(`repetition_penalty` / `no_repeat_ngram_size`), no limpieza posterior. Esto refuerza —en lugar de
debilitar— la limitación ya declarada, y la vuelve más precisa: no es un detalle cosmético postergable,
sino que necesita regenerar con otros parámetros de decodificación. Nota operativa: esos parámetros
**crashean Mini-VLM** (Phi-3.5-vision: los `input_ids` contienen tokens de imagen fuera del rango de
vocabulario), por lo que la vía practicable es LLaVA-Med.
