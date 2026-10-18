# Ficha 3.8 — Pipeline propuesto

**Revisión del autor (18/10/2026), ya aplicada en el `.tex`:** Ahora es 3.7. Se presenta como la propuesta central; sin fechas; el piloto de noreasoning en una oración y la declaración de la concordancia remitida a 3.3; cierre que enlaza con las líneas base de 3.3 y con 3.8.

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/08-pipeline.tex` (sale de `06-pipeline.tex`, que hoy tiene solo tres `\pendiente`). Labels: `sec:met_pipeline` (sección); `sec:met_cascada`, `sec:met_recuperacion`, `sec:met_ruteo` (subsecciones, nombres propuestos; ninguno lo referencia todavía). Figuras: `fig:met_pipeline`, `fig:met_ruteo`. Ecuación: `eq:met_politica_ruteo`.

## Hilo conductor

Pregunta que responde la sección: ¿cómo se encadenan el clasificador, la recuperación y el generador en un único sistema, y qué regla decide si el reporte afirma un diagnóstico, enuncia candidatos o deriva el caso?

Viene de: 3.7 deja los generadores (Mini-VLM, LLaVA-Med y SkinVL-MM) ajustados con LoRA y la separación entre reporte y razonamiento (`sec:met_generacion`). **3.7 todavía no tiene ficha**: lo que se toma de ella es lo que el hilo del capítulo (`fichas/03-materiales-metodos/00-capitulo.md`) le asigna, «un generador que no discrimina necesita que el diagnóstico venga de afuera». De 3.5 y 3.6 toma los clasificadores supervisados (Swin-Tiny) y el kNN sobre embeddings de DermLIP, que 3.6 presenta como uno de los modos de DermLIP. Verificar cuando 3.7 se apruebe.

Deja instalado: (a) las tres salidas del sistema (reporte definitivo, reporte diferencial, derivación) con su regla de decisión, que 3.9 usa para los análisis por nivel; (b) la línea base sin generador, que es la comparación que aísla lo que aporta el generador; (c) la cascada anclada a tres fuentes de diagnóstico (Swin-Tiny, DermLIP y *oracle*) más el caso sin anclaje, que los Caps. 4 y 5 comparan. Además, la comparación de la cascada con el *grounding* simple y con la línea base sin generador comparte el mismo clasificador, y eso es lo que 3.9 tiene que sostener con pruebas pareadas.

```
Intro (sin subsección)
P1  Un VLM generativo tiene dos limitaciones que el trabajo evalúa por separado: como clasificador no
    discrimina bien las lesiones (Sección~\ref{sec:met_clasif_vlm}), y al redactar no se compromete con un
    diagnóstico sino que hedea (Sección~\ref{sec:marco_rep_fallas}). Por eso se separan las tareas: un
    clasificador decide el diagnóstico y el generador redacta el reporte                 justifica
    ↓ necesidad — si el generador no decide, el diagnóstico tiene que venir de otra fuente, y esa fuente
      tiene que discriminar
P2  La cascada: el clasificador entrega una clase, que se inyecta en el prompt junto con la imagen, y el
    generador redacta un reporte que la afirma (*grounding*, Sección~\ref{sec:marco_rep_generacion}).
    Su costo es que el reporte hereda el error del clasificador. Su límite es que una sola clase no dice
    cuándo el clasificador duda. Figura~\ref{fig:met_pipeline}                            describe · limita
    ↓ contraste — un segundo predictor, con otros datos y otro sesgo, permite saber si el primero duda
P3  Ese segundo predictor es un kNN sobre embeddings de DermLIP, que recupera los casos de entrenamiento
    más parecidos. Sus vecinos cumplen dos funciones: son evidencia textual para el generador y son una
    señal de concordancia con el clasificador (Sección~\ref{sec:marco_concordancia})     define · justifica
    ↓ ampliación — la recuperación se usa de dos maneras, como contexto del prompt y como regla de ruteo

