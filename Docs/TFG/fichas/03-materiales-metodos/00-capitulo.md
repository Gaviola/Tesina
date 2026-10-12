# Ficha del Capítulo 3 — Materiales y métodos

**Estado (11/10/2026): aprobada por el autor como punto de partida; se ajusta a medida que surjan detalles.** Contrato del capítulo. Ninguna sección se redacta hasta que
el autor apruebe esta ficha y la ficha de la sección (guía §1).

Fuentes de esta ficha: el andamiaje actual de `Chapters/03-Materiales-Metodos/` (con el feedback del tutor del
14/09 y la revisión del 25/09 en sus comentarios), la ficha del Cap. 2 (`fichas/02-marco-teorico/00-capitulo.md`),
la ficha de referencia del Cap. 4 (rama `doc/cap04-resultados-clasificacion`), la tercera revisión del tutor
(`feedback/cap1_2/feedback_cap1_y_2_v3.md`, Audios 3 y 4), `Docs/experimentacion/experimentacion.tex` y el
Capítulo 3 de la tesina de ejemplo (`Docs/tesinamaglione_ejemplo.pdf`, pp. 37–58).

## Lo que se toma de la tesina de ejemplo

El Capítulo 3 de la tesina de ejemplo («Metodología y desarrollo del trabajo») resuelve un problema parecido:
datos propios con dificultades (desbalance de 95/4/1 %, registros atípicos, partición que no puede filtrar
información entre conjuntos), modelos de aprendizaje profundo comparados contra una línea base y cómputo
limitado. Su orden es: definición formal de la tarea → flujo de trabajo (figura) → datos (recolección, análisis
exploratorio, preprocesamiento, conjunto final) → arquitecturas → modelo *baseline* → hiperparámetros → método
de entrenamiento → métricas.

| De la tesina de ejemplo | Cómo se traslada | Qué se mejora |
|---|---|---|
| §3.1 «Definición formal de la tarea», en un párrafo destacado, con las clases enumeradas | 3.1 define las tres tareas del trabajo (clasificación en siete clases, detección binaria de melanoma, generación del reporte) con su entrada, su salida y la restricción de cómputo | Cada tarea se vincula con la pregunta (PI1, PI2) y el objetivo (OE) que responde |
| §3.2 «Flujo de trabajo» con una figura de etapas | 3.2 presenta el flujo con una figura TikZ | El flujo del ejemplo es lineal; el de este trabajo fue iterativo y la figura muestra dónde una hipótesis refutada cambió el rumbo (desbalance → especialización de dominio → cascada) |
| §3.3.2 Análisis exploratorio con figuras de distribución | 3.3 incluye un análisis exploratorio de *HAM10000*: distribución de clases, imágenes por lesión, ejemplos por clase | En el ejemplo el análisis es descriptivo; acá cada hallazgo justifica una decisión: el desbalance → la métrica (3.4); las imágenes repetidas por lesión → la partición disjunta; la modalidad → el rol de cada conjunto |
| §3.3.1 Tablas de las variables de cada fuente | Tabla de los conjuntos (modalidad, tamaño, rol, origen del texto) | Se agrega quién escribió los textos de referencia, que condiciona la validez de las métricas con referencia |
| §3.3.4 Distribución del conjunto final | Tabla de tamaños por clase en entrenamiento, validación y test de la partición por lesión | — |
| §3.5 «Modelo *baseline*» con su ecuación | 3.4 fija las líneas base y las cotas en un solo lugar: azar (1/7), clasificador mayoritario, clasificadores supervisados como referencia de los VLM, *oracle* y línea base sin generador para el *pipeline* | El ejemplo tiene una sola línea base; acá hay una por pregunta |
| §3.6 Tablas de hiperparámetros (parámetro, descripción, valores explorados), parámetros comunes y estrategia de búsqueda con el número de configuraciones | 3.5 lleva una tabla de los hiperparámetros explorados en el barrido y los fijos, con la estrategia de búsqueda y el número de corridas; 3.7 la configuración de LoRA y de decodificación | Las grillas completas van al Apéndice A; el cuerpo explica por qué esos rangos. Se reportan semillas y desvío, que el ejemplo no tiene |
| §3.7 Partición temporal justificada para que no se filtre información del futuro | La partición disjunta por lesión cumple el mismo papel y se justifica igual | Se cuantifica la fuga de la partición original y se dice cómo se midió su efecto |
| §3.7–3.8 Detención temprana, optimizador, función de pérdida con fórmula | Receta de entrenamiento en 3.5 | Las fórmulas ya están en el Cap. 2: acá solo se nombran con `\ref` y se dan los valores |
| §3.8 Métricas justificadas por el problema (minimizar falsos negativos) | 3.4 justifica cada métrica por el costo de las confusiones | El ejemplo redefine las métricas del Cap. 2; acá no se redefinen |

