# Ficha del Capítulo 2 — Marco teórico

Contrato de contenido del capítulo. Cada sección declara su mensaje central, el esqueleto de
párrafos, las claves de cita que se usan y su extensión. Lo que no está acá no se escribe; lo que
falte se anota como pregunta abierta al entregar la sección.

**Extensión total: a revisar.** El reparto original era: apertura 0,5 · §2.1 2,5 · §2.2 5–5,5 ·
§2.3 2,5–3 · §2.4 4 · §2.5 4,5 · §2.6 3 · §2.7 5–5,5, con un total de 27–30 páginas.

**Lo escrito desmiente ese reparto (22/09/2026).** Con el bloque A terminado, §2.1 ocupa 2 páginas
contra las 2,5 previstas, §2.2 ocupa **3 contra 5–5,5** y §2.3 ocupa 2 contra 2,5–3: 7 páginas donde
el reparto decía 10–11. No falta ningún párrafo —los dieciséis de §2.2 están escritos—, así que el
error está en la estimación y no en el contenido: el plan de párrafos de esta ficha, redactado con
párrafos de 6 líneas, no da para 5 páginas en §2.2. El reparto corregido del bloque A es **§2.1 2 ·
§2.2 3–3,5 · §2.3 2–2,5**.

**Consecuencia, que hay que decidir.** Si los bloques B y C se desvían en la misma proporción, el
capítulo cierra en 20–22 páginas y no en las 25–30 que pide la guía. Estirar la prosa escrita no es
una opción: la guía prohíbe el relleno y el texto actual no tiene grasa. Las dos salidas reales son
ampliar el plan de contenido de B y C —más subsecciones o más profundidad, decididas en la ficha de
cada bloque— o bajar el objetivo del capítulo en la guía. **Se decide al detallar el bloque B.**

**Estado de la bibliografía: resuelto (22/09/2026).** El `.bib` no cubría la clínica, la
calibración, la inferencia estadística ni las métricas de generación modernas; se incorporaron las
**26 referencias** de la auditoría de `refs_pendientes.md`, verificadas contra el editor o el
repositorio oficial, y el archivo pasó de 82 a 108 entradas. Las claves que esa tanda agregó se
marcan con `(p)` en las tablas de esta ficha para distinguirlas de las que ya estaban. Todas son
citable de inmediato.

**La ficha se completa por bloques**, uno por vez, y el autor aprueba cada bloque antes de que se
redacte prosa. Los bloques restantes figuran al final como esquema, sin detalle.

---

## Bloque A — §2.1 a §2.3

Orden de redacción del bloque: §2.2 → §2.3 → **§2.1 al final**, cuando el autor haya incorporado
las referencias clínicas. Las tres secciones quedan en orden de documento dentro del `.tex`.

### Acrónimos que pide este bloque

| Sigla | Expansión | Sección |
|---|---|---|
| `rlhf` | Aprendizaje por refuerzo a partir de retroalimentación humana (*Reinforcement Learning from Human Feedback*) | 2.3.1 |

Los ya declarados que se usan: `cnn`, `vit`, `llm`, `vlm`, `lora`, `peft`, `mel`, `nv`, `bcc`,
`akiec`, `bkl`, `df`, `vasc`. RNN y LSTM **no** se usan como sigla: el recorte de la fuente los
reduce a una mención y se escriben en palabras.

---

## 2.1 Fundamentos clínicos — `sec:marco_clinico`

**Mensaje central.** El diagnóstico dermatológico asigna la lesión a una categoría de un inventario
cerrado con costos de confusión asimétricos, sobre dos modalidades de imagen que no son
intercambiables, y deja un reporte con partes funcionales y un vocabulario finito: eso es lo que
después miden los modelos.

**Extensión: 2 páginas** (tres subsecciones).

**Alcance clínico fijado (22/09/2026).** Es la sección de dominio del trabajo y no un curso de
dermatología: el lector modelo es de Ciencias de la Computación. Cada subsección existe por lo que
aporta a la tarea y a la evaluación, y nada más. §2.1.1 define el espacio de etiquetas del
clasificador —sin saber qué es MEL y qué es AKIEC, las confusiones del Capítulo~\ref{cp:res_clasif}
no significan nada—; §2.1.2 define la diferencia de dominio entre conjuntos —sin ella no se
entiende la comparación entre HAM10000 y SkinCaRe—; §2.1.3 define el formato del texto que se
genera —sin él, las métricas de entidades clínicas de §2.5.3 aparecen de la nada—. Nada de
morfología clínica detallada ni de algoritmos diagnósticos más allá de nombrarlos.

### 2.1.1 Lesiones cutáneas y categorías diagnósticas

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | El objeto clínico: la lesión de piel como alteración visible de la piel; el diagnóstico asigna una categoría, y esa asignación es lo que el trabajo modela como clasificación | La tarea de clasificación tiene objeto y espacio de salidas definidos por la clínica, no por el modelo | — |
| 2 | Las siete categorías de HAM10000, con lo que designa cada sigla —MEL melanoma, NV nevo melanocítico, BCC carcinoma basocelular, AKIEC queratosis actínica / carcinoma intraepitelial, BKL lesión queratósica benigna, DF dermatofibroma, VASC lesión vascular— y su orden según la gravedad: benignas, premalignas y malignas | El espacio de etiquetas del trabajo es el de HAM10000 y su gravedad no se reduce a un bit | `tschandl2018ham10000` |
| 3 | Costos asimétricos de la confusión: confundir MEL con NV retrasa la extirpación de una lesión cuya letalidad depende del estadio; confundir NV con MEL lleva a extirpar una lesión benigna sin necesidad; las confusiones entre clases benignas pesan menos | No todas las confusiones del clasificador cuestan lo mismo; sostiene las métricas por clase del Capítulo~\ref{cp:res_clasif} | `tschandl2018ham10000`, `nci2026melanoma` |

**Qué no va.** Epidemiología ni cifras de incidencia: ya están en §1.1 y la guía prohíbe
recapitular. Tampoco la descripción de las imágenes: eso es §2.1.2. Ni sintomatología ni criterios
clínicos de diagnóstico: fuera del alcance del trabajo.

### 2.1.2 Dermatoscopía y fotografía clínica

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Dos modalidades de la misma lesión: la fotografía clínica la registra tal como se ve a simple vista; la dermatoscopía la examina con aumento e iluminación controladas | Son dos observaciones distintas, con resolución y contenido distintos | `kittler2002diagnostic`, `vestergaard2008dermoscopy` |
| 2 | Qué añade la dermatoscopía y por qué la mejora depende de la formación de quien examina: sin entrenamiento específico no aventaja a la inspección simple | La modalidad no basta; el criterio interpretativo se entrena | `kittler2002diagnostic`, `vestergaard2008dermoscopy` |
| 3 | Consecuencia para el aprendizaje automático: las dos modalidades no son intercambiables como material de entrenamiento porque la distribución de los rasgos cambia entre ellas; HAM10000 es dermatoscópico y SkinCaRe es de fotografía clínica | Prepara el análisis de conjuntos de `sec:marco_datos_sesgo` y cualquier transferencia entre conjuntos del Capítulo~\ref{cp:metodos} | `tschandl2018ham10000`, `shen2025skincare` |

**Qué no va.** La modalidad del resto de los conjuntos —HIBA, MM-Skin, Derm1M— se declara en
§2.6, en el cuadro comparativo. Acá solo HAM10000 y SkinCaRe, que es el par que el esqueleto fija.
Ni física óptica ni técnica de adquisición.

