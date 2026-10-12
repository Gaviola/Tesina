# Plan — Mini-VLM v3: LoRA sobre el modelo de lenguaje

**Fecha:** 2026-10-12
**Origen:** [verificaciones_cap03_resul](../resul/verificaciones_cap03_resul_20261011.md). El `stage2_mini_vlm_v2` tiene
6 291 456 parámetros LoRA, todos en el codificador CLIP: Phi-3.5-vision fusiona la atención del LLM en `qkv_proj`, y
`target_modules=["q_proj", "v_proj"]` solo coincide con la atención de CLIP. El LLM de Mini-VLM nunca se ajustó, a
diferencia de LLaVA-Med (33 554 432 parámetros: 27.3 M en Mistral + 6.3 M en CLIP). La tesina describe el ajuste como
LoRA sobre el modelo de lenguaje. **Decisión del autor (2026-10-12):** reentrenar y regenerar los experimentos que
usan ese checkpoint.

## Hipótesis / pregunta

¿Ajustar el LLM de Mini-VLM cambia (1) su clasificación por verosimilitud y CoT, (2) la consistencia diagnóstica de
sus reportes con y sin anclaje, y (3) sus métricas con referencia? Cualquier resultado es reportable: el objetivo es
que el modelo que la tesina describe sea el que se evaluó.

## Diseño

- **Etapa 2 v3:** idéntica a v2 (lr 2.495e-5 constante, 10 épocas, paciencia 3, lote 4 × 8, r 64, alpha 64, dropout 0,
  SkinCoT EN, misma etapa 1 `stage1_mini_vlm/best_model.pt`, semilla 42) salvo
  `--lora_target_modules qkv_proj q_proj v_proj`: LLM (q, k, v fusionados) + CLIP (q, v), lo más parecido a LLaVA-Med
  sin partir la matriz fusionada. Verificado sin cargar pesos (`init_empty_weights` + `get_peft_model`): 31 457 280
  entrenables = 25 165 824 en el LLM + 6 291 456 en CLIP. Salida `outputs/checkpoints/stage2_mini_vlm_v3/`.
- **Regeneración con el checkpoint v3** (jobs que dependen del entrenamiento, `afterok`), salidas en
  `outputs/generated_reports/mini_vlm_v3/` y `outputs/results/mini_vlm/v3/` (no se pisa nada de v2):
  1. Cascada (test 1503): `full_baseline`, `full_dermlip`, `full_swin_les`, `full_oracle` y `full_differential_les`
     (248), con los mismos `full_dx_*.csv` e índices que v2.
  2. Brazos extra: `full_rag_les`, `full_swin_rag_les` (1503) y las ablaciones `full_oracle_noimage`,
     `full_wrong_swap` (400, como en v2).
  3. Clasificación con el checkpoint: verosimilitud y CoT sobre el test de HAM10000.
  4. Nivel 1 con la partición de prueba: MM-Skin test (1653) y SkinCoT test (457), con referencia.
- **LLaVA-Med v2, Nivel 1 con la partición de prueba** (sin dependencia): MM-Skin test y SkinCoT test, para comparar
  con Mini-VLM v3 sobre las mismas imágenes (los v2 cubrían el archivo completo cortado por tiempo).
- Decodificación igual que v2: voraz, 384 tokens, semilla 42.
- **Evaluación local:** `ensemble_bootstrap.py --model mini_vlm_v3 --anchor les --report_only --strict`,
  `rag_les_eval.py`, `evaluate_reports.py` / `level1_mmskin_recalc.py` y `evaluate_classify.py`, contra v2.

## Criterios de éxito / interpretación

- **Completo:** checkpoint v3 con `trainable params` ≈ 31.5 M en el log; todos los brazos con sus conteos
  (`run_arm`).
- **Lectura:** se reportan v3 frente a v2 con *bootstrap* pareado. Si v3 no cambia la cascada (la fidelidad viene del
  clasificador), la conclusión del Cap. 5 se mantiene y se declara que el ajuste del LLM no la altera. Si cambia,
  las tablas del Cap. 5 pasan a v3 y v2 queda como antecedente.

## Sincronización con clústeres

- No hay jobs corriendo en Mendieta.
- Cambios de código que el clúster necesita: `scripts/train_vlm_stage2.py` (`--lora_target_modules`, métricas
  versionadas por `--run-name`), `scripts/generate_report.py` (filtro de partición con extensión, referencias NaN) y
  los `.sh` de `slurm/mendieta/v5/`. Se suben por `scp` esos archivos (la carpeta principal del repo está en otra rama
  y `sync_up` subiría código viejo); se verifica md5 remoto. `train_vlm_classify.py` remoto debe ser igual al local
  (se verifica md5).
- `submit.py` gana `--after JOBID` (`sbatch --dependency=afterok:JOBID`) y los alias `*_v3`.
- **Validación local:** `bash -n` de los `.sh`; conteo de parámetros LoRA sin cargar pesos (hecho); no se entrena
  localmente.

## Costo estimado

Entrenamiento ~9.5 h (v2: 9 h 21 min). Generación Mini-VLM ~16.5 s/reporte sin RAG y ~25 s con RAG: cascada
6 260 reportes ≈ 29 h; extra 3 006 + 800 ≈ 25 h; Nivel 1 2 110 ≈ 10 h; clasificación ≈ 2 × 6 h. LLaVA-Med Nivel 1:
~2 100 × 50–66 s ≈ 30–38 h (se reanuda si corta). Límite por job: 2 días. Cola de Mendieta: 5–10 días.
