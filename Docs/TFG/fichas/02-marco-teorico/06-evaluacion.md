# Ficha 2.6 — Evaluación de modelos

Sección del `.tex`: `Chapters/02-Marco-Teorico/06-evaluacion.tex`. Reúne los actuales `08-evaluacion.tex` y
`09-sesgo-robustez.tex`.

**Estado: aprobada y redactada (2026-10-12).** El autor aprobó las cuatro decisiones recomendadas. Extensión
resultante: unas 9.5 páginas (p. 36–45 del PDF), con dos figuras y una tabla. Es casi una página menos que las
dos secciones viejas juntas, pero más que las 6.5–7 que estimaba esta ficha: las métricas se conservaron todas
porque la experimentación las usa. Responde a la tercera revisión del tutor
(`feedback_cap1_y_2_v3.md`):
- La propuesta «IDEA» para 2.6 dice: «Clasificación, generación, calibración, robustez, sesgos y generalización».
- Pide que «cada conjunto de métricas comience explicando qué aspecto del desempeño pretende evaluar y por qué ese
  aspecto es importante». También que algunas métricas solo se nombren, con una explicación breve y su fórmula.
- Sobre la vieja 2.9, en p63 y p65, dice: «no tengo claro que aporta […] a tu trabajo»; «quizas como intro de
  metricas, dado que las metricas vienen a evaluar integramente el trabajo».

Hoy las dos secciones ocupan unas 10 páginas: la 2.6 va de la p. 59 a la 67 y la 2.7 de la 67 a la 69. El plan
del capítulo fija 6–7. Se aplica el criterio de 2.4 y 2.5: no se presenta lo que la experimentación no usa. Eso
se verificó el 2026-10-12 contra `Codigo/` y contra los Caps. 3 y 4 del worktree `../Tesina-cap03` (ver abajo).

## Hilo conductor

Pregunta que responde la sección: ¿cómo se mide si un clasificador y un generador funcionan, y qué puede afirmar
esa medida fuera del conjunto en que se calculó?

Viene de varias secciones:
- **2.5** cierra con: «Clasificadores, generadores y reglas de decisión producen así salidas de tres tipos:
  categorías, textos y decisiones de abstención. Cada una exige sus propias métricas, y ninguna de ellas, medida
  sobre datos de la misma fuente que los de entrenamiento, garantiza el desempeño del sistema fuera de esa
  fuente». También deja la calidad descriptiva, la fidelidad diagnóstica, el vocabulario estandarizado, el
  origen del texto de referencia, la alucinación y `hartsock2024vision`.
- **2.1** deja las particiones, el sobreajuste con el ejemplo de «una regla o una marca de tinta» y el desbalance
  de clases. También el cambio de distribución, que remite a `sec:marco_generalizacion`.
- **2.4** deja la cobertura y el riesgo selectivo (`eq:marco_riesgo_selectivo`), la calibración como concepto
  («Las métricas de calibración y las formas de corregirla se presentan en la Sección 2.6»), la temperatura
  (`eq:marco_temperatura`) y los costos asimétricos.

Deja instalado: sesgo, cambio de dominio y de subpoblación, validación externa y evaluación desagregada, y todas
las métricas que usan los Caps. 3–5. Para 2.7 deja un criterio: con qué datos y con qué protocolo se evaluó un
trabajo.

