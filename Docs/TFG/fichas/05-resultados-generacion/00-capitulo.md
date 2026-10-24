# Ficha del Capítulo 5 — Resultados: generación de reportes y pipeline integrado

**Estado (24/10/2026): redactado entero sin aprobación previa**, por pedido del autor («escribe todo el cap y después
lo reviso entero»), con la estructura del Cap. 4 reorganizado. Cada sección tiene su ficha con el hilo, las fuentes,
las decisiones tomadas y las preguntas para la revisión.

## Hilo del capítulo

Pregunta que responde el capítulo: ¿los reportes que genera un VLM afirman el diagnóstico correcto y describen la
lesión? (PI2, OE2 y la parte del OE3 que toca a la generación: incertidumbre y costo).

Viene de: el Cap. 4 cierra con que el diagnóstico no puede salir del generador y lo fija Swin-Tiny a través de la
cascada (`sec:res_clasif_discusion`). El Cap. 3 deja la cascada, la recuperación y el ruteo (`sec:met_pipeline`), la
consistencia diagnóstica oficial (`sec:met_eval_generacion`), las fuentes de comparación y la línea base sin
generador (`sec:met_referencias`) y el costo (`sec:met_costo`).
Deja instalado: el diagnóstico del reporte viene del clasificador; la descripción, del generador; el ruteo decide
cuánto afirma el pipeline. Para el Cap. 6: falta de especialistas, errores compartidos, una semilla en el ancla, costo.

```
Intro   Qué contiene y cómo se organiza; convenciones: prueba por lesión, métrica oficial (solo reporte, estricta),
        un reporte por imagen sin desvío, bootstrap pareado, citas en inglés
         ↓ necesidad: antes de la cascada, ¿qué escribe un generador solo?
5.1     Generación sin diagnóstico: Nivel 1 (estilo de la referencia) y consistencia sin anclaje (LLaVA enumera,
        Mini elige mal, SkinVL repite «tinea corporis»)
         ↓ consecuencia: el diagnóstico tiene que venir de afuera
5.2     Cascada: consistencia = exactitud de Swin (el generador copia); por clase sobre la diagonal; la imagen no
        cambia el diagnóstico pero sí la descripción; fallas; recuperación no reemplaza al clasificador
         ↓ necesidad: la cascada afirma también los errores; ¿se pueden reconocer?
5.3     Ruteo: la concordancia separa (0.915 frente a ~0.57); el par cubre 0.847; 102 de 230 errores compartidos
        (38 melanomas afirmados como otra clase); pipeline = línea base sin generador; ejemplos
         ↓ ampliación: comparar los generadores y su costo
5.4     Comparación entre generadores (Mini = SkinVL en fidelidad, Mini > LLaVA; SkinVL describe la mitad); control
        Mini v3; costo (sec:res_costo)
5.5     Estado del arte: MM-Skin (BLEU frente a BERTScore), SkinGPT-4, RULE, Khan
5.6     Discusión: PI2 en sus dos partes
→ Cap. 6: discusión transversal y limitaciones.
```

## Secciones, archivos y labels

| Sec. | Título | Archivo | Label | Pág. |
|---|---|---|---|---|
| Intro | — | `00-capitulo.tex` | `cp:res_gen` | 0.7 |
| 5.1 | Generación de reportes sin diagnóstico | `01-generacion-directa.tex` | `sec:res_gen_directa` | 3 |
| 5.2 | Cascada clasificador–generador | `02-cascada.tex` | `sec:res_gen_cascada` | 6.5 |
| 5.3 | Ruteo por concordancia y pipeline completo | `03-ruteo.tex` | `sec:res_gen_incertidumbre` | 4.5 |
| 5.4 | Comparación entre los generadores | `04-comparacion-generadores.tex` | `sec:res_gen_comparacion` | 3.5 |
| 5.5 | Comparación con el estado del arte | `05-estado-del-arte.tex` | `sec:res_gen_estado_arte` | 2 |
| 5.6 | Discusión de los resultados de generación | `06-discusion.tex` | `sec:res_gen_discusion` | 1 |

Unas 19 páginas. Los archivos del esqueleto anterior se renombraron (`03-ensamble-cascada` → `02-cascada`,
`08-ensamble-incertidumbre` → `03-ruteo`, `10-costo-computacional` → `04-comparacion-generadores`, `11-discusion` →
`06-discusion`) o se borraron (razonamiento, taxonomía, SkinVL, ablaciones, recuperación y ejemplos pasan a ser
subsecciones). Se conserva `sec:res_costo`, que cita el Cap. 6.

