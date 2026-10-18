# Ficha 3.4 — Criterios de evaluación y líneas base

**Revisión del autor (18/10/2026), ya aplicada en el `.tex`:** Ahora es 3.3. Sin fechas. Cada métrica con su justificación: F1 ponderado para la época por estabilidad con DF y VASC chicos en validación; F1 macro entre configuraciones; especificidad ≥ 0.85 como decisión de diseño (tope de 15 % de falsas alarmas en validación). Las decisiones tomadas con la prueba a la vista se declaran una sola vez acá. «Líneas base» explica qué es una línea base y una cota. Recibe de la antigua 3.9 la comparación estadística (`sec:met_estadistica`, `tab:met_pruebas` simplificada).

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/04-criterios-evaluacion.tex` (sale de la primera subsección de `07-protocolo-evaluacion.tex`). Labels: `sec:met_protocolo` (la sección), `sec:met_seleccion` (3.4.1). Labels nuevos propuestos: `sec:met_lineas_base` (3.4.2) y `sec:met_eval_generacion` (3.4.3).

Esta sección no presenta ningún desempeño de clasificadores, VLM, *pipeline* ni generación. El único valor numérico que aparece es el del clasificador trivial, que es propiedad de los datos (test: 1006 imágenes de NV sobre 1503).

## Hilo conductor

Pregunta que responde la sección: ¿con qué números se elige cada modelo, contra qué se compara y qué se presenta como resultado, sin que el test intervenga en ninguna elección?

Viene de: 3.3 deja las siete categorías de HAM10000 con su gravedad, el desbalance (NV reúne el 67 % del conjunto), la partición disjunta por lesión (validación de 1289 imágenes y test de 1503, idéntico al original) y la remisión a esta sección para saber con qué métricas se juzga el clasificador.
Deja instalado: para 3.5, la métrica de selección, el criterio del *checkpoint* y la métrica de resultado; para 3.6 a 3.8, las líneas base y cotas y la métrica oficial de generación; para 3.9, la distinción entre lo que decide y lo que solo se reporta.

```
P1  Costos asimétricos de las confusiones (prosa ya escrita, sin cambios)           función: justifica
    ↓ necesidad — una medida que pese a todas las clases por igual exige una definición que el lector pueda seguir
P2  Sensibilidad macro como resultado principal: corrige la exactitud, que con NV al 67 % es engañosa   función: justifica
    ↓ limitación — no ve los falsos positivos: la maximiza un modelo que sobre-predice las clases raras
P3  F1 macro como complemento y como métrica de selección; no se usa el F1 ponderado, dominado por NV   función: justifica
    ↓ consecuencia — la métrica que se presenta no es la que elige: cada una responde una pregunta distinta
P4  Dos niveles de selección: el checkpoint de cada corrida por F1 ponderado en validación, y la corrida ganadora del barrido por F1 macro en validación   función: define · justifica
    ↓ necesidad — el criterio se fija antes de mirar el resultado de cualquier configuración
P5  Ninguna elección usa el test; el resultado principal es la media ± desvío de tres semillas del ganador   función: limita
    ↓ necesidad — el umbral de melanoma también se fija en validación, antes de aplicarlo al test
P6  Umbral de detección de melanoma: especificidad ≥ 0.85 fijada en validación   función: justifica
    ↓ contraste — la clasificación dice qué clase es; las líneas base dicen contra qué se compara el resultado
P7  Líneas base y cotas (3.4.2): azar, clasificador trivial, clasificadores supervisados, oráculo y línea base sin generador   función: define
    ↓ necesidad — la clasificación no alcanza para la generación: un texto también se evalúa por lo que afirma
P8  Métricas de generación en dos niveles (3.4.3): Nivel 1 con referencia, Nivel 2 sin referencia   función: define · limita
    ↓ ampliación — de las métricas del Nivel 2, la consistencia diagnóstica es la oficial
P9  Métrica oficial: solo el reporte, sin razonamiento, con *matcher* estricto   función: define
    ↓ limitación — que el diagnóstico aparezca en el texto no garantiza que el texto sea correcto
