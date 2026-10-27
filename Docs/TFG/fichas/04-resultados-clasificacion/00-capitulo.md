# Ficha del Capítulo 4 — Resultados: clasificación diagnóstica y detección de melanoma

**Estado (24/10/2026): aprobada por el autor.** Contrato del capítulo. Ninguna sección se redacta hasta que el
autor apruebe esta ficha y la ficha de la sección (guía §1).

Reemplaza la ficha del 18/10. La estructura sigue la revisión del tutor del Cap. 3 (21/10, guía §3, «Capítulo de
metodología»): los resultados replican `tab:met_experimentos` y cada comparación va en la sección de su experimento.
Lo que cambia está en «Cambios respecto de la ficha del 18/10».

## Hilo del capítulo

Esquema original (18/10); la estructura vigente es la de la tabla de secciones y la de «Reorganización (24/10/2026)».

Pregunta que responde el capítulo: ¿clasifica un VLM las lesiones dermatoscópicas, y en particular el melanoma, tan
bien como un clasificador supervisado, y se sostiene el desempeño de los clasificadores fuera de la prueba? (PI1,
OE1 y la parte del OE3 que toca a la clasificación: otra población, perturbaciones, calibración, interpretabilidad
y costo.)

Viene de: el Cap. 3 deja los modelos y su configuración (3.3 supervisados, 3.4 VLM), la selección y las pruebas
estadísticas (3.7, `sec:met_seleccion` y `sec:met_estadistica`), las evaluaciones complementarias (3.8,
`sec:met_complementarios`) y la tabla de experimentos, cuya última oración remite a este capítulo.
Deja instalado: el clasificador de referencia (Swin-Tiny), el punto de operación para melanoma y la conclusión de
que un VLM generativo no aporta el diagnóstico. El Cap. 5 los usa en la cascada y en el ruteo.

```
Intro    Qué contiene el capítulo y cómo se organiza (por contenido, sin «responde la PI1»); todo número es de la
         prueba de la partición por lesión, con la configuración elegida en validación; media ± sd con tres semillas
          ↓ necesidad: antes de evaluar a un VLM hace falta saber cuánto rinde un clasificador supervisado
4.1      Clasificadores supervisados: los cuatro con el mismo procedimiento, sensibilidad por clase, ensamble,
         pruebas entre ellos y comparación con la literatura; subsecciones con las funciones de pérdida y con el
         efecto de la fuga de información
          ↓ ampliación: de las siete clases a la de mayor costo clínico
4.2      Detección de melanoma: AUC, sensibilidad y especificidad con el umbral fijado en validación,
         comparación con la literatura
          ↓ contraste: con esa referencia, ¿clasifica igual un VLM?
4.3      Clasificación con VLM: los generativos con las cuatro estrategias y el colapso; los controles de la
         imagen gris y de las fotografías clínicas, y por qué el colapso no se explica por el desbalance; DermLIP
         con sus cuatro usos y el control con Swin-ImageNet; McNemar con Holm sobre los 21 pares; literatura
          ↓ necesidad: la prueba es de la misma fuente que el entrenamiento; ¿se sostiene el clasificador fuera de ella?
4.4      Evaluaciones complementarias: generalización (HIBA), robustez, calibración, interpretabilidad y costo,
         una subsección corta cada una
          ↓ cierre
4.5      Discusión: qué muestran los resultados respecto de PI1 y por qué el diagnóstico del pipeline viene
         del clasificador; la discusión que cruza clasificación y generación queda para el Cap. 6
→ Cap. 5: un generador que no discrimina necesita que el diagnóstico venga de afuera.
```

## Secciones, fuentes y archivos

