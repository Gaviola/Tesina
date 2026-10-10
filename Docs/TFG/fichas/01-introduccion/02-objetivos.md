# Ficha 1.2 — Objetivos (con las preguntas de investigación)

Sección del `.tex`: `Chapters/01-Introduccion/02-objetivos.tex`.

**Estado: propuesta pendiente de aprobación del autor (2026-10-10).** El tutor no comentó la sección en la
tercera revisión. Los cambios surgen de la reescritura de 1.1, de la guía (cohesión y léxico) y de la
decisión 6 de `00-capitulo.md`.

## Hilo conductor

Pregunta que responde la sección: ¿qué preguntas guían el trabajo y qué objetivos se fija para responderlas?

Viene de: 1.1 cierra con dos cuestiones abiertas (si un VLM clasifica tan bien como un clasificador de
imágenes, y si sus reportes son fieles a la imagen y al diagnóstico) y con la restricción de hardware de
consumo.

Deja instalado: PI1, PI2, el objetivo general, OE1–OE3 y la tabla que los relaciona con los capítulos, que
lleva naturalmente a 1.3.

```
P1  Las dos cuestiones del final de 1.1 se formulan como preguntas de investigación → PI1, PI2
    (redacción actual, sin cambios)                                        función: define
    ↓ finalidad — «Para responderlas…»
P2  Objetivo general: un sistema basado en aprendizaje profundo y VLM, adaptados de modelos
    preentrenados, que asista en el diagnóstico y en la generación de reportes. Una oración dice qué
    se evalúa: el desempeño en la clasificación, si el reporte afirma el diagnóstico correcto y si el
    sistema se ejecuta con recursos convencionales (retoma la restricción de 1.1)   función: define
    ↓ descomposición — el objetivo general se divide en tres específicos
P3  OE1–OE3: los dos primeros corresponden a las dos tareas (clasificar y generar) y el tercero a la
    evaluación en escenarios exigentes                                      función: define
    ↓ ampliación
P4  Tabla objetivo–pregunta–capítulo, presentada en una oración          función: organiza (→ 1.3)
→ Transición a 1.3: la tabla ya remite a los capítulos; 1.3 los describe uno por uno.

Se definen acá: PI1, PI2, OE1–OE3.
Se retoman de antes: las dos cuestiones abiertas y la restricción de hardware (1.1).
Extensión: sin cambios, una página y media con la tabla.
```

## Qué cambia respecto del texto actual

| Dónde | Hoy | Cambio | Motivo |
|---|---|---|---|
| Primera oración | «A partir de las problemáticas planteadas, se establecen los objetivos del presente trabajo, cuya formulación se articula en torno a dos preguntas fundamentales que orientan su desarrollo:» | «Las dos cuestiones planteadas al final de la sección anterior se formulan como las preguntas de investigación del trabajo:» | Retoma el cierre de 1.1 en lugar de repetirlo, presenta primero las preguntas (comentario p26) y saca «fundamentales» (adjetivo de énfasis) |
| Objetivo general | «…con el fin de mejorar la exactitud diagnóstica y agilizar el flujo de trabajo.» | «…con el fin de contribuir a mejorar la exactitud diagnóstica y agilizar el flujo de trabajo.» | El trabajo no mide el efecto clínico; la finalidad se enuncia con su alcance (guía, «Afirmaciones medidas») |
| Oración siguiente | «Se analiza cuán bien clasifica, si el reporte afirma el diagnóstico correcto y si el sistema puede ejecutarse con recursos computacionales convencionales.» | «En particular, se evalúan su desempeño en la clasificación, la correspondencia entre el diagnóstico que afirma el reporte y el correcto, y la posibilidad de ejecutarlo con recursos computacionales convencionales.» | «Cuán bien» es informal |
| Antes de los OE | «Los objetivos específicos son:» | «El objetivo general se divide en tres objetivos específicos. Los dos primeros corresponden a las dos tareas, y el tercero, a la evaluación del sistema:» | Dice cómo se relacionan los OE con el objetivo general y con las dos tareas |
| OE3 | «…como imágenes de otra población o casos en que no tiene seguridad sobre el diagnóstico, analizando su exactitud diagnóstica, la calidad del texto generado y su utilidad práctica, incluido su costo computacional.» | «…como imágenes de otra población o casos en los que el sistema no tiene certeza sobre el diagnóstico, analizando su exactitud diagnóstica, la calidad del texto generado y su costo computacional.» | Sale «utilidad práctica» (decisión del 28/09: no hubo evaluación con especialistas) |

