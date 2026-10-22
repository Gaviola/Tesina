# Ficha del Capítulo 3 — Materiales y métodos

**Estado (11/10/2026): aprobada por el autor como punto de partida; revisada el 18/10/2026 (ver abajo).** Contrato del capítulo. Ninguna sección se redacta hasta que
el autor apruebe esta ficha y la ficha de la sección (guía §1).

## Revisión del tutor del 21/10/2026 (prevalece sobre todo lo que sigue) — PROPUESTA, a aprobar

Fuente: `feedback/cap_3/feedback_cap3.md` (mensaje, tres audios y 31 comentarios del PDF transcritos al final).
Las reglas generales que deja pasaron a la guía (§3, «Capítulo de metodología», y entradas nuevas en «Léxico
preciso», «Voz y estilo» y la lista de control). Mensaje del tutor: el capítulo no está mal, pero hay que
reordenarlo para que se lea como las decisiones que llevan del problema al *pipeline* y a su evaluación.
Revierte la decisión D2 del 11/10 (criterios antes de los modelos).

### Estructura nueva

| Nueva | Título | Archivo (renombrado) | Viene de | Qué cambia |
|---|---|---|---|---|
| Intro | — | `00-capitulo.tex` | Intro | Primero la lógica metodológica (problema → componentes → integración → evaluación), después la organización en dos o tres oraciones; sin describir el *pipeline* (lo hace 3.1) ni sección por sección; presente |
| 3.1 | Definición de las tareas y flujo de trabajo | `01-tareas.tex` | 3.1 | Problema y tareas juntos; la restricción de cómputo queda como alcance, sin GPU ni clústeres; la Figura 3.1 (redibujada con el orden nuevo) culmina la sección con una oración por etapa; abre con «la propuesta de este trabajo integra…» |
| 3.2 | Conjuntos de datos | `02-datos.tex` | 3.2 | P1 describe los conjuntos; P2 explica su papel por uso (entrenamiento, validación, prueba, evaluación externa, preentrenamiento de terceros) y por qué *HAM10000* pesa más; la tabla agrupa por uso. Partición reescrita: 70/15/15 explicado, la fuga dicha sin «inflar», sin «así está hecha». *SkinCaRe* sin «en dos partes». Cierre: cómo los datos condicionan la elección de los modelos |
| 3.3 | Clasificadores supervisados | `03-clasificadores-supervisados.tex` | 3.4 | Estructura común: propósito → modelos seleccionados (por qué, luego características) → figura de uso → configuración (entrada, entrenamiento) → procedimiento experimental (búsqueda, semillas, funciones de pérdida, ensamble). Los criterios se nombran con `\ref` a 3.7. «Función de pérdida» en la tabla; «voto suave (*soft voting*)». Conserva el párrafo de cierre hacia los VLM |
| 3.4 | Clasificación con modelos visión–lenguaje | `04-clasificacion-vlm.tex` | 3.5 | La misma estructura que 3.3; figura de uso de Mini-VLM/LLaVA-Med y de DermLIP; sin repetir arquitectura del Cap. 2 |
| 3.5 | Generación de reportes | `05-generacion-reportes.tex` | 3.6 | Abre con qué información necesita un reporte y qué limitaciones tienen los modelos por separado; configuración de entrenamiento y de generación agrupadas; cierra con por qué la generación aislada lleva a integrar los componentes. Sin «inventario cerrado»; LoRA solo se nombra |
| 3.6 | Pipeline propuesto | `06-pipeline.tex` | 3.7 | Componentes disponibles (qué aporta cada uno) → necesidad de integrarlos (debilidades conocidas por el marco y el estado del arte, sin resultados propios) → arquitectura (figura) → funcionamiento (cascada, recuperación) → decisiones de salida (ruteo en tres niveles). Sale «como muestra el Capítulo 4». Arquitectura general separada de las reglas de decisión |
| 3.7 | Protocolo y criterios de evaluación | `07-criterios-evaluacion.tex` | 3.3 | Criterios generales (selección en validación, referencias, semillas) → métricas de clasificación y umbral de melanoma → evaluación de la generación de reportes → comparación estadística. Tabla experimento → qué se busca → métrica. Recibe el *oracle* y la línea base sin generador como referencias del *pipeline* |
| 3.8 | Evaluaciones complementarias | `08-evaluaciones-complementarias.tex` | 3.8 | Una subsección por tipo: generalización a otra población, robustez, calibración, interpretabilidad, costo computacional; cada una con objetivo, procedimiento y métrica. Sin GPU ni lotes («el costo computacional de los modelos y del *pipeline*»); la Tabla 2.8 citada con su capítulo |
| 3.9 | Entorno experimental y recursos computacionales | `09-entorno-experimental.tex` (nuevo) | dispersa en 3.1, 3.3, 3.6, 3.8 | GPU y clústeres y qué se ejecutó en cada uno, precisión numérica, tamaños de lote, semillas, bibliotecas, cómo se midió el costo y remisión al apéndice de reproducibilidad |

