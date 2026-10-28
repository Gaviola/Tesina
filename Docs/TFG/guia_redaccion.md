# Guía de redacción de la tesina

Contrato único para la redacción del documento final. Quien escriba una sección —el autor o un
agente— lee esta guía antes de escribir la primera línea, y todo lo que produzca se evalúa contra
ella. Las decisiones acá fijadas valen para todos los capítulos: si algo hay que cambiar, se cambia
en este archivo y no sección por sección.

## 1. Circuito de trabajo

### Un archivo por sección

Desde el 10/10/2026 cada capítulo es una carpeta y cada `\section` un archivo, para revisar los cambios
sección por sección:

| Qué | Dónde |
|---|---|
| Encabezado del capítulo (`\chapter`, comentarios de extensión y fuentes, introducción) y los `\input` de sus secciones | `Chapters/<NN-Capitulo>/00-capitulo.tex` (lo trae `tesina.tex` con `\include`) |
| Una sección, con sus subsecciones | `Chapters/<NN-Capitulo>/<NN-seccion>.tex` |
| Diagramas del capítulo | `Figures/Capitulos/<NN-Capitulo>/<nombre>.tex` |
| Ficha general del capítulo (mensaje, estructura, decisiones, historial) | `fichas/<nn-capitulo>/00-capitulo.md` |
| Ficha de una sección (hilo conductor y plan) | `fichas/<nn-capitulo>/<NN-seccion>.md`, con el mismo nombre que su `.tex` |
| Apéndices | `Chapters/Apendices/<letra>-<nombre>.tex`, uno por apéndice |

Una sección nueva se agrega creando su archivo y su `\input` en `00-capitulo.tex`; si cambia el orden de las
secciones, se renombran los archivos para que el prefijo numérico siga el orden del índice.

### Etapas

Cada sección del documento pasa por cuatro etapas, **de a una sección por vez**. No se saltea ninguna.

| Etapa | Qué se produce | Quién decide |
|---|---|---|
| 1. Ficha | `fichas/<nn-capitulo>/<NN-seccion>.md`: mensaje central, **hilo conductor** (ver abajo), claves de cita, figuras y extensión | El autor aprueba antes de que se escriba prosa |
| 2. Redacción | La prosa se escribe **en el `.tex` de la sección**, siguiendo el hilo de la ficha, y se compila | Quien redacta |
| 3. Pasada de estilo | La sección se relee contra la lista de control (§3, «Lista de control») y se corrige | Quien redacta |
| 4. Cierre | Un commit por sección en la rama del capítulo; el autor la revisa sobre el diff y la envía al tutor por separado | El autor |

Sin ficha aprobada no se redacta. La ficha es el punto de control real: es más rápido corregir un
esqueleto de una página que treinta páginas de prosa ajena. La sección siguiente no se empieza hasta que
la anterior está cerrada, porque lo que una define la otra solo lo retoma (§3, «Estructura y progresión»).

**Cada sección se escribe conociendo las anteriores del capítulo** (decisión del autor, 10/10/2026). Antes
de armar la ficha de una sección se leen el `.tex` de las secciones anteriores del mismo capítulo y el
«Deja instalado» y el «Se definen acá» de sus fichas, además del hilo del capítulo en `00-capitulo.md`.
El «Viene de» de la ficha nueva cita lo que dejó la sección anterior, la primera oración de la sección lo
retoma, y lo que ya se definió antes solo se nombra con `\ref`. Si al escribir aparece algo que habría que
cambiar en una sección ya cerrada, se anota como pregunta y no se toca sin acuerdo.
Primero se resuelven la organización y la coherencia (etapas 1 y 2) y después la gramática y el estilo
(etapa 3), como pidió el tutor (revisión del 09/10/2026).

### Hilo conductor en la ficha

La ficha de cada sección empieza con un esqueleto que muestra cómo se encadenan los párrafos, antes de
cualquier tabla de contenidos. Es la herramienta para que el texto sea un desarrollo argumentativo y no una
enumeración de conceptos (tutor, 09/10/2026, Audio 3). Formato:

```
## Hilo conductor

Pregunta que responde la sección: ¿…?
Viene de: lo que dejó instalado la sección anterior (concepto o limitación).
Deja instalado: lo que la sección siguiente va a usar.

P1  [idea central del párrafo]                         función: define | justifica | interpreta | limita
    ↓ relación: necesidad — «Para usar estas representaciones en una clasificación, hace falta…»
P2  [idea central]                                     función: …
    ↓ relación: consecuencia — «Por lo tanto…»
P3  …
→ Transición a la sección siguiente: «…» (una o dos oraciones)

Se definen acá (y no se vuelven a definir): término (*English term*), …
Se retoman de antes (solo se nombran, con \ref): …
Extensión: N párrafos, ~N páginas.
```

Cada flecha nombra la relación que une un párrafo con el siguiente (causa, consecuencia, necesidad, contraste,
ejemplo, ampliación). Si entre dos párrafos no se puede escribir la flecha, falta un párrafo, sobra uno o
están en el orden equivocado. La columna «función» aplica el criterio del marco teórico (§3, «Cada concepto
cumple una función»): un párrafo sin función se borra.

**No hay borradores en archivos aparte.** El circuito tuvo una etapa intermedia que escribía la
sección en `borradores/<label>.tex` antes de tocar el capítulo, y se eliminó: apenas la sección
quedaba integrada existían dos copias del mismo texto, y la copia vieja empezaba a divergir en
cuanto el autor corregía el capítulo. El capítulo es la única fuente de verdad. Lo que la etapa
intermedia protegía se consigue igual: el capítulo nunca queda roto porque la sección sin escribir
tiene su `\pendiente` y compila, y la revisión se hace sobre el diff del commit, que además muestra
las dos versiones juntas.

## 2. Reglas para quien redacta

1. **La ficha es el alcance.** No se agregan secciones, subsecciones ni temas que la ficha no
   incluya. Lo que parezca faltar se anota como pregunta abierta al entregar la sección; no se
   escribe en el `.tex`.
2. **No se inventa evidencia.** Ningún número, resultado, porcentaje o afirmación empírica puede
   aparecer si no está en las fuentes indicadas en la ficha. Si falta un dato, se deja la marca
   `\pendiente{}` con lo que haría falta medir.
3. **No se inventan referencias.** Solo se citan claves que ya existen en
   `Bibliography/Bibliography.bib` (ver sección 6).
4. **Se toca la sección y nada más.** La redacción de una sección modifica su `.tex` y, si la ficha
   pide una figura, el archivo de esa figura en `Figures/Capitulos/<NN-Capitulo>/`. Ni `tesina.tex`,
   ni otras secciones, ni el `.bib`. Si hiciera falta tocar un archivo compartido (por ejemplo, para
   quitar de otra sección una definición repetida), se reporta aparte y se justifica.
5. **Toda decisión se reporta.** Al terminar, la sección se entrega con: claves citadas,
   afirmaciones sin respaldo, decisiones tomadas por cuenta propia y preguntas abiertas. Las que
   condicionan lo que se escriba después se anotan en «Decisiones tomadas» de la ficha, que es lo
   que sobrevive a la conversación.

## 3. Voz y estilo

- **Impersonal y descriptiva.** «Se evalúan cuatro arquitecturas», no «evaluamos» ni «el autor
  evalúa». Nunca se habla del autor en tercera persona.
- **Tiempo verbal con función fija** (tutor, 21/10/2026). El presente describe cómo funciona el método y
  el *pipeline* («el clasificador fija el diagnóstico», «se evalúa con la sensibilidad macro»), y es el
  tiempo de la metodología. El pasado queda para los procedimientos experimentales ya realizados («la
  búsqueda se hizo sobre Swin-Tiny», «la variante se eligió en un piloto»). No se escribe «se construyó
  cada componente y se evaluó» donde se describe el método.