3.8.1 Cascada clasificador–generador (*grounding*) (sec:met_cascada)
P4  La instrucción: el prompt contiene el diagnóstico y la plantilla *noreasoning* pide solo el reporte
    final, prohíbe el razonamiento y los diferenciales. Motivo: el generador tiende a razonar en voz alta y
    a contradecir el diagnóstico que recibe, y prohibirlo explícitamente lo obliga a comprometerse.
    Se define acá la variante; la instrucción como parte de la configuración, en Cap. 2              justifica
    ↓ necesidad — falta decir qué diagnósticos entran en la cascada
P5  Cuatro fuentes del diagnóstico: Swin-Tiny (ancla principal, partición por lesión); DermLIP
    zero-shot (alternativa sin entrenamiento sobre HAM); *oracle* (diagnóstico verdadero, cota superior,
    no usable en la práctica); y sin anclaje (el generador sin diagnóstico, línea base de Sección~\ref{sec:met_protocolo}).   describe
    ↓ consecuencia — el generador es el mismo en las cuatro fuentes: solo cambia el diagnóstico que recibe
P6  Los generadores son los de la Sección~\ref{sec:met_generacion}, con sus pesos ajustados y sin
    reentrenar para la cascada: el *grounding* es solo de inferencia. Decodificación según 3.7. Los
    reportes se evalúan sin el bloque de razonamiento (métrica de Sección~\ref{sec:met_protocolo})    describe · limita

3.8.2 *Grounding* por recuperación (sec:met_recuperacion)
P7  El kNN: embeddings de DermLIP normalizados, coseno, k = 3, voto mayoritario, y empate a favor del
    vecino más similar. El índice contiene solo imágenes de entrenamiento de la partición por lesión
    (Sección~\ref{sec:met_particiones}): ni imágenes ni lesiones de test. Por qué por lesión: si una foto
    de test tiene como vecina otra foto de su misma lesión, el voto mide memoria y no generalización
    (la fuga se define en Sección~\ref{sec:marco_regularizacion}). Se retoma el kNN de Sección~\ref{sec:met_clasif_vlm}     define · justifica
    ↓ necesidad — los vecinos tienen que entrar al prompt como texto
P8  El contexto es una frase fija con los diagnósticos de los tres vecinos y, si el metadato lo trae, su
    localización. Hay dos plantillas: la de recuperación sola (sin clasificador; pide el diagnóstico) y
    Swin + recuperación (el diagnóstico del ancla y el contexto, sin diferenciales). Esta última cambia
    la plantilla *noreasoning*: por eso es un brazo de comparación y no parte de la cascada del ruteo
    (ver pregunta 9)                                                                       describe
    ↓ contraste — hasta acá la recuperación es evidencia; el ruteo la usa además como segundo predictor

3.8.3 Ruteo por concordancia en tres niveles (sec:met_ruteo)
P9  La regla usa las decisiones de dos predictores y no sus probabilidades: la concordancia no necesita
    calibración ni umbral que ajustar. Antes de adoptarla se probó la confianza de la softmax, que
    no dio una relación monótona con la exactitud (ver pregunta 2). Los dos predictores tienen sesgos
    distintos: uno ajusta fronteras de decisión sobre HAM10000 y el otro no es paramétrico sobre una
    representación preentrenada                                                          justifica
    ↓ necesidad — con esa señal, hace falta una regla que asigne cada caso a un nivel
P10 Con a(x) = 1 si el clasificador y el kNN coinciden, y κ(x) el consenso de los vecinos
    (Ecuación~\ref{eq:marco_knn}), con k = 3 el consenso vale 1/3, 2/3 o 1. Los tres niveles son:
    \begin{enumerate}
      \item \textbf{Afirmativo} (a = 1): reporte definitivo con el diagnóstico del clasificador, con la
            plantilla *noreasoning*.
      \item \textbf{Diferencial} (a = 0 y κ > 1/3): reporte que enuncia el par {clasificador, kNN} con la
            plantilla diferencial.
      \item \textbf{Abstención} (a = 0 y κ = 1/3, los tres vecinos de clases distintas): no se genera
            reporte y el caso se deriva a un especialista.
    \end{enumerate}
    Las plantillas van en el Apéndice B. Se formaliza en la ecuación `eq:met_politica_ruteo` (define)
    ↓ interpretación — con una señal discreta no hay umbral que ajustar, y los tres niveles particionan
      todos los casos
