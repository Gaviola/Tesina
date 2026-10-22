# Ficha 3.7 — Pipeline propuesto

**Revisión del tutor (21/10/2026), aplicada el 22/10:** Antes era 3.7. Orden pedido por el tutor: componentes disponibles → necesidad de integrarlos (desde el estado del arte, `sec:marco_rep_fallas` y `sec:marco_senales_confianza`; sale «como muestra el Capítulo 4», 25) → arquitectura (figura) → funcionamiento (cascada, recuperación) → decisiones de salida (ruteo). En la cascada, el diseño de la instrucción va antes del piloto. Las cuatro fuentes de diagnóstico, el *oracle* y la línea base sin generador pasan a 3.7 (decisión del autor del 22/10). La concordancia como señal se presenta como hipótesis del diseño.

**Revisión del autor (21/10/2026):** el autor quitó la oración que declaraba que la concordancia se eligió como señal con resultados de prueba conocidos; queda declarado solo el piloto de *noreasoning* (17 imágenes de prueba).

**Revisión del autor (20/10/2026):** T2 se justifica en vez de «queda fuera»: no necesita del generador, la resuelve el clasificador con el umbral de 3.3; las dos decisiones con la prueba a la vista (17 imágenes del piloto de *noreasoning*, concordancia como señal) se declaran acá, donde se describen, y no en 3.3; el oracle define «cota superior» (ya no la define 3.3); salen repeticiones (fuga de información en el índice, «la recuperación es el segundo predictor», «no hay umbral que ajustar» dicho dos veces, «sin el bloque de razonamiento»); «no redacta» → «no genera texto»; la línea base sin generador ya no remite a `sec:met_lineas_base`.

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Ahora es 3.7 (antes 3.8). Se presenta como la propuesta central; sin fechas; el piloto de noreasoning en una oración y la declaración de la concordancia elegida remitida a 3.3; cierre que enlaza con las líneas base de 3.3 y con 3.8.

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita el 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/07-pipeline.tex` (antes `08-pipeline.tex`; sale de `06-pipeline.tex`). Labels: `sec:met_pipeline` (sección); `sec:met_cascada`, `sec:met_recuperacion`, `sec:met_ruteo` (subsecciones; `sec:met_ruteo` y `sec:met_cascada` los referencia 3.3, `sec:met_pipeline` la referencia 3.3 y el capítulo). Figuras: `fig:met_pipeline`, `fig:met_ruteo`. Ecuación: `eq:met_politica_ruteo`.

## Hilo conductor

Pregunta que responde la sección: ¿cómo se encadenan el clasificador, la recuperación y el generador en un único sistema, y qué regla decide si el reporte afirma un diagnóstico, enuncia candidatos o deriva el caso?

Viene de: 3.6 (Generación de reportes) deja los generadores (Mini-VLM, LLaVA-Med y SkinVL) ajustados con LoRA, la separación entre reporte y razonamiento y la decodificación (`sec:met_generacion`). De 3.4 y 3.5 toma el clasificador supervisado (Swin-Tiny) y el kNN sobre *embeddings* de DermLIP, uno de los modos de DermLIP. De 3.3 toma la métrica de generación, la declaración de las decisiones tomadas con resultados de prueba a la vista (`sec:met_seleccion`), y el anuncio de las referencias propias del *pipeline*, la cota superior (*oracle*) y la línea base sin generador (`sec:met_lineas_base`).

Deja instalado: (a) el sistema completo y sus tres salidas (reporte definitivo, reporte diferencial, derivación) con su regla de decisión; (b) la línea base sin generador, que aísla lo que aporta el generador y que, junto con el *oracle*, completa las referencias anunciadas en 3.3; (c) la cascada anclada a tres fuentes de diagnóstico (Swin-Tiny, DermLIP y *oracle*) más el caso sin anclaje, que los Caps. 4 y 5 comparan; (d) la pregunta pendiente, cómo se comporta el sistema fuera de las condiciones en que se entrenó, que 3.8 (Evaluación en otros escenarios) responde.

```
Intro (sin subsección)
P1  Los generadores de 3.6 son VLM generativos con dos limitaciones que el trabajo evalúa por separado:
    como clasificadores no discriminan bien (resultados en Cap.~\ref{cp:res_clasif}) y al redactar no se
    comprometen con un diagnóstico y recurren a reservas (hedging, sec:marco_rep_fallas). El pipeline es la
    propuesta central y atiende ambas separando las tareas: el clasificador decide el diagnóstico y el
    generador redacta el reporte. Resuelve T1 y T3; T2 (detección de melanoma) queda fuera porque el ruteo
    no emite una decisión binaria                                                  justifica · delimita
    ↓ necesidad — hace falta una manera concreta de separar las tareas
