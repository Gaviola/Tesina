# Ficha 2.2 — Arquitecturas para clasificación de imágenes

Sección del `.tex`: `Chapters/02-Marco-Teorico/02-arquitecturas-imagenes.tex`, que reúne
`02-redes-convolucionales.tex` y `03-transformers.tex`.

**Estado: aprobada, redactada y revisada por el autor (2026-10-11).** Extensión resultante: unas 6 páginas
(p. 37–43), con cuatro figuras; las 2.2 y 2.3 viejas ocupaban unas 5, y la ficha estimaba 4.5. La diferencia
viene de la revisión del autor (decisión 3). P7 quedó en dos párrafos
(atención; atención multicabezal) y P8 en dos (codificación de posición; bloque y codificador). En la
ecuación del Swin, los canales pasan a llamarse $D$, porque $C$ es la cantidad de clases (decisión vigente 4).
Responde a la tercera revisión del tutor (`feedback_cap1_y_2_v3.md`: la propuesta «IDEA», el mensaje, el
Audio 2 y los comentarios de las p. 36–41). Las fichas viejas `02-redes-convolucionales.md` y
`03-transformers.md` pasaron a `historial.md`.

## Hilo conductor

Pregunta que responde la sección: ¿cómo aprovechan la estructura de una imagen las arquitecturas que
clasifican lesiones en este trabajo, y en qué se diferencian?

Viene de: 2.1 deja red, capa, parámetros, activación, softmax, entrenamiento, regularización, preentrenamiento
en *ImageNet*, *backbone* y cabeza, ajuste fino. También deja una limitación: la red de 2.1 trata la imagen
como un vector, sin la disposición espacial de los píxeles.

Deja instalado: convolución, mapa de características, campo receptivo, conexión residual; *token*, parche
(*patch*), *embedding*, atención, atención multicabezal, codificación de posición, bloque transformer y
codificador; sesgo inductivo; ViT y Swin; línea base. Y una limitación para 2.3: ninguno de estos
clasificadores produce texto.