Lo que **no** se toma: los títulos de párrafo en negrita (la guía los prohíbe), la introducción que anuncia cada
sección por número con detalle técnico, y las listas de una línea por elemento cuando la prosa encadena mejor.

## Hilo del capítulo

Pregunta que responde el capítulo: ¿qué tareas, datos, modelos, procedimientos y criterios se usaron para
responder PI1 y PI2, de modo que otra persona pueda reproducir los experimentos y entender por qué se tomó cada
decisión?

Viene de: el Cap. 2 dejó los conceptos y, en el estado del arte, las limitaciones que el trabajo aborda y el
posicionamiento del *pipeline* (`sec:estado_arte_posicion`).
Deja instalado: todo lo que los Caps. 4 y 5 necesitan para presentar un resultado sin explicar cómo se obtuvo.

```
Intro    A partir de las limitaciones del estado del arte, el capítulo describe cómo se diseñó el trabajo
          ↓ necesidad: antes de cualquier experimento, qué se le pide exactamente a los modelos
3.1      Definición de las tareas: clasificación en siete clases, detección de melanoma, generación del
         reporte; entrada, salida y restricción de cómputo de cada una
          ↓ necesidad: tres tareas y dos preguntas requieren un plan de trabajo
3.2      Flujo de trabajo: ciclo hipótesis → ejecución → análisis → decisión (figura), registro de cada
         corrida, entorno de ejecución
          ↓ necesidad: la primera etapa del flujo son los datos
3.3      Conjuntos de datos: tabla de conjuntos; análisis exploratorio de HAM10000; partición disjunta por
         lesión; SkinCaRe, MM-Skin, Derm1M e HIBA
          ↓ consecuencia: datos desbalanceados y confusiones de costo desigual obligan a fijar cómo se decide
3.4      Criterios de evaluación y líneas base: métrica principal y de selección, líneas base y cotas,
         umbral de melanoma, métrica oficial de generación, fidelidad diagnóstica vs validez clínica
          ↓ aplicación: con esos criterios se entrenan y seleccionan los clasificadores
3.5      Clasificadores supervisados: arquitecturas, preprocesamiento, receta, desbalance, hiperparámetros y
         búsqueda, ensamble, detección de melanoma
          ↓ contraste: los clasificadores no generan texto; PI1 pregunta si un VLM clasifica igual de bien
3.6      Clasificación con VLM: generales (Mini-VLM, LLaVA-Med) con cuatro estrategias; DermLIP y sus modos
          ↓ necesidad: PI2 pide un reporte; los VLM generativos se ajustan para generarlo
3.7      Generación de reportes: formato, generadores, ajuste en dos etapas, configuración de LoRA,
         decodificación
          ↓ consecuencia: un generador que no discrimina necesita que el diagnóstico venga de afuera
3.8      Pipeline: cascada clasificador → generador, grounding por recuperación, ruteo en tres niveles
          ↓ necesidad: el test de la misma fuente no alcanza para sostener un resultado (Sección 2.6)
3.9      Análisis complementarios: protocolos de inferencia, pruebas estadísticas, validación externa,
         perturbaciones, calibración, Grad-CAM y costo computacional
→ Cierre: el capítulo deja definido el protocolo; los resultados de clasificación abren el Cap. 4.
```

## Secciones, origen y archivos

