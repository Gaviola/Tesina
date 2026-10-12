# Ficha 3.7 — Generación de reportes

**Estado: propuesta, sin aprobar.** Archivo: `Chapters/03-Materiales-Metodos/07-generacion-reportes.tex` (sale de `05-generacion-reportes.tex`). Labels: `sec:met_generacion`.

## Hilo conductor

Pregunta que responde la sección: ¿con qué modelos, qué ajuste, qué instrucción y qué decodificación se genera el reporte, y cómo se separa el texto del reporte del razonamiento que traen los datos de entrenamiento?

Viene de: 3.6 presentó Mini-VLM y LLaVA-Med como VLM generales, con cuatro estrategias de clasificación, y DermLIP como VLM especializado en clasificación. Dejó abierto que PI2 pide un reporte, y ningún clasificador lo produce. Los dos VLM generativos se ajustan para generarlo; en 3.6 no se vuelven a describir.
Deja instalado: para 3.8, dos generadores ajustados y un generador dermatológico sin ajuste propio, cada uno con su instrucción de inferencia y su decodificación fija; la regla de medir solo el reporte; y la configuración de LoRA y de entrenamiento de la Tabla de esta sección. Un generador que redacta a partir de la imagen y de la instrucción necesita que el diagnóstico venga de afuera cuando se lo quiere afirmar con fidelidad: eso lo resuelve 3.8.