### 2.1.3 El reporte dermatológico

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Las dos partes del reporte de las que se ocupa el trabajo —descripción e impresión diagnóstica—, que son las que anotan los conjuntos de pares imagen--texto; el diferencial y la recomendación de manejo quedan fuera | El reporte es un texto con partes funcionales identificables y el trabajo se pronuncia sobre dos de ellas | `shen2025skincare` |
| 2 | Vocabulario del reporte: un inventario finito de términos para color, patrón, forma y distribución, estandarizado por consenso; dentro de él, la lista de 7 puntos convierte hallazgos visuales en peso diagnóstico | El vocabulario clínico es finito, condición para medir la riqueza clínica de un texto generado | `kittler2016standardization` (p), `argenziano1998checklist` (p) |
| 3 | Los criterios nombrados no son estables entre observadores: la concordancia sobre los criterios dermatoscópicos va de pobre a moderada. Cierre hacia la evaluación: un reporte correcto exige diagnóstico acertado y descripción fiel, las dos condiciones de la Figura~\ref{fig:intro_dos_tareas}, y las métricas de riqueza clínica del Capítulo~\ref{cp:metodos} se definen sobre este vocabulario | El puente entre imagen y diagnóstico pasa por criterios que varían entre observadores; instala la distinción entre fidelidad diagnóstica y calidad del texto | `carrera2016validity` (p) |

**Qué no va.** Ni ejemplos de reportes escritos por el trabajo (eso es Capítulo~\ref{cp:res_gen})
ni la rúbrica de evaluación con especialistas (apéndice, pendiente). Ni un glosario morfológico
completo: solo los términos que después aparecen en las métricas.

---

## 2.2 Aprendizaje profundo para visión — `sec:marco_vision`

**Mensaje central.** Dos familias de arquitectura conviven en el comparativo —convolucionales
modernas y *transformers* visuales— y todas parten de representaciones pre-entrenadas; el desbalance
del conjunto se ataca en la pérdida, no en la métrica.

**Extensión: 3–3,5 páginas** (la estimación original decía 5–5,5; ver el encabezado de la ficha).

**Recorte de la fuente.** De `Docs/marco_teorico/Documento_LLMs_VLLMs.tex` se toma solo
convolución, jerarquía de características, atención y ViT. MLP y aproximación universal, VGG,
ResNet, EfficientNet, RNN, LSTM, one-hot y NLP general quedan fuera; VGG y ResNet entran como
hito nombrado en §2.2.1 ¶2, sin desarrollo.

### 2.2.1 Redes convolucionales

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | La operación de convolución: el kernel se desliza sobre la entrada, con conectividad local y pesos compartidos; la red entera es una composición de esas operaciones | La convolución codifica el supuesto de estructura local estacionaria en la imagen | `lecun1998gradient` (p) |
| 2 | Jerarquía de características: con la profundidad, la red compone bordes en texturas, texturas en partes y partes en objetos; VGG y ResNet fijaron el repertorio de bloques que las arquitecturas actuales refinan | La profundidad compone rasgos locales en rasgos semánticos | `simonyan2015very`, `he2015residual` |
| 3 | DenseNet: conexiones densas entre capas, cada capa recibe las características de todas las anteriores; la reutilización reduce parámetros sin perder capacidad, y con conjuntos del orden de las decenas de miles de imágenes esa economía importa | DenseNet es una de las dos arquitecturas convolucionales del comparativo | `huang2018densely`, `he2015residual` |
| 4 | ConvNeXt: una ResNet modernizada con las decisiones de diseño del *transformer* —kernels de mayor tamaño, menos no-linealidades, normalización por capa— que iguala al Swin manteniendo el molde convolucional | El contraste CNN–*transformer* del Capítulo~\ref{cp:res_clasif} enfrenta arquitecturas contemporáneas, no una CNN obsoleta | `liu2022convnet` (p) |

### 2.2.2 Transformers y mecanismo de atención

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | La atención como direccionamiento por contenido: cada posición pondera los valores de todas las demás según la compatibilidad entre consulta y clave, sin recurrencia ni convolución | La atención sustituye la secuencialidad por comparación global entre posiciones | `vaswani2017attention` |
| 2 | Atención escalada por producto punto: proyecciones de consulta, clave y valor, y $\mathrm{softmax}(QK^{\top}/\sqrt{d})V$ (`eq:marco_atencion`); el escalado por la raíz de la dimensión evita que el producto punto sature la softmax | Definición formal que usan todas las arquitecturas siguientes | `vaswani2017attention` |
| 3 | Atención multi-cabeza: proyecciones a subespacios más pequeños, atención por cabeza y concatenación; cada cabeza captura relaciones de distinto tipo | La composición de cabezas amplía la representación sin aumentar la dimensión total | `vaswani2017attention` |
| 4 | Arquitectura codificador–decodificador: el codificador contextualiza la entrada y el decodificador genera la salida token a token; en este trabajo el codificador procesa la imagen y el decodificador, el texto | Instala el esquema que reutilizan los modelos multimodales de §2.4 | `vaswani2017attention` |

### 2.2.3 Vision Transformer y Swin Transformer

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | ViT: la imagen se divide en parches, cada parche se aplana y proyecta a un token, y la secuencia pasa por un codificador *transformer* con embebidos de posición | En el ViT la imagen es una secuencia y no hay operación convolucional | `dosovitskiy2021image`, `vaswani2017attention` |
| 2 | Sesgo inductivo: el ViT no incorpora localidad ni equivariancia de escala; con datos de pre-entrenamiento amplios supera a las CNN, y con datos escasos la relación se invierte | Condiciones bajo las cuales el ViT es preferible, decisivas con conjuntos médicos | `dosovitskiy2021image` |
| 3 | Swin: atención por ventanas, con costo lineal en el número de parches; ventanas desplazadas entre capas para conectar regiones; representación jerárquica tipo pirámide, con el mapa de características reduciéndose por etapas | El Swin devuelve mapas multiescala y no una única resolución, y por eso sirve de backbone más allá de la clasificación | `liu2021swin` |
| 4 | Cierre: DenseNet y ConvNeXt del lado convolucional, ViT y Swin del lado *transformer*, son las cuatro estrategias que se enfrentan en el Capítulo~\ref{cp:res_clasif} sobre el mismo material | Instala el eje del comparativo de clasificación | — |

**Figura: aprobada (22/09/2026).** `fig:marco_vit_patches` en `Figures/Capitulos/02-vit-patches.tex`,
TikZ, con los estilos de `13-Figuras.sty`: imagen → rejilla de parches → secuencia de tokens con
embebido de posición. Va después de ¶1, con el flotante completo en el archivo.

### 2.2.4 Transferencia de aprendizaje y desbalance de clases

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Transferencia de aprendizaje: representaciones aprendidas sobre un corpus grande de imágenes se reutilizan para la tarea de destino; la extracción de características congela el backbone y el ajuste fino lo actualiza | Justifica no entrenar desde cero con un conjunto de decenas de miles de imágenes | `pan2010survey` |
| 2 | El pre-entrenamiento en ImageNet es la inicialización estándar de los backbones visuales, y todos los clasificadores del trabajo parten de ahí | El punto de partida común hace comparables las arquitecturas | `russakovsky2015imagenet` (p), `he2015residual` |
| 3 | Aumento de datos: rotaciones, recortes, desplazamientos y cambios de color como regularizador; amplía la cobertura del espacio de imágenes pero no la de las clases raras | El aumento regulariza y no corrige el desbalance | `shorten2019survey` |
| 4 | Desbalance: la distribución de clases de HAM10000 es muy asimétrica y la exactitud sobre la mayoría esconde el desempeño sobre las minorías; tres respuestas en la función de pérdida —pesos por clase, pérdida focal, *balanced softmax*— se enfrentan en el Capítulo~\ref{cp:res_clasif} | Instala las estrategias evaluadas y el porqué de evaluarlas | `tschandl2018ham10000`, `lin2017focal` (p), `ren2020balanced` (p) |

**Qué no va.** Ni resultados propios ni la tabla de arquitecturas comparadas: son
Capítulo~\ref{cp:res_clasif}. Ni perplejidad ni métricas de generación: §2.5.

---

## 2.3 Modelos de lenguaje — `sec:marco_llm`

**Mensaje central.** Un gran modelo de lenguaje es un predictor del siguiente token pre-entrenado
en corpus grandes, y el ajuste con LoRA lo hace asequible en hardware de consumo sin cambiar su
inferencia.

**Extensión: 2–2,5 páginas.**