Los labels se mueven con su contenido, así que los `\ref` de otros capítulos no se rompen (`sec:met_seleccion`,
`sec:met_protocolo`, `sec:met_estadistica`, `sec:met_complementarios` siguen existiendo).

### Comentarios puntuales y dónde se resuelven

| # (feedback) | Qué | Dónde |
|---|---|---|
| 1, 2 | Presente en la intro; «pruebas diseñadas» | Intro |
| 3, 4, 20 | Modelos y *pipeline* antes que métricas y pruebas | Estructura nueva |
| 5 | «encadena» → «integra» | 3.1 |
| 6, 28, 29 | Hardware, GPU y lotes a una sección propia | 3.9 |
| 7 | Flujo con una oración por etapa | 3.1 |
| 8–10 | Papel de los conjuntos explicado en dos párrafos | 3.2 |
| 11–14 | Partición: 70/15/15, fuga, «inflaba» | 3.2 |
| 15 | «en dos partes» | 3.2 |
| 16 | Quitar «(Sección 3.2.1)» | 3.7 |
| 17 | «Evaluación de la generación de reportes» | 3.7 |
| 18 | «tenga un valor más alto de una métrica» | 3.7 |
| 19 | Tabla de pruebas citada junto a ella | 3.7 |
| 21 | «Función de pérdida» | 3.3 |
| 22 | «voto suave (*soft voting*)» | 3.3 |
| 23 | Figuras de los modelos | 3.3, 3.4, 3.5 |
| 24 | «inventario cerrado» | 3.5 |
| 25, 26 | Sin resultados en la motivación del *pipeline* | 3.6 |
| 27, 30, 31 | «sistema», Tabla 2.8, «protocolo» | 3.8 |

### Figuras nuevas (TikZ, estilos de `13-Figuras.sty`)

- 3.1: flujo de trabajo con el orden nuevo (reemplaza `flujo_trabajo.tex`).
- 3.3: clasificador supervisado en este trabajo: *backbone* preentrenado → *dropout* → capa lineal de siete
  salidas → probabilidades; qué se entrena en cada etapa.
- 3.4: Mini-VLM y LLaVA-Med (codificador visual → proyector → modelo de lenguaje, con el *prompt*) y DermLIP
  (codificador de imagen → *embedding* → cuatro cabezas). La Figura 3.5 (*zero-shot* frente a verosimilitud) se
  conserva o se integra.
- 3.5: el ajuste en dos etapas, con qué se entrena y qué queda congelado en cada una.

## Revisión del autor del 18/10/2026 (reemplazada en la estructura por la del 21/10)

El autor revisó el capítulo redactado y pidió acercarlo a la tesina de ejemplo: menos extensión, mejor hilo entre
secciones, solo la configuración final y nada que importe al equipo pero no al lector. Se aplicó así:

| Nueva | Título | Archivo | Qué cambió |
|---|---|---|---|
| Intro | — | `00-capitulo.tex` | Anuncia cada sección por número, como la tesina de ejemplo |
| 3.1 | Definición de las tareas y flujo de trabajo | `01-tareas.tex` | Absorbe la antigua 3.2; definición formal de la tarea; figura del flujo como etapas del método |
| 3.2 | Conjuntos de datos | `02-datos.tex` | Menos cifras en el texto |
| 3.3 | Criterios de evaluación | `03-criterios-evaluacion.tex` | Justificación de cada métrica; líneas base explicadas; recibe la comparación estadística |
| 3.4 | Clasificadores supervisados | `04-clasificadores-supervisados.tex` | Solo la configuración final; sin receta anterior ni búsqueda vieja |
| 3.5 | Clasificación con VLM | `05-clasificacion-vlm.tex` | Orden de presentación y transiciones |
| 3.6 | Generación de reportes | `06-generacion-reportes.tex` | Sin repeticiones ni historia de LoRA; «Inferencia» une razonamiento y decodificación |
| 3.7 | Pipeline propuesto | `07-pipeline.tex` | Presentado como propuesta central; sin fechas |
| 3.8 | Evaluación en otros escenarios | `08-evaluacion-escenarios.tex` | Reemplaza a «Análisis complementarios»; sin tablas de protocolo |

Resultado: el capítulo tiene unas 12 páginas menos (el documento pasó de 155 a 143).

**Reglas que fijó el autor (valen también para los Caps. 4 y 5):**
- R1. Separar lo que importa al lector de lo que importa al equipo. No van: fechas de decisiones, revisiones del
  tutor, cambios durante el proceso, versiones de los resultados, Weights & Biases, versiones de CUDA, el registro
  de experimentos. Sí van: la configuración que produjo los resultados y la justificación de cada decisión.