```
(sin subsección: un párrafo de entrada)
P1  Retoma la limitación de 2.1: en una imagen, los píxeles vecinos están relacionados y un mismo patrón
    puede aparecer en cualquier lugar. Las arquitecturas de esta sección incorporan esa estructura de dos
    maneras, la convolución y la atención, y los cuatro clasificadores que evalúa el trabajo (DenseNet,
    ConvNeXt, ViT y Swin) pertenecen a esas dos familias                         función: orienta · justifica
    ↓ necesidad — la primera manera, en orden histórico, es la convolución

2.2.1 Redes convolucionales (sec:marco_cnn)
P2  Convolución: un filtro pequeño recorre la imagen y produce un mapa de características que responde
    donde aparece su patrón. Dos supuestos: la información relevante es local, y un mismo patrón puede
    aparecer en cualquier parte (pesos compartidos). Varios filtros dan varios canales. Figura 2.2,
    sin ecuación                                                                  define
    ↓ consecuencia — al apilar convoluciones y reducciones, cada unidad ve una región más grande
P3  Arquitectura de una CNN: convolución, activación y reducción (*pooling*); campo receptivo. Así se
    concreta la cadena de rasgos simples a complejos de la introducción de 2.1, que se nombra y no se
    repite. Un promedio global da el vector de características que recibe la cabeza (2.1.3)   define
    ↓ problema — agregar capas debería ayudar, pero a partir de cierta profundidad la red empeora
P4  Degradación y conexión residual (ResNet), con su ecuación, que vuelve en el bloque transformer. No es
    sobreajuste: sube también el error de entrenamiento (remite a 2.1.2)          define · justifica
    ↓ ampliación — las dos CNN que evalúa el trabajo parten de esta idea
P5  DenseNet (concatena los mapas de las capas anteriores y reutiliza los rasgos, con menos parámetros) y
    ConvNeXt (una ResNet rediseñada con decisiones tomadas de los transformers). Una o dos oraciones
    cada una, sin fórmula                                                        explica lo usado
    ↓ limitación — la convolución solo relaciona píxeles cercanos, y vincular regiones lejanas exige
      muchas capas

2.2.2 Atención y arquitectura transformer (sec:marco_atencion)
P6  La atención relaciona cualquier par de posiciones en una sola capa. Se propuso para texto, en el
    transformer, y hoy es la base de los modelos de texto y de buena parte de los de imagen. Para
    aplicarla, la entrada se divide en *tokens*: fragmentos de palabra o parches (*patches*) de la
    imagen, cada uno representado por un *embedding*                             define
    ↓ necesidad — cómo decide cada token qué información tomar de los demás
P7  Atención escalada por producto punto: qué representan la consulta, la clave y el valor, con su
    ecuación, por qué se divide por √d_k (una oración) y la Figura 2.3. La atención multicabezal
    (*multi-head attention*), en una oración                                     define
    ↓ limitación — la operación no tiene en cuenta el orden de los tokens
P8  Codificación de posición en dos oraciones: se suma un vector de posición, que el ViT aprende y el Swin
    reemplaza por un sesgo relativo (remite a 2.2.4). El bloque transformer, en prosa: atención y
    perceptrón por token, cada uno con conexión residual (ecuación de P4) y normalización por capa. Una
    pila de bloques forma el codificador; el decodificador, que genera texto, se presenta en 2.3
                                                                                  define (condensado)
    ↓ consecuencia — si los tokens son parches, el mismo codificador clasifica imágenes

2.2.3 Vision Transformer (sec:marco_vit)
P9  El ViT paso a paso: rejilla de parches de 16 × 16 (Figura 2.4), cada parche aplanado y proyectado a
    su *embedding*, la posición aprendida, el token de clase, los bloques y la cabeza sobre el token de
    clase                                                                          define
    ↓ contraste — frente a la CNN, el ViT supone mucho menos sobre las imágenes
P10 **Sesgo inductivo** (*inductive bias*), definido como los supuestos sobre los datos que la arquitectura
    incorpora de antemano. La CNN trae localidad y equivariancia a traslaciones en cada capa; el ViT
    tiene que aprender las relaciones espaciales de los datos. Por eso, preentrenado solo sobre
    *ImageNet* rinde por debajo de CNN comparables, y con 14 a 300 millones de imágenes las supera
    (dato verificado). De ahí la importancia del preentrenamiento (remite a 2.1.3)   justifica
    ↓ problema — además, comparar cada token con todos tiene un costo que crece con el cuadrado del
      número de parches

2.2.4 Swin Transformer (sec:marco_swin)
P11 Atención por ventanas locales de M × M parches y la ecuación del costo: cuadrático en la atención
    global, lineal por ventanas                                                  define · justifica
    ↓ limitación — las ventanas fijas no se comunican entre sí
P12 Ventanas desplazadas (Figura 2.5) y fusión de parches entre etapas, que forman una pirámide
    jerárquica como la de una CNN; la posición como sesgo relativo                 define

(cierre de la sección, sin subsección)
P13 Síntesis: las familias se diferencian en cuánto suponen sobre la imagen. La CNN es local y
    jerárquica; el ViT, global y dependiente del preentrenamiento; el Swin combina la atención con la
    jerarquía. ConvNeXt, con un diseño actualizado, iguala al Swin, de modo que la diferencia no está
    solo en la operación. Por eso el trabajo evalúa representantes de las dos familias, y estos
    clasificadores supervisados son la **línea base** (*baseline*) contra la que se comparan los VLM
                                                                         interpreta · justifica
→ Transición a 2.3: «Ninguno de estos clasificadores produce texto: su salida es una probabilidad por
  clase. Para redactar un reporte hace falta un modelo que genere secuencias de palabras, y los modelos
  de lenguaje actuales se construyen sobre el transformer de la Sección 2.2.2, usado como decodificador.»

Se definen acá (y no se vuelven a definir): convolución, mapa de características, campo receptivo, conexión
residual, *token*, parche (*patch*), *embedding*, atención (consulta, clave, valor), atención multicabezal
(*multi-head attention*), codificación de posición, bloque transformer, codificador, sesgo inductivo
(*inductive bias*), ViT, Swin, línea base (*baseline*).
Se retoman de antes (solo se nombran, con \ref): capa y activación (eq:marco_capa), cabeza y *backbone*,
preentrenamiento y ajuste fino (2.1.3), sobreajuste (2.1.2), la jerarquía de rasgos (introducción de 2.1).
Remisiones hacia adelante: decodificador y modelos de lenguaje (2.3); VLM (2.3).
Extensión: 13 párrafos, unas 4.5 páginas (hoy, 2.2 y 2.3 suman unas 5, p. 37–42).
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor: 2.2 reúne CNN, ViT y Swin, «con énfasis en las características relevantes para los modelos evaluados» | Se reúnen las 2.2 y 2.3 actuales. P1 nombra los cuatro clasificadores del trabajo, y cada arquitectura se explica por lo que la distingue |
| Mensaje: condensar «la explicación individual de varias arquitecturas CNN» | DenseNet y ConvNeXt quedan en un párrafo (P5), sin la fórmula de DenseNet. Sale la ecuación de la convolución, que la Figura 2.2 ya muestra |
| Mensaje: condensar «los aspectos más generales de la arquitectura transformer» | Salen la apertura sobre las redes que procesan secuencias (las RNN no se presentan, decisión vigente 9), la posición sinusoidal, la diferencia entre normalizar antes o después y su ecuación (`eq:marco_bloque`), y la máscara del decodificador (pasa a 2.3). La oración de Kaplan sobre dónde están los parámetros pasa a 2.3, donde la usa LoRA |
| Audio 2: ViT y Swin «necesitan un poco más de trabajo porque es el core» | El ViT se explica paso a paso (P9), el sesgo inductivo se define (hoy se usa sin definir) y el Swin conserva la ecuación del costo, la figura y sus dos párrafos |
| p36, la Figura 2.2 tiene las etiquetas pegadas | Se separan las tres matrices y las etiquetas van en dos líneas. «Mapa de activación» pasa a «mapa de características», como dice el texto |
| p38, «atención multi-cabeza» suena mal | «atención multicabezal (*multi-head attention*)», como fija la tabla de términos de la guía |
| p39, «El ViT lleva a las imágenes el codificador del transformer»: no se entiende | P8 cierra diciendo que el codificador opera sobre cualquier secuencia de tokens, y P9 describe qué hace el ViT con la imagen, paso a paso |
| p40, «cada token atiende a todos los demás»: suena raro | «cada token se compara con todos los demás» |
| p40, «parches» sin el inglés | «parches (*patches*)» en su primera aparición (P6) |
| p41, «Puede enfrentar arquitecturas supervisadas…», «esta segunda dice», «Ninguno» | Sale la subsección de la línea base. Su idea central pasa a P13, y la transición usa «Ninguno de estos clasificadores…». La oración sobre qué hace válida una comparación (mismos datos, particiones y métricas) es metodología y queda para el Cap. 3 |
| Mensaje: transiciones entre aprendizaje profundo, arquitecturas visuales y lenguaje | P1 retoma la limitación con que cierra 2.1, y la transición final anuncia el decodificador de 2.3 |
| Cursiva en los conjuntos de datos | *ImageNet* |

## Archivos y labels

- `02-arquitecturas-imagenes.tex` reemplaza a los dos archivos viejos, y `00-capitulo.tex` pasa a tener un solo
  `\input`. El capítulo queda con 9 secciones.
- `\label{sec:marco_vision}` va en la nueva `\section`. Se conservan `sec:marco_cnn`, `sec:marco_atencion`
  (lo usa 2.4 para las proyecciones de LoRA), `sec:marco_vit` (2.5) y `sec:marco_swin` (2.8), y también
  `eq:marco_residual`, `eq:marco_atencion` y `eq:marco_swin_costo` y las cuatro figuras.
- Salen, porque nadie los cita: `sec:marco_atencion_producto`, `sec:marco_posicion`,
  `sec:marco_bloque_transformer`, `sec:marco_baseline_visual`, `eq:marco_convolucion` y `eq:marco_bloque`.
- Figura de la convolución: `Figures/Capitulos/02-Marco-Teorico/convolucion.tex`.

## Citas

`lecun1998gradient`, `goodfellow2016deep`, `he2015residual`, `huang2018densely`, `liu2022convnet`,
`vaswani2017attention`, `dosovitskiy2021image`, `liu2021swin` y `argenziano1998checklist` (estructuras
dermatoscópicas del ejemplo de la jerarquía). Todas existen en el `.bib`. `kaplan2020scaling`
y `brown2020language` pasan a 2.3.

## Decisiones

1. **Sale la ecuación de la convolución** (autor, 2026-10-11): la Figura 2.2 muestra la operación, y el tutor
   pidió condensar las CNN.

2. **La línea base se define en el cierre de 2.2** (autor, 2026-10-11): ahí se presentan los clasificadores,
   y los Caps. 3 y 4 usan el término. La sección 2.6 no la redefine.

3. **Revisión del autor sobre el texto redactado** (autor, 2026-10-11):
   - La convolución se explica paso a paso: qué codifica el filtro, cómo calcula el producto punto con la
     ventana, un filtro concreto (columnas de pesos positivos, nulos y negativos) que da un valor grande en
     un cambio de claro a oscuro y cero en un tono uniforme, y por qué el mapa de la Figura 2.2 es de 4 × 4.
   - La degradación se ilustra con la red de 56 capas que obtiene más error de entrenamiento que la de 20, y
     se explica por qué no basta con que las capas extra calculen la identidad. La conexión residual se
     define como la suma de la entrada del bloque al resultado de sus capas (sin la palabra «atajo») y se
     explica por qué agregar bloques ya no empeora la red.
   - Ejemplos dermatoscópicos genéricos, sin nombrar conjuntos (decisión vigente 1): el contorno de la lesión
     en la convolución, la jerarquía de rasgos con estructuras de la lesión, el borde opuesto como límite de
     la convolución, y lo que cubre cada parche del ViT. Sale la comparación con el tamaño del conjunto del
     trabajo, porque no aporta teoría y adelanta el Cap. 3.
   - Cada arquitectura se presenta por la limitación de la anterior: la apertura del ViT plantea si un
     transformer sin convoluciones puede clasificar imágenes, y la del Swin nombra los dos problemas que deja
     el ViT (costo cuadrático y una sola escala), que resuelven las ventanas y la fusión de parches.
   - Se quitan repeticiones: la cadena de rasgos simples a complejos, el anuncio del bloque transformer, el
     anuncio de las subsecciones siguientes y la idea de que el Swin recupera localidad y jerarquía, que
     queda solo en la síntesis del cierre.
