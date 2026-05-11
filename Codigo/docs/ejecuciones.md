# Registro de Ejecuciones

Ayuda-memoria cronológico de experimentos enviados a cluster, ordenado de más reciente a más antiguo.

---

## 2026-05-10

### HIBA re-run mejores trials sweep v4 — TOKO
Re-entrenamiento de los mejores trials con `--eval-hiba` para obtener métricas OOD.
ConvNeXt-Tiny t06 (lr=7.5e-5, wd=0.10, m=6) y Swin-Tiny t08 (lr=1.5e-4, wd=0.05, m=6).

**Jobs:** 95444 (ConvNeXt-Tiny t06 HIBA), 95445 (Swin-Tiny t08 HIBA)  
**Cluster:** TOKO  
**Resultados:** [clasificadores_resul_sweep_v4_20260510.md](resul/clasificadores_resul_sweep_v4_20260510.md) (sección 7 — pendiente)

```bash
python scripts/toko/submit_sweep.py --rerun-hiba convnext_tiny t06
python scripts/toko/submit_sweep.py --rerun-hiba swin_tiny t08
```

---

### Sweep clasificadores modern v4 — TOKO
Sweep de hiperparámetros para ConvNeXt-Tiny y Swin-Tiny (recipe modern v3, sin DenseNet/ViT).
15 trials por modelo (30 jobs totales): lr × weight_decay × randaugment_m, pre-muestreados.
Métricas objetivo: val_f1_weighted. Sin HIBA durante el sweep.
**Hallazgo:** Swin-Tiny t08 (F1=0.8817) supera al ViT-B/16 legacy (F1=0.8621) — nuevo mejor clasificador de Fase 1.

**Jobs:** 95400–95429 (14/15 Swin completados — t01 falló)  
**Cluster:** TOKO  
**Plan:** [clasificadores_sweep_modern_v4_plan_20260510.md](ideas/clasificadores_sweep_modern_v4_plan_20260510.md)  
**Resultados:** [clasificadores_resul_sweep_v4_20260510.md](resul/clasificadores_resul_sweep_v4_20260510.md)

---

### Stage 2 v2 — Mendieta
Re-entrenamiento de Stage 2 para LLaVA-Med y Mini-VLM con epochs=10 (vs 3 del sweep original).
Mismos HPs del mejor trial (t04): lr=2.495e-5, lora_r=64, lora_alpha=64, lora_dropout=0.0.
Tiempo SLURM: 2 días (máximo disponible).

**Jobs:** 1153597 (Mini-VLM), 1153598 (LLaVA-Med)  
**Cluster:** Mendieta  
**Plan:** [reportes_mejoras_v2_plan_20260510.md](ideas/reportes_mejoras_v2_plan_20260510.md)

---

### Mejoras de inferencia y evaluación aplicadas al código
Sin jobs. Cambios implementados localmente:
- **A1:** `scripts/generate_report.py` — `REPORT_PROMPT` corregido a `"Describe this skin lesion."` (alineado con instrucción de Stage 2)
- **A2:** `src/evaluation/clinical_ner.py` — `_DIAGNOSIS_SYNONYMS` ampliado con etiquetas SkinCaRe; `_normalize_label()` normaliza folder-names antes de buscar sinónimos (diagnostic_consistency de SkinCaRe era ≈0% por este bug)

---

## 2026-05-07

### Clasificación VLM — LLaVA-Med FT re-envío — Mendieta
Re-envío de jobs 1151165 y 1151169 (LLaVA-Med FT likelihood y CoT) tras fix del bug de LoRA rank mismatch.
El bug: `lora_config.json` tenía r=64 pero el checkpoint fue entrenado con r=16.
Fix: `scripts/train_vlm_classify.py` detecta el rank real del checkpoint antes de aplicar LoRA.

**Jobs:** 1153591 (likelihood), 1153592 (CoT)  
**Cluster:** Mendieta  
**Resultados:** [vlm_clasificacion_resul_v2_20260510.md](resul/vlm_clasificacion_resul_v2_20260510.md)

---

## 2026-05-07 (madrugada)

### Clasificación VLM — all_classify_lik + all_classify_cot — Mendieta
Primera corrida completa de los métodos likelihood y CoT para todos los modelos VLM.
Jobs 1151163–1151170: Mini-VLM ZS/FT × likelihood/CoT + LLaVA-Med ZS/FT × likelihood/CoT.
LLaVA-Med FT (1151165, 1151169) crashearon por LoRA rank mismatch (ver fix arriba).

**Jobs:** 1151163–1151170  
**Cluster:** Mendieta  
**Resultados:** [vlm_clasificacion_resul_v2_20260510.md](resul/vlm_clasificacion_resul_v2_20260510.md)

---

## 2026-05-03

### Generación de reportes — all_gen — Mendieta
Primera corrida de generación de reportes sobre HAM10000, SkinCaRe y MM-SkinQA.
Resultados analizados y documentados en reportes_resul_v1.

**Cluster:** Mendieta  
**Resultados:** [reportes_resul_v1_20260503.md](resul/reportes_resul_v1_20260503.md)

---

## 2026-05-01

### Clasificadores Fase 1 — modern v3 — TOKO
Corrida final de clasificadores con recipe modern v3 (Focal Loss removido → CE + class weights).
Modelos: DenseNet121, ViT-B/16, ConvNeXt-Tiny, Swin-Tiny. Con evaluación HIBA OOD.

**Cluster:** TOKO  
**Resultados:** [clasificadores_resul_final_20260501.md](resul/clasificadores_resul_final_20260501.md)

---

## Documentos de referencia

| Documento | Tipo | Descripción |
|-----------|------|-------------|
| [clasificadores_sweep_modern_v4_plan_20260510.md](ideas/clasificadores_sweep_modern_v4_plan_20260510.md) | Plan | Sweep HPs ConvNeXt/Swin en TOKO |
| [reportes_mejoras_v2_plan_20260510.md](ideas/reportes_mejoras_v2_plan_20260510.md) | Plan | Stage 2 v2 + fixes A1/A2 |
| [clasificadores_resul_sweep_v4_20260510.md](resul/clasificadores_resul_sweep_v4_20260510.md) | Resultado | Sweep v4: ConvNeXt-Tiny + Swin-Tiny HPs (sección HIBA pendiente jobs 95444/95445) |
| [vlm_clasificacion_resul_v2_20260510.md](resul/vlm_clasificacion_resul_v2_20260510.md) | Resultado | Análisis VLM likelihood/CoT |
| [clasificadores_resul_final_20260501.md](resul/clasificadores_resul_final_20260501.md) | Resultado | Análisis final clasificadores Fase 1 (v3) |
| [reportes_resul_v1_20260503.md](resul/reportes_resul_v1_20260503.md) | Resultado | Resultados generación de reportes v1 |
| [vlm_clasificacion_v2_plan_20260501.md](ideas/vlm_clasificacion_v2_plan_20260501.md) | Plan | Mejoras clasificación VLMs |
| [reportes_v1_plan_20260503.md](ideas/reportes_v1_plan_20260503.md) | Plan | Ideas originales para generación de reportes |
