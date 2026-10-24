# Ficha 3.5 — Clasificación con modelos visión–lenguaje

**Revisión del tutor (21/10/2026), aplicada el 22/10:** Antes era 3.5. La misma estructura que 3.3: el propósito (separar especialización de generación de texto) justifica los tres modelos; cada modelo con su motivo antes de sus características; figura de uso nueva (`vlms.tex`) con los generativos y las cuatro cabezas de DermLIP (23). Los controles (imagen gris y cabezas clásicas sobre DermLIP y Swin) pasan a «Procedimiento experimental». `sec:met_dermlip` queda como label dentro de 3.4.2.

**Revisión del autor (20/10/2026):** la estrategia 4 ya no habla del «checkpoint de la etapa 2» (el lector no lo conoce): dice que se repiten la verosimilitud y el CoT con los modelos ajustados con LoRA para generar reportes (3.6), sin HAM10000; sale la oración meta «Este control se describe aquí como procedimiento…»; se acorta la repetición de que DermLIP zero-shot y los VLM generativos no usan HAM10000.

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Antes era 3.6 y se llamaba `06-clasificacion-vlm`. Los modelos se nombran al final de la introducción, después de presentar los dos tipos de VLM; transición nueva a DermLIP (por qué se incluye); el último párrafo ya no repite los tamaños de la partición. Lo que la revisión quitó del texto está en la sección final «Quitado en la revisión del 18/10/2026».

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada y revisada el 18/10/2026.** Archivo: `Chapters/03-Materiales-Metodos/05-clasificacion-vlm.tex`. Labels: `sec:met_clasif_vlm` (fijo), `sec:met_vlm_generativos`, `sec:met_vlm_estrategias`, `sec:met_dermlip`, `eq:met_likelihood`, `fig:met_zsvslik` (la figura está en `Figures/Capitulos/03-Materiales-Metodos/zsvslik.tex`).

## Hilo conductor

Pregunta que responde la sección: ¿puede un VLM obtener una clase de cada imagen con las mismas siete categorías que los clasificadores de la Sección~\ref{sec:met_supervisados} (3.4), y con qué procedimiento se la obtiene?

Viene de: 3.4 deja los clasificadores supervisados, que devuelven una distribución sobre las siete clases y no generan texto. Esa diferencia abre PI1: si un VLM clasifica igual de bien. Antes: 3.1 definió las tareas, 3.2 los datos y 3.3 los criterios de evaluación.

Deja instalado: los dos VLM generativos y las cuatro maneras de obtener una clase con ellos; el checkpoint ajustado con LoRA, que la Sección~\ref{sec:met_generacion} (3.6) también usa; DermLIP con sus cuatro modos de uso y su control sobre Swin-ImageNet congelado. La Sección~\ref{sec:met_generacion} ajusta los generativos para redactar el reporte; la Sección~\ref{sec:met_pipeline} (3.7) usa el mismo kNN de DermLIP como índice de casos.

