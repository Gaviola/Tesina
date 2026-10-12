# Ficha 3.9 — Análisis complementarios

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/09-analisis-complementarios.tex`. Labels: `sec:met_complementarios` (sección); `sec:met_inferencia`, `sec:met_estadistica` y `sec:met_analisis_compl` (subsecciones, propuestas). Tablas propuestas: `tab:met_protocolos` y `tab:met_pruebas`.

Fuentes de esta ficha: andamiaje `Chapters/03-Materiales-Metodos/07-protocolo-evaluacion.tex` (las tres subsecciones pendientes); `Codigo/docs/resul/split_lesion_resul_20260926.md` y `revision_experimentacion_20261003.md` (números y protocolo vigentes); los resultados de la partición por lesión en `M\Codigo\outputs\results\` (`lesion_split_report.json`, `statistical_tests_les.json`, `robustness/robustness_summary.json`, `calibration_les/calibration_summary.json`, `cost/cost_comparison.json`, `*_hiba_test_results.json`); y los scripts citados en cada párrafo. Los documentos `tests_estadisticos`, `robustez`, `calibracion`, `interpretabilidad` y `costo` (julio) son anteriores a la partición por lesión: sirven para la idea de cada análisis, no para sus parámetros.

## Hilo conductor

Pregunta que responde la sección: ¿con qué regla de inferencia, prueba estadística y análisis se lee cada resultado de los Caps. 4 y 5, y qué pregunta responde cada análisis que no es «cuánto acierta el modelo»?

Viene de: 3.8 presentó el *pipeline* (cascada clasificador → generador, *grounding* por recuperación, ruteo en tres niveles). El test de la misma fuente no alcanza para sostener un resultado (`sec:marco_generalizacion`): hace falta medir con datos de otra población, con imágenes de peor calidad, con probabilidades que se puedan leer como confianza y con un costo de cómputo declarado.

Deja instalado: el protocolo completo. Los Caps. 4 y 5 presentan números nombrando la regla que los produce y la prueba que los compara, sin volver a definirlas.

```
P1  Cada número de los Caps. 4 y 5 depende de cuatro decisiones: la regla de inferencia, el checkpoint, la
    partición y la prueba con la que se compara. Se fijan acá una vez; la Tabla 3.1 las enumera por resultado
                                                                              define · justifica
    ↓ necesidad — la regla de inferencia cambia el número antes de cualquier comparación

[3.9.1 Protocolos de inferencia]
P2  Vista única (una pasada con el preprocesamiento de validación) y TTA (promedio de las probabilidades de
    la imagen y de su reflejo horizontal). La receta moderna usa TTA. El checkpoint es la época con mejor F1
    ponderado en validación; el trial, el de mejor F1 macro en validación (`sec:met_seleccion`). La partición
    es la disjunta por lesión: el test tiene 1503 imágenes, las mismas del original                 define
    ↓ excepción — no todos los resultados usan la misma regla, y la diferencia se declara
P3  Excepciones: DenseNet121 y ViT-B/16 se entrenaron con la receta legacy, en vista única y con una semilla;
    los VLM ajustados se entrenaron con la partición aleatoria, así que su test contiene lesiones vistas en
    el entrenamiento; la robustez y el Grad-CAM usan vista única, de modo que su línea de base no es la de las
    tablas con TTA                                                                              limita
    → Tabla 3.1 (una fila por resultado con su regla, checkpoint, partición y prueba)

[3.9.2 Análisis estadístico]
P4  Tres comparaciones, tres pruebas. Si la diferencia entre dos modelos en una métrica agregada excede lo que
    cambia la composición del test: bootstrap pareado sobre imágenes. Si un modelo acierta imágenes que el
    otro falla: McNemar exacto. Si la mejora es sistemática entre clases: Wilcoxon sobre el recall de las siete
    clases. La Tabla 3.2 fija cada una y sus parámetros                                          define
    ↓ limitación — las pruebas no corrigen por comparaciones múltiples y no remuestrean lesiones
P5  Cómo se leen: un intervalo de confianza del 95 % que no contiene el cero indica diferencia; el p-valor
    del bootstrap solo orienta. Las pruebas pareadas se corren sobre la corrida de la semilla 42, y la
    variación entre semillas se reporta como desvío (`sec:met_protocolo`). Son 21 pares entre siete modelos.
    El bootstrap remuestrea imágenes, no lesiones                                               limita
    → Tabla 3.2

[3.9.3 Análisis complementarios]
P6  Validación externa: ¿el desempeño se sostiene en una población distinta de la del entrenamiento? Solo se
    evalúa el test externo HIBA, con los dos clasificadores ganadores (semilla 42, TTA). Se compara con el
    test de HAM10000 del mismo checkpoint, y se separa por modalidad, porque HIBA mezcla dermatoscopía y
    fotografía clínica. Las diez categorías de HIBA se llevan a las siete de HAM10000 con el mapeo descrito
    en 3.3 (`sec:met_datasets`); ese mapeo introduce una fuente de ruido que se declara       describe · limita
    ↓ ampliación — la población cambia, pero las imágenes siguen siendo las de la captura original
