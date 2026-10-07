# Ficha del Capítulo 1 — Introducción (versión 2, revisión del tutor)

Contrato de contenido de la **nueva versión** del capítulo. Reemplaza al plan del 2026-09-26, que
describía la versión ya escrita en `Chapters/01-Introduccion.tex`. Esa versión se reescribe según la
revisión del tutor (códigos en `tareas_revision_cap1-2.md`: **A1–A16**, **M1.1–M1.12**, **p27–p35**, y
las decisiones **D1** y **D2**). Cada sección declara su mensaje, el esqueleto de párrafos, las claves de
cita y la extensión. Lo que no está acá no se escribe; lo que falte se anota como pregunta abierta.

**Estado: propuesta pendiente de aprobación del autor.** No se redacta prosa hasta que se apruebe.

**Estructura del capítulo (cuatro secciones, antes cinco):**

| Sección | Antes | Ahora |
|---|---|---|
| Intro del capítulo | resumen técnico con fases y GPU | presentación de contenido y organización, sin detalle técnico (I1, p27) |
| 1.1 Contexto y motivación | 7 párrafos sin hilo | 11 párrafos en 4 bloques con hilo conductor (I2, A3) |
| 1.2 Preguntas de investigación | PI1, PI2 + H1–H6 | solo PI1 y PI2 reformuladas (I3, I4, D1) |
| 1.3 Objetivos | textuales del plan + párrafo de discrepancias | objetivo general adaptado (D2) + OE1–OE3 revisados + tabla objetivo–pregunta–capítulo (I5, I6) |
| ~~1.4 Alcance y delimitación~~ | 4 párrafos | eliminada (I7) |
| 1.4 Organización del documento | «Responde la PI1» | «Este capítulo presenta…» (I8, p33) |

**Extensión total: 6–7 páginas.** Baja respecto de las 8–10 anteriores porque salen Alcance (1–1.5 p), las
hipótesis (1 p) y el párrafo de hardware y de «modelos que ya existen» (0.5 p). La guía (§5) y el
comentario del `.tex` dicen 8–10; ver pregunta abierta 1.

**Reglas que gobiernan esta ficha** (T2, guía de redacción; a incorporar a la guía):
- ningún término se usa antes de haberlo presentado (A1);
- cada párrafo retoma el anterior y lleva al siguiente (A3, A7);
- nada de metodología, datasets ni algoritmos en la introducción (A1);
- la intro de capítulo dice qué trae y cómo se organiza, sin detalle técnico ni figuras (p27, p35).

---

## Intro del capítulo (párrafo de apertura) — I1, p27

**Mensaje.** Qué contiene el capítulo y cómo se organiza. Nada técnico.

**Extensión: 1 párrafo de 4–5 líneas.** Sin figura.

**Esqueleto (una sola pieza).**
1. Este capítulo presenta el problema que motiva el trabajo: la dificultad de diagnosticar y de
   documentar lesiones de piel, y el aporte posible de la inteligencia artificial.
2. A partir de ese problema se formulan las preguntas de investigación y se enuncian los objetivos.
3. El capítulo cierra con la organización del documento.

**Se saca** (p27): el codificador visual, el LLM, las «dos fases», la GPU y «en sus dos partes» («¿el
cuerpo tiene dos partes?»). Los VLM, las fases y el hardware aparecen recién donde se motivan.

**Redacción sugerida** (a ajustar al redactar): «Este capítulo presenta el problema que motiva el
trabajo, las preguntas de investigación y los objetivos que lo organizan, y describe cómo se estructura
el resto del documento. Primero se plantea el problema clínico del diagnóstico de lesiones de piel y de su
documentación, y qué puede aportar la inteligencia artificial. A partir de ahí se formulan las preguntas y
se enuncian los objetivos, y se cierra con la organización de los capítulos siguientes.»

**Citas:** ninguna.

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

---

## 1.2 Preguntas de investigación — `sec:intro_preguntas` — I3, I4, D1, M1.6–M1.7

**Mensaje central.** Dos preguntas, una por tarea, concretas y ligadas a las métricas con que se responden
después. Sin hipótesis (D1).

**Extensión: 0.5–0.75 páginas.** Título nuevo: «Preguntas de investigación» (antes «…e hipótesis»,
`sec:intro_preguntas` se mantiene).

