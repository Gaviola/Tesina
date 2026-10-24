# Resultado — Verificaciones para los pendientes del Capítulo 3

**Fecha:** 2026-10-11 · **Sin jobs SLURM** (local, CPU) · **Origen:** los `\pendiente{}` de la primera versión del
Cap. 3 (`Docs/TFG/Chapters/03-Materiales-Metodos/`). Scripts: `scripts/verificaciones_cap03.py` (HIBA, bootstrap por
lesión, Holm) y `scripts/verificaciones_cap03_vlm_ci.py` (IC de los VLM), más inspecciones de logs, datos y código
anotadas con su fuente. Los números de desempeño que aparecen acá van a los Caps. 4 y 5; el Cap. 3 solo usa el
procedimiento.

## 1. Datos

| Pregunta | Respuesta | Fuente |
|---|---|---|
| ¿Por qué se excluyen 439 imágenes de SkinCAP? | La columna «Do not consider this image» viene de SKINCON, cuyos anotadores podían marcar así las imágenes de mala calidad. Ninguna de las 439 tiene conceptos anotados; las 3 561 restantes tienen al menos uno. 419 son de Fitzpatrick 17k y 20 de DDI | `data/raw/skincare/SkinCAP/skincap_v240623.csv`; paper SKINCON p. 4 §2.2 («A label of "Do not use" was allowed to remove any images that were poor quality») |
| Origen de las imágenes de SkinCoT | Atlas DermNet (las de SkinCAP, Fitzpatrick 17k y DDI). El README no lo dice; menciona Fitzpatrick 17k, DDI y SKINCON solo para SkinCAP y en los requisitos de acceso | paper SkinCaRe pp. 3–5; `README.md` l. 82–85 y 118; carpetas de `SkinCoT/EN` con nombres de categoría de DermNet |
| ¿SkinCoT cierra con una impresión diagnóstica? | Sí: el LLM recibía la etiqueta de DermNet y debía nombrarla en la última oración. 2 942/3 041 textos tienen `<think>` | paper SkinCaRe p. 5; inspección de 4 archivos |
| MM-Skin, modalidad «derm» y tamaño | «derm» = dermatoscopía (1 039 imágenes, igual que la Tabla 2 del paper). Paper: 11 039 imágenes, 9 369 pares con texto (las subfiguras comparten leyenda). Local: 11 090 filas, 11 015 imágenes, 1 721 filas sin texto (11 090 − 1 721 = 9 369) | `MM-SkinQA/caption.csv`; zeng2025mmskin p. 3 y Tabla 2 p. 5 |
| MM-Skin: ¿Nivel 1 sobre el test? | No: sobre el archivo completo en orden, cortado por tiempo (Mini-VLM 7 129, LLaVA-Med 2 601 reportes v2; incluyen 4 963/1 814 de la partición de train). Ningún generador propio se ajustó con MM-Skin; SkinVL-MM sí, y no se evalúa sobre él | `slurm/mendieta/v2/generate_reports_{mini,llava}.sh:92-102`; `ejecuciones.md:1326-1327` |
| **MM-Skin: referencias «nan»** | **539 reportes de Mini-VLM y 175 de LLaVA-Med tienen como referencia la cadena «nan»** (filas sin descripción) y entran en las métricas de Nivel 1: `generate_report.py` no filtra NaN y `evaluate_reports.py:87` solo descarta cadenas vacías. Hay que recalcular Nivel 1 excluyéndolas | `outputs/generated_reports/*/v2/mmskin/` |
| HIBA: ¿1 616 o 243? | 1 616 (completo). Los `*_hiba_test_results.json` tienen `n_samples` 1616; `HIBADataset` sin `splits_file` no filtra. El test de 243 de `hiba_splits.json` no se usa | `train_classifier.py:587-592`; `hiba.py:71-76` |
| SkinVL: método | LLaVA-Med v1.5 + LoRA (rango 128, alpha 64, lr 5e-5) sobre el LLM y la proyección visual, CLIP congelado, una etapa. Variante usada: SkinVL-MM (solo MM-Skin). Los pesos publicados son completos (LoRA probablemente fusionado; el paper no lo dice). El Cap. 2 (`10-estado-arte.tex:351-353`) da 171 600 imágenes, que es SkinVL-PubMM | zeng2025mmskin pp. 6–7 |
| Generación sin diagnóstico | Ningún generador cierra con una impresión diagnóstica. Mini-VLM: diferencial abierto, 330/1 503 dicen que no se puede dar un diagnóstico definitivo. LLaVA-Med: copia la plantilla de SkinCoT; 1 354/1 503 (90 %) quedan cortados por el límite de 384 tokens antes de la conclusión | `generated_reports/{mini_vlm,llava_med}/full_baseline/` |

