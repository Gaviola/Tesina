# Cambios — Clasificación de Lesiones con VLMs

Documento técnico que describe los cambios introducidos para mejorar la clasificación de lesiones dermatoscópicas (HAM10000, 7 clases) con LLaVA-Med y Mini-VLM (Phi-3.5-vision), cuyos resultados previos mostraban colapso a una única clase tanto en zero-shot como tras fine-tuning.

---

## 1. Motivación

### 1.1 Diagnóstico del problema

En la evaluación previa de Fase 1 (ver `Codigo/INFORME_TECNICO.md` §4.4), los VLMs presentaron un fenómeno de **colapso de clase** al clasificar:

| Modelo               | Accuracy | Clase dominante predicha            |
|----------------------|---------:|-------------------------------------|
| LLaVA-Med zero-shot  |  11.44 % | MEL en 1.450/1.503 imágenes (96.5 %) |
| LLaVA-Med fine-tuned |  11.11 % | MEL en 1.503/1.503 imágenes (100 %)  |
| Mini-VLM zero-shot   |   5.12 % | BCC en 1.484/1.503 imágenes (98.7 %) |
| Mini-VLM fine-tuned  |  11.18 % | MEL en 1.500/1.503 imágenes          |

Los clasificadores tradicionales, en contraste, alcanzaron accuracy de 52.3 % (DenseNet121) y 63.1 % (ViT-B/16). El accuracy de los VLMs coincide con la frecuencia a priori de la clase dominante, indicando que el modelo aprende esencialmente a ignorar la imagen.

### 1.2 Análisis de causas raíz

El pipeline original funciona así:

1. Para cada imagen, se envía el prompt:
   ```
   Classify this dermoscopic image into one of the following categories:
   MEL, NV, BCC, AKIEC, BKL, DF, VASC.
   Respond with only the category label.
   ```
2. El modelo ejecuta `generate(do_sample=False)` → respuesta autoregresiva greedy.
3. Se parsea la respuesta con regex buscando una de las 7 etiquetas.

Causas del colapso identificadas:

- **Desalineación del checkpoint**: los modelos fine-tuneados en Fase 2 (Stage 2 con LoRA) fueron entrenados para **generación de reportes** con SkinCaRe, no para clasificación de etiqueta única. Usarlos para clasificación es out-of-distribution. El fine-tuning reforzó el colapso al concentrar aún más la masa probabilística en narrativas específicas.
- **Greedy determinístico**: `do_sample=False` selecciona siempre el token de mayor probabilidad. Si el prior del modelo favorece "melanoma" (clase más discutida en literatura médica), toda imagen recibe esa respuesta.
- **Sesgo de tokenización**: etiquetas como `MEL`, `NV`, `DF` son 1 token; `AKIEC` son 3-4 tokens; `VASC` son 2-3. La probabilidad multiplicativa penaliza a las clases con más tokens.
- **Paradigma inadecuado**: los VLMs están entrenados para generación libre, no para clasificación de etiqueta discreta. Forzar esa forma de respuesta va contra su distribución de entrenamiento.

Un indicador directo de esto es que la **consistencia diagnóstica** medida en los reportes generados (Nivel 2 de evaluación) fue 71.47 % para LLaVA-Med y 31.34 % para Mini-VLM — muy superior al 11 % de accuracy de clasificación. Los modelos saben el diagnóstico correcto en un reporte; el problema está en cómo se lo consultamos.

---

## 2. Solución — Likelihood Scoring con Ensemble de Prompts

### 2.1 Idea central

En vez de pedir al modelo que **genere** la etiqueta y parsear su respuesta, le calculamos directamente `P(clase | imagen, prompt)` para cada una de las 7 clases y elegimos el argmax.

Esto convierte la tarea de generación abierta a clasificación cerrada por construcción:

- No hay bucle autoregresivo → no hay "greedy trap" que lleve a colapso.
- Todas las clases se comparan simultáneamente con el mismo prompt → la decisión es una comparación explícita, no una proyección implícita del prior.
- UNKNOWN desaparece: siempre hay una clase con mayor score.

### 2.2 Tres refinamientos

1. **Length normalization**. Dado que clases tienen distinta cantidad de tokens, la suma de log-probs las haría incomparables. Dividimos por número de tokens de la completion:
   ```
   score(clase) = Σ log P(token_i | contexto) / num_tokens
   ```