**Esqueleto.**
1. **Párrafo de entrada** (2–3 líneas): retoma ¶11 (el problema de investigación) y dice que se traduce en
   dos preguntas, una por tarea, porque las salidas son de naturaleza distinta y se evalúan con criterios
   distintos.
2. **`enumerate` con PI1 y PI2.**
3. **Párrafo de cierre** (2–3 líneas): las preguntas se responden en los Capítulos 4 y 5, y se discuten
   en conjunto en el Capítulo 6. Sin adelantar resultados.

**Redacción propuesta.**

**PI1.** ¿Cómo se compara el desempeño de los modelos visión–lenguaje, tanto generales como especializados
en dermatología, con el de clasificadores visuales supervisados (redes convolucionales y transformers
visuales) en la clasificación de lesiones de piel y en la identificación de melanoma, medido con F1 macro y
sensibilidad macro para la clasificación, y con sensibilidad, especificidad y AUC para el melanoma?

**PI2.** ¿Qué fidelidad diagnóstica alcanzan los reportes generados a partir de la imagen por un modelo
visión–lenguaje ajustado, entendida como la coincidencia entre el diagnóstico que el reporte afirma y el de
referencia de la imagen, y qué calidad descriptiva tienen, entendida como la adecuación del texto a la
lesión que la imagen muestra y medida con métricas de similitud textual y de contenido, considerando ambas
dimensiones por separado?

Cambios respecto de la versión anterior y su porqué: «aporta mejoras reales» y «precisos, completos y
clínicamente relevantes» (no medibles ni separados) se reemplazan por comparaciones ligadas a métricas
(M1.6, M1.7). PI2 separa fidelidad diagnóstica de calidad descriptiva, «dos dimensiones que el propio
documento reconoce como independientes» (M1.7). «Precisos» sale también por la regla de terminología
(«precisión» queda para *precision*).

**Qué se elimina (I4, D1).** H1–H6 y todo el texto que las rodeaba: la distinción entre hipótesis de partida
y exploratorias, «Se plantea tras refutarse…», «Su respaldo es por eso más débil…» y el párrafo sobre el
orden de formulación. **Qué pasa con H3–H6:** los análisis (desbalance, especialización de dominio,
cascada, incertidumbre) se mantienen en los Caps. 4 y 5 como preguntas o análisis que surgen de un
resultado, sin llamarlos hipótesis (M2). **Referencias a H1–H6 que hay que actualizar** al tocar esos
capítulos: `04-Resultados-Clasificacion.tex` l. 12, `05-Resultados-Generacion.tex` l. 13,
`06-Discusion.tex` l. 56–58 (que además remite a `sec:intro_preguntas`).

**Citas:** ninguna.

---

## 1.3 Objetivos — `sec:intro_objetivos` — I5, I6, D2, M1.10–M1.12

**Mensaje central.** Un objetivo general y tres específicos, coherentes con lo que se hizo, y una tabla que
los enlaza con las preguntas y los capítulos.

**Extensión: 1–1.5 páginas** (con la tabla).

**Esqueleto.**
1. **Párrafo de entrada** (1–2 líneas): a partir del problema y de las preguntas se plantea el objetivo
   general y tres objetivos específicos. Se elimina «Los objetivos se enuncian tal como fueron
   formulados…» (p32).
2. **Objetivo general** (un párrafo).
3. **Objetivos específicos** (`enumerate`, con una línea de detalle por objetivo).
4. **Párrafo de presentación de la tabla** (1–2 líneas) + **Tabla** (I6).

Se elimina el párrafo «Dos de esas formulaciones no coinciden…» (D2, p32: «Esto no va»). El balance de lo
cumplido queda en `sec:concl_objetivos`.

**Objetivo general propuesto** (adaptación de M1.10, no copia). Cubre clasificación, generación de reportes,
fidelidad diagnóstica y hardware limitado; deja fuera «mejorar la precisión diagnóstica y optimizar el flujo
de trabajo», que el trabajo no mide:

> Diseñar, implementar y evaluar un enfoque de aprendizaje profundo y de modelos visión–lenguaje,
> adaptados a partir de modelos pre-entrenados, para clasificar lesiones cutáneas y generar reportes
> dermatológicos a partir de imágenes, y analizar su desempeño diagnóstico, la fidelidad diagnóstica de los
> reportes y su viabilidad computacional con recursos de hardware limitados.

**Objetivos específicos propuestos** (sin sugerir entrenamiento desde cero: en todos los casos se
diseñó, implementó y evaluó adaptando modelos pre-entrenados; p32).

