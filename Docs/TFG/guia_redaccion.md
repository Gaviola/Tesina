# Guía de redacción de la tesina

Contrato único para la redacción del documento final. Quien escriba una sección —el autor o un
agente— lee esta guía antes de escribir la primera línea, y todo lo que produzca se juzga contra
ella. Las decisiones acá fijadas valen para todos los capítulos: si algo hay que cambiar, se cambia
en este archivo y no sección por sección.

## 1. Circuito de trabajo

Cada sección del documento pasa por tres etapas. No se saltea ninguna.

| Etapa | Qué se produce | Quién decide |
|---|---|---|
| 1. Ficha | `fichas/<capitulo>.md`: mensaje central, esqueleto de párrafos, claves de cita, figuras y extensión | El autor aprueba antes de que se escriba prosa |
| 2. Redacción | La prosa se escribe **en el `.tex` del capítulo**, reemplazando el `\pendiente` de la sección, y se compila | Quien redacta |
| 3. Cierre | Un commit por sección en la rama del capítulo | El autor, sobre el diff |

Sin ficha aprobada no se redacta. La ficha es el punto de control real: es más rápido corregir un
esqueleto de una página que treinta páginas de prosa ajena.

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
4. **Se toca el capítulo y nada más.** La redacción de una sección modifica el `.tex` de su
   capítulo y, si la ficha pide una figura, el archivo de esa figura en `Figures/Capitulos/`. Ni
   `tesina.tex`, ni otros capítulos, ni el `.bib`. Si hiciera falta tocar un archivo compartido, se
   reporta aparte y se justifica.
5. **Toda decisión se reporta.** Al terminar, la sección se entrega con: claves citadas,
   afirmaciones sin respaldo, decisiones tomadas por cuenta propia y preguntas abiertas. Las que
   condicionan lo que se escriba después se anotan en «Decisiones tomadas» de la ficha, que es lo
   que sobrevive a la conversación.

## 3. Voz y estilo

- **Impersonal y descriptiva.** «Se evalúan cuatro arquitecturas», no «evaluamos» ni «el autor
  evalúa». Nunca se habla del autor en tercera persona.
- **El texto es propio.** No se escribe meta-lenguaje sobre el documento ni sobre la plantilla
  («este capítulo fue elaborado a partir de…», «material no desarrollado por el autor»).
- **Párrafos de 4 a 8 líneas**, uno por idea, encadenados. Se evitan las listas de viñetas en el
  cuerpo salvo cuando enumeran elementos realmente paralelos (clases, métricas, configuraciones).
- **Cada sección abre directamente con su contenido** y cierra con lo que deja instalado para la
  siguiente. No se anuncia lo que se va a hacer («en esta sección se describirá…», «esta sección
  presenta cómo…»): se hace. La excepción es la introducción de cada capítulo, que sí describe qué
  contiene el capítulo y cómo se organiza (ver «Estructura y progresión»).
- **Nada de relleno.** Sin frases de transición vacías, sin recapitulaciones de lo ya dicho, sin
  adjetivos de énfasis («notablemente», «sumamente»).
- **Español neutro formal.** Documentación y documento en español; el código y los nombres de
  variables, en inglés.
- **Los términos en inglés se usan cuando son los corrientes en el área.** *Pipeline*, *array*,
  *prompt*, *zero-shot*, *linear probe*, *grounding*, *hedging*, *bootstrap*, *trade-off*,
  *image captioning*, *kernel*, *greedy decoding*, *beam search*, *sampling*, *top-k*, *top-p* o
  *nucleus sampling* no tienen equivalente castellano instalado; traducirlos («búsqueda codiciosa»,
  «muestreo de núcleo») dificulta la lectura en lugar de facilitarla, así que se usan tal cual. Lo
  mismo vale para calcos de expresiones: «la masa de probabilidad acumulada» se reformula como «la
  probabilidad acumulada». Se prefiere el castellano cuando ya es de uso
  corriente («ajuste fino», «conjunto de datos», «aprendizaje profundo», «atención multi-cabeza»).
- **Cursiva la primera vez en cada capítulo** con `\emph{}`; después, redonda. En títulos de
  sección y en los índices, siempre redonda. Un término que aparece cincuenta veces en cursiva es
  ruido tipográfico.
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
  atribuye («que sus autores presentan como el primer conjunto público…»).
- **Las decisiones se explican desde los objetivos.** «Como uno de los objetivos es ejecutar todo en una
  GPU de consumo, los modelos se adaptan con LoRA», no «se adaptan con LoRA, y por eso se ejecutan en una
  GPU de consumo». La causalidad sigue el orden en que se tomó la decisión.
- **Alternativas paralelas en lista.** Cuando un párrafo enumera opciones que se comparan (estrategias de
  pérdida, variantes de un método), van en `enumerate`, no numeradas a mano dentro del texto.

### Conceptos, fórmulas y notación

El documento es explicativo: el lector tiene que poder reconstruir cómo se calcula cada cosa que el
trabajo usa sin ir a la fuente.

- **Cada método o métrica que el trabajo usa se define con su fórmula**, además de con palabras: cómo
  se calcula, no solo qué mide. Vale para las métricas de clasificación, calibración y texto, las
  pruebas estadísticas y los métodos (Adam, Grad-CAM, RAG).
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
- **La introducción de un capítulo dice qué contiene y cómo se organiza**, sin detalle técnico y
  sin figuras, salvo que la figura sea imprescindible para entender la organización.
