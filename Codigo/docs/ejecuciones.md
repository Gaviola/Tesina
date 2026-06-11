# Registro de Ejecuciones

Ayuda-memoria cronológico de experimentos enviados a cluster, ordenado de más reciente a más antiguo.

---

## 2026-06-10

### Ensamble — Nivel 1 sobre SkinCoT + prep local — Mendieta
Para paralelizar (3 jobs simultáneos), se lanza el Nivel 1 sobre **SkinCoT** (único dataset con
referencias). Genera el SkinCoT test split (460 imgs, 23 clases) con LLaVA bajo baseline vs
oracle-noreasoning, `--reference_dir` para Nivel 1.

**Implementación:** CSV oracle SkinCoT (`outputs/skincot_dx_oracle.csv`, image_id→clase DermNet, subida
por scp); SLURM `ensemble_skincot_level1_llava.sh`. **Prep local:** flag `--strip-reasoning` agregado a
`evaluate_reports.py` (elimina `<think>` → mide report-only automático).

**Job:** 1156725 (LLaVA-Med v2, SkinCoT, baseline + oracle)
**Cluster:** Mendieta | **Resultados (pendiente):** Nivel 1 (BLEU/ROUGE/BERTScore/METEOR/CIDEr) vs
referencias + Nivel 2, baseline vs oracle.

### Ensamble — corrida completa 4 condiciones — Mendieta
Con el prompt ganador fijo (`noreasoning`), corrida realista del ensamble: 4 condiciones sobre un
subconjunto del **HAM test split** (~400 imgs), evaluando **report-only**.

**Condiciones (grounding):** (0) baseline, (A) oracle (gt), (B) **Swin** (acc test ~0.80), (C)
**DermLIP** ZS (acc ~0.38). El gap oracle vs swin/dermlip = costo de propagación de error.

**Implementación:** split-filtering (`--splits_file`/`--split`) agregado a `generate_report.py`;
predicciones de Swin/DermLIP mapeadas a image_ids (orden idéntico, y_true coincide 1503/1503) →
CSVs `outputs/full_dx_{oracle,swin,dermlip}.csv` (subidas por scp). SLURM `ensemble_full_llava.sh`,
max_tokens 384. Swin: `modern_v3_predictions.json`; DermLIP: `dermlip_zeroshot_vit-b-16_predictions.json`.

**Jobs (en paralelo):** 1156723 (LLaVA-Med v2) + **1156724 (Mini-VLM v2)** — misma corrida 4
condiciones × 400 imgs, mismas CSVs de grounding (model-agnostic), `ensemble_full_{llava,mini}.sh`.
**Cluster:** Mendieta | **Tiempo estimado:** ~20-24h c/u
**Resultados (pendiente):** enriquecer + evaluar report-only por condición → tabla
baseline/oracle/swin/dermlip **× {LLaVA, Mini}** (comparación cross-model). Luego: Nivel 1 sobre SkinCoT.

```bash
python scripts/mendieta/submit.py ensemble_full_llava
```

### Ensamble v3 — variante "noreasoning" (último lever de prompt) — Mendieta
El re-pilot v2 dio `confirmed` report-only 0.70 pero con 53% de razonamiento residual. Antes de
saltar al fine-tune, se prueba el último lever barato de prompt: variante **`noreasoning`** que
**prohíbe explícitamente** el razonamiento/`<think>` y pide solo el reporte final comprometido.

**Implementación:** variante `noreasoning` en `GROUNDED_TEMPLATES` (`generate_report.py`); SLURM
`pilot_ensemble_v3_llava.sh` (oracle, mismas 100 imgs HAM, LLaVA v2, max_tokens 384).

**Job:** 1156506 (LLaVA-Med v2, variante noreasoning, 100 imgs) — COMPLETED (~44min).
**Cluster:** Mendieta
**Resultado (analizado 2026-06-10):** **el prompt ALCANZÓ.** `noreasoning` → cons **report-only 0.850**
(full 0.860, coinciden), **% razonamiento 1%** (vs 53-78% de las otras), recall 0.79. Eliminó el
`<think>` y llevó el reporte comprometido de 0.30 (soft) → 0.85. **No hace falta fine-tune para el
commitment.** Detalle: [ensamble_resul_20260607 §2.5/§4](resul/ensamble_resul_20260607.md).

