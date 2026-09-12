# Plan — Split disjunto por lesión, selección en validación y semillas

**Fecha:** 2026-09-12 · **Cluster:** TOKO (RTX 4080, cola corta) + local (RTX 4070)
· **Origen:** [feedback_20260912.md](../feedback_20260912.md) (acciones 1, 2, 4, 8, 10, 11)

## Motivación

El tutor pidió verificar que el split de HAM10000 no mezcle una misma lesión entre train y test, y que la
selección de hiperparámetros/checkpoints se haya hecho solo con validación. La auditoría previa a este plan
(`scripts/leakage_analysis.py`, `outputs/results/leakage_analysis.json`) encontró tres problemas:

1. **Leakage lesión-nivel.** `prepare_data.py` estratifica **por imagen**. HAM10000 tiene 10015 imágenes de
   7470 lesiones (no publica id de paciente; la lesión es la agrupación más fina disponible). **543/1503
   imágenes de test (36.1%) comparten lesión con train**, con fuerte sesgo hacia las clases minoritarias
   (MEL 106/167 = 63%, BCC 54/77 = 70%). Efecto medido sin re-entrenar, sobre el subconjunto limpio
   (n=894, lesión ausente de train y val): Swin headline sens. macro 0.870 → 0.804, recall MEL 0.766 → 0.608.
   Control: DermLIP zero-shot (nunca vio HAM) rinde **peor** en las imágenes fugadas (sens. 0.477 vs 0.527),
   así que la ventaja de Swin en ellas (0.936) es atribuible a haber visto la lesión, no a que sean fáciles.
2. **Selección por test en ConvNeXt.** El ganador del sweep v4 (t06) es el mejor en **test**; en validación
   gana t09 (0.874 vs 0.861). Swin t08 sí es el mejor en validación. Los legacy (ViT/DenseNet) se eligieron
   por `best_val_f1` en W&B (verificado: el export solo tiene métricas de validación).
3. **El test se evalúa con los pesos de la última época**, no con `best_model.pt`: nadie recarga el
   checkpoint elegido por `val_f1` (Swin t08: mejor época 35, evaluado en la 40). No es sesgo optimista, pero
   contradice la afirmación "checkpoint seleccionado en validación".

## Diseño experimental

### Split (`scripts/make_lesion_disjoint_split.py` → `data/splits/ham10000_splits_lesion.json`)
- **Test idéntico** (las mismas 1503 imágenes): preserva la comparabilidad con VLMs, DermLIP ZS, generación de
  reportes y ruteo, todo ya evaluado sobre esas imágenes.
- Se descartan de train/val las **776 imágenes** cuya lesión aparece en test.
- El resto se reparte con `StratifiedGroupKFold` (grupos = `lesion_id`, estratos = `dx`, 6 folds, seed 42):
  **train 6447 / val 1289**. Solapamiento de lesiones verificado = 0 en train-test, val-test y train-val.
- Costo: train 8% más chico que el original (7010) → los modelos nuevos quedan, si acaso, en desventaja.

### Correcciones de código
- `train_classifier.py --eval-best-checkpoint`: recarga `best_model.pt` (mejor `val_f1`) antes de evaluar.
- `train_classifier.py --save-val-predictions`: guarda predicciones de validación (mismo protocolo TTA), para
  ajustar umbrales de melanoma y calibración post-hoc **en validación**.
- `submit_sweep.py --lesion-split --class-weights {auto,none,both} --trials --seeds`: los defaults reproducen
  el sweep v4 original.

### Corridas (TOKO)
| Tanda | Qué | Jobs | Selección |
|---|---|---|---|
| A | Swin-Tiny: grid v4 (15 trials) × class weights {auto, none} | 30 | mejor `val_f1` (val agrupada) |
| A | ConvNeXt-Tiny: ídem | 30 | ídem |
| B | Legacy DenseNet121 / ViT-B/16 con sus HPs ya elegidos en val | 2 | — |
| C | Ganador de Swin y de ConvNeXt × semillas {43, 44} (la 42 ya está en A) | 4 | — |
| D | Réplica de `tab:desbalance` (4 pérdidas × Swin/ConvNeXt/DenseNet, mismo diseño) | 12 | — (ablación) |

El grid se duplica con `class_weights=none` porque el Swin "CE simple" del cuadro de desbalance (acc 0.923)
supera al headline (0.868) pero nunca pasó por selección: así la pérdida también se elige en validación.

### Local
- Embeddings DermLIP de las 10015 imágenes (cache) → kNN (k=3), linear-probe (LogReg) y SVM-RBF re-ajustados
  sobre el train disjunto; ruteo de 3 niveles recomputado con Swin nuevo + kNN nuevo.
- Macro-F1 para todas las filas de `tab:clasificacion`.
- Calibración post-hoc (temperature scaling ajustado en val) de los clasificadores nuevos: ECE/MCE/Brier antes
  y después.
- Detección de melanoma con los modelos nuevos (umbral esp≥0.85 fijado en val).
- **Generación de reportes: no se re-genera** (semanas de cola en Mendieta). Se reporta sobre el subconjunto
  limpio del test original, donde el pipeline avanzado sigue siendo significativo (Mini +0.077 [0.058, 0.095];
  LLaVA-Med +0.096 [0.078, 0.117]).

## Criterios de éxito / interpretación

- **Headline válido:** media ± desvío de 3 semillas del ganador en validación, sobre test, sin leakage.
- **Estabilidad entre semillas:** desvío de sens. macro ≤ 0.02 → la conclusión no depende de una
  inicialización. Si es mayor, se reporta igual y se matiza.
- **Conclusiones centrales** (especializado >> VLM general; DermLIP ZS rompe el colapso; el ensamble consciente
  mejora la fidelidad): se sostienen si el orden de los enfoques no cambia con los números nuevos.
- Se espera que la sens. macro de los supervisados **baje** (del orden de lo observado en el subconjunto
  limpio). Eso no es un fracaso del experimento sino la estimación honesta.

## Sincronización con clústeres

- `sync_up.py` de TOKO sube `src/`, `scripts/`, `configs/`, `slurm/` **y `data/splits/`** (lista blanca):
  el split nuevo viaja sin pasos extra. No requiere `--delete` (solo se agregan archivos).
- Los datos procesados de HAM10000 y los pesos torchvision ya están en el scratch de TOKO (se usaron en v4).
  Scratch no persistente: bajar resultados con `sync_down.py` apenas terminen.
- **Validación local:** `py_compile` + `--dry-run --print-script` de `submit_sweep.py` (verificado que el
  modo original genera el mismo comando). El entrenamiento no se prueba localmente: se envía primero **un**
  trial y, si arranca y guarda predicciones de val, el resto.

## Costo estimado

Swin t08 tardó 22 min en TOKO (40 épocas). 66 jobs × ~25–40 min ≈ 30–40 h-GPU, repartidas en la cola corta.
Local: embeddings DermLIP ~10 min en la RTX 4070.