P11 Es la política de tres salidas de Sección~\ref{sec:marco_tres_salidas}, con la concordancia en lugar de
    la confianza: la abstención es una predicción selectiva (Sección~\ref{sec:marco_pred_selectiva}) y el
    diferencial presenta como candidatos el diagnóstico del clasificador y el voto del kNN, no los dos
    primeros del clasificador. Un caso con a = 0 y consenso parcial del kNN también cae en diferencial
    (interpreta)
    ↓ necesidad — la regla dice qué sale; falta qué sale sin generador para medir cuánto aporta el generador
P12 Línea base sin generador: el mismo ruteo, sin redactar. El nivel afirmativo escribe el diagnóstico del
    clasificador, el diferencial escribe el par y la abstención queda igual. Compara el sistema con lo
    que se obtiene solo con el ruteo (define)
    → Transición a 3.9: «La cascada se compara con líneas base que usan el mismo clasificador. La
      Sección~\ref{sec:met_complementarios} describe las pruebas con que se analiza esa diferencia.»
```

Figuras de la sección: `fig:met_pipeline` (pipeline completo, P2) y `fig:met_ruteo` (ruteo en tres niveles, P10).

Se definen acá (y no se vuelven a definir): la cascada como arquitectura y la variante *noreasoning* (la noción general de *grounding* es de Sección~\ref{sec:marco_rep_generacion}); la construcción del contexto de recuperación con sus dos plantillas; el kNN usado como índice (su definición como clasificador está en 3.6); la regla de tres niveles con su ecuación; la línea base sin generador.
Se retoman de antes (solo se nombran, con `\ref`): *grounding* y la instrucción del generador (`sec:marco_rep_generacion`); *hedging* y fallas del texto (`sec:marco_rep_fallas`); recuperación de imágenes y RAG (`sec:marco_recuperacion_imagenes`, `sec:marco_rag`); concordancia y consenso (`sec:marco_concordancia`, `eq:marco_knn`); las tres salidas y la predicción selectiva (`sec:marco_tres_salidas`, `sec:marco_pred_selectiva`); confianza y calibración (`sec:marco_senales_confianza`); integración de los mecanismos (`sec:marco_integracion`). De 3.3, 3.4, 3.5, 3.6 y 3.7: partición por lesión, métrica y línea base de referencia, Swin-Tiny, DermLIP, los tres generadores y su decodificación.
Remisiones hacia adelante: pruebas pareadas y análisis complementarios (3.9); métrica oficial de consistencia (3.4).
Extensión: 12 párrafos, dos figuras y una lista de tres ítems; unas 3.5 páginas (orientativo del capítulo).

## Subsecciones

Tres, las del andamiaje, con dos cambios de título:
- «Cascada clasificador–generador (*grounding*)» (P4–P6): se mantiene.
- «*Grounding* por recuperación» (P7–P8): se mantiene.
- «Ruteo por incertidumbre en tres niveles» pasa a «Ruteo por concordancia en tres niveles» (P9–P12): la señal es la concordancia de Sección~\ref{sec:marco_concordancia}, no una incertidumbre calibrada (pregunta 12).
La sección no tiene título largo: «Pipeline propuesto» (ver pregunta 12).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Dos limitaciones de los VLM (clasificador que no discrimina; generador que hedea) y la decisión de separar las tareas. Primera oración: «Un VLM generativo tiene dos limitaciones que el trabajo evalúa por separado.» Forward ref a Cap. 4 sin cifras (pregunta 1). | Limitaciones: `Chapters/02-Marco-Teorico/07-generacion-reportes.tex` (`sec:marco_rep_fallas`). Discriminación: 3.6 y Cap. 4. | ninguna nueva |
| P2 | Cascada: el clasificador entrega una clase, que va en el prompt con la imagen; costo (hereda errores) y límite (una clase no expresa duda). | `Docs/experimentacion/experimentacion.tex`, `fig:cascada` (sin cifras; ver figuras). Costo y límite: `07-generacion-reportes.tex` (`sec:marco_rep_generacion`). | ninguna nueva |
| P3 | El kNN de DermLIP como segundo predictor; dos funciones: evidencia textual y señal de concordancia. | `Chapters/02-Marco-Teorico/05-vlm.tex` (`eq:marco_vecinos`, `eq:marco_knn`). | `cover1967nearest` (kNN; Cap. 2 ya lo cita) |
| P4 | Plantilla *noreasoning*: texto fijo con el diagnóstico; prohíbe razonamiento y diferenciales. Motivo: razonamiento en voz alta y contradicción del diagnóstico. La medición de la variante no va acá. | Plantilla: `Codigo/scripts/generate_report.py` líneas 142–147 (`GROUNDED_TEMPLATES["noreasoning"]`). Uso en la cascada: líneas 477–484. Motivo: `Codigo/docs/ideas/ensamble_clasificador_generador_plan_20260605.md` §9.2 y §9.5 (texto de decisión, sin cifras). | ninguna nueva |
| P5 | Cuatro fuentes: Swin-Tiny (ancla por lesión, semilla 42); DermLIP zero-shot; *oracle*; sin anclaje. | Ancla: `Codigo/docs/resul/revision_experimentacion_20261003.md` §1 («`full_dx_swin_les.csv` = argmax de Swin semilla 42»); generación con `Codigo/scripts/make_dx_csv.py` (corrida `swin_tiny_sweep_t06_les_cwnone`, `Codigo/docs/ejecuciones.md` línea 243; verificar contra 3.5). DermLIP zero-shot: `Codigo/scripts/dermlip_split_eval.py` (encabezado: el zero-shot no depende de la partición). *Oracle*: gt de `Codigo/outputs/full_dx_oracle.csv` (`build_uncertainty_3tier.py`, valor por defecto). | `sec:met_clasif_vlm`, `sec:met_supervisados` (remisiones) |
| P6 | Generadores de 3.7 sin reentrenar para la cascada (solo inferencia); decodificación de 3.7; reporte sin razonamiento. | Decisión: `Codigo/docs/ideas/ensamble_clasificador_generador_plan_20260605.md` §2.2 («el grounding es solo de inferencia»). Reporte sin razonamiento: `Codigo/docs/resul/revision_experimentacion_20261003.md` §2.2 (decisión «reporte, no razonamiento» en 3.4). | `li2023llavamed` (solo si 3.7 no lo cita antes) |
| P7 | kNN: DermLIP ViT-B/16 normalizado, coseno, k = 3, voto, empate al más similar; índice de train de la partición por lesión; motivo de la fuga por foto de la misma lesión. | `Codigo/scripts/dermlip_split_eval.py` líneas 100–111 (kNN, empate, texto del contexto). Índice por lesión: mismo archivo, sección `lesion` (genera `Codigo/outputs/rag/rag_context_les.csv`). Tamaño del train de la partición por lesión: `M\Codigo\outputs\results\dermlip\dermlip_split_eval.json`, clave `lesion.n_train` = 6447 (verificar contra 3.3). Test = 1503. Partición: `Codigo/scripts/make_lesion_disjoint_split.py`. Vecinos de un mismo `lesion_id`: `make_lesion_disjoint_split.py` encabezado. | `cover1967nearest`, `tschandl2018ham10000` (HAM10000, si 3.3 no lo cita antes) |
| P8 | Frase del contexto con diagnósticos y localización; plantilla de recuperación sola (`RAG_TEMPLATE`) y de Swin + recuperación (`GROUNDED_RAG_TEMPLATE`). | `Codigo/scripts/generate_report.py` líneas 150–163 (plantillas), 495–501 (cuál se usa). Formato del contexto: `dermlip_split_eval.py` línea 111. Decodificación de la corrida RAG: `--max_tokens 384 --seed 42`, sin `repetition_penalty` (`Codigo/docs/ideas/rag_les_plan_20261003.md`, Diseño). | `lewis2020retrievalaugmented` solo si hace falta; si no, `\ref{sec:marco_rag}` |
| P9 | Por qué concordancia y no softmax: decisiones y no probabilidades; sin umbral; sesgos distintos; primera medición de la softmax no monótona (sin cifras). | `Codigo/docs/ideas/incertidumbre_p54_plan_20260725.md` §«Pivote de señal» (origen del cambio; ver pregunta 2). `Codigo/scripts/build_uncertainty_agreement.py` encabezado (regla de acuerdo). Calibración: `Codigo/scripts/temperature_scaling.py`. | `geifman2017selective`, `elyaniv2010foundations` (solo `\ref`, Cap. 2); `guo2017calibration` opcional |
| P10 | Ecuación de la política y los tres niveles en lista. Los valores de κ con k = 3. | `Codigo/scripts/build_uncertainty_3tier.py` líneas 69–76 (reglas exactas: `s == k` → afirmativo; `n_distinct >= 3` → abstención; resto → diferencial). Candidatos del diferencial: `f"{s}; {k}"` (línea 76). Plantillas: `generate_report.py` línea 167 (`DIFFERENTIAL_TEMPLATE`). Abstención: no se genera (`Codigo/docs/resul/reanclaje_cascada_resul_20261003.md` §2, el diferencial es el único que se genera). | `eq:marco_knn`, `eq:marco_politica` (`\ref`) |
| P11 | Relación con las tres salidas de Cap. 2; abstención como predicción selectiva; el diferencial no es el top-2 del clasificador. | `Codigo/docs/resul/revision_experimentacion_20261003.md` §2.1 (el diferencial recibe {top-1 de Swin, voto kNN}, no el top-2). | `\ref{sec:marco_tres_salidas}`, `\ref{sec:marco_pred_selectiva}` |
| P12 | Línea base sin generador: escribe diagnóstico o par, sin redactar. | `Codigo/scripts/ensemble_bootstrap.py` líneas 209–215 (`mech`, `mech_d`). | ninguna |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `fig:met_pipeline` (`Figures/Capitulos/03-Materiales-Metodos/pipeline.tex`, carpeta nueva) | Imagen → clasificador (Swin-Tiny o DermLIP) → diagnóstico; imagen → kNN sobre el índice de train → contexto; concordancia → ruteo → generador (*noreasoning*) → reporte; abstención → derivación. Sin cifras. | `experimentacion.tex` `fig:cascada` (no tiene cifras; quitar «Noreasoning: variante...» del epígrafe y pasarla al texto). Base de `Figures/Capitulos/02-Marco-Teorico/mapa-capitulo.tex`, que dice «versión simplificada del diagrama de `sec:met_pipeline`»: si uno cambia, revisar el otro. | a adaptar (TikZ con `13-Figuras.sty`, rama del kNN nueva) |
| `fig:met_ruteo` (`Figures/Capitulos/03-Materiales-Metodos/ruteo.tex`) | Tres niveles con su condición en la flecha: coinciden (afirmativo); desacuerdo con vecinos no todos distintos (diferencial); desacuerdo con tres vecinos distintos (abstención). Sin cifras. | `experimentacion.tex` `fig:incertidumbre`: quitar los porcentajes (74, 22, 4 %), las coberturas y el 93.4 %. Corregir la etiqueta «consenso parcial», que cubre también el caso de un consenso unánime del kNN distinto del clasificador (ver P10). | a adaptar |
| Lista de tres niveles | Los tres niveles con su acción | Texto de P10 | en el cuerpo (`enumerate`) |

No hay tablas nuevas. Los estilos de `13-Figuras.sty` alcanzan (`figentrada`, `figtarea`, `figsalida`, `figgrupo`, `figflecha`, `figetiqueta`). Ver pregunta 14 sobre el nodo de derivación.

## Prosa ya escrita que se conserva

Ninguna. `06-pipeline.tex` tiene solo tres `\pendiente`. Se reutilizan los títulos de subsección (con el cambio de la tercera), y el `\pendiente` del diagrama se reemplaza por la figura.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`, hoy con `\pendiente`):** texto completo de las plantillas que usa la sección: la de *noreasoning* (`GROUNDED_TEMPLATES["noreasoning"]`), la de recuperación sola (`RAG_TEMPLATE`), la de Swin + recuperación (`GROUNDED_RAG_TEMPLATE`), la diferencial (`DIFFERENTIAL_TEMPLATE`) y la baseline (`REPORT_PROMPT`). Las variantes `soft`, `dxfirst`, `conclude` y `confirmed` se listan como descartadas, sin resultados (ver pregunta 4). Para la abstención no hay plantilla.
- **Apéndice E (`ap:reproducibilidad`):** los scripts del ruteo y del índice (`build_uncertainty_3tier.py`, `dermlip_split_eval.py`, `make_dx_csv.py`), con sus parámetros.