## 2. Entrenamiento e historia de decisiones

| Pregunta | Respuesta | Fuente |
|---|---|---|
| Piloto de *noreasoning* | Primeras 100 imágenes de HAM por nombre (ISIC_0024306–0024405), sin `--split`: en la partición por lesión, 67 train, 10 val, 17 test y 6 excluidas. La variante se eligió con la consistencia del reporte respecto del diagnóstico inyectado | `pilot_ensemble*_llava.sh:34-39`; `generate_report.py:316-342`; `ensamble_resul_20260607.md:63-66` |
| Clúster de la generación de Mini-VLM | Mendieta en todas las corridas (v1, v2, `full_*`, re-anclaje, RAG); TOKO solo clasificación | `jobs_log.txt` |
| DenseNet121 y ViT-B/16 fuera del barrido v4 | El plan invoca la incompatibilidad «BatchNorm + augmentación agresiva» de v1–v3, que solo se analizó para DenseNet; ViT-B/16 usa LayerNorm | `clasificadores_sweep_modern_v4_plan_20260510.md:15`; `clasificadores_resul_iteraciones_20260429.md:228-230` |
| Cabezas sobre DermLIP | Valores fijos (logística C = 1, SVM C = 10, kNN k = 3); sin búsqueda sobre validación | `dermlip_split_eval.py:100-115`; `embeddings_classical.py:80-82` |
| Etapa 1 de la generación | El último `stage1_<m>/best_model.pt` escrito en Mendieta es el trial t04 del barrido de fase 2: lr 1.0945e-4, 2 épocas, paciencia 0, SkinCAP 2 492/534; lote 16 (LLaVA-Med reducido a 5 × 3 = 15). Los `train_vlm_s1*.sh` (lr 1e-3) no produjeron ese checkpoint. **Confirmado** en los logs v2 1153597 (Mini-VLM) y 1153598 (LLaVA-Med): «Checkpoint Stage 1 cargado … (época 2)». Copias locales: la de LLaVA-Med no coincide con ningún trial; la de Mini-VLM está truncada | logs 1147374, 1147378; `mejores_params.txt` |
| Etapa 2: proyector, cuantización, lote | Proyector congelado (solo LoRA entrenable). Sin cuantización. Lote 4 × 8 = 32 sin reducción (logs v2: ante la falta de memoria en el primer batch solo se activa *gradient checkpointing*). Ambas corridas llegan a la época 10 con val_loss en descenso (LLaVA-Med 0.9394, Mini-VLM 1.3339): la detención temprana no se activó. «Mini eff_bs=8 (OOM)» de `reportes_resul_v1` contradice el log 1147378 (4 × 4) | `two_stage.py:1252`; `train_vlm_stage2.py:126, 296-301` |
| **LoRA: parámetros entrenables** | LLaVA-Med 33 554 432 = 27 262 976 en Mistral (q, v; 32 capas) + 6 291 456 en CLIP. Mini-VLM 6 291 456 = solo CLIP ViT-L/14 (24 capas × q, v × r 64). Confirma que el LoRA de Mini-VLM no tocó el LLM | logs v2 1153597 y 1153598 («trainable params»); checkpoint `stage2_mini_vlm_v2` |
| Latencia de LLaVA-Med | 49.4 s/reporte (job 1172480, 384 tokens) a 66.1 s (job 1154213, 512 tokens); `cost_comparison.json` toma 66.1. Si se re-ejecuta `measure_cost.py`, Mini-VLM pasa de 24.1 a 50.3 por el log de 1179315 | `measure_cost.py:80-95` |

