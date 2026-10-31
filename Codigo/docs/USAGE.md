# Guía de uso — DermVLM

Cómo instalar el entorno, preparar los datos y ejecutar cada etapa de la experimentación de la tesina. Las etapas
siguen el orden de la Tabla B.1 del Apéndice B. Todos los comandos se ejecutan desde `Codigo/`, y cada script
documenta sus opciones con `--help`.

Los hiperparámetros viven en `configs/` (YAML); los scripts los leen y no los fijan en el código. Los datos se
guardan en `data/` y los resultados en `outputs/`, dos carpetas que no se versionan.

---

## 1. Instalación

Requisitos: Python 3.10 o superior y, para entrenar y generar, una GPU NVIDIA con soporte de bf16 (Ampere o
posterior).

```bash
python -m venv .venv
source .venv/bin/activate        # Linux
.venv\Scripts\activate           # Windows

python scripts/setup_env.py      # instala PyTorch según la GPU y después requirements.txt
pip install -e .
```

`requirements.txt` no incluye `torch` ni `torchvision`, para no instalar la versión sin GPU por defecto. Para
instalarlos a mano, elegir el índice de PyTorch que corresponda al driver (por ejemplo,
`pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128`) y después
`pip install -r requirements.txt` y `pip install -e .`.

DermLIP necesita además `open_clip_torch`, y la evaluación de entidades clínicas, los modelos de SciSpaCy:

```bash
pip install open_clip_torch scispacy
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bionlp13cg_md-0.5.3.tar.gz
```

---

## 2. Datos

Los conjuntos se descargan a mano a `data/raw/`, salvo *SkinCaRe*, que descarga el propio script.

