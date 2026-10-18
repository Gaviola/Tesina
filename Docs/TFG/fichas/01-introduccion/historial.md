# Ficha del Capítulo 1 — Historial

Registro del plan y las decisiones del 26 y el 28/09/2026. **No rige**: lo vigente está en `00-capitulo.md`.
Las referencias a líneas y párrafos (¶) son las de esa versión.

Contrato de contenido de la **nueva versión** del capítulo. Reemplaza al plan del 2026-09-26, que
describía la versión ya escrita en `Chapters/01-Introduccion.tex`. Esa versión se reescribe según la
revisión del tutor (códigos en `tareas_revision_cap1-2.md`: **A1–A16**, **M1.1–M1.12**, **p27–p35**, y
las decisiones **D1** y **D2**). Cada sección declara su mensaje, el esqueleto de párrafos, las claves de
cita y la extensión. Lo que no está acá no se escribe; lo que falte se anota como pregunta abierta.

**Estado: propuesta pendiente de aprobación del autor.** No se redacta prosa hasta que se apruebe.

**Estructura del capítulo (cuatro secciones, antes cinco):**

| Sección | Antes | Ahora |
|---|---|---|
| Intro del capítulo | resumen técnico con fases y GPU | presentación de contenido y organización, sin detalle técnico (I1, p27) |
| 1.1 Contexto y motivación | 7 párrafos sin hilo | 11 párrafos en 4 bloques con hilo conductor (I2, A3) |
| 1.2 Preguntas de investigación | PI1, PI2 + H1–H6 | solo PI1 y PI2 reformuladas (I3, I4, D1) |
| 1.3 Objetivos | textuales del plan + párrafo de discrepancias | objetivo general adaptado (D2) + OE1–OE3 revisados + tabla objetivo–pregunta–capítulo (I5, I6) |
| ~~1.4 Alcance y delimitación~~ | 4 párrafos | eliminada (I7) |
| 1.4 Organización del documento | «Responde la PI1» | «Este capítulo presenta…» (I8, p33) |

**Extensión total: 6–7 páginas.** Baja respecto de las 8–10 anteriores porque salen Alcance (1–1.5 p), las
hipótesis (1 p) y el párrafo de hardware y de «modelos que ya existen» (0.5 p). La guía (§5) y el
comentario del `.tex` dicen 8–10; ver pregunta abierta 1.

**Reglas que gobiernan esta ficha** (T2, guía de redacción; a incorporar a la guía):
- ningún término se usa antes de haberlo presentado (A1);
- cada párrafo retoma el anterior y lleva al siguiente (A3, A7);
- nada de metodología, datasets ni algoritmos en la introducción (A1);
- la intro de capítulo dice qué trae y cómo se organiza, sin detalle técnico ni figuras (p27, p35).

---

## Intro del capítulo (párrafo de apertura) — I1, p27

**Mensaje.** Qué contiene el capítulo y cómo se organiza. Nada técnico.

**Extensión: 1 párrafo de 4–5 líneas.** Sin figura.

**Esqueleto (una sola pieza).**
1. Este capítulo presenta el problema que motiva el trabajo: la dificultad de diagnosticar y de
   documentar lesiones de piel, y el aporte posible de la inteligencia artificial.
2. A partir de ese problema se formulan las preguntas de investigación y se enuncian los objetivos.
3. El capítulo cierra con la organización del documento.

**Se saca** (p27): el codificador visual, el LLM, las «dos fases», la GPU y «en sus dos partes» («¿el
cuerpo tiene dos partes?»). Los VLM, las fases y el hardware aparecen recién donde se motivan.

**Redacción sugerida** (a ajustar al redactar): «Este capítulo presenta el problema que motiva el
trabajo, las preguntas de investigación y los objetivos que lo organizan, y describe cómo se estructura
el resto del documento. Primero se plantea el problema clínico del diagnóstico de lesiones de piel y de su
documentación, y qué puede aportar la inteligencia artificial. A partir de ahí se formulan las preguntas y
se enuncian los objetivos, y se cierra con la organización de los capítulos siguientes.»

