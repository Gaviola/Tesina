# Ficha 3.8 — Evaluación en otros escenarios

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Reemplaza a la antigua 3.9 «Análisis complementarios» con el título «Evaluación en otros escenarios» (OE3). Sin las tres tablas de protocolo; las pruebas estadísticas pasaron a 3.3; un párrafo y una pregunta por análisis (HIBA, perturbaciones, calibración, Grad-CAM, costo).

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita el 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/08-evaluacion-escenarios.tex` (antes `09-analisis-complementarios.tex`). Label: `sec:met_complementarios` (se conserva el nombre de la sección anterior porque lo referencian 3.1, 3.2, 3.3 y el `00-capitulo.tex`, y la figura `flujo_trabajo.tex`). Sin subsecciones. Desaparecen `sec:met_inferencia`, `sec:met_analisis_compl`, `tab:met_protocolos`, `tab:met_protocolos_vlm`, `tab:met_protocolos_analisis` y `tab:met_pruebas` (esta última vive ahora en 3.3); `sec:met_estadistica` pasó a 3.3.

Fuentes de esta ficha: encabezado del `.tex` (`scripts/robustness_perturbations.py`; `scripts/posthoc_calibration.py`; `scripts/interpretability.py`; `scripts/measure_cost.py`; `outputs/results/{lesion_split_report, robustness/robustness_summary, cost/cost_comparison, *_hiba_test_results}.json`; `docs/resul/revision_experimentacion_20261003.md`); `Codigo/docs/resul/split_lesion_resul_20260926.md`; los resultados de la partición por lesión en `M\Codigo\outputs\results\` (`calibration_les/calibration_summary.json`, entre otros). Los documentos `robustez`, `calibracion`, `interpretabilidad` y `costo` (julio) son anteriores a la partición por lesión: sirven para la idea de cada análisis, no para sus parámetros.

## Hilo conductor

Pregunta que responde la sección: ¿qué ocurre con el sistema cuando cambian las condiciones en que se entrenó (otra población, peor captura), y qué más hay que saber para usarlo (cuánto vale su probabilidad, en qué se apoya, qué cuesta)?

Viene de: 3.7 describió el *pipeline* completo y dejó planteada la pregunta de cómo se evalúa fuera de las condiciones en que se entrenó. Toma de 3.4 los clasificadores elegidos (Swin-Tiny y ConvNeXt-Tiny, semilla 42, `sec:met_supervisados`) y de 3.3 las pruebas con que se comparan los resultados (`sec:met_estadistica`) y la mención de que la calibración «se analiza en la Sección `sec:met_complementarios`; no decide». De 3.2 toma *HIBA* y el mapeo de sus diagnósticos, que 3.2 anuncia que se retoma acá.

Deja instalado: el protocolo completo del capítulo. Los resultados de clasificación, incluidos los de esta sección, se presentan en el Cap. 4 (`cp:res_clasif`), y los de generación y del *pipeline*, en el Cap. 5 (`cp:res_gen`).

```
P1  La prueba de HAM10000 mide el desempeño en las mismas condiciones del entrenamiento (misma población,
    mismo equipo, misma forma de etiquetar). El tercer objetivo específico (OE3) pide evaluar el sistema
    cuando esas condiciones cambian (sec:marco_generalizacion). Cada análisis responde una pregunta
    distinta; casi todos se aplican a los clasificadores, que fijan el diagnóstico del pipeline, y el último
    incluye también a los generadores. Salvo que se indique otra cosa, se usan los modelos de
    sec:met_supervisados con la semilla 42                                          justifica · delimita
    ↓ necesidad — la primera condición que cambia es la población
