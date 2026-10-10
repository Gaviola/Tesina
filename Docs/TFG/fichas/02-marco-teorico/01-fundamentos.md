# Ficha 2.1 — Fundamentos del aprendizaje profundo

Sección del `.tex`: `Chapters/02-Marco-Teorico/01-fundamentos.tex`.

**Estado: propuesta pendiente de aprobación del autor (2026-10-10).** Responde a la tercera revisión del
tutor (`feedback_cap1_y_2_v3.md`: mensaje, Audio 2 y los comentarios de las p. 30–35).

## Hilo conductor

Pregunta que responde la sección: ¿cómo aprende una red neuronal a clasificar imágenes, qué hace que lo
aprendido valga para casos nuevos y cómo se aprovecha un modelo ya entrenado cuando hay pocos datos?

Viene de: la introducción del capítulo (todos los modelos del trabajo son redes neuronales profundas).
Es la primera sección, así que no retoma conceptos.

Deja instalado: red, capa, parámetros, activación, clase, *logits*, softmax, entropía cruzada, entrenamiento,
inferencia; generalización, sobreajuste, particiones, fuga de información, cambio de distribución,
regularización, aumento de datos, TTA, desbalance; preentrenamiento, transferencia, *backbone* y cabeza,
extracción de características, ajuste fino, olvido catastrófico. Y una limitación para 2.2: la red trata su
entrada como un vector, sin la disposición espacial de los píxeles.

```
(sin subsección: dos párrafos de entrada)
P1  Aprendizaje automático y supervisado: los modelos del trabajo aprenden la tarea de ejemplos
    etiquetados, no de reglas escritas a mano                                       función: define
    ↓ relación: contraste — los métodos se diferencian por cómo describen cada ejemplo
P2  Aprendizaje profundo: aprende también la descripción (la representación), en una cadena de
    transformaciones que van de rasgos simples a conceptos; esa cadena es una red neuronal    define
    ↓ necesidad — qué es una red y cómo produce una respuesta

2.1.1 Redes neuronales y aprendizaje supervisado
P3  Red neuronal: neuronas → capa → red de varias capas; activación no lineal; parámetros.
    Ecuación de la capa y Figura 2.1                                                define
    ↓ consecuencia — en un clasificador, la última capa da un valor por clase
P4  Clasificación: qué es una clase (tipo de lesión), logits, softmax → probabilidades entre 0 y 1
    que suman uno; clase predicha y confianza (remite a 2.4)                         define
    ↓ necesidad — para que esas probabilidades sirvan hay que ajustar los parámetros, y para eso
      medir cuánto se equivoca la red
P5  Pérdida: la entropía cruzada mide el error de una predicción; qué castiga y por qué
    (un error con mucha confianza pesa más)                                          define
    ↓ consecuencia — entrenar es buscar los parámetros que minimizan la pérdida
P6  Entrenamiento: descenso del gradiente por lotes y épocas, retropropagación, Adam (su costo de
    memoria, remite a LoRA en 2.3), tasa de aprendizaje con calentamiento y coseno; inferencia
                                                                      define · justifica (LoRA)
    ↓ problema — que la pérdida baje en el entrenamiento no garantiza aciertos en casos nuevos

2.1.2 Generalización y desafíos del aprendizaje
P7  Generalización y sobreajuste (*overfitting*): aprender las particularidades y el ruido de los
    ejemplos en lugar de lo que distingue a las clases; cambio de distribución en una oración
    (remite a 2.6)                                                       define · fundamenta límites
    ↓ necesidad — para detectarlo hay que medir el error sobre datos no usados
P8  Particiones de entrenamiento, validación y prueba (*test*), con la redacción que propone el
    tutor: una oración por partición                                                 define
    ↓ precaución — «Una situación a evitar es que…»
P9  Fuga de información (*data leakage*): imágenes del mismo paciente o lesión en dos
    particiones                                                            define · justifica (Cap. 3)
    ↓ ampliación — además de medir el sobreajuste, se lo puede reducir
P10 **Regularización** (*regularization*), en negrita donde se define: definición del tutor (evitar aprender lo demasiado específico de los
    ejemplos de entrenamiento, para predecir bien sobre datos nuevos), y una oración que presenta la
    lista. Lista con el nombre en negrita:                                 define · explica lo usado
      · decaimiento de pesos (*weight decay*) y AdamW, con una oración que diga por qué con Adam se
        aplica aparte;
      · detención temprana (*early stopping*);
      · suavizado de etiquetas (*label smoothing*), que además mejora la calibración (remite a 2.4);
      · aumento de datos (*data augmentation*): transformaciones que conservan la clase, con
        RandAugment y el borrado aleatorio como métodos concretos, y el cuidado con el color en
        dermatoscopía.
    Cierra con el TTA: el aumento usado también al predecir.
    ↓ contraste — otro desafío no depende de cuánto memoriza el modelo sino de cómo se reparten
      los ejemplos entre las clases
P11 **Desbalance de clases** (*class imbalance*), en negrita: por qué favorece a las clases más frecuentes; variables
    n, n_c, y; las tres pérdidas en lista (ponderada, focal, *balanced softmax*); la alternativa de
    fijar un umbral en validación; la exactitud global lo oculta, y por eso se usan métricas por
    clase (solo se nombran, remite a 2.6)                       define · explica lo usado · justifica
    ↓ necesidad — todas estas medidas trabajan con los datos disponibles; con pocos datos conviene
      partir de un modelo que ya aprendió de otros

2.1.3 Modelos preentrenados y transferencia de aprendizaje
P12 Preentrenamiento y transferencia: pocos datos etiquetados en medicina; *ImageNet*; capas
    generales y específicas; la distancia con las imágenes médicas motiva el preentrenamiento en el
    dominio (DermLIP, remite a 2.3)                                         define · justifica
    ↓ consecuencia — cómo se reutiliza el modelo preentrenado
P13 *Backbone* y cabeza; extracción de características (la evaluación por *linear probe* es este caso);
    ajuste fino (*fine-tuning*); el compromiso entre libertad y sobreajuste, y el olvido catastrófico
    (*catastrophic forgetting*); cuando el modelo es tan grande que el ajuste fino no entra en una
    GPU, se recurre a métodos que entrenan pocos parámetros (remite a LoRA, 2.3)    define · justifica
    ↓ ampliación — entre los dos extremos hay estrategias intermedias
P14 Ajuste en dos etapas y tasa de aprendizaje por capa (*layer-wise learning rate decay*), con la
    ecuación de la tasa por capa                                       explica lo usado · justifica
→ Transición a 2.2: «La red descrita en esta sección trata su entrada como un vector y no aprovecha
  que, en una imagen, los píxeles vecinos están relacionados. Las arquitecturas de la sección
  siguiente incorporan esa estructura.»

Se definen acá (y no se vuelven a definir): los conceptos de «Deja instalado».
Se retoman de antes: nada.
Remisiones hacia adelante (`\ref`): calibración (2.4), LoRA y DermLIP (2.3), métricas y cambio de
distribución (2.6).
Extensión: 14 párrafos, unas 4 páginas (hoy 5.2).
```