2. **Multi-sinónimo con agregación por max**. Cada clase tiene 3 sinónimos clínicos. Scoreamos cada uno; el score de la clase es el máximo. Esto permite que el modelo elija la forma verbal que conoce mejor y mitiga los sesgos de tokenización residuales:

   ```python
   CLASS_SYNONYMS = {
       "MEL":   ["melanoma", "malignant melanoma", "MEL"],
       "NV":    ["melanocytic nevus", "nevus", "mole"],
       "BCC":   ["basal cell carcinoma", "basal cell", "BCC"],
       "AKIEC": ["actinic keratosis", "intraepithelial carcinoma", "AKIEC"],
       "BKL":   ["benign keratosis", "seborrheic keratosis", "solar lentigo"],
       "DF":    ["dermatofibroma", "fibrous histiocytoma", "DF"],
       "VASC":  ["vascular lesion", "angioma", "VASC"],
   }
   ```

3. **Ensemble de 4 prompts** (2 abiertos + 2 cerrados). Reduce la sensibilidad al fraseo particular del prompt y permite medir el efecto del framing abierto vs. cerrado como ablación:

   ```python
   PROMPT_TEMPLATES = {
       "O1": "What is the most likely diagnosis for this dermoscopic image?",
       "O2": "Identify the type of skin lesion shown in this image.",
       "C1": ("Given this dermoscopic image, the diagnosis among melanoma, "
              "melanocytic nevus, basal cell carcinoma, actinic keratosis, "
              "benign keratosis, dermatofibroma, or vascular lesion is"),
       "C2": ("Select the correct diagnosis from: melanoma, melanocytic "
              "nevus, basal cell carcinoma, actinic keratosis, benign "
              "keratosis, dermatofibroma, vascular lesion. Answer:"),
   }
   ```

   Score final por clase: media de scores length-normalized sobre los 4 prompts. Argmax → predicción ensemble.

### 2.3 Algoritmo en pseudocódigo

Para una imagen `img`:

```
for prompt_id, prompt_text in PROMPT_TEMPLATES.items():
    prefix = build_chat_template(vlm_name, prompt_text)
    for class_code, synonyms in CLASS_SYNONYMS.items():
        for synonym in synonyms:
            # Teacher-forcing: un único forward pass.
            full_text = prefix + synonym
            logits = model(image, full_text).logits
            logp = sum(log_softmax(logits[t-1])[input_ids[t]]
                       for t in completion_positions)
            score_per_synonym = logp / num_completion_tokens
        score[prompt_id][class_code] = max(score_per_synonym for synonym)

ensemble_score[class_code] = mean(score[p][class_code] for p in prompts)
pred = argmax(ensemble_score)
```

### 2.4 Costo computacional

Por imagen: 4 prompts × 7 clases × 3 sinónimos = **84 forwards teacher-forced** (cada uno de ~60-100 tokens, no autoregresivo).

Comparación vs. el método `generate` original:
- Generate: 32 pasos autoregresivos por imagen ≈ 48 k forwards sobre 1503 imágenes.
- Likelihood: 84 × 1503 = 126 k forwards teacher-forced (cada uno ~3× más barato que un paso autoregresivo con KV-cache ya construido, por el paralelismo del forward sobre la secuencia completa).

Net: el tiempo total es comparable o ligeramente inferior al método generate para LLaVA-Med. Para Mini-VLM (que procesa `batch_size=1` por limitación de `apply_chat_template`), el tiempo es algo mayor pero cabe en la ventana SLURM de 4 h.

---

## 3. Diseño experimental — Tabla 2×2

Para cuantificar por separado la mejora del **método de inferencia** vs. la mejora del **fine-tuning**, se ejecutan los 4 cuadrantes:

|          | `--method generate`                    | `--method likelihood`                   |
|----------|----------------------------------------|-----------------------------------------|
| **base** (zero-shot) | baseline original del INFORME | aislado el efecto del método |
| **fine-tuned** (Stage 2) | checkpoint Stage 2 + parse | checkpoint Stage 2 + likelihood |

Esto permite atribuir la mejora a:
- Solo el método (base × likelihood > base × generate)
- Solo el fine-tuning (ft × generate > base × generate)
- Interacción (ft × likelihood vs. suma de efectos individuales)

Y adicionalmente, el JSON de cada run de likelihood contiene predicciones por prompt individual, lo que habilita:
- Accuracy por prompt (`O1`, `O2`, `C1`, `C2`) para medir el efecto del framing
- Análisis de confianza y calibración post-hoc desde la matriz completa de log-probs
- Ablación "dejar un prompt fuera" sin re-ejecutar los jobs

---

## 4. Archivos introducidos o modificados