| Sec. | Título | Archivo | Label | Ext. | Fuentes |
|---|---|---|---|---|---|
| Intro | — | `00-capitulo.tex` | `cp:res_clasif` | 0.5 p. | — |
| 4.1 | Clasificadores supervisados y detección de melanoma | `01-clasificadores-supervisados.tex` | `sec:res_supervisados` | 8 p. | `lesion_split_report.json` (`ganadores`, `sweep`, `melanoma`, `melanoma_semillas`, `legacy_y_desbalance`), `densenet_vit_moderna_report.json`, `statistical_tests_les_v2.json` (pares entre supervisados), `classifier_ensemble_les/`, `per_class_les/`; fuga: `leakage_analysis.json` |
| 4.2 | Evaluaciones complementarias del clasificador | `02-evaluaciones-complementarias.tex` | `sec:res_complementarios` | 5 p. | HIBA: `hiba_por_modalidad.json`; robustez: `robustness/robustness_summary.json`; calibración: `lesion_split_report.json` (`calibracion`), `calibration_les/`; interpretabilidad: `interpretability_les/` |
| 4.3 | Clasificación con modelos visión--lenguaje (tres subsecciones: generativos y colapso, controles, DermLIP) | `03-clasificacion-vlm.tex` | `sec:res_vlm` | 5 p. | `mini_vlm/v2/`, `llava_med/v2/`; `*_likelihood_noimage_*`; `*_likelihood_clinical_*`; `dermlip/dermlip_split_eval.json`, `embeddings/` |
| 4.4 | Comparación entre los clasificadores y costo | `04-comparacion-modelos.tex` | `sec:res_comparacion` | 3 p. | `statistical_tests_les_v3.json`, `densenet_vit_moderna_report.json` (Holm, 21 pares), `cost/cost_comparison_v3.json` |
| 4.5 | Comparación con el estado del arte | `05-estado-del-arte.tex` | `sec:res_estado_arte` | 2.5 p. | Tablas del Cap. 2; `Docs/tabla_resultados_sota/` (v34) |
| 4.6 | Discusión de los resultados de clasificación | `06-discusion.tex` | `sec:res_clasif_discusion` | 1 p. | secciones anteriores |

Total orientativo: unas 21 páginas. Archivos renombrados al aprobarse la ficha (24/10).

Todas las fuentes de la tabla están en `Codigo/outputs/results/` o `Codigo/docs/resul/`. La prueba de la partición
por lesión es la misma de 1 503 imágenes que la de la partición aleatoria (`split_lesion_resul_20260926.md` §2), así
que los resultados de los VLM, que no se ajustan con *HAM10000*, valen sin repetirse.

## Cambios respecto de la ficha del 18/10

| # | Cambio | Motivo |
|---|---|---|
| C11 | Diez secciones pasan a cinco, en el orden de `tab:met_experimentos`. «Estado del arte» (4.5 vieja) y «Calibración y significancia» (4.6 vieja) desaparecen: cada comparación con la literatura y cada prueba estadística van en la sección de su experimento | Revisión del tutor del Cap. 3 (21/10), guía §3: «los resultados replican esa estructura» |
| C12 | Funciones de pérdida y fuga de información son subsecciones de 4.1. Generalización, robustez, calibración, interpretabilidad y costo son subsecciones de 4.4, como en 3.8 | Pedido del autor (24/10): no dar sección propia a experimentos cortos |
| C13 | El «re-diagnóstico del colapso» (4.3 vieja) entra a 4.3 nueva. Lo de que no es el desbalance se argumenta con resultados de la misma sección (colapso ya en *zero-shot*, a una clase distinta según modelo y estrategia), sin método aparte | Decisión del autor (24/10) |
| C14 | Entra el control con fotografías clínicas de *SkinCAP*; su procedimiento se agregó a 3.4 (commit e821d86) | Decisión del autor (24/10) |
| C15 | Sin hipótesis H1–H4: el Cap. 1 ya no las tiene (D1 del Cap. 1). Se habla de PI1 y de los objetivos | Cap. 1 vigente |
| C16 | La «Discusión» final queda, con ese nombre, pero de una página: la discusión transversal es el Cap. 6 | Tutor (14/09): el cierre se llama «Discusión»; Cap. 6 existe |
| C17 | Se agrega el costo de los clasificadores (parámetros, tiempo por imagen, imágenes por segundo) | `tab:met_experimentos`: el costo de los clasificadores va al Cap. 4 |

### Cambios anteriores que siguen vigentes (ficha del 18/10)

- **C1–C2.** DenseNet121 y ViT-B/16 entran con la configuración de su familia y tres semillas. Con el mismo
  procedimiento, ViT-B/16 empata con Swin y ConvNeXt, y DenseNet121 queda abajo en F1 macro y sensibilidad macro
  (*bootstrap*) sin diferencia en McNemar con Holm. Las corridas con la receta anterior no aparecen.