## Qué cambia respecto del texto actual

| Comentario | Cambio |
|---|---|
| p30, «que en la práctica son datos»: conectar mejor | P1 abre desde el trabajo («Los modelos que se comparan en este trabajo…») y la experiencia se nombra como ejemplos, sin la aclaración suelta |
| Audio 2: salto de supervisado y no supervisado al aprendizaje profundo | Sale el aprendizaje no supervisado, que el trabajo no usa. El autosupervisado pasa a 2.3, donde se explica el preentrenamiento de los LLM |
| Audio 2 y mensaje: los conceptos deben construirse unos sobre otros | 2.1.1 sigue la cadena entrada → capas → un valor por clase → softmax → pérdida → entrenamiento. Se unen las 2.1.1 y 2.1.2 actuales |
| p32, «La pérdida de clasificación es la entropía cruzada.»: redactar mejor | P5 abre presentando la función de pérdida como lo que mide el error y después nombra la entropía cruzada |
| p33, «Vale»: falta un texto intro | La propiedad se introduce como consecuencia de la fórmula («Por cómo está definida, la pérdida…») |
| Menos matemática en lo general | Salen la ecuación del descenso del gradiente (`eq:marco_gradiente`, nadie la cita), la penalización L2 y el gradiente $p_c - q_c$. Quedan la capa, la softmax, la entropía cruzada y la tasa por capa |
| p33, memorizar no se entiende | P7 explica qué se memoriza (las particularidades y el ruido) y qué se pierde |
| p33, sobreajuste sin el inglés | «sobreajuste (*overfitting*)», y lo mismo para cada término que se usa en inglés |
| p33, particiones mal redactadas | P8 usa la redacción del tutor |
| p33, «Si imágenes»: no se empieza así | «Una situación a evitar es que…» |
| p33, la definición de regularización es incorrecta | Definición del tutor |
| p33, varias técnicas en un párrafo: usar viñetas | P10 en lista |
| p33, «no vale», «wut?» sobre AdamW | Una oración que explica que Adam reescala el paso de cada parámetro, y que por eso el decaimiento se aplica directamente sobre los parámetros |
| p34, el aumento de datos llega sin transición | Pasa a ser un ítem de la lista de regularización, presentado por lo que hace |
| p34, RandAugment: ¿qué es? ¿cita? | «un método de aumento de datos que…», con `cubuk2020randaugment` |
| p34, títulos de párrafo | No se usan (decisión del autor): el tema nuevo se marca con el término en negrita y el inglés entre paréntesis, y la transición lo introduce |
| p34, «favorece a las frecuentes» | «favorece a las clases más frecuentes» |
| Definir una sola vez | Salen de 2.1 las definiciones de sensibilidad y F1 macro (quedan en 2.6) y las menciones a los LLM en la softmax y la entropía cruzada (2.3 las retoma) |
| p35, *ImageNet* en cursiva | Cursiva, y la regla vale para todo conjunto de datos |
| Mensaje: 2.1.3 con más detalle, porque el trabajo la usa | Se conservan las dos etapas y la tasa por capa con su ecuación, y se agrega el vínculo con LoRA |