P2  La cascada clasificador–generador: el clasificador entrega una clase, que se inyecta en el prompt junto
    con la imagen, y el generador redacta un reporte que la afirma (grounding, sec:marco_rep_generacion).
    Su costo: el reporte hereda el error del clasificador. Su límite: una sola clase no indica cuándo el
    clasificador duda. Figura~\ref{fig:met_pipeline}                                describe · limita
    ↓ contraste — el límite de la cascada pide un segundo predictor que permita saber si el primero duda
P3  Un segundo predictor, con otros datos y otro sesgo: un kNN sobre embeddings de DermLIP que recupera los
    casos de entrenamiento más parecidos (cover1967nearest). Sus vecinos cumplen dos funciones: evidencia
    textual para el generador y base de una señal de concordancia con el clasificador
    (sec:marco_concordancia)                                                      define · justifica
    ↓ ampliación — las dos funciones se detallan en el orden de la cascada: instrucción y fuentes del
      diagnóstico, recuperación como contexto, recuperación como ruteo

3.7.1 Cascada clasificador–generador (grounding) (sec:met_cascada)
P4  La instrucción con que el generador recibe el diagnóstico: la variante noreasoning pide solo el reporte
    final, prohíbe los bloques de razonamiento y prohíbe mencionar diagnósticos alternativos. Motivo: los
    generadores razonan en voz alta y contradicen el diagnóstico que reciben; prohibirlo los obliga a
    comprometerse. Plantilla completa en Apéndice~\ref{ap:prompts}. Se eligió en un piloto de 100 imágenes
    de HAM10000 con el diagnóstico verdadero inyectado, midiendo en cuántos reportes se afirmaba; 17 de
    esas imágenes son de la prueba (sec:met_seleccion)                              define · justifica
    ↓ necesidad — falta decir de dónde viene el diagnóstico que entra al prompt
P5  Cuatro fuentes del diagnóstico, comparadas con el mismo generador: Swin-Tiny (argmax, semilla 42, ancla
    principal, partición por lesión, sec:met_supervisados); DermLIP zero-shot (alternativa sin
    entrenamiento sobre HAM10000, sec:met_clasif_vlm); *oracle* (diagnóstico verdadero, cota superior, no
    usable en la práctica); y sin anclaje (generador sin diagnóstico, muestra qué aporta el anclaje)
                                                                                  describe
    ↓ consecuencia — el generador es el mismo en las cuatro fuentes: solo cambia el diagnóstico que recibe
P6  Los generadores son los de sec:met_generacion, con los pesos ajustados allí; la cascada no los
    reentrena (el grounding es solo de inferencia). La decodificación es la de esa sección y los reportes
    se evalúan sin el bloque de razonamiento, con la métrica de sec:met_protocolo       describe · delimita
    ↓ contraste — hasta acá la cascada usa solo al clasificador; ahora entra la recuperación

3.7.2 Grounding por recuperación (sec:met_recuperacion)
P7  El kNN es el de sec:met_clasif_vlm, usado como índice de casos y no como clasificador: embeddings de
    DermLIP normalizados, similitud coseno, k = 3, voto mayoritario; con tres vecinos de clases distintas el
    voto cae en el más cercano, y ese es el diagnóstico que el kNN registra en el nivel de abstención
    (sec:met_ruteo). El índice contiene solo imágenes de entrenamiento de la partición por lesión
    (sec:met_particiones), 6 447 imágenes, sin imágenes ni lesiones de test. Por qué: si una foto de test
    tiene como vecina otra de su misma lesión, el voto mide memoria y no generalización (la fuga se define
    en sec:marco_regularizacion)                                                   define · justifica
    ↓ necesidad — los vecinos tienen que entrar al prompt como texto
