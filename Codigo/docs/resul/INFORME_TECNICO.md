# Informe Técnico — DermVLM

**Tesina de grado:** *Detección, diagnóstico y generación automática de reportes para lesiones de piel utilizando modelos de lenguajes de visión*

---

## Índice

1. [Introducción y Motivación](#1-introducción-y-motivación)
2. [Datasets Utilizados](#2-datasets-utilizados)
3. [Modelos Implementados](#3-modelos-implementados)
4. [Fase 1 — Clasificación de Lesiones](#4-fase-1--clasificación-de-lesiones)
5. [Fase 2 — Generación de Reportes Clínicos](#5-fase-2--generación-de-reportes-clínicos)
6. [Análisis e Interpretación de Resultados](#6-análisis-e-interpretación-de-resultados)
7. [Infraestructura y Reproducibilidad](#7-infraestructura-y-reproducibilidad)
8. [Arquitectura del Código](#8-arquitectura-del-código)
9. [Trabajo Futuro — Fase 3](#9-trabajo-futuro--fase-3)

---

## 1. Introducción y Motivación

### 1.1 Contexto del Problema

El melanoma y otras lesiones cutáneas malignas representan un problema de salud pública creciente. La detección temprana es crítica: el melanoma detectado en estadio I tiene una supervivencia a 5 años superior al 98%, que cae drásticamente al 23% en estadio IV. Sin embargo, el diagnóstico dermatológico requiere especialistas altamente entrenados, cuyo acceso es desigual tanto geográficamente como por nivel socioeconómico.

La dermoscopia digital ha permitido capturar imágenes de alta resolución de lesiones cutáneas, abriendo la puerta a sistemas de asistencia diagnóstica basados en inteligencia artificial. En los últimos años, los avances en *deep learning* han producido clasificadores con rendimiento comparable al de dermatólogos expertos en tareas de clasificación binaria (benigno/maligno). Sin embargo, la clasificación multiclase en contextos clínicos reales sigue siendo un desafío, y la generación de reportes clínicos estructurados es un área prácticamente inexplorada.

### 1.2 Objetivos de la Tesina

Este trabajo tiene tres objetivos principales:

1. **Comparar clasificadores tradicionales vs. VLMs** en la tarea de clasificación multiclase de lesiones cutáneas dermoscópicas. Se evalúan dos arquitecturas clásicas (DenseNet121 y ViT-B/16) contra dos modelos de lenguaje visual (*Vision-Language Models*, VLMs): LLaVA-Med y Mini-VLM (Phi-3.5-vision).

2. **Fine-tunear VLMs para generación de reportes clínicos** mediante un pipeline de dos etapas con LoRA, entrenando los modelos para producir reportes estructurados con hallazgos, impresión diagnóstica y diagnósticos diferenciales.

3. **Evaluar la calidad clínica de los reportes generados** a través de un framework de evaluación de tres niveles: métricas automáticas de texto, NER clínico sin referencia, y revisión manual.

### 1.3 Hipótesis de Trabajo

- Los clasificadores tradicionales (DenseNet, ViT) superarán a los VLMs en la tarea de clasificación zero-shot, ya que están diseñados explícitamente para ese fin.
- Los VLMs, una vez fine-tuneados, serán capaces de generar reportes clínicamente útiles que los clasificadores tradicionales no pueden producir.
- Existirá un trade-off entre el modelo más grande (LLaVA-Med) y el más liviano (Mini-VLM) en términos de calidad diagnóstica vs. cobertura terminológica.

---

## 2. Datasets Utilizados

### 2.1 HAM10000 — Human Against Machine with 10000 training images

**Uso:** Clasificación (Fase 1) + evaluación de reportes (Fase 2)

HAM10000 es el dataset de referencia para clasificación multiclase de lesiones dermoscópicas. Contiene 10.015 imágenes de dermoscopia de alta resolución anotadas por dermatólogos expertos, recopiladas en el contexto del desafío ISIC 2018.

**Clases y distribución:**

| Clase | Código | Descripción | N (total) | % |
|-------|--------|-------------|-----------|---|
| Nevus melanocítico | NV | Lunar benigno | ~6.705 | 66.9% |
| Melanoma | MEL | Cáncer de piel maligno | ~1.113 | 11.1% |
| Queratosis benigna | BKL | Queratosis seborreica, lentigo solar | ~1.099 | 11.0% |
| Carcinoma basocelular | BCC | Cáncer no-melanoma | ~514 | 5.1% |
| Queratosis actínica | AKIEC | Lesión precancerosa | ~327 | 3.3% |
| Dermatofibroma | DF | Tumor cutáneo benigno | ~115 | 1.1% |
| Lesiones vasculares | VASC | Angiomas, granulomas | ~142 | 1.4% |

El fuerte desbalance de clases (NV representa ~67% del total) es un desafío central del dataset. Para mitigarlo se utilizaron pesos de clase inversamente proporcionales a la frecuencia en la función de pérdida.

**Splits:** 70% entrenamiento / 15% validación / 15% test. El set de test (1.503 imágenes) coincide con el split del challenge ISIC 2018, garantizando comparabilidad con la literatura.

**Metadatos disponibles:** edad del paciente, sexo, localización anatómica, fuente del dataset (ViDIR, Rosendahl, HAM).

### 2.2 SkinCaRe — Skin Caption and Report Dataset

**Uso:** Entrenamiento de generación de reportes (Fase 2)

SkinCaRe es un dataset compuesto que combina dos fuentes:

- **SkinCAP** (~4.000 pares imagen-caption): imágenes dermoscópicas con descripciones breves en lenguaje natural. Utilizado en la Etapa 1 del pipeline de fine-tuning (alineación del proyector visual).
- **SkinCoT** (~3.041 pares adicionales): reportes más extensos con razonamiento clínico estructurado. Utilizado en conjunto con SkinCAP en la Etapa 2 (fine-tuning con LoRA).

El dataset completo (~7.041 pares) proporciona supervisión textual diversa: desde descripciones morfológicas breves hasta reportes clínicos detallados con diagnósticos diferenciales.

### 2.3 MM-Skin — Multimodal Skin Dataset

**Uso:** Evaluación de generación de reportes con métricas de referencia (Nivel 1)

MM-Skin contiene 11.002 imágenes con dos tipos de anotaciones:
- 11.090 pares imagen-caption (descripciones en lenguaje natural)
- 27.259 pares imagen-pregunta-respuesta (VQA, *Visual Question Answering*)

Permite evaluar la calidad de los reportes generados comparándolos contra referencias humanas mediante métricas automáticas (BLEU, ROUGE, BERTScore).

### 2.4 HIBA — Hospital Italiano de Buenos Aires Dataset

**Uso:** Análisis de sesgo por fototipo cutáneo (Fase 3, trabajo futuro)

HIBA contiene 1.616 imágenes dermoscópicas con metadatos de fototipo de Fitzpatrick (I-IV). Este dataset permite evaluar si los modelos exhiben sesgos diagnósticos según el tono de piel del paciente, una dimensión crítica de equidad en sistemas médicos de IA.

---

## 3. Modelos Implementados

Todos los modelos se instancian a través de `src/models/factory.py` usando el patrón Registry, lo que permite intercambiarlos mediante configuración YAML sin modificar código.

### 3.1 DenseNet121

**Arquitectura:** Red convolucional con conexiones densas (*Dense Connections*). Cada capa recibe como entrada las feature maps de todas las capas anteriores, favoreciendo la reutilización de características y el flujo de gradientes.

**Implementación:**
- Backbone: DenseNet121 pre-entrenado en ImageNet (1.000 clases)
- Head de clasificación: `Linear(1024, num_classes=7)` reemplaza la capa final
- Estrategia de fine-tuning: backbone inicialmente congelado, con posibilidad de descongelar capas progresivamente
- VRAM estimada: ~4-6 GB en entrenamiento

**Por qué DenseNet:** Es la arquitectura CNN de referencia en clasificación dermatológica, habiendo ganado el ISIC Challenge 2018. Sirve como baseline CNN sólido.

### 3.2 ViT-B/16 (Vision Transformer)

**Arquitectura:** Transformer aplicado a imágenes. La imagen de 224×224 se divide en patches de 16×16 píxeles (196 patches), que se proyectan como tokens y se procesan con atención multi-cabeza.

**Implementación:**
- Backbone: ViT-B/16 pre-entrenado en ImageNet-21k
- Head: `Linear(768, 7)` con dropout (p=0.1)
- Todos los parámetros son entrenables desde el inicio
- VRAM estimada: ~6-8 GB en entrenamiento

**Por qué ViT:** Representa el estado del arte en clasificación visual general, con capacidad de capturar dependencias globales en la imagen que las CNNs pueden perder.

### 3.3 LLaVA-Med

**Arquitectura:** Vision-Language Model para el dominio médico.
- **Encoder visual:** CLIP ViT-L/14 (entrena la representación visual)
- **Proyector:** MLP de dos capas que mapea embeddings visuales al espacio del LLM
- **LLM:** Mistral-7B con fine-tuning médico
- **Template de prompt:** `[INST] <image>\n{prompt} [/INST]`

**Optimizaciones de memoria:**
- Cuantización 4-bit NF4 (`BitsAndBytesConfig`) cuando VRAM < umbral
- `skip_modules` para cuantización: `model.multi_modal_projector` y `model.vision_tower` (el tower CLIP cuantizado genera NaN)
- Atención SDPA (PyTorch 2.0+) con fallback a `eager`
- Device map: `"cuda:0"` si VRAM suficiente, `"auto"` (con CPU offload) si no

**VRAM estimada:** ~14 GB (bf16) / ~5 GB (4-bit NF4)

### 3.4 Mini-VLM (Phi-3.5-vision)

**Arquitectura:** VLM compacto para entornos con VRAM limitada.
- **Encoder visual:** CLIP ViT-B/16 (más liviano que ViT-L/14)
- **LLM:** Phi-3-mini (3.8B parámetros, arquitectura Phi de Microsoft)
- **Template de prompt:** Formato de chat con `<|image_1|>\n{prompt}`

**Características técnicas:**
- Requiere `trust_remote_code=True` (modelo con código custom)
- Dynamic cache patching para compatibilidad con transformers ≥ 4.41.0
- Parámetro `num_crops` para controlar VRAM: menos crops = menor resolución pero menos memoria
- Procesamiento secuencial forzado (batch size = 1) por limitaciones de implementación

**VRAM estimada:** ~8 GB (bf16) / ~4-5 GB (4-bit NF4)

---

## 4. Fase 1 — Clasificación de Lesiones

### 4.1 Objetivo

Establecer un benchmark comparativo de rendimiento en clasificación multiclase de lesiones dermoscópicas entre:
- Clasificadores tradicionales entrenados supervisadamente (DenseNet121, ViT-B/16)
- VLMs usados en modo zero-shot (LLaVA-Med, Mini-VLM)
- Ambos VLMs con fine-tuning de clasificación directa

### 4.2 Entrenamiento de Clasificadores Tradicionales

**Script:** `scripts/train_classifier.py`

**Hiperparámetros:**

| Parámetro | DenseNet121 | ViT-B/16 |
|-----------|-------------|----------|
| Epochs | 30 | 30 |
| Learning rate | 1e-4 | 1e-4 |
| Batch size | 32 | 16 |
| Weight decay | 0.01 | 0.01 |
| Optimizer | AdamW | AdamW |
| Scheduler | CosineAnnealingLR | CosineAnnealingLR |
| Early stopping | patience=5, val_f1 | patience=5, val_f1 |
| Loss | CrossEntropyLoss (class weights) | CrossEntropyLoss (class weights) |

**Augmentaciones de entrenamiento** (`src/data/transforms.py`):
- Rotación aleatoria ±30°
- Flip horizontal aleatorio
- ColorJitter (brillo, contraste, saturación)
- Normalización ImageNet (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

**Validación/Test:** Solo resize a 224×224 + normalización ImageNet.

Los pesos de clase se calculan como la inversa de la frecuencia de cada clase, normalizados. Esto penaliza más los errores en clases minoritarias (DF, VASC, AKIEC), que son clínicamente relevantes.

### 4.3 Clasificación Zero-Shot con VLMs

**Script:** `scripts/train_vlm_classify.py`

Los VLMs se evaluaron en modo zero-shot: sin ningún entrenamiento adicional, se les pidió clasificar cada imagen en una de las 7 categorías HAM10000 mediante un prompt en lenguaje natural.

**Prompt utilizado:**
```
Classify this dermoscopic image into one of the following categories:
MEL, NV, BCC, AKIEC, BKL, DF, VASC.
Respond with only the category label.
```

La respuesta del modelo se parseó buscando coincidencia exacta con los 7 códigos. Respuestas que no coincidían con ningún código se marcaban como "unknown" (en la práctica: 0 casos — ambos modelos siempre respondían algo dentro del vocabulario esperado).

**Configuración de inferencia:**
- LLaVA-Med: batch_size=4, temperatura default
- Mini-VLM: batch_size=1 (limitación de implementación)
- Ambos: bf16 en GPU Ampere/Ada

**Fine-tuning de clasificación (LLaVA-Med y Mini-VLM):**

Se intentó un fine-tuning liviano de ambos VLMs para la tarea de clasificación directa, entrenando con el mismo prompt y usando las etiquetas de texto como targets. El objetivo era ver si los modelos podían aprender a responder con el código de clase correcto.

### 4.4 Resultados de Clasificación

#### Métricas Globales

| Modelo | Accuracy | F1 (weighted) | Sens. Macro | Spec. Macro |
|--------|----------|---------------|-------------|-------------|
| DenseNet121 | 52.29% | 0.5805 | 39.42% | 91.98% |
| **ViT-B/16** | **63.14%** | **0.6676** | **51.96%** | **93.26%** |
| LLaVA-Med (zero-shot) | 11.44% | 0.0296 | 15.61% | 85.80% |
| LLaVA-Med (fine-tuned) | 11.11% | 0.0222 | 14.29% | 85.71% |
| Mini-VLM (zero-shot) | 5.12% | 0.0061 | 14.39% | 85.71% |
| Mini-VLM (fine-tuned) | 11.18% | 0.0236 | 14.47% | 85.73% |

*Evaluado sobre 1.503 imágenes del set de test HAM10000.*

#### Sensibilidad por Clase — DenseNet121

| Clase | Sensibilidad | Especificidad | F1-Score | Support |
|-------|-------------|---------------|----------|---------|
| MEL | 52.69% | 76.95% | 0.313 | 167 |
| **NV** | **59.54%** | **93.56%** | **0.732** | **1006** |
| BCC | 38.96% | 93.13% | 0.293 | 77 |
| AKIEC | 22.45% | 96.70% | 0.204 | 49 |
| BKL | 26.06% | 90.96% | 0.261 | 165 |
| DF | 35.29% | 94.62% | 0.117 | 17 |
| VASC | 40.91% | 97.97% | 0.295 | 22 |

#### Sensibilidad por Clase — ViT-B/16

| Clase | Sensibilidad | Especificidad | F1-Score | Support |
|-------|-------------|---------------|----------|---------|
| MEL | 55.69% | 81.59% | 0.368 | 167 |
| **NV** | **69.68%** | **89.13%** | **0.796** | **1006** |
| BCC | 66.23% | 90.95% | 0.397 | 77 |
| AKIEC | 42.86% | 97.18% | 0.378 | 49 |
| BKL | 39.39% | 96.11% | 0.461 | 165 |
| DF | 35.29% | 99.66% | 0.429 | 17 |
| VASC | 54.55% | 98.18% | 0.393 | 22 |

#### El Fenómeno de Colapso de Clase en VLMs

Los resultados de los VLMs en clasificación zero-shot revelan un fenómeno llamativo: **colapso a una única clase**.

**LLaVA-Med:**
- Predice MEL en 1.450 de 1.503 imágenes (~96.5%)
- Solo BCC tiene alguna predicción alternativa (53 imágenes)
- Sensibilidad MEL: 97.6%, sensibilidad para todas las demás clases: 0%
- Accuracy = 11.44% ≈ proporción de MEL en el test set (11.1%)

**Mini-VLM (zero-shot):**
- Predice BCC en 1.484 de 1.503 imágenes (~98.7%)
- Solo AKIEC tiene mínima predicción alternativa (19 imágenes)
- Sensibilidad BCC: 98.7%, resto: ~0%
- Accuracy = 5.12% ≈ proporción de BCC en el test set (5.1%)

**LLaVA-Med (fine-tuned):**
- Colapso **completo** a MEL: predice MEL en 1.503 de 1.503 imágenes (100%)
- Sensibilidad MEL: 100.0%, especificidad MEL: 0.0% (predice TODO como MEL sin excepción)
- El fine-tuning agrava el colapso respecto al zero-shot (1.450 → 1.503 predicciones MEL)
- Accuracy = 11.11% ≈ proporción de MEL en el test set

**Mini-VLM (fine-tuned):**
- El colapso persiste pero cambia de clase: colapsa a MEL (1.500/1.503 predicciones MEL)
- Sensibilidad MEL: 100.0%, resto: ~0%
- El fine-tuning no resolvió el problema, solo cambió la clase de destino (de BCC a MEL)

**Conclusión sobre fine-tuning de clasificación:** el fine-tuning de etiqueta directa no resuelve el problema de colapso en **ninguno** de los dos VLMs. En LLaVA-Med incluso lo empeora. El enfoque de forzar a un VLM generativo a responder con un código discreto no es viable sin cambios más profundos en la arquitectura o el prompt.

La matriz de confusión de LLaVA-Med zero-shot ilustra el colapso:

```
Pred: MEL   NV   BCC  AKIEC BKL  DF  VASC
Real MEL: [163,   0,   4,   0,   0,  0,   0]   → 97.6% como MEL
Real  NV: [983,   0,  23,   0,   0,  0,   0]   → 97.7% como MEL
Real BCC: [ 68,   0,   9,   0,   0,  0,   0]   → 88.3% como MEL
Real AKIEC:[46,   0,   3,   0,   0,  0,   0]   → 93.9% como MEL
Real BKL: [159,   0,   6,   0,   0,  0,   0]   → 96.4% como MEL
Real  DF: [ 16,   0,   1,   0,   0,  0,   0]   → 94.1% como MEL
Real VASC:[ 18,   0,   4,   0,   0,  0,   0]   → 81.8% como MEL
```

**Causas posibles del colapso:**
1. Los VLMs generativos no están diseñados para tareas de clasificación de etiqueta única. Al forzarlos a responder con un solo código, tienden al diagnóstico más "evidente" o "peligroso" (melanoma es la respuesta más mencionada en la literatura médica).
2. La temperatura de generación default favorece respuestas de alta confianza, eliminando la diversidad necesaria para clasificar bien.
3. El desbalance de clases en el preentrenamiento médico puede haber sesgado al modelo hacia ciertas categorías.
4. El prompt engineering no fue optimizado — prompts más elaborados con ejemplos few-shot podrían mejorar los resultados.

---

## 5. Fase 2 — Generación de Reportes Clínicos

### 5.1 Objetivo

Fine-tunear LLaVA-Med y Mini-VLM para generar reportes clínicos estructurados a partir de imágenes dermoscópicas. El reporte objetivo incluye:
- **Hallazgos:** descripción morfológica de la lesión
- **Impresión diagnóstica:** diagnóstico más probable
- **Diagnósticos diferenciales:** otros diagnósticos a considerar

El prompt de generación utilizado fue:
```
Describe this skin lesion with a structured clinical report that includes:
findings, diagnostic impression, and differential diagnosis.
```

### 5.2 Pipeline de Fine-tuning en Dos Etapas

El fine-tuning de VLMs multimodales es más complejo que el de modelos de texto, porque requiere alinear dos espacios de representación distintos: el espacio visual (CLIP) y el espacio lingüístico (LLM). Se implementó un pipeline de dos etapas inspirado en LLaVA original:

#### Etapa 1 — Alineación Visual-Textual (MLP Projector)

**Objetivo:** Entrenar el proyector MLP para que las representaciones visuales de CLIP sean "inteligibles" para el LLM, sin modificar el LLM.

**Configuración:**
- Dataset: SkinCAP (~4.000 pares imagen-caption)
- Módulos entrenados: **solo el proyector MLP** (LLM y CLIP encoder congelados)
- Epochs: 1 (suficiente para convergencia inicial)
- Learning rate: 2e-4
- Batch size: 16
- Tarea: predecir el caption dado la imagen

**Intuición:** Es como "conectar" el encoder visual al LLM. El proyector aprende a traducir vectores de imagen a un espacio que el LLM ya sabe procesar.

#### Etapa 2 — LoRA Fine-tuning

**Objetivo:** Fine-tunear el LLM con el proyector ya alineado, para que el modelo aprenda a generar reportes clínicos estructurados.

**¿Por qué LoRA?** Los LLMs de 7B parámetros requieren ~28 GB en fp32 para almacenar gradientes durante el entrenamiento completo. LoRA (*Low-Rank Adaptation*) introduce matrices de bajo rango que modifican indirectamente los pesos del modelo, reduciendo los parámetros entrenables de 7B a ~10-50M, con una fracción del costo de VRAM.

**Configuración LoRA:**

```yaml
r: 64                  # Rango de las matrices de adaptación
lora_alpha: 128        # Factor de escala (alpha/r = 2.0)
lora_dropout: 0.05     # Regularización
target_modules:
  - q_proj             # Proyección de queries en atención
  - v_proj             # Proyección de values en atención
task_type: CAUSAL_LM
```

**Configuración de entrenamiento:**
- Dataset: SkinCaRe completo (~7.041 pares)
- Módulos congelados: encoder visual CLIP
- Módulos entrenables: LoRA adapters en LLM + proyector MLP
- Epochs: 3
- Learning rate: 2e-5
- Batch size: 4
- Gradient accumulation: 8 steps (batch efectivo = 32)
- Early stopping: patience=3, monitor=val_loss

### 5.3 Resultados de Entrenamiento

#### Etapa 1 — LLaVA-Med (5 epochs)

| Epoch | Train Loss | Val Loss |
|-------|-----------|----------|
| 1 | 1.9835 | 1.9248 |
| 2 | 1.8032 | 1.8490 |
| 3 | 1.6897 | 1.8185 |
| **4** | **1.5613** | **1.8134** ← mejor |
| 5 | 1.4655 | 1.8338 |

**Observación:** La pérdida de validación se estabiliza en epoch 4 y comienza a subir en epoch 5, indicando inicio de overfitting. Esto es esperable: el proyector tiene capacidad limitada y converge rápido con un dataset relativamente pequeño (~4K pares).

#### Etapa 1 — Mini-VLM (5 epochs)

| Epoch | Train Loss | Val Loss |
|-------|-----------|----------|
| 1 | 1.9736 | 1.9108 |
| 2 | 1.7825 | 1.8475 |
| **3** | **1.6155** | **1.8410** ← mejor |
| 4 | 1.3657 | 1.9183 |
| 5 | 1.1831 | 2.0111 |

**Observación:** Mini-VLM muestra un overfitting más pronunciado que LLaVA-Med. La pérdida de entrenamiento cae agresivamente (de 1.97 a 1.18) mientras la validación sube (de 1.91 a 2.01). El proyector de Phi-3-mini parece tener mayor capacidad de memorización que el de Mistral-7B, lo que lleva a sobreajuste con menos epochs.

#### Etapa 2 — LLaVA-Med con LoRA (3 epochs)

| Epoch | Train Loss | Val Loss |
|-------|-----------|----------|
| 1 | 0.7997 | 0.7449 |
| 2 | 0.6888 | 0.7260 |
| **3** | **0.6255** | **0.7239** ← mejor |

**Observación:** Entrenamiento estable. La pérdida de validación converge suavemente sin signos de overfitting severo. La brecha train-val (~0.10) es razonable para un modelo generativo. La reducción de pérdida de 0.80→0.63 indica que el modelo está aprendiendo los patrones del dataset SkinCaRe.

#### Etapa 2 — Mini-VLM con LoRA (3 epochs)

| Epoch | Train Loss | Val Loss |
|-------|-----------|----------|
| 1 | 1.0119 | 0.9296 |
| 2 | 0.9203 | 0.8984 |
| **3** | **0.8963** | **0.8799** ← mejor |

**Observación:** Mini-VLM parte de una pérdida inicial más alta (~1.01 vs 0.80 de LLaVA-Med), consistente con un modelo base menos especializado en el dominio médico. La convergencia es estable pero los valores absolutos son mayores, sugiriendo que Mini-VLM tiene más dificultad para modelar los patrones del lenguaje clínico que LLaVA-Med.

### 5.4 Framework de Evaluación de Reportes

Se implementó un sistema de evaluación de tres niveles, considerando que los reportes médicos son difíciles de evaluar automáticamente:

#### Nivel 1 — Métricas Automáticas con Referencia

**Archivo:** `src/evaluation/generation.py`

Se calculan contra reportes de referencia del dataset MM-Skin:

| Métrica | Qué mide | Implementación |
|---------|----------|---------------|
| BLEU-4 | Solapamiento de n-gramas (hasta 4-gramas) | HuggingFace `evaluate` |
| ROUGE-L | Subsecuencia común más larga | HuggingFace `evaluate` |
| BERTScore F1 | Similitud semántica via embeddings | DeBERTa / DistilBERT fallback |
| METEOR | N-gramas + sinónimos + stemming | HuggingFace `evaluate` |
| CIDEr | TF-IDF ponderado (imagen-referencia) | pycocoevalcap / impl. propia |

Cada métrica falla de forma independiente (try/except individual), garantizando que una librería faltante no detenga toda la evaluación.

#### Nivel 2 — NER Clínico sin Referencia

**Archivo:** `src/evaluation/clinical_ner.py`

Este nivel evalúa la calidad clínica **sin necesitar un reporte de referencia**, lo que es más realista en la práctica médica.

**Pipeline de extracción de entidades:**

1. **SciSpaCy** (NLP biomédico): intenta cargar `en_ner_bionlp13cg_md`, con fallback a `en_core_sci_md`
2. **Diccionario dermatológico personalizado**: términos organizados en 3 categorías:
   - *Criterios ABCDE*: asimetría, borde, color, diámetro, evolución
   - *Tipos de lesión*: melanoma, nevus, carcinoma, queratosis, dermatofibroma, angioma, etc.
   - *Características clínicas*: pigmentación, ulceración, bordes irregulares, vascularización, etc.

**Métricas calculadas:**

- **Clinical Entity Recall:** proporción de categorías de términos dermatológicos que el reporte menciona al menos una vez. Un reporte que menciona términos de las 3 categorías obtiene recall = 1.0.

- **Diagnostic Consistency:** porcentaje de reportes donde el diagnóstico de ground truth aparece mencionado en el texto generado. Se implementa matching con sinónimos:

```python
synonyms = {
    "MEL": ["melanoma", "mel ", "malignant melanoma"],
    "NV":  ["nevus", "nevi", "melanocytic nevus", "mole"],
    "BCC": ["basal cell", "bcc", "basalioma"],
    "AKIEC": ["actinic keratosis", "intraepithelial carcinoma", "akiec"],
    "BKL": ["seborrheic keratosis", "solar lentigo", "bkl", "benign keratosis"],
    "DF":  ["dermatofibroma", "df "],
    "VASC": ["vascular", "angioma", "granuloma", "vasc"]
}
```

#### Nivel 3 — Revisión Manual

**Archivo:** `scripts/evaluate_reports.py`

Genera CSVs para evaluación humana con los campos:
- `image_id`, `model`, `generated_report`, `reference`, `gt_label`
- `evaluator_score` (1-5, a completar por revisor)
- `evaluator_comments` (texto libre)

**Rúbrica sugerida:**
- **1:** Incoherente o clínicamente incorrecto
- **2:** Parcialmente correcto pero con errores graves
- **3:** Correcto pero incompleto
- **4:** Completo y clínicamente útil
- **5:** Excelente, comparable a reporte médico profesional

Los CSVs generados (`level3_llava_med_manual_review.csv`, `level3_mini_vlm_manual_review.csv`) contienen 1.503 reportes cada uno, listos para revisión por un dermatólogo.

### 5.5 Resultados de Evaluación — Nivel 2 (NER Clínico)

| Modelo | Clinical Entity Recall | Diagnostic Consistency |
|--------|------------------------|------------------------|
| LLaVA-Med | **45.69%** | **71.47%** |
| Mini-VLM | **60.68%** | 31.34% |

**Interpretación detallada:**

**LLaVA-Med** muestra alta consistencia diagnóstica (71.5%): en casi 3 de cada 4 reportes, el texto generado menciona explícitamente el diagnóstico correcto o un sinónimo reconocido. Sin embargo, su entity recall más bajo (45.7%) sugiere que los reportes tienden a ser más concisos o directos al diagnóstico, sin elaborar tanto la descripción morfológica.

**Mini-VLM** produce reportes con mayor riqueza terminológica (60.7% entity recall): menciona más términos del vocabulario dermatológico, describiendo con más detalle características como asimetría, pigmentación o tipo de borde. Sin embargo, la consistencia diagnóstica es baja (31.3%): el diagnóstico correcto solo aparece en 1 de cada 3 reportes.

Este trade-off sugiere que:
- LLaVA-Med genera reportes más orientados al diagnóstico final (útil para segunda opinión)
- Mini-VLM genera descripciones morfológicas más ricas pero con menor precisión diagnóstica (útil para descripción de hallazgos)

---

## 6. Análisis e Interpretación de Resultados

### 6.1 Clasificación vs. Generación: Tareas Fundamentalmente Distintas

El resultado más importante de esta tesina es la demostración empírica de que **clasificación y generación de texto son tareas fundamentalmente distintas, y los modelos diseñados para una no necesariamente funcionan bien en la otra**.

Los clasificadores DenseNet y ViT están optimizados para mapear una imagen a una de 7 etiquetas. Aprenden representaciones internas que maximizan la separabilidad entre clases. Este objetivo está perfectamente alineado con la tarea de clasificación.

Los VLMs, en cambio, están diseñados para generar texto dado un contexto visual. Aprenden a producir descripciones, responder preguntas, razonar sobre imágenes. Forzarlos a responder con una única etiqueta va en contra de su distribución de entrenamiento: un VLM médico "sabe" que la respuesta correcta a "¿qué lesión es esta?" es un párrafo de explicación, no un código de 3 letras.

El resultado más revelador es que el **fine-tuning de clasificación directa empeora el comportamiento** en lugar de mejorarlo. LLaVA-Med fine-tuned pasa de 1.450 a 1.503 predicciones MEL (colapso total), y Mini-VLM fine-tuned cambia su clase de colapso de BCC a MEL sin ganar verdadera capacidad discriminativa. Esto confirma que el problema no es de falta de entrenamiento, sino de inadecuación fundamental del paradigma de respuesta discreta para modelos generativos.

### 6.2 Rendimiento de Clasificadores Tradicionales

**ViT supera a DenseNet** en todas las métricas:
- +10.85 puntos de accuracy (63.1% vs 52.3%)
- +0.087 en F1 weighted (0.668 vs 0.581)
- +12.54 puntos en sensibilidad macro (52.0% vs 39.4%)

La ventaja del ViT proviene de su mecanismo de atención global: puede relacionar características de distintas regiones de la imagen, algo que las CNNs realizan de forma más local. En dermoscopia, el contexto global (distribución del pigmento, simetría global) es importante para distinguir, por ejemplo, melanoma de nevo.

**Ambos modelos sufren con clases minoritarias:**
- DF (17 casos en test): sensibilidad ≤ 35.3% en ambos modelos
- AKIEC (49 casos): sensibilidad 22.4% (DenseNet) / 42.9% (ViT)
- VASC (22 casos): sensibilidad 40.9% / 54.5%

Esto es esperado con el nivel de desbalance del dataset (NV domina con 67%). El uso de class weights en la loss ayuda pero no elimina completamente el problema.

### 6.3 Overfitting en Etapa 1 vs. Estabilidad en Etapa 2

Un hallazgo interesante del entrenamiento es el contraste entre ambas etapas:

- **Etapa 1** (solo proyector MLP): overfitting claro, especialmente en Mini-VLM donde la val_loss sube de 1.91 a 2.01 mientras la train_loss baja a 1.18.
- **Etapa 2** (LoRA + proyector): entrenamiento estable, val_loss decrece suavemente en ambos modelos.

La explicación es la complejidad relativa de cada componente entrenado:
- El proyector MLP tiene pocos parámetros y alta capacidad de memorización. Con ~4K ejemplos de Stage 1, tiende a sobreajustar.
- LoRA entrena adaptadores de bajo rango que tienen regularización implícita (el rango r=64 es una fracción pequeña de la dimensión de las matrices de atención). Además, el dataset Stage 2 es más grande (~7K ejemplos) y más diverso.

### 6.4 Limitaciones Identificadas

1. **Evaluación Nivel 1 pendiente:** Las métricas automáticas (BLEU, ROUGE, BERTScore) con referencia MM-Skin no fueron ejecutadas en los resultados finales (el `backend` en los JSONs de Nivel 2 es "none", indicando que SciSpaCy no estaba disponible en el entorno de evaluación). Se evaluó solo con el diccionario.

2. **Evaluación manual (Nivel 3) pendiente:** Los CSVs están generados y listos, pero la revisión por dermatólogo no se completó. Es el paso final crítico para validar la calidad clínica real de los reportes.

3. **Mini-VLM fine-tuned para clasificación:** El fine-tuning no mejoró la clasificación, sugiriendo que el approach de "responde con la etiqueta" no es el correcto para VLMs. Alternativas a explorar: few-shot prompting, chain-of-thought, o fine-tuning de clasificación con head explícito.

4. **Cuantización en evaluación NER:** El `backend: "none"` en los resultados indica que el modelo SciSpaCy no estaba disponible, por lo que la evaluación se basó solo en el diccionario personalizado. Con SciSpaCy activo, los valores de entity recall serían potencialmente mayores.

---

## 7. Infraestructura y Reproducibilidad

### 7.1 Hardware Utilizado

| Entorno | GPU | VRAM | Arquitectura | Uso |
|---------|-----|------|-------------|-----|
| Local | RTX 4070 | 12 GB | Ada Lovelace (sm=89) | Desarrollo y debug |
| TOKO | RTX 4080 | 16 GB | Ada Lovelace (sm=89) | Entrenamiento clasificadores |
| MendietaF2 | A30 | 24 GB | Ampere (sm=80) | Entrenamiento VLMs |

### 7.2 Gestión de Precisión Numérica

**Archivo:** `src/utils/device.py`

La precisión se selecciona automáticamente según la arquitectura GPU:
- **Ampere+ (SM ≥ 8.0):** `torch.bfloat16` — mejor estabilidad numérica que fp16, nativo en estas GPUs
- **Pre-Ampere (SM < 8.0):** `torch.float32` — fp16 sin Tensor Cores puede causar overflow/underflow

Para GPUs Ada (RTX 4070, RTX 4080) se activa `CUBLAS_WORKSPACE_CONFIG=:16:8` para determinismo completo con operaciones matriciales.

### 7.3 Reproducibilidad

**Archivo:** `src/utils/seed.py`

Todos los scripts invocan `set_seed(42)` que configura:
```python
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

### 7.4 Clusters HPC — SLURM

**Directorio:** `slurm/`

Se implementaron scripts SLURM para ejecutar todos los experimentos en los clusters institucionales:

| Script | Tiempo límite | Descripción |
|--------|--------------|-------------|
| `mendieta_generate_reports_llava.sh` | 12h | Generación de reportes LLaVA-Med |
| `mendieta_generate_reports_mini.sh` | 12h | Generación de reportes Mini-VLM |
| `mendieta_vlm_classify_llava.sh` | 4h | Clasificación zero-shot LLaVA-Med |
| `mendieta_vlm_classify_mini.sh` | 4h | Clasificación zero-shot Mini-VLM |
| `mendieta_vlm_classify_llava_ft.sh` | 6h | Fine-tuning clasificación LLaVA-Med |
| `mendieta_vlm_classify_mini_ft.sh` | 6h | Fine-tuning clasificación Mini-VLM |

Todos los scripts configuran modo offline de HuggingFace (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`) para evitar descargas durante la ejecución, usando directorio temporal en `/scratch/{JOBID}`.

### 7.5 Envío Automatizado de Jobs

**Scripts:** `scripts/mendieta_submit.py`, `scripts/toko_submit.py`

Automatizan el ciclo completo:
1. Sincronización de código local → cluster (via rsync o tar)
2. Envío del job con `sbatch`
3. Captura del JOBID para monitoreo

```bash
# Ejemplos de uso
python scripts/mendieta_submit.py mini_s1          # Stage 1 Mini-VLM
python scripts/mendieta_submit.py llava_s2         # Stage 2 LLaVA-Med (LoRA)
python scripts/mendieta_submit.py gen_llava        # Generación de reportes
python scripts/mendieta_submit.py all_gen          # Ambos modelos, generación
python scripts/mendieta_submit.py all_classify     # Ambos modelos, clasificación

# Sin sincronización (si el código ya está actualizado)
python scripts/mendieta_submit.py gen_mini --no-sync
```

### 7.6 Gestión de Memoria en VLMs

La estrategia de carga de modelos VLMs es robusta ante distintas disponibilidades de VRAM:

```
1. Obtener VRAM disponible (get_free_vram_gb())
2. Si VRAM >= umbral_modelo:
   device_map = "cuda:0"  (sin CPU offload)
   Intentar carga en bf16
3. Si VRAM < umbral_modelo:
   device_map = "auto"    (con CPU offload automático)
   Intentar carga con 4-bit NF4 (BitsAndBytesConfig)
4. Si falla cuantización:
   Reintentar sin cuantización (con warning)
5. Si falla atención SDPA:
   Fallback a atención "eager" (más lenta pero compatible)
```

---

## 8. Arquitectura del Código

### 8.1 Patrones de Diseño

El código sigue patrones estándar de ingeniería de software aplicados a proyectos ML:

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Factory + Registry** | `src/models/factory.py` | Instanciar cualquier modelo por nombre de string |
| **Template Method** | `src/models/vlm_base.py` | Interfaz común para todos los VLMs |
| **Template Method** | `src/data/base_dataset.py` | Interfaz común para todos los datasets |
| **Strategy** | `src/utils/device.py` | Selección automática de dtype/device |
| **Config-Driven** | `configs/*.yaml` | Todos los hiperparámetros externalizados |

### 8.2 Estructura de Módulos

```
src/
├── models/
│   ├── factory.py          # Registry + instanciación
│   ├── vlm_base.py         # ABC: load_components(), generate(), forward()
│   ├── classifiers.py      # DenseNet121Classifier, ViTClassifier
│   ├── llava_med.py        # LLaVA-Med (CLIP ViT-L/14 + Mistral-7B)
│   └── mini_vlm.py         # Phi-3.5-vision (CLIP ViT-B/16 + Phi-3-mini)
│
├── data/
│   ├── base_dataset.py     # ABC con retry NFS, class weights
│   ├── ham10000.py         # HAM10000: 7 clases, splits JSON
│   ├── skincare.py         # SkinCaRe: pares imagen-texto
│   ├── mmskin.py           # MM-Skin: captions + VQA
│   ├── hiba.py             # HIBA: metadatos Fitzpatrick
│   └── transforms.py       # Augmentaciones centralizadas
│
├── training/
│   ├── trainer.py          # Loop de entrenamiento genérico
│   ├── two_stage.py        # Pipeline 2 etapas VLM
│   ├── lora_config.py      # Factory de configuraciones LoRA
│   └── callbacks.py        # EarlyStopping, ModelCheckpoint
│
├── evaluation/
│   ├── classification.py   # Accuracy, F1, AUC, sens/spec
│   ├── generation.py       # BLEU, ROUGE, BERTScore, METEOR, CIDEr
│   └── clinical_ner.py     # SciSpaCy + diccionario + métricas NER
│
└── utils/
    ├── device.py           # CUDA detection, dtype, VRAM monitor
    ├── seed.py             # set_seed() reproducibilidad
    ├── logging.py          # Logging estructurado + wandb
    └── io.py               # JSON/CSV helpers
```

### 8.3 Convenciones

- **Idioma del código:** inglés (variables, funciones, docstrings técnicos)
- **Idioma de logs:** español (mensajes al usuario en consola)
- **Imports:** siempre desde `src.` (e.g., `from src.utils.seed import set_seed`)
- **Scripts:** usan `sys.path.insert(0, ...)` para resolver imports desde `Codigo/`
- **Salida de datasets:** diccionario estandarizado `{"image": tensor, "label": int, "text": str, "metadata": dict}`

### 8.4 Configuración (Hydra/YAML)

Todos los hiperparámetros viven en `configs/`:

```
configs/
├── base.yaml                    # seed, device, wandb, paths
├── phase1_classification.yaml   # Hiperparámetros Fase 1
├── phase2_generation.yaml       # Hiperparámetros Fase 2 (stages + LoRA)
├── densenet.yaml                # Específico DenseNet121
├── vit.yaml                     # Específico ViT-B/16
├── llava_med.yaml               # Específico LLaVA-Med
└── mini_vlm.yaml                # Específico Mini-VLM
```

El principio es que **ningún valor numérico debe estar hardcodeado en Python**. Cualquier cambio de hiperparámetro se hace en YAML sin tocar el código.

---

## 9. Trabajo Futuro — Fase 3

### 9.1 Estudios de Ablación (Planificados)

**Notebook:** `notebooks/03_ablation_analysis.ipynb` (esqueleto implementado)

| Ablación | Variable | Valores a explorar |
|----------|----------|-------------------|
| Rango LoRA | `r` | 16, 32, **64** (actual), 128 |
| Alpha LoRA | `lora_alpha` | 32, 64, **128** (actual), 256 |
| LoRA vs QLoRA | quantization | LoRA (bf16) vs QLoRA (4-bit NF4) |
| Datos de alineación | Stage 1 dataset size | 25%, 50%, 75%, 100% de SkinCAP |
| Target modules | LoRA targets | q+v (actual) vs q+k+v+o vs all linear |

### 9.2 Análisis de Sesgo por Fototipo

Usando el dataset HIBA, se planea evaluar si los modelos exhiben rendimiento diferencial según el fototipo de Fitzpatrick del paciente. Esto es crítico para garantizar equidad en un sistema de diagnóstico médico.

### 9.3 Mejora de Clasificación con VLMs

Los resultados de clasificación zero-shot son claramente deficientes. Alternativas a explorar:
- **Few-shot prompting:** incluir 1-3 ejemplos de cada clase en el prompt
- **Chain-of-thought:** pedir al modelo que razone antes de dar la etiqueta
- **Temperatura calibrada:** reducir temperatura para respuestas más determinísticas
- **Prompt con descripción de clases:** en lugar de solo los códigos, incluir descripción morfológica de cada clase

### 9.4 Evaluación Manual Completa

Los CSVs de Nivel 3 (`level3_llava_med_manual_review.csv`, `level3_mini_vlm_manual_review.csv`) deben ser revisados por un dermatólogo con la rúbrica definida. Esta evaluación proporcionará la validación clínica final del sistema y es el aporte más directo a la práctica médica.

---

## Apéndice — Comandos de Uso

### Fase 1 — Clasificación

```bash
# Entrenar clasificadores tradicionales
python scripts/train_classifier.py --model densenet --epochs 30
python scripts/train_classifier.py --model vit --epochs 30

# Clasificación zero-shot con VLMs (dry-run para verificar)
python scripts/train_vlm_classify.py --model llava_med --dry-run
python scripts/train_vlm_classify.py --model mini_vlm --dry-run

# Evaluación comparativa
python scripts/evaluate_classify.py  # Genera tabla comparativa de todos los modelos
```

### Fase 2 — Generación de Reportes

```bash
# Stage 1: Alineación del proyector
python scripts/train_vlm_stage1.py --model llava_med --epochs 1
python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1

# Stage 2: LoRA fine-tuning
python scripts/train_vlm_stage2.py --model llava_med --checkpoint outputs/checkpoints/stage1_llava_med/best_model.pt --epochs 3
python scripts/train_vlm_stage2.py --model mini_vlm --checkpoint outputs/checkpoints/stage1_mini_vlm/best_model.pt --epochs 3

# Generación de reportes
python scripts/generate_report.py --model llava_med --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt --images_dir data/processed/HAM10000 --output_dir outputs/generated_reports/llava_med/HAM10000

# Evaluación de reportes
python scripts/evaluate_reports.py --model llava_med --level 2  # NER clínico
python scripts/evaluate_reports.py --model mini_vlm --level 2
```

### Clusters HPC

```bash
# Enviar jobs a MendietaF2
python scripts/mendieta_submit.py all_gen      # Generación completa (ambos modelos)
python scripts/mendieta_submit.py all_classify # Clasificación completa

# Monitorear jobs
python scripts/mendieta_monitor.py             # Lista todos los jobs activos
python scripts/mendieta_monitor.py <job_id>   # Estado de un job específico
```

---

*Documento generado el 2026-03-25. Resultados basados en experimentos ejecutados en los clusters TOKO y MendietaF2.*
