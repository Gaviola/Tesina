# Tareas de la revisión del tutor: capítulos 1 y 2

Origen: devolución del tutor sobre la versión del 2026-09-26. Fuentes, en `Docs/TFG/feedback/` (no versionada):

- `feedback_cap1_y_2.md`: audios y mensajes. Se citan como **A5** (audio 5), **M1.4** (mensaje 4 del cap 1) y **M2.3** (mensaje 3 del cap 2).
- `REVISADO_TFG_Gaviola_cap1-2.pdf`: comentarios sobre el PDF. Se citan como **p27**, con la página del PDF.

Referencia de forma: `Docs/tesinamaglione_ejemplo.pdf`, una tesina terminada de la misma carrera. Hay que consultarla cuando haya dudas de estructura o de convención. De ahí salen, por ejemplo, la intro de capítulo que describe las secciones, la organización del documento con «En este capítulo se presenta…» y la motivación sin adelantar metodología.

Estado: `[ ]` pendiente · `[~]` en curso · `[x]` hecha · `[?]` requiere decisión.

---

## 0. Decisiones previas (bloquean tareas)

- [x] **D1. Hipótesis (A2, M1.4, M1.5, p31). Decisión (2026-09-28): se eliminan las seis hipótesis.** La introducción queda con preguntas de investigación y objetivos.
  - Motivo: el tutor exige que una hipótesis se compruebe con un análisis exhaustivo (búsqueda de hiperparámetros, configuraciones), y el trabajo no está planteado así. Los objetivos y las preguntas ya organizan el trabajo.
  - H3–H6 no se pierden. Los análisis que las motivaron (desbalance, especialización de dominio, cascada, incertidumbre) quedan en los Caps. 4 y 5 como preguntas o análisis que surgen de un resultado, sin llamarlos hipótesis ni presentarlos como refutados.
  - Se puede revisar cuando la introducción esté reescrita. Si el tutor pide hipótesis, se vuelve a la opción de conservar solo H1 y H2.
- [x] **D2. Objetivo general (M1.8–M1.10). Decisión: se adapta la redacción del tutor (M1.10) sin copiarla literal.** Tiene que mencionar la clasificación, la generación de reportes, la fidelidad diagnóstica y el hardware limitado. Con eso sobra el párrafo «Dos de esas formulaciones no coinciden…» (p32), que se elimina.
- [x] **D3. Estructura del Cap. 2 (M2.1). Decisión: se adoptan las diez secciones** (tarea C1).
- [x] **D4. Alcance del estado del arte (A15, A16). Decisión: del orden de 11 o 12 trabajos nuevos (número orientativo, no estricto), publicados entre 2020 y 2026,** repartidos entre los tres ejes (unos 4 por eje).
  - Se priorizan los que tienen texto completo accesible: arXiv, acceso abierto, PMC o PDF institucional. Un trabajo sin texto completo no entra, porque todo dato se verifica contra el PDF.
  - Los trabajos anteriores a 2020 solo quedan si son hitos imprescindibles (A15).
  - Circuito: se busca una lista de candidatos, el autor elige, se proponen en `refs_pendientes.md`, se descargan a `Papers/` y se leen antes de redactar.

## 1. Transversales (guía, siglas, formato)

- [x] **T1. Formato de siglas (M2.4–M2.7).** La primera aparición pasa a ser `Modelos visión–lenguaje (*Vision–Language Models*, VLM)`:
  - español primero;
  - inglés en cursiva;
  - la sigla en letra normal, dentro del mismo paréntesis y separada por coma.

  Hoy sale «Modelo Visión–Lenguaje (*Vision–Language Model*) (VLM)». Hay que cambiar el estilo de `\newacronym` en `06-Glossary.sty` o `10-Macros.sty` y reescribir `Matter/05-Acronyms.tex` para separar el español del inglés. Las entradas que hoy solo tienen inglés (CLIP, LoRA, PEFT, RAG, kNN, CoT, TTA, ECE) necesitan su nombre en español. Después de definida, la sigla se usa sola, sin repetir el significado. La lista de acrónimos tiene que usar exactamente las mismas denominaciones.