P8  El contexto es una frase fija con los diagnósticos de los tres vecinos y, si el metadato lo trae, su
    localización. Dos plantillas: recuperación sola (sin clasificador, pide el diagnóstico) y Swin más
    recuperación (diagnóstico del ancla y contexto, sin diferenciales), que reemplaza a noreasoning; por eso
    es un brazo de comparación y no entra en la cascada del ruteo. En el ruteo la recuperación cumple
    además la función de segundo predictor (sec:met_ruteo)                          describe · delimita
    ↓ contraste — hasta acá la recuperación es evidencia para el generador; ahora es una señal de decisión

3.7.3 Ruteo por concordancia en tres niveles (sec:met_ruteo)
P9  La señal del ruteo es la concordancia entre los dos predictores (sec:marco_concordancia). Usa sus
    decisiones y no sus probabilidades: no depende de la calibración de la softmax ni necesita un umbral.
    Los predictores tienen sesgos distintos (uno ajusta fronteras de decisión sobre HAM10000,
    tschandl2018ham10000; el otro es no paramétrico sobre una representación preentrenada), por lo que se
    espera que sus errores no coincidan siempre. Que la concordancia separe aciertos de errores se comprueba
    en Cap.~\ref{cp:res_clasif}, no se supone; la elección de la señal se declara en sec:met_seleccion
                                                                                  justifica · limita
    ↓ necesidad — con esa señal hace falta una regla que asigne cada caso a un nivel
P10 Con a(x) la concordancia entre el clasificador y el voto del kNN y κ(x) el consenso de los vecinos
    (eq:marco_knn; con k = 3 vale 1/3, 2/3 o 1), la regla es la ecuación eq:met_politica_ruteo. Lista de
    tres niveles excluyentes con su acción: afirmativo (a = 1; reporte definitivo con el diagnóstico del
    clasificador y plantilla noreasoning), diferencial (a = 0 y κ > 1/3; reporte que enuncia el par
    clasificador–kNN con la plantilla diferencial) y abstención (a = 0 y κ = 1/3; no se genera reporte y el
    caso se deriva). Plantillas en Apéndice~\ref{ap:prompts}; la plantilla diferencial atribuye la
    incertidumbre al clasificador aunque un candidato venga del kNN y se describe tal cual. Como la señal es
    discreta no hay umbral y los niveles cubren todos los casos. Figura~\ref{fig:met_ruteo}
                                                                                  define
    ↓ interpretación — la regla se lee como la política de tres salidas del Cap. 2
P11 Es la política de tres salidas de sec:marco_tres_salidas, con la concordancia en lugar de la confianza.
    La abstención es una predicción selectiva (sec:marco_pred_selectiva): en ese nivel no se emite reporte.
    El diferencial presenta como candidatos el diagnóstico del clasificador y el voto del kNN, no los dos
    primeros del clasificador, porque lo que el ruteo mide es el desacuerdo entre ambos predictores. La regla
    dice qué se emite, pero no cuánto aporta el generador                           interpreta · delimita
    ↓ necesidad — para medir el aporte del generador hace falta una referencia que use el ruteo sin redactar
P12 Línea base sin generador: mismo ruteo y mismo clasificador, sin redactar (el afirmativo devuelve el
    diagnóstico, el diferencial devuelve el par, la abstención queda igual). Junto con el *oracle* completa
    las referencias del pipeline anunciadas en sec:met_lineas_base; las diferencias se analizan con las
    pruebas de sec:met_estadistica                                                  define · cierra
    → Transición a 3.8: «Con el pipeline queda descrito el sistema completo; falta ver cómo se evalúa fuera
      de las condiciones en que se entrenó.»
