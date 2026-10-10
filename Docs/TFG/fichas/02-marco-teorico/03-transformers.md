# Ficha 2.3 — Transformers y mecanismos de atención

Sección del `.tex`: `Chapters/02-Marco-Teorico/03-transformers.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.2 Transformers y mecanismos de atención — `sec:marco_atencion`

**Mensaje central.** La atención compara directamente todas las posiciones y sustituye la recurrencia; el
transformer se construye sobre ella y sus dos módulos dan lugar a modelos visuales y de lenguaje distintos.

**Razón de ser.** Todo lo que sigue (ViT, Swin, LLM, VLM) usa esta operación. **Extensión: 1,5 páginas.**

| Contenido | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| Idea de la atención, *tokens* | l. 206–213 | Se elimina «reemplaza el recorrido paso a paso de las redes recurrentes» tal como está (las RNN no se presentaron); se reformula como «frente al procesamiento secuencial de 2.1» | Definición de *embedding* (traída de l. 288–290) al introducir la proyección del token: es la primera vez que se necesita |
| Atención escalada por producto punto | l. 215–225, `eq:marco_atencion`, `fig:marco_atencion` | — | — |
| Atención multi-cabeza | l. 229–232 | — | — |
| Codificador y decodificador | l. 234–239 | Se elimina la oración con referencias adelante a `sec:marco_vit` y `sec:marco_llm_grandes` si sobra (se mantienen: es la transición) | Una oración: **codificación de la posición** (la atención no distingue el orden; se suma un *embedding* de posición), que hoy solo aparece en el ViT (l. 290) |

**Párrafo de transición (C4).** Ideas: la atención es una operación sobre secuencias de *tokens*; según qué
módulo se conserve (codificador o decodificador) y qué se tokenice (parches o palabras), sale una familia
distinta. Se empieza por las imágenes (2.3), donde conviven con las convolucionales.
**Citas:** `vaswani2017attention`, `dosovitskiy2021image`, `brown2020language`.