**Siguiente:** corrida completa 4 condiciones (baseline/oracle/Swin/DermLIP) con `noreasoning` sobre
HAM test → ensamble realista; + Nivel 1 sobre SkinCoT; + Mini-VLM.

```bash
python scripts/mendieta/sync_up.py && python scripts/mendieta/submit.py pilot_ensemble_v3_llava
```

---

## 2026-06-06

### Ensamble v2 — re-pilot de prompt (3 variantes que fuerzan commitment) — Mendieta
El pilot 1 (job 1155834) mostró que el grounding "soft" es débil: oracle solo 0.60, el modelo ignora
el dx ~40% (ver entrada 2026-06-05). Re-diseño del prompt: 3 variantes oracle que fuerzan el commitment.

**Implementación:** `GROUNDED_TEMPLATES` en `generate_report.py` (`soft`/`dxfirst`/`conclude`/`confirmed`)
+ flag `--grounded_variant`. SLURM `pilot_ensemble_v2_llava.sh` corre las 3 variantes oracle sobre las
mismas 100 imgs HAM (LLaVA v2), `max_tokens=384` (vs 256, reduce truncamiento).

**Job:** 1156019 (LLaVA-Med v2, 3 variantes oracle, 100 imgs c/u) — COMPLETED (~4h).
**Cluster:** Mendieta
**Resultados (analizado 2026-06-07):** [ensamble_resul_20260607 §2.5](resul/ensamble_resul_20260607.md).
Evaluado **full Y report-only** (sin `<think>`):

| Variante | cons full | cons report-only | %txt en `<think>` |
|----------|-----------|------------------|-------------------|
| dxfirst | 0.900 | 0.430 | 78% |
| conclude | 0.970 | 0.570 | 72% |
| **confirmed** | 0.930 | **0.700** | 53% |

**Veredicto:** report-only reordena las variantes (conclude gana en full pero su reporte solo acierta
0.57). **`confirmed` es la mejor** (report-only 0.70 vs 0.30 del soft) — el "no diferenciales" reduce
el dumping a razonamiento. Pero el **prompt tiene techo** (~0.70, aún 53% razonamiento). Siguiente:
una variante que **prohíba el razonamiento** (barato) o, si se estanca, **fine-tune grounding-aware**.

**Extensiones planificadas** (plan ensamble §9): Nivel 1 (BLEU/ROUGE/BERTScore/METEOR/CIDEr) vs
referencias **SkinCoT** (HAM no tiene referencias), segundo generador **Mini-VLM**, y **fine-tune
grounding-aware** si el prompt no alcanza.

```bash
python scripts/mendieta/sync_up.py && python scripts/mendieta/submit.py pilot_ensemble_v2_llava
```

### Hallazgo: no diferenciamos reporte vs razonamiento (analizado 2026-06-07)
SkinCoT bundlea razonamiento (`<think>`) + reporte; entrenamos/evaluamos sobre el texto completo. La
`diagnostic_consistency` está **inflada por menciones dentro del razonamiento**: en el oracle del
pilot 1, sacar `<think>` baja la consistency **0.60 → 0.30** (63% del texto es razonamiento). →
**Hay que medir el reporte comprometido, no el texto completo.** Decisión prompt-vs-fine-tune:
**prompt primero** (re-pilot mide el techo), fine-tune grounding-aware solo si se estanca. Documentado
en [ensamble_resul_20260607.md](resul/ensamble_resul_20260607.md) + plan ensamble §9.5.

### Actualización de documentación
`plan_implementacion.md` actualizado (§0 estado actual + desviaciones: datasets reales, DermLIP,
re-diagnóstico, ensamble, clusters; corregida estructura skincare/mmskin/dermlip). Plan ensamble §9
con re-pilot + extensiones (Nivel 1 SkinCoT, Mini-VLM, fine-tune grounding-aware) + §9.5 reporte/razonamiento.

---

## 2026-06-05

### Pilot ensamble (grounding) — baseline vs oracle — Mendieta
De-risk del [plan ensamble](ideas/ensamble_clasificador_generador_plan_20260605.md): ¿inyectar el
diagnóstico en el prompt sube la `diagnostic_consistency` (que hedea, 0.63)? El pilot local quedó
**bloqueado** (torch local es CPU-only `2.10.0+cpu` → LLaVA-Med 7B no corre local; DermLIP sí porque
es chico y cae a CPU). Se adapta a SLURM de Mendieta (donde la generación VLM ya funciona + checkpoint v2).