- R2. Describir solo la configuración final, no las iteraciones viejas; el énfasis está en el *pipeline*.
- R3. No repetir teoría del Cap. 2: nombrarla con `\ref`. No repetir lo que otra sección ya presentó.
- R4. Cada métrica o umbral lleva su justificación.
- R5. Mismo hilo que los Caps. 1 y 2: cada sección retoma la anterior y deja instalada la siguiente.

**Decisiones del autor (18/10/2026):**
- D-A. La antigua 3.9 se disuelve: las pruebas estadísticas pasan a 3.3 (`sec:met_estadistica`); HIBA,
  perturbaciones, calibración, Grad-CAM y costo quedan en 3.8, un párrafo por pregunta. Se quitan
  `tab:met_protocolos`, `tab:met_protocolos_vlm`, `tab:met_protocolos_analisis`, `sec:met_inferencia` y
  `sec:met_analisis_compl`.
- D-B. Las corridas de DenseNet121 y ViT-B/16 con la receta anterior salen del Cap. 3 (y su búsqueda aleatoria de
  28 corridas). En el Cap. 4 se decide después si aparecen.
- D-C. Las decisiones tomadas con la prueba a la vista (F1 macro como criterio, concordancia como señal de ruteo,
  plantilla *noreasoning* elegida en un piloto con 17 imágenes de prueba) se declaran una sola vez, en 3.3.
- D-D. La especificidad ≥ 0.85 del umbral de melanoma se justifica como decisión de diseño (tope de 15 % de falsas
  alarmas en validación), sin atribuirla a una guía clínica.
- D-E. Se quitan las ablaciones de la receta de 3.4: no tienen resultados ni en local ni en TOKO.

**Pendientes:** la Etapa 1 de LLaVA-Med y la clasificación de Mini-VLM v3 no cambian el texto del Cap. 3. El Cap. 3
no tiene `\pendiente`.

Fuentes de esta ficha: el andamiaje actual de `Chapters/03-Materiales-Metodos/` (con el feedback del tutor del
14/09 y la revisión del 25/09 en sus comentarios), la ficha del Cap. 2 (`fichas/02-marco-teorico/00-capitulo.md`),
la ficha de referencia del Cap. 4 (rama `doc/cap04-resultados-clasificacion`), la tercera revisión del tutor
(`feedback/cap1_2/feedback_cap1_y_2_v3.md`, Audios 3 y 4), `Docs/experimentacion/experimentacion.tex` y el
Capítulo 3 de la tesina de ejemplo (`Docs/tesinamaglione_ejemplo.pdf`, pp. 37–58).

## Lo que se toma de la tesina de ejemplo

El Capítulo 3 de la tesina de ejemplo («Metodología y desarrollo del trabajo») resuelve un problema parecido:
datos propios con dificultades (desbalance de 95/4/1 %, registros atípicos, partición que no puede filtrar
información entre conjuntos), modelos de aprendizaje profundo comparados contra una línea base y cómputo
limitado. Su orden es: definición formal de la tarea → flujo de trabajo (figura) → datos (recolección, análisis
exploratorio, preprocesamiento, conjunto final) → arquitecturas → modelo *baseline* → hiperparámetros → método
de entrenamiento → métricas.