```
P1   Dos tipos de VLM responden PI1: generativos (devuelven texto: hay que decidir cómo se vuelve
     clase) y contrastivos (no generan, dan una representación sobre la que se clasifica). Se evalúan
     dos generativos (uno de datos generales, otro biomédico) y un contrastivo dermatológico;
     los generativos son Mini-VLM y LLaVA-Med                              función: justifica · anuncia
     ↓ presentación — los dos generativos nombrados se describen uno por uno
P2   Mini-VLM = Phi-3.5-vision-instruct: CLIP ViT-L/14 a 336 px, proyección MLP, Phi-3.5-mini (32 capas,
     3 072 dimensiones), unos 4 150 millones de parámetros. Motivo: pesos abiertos y tamaño que permite
     LoRA en una GPU de consumo                                              función: describe · justifica
     ↓ contraste — el segundo generativo es biomédico y más pesado
P3   LLaVA-Med v1.5 con Mistral-7B (mismo tipo de codificador, proyección, Mistral-7B), entrenado con
     figuras y leyendas biomédicas; unos 7 mil millones de parámetros de lenguaje. La comparación pone
     frente a frente biomédico y propósito general                           función: describe · justifica
     ↓ necesidad — ninguno devuelve siempre una etiqueta válida: hace falta fijar cómo se obtiene una clase
P4   Párrafo-puente: ninguno de los dos devuelve siempre una etiqueta válida cuando se le pide un
     diagnóstico; hace falta fijar cómo se obtiene una clase con cada uno    función: justifica
     ↓ necesidad — se enumeran las cuatro maneras
P5   Cuatro estrategias con las mismas siete categorías (lista): (1) zero-shot por generación con
     decodificación voraz y parseo, «desconocido» si no hay etiqueta; (2) likelihood scoring;
     (3) razonamiento paso a paso (CoT) con línea «Final diagnosis:», límites de 32 y 200 tokens;
     (4) ajuste fino con LoRA (checkpoint de la etapa 2 de generación, entrenado con SkinCaRe,
     no con HAM10000). Figura fig:met_zsvslik contrasta las dos primeras; prompts en el Apéndice B
                                                                            función: describe
     ↓ ampliación — la segunda estrategia se define con una fórmula
P6   Puntaje por verosimilitud (eq:met_likelihood): máximo entre los tres sinónimos del log-probabilidad
     normalizado por tokens, promedio sobre cuatro prompts, argmax. Nunca produce «desconocido»; la
     respuesta generada sí puede no contener etiqueta                       función: define · justifica
     ↓ ampliación — con el mismo cálculo, sin imagen, se comprueba si el puntaje depende de la imagen
P7   Control sin imagen: el cálculo se repite con una imagen gris neutra de 224 × 224 (RGB 128); si la
     distribución no cambia, guía el prompt y no la imagen. Solo procedimiento; resultados en los
     capítulos de resultados                                                función: justifica
     ↓ contraste — con los generativos, la clase sale siempre de un texto; DermLIP evita ese paso
P8   DermLIP: VL contrastivo al estilo de CLIP, ViT-B/16 y codificador de texto, preentrenado en los
     pares de Derm1M (sec:met_datasets); no genera texto, da un embedding de 512 dimensiones. Se
     incluye para distinguir dos explicaciones de un mal resultado de los VLM generales: falta de
     especialización o mala forma de clasificar (generar texto)             función: define · justifica
     ↓ necesidad — el embedding congelado y normalizado sirve de cuatro maneras
P9   Cuatro modos (lista): zero-shot por similitud coseno con cuatro plantillas; linear probe
     (regresión logística, C = 1.0, pesos balanceados); kNN (k = 3, voto mayoritario, empate al más
     similar); SVM-RBF (C = 10, estandarizado, pesos balanceados). Valores fijos, sin búsqueda de
     C ni de k sobre validación. Cierre: con cuatro cabezas sobre la misma representación, un resultado
     mezcla representación y cabeza                                         función: describe · limita
     ↓ necesidad — para separar ambos efectos hace falta un control
P10  Control: cabezas clásicas equivalentes (SVM-RBF con C = 10, regresión logística, random forest de
     300 árboles, pesos balanceados) sobre el embedding de Swin-ImageNet congelado, sin ajuste en
     HAM10000. Si la diferencia entre representaciones es la misma con cada cabeza, el efecto es de la
     representación                                                         función: justifica
     ↓ consecuencia — qué partición usa cada pieza, para que todo sea comparable con los supervisados
P11  Partición: cabezas y control se ajustan sobre el entrenamiento de la partición por lesión; DermLIP
     zero-shot y los VLM generativos (ajustados con SkinCaRe) no dependen de ella; todos se evalúan
     sobre la misma prueba que los supervisados                             función: limita
→ Transición a la Sección~\ref{sec:met_generacion}: «Los VLM generativos, además de clasificar, pueden redactar, y esa es la tarea de la sección siguiente.»

Se definen acá (y no se vuelven a definir): zero-shot por generación con parseo y «desconocido»; likelihood scoring con la ecuación eq:met_likelihood (sinónimos, normalización por tokens, ensamble de prompts); Chain-of-Thought con su formato, parseo y límite de tokens; control sin imagen; los modos de DermLIP (zero-shot por plantillas, linear probe, kNN con k = 3, SVM-RBF); control con Swin-ImageNet.
Se retoman de antes (solo se nombran, con \ref): VLM (`sec:marco_vlm`); CLIP; VLM generativo y clasificación por verosimilitud (`eq:marco_lm`); LLM y decodificación voraz (`sec:marco_llm`); LoRA; similitud coseno (`eq:marco_cos`); kNN (`eq:marco_knn`, `eq:marco_vecinos`); Derm1M y partición por lesión (`sec:met_datasets`, `sec:met_particiones`); ajuste en dos etapas (`sec:met_generacion`, 3.6).
Extensión: 11 párrafos de prosa, tres subsecciones, una figura, una ecuación y dos listas; el encabezado del `.tex` estima unas 3.5 páginas.

## Subsecciones

- **3.5.1 Mini-VLM y LLaVA-Med** (`sec:met_vlm_generativos`): P2, P3 y el párrafo-puente P4. Arquitectura, tamaño y motivo de cada modelo.
- **3.5.2 Cuatro estrategias para obtener una clase** (`sec:met_vlm_estrategias`): P5 a P7. Las cuatro estrategias, la fórmula del scoring y el control sin imagen.
- **3.5.3 DermLIP y sus modos de uso** (`sec:met_dermlip`): P8 a P11. Qué es DermLIP y por qué se incluye, sus cuatro modos, el control y la partición.

P1 queda fuera de subsección. La transición a 3.6 es la última oración de P11.

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas) |
|---|---|---|---|
| P1 | Dos tipos de VLM: generativos (responden con texto) y contrastivos (dan una representación). Se evalúan dos generativos —uno entrenado con datos generales y otro con datos biomédicos— y un contrastivo dermatológico. Nombra Mini-VLM y LLaVA-Med. | Salida de los clasificadores de 3.4 (sin texto), `sec:met_supervisados`. | Ninguna nueva (`sec:marco_vlm`, solo \ref) |
| P2 | Mini-VLM es Phi-3.5-vision-instruct, con codificador CLIP ViT-L/14 a 336 px, proyección MLP y LLM Phi-3.5-mini (32 capas, 3 072 dimensiones). Unos 4 150 millones de parámetros. Motivo: pesos abiertos y LoRA en una GPU de consumo. | `hf://models/microsoft/Phi-3.5-vision-instruct/config.json` (`img_processor.model_name` = `openai/clip-vit-large-patch14-336`; `hidden_size` 3072; `num_hidden_layers` 32; `embd_layer.projection_cls` = mlp). Ficha del modelo: 4146.6M parámetros; con el adaptador v3 el log cuenta 4 178 078 720 (4146.6M + 31.5M entrenables; job Mendieta 1179985). `src/models/mini_vlm.py` (MODEL_NAME; docstring, ViT-L/14). | `abdin2024phi3` (Phi-3 report, arXiv:2404.14219) |
| P3 | LLaVA-Med v1.5 con Mistral-7B: CLIP ViT-L/14, proyección, Mistral-7B; entrenado con figuras y leyendas de la literatura biomédica; unos 7 mil millones de parámetros de lenguaje, el más pesado de los dos. Motivo: es el VLM biomédico con el que se contrasta el de propósito general. | `src/models/llava_med.py` (MODEL_NAME = `chaoyinshe/llava-med-v1.5-mistral-7b-hf`; docstring: CLIP ViT-L/14, MLP, Mistral-7B). Entrenamiento biomédico: Cap. 2, `sec:marco_vlm_generativos` (no verificado en esta ficha). | `li2023llavamed`. La atribución de v1.5 Mistral queda en Preguntas abiertas (4). |
| P4 | Párrafo-puente: ninguno de los dos devuelve siempre una etiqueta válida cuando se le pide un diagnóstico; hace falta fijar cómo se obtiene una clase con cada uno. | — | Ninguna |
| P5 | Enumeración de las cuatro estrategias (detalle abajo). Todas usan el mismo conjunto de siete categorías. La Figura~\ref{fig:met_zsvslik} contrasta las dos primeras; los prompts completos van al Apéndice~\ref{ap:prompts}. | Ver «Detalle de P5 y P9» más abajo. | `hu2021lora` (estrategia 4); `shen2025skincare` (SkinCaRe, sobre el que se ajusta el checkpoint) |
| P6 | Likelihood scoring: para cada imagen y cada clase se toman los tres sinónimos, se calcula el log-probabilidad de cada uno como continuación del prompt dada la imagen, se divide por su cantidad de tokens y se queda con el máximo; se promedia sobre los cuatro prompts y se elige la clase de mayor puntaje (`eq:met_likelihood`). Nunca produce «desconocido». La respuesta generada, en cambio, depende de la decodificación y puede no contener ninguna etiqueta. | `src/evaluation/vlm_scoring.py`: `PROMPT_TEMPLATES` (O1, O2, C1, C2), `CLASS_SYNONYMS` (3 por clase), `score_class` (máximo por sinónimo, normalización por `n_tok`), `score_image` (promedio de los 4 prompts; `pred_ensemble`). Fórmula en el `.tex`: $s_c = \frac{1}{\lvert\mathcal{P}\rvert}\sum_{p} \max_{s \in S_c} \frac{\log P(s \mid p, x)}{\lvert s\rvert}$, $\hat{c} = \arg\max_c s_c$. | `eq:marco_lm` (Cap. 2, solo \ref) |
| P7 | Control: el scoring se repite con cada imagen reemplazada por una gris neutra de 224 × 224 píxeles (RGB 128). Si el modelo sigue dando la misma distribución de puntajes, el prompt y no la imagen guía la respuesta. Se describe el procedimiento; los resultados van a los capítulos de resultados. | `scripts/train_vlm_classify.py` líneas 147 a 150 (`blank_image`), sufijo `_noimage` (línea 265). `docs/ideas/prior_lenguaje_noimage_plan_20260823.md` (criterio de interpretación, § «Criterios de éxito»). | Ninguna nueva |
| P8 | DermLIP: VL contrastivo al estilo de CLIP con ViT-B/16 y codificador de texto, preentrenado sobre los pares dermatológicos de Derm1M (`sec:met_datasets`). No genera texto; da un embedding de 512 dimensiones por imagen. Se incluye para distinguir dos explicaciones de un mal resultado de los VLM generales: que les falte especialización en dermatología, o que generar texto sea una mala forma de clasificar. | `src/models/dermlip.py` (línea 25, `hf-hub:redlessone/DermLIP_ViT-B-16`; línea 64, `open_clip.create_model_and_transforms`). `docs/resul/embeddings_resul_20260707.md` (dim 512). `docs/ideas/dermlip_clasificacion_plan_20260604.md` §1 y §2 (motivación; no genera). | `yan2025derm1miccv`; CLIP solo \ref (Cap. 2) |
| P9 | Cuatro modos (lista, detalle abajo) sobre el embedding congelado y normalizado. Los valores de las cabezas son fijos: no hubo búsqueda de $C$ ni de $k$ sobre validación. Con cuatro cabezas sobre la misma representación, un resultado mezcla el efecto de la representación y el de la cabeza. | `src/models/dermlip.py` líneas 28 a 35 (`DEFAULT_TEMPLATES`), 98 a 130 (`zero_shot_logits`, `embed_images`). `scripts/eval_dermlip_linearprobe.py` líneas 88 y 89. `scripts/dermlip_split_eval.py` líneas 100, 113 a 115. `scripts/embeddings_classical.py` líneas 77 a 82. | `eq:marco_cos`, `eq:marco_knn`, `eq:marco_vecinos` (Cap. 2, solo \ref) |
| P10 | Control: cabezas clásicas equivalentes (SVM-RBF con $C = 10$, regresión logística y random forest de 300 árboles, todas con pesos balanceados) sobre el embedding de Swin congelado, preentrenado en ImageNet, sin ajuste en HAM10000. Si la diferencia entre las dos representaciones es la misma con cada cabeza, el efecto es de la representación. | `scripts/embeddings_classical.py` líneas 27 a 31 y 77 a 82 (RF con 300 árboles, `class_weight` balanced). Swin-ImageNet: 768 dimensiones (`docs/resul/embeddings_resul_20260707.md`). Versión sobre la partición por lesión: `outputs/results/embeddings/embeddings_classical_les.json` (`docs/resul/split_lesion_resul_20260926.md` §6). | `liu2021swin` (solo como backbone) |
| P11 | Partición. Las cabezas y el control se ajustan sobre el entrenamiento de la partición por lesión (`sec:met_particiones`). El zero-shot de DermLIP no depende de la partición (no se ajusta con HAM10000) y lo mismo vale para los VLM generativos, cuyo ajuste usa SkinCaRe (`sec:met_generacion`). Todos se evalúan sobre la misma prueba que los supervisados. Cierre: los generativos, además de clasificar, pueden redactar. | `docs/resul/split_lesion_resul_20260926.md` §2 (partición disjunta, sin solapamiento), §6 (DermLIP ZS sin efecto de la partición; cabezas re-ajustadas). Decisión 6 de `fichas/03-materiales-metodos/00-capitulo.md` (los VLM generales no se ajustaron sobre HAM10000). | Ninguna nueva |