| Nueva | Título | Contenido | Archivo | Labels | Ext. |
|---|---|---|---|---|---|
| 3.1 | Definición de las tareas | Las tres tareas en el formato de «definición formal» del ejemplo; inventario de siete clases de *HAM10000* con su gravedad (prosa ya escrita en `sec:met_ham`, se mueve acá); «detección» = binaria derivada, no localización; generación = descripción + impresión diagnóstica; restricción: una GPU de consumo; relación tarea → PI → OE | `01-tareas.tex` (nuevo) | `sec:met_tareas` | 1.5–2 p. |
| 3.2 | Flujo de trabajo | Figura del flujo iterativo; ciclo con registro (plan, ejecución, resultado con veredicto); el orden de los Caps. 4 y 5 sigue el de las decisiones; entorno: RTX 4070 local, TOKO (RTX 4080), Mendieta (A30), SLURM, seguimiento de experimentos; reproducibilidad → Apéndice E | `02-flujo-trabajo.tex` (absorbe `01-metodologia` y `08-infraestructura`) | `sec:met_metodologia`, `sec:met_infra` | 2–2.5 p. |
| 3.3 | Conjuntos de datos | Tabla de conjuntos; análisis exploratorio de *HAM10000* (distribución de clases, imágenes por lesión, ejemplos por clase); partición disjunta por lesión (fuga cuantificada, reevaluación sobre el subconjunto limpio, `StratifiedGroupKFold`, tabla de tamaños por clase y partición); *SkinCaRe* (*SkinCAP*, *SkinCoT* y su formato de razonamiento, con un ejemplo de texto), *MM-Skin*, *Derm1M* (solo como preentrenamiento de DermLIP), *HIBA* (solo test; 346 de sus 1616 imágenes son clínicas) | `03-datos.tex` (sale de `02-datos-particiones`) | `sec:met_datasets`, `sec:met_ham`, `sec:met_particiones` | 5–6 p. |
| 3.4 | Criterios de evaluación y líneas base | Costos asimétricos (ya escrito) → sensibilidad macro como resultado principal; líneas base y cotas (azar, clasificador mayoritario, *oracle*, línea base sin generador); F1 macro para elegir la corrida y F1 ponderado para el *checkpoint*; el test no decide nada; umbral de melanoma con especificidad ≥ 0.85 fijado en validación; métrica oficial de generación (solo el reporte, *matcher* estricto) y los dos niveles; fidelidad diagnóstica ≠ validez clínica; media ± desvío de tres semillas | `04-criterios-evaluacion.tex` (sale de `07-protocolo-evaluacion`) | `sec:met_protocolo`, `sec:met_seleccion` | 3 p. |
| 3.5 | Clasificadores supervisados | DenseNet121, ViT-B/16, Swin-Tiny, ConvNeXt-Tiny y por qué esas cuatro; preprocesamiento, aumento y TTA; receta (AdamW, *cosine*, detención temprana con su paciencia); pérdidas para desbalance; tabla de hiperparámetros explorados y fijos, estrategia de búsqueda y número de corridas; semillas; ensamble Swin + ConvNeXt; detección de melanoma | `05-clasificadores-supervisados.tex` (sale de `03-modelos-evaluados`) | `sec:met_supervisados` | 4–5 p. |
| 3.6 | Clasificación con modelos visión–lenguaje | Mini-VLM y LLaVA-Med: arquitectura, tamaño, motivo; las cuatro estrategias (figura de *zero-shot* frente a *likelihood*), *prompts* (Apéndice B) y parseo; DermLIP: *zero-shot*, *linear probe*, kNN y SVM sobre *embeddings*, y el control con las mismas cabezas sobre Swin-*ImageNet* congelado | `06-clasificacion-vlm.tex` (sale de `04-clasificacion-vlm`) | `sec:met_clasif_vlm` | 3.5 p. |
| 3.7 | Generación de reportes | Partes del reporte (ya escrito); generadores (Mini-VLM y LLaVA-Med ajustados; SkinVL como generador especializado); ajuste en dos etapas sobre *SkinCaRe*; tabla de configuración de LoRA; separación reporte / razonamiento; decodificación | `07-generacion-reportes.tex` (sale de `05-generacion-reportes`) | `sec:met_generacion` | 3 p. |
| 3.8 | Pipeline propuesto | Por qué separar diagnóstico y redacción; cascada con *grounding* y variante *noreasoning*; *grounding* por recuperación (kNN DermLIP, k = 3); ruteo en tres niveles por acuerdo Swin–kNN y sus plantillas (Apéndice B). Diagrama del *pipeline* y del ruteo | `08-pipeline.tex` (sale de `06-pipeline`) | `sec:met_pipeline` | 3.5 p. |
| 3.9 | Análisis complementarios | Tabla de protocolos de inferencia (vista única o TTA, *checkpoint*, partición por resultado); *bootstrap* pareado, McNemar y Wilcoxon (cuál corresponde a qué comparación); *HIBA*; perturbaciones de adquisición; calibración *post-hoc* ajustada en validación; Grad-CAM; medición del costo computacional | `09-analisis-complementarios.tex` (sale de `07-protocolo-evaluacion`) | `sec:met_complementarios` | 3 p. |

