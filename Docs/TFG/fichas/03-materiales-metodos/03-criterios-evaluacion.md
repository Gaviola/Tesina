# Ficha 3.3 — Criterios de evaluación

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Ahora es 3.3 (antes 3.4). Sin fechas. Cada métrica con su justificación: F1 ponderado para la época por estabilidad con DF y VASC chicos en validación; F1 macro entre configuraciones; especificidad ≥ 0.85 como decisión de diseño (tope de 15 % de falsas alarmas en validación). Las decisiones tomadas con la prueba a la vista se declaran una sola vez acá. «Líneas base» explica qué es una línea base y una cota. Recibe de la antigua 3.9 la comparación estadística (`sec:met_estadistica`, `tab:met_pruebas` simplificada).

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita en la revisión del 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/03-criterios-evaluacion.tex` (antes `04-criterios-evaluacion.tex`; sale de la primera subsección de `07-protocolo-evaluacion.tex`). Labels: `sec:met_protocolo` (la sección), `sec:met_seleccion` (3.3.1, «Métricas de clasificación»), `sec:met_lineas_base` (3.3.2), `sec:met_eval_generacion` (3.3.3) y `sec:met_estadistica` (3.3.4, «Comparación estadística», que antes era la subsección de la 3.9). Tablas: `tab:met_roles` (papel de cada métrica) y `tab:met_pruebas` (pruebas estadísticas según la comparación). La sección no tiene párrafo propio antes de la primera subsección.

Esta sección no presenta ningún desempeño de clasificadores, VLM, *pipeline* ni generación. Los únicos valores numéricos que aparecen son los del clasificador trivial, que son propiedad de los datos (test: 1006 imágenes de NV sobre 1503), y los parámetros de las pruebas estadísticas.

## Hilo conductor

Pregunta que responde la sección: ¿con qué números se elige cada modelo, contra qué se compara, qué se presenta como resultado y cómo se decide que una diferencia entre modelos es real, sin que el test intervenga en ninguna elección?

Viene de: 3.2 deja las siete categorías de HAM10000 con el desbalance (NV reúne dos tercios del conjunto, DF y VASC no llegan al 1.5 % cada una), la partición disjunta por lesión con su tabla de tamaños (`tab:met_tamanos`), el rol de cada conjunto y quién escribió los textos de referencia (`tab:met_conjuntos`), y la remisión a esta sección para saber con qué métricas se juzga al clasificador (`sec:met_protocolo`). 3.1 dejó la gravedad desigual de las categorías (`sec:met_tareas`) y las tres tareas (T1 clasificación, T2 detección de melanoma, T3 generación).
Deja instalado: para 3.4, la métrica de selección de la época y de la configuración, el resultado principal y el umbral de melanoma; para 3.5 a 3.7, las líneas base y cotas y la métrica oficial de generación; para 3.8, la distinción entre lo que decide y lo que solo se reporta (`tab:met_roles`); para los Caps. 4 y 5, la prueba que corresponde a cada comparación (`tab:met_pruebas`).

```
3.3.1 Métricas de clasificación (sec:met_seleccion)
P1  Costos asimétricos de las confusiones y NV al 67 %: un buen resultado global puede esconder un mal
    desempeño en las clases que importan; las métricas tienen que mirar cada clase con el mismo peso   función: justifica
    ↓ necesidad — una medida que cumpla esa condición
P2  Sensibilidad macro como resultado principal; la exactitud no cumple la condición (clasificador
    trivial: exactitud 0.669, sensibilidad macro 0.143)                                                función: define · justifica
    ↓ limitación — la sensibilidad macro no castiga los falsos positivos
P3  F1 macro corrige ese sesgo: criterio con que se elige la mejor configuración de cada modelo y se
    reporta junto a la sensibilidad macro; el F1 ponderado queda dominado por NV (trivial: 0.537 frente
    a 0.115 del F1 macro)                                                                              función: justifica
    ↓ consecuencia — hay dos métricas de selección y hay que decir cuál elige qué
P4  Elección en dos niveles: la época por F1 ponderado (estabilidad, con 14 DF y 18 VASC en validación,
    `tab:met_tamanos`) y la configuración por F1 macro; la prueba no interviene en ninguna             función: define · justifica
    ↓ problema — las métricas de clases minoritarias dependen de pocas imágenes y cambian entre ejecuciones
P5  Tres semillas (42, 43 y 44), media ± desvío muestral; el desvío con tres semillas es una estimación
    gruesa y las comparaciones se completan con las pruebas de 3.3.4                                   función: define · limita
    ↓ excepción — «la prueba no interviene» tiene tres matices que hay que declarar