```
(sin subsección: un párrafo de entrada)
P1  Parte del cierre de 2.5 sin repetirlo. Las decisiones de abstención ya tienen medida: la cobertura y el
    riesgo selectivo de 2.4.1, calculados con la métrica de la salida que se acepta. Esta sección se ocupa de las
    categorías y de los textos, y empieza por la pregunta previa: qué puede afirmar una métrica calculada sobre
    el test. Dos o tres oraciones; ordena la sección                                     función: orienta
    ↓ necesidad — antes de las métricas, qué alcance tiene una medida sobre el test

2.6.1 Sesgo y generalización (sec:marco_generalizacion)
P2  Una métrica sobre el test estima el desempeño en la distribución del test, que viene de la misma fuente que
    el entrenamiento. El cambio de distribución de 2.1 se nombra sin redefinirlo, y se distinguen sus dos formas:
    cambio de dominio y cambio de subpoblación [koh2021wilds]                            define
    ↓ ejemplo — el dominio en dermatología
P3  Dominio. La modalidad: la fotografía clínica y la dermatoscopía registran rasgos distintos
    [dinnes2018dermoscopy, kittler2016standardization]. Dentro de una misma modalidad varían la iluminación, la
    distancia, la resolución y la compresión, y un modelo que se apoya en la textura fina o en el color exacto
    pierde desempeño ante imágenes de igual contenido clínico. Se evalúa de dos formas: en un conjunto de otra
    fuente (**validación externa**) o, sin otro conjunto, degradando el test de forma controlada (2.6.6)
                                                                                         justifica
    ↓ contraste — misma fuente, otras proporciones
P4  Subpoblación. Los fototipos poco representados en el entrenamiento se clasifican peor
    [groh2021neural, daneshjou2022disparities]. Sin cifras, porque las da el Cap. 1. Una métrica agregada lo
    oculta cuando el grupo es chico, así que se calcula por separado para cada grupo, por fototipo o por
    modalidad (**evaluación desagregada**)                                                justifica
    ↓ ampliación — el caso en que la métrica sobre el test no detecta nada
P5  Rasgos espurios. Retoma la regla y la marca de tinta de 2.1: si acompañan más a los melanomas, el modelo
    acierta sin mirar la lesión, y eso está documentado en conjuntos públicos de dermatoscopía [yan2023towards].
    Los modelos contrastivos permiten buscarlos [kim2024transparent]. Como el rasgo también está en el test,
    ninguna métrica sobre el test lo revela; hace falta ver en qué se apoya el modelo (2.6.7). Cierra
    ordenando lo que sigue: primero las métricas de cada salida, después las propiedades comunes a todas,
    entre ellas la robustez y la interpretabilidad, que responden a P3 y a P5             justifica
    ↓ necesidad — la métrica de base

2.6.2 Evaluación de la clasificación (sec:marco_eval_clasif)
P6  Qué evalúa y por qué: en qué clases acierta el modelo y con cuáles las confunde. Con desbalance (2.1) y
    costos asimétricos (2.4), una sola cifra no alcanza. Matriz de confusión y caso binario
    (fig:marco_matriz_roc)                                                              define
P7  Lista que se conserva casi sin cambios: exactitud y su límite, sensibilidad macro (y exactitud balanceada
    como sinónimo), precisión con F1 macro y ponderado, sensibilidad y especificidad de una clase (detección),
    ROC y AUC con el AUC macro. Sale «aquí se usa el promedio simple», que es una decisión propia; queda la
    definición del AUC macro                                                            define
    ↓ contraste — un reporte es un texto

2.6.3 Evaluación de la generación (sec:marco_eval_texto)
P8  Qué evalúa y por qué: los dos requisitos de 2.5.2. Un texto admite muchas versiones correctas. Tres
    familias (tab:marco_familias_texto)                                                 define
P9  Métricas textuales, cada una con una o dos oraciones y su fórmula: BLEU, ROUGE-L (solo con β = 1), METEOR,
    CIDEr y BERTScore                                                                   define
P10 Límite de la referencia: la concordancia entre dermatólogos [carrera2016validity] y su origen, que remite
    a 2.5.1 sin repetirlo. De ahí las métricas sin referencia                           limita
P11 Consistencia diagnóstica (eq:marco_fd) y cobertura de entidades clínicas (eq:marco_cobertura_ent),
    sin cambios                                                                         define
P12 Ninguna comprueba que lo descrito esté en la imagen [hartsock2024vision]. Hace falta que un especialista
    lea el reporte contra la imagen con una rúbrica                                     limita
    ↓ ampliación — propiedades que valen para cualquier salida; primero, cuánto creer la probabilidad

2.6.4 Calibración (sec:marco_eval_calib)
P13 Qué evalúa y por qué: 2.4 mostró que un umbral sobre la probabilidad solo tiene lectura si el modelo está
    calibrado. Diagrama de confiabilidad, ECE y MCE (fig:marco_confiabilidad)            define
P14 Brier, más una oración nueva: la entropía cruzada media sobre el test (eq:marco_entropia, sin redefinir)
    también mide calibración y se llama log-pérdida. El Cap. 3 la reporta              define
P15 Corrección posterior: temperature scaling (eq:marco_temperatura) y vector scaling. Sale la oración que
    remite a la curva riesgo–cobertura, que 2.4 ya no tiene; 2.4.2 ya dice que la calibración no mide la
    separación                                                                          define
    ↓ necesidad — toda métrica se calcula sobre una muestra

2.6.5 Inferencia estadística (sec:marco_eval_estadistica)
P16 Por qué: dos modelos que difieren en centésimas. Bootstrap, intervalo percentil y versión pareada  define
P17 McNemar (decisión 1)                                                                define
P18 Holm                                                                                define
    ↓ retoma P3 — las condiciones de adquisición

2.6.6 Robustez (sec:marco_eval_robustez)
P19 Definición y caída relativa (eq:marco_robustez, solo la relativa: decisión 4), perturbaciones sintéticas
    [hendrycks2019benchmarking]. Límite: cubren una parte de la variación real y no reemplazan la validación
    externa                                                                             define, limita
    ↓ retoma P5 — en qué se apoya el modelo

2.6.7 Interpretabilidad visual (sec:marco_eval_gradcam)
P20 Grad-CAM con su fórmula, sin cambios                                                define
P21 Límites [adebayo2018sanity] y uso: detectar un modelo que se apoya en el rasgo espurio de P5. Sin
    «atajo»                                                                             limita
→ Transición a 2.7: con qué datos y con qué protocolo se evaluó un trabajo decide si su resultado se sostiene
  fuera de su conjunto de origen. Ese es el criterio con que 2.7 revisa la literatura.

Se definen acá (y no se vuelven a definir):
- sesgo y generalización: cambio de dominio, cambio de subpoblación, validación externa, evaluación
  desagregada, rasgo espurio;
- clasificación: matriz de confusión, exactitud, sensibilidad macro, precisión, F1 macro y ponderado,
  especificidad, detección, ROC, AUC;
- generación: las cinco métricas textuales, consistencia diagnóstica, cobertura de entidades clínicas;
- calibración: ECE, MCE, Brier, log-pérdida, temperature scaling y vector scaling;
- inferencia y robustez: bootstrap, McNemar, Holm, robustez;
- interpretabilidad: Grad-CAM.
Se retoman de antes (solo se nombran, con \ref):
- de 2.1: cambio de distribución, particiones, desbalance, entropía cruzada;
- de 2.4: cobertura y riesgo selectivo, calibración (concepto), temperatura, costos;
- de 2.5: calidad descriptiva, fidelidad diagnóstica, vocabulario, origen de la referencia, alucinación.
Extensión: 21 párrafos (P7 y P9 son listas), dos figuras y una tabla, unas 6.5–7 páginas.
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor para 2.6, y «quizas como intro de metricas» (p65) | La vieja 2.9 pasa a ser 2.6.1, la introducción de la evaluación. Explica qué no puede afirmar una métrica sobre el test y anuncia la robustez (2.6.6) y la interpretabilidad (2.6.7), que lo responden |
| «no tengo claro que aporta […] a tu trabajo» (p65) | Cada párrafo de 2.6.1 termina en lo que pide a la evaluación: validación externa, evaluación desagregada, perturbaciones o Grad-CAM. Son los análisis que usa el Cap. 3 (`sec:met_analisis_compl`) |
| «cada conjunto de métricas comience explicando qué aspecto del desempeño pretende evaluar» | 2.6.2, 2.6.3, 2.6.4 y 2.6.5 abren con qué evalúan y por qué importa |
| «alguna solo conviene nombrarlas y dar una explicación breve, con su formula» | Las cinco métricas textuales, que no deciden ninguna elección (Cap. 3), bajan a una o dos oraciones con su fórmula. ROUGE-L queda solo con β = 1 |
| Repetición con 2.4 y el Cap. 1 | Sale el experimento de Groh 2024, porque ya está en 2.4. Salen Jones y el conjunto argentino, porque ya están en el Cap. 1 y son motivación, no concepto. El fototipo queda sin cifras |
| Coherencia con 2.4 | Sale «propiedad que mide la curva riesgo–cobertura de la Sección 2.4.2», que 2.4 ya no tiene |
| Coherencia con el Cap. 3 | Se agrega la log-pérdida, que el Cap. 3 mide y remite a `sec:marco_eval_calib`. McNemar y robustez se ajustan a lo que calcula el código (decisiones 1 y 4) |
| «Evaluación transversal» con `\subsubsection` y el truco de `secnumdepth` | Siete subsecciones planas (decisión 2) |
| Vocabulario del autor | Sin «atajo»: «rasgo espurio» |
| Figura 2.12 fuera de su página; *overfull* en `matriz-confusion.tex` | Se corrigen al compilar |

## Verificación contra la experimentación (2026-10-12)

| Lo que usa la experimentación | Dónde | En 2.6 |
|---|---|---|
| Validación externa en *HIBA*, separada por modalidad, fototipos I–IV | Cap. 3 `09-analisis-complementarios.tex`, Cap. 4 `07-robustez.tex` | P3, P4 |
| Perturbaciones de adquisición (JPEG, ruido, desenfoque, resolución) y caída relativa de la sensibilidad macro | Cap. 3 `09`, `robustness_perturbations.py` | P3, P19 |
| Grad-CAM del Swin | Cap. 3 `09`, `interpretability.py` | P20–P21 |
| Exactitud, sensibilidad macro, F1 macro y ponderado | Cap. 3 `04-criterios-evaluacion.tex` (`tab:met_roles`), `classification.py` | P7 |
| Sensibilidad y especificidad de melanoma, AUC de melanoma; maligno frente a benigno | Cap. 3 `04`, Cap. 4 `09-deteccion-melanoma.tex`, `melanoma_detection.py` | P7 |
| AUC macro (`roc_auc_score`, `ovr`, `macro`) | `classification.py`, `resul/split_lesion_resul_20260926.md` | P7 |
| BLEU-4, ROUGE-L, METEOR, CIDEr, BERTScore (Nivel 1, no decide) | Cap. 3 `04`, `generation.py` | P9 |
| Consistencia diagnóstica (métrica oficial) y cobertura de entidades | Cap. 3 `04`, `clinical_ner.py` | P11 |
| ECE y MCE con diez intervalos, Brier, log-pérdida; *temperature* y *vector scaling* | Cap. 3 `09`, `posthoc_calibration.py` (`nll`) | P13–P15 |
| Bootstrap percentil y pareado (2000 remuestreos) | Cap. 3 `09`, `statistical_tests.py` | P16 |
| McNemar **exacto** (binomial); «La aproximación χ² (Ecuación~\ref{eq:marco_mcnemar}) no se usa en ningún resultado» | Cap. 3 `09`, `mcnemar_exact` | P17 (decisión 1) |
| Holm sobre 21 pares | Cap. 3 `09` | P18 |
| Cobertura y riesgo selectivo de los niveles del ruteo | Cap. 3 `08-pipeline.tex` | P1 remite a 2.4 |
| No se usa: curva riesgo–cobertura, caída absoluta, ROUGE con β ≠ 1 | — | Salen |

## Archivos y labels

- `git mv 08-evaluacion.tex 06-evaluacion.tex`. El contenido de `09-sesgo-robustez.tex` pasa a 2.6.1 y ese
  archivo se borra con `git rm`. En `00-capitulo.tex`, los dos `\input` pasan a ser uno.
- Las fichas viejas `08-evaluacion.md` y `09-sesgo-robustez.md` pasan a `historial.md`.
- Se conservan todos los labels:
  - sección: `sec:marco_evaluacion`, `sec:marco_generalizacion` (que pasa a ser la subsección 2.6.1),
    `sec:marco_eval_clasif`, `sec:marco_eval_texto`, `sec:marco_eval_calib`, `sec:marco_eval_estadistica`,
    `sec:marco_eval_robustez`, `sec:marco_eval_gradcam`;
  - todas las ecuaciones;
  - `fig:marco_matriz_roc`, `fig:marco_confiabilidad`, `tab:marco_familias_texto`.
- Sale `sec:marco_eval_transversal`, que nadie cita.
- Fuera de esta sección: el Cap. 3, en la otra rama, cita `sec:marco_generalizacion` en 8 lugares, y el label
  sigue resolviendo. Si se aprueba la decisión 1, su oración sobre la aproximación χ² queda pendiente, como la de
  «política».

## Citas

Se mantienen:
- `koh2021wilds`, `dinnes2018dermoscopy`, `kittler2016standardization`, `groh2021neural`,
  `daneshjou2022disparities`, `yan2023towards`, `kim2024transparent`;
- `brodersen2010balanced`, `sokolova2009systematic`, `fawcett2006introduction`;
- `papineni2002bleu`, `lin2004rouge`, `banerjee2005meteor`, `vedantam2015cider`, `zhang2020bertscore`,
  `carrera2016validity`, `hartsock2024vision`;
- `guo2017calibration`, `brier1950verification`, `efron1979bootstrap`, `mcnemar1947note`, `holm1979simple`;
- `hendrycks2019benchmarking`, `selvaraju2017gradcam`, `adebayo2018sanity`.

Salen de esta sección:
- `groh2024learningaided` (está en 2.4);
- `jones2022intelligence` y `riccilara2023dataset` (están en el Cap. 1; *HIBA* se presenta en el Cap. 3).

No hay citas nuevas.

## Respuestas del autor (2026-10-12)

Las cuatro aprobadas como se recomendaron. La decisión 1 reemplaza la decisión vigente 6 de `00-capitulo.md`
en lo que hace a McNemar: queda solo la versión exacta, y en el Cap. 3 (otra rama) queda pendiente corregir
«La aproximación $\chi^2$ (Ecuación~\ref{eq:marco_mcnemar}) no se usa en ningún resultado», porque la
ecuación ahora es el valor $p$ exacto.

Ajustes de la redacción que no estaban en la propuesta:
- Los términos nuevos de 2.6.1 y la log-pérdida llevan el inglés entre paréntesis (guía §3, punto 7).
- La cobertura de entidades dice que usa una lista cerrada de términos tomada del vocabulario estandarizado
  de 2.5.1, que es lo que dice también la tabla de familias.
- Para que cada flotante quede en la página de su mención, la Tabla 2.2 se cita al comienzo del párrafo que
  la sigue, y la Figura 2.13 se comenta en un párrafo propio después de ella: el modelo es sobreconfiado, sus
  barras quedan por debajo de la diagonal y esa franja es la brecha que promedia el ECE.
- `matriz-confusion.tex`: el panel (b) se corre 9 mm a la izquierda (`xshift` de 95 a 86 mm), lo que elimina
  el *overfull* de 24.7 pt.

Decisiones (texto de la propuesta):

1. **McNemar, solo la versión exacta** (recomendado). El código usa solo la exacta y el Cap. 3 aclara que la
   χ² no se usa. Por eso `eq:marco_mcnemar` pasaría a ser el valor $p$ binomial,
   $p = \min\bigl(1,\ 2\sum_{i=0}^{\min(b,c)} \binom{b+c}{i} 2^{-(b+c)}\bigr)$, y la χ² saldría. Es el mismo
   criterio que sacó la curva riesgo–cobertura. Cambia la decisión vigente 6 («McNemar en sus dos versiones»).
   Costo: la oración del Cap. 3 que remite a la χ² hay que corregirla en esa rama. Alternativa: dejar las dos
   versiones como hoy.
2. **Siete subsecciones planas** (recomendado), sin «Evaluación transversal» ni `\subsubsection`. El índice no
   cambia, porque muestra solo secciones, y en el texto cada propiedad queda con su número. Alternativa:
   conservar 2.6.4 «transversal» con cuatro sub-subsecciones.
3. **Conservar la tabla de las tres familias de métricas de texto y acortar la prosa** (recomendado). La columna
   «No ve» es lo que pide el tutor: qué información brinda cada métrica y cuál no. Alternativa: sacar la tabla y
   presentar las familias en un párrafo, que ahorra media página.
4. **Robustez solo con la caída relativa** (recomendado). Es la que usa el Cap. 3. La absoluta sale de la
   ecuación.