**Implementación grounding (en `generate_report.py`):** `--grounded_prompt` + `--diagnosis_source`
(CSV image_id→dx) inyecta el dx por imagen vía `GROUNDED_TEMPLATE`; `--limit N` para pilots. El SLURM
genera ~100 imgs HAM bajo (0) baseline y (A) oracle (gt) sobre las mismas imágenes, checkpoint v2,
max_tokens 256. El CSV oracle se construye en el cluster desde el metadata HAM.

**Job:** 1155834 (LLaVA-Med v2, baseline + oracle, 100 imgs) — COMPLETED (~2h).
**Cluster:** Mendieta
**Resultados (analizado 2026-06-06):**
| Condición | diag_consistency | recall |
|-----------|------------------|--------|
| (0) baseline | 0.480 | 0.653 |
| (A) oracle (grounded gt) | 0.600 | 0.857 |
| **Δ grounding** | **+0.120** | **+0.204** |

**Veredicto: grounding ayuda pero el prompt es DÉBIL.** El oracle (con dx correcto) solo llega a 0.60,
NO al >0.85 esperado (criterio §3 del plan). Causa: el reporte menciona el dx dado en solo **61/100**
casos → el modelo **ignora el dx inyectado ~40%** (su prior CoT `<think>` se impone; y `max_tokens=256`
puede truncar antes de enunciar el dx). El mecanismo es válido (consistency ≈ tasa de mención).

**Siguiente paso:** rediseñar el prompt para **forzar el commitment** (dx primero y obligado, ej.
`"Diagnosis: {dx}. Now describe..."`) → re-pilot oracle barato → si llega a ~0.85, recién la corrida
completa de 4 condiciones (baseline/oracle/Swin/DermLIP).

```bash
python scripts/mendieta/sync_up.py && python scripts/mendieta/submit.py pilot_ensemble_llava
python scripts/mendieta/sync_down.py --reports   # al volver
```

### DermLIP ZS — clasificación derm-especializada en HAM — local (sin cluster)
Sin jobs SLURM. Se agregó **DermLIP** (VL classifier CLIP-style, derm-especializado, entrenado en
Derm1M) y se evaluó zero-shot sobre HAM10000 test. Corre **local** (RTX 4070, ViT-B/16 ~150M, 1503
imgs en ~1m44s) — no necesita cluster.

**Implementación:** `src/models/dermlip.py` (`DermLIPClassifier`, ZS por similitud imagen-texto +
linear-probe opcional), registro `"dermlip"` en factory, `scripts/eval_dermlip_classify.py`,
`open_clip_torch` en requirements.

**Resultado (CUMPLE ambos criterios):** [dermlip_clasificacion_resul_20260605.md](resul/dermlip_clasificacion_resul_20260605.md).
- **ZS HAM:** sens_macro **0.510** (vs LLaVA 0.157 / Mini 0.181 ≈ azar) → +0.37. Rompe el collapse,
  predice las 7 clases, spec 0.90, alta sens MEL (0.76). Acc 0.377 (sesgo a MEL + desbalance NV).
- **Linear-probe HAM** (encoder congelado + LR, n_train=7010, ~9min CPU): **F1 0.762, acc 0.741,
  sens_macro 0.739** — cerca del Swin supervisado (0.88), sens balanceada.
- **ZS clínica (SkinCAP):** sens_macro **0.454** → discrimina en ambos dominios.

Confirma: *VLM general → colapsa en ambos dominios; VL derm-especializado → discrimina (ZS y
linear-probe), dermatoscopía y clínica; supervisado → mejor accuracy.* Filas DermLIP agregadas a
tabla SOTA v32 ((e.zs), (e.lp)). USAGE.md + plan_implementacion.md actualizados.

```bash
pip install open_clip_torch
python scripts/eval_dermlip_classify.py --checkpoint vit-b-16
python scripts/eval_dermlip_classify.py --checkpoint vit-b-16 --eval-dataset skincap_clinical
python scripts/eval_dermlip_linearprobe.py --checkpoint vit-b-16
```

