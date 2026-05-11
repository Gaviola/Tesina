# Clasificación VLM — Resultados v2 (Likelihood + CoT)

**Fecha:** 2026-05-06/07  
**Cluster:** Mendieta (A30 24GB, CUDA 12.2)  
**Jobs SLURM:** 1151163–1151170  
**Dataset:** HAM10000 Test Set (n=1503, 7 clases)

---

## 1. Resumen de jobs ejecutados

| Job ID | Modelo | Método | ZS/FT | Estado |
|--------|--------|--------|-------|--------|
| 1151163 | LLaVA-Med | likelihood | ZS | Completado |
| 1151164 | Mini-VLM | likelihood | ZS | Completado |
| 1151165 | LLaVA-Med | likelihood | FT | **CRASH** — LoRA rank mismatch |
| 1151166 | Mini-VLM | likelihood | FT | Completado |
| 1151167 | LLaVA-Med | CoT | ZS | Completado |
| 1151168 | Mini-VLM | CoT | ZS | Completado |
| 1151169 | LLaVA-Med | CoT | FT | **CRASH** — LoRA rank mismatch |
| 1151170 | Mini-VLM | CoT | FT | Completado |

---

## 2. Resultados completos

### 2.1 Tabla comparativa (HAM10000 Test Set, n=1503)

| Modelo | Método | ZS/FT | Acc | F1-w | Sens. macro | Spec. macro |
|--------|--------|-------|-----|------|------------|------------|
| LLaVA-Med | generate ★ | ZS | 0.1144 | 0.030 | — | — |
| Mini-VLM | generate ★ | ZS | 0.0512 | 0.006 | — | — |
| LLaVA-Med | likelihood | ZS | 0.0366 | 0.028 | 0.157 | 0.856 |
| Mini-VLM | likelihood | ZS | 0.1890 | 0.268 | 0.181 | 0.871 |
| LLaVA-Med | likelihood | FT | — | — | — | — |
| **Mini-VLM** | **likelihood** | **FT** | **0.6660** | **0.536** | **0.142** | **0.857** |
| LLaVA-Med | CoT | ZS | 0.1023 | 0.019 | 0.143 | 0.857 |
| Mini-VLM | CoT | ZS | 0.0929 | 0.022 | 0.124 | 0.856 |
| LLaVA-Med | CoT | FT | — | — | — | — |
| Mini-VLM | CoT | FT | 0.1153 | 0.040 | 0.141 | 0.857 |

★ Resultados de la primera iteración (método `generate`, descritos en `vlm_clasificacion_v1_plan.md`).

### 2.2 Accuracy por prompt — método likelihood

| Modelo | ZS/FT | O1 | O2 | C1 | C2 |
|--------|-------|----|----|----|----|
| LLaVA-Med | ZS | 0.074 | 0.073 | 0.087 | 0.065 |
| Mini-VLM | ZS | 0.167 | **0.014** | 0.290 | **0.352** |
| Mini-VLM | FT | 0.536 | 0.110 | 0.371 | **0.570** |

**Observación crítica sobre Mini-VLM:** El prompt `O2` ("Identify the type of skin lesion shown in this image") obtiene accuracy casi nulo (1.4% ZS, 11% FT), mientras que los prompts cerrados `C1`/`C2` son los más efectivos. Esto indica que el framing abierto sin restricción de vocabulario es fuertemente perjudicial para Mini-VLM.

### 2.3 Tasa UNKNOWN — método CoT

| Modelo | ZS/FT | UNKNOWN | % |
|--------|-------|---------|---|
| LLaVA-Med | ZS | 223/1503 | 14.8% |
| Mini-VLM | ZS | 7/1503 | 0.5% |
| Mini-VLM | FT | 20/1503 | 1.3% |

LLaVA-Med no sigue el formato CoT en un 14.8% de los casos (el parseo `Final diagnosis:` falla). Mini-VLM sigue el formato casi perfectamente (≤1.3% UNKNOWN).

---

## 3. Análisis de problemas

### 3.1 CRASH crítico: LLaVA-Med FT (jobs 1151165 y 1151169)

**Error:** `RuntimeError: size mismatch for lora_A/lora_B weights` en `load_state_dict`.