- **Construcciones variadas.** «Se evalúa», «se compara», «se usa», «la sección presenta» son correctas,
  pero repetidas en párrafos seguidos vuelven monótono el texto. Se alternan con otras construcciones
  («con este propósito se aplica…», «la comparación incluye…») sin forzar sinónimos imprecisos.
- **El texto es propio.** No se escribe meta-lenguaje sobre el documento ni sobre la plantilla
  («este capítulo fue elaborado a partir de…», «material no desarrollado por el autor»).
- **Párrafos de 4 a 8 líneas**, uno por idea, encadenados. Se evitan las listas de viñetas en el
  cuerpo salvo cuando enumeran elementos realmente paralelos (clases, métricas, configuraciones).
- **Cada sección abre directamente con su contenido** y cierra con lo que deja instalado para la
  siguiente. No se anuncia lo que se va a hacer («en esta sección se describirá…», «esta sección
  presenta cómo…»): se hace. La excepción es la introducción de cada capítulo, que sí describe qué
  contiene el capítulo y cómo se organiza (ver «Estructura y progresión»).
- **Nada de relleno.** Sin frases que anuncian lo que viene, sin recapitulaciones de lo ya dicho, sin
  adjetivos de énfasis («notablemente», «sumamente»). Una oración que relaciona un concepto con el
  anterior **no es relleno**: es la transición que el lector necesita (ver «Cohesión y progresión»).
- **Español neutro formal.** Documentación y documento en español; el código y los nombres de
  variables, en inglés.
- **Los términos en inglés se usan cuando son los corrientes en el área.** *Pipeline*, *array*,
  *prompt*, *zero-shot*, *linear probe*, *grounding*, *hedging*, *bootstrap*, *trade-off*,
  *image captioning*, *kernel*, *greedy decoding*, *beam search*, *sampling*, *top-k*, *top-p* o
  *nucleus sampling* no tienen equivalente castellano instalado; traducirlos («búsqueda codiciosa»,
  «muestreo de núcleo») dificulta la lectura en lugar de facilitarla, así que se usan tal cual. Lo
  mismo vale para calcos de expresiones: «la masa de probabilidad acumulada» se reformula como «la
  probabilidad acumulada». Se prefiere el castellano cuando ya es de uso
  corriente («ajuste fino», «conjunto de datos», «aprendizaje profundo», «atención multicabezal»).
- **Término en castellano con el inglés entre paréntesis la primera vez.** Muchos lectores conocen
  los conceptos del área por su nombre en inglés, así que la primera aparición en el documento de un
  término traducido lleva el original en cursiva: «sobreajuste (*overfitting*)», «aumento de datos
  (*data augmentation*)», «parches (*patches*)», «atención multicabezal (*multi-head attention*)»,
  «fuga de información (*data leakage*)». Vale para todo término que se use habitualmente en inglés en
  el área, no solo para las siglas (tutor, 09/10/2026). Si el término se definió en otro capítulo y el
  lector lo conoce sobre todo en inglés, su primera aparición en el capítulo nuevo repite el original
  entre paréntesis junto al `\ref`: «voto suave (*soft voting*; Sección~\ref{…})» (tutor, 21/10/2026).
- **Cursiva la primera vez en cada capítulo** con `\emph{}`; después, redonda. En títulos de
  sección y en los índices, siempre redonda. Un término que aparece cincuenta veces en cursiva es
  ruido tipográfico.
- **Los nombres de conjuntos de datos van siempre en cursiva** (`\emph{ImageNet}`, `\emph{HAM10000}`,
  `\emph{Derm1M}`), en el texto, los epígrafes y las tablas, como el título de una obra (pedido del tutor,
  09/10/2026). En títulos de sección e índices, redonda. Los nombres de modelos (DermLIP, LLaVA) y las
  siglas van en redonda. Se aplica al reescribir cada sección.
- **Las siglas se definen una sola vez en el documento.** La primera aparición va con `\gls{}`, que
  escribe el nombre en español, y entre paréntesis el nombre en inglés en cursiva y la sigla en
  redonda, separados por coma: «red neuronal convolucional (*Convolutional Neural Network*, CNN)».
  De ahí en más va la sigla sola (VLM, LoRA, RAG, ECE), sin repetir su significado. El formato lo
  arma `Configurations/06-Glossary.sty` y las entradas se declaran con `\acronimo` (sección 4,
  «Acrónimos»); no se escribe a mano.
- **Los dos puntos y el punto y coma, con moderación.** Los dos puntos anuncian lo que viene después:
  una enumeración, una definición, un nombre, un ejemplo. No son un conector entre oraciones: si lo que
  sigue es una explicación o una continuación del pensamiento, va punto y seguido, coma o
  subordinación. El punto y coma tampoco encadena oraciones completas; en ese caso se prefiere el punto
  y seguido.
- **Verbos literales.** Para las operaciones técnicas se usa el verbo que las nombra, no uno figurado:
  una métrica se «evalúa» (no se «juzga»), dos valores «se separan» (no «se apartan»), un modelo
  «acierta» las imágenes de una clase (no las «encuentra»).
- **Sin elipsis nominales.** «Los modelos de solo decodificador», no «la de solo decodificador»: se
  repite el sustantivo o se reestructura la oración en lugar de dejarlo implícito.
- **Sin gerundio de consecuencia.** «El cálculo se paraleliza y aprovecha mejor el hardware», no «se
  paraleliza permitiendo un cálculo más eficiente».
- **Afirmaciones medidas.** No se escribe «el primero», «la prueba recomendada» o «el supuesto es
  débil» si la fuente no lo dice así. Cuando la afirmación es de los autores del trabajo citado, se les
  atribuye («que sus autores presentan como el primer conjunto público…»). Las capacidades y las
  limitaciones de los modelos se enuncian con su alcance («en los trabajos revisados», «sobre
  imágenes dermatoscópicas», «suele»), no como verdades generales, y se prefieren las palabras de
  intensidad moderada: «dificultades» o «limitaciones» antes que «problemas».
- **Sin futurología.** Las conclusiones describen lo medido. Lo que no se evaluó se enuncia como limitación o trabajo
  futuro, no como un beneficio esperable: «un generador más grande mejoraría la descripción» solo si hay evidencia;
  si no, se escribe «no se evaluó» o «queda como trabajo futuro». Las implicaciones se derivan de los resultados, no
  de lo que podría pasar con más datos, más cómputo o una evaluación que no se hizo.
- **Las decisiones se explican desde los objetivos.** «Como uno de los objetivos es ejecutar todo en una
  GPU de consumo, los modelos se adaptan con LoRA», no «se adaptan con LoRA, y por eso se ejecutan en una
  GPU de consumo». La causalidad sigue el orden en que se tomó la decisión.
- **Alternativas paralelas en lista.** Cuando un párrafo enumera opciones que se comparan (estrategias de
  pérdida, variantes de un método) o varias técnicas de una misma familia (las de regularización), van en
  una lista (`enumerate` o `itemize`) con el nombre de cada una en negrita al comienzo, precedida por una
  oración que dice qué tienen en común. No se encadenan cuatro técnicas en un mismo párrafo.

### Cohesión y progresión del texto

Revisión del tutor del 09/10/2026: el texto se leía como una enumeración de conceptos y no como un
desarrollo argumentativo. Los párrafos acumulaban ideas de temas distintos, las primeras oraciones no
decían de qué trataba el párrafo y se pasaba de un tema al siguiente sin transición. Estas reglas
prevalecen sobre «Concisión»: **la concisión se logra sacando temas, no comprimiendo los que quedan**.

- **La primera oración de un párrafo lo orienta.** Dice de qué trata el párrafo y, cuando hace falta, cómo
  se relaciona con el anterior. No abre con un detalle, una cifra, un condicional ni el nombre de una
  técnica que el lector todavía no conoce. «Si imágenes de una misma lesión caen en dos particiones…» se
  reescribe como «Una situación a evitar es que imágenes de una misma lesión…»; «El aumento de datos
  aplica…», después de un párrafo sobre regularización, necesita antes una oración que diga por qué
  aparece.