**Pendiente (baja prioridad):** variante `DermLIP_PanDerm` (bloqueada: config custom de open_clip),
fine-tune completo del encoder. Plan: [dermlip_clasificacion_plan_20260604.md](ideas/dermlip_clasificacion_plan_20260604.md).

---

## 2026-06-03

### Domain gap — clasificación VLM ZS sobre foto clínica (SkinCAP) — Mendieta
Confirmación afirmativa del domain gap (ver re-diagnóstico abajo). Se evalúa la clasificación VLM
**zero-shot likelihood** sobre **foto clínica** (SkinCAP mapeado a 7 clases HAM) para comparar
`sens_macro` contra HAM dermatoscópica (ZS: LLaVA 0.157, Mini 0.181).

**Implementación (local, verificada):** adaptador `SkinCAPClassificationDataset` + `SKINCAP_TO_HAM`
en `src/data/skincare.py` (mapeo curado, 624 imgs, 7 clases, min 34/clase); flag `--eval-dataset
{ham10000,skincap_clinical}` en `train_vlm_classify.py` (+ tag `_clinical` en outputs); SLURM
`slurm/mendieta/vlm_classify_{llava,mini}_clinical.sh`; aliases `classify_{llava,mini}_clinical` +
grupo `all_classify_clinical`. SkinCAP confirmado en cluster (ruta anidada, manejada por `_resolve_root`).

**Jobs:** 1155373 (LLaVA-Med ZS clínica), 1155374 (Mini-VLM ZS clínica) — ambos COMPLETED (2-3h).
**Cluster:** Mendieta
**Plan:** [vlm_domain_gap_clinica_plan_20260603.md](ideas/vlm_domain_gap_clinica_plan_20260603.md)
**Resultados (analizado 2026-06-04):** [vlm_domain_gap_clinica_resul_20260604.md](resul/vlm_domain_gap_clinica_resul_20260604.md).

**Veredicto: domain gap NO confirmado.** sens_macro clínica = 0.106 (LLaVA) / 0.176 (Mini) ≈ azar,
≤ HAM ZS (0.157/0.181). El VLM **también colapsa en clínica**, y a una clase **distinta** (HAM→NV/MEL,
clínica→**DF**) → la predicción es artefacto del prompt, no de la imagen. **Reenmarcado:** no es domain
gap dermatoscopía, sino **incapacidad general de grano fino**. Cierra la línea de clasificación VLM
(resultado negativo sólido); la contribución VLM queda del lado de la **generación de reportes**.

```bash
python scripts/mendieta/sync_up.py && python scripts/mendieta/submit.py all_classify_clinical
python scripts/mendieta/sync_down.py   # al volver
```

### Re-diagnóstico del class collapse — premisa de v3 falsificada — local
Sin jobs. Al empezar a implementar v3 (class-balanced sampling) se verificó la premisa contra los
datos reales y **se cayó**: el class collapse NO es por imbalance de entrenamiento.

**Evidencia (todo local, sobre datos/predicciones existentes):**
1. **Stage 2 (SkinCoT) está balanceado:** 23 clases DermNet, "Melanoma...Nevi and Moles" en puesto 9
   (76, 3.6%). **Stage 1 (SkinCAP):** 179 clases, melanocytic-nevi top 3.3%. Ninguno sesgado a NV/MEL.
2. **El colapso existe en zero-shot** (sens_macro ZS 0.12–0.18 ≈ 1/7), antes del fine-tuning → no
   lo causa SkinCoT.
3. **Cada combo colapsa a una clase arbitraria distinta:** LLaVA lik→MEL 59%, LLaVA CoT→VASC 81%,
   Mini lik→NV 99%, Mini CoT→MEL 97%. No es frecuencia (sería la misma clase) → incapacidad de
   discriminar dermatoscopía.
4. CNN supervisados sobre la misma HAM → F1=0.88 (HAM es discriminable; fallo VLM-específico).

**Diagnóstico correcto:** limitación de **dominio** (VLMs de foto clínica/texto no transfieren a
dermatoscopía). Es un hallazgo de tesis, no corregible por re-balanceo.

**Decisión: v3 (class weights) ANULADO.** No se implementa ni se envían jobs. Documentado en
[vlm_clasificacion_resul_v3 §5.4](resul/vlm_clasificacion_resul_v3_20260517.md), banner en
[plan v3](ideas/reportes_mejoras_v3_class_weights_plan_20260525.md), notas en
[reportes_resul_v2 §5](resul/reportes_resul_v2_20260517.md).

