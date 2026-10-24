# Ficha 3.1 — Definición de las tareas y flujo de trabajo

**Revisión del tutor (21/10/2026), aplicada el 22/10:** Abre con «la propuesta de este trabajo se basa en integrar…» (comentario 5). El hardware pasa a 3.9; la restricción de cómputo queda como alcance (una sola GPU de hasta 24 GB, sin varias GPU ni GPU de última generación). El flujo cierra la sección con una oración por etapa y es el único lugar donde se describe el *pipeline* antes de 3.6. Figura `flujo_trabajo.tex` redibujada con el orden nuevo (datos → componentes → *pipeline* → evaluación). La introducción del capítulo (`00-capitulo.tex`) presenta primero la lógica metodológica y después la organización, en presente.

**Revisión del autor (20/10/2026):** «se juzga» → «se evalúa» (guía §3, verbos literales); sale de P de flujo la oración «Que el diagnóstico lo fije un clasificador… responde a un resultado», que repetía la apertura de 3.7; T3 reformulado para evitar una línea huérfana.

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Absorbe la antigua 3.2 (flujo de trabajo): definición formal de la tarea en el formato de la tesina de ejemplo, lista T1–T3 sin el detalle de PI/OE, «gradación» → «no tienen la misma gravedad», HAM10000 presentado con remisión a 3.2, GPUs en una oración (sin tabla, sin CUDA, sin W&B ni versionado), figura del flujo redibujada como etapas del método (sin historia de hipótesis ni ciclo de iteración). Título: «Definición de las tareas y flujo de trabajo».

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita el 18/10/2026 y ficha actualizada a esa versión.** Archivo: `Chapters/03-Materiales-Metodos/01-tareas.tex`. Figura: `Figures/Capitulos/03-Materiales-Metodos/flujo_trabajo.tex`. Labels: `sec:met_tareas`, `fig:met_flujo`. Los labels `sec:met_metodologia` y `sec:met_infra` de la antigua 3.2 ya no existen y nadie los referencia (verificado con `grep` sobre los `.tex`).

## Hilo conductor

Pregunta que responde la sección: ¿qué le pide el trabajo al sistema en su conjunto (entrada, salida, restricción de cómputo), cómo se reparte en tres tareas y en qué orden se recorre el método?
Viene de: la introducción del Cap. 3 y la propuesta del Cap. 2 (`sec:estado_arte_posicion`): un *pipeline* que encadena un clasificador, una recuperación de casos parecidos y un generador de reportes. La sección no abre con la tabla de brechas (`tab:marco_brechas`): retoma solo la propuesta.
Deja instalado: para 3.2, las siete categorías de *HAM10000* con su gravedad, la primera etapa del flujo (los datos: qué conjuntos, qué papel cumple cada uno, cómo se parte el que entrena a los clasificadores) y la restricción de una GPU de consumo. Para 3.3, que no todos los errores cuestan lo mismo (`sec:met_protocolo`). Para 3.4–3.7, las tres tareas con su entrada y salida (T1, T2, T3), la decisión de adaptar modelos preentrenados con LoRA y el orden de las etapas (Figura `fig:met_flujo`). Para 3.8, que el tercer objetivo específico no agrega una tarea: se aplica a clasificadores y *pipeline*.