P6  Configuraciones y umbrales se eligen en validación; tres decisiones no son ajenas a la prueba (F1
    macro como criterio, concordancia como señal del ruteo, instrucción del generador elegida en un
    piloto con 17 imágenes de prueba); ninguna elige un modelo ni fija un umbral sobre la prueba       función: limita
    ↓ ampliación — la detección de melanoma (T2) necesita un criterio propio
P7  Umbral de melanoma: mayor sensibilidad con especificidad ≥ 0.85 fijado en validación y aplicado sin
    cambios a la prueba; decisión de diseño (tope de 15 % de falsas alarmas); AUC se informa sin
    intervenir                                                                                         función: define · justifica

3.3.2 Líneas base (sec:met_lineas_base)
    ↓ contraste — las métricas dicen cómo medir; falta decir contra qué se compara
P8  Qué es una línea base (procedimiento más simple, mismo conjunto de prueba, nivel que hay que superar)
    y qué es una cota superior (mejor resultado alcanzable en condiciones ideales)                      función: define · justifica
    ↓ aplicación — cuáles son las referencias del trabajo
P9  Tres niveles para la clasificación: azar (1/7), clasificador trivial (siempre NV) y clasificadores
    supervisados como referencia de los VLM (PI1); las referencias del pipeline (cota con diagnóstico
    verdadero y línea base sin generador) se definen en 3.7 (`sec:met_pipeline`)                       función: define

3.3.3 Evaluación de la generación (sec:met_eval_generacion)
    ↓ contraste — un texto no se evalúa como una clase: hay o no un texto de referencia
P10 Dos niveles según haya o no referencia; Nivel 1 (BLEU-4, ROUGE-L, METEOR, CIDEr, BERTScore) solo
    para MM-Skin y SkinCoT, no decide; esas referencias no son diagnósticos clínicos de la lesión y
    quién las escribió condiciona lo que mide (`tab:met_conjuntos`)                                    función: define · limita
    ↓ ampliación — el Nivel 2 no necesita referencia
P11 Nivel 2 en la prueba de HAM10000: cobertura de entidades clínicas (riqueza, no pertinencia) y
    consistencia diagnóstica (nombra el diagnóstico verdadero o un sinónimo); esta última es la métrica
    principal de generación porque responde la segunda pregunta de investigación (PI2)                  función: define · justifica
    ↓ precisión — cómo se calcula la consistencia diagnóstica
P12 Solo sobre el reporte (se descartan los bloques `<think>`, porque el clínico lee el reporte) y con
    búsqueda estricta por palabra completa (una búsqueda por fragmentos acreditaría «mel» dentro de
    «melanocytic»)                                                                                      función: define · justifica
    ↓ limitación — que el diagnóstico aparezca no garantiza que el texto sea correcto
P13 Fidelidad diagnóstica no es validez clínica; ningún resultado se presenta como evidencia de validez
    clínica; remite a `sec:marco_rep_fallas` y presenta `tab:met_roles`                                función: limita
    → `tab:met_roles` (papel de cada métrica: decide, resultado principal, complemento, solo se informa)

3.3.4 Comparación estadística (sec:met_estadistica)
    ↓ necesidad — las métricas dan un número; falta decidir cuándo una diferencia es real
P14 Una métrica más alta en la prueba no alcanza (con otra muestra el orden podría invertirse); cada
    comparación usa la prueba que corresponde (`tab:met_pruebas`): bootstrap sobre las imágenes (pareado
    entre dos modelos) para cuánto varía una métrica y si la diferencia la excede; McNemar exacto sobre
    los casos discordantes para saber si un modelo acierta lo que el otro falla                       función: define · justifica
    ↓ consecuencia — siete modelos forman 21 pares: hace falta controlar el error por comparaciones múltiples
P15 Holm sobre los valores p de McNemar; en el bootstrap, diferencia real si el IC del 95 % no contiene
    el cero; sensibilidad por clase comparada de forma descriptiva (con siete valores ninguna prueba de
    rangos alcanzaría el umbral de Holm para 21 comparaciones); pruebas sobre la semilla 42 y la variación
    entre semillas como desvío                                                                         función: define · limita
    → `tab:met_pruebas` (comparación, pregunta, prueba, criterio)