- **Primero el problema, después la técnica.** Antes de nombrar una técnica (RandAugment, AdamW, el
  TTA) se dice qué dificultad resuelve y qué tipo de cosa es («un método de aumento de datos que…»), y
  se cita su fuente. Un nombre propio que aparece sin presentación deja al lector preguntándose de
  dónde viene.
- **Oraciones autocontenidas que se encadenan.** Cada oración dice una cosa completa y define algo que la
  siguiente usa. Modelo del tutor para las particiones: «Para estimar este error se utilizan datos que no
  se emplearon durante el ajuste del modelo. Con este propósito, el conjunto de datos se divide en tres
  particiones disjuntas: entrenamiento, validación y prueba. El conjunto de entrenamiento se usa para
  ajustar los parámetros, mientras que el de validación permite seleccionar las configuraciones y los
  hiperparámetros. Finalmente, el de prueba se emplea para evaluar el rendimiento sobre datos no
  utilizados durante el desarrollo…».
- **Los conceptos se construyen unos sobre otros.** La explicación avanza de lo que el lector ya tiene a
  lo nuevo, y cada concepto se apoya en los anteriores. Ejemplo del tutor: la red recibe los datos de
  entrada → los transforma y produce un valor por cada clase posible (y se dice qué es una clase) → como
  esos valores no son probabilidades, la softmax los lleva al rango 0–1 con suma uno → la entropía
  cruzada compara esas probabilidades con la etiqueta. Al terminar, el lector entiende cómo funciona la
  red, no una lista de definiciones.
- **Las relaciones entre oraciones se dicen con conectores.** Cuando dos afirmaciones tienen una relación
  de causa, consecuencia, contraste o finalidad, se la explicita en lugar de yuxtaponerlas. Conectores
  sencillos, uno por relación, sin construcciones rebuscadas:

  | Relación | Conectores |
  |---|---|
  | Causa | porque, ya que, dado que, debido a |
  | Consecuencia | por lo tanto, en consecuencia, por ello, de este modo, así |
  | Contraste | sin embargo, en cambio, no obstante, a diferencia de |
  | Finalidad | para ello, con este propósito, a fin de |
  | Necesidad | para…, es necesario…; esto requiere… |
  | Adición y orden | además, asimismo, por otra parte, en primer lugar, finalmente |
  | Ejemplo y reformulación | por ejemplo, en particular, es decir |

  El registro es el de un estudiante que termina la carrera: claro y formal, no ampuloso. Si una oración
  necesita tres subordinadas para decir algo simple, se parte en dos.
- **Un párrafo, una idea central.** Si un párrafo reúne varios conceptos, resultados o antecedentes, se
  divide en unidades temáticas o se pasa a una lista (ver «Alternativas paralelas en lista»). **No se usan
  títulos de párrafo** (`\paragraph{}`): cortan el hilo y dificultan la lectura (decisión del autor,
  10/10/2026). Cuando un párrafo introduce un tema nuevo, lo marca el nombre del concepto en negrita donde se
  define, con el inglés entre paréntesis: «La **regularización** (*regularization*) busca…».
- **Cada párrafo cierra su idea.** La última oración completa la idea central y, cuando corresponde, la
  relaciona con el argumento de la sección o con el trabajo («…y por eso las particiones se arman por
  lesión»), sin recapitular.
- **No se salta de tema de tropezón.** Entre dos secciones o subsecciones hay siempre una oración que
  diga por qué el tema siguiente hace falta (la limitación que deja el anterior, la pregunta que
  queda abierta). Vale también para el comienzo de una sección: su primer párrafo retoma lo que dejó la
  anterior.

### Léxico preciso

- **Sin adjetivos de grado sin referencia.** «Valores altos», «exactitudes altas», «bajo costo», «buen
  desempeño» no dicen nada si no se sabe respecto de qué. Se da el valor, la comparación o el criterio:
  «exactitudes superiores al 90 %», «mayores que las de los dermatólogos del mismo estudio».
- **Sin referencias ambiguas.** «Eso», «esto», «lo», «esta forma», «esa equivalencia» se reemplazan por
  el sustantivo cuando no es inmediato a qué remiten. Ante la duda, se repite el sustantivo.
- **Sin calcos ni verbos figurados.** Las expresiones que suenan traducidas del inglés o fuera de
  contexto se reescriben con el verbo literal. Casos señalados por el tutor:

  | Se evita | Se escribe |
  |---|---|
  | «Cada línea deja algo sin resolver» | «La revisión de las distintas líneas de investigación permite identificar limitaciones que aún no se abordaron de manera conjunta» |
  | «De esos huecos sale el *pipeline*» | «A partir de las limitaciones identificadas se propone un *pipeline* que integra…» |
  | «Los clasificadores descansan sobre la prueba…» | «La evaluación de los clasificadores se realizó principalmente sobre…» |
  | «Cada pieza atiende una brecha» | «Cada componente del *pipeline* busca abordar una de las limitaciones identificadas» |
  | «cada token atiende a todos los demás» | «la atención relaciona cada token con todos los demás» |
  | «tropieza con la memoria» | «requiere más memoria de la que tiene una GPU de consumo» |
  | «El ViT lleva a las imágenes el codificador» | «El ViT aplica a las imágenes el codificador del transformer» |
  | «que una imagen y su descripción queden cerca» | «que una imagen y su descripción tengan *embeddings* similares» |
  | «no redacta» | «no genera texto» |
  | «una predicción merece afirmarse» | «una predicción es lo bastante confiable para presentarla como diagnóstico» |
  | «esta segunda dice si…» | «esta última permite determinar si…» |
  | «esa equivalencia no vale» | se explica por qué no se cumple |
  | «la propuesta encadena un clasificador…» | «la propuesta de este trabajo integra un clasificador…» |
  | «cuánto inflaba la fuga los resultados» | «cuánto sobreestima el desempeño la fuga de información» |
  | «eligen una etiqueta de un inventario cerrado» | «eligen una de las siete clases» |
  | «sus propiedades deciden la métrica y la partición» | se dice qué propiedad lleva a qué decisión: «como NV reúne dos tercios de las imágenes, las métricas dan a cada clase el mismo peso» |
  | «qué cuesta usar el sistema» | «el costo computacional de entrenar y ejecutar los modelos y el *pipeline*» |
  | «Así resuelve juntas la clasificación y…» | «De este modo, el *pipeline* permite resolver…» |
  | «descarta» | «no permite excluir», «no explica», «no se sostiene» |
  | «demuestra», «prueba que» | «indica», «es compatible con», «los resultados muestran que» |
  | «garantiza» | «en estos experimentos», «bajo estas condiciones» |
  | «siempre», «nunca» sin alcance | «en la prueba», «en los casos evaluados» |
  | «nivel del azar» cuando el IC excluye 1/7 | «cerca del azar», «apenas por encima del azar» |

- **Artículo delante del nombre de una técnica.** «El preentrenamiento contrastivo lenguaje–imagen
  (CLIP) entrena…», no «Preentrenamiento contrastivo… entrena…».
- **Sustantivos con referente.** «El sistema», «el protocolo», «el modelo» o «las pruebas» a secas no
  dicen nada si en ese punto hay más de un candidato. Se nombra el objeto: «el *pipeline*», «los
  clasificadores supervisados», «el procedimiento de evaluación de la Sección~\ref{…}» (tutor,
  21/10/2026).
- **Las cifras compactas se explican.** Una notación como «70/15/15», «$k = 3$» o «IC del 95 %» se dice
  con palabras la primera vez: «70 % de las imágenes para entrenamiento, 15 % para validación y 15 % para
  prueba».