```

Figuras de la sección: `fig:met_pipeline` (pipeline completo, citada en P2, insertada tras P2) y `fig:met_ruteo` (ruteo en tres niveles, citada en P10, insertada tras P10). Ecuación: `eq:met_politica_ruteo` (P10). Lista de tres niveles (P10).

Se definen acá (y no se vuelven a definir): la cascada como arquitectura y la variante *noreasoning* (la noción general de *grounding* es de `sec:marco_rep_generacion`); las cuatro fuentes del diagnóstico, incluido el *oracle* como cota superior y el caso sin anclaje; la construcción del contexto de recuperación con sus dos plantillas; el kNN usado como índice (su definición como clasificador está en 3.5); la regla de tres niveles con su ecuación; la línea base sin generador.
Se retoman de antes (solo se nombran, con `\ref`): *grounding* (`sec:marco_rep_generacion`); *hedging* y fallas del texto (`sec:marco_rep_fallas`); concordancia y consenso (`sec:marco_concordancia`, `eq:marco_knn`); las tres salidas y la predicción selectiva (`sec:marco_tres_salidas`, `sec:marco_pred_selectiva`); la fuga de información (`sec:marco_regularizacion`). De 3.2, 3.3, 3.4, 3.5 y 3.6: la partición por lesión (`sec:met_particiones`), la métrica de generación (`sec:met_protocolo`), la declaración de decisiones con la prueba a la vista (`sec:met_seleccion`), las referencias anunciadas (`sec:met_lineas_base`), las pruebas estadísticas (`sec:met_estadistica`), Swin-Tiny (`sec:met_supervisados`), DermLIP y su kNN (`sec:met_clasif_vlm`), los generadores y su decodificación (`sec:met_generacion`).
Remisiones hacia adelante: resultados de clasificación (`cp:res_clasif`); evaluación en otros escenarios (3.8, solo por la frase de transición, sin `\ref`); Apéndice B (`ap:prompts`).
Extensión: 12 párrafos, dos figuras y una lista de tres ítems; unas 3.5 páginas (estimación del encabezado del `.tex`).

## Subsecciones

Tres, bajo una introducción de tres párrafos (P1–P3) que no tiene subsección:
- «Cascada clasificador–generador (*grounding*)» (P4–P6), `sec:met_cascada`.
- «*Grounding* por recuperación» (P7–P8), `sec:met_recuperacion`.
- «Ruteo por concordancia en tres niveles» (P9–P12), `sec:met_ruteo`: la señal es la concordancia de `sec:marco_concordancia`, no una incertidumbre calibrada.
Título de la sección: «Pipeline propuesto» (sin «ensamble» ni «consciente de la incertidumbre»).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas y referencias internas |
|---|---|---|---|
| P1 | Dos limitaciones de los VLM (clasificador que no discrimina; generador que hedea), el pipeline como propuesta central que separa las tareas, y su alcance: T1 y T3; T2 queda fuera porque el ruteo no emite decisión binaria. Sin cifras; remite a `cp:res_clasif`. | Limitaciones: `Chapters/02-Marco-Teorico/05-generacion-reportes.tex` (`sec:marco_rep_fallas`). Discriminación: 3.5 y Cap. 4. | `sec:met_generacion`, `sec:marco_rep_fallas`, `cp:res_clasif` |
| P2 | Cascada: el clasificador entrega una clase, que va en el prompt con la imagen; costo (hereda errores) y límite (una clase no expresa duda). Cita la figura del pipeline. | `Docs/experimentacion/experimentacion.tex`, `fig:cascada` (sin cifras). Costo y límite: `05-generacion-reportes.tex` (`sec:marco_rep_generacion`). | `sec:marco_rep_generacion`, `fig:met_pipeline` |
| P3 | El kNN de DermLIP como segundo predictor; dos funciones: evidencia textual y señal de concordancia. | `Chapters/02-Marco-Teorico/` (`eq:marco_vecinos`, `eq:marco_knn`). | `cover1967nearest`; `sec:marco_concordancia` |
| P4 | Variante *noreasoning*: pide solo el reporte, prohíbe razonamiento y diferenciales; motivo: razonamiento en voz alta y contradicción del diagnóstico. Elegida en un piloto de 100 imágenes de HAM10000 con el diagnóstico verdadero, midiendo en cuántos reportes se afirmaba; 17 son de la prueba. | Plantilla: `Codigo/scripts/generate_report.py` líneas 142–147 (`GROUNDED_TEMPLATES["noreasoning"]`); uso en la cascada, líneas 477–484. Motivo y piloto: `Codigo/docs/ideas/ensamble_clasificador_generador_plan_20260605.md` §9.2 y §9.5; `Codigo/docs/resul/ensamble_resul_20260607.md` §1–3 (el desglose por partición del piloto no va en el texto; la declaración está en 3.3). | `ap:prompts`, `sec:met_seleccion` |
| P5 | Cuatro fuentes: Swin-Tiny (ancla por lesión, semilla 42); DermLIP zero-shot; *oracle*; sin anclaje. | Ancla: `Codigo/docs/resul/revision_experimentacion_20261003.md` §1 («`full_dx_swin_les.csv` = argmax de Swin semilla 42»); `Codigo/scripts/make_dx_csv.py` (corrida `swin_tiny_sweep_t06_les_cwnone`, `Codigo/docs/ejecuciones.md` línea 243). DermLIP zero-shot: `Codigo/scripts/dermlip_split_eval.py` (el zero-shot no depende de la partición). *Oracle*: gt de `Codigo/outputs/full_dx_oracle.csv` (`build_uncertainty_3tier.py`, valor por defecto). | `sec:met_supervisados`, `sec:met_clasif_vlm` |
| P6 | Generadores de 3.6 sin reentrenar para la cascada (solo inferencia); decodificación de 3.6; reporte evaluado sin razonamiento. | Decisión: `Codigo/docs/ideas/ensamble_clasificador_generador_plan_20260605.md` §2.2 («el grounding es solo de inferencia»). Reporte sin razonamiento: `revision_experimentacion_20261003.md` §2.2. | `sec:met_generacion`, `sec:met_protocolo` |
| P7 | kNN: DermLIP ViT-B/16 normalizado, coseno, k = 3, voto, empate al más similar (que es el diagnóstico del kNN en la abstención); índice de train de la partición por lesión (6 447 imágenes); motivo de la fuga por foto de la misma lesión. | `Codigo/scripts/dermlip_split_eval.py` líneas 100–111 (kNN, empate, texto del contexto); índice por lesión: sección `lesion` del mismo archivo (genera `Codigo/outputs/rag/rag_context_les.csv`). Tamaño del train: `lesion.n_train` = 6447 en `Codigo/outputs/results/dermlip/dermlip_split_eval.json`, coincide con 3.2 (`02-datos.tex`) y 3.4. Partición: `Codigo/scripts/make_lesion_disjoint_split.py`. | `sec:met_clasif_vlm`, `sec:met_particiones`, `sec:marco_regularizacion`, `sec:met_ruteo` |
| P8 | Frase del contexto con diagnósticos y localización; plantilla de recuperación sola (`RAG_TEMPLATE`) y de Swin + recuperación (`GROUNDED_RAG_TEMPLATE`), esta última brazo de comparación fuera de la cascada del ruteo. | `Codigo/scripts/generate_report.py` líneas 150–163 (plantillas), 495–501 (cuál se usa). Formato del contexto: `dermlip_split_eval.py` línea 111. | `sec:met_ruteo` |
| P9 | Por qué concordancia: decisiones y no probabilidades, sin calibración ni umbral; sesgos distintos; la utilidad de la señal se comprueba en el Cap. 4; la elección de la señal se declara en 3.3. | `Codigo/scripts/build_uncertainty_agreement.py` (encabezado, regla de acuerdo). Origen de la elección: `Codigo/docs/ideas/incertidumbre_p54_plan_20260725.md` §«Pivote de señal» (no se cita en el texto). | `sec:marco_concordancia`, `tschandl2018ham10000`, `cp:res_clasif`, `sec:met_seleccion` |
| P10 | Ecuación de la política, valores de κ con k = 3, lista de tres niveles con su acción; plantillas al Apéndice B; la plantilla diferencial atribuye la incertidumbre al clasificador; no hay umbral y los niveles cubren todos los casos. | `Codigo/scripts/build_uncertainty_3tier.py` líneas 69–76 (reglas: `s == k` → afirmativo; `n_distinct >= 3` → abstención; resto → diferencial; candidatos `f"{s}; {k}"`). Plantilla diferencial: `generate_report.py` línea 167 (`DIFFERENTIAL_TEMPLATE`). Abstención sin generación: `Codigo/docs/resul/reanclaje_cascada_resul_20261003.md` §2. | `eq:marco_knn`, `eq:met_politica_ruteo`, `ap:prompts`, `fig:met_ruteo` |
| P11 | Relación con las tres salidas del Cap. 2; abstención como predicción selectiva; el diferencial no es el top-2 del clasificador; la regla no dice cuánto aporta el generador. | `revision_experimentacion_20261003.md` §2.1 (el diferencial recibe {top-1 de Swin, voto kNN}). | `sec:marco_tres_salidas`, `sec:marco_pred_selectiva` |
| P12 | Línea base sin generador: mismo ruteo y clasificador, sin redactar; completa con el *oracle* las referencias anunciadas en 3.3; diferencias analizadas con las pruebas de 3.3; transición a 3.8. | `Codigo/scripts/ensemble_bootstrap.py` líneas 209–215 (`mech`, `mech_d`). | `sec:met_lineas_base`, `sec:met_estadistica` |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `fig:met_pipeline` (`Figures/Capitulos/03-Materiales-Metodos/pipeline.tex`) | Imagen → clasificador (Swin-Tiny o DermLIP) → diagnóstico; imagen → kNN sobre el índice de train → contexto; concordancia → ruteo → generador (*noreasoning*) → reporte; abstención → derivación. Sin cifras. | `experimentacion.tex` `fig:cascada`. Base de `Figures/Capitulos/02-Marco-Teorico/mapa-capitulo.tex`, que dice «versión simplificada del diagrama de `sec:met_pipeline`»: si uno cambia, revisar el otro. | incluida tras P2 (`\input`) |
| `fig:met_ruteo` (`Figures/Capitulos/03-Materiales-Metodos/ruteo.tex`) | Tres niveles con su condición en la flecha. Sin cifras. | `experimentacion.tex` `fig:incertidumbre`, sin porcentajes ni coberturas. | incluida tras P10 (`\input`) |
| Lista de tres niveles | Los tres niveles con su acción | Texto de P10 | en el cuerpo (`enumerate`) |

No hay tablas. Los estilos de `13-Figuras.sty` alcanzan.

## Prosa ya escrita que se conserva

Ninguna del andamiaje. Se conservan los títulos de subsección.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`):** texto completo de las plantillas que usa la sección: *noreasoning* (`GROUNDED_TEMPLATES["noreasoning"]`), recuperación sola (`RAG_TEMPLATE`), Swin + recuperación (`GROUNDED_RAG_TEMPLATE`), diferencial (`DIFFERENTIAL_TEMPLATE`) y línea base (`REPORT_PROMPT`). Para la abstención no hay plantilla.
- **Apéndice E (`ap:reproducibilidad`):** los scripts del ruteo y del índice (`build_uncertainty_3tier.py`, `dermlip_split_eval.py`, `make_dx_csv.py`), con sus parámetros.