### 2.3.1 Grandes modelos de lenguaje

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Mención breve de la etapa previa: redes recurrentes y redes de memoria a corto y largo plazo procesaban la secuencia paso a paso, y la atención las superó en alcance y paralelismo | Marco histórico mínimo, sin desarrollar arquitecturas que el trabajo no usa | `elman1990finding` |
| 2 | Modelado de lenguaje como predicción del siguiente token; el pre-entrenamiento es auto-supervisado sobre corpus de miles de millones de palabras | Define la tarea con la que se obtienen los LLMs actuales | `brown2020language`, `touvron2023llama` |
| 3 | Familias arquitectónicas: solo-codificador para representación, solo-decodificador para generación; el componente de lenguaje del trabajo pertenece a la segunda | Delimita qué LLM entra en el *pipeline* | `devlin2019bert`, `brown2020language`, `touvron2023llama` |
| 4 | Ciclo de vida: pre-entrenamiento, ajuste fino supervisado y alineación con retroalimentación humana; cada etapa cambia el comportamiento del modelo sin cambiar su arquitectura | Los tres estados en que se puede usar un LLM | `ouyang2022training` |
| 5 | Decodificación: búsqueda codiciosa y búsqueda por haz (*beam search*) frente a muestreo; temperatura, *top-k* y muestreo de núcleo; el muestreo evita la degeneración textual pero introduce varianza entre corridas | La estrategia de decodificación es un hiperparámetro del generador y afecta a todo lo que se mida sobre él | `holtzman2020curious` (p) |

### 2.3.2 Ajuste eficiente de parámetros: LoRA

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Costo del ajuste fino completo: gradientes y estados del optimizador para todos los parámetros; para modelos de miles de millones eso excede la memoria de una GPU de consumo | El cuello de botella del ajuste es de memoria | `hu2021lora` |
| 2 | Formulación de LoRA: sobre los pesos congelados $W$ se añade un incremento de bajo rango $BA$, con $B\in\mathbb{R}^{d\times r}$, $A\in\mathbb{R}^{r\times k}$ y $r\ll\min(d,k)$; solo $A$ y $B$ se entrenan (`eq:marco_lora`) | Definición formal de la técnica que hace viable todo el trabajo | `hu2021lora` |
| 3 | Efecto sobre la huella de memoria: los parámetros entrenables y sus estados del optimizador caen órdenes de magnitud, y al terminar el ajuste los adaptadores se fusionan en $W$ sin costo de inferencia | Es lo que permite ajustar en el presupuesto de 12–36 GB que fija §1.4 | `hu2021lora`, `yilmaz2025resourceefficient` |
| 4 | Cierre: los modelos adaptados del trabajo se ajustan con LoRA, y la configuración concreta de rango, módulos y objetivo va en el Capítulo~\ref{cp:metodos} | Instala la restricción de cómputo como decisión de diseño y no como limitación | — |

**Qué no va.** Ni destilación de conocimiento —no es eje del trabajo; se menciona donde aparece en
el estado del arte, §2.7.3— ni RAG —va en §2.4.4— ni leyes de escalado.

---

## Propuesta del 25/09/2026 — fundamentos e hilo conductor (aprobada y redactada el 25/09/2026)

**Estado.** §2.1 redactada; apertura del capítulo con `fig:marco_mapa`; aperturas y cierres de visión y lenguaje reescritos. Figuras hechas: mapa, perceptrón, convolución, atención, Swin y LoRA. Quedan para cuando se redacten sus secciones (bloques B y C): CLIP, LLaVA, diagrama de confiabilidad y dermatoscopía frente a fotografía clínica. Las cuatro referencias nuevas figuran como indefinidas hasta que se incorporen al `.bib` (entradas listas en `refs_pendientes.md`).

Responde dos observaciones del autor: el capítulo arranca en la atención sin haber presentado qué es
una red neuronal ni cómo se entrena, y las secciones se leen como conceptos sueltos, sin un hilo que
las una. **Nada de esto se redacta hasta que el autor lo apruebe.**

### Nueva §2.1 Fundamentos del aprendizaje profundo — `sec:marco_fundamentos`

**Mensaje central.** Una red neuronal es una composición de transformaciones con parámetros que se
ajustan minimizando una pérdida por descenso del gradiente; lo que se aprende sobre entrenamiento
solo vale si se sostiene en datos que el modelo no vio. Solo entra lo que el resto del documento usa.

**Extensión: 3–3,5 páginas.** No es un curso: cada concepto figura porque un capítulo posterior lo
nombra.

| # | Subsección / párrafo | Por qué hace falta (dónde se usa después) | Citas |
|---|---|---|---|
| 1 | Neurona artificial y perceptrón multicapa: suma ponderada, activación no lineal, capas apiladas | Base de todas las arquitecturas; la cabeza de clasificación y el proyector de LLaVA son perceptrones | `rumelhart1986learning`, `goodfellow2016deep` (p) |
| 2 | Clasificación: *logits*, softmax, probabilidad por clase, entropía cruzada como pérdida | Balanced softmax (§2.3.4), calibración y *temperature scaling* (§2.6.2), *likelihood scoring* (Cap. 3) | `goodfellow2016deep` (p) |
| 3 | Entrenamiento: descenso del gradiente estocástico, retropropagación, lotes, épocas, tasa de aprendizaje, Adam | LoRA (§2.4.2) razona en términos de gradientes y estados de Adam; hiperparámetros del Cap. 3 | `rumelhart1986learning`, `kingma2015adam` (p) |
| 4 | Generalización: sobreajuste, partición entrenamiento/validación/test, regularización (decaimiento de pesos, *dropout*, aumento de datos) y selección del *checkpoint* en validación | Criterio de selección del Cap. 3, fuga entre particiones, §2.7 | `goodfellow2016deep` (p), `srivastava2014dropout` (p) |
| 5 | Familias según la estructura de la entrada: perceptrón para vectores, convolucionales para grillas (se desarrollan en §2.3), recurrentes para secuencias. Las recurrentes con su límite (dependencias largas), que motiva la atención | Hace de puente a §2.2; recupera la mención de RNN/LSTM que hoy abre la sección de atención | `elman1990finding`, `hochreiter1997long` (p) |

**Figura propuesta:** perceptrón multicapa con el paso hacia adelante y la retropropagación del
gradiente en sentido inverso (TikZ, en color).

### Hilo conductor del capítulo

**Diagnóstico.** Las secciones se presentan como conceptos independientes. En la revisión del
25/09 se quitaron las frases de traspaso por vacías («falta el mecanismo que le hace llegar la
imagen»), y no se reemplazaron por nada: el problema no eran los traspasos sino que no dijeran nada
concreto.

**Propuesta.** El capítulo recorre el *pipeline* en el orden en que lo atraviesa un caso: la imagen
se representa (visión), la representación se vuelve texto (lenguaje), las dos modalidades se unen
(VLM), la salida se juzga (evaluación) y se pregunta cuándo deja de valer lo medido (generalización).

1. **Apertura del capítulo** (reemplaza el `\pendiente` inicial, que era del bloque C): presenta ese
   recorrido con una **figura mapa**, el *pipeline* simplificado (imagen → clasificador y kNN →
   generador → reporte → evaluación) con cada componente rotulado con la sección que lo explica.
2. **Cada sección abre situándose en el mapa** con una o dos oraciones («El primer componente del
   *pipeline* recibe la imagen…») y **cierra con el problema concreto que deja abierto** y que la
   siguiente resuelve. Ejemplo para el cierre de visión: un clasificador entrega una distribución
   sobre siete categorías y ningún texto; producir el reporte exige un modelo que genere secuencias.
3. Orden resultante: §2.1 Fundamentos · §2.2 Transformers y atención · §2.3 Visión · §2.4 Lenguaje
   · §2.5 Modelos visión--lenguaje · §2.6 Evaluación · §2.7 Sesgo y generalización · §2.8 Estado
   del arte.

### Figuras propuestas para el capítulo

TikZ propio salvo indicación. «Adaptada de» = redibujada a partir de la figura del trabajo citado.

