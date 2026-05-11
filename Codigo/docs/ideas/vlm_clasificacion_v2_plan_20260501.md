# Mejoras para Clasificación con VLMs — LLaVA-Med y Mini-VLM

**Estado:** T1 y T2 implementados — ejecutando en clusters
**Fecha:** 2026-05-01
**Modelos afectados:** LLaVA-Med 7B (Mistral-7B), Mini-VLM (CLIP ViT-B/16 + Phi-3.5-mini)
**Dataset:** HAM10000 (test, n=1503) + HIBA OOD (n=1616)

---

## 1. Contexto y motivación

### 1.1 Resultados actuales (baseline v1)

Los VLMs fueron evaluados en clasificación usando el método `generate` con prompt engineering básico:

| Modelo | Acc (HAM) | F1-w (HAM) | Método |
|--------|-----------|-----------|--------|
| LLaVA-Med 7B (ZS) | 0.1144 | 0.030 | generate |
| Mini-VLM (ZS) | 0.0512 | 0.006 | generate |

Ambos resultados están **por debajo de la probabilidad aleatoria** (14.3% para 7 clases), indicando colapso severo hacia clases mayoritarias o hacia salidas de texto no parseables.

### 1.2 Objetivo de la tesina

La tesina no compara clasificadores aislados sino que evalúa la **relación entre calidad (clasificación + reporte) y costo computacional** por modelo. Los VLMs son necesarios para la generación de reportes; la clasificación es una tarea adicional que se espera que el mismo checkpoint resuelva.

**Restricción clave:** se usa el mismo modelo fine-tuneado para clasificación y generación de reportes. No se hace fine-tuning separado para clasificación.

### 1.3 Referencia SOTA

| Trabajo | Método | Acc HAM10000 |
|---------|--------|-------------|
| Skin-R1 (Qwen2.5-VL-7B + RL) | FT + GRPO | 87.86% |
| SkinVL-Pub (LLaVA-Med + LoRA) | FT supervisado | 63.46% |
| LLaVA-Med-7B | ZS | 62.16% |
| GPT-4V | ZS | 55.21% |

El gap entre LLaVA-Med ZS externo (62%) y nuestra evaluación ZS (11%) indica que el problema no es el modelo sino el **método de evaluación** (generate vs likelihood) y la falta de aprovechamiento del fine-tuning de Stage 2.

---

## 2. Análisis del pipeline actual

### 2.1 Método `generate` (usado en v1)

```
prompt → model.generate() → texto libre → regex parse → clase
```

**Problema:** El modelo genera texto libre y puede producir respuestas no parseables, descripciones largas, o colapsar hacia la clase más probable a priori. Con 7 clases desbalanceadas (NV = 67% del test), el modelo puede alcanzar 67% de "accuracy" simplemente respondiendo siempre "NV" — pero la forma de parsear la respuesta libre hace que el 5–11% sea el resultado real.

### 2.2 Método `likelihood` (implementado, no usado en v1)

```
para cada clase c en {MEL, NV, BCC, AKIEC, BKL, DF, VASC}:
    score(c) = max_synonym [ log P(c_text | image, prompt_prefix) / n_tokens ]
pred = argmax_c score(c)
```

- Ensemble de 4 prompts (2 abiertos + 2 cerrados)
- 3 sinónimos por clase, normalización por longitud
- **Nunca produce UNKNOWN** — siempre devuelve una clase válida
- Implementado en `src/evaluation/vlm_scoring.py`

Este método es directamente comparable con cómo Skin-R1 y SkinVL evalúan ZS: calculando probabilidades condicionadas en lugar de generar texto libre.

---

## 3. Técnicas a implementar

Ordenadas de menor a mayor costo computacional/implementación.

### 3.1 T1 — Likelihood scoring correcto ✅ IMPLEMENTADO

**Descripción:** Usar el método `likelihood` ya implementado con los checkpoints actuales (base y fine-tuneado Stage 2).

**Implementación:** `scripts/train_vlm_classify.py --method likelihood`. Implementado en `src/evaluation/vlm_scoring.py` con ensemble de 4 prompts (O1, O2, C1, C2), 3 sinónimos por clase agregados por max, y length-normalization.