```
(sin subsecciones: P1–P8; una cita en bloque, una lista de tres ítems y una figura)
P1  La propuesta del Cap. 2 encadena clasificador, recuperación y generador; antes de describir cada
    componente hay que fijar qué se le pide al sistema. Definición formal de la tarea, en una cita en
    bloque: imagen dermatoscópica → una de siete categorías, indicar si es melanoma, redactar un
    reporte que describa la lesión y afirme el diagnóstico, con modelos que corran en una GPU de
    consumo                                                                              función: define
    ↓ necesidad — la definición nombra «siete categorías»: hace falta decir cuáles son
P2  Las siete categorías son las de HAM10000 (`tschandl2018ham10000`, composición en
    `sec:met_datasets`): MEL, NV, BCC, AKIEC, BKL, DF y VASC; no tienen la misma gravedad (benignas:
    NV, BKL, DF, VASC; AKIEC: premalignas y carcinomas in situ; malignas: MEL y BCC). Por eso no todos
    los errores cuestan lo mismo, y eso decide las métricas (`sec:met_protocolo`)      función: define · justifica
    ↓ ampliación — con las categorías definidas, se desglosa la definición en las tareas que la componen
P3  Lista de tres ítems (alternativas paralelas): T1 clasificación (imagen → una de las siete
    categorías, con una probabilidad para cada una); T2 detección de melanoma (misma imagen → decisión
    binaria, derivada de la probabilidad de melanoma de T1; no localiza, dice qué es); T3 generación
    del reporte (imagen y diagnóstico del clasificador → texto con la descripción de la lesión y la
    impresión diagnóstica)                                                               función: define
    ↓ consecuencia — cada tarea responde una de las preguntas de investigación
P4  T1 y T2 responden la primera pregunta (si un VLM clasifica tan bien como un clasificador entrenado
    solo con imágenes) y T3 la segunda (si el reporte afirma el diagnóstico correcto);
    `sec:intro_objetivos`                                                                función: justifica
    ↓ limitación — T3 produce un texto: falta decir qué partes del reporte cubre y cuáles quedan fuera
P5  El reporte de T3 se limita a dos partes (descripción de lo que se ve e impresión diagnóstica),
    las que los conjuntos de pares imagen–texto anotan (`shen2025skincare`) y por lo tanto las que un
    modelo puede aprender. Quedan fuera el diagnóstico diferencial completo, la recomendación de manejo
    y las imágenes de histopatología                                                     función: limita
    ↓ necesidad — queda la última condición de la definición, una sola GPU de consumo
P6  La restricción de cómputo rige las decisiones de modelado: no se preentrena ningún modelo; los
    VLM se adaptan con LoRA (`sec:marco_llm_lora`, `hu2021lora`). Tres GPU: RTX 4070 de 12 GB (equipo
    personal), RTX 4080 de 16 GB (clúster TOKO, UNCuyo; clasificadores) y A30 de 24 GB (clúster
    Mendieta, UNC; ajuste de VLM y generación de reportes). Semilla 42 salvo indicación;
    `ap:reproducibilidad`                                                                función: justifica · describe
    ↓ necesidad — con tareas y restricción fijadas, falta el orden en que se recorre el método
P7  Flujo de trabajo (Figura `fig:met_flujo`): datos y partición por lesión y criterios de evaluación;
    clasificadores supervisados como referencia; clasificación con VLM; ajuste de VLM para generar
    reportes; *pipeline* (clasificador fija el diagnóstico, generador redacta, concordancia con los
    casos recuperados decide afirmar, ofrecer diagnóstico diferencial o derivar). Que el diagnóstico lo
    fije un clasificador responde a un resultado (los VLM generales no discriminan,
    `cp:res_clasif`). El tercer objetivo específico no agrega una tarea: se aplica a clasificadores y
    *pipeline* con los análisis de `sec:met_complementarios`                    función: describe · justifica
    ↓ necesidad — la primera etapa del flujo son los datos
P8  Cierre de una oración: la primera etapa son los datos (qué conjuntos, qué papel cumple cada uno,
    cómo se parte el que entrena a los clasificadores)                                  función: transición
→ Transición a 3.2: el propio P8 («La primera etapa del flujo son los datos: qué conjuntos se usan, qué
  papel cumple cada uno y cómo se parte el que entrena a los clasificadores.»)

Se definen acá (y no se vuelven a definir): la tarea del trabajo (definición formal) y T1, T2, T3 con su entrada y salida; las siete categorías de *HAM10000* y su gravedad; la detección de melanoma como binario derivado de T1 (no localización); las dos partes del reporte de T3 y lo que queda fuera (diagnóstico diferencial completo, manejo, histopatología); la restricción de una GPU de consumo y la decisión de no preentrenar y adaptar con LoRA; las tres GPU; el orden del flujo (Figura `fig:met_flujo`).
Se retoman de antes (solo se nombran, con \ref): PI1, PI2 y el tercer objetivo específico (`sec:intro_objetivos`); la propuesta (`sec:estado_arte_posicion`); LoRA (`sec:marco_llm_lora`); VLM (`\gls{vlm}`).
Remisiones hacia adelante: composición de HAM10000 (`sec:met_datasets`, 3.2); métricas y costos de confusión (`sec:met_protocolo`, 3.3); cada etapa del flujo en la Figura `fig:met_flujo` (3.2 `sec:met_datasets`, 3.3 `sec:met_protocolo`, 3.4 `sec:met_supervisados`, 3.5 `sec:met_clasif_vlm`, 3.6 `sec:met_generacion`, 3.7 `sec:met_pipeline`, 3.8 `sec:met_complementarios`); generación de reportes (`sec:met_generacion`); resultados de clasificación (`cp:res_clasif`); reproducibilidad (`ap:reproducibilidad`).
Extensión: ocho párrafos (con una cita en bloque, una lista y una figura), unas 2–2.5 páginas (el encabezado del `.tex` dice 2–2.5 p.).
```