**Causa raíz:** El checkpoint fine-tuneado de LLaVA-Med (Stage 2, `outputs/checkpoints/stage2_llava_med/best_model.pt`) fue entrenado con LoRA rank `r=16`. El código de carga actual inicializa el modelo con `r=64` antes de cargar el checkpoint, produciendo incompatibilidad de dimensiones:

```
Checkpoint:  lora_A.default.weight → torch.Size([16, 1024])
Modelo actual: lora_A.default.weight → torch.Size([64, 1024])
```

Este error afecta a todos los layers del vision tower (ViT-L/14) y del LLM (LLaMA-2 7B).

**Impacto:** No se tienen resultados de LLaVA-Med fine-tuned para ningún método. La mitad del 2×2 experimental ({LLaVA-Med FT} × {likelihood, CoT}) está vacío.

**Fix requerido:** Leer el rank del checkpoint guardado antes de inicializar el modelo LoRA:
```python
# En load_checkpoint o en llava_med.py:
ckpt = torch.load(checkpoint_path, map_location="cpu")
lora_r = ckpt.get("lora_r", 16)  # leer r del checkpoint
model = load_llava_med(lora_r=lora_r, ...)
model.load_state_dict(ckpt["model_state_dict"])
```
O alternativamente, guardar la config LoRA en el checkpoint al momento de entrenamiento y releerla al inferir.

### 3.2 LLaVA-Med likelihood ZS: degradación vs generate

LLaVA-Med likelihood ZS (Acc=0.037) rinde **peor** que generate ZS (Acc=0.114). Esto es contraintuitivo dado que el método likelihood elimina el greedy trap. Las causas probables:

1. **El tokenizador lento activa un path diferente** (`LlavaProcessor` construido manualmente por fallo de `AutoProcessor`). El tokenizador lento puede generar posiciones de completion distintas de las esperadas, corrompiendo el scoring por posición.
2. **Los log-probs del LLM de LLaVA-Med no son comparables entre sinónimos** — el modelo no fue entrenado en el dominio dermatoscópico para text completion, sino para VQA abierta. Los scores de completion son arbitrariamente pequeños y no reflejan preferencia real entre clases.
3. **Ensemble degenerado:** todos los prompts dan accuracy < 10%, sugiriendo que el ordenamiento por log-prob no captura señal visual útil en ningún framing.

### 3.3 Mini-VLM likelihood ZS: mejora real pero señal degenerada

Mini-VLM likelihood ZS sube de Acc=0.051 a Acc=0.189 — una mejora de +13.8 pt sobre generate. Sin embargo:

- La sensibilidad macro es 0.181, consistente con mayoría NV predicha (NV = 67% del test).
- El prompt O2 produce accuracy = 1.4%, indicando que el modelo colapsa a una clase para ese framing.
- Los prompts cerrados (C1=0.290, C2=0.352) superan a los abiertos, confirmando que la restricción de vocabulario ayuda.

### 3.4 Mini-VLM likelihood FT: resultado más prometedor pero acc ≠ capacidad diagnóstica

Mini-VLM FT likelihood es el mejor resultado: Acc=0.666, F1=0.536. Sin embargo:

- **Sensibilidad macro = 0.142** — similar a una predicción aleatoria por clase (1/7 ≈ 0.143). Esto indica colapso severo hacia la clase NV (67% del test).
- La accuracy de 0.666 es consistente con predecir siempre NV: 1006/1503 = 0.669.
- El prompt O2 (0.110) confirma que para ese framing el modelo predice casi siempre una sola clase.
- El fine-tuning Stage 2 (orientado a generación de reportes) introduce un prior hacia "melanocytic nevus" al hacer likelihood scoring, posiblemente porque NV es la clase más común en los datos de entrenamiento SkinCaRe.

**Diagnóstico de colapso:** La probabilidad `P(texto | imagen, prompt)` es alta para los sinónimos de NV porque NV domina los reportes del corpus de entrenamiento. El Stage 2 reinforzó este bias al entrenar en SkinCaRe donde NV es la clase más frecuente.

### 3.5 CoT: sin mejora sobre likelihood, alto costo