## Lo que NO va en esta sección (y dónde está)

- Tamaños de los niveles (cuántos casos caen en cada uno) y cobertura del diagnóstico verdadero por nivel: Cap. 4 (clasificación y ruteo) y Cap. 5 (cascada). Ningún número de resultado en esta sección.
- Consistencia diagnóstica de la cascada y de la línea base, diferencias con su intervalo: Cap. 5. La métrica en sí (solo reporte, *matcher* estricto) está en 3.3.
- Medición de la variante *noreasoning* y de las otras variantes del prompt sobre el *oracle*: Cap. 4 o Apéndice C. La declaración de que el piloto incluía imágenes de prueba está en 3.3 (`sec:met_seleccion`).
- Resultados de RAG (la corrida por lesión no tiene resultado registrado todavía, `Codigo/docs/ejecuciones.md`): Cap. 5.
- Calibración de la softmax (ECE, temperatura): Cap. 4 y 3.8 (calibración post-hoc).
- Ancla anterior, la de la partición por imagen, con la fuga: no se describe (R2).
- Taxonomía de errores, repetición y análisis por clase del ruteo: Cap. 5. La taxonomía del nivel diferencial (`ok_diferencial`) es un criterio de evaluación, no del método.
- Pruebas estadísticas pareadas: 3.3 (`sec:met_estadistica`). Ablación de diagnóstico sustituido (`make_wrong_dx.py`): no hay hoy un lugar en 3.8 (ver «Quitado»).
- El kNN como clasificador, su *linear probe* y su SVM: 3.5. Swin-Tiny y su entrenamiento: 3.4.
- Definiciones de predicción selectiva, concordancia, calibración y *grounding* general: Cap. 2 (solo `\ref`).
- Costo computacional de la cascada: 3.8.

