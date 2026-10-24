# Registro de Ejecuciones

Ayuda-memoria cronológico de experimentos enviados a cluster, ordenado de más reciente a más antiguo.

---

## 2026-10-24

### DermLIP zero-shot con el protocolo oficial de Derm1M — **Sin jobs SLURM** (local, RTX 4070)
Plan `ideas/dermlip_zs_protocolo_plan_20261024.md`; resultado `resul/dermlip_zs_protocolo_resul_20261024.md`.
Prueba por lesión (1 503), plantillas (4 propias / 8 oficiales) × nombres de clase (propios / oficiales de
`zero_shot_metadata.py`). Control 0.377 / 0.510 (reproduce); oficial 0.716 de exactitud y 0.544 de sensibilidad
macro. Salida nueva `outputs/results/dermlip/dermlip_zs_protocolo.json`; nada sobrescrito.

```
../.venv/Scripts/python.exe scripts/dermlip_zs_protocolo.py
```

---

### Figuras por semilla del Cap. 4 — **Sin jobs SLURM** (local, CPU)
Dos funciones nuevas en `scripts/figuras_cap4.py`: `recall-clase-semillas.pdf` (sensibilidad por clase de las tres
semillas de los cuatro supervisados, `*_les_cwnone{,_s43,_s44}_test_results.json`) y `melanoma-semillas.pdf`
(`lesion_split_report.json`, `melanoma_semillas`). Las medias coinciden con las tablas que reemplazan. Sin
resultados nuevos.

---

### Seis figuras más para el Cap. 4 — **Sin jobs SLURM** (local, CPU)
Reorganización del Cap. 4 pedida por el autor (menos cifras en la prosa, más figuras). `scripts/figuras_cap4.py` (desde
`Codigo/`, con `.venv`) lee solo JSON de `outputs/results/` y escribe en
`Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion/`: `resumen-sensibilidad-macro`, `confusion-swin`,
`robustez-curvas`, `calibracion-swin`, `hiba-por-clase-swin` y `distribucion-vlm-generativos` (`.pdf`). Sin resultados
nuevos ni archivos sobrescritos. Lo que recalcula coincide con las tablas: sensibilidad macro de los generativos
(«desconocido» como error) Mini 0.144 / 0.181 / 0.123 / 0.141 / 0.145, LLaVA 0.156 / 0.157 / 0.112 / 0.137 / 0.045;
ECE de Swin 0.040 sin pesos y 0.376 con pesos; HIBA 0.716 → 0.424.

```
.venv/Scripts/python.exe scripts/figuras_cap4.py
```

---

### Costo de los clasificadores remedido con memoria de GPU — **Sin jobs SLURM** (local, RTX 4070)
`measure_cost.py` corregido: clases del proyecto con cabeza de 7 salidas (antes torchvision con 1 000, p. ej.
DenseNet121 8.0 M en vez de 6.96 M), autocast bf16 como la evaluación (`--dtype`, por defecto bf16) y pico de memoria
medido con `max_memory_allocated` (antes, estimación parámetros × 4 B + 0.5 GB). Los logs SLURM no traen el pico
(solo `nvidia-smi` al inicio). Dos corridas; la memoria coincide y los tiempos varían 5–15 %.

```
python scripts/measure_cost.py --output outputs/results/cost/cost_comparison_v3.json
python scripts/measure_cost.py --output outputs/results/cost/cost_comparison_v3_rep.json
```

Lote de 32 (pico, GB) / ms por imagen / img/s: Swin 0.522 / 11.05 / 1 353; ConvNeXt 0.407 / 4.99 / 1 739; ViT 0.678 /
5.72 / 904; DenseNet 0.216 / 19.89 / 1 700. Generadores sin cambios (16.4 / 26.2 / 3.4 s por reporte).
`cost_comparison{,_v2}.json` y `cost_latency.png` no se tocaron (la figura nueva es `cost_comparison_v3_latency.png`).

---

### Figuras del Cap. 4: curva ROC de melanoma y Grad-CAM en castellano — **Sin jobs SLURM** (local, CPU)
Dos figuras para la tesina, sin resultados nuevos ni archivos de `outputs/` sobrescritos. **ROC:** Swin-Tiny t06
semilla 42 (`swin_tiny_sweep_t06_les_cwnone_predictions.json`), umbral 0.211 de `lesion_split_report.json`;
recalcula AUC 0.919, argmax 0.701 / 0.922 y umbral 0.778 / 0.862, iguales a la fuente. **Grad-CAM:** mismas
funciones y selección que `scripts/interpretability.py` (primera imagen de cada clase, checkpoint
`swin_tiny_sweep_t06_les_cwnone`), solo con rótulos en castellano; las predicciones coinciden con la figura de
`interpretability_les/` (VASC → NV y BCC → MEL, las demás correctas). Scripts: `scripts/figura_roc_melanoma.py` y `scripts/figura_gradcam_tesina.py` (desde `Codigo/`);
salida en `Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion/{roc-melanoma-swin,gradcam-swin}.pdf`.

---

### Mini-VLM v3: descarga y evaluación parcial — TOKO 99257/99258 y Mendieta short (local)
**TOKO:** 99257 `TIMEOUT` a las 12 h (oracle 1 503/1 503 y 290 de DermLIP); 99258 `COMPLETED` el 21/10 14:50
(DermLIP 1 503/1 503). **Mendieta:** `skincot_test` 457/457 y `full_differential_les` 248/248 completos;
`full_swin_les` 963/1 503 y `full_baseline` 372/1 503. Los 12 tramos que quedan en `short` (Swin 13–18 y 20–22
de 25; baseline 5–7 de 28) se liberaron el 20/10 con `ExcNodeList=ivb02,ivb11`, volvieron a fallar en ivb14
(`user_env_retrieval_failed_requeued_held`, Restarts=2) y siguen retenidos. Los jobs de `multi` (1179986–1179990)
siguen `PENDING` por prioridad. Reportes bajados por `tar` sobre ssh a `generated_reports/mini_vlm/v3/<brazo>`.

```
python scripts/evaluate_reports.py --model mini_vlm --level 1 --dataset v3/skincot_test --strip-reasoning --output_dir outputs/results/level1_test/skincot_test
```

Consistencia oficial v3 − v2 (mismas imágenes): oracle −0.033 [−0.042, −0.023] (0.967; el diagnóstico queda
dentro del `<think>` cortado), DermLIP +0.021, Swin por lesión −0.007 (n.s., n = 963), diferencial +0.032 (n.s.).
Nivel 1 SkinCoT: 80/457 reportes vacíos al quitar el `<think>`; sobre 349 pares, v3 queda por debajo de LLaVA-Med
v2 en las cinco métricas (BERTScore 0.781 frente a 0.797).
**Resul:** [mini_vlm_lora_llm_resul_v3_20261024.md](resul/mini_vlm_lora_llm_resul_v3_20261024.md) (parcial,
NO CUMPLE por incompleto).

---

## 2026-10-20

### Mini-VLM v3 en short: nodo ivb02 excluido y primer vistazo parcial — Mendieta jobs 1180970–1181064 (local)
Durante la noche terminaron 16 tramos (todos `COMPLETED`; 1180965 `TIMEOUT` con lo que llegó a generar) y desde
~01:17 no arrancó ninguno más: 38 quedaron `user_env_retrieval_failed_requeued_held`, 33 de los 40 reintentos
fallidos en ivb02 y 7 en ivb11. El script pasa a `#SBATCH --exclude=ivb02,ivb11` (local y remoto) y a los jobs
encolados se les aplicó `scontrol update ExcNodeList=ivb02,ivb11` + `scontrol release` (también a 1179986–1179990).

Reportes al cortar (remoto y bajados a `generated_reports/mini_vlm/v3/<brazo>`): `skincot_test` 255/457,
`full_differential_les` 50, `full_swin_les` 300/1 503, `full_baseline` 283/1 503. Mediana de ~207 palabras (34 con
el checkpoint sin cargar), así que el modelo cargado es v3. Comparación preliminar sobre las mismas imágenes
(script de borrador fuera del repo; métrica oficial: solo el reporte, matcher estricto, bootstrap pareado 2 000):

| Brazo | n | v3 | v2 | Δ [IC 95 %] |
|---|---|---|---|---|
| `full_swin_les` | 300 | 0.840 | 0.860 | −0.020 [−0.043, +0.003] |
| `full_differential_les` | 50 | 0.840 | 0.840 | 0.000 [−0.060, +0.060] |
| `full_baseline` | 283 | 0.194 | 0.187 | +0.007 [−0.053, +0.071] |

Nivel 1 en SkinCoT test (solo el reporte): v3 imita el formato de SkinCoT y abre `<think>` en 164/255 reportes;
con 384 tokens, **50/255 (20 %) quedan solo con razonamiento** (cortado o en bucle de `<think>`) y el reporte queda
vacío. LLaVA-Med v2, con el mismo presupuesto: 11/457 con `<think>`, 0 vacíos. Sobre los 193 pares con referencia y
reporte no vacío en ambos: v3 BLEU-4 0.061, ROUGE-L 0.145, BERTScore F1 0.780; LLaVA-Med 0.108, 0.193, 0.797. En los
brazos de HAM10000 el `<think>` aparece en 25 % (swin_les) y 21 % (baseline) de los reportes, sin dejar ninguno vacío.
**Resul:** pendiente (faltan tramos; la decisión sobre v3 es del autor).

**TOKO:** la copia del checkpoint se retoma por la máquina local en tramos de 1 GiB que se saltean si ya están
completos (borrador `toko_chunks.sh`, fuera del repo); al terminar arma el archivo, verifica el md5 y envía
`slurm/toko/v5/gen_mini_v3.sh` dos veces con `afterany`. Copia completa a las 18:51 (9 tramos, ~50 min, md5
`de25b7e4…` igual en origen y destino). **TOKO jobs 99257** (en gpu1 desde las 18:54, empieza por oracle) **y
99258** (`afterany:99257`). **Resul:** pendiente.

## 2026-10-19

### Mini-VLM v3 troceado en la partición short (prueba de 10 tramos) — Mendieta jobs 1180951–1180978
Los jobs de `multi` de v3 (1179986–1179990) siguen `PENDING` (Priority) desde el 18/10; `sbatch --test-only`
estima el arranque de la cascada en `multi` para el 28/10 y el de un job de 1 h en `short` para la misma noche
(`short` tiene `PriorityJobFactor=100`, `multi` 0). Cambios: `generate_report.py --shard K/N` (procesa el tramo K
de N tras `--limit`) y `slurm/mendieta/v5/gen_short_mini_v3.sh` (un tramo de un brazo de generación de v3, mismos
argumentos que cascade/extra/level1_test, 5 CPU y 32 GB en vez del nodo entero; Mini-VLM usa ~25 GB). Subidos por
`scp` (md5 verificado; copia `generate_report.py.bak_20261019` en remoto).

Un primer envío de todos los brazos en 148 tramos (1180803–1180950) se canceló entero antes de generar nada: el
autor pidió probar con 10, y los que arrancaron fallaron con `user env retrieval failed requeued held`. La causa es
el nodo ivb11 (en ivb10 e ivb12 arrancan bien), así que el script lo excluye (`#SBATCH --exclude=ivb11`). Prueba
vigente: tramos 0–9 de 16 de `full_baseline` (~94 imágenes cada uno), enviados como `submit.py`, con
`. /etc/profile` antes de `sbatch`:

```
for k in $(seq 0 9); do sbatch --export=ALL,ARM=full_baseline,SHARD=$k/16 slurm/mendieta/v5/gen_short_mini_v3.sh; done
```

**Checkpoint v3 sin cargar (bug, corregido).** Esos 10 tramos (7 completos, 742 reportes) iban a ~6 s por reporte
con textos de ~34 palabras y sin diagnóstico, frente a 160 en v2: era Phi-3.5-vision base. El reintento por OOM
de 1179985 reusó el modelo ya envuelto por PEFT y el checkpoint guardó las claves como
`model.base_model.model.base_model.model.…`; `generate_report.py` cargaba con `strict=False`, así que ninguna de
las 753 claves entraba y no avisaba. Los adaptadores son uno solo (160 tensores LoRA = 96 de CLIP + 64 de
`qkv_proj`; 31 457 280 entrenables), así que el entrenamiento vale: solo cambia el nombre. v2 no tiene el prefijo
doble y sus resultados no cambian. Arreglo: `src/training/lora_config.py` (`normalize_peft_keys`,
`load_finetuned_state_dict`: colapsa el prefijo y falla si queda un adaptador sin cargar), usado por
`generate_report.py` y `train_vlm_classify.py` (este cargaba estricto, así que 1179988–1179989 habrían fallado
con error). Verificado sin GPU: las claves normalizadas de v3 = las de v2 + 64 LoRA de `qkv_proj`, con
`qkv_proj.weight` → `qkv_proj.base_layer.weight`. Subidos por `scp` (md5 verificado; copias `*.bak_20261019` y
`generate_report.py.bak_20261019b`). Los 742 reportes inválidos quedan apartados en
`generated_reports/mini_vlm_v3/_invalido_ckpt_sin_cargar_full_baseline/` (remoto). Los jobs de `multi`
estuvieron retenidos (`scontrol hold`) mientras tanto y se liberaron con el código corregido.

Con el arreglo (1180965, tramo 0/16): «0 claves faltantes, 0 sobrantes», reportes de ~200 palabras con diferencial
razonado y ~50 s por reporte, así que 94 imágenes no entran en 1 h. El resto de la prueba va en tramos de ~54
(1/28 a 9/28, jobs 1180970–1180978); un tramo cortado se completa con cualquier partición posterior porque se
saltean los reportes ya válidos. La clasificación (1179988–1179989) no se trocea. **Resul:** pendiente.

**Prioridad para el Cap. 3 (decisión del autor).** Lo indispensable es confirmar que v3 es la configuración final:
la pérdida de validación de la etapa 2 baja de 1.334 (v2, 1153597) a 0.960 (v3, 1179985; LLaVA-Med 0.939). Se
envían primero SkinCoT test (Nivel 1, 9 tramos, 1181026–1181034), el nivel diferencial (5, 1181035–1181039) y
Swin por lesión (25, 1181040–1181064); los 9 tramos de `full_baseline` pasan a `nice=500`. El resto (baseline,
recuperación, ablaciones, MM-Skin) queda para los Caps. 4–5; para el Nivel 1 de MM-Skin y, si hace falta, para la
recuperación alcanza un subconjunto fijo de ~500 imágenes.

**TOKO** (`slurm/toko/v5/gen_mini_v3.sh`, nuevo): oracle y dermlip completos (1 503 c/u), brazos que Mendieta no
tiene asignados. Partición `gpu`, límite 12 h, así que se encadenan dos envíos (`afterany`). Subidos
`generate_report.py`, `lora_config.py` y `clinical_ner.py` (los únicos distintos del local; copias
`*.bak_20261019`), `full_dx_{oracle,dermlip}.csv` y la configuración LoRA. El checkpoint (8.7 GB, md5
`de25b7e4…`) va de Mendieta a TOKO por la máquina local (Mendieta no tiene clave para TOKO), con un script que
verifica el md5 y recién entonces envía los dos jobs. **Postergado:** la copia se cortó a 1.4 GB porque había que
apagar la máquina local; se borró el `.part` y no se envió nada a TOKO (oracle y dermlip son para el Cap. 5).

### Nivel 1 de LLaVA-Med v2 sobre las particiones de prueba — descarga de Mendieta job 1179991 (local)
1179991 termina `FAILED` tras 30 h, pero la generación está completa: SkinCoT 457/457 y MM-Skin 1 650/1 653. Las 3
que «faltan» son entradas `bk7_.DS_Store`, `bk8_.DS_Store` y `bk10_.DS_Store` de `mmskin_splits.json` (basura de
`caption.csv`), así que el control final del script falla en falso. Corregido en `slurm/mendieta/v5/level1_test.sh`
(espera 1 650); 1179990 (Mini-VLM v3) ya se envió con la copia anterior y terminará igual. Reportes bajados por
`tar` sobre ssh a `generated_reports/llava_med/v2/{skincot,mmskin}_test`, log en `outputs/slurm_logs/level1/`.