CoT ZS para ambos modelos rinde peor que likelihood en accuracy y F1. CoT FT para Mini-VLM también es peor que likelihood FT. Causas:

- **LLaVA-Med ZS:** 14.8% de respuestas no parseable — el modelo no sigue el formato "Final diagnosis:" con consistencia. Las métricas excluyen UNKNOWN pero la distribución de los 1280 parseados sigue siendo degenerada.
- **Mini-VLM ZS:** Accuracy = 0.093 < likelihood 0.189 — el razonamiento paso a paso no ayuda cuando el modelo base no tiene conocimiento dermatológico suficiente para generar features descriptivas útiles.
- **Mini-VLM FT CoT:** El Stage 2 fue entrenado para generar reportes SkinCaRe (que tienen estructura propia), no para seguir el formato ABCDE + "Final diagnosis:". El modelo genera texto plausible pero el campo "Final diagnosis:" no correlaciona con la imagen.

---

## 4. Comparación global: VLMs vs clasificadores supervisados

| Modelo | Método | Acc HAM | F1-w HAM |
|--------|--------|---------|---------|
| **DenseNet121 legacy** | supervisado | **0.846** | **0.852** |
| **ViT-B/16 legacy** | supervisado | **0.858** | **0.862** |
| ConvNeXt-Tiny modern v3 | supervisado | 0.819 | 0.846 |
| Swin-Tiny modern v3 | supervisado | 0.795 | 0.816 |
| Mini-VLM FT | likelihood | 0.666 | 0.536 |
| Mini-VLM ZS | likelihood | 0.189 | 0.268 |
| LLaVA-Med ZS | CoT | 0.102 | 0.019 |
| Mini-VLM ZS | CoT | 0.093 | 0.022 |
| LLaVA-Med ZS | likelihood | 0.037 | 0.028 |
| Mini-VLM ZS | generate | 0.051 | 0.006 |
| LLaVA-Med ZS | generate | 0.114 | 0.030 |

Los clasificadores supervisados superan a todos los VLMs por un margen amplio. El mejor VLM (Mini-VLM FT likelihood) está 19 puntos por debajo del DenseNet legacy en accuracy y 32 puntos en F1.

---

## 5. Errores específicos de implementación identificados

| Error | Descripción | Fix necesario |
|-------|-------------|---------------|
| **LoRA rank mismatch** (jobs 1151165, 1151169) | El checkpoint Stage 2 de LLaVA-Med tiene r=16 pero el model init usa r=64 | Guardar y releer `lora_r` del checkpoint antes de inicializar el modelo |
| **Prompt O2 degenerado en Mini-VLM** | "Identify the type of skin lesion shown in this image" → colapso a clase única | Remover O2 del ensemble o reemplazar por prompt más informativo |
| **Sensibilidad macro ≈ 1/7 en FT likelihood** | El Stage 2 introduce prior hacia NV en los log-probs | Requiere T3 (LoRA classification adapter) para desacoplar el prior de clasificación del de generación |
| **CoT UNKNOWN rate en LLaVA-Med (14.8%)** | El parseo `Final diagnosis:` falla frecuentemente | Mejorar el regex de parseo o ajustar el formato del prompt |

---

## 6. Narrativa para la tesina

Los resultados de la iteración v2 confirman las limitaciones estructurales de usar VLMs para clasificación directa:

1. **El método de scoring importa, pero no es suficiente.** Likelihood scoring mejoró significativamente sobre `generate` para Mini-VLM ZS (+13.8 pt). Para LLaVA-Med ZS, el método empeoró los resultados por incompatibilidades en el pipeline de tokenización.

2. **El fine-tuning Stage 2 ayuda en un caso específico.** Mini-VLM FT likelihood alcanzó Acc=0.666, el mejor resultado VLM hasta ahora. Sin embargo, la sensibilidad macro = 0.142 revela que este "resultado" es esencialmente colapso hacia NV (la clase mayoritaria), no clasificación discriminativa real.

3. **CoT no aporta sobre likelihood.** Sin un entrenamiento previo en razonamiento diagnóstico estructurado (como Skin-R1), el chain-of-thought genera texto clínico superficialmente plausible pero sin correlación con la imagen real.