## Lo que NO va en esta sección (y dónde está)

- Tamaños de los niveles (cuántos casos caen en cada uno) y cobertura del diagnóstico verdadero por nivel: Cap. 4 (clasificación y ruteo) y Cap. 5 (cascada). En esta sección no aparece ningún número de resultado.
- Consistencia diagnóstica de la cascada y de la línea base, diferencias con su intervalo: Cap. 5. La métrica en sí (solo reporte y matcher estricto) va a 3.4.
- Medición de la variante *noreasoning* y de las otras variantes del prompt sobre el *oracle*: Cap. 4 o Apéndice C (`C-Resultados-Complementarios`).
- Resultados de RAG (la corrida por lesión no tiene resultado registrado todavía, `Codigo/docs/ejecuciones.md`): Cap. 5.
- Calibración de la softmax (ECE, temperatura): Cap. 4 (calibración) y 3.9 (calibración post-hoc).
- Ancla anterior, la de la partición por imagen, con la fuga: no se describe acá. Su declaración va a Cap. 5 o 3.9 (ver pregunta 8).
- Taxonomía de errores, repetición y análisis por clase del ruteo: Cap. 5 y 3.9. La taxonomía del nivel diferencial (`ok_diferencial`) es un criterio de evaluación, no del método.
- Ablación de diagnóstico sustituido por una clase confundible (`make_wrong_dx.py`): 3.9 (análisis complementarios). Propongo que 3.9 la liste como ablación.
- El kNN como clasificador, su *linear probe* y su SVM: 3.6. Swin-Tiny y su entrenamiento: 3.5.
- Definiciones de predicción selectiva, concordancia, calibración y *grounding* general: Cap. 2 (solo `\ref`).
- Costo computacional de la cascada: 3.9.

