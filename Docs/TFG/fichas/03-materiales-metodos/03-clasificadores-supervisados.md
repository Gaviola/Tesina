# Ficha 3.4 — Clasificadores supervisados

**Revisión del autor (20/10/2026):** sale la oración «En cada familia hay un modelo anterior y uno más reciente…» (no aportaba) y «Todos se entrenan en una GPU de consumo» (ya dicho en 3.1); las dos etapas se describen como extracción de características y luego ajuste fino, las dos opciones de `sec:marco_transferencia`, con el motivo de la primera (no partir de una cabeza al azar); la apertura remite a `sec:met_seleccion` (desaparece `sec:met_lineas_base`) y llama línea base a los clasificadores.

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Ahora es 3.4 (antes 3.5). Solo la configuración final: sin «receta moderna/anterior», sin las corridas legacy de DenseNet121 y ViT-B/16 ni su búsqueda aleatoria, sin la subsección de búsqueda (queda un párrafo y la tabla de valores explorados y elegidos), sin la oración que prometía las ablaciones de la receta (no tienen fuente). DenseNet121 y ViT-B/16 usan la configuración ganadora de su familia, explicado en una oración.

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita en la revisión del 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/04-clasificadores-supervisados.tex` (antes `05-clasificadores-supervisados.tex`). Labels: `sec:met_supervisados` (sección) y `sec:met_supervisados_arquitecturas`, `sec:met_supervisados_preprocesamiento`, `sec:met_supervisados_receta`, `sec:met_supervisados_ensamble` (subsecciones). Desaparece `sec:met_supervisados_busqueda`: la búsqueda ya no es subsección. Tablas: `tab:met_modelos_sup`, `tab:met_receta`, `tab:met_barrido`.

Sale de: la subsección «Clasificadores supervisados» de `03-modelos-evaluados.tex` (solo `\pendiente`, sin prosa que conservar) y la subsección «Preprocesamiento y aumento de datos» de `02-datos-particiones.tex` (`\pendiente`, sin prosa). `sec:met_modelos` desaparece (ningún `\ref` la usa).

## Hilo conductor

Pregunta que responde la sección: ¿qué clasificadores supervisados se entrenan, con qué preprocesamiento, receta e hiperparámetros, y cómo se obtiene de ellos una probabilidad de melanoma?

Viene de: 3.3 fija el criterio con el que se juzgan los modelos (sensibilidad macro como resultado principal; F1 ponderado en validación para la época; F1 macro en validación para la configuración; la prueba no interviene; umbral de melanoma con especificidad ≥ 0.85 fijado en validación; media ± desvío de tres semillas) y las líneas base, entre ellas la de que los clasificadores supervisados son la referencia de los VLM (`sec:met_lineas_base`). 3.2 deja la partición disjunta por lesión (6447 imágenes de entrenamiento) y el desbalance de las siete clases. El Cap. 2 deja las arquitecturas (2.2), la receta general y el desbalance (2.1) y el ensamble por voto suave (`sec:marco_senales_confianza`).

Deja instalado: los cuatro modelos con una misma receta; el par de la búsqueda (Swin-Tiny y ConvNeXt-Tiny) con su ensamble; la probabilidad de melanoma y su umbral. Para 3.5: estos clasificadores producen una probabilidad por clase y no texto, y se los compara con las mismas métricas con un VLM (PI1).

```
Introducción de la sección (sin subsección)
P1  Dos funciones de los clasificadores: referencia con la que se juzga si un VLM clasifica bien
    (`sec:met_lineas_base`) y, dentro del pipeline, quienes fijan el diagnóstico; anuncia el orden:
    arquitecturas, preprocesamiento, entrenamiento e hiperparámetros, ensamble y melanoma          función: justifica
    ↓ necesidad — antes del procedimiento, qué modelos son

3.4.1 Arquitecturas (sec:met_supervisados_arquitecturas)
P2  Cuatro arquitecturas, dos convolucionales (DenseNet121, ConvNeXt-Tiny) y dos transformers (ViT-B/16,
    Swin-Tiny); en cada familia un modelo anterior y uno más reciente (compara tipos y generaciones);
    pesos de ImageNet-1K y cabeza de siete salidas con dropout 0.3 (`tab:met_modelos_sup`); GPU de
    consumo, las variantes Tiny tienen un tercio de los parámetros de ViT-B/16                       función: define · justifica
    ↓ necesidad — qué le llega a los modelos: la imagen que se les da y cómo se la varía

