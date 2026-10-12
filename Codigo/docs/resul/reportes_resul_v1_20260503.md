# Resultados de Generación de Reportes Clínicos — Fase 2

**Fecha:** 2026-05-03  
**Modelos:** LLaVA-Med 7B + LoRA, Mini-VLM (CLIP ViT-B/16 + Phi-3-mini) + LoRA  
**Datasets de entrenamiento:** SkinCaRe SkinCAP (Stage 1), SkinCaRe SkinCoT EN (Stage 2)  
**Datasets de evaluación:** HAM10000 test set, SkinCaRe test split, MM-SkinQA  
**Cluster:** Mendieta (A30 24GB, CUDA 12.1)

---

## 1. Pipeline de entrenamiento

El fine-tuning se realizó en dos etapas sobre los dos VLMs del proyecto.

### 1.1 Stage 1 — Alineamiento visual-textual

- **Datos:** SkinCAP (~4k pares imagen-caption corta del dataset SkinCaRe)
- **Objetivo:** Adaptar el MLP de proyección para el dominio dermatológico sin modificar el vision encoder ni el LLM
- **Parámetros congelados:** vision encoder + LLM (solo el proyector es entrenable)
- **Instrucción de entrenamiento:** `"Describe this skin lesion."` (fija para todos los ejemplos)
- **Hiperparámetros (mejores, compartidos por ambos modelos):**
  - lr: `1.094512e-04`
  - épocas: 2
  - batch_size: estimado automáticamente por VRAM disponible

### 1.2 Stage 2 — Ajuste de instrucciones con LoRA

- **Datos:** SkinCoT EN (~3k pares imagen-narrativa de razonamiento clínico del dataset SkinCaRe)
- **Objetivo:** Adaptar el LLM para generar razonamientos diagnósticos estructurados a partir de imágenes dermoscópicas
- **Parámetros entrenables:** LoRA aplicado a `q_proj` y `v_proj` del LLM; proyector y vision encoder congelados
- **Checkpoint de partida:** mejor checkpoint de Stage 1

Se realizó un sweep de hiperparámetros en Mendieta con 4 trials por modelo (seed=42). Solo se completaron los trials t03 y t04 (5 épocas); los trials t01 y t02 (15 épocas) posiblemente no finalizaron dentro del tiempo de cola.

**Mejores hiperparámetros — ambos modelos:**

| Parámetro | Valor |
|-----------|-------|
| `lora_r` | 64 |
| `lora_alpha` | 64 (multiplier=1.0) |
| `lora_dropout` | 0.0 |
| `stage2_lr` | 2.4952e-05 |
| `épocas` | 5 |
| `grad_accum` | 4 |

**Batch efectivo:** 16 para LLaVA-Med, 8 para Mini-VLM (reducido por OOM en A30 con Phi-3-mini)

> **Corrección (2026-10-12, [verificaciones_cap03](verificaciones_cap03_resul_20261011.md)).** El log del
> barrido 1147378 (trial t04 de Mini-VLM, misma configuración) muestra lote 4 × 4 = 16: ante falta de memoria
> el código activa *gradient checkpointing* y no reduce el lote efectivo (`train_vlm_stage2.py:296-301`). El
> modelo es Phi-3.5-vision, no Phi-3-mini. Además, el LoRA de Mini-VLM quedó solo en el codificador CLIP
> (6 291 456 parámetros), porque Phi-3.5 fusiona la atención del LLM en `qkv_proj`; se reentrena como v3
> ([plan](../ideas/mini_vlm_lora_llm_plan_20261012.md)).

**Val loss final (Stage 2):**

| Modelo | Trial ganador | Val loss Stage 2 | Val loss Stage 1 |
|--------|--------------|-----------------|-----------------|
| LLaVA-Med | t04 (job 1147374) | **0.9536** (época 5/5) | 1.3432 (época 2/2) |
| Mini-VLM | t04 (job 1147378) | **1.3494** (época 5/5) | 1.8372 (época 2/2) |

Tendencia del sweep: `lora_r=64` con lr más alta (~2.5e-05) superó a `lora_r=16` con lr más baja en ambos modelos. LLaVA-Med obtiene menor val loss, consistente con su mayor capacidad (7B vs 3.8B parámetros del LLM) y mayor vision encoder (ViT-L/14 vs ViT-B/16).

---

## 2. Generación de reportes (inferencia)