```
python scripts/evaluate_reports.py --model llava_med --level 1 --dataset v2/skincot_test --strip-reasoning --output_dir outputs/results/level1_test/skincot_test
python scripts/evaluate_reports.py --model llava_med --level 1 --dataset v2/mmskin_test  --strip-reasoning --output_dir outputs/results/level1_test/mmskin_test
```

Se descartan los pares sin referencia: en SkinCoT, 31 textos que están enteros dentro de `<think>` y no dejan
referencia al quitarlo (quedan 426); en MM-Skin, 236 filas de `caption.csv` sin descripción (quedan 1 414).

| LLaVA-Med v2 | n | BLEU-4 | ROUGE-L | METEOR | CIDEr | BERTScore F1 |
|---|---|---|---|---|---|---|
| SkinCoT test | 426 | 0.102 | 0.191 | 0.329 | 0.054 | 0.797 |
| MM-Skin test | 1 414 | 0.001 | 0.037 | 0.088 | 0.009 | 0.669 |

MM-Skin coincide con el subconjunto de prueba del recálculo del 12/10 (n = 381, BERTScore 0.670). Falta Mini-VLM
v3 (1179990, `PENDING`).

---

## 2026-10-18

### Verificaciones del Cap. 3 contra el código — **Sin jobs SLURM** (local)
Sale de contrastar el Cap. 3 con el código y los registros. Mendieta: 1179986–1179990 siguen `PENDING`
(Priority) y 1179991 corre hace 21 h; el Cap. 3 describe Mini-VLM v3 y lo marca con `\pendiente`.

- **Calibración post-hoc del split por lesión regenerada** (`posthoc_calibration.py --glob-lesion` →
  `outputs/results/calibration/posthoc_calibration.json`; no estaba en local ni en TOKO/Mendieta). Reproduce el
  registro del 26/09: Swin t06 ECE 0.040 → TS 0.027 (T = 0.85) → VS 0.014; ConvNeXt t02 0.040 → 0.027 → 0.033.
- **HIBA por modalidad versionado** (`scripts/hiba_por_modalidad.py`, nuevo → `outputs/results/hiba_por_modalidad.json`).
  Las 1 616 imágenes se alinean por posición con `metadata.csv` (verificado con `y_true`). Swin 0.624 / 0.263 de
  exactitud (dermoscópica / clínica), ConvNeXt 0.632 / 0.283: coincide con la revisión del 03/10. Todas las
  corridas `*_predictions_hiba.json` usan las mismas 1 616 imágenes.
- **Piloto de plantillas recalculado con el matcher estricto** (LLaVA-Med, 100 imágenes, sin `<think>`):
  noreasoning 0.86, confirmed 0.69, conclude 0.58, dxfirst 0.50, baseline 0.46. El orden no cambia; si además se
  quita el `<think>` sin cerrar, noreasoning sigue en 0.86 y las demás caen a 0.05–0.47.
- **`<think>` sin cerrar** (`THINK_RE` exige el cierre): solo afecta a LLaVA-Med. En `full_differential_les`, 144 de
  248 reportes; la consistencia estricta pasaría de 0.677 a 0.407 si se quitara hasta el final. En los demás brazos
  de LLaVA-Med son 8–30 de 1 503 (diferencias ≤ 0.006). Mini-VLM y SkinVL-MM: ninguno.
- **`THINK_RE` corregido y LLaVA-Med re-evaluado.** La expresión de los siete scripts de medición
  (`ensemble_bootstrap`, `per_class_ensemble`, `error_taxonomy`, `rag_les_eval`, `level1_mmskin_recalc`,
  `generate_template_report`, `evaluate_reports --strip-reasoning`) pasa a `<think>.*?(?:</think>|$)`: un bloque que
  el límite de 384 tokens dejó abierto se quita hasta el final. Copias previas en
  `outputs/results/_pre_think_fix_20261018/`. Re-ejecutados `ensemble_bootstrap.py --model llava_med --anchor les
  --report_only --strict`, `per_class_ensemble.py --strict` (3 generadores → `per_class_les_strict/`),
  `uncertainty_analysis.py --model llava_med --anchor les` y `error_taxonomy.py --models llava_med`
  (→ `error_taxonomy_les/llava_med/`). Cambios (LLaVA-Med): Swin 0.749 → 0.745, oracle 0.860 → 0.854, DermLIP
  0.345 → 0.340, sin anclaje igual (0.582). **Pipeline frente a grounding simple (n = 1452): +0.034 [+0.020,
  +0.048] → −0.011 [−0.025, +0.003], n. s.**; diferencial frente a forzado (n = 248): +0.198 → −0.065 [−0.141,
  +0.016], n. s.; pipeline − sin generador −0.110 → −0.160. Con LLaVA-Med el ruteo deja de mejorar el reporte:
  la ganancia anterior venía de razonamiento sin cerrar que nombraba los candidatos. Mini-VLM y SkinVL-MM sin
  cambios. Pendiente: `experimentacion.tex:82` conserva la cifra anterior (+0.056).
- **Partición de SkinCoT:** 18 imágenes figuran en dos carpetas de enfermedad con textos distintos; el split por id
  deja 2 136 / 463 / 460 pares (lo que cargó el entrenamiento) y 3 ids de prueba también en train o val
  (`lichen-planus-89`, `molluscum-contagiosum-144`, `alopecia-areata-23`).

---

## 2026-10-17

### DenseNet121 y ViT-B/16 moderna: descarga y análisis — **Sin jobs SLURM** (local)
Resul: [densenet_vit_moderna_resul](resul/densenet_vit_moderna_resul_20261017.md) (cierra el plan del 12/10;
veredicto **CUMPLE**). Descarga por `scp` de los 18 JSON de las 6 corridas y de los `.out` 99007–99012 (no
`sync_down`, para no pisar `outputs/results/` local con copias remotas).

- **Tests estadísticos:** `statistical_tests.py --models` con los ganadores `_les`, DenseNet121 t02 y ViT-B/16 t06
  modernos (semilla 42), DermLIP ZS y VLM ZS → `outputs/results/statistical_tests_les_v2.json` (el `_les` anterior,
  con los legacy, se conserva). Swin vs ViT p = 0.42; Swin vs DenseNet p = 0.021, ns con Holm.
- **Informe:** `scripts/densenet_vit_moderna_report.py` (nuevo) → `outputs/results/densenet_vit_moderna_report.json`:
  media ± sd en test y validación, receta anterior frente a moderna y Holm sobre las dos familias de 21 pares.
  ViT-B/16 F1m 0.707 ± 0.025 (Swin 0.733 ± 0.026), DenseNet121 0.655 ± 0.017.
- **Tabla SOTA:** `Docs/tabla_resultados_sota/tablas_comparativas_sota_v34.tex`.

---

## 2026-10-12

### DenseNet121 y ViT-B/16 con la receta moderna (split por lesión) — TOKO jobs 99007–99012
Plan: [densenet_vit_moderna_plan](ideas/densenet_vit_moderna_plan_20261012.md). Los dos modelos que quedaron con la
receta legacy se entrenan con la moderna y el trial ganador de su familia, sin pesos por clase, semillas 42/43/44:
DenseNet121 ← t02 de ConvNeXt (99007–99009), ViT-B/16 ← t06 de Swin (99010–99012). Cambio de código:
`submit_sweep.py --model` acepta `densenet` y `vit`. Código remoto idéntico al local (md5 sin CRLF); sin `sync_up`.

```
python scripts/toko/submit_sweep.py --model densenet --lesion-split --class-weights none --trials t02 --seeds 42 43 44
python scripts/toko/submit_sweep.py --model vit      --lesion-split --class-weights none --trials t06 --seeds 42 43 44
```

**Resul:** [densenet_vit_moderna_resul](resul/densenet_vit_moderna_resul_20261017.md). 6/6 OK el 14/10.

### Mini-VLM v3 (LoRA sobre el LLM) + Nivel 1 sobre las particiones de prueba — Mendieta jobs 1179985–1179991
Plan: [mini_vlm_lora_llm_plan](ideas/mini_vlm_lora_llm_plan_20261012.md). El LoRA de `stage2_mini_vlm_v2` quedó
solo en CLIP; v3 usa `--lora_target_modules qkv_proj q_proj v_proj` (31 457 280 entrenables, verificado sin cargar
pesos). Cambios de código: `train_vlm_stage2.py` (`--lora_target_modules`; métricas `stage2_metrics_<run>.json`),
`generate_report.py` (filtro de partición acepta nombres con extensión, como los de `mmskin_splits.json`;
referencias NaN ya no se guardan como «nan»), `evaluate_reports.py` (descarta referencias «nan»), `submit.py`
(`--after JOBID` → `afterok`, alias `*_v3`), `slurm/mendieta/v5/`. Subidos por `scp` (md5 verificado; copias
`*.bak_20261012` en remoto); no se usó `sync_up` porque la carpeta principal está en otra rama.

| Job | Alias | Depende de | Qué hace |
|---|---|---|---|
| 1179985 | `mini_s2_v3` | — | Etapa 2 v3 → `outputs/checkpoints/stage2_mini_vlm_v3/` |
| 1179986 | `cascade_mini_v3` | 1179985 | baseline, swin_les, oracle, dermlip (1503) + differential_les (248) → `generated_reports/mini_vlm_v3/` |
| 1179987 | `extra_mini_v3` | 1179985 | rag_les, swin_rag_les (1503) + oracle_noimage, wrong_swap (400) |
| 1179988 | `classify_mini_v3_lik` | 1179985 | Clasificación por verosimilitud → `results/mini_vlm/v3/` |
| 1179989 | `classify_mini_v3_cot` | 1179985 | Clasificación CoT → `results/mini_vlm/v3/` |
| 1179990 | `level1_mini_v3` | 1179985 | SkinCoT test (457) + MM-Skin test (1653) |
| 1179991 | `level1_llava_v2` | — | Ídem con LLaVA-Med v2 → `generated_reports/llava_med/v2/{skincot,mmskin}_test` |

**Envío:**
```
python scripts/mendieta/submit.py mini_s2_v3 --no-sync                       # 1179985
python scripts/mendieta/submit.py after_mini_v3 --no-sync --after 1179985    # 1179986-1179990
python scripts/mendieta/submit.py level1_llava_v2 --no-sync                  # 1179991
```

**Locales del mismo día (sin SLURM):** Nivel 1 de MM-Skin recalculado sin las referencias «nan»
(`scripts/level1_mmskin_recalc.py`, nota en [reportes_resul_v2](resul/reportes_resul_v2_20260517.md) §4.1);
latencia de generación desde las corridas comparables del re-anclaje (`measure_cost.py`, nota en
[costo_resul](resul/costo_resul_20260705.md)): Mini-VLM 16.4 s, LLaVA-Med 26.2 s, SkinVL-MM 3.4 s por reporte.

**Resul:** pendiente hasta que bajen los jobs.

## 2026-10-11

### Verificaciones para los pendientes del Cap. 3 — **Sin jobs SLURM** (local)
Resul: [verificaciones_cap03_resul](resul/verificaciones_cap03_resul_20261011.md) — **CUMPLE**. Se bajaron los logs
1153597/1153598 (stage 2 v2) y se calcularon con `scripts/verificaciones_cap03.py` y
`scripts/verificaciones_cap03_vlm_ci.py` los IC de HIBA, el bootstrap por lesión, Holm y los IC de los VLM ajustados.
Hallazgos: el LoRA de Mini-VLM entrena solo el codificador visual (6 291 456 parámetros; Phi-3.5 fusiona la atención
en `qkv_proj`); las métricas de Nivel 1 de MM-Skin incluyen 539/175 referencias «nan» y no usan su partición; el
piloto de *noreasoning* mezcló 67 train / 10 val / 17 test; Wilcoxon por clase no sobrevive a Holm.

## 2026-10-03

### RAG con el índice por lesión + métrica oficial de la cascada — Mendieta job 1179315
Decisiones del autor sobre la [revisión](resul/revision_experimentacion_20261003.md) (§5): métrica oficial
solo reporte + matcher estricto; H6 se lee como propiedad del ruteo; RAG se regenera; el ancla se declara
como limitación.

- **Métrica oficial implementada** (local): `clinical_ner.diagnostic_consistency_flags(strict=True)` con los
  términos de la taxonomía (`CLASS_TERMS` movido a `clinical_ner.py`; taxonomía idéntica);
  `ensemble_bootstrap.py --report_only --strict` (+ línea base sin generador) y
  `per_class_ensemble.py --strict`. Cifras: Mini 0.798 → 0.849, LLaVA 0.687 → 0.749, SkinVL 0.794 → 0.846;
  pipeline − sin generador: Mini −0.003 (n. s.), LLaVA −0.110. `tab:cascada` (v33) actualizada.
- **RAG regenerado:** plan [rag_les_plan](ideas/rag_les_plan_20261003.md). Script
  `slurm/mendieta/v4/rag_les_mini_vlm.sh` (alias `rag_les`): `full_rag_les` y `full_swin_rag_les`, Mini-VLM,
  1503 cada uno, índice `rag_context_les.csv`, con `run_arm` y prueba de `/scratch`. Subidos por `scp` el
  `.sh` y `rag_context_les.csv` (md5 verificado); `generate_report.py` remoto idéntico al local.

**Envío:**
```
python scripts/mendieta/submit.py rag_les --no-sync   # 1179315 (inicio estimado 2026-10-04 15:45)
```

**Resul (2026-10-11):** [rag_les_resul](resul/rag_les_resul_20261011.md) — **CUMPLE**. Job COMPLETED (21 h),
2 × 1503 reportes, bajados con `sync_down.py --reports`; evaluación local con `scripts/rag_les_eval.py`
(`outputs/results/rag_les_eval.json`). RAG solo 0.669 (+0.506 sobre no anclar, −0.180 frente al *grounding*
Swin 0.849, −0.112 frente al voto kNN impreso 0.781); Swin + RAG 0.862 (+0.013 [+0.007, +0.019] sobre Swin),
ganancia que viene de nombrar la clase de los vecinos (consistencia exclusiva −0.055 frente a Swin impreso).

### Revisión profunda de la experimentación — **Sin jobs SLURM** (local + segunda opinión)
Resul: [revision_experimentacion](resul/revision_experimentacion_20261003.md) — **CUMPLE con correcciones**.
Revisión propia + auditoría independiente (Fable 5.1). Clasificación, partición, selección y titulares
reproducidos sin fuga ni selección sobre test. Hallazgos:

- **Pipeline avanzado = ruteo, no generador:** imprimir los candidatos sin generador da 0.904 sobre las
  1452 no derivadas; Mini-VLM 0.901 (−0.003, n. s.), LLaVA-Med 0.793 (−0.110). El diferencial recibe {Swin,
  kNN}, no el top-2.
- **`ensemble_bootstrap.py` contaba texto `<think>`** (solo LLaVA-Med): pipeline +0.056 → +0.032 solo reporte;
  v3 +0.125 → +0.092. Nuevo `--report_only` (salida `*_report_only.json`).
- **Matcher de consistencia por subcadena** («mel» en «melanocytic», «nv» en «invasion»): el «12 %» de Mini
  con ancla equivocada es artefacto (1.7 % estricto). Δ del re-anclaje sin cambios.
- **RAG con índice con fuga:** kNN 0.831 → 0.781 con índice por lesión; en el subconjunto limpio RAG solo
  queda −0.087 [−0.136, −0.038] bajo el grounding Swin.
- **HIBA:** 346/1616 clínicas (acc Swin 0.263 vs 0.624 dermoscópicas); fototipos I–IV. Corregido en v33.
- **Ruteo mal descrito** (no usa calibración ni τ). Corregido en v33 y en el resul del re-anclaje.
- **Por clase** (`per_class_ensemble.py` ahora lee la etiqueta de la metadata → `per_class_les/`): la mejora
  del ancla nueva es de nevus; melanoma, BCC, AK y vascular bajan.

**Pendiente del autor:** métrica oficial (solo reporte + estricto), lectura de H6, RAG, punto de operación
del ancla.