- [x] **T2. Guía de redacción: reglas nuevas.** Hay que agregar a `guia_redaccion.md`:
  - La intro de capítulo dice de qué trata el capítulo y cómo se organiza, sin detalle técnico y sin figuras, salvo que la figura sea imprescindible (p27, p35).
  - En la organización del documento, cada capítulo se describe con «Este capítulo presenta…» y no con «Responde la PI1» (p33).
  - Cada párrafo retoma el anterior y lleva al siguiente; no se enumera información suelta (A3, A7).
  - Cada concepto del marco teórico se justifica con una pregunta: ¿por qué el lector necesita esto para entender lo que se hizo o el resultado? El lector es general: tanto un informático como un dermatólogo (A7).
  - El marco teórico trata cuestiones teóricas: nada de particiones, datasets ni decisiones propias (p38, p43).
  - Ningún término se usa antes de haberlo presentado (A1).
  - Se evitan las líneas viudas y huérfanas reformulando la frase, y los espacios en blanco grandes (p59, p60).
  - Se agrega el formato de siglas de T1.
  - Se agrega la referencia a la tesina de ejemplo.
- [ ] **T3. Barrido final de viudas, huérfanas y huecos** en caps 1 y 2, después de las reescrituras (p59 «sesgo [76].», p60 hueco antes de 2.8.1).

## 2. Capítulo 1: Introducción

- [ ] **I1. Intro del capítulo (p27).** Reescribirla como presentación de lo que trae el capítulo y cómo está organizado. Sacar el resumen técnico: codificador visual, LLM, dos fases y GPU. Sacar también «sus dos partes» (p27: «¿el cuerpo tiene dos partes?»).
- [ ] **I2. Rehacer Contexto y motivación con hilo conductor (A3, M1.1–M1.3, p28–p30).** Estructura propuesta por el tutor:
  1. **Problema clínico y detección temprana.** Incidencia, mortalidad y supervivencia. Cierra con por qué hacen falta herramientas de apoyo al diagnóstico. El dato de GLOBOCAN se redacta como «la última estimación de GLOBOCAN, publicada en 2026, para el año 2024…» (p27). `sung2026global` ya es la más reciente, así que solo cambia la frase.
  2. **Limitaciones del diagnóstico y de la documentación.** Dentro de la detección temprana hay varios factores:
     - hay pocos especialistas: el dato de densidad de dermatólogos [5] va **antes**;
     - pocos clínicos tienen formación en dermatoscopía [3];
     - la lectura varía entre especialistas [4];
     - hay una carga de documentación [6].

     De esto salen dos retrasos, en la interpretación y en la documentación, que motivan dos tareas computacionales. Se elimina «El diagnóstico humano tampoco está resuelto» (p28: el diagnóstico siempre es humano). El párrafo de dermatoscopía se reescribe diciendo qué aporta al problema (p28).
  3. **Posibilidades y limitaciones de la IA.** Primero se dice que se aplicaron métodos computacionales y, entre ellos, redes neuronales. Después, CNN y transformers visuales para clasificación. Después, VLM para integrar imagen y texto. El hito de 2017 no abre la sección (A3).
  4. **Problema de investigación.** Limitaciones pendientes, generalización y reportes con diagnóstico fiel. Arranca con «A partir de lo anterior se identifican dos temas de trabajo aún abiertos» (p29), y los dos temas van en punto seguido, no en párrafos aparte (p29). Agregar un párrafo que **conecte las dos tareas** y explique por qué no basta con resolverlas por separado (M1.3).
  - Sacar el párrafo «En dermatología esos modelos ya existen» (p30: «explicando cosas al voleo») y el del hardware como eje (p30: «es metodología»). La restricción de hardware puede quedar en una frase dentro del problema o del objetivo (M1.10), sin detalle de GB ni configuraciones.
  - Sacar la definición operativa de «detección» (binaria derivada de la multiclase) y el párrafo sobre las dos condiciones de un reporte correcto, o reducirlos a lo que el lector necesita. La definición precisa va en Cap. 2 o Cap. 3 (A1).
  - Revisar si la Figura 1.1 sigue teniendo sentido en la nueva motivación.
- [ ] **I3. Preguntas de investigación (M1.6, M1.7).** Hacerlas concretas y ligadas a las métricas que se usan después:
  - **PI1:** comparar el desempeño de VLM generales y especializados con clasificadores visuales supervisados, incluida la detección de melanoma.
  - **PI2:** separar la **fidelidad diagnóstica** de la **calidad descriptiva** del texto.