**Siguiente paso decidido:** (a) **confirmación afirmativa del domain gap** — evaluar VLM zero-shot
sobre foto clínica (SkinCAP mapeado a 7 clases HAM) vs dermatoscopía. Plan:
[vlm_domain_gap_clinica_plan_20260603.md](ideas/vlm_domain_gap_clinica_plan_20260603.md).
**En pausa / a futuro:** (b) iteración de *solo generación* (foco: reporte de la imagen; el estilo
CoT/commitment-line es secundario), problema independiente del collapse.

---

## 2026-06-02

### Análisis gen v2 (jobs 1154471-1154472) + decisión Camino B — Mendieta
Sin jobs nuevos. Análisis de los re-envíos de generación v2 (orden invertido) que terminaron en Mendieta.

**Ambos re-envíos volvieron a hacer TIMEOUT 48h**, esta vez muriendo **dentro de HAM10000**
(1154471 LLaVA: 2587/10015; 1154472 Mini: 6855/10015). **SkinCoT nunca alcanzado (0 reportes).**

**Causa raíz (el "fix de orden invertido" trató el síntoma):** el SLURM genera sobre las **10015
imágenes completas** de HAM (no el test split; el plan asumió ~1.5k, error ×7) y LLaVA genera a
~1,1 min/img (`max_tokens=512`, sin batch) → 10015 imgs ≈ 7,6 días, imposible en 48h. Regresión
extra: el SLURM v2 omitió `--label_csv`, dejando `gt_label` vacío en los reportes.

**Aproximación de métricas (sin re-correr cluster):** se reconstruyó `gt_label` localmente
(`enrich_reports.py`: `image_id → dx → nombre`) sobre el prefijo generado. El prefijo es
estadísticamente representativo (nevus ~69% ≈ full 66.9%). **Veredicto: NO CUMPLE GATING** —
diagnostic_consistency HAM regresa −0.084 (LLaVA 0.72→0.63) y −0.124 (Mini 0.35→0.23). Recall
sube en LLaVA (0.46→0.82, por fix A1) pero con costo de fidelidad diagnóstica (hedging/CoT).
Nivel 1 (BLEU/CIDEr) plano y ~0.

**Resultados:** [reportes_resul_v2_20260517.md §4-§8](resul/reportes_resul_v2_20260517.md) completado.

**Decisión: Camino B** — pivotear a v3 sin re-correr v2 (su número de gating ya existe y falla).
La generación v3 debe bakear los fixes de scope (HAM→test split, re-agregar `--label_csv`,
recortar MM-SkinQA, evaluar `max_tokens` 512→256). El plan v3 se actualiza con estos fixes.

```bash
python scripts/mendieta/sync_down.py --reports
python scripts/evaluate_reports.py --model {llava_med,mini_vlm} --level {1,2} --dataset v2/{HAM10000,mmskin}
```

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
| [vlm_domain_gap_clinica_plan_20260603.md](ideas/vlm_domain_gap_clinica_plan_20260603.md) | Plan | Confirmación afirmativa domain gap (VLM ZS foto clínica vs dermatoscopía) |
| [vlm_domain_gap_clinica_resul_20260604.md](resul/vlm_domain_gap_clinica_resul_20260604.md) | Resultado | Domain gap NO confirmado → limitación general de grano fino; clasificación VLM cerrada |
| [dermlip_clasificacion_plan_20260604.md](ideas/dermlip_clasificacion_plan_20260604.md) | Plan | Agregar DermLIP (VL classifier derm-especializado, CLIP-style) — ¿resuelve la clasificación? |
| [dermlip_clasificacion_resul_20260605.md](resul/dermlip_clasificacion_resul_20260605.md) | Resultado | DermLIP ZS rompe el collapse (sens_macro 0.51 vs 0.14) — CUMPLE |
| [ensamble_clasificador_generador_plan_20260605.md](ideas/ensamble_clasificador_generador_plan_20260605.md) | Plan | Ensamble cascada clasificador→generador (grounding) — arregla clasificación + hedging de generación |
| [ensamble_resul_20260607.md](resul/ensamble_resul_20260607.md) | Resultado | Pilot 1 (grounding soft débil) + hallazgo reporte-vs-razonamiento (consistency inflada por el `<think>`) |
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