| De la tesina de ejemplo | Cómo se traslada | Qué se mejora |
|---|---|---|
| §3.1 «Definición formal de la tarea», en un párrafo destacado, con las clases enumeradas | 3.1 define las tres tareas del trabajo (clasificación en siete clases, detección binaria de melanoma, generación del reporte) con su entrada, su salida y la restricción de cómputo | Cada tarea se vincula con la pregunta (PI1, PI2) y el objetivo (OE) que responde |
| §3.2 «Flujo de trabajo» con una figura de etapas | 3.2 presenta el flujo con una figura TikZ | El flujo del ejemplo es lineal; el de este trabajo fue iterativo y la figura muestra dónde una hipótesis refutada cambió el rumbo (desbalance → especialización de dominio → cascada) |
| §3.3.2 Análisis exploratorio con figuras de distribución | 3.3 incluye un análisis exploratorio de *HAM10000*: distribución de clases, imágenes por lesión, ejemplos por clase | En el ejemplo el análisis es descriptivo; acá cada hallazgo justifica una decisión: el desbalance → la métrica (3.4); las imágenes repetidas por lesión → la partición disjunta; la modalidad → el rol de cada conjunto |
| §3.3.1 Tablas de las variables de cada fuente | Tabla de los conjuntos (modalidad, tamaño, rol, origen del texto) | Se agrega quién escribió los textos de referencia, que condiciona la validez de las métricas con referencia |
| §3.3.4 Distribución del conjunto final | Tabla de tamaños por clase en entrenamiento, validación y test de la partición por lesión | — |
| §3.5 «Modelo *baseline*» con su ecuación | 3.4 fija las líneas base y las cotas en un solo lugar: azar (1/7), clasificador mayoritario, clasificadores supervisados como referencia de los VLM, *oracle* y línea base sin generador para el *pipeline* | El ejemplo tiene una sola línea base; acá hay una por pregunta |
| §3.6 Tablas de hiperparámetros (parámetro, descripción, valores explorados), parámetros comunes y estrategia de búsqueda con el número de configuraciones | 3.5 lleva una tabla de los hiperparámetros explorados en el barrido y los fijos, con la estrategia de búsqueda y el número de corridas; 3.7 la configuración de LoRA y de decodificación | Las grillas completas van al Apéndice A; el cuerpo explica por qué esos rangos. Se reportan semillas y desvío, que el ejemplo no tiene |
| §3.7 Partición temporal justificada para que no se filtre información del futuro | La partición disjunta por lesión cumple el mismo papel y se justifica igual | Se cuantifica la fuga de la partición original y se dice cómo se midió su efecto |
| §3.7–3.8 Detención temprana, optimizador, función de pérdida con fórmula | Receta de entrenamiento en 3.5 | Las fórmulas ya están en el Cap. 2: acá solo se nombran con `\ref` y se dan los valores |
| §3.8 Métricas justificadas por el problema (minimizar falsos negativos) | 3.4 justifica cada métrica por el costo de las confusiones | El ejemplo redefine las métricas del Cap. 2; acá no se redefinen |

Lo que **no** se toma: los títulos de párrafo en negrita (la guía los prohíbe), la introducción que anuncia cada
sección por número con detalle técnico, y las listas de una línea por elemento cuando la prosa encadena mejor.

## Hilo del capítulo

Pregunta que responde el capítulo: ¿qué tareas, datos, modelos, procedimientos y criterios se usaron para
responder PI1 y PI2, de modo que otra persona pueda reproducir los experimentos y entender por qué se tomó cada
decisión?

Viene de: el Cap. 2 dejó los conceptos y, en el estado del arte, las limitaciones que el trabajo aborda y el
posicionamiento del *pipeline* (`sec:estado_arte_posicion`).
Deja instalado: todo lo que los Caps. 4 y 5 necesitan para presentar un resultado sin explicar cómo se obtuvo.

Estructura vigente desde la revisión del 18/10/2026:

```
Intro    Retoma la propuesta del Cap. 2 y anuncia qué hace cada sección, por número
          ↓ necesidad: antes de describir cada componente, qué se le pide al sistema
3.1      Tareas y flujo: definición formal de la tarea; siete categorías de HAM10000 y su gravedad; T1–T3;
         partes del reporte; una GPU de consumo y las tres GPU usadas; flujo en etapas (figura)
          ↓ necesidad: la primera etapa del flujo son los datos
3.2      Datos: tabla de conjuntos; HAM10000 (distribución, imágenes por lesión, respaldo de etiquetas);
         partición por lesión y medición de la fuga; SkinCaRe; MM-Skin, HIBA y Derm1M
          ↓ consecuencia: desbalance y costo desigual de las confusiones obligan a fijar cómo se juzga
3.3      Criterios: métricas de clasificación y su justificación, selección en dos niveles, semillas,
         decisiones con la prueba a la vista, umbral de melanoma; líneas base; evaluación de la generación;
         comparación estadística
          ↓ aplicación: con esos criterios se entrenan y eligen los clasificadores
3.4      Clasificadores supervisados: arquitecturas, preprocesamiento y TTA, entrenamiento e hiperparámetros,
         comparación de pérdidas para el desbalance, ensamble y detección de melanoma
          ↓ contraste: no generan texto; PI1 pregunta si un VLM clasifica igual de bien
3.5      Clasificación con VLM: Mini-VLM y LLaVA-Med con cuatro estrategias; DermLIP y sus modos; control
          ↓ ampliación: los VLM generativos además pueden redactar
3.6      Generación: generadores (incluido SkinVL), ajuste en dos etapas sobre SkinCaRe, inferencia
          ↓ consecuencia: el generador no decide si afirmar un diagnóstico
3.7      Pipeline (propuesta central): cascada con grounding, recuperación, ruteo en tres niveles, oracle y
         línea base sin generador
          ↓ necesidad: la prueba de HAM10000 no cambia las condiciones de entrenamiento (OE3)
3.8      Evaluación en otros escenarios: HIBA, perturbaciones, calibración, Grad-CAM, costo
→ Cierre: los resultados de clasificación abren el Cap. 4, y los de generación, el Cap. 5.
```

