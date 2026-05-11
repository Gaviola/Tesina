# Plan de Implementación — Mejoras a Generación de Reportes Clínicos

**Fecha:** 2026-05-03
**Estado:** Pendiente de ejecución
**Documento base:** [reportes_resul_1.md](../resul/reportes_resul_1.md)
**Modelos afectados:** LLaVA-Med 7B + LoRA (r=64), Mini-VLM (CLIP ViT-B/16 + Phi-3-mini) + LoRA (r=64)

---

## 1. Contexto

A partir del análisis de resultados de la primera generación de reportes (ver [reportes_resul_1.md](../resul/reportes_resul_1.md)) se identificaron 7 problemas (P1–P7) y 12 mejoras agrupadas en 3 niveles:

- **Nivel A:** sin reentrenamiento (4 mejoras) — días
- **Nivel B:** con reentrenamiento (4 mejoras) — semanas
- **Nivel C:** cambios de arquitectura (4 mejoras) — meses

Este documento ordena los pasos de implementación según **prioridad = impacto / costo** y aporta los detalles técnicos necesarios para ejecutarlos.

---

## 2. Orden de implementación recomendado

| Prio | ID | Mejora | Tipo | Costo | Riesgo |
|------|-----|--------|------|-------|--------|
| 1 | A2 | Normalización de etiquetas SkinCaRe | Métricas | 1–2 h | Bajo |
| 2 | A1 | Alinear prompt de inferencia con Stage 1 | Inferencia | 2 h | Bajo |
| 3 | A4 | Completar evaluación LLaVA-Med en MM-SkinQA | Inferencia | 4–6 h GPU | Bajo |
| 4 | A3 | Evaluar sobre MM-Skin test split | Eval / SOTA | 1 día GPU | Bajo |
| 5 | C4 | LLM-as-Judge para evaluación clínica | Métricas | 1 día | Bajo (costo API) |
| 6 | C2 | Pérdida auxiliar de entidades clínicas | Entrenamiento | 3–5 días | Medio |
| 7 | B3 | Alinear instrucción de Stage 1 con Stage 2 | Entrenamiento | 1 día | Bajo |
| 8 | B2 | Aumentar épocas de Stage 2 | Entrenamiento | 2–3 días GPU | Bajo |
| 9 | B1 | Mezclar SkinCoT + reportes estructurados | Datos+Train | 1 sem | Medio |
| 10 | B4 | Sweep ampliado (LoRA r=128, más capas) | Entrenamiento | 1 sem | Medio |
| 11 | C3 | Adaptación de dominio con HIBA | Datos+Train | 2 sem | Alto |
| 12 | C1 | Vision encoder ViT-L/14 para Mini-VLM | Arquitectura | 3 sem | Alto |

**Criterio de orden:**
- Primero las correcciones de medición (A2, A1, A4, A3, C4): permiten saber el verdadero punto de partida antes de invertir en reentrenar.
- Luego las mejoras de entrenamiento de menor a mayor riesgo (C2, B3, B2, B1, B4).
- Por último los cambios estructurales (C3, C1) que requieren mayor esfuerzo y pueden invalidar trabajos previos.

---

## 3. Detalle técnico por mejora

### 3.1 [Prio 1] A2 — Normalización de etiquetas SkinCaRe

**Problema (P5):** El campo `gt_label` de SkinCaRe contiene nombres de carpeta (`"Eczema Photos"`, `"Light Diseases and Disorders of Pigmentation"`, etc.), no terminología médica, lo que provoca diagnostic consistency ≈ 0%.

**Implementación:**

1. Crear el archivo `Codigo/src/evaluation/label_normalization.py` con un mapeo de carpeta → lista de sinónimos médicos:

```python
SKINCARE_LABEL_SYNONYMS: dict[str, list[str]] = {
    "Eczema Photos": ["eczema", "atopic dermatitis", "dermatitis", "AD"],
    "Melanoma Skin Cancer Nevi and Moles": ["melanoma", "melanocytic nevus", "nevus", "mole"],
    "Psoriasis pictures Lichen Planus and related diseases": ["psoriasis", "lichen planus"],
    "Tinea Ringworm Candidiasis and other Fungal Infections": ["tinea", "ringworm", "candidiasis", "fungal infection", "dermatophytosis"],
    "Acne and Rosacea Photos": ["acne", "rosacea"],
    "Bullous Diseases Photos": ["bullous", "pemphigus", "pemphigoid"],
    "Cellulitis Impetigo and other Bacterial Infections": ["cellulitis", "impetigo", "bacterial infection"],
    "Exanthems and Drug Eruptions": ["exanthem", "drug eruption", "morbilliform"],
    "Herpes HPV and other STDs Photos": ["herpes", "HPV", "wart", "molluscum"],
    "Light Diseases and Disorders of Pigmentation": ["vitiligo", "melasma", "hyperpigmentation", "hypopigmentation"],
    "Lupus and other Connective Tissue diseases": ["lupus", "discoid lupus", "scleroderma"],
    "Nail Fungus and other Nail Disease": ["onychomycosis", "nail fungus", "paronychia"],
    "Poison Ivy Photos and other Contact Dermatitis": ["contact dermatitis", "poison ivy", "allergic dermatitis"],
    "Scabies Lyme Disease and other Infestations and Bites": ["scabies", "lyme disease", "insect bite"],
    "Seborrheic Keratoses and other Benign Tumors": ["seborrheic keratosis", "benign tumor", "skin tag"],
    "Systemic Disease": ["systemic", "vasculitis", "sarcoidosis"],
    "Urticaria Hives": ["urticaria", "hives"],
    "Vascular Tumors": ["hemangioma", "vascular tumor", "angioma"],
    "Vasculitis Photos": ["vasculitis", "purpura"],
    "Warts Molluscum and other Viral Infections": ["wart", "molluscum", "viral infection"],
}
```

2. Modificar `Codigo/src/evaluation/clinical_ner.py::diagnostic_consistency()` para aceptar el mapping:

```python
def diagnostic_consistency(report: str, gt_label: str,
                           synonyms_map: dict[str, list[str]] | None = None) -> bool:
    report_lower = report.lower()
    if synonyms_map and gt_label in synonyms_map:
        candidates = synonyms_map[gt_label]
    else:
        candidates = [gt_label]
    return any(re.search(rf"\b{re.escape(c.lower())}\b", report_lower) for c in candidates)
```

3. Recalcular las métricas NER en `notebooks/02_results_phase2.ipynb` cargando el mapping para SkinCaRe y manteniéndolo vacío para HAM10000 y MM-SkinQA.

4. Persistir los nuevos resultados en `outputs/metrics_cache/ner_skincare_normalized.json` para conservar trazabilidad respecto del cálculo previo.

**Validación:** spot-check manual de 20 reportes — verificar que la normalización no produce falsos positivos por sinónimos demasiado generales (ej. "infection" matchea casi todo).

---

### 3.2 [Prio 2] A1 — Alinear prompt de inferencia con Stage 1

**Problema (P2):** El proyector MLP de Stage 1 se entrenó con `"Describe this skin lesion."` mientras que la inferencia usa un prompt estructurado más largo, lo que puede degradar la calidad de la representación visual proyectada al LLM.

**Implementación:**

1. Modificar `Codigo/scripts/generate_report.py:49-52` para soportar múltiples prompts:

```python
PROMPT_PRESETS = {
    "stage1": "Describe this skin lesion.",
    "stage2_short": "Describe the skin lesion in this image.",
    "structured": (
        "Describe this skin lesion with a structured clinical report that includes: "
        "findings, diagnostic impression, and differential diagnosis."
    ),
}
```

2. Añadir flag CLI `--prompt-preset` con default `"stage1"`. Persistir el prompt usado en cada JSON generado (ya se hace en línea 172 de `generate_report.py`).

3. Generar un set de comparación pequeño (n=200) con cada preset sobre HAM10000 y SkinCaRe para A/B test antes de regenerar todo:
   - `outputs/generated_reports_ab/{model}_{preset}/`
4. Recomputar métricas (NER + texto + cualitativo) sobre el A/B test y elegir el mejor preset.

5. Si el preset ganador difiere del actual, regenerar los reportes completos sobre los 3 datasets (~1 día GPU para los 4 jobs).