### Re-anclaje: LLaVA-Med terminado y evaluado; cierre del re-anclaje — Mendieta 1178901
Terminó el 2026-10-01 18:08 (12 h 56 min, exit 0; el `run_arm` nuevo no marcó fallas): `full_swin_les`
1503/1503 y `full_differential_les` 248/248. Bajado por `tar` sobre `ssh`; logs en
`outputs/logs/llava_med/1178901.*`. Evaluado localmente con `C:\Python313\python.exe`
(`ensemble_bootstrap.py --model llava_med --anchor les`, `uncertainty_analysis.py --model llava_med
--anchor les`, `error_taxonomy.py` → `error_taxonomy_les/llava_med/`). No queda ningún job en cola.

- **Grounding con el Swin nuevo:** consistencia 0.696 → **0.752**, Δ +0.057 [+0.039, +0.075]; frente a
  oracle −0.099 (antes −0.156); frente a sin anclaje +0.107 (antes +0.051).
- **Pipeline avanzado vs grounding simple (n = 1452):** 0.816 vs 0.760, Δ **+0.056** [+0.043, +0.070]
  (antes +0.125). Subconjunto diferencial (n = 248): 0.843 vs 0.516, Δ +0.327 (antes +0.542).
- **Taxonomía consciente del nivel:** dx incorrecto 9.5 % → 9.0 % (antes 13.5 % → 7.0 %). Dentro del
  nivel diferencial, LLaVA-Med deja afuera el gt en 61/248 reportes (antes 61/334), mientras que el
  grounding simple pasó de 155 a 69 errores en ese subconjunto: con LLaVA-Med el pipeline ya casi no
  corrige diagnósticos, solo convierte hedging/contradicciones en diferenciales. Abstención: 19 dx
  incorrectos evitados de 51.
- **Taxonomía report-only:** dx incorrecto 0.14 → 0.10; ok 0.35 → 0.38.
- **Tabla SOTA v33:** tabla nueva `tab:cascada` (tres generadores × anclaje + pipeline avanzado) y
  `tab:posicionamiento` corregida, que todavía tenía los números de la partición por imagen.

**Resul:** [reanclaje_cascada_resul](resul/reanclaje_cascada_resul_20261003.md) — veredicto **CUMPLE**
(la ganancia del pipeline avanzado baja a +0.043/+0.056).

## 2026-09-27

### Re-anclaje: Mini-VLM terminado y evaluado — Mendieta 1177953
Terminó el 2026-09-27 02:26 (8 h 08 min, exit 0, `.err` sin errores): `full_swin_les` 1503/1503 y
`full_differential_les` 248/248. Bajado y evaluado localmente (`ensemble_bootstrap.py --anchor les`,
`uncertainty_analysis.py --anchor les`, `error_taxonomy.py` → `error_taxonomy_les/mini_vlm/`).
**LLaVA-Med 1178901 sigue en cola** (prioridad; inicio estimado por SLURM: 2026-09-29 12:18).

- **Grounding con el Swin nuevo:** consistencia diagnóstica 0.812 → **0.864**, Δ +0.052 [+0.033, +0.071]
  (el ancla pasó de 0.795 a 0.847). Frente a oracle: −0.135 [−0.152, −0.117] (antes −0.187).
- **Pipeline avanzado vs grounding simple (n = 1452 no derivadas):** 0.916 vs 0.873, Δ **+0.043**
  [+0.031, +0.054]. Sigue siendo significativo, pero la ganancia es un tercio de la anterior (+0.118):
  con un ancla mejor calibrada hay menos casos inciertos (248 diferenciales en vez de 334) y el grounding
  simple ya acierta más.
- **Subconjunto diferencial (n = 248):** 0.855 vs 0.605 forzado, Δ +0.250 [+0.190, +0.310] (antes +0.509).
- **Taxonomía consciente del nivel:** dx incorrecto 13.6 % → 9.0 %; la repetición sigue amplificándose en
  el nivel diferencial con Mini-VLM (0.5 % → 3.3 %), como en la versión anterior. Derivar evita 20 dx
  incorrectos de las 51 abstenciones.
- **Taxonomía report-only:** dx incorrecto 0.20 → 0.15; ok 0.38 → 0.40.
- **Entorno local:** el `python` del PATH pasó a ser 3.14 (sin pandas); todo el análisis corre con
  `C:\Python313\python.exe`, el mismo de las corridas anteriores.

**Resul:** [reanclaje_cascada_resul](resul/reanclaje_cascada_resul_20261003.md).

## 2026-09-26

### Análisis locales migrados al split por lesión + resul — **Sin jobs SLURM** (local)
Resul: [split_lesion_resul](resul/split_lesion_resul_20260926.md) (cierra los planes del 12/09 y del 17/09;
veredicto **CUMPLE**, con Swin fuera del criterio de estabilidad: sd sens. macro 0.025 > 0.02).

- **Ensamble de clasificadores:** `classifier_ensemble.py --preset les` (antes solo modern_v3). Salida
  nueva en `outputs/results/classifier_ensemble_les/`; el preset v3 reproduce su 0.862. Swin+ConvNeXt
  por semilla: F1m 0.747±0.005, sens. macro 0.706±0.002 (Swin solo 0.733±0.026 / 0.692±0.025).
- **Tests estadísticos:** `statistical_tests.py --models` con los ganadores `_les`, legacy `_les`, DermLIP
  ZS y VLM ZS → `outputs/results/statistical_tests_les.json`. Swin vs ConvNeXt no significativo
  (McNemar p = 0.87); Swin > DenseNet/ViT (p < 0.001).
- **Grad-CAM:** `interpretability.py` tenía el mismo error de preprocesamiento que las perturbaciones
  (`center_crop=False` en modelos modern) y superponía el mapa sobre la imagen sin recortar. Corregido
  (`--no-center-crop` para el modo legacy; carga con `strict=True`); default al Swin `t06_les`, salida en
  `interpretability_les/`. La saliencia de DermLIP es un artefacto de grilla de parches en ambas versiones.
- **Melanoma:** ya estaba migrado dentro de `lesion_split_report.json`; no se rehízo.
- **Embeddings congelados + clásicos (DermLIP vs Swin-ImageNet):** `embeddings_classical.py --splits_file`
  (antes fijo a la partición aleatoria; agrega F1 macro) → `embeddings/embeddings_classical_les.json`.
  Sens. macro DermLIP vs ImageNet: SVM 0.673 vs 0.466, LogReg 0.689 vs 0.538, RF 0.515 vs 0.162 (antes
  SVM 0.788 vs 0.579). El SVM de DermLIP reproduce el 0.673 de `dermlip_split_eval.json`. H4 se sostiene.
- **Ejemplos de perturbaciones:** `robustness_examples.py` tenía fijo el Swin v3 y la tendencia v3 (ruido y
  JPEG fallan primero). Con el Swin nuevo la tendencia es ruido y desenfoque primero, JPEG y resolución
  toleradas hasta sev4–5; checkpoint y tendencia pasan a argumentos. Salida `robustness_examples_les.png`
  (ISIC_0025567, ISIC_0032013; todas las fallas caen en NV).
- **SkinVL `full_swin_les` (1177955) bajado y evaluado:** consistencia diagnóstica 0.802 → **0.847**
  (= exactitud del ancla), Δ +0.045 [+0.025, +0.064]; taxonomía: ok 0.79 → 0.85, dx incorrecto 0.20 → 0.15.
  `outputs/results/ensemble_bootstrap_skinvl_les.json`, `error_taxonomy_les/skinvl/`.
- **Los reportes `_les` no traen `gt_label`**: los `reanchor_*.sh` no pasan `--label_csv`. No afecta la
  generación; `error_taxonomy.py` ahora lo toma de la metadata de HAM cuando falta (antes daba 100 %
  `dx_incorrecto`). `ensemble_bootstrap.py` y `uncertainty_analysis.py` ya usaban la metadata.
- **Melanoma por semilla:** `lesion_split_report.py` agrega `melanoma_semillas` (el resto del JSON queda
  idéntico). Esp ≥ 0.85 en val: sens Swin 0.796 ± 0.036, ConvNeXt 0.794 ± 0.012, ensamble 0.828 ± 0.007;
  AUC 0.921 / 0.909 / 0.926. Con *argmax*, Swin 0.623 ± 0.071: el umbral en val también estabiliza.
- **Figuras de soporte del Cap. 4:** (1) `evaluate_calibration.py --hist --labels` → `calibration_les/`:
  ganadores sin pesos ECE 0.040, mismo trial con pesos por clase 0.376 (Swin) / 0.211 (ConvNeXt), con 76–79 %
  de predicciones de confianza < 0.5; (2) `interpretability.py --no-dermlip` → `interpretability_swin.png`;
  (3) `plot_classification_summary.py` (nuevo) → `classification_summary_les.png`, reemplaza a la
  `F1_clasificacion.png` hecha a mano, que además rotulaba como «gen ZS» barras de *likelihood*.
- **Tabla SOTA v33** (`Docs/tabla_resultados_sota/tablas_comparativas_sota_v33.tex`): filas propias de
  clasificación (media ± sd de 3 semillas + ensamble), melanoma y HIBA con la partición por lesión; nota de
  comparabilidad con el efecto medido de la fuga. Tablas de generación sin cambios hasta el re-anclaje.
- **Preparado para Mini-VLM y LLaVA-Med:** `ensemble_bootstrap.py` y `uncertainty_analysis.py` aceptan
  `--anchor les` (brazos `*_les`, `uncertainty_3tier_les.csv`, salida con sufijo `_les`); el modo v3
  reproduce exactamente sus JSON anteriores.

### Re-anclaje: estado real de 1177953-1177955 + reenvío de LLaVA-Med — Mendieta job 1178901
Los tres jobs del 2026-09-17 recién arrancaron el 2026-09-26 (cola).

- **1177955 (SkinVL `full_swin_les`): OK**, 1503/1503. Falta bajarlo.
- **1177953 (Mini-VLM):** corriendo (1110/1503 de `full_swin_les` a las 22:19; después, 248 diferenciales).
- **1177954 (LLaVA-Med): FALLÓ sin avisar.** `OSError: [Errno 5] Input/output error` en
  `/scratch/1177954` del nodo ivb17 al crear temporales (import de wandb/torch). El `.sh` no propagaba
  el error: SLURM lo marcó COMPLETED, exit 0, en 3 min y sin ningún reporte.
- **Arreglo en `slurm/mendieta/v4/reanchor_*.sh`:** (1) `/scratch` se prueba escribiendo un archivo, no
  solo con `mkdir`; si falla, `TMPDIR=/tmp`. (2) Cada brazo corre por `run_arm <out_dir> <n>`, que
  registra el código de salida de `generate_report.py` y cuenta los `*_report.json`; si algo falla, el
  job termina con exit 1 (FAILED). Probado localmente con un `PYTHON` falso. Subido solo el `.sh` por
  `scp` (sin `sync_up`, para no tocar el job de Mini-VLM en curso).

**Envío:**
```
python scripts/mendieta/submit.py reanchor_llava   # 1178901
```

**Resul:** [reanclaje_cascada_resul](resul/reanclaje_cascada_resul_20261003.md).

## 2026-09-17

### Decisión: el ganador del barrido se elige por F1 macro en validación
Cierra la tensión que quedaba abierta en la entrada del 2026-09-15. Plan:
`docs/ideas/criterio_seleccion_plan_20260917.md`. Sin jobs: es una decisión de selección sobre
resultados ya existentes.

- **El F1 ponderado queda descartado como criterio**: está dominado por NV (67 % de los datos) y
  excluía sistemáticamente las corridas con pesos por clase.
- **La sensibilidad macro sola también queda descartada**: ignora los falsos positivos, así que
  elegir por ella premia sobre-predecir las minoritarias. Con ese criterio Swin pasaba a
  `t02_les` y perdía 12 puntos de exactitud y 14 de F1 macro (0.755 → 0.611).
- **Se elige F1 macro en validación**: balanceado por clase y penaliza falsos positivos. La
  sensibilidad macro sigue siendo la métrica principal de reporte en test.
- **Ganadores con el criterio nuevo** (seed 42, sin TTA):
  - Swin-Tiny: `t06_les_cwnone`, **no cambia**; conserva las semillas 42/43/44.
  - ConvNeXt-Tiny: `t06_les_cwnone` → **`t02_les_cwnone`**, que mejora en todo respecto del
    anterior: acc 0.840 → 0.845, F1m 0.711 → 0.727, sensM 0.682 → 0.694, recall MEL 0.503 → 0.599.
- **Dos niveles de selección, solo cambia uno.** El *checkpoint* dentro de cada corrida se sigue
  eligiendo por F1 ponderado (`trainer.py:188`, `monitor: val_f1`); cambiarlo obligaría a reentrenar
  las 60 corridas. El documento tiene que decirlo con precisión.
- **Pendiente de ejecución:** semillas 43/44 y HIBA del ConvNeXt nuevo. Hasta que estén, su fila es
  de una sola semilla y la mejora de recall MEL (+0.096) es de ~1.5 desvíos, sugestiva y no firme.

**Resul:** [split_lesion_resul](resul/split_lesion_resul_20260926.md).

### Semillas + HIBA del criterio nuevo, y dos arreglos aguas abajo — TOKO jobs 98243-98246
Los 4 jobs terminaron el 2026-09-17 sin errores (early stopping ~17 épocas, 3-8 min cada uno).
`sync_down.py` + `scripts/lesion_split_report.py`.

- **Ganador nuevo de ConvNeXt con tres semillas** (`t02_les_cwnone`): acc 0.843±0.005,
  F1w 0.840±0.005, **F1m 0.727±0.007**, sensM 0.691±0.009, recall MEL 0.553±0.042.
  Contra el anterior (`t06_les_cwnone`): F1m 0.723±0.013, sensM 0.700±0.018, MEL 0.535±0.028.
  **Criterio de éxito del plan: cumplido** — el F1 macro sube (0.723 → 0.727) y le baja la varianza
  a la mitad; la sensibilidad macro cede 0.009, dentro del desvío anterior.
- **La mejora de melanoma de la semilla 42 era ruido.** +0.096 con una semilla (0.503 → 0.599) queda
  en +0.018 con tres (0.535 → 0.553), dentro del ±0.042. Segundo caso del mismo fenómeno que la
  entrada del 2026-09-15: las métricas de clases minoritarias no se leen con una semilla.
- **Primera validación externa en HIBA con el split por lesión.** Las únicas corridas con HIBA que
  existían eran del barrido por imagen (`convnext_tiny_sweep_t06_hiba`, `swin_tiny_sweep_t08_hiba`).
  Ahora: Swin HAM 0.847/sensM 0.716 → HIBA (n=1616) **0.546/0.424**; ConvNeXt HAM 0.845/0.694 →
  HIBA **0.558/0.447**. Caída de ~30 puntos de exactitud en los dos, del mismo orden. El recall de
  melanoma en HIBA queda en 0.455 (Swin) y 0.435 (ConvNeXt), por debajo de lo que dan en HAM10000
  (0.623±0.071 y 0.553±0.042): la clase prioritaria es también la que peor generaliza.
  `--rerun-hiba` no servía (reentrena sin `--lesion-split` ni `--class-weights`): se agregó
  `--eval-hiba` al camino normal de `submit_sweep.py`.
- **Perturbaciones: error de preprocesamiento, anterior a este cambio.**
  `robustness_perturbations.py` evaluaba con `center_crop=False` (Resize cuadrado, legacy) modelos
  de receta `modern`, que entrena y evalúa con Resize(256)+CenterCrop(224). El baseline de Swin daba
  sensM 0.620 en lugar de 0.700. Corregido, y el script pasa a usar los checkpoints del split por
  lesión en vez de los `*_modern_v3`. Resultados nuevos (sens. macro, severidad 0→5):
  - Swin (base 0.700): ruido 0.572/0.409/0.221/0.156/0.143 · blur 0.629/0.429/0.286/0.235/0.201 ·
    JPEG 0.644/0.619/0.577/0.468/0.177 · resolución 0.668/0.614/0.519/0.400/0.249.
  - ConvNeXt (base 0.680): ruido 0.514/0.305/0.187/0.156/0.143 · blur 0.606/0.571/0.487/0.434/0.272 ·
    JPEG 0.635/0.591/0.532/0.396/0.157 · resolución 0.650/0.657/0.616/0.548/0.425.
  - **ConvNeXt aguanta bastante mejor la degradación espacial** (blur sev3 0.487 vs 0.286 de Swin;
    resolución sev5 0.425 vs 0.249), mientras que Swin resiste algo mejor el ruido en severidad
    baja. El 0.143 al que caen los dos es 1/7: colapso a una sola clase.
  - El ruido gaussiano es la perturbación más dañina y la pérdida de resolución la más benigna, en
    los dos modelos.