```
P1  Qué genera el modelo: descripción de lo que se ve e impresión diagnóstica; el diagnóstico    define
    diferencial y la recomendación quedan fuera (prosa ya escrita, se conserva)
    ↓ necesidad — 3.6 usa estos VLM para clasificar; para redactar hace falta ajustarlos
P2  Los dos VLM generales de 3.6, ajustados: Mini-VLM (Phi-3.5-vision-instruct) y LLaVA-Med v1.5    justifica
    (Mistral-7B). Son los mismos modelos base, con el ajuste que genera texto
    ↓ contraste — ambos son de propósito general; falta un generador de dermatología
P3  SkinVL: qué es, de dónde sale, por qué se incluye y cómo se usó (conversión a formato HF,        define · justifica
    sin ajuste propio)
    ↓ necesidad — antes de ajustar, el ajuste en dos etapas tiene que decir con qué datos
P4  Ajuste en dos etapas: etapa 1 alinea el proyector con SkinCAP; etapa 2 ajusta el LLM con LoRA     describe
    sobre SkinCoT. La instrucción es la misma en ambas etapas
    ↓ necesidad — con qué datos: los del área tienen texto de clínicos y HAM10000 no tiene reportes
P5  Por qué SkinCaRe y no HAM10000: HAM10000 trae etiquetas, no reportes; SkinCaRe trae un texto por   justifica
    imagen. La partición de prueba de HAM10000 queda para evaluar la fidelidad (3.4), no para entrenar
    ↓ contraste — pero los textos de SkinCoT son razonamientos, no reportes
P6  La configuración de LoRA y del entrenamiento, con la razón desde el objetivo de una GPU de consumo  describe · justifica
    (Tabla 3.7.a)
    ↓ consecuencia — el texto de entrenamiento lleva el razonamiento, y eso condiciona la evaluación
P7  Reporte y razonamiento en SkinCoT: los bloques <think>...</think>, qué aprende el modelo al           describe · limita
    entrenar con el texto completo, y por qué el razonamiento tiene valor para auditar (y no para medir)
    ↓ necesidad — si el razonamiento se mide como reporte, la métrica se infla
P8  Qué se le pide y qué se mide: la instrucción de inferencia coincide con la de entrenamiento; los     justifica
    bloques se quitan antes de medir y las métricas se computan sobre el reporte (criterio de 3.4)
    ↓ ampliación — con qué decodificación se genera ese texto
P9  Decodificación: voraz, 384 tokens, un reporte por imagen; sin penalización de repetición en las       describe · limita
    corridas finales; el posprocesamiento de repeticiones se descartó (resultado en el Cap. 5 si
    corresponde)
→ Transición a 3.8: «…el generador redacta el texto, pero no decide si la lesión es lo bastante clara
  para afirmar un diagnóstico; esa decisión y la evidencia que la sostiene se incorporan en 3.8.»
  (ajustar; no anunciar, §3 de la guía: la transición debe ser una afirmación sobre el generador)

Se definen acá (y no se vuelven a definir): los tres generadores tal como se usan en el trabajo;
la instrucción de inferencia («Describe this skin lesion.») y su coincidencia con el entrenamiento;
la configuración de LoRA y de entrenamiento de las dos etapas; la separación reporte / razonamiento
para entrenamiento y evaluación; la decodificación del trabajo (voraz, 384 tokens, sin penalización).
Se retoman de antes (solo se nombran, con \ref): LLM, aprendizaje en contexto, decodificación voraz,
muestreo, *top-p* y temperatura (`sec:marco_llm_grandes`, `eq:marco_temperatura`); LoRA
(`sec:marco_llm_lora`, `eq:marco_lora`); VLM generativo y LLaVA (`sec:marco_vlm_generativos`);
clasificación por verosimilitud (`sec:marco_vlm`); reporte clínico, descripción e impresión
(`sec:marco_rep_tarea`, `tab:marco_partes_reporte`); generación condicionada y *grounding*
(`sec:marco_rep_generacion`, `eq:marco_rep_condicionada`); alucinación, *hedging* y repetición
(`sec:marco_rep_fallas`, `tab:marco_fallas`); RAG (`sec:marco_rag`); métrica oficial y criterios de
generación (`sec:met_protocolo`); SkinCaRe, SkinCoT y HAM10000 (`sec:met_datasets`, `sec:met_ham`,
`sec:met_particiones`); DermLIP y los VLM de clasificación (`sec:met_clasif_vlm`).
Extensión: 9 párrafos, unas 3 a 3.5 páginas, con una tabla de configuración (media página) y una
tabla breve de decodificación.

## Subsecciones

- **3.7.1 Partes del reporte que genera el trabajo.** P1.
- **3.7.2 Generadores.** P2 y P3. Mini-VLM y LLaVA-Med se presentan como generadores (no como clasificadores,
  eso es 3.6); SkinVL, como generador dermatológico de comparación.
- **3.7.3 Ajuste en dos etapas sobre SkinCaRe.** P4, P5 y P6, con la Tabla 3.7.a.
- **3.7.4 Reporte y razonamiento.** P7 y P8.
- **3.7.5 Decodificación.** P9, con la Tabla 3.7.b.

## Contenido por párrafo

Rutas de `Codigo/outputs/`, `Codigo/data/` y `Codigo/mejores_params.txt`: no están versionadas, se leen en la copia `M`.

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | El reporte tiene dos partes que el trabajo genera: la descripción de lo visible y la impresión diagnóstica. Diferencial y recomendación quedan fuera. | Prosa ya escrita (`05-generacion-reportes.tex`, párrafo 1). Las dos partes coinciden con `reportes_mejoras_v2_plan` (instrucción a alinear con el entrenamiento) y con `tab:marco_partes_reporte` del Cap. 2 | `shen2025skincare` (la prosa ya la usa; ver Q14) |
| P2 | Mini-VLM y LLaVA-Med, los mismos modelos base de 3.6, se ajustan para generar. Son de propósito general, por eso se usan como línea de comparación del resto de los generadores. | Mini-VLM = `microsoft/Phi-3.5-vision-instruct` (`Codigo/src/models/mini_vlm.py:78`). LLaVA-Med = `chaoyinshe/llava-med-v1.5-mistral-7b-hf` (`Codigo/src/models/llava_med.py:22`). Los dos YAML de `Codigo/configs/models/` están desactualizados (Q9, Q10) | `abdin2024phi3` (Phi-3), `li2023llavamed`, `liu2023visual` (LLaVA), `jiang2023mistral` (Mistral 7B, base de LLaVA-Med v1.5) |
| P3 | SkinVL: LLaVA-Med v1.5 con Mistral-7B ajustado a dermatología con MM-Skin. Los pesos publicados (`zwq803/SkinVL-MM`) están en el formato original de LLaVA-Med y no traen el codificador visual. Se convirtió a formato HF trasplantando sus pesos de lenguaje y proyector sobre la base `chaoyinshe/llava-med-v1.5-mistral-7b-hf`, que aporta el codificador visual. No se lo ajustó. Se incluye como generador especializado de comparación: ¿la especialización de dominio cambia el texto frente a los generales? | `Codigo/src/models/skinvl.py` (subclase de LLaVA-Med; `MODEL_NAME = data/checkpoints/skinvl-mm-hf`); `Codigo/scripts/convert_skinvl_to_hf.py` (docstring: el repo trae 295 tensores sin el vision tower; la base aporta `vision_tower`); `Codigo/docs/ideas/skinvl_ensemble_plan_20260705.md` (pesos completos, sin LoRA, según la inspección del repo). Corrida sin ajuste propio: `slurm/mendieta/v3/generate_reports_skinvl.sh` (sin `--checkpoint`, 384 tokens) | `zeng2025mmskin` (MM-Skin y SkinVL, ver Q11) |
| P4 | Etapa 1: se entrena solo el proyector visual con pares imagen–caption de SkinCAP (vision encoder y LLM congelados). Etapa 2: LoRA sobre el LLM con los pares de SkinCoT EN (vision encoder congelado). La instrucción es «Describe this skin lesion.» en ambas etapas. | `Codigo/scripts/train_vlm_stage1.py`, `train_vlm_stage2.py`; `Codigo/src/training/two_stage.py` (`_freeze_for_stage1` l.374; `_freeze_vision_encoder` l.522; `run_stage2` l.1196); `VLMTrainCollator.CAPTION_INSTRUCTION` (`two_stage.py` l.111). Proyector en etapa 2: Q4 | `hu2021lora`, `liu2023visual` |
| P5 | HAM10000 tiene etiquetas diagnósticas y no reportes; por eso no sirve como texto de referencia ni de entrenamiento del generador, y su partición de prueba (1503 imágenes) se usa para medir la fidelidad diagnóstica (3.4). SkinCaRe trae, para cada imagen, un texto de clínicos: captions de SkinCAP (dermatólogos) y razonamiento diagnóstico revisado de SkinCoT. La etapa 2 ve 23 clases tipo DermNet, no las 7 de HAM10000. | `Codigo/data/raw/skincare/README.md` (SkinCAP: 4000 imágenes; SkinCoT: 3041 pares, revisados por clínicos en seis ejes; 7041 en total). `Codigo/data/raw/skincare/SkinCoT/EN/` tiene 23 carpetas (conteo propio). HAM: 1503 en la partición por lesión (`Codigo/docs/resul/split_lesion_resul_20260926.md`, §1) | `shen2025skincare`, `tschandl2018ham10000` |
| P6 | Como uno de los objetivos es ejecutar todo en una GPU de consumo (3.2), los modelos se adaptan con LoRA en lugar de ajustar todos sus parámetros. Se fijan rango, escala, dropout, módulos y tasa de aprendizaje (Tabla 3.7.a). La cifra de memoria que lo justifica no está en las fuentes leídas (Q17). | Tabla 3.7.a (abajo). Valores de la etapa 2 del checkpoint final: `Codigo/outputs/checkpoints/stage2_mini_vlm_v2/lora_config.json` (r 64, alpha 64, dropout 0.0, `q_proj` y `v_proj`); `Codigo/slurm/mendieta/v2/train_vlm_s2.sh` y `train_vlm_s2_mini.sh` (lr 2.495e-5, lote 4, acumulación 8, 10 épocas, sin `--lora_*` adicional); `two_stage.py` l.1196–1290 (AdamW, decaimiento 0.01, eps 1e-7, sin planificador, detención temprana con paciencia 3, recorte de norma 1.0). Los VRAM de `Codigo/configs/models/*.yaml` son estimaciones, no se citan | `hu2021lora` |
| P7 | En SkinCoT el texto es una narrativa de razonamiento diagnóstico; los pasos van entre bloques `<think>...</think>`. El modelo aprende a reproducirlos, incluidos los bloques, y su salida mezcla razonamiento y reporte. El razonamiento tiene valor para auditar el proceso (interpretabilidad), por eso no se quita del entrenamiento. | Conteo propio sobre `Codigo/data/raw/skincare/SkinCoT/EN/*.txt` (copia en `M`): 3041 textos, 2942 con `<think>` (96.7 %), 3.25 bloques en promedio por texto; 537 empiezan con la frase «To analyze the case…». El entrenamiento usa el texto tal cual (`skincare.py` l.173, sin quitar bloques). Quitar los bloques ocurre solo en la referencia de evaluación (`generate_report.py` `_strip_cot`, `fix_reports.py`) | `shen2025skincare` |
| P8 | La instrucción de inferencia es la de entrenamiento («Describe this skin lesion.»): una instrucción distinta de la usada en el entrenamiento cambia el prompt que recibe el modelo respecto de lo que aprendió. Las métricas de generación se calculan sobre el reporte, sin los bloques `<think>`: si se midieran sobre el texto completo, las menciones de diagnósticos hipotetizados dentro del razonamiento contarían como aciertos. La magnitud del efecto va al Cap. 5, sin cifras acá. | `generate_report.py` l.52 (`REPORT_PROMPT`); `evaluate_reports.py` l.184–207 (`--strip-reasoning`); criterio de métrica oficial en `Codigo/docs/resul/revision_experimentacion_20261003.md` (§5, «solo reporte + matcher estricto»). Efecto del razonamiento: solo referencia a `Codigo/docs/experimentacion` (números viejos, no usar) | — (los criterios son del trabajo) |
| P9 | Decodificación voraz (`do_sample=False`), una imagen por llamada, 384 tokens nuevos, semilla 42. Voraz tiende a repetirse en la generación abierta (ya dicho en el Cap. 2), y el trabajo lo acepta por reproducibilidad. El límite de 384 tokens reemplazó al de 256 del piloto, para reducir el truncamiento antes de enunciar el diagnóstico (comentario del piloto). No se usó penalización de repetición ni `no_repeat_ngram_size` en las corridas finales (la penalización falla en Mini-VLM; el posprocesamiento post-hoc de repeticiones se evaluó y no se adopta). | `llava_med.py` l.195 y `mini_vlm.py` l.255 (`do_sample=False`); `Codigo/slurm/mendieta/pilot_ensemble_v2_llava.sh` l.20 (motivo de 384); 512 por defecto en `generate_report.py` l.218 y en las corridas v1–v2 (`slurm/mendieta/v1` y `v2`); 384 en `ensemble_full_*.sh` y en `v3/`, `v4/`; `slurm/mendieta/v3/rag_generation.sh` l.18–20 (P5.5 quitado); `Codigo/scripts/repetition_postprocess.py` y `Codigo/docs/resul/analisis_pipeline_avanzado_resul_20260908.md` (addendum: no se adopta) | `holtzman2020curious` |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Tabla 3.7.a — Configuración de LoRA y del entrenamiento (etapa 1 y etapa 2) | Parámetro, descripción breve y valor; filas agrupadas por etapa (formato de la tesina de ejemplo, Tabla 3.6) | Ver filas abajo | a armar, con las preguntas Q1, Q2, Q5, Q6 resueltas |
| Tabla 3.7.b — Decodificación | Estrategia, máximo de tokens, instrucción, semilla, posprocesamiento | Ver filas abajo | a armar |
| (sin figura) | Ejemplo de texto de SkinCoT: ya está en 3.3 (`ej_skincot_human.jpg`), no se repite acá | — | no corresponde |

**Tabla 3.7.a (propuesta):**

| Parámetro | Valor | Fuente |
|---|---|---|
| *Etapa 1 (proyector)* | | |
| Parámetros entrenables | Proyector visual (LLaVA-Med: `multi_modal_projector`; Mini-VLM: `img_projection`, `glb_GN`, `sub_GN`) | `two_stage.py` `_freeze_for_stage1` l.374 |
| Congelado | Codificador visual y LLM | idem |
| Datos | SkinCAP: 2492 / 534 / 535 (entrenamiento / validación / prueba) | `Codigo/data/splits/skincare_skincap_splits.json` (suma 3561; Q10) |
| Optimizador y planificador | AdamW, decaimiento 0, eps 1e-7; coseno (`CosineAnnealingLR`) | `two_stage.py` l.1158–1174 |
| Tasa de aprendizaje, épocas, lote | a definir (Q1): 1.09e-4 y 2 épocas (mejor del barrido), o 1e-3 y 5 épocas con paciencia 2 (Mendieta), o 2e-3 y 1 época (TOKO) | `Codigo/outputs/mejores_params.txt`; `slurm/mendieta/train_vlm_s1_*.sh`; `slurm/toko/train_vlm_s1_llava.sh` |
| *Etapa 2 (LoRA sobre el LLM; checkpoints finales `stage2_*_v2`)* | | |
| Rango $r$ | 64 | `lora_config.json` del checkpoint Mini-VLM; `train_vlm_s2*.sh` v2 |
| Escala $\alpha$ | 64 ($\alpha/r = 1$) | idem |
| Dropout de LoRA | 0.0 | idem |
| Módulos | `q_proj`, `v_proj` del LLM (Q2) | idem; `train_vlm_stage2.py` l.232 |
| Tasa de aprendizaje | $2.495 \times 10^{-5}$, constante (sin planificador) | `slurm/mendieta/v2/train_vlm_s2*.sh`; `two_stage.py` `run_stage2` (`scheduler=None`) |
| Optimizador | AdamW, decaimiento 0.01, eps 1e-7 | `two_stage.py` `run_stage2` |
| Épocas | máximo 10, detención temprana sobre `val_loss` con paciencia 3 | `slurm/mendieta/v2/`; `train_vlm_stage2.py` l.227 |
| Lote y acumulación | 4 y 8 (efectivo 32), reducción automática si hay falta de memoria (Q6) | `slurm/mendieta/v2/`; `train_vlm_stage2.py` (OOM) |
| Longitud máxima | 2048 tokens | `train_vlm_stage2.py` l.213 |
| Recorte de gradiente | norma 1.0 | `two_stage.py` l.782 |
| Precisión | bf16 en GPU Ampere o posterior | `Codigo/src/utils/device.py` `get_training_dtype` |
| Semilla | 42 | `slurm/mendieta/v2/` |
| Datos | SkinCoT EN: 2128 / 456 / 457 (entrenamiento / validación / prueba) | `Codigo/data/splits/skincare_skincot_splits.json` |
| Instrucción | «Describe this skin lesion.» en todos los pares | `CAPTION_INSTRUCTION` |

**Tabla 3.7.b (propuesta):**

| Parámetro | Valor | Fuente |
|---|---|---|
| Estrategia | voraz (`do_sample=False`) en ambos VLM | `llava_med.py` l.195; `mini_vlm.py` l.255 |
| Máximo de tokens nuevos | 384 (512 en v1 y v2) | slurm, ver P9 |
| Llamadas | una imagen por llamada | `generate_report.py` `_generate_single` |
| Penalización de repetición | no usada en corridas finales (disponible por CLI) | `rag_generation.sh` l.18–20 |
| Instrucción de inferencia | «Describe this skin lesion.» en la condición base | `generate_report.py` l.52 |
| Semilla | 42 | slurm |
| Posprocesamiento | se quitan los bloques `<think>` antes de medir | `evaluate_reports.py --strip-reasoning` |

**Valores de `Codigo/configs/phase2_generation.yaml` (r 64, alpha 128, dropout 0.05, siete módulos, 3 épocas, lr 2e-5) no se usan en esta tabla**: el código no lee ese YAML (ver Q3).

## Prosa ya escrita que se conserva

- **Párrafo 1** de `05-generacion-reportes.tex` (desde «El reporte dermatológico deja por escrito…» hasta «…quedan fuera del alcance.») pasa a P1, sin cambios de contenido.
  Revisar en la pasada de estilo: (a) la frase «las que los conjuntos de pares imagen–texto del área anotan junto a cada imagen» apoya la afirmación en `shen2025skincare`; el README dice que SkinCAP anota descripciones y SkinCoT, razonamiento diagnóstico. Conviene precisar qué anota cada subconjunto (Q14). (b) La primera oración abre con «El reporte…» y no con su función en el capítulo: aceptable, la guía no lo prohíbe.
- El `\pendiente{}` del final se reemplaza por las subsecciones 3.7.2–3.7.5. No quedan `\pendiente` en el archivo salvo los que dependan de Q1.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`):** `REPORT_PROMPT`, las plantillas condicionadas por diagnóstico (`confirmed`, `noreasoning`, RAG, incertidumbre, las de SkinVL) y la lista de instrucciones de SkinVL. En 3.7 solo se nombra la instrucción base y la regla «sin bloques <think>».
- **Apéndice E (`ap:reproducibilidad`):** comandos exactos de entrenamiento y generación (`slurm/mendieta/v2/`, `v3/`, `v4/`) y el conteo de bloques `<think>` como script reproducible.
- **Apéndice F (fichas de conjuntos y modelos):** ficha de SkinVL (origen de los pesos, conversión, licencia) si el texto de P3 resulta largo.

## Lo que NO va en esta sección (y dónde está)

- **Resultados de cualquier generador:** consistencia diagnóstica, recall de entidades, BLEU, ROUGE, BERTScore, hedging, dx incorrecto, repetición, ablaciones (imagen frente a diagnóstico, diagnóstico erróneo), comparación con SkinVL, variantes de prompt de SkinVL, posprocesamiento de repeticiones: Cap. 5 (`cp:res_gen`, `sec:res_gen_skinvl` ya existe).
- **Razonamiento de la cascada, plantillas con diagnóstico, *noreasoning*, *grounding* por recuperación, ruteo:** 3.8.
- **Clasificación de los VLM por verosimilitud, DermLIP, *linear probe*, kNN y SVM:** 3.6 (`sec:met_clasif_vlm`).
- **Costo de entrenamiento y de generación (horas de GPU):** 3.9 (costo computacional, `sec:met_complementarios`). `ejecuciones.md` tiene la medición, no es un desempeño.
- **Definiciones** de LLM, LoRA, decodificación, alucinación, *hedging*, RAG, reporte clínico y VLM generativo: Cap. 2. Solo `\ref`.
- **Fundamentos de AdamW y del planificador coseno** (`loshchilov2019decoupled`, `loshchilov2017sgdr`): Cap. 2 (2.1, optimización), solo se nombran acá.
- **Formato del `<think>` de SkinCoT y ejemplo de texto:** 3.3.
- **Planes que se anularon** (`reportes_mejoras_v3_class_weights_plan_20260525.md`, focal loss, *commitment-line* en los objetivos de entrenamiento): no entran; la anulación consta en el encabezado del plan.

## Preguntas abiertas para el autor

1. **Etapa 1: ¿qué configuración produjo `stage1_llava_med/best_model.pt` y `stage1_mini_vlm/best_model.pt`?** Hay tres candidatos: lr 1.094512e-04 y 2 épocas (`Codigo/outputs/mejores_params.txt`, barrido en Mendieta), lr 1e-3 y 5 épocas con paciencia 2 (`slurm/mendieta/train_vlm_s1_*.sh`), o lr 2e-3 y 1 época (`slurm/toko/train_vlm_s1_llava.sh`, `USAGE.md`). El checkpoint no trae `sweep_config.json`. Sin esto la fila de la etapa 1 no se puede completar.
2. **LoRA en Mini-VLM (Phi-3.5-vision): ¿existen los módulos `q_proj` y `v_proj`?** En la implementación de Phi-3 que conozco, la atención usa un proyector combinado `qkv_proj` (y el MLP, `gate_up_proj`); hay que verificarlo en el código remoto de Phi-3.5-vision. Si no existen, PEFT no aplica el adaptador a la atención o falla, y `generate_report.py` carga el checkpoint con `load_state_dict(strict=False)`, que no avisa de claves faltantes. Verificar las claves del adaptador en `best_model.pt` sin cargar el modelo. Si el nombre no coincide, la Tabla 3.7.a y la descripción de P6 cambian.
3. **`phase2_generation.yaml` no se lee en ningún script** (`grep` de `phase2_generation` en `src` y `scripts` vacío). Sus valores (r 64, alpha 128, dropout 0.05, siete módulos, 3 épocas, lr 2e-5) no son los de las corridas finales. Decidir: actualizarlo a lo que se corrió, o declarar que las corridas se lanzaron con argumentos de línea de comando. `AGENTS.md` dice que `configs/` es la fuente de verdad de hiperparámetros, así que la discrepancia tiene que resolverse antes de cerrar el capítulo.
4. **Proyector en la etapa 2.** `train_mlp: true` en el YAML y el comentario de `_freeze_vision_encoder` dicen que el proyector se entrena. Pero `get_peft_model` congela los parámetros no adaptadores, así que, si nadie los marca en `modules_to_save`, el proyector queda congelado en la etapa 2. La descripción de P4 y el párrafo de LLaVA del Cap. 2 (`05-vlm.tex`, «el proyector se entrena entero») dependen de esto. Verificar con `print_trainable_parameters` del log de un job.
5. **Relación con el Cap. 2:** el texto de `05-vlm.tex` describe la segunda etapa de LLaVA como «se ajustan el proyector y el LLM». Si la respuesta a Q4 es que el proyector queda congelado, el Cap. 2 no debe presentarlo como parte del ajuste de este trabajo.
6. **Tamaño de lote efectivo de la etapa 2 v2.** El SLURM pide lote 4 y acumulación 8 (32). `train_vlm_stage2.py` reduce el lote a la mitad ante falta de memoria y duplica la acumulación, así que el efectivo se mantiene, pero el lote real puede haber cambiado. Confirmar en el log de los jobs `stage2_*_v2` (línea «Iniciando entrenamiento | batch_size | grad_accum»).
7. **Cuantización.** `USAGE.md` dice que LLaVA-Med se carga en 4 bits si la VRAM libre es menor que 14 GB; en el entrenamiento (`train_vlm_stage2.py`) el umbral es el requisito más 4 GB. Confirmar que las corridas de A30 (24 GB) no cuantizaron. Si alguna lo hizo, la Tabla 3.7.a tiene que decirlo.
8. **Número de épocas del modelo final.** Uso `stage2_*_v2` (10 épocas), porque es el checkpoint que consumen las corridas de ensamble, RAG, incertidumbre y reanclaje (`ensemble_full_*.sh`, `v3/`, `v4/`). Las épocas 3 (v1) y 5 (barrido) quedan como historia de iteraciones; no se mencionan como resultados en 3.7. Confirmar.
9. **LLaVA-Med base.** El código usa `chaoyinshe/llava-med-v1.5-mistral-7b-hf` (Mistral-7B, v1.5). `Codigo/configs/models/llava_med.yaml` dice «llm: meta-llama/Llama-2-7b-chat-hf» y `pretrained_weights: microsoft/llava-med-v1.5-mistral-7b`; `Codigo/CLAUDE.md` dice «LLaMA-2 7B». La tesina tiene que decir Mistral-7B (ver `jiang2023mistral`). Los YAML y `CLAUDE.md` están desactualizados.
10. **Mini-VLM y SkinCAP.** (a) `Codigo/configs/models/mini_vlm.yaml` describe «CLIP ViT-B/16 + Phi-3-mini»; el código carga `microsoft/Phi-3.5-vision-instruct`, que es lo que dicen 2.3 y 3.6 (`fichas/`). Decidir y corregir el YAML. (b) SkinCAP: el README dice 4000 imágenes, pero los splits suman 3561 (2492 + 534 + 535). ¿Qué pares se excluyen y por qué? Afecta la Tabla 3.7.a y la 3.3.
11. **SkinVL: pesos y cita.** La inspección del repo (`skinvl_ensemble_plan_20260705.md`) dice que los pesos publicados son completos, sin adaptador LoRA. El Cap. 2 (`10-estado-arte.tex`, l.351) atribuye a `zeng2025mmskin` un ajuste con proyección y adaptadores LoRA. Las dos cosas pueden ser ciertas (el repo publica los pesos ya fusionados); conviene escribir P3 según lo que dice el artículo y anotar la inspección como dato propio. Propuesta de cita: `zeng2025mmskin` (el mismo que usa el Cap. 2 para SkinVL). Si el autor prefiere una referencia dedicada al repo `zwq803/SkinVL-MM`, va a `refs_pendientes.md`. Confirmar que `zeng2025mmskin` es el artículo que presenta SkinVL.
12. **Declaración sobre la fuga en el Cap. 3 (§Alcance 6 de la ficha del capítulo).** Dice que «los VLM generales ajustados (su entrenamiento contiene lesiones del test)». Con lo que leí: SkinCAP y SkinCoT vienen de Fitzpatrick 17k y DDI (README de SkinCaRe), y MM-SkinQA son imágenes de libros de histopatología (`VQA.csv`). No encontré solapamiento con HAM10000. Puede venir del preentrenamiento de LLaVA-Med o del corpus de MM-Skin (SkinVL), que no verifiqué. Antes de declararlo en P3 o P5, verificar qué fuente lo produce. Si no hay solapamiento, la declaración se quita.
13. **Duplicación con 3.1.** La ficha 3.1 (Tabla de secciones) dice que «generación = descripción + impresión diagnóstica» se define en 3.1. P1 define las mismas dos partes. Propongo que 3.1 las nombre y remita a `sec:met_generacion`, y que 3.7 conserve la prosa ya escrita. Decisión del autor (guía §2.1 y §3).
14. **Qué anota cada subconjunto de SkinCaRe.** Para la frase de P1 sobre los conjuntos de pares: SkinCAP tiene captions de dermatólogos; SkinCoT, razonamiento diagnóstico revisado. Confirmar si «impresión diagnóstica» está en el texto de SkinCoT o si el texto del reporte se construye a partir de él (la conclusión del razonamiento).
15. **Impresión diagnóstica en la condición base.** La instrucción «Describe this skin lesion.» no pide un diagnóstico. El modelo, entrenado con SkinCoT, produce una conclusión por el razonamiento. ¿La impresión diagnóstica de la condición base está en el texto generado? Verificar con 3 o 4 reportes de una corrida (no hace falta una métrica). Si no aparece, P1 tiene que decir que la impresión solo se obtiene con diagnóstico declarado (3.8).
16. **Premisa del último párrafo de la transición.** La ficha del capítulo dice «un generador que no discrimina necesita que el diagnóstico venga de afuera». Es una conclusión de resultados (Cap. 4 y 5). En 3.7 puede aparecer como motivo, con `\ref` al capítulo de resultados y sin cifras. Confirmar que el autor quiere esa formulación.
17. **Memoria que justifica LoRA (P6).** La razón «una GPU de consumo» necesita una cifra. Las estimaciones de `Codigo/configs/models/*.yaml` (14 GB con LoRA para LLaVA-Med, 8 GB para Mini-VLM) y las de `USAGE.md` son estimaciones, no mediciones, y no hay medición del ajuste completo en el repositorio. Opciones: citar a `hu2021lora` para la reducción de memoria (es lo que ya afirma el Cap. 2) y decir que el trabajo usa LoRA por su costo de memoria, sin cifra propia; o medir la VRAM de un ajuste completo y citarla como dato del trabajo.

## Decisiones tomadas por cuenta propia

- **D1. Mini-VLM = `microsoft/Phi-3.5-vision-instruct`** (código, `mini_vlm.py`, y lo que dicen 2.3 y 3.6). El YAML queda como discrepancia (Q10).
- **D2. Configuración de LoRA y entrenamiento de la etapa 2 = la del checkpoint final (`stage2_*_v2`)**, tomada de `lora_config.json` y de los SLURM v2, no del YAML (Q3).
- **D3. Generadores finales = los checkpoints `stage2_*_v2`.** Los usan `ensemble_full_*.sh` y los scripts de `v3/` y `v4/`. Las generaciones v1 y v2 (512 tokens; la v1 con el checkpoint de 3 épocas) quedan como iteraciones previas y no son el modelo final.
- **D4. Instrucción de inferencia = la de entrenamiento** («Describe this skin lesion.»). Justificación desde el objetivo: que el prompt de inferencia no se aleje de lo que vio el modelo. La versión anterior del prompt, más larga, se abandonó por esa razón; no se describe acá.
- **D5. Entrenamiento con el texto completo de SkinCoT, incluidos los bloques `<think>`.** Coincide con el código. Se justifica porque el razonamiento es auditable; la separación se hace en la evaluación, no en el entrenamiento.
- **D6. Decodificación voraz, 384 tokens, una imagen por llamada, semilla 42.** 384 por el piloto con 256 (`pilot_ensemble_v2_llava.sh`, l.20).
- **D7. SkinVL sin ajuste propio**, convertido a HF sobre la base `chaoyinshe/llava-med-v1.5-mistral-7b-hf`, con el mismo `REPORT_PROMPT` y la misma decodificación que los otros dos generadores. Así la comparación cambia solo el generador.
- **D8. La penalización de repetición y `no_repeat_ngram_size` no se usan en las corridas finales.** La de Mini-VLM falla (Phi-3.5, tokens de imagen fuera del rango del vocabulario, según `analisis_pipeline_avanzado_resul_20260908.md`). Para LLaVA-Med quedó diferida (`mejoras_resultados_p5_plan_20260713.md`). Se declara en 3.7, sin cifras.
- **D9. El posprocesamiento de repeticiones (`repetition_postprocess.py`) no se adopta.** Se descarta por su resultado (addendum del 2026-09-08). El resultado va al Cap. 5, no acá.
- **D10. Tablas de configuración en el cuerpo, grillas no** (la búsqueda de LoRA completa va a `ap:hiperparametros`). Sigue el ejemplo (§3.6).

## Números sin verificar

- Duración del entrenamiento y del procesamiento de generación (`ejecuciones.md`): no se usan en 3.7.
- «trasplantados ≈ 291» del runbook de SkinVL: es lo que espera el runbook; no encontré el log real de la conversión. No se cita como dato.
- Tamaño exacto de los conjuntos de SkinCAP (Q10).
- Lote efectivo y cuantización reales de la etapa 2 v2 (Q6, Q7).
