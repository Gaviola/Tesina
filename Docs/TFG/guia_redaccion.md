# Guía de redacción de la tesina

Contrato único para la redacción del documento final. Quien escriba una sección —el autor o un
agente— lee esta guía antes de escribir la primera línea, y todo lo que produzca se juzga contra
ella. Las decisiones acá fijadas valen para todos los capítulos: si algo hay que cambiar, se cambia
en este archivo y no sección por sección.

## 1. Circuito de trabajo

Cada sección del documento pasa por cuatro etapas. No se saltea ninguna.

| Etapa | Qué se produce | Quién decide |
|---|---|---|
| 1. Ficha | `fichas/<capitulo>.md`: mensaje central, esqueleto de párrafos, claves de cita, figuras y extensión | El autor aprueba antes de que se escriba prosa |
| 2. Borrador | `borradores/<label>.tex`: la sección redactada, como archivo aparte | Quien redacta; no toca el capítulo |
| 3. Integración | El borrador se empalma en `Chapters/`, se borra el `\pendiente` y se compila | Revisión por diff |
| 4. Cierre | Un commit por sección en la rama del capítulo | El autor |

Sin ficha aprobada no se redacta. La ficha es el punto de control real: es más rápido corregir un
esqueleto de una página que treinta páginas de prosa ajena.

## 2. Reglas para quien redacta

1. **La ficha es el alcance.** No se agregan secciones, subsecciones ni temas que la ficha no
   incluya. Lo que parezca faltar se anota al final del borrador como pregunta abierta.
2. **No se inventa evidencia.** Ningún número, resultado, porcentaje o afirmación empírica puede
   aparecer si no está en las fuentes indicadas en la ficha. Si falta un dato, se deja la marca
   `\pendiente{}` con lo que haría falta medir.
3. **No se inventan referencias.** Solo se citan claves que ya existen en
   `Bibliography/Bibliography.bib` (ver sección 6).
4. **El borrador no toca otros archivos.** Ni `tesina.tex`, ni otros capítulos, ni el `.bib`.
5. **Toda decisión se reporta.** Al terminar, el borrador se entrega con: claves citadas,
   afirmaciones sin respaldo, decisiones tomadas por cuenta propia y preguntas abiertas.

## 3. Voz y estilo

- **Impersonal y descriptiva.** «Se evalúan cuatro arquitecturas», no «evaluamos» ni «el autor
  evalúa». Nunca se habla del autor en tercera persona.
- **El texto es propio.** No se escribe meta-lenguaje sobre el documento ni sobre la plantilla
  («este capítulo fue elaborado a partir de…», «material no desarrollado por el autor»).
- **Párrafos de 4 a 8 líneas**, uno por idea, encadenados. Se evitan las listas de viñetas en el
  cuerpo salvo cuando enumeran elementos realmente paralelos (clases, métricas, configuraciones).
- **Cada sección abre diciendo qué establece** y cierra con lo que deja instalado para la
  siguiente. No se anuncia lo que se va a hacer («en esta sección se describirá…»): se hace.
- **Nada de relleno.** Sin frases de transición vacías, sin recapitulaciones de lo ya dicho, sin
  adjetivos de énfasis («notablemente», «sumamente»).
- **Español neutro formal.** Documentación y documento en español; el código y los nombres de
  variables, en inglés.
- **Los términos en inglés se usan cuando son los corrientes en el área.** *Pipeline*, *array*,
  *prompt*, *zero-shot*, *linear probe*, *grounding*, *hedging*, *bootstrap*, *trade-off* o
  *image captioning* no tienen equivalente castellano instalado; traducirlos dificulta la lectura
  en lugar de facilitarla, así que se usan tal cual. Se prefiere el castellano cuando ya es de uso
  corriente («ajuste fino», «conjunto de datos», «aprendizaje profundo», «atención multi-cabeza»).
- **Cursiva la primera vez en cada capítulo** con `\emph{}`; después, redonda. En títulos de
  sección y en los índices, siempre redonda. Un término que aparece cincuenta veces en cursiva es
  ruido tipográfico.
- **Las siglas se usan libremente una vez introducidas.** La primera aparición en cada capítulo va
  con `\gls{}`, que expande la forma completa; de ahí en más, la sigla sola (VLM, LoRA, RAG, ECE).

## 4. Terminología fijada

La tabla fija decisiones de consistencia, no prohibiciones generales: cuando dos términos son
ambos aceptables, se usa el de la columna izquierda para que el documento no alterne entre los
dos. Está sujeta a cambios; lo que no cambia es que una vez elegido un término, se usa en todos
los capítulos.

| Se usa | No se usa | Nota |
|---|---|---|
| fuga de información entre particiones (*data leakage*) | fuga de datos, contaminación | Se define en la primera aparición (Materiales y métodos); después alcanza «fuga de información» |
| entorno real | producción | |
| partición, subconjunto | *split* | «partición disjunta por lesión» es el nombre del procedimiento |
| modelo visión--lenguaje (VLM) | modelo de lenguaje visual, modelo multimodal (a secas) | El guion es `--` (semirraya) |
| *pipeline* | sistema propuesto, tubería, canal | Nombra la arquitectura completa: clasificador, kNN y generador encadenados. «Sistema» queda para usos genéricos («sistema de apoyo al diagnóstico») |
| exactitud | precisión | «precisión» queda reservada para *precision* |
| sensibilidad macro | *recall* macro, exhaustividad | |
| F1 ponderado, F1 macro | F1-score, puntaje F1 | |
| ajuste fino | *fine-tuning* | El anglicismo solo en la definición inicial |
| conjunto de datos | *dataset* | |
| reporte | informe | Consistencia con el título de la tesina |
| fidelidad diagnóstica | precisión diagnóstica | Es la métrica sin referencia, no una *precision* |