- **El anclaje de la cascada sigue en v3.** Los dos Swin coinciden en 80.6% del test: cambian 291
  diagnósticos (19.4%), y el anclaje nuevo es más exacto (0.795 → 0.847) y sobre-predice mucho menos
  melanoma (279 → 221 casos, contra 167 reales). `outputs/full_dx_swin_les.csv` generado con el
  script nuevo `scripts/make_dx_csv.py`. **Regenerar los reportes es una campaña de ~5000-6000
  reportes en Mendieta: pendiente de decidir el alcance.**
- Descartado: la sospecha de que el informe mezclaba números con y sin TTA. Todo el barrido es con
  TTA; ver el plan.

**Resul:** [split_lesion_resul](resul/split_lesion_resul_20260926.md).

### Re-anclaje de la cascada al split por lesión — Mendieta jobs 1177953-1177955
Enviados el 2026-09-17, alcance «titulares»: `full_swin_les` con los tres generadores (1503 cada
uno) y `full_differential_les` con Mini-VLM y LLaVA-Med. Scripts nuevos en `slurm/mendieta/v4/`,
registrados en `submit.py` como `reanchor_{mini,llava,skinvl}`. Quedan afuera los brazos de RAG y
`full_uncertainty` (400 cada uno), que son complementarios.

- **Anclaje nuevo:** `outputs/full_dx_swin_les.csv`, generado con `scripts/make_dx_csv.py` desde
  `swin_tiny_sweep_t06_les_cwnone`. Cambian 291/1503 diagnósticos (19.4%); exactitud del anclaje
  0.795 → 0.847; melanomas predichos 279 → 221 (reales: 167).
- **La calibración estaba mal, y era peor que el anclaje.** `temperature_scaling.py` tenía fijos el
  checkpoint `swin_tiny_modern_v3` **y** el split aleatorio, cuyo val se solapa con el train del
  split por lesión: ajustaba la temperatura sobre imágenes que el modelo ya había visto. Ambos
  parametrizados. Antes → ahora: T 0.527 → 0.850, τ 0.930 → 0.680, **ECE test crudo 0.394 → 0.040**,
  calibrado 0.344 → 0.027, casos inconfiados 1278 (85%) → **199 (13%)**. Los números viejos eran
  implausibles y nadie los había mirado de cerca.
- **El ruteo de 3 niveles cambia y los números bajan** (`build_uncertainty_3tier.py` con
  `full_dx_swin_les.csv` + `rag_context_les.csv`, que ya existía del 12/09):

  | Nivel | v3 | split por lesión |
  |---|---|---|
  | Afirmativo | 1111 (74%), acc 0.944 | 1204 (80%), acc 0.915 |
  | Diferencial | 334 (22%), cobertura 0.898 | 248 (17%), 0.847 |
  | Abstención | 58 (4%), 0.793 | 51 (3%), 0.647 |
  | Cobertura de lo presentado | 0.934 | **0.904** |

  El conjunto diferencial no solo se achica: son **otras** imágenes, así que el brazo se regenera
  con lista nueva (`uncertainty_differential_les.csv`), no se re-prompearon los mismos casos.
- Los brazos `full_baseline`, `full_oracle`, `full_dermlip`, `full_oracle_noimage` y
  `full_wrong_swap` no dependen del Swin y no se tocan.

**Resul:** [reanclaje_cascada_resul](resul/reanclaje_cascada_resul_20261003.md).

## 2026-09-15

### Semillas 43/44 + reenvíos: cierre del split por lesión — TOKO jobs 98041–98046
Cierra la entrada del 2026-09-13. Cola vacía, los 6 jobs terminaron el 2026-09-14. `sync_down.py` +
`scripts/lesion_split_report.py` (`outputs/results/lesion_split_report.json`).

- **Ganadores confirmados** (ambos `t06_les_cwnone`, media ± sd sobre semillas 42/43/44 en test):
  - Swin-Tiny: acc 0.846±0.002, F1w 0.846±0.004, F1m 0.733±0.026, sensM 0.692±0.025, **recall MEL 0.623±0.071**.
  - ConvNeXt-Tiny: acc 0.844±0.004, F1w 0.841±0.007, F1m 0.723±0.013, sensM 0.700±0.018, recall MEL 0.535±0.028.
- **La semilla 42 era optimista para melanoma.** El 0.701 de recall MEL que traía Swin con seed 42 queda en
  0.623±0.071 al promediar: es la métrica con más varianza entre semillas (sd 0.071 vs 0.002 de accuracy).
  El número que se reporta en el documento tiene que ser la media ± sd, no la semilla única.
- **Reenvíos (`class_weights=auto`), ya sin crash del DataLoader:** `swin_tiny_sweep_t04_les` val F1w 0.782
  (test sensM 0.772) y `convnext_tiny_sweep_t15_les` val F1w 0.814 (test sensM 0.738). Ninguno alcanza el
  0.850/0.848 de los ganadores en validación → **el barrido queda completo (74/74) y el ganador no cambia**.
- Sigue abierta la tensión de selección: por F1 ponderado en val gana siempre `cwnone`, pero las corridas con
  pesos por clase llegan a sensM ~0.78 en test. Decidir el criterio antes de escribir los números finales.

**Resul:** [split_lesion_resul](resul/split_lesion_resul_20260926.md).

## 2026-09-13

### Split por lesión: barrido terminado + tanda C (semillas) — TOKO jobs 98041–98044 + 2 reenvíos
Continúa la entrada del 2026-09-12. Cola vacía; `sync_down.py` + `scripts/lesion_split_report.py`
(`outputs/results/lesion_split_report.json`). Resul: [split_lesion_resul](resul/split_lesion_resul_20260926.md).

- **72/74 corridas OK.** Fallaron `swin_tiny_sweep_t04_les` (97983) y `convnext_tiny_sweep_t15_les` (97963),
  ambas con `class_weights=auto`: crash del DataLoader (`worker killed by signal: Segmentation fault/Aborted`),
  no un error de código. Reenviadas. No cambian el ganador: con `auto` el mejor val F1w es 0.808 (Swin) y
  0.819 (ConvNeXt), frente a 0.850 y 0.848 de los ganadores.
- **Ganadores en val (seed 42):** ambos `t06_les_cwnone` (sin pesos por clase). Swin: val F1w 0.850 → test acc
  0.847, F1w 0.850, F1m 0.755, sensM 0.716, recall MEL 0.701. ConvNeXt: val 0.848 → test acc 0.840, F1m 0.711,
  sensM 0.682, recall MEL 0.503. Con pesos por clase la sensM de test sube (hasta ~0.78) pero val F1w cae.
  Selección por F1 ponderado → gana siempre `cwnone`; queda para discutir en el doc (criterio de selección
  vs métrica prioritaria).
- **Legacy/desbalance (`_les`):** DenseNet 0.812/sensM 0.672, ViT 0.814/0.664; Swin CE 0.860/0.707, focal
  0.781/0.773, weighted 0.752/0.783.
- **Calibración (Swin ganador):** sin pesos por clase ya está bien calibrado (ECE 0.040 → TS 0.027 → VS 0.014;
  VS baja sensM 0.716 → 0.675). Confirma que la descalibración anterior venía de los pesos por clase.
- **Ruteo (Swin nuevo + kNN del split por lesión):** afirmativo 80.1% (cobertura 0.915), diferencial 16.5%
  (0.847), abstención 3.4%; cobertura no derivados 0.904.

**Envíos:**
```
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights none --trials t06 --seeds 43 44      # 98041-98042
python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split --class-weights none --trials t06 --seeds 43 44  # 98043-98044
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights auto --trials t04    # reenvío
python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split --class-weights auto --trials t15  # reenvío
```

## 2026-09-12

### Split disjunto por lesión + selección en val + semillas — TOKO jobs 97933–98007 (73 jobs)
Plan: [split_lesion_semillas_plan](ideas/split_lesion_semillas_plan_20260912.md) · Origen:
[feedback_20260912](feedback_20260912.md). Resul: [split_lesion_resul](resul/split_lesion_resul_20260926.md).

**Auditoría previa (local, `scripts/leakage_analysis.py` → `outputs/results/leakage_analysis.json`):**
- **LEAKAGE CONFIRMADO.** `prepare_data.py` estratifica POR IMAGEN. 543/1503 imágenes de test (36.1%)
  comparten `lesion_id` con train; MEL 106/167 (63%), BCC 54/77 (70%). Swin headline sobre el subconjunto
  limpio (n=894, lesión fuera de train y val): sens. macro 0.870 → 0.804, recall MEL 0.766 → 0.608 (acc sube
  0.868 → 0.890 solo por composición: el limpio es 83% NV). Control: DermLIP ZS (nunca vio HAM) rinde PEOR en
  las fugadas (sens 0.477 vs 0.527) → la ventaja de Swin en ellas (0.936) es leakage, no facilidad.
- **Robusto al leakage:** pipeline avanzado sobre el limpio sigue significativo (Mini +0.077 [0.058,0.095];
  LLaVA +0.096 [0.078,0.117]); cobertura del ruteo 0.941; colapso VLM igual.
- **Selección:** checkpoint por época = `val_f1` ✓. Legacy ViT/DenseNet elegidos por `best_val_f1` (W&B solo
  tiene val) ✓. Swin t08 = mejor también en val ✓. **ConvNeXt t06 fue elegido por TEST** (en val gana t09,
  0.874 vs 0.861). **Bug:** nadie recargaba `best_model.pt` → test evaluado con pesos de la ÚLTIMA época
  (Swin t08: mejor época 35, evaluado en 40).
- **Estadística:** `statistical_tests.py` usaba Swin modern_v3 + VLMs de first_iteration (ZS por generación),
  no los modelos de `tab:clasificacion`; el IC de Swin [0.77,0.85] ni contiene el headline 0.870.
- **DermLIP por split (`scripts/dermlip_split_eval.py`, control reproduce el doc):** kNN sens 0.666→0.568,
  SVM-RBF 0.788→0.673, linear-probe 0.747→0.729. La inflación escala con la capacidad de memorizar (métodos
  locales caen, el lineal casi no).

**Código:** `make_lesion_disjoint_split.py` (test IDÉNTICO; descarta 776 imágenes de lesiones de test;
StratifiedGroupKFold → train 6447 / val 1289; solapamiento 0 verificado). `train_classifier.py`
`--eval-best-checkpoint` + `--save-val-predictions` (+ image_ids en las predicciones). `submit_sweep.py`
`--lesion-split --class-weights {auto,none,both} --trials --seeds` (defaults = sweep v4 original, verificado
con --dry-run). `submit.py`: `les_legacy`, `les_imb_all`. `statistical_tests.py --models` (alinea por
image_ids, agrega F1 macro). `posthoc_calibration.py` (TS + vector scaling en val).

**Envíos (TOKO):**
```
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights auto --trials t08  # 97933 (humo)
python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split --class-weights both            # 97935-97964
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights none               # 97965-97979
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights auto --trials t01..t15 sin t08  # 97980-97993
python scripts/toko/submit.py les_legacy     # 97994-97995
python scripts/toko/submit.py les_imb_all    # 97996-98007
```
Humo 97933 OK (Swin t08 cw auto): corte por paciencia en época 18, evaluó con checkpoint de la época 13
(val_f1 0.753), test acc 0.753 / sens 0.780, 1289 preds de val guardadas. Validación muy oscilante (0.75 →
0.23 → 0.37 entre épocas) — el barrido elige en val. TOKO corre 1 job a la vez (~20–25 min c/u): se bajó la
prioridad (`nice=500`) de ConvNeXt/legacy/imb para que Swin corra primero. Pendiente tanda C (semillas 43/44
del ganador en val de cada modelo).

**Calibración post-hoc (prototipo sobre modern_v3 TTA, split original):** TS apenas mejora (ECE 0.394→0.344,
T=0.53); vector scaling la corrige (ECE→0.010, Brier 0.58→0.19) pero sube acc (0.80→0.87) y BAJA sens. macro
(0.798→0.732): los pesos por clase desplazan el sesgo por clase; deshacerlo devuelve predicciones a NV.

### Réplica del ensamble consciente de la incertidumbre con LLaVA-Med — Mendieta 1172480 (analizado)
Resul: [incertidumbre_llava_replica_resul](resul/incertidumbre_llava_replica_resul_20260912.md).
Job terminó 2026-09-11 16:39, 334/334 reportes, 0 errores. `ensemble_bootstrap.py` y
`uncertainty_analysis.py` parametrizados con `--model` (Mini reproduce exacto sus números).
**Veredicto: CUMPLE.** No derivados 0.706 → 0.831 (Δ +0.125 [0.109,0.143]); diferencial 0.353 → 0.895;
cohorte completa 0.696 → 0.799. dx incorrecto 13.5% → 7.0% (cohorte 14.2% → 6.7%). **Corrige una lectura
previa:** la repetición NO se amplifica con LLaVA-Med (0.1% → 0.3%) → la amplificación es propia de Mini-VLM,
no del formato diferencial. Aplicado al `.tex`: `tab:incertidumbre_e2e` y `tab:taxonomia_incert` con ambos
generadores, párrafos "Réplica con el segundo generador" y "Cómo leer el 0.94" (descomposición: afirmativo
0.951 ≈ acc del ancla 0.944; diferencial 0.901 tipo top-2; cohorte completa 0.904).

### Documento: reformulaciones del feedback (sin números nuevos de clasificación) — **Sin jobs SLURM**
- Afirmaciones absolutas sobre la imagen → acotadas. Evidencia nueva (local): sin imagen todos los reportes
  de una clase son IDÉNTICOS (Jaccard intra-clase 1.00); con imagen 99% distintos (0.36 Mini / 0.28 LLaVA);
  entity recall de Mini 0.79 → 0.38 sin imagen. "La imagen no cambia qué diagnóstico se redacta, sí qué se
  describe."
- Párrafo "¿Qué aporta entonces el VLM?" (clasificador = diagnóstico; VLM = riqueza, especificidad por caso,
  lenguaje; nada de eso validado clínicamente).
- Métricas: agregado F1 macro y justificación concreta de sens. macro (clasificador "todo nevo": acc 0.669,
  sens 0.143; Mini-VLM FT real: acc 0.660, sens 0.141). Párrafo "Fidelidad diagnóstica no es validez
  clínica" + 5 frases que atribuían utilidad clínica reformuladas.

## 2026-09-08

### Seccion final: solo limitaciones, sin trabajo futuro — **Sin jobs SLURM** (doc)
Segunda pasada sobre la misma seccion: el autor decidio **borrar todo el trabajo futuro** y dejar solo
limitaciones (ya habia borrado a mano los items de repeticion, un-solo-generador y validacion clinica).
Renombrada `Limitaciones y lineas abiertas` -> **`Limitaciones`**; sacada de la entradilla la frase sobre
"la via que tendria quien quisiera continuarlas". Los dos items que aun mezclaban limitacion con propuesta
se reescribieron para que **la limitacion sea la afirmacion**, no el preambulo de una sugerencia:
- **OOD**: antes cerraba con "cerrar esa brecha es la linea abierta de mayor impacto". Ahora dice que la
  caida sobre HIBA **acota el alcance de lo reportado**: como el clasificador es el que ancla la fidelidad,
  la mejora 0.82->0.94 no debe leerse como transferible a otra poblacion. Mas fuerte que la version previa,
  porque conecta la limitacion con el resultado principal.
