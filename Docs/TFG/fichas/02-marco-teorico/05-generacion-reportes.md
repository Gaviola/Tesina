# Ficha 2.5 — Generación automática de reportes dermatológicos

Sección del `.tex`: `Chapters/02-Marco-Teorico/05-generacion-reportes.tex` (hoy `07-generacion-reportes.tex`).

**Estado: aprobada y redactada (2026-10-12).** Extensión resultante: unas 4.5 páginas (p. 54–59), con una tabla, dos figuras y una ecuación. El autor aprobó las cinco decisiones recomendadas. Responde a la
tercera revisión del tutor
(`feedback_cap1_y_2_v3.md`: la propuesta «IDEA» para 2.5, «estructura clínica, calidad descriptiva, fidelidad
diagnóstica, estrategias de generación, errores y recuperación», y el mensaje general). El PDF no tiene
comentarios puntuales sobre esta sección. Hoy ocupa unas 5 páginas (p. 54–59), con tres tablas y dos figuras;
el plan del capítulo fija 4–5. Aplica el criterio que el autor fijó en 2.4: no se presenta lo que la
experimentación no usa (verificado contra `Codigo/` y los Caps. 3 y 5 el 2026-10-12, ver abajo).

## Hilo conductor

Pregunta que responde la sección: ¿qué se le exige a un reporte dermatológico, de qué formas puede generarlo
un VLM, cómo falla el texto generado y qué evidencia puede recibir el generador para fallar menos?

Viene de: 2.3 deja el *prompt*, el aprendizaje en contexto («la Sección 2.5.3 la usa para anclar el
reporte»), la decodificación voraz y su tendencia a repetir [holtzman2020curious], los VLM generativos y el kNN
con sus dos ecuaciones («el espacio contrastivo sirve también de índice de casos parecidos, que la Sección
2.5.5 usa como evidencia para el texto»). 2.4 deja la política de tres salidas, la concordancia y el consenso
de los vecinos, y cierra con el problema: «la decisión de la política llega al lector a través de un texto, y
un texto puede deshacerla […]. Por eso, generar el reporte plantea problemas propios, distintos de los de
clasificar».

Deja instalado: reporte clínico (descripción e impresión diagnóstica), vocabulario estandarizado, calidad
descriptiva, fidelidad diagnóstica, generación de extremo a extremo y condicionada (*grounding*), alucinación,
*hedging*, las fallas de la taxonomía, RAG, evidencia visual por recuperación. Y una necesidad para 2.6: las
categorías, los textos y las abstenciones se evalúan con métricas distintas.