- [ ] **I4. Eliminar las hipótesis (D1).**
  - La Sección 1.2 pasa a llamarse «Preguntas de investigación» y conserva solo PI1 y PI2 (I3).
  - Se eliminan H1–H6 y todo el texto que las rodea: los estatus, «Se plantea tras refutarse…», «Su respaldo es por eso más débil…» y el párrafo sobre el orden de formulación.
  - Buscar con `grep` las referencias a H1–H6 en los demás capítulos y en las fichas; ver M2.
- [ ] **I5. Objetivos** según D2: adaptar la redacción del tutor (M1.10).
  - Sacar «Los objetivos se enuncian tal como fueron formulados…» y el párrafo de las discrepancias (p32: «Esto no va»).
  - Opcional: agregar texto que describa cada objetivo específico con más detalle (p32).
  - OE1 y OE2: el tutor señala que en todos los casos se diseñó, implementó y evaluó, y que nunca se creó un modelo nuevo (p32). La redacción no tiene que sugerir que se entrenó desde cero.
- [ ] **I6. Tabla objetivos ↔ preguntas ↔ capítulos (M1.11, M1.12).** Hacer una tabla breve que relacione cada objetivo específico con su pregunta y con el capítulo donde se evalúa. Solo tiene sentido si el resto queda ordenado y autocontenido.
- [ ] **I7. Eliminar la Sección 1.4, Alcance y delimitación (A1, p32–p33: «TODO ESTO NO VA»).** Su contenido va a donde corresponde: datasets, fidelidad diagnóstica vs validez clínica, cómputo y LoRA al Cap. 3 (ver tarea M1); limitaciones al Cap. 6.
- [ ] **I8. Organización del documento (p33).** Cada capítulo se describe como «Este capítulo presenta…». Por ejemplo: «El capítulo presenta la metodología de trabajo, los conjuntos…» y «Este capítulo presenta la comparación de estrategias…». Sin «Responde la PI1».

## 3. Capítulo 2: Marco teórico, estructura

- [ ] **C1. Reorganizar según M2.1** (D3):
  1. Fundamentos del aprendizaje profundo
  2. Transformers y mecanismos de atención
  3. Aprendizaje profundo para clasificación visual
  4. Modelos de lenguaje y adaptación eficiente
  5. Modelos visión–lenguaje
  6. **Generación de reportes y recuperación de información** (nueva sección, ver G1–G3)
  7. **Incertidumbre y predicción selectiva** (nueva, ver G4)
  8. Evaluación de modelos (reordenada, ver E1)
  9. Sesgo, robustez y generalización
  10. Estado del arte y posicionamiento del trabajo

  Actualizar la ficha `fichas/02-marco-teorico.md` antes de reescribir.
- [ ] **C2. Intro del capítulo (p35).**
  - Hablar del contenido del capítulo, no de detalles técnicos.
  - Sacar la Figura 2.1 (mapa sobre el pipeline): las intros no llevan figuras (p35), y el marco no se presenta sobre el pipeline sino con los conceptos que después lo sostienen (p59, A11).
  - Evaluar si `Figures/Capitulos/02-mapa-capitulo.tex` se reutiliza en el Cap. 3.
- [ ] **C3. Apertura de 2.1 (p35).** Entrar directamente al aprendizaje profundo, sin «Esta sección presenta cómo una red neuronal produce…».
- [ ] **C4. Transiciones entre conceptos y secciones (A7, A8).** Cada sección de 2.2 a 2.5 cierra con un párrafo que relaciona sus arquitecturas con las de la sección siguiente. El recorrido es: redes neuronales → MLP → redes profundas → *deep learning* → modelos que se desarrollaron con el tiempo → LLM → VLM.
- [ ] **C5. Recortar el MLP y eliminar las redes recurrentes (A5).** Conservar solo las ecuaciones y definiciones necesarias para los experimentos.
- [ ] **C6. Disolver 2.1.5, Familias de redes según la estructura de la entrada (A6).** Resumirla en uno o dos párrafos que sirvan de transición hacia CNN y Transformers. El gradiente que se desvanece o explota se conserva brevemente, porque justifica las conexiones residuales. Las RNN y las LSTM salen. Si hace falta, queda una frase sobre la limitación secuencial que motiva la atención.

## 4. Capítulo 2: contenido

### Fundamentos y visión

