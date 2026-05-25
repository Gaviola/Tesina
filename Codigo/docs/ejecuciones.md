# Registro de Ejecuciones

Ayuda-memoria cronológico de experimentos enviados a cluster, ordenado de más reciente a más antiguo.

---

## 2026-05-25

### Análisis de jobs 1154209-1154214 + re-envío gen v2 — Mendieta
Descarga y análisis de los 6 jobs enviados el 2026-05-17 (Stage 2 v2 evaluación).

**Clasificación VLM (jobs 1154209-1154212):** 4/4 COMPLETED. Resultados llenados in-place en
[vlm_clasificacion_resul_v3_20260517.md](resul/vlm_clasificacion_resul_v3_20260517.md).
**Veredicto: NO CUMPLE criterio gating.** Stage 2 v2 (epochs=10) no rompe el class collapse:
- LLaVA-Med FT lik v2: F1 mejora +0.100 (0.098→0.198) pero sens_macro baja (0.163→0.137 < 1/7).
- Mini-VLM FT lik v2: prácticamente sin cambios (perfect collapse a NV persiste, sens_macro=0.141).
- LLaVA-Med FT CoT v2: regresión crítica — UNKNOWN sube 30%→81% (catastrophic forgetting del formato).
- Mini-VLM FT CoT v2: collapse cambia de NV→MEL pero sens_macro marginal (0.145).

Diagnóstico: el cuello de botella es **imbalance + objective**, no convergencia. Se planifica iteración v3.

**Generación de reportes (jobs 1154213-1154214):** TIMEOUT en ambos tras 48h, procesando solo MM-SkinQA
(LLaVA-Med: 2600/22004 = 11.8%; Mini-VLM: 7120/22004 = 32.4%). **HAM10000 y SkinCoT en 0 reportes**, impidiendo
evaluar diagnostic_consistency (criterio gating de generación).

**Acción correctiva — Re-envío con orden invertido:** modificados `slurm/mendieta/v2/generate_reports_{llava,mini}.sh`
para procesar primero HAM10000 → SkinCoT → MM-SkinQA. Garantiza HAM+SkinCoT (~3k imgs combinadas) en ≤24h
incluso si MM-SkinQA timeout. Resume defensivo preserva los reportes MM-SkinQA parciales.

**Jobs re-enviados:** 1154471 (LLaVA-Med v2), 1154472 (Mini-VLM v2)
**Cluster:** Mendieta
**Resultados pendientes:** [reportes_resul_v2_20260517.md](resul/reportes_resul_v2_20260517.md) §4 (cuando termine)

**SOTA tabla:** Tabla 1 de `Docs/tabla_resultados_sota/tablas_comparativas_sota_v32.tex` actualizada con
4 filas v2 ((c.lik.ft.v2), (c.cot.ft.v2), (d.lik.ft.v2), (d.cot.ft.v2)) + notas al pie ρ y σ.

**Plan v3 escrito:** [reportes_mejoras_v3_class_weights_plan_20260525.md](ideas/reportes_mejoras_v3_class_weights_plan_20260525.md)
— ataca imbalance directamente vía class weights y/o focal loss en Stage 2.

```bash
# Re-envío:
python scripts/mendieta/sync_up.py
python scripts/mendieta/submit.py all_gen_v2
```

---

## 2026-05-17

### Reorganización v1/v2 de paths y scripts SLURM
Restructuración de outputs y scripts SLURM en subfolders `v1/` y `v2/` para evitar
colisiones entre iteraciones. Cambios:

- **Checkpoints en cluster:** rename `stage2_{model}_{model}_s2_v2/` → `stage2_{model}_v2/`.
- **Outputs locales y en cluster:** `generated_reports/{model}/{dataset}/` → `generated_reports/{model}/v1/{dataset}/`; `results/{model}/{archivos VLM}` → `results/{model}/v1/{archivos}` (training metrics + classification preds). Legacy duplicados prefijados `_legacy_`.
- **SLURM scripts:** los originales movidos a `slurm/mendieta/v1/`; nuevos scripts v2 en `slurm/mendieta/v2/`. Carpeta indica versión, archivos sin sufijo `_v2`.
- **`submit.py`:** rutas v1 actualizadas, aliases v2 nuevos (`gen_*_v2`, `classify_*_ft_*_v2`, grupos `all_vlm_v2`, etc.).
- **`sync_up.py`:** flag `--delete` agregado (solo rsync). En Windows nativo (tar mode) los huérfanos se limpian por SSH manualmente (hecho).
- **Datos out-of-scope:** archivos de clasificadores TOKO (densenet/vit/swin/convnext sweep) intactos en `outputs/results/` root.