```
(sin subsección: un párrafo de entrada)
P1  Parte del cierre de 2.4 sin repetirlo: si el texto puede deshacer la decisión de la política, hay que
    saber qué se le exige a un reporte, cómo se produce, cómo falla y qué información puede recibir el
    generador para fallar menos. Dos o tres oraciones; ordena la sección                 función: orienta
    ↓ necesidad — qué es lo que se genera

2.5.1 El reporte clínico dermatológico (sec:marco_rep_tarea)
P2  Qué es (registro escrito del examen de una lesión, en la historia clínica, comunica a otro profesional,
    por ejemplo al especialista que recibe la derivación de 2.4). Sus dos partes (decisión vigente 7): la
    descripción de los hallazgos y la impresión diagnóstica que los resume, o los diferenciales si hay duda
    (remite a 2.4.4). La descripción usa un vocabulario estandarizado por consenso [kittler2016standardization];
    ejemplo: los criterios mayores de la lista de 7 puntos (red de pigmento atípica, velo azul-blanquecino,
    patrón vascular atípico) pesan a favor de melanoma [argenziano1998checklist] (verificar los tres
    criterios contra el resumen antes de redactar). Sin tabla (decisión 2)                  define
    ↓ ampliación — de dónde viene la tarea y con qué datos se aprende
P3  Historia condensada: de la descripción automática de imágenes al reporte médico, primero en radiología
    desde 2018 [jing2018automatic, chen2020generating], y con los VLM generativos un único modelo que recibe
    imagen e instrucción [hartsock2024vision]. Todos requieren pares imagen–texto clínico; en dermatología
    son escasos y recientes, y su texto lo escribieron dermatólogos, lo tomaron de libros o lo generó un modelo
    con revisión [shen2025skincare, zeng2025mmskin, yan2025derm1miccv]. Ese origen condiciona su validez como
    referencia (decisión vigente 7; el detalle va al Cap. 3)                              contextualiza
    ↓ necesidad — qué hace correcto a un reporte generado

2.5.2 Calidad descriptiva y fidelidad diagnóstica (sec:marco_rep_ejes)
P4  Calidad descriptiva: correspondencia entre lo que el texto describe y lo que la imagen muestra, con el
    vocabulario de P2, que permite medirla (remite a 2.6)                                 define
P5  Fidelidad diagnóstica: el diagnóstico que nombra el texto es el correcto. Independiente de la anterior,
    con ejemplo dermatológico: un texto describe bien una red de pigmento atípica y cierra en nevo cuando es
    un melanoma; otro nombra melanoma con un velo azul-blanquecino que la imagen no tiene. Un reporte es
    correcto solo si cumple las dos (fig:intro_dos_tareas, `planteo-problema.tex`, decisión vigente 10) define
    ↓ ampliación — la condición que agrega 2.4
P6  Un tercer requisito, que viene de 2.4: la certeza del texto corresponde a la decisión de la política
    (afirma cuando la política afirma, enuncia los candidatos cuando ofrece diferenciales). Sin «no se
    redacta». Los tres requisitos dependen de cómo se produce el texto                  justifica
    ↓ necesidad — cómo se produce

2.5.3 Estrategias de generación (sec:marco_rep_generacion)
P7  De extremo a extremo: $y \sim p_\theta(\cdot \mid x)$; el VLM describe e infiere el diagnóstico, y tiene
    que ser a la vez buen clasificador y buen redactor (fig:marco_generacion_reportes)        define
P8  Condicionada en evidencia externa (eq:marco_rep_condicionada, se copia): $c(x)$ es el diagnóstico de un
    clasificador, los casos recuperados (2.5.5) o los candidatos de la política (eq:marco_politica). Se llama
    *grounding*; es el aprendizaje en contexto de 2.3, que se nombra sin redefinir [brown2020language] define
P9  Qué se gana y qué cuesta: la fidelidad pasa a depender de la evidencia y la descripción sigue a cargo del
    generador; el reporte hereda el error de la evidencia con la misma fluidez que un acierto. La instrucción
    también es parte de la configuración: puede pedir que el modelo exponga su razonamiento antes de concluir
    o que entregue solo el reporte. Oración nueva: un razonamiento explícito enumera hipótesis que después
    descarta, de modo que, leído como parte del reporte, el texto nombra diagnósticos que no sostiene (el
    Cap. 3 separa razonamiento y reporte; decisión 5)                                   justifica
    ↓ limitación — en las dos estrategias el texto puede fallar sin que una métrica de clasificación lo vea

2.5.4 Fallas del texto generado (sec:marco_rep_fallas)
P10 Alucinación: definición y origen [ji2023survey]; en descripción de imágenes, en parte por el peso de los
    patrones del lenguaje [rohrbach2018object] (lo retoma el Cap. 5 con las ablaciones de la imagen); en VLM
    [bai2024hallucination]; los VLM médicos ajustados al dominio alucinan más [gu2024medvh]. Por qué cuesta en
    medicina: un hallazgo inventado tiene la misma forma que uno real y puede cambiar una conducta  define
P11 *Hedging* (sin cita, decisión vigente 6): texto genérico que no compromete un diagnóstico. Expresar
    incertidumbre no es una falla; lo es cuando no depende del caso. [kalai2025hallucinate] sobre los
    incentivos de la evaluación. Los diferenciales que justifica la política de 2.4 son lo opuesto  define
P12 Tabla tab:marco_fallas con las cinco categorías que asigna la taxonomía del trabajo (diagnóstico
    incorrecto, contradicción, *hedging*, repetición, texto insuficiente), de mayor a menor gravedad. La
    repetición remite a la decodificación voraz de 2.3. La alucinación sale de la tabla (decisión 3): puede
    acompañar a cualquiera, incluso a un diagnóstico correcto, y no se reconoce por la forma del texto  define
P13 Las métricas de solapamiento con una referencia no detectan si se transmiten los hallazgos correctos
    [hartsock2024vision]; la fidelidad y el contenido clínico se miden por separado (2.6). Una forma de
    reducir estas fallas es darle al generador información que no obtiene de la imagen   justifica
    ↓ necesidad — de dónde sacar esa información

2.5.5 La recuperación como fuente de evidencia (sec:marco_rep_recuperacion)
P14 RAG en palabras, sin ecuación (decisión 1): base de documentos, recuperador y generador; en la formulación
    original el recuperador se entrena junto con el generador, que combina las salidas obtenidas con cada
    documento, y la base se cambia sin reentrenar [lewis2020retrievalaugmented]. En radiología, recuperar
    reportes de casos parecidos y preferir los de mismos hallazgos mejora lo generado [sun2025factaware]
                                                                                          define
P15 Con una base de casos etiquetados, lo recuperable son imágenes: los $k$ vecinos de eq:marco_vecinos (2.3,
    sin redefinir) y su diagnóstico o localización como evidencia visual; $c(x) = \psi(\mathcal{N}_k(x))$.
    Antecedente: recuperar descripciones de imágenes parecidas y pasarlas como *prompt*, sin entrenar el
    recuperador [ramos2023smallcap]. Las tres diferencias con la formulación original, en prosa (recuperador
    congelado, sin combinar salidas, lo recuperado es de la misma modalidad). Sus límites ya están en 2.4.3
    (los vecinos existen aunque no se parezcan): se remiten, no se repiten                define
    ↓ consecuencia — evidencia y señal cumplen funciones distintas
P16 (`sec:marco_integracion`, se conserva con \phantomsection) La recuperación aporta qué diagnosticar y la
    señal de 2.4 decide cuánto afirmar: integradas, la evidencia condiciona el texto y la política elige si
    afirma, ofrece diferenciales o deriva el caso. Sin tabla (decisión 4)                 integra
→ Transición a 2.6: clasificadores, generadores y señales producen categorías, textos y decisiones de
  abstención; cada salida exige sus métricas, y medirlas en el test de la misma fuente no garantiza el
  desempeño fuera de ella (que es por donde empieza 2.6).

Se definen acá (y no se vuelven a definir): reporte clínico, vocabulario estandarizado, calidad descriptiva,
fidelidad diagnóstica, generación de extremo a extremo y condicionada, *grounding*, alucinación, *hedging*,
contradicción, texto insuficiente, RAG, evidencia visual.
Se retoman de antes (solo se nombran, con \ref): *prompt*, aprendizaje en contexto, decodificación voraz y
repetición, VLM generativo, kNN y sus ecuaciones (2.3); política de tres salidas, diferencial, derivación,
consenso de los vecinos (2.4).
Remisiones hacia adelante: métricas de texto, consistencia diagnóstica y cobertura de entidades (2.6); qué
texto de referencia trae cada conjunto, la plantilla diferencial y el kNN concreto (Cap. 3).
Extensión: 16 párrafos, dos ecuaciones (las dos de generación; sale la de RAG), una tabla, dos figuras, unas
4–4.5 páginas.
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor: «estructura clínica, calidad descriptiva, fidelidad diagnóstica, estrategias de generación, errores y recuperación» | Cinco subsecciones en ese orden. El título pasa a «Generación automática de reportes dermatológicos» y 2.5.3 a «Estrategias de generación» |
| Criterio del autor (2.4): nada que la experimentación no use | Sale la ecuación de RAG (decisión 1), la recomendación de conducta (decisión 2), la tabla de mecanismos con la fila de recuperar documentos (decisión 4) y `khandelwal2020generalization` (decisión 4) |
| Redundancia con 2.3 y 2.4 | El kNN, el aprendizaje en contexto y la decodificación se nombran con `\ref`. La concordancia ya no se vuelve a presentar (hoy lo hacen la tabla de mecanismos y el párrafo de integración), y el límite de los vecinos remite a 2.4.3 |
| Coherencia con el código | La tabla de fallas pasa a las cinco categorías de `error_taxonomy.py`; la alucinación, que el código no detecta por reglas, queda en prosa (decisión 3) |
| Hilo con el Cap. 3 y el Cap. 5 | P9 agrega el razonamiento explícito, que el Cap. 3 separa del reporte y el Cap. 5 analiza (`02-reporte-razonamiento.tex`). P10 deja dicho el peso del lenguaje, que retoman las ablaciones de la imagen |
| «No redacta» (tutor, p44; preferencia del autor) | Sale «o no se redacta» de los ejes y de la integración: el tercer requisito y P16 dicen «deriva el caso» |
| Ejemplos del dominio | P2 (criterios de la lista de 7 puntos), P5 (red de pigmento atípica, nevo frente a melanoma, velo inventado) |
| Párrafos que juntan ideas | Los ejes se separan en tres párrafos con un requisito cada uno; el párrafo de costos (hoy mezcla herencia del error, cantidad de modelos e instrucción) queda con dos ideas: herencia del error e instrucción |
| Transición desde 2.4 | P1 parte del cierre de 2.4 (el texto puede deshacer la política) |
| Transición a 2.6 | Se completa con el problema por el que empieza 2.6 (el test de la misma fuente) |

## Verificación contra la experimentación (2026-10-12)

| Lo que usa la experimentación | Dónde | En 2.5 |
|---|---|---|
| Reporte con descripción e impresión, sin diferencial ni recomendación | Cap. 3 `07-generacion-reportes.tex` | P2 |
| Cascada clasificador–generador, *grounding* solo de inferencia, condiciones con *oracle* y sin anclaje | Cap. 3 `08-pipeline.tex`, `generate_report.py` | P8–P9 (sin las condiciones, que son Cap. 3) |
| Plantillas *noreasoning*, diferencial y de recuperación | `generate_report.py` | P9 (instrucción), P8 ($c(x)$ = candidatos) |
| Bloques de razonamiento que se quitan antes de medir | Cap. 3, Cap. 5 | P9 |
| Decodificación voraz y repetición | Cap. 3, `repetition_postprocess.py` | 2.3; P12 remite |
| Taxonomía: repetición, contradicción, diagnóstico incorrecto, *hedging*, insuficiente | `error_taxonomy.py` | P12 |
| *Hedging* como motivo del *pipeline* | Cap. 3 `08-pipeline.tex` (cita `sec:marco_rep_fallas`) | P11 |
| Riesgo de alucinación como cautela | Cap. 3 `04-criterios-evaluacion.tex` | P10 |
| kNN sobre DermLIP, $k = 3$, diagnóstico y localización en una frase fija | Cap. 3 `08-pipeline.tex`, `build_rag_index.py` | P15 (como concepto) |
| RAG como nombre del índice | Cap. 3 `02-flujo-trabajo.tex` | P14 |
| Ablaciones de la imagen (Cap. 5, pendiente) | `05-Resultados-Generacion/06-aporte-imagen-vlm.tex` | P10 |
| No se usa: RAG de Lewis entrenado y con marginalización, recuperación de documentos de texto, kNN-LM | — | Salen la ecuación, la fila de la tabla y `khandelwal2020generalization` |

## Archivos y labels

- `git mv 07-generacion-reportes.tex 05-generacion-reportes.tex`; `00-capitulo.tex` cambia ese `\input`. La ficha
  vieja `07-generacion-reportes.md` pasa a `historial.md`.
- Se conservan todos los labels de sección, porque los usan 2.3 (`sec:marco_rep_generacion`,
  `sec:marco_rep_recuperacion`), la vieja 2.8 (`sec:marco_rep_tarea`, `sec:marco_rep_ejes`,
  `sec:marco_rep_fallas`), el estado del arte (`sec:marco_rep_ejes`, `sec:marco_recuperacion_imagenes`,
  `sec:marco_integracion`) y el Cap. 3 (`sec:marco_rep_generacion`, `sec:marco_rep_fallas`):
  `sec:marco_reportes`, `sec:marco_rep_tarea`, `sec:marco_rep_ejes`, `sec:marco_rep_generacion`,
  `sec:marco_rep_fallas`, `sec:marco_rep_recuperacion`, `sec:marco_rag`, `sec:marco_recuperacion_imagenes`,
  `sec:marco_integracion`.
- Ecuaciones: `eq:marco_rep_condicionada` se copia. Sale `eq:marco_rag`, que nadie cita fuera de la sección.
- Tablas: `tab:marco_fallas` se reescribe con cinco filas. Salen `tab:marco_partes_reporte` y
  `tab:marco_mecanismos`, que solo se citan en la propia sección.
- Figuras: `planteo-problema.tex` (`fig:intro_dos_tareas`) y `generacion-reportes.tex`
  (`fig:marco_generacion_reportes`) se mantienen sin cambios.

## Citas

Se mantienen: `kittler2016standardization`, `argenziano1998checklist`, `jing2018automatic`,
`chen2020generating`, `hartsock2024vision`, `shen2025skincare`, `zeng2025mmskin`, `yan2025derm1miccv`,
`brown2020language`, `ji2023survey`, `rohrbach2018object`, `bai2024hallucination`, `gu2024medvh`,
`kalai2025hallucinate`, `holtzman2020curious` (si la tabla lo sigue citando; si no, basta el `\ref` a 2.3),
`lewis2020retrievalaugmented`, `sun2025factaware`, `ramos2023smallcap`.
Sale: `khandelwal2020generalization` (decisión 4). No hay citas nuevas.

## Respuestas del autor (2026-10-12)

Las cinco aprobadas como se recomendaron. Además, en la misma revisión el autor pidió cambiar «política» por
«regla de decisión» (hecho en 2.4, commit dad245e), así que 2.5 usa «regla de decisión» y la figura
`generacion-reportes.tex` cambia el nodo «Política» por «Regla de decisión». Los tres criterios mayores de la
lista de 7 puntos se verificaron contra Dermoscopedia y dermoscopy.org (el PDF de Argenziano no está en
`Papers/`).

Decisiones (texto de la propuesta):

1. **RAG sin ecuación** (recomendado). La experimentación no entrena el recuperador ni combina salidas: solo
   usa la variante por contexto. Queda RAG en palabras, con lo que hace falta para decir en qué difiere la
   variante. Es el mismo criterio que sacó la curva riesgo–cobertura de 2.4. La decisión vigente 4 lista la
   fórmula de RAG entre las verificadas; eso dice cómo copiarla, no obliga a conservarla.
2. **El reporte con dos partes y sin tabla** (recomendado). La decisión vigente 7 y el Cap. 3 dicen que las
   partes son la descripción y la impresión diagnóstica; la recomendación de conducta no se genera ni se
   evalúa. Con dos partes, la tabla no aporta frente a una oración.
3. **La tabla de fallas con las cinco categorías de la taxonomía** (recomendado), y la alucinación en prosa.
   Hoy la tabla tiene seis filas y una es la alucinación, que la taxonomía del trabajo no asigna. Así el
   Cap. 5 presenta exactamente las categorías que define 2.5.
4. **Sin tabla de mecanismos ni `khandelwal2020generalization`** (recomendado). De sus tres filas, una es la
   recuperación de documentos, que el trabajo no usa, y otra repite la concordancia de 2.4. El cierre queda
   en un párrafo. El kNN-LM de Khandelwal es recuperación para un modelo de lenguaje, más lejos de lo que se
   hace que el antecedente de `ramos2023smallcap`.
5. **El razonamiento explícito en una oración, sin cita nueva** (recomendado). Hace falta porque el Cap. 3
   separa razonamiento y reporte y el Cap. 5 lo analiza. La alternativa es citar *chain-of-thought* (Wei et
   al., 2022), que hoy no está en el `.bib` y habría que verificar e incorporar.