P7  Perturbaciones de adquisición: ¿qué pasa si las condiciones de captura empeoran, sin otro conjunto de
    datos? Cuatro perturbaciones, cinco niveles cada una, sobre las 1503 imágenes originales antes del
    preprocesamiento. JPEG con calidad 70, 50, 30, 15 y 5; ruido gaussiano con desvío 8, 16, 32, 48 y 64 sobre
    la escala de 0 a 255; desenfoque gaussiano de radio 1, 2, 3, 4 y 6 píxeles; resolución reducida al 75, 50,
    35, 25 y 15 % y vuelta al tamaño original. La medida es la caída relativa de la sensibilidad macro
    (`eq:marco_robustez`), con vista única. Las perturbaciones sintéticas cubren solo parte de la variación
    real entre equipos                                                         define · limita
    ↓ contraste — la robustez mide cuánto cambia el acierto; la calibración, cuánto vale la probabilidad
P8  Calibración: ¿cuánto vale la probabilidad del modelo como medida de confianza, y se puede corregir sin
    reentrenar? Se miden ECE, MCE, Brier y log-pérdida (`eq:marco_ece`) sin calibrar y con dos ajustes
    post-hoc, *temperature scaling* (`eq:marco_temperatura`) y *vector scaling*. Ambos se ajustan sobre las
    predicciones de validación del ganador y se evalúan en el test. El primero no cambia la clase predicha; el
    segundo puede cambiarla. Como se guardan probabilidades promediadas con TTA, los logits se reconstruyen
    como log(p), una aproximación que se declara. Se miden dos versiones del mismo trial: con y sin pesos por
    clase                                                                           define · justifica
    ↓ ampliación — la calibración dice cuánto creer la probabilidad; la siguiente pregunta es en qué se apoya
P9  Grad-CAM: ¿el modelo mira la lesión o el contexto de la imagen? Se aplica al Swin ganador sobre la salida
    de su última etapa, con el gradiente del logit de la clase predicha (`eq:marco_gradcam`), y se muestra
    sobre el recorte de validación que recibe el modelo. Son siete imágenes, una por clase, tomadas del test.
    Es una inspección cualitativa: no mide acierto ni prueba razonamiento clínico. Queda fuera la saliencia por
    gradiente de DermLIP, que no se interpreta                                                 define · limita
    ↓ contraste — hasta acá, cada análisis mide el modelo; el último mide qué cuesta usarlo
P10 Costo computacional: ¿qué hardware exige cada alternativa? Para los clasificadores se mide la cantidad de
    parámetros, la latencia con lote de una imagen y el *throughput* con lote de 32, en fp32, sobre una entrada
    aleatoria de 224 × 224 con calentamiento y promedio de 20 iteraciones, en una RTX 4070 de 12 GB. La memoria
    de video (VRAM) es una estimación por pesos, no un valor medido. Para los generadores se toman los segundos
    por reporte de los registros de SLURM en A30, con decodificación voraz y 512 tokens como máximo. No es un
    *benchmark* pareado: sirve para el orden de magnitud                                      describe · limita
    → Transición a Cap. 4: los resultados de clasificación (`cp:res_clasif`) se leen con este protocolo: cada
      número lleva la regla y la partición de la Tabla 3.1, y cada diferencia, la prueba de la Tabla 3.2.

Se definen acá (y no se vuelven a definir): vista única y TTA como reglas de inferencia; el protocolo por
resultado (Tabla 3.1); los parámetros de cada prueba (Tabla 3.2: remuestreos, nivel, N de Wilcoxon); el conjunto
y los niveles de cada perturbación; la reconstrucción de logits con log(p); la medición de costo y su estimación
de VRAM; la pregunta que responde cada análisis.
Se retoman de antes (solo se nombran, con \ref): sensibilidad macro (`eq:marco_acc_bal`), F1 macro (`eq:marco_f1`),
bootstrap pareado, McNemar (`eq:marco_mcnemar`), Wilcoxon (`eq:marco_wilcoxon`), ECE (`eq:marco_ece`), MCE, Brier,
*temperature scaling* (`eq:marco_temperatura`), *vector scaling*, caída relativa (`eq:marco_robustez`), Grad-CAM
(`eq:marco_gradcam`); la partición (`sec:met_particiones`), los ganadores (`sec:met_seleccion`), el umbral de melanoma
(`sec:met_protocolo`), la cascada y el ruteo (`sec:met_pipeline`), la receta y el TTA (`sec:met_supervisados`), la
decodificación de los generadores (`sec:met_generacion`), el hardware (`sec:met_infra`).
Extensión: 11 párrafos (P1 a P10 y la transición), unas 3 páginas con dos tablas.

