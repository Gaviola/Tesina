# Ficha 3.6 — Generación de reportes

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Antes era 3.7 y su archivo era `07-generacion-reportes.tex`. Sin repetir la presentación de Mini-VLM y LLaVA-Med; sin la historia de la primera configuración de LoRA (queda solo la v3: 31 457 280 entrenables); primero por qué SkinCaRe y después las dos etapas; «Reporte y razonamiento» y «Decodificación» se unen en «Inferencia»; sin «corridas finales» ni el límite de tokens del piloto. Lo que la revisión quitó del texto está en la sección final «Quitado en la revisión del 18/10/2026».

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada y revisada el 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/06-generacion-reportes.tex`. Labels: `sec:met_generacion`, `tab:met_lora`, `tab:met_decodificacion`. Las subsecciones no llevan label.

## Hilo conductor

Pregunta que responde la sección: ¿con qué modelos, qué ajuste, qué instrucción y qué decodificación se genera el reporte, y cómo se separa el texto del reporte del razonamiento que traen los datos de entrenamiento?

Viene de: 3.5 presentó Mini-VLM y LLaVA-Med como VLM de clasificación, con cuatro estrategias, y DermLIP como VLM especializado; en 3.5 los VLM clasifican, es decir, eligen una etiqueta de un inventario cerrado. Dejó abierto que la tarea de generación (T3, `sec:met_tareas`, 3.1) pide un texto libre con las dos partes del reporte, y que ningún clasificador lo produce. Antes: 3.4 clasificadores supervisados, 3.3 criterios de evaluación, 3.2 datos, 3.1 tareas y flujo de trabajo.
Deja instalado: para 3.7, tres generadores (dos ajustados y uno dermatológico sin ajuste propio), cada uno con su instrucción de inferencia y su decodificación fija; la regla de medir solo el reporte; y la configuración de LoRA y de entrenamiento de la Tabla~\ref{tab:met_lora}. Un generador que redacta a partir de la imagen y de la instrucción no decide si la lesión es lo bastante clara para afirmar un diagnóstico: eso lo incorpora el *pipeline* de 3.7.

```
P1  De clasificar a generar: en 3.5 los VLM eligen una etiqueta; la tarea T3 pide un texto libre con las  justifica
    dos partes del reporte (descripción e impresión diagnóstica, sec:met_tareas). Esa forma de salida no
    se obtiene con una instrucción: los modelos se ajustan con textos clínicos antes de usarlos
    ↓ presentación — qué modelos se ajustan y cuál se agrega
P2  Generadores ajustados = Mini-VLM y LLaVA-Med, los mismos que se evalúan como clasificadores
    (sec:met_vlm_generativos, sin repetir su presentación); el ajuste cambia su salida de etiqueta a
    texto. Ninguno está especializado en dermatología: se agrega un tercero            describe · justifica
    ↓ contraste — falta un generador de dermatología
P3  SkinVL: lo presentan zeng2025mmskin junto con MM-Skin; parte de LLaVA-Med v1.5 con Mistral-7B y
    ajusta con LoRA (rango 128) el modelo de lenguaje y la proyección visual, con el codificador visual
    congelado, en una sola etapa. Se usa SkinVL-MM (zwq803/SkinVL-MM), combinada con la versión de
    LLaVA-Med que trae el codificador visual, sin ajuste adicional. Sirve para saber si un generador
    especializado escribe reportes distintos de los generales                          define · justifica
    ↓ necesidad — antes de las dos etapas, con qué datos se ajusta y por qué esos
P4  Por qué SkinCaRe y no HAM10000: HAM10000 trae una etiqueta por imagen y no un texto que aprender a
    escribir; su prueba queda reservada para medir la fidelidad diagnóstica (sec:met_eval_generacion).
    Las dos partes de SkinCaRe enseñan cosas distintas: SkinCAP, descripciones observacionales; SkinCoT,
    de 23 enfermedades, siempre con impresión diagnóstica explícita. De ahí las dos etapas, con una
    parte cada una y la misma instrucción «Describe this skin lesion.»                  justifica · describe
    ↓ desarrollo — qué se entrena en cada etapa
P5  Etapa 1: SkinCAP alinea imagen y texto; solo se entrena el proyector visual, con codificador visual
    y LLM congelados. Etapa 2: SkinCoT enseña a redactar hasta el diagnóstico; LoRA (sec:marco_llm_lora)
    sobre las proyecciones de atención del LLM y del codificador visual, proyector congelado; q_proj y
    v_proj, salvo en el LLM de Mini-VLM, que usa qkv_proj. LLaVA-Med entrena 33 554 432 parámetros y
    Mini-VLM 31 457 280, menos del 1 % de cada modelo. Remite a la Tabla tab:met_lora    describe · justifica
    ↓ ampliación — cómo se eligieron y conservaron los valores de la tabla