### 4.1 Nuevo módulo de scoring

**`Codigo/src/evaluation/vlm_scoring.py`** (nuevo)

Contiene:
- `CLASS_SYNONYMS`: dict de sinónimos por clase.
- `PROMPT_TEMPLATES`: dict de los 4 prompts del ensemble.
- `score_class(vlm, vlm_name, image, prompt_text, class_code, length_normalize)`: score de una clase bajo un prompt, agregando sinónimos por max.
- `score_image(vlm, vlm_name, image, class_codes, prompts, length_normalize, keep_synonym_details)`: función principal, retorna matriz completa de log-probs, predicciones por prompt y ensemble.

### 4.2 Script de clasificación extendido

**`Codigo/scripts/train_vlm_classify.py`** (modificado)

- Nuevo argumento `--method {generate, likelihood}` (default `generate`).
- Nueva función `run_likelihood_eval(...)` que itera el test set y llama `score_image` por imagen.
- Soporte de `--dry-run` para el método likelihood: procesa N imágenes y reporta VRAM, velocidad, distribución de predicciones y ETA completo.
- Argumento adicional `--keep_synonym_details` para guardar logprobs por sinónimo individual (debug).
- Archivos de salida separados: sufijo `_likelihood` (zero-shot) o `_likelihood_finetuned` (con `--checkpoint`).

### 4.3 Scripts SLURM parametrizables

Cada uno de los 4 scripts de clasificación SLURM ahora lee `METHOD=${METHOD:-generate}` del ambiente y lo pasa a Python. Reutilizan los mismos archivos; la variante `likelihood` se activa desde `submit.py` sin duplicar archivos:

- `Codigo/slurm/mendieta/vlm_classify_llava.sh`
- `Codigo/slurm/mendieta/vlm_classify_mini.sh`
- `Codigo/slurm/mendieta/vlm_classify_llava_ft.sh`
- `Codigo/slurm/mendieta/vlm_classify_mini_ft.sh`

### 4.4 Submit con nuevas entradas

**`Codigo/scripts/mendieta/submit.py`** (modificado)

Nuevas entradas:
- `classify_llava_lik`, `classify_mini_lik`: likelihood sobre el modelo base.
- `classify_llava_ft_lik`, `classify_mini_ft_lik`: likelihood sobre el modelo fine-tuned.
- Grupo `all_classify_lik`: envía los 4 jobs de likelihood.

Todas usan tuplas `(script, {"METHOD": "likelihood"})` aprovechando el soporte existente de variables de entorno de `submit_job()`.

### 4.5 Documentación

- **`Codigo/subir_mendieta.md`**: sección de dry-run para likelihood + tabla con nombres de archivos de salida del 2×2.
- **`Codigo/cambios_clasificacion_vlms.md`**: este documento.

---

## 5. Uso paso a paso

### 5.1 Validación local (dry-run)

Antes de enviar al cluster, verificar que el pipeline corre y la distribución de predicciones no colapsa:

```bash
# Zero-shot (sin ckpt; ~5 min local en RTX 4070)
python scripts/train_vlm_classify.py --model mini_vlm --method likelihood --dry-run
python scripts/train_vlm_classify.py --model llava_med --method likelihood --dry-run --dry-run-batches 20

# Con checkpoint fine-tuned (solo si está descargado localmente)
python scripts/train_vlm_classify.py --model llava_med --method likelihood --dry-run \
    --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt
```

El resumen reporta:
- Distribución de predicciones ensemble por clase (alarma si >80 % en una sola).
- VRAM pico y headroom.
- Velocidad (imágenes/segundo) y tiempo total estimado.
- Primeras 5 muestras con `true`, `pred_ensemble` y `pred_per_prompt`.

### 5.2 Envío al cluster

Asumiendo que `all_classify` y `all_classify_ft` (método `generate`) ya produjeron resultados en `outputs/results/`:

```bash
# Subir cambios de codigo
python scripts/mendieta/sync_up.py

# Lanzar los 4 jobs de likelihood (2x2 completo de likelihood)
python scripts/mendieta/submit.py all_classify_lik

# Monitorear
python scripts/mendieta/monitor.py
python scripts/mendieta/monitor.py <JOBID>  # tail del log

# Bajar resultados cuando terminen
python scripts/mendieta/sync_down.py
```

O jobs individuales si se prefiere:
```bash
python scripts/mendieta/submit.py classify_llava_lik      # base, ~4 h
python scripts/mendieta/submit.py classify_mini_lik       # base, ~4 h
python scripts/mendieta/submit.py classify_llava_ft_lik   # ft,   ~4 h
python scripts/mendieta/submit.py classify_mini_ft_lik    # ft,   ~4 h
```