- **C3.** Sin Wilcoxon: la sensibilidad por clase se compara de forma descriptiva y McNemar se corrige con Holm sobre
  21 pares (`sec:met_estadistica`). `statistical_tests_les_v2.json` trae Wilcoxon, pero no se usa.
- **C4.** Sin maligno frente a benigno: la detección es solo MEL frente al resto (3.1).
- **C5.** Los VLM generativos no se ajustaron sobre *HAM10000*; la estrategia de ajuste fino usa el *checkpoint* de
  generación entrenado con *SkinCaRe*. No hay fuga que declarar.
- **C7.** 15 de 21 pares son significativos con Holm, todos los que incluyen un modelo *zero-shot*; ningún par entre
  supervisados lo es (`densenet_vit_moderna_resul_20261017.md` §3).
- **C9.** Rigen las reglas de la guía para todo el documento: sin fechas, revisiones del tutor ni iteraciones viejas;
  solo resultados finales; método y teoría se nombran con `\ref`.
- **C10.** Mini-VLM ajustado se reporta con el *checkpoint* v2 (LoRA solo en el codificador visual), la
  configuración principal de 3.5. La clasificación con v3 no se espera; el control v3 es de generación (Cap. 5).

## Alcance y decisiones heredadas

1. **Fuente única: la partición disjunta por lesión.** La partición aleatoria aparece solo en la subsección de la
   fuga de información y, si hace falta, en la inflación de los métodos sobre DermLIP (4.3).
2. **El Cap. 4 no explica cómo se obtuvo nada.** Receta, búsqueda, umbral y pruebas se nombran con `\ref` al Cap. 3.
   Si un número necesita su regla, se dice en una oración con `\ref` a la sección que la define.
3. **Media ± sd de tres semillas** cuando existen (los cuatro supervisados y el ensamble). Las funciones de pérdida y
   los VLM tienen una semilla y se reportan sin desvío.
4. **Selección en validación, lectura en la prueba.** Ninguna conclusión elige un modelo mirando la prueba.
5. **Swin-Tiny es el clasificador de referencia**: mayor F1 macro medio en validación con las tres semillas entre los
   dos de la búsqueda (0.781 ± 0.018 frente a 0.740 ± 0.027 de ConvNeXt; `lesion_split_report.json`, `ganadores`).
   Con la semilla 42 sola, ConvNeXt queda apenas arriba (0.770 frente a 0.766). Ver pregunta 2. El ensamble es
   Swin + ConvNeXt.
6. **Guía completa**, en particular para resultados: primera oración que orienta; cifras solo las que sostienen el
   argumento y el resto en tablas; tres decimales en métricas, dos en porcentajes, `$\pm$` para el desvío; adjetivos
   de grado con referencia; tablas y figuras citadas en el párrafo que las precede; en resultados se cita solo para
   comparar con trabajos ajenos; afirmaciones con su alcance («en esta prueba», «con una semilla»).
7. **Terminología** (guía §4): «exactitud», no «precisión»; «reporte» solo para el informe clínico; «sensibilidad
   macro»; «fuga de información».

## Redacción de 4.2 a 4.5 e introducción (24/10/2026)

El autor pidió escribir el resto del capítulo de una pasada, con sus fichas, y revisarlo entero al final. Cada sección
tiene su commit y su ficha, con las decisiones tomadas y las preguntas para la revisión. La introducción describe el
capítulo por su contenido y fija las convenciones de las cifras (prueba de la partición por lesión, configuración
elegida en validación, media ± desvío con tres semillas; pruebas, umbral y evaluaciones complementarias con la
semilla 42).

Preguntas para la revisión del capítulo, reunidas de las fichas:

- 4.2: ¿curva ROC de Swin con los dos puntos de operación? (no existe; la tabla alcanza).
- 4.3: ¿DermLIP sobre *SkinCAP* (0.454) como contraste del control clínico? Exige una oración en 3.4.
- 4.4: ¿regenerar la figura de Grad-CAM con rótulos en castellano?

La pregunta 1 de abajo quedó resuelta en 4.3: la figura solo tiene los modelos sin ajuste y no se usa.

## Preguntas abiertas

1. ¿La figura `classification_summary_les.png` usa Mini-VLM v2 ajustado? Si no, se regenera o se arma la tabla sin
   figura (se verifica en la ficha de 4.3).
