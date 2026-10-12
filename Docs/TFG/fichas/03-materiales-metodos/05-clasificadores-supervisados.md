# Ficha 3.5 — Clasificadores supervisados

**Estado: propuesta, sin aprobar.** Archivo: `Chapters/03-Materiales-Metodos/05-clasificadores-supervisados.tex`. Labels: `sec:met_supervisados` (sección) y `sec:met_supervisados_arquitecturas`, `sec:met_supervisados_preprocesamiento`, `sec:met_supervisados_receta`, `sec:met_supervisados_busqueda`, `sec:met_supervisados_ensamble` (subsecciones; propuestos).

Sale de: la subsección «Clasificadores supervisados» de `03-modelos-evaluados.tex` (solo `\pendiente`, sin prosa que conservar) y la subsección «Preprocesamiento y aumento de datos» de `02-datos-particiones.tex` (`\pendiente`, sin prosa). `sec:met_modelos` desaparece (ningún `\ref` la usa).

## Hilo conductor

Pregunta que responde la sección: ¿qué clasificadores supervisados se entrenan, con qué preprocesamiento, receta, búsqueda de hiperparámetros y criterio de selección, y cómo se obtiene de ellos una probabilidad de melanoma?

Viene de: 3.4 fija el criterio con el que se juzgan los modelos (sensibilidad macro como resultado principal; F1 macro en validación para elegir el trial; F1 ponderado en validación para el *checkpoint*; el test no interviene; umbral de melanoma con especificidad ≥ 0.85 fijado en validación; media ± desvío de tres semillas). 3.3 deja la partición disjunta por lesión y el desbalance de las siete clases. El Cap. 2 deja las arquitecturas (2.2), la receta general y el desbalance (2.1), la línea base (2.2) y el ensamble por voto suave (`sec:marco_senales_confianza`).

Deja instalado: los cuatro modelos y las dos recetas; el par ganador (Swin-Tiny y ConvNeXt-Tiny) con su ensamble; la probabilidad de melanoma y su umbral. Para 3.6: estos clasificadores producen una probabilidad por clase y no texto, y el Swin preentrenado con el *backbone* congelado reaparece como control de DermLIP.

```
3.5.1 Arquitecturas
P1  Cuatro modelos, una CNN y un transformer visual por familia, preentrenados en ImageNet, con cabeza de
    siete salidas. Se nombran las variantes Tiny y el tamaño de cada una                    justifica
    ↓ necesidad — los cuatro comparten el mismo problema de entrada, que hay que fijar antes de entrenar
P2  Dos recetas: la moderna (ConvNeXt-Tiny y Swin-Tiny, con barrido) y la legacy (DenseNet121 y ViT-B/16,
    sin barrido). Se adelanta la diferencia sin detallar la receta                          describe
    ↓ necesidad — qué le llega al modelo: imágenes de 224 × 224 normalizadas como las de ImageNet

3.5.2 Preprocesamiento, aumento de datos y TTA
P3  Resolución y normalización; la forma de validación y test depende de la receta               describe
    ↓ problema — con 6 447 imágenes de entrenamiento el riesgo es el sobreajuste
P4  Aumento de datos en entrenamiento, en ambas recetas, con sus parámetros                      describe · justifica
    ↓ necesidad — el aumento se aplica en entrenamiento, y en inferencia se usa TTA
P5  TTA: promedio de las probabilidades de la imagen y de su reflejo horizontal; solo en la receta
    moderna, y también en validación para el umbral y la calibración                             define · describe
    ↓ consecuencia — la salida del clasificador es una probabilidad por clase, que sirve para 3.4 y 3.9

3.5.3 Receta de entrenamiento y pérdidas
P6  Receta moderna en dos etapas: cabeza sola una época; después red completa con decaimiento de la tasa
    por capa, calentamiento lineal y coseno. Optimizador AdamW y suavizado de etiquetas               describe · define
    ↓ problema — la red puede memorizar el conjunto de entrenamiento y dejar de generalizar
P7  Detención temprana con paciencia 5 sobre el F1 ponderado de validación, un único contador para
    las dos etapas; el *checkpoint* es la época con mejor F1 ponderado; el test usa ese *checkpoint*  describe · justifica
    ↓ contraste — la pérdida de entrenamiento no sirve para comparar los modelos
P8  Pérdida base (entropía cruzada) y sus variantes para el desbalance: pesos por clase, focal y
    *balanced softmax*, en lista. Se explica qué se compara en el barrido y qué en la réplica    define · justifica
    ↓ contraste — la receta legacy no usa suavizado ni calentamiento, y ajusta con pesos por clase
P9  Receta legacy: una etapa, AdamW, sin suavizado ni calentamiento, sin TTA; decisión de declarar
    las ablaciones de la receta sobre la partición anterior                                      describe · limita
    ↓ necesidad — con las recetas definidas, hay que decir cómo se eligieron sus valores

3.5.4 Búsqueda de hiperparámetros y semillas
P10 Barrido moderno: 15 combinaciones predefinidas de tasa de aprendizaje, decaimiento de pesos y
    magnitud de RandAugment, por dos pesos de clase, por dos modelos: 60 corridas. Estrategia y
    motivo (nodos sin internet, sin agente de W&B)                                              describe · justifica
    ↓ consecuencia — el trial se elige por F1 macro en validación; la pérdida forma parte del trial
P11 Búsqueda legacy: 28 corridas aleatorias con rangos amplios, elegidas por F1 ponderado de validación  describe · limita
    ↓ necesidad — los ganadores de la búsqueda necesitan semillas para reportarse con desvío
P12 Ganadores (Swin-Tiny t06, ConvNeXt-Tiny t02, sin pesos por clase), semillas 42, 43 y 44 y
    media ± desvío; legacy y réplica con una sola semilla                                        define · limita
    ↓ ampliación — con dos modelos, el paso siguiente es combinarlos

3.5.5 Ensamble y detección de melanoma
P13 Ensamble por voto suave de los dos ganadores; solo ese par, porque se fijó con la validación  define · justifica
    ↓ ampliación — el mismo ensamble sirve para la clasificación y para la detección de melanoma
P14 Detección de melanoma: probabilidad de la clase MEL, umbral fijado en validación con
    especificidad ≥ 0.85 y aplicado sin cambios al test                                          define · justifica
→ Transición a 3.6: «Estos clasificadores devuelven una probabilidad por clase y no generan texto.
  Para saber si un modelo visión–lenguaje, que sí genera texto, clasifica con la misma calidad, se
  comparan ambos con las mismas métricas (Sección~\ref{sec:met_clasif_vlm}).»
```