## Preguntas abiertas para el autor

1. **(resuelta)** Motivación con resultados. P1 remite a `cp:res_clasif` sin cifras y cita el *hedging* del Cap. 2.
2. **(resuelta)** Justificación de la softmax. Opción (b): P9 justifica por diseño (decisiones sin calibración ni umbral) y no hace afirmación empírica sobre la softmax. La calibración corregida y la regla con umbral siguen sin medirse; si se quiere defender con datos, va al Cap. 4.
3. **(resuelta)** Señal elegida con el test a la vista. Se declara una sola vez, en 3.3 (`sec:met_seleccion`); P9 solo remite (D-C).
4. **(resuelta)** Selección de la variante *noreasoning*. P4 la declara en una oración (piloto de 100 imágenes, 17 de prueba) y remite a 3.3 (D-C). Queda por confirmar la cifra de 17 contra `ensamble_resul_20260607.md`.
5. **(resuelta)** Plantilla diferencial. P10 la describe tal cual («atribuye la incertidumbre al clasificador») sin cambiar corridas ya generadas; el texto completo va al Apéndice B.
6. **(resuelta)** Voto kNN en abstención. P7 lo explica (el voto cae en el vecino más cercano).
7. **Script de RAG desactualizado.** `Codigo/scripts/build_rag_index.py` hardcodea `ham10000_splits.json` (partición por imagen). El índice por lesión sale de `dermlip_split_eval.py`, que es el que se cita. Cambio de código, no de tesina; sigue abierta.
8. **(obsoleta tras la revisión del 18/10)** Ancla anterior (partición por imagen). Con R2 no se describe en el Cap. 3; su declaración, si hace falta, va al Cap. 5.
9. **(resuelta)** La recuperación no entra en la cascada del ruteo: Swin + recuperación es un brazo de comparación (P8).
10. **(resuelta)** La línea base sin generador se define en 3.7 (P12). 3.3 solo la anuncia (`sec:met_lineas_base`), como pedía la revisión cruzada.
11. **(obsoleta tras la revisión del 18/10)** Frase «el test de la misma fuente no alcanza» del hilo del capítulo. La transición de 3.7 a 3.8 es ahora «falta ver cómo se evalúa fuera de las condiciones en que se entrenó», y las pruebas pareadas están en 3.3.
12. **(resuelta)** Título «Pipeline propuesto» y tercera subsección «Ruteo por concordancia en tres niveles».
13. **(resuelta)** Independencia. P9 dice «sesgos distintos» y «se espera que sus errores no coincidan siempre»; no afirma independencia ni que Derm1M excluya HAM10000 (3.2 lo trata aparte).
14. **Nodo de derivación.** El texto dice «no se genera reporte y el caso se deriva a un especialista» y el Apéndice B no lleva plantilla para ese nivel; sigue abierto solo si el Apéndice B incluye un mensaje de derivación.
15. **(resuelta)** Melanoma (T2): P1 dice que queda fuera porque el ruteo no emite decisión binaria.
16. **Decodificación.** P6 remite a la decodificación de 3.6 sin valores. Verificar que 3.6 fije `--max_tokens 384 --seed 42` y sin `repetition_penalty` para la corrida de RAG (`Codigo/docs/ideas/rag_les_plan_20261003.md`); sigue abierta.
17. **(obsoleta)** Bibliografía. 3.7 solo cita `cover1967nearest` y `tschandl2018ham10000`; `abdin2024phi3` y `zeng2025mmskin` están en el `.bib` y los usan 3.5 y 3.6.

