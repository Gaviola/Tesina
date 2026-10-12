# Ficha 3.1 — Definición de las tareas

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/01-tareas.tex` (nuevo). Labels: `sec:met_tareas`.

## Hilo conductor

Pregunta que responde la sección: ¿qué le pide el trabajo a cada modelo, con qué entrada y qué salida, y bajo qué restricción de cómputo?
Viene de: la introducción del Cap. 3, que retoma las limitaciones del estado del arte (`sec:estado_arte_posicion`, `tab:marco_brechas` del Cap. 2). De las cuatro brechas de esa tabla, tres se convierten en tareas o en restricciones de esta sección: la comparación sin protocolo común (→ PI1), el texto evaluado por su parecido con una referencia (→ PI2) y el cómputo fuera del alcance de un equipo sin infraestructura (→ restricción). La cuarta, la incertidumbre sin integrar, no es una tarea: es la decisión de afirmar o derivar, que corresponde al *pipeline* (3.8).
Deja instalado: tres tareas con sus identificadores (T1 clasificación, T2 detección de melanoma, T3 generación del reporte), con entrada, salida, pregunta y objetivo; las siete clases y su gravedad; la restricción de una GPU de consumo y la decisión de adaptar modelos preentrenados con LoRA en lugar de preentrenar un VLM. 3.2 (flujo de trabajo) usa las tres tareas para ordenar las etapas; 3.3 usa las clases para describir el conjunto; 3.4 usa la gravedad para justificar las métricas.

```
(sin subsecciones: un párrafo de entrada, una lista de tres tareas y tres párrafos; P1–P5 en total)
P1  Las tres tareas salen de las dos preguntas de la introducción y de las brechas del estado del arte.
    Primera oración: lo orienta y lo retoma (Viene de)                                   función: define
    ↓ necesidad — cada tarea necesita una definición formal: qué entra, qué sale, qué pregunta responde
P2  Lista de tres ítems, alternativas paralelas (guía §3): T1 clasificación; T2 detección de melanoma,
    derivada de T1; T3 generación del reporte. Cada ítem: entrada, salida, PI y OE           función: define
    ↓ necesidad — la salida de T1 y la base de T2 son siete categorías: cuáles son y cuánto pesa cada una
P3  Inventario de HAM10000: siete categorías, agrupadas por gravedad (benignas; AKIEC; malignas). Es el
    párrafo ya escrito que se mueve de 3.3. Cierra con el enlace a 3.4 (el costo de cada confusión)   define · justifica
    ↓ consecuencia — las tres tareas corren en un equipo de una GPU de consumo: esa restricción las condiciona
P4  Restricción de cómputo: una GPU de consumo para entrenar y ejecutar todo. Por eso no se preentrena
    un VLM: se adaptan modelos preentrenados con LoRA (`hu2021lora`)                     justifica
    ↓ limitación — ninguna de las tres tareas cubre la histopatología
P5  Fuera de alcance: histopatología. Cierre: las tres tareas se resuelven con un plan de trabajo
    que se itera (transición a 3.2)                                                       limita
→ Transición a 3.2: «Las tres tareas no se resolvieron en un orden fijo: cada resultado obligó a
  revisar la siguiente decisión, y la Sección~\ref{sec:met_metodologia} describe ese ciclo.»