## Subsecciones

Ninguna. La sección es un bloque, como la definición formal del ejemplo (pp. 37–38 del PDF de la tesina de ejemplo).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | La propuesta del Cap. 2 (clasificador, recuperación de casos parecidos, generador) y la definición formal de la tarea del trabajo en una cita en bloque en cursiva: clasificar en siete categorías, indicar si es melanoma, redactar un reporte que describa y afirme el diagnóstico, en una sola GPU de consumo. | Propuesta: `Chapters/02-Marco-Teorico/10-estado-arte.tex` (`sec:estado_arte_posicion`). Formato: tesina de ejemplo, §3.1. | ninguna |
| P2 | Las siete categorías son las de *HAM10000*; siglas con `\gls{}` (primera aparición en el documento); gravedad: benignas NV, BKL, DF, VASC; AKIEC reúne premalignas y carcinomas in situ; malignas MEL y BCC. Remisión a la composición (3.2) y a las métricas (3.3). | Siglas y nombres: `Matter/05-Acronyms.tex` líneas 22–28. Gravedad: prosa de la antigua `02-datos-particiones.tex` líneas 7–12, con la cita de Tschandl. | `tschandl2018ham10000` (`Bibliography.bib` línea 760) |
| P3 | Lista de tres ítems en cursiva. T1: entrada imagen, salida una de las siete categorías con una probabilidad para cada una. T2: misma imagen, salida binaria melanoma o no, obtenida de la probabilidad de melanoma de T1; no busca dónde está la lesión sino qué es. T3: entrada imagen y diagnóstico que propone el clasificador; salida texto que describe la lesión y enuncia la impresión diagnóstica. | T2 derivada y «no localización»: `Codigo/docs/ideas/cierre_experimentacion_plan_20260805.md` §1.8 (líneas 30–39) y §2 B1 (líneas 59–61). Entrada de T3 con el diagnóstico del clasificador: coincide con la cascada de 3.7 (`07-pipeline.tex`). | ninguna |
| P4 | T1 y T2 → primera pregunta de investigación (si un VLM clasifica tan bien como un clasificador entrenado solo con imágenes); T3 → segunda (si el reporte afirma el diagnóstico correcto). Sin OE por ítem. | PI1 y PI2: `Chapters/01-Introduccion/02-objetivos.tex` líneas 5–10. | ninguna |
| P5 | El reporte de T3 se limita a descripción e impresión diagnóstica: son las partes que los conjuntos de pares imagen–texto anotan junto a cada imagen y, por lo tanto, las que un modelo puede aprender. Fuera de alcance: diagnóstico diferencial completo, recomendación de manejo e histopatología. | Partes del reporte: texto del encabezado del `.tex` (`shen2025skincare`). Histopatología fuera: handoff del Cap. 1 (commit f520295); `Chapters/06-Discusion/07-limitaciones.tex` línea 15. | `shen2025skincare` |
| P6 | La restricción de una GPU rige el modelado: no se preentrena nada, los VLM se adaptan con LoRA (entrena una fracción pequeña de sus parámetros). Tres GPU: RTX 4070 de 12 GB, equipo personal; RTX 4080 de 16 GB, TOKO (UNCuyo), clasificadores; A30 de 24 GB, Mendieta (UNC), ajuste de VLM y generación. Semilla 42 salvo indicación. Apéndice E reúne lo necesario para repetir cada experimento. | Restricción: `Chapters/01-Introduccion/01-contexto-motivacion.tex` líneas 75–79. GPU y clústeres: `Codigo/CLAUDE.md` (según el encabezado del `.tex`); memoria del proyecto: TOKO es RTX 4080 de 16 GB. Semilla 42: afirmación del `.tex`; no verificada contra `Codigo/` al poner al día la ficha. Apéndice: `ap:reproducibilidad` (`Chapters/Apendices/E-Reproducibilidad.tex`). | `hu2021lora` (línea 310 del `.bib`) |
| P7 | Flujo de la Figura `fig:met_flujo`: (1) datos y partición, (2) criterios, (3) clasificadores supervisados como referencia, (4) VLM, (5) generación, (6) *pipeline*. Descripción del *pipeline*. La decisión de que el diagnóstico lo fije un clasificador se justifica con un resultado del Cap. 4. El tercer objetivo específico (evaluar en distintos escenarios) no agrega tarea: se aplica a clasificadores y *pipeline* en 3.8. | Orden: el de las secciones 3.2–3.8 del capítulo. Resultado: Cap. 4 (`cp:res_clasif`). Figura: `Figures/Capitulos/03-Materiales-Metodos/flujo_trabajo.tex`. | ninguna |
| P8 | Cierre: la primera etapa del flujo son los datos y su partición. | — | ninguna |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Figura `fig:met_flujo` | Seis etapas en escalera, cada una con la sección que la describe (1. Datos y partición por lesión; 2. Criterios de evaluación; 3. Clasificadores supervisados; 4. Clasificación con VLM; 5. Generación de reportes; 6. *Pipeline*: cascada y ruteo) y un nodo «Evaluación en otros escenarios» con flechas punteadas desde los clasificadores y el *pipeline*. Sin cifras ni fechas | `Figures/Capitulos/03-Materiales-Metodos/flujo_trabajo.tex` (estilos de `13-Figuras.sty`) | existe; se cita en P7 |