Se definen acá (y no se vuelven a definir): las dos recetas como configuración (no como concepto); la estrategia del barrido (15 combinaciones con magnitud de RandAugment asignada en rotación, por pesos de clase); la regla de selección del trial, del *checkpoint* y de las semillas; el par del ensamble; la regla del umbral de melanoma (la de 3.4, aplicada).

Se retoman de antes (solo se nombran, con `\ref`): CNN, ViT y Swin (`sec:marco_vision`, `sec:marco_cnn`, `sec:marco_vit`, `sec:marco_swin`); línea base (`sec:marco_vision`); preentrenamiento, cabeza, *backbone*, ajuste fino, dos etapas y decaimiento de la tasa por capa (`sec:marco_transferencia`, `eq:marco_llrd`); entropía cruzada, softmax, AdamW, calentamiento, coseno (`sec:marco_fundamentos`, `eq:marco_entropia`, `eq:marco_softmax`); sobreajuste, detención temprana, decaimiento de pesos, suavizado de etiquetas, aumento de datos, RandAugment, borrado aleatorio y TTA (`sec:marco_regularizacion`); pesos por clase, focal y *balanced softmax* (`sec:marco_desbalance`, `eq:marco_entropia`); voto suave (`sec:marco_senales_confianza`); sensibilidad, especificidad, F1, AUC y detección como tarea binaria (`sec:marco_eval_clasif`, `eq:marco_sens_esp`, `eq:marco_f1`, `eq:marco_auc`).

Extensión: 14 párrafos, unas 4.5–5 páginas, en cinco subsecciones.

## Subsecciones

- **3.5.1 Arquitecturas y cabezas** (P1–P2): los cuatro modelos, sus variantes, su preentrenamiento y su cabeza; por qué estas cuatro; la división en dos recetas.
- **3.5.2 Preprocesamiento, aumento de datos y TTA** (P3–P5): resolución y normalización, aumentos en entrenamiento, TTA.
- **3.5.3 Receta de entrenamiento y pérdidas** (P6–P9): receta moderna, detención temprana, pérdidas para el desbalance, receta legacy.
- **3.5.4 Búsqueda de hiperparámetros y semillas** (P10–P12): barrido moderno, búsqueda legacy, ganadores y semillas.
- **3.5.5 Ensamble y detección de melanoma** (P13–P14).

## Contenido por párrafo