Se definen acá (y no se vuelven a definir): T1, T2, T3 (con sus entradas, salidas, PI y OE); las siete
categorías de *HAM10000* y su gravedad; la detección de melanoma como binario derivado de T1 (no localización ni segmentación); la restricción de una GPU de consumo; la
decisión de no preentrenar un VLM y de adaptar modelos con LoRA; la exclusión de histopatología.
(El contenido de la gravedad de las siete categorías se define acá; los nombres de las siglas, en 05-Acronyms.)
Se retoman de antes (solo se nombran, con \ref): PI1 y PI2 y OE1–OE3 (`sec:intro_objetivos`); las
brechas (`sec:estado_arte_posicion`); CNN, ViT, VLM y LoRA (`sec:marco_vision`, `sec:marco_vlm`,
`sec:marco_llm_lora`); fidelidad diagnóstica y calidad descriptiva (`sec:marco_rep_ejes`).
Remisiones hacia adelante: métricas y costos asimétricos (`sec:met_seleccion`, 3.4); partes del reporte
(`sec:met_generacion`, 3.7); hardware (3.2); conjuntos y partición (3.3).
Extensión: cuatro párrafos (P1, P3, P4, P5) y una lista de tres ítems (P2), unas 2 páginas (orientativo 1.5–2 p., ficha del Cap. 3).
```

## Subsecciones

Ninguna. La sección es un bloque, como la definición formal del ejemplo (pp. 37–38 del PDF de la tesina de ejemplo, págs. impresas 37–38).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Las tres tareas del trabajo, derivadas de PI1 y PI2 y de tres brechas del estado del arte. Primera oración propuesta: «Las limitaciones de la Sección~\ref{sec:estado_arte_posicion} se traducen en tres tareas que el trabajo define de manera formal.» | PI1 y PI2: `Chapters/01-Introduccion/02-objetivos.tex` líneas 5–10. Brechas: `Chapters/02-Marco-Teorico/10-estado-arte.tex`, `tab:marco_brechas` (después de la línea 590). Conexión PI1 con «en particular el melanoma»: misma fuente, PI1. | ninguna |
| P2 | Lista de tres ítems. Cada ítem: nombre en negrita al comienzo; entrada; salida; pregunta; objetivo. **T1 Clasificación** (entrada: imagen dermatoscópica; salida: una de las siete categorías de HAM10000; PI1; OE1). **T2 Detección de melanoma** (entrada: la misma imagen; salida: decisión binaria melanoma frente a resto, derivada de la salida de T1; PI1, en particular el melanoma; OE1, «identificar posibles melanomas»). **T3 Generación del reporte** (entrada: imagen de la lesión; salida: texto con descripción de la lesión e impresión diagnóstica; PI2; OE2). La detección no es localización ni segmentación: la lesión ya es el objeto de la imagen. | OE1, OE2: `02-objetivos.tex` líneas 19–27. «Identificar posibles melanomas»: OE1 (misma fuente). T2 derivada y «no localización»: `planes`: `Codigo/docs/ideas/cierre_experimentacion_plan_20260805.md` §1.8, líneas 30–39 (screening = binario melanoma-vs-resto, cierra el gap terminológico) y §2 B1, líneas 59–61. «Dermatoscópicas ya recortadas y centradas en una única lesión»: mismo plan §1.8, líneas 33–36; **a verificar** con la documentación de HAM10000 (no se leyó en esta ficha). Partes del reporte: `Chapters/03-Materiales-Metodos/05-generacion-reportes.tex` líneas 4–5 (solo se nombran aquí; el texto se mueve a 3.7). | `tschandl2018ham10000` (verificada, `Bibliography.bib` línea 760) para HAM10000 como conjunto de referencia. |
| P3 | Inventario: siete categorías de HAM10000 (MEL, NV, BCC, AKIEC, BKL, DF, VASC), con la gravedad (benignas: NV, BKL, DF, VASC; AKIEC: premalignas y carcinomas in situ; malignas: MEL y BCC). Cierra con el enlace a 3.4: la gravedad determina el costo de cada confusión (`\ref{sec:met_seleccion}`). Se mueve el párrafo ya escrito. | Prosa ya escrita: `Chapters/03-Materiales-Metodos/02-datos-particiones.tex` líneas 7–12 (subsección HAM10000, párrafo único). Siglas y nombres en español: `Matter/05-Acronyms.tex` líneas 22–28. Gravedad: misma prosa, con la cita de Tschandl. | `tschandl2018ham10000` (verificada). |
| P4 | Restricción de cómputo: cada modelo se entrena y se ejecuta en una GPU de consumo, sin infraestructura de alto rendimiento. Como uno de los objetivos es ejecutar todo en esa GPU, no se preentrena un VLM: se adaptan modelos preentrenados con LoRA, que entrena un número reducido de parámetros. Los detalles de la GPU van en 3.2 (`\ref`). | Restricción: `Chapters/01-Introduccion/01-contexto-motivacion.tex` líneas 75–79 («una sola GPU», «commodity hardware»). Decisión LoRA y no preentrenar: `fichas/01-introduccion/01-contexto-motivacion.md` líneas 201–205 («restricción de cómputo y no pre-entrenar; LoRA → Cap. 3»). Brecha de cómputo: `tab:marco_brechas` (Cap. 2, última fila). Objetivo general: `02-objetivos.tex` línea 13 («adaptados a partir de modelos preentrenados»). | `hu2021lora` (verificada, línea 310). LoRA en el marco: `sec:marco_llm_lora` (Cap. 2, sin cita nueva). |
| P5 | Fuera de alcance: la histopatología (cortes de tejido), que las tres tareas no cubren. Cierre: las tres tareas se resuelven con un plan iterativo (transición a 3.2). | Histopatología fuera: `Chapters/03-Materiales-Metodos/00-capitulo.tex` línea 32 (`\pendiente`, handoff del Cap. 1, commit f520295). Ninguna mención en el texto actual del Cap. 1; el Cap. 6 limita la extensión a histopatología (`Chapters/06-Discusion/07-limitaciones.tex` línea 15). | ninguna |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado (existe / a adaptar / a generar) |
|---|---|---|---|
| — | Ninguna. La sección no lleva figura. Si se quiere un cuadro con T1–T3 (entrada, salida, PI, OE), ver pregunta 7. | — | — |

## Prosa ya escrita que se conserva

- **Párrafo de HAM10000** (`Chapters/03-Materiales-Metodos/02-datos-particiones.tex` líneas 7–12): se mueve a P3 de 3.1 casi tal cual. Cambios: (a) `HAM10000` en cursiva (`\emph{HAM10000}`, guía §3, conjuntos de datos); (b) la primera oración se conserva porque ya dice de qué trata («El clasificador asigna cada imagen a una etiqueta de un inventario cerrado…»), pero conviene que mencione T1 para que el párrafo quede atado a la lista; (c) `\gls{mel}` … `\gls{vasc}`: es la primera aparición de estas siglas en el documento (verificado: ni los Caps. 1 y 2 las usan), así que el `\gls{}` va acá; (d) la última oración («Esa gradación determina cuánto cuesta cada confusión…») se conserva con su `\ref{sec:met_seleccion}`.
- **En 02-datos-particiones.tex** queda solo el `\subsection{HAM10000}` con su label `sec:met_ham` y el `\pendiente` de composición y distribución (eso es 3.3). **El label `sec:met_ham` no se mueve**: el `\ref` del Cap. 2 (`01-fundamentos.tex:161`, «los nevos superan varias veces a los melanomas») apunta a la distribución de clases, que queda en 3.3.
- **No se mueve** el párrafo de `05-generacion-reportes.tex` (partes del reporte): va a 3.7 (`07-generacion-reportes.tex`). En 3.1 solo se nombra la tarea.

## Lo que va al apéndice

Nada. El inventario de clases con su tamaño va en 3.3 (tabla de tamaños por clase y partición). Las grillas de hiperparámetros y los *prompts* van a los apéndices A y B, fuera de esta sección.

## Lo que NO va en esta sección (y dónde está)

- Partes del reporte (descripción e impresión diagnóstica, con su fundamento): **3.7**.
- Composición de HAM10000, distribución de clases, desbalance, imágenes por lesión, partición disjunta por lesión: **3.3**.
- Rol de cada conjunto (HAM10000 para entrenar y medir fidelidad, SkinCaRe solo como fuente de pares imagen–texto, HIBA para generalización): **3.3**. Es el handoff del Cap. 1 que el `\pendiente` de `00-capitulo.tex` menciona, y se resuelve en 3.3.
- Costos asimétricos de confusión, métrica principal, de selección y oficial de generación, fidelidad diagnóstica frente a validez clínica: **3.4**.
- Hardware concreto (RTX 4070 local, TOKO con RTX 4080, Mendieta con A30, SLURM) y, si se aprueba, las cifras de memoria: **3.2**.
- Definiciones de CNN, ViT, VLM, LoRA, CLIP, fidelidad diagnóstica y calidad descriptiva: **Cap. 2**, solo con `\ref`.
- Resultados o desempeños de ningún tipo (guía del Cap. 3, regla 3).
- Evaluación en escenarios distintos (OE3): **3.4 y 3.9**; no es una tarea.

## Preguntas abiertas para el autor

1. **Mapeo maligno/benigno (AKIEC).** El plan de cierre (`cierre_experimentacion_plan_20260805.md` §2 B1, líneas 59–61) define maligno = {MEL, BCC, AKIEC} y benigno = {NV, BKL, DF, VASC}, y marca «confirmar mapeo con el tutor». La prosa existente dice que AKIEC reúne lesiones premalignas y carcinomas in situ, y que solo MEL y BCC son malignas. Propuesta: 3.1 define solo el binario melanoma frente a resto. El binario maligno/benigno, con AKIEC incluido o no, se define en 3.4 cuando el tutor confirme el mapeo.
2. **Entrada de T3.** ¿Entra solo la imagen, o también la salida del clasificador (grounding por recuperación y diagnóstico de la cascada de 3.8)? OE2 dice «integre información visual y textual para producir un diagnóstico preliminar y el reporte»; la definición formal de T3 depende de que se resuelva esto.
3. **Salida de T1.** ¿La clase predicha, o la clase con un vector de probabilidades? Propuesta: la clase predicha en la definición formal, y las probabilidades (y la calibración) en 3.4 y 3.5, donde se usan.
4. **Dónde se define «detección».** El Cap. 1 (`fichas/01-introduccion/01-contexto-motivacion.md` líneas 191–194) dejó la definición operativa para «Cap. 2 §2.8 o Cap. 3». Propuesta: 3.1, como definición formal de T2; el Cap. 2 solo menciona la binarización como concepto (`08-evaluacion.tex` línea 48). Confirmar. La justificación del desfase entre el título de la tesina («detección») y lo desarrollado («clasificación») (plan §1.8) va en P4, o se omite si el tutor lo considera innecesario.
5. **Cifras de hardware.** La ficha del Cap. 1 (línea 185–186) manda al Cap. 3 «los 12–36 GB, la clase de GPU y el argumento…». Propuesta: 3.1 dice solo «una GPU de consumo»; las cifras van en 3.2. Confirmar.
6. **Histopatología.** La exclusión viene del `\pendiente` del Cap. 3, no de un párrafo del Cap. 1. Confirmar que se afirma en 3.1 y no en la introducción del Cap. 1 (que ya no tiene alcance; ficha del Cap. 1, línea 169).
7. **Cuadro resumen de T1–T3.** ¿Se agrega una tabla (tarea, entrada, salida, PI, OE) además de la lista? El ejemplo no la tiene. Propuesta: no, para no repetir la lista (guía §3, «Concisión»).
8. **Test externo HIBA y espacio de clases.** El plan (A5, líneas 53–55) mapea SCC→AKIEC y se evalúa HIBA en el espacio de clases común. ¿Se dice en 3.1 (una oración en P3) o en 3.3? Propuesta: 3.3.

## Números que no pude verificar

- «Dermatoscópicas ya recortadas y centradas en una única lesión» (HAM10000 y HIBA): viene del plan §1.8. No se leyó la documentación de los conjuntos. **A verificar.**
- Ningún otro número nuevo. «Siete clases» y la gravedad se leen de la prosa existente (`02-datos-particiones.tex`) y de `05-Acronyms.tex`.

## Decisiones tomadas por cuenta propia

- **D1 — Formato de la definición formal.** Lista de tres ítems con el nombre en negrita al comienzo (guía §3, «Alternativas paralelas en lista»), en lugar de la frase destacada en cursiva del ejemplo. La guía prohíbe los títulos de párrafo en negrita, y la lista tiene la misma función de forma sin romper la guía.
- **D2 — Orden.** Tareas → inventario de clases → restricción de cómputo → exclusión y transición. El inventario va después de la lista porque T1 se define con esas clases; la restricción va después porque es la razón de la decisión de LoRA, no de las tareas.
- **D3 — T2 es el binario melanoma frente a resto.** El binario maligno/benigno no se define acá (pregunta 1).
- **D4 — Relación con los objetivos.** T1 → PI1 y OE1; T2 → PI1 (en particular el melanoma) y OE1 («identificar posibles melanomas»); T3 → PI2 y OE2. OE3 (evaluación en escenarios) no es una tarea: se remite a 3.4 y 3.9.
- **D5 — Labels.** `sec:met_tareas` es nuevo en `01-tareas.tex`. `sec:met_ham` se queda en 3.3 (ver «Prosa ya escrita»).
- **D6 — Commit de la sección.** El párrafo se quita de `02-datos-particiones.tex` en el mismo commit que escribe 3.1, porque es la única forma de no tener dos copias (guía §1, «No hay borradores en archivos aparte»; §8, «quitar de otra sección una definición repetida» debe decirlo el mensaje del commit).
- **D7 — Número de párrafos.** Cuatro párrafos más la lista de tres ítems (P1–P5), dentro de las 1.5–2 páginas previstas. Alcanza para las tres definiciones, el inventario y la restricción sin repetir la motivación de la Introducción.
- **D8 — Preguntas abiertas aplicadas.** Se aplicaron las propuestas de las preguntas 1 (solo el binario melanoma frente a resto en 3.1), 3 (clase predicha en T1; probabilidades en 3.4 y 3.5), 4 (detección = T2 derivada, definida en 3.1), 5 (solo «una sola GPU de consumo» en 3.1; detalle en 3.2.1, `sec:met_infra`), 6 (histopatología afirmada en 3.1) y 7 (sin tabla T1–T3). La pregunta 2 (entrada de T3) no tiene propuesta y queda como `\pendiente`. La pregunta 8 (HIBA) no se toca en 3.1.
- **D9 — Dato no verificado.** La oración «dermatoscópicas ya recortadas y centradas en una única lesión» (HAM10000 y HIBA) no se escribió: queda como `\pendiente` en T2 hasta confirmarla en la documentación del conjunto.
- **D10 — Desfase título y clasificación.** La pregunta 4 propone explicar el desfase entre «detección» (título) y «clasificación» (lo desarrollado) en P4, pero el plan de P4 no lo incluye. No se agregó; queda a decisión del autor.
- **D11 — Ajustes de la prosa conservada.** En el párrafo de las partes del reporte se cambió «las dos tareas del problema» por «lo que T3 debe producir», porque la sección define tres tareas. En el párrafo de HAM10000 se agregó el `\emph{}` al conjunto y se mantuvo el resto. LoRA se nombra sin `\gls{}` porque ya se declaró en el Capítulo 2 (`sec:marco_llm_lora`); VLM tampoco se vuelve a declarar porque lo hace el Capítulo 1.