Total orientativo: 29–32 páginas (el ejemplo ocupa 22 sin la aplicación web; este trabajo tiene dos tareas y un
*pipeline*). Los archivos se renombran en el commit de la sección que los reescribe.

**Labels que no pueden cambiar** (los usan otros capítulos o la ficha del Cap. 4): `cp:metodos`, `sec:met_ham`,
`sec:met_seleccion`, `sec:met_particiones`, `sec:met_protocolo`, `sec:met_clasif_vlm`. `sec:met_modelos`
desaparece (nadie lo referencia). `sec:met_ham` queda en 3.3 sobre el análisis de *HAM10000*; las categorías
pasan a 3.1, y el `\ref` del Cap. 2 (`01-fundamentos.tex:161`, «los nevos superan varias veces a los
melanomas») sigue apuntando bien porque habla de la distribución de clases, que queda en 3.3.

## Figuras y tablas previstas

| Sección | Elemento | Origen | Estado |
|---|---|---|---|
| 3.2 | Flujo de trabajo iterativo | TikZ nuevo, estilos de `13-Figuras.sty` | a dibujar |
| 3.3 | Tabla de conjuntos (modalidad, tamaño, rol, origen del texto) | `experimentacion.tex` (`tab:datasets`), corregida (*HIBA*) | a adaptar |
| 3.3 | Distribución de clases de *HAM10000* | `Docs/experimentacion/imagenes/F0_ham_dist.png`, o regenerada con la paleta Okabe–Ito | existe |
| 3.3 | Imágenes por lesión (histograma) | script nuevo sobre los metadatos de `Codigo/data/raw/HAM10000` | a generar |
| 3.3 | Una imagen de ejemplo por clase | `Codigo/data/raw/HAM10000`; revisar la licencia de *HAM10000* antes de reproducir (guía §7) | a generar |
| 3.3 | Tamaños por clase y partición | `Codigo/outputs/results/lesion_split_report.json` | a armar |
| 3.3 | Ejemplo de texto de *SkinCoT* | `ej_skincot_human.jpg` y el texto del conjunto | existe |
| 3.5 | Hiperparámetros explorados y fijos | `Codigo/configs/*.yaml`, `split_lesion_resul_20260926.md` | a armar |
| 3.6 | *Zero-shot* frente a *likelihood scoring* | `experimentacion.tex` (`fig:zsvslik`), redibujada con los estilos de la plantilla | a adaptar |
| 3.7 | Configuración de LoRA y decodificación | `Codigo/configs/` | a armar |
| 3.8 | Diagrama del *pipeline* y del ruteo | `experimentacion.tex` (`fig:cascada`, `fig:incertidumbre`) y `mapa-capitulo.tex` como base, sin cifras de resultados | a adaptar |
| 3.9 | Protocolo de inferencia por resultado; prueba estadística por comparación | fichas de los Caps. 4 y 5 | a armar |

## Decisiones de esta ficha (a confirmar por el autor)