- [ ] **F1. Transferencia de aprendizaje (A5):** desarrollarla más. Explicar qué se transfiere, por qué funciona con pocos datos médicos, y la diferencia entre extracción de características y ajuste fino.
- [ ] **F2. Ajuste fino (A5):** desarrollarlo como concepto propio (completo o parcial, tasa de aprendizaje menor, riesgo de olvido) y conectarlo con LoRA en 2.4.
- [ ] **F3. Balance de clases (A5, p43).**
  - Tratarlo como tema teórico completo: remuestreo, pesos por clase, *focal loss*, métricas sensibles al desbalance y ajuste de umbral.
  - Sacar el párrafo sobre la distribución de HAM10000 (p43: «va en el cap 3»).
  - Revisar que queden cubiertos los enfoques que se usan en el Cap. 4.
- [ ] **F4. Generalización (A5, p38).**
  - Ampliar un poco.
  - Sacar la mención a la partición de HAM10000 (p38: «no hables de cosas prácticas»). En su lugar va el principio general: casos o pacientes repetidos entre particiones inflan la estimación.
- [ ] **F5. CNN y ViT como *baseline* (A9).** En las secciones de CNN y ViT, decir que ambas familias son la referencia contra la que se evalúa el desempeño de los modelos multimodales.

### Generación de reportes (hoy subrepresentada, A10)

- [ ] **G1. Nueva sección de generación de reportes con tres ejes (A11):**
  1. generar una descripción visual a partir de la imagen;
  2. incorporar información diagnóstica al texto;
  3. tratar las predicciones inciertas para no afirmar diagnósticos que la evidencia no justifica.

  Tiene que tener un peso comparable al de clasificación. El Cap. 1 presenta dos tareas y el marco hoy casi solo trata una.
- [ ] **G2. Alucinaciones y *hedging* (A11).** Ya se mencionan, pero hay que desarrollarlos: contexto, consecuencias, ventajas y desventajas de cada comportamiento, y qué pasa si no se analizan.
- [ ] **G3. Separar tres mecanismos de recuperación y decisión (A12, A13).** Presentar por separado:
  - **a)** recuperar documentos para condicionar la generación (RAG en sentido original);
  - **b)** recuperar imágenes similares como evidencia visual (kNN sobre embeddings DermLIP);
  - **c)** usar la concordancia entre predicciones para decidir (acuerdo entre Swin y kNN).

  Cerrar explicando qué aportaría integrarlos, sin adelantar la implementación.

  **Hay que corregir la fórmula de RAG (A13).** La ecuación `eq:marco_rag`, de Lewis, marginaliza sobre documentos recuperados con un recuperador entrenado. La implementación (`Codigo/scripts/build_rag_index.py`, `generate_report.py`) hace otra cosa: recupera los k=3 casos de entrenamiento más parecidos por coseno sobre embeddings de DermLIP y pega su diagnóstico y su localización como texto en el *prompt*. No marginaliza, no entrena el recuperador y no recupera documentos. El texto tiene que decir explícitamente que el trabajo usa una variante de condicionamiento por contexto, o bien reemplazar la ecuación por una que describa eso.
- [ ] **G4. Nueva sección de incertidumbre y predicción selectiva (A11).** Tiene que cubrir:
  - la predicción selectiva y la abstención;
  - las tres salidas posibles: afirmar un diagnóstico, ofrecer diferenciales o derivar si no se alcanza la confianza;
  - la relación con la calibración.

  Así la cascada del Cap. 3 aparece como consecuencia del marco y no como algo hecho «porque sí». Necesita referencias sobre predicción selectiva y abstención (por ejemplo, Geifman y El-Yaniv 2017, a verificar), que se proponen en `refs_pendientes.md`.

### Evaluación

- [ ] **E1. Reordenar las métricas según lo que evalúan (A14):**
  - **Clasificación:** matriz de confusión primero, después exactitud balanceada, F1 macro, sensibilidad, especificidad y AUC.
  - **Generación:** métricas textuales, diagnósticas (entidades) y descriptivas.
  - **Transversal:** calibración, inferencia estadística, robustez e interpretabilidad.

  Verificar que cada métrica presentada se use en los resultados; si no se usa, sale.

## 5. Estado del arte (A15, A16, p59–p60)