Las preguntas, la tabla y su epígrafe no cambian.

**Preguntas para el autor:**
1. ¿El título pasa a «Preguntas de investigación y objetivos»? Hoy es «Objetivos», pero la sección abre
   con las preguntas, y el título nuevo refleja el orden que pidió el tutor. El label `sec:intro_objetivos`
   se conserva.

---

# Historial

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 1.2 Preguntas de investigación — `sec:intro_preguntas` — I3, I4, D1, M1.6–M1.7

**Mensaje central.** Dos preguntas, una por tarea, concretas y ligadas a las métricas con que se responden
después. Sin hipótesis (D1).

**Extensión: 0.5–0.75 páginas.** Título nuevo: «Preguntas de investigación» (antes «…e hipótesis»,
`sec:intro_preguntas` se mantiene).

**Esqueleto.**
1. **Párrafo de entrada** (2–3 líneas): retoma ¶11 (el problema de investigación) y dice que se traduce en
   dos preguntas, una por tarea, porque las salidas son de naturaleza distinta y se evalúan con criterios
   distintos.
2. **`enumerate` con PI1 y PI2.**
3. **Párrafo de cierre** (2–3 líneas): las preguntas se responden en los Capítulos 4 y 5, y se discuten
   en conjunto en el Capítulo 6. Sin adelantar resultados.

**Redacción propuesta.**

**PI1.** ¿Cómo se compara el desempeño de los modelos visión–lenguaje, tanto generales como especializados
en dermatología, con el de clasificadores visuales supervisados (redes convolucionales y transformers
visuales) en la clasificación de lesiones de piel y en la identificación de melanoma, medido con F1 macro y
sensibilidad macro para la clasificación, y con sensibilidad, especificidad y AUC para el melanoma?

**PI2.** ¿Qué fidelidad diagnóstica alcanzan los reportes generados a partir de la imagen por un modelo
visión–lenguaje ajustado, entendida como la coincidencia entre el diagnóstico que el reporte afirma y el de
referencia de la imagen, y qué calidad descriptiva tienen, entendida como la adecuación del texto a la
lesión que la imagen muestra y medida con métricas de similitud textual y de contenido, considerando ambas
dimensiones por separado?

Cambios respecto de la versión anterior y su porqué: «aporta mejoras reales» y «precisos, completos y
clínicamente relevantes» (no medibles ni separados) se reemplazan por comparaciones ligadas a métricas
(M1.6, M1.7). PI2 separa fidelidad diagnóstica de calidad descriptiva, «dos dimensiones que el propio
documento reconoce como independientes» (M1.7). «Precisos» sale también por la regla de terminología
(«precisión» queda para *precision*).

**Qué se elimina (I4, D1).** H1–H6 y todo el texto que las rodeaba: la distinción entre hipótesis de partida
y exploratorias, «Se plantea tras refutarse…», «Su respaldo es por eso más débil…» y el párrafo sobre el
orden de formulación. **Qué pasa con H3–H6:** los análisis (desbalance, especialización de dominio,
cascada, incertidumbre) se mantienen en los Caps. 4 y 5 como preguntas o análisis que surgen de un
resultado, sin llamarlos hipótesis (M2). **Referencias a H1–H6 que hay que actualizar** al tocar esos
capítulos: `04-Resultados-Clasificacion.tex` l. 12, `05-Resultados-Generacion.tex` l. 13,
`06-Discusion.tex` l. 56–58 (que además remite a `sec:intro_preguntas`).

**Citas:** ninguna.

---

## 1.3 Objetivos — `sec:intro_objetivos` — I5, I6, D2, M1.10–M1.12

**Mensaje central.** Un objetivo general y tres específicos, coherentes con lo que se hizo, y una tabla que
los enlaza con las preguntas y los capítulos.

**Extensión: 1–1.5 páginas** (con la tabla).

**Esqueleto.**
1. **Párrafo de entrada** (1–2 líneas): a partir del problema y de las preguntas se plantea el objetivo
   general y tres objetivos específicos. Se elimina «Los objetivos se enuncian tal como fueron
   formulados…» (p32).