**Claves de cita** (todas en el `.bib`): `goodfellow2016deep`, `rumelhart1986learning`, `kingma2015adam`,
`goyal2017accurate`, `loshchilov2017sgdr`, `loshchilov2019decoupled`, `szegedy2016rethinking`, `muller2019does`,
`cubuk2020randaugment`, `zhong2020random`, `kittler2016standardization`, `shorten2019survey`,
`krizhevsky2012imagenet`, `buda2018systematic`, `lin2017focal`, `ren2020balanced`, `pan2010survey`,
`russakovsky2015imagenet`, `raghu2019transfusion`, `yosinski2014transferable`, `kumar2022finetuning`,
`howard2018universal`.

**Labels que se conservan** (los citan otras secciones): `sec:marco_fundamentos`, `eq:marco_capa`,
`eq:marco_softmax`, `sec:marco_regularizacion`, `sec:marco_desbalance`, `sec:marco_transferencia`. Las
etiquetas `sec:marco_redes`, `sec:marco_softmax`, `eq:marco_entropia` y `eq:marco_llrd` siguen existiendo. Sale
`eq:marco_gradiente`.

**Decisiones del autor (2026-10-10):**
1. Sale el aprendizaje no supervisado; el autosupervisado se explica en 2.3.
2. Sin títulos de párrafo: cada concepto nuevo va en negrita donde se define, con el inglés entre paréntesis.

---

# Historial

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.1 Fundamentos del aprendizaje profundo — `sec:marco_fundamentos`

**Mensaje central.** Una red neuronal es una composición de transformaciones con parámetros que se ajustan
minimizando una pérdida; lo aprendido solo vale si se sostiene en datos no vistos, y se puede mejorar
reutilizando conocimiento previo (transferencia) y corrigiendo el desbalance de clases.

**Apertura (C3).** Sin «Esta sección presenta…». Entra directo: «Una neurona artificial calcula…»
(l. 43). Se elimina el párrafo de las l. 37–38.

**Extensión: 6 páginas.**