P2  Primera pregunta, ¿el desempeño se sostiene en otra población? Se evalúan Swin-Tiny y ConvNeXt-Tiny
    sobre las 1 616 imágenes de HIBA (sec:met_datasets), sin ningún ajuste, y se compara cada uno con su
    resultado en la prueba de HAM10000. Como HIBA mezcla imágenes dermatoscópicas y clínicas, el resultado se
    separa por modalidad. Parte de la diferencia puede deberse al mapeo de diagnósticos (el carcinoma
    escamoso va a AKIEC) y no al cambio de población; esa fuente de ruido no puede separarse y se declara
                                                                                  describe · limita
    ↓ ampliación — el conjunto cambia de población; sigue la misma población con la captura degradada
P3  Segunda pregunta, ¿qué ocurre si empeoran las condiciones de captura, sin cambiar de conjunto? A las
    1 503 imágenes de prueba se aplican cuatro perturbaciones con cinco niveles cada una: JPEG (calidad de
    70 a 5), ruido gaussiano (desvío de 8 a 64 sobre 0–255), desenfoque gaussiano (radio de 1 a 6 píxeles)
    y reducción de resolución (de 0.75 a 0.15 del tamaño, y vuelta al original). Se mide la caída relativa
    de la sensibilidad macro frente a la imagen sin perturbar (eq:marco_robustez). Este análisis, como el
    de interpretabilidad, usa una sola vista (sin TTA). Las perturbaciones sintéticas cubren solo parte de la
    variación real entre equipos                                                    define · limita
    ↓ contraste — la robustez mide cuánto cambia el acierto; la calibración, cuánto vale la probabilidad
P4  Tercera pregunta, ¿cuánto se puede confiar en la probabilidad del modelo, que fija el umbral de melanoma
    y que un clínico leería como certeza? Se miden ECE y Brier (sec:marco_eval_calib) sin calibrar y con dos
    ajustes posteriores, temperature scaling (divide todas las salidas por un mismo valor; no cambia la
    clase predicha) y vector scaling (factor y sesgo por clase; puede cambiarla), ajustados en validación y
    evaluados en la prueba. Como los pesos por clase alteran la confianza, se comparan dos versiones de la
    misma configuración, con y sin ellos                                            define · justifica
    ↓ ampliación — la calibración dice cuánto creer la probabilidad; la siguiente pregunta es en qué se apoya
P5  Cuarta pregunta, ¿en qué parte de la imagen se apoya el modelo? Grad-CAM (sec:marco_eval_gradcam) sobre
    Swin-Tiny, en la última etapa de la red y para la clase predicha, en siete imágenes de prueba, una por
    clase. Es una inspección cualitativa: muestra si la activación cae sobre la lesión, pero no mide el
    acierto ni prueba un razonamiento clínico                                       define · limita
    ↓ contraste — hasta acá cada análisis mide el modelo; el último mide qué cuesta usarlo
P6  Última pregunta, ¿qué cuesta usar el sistema? Clasificadores: número de parámetros, tiempo de
    inferencia de una imagen y imágenes por segundo en lotes de 32, sobre la RTX 4070. Generadores: tiempo
    por reporte de las ejecuciones en la A30, que comparten instrucción, decodificación y límite de tokens,
    de modo que la diferencia refleja el modelo y la longitud de lo que escribe. No es una medición
    controlada sino una estimación del orden de magnitud, que permite contrastar el sistema con el cómputo
    de la literatura (tab:marco_brechas)                                            describe · limita
    ↓ cierre — con los cinco análisis el protocolo del capítulo está completo
P7  Con estos análisis queda completo el protocolo. Los resultados de clasificación, incluidos los de esta
    sección, se presentan en el Cap. 4 (cp:res_clasif) y los de generación y del pipeline, en el Cap. 5
    (cp:res_gen)                                                                    cierra
    → Transición al Cap. 4: los resultados de clasificación abren con este protocolo ya definido.
