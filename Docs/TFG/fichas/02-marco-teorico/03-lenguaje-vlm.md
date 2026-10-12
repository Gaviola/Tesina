# Ficha 2.3 — Modelos de lenguaje y modelos visión–lenguaje

Sección del `.tex`: `Chapters/02-Marco-Teorico/03-lenguaje-vlm.tex`, que reúne `04-modelos-lenguaje.tex` y
`05-vlm.tex`.

**Estado: aprobada y redactada (2026-10-11).** Extensión resultante: unas 6.5 páginas (p. 43–49), con tres
figuras y seis ecuaciones; las 2.4 y 2.5 viejas ocupaban lo mismo, y la ficha estimaba 5. Lo que se recortó
(Kaplan como ley de escala, LLaMA, el detalle de Phi, la redefinición del *linear probe*) se compensa con lo
que se agregó para responder al tutor (el cálculo de memoria, el ejemplo de LoRA, el aprendizaje
autosupervisado, el sentido de «alinear» y la transición a 2.4). En la ecuación del modelo de lenguaje, la
longitud de la secuencia pasa a llamarse $n$, porque $T$ es la temperatura. La apertura no repite el cierre de
2.2. Responde a la tercera revisión del tutor (`feedback_cap1_y_2_v3.md`: la propuesta «IDEA», el mensaje, el
Audio 2 y los comentarios de las p. 41–47). Las fichas viejas `04-modelos-lenguaje.md` y `05-vlm.md` pasaron
a `historial.md`.

## Hilo conductor

Pregunta que responde la sección: ¿cómo se obtiene un modelo que genere texto, cómo se lo adapta con los
recursos del trabajo y cómo se lo conecta con una imagen?

Viene de: 2.1 deja preentrenamiento, transferencia, ajuste fino, *linear probe*, olvido catastrófico, Adam y
la memoria que ocupa por parámetro (remite a esta sección). 2.2 deja *token*, *embedding*, atención, bloque
transformer, codificador, ViT y línea base, y una limitación: ninguno de los clasificadores produce texto, y
el decodificador del transformer «se presenta en la Sección 2.3».

Deja instalado: modelo de lenguaje, decodificador y máscara, aprendizaje autosupervisado, LLM, *prompt*,
aprendizaje en contexto, estrategia de decodificación y temperatura, PEFT y LoRA, VLM, CLIP, similitud
coseno, clasificación *zero-shot*, kNN, VLM generativo y proyector, clasificación por verosimilitud. Y una
limitación para 2.4: clasificadores y VLM responden siempre, y su puntaje no dice cuánto confiar.

