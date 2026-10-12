# Ficha 2.4 — Incertidumbre y predicción selectiva

Sección del `.tex`: `Chapters/02-Marco-Teorico/04-incertidumbre.tex` (hoy `06-incertidumbre.tex`).

**Estado: aprobada y redactada (2026-10-12).** Extensión resultante: unas 3.5 páginas (p. 50–53), con cuatro
ecuaciones y sin tablas ni figuras. Responde a la tercera revisión del tutor (`feedback_cap1_y_2_v3.md`: la
propuesta «IDEA» para 2.4, «confianza, calibración, abstención y políticas de decisión»; el mensaje general; el
comentario de la p. 47). Al aprobarla, el autor pidió quitar lo que la experimentación no usa (la curva
riesgo–cobertura) y quedarse con la ecuación o con la tabla de las tres salidas, no con las dos (decisiones 2
y 4). La ficha vieja `06-incertidumbre.md` pasó a `historial.md`.

## Hilo conductor

Pregunta que responde la sección: ¿por qué un modelo puede equivocarse con confianza, y cómo se decide cuándo
sostener una predicción, cuándo ofrecer alternativas y cuándo derivar el caso?

Viene de: 2.1 deja la softmax y la lectura de su máxima probabilidad como confianza «solo si el modelo está
calibrado» (remite a esta sección), el cambio de distribución, la partición en validación y test, y el
suavizado de etiquetas, que «suele mejorar su calibración» (remite a esta sección). 2.2 deja los
clasificadores. 2.3 deja el kNN con sus dos ecuaciones (`eq:marco_vecinos`, `eq:marco_knn`), la temperatura y
los puntajes por verosimilitud de un VLM, que ordenan las clases sin reflejar la probabilidad de acertar. Su
cierre ya plantea el problema: los modelos responden siempre y hace falta decidir cuándo una predicción es lo
bastante confiable para sostenerla y cuándo conviene abstenerse.

Deja instalado: incertidumbre aleatoria y epistémica, clasificador selectivo $(f, g)$, cobertura, riesgo
selectivo, señal de confianza $\kappa$ y umbral, curva riesgo–cobertura, máxima probabilidad softmax,
calibración (concepto), sobreconfianza, ensamble y voto suave, concordancia, consenso de los vecinos, política
de tres salidas y predicción por conjuntos. Y una limitación para 2.5: la política decide qué se emite, pero
un texto generado puede contradecir esa decisión.