| Subsección | Razón de ser | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|---|
| 2.1.1 Neurona artificial y perceptrón multicapa — `sec:marco_perceptron` | Base de la cabeza de clasificación y del proyector de los VLM (2.5) | l. 43–54 y `eq:marco_capa`; una oración de l. 56–60 sobre parámetros $\theta$ | **Se recorta**: el segundo párrafo de las l. 56–60 pierde la remisión a softmax (pasa a 2.1.2) | — |
| 2.1.2 Clasificación: softmax y entropía cruzada — `sec:marco_softmax` | Todo el capítulo opera sobre $p_c$: desbalance, calibración, temperatura | l. 65–74 y `eq:marco_softmax` | **Se elimina** el párrafo de las l. 76–81 («Varias piezas del trabajo operan…»): menciona `sec:met_clasif_vlm` (decisión propia). Se reemplaza por una oración de razón de ser sin remitir a Cap. 3 | — |
| 2.1.3 Entrenamiento por descenso del gradiente — `sec:marco_entrenamiento` | Justifica el costo de memoria que motiva LoRA (2.4.2) y los hiperparámetros | l. 86–122, `eq:marco_gradiente`, `eq:marco_adam`, `fig:marco_perceptron` (ver pregunta 6) | — | **Dificultad de entrenar redes profundas** (C6): se traslada acá el gradiente que se desvanece o explota de l. 181–191, en un párrafo. **Se elimina** todo lo de RNN y LSTM (l. 193–201) y la cita `hochreiter1997long`. Conserva una frase: las conexiones residuales (2.3.1) y la normalización atenúan el problema, y la recurrencia secuencial limita el paralelismo (se retoma en 2.2) |
| 2.1.4 Generalización y regularización — `sec:marco_regularizacion` | Toda métrica es una estimación de desempeño sobre datos no vistos; el resto del capítulo (2.8, 2.9) depende de esta idea | l. 127–169 y `eq:marco_weight_decay` | **Se elimina** la referencia a HAM10000 y `sec:met_particiones` (l. 136–137). La oración final del párrafo de aumento de datos sobre dermatoscopía (l. 163–165) pasa a ejemplo general («cuando el color distingue las clases…») y se puede mantener la cita `kittler2016standardization` solo si se lo formula como ejemplo del dominio, no como decisión propia | **Ampliación (F4, A5)**: ver párrafos abajo |
| 2.1.5 Transferencia de aprendizaje y ajuste fino — `sec:marco_transferencia` | Los clasificadores, el codificador visual, el LLM y LoRA se apoyan en pesos preentrenados; sin este concepto el lector no entiende por qué se puede trabajar con pocos datos médicos | l. 316–326 (segunda mitad: ImageNet, `russakovsky2015imagenet`, comparabilidad entre arquitecturas) | **Se elimina** la frase «Todas las arquitecturas del trabajo parten…» (decisión propia). Queda el hecho general: ImageNet como corpus de preentrenamiento de referencia | **Subsección nueva completa (F1, F2)**: ver párrafos abajo |
| 2.1.6 Desbalance de clases — `sec:marco_desbalance` | El desempeño global oculta el de las clases minoritarias; las correcciones de esta subsección se enfrentan en Cap. 4 | l. 334–340 (lista de tres pérdidas), citas `lin2017focal`, `ren2020balanced` | **Se elimina** l. 328–331 (distribución de HAM10000 y referencia a `cp:res_clasif`) y la frase «El Capítulo… compara en cambio tres modificaciones» | **Subsección nueva completa (F3)**: ver párrafos abajo |
| Cierre de 2.1 (sin título) | Transición hacia atención y arquitecturas (C4, C6, A7) | — | — | **Un párrafo** (ver abajo) |

### 2.1.4 ampliación (F4)

Ideas por párrafo, en orden:

1. **Qué mide y qué no la pérdida de entrenamiento** (reutiliza l. 127–130): sobreajuste como memorización.
2. **Error de generalización.** Definir el riesgo esperado $R(\theta)=\mathbb{E}_{(x,y)\sim\mathcal{D}}[\ell(f_\theta(x),y)]$
   y el riesgo empírico $\hat R(\theta)=\frac1n\sum_i \ell(f_\theta(x_i),y_i)$; la brecha $R-\hat R$ es lo que
   crece con el sobreajuste. Cita: `goodfellow2016deep`. Nuevo.
3. **Compromiso sesgo–varianza y capacidad**, en dos oraciones: un modelo con muy poca capacidad no ajusta
   (subajuste), y con demasiada memoriza. Cita `goodfellow2016deep`. Nuevo.
4. **Particiones y estimación honesta** (reutiliza l. 132–135). Agregar **el principio general**: las
   observaciones de la misma fuente (mismo paciente, misma lesión, misma sesión de adquisición) están
   correlacionadas; si aparecen en particiones distintas, la de test deja de ser independiente y la
   estimación es optimista. Se introduce el término *fuga de información entre particiones* (*data leakage*)
   con su definición, de acuerdo con la tabla de terminología de la guía §4, que la fija «en la primera
   aparición (Materiales y métodos)». **Conflicto**: la guía dice que se define en Cap. 3, pero A1 y el orden
   de lectura piden definirlo antes de usarlo (2.9 y Cap. 3 lo usan). Propuesta: se define acá y la guía se
   actualiza. Pregunta 8.
5. **Validación cruzada y variabilidad de la estimación**: una oración (una sola partición da una estimación
   con varianza; se retoma en 2.8.3). Cita `goodfellow2016deep`. Nuevo.