3.4.2 Preprocesamiento y aumento de datos (sec:met_supervisados_preprocesamiento)
P3  Imágenes de 224 × 224 normalizadas con ImageNet; con 6447 imágenes de entrenamiento el riesgo es el
    sobreajuste; aumentos que cambian la imagen sin cambiar la clase (recorte 70–100 %, volteo,
    RandAugment con M de `tab:met_barrido`, borrado aleatorio p = 0.25)                               función: describe · justifica
    ↓ contraste — el aumento solo vale en entrenamiento; en validación y prueba la entrada es fija
P4  Validación y prueba: Resize 256 y recorte central 224; probabilidades con TTA (imagen y su reflejo
    horizontal); la salida de cada clasificador es una probabilidad por clase, de la que se calculan
    las métricas de 3.3                                                                               función: describe · define
    ↓ necesidad — con la entrada fija, cómo se entrena

3.4.3 Entrenamiento e hiperparámetros (sec:met_supervisados_receta)
P5  Ajuste en dos etapas (una época solo la cabeza; luego toda la red con decaimiento de la tasa por
    capa 0.85, tres épocas de calentamiento y coseno, hasta 39 épocas); AdamW; entropía cruzada con
    suavizado de 0.1; detención temprana con paciencia 5 sobre el F1 ponderado, y se conserva la mejor
    época (`sec:met_seleccion`); `tab:met_receta` reúne los valores comunes                        función: describe · define
    ↓ necesidad — algunos valores de la receta no se fijan de antemano: se buscan
P6  Búsqueda en grilla de tasa de aprendizaje, decaimiento de pesos y magnitud de RandAugment
    (`tab:met_barrido`), con y sin pesos por clase: 30 configuraciones por modelo; hecha sobre Swin-Tiny
    y ConvNeXt-Tiny, ganó por F1 macro en validación una configuración sin pesos por clase; DenseNet121
    y ViT-B/16 usan la configuración ganadora de su familia (la de ConvNeXt y la de Swin) con la salvedad
    de que puede no ser la mejor para ellos; grilla completa en el Apéndice A                         función: describe · justifica · limita
    ↓ ampliación — los pesos por clase no son la única forma de tratar el desbalance
P7  Comparación aparte de cuatro pérdidas (entropía cruzada sin pesos, con pesos inversos a la
    frecuencia, focal con γ = 2, *balanced softmax*) sobre Swin-Tiny, ConvNeXt-Tiny y DenseNet121, con
    el resto de los hiperparámetros fijos (decaimiento 0.05, M = 9, tasa 10⁻⁴ o 7.91 × 10⁻⁵ en
    DenseNet121) y una sola semilla                                                                   función: define · justifica · limita
    ↓ ampliación — con los modelos entrenados y elegidos, el paso siguiente es combinarlos

3.4.4 Ensamble y detección de melanoma (sec:met_supervisados_ensamble)
P8  Ensamble por voto suave de Swin-Tiny y ConvNeXt-Tiny, los dos de la búsqueda; solo ese par porque son
    los que eligió la validación y otra combinación exigiría mirar la prueba; la detección de melanoma
    usa la probabilidad de melanoma de cada modelo o del ensamble, con el umbral de 3.3               función: define · justifica
    ↓ contraste — estos modelos devuelven una probabilidad y no generan texto
P9  Los clasificadores no generan texto; para saber si un VLM, que sí lo genera, clasifica tan bien, se
    los compara con las mismas métricas                                                                función: justifica
→ Transición a 3.5: P9 (sin `\ref`; hoy 3.5 no se nombra por label desde acá).