P10 Fidelidad diagnóstica no es validez clínica   función: limita
→ Transición a la sección siguiente: «Con estos criterios se entrenan y comparan los clasificadores supervisados (Sección~\ref{sec:met_supervisados}).»
```

Se definen acá (y no se vuelven a definir): criterio de selección en dos niveles; umbral de melanoma; líneas base y cotas como procedimientos (azar, clasificador trivial, oráculo, línea base sin generador); regla del Nivel 1 y del Nivel 2 como métricas del trabajo; matcher estricto; desvío de tres semillas.
Se retoman de antes (solo se nombran, con `\ref`): sensibilidad macro, F1 macro, F1 ponderado, exactitud, sensibilidad y especificidad, AUC y matriz de confusión (`sec:marco_eval_clasif`); BLEU-4, ROUGE-L, METEOR, CIDEr, BERTScore, cobertura de entidades clínicas y consistencia diagnóstica (`sec:marco_eval_texto`); línea base (`sec:marco_vision`, cierre de 2.2); fuga de información y partición (`sec:marco_regularizacion`, 2.1); alucinación (`sec:marco_rep_fallas`).
Extensión: 10 párrafos, unas 3 páginas, repartidas en tres subsecciones.

## Subsecciones

- **3.4.1 Métricas de decisión y criterio de selección** (`sec:met_seleccion`): P1 a P6. Costos de las confusiones, sensibilidad macro y F1 macro, los dos niveles de selección, el test fuera de las decisiones y el umbral de melanoma.
- **3.4.2 Líneas base y cotas** (`sec:met_lineas_base`): P7. Cada línea base se define como un procedimiento y se dice qué pregunta responde.
- **3.4.3 Evaluación de la generación** (`sec:met_eval_generacion`): P8 a P10. Los dos niveles, la métrica oficial y la distinción entre fidelidad y validez clínica.

Sin títulos de párrafo (guía §3). Los dos labels nuevos no están en la tabla de labels que no pueden cambiar, así que se pueden fijar al escribir.

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Las confusiones tienen costo distinto (MEL por NV retrasa la extirpación; NV por MEL extirpa una lesión benigna); por eso se mide por clase y se pesa cada clase igual. Prosa conservada. | Ningún número nuevo en P1. NV en HAM10000: 6705 de 10015 = 66.9 % (`M\Codigo\data\raw\HAM10000\HAM10000_metadata`, columna `dx`). | `tschandl2018ham10000`, `nci2026melanoma` (ya en la prosa) |
| P2 | La sensibilidad macro es el resultado principal: promedio de la sensibilidad por clase, sin ponderar. La exactitud engaña con NV al 67 %: el trivial que responde siempre NV tiene exactitud 0.669 y no reconoce ningún melanoma. Mide directamente las clases minoritarias. | Trivial sobre el test: exactitud 0.669 (1006 / 1503); sensibilidad macro 1/7 = 0.143. Verificado con `y_true` de `M\Codigo\outputs\results\swin_tiny_sweep_t06_les_cwnone_predictions.json` (1503 imágenes: MEL 167, NV 1006, BCC 77, AKIEC 49, BKL 165, DF 17, VASC 22). | `sokolova2009systematic` (promedio por clase); `brodersen2010balanced` (exactitud balanceada, binaria). Definiciones en `sec:marco_eval_clasif`. |
| P3 | El F1 macro es el complemento y la métrica de selección: pondera las clases por igual y penaliza falsos positivos. El F1 ponderado queda dominado por NV. Se reportan juntas; cuando divergen, la diferencia es el intercambio entre detectar y sobre-alertar. | Trivial: F1 ponderado 0.537, F1 macro 0.115 (cálculo verificado con los mismos `y_true`). Razón de la elección: `Codigo\docs\ideas\criterio_seleccion_plan_20260917.md` (sección «Decisión»); `Codigo\docs\resul\split_lesion_resul_20260926.md` §4. | Definición en `eq:marco_f1` (`sec:marco_eval_clasif`). |
| P4 | Dos niveles, con métricas distintas. Dentro de cada corrida, el *checkpoint* es la época con mayor F1 ponderado en validación. Entre corridas, el ganador del barrido es el de mayor F1 macro en validación, entre 30 candidatos por modelo (15 *trials* × 2 pesos por clase). | `src/training/trainer.py:188` (`val_f1` ponderado); `scripts/train_classifier.py:386-387` (`EarlyStopping` y `CheckpointCallback` con `monitor="val_f1"`, `mode="max"`); `configs/phase1_classification.yaml:8` (`monitor: val_f1`); `scripts/lesion_split_report.py:95-98` (ranking por `val.f1_macro`). | — |
| P5 | Ninguna elección usa el test. El test se evalúa para todo el barrido (así lo registra el JSON), pero no decide nada. El resultado principal es la media ± desvío de las semillas 42, 43 y 44 del ganador de cada modelo. El desvío es el muestral. | `scripts/lesion_split_report.py:67, 165` (`ddof=1`); `scripts/train_classifier.py:476` (`--eval-best-checkpoint`); `split_lesion_resul_20260926.md` §2 (semillas 42/43/44). | — |
| P6 | Detección de melanoma = clasificación binaria melanoma frente al resto (sin localización). Umbral: el que en validación maximiza la sensibilidad con especificidad ≥ 0.85. Se aplica sin cambios a test, para el ganador de cada modelo y para el ensamble (media de probabilidades). Con el argmax se pierde una fracción grande de melanomas; el umbral desplaza el punto de operación hacia la sensibilidad y acepta más falsos positivos. | `scripts/melanoma_detection.py:59-65` (`_thr_at_spec`) y `:101` (umbral fijado en val); `scripts/lesion_split_report.py` (punto 4 del docstring); `split_lesion_resul_20260926.md` §7. Ensamble = media de probabilidades: `scripts/melanoma_detection.py:154`. | — |
| P7 | Líneas base y cotas, cada una como procedimiento: (a) azar: 1/7 de sensibilidad macro; (b) clasificador trivial: siempre NV, valores de P2–P3; (c) clasificadores supervisados de 3.5 como referencia de los VLM (la línea base de 2.2); (d) oráculo: el generador recibe el diagnóstico verdadero, cota superior de la consistencia de la cascada; (e) línea base sin generador: el nivel afirmativo presenta el diagnóstico de Swin y el diferencial el par {top-1 de Swin, voto kNN}, sin generador. Mide cuánto aporta el generador al ruteo. | (e): `scripts/ensemble_bootstrap.py:207-218` (`mech`, con `cands[i][:1]` para el nivel afirmativo). Definición de la cota: `Codigo\docs\resul\reanclaje_cascada_resul_20261003.md` §2 (`full_oracle`). Lectura de la línea base: `Codigo\docs\resul\revision_experimentacion_20261003.md` §2.1 y §5. Sin valores de desempeño en esta sección. | `sec:marco_vision` (línea base, cierre de 2.2). |
| P8 | Dos niveles de generación. Nivel 1, con referencia (BLEU-4, ROUGE-L, METEOR, CIDEr, BERTScore F1): solo sirve para MM-Skin y SkinCoT, que tienen texto de referencia y no para HAM10000. Esas referencias no son de especialistas: las de MM-Skin vienen de libros de texto y las de SkinCoT las genera un *pipeline* de modelos de lenguaje que luego certifican dermatólogos. Nivel 2, sin referencia: cobertura de entidades clínicas (*clinical entity recall*), que mide riqueza y no pertinencia, y consistencia diagnóstica (*diagnostic consistency*), que mide fidelidad diagnóstica automática. La consistencia es la métrica más importante de generación. | `src/evaluation/generation.py` (Nivel 1); `src/evaluation/clinical_ner.py:187` (`_compute_entity_recall`) y `:213` (`diagnostic_consistency_flags`); `Docs\experimentacion\experimentacion.tex` l. 242–292 (argumento, números viejos). Origen de las referencias: experimentacion.tex (a verificar en los artículos de los conjuntos). | `shen2025skincare` (SkinCaRe, que contiene SkinCoT); `zeng2025mmskin` (MM-Skin). Ambas existen en el `.bib`; verificar que describen el origen de las referencias. |
| P9 | La métrica oficial de generación es la consistencia diagnóstica medida solo sobre el reporte: los bloques de razonamiento (`<think>…</think>`) se descartan, porque el clínico lee el reporte. Se usa un *matcher* estricto: términos distintivos por clase, con límite de palabra y sin coincidencias por subcadena. Un *matcher* por subcadena acreditaba diagnósticos que el texto no nombraba («mel» dentro de «melanocytic», «keratosis» dentro de «actinic keratosis»). La misma regla gobierna la taxonomía de errores. | `src/evaluation/clinical_ner.py:196-236` (`CLASS_TERMS`, `CLASS_RE`, `strict=True`); `scripts/ensemble_bootstrap.py:48, 81` (`THINK_RE`, `--report_only`); `Codigo\docs\resul\revision_experimentacion_20261003.md` §2.2, §2.3 y §5.1 (decisión del autor del 2026-10-03). | — |
| P10 | Fidelidad diagnóstica no es validez clínica. La consistencia comprueba que el diagnóstico verdadero, o un sinónimo, aparece en el texto. No comprueba que la descripción morfológica sea correcta, que no haya afirmaciones falsas junto al diagnóstico ni que el texto sea útil o seguro. Ambas métricas de nivel 2 son *proxies*. Por eso ningún resultado se presenta como evidencia de validez clínica. | `Docs\experimentacion\experimentacion.tex` l. 280–292 («Fidelidad diagnóstica no es validez clínica»). | `hartsock2024vision` (alucinación, ya citada en 2.6). |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Tabla 3.x (`tab:met_roles`), al cierre de 3.4.1 o 3.4.3 | Para cada métrica, su rol en el trabajo: decide (selección, umbral), resultado principal, complemento, o solo se reporta. Columna «se define en» con el label del Cap. 2. Filas: sensibilidad macro, F1 macro, F1 ponderado (solo checkpoint), exactitud (solo como referencia del trivial), sensibilidad y especificidad de melanoma (umbral), AUC de melanoma (reporta), cobertura de entidades, consistencia diagnóstica (oficial), Nivel 1 (solo MM-Skin y SkinCoT), calibración, McNemar y Wilcoxon, HIBA (3.9) | Esta ficha; labels de `Chapters/02-Marco-Teorico/08-evaluacion.tex` | a generar |

No hay figuras nuevas en esta sección.

## Prosa ya escrita que se conserva

- `Chapters/03-Materiales-Metodos/07-protocolo-evaluacion.tex`, líneas 7–11 (costos asimétricos): se conserva sin cambios y pasa a ser P1 de 3.4.1. Su cita a `nci2026melanoma` existe en el `.bib`.
- `07-protocolo-evaluacion.tex`, líneas 20–30 (dentro del `\pendiente`): el argumento de por qué la sensibilidad macro no decide y el F1 macro sí. Se reescribe como P2 a P4 con las cifras del trivial y la distinción entre los dos niveles, pero sus frases sirven como base. Hay que quitar la expresión «el criterio se aplica también al checkpoint», que el plan del 17/09 ya marcó como inexacta.
- `07-protocolo-evaluacion.tex`, líneas 13–18 (lista de contenidos dentro del `\pendiente`): se reemplaza por la prosa de P5 a P10.

## Lo que va al apéndice

- Ranking completo de los 30 candidatos por modelo en validación (F1 macro, sensibilidad macro, peso por clase), a continuación de las grillas de hiperparámetros: `ap:hiperparametros` (Apéndice A), si el autor lo acepta.
- Lista de términos del *matcher* estricto (`CLASS_TERMS`): Apéndice A o B, según la preferencia del autor. En el cuerpo queda solo la regla.

## Lo que NO va en esta sección (y dónde está)

- Ningún desempeño de clasificadores, VLM, ruteo, *pipeline* ni generación. Esos valores van a los Caps. 4 y 5.
- Calibración (ECE, Brier, *temperature scaling*, *vector scaling*), *bootstrap* pareado, McNemar, Wilcoxon, HIBA, perturbaciones y Grad-CAM: van a 3.9 (`sec:met_complementarios`).
- Definiciones y fórmulas de las métricas: Cap. 2, `sec:marco_evaluacion`, `sec:marco_eval_texto`, `sec:marco_eval_calib`, `sec:marco_eval_estadistica`.
- El concepto de línea base: Cap. 2, `sec:marco_vision`. Aquí solo cómo se implementa cada una.
- Receta de entrenamiento, barrido, pesos por clase y sus valores: 3.5 (`sec:met_supervisados`).
- Selección del *checkpoint* del generador: `src/training/two_stage.py` (líneas 1176 y 1276) usa `val_loss` con `mode="min"`, no `val_f1`. Va a 3.7 (`sec:met_generacion`), no acá.
- Ruteo de tres niveles, umbrales de incertidumbre y taxonomía de errores: 3.8.
- Cuantificación de la fuga de información (36 % del test con lesión en entrenamiento): 3.3 (`sec:met_particiones`).

## Preguntas abiertas para el autor

1. **«El test no interviene en ninguna decisión» necesita una aclaración.** El cambio del criterio de selección de F1 ponderado a F1 macro (17/09) se justificó con métricas de test, según `Codigo\docs\resul\revision_experimentacion_20261003.md` §2.8. Además, el plan del 17/09 fijaba como criterio de éxito que la sensibilidad macro no empeorara (0.700 ± 0.018), y ConvNeXt pasó a 0.691 ± 0.009. `split_lesion_resul_20260926.md` §4 la declara «cumplida». Propongo que 3.4 diga que la elección final se hizo en validación, y que el cambio de criterio se decidió después de ver el test y se declara con sus cifras. ¿Se acepta esa redacción? La tabla del plan del 17/09 tampoco dice si sus valores son de validación o de test (verificar antes de citarla).
2. **El ranking del barrido usa una sola semilla.** Los 60 candidatos del barrido corren con semilla 42; las semillas 43 y 44 solo se corrieron para los dos ganadores (`lesion_split_report.json`: 60 entradas con `seed` 42, 3 con 43 y 3 con 44). ¿Se declara así en 3.4 o se corren las semillas de todos los candidatos?
3. **Monitor del *checkpoint*.** El F1 ponderado se mantuvo porque cambiarlo obligaba a reentrenar las 60 corridas (plan del 17/09). Es una razón de costo, no de método. ¿Se escribe así en el texto o se busca otra justificación?
4. **Nivel 1 en los Caps. 4 y 5.** En los resultados vigentes (septiembre–octubre de 2026) no aparece. Sí figura en los reportes de mayo (`reportes_resul_v1_20260503.md`, `reportes_resul_v2_20260517.md`), sobre la partición anterior. Si no se reporta, 3.4.3 lo define y dice que no se usa para decidir. ¿Se mantiene la definición?
5. **Calibración.** El `\pendiente` de `07-protocolo-evaluacion.tex` la menciona entre las métricas que se justifican acá, pero en 3.4 no decide nada. Propongo moverla a 3.9, como indica la ficha del capítulo. ¿Se confirma?
6. **Nombres de las métricas del Nivel 2.** El Cap. 2 llama «consistencia diagnóstica» a la métrica y dice que equivale a la «fidelidad diagnóstica», y la guía §4 fija «fidelidad diagnóstica» para el concepto. Propongo usar «consistencia diagnóstica» (*diagnostic consistency*) para la métrica y «cobertura de entidades clínicas» (*clinical entity recall*) para la otra, como en el Cap. 2. La guía §4 no tiene entradas para estos dos términos; si se aprueba, conviene agregarlas allí (no lo toqué).
7. **Desvío con tres semillas.** Con tres valores, el desvío es inestable: el intervalo de confianza del desvío de Swin en sensibilidad macro va de 0.013 a 0.157 (`revision_experimentacion_20261003.md` §2.8). ¿Se incluye una frase en 3.4 que lo diga, o se deja para 3.9?
8. **Oráculo y línea base sin generador.** No están definidos en el Cap. 2 (no encontré «oráculo» ni «oracle» en `Chapters/02-Marco-Teorico`). Esta ficha los define aquí como procedimientos. ¿Se usa «oráculo (*oracle*)»?
9. **Origen de las referencias de Nivel 1.** Lo afirma `experimentacion.tex` (MM-Skin de libros de texto; SkinCoT certificado por dermatólogos). No lo verifiqué en los artículos. Hay que chequearlo antes de escribir P8.
10. **Matcher.** ¿La lista de términos va al apéndice o solo se describe la regla?

## Decisiones tomadas por cuenta propia

- **D1. Tres subsecciones** (3.4.1 con `sec:met_seleccion`, 3.4.2 y 3.4.3 con labels nuevos). Así la sección se lee como criterio, después líneas base y después generación, y 3.5 encuentra el criterio antes de usarlo.
- **D2. El clasificador trivial es el único valor numérico**, porque es propiedad de los datos y no de un modelo. Verificado con el test de 1503 imágenes; los valores coinciden con los de `experimentacion.tex` porque el test es el mismo (`revision_experimentacion_20261003.md` §1).
- **D3. El umbral de melanoma** se define como «el que en validación maximiza la sensibilidad con especificidad ≥ 0.85», que es lo que hace `_thr_at_spec`. El ensamble usa la media de probabilidades.
- **D4. El desvío es muestral** (`ddof=1`), como en `lesion_split_report.py`.
- **D5. Calibración, pruebas estadísticas y HIBA salen de 3.4** y van a 3.9. Para la calibración se pide confirmación (pregunta 5); las pruebas y HIBA no tienen pregunta porque no decidían nada en 3.4.
- **D6. La métrica oficial de generación** es la consistencia diagnóstica solo sobre el reporte, con matcher estricto, según la decisión del autor del 2026-10-03 (`revision_experimentacion_20261003.md` §5.1). Los valores de la cascada no se citan en 3.4.
- **D7. Tomo de la tesina de ejemplo** la forma de justificar las métricas a partir del problema (Maglione, pp. 58–59) y la línea base como modelo sencillo que sirve de referencia para comparar (p. 55). No tomo su estilo de títulos de párrafo ni la ecuación de la línea base.
- **D8. Oráculo y línea base sin generador se definen como procedimientos**, sin valores (ver pregunta 8).