**Hipótesis a verificar:** el preset `stage1` mejora el entity recall y reduce las alucinaciones de Mini-VLM, a costa de menor estructura visible en el reporte.

---

### 3.3 [Prio 3] A4 — Completar evaluación LLaVA-Med en MM-SkinQA

**Problema (P7):** Solo se generaron 20 reportes de LLaVA-Med en MM-SkinQA, mientras que Mini-VLM completó 2.809. Diagnóstico estadísticamente no representativo.

**Implementación:**

1. Inspeccionar el log SLURM del job correspondiente (búsqueda en `outputs/logs/llava_med/`) para verificar si hubo un timeout, OOM, o un bug en el dataset loader.

2. Verificar que el split de MM-SkinQA es idéntico para ambos modelos. El loader está en `Codigo/src/data/mm_skin.py`. Confirmar que se usa el mismo subset (n≈2.800).

3. Si el problema fue un timeout: reenviar el job en TOKO con `--time=12:00:00` (los reportes de LLaVA-Med 7B son ~3× más lentos que Mini-VLM por la diferencia de tamaño del LLM). Script SLURM: `slurm/toko/generate_reports_llava.sh`.

4. Si el problema fue un bug: verificar manejo de excepciones en `scripts/generate_report.py:115-123` — actualmente cualquier excepción aborta el batch entero. Añadir try/except por imagen y persistir los errores en un `errors.jsonl` paralelo.

5. Recomputar métricas de texto sobre el set completo.

---

### 3.4 [Prio 4] A3 — Evaluar sobre MM-Skin test split

**Problema:** La tabla SOTA ([tablas_comparativas_sota_v32.tex](../../../Docs/tabla_resultados_sota/tablas_comparativas_sota_v32.tex)) reserva las filas (c) y (d) para "MM-Skin (test split)" pero actualmente se evaluó sobre SkinCaRe y MM-SkinQA, lo cual no es directamente comparable.

**Implementación:**

1. Verificar disponibilidad del MM-Skin test split. El paper de MM-Skin ([MMSkin2025]) publica el split en HuggingFace: <https://huggingface.co/datasets/Joey-Chou/MM-Skin>. Descargar con `Codigo/scripts/prepare_data.py --download-mmskin`.

2. Crear un loader específico para MM-Skin dermoscopy en `Codigo/src/data/mm_skin.py::MMSkinDermoscopyDataset` que cargue el subset `dermoscopy` y exponga el campo `caption` como referencia.

3. Generar reportes con ambos modelos sobre el split test (~700 imágenes según el paper):
   ```bash
   python scripts/generate_report.py --model llava_med --dataset mmskin_dermo --split test
   python scripts/generate_report.py --model mini_vlm --dataset mmskin_dermo --split test
   ```

4. Calcular BLEU-4, ROUGE-L, METEOR y BERTScore. Importante: **usar el mismo modelo BERTScore que el paper** (revisar el repositorio de MM-Skin para identificar el modelo, posiblemente RoBERTa-large) para que la comparación sea válida.

5. Actualizar la tabla SOTA con los valores obtenidos.

**Resultado esperado:** confirmar o refutar que nuestros modelos superan al SOTA SkinVL-MM en BERTScore (actualmente 70.54–76.63 vs 57.76 del SOTA).

---

### 3.5 [Prio 5] C4 — LLM-as-Judge para evaluación clínica

**Justificación:** Las métricas automáticas (BLEU, ROUGE) penalizan el uso de sinónimos y el cambio de estructura, por lo que no reflejan la calidad clínica real de los reportes. Un LLM grande puede actuar como evaluador clínico.

**Implementación:**

1. Crear `Codigo/src/evaluation/llm_judge.py` con dos modos:
   - **Modo absoluto:** evalúa un reporte solo, en 4 dimensiones (corrección diagnóstica, completitud morfológica, coherencia estructural, ausencia de alucinaciones), cada una en escala 1–5.
   - **Modo comparativo:** A/B entre dos reportes (LLaVA-Med vs Mini-VLM) para la misma imagen.

2. Prompt template (modo absoluto):