## Subsecciones

- **3.9.1 Protocolos de inferencia** (`sec:met_inferencia`): P2 y P3, con la Tabla 3.1. P1 abre la sección sin subsección.
- **3.9.2 Análisis estadístico** (`sec:met_estadistica`): P4 y P5, con la Tabla 3.2.
- **3.9.3 Análisis complementarios** (`sec:met_analisis_compl`): P6 a P10. Cada párrafo abre con la pregunta que responde.

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas y referencias internas |
|---|---|---|---|
| P1 | Cuatro decisiones (regla, checkpoint, partición, prueba) por resultado; se fijan una vez. | Ninguno. | — |
| P2 | Vista única o TTA (promedio de softmax de la imagen original y su reflejo horizontal). Receta moderna con `tta=True`. Checkpoint: época con mejor F1 ponderado en validación (`trainer.py`, `monitor: val_f1`), con `--eval-best-checkpoint`; trial por F1 macro en validación. Partición por lesión, test de 1503 imágenes idéntico al original; semillas 42, 43 y 44. | `src/training/recipes.py` (receta `modern`, `tta=True`); `docs/resul/split_lesion_resul_20260926.md` §2 y §4; `docs/ejecuciones.md` (flags `--eval-best-checkpoint`, `--save-val-predictions`). | `sec:met_seleccion`, `sec:met_particiones`, `sec:met_supervisados` |
| P3 | Excepciones declaradas: (a) DenseNet121 y ViT-B/16, receta legacy con `tta: False`, semilla 42; (b) VLM ajustados (Stage 2 v2, 10 épocas, `lora_r=64`) con partición aleatoria, cuyo test contiene lesiones de entrenamiento; (c) robustez y Grad-CAM, vista única; (d) costo, sin TTA. | `outputs/results/densenet_legacy_les_test_results.json` y `vit_legacy_les_test_results.json` (`tta: false`); `docs/resul/vlm_clasificacion_resul_v3_20260517.md` §2; `docs/resul/robustez_resul_20260707.md` y `robustness_summary.json` (campo `protocolo`); `docs/resul/revision_experimentacion_20261003.md` §5; Cap. 4 ficha §4.2 («Declarar»). | `ap:reproducibilidad`; `sec:met_generacion` (VLM) |
| P4 | Las tres pruebas y su pregunta (Tabla 3.2). Bootstrap de 2000 remuestreos con reposición de imágenes, mismas imágenes para ambos modelos; McNemar sobre los pares discordantes; Wilcoxon sobre siete pares de recall por clase. | `Codigo/scripts/statistical_tests.py` (`bootstrap_ci`, `paired_bootstrap_diff`, `mcnemar_exact`, `wilcoxon`; `--n_boot` por defecto 2000, `--seed` 42); `Codigo/scripts/ensemble_bootstrap.py` (`paired_bootstrap_diff_flags`, `n_boot=2000`). | `sec:marco_eval_estadistica`, `eq:marco_mcnemar`, `eq:marco_wilcoxon` |
| P5 | Lectura: IC percentil al 95 %; diferencia si el IC no contiene 0; el p del bootstrap (2 veces la menor proporción de remuestreos de signo contrario) solo orienta. McNemar y Wilcoxon a nivel 0.05 bilateral. Pruebas sobre la semilla 42. Sin corrección por comparaciones múltiples (21 pares de McNemar y 21 de Wilcoxon). Bootstrap sobre imágenes (1503), no sobre lesiones (1429 en test). | `docs/resul/split_lesion_resul_20260926.md` §3 («McNemar p = 0.87», semilla 42); `docs/resul/revision_experimentacion_20261003.md` §2.8 (1503 imágenes, 1429 lesiones); `statistical_tests.py` (`p = 2 * min(...)`). | — |
| P6 | Validación externa en HIBA: solo test; ganadores con semilla 42 y TTA; comparación con HAM10000 del mismo checkpoint; separación por modalidad (346 de 1616 imágenes son clínicas); fototipos I a IV. Mapeo de diez categorías a siete (SCC → AKIEC, declarado como fuente de ruido). Un solo checkpoint por modelo, sin IC. | `src/data/hiba.py` (`HIBA_TO_HAM10000`); `outputs/results/swin_tiny_sweep_t06_les_cwnone_hiba_test_results.json` y `convnext_tiny_sweep_t02_les_cwnone_hiba_test_results.json` (`tta: true`, `hiba.n_samples` 1616); `docs/resul/revision_experimentacion_20261003.md` §2.5. | `sec:met_datasets`; `riccilara2023dataset` (la clave `riccilara2023hiba` **no existe** en el `.bib`); `sec:marco_generalizacion` |
| P7 | Cuatro perturbaciones con cinco niveles cada una (valores en el hilo, P7). Sobre las 1503 imágenes originales, antes de `Resize(256)` + `CenterCrop(224)`. Vista única, sin TTA. Semilla 42 para el ruido. Caída relativa de la sensibilidad macro frente al baseline de vista única. | `Codigo/scripts/robustness_perturbations.py` (`JPEG_Q`, `NOISE_S`, `BLUR_R`, `RES_F`; `rng = default_rng(42)`); `outputs/results/robustness/robustness_summary.json` (ganadores `t06` y `t02`, `n_imagenes` 1503). | `sec:marco_eval_robustez`, `eq:marco_robustez`, `hendrycks2019benchmarking` |
| P8 | Calibración sin ajustar, con *temperature scaling* (un escalar T, minimiza log-pérdida en validación, LBFGS con lr 0.1 y 500 iteraciones) y con *vector scaling* (factor y sesgo por clase, regularización L2 de 1e-3). ECE y MCE con 10 intervalos de igual ancho. Dos versiones del trial: sin pesos por clase (ganador) y con pesos. | `Codigo/scripts/posthoc_calibration.py` (`fit`, `metrics`, log(p) como logits); `Codigo/scripts/lesion_split_report.py` §5 (usa las funciones de `posthoc_calibration.py`, semilla 42); `Codigo/scripts/evaluate_calibration.py` (`--n_bins` 10); `outputs/results/lesion_split_report.json` (clave `calibracion`); `outputs/results/calibration_les/calibration_summary.json`. | `sec:marco_eval_calib`, `eq:marco_ece`, `eq:marco_brier`, `guo2017calibration` |
| P9 | Grad-CAM sobre la última etapa del Swin ganador (semilla 42), gradiente del logit de la clase predicha, ReLU, mapa reescalado y superpuesto al recorte de validación. Siete imágenes, una por clase, en el orden del test. Sin DermLIP. | `Codigo/scripts/interpretability.py` (`_swin_gradcam`, `model.backbone.features`, `--n_per_class 1`, `--no-dermlip` para la versión solo Swin; ckpt por defecto `swin_tiny_sweep_t06_les_cwnone`); `docs/resul/revision_experimentacion_20261003.md` §2.7. | `sec:marco_eval_gradcam`, `eq:marco_gradcam`, `selvaraju2017gradcam`, `adebayo2018sanity` |
| P10 | Clasificadores: parámetros en millones, latencia con lote 1, *throughput* con lote 32, fp32, entrada aleatoria 224 × 224, calentamiento de 5 y 20 medidas, `torch.no_grad`, RTX 4070 12 GB. VRAM: parámetros × 4 bytes + 0.5 GB (estimación). Generadores: segundos por reporte = (tiempo último − tiempo primero) / (reportes último − primero) en las líneas «Progreso» de los registros SLURM, A30 24 GB; decodificación voraz (`do_sample=False`) y `max_new_tokens` 512 por defecto. | `Codigo/scripts/measure_cost.py` (`_bench_classifier`, `_gen_latency_from_logs`, `REFERENCE`); `outputs/results/cost/cost_comparison.json` (campo `fuente`: «medido (NVIDIA GeForce RTX 4070)»); `src/models/llava_med.py` y `mini_vlm.py` (`do_sample=False`); `scripts/generate_report.py` (`--max_tokens` 512). | `sec:met_infra`, `sec:met_generacion`, `cp:discusion` (la comparación con hardware de la literatura va allí) |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Tabla 3.1 (`tab:met_protocolos`) | Una fila por resultado de los Caps. 4 y 5: regla de inferencia, checkpoint, partición y prueba o IC | Tabla de abajo, filas por resultado | a armar en LaTeX; verificar las filas marcadas «a verificar» |
| Tabla 3.2 (`tab:met_pruebas`) | Comparación, pregunta, prueba, parámetros, nivel y función en el código | Tabla de abajo | a armar en LaTeX |
| Ninguna figura | El Cap. 3 no muestra resultados. Las curvas de perturbaciones, los diagramas de confiabilidad, los mapas de Grad-CAM y el gráfico de costo van al Cap. 4 (§4.6 a §4.8) y al Cap. 5 (§10) | `robustness_curves.png`, `calibration_les/reliability_diagrams.png`, `interpretability_les/`, `cost_latency.png` | no se incorporan en 3.9 |