| # | Cambio respecto del andamiaje | Motivo |
|---|---|---|
| D1 | «Modelos evaluados» se disuelve: cada modelo se presenta en la sección de la tarea que cumple (3.5, 3.6, 3.7) | El andamiaje describía Mini-VLM y LLaVA-Med en un lugar y su uso en otro. Ordenado por tarea, 3.5–3.6 preparan el Cap. 4 y 3.7–3.8 el Cap. 5, y cada modelo se presenta una vez, donde aparece primero |
| D2 | Los criterios de evaluación suben a 3.4, antes de los modelos, y reúnen las líneas base | El barrido de 3.5 elige por F1 macro y la detección de melanoma usa un umbral; si el criterio se explica al final, se usa antes de presentarlo (guía §3). Las líneas base juntas siguen el ejemplo (§3.5) |
| D3 | Sección nueva 3.1, definición formal de las tareas | Sigue al ejemplo (§3.1). Hoy las tareas están repartidas entre el `\pendiente` del capítulo, `sec:met_ham` y `sec:met_generacion` |
| D4 | Metodología e infraestructura se unen en 3.2, «Flujo de trabajo» | Sigue al ejemplo (§3.2) y deja el hardware dicho antes de que 3.5–3.8 lo usen para justificar decisiones (LoRA, modelos *Tiny*) |
| D5 | Análisis exploratorio de *HAM10000* con figuras nuevas en 3.3 | Sigue al ejemplo (§3.3.2), con la diferencia de que cada hallazgo justifica una decisión |
| D6 | Tablas de hiperparámetros en el cuerpo (3.5, 3.7); grillas completas en el Apéndice A | Sigue al ejemplo (§3.6). Hoy todo iba al apéndice |
| D7 | Preprocesamiento y aumento pasan de los datos a 3.5 | Son parte de la receta de entrenamiento de los clasificadores |
| D8 | Los análisis complementarios quedan al final, en 3.9 | Se aplican a modelos y al *pipeline* ya presentados |

## Alcance y decisiones heredadas

1. **Cada capítulo habla de lo suyo.** El Cap. 3 no define conceptos: los nombra y remite al Cap. 2 con `\ref`
   (tabla de abajo). Tampoco presenta resultados: un número aparece solo si describe datos o configuración
   (tamaños, porcentaje de fuga, hiperparámetros), nunca un desempeño. Los desempeños van a los Caps. 4 y 5. Las
   figuras que se adaptan de `experimentacion.tex` pierden sus cifras de resultados.
2. **Recibe del Cap. 1** (commit f520295, hoy en el `\pendiente` de `00-capitulo.tex`): el rol de cada conjunto,
   la histopatología fuera de alcance, «detección» = tarea binaria de melanoma derivada de la clasificación (no
   localización ni segmentación), fidelidad diagnóstica ≠ validez clínica, y la decisión de no preentrenar un
   VLM y adaptar modelos preentrenados con LoRA por la restricción de cómputo.
3. **Recibe del Cap. 2** (revisión del 25/09, decisión 14 del historial): las categorías de *HAM10000* (ya
   escrito, pasa a 3.1), los costos asimétricos de confusión (ya escrito, 3.4) y las partes del reporte (ya
   escrito; pasa a 3.1 como salida de la tarea de generación, y 3.7 lo retoma con `\ref`). La prosa ya escrita
   se conserva y se ajusta al hilo.
4. **Lo que la ficha del Cap. 2 manda al Cap. 3:** la versión de McNemar que usa el código, quién escribió los
   textos de referencia de *SkinCaRe* y *MM-Skin*, la distribución de *HAM10000* y la partición.
5. **Fuente de los números.** Partición disjunta por lesión: `Codigo/docs/resul/split_lesion_resul_20260926.md`
   y `Codigo/outputs/results/lesion_split_report.json`. Métrica oficial de la cascada, ruteo, *HIBA* y RAG:
   `Codigo/docs/resul/revision_experimentacion_20261003.md` (§5, decisiones) y `reanclaje_cascada_resul_20261003.md`.
   `Docs/experimentacion/experimentacion.tex` sirve para la estructura y el argumento, **no** para los números:
   su cuerpo es de la partición aleatoria (ver la nota de actualización al comienzo de ese archivo).
   Hiperparámetros: los valores efectivos están en `Codigo/src/training/recipes.py` y en los scripts de envío de
   los barridos, no en `Codigo/configs/*.yaml`, que `train_classifier.py` no lee y que en parte quedaron
   desactualizados (p. ej. `mini_vlm.yaml` describe CLIP ViT-B/16 + Phi-3-mini, pero el modelo usado es
   Phi-3.5-vision-instruct, según `src/models/mini_vlm.py`). Todo número de una ficha de sección dice de qué
   archivo sale.