P6  (tras la tabla) La tasa de la etapa 1 se eligió con una búsqueda sobre validación; en la etapa 2 la
    pérdida de validación siguió bajando hasta la última época, que es la que se conserva  justifica
    ↓ consecuencia — el texto de entrenamiento lleva razonamiento y eso condiciona la inferencia y la medición
P7  Reporte y razonamiento: casi todos los textos de SkinCoT intercalan bloques <think>; el modelo
    aprende a reproducirlos y su salida mezcla razonamiento y reporte. Se conservan al entrenar (permiten
    ver cómo llega a su descripción) y se quitan antes de medir (si no, los diagnósticos que el
    razonamiento solo menciona como hipótesis contarían como aciertos, sec:met_eval_generacion)
                                                                                        describe · limita
    ↓ ampliación — con qué instrucción y decodificación se genera ese texto
P8  Inferencia: misma instrucción del entrenamiento; decodificación voraz (sec:marco_llm_grandes) para
    que la generación sea reproducible; una imagen por vez; máximo de 384 tokens nuevos, suficiente
    para llegar al diagnóstico (Tabla tab:met_decodificacion); sin penalización de repetición porque en
    Mini-VLM hace fallar la generación. Cierre: el generador redacta pero no decide si la lesión es
    lo bastante clara para afirmar un diagnóstico; esa decisión la incorpora el pipeline  describe · limita
→ Transición a 3.7: «Con esto el generador redacta el reporte, pero no decide si la lesión es lo bastante clara para afirmar un diagnóstico; esa decisión es la que incorpora el *pipeline*.» (última oración de P8; es una afirmación sobre el generador, no un anuncio)

Se definen acá (y no se vuelven a definir): los tres generadores tal como se usan en el trabajo (sin repetir la presentación de Mini-VLM y LLaVA-Med de 3.5); la instrucción de inferencia («Describe this skin lesion.») y su coincidencia con el entrenamiento; la configuración de LoRA y de entrenamiento de las dos etapas; la separación reporte / razonamiento para entrenamiento y evaluación; la decodificación del trabajo (voraz, 384 tokens, sin penalización).
Se retoman de antes (solo se nombran, con \ref): las dos partes del reporte y la tarea T3 (`sec:met_tareas`, 3.1); Mini-VLM y LLaVA-Med (`sec:met_vlm_generativos`, 3.5); LoRA (`sec:marco_llm_lora`); decodificación voraz y muestreo (`sec:marco_llm_grandes`); métrica oficial y criterio de medición del reporte (`sec:met_eval_generacion`, 3.3); SkinCaRe, SkinCoT, MM-Skin y HAM10000 se presentan en 3.2 (`sec:met_datasets`, `sec:met_particiones`); el `.tex` los nombra sin `\ref` a esa sección.
Extensión: 8 párrafos de prosa, tres subsecciones y dos tablas (configuración de LoRA y del entrenamiento; decodificación); el encabezado del `.tex` estima 3 a 3.5 páginas.

## Subsecciones

- **3.6.1 Generadores.** P2 y P3. Mini-VLM y LLaVA-Med como generadores (sin repetir su presentación); SkinVL como generador dermatológico de comparación.
- **3.6.2 Ajuste en dos etapas sobre SkinCaRe.** P4, P5 y P6, con la Tabla~\ref{tab:met_lora}.
- **3.6.3 Inferencia.** P7 y P8, con la Tabla~\ref{tab:met_decodificacion}. Une las antiguas «Reporte y razonamiento» y «Decodificación».

P1 queda fuera de subsección. La transición a 3.7 es la última oración de P8.

## Contenido por párrafo