Rutas relativas a `W\Codigo\` salvo indicación. Las líneas de `train_classifier.py` y de los scripts son las verificadas al escribir la ficha.

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | DenseNet121 (CNN, bloques densos), ConvNeXt-Tiny (CNN moderna), ViT-B/16 (transformer con parches de 16 × 16), Swin-Tiny (transformer jerárquico con ventanas). Preentrenados con pesos ImageNet-1K; cabeza `Dropout(0.3)` + lineal de 7 salidas. Las variantes Tiny encajan en la restricción de cómputo de 3.1 (una GPU de consumo). Parámetros con cabeza de 7 clases, de los logs de entrenamiento: DenseNet121 6 961 031; ConvNeXt-Tiny 27 825 511; ViT-B/16 85 804 039; Swin-Tiny 27 524 737 | Pesos: `src/models/classifiers.py` (DenseNet l. 15, ConvNeXt l. 57, Swin l. 100, ViT l. 136). Cabeza: mismas clases, l. 18–23, 60–66, 103–107, 139–144. Parámetros: `M\Codigo\outputs\logs\*` (líneas «Modelo: <m> \| Parámetros», del 11–12/04/2026 para DenseNet y ViT, y 29–30/04/2026 para Swin y ConvNeXt). Las cifras de `W\Codigo\docs\resul\costo_resul_20260705.md` (8.0 M para DenseNet121) no coinciden con las de los logs; ver «Preguntas abiertas» | dosovitskiy2021image, liu2021swin, huang2018densely, liu2022convnet, russakovsky2015imagenet; Cap. 2: `sec:marco_vision`, `sec:marco_cnn`, `sec:marco_vit`, `sec:marco_swin`, `sec:marco_transferencia` |
| P2 | Las dos recetas: la moderna para ConvNeXt y Swin (y para las réplicas del desbalance); la legacy para DenseNet y ViT, que quedan fuera del barrido. Se nombra el motivo solo en P10 | `W\Codigo\scripts\toko\submit.py` (`_CLS_LR` l. 41–46; trabajos `les_densenet_legacy` y `les_vit_legacy` l. 70–81); `W\Codigo\docs\ideas\clasificadores_sweep_modern_v4_plan_20260510.md` §1 | — |
| P3 | Las imágenes llegan a 224 × 224 y se normalizan con la media y el desvío de ImageNet. Entrenamiento: sin cambios. Validación y test: receta moderna `Resize(256)` + `CenterCrop(224)`; receta legacy `Resize((224, 224))` (sin preservar proporción). Con 6 447 imágenes de entrenamiento (partición por lesión), el riesgo es el sobreajuste | `W\Codigo\scripts\prepare_data.py` l. 31 y 81–93 (`IMAGE_SIZE = 224`, `resize((size, size), LANCZOS)`); `W\Codigo\src\data\transforms.py` (`IMAGENET_MEAN/STD` l. 4–5; `get_val_transforms` l. 57–78); `scripts/train_classifier.py` l. 275 y 286 (`center_crop=args.random_resized_crop`); 6 447 de `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §2 | sec:marco_regularizacion (sobreajuste); russakovsky2015imagenet (ImageNet) |
| P4 | Receta moderna, aumento en entrenamiento: `RandomResizedCrop` con escala mínima 0.7; volteo horizontal (p = 0.5); RandAugment con N = 2 transformaciones y magnitud M de la grilla (6, 9 o 12); borrado aleatorio con p = 0.25. Receta legacy: rotación de hasta 30°, volteo, `ColorJitter` (brillo, contraste y saturación 0.2; tono 0.1). Se explica el problema antes de RandAugment: la variación de la lesión sin cambiar su clase | `W\Codigo\src\data\transforms.py` l. 8–54 (rama `randaugment`, `random_erasing`, `rrc_scale_min`); `W\Codigo\src\training\recipes.py` l. 69–88 (`modern`: `randaugment_n` default 2, `random_erasing=0.25`, `rrc_scale_min=0.7`) | cubuk2020randaugment, zhong2020random, kittler2016standardization, shorten2019survey; Cap. 2: `sec:marco_regularizacion` |
| P5 | TTA: se promedian las probabilidades de la imagen original y de su reflejo horizontal. Se aplica en test y, con `--save-val-predictions`, en validación (mismo protocolo, para el umbral de P14 y la calibración de 3.9). La receta legacy no usa TTA | `W\Codigo\src\evaluation\tta.py` l. 15–72 (`tta_modes=("original","hflip")`, promedio `probs_sum / len(modes)`); `W\Codigo\scripts\train_classifier.py` l. 489–491 (test) y l. 549–553 (validación) | krizhevsky2012imagenet (TTA); Cap. 2: `sec:marco_regularizacion` |
| P6 | Receta moderna, dos etapas. Etapa 1: 1 época, backbone congelado, solo la cabeza, tasa del trial, sin planificador. Etapa 2: todo descongelado; decaimiento de la tasa por capa con factor 0.85 (Swin: 10 grupos; la entrada recibe 0.85^9 ≈ 0.23 de la tasa de la cabeza); calentamiento lineal de 3 épocas desde 0.1 y coseno sobre las 36 restantes; 40 épocas en total. AdamW con el decaimiento de pesos del trial; suavizado de etiquetas 0.1; sin MixUp ni CutMix; focal γ = 0 (ver «Decisiones») | `W\Codigo\scripts\train_classifier.py` l. 391–446 (etapa 1 `opt_s1` l. 399; etapa 2 l. 416–446); `W\Codigo\src\training\optim_groups.py` l. 20–72 (`get_llrd_groups`), l. 135–153 (`_swin_tiny_layers`), l. 156–166 (`get_head_params`); `W\Codigo\src\training\schedulers.py` l. 16–63 (`build_scheduler`, calentamiento con `LinearLR` y `start_factor=0.1`); `W\Codigo\src\training\recipes.py` l. 69–88; `W\Codigo\docs\ideas\clasificadores_sweep_modern_v4_plan_20260510.md` §2 (valores fijos) | loshchilov2019decoupled (AdamW), szegedy2016rethinking, muller2019does (suavizado), goyal2017accurate (calentamiento), loshchilov2017sgdr (coseno), howard2018universal, kumar2022finetuning (dos etapas y LLRD); Cap. 2: `eq:marco_llrd`, `sec:marco_transferencia` |
| P7 | Detención temprana: paciencia 5 épocas sobre el F1 ponderado de validación, un único contador que cruza las dos etapas. Se guarda el *checkpoint* de la época con mejor F1 ponderado (`val_f1`). El test se evalúa recargando ese *checkpoint* (`--eval-best-checkpoint`). Precisión mixta bf16 en GPUs Ampere o posteriores. Motivo: el criterio de 3.4 se aplica al trial, no a la época; cambiarlo obligaría a reentrenar | `W\Codigo\scripts\train_classifier.py` l. 386–387 (`EarlyStopping(patience=args.patience, monitor="val_f1")`, `CheckpointCallback`), l. 476–479 (`--eval-best-checkpoint`); `W\Codigo\src\training\callbacks.py` l. 11–81; `W\Codigo\src\training\trainer.py` l. 188 (`val_f1` = F1 ponderado), l. 234–235 (planificador opcional); `W\Codigo\src\utils\device.py` l. 13–25 (bf16 si capacidad ≥ 8); `W\Codigo\docs\ideas\criterio_seleccion_plan_20260917.md` (tabla «Los dos niveles») | goodfellow2016deep (detención temprana); Cap. 2: `sec:marco_regularizacion` |
| P8 | Pérdida base: entropía cruzada con las probabilidades de la softmax. Con pesos por clase, la pérdida ponderada de cada ejemplo lleva el peso del inverso de la frecuencia de su clase. Las cuatro pérdidas comparadas, en lista: (1) entropía cruzada sin pesos; (2) entropía cruzada ponderada; (3) focal con γ = 2; (4) *balanced softmax*. El barrido moderno compara solo (1) y (2); la réplica del desbalance compara las cuatro, con la misma receta y sin alterar otros valores (salvo la tasa, ver «Preguntas abiertas», 5) | `W\Codigo\src\training\losses.py` l. 19–89 (`FocalLoss`), l. 92–112 (`BalancedSoftmaxLoss`, `logits + log_prior`), l. 115–141 (`build_loss`); `W\Codigo\scripts\train_classifier.py` l. 49–57 (`compute_class_weights`, `total/(C·n_c)`) y l. 370 (uso); `W\Codigo\scripts\toko\submit.py` l. 102–163 (`imb_*`: `--focal-gamma 0 --class-weights none|auto`, `--focal-gamma 2.0`, `--balanced-softmax`) | lin2017focal, ren2020balanced, buda2018systematic; Cap. 2: `sec:marco_desbalance`, `eq:marco_entropia` |
| P9 | Receta legacy (DenseNet121 y ViT-B/16): una etapa; AdamW con tasa, decaimiento de pesos y planificador de la búsqueda legacy (P11); suavizado 0; sin calentamiento; 30 épocas; paciencia 5; pesos por clase `auto` (el valor por defecto de la CLI, sin bandera en los trabajos legacy); sin TTA. Se declara que las ablaciones de la receta (sin MixUp, sin TTA, etc.) se hicieron sobre la partición anterior y se presentan en Cap. 4 como análisis de mecanismo | `W\Codigo\src\training\recipes.py` l. 62–68 (`legacy`: 30 épocas, `label_smoothing=0`, `warmup_epochs=0`); `W\Codigo\scripts\train_classifier.py` l. 118–119 (`--class-weights` default `auto`), l. 104 (`--patience` default 5); `W\Codigo\scripts\toko\submit.py` l. 70–81; `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §8 (ablaciones sobre la partición anterior) | — (ablaciones: sin cita) |
| P10 | Barrido moderno: 5 tasas de aprendizaje × 3 decaimientos de pesos = 15 combinaciones, con la magnitud de RandAugment asignada en rotación (cada valor de M aparece en 5 combinaciones; no es producto cartesiano); por cada una, pesos por clase `auto` y `none`: 30 corridas por modelo, 60 en total. Fijo: 40 épocas, semilla 42, focal γ = 0, suavizado 0.1, decaimiento por capa 0.85, dos etapas, TTA. Se usa una lista predefinida y no un agente de W&B porque los nodos de TOKO no tienen internet. Trial ganador: mayor F1 macro en validación entre las 30 corridas del modelo (la combinación de pesos forma parte del trial) | `W\Codigo\configs\sweeps\phase1_modern_sweep_grid.yaml` l. 18–41 (grilla de 15 trials, l. 22–23 base flags); `W\Codigo\scripts\toko\submit_sweep.py` l. 1–25 (uso) y l. 146–156 (comando de entrenamiento: `--recipe modern --focal-gamma 0`, `--class-weights`); `W\Codigo\scripts\lesion_split_report.py` l. 71–110 (ranking por `val.f1_macro`, ganador entre las dos variantes); `W\Codigo\docs\ideas\clasificadores_sweep_modern_v4_plan_20260510.md` §4 (sin internet); `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §2 | — |
| P11 | Búsqueda legacy: 28 corridas aleatorias (muestreo con semilla por defecto 42 de `sweep_utils`; 15 de DenseNet121 y 13 de ViT-B/16 en la exportación). Rangos: tasa log-uniforme entre 1e-5 y 1e-3; decaimiento de pesos en {0, 0.001, 0.01, 0.1}; planificador en {coseno, ninguno}; suavizado en {0, 0.05, 0.1}; congelar el *backbone* en {sí, no}; 30 épocas fijas. Elegidas por el mejor F1 ponderado de validación (criterio anterior al del 17/09). Valores elegidos: DenseNet121, tasa 7.91e-5, decaimiento 0.01, suavizado 0, coseno, *backbone* sin congelar; ViT-B/16, tasa 1.56e-5, decaimiento 0.01, suavizado 0, sin planificador, *backbone* sin congelar | `W\Codigo\configs\sweeps\phase1_sweep.yaml` l. 1–70 (rangos); `W\Codigo\scripts\sweep_utils.py` l. 55–66 (`generate_combinations`, muestreo aleatorio); `M\Codigo\wandb_sweep_phase1.csv` (28 filas; columnas `model`, `lr`, `weight_decay`, `label_smoothing`, `scheduler`, `freeze_backbone`, `best_val_f1`); `W\Codigo\configs\models\densenet.yaml` y `vit.yaml` (valores coincidentes); `W\Codigo\docs\resul\clasificadores_resul_iteraciones_20260429.md` §7.3 (dice «25+» configuraciones: ver «Preguntas») | — |
| P12 | Ganadores (por F1 macro de validación, semilla 42): Swin-Tiny, trial t06: tasa 7.5e-5, decaimiento 0.10, M = 6, sin pesos por clase; ConvNeXt-Tiny, trial t02: tasa 3.0e-5, decaimiento 0.05, M = 9, sin pesos. Cada uno con semillas 43 y 44 además de la 42 (media ± desvío en 3.4). Legacy y réplica: una semilla (42), y se dice en el texto que su desvío no se estimó | `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §2–§3 (ganadores y semillas); `M\Codigo\outputs\results\swin_tiny_sweep_t06_les_cwnone_{s43,s44}_test_results.json` y `convnext_tiny_sweep_t02_les_cwnone_{s43,s44}_test_results.json` (existen); `W\Codigo\docs\ideas\criterio_seleccion_plan_20260917.md` | — |
| P13 | Ensamble por voto suave: promedio aritmético de las probabilidades (con TTA) de Swin-Tiny t06 y ConvNeXt-Tiny t02; la clase predicha es la de mayor probabilidad media. Solo ese par: son los ganadores elegidos en validación, y otra combinación requeriría mirar el test. El mismo promedio sirve para P14; el ruteo de 3.8 usa solo el Swin con el kNN de DermLIP | `W\Codigo\scripts\classifier_ensemble.py` l. 1–12 (voto suave, preset `les`), l. 133 (`np.mean(... axis=0)`); `W\Codigo\scripts\lesion_split_report.py` (ensamble de melanoma) | sec:marco_senales_confianza (voto suave, Cap. 2) |
| P14 | Detección de melanoma: tarea binaria MEL contra el resto (clase 0 de HAM10000); puntaje = probabilidad de MEL (del modelo o del promedio). Umbral: entre los puntos de la curva ROC de validación con especificidad ≥ 0.85, el de mayor sensibilidad; se aplica sin cambios al test. AUC y PR-AUC no dependen del umbral. Con la misma tarea derivada, el script calcula también maligno frente a benigno (ver «Preguntas») | `W\Codigo\scripts\melanoma_detection.py` l. 29–31 (orden de clases, MEL = 0), l. 59–63 (`_thr_at_spec`: máxima sensibilidad con especificidad ≥ objetivo), l. 85–101 (`_task_report`, umbral ajustado en validación); `W\Codigo\scripts\lesion_split_report.py` (`_task_report` con `yv, pv`) | Cap. 2: `sec:marco_eval_clasif`, `eq:marco_sens_esp`, `eq:marco_auc`; 3.4: `sec:met_seleccion` |

## Figuras y tablas

No se propone figura: la receta cabe en tablas. Las cifras van en tablas en el cuerpo y las grillas completas al apéndice.

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Tabla A (3.5.1) | Los cuatro modelos: familia, variante, preentrenamiento, cabeza, parámetros, tamaño de lote | `src/models/classifiers.py`; logs de entrenamiento (parámetros); `scripts/train_classifier.py` l. 315 (lote 32 ó 16) | a armar |
| Tabla B (3.5.3) | Receta moderna y legacy lado a lado: optimizador; tasa; decaimiento de pesos; épocas; etapas; decaimiento por capa; calentamiento; planificador; suavizado; pesos por clase; paciencia; lote; aumentos; TTA; focal | `recipes.py` (`legacy`, `modern`); `submit_sweep.py` l. 146–156; `submit.py` l. 41–81 y 102–163 | a armar |
| Tabla C (3.5.4) | Barrido moderno: parámetro, valores explorados, forma de asignación y valor fijo | `configs/sweeps/phase1_modern_sweep_grid.yaml`; `submit_sweep.py`; `split_lesion_resul_20260926.md` §2 | a armar |
| Apéndice A | Las 15 combinaciones del barrido moderno con su M; la lista de las 28 configuraciones legacy (sin métricas); los comandos de los ganadores y de la réplica | `phase1_modern_sweep_grid.yaml`; `M\Codigo\wandb_sweep_phase1.csv` (solo columnas de configuración); `submit.py` | a armar |

## Prosa ya escrita que se conserva

Ninguna: las dos subsecciones de origen tienen solo `\pendiente{}`. Lo que sí se conserva es el `\label{sec:met_modelos}`: se elimina, porque nadie lo cita.

## Lo que va al apéndice

- Las 15 combinaciones del barrido con su magnitud de RandAugment (Apéndice A, `ap:hiperparametros`).
- Las 28 configuraciones de la búsqueda legacy (valores, sin métricas).
- Los comandos y banderas de cada ganador y de cada corrida de la réplica (`ap:reproducibilidad`, Apéndice E, si se decide allí).

## Lo que NO va en esta sección (y dónde está)

- **Ningún desempeño** (exactitud, sensibilidad, F1, AUC, ECE, ruteo, Grad-CAM): va a Caps. 4 y 5. La réplica del desbalance se describe por su configuración, no por lo que dio.
- **Las corridas sobre la partición con fuga y los modelos v3 y v4** (`*_modern_v3`, `*_sweep_*` sin `_les`, `swin_tiny_modern_v3`): quedan fuera de 3.5. Su mención, si corresponde, va en Cap. 4 como declaración de la partición anterior.
- **Las combinaciones de cuatro modelos** (Swin, DenseNet, ViT y ConvNeXt): se evaluaron después de elegir el ensamble, sobre el test; no son reportables como ganador (`split_lesion_resul_20260926.md` §3).
- **HIBA** (validación externa de los ganadores): va a 3.9 (`sec:met_complementarios`) o al Cap. 4, según se decida.
- **Calibración post-hoc, ruteo de tres niveles, *grounding* y RAG**: van a 3.9 y 3.8.
- **Historia de las recetas** (MixUp desactivado en una versión anterior, focal γ = 2 de la receta v1, decaimientos probados en versiones v1–v3): está en `ejecuciones.md` y en el historial; en 3.5 solo se dice qué se usó.
- **El criterio de selección del 17/09 y su evolución**: la justificación es de 3.4. En 3.5 se referencia `sec:met_seleccion`.

## Preguntas abiertas para el autor

1. **Comparación confundida entre recetas.** DenseNet y ViT (legacy) se entrenaron con pesos por clase `auto` y sin TTA; los ganadores (receta moderna) sin pesos y con TTA. Cualquier comparación entre legacy y moderna mezcla la receta con el manejo del desbalance. ¿Lo declaro así en 3.5 (propuesta: sí, en P9) y lo tomo en Cap. 4? No propongo re-correr las legacy.
2. **Motivo de excluir DenseNet y ViT del barrido.** El plan v4 §1 invoca la incompatibilidad «con BatchNorm + augmentación agresiva». ViT no usa BatchNorm (usa LayerNorm), así que ese motivo no lo cubre. ¿Qué motivo escribo para ViT?
3. **Búsqueda legacy con criterio distinto.** Se eligió por F1 ponderado de validación (criterio anterior al 17/09); el barrido moderno, por F1 macro. ¿Lo declaro en P11 (propuesta: sí, con la frase de P11)?
4. **Dónde van las ablaciones de la receta.** El cierre de Cap. 3 las declara sobre la partición anterior. ¿Una oración en P9 con remisión a Cap. 4, o van a 3.9?
5. **Tasa de la réplica del desbalance.** Las corridas `imb_*` usan la tasa de `_CLS_LR` (1e-4 para Swin y ConvNeXt; 7.91e-5 para DenseNet), no la del trial ganador, y no hubo búsqueda para cada pérdida. Propuesta: decirlo en P8 como decisión de diseño de la réplica. ¿Confirmás?
6. **Maligno frente a benigno.** `melanoma_detection.py` y `lesion_split_report.py` calculan también la tarea MEL+BCC+AKIEC contra el resto. ¿Se reporta en Cap. 4? Si sí, una oración en P14 la define.
7. **Parámetros de DenseNet121.** `costo_resul_20260705.md` da 8.0 M, que corresponde a la cabeza de 1000 clases. Los logs (cabeza de 7) dan 6.96 M. Usé los logs. ¿Confirmás?
8. **Número de configuraciones legacy.** El texto de `clasificadores_resul_iteraciones_20260429.md` §7.3 dice «25+»; la exportación tiene 28 filas (15 + 13). Usé 28; el documento debería corregirse en Cap. 4 si se cita.
9. **«Tiny» por cómputo.** La justificación de las variantes Tiny es mía, a partir de la restricción de 3.1 (GPU de consumo). ¿Querés que lo diga así o lo atribuyo a otra fuente?
10. **Frase «todo con TTA».** `split_lesion_resul_20260926.md` §2 dice «Todo con TTA», pero los JSON de DenseNet y ViT legacy tienen `tta: false`. No afecta 3.5 (que dice que legacy no usa TTA), pero el resultado del Cap. 4 no debe repetir la frase.
11. **Tamaño original de HAM10000.** No está en el repositorio. Si el texto de 3.3 lo da (600 × 450, a verificar), P3 lo retoma para explicar la deformación al pasar a cuadrado.

## Decisiones tomadas por cuenta propia

1. **La fuente de los valores son el código que se ejecutó** (`recipes.py`, `train_classifier.py`, `submit_sweep.py`, `submit.py`, `phase1_modern_sweep_grid.yaml`), no los `configs/*.yaml`. Los `configs/models/*.yaml` dicen en sus comentarios que `train_classifier.py` «NO lee este YAML», y `phase1_classification.yaml` tiene una configuración base (30 épocas, tasa 1e-4, cosenoide) que no coincide con las corridas reportadas (las legacy usan 7.91e-5 y 1.56e-5, y la moderna 40 épocas). Recomiendo no citar los YAML como fuente en 3.5 y actualizarlos o marcarlos como documentación.
2. **Focal γ en la receta moderna.** `recipes.py` define `focal_gamma=1.0` para `modern`, pero los barridos y las réplicas modernas pasan `--focal-gamma 0` o `2.0` explícito. En 3.5 se describe el valor efectivo (0 en el barrido). El comentario de `recipes.py` que dice «capas tempranas reciben ~20 % de base_lr» no coincide con 0.85^9 ≈ 0.23 (Swin); la ficha usa el cálculo.
3. **Términos de Cap. 2 sin repetir.** La lista de P6, P8 y P9 nombra los conceptos con `\ref`; no se vuelven a definir. Las siglas (CNN, ViT, TTA, AUC, VLM) se usan con `\gls{}`, ya declaradas; **LLRD no se usa como sigla**: se escribe «decaimiento de la tasa por capa (*layer-wise learning rate decay*)». La primera aparición en el capítulo lleva cursiva.
4. **Nombres de versión fuera del texto.** En el documento se dice «receta moderna» y «receta legacy», no «modern v3», «v4» ni «legacy_les». Los nombres internos de corrida no aparecen en el cuerpo, solo en la tabla de trials (`t02`, `t06`).
5. **La variante de pesos forma parte del trial.** `lesion_split_report.py` (l. 98) rankea las dos variantes de pesos juntas por F1 macro, así que la ficha describe el ganador con su variante. `criterio_seleccion_plan_20260917.md` (tabla «Los dos niveles») aplica el F1 macro al trial y deja el F1 ponderado al *checkpoint*; su frase sobre la «pérdida» es ambigua. Conviene que 3.4 use la misma formulación.
6. **Contador de paciencia compartido** entre las dos etapas (así lo implementa `train_classifier.py`, con un único `callbacks`). Se describe como tal.
7. **Número de corridas.** 60 (barrido) + 2 (legacy) + 12 (réplica) = 74, que coincide con `split_lesion_resul_20260926.md` §2. Se suman 4 semillas de los dos ganadores (verificadas en los JSON). No cuento los `_hiba` (reejecuciones de validación externa). Los trabajos SLURM de 97933–98246 no los revisé uno por uno.
8. **Sin figura en 3.5.** La receta se muestra en tablas; el diagrama de flujo va en 3.2 y el de la cascada en 3.8.
9. **Preguntas abiertas aplicadas en la redacción** (las que proponían opción): 1 (legacy con vista única y pesos por clase, declarado en P9), 3 (búsqueda legacy por F1 ponderado, declarado en 3.5.4), 4 (ablaciones en Cap. 4, con remisión en P9), 5 (réplica del desbalance con tasa fija, declarado en P8), 7 (parámetros de los logs), 8 (28 configuraciones), 9 (Tiny por la restricción de 3.1, sin atribución).
10. **Preguntas sin opción en el `.tex`, como `\pendiente{}`:** 2 (motivo de excluir DenseNet121 y ViT-B/16 del barrido, en P2) y 6 (maligno frente a benigno, al final de 3.5.5). La 10 no afecta a 3.5 y la 11 no se usa.
11. **Cita no usada:** `kittler2016standardization` tiene por título «Standardization of terminology in dermoscopy» y no respalda el aumento de datos de P4. Se citan `cubuk2020randaugment`, `zhong2020random` y `shorten2019survey`. La ficha debe corregirse o proponer otra fuente.
12. **Acrónimo nuevo propuesto** (GPU, en texto llano en P1): `\acronimo{gpu}{GPU}{unidad de procesamiento gráfico}{Graphics Processing Unit}`.
13. **PR-AUC omitido:** no está declarada ni aparece en los resultados citados. Solo se usa AUC.
14. **Réplica del desbalance:** `submit.py` no pasa `--weight-decay` ni `--randaugment-m` en `imb_*`, así que toman 0.05 y M = 9 de la receta moderna. La tasa es la de `_CLS_LR`. Verificado en el código y en el texto de P8.
15. **Inconsistencia en el repositorio:** `configs/sweeps/phase1_sweep.yaml` declara `method: bayes`, pero `sweep_utils.generate_combinations` muestrea al azar, que es lo que el texto describe. Conviene corregir el yaml o su comentario.
16. **Verificación:** las tablas A, B y C y los valores de P1–P14 se comprobaron contra el código (`recipes.py`, `train_classifier.py`, `submit_sweep.py`, `submit.py`, `transforms.py`, `optim_groups.py`, `losses.py`, `tta.py`, `lesion_split_report.py`), los logs (parámetros), el CSV legacy (mejores configuraciones) y `split_lesion_resul_20260926.md`. Los JSON de semillas 43 y 44 existen.