## Detalle de P5 y P9 (listas)

**P5, las cuatro estrategias** (`enumerate` en el `.tex`; la 1 y la 2 con el nombre en cursiva, la 3 y la 4 en texto llano):

1. **Zero-shot por generación.** Prompt `CLASSIFICATION_PROMPT` (Apéndice B). Decodificación voraz: `do_sample=False` en `src/models/mini_vlm.py` (línea 255) y en `src/models/llava_med.py` (línea 194). Parseo: coincidencia exacta con una etiqueta o la primera etiqueta que aparece como palabra completa (`parse_vlm_response`, `scripts/train_vlm_classify.py`). Sin etiqueta válida, la respuesta cuenta como «desconocido» (`UNKNOWN`).
2. **Likelihood scoring.** Ver P6 y `eq:met_likelihood`. Prompts: O1, O2, C1 y C2 (texto en Apéndice B). Prefijo de chat distinto por modelo (`_build_prefix` en `vlm_scoring.py`).
3. **Razonamiento paso a paso (CoT).** Prompt `COT_PROMPT`: describir los rasgos de la lesión, listar diagnósticos diferenciales y concluir con una línea «Final diagnosis:» seguida de la clase. Si la línea falta, se usa el parseo de la estrategia 1; sin etiqueta válida, «desconocido». La respuesta se limita a 32 tokens nuevos en la estrategia 1 y a 200 en esta (`--max_new_tokens`; `max(args.max_new_tokens, 200)` en `train_vlm_classify.py`).
4. **Ajuste fino con LoRA.** El checkpoint de la etapa 2 de generación (Sección~\ref{sec:met_generacion}), ajustado con LoRA sobre SkinCaRe y evaluado por verosimilitud o por CoT. No se ajustó sobre HAM10000. La configuración de LoRA ya no se repite acá: está en la Tabla~\ref{tab:met_lora} de 3.6.

