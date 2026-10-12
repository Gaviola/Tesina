# Ficha 3.6 — Clasificación con modelos visión–lenguaje

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/06-clasificacion-vlm.tex`. Labels: `sec:met_clasif_vlm` (fijo). Propuestos: `sec:met_vlm_generativos`, `sec:met_vlm_estrategias`, `sec:met_dermlip`, `eq:met_likelihood`, `fig:met_zsvslik`.

## Hilo conductor

Pregunta que responde la sección: ¿puede un VLM obtener una clase de cada imagen con las mismas siete categorías que los clasificadores de la Sección~\ref{sec:met_supervisados}, y con qué procedimiento se la obtiene?

Viene de: 3.5 deja los clasificadores supervisados, que devuelven una distribución sobre las siete clases y no generan texto. Esa diferencia abre PI1: si un VLM clasifica igual de bien.

Deja instalado: los dos VLM generativos y las cuatro maneras de obtener una clase con ellos; el checkpoint ajustado con LoRA, que la Sección~\ref{sec:met_generacion} también usa; DermLIP con sus cuatro modos de uso y su control sobre Swin-ImageNet congelado. La Sección~\ref{sec:met_generacion} ajusta los generativos para redactar el reporte; la Sección~\ref{sec:met_pipeline} usa el kNN con DermLIP.

```
P1   Dos familias de VLM responden PI1: generativos (Mini-VLM, LLaVA-Med), que devuelven texto,
     y contrastivo (DermLIP), que no genera. Se presentan las dos       función: justifica
     ↓ necesidad — los generativos devuelven texto, así que hace falta decidir cómo se convierte en clase
P2   Mini-VLM: Phi-3.5-vision-instruct (codificador CLIP ViT-L/14 a 336 px, proyección MLP, LLM
     Phi-3.5-mini; 4.1 mil millones de parámetros). Motivo: pesos abiertos y tamaño que permite LoRA
     en una GPU de consumo                                                  función: describe · justifica
     ↓ contraste — LLaVA-Med es mayor y su entrenamiento es biomédico
P3   LLaVA-Med v1.5 con Mistral-7B (CLIP ViT-L/14, proyección, Mistral-7B), entrenado con figuras y
     leyendas biomédicas. Motivo: es el VLM biomédico con el que se contrasta el de propósito general
                                                                            función: describe · justifica
     ↓ necesidad — ninguno de los dos devuelve siempre una etiqueta: hacen falta cuatro estrategias
P4   Cuatro estrategias para obtener una clase: zero-shot por generación, likelihood scoring,
     Chain-of-Thought y ajuste fino con LoRA (lista)                        función: describe
     ↓ causa — la generación depende de la decodificación y puede no contener una etiqueta; el scoring compara las clases directamente
P5   Likelihood scoring: qué compara, la fórmula (eq:met_likelihood) y por qué nunca produce «desconocido»
                                                                            función: define · justifica
     ↓ ampliación — con la misma comparación, sin imagen, se separa el lenguaje de la imagen
P6   Control sin imagen: el scoring se repite con una imagen gris neutra          función: justifica
     ↓ contraste — hasta aquí, los VLM generativos; DermLIP es otro tipo de modelo
P7   DermLIP: VL contrastivo ViT-B/16 preentrenado en Derm1M, que no genera texto. Motivo: separar la
     especialización de dominio de la modalidad generativa                  función: define · justifica
     ↓ necesidad — DermLIP sirve con cuatro modos, todos sobre embeddings congelados
P8   Cuatro modos (lista): zero-shot, linear probe, kNN (k = 3) y SVM-RBF    función: describe
     ↓ contraste — ¿lo que clasifica es la representación o la cabeza? Se responde con un control
P9   Control: las mismas cabezas clásicas sobre Swin-ImageNet congelado     función: justifica
     ↓ limitación — el resultado depende de la partición, y la partición anterior tiene fuga
P10  Partición: qué se ajusta sobre la partición disjunta por lesión y qué quedó sobre la anterior
                                                                            función: limita
→ Transición a la Sección~\ref{sec:met_generacion}: «Los VLM generativos se ajustan en la Sección~\ref{sec:met_generacion} para redactar el reporte, y ese mismo checkpoint es el que aquí se evalúa como clasificador.»

