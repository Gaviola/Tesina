# Ficha del Capítulo 1 — Introducción

Contrato de contenido del capítulo. Cada sección declara su mensaje central, el esqueleto de
párrafos, las claves de cita que se usan y su extensión. Lo que no está acá no se escribe; lo que
falte se anota como pregunta abierta al final del borrador.

**Extensión total: 8–10 páginas.** El comentario del `.tex` decía 10–12 y la guía 6–8: ninguna de
las dos valía, porque el capítulo absorbió el antiguo capítulo de hipótesis y objetivos. Se fija
8–10 y se corrigen ambos archivos.

**Estado de la bibliografía: resuelto.** El encuadre clínico y epidemiológico con el que abre el
capítulo no tenía ni una referencia que lo sostuviera; se incorporaron ocho, verificadas contra la
página del editor y con DOI. El `.bib` pasó de 72 a 80 entradas y el capítulo se puede redactar
completo. El detalle de qué quedó incompleto en esas entradas está en `refs_pendientes.md`.

---

## 1.1 Contexto y motivación — `sec:intro_contexto`

**Mensaje central.** El diagnóstico dermatológico asistido exige dos tareas distintas —asignar una
categoría y describir la lesión— y los modelos visión–lenguaje prometen resolver ambas con un solo
modelo; este trabajo pone esa promesa a prueba con hardware accesible.

**Extensión: 3–3,5 páginas.** Es la sección más larga del capítulo y la única que argumenta.

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Carga del cáncer de piel y valor de la detección temprana del melanoma: incidencia, mortalidad y la diferencia de supervivencia según el estadio en que se detecta | El problema tiene magnitud y la detección temprana cambia el desenlace | `bray2024global`, `loria2020cutaneous` |
| 2 | Por qué el diagnóstico visual es difícil: la dermatoscopía mejora la exactitud respecto de la inspección a ojo desnudo pero exige entrenamiento, y entre observadores hay variabilidad apreciable | La tarea no es trivial ni está resuelta por la vía humana | `kittler2002diagnostic`, `vestergaard2008dermoscopy`, `tschandl2019comparison` |
| 3 | Acceso desigual al especialista y costo de tiempo del informe: la densidad de dermatólogos es muy dispar y la redacción del reporte consume tiempo clínico | Hay un problema de escala que justifica la asistencia automática | `freeman2026global`, `sinsky2016allocation` |
| 4 | Qué resolvió el aprendizaje profundo y qué no: desempeño comparable al de especialistas en condiciones controladas, pero la salida es una etiqueta y no un informe, y el desempeño cae en fototipos poco representados en los conjuntos públicos —motivo por el cual la validación externa se hace sobre HIBA, de población argentina | El estado actual deja dos huecos concretos: la forma de la salida y la generalización | `esteva2017dermatologistlevel`, `tschandl2019comparison`, `magalhaes2024systematic`, `kreouzi2024learning`, `jones2022intelligence`, `daneshjou2022disparities`, `groh2021neural`, `riccilara2023dataset` |
| 5 | Precisión del problema: las dos tareas (clasificar y describir), qué significa «detección» acá —tarea binaria de melanoma derivada de la clasificación, no localización ni segmentación— y por qué un reporte correcto exige a la vez diagnóstico acertado y descripción fiel de la imagen | Delimitación propia; es la definición que gobierna todo el documento | sin citas |
| 6 | La promesa de los modelos visión–lenguaje: el espacio común imagen–texto y los generativos multimodales, con los modelos dermatológicos que ya existen. Cierra enunciando por qué *parecen* resolver ambas tareas de una vez | Hay una razón técnica concreta para esperar que funcione | `radford2021learning`, `liu2023visual`, `li2023llavamed`, `zhou2023skingpt4`, `yan2025derm1m` |
| 7 | El eje transversal: hardware accesible. Qué significa una GPU de consumo de 12–24 GB, por qué eso decide qué modelos entran en el trabajo y qué hace viable el ajuste con LoRA | La restricción de cómputo es una decisión de diseño, no una limitación a disculpar | `hu2021lora`, `yilmaz2025resourceefficient` |