### Re-evaluación local del baseline v1 de reportes con fix A2 — local
Sin jobs SLURM. Se re-evaluaron los 6 combos (2 modelos × 3 datasets) usando
`scripts/evaluate_reports.py` con `clinical_ner.py` actualizado (fix A2).
Resultado clave: diagnostic_consistency en SkinCoT pasa de ~0% (pre-fix) a 0.20–0.34.

**Output:** `outputs/results/{model}/v1/reeval/level{1,2}_{model}_results.json`
**Resultados detallados:** §3 de [reportes_resul_v2_20260517.md](resul/reportes_resul_v2_20260517.md)

### Cierre Fase 1 — HIBA sweep v4 — TOKO
Análisis de jobs 95444 y 95445 (HIBA re-run de ConvNeXt-Tiny t06 y Swin-Tiny t08).
- **Swin-Tiny v4 HIBA:** F1=0.5958 (+0.020 vs v3), pero AUC −0.036 y sens MEL −0.059.
- **ConvNeXt-Tiny v4 HIBA:** F1=0.5235 (−0.065 vs v3) — degrada todas las métricas OOD.
- Sens MEL cae en ambos modelos v4. Trade-off in-distribution vs OOD documentado.

**Resultados:** §7 actualizado in-place en [clasificadores_resul_sweep_v4_20260510.md](resul/clasificadores_resul_sweep_v4_20260510.md)
**SOTA tabla:** Tablas 1, 1b y 5 actualizadas en `Docs/tabla_resultados_sota/tablas_comparativas_sota_v32.tex`. Filas (a')(b') reemplazadas con sweep v4. Agregadas 8 filas VLM likelihood/CoT en Tabla 1 (deuda pendiente de v2).

### VLM Stage 2 v2 — clasificación FT (4 jobs) + generación (2 jobs) — Mendieta
Evaluación de la capacidad de predicción y generación de los checkpoints Stage 2 v2 (10 epochs vs 3 de v1, HPs t04).
Cola estimada: 5-7 días. Timeout SLURM 2 días por job (generación puede no completar 3 datasets en una corrida; protocolo de re-envío con resume defensivo documentado).

**Jobs:** 1154209 (LLaVA-Med FT lik), 1154210 (Mini-VLM FT lik), 1154211 (LLaVA-Med FT CoT), 1154212 (Mini-VLM FT CoT), 1154213 (LLaVA-Med gen v2 3-datasets), 1154214 (Mini-VLM gen v2 3-datasets)
**Cluster:** Mendieta
**Resultados clasificación (pendiente):** [vlm_clasificacion_resul_v3_20260517.md](resul/vlm_clasificacion_resul_v3_20260517.md)
**Resultados generación (pendiente):** [reportes_resul_v2_20260517.md](resul/reportes_resul_v2_20260517.md)

```bash
python scripts/mendieta/submit.py all_vlm_v2
```

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
| [clasificadores_resul_sweep_v4_20260510.md](resul/clasificadores_resul_sweep_v4_20260510.md) | Resultado | Sweep v4: ConvNeXt-Tiny + Swin-Tiny HPs (§7 HIBA completado 2026-05-17) |
| [vlm_clasificacion_resul_v3_20260517.md](resul/vlm_clasificacion_resul_v3_20260517.md) | Resultado | VLM clasificación FT con Stage 2 v2 (completado 2026-05-25 — NO cumple gating) |
| [reportes_resul_v2_20260517.md](resul/reportes_resul_v2_20260517.md) | Resultado | Generación reportes v2 + re-eval v1 con fix A2 (parcial — re-envíos 1154471/1154472) |
| [reportes_mejoras_v3_class_weights_plan_20260525.md](ideas/reportes_mejoras_v3_class_weights_plan_20260525.md) | Plan | v3 Stage 2 con class weights / focal loss (ataca class collapse) |
| [vlm_clasificacion_resul_v2_20260510.md](resul/vlm_clasificacion_resul_v2_20260510.md) | Resultado | Análisis VLM likelihood/CoT |
| [clasificadores_resul_final_20260501.md](resul/clasificadores_resul_final_20260501.md) | Resultado | Análisis final clasificadores Fase 1 (v3) |
| [reportes_resul_v1_20260503.md](resul/reportes_resul_v1_20260503.md) | Resultado | Resultados generación de reportes v1 |
| [vlm_clasificacion_v2_plan_20260501.md](ideas/vlm_clasificacion_v2_plan_20260501.md) | Plan | Mejoras clasificación VLMs |
| [reportes_v1_plan_20260503.md](ideas/reportes_v1_plan_20260503.md) | Plan | Ideas originales para generación de reportes |