Se definen acá (y no se vuelven a definir): zero-shot por generación con parseo y «desconocido»; likelihood scoring con la ecuación eq:met_likelihood (sinónimos, normalización por tokens, ensamble de prompts); Chain-of-Thought con su formato y parseo; control sin imagen; los modos de DermLIP (zero-shot por plantillas, linear probe, kNN con k = 3, SVM-RBF); control con Swin-ImageNet.
Se retoman de antes (solo se nombran, con \ref): CLIP (`sec:marco_vlm_clip`); VLM generativo y clasificación por verosimilitud (`sec:marco_vlm_generativos`, `eq:marco_lm`); LLM y decodificación voraz (`sec:marco_llm`); LoRA (`sec:marco_llm_lora`); similitud coseno (`eq:marco_cos`); kNN (`eq:marco_knn`, `eq:marco_vecinos`); ajuste fino (`sec:marco_transferencia`); fuga de información (`sec:marco_regularizacion`); línea base (`sec:marco_vision`).
Extensión: 10 párrafos y tres subsecciones, unas 3.5 páginas.

## Subsecciones

- **3.6.1 Mini-VLM y LLaVA-Med** (`sec:met_vlm_generativos`): P2 y P3. Arquitectura, tamaño y motivo de cada modelo.
- **3.6.2 Cuatro estrategias para obtener una clase** (`sec:met_vlm_estrategias`): P4 a P6. Las cuatro estrategias, la fórmula del scoring y el control sin imagen.
- **3.6.3 DermLIP y sus modos de uso** (`sec:met_dermlip`): P7 a P10. Qué es DermLIP, sus cuatro modos, el control y la partición.