Rutas de `Codigo/outputs/`, `Codigo/data/` y `Codigo/mejores_params.txt`: no están versionadas, se leen en la copia `M`.

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | En 3.5 los VLM eligen una etiqueta; la tarea de generación (T3) pide un texto libre con descripción de la lesión e impresión diagnóstica (`sec:met_tareas`). Esa forma de salida no se obtiene con una instrucción, y por eso los modelos se ajustan con textos clínicos antes de usarlos. | Las dos partes coinciden con `reportes_mejoras_v2_plan` (instrucción a alinear con el entrenamiento) y con `tab:marco_partes_reporte` del Cap. 2; la definición está en 3.1. | Ninguna nueva |
| P2 | Mini-VLM y LLaVA-Med, los mismos modelos que se evalúan como clasificadores, son los generadores ajustados; el ajuste cambia su salida de una etiqueta a un texto. Ninguno está especializado en dermatología, así que se agrega un tercer generador. | Mini-VLM = `microsoft/Phi-3.5-vision-instruct` (`Codigo/src/models/mini_vlm.py:78`). LLaVA-Med = `chaoyinshe/llava-med-v1.5-mistral-7b-hf` (`Codigo/src/models/llava_med.py:22`). | Ninguna nueva (se remite a `sec:met_vlm_generativos`) |
| P3 | SkinVL, presentado junto con MM-Skin: parte de LLaVA-Med v1.5 con Mistral-7B y ajusta con LoRA (rango 128) el modelo de lenguaje y la proyección visual, con el codificador visual congelado, en una sola etapa de instrucciones. Se usa la variante SkinVL-MM (solo MM-Skin), con los pesos publicados (`zwq803/SkinVL-MM`); como no incluyen el codificador visual, se combinaron con los de la versión de LLaVA-Med que sí lo trae, sin ajuste adicional. Sirve para saber si un generador especializado en dermatología escribe reportes distintos de los generales. | `Codigo/src/models/skinvl.py` (subclase de LLaVA-Med; `MODEL_NAME = data/checkpoints/skinvl-mm-hf`); `Codigo/scripts/convert_skinvl_to_hf.py` (el repo trae 295 tensores sin el vision tower; la base aporta `vision_tower`); `Codigo/docs/ideas/skinvl_ensemble_plan_20260705.md` (pesos completos, sin LoRA, según la inspección del repo: ver Preguntas abiertas 11). Corrida sin ajuste propio: `slurm/mendieta/v3/generate_reports_skinvl.sh` (sin `--checkpoint`, 384 tokens). | `zeng2025mmskin` (MM-Skin y SkinVL) |
| P4 | HAM10000 trae una etiqueta por imagen y no un texto que el generador pueda aprender a escribir; su prueba queda reservada para medir la fidelidad diagnóstica. SkinCAP son descripciones observacionales (sitio, morfología, color, distribución); SkinCoT, de 23 enfermedades y no de las siete de HAM10000, termina siempre con una impresión diagnóstica explícita. Por eso el ajuste va en dos etapas, una con cada parte, y en ambas la instrucción es «Describe this skin lesion.». | `Codigo/data/raw/skincare/README.md` (SkinCAP: 4000 imágenes; SkinCoT: 3041 pares, revisados por clínicos en seis ejes; 7041 en total). `Codigo/data/raw/skincare/SkinCoT/EN/` tiene 23 carpetas (conteo propio). Instrucción: `VLMTrainCollator.CAPTION_INSTRUCTION` (`two_stage.py` l.111). El «siempre» de la impresión diagnóstica no está verificado (Preguntas abiertas 15). | `shen2025skincare`, `tschandl2018ham10000` |
| P5 | Etapa 1: se entrena solo el proyector visual con SkinCAP (codificador visual y LLM congelados). Etapa 2: LoRA sobre las proyecciones de atención del LLM y del codificador visual con SkinCoT, proyector congelado; `q_proj` y `v_proj` en ambos, salvo el LLM de Mini-VLM, que reúne las tres proyecciones en `qkv_proj`. Entrenables: 33 554 432 en LLaVA-Med y 31 457 280 en Mini-VLM, menos del 1 % de cada modelo. La Tabla~\ref{tab:met_lora} reúne la configuración. | `Codigo/scripts/train_vlm_stage1.py`, `train_vlm_stage2.py`; `Codigo/src/training/two_stage.py` (`_freeze_for_stage1` l.374; `_freeze_vision_encoder` l.522; `run_stage2` l.1196). Mini-VLM v3: job Mendieta 1179985, log `outputs/slurm_logs/mini_vlm/1179985.out` (LoRA en `qkv_proj` del modelo de lenguaje y `q_proj`/`v_proj` del codificador visual; 31 457 280 entrenables = 0.75 % de 4 178 078 720; mejor época 10, `val_loss` 0.9598). El 33 554 432 de LLaVA-Med no tiene fuente en esta ficha (ver «Números sin verificar»). | `hu2021lora` (solo \ref a `sec:marco_llm_lora`) |
| P6 | La tasa de aprendizaje de la etapa 1 se eligió con una búsqueda sobre validación. En la etapa 2 la pérdida de validación siguió bajando hasta la última época, que es la que se conserva. | `Codigo/outputs/mejores_params.txt` (barrido de la etapa 1, 1.09e-4); `two_stage.py` (detención temprana con paciencia 3; mejor época 10 en Mini-VLM v3, log 1179985). | Ninguna |
| P7 | Casi todos los textos de SkinCoT intercalan bloques `<think>`; el modelo aprende a reproducirlos y su salida mezcla razonamiento y reporte. Se conservan al entrenar (permiten ver cómo llega a su descripción) y se quitan antes de medir: si se midiera el texto completo, los diagnósticos que el razonamiento solo menciona como hipótesis contarían como aciertos. | Conteo propio sobre `Codigo/data/raw/skincare/SkinCoT/EN/*.txt` (copia en `M`): 3041 textos, 2942 con `<think>` (96.7 %), 3.25 bloques en promedio; el `.tex` dice «casi todos» sin cifra. Entrenamiento con el texto tal cual (`skincare.py` l.173). Quitar los bloques ocurre solo en la referencia de evaluación (`generate_report.py` `_strip_cot`, `fix_reports.py`; `evaluate_reports.py --strip-reasoning`). Criterio: `Codigo/docs/resul/revision_experimentacion_20261003.md` (§5, «solo reporte + matcher estricto»), `sec:met_eval_generacion`. | `shen2025skincare` (solo contexto) |
| P8 | En inferencia: misma instrucción del entrenamiento y decodificación voraz (elegir el token más probable en cada paso), lo que hace la generación reproducible. Una imagen por vez, máximo de 384 tokens nuevos, suficiente para que el texto llegue al diagnóstico. La voraz tiende a repetir frases, pero no se usa penalización de repetición porque en Mini-VLM hace fallar la generación. Cierre: el generador redacta el reporte pero no decide si la lesión es lo bastante clara para afirmar un diagnóstico; esa decisión la incorpora el pipeline. | `generate_report.py` l.52 (`REPORT_PROMPT`); `llava_med.py` l.195 y `mini_vlm.py` l.255 (`do_sample=False`); 384 en `ensemble_full_*.sh` y en `slurm/mendieta/v3/` y `v4/`; `slurm/mendieta/v3/rag_generation.sh` l.18–20; la falla de la penalización en Mini-VLM: `Codigo/docs/resul/analisis_pipeline_avanzado_resul_20260908.md`. | `sec:marco_llm_grandes` (solo \ref); `holtzman2020curious` no se cita en el `.tex` |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `tab:met_lora` — Configuración de LoRA y del entrenamiento (dos etapas) | Parámetro y valor; filas agrupadas por etapa | Ver filas abajo | hecha (en P5) |
| `tab:met_decodificacion` — Decodificación de los tres generadores | Parámetro y valor | Ver filas abajo | hecha (en P8) |
| (sin figura) | Ejemplo de texto de SkinCoT: ya está en 3.2 (`ej_skincot_human.jpg`), no se repite acá | — | no corresponde |