## Secciones, origen y archivos

Ver la tabla del bloque «Revisión del autor del 18/10/2026» al comienzo de esta ficha. Lo que sigue es la
correspondencia con la estructura de nueve secciones del 11/10, que se conserva para leer las fichas viejas:

| Antes (11/10) | Ahora (18/10) |
|---|---|
| 3.1 Definición de las tareas + 3.2 Flujo de trabajo | 3.1 Definición de las tareas y flujo de trabajo (`01-tareas.tex`) |
| 3.3 Conjuntos de datos | 3.2 (`02-datos.tex`) |
| 3.4 Criterios de evaluación y líneas base | 3.3 Criterios de evaluación (`03-criterios-evaluacion.tex`), con la comparación estadística |
| 3.5 Clasificadores supervisados | 3.4 (`04-clasificadores-supervisados.tex`) |
| 3.6 Clasificación con VLM | 3.5 (`05-clasificacion-vlm.tex`) |
| 3.7 Generación de reportes | 3.6 (`06-generacion-reportes.tex`) |
| 3.8 Pipeline propuesto | 3.7 (`07-pipeline.tex`) |
| 3.9 Análisis complementarios | 3.8 Evaluación en otros escenarios (`08-evaluacion-escenarios.tex`); la estadística pasó a 3.3 |

**Labels que no pueden cambiar** (los usan otros capítulos o las fichas del Cap. 4): `cp:metodos`, `sec:met_ham`,
`sec:met_seleccion`, `sec:met_particiones`, `sec:met_protocolo`, `sec:met_clasif_vlm`, `sec:met_estadistica`,
`sec:met_complementarios`. Desaparecieron en la revisión: `sec:met_metodologia`, `sec:met_infra`,
`tab:met_entorno`, `sec:met_supervisados_busqueda`, `sec:met_inferencia`, `sec:met_analisis_compl`,
`tab:met_protocolos`, `tab:met_protocolos_vlm`, `tab:met_protocolos_analisis` (ninguno se referenciaba fuera del
capítulo).

## Figuras y tablas previstas

| Sección | Elemento | Origen | Estado |
|---|---|---|---|
| 3.2 | Flujo de trabajo iterativo | TikZ nuevo, estilos de `13-Figuras.sty` | a dibujar |
| 3.3 | Tabla de conjuntos (modalidad, tamaño, rol, origen del texto) | `experimentacion.tex` (`tab:datasets`), corregida (*HIBA*) | a adaptar |
| 3.3 | Distribución de clases de *HAM10000* | `Docs/experimentacion/imagenes/F0_ham_dist.png`, o regenerada con la paleta Okabe–Ito | existe |
| 3.3 | Imágenes por lesión (histograma) | script nuevo sobre los metadatos de `Codigo/data/raw/HAM10000` | a generar |
| 3.3 | Una imagen de ejemplo por clase | `Codigo/data/raw/HAM10000`; revisar la licencia de *HAM10000* antes de reproducir (guía §7) | a generar |
| 3.3 | Tamaños por clase y partición | `Codigo/outputs/results/lesion_split_report.json` | a armar |
| 3.3 | Ejemplo de texto de *SkinCoT* | `ej_skincot_human.jpg` y el texto del conjunto | existe |
| 3.5 | Hiperparámetros explorados y fijos | `Codigo/configs/*.yaml`, `split_lesion_resul_20260926.md` | a armar |
| 3.6 | *Zero-shot* frente a *likelihood scoring* | `experimentacion.tex` (`fig:zsvslik`), redibujada con los estilos de la plantilla | a adaptar |
| 3.7 | Configuración de LoRA y decodificación | `Codigo/configs/` | a armar |
| 3.8 | Diagrama del *pipeline* y del ruteo | `experimentacion.tex` (`fig:cascada`, `fig:incertidumbre`) y `mapa-capitulo.tex` como base, sin cifras de resultados | a adaptar |
| 3.9 | Protocolo de inferencia por resultado; prueba estadística por comparación | fichas de los Caps. 4 y 5 | a armar |

## Decisiones de esta ficha (a confirmar por el autor)