P1 y la transición quedan fuera de subsección.

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Dos familias de VLM: generativos (Mini-VLM, LLaVA-Med) y contrastivo (DermLIP). PI1 pregunta por los generativos, que son la familia que devuelve texto. | Salida de los clasificadores de 3.5 (sin texto), `sec:met_supervisados`. PI1 y OE: Sección~\ref{sec:met_tareas}. | `radford2021learning`, `liu2023visual` (ya en Cap. 2; solo \ref) |
| P2 | Mini-VLM es Phi-3.5-vision-instruct, con codificador CLIP ViT-L/14 a 336 px, proyección MLP y LLM Phi-3.5-mini (32 capas, 3072 dimensiones). Tamaño: 4.1 mil millones de parámetros. Motivo: pesos abiertos y LoRA en una GPU de consumo (8 GB estimados). | `hf://models/microsoft/Phi-3.5-vision-instruct/config.json` (`img_processor.model_name` = `openai/clip-vit-large-patch14-336`; `hidden_size` 3072; `num_hidden_layers` 32; `embd_layer.projection_cls` = mlp). Ficha del modelo: 4146.6M parámetros. `src/models/mini_vlm.py` (MODEL_NAME; docstring, ViT-L/14). `configs/models/mini_vlm.yaml` (`vram_estimate.lora: 8`, estimación). | `abdin2024phi3` (Phi-3 report, arXiv:2404.14219, que la ficha del modelo lista) |
| P3 | LLaVA-Med v1.5 con Mistral-7B: CLIP ViT-L/14, proyección MLP, Mistral-7B. Entrenado con figuras y leyendas de la literatura biomédica. Motivo: es el VLM biomédico con el que se contrasta el de propósito general. LoRA estimado en 14 GB, QLoRA en 10 GB. | `src/models/llava_med.py` (MODEL_NAME = `chaoyinshe/llava-med-v1.5-mistral-7b-hf`; docstring: CLIP ViT-L/14, MLP, Mistral-7B). `configs/models/llava_med.yaml` (`vram_estimate`; estimación). Entrenamiento biomédico: Cap. 2, `sec:marco_vlm_generativos` (no verificado en esta ficha). | `li2023llavamed`. La atribución de v1.5 Mistral queda en Preguntas abiertas (4). |
| P4 | Enumeración de las cuatro estrategias (detalle abajo). Todas usan el mismo conjunto de siete categorías y el mismo conjunto de prueba. | Ver «Detalle de P4 y P8» más abajo. | `hu2021lora` (estrategia d); `shen2025skincare` (SkinCaRe, sobre el que se ajusta el checkpoint) |
| P5 | Likelihood scoring: para cada imagen y cada clase, se toma el máximo entre sus tres sinónimos del log-probabilidad normalizado por tokens; después se promedia sobre los cuatro prompts y se elige la clase de mayor valor. Nunca produce «desconocido». La respuesta generada, en cambio, depende de la decodificación y puede no contener ninguna etiqueta. | `src/evaluation/vlm_scoring.py`: `PROMPT_TEMPLATES` (O1, O2, C1, C2), `CLASS_SYNONYMS` (3 por clase), `score_class` (máximo por sinónimo, normalización por `n_tok`), `score_image` (promedio de los 4 prompts; `pred_ensemble`). Docstring del módulo: «Length normalization», «Multi-sinonimo», «Ensemble de 4 prompts». Fórmula propuesta: $s_c = \frac{1}{4}\sum_{p} \max_{s \in S_c} \frac{\log P(s \mid \text{prefijo}_p, \text{imagen})}{\lvert s \rvert}$; clase predicha $\arg\max_c s_c$ (`eq:met_likelihood`). | `eq:marco_lm` (Cap. 2, solo \ref) |
| P6 | Control: el scoring se repite con cada imagen reemplazada por una gris neutra de 224 × 224 píxeles (RGB 128). Si el modelo sigue prediciendo la misma distribución, el prompt y no la imagen guía la respuesta. Se describe el procedimiento; los resultados van al Cap. 4. | `scripts/train_vlm_classify.py` líneas 147 a 150 (`blank_image`), sufijo `_noimage` (línea 265). `docs/ideas/prior_lenguaje_noimage_plan_20260823.md` (criterio de interpretación, § «Criterios de éxito»). | Ninguna nueva |
| P7 | DermLIP: VL contrastivo CLIP-style con ViT-B/16 (checkpoint `redlessone/DermLIP_ViT-B-16`, vía open_clip), preentrenado en Derm1M, alrededor de un millón de pares imagen–texto dermatológicos. No genera texto. Embedding de 512 dimensiones. Motivo: separar la especialización de dominio de la modalidad generativa. | `src/models/dermlip.py` (línea 25, `hf-hub:redlessone/DermLIP_ViT-B-16`; línea 64, `open_clip.create_model_and_transforms`). `docs/resul/embeddings_resul_20260707.md` (dim 512). `docs/ideas/dermlip_clasificacion_plan_20260604.md` §1 y §2 (motivación; no genera). Cifra de Derm1M: Cap. 2 (no verificada aquí). | `yan2025derm1miccv`; `radford2021learning` (solo \ref, Cap. 2) |
| P8 | Cuatro modos (lista, detalle abajo): zero-shot por similitud coseno con cuatro plantillas; linear probe; kNN con k = 3; SVM-RBF. Todos sobre embeddings de imagen congelados y normalizados. | `src/models/dermlip.py` líneas 28 a 35 (`DEFAULT_TEMPLATES`), 98 a 130 (`zero_shot_logits`, `embed_images`). `scripts/eval_dermlip_linearprobe.py` líneas 88 y 89. `scripts/dermlip_split_eval.py` líneas 100, 113 a 115. `scripts/embeddings_classical.py` líneas 77 a 82. | `cover1967nearest` (voto por vecinos, kNN); fórmulas `eq:marco_knn` y `eq:marco_vecinos` (Cap. 2, solo \ref) |
| P9 | Control: las mismas cabezas clásicas (SVM-RBF, regresión logística y random forest) sobre Swin-ImageNet congelado, sin ajuste en HAM10000. La diferencia entre las dos representaciones con la misma cabeza aísla el efecto de la representación. | `scripts/embeddings_classical.py` líneas 27 a 31 y 77 a 82 (RF con 300 árboles, `class_weight` balanced). Dimensión de Swin-ImageNet: 768 (`docs/resul/embeddings_resul_20260707.md`). Versión sobre la partición por lesión: `outputs/results/embeddings/embeddings_classical_les.json` (`docs/resul/split_lesion_resul_20260926.md` §6). | `liu2021swin` (solo como backbone; el ajuste fino no se describe aquí) |
| P10 | Partición. La zero-shot de DermLIP no depende de la partición (nunca vio HAM10000). Las cabezas (linear probe, kNN, SVM) y el control se ajustan sobre el entrenamiento de la partición disjunta por lesión, que es la que se reporta. Los VLM generativos ajustados (estrategia d y checkpoint de 3.7) se entrenaron con la partición anterior, que tiene lesiones del test. Se declara: la fuga solo podría favorecerlos. | `docs/resul/split_lesion_resul_20260926.md` §2 (partición: 6447 de entrenamiento, 1289 de validación, sin solapamiento), §6 (DermLIP ZS sin efecto de la partición; cabezas re-ajustadas), §8 (qué queda sobre la partición anterior). Decisión 6 de `fichas/03-materiales-metodos/00-capitulo.md` (lista de lo que queda sobre la partición anterior). | `shen2025skincare` no aplica aquí; fuga: `sec:marco_fundamentos` (Cap. 2, solo \ref) |