**Ganancia esperada:** +20–40% Acc sobre el método `generate`. LLaVA-Med externo ZS con likelihood scoring alcanza ~62% (Skin-R1 paper).

**Costo:** Bajo. Sin entrenamiento, solo inferencia.

**Corridas (via submit.py):**
```bash
# TOKO
python scripts/toko/submit.py all_classify_lik   # 4 jobs: base + ft, ambos modelos

# Mendieta
python scripts/mendieta/submit.py all_classify_lik
```

**Outputs:** `{model}_likelihood[_finetuned]_{predictions,test_results}.json`

---

### 3.2 T2 — Structured prompting / Chain-of-Thought (CoT) ✅ IMPLEMENTADO

**Descripción:** El modelo razona paso a paso sobre features dermoscópicas (ABCDE: asimetría, bordes, colores, diámetro, estructuras especiales) antes del diagnóstico final. Basado en Skin-R1 (SFT sobre trayectorias diagnósticas).

**Formato de prompt (COT_PROMPT en `vlm_scoring.py`):**

```
"You are a dermatology expert analyzing a dermoscopic image.
Think step by step and use the following format exactly:
Features: [describe asymmetry, borders, colors, diameter, special structures]
Differential: [list the most likely diagnoses with brief reasoning]
Final diagnosis: [one of: MEL, NV, BCC, AKIEC, BKL, DF, VASC]"
```

**Parseo (`parse_cot_response` en `train_vlm_classify.py`):**
1. Busca `Final diagnosis: <LABEL>` con regex (case-insensitive, tolera `[...]`)
2. Si el campo existe pero contiene nombre largo → busca código de clase dentro
3. Fallback a `parse_vlm_response()` si no encuentra el campo

**Archivos modificados:**
- `src/evaluation/vlm_scoring.py`: añadidos `ABCDE_FEATURES` (descriptores morfológicos por clase) y `COT_PROMPT`
- `scripts/train_vlm_classify.py`: añadidos `parse_cot_response()`, `run_cot_eval()` y `--method cot` en argparse
- `slurm/toko/vlm_classify_{llava,mini}.sh`: añadido soporte `METHOD` env var
- `slurm/toko/vlm_classify_{llava,mini}_ft.sh`: scripts ft nuevos para TOKO
- `scripts/toko/submit.py` y `scripts/mendieta/submit.py`: añadidos jobs `*_cot` y grupo `all_classify_cot`

**Ganancia esperada:** +5–15% Acc sobre T1 con el checkpoint Stage 2 (entrenado para texto clínico estructurado).

**Costo:** Bajo. Sin entrenamiento. `max_new_tokens=200` → ~2× más lento que generate.

**Corridas (via submit.py):**
```bash
# TOKO
python scripts/toko/submit.py all_classify_cot   # 4 jobs: base + ft, ambos modelos

# Mendieta
python scripts/mendieta/submit.py all_classify_cot
```

**Outputs:** `{model}_cot[_finetuned]_{predictions,test_results}.json`

---

### 3.3 T3 — LoRA classification adapter sobre checkpoint Stage 2

**Descripción:** Agregar un LoRA de clasificación de baja rank (r=8 o r=16) sobre el checkpoint de Stage 2, entrenado supervisadamente con las etiquetas de HAM10000. El objetivo es maximizar la probabilidad de la clase correcta usando las representaciones aprendidas en Stage 2 (generación de reportes).

**Motivación:** MM-Skin demostró que LLaVA-Med + LoRA supervisado llega a 63.46% en HAM10000. Con un checkpoint Stage 2 que ya tiene alineación visual-texto en el dominio dermatológico, el LoRA de clasificación debería converger más rápido y a un mejor resultado.

**Diseño:**

```
Checkpoint Stage 2 (frozen) 
    + LoRA-cls (r=8, alpha=16, target: q_proj, v_proj del LLM)
    entrenado con:
        input: imagen + prompt de clasificación
        target: token de la clase correcta (e.g., "MEL")
        loss: CrossEntropy sobre logits del primer token de respuesta
```

**Training:**
- Dataset: HAM10000 train (6951 imágenes) con etiquetas como texto
- Epochs: 5–10 (early stopping sobre val F1)
- LR: 2e-4, batch: 8, gradient accumulation: 4
- Cluster: TOKO (RTX 4080 16GB) o Mendieta (A30 24GB)