**`tab:met_lora` (dos columnas, parámetro y valor, como está en el `.tex`):**

| Parámetro | Valor | Fuente |
|---|---|---|
| *Etapa 1 (proyector)* | | |
| Parámetros entrenables | Proyector visual (LLaVA-Med: `multi_modal_projector`; Mini-VLM: `img_projection`, `glb_GN` y `sub_GN`) | `two_stage.py` `_freeze_for_stage1` l.374 |
| Congelados | Codificador visual y modelo de lenguaje | idem |
| Datos | 2 492 / 534 / 535 (entrenamiento / validación / prueba) | `Codigo/data/splits/skincare_skincap_splits.json` (suma 3561; ver Preguntas abiertas 10) |
| Optimizador | AdamW, decaimiento 0, eps $10^{-7}$ | `two_stage.py` l.1158–1174 |
| Planificador | Coseno (`CosineAnnealingLR`) | idem |
| Tasa de aprendizaje | $1.09 \times 10^{-4}$ | `Codigo/outputs/mejores_params.txt` (barrido; ver Preguntas abiertas 1) |
| Épocas | 2, sin detención temprana | idem |
| Lote | 16 (15 en LLaVA-Med, reducido por memoria) | sin fuente en esta ficha (ver «Números sin verificar») |
| *Etapa 2 (LoRA)* | | |
| Rango $r$ | 64 | `lora_config.json` de `stage2_mini_vlm_v2`; `train_vlm_s2*.sh` v2 |
| Escala $\alpha$ | 64 | idem |
| Dropout de LoRA | 0.0 | idem |
| Módulos | `q_proj`, `v_proj`; en Mini-VLM, además `qkv_proj` | idem; log del job 1179985 (v3 de Mini-VLM) |
| Proyector | Congelado | `get_peft_model` congela los parámetros no adaptadores (ver Preguntas abiertas 4) |
| Datos | 2 128 / 456 / 457 (entrenamiento / validación / prueba) | `Codigo/data/splits/skincare_skincot_splits.json` |
| Instrucción | «Describe this skin lesion.» | `CAPTION_INSTRUCTION` |
| Tasa de aprendizaje | $2.495 \times 10^{-5}$ | `slurm/mendieta/v2/train_vlm_s2*.sh` |
| Optimizador | Decaimiento 0.01, eps $10^{-7}$ (AdamW) | `two_stage.py` `run_stage2` |
| Épocas | 10, paciencia 3 | `slurm/mendieta/v2/`; `train_vlm_stage2.py` l.227 |
| Lote y acumulación | 4 y 8 (32 efectivos) | `slurm/mendieta/v2/` (ver Preguntas abiertas 6) |
| Longitud máxima | 2 048 | `train_vlm_stage2.py` l.213 |
| Recorte de gradiente | 1.0 | `two_stage.py` l.782 |
| Precisión | bf16 en GPU de arquitectura Ampere o posterior | `Codigo/src/utils/device.py` `get_training_dtype` |
| Cuantización | No | sin verificar (ver Preguntas abiertas 7) |
| Semilla | 42 | `slurm/mendieta/v2/` |

