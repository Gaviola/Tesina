# Ficha 2.9 — Sesgo, robustez y generalización

Sección del `.tex`: `Chapters/02-Marco-Teorico/09-sesgo-robustez.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.9 Sesgo, robustez y generalización — `sec:marco_generalizacion`

**Mensaje central.** El desempeño medido en una distribución no se transfiere sin más a otra: cambian los
dominios, las subpoblaciones y los rasgos espurios, y esas diferencias producen disparidades medibles.

**Razón de ser.** Justifica evaluar fuera de la distribución de entrenamiento y perturbar las imágenes; es el
fundamento de la robustez de 2.8.3. **Extensión: 2 páginas.**

**Se conserva (l. 902–954):** cambio de distribución (`koh2021wilds`), modalidad, atajos (`kim2024transparent`),
tono de piel (`groh2021neural`, `daneshjou2022disparities`), disparidad en la colaboración
(`groh2024learningaided`), población (`jones2022intelligence`).

| Cambio | Ubicación | Razón |
|---|---|---|
| Se elimina «HAM10000 es dermatoscópico y SkinCaRe es de fotografía clínica, de modo que toda comparación entre los dos conjuntos arrastra esa diferencia de dominio» | l. 917–919 | Dato práctico de los conjuntos (p43, A1). Queda el principio: la diferencia de modalidad es un cambio de dominio |
| Se elimina «El trabajo lo usa solo como test… se describen en la Sección~\ref{sec:met_protocolo}» | l. 952–954 | Decisión propia. Se conserva la frase de `riccilara2023dataset` como ejemplo de evidencia local en un país, sin adjetivos de primicia (guía §3: «que sus autores presentan como…») |
| Se elimina «Un mapa de Grad-CAM que marca la tinta y no la lesión es el síntoma visible de ese atajo» o se deja como ejemplo general | l. 927–928 | Ya está en 2.8.3 |
| Se elimina el detalle de qué modelo o conjunto: se mantienen Fitzpatrick17k y DDI porque son la evidencia | — | Es literatura, no decisión propia |
| **Agregar subsección de robustez** (un párrafo, «Robustez frente a variaciones de adquisición») | nuevo | Las causas de la pérdida de desempeño ante perturbaciones (iluminación, resolución, compresión) se explican acá; la medición está en 2.8.3. Cita `hendrycks2019benchmarking` |
| Título pasa a «Sesgo, robustez y generalización» | — | M2.1 |

**Párrafo de transición a 2.10.** Con los conceptos de clasificación, generación, incertidumbre, evaluación y
generalización ya presentados, se puede revisar la literatura con un criterio: qué problema aborda cada trabajo,
con qué datos y protocolo lo evalúa y qué deja sin resolver.