**P9, los cuatro modos de DermLIP** (`enumerate` en el `.tex`):

1. **Zero-shot.** Similitud coseno entre el embedding de la imagen y el de cada clase, con el texto de cada clase promediado sobre las cuatro plantillas de `DEFAULT_TEMPLATES` (el `.tex` cita «A dermatoscopic image of *clase*» como ejemplo). Argmax, sin «desconocido».
2. **Linear probe.** Regresión logística sobre el embedding normalizado congelado; `C = 1.0`, `class_weight = balanced`.
3. **Vecinos más cercanos (kNN).** `k = 3`, similitud coseno, voto mayoritario; si hay empate, gana el vecino más similar (`dermlip_split_eval.py` línea 100; mismo criterio que `build_rag_index.py`).
4. **SVM con núcleo RBF.** `SVC(C = 10, kernel = rbf, class_weight = balanced)` sobre embeddings estandarizados (`embeddings_classical.py` línea 80; `dermlip_split_eval.py` línea 115).

Los valores de las cabezas son fijos en el código y el `.tex` lo declara («no hubo búsqueda de $C$ ni de $k$ sobre validación»). No se verificó contra `ejecuciones.md` (ver Preguntas abiertas 12).

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Zero-shot frente a likelihood (`fig:met_zsvslik`) | (a) Zero-shot: imagen y prompt → el VLM genera texto → parseo → clase o «desconocido». (b) Likelihood: imagen y prompt → el VLM puntúa el nombre de cada clase → argmax, sin «desconocido». Sin cifras. | `Docs/experimentacion/experimentacion.tex` líneas 69 a 91 (`fig:zsvslik`), redibujada con los estilos de `Configurations/13-Figuras.sty`. Archivo: `Figures/Capitulos/03-Materiales-Metodos/zsvslik.tex`. Se cita en P5. | hecha |