**Citas:** ninguna.

---



## Orden de redacción

1. §1.1 (la que argumenta; la más larga). 2. §1.2 y §1.3. 3. Organización, al final, cuando los títulos de los
capítulos no se muevan. 4. Intro del capítulo, después de escribir todo lo demás. La tabla de §1.3 al último,
con los Caps. 3–5 cerrados.

## Claves de cita del capítulo (verificadas contra `Bibliography.bib`, 2026-09-28)

Usadas en la nueva versión: `sung2026global`, `nci2026melanoma`, `freeman2026global`,
`dinnes2018dermoscopy`, `tschandl2019comparison`, `arndt2017tethered`, `esteva2017dermatologistlevel`,
`dosovitskiy2021image`, `liu2021swin`, `magalhaes2024systematic`, `kreouzi2024learning`,
`jones2022intelligence`, `radford2021learning`, `liu2023visual`, `li2023llavamed`,
`daneshjou2022disparities`, `groh2021neural`, `loria2020cutaneous`. Todas existen.

Salen del capítulo: `zhou2023skingpt4`, `yan2025derm1m`, `yilmaz2025resourceefficient` (a Cap. 2/§2.10 o
Cap. 3), `riccilara2023dataset`, `tschandl2018ham10000`, `shen2025skincare` (Cap. 3), `hu2021lora` (Cap. 3).

No existen en el `.bib`: `kittler2002diagnostic`, `vestergaard2008dermoscopy`, `sinsky2016allocation`,
mencionadas en la ficha anterior (versión del 2026-09-26, resuelta con `dinnes2018dermoscopy` y
`arndt2017tethered`). No usarlas. `dosovitskiy2021image` y `liu2021swin` se incorporan para ¶7; verificar
que sean las claves que el Cap. 2 usa para ViT y Swin.

## Preguntas abiertas para el autor

1. **Extensión.** La propuesta queda en 6–7 páginas, por debajo de las 8–10 fijadas. ¿Se ajusta la guía (§5)
   y el comentario del `.tex`, o se prefiere ampliar ¶1–¶11 con más datos?
2. **OE3 y «utilidad práctica».** El plan de trabajo la incluía y no se evaluó con especialistas. ¿Se
   elimina (como en la propuesta) o se mantiene con redacción que la deje como línea futura?
3. **Métricas dentro de PI1 y PI2.** Se nombran F1 macro, sensibilidad macro, especificidad, AUC, y
   «métricas de similitud textual y de contenido». ¿Son las que usan finalmente los Caps. 4 y 5? Si el Cap. 5
   evalúa con métricas de entidades diagnósticas, PI2 conviene nombrarlas.
4. **«Fidelidad diagnóstica» en PI2.** El término queda con una glosa entre comas, aunque la regla A1
   pide no usar términos antes de presentarlos. Se justifica porque el término es el del propio tutor
   (M1.7, M1.10), pero ¿se prefiere la glosa o una redacción sin término técnico («si el diagnóstico que
   afirma el reporte es el correcto»)?
5. **Figura 1.1.** ¿Se acepta que se traslade al Cap. 2 (§2.6), o se prefiere eliminarla o dejarla en el
   Cap. 1?
6. **Hipótesis.** D1 las elimina. La propuesta del tutor (M1.4, M1.5) admitía conservar H1 y H2; si el
   tutor las pide, se vuelve a esa opción (D1).
7. **Cifras de `arndt2017tethered` y `dinnes2018dermoscopy`.** Son de atención primaria general y de dermatoscopía
   en manos no especialistas. ¿Se dejan ambas como respaldo de ¶4 y ¶6 con la aclaración de alcance?

---

## Decisiones tomadas (vigentes)

1. **El presupuesto de memoria de GPU es 12--36 GB, no 12--24** (Cap. 3 lo declara; el Cap. 1 ya no lo
   menciona).