## Preguntas abiertas para el autor

1. **Motivación con resultados.** P1 dice que los VLM no discriminan y que el generador hedea. Ambas afirmaciones son resultados que se muestran en el Cap. 4, y el capítulo no presenta resultados. Propongo una oración con forward ref a Cap. 4, sin cifras, y la cita de Cap. 2 para el hedging. ¿Se acepta?
2. **Justificación de la softmax (la más delicada).** La no monotonía que motivó el pivote (plan del 25/07, §«Pivote de señal») se midió con una calibración con temperatura T = 0.53. La revisión del 03/10 (§2.6) dice que esa calibración tenía un error, y que con la corregida el resultado no se volvió a medir; la segunda auditoría dio una estimación de una regla con umbral sobre la softmax, sin verificar. Opciones: (a) volver a medir la regla con umbral con la calibración corregida y reportarla en Cap. 4 o 3.9; (b) justificar en 3.8 solo por diseño (decisiones sin calibración ni umbral) y quitar la afirmación empírica de P9. **Propongo (b) y, si se quiere defender la elección con datos, (a).**
3. **Señal elegida con el test a la vista.** El plan del 25/07 (§1) decidió la concordancia mirando cifras de test. La validación confirmó solo las proporciones de los niveles (revisión §2.6, «atenuante»), no la cobertura. ¿Se declara en 3.8, en 3.9 (limitaciones) o en Cap. 5? Propongo una frase en 3.9.
4. **Selección de la variante *noreasoning*.** Se eligió en junio entre variantes medidas sobre 100 imágenes de HAM10000 con el *oracle* (`Codigo/docs/resul/ensamble_resul_20260607.md`, §1–3). El documento no dice de qué partición son esas 100 imágenes, y en ese momento la partición era por imagen. Si son de test, la elección se hizo sobre test y hay que declararlo en 3.8 o 3.4. Verificar antes de redactar P4.
5. **Plantilla diferencial.** `DIFFERENTIAL_TEMPLATE` dice «The classifier is uncertain…» y lista candidatos que vienen de dos fuentes (el clasificador y el kNN). El texto es inexacto para el caso del kNN. Propongo describirla tal cual en el Apéndice B y declararlo, sin cambiar corridas ya generadas.
6. **Voto kNN en abstención.** Con tres vecinos de clases distintas, el «voto» es el dx del vecino más cercano (`Counter.most_common` desempata por orden de similitud, `dermlip_split_eval.py` línea 107). Ese dx es el «kNN» de la cobertura de abstención. Propongo describirlo así en P7 y explicarlo en 3.9 donde aparezca la cobertura.
7. **Script de RAG desactualizado.** `Codigo/scripts/build_rag_index.py` hardcodea `ham10000_splits.json` (partición por imagen): reproduce el índice con fuga. El índice por lesión sale de `dermlip_split_eval.py`. En la sección se cita `dermlip_split_eval.py`. ¿Se corrige `build_rag_index.py` (por ejemplo, con `--splits_file`)? Es un cambio de código, no de tesina.
8. **Ancla anterior.** Hace falta decidir dónde se declara que el ancla anterior (partición por imagen) tenía fuga y que los brazos RAG y de incertidumbre sobre ella son anteriores: Cap. 5 o 3.9. La ficha de Cap. 3 (`00-capitulo.md`, alcance 6) dice que RAG está «declarado sobre la partición anterior»; si la corrida por lesión (job 1179315) termina, ese punto queda desactualizado y hay que cambiarlo en la ficha del capítulo.
9. **¿Entra la recuperación en la cascada del ruteo?** `generate_report.py` cambia la plantilla cuando hay contexto RAG (líneas 495–498). Swin + recuperación, por lo tanto, no usa *noreasoning*. Propongo que la cascada del ruteo no lleve contexto RAG, y que Swin + recuperación sea un brazo de comparación (P8). ¿Se confirma?
10. **Dónde se define la línea base sin generador.** La ficha de 3.4 la lista entre sus líneas base. Propongo definirla en 3.8 (es el mecanismo del ruteo) y que 3.4 solo la nombre con `\ref`. Hay que cambiar la fila de «Dónde se define» de `00-capitulo.md` para que coincida.
11. **Frase del hilo del capítulo.** El hilo dice que 3.8 necesita «el test de la misma fuente no alcanza para sostener un resultado (Sección 2.6)». Interpreto que la comparación entre la cascada y el *grounding* simple comparte el clasificador, y que por eso hacen falta análisis complementarios (3.9). Confirmar la intención, y el label de la «Sección 2.6» (`sec:marco_evaluacion`, si corresponde).
12. **Título de la sección.** Propongo «Pipeline propuesto», sin «ensamble» ni «consciente de la incertidumbre»: la señal es concordancia (Cap. 2, `sec:marco_concordancia`), no una incertidumbre calibrada, y la guía §4 reserva «*pipeline*» para la arquitectura completa. Confirmar.
13. **Afirmaciones sobre independencia.** La justificación del ruteo usa «sesgos distintos». Que los errores sean independientes no está medido, así que no se escribe como hecho. Además, DermLIP se preentrenó sobre Derm1M, y la revisión (§2.8) no pudo verificar que Derm1M no contenga imágenes de HAM10000. En la sección no se escribe que Derm1M excluye HAM10000.
14. **Nodo de derivación.** El nivel de abstención no tiene prompt ni texto. ¿El Apéndice B incluye un mensaje de derivación o solo la regla? Propongo solo la regla.
15. **Melanoma (T2).** El ruteo no emite una decisión binaria de melanoma. Propongo que 3.8 diga que la cascada sirve a T1 (diagnóstico) y T3 (reporte), y que T2 queda fuera de este pipeline. Confirmar.
16. **Decodificación.** El plan del 03/10 usa `--max_tokens 384 --seed 42` y sin `repetition_penalty`, porque en Mini-VLM ese parámetro no funciona. Verificar que 3.7 fija lo mismo.
17. **Bibliografía.** DermLIP se cita con `yan2025derm1miccv` (Derm1M, que presenta DermLIP; verificar). Mini-VLM se identifica como Phi-3.5-vision en el código de análisis, y su clave no está en el `.bib` (`abdin2024phi3` es el reporte de Phi-3). SkinVL tampoco tiene clave. Son referencias para 3.6 y 3.7; si hacen falta, van a `refs_pendientes.md`. 3.8 no cita ninguna de ellas.