- **Las partes cierran con el total.** Si un párrafo reparte un total («de los 51 casos, 20 incorrectos y 29
  correctos»), la suma tiene que dar el total o se dice qué queda afuera: «y dos contradicciones». Una cuenta que no
  cierra obliga al lector a desconfiar de las demás cifras.
- **Títulos completos.** El título de una sección o subsección se entiende fuera de contexto, porque se
  lee en el índice: «Evaluación de la generación de reportes», no «Evaluación de la generación».

### Lista de control de la pasada de estilo

Etapa 3 del circuito. Se recorre la sección párrafo por párrafo:

1. ¿La primera oración de cada párrafo dice de qué trata y lo conecta con el anterior?
2. ¿Cada párrafo tiene una sola idea central y la cierra?
3. ¿Toda técnica nombrada se presentó antes por el problema que resuelve, con cita?
4. ¿Las relaciones de causa, consecuencia o contraste están dichas con un conector?
5. ¿Quedan «eso», «esto», «lo» o adjetivos de grado («alto», «bajo») sin referencia?
6. ¿Quedan calcos, verbos figurados o afirmaciones categóricas sin alcance?
7. ¿Cada término traducido lleva el inglés entre paréntesis en su primera aparición?
8. ¿Se redefine algo que ya se definió en otra sección? Si es así, se reemplaza por una mención con `\ref`.
9. ¿La sección abre retomando la anterior y cierra con la transición a la siguiente?
10. ¿El presente describe el método y el pasado solo lo ya realizado? ¿Se repite «se evalúa», «se compara» en párrafos seguidos?
11. ¿Quedan «el sistema», «el protocolo» o cifras compactas («70/15/15») sin decir a qué se refieren?
12. En la metodología: ¿algún párrafo adelanta un resultado, justifica una decisión con un resultado sin decir de dónde sale, o mezcla el método con el hardware (§3, «Capítulo de metodología»)?
13. ¿Compila sin huérfanas ni flotantes fuera de lugar (§7)?
14. En un capítulo de resultados: ¿la sección abre con contexto, describe el objeto (filas y columnas, ejes y paneles), da primero el mejor y el peor valor y separa la conjetura? ¿Cierra con un balance que no repite la discusión?
15. ¿Cada afirmación comparativa nombra la prueba que la respalda y evita mezclar McNemar con el *bootstrap*?
16. ¿El tono no supera la evidencia («descarta», «demuestra», «garantiza», «siempre», «nunca», «nivel del azar»)?

### Concisión: menos es más

Decisión del autor (2026-10-04), tras comparar con la tesina de ejemplo: el texto estaba más largo y
más desconectado de lo necesario. Una explicación simple, concisa y precisa se entiende mejor que una
exhaustiva. La revisión del tutor del 09/10/2026 mostró el riesgo opuesto: al condensar se juntaron
oraciones de temas distintos en un mismo párrafo y se perdieron las transiciones. Se recorta quitando
conceptos que el trabajo no necesita o bajando su profundidad, nunca quitando los conectores y las
oraciones que orientan (ver «Cohesión y progresión del texto»).

- **Cada oración aporta un dato, una definición o un vínculo que el lector necesita.** Si se puede
  borrar sin que el lector pierda nada, se borra. Una idea se dice una vez: no se repite al cerrar el
  párrafo ni en la tabla y en el texto con las mismas palabras.
- **Las transiciones son conceptuales y cortas.** Una oración que conecta un concepto con el
  siguiente («el ajuste completo de un modelo grande no entra en una GPU, y eso motiva LoRA») basta.
  No se escriben párrafos de cierre que anuncian la sección siguiente o enumeran lo que viene
  («Ese orden es el de lo que sigue: primero…, después…»), ni que recapitulan lo ya dicho
  («Las probabilidades $p_c$ son la cantidad sobre la que operan varias piezas de este capítulo…»).
- **Sin aclaraciones defensivas.** No se agregan frases que se adelantan a una objeción («es una
  propiedad deseable y no un diseño», «se toman como muestra del alcance, no como el desempeño
  alcanzable hoy») salvo que el lector se vaya a equivocar sin ellas.
- **Un ejemplo por idea, y solo si aclara.** Los ejemplos de otros dominios (el 6 rotado que pasa a
  ser un 9) sobran cuando la idea se entiende sin ellos.
- **Cifras solo las que sostienen el argumento.** Un dato por afirmación; el resto, si hace falta,
  va en una tabla. En la introducción alcanzan los números que muestran la magnitud del problema.
- **Epígrafes (`\caption`) breves.** Una oración que dice qué muestra la figura o la tabla, de una
  línea o poco más (orientativo: hasta unas 20 palabras). La explicación de cómo leerla va en el
  párrafo que la cita, no en el epígrafe. Una segunda oración corta solo para abreviaturas o para
  «Tomada de / Adaptada de \cite{}». Con un epígrafe así, el argumento opcional `\caption[...]`
  sobra.
- **Estado del arte: análisis agrupado, no sucesión de fichas.** Revisión del tutor del 09/10/2026: un
  párrafo por trabajo que reúne objetivo, arquitectura, datos, métricas, resultados, limitaciones y
  hardware, uno tras otro, se lee como una lista de antecedentes. Los trabajos se agrupan por lo que
  comparten (el mismo problema, el mismo conjunto de datos, el mismo enfoque) y el texto dice cómo se
  relacionan: qué agrega cada uno respecto del anterior, en qué se diferencian y qué problema sigue
  abierto, de modo que se entienda la evolución de la línea. Cuando un trabajo se desarrolla, se
  distinguen el problema, el método, los resultados y las limitaciones. Las cifras de detalle
  (arquitecturas exactas, tamaños de partición, hardware) van en la tabla comparativa o no van. Los
  trabajos secundarios, en una o dos oraciones dentro del grupo; un antecedente breve puede quedar en un
  solo párrafo. Cada eje ocupa del orden de una carilla y media a dos (pedido del tutor, A16), tabla
  aparte.
- **Referencia de proporciones** (`Docs/tesinamaglione_ejemplo.pdf`): introducción de unas tres
  páginas, epígrafes de una línea, un párrafo por trabajo en el estado del arte, transiciones de una
  oración.

### Conceptos, fórmulas y notación

El documento es explicativo: el lector tiene que poder reconstruir cómo se calcula cada cosa que el
trabajo usa sin ir a la fuente.

- **La profundidad de cada concepto es proporcional a su importancia para entender los experimentos y
  los aportes** (tutor, 09/10/2026). Un tema puede ser central para la inteligencia artificial y no
  necesitar más de un párrafo acá. Los fundamentos generales del aprendizaje profundo (optimización,
  retropropagación, Adam y los planificadores de la tasa de aprendizaje, las variantes de
  regularización, las arquitecturas CNN una por una, los aspectos generales del transformer) se
  nombran y se dice qué hacen, sin fórmulas propias ni desarrollos matemáticos. Lo que es el núcleo del
  trabajo (ViT, Swin, LLM, VLM, LoRA, transferencia y ajuste fino, incertidumbre, generación de
  reportes) se desarrolla con más detalle. Si no queda claro por qué el lector necesita una fórmula para
  entender la investigación, la fórmula sale.
- **Las métricas y métodos que el trabajo usa se definen con su fórmula**, además de con palabras: cómo
  se calcula, no solo qué mide. Vale para las métricas de clasificación, calibración y texto, las
  pruebas estadísticas y los métodos (Grad-CAM, RAG). Cada grupo de métricas abre diciendo qué aspecto
  del desempeño evalúa y por qué ese aspecto importa en este trabajo. Las métricas secundarias se
  nombran con una explicación breve, su fórmula y qué información dan sobre los resultados, sin más
  desarrollo.