Se definen acá (y no se vuelven a definir): los cuatro modelos y su cabeza; la receta única de entrenamiento (`tab:met_receta`); la estrategia de búsqueda (15 combinaciones con M asignada en rotación, por pesos de clase) y la regla de heredar la configuración de la familia; la comparación de las cuatro pérdidas; el par del ensamble.
Se retoman de antes (solo se nombran, con `\ref`): CNN, ViT y Swin (`sec:marco_cnn`, `sec:marco_vit`, `sec:marco_swin`); sobreajuste, detención temprana, aumento de datos, borrado aleatorio y TTA (`sec:marco_regularizacion`); transferencia en dos etapas y decaimiento de la tasa por capa (`sec:marco_transferencia`, `eq:marco_llrd`); desbalance, pesos por clase, focal y *balanced softmax* (`sec:marco_desbalance`); voto suave (`sec:marco_senales_confianza`); criterio de selección, líneas base y umbral de melanoma (3.3: `sec:met_seleccion`, `sec:met_lineas_base`); partición (3.2: `sec:met_particiones`).
Extensión: 9 párrafos, unas 3.5–4 páginas, en cuatro subsecciones y tres tablas.

## Subsecciones

- **Introducción de la sección** (P1): sin subsección.
- **3.4.1 Arquitecturas** (`sec:met_supervisados_arquitecturas`): P2, con `tab:met_modelos_sup`.
- **3.4.2 Preprocesamiento y aumento de datos** (`sec:met_supervisados_preprocesamiento`): P3 y P4.
- **3.4.3 Entrenamiento e hiperparámetros** (`sec:met_supervisados_receta`): P5 a P7, con `tab:met_receta` y `tab:met_barrido`.
- **3.4.4 Ensamble y detección de melanoma** (`sec:met_supervisados_ensamble`): P8 y P9.

## Contenido por párrafo