6. **Declarado sobre la partición anterior** (no se rehace; el Cap. 3 lo dice donde corresponde): RAG y
   `full_uncertainty`, métricas por clase y taxonomía de la cascada, ablaciones de la receta. **Los VLM generales
   no se ajustaron sobre *HAM10000*** (corrección del 11/10/2026): la estrategia «ajuste fino» de clasificación
   evalúa sobre *HAM10000* el *checkpoint* de la etapa 2 de generación, entrenado con *SkinCaRe*
   (`train_vlm_classify.py --checkpoint stage2_*_v2`, `vlm_clasificacion_resul_v3_20260517.md`). No hay fuga en
   esos modelos. La ficha del Cap. 4 (rama `doc/cap04-resultados-clasificacion`, §4.2, «Declarar») dice lo
   contrario y hay que corregirla.
7. **Apéndices.** El detalle que no hace falta para seguir el argumento va al apéndice y se remite: grillas
   completas (A, `ap:hiperparametros`), *prompts* y plantillas (B, `ap:prompts`), reproducibilidad (E,
   `ap:reproducibilidad`), fichas de conjuntos y modelos (F).

## Dónde se define cada cosa

Lo que es concepto se definió en el Cap. 2 y acá solo se nombra con `\ref`. Lo que es decisión propia se define
una vez en el Cap. 3.

| Qué | Se define en | Se retoma en |
|---|---|---|
| Red neuronal, entropía cruzada, generalización, particiones, fuga de información, regularización, aumento, TTA, desbalance, transferencia | Cap. 2 (`sec:marco_fundamentos`, `sec:marco_regularizacion` —ahí están la fuga y el TTA—, `sec:marco_desbalance`, `sec:marco_transferencia`) | 3.3, 3.5 |
| CNN, ViT, Swin, ConvNeXt | Cap. 2 (`sec:marco_vision`) | 3.5 |
| LLM, LoRA, CLIP, VLM generativo, clasificación por verosimilitud | Cap. 2 (`sec:marco_llm`, `sec:marco_llm_lora`, `sec:marco_vlm`) | 3.6, 3.7 |
| Calibración, abstención, predicción selectiva, tres salidas | Cap. 2 (`sec:marco_incertidumbre`) | 3.8, 3.9 |
| Reporte clínico, alucinación, *hedging*, RAG | Cap. 2 (`sec:marco_reportes`) | 3.7, 3.8 |
| Métricas (sensibilidad macro, F1, AUC, ECE, BLEU…, McNemar, Grad-CAM), robustez, cambio de dominio | Cap. 2 (`sec:marco_evaluacion`, `sec:marco_generalizacion`) | 3.4, 3.9 |
| Las tres tareas, las siete clases, las dos partes del reporte, la restricción de cómputo | 3.1 | todo el capítulo |
| Ciclo iterativo, registro, entorno de ejecución | 3.2 | 3.9 (costo) |
| Composición de *HAM10000*, imágenes por lesión, partición disjunta por lesión, formato de *SkinCoT* | 3.3 | 3.4, 3.5, 3.7 |
| Métrica principal, de selección y oficial de generación; líneas base de clasificación (azar, clasificador mayoritario, supervisados como referencia de los VLM); umbral de melanoma; fidelidad vs validez | 3.4 | 3.5–3.9 |
| Receta de entrenamiento, búsqueda de hiperparámetros, ensamble de clasificadores | 3.5 | 3.8, 3.9 |
| Mini-VLM, LLaVA-Med, las cuatro estrategias, DermLIP y sus modos | 3.6 | 3.7, 3.8 |
| SkinVL, ajuste en dos etapas, separación reporte / razonamiento | 3.7 | 3.8 |
| Cascada, *grounding*, *noreasoning*, ruteo en tres niveles; *oracle* y línea base sin generador (necesitan la cascada y el ruteo, que se presentan acá) | 3.8 | 3.9 |