## Decisiones tomadas por cuenta propia

1. **Estructura.** Una introducción de tres párrafos (limitaciones y propuesta, cascada, recuperación como segundo predictor) y tres subsecciones (cascada, recuperación, ruteo). La cascada sin recuperación no tiene subsección propia: se describe dentro de 3.7.1.
2. **Definición de la cascada.** La noción general de *grounding* está en el Cap. 2; 3.7 la nombra y define solo la cascada concreta y la variante *noreasoning*.
3. **Fórmula de la regla.** Se define con su ecuación (`eq:met_politica_ruteo`, P10), con a(x) y κ(x) del Cap. 2.
4. **Lista de niveles.** Los tres niveles son alternativas paralelas y excluyentes: `enumerate` con el nombre en cursiva (guía §3). Los pasos de la cascada, secuenciales, van en prosa.
5. **Abstención sin generación.** Se mantiene lo que hace el código (`reanclaje_cascada_resul_20261003.md` §2).
6. **Dos figuras, dos archivos.** `pipeline.tex` y `ruteo.tex`, uno por diagrama (guía §7).
7. **Sin números de resultado.** Los únicos números son de configuración o de datos: k = 3, semilla 42, 100 imágenes del piloto (17 de prueba) y 6 447 imágenes del índice.
8. **Descripción corregida del ruteo** (revisión del 03/10): acuerdo Swin–kNN, no confianza calibrada ni umbral τ; el diferencial presenta {clasificador, kNN}, no el top-2.
9. **Forward references.** Las limitaciones de P1 remiten al Cap. 4 sin cifras; las referencias propias de P12 remiten a 3.3; la transición a 3.8 va sin `\ref`.
10. **Cierre.** P12 cierra con la línea base sin generador, el enlace a las líneas base y las pruebas de 3.3, y una oración que instala 3.8 como pregunta pendiente (R5).