```
(sin subsección: un párrafo de entrada)
P1  No repite el cierre de 2.3 (como 2.3 no repitió el de 2.2): parte de él. Decidir cuándo abstenerse
    exige saber por qué un modelo se equivoca con confianza, cómo se formaliza «no responder», con qué señal
    se estima la confianza y qué hace el sistema con ella; esas cuatro preguntas ordenan la sección. Responde
    a p47 («de tropezón»): la entrada se induce desde 2.3                               función: orienta
    ↓ necesidad — de dónde viene la incertidumbre

2.4.1 Incertidumbre en la clasificación diagnóstica (sec:marco_incert_fuentes)
P2  Dos fuentes, cada una con un ejemplo dermatológico. Aleatoria: una lesión cuyo aspecto es compatible con
    un nevo y con un melanoma deja la respuesta indeterminada aunque el modelo sea bueno, y más datos no la
    reducen. Epistémica: el modelo vio pocos ejemplos de una clase (remite al desbalance de 2.1) y la
    incertidumbre baja con más datos [kendall2017uncertainties]. El cambio de distribución de 2.1 se nombra
    como el caso extremo de la epistémica, sin redefinirlo                                define
    ↓ consecuencia — la softmax no tiene una salida para «no lo sé»
P3  Por qué la probabilidad no basta: la softmax reparte siempre una probabilidad que suma uno, de modo que
    no existe una salida que exprese «este caso no lo conozco», y una imagen fuera de lo visto puede recibir
    una probabilidad alta (dicho sin «alta»: cercana a uno). Enlaza con P2: ninguna de las dos fuentes queda
    separada en ese número                                                               justifica
    ↓ ampliación — por qué importa en dermatología
P4  Los errores no cuestan lo mismo (no detectar un melanoma frente a derivar un nevo) y la decisión final la
    toma una persona: el apoyo de un sistema mejoró la exactitud de dermatólogos y de médicos de atención
    primaria [groh2024learningaided], así que la salida es un insumo y no la decisión. Un sistema que reconoce
    su límite y deriva puede ser preferible a uno que siempre responde               justifica
    ↓ necesidad — formalizar la abstención para medir cuánto se gana

2.4.2 Predicción selectiva y abstención (sec:marco_pred_selectiva)
P5  Clasificador selectivo $(f, g)$, cobertura y riesgo selectivo (eq:marco_riesgo_selectivo, se copia),
    con la lectura sobre $n$ imágenes [elyaniv2010foundations, geifman2017selective]          define
P6  $g$ a partir de una señal $\kappa$ y un umbral $\tau$ (eq:marco_umbral_confianza, se copia). El
    compromiso: subir $\tau$ baja la cobertura y, si la señal separa aciertos de errores, también el riesgo.
    Sin curva riesgo–cobertura (decisión 2). Cierre: cuánto baja el riesgo por caso no respondido depende
    de la señal                                                                           define
    ↓ necesidad — qué señal usar

2.4.3 Señales de confianza y calibración (sec:marco_senales_confianza)
P7  La más simple: la máxima probabilidad softmax [hendrycks2017baseline]. Calibración en palabras y con un
    ejemplo: entre las imágenes a las que el modelo asigna 0.9 de probabilidad de melanoma, el 90 % lo son;
    la fórmula de Guo en línea. Sobreconfianza, atribuida a Guo y no como afirmación categórica («observaron
    que…»). Las métricas y las correcciones, en 2.6                                       define
    ↓ limitación — la probabilidad de un solo modelo no ve la incertidumbre epistémica
P8  Señales que comparan modelos. El desacuerdo entre modelos entrenados de forma distinta crece donde los
    datos no alcanzaron para fijar el modelo, y en eso aproxima la incertidumbre epistémica de P2. Ensamble y
    voto suave [lakshminarayanan2017simple] (el Cap. 3 lo usa)                     define · retoma
P9  Concordancia (eq:marco_concordancia, se copia; `sec:marco_concordancia` se conserva): dos predictores
    con sesgos distintos, como un clasificador y el kNN de 2.3. Ejemplo: el clasificador dice nevo y los
    vecinos, melanoma. Sirve solo si $P(\text{error} \mid a = 1) < P(\text{error} \mid a = 0)$, condición que
    se verifica con datos. Usa decisiones y no probabilidades, por eso no depende de la calibración; no
    informa cuando los dos comparten un error                                             define
P10 Consenso de los vecinos, $\max_c \hat{p}_{\text{kNN}}$ (eq:marco_knn de 2.3): vale 1 cuando los $k$
    vecinos coinciden. Depende de la representación y de la base: si la base no tiene casos parecidos, los
    vecinos existen igual y no informan                                                   define
P11 La calibración no crea información: el modelo que asigna 0.7 a todo y acierta el 70 % está calibrado y
    no separa casos. Una señal se juzga por cuánto menor es la tasa de error entre lo que acepta que entre
    lo que rechaza (la condición de P9, generalizada)                                   justifica
    ↓ ampliación — con una señal, la decisión deja de ser binaria

2.4.4 Tres salidas: afirmar, ofrecer diferenciales o derivar (sec:marco_tres_salidas)
P12 Un clínico que duda entre dos o tres diagnósticos los enuncia como diferencial. Tres salidas y la
    política con dos umbrales (eq:marco_politica, se copia; 2.5 la cita). Una oración nueva: si la señal es
    discreta, como la concordancia, los niveles se definen por sus valores y no hay umbral que ajustar (el
    Cap. 3 aplica la política «con la concordancia en lugar de la confianza»)          define
    Sin tabla (decisión 4)
P13 La salida diferencial como predicción por conjuntos $S(x)$: las clases más probables de un modelo o las
    predicciones de dos predictores que no coinciden (ejemplo: {nevo, melanoma}); $|S(x)| = 1$ es afirmar
                                                                                          define
P14 Qué arriesga cada salida, en prosa (lo que decía la tabla): afirmar, un error con forma de acierto;
    diferencial, menos información y más probabilidad de contener la clase; derivar, ningún diagnóstico.
    Los umbrales se fijan en validación, no en test (remite a las particiones de 2.1)  justifica
→ Transición a 2.5: la política decide qué se emite, pero salvo al derivar, lo que llega al lector es un
  reporte generado, y un texto puede deshacer esa decisión: afirmar con certeza un diagnóstico que la
  política dejó abierto, o contradecir el que recibió. Sin «no redacta» (el tutor lo objetó en p44).

Se definen acá (y no se vuelven a definir): incertidumbre aleatoria y epistémica, clasificador selectivo,
cobertura, riesgo selectivo, señal de confianza, calibración (concepto),
sobreconfianza, ensamble, voto suave, concordancia, consenso de los vecinos, política de tres salidas,
predicción por conjuntos.
Se retoman de antes (solo se nombran, con \ref): softmax (2.1), cambio de distribución, desbalance y
particiones (2.1), kNN y sus ecuaciones (2.3).
Remisiones hacia adelante: ECE, Brier y *temperature scaling* (2.6); generación condicionada por la
política (2.5).
Extensión: 15 párrafos, cinco ecuaciones (cuatro existentes y la del consenso), unas 3.5 páginas.
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor: «confianza, calibración, abstención y políticas de decisión» | Se mantiene la estructura de cuatro subsecciones, que ya cubre los cuatro temas en ese orden |
| p47, el salto «de tropezón» a 2.6 | La transición ya está en el cierre de 2.3. P1 parte de ella sin repetirla y anuncia las cuatro preguntas que ordenan la sección |
| Mensaje: profundidad proporcional a lo que usa el trabajo | Las señales que usa el trabajo (voto suave, concordancia, consenso de los vecinos) quedan con su ecuación. Sale la curva riesgo–cobertura: ni el código ni los resultados la calculan (verificado el 2026-10-12 en `Codigo/` y en los Caps. 3–7) |
| Mensaje: expresiones vagas («valores altos») | Sale la tabla, que decía «confianza alta, intermedia, baja»; la ecuación usa los umbrales. P3 dice «cerca de uno» |
| Redundancia entre la tabla y la ecuación de la política | Queda la ecuación, que la vieja 2.7 cita y que el Cap. 3 replica en su regla de ruteo. Lo que la tabla decía de los riesgos pasa a P14 |
| Mensaje: afirmaciones categóricas | «Las redes profundas actuales tienden a ser sobreconfiadas» pasa a atribuirse a Guo et al. |
| Mensaje: párrafos que juntan ideas | P2 y P3 se separan (fuentes por un lado; por qué la softmax no las muestra, por otro). Hoy el segundo párrafo mezcla el cambio de distribución con la softmax |
| Preferencia del autor: ejemplos del dominio | Ejemplos dermatológicos en P2 (nevo/melanoma, clase con pocos ejemplos), P7 (calibración con melanoma), P9 y P13 (nevo frente a melanoma) |
| Hilo con 2.1 y 2.3 | P2 remite al desbalance; P13, a las particiones; P9 y P10, al kNN de 2.3. El cambio de distribución se nombra con `\ref` a 2.1 (`sec:marco_regularizacion`), no a la vieja 2.9 |
| Hilo con el Cap. 3 | P12 agrega una oración sobre señales discretas, porque el ruteo del Cap. 3 aplica la política con la concordancia |
| Transición a 2.5 | Plantea el problema propio del texto (puede deshacer la decisión) en lugar de «no redacta nada» |

## Archivos y labels

- `git mv 06-incertidumbre.tex 04-incertidumbre.tex`; `00-capitulo.tex` cambia ese `\input`. La ficha vieja
  `06-incertidumbre.md` pasa a `historial.md`.
- Se conservan todos los labels, porque los usan 2.1, la vieja 2.7, la vieja 2.8, el estado del arte y el
  Cap. 3: `sec:marco_incertidumbre`, `sec:marco_incert_fuentes`, `sec:marco_pred_selectiva` (2.6, Cap. 3),
  `sec:marco_senales_confianza` (2.1, 2.5, 2.6, Cap. 3), `sec:marco_concordancia` (Cap. 3),
  `sec:marco_tres_salidas` (2.5, 2.7, Cap. 3), `eq:marco_riesgo_selectivo`, `eq:marco_umbral_confianza`,
  `eq:marco_concordancia` y `eq:marco_politica` (2.5). Las ecuaciones se copian sin reescribirlas (decisión
  vigente 4). Sale `tab:marco_salidas`, que solo se citaba en la propia sección. Nueva `eq:marco_consenso`
  (revisión del autor): el consenso pasa a ecuación aparte porque en línea el subíndice kNN se leía como
  parte del $\max_c$. El Cap. 3 lo cita hoy por `eq:marco_knn`; puede pasar a citar `eq:marco_consenso`.
- Sin figuras.
- **Pendiente para 2.6** (no se toca ahora, porque una sección solo toca su `.tex`): la vieja 2.8
  (`08-evaluacion.tex`, cierre de la calibración) dice que la propiedad de servir para abstenerse «la mide la
  curva riesgo–cobertura de la Sección 2.4.2». Al reescribir 2.6, esa oración tiene que remitir a la
  separación entre aciertos y errores de 2.4.3, porque la curva ya no está.

## Citas

`kendall2017uncertainties`, `groh2024learningaided`, `elyaniv2010foundations`, `geifman2017selective`,
`hendrycks2017baseline`, `guo2017calibration`, `lakshminarayanan2017simple`. Todas existen en el `.bib` y ya
se usan hoy. No entran citas nuevas; `angelopoulos2021gentle` (predicción conforme) sigue fuera (decisión
vigente 2). Groh 2024 respalda lo que se dice (el apoyo mejoró la exactitud de los dos grupos; datos ya
verificados en `00-capitulo.md`).

## Decisiones

Respuestas del autor (2026-10-12):

1. **Se mantienen las dos fuentes de incertidumbre**, conectadas con las señales: P8 dice que el desacuerdo
   entre modelos aproxima la epistémica. Aprobada.
2. **Sale la curva riesgo–cobertura.** El autor pidió no incluir lo que la experimentación no usa, previa
   verificación. Ni el código ni los resul docs ni los Caps. 3–7 la calculan. El único umbral sobre la
   softmax (`scripts/temperature_scaling.py`, P5.4) fijó un punto de operación y se descartó porque esa señal
   no separaba aciertos de errores; la tesina no lo presenta. Quedan el compromiso entre cobertura y riesgo, en
   una oración, y la ecuación del umbral, que la política de tres salidas generaliza.
3. **Oración sobre señales discretas en P12.** Aprobada.
4. **Ecuación sin tabla.** El autor pidió quedarse con una de las dos. Queda la ecuación, porque la cita la
   vieja 2.7 y el Cap. 3 replica su forma; lo que la tabla decía de los riesgos pasa a P14.

Revisión del autor sobre la prosa (2026-10-12):

- P3 (costos y decisión humana): la oración «La decisión final, por otra parte, la toma una persona» quedaba
  suelta. Ahora encadena costos → derivar es preferible ante la duda → esa opción existe porque el sistema
  asiste a quien decide (Groh) → un sistema que deriva puede ser más útil.
- P8: «Aunque esté calibrada» no decía qué estaba calibrado. Ahora dice «Calibrar la softmax, sin embargo, no
  hace visible la incertidumbre epistémica».
- P10: el consenso en línea se leía mal; pasa a `eq:marco_consenso`.
- P13: sale «hasta que su probabilidad acumulada alcance un umbral», porque ningún experimento arma conjuntos
  así. Queda «las clases más probables de un modelo», que el Cap. 3 usa como contraste del par
  clasificador–kNN.
- Cobertura frente al código (`build_uncertainty_3tier.py`, `build_uncertainty_agreement.py`,
  `classifier_ensemble.py`, `uncertainty_analysis.py`, `temperature_scaling.py`) y al Cap. 3 (`08-pipeline.tex`,
  `05-clasificadores-supervisados.tex`): voto suave, concordancia, consenso con $k = 3$, política de tres
  salidas con señal discreta, diferencial como par de predictores y abstención como predicción selectiva están
  en la sección. ECE, MCE, Brier, diagramas de confiabilidad, *temperature* y *vector scaling* son de 2.6 (ya
  están en la vieja `08-evaluacion.tex`).
- Terminología (2026-10-12): «política» pasa a «regla de decisión», que el autor prefiere y que el Cap. 3 ya
  usa («La regla que asigna cada caso a un nivel»). Se define en negrita en 2.4.4 y después se dice «la
  regla». El label `eq:marco_politica` y el símbolo $\pi(x)$ se conservan. Pendiente fuera de esta sección: el
  Cap. 3 (`08-pipeline.tex`, «Esta regla es la política de tres salidas») y la figura de 2.5
  (`generacion-reportes.tex`, nodo «Política»), que se cambia al reescribir 2.5.