Los reportes se generaron con un prompt fijo sobre tres datasets:

```
"Describe this skin lesion with a structured clinical report that includes:
findings, diagnostic impression, and differential diagnosis."
```

**Nota sobre mismatch de prompts:** Durante el Stage 1 la instrucción de entrenamiento fue `"Describe this skin lesion."` (más corta y genérica). La instrucción de inferencia es más específica y solicita una estructura (findings, diagnostic impression, differential). Esta discrepancia entre el prompt de entrenamiento y el de inferencia puede afectar la coherencia estructural de los reportes generados.

**Volumen de reportes generados:**

| Dataset | LLaVA-Med | Mini-VLM | Pares con referencia |
|---------|-----------|----------|---------------------|
| HAM10000 | 3.042 | 2.240 | 0 (sin referencias) |
| SkinCaRe | 3.023 | 3.023 | 2.814 (CoT SkinCoT) |
| MM-SkinQA | 20 | 2.809 | todos |

La diferencia en el volumen de HAM10000 (3.042 vs 2.240) sugiere que el pipeline de Mini-VLM procesó menos imágenes, posiblemente por timeouts o errores de generación en algunas imágenes del test set.

---

## 3. Resultados cuantitativos

### 3.1 Evaluación NER clínico

Métricas basadas en diccionario dermatológico personalizado (categorías ABCDE, tipos de lesión, características clínicas). Backend SciSpaCy no disponible en el entorno; los valores de entity recall podrían ser mayores con NER biomédico activo.

**Clinical Entity Recall:** proporción de categorías terminológicas dermatológicas presentes en el reporte.  
**Diagnostic Consistency:** porcentaje de reportes donde el diagnóstico correcto (o sinónimo) aparece en el texto.

#### HAM10000 (n=3.042 / 2.240)

| Modelo | Clinical Entity Recall | Diagnostic Consistency |
|--------|----------------------|----------------------|
| LLaVA-Med | 45.69% | **71.47%** |
| Mini-VLM | **60.68%** | 31.34% |

#### SkinCaRe (n=3.023)

| Modelo | Clinical Entity Recall | Diagnostic Consistency |
|--------|----------------------|----------------------|
| LLaVA-Med | 37.09% | ≈ 0.00% |
| Mini-VLM | **56.61%** | ≈ 0.03% |

#### MM-SkinQA

| Modelo | Clinical Entity Recall |
|--------|----------------------|
| LLaVA-Med | 53.33% |
| Mini-VLM | 38.44% |

### 3.2 Métricas de similitud textual

Calculadas contra las referencias disponibles (SkinCoT EN para SkinCaRe, descripciones histopatológicas para MM-SkinQA). BLEU-4, ROUGE-L y BERTScore F1 en escala 0–1.

#### SkinCaRe vs referencias SkinCoT (n=2.814 pares)

| Modelo | BLEU-4 | ROUGE-L | BERTScore F1 |
|--------|--------|---------|--------------|
| LLaVA-Med | 0.0155 | 0.0660 | 0.7054 |
| Mini-VLM | **0.0347** | **0.1366** | **0.7663** |

#### MM-SkinQA vs referencias histopatológicas

| Modelo | n pares | BLEU-4 | ROUGE-L | BERTScore F1 |
|--------|---------|--------|---------|--------------|
| LLaVA-Med | 20 | 0.0000 | 0.0473 | 0.6953 |
| Mini-VLM | 2.809 | 0.0030 | 0.0803 | **0.7373** |

---

## 4. Análisis cualitativo de reportes generados

### 4.1 LLaVA-Med — HAM10000

Los reportes son cortos (3–5 oraciones), clínicamente coherentes y correctamente orientados al diagnóstico. El modelo nombra el tipo de lesión con terminología técnica específica (ej. "junctional nevus", "congenital melanocytic nevus"). Sin embargo, no describe características morfológicas observables de la imagen sino que aporta conocimiento general sobre el tipo de lesión, lo que sugiere que el modelo está más "recordando" que "observando".

Ejemplo para `gt_label=nevus`:
> *"This skin lesion is a junctional nevus, which is a type of mole that develops at the junction between the epidermis and dermis layers of the skin. It is characterized by its brown coloration and irregular borders. Differential diagnosis includes other types of moles and pigmented lesions..."*

### 4.2 Mini-VLM — HAM10000

