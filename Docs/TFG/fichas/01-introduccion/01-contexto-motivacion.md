# Ficha 1.1 — Contexto y motivación

Sección del `.tex`: `Chapters/01-Introduccion/01-contexto-motivacion.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 1.1 Contexto y motivación — `sec:intro_contexto` — I2, A3, M1.1–M1.3, p28–p30

**Mensaje central.** Partiendo del problema clínico se llega, sin saltos, a dos tareas
computacionales, y de ahí a un problema de investigación que las conecta. La sección **motiva**: no
describe la metodología ni introduce términos que el marco teórico todavía no explicó (A1, A3).

**Extensión: 2.5–3 páginas.** 11 párrafos, 4 bloques. Cada párrafo de 4 a 7 líneas.

**Hilo conductor en una línea.** Detección temprana → hay pocos especialistas, lecturas variables y carga de
documentación → dos retrasos = dos tareas → métodos computacionales: CNN y transformers para clasificar,
VLM para integrar imagen y texto → quedan dos temas abiertos (generalización y salida fiel) → las dos
tareas están conectadas y no basta resolverlas por separado.

### Bloque 1. Problema clínico y detección temprana

| # | Idea | Viene de → lleva a | Citas |
|---|---|---|---|
| 1 | Carga del cáncer de piel. «La última estimación de GLOBOCAN, publicada en 2026, para el año 2024, atribuye 1 138 314 casos nuevos de cáncer de piel no melanoma (quinto tumor más frecuente) y 337 969 de melanoma». El melanoma es menos de una cuarta parte de los casos y casi la mitad de las muertes (58 398 frente a 58 721). Cifras ya verificadas (decisión 2 y 8, se conservan) | Abre el capítulo (tras la intro) → cierra con que esa fracción menor de casos concentra la mitad de la mortalidad, lo que pide saber de qué depende el desenlace | `sung2026global` |
| 2 | El desenlace depende del momento del diagnóstico. Supervivencia relativa a cinco años: 100.0 % localizado, 76.0 % regional, 34.0 % con metástasis a distancia; 77 % se diagnostica localizado, 10 % regional, 5 % a distancia; el margen de mejora está en el 15 % no localizado. **Cierra el bloque**: por eso importan las herramientas de apoyo al diagnóstico que ayuden a detectar a tiempo (M1.2) | ¶1 (peso del melanoma) → ¶3 (qué frena la detección temprana) | `nci2026melanoma` |

Se elimina la frase «La mayoría de las lesiones que llegan a consulta son benignas…» salvo que el autor la
quiera conservar: no tiene cita y no conduce a ningún párrafo siguiente.

### Bloque 2. Limitaciones del diagnóstico y de la documentación

Estructura de M1.1 y Audio 3: «dentro de la detección temprana hay varios factores». Se elimina «El
diagnóstico humano tampoco está resuelto» (p28: el diagnóstico siempre es humano).

| # | Idea | Viene de → lleva a | Citas |
|---|---|---|---|
| 3 | **Pocos especialistas** (va primero, Audio 3). Densidad media de 2.66 dermatólogos cada 100 000 habitantes en 158 países, de 0.37 en ingreso bajo a 5.05 en ingreso alto. Consecuencia: la primera valoración de una lesión queda muchas veces en manos de quien no es especialista | ¶2 (detectar a tiempo) → ¶4 (qué herramienta usa ese clínico) | `freeman2026global` |
| 4 | **Dermatoscopía: qué aporta y qué exige.** Mejora la exactitud diagnóstica respecto de la inspección a simple vista, pero sobre todo en manos experimentadas; hay pocos datos que respalden su uso en atención primaria, donde la revisión sistemática de 104 estudios la recomienda solo para clínicos con formación adecuada. Cierra diciendo qué aporta al problema: la herramienta existe, pero pocos clínicos tienen la formación (p28) | ¶3 (no hay especialistas) → ¶5 (aun entre formados la lectura no es uniforme) | `dinnes2018dermoscopy` |
| 5 | **La lectura varía entre observadores.** Estudio de 511 observadores y 139 algoritmos sobre el mismo material dermatoscópico: rango amplio de desempeño asociado a la formación. Dos consecuencias: no hay una lectura única y, por lo tanto, la etiqueta de un solo observador no es una referencia estable. **No se afirma una cifra de concordancia** (decisión 3, se conserva) | ¶4 → ¶6 | `tschandl2019comparison` |
| 6 | **Carga de documentación.** Registros de historia clínica electrónica en atención primaria: 5.9 h de una jornada de 11.4 h frente a ella, 1.4 h fuera del horario de atención; 44.2 % en tareas administrativas. Redactar el reporte de una lesión es parte de esa carga y una tarea distinta de emitir el diagnóstico. **Cierre del bloque (M1.2, Audio 3):** pocos especialistas, lecturas que varían y documentación que consume tiempo alargan los tiempos y generan **dos retrasos**, el de la interpretación y el de la documentación. De ahí dos tareas computacionales distintas: asignar una categoría a la lesión y redactar su reporte | ¶5 → ¶7 (se buscan métodos computacionales que aceleren ambas) | `arndt2017tethered` |

Nota de transparencia: `arndt2017tethered` es de atención primaria general, no de dermatología; el párrafo
lo dice así, como en la versión anterior.

### Bloque 3. Posibilidades y limitaciones de la inteligencia artificial

Orden de M1.2 y Audio 3: primero «se aplicaron métodos computacionales», después redes neuronales,
después CNN y transformers visuales para clasificar, después VLM. **El hito de 2017 no abre el bloque.**

| # | Idea | Viene de → lleva a | Citas |
|---|---|---|---|
| 7 | Para reducir esos retrasos se aplicaron métodos computacionales, entre ellos las redes neuronales. Con el aprendizaje profundo, las redes convolucionales y los *transformers* visuales se aplicaron a la clasificación de lesiones. Ejemplo fechado: en 2017 una red convolucional alcanzó un desempeño comparable al de dermatólogos certificados, y en 2019 los mejores algoritmos superaron a los expertos en el estudio ya citado (van como muestra del alcance, no como apertura). Las CNN (`\gls{cnn}`) y los ViT (`\gls{vit}`) se nombran acá por primera vez en el capítulo | ¶6 (dos tareas, la primera es clasificar) → ¶8 (limitaciones de estos métodos) | `esteva2017dermatologistlevel`, `tschandl2019comparison`, `dosovitskiy2021image`, `liu2021swin` |
| 8 | Las revisiones sistemáticas registran exactitudes altas en condiciones controladas, pero se cuestiona si ese desempeño se conserva fuera de la interpretación especializada, por ejemplo en atención primaria. Además, estos modelos producen una categoría y no el texto que la describe: la segunda tarea, la documentación, queda sin asistencia | ¶7 → ¶9 (VLM como respuesta parcial a la salida en texto) | `magalhaes2024systematic`, `kreouzi2024learning`, `jones2022intelligence` |
| 9 | Los modelos visión–lenguaje (`\gls{vlm}`) integran información visual y textual: alinean imágenes y descripciones en un espacio común, lo que permite clasificar comparando la imagen con frases, y los generativos multimodales agregan un modelo de lenguaje que produce texto libre condicionado a la imagen. Su adaptación al dominio biomédico mostró que el procedimiento se traslada a imágenes médicas. Se explica en una frase por concepto, sin detalle técnico (el detalle es Cap. 2) | ¶8 → ¶10 (qué queda abierto aun con estos modelos) | `radford2021learning`, `liu2023visual`, `li2023llavamed` |

**Se saca de acá «En dermatología esos modelos ya existen»** (SkinGPT-4, Derm1M). Eran «explicar cosas al
voleo» (p30) y pertenecen al estado del arte (Cap. 2, §2.10, eje de VLM en dermatología). No se citan en
el Cap. 1.

### Bloque 4. Problema de investigación y oportunidad de contribución

| # | Idea | Viene de → lleva a | Citas |
|---|---|---|---|
| 10 | Arranca con «A partir de lo anterior se identifican dos temas de trabajo aún abiertos» (p29). Los dos temas, **en un solo párrafo, en punto seguido** (p29). (a) **Generalización**: los sistemas de IA dermatológica caen en desempeño en los fototipos menos representados en los datos de entrenamiento, que dominan los conjuntos públicos, y la población local no es homogénea (registro argentino de 10 199 casos con diferencias regionales). (b) **Reportes diagnósticamente fieles**: generar un texto que describa la lesión y afirme el diagnóstico correcto, sin afirmar lo que la imagen no respalda | ¶9 → ¶11 | `daneshjou2022disparities`, `groh2021neural`, `loria2020cutaneous` |
| 11 | **Párrafo que conecta las dos tareas** (M1.3, Audio 10). La salida de una es la entrada de la otra: el diagnóstico de la clasificación es lo que el texto debe afirmar y sostener. Por eso no basta resolverlas por separado: un texto fluido puede sostener un diagnóstico equivocado, y un diagnóstico acertado puede ir con una descripción que no corresponde a la lesión, así que un modelo bueno en clasificar no garantiza un reporte fiel, ni un texto convincente garantiza un diagnóstico correcto. El párrafo cierra enunciando el problema de investigación: estudiar en conjunto la clasificación de lesiones y la generación de reportes con VLM, con recursos de hardware limitados (una frase, sin GB ni configuraciones, M1.10). Deja instalado el paso a las preguntas | ¶10 → §1.2 | ninguna (es síntesis propia) |

**Decisiones de contenido que se derivan del feedback:**
- La **restricción de hardware** queda en una frase dentro de ¶11 (y en el objetivo general); no es un eje
  ni un párrafo propio (p30: «es metodología»). Los 12–36 GB, la clase de GPU y el argumento de que los
  experimentos corren en equipamiento de laboratorio o de servicio clínico van al Cap. 3.
- `yilmaz2025resourceefficient` sale del Cap. 1 y pasa al estado del arte (Cap. 2, §2.10) o al Cap. 3.
- `riccilara2023dataset` (HIBA) sale del Cap. 1: nombrar un conjunto de datos es metodología. En ¶10 la
  generalización se motiva con la evidencia sobre fototipos y población local, sin nombrar HIBA.
- `hu2021lora` sale del Cap. 1 (ya no hay Alcance donde se explicaba).
- La **definición operativa de «detección»** (binaria derivada de la multiclase; no localización ni
  segmentación) sale del Cap. 1. Se escribe «identificación de melanoma» o «detección de melanoma» en su
  sentido corriente, sin definir; la definición precisa va en el Cap. 2 (§2.8, evaluación) o en el
  Cap. 3 (A1). **Se elimina** también el párrafo de las «dos condiciones de un reporte correcto» como
  párrafo aparte: queda reducido a las dos oraciones de ¶11.

**Tabla de qué se elimina y a dónde va**

| Se elimina del Cap. 1 | Motivo | Va a |
|---|---|---|
| Sección 1.4 Alcance y delimitación completa | A1, p32–p33: «TODO ESTO NO VA»; anticipa metodología y términos no presentados | ver desglose siguiente |
| — datasets (HAM10000, SkinCaRe, HIBA) y su papel | Metodología | Cap. 3 (M1) |
| — «fidelidad diagnóstica» vs «validez clínica» | Término sin introducir; es definición y limitación | Cap. 2 (§2.8, definición de la métrica) para el concepto; Cap. 6 (M3) para el límite de la evaluación |
| — significado de «detección» | A1 | Cap. 2 §2.8 o Cap. 3 |
| — restricción de cómputo y no pre-entrenar; LoRA | Metodología | Cap. 3 (decisión de diseño con `hu2021lora`); una frase queda en el objetivo general |
| — «no se desarrolla un producto clínico ni se valida con pacientes» | Limitación | Cap. 6, `sec:disc_limitaciones` (M3) |
| Párrafo «Un eje atraviesa el trabajo: el hardware» | p30: «es metodología» | Cap. 3; en Cap. 1 queda una frase (¶11) |
| Párrafo «En dermatología esos modelos ya existen» | p30: «explicando cosas al voleo» | Cap. 2 §2.10, eje de VLM en dermatología |
| Definición operativa de «detección» y párrafo de las dos condiciones del reporte | A1 | Cap. 2 §2.8 / Cap. 3; dos oraciones en ¶11 |
| «El diagnóstico humano tampoco está resuelto» | p28, A3 | Reescrito como bloque 2 |
| «Ya en 2017…» como apertura del bloque de IA | A3 | Pasa a ¶7 como ejemplo fechado |
| «Adelantar el diagnóstico…», «La mayoría de las lesiones son benignas» | sin cita / sin hilo | Se eliminan |

**Figura 1.1 (`fig:intro_dos_tareas`, `Figures/Capitulos/01-planteo-problema.tex`).** Recomendación: **se
quita del Capítulo 1.** Razones: (i) la intro no lleva figuras salvo que sean imprescindibles (p27,
p35) y esta no lo es para entender la motivación, que se sostiene en prosa; (ii) su contenido codifica
justamente lo que sale de la sección: la definición de «detección» y la «promesa del VLM» encerrada en un
recuadro. **Dónde queda:** el Cap. 2 ya la referencia (`Chapters/02-Marco-Teorico.tex`, ~l. 552, sección de
reportes, donde explica las dos condiciones de un reporte correcto). Propuesta: se traslada el `\input` a
esa sección del Cap. 2 (nueva §2.6) y se ajusta el recuadro de la promesa. En el Cap. 3 se deriva de ella
el diagrama del *pipeline*, como ya preveía la versión anterior de esta ficha. El traslado toca otro
capítulo (guía §2.4): se ejecuta al reescribir el Cap. 2, no al reescribir este. Hasta entonces la
referencia de la l. 552 sigue válida si el archivo se mantiene. Alternativa si el autor quiere conservarla acá:
ubicarla después de ¶11 con el recuadro de la promesa quitado.