## Detalle de P4 y P8 (listas)

**P4, las cuatro estrategias** (`enumerate`, con el nombre en negrita):

1. **Zero-shot por generación.** Prompt `CLASSIFICATION_PROMPT` (Apéndice B). Decodificación voraz: `do_sample=False` en `src/models/mini_vlm.py` (línea 255) y en `src/models/llava_med.py` (línea 194). Longitud máxima por defecto de 32 tokens (`--max_new_tokens`). Parseo: coincidencia exacta con una etiqueta o la primera etiqueta que aparece como palabra completa (`parse_vlm_response`, `scripts/train_vlm_classify.py`). Sin etiqueta válida, la respuesta cuenta como «desconocido» (`UNKNOWN`).
2. **Likelihood scoring.** Ver P5 y `eq:met_likelihood`. Prompts: O1 «What is the most likely diagnosis for this dermoscopic image?»; O2 «Identify the type of skin lesion shown in this image.»; C1 y C2 listan las siete clases (texto en Apéndice B). Prefijo de chat distinto por modelo (`_build_prefix` en `vlm_scoring.py`).
3. **Chain-of-Thought.** Prompt `COT_PROMPT`: razonamiento sobre rasgos (Features), diferenciales (Differential) y una línea final «Final diagnosis: [clase]». Longitud máxima de 200 tokens (`max(args.max_new_tokens, 200)`). Parseo: el campo `Final diagnosis:`; si falla, el parseo de la estrategia 1; sin etiqueta válida, «desconocido».
4. **Ajuste fino con LoRA.** El checkpoint del ajuste en dos etapas de la Sección~\ref{sec:met_generacion}, entrenado sobre SkinCaRe con LoRA (`configs/phase2_generation.yaml`: r = 64, α = 128, dropout 0.05, siete módulos lineales: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`). Se evalúa por verosimilitud o por CoT. No se entrena con etiquetas de HAM10000 (ver Preguntas abiertas 5 y 6).

**P8, los cuatro modos de DermLIP** (`enumerate`, con el nombre en negrita):

1. **Zero-shot.** Similitud coseno entre el embedding de la imagen y el de cada clase, con el texto de cada clase promediado sobre las cuatro plantillas de `DEFAULT_TEMPLATES` («This is a skin image of {c}», «A dermatoscopic image of {c}», «A clinical photograph of {c}», «An image showing {c}»). Argmax, sin «desconocido».
2. **Linear probe.** Regresión logística sobre el embedding normalizado congelado; `C = 1.0`, `class_weight = balanced`, `max_iter = 2000`. Sin estandarizar (en `dermlip_split_eval.py` el `StandardScaler` se aplica solo al SVM).
3. **kNN.** `k = 3`, similitud coseno, voto mayoritario; si hay empate, gana el vecino más similar (`dermlip_split_eval.py` línea 100; mismo criterio que `build_rag_index.py`).
4. **SVM-RBF.** `SVC(C = 10, kernel = rbf, class_weight = balanced)` sobre embeddings estandarizados con `StandardScaler` (`embeddings_classical.py` línea 80; `dermlip_split_eval.py` línea 115).

Los valores de las cabezas son fijos en el código. No se ve un barrido de hiperparámetros para ellas (a verificar; ver Preguntas abiertas 12).

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Zero-shot frente a likelihood (`fig:met_zsvslik`) | (a) Zero-shot: imagen y prompt → el VLM genera texto → parseo → clase o «desconocido». (b) Likelihood: imagen y prompt → el VLM puntúa el nombre de cada clase → argmax, sin «desconocido». Sin cifras. | `Docs/experimentacion/experimentacion.tex` líneas 69 a 91 (`fig:zsvslik`). Redibujar con `figentrada`, `figtarea`, `figsalida` de `Configurations/13-Figuras.sty`, con la paleta Okabe–Ito. Archivo nuevo: `Figures/Capitulos/03-Materiales-Metodos/zsvslik.tex`. | a adaptar |

No se incluye la figura `fig:tipos` (tres familias de modelos) de `experimentacion.tex`: la distinción entre familias ya la hacen 2.3 y 3.5 (ver Decisiones, D3). Tampoco hay tabla de estrategias: son alternativas paralelas y van en lista (guía §3).

## Prosa ya escrita que se conserva

Nada. `04-clasificacion-vlm.tex` tiene solo un `\pendiente` con la intro de las cuatro estrategias, y `03-modelos-evaluados.tex` tiene solo `\pendiente` en sus cuatro subsecciones. El `\pendiente` de `04` se reemplaza por esta sección.

Traslado de contenido: las subsecciones de VLM generales y de DermLIP de `03-modelos-evaluados.tex` pasan a `06-clasificacion-vlm.tex`. La subsección de SkinVL pasa a `07-generacion-reportes.tex` (Decisión D2). El archivo `03` lo reescribe la Sección 3.5, que se renombra a `05-clasificadores-supervisados.tex`.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`, `Chapters/Apendices/B-Prompts.tex`):** `CLASSIFICATION_PROMPT`; O1, O2, C1 y C2 completos; `COT_PROMPT`; los prefijos de chat de LLaVA-Med (`[INST] <image>` ... `[/INST]`) y de Mini-VLM (plantilla de chat con `<|image_1|>`); `CLASS_SYNONYMS` (21 términos: 7 clases por 3 sinónimos); `DEFAULT_TEMPLATES` de DermLIP.
- **Apéndice A (`ap:hiperparametros`):** no hay grillas de búsqueda para estas cabezas. Los valores fijos se citan en el cuerpo, en el «Detalle de P8».