| # | Cambio respecto del andamiaje | Motivo |
|---|---|---|
| D1 | «Modelos evaluados» se disuelve: cada modelo se presenta en la sección de la tarea que cumple (3.5, 3.6, 3.7) | El andamiaje describía Mini-VLM y LLaVA-Med en un lugar y su uso en otro. Ordenado por tarea, 3.5–3.6 preparan el Cap. 4 y 3.7–3.8 el Cap. 5, y cada modelo se presenta una vez, donde aparece primero |
| D2 | Los criterios de evaluación suben a 3.4, antes de los modelos, y reúnen las líneas base | El barrido de 3.5 elige por F1 macro y la detección de melanoma usa un umbral; si el criterio se explica al final, se usa antes de presentarlo (guía §3). Las líneas base juntas siguen el ejemplo (§3.5) |
| D3 | Sección nueva 3.1, definición formal de las tareas | Sigue al ejemplo (§3.1). Hoy las tareas están repartidas entre el `\pendiente` del capítulo, `sec:met_ham` y `sec:met_generacion` |
| D4 | Metodología e infraestructura se unen en 3.2, «Flujo de trabajo» | Sigue al ejemplo (§3.2) y deja el hardware dicho antes de que 3.5–3.8 lo usen para justificar decisiones (LoRA, modelos *Tiny*) |
| D5 | Análisis exploratorio de *HAM10000* con figuras nuevas en 3.3 | Sigue al ejemplo (§3.3.2), con la diferencia de que cada hallazgo justifica una decisión |
| D6 | Tablas de hiperparámetros en el cuerpo (3.5, 3.7); grillas completas en el Apéndice A | Sigue al ejemplo (§3.6). Hoy todo iba al apéndice |
| D7 | Preprocesamiento y aumento pasan de los datos a 3.5 | Son parte de la receta de entrenamiento de los clasificadores |
| D8 | Los análisis complementarios quedan al final, en 3.9 | Se aplican a modelos y al *pipeline* ya presentados |

## Alcance y decisiones heredadas

1. **Cada capítulo habla de lo suyo.** El Cap. 3 no define conceptos: los nombra y remite al Cap. 2 con `\ref`
   (tabla de abajo). Tampoco presenta resultados: un número aparece solo si describe datos o configuración
   (tamaños, porcentaje de fuga, hiperparámetros), nunca un desempeño. Los desempeños van a los Caps. 4 y 5. Las
   figuras que se adaptan de `experimentacion.tex` pierden sus cifras de resultados.
2. **Recibe del Cap. 1** (commit f520295, hoy en el `\pendiente` de `00-capitulo.tex`): el rol de cada conjunto,
   la histopatología fuera de alcance, «detección» = tarea binaria de melanoma derivada de la clasificación (no
   localización ni segmentación), fidelidad diagnóstica ≠ validez clínica, y la decisión de no preentrenar un
   VLM y adaptar modelos preentrenados con LoRA por la restricción de cómputo.
3. **Recibe del Cap. 2** (revisión del 25/09, decisión 14 del historial): las categorías de *HAM10000* (ya
   escrito, pasa a 3.1), los costos asimétricos de confusión (ya escrito, 3.4) y las partes del reporte (ya
   escrito; pasa a 3.1 como salida de la tarea de generación, y 3.7 lo retoma con `\ref`). La prosa ya escrita
   se conserva y se ajusta al hilo.
4. **Lo que la ficha del Cap. 2 manda al Cap. 3:** la versión de McNemar que usa el código, quién escribió los
   textos de referencia de *SkinCaRe* y *MM-Skin*, la distribución de *HAM10000* y la partición.
5. **Fuente de los números.** Partición disjunta por lesión: `Codigo/docs/resul/split_lesion_resul_20260926.md`
   y `Codigo/outputs/results/lesion_split_report.json`. Métrica oficial de la cascada, ruteo, *HIBA* y RAG:
   `Codigo/docs/resul/revision_experimentacion_20261003.md` (§5, decisiones) y `reanclaje_cascada_resul_20261003.md`.
   `Docs/experimentacion/experimentacion.tex` sirve para la estructura y el argumento, **no** para los números:
   su cuerpo es de la partición aleatoria (ver la nota de actualización al comienzo de ese archivo).
   Hiperparámetros: los valores efectivos están en `Codigo/src/training/recipes.py` y en los scripts de envío de
   los barridos, no en `Codigo/configs/*.yaml`, que `train_classifier.py` no lee y que en parte quedaron
   desactualizados (p. ej. `mini_vlm.yaml` describe CLIP ViT-B/16 + Phi-3-mini, pero el modelo usado es
   Phi-3.5-vision-instruct, según `src/models/mini_vlm.py`). Todo número de una ficha de sección dice de qué
   archivo sale.
6. **Declarado sobre la partición anterior** (no se rehace; el Cap. 3 lo dice donde corresponde): RAG y
   `full_uncertainty`, métricas por clase y taxonomía de la cascada, ablaciones de la receta. **Los VLM generales
   no se ajustaron sobre *HAM10000*** (corrección del 11/10/2026): la estrategia «ajuste fino» de clasificación
   evalúa sobre *HAM10000* el *checkpoint* de la etapa 2 de generación, entrenado con *SkinCaRe*
   (`train_vlm_classify.py --checkpoint stage2_*_v2`, `vlm_clasificacion_resul_v3_20260517.md`). No hay fuga en
   esos modelos. La ficha del Cap. 4 (rama `doc/cap04-resultados-clasificacion`, §4.2, «Declarar») dice lo
   contrario y hay que corregirla.