| Figura | Sección | Origen |
|---|---|---|
| Mapa del capítulo sobre el *pipeline* | apertura | propia |
| Perceptrón multicapa y retropropagación | §2.1 | propia |
| Convolución: filtro que recorre la imagen y mapa de activación | §2.3.1 | propia |
| Atención: $Q$, $K$, $V$, matriz de pesos y salida | §2.2 | propia, o tomada de `vaswani2017attention` (Google autoriza reproducir sus figuras en trabajos académicos con atribución) |
| Ventanas desplazadas del Swin | §2.3.2 | adaptada de `liu2021swin` |
| LoRA: $W$ congelada en paralelo con $B A$ | §2.4.2 | adaptada de `hu2021lora` |
| CLIP: matriz de similitud imagen--texto del entrenamiento contrastivo | §2.5.1 | adaptada de `radford2021learning` |
| Arquitectura tipo LLaVA: codificador visual, proyector y LLM | §2.5.2 | adaptada de `liu2023visual` |
| Diagrama de confiabilidad ilustrativo | §2.6.2 | propia, con datos sintéticos rotulados como tales |
| Misma lesión en dermatoscopía y en fotografía clínica | §2.7 | imágenes de los conjuntos, con su licencia |

Para el Capítulo 3 quedan anotadas: mosaico de las siete clases de HAM10000 (licencia CC BY-NC 4.0,
compatible con atribución), distribución de clases, esquema de la fuga entre particiones y el
diagrama del *pipeline* ya previsto.

---

## Bloque B — §2.5 Modelos visión--lenguaje y §2.6 Evaluación (aprobado y redactado el 25/09/2026)

Numeración nueva (decisión 14). Cada sección abre situándose en el *pipeline* y cierra con lo que deja
abierto, como pide el hilo conductor.

### Acrónimos que pide este bloque

| Sigla | Expansión | Sección |
|---|---|---|
| `mce` | Error de calibración máximo (*Maximum Calibration Error*) | 2.6.2 |

Ya declarados que se usan: `vlm`, `clip`, `llm`, `rag`, `knn`, `ece`, `auc`, `lora`, `mel`, `nv`.
Los nombres de métricas de texto (BLEU, ROUGE-L, METEOR, CIDEr, BERTScore) y Grad-CAM **no** se
declaran como acrónimo: se usan como nombres propios, igual que en la literatura.

---

## 2.5 Modelos visión--lenguaje — `sec:marco_vlm`

**Mensaje central.** Hay dos maneras de unir imagen y texto: alinearlos en un espacio común
(contrastivo, sirve para clasificar y recuperar) o inyectar la imagen en un LLM (generativo, sirve para
redactar). El *pipeline* usa las dos, y la generación médica tiene fallas propias que la evaluación
tiene que poder ver.

**Extensión: 4–4,5 páginas.**

**Apertura (1 párrafo).** El LLM de §2.4 solo recibe texto; esta sección presenta las dos formas de
conectarlo con la imagen y qué papel cumple cada una en el *pipeline* (DermLIP para clasificar y
recuperar vecinos, el generador para redactar).

### 2.5.1 Alineación contrastiva: CLIP

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Dos codificadores, uno de imagen y uno de texto, proyectan a un espacio común; el entrenamiento contrastivo sobre pares imagen--texto acerca los *embeddings* de cada par y aleja los de pares distintos dentro del lote | La alineación produce un espacio donde la similitud entre imagen y texto es medible | `radford2021learning` |
| 2 | Clasificación *zero-shot*: cada clase se escribe como texto («una imagen dermatoscópica de un melanoma»), y la imagen se asigna a la clase cuyo *embedding* de texto está más cerca; el resultado depende de cómo se redacta el *prompt* | Un modelo contrastivo clasifica sin ajuste, y la redacción del *prompt* es parte del clasificador | `radford2021learning` |
| 3 | *Linear probe* y vecinos: congelando el codificador de imagen, un clasificador lineal o un kNN sobre los *embeddings* aprovechan la representación con pocas etiquetas | Instala los modos de uso de DermLIP del Cap. 3 y la búsqueda de vecinos de §2.5.4 | `radford2021learning` |
| 4 | Pre-entrenamiento de dominio: el mismo esquema sobre pares dermatológicos (Derm1M) da DermLIP; un modelo entrenado sobre imágenes generales no conoce el vocabulario clínico | Justifica usar un modelo contrastivo especializado y no el CLIP original | `yan2025derm1m` |

**Figura:** matriz de similitud imagen--texto del lote, con la diagonal de pares correctos resaltada
(`fig:marco_clip`, adaptada de `radford2021learning`, TikZ).

### 2.5.2 Modelos multimodales generativos

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Esquema LLaVA: un codificador visual tipo CLIP, un proyector (perceptrón, §2.1.1) que lleva los rasgos visuales a la dimensión de los *embeddings* del LLM, y un LLM de solo decodificador que recibe los tokens visuales como prefijo del texto | Un VLM generativo es un LLM con una entrada visual adicional, no un codificador--decodificador | `liu2023visual` |
| 2 | Alternativa con consultas aprendidas (Q-Former de BLIP-2), que resume la imagen en un número fijo de tokens; se nombra para mostrar que el puente entre las dos partes es una decisión de diseño | El proyector no es único; condiciona cuánta información visual llega al LLM | `li2023blip2` |
| 3 | *Visual instruction tuning* en dos etapas: primero se entrena solo el proyector sobre pares imagen--leyenda, después el conjunto sobre instrucciones visuales | Así se obtiene un VLM que responde instrucciones sobre una imagen | `liu2023visual` |
| 4 | Adaptación al dominio médico: LLaVA-Med repite la receta con figuras y leyendas de artículos biomédicos; modelos pequeños como Phi-3.5-Vision permiten ajustar con LoRA en hardware de consumo; SkinVL aplica la receta a dermatología con texto de libros de referencia | Instala los tres generadores del trabajo como variantes de un mismo esquema | `li2023llavamed`, `abdin2024phi3`, `zeng2025mmskin` |

**Figura:** arquitectura tipo LLaVA — imagen → codificador visual → proyector → tokens visuales +
tokens de la instrucción → LLM → texto (`fig:marco_llava`, adaptada de `liu2023visual`, TikZ).

### 2.5.3 Generación de texto a partir de imágenes médicas

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | De *image captioning* a la redacción de reportes: la tarea nace en radiología, donde el reporte es largo, estructurado y mayormente normal; requiere pares imagen--texto clínico | La generación de reportes es una tarea con datos y formato propios | `jing2018automatic`, `chen2020generating` |
| 2 | En dermatología los pares son escasos y recientes (SkinCaRe, MM-Skin, Derm1M), y el texto combina descripción e impresión diagnóstica | Sitúa los datos que el trabajo usa para ajustar | `shen2025skincare`, `zeng2025mmskin`, `yan2025derm1m` |
| 3 | Alucinación: el modelo describe hallazgos que la imagen no tiene, con la misma fluidez que los reales | Primera falla característica; un texto fluido no es un texto fiel | `gu2024medvh` |
| 4 | *Hedging*: descripciones genéricas, compatibles con cualquier lesión, que evitan comprometer un diagnóstico | Segunda falla; un texto sin errores puede no decir nada | ver pregunta abierta 4 |
| 5 | Dos condiciones de un reporte correcto, retomando `fig:intro_dos_tareas`: fidelidad diagnóstica (la categoría es la acertada) y calidad del texto (la descripción corresponde a la imagen). Pueden fallar por separado, y la evaluación de §2.6.3 mide las dos | Instala la distinción sobre la que se apoya el Cap. de resultados de generación | — |

### 2.5.4 Generación aumentada por recuperación

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | RAG: el generador recibe, además de la entrada, documentos recuperados de una base externa, y condiciona el texto en ellos; separa lo que el modelo sabe de lo que se le muestra | La recuperación aporta evidencia sin reentrenar | `lewis2020retrievalaugmented` |
| 2 | Recuperación por vecinos: la búsqueda se hace por similitud de *embeddings*; los k vecinos más cercanos de la entrada aportan casos parecidos cuya información se usa en la predicción | kNN sobre *embeddings* como mecanismo de recuperación | `khandelwal2020generalization` |
| 3 | Variante multimodal en generación de reportes médicos: se recuperan imágenes parecidas y sus textos para anclar el reporte en hechos | Precedente directo del *grounding* por recuperación del *pipeline* | `sun2025factaware` |
| 4 | Cierre: el *pipeline* recupera los vecinos visuales con DermLIP (§2.5.1) y el acuerdo entre vecinos y clasificador informa la incertidumbre; el detalle va en Cap. 3. Queda abierto cómo juzgar la salida → §2.6 | Instala el uso de kNN del *pipeline* | — |