```
(sin subsección: un párrafo de entrada)
P1  Retoma el cierre de 2.2: un clasificador devuelve una probabilidad por clase, pero un reporte es texto.
    Hacen falta tres piezas, que ordenan la sección: un modelo que genere texto, una forma de adaptarlo a la
    dermatología con una GPU de consumo y una forma de conectarlo con la imagen          función: orienta
    ↓ necesidad — la primera pieza es el modelo de lenguaje

2.3.1 Grandes modelos de lenguaje (sec:marco_llm_grandes)
P2  Qué es un modelo de lenguaje, con un ejemplo antes de la ecuación: dado «La lesión presenta una red de
    pigmento», el modelo asigna a cada token posible la probabilidad de ser el siguiente. La probabilidad de
    una secuencia es el producto de esas probabilidades (eq:marco_lm). Responde a p41 («cruda y dura»)
                                                                                  define
    ↓ necesidad — cómo se calcula esa probabilidad con el transformer de 2.2
P3  El decodificador: los bloques de 2.2 con una máscara que impide a cada token tomar información de los
    posteriores, de modo que en un solo paso se entrena la predicción de todas las posiciones. Esa tarea no
    necesita etiquetas, porque cada token es la respuesta del anterior: **aprendizaje autosupervisado**
    (*self-supervised learning*), en contraste con el supervisado de 2.1. Dos tipos de modelos de lenguaje
    preentrenados según la mitad del transformer: solo decodificador, que generan (un **LLM** es uno de estos
    sobre corpus enormes; GPT-3, 175 mil millones de parámetros), y solo codificador, como BERT, que no
    generan; BERT se nombra porque 2.6 usa uno para evaluar texto                           define
    ↓ ampliación — de modelo preentrenado a modelo que sigue instrucciones
P4  Sin nombrar modelos (Mistral y Phi se presentan en el Cap. 3; revisión del autor, 2026-10-12; «pesos
    abiertos» pasa a abrir 2.3.2). Después del preentrenamiento, el ajuste fino sobre pares instrucción–respuesta y la
    alineación con preferencias humanas (RLHF, una oración) dan un modelo que sigue instrucciones
                                                                          explica lo usado
    ↓ consecuencia — si el modelo sigue instrucciones, el texto de entrada pasa a ser el medio de control
P5  *Prompt* y aprendizaje en contexto (*in-context learning*): lo que se agrega al *prompt* cambia la salida
    sin cambiar los pesos. Base del condicionamiento por evidencia de 2.5                 define
    ↓ necesidad — de la distribución sobre el vocabulario hay que elegir un token en cada paso
P6  Generación token a token y estrategia de decodificación: voraz (se repite), muestreo, temperatura
    (eq:marco_temperatura, la misma que usa la calibración de 2.6) y *top-p*            define
    ↓ problema — estos modelos tienen miles de millones de parámetros, y adaptarlos al dominio es caro

2.3.2 Ajuste eficiente de parámetros: LoRA (sec:marco_llm_lora)
P7  El problema, con números: un modelo de 7 mil millones de parámetros a 16 bits ocupa 14 GB solo en pesos;
    el ajuste fino completo suma un gradiente por parámetro y los dos promedios de Adam que 2.1 anticipó, y
    la memoria llega al menos a cuatro veces esa cifra, unos 56 GB, por encima de una GPU de consumo. Los
    métodos PEFT congelan el modelo y entrenan pocos parámetros. Responde a p42 («tropieza con la memoria»)
                                                                         justifica · define
    ↓ necesidad — cuáles parámetros entrenar
P8  LoRA: el cambio que introduce el ajuste fino tiene rango bajo; ecuación (eq:marco_lora), Figura LoRA,
    inicialización de B en cero, rol de r y α                                          define
P9  Qué matrices adaptar: casi todos los parámetros están en las proyecciones de la atención y del perceptrón
    (Kaplan); el trabajo original adapta Q y V. Reducción en GPT-3 (10 000 veces menos parámetros entrenables,
    tres veces menos memoria) y sin latencia al fusionar                  explica lo usado
    ↓ limitación — un LLM adaptado solo recibe texto, y el reporte describe una imagen

2.3.3 Modelos visión–lenguaje contrastivos: CLIP (sec:marco_vlm, sec:marco_vlm_clip)
P10 **VLM**: procesa imagen y texto. Dos formas: alinear en un espacio común, o conectar un codificador
    visual a un LLM. El codificador visual suele ser un ViT de 2.2. Sin «aparecieron en ese orden» (p44)
                                                                                  define · orienta
P11 El preentrenamiento contrastivo lenguaje–imagen (CLIP), con artículo (p44): dos codificadores, similitud
    coseno (eq:marco_cos) y qué significa: alinear es que una imagen y su descripción tengan similitud
    cercana a 1, en lugar de «queden cerca» (p44). Contraste entre N pares, Figura CLIP, 400 millones de
    pares sin etiquetas de clase                                                   define
    ↓ consecuencia — el espacio compartido permite clasificar sin entrenar
P12 *Zero-shot* con textos de clase («una imagen dermatoscópica de un melanoma») y su dependencia de la
    plantilla. Con etiquetas: *linear probe* (solo se nombra, 2.1.3) y kNN con sus dos ecuaciones
    (eq:marco_vecinos, eq:marco_knn), que 2.4 y 2.5 reutilizan                       define
    ↓ limitación — CLIP solo relaciona lo que vio, y casi no vio dermatoscopía
P13 DermLIP: el mismo esquema sobre un millón de pares dermatológicos. Cierre: un modelo contrastivo no genera
    texto, en lugar de «no redacta» (p44)                                            explica lo usado

2.3.4 Modelos visión–lenguaje generativos (sec:marco_vlm_generativos)
P14 LLaVA: codificador visual tipo CLIP, proyector y LLM de solo decodificador; los tokens visuales entran
    como parte del *prompt* (Figura LLaVA). Entrenamiento en dos etapas, con LoRA en la segunda   define
P15 La receta en el dominio médico: LLaVA-Med (sobre Mistral), SkinVL (dermatología) y Phi-3.5-vision
    (más chico)                                                                     explica lo usado
    ↓ problema — un VLM generativo devuelve texto, no una probabilidad por clase
P16 Clasificar con un VLM generativo: buscar la clase en la respuesta o puntuar cada nombre de clase con
    eq:marco_lm, normalizado por longitud. Esos puntajes ordenan las clases, pero no están calibrados
                                                                                  define
→ Transición a 2.4 (responde a p46 «afirmarse» y p47 «de tropezón»): tanto los clasificadores de 2.2 como los
  VLM devuelven una respuesta para cualquier imagen, incluso cuando se equivocan, y su puntaje no indica
  cuánto confiar en ella. Antes de pedir un reporte hay que decidir cuándo una predicción es lo bastante
  confiable para sostenerla, y cuándo conviene abstenerse; ese es el tema de 2.4.

Se definen acá (y no se vuelven a definir): modelo de lenguaje, decodificador y máscara, aprendizaje
autosupervisado (*self-supervised learning*), LLM, *prompt*, aprendizaje en contexto (*in-context learning*),
estrategia de decodificación, temperatura, *top-p*, PEFT, LoRA, VLM, CLIP, similitud coseno, *zero-shot*,
kNN, VLM generativo, proyector, clasificación por verosimilitud.
Se retoman de antes (solo se nombran, con \ref): softmax y logits (2.1), Adam y su memoria (2.1), ajuste fino,
*linear probe* y olvido catastrófico (2.1.3), *token*, *embedding*, atención, bloque y codificador (2.2.2),
ViT (2.2.3), línea base (2.2).
Remisiones hacia adelante: calibración (2.4 y 2.6), condicionamiento por evidencia y recuperación (2.5),
métricas de texto con BERT (2.6).
Extensión: 16 párrafos, unas 5 páginas.
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor: 2.3 reúne «Transformers, LLM, LoRA, CLIP y VLM generativos» | Se reúnen las 2.3 y 2.4 actuales (archivos `04` y `05`). El transformer ya está en 2.2; acá entra solo el decodificador |
| Mensaje: profundidad proporcional a la importancia para el trabajo | P4 deja solo las familias que usa el trabajo (Mistral, Phi). Salen la ley de escala de Kaplan, la comparación Mistral–LLaMA 2, LLaMA y el detalle de los datos de Phi (`gunasekar2023textbooks`). Kaplan se usa solo para decir dónde están los parámetros (P9) |
| p41, apertura «muy cruda y dura» | P1 retoma el cierre de 2.2 y anuncia las tres piezas; P2 explica el modelo de lenguaje con un ejemplo dermatológico antes de la ecuación |
| p42, «tropieza con la memoria»: no se entiende | P7 plantea el problema con números (14 GB de pesos, unos 56 GB para el ajuste completo) y remite a 2.1 para Adam |
| p44, «que aparecieron en ese orden» | Sale. P10 presenta las dos formas sin cronología |
| p44, «queden cerca» | Se define con la similitud coseno: cercana a 1 |
| p44, «no redacta» | «no genera texto» |
| p44, falta el artículo antes de CLIP | «El preentrenamiento contrastivo lenguaje–imagen (CLIP)…» |
| p46, «merece afirmarse» | Sale; la transición habla de cuándo una predicción es lo bastante confiable para sostenerla |
| p47, salto abrupto a 2.6 | La transición une clasificadores y VLM en el mismo problema (responden siempre) y anuncia 2.4 |
| Redundancia con 2.1 | El *linear probe* ya no se define (2.1.3); Adam solo se nombra |
| Concepto pendiente de la tabla del capítulo | Se define el aprendizaje autosupervisado (P3) |

## Archivos y labels

- `git mv 04-modelos-lenguaje.tex 03-lenguaje-vlm.tex`; sale `05-vlm.tex`. `00-capitulo.tex` pasa a un solo
  `\input`, y el capítulo queda con 8 secciones.
- `\label{sec:marco_llm}` va en la nueva `\section` (lo usa 2.2). `sec:marco_vlm` va en 2.3.3, junto a
  `sec:marco_vlm_clip`, porque ahí se definen los VLM (lo usan 2.2 y el estado del arte).
- Se conservan `sec:marco_llm_grandes` (2.5, 2.6), `sec:marco_llm_lora` (2.1, estado del arte),
  `sec:marco_vlm_clip` (2.1, 2.4), `sec:marco_vlm_generativos`, y las ecuaciones `eq:marco_lm`,
  `eq:marco_temperatura` (2.6), `eq:marco_lora`, `eq:marco_cos`, `eq:marco_vecinos` (2.5) y `eq:marco_knn`
  (2.4). Se copian sin reescribirlas (decisión vigente 4).
- Figuras: `lora.tex`, `clip.tex` y `llava.tex`, sin cambios.

## Citas

`brown2020language`, `devlin2019bert`, `jiang2023mistral`, `abdin2024phi3`, `ouyang2022training`,
`holtzman2020curious`, `hu2021lora`, `kaplan2020scaling`, `radford2021learning`, `cover1967nearest`,
`yan2025derm1miccv`, `liu2023visual`, `li2023llavamed`, `zeng2025mmskin`. Todas existen en el `.bib`. Salen
`touvron2023llama` y `gunasekar2023textbooks`. El cálculo de memoria de P7 es aritmético y no lleva cita.

## Decisiones

Aprobadas por el autor (2026-10-11):

1. **La decodificación queda en 2.3** (recomendado). Es la forma en que un LLM produce texto, los generadores
   del trabajo muestrean con temperatura y *top-p*, y la temperatura reaparece en la calibración de 2.6. La
   alternativa es pasarla a 2.5, junto a las estrategias de generación del reporte.
2. **Familias de LLM recortadas a las que usa el trabajo** (P4), con BERT en una oración para 2.6.
3. **Ejemplo de memoria con un modelo de 7 mil millones de parámetros** (P7), el tamaño de LLaVA-Med.
4. **kNN conserva sus dos ecuaciones**, porque 2.4 y 2.5 las citan por número.