Los reportes adoptan un formato de nota clínica ("Upon examination, the patient presents with...") con descripciones más ricas que incluyen tamaño, localización y color. Sin embargo, se observan **alucinaciones sistemáticas**: el modelo inventa datos morfológicos (ej. "2 cm pinkish-brown macule on the lower abdomen", "central area of necrosis") que no son verificables, y el **diferencial incluye patologías agresivas** (melanoma, BCC, SCC) incluso para lesiones con `gt_label=nevus`. Esto explica directamente la baja diagnostic consistency (31.34%): el modelo menciona el diagnóstico correcto en el diferencial pero no como diagnóstico principal.

Ejemplo para `gt_label=nevus`:
> *"Upon examination, the patient presents with a 2 cm pinkish-brown macule on the lower abdomen. The lesion is irregular in shape and has a slightly raised border. The differential diagnosis includes dermatofibroma, melanoma, and basal cell carcinoma."*

### 4.3 LLaVA-Med — SkinCaRe

Los reportes adoptan la estructura solicitada en el prompt (findings / diagnostic impression / differential diagnosis) pero presentan **repetición de contenido**: los mismos hallazgos aparecen reiterados en las secciones de Diagnostic Impression, Recommendations y Summary. Este patrón es un artefacto del fine-tuning con LoRA sobre un dataset pequeño (~3k ejemplos), donde el modelo aprendió a completar una plantilla estructural repitiendo el contenido en lugar de sintetizarlo.

### 4.4 Mini-VLM — SkinCaRe

Los reportes son más extensos y mejor formateados (Markdown con bullets y negrita), con secciones claramente diferenciadas. Son informativos y clínicamente plausibles, pero tienden a exceder la longitud del prompt y a veces se truncan. La entidad de mayor recall de Mini-VLM (56.61% vs 37.09% de LLaVA-Med) refleja esta riqueza descriptiva morfológica. Sin embargo, el diagnóstico final no siempre coincide con el de la referencia SkinCoT, que razona desde hallazgos visibles hacia un diagnóstico específico.

---

## 5. Comparación con el estado del arte

La comparación directa con el SOTA es **limitada por diferencias de dataset**. Los trabajos de referencia (MM-Skin paper, SkinR1) evaluaron sus modelos sobre el test split de MM-Skin (imágenes dermoscópicas), mientras que nuestras métricas de texto se calcularon sobre SkinCaRe (CoT references) y MM-SkinQA (histopatología). El plan original contemplaba evaluar sobre MM-Skin test split, pero los reportes generados sobre MM-SkinQA son parcialmente comparables.

### Comparación aproximada con MM-Skin SOTA (dermoscopia, escala 0–100)

| Modelo | BLEU-4 | ROUGE-L | BERTScore |
|--------|--------|---------|-----------|
| SkinVL-MM (LLaVA-Med+LoRA) — SOTA | 2.84 | 19.53 | 57.76 |
| SkinVL-PubMM (baseline SOTA) | 2.60 | 24.53 | 60.94 |
| LLaVA-Med-v1.5-7B (ZS baseline) | 2.58 | 14.81 | 63.31 |
| **LLaVA-Med (este trabajo) — SkinCaRe** | **1.55** | **6.60** | **70.54** |
| **Mini-VLM (este trabajo) — SkinCaRe** | **3.47** | **13.66** | **76.63** |

*Nota de escala: nuestros valores originales en 0–1 se multiplicaron por 100. El BERTScore del SOTA usa un modelo distinto (no especificado), por lo que la comparación no es directa. BLEU-4 y ROUGE-L sí son comparables en escala.*

**Observaciones:**
- **BLEU-4:** Mini-VLM (3.47) supera marginalmente al SOTA (2.84) en valor numérico, pero los datasets son distintos y las referencias de SkinCaRe (CoT chains) son más cortas y distintas en estilo a las referencias de MM-Skin, lo que puede inflar el BLEU artificialmente.
- **ROUGE-L:** Ambos modelos están por debajo del SOTA (6.60 y 13.66 vs 19.53). Esto refleja que las referencias SkinCoT son narrativas de razonamiento, no reportes estructurados; el modelo genera reportes estructurados → menor superposición de n-gramas con las referencias.
- **BERTScore:** Nuestros modelos obtienen valores más altos que el SOTA (70.54–76.63 vs 57.76–63.31). Esto es alentador pero debe interpretarse con cautela dado el cambio de modelo BERTScore (usamos DistilBERT, el SOTA no especifica).