**Dependencia con la reescritura del Cap. 2.** Los labels del Cap. 2 se conservan al reescribirlo (su ficha lo
fija), así que los `\ref` de este capítulo no se rompen. Si al reescribir el Cap. 2 un concepto cambia de
sección, se corrige el `\ref` acá; no se redefine.

## Revisión cruzada de las fichas de sección (11/10/2026)

Las nueve fichas se prepararon en paralelo. Lo que esta revisión resolvió prevalece sobre lo que diga cada ficha:

1. **Labels del Cap. 2.** La fuga de información y el TTA están en `sec:marco_regularizacion` (2.1), no en
   `sec:marco_generalizacion` (2.9, sesgo y robustez). Ya corregido en las fichas 3.2, 3.3, 3.4, 3.6, 3.8 y 3.9.
2. **Claves de cita.** *HIBA* es `riccilara2023dataset`; LLaVA-Med es `li2023llavamed`; LoRA es `hu2021lora`.
   Mini-VLM (Phi-3.5-vision) y SkinVL no tienen clave en el `.bib`: se proponen en `refs_pendientes.md`.
3. **Duplicaciones.** Las partes del reporte se definen en 3.1 (3.7 las nombra). El *oracle* y la línea base sin
   generador se definen en 3.8 (3.4 solo anuncia que el *pipeline* tiene su propia línea base).
4. **VLM ajustados sin fuga** (ver «Alcance», punto 6). Afecta a 3.6 y a la ficha del Cap. 4.
5. **Mini-VLM** es Phi-3.5-vision-instruct; los `.yaml` y `experimentacion.tex` que dicen CLIP ViT-B/16 +
   Phi-3-mini están desactualizados.

Preguntas que cruzan varias secciones y decide el autor (el detalle está en cada ficha):

- **Decisiones tomadas mirando el test.** El paso a F1 macro como criterio de selección (17/09, ficha 3.4), la
  elección de la concordancia como señal de ruteo (julio, ficha 3.8) y posiblemente la variante *noreasoning*
  (junio, ficha 3.8, a verificar) se motivaron con cifras de test. La frase «el test no interviene en ninguna
  decisión» no se puede escribir tal cual: se declara qué decisiones se tomaron así y por qué no invalidan el
  resultado.
- **Protocolos mezclados.** DenseNet121 y ViT-B/16 (receta anterior) se evalúan con vista única y pesos por
  clase; Swin y ConvNeXt, con TTA y sin pesos (fichas 3.5 y 3.9). Hay que declararlo o reevaluar los primeros
  con TTA (`reeval_tta_probs.py`).
- **Comparaciones múltiples.** 21 pares de McNemar y 21 de Wilcoxon sin corrección (ficha 3.9).
- **Evaluación en *HIBA*.** Las 1 616 imágenes o el test de `hiba_splits.json` (243) (fichas 3.3 y 3.9).
- **Licencias.** *HAM10000* (CC BY-NC 4.0) para reproducir ejemplos por clase; *SkinCaRe* declara dos licencias
  y prohíbe redistribuir (ficha 3.3).

## Introducción del capítulo

Un párrafo, sin detalle técnico ni figuras: qué describe el capítulo (todo lo necesario para reproducir los
experimentos) y en qué orden. Se escribe al final, como en el Cap. 2.

## Orden de trabajo

1. El autor aprueba esta ficha (estructura, D1–D8).
2. Fichas de sección 3.1–3.9 con su hilo conductor (`fichas/03-materiales-metodos/<NN-seccion>.md`). Se pueden
   preparar en paralelo porque la tabla «Dónde se define cada cosa» fija qué define cada una; el autor las
   aprueba.
3. Figuras que dependen de datos (imágenes por lesión, ejemplos por clase, tamaños de la partición): un script
   en `Codigo/scripts/` antes de redactar 3.3.
4. Prosa en el `.tex` de cada sección, pasada de estilo y un commit por sección.
5. Introducción del capítulo (`00-capitulo.tex`) al final.