## Lo que NO va en esta sección (y dónde está)

- **Cualquier desempeño** de las cuatro estrategias, de DermLIP en sus cuatro modos, del control sin imagen o del control con Swin-ImageNet: Cap. 4. Incluye el colapso en likelihood y la tasa de «desconocido» en generación.
- **La historia de las iteraciones** (v1 a v3 de la clasificación con VLM, los planes T1 a T5, el re-diagnóstico del colapso y la hipótesis de dominio clínico): Cap. 4 o Apéndice C (`C-Resultados-Complementarios.tex`), según el autor.
- **Saliencia de DermLIP:** no se presenta como evidencia de que el modelo mire la lesión; en `split_lesion_resul_20260926.md` §7 es un artefacto de la grilla de parches. Va a 3.9 (`sec:met_complementarios`) como limitación, si se incluye.
- **Explicación de CLIP, LLM, LoRA, decodificación voraz y clasificación por verosimilitud:** Cap. 2, solo \ref.
- **Adaptador LoRA de clasificación entrenado con etiquetas de HAM10000** (plan `vlm_clasificacion_v2_plan_20260501.md`, T3): no figura en esta ficha. Ver Preguntas abiertas 6.
- **Descriptores ABCDE:** `ABCDE_FEATURES` se define en `vlm_scoring.py`, pero no se usa en `COT_PROMPT` (búsqueda en `src/` y `scripts/`). No se describen como parte del CoT.
- **Mini-VLM como «médico»:** ver Preguntas abiertas 1.

## Preguntas abiertas para el autor