No se incluye la figura `fig:tipos` (tres familias de modelos) de `experimentacion.tex`: la distinción entre familias ya la hacen 2.3 y P1. Tampoco hay tabla de estrategias: son alternativas paralelas y van en lista (guía §3).

## Prosa ya escrita que se conserva

Nada de versiones anteriores al andamiaje: la sección se escribió desde cero el 11/10/2026 y se reordenó el 18/10/2026.

## Lo que va al apéndice

- **Apéndice B (`ap:prompts`, `Chapters/Apendices/B-Prompts.tex`):** `CLASSIFICATION_PROMPT`; O1, O2, C1 y C2 completos; `COT_PROMPT`; los prefijos de chat de LLaVA-Med (`[INST] <image>` ... `[/INST]`) y de Mini-VLM (plantilla de chat con `<|image_1|>`); `CLASS_SYNONYMS` (21 términos: 7 clases por 3 sinónimos); `DEFAULT_TEMPLATES` de DermLIP.
- **Apéndice A (`ap:hiperparametros`):** no hay grillas de búsqueda para estas cabezas. Los valores fijos se citan en el cuerpo (P9, P10).

## Lo que NO va en esta sección (y dónde está)

- **Cualquier desempeño** de las cuatro estrategias, de DermLIP en sus cuatro modos, del control sin imagen o del control con Swin-ImageNet: Cap. 4. Incluye el colapso en likelihood y la tasa de «desconocido» en generación.
- **La historia de las iteraciones** (v1 a v3 de la clasificación con VLM, los planes T1 a T5, el re-diagnóstico del colapso y la hipótesis de dominio clínico): Cap. 4 o Apéndice C (`C-Resultados-Complementarios.tex`), según el autor.
- **Saliencia de DermLIP:** no se presenta como evidencia de que el modelo mire la lesión; en `split_lesion_resul_20260926.md` §7 es un artefacto de la grilla de parches. Va a 3.8 (`sec:met_complementarios`, el label que conserva 08-evaluacion-escenarios.tex) como limitación, si se incluye.
- **Explicación de CLIP, LLM, LoRA, decodificación voraz y clasificación por verosimilitud:** Cap. 2, solo \ref.
- **Configuración de LoRA y ajuste en dos etapas:** 3.6 (`sec:met_generacion`, Tabla~\ref{tab:met_lora}).
- **Adaptador LoRA de clasificación entrenado con etiquetas de HAM10000** (plan `vlm_clasificacion_v2_plan_20260501.md`, T3): no figura en esta ficha. Ver Preguntas abiertas 6.
- **Descriptores ABCDE:** `ABCDE_FEATURES` se define en `vlm_scoring.py`, pero no se usa en `COT_PROMPT` (búsqueda en `src/` y `scripts/`). No se describen como parte del CoT.
- **Mini-VLM como «médico»:** ver Preguntas abiertas 1.

