# Plan: Mejoras de Generación de Reportes — v2

**Fecha:** 2026-05-10  
**Cluster:** Mendieta (A30 24GB, CUDA 12.2)  
**Modelos:** LLaVA-Med 7B + LoRA, Mini-VLM (Phi-3-mini) + LoRA  
**Referencia:** `docs/resul/reportes_resul_v1_20260503.md`

---

## 1. Contexto

La evaluación v1 identificó seis problemas principales. Este plan aplica las mejoras factibles dentro del scope de la tesina, clasificadas en:

- **A (sin reentrenamiento):** correcciones de inferencia y evaluación
- **B (con reentrenamiento):** Stage 2 con más épocas (B2 únicamente)

Se descartó explícitamente:
- **B1** (mezclar MM-SkinQA en Stage 2): requiere cambios de código no triviales en el pipeline de entrenamiento y normalización de formato
- **B3** (re-run Stage 1 con instrucción corregida): costo doble sin ganancia proporcional; la instrucción de Stage 1 ya coincide con Stage 2

---

## 2. Mejoras implementadas

### A1 — Corrección de instrucción de inferencia ✅

**Archivo modificado:** `scripts/generate_report.py`

**Cambio:** `REPORT_PROMPT` actualizado de:
```
"Describe this skin lesion with a structured clinical report that includes:
findings, diagnostic impression, and differential diagnosis."
```
a:
```
"Describe this skin lesion."
```

**Por qué:** Stage 2 se entrenó con `VLMTrainCollator.CAPTION_INSTRUCTION = "Describe this skin lesion."` como instrucción para todos los pares SkinCoT. La instrucción de inferencia larga nunca apareció en training, generando distribución shift en el prompt que reduce la calidad de las respuestas.

---

### A2 — Normalización de etiquetas SkinCaRe para diagnostic_consistency ✅

**Archivo modificado:** `src/evaluation/clinical_ner.py`

**Cambio:** Agregado `_FOLDER_TO_CANONICAL` que mapea folder-names de SkinCaRe a claves canónicas del dict de sinónimos. Agregada función `_normalize_label()` que aplica esa normalización antes de buscar sinónimos. Ampliado `_DIAGNOSIS_SYNONYMS` con 15+ diagnósticos de SkinCaRe (eczema, psoriasis, tinea, etc.).

**Por qué:** La diagnostic_consistency en SkinCaRe era ≈0% porque `gt_label` contiene el nombre de carpeta del dataset (ej. `"Eczema Photos"`) en lugar de la terminología médica que usa el modelo (ej. `"eczema"`, `"atopic dermatitis"`). Con normalización, la métrica debe reflejar la calidad diagnóstica real.

---

### A3 — Evaluación sobre MM-Skin test split (pendiente en cluster)

No requiere cambios de código: los targets `gen_llava_mmskin` y `gen_mini_mmskin` ya existen en `mendieta/submit.py` con `DATASETS=mmskin`. Tras re-correr con la instrucción corregida (A1), los reportes sobre MM-SkinQA serán comparables con el SOTA (SkinVL-MM).

---

### A4 — LLaVA-Med: solo 20 reportes en MM-SkinQA

El problema es de disponibilidad de datos en el cluster: solo 20 imágenes estaban en el directorio `data/processed/MM-SkinQA` cuando se corrió el job. Mini-VLM procesó 2.809 porque accedió al split completo.

**Fix:** Verificar que el dataset completo MM-SkinQA esté sincronizado en Mendieta antes de correr `gen_llava_mmskin`. El script `generate_report.py` ya hace resume defensivo (salta imágenes con reporte válido), por lo que no es necesario borrar los 20 reportes existentes.

---

### B2 — Stage 2 con 10 épocas ✅

**Archivos creados:**
- `slurm/mendieta/train_vlm_s2_v2.sh` — LLaVA-Med, epochs=10
- `slurm/mendieta/train_vlm_s2_mini_v2.sh` — Mini-VLM, epochs=10

**Hiperparámetros:** Idénticos al mejor trial del sweep (t04):
- `lr=2.495e-5`, `lora_r=64`, `lora_alpha=64`, `lora_dropout=0.0`, `grad_accum=8`
- Tiempo SLURM: 2 días (máximo de Mendieta, ya configurado en v1)

**Por qué:** Ambos modelos mejoraban continuamente hasta la época 5/5 (val_loss decreciente sin plateau), indicando underfitting. Los trials de 15 épocas del sweep no completaron. Con 10 épocas esperamos convergencia más completa sin riesgo de overfitting sobre los ~2k pares SkinCoT.

**Targets de envío:**
```bash
python scripts/mendieta/submit.py mini_s2_v2
python scripts/mendieta/submit.py llava_s2_v2
# o ambos:
python scripts/mendieta/submit.py all_s2_v2
```

---

## 3. Pasos post-entrenamiento

Una vez completado B2 y obtenidos los checkpoints `stage2_llava_med_v2` y `stage2_mini_vlm_v2`:

1. **Re-correr generación con checkpoints v2 e instrucción A1:**
   ```bash
   python scripts/mendieta/submit.py all_gen          # HAM10000 + SkinCaRe
   python scripts/mendieta/submit.py all_gen_mmskin   # MM-SkinQA (verificar datos A4)
   ```

2. **Evaluar métricas:** Las mejoras A1 y A2 se aplicarán automáticamente en el nuevo `generate_report.py`.

3. **Comparar v1 vs v2:** Documentar en `docs/resul/reportes_resul_v2_*.md` con:
   - BLEU-4, ROUGE-L, BERTScore F1 (SkinCaRe + MM-SkinQA)
   - Clinical Entity Recall (HAM10000 + SkinCaRe)
   - Diagnostic Consistency (con normalización A2)

---

## 4. Mejoras descartadas y justificación

| Mejora | Descartada porque |
|--------|-------------------|
| **B1** — Mezclar MM-SkinQA en Stage 2 | Requiere refactorizar `train_vlm_stage2.py` para soportar `ConcatDataset` + normalizar formato entre SkinCoT (CoT chains) y MM-SkinQA (VQA pairs). Costo alto, ganancia incierta. |
| **B3** — Re-run Stage 1 con instrucción corregida | `CAPTION_INSTRUCTION = "Describe this skin lesion."` ya es la instrucción de Stage 1. El mismatch era solo en inferencia, resuelto con A1. Re-correr Stage 1 duplicaría el costo de cluster sin beneficio adicional. |
| **B4** — LoRA r=128 | El sweep ya seleccionó r=64 sobre r=16; doblar a r=128 es especulativo y aumenta VRAM significativamente en LLaVA-Med (ya cerca del límite de 24GB). |
| **C1–C4** | Mejoras de arquitectura y largo plazo fuera del scope de la tesina. |

---

## 5. Estimado de tiempos en cluster

| Job | Modelo | Estimado |
|-----|--------|----------|
| `llava_s2_v2` | LLaVA-Med | ~12-16h en A30 24GB |
| `mini_s2_v2` | Mini-VLM | ~8-10h en A30 24GB |
| `all_gen` (post v2) | Ambos | ~12h + 8h |
| `all_gen_mmskin` | Ambos | ~4h + 4h |