**Qué no va.** Ni resultados propios, ni prompts, ni la cascada (Cap. 3, `sec:met_pipeline`), ni la
clasificación con VLMs generativos (Cap. 3, `sec:met_clasif_vlm`). Ni la revisión de modelos
dermatológicos concretos más allá de nombrarlos: eso es el estado del arte.

---

## 2.6 Evaluación de modelos — `sec:marco_evaluacion`

**Mensaje central.** Cada salida del *pipeline* se juzga con una familia de métricas distinta —la
etiqueta, la probabilidad y el texto—, cada métrica ve una parte y no otra, y una diferencia entre dos
modelos solo cuenta si supera la variación del conjunto de test.

**Extensión: 4,5–5 páginas.**

**Apertura (1 párrafo).** Qué se evalúa de cada componente: la clase (§2.6.1), la probabilidad que la
acompaña (§2.6.2), el texto (§2.6.3); cómo se decide si dos modelos difieren (§2.6.4) y qué miró el
modelo (§2.6.5).

### 2.6.1 Métricas de clasificación

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Matriz de confusión; sensibilidad y especificidad para la tarea binaria (melanoma frente al resto) | Definiciones base | `fawcett2006introduction` |
| 2 | Exactitud engañosa: con NV en torno a dos tercios de HAM10000, predecir siempre NV da exactitud alta y sensibilidad nula en MEL | La exactitud no sirve con clases desbalanceadas (retoma §2.3.4) | `tschandl2018ham10000` |
| 3 | F1 por clase; promedio macro (todas las clases pesan igual) frente a ponderado (pesa por soporte); sensibilidad macro | Qué promedio refleja las clases minoritarias | — (definiciones) |
| 4 | Curva ROC y AUC: desempeño a lo largo de todos los umbrales, independiente del umbral elegido; uno contra el resto en el caso multiclase | Métrica que no depende de fijar un umbral | `fawcett2006introduction` |

Ecuaciones: F1 y promedio macro (`eq:marco_f1`).

### 2.6.2 Calibración de probabilidades

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Un modelo está calibrado cuando, entre las predicciones con confianza 0.8, acierta el 80 %; las redes profundas modernas tienden a ser sobreconfiadas | La probabilidad de salida no es una confianza confiable por defecto | `guo2017calibration` |
| 2 | Diagrama de confiabilidad; ECE como brecha media ponderada entre confianza y exactitud por intervalo; MCE como la brecha máxima (`eq:marco_ece`) | Cómo se mide la calibración | `guo2017calibration` |
| 3 | Puntaje de Brier: error cuadrático entre la probabilidad y el resultado; mezcla calibración y discriminación | Métrica complementaria, sin intervalos | `brier1950verification` |
| 4 | Calibración post-hoc sobre validación: *temperature scaling* (un escalar que divide los *logits*) y *vector scaling* (un factor y un sesgo por clase); no cambian la clase predicha | La calibración se corrige después del entrenamiento sin tocar la exactitud; importa porque el *pipeline* usa la confianza para rutear | `guo2017calibration` |

**Figura:** diagrama de confiabilidad ilustrativo, con datos sintéticos rotulados como tales
(`fig:marco_confiabilidad`, propia, TikZ/pgfplots).

### 2.6.3 Métricas de generación de texto

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Con referencia, por solapamiento de n-gramas: BLEU (precisión de n-gramas con penalización por brevedad), ROUGE-L (subsecuencia común más larga), METEOR (alineación con sinónimos y raíces), CIDEr (n-gramas ponderados por TF-IDF contra varias referencias) | Qué compara cada una | `papineni2002bleu`, `lin2004rouge`, `banerjee2005meteor`, `vedantam2015cider` |
| 2 | Con referencia, semántica: BERTScore compara *embeddings* contextuales token a token y tolera paráfrasis | Supera la coincidencia literal, pero sigue midiendo parecido con un texto | `zhang2020bertscore` |
| 3 | (escrito) Límite de las métricas con referencia: variabilidad entre observadores | — | `carrera2016validity` |
| 4 | (escrito) Vocabulario finito como base de las métricas sin referencia | — | `kittler2016standardization`, `argenziano1998checklist` |
| 5 | Métricas sin referencia del trabajo, como concepto: cobertura de entidades clínicas (cuántos términos del vocabulario menciona el reporte) y consistencia diagnóstica (si el texto nombra la categoría correcta). Qué ve cada familia: las con referencia premian el parecido de forma, las sin referencia la presencia de contenido clínico, y ninguna detecta por sí sola una alucinación. La definición operativa va en Cap. 3 | Conecta con las dos condiciones de §2.5.3 | — |

### 2.6.4 Inferencia estadística para comparar modelos

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | El conjunto de test es una muestra; una diferencia de métricas puede deberse a qué imágenes cayeron en él | Una diferencia sin medida de incertidumbre no es un resultado | — |
| 2 | *Bootstrap*: se remuestrea el test con reposición para obtener la distribución de la métrica; pareado, se remuestrean las mismas imágenes para los dos modelos y se obtiene un intervalo para la diferencia | Intervalos para métricas agregadas (F1 macro, AUC) | `efron1979bootstrap` |
| 3 | McNemar: sobre los mismos casos, cuenta solo los discordantes (uno acierta y el otro no) y prueba si están desbalanceados | Comparación de aciertos por imagen | `mcnemar1947note` |
| 4 | Wilcoxon de rangos con signo: diferencias pareadas por clase, sin suponer normalidad; recomendado para comparar clasificadores | Comparación de la sensibilidad por clase | `wilcoxon1945individual`, `demsar2006statistical` |

### 2.6.5 Interpretabilidad visual

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Grad-CAM: pondera los mapas de activación de la última capa convolucional por el gradiente de la clase y produce un mapa de calor de las regiones que más influyeron en ella | Qué regiones de la imagen usó el clasificador | `selvaraju2017gradcam` |
| 2 | Límites: resolución de la última capa (mapas gruesos), muestra dónde miró el modelo y no por qué; no valida que la decisión sea correcta. Cierre hacia §2.7: un modelo puede atender a artefactos del conjunto | Grad-CAM sirve para detectar atajos, no para certificar el razonamiento | `selvaraju2017gradcam` (ver pregunta abierta 5) |

**Qué no va.** Ni los valores obtenidos, ni la elección de la métrica de selección (Cap. 3,
`sec:met_seleccion`), ni la rúbrica con especialistas (apéndice). Ni perplejidad ni métricas con LLM
como juez: el trabajo no las usa.

---

## Bloque C — §2.7 Sesgo y generalización y §2.8 Estado del arte (aprobado y redactado el 25/09/2026)

Numeración nueva (decisión 14). Todo número que aparezca en la prosa o en las tablas se verifica
contra el PDF del trabajo citado al redactar; `Docs/estado_del_arte/resumen_papers.tex` y
`Docs/tabla_resultados_sota/` sirven de guía, no de fuente.

### Referencias nuevas que pide este bloque

| Clave | Trabajo | Uso |
|---|---|---|
| `koh2021wilds` | Koh et al., *WILDS: A Benchmark of in-the-Wild Distribution Shifts*, ICML 2021 (PDF ya en `Papers/`) | Definición de cambio de distribución, §2.7 ¶1. Se agrega al `.bib` al aprobarse el bloque |

---

## 2.7 Sesgo y generalización — `sec:marco_generalizacion`

**Mensaje central.** Lo medido en una partición del conjunto de entrenamiento vale para esa
distribución; en dermatología la distribución cambia con la modalidad, con el tono de piel y con la
población, y un modelo puede además apoyarse en artefactos del conjunto. Por eso el trabajo evalúa
fuera de distribución.