## Preguntas abiertas para el autor

1. **Terminología.** La guía §4 fija «VLM médicos de propósito general» para los modelos. Mini-VLM (Phi-3.5-vision) es un VLM general, no médico. El `.tex` dice en P1 «dos generativos de propósito general, uno entrenado con datos generales y otro con datos biomédicos», y en P3 llama a LLaVA-Med «VLM biomédico» frente al «de propósito general»: la fórmula de P1 llama «de propósito general» a los dos. **Abierta**: unificar (propuesta: «VLM de propósito general (Mini-VLM)» y «VLM biomédico (LLaVA-Med)») y decidir si se cambia la fila de la tabla de términos de la guía.
2. **Codificador de Mini-VLM (resuelta en el `.tex`).** El texto usa CLIP ViT-L/14 a 336 px, el valor verificado en el `config.json` del checkpoint. Siguen en contradicción fuera del Cap. 3: `Codigo/configs/models/mini_vlm.yaml` (CLIP ViT-B/16 + Phi-3-mini), los encabezados de `slurm/*/vlm_classify_mini*.sh` y `slurm/*/train_*mini*.sh`, `Codigo/docs/resul/INFORME_TECNICO.md` §3.4 y `Docs/experimentacion/experimentacion.tex`. Los archivos de código no se tocaron.
3. **Parámetros de Mini-VLM (resuelta en el `.tex`, falta unificar el resto).** El `.tex` dice «unos 4 150 millones»; la ficha del modelo da 4146.6M y el log del job 1179985 da 4 178 078 720 con el adaptador v3. Cap. 2 (`04-modelos-lenguaje.tex`, línea 35) y `measure_cost.py` / `costo_resul_20260705.md` dicen 4200. **Abierta** solo la unificación en Cap. 2 y en el resto.
4. **Atribución de LLaVA-Med v1.5 con Mistral.** Cap. 2 (`05-vlm.tex`) atribuye la versión 1.5 con Mistral a `zeng2025mmskin`. El `.tex` cita `li2023llavamed`. El checkpoint usado (`chaoyinshe/llava-med-v1.5-mistral-7b-hf`) es una conversión a HF. `configs/models/llava_med.yaml` dice «Llama-2-7b-chat» (desactualizado). **Abierta** para el Cap. 2; si hace falta la fuente del checkpoint, se propone en `refs_pendientes.md`.
5. **Checkpoint del ajuste fino (parcialmente resuelta).** El `.tex` dice «el checkpoint de la etapa 2 de generación» sin versión, y 3.6 describe la configuración de v2 para LLaVA-Med. Para Mini-VLM existe el reentrenamiento v3 (LoRA en `qkv_proj` del modelo de lenguaje y `q_proj`/`v_proj` del codificador visual; 31 457 280 entrenables); el paso de los Caps. 4 y 5 a v3 queda en sus fichas. Confirmar que las corridas de clasificación con ajuste fino de Mini-VLM que se reporten usen v3.
6. **Adaptador LoRA de clasificación (T3).** La ficha asume que nunca se entrenó un LoRA sobre etiquetas HAM10000 (la estrategia 4 usa el checkpoint de SkinCaRe). Hay que confirmarlo con `ejecuciones.md`. Si se ejecutó, va a 3.5 como estrategia propia.
7. **Dónde se define el kNN (resuelta).** Se define acá, con k = 3, y 3.7 lo remite (`07-pipeline.tex` lo retoma con `\ref{sec:met_clasif_vlm}`).
8. **Control sin imagen (resuelta).** Queda en 3.5.2 como parte del método de likelihood (P7).
9. **Lentigo solar entre los sinónimos de BKL.** `CLASS_SYNONYMS["BKL"]` incluye «solar lentigo». Es una lesión pigmentada benigna, pero no una queratosis. Conviene que lo revise la rúbrica clínica (`docs/rubrica_validacion_clinica.md`) antes de escribirlo en el apéndice. **Abierta.**
10. **Referencia de Derm1M.** El `.bib` tiene `yan2025derm1m` (arXiv) y `yan2025derm1miccv` (ICCV) para el mismo trabajo. El `.tex` cita `yan2025derm1miccv`. **Abierta**: elegir una sola entrada. No se edita el `.bib` en esta tarea.
11. **Referencia de Phi-3.5-vision.** `abdin2024phi3` es el reporte técnico de Phi-3. No hay entrada para la ficha del modelo Phi-3.5-vision. **Abierta**: ¿se propone en `refs_pendientes.md`?
12. **Barrido de hiperparámetros de las cabezas (resuelta en el `.tex`, a verificar).** El `.tex` declara que no hubo búsqueda de $C$ ni de $k$ sobre validación. En el código los valores son fijos, pero no se contrastó con `ejecuciones.md`.
13. **Clave de cita para la figura de `experimentacion.tex` (obsoleta tras la revisión del 18/10).** La figura redibujada (`zsvslik.tex`) no contiene `\cite`; no queda la clave `li2024llavamed`.
14. **Mini-VLM en clasificación.** `vlm_clasificacion_resul_v2` documenta batch de tamaño 1 para Mini-VLM, y `num_crops` por defecto (4) en clasificación. No se verificó que se haya fijado otro valor. Va al apéndice si se describe. **Abierta.**