- **OE1.** Diseñar, implementar y evaluar, adaptando modelos pre-entrenados, clasificadores de lesiones
  cutáneas basados en redes convolucionales, transformers visuales y modelos visión–lenguaje, para
  identificar posibles melanomas.
  *Detalle:* compara modelos visión–lenguaje generales y especializados con clasificadores visuales
  supervisados sobre el mismo material y mide su desempeño en la clasificación y en la identificación de
  melanoma. Responde la PI1.
- **OE2.** Diseñar, implementar y evaluar, adaptando modelos pre-entrenados, un modelo visión–lenguaje que
  integre información visual y textual para producir un diagnóstico preliminar y reportes de lesiones
  cutáneas.
  *Detalle:* incluye estrategias para que el texto afirme solo el diagnóstico que la evidencia respalda, y
  evalúa por separado la fidelidad diagnóstica y la calidad descriptiva de los reportes. Responde la PI2.
- **OE3.** Evaluar el desempeño de los modelos desarrollados en distintas condiciones, analizando su
  desempeño diagnóstico, la calidad del texto generado y su costo computacional.
  *Detalle:* incluye la generalización a otra población, la calibración de la confianza de las predicciones
  y el tratamiento de la incertidumbre. Contribuye a responder las dos preguntas.

Diferencias con el plan de trabajo: OE2 pasa de «diseñar y entrenar» a «diseñar, implementar y evaluar,
adaptando modelos pre-entrenados»; OE3 abandona «utilidad práctica para el flujo de trabajo» (no hubo
evaluación con especialistas) y «escenarios clínicos» (concretados como generalización, calibración e
incertidumbre, según la decisión de la ficha anterior). Ver pregunta abierta 2.

**Tabla objetivo ↔ pregunta ↔ capítulo (I6, M1.11)** (`tab:intro_objetivos_preguntas`, `tabularx` con
`booktabs`, `\caption` arriba, rotulada «Tabla»):

| Objetivo específico | Pregunta | Se diseña y describe en | Se evalúa y responde en |
|---|---|---|---|
| OE1. Clasificadores de lesiones y de melanoma (CNN, ViT, VLM) | PI1 | Cap. 3, Materiales y métodos | Cap. 4, Resultados de clasificación |
| OE2. VLM para generar reportes | PI2 | Cap. 3, Materiales y métodos | Cap. 5, Resultados de generación |
| OE3. Evaluación en distintas condiciones | PI1 y PI2 | Cap. 3 (protocolo de evaluación) | Caps. 4 y 5 (resultados) y Cap. 6 (discusión y limitaciones) |

Debajo, una línea: el marco conceptual de todo está en el Cap. 2 y el balance de los objetivos en el
Cap. 7. Se mantiene breve para no repetir §1.4 (organización). La tabla solo se incluye si al cerrar los
Caps. 3–5 esas correspondencias siguen siendo ciertas (M1.12: «todo tiene que estar bien ordenado y
autocontenido»).

**Citas:** ninguna.

---

## 1.4 Organización del documento — `sec:intro_organizacion` — I8, p33

**Mensaje.** Qué presenta cada capítulo. **Formato: «Este capítulo presenta…»**, sin «Responde la PI1».

**Extensión: 0.5 páginas.** Lista `description` por capítulo, con `\ref`, más un párrafo de cierre para
los apéndices (el anexo se unificó con ellos, revisión del tutor del 2026-10-05). Sin describir el Cap. 1. Sin estimaciones de extensión.

**Redacción propuesta.**

- **Capítulo 2, Marco teórico.** Este capítulo presenta los conceptos necesarios para leer el resto:
  los fundamentos del aprendizaje profundo, los *transformers*, la clasificación visual, los modelos de
  lenguaje y los modelos visión–lenguaje, la generación de reportes y el tratamiento de la
  incertidumbre, las métricas de evaluación, el sesgo y la generalización, y el estado del arte.
- **Capítulo 3, Materiales y métodos.** Este capítulo presenta la metodología de trabajo: los conjuntos de
  datos, los modelos que se comparan, el formato del reporte, el *pipeline* y el protocolo de evaluación.
- **Capítulo 4, Resultados de clasificación.** Este capítulo presenta la comparación de las estrategias de
  clasificación, los análisis que surgen de sus resultados y la evaluación del desempeño fuera del
  conjunto de entrenamiento.