6. **Regularización** (reutiliza l. 139–169: decaimiento de pesos, *dropout*, aumento de datos, detención temprana).
   Si el Cap. 4 usa suavizado de etiquetas, MixUp/CutMix, borrado aleatorio o RandAugment, se agregan
   (ver pregunta 7; el código los usa: `configs/models/swin_tiny.yaml`, `src/data/collators.py`).

### 2.1.5 Transferencia de aprendizaje y ajuste fino (F1, F2) — párrafos

1. **El problema.** Con pocos datos etiquetados (típico de los conjuntos médicos) entrenar desde cero produce
   sobreajuste (enlaza con 2.1.4). Idea: reutilizar lo aprendido en otra tarea con más datos. Cita
   `pan2010survey` (definición formal de transferencia: dominio y tarea de origen y de destino).
2. **Qué se transfiere.** Las primeras capas de una red visual aprenden rasgos generales (bordes, texturas) y
   las últimas, rasgos específicos de la tarea de origen; por eso los primeros se reutilizan mejor. Cita
   `yosinski2014transferable` (nueva; verificada: arXiv 1411.1792).
3. **Por qué funciona con pocos datos** y **cuándo deja de funcionar bien**: la transferencia pierde
   beneficio cuando la tarea de origen es muy distinta de la de destino; en imágenes médicas el beneficio
   puede ser menor que el esperado y venir en parte del tamaño del modelo. Cita `raghu2019transfusion`
   (nueva; verificada: arXiv 1902.07208). Esto es importante para no sobrevender la transferencia.
4. **Dos formas de usarla.** Definir formalmente con $\theta=(\theta_b,\theta_h)$, $b$ por *backbone* y
   $h$ por cabeza de clasificación, con $\theta_b$ inicializado en $\theta_b^{\text{pre}}$:
   - **extracción de características**: $\theta_b$ se congela y se minimiza $\mathcal{L}$ solo respecto de
     $\theta_h$;
   - **ajuste fino**: se actualizan $\theta_b$ y $\theta_h$; en la variante habitual, con una tasa de
     aprendizaje $\eta_b<\eta_h$ para no destruir lo preentrenado.
5. **Ajuste fino como concepto propio (F2).** Variantes: completo o parcial (se descongelan las últimas
   capas); tasa de aprendizaje menor para el *backbone*; caída de tasa por capas (*layer-wise learning rate
   decay*) y ajuste en dos etapas (primero la cabeza, después todo) si el Cap. 3 los usa (pregunta 7). Riesgo: el
   **olvido catastrófico**, que el modelo pierde lo aprendido antes al ajustarse a la tarea nueva. Cita
   `kirkpatrick2017overcoming` (nueva; verificada: arXiv 1612.00796; ver pregunta 10 sobre si conviene citarla o
   describir el olvido sin cita).
6. **Costo del ajuste fino completo y anticipo de LoRA.** Cada parámetro entrenado arrastra su gradiente y los
   dos promedios de Adam (2.1.3): en modelos muy grandes eso no cabe en memoria. Se cierra con «La
   Sección~\ref{sec:marco_llm_lora} presenta una alternativa» y no con la decisión del trabajo.
7. **ImageNet y preentrenamiento a gran escala** (reutiliza l. 323–324): `russakovsky2015imagenet` como
   corpus de referencia; en 2.3.2 se retoma con la escala del preentrenamiento del ViT (l. 297–302).

Fórmulas nuevas de 2.1.5: la partición $\theta=(\theta_b,\theta_h)$ con las dos reglas de actualización.
Ejemplo:
$\theta_h\leftarrow\theta_h-\eta_h\nabla_{\theta_h}\mathcal{L}$, $\;\theta_b\leftarrow\theta_b-\eta_b\nabla_{\theta_b}\mathcal{L}$,
con $\eta_b=0$ en extracción de características y $\eta_b<\eta_h$ en el ajuste fino.

### 2.1.6 Desbalance de clases (F3) — párrafos

1. **Qué es y por qué importa.** Distribución de clases $\pi_c=n_c/n$; razón de desbalance
   $\rho=\max_c n_c/\min_c n_c$. Con datos desbalanceados, minimizar la entropía cruzada promedio favorece a
   las clases frecuentes: la pérdida total está dominada por sus ejemplos. Cita `buda2018systematic` (nueva;
   verificada: arXiv 1710.05381; estudio sistemático sobre CNN). Ejemplo hipotético, sin HAM10000.
2. **Por qué el aumento de datos no lo corrige** (reutiliza l. 330–331 con `shorten2019survey`): si se aplica
   igual a todas las clases, la proporción no cambia.