**Prohibido:** la palabra «caveat» en cualquier contexto.

**Números.** Punto decimal, no coma (`0.846`). La plantilla de la UMU no se pronuncia al respecto
y la norma general del español es la coma, pero en el área los resultados se reportan con punto y
el material de experimentación propio ya lo usa en sus 267 valores, sin una sola coma; cambiar de
criterio obligaría a reescribir todas las tablas. Tres decimales en métricas, dos en porcentajes,
desviación con `$\pm$`. No hace falta configurar nada: `babel` con la opción `spanish` solo trata
la coma como separador decimal en modo matemático, y el punto funciona igual dentro y fuera de
`$...$`.

**Acrónimos.** Se declaran en `Matter/05-Acronyms.tex` y se invocan con `\gls{}` en la primera
aparición de cada capítulo. No se redefine un acrónimo ya declarado.

## 5. Extensión

La ficha fija la extensión de cada sección. Como referencia, el documento apunta a 90–110 páginas:
introducción 6–8, marco teórico 25–30, materiales y métodos 20–25, cada capítulo de resultados
25–30, discusión 8–12, conclusiones 4–6.

Las estimaciones de extensión y las fuentes de cada capítulo van como **comentarios LaTeX**
(`% Extensión estimada:`, `% Fuentes:`) al inicio del archivo, nunca en el cuerpo del texto.

## 6. Citas y bibliografía

`Bibliography/Bibliography.bib` es el archivo único y canónico: 72 entradas, claves normalizadas
como `<apellido><año><palabra>` (`vaswani2017attention`, `tschandl2018ham10000`,
`yan2025derm1m`).

- **Solo se citan claves existentes.** Antes de citar se verifica:
  `grep "^@.*{clave," Bibliography/Bibliography.bib`.
- **Las referencias nuevas no se agregan al `.bib`.** Se proponen en `refs_pendientes.md` con
  título, autores, año y DOI o URL, y el autor las incorpora. El `.bib` no se sobrescribe con una
  exportación de Zotero: la biblioteca está incompleta respecto del documento (ver
  `refs_pendientes.md`).
- **Estilo numérico** (`numeric-comp`, bibliografía en orden de aparición):
  - `\cite{clave}` para el caso normal → `[12]`.
  - `\textcite{clave}` cuando el autor es el sujeto de la oración → `Yan et al. [12]`.
  - Varias referencias juntas van en una sola llamada, `\cite{a,b,c}` → `[3-5]`, nunca
    `\cite{a}\cite{b}`.
- **En el marco teórico, toda afirmación sobre el estado del conocimiento lleva cita.** En los
  capítulos de resultados se cita solo para comparar con trabajos ajenos.
- No se cita por autoridad ni se acumulan referencias: cada cita respalda una afirmación concreta.

## 7. Convenciones LaTeX

- **Etiquetas:** `\label{cp:...}` capítulos, `\label{sec:...}` secciones y subsecciones,
  `\label{fig:...}`, `\label{tab:...}`, `\label{eq:...}`. El prefijo temático se conserva
  (`sec:marco_vlm`, `sec:res_gen_cascada`).
- **Referencias cruzadas:** `Capítulo~\ref{cp:marco}`, `Sección~\ref{sec:met_particiones}`,
  `Tabla~\ref{tab:...}`, con tilde para evitar el corte de línea. Nunca «ver arriba» o «más
  adelante» sin `\ref`.
- **Marcas de estado:** `\pendiente{...}` para contenido no escrito. Se elimina al redactar la
  sección. La lista se imprime con `\listadependientes` y solo existe con `docstage=working`.
- **Figuras** en `Figures/`, formato vectorial cuando sea posible, con `\caption` que se entienda
  sin leer el cuerpo del texto y `\label`. Las tablas llevan `\caption` arriba.
- **Código** con `minted` (requiere `-shell-escape`). Fragmentos cortos, solo si aportan.
- **Compilación:** `latexmk -xelatex -shell-escape tesina.tex` desde `Docs/TFG/`.

## 8. Ramas y commits

Un capítulo, una rama: `doc/cap01-introduccion`, `doc/cap02-marco-teorico`, y así. Se ramifica
desde `master` actualizado y se integra cuando el capítulo está cerrado.

- Un commit por sección redactada, con el asunto en imperativo y en español.
- El `.tex` del capítulo y el borrador correspondiente van en el mismo commit.
- **Se compila en la rama en la que se está trabajando**, tantas veces como haga falta: es la única
  forma de ver cómo queda el documento. `tesina.pdf` está versionado y se commitea también ahí.
- El PDF es un artefacto generado, así que su conflicto de merge no se resuelve a mano.
  `.gitattributes` lo marca con el driver `keep-ours`, que toma la versión local sin preguntar;
  **después de un merge que haya tocado capítulos hay que recompilar**, porque el PDF que quedó no
  incluye los cambios de la otra rama. El driver es local a cada clon y se registra una vez:

      git config merge.keep-ours.name "Conserva la version local; el artefacto se regenera recompilando"
      git config merge.keep-ours.driver true