**Tabla 3.1 (propuesta): protocolo por resultado.** Las filas se conservan en el orden de los Caps. 4 y 5.

| Resultado (cap., sección) | Regla de inferencia | Checkpoint | Partición | Prueba o IC | Fuente |
|---|---|---|---|---|---|
| Swin-Tiny y ConvNeXt-Tiny, métricas de test con media ± desvío (4.1, 4.9) | TTA | Época con mejor F1 ponderado en val; trial por F1 macro en val | Por lesión (1503), semillas 42, 43 y 44 | IC bootstrap por métrica; desvío entre semillas | `split_lesion_resul_20260926.md` §2–4 |
| Ensamble Swin+ConvNeXt, voto suave (4.1, 4.9) | TTA, promedio de probabilidades | Ganadores, por semilla | Por lesión; media ± desvío | Desvío entre semillas | `classifier_ensemble.py --preset les` (a verificar la salida `ensemble_seeds.json`) |
| Réplica de desbalance: CE, CE ponderada, focal, *balanced softmax* × 3 arquitecturas (4.1) | TTA (receta modern, semilla 42) | Ganador por pérdida en val (a verificar) | Por lesión | Sin IC en el resumen (a verificar) | `densenet_imb_*_les_test_results.json` (`tta: true`) |
| DenseNet121 y ViT-B/16, receta legacy (4.1) | **Vista única** (`tta: false`) | Ganadores legacy | Por lesión | McNemar y bootstrap contra Swin: **protocolos distintos, declarar** | `densenet_legacy_les_test_results.json`, `vit_legacy_les_test_results.json` |
| VLM generales, *zero-shot* por generación y por verosimilitud (4.2) | Vista única (a verificar) | Ninguno (preentrenados) | Test HAM (1503) | IC bootstrap de sensibilidad macro; McNemar; Wilcoxon | `statistical_tests_les.json` (rutas de predicciones no registradas) |
| VLM generales ajustados, verosimilitud y CoT (4.2, 4.3) | Vista única (a verificar) | `stage2_{llava_med,mini_vlm}_v2` (10 épocas) | **Partición aleatoria** (fuga declarada) | Sin IC (a verificar) | `vlm_clasificacion_resul_v3_20260517.md` §2 |
| Prueba con imagen gris y sin imagen (4.3) | Vista única (a verificar) | Los ajustados | Test HAM (1503) | Descriptiva | `prior_lenguaje_noimage_resul_20260824.md` |
| VLM *zero-shot* sobre foto clínica, SkinCAP mapeado (n = 624) (4.3, 4.4) | *Zero-shot*, vista única (a verificar) | Ninguno | SkinCAP mapeado a 7 clases (`SKINCAP_TO_HAM`) | Descriptiva | `vlm_domain_gap_clinica_resul_20260604.md` §2 |
| DermLIP *zero-shot* en HAM y en foto clínica (4.4) | Vista única (a verificar) | DermLIP ViT-B/16 preentrenado | Test HAM (1503); SkinCAP (624) | IC bootstrap; McNemar; Wilcoxon | `statistical_tests_les.json`, `dermlip_clasificacion_resul_20260605.md` |
| kNN (k = 3), regresión logística y SVM-RBF sobre *embeddings* de DermLIP (4.4) | *Embeddings* de vista única (a verificar) | Cabezas ajustadas en train | Entrenamiento y test por lesión | Semilla 42, sin IC | `dermlip_split_eval.py` |
| Control: mismas cabezas sobre Swin-ImageNet congelado (4.4) | Idem (a verificar) | Preentrenado en ImageNet | Idem | Semilla 42, sin IC | `embeddings_classical_les.json` (a verificar) |
| Calibración: sin calibrar, TS y VS (4.6) | TTA | Ganadores, semilla 42 | Ajuste en val; evaluación en test | ECE, MCE, Brier; sin IC | `lesion_split_report.json` (`calibracion`) |
| Wilcoxon por clase (4.6) | TTA, misma corrida | Ganadores, semilla 42 | Test | Wilcoxon con N = 7 | `statistical_tests_les.json` (`wilcoxon_perclass`) |
| HIBA, externa (4.7) | TTA | Ganadores, semilla 42 | HIBA (1616), solo test | Sin IC (pregunta abierta 9) | `*_hiba_test_results.json` |
| Perturbaciones de adquisición (4.7) | **Vista única** | Ganadores, semilla 42 | Test (1503) | Sin IC; una corrida | `robustness_summary.json` |
| Grad-CAM de Swin (4.8) | Vista única, recorte de validación | Ganador, semilla 42 | 7 imágenes del test | Cualitativa | `interpretability.py` |
| Melanoma-vs-resto, AUC y punto de operación con esp ≥ 0.85 (4.9) | TTA | Ganadores y ensamble, semillas 42, 43 y 44 | Umbral fijado en val; test | Media ± desvío | `lesion_split_report.json` (`melanoma_semillas`) |
| Consistencia y cobertura de los reportes, con cada generador (Cap. 5, 01 y 02) | Decodificación voraz; métrica oficial de solo reporte y matcher estricto | Ancla Swin por lesión, semilla 42 | Test (1503) o subconjunto según el brazo (a verificar) | Según el brazo | `revision_experimentacion_20261003.md` §5 |
| Ensamble y cascada: ruteo, línea base mecánica (Cap. 5, 03 y 08) | Ancla Swin por lesión, semilla 42; métrica oficial | Ganador | 1503; 1452 no derivadas; 248 diferenciales | Bootstrap pareado, 2000 remuestreos, IC 95 % | `ensemble_bootstrap_*_les_report_only_strict.json` |
| RAG con índice por lesión (Cap. 5, 07) | Vista única (a verificar) | DermLIP kNN (k = 3) sobre train | Test (1503) | Bootstrap pareado | **Pendiente**: `full_rag_les` vacío el 11/10/2026 (job 1179315) |
| Costo de clasificadores y generadores (Cap. 5, 10) | Sin TTA; latencia medida | Modelos sin entrenar (arquitectura) y logs de generación | Entrada aleatoria y registros SLURM | Sin IC | `cost_comparison.json` |