**Figura.** Ninguna en esta pasada. El esquema de §1.1 se deriva del diagrama del *pipeline* del
Capítulo 3 (`sec:met_pipeline`) una vez que ese exista, simplificándolo al planteo del problema: las
dos tareas y por dónde entra un modelo visión--lenguaje. Queda anotado como `\pendiente{}` en el
lugar donde irá, para que no se pierda. La sección se redacta sin depender de la figura.

**Cómo se citan las dos referencias anteriores a la ventana.** `esteva2017dermatologistlevel` y
`tschandl2019comparison` son de la era de las CNN, previa a los *transformers*. En el párrafo 4 van
fechadas y presentadas como el punto de partida —«ya en 2017 se mostró que…»—, nunca como el
desempeño alcanzable hoy. El criterio completo está en la guía, sección 6.

**Qué no va.** Nada de arquitecturas, fórmulas ni métricas: eso es el Capítulo 2. Ningún número de
resultado propio.

---

## 1.2 Preguntas de investigación e hipótesis — `sec:intro_preguntas`

**Mensaje central.** Dos preguntas, una por tarea, y seis hipótesis de las cuales solo dos son
previas al trabajo: las otras cuatro surgieron al refutarse las anteriores, y se presentan así a
propósito.

**Extensión: 2–2,5 páginas.**

El contenido sustantivo ya está redactado en el `\pendiente` actual y **se conserva textual**: PI1,
PI2, H1 y H2 como hipótesis de partida, y H3 a H6 con la indicación de qué resultado motivó cada
una. Lo que falta es el envoltorio:

1. **Párrafo de entrada** (antes de las PI): encadena con el cierre de §1.1 y explica que las dos
   preguntas se corresponden con las dos tareas, y por eso con las dos fases de la metodología.
2. **Párrafo puente** (entre las PI y las hipótesis): distingue hipótesis de partida de hipótesis
   emergentes.
3. **Párrafo de cierre** (después de H6): explicita que H1 y H3 se refutaron y que el trabajo se
   reorientó, y que presentarlas en orden de aparición —en lugar de reescribir la historia con las
   hipótesis que sí se cumplieron— es lo que permite leer los resultados como evidencia y no como
   confirmación. Remite a los capítulos de resultados sin adelantar números.

**Citas:** ninguna. Es contenido propio.

---

## 1.3 Objetivos — `sec:intro_objetivos`

**Mensaje central.** Un objetivo general y tres específicos, tomados del plan de trabajo aprobado.

**Extensión: 3/4 de página.**

El objetivo general y OE1–OE3 se conservan **textuales del plan de trabajo**, con una sola frase de
entrada que los presenta. No se reescriben para acomodarlos a lo que efectivamente se hizo.

**Tensión que hay que dejar planteada, no resolver acá.** OE2 dice «diseñar y entrenar un modelo
visión–lenguaje» y el trabajo no entrenó ninguno desde cero: ajustó modelos existentes con LoRA.
Lo mismo con «precisión diagnóstica» del objetivo general, que en el trabajo se concreta como
fidelidad diagnóstica del reporte. Acá no se resuelve: §1.4 ¶4 explica por qué no se pre-entrena un
modelo desde cero, y el balance de lo cumplido se hace en `sec:concl_objetivos`.

**Citas:** ninguna.

---

## 1.4 Alcance y delimitación — `sec:intro_alcance`

**Por qué existe esta sección.** En una tesina o un TFG es una sección convencional y esperable: el
lector necesita saber sobre qué se pronuncia el trabajo antes de leer los resultados. En un
artículo de revista no suele existir como sección propia —ahí las limitaciones van al final de la
discusión—, y de ahí viene la sensación de que sobra. Se conserva, pero delgada y en positivo:
enuncia **qué establece** el trabajo y sobre qué material, y deja lo que no establece en un cierre
breve. El análisis de limitaciones y amenazas a la validez no va acá: es `sec:disc_limitaciones`.

**Mensaje central.** El trabajo establece fidelidad diagnóstica sobre imágenes dermatoscópicas,
medida con métricas automáticas y con modelos que corren en hardware de consumo.

**Extensión: 1–1,5 páginas.** Se recortó respecto de la primera versión de esta ficha, que la
estiraba a 2 páginas metiéndole material que corresponde a otros capítulos.