- **La fórmula sigue la notación del trabajo original** (la de Guo para el ECE, la de Selvaraju para
  Grad-CAM) salvo que choque con un símbolo ya usado en el capítulo; en ese caso se cambia el símbolo y
  no el concepto. Convenciones fijas del documento: $C$ clases, $n$ imágenes, $p_c$ probabilidad de la
  clase $c$, $\mathbf{z}$ logits, $\theta$ parámetros, $\eta$ tasa de aprendizaje, $\mathcal{L}$
  pérdida; vectores en negrita minúscula y matrices en mayúscula.
- **Símbolo o término original entre paréntesis en la primera mención**: «una consulta ($Q$)», «un
  filtro de pequeño tamaño (*kernel*)», «detención temprana (*early stopping*)».
- **Negrita en el nombre de una métrica, prueba o método en el lugar donde se define** (**F1**,
  **BLEU**, **prueba de McNemar**, **Grad-CAM**), para que se encuentren al hojear. Solo en la
  definición; las menciones posteriores van en redonda.
- **Un término técnico se define en la primera aparición del capítulo**, en el cuerpo del texto
  (*token*, *embedding*). El glosario no se imprime, así que no reemplaza esa definición.
- **Sin meta-texto sobre el alcance** («solo incluye lo que los capítulos siguientes usan»): la sección
  abre diciendo qué presenta, no qué deja afuera.

### Estructura y progresión

Reglas que surgen de la revisión del tutor de los capítulos 1 y 2 (2026-09-28). Para dudas de
estructura o de convención que esta guía no resuelve, la referencia es una tesina terminada de la
misma carrera que pasó el tutor (`Docs/tesinamaglione_ejemplo.pdf`, no versionada).

- **Cada capítulo habla de lo suyo.** La introducción no adelanta metodología, conjuntos de datos
  ni algoritmos; el marco teórico no habla de particiones, de la distribución de un conjunto ni de
  decisiones propias («no hables de cosas prácticas»). Eso va en el Capítulo 3.
- **Ningún término se usa antes de haberlo presentado.** Si un concepto aparece, se explica en ese
  lugar o ya se explicó antes; no se escribe «esto se verá después».
- **Cada concepto se define una sola vez**, en la sección donde es más pertinente. Las secciones
  posteriores lo nombran y remiten con `\ref`, sin volver a explicarlo (tutor, 09/10/2026, Audio 3):
  al hablar de los LLM alcanza con «como en cualquier red neuronal, el modelo tiene que generalizar
  (Sección~\ref{…})». La ficha de cada sección lista qué define y qué retoma.
- **La introducción de un capítulo dice qué contiene y cómo se organiza**, sin detalle técnico y
  sin figuras, salvo que la figura sea imprescindible para entender la organización.
- **En la organización del documento cada capítulo se describe por su contenido**: «Este capítulo
  presenta la comparación de estrategias de clasificación…», no «Responde la PI1».
- **Hilo conductor.** Cada párrafo retoma algo del anterior y lleva al siguiente; la sección no es
  una sucesión de datos sueltos. Una frase como «El diagnóstico humano tampoco está resuelto» que
  abre un tema sin conectarlo con lo anterior es la señal de que falta la transición.
- **Cada concepto del marco teórico cumple una función** (revisión del tutor, 2026-10-05): explica una
  arquitectura o técnica que el trabajo usa, justifica una decisión metodológica o experimental, permite
  interpretar un resultado o fundamenta una limitación, una comparación o una contribución. La extensión
  sigue a la función: la retropropagación cumple en parte la primera y alcanza con unas líneas, mientras
  que LoRA, la calibración, la incertidumbre, el desbalance de clases y la generación condicionada cumplen
  varias y se desarrollan más. Los fundamentos generales (§2.1) ocupan unas tres páginas. A la inversa,
  toda técnica que usan el código o los experimentos que se reportan (la receta de entrenamiento de
  `Codigo/src/training/recipes.py`, el TTA, el ensamble, la clasificación de un VLM por verosimilitud)
  tiene en el marco al menos una o dos oraciones que la expliquen, para que el Cap. 3 pueda remitir a ella.
- **El marco teórico se escribe para un lector general.** La pregunta para cada concepto es por qué
  el lector lo necesita para entender lo que se hizo o el resultado. El lector puede ser un
  informático, que ya conoce las redes neuronales, o un dermatólogo, que no las conoce.
- **El marco teórico no se ordena según el *pipeline*.** Presenta los conceptos que después
  justifican el *pipeline*, de modo que el diseño del Capítulo 3 aparezca como consecuencia del
  marco y del estado del arte, y no al revés.
- **Transición entre secciones.** Cada sección del marco cierra relacionando sus arquitecturas o
  conceptos con los de la sección siguiente, en una o dos oraciones (ver «Concisión»).
- **El estado del arte cierra cada eje con una síntesis**: qué aporta la línea, cómo la atacan las
  distintas familias de trabajos y qué queda sin resolver, en uno o dos párrafos. Por cada trabajo
  se dice objetivo, método, datos, métricas, contra qué se comparó, resultados, si hubo evaluación
  con expertos y qué limitaciones reconocen los autores, en un párrafo compacto (ver «Concisión»).

### Capítulo de metodología

Revisión del tutor del Capítulo 3 (21/10/2026, `feedback/cap_3/feedback_cap3.md`). El capítulo no se lee como una
colección de algoritmos y experimentos, sino como la explicación ordenada de las decisiones que llevan del
problema inicial al *pipeline* y a su evaluación. Valen para el Cap. 3 y, en lo que corresponda, para los
capítulos de resultados.

- **Primero lo que se evalúa, después cómo se evalúa.** El orden es: problema y tareas → flujo de trabajo →
  datos → componentes (cada familia de modelos) → integración en el *pipeline* → criterios y procedimientos
  de evaluación → entorno experimental. Las métricas no aparecen antes que los modelos que miden. Si una
  sección anterior necesita un criterio (por ejemplo, con qué métrica se elige una configuración), lo
  nombra con `\ref` hacia adelante en una oración y la definición queda en la sección de evaluación.
- **El flujo de trabajo va primero y es breve.** La figura del flujo culmina la definición de las tareas:
  una oración por etapa dice qué hace, y cada sección siguiente la desarrolla. La introducción del capítulo
  presenta la lógica metodológica general y después cómo se organiza; no repite la descripción del
  *pipeline* que hace la primera sección.
- **Secciones paralelas con la misma estructura.** Las secciones que presentan familias de modelos siguen el
  mismo orden: propósito (qué pregunta o tarea atiende la familia) → modelos seleccionados → configuración
  → procedimiento experimental. Leer una sección prepara al lector para la siguiente.
- **Por qué antes que qué.** Un modelo se presenta desde la necesidad: «para evaluar X se necesita Y; por
  ello se usa Z, que tiene tales características y produce tal salida». Las características técnicas
  vienen después de la razón de la elección.
- **Una figura por modelo o familia, sobre cómo se usa en el trabajo.** El Cap. 3 no redibuja la
  arquitectura genérica del Cap. 2: muestra qué entra, qué sale, qué se entrena y qué queda congelado en
  este trabajo, y el párrafo que la cita la explica.
- **No se repite el marco teórico.** Se dice qué modelo se ajusta, qué parámetros se configuran y por qué
  se usa la técnica, y se remite con `\ref` a su definición. No se vuelve a explicar cómo funciona LoRA o
  una red convolucional.
- **Un párrafo, una función.** Un párrafo presenta un modelo y justifica su elección; otro explica cómo se
  configura o se usa. Características de arquitectura, motivos de selección, detalles de entrenamiento y
  resultados esperados no van juntos.
- **Diseño antes que implementación.** En el *pipeline* se distinguen la arquitectura general de las reglas
  particulares de decisión, y las decisiones de diseño se explican antes de sus detalles de implementación.
  Orden de argumento: componentes disponibles → necesidad de integrarlos → arquitectura propuesta (figura)
  → funcionamiento → decisiones de salida.