**`tab:met_decodificacion`:**

| Parámetro | Valor | Fuente |
|---|---|---|
| Estrategia | Voraz (`do_sample=False`) | `llava_med.py` l.195; `mini_vlm.py` l.255 |
| Máximo de tokens nuevos | 384 | `slurm/mendieta/v3/`, `v4/`, `ensemble_full_*.sh` |
| Llamadas | Una imagen por llamada | `generate_report.py` `_generate_single` |
| Penalización de repetición | No se usa | `rag_generation.sh` l.18–20 |
| Instrucción de inferencia | «Describe this skin lesion.», la misma del entrenamiento | `generate_report.py` l.52 |
| Semilla | 42 | slurm |
| Posprocesamiento | Se quitan los bloques `<think>` antes de medir | `evaluate_reports.py --strip-reasoning` |

**Valores de `Codigo/configs/phase2_generation.yaml` (r 64, alpha 128, dropout 0.05, siete módulos, 3 épocas, lr 2e-5) no se usan en las tablas**: el código no lee ese YAML (ver Preguntas abiertas 3).

## Prosa ya escrita que se conserva

Nada de la versión anterior a la revisión. El párrafo 1 original («El reporte dermatológico deja por escrito…») se movió a 3.1 (`sec:met_tareas`), donde se definen las dos partes del reporte (R3); P1 de esta sección lo retoma con `\ref`.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`):** `REPORT_PROMPT`, las plantillas condicionadas por diagnóstico (`confirmed`, `noreasoning`, RAG, incertidumbre, las de SkinVL) y la lista de instrucciones de SkinVL. En 3.6 solo se nombra la instrucción base y la regla «sin bloques <think>».
- **Apéndice E (`ap:reproducibilidad`):** comandos exactos de entrenamiento y generación (`slurm/mendieta/v2/`, `v3/`, `v4/`) y el conteo de bloques `<think>` como script reproducible.
- **Apéndice F (fichas de conjuntos y modelos):** ficha de SkinVL (origen de los pesos, conversión, licencia) con el detalle de la conversión que el texto ya no trae.

## Lo que NO va en esta sección (y dónde está)

- **Resultados de cualquier generador:** consistencia diagnóstica, recall de entidades, BLEU, ROUGE, BERTScore, hedging, dx incorrecto, repetición, ablaciones (imagen frente a diagnóstico, diagnóstico erróneo), comparación con SkinVL, variantes de prompt de SkinVL, posprocesamiento de repeticiones: Cap. 5 (`cp:res_gen`, `sec:res_gen_skinvl` ya existe).
- **Razonamiento de la cascada, plantillas con diagnóstico, *noreasoning*, *grounding* por recuperación, ruteo:** 3.7.
- **Clasificación de los VLM por verosimilitud, DermLIP, *linear probe*, kNN y SVM, y la presentación de Mini-VLM y LLaVA-Med:** 3.5 (`sec:met_clasif_vlm`, `sec:met_vlm_generativos`).
- **Costo de entrenamiento y de generación (horas de GPU):** 3.8 (costo computacional, `sec:met_complementarios`). `ejecuciones.md` tiene la medición, no es un desempeño.
- **Definiciones** de LLM, LoRA, decodificación, alucinación, *hedging*, RAG, reporte clínico y VLM generativo: Cap. 2. Solo `\ref`.
- **Fundamentos de AdamW y del planificador coseno** (`loshchilov2019decoupled`, `loshchilov2017sgdr`): Cap. 2 (2.1, optimización), solo se nombran acá.
- **Formato del `<think>` de SkinCoT y ejemplo de texto:** 3.2.
- **Planes que se anularon** (`reportes_mejoras_v3_class_weights_plan_20260525.md`, focal loss, *commitment-line* en los objetivos de entrenamiento): no entran; la anulación consta en el encabezado del plan.

## Preguntas abiertas para el autor

1. **Etapa 1: ¿qué configuración produjo `stage1_llava_med/best_model.pt` y `stage1_mini_vlm/best_model.pt`? (resuelta en el `.tex`, a verificar)** El `.tex` y la tabla adoptan lr 1.094512e-04 y 2 épocas (`Codigo/outputs/mejores_params.txt`, barrido en Mendieta), sin detención temprana, lote 16 (15 en LLaVA-Med). Siguen sin coincidir: `slurm/mendieta/train_vlm_s1_*.sh` (lr 1e-3, 5 épocas, paciencia 2) y `slurm/toko/train_vlm_s1_llava.sh` (lr 2e-3, 1 época). El checkpoint no trae `sweep_config.json`. Ver D14.
2. **LoRA en Mini-VLM: ¿existen los módulos `q_proj` y `v_proj`? (resuelta por el reentrenamiento v3)** El `.tex` y la tabla ya describen la configuración v3 (`qkv_proj` en el modelo de lenguaje; `q_proj` y `v_proj` en el codificador visual; 31 457 280 entrenables, job 1179985).
3. **`phase2_generation.yaml` no se lee en ningún script** (`grep` de `phase2_generation` en `src` y `scripts` vacío). Sus valores (r 64, alpha 128, dropout 0.05, siete módulos, 3 épocas, lr 2e-5) no son los de las corridas finales. **Abierta**: actualizarlo a lo que se corrió, o declarar que las corridas se lanzaron con argumentos de línea de comando (`AGENTS.md` dice que `configs/` es la fuente de verdad de hiperparámetros).
4. **Proyector en la etapa 2 (resuelta en el `.tex`, a verificar).** El `.tex` y la tabla dicen «Proyector: Congelado». Es coherente con que `get_peft_model` congele lo que no es adaptador y con el conteo de Mini-VLM v3 (31 457 280 = el LoRA), pero para LLaVA-Med no se verificó con `print_trainable_parameters` de un job.
5. **Relación con el Cap. 2.** `05-vlm.tex` describe la segunda etapa de LLaVA como «se ajustan el proyector y el LLM». Con el proyector congelado en la etapa 2, el Cap. 2 no debe presentarlo como parte del ajuste de este trabajo. **Abierta**, a corregir en el Cap. 2.
6. **Tamaño de lote efectivo de la etapa 2 v2.** El SLURM pide lote 4 y acumulación 8 (32); `train_vlm_stage2.py` reduce el lote a la mitad ante falta de memoria y duplica la acumulación. Confirmar en el log de los jobs `stage2_*_v2` (línea «Iniciando entrenamiento | batch_size | grad_accum»). **Abierta.**
7. **Cuantización.** La tabla dice «No»; `USAGE.md` dice que LLaVA-Med se carga en 4 bits si la VRAM libre es menor que 14 GB. Confirmar que las corridas de A30 (24 GB) no cuantizaron. **Abierta.**
8. **Número de épocas del modelo final (resuelta).** Se usa `stage2_*_v2` (10 épocas), que consumen el ensamble, RAG, incertidumbre y reanclaje; el `.tex` dice «10, paciencia 3». Mini-VLM tiene además v3 (mejor época 10).
9. **LLaVA-Med base (resuelta en el `.tex`).** El `.tex` dice Mistral-7B. Siguen desactualizados `Codigo/configs/models/llava_med.yaml` («Llama-2-7b-chat») y `Codigo/CLAUDE.md` («LLaMA-2 7B»).
10. **Mini-VLM y SkinCAP.** (a) `Codigo/configs/models/mini_vlm.yaml` describe «CLIP ViT-B/16 + Phi-3-mini» y debe corregirse (el código carga Phi-3.5-vision). (b) SkinCAP: `02-datos.tex` dice 4 000 imágenes, pero los splits suman 3 561 (2 492 + 534 + 535) y la tabla del `.tex` usa esos tamaños. **Abierta**: ¿qué pares se excluyen y por qué?
11. **SkinVL: pesos y cita (resuelta en el `.tex`).** El `.tex` sigue al artículo (`zeng2025mmskin`: LoRA de rango 128 sobre el modelo de lenguaje y la proyección, una sola etapa) y no menciona la inspección propia del repo (pesos ya fusionados, sin adaptador). Falta confirmar que `zeng2025mmskin` es el artículo que presenta SkinVL.
12. **Declaración sobre la fuga (obsoleta tras la revisión del 18/10).** El `.tex` no declara solapamiento entre SkinCAP/SkinCoT y HAM10000, y la corrección del 11/10 establece que los VLM generales no se ajustaron sobre HAM10000.
13. **Duplicación con 3.1 (resuelta).** 3.1 define las dos partes del reporte; P1 las nombra y remite a `sec:met_tareas`.
14. **Qué anota cada subconjunto de SkinCaRe (resuelta en el `.tex`).** P4 dice: SkinCAP, descripciones observacionales; SkinCoT, razonamiento terminado en impresión diagnóstica.
15. **Impresión diagnóstica en la condición base (a verificar).** P4 afirma que los textos de SkinCoT «terminan siempre» con una impresión diagnóstica explícita; la ficha no lo contrastó (conteo de `<think>` sí, el de la conclusión no). La instrucción «Describe this skin lesion.» no pide un diagnóstico: verificar con 3 o 4 reportes de una corrida que la impresión aparece en el texto generado.
16. **Premisa del último párrafo de la transición (obsoleta tras la revisión del 18/10).** La transición ya es una afirmación sobre el generador («no decide si la lesión es lo bastante clara…»), sin remitir a resultados.
17. **Memoria que justifica LoRA (resuelta).** El `.tex` dice «Por la restricción de cómputo» y remite a `sec:marco_llm_lora`, sin cifra de memoria.

## Decisiones tomadas por cuenta propia

- **D1. Mini-VLM = `microsoft/Phi-3.5-vision-instruct`** (código, `mini_vlm.py`, y lo que dicen 2.3 y 3.5). El YAML queda como discrepancia (pregunta 10).
- **D2. Configuración de LoRA y entrenamiento de la etapa 2 = la del checkpoint final (`stage2_*_v2`)**, tomada de `lora_config.json` y de los SLURM v2, no del YAML (pregunta 3). Mini-VLM: configuración de módulos de v3.
- **D3. Generadores finales = los checkpoints `stage2_*_v2`** (Mini-VLM, además, v3). Los usan `ensemble_full_*.sh` y los scripts de `v3/` y `v4/`. Las generaciones v1 y v2 (512 tokens) son iteraciones previas y no figuran en el `.tex` (R2).
- **D4. Instrucción de inferencia = la de entrenamiento** («Describe this skin lesion.»). La versión anterior del prompt, más larga, se abandonó; no se describe acá.
- **D5. Entrenamiento con el texto completo de SkinCoT, incluidos los bloques `<think>`.** Se justifica porque el razonamiento permite ver cómo llega el modelo a su descripción; la separación se hace en la evaluación, no en el entrenamiento.
- **D6. Decodificación voraz, 384 tokens, una imagen por llamada, semilla 42.** El `.tex` justifica los 384 como «suficiente para que el texto llegue al diagnóstico», sin mencionar el piloto de 256 (R1).
- **D7. SkinVL sin ajuste propio**, con el mismo `REPORT_PROMPT` y la misma decodificación que los otros dos generadores. Así la comparación cambia solo el generador.
- **D8. La penalización de repetición y `no_repeat_ngram_size` no se usan.** La de Mini-VLM falla (Phi-3.5, tokens de imagen fuera del rango del vocabulario, según `analisis_pipeline_avanzado_resul_20260908.md`). Se declara sin cifras.
- **D9. El posprocesamiento de repeticiones (`repetition_postprocess.py`) no se adopta** y ya no se menciona en el `.tex`; el resultado va al Cap. 5.
- **D10. Tablas de configuración en el cuerpo, grillas no** (la búsqueda completa va a `ap:hiperparametros`).
- **D11. Cita de SkinVL = `zeng2025mmskin`.** Mini-VLM se cita con `abdin2024phi3` en 3.5; esta sección ya no lo cita.
- **D12. Referencia a 3.5 = `sec:met_vlm_generativos`** (existe en `05-clasificacion-vlm.tex`; la ficha anterior decía `sec:met_clasif_vlm` porque aún no existía).
- **D13. (resuelta por el reentrenamiento v3 de Mini-VLM)** El hallazgo de que `stage2_mini_vlm_v2/best_model.pt` tenía 48 adaptadores (`q_proj`, `v_proj`) en el codificador visual y ninguno en el modelo de lenguaje quedó superado: Mini-VLM se reentrenó con adaptadores en el LLM. El texto ya no describe la primera configuración (R2).
- **D14. Etapa 1 parcialmente resuelta (pregunta 1).** El `.tex` adopta el valor del barrido (1.09e-4, 2 épocas), pero `stage1_llava_med/best_model.pt` registra época 1 con `val_loss` 1.82 (el barrido: mejor en época 2 de 2, 1.34) y `stage1_mini_vlm/best_model.pt` no es un zip legible (archivo truncado de 2.6 GB; `best_model_firts.pt` registra época 3 con `val_loss` 1.84). La etapa 2 v2 de Mini-VLM se entrenó desde `stage1_mini_vlm/best_model.pt`: conviene revisar ese archivo.
- **D15. Proyector y cuantización (preguntas 4 y 7) y lote real (pregunta 6)**: la tabla del `.tex` ya los fija (congelado; no; 4 y 8), sin verificación en la copia local.
- **D16. Mini-VLM v3 verificado (2026-10-18).** Se reentrenó con `qkv_proj q_proj v_proj` (job 1179985, 9 h 51 min). El log confirma 31 457 280 parámetros entrenables (0.75 % de 4 178 078 720); mejor época 10, `val_loss` 0.9598. El `.tex` usa el conteo; el paso de los Caps. 4 y 5 a v3 queda en sus fichas. **Resuelta** (cierra D13 y la pregunta 2).

## Números sin verificar

- Duración del entrenamiento y del procesamiento de generación (`ejecuciones.md`): no se usan.
- «trasplantados ≈ 291» del runbook de SkinVL: ya no figura en el `.tex`.
- Tamaño exacto de los conjuntos de SkinCAP (pregunta 10).
- Lote efectivo y cuantización reales de la etapa 2 v2 (preguntas 6 y 7).
- 33 554 432 parámetros entrenables de LLaVA-Med y «menos del 1 %»: sin fuente en la ficha; falta el log del job de LLaVA-Med.
- Lote de la etapa 1 («16, 15 en LLaVA-Med»): sin fuente en la ficha.
- Rango 128 de SkinVL: viene del artículo, no se contrastó.

## Quitado en la revisión del 18/10/2026

Lo que la ficha anterior fijaba y el `.tex` actual ya no dice. Se conserva acá para no perder la fuente.

- Presentación repetida de Mini-VLM y LLaVA-Med como generadores (modelos base, `abdin2024phi3`, `li2023llavamed`, `liu2023visual`, `jiang2023mistral`): R3, ya están en 3.5; el `.tex` remite con `\ref{sec:met_vlm_generativos}`. Fuente: `mini_vlm.py:78`, `llava_med.py:22`.
- Historia de la primera configuración de LoRA de Mini-VLM (48 adaptadores `q_proj`/`v_proj` en el codificador visual, ninguno en el modelo de lenguaje; `\pendiente` de la tabla): R2, solo se describe la v3 (D13, D16). Fuente: `Codigo/outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt`, `lora_config.json`.
- Desglose de parámetros entrenables por componente: R1/R2, el `.tex` da solo el total por modelo. Fuente: log 1179985.
- Límite de 256 tokens del piloto y su motivo para subir a 384 (`slurm/mendieta/pilot_ensemble_v2_llava.sh` l.20; 512 por defecto en `generate_report.py` l.218 y en las corridas `slurm/mendieta/v1` y `v2`): R1/R2, historia del proceso.
- «Corridas finales» (sin penalización de repetición en las corridas finales; la tabla decía «512 en v1 y v2»): R1/R2.
- Detalles de conversión de SkinVL (pesos en formato original de LLaVA-Med con 295 tensores y sin `vision_tower`, trasplante a formato HF sobre `chaoyinshe/llava-med-v1.5-mistral-7b-hf`, script `convert_skinvl_to_hf.py`, ≈ 291 tensores del runbook): R1; el `.tex` dice que los pesos «no incluyen el codificador visual» y se combinaron con los de la versión de LLaVA-Med que sí lo trae. Va al Apéndice F si hace falta.
- Posprocesamiento de repeticiones (`repetition_postprocess.py`, addendum de `analisis_pipeline_avanzado_resul_20260908.md`, «no se adopta») y la mención a `holtzman2020curious`: R1/R2.
- Antigua subsección «Partes del reporte que genera el trabajo» (3.7.1, prosa original): R3, la definición está en 3.1 (`sec:met_tareas`).
- Subsecciones separadas «Reporte y razonamiento» (3.7.4) y «Decodificación» (3.7.5): se unen en «Inferencia» (3.6.3).
- Cifras del conteo de `<think>` (3041 textos, 2942 con `<think>`, 96.7 %, 3.25 bloques por texto, 537 empiezan con «To analyze the case…»): R1; el `.tex` dice «casi todos». Fuente conservada en la tabla de P7.
- Cifras de test de HAM10000 (1 503 imágenes) en el párrafo del porqué de SkinCaRe: R3, están en 3.2.
- Justificación explícita de LoRA por memoria con cifra y la opción de medir la VRAM de un ajuste completo (pregunta 17 anterior): el `.tex` justifica con «la restricción de cómputo» (R3, `sec:marco_llm_lora`).
- Detalle de la instrucción del mismo prompt con la versión larga abandonada (D4): R2.
- Tasas alternativas de la etapa 1 (1e-3 con 5 épocas en Mendieta; 2e-3 con 1 época en TOKO): R2; solo queda el valor del barrido.