## Decisiones tomadas (24/10/2026)

1. **Estructura del Cap. 4**: el análisis sigue a la cascada con Swin-Tiny y Mini-VLM (configuración principal); los
   otros generadores se nombran donde difieren y se comparan una vez (5.4); una sola sección de literatura (5.5).
2. **Una cifra clave por párrafo**; las demás en tablas y en cinco figuras nuevas (`Codigo/scripts/figuras_cap5.py`)
   más una figura de ejemplos con imágenes de HAM10000 (CC BY-NC 4.0, la misma licencia que ya cita el Cap. 3).
3. **Métrica oficial** en todo el capítulo (solo reporte, búsqueda estricta). Lo que no estaba calculado así
   (ablaciones, taxonomía con categorías del marco, consistencia por clase frente a la sensibilidad del ancla,
   errores compartidos, vecino equivocado, comparaciones entre generadores) se recalculó con
   `Codigo/scripts/cap5_derivados.py` → `outputs/results/cap5_derivados.json`.
4. **Taxonomía con las categorías de `tab:marco_fallas` (Cap. 2)**: una expresión de reserva junto al
   diagnóstico correcto («consistent with nevus») se cuenta como «correcto, con reservas» y no como *hedging*, porque
   el marco define el *hedging* como evitar comprometerse. `error_taxonomy.py` la contaba como *hedging* (por eso la
   experimentación decía que el *hedging* persistía con el oracle).
5. **«Solo la clase verdadera»** (consistencia exclusiva de `rag_les_resul`) se informa como columna auxiliar para
   mostrar que la consistencia sin anclaje de LLaVA-Med viene de enumerar clases.
6. **Sin DermLIP como fuente** hasta que terminen los reportes `full_dermlip_oficial` (\pendiente en 5.2). La
   condición vieja (`full_dermlip`, exactitud 0.38) no aparece.
7. **Mini-VLM v3 solo como control** (5.4.1), con los brazos parciales declarados (Swin 963, sin anclaje 372).

## Respuestas del autor (24/10/2026)

1. Cap. 3 corregido: variantes de la cascada en `sec:met_referencias`, regla de fallas en `sec:met_eval_generacion`,
   fila nueva en `tab:met_experimentos` y `\ref` de `sec:met_ruteo` a `cp:res_gen`; 5.2 remite a esas secciones.
2. Nivel 1 de Mini-VLM v2 en SkinCoT: enviado (jobs 1183331–1183334).
3. DermLIP: se espera a los jobs y se agrega al terminar.
4. Memoria: se mide en la A30 (`measure_vlm_memory.py`, jobs 1183335–1183337), como en el Cap. 4.
5. Figura de ejemplos: queda como está.

## Preguntas para la revisión del capítulo

1. **Cap. 3 (no se tocó):** (a) no describe las ablaciones sin imagen y con diagnóstico equivocado ni la regla de la
   taxonomía; 5.2 las explica en una oración cada una. ¿Se agrega un párrafo corto a `sec:met_referencias` y una fila a
   `tab:met_experimentos`? (b) `sec:met_ruteo` dice que la hipótesis de la concordancia «se pone a prueba en el
   Capítulo~\ref{cp:res_clasif}», pero se prueba en 5.3: habría que cambiar el `\ref` a `cp:res_gen`.
2. **Nivel 1 de Mini-VLM (principal) en SkinCoT:** no existe. ¿Se envían tres tramos a `short` (457 reportes, ~2 h de
   GPU)? Mientras tanto queda un `\pendiente` en 5.1.
3. **DermLIP en la cascada:** al terminar los jobs 1183274–1183301, se agrega la columna, los puntos de la figura y un
   párrafo (\pendiente en 5.2). Si no terminan el 27/10, ¿se quita la mención o se usa la condición vieja como
   «clasificador débil»?
4. **Memoria de los generadores**: es la de los pesos en bf16 (parámetros × 2 bytes), no una medición. ¿Alcanza?
5. **Figura de ejemplos**: el segundo reporte repite la instrucción («The final clinical report should include…»). Se
   eligió a propósito como defecto que las métricas no ven. ¿Se prefiere otro ejemplo?