**Extensión: 2–2,5 páginas.**

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Cambio de distribución: el modelo aprende la distribución de entrenamiento; en uso real las imágenes vienen de otra, y el desempeño medido en test no se transfiere. Dos casos: cambio de dominio (otra fuente de datos) y cambio de subpoblación (otras proporciones de grupos) | Una métrica de test es condicional a la distribución del test | `koh2021wilds` |
| 2 | (escrito) Cambio de modalidad: dermatoscopía frente a fotografía clínica; HAM10000 frente a SkinCaRe | — | `dinnes2018dermoscopy`, `kittler2016standardization`, `tschandl2018ham10000`, `shen2025skincare` |
| 3 | Atajos: un modelo puede asociar la clase a artefactos que acompañan a ciertas lesiones en el conjunto, como marcas de tinta o reglas; auditando conjuntos dermatológicos con un modelo contrastivo se encontraron marcas de tinta asociadas a malignidad. Retoma el cierre de Grad-CAM (§2.6.5) | Una exactitud alta puede apoyarse en rasgos que no existen fuera del conjunto | `kim2024transparent` |
| 4 | Tono de piel: en Fitzpatrick17k, los modelos entrenados con pieles claras rinden peor en pieles oscuras; en DDI, algoritmos con AUC alto en sus conjuntos de origen caen mucho y muestran diferencias entre tonos claros y oscuros; el ajuste con datos diversos reduce la brecha | La subrepresentación de un grupo produce disparidades medibles | `groh2021neural`, `daneshjou2022disparities` |
| 5 | La disparidad también afecta la colaboración con el médico: con apoyo de IA mejora la exactitud general de dermatólogos y médicos de atención primaria, pero en los segundos la brecha entre tonos se amplía | Mejorar el promedio no reduce el sesgo | `groh2024learningaided` |
| 6 | Población: la mayoría de los algoritmos no se valida en poblaciones de baja prevalencia ni en atención primaria; el conjunto del Hospital Italiano de Buenos Aires (HIBA) se creó para evaluar herramientas de IA en población argentina. Cierre: el trabajo evalúa en HIBA sin entrenar sobre él y bajo perturbaciones de adquisición (Cap. 3) | Motiva la evaluación fuera de distribución del trabajo | `jones2022intelligence`, `riccilara2023dataset` |

**Qué no va.** Ni resultados propios en HIBA, ni la descripción de los conjuntos usados (Cap. 3,
`sec:met_datasets`), ni métodos de mitigación del sesgo que el trabajo no aplica.

---

## 2.8 Estado del arte — `sec:estado_arte`

**Mensaje central.** El diagnóstico automático de lesiones está maduro en clasificación pero se
evalúa con métricas y conjuntos que ocultan el desempeño en las clases y poblaciones que importan; los
VLM dermatológicos contrastivos ya superan a los generales; y los generadores de reportes se evalúan
casi siempre por parecido textual y con hardware fuera del alcance de este trabajo. De ahí la brecha
triple que cierra la sección.

**Extensión: 5–6 páginas** (dos tablas).

**Apertura (1 párrafo).** Tres líneas de trabajo, en el orden del *pipeline*; cada subsección cierra
con qué toma el trabajo de esa línea o en qué se diferencia. Los trabajos anteriores a 2020 aparecen
como hitos fechados (guía §6).

### 2.8.1 Diagnóstico automático de lesiones de piel

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Hitos: en 2017 una CNN alcanzó desempeño comparable a dermatólogos; en 2019, sobre HAM10000, los mejores algoritmos superaron a los lectores humanos. Son anteriores a los *transformers* y se citan como punto de partida | Marco histórico fechado | `esteva2017dermatologistlevel`, `tschandl2019comparison` |
| 2 | Conjuntos públicos (Tabla `tab:marco_conjuntos`): el área se apoya en conjuntos dermatoscópicos de pieles mayormente claras y en conjuntos clínicos más diversos pero sin texto; los pares imagen--texto son recientes | Qué datos existen y qué les falta | ver tabla |
| 3 | Clasificación actual: las revisiones sistemáticas muestran el predominio de CNN y la falta de estandarización en métricas y validación externa; trabajos recientes sobre HAM10000 con EfficientNet, Swin y ensambles reportan exactitudes altas, a menudo con exactitud o F1 ponderado como métrica principal (retoma §2.6.1) | La cifra que se reporta suele ser la que esconde las clases minoritarias | `magalhaes2024systematic`, `kim2025skinsavvy2`, `aboulmira2024skinhealthmate`, `khan2025ensemble`, `kreouzi2024learning` |
| 4 | Problemas recurrentes: desbalance, generalización y sesgo por tono (remite a §2.7). Cierre: el trabajo compara cuatro arquitecturas bajo un mismo protocolo, con F1 macro y partición por lesión | Qué toma y en qué se diferencia | — |

**Tabla `tab:marco_conjuntos`** — columnas: conjunto, modalidad, tamaño, etiquetas, texto asociado,
población. Filas: HAM10000, ISIC 2018, PH² (si llega el PDF; si no, sin fila), Fitzpatrick17k, DDI,
SkinCon, SCIN, HIBA, SkinCaRe, MM-Skin, Derm1M.
Citas: `tschandl2018ham10000`, `codella2019skin`, `mendonca2013ph2`, `groh2021neural`,
`daneshjou2022disparities`, `daneshjou2022skincon`, `ward2024empirical`, `riccilara2023dataset`,
`shen2025skincare`, `zeng2025mmskin`, `yan2025derm1m`.

### 2.8.2 Modelos visión--lenguaje en dermatología

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Modelos contrastivos con texto médico: MONET (literatura médica, anotación de conceptos), MedImageInsight (general, varios dominios, incluye kNN) | Primeros espacios imagen--texto con vocabulario clínico | `kim2024transparent`, `codella2024medimageinsight` |
| 2 | Modelos dermatológicos a gran escala: Derm1M/DermLIP (ontología clínica, *zero-shot*), MAKE (texto descompuesto en aspectos sobre Derm1M), PanDerm (fundacional multimodal, cuatro modalidades) | El pre-entrenamiento dermatológico supera al biomédico general | `yan2025derm1m`, `yan2025make`, `yan2025vision` |
| 3 | Por qué DermLIP: pesos abiertos, contrastivo (sirve para clasificar y para recuperar vecinos), especializado y ejecutable en el hardware del trabajo | Justifica la elección | `yan2025derm1m` |
| 4 | VLM médicos generales: LLaVA-Med, Med-Flamingo, PeFoMed, MedTrinity; evaluados sobre todo en VQA radiológica y patológica; en dermatología la evidencia es escasa y los modelos ajustados al dominio tienden a alucinar más (retoma §2.5.3). Cierre: el trabajo mide LLaVA-Med y Phi-3.5-Vision en dermatología bajo el mismo protocolo que los clasificadores | Hueco de evidencia que el trabajo cubre | `li2023llavamed`, `moor2023medflamingo`, `he2025pefomed`, `xie2025medtrinity25m`, `gu2024medvh`, `abdin2024phi3` |

### 2.8.3 Generación de reportes dermatológicos

| # | Párrafo | Afirmación que sostiene | Citas |
|---|---|---|---|
| 1 | Generadores de extremo a extremo: SkinGPT-4 (MiniGPT-4 ajustado, evaluación con dermatólogos), SkinVL (LLaVA-Med ajustado con MM-Skin), DermatoLlama/SCALEMED (datos sintéticos), Skin-R1 (razonamiento con aprendizaje por refuerzo) | Estado de la generación directa | `zhou2023skingpt4`, `zhou2024pretrained`, `zeng2025mmskin`, `yilmaz2025resourceefficient`, `liu2025skinr1` |
| 2 | Clasificador más LLM: ensambles de CNN cuya predicción redacta un LLM, y sistemas con GPT-4; la destilación de reportes estructurados (7 puntos) desde un modelo maestro, que se compara con RAG | Precedentes del *grounding* por clasificación del trabajo | `khan2025ensemble`, `kim2025skinsavvy2`, `chakrabarti2025skin` |
| 3 | Otras direcciones: explicación visual generativa (SkinGEN), VLM para una enfermedad concreta (MpoxVLM) | Delimita el campo | `lin2025skingen`, `cao2024mpoxvlm` |
| 4 | Cómo se evalúa: la mayoría con métricas con referencia (BLEU, ROUGE, BERTScore) y pocos con especialistas o con fidelidad diagnóstica; el hardware va de una GPU de consumo a ocho A100 | Instala la comparación de la tabla | los anteriores |
| 5 | Cierre: la brecha triple ya enunciada en el `\pendiente` (comparación bajo un mismo protocolo; evaluación por fidelidad diagnóstica; incertidumbre y hardware accesible), con lo que el trabajo aporta en cada punto | Motiva la tesina desde la literatura | — |