- **Ningún resultado en la metodología.** No se justifica una decisión con un resultado de los capítulos
  siguientes («como muestra el Capítulo 4»). La motivación sale de los objetivos, del marco teórico o del
  estado del arte (las debilidades conocidas de cada familia de modelos). Si una decisión surgió de un
  experimento propio (un piloto, una búsqueda en validación), se dice cuál fue y sobre qué datos.
- **El método separado de las herramientas.** GPU, clústeres, tamaños de lote, precisión numérica, semillas y
  bibliotecas van en una sección de entorno experimental al final del capítulo. En el cuerpo queda solo la
  restricción de cómputo, como parte del alcance de la propuesta (una GPU de consumo, sin clústeres ni GPU
  de última generación).
- **Los datos, por su uso.** Los conjuntos se distinguen de manera consistente según para qué se usan:
  entrenamiento, validación, prueba, evaluación externa o preentrenamiento de modelos de terceros. Primero
  se describen en general y después, en otro párrafo, se explica qué papel cumple cada uno en la
  experimentación y por qué uno tiene más peso que los otros. Los párrafos no se vuelven una ficha por
  conjunto.
- **Cada experimento con su objetivo y su métrica.** La sección de evaluación presenta primero los criterios
  generales y las métricas, y después los procedimientos complementarios, cada uno separado
  (generalización a otra población, robustez, calibración, interpretabilidad, costo). Una tabla hace
  explícita la correspondencia experimento → qué se busca → métrica.
- **El diseño experimental se ordena por etapas y dice cuántas ejecuciones tiene cada configuración.** Después de las
  métricas, una sección ordena los experimentos como se ejecutan: primero los de clasificación y después los de
  generación, cada etapa con lo que usa de la anterior. Dice cuántas ejecuciones tiene cada configuración y por qué
  (la búsqueda y las funciones de pérdida, una; los clasificadores, tres; los modelos deterministas, una), y deja los
  números de semilla en el entorno experimental. Con tres ejecuciones, el desvío es una estimación gruesa de la
  variación y no un intervalo de confianza: se dice en las métricas y se retoma en las limitaciones.
- **Los resultados replican esa estructura.** Si la metodología dice «primero se compara A, B y C», los
  Caps. 4 y 5 presentan esos resultados juntos en una sección, y las comparaciones entre ellos van en la
  misma sección.
- **Tablas y figuras citadas antes y cerca.** Cada flotante se cita en el párrafo que lo precede. Una tabla
  o figura de otro capítulo se cita con su capítulo («la Tabla~\ref{…} del Capítulo~\ref{…}»), porque el
  lector la busca en la página.

### Capítulos de resultados

Revisión del tutor de los Caps. 4 y 5 (26/10/2026, audio 5, `feedback/cap4_5/feedback_cap_4_5.md`). Cada resultado se
presenta con el mismo esquema, y prevalece sobre «Cada sección abre directamente con su contenido» en estos capítulos:

1. **Contexto.** Qué se analiza, con qué modelos y sobre qué datos («Esta sección presenta los resultados de los cuatro
   clasificadores supervisados sobre las 1 503 imágenes de prueba…»). La introducción de cada sección dice qué se va a
   mostrar en ella, en general; cada subsección lo muestra en particular. El diseño del experimento no se repite: se
   remite al Cap. 3, y lo que no esté allí se agrega allí. Tampoco se explica de nuevo cómo se calcula una métrica ni
   cómo funciona un componente: se nombra con `\ref` y se dice qué condición se está midiendo.
2. **El objeto.** Qué tabla o figura se presenta y qué contiene: qué hay en las filas y en las columnas, o en cada eje
   y en cada panel. La redacción varía para no repetir la fórmula.
3. **Los valores.** Primero cuál obtiene el mejor resultado y cuál el peor, después el detalle. Un solo orden para todo
   el texto: **de lo general a lo particular**. Frases cortas.
4. **La conjetura, separada.** El valor y la explicación de por qué se da van en oraciones distintas, y la explicación
   se marca como tal («posiblemente porque…», «una explicación posible es…») y se apoya en lo que se sabe del modelo
   (arquitectura, preentrenamiento, configuración), nunca en «porque es el mejor».

Además:

- **No se habla de semillas** en los resultados: se habla de ejecuciones, y cuando una cifra corresponde a una sola se
  dice «ejecución de referencia» y se remite a la sección que la define, sin repetir el número de semilla.
- **Cada conclusión dice qué prueba respalda lo que afirma**: McNemar compara los aciertos por imagen y el *bootstrap*
  pareado, la diferencia de una métrica. Las dos no se mezclan en una misma oración: «las diferencias son significativas
  en McNemar, salvo la de DenseNet frente a DermLIP en sensibilidad macro» confunde dos pruebas y dos cantidades. Si las
  dos no coinciden, se explica por qué miden cosas distintas.
- **Las afirmaciones se atenúan** a lo que muestran los datos: «no mejora» o «no permite excluir» en lugar de
  «descarta», y «cerca del azar» en lugar de «nivel del azar» cuando el intervalo excluye 1/7.
- **La corrección diagnóstica de los reportes se mide**; la fidelidad visual de la descripción queda parcialmente sin
  verificar, sin decir que «no se puede determinar»: se escribe qué se midió y qué queda por verificar.

### Balance de cierre y capítulo de discusión

Revisión del tutor de los Caps. 4 y 5 (26/10/2026, comentarios al texto y audios 2 a 4). Cada capítulo de resultados
cierra con un **balance**; la interpretación conjunta va en el capítulo de discusión, y ninguno de los dos repite al
otro.

- **El balance cierra el capítulo, no lo discute.** Dos o tres párrafos que enuncian los hallazgos del capítulo con las
  cifras ya presentadas y remiten a la sección donde se midieron. No agrega argumentos, no compara con la literatura y
  no adelanta las implicaciones: eso es materia de la discusión. Su última oración prepara el capítulo siguiente.
- **La discusión es transversal.** Responde las preguntas de investigación en conjunto, interpreta los hallazgos que
  cruzan los dos capítulos, deriva implicaciones para el diseño, reúne las limitaciones y las amenazas a la validez, y
  contrasta con la literatura cuando corresponde. No vuelve a describir los resultados ni repite el balance.
- **La discusión tiene que ser sustantiva.** Si el material disponible solo alcanza para resumir los capítulos, no se
  justifica un capítulo aparte: la discusión se integra al final del capítulo de resultados. Un capítulo de discusión
  se organiza por argumentos, no por el orden de los capítulos que interpreta.
- **El balance no introduce cifras nuevas.** Usa las que ya están en las tablas y figuras del capítulo; si una cifra
  hace falta para el balance y no está en el capítulo, se agrega en la sección donde se midió, no en el cierre.

### Patrones de escritura automatizada

Recomendaciones para no caer en el tono predecible de la escritura generada por modelos de IA.
Se aplican según el contexto y **no son requisitos duros**: las convenciones de esta guía —voz
impersonal, terminología, tipografía— prevalecen sobre ellas, y la pasada se hace al revisar la
prosa, no como regla de cierre. «Guion largo» es la raya `—`; no aplica al guion doble de los
compuestos como «visión--lenguaje».

Al revisar la prosa se buscan estos tics y se corrigen cuando aparecen sin motivo:

- adverbios de énfasis o de relleno que no agregan información;
- objetos inanimados con verbos de persona («la decisión surge») cuando hay un agente que nombrar;
- frases de relleno del tipo «esto es lo que…»;
- contrastes «no es X, es Y» donde alcanza con decir Y;
- tres oraciones seguidas de la misma longitud, o párrafos que cierran siempre con una frase corta y rotunda;
- rayas (—) en la prosa;
- afirmaciones vagas («las implicaciones son significativas») en lugar de la implicación concreta;
- conectores metatextuales («el resto de este capítulo…»).

La pasiva refleja impersonal («se evalúan») es la voz del documento (sección 3) y no entra en esta lista.

## 4. Terminología fijada