2. **§1.1 ¶1 afirmaba algo falso y quedó corregido.** El melanoma es menos de una cuarta parte de los casos y
   casi la mitad de las muertes: GLOBOCAN 2024 da 58 398 muertes por melanoma y 58 721 por el resto de los
   cánceres de piel. La fuente es `sung2026global` (GLOBOCAN 2024, publicado el 08/07/2026), que superó a
   `bray2024global` (GLOBOCAN 2022). Detalle en `refs_pendientes.md`. La nueva redacción del dato dice «la
   última estimación de GLOBOCAN, publicada en 2026, para el año 2024» (p27).

3. **Variabilidad interobservador: no se afirma una cifra de concordancia.** El párrafo se limita a que el
   desempeño depende de la experiencia y varía entre observadores, que es lo que sostiene
   `tschandl2019comparison`.

4. **Los capítulos llevan párrafo de apertura** (21/09/2026), ahora con el contenido de «Intro del capítulo»:
   qué trae y cómo se organiza, sin detalle técnico.

5. **El margen de mejora se focaliza en el 15 % de diagnósticos no localizados** (77/10/5; 10+5 = 15 %).

6. **Patrones de escritura automatizada** (guía §3): pasada de estilo al revisar la prosa. Se conserva el guion
   doble de «visión--lenguaje».

7. **«acá» se reemplaza por «en este trabajo»** o se reestructura.

8. **El «quinto tumor más frecuente» se verificó** contra la fact sheet de GLOBOCAN 2024 (IARC).

9. **Referencias anteriores a 2020** (`esteva2017dermatologistlevel`, `tschandl2019comparison`): van fechadas y
   presentadas como punto de partida, no como el desempeño alcanzable hoy (guía §6).

10. **H2 dejaba de decir «precisos»** (término reservado para *precision*): al eliminarse las hipótesis
    (D1) deja de aplicar; la regla se mantiene en PI2 y en los objetivos.

## Historial

- **2026-09-25.** LoRA sale de §1.1; Argentina se funde con generalización; SkinCaRe aclarado en Alcance;
  hipótesis «emergentes» pasan a «exploratorias»; apertura reescrita según el plan; organización en lista
  `description`. Esos cambios quedan superados por la revisión de abajo.

## Revisión del tutor (2026-09-28)

Origen: devolución del tutor sobre la versión del 2026-09-26 (`feedback/feedback_cap1_y_2.md`,
`REVISADO_TFG_Gaviola_cap1-2.pdf`) y decisiones D1 y D2 de `tareas_revision_cap1-2.md`.

**Qué cambia y por qué.**