4. **La hipótesis de desalineación se confirma.** Los checkpoints Stage 2 fueron entrenados para generación de reportes, no para clasificación. El likelihood scoring con esos checkpoints hereda el prior lingüístico del corpus de entrenamiento (SkinCaRe) donde NV es dominante.

---

## 7. Próximos pasos recomendados

### 7.1 Fix urgente — LoRA rank mismatch en LLaVA-Med FT

Corregir la carga del checkpoint para leer `lora_r` dinámicamente. Sin este fix, todos los experimentos FT de LLaVA-Med seguirán fallando. La corrección es de una línea en `src/utils/io.py` o `src/models/llava_med.py`.

```python
# En load_checkpoint (src/utils/io.py):
ckpt = torch.load(path, map_location="cpu")
if "lora_config" in ckpt:
    # Re-init model con el rank correcto antes de cargar pesos
    lora_r = ckpt["lora_config"].get("r", 16)
    # pasar lora_r al constructor del modelo
```

### 7.2 Re-ejecutar LLaVA-Med FT likelihood y CoT

Después del fix, re-correr jobs 1151165 y 1151169 equivalentes. Estimado: 6h cada uno en Mendieta.

### 7.3 Decidir si continuar con T3 (LoRA classification adapter)

Según el plan en `vlm_clasificacion_v2_plan.md`, la condición de inicio de T3 es:
> Si el mejor resultado de T1+T2 no supera F1 ≥ 0.55 en HAM10000

Mini-VLM FT likelihood tiene F1=0.536 — muy cerca del umbral pero con sensibilidad macro 0.142 (colapso hacia NV). Dado que el "resultado" es artificialmente inflado por el prior NV, se recomienda **continuar con T3** para obtener clasificación real.

**Alternativa conservadora antes de T3:** reducir el ensemble a solo prompts cerrados (C1, C2) y evaluar si el ensemble de 2 prompts con Mini-VLM FT da mejores resultados ajustados por clase (sin O2 degenerado). Costo: re-ejecutar un job rápido.

### 7.4 Para la narrativa de la tesina

El gap VLM-clasificador es ahora claro y cuantificado:
- Mejor clasificador: ViT-B/16 legacy, F1=0.862
- Mejor VLM: Mini-VLM FT likelihood, F1=0.536 (pero con colapso de clase)
- Gap real: ~30 puntos F1

Este gap motiva la pregunta de si los VLMs compensan en otras dimensiones (calidad del reporte, razonamiento clínico, generalización OOD). Los resultados de reportes (`reportes_resul_v1.md`) son el contraargumento necesario.

---

## 8. Archivos de salida

En `outputs/results/` (en el cluster, pendientes de `sync_down`):

| Archivo | Modelo | Método |
|---------|--------|--------|
| `llava_med_likelihood_predictions.json` | LLaVA-Med | likelihood ZS |
| `llava_med_likelihood_test_results.json` | LLaVA-Med | likelihood ZS |
| `mini_vlm_likelihood_predictions.json` | Mini-VLM | likelihood ZS |
| `mini_vlm_likelihood_test_results.json` | Mini-VLM | likelihood ZS |
| `mini_vlm_likelihood_finetuned_predictions.json` | Mini-VLM | likelihood FT |
| `mini_vlm_likelihood_finetuned_test_results.json` | Mini-VLM | likelihood FT |
| `llava_med_cot_predictions.json` | LLaVA-Med | CoT ZS |
| `llava_med_cot_test_results.json` | LLaVA-Med | CoT ZS |
| `mini_vlm_cot_predictions.json` | Mini-VLM | CoT ZS |
| `mini_vlm_cot_test_results.json` | Mini-VLM | CoT ZS |
| `mini_vlm_cot_finetuned_predictions.json` | Mini-VLM | CoT FT |
| `mini_vlm_cot_finetuned_test_results.json` | Mini-VLM | CoT FT |

Los archivos de LLaVA-Med FT no existen por los crashes.

---

*Resultados ejecutados el 2026-05-06/07 en el cluster Mendieta (A30 24GB, CUDA 12.2, nodos ivb).*