→ Transición a la sección siguiente: «Con estos criterios se entrenan y se eligen los clasificadores supervisados de la sección siguiente.»
```

Se definen acá (y no se vuelven a definir): criterio de selección en dos niveles (época y configuración); umbral de melanoma; qué es una línea base y una cota; azar y clasificador trivial como líneas base de clasificación; Nivel 1 y Nivel 2 como métricas del trabajo; consistencia diagnóstica solo sobre el reporte y con búsqueda estricta; media ± desvío muestral de tres semillas; la prueba que corresponde a cada comparación, Holm sobre McNemar y el criterio de IC sin el cero; las tres decisiones tomadas con la prueba a la vista.
Se retoman de antes (solo se nombran, con `\ref`): sensibilidad macro, F1, AUC, sensibilidad y especificidad (`sec:marco_eval_clasif`, `eq:marco_f1`, `eq:marco_auc`); BLEU-4, ROUGE-L, METEOR, CIDEr, BERTScore, cobertura de entidades y consistencia diagnóstica (`sec:marco_eval_texto`); bootstrap, McNemar y Holm (`sec:marco_eval_estadistica`, `eq:marco_holm`); alucinación (`sec:marco_rep_fallas`); calibración (`sec:marco_eval_calib`); gravedad de las categorías (`sec:met_tareas`), distribución de clases (`sec:met_ham`), tamaños de validación (`tab:met_tamanos`) y origen de los textos de referencia (`tab:met_conjuntos`) de 3.1 y 3.2.
Se anuncian y se definen después: cota superior con diagnóstico verdadero y línea base sin generador (3.7, `sec:met_pipeline`); concordancia como señal de ruteo (`sec:met_ruteo`) e instrucción *noreasoning* (`sec:met_cascada`), que acá solo se declaran como decisiones con la prueba a la vista; análisis de calibración (3.8, `sec:met_complementarios`).
Extensión: 15 párrafos más la transición, unas 4–4.5 páginas, repartidas en cuatro subsecciones y dos tablas.

## Subsecciones

- **3.3.1 Métricas de clasificación** (`sec:met_seleccion`): P1 a P7. Costos de las confusiones, sensibilidad macro y F1 macro, los dos niveles de selección, las semillas, las decisiones con la prueba a la vista y el umbral de melanoma.
- **3.3.2 Líneas base** (`sec:met_lineas_base`): P8 y P9. Qué es una línea base y una cota; las referencias de clasificación.
- **3.3.3 Evaluación de la generación** (`sec:met_eval_generacion`): P10 a P13, con `tab:met_roles`. Los dos niveles, la métrica oficial y la distinción entre fidelidad y validez clínica.
- **3.3.4 Comparación estadística** (`sec:met_estadistica`): P14 y P15, con `tab:met_pruebas`. Antes era la subsección de pruebas de la antigua 3.9.

Sin títulos de párrafo (guía §3).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Las confusiones tienen costo distinto (MEL por NV retrasa la extirpación; NV por MEL extirpa una lesión benigna; entre benignas, menos consecuencias). NV reúne dos tercios de HAM10000, así que un buen resultado global puede esconder un mal desempeño en las clases que importan. | Ningún número nuevo (el 67 % queda en «dos tercios»). NV en HAM10000: 6705 de 10015 = 66.9 % (`M\Codigo\data\raw\HAM10000\HAM10000_metadata`, columna `dx`). | `tschandl2018ham10000`, `nci2026melanoma` |
| P2 | Sensibilidad macro = promedio de la sensibilidad de las siete clases sin ponderar: es el resultado principal. La exactitud no cumple la condición: el trivial que responde siempre NV tiene exactitud 0.669 y sensibilidad macro 0.143 (1/7). | Trivial sobre el test: exactitud 0.669 (1006 / 1503); sensibilidad macro 1/7 = 0.143. Verificado con `y_true` de `M\Codigo\outputs\results\swin_tiny_sweep_t06_les_cwnone_predictions.json` (1503 imágenes: MEL 167, NV 1006, BCC 77, AKIEC 49, BKL 165, DF 17, VASC 22). Definición en `sec:marco_eval_clasif`. | (en el Cap. 2: `sokolova2009systematic`, `brodersen2010balanced`; el `.tex` no las cita) |
| P3 | La sensibilidad macro no castiga los falsos positivos: un modelo que asigna muchas imágenes a las clases minoritarias sube su sensibilidad a costa de errores en las demás. El F1 macro combina sensibilidad y precisión por clase y pondera igual; es el criterio con que se elige la mejor configuración de cada modelo y se reporta junto a la sensibilidad macro. Cuando divergen, la diferencia es el intercambio entre detectar y dar falsas alarmas. El F1 ponderado queda dominado por NV. | Trivial: F1 ponderado 0.537, F1 macro 0.115 (cálculo verificado con los mismos `y_true`). Razón de la elección: `Codigo\docs\ideas\criterio_seleccion_plan_20260917.md` (sección «Decisión»); `Codigo\docs\resul\split_lesion_resul_20260926.md` §4. | Definición en `eq:marco_f1` (`sec:marco_eval_clasif`) |
| P4 | Dos niveles. Dentro de cada entrenamiento se guarda la época con mayor F1 ponderado en validación: con 14 imágenes de DF y 18 de VASC (`tab:met_tamanos`) el F1 macro cambia mucho de una época a otra por un par de aciertos, y el F1 ponderado es más estable para decidir cuándo detener. Entre configuraciones se elige la de mayor F1 macro en validación, porque en esa comparación pesan las clases minoritarias. La prueba no interviene en ninguna de las dos. | `src/training/trainer.py:188` (`val_f1` ponderado); `scripts/train_classifier.py:386-387` (`EarlyStopping` y `CheckpointCallback` con `monitor="val_f1"`, `mode="max"`); `configs/phase1_classification.yaml:8` (`monitor: val_f1`); `scripts/lesion_split_report.py:95-98` (ranking por `val.f1_macro`). Tamaños de validación (14 DF, 18 VASC): `tab:met_tamanos` de 3.2. **La justificación por estabilidad es de la revisión del 18/10/2026; el motivo del código era no reentrenar las 60 corridas (ver «Decisiones»).** | — |
| P5 | Las métricas de las clases minoritarias cambian de una ejecución a otra porque dependen de pocas imágenes. Cada modelo elegido se entrena con tres semillas (42, 43 y 44) y el resultado es media ± desvío muestral. Con tres semillas el desvío es una estimación gruesa; las comparaciones entre modelos se completan con las pruebas de 3.3.4. | `scripts/lesion_split_report.py:67, 165` (`ddof=1`); `split_lesion_resul_20260926.md` §2 (semillas 42/43/44). Lo gruesa que es la estimación: `revision_experimentacion_20261003.md` §2.8 (IC del desvío de Swin en sensibilidad macro de 0.013 a 0.157; la cifra ya no está en el texto). | — |
| P6 | Configuraciones y umbrales se eligen en validación; la prueba solo informa. Tres decisiones de diseño no son del todo ajenas a la prueba: el F1 macro como criterio de selección y la concordancia entre predictores como señal del ruteo (`sec:met_ruteo`) se adoptaron con resultados de prueba ya conocidos, y la instrucción con que el generador recibe el diagnóstico (`sec:met_cascada`) se eligió en un piloto que incluía 17 imágenes de prueba. Ninguna elige un modelo ni fija un umbral sobre la prueba; el cambio de criterio no mejoró las cifras de prueba de los modelos elegidos. Se declaran para que se lea con ese antecedente. | `Codigo\docs\resul\revision_experimentacion_20261003.md` §2.8 (el cambio de criterio se justificó con métricas de prueba); `split_lesion_resul_20260926.md` §4 (con el criterio anterior, ConvNeXt t06 tenía sensibilidad macro 0.700 frente a 0.691 de t02: el cambio no la mejoró); piloto de 17 imágenes: ver `07-pipeline.tex` l. 40 y la ficha 3.7. | — |
| P7 | Detección de melanoma (T2): con el argmax el costo de perder un melanoma no interviene. El umbral sobre la probabilidad de melanoma se fija en validación como el de mayor sensibilidad entre los que mantienen especificidad ≥ 0.85, y se aplica sin cambios a la prueba. Decisión de diseño que traduce el costo asimétrico: no perder melanomas, con tope de 15 % de falsas alarmas en validación. El AUC no depende del umbral y se informa sin intervenir. | `scripts/melanoma_detection.py:59-65` (`_thr_at_spec`) y `:101` (umbral fijado en val); `scripts/lesion_split_report.py` (punto 4 del docstring); `split_lesion_resul_20260926.md` §7. | AUC: `eq:marco_auc` |
| P8 | Un resultado aislado no dice si un modelo es bueno. Línea base = procedimiento más simple aplicado al mismo conjunto de prueba, que fija el nivel que hay que superar para que la complejidad se justifique; cota superior = mejor resultado alcanzable en condiciones ideales, que muestra cuánto margen queda. | Ninguno. Concepto de línea base: `sec:marco_vision` (cierre de 2.2); ejemplo: §3.5 de la tesina de ejemplo. | — |
| P9 | Clasificación, tres niveles: azar (1/7 de sensibilidad macro); clasificador trivial (siempre NV, lo que se obtiene del desbalance sin mirar la imagen); clasificadores supervisados de 3.4 como referencia de los VLM (PI1 se responde comparándolos). El *pipeline* tiene su cota superior (recibe el diagnóstico verdadero) y su línea base sin generador, que se definen en 3.7 porque necesitan la cascada y el ruteo. | Definición de la cota: `Codigo\docs\resul\reanclaje_cascada_resul_20261003.md` §2 (`full_oracle`). Línea base sin generador: `scripts/ensemble_bootstrap.py:207-218` (`mech`). Lectura: `revision_experimentacion_20261003.md` §2.1 y §5. Sin valores de desempeño. | — |
| P10 | Dos niveles de generación según haya o no texto de referencia. Nivel 1: BLEU-4, ROUGE-L, METEOR, CIDEr y BERTScore; solo se aplica a MM-Skin y SkinCoT; no decide ninguna elección. Esas referencias no son diagnósticos clínicos de la lesión y quién las escribió condiciona lo que mide la comparación (`tab:met_conjuntos`). | `src/evaluation/generation.py` (Nivel 1). Origen de las referencias: se dice en 3.2 (MM-Skin de libros de texto; SkinCoT generado por un modelo de lenguaje con la etiqueta verdadera y revisado por dermatólogos): `02-datos.tex` l. 159–163 y 180–182. | `sec:marco_eval_texto`; (`shen2025skincare`, `zeng2025mmskin` se citan en 3.2) |
| P11 | Nivel 2, sin referencia, sobre la prueba de HAM10000. Cobertura de entidades clínicas: cuenta cuántos términos clínicos relevantes aparecen, así que mide riqueza y no pertinencia. Consistencia diagnóstica: comprueba si el reporte nombra el diagnóstico verdadero o un sinónimo; es la métrica principal de generación porque responde directamente PI2. | `src/evaluation/clinical_ner.py:187` (`_compute_entity_recall`) y `:213` (`diagnostic_consistency_flags`). | — |
| P12 | La consistencia se calcula solo sobre el reporte: los bloques de razonamiento entre `<think>` se descartan, porque el clínico lee el reporte. Búsqueda estricta por palabra completa de los términos distintivos de cada clase; una búsqueda por fragmentos acreditaría diagnósticos que el texto no nombra («mel» dentro de «melanocytic», «keratosis» dentro de «actinic keratosis»). | `src/evaluation/clinical_ner.py:196-236` (`CLASS_TERMS`, `CLASS_RE`, `strict=True`); `scripts/ensemble_bootstrap.py:48, 81` (`THINK_RE`, `--report_only`); `revision_experimentacion_20261003.md` §2.2, §2.3 y §5.1. | — |
| P13 | La consistencia mide fidelidad diagnóstica, no validez clínica: comprueba que el diagnóstico verdadero aparece, no que la descripción morfológica sea correcta, que no haya afirmaciones falsas junto al diagnóstico ni que el texto sea útil o seguro. Ningún resultado se presenta como evidencia de validez clínica; la alucinación motiva la cautela. Cierra con `tab:met_roles`. | `Docs\experimentacion\experimentacion.tex` l. 280–292 («Fidelidad diagnóstica no es validez clínica»). | `sec:marco_rep_fallas` (`hartsock2024vision` se cita ahí) |
| P14 | Una métrica más alta no basta para afirmar que un modelo es mejor. Cada comparación usa la prueba que corresponde (`tab:met_pruebas`): *bootstrap* sobre las imágenes, pareado entre dos modelos, para cuánto varía una métrica por la composición de la prueba y si la diferencia la excede; McNemar exacto sobre los casos en que los dos modelos discrepan, para saber si uno acierta imágenes en las que el otro falla. | `Codigo\scripts\statistical_tests.py` (`bootstrap_ci`, `paired_bootstrap_diff`, `mcnemar_exact`; `--n_boot` 2000, `--seed` 42); `Codigo\scripts\ensemble_bootstrap.py` (`paired_bootstrap_diff_flags`, `n_boot=2000`). | `sec:marco_eval_estadistica` |
| P15 | Siete modelos forman 21 pares: los valores p de McNemar se corrigen con Holm (controla la probabilidad de declarar al menos una diferencia falsa entre todas). En el *bootstrap*, la diferencia es real si el IC del 95 % no contiene el cero. La sensibilidad por clase se compara de forma descriptiva (contando en cuántas de las siete clases mejora cada modelo): con siete valores, ninguna prueba de rangos alcanzaría el umbral de Holm para 21 comparaciones. Las pruebas se calculan sobre la ejecución con semilla 42; la variación entre semillas se informa como desvío. `tab:met_pruebas`: 2000 remuestreos de las imágenes de prueba, semilla 42; cinco filas (métrica agregada, diferencia de F1 o sensibilidad macro, aciertos por imagen, sensibilidad por clase, consistencia diagnóstica entre variantes del pipeline). | Holm: `Codigo\scripts\densenet_vit_moderna_report.py:35` (`holm`), sobre los 21 pares de `statistical_tests_les_v2.json`. Umbral de Holm para 21 pares: 0.05/21 ≈ 0.0024; p mínimo bilateral de Wilcoxon con N = 7: 0.016 (`split_lesion_resul_20260926.md`; ficha antigua 3.9, pregunta 11). Semilla 42: `split_lesion_resul_20260926.md` §3. | `eq:marco_holm` |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `tab:met_roles`, al cierre de 3.3.3 | Para cada métrica, su papel: resultado principal, decide la elección de época o de configuración, umbral de melanoma, complemento, o solo se informa. Columna «Se define en». Diez filas: sensibilidad macro, F1 macro, F1 ponderado, exactitud, sensibilidad y especificidad de melanoma, AUC de melanoma, Nivel 1, cobertura de entidades, consistencia diagnóstica, calibración (ECE, Brier; remite a `sec:met_complementarios`) | Esta ficha; labels de `Chapters/02-Marco-Teorico/06-evaluacion.tex` | redactada |
| `tab:met_pruebas`, al cierre de 3.3.4 | Cinco filas: comparación, pregunta que responde, prueba, criterio. Versión simplificada de la antigua tabla de la 3.9 (sin columnas de parámetros ni de función de código; sin la fila de Wilcoxon por clase en su forma inferencial) | `scripts/statistical_tests.py`, `scripts/ensemble_bootstrap.py` | redactada |

No hay figuras nuevas en esta sección.

## Lo que va al apéndice

- Ranking completo de los 30 candidatos por modelo en validación (F1 macro, sensibilidad macro, peso por clase), a continuación de las grillas de hiperparámetros: `ap:hiperparametros` (Apéndice A, hoy `\pendiente`), si el autor lo acepta.
- Lista de términos del *matcher* estricto (`CLASS_TERMS`): Apéndice A o B, según la preferencia del autor. En el cuerpo queda solo la regla.
- Comandos de `statistical_tests.py` y `ensemble_bootstrap.py` con sus argumentos y versiones de SciPy: Apéndice E (`ap:reproducibilidad`).

## Lo que NO va en esta sección (y dónde está)

- Ningún desempeño de clasificadores, VLM, ruteo, *pipeline* ni generación. Esos valores van a los Caps. 4 y 5.
- Calibración (ECE, Brier, *temperature scaling*, *vector scaling*), HIBA, perturbaciones, Grad-CAM y costo: 3.8 (`sec:met_complementarios`).
- Definiciones y fórmulas de las métricas y de las pruebas: Cap. 2 (`sec:marco_evaluacion`, `sec:marco_eval_texto`, `sec:marco_eval_calib`, `sec:marco_eval_estadistica`).
- El concepto de línea base: Cap. 2, `sec:marco_vision`. Aquí solo cómo se implementa cada una.
- Receta de entrenamiento, barrido, pesos por clase y ensamble: 3.4 (`sec:met_supervisados`).
- Selección del *checkpoint* del generador: `src/training/two_stage.py` (líneas 1176 y 1276) usa `val_loss` con `mode="min"`, no `val_f1`. Va a 3.6 (`sec:met_generacion`).
- Cota superior, línea base sin generador, ruteo de tres niveles, umbrales de incertidumbre y taxonomía de errores: 3.7 (`sec:met_pipeline`).
- Cuantificación de la fuga de información: 3.2 (`sec:met_particiones`).

## Quitado en la revisión del 18/10/2026

Contenido de la versión anterior de la ficha y del `.tex` que ya no está en el texto. Se conserva acá para no perder las fuentes.

- **Fechas y bitácora del criterio de selección** (cambio de criterio del 17/09, plan del 17/09, decisión del autor del 2026-10-03, «criterio anterior al 17/09»): fuera por R1. Queda la decisión y su justificación; la declaración de que se tomó con la prueba a la vista pasa a P6 (D-C). Fuentes: `criterio_seleccion_plan_20260917.md`, `revision_experimentacion_20261003.md` §2.8 y §5.1.
- **«30 candidatos por modelo (15 *trials* × 2 pesos por clase)»** del antiguo P4: el detalle del barrido pasó a 3.4 (R3, no repetir lo que otra sección presenta). Fuente: `scripts/lesion_split_report.py:95-98`.
- **«El test se evalúa para todo el barrido (así lo registra el JSON)» y el flag `--eval-best-checkpoint`** del antiguo P5: detalle del registro de experimentos, fuera por R1. Fuente: `scripts/train_classifier.py:476`.
- **Ensamble en la detección de melanoma** (umbral aplicado al ensamble, media de probabilidades) del antiguo P6: pasó a 3.4, subsección «Ensamble y detección de melanoma» (R3). Fuente: `scripts/melanoma_detection.py:154`.
- **Fracción de melanomas que se pierde con el argmax**: el texto lo dice sin cifra (R4: la sección no presenta desempeños). Fuente: `split_lesion_resul_20260926.md` §7.
- **Cifra del intervalo de confianza del desvío de Swin (0.013 a 0.157)** del antiguo P5 y de la pregunta 7: queda solo «estimación gruesa» (R1: detalle estadístico que importa al equipo). Fuente: `revision_experimentacion_20261003.md` §2.8.
- **Definición del oráculo y de la línea base sin generador** (antiguo P7 (d) y (e)): salen de esta sección y se definen en 3.7 (R3; ya figuraba en la «Revisión cruzada» del 11/10). Fuentes: `reanclaje_cascada_resul_20261003.md` §2, `ensemble_bootstrap.py:207-218`.
- **Nombre «oráculo (*oracle*)»**: el texto dice «cota superior que recibe el diagnóstico verdadero» (pregunta 8, obsoleta).
- **Fuentes de las referencias del Nivel 1** (libros de texto para MM-Skin; *pipeline* de modelos de lenguaje con certificación de dermatólogos para SkinCoT) y las citas `shen2025skincare` y `zeng2025mmskin`: ya no se dicen en 3.3; el texto remite a `tab:met_conjuntos` de 3.2 (R3). Fuente: `experimentacion.tex` l. 242–292; `02-datos.tex` l. 152–185.
- **`hartsock2024vision`**: ya no se cita en 3.3; el texto remite a `sec:marco_rep_fallas`, donde está citada (R3).
- **`sokolova2009systematic` y `brodersen2010balanced`** (antiguo P2): ya no se citan en 3.3; la definición y sus fuentes están en `sec:marco_eval_clasif` (R3).
- **«Para qué sirve el *matcher* en la taxonomía de errores»** («la misma regla gobierna la taxonomía de errores») del antiguo P9: salió de 3.3; la taxonomía se presenta en 3.7.
- **Fila de Wilcoxon por clase como prueba inferencial** (antigua `tab:met_pruebas` de la 3.9, N = 7, `zero_method="wilcox"`, función `wilcoxon_perclass`): reemplazada por una comparación descriptiva con la razón que da P15 (ver «Decisiones», 3). Pregunta 11 de la ficha antigua 3.9 (N efectiva de Wilcoxon): obsoleta. Fuentes: `statistical_tests.py` (`wilcoxon_perclass`), `statistical_tests_les.json`.
- **Columnas «Parámetros», «Nivel» y «Código» de la antigua `tab:met_pruebas`**, y el p-valor del bootstrap como orientación (`p = 2·min(...)`): tabla simplificada (D-A). El nivel 0.05 de McNemar queda como «$p < 0.05$ corregido».
- **Limitación «el bootstrap remuestrea imágenes, no lesiones»** (1503 imágenes, 1429 lesiones en la prueba): el texto dice «remuestreos de las imágenes de prueba» pero ya no declara que los IC pueden ser optimistas. Queda como pregunta abierta 4. Fuente: `revision_experimentacion_20261003.md` §2.8.
- **Filas de `tab:met_roles`** sobre McNemar, Wilcoxon y HIBA (antigua tabla propuesta): salen; las pruebas pasaron a `tab:met_pruebas` y HIBA a 3.8 (D-A).
- **Tabla de protocolos de inferencia por resultado** (`tab:met_protocolos`, `tab:met_protocolos_vlm`, `tab:met_protocolos_analisis`) y la subsección `sec:met_inferencia`: eliminadas (D-A). Las excepciones de protocolo (corridas legacy en vista única, VLM con partición distinta) las cubre D-B para DenseNet121 y ViT-B/16; las demás, si hacen falta, se declaran en el capítulo que presenta el resultado.
- **«Calibración»**: ya no se discute en esta sección; `tab:met_roles` remite a `sec:met_complementarios` (pregunta 5, resuelta).

## Preguntas abiertas para el autor

1. **(resuelta; el autor debe validar la redacción)** «El test no interviene en ninguna decisión» necesitaba una aclaración. La revisión del 18/10 la hizo en P6: la elección se hace en validación y las tres decisiones tomadas con la prueba a la vista se declaran una sola vez (D-C). Queda por verificar que la tabla del plan del 17/09 (sensibilidad macro 0.700 ± 0.018 del criterio anterior) sea de test, no de validación, antes de citarla en el Cap. 4.
2. **El ranking del barrido usa una sola semilla.** Los 60 candidatos del barrido corren con semilla 42; las semillas 43 y 44 solo se corrieron para los dos ganadores (`lesion_split_report.json`). El `.tex` de 3.3 no lo dice y el de 3.4 tampoco: «tres semillas» se refiere al modelo ya elegido. ¿Se declara en 3.4 (sección del barrido)?
3. **(resuelta, a validar)** Monitor del *checkpoint*: el motivo del código era no reentrenar las 60 corridas (plan del 17/09). El texto lo reemplazó por la estabilidad con DF y VASC chicos (ver «Decisiones», 1).
4. **Bootstrap por imagen.** El test tiene 1503 imágenes y 1429 lesiones. El `.tex` ya no dice que los IC pueden ser optimistas por remuestrear imágenes. ¿Se restituye una oración en 3.3.4 o se deja para el Cap. 4?
5. **Nivel 1 en los Caps. 4 y 5.** En los resultados vigentes (septiembre–octubre de 2026) no aparece; sí en los reportes de mayo (`reportes_resul_v1_20260503.md`, `reportes_resul_v2_20260517.md`), sobre la partición anterior. Si no se reporta, 3.3.3 lo define y dice que no decide. ¿Se mantiene la definición?
6. **(resuelta)** Calibración: movida a 3.8; `tab:met_roles` solo remite (antigua pregunta 5).
7. **(resuelta)** Nombres de las métricas del Nivel 2: el texto usa «consistencia diagnóstica» y «cobertura de entidades clínicas» (antigua pregunta 6). La guía §4 sigue sin entradas para estos dos términos; si se aprueba, conviene agregarlas allí (no lo toqué).
8. **(resuelta)** Desvío con tres semillas: P5 dice que es una estimación gruesa y remite a las pruebas (antigua pregunta 7).
9. **(obsoleta tras la revisión del 18/10)** Oráculo y línea base sin generador (antigua pregunta 8): se definen en 3.7.
10. **(obsoleta tras la revisión del 18/10)** Origen de las referencias de Nivel 1 (antigua pregunta 9): ya no se afirma en 3.3; se dice en 3.2 y hay que verificarlo allí contra los artículos de los conjuntos.
11. **Matcher.** ¿La lista de términos (`CLASS_TERMS`) va al apéndice o solo se describe la regla? (antigua pregunta 10; sigue abierta).
12. **(resuelta, a validar)** Comparaciones múltiples (pregunta 1 de la antigua 3.9): el texto aplica Holm a McNemar y deja la sensibilidad por clase como descriptiva (ver «Decisiones», 3).
13. **«Siete modelos».** P15 dice «como se comparan siete modelos, que forman 21 pares», pero 3.4 presenta cuatro arquitecturas más el ensamble. ¿Cuáles son los siete (por ejemplo, los cuatro clasificadores, el ensamble y dos VLM)? Hay que decirlo o remitir a la sección que los enumera.

## Decisiones tomadas por cuenta propia

- **D1. Cuatro subsecciones** (3.3.1 con `sec:met_seleccion`, 3.3.2 con `sec:met_lineas_base`, 3.3.3 con `sec:met_eval_generacion` y 3.3.4 con `sec:met_estadistica`). La sección se lee como criterio, después líneas base, después generación y después pruebas, y 3.4 encuentra el criterio antes de usarlo.
- **D2. El clasificador trivial es el único valor numérico de desempeño**, porque es propiedad de los datos y no de un modelo. Verificado con el test de 1503 imágenes (`revision_experimentacion_20261003.md` §1).
- **D3. El umbral de melanoma** se define como «el que en validación maximiza la sensibilidad con especificidad ≥ 0.85», que es lo que hace `_thr_at_spec`. El ensamble usa la media de probabilidades (3.4).
- **D4. El desvío es muestral** (`ddof=1`), como en `lesion_split_report.py`.
- **D5. Calibración y HIBA salen de 3.3** y van a 3.8. Las pruebas estadísticas entran desde la antigua 3.9 (D-A).
- **D6. La métrica oficial de generación** es la consistencia diagnóstica solo sobre el reporte, con búsqueda estricta (`revision_experimentacion_20261003.md` §5.1). Los valores de la cascada no se citan en 3.3.
- **D7. Se toma de la tesina de ejemplo** la forma de justificar las métricas a partir del problema (Maglione, pp. 58–59) y la línea base como modelo sencillo que sirve de referencia para comparar (p. 55). No se toma su estilo de títulos de párrafo ni la ecuación de la línea base.
- **D8. Decisiones nuevas de la revisión del 18/10/2026, a validar por el autor:**
  1. **El F1 ponderado elige la época por estabilidad.** Con 14 imágenes de DF y 18 de VASC en validación, el F1 macro salta entre épocas por un par de aciertos y el F1 ponderado, dominado por las clases grandes, es más estable para decidir cuándo detener. El motivo histórico era otro: cambiar el monitor obligaba a reentrenar las 60 corridas del barrido (plan del 17/09), una razón de costo y no de método. El texto da la razón de método y omite la de costo.
  2. **La especificidad ≥ 0.85 se justifica como decisión de diseño**, no como valor clínico (D-D): se prioriza no perder melanomas, con un tope de 15 % de falsas alarmas en validación. No se atribuye a ninguna guía clínica.
  3. **Holm sobre McNemar y comparación descriptiva de la sensibilidad por clase** (cambio respecto de la antigua 3.9, que corría Wilcoxon sobre siete clases sin corrección). La razón que da el texto: con siete valores ninguna prueba de rangos alcanza el umbral de Holm para 21 comparaciones. Esta decisión no figura entre D-A a D-E y la tomó la redacción de la revisión; ver pregunta 12.