### 5.3 Archivos de salida

Al terminar un job de likelihood, en `Codigo/outputs/results/`:

- `{model}_likelihood[_finetuned]_predictions.json`:
  - `y_true`, `y_pred` (argmax ensemble), `y_pred_per_prompt` (N × 4)
  - `logp_matrix` (N × 4 × 7) — todas las log-probs length-normalized
  - `prompts`, `class_names`, `class_synonyms`
  - `image_ids`
- `{model}_likelihood[_finetuned]_test_results.json`:
  - Accuracy ensemble, F1 weighted, sens/spec macro y por clase
  - Matriz de confusión
  - `per_prompt_accuracy`: dict `{O1: ..., O2: ..., C1: ..., C2: ...}`

### 5.4 Análisis post-hoc

Los notebooks de análisis (`notebooks/01_results_phase1.ipynb`) pueden leer los nuevos JSONs directamente y generar tablas de comparación. El archivo `logp_matrix` permite por ejemplo:
- Construir curvas de confianza vs. accuracy.
- Analizar qué prompt acierta más por clase (ganancia potencial si se usa un ensemble ponderado).
- Probar "dejar un prompt fuera" para medir contribución marginal.

---

## 6. Decisiones de diseño — por qué estas elecciones

| Decisión | Alternativas consideradas | Razón |
|----------|---------------------------|-------|
| Likelihood scoring | Prompt engineering, constrained decoding, parsear diagnóstico del reporte generado | Estándar para clasificación cerrada con VLMs (SLAKE-VQA, MedBench). Evita colapso por construcción, no requiere re-entrenar. |
| Sinónimos con `max` | Tomar un único nombre canónico; promedio de sinónimos | Max reduce sensibilidad a qué forma verbal "conoce mejor" el modelo sin diluir señal. Promedio penaliza clases cuyos sinónimos son dispares. |
| Length-normalize | Sin normalizar; normalización con potencia (α<1) | Normalización simple es lo que usa CLIP y LLaVA-Eval. α<1 agrega hiperparámetro sin ganancia clara. |
| 4 prompts (2+2) | Uno solo; 3 abiertos + 3 cerrados (6) | 4 es el mínimo para medir balance abierto-vs-cerrado. Cada prompt agrega ~25 % del costo. |
| Prompt cerrado listando las 7 clases | Formato multiple-choice con A/B/C; descripción morfológica por clase | Alinea el prompt con la tarea cerrada sin introducir nueva tokenización (A/B/C) que el modelo no conoce. |
| Guardar matriz completa de log-probs | Solo accuracy final; solo predicciones por prompt | 2 MB por run, habilita todos los análisis post-hoc sin re-ejecutar (slow, cuota-limitado). |
| Parametrización por `METHOD` env var | Scripts SLURM duplicados | Reutiliza el patrón existente (`DATASETS` en `generate_reports_*.sh`). No duplica archivos. |

---

## 7. Limitaciones y trabajo futuro

1. **Batch sincero de scoring**. La implementación procesa `(prompt, clase, sinónimo)` de forma secuencial. Se puede batchar dentro de una misma imagen (21 completions en paralelo → ~10× speed-up en LLaVA-Med). No implementado para mantener el código simple; si el tiempo es un bloqueo, agregar en una segunda iteración.

2. **Mini-VLM con batch size 1**. Phi-3.5-vision fuerza `batch_size=1` por limitaciones del chat template. El scoring hereda esa limitación. Una optimización futura sería generar las 21 completions via `batch_encode_plus` + padding left.

3. **Sinónimos fijos**. El conjunto de sinónimos se fijó manualmente. Un sweep ligero podría buscar cuáles sinónimos contribuyen más (e.g. `"mole"` vs `"melanocytic nevus"` podría variar por modelo).

4. **Sin calibración de temperatura**. Las log-probs del modelo pueden estar mal calibradas; aplicar temperature scaling sobre los scores podría mejorar la separabilidad, pero requiere un set de validación separado.

5. **El método solo aplica a clasificación cerrada**. Para tareas abiertas (generación de reportes) el método `generate` sigue siendo el único viable. Esto es consistente con la separación Fase 1 / Fase 2 del proyecto.

---

*Documento creado el 2026-04-24 en el contexto de mejorar las métricas de clasificación VLM de la Fase 1 de la tesina.*