**Tabla 3.2 (propuesta): pruebas por comparación.**

| Comparación | Pregunta que responde | Prueba | Parámetros | Nivel | Código |
|---|---|---|---|---|---|
| Métrica agregada de un modelo (exactitud, F1 ponderado, F1 macro, sensibilidad macro) | ¿Cuánto varía por la composición del test? | IC percentil de bootstrap | 2000 remuestreos con reposición de imágenes; semilla 42 | IC del 95 % | `bootstrap_ci` |
| Diferencia de F1 macro o de sensibilidad macro entre dos modelos | ¿La diferencia excede la variación de la muestra? | Bootstrap pareado | 2000 remuestreos, mismas imágenes | IC del 95 % sin 0 | `paired_bootstrap_diff` |
| Aciertos por imagen entre dos modelos | ¿Uno acierta imágenes en las que el otro falla? | McNemar exacto (binomial bilateral sobre los discordantes) | Casos discordantes b y c; sin corrección de continuidad | 0.05 | `mcnemar_exact` |
| Recall por clase entre dos modelos | ¿La mejora es sistemática entre clases? | Wilcoxon de rangos con signo bilateral | N = 7 clases; `zero_method="wilcox"` | 0.05 | `wilcoxon_perclass` |
| Consistencia diagnóstica por reporte (cascada, ensamble) | ¿La diferencia de proporciones excede la variación de los reportes? | Bootstrap pareado de la diferencia de medias | 2000 remuestreos; semilla 42 | IC del 95 % sin 0 | `paired_bootstrap_diff_flags` |