| Cambio | Código | Motivo |
|---|---|---|
| Intro del capítulo: de resumen técnico a presentación de contenido y organización; se sacan codificador visual, LLM, fases, GPU y «sus dos partes» | I1, p27, T2 | «Las intros no llevan detalle técnico»; los términos aparecen donde se motivan |
| Contexto y motivación rehecho en 4 bloques con hilo conductor (problema clínico → limitaciones del diagnóstico y documentación → IA → problema de investigación); cada párrafo retoma el anterior | I2, A3, M1.1, M1.2, p28–p30 | «Parece un informe de una materia»: falta conexión entre párrafos |
| Dato de densidad de dermatólogos antes de la dermatoscopía; se elimina «El diagnóstico humano tampoco está resuelto»; dos retrasos (interpretación, documentación) → dos tareas | A3, M1.2, p28 | El hilo sigue la detección temprana y sus factores |
| El hito de 2017 deja de abrir el bloque de IA y pasa a ejemplo dentro de ¶7; se abre con «métodos computacionales, entre ellos redes neuronales» | A3 | «Eso no interesa en ese punto» |
| «Dos temas de trabajo aún abiertos» en un solo párrafo, y párrafo nuevo que conecta las dos tareas | I2, p29, M1.3, A10 | No basta resolverlas por separado |
| Se eliminan «En dermatología esos modelos ya existen» y el párrafo de hardware como eje; el hardware queda en una frase | p30, M1.10 | «Explicando cosas al voleo»; «es metodología» |
| Se eliminan la definición operativa de «detección» y el párrafo de las dos condiciones del reporte (queda en dos oraciones) | A1, I2 | Términos sin introducir; definición en Cap. 2/3 |
| Figura 1.1: se quita del capítulo y se propone trasladarla al Cap. 2 (§2.6) | p27, p35 | La intro no lleva figuras |
| Sección «Preguntas de investigación e hipótesis» → «Preguntas de investigación»; se eliminan H1–H6 | D1, I4, A2, M1.4, M1.5, p31 | Una hipótesis exige un análisis exhaustivo que el trabajo no plantea; formuladas a posteriori no son hipótesis; H3–H6 pasan a análisis de los Caps. 4 y 5 (M2) |
| PI1 y PI2 reformuladas, ligadas a métricas; PI2 separa fidelidad diagnóstica de calidad descriptiva | I3, M1.6, M1.7 | Más concretas |
| Objetivo general adaptado de la propuesta del tutor; se elimina el párrafo de discrepancias | D2, I5, M1.10, p32 | «Esto no va»; el objetivo ya menciona clasificación, reportes, fidelidad diagnóstica y hardware limitado |
| OE1–OE3 sin «entrenar»; todos «diseñar, implementar y evaluar» adaptando modelos pre-entrenados | I5, p32 | Nunca se creó un modelo nuevo |
| Tabla objetivo–pregunta–capítulo | I6, M1.11, M1.12 | Facilita seguir el hilo de la tesina |
| Se elimina la Sección 1.4 Alcance y delimitación; su contenido se reparte | I7, A1, A2, p32–p33 | «TODO ESTO NO VA»: datasets, fidelidad vs validez, cómputo y LoRA → Cap. 3; limitaciones → Cap. 6 |
| Organización del documento con «Este capítulo presenta…» | I8, p33, T2 | Sin «Responde la PI1» |

**Consecuencias en otros capítulos (M1–M4).** Cap. 3 recibe datasets, definición de detección, fidelidad
diagnóstica vs validez clínica, cómputo y LoRA. Cap. 6 recibe las limitaciones que estaban en Alcance.
Caps. 4, 5 y 6 dejan de hablar de hipótesis (l. 12, l. 13, l. 56–58). `\ref` que hay que actualizar:
`sec:intro_alcance` (eliminada), y las de `sec:intro_preguntas` que hablan de hipótesis.

**Lo que no cambia.** Las cifras verificadas de §1.1 (GLOBOCAN, NCI, densidad de dermatólogos, registro
argentino, historia clínica electrónica), las referencias que las sostienen y las decisiones de
terminología: «reporte» = informe clínico, «exactitud» y no «precisión», decimales con punto, voz
impersonal, sin «caveat», sin gerundio de consecuencia.

## Decisiones del autor sobre las preguntas abiertas (2026-09-28)

1. **Extensión:** no hay límite. El capítulo tiene la extensión que necesite; la guía §5 queda como
   referencia orientativa.
2. **OE3:** se elimina «utilidad práctica», porque no hubo evaluación con especialistas.
3. **PI1 y PI2:** se nombran familias de métricas y no la lista completa. Redacción aprobada:
   - **PI1.** ¿Cómo se compara el desempeño de modelos visión–lenguaje generales y especializados con el de
     clasificadores visuales supervisados en la clasificación de lesiones de piel y en la detección de melanoma?
   - **PI2.** ¿Qué fidelidad diagnóstica y qué calidad descriptiva alcanzan, por separado, los reportes que
     genera un VLM ajustado a partir de la imagen?
4. **«Fidelidad diagnóstica»:** se presenta con palabras en el bloque del problema de investigación (¶10–¶11),
   donde se dice que un reporte tiene que afirmar el diagnóstico correcto y describir la lesión que se ve. Así
   PI2 ya no usa un término sin presentar y no necesita glosa.
5. **Figura 1.1:** sale del Cap. 1 y pasa al Cap. 2, §2.6.2.
6. **Hipótesis:** se eliminan (D1).
7. **`arndt2017tethered` y `dinnes2018dermoscopy`:** se mantienen, con la aclaración de alcance en el texto.