Rutas relativas a `W\Codigo\` salvo indicación. Las líneas de `train_classifier.py` y de los scripts son las verificadas al escribir la ficha.

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Los clasificadores son la referencia de los VLM y, en el pipeline, fijan el diagnóstico. Anuncia las partes de la sección. | Ninguno. | — |
| P2 | DenseNet121 (CNN, bloques densos), ConvNeXt-Tiny (CNN moderna), ViT-B/16 (transformer con parches de 16 × 16), Swin-Tiny (transformer jerárquico con ventanas). **Un modelo anterior y uno más reciente por familia** (justificación agregada por la revisión; ver «Decisiones»). Preentrenados con pesos ImageNet-1K; cabeza `Dropout(0.3)` + lineal de 7 salidas. Una GPU de consumo (3.1); las variantes Tiny, de unos 27.5 millones de parámetros, tienen un tercio de los de ViT-B/16. Parámetros con cabeza de 7 clases: DenseNet121 6 961 031; ConvNeXt-Tiny 27 825 511; ViT-B/16 85 804 039; Swin-Tiny 27 524 737. Lote 32 (DenseNet, ConvNeXt) o 16 (ViT, Swin). | Pesos: `src/models/classifiers.py` (DenseNet l. 15, ConvNeXt l. 57, Swin l. 100, ViT l. 136). Cabeza: mismas clases, l. 18–23, 60–66, 103–107, 139–144. Parámetros: `M\Codigo\outputs\logs\*` (líneas «Modelo: <m> \| Parámetros»). Lote: `scripts/train_classifier.py` l. 315. Las cifras de `costo_resul_20260705.md` (8.0 M para DenseNet121) no coinciden con las de los logs: se usan los logs. | Cap. 2: `sec:marco_cnn`, `sec:marco_vit`, `sec:marco_swin`. El `.tex` no cita aquí `dosovitskiy2021image`, `liu2021swin`, `huang2018densely`, `liu2022convnet` ni `russakovsky2015imagenet` (están en el Cap. 2) |
| P3 | Las imágenes llegan a 224 × 224 y se normalizan con la media y el desvío de ImageNet. Con 6 447 imágenes de entrenamiento el riesgo es el sobreajuste. Aumentos: recorte aleatorio de 70–100 % del área; volteo horizontal (p = 0.5); dos transformaciones de RandAugment con magnitud M (`tab:met_barrido`); borrado aleatorio con p = 0.25. | `W\Codigo\scripts\prepare_data.py` l. 31 y 81–93 (`IMAGE_SIZE = 224`); `W\Codigo\src\data\transforms.py` (`IMAGENET_MEAN/STD` l. 4–5; rama `randaugment`, `random_erasing`, `rrc_scale_min`, l. 8–54); `W\Codigo\src\training\recipes.py` (`randaugment_n` 2, `random_erasing` 0.25, `rrc_scale_min` 0.7); 6 447 de `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §2. | `cubuk2020randaugment`, `zhong2020random`; Cap. 2: `sec:marco_regularizacion`, `sec:met_particiones` (3.2) |
| P4 | Validación y prueba: `Resize(256)` + `CenterCrop(224)`. TTA: se promedian las probabilidades de la imagen y de su reflejo horizontal. La salida es una probabilidad por clase, de la que se calculan las métricas de 3.3. | `W\Codigo\src\data\transforms.py` (`get_val_transforms` l. 57–78); `scripts/train_classifier.py` l. 275 y 286; `W\Codigo\src\evaluation\tta.py` l. 15–72 (`tta_modes=("original","hflip")`, promedio `probs_sum / len(modes)`); `scripts/train_classifier.py` l. 489–491 (prueba) y 549–553 (validación con `--save-val-predictions`). | `krizhevsky2012imagenet` (TTA); `sec:marco_regularizacion`; `sec:met_protocolo` (3.3) |
| P5 | Dos etapas. Etapa 1: una época, red congelada, solo la cabeza. Etapa 2: toda la red, decaimiento de la tasa por capa con factor 0.85, calentamiento lineal de 3 épocas desde 0.1 de la tasa y coseno; hasta 39 épocas (40 en total). AdamW; entropía cruzada con suavizado de etiquetas 0.1. Detención temprana: paciencia 5 sobre el F1 ponderado de validación, se conserva la mejor época. bf16. `tab:met_receta`. | `W\Codigo\scripts\train_classifier.py` l. 391–446 (etapas 1 y 2), l. 386–387 (`EarlyStopping(patience, monitor="val_f1")`, `CheckpointCallback`); `W\Codigo\src\training\optim_groups.py` l. 20–72 (`get_llrd_groups`); `W\Codigo\src\training\schedulers.py` l. 16–63 (`build_scheduler`, `LinearLR` con `start_factor=0.1`); `W\Codigo\src\training\recipes.py` (`modern`); `W\Codigo\src\training\trainer.py` l. 188 (`val_f1` ponderado); `W\Codigo\src\utils\device.py` l. 13–25 (bf16). | `loshchilov2019decoupled` (AdamW), `szegedy2016rethinking`, `muller2019does` (suavizado), `goyal2017accurate` (calentamiento), `loshchilov2017sgdr` (coseno); Cap. 2: `sec:marco_transferencia`, `eq:marco_llrd`; 3.3: `sec:met_seleccion` |
| P6 | Búsqueda: 5 tasas × 3 decaimientos de pesos = 15 combinaciones, con M ∈ {6, 9, 12} asignada en rotación (cada valor en cinco combinaciones), por dos pesos de clase (inversos a la frecuencia; ninguno) = 30 por modelo. Se hizo sobre Swin-Tiny y ConvNeXt-Tiny; ganó por F1 macro en validación: Swin-Tiny, tasa 7.5e-5, decaimiento 0.10, M = 6, sin pesos; ConvNeXt-Tiny, tasa 3.0e-5, decaimiento 0.05, M = 9, sin pesos. DenseNet121 usa la de ConvNeXt-Tiny; ViT-B/16, la de Swin-Tiny. Salvedad: un resultado peor puede deberse a la configuración heredada. Grilla completa en el Apéndice A. | `W\Codigo\configs\sweeps\phase1_modern_sweep_grid.yaml` l. 18–41 (15 trials); `W\Codigo\scripts\toko\submit_sweep.py` l. 146–156; `W\Codigo\scripts\lesion_split_report.py` l. 71–110 (ranking por `val.f1_macro`, ganador entre las dos variantes de pesos); `W\Codigo\docs\resul\split_lesion_resul_20260926.md` §2–§3; `W\Codigo\docs\ideas\densenet_vit_moderna_plan_20261012.md` y `W\Codigo\docs\resul\densenet_vit_moderna_resul_20261017.md` §1 (DenseNet121 con el t02 de ConvNeXt y ViT-B/16 con el t06 de Swin, semillas 42, 43 y 44). | — |
| P7 | Las cuatro pérdidas: (1) entropía cruzada sin pesos; (2) con pesos inversos a la frecuencia; (3) focal con γ = 2; (4) *balanced softmax* (suma a cada logit el logaritmo de la frecuencia de su clase). Sobre Swin-Tiny, ConvNeXt-Tiny y DenseNet121, con el mismo procedimiento. Fijos: decaimiento de pesos 0.05, M = 9 y tasa 10⁻⁴ (7.91 × 10⁻⁵ en DenseNet121); una sola semilla. | `W\Codigo\src\training\losses.py` l. 19–141 (`FocalLoss`, `BalancedSoftmaxLoss`, `build_loss`); `W\Codigo\scripts\train_classifier.py` l. 49–57 y 370; `W\Codigo\scripts\toko\submit.py` l. 41–46 (`_CLS_LR`) y l. 102–163 (`imb_*`: `--focal-gamma 0 --class-weights none\|auto`, `--focal-gamma 2.0`, `--balanced-softmax`). `submit.py` no pasa `--weight-decay` ni `--randaugment-m` en `imb_*`: toman 0.05 y M = 9. | `lin2017focal`, `ren2020balanced`; Cap. 2: `sec:marco_desbalance` |
| P8 | Voto suave: promedio de las probabilidades de Swin-Tiny y ConvNeXt-Tiny; la clase predicha es la de mayor promedio. Solo ese par: son los que eligió la validación. Detección de melanoma: puntaje = probabilidad de melanoma de cada modelo o del ensamble, con el umbral de 3.3. | `W\Codigo\scripts\classifier_ensemble.py` l. 1–12 (voto suave, preset `les`), l. 133 (`np.mean(... axis=0)`); `W\Codigo\scripts\melanoma_detection.py` l. 59–63 (`_thr_at_spec`), l. 85–101 (umbral ajustado en validación), l. 154 (ensamble). | Cap. 2: `sec:marco_senales_confianza`; 3.3: `sec:met_seleccion` |
| P9 | Los clasificadores devuelven una probabilidad por clase y no generan texto; se los compara con un VLM con las mismas métricas. | Ninguno. | — |