## Prosa ya escrita que se conserva

Ninguna. Las tres subsecciones de `07-protocolo-evaluacion.tex` son solo `\pendiente{}`; se reemplazan por la prosa de P2 a P10. Del andamiaje se conserva la lista de análisis y su orden (validación externa, perturbaciones, calibración e interpretabilidad), y se agrega el costo, que el Cap. 5 (§10) ya mide.

## Lo que va al apéndice

- Rutas de los checkpoints, nombres de las corridas (`swin_tiny_sweep_t06_les_cwnone`, `convnext_tiny_sweep_t02_les_cwnone`), comandos de `statistical_tests.py` y `ensemble_bootstrap.py` con sus argumentos, y versiones de SciPy y PyTorch: Apéndice E (`ap:reproducibilidad`).
- Mapeo completo de las categorías de HIBA a las de HAM10000: ficha de HIBA en el Apéndice F, remitido desde P6.

## Lo que NO va en esta sección (y dónde está)

- Desempeños, IC, p-valores y latencias medidas: Caps. 4 y 5. Esta sección no presenta números de desempeño.
- Figuras de perturbaciones, calibración, Grad-CAM y costo con resultados: Caps. 4 y 5.
- Definiciones de ECE, MCE, Brier, *temperature scaling*, *vector scaling*, McNemar, Wilcoxon, bootstrap, caída relativa y Grad-CAM: Cap. 2 (`sec:marco_eval_estadistica`, `sec:marco_eval_calib`, `sec:marco_eval_robustez`, `sec:marco_eval_gradcam`). Acá solo parámetros y uso.
- Justificación de sensibilidad macro, F1 macro, umbral de melanoma y media ± desvío de semillas: 3.4 (`sec:met_seleccion`, `sec:met_protocolo`).
- Receta de entrenamiento, aumento y definición del TTA: 3.5 (`sec:met_supervisados`).
- Decodificación de los generadores, formato del reporte y parseo: 3.7 (`sec:met_generacion`).
- Ruteo en tres niveles y cascada: 3.8 (`sec:met_pipeline`). El ruteo no usa la confianza calibrada ni el umbral τ (revisión del 03/10, §2.6).
- Comparación de hardware con el estado del arte y discusión del costo: `cp:discusion`.
- Fuga de información cuantificada y partición por lesión: 3.3 (`sec:met_particiones`).