## Quitado en la revisión del 18/10/2026

- **Fecha de la elección de *noreasoning* («en junio»)** y la referencia a que se eligió «mirando el test»: R1 (fechas de decisiones). El `.tex` no las menciona.
- **Detalle del piloto de *noreasoning* (desglose por partición, variantes `soft`, `dxfirst`, `conclude`, `confirmed`, medición sobre el *oracle*):** R1/R2 y D-C. En 3.7.1 queda una oración (100 imágenes de HAM10000, 17 de prueba); la declaración de que esas 17 son de prueba está en 3.3 (`sec:met_seleccion`). El detalle, si se conserva, va al Cap. 4 o al Apéndice C.
- **Declaración de la concordancia elegida con cifras de prueba («en julio»):** D-C. Se declara una sola vez, en 3.3 (`sec:met_seleccion`); P9 solo remite.
- **Origen histórico del cambio de señal (pivote desde la confianza de la softmax, plan del 25/07):** R1/R2. No va en el Cap. 3; P9 justifica la concordancia por diseño.
- **Parámetros finos de decodificación de la corrida RAG (`--max_tokens 384 --seed 42`, sin `repetition_penalty`):** R3. P6 remite a la decodificación de 3.6.
- **Tamaño de la prueba (1503) en el índice de recuperación:** R3. Ya lo presenta 3.2; P7 conserva solo las 6 447 imágenes del índice.
- **Transición a la antigua 3.9 («La Sección `sec:met_complementarios` describe las pruebas con que se analiza esa diferencia»):** D-A. Las pruebas pasaron a 3.3 (`sec:met_estadistica`); la transición ahora es a 3.8 y plantea la pregunta de la evaluación fuera de las condiciones de entrenamiento.
- **Ablación de diagnóstico sustituido por una clase confundible (`make_wrong_dx.py`), que la ficha anterior proponía listar en 3.9:** D-A. 3.8 no la incluye; queda sin lugar en el Cap. 3 (decisión del autor si se conserva).
- **Mención del ancla anterior (partición por imagen) y de RAG/`full_uncertainty` declarados sobre la partición anterior:** R2. No se describe la configuración vieja.