7. **Apéndices.** El detalle que no hace falta para seguir el argumento va al apéndice y se remite: grillas
   completas (A, `ap:hiperparametros`), *prompts* y plantillas (B, `ap:prompts`), reproducibilidad (E,
   `ap:reproducibilidad`), fichas de conjuntos y modelos (F).

## Dónde se define cada cosa

Lo que es concepto se definió en el Cap. 2 y acá solo se nombra con `\ref`. Lo que es decisión propia se define
una vez en el Cap. 3.

| Qué | Se define en | Se retoma en |
|---|---|---|
| Red neuronal, entropía cruzada, generalización, particiones, fuga de información, regularización, aumento, TTA, desbalance, transferencia | Cap. 2 (`sec:marco_fundamentos`, `sec:marco_regularizacion` —ahí están la fuga y el TTA—, `sec:marco_desbalance`, `sec:marco_transferencia`) | 3.2, 3.4 |
| CNN, ViT, Swin, ConvNeXt | Cap. 2 (`sec:marco_vision`) | 3.4 |
| LLM, LoRA, CLIP, VLM generativo, clasificación por verosimilitud | Cap. 2 (`sec:marco_llm`, `sec:marco_llm_lora`, `sec:marco_vlm`) | 3.5, 3.6 |
| Calibración, abstención, predicción selectiva, tres salidas | Cap. 2 (`sec:marco_incertidumbre`) | 3.7, 3.8 |
| Reporte clínico, alucinación, *hedging*, RAG | Cap. 2 (`sec:marco_reportes`) | 3.6, 3.7 |
| Métricas (sensibilidad macro, F1, AUC, ECE, BLEU…, McNemar, Holm, Grad-CAM), robustez, cambio de dominio | Cap. 2 (`sec:marco_evaluacion`, `sec:marco_generalizacion`) | 3.3, 3.8 |
| Las tres tareas, las siete clases y su gravedad, las dos partes del reporte, la restricción de cómputo, el flujo | 3.1 | todo el capítulo |
| Composición de *HAM10000*, imágenes por lesión, partición disjunta por lesión, formato de *SkinCoT* | 3.2 | 3.3, 3.4, 3.6 |
| Métrica principal, de selección y de generación; líneas base; umbral de melanoma; fidelidad vs validez; pruebas estadísticas; decisiones con la prueba a la vista | 3.3 | 3.4–3.8 |
| Configuración de entrenamiento, hiperparámetros, ensamble de clasificadores | 3.4 | 3.7, 3.8 |
| Mini-VLM, LLaVA-Med, las cuatro estrategias, DermLIP y sus modos | 3.5 | 3.6, 3.7 |
| SkinVL, ajuste en dos etapas, separación reporte / razonamiento | 3.6 | 3.7 |
| Cascada, *grounding*, *noreasoning*, ruteo en tres niveles; *oracle* y línea base sin generador | 3.7 | 3.8 |

**Dependencia con la reescritura del Cap. 2.** Los labels del Cap. 2 se conservan al reescribirlo (su ficha lo
fija), así que los `\ref` de este capítulo no se rompen. Si al reescribir el Cap. 2 un concepto cambia de
sección, se corrige el `\ref` acá; no se redefine.

## Revisión cruzada de las fichas de sección (11/10/2026; numeración vieja, ver la correspondencia arriba)

Las nueve fichas se prepararon en paralelo. Lo que esta revisión resolvió prevalece sobre lo que diga cada ficha:

1. **Labels del Cap. 2.** La fuga de información y el TTA están en `sec:marco_regularizacion` (2.1), no en
   `sec:marco_generalizacion` (2.9, sesgo y robustez). Ya corregido en las fichas 3.2, 3.3, 3.4, 3.6, 3.8 y 3.9.
2. **Claves de cita.** *HIBA* es `riccilara2023dataset`; LLaVA-Med es `li2023llavamed`; LoRA es `hu2021lora`.
   Mini-VLM (Phi-3.5-vision) es `abdin2024phi3` y SkinVL (presentado en el artículo de *MM-Skin*) es
   `zeng2025mmskin`: las dos ya estaban en el `.bib` (corrección del 11/10/2026).
3. **Duplicaciones.** Las partes del reporte se definen en 3.1 (3.7 las nombra). El *oracle* y la línea base sin
   generador se definen en 3.8 (3.4 solo anuncia que el *pipeline* tiene su propia línea base).