No hay tablas. El cuadro resumen de T1–T3 se descartó (no repetir la lista).

## Prosa ya escrita que se conserva

- **Párrafo de HAM10000** (antes en `02-datos-particiones.tex`): ahora es P2, ajustado: «gradación» → «no tienen la misma gravedad», remisión a 3.2 (`sec:met_datasets`) y a 3.3 (`sec:met_protocolo`, antes `sec:met_seleccion`). `HAM10000` va en cursiva. El label `sec:met_ham` se queda en 3.2.
- **No se mueve** a 3.1 el texto de `06-generacion-reportes.tex`: P5 formula las dos partes del reporte con sus propias palabras y `shen2025skincare`.

## Lo que va al apéndice

Reproducibilidad (versiones, semillas, comandos): Apéndice E (`ap:reproducibilidad`), citado en P6. El inventario de clases con su tamaño va en la tabla de 3.2.

## Lo que NO va en esta sección (y dónde está)

- Composición de HAM10000, distribución de clases, imágenes por lesión, partición disjunta por lesión y rol de cada conjunto: **3.2**.
- Costos asimétricos de confusión, métrica principal, de selección y oficial de generación, fidelidad diagnóstica frente a validez clínica: **3.3**.
- Detalles del tipo de modelo, receta y búsqueda: **3.4**; estrategias de los VLM: **3.5**; ajuste en dos etapas y LoRA: **3.6**; cascada y ruteo: **3.7**; HIBA, perturbaciones, calibración, Grad-CAM y costo: **3.8**.
- Definiciones de CNN, ViT, VLM, LoRA, fidelidad diagnóstica y calidad descriptiva: **Cap. 2**, solo con `\ref`.
- Resultados o desempeños (regla del capítulo): ver la inconsistencia anotada en «Preguntas abiertas», punto 9.

## Preguntas abiertas para el autor

Las preguntas 1–8 de la versión anterior de la ficha quedaron resueltas por la revisión del 18/10 (se conservan para registro).

1. **Mapeo maligno/benigno (AKIEC)** (sigue abierta, pasa a 3.3). El plan de cierre define maligno = {MEL, BCC, AKIEC}; la prosa dice que AKIEC reúne premalignas y carcinomas in situ. 3.1 define solo el binario melanoma frente a resto (T2); el binario maligno/benigno, si se usa, lo define 3.3.
2. **Entrada de T3 (resuelta).** El `.tex` define la entrada como la imagen y el diagnóstico que propone el clasificador (coherente con la cascada de 3.7).
3. **Salida de T1 (resuelta).** El `.tex` define la salida como una de las siete categorías con una probabilidad para cada una (la ficha anterior proponía solo la clase).
4. **Dónde se define «detección» (resuelta).** En 3.1, como T2 derivada de T1. El desfase entre el título de la tesina («detección») y lo desarrollado («clasificación») no se explica en el texto; sigue a decisión del autor.
5. **Cifras de hardware (resuelta).** La sección da las tres GPU con su memoria (12, 16 y 24 GB) en una oración; no hay tabla.
6. **Histopatología (resuelta).** Se afirma como fuera de alcance en 3.1 (P5).
7. **Cuadro resumen de T1–T3 (resuelta).** No hay tabla.
8. **HIBA y espacio de clases (resuelta).** Se trata en 3.2, no en 3.1.
9. **Resultado citado en P7 (nueva).** P7 dice que los VLM generales no discriminan entre las siete categorías (`cp:res_clasif`). Es un resultado, y la regla del capítulo es que el Cap. 3 no presenta resultados; está justificado como razón de diseño del *pipeline* y remite al Cap. 4. A confirmar por el autor.