```

La sección no tiene figuras, tablas, ecuaciones ni listas; cita `eq:marco_robustez` (P3), `sec:marco_eval_calib` (P4), `sec:marco_eval_gradcam` (P5) y `tab:marco_brechas` (P6).

Se definen acá (y no se vuelven a definir): la pregunta que responde cada análisis; el conjunto y los niveles de cada perturbación; los dos ajustes posteriores de calibración y la comparación con y sin pesos por clase; el uso de Grad-CAM (capa, clase, siete imágenes); la medición del costo (qué se mide y en qué hardware).
Se retoman de antes (solo se nombran, con `\ref`): *HIBA* y su mapeo de diagnósticos (`sec:met_datasets`); la generalización y el OE3 (`sec:marco_generalizacion`); caída relativa (`eq:marco_robustez`); ECE y Brier (`sec:marco_eval_calib`); Grad-CAM (`sec:marco_eval_gradcam`); los clasificadores elegidos (`sec:met_supervisados`); la tabla de brechas del estado del arte (`tab:marco_brechas`); el *pipeline* (3.7, solo por la frase de entrada).
Remisiones hacia adelante: Cap. 4 (`cp:res_clasif`) y Cap. 5 (`cp:res_gen`); esta sección cierra el Cap. 3.
Extensión: 7 párrafos sin tablas; unas 2–2.5 páginas (estimación del encabezado del `.tex`).

## Subsecciones

Ninguna. Cada análisis ocupa un párrafo (P2 a P6) y abre con la pregunta que responde; P1 abre la sección y P7 la cierra.

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas y referencias internas |
|---|---|---|---|
| P1 | Por qué la prueba de HAM10000 no alcanza; el OE3; a quién se aplican los análisis; modelos y semilla por defecto. | Ninguno. OE3: `Chapters/01-Introduccion/02-objetivos.tex` (tabla de objetivos y preguntas). | `sec:marco_generalizacion`, `sec:met_supervisados` |
| P2 | Validación externa en *HIBA*: Swin-Tiny y ConvNeXt-Tiny, sin ajuste, 1 616 imágenes; comparación con la prueba de HAM10000; separación por modalidad; mapeo con SCC → AKIEC como ruido declarado. | `src/data/hiba.py` (`HIBA_TO_HAM10000`); `outputs/results/swin_tiny_sweep_t06_les_cwnone_hiba_test_results.json` y `convnext_tiny_sweep_t02_les_cwnone_hiba_test_results.json` (`hiba.n_samples` 1616); `revision_experimentacion_20261003.md` §2.5. | `sec:met_datasets` |
| P3 | Cuatro perturbaciones con cinco niveles, sobre las 1 503 imágenes de prueba; caída relativa de la sensibilidad macro; vista única, sin TTA. | `Codigo/scripts/robustness_perturbations.py` (`JPEG_Q`, `NOISE_S`, `BLUR_R`, `RES_F`; `rng = default_rng(42)`); `outputs/results/robustness/robustness_summary.json` (ganadores `t06` y `t02`, `n_imagenes` 1503). Los niveles intermedios (calidad 50, 30, 15; desvío 16, 32, 48; radio 2, 3, 4; resolución 0.50, 0.35, 0.25) ya no figuran en el texto. | `eq:marco_robustez`; `hendrycks2019benchmarking` (no citada en el texto actual) |
| P4 | Calibración: ECE y Brier, sin calibrar y con *temperature scaling* y *vector scaling* ajustados en validación; versiones con y sin pesos por clase. | `Codigo/scripts/posthoc_calibration.py` (`fit`, `metrics`); `Codigo/scripts/lesion_split_report.py` §5 (semilla 42); `Codigo/scripts/evaluate_calibration.py`; `outputs/results/lesion_split_report.json` (clave `calibracion`); `outputs/results/calibration_les/calibration_summary.json`. | `sec:marco_eval_calib` |
| P5 | Grad-CAM sobre la última etapa de Swin-Tiny, clase predicha, siete imágenes de prueba, una por clase; inspección cualitativa. | `Codigo/scripts/interpretability.py` (`_swin_gradcam`, `--n_per_class 1`, `--no-dermlip`); `revision_experimentacion_20261003.md` §2.7. | `sec:marco_eval_gradcam` |
| P6 | Costo: parámetros, latencia de una imagen y *throughput* con lote 32 en la RTX 4070 (clasificadores); tiempo por reporte en la A30 (generadores); orden de magnitud, no *benchmark*. | `Codigo/scripts/measure_cost.py` (`_bench_classifier`, `_gen_latency_from_logs`); `outputs/results/cost/cost_comparison.json` (campo `fuente`: «medido (NVIDIA GeForce RTX 4070)»); generadores: registros de SLURM en A30. | `tab:marco_brechas` |
| P7 | Cierre: protocolo completo; dónde se presentan los resultados. | Ninguno. | `cp:res_clasif`, `cp:res_gen` |

## Figuras y tablas

Ninguna. El Cap. 3 no muestra resultados: las curvas de perturbaciones, los diagramas de confiabilidad, los mapas de Grad-CAM y el gráfico de costo con datos van al Cap. 4 y al Cap. 5 (`robustness_curves.png`, `calibration_les/reliability_diagrams.png`, `interpretability_les/`, `cost_latency.png`). Las tablas de protocolo por resultado y de pruebas por comparación dejaron de estar en esta sección (ver «Quitado»).

## Prosa ya escrita que se conserva

Ninguna de la versión anterior; se reescribió. Se conserva el orden de los análisis (validación externa, perturbaciones, calibración, interpretabilidad y costo).

## Lo que va al apéndice

- Rutas de los checkpoints, nombres de las corridas (`swin_tiny_sweep_t06_les_cwnone`, `convnext_tiny_sweep_t02_les_cwnone`), comandos de los scripts con sus argumentos y versiones de PyTorch: Apéndice E (`ap:reproducibilidad`).
- Parámetros finos de cada análisis (todos los niveles de las perturbaciones, optimizador y regularización de los ajustes de calibración, condiciones de medición del costo): Apéndice E, si el autor decide conservarlos.
- Mapeo completo de las categorías de *HIBA*: ficha de HIBA en el Apéndice F.

## Lo que NO va en esta sección (y dónde está)

- Desempeños, intervalos, valores p y latencias medidas: Caps. 4 y 5.
- Figuras con resultados de perturbaciones, calibración, Grad-CAM y costo: Caps. 4 y 5.
- Definiciones de ECE, Brier, *temperature scaling*, *vector scaling*, caída relativa y Grad-CAM: Cap. 2 (`sec:marco_eval_calib`, `sec:marco_eval_robustez`, `sec:marco_eval_gradcam`). Acá solo qué se hace con cada una.
- Pruebas estadísticas (bootstrap, McNemar, tabla de pruebas): 3.3 (`sec:met_estadistica`).
- Reglas de inferencia, checkpoint, semillas y desvío: 3.3 (métricas de clasificación) y 3.4 (receta y TTA).
- Mapeo de *HIBA* y composición del conjunto: 3.2 (`sec:met_datasets`).
- Decodificación de los generadores: 3.6 (`sec:met_generacion`). Ruteo y cascada: 3.7 (`sec:met_pipeline`).
- Comparación de hardware con el estado del arte y discusión del costo: `cp:discusion`.

## Preguntas abiertas para el autor

1. **(obsoleta tras la revisión del 18/10)** Comparaciones múltiples. Ahora 3.3 aplica la corrección de Holm a McNemar y compara las clases de forma descriptiva; ya no es un tema de esta sección.
2. **(obsoleta tras la revisión del 18/10)** Bootstrap por imagen o por lesión. Es de 3.3 (`sec:met_estadistica`).
3. **(obsoleta tras la revisión del 18/10)** Prueba para la consistencia de reportes. Es de 3.3 (su tabla ya incluye el *bootstrap* pareado de la diferencia de proporciones).
4. **(resuelta)** Dónde se define el TTA. En el Cap. 2; 3.4 dice cómo se aplica. Esta sección solo dice qué análisis no lo usa.
5. **(obsoleta tras la revisión del 18/10)** Protocolo sin verificar (vista de los VLM y de los *embeddings*, rutas de `statistical_tests_les.json`). Salió con las tablas de protocolo (D-A); se verifica al redactar los Caps. 4 y 5.
6. **Foto clínica.** Ya no está en esta sección: la evaluación sobre SkinCAP mapeado no figura en el `.tex`. Si se conserva, va al Cap. 4 y su declaración a 3.2.
7. **Costo de los generadores.** Sigue abierta. La latencia de Mini-VLM sale de un solo registro (A30) y la de LLaVA-Med de dos; el código toma el valor más alto. ¿Se reporta un rango o se vuelve a medir? Además `costo_resul_20260705.md` tiene latencias anteriores a `cost_comparison.json`; se usa el JSON.
8. **(resuelta)** Clave de HIBA: `riccilara2023dataset`, que usa 3.2. Esta sección no cita a *HIBA*, solo remite a `sec:met_datasets`.
9. **IC para HIBA.** Sigue abierta: hoy HIBA no tiene intervalo (un checkpoint por modelo). Un *bootstrap* sobre 1 616 imágenes es barato; si se agrega, se declara en 3.3 o en el Cap. 4.
10. **RAG.** Fuera de esta sección (era una fila de la Tabla 3.1); pendiente del Cap. 5 si la corrida por lesión termina (job 1179315).
11. **(obsoleta tras la revisión del 18/10)** N efectiva de Wilcoxon. 3.3 ya no usa la prueba de rangos.
12. **(resuelta)** Saliencia de DermLIP: P5 no la menciona; se omite del Cap. 3.
13. **(resuelta)** La temperatura del ruteo no va al Cap. 3.
14. **(obsoleta tras la revisión del 18/10)** Comparación entre protocolos (legacy frente a modernos). Salió del Cap. 3 (D-B).

## Decisiones tomadas por cuenta propia

1. **Un párrafo y una pregunta por análisis.** Cada uno de P2 a P6 abre con «La primera/segunda/… pregunta es…» (D-A y R5), distinta de «cuánto acierta».
2. **Sin subsecciones ni tablas.** La sección cierra el capítulo con cinco análisis breves; el protocolo por resultado se declara en los capítulos de resultados.
3. **Modelos por defecto.** P1 fija los modelos elegidos en 3.4 con semilla 42, y cada párrafo solo dice la excepción.
4. **Robustez e interpretabilidad en vista única.** Se declara en P3 en una oración, sin explicar la diferencia con las tablas con TTA.
5. **Calibración con ECE y Brier.** Se mide lo que 3.3 menciona; la elección de los ajustes está en P4 (con y sin pesos por clase).
6. **Grad-CAM solo sobre Swin.** Siete imágenes, una por clase. La saliencia de DermLIP queda fuera.
7. **Costo con su límite explícito.** P6 dice que no es una medición controlada sino un orden de magnitud.
8. **Label conservado.** `sec:met_complementarios` se mantiene pese al cambio de título para no tocar las referencias de 3.1, 3.2, 3.3, `00-capitulo.tex` y `flujo_trabajo.tex`.
9. **Cierre del capítulo.** P7 enlaza con los Caps. 4 y 5 (R5).

## Quitado en la revisión del 18/10/2026

- **Las tres tablas de protocolo (`tab:met_protocolos`, `tab:met_protocolos_vlm`, `tab:met_protocolos_analisis`; la Tabla 3.1 «protocolo por resultado» de 21 filas):** D-A, R1/R3. Salieron enteras; no se movieron. La regla de inferencia y la partición de cada resultado se declaran donde se presentan (Caps. 4 y 5).
- **Subsección 3.9.1 «Protocolos de inferencia» (`sec:met_inferencia`):** D-A. Vista única frente a TTA, checkpoint por F1 ponderado y partición por lesión ya están en 3.4 y 3.3; queda una oración en P3 (robustez e interpretabilidad usan una sola vista).
- **Excepciones de protocolo** (DenseNet121 y ViT-B/16 legacy con vista única y una semilla; VLM ajustados): D-B. Las corridas con la receta anterior salen del Cap. 3; los VLM ajustados no tuvieron fuga (3.5). Se decide en el Cap. 4 si aparecen.
- **Subsección 3.9.2 «Análisis estadístico» y `tab:met_pruebas` (bootstrap, McNemar exacto, Wilcoxon sobre siete clases, lectura del IC, 21 pares, sin corrección, remuestreo por imagen):** D-A. Pasaron a 3.3 (`sec:met_estadistica`); allí McNemar se corrige con Holm y las clases se comparan de forma descriptiva (ficha de 3.3, a cargo de otro agente).
- **Subsección 3.9.3 «Análisis complementarios» (`sec:met_analisis_compl`) y el título «Análisis complementarios» (`sec:met_complementarios` sigue como label):** D-A. Pasa a sección sin subsecciones con el título «Evaluación en otros escenarios».
- **Apertura anterior de la sección («cada número de los Caps. 4 y 5 depende de cuatro decisiones: regla de inferencia, checkpoint, partición y prueba»):** D-A. Era el párrafo que presentaba las tablas de protocolo; P1 ahora justifica la sección por el OE3.
- **HIBA: detalle de 346 de 1 616 imágenes clínicas, fototipos I a IV, ganadores con TTA, un checkpoint por modelo sin IC, comparación con HAM10000 «del mismo checkpoint»:** R3. 3.2 ya presenta el conjunto (proporción de dermatoscópicas y mapeo); P2 conserva la modalidad, el mapeo y el ruido declarado. El 346 exacto ya no figura en ningún lugar del Cap. 3.
- **Perturbaciones: niveles intermedios de cada una (calidad 50, 30, 15; desvío 16, 32, 48; radio 2, 3, 4; resolución 0.50, 0.35, 0.25), semilla 42 del ruido y el momento de aplicación (antes de `Resize(256)` + `CenterCrop(224)`):** R3/R4. Quedan solo los extremos de cada serie; el detalle puede ir al Apéndice E. También se quitó la nota de que la línea base de robustez (vista única) queda por debajo de la de las tablas con TTA.
- **Calibración: MCE y log-pérdida, parámetros de los ajustes (L-BFGS con lr 0.1 y 500 iteraciones, regularización L2 de 1e-3, 10 intervalos), reconstrucción de logits como log(p) a partir de probabilidades promediadas con TTA:** R3. P4 conserva ECE, Brier, los dos ajustes y la comparación con y sin pesos. La reconstrucción con log(p), que antes se declaraba como aproximación, ya no se dice en el Cap. 3 (se pierde una limitación declarada; decisión del autor si vuelve al Apéndice E).
- **Grad-CAM: ReLU, superposición sobre el recorte de validación, orden de las imágenes en el test y la omisión de DermLIP:** R3. P5 conserva capa, clase, número de imágenes y su límite cualitativo.
- **Costo: precisiones de la medición (fp32, entrada aleatoria de 224 × 224, calentamiento de 5 y promedio de 20 iteraciones, `no_grad`, GPU de 12 GB), VRAM estimada por pesos (parámetros × 4 bytes + 0.5 GB), cálculo de segundos por reporte con las líneas «Progreso» de SLURM, decodificación voraz y 512 tokens máximo:** R1/R3. P6 conserva qué se mide y dónde; los parámetros finos pueden ir al Apéndice E. La VRAM estimada dejó de reportarse.
- **Transición a la antigua 3.9: «cada número lleva la regla y la partición de la Tabla 3.1, y cada diferencia, la prueba de la Tabla 3.2»:** D-A. P7 cierra con la ubicación de los resultados (Caps. 4 y 5).
- **Fechas y registro de documentos de julio (antiguos `tests_estadisticos`, `robustez`, `calibracion`, `interpretabilidad`, `costo`):** R1. No se citan en el `.tex`.