- **En la organización del documento cada capítulo se describe por su contenido**: «Este capítulo
  presenta la comparación de estrategias de clasificación…», no «Responde la PI1».
- **Hilo conductor.** Cada párrafo retoma algo del anterior y lleva al siguiente; la sección no es
  una sucesión de datos sueltos. Una frase como «El diagnóstico humano tampoco está resuelto» que
  abre un tema sin conectarlo con lo anterior es la señal de que falta la transición.
- **El marco teórico se escribe para un lector general.** La pregunta para cada concepto es por qué
  el lector lo necesita para entender lo que se hizo o el resultado. El lector puede ser un
  informático, que ya conoce las redes neuronales, o un dermatólogo, que no las conoce.
- **El marco teórico no se ordena según el *pipeline*.** Presenta los conceptos que después
  justifican el *pipeline*, de modo que el diseño del Capítulo 3 aparezca como consecuencia del
  marco y del estado del arte, y no al revés.
- **Transición entre secciones.** Cada sección del marco cierra con un párrafo que relaciona sus
  arquitecturas o conceptos con los de la sección siguiente.
- **El estado del arte cierra cada eje con una síntesis**: qué aporta la línea, cómo la atacan las
  distintas familias de trabajos y qué queda sin resolver. Por cada trabajo se dice objetivo,
  método, datos, métricas, contra qué se comparó, resultados, si hubo evaluación con expertos y
  qué limitaciones reconocen los autores.

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
| fuga de información entre particiones (*data leakage*) | fuga de datos, contaminación | Se define en la primera aparición (Materiales y métodos); después alcanza «fuga de información» |
| entorno real | producción | |
| partición, subconjunto | *split* | «partición disjunta por lesión» es el nombre del procedimiento |
| modelo visión--lenguaje (VLM) | modelo de lenguaje visual, modelo multimodal (a secas) | El guion es `--` (semirraya) |
| *pipeline* | sistema propuesto, tubería, canal | Nombra la arquitectura completa: clasificador, kNN y generador encadenados. «Sistema» queda para usos genéricos («sistema de apoyo al diagnóstico») |
| exactitud | precisión | «precisión» queda reservada para *precision* |
| sensibilidad macro | *recall* macro, exhaustividad | |
| F1 ponderado, F1 macro | F1-score, puntaje F1 | |
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

La ficha fija la extensión de cada sección. Como referencia, el documento apunta a 90–110 páginas:
introducción 8–10, marco teórico 25–30, materiales y métodos 20–25, cada capítulo de resultados
25–30, discusión 8–12, conclusiones 4–6.

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
- **Figuras** en `Figures/`, formato vectorial cuando sea posible, con `\caption` que se entienda
  sin leer el cuerpo del texto y `\label`. Las tablas llevan `\caption` arriba.
- **Diagramas.** Uno por archivo en `Figures/Capitulos/`, con el flotante completo adentro
  (`figure`, `\caption`, `\label`), y se traen con `\input{Figures/Capitulos/...}` desde la sección.
  Se dibujan con TikZ, no se importan como imagen: así se editan con el documento y escalan con la
  fuente. Los estilos comunes —recuadros, flechas, agrupaciones— están en
  `Configurations/13-Figuras.sty` y se usan tal cual (`figentrada`, `figtarea`, `figsalida`,
  `figgrupo`, `figflecha`); si hace falta un estilo nuevo, se agrega ahí y no en el diagrama.
  **Color con la paleta de Okabe e Ito** definida en ese archivo (`figazul`, `fignaranja`,
  `figverde`, `figbermellon`, `figceleste`, `figpurpura`), que distinguen las personas con
  daltonismo. El color nunca es la única señal: cada rol conserva además su forma de trazo y los
  rellenos son claros, de modo que el diagrama sigue siendo legible impreso en blanco y negro. No se
  usan colores fuera de la paleta.
- **Posición de las figuras.** Por defecto `[htbp]`. Si al compilar la figura salta a la página
  siguiente y corta un párrafo que viene después de ella, se usa `[H]` (paquete `float`, cargado en
  `13-Figuras.sty`) para fijarla donde se la trae con `\input`. Las etiquetas de un diagrama no se
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
  reformulando la frase o sacando alguna palabra, no con espaciado manual.
- **Código** con `minted` (requiere `-shell-escape`). Fragmentos cortos, solo si aportan.
- **Compilación:** `latexmk -xelatex -shell-escape tesina.tex` desde `Docs/TFG/`.

## 8. Ramas y commits

Un capítulo, una rama: `doc/cap01-introduccion`, `doc/cap02-marco-teorico`, y así. Se ramifica
desde `master` actualizado y se integra cuando el capítulo está cerrado.

- Un commit por sección redactada, con el asunto en imperativo y en español.
- En ese commit van el `.tex` del capítulo, las figuras que la sección haya incorporado y la ficha
  si se actualizó.
- **Se compila en la rama en la que se está trabajando**, tantas veces como haga falta: es la única
  forma de ver cómo queda el documento. `tesina.pdf` está versionado y se commitea también ahí.
- El PDF es un artefacto generado, así que su conflicto de merge no se resuelve a mano.
  `.gitattributes` lo marca con el driver `keep-ours`, que toma la versión local sin preguntar;
  **después de un merge que haya tocado capítulos hay que recompilar**, porque el PDF que quedó no
  incluye los cambios de la otra rama. El driver es local a cada clon y se registra una vez:

      git config merge.keep-ours.name "Conserva la version local; el artefacto se regenera recompilando"
      git config merge.keep-ours.driver true
