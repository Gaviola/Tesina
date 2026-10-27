# Ficha del Capítulo 6 — Discusión general

**Estado: redactado entero sin aprobación previa**, por pedido del autor («escribirlo entero y después lo reviso»), como
los Caps. 4 y 5. Cada sección tiene su ficha con el hilo, las fuentes, las decisiones tomadas y las preguntas para la
revisión.

## Hilo del capítulo

Pregunta que responde el capítulo: ¿qué significan, en conjunto, los resultados de la clasificación y de la
generación, y hasta dónde valen?

Viene de: los balances de 4.6 y 5.6, breves por pedido del tutor (revisión de los Caps. 4 y 5), que remiten acá la
discusión transversal. El material argumentativo que salió de ellos estaba como comentarios en estos archivos y quedó
integrado en la prosa (ver «Origen del material»).
Deja instalado (para el Cap. 7): respuestas a PI1 y PI2; especialización > modalidad; el clasificador fija la
fidelidad y el generador redacta; el ruteo como apoyo y no reemplazo; lecciones de evaluación; viabilidad en una GPU
de consumo; limitaciones.

```
Intro  Qué contiene y en qué orden (como las intros de los Caps. 4 y 5)
        ↓
6.1    PI1 (no, para los VLM usados como tales; sí para la representación especializada con cabeza) y
       PI2 (diagnóstico sí, en la medida del clasificador; descripción parcial) → las dos respuestas se encadenan
        ↓ necesidad: ¿qué explica la primera respuesta?
6.2    Especialización frente a modalidad: SkinCAP y gris → especialización; control de representación;
       SkinVL muestra que la especialización generativa depende del formato; literatura
        ↓ consecuencia: el diagnóstico sale de un clasificador
6.3    División del trabajo: consistencia = exactitud de la fuente; implicación de diseño y de evaluación;
       ruteo = tercera tarea (0.849 → 0.870, atribuible al ruteo); decisiones respaldadas; costo del reparto
        ↓ necesidad: la redacción no indica si el diagnóstico es correcto
6.4    Fidelidad frente a validez clínica: qué mide cada métrica; descripción verificada en parte; expertos
       escasos también en la literatura; ruteo como señal; errores compartidos → apoyo, no reemplazo
        ↓ ampliación: lecciones sobre cómo medir
6.5    Lecciones: partición, regla de decisión, variación entre ejecuciones, prueba sobre la métrica que
       selecciona, métricas de texto (estilo y enumeración)
        ↓ ampliación: comparación con la literatura en costo
6.6    Hardware: costo medido; cómputo de la literatura; qué parte de la brecha es escala (clasificación no,
       contrastivo sí, generación no ordena la fidelidad)
        ↓ consecuencia: lo que la restricción deja fuera
6.7    Limitaciones: amenazas por tipo de validez (lista); especialistas; ancla de una ejecución; decisiones
       sin evaluar (lista); respaldo independiente o exploratorio → Cap. 7
```

## Secciones, archivos y labels

| Sec. | Título | Archivo | Label | Pág. |
|---|---|---|---|---|
| Intro | — | `00-capitulo.tex` | `cp:discusion` | 0.5 |
| 6.1 | Respuesta a las preguntas de investigación | `01-respuesta-preguntas.tex` | `sec:disc_preguntas` | 1.3 |
| 6.2 | Especialización de dominio frente a modalidad | `02-dominio-modalidad.tex` | `sec:disc_especializacion` | 1.3 |
| 6.3 | División de trabajo entre clasificador y generador | `03-clasificador-generador.tex` | `sec:disc_division` | 1.8 |
| 6.4 | Fidelidad diagnóstica y validez clínica | `04-fidelidad-validez.tex` | `sec:disc_validez_clinica` | 1.5 |
| 6.5 | Lecciones metodológicas | `05-lecciones-metodologicas.tex` | `sec:disc_lecciones` | 1.7 |
| 6.6 | Viabilidad en hardware accesible | `06-hardware-accesible.tex` | `sec:disc_hardware` | 1.2 |
| 6.7 | Limitaciones y amenazas a la validez | `07-limitaciones.tex` | `sec:disc_limitaciones` | 2 |

Unas 10 páginas, sin figuras ni tablas: la tabla de aportes ya está en 5.6 (`tab:res_gen_aportes`) y se cita.

## Origen del material de 4.6 y 5.6

| Párrafo | Va a |
|---|---|
| 4.6 p1 (respuesta a PI1) | 6.1 P1–P2 |
| 4.6 p2 (arquitectura, ejecuciones, umbral, partición) | 6.5 P1–P4 |
| 4.6 p3 (HIBA, calibración) | 6.7, validez externa |
| 4.6 p4 (el diagnóstico no sale del generador) | 6.3 P1 |
| 5.6 p1 (descripción) | 6.1 P3 y 6.4 P2 |
| 5.6 p3 (el reparto como aporte) | 6.3 P3 |
| 5.6 p4 (decisiones respaldadas) | 6.3 P4 |
| 5.6 p5 (plantilla diferencial, umbral de melanoma) | 6.7, lista de decisiones |
| 5.6 p6 (errores compartidos, derivación) | 6.4 P4–P5 y 6.7 |

## Decisiones tomadas

- Se conserva la estructura de siete secciones del esqueleto. Sin hipótesis: el Cap. 1 solo plantea PI1 y PI2.
- Sin semillas: «ejecución de referencia» y «variación entre ejecuciones», como en los Caps. 3–5.
- Las frases atenuadas en los Caps. 4 y 5 se mantienen atenuadas acá («puede atribuirse», «rara vez corrige»,
  «coincide con»); «toda la ganancia proviene» del comentario de 5.6 no se usó.
- Las comparaciones con la literatura van dentro de cada sección temática (6.2, 6.4, 6.5, 6.6), sin sección propia.
- Del documento de experimentación se tomaron las amenazas y limitaciones, pero no los números (eran de v3) ni el
  tiempo de cola en el clúster (dato interno), ni «generación sobre el test original», que ya no aplica.

## Preguntas para la revisión

1. 6.1: ¿alcanza con dos párrafos por pregunta, o el tutor espera una tabla PI → respuesta → evidencia?
2. 6.7: ¿las dos listas (amenazas y decisiones sin evaluar) están bien, o se prefieren párrafos?
3. 6.6: la afirmación de que un generador más grande «posiblemente no elevaría la consistencia» es una conjetura
   apoyada en el oracle; ¿se deja?