- **Capítulo 5, Resultados de generación.** Este capítulo presenta la evaluación de los reportes
  generados, el análisis de sus fallas y la comparación de las configuraciones del pipeline con su costo
  de cómputo.
- **Capítulo 6, Discusión.** Este capítulo presenta la interpretación conjunta de los resultados, la
  respuesta a las preguntas de investigación y las limitaciones del trabajo.
- **Capítulo 7, Conclusiones.** Este capítulo presenta los hallazgos principales, el balance de los
  objetivos y las líneas de trabajo futuro.

Nota de forma: repetir siete veces «Este capítulo presenta» es aceptable acá porque el formato lo pide el
tutor (p33) y lo usa la tesina de ejemplo; si suena mecánico, la primera entrada lo dice completo y las
siguientes pueden abrir con el sustantivo («El capítulo presenta…»), como en el ejemplo de p33.
«Pipeline» aparece en la lista sin explicación, porque el Cap. 3 lo define: no se lo presenta en el Cap. 1
como término técnico. Si el autor prefiere no usarlo antes de definirlo, se reemplaza por «el enfoque
propuesto».

**Citas:** ninguna.

---

## Orden de redacción

1. §1.1 (la que argumenta; la más larga). 2. §1.2 y §1.3. 3. Organización, al final, cuando los títulos de los
capítulos no se muevan. 4. Intro del capítulo, después de escribir todo lo demás. La tabla de §1.3 al último,
con los Caps. 3–5 cerrados.

## Claves de cita del capítulo (verificadas contra `Bibliography.bib`, 2026-09-28)

Usadas en la nueva versión: `sung2026global`, `nci2026melanoma`, `freeman2026global`,
`dinnes2018dermoscopy`, `tschandl2019comparison`, `arndt2017tethered`, `esteva2017dermatologistlevel`,
`dosovitskiy2021image`, `liu2021swin`, `magalhaes2024systematic`, `kreouzi2024learning`,
`jones2022intelligence`, `radford2021learning`, `liu2023visual`, `li2023llavamed`,
`daneshjou2022disparities`, `groh2021neural`, `loria2020cutaneous`. Todas existen.

Salen del capítulo: `zhou2023skingpt4`, `yan2025derm1m`, `yilmaz2025resourceefficient` (a Cap. 2/§2.10 o
Cap. 3), `riccilara2023dataset`, `tschandl2018ham10000`, `shen2025skincare` (Cap. 3), `hu2021lora` (Cap. 3).

No existen en el `.bib`: `kittler2002diagnostic`, `vestergaard2008dermoscopy`, `sinsky2016allocation`,
mencionadas en la ficha anterior (versión del 2026-09-26, resuelta con `dinnes2018dermoscopy` y
`arndt2017tethered`). No usarlas. `dosovitskiy2021image` y `liu2021swin` se incorporan para ¶7; verificar
que sean las claves que el Cap. 2 usa para ViT y Swin.

## Preguntas abiertas para el autor

1. **Extensión.** La propuesta queda en 6–7 páginas, por debajo de las 8–10 fijadas. ¿Se ajusta la guía (§5)
   y el comentario del `.tex`, o se prefiere ampliar ¶1–¶11 con más datos?
2. **OE3 y «utilidad práctica».** El plan de trabajo la incluía y no se evaluó con especialistas. ¿Se
   elimina (como en la propuesta) o se mantiene con redacción que la deje como línea futura?
3. **Métricas dentro de PI1 y PI2.** Se nombran F1 macro, sensibilidad macro, especificidad, AUC, y
   «métricas de similitud textual y de contenido». ¿Son las que usan finalmente los Caps. 4 y 5? Si el Cap. 5
   evalúa con métricas de entidades diagnósticas, PI2 conviene nombrarlas.
4. **«Fidelidad diagnóstica» en PI2.** El término queda con una glosa entre comas, aunque la regla A1
   pide no usar términos antes de presentarlos. Se justifica porque el término es el del propio tutor
   (M1.7, M1.10), pero ¿se prefiere la glosa o una redacción sin término técnico («si el diagnóstico que
   afirma el reporte es el correcto»)?
5. **Figura 1.1.** ¿Se acepta que se traslade al Cap. 2 (§2.6), o se prefiere eliminarla o dejarla en el
   Cap. 1?
6. **Hipótesis.** D1 las elimina. La propuesta del tutor (M1.4, M1.5) admitía conservar H1 y H2; si el
   tutor las pide, se vuelve a esa opción (D1).