2. **Objetivo general** (un párrafo).
3. **Objetivos específicos** (`enumerate`, con una línea de detalle por objetivo).
4. **Párrafo de presentación de la tabla** (1–2 líneas) + **Tabla** (I6).

Se elimina el párrafo «Dos de esas formulaciones no coinciden…» (D2, p32: «Esto no va»). El balance de lo
cumplido queda en `sec:concl_objetivos`.

**Objetivo general propuesto** (adaptación de M1.10, no copia). Cubre clasificación, generación de reportes,
fidelidad diagnóstica y hardware limitado; deja fuera «mejorar la precisión diagnóstica y optimizar el flujo
de trabajo», que el trabajo no mide:

> Diseñar, implementar y evaluar un enfoque de aprendizaje profundo y de modelos visión–lenguaje,
> adaptados a partir de modelos pre-entrenados, para clasificar lesiones cutáneas y generar reportes
> dermatológicos a partir de imágenes, y analizar su desempeño diagnóstico, la fidelidad diagnóstica de los
> reportes y su viabilidad computacional con recursos de hardware limitados.

**Objetivos específicos propuestos** (sin sugerir entrenamiento desde cero: en todos los casos se
diseñó, implementó y evaluó adaptando modelos pre-entrenados; p32).

- **OE1.** Diseñar, implementar y evaluar, adaptando modelos pre-entrenados, clasificadores de lesiones
  cutáneas basados en redes convolucionales, transformers visuales y modelos visión–lenguaje, para
  identificar posibles melanomas.
  *Detalle:* compara modelos visión–lenguaje generales y especializados con clasificadores visuales
  supervisados sobre el mismo material y mide su desempeño en la clasificación y en la identificación de
  melanoma. Responde la PI1.
- **OE2.** Diseñar, implementar y evaluar, adaptando modelos pre-entrenados, un modelo visión–lenguaje que
  integre información visual y textual para producir un diagnóstico preliminar y reportes de lesiones
  cutáneas.
  *Detalle:* incluye estrategias para que el texto afirme solo el diagnóstico que la evidencia respalda, y
  evalúa por separado la fidelidad diagnóstica y la calidad descriptiva de los reportes. Responde la PI2.
- **OE3.** Evaluar el desempeño de los modelos desarrollados en distintas condiciones, analizando su
  desempeño diagnóstico, la calidad del texto generado y su costo computacional.
  *Detalle:* incluye la generalización a otra población, la calibración de la confianza de las predicciones
  y el tratamiento de la incertidumbre. Contribuye a responder las dos preguntas.

Diferencias con el plan de trabajo: OE2 pasa de «diseñar y entrenar» a «diseñar, implementar y evaluar,
adaptando modelos pre-entrenados»; OE3 abandona «utilidad práctica para el flujo de trabajo» (no hubo
evaluación con especialistas) y «escenarios clínicos» (concretados como generalización, calibración e
incertidumbre, según la decisión de la ficha anterior). Ver pregunta abierta 2.

**Tabla objetivo ↔ pregunta ↔ capítulo (I6, M1.11)** (`tab:intro_objetivos_preguntas`, `tabularx` con
`booktabs`, `\caption` arriba, rotulada «Tabla»):

| Objetivo específico | Pregunta | Se diseña y describe en | Se evalúa y responde en |
|---|---|---|---|
| OE1. Clasificadores de lesiones y de melanoma (CNN, ViT, VLM) | PI1 | Cap. 3, Materiales y métodos | Cap. 4, Resultados de clasificación |
| OE2. VLM para generar reportes | PI2 | Cap. 3, Materiales y métodos | Cap. 5, Resultados de generación |
| OE3. Evaluación en distintas condiciones | PI1 y PI2 | Cap. 3 (protocolo de evaluación) | Caps. 4 y 5 (resultados) y Cap. 6 (discusión y limitaciones) |

Debajo, una línea: el marco conceptual de todo está en el Cap. 2 y el balance de los objetivos en el
Cap. 7. Se mantiene breve para no repetir §1.4 (organización). La tabla solo se incluye si al cerrar los
Caps. 3–5 esas correspondencias siguen siendo ciertas (M1.12: «todo tiene que estar bien ordenado y
autocontenido»).

**Citas:** ninguna.