## Figuras y tablas

No se propone figura: la receta cabe en tablas. Las cifras van en tablas en el cuerpo y las grillas completas al apéndice.

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `tab:met_modelos_sup` (3.4.1) | Los cuatro modelos: familia, pesos iniciales, cabeza, parámetros, tamaño de lote | `src/models/classifiers.py`; logs de entrenamiento; `scripts/train_classifier.py` l. 315 | redactada |
| `tab:met_receta` (3.4.3) | Parámetros de entrenamiento comunes a los cuatro: optimizador, épocas, decaimiento por capa, planificador, pérdida, detención temprana, aumentos, inferencia, precisión numérica, semillas | `recipes.py` (`modern`); `submit_sweep.py` l. 146–156 | redactada |
| `tab:met_barrido` (3.4.3) | Hiperparámetros explorados (tasa, decaimiento de pesos, M, pesos por clase) y valores elegidos para Swin-Tiny y ConvNeXt-Tiny | `configs/sweeps/phase1_modern_sweep_grid.yaml`; `submit_sweep.py`; `split_lesion_resul_20260926.md` §2 | redactada |
| Apéndice A (`ap:hiperparametros`) | Las 15 combinaciones con su M; los comandos de los ganadores y de la comparación de pérdidas. Hoy el apéndice es un `\pendiente` | `phase1_modern_sweep_grid.yaml`; `submit.py` | a armar |

## Lo que va al apéndice

- Las 15 combinaciones del barrido con su magnitud de RandAugment (Apéndice A, `ap:hiperparametros`), y los hiperparámetros de DenseNet121 y ViT-B/16 (los heredados), las configuraciones de las pérdidas frente al desbalance y la configuración de LoRA (lo que enumera su `\pendiente`).
- Los comandos y banderas de cada ganador y de cada corrida de la comparación de pérdidas (`ap:reproducibilidad`, Apéndice E, si se decide allí).

## Lo que NO va en esta sección (y dónde está)

- **Ningún desempeño** (exactitud, sensibilidad, F1, AUC, ECE, ruteo, Grad-CAM): va a Caps. 4 y 5. La comparación de pérdidas se describe por su configuración, no por lo que dio.
- **Las corridas sobre la partición con fuga y los modelos v3 y v4**: quedan fuera. Su mención, si corresponde, va en el Cap. 4 como declaración de la partición anterior.
- **Las combinaciones de cuatro modelos** (Swin, DenseNet, ViT y ConvNeXt): se evaluaron después de elegir el ensamble, sobre la prueba; no son reportables como ganador (`split_lesion_resul_20260926.md` §3).
- **HIBA, calibración post-hoc, perturbaciones y Grad-CAM**: 3.8 (`sec:met_complementarios`). **Ruteo de tres niveles, *grounding* y RAG**: 3.7.
- **Historia de las recetas** (MixUp, focal γ = 2 de la receta anterior, decaimientos probados en versiones previas): está en `ejecuciones.md`; acá solo se dice qué se usó.
- **El criterio de selección y su evolución**: la justificación es de 3.3 (`sec:met_seleccion`).

