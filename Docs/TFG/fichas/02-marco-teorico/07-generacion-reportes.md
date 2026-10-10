# Ficha 2.7 — Generación de reportes

Sección del `.tex`: `Chapters/02-Marco-Teorico/07-generacion-reportes.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.6 Generación de reportes y recuperación de información — `sec:marco_reportes`

**Sección nueva (G1, G2, G3).** Peso comparable al de la clasificación. **Extensión: 6 páginas.**

**Mensaje central.** Generar un reporte dermatológico implica tres problemas distintos: describir lo que se
ve, incorporar un diagnóstico y no afirmar más de lo que la evidencia justifica. Los modelos fallan de dos
maneras opuestas, alucinando o evitando comprometerse, y hay tres mecanismos diferentes de recuperación y
decisión que pueden ayudar a corregirlos.

**Razón de ser.** El Cap. 1 presenta dos tareas de peso equivalente; el marco tiene que tratarlas de igual
modo. Los tres ejes son la pregunta de investigación PI2 (fidelidad diagnóstica frente a calidad descriptiva)
formulada en teoría.

**Apertura.** Una oración sobre qué es un reporte clínico y por qué su generación automática no es una simple
descripción de imagen.

| Subsección | Razón de ser | Se reutiliza | Nuevo |
|---|---|---|---|
| 2.6.1 De la descripción de imágenes al reporte clínico — `sec:marco_rep_tarea` | Definir la tarea y su dificultad | l. 521–537 (*image captioning*, radiología, `jing2018automatic`, `chen2020generating`, texto y referencia) | Recorte: se elimina el detalle de qué escribió cada conjunto (SkinCAP, SkinCoT, MM-Skin, Derm1M; l. 529–537) y se deja la idea general: la referencia proviene de fuentes con distinto grado de curaduría y eso condiciona la evaluación (`shen2025skincare`, `zeng2025mmskin`, `yan2025derm1m` como ejemplos, detalles en Cap. 3). Se elimina «que son las dos partes del reporte de las que se ocupa el trabajo» |
| 2.6.2 Tres ejes de la generación de reportes — `sec:marco_rep_ejes` | Ordenar el problema (A11) | l. 551–556 (dos condiciones independientes) | **Nuevo**, tres bloques (ver abajo) |
| 2.6.3 Alucinaciones y *hedging* — `sec:marco_rep_fallas` | G2: desarrollo | l. 539–549 | **Nuevo**, ver abajo |
| 2.6.4 Recuperar documentos: RAG — `sec:marco_rag` | Mecanismo (a) | l. 561–579 (Lewis, `eq:marco_rag`) | Reescritura según §6 |
| 2.6.5 Recuperar imágenes similares — `sec:marco_recuperacion_imagenes` | Mecanismo (b) | l. 581–594 (kNN, `khandelwal2020generalization`, `sun2025factaware`) | **Nuevo**: ver abajo |
| 2.6.6 Concordancia entre predicciones — `sec:marco_concordancia` | Mecanismo (c) | — | **Nuevo**: ver abajo |
| 2.6.7 Qué aportaría integrar los tres mecanismos — `sec:marco_integracion` | Cierra el eje sin adelantar la implementación | — | **Nuevo**: ver abajo |

### 2.6.2 Tres ejes (A11) — ideas por párrafo

1. **Eje 1: describir lo que se ve.** Producir un texto que refleje rasgos visuales de la lesión (color,
   patrón, distribución, estructuras). Se reutiliza el vocabulario cerrado, estandarizado por consenso, que hoy
   está en 2.6.3 (l. 798–804): conviene que aparezca acá porque define qué es una descripción correcta y
   permite medirla (2.8.2). Citas: `kittler2016standardization`, `argenziano1998checklist`. La **calidad
   descriptiva** es la correspondencia entre lo dicho y lo que la imagen muestra.
2. **Eje 2: incorporar información diagnóstica.** El texto necesita nombrar una categoría. Dos formas de lograrlo:
   que el mismo modelo generativo infiera el diagnóstico de la imagen (de extremo a extremo) o que se lo
   *condicione* en un diagnóstico o evidencia externos (una predicción de otro modelo, casos recuperados). Se
   define la **fidelidad diagnóstica** (el diagnóstico que nombra el texto es el correcto) y se establece que es
   independiente de la calidad descriptiva: puede haber un texto descriptivamente fiel con un diagnóstico
   erróneo, y un diagnóstico correcto acompañado de hallazgos inventados (retoma la Figura~\ref{fig:intro_dos_tareas} del Cap. 1;
   ver pregunta 5 sobre la dependencia con Cap. 1). Cita `gu2024medvh` para lo que se sabe de las fallas de
   los VLM médicos.
3. **Eje 3: tratar las predicciones inciertas.** Cuando el diagnóstico no está claro, afirmar uno es el peor
   caso; las alternativas son presentar varios candidatos o no afirmar y derivar. Esto es el tema de 2.7. Este
   párrafo instala el problema; 2.7 lo resuelve. No se adelanta el ruteo.
4. **Cómo se relacionan los ejes.** El eje 2 usa lo que el eje 3 decide (qué afirmar) y el eje 1 depende de que
   el modelo mire la imagen. Ese orden de dependencia justifica el orden de 2.6.3 a 2.7.

### 2.6.3 Alucinaciones y *hedging* (G2) — ideas por párrafo

1. **Alucinación: definición y contexto.** Texto fluido con contenido no sustentado por la imagen (o por la
   entrada). Se originó en generación de lenguaje natural y en descripción de imágenes: `ji2023survey`
   (nueva; verificada: arXiv 2202.03629), `rohrbach2018object` (nueva; verificada: arXiv 1809.02156;
   muestra que las métricas estándar de oraciones no siempre reflejan la alucinación, y que se debe en parte a
   *priors* del lenguaje). En VLM: `bai2024hallucination` (nueva; verificada: arXiv 2404.18930). En VLM
   médicos: `gu2024medvh` (ya está; los modelos ajustados al dominio alucinan más, l. 541–543).
2. **Por qué es especialmente costosa en medicina.** El lector no puede separarla del contenido correcto por la
   sola forma del texto; introduce hallazgos que pueden cambiar una conducta. No se afirma más que lo que
   respaldan las fuentes.
3. ***Hedging*: definición.** Descripciones genéricas, compatibles con casi cualquier lesión, sin comprometer un
   diagnóstico (l. 545–549). Se mantiene sin cita como falla observada durante la experimentación (decisión
   15 vigente), pero se puede relacionar con **abstención**: `kalai2025hallucinate` (nueva; verificada: arXiv
   2509.04664) argumenta que los esquemas de evaluación que premian acertar y no penalizan adivinar
   incentivan la alucinación; la contracara de expresar incertidumbre es lo que se llama aquí *hedging*
   cuando es indiscriminado. **No** se afirma que Kalai trate el *hedging* (revisar el PDF antes de citar).
4. **Ventajas y desventajas de cada comportamiento**, en una tabla o `enumerate` de tres filas: (i) afirmar
   (útil si acierta, dañino si no; fluidez engañosa); (ii) alucinar (mismas características, con detalles
   inventados); (iii) *hedging* (no afirma nada falso, pero no informa y es inaccionable; enmascara si el modelo
   "sabe" o no). El comportamiento deseable es expresar incertidumbre **cuando y solo cuando corresponde**, que
   conecta con 2.7.
5. **Qué pasa si no se analizan.** Las métricas de solapamiento con la referencia (2.8.2) pueden premiar un
   texto genérico, y ninguna detecta por sí sola un hallazgo inventado; un desempeño alto en esas métricas puede
   coexistir con reportes inutilizables. Por eso hace falta medir la fidelidad diagnóstica y la cobertura
   clínica por separado y revisar el texto contra la imagen (retoma l. 814–819). Sin números.

### 2.6.5 Recuperar imágenes similares — ideas

1. **Idea.** En vez de documentos, se dispone de una base de casos etiquetados. Para una imagen consulta $x$ se
   buscan los $k$ casos más cercanos en el espacio de *embeddings* $f$ de un codificador visual:
   $\mathcal{N}_k(x)=\operatorname{arg\,top\text{-}k}_{j}\,\cos(f(x),f(x_j))$. La información asociada a esos
   casos (diagnóstico, localización) es **evidencia visual**: qué se ha visto que se parece.
2. **Clasificador kNN como estimador local.** $\hat p_{\text{kNN}}(c\mid x)=\frac1k\sum_{j\in\mathcal{N}_k(x)}\mathbf{1}[y_j=c]$
   y predicción por voto mayoritario. Cita `cover1967nearest` (nueva; sin verificar; es la referencia clásica) y
   `khandelwal2020generalization` (la búsqueda de vecinos mejora la predicción sin entrenamiento adicional, ya en el `.tex`).
3. **Diferencia con RAG.** No hay documentos ni recuperador entrenado: el codificador ya existe y se usa
   congelado; lo recuperado son etiquetas de imágenes y no textos. Es una recuperación de la misma
   modalidad que la consulta (imagen–imagen), no de otra (imagen–documento).
4. **Antecedentes.** En descripción de imágenes, la recuperación de descripciones de imágenes parecidas como
   *prompt* (`ramos2023smallcap`, nueva; verificada: arXiv 2209.15323; CLIP + GPT-2 condicionado en captions
   recuperados). En reportes médicos, `sun2025factaware` (ya en el `.tex`).
5. **Límites.** La calidad de la evidencia depende de la representación y de la cobertura de la base; los
   vecinos de una clase rara pueden pertenecer a otra; si no hay casos parecidos, los vecinos igual existen y
   no son informativos (el $k$ vecinos más cercanos siempre existe). Esa última observación conecta con 2.7.3.

### 2.6.6 Concordancia entre predicciones — ideas

1. **Idea.** Dos predictores con sesgos distintos (por ejemplo, uno supervisado y otro basado en vecinos sobre
   una representación aprendida de otra forma) pueden coincidir o no sobre la misma imagen. Definir
   $a(x)=\mathbf{1}[\hat y_1(x)=\hat y_2(x)]$.
2. **Por qué es una señal.** El desacuerdo entre modelos aproxima la incertidumbre del sistema (ensambles:
   `lakshminarayanan2017simple`, nueva; verificada: arXiv 1612.01474). La afirmación medible es
   $P(\text{error}\mid a=1)<P(\text{error}\mid a=0)$; se enuncia como condición que se verifica con datos,
   nunca como hecho. **Sin cifras del trabajo** (los resultados de acuerdo Swin–kNN van en Cap. 5).
3. **Qué no es.** No recupera información ni condiciona el texto: es una regla de decisión. Se distingue de los
   dos mecanismos anteriores por esa razón. La política de decisión se desarrolla en 2.7.3–2.7.4.

### 2.6.7 Integración — ideas (sin adelantar implementación)

1. **Qué aporta cada mecanismo por separado**, en una tabla de tres filas: qué recupera o computa, sobre qué
   modalidad, qué problema del reporte ayuda a resolver (descripción, diagnóstico, incertidumbre) y qué no
   resuelve.
2. **Qué aportaría integrarlos.** La evidencia recuperada puede condicionar el texto (eje 2); la concordancia
   entre predictores puede decidir cuánta afirmación permite la evidencia (eje 3). Combinados, el texto
   generado quedaría condicionado por evidencia y por el nivel de acuerdo: afirmaría cuando las señales
   coinciden y matizaría cuando no. Se formula como **propiedad deseable** y no como diseño.
3. **Qué queda abierto** (hipótesis para Cap. 3–5, sin nombrarlas hipótesis): si la evidencia recuperada mejora
   la fidelidad diagnóstica; si el acuerdo entre predictores separa los casos confiables. Esto se estudia con
   experimentos y se define en Cap. 3. No se menciona Swin, DermLIP ni k=3.

**Párrafo de transición a 2.7.** La integración depende de poder decidir, para cada imagen, cuánta afirmación
justifica la evidencia; esa decisión es un problema con su propia teoría, la predicción selectiva.
**Citas de 2.6:** existentes: `jing2018automatic`, `chen2020generating`, `shen2025skincare`, `zeng2025mmskin`,
`yan2025derm1m`, `gu2024medvh`, `kittler2016standardization`, `argenziano1998checklist`,
`lewis2020retrievalaugmented`, `khandelwal2020generalization`, `sun2025factaware`, `brown2020language`.
Nuevas: `ji2023survey`, `rohrbach2018object`, `bai2024hallucination`, `kalai2025hallucinate`,
`ramos2023smallcap`, `gao2023retrieval` (revisión de RAG; opcional), `cover1967nearest`,
`lakshminarayanan2017simple`.

## 6. Corrección de RAG (G3, A13)

**Diagnóstico.** La `eq:marco_rag` (l. 574–577) es la formulación original de Lewis et al. (RAG-Sequence):
$p(y\mid x)\approx\sum_{z\in\text{top-}K}p_\eta(z\mid x)\,p_\theta(y\mid x,z)$, con un recuperador entrenado
$p_\eta$ y marginalización sobre documentos. La implementación
(`Codigo/scripts/build_rag_index.py`, `generate_report.py`) hace otra cosa:

- Recupera, para cada imagen de test, los **$k=3$ casos de entrenamiento** más cercanos por **coseno** sobre
  *embeddings* de **DermLIP ViT-B/16** L2-normalizados, congelado (`sims = Xte @ Xtr.T`, `argpartition`).
- Con cada vecino arma un texto: diagnóstico completo (por ejemplo «melanoma») y localización entre
  paréntesis si existe, y lo concatena en una oración fija en inglés: «Retrieved visually similar
  dermatoscopic cases were diagnosed as: …».
- Ese texto (`rag_context`) se **pega en el *prompt*** (`RAG_TEMPLATE`, `GROUNDED_RAG_TEMPLATE`), junto con la
  imagen. El generador produce una sola salida, condicionada en imagen y *prompt*. **No marginaliza**.
- No entrena el recuperador, no hay índice aproximado (matriz de similitud completa), y lo recuperado **no son
  documentos**: son diagnóstico y localización de imágenes de la partición de entrenamiento, no textos de
  reportes ni de literatura.
- El voto mayoritario de los vecinos (`rag_knn_dx`) se guarda aparte y es una señal de 2.6.6; con tres vecinos
  todos distintos, `Counter.most_common` resuelve el empate a favor del vecino más cercano (los vecinos se
  ordenan por similitud descendente). El ruteo de 3 niveles (`build_uncertainty_3tier.py`) usa que los tres
  vecinos sean distintos como criterio de abstención; el de 2 niveles (`build_uncertainty_agreement.py`) usa solo
  si Swin y el voto kNN coinciden. Nada de esto va en el Cap. 2; queda para Cap. 3 (verificar).

**Cómo se presenta en 2.6.4 (ideas por párrafo):**

1. **Qué es RAG** (reutiliza l. 561–565): las tres partes (base, recuperador, generador) y la separación entre
   memoria paramétrica y evidencia. Cita `lewis2020retrievalaugmented`.
2. **La ecuación original, atribuida a Lewis** (reutiliza `eq:marco_rag` con la explicación de l. 567–579), con la
   frase explícita: «Esta es la formulación de Lewis et al., que combina un recuperador entrenado y un
   generador y marginaliza sobre los documentos recuperados». Se aclara que en ella el recuperador es una parte
   entrenada conjuntamente con el generador y que los documentos son textos.
3. **La idea general que sobrevive a la formulación**: lo esencial es que el generador condiciona en información
   recuperada. Se puede escribir en forma simplificada, sin marginalización:
   $$y\sim p_\theta\!\bigl(\,\cdot\mid x,\ c(x)\bigr),\qquad c(x)=\psi\bigl(\mathcal{N}_k(x)\bigr),$$
   donde $\mathcal{N}_k(x)$ son los elementos recuperados y $\psi$ los serializa como texto que se agrega al
   *prompt*. Se lo llama **condicionamiento por contexto** y se apoya en 2.4.1 (contexto y *in-context learning*,
   `brown2020language`): el modelo no cambia sus pesos, cambia lo que ve.
4. **Diferencias con RAG original**, en una tabla de tres filas o una oración por diferencia: (i) el recuperador
   no se entrena junto con el generador; (ii) no se marginaliza sobre los documentos, el generador recibe todo
   el contexto a la vez; (iii) lo recuperado puede no ser un documento. **El texto dice explícitamente** que el
   trabajo implementa esta variante y no el modelo de Lewis, sin describir la implementación (eso es Cap. 3).
   No se usa la sigla «RAG» sin calificar cuando se habla de la variante: se dice «condicionamiento por contexto
   con recuperación» y, cuando convenga, «variante de RAG por contexto». La sigla con su expansión (Lewis)
   queda para la formulación original.
5. **Sin adelantar la implementación:** no se nombra DermLIP, $k=3$, la localización ni el *prompt*.