## Números que no pude verificar

- «Dermatoscópicas ya recortadas y centradas en una única lesión»: **ya no aparece** en el `.tex` (obsoleta tras la revisión del 18/10).
- Los nombres institucionales de los clústeres (UNCuyo para TOKO, UNC para Mendieta) y las memorias de GPU (12, 16, 24 GB) salen de `Codigo/CLAUDE.md` según el encabezado del `.tex`; no se volvieron a verificar al poner al día la ficha.

## Decisiones tomadas por cuenta propia

- **D1 — Formato de la definición formal.** Cita en bloque en cursiva (como el ejemplo) con la definición de la tarea, y después una lista de tres ítems (guía §3, «Alternativas paralelas en lista»). Los ítems llevan el nombre en cursiva, no en negrita ni como título de párrafo.
- **D2 — Orden.** Definición → siete categorías → desglose en T1–T3 → mapeo con las preguntas → partes del reporte y alcance → restricción de cómputo → flujo → transición.
- **D3 — T2 es el binario melanoma frente a resto,** derivado de la probabilidad de melanoma de T1.
- **D4 — Relación con los objetivos.** Solo PI1 y PI2 (T1 y T2 → primera pregunta; T3 → segunda), sin OE por ítem; el tercer objetivo específico se resuelve en P7 como análisis aplicado, no como tarea.
- **D5 — Labels.** `sec:met_tareas` y `fig:met_flujo`. `sec:met_ham` se queda en 3.2.
- **D6 — Flujo como etapas del método (nuevo).** La figura y P7 presentan el método como seis etapas encadenadas en el orden del capítulo, sin ciclo de iteración ni hipótesis refutadas (R1, R2).
- **D7 — Partes del reporte en 3.1 (nuevo).** El alcance de T3 (qué partes del reporte se generan y cuáles quedan fuera) se declara acá (P5), con `shen2025skincare`; la versión anterior de esta ficha lo mandaba a la antigua 3.7. 3.6 puede retomarlo con `\ref`.
- **D8 — Hardware en 3.1 (nuevo).** Las tres GPU se dicen una vez, en P6 (R1: sin CUDA, sin W&B, sin versionado).

## Quitado en la revisión del 18/10/2026

Una línea por ítem. El contenido de fuentes sigue disponible en las fichas antiguas del historial de git.

- Ciclo hipótesis → ejecución → análisis → decisión como estructura del flujo (R1, R2: historia del proceso; el flujo es ahora una secuencia de etapas del método).
- Figura con «dónde una hipótesis refutada cambió el rumbo» (desbalance → especialización de dominio → cascada) (R1, R2).
- Registro de cada corrida y los documentos de cada iteración (`docs/ideas/`, `docs/ejecuciones.md`, `docs/resul/`) como parte de la sección (R1: importa al equipo, no al lector).
- Orden de los Caps. 4 y 5 como reflejo del orden de las decisiones (R1).
- Tabla de entorno de ejecución con CUDA, versiones, SLURM, seguimiento de experimentos (Weights & Biases) y versionado (R1); quedan solo las tres GPU en una oración y el Apéndice E.
- Los «12–36 GB» y el argumento de hardware que la ficha del Cap. 1 mandaba al Cap. 3, y el uso de memoria por modelo (R1); quedan una GPU de consumo y las tres capacidades.
- Detalle de PI y OE por ítem de la lista (OE1, OE2 y la cita de «identificar posibles melanomas») (R3: no repetir lo que el Cap. 1 ya presentó); queda solo el mapeo con PI1 y PI2.
- La palabra «gradación» de la gravedad de las categorías (se reemplaza por «no tienen la misma gravedad»).
- Transición original a 3.2 («Las tres tareas no se resolvieron en un orden fijo: cada resultado obligó a revisar la siguiente decisión…», `sec:met_metodologia`) (R1: historia del proceso); 3.2 ya no es el flujo.
- Aclaración de que 3.2 ordena las etapas con las tres tareas; esa función ahora la cumple P7 de esta misma sección.
- Brechas del estado del arte y su relación con las tareas (`tab:marco_brechas`) en «Viene de» (R3: el Cap. 2 ya lo presentó); queda solo la propuesta.
- Línea «dermatoscópicas ya recortadas y centradas en una única lesión» (nunca verificada; no está en el texto).