## Quitado en la revisión del 18/10/2026

Contenido de la versión anterior de la ficha y del `.tex` que ya no está en el texto. Se conserva acá para no perder las fuentes.

- **Dos recetas («moderna» y «legacy») y la tabla B lado a lado**: hay una sola receta (R2, D-B). Fuentes: `recipes.py` l. 62–88; `submit.py` l. 41–81.
- **Párrafo de DenseNet121 y ViT-B/16 «con la receta anterior», réplicas y TOKO 99007–99012 «completos el 14/10»**, decisión del autor del 2026-10-12: fechas e historia del proceso (R1, R2, D-B). Fuentes: `densenet_vit_moderna_plan_20261012.md`, `densenet_vit_moderna_resul_20261017.md` §1, `submit.py` (`les_densenet_legacy`, `les_vit_legacy`).
- **Preprocesamiento de la receta legacy** (`Resize((224, 224))` sin preservar proporción) **y su aumento** (rotación de hasta 30°, `ColorJitter` con brillo, contraste y saturación 0.2 y tono 0.1; sin TTA): receta anterior (R2, D-B). Fuente: `transforms.py`, `recipes.py` l. 62–68.
- **Receta legacy como párrafo (P9 anterior)**: una etapa, AdamW, sin suavizado ni calentamiento, 30 épocas, paciencia 5, pesos por clase `auto` por defecto, sin TTA; y **la declaración de que las ablaciones de la receta se hicieron sobre la partición anterior y van al Cap. 4** (R2, D-B, D-E: no tienen resultados ni en local ni en TOKO). Fuentes: `recipes.py` l. 62–68, `train_classifier.py` l. 104 y 118–119, `split_lesion_resul_20260926.md` §8.
- **Búsqueda legacy** (28 corridas aleatorias: 15 de DenseNet121 y 13 de ViT-B/16; tasa log-uniforme entre 1e-5 y 1e-3, decaimiento en {0, 0.001, 0.01, 0.1}, planificador en {coseno, ninguno}, suavizado en {0, 0.05, 0.1}, congelar el *backbone* en {sí, no}, 30 épocas; elegidas por F1 ponderado; valores elegidos: DenseNet121 tasa 7.91e-5, decaimiento 0.01; ViT-B/16 tasa 1.56e-5, decaimiento 0.01): D-B. Fuentes: `configs/sweeps/phase1_sweep.yaml` l. 1–70; `scripts/sweep_utils.py` l. 55–66; `M\Codigo\wandb_sweep_phase1.csv`; `clasificadores_resul_iteraciones_20260429.md` §7.3.
- **Subsección «Búsqueda de hiperparámetros y semillas»** (`sec:met_supervisados_busqueda`, P10 a P12): la búsqueda queda en un párrafo y `tab:met_barrido` dentro de 3.4.3 (revisión del 18/10; R2).
- **Motivos de la estrategia del barrido**: lista predefinida y no un agente de W&B porque los nodos de TOKO no tienen internet; semilla 42 y valores fijos (40 épocas, focal γ = 0, suavizado 0.1) como lista aparte; trial elegido «entre las 30 corridas del modelo». Es registro de experimentos y de infraestructura (R1). Fuentes: `submit_sweep.py` l. 1–25; `clasificadores_sweep_modern_v4_plan_20260510.md` §4.
- **Motivo de excluir DenseNet121 y ViT-B/16 del barrido** (incompatibilidad «con BatchNorm + augmentación agresiva»; no cubre a ViT): el texto no da ese motivo, solo que heredan la configuración de su familia para compararlos con el mismo procedimiento. Fuente: `clasificadores_sweep_modern_v4_plan_20260510.md` §1.
- **Detalles de implementación**: un único contador de paciencia que cruza las dos etapas; recarga del *checkpoint* para el test (`--eval-best-checkpoint`); tasa de la etapa 1 «del trial» y sin planificador; Swin con 10 grupos (la entrada recibe 0.85⁹ ≈ 0.23 de la tasa de la cabeza); sin MixUp ni CutMix; focal γ = 0 en la receta (R1: importan al equipo, no al lector). Fuentes: `train_classifier.py` l. 386–387, 399, 416–446, 476–479; `optim_groups.py` l. 135–153.
- **Pérdidas «en lista»** (P8 anterior): el texto las describe en prosa corrida. **Pesos por clase como `total/(C·n_c)`** (fórmula): el texto dice «inversos a la frecuencia». Fuente: `train_classifier.py` l. 49–57.
- **Ganadores con nombre de *trial* (`t06`, `t02`) y semillas 43 y 44 «solo para los ganadores»**: el texto da los valores de `tab:met_barrido` sin nombres internos (decisión 4 anterior); las semillas figuran en `tab:met_receta`. Fuente: `split_lesion_resul_20260926.md` §2–§3; JSON de semillas 43 y 44 en `M\Codigo\outputs\results\`.
- **Aclaración «legacy y réplica con una sola semilla; su desvío no se estimó»**: queda solo que la comparación de pérdidas usa una semilla.
- **Número total de corridas** (60 + 2 + 12 = 74, más 4 semillas de los ganadores): registro de experimentos (R1). Fuente: `split_lesion_resul_20260926.md` §2.
- **Mención de que el ruteo de 3.7 usa solo Swin con el kNN de DermLIP** (P13 anterior): salió del párrafo del ensamble (R3: lo presenta 3.7).
- **Tarea binaria maligno frente a benigno** (MEL+BCC+AKIEC contra el resto, calculada en `melanoma_detection.py` y `lesion_split_report.py`) y **PR-AUC**: el texto no los menciona (antigua pregunta 6; decisión 13). Queda decidir en el Cap. 4 si se reporta.
- **Citas no usadas por el `.tex`**: `dosovitskiy2021image`, `liu2021swin`, `huang2018densely`, `liu2022convnet`, `russakovsky2015imagenet`, `howard2018universal`, `kumar2022finetuning`, `goodfellow2016deep`, `shorten2019survey`, `buda2018systematic` (las nombra el Cap. 2; R3). `kittler2016standardization` no respalda el aumento de datos (es «Standardization of terminology in dermoscopy») y no debe citarse.
- **Nota del repositorio, sin efecto en el texto**: `configs/sweeps/phase1_sweep.yaml` declara `method: bayes`, pero `sweep_utils.generate_combinations` muestrea al azar. Conviene corregir el yaml o su comentario (la búsqueda legacy que lo usa salió del capítulo).

## Preguntas abiertas para el autor

1. **(obsoleta tras la revisión del 18/10)** Comparación confundida entre recetas (legacy con pesos y vista única, moderna sin pesos y con TTA): ya no hay dos recetas en el capítulo (D-B).
2. **(resuelta)** Motivo de excluir DenseNet121 y ViT-B/16 del barrido: el texto dice que heredan la configuración de su familia, para compararlos con el mismo procedimiento, y declara la salvedad. No se invoca BatchNorm.
3. **(obsoleta tras la revisión del 18/10)** Búsqueda legacy con criterio distinto (F1 ponderado): la búsqueda legacy salió del capítulo.
4. **(obsoleta tras la revisión del 18/10)** Dónde van las ablaciones de la receta: se quitan de 3.4 (D-E).
5. **(resuelta; queda una incoherencia)** Tasa de la comparación de pérdidas: el texto la fija en 10⁻⁴ (7.91 × 10⁻⁵ en DenseNet121) y dice que el resto se mantiene fijo, pero 7.91 × 10⁻⁵ era la tasa ganadora de la búsqueda legacy de DenseNet121, que el capítulo ya no explica, mientras que DenseNet121 usa ahora 3.0 × 10⁻⁵ (la de ConvNeXt-Tiny). ¿Se aclara el origen de ese valor o se reemplaza por una frase del tipo «la tasa de cada modelo»?
6. **(obsoleta en el `.tex`; decidir en el Cap. 4)** Maligno frente a benigno: el `.tex` no tiene `\pendiente` ni lo menciona.
7. **(resuelta)** Parámetros de DenseNet121: se usan los de los logs (6.96 M, cabeza de 7 clases) y no los de `costo_resul_20260705.md` (8.0 M, cabeza de 1000).
8. **(obsoleta tras la revisión del 18/10)** Número de configuraciones legacy (25+ frente a 28).
9. **(resuelta)** «Tiny» por cómputo: el texto lo dice con la restricción de una GPU de consumo y el tamaño relativo a ViT-B/16, sin atribución.
10. **(obsoleta tras la revisión del 18/10)** Frase «todo con TTA» de `split_lesion_resul_20260926.md`: ya no se contrasta con las corridas legacy; sigue siendo una frase imprecisa del documento de resultados que no hay que repetir en el Cap. 4.
11. **(obsoleta tras la revisión del 18/10)** Tamaño original de HAM10000 para explicar la deformación al pasar a cuadrado: el texto ya no describe `Resize((224, 224))`.
12. **Semilla del barrido.** El texto no dice que el barrido se corrió con una sola semilla y que las semillas 43 y 44 solo se corrieron para el modelo elegido (60 entradas con semilla 42 en `lesion_split_report.json`). `tab:met_receta` pone «Semillas 42, 43 y 44» sin distinguir. ¿Se declara?

## Decisiones tomadas por cuenta propia

1. **La fuente de los valores son el código que se ejecutó** (`recipes.py`, `train_classifier.py`, `submit_sweep.py`, `submit.py`, `phase1_modern_sweep_grid.yaml`), no los `configs/*.yaml`. Los `configs/models/*.yaml` dicen en sus comentarios que `train_classifier.py` «NO lee este YAML», y `phase1_classification.yaml` tiene una configuración base que no coincide con las corridas reportadas. El `.tex` lo declara en su comentario inicial.
2. **Justificación de las cuatro arquitecturas: «un modelo anterior y uno más reciente por familia».** La agregó la revisión del 18/10/2026 y debe validarla el autor: permite comparar los dos tipos de arquitectura y dos generaciones de cada uno. Reemplaza a la justificación que proponía esta ficha (CNN y transformer, variantes Tiny por cómputo). Queda la restricción de cómputo para las variantes Tiny. El autor debe confirmar que ConvNeXt-Tiny (2022) y Swin-Tiny/ViT-B/16 (2021) se presentan como la generación «más reciente» de sus familias, y que DenseNet121 es la «anterior» de las convolucionales.
3. **Focal γ en la receta.** `recipes.py` define `focal_gamma=1.0` para `modern`, pero el barrido y la comparación de pérdidas pasan `--focal-gamma 0` o `2.0` explícito. El texto describe el valor efectivo (entropía cruzada en el barrido; γ = 2 en la comparación). El comentario de `recipes.py` («capas tempranas reciben ~20 % de base_lr») no coincide con 0.85⁹ ≈ 0.23 (Swin).
4. **Términos de Cap. 2 sin repetir.** Las siglas (CNN, ViT, TTA, VLM) se usan con `\gls{}`; **LLRD no se usa como sigla**: el texto dice «cada capa recibe 0.85 veces la tasa de aprendizaje de la capa siguiente». La primera aparición en el capítulo lleva cursiva.
5. **Nombres de versión fuera del texto.** No hay «receta moderna» ni «legacy» (D-B, R2); los nombres internos de corrida no aparecen.
6. **La variante de pesos forma parte de la configuración.** `lesion_split_report.py` (l. 98) rankea las dos variantes de pesos juntas por F1 macro; el texto dice que ganó una configuración sin pesos por clase en ambos modelos.
7. **Sin figura en 3.4.** La receta se muestra en tablas; el flujo va en 3.1 y la cascada en 3.7.
8. **Acrónimo nuevo propuesto** (GPU, en texto llano en P2): `\acronimo{gpu}{GPU}{unidad de procesamiento gráfico}{Graphics Processing Unit}`.
9. **Verificación:** los valores de las tablas y de P2–P8 se comprobaron contra el código (`recipes.py`, `train_classifier.py`, `submit_sweep.py`, `submit.py`, `transforms.py`, `optim_groups.py`, `losses.py`, `tta.py`, `lesion_split_report.py`), los logs (parámetros) y `split_lesion_resul_20260926.md`. Los JSON de semillas 43 y 44 existen.