**Tabla `tab:marco_generadores`** — columnas: trabajo, modelo base, tarea, datos, métricas, hardware.
Filas: los trabajos de ¶1–¶3.

**Qué no va.** Ni resultados propios ni la tabla de posicionamiento contra el SOTA (capítulos de
resultados). Ni Med-PaLM 2, que es de preguntas y respuestas sin imagen, ni los trabajos sin relación
con lesiones de piel del `.bib` (difusión, flujos normalizantes, leyes de escalado).

---

## Próximos bloques (esquema, sin detalle)

| Bloque | Secciones | Extensión | Estado |
|---|---|---|---|
| **B** | §2.4 Modelos visión--lenguaje (CLIP; multimodales generativos; generación de texto a partir de imágenes médicas; RAG) · §2.5 Evaluación de modelos (clasificación; calibración; generación de texto; inferencia estadística; interpretabilidad) | 8,5–9 páginas | Se detalla al aprobarse este bloque |
| **C** | §2.6 Conjuntos de datos, sesgo y generalización · §2.7 Estado del arte (diagnóstico automático; VLMs en dermatología; generación de reportes) · párrafo de apertura del capítulo | 8–9 páginas | Se detalla después del bloque B |

El bloque C lleva además la tabla comparativa de §2.7.3 —modelo, tarea, datos, métricas y
hardware— y el cierre con la brecha triple que enuncia el `.tex`. Las tablas de resultados de
`Docs/tabla_resultados_sota/` **no** se copian al capítulo: son material de los capítulos de
resultados; acá solo alimentan la comparación cualitativa.

---
## Preguntas abiertas

1. **Acrónimos de los bloques B y C** (BLEU, ROUGE, METEOR, CIDEr, BERTScore, MCE, Grad-CAM y los
   que surjan): se piden en la ficha de cada bloque, no ahora.

2. **Cómo se cierra la brecha de extensión del capítulo.** El bloque A cerró en 7 páginas contra
   las 10–11 estimadas, y al ritmo actual el capítulo termina en 20–22 y no en 25–30. Hay que
   decidir, al detallar el bloque B, si se amplía el plan de contenido o si se baja el objetivo de
   la guía. Ver el encabezado de esta ficha.

3. **La expansión de los acrónimos deja paréntesis anidados.** `\gls{llm}` imprime «Gran Modelo de
   Lenguaje (Large Language Model) (LLM)», y lo mismo pasa con `cnn`, `vlm` y `ood`, que ya se
   imprimen así en el Capítulo 1. Se arregla en una línea por acrónimo en `Matter/05-Acronyms.tex`,
   sacando el inglés entre paréntesis de la forma larga: la lista de acrónimos lo sigue mostrando.
   Afecta a capítulos ya revisados, así que lo decide el autor.

## Decisiones tomadas

1. **Las claves propuestas se nombran ahora, no al citar.** La auditoría de `refs_pendientes.md`
   ya fija el nombre de cada clave para que la incorporación al `.bib` y la redacción usen el mismo
   identificador y no haya que reescribir citas.

2. **Las páginas estimadas usan coma decimal** (`3–3,5`), como en la ficha de la introducción: la
   regla del punto decimal de la guía se aplica a los resultados del documento, no a las estimaciones
   de esta ficha.

3. **RNN y LSTM no se acortan a sigla.** La mención histórica de §2.3.1 queda más breve escrita
   en palabras, y evita dos entradas de acrónimo para material que el recorte deja en una oración.

4. **§2.1 se queda como sección de dominio, adelgazada** (22/09/2026). La duda del autor era si
   corresponde un marco teórico clínico en una tesina de Ciencias de la Computación. Se resuelve así:
   la sección existe porque define lo que el trabajo mide —las etiquetas del clasificador, la
   diferencia de dominio entre conjuntos y el formato del texto generado— y se limita a eso. Baja de
   3 a 2,5 páginas, §2.1.1 pasa de cuatro párrafos a tres (la gravedad de las clases se funde con la
   taxonomía), §2.1.2 de cuatro a tres y §2.1.3 de cuatro a tres (los criterios estructurados se
   funden con el vocabulario). Se aclara en la sección que no es un curso de dermatología.

5. **Vocabulario sin palabras rebuscadas** (22/09/2026). «Exéresis» se reemplazó por «extirpar una
   lesión benigna sin necesidad», «glosa» por «lo que designa cada sigla», «etiológica» por
   «diagnóstica», «escala macroscópica» por «tal como se ve a simple vista» y «superficie cutánea»
   por «la piel». Se aplica al resto del capítulo en la pasada de estilo de cada sección.

6. **`nvidia2023beginners` no se cita** (22/09/2026). Con `holtzman2020curious` para decodificación,
   el *ebook* de NVIDIA queda sin uso en el capítulo. La entrada se conserva en el `.bib` sin usar;
   retirarla es decisión del autor.

7. **La figura de §2.2.3 se dibuja** (22/09/2026). `fig:marco_vit_patches`, TikZ en escala de
   grises, después de ¶1 de §2.2.3.

8. **§2.1.3 ¶1 ya no enuncia las cuatro partes del reporte** (22/09/2026). La ficha pedía
   descripción, impresión diagnóstica, diagnóstico diferencial y recomendación de manejo, con
   `kittler2016standardization` de respaldo, pero ese trabajo es el consenso de la ISD sobre
   **terminología dermatoscópica** y no dice nada sobre el formato del informe; el `.bib` no tiene
   ninguna referencia que lo diga. El párrafo pasa a enunciar las dos partes de las que el trabajo
   se ocupa —descripción e impresión diagnóstica—, que son las que anotan los conjuntos de pares
   imagen--texto y se sostienen con `shen2025skincare`, y deja el diferencial y la recomendación
   como lo que queda fuera del alcance. `kittler2016standardization` se conserva en ¶2, que es
   donde sí corresponde: el vocabulario estandarizado por consenso. En `refs_pendientes.md` quedó
   propuesta una referencia clínica sobre estructura del informe, por si se quiere recuperar la
   enumeración completa.

9. **LSTM sale de §2.3.1 ¶1** (22/09/2026). La mención «las redes de memoria a corto y largo plazo
   alargaron esa memoria» no tenía fuente: Hochreiter y Schmidhuber 1997 no está en el `.bib` y
   `elman1990finding` es siete años anterior. Como la decisión 3 ya dejaba LSTM en una mención
   mínima, se elimina la cláusula y el párrafo queda con las redes recurrentes, que Elman sí
   sostiene.

10. **«Embedding» es el término, no «embebido»** (22/09/2026). Convivían los dos en el mismo
    capítulo. Se elige el inglés por el criterio que la guía ya aplica a *pipeline* o *prompt*, y
    la decisión quedó registrada en la tabla de terminología de la guía §4.

11. **Se corrige «invariancia» por «equivariancia» a traslaciones en §2.2.3 ¶2** (22/09/2026). La
    convolución es equivariante a traslaciones; la invariancia la aporta el *pooling*. Es lo que
    dice Dosovitskiy y lo que decía esta ficha.

12. **AKIEC no es solo premaligna** (22/09/2026). La clase agrupa queratosis actínica y carcinoma
    intraepitelial, que ya es un carcinoma in situ; por eso HAM10000 las junta. §2.1.1 ¶2 pasa a
    decir «reúne lesiones premalignas y carcinomas in situ».