- [ ] **S1. Sacar la Tabla 2.1 de datasets y la descripción de los conjuntos (A16).** Los datasets se mencionan en una línea («HAM10000, un conjunto de referencia muy utilizado») y se detallan en el Cap. 3. En p60 el tutor pide escribir «del conjunto de datos HAM10000», no solo el nombre.
- [ ] **S2. Intro de la sección y de cada subsección (p59, p60).**
  - No presentar las líneas «en el orden del pipeline» (p59).
  - Agregar una intro a cada subsección (p60).
  - No abrir con «La línea tiene dos hitos anteriores a 2020»; abrir con «En 2017…» o con otra frase inicial (p60).
- [ ] **S3. Sumar del orden de 11 o 12 trabajos (orientativo) de 2020 a 2026, con texto completo accesible (A15, A16, D4).** Los ejes son clasificación de lesiones, VLM en dermatología y generación de reportes, con unos 4 trabajos nuevos por eje. Se suman a los que ya se citan y dejan cada eje en 6 u 8 trabajos. Los hitos anteriores se descartan salvo que sean imprescindibles.
  - **S3a.** Armar una lista de candidatos por eje, con año, venue, acceso y por qué entra. La elige el autor.
  - **S3b.** Proponer los elegidos en `refs_pendientes.md` y descargarlos a `Papers/`.
  - **S3c.** Hacer una ficha de lectura por trabajo con los puntos de abajo, verificada contra el PDF.

  Por cada trabajo hay que cubrir:
  - objetivo;
  - problema o enfoque puntual;
  - método y novedad de la arquitectura o del enfoque;
  - datos;
  - métricas;
  - contra qué trabajos del estado del arte se comparó;
  - resultados;
  - si hubo evaluación con expertos;
  - limitaciones que reconocen los autores.

  Las referencias nuevas van a `refs_pendientes.md` y se verifican contra el PDF.
- [ ] **S4. Síntesis al final de cada subsección (A15, A16).** Resumir cómo cada familia de enfoques ataca el problema, qué aporta la línea y qué queda sin resolver. Comparar problema, arquitecturas, datos, protocolo y limitaciones.
- [ ] **S5. Tabla comparativa de trabajos (A16).** Una tabla por eje o una tabla general, con trabajo, año, arquitectura, datos, métricas, resultado principal y evaluación con expertos. La Tabla 2.2 de generadores puede ser el punto de partida.
- [ ] **S6. Posicionamiento (A16, M2.1 punto 10).** Cerrar mostrando que el pipeline y los análisis del trabajo se desprenden de los huecos que dejó la revisión. La novedad es el pipeline, no una réplica.

## 6. Consecuencias en otros capítulos

- [ ] **M1. Cap. 3 recibe:**
  - la Tabla 2.1 de datasets (S1);
  - la distribución de HAM10000 (F3);
  - lo de la partición de HAM10000 (F4);
  - de la Sección 1.4: los datasets, la definición operativa de detección, fidelidad diagnóstica vs validez clínica, y cómputo y LoRA (I7);
  - posiblemente el mapa del pipeline (C2).
- [ ] **M2. Caps. 4 y 5 absorben los análisis de H3–H6** (desbalance, especialización de dominio, cascada, incertidumbre) como preguntas que surgen de un resultado, sin llamarlos hipótesis (D1). Hay referencias a hipótesis en:
  - los `\pendiente` de apertura de `04-Resultados-Clasificacion.tex` (l. 12) y `05-Resultados-Generacion.tex` (l. 13);
  - `06-Discusion.tex` (l. 56), donde la discusión responde hipótesis por hipótesis;
  - `fichas/01-introduccion.md`.
- [ ] **M3. Cap. 6 recibe** las limitaciones que estaban en Alcance (I7).
- [ ] **M4. Actualizar las referencias cruzadas** (`\ref`) que apuntan a secciones movidas o eliminadas: 1.4, 2.1.5, las 2.6.x que se renumeran y la Tabla 2.1.

## Orden sugerido

1. S3a (lista de candidatos). Se puede ir leyendo en paralelo con el resto.
2. T1 y T2: sirven de base para todo lo demás.
3. Ficha del Cap. 2 (C1).
4. Cap. 1 (I1–I8).
5. Cap. 2: estructura, fundamentos, reportes, incertidumbre y evaluación (C2–C6, F, G, E).
6. Estado del arte (S1–S6). Es lo más largo, porque requiere buscar y leer papers.
7. M1–M4 y el barrido T3.