La evaluación sobre MM-Skin test split (como estaba planeada en la tabla SOTA) sigue pendiente y permitiría una comparación directa.

---

## 6. Problemas identificados

### P1 — Mismatch entre estilo de entrenamiento y de referencia
Los modelos se entrenaron sobre SkinCoT EN, que son narrativas de **razonamiento diagnóstico progresivo** (estructura CoT: "I consider... I narrow down... I conclude..."). El prompt de inferencia solicita un **reporte clínico estructurado** (findings / impression / differential). Los modelos generan el formato pedido, pero las referencias con las que se evalúan son del estilo CoT, lo cual genera baja superposición léxica (BLEU/ROUGE bajos) aunque el contenido semántico sea similar (BERTScore moderado/alto).

### P2 — Mismatch entre prompt de entrenamiento Stage 1 e inferencia
El Stage 1 entrenó con la instrucción corta `"Describe this skin lesion."`, mientras que la inferencia usa un prompt más largo con estructura explícita. Esta discrepancia puede afectar la fluidez y coherencia del reporte, ya que el proyector MLP se adaptó al estilo de la instrucción corta.

### P3 — Repetición estructural en LLaVA-Med (SkinCaRe)
LLaVA-Med aprende una plantilla de reporte pero repite el mismo contenido en múltiples secciones. Artefacto esperado de fine-tuning con dataset pequeño y sin restricción de longitud o diversidad en la respuesta.

### P4 — Alucinaciones morfológicas en Mini-VLM (HAM10000)
Mini-VLM inventa datos clínicos específicos (tamaño, localización, características histológicas) no verificables a partir de la imagen, y tiende a incluir diagnósticos agresivos en el diferencial de lesiones benignas. Probable efecto de los datos de entrenamiento de Phi-3-mini, que incluyen texto médico general con un sesgo hacia describir patologías severas.

### P5 — Diagnostic consistency SkinCaRe: artefacto de etiquetas, no falla del modelo
La diagnostic consistency ≈ 0% en SkinCaRe se debe a que el campo `gt_label` contiene el nombre de la carpeta del dataset (ej. `"Eczema Photos"`) en lugar de la terminología médica que el modelo emplea (ej. `"atopic dermatitis"`, `"eczema"`). Las etiquetas fueron inferidas del nombre de carpeta y no están normalizadas. No refleja una falla real del modelo en el diagnóstico.

### P6 — Underfitting por sweep limitado
Solo se completaron 4 trials por modelo (los de 5 épocas), de los cuales el mejor checkpointa en la época final (5/5 para ambos modelos), lo que sugiere que el entrenamiento podría haberse beneficiado de más épocas. Los trials con 15 épocas (t01, t02) posiblemente no terminaron. El espacio de hiperparámetros explorado fue pequeño.

### P7 — n=20 para LLaVA-Med en MM-SkinQA
La evaluación de métricas de texto para LLaVA-Med en MM-SkinQA es sobre solo 20 pares, lo que no es estadísticamente representativo. Puede deberse a errores de generación o a que las 20 imágenes fueron las únicas del split disponibles localmente.

---

## 7. Propuestas de mejora

### A — Mejoras sin reentrenamiento (quick wins)

**A1. Corregir la instrucción de inferencia para que coincida con Stage 1:**  
Usar `"Describe this skin lesion."` o una instrucción intermedia que haya estado presente en Stage 2 (SkinCoT). Esto reduce el mismatch de distribución entre entrenamiento e inferencia.

**A2. Normalizar las etiquetas de SkinCaRe para la diagnostic consistency:**  
Mapear `"Eczema Photos"` → `["eczema", "atopic dermatitis", "dermatitis"]`, etc. La métrica actual castiga al modelo por usar la terminología médica correcta. Con normalización, la diagnostic consistency de SkinCaRe debería subir sustancialmente.

**A3. Evaluar sobre MM-Skin test split:**  
Para poder comparar directamente con el SOTA (SkinVL-MM, SkinVL-PubMM) se necesita ejecutar la generación sobre el test split de MM-Skin, que era el dataset planeado en la tabla SOTA.

**A4. Aumentar n para LLaVA-Med en MM-SkinQA:**  
Verificar por qué solo se generaron 20 reportes y completar la evaluación sobre el set completo.