```
Eres un dermatólogo evaluador. Recibirás:
- Imagen: <imagen dermoscópica>
- gt_label: <etiqueta de referencia>
- Reporte generado: <reporte>

Evalúa el reporte en 4 dimensiones (1=muy malo, 5=excelente):
1. Corrección diagnóstica (¿coincide con gt_label?)
2. Completitud morfológica (¿menciona características visibles relevantes?)
3. Coherencia estructural (¿está bien organizado?)
4. Ausencia de alucinaciones (¿inventa datos no verificables?)

Responde SOLO en formato JSON: {"diagnosis": 1-5, "morphology": 1-5, "structure": 1-5, "no_hallucination": 1-5, "comment": "..."}
```

1. Para reducir costo, evaluar sobre un subset estratificado (50 imágenes por clase × 7 clases = 350 imágenes) y reportar intervalos de confianza.

2. Persistir en `outputs/metrics_cache/llm_judge_{dataset}_{model}.json`.

**Validación:** correlacionar el score del juez con el entity recall y la diagnostic consistency. Una baja correlación sugiere que las métricas automáticas no capturan la calidad clínica.

---

### 3.6 [Prio 6] C2 — Pérdida auxiliar de entidades clínicas

**Justificación:** Mini-VLM tiene mayor entity recall que LLaVA-Med (60.7% vs 45.7% en HAM10000) pero ambos están lejos de un dermatólogo (>90%). Una pérdida auxiliar incentivaría la inclusión de terminología clínica específica.

**Implementación:**

1. Construir un vocabulario dermatológico estructurado en `Codigo/src/evaluation/derm_vocab.py`:

```python
DERM_VOCAB: dict[str, list[str]] = {
    "asymmetry":      ["asymmetric", "asymmetry", "irregular shape"],
    "border":         ["border", "irregular border", "well-defined", "ill-defined"],
    "color":          ["uniform color", "multiple colors", "pigmented", "erythema", "brown", "black"],
    "diameter":       ["diameter", "size", "millimeter", "cm"],
    "elevation":      ["raised", "flat", "papule", "macule", "nodule"],
    "surface":        ["smooth", "scaly", "ulcerated", "crusted", "keratotic"],
    "vasculature":    ["telangiectasia", "vascular pattern", "arborizing"],
    "pigment_pattern": ["pigment network", "globules", "streaks", "blue-white veil"],
}
```

2. Modificar `Codigo/src/training/two_stage.py` para aceptar una pérdida auxiliar en Stage 2:

```python
def entity_coverage_loss(generated_logits, target_ids, derm_token_ids):
    """
    Recompensa al modelo por asignar alta probabilidad a tokens del vocabulario
    dermatológico cuando aparecen en el target.
    Implementación: BCE entre P(derm_token | context) y la presencia binaria
    del token en el target.
    """
    ...
```

3. La pérdida total queda: `loss = ce_loss + λ * entity_coverage_loss`. Empezar con `λ=0.1` y ajustar si la entity coverage no mejora.

4. Reentrenar Stage 2 con esta pérdida sobre el mejor checkpoint Stage 1 actual. No requiere repetir Stage 1.

5. Evaluar entity recall pre/post sobre HAM10000 y SkinCaRe. Objetivo: +10 puntos en entity recall sin degradar BERTScore.

---

### 3.7 [Prio 7] B3 — Alinear instrucción de Stage 1 con Stage 2

**Problema (P2):** Stage 1 usa una instrucción fija (`"Describe this skin lesion."`), pero Stage 2 usa instrucciones variables del dataset SkinCoT que típicamente piden razonamiento estructurado. El proyector se adapta a la instrucción simple, no a la compleja.

**Implementación:**

1. Editar `Codigo/src/training/two_stage.py:111`:

```python
# Antes
CAPTION_INSTRUCTION = "Describe this skin lesion."

# Después
CAPTION_INSTRUCTION_VARIANTS = [
    "Describe this skin lesion.",
    "Describe the skin lesion in this image.",
    "What does this skin lesion look like?",
    "Provide a clinical description of this skin lesion.",
    "Describe this skin lesion with a structured clinical report including findings and impression.",
]
```

2. En `VLMTrainCollator.__call__()`, samplear aleatoriamente una instrucción por ejemplo:

```python
import random
if self.mode == "caption":
    instructions = [random.choice(CAPTION_INSTRUCTION_VARIANTS) for _ in batch]
```

3. Reentrenar Stage 1 con la nueva variabilidad de instrucción (1 día GPU por modelo). Reentrenar Stage 2 sobre el nuevo checkpoint Stage 1 (2 días GPU).

4. Comparar val loss y métricas finales con el run actual. Hipótesis: mejora la robustez del proyector frente a prompts diversos en inferencia.

---

### 3.8 [Prio 8] B2 — Aumentar épocas de Stage 2

**Problema (P6):** El mejor val loss ocurre en la época final (5/5) en ambos modelos, sugiriendo que el modelo aún está mejorando. Los trials largos (15 épocas) no completaron por timeout.

**Implementación:**

1. Editar `Codigo/configs/sweeps/phase2_sweep.yaml` para:
   - `stage2_epochs`: explorar [10, 15, 20]
   - early stopping con paciencia=3 sobre val loss
   - Guardar checkpoint cada época

2. Ajustar `slurm/mendieta/vlm_classify_*.sh` con tiempo `2-00:00:00` (48h) — los trials de 15 épocas en LLaVA-Med tardaron ~30h.

3. Lanzar nuevo sweep en Mendieta con n=4 trials por modelo, fijando `lora_r=64`, `lora_alpha=64`, `lora_dropout=0.0`, `stage2_lr=2.5e-5` (mejores valores actuales) y variando solo épocas:
   ```bash
   python scripts/sweep_phase2.py --cluster mendieta --n-trials 4 --model llava_med
   python scripts/sweep_phase2.py --cluster mendieta --n-trials 4 --model mini_vlm
   ```

4. Validar que la pérdida de validación deja de bajar antes de las 20 épocas (de lo contrario, ampliar más).

5. Si el modelo ganador converge a val loss < 0.85 (LLaVA-Med) o < 1.30 (Mini-VLM), regenerar reportes y comparar métricas.

**Riesgo:** overfitting al dataset SkinCoT (~3k pares). Mitigar con dropout=0.05 si se observa divergencia entre train/val loss.

---

### 3.9 [Prio 9] B1 — Mezclar SkinCoT + reportes estructurados

**Problema (P1):** El modelo se entrena en estilo CoT pero se evalúa contra referencias mixtas y se le pide formato estructurado en inferencia. Esto produce mismatch de distribución.

**Implementación:**

1. **Construir el dataset de reportes estructurados** en `Codigo/src/data/structured_reports.py`. Tres fuentes posibles:
   - **MM-Skin VQA convertido a reporte:** concatenar las preguntas y respuestas de cada imagen y parsearlas en un reporte estructurado con secciones Findings/Impression/Differential. Tamaño: ~6.000 reportes.
   - **Generación sintética con LLM-judge:** usar GPT-4 para reformular las narrativas SkinCoT en reportes estructurados manteniendo el contenido. Costo: ~$30 USD por 3.000 reformulaciones.
   - **Augmentation programática:** plantillas regex que extraen entidades de SkinCoT y las distribuyen en secciones de reporte.

2. **Configurar dataset híbrido** con peso 0.5 para SkinCoT y 0.5 para reportes estructurados:

```python
class HybridReportDataset(Dataset):
    def __init__(self, skincot_ds, structured_ds, structured_ratio=0.5):
        ...
    def __getitem__(self, idx):
        if random.random() < self.structured_ratio:
            return self.structured_ds[idx % len(self.structured_ds)]
        return self.skincot_ds[idx % len(self.skincot_ds)]
```

3. Reentrenar Stage 2 sobre este dataset híbrido. Mantener hiperparámetros del mejor trial actual.

4. Validar que las métricas de texto (BLEU/ROUGE) suben significativamente (esperado: ROUGE-L de 0.07 → 0.15+ sobre SkinCaRe), confirmando reducción del mismatch de estilo.

**Riesgo:** los reportes estructurados sintéticos pueden introducir sesgos del LLM generador. Mitigar revisando manualmente 50 muestras antes del fine-tuning.

---

