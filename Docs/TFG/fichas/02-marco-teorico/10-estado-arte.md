# Ficha 2.10 — Estado del arte

Sección del `.tex`: `Chapters/02-Marco-Teorico/10-estado-arte.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.10 Estado del arte y posicionamiento del trabajo — `sec:estado_arte`

**Mensaje central.** Cada línea aporta algo y deja algo sin resolver; los huecos combinados son los que
originan el *pipeline* y los análisis del trabajo, que por eso no repiten trabajos previos.

**Extensión: 9–11 páginas** (tres ejes de 2 páginas cada uno, más tablas, intro y posicionamiento).

**Intro de la sección (p59, S2).** Sin «los tres ejes en el orden del *pipeline*». Dice qué revisa (los
trabajos más cercanos a la tesina), con qué criterio los agrupa (tres problemas: clasificación de lesiones, modelos
visión–lenguaje en dermatología, generación de reportes) y el criterio temporal (2020–2026; los anteriores como
hitos fechados; guía §6). Se mantiene la frase sobre el corte práctico (l. 962–964). Sin figuras.

**Estructura de cada eje** (aplica a los tres):

1. Intro de la subsección (p60): qué problema aborda esta línea, con qué datos y protocolos se suele evaluar,
   qué se espera de un trabajo.
2. Hitos anteriores a 2020 (solo si son imprescindibles; A15).
3. Trabajos existentes, reescritos con el formato de nueve puntos de S3 (objetivo, problema puntual, método y
   novedad, datos, métricas, con qué se compararon, resultados, evaluación con expertos, limitaciones), verificados
   contra el PDF.
4. **Lugar marcado: «Trabajos nuevos: pendiente de S3».** Se agregan a los ya citados hasta llegar a 6–8 por eje.
5. **Síntesis (S4, A15, A16)**, un párrafo por eje: cómo las familias de enfoques atacan el problema (problema,
   arquitecturas, datos, protocolo, limitaciones) y qué queda sin resolver.
6. **Tabla comparativa (S5)**: trabajo, año, arquitectura, datos, métricas, resultado principal, evaluación con
   expertos.

| Subsección | Se reutiliza | Se elimina | Trabajos citados hoy | Nuevo |
|---|---|---|---|---|
| 2.10.1 Clasificación de lesiones — `sec:estado_arte_diagnostico` | l. 966–1036 sin la tabla de conjuntos; hitos de `esteva2017dermatologistlevel` y `tschandl2019comparison` (redactados sin «La línea tiene dos hitos…» → «En 2017…» o una intro) | **`tab:marco_conjuntos` y su párrafo** (l. 978–1019, S1). Se escribe «del conjunto de datos HAM10000» donde corresponda (p60) y se remite a Cap. 3. **Se elimina** el cierre «el trabajo compara cuatro arquitecturas… bajo la misma partición» (l. 1033–1036): pasa al posicionamiento | `magalhaes2024systematic`, `aboulmira2024skinhealthmate`, `khan2025ensemble`, `kreouzi2024learning`, `kim2025skinsavvy2` | S3: ≈ 4 trabajos; tabla `tab:marco_sota_clasificacion` |
| 2.10.2 VLM en dermatología — `sec:estado_arte_vlm` | l. 1038–1069 | **Se elimina** «El trabajo usa DermLIP…» (l. 1056–1059) y «El trabajo mide LLaVA-Med y Phi-3.5-Vision…» (l. 1068–1069): pasan al posicionamiento | `kim2024transparent`, `codella2024medimageinsight`, `yan2025derm1m`, `yan2025make`, `yan2025vision`, `li2023llavamed`, `moor2023medflamingo`, `he2025pefomed`, `xie2025medtrinity25m`, `zeng2025mmskin`, `abdin2024phi3` | S3: ≈ 4 trabajos; tabla `tab:marco_sota_vlm` |
| 2.10.3 Generación de reportes — `sec:estado_arte_reportes` | l. 1071–1128, con `tab:marco_generadores` como punto de partida de S5 | Se elimina «como hace este trabajo» (l. 1085); cierre de l. 1130–1134 se convierte en síntesis del eje | `zhou2023skingpt4`, `zhou2024pretrained`, `zeng2025mmskin`, `yilmaz2025resourceefficient`, `liu2025skinr1`, `khan2025ensemble`, `kim2025skinsavvy2`, `chakrabarti2025skin`, `lin2025skingen`, `cao2024mpoxvlm` | S3: ≈ 4 trabajos; tabla ampliada (agregar columnas de datos y expertos) |
| 2.10.4 Posicionamiento del trabajo — `sec:estado_arte_posicion` | l. 1136–1144 (brecha triple) | Se reformulan las dos excepciones | Los ya citados | **Nuevo**, ver abajo |

**Observación sobre profundidad (A16).** El tutor pide 7–8 artículos por eje, con una carilla y media a dos por
eje y análisis en los nueve puntos. Hoy hay ≈ 5 en clasificación dentro de la ventana, ≈ 10 en VLM y ≈ 10 en
reportes, pero la mayoría con 2–3 líneas de descripción. Los ya citados **también** hay que reverificar contra
el PDF en los nueve puntos (no solo los nuevos). Ver pregunta 11.

### 2.10.4 Posicionamiento (S6) — ideas

1. **Qué dejó sin resolver cada línea** (tres oraciones, una por eje, con la síntesis de arriba): clasificación:
   métricas que ocultan las clases minoritarias y poca validación externa; VLM: modelos generales medidos
   sobre todo en radiología y patología, evidencia escasa en dermatología, y especializados
   contrastivos que clasifican y recuperan pero no redactan; reportes: evaluación por parecido textual, poca
   fidelidad diagnóstica, hardware fuera de alcance, pocos tratan la incertidumbre.
2. **Tabla brecha → decisión** (opcional): brecha | evidencia | qué hace el trabajo. Tres filas, sin cifras propias.
3. **De los huecos al *pipeline*.** La comparación bajo un mismo protocolo responde a la primera brecha; la
   medición de fidelidad y calidad descriptiva por separado, a la segunda; el ruteo por incertidumbre con
   recuperación, a la tercera, ligada a 2.6 y 2.7. Se dice que el aporte es el *pipeline* y el análisis
   conjunto, no la réplica de un modelo previo (A16). Se puede mencionar DermLIP como codificador contrastivo
   ejecutable en hardware accesible (es la justificación de elección hoy en l. 1056–1059). Descripción
   completa del *pipeline*: Cap. 3.
4. **Excepciones reconocidas** (decisión 16 vigente): el ensamble de `khan2025ensemble` ya deriva casos
   discordantes; `chakrabarti2025skin` mide corrección diagnóstica.