| # | Párrafo | Contenido |
|---|---|---|
| 1 | Dominio y datos | HAM10000 dermatoscópico como conjunto principal, SkinCaRe como fuente de pares imagen--texto y HIBA para validación externa. Quedan fuera la histopatología y la fotografía clínica como dominio principal |
| 2 | Qué significa cada término acá | «Detección» es clasificación —la tarea binaria de melanoma se deriva de ella—, no localización ni segmentación. «Fidelidad diagnóstica» es la consistencia entre el diagnóstico que redacta el reporte y la etiqueta de referencia, medida sin texto de referencia |
| 3 | Qué establece y qué no | Las métricas automáticas establecen fidelidad diagnóstica; establecer validez clínica requiere que especialistas lean los reportes. Cierra con lo que el trabajo no es: no se desarrolla un producto de uso clínico ni se valida con pacientes |
| 4 | La restricción de cómputo como decisión de alcance | Solo entran modelos que corren en GPUs de consumo de 12--24 GB. De ahí se sigue que no se pre-entrena un modelo visión--lenguaje desde cero: el pre-entrenamiento exige cómputo y volumen de datos de otro orden, fuera del alcance de una tesina y del hardware disponible. Se ajustan modelos existentes con LoRA, que es lo que vuelve viable el ajuste en ese hardware |

**Redacción condicionada de ¶3.** La evaluación por especialistas está pendiente y puede concretarse
(la sección `sec:res_gen_especialistas` y el apéndice de la rúbrica están comentados, esperando).
El párrafo se redacta como afirmación metodológica —«las métricas automáticas establecen X;
establecer validez clínica requiere Y»—, que es verdadera se concrete o no. Si se concreta, se
agrega una oración; no hay que reescribir la sección. **No** se redacta como «este trabajo no
establece validez clínica», que obligaría a rehacerla.

**Qué se saca de esta sección.** La primera versión de esta ficha tenía un cuarto párrafo con todas
las desviaciones respecto del plan juntas, lo que reconstruía por la ventana la sección «Evolución
respecto del plan de trabajo» que se eliminó del capítulo, y con un tono defensivo. Cada desviación
va donde ocurre:

| Desviación | Dónde se explica |
|---|---|
| No se pre-entrena un VLM desde cero; se ajusta con LoRA | Acá, ¶4, porque es una decisión de alcance; el detalle técnico en `cp:metodos` |
| La comparación CNN--ViT--VLM se amplió a cuatro estrategias y después a un modelo visión--lenguaje dermatológico | `cp:metodos` como diseño, y `cp:res_clasif` como el resultado que lo motivó |
| Los «escenarios clínicos» de OE3 se concretan como robustez, calibración e incertidumbre | `sec:met_protocolo`, subsección de análisis complementarios, y las secciones de resultados correspondientes |
| A las métricas de similitud se agrega la consistencia diagnóstica | `sec:met_protocolo`, subsección de selección de modelos y criterio de decisión |
| Balance general de lo cumplido y lo desviado | `sec:concl_objetivos` |

**Citas:** `tschandl2018ham10000`, `shen2025skincare`, `riccilara2023dataset`, `hu2021lora`.

---

## 1.5 Organización del documento — `sec:intro_organizacion`

**Mensaje central.** Qué hay en cada uno de los siete capítulos.

**Extensión: 1/2 página.** Un párrafo corrido, no una lista: dos o tres renglones por capítulo,
con `\ref` a cada uno. Sin estimaciones de extensión en el cuerpo.

**Citas:** ninguna.

---

## Orden de redacción sugerido

Ya no hay dependencias bibliográficas, así que el orden es por dificultad: §1.1 es la única sección
que argumenta y conviene escribirla con la cabeza fresca; §1.2 y §1.3 son casi solo envoltorio
sobre texto que ya existe; §1.5 se escribe al final, cuando los títulos definitivos de los
capítulos ya no se muevan.

## Decisiones tomadas

1. **Variabilidad interobservador (§1.1 ¶2): se sostiene con lo que ya está en el `.bib`.** Kittler
   establece que la exactitud depende de la experiencia del examinador y Tschandl 2019 muestra la
   dispersión entre 511 lectores. No se agrega un estudio dedicado de concordancia, así que el
   párrafo **no puede afirmar una cifra de concordancia entre observadores**: se limita a que el
   desempeño depende de la experiencia y varía entre lectores, que es exactamente lo que esas dos
   referencias sostienen.