### 3.10 [Prio 10] B4 — Sweep ampliado de LoRA

**Justificación:** El sweep actual exploró r ∈ {16, 64} y solo `q_proj`/`v_proj`. Hay margen para explorar más capas y rangos mayores.

**Implementación:**

1. Editar `Codigo/configs/sweeps/phase2_sweep.yaml`:

```yaml
parameters:
  lora_r:
    values: [32, 64, 128]
  lora_target_modules:
    values:
      - ["q_proj", "v_proj"]
      - ["q_proj", "k_proj", "v_proj", "o_proj"]
      - ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
  lora_dropout:
    values: [0.0, 0.05]
```

2. Modificar `Codigo/src/training/lora_config.py` para parametrizar `target_modules`:

```python
def get_lora_config(r, alpha, dropout, target_modules):
    return LoraConfig(
        r=r, lora_alpha=alpha, lora_dropout=dropout,
        target_modules=target_modules,
        bias="none", task_type="CAUSAL_LM",
    )
```

3. Lanzar sweep de 12 trials × 2 modelos en Mendieta. Tiempo total estimado: 1 semana.

4. Combinar con la mejora B2 (más épocas) para evitar duplicar el costo.

**Restricción de VRAM:** r=128 con todas las capas (`gate_proj`, `up_proj`, `down_proj`) puede no caber en 24 GB de A30. Validar con dry-run antes de lanzar el sweep completo.

---

### 3.11 [Prio 11] C3 — Adaptación de dominio con HIBA

**Justificación:** Los clasificadores supervisados pierden 23–32 puntos de accuracy en HIBA respecto de HAM10000 (Tabla 1b). Para los VLMs no se ha medido aún esta brecha en generación de reportes, pero es esperable que existan los mismos sesgos de fototipo y adquisición.

**Implementación:**

1. **Construir referencias para HIBA.** HIBA no tiene captions ni razonamientos clínicos. Opciones:
   - Pseudo-etiquetas con un VLM grande (LLaVA-Med externo o GPT-4V) para generar reportes de referencia. Validar con dermatólogo de la institución HIBA.
   - Usar solo el `gt_label` y el fototipo como condicionamiento textual en el entrenamiento, sin reporte completo.

2. **Crear un dataset HIBA en estilo CoT** con un LLM auxiliar:
   - Input: imagen HIBA + gt_label + fototipo
   - Output (generado por LLM): razonamiento CoT en estilo SkinCoT
   - Validación: muestreo de 100 ejemplos por dermatólogo

3. **Fine-tuning con dataset combinado:** 60% SkinCoT + 40% HIBA-CoT en Stage 2. Mantener Stage 1 igual.

4. **Evaluación:** generar reportes sobre HIBA test set y medir métricas + LLM-as-Judge clínico.

**Riesgo:** sin ground-truth real, las pseudo-etiquetas pueden introducir sesgos del modelo generador. Es la mejora de mayor riesgo del plan.

---

### 3.12 [Prio 12] C1 — Vision encoder ViT-L/14 para Mini-VLM

**Justificación:** Mini-VLM usa CLIP ViT-B/16 mientras que LLaVA-Med usa CLIP ViT-L/14. La menor resolución y capacidad visual de B/16 puede limitar la descripción de características morfológicas finas (pigment network, atypical vasculature).

**Implementación:**

1. **Verificar compatibilidad con Phi-3.5-vision.** El modelo `microsoft/Phi-3.5-vision-instruct` viene con ViT-B/16 incrustado en su pipeline. Reemplazarlo requiere:
   - Bypass del processor multimodal de Phi-3.5
   - Ensamblar manualmente: `CLIP-ViT-L/14` → MLP projector → tokens visuales → LLM Phi-3-mini
   - Reentrenar Stage 1 desde cero (el proyector es nuevo)

2. **Alternativa más segura:** cambiar la base completa a `microsoft/Phi-3.5-vision-instruct-336` con resolución mayor manteniendo ViT-B/16, o explorar `microsoft/Phi-3.5-vision-instruct-1024` si está disponible.