**Evaluación:** Likelihood scoring con el checkpoint Stage 2 + LoRA-cls (los LoRAs son aditivos).

**Ganancia esperada:** +30–50% Acc sobre T1 puro. Meta: F1-weighted ≥ 0.60 en HAM10000.

**Costo:** Medio. Requiere entrenamiento adicional (~2–4h en TOKO).

**Archivos a modificar/crear:**
- `configs/vlm_classify_lora.yaml` — hiperparámetros del LoRA de clasificación
- `scripts/train_vlm_classify_lora.py` — script de fine-tuning para clasificación
- `slurm/toko/vlm_cls_lora_llava.sh` y `vlm_cls_lora_mini.sh` — jobs SLURM

---

### 3.4 T4 — Dual visual encoder (opcional, Mendieta)

**Descripción:** Agregar un segundo encoder visual especializado en clasificación, paralelo al CLIP existente. Basado en MpoxVLM. El ViT classifier (e.g., ConvNeXt-Tiny o el mejor clasificador Fase 1) proyecta features de clasificación al espacio del LLM mediante un MLP adicional.

**Arquitectura:**

```
imagen → CLIP ViT-B/16 (frozen) → MLP projection → tokens visuales generales
imagen → ConvNeXt-Tiny (frozen, fine-tuned HAM) → MLP_cls → tokens clasificación
                                                              ↓
                                              concat → LLM → respuesta
```

**Motivación:** El CLIP encoder captura features generales; el ConvNeXt-Tiny ya tiene features específicas de HAM10000. La combinación evita el olvido catastrófico y provee señal directa de clasificación.

**Costo:** Alto. Requiere modificar la arquitectura del modelo base, aumenta VRAM significativamente (~18–22GB). Solo viable en Mendieta (A30 24GB).

**Cuando aplicar:** Si T3 no alcanza F1 ≥ 0.60 en HAM10000.

---

### 3.5 T5 — GRPO / RL con reward de clasificación (opcional, Mendieta)

**Descripción:** Replicar la estrategia de Skin-R1: tras el SFT (Stage 2), aplicar GRPO con un reward function que incluya accuracy de clasificación y corrección de formato del razonamiento.

**Reward function:**
```
R = w1 * I(pred_class == true_class)       # exactitud de diagnóstico
  + w2 * I(formato_correcto)               # respeta estructura CoT
  + w3 * rouge(reporte_generado, referencia)  # calidad del reporte
```

**Motivación:** Skin-R1 pasó de ~70% (SFT solo) a 87.86% (SFT + GRPO). La diferencia crítica es que el reward incentiva el razonamiento clínico correcto, no solo la predicción final.

**Costo:** Muy alto. GRPO requiere múltiples rollouts por sample. Factible en Mendieta con A30 24GB para modelos de 7B con QLoRA (4-bit).

**Cuando aplicar:** Si T1–T4 no superan F1 ≥ 0.75. Es la última iteración antes de concluir que el costo computacional de los VLMs no justifica la mejora sobre los clasificadores supervisados.

---

## 4. Plan de ejecución por fases

| Fase | Técnica | Estado | Cluster | Entregable | Criterio de parada |
|------|---------|--------|---------|-----------|-------------------|
| **v2** | T1: Likelihood scoring | ✅ Implementado | TOKO + Mendieta | Acc ZS y FT con likelihood para ambos VLMs | Si FT Stage 2 ≥ 0.55 F1 → v3; si no → T2 |
| **v2** | T2: CoT prompting | ✅ Implementado | TOKO + Mendieta | Acc con structured prompt para ambos VLMs | Comparar vs T1 |
| **v3** | T3: LoRA classification | Pendiente | TOKO o Mendieta | Checkpoint + métricas HAM10000 + HIBA | Si ≥ 0.60 F1 → reportar; si no → T4 |
| **v4** | T4: Dual encoder | Pendiente | Mendieta | Checkpoint modificado + métricas | Si ≥ 0.70 F1 → reportar; si no → T5 |
| **v5** | T5: GRPO/RL | Pendiente | Mendieta | Checkpoint RL + métricas | Reportar resultado final |