## 3. Cálculos estadísticos

**HIBA (n = 1 616), IC bootstrap 95 % (2000, semilla 42), TTA, semilla 42:**

| Modelo | Sensibilidad macro | Exactitud | F1 macro |
|---|---|---|---|
| Swin-Tiny t06 | 0.424 [0.392, 0.456] | 0.546 [0.522, 0.571] | 0.419 [0.387, 0.448] |
| ConvNeXt-Tiny t02 | 0.447 [0.413, 0.480] | 0.558 [0.532, 0.581] | 0.435 [0.403, 0.464] |

**Bootstrap por imagen frente a por lesión** (Swin − ConvNeXt, test por lesión, 1 503 imágenes, 1 429 lesiones):

| Métrica | Δ | Por imagen | Por lesión |
|---|---|---|---|
| F1 macro | +0.029 | [−0.015, +0.074] | [−0.015, +0.076] |
| Sensibilidad macro | +0.022 | [−0.027, +0.071] | [−0.029, +0.071] |
| Exactitud | +0.002 | [−0.014, +0.018] | [−0.014, +0.017] |

Remuestrear por lesión no cambia ninguna conclusión.

**Corrección de Holm** (`statistical_tests_les.json`, 21 pares por familia): McNemar, 19 significativas con y sin
Holm (no lo son Swin–ConvNeXt y DenseNet–ViT). Wilcoxon por clase: 10 sin corrección, 0 con Holm. Con siete clases el
menor p posible es 0.0156, por encima del primer umbral de Holm (0.05/21 = 0.0024): Wilcoxon con N = 7 no puede dar
significancia en una familia de 21.

**VLM ajustados (HAM10000, 1 503), IC bootstrap:** LLaVA-Med verosimilitud v1 exactitud 0.037 [0.028, 0.047]; v2
ajustado 0.179 [0.159, 0.196]; CoT v2 0.031 [0.023, 0.040]. Mini-VLM verosimilitud v2 0.660 [0.635, 0.684] con
sensibilidad macro 0.141 [0.140, 0.142] (colapso en NV); CoT v2 0.111 [0.096, 0.127].

**Protocolos:** la prueba sin imagen usa una imagen gris de 224 × 224, ensamble de 4 *prompts*, modelo base
(`finetuned=False`), vista única. VLM *zero-shot* sobre foto clínica: todo SkinCAP filtrado por `SKINCAP_TO_HAM`
(n = 624), no su test. Consistencia: n = 1 503 en los brazos principales; 400 en las ablaciones (`oracle_noimage`,
`wrong_swap`, `rag`, `swin_rag`, `uncertainty`); 248 en el diferencial; 1 452 no derivadas. `full_swin_rep` de
Mini-VLM está vacío.

## 4. Conclusión (veredicto)

**CUMPLE** como verificación: se respondieron 19 de los 26 pendientes del Cap. 3 con fuente. Quedan como decisiones
del autor: mencionar la segunda opinión del 03/10, semillas del barrido, justificación de ViT-B/16 fuera del barrido,
maligno frente a benigno, corrección de Holm y LoRA de Mini-VLM (declarar o reentrenar). Acciones propuestas: (1) recalcular el Nivel 1 de MM-Skin sin las referencias «nan» (local);
(2) si se decide reentrenar Mini-VLM con LoRA sobre
`qkv_proj`, plan nuevo y job en Mendieta.