13. **Reorganización tras la revisión del 25/09/2026.**
    - **La atención pasa a sección propia** (`sec:marco_atencion`), entre §2.1 y visión, porque la
      usan visión y lenguaje. La mención de las redes recurrentes (antes §2.3.1 ¶1) abre esa
      sección, donde motiva la atención en lugar de aparecer después de ella. Las secciones
      siguientes corren un número: visión es §2.3, lenguaje §2.4, VLM §2.5, evaluación §2.6, datos
      §2.7 y estado del arte §2.8. Las tablas de esta ficha conservan la numeración vieja.
    - **El párrafo codificador–decodificador se corrige.** Decía que el trabajo procesa la imagen con
      el codificador y el texto con el decodificador, lo que contradecía §2.3.1 ¶3 (LLM de solo
      decodificador) y no describe a LLaVA. Ahora dice que el ViT conserva el codificador y los LLM
      generativos el decodificador; cómo se unen en un VLM queda en el `\pendiente` de §2.4.2.
    - **§2.2.3 ¶2 (ViT) se corrige.** La inversión ViT/CNN de Dosovitskiy depende de la escala del
      pre-entrenamiento (ImageNet frente a 14–300 millones de imágenes), no del tamaño del conjunto
      médico. §2.2.3 ¶4 se elimina por repetir §2.2.4 ¶2.
    - **La distinción fidelidad diagnóstica / calidad del texto se instala solo en §2.4.3**, que
      además retoma `fig:intro_dos_tareas`. §2.1.3 ¶3 pasa a extraer de la variabilidad entre
      observadores la consecuencia para las métricas con referencia (`sec:marco_eval_texto`).
    - **La exactitud engañosa se explica solo en §2.5.1** (`sec:marco_eval_clasif`); §2.1.1 ¶3 y
      §2.2.4 ¶4 remiten a ella.
    - Se eliminaron la apertura defensiva de §2.1, las frases de traspaso al final de §2.2 y §2.3 y
      la mención de Swin para tareas de localización, y se hizo una pasada sobre los cierres
      sentenciosos y el contraste «no X, sino Y».

14. **El capítulo queda solo con conceptos de computación** (25/09/2026). Se anula la decisión 4. La
    duda del autor volvió a plantearse revisando la estructura completa: cada pieza de §2.1 tenía un
    lugar donde se usa, y en varios casos ese lugar ya existía y la duplicaba. El reparto:
    - §2.1.1 ¶2 (siete categorías y gravedad) → Materiales y métodos, `sec:met_ham`. ¶1 se descarta
      (la definición de lesión era casi tautológica). ¶3 (costos asimétricos) → `sec:met_seleccion`,
      donde justifica las métricas por clase.
    - §2.1.2 ¶1-2 (qué es la dermatoscopía, dependencia de la formación) se eliminan: ya están en
      §1.1 con las mismas citas. ¶3 (modalidades como dominios distintos) → nueva sección «Sesgo y
      generalización» (`sec:marco_generalizacion`), que reemplaza a «Conjuntos de datos, sesgo y
      generalización».
    - §2.1.3 ¶1 (partes del reporte) → `sec:met_generacion`. ¶2 (vocabulario finito) y ¶3
      (variabilidad entre observadores) → `sec:marco_eval_texto`, como base de las métricas sin
      referencia y límite de las con referencia.
    - Conjuntos concretos: los usados ya estaban en `sec:met_datasets` (incluida la falta de
      identificador de paciente de HAM10000, que es `sec:met_particiones`); el repaso de los no usados
      pasa a un cuadro en el estado del arte. Se respeta el criterio del tutor del 14/09: el sesgo y la
      generalización, que son conceptos, se quedan en este capítulo.
    - La extensión del capítulo baja; las páginas son estimativas y no bloquean (autor, 25/09/2026).
    - Numeración resultante: §2.1 atención, §2.2 visión, §2.3 lenguaje, §2.4 VLM, §2.5 evaluación,
      §2.6 sesgo y generalización, §2.7 estado del arte.
15. **Bloque B (25/09/2026).**
    - El *hedging* se presenta sin cita, como falla observada durante la experimentación del trabajo,
      con remisión al Capítulo de resultados de generación (autor).
    - Los límites de Grad-CAM se citan con `adebayo2018sanity`, agregado al `.bib`. Adebayo muestra que
      Grad-CAM **supera** sus pruebas de aleatorización; el texto lo dice así y usa el trabajo para
      sostener que la inspección visual sola no valida un método, no para descalificar a Grad-CAM.
    - Las métricas sin referencia se presentan como concepto en §2.6.3; la lista de términos y las
      reglas de coincidencia van en Materiales y métodos (`sec:met_protocolo`), cuyo `\pendiente`
      todavía no lo menciona.
    - MCE se escribe en línea («error de calibración máximo (MCE)») y no se declara como acrónimo,
      para no tocar `Matter/05-Acronyms.tex`.
    - La ficha decía que la calibración post-hoc no cambia la clase predicha. Vale para el
      *temperature scaling*, no para el *vector scaling*, que puede cambiarla; el texto lo distingue.
    - «LLaVA fijó el esquema que sigue la mayoría de los VLM abiertos» no tenía respaldo y quedó como
      «los VLM generativos que usa el trabajo siguen el esquema de LLaVA».
16. **Bloque C (25/09/2026).**
    - `koh2021wilds` se agregó al `.bib` (autor).
    - Las tablas de §2.8 dicen qué evalúa cada trabajo y con qué hardware, no los valores que obtuvo;
      las cifras del estado del arte se comparan en los capítulos de resultados (autor).
    - PH² sale de la tabla de conjuntos (autor). `mendonca2013ph2` queda en el `.bib` sin citar.
    - DermaSynth son **textos** sintéticos redactados sobre 82 379 imágenes reales públicas, no imágenes
      generadas por difusión, como decía `Docs/estado_del_arte/resumen_papers.tex`. El resumen tiene
      errores: no sirve de fuente.
    - El cierre reconoce dos excepciones a la brecha: el ensamble de Khan et al. ya deriva los casos
      discordantes, y Chakrabarti et al. miden corrección diagnóstica además de métricas con referencia.
    - DDI se cita sin cifras de AUC: el PDF da los intervalos por fototipo y no un valor único claro.
    - Las revisiones de Jones y Magalhães se citan por lo que dicen textualmente («muchos» estudios, no
      «la mayoría»; variabilidad metodológica, no métricas).
    - Pregunta abierta: `babel` imprime «Cuadro 2.1» y la guía pide «Tabla~\ref{}» en el texto.
      Se unifica con `\renewcommand{\spanishtablename}{Tabla}` (o la opción `es-tabla` de babel) en
      la configuración compartida; lo decide el autor. (Resuelta: `10-Macros.sty` redefine `\tablename`.)
17. **Revisión del autor sobre el capítulo completo (26/09/2026).** Amplía el alcance de la ficha a pedido
    del autor:
    - Cada métrica y método que el trabajo usa se presenta con su fórmula: Adam, decaimiento de pesos,
      probabilidad de un modelo de lenguaje, temperatura de decodificación, RAG (formulación de Lewis),
      TPR/FPR y AUC, Brier, BLEU, ROUGE-L, METEOR, CIDEr, BERTScore, McNemar, Wilcoxon y Grad-CAM. Las
      fórmulas se verificaron contra los PDF originales.
    - Se agregan el desvanecimiento y la explosión del gradiente (§2.1.5), el aumento de datos se mueve a
      la regularización (§2.1.4) y se detalla, y se definen *token* y *embedding* en su primera aparición.
    - La decodificación usa los términos en inglés (*greedy decoding*, *beam search*, *top-p*), y aclara
      que el *beam search* sigue siendo la opción habitual en generación dirigida (Holtzman).
    - El origen del texto de SkinCaRe, MM-Skin y Derm1M entra en §2.5.3 porque condiciona la validez de la
      referencia: SkinCAP lo escribieron dermatólogos; SkinCoT lo redactó un LLM y lo certificaron
      dermatólogos.
    - El código aplica McNemar exacto (binomial sobre los discordantes), no la aproximación $\chi^2$; el
      texto presenta las dos y dice que el trabajo usa la exacta.
    - El corte de 2020 del estado del arte se presenta como criterio para acotar la búsqueda, no como
      frontera de arquitectura. HIBA: «primer conjunto público» se atribuye a sus autores.
    - Notación: $C$ clases en todo el capítulo (la softmax había pasado a $N$, que choca con los $N$ pares
      de CLIP); CIDEr usa $J$ referencias para no chocar con los $M$ intervalos del ECE.