---

## 5. Métricas objetivo

| Técnica | F1-w mínimo (HAM) | F1-w meta (HAM) | Criterio para avanzar |
|---------|------------------|----------------|----------------------|
| T1 Likelihood | 0.40 | 0.55 | Si < 0.40 → revisar implementación |
| T2 CoT | +0.05 sobre T1 | +0.10 sobre T1 | Siempre ejecutar, comparar |
| T3 LoRA-cls | 0.55 | 0.65 | Si ≥ 0.60 → reportar como resultado final |
| T4 Dual encoder | 0.65 | 0.75 | Si ≥ 0.70 → reportar como resultado final |
| T5 GRPO/RL | 0.75 | 0.85 | Resultado final independientemente |

---

## 6. Análisis de papers SOTA — técnicas aplicables

### 6.1 Skin-R1 (Qwen2.5-VL-7B + GRPO, 87.86% HAM10000)

**Técnica clave:** SFT sobre trayectorias diagnósticas estructuradas + GRPO con reward multi-componente.

**Aplicable a nuestros modelos:**
- CoT prompting (T2): replicar el formato de razonamiento jerárquico
- GRPO (T5): el reward de clasificación + formato es directamente transferible

**Lo que NO aplicamos:** El SFT sobre trayectorias requiere un dataset de razonamiento clínico que no tenemos para HAM10000. SkinCaRe tiene reportes pero no trayectorias diagnósticas paso a paso.

### 6.2 MM-Skin / SkinVL (LLaVA-Med + LoRA, 60–63% HAM10000)

**Técnica clave:** LoRA supervisado sobre etiquetas de clasificación con dataset textbook-derivado.

**Aplicable a nuestros modelos:**
- T3 (LoRA classification adapter) replica directamente este enfoque
- La diferencia: usamos el checkpoint Stage 2 (ya domain-adapted) en lugar del LLaVA-Med base

**Ventaja esperada sobre MM-Skin:** Stage 2 ya entrenó en SkinCaRe (reportes dermatológicos), por lo que el LoRA de clasificación parte de representaciones más específicas del dominio → debería converger antes y a mejor resultado.

### 6.3 MAKE (Multi-Aspect Knowledge, 49.29% ZS promedio 8 datasets)

**Técnica clave:** Descomposición del conocimiento clínico en aspectos (terminología, descriptores visuales, síntomas) para prompting enriquecido.

**Aplicable a nuestros modelos:**
- Mejorar los sinónimos y prompts cerrados en `vlm_scoring.py` con terminología más rica
- Agregar prompts con descriptores morfológicos específicos (e.g., "lesión con bordes irregulares, variación de color, diámetro > 6mm" para MEL)
- Incluible en T2 (CoT prompting) como contexto inicial

**Implementación en `vlm_scoring.py`:** Extender `CLASS_SYNONYMS` con descriptores ABCDE para cada clase.

### 6.4 MpoxVLM (Dual encoder, 90.38% binario)

**Técnica clave:** Encoder visual específico de tarea paralelo al CLIP general.

**Aplicable:** T4 (Dual encoder). El ConvNeXt-Tiny entrenado en HAM10000 (Fase 1) es el candidato natural para el segundo encoder.

**Limitación:** Solo viable en Mendieta (24GB) por el costo de VRAM.

---

## 7. Archivos clave existentes