1. **Terminología.** La guía §4 fija «VLM médicos de propósito general» para los modelos. Mini-VLM (Phi-3.5-vision) es un VLM general, no médico. Propongo: «VLM de propósito general (Mini-VLM)» y «VLM biomédico (LLaVA-Med)». ¿Se cambia la fila de la tabla de términos o se mantiene la fórmula?
2. **Codificador de Mini-VLM.** El `config.json` del checkpoint dice CLIP ViT-L/14 a 336 px. Están en contradicción con: `Codigo/configs/models/mini_vlm.yaml` (CLIP ViT-B/16 + Phi-3-mini), los encabezados de `slurm/*/vlm_classify_mini*.sh` y `slurm/*/train_*mini*.sh` (ViT-B/16 + Phi-3-mini), `Codigo/docs/resul/INFORME_TECNICO.md` §3.4 y `Docs/experimentacion/experimentacion.tex` (CLIP ViT-B/16 + Phi-3.5). La ficha usa el valor verificado. Los archivos de código no se tocaron.
3. **Parámetros de Mini-VLM.** La ficha del modelo dice 4146.6M. Cap. 2 (`04-modelos-lenguaje.tex`, línea 35) y `measure_cost.py` / `costo_resul_20260705.md` dicen 4200. La ficha propone «4.1 mil millones». ¿Se unifica en Cap. 2 y en el resto?
4. **Atribución de LLaVA-Med v1.5 con Mistral.** Cap. 2 (`05-vlm.tex`) atribuye la versión 1.5 con Mistral a `zeng2025mmskin`. El checkpoint usado (`chaoyinshe/llava-med-v1.5-mistral-7b-hf`) es una conversión a HF. `configs/models/llava_med.yaml` dice «Llama-2-7b-chat» (desactualizado). ¿Se cita `li2023llavamed` y, si hace falta la fuente del checkpoint, se propone en `refs_pendientes.md`?
5. **Checkpoint del ajuste fino.** Hay dos versiones de Stage 2: v1 con 3 épocas (`phase2_generation.yaml`) y v2 con 10 épocas (`reportes_resul_v2`, y las corridas FT de `vlm_clasificacion_resul_v3`). ¿Cuál se describe en 3.6 y 3.7? La ficha asume v2 para la clasificación; la fecha de corte debe coincidir con 3.7.
6. **Adaptador LoRA de clasificación (T3).** La ficha asume que nunca se entrenó un LoRA sobre etiquetas HAM10000 (la estrategia d usa el checkpoint de SkinCaRe). Hay que confirmarlo con `ejecuciones.md`. Si se ejecutó, va a 3.6 como estrategia propia.
7. **Dónde se define el kNN.** La ficha lo define en 3.6 con k = 3, porque se presenta como cabeza sobre DermLIP. La Sección~\ref{sec:met_pipeline} lo remite. ¿Se acepta?
8. **Control sin imagen.** La ficha lo ubica en 3.6.2 como parte del método de likelihood. Alternativa: 3.9 como análisis complementario. ¿Cuál?
9. **Lentigo solar entre los sinónimos de BKL.** `CLASS_SYNONYMS["BKL"]` incluye «solar lentigo». Es una lesión pigmentada benigna, pero no una queratosis. Conviene que lo revise la rúbrica clínica (`docs/rubrica_validacion_clinica.md`) antes de escribirlo en el apéndice.
10. **Referencia de Derm1M.** El `.bib` tiene `yan2025derm1m` (arXiv) y `yan2025derm1miccv` (ICCV) para el mismo trabajo. La ficha cita `yan2025derm1miccv`. ¿Se elige una sola entrada? No se edita el `.bib` en esta tarea.
11. **Referencia de Phi-3.5-vision.** `abdin2024phi3` es el reporte técnico de Phi-3 (arXiv:2404.14219, que la ficha del modelo lista). No hay entrada para la ficha del modelo Phi-3.5-vision. ¿Se propone en `refs_pendientes.md`?
12. **Barrido de hiperparámetros de las cabezas.** No hay grilla en `embeddings_classical.py` ni en `dermlip_split_eval.py`. ¿Hubo búsqueda sobre validación (C, k) que deba declararse, o los valores son fijos? (a verificar)
13. **Clave de cita para la figura de `experimentacion.tex`.** Usa `li2024llavamed`, que no existe en el `.bib`. Corresponde `li2023llavamed`.
14. **Mini-VLM en clasificación.** `vlm_clasificacion_resul_v2` documenta batch de tamaño 1 para Mini-VLM, y `num_crops` por defecto (4) en clasificación. No verifiqué que se haya fijado otro valor. Va al apéndice si se describe.

## Decisiones tomadas por cuenta propia