## Decisiones tomadas por cuenta propia

- **D1. Subsecciones.** Tres subsecciones: 3.5.1 (generativos), 3.5.2 (cuatro estrategias), 3.5.3 (DermLIP). Se mantiene tras la revisión del 18/10.
- **D2. SkinVL sale de 3.5** y va a 3.6, como indica la tabla de secciones de la ficha del capítulo (D1 del andamiaje).
- **D3. Sin `fig:tipos`.** La distinción de familias la hacen 2.3 y P1. Si el autor quiere la figura aquí, se agrega como figura de contexto.
- **D4. Estrategias en lista, no en tabla** (guía §3, «Alternativas paralelas en lista»). Sin tabla resumen.
- **D5. Fórmula propia del scoring** (`eq:met_likelihood`). La fórmula de la probabilidad está en Cap. 2 (`eq:marco_lm`). La forma exacta del ensamble (máximo sobre sinónimos, promedio sobre prompts) es propia del trabajo y se define acá (guía §3, «Conceptos, fórmulas y notación»).
- **D6. Motivos desde los objetivos** (guía §3). Mini-VLM y LLaVA-Med se incluyen porque el objetivo de ejecutar todo en una GPU de consumo exige LoRA, y el contraste biomédico frente a propósito general es parte de PI1. La revisión del 18/10 sumó el motivo de DermLIP (P8: separar falta de especialización de mala forma de clasificar). Confirmar.
- **D7. Ningún desempeño.** La sección describe datos y configuración.
- **D8. Control sin imagen y control con Swin-ImageNet** se describen como procedimiento, con el criterio de interpretación del plan. Los resultados van al Cap. 4.
- **D9. Partición declarada en P11**, como pide la ficha del capítulo (decisión 6), pero sin repetir tamaños (R3, revisión del 18/10).
- **D10. Cita de Phi-3.5-vision.** Se cita `abdin2024phi3` para Mini-VLM. No queda `\pendiente` por cita.
- **D11. P11 sin «la fuga solo podría favorecerlos».** Los VLM generativos no se ajustaron sobre *HAM10000*. Se escribe la versión vigente: las cabezas de DermLIP y el control se reajustan sobre la partición por lesión, la zero-shot no depende de la partición y el checkpoint se entrenó con *SkinCaRe*.
- **D12. Terminología de la pregunta 1** aplicada en P2 y P3 (Mini-VLM «de propósito general», LLaVA-Med «biomédico»), con la fórmula de P1 aún sin unificar. La fila de la guía §4 queda para el autor.
- **D13. (obsoleta tras la revisión del 18/10)** Cifras solo de datos: 776 imágenes descartadas, 6 447 / 1 289 / 1 503. El `.tex` ya no repite los tamaños de la partición (R3).
- **D14. (resuelta)** Los pendientes que quedaban en el `.tex` están cerrados: las longitudes máximas (32 y 200 tokens) figuran en la estrategia 3; ya no se menciona la cantidad de pares de *Derm1M*; la búsqueda de $C$ y $k$ se declara inexistente (pregunta 12, a verificar). No quedan `\pendiente` en el archivo.
- **D15. Acrónimos.** `Matter/05-Acronyms.tex` define `knn`; el `.tex` usa `\gls{vlm}`, `\gls{clip}`, `\gls{llm}`, `\gls{lora}`, `\gls{cot}` y `\gls{knn}`, y escribe en texto llano SVM, RBF, MLP y GPU. Propuestos y sin agregar: `\acronimo{svm}{SVM}{máquina de vectores de soporte}{Support Vector Machine}`, `\acronimo{rbf}{RBF}{de base radial}{Radial Basis Function}`, `\acronimo{mlp}{MLP}{perceptrón multicapa}{Multilayer Perceptron}`, `\acronimo{gpu}{GPU}{unidad de procesamiento gráfico}{Graphics Processing Unit}`.