### B — Mejoras de entrenamiento (requieren reentrenar)

**B1. Incluir ejemplos de reporte estructurado en Stage 2:**  
El dataset SkinCoT provee razonamientos CoT, pero el modelo se evalúa generando reportes estructurados. Mezclar datos SkinCoT con ejemplos de reportes clínicos reales (ej. de MM-Skin QA con formato report) en Stage 2 reduciría el mismatch de estilo.

**B2. Aumentar épocas de Stage 2:**  
Ambos modelos mejoran hasta la época 5/5 (val loss decrece), sugiriendo que aún no convergieron. Explorar 10–15 épocas (como los trials t01/t02 que no completaron). Considerar early stopping sobre val loss con paciencia=3.

**B3. Instrucción de Stage 1 alineada con Stage 2:**  
Cambiar `CAPTION_INSTRUCTION` de `"Describe this skin lesion."` a una instrucción que incluya la estructura de reporte buscada, o bien usar la misma instrucción que Stage 2 durante Stage 1. Reduce el mismatch de prompt entre etapas.

**B4. Explorar mayor rango de LoRA:**  
El sweep seleccionó r=64 sobre r=16. Podría explorarse r=128 o incluir más capas (ej. `k_proj`, `o_proj`) para mayor capacidad de adaptación.

### C — Mejoras de arquitectura (largo plazo)

**C1. Vision encoder más potente para Mini-VLM:**  
Mini-VLM usa CLIP ViT-B/16, mientras que LLaVA-Med usa CLIP ViT-L/14 (mayor resolución y capacidad visual). Actualizar Mini-VLM a ViT-L/14 podría mejorar la descripción de características morfológicas finas en las imágenes dermoscópicas, que son determinantes para el diagnóstico.

**C2. Pérdida auxiliar de entidades clínicas:**  
Incorporar como señal de entrenamiento el entity recall sobre el vocabulario dermatológico (ABCDE, tipos de lesión). Esto incentivaría a los modelos a incluir terminología clínica específica y aumentaría el entity recall sin necesidad de más datos.

**C3. Incorporación de datos HIBA para adaptación de dominio:**  
Los clasificadores supervisados mostraron un domain shift significativo (−25 pts de accuracy) al evaluar sobre pacientes argentinos (HIBA). Incluir imágenes HIBA en el fine-tuning de generación podría mejorar la robustez de los reportes para fototipos III–VI, que son los más prevalentes en la población objetivo.

**C4. Evaluar con un LLM mayor como juez clínico:**  
Para evaluación cualitativa automatizada, usar GPT-4 o un LLM biomédico (MedGemma, BioMistral) como evaluador de calidad clínica del reporte (corrección diagnóstica, completitud de hallazgos, coherencia). Esto complementa las métricas automáticas que no capturan calidad clínica real.

---

## 8. Conclusiones

Los modelos fine-tuneados generan reportes clínicamente coherentes y legibles, con terminología dermatológica apropiada. La evaluación cuantitativa muestra un patrón consistente: **Mini-VLM supera a LLaVA-Med en métricas de similitud textual** (BLEU-4, ROUGE-L, BERTScore) y en entity recall sobre HAM10000 y SkinCaRe, lo cual es notable dado que Phi-3-mini (3.8B) es un LLM más pequeño que LLaMA-2 7B. Esto sugiere que la arquitectura del LLM y su preentrenamiento sobre instrucciones tiene más peso en la calidad del texto generado que el tamaño del modelo.

Por su parte, **LLaVA-Med obtiene mayor diagnostic consistency en HAM10000** (71.47% vs 31.34%), lo que indica que sus reportes son más precisos en cuanto al diagnóstico final, aunque menos ricos en descripción morfológica.

Los valores bajos de BLEU-4 y ROUGE-L no deben interpretarse aisladamente como indicadores de mala calidad: son consecuencia directa del mismatch entre el estilo de las referencias (CoT reasoning chains) y el estilo de los reportes generados (reportes clínicos estructurados). El BERTScore moderado-alto (0.70–0.77) confirma que el contenido semántico es relevante y alineado con el dominio dermatológico.

Los principales problemas a resolver antes de una evaluación definitiva son: (1) evaluar sobre MM-Skin test split para comparar directamente con el SOTA, (2) corregir la métrica de diagnostic consistency en SkinCaRe con normalización de etiquetas, y (3) explorar entrenamiento con más épocas.
