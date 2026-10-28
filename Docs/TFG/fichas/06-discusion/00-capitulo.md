# Ficha del Capítulo 6 — Discusión general

**Estado: reestructurado y redactado entero tras la revisión del autor** (28/10). La primera versión (siete
secciones) seguía el orden de los resultados y repetía sus cifras. Esta versión se organiza por argumentos, cada uno
con una conjetura propia que cruza los Caps. 4 y 5.

## Hilo del capítulo

Pregunta que responde el capítulo: ¿qué explica, en conjunto, lo que se midió en la clasificación y en la generación,
y hasta dónde vale?

Viene de: los balances de 4.6 y 5.6, que enuncian los hallazgos sin interpretarlos.
Deja instalado (para el Cap. 7): dónde está la especialización de un VLM; por qué el generador transcribe; la
concordancia como predicción selectiva y sus límites; qué limita el desempeño (datos y evaluación, no escala, salvo
en el preentrenamiento contrastivo); limitaciones. **Las respuestas directas a PI1 y PI2 pasan al Cap. 7**
(material guardado como comentario en `Chapters/07-Conclusiones/01-conclusiones-generales.tex`).

```
Intro  Qué interpreta el capítulo y en qué orden; las respuestas a las PI se enuncian en el Cap. 7
        ↓
6.1    Representación y decisión: la especialización está en la representación; los generativos «ven»
       (la descripción cambia con la imagen) pero no deciden la clase → el cuello de botella es el paso
       a la clase. Depende del uso: como clasificador autónomo, no; como codificador, se acerca
        ↓ consecuencia: los generativos ceden la decisión… ¿a qué?
6.2    Texto frente a imagen: en los dos capítulos, cuando compiten, gana el texto (prompt, diagnóstico
       inyectado, vecinos). Conjetura: viene del modelo de lenguaje base (el ajuste nunca vio diagnósticos).
       Consecuencias: el generador transcribe (diseño y evaluación por componente) y no es segunda opinión;
       la descripción se adapta al diagnóstico
        ↓ necesidad: la señal de confianza tiene que venir de fuera del generador
6.3    Concordancia como predicción selectiva: cobertura 0.80, riesgo selectivo 0.085 frente a 0.153.
       Funciona por la heterogeneidad de los predictores, pero sus errores coinciden ~3 veces más que si
       fueran independientes (comparten los datos). Tensión: consistencia ≈ exactitud (domina NV) frente a
       la prioridad clínica del melanoma. Apoyo, no reemplazo
        ↓ ampliación: si el límite no está en el generador ni en el ruteo, ¿dónde está?
6.4    Datos, evaluación y escala: arquitectura y tamaño pesan menos que partición, regla, variación y métrica;
       la escala explica la brecha solo en el preentrenamiento contrastivo; la restricción de cómputo es
       compatible con la fidelidad
        ↓ delimita
6.5    Validez y limitaciones: qué miden las métricas; amenazas por tipo (lista); alcance; ancla de una
       ejecución; decisiones sin evaluar (lista); respaldo independiente o exploratorio → Cap. 7
```

## Secciones, archivos y labels

| Sec. | Título | Archivo | Label |
|---|---|---|---|
| Intro | Discusión general | `00-capitulo.tex` | `cp:discusion` |
| 6.1 | Especialización de la representación y decisión diagnóstica | `01-representacion-decision.tex` | `sec:disc_representacion` |
| 6.2 | El peso del texto frente a la imagen en los generadores | `02-texto-imagen.tex` | `sec:disc_texto_imagen` |
| 6.3 | La concordancia como predicción selectiva | `03-concordancia-selectiva.tex` | `sec:disc_concordancia` |
| 6.4 | Datos, evaluación y escala como límites del desempeño | `04-datos-evaluacion-escala.tex` | `sec:disc_limites` |
| 6.5 | Validez de las conclusiones y limitaciones | `05-validez-limitaciones.tex` | `sec:disc_limitaciones` |

## Decisiones tomadas

- **Sin repetir resultados.** Cada sección abre con la pregunta que discute; las cifras aparecen solo cuando un
  argumento las necesita, con `\ref` a donde se midieron.
- **Cifras derivadas nuevas** (solo en 6.3, marcadas como cálculo sobre cifras ya presentadas): cobertura 0.80 y
  riesgo selectivo 0.085 (1 204 afirmados, 102 errores); 158 imágenes con los dos predictores equivocados frente a
  unas 50 esperables si sus errores fueran independientes (0.153 × 0.219 × 1 503). Fuentes: `sec:res_gen_concordancia`
  (230 errores, 102 afirmados), `sec:res_gen_rag` (171 y 72), `tab:res_dermlip` (kNN 0.781).
- **Conjeturas marcadas** («una explicación posible», «posiblemente»), cada una con su explicación alternativa.
- **Sin futurología** (guía §3): lo no evaluado se enuncia como «no se evaluó», no como beneficio esperable. La
  conjetura del generador más grande se reemplazó por una cota medida: con el oracle, Mini-VLM ya nombra el
  diagnóstico en 0.999 de los reportes.
- McNemar frente a *bootstrap* queda en una oración (6.4): responden preguntas distintas.
- Las 400 imágenes de las variantes se remiten a 3.7 y 5.2; en 6.5 solo su consecuencia (intervalos más amplios).
- Semillas: solo «ejecuciones» y «ejecución de referencia».