La tabla fija decisiones de consistencia, no prohibiciones generales: cuando dos términos son
ambos aceptables, se usa el de la columna izquierda para que el documento no alterne entre los
dos. Está sujeta a cambios; lo que no cambia es que una vez elegido un término, se usa en todos
los capítulos.

| Se usa | No se usa | Nota |
|---|---|---|
| fuga de información entre particiones (*data leakage*) | fuga de datos, contaminación | Se define como concepto general en el marco teórico (generalización, §2.1.3); después alcanza «fuga de información» |
| entorno real | producción | |
| publicado solo en arXiv, sin revisión de pares | preimpresión, *preprint* | Revisión del autor, 2026-10-04; en las tablas basta una marca con nota |
| \glspl{vlm} médicos de propósito general | médicos generales (para modelos) | «médicos generales» se lee como profesionales |
| preentrenamiento, preentrenado | pre-entrenamiento, pre-entrenado | El prefijo *pre-* va soldado (RAE) |
| partición, subconjunto | *split* | «partición disjunta por lesión» es el nombre del procedimiento |
| modelo visión--lenguaje (VLM) | modelo de lenguaje visual, modelo multimodal (a secas) | El guion es `--` (semirraya) |
| *pipeline* | sistema propuesto, tubería, canal | Nombra la arquitectura completa: clasificador, kNN y generador encadenados. «Sistema» queda para usos genéricos («sistema de apoyo al diagnóstico») |
| exactitud | precisión | «precisión» queda reservada para *precision* |
| atención multicabezal (*multi-head attention*) | atención multi-cabeza | Pedido del tutor (09/10/2026) |
| parche (*patch*) | — | El inglés entre paréntesis en la primera mención |
| sensibilidad macro | *recall* macro, exhaustividad, exactitud balanceada (como nombre propio) | Es el mismo número que la exactitud balanceada; la definición lo menciona una vez como sinónimo |
| F1 ponderado, F1 macro | F1-score, puntaje F1 | |
| función de pérdida | pérdida (a secas, en tablas y títulos) | En la prosa, «la pérdida» basta una vez que se nombró la función (tutor, 21/10/2026) |
| ajuste fino | *fine-tuning* | El anglicismo solo en la definición inicial |
| conjunto de datos | *dataset* | |
| reporte | informe | Consistencia con el título de la tesina. **«Reporte» designa únicamente el informe clínico**: no se lo usa en el sentido de «lo que se reporta». Para eso se dice «métrica de selección» (con qué se elige el modelo, en validación) y «resultado principal» (qué número se presenta, en test) |
| fidelidad diagnóstica | precisión diagnóstica | Es la métrica sin referencia, no una *precision* |
| participantes, evaluadores (en estudios de lectura) | lectores (*readers*) | Calco del inglés. «Observadores» queda para los estudios de concordancia entre especialistas |
| clasificadores, modelos | algoritmos (para un modelo entrenado) | «Algoritmo» queda para el procedimiento (la lista de 7 puntos, el descenso del gradiente) |
| *embedding* | embebido, incrustación, vector latente | Cursiva la primera vez de cada capítulo, como el resto de los términos en inglés. Vale también para los compuestos: «*embedding* de posición», «kNN sobre embeddings» |

**Prohibido:** la palabra «caveat» en cualquier contexto.

**Números.** Punto decimal, no coma (`0.846`). La plantilla de la UMU no se pronuncia al respecto
y la norma general del español es la coma, pero en el área los resultados se reportan con punto y
el material de experimentación propio ya lo usa en sus 267 valores, sin una sola coma; cambiar de
criterio obligaría a reescribir todas las tablas. Tres decimales en métricas, dos en porcentajes,
desviación con `$\pm$`. `babel` con la opción `spanish` convierte el punto en coma dentro de las
fórmulas (`$0.5$` se imprimía «0,5»); `Configurations/10-Macros.sty` lo desactiva con
`\decimalpoint`, así que el punto se escribe igual dentro y fuera de `$...$`.

**Acrónimos.** Se declaran en `Matter/05-Acronyms.tex` con
`\acronimo[opciones]{etiqueta}{SIGLA}{nombre en español}{nombre en inglés}`: el español en
minúscula (se inserta dentro de una oración; al comienzo de oración se usa `\Gls{}`) y el inglés
vacío si la sigla no lo tiene (IA, las categorías de HAM10000). Si la sigla se usa en plural, se
declara `longplural`. Las siglas no llevan marca de plural («las CNN»). Se invocan con `\gls{}` en
la primera aparición del documento; la lista de acrónimos toma de la misma entrada el español y el
inglés, así que las denominaciones coinciden. No se redefine un acrónimo ya declarado.

## 5. Extensión

**No hay límite de extensión.** Cada capítulo tiene la extensión que necesite para cubrir su
contenido (decisión del autor, 2026-09-28). La ficha estima la extensión de cada sección solo como
orientación para planificar. Que no haya límite no habilita el relleno: la extensión se justifica
con contenido, y ante la duda se elige la versión más corta (ver «Concisión», 2026-10-04).

Las estimaciones de extensión y las fuentes de cada capítulo van como **comentarios LaTeX**
(`% Extensión estimada:`, `% Fuentes:`) al inicio del archivo, nunca en el cuerpo del texto.

## 6. Citas y bibliografía

`Bibliography/Bibliography.bib` es el archivo único y canónico, con claves normalizadas
como `<apellido><año><palabra>` (`vaswani2017attention`, `tschandl2018ham10000`,
`yan2025derm1m`).

### Criterios de selección de fuentes

- **Ventana de referencia: 2020–2026.** Se prefieren trabajos de los últimos seis años. Ahí están
  las fuentes actualizadas y ahí se concentra la literatura efectivamente comparable con este
  trabajo.
- **El corte es un criterio práctico para acotar la búsqueda**, no una frontera técnica: entre 2017
  y 2020 ya hay trabajos con *transformers*, así que en el documento no se lo justifica por la
  arquitectura. El estado del arte del Capítulo~2 se construye con trabajos de la ventana; los
  anteriores entran como hitos y se los presenta como tales, fechados.
- **Un trabajo anterior a 2020 se cita si cumple al menos una de estas condiciones:**
  1. es fundacional y ampliamente aceptado, de manera que lo que aporta no quedó superado sino
     incorporado: la definición de una arquitectura, de una métrica o de un concepto;
  2. contiene información difícil de conseguir de otro modo, como los datos de Argentina o las
     bases clínicas del problema;
  3. es el artículo original de un recurso que el trabajo usa, como el del conjunto de datos.
- **Acceso abierto cuando se pueda.** No es excluyente, pero entre dos fuentes equivalentes se toma
  la que se lee sin barrera de pago. Se evalúa caso por caso, y para las fuentes clínicas suele no
  haber alternativa.

El encuadre de cada referencia anterior a 2020 que ya está en el `.bib` queda registrado en
`refs_pendientes.md`.

- **Solo se citan claves existentes.** Antes de citar se verifica:
  `grep "^@.*{clave," Bibliography/Bibliography.bib`.
- **Las referencias nuevas no se agregan al `.bib`.** Se proponen en `refs_pendientes.md` con
  título, autores, año y DOI o URL, y el autor las incorpora. El `.bib` no se sobrescribe con una
  exportación de Zotero: la biblioteca está incompleta respecto del documento (ver
  `refs_pendientes.md`).
- **Estilo numérico** (`numeric-comp`, bibliografía en orden de aparición):
  - `\cite{clave}` para el caso normal → `[12]`.
  - `\textcite{clave}` cuando el autor es el sujeto de la oración → `Yan et al. [12]`.
  - Varias referencias juntas van en una sola llamada, `\cite{a,b,c}` → `[3-5]`, nunca
    `\cite{a}\cite{b}`.
- **En el marco teórico, toda afirmación sobre el estado del conocimiento lleva cita.** En los
  capítulos de resultados se cita solo para comparar con trabajos ajenos.