## Preguntas abiertas para el autor

1. **Comparaciones múltiples.** Con siete modelos hay 21 pares de McNemar y 21 de Wilcoxon, y el código no corrige (las estrellas son sin corrección). ¿Se declara la limitación o se aplica Holm a cada familia de pruebas?
2. **Bootstrap por imagen.** El test tiene 1503 imágenes y 1429 lesiones. ¿Se remuestrea por lesión, o se declara que los IC pueden ser optimistas?
3. **Prueba para la consistencia de reportes.** `statistical_tests.py --consistency_json` admite McNemar sobre consistencia por reporte, pero la cascada usa bootstrap pareado (`ensemble_bootstrap.py`). Propongo bootstrap para toda la consistencia de reportes y McNemar solo para aciertos por imagen, pero hay que confirmarlo.
4. **Dónde se define el TTA.** Resuelto en la revisión cruzada (11/10): el TTA está definido en el Cap. 2 (`01-fundamentos.tex`, l. 152, dentro de `sec:marco_regularizacion`). 3.5 dice cómo se aplica y 3.9 solo lo nombra.
5. **Protocolo sin verificar.** Quedan marcados «a verificar» la vista de los VLM y de los *embeddings* de DermLIP (¿TTA?), la réplica del control con Swin-ImageNet, y las rutas de predicciones de `statistical_tests_les.json`, que no registra ni rutas ni `n_boot`. Hay que confirmarlo con los comandos de cada corrida.
6. **Foto clínica.** La evaluación de SkinCAP tiene n = 624 con mapeo curado. El documento de dominio advierte que SkinCAP se usó en el *stage 1* de los VLM. ¿Qué subconjunto se usó como test clínico, y cómo se declara en 3.3 y en la Tabla 3.1?
7. **Costo de los generadores.** La latencia de Mini-VLM sale de un solo registro (A30). La de LLaVA-Med sale de dos registros, y el código toma el valor más alto (`rates[len//2]` con dos valores). ¿Se reporta un rango, o se vuelve a medir? La columna «A30 / RTX 4080» de la tabla de referencia no coincide con el registro. Además, `docs/resul/costo_resul_20260705.md` tiene latencias anteriores a `cost_comparison.json` (p. ej. Swin 8.7 ms frente a 9.51 ms): se usa el JSON.
8. **Clave de HIBA.** `riccilara2023hiba` no está en el `.bib`. Se usa `riccilara2023dataset`, que es la del dataset en el Cap. 2. Hay que confirmar si la cita de HIBA es la correcta.
9. **IC para HIBA.** Hoy HIBA no tiene IC (un checkpoint por modelo). Un bootstrap sobre 1616 imágenes es barato. ¿Se agrega?
10. **RAG.** `outputs/generated_reports/mini_vlm/full_rag_les` está vacío el 11/10/2026 (job 1179315 con inicio estimado el 04/10). Hay que confirmar el estado antes de cerrar el Cap. 5, porque la fila de RAG de la Tabla 3.1 queda pendiente.
11. **N efectiva de Wilcoxon.** Con siete clases el p mínimo bilateral es 0.016. Cuando una clase tiene el mismo recall en los dos modelos, `zero_method="wilcox"` la descarta y N baja a 6, con p mínimo 0.031. Esto aparece en `statistical_tests_les.json` (p = 0.031 con estadístico 0 para Swin frente a ViT-B/16). Hay que declarar la N por par en el Cap. 4.
12. **Saliencia de DermLIP.** Se descartó como artefacto del gradiente (revisión del 03/10, §2.7). ¿Se menciona en una oración de 3.9 o se omite del Cap. 3 por completo?
13. **Temperatura del ruteo.** `temperature_scaling.py` y su τ no se usan en la cascada reportada. ¿Se confirma que no van al Cap. 3?
14. **Comparación entre protocolos.** Los clasificadores legacy (vista única, una semilla) se comparan con Swin y ConvNeXt (TTA y tres semillas) en el Cap. 4 §4.1. La tabla lo declara; la pregunta es si el texto del Cap. 4 también lo hace.

## Decisiones tomadas por cuenta propia