- **D1. Subsecciones.** Tres subsecciones: 3.6.1 (generativos), 3.6.2 (cuatro estrategias), 3.6.3 (DermLIP). Labels propuestos en el encabezado.
- **D2. SkinVL sale de 3.6** y va a 3.7, como indica la tabla de secciones de la ficha del capítulo (D1 del andamiaje).
- **D3. Sin `fig:tipos`.** La distinción de familias ya la hacen 2.3 y 3.5. Si el autor quiere la figura aquí, se agrega como figura de contexto de 3.6.
- **D4. Estrategias en lista, no en tabla** (guía §3, «Alternativas paralelas en lista»). Sin tabla resumen, para no repetir el contenido.
- **D5. Fórmula propia del scoring** (`eq:met_likelihood`). La fórmula de la probabilidad y la normalización por longitud están en Cap. 2 (`eq:marco_lm`). La forma exacta del ensamble (max sobre sinónimos, promedio sobre prompts) es propia del trabajo y se define aquí (guía §3, «Conceptos, fórmulas y notación»).
- **D6. Motivos desde los objetivos** (guía §3). Mini-VLM y LLaVA-Med se incluyen porque el objetivo de ejecutar todo en una GPU de consumo exige LoRA, y el contraste biomédico frente a propósito general es parte de PI1. Confirmar.
- **D7. Ningún desempeño.** La sección describe datos y configuración. Los números que aparecen (parámetros, dimensiones, tokens, sinónimos, tamaños de partición) salen de archivos citados en la tabla.
- **D8. Control sin imagen y control con Swin-ImageNet** se describen como procedimiento, con el criterio de interpretación del plan. Los resultados van al Cap. 4.
- **D9. Partición declarada en P10**, como pide la ficha del capítulo (decisión 6), en lugar de en el apéndice.
- **D10. Cita de Phi-3.5-vision.** Se cita `abdin2024phi3` para Mini-VLM (corrección del coordinador: el reporte de Phi-3 presenta Phi-3.5-vision). No queda `\pendiente` por cita.
- **D11. P10 sin «la fuga solo podría favorecerlos».** La revisión cruzada (punto 4) y la decisión 6 de la ficha del capítulo fijan que los VLM generativos no se ajustaron sobre *HAM10000*; la frase de P10 se contradecía con eso. Se escribe la versión vigente: las cabezas de DermLIP y el control se reajustan sobre la partición por lesión, la zero-shot no depende de la partición y el checkpoint se entrenó con *SkinCaRe*.
- **D12. Terminología de la pregunta 1 aplicada.** Mini-VLM es «VLM de propósito general» y LLaVA-Med «VLM biomédico». La fila de la guía §4 sigue diciendo «médicos de propósito general» y queda para el autor.
- **D13. Cifras solo de datos.** Del reporte de la partición (§2) se usan 776 imágenes descartadas, 6\,447 de entrenamiento, 1\,289 de validación y 1\,503 de test. No se toma ningún valor de §6 (son resultados).
- **D14. Pendientes que quedan en el `.tex`.** Longitudes máximas de generación (estrategias 1 y 3, sin verificar en `train_vlm_classify.py`), cantidad de pares de *Derm1M* (a confirmar en `yan2025derm1miccv`) y si hubo búsqueda de $C$ y $k$ sobre validación (pregunta 12; en el código los valores son fijos, pero no se verificó en `ejecuciones.md`).
- **D15. Acrónimos nuevos propuestos** (no están en `Matter/05-Acronyms.tex`): `\acronimo{svm}{SVM}{máquina de vectores de soporte}{Support Vector Machine}`, `\acronimo{rbf}{RBF}{de base radial}{Radial Basis Function}`, `\acronimo{mlp}{MLP}{perceptrón multicapa}{Multilayer Perceptron}`, `\acronimo{gpu}{GPU}{unidad de procesamiento gráfico}{Graphics Processing Unit}`. Por ahora se escriben en texto llano en el `.tex` (SVM, RBF, MLP, GPU).

## Números que no pude verificar

- Estimaciones de VRAM (8 GB Mini-VLM, 14 GB y 10 GB LLaVA-Med): son valores de `configs/models/*.yaml`, no mediciones.
- Cifra de Derm1M («alrededor de un millón de pares»): viene de Cap. 2, no verificada contra el trabajo original.
- «Entrenado con figuras y leyendas biomédicas» (LLaVA-Med): viene de Cap. 2, no verificado aquí.
- Extensión de 3.5 páginas: estimación.