7. **Cifras de `arndt2017tethered` y `dinnes2018dermoscopy`.** Son de atención primaria general y de dermatoscopía
   en manos no especialistas. ¿Se dejan ambas como respaldo de ¶4 y ¶6 con la aclaración de alcance?

---

## Decisiones tomadas (vigentes)

1. **El presupuesto de memoria de GPU es 12--36 GB, no 12--24** (Cap. 3 lo declara; el Cap. 1 ya no lo
   menciona).

2. **§1.1 ¶1 afirmaba algo falso y quedó corregido.** El melanoma es menos de una cuarta parte de los casos y
   casi la mitad de las muertes: GLOBOCAN 2024 da 58 398 muertes por melanoma y 58 721 por el resto de los
   cánceres de piel. La fuente es `sung2026global` (GLOBOCAN 2024, publicado el 08/07/2026), que superó a
   `bray2024global` (GLOBOCAN 2022). Detalle en `refs_pendientes.md`. La nueva redacción del dato dice «la
   última estimación de GLOBOCAN, publicada en 2026, para el año 2024» (p27).

3. **Variabilidad interobservador: no se afirma una cifra de concordancia.** El párrafo se limita a que el
   desempeño depende de la experiencia y varía entre observadores, que es lo que sostiene
   `tschandl2019comparison`.

4. **Los capítulos llevan párrafo de apertura** (21/09/2026), ahora con el contenido de «Intro del capítulo»:
   qué trae y cómo se organiza, sin detalle técnico.

5. **El margen de mejora se focaliza en el 15 % de diagnósticos no localizados** (77/10/5; 10+5 = 15 %).

6. **Patrones de escritura automatizada** (guía §3): pasada de estilo al revisar la prosa. Se conserva el guion
   doble de «visión--lenguaje».

7. **«acá» se reemplaza por «en este trabajo»** o se reestructura.

8. **El «quinto tumor más frecuente» se verificó** contra la fact sheet de GLOBOCAN 2024 (IARC).

9. **Referencias anteriores a 2020** (`esteva2017dermatologistlevel`, `tschandl2019comparison`): van fechadas y
   presentadas como punto de partida, no como el desempeño alcanzable hoy (guía §6).

10. **H2 dejaba de decir «precisos»** (término reservado para *precision*): al eliminarse las hipótesis
    (D1) deja de aplicar; la regla se mantiene en PI2 y en los objetivos.

## Historial

- **2026-09-25.** LoRA sale de §1.1; Argentina se funde con generalización; SkinCaRe aclarado en Alcance;
  hipótesis «emergentes» pasan a «exploratorias»; apertura reescrita según el plan; organización en lista
  `description`. Esos cambios quedan superados por la revisión de abajo.

## Revisión del tutor (2026-09-28)

Origen: devolución del tutor sobre la versión del 2026-09-26 (`feedback/feedback_cap1_y_2.md`,
`REVISADO_TFG_Gaviola_cap1-2.pdf`) y decisiones D1 y D2 de `tareas_revision_cap1-2.md`.

**Qué cambia y por qué.**