| Archivo | Rol |
|---------|-----|
| `src/evaluation/vlm_scoring.py` | Likelihood scoring, sinónimos, `ABCDE_FEATURES`, `COT_PROMPT`, `PROMPT_TEMPLATES` |
| `scripts/train_vlm_classify.py` | Script principal de evaluación (generate + likelihood + cot) |
| `src/models/llava_med.py` | Modelo LLaVA-Med, método `generate()` |
| `src/models/mini_vlm.py` | Modelo Mini-VLM, método `generate()` |
| `slurm/toko/vlm_classify_llava.sh` | Job TOKO LLaVA-Med base — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/toko/vlm_classify_mini.sh` | Job TOKO Mini-VLM base — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/toko/vlm_classify_llava_ft.sh` | Job TOKO LLaVA-Med fine-tuned — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/toko/vlm_classify_mini_ft.sh` | Job TOKO Mini-VLM fine-tuned — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/mendieta/vlm_classify_llava.sh` | Job Mendieta LLaVA-Med base — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/mendieta/vlm_classify_mini.sh` | Job Mendieta Mini-VLM base — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/mendieta/vlm_classify_llava_ft.sh` | Job Mendieta LLaVA-Med fine-tuned — soporta `METHOD={generate,likelihood,cot}` |
| `slurm/mendieta/vlm_classify_mini_ft.sh` | Job Mendieta Mini-VLM fine-tuned — soporta `METHOD={generate,likelihood,cot}` |
| `scripts/toko/submit.py` | Submit TOKO: jobs `*_lik`, `*_cot`, grupos `all_classify_lik`, `all_classify_cot` |
| `scripts/mendieta/submit.py` | Submit Mendieta: jobs `*_lik`, `*_cot`, grupos `all_classify_lik`, `all_classify_cot` |
| `configs/llava_med_stage2.yaml` | Config Stage 2 actual |
| `configs/mini_vlm_stage2.yaml` | Config Stage 2 actual |

---

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| T1 no mejora significativamente sobre generate | Revisar implementación de likelihood; verificar que los prefijos de prompt sean correctos por modelo |
| T3 LoRA-cls interfiere con capacidad de generación de reportes | Usar rank bajo (r=8); evaluar reportes antes y después del LoRA-cls |
| T3 sobreajusta a clases mayoritarias de HAM | Aplicar class weights o focal loss en el CE de clasificación |
| T4 excede VRAM de A30 (24GB) | Usar QLoRA (4-bit) para el LLM; mantener CLIP y ConvNeXt en fp16 |
| T5 GRPO desestabiliza el modelo | Ejecutar con KL penalty alta (β=0.1); monitorear entropy del policy |
| Checkpoint Stage 2 no disponible cuando se necesite T3 | Asegurarse de que Stage 2 esté completo y descargado antes de iniciar v3 |

---

## 9. Estado de implementación y próximos pasos

### v2 — Completado (T1 + T2)

T1 y T2 están implementados y encolados en ambos clusters. Los 8 jobs por cluster cubren la tabla 2×3 ({base, ft} × {generate, likelihood, cot}).

```bash
# Enviar todos los jobs de T1 + T2 (una sola vez por cluster)
python scripts/toko/submit.py all_classify_lik && python scripts/toko/submit.py all_classify_cot
python scripts/mendieta/submit.py all_classify_lik && python scripts/mendieta/submit.py all_classify_cot

# Monitorear
python scripts/toko/monitor.py
python scripts/mendieta/monitor.py

# Bajar resultados cuando terminen
python scripts/toko/sync_down.py
python scripts/mendieta/sync_down.py
```

### v3 — Pendiente (T3: LoRA classification adapter)

**Condición de inicio:** si el mejor resultado de T1+T2 no supera F1 ≥ 0.55 en HAM10000.

**Archivos a crear:**
- `configs/vlm_classify_lora.yaml` — hiperparámetros del LoRA de clasificación
- `scripts/train_vlm_classify_lora.py` — script de fine-tuning para clasificación
- `slurm/toko/vlm_cls_lora_llava.sh` y `vlm_cls_lora_mini.sh` — jobs SLURM

### v4/v5 — Condicionales (T4: dual encoder, T5: GRPO/RL)

Implementar solo si T3 no alcanza F1 ≥ 0.60. Ver secciones 3.4 y 3.5.

---

## 10. Referencias

- Yue et al. (2025). *Skin-R1: Toward Trustworthy Clinical Reasoning for Dermatological Diagnosis*. arXiv.
- Ye et al. (2025). *MM-Skin: Enhancing Dermatology Vision-Language Model with an Image-Text Dataset Derived from Textbooks*. arXiv.
- Zhu et al. (2024). *MpoxVLM: A Vision-Language Model for Diagnosing Skin Lesions from Mpox Virus Infection*. arXiv.
- Jin et al. (2024). *MAKE: Multi-Aspect Knowledge-Enhanced Vision-Language Pretraining for Zero-shot Dermatological Assessment*. arXiv.