- No se cita por autoridad ni se acumulan referencias: cada cita respalda una afirmación concreta.

## 7. Convenciones LaTeX

- **Etiquetas:** `\label{cp:...}` capítulos, `\label{sec:...}` secciones y subsecciones,
  `\label{fig:...}`, `\label{tab:...}`, `\label{eq:...}`. El prefijo temático se conserva
  (`sec:marco_vlm`, `sec:res_gen_cascada`).
- **Referencias cruzadas:** `Capítulo~\ref{cp:marco}`, `Sección~\ref{sec:met_particiones}`,
  `Tabla~\ref{tab:...}`, con tilde para evitar el corte de línea. Nunca «ver arriba» o «más
  adelante» sin `\ref`.
- **Marcas de estado:** `\pendiente{...}` para contenido no escrito. Es el lugar donde después se
  escribe la sección: la prosa lo reemplaza en el mismo archivo. La lista se imprime con
  `\listadependientes` y solo existe con `docstage=working`.
- **Figuras** en `Figures/`, formato vectorial cuando sea posible, con `\caption` breve que dice
  qué muestra (sección 3, «Concisión»; la explicación va en el texto) y `\label`. Las tablas llevan
  `\caption` arriba.
- **Diagramas.** Uno por archivo en `Figures/Capitulos/<NN-Capitulo>/`, con el flotante completo adentro
  (`figure`, `\caption`, `\label`), y se traen con `\input{Figures/Capitulos/<NN-Capitulo>/...}` desde la
  sección. Las etiquetas tienen aire entre sí y respecto de los recuadros: si dos textos quedan pegados
  en el PDF, se separan o se acortan (tutor, 09/10/2026, Figura 2.2).
  Se dibujan con TikZ, no se importan como imagen: así se editan con el documento y escalan con la
  fuente. Los estilos comunes —recuadros, flechas, agrupaciones— están en
  `Configurations/13-Figuras.sty` y se usan tal cual (`figentrada`, `figtarea`, `figsalida`,
  `figgrupo`, `figflecha`); si hace falta un estilo nuevo, se agrega ahí y no en el diagrama.
  **Color con la paleta de Okabe e Ito** definida en ese archivo (`figazul`, `fignaranja`,
  `figverde`, `figbermellon`, `figceleste`, `figpurpura`), que distinguen las personas con
  daltonismo. El color nunca es la única señal: cada rol conserva además su forma de trazo y los
  rellenos son claros, de modo que el diagrama sigue siendo legible impreso en blanco y negro. No se
  usan colores fuera de la paleta.
- **Posición de las figuras (revisión del autor, 2026-10-04).** Figuras y tablas del cuerpo van con `[H]`
  (paquete `float`, cargado en `13-Figuras.sty`): quedan exactamente donde se las trae con `\input`, y
  `\raggedbottom` deja el hueco al pie de la página y no entre párrafos. Las tablas grandes del estado del
  arte flotan con `[htbp]`, con un `\FloatBarrier` antes de cada subsección para que no salgan de ella; una
  tabla que no entra en una página se parte en dos. **Después de cada cambio que mueva texto** se compila y
  se corre `python check_floats.py <capítulo>` desde `Docs/TFG/`: lista cada flotante con la página de su
  epígrafe y la de su primera mención, y marca los que nunca se mencionan (todo flotante se menciona en el
  texto). Se revisan además las miniaturas de las páginas del capítulo. Las etiquetas de un diagrama no se
  superponen con recuadros ni con flechas, y las flechas llegan al borde de un nodo, no al hueco entre
  dos.
- **Tablas.** `tabularx` con `booktabs` y `\caption` arriba. Cuando las celdas ocupan varias líneas,
  las filas de datos se separan con `\filasep` (regla fina gris, en `08-Tables.sty`) para seguir cada
  fila a simple vista. Las columnas se dimensionan para que los nombres propios no se corten con guion.
- **Figuras de otros trabajos.** Se pueden reproducir con la cita en el `\caption`: «Tomada de
  \cite{clave}» si se reproduce tal cual, «Adaptada de \cite{clave}» si se redibuja o modifica.
  Antes de incluirla se revisa la licencia del trabajo (CC BY permite reproducir con atribución;
  la licencia por defecto de arXiv no, y en ese caso se redibuja en TikZ y se pone «Adaptada de»).
  El archivo va en `Figures/Externas/`, en el formato original si es vectorial.
- **Viudas, huérfanas y huecos.** Al compilar se revisa que ningún párrafo termine con una o dos
  palabras solas en la última línea ni deje una línea aislada al pie o al comienzo de una página, y
  que no queden espacios en blanco grandes antes de un título o de una figura. Se corrigen
  reformulando la frase o sacando alguna palabra, no con espaciado manual. `Configurations/10-Macros.sty`
  pide además a TeX que la última línea de cada párrafo ocupe al menos 8em (`\parfillskip`), lo que
  resuelve la mayoría de los casos; los que quedan (listas, epígrafes, párrafos muy ajustados) se
  corrigen a mano. **Antes de cada commit** se corre `python -X utf8 check_huerfanas.py <capítulo>`
  desde `Docs/TFG/` (después de compilar), que lista las últimas líneas de párrafo con tres palabras o
  menos, y `python -X utf8 check_floats.py <capítulo>` para los flotantes. Una tabla que ocupa casi una
  página no entra nunca junto a su mención: va con `[!t]` después del párrafo que la menciona, para que
  el texto llene la página y no quede un hueco.
- **Código** con `minted` (requiere `-shell-escape`). Fragmentos cortos, solo si aportan.
- **Compilación:** `latexmk -xelatex -shell-escape tesina.tex` desde `Docs/TFG/`.

## 8. Ramas y commits

Un capítulo, una rama: `doc/cap01-introduccion`, `doc/cap02-marco-teorico`, y así. Se ramifica
desde `master` actualizado y se integra cuando el capítulo está cerrado.

- Un commit por sección redactada, con el asunto en imperativo y en español.
- En ese commit van el `.tex` de la sección, las figuras que haya incorporado y su ficha. Un commit
  no mezcla dos secciones, salvo que el cambio sea quitar de otra sección una definición repetida, y
  en ese caso el mensaje lo dice.
- **Se compila en la rama en la que se está trabajando**, tantas veces como haga falta: es la única
  forma de ver cómo queda el documento. `tesina.pdf` está versionado y se commitea también ahí.
- El PDF es un artefacto generado, así que su conflicto de merge no se resuelve a mano.
  `.gitattributes` lo marca con el driver `keep-ours`, que toma la versión local sin preguntar;
  **después de un merge que haya tocado capítulos hay que recompilar**, porque el PDF que quedó no
  incluye los cambios de la otra rama. El driver es local a cada clon y se registra una vez:

      git config merge.keep-ours.name "Conserva la version local; el artefacto se regenera recompilando"
      git config merge.keep-ours.driver true

## 9. Preliminares y cierre

Revisión del tutor de los Caps. 4 y 5 (26/10/2026, comentarios a las páginas preliminares). Las piezas que rodean al
cuerpo también se cierran antes de la entrega.

- **El resumen se escribe al final**, con las cifras definitivas y sin `\pendiente`. Cubre el problema, la propuesta,
  los datos y el método, los resultados principales y el aporte; no adelanta conclusiones que el cuerpo no sostiene ni
  incluye cifras que no estén en los capítulos. El resumen en inglés se escribe junto con el español, con la misma
  estructura y las mismas cifras.
- **La dedicatoria y los agradecimientos se completan antes de la entrega.** No se dejan como `\pendiente` en la
  versión que se envía al tutor.
- **Las conclusiones no introducen información nueva.** Distinguen lo que se midió de lo que queda como limitación o
  trabajo futuro, y cada aporte remite al capítulo que lo sustenta. No prometen beneficios que no se evaluaron ni
  convierten una posibilidad en un resultado.