3. **Implementación nativa con CLIP-L/14:** crear `Codigo/src/models/mini_vlm_l14.py`:
   - Cargar `openai/clip-vit-large-patch14-336`
   - Cargar `microsoft/Phi-3-mini-128k-instruct` como LLM
   - MLP projector de dimensión `1024 → 4096` (dim del LLM)
   - Reescribir `load_components()` y la lógica de `<|image_1|>` para concordar con la nueva base

4. **Costo de VRAM:** ViT-L/14 + Phi-3-mini consume ~12 GB en inferencia y ~16 GB en LoRA. Cabe en A30 (24 GB) pero no en RTX 4080 (16 GB) sin cuantización.

5. **Reentrenar Stage 1 + Stage 2 desde cero.** Tiempo estimado: 3 días GPU para Stage 1 + 5 días GPU para sweep Stage 2.

**Justificación de prioridad baja:** alta complejidad, riesgo de regresión en Mini-VLM, y la ganancia esperada es marginal sobre LLaVA-Med (que ya tiene ViT-L/14).

---

## 4. Métricas de éxito

Cada mejora se valida contra los siguientes umbrales:

| Métrica | Baseline (mejor actual) | Objetivo a 3 meses | Objetivo a 6 meses |
|---------|------------------------|-------------------|--------------------|
| Entity recall HAM10000 | 60.7% (Mini-VLM) | 70% | 85% |
| Diagnostic consistency HAM10000 | 71.5% (LLaVA-Med) | 80% | 90% |
| BERTScore SkinCaRe | 0.766 (Mini-VLM) | 0.80 | 0.85 |
| ROUGE-L SkinCaRe | 0.137 (Mini-VLM) | 0.20 | 0.30 |
| LLM-judge clínico (1–5) | N/A | ≥ 3.5 promedio | ≥ 4.0 promedio |
| BLEU-4 MM-Skin test (vs SOTA 2.84) | N/A | 2.5 | 3.5 |

---

## 5. Cronograma sugerido

```
Semana 1-2:  Prio 1-4 (correcciones de medición + completar evaluaciones)
             → re-publicar resultados con métricas corregidas
Semana 3-4:  Prio 5 (LLM-as-Judge) + diseño del dataset estructurado para B1
Semana 5-7:  Prio 6-8 (entity loss, alineación de prompts, más épocas)
             → primer reentrenamiento mayor
Semana 8-11: Prio 9-10 (dataset híbrido + sweep ampliado)
             → segundo reentrenamiento mayor
Semana 12+:  Prio 11-12 (HIBA + ViT-L/14) según resultados acumulados
```

---

## 6. Dependencias entre mejoras

- **A2 → todas:** sin métricas correctas no se puede medir el impacto de las demás mejoras.
- **A3, A4 → C4:** el LLM-judge debe correrse sobre el dataset comparable con SOTA.
- **B3 → B2 → B1 → B4:** cada paso de entrenamiento se construye sobre el anterior.
- **C2 (entity loss) ⊥ B-series:** se puede combinar con cualquier reentrenamiento.
- **C3 (HIBA), C1 (ViT-L) son independientes** entre sí pero ambos requieren reentrenamiento completo.

---

## 7. Archivos clave a modificar

```
Codigo/
├── src/
│   ├── evaluation/
│   │   ├── label_normalization.py     # NUEVO (A2)
│   │   ├── derm_vocab.py              # NUEVO (C2)
│   │   ├── llm_judge.py               # NUEVO (C4)
│   │   └── clinical_ner.py            # MODIFICAR (A2)
│   ├── data/
│   │   ├── mm_skin.py                 # MODIFICAR (A3)
│   │   └── structured_reports.py      # NUEVO (B1)
│   ├── models/
│   │   └── mini_vlm_l14.py            # NUEVO (C1)
│   └── training/
│       ├── two_stage.py               # MODIFICAR (B3, C2)
│       └── lora_config.py             # MODIFICAR (B4)
├── scripts/
│   ├── generate_report.py             # MODIFICAR (A1)
│   └── sweep_phase2.py                # MODIFICAR (B2, B4)
├── configs/
│   └── sweeps/phase2_sweep.yaml       # MODIFICAR (B2, B4)
└── notebooks/
    └── 02_results_phase2.ipynb        # MODIFICAR (A2, recálculo)
```