1. **McNemar en su versión exacta.** Se describe la binomial bilateral sobre los casos discordantes, que es lo que usa `mcnemar_exact` para todos los pares. La versión χ² de `eq:marco_mcnemar` no se usa en ningún resultado. No se toca el Cap. 2; queda como pregunta si el Cap. 2 la presenta como aproximación o la quita.
2. **El p del bootstrap no decide.** Se decide por el IC percentil al 95 %. El p aproximado (`p = 2 · min(...)`) se imprime en el código pero no se reporta como prueba.
3. **Pruebas sobre la semilla 42.** Las pruebas pareadas se corren sobre la corrida de referencia, no sobre el promedio de semillas. La variación entre semillas se reporta como desvío en 3.4 y en el Cap. 4. Es lo que hace `split_lesion_resul_20260926.md`.
4. **Excepciones declaradas, no corregidas.** Los legacy en vista única y los VLM con partición aleatoria se mantienen tal como se midieron y se declaran en la Tabla 3.1. No se re-corren.
5. **Calibración con `posthoc_calibration.py`.** TS y VS se ajustan en validación y se evalúan en test, con la semilla 42. `temperature_scaling.py` queda fuera (pregunta 13).
6. **Grad-CAM solo sobre Swin.** Siete imágenes, una por clase, con el checkpoint ganador. La saliencia de DermLIP queda fuera (pregunta 12).
7. **Costo con su estimación explícita.** La VRAM se describe como estimación por pesos, y las latencias de los generadores como segundos por reporte de los registros de SLURM, sin afirmar un *benchmark* pareado.
8. **Estructura en tres subsecciones.** P1 abre la sección y P2–P10 se reparten en 3.9.1, 3.9.2 y 3.9.3. Cada análisis de 3.9.3 abre con la pregunta que responde, distinta de «cuánto acierta», como pide el encargo.
9. **Robustez con su línea de base de vista única.** Se declara que la sensibilidad base de la curva (vista única) queda por debajo de la de las tablas con TTA, y que lo que se mide es la caída relativa.
10. **VLM ajustados sin fuga (redacción).** La P3(b) de esta ficha declaraba partición aleatoria con fuga. Se redactó según la revisión cruzada (punto 6 del Cap. 3): el ajuste usa SkinCaRe y no HAM10000, y el test es el de 1 503 imágenes. Los scripts de clasificación de VLM leen `ham10000_splits.json` por defecto (test idéntico al original). Confirmar el texto de P3.
11. **Monitor del checkpoint.** El checkpoint se elige por `val_f1` (máximo) en `CheckpointCallback`, llamado desde `scripts/train_classifier.py`, no en `trainer.py`; el log del trainer resume la mejor época por `val_loss`, pero el `best_model.pt` que se evalúa es el de F1 ponderado. Se redactó así.
12. **Consistencia de reportes.** Se aplica la propuesta de la pregunta 3: bootstrap pareado de la diferencia de medias para la consistencia; McNemar solo para aciertos por imagen (Tabla 3.2).
13. **Tabla 3.1 partida en dos.** Por tamaño, `tab:met_protocolos` (clasificación, 14 filas) y `tab:met_protocolos_analisis` (análisis y generación, 7 filas). Etiqueta nueva.
14. **Columna «Función» en la Tabla 3.2.** Se conserva la columna con el nombre de la función de código, porque la ficha la pide; la columna «Fuente» de la Tabla 3.1 se quitó.
15. **Verificaciones sobre código y JSON.** Verificado: McNemar exacto (`mcnemar_exact`); bootstrap con 2 000 remuestreos y semilla 42; `zero_method="wilcox"`; perturbaciones y niveles; calibración (L-BFGS, lr 0.1, 500 iteraciones, L2 de 1e-3 solo en vector scaling, 10 bins); Grad-CAM con ReLU; costo (fp32, `no_grad`, 5 y 20 iteraciones, VRAM = parámetros × 4 bytes + 0.5 GB); TTA en `imb` y HIBA (`tta: true`); legacy (`tta: false`); HIBA 1 616, 346 clínicas, fototipos I–IV. Vista única de VLM y DermLIP: los scripts de evaluación no aplican flip. Pendiente: confirmar la tabla de imágenes grises y sin imagen, el subconjunto de SkinCAP, y la ejecución de RAG.
16. **Acrónimos nuevos propuestos** (sin declarar, escritos en texto llano): `\acronimo{ic}{IC}{intervalo de confianza}{Confidence Interval}`; `\acronimo{mce}{MCE}{error de calibración máximo}{Maximum Calibration Error}`; `\acronimo{vram}{VRAM}{memoria de video}{Video Random-Access Memory}`; `\acronimo{slurm}{SLURM}{gestor de trabajos del clúster}{Simple Linux Utility for Resource Management}`; `\acronimo{jpeg}{JPEG}{formato de compresión de imágenes}{Joint Photographic Experts Group}`; `\acronimo{svm}{SVM}{máquina de vectores de soporte}{Support Vector Machine}`; `\acronimo{rbf}{RBF}{función de base radial}{Radial Basis Function}`; `\acronimo{relu}{ReLU}{unidad lineal rectificada}{Rectified Linear Unit}`.