2. **Elección de Swin en 3.6 y 3.7.** 3.6 dice que Swin es «el de mayor F1 macro en validación», pero 3.7
   (`sec:met_seleccion`) solo define cómo se elige la configuración dentro de cada modelo, no entre modelos. La
   afirmación vale con la media de las tres semillas y no con la semilla 42 sola. Propuesta: en 3.6, «el de mayor F1
   macro medio en validación con las tres semillas», y en 4.1 dar los dos valores.

## Reorganización (24/10/2026)

El autor encontró el capítulo difícil de seguir por la cantidad de cifras y porque cada subsección recorría los
cuatro modelos. Se acordó: (1) las cuatro arquitecturas se comparan una vez y el análisis sigue con Swin-Tiny,
nombrando a las demás solo donde se comportan distinto; (2) como regla, una cifra clave por párrafo y el resto en
tablas y figuras (seis figuras nuevas, `Codigo/scripts/figuras_cap4.py`); (3) una sola sección de comparación con
la literatura (4.5) y una de comparación entre familias con el costo (4.4). Estructura nueva: 4.1 supervisados
(con melanoma), 4.2 evaluaciones complementarias, 4.3 VLM, 4.4 comparación entre clasificadores, 4.5 estado del
arte, 4.6 discusión.

## Revisión externa (25/10/2026)

Revisión de los Caps. 4 y 5 por otro agente (`agent_feedback_cap_4_5.md`), aceptada por el autor con una segunda
opinión. Cambios en este capítulo:

- **Convención de melanoma:** el cuerpo del capítulo usa la media de las tres semillas (0.623 → 0.796), como el resto
  de las tablas; la curva ROC y las pruebas usan la semilla 42, que es la que ancla los reportes del Cap. 5 (0.701).
  La intro lo declara.
- **Correcciones de datos:** el IC de LLaVA-Med no incluye 1/7 (0.145–0.168); los 15 pares significativos lo son en
  McNemar, y la excepción en sensibilidad macro es DenseNet121–DermLIP (250 frente a 85 aciertos discordantes);
  la fuga se mide como prueba completa (0.870) menos grupo limpio (0.804), y las 66 imágenes restantes comparten
  lesión solo con la validación; DermLIP «sin ajuste sobre HAM10000» (no figura entre las fuentes de Derm1M) en vez
  de «no vio HAM10000»; «ningún VLM sin una cabeza entrenada».
- **Estructura:** 4.1 se titula «Clasificadores supervisados y detección de melanoma» para que el melanoma aparezca
  en el índice; 4.3 se parte en tres subsecciones; 4.4 suma «y costo» al título y termina con la transición a 4.5;
  el puntero al costo del Cap. 5 pasa a 4.6.
- **Tablas:** latencia (una imagen) y rendimiento (lote de 32) separados en el costo; umbral de Holm explicado;
  «Sin etiqueta» y proporción entre paréntesis en las tablas de VLM; la fila con pesos de la calibración aclarada.
- **Cursivas:** primera vez en el capítulo en cursiva y después redonda (guía §3), aplicado con un script.

## Revisión del tutor (26/10/2026)

Feedback en `feedback/cap4_5/feedback_cap_4_5.md`. Aplicado en la rama `doc/cap05-resultados-generacion`:

- Introducción adaptada de la redacción del tutor; las convenciones (prueba, ejecuciones) pasan al Cap. 3 (3.7, 3.9)
  y a cada sección.
- Todas las secciones siguen el esquema contexto → objeto (qué hay en filas, columnas, ejes) → valores (mejor y peor
  primero, de lo general a lo particular) → conjetura separada (guía, «Capítulos de resultados»).
- Sin semillas: «ejecuciones», y «ejecución de referencia» (definida en 3.7) para las pruebas, la ROC, la matriz de
  confusión y las evaluaciones complementarias.
- McNemar y el *bootstrap* separados, con la prueba que respalda cada conclusión (4.1.1, 4.4, 4.6).
- «Descarta» (control de *SkinCAP*) atenuado; el resto de las frases tajantes va a la lista para el autor.
- 4.6 pasa a «Balance de los resultados de clasificación», dos párrafos sin argumentación; los cuatro párrafos
  anteriores quedan como comentarios en las secciones del Cap. 6 donde se integran.