4. **VLM ajustados sin fuga** (ver «Alcance», punto 6). Afecta a 3.6 y a la ficha del Cap. 4.
5. **Mini-VLM** es Phi-3.5-vision-instruct; los `.yaml` y `experimentacion.tex` que dicen CLIP ViT-B/16 +
   Phi-3-mini están desactualizados.

Preguntas que cruzan varias secciones y decide el autor (el detalle está en cada ficha):

- **Decisiones tomadas mirando el test.** *(Resuelta el 18/10: se declaran una sola vez en 3.3, D-C.)* El paso a F1 macro como criterio de selección (17/09, ficha 3.4), la
  elección de la concordancia como señal de ruteo (julio, ficha 3.8) y posiblemente la variante *noreasoning*
  (junio, ficha 3.8, a verificar) se motivaron con cifras de test. La frase «el test no interviene en ninguna
  decisión» no se puede escribir tal cual: se declara qué decisiones se tomaron así y por qué no invalidan el
  resultado.
- **Protocolos mezclados.** DenseNet121 y ViT-B/16 (receta anterior) se evalúan con vista única y pesos por
  clase; Swin y ConvNeXt, con TTA y sin pesos (fichas 3.5 y 3.9). **Resuelto (2026-10-17):** los dos se
  reentrenaron con la receta moderna (TOKO 99007–99012; `densenet_vit_moderna_resul_20261017.md`) y las corridas
  anteriores quedan como antecedente. **Revisión del 18/10:** salen del Cap. 3 (D-B).
- **Comparaciones múltiples.** *(Resuelta el 12/10: Holm sobre McNemar; recall por clase descriptivo, sin Wilcoxon; 3.3.)*
- **Evaluación en *HIBA*.** *(Resuelta: las 1 616 imágenes; 3.2 y 3.8.)*
- **Licencias.** *HAM10000* (CC BY-NC 4.0) para reproducir ejemplos por clase; *SkinCaRe* declara dos licencias
  y prohíbe redistribuir (ficha 3.3).

## Introducción del capítulo

Escrita el 18/10/2026 en el formato de la tesina de ejemplo: retoma la propuesta del Cap. 2 y anuncia,
por número, qué hace cada sección.

## Pasada de estilo (18/10/2026)

Revisión de las ocho secciones contra la lista de control de la guía §3 (hilo, conectores, legibilidad y estilo),
aplicada en cuatro grupos de cambios —legibilidad, reglas de la guía, tipografía y siglas, mecánica— más este
registro. Los grupos quedan separados para commitear por separado cuando el autor apruebe el diff.

| Qué se corrigió | Dónde |
|---|---|
| Oraciones ambiguas (la Figura 3.5, las decisiones del ruteo, «no es paramétrico», «su prueba», la prueba estadística frente al conjunto de prueba) | 3.3, 3.5, 3.6, 3.7 |
| Elipsis nominales y verbos figurados («mirar», «razonar en voz alta», «se describe tal cual está») | 3.2–3.7 |
| Las cuatro pérdidas del desbalance y las cuatro fuentes del anclaje pasan a lista, con los nombres en negrita | 3.4, 3.7 |
| Terminología: «test» → «prueba»; «se reporta» → «se informa»; «el intercambio» → *trade-off* | 3.3, 3.7 |
| SVM y MLP declaradas en el glosario; RGB se escribe por extenso; \emph{bfloat16} (bf16) al revés de antes | 3.5, 3.6, `Matter/05-Acronyms.tex` |
| Cursiva solo en la primera mención del capítulo de cada término en inglés (*prompt*, *tokens*, *checkpoint*, *zero-shot*, *oracle*), redonda después; nombres de lista en negrita también en T1–T3 | 3.1, 3.5, 3.7 |
| 3.3 abre con encuadre propio; 3.4 deja de anunciar su contenido (guía §3) | 3.3, 3.4 |
| Tablas de 3.2 y de 3.6 con `[H]`, como el resto; epígrafes recortados y su explicación movida al párrafo que los cita | 3.2, 3.3, 3.6 |
| `check_huerfanas 3`: 0 huérfanas. `check_floats 3`: los 8 flags que quedan son flotantes `[H]` cuyo `\input` va después de la mención | todo el capítulo |

**Decisiones:** la cursiva de un término en inglés marca su primera mención en el capítulo y después va en redonda
(como se hizo en el Cap. 2); las listas de alternativas nombran cada opción en negrita (guía §3, «Alternativas
paralelas en lista»). *Temperature scaling* y *vector scaling* ya estaban en cursiva; no hubo que tocarlos.

## Orden de trabajo

Cumplido hasta el paso 5 (prosa de las ocho secciones e introducción, revisada el 18/10/2026). La pasada de estilo
está aplicada (ver arriba); falta la aprobación del autor sobre el diff y los commits por grupos.