## Números que no pude verificar

- Cifra de Derm1M: ya no figura en el `.tex`.
- «Entrenado con figuras y leyendas biomédicas» (LLaVA-Med) y «unos 7 mil millones de parámetros de lenguaje»: vienen del Cap. 2 y de la arquitectura Mistral-7B, no verificados aquí.
- Que no hubo búsqueda de $C$ ni de $k$ (pregunta 12).
- Extensión de 3.5 páginas: estimación del encabezado del `.tex`.

## Quitado en la revisión del 18/10/2026

Lo que la ficha anterior fijaba y el `.tex` actual ya no dice. Se conserva acá para no perder la fuente.

- Tamaños de la partición (776 descartadas, 6 447 de entrenamiento, 1 289 de validación, 1 503 de test): R3, ya están en 3.2 (`sec:met_particiones`). Fuente: `split_lesion_resul_20260926.md` §2.
- Referencia explícita a PI1 y OE con `\ref{sec:met_tareas}` en P1: el `.tex` dice «la primera pregunta de investigación» sin remitir; el vínculo con 3.1 lo da la introducción del capítulo (R3).
- Estimaciones de VRAM (8 GB Mini-VLM; 14 GB con LoRA y 10 GB con QLoRA para LLaVA-Med) y la expresión «4.1 mil millones»: R1 (son estimaciones de `configs/models/*.yaml`, no mediciones); el `.tex` da «unos 4 150 millones» y omite la VRAM.
- Configuración de LoRA de la estrategia de ajuste fino (r = 64, α = 128, dropout 0.05, siete módulos lineales, de `phase2_generation.yaml`): R3 y obsoleta, la configuración vigente está en la Tabla~\ref{tab:met_lora} de 3.6 y el YAML no lo lee ningún script. También sale el nombre del script (`train_vlm_classify.py --checkpoint stage2_*_v2`).
- Texto de los prompts O1 y O2 y qué listan C1 y C2: R3/R4, van solo al Apéndice B.
- Detalles de código del linear probe y del SVM (`max_iter = 2000`, que el linear probe no se estandariza y que el `StandardScaler` se aplica solo al SVM en `dermlip_split_eval.py`): R1 (detalle del equipo); el `.tex` conserva `C`, pesos balanceados y «estandarizados» para el SVM.
- Las cuatro plantillas del zero-shot de DermLIP en texto («This is a skin image of {c}», «A clinical photograph of {c}», «An image showing {c}»): el `.tex` cita una sola como ejemplo; el resto va al Apéndice B.
- Nombre del checkpoint de DermLIP (`redlessone/DermLIP_ViT-B-16`), carga con open_clip y cifra de Derm1M («alrededor de un millón de pares»): R1/R3; el `.tex` dice «los pares dermatológicos de *Derm1M*» y remite a `sec:met_datasets`.
- Párrafo P10 anterior con la declaración de qué quedó sobre la partición anterior: obsoleto tras D11 y la corrección del 11/10 (los VLM generales no se ajustaron sobre HAM10000); P11 es la versión corta (R2, R3).
- Tabla de la ficha anterior que mencionaba «Decisión 6» como fuente de P10: se conserva solo en P11.

## Agregado del 24/10/2026: control con fotografías clínicas

Aprobado por el autor al planificar el Cap. 4: el resultado de `vlm_domain_gap_clinica_resul_20260604.md` (si los
VLM generativos clasifican mejor fotografías clínicas que dermatoscópicas) entra a 4.3 del Cap. 4, y por eso su
procedimiento tiene que estar acá.

- **P nuevo (segundo control de `sec:met_vlm_procedimiento`):** verosimilitud sin ajuste sobre las 624 imágenes de
  *SkinCAP* cuyo diagnóstico corresponde a una de las siete clases (`SKINCAP_TO_HAM` en `src/data/skincare.py`), sin
  partición porque los modelos no se ajustan. Criterio: si clasifican mejor las fotografías clínicas, la dificultad
  está en la modalidad. Sin resultados.
- El control con Swin-ImageNet pasa a ser el tercero; el párrafo de datos exceptúa este control de «la misma prueba».
- `tab:met_experimentos` (3.8): la fila de clasificación con VLM agrega *SkinCAP* como control en «Datos».

## Agregado del 24/10/2026 (revisión del Cap. 4)

El segundo control suma una oración: DermLIP sin ajuste clasifica las mismas 624 fotografías de *SkinCAP* como
contraste de un modelo especializado. Lo pidió el autor al revisar 4.3, que informa ese resultado.