- **"Via de grounding no explorada"** (era 100% propuesta: "potencialmente mas barata que fine-tunear")
  -> **"Anclajes no evaluados"**: el ensamble se probo con tres anclas (0.38 / 0.80 / 1.00), de modo que la
  relacion exactitud-del-ancla vs fidelidad se caracteriza sobre **tres puntos y no sobre un barrido**.
- **Reportes de especialistas**: sacado "ampliar la comparacion requeriria antes conseguir una fuente" ->
  "no existe publicamente un corpus dermatoscopico redactado por especialistas, de modo que la comparacion
  no puede extenderse mas alla de SkinCoT".

**Puntero roto detectado y arreglado:** "Validez de constructo" (Amenazas a la validez) decia "la validacion
clinica humana aun esta pendiente **(vease abajo)**", apuntando al item que el autor habia borrado ->
reescrito como "que no interviene en ninguna de las evaluaciones reportadas".

Barrido final sin coincidencias para: "trabajo futuro", "lineas abiertas", "en curso", "en ejecucion",
"se incorporaran", "queda pendiente", "paso siguiente/inmediato", "sin explorar", "quien quisiera/lo
intente", "continuar". Las dos menciones que quedan a un especialista (Secc. interpretabilidad) son
enunciados de limitacion, no compromisos. Compila limpio: **42 pags** (era 43), 0 errores, 0 undefined.

### Cierre del marco temporal: fuera "trabajo en proceso/futuro" — **Sin jobs SLURM** (doc)
El autor propuso sacar el "trabajo en proceso y futuro" y dejar las cosas como lineas para "si alguien
quisiera" continuar. **De acuerdo, y con una razon adicional: parte del texto ya era falso.** El abstract
decia "las corridas a mayor escala **estan en curso**" cuando la comparacion central ya se evaluo sobre el
test completo (1503); y la conclusion cerraba con "conclusiones parciales y sujetas a la experimentacion en
curso". Ambos arreglados: ahora acotan el **alcance** (dermatoscopia de HAM10000, metricas automaticas) en
vez de prometer trabajo.

**Seccion renombrada** `Limitaciones y trabajo en proceso o futuro` -> **`Limitaciones y lineas abiertas`**,
con parrafo introductorio que declara la experimentacion cerrada y encuadra lo que sigue como "puntos de
entrada para el siguiente, no compromisos pendientes de este trabajo". Reescritos los 9 items para sacar
todo compromiso en primera persona:
- **Repeticion**: "lo que constituye trabajo futuro" -> "quien lo intente debe saber que...".
- **Reportes de especialistas**: "queda pendiente de una fuente apropiada" -> "requeriria antes conseguir
  una fuente, que no existe publicamente para esa modalidad".
- **Un solo generador** (era el unico "en proceso" real, job Mendieta 1172480): eliminado
  "esa corrida esta en ejecucion... sus resultados se incorporaran cuando finalice" -> ahora dice cuan
  barato seria cerrarlo (solo 334 reportes) y lo rotula "la linea abierta mas barata de todas".
- **OOD**: "queda como trabajo futuro" -> "la de mayor impacto para uso clinico real", con el porque
  (cualquier mejora en reportes es secundaria si el clasificador que ancla no transfiere).
- **Validacion clinica**: sacado "idealmente antes de la defensa" -> dependencia externa que excede lo que
  la experimentacion podia resolver; por eso se deja el instrumento listo.
- **Extensiones planificadas** -> **Generadores no evaluados**; sacado el resabio de documento de
  planificacion ("inicialmente planificada, ya se concreto") y agregado el argumento de que el resultado de
  SkinVL vuelve menos probable que cambiar de generador altere la conclusion central.

Nota: si el job 1172480 termina antes de la defensa, el resultado se agrega como resultado; el texto ya no
depende de el. Verificado: **cero** ocurrencias de "en curso", "en ejecucion", "se incorporaran",
"trabajo futuro", "en proceso" y "planificad" en todo el documento. Compila limpio: 43 pags, 0 errores,
0 undefined.

### Consistencia de negritas en los cuadros — **Sin jobs SLURM** (doc)
El autor reporto 4 inconsistencias en el resaltado. **Las 4 verificadas y correctas**, mas **5 errores
adicionales del mismo tipo** encontrados al barrer los 23 cuadros. Convencion unificada: **negrita = mejor
valor dentro del bloque comparable**, sin aclararlo en el caption (el autor pidio explicitamente NO
documentarlo: se sobreentiende).

**Reportados por el autor:**
1. `tab:generacion_v1v2` (C10): sin ninguna negrita -> resaltado el mejor entre v1/v2 por modelo y metrica.
2. `tab:skinvl` (C12): resaltaba el **oracle** como mejor, lo cual es trivial y no informa. -> Oracle
   separado con `\midrule`, en cursiva y rotulado "cota superior"; negrita al mejor **realizable** (Swin).
3. `tab:melanoma` (C8): la primera fila no se entendia — era un encabezado de bloque `\multicolumn` que
   ademas traia embutidas las tasas de FN de los 3 modelos. Ademas **las FN eran redundantes**: son
   exactamente el complemento de Sens.(esp>=85). -> Encabezados limpios ("Tarea A/B — ..."), FN fuera de la
   tabla (queda en la prosa, que ya las citaba), y corregida la negrita de Espec. (estaba en 0.860 cuando
   el maximo es 0.862).
4. `tab:taxonomia_incert` (C17), `tab:ruteo_clase` (C18), `tab:ensamble_skincot` (C20), `tab:sota_gen` (C21):
   - C17: decia "mejor por fila" pero faltaban `ok` y `hedging`, y la direccion de "mejor" cambia por fila.
     -> Agregada fila **Correcto (total)** (unica comparable: el pipeline reparte aciertos entre `ok` y
     `ok diferencial`) con 555 (38.4%) vs **738 (51.1%)**, flechas de direccion y negritas completas.
   - C18: negritas incompletas y sin criterio (los porcentajes suman 100% por fila, no hay "mejor").
     -> Maximo por columna: VASC afirmativo, MEL diferencial, DF abstencion.
   - C20: solo la consistencia resaltada. -> Maximo por columna; el resaltado queda **repartido**, que es
     justamente el hallazgo (metricas lexicas y fidelidad apuntan en direcciones opuestas).
   - C21: sin negritas. -> Resaltado **solo dentro de cada bloque internamente comparable** (los 3 modelos
     de Zeng et al. entre si; los 2 propios entre si); entre bloques no, porque los protocolos difieren.

**Encontrados de mas (mismo defecto):** `tab:ensamble` (C11) y `tab:rag` (C15) resaltaban el oracle igual
que C12 -> mismo tratamiento (en C15 la negrita paso a Grounding Swin+RAG 0.84, el mejor candidato real, que
la propia nota al pie ya senalaba sin resaltarlo); `tab:plantilla` (C14) decia "mejor por fila" cuando el
resaltado es por columna dentro de cada bloque, y tenia doble negrita (0.828 y 0.830); `tab:ablaciones` (C13)
resaltaba el `Delta` (que no es un "mejor") -> negrita al maximo por columna.

**Analisis agregado:** un parrafo en la prosa del pipeline avanzado con el dato que la nueva fila hace
visible — la fraccion de reportes **diagnosticamente correctos** sube de 38.4% a **51.1%**, o sea que el
sistema no solo evita afirmaciones falsas sino que ademas acierta mas seguido.

Verificado con un scan automatico de los 23 cuadros (script en scratchpad): los 7 casos que marca son
falsos positivos por bloques internos (por arquitectura en C4, por tarea en C8, por grounding en C14,
por bloque en C19/C21, significacion en C7, direcciones mixtas en C17). Compila limpio: **43 pags,
0 errores, 0 undefined, 0 citas rotas**, sin overfull nuevos (max 21.4pt, igual que antes).