## Decisiones tomadas por cuenta propia

1. **Estructura.** Una introducción de tres párrafos (limitaciones, cascada, recuperación) y tres subsecciones (cascada, recuperación, ruteo). La cascada sin recuperación no tiene subsección propia: se describe dentro de la 3.8.1.
2. **Definición de la cascada.** La noción general de *grounding* está en Cap. 2 (`sec:marco_rep_generacion`), así que 3.8 la nombra y define solo la cascada concreta y la variante *noreasoning*. «Cascada, *grounding*, *noreasoning*, ruteo en tres niveles → 3.8» de `00-capitulo.md` se lee con esa distinción.
3. **Fórmula de la regla.** La regla es un método del trabajo, así que se define con su fórmula (`eq:met_politica_ruteo`, en P10), con a(x) y κ(x) de Cap. 2.
4. **Lista de niveles.** Los tres niveles son alternativas paralelas, así que van en `enumerate` con el nombre en negrita, como indica la guía §3. Los pasos de la cascada son secuenciales y van en prosa, no en lista.
5. **Abstención sin generación.** Se mantiene lo que hace el código: el nivel de abstención no genera texto (`reanclaje_cascada_resul_20261003.md` §2). Consecuencia: el Apéndice B no tiene plantilla para ese nivel.
6. **Dos figuras, dos archivos.** Pipeline y ruteo van en `pipeline.tex` y `ruteo.tex`, uno por diagrama (guía §7). La carpeta `Figures/Capitulos/03-Materiales-Metodos/` no existe todavía y la crea el primer commit de esta sección.
7. **Sin números de resultado.** La sección no cita porcentajes ni cifras de desempeño. Los únicos números son de configuración o de datos (k = 3, semilla 42, tamaño del índice de train de la partición por lesión, 1503 test, 384 tokens), y cada uno tiene su fuente en la sección «Contenido por párrafo».
8. **Lectura de la revisión del 03/10.** Se usa la descripción corregida del ruteo (acuerdo Swin–kNN, no confianza calibrada ni umbral τ) y del RAG (índice por lesión; no se describe el índice anterior). El diferencial presenta {clasificador, kNN}, no el top-2 del clasificador.
9. **Título y subsecciones.** Se propone el título «Pipeline propuesto» y el cambio de la tercera subsección (pregunta 12); sin cambios de estructura respecto del andamiaje.
10. **Forward references.** Las limitaciones de P1 remiten al Cap. 4 sin cifras; las pruebas (3.9) y la métrica (3.4) se remiten con `\ref`.
11. **Redacción (aplicación de las propuestas de las preguntas abiertas).** Se aplicaron: P1 con referencia a `cp:res_clasif` sin cifras (pregunta 1); P9 sin la afirmación empírica sobre la softmax, solo el argumento de diseño (pregunta 2, opción b); declaración de la concordancia elegida con cifras de test en P9 (pregunta 3 y decisión transversal 1); la plantilla diferencial se describe tal cual en P10 (pregunta 5); el voto en abstención se explica en P7 (pregunta 6); la cascada del ruteo sin contexto RAG (pregunta 9); la línea base sin generador se define en P12 (pregunta 10); título «Pipeline propuesto» y subsección «Ruteo por concordancia en tres niveles» (pregunta 12); sin plantilla de abstención (pregunta 14); T2 queda fuera del pipeline y la cascada atiende T1 y T3 (pregunta 15, referido a las tareas de 3.1).
12. **Noreasoning sin declarar.** La ficha no confirma que la elección de *noreasoning* se hizo mirando el test (pregunta 4, «a verificar»). Queda un `\pendiente{}` en P4 y no se declara en el texto.
13. **Pendiente para el Apéndice B.** Las plantillas completas de cada nivel (*noreasoning*, diferencial, recuperación, Swin + recuperación, línea base) se publican en `Chapters/Apendices/B-Prompts.tex`, que hoy tiene solo `\pendiente{}`. Esta sección no lo toca.
14. **Figuras.** `Figures/Capitulos/03-Materiales-Metodos/pipeline.tex` y `ruteo.tex`, sin cifras. El `mapa-capitulo.tex` del Cap. 2 dice que es una versión simplificada del pipeline: el diagrama de 3.8 incluye el ruteo, así que la coherencia es solo de componentes.