3. **Tres familias de corrección**, en `enumerate` (guía §3, alternativas en lista):
   - **A nivel de datos (remuestreo)**: sobremuestrear las minoritarias o submuestrear las mayoritarias. La
     probabilidad de muestreo de la clase $c$ es proporcional a $n_c^{\,q}$, con $q=1$ el muestreo natural y
     $q=0$ el balanceado por clase. Cita `buda2018systematic` (oversampling fue la más eficaz en su estudio,
     sin causar sobreajuste en CNN; verificar en el PDF antes de escribirlo).
   - **A nivel de pérdida**: (i) ponderación $\mathcal{L}=-w_y\log p_y$ con $w_c\propto 1/n_c$;
     (ii) pérdida focal $\mathcal{L}_{\text{focal}}=-(1-p_y)^{\gamma}\log p_y$, con $\gamma\ge 0$ ($\gamma=0$
     es la entropía cruzada) `lin2017focal`; (iii) *balanced softmax*,
     $p_c=\dfrac{n_c\exp(z_c)}{\sum_j n_j\exp(z_j)}$, equivalente a sumar $\log n_c$ al logit
     `ren2020balanced`. Variante: pérdida basada en el número efectivo de muestras `cui2019classbalanced`
     (opcional; pregunta 7).
   - **A nivel de decisión (ajuste de umbral)**: el clasificador se entrena sin corrección y después se
     reescalan las probabilidades por el inverso del *prior*, $\tilde p_c\propto p_c/\pi_c$, o se elige el
     umbral de decisión en validación. Cita `elkan2001foundations` (nueva; sin verificar). Sirve al tema de
     2.7 (umbral = punto de operación).
4. **Métricas sensibles al desbalance.** Solo una oración y remisión a 2.8.1: exactitud engaña, F1 macro y
   sensibilidad macro no. No repetir la explicación.
5. **Qué no corrige.** Ninguna de las tres cambia la información de las clases raras; solo cambia cuánto pesan
   (relación con generalización: pocas muestras de una clase limitan cuánto se puede aprender de ella).
   Cierre hacia 2.1.7 (cierre de sección) y nada de Cap. 4.

**Verificación pendiente (F3).** Cubrir los enfoques que se usan en Cap. 4. El código tiene
`class_weights: auto`, pérdida focal (`--focal-gamma`), suavizado de etiquetas, MixUp/CutMix, TTA
(original y volteo horizontal), ajuste en dos etapas y decaimiento de la tasa por capas (0.85). Todo lo que el
Cap. 4 nombre tiene que haberse definido antes, en 2.1.4 o 2.1.5, o se declara fuera del capítulo.
El autor confirma cuáles entran (pregunta 7).

### Cierre de 2.1 — párrafo de transición (C4, A7)

Ideas, en un solo párrafo de 5–6 líneas:

1. Apilar capas produce jerarquías de representaciones cada vez más abstractas; eso es el aprendizaje profundo.
2. A lo largo del tiempo se desarrollaron arquitecturas que incorporan la estructura del dato en lugar de
   tratar la entrada como un vector: las convolucionales para las imágenes (l. 174–179 de la versión actual,
   sin RNN), y para las secuencias, modelos que primero avanzan elemento a elemento y tienen dos límites
   (dependencias lejanas y falta de paralelismo; cita `vaswani2017attention`).
3. Eso motiva la atención (2.2), que reemplaza el recorrido secuencial por comparación directa, y sobre ella
   se construyen tanto los modelos visuales (2.3) como los de lenguaje (2.4), que a su vez llevan a los modelos
   visión–lenguaje (2.5). Esa cadena LLM → VLM es la de A7.

**Citas de 2.1:** existentes: `rumelhart1986learning`, `goodfellow2016deep`, `kingma2015adam`,
`srivastava2014dropout`, `shorten2019survey`, `pan2010survey`, `russakovsky2015imagenet`, `lin2017focal`,
`ren2020balanced`, `lecun1998gradient`, `he2015residual`, `hornik1989multilayer` (opcional para una
oración sobre capacidad de representación), `kittler2016standardization`. Sale `hochreiter1997long` y
`elman1990finding` deja de usarse en 2.1 (ver 2.2). Nuevas: `yosinski2014transferable`,
`raghu2019transfusion`, `kirkpatrick2017overcoming`, `buda2018systematic`, `cui2019classbalanced`,
`elkan2001foundations`.