| Cambio | Código | Motivo |
|---|---|---|
| Intro del capítulo: de resumen técnico a presentación de contenido y organización; se sacan codificador visual, LLM, fases, GPU y «sus dos partes» | I1, p27, T2 | «Las intros no llevan detalle técnico»; los términos aparecen donde se motivan |
| Contexto y motivación rehecho en 4 bloques con hilo conductor (problema clínico → limitaciones del diagnóstico y documentación → IA → problema de investigación); cada párrafo retoma el anterior | I2, A3, M1.1, M1.2, p28–p30 | «Parece un informe de una materia»: falta conexión entre párrafos |
| Dato de densidad de dermatólogos antes de la dermatoscopía; se elimina «El diagnóstico humano tampoco está resuelto»; dos retrasos (interpretación, documentación) → dos tareas | A3, M1.2, p28 | El hilo sigue la detección temprana y sus factores |
| El hito de 2017 deja de abrir el bloque de IA y pasa a ejemplo dentro de ¶7; se abre con «métodos computacionales, entre ellos redes neuronales» | A3 | «Eso no interesa en ese punto» |
| «Dos temas de trabajo aún abiertos» en un solo párrafo, y párrafo nuevo que conecta las dos tareas | I2, p29, M1.3, A10 | No basta resolverlas por separado |
| Se eliminan «En dermatología esos modelos ya existen» y el párrafo de hardware como eje; el hardware queda en una frase | p30, M1.10 | «Explicando cosas al voleo»; «es metodología» |
| Se eliminan la definición operativa de «detección» y el párrafo de las dos condiciones del reporte (queda en dos oraciones) | A1, I2 | Términos sin introducir; definición en Cap. 2/3 |
| Figura 1.1: se quita del capítulo y se propone trasladarla al Cap. 2 (§2.6) | p27, p35 | La intro no lleva figuras |
| Sección «Preguntas de investigación e hipótesis» → «Preguntas de investigación»; se eliminan H1–H6 | D1, I4, A2, M1.4, M1.5, p31 | Una hipótesis exige un análisis exhaustivo que el trabajo no plantea; formuladas a posteriori no son hipótesis; H3–H6 pasan a análisis de los Caps. 4 y 5 (M2) |
| PI1 y PI2 reformuladas, ligadas a métricas; PI2 separa fidelidad diagnóstica de calidad descriptiva | I3, M1.6, M1.7 | Más concretas |
| Objetivo general adaptado de la propuesta del tutor; se elimina el párrafo de discrepancias | D2, I5, M1.10, p32 | «Esto no va»; el objetivo ya menciona clasificación, reportes, fidelidad diagnóstica y hardware limitado |
| OE1–OE3 sin «entrenar»; todos «diseñar, implementar y evaluar» adaptando modelos pre-entrenados | I5, p32 | Nunca se creó un modelo nuevo |
| Tabla objetivo–pregunta–capítulo | I6, M1.11, M1.12 | Facilita seguir el hilo de la tesina |
| Se elimina la Sección 1.4 Alcance y delimitación; su contenido se reparte | I7, A1, A2, p32–p33 | «TODO ESTO NO VA»: datasets, fidelidad vs validez, cómputo y LoRA → Cap. 3; limitaciones → Cap. 6 |
| Organización del documento con «Este capítulo presenta…» | I8, p33, T2 | Sin «Responde la PI1» |

**Consecuencias en otros capítulos (M1–M4).** Cap. 3 recibe datasets, definición de detección, fidelidad
diagnóstica vs validez clínica, cómputo y LoRA. Cap. 6 recibe las limitaciones que estaban en Alcance.
Caps. 4, 5 y 6 dejan de hablar de hipótesis (l. 12, l. 13, l. 56–58). `\ref` que hay que actualizar:
`sec:intro_alcance` (eliminada), y las de `sec:intro_preguntas` que hablan de hipótesis.

**Lo que no cambia.** Las cifras verificadas de §1.1 (GLOBOCAN, NCI, densidad de dermatólogos, registro
argentino, historia clínica electrónica), las referencias que las sostienen y las decisiones de
terminología: «reporte» = informe clínico, «exactitud» y no «precisión», decimales con punto, voz
impersonal, sin «caveat», sin gerundio de consecuencia.

## Decisiones del autor sobre las preguntas abiertas (2026-09-28)

1. **Extensión:** no hay límite. El capítulo tiene la extensión que necesite; la guía §5 queda como
   referencia orientativa.
2. **OE3:** se elimina «utilidad práctica», porque no hubo evaluación con especialistas.
3. **PI1 y PI2:** se nombran familias de métricas y no la lista completa. Redacción aprobada:
   - **PI1.** ¿Cómo se compara el desempeño de modelos visión–lenguaje generales y especializados con el de
     clasificadores visuales supervisados en la clasificación de lesiones de piel y en la detección de melanoma?
   - **PI2.** ¿Qué fidelidad diagnóstica y qué calidad descriptiva alcanzan, por separado, los reportes que
     genera un VLM ajustado a partir de la imagen?
4. **«Fidelidad diagnóstica»:** se presenta con palabras en el bloque del problema de investigación (¶10–¶11),
   donde se dice que un reporte tiene que afirmar el diagnóstico correcto y describir la lesión que se ve. Así
   PI2 ya no usa un término sin presentar y no necesita glosa.
5. **Figura 1.1:** sale del Cap. 1 y pasa al Cap. 2, §2.6.2.
6. **Hipótesis:** se eliminan (D1).
7. **`arndt2017tethered` y `dinnes2018dermoscopy`:** se mantienen, con la aclaración de alcance en el texto.