| Conjunto | Fuente | Destino |
|---|---|---|
| HAM10000 | [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T) | `data/raw/HAM10000/` |
| SkinCaRe (SkinCAP y SkinCoT) | Hugging Face `yuhos16/SkinCaRe` (acceso restringido, requiere `HF_TOKEN`) | `data/raw/skincare/` |
| MM-Skin | [GitHub ZwQ803/MM-Skin](https://github.com/ZwQ803/MM-Skin) | `data/raw/MM-SkinQA/` |
| HIBA | [GitHub piashiba/HIBASkinLesionsDataset](https://github.com/piashiba/HIBASkinLesionsDataset) | `data/raw/HIBA/` |

Estructura esperada:

```
data/raw/
├── HAM10000/
│   ├── HAM10000_metadata                 # CSV sin extensión
│   ├── HAM10000_images_part_1/           # ISIC_XXXXXXX.jpg
│   └── HAM10000_images_part_2/
├── skincare/
│   ├── SkinCAP/skincap_v240715.xlsx y SkinCAP/skincap/   # imágenes .png
│   └── SkinCoT/EN/<clase>/ y SkinCoT/images/<clase>/
├── MM-SkinQA/
│   ├── caption.csv
│   └── *.png                             # imágenes sueltas en la raíz
└── HIBA/
    ├── metadata.csv                      # la columna de id es isic_id
    └── images/
```

---

## 3. Preparación de los datos y partición por lesión

```bash
export HF_TOKEN=hf_xxxxxxxxxxxx
python scripts/prepare_data.py --download-skincare --data_dir data   # solo la primera vez
python scripts/prepare_data.py --data_dir data --seed 42 --image_size 224
python scripts/make_lesion_disjoint_split.py
```

`prepare_data.py` redimensiona las imágenes a `data/processed/` y escribe las particiones en `data/splits/`.
`make_lesion_disjoint_split.py` arma la partición de *HAM10000* disjunta por lesión
(`data/splits/ham10000_splits_lesion.json`): conserva las mismas 1 503 imágenes de prueba y reparte el
entrenamiento y la validación de modo que ninguna lesión quede en dos particiones. Todos los resultados de la tesina
usan esta partición.

---

## 4. Clasificadores supervisados

El barrido de hiperparámetros de Swin-Tiny y ConvNeXt-Tiny se envía a TOKO, un trabajo por combinación
(`configs/sweeps/phase1_modern_sweep_grid.yaml`):

```bash
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights both
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights none --trials t06 --seeds 43 44
```

El segundo comando repite la combinación elegida con las semillas 43 y 44. Para entrenar un modelo suelto:

```bash
python scripts/train_classifier.py --model swin_tiny --splits-file data/splits/ham10000_splits_lesion.json --seed 42
```

`--model` acepta `densenet`, `vit`, `convnext_tiny` y `swin_tiny`. Después del entrenamiento:

```bash
python scripts/lesion_split_report.py     # elige el ganador por F1 macro en validación y resume la partición por lesión
python scripts/classifier_ensemble.py --preset les   # ensamble por voto suave
python scripts/melanoma_detection.py      # detección de melanoma y umbral fijado en validación
```

---

## 5. Modelos visión–lenguaje en clasificación

```bash
# VLM generativos: --method generate (por defecto) o likelihood
python scripts/train_vlm_classify.py --model llava_med --method likelihood
python scripts/train_vlm_classify.py --model mini_vlm --method likelihood

# DermLIP: sin ajuste, cabezas sobre el embedding y kNN
python scripts/eval_dermlip_classify.py --checkpoint vit-b-16
python scripts/eval_dermlip_linearprobe.py --checkpoint vit-b-16
python scripts/dermlip_split_eval.py      # reajusta kNN, regresión logística y SVM con la partición por lesión
```

`train_vlm_classify.py` tiene `--dry-run`, que procesa unos pocos lotes y muestra la memoria y las respuestas
interpretadas, útil antes de enviar el trabajo al clúster. Los controles del colapso usan `--no_image` (imagen gris)
y `--eval-dataset` (fotografías clínicas).

---

## 6. Evaluación de la clasificación

```bash
python scripts/evaluate_classify.py --results_dir outputs/results
python scripts/statistical_tests.py       # bootstrap pareado y McNemar
python scripts/leakage_analysis.py        # efecto de la fuga de información de la partición por imagen
```

## 7. Evaluaciones complementarias

```bash
# Generalización a HIBA: reentrena la combinación elegida y la evalúa también en HIBA
python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights none --trials t06 --eval-hiba
python scripts/hiba_por_modalidad.py                 # HIBA por modalidad
python scripts/robustness_perturbations.py           # perturbaciones de la imagen
python scripts/evaluate_calibration.py               # ECE, Brier y diagramas de confiabilidad
python scripts/interpretability.py                   # Grad-CAM de Swin-Tiny y saliencia de DermLIP
```

---

## 8. Ajuste de los generadores

El ajuste tiene dos etapas: la primera alinea el proyector con *SkinCAP*, y la segunda ajusta con LoRA sobre
*SkinCoT*.

```bash
python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1 --lr 2e-3 --batch_size 16
python scripts/train_vlm_stage2.py --model mini_vlm \
    --checkpoint outputs/checkpoints/stage1_mini_vlm/best_model.pt
```

`--model` acepta `llava_med` y `mini_vlm`. SkinVL se usa sin ajuste: sus pesos se convierten una vez con
`slurm/mendieta/v3/convert_skinvl.sh`.

---

## 9. Pipeline y generación de reportes

El *pipeline* necesita tres archivos: el diagnóstico de Swin-Tiny, el contexto del kNN de DermLIP y el nivel del
ruteo de cada imagen.

```bash
python scripts/make_dx_csv.py \
    --predictions outputs/results/swin_tiny_sweep_t06_les_cwnone_predictions.json \
    --output outputs/full_dx_swin_les.csv
python scripts/dermlip_split_eval.py      # escribe outputs/rag/rag_context_les.csv
python scripts/build_uncertainty_3tier.py \
    --swin_csv outputs/full_dx_swin_les.csv --rag_csv outputs/rag/rag_context_les.csv \
    --output outputs/uncertainty/uncertainty_3tier_les.csv
```

El ruteo asigna a cada imagen el nivel afirmativo, diferencial o de derivación, y escribe además
`uncertainty_differential_les.csv`, con solo las imágenes del nivel diferencial. La generación de los dos primeros
niveles:

```bash
COMMON="--model mini_vlm --checkpoint outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt \
  --images_dir data/processed/HAM10000 --splits_file data/splits/ham10000_splits.json --split test \
  --max_tokens 384 --seed 42"

# Nivel afirmativo: cascada con el diagnóstico de Swin-Tiny
python scripts/generate_report.py $COMMON --diagnosis_source outputs/full_dx_swin_les.csv \
    --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/mini_vlm/full_swin_les

# Nivel diferencial: solo las imágenes de ese nivel, con los dos candidatos
python scripts/generate_report.py $COMMON \
    --uncertainty_csv outputs/uncertainty/uncertainty_differential_les.csv --uncertainty \
    --only_ids_csv outputs/uncertainty/uncertainty_differential_les.csv \
    --output_dir outputs/generated_reports/mini_vlm/full_differential_les
```

El nivel de derivación no genera reporte. Los trabajos de Mendieta que ejecutan estos pasos están en `slurm/mendieta/v4/` y `slurm/mendieta/v5/`.
`generate_report.py` retoma la generación si el trabajo se corta: saltea los reportes ya escritos.

Otras opciones de `generate_report.py`: `--model skinvl`, `--no_image` (cascada sin imagen), `--rag` con
`--rag_context_csv` (contexto recuperado) y `--image` para un reporte de una sola imagen.

---

## 10. Evaluación de los reportes

```bash
python scripts/evaluate_reports.py --model mini_vlm --level 1 --dataset <conjunto>   # BLEU, ROUGE-L, BERTScore, METEOR, CIDEr
python scripts/evaluate_reports.py --model mini_vlm --level 2                        # entidades clínicas
python scripts/ensemble_bootstrap.py --model mini_vlm --anchor les --report_only --strict   # consistencia diagnóstica
python scripts/uncertainty_analysis.py --model mini_vlm --anchor les   # resultados del ruteo
python scripts/error_taxonomy.py          # falla principal de cada reporte
```

## 11. Costo computacional

```bash
python scripts/measure_cost.py            # clasificadores, en la GPU local
python scripts/measure_vlm_memory.py --model mini_vlm \
    --checkpoint outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt --n 20   # generadores, en la A30
```

---

## 12. Ejecución en los clústeres

Cada clúster tiene sus scripts de gestión en `scripts/mendieta/` y `scripts/toko/`, con los datos de conexión en su
`config.py`:

```bash
python scripts/mendieta/setup.py          # configuración inicial, una vez
python scripts/mendieta/sync_up.py        # sube el código
python scripts/mendieta/sync_data.py      # sube los datos
python scripts/mendieta/submit.py <alias> # envía un trabajo (los alias están en submit.py)
python scripts/mendieta/monitor.py        # estado de la cola
python scripts/mendieta/sync_down.py      # baja métricas y logs (--reports, --checkpoints)
```

Los nodos de cómputo no tienen acceso a internet, así que los pesos de Hugging Face se descargan antes con
`scripts/mendieta/download_models.py`. Los trabajos SLURM están en `slurm/<clúster>/`, versionados por iteración
(`v1/` a `v5/`).

## 13. Configuración

| Archivo | Contenido |
|---|---|
| `configs/base.yaml` | Semilla, dispositivo, rutas |
| `configs/phase0_data.yaml` | Conjuntos, particiones, preprocesamiento y aumentos |
| `configs/phase1_classification.yaml` | Entrenamiento de los clasificadores |
| `configs/phase2_generation.yaml` | Ajuste de los generadores en dos etapas y LoRA |
| `configs/models/*.yaml` | Hiperparámetros de cada modelo |
| `configs/sweeps/*.yaml` | Espacios de búsqueda de los barridos |