### CORRECCION FACTUAL: SkinCoT no son reportes de dermatologo — **Sin jobs SLURM** (doc)
El autor detecto que la Figura 18 describia la referencia de SkinCoT como "reporte de un dermatologo".
**Verificado contra el paper** (`Papers/derma/SkinCaRe...pdf`, §2.3): es INCORRECTO. SkinCoT se construye
con un pipeline de 3 LLMs —Gemini 2.5 Pro (descripcion observacional), GPT-o4-mini (borrador de
razonamiento **usando la etiqueta verdadera**), DeepSeek-R1 (normalizacion)— y recien despues dermatologos
**certifican y filtran** sobre 6 criterios (se descarta lo que puntua <4.5). SkinCAP si es
dermatologist-authored, pero la figura usa un caso de SkinCoT. Corregidos **6 lugares**: etiqueta y caption
de `fig:human_vs_gen`, parrafo que la introduce, limitacion de referencias humanas (renombrada "Ausencia de
reportes redactados por especialistas"), descripcion del Nivel 1 (ya no dice "escrito por un humano") y
fila de SkinCaRe en `tab:datasets` (distingue SkinCAP redactado vs SkinCoT generado+certificado).

### Ultima pasada: resultados desconectados que se explican entre si — **Sin jobs SLURM** (doc)
Conexion agregada en `sec:ablaciones`: la ablacion imagen-vs-dx y el test del prior del lenguaje
(`sec:rediag`) usan **el mismo recurso experimental** (imagen neutra) y revelan la misma propiedad con
signos opuestos —en clasificacion quitar la imagen no impide predecir (colapso 100% a una clase); en
generacion no degrada la fidelidad—. Ambos: **los VLMs se anclan en el texto, no en la senal visual**. Esa
unica propiedad explica a la vez el fracaso (inhabilita como clasificadores) y el exito (los vuelve
transcriptores fieles dentro de la cascada), con la propagacion de error como contracara.
Compila limpio: **43 pags, 0 undefined, 0 citas rotas**.


### Auditoria de analisis EXPLICATIVO (no descriptivo) — **Sin jobs SLURM** (doc)
Segunda pasada de auditoria, esta vez preguntando por cada resultado: ¿se explica el comportamiento y por
que ocurre, o solo se describe? Bien explicados ya: colapso de VLMs (4 evidencias + test sin imagen),
DermLIP (objetivo contrastivo + Derm1M + ontologia), calibracion (regularizacion del recipe moderno),
propagacion de error, SkinVL (mode collapse), trade-off BLEU/consistency, hedging, repeticion en diferencial.
**Cuatro huecos encontrados y cerrados:**
1. **Por que el acuerdo funciona y la softmax no** (decision de diseno central del ruteo, estaba sin
   justificar): softmax mal calibrada (ECE 0.19-0.39, sub-confiada, no monotona al rutear) vs acuerdo entre
   dos modelos con sesgos inductivos y datos distintos (errores independientes) que ademas usa solo
   DECISIONES, no probabilidades -> inmune a la mala calibracion.
2. **Por que melanoma cae en diferencial** (dato calculado nuevo): de los 67 melanomas diferenciales, 32
   (48%) son {melanoma, nevo} y 13 (19%) {melanoma, queratosis benigna} -> dos tercios reproducen los
   diferenciales clinicos canonicos; el desacuerdo aparece donde las clases se solapan de verdad.
3. **Por que el re-balanceo empeora** (0.923->0.795): la augmentacion ya habia compensado el sesgo, asi que
   la correccion no elimina un sesgo sino que introduce el opuesto (sobre-prediccion de clases raras ->
   falsos positivos masivos sobre nevo, 67% del conjunto). Las class-weights, las mas agresivas, son las
   que mas danan.
4. **Por que el oracle de LLaVA se queda en 0.852 y Mini llega a 0.999**: conexion que ya estaba en el doc
   sin unir — el ajuste de prompt sobre LLaVA+oracle habia dado 0.85, el mismo numero; 0.852 no es limite
   del grounding sino el techo de la ingenieria de prompt en un modelo con prior de deliberacion.
Compila limpio: **42 pags, 0 undefined**.


### Auditoria resultados-vs-escritura: hueco encontrado (ensamble de clasificadores) — **Sin jobs SLURM** (doc)
Auditoria sistematica de (1) resultados calculados vs escritos, (2) completitud, (3) analisis por tabla.
Verificado OK: 23 tablas y 22 figuras, **ninguna huerfana** (todas referenciadas); todos los `resul` docs
tienen su contenido reflejado en el `.tex`; los JSON de `outputs/results/` estan cubiertos.
**Hueco real:** el **ensamble de clasificadores por voto suave (Swin+ConvNeXt)** se usaba en `tab:melanoma`
y `tab:sota_melanoma` (filas "Ensamble (voto)") **sin haberse definido ni caracterizado antes**, y su
resultado multiclase (P5.1, `mejoras_p5_local_resul_20260713.md`) nunca se habia escrito. Agregado parrafo
en `sec:melanoma` que lo define (voto suave de probabilidades con TTA) y situa su aporte: sens. macro 0.846
vs 0.827 del mejor individual (+0.019), +0.004 F1-w, a costa de 2x inferencia -> apilar modelos es mas caro
que TTA sobre un unico modelo in-distribution, pero en melanoma binario si da el mejor AUC. Nota al pie
aclara que usa checkpoints modern_v3 locales (por eso no coincide con los headline del barrido).
Compila limpio: **42 pags, 0 undefined**.


### Cierre de pendientes de Limitaciones — Mendieta job 1172480 + post-proceso local
Auditoria de los 9 items de `sec:limitaciones`: la mayoria NO son tareas pendientes sino limitaciones
descriptivas ya justificadas. Dos si eran accionables:

**(A) Replica del ruteo con el 2do generador (LLaVA-Med) — Mendieta job 1172480, PENDING.**
Correccion importante: la limitacion decia que exigia "una corrida de generacion completa", lo cual era
**inexacto** — LLaVA-Med ya tiene `full_swin` sobre las 1503 (nivel afirmativo) y la abstencion no genera,
asi que solo faltan los **334 reportes diferenciales**. Script nuevo
`slurm/mendieta/v3/uncertainty_generation_llava.sh` (alias `unc_gen_llava` en `scripts/mendieta/submit.py`),
mismos hiperparametros que la corrida de Mini-VLM y que `full_swin` de LLaVA (checkpoint
`stage2_llava_med_v2`, max_tokens 384, seed 42) para comparacion pareada. **Va a Mendieta, no a TOKO**:
TOKO solo tiene `stage1_llava_med` y su `outputs/uncertainty/` esta vacio (sync_up excluye `outputs/`);
Mendieta tiene el checkpoint v2, el CSV del diferencial y todos los `full_*`. Texto de la limitacion
corregido en el `.tex`.

**(B) ¿Es la repeticion mitigable sin regenerar? — NO.** `scripts/repetition_postprocess.py` (local):
deduplicacion de oraciones + truncado del bucle final sobre los 334 reportes diferenciales. Recupera solo
**11 de 59** afectados (17.7% -> 14.4%), pierde 2 menciones del gt y degrada 6 reportes a `otros`; la
longitud media apenas baja (212 -> 208 palabras). Conclusion: la repeticion es **degeneracion pervasiva**,
no un bucle final recortable -> requiere intervenir el **decodificado** (repetition_penalty), inviable en
Mini-VLM (tokens de imagen fuera de vocabulario) y practicable en LLaVA-Med. Documentado como addendum en
[analisis_pipeline_avanzado_resul](resul/analisis_pipeline_avanzado_resul_20260908.md) y aplicado a la
limitacion de artefactos en el `.tex`.

Compila limpio: **41 pags, 0 undefined, 0 citas rotas, overfull max 21.4pt**.


### Caracterizacion del pipeline avanzado (taxonomia + ruteo por clase) — **Sin jobs SLURM** (local)
Plan: [analisis_pipeline_avanzado_plan](ideas/analisis_pipeline_avanzado_plan_20260908.md) ·
Resul: [analisis_pipeline_avanzado_resul](resul/analisis_pipeline_avanzado_resul_20260908.md).
Script nuevo `scripts/uncertainty_analysis.py` sobre datos ya en disco (`uncertainty_3tier.csv`,
`full_swin` 1503, `full_differential` 334). **Ajuste metodologico:** `classify_error` marca "contradiccion"
si el texto menciona >=2 clases, pero el reporte diferencial menciona 2 candidatos POR DISENO; para ese
nivel se reclasifica (`ok_diferencial` si el gt esta entre los candidatos).
**Veredicto: CUMPLE.** (A) `dx_incorrecto` cae 19.0% -> 6.6% sobre las 1445 no derivadas; las 58 abstenidas
habrian producido 26 dx incorrectos que se evitan al derivar; sobre la cohorte completa 20.0% -> 6.3%
(reduccion del 68%, 3.2x). Contrapartida honesta: `repeticion` empeora 0.3% -> 4.3%. (B) El ruteo resulta
**consciente del riesgo sin haber sido disenado asi**: afirma 81.3% en nevo y 90.9% en vascular, pero solo
52.7% en melanoma (40.1% diferencial, 7.2% abstencion) -> no afirma melanoma a ciegas; dermatofibroma (n=17)
es la de mayor abstencion (35.3%).
Aplicado al `.tex`: nuevos `tab:taxonomia_incert` y `tab:ruteo_clase` + dos parrafos en `sec:incertidumbre`.
Compila limpio: **41 pags, 0 undefined, 0 citas rotas, overfull max 21.4pt**.


### Cierre: Wilcoxon reportado + limitacion del pipeline avanzado — **Sin jobs SLURM** (doc)
Dos huecos detectados al auditar el feedback de las 3 rondas contra el `.tex`:
**(1)** El test de **Wilcoxon** (pedido explicitamente en la ronda 1: "bootstrap, McNemar, Wilcoxon") estaba
calculado en `scripts/statistical_tests.py` y guardado en `outputs/results/statistical_tests.json`, pero
**nunca se reportaba en el documento**. Agregado: nuevo `tab:wilcoxon` (Cuadro 7) + parrafo en la seccion de
significancia — recall por clase pareado (7 pares): Swin supera a los 3 VLM (p<=0.031); Mini-VLM y LLaVA-Med
son indistinguibles (p=1.00, dif. mediana 0.00); DermLIP vs Mini-VLM no alcanza significancia (p=0.109).
**(3)** Nueva limitacion declarada: el ensamble consciente de la incertidumbre se valido **end-to-end solo
con Mini-VLM**; el componente de decision es independiente del generador (cobertura 0.934 se traslada), pero
falta verificar la redaccion diferencial con LLaVA-Med.
(El item 2 —dataset unificado— se dejo fuera por decision del autor.)
Incidencia: la insercion inicial se corrompio (heredoc colapso `\`→`\`, ``→backspace); se reparo y
re-inserto. Tambien se quito un `\mbox` en la fila de SkinCaRe que causaba overfull de 38pt.
Compila limpio: **40 pags, 0 undefined, 0 citas rotas, overfull max 21.4pt** (preexistente).

## 2026-08-23

### #2 Test del prior del lenguaje (P(clase|prompt) sin imagen) — TOKO — jobs 97463, 97464
Plan: [prior_lenguaje_noimage_plan](ideas/prior_lenguaje_noimage_plan_20260823.md).
Nuevo flag `--no_image` en `scripts/train_vlm_classify.py` (reemplaza cada imagen por una gris neutra
224×224, aislando el prior del lenguaje; sufijo de salida `_noimage`). SLURM `vlm_classify_{mini,llava}.sh`
extendidos con `EXTRA_ARGS`; aliases nuevos `classify_{mini,llava}_noimg` en `scripts/toko/submit.py`
(METHOD=likelihood + EXTRA_ARGS=--no_image). Comando: `python scripts/toko/submit.py classify_mini_noimg`
y `classify_llava_noimg`. **Jobs 97463 (Mini-VLM) y 97464 (LLaVA-Med), RUNNING en TOKO (gpu1/gpu2, sin cola).**
**COMPLETADO** (jobs 97463/97464 terminaron OK: 6h22m / 5h05m). Resul:
[prior_lenguaje_noimage_resul](resul/prior_lenguaje_noimage_resul_20260824.md). **Veredicto: CUMPLE** —
sin imagen ambos VLMs colapsan al 100% a una clase fija (Mini→MEL acc 0.111, LLaVA→DF acc 0.011), nunca se
abstienen; con imagen apenas se dispersan (Mini 1→2 clases/acc 0.189, LLaVA 1→5 clases/acc 0.037) → el prior
del lenguaje domina sobre el contenido visual. `sec:rediag` actualizado: la conjetura pasó a **resultado
directo** (se quitó "queda como trabajo futuro"). Doc compila limpio (40 págs, 0 undefined).
#3 (penalización repetición) y #4-generación (SVM grounding) NO se lanzan: son corridas de generación de
horas y valor bajo-medio; quedan declarados como trabajo futuro.


### Revisión externa 2.ª pasada — aplicación de mejoras al `.tex` — **Sin jobs SLURM** (doc)
Fuente: `review_experimentacion_20260823.md` (revisión de otro agente). Verificadas contra el `.tex` (todas
se sostuvieron) y aplicadas: **consistencia numérica** (1.1 nota baseline RAG 0.20/n=400; 1.2 fuente del
recall 0.77; 1.3 nota Swin Acc 0.80=checkpoint ancla vs headline 0.868 en `tab:ensamble`/`tab:skinvl`;
1.5 abstract "diagnostic consistency"; 1.6 rango FN melanoma 0.07–0.14; 1.7 n/condición de mediciones
puntuales; 1.8 rangos de costo texto↔tabla); **tablas** (2.1 columnas `tab:sota_melanoma`; 2.3 espaciado
`tab:costo_total`; 2.5 cuadro/tabla en texto corrido; 2.6 fila "Total no derivado 0.934" + definición de
cobertura); **figuras** (3.1 **nuevo diagrama TikZ `fig:incertidumbre`** de 3 niveles; 3.3 nota reportes en
inglés); **claridad** (4.2 suavizar conjetura "prior del lenguaje" + test futuro; 4.3 calib "~40%" no "30%";
4.4 conectar trade-off SkinCoT con `tab:sota_gen`; 4.6 **nueva subsección "Amenazas a la validez"**);
**bibliografía** (5.1 citar HAM10000; 5.5 limpiar entrada Kreouzi); **estilo** (6.x coloquialismos).
Compila limpio: **39 págs, 0 undefined, 0 citas rotas**, overfull máx 21.4pt (preexistente).
Pendiente para el autor (no fabricado): referencias reales de SkinCaRe/HIBA (5.2/5.3, dejadas como footnote
"recurso público") y autores completos de `liu2025skinr1`/`SkinHealthMate2024`/`SkinSavvy22025` (5.6).

### Cierre de referencias + arreglo del diagrama de incertidumbre — **Sin jobs SLURM** (doc)
Referencias faltantes completadas desde `Docs/estado_del_arte/{resumen_papers.tex,referencias.bib}` y
`Papers/derma/`: **SkinCaRe** (`shen2025skincare`, Shen et al. 2025, arXiv:2405.18004) y **HIBA**
(`riccilara2023hiba`, Ricci Lara et al. 2023, Sci Data) agregadas y citadas (se quitaron las footnotes
"recurso público"); autores completados en `liu2025skinr1`, `SkinHealthMate2024`, `SkinSavvy22025`.
`fig:incertidumbre` reescrita (cajas en columna con separación real, etiquetas `sloped` en las flechas) —
se corrigió el solapamiento visual. Compila limpio: **40 págs, 0 undefined, 0 citas rotas**.

### Cierre de experimentación — F4 (ejemplo humano vs generado) + análisis de trabajo futuro — **Sin jobs SLURM** (doc)
**#1 (F4):** nueva `fig:human_vs_gen` (Figura 18) — reporte de dermatólogo (referencia SkinCoT,
`03DermatitisArm1`, eczema) vs reporte generado por el ensamble sobre el mismo caso, usando datos ya
existentes (`outputs/generated_reports/llava_med/skincot_oracle/`). Imagen copiada a
`imagenes/ej_skincot_human.jpg`. Se actualizó la limitación correspondiente (ya no falta la comparación).
**#2 verificado NO reutilizable:** `full_oracle_noimage` tiene el gt inyectado (oracle), no sirve para el
test P(clase|prompt sin imagen); ese test requiere una corrida VLM nueva sin imagen (ver análisis de cierre).
Compila: **40 págs, 0 undefined, 0 citas rotas**.

### Cierre agosto — Plan + B1/D1 Detección de melanoma — **Sin jobs SLURM** (local)
Plan de cierre de experimentación: [cierre_experimentacion_plan](ideas/cierre_experimentacion_plan_20260805.md)
(8 decisiones de grilling: robustez-first + SOTA acotado a melanoma/reportes vs hardware; sistema propuesto =
pipeline avanzado con incertidumbre 3-niveles + RAG + abstención; rúbrica clínica no-bloqueante; 1503 por
sync+re-eval; generación en TOKO; gap detección→clasificación justificado).
**B1+D1 (melanoma):** `scripts/melanoma_detection.py` sobre probs TTA. **Melanoma-vs-resto AUC 0.93–0.95**
(competitivo a bajo costo); el argmax pierde 27% de melanomas (FN 0.27) pero **optimizar el umbral baja la
FN a 0.07** (esp≥85). Maligno-vs-benigno AUC 0.94–0.96. Macro-AUC-OvR 0.94–0.95. Resul:
[melanoma_detection_resul_20260805.md](resul/melanoma_detection_resul_20260805.md). **Caveat:** umbral fijado
sobre test (ilustrativo) → pendiente fijarlo en validación. **Veredicto: CUMPLE (con caveat).**

### Cierre agosto — B2 (stats+val) + C (1503) — **Sin jobs SLURM** (local)
**B2a:** `reeval_tta_probs.py` extendido a val+test → umbral de melanoma fijado en **validación** y aplicado
a test (caveat CERRADO): ConvNeXt melanoma AUC 0.949 sens 0.91/FN 0.09; ensamble sens 0.93/FN 0.07.
**B2b:** `statistical_tests.py` + **bootstrap pareado** de Δ F1-macro/sens-macro (McNemar no aplica a esas
métricas — lo pidió el tutor) y Δ consistencia entre condiciones de generación; todas las Δ de Swin
significativas. **C:** bajadas las 1503 de Mini/LLaVA (tar+scp por el login de Mendieta; scheduler sigue
caído) y re-evaluado el ensamble → **1503 confirma el 400** (Mini Swin 0.812 vs 0.830; oracle 0.999).
`tab:ensamble` + texto + limitación a 1503 (32 págs, compila). Elimina la asimetría 400/1503.

### Cierre agosto — Workstream A (pulido) + integración melanoma al .tex — **Sin jobs SLURM**
Aplicados los ítems de forma/claridad del feedback 2026-08-05: **Cuadro 3** (`tab:sota_clasif`) sin columna
Fuente (cita a paréntesis) + mejores en negrita; **Cuadro 9** (`tab:skinvl`) actualizado a 1503 + negritas
(la frase "mover 1.ª con 2.ª col" quedó ambigua para esta tabla → confirmar con tutor); **Grad-CAM**
reencuadrado como análisis cualitativo complementario (no prueba de validez clínica); **HAM↔HIBA** aclarado
(mapeo 6/7 1:1, SCC→AKIEC 158 imgs, mismo espacio 7-clases, caída = población y/o anotación); **protocolo de
perturbaciones** explicado (cada filtro por separado, determinístico, 4×5=20 versiones del test); **gap
detección→clasificación** justificado. **Nueva subsección `sec:melanoma`** (`tab:melanoma`) con la suite
clínica: melanoma-vs-resto AUC 0.93–0.95, argmax FN 0.27 → optimizado (umbral en val) FN 0.07; maligno-vs-
benigno; macro-AUC-OvR 0.94–0.95. Doc: **33 págs, compila, 0 undefined.** Pendiente: tabla SOTA + best-mark
exhaustivo en tablas restantes.

### Cierre agosto — D2 (incertidumbre 3 niveles) + E (rúbrica) — **Sin jobs SLURM** (local)
**D2 routing:** `build_uncertainty_3tier.py` — ensamble consciente de la incertidumbre con el marco del
tutor (afirmativo/diferencial/**abstención**) alimentado por el **acuerdo Swin↔kNN-DermLIP** (no softmax).
Test 1503: afirmativo 74% (acc 0.944), diferencial 22% (gt∈candidatos 0.898), abstención 4% (deriva).
**El sistema presenta el gt en el 93.4% de los no-derivados** vs ~80% del grounding forzado. Resul:
[incertidumbre_3niveles_resul_20260805.md](resul/incertidumbre_3niveles_resul_20260805.md). Integrado al
`.tex` (§`sec:incertidumbre`, `tab:incertidumbre`, 34 págs). **Generación de los 334 diferenciales:** intento local **falló** (el torch de la `.venv` es `2.10.0+cpu`,
sin CUDA — la GPU RTX 4070 está pero el build no la usa; un VLM 4.2B en CPU es inviable). **El scheduler de
Mendieta se recuperó** → se generan ahí (todo cacheado). Infra: `generate_report.py --only_ids_csv` +
`uncertainty_differential.csv` (334), SLURM `uncertainty_generation.sh` actualizado a solo-diferenciales.
Cancelado el job viejo 1161538 (usaba el CSV binario previo). **Job 1163000 (COMPLETED, 3h45m).** 334 diferenciales bajados y evaluados. **En el subconjunto
diferencial:** el reporte diferencial menciona el gt **0.901 vs 0.392** del grounding forzado (entity recall
0.87 vs 0.69). **Sistema completo (1445 no-abstenidos):** consistency **0.940 (avanzado) vs 0.822
(grounding simple)** —el $0.940$ coincide con la cobertura del router $0.934$—. Integrado a
`experimentacion.tex` (`tab:incertidumbre_e2e`, §incertidumbre, 34 págs). **D2 CERRADO. Veredicto: CUMPLE
completo.** Cierra el pipeline avanzado end-to-end. **E:** rúbrica clínica (`docs/rubrica_validacion_clinica.md`, 5
criterios del tutor + proxies) + muestra estratificada n=28 (`sample_reports_for_review.py` →
`outputs/review/muestra_revision_clinica.csv`). No bloquea; lista para especialista.
**Tabla SOTA:** nueva `tab:sota_melanoma` en `tablas_comparativas_sota_v32.tex` — detección de melanoma
binaria: ensamble **AUC 0.954 ≈ SOTA (Kreouzi2024, 0.951)** con modelos Tiny/GPU consumo; FN 0.07, VPN 0.99.
Compila (wrapper 6 págs).

## 2026-08-17

### S6 consolidación — E1 (bootstrap pareado ensamble/incertidumbre) + E2 (regenerar fig:robustez_ej) — **Sin jobs SLURM** (local)
Handoff: [handoff_s6_consolidacion.md](review_sessions/handoff_s6_consolidacion.md) (aplica los 5 reportes de
revisión `docs/review_sessions/reporte_s{1..5}_*.md`).
**E1:** `scripts/ensemble_bootstrap.py` (nuevo, reusa `paired_bootstrap_diff_flags` de `statistical_tests.py`
y `diagnostic_consistency_flags` de `clinical_ner.py`) sobre los reportes ya generados en
`outputs/generated_reports/mini_vlm/full_{baseline,dermlip,swin,oracle,differential}` + gt_label de
`data/raw/HAM10000`. Los puntuales reproducen exactamente los números ya citados en `tab:ensamble`
(0.246/0.497/0.812/0.999) y `tab:incertidumbre_e2e` (0.822/0.940, subset diferencial 0.392/0.901) — valida el
script. ICs pareados (n\_boot=2000): Swin vs Oracle Δ=-0.187 [-0.207,-0.168]; pipeline avanzado vs grounding
simple Δ=+0.118 [+0.101,+0.134] (n=1445); diferencial vs forzado Δ=+0.509 [+0.452,+0.566] (n=334). Todas
significativas (IC no cruza 0). Resultado: `outputs/results/ensemble_bootstrap.json`.
**E2:** `scripts/robustness_examples.py` extendido a multi-ejemplo (antes 1 imagen fija). La imagen previa
mostraba blur/resolución fallando antes que ruido/JPEG, **contradiciendo la curva agregada real**
(`fig:robustez`: ruido es la perturbación más dañina, resolución la más tolerada — confirmado inspeccionando
el PNG). El nuevo selector busca automáticamente ejemplos cuyo patrón de primera-falla coincide con esa
tendencia agregada (ya no con la caracterización del handoff, que tenía la dirección invertida). 2 ejemplos
(BKL, DF) regenerados, ambos coherentes con el texto y `fig:robustez`. Nota: el handoff S6 describía la
tendencia agregada al revés ("falla primero en desenfoque/resolución") — se verificó contra `P24_robustness.png`
y se siguió el dato real, no la descripción del handoff.

#### Pasada de verificación final (post-S6) — cierre de E1/E2 en el `.tex`
La verificación independiente detectó dos brechas que S6 dejó abiertas pese a reportarlas como hechas:
**(P1)** los ICs bootstrap de E1 se habían computado (`ensemble_bootstrap.json`) pero **nunca se insertaron
en el `.tex`** — `tab:ensamble` y `tab:incertidumbre_e2e` no tenían significancia. Corregido: se agregó la
prosa de significancia pareada a ambas (Δ y IC95 del JSON; baseline→Swin Δ=+0.567 [0.536,0.596],
Swin→oracle Δ=0.187, pipeline vs grounding Δ=+0.118, diferencial vs forzado Δ=+0.509).
**(P2)** la figura regenerada por S6 seguía teniendo un ejemplo (DF) que **contradecía su caption** (ruido/JPEG
verdes en los 5 niveles; solo fallaba desenfoque). El selector usaba `score<0`, que se satisface solo con el
ruido. Se endureció `_exhibits_trend` a `max(fast) < min(slow)` (ruido *y* JPEG deben fallar antes que
desenfoque *y* resolución) + early-stop por pool. Regenerada: 2 ejemplos BKL (ISIC\_0034291, ISIC\_0034175),
ambos verificados visualmente coherentes con el caption. Docstrings del script corregidos (estaban invertidos).
Compila limpio: 38 págs, 0 undefined, overfull máx 21.4pt (preexistente).

## 2026-07-25

### P5.4 — Generación consciente de la incertidumbre — Mendieta
**Job Mendieta 1161538 (enviado).** Plan:
[incertidumbre_p54_plan](ideas/incertidumbre_p54_plan_20260725.md). SLURM
`slurm/mendieta/v3/uncertainty_generation.sh` (alias `unc_gen`), Mini-VLM n=400, modo `--uncertainty`.
**⚠️ NO CORRIÓ:** al 2026-07-30 sigue PENDING sin arrancar (0 reportes, sin logs) — el planificador de
Mendieta (`slurmctld`) está **caído** ("Unable to contact slurm controller"). El job quedó fantasma
(sacct lo ve PENDING pero squeue/scontrol/scancel fallan). Infra lista y esperando (CSV subido, código
sincronizado); reenviar cuando CCAD restablezca el scheduler.
**Trabajo local previo:** (1) `temperature_scaling.py` (Swin, T=0.53, ECE 0.39→0.34) — la **confianza
softmax NO sirve para rutear** (no monótona vs exactitud; sub-confianza en la clase mayoritaria).
(2) Pivote a **acuerdo Swin↔kNN-DermLIP** (`build_uncertainty_agreement.py`): acuerdo 74% acc 0.944;
desacuerdo 26% con gt∈{Swin,kNN} 88% (vs Swin solo 0.37). CSV subido por scp. generate_report.py: nuevo
modo `--uncertainty` + `DIFFERENTIAL_TEMPLATE`. **Pendiente análisis de generación.**

## 2026-07-21

### Desbalance extendido a ConvNeXt + DenseNet (mejora #2, 2.ª tanda) — Mendieta
**Jobs Mendieta 1161112–1161119.** Plan:
[desbalance_multimodelo_plan](ideas/desbalance_multimodelo_plan_20260721.md). Replica el desbalance de Swin
(P2.2) en **ConvNeXt-Tiny y DenseNet121** × 4 pérdidas, mismo recipe modern. (Se planeó TOKO pero estaba
caído → Mendieta.)
- **ConvNeXt (1161112–1161115): COMPLETED.** CE-plano mejor global (acc 0.912 / f1-w 0.910; sens macro
  0.824); class-weights degrada fuerte (acc 0.691); Focal sube sens macro a 0.842 pero −11 pts de acc. El
  patrón de Swin se repite (2 arquitecturas: transformer + CNN).
- **DenseNet (1161116–1161119): FALLARON** — nodos de Mendieta offline, torchvision no pudo bajar los
  pesos ImageNet (`Network is unreachable`). Re-envío 1161532–1161535 en Mendieta **cancelado**; TOKO
  volvió (cola casi nula, pesos DenseNet ya cacheados de `cls_densenet_modern`) → re-enviados a TOKO.
  **TOKO 97086–97089: COMPLETED.** DenseNet: **CE-plano gana las tres métricas** (acc 0.876 / f1-w 0.870 /
  sens 0.738); el re-balanceo desploma la exactitud (→0.56–0.63) por ~0 de sens. **Cierra 3/3
  arquitecturas.** Descarga: `outputs/results/imb_extra/`. Resul actualizado (veredicto CUMPLE completo);
  `tab:desbalance` extendido a 3 arquitecturas (32 págs, compila).

Resul: [desbalance_multimodelo_resul_20260725.md](resul/desbalance_multimodelo_resul_20260725.md).
**Veredicto: CUMPLE (parcial, 2/3 arquitecturas).** Cuadro `tab:desbalance` de `experimentacion.tex`
extendido a Swin+ConvNeXt (DenseNet se agrega al completar). Descarga: `outputs/results/imb_extra/`.

### Mejoras al documento (2.ª tanda de `mejoras.md`) — **Sin jobs SLURM** (local)
Pulido de `experimentacion.tex` (6 ítems + lineamiento): (#2) nueva figura `P24_robustness_examples.png`
—una imagen en los 5 niveles de cada perturbación con la predicción de Swin, verde/rojo según acierto—
(`scripts/robustness_examples.py`); (#3) **regenerada** `P25_interpretability.png` en layout landscape
(2 clases/fila) para que no deje hoja en blanco ni se salga de márgenes; (#4) taxonomía con ejemplos
reales de cada error + jerarquía de gravedad (hedging/contradicción < dx incorrecto/repetición); (#5)
aclarado el $\approx$0.00 del baseline SkinVL (verificado: 3/1503 aciertos = consistency 0.002, colapso de
modo); (#6) nuevo Cuadro `tab:costo_total` con costo de entrenar (stage2 Mini 9.4h / LLaVA 7.0h, medido)
y de generar el test completo; lineamiento: auditados los floats (15 tablas + 20 figuras, todos con
caption/número). **Pendiente #1** (desbalance en más modelos) — requiere experimento nuevo en TOKO.
Doc compila 30 págs, 0 undefined.

## 2026-07-13

### P5.3 (RAG) + P5.5 (fix repetición) — Mini-VLM con casos similares (DermLIP)
**Job Mendieta 1160209 (enviado).** SLURM: `slurm/mendieta/v3/rag_generation.sh` (alias `rag_gen`).
Índice RAG precomputado **local** con embeddings DermLIP (`scripts/build_rag_index.py` →
`outputs/rag/rag_context.csv`, k=3; **dato: kNN-dx da 0.831 acc**, la recuperación sola casi iguala a un
clasificador). Subido por scp (outputs/ excluido de sync_up). Condiciones (Mini-VLM, n=400, con
rep_penalty=1.3/no_repeat_ngram=3): (1) `full_rag` RAG-only, (2) `full_swin_rag` grounding+RAG,
(3) `full_swin_rep` grounding sin RAG con fix (aísla RAG + valida P5.5 vs `full_swin` previo).
Cambios de código: `--rag_context_csv/--rag`, templates RAG, `--repetition_penalty/--no_repeat_ngram_size`
+ forward de `**kwargs` a `model.generate` en llava_med/mini_vlm (SkinVL hereda). **Pendiente análisis.**

### P5.1 Ensamble de clasificadores + P5.2 Wilcoxon — **Sin jobs SLURM** (local)
Ronda P5 (mejorar resultados). **P5.1:** voto suave Swin+ConvNeXt (re-eval con TTA local,
`scripts/reeval_tta_probs.py` + `scripts/classifier_ensemble.py`) → sens. macro 0.846 vs mejor individual
0.827 (Δ+0.019, a 2× costo). **P5.2:** Wilcoxon por clase agregado a `statistical_tests.py` (Swin domina
todo clase-a-clase p<0.05; los 2 VLMs generales indistinguibles entre sí p=1.0). Resul:
[mejoras_p5_local_resul_20260713.md](resul/mejoras_p5_local_resul_20260713.md). **Veredicto: CUMPLE.**
Plan: [mejoras_resultados_p5_plan](ideas/mejoras_resultados_p5_plan_20260713.md). Pendiente integrar a tex.

### P4.2 (mejoras.md #8) — SkinVL baseline con prompts alternativos
**Job Mendieta 1160208 (COMPLETED, 1h03m).** SLURM: `slurm/mendieta/v3/skinvl_baseline_prompts.sh` (alias
`skinvl_prompts`). 2 prompts alternativos (diagnóstico directo / rol clínico) × 400. **Resultado:** el
prompt NO des-colapsa — solo cambia el atractor (baseline 72% "tinea corporis" → prompts nuevos 33–56%
"lichen planus pigmentosus"). Ambos diagnósticos están **fuera de las 7 clases de HAM** → confirma mismatch
de distribución MM-Skin→HAM, no del prompt. Resul:
[skinvl_prompts_p42_resul_20260715.md](resul/skinvl_prompts_p42_resul_20260715.md). **Veredicto: CUMPLE.**
Integrado a `experimentacion.tex` §SkinVL. Cierra mejora #8.

### P5.3 (RAG) — Grounding por recuperación (DermLIP), Mini-VLM
**Job Mendieta 1160552 (COMPLETED, 5h44m)** (re-envío del 1160209 que crasheó por los params de repetición
P5.5, incompatibles con Mini-VLM). Índice RAG local (`build_rag_index.py`, k=3, kNN-dx acc **0.831**).
Condiciones `full_rag` (RAG-only) y `full_swin_rag` (grounding+RAG), n=400.
**Resultado:** RAG-only lleva consistency 0.20→**0.76** (≈ clasificador Swin 0.83) SIN clasificador
entrenado, con el **entity recall más alto (0.91)**; sumar RAG sobre el clasificador aporta poco
(0.83→0.84, baja riqueza). Resul: [rag_resul_20260719.md](resul/rag_resul_20260719.md). **Veredicto:
CUMPLE.** Integrado a `experimentacion.tex` §Grounding por recuperación (RAG) (`tab:rag`).
P5.5 sigue diferido a LLaVA-Med.

### P4.1 (mejoras.md #9) — Ablaciones imagen-vs-dx y dx-erróneo en LLaVA-Med y Mini-VLM
**Job Mendieta 1160045 (COMPLETED, 6h20m).** SLURM: `slurm/mendieta/v3/ablations_llava_mini.sh`
(alias `abl_llava_mini`). Genera, para `llava_med` y `mini_vlm` (checkpoints `stage2_*_v2`, `--limit 400`):
`full_oracle_noimage` (`--no_image`) y `full_wrong_swap` (dx swap). Objetivo: extender a los otros
generadores las ablaciones que estaban solo sobre SkinVL.

Bajada targeted (tar+scp, 4 carpetas × 400). **Bug conocido:** el job no pasó `--label_csv` → `gt_label`
vacío; parcheado local desde `outputs/full_dx_oracle.csv` (image_id sin `.jpg` → diagnosis). Evaluación
de *diagnostic consistency* sobre el conjunto común (n=400): `outputs/results/ablation_llava_mini_p41.json`.

**Resultado (consistency):** P1.2 imagen-vs-dx Δ(oracle−noimage): SkinVL +0.03, **LLaVA-Med −0.15**
(la imagen introduce duda: 0.85→1.00 al quitarla), Mini-VLM 0.00. P1.3 dx-erróneo: 0.07–0.11 en los tres.
El patrón de SkinVL se generaliza: la fidelidad la aporta el clasificador, la imagen es prescindible, el
error del clasificador se propaga íntegro. Resul:
[ablaciones_p41_resul_20260713.md](resul/ablaciones_p41_resul_20260713.md). **Veredicto: CUMPLE.**
Integrado a `experimentacion.tex` §Ablaciones (Cuadro nuevo, 3 generadores). Cierra mejora #9.

---

## 2026-07-05

### Extensión jul-ago: arranque — verificación SOTA + P0.1 Calibración — **Sin jobs SLURM** (local)
Se organizó el feedback del tutor ([feedback_20260705.md](feedback_20260705.md)) en un backlog
priorizado: [plan-julio-agosto.md](plan-julio-agosto.md) (P0 local / P1 cluster SkinVL / P2 / P3).

**Previo (misma tanda, docs `Docs/`):** verificación de TODOS los números SOTA contra los papers
(Skin-R1, MM-Skin, SkinSavvy2 tenían cifras erróneas → corregidas en `experimentacion.tex` y
`tablas_comparativas_sota_v32.tex`; los 9 papers externos estaban OK). Enriquecimiento de las tablas
SOTA de clasificación (PanDerm, SkinVL, Mini-VLM, FT) y generación (nuestros modelos + KD/DermatoLlama/
PeFoMed, con caveat de métricas léxicas).

**P0.1 Calibración (local):** ECE/MCE/Brier + reliability diagrams sobre `y_prob` ya guardado
(`modern_v3`, n=1503). Código nuevo: `src/evaluation/classification.py` (funciones de calibración) +
`scripts/evaluate_calibration.py`. Salida: `outputs/results/calibration/`.
**Hallazgo:** los clasificadores están mal calibrados (ECE 0.19–0.39) pero **sub-confiados**, no
sobre-confiados (Swin: conf media 0.42 vs acc 0.795); los más precisos (Swin/ConvNeXt) son los peor
calibrados. `eval_dermlip_classify.py` modificado para guardar `y_prob` (falta re-correr DermLIP local).
Resul: [calibracion_resul_20260705.md](resul/calibracion_resul_20260705.md). **Veredicto: CUMPLE.**

**P0.2 Tests estadísticos (local):** IC bootstrap 95% + McNemar exacto sobre los 1503 del test HAM
(Swin vs DermLIP vs Mini-VLM vs LLaVA-Med). Código: `scripts/statistical_tests.py`. Todas las diferencias
p<0.001; el gradiente de especialización tiene IC no solapados y los VLMs generales quedan en IC que
abrazan el azar (sens. macro Mini [0.137,0.152], LLaVA [0.145,0.168], azar=0.143). Ensamble pendiente de
P0.3 (script acepta `--consistency_json`). Resul:
[tests_estadisticos_resul_20260705.md](resul/tests_estadisticos_resul_20260705.md). **Veredicto: CUMPLE.**

**P0.3 Análisis por clase del ensamble (local):** Diagnostic Consistency / Clinical Recall por clase gt
× condición de grounding (report-only), sobre los 400×4×2 reportes ya generados. Código:
`src/evaluation/clinical_ner.py` (`diagnostic_consistency_flags`) + `scripts/per_class_ensemble.py`.
Salida: `outputs/results/per_class/` (heatmap + summary + arrays por-reporte). **Hallazgo:** el grounding
rescata sobre todo las clases **minoritarias** colapsadas (Mini-VLM AKIEC 0.00→0.83, BKL 0.07→0.77 con
Swin); un clasificador débil (DermLIP) **daña** las clases fuertes de LLaVA (mel 0.85→0.69). Cierra P0.2
ensamble: propagación monótona significativa (McNemar p<1e-16, IC no solapados). Resul:
[per_class_ensemble_resul_20260705.md](resul/per_class_ensemble_resul_20260705.md). **Veredicto: CUMPLE.**

**P0.4 Comparación de costo (local + logs):** params/VRAM/latencia. Clasificadores medidos en vivo (RTX
4070); VLMs parseados de logs SLURM (A30). Código: `scripts/measure_cost.py`. Salida:
`outputs/results/cost/` (json + `cost_latency.png`). **Hallazgo:** brecha ~3–4 órdenes: clasificadores
4–12 ms/img y <1 GB en GPU de consumo; VLMs 24 s (Mini) / 66 s (LLaVA-Med) por reporte y 10–14 GB en A30.
La clasificación es barata; la generación domina el costo del ensamble. Resul:
[costo_resul_20260705.md](resul/costo_resul_20260705.md). **Veredicto: CUMPLE.**

**P0.5 Taxonomía de errores (local):** clasificación por reglas del error principal de cada reporte, por
condición de grounding. Código: `scripts/error_taxonomy.py`. Salida: `outputs/results/error_taxonomy/`
(barras apiladas + summary). **Hallazgo:** el grounding bueno elimina `dx_incorrecto` (→0 con oracle) y
`contradiccion`; un clasificador débil (DermLIP) **dispara** `dx_incorrecto` (Mini 0.30→0.60 = propagación
de error); el `hedging` **persiste** aun con dx perfecto (Mini oracle 0.43). Resul:
[error_taxonomy_resul_20260705.md](resul/error_taxonomy_resul_20260705.md). **Veredicto: CUMPLE.**

**P0.6 Integración en LaTeX (local):** los 5 resultados P0.1–P0.5 integrados en
`Docs/experimentacion/experimentacion.tex` (**21 págs**, 0 refs sin resolver): subsección de calibración
(Cuadro+figura) + significancia estadística; análisis por clase (heatmap) + taxonomía de errores (figura)
en la sección de ensamble; sección nueva de **Costo computacional** (tabla+figura); DermLIP en profundidad
(por qué el contrastivo/Derm1M discrimina); frase-caveat de métricas. Figuras copiadas a `imagenes/`.
**Veredicto: CUMPLE.**

**Ola 1 — SkinVL (P1.1): conversión OK + ola completa lanzada (2026-07-07).**
Tras 2 fixes del conversor (vocab 32000 vs 32064 → copia parcial de embed/lm_head conservando filas del
token de imagen; tokenizer fast no parsea → copiar archivos crudos del base en vez de re-serializar), el
**job 1159527 (COMPLETED)** convirtió SkinVL a HF y corrió el smoke: SkinVL carga (fallback tokenizer
lento), genera texto derma coherente y **responde al grounding** (oracle: nevus/dermatofibroma/melanoma
según dx). **Señal:** el *baseline* colapsa (5 imgs distintas → reporte idéntico "tinea corporis") y la
morfología se ve boilerplate → SkinVL usa poco la imagen (lo cuantificará la ablación P1.2). Veredicto
smoke: PASS. **Ola completa job 1159785 (PD)**: baseline + grounding{oracle,swin,dermlip} + no_image
(P1.2) + wrong_dx (P1.3) sobre el test split 1503 (~4-7 s/reporte). `wrong_swap.csv` generado en cluster.
**Resultado (COMPLETED, 10h24m):** SkinVL grounded ≈ Mini-VLM (Swin 0.80, oracle 1.00) y supera a
LLaVA; **NO hedea** (0.00 vs LLaVA 0.20-0.27 / Mini 0.37-0.43) → decisivo; pero reportes terse (recall
0.33-0.50 vs 0.75-0.79) y baseline colapsa total (0.00). **Ablaciones:** P1.2 oracle 1.00 vs sin-imagen
0.97 → la imagen aporta ~nada dado el dx; P1.3 dx-erróneo cons 0.11 → se compromete con el error. Fidelidad
del ensamble = clasificador, no la visión del generador. (`gt_label` parcheado desde `full_dx_oracle.csv`;
el SLURM no pasó `--label_csv`.) Resul: [skinvl_resul_20260707.md](resul/skinvl_resul_20260707.md).
**Veredicto: CUMPLE.**

**P2.1 Plantilla clínica (local):** baseline de generación por plantilla (clasificador→dx→morfología fija).
Código: `scripts/generate_template_report.py`. **Hallazgo:** la plantilla iguala/supera a los VLM en
diagnostic consistency (Swin-grounded 0.828 vs LLaVA 0.703 / Mini 0.830; oracle 1.000) a costo cero, pero
con menor recall (0.42 vs 0.75–0.79). El aporte del VLM es riqueza/fluidez, no fidelidad. Resul:
[plantilla_resul_20260707.md](resul/plantilla_resul_20260707.md). **Veredicto: CUMPLE.**

**P2.2 Manejo del desbalance — TOKO jobs 96860–96863 (PD).** Swin-Tiny (recipe modern), variando solo la
loss: CE-plano (`--class-weights none`) / CE-weighted / Focal γ=2 / Balanced-softmax. Código nuevo:
`BalancedSoftmaxLoss` en `src/training/losses.py`; flags `--class-weights {auto,none}` y
`--balanced-softmax` en `train_classifier.py`; aliases `imb_swin_*` en `toko/submit.py`. Fix del mismo bug
de `stderr` None en `toko/submit.py`. Plan: [desbalance_plan_20260707.md](ideas/desbalance_plan_20260707.md).
Objetivo: ver si el manejo del desbalance mueve la aguja o el clasificador ya es robusto.
**Resultado (COMPLETED):** CE-plano (sin manejo) es el MEJOR — acc 0.923 / sens_macro **0.887**; las
class-weights EMPEORAN (sens 0.809), Focal/Balanced-softmax intermedios (0.857). El desbalance de HAM no
es el cuello de botella del clasificador → refuerza que el colapso VLM no es desbalance. Resul:
[desbalance_resul_20260707.md](resul/desbalance_resul_20260707.md). **Veredicto: CUMPLE.**

**P2.4 Robustez por perturbación (local, RTX 4070):** JPEG/ruido/blur/resolución en 5 niveles sobre el
test de HAM, midiendo caída de sens. macro. Se bajaron de TOKO los checkpoints `swin_tiny_modern_v3` y
`convnext_tiny_modern_v3` (los locales eran legacy colapsados). Código: `scripts/robustness_perturbations.py`.
**Hallazgo:** el **ruido** es lo más dañino (Swin 0.74→0.38 con ruido moderado); la **resolución** lo más
tolerado (~0.53 aun severa); degradación gradual. Integrado a `experimentacion.tex` (§Robustez, fig).
Resul: [robustez_resul_20260707.md](resul/robustez_resul_20260707.md). **Veredicto: CUMPLE.**

**P2.3 Clásicos sobre embeddings (local, RTX 4070):** SVM/RF/LogReg sobre embeddings congelados de DermLIP
vs Swin-ImageNet. Se instaló `open_clip_torch 3.3.0` (+ `timm`) local para cargar DermLIP. Código:
`scripts/embeddings_classical.py`. **Hallazgo:** SVM sobre embeddings **DermLIP F1 0.881 / sens 0.788 ≈
Swin fine-tuneado (0.882)** sin entrenar modelo pesado; la representación genérica (Swin-ImageNet) rinde
mucho menos (sens 0.58). La representación derm-especializada es lo determinante. Integrado a
`experimentacion.tex` (§DermLIP). Resul: [embeddings_resul_20260707.md](resul/embeddings_resul_20260707.md).
**Veredicto: CUMPLE.**

**P2.5 Interpretabilidad (local, RTX 4070):** Grad-CAM sobre Swin + saliencia por gradiente sobre DermLIP,
una imagen por clase. Código: `scripts/interpretability.py`. **Hallazgo:** ambos atienden la **lesión**
(no el fondo); Swin más focalizado. Caso honesto: BCC → atiende bien pero predice MEL (error de
discriminación, no de atención). Integrado a `experimentacion.tex`. Resul:
[interpretabilidad_resul_20260707.md](resul/interpretabilidad_resul_20260707.md). **Veredicto: CUMPLE.**

**Integración LaTeX final:** `experimentacion.tex` = **24 páginas**, 0 refs sin resolver. Todo el backlog
P0/P1/P2 del plan jul-ago quedó cerrado.

**Ola 1 — SkinVL (P1.1): [historial] conversión movida al cluster (RAM local insuficiente, 32 GB).**
`zwq803/SkinVL-MM` descargado en Mendieta (14 GB; base ya cacheado). Conversión a HF vía trasplante de
pesos sobre el HF base + **smoke test** (5 imgs) en un mismo job GPU (Mendieta exige >=1 GPU):
**job 1159067 (PD)**. Detalle de-risk: SkinVL trae solo pesos fine-tuneados (295 tensores, sin vision
tower); el conversor los renombra al schema HF. Bug de descarga xet en Windows → se hace todo en el
cluster (Linux). Fixes: `submit.py` (stderr None + `logs/skinvl`). Runbook:
[skinvl_runbook_20260705.md](ideas/skinvl_runbook_20260705.md).

**Prep Ola 1 — SkinVL (P1.1):** de-risk de `zwq803/SkinVL-MM` → **pesos FULL, formato original
LLaVA-Med** (`LlavaMistralForCausalLM`), no HF → requiere conversión a HF (no LoRA; sin versión HF
publicada; transformers 5.2 sin conversor). Creado: wrapper `src/models/skinvl.py` (subclass fino de
LLaVAMed) + registro en `factory.py`; flag `generate_report.py --no_image` (P1.2, testeado);
`scripts/make_wrong_dx.py` (P1.3, testeado); SLURM `slurm/mendieta/v3/generate_reports_skinvl.sh`
(baseline+grounding+no_image+dx-erróneo). Plan/gating:
[skinvl_ensemble_plan_20260705.md](ideas/skinvl_ensemble_plan_20260705.md). **Gate:** conversión HF +
validar carga local antes de encolar.

---

## 2026-06-18

### Consolidación + refinamiento (test split completo) en paralelo — Mendieta
Inicio de la fase de consolidación (documento LaTeX: cuadros/figuras/samples). En paralelo, para
aprovechar la cola, se lanza el **refinamiento**: completar el ensamble al **test split completo (1503)**
(antes 400). Reutiliza `ensemble_full_{llava,mini}.sh` sin `--limit` (resume defensivo saltea las 400
ya generadas) → números definitivos para las tablas.

**Jobs:** 1157589 (LLaVA full test), 1157590 (Mini full test) — Mendieta, 2 días, resume si timeout.

**Extensión (documentada, pendiente de integración):** **SkinVL** (`zwq803/SkinVL-MM`, HF) — VLM
derm-especializado (LLaVA-Med-v1.5-7B + LoRA sobre MM-Skin). Candidato a tercer generador del ensamble.
Requiere wrapper + descarga/cache en cluster. Plan: [consolidacion_y_extensiones_plan_20260618.md](ideas/consolidacion_y_extensiones_plan_20260618.md).

**Entregables de consolidación creados:**
- **Documento LaTeX formal:** `Docs/experimentacion/` (`experimentacion.tex` + `referencias.bib` +
  `imagenes/`). Compila limpio (**15 páginas**, 0 citas sin resolver). 2.ª revisión (feedback tutor):
  resumen reescrito; intro con estrategias explicadas + cómo se refutó el desbalance; figuras nuevas
  (distribución HAM, colapso de predicciones); métricas contextualizadas a la tesina; diseño detallado
  + diagrama zero-shot/likelihood; SOTA con supervisados + análisis de la contradicción LLaVA-Med
  (accuracy inflada por NV); DermLIP descrito y sustentado; generación con ejemplo de estructura + diseño
  detallado + por qué ensamble (con desventajas y valor del razonamiento); "entorno real" (no producción);
  ejemplos verboso/conciso; tabla SOTA generación; conclusiones atadas a los objetivos del plan; límites
  (400 solo en reportes, costo de cola 4-6 días). Versión previa:
  intro detallada del proceso iterativo; datasets con rol explicado; métricas explicadas (qué/por qué);
  **2 tablas de comparación SOTA** (clasif.\ + generación) con el caveat de accuracy-inflada-por-NV;
  re-diagnóstico (4 evidencias) y conjetura del fallo; origen de `<think>` (SkinCoT=CoT); justificación
  del ensamble + `diagnostic consistency` + `noreasoning`; baseline/oracle/gt definidos; figuras
  descritas; **3 ejemplos cualitativos** largos con criterios buen/mal reporte. 7 cuadros, 3 figuras,
  2 esquemas TikZ.
- **Material de apoyo:** `Codigo/docs/consolidacion/` (tablas.tex, figuras/, samples.md).
- Figuras con métricas ampliadas (Acc/F1/sens en clasificación; consistency+recall en ensamble;
  léxicas en SkinCoT).

### Ensamble — Nivel 1 sobre SkinCoT + prep local — Mendieta
Para paralelizar (3 jobs simultáneos), se lanza el Nivel 1 sobre **SkinCoT** (único dataset con
referencias). Genera el SkinCoT test split (460 imgs, 23 clases) con LLaVA bajo baseline vs
oracle-noreasoning, `--reference_dir` para Nivel 1.

**Implementación:** CSV oracle SkinCoT (`outputs/skincot_dx_oracle.csv`, image_id→clase DermNet, subida
por scp); SLURM `ensemble_skincot_level1_llava.sh`. **Prep local:** flag `--strip-reasoning` agregado a
`evaluate_reports.py` (elimina `<think>` → mide report-only automático).

**Job:** 1156725 (LLaVA-Med v2, SkinCoT, baseline + oracle) — COMPLETED.
**Cluster:** Mendieta
**Resultados (analizado 2026-06-18):** baseline BLEU 0.102 / METEOR 0.330 / CIDEr 0.054, consistency
0.392; oracle BLEU 0.040 / METEOR 0.209 / CIDEr 0.038, consistency **0.567**. **Trade-off:**
grounding+noreasoning ↑ consistency (0.39→0.57) pero ↓ léxico (reporte conciso vs referencia CoT
verbosa) → para reportes, Nivel 2 es la métrica principal; Nivel 1 con caveat. Ver
[ensamble_resul §6.2](resul/ensamble_resul_20260607.md).

### Ensamble — corrida completa 4 condiciones — Mendieta
Con el prompt ganador fijo (`noreasoning`), corrida realista del ensamble: 4 condiciones sobre un
subconjunto del **HAM test split** (~400 imgs), evaluando **report-only**.

**Condiciones (grounding):** (0) baseline, (A) oracle (gt), (B) **Swin** (acc test ~0.80), (C)
**DermLIP** ZS (acc ~0.38). El gap oracle vs swin/dermlip = costo de propagación de error.

**Implementación:** split-filtering (`--splits_file`/`--split`) agregado a `generate_report.py`;
predicciones de Swin/DermLIP mapeadas a image_ids (orden idéntico, y_true coincide 1503/1503) →
CSVs `outputs/full_dx_{oracle,swin,dermlip}.csv` (subidas por scp). SLURM `ensemble_full_llava.sh`,
max_tokens 384. Swin: `modern_v3_predictions.json`; DermLIP: `dermlip_zeroshot_vit-b-16_predictions.json`.

**Jobs (en paralelo):** 1156723 (LLaVA-Med v2) + 1156724 (Mini-VLM v2) — COMPLETED.
**Cluster:** Mendieta
**Resultados (analizado 2026-06-18):** [ensamble_resul_20260607 §6](resul/ensamble_resul_20260607.md).
HAM diagnostic_consistency **report-only**:

| grounding (clasif. acc) | LLaVA | Mini |
|-------------------------|-------|------|
| baseline | 0.595 | 0.198 |
| DermLIP ZS (0.38) | 0.445 | 0.485 |
| Swin (0.80) | 0.703 | 0.830 |
| oracle (1.0) | 0.845 | 1.000 |

**Veredicto: el ensamble funciona y la calidad del clasificador propaga monótonamente.** Con Swin:
Mini 0.20→0.83, LLaVA 0.60→0.70. Un clasificador débil (DermLIP ZS) puede empeorar (LLaVA 0.445 <
baseline). Mini obedece el grounding perfecto (oracle 1.0). Receta óptima: **Swin + generador
noreasoning**.

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
| [mini_vlm_lora_llm_resul_v3_20261024.md](resul/mini_vlm_lora_llm_resul_v3_20261024.md) | Resultado | Mini-VLM v3 (LoRA en el LLM), parcial: no cambia la cascada con Swin; oracle 0.967 por el `<think>` |
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
