# Registro de Ejecuciones

Ayuda-memoria cronológico de experimentos enviados a cluster, ordenado de más reciente a más antiguo.

---

## 2026-08-05

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
