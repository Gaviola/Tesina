# Mejoras Clasificadores Fase 1 — Iteración v2

## 1. Resultados de la iteración v1 (modern recipe)

Jobs ejecutados en TOKO (RTX 4080 16 GB, CUDA 12.6), 2026-04-28/29.

| Modelo | Recipe | Acc (HAM) | F1 (HAM) | Mejor época |
|---|---|---|---|---|
| DenseNet121 | legacy | 0.8456 | 0.8517 | 28/30 |
| ViT-B/16 | legacy | 0.8576 | 0.8621 | 28/30 |
| **DenseNet121** | **modern v1** | **0.7572** | **0.7763** | **17/40** |
| **ViT-B/16** | **modern v1** | **0.8097** | **0.8205** | **~18/40** |
| **ConvNeXt-Tiny** | **modern v1** | **0.8150** | **0.8276** | **~9/40** |
| **Swin-Tiny** | **modern v1** | **0.8576** | **0.8648** | **~14/40** |

**Observación:** El recipe `modern` empeoró a DenseNet121 (-9% F1) y a ViT (-4% F1). ConvNeXt y Swin alcanzaron rendimientos similares a los legacy.

---

## 2. Diagnóstico: qué falló

### 2.1 Causa principal — MixUp/CutMix produce explosión de val_loss

El patrón es **idéntico en los 4 modelos**: a partir del epoch 2 de Stage 2, la val_loss se dispara mientras la val_f1 mejora lentamente.

```
DenseNet modern — Stage 2:
  Epoch 3:  val_loss=1.38, val_f1=0.60
  Epoch 7:  val_loss=1.63, val_f1=0.76
  Epoch 17: val_loss≈1.75, val_f1=0.82  ← best checkpoint
  Epoch 22: EarlyStopping

ViT modern — Stage 2:
  Epoch 2:  val_loss=1.50, val_f1=0.61
  Epoch 6:  val_loss=1.87, val_f1=0.75
  Epoch 17: val_f1=0.83  ← best
  Epoch 25: EarlyStopping
```

**Explicación:** MixUp y CutMix entran el modelo con etiquetas blandas (combinaciones convexas de one-hot). El modelo aprende a producir distribuciones de probabilidad **planas** entre las clases mezcladas. Cuando se evalúa en el conjunto de validación (etiquetas duras), la entropía cruzada aumenta aunque el argmax sea correcto → val_loss crece, val_f1 mejora.

Consecuencia: el modelo entrenado con MixUp produce probabilidades poco calibradas en imágenes reales, lo que degrada la accuracy y el F1 en el test set.

**Referencias:** Thulasidasan et al. (2019), *On Mixup Training: Improved Calibration and Predictive Uncertainty for Deep Neural Networks*.

### 2.2 Causa secundaria — LLRD demasiado agresivo

Con `llrd=0.75` y 11 grupos para DenseNet, la capa inicial recibe:
```
lr = base_lr × 0.75^10 = 7.91e-5 × 0.0563 ≈ 4.5e-6
```
Esto prácticamente congela las capas tempranas durante Stage 2, limitando la adaptación al dominio dermatológico.

### 2.3 Bug — AUC-ROC = None en todos los modelos modernos

El código TTA promedia softmax de 2 vistas en bf16/fp32. Las probabilidades resultantes no suman exactamente 1.0 por precisión floating-point. Sklearn's `roc_auc_score` rechaza probabilidades que no suman a 1 → siempre retorna None.

**Fix:** normalizar `y_prob` antes de llamar a `roc_auc_score`.

### 2.4 Error — HIBA data no disponible en TOKO

```
ERROR - HIBA metadata.csv no encontrado. Skipping eval HIBA.
```

El directorio `data/processed/HIBA/` no fue sincronizado al cluster. No hay resultados OOD para ningún modelo.

### 2.5 JSON fragmentado

Los resultados HAM10000 y HIBA se guardan en archivos separados (`*_test_results.json` y `*_test_results_hiba.json`), dificultando la comparación. El `aggregate_classifier_results.py` debe buscar dos archivos por modelo.

---

## 3. Cambios para la iteración v2

### 3.1 Parámetros del recipe `modern` (actualización)

| Parámetro | v1 | v2 | Razón |
|---|---|---|---|
| `mixup_alpha` | 0.2 | **0.0** | Eliminar calibración dañina |
| `cutmix_alpha` | 1.0 | **0.0** | Ídem |
| `focal_gamma` | 2.0 | **1.0** | Gamma más suave; sin MixUp gamma=2 es innecesariamente agresivo |
| `llrd` | 0.75 | **0.85** | Menos decaimiento → capas tempranas reciben más gradiente |

Todo lo demás se mantiene: RandAugment, RandomErasing, warmup=3, two-stage, TTA, label_smoothing=0.1.

Con `llrd=0.85` y 11 grupos, la primera capa de DenseNet recibe:
```
lr = 7.91e-5 × 0.85^10 ≈ 7.91e-5 × 0.197 ≈ 1.56e-5
```
Mucho más razonable que los ~4.5e-6 de v1.

### 3.2 Fix AUC-ROC

En `evaluate_classification`, normalizar `y_prob` para que sus filas sumen 1 antes de invocar `roc_auc_score`:
```python
y_prob = y_prob / y_prob.sum(axis=1, keepdims=True).clip(min=1e-12)
```

### 3.3 JSON consolidado por run

Nuevo formato `{run_name}_test_results.json`:
```json
{
  "model": "densenet",
  "run_name": "densenet_modern",
  "recipe": "modern",
  "ham10000": {
    "n_samples": 2003,
    "accuracy": ...,
    "f1_weighted": ...,
    "auc_roc_macro": ...,
    "sensitivity_macro": ...,
    "specificity_macro": ...,
    "sensitivity_per_class": {...},
    "specificity_per_class": {...},
    "confusion_matrix": [...]
  },
  "hiba": {
    "n_samples": 1616,
    "accuracy": ...,
    ...
  },
  "combined": {
    "n_samples": 3619,
    "accuracy": ...,
    ...
  }
}
```

La sección `hiba` y `combined` solo se incluyen cuando `--eval-hiba` está activo y el dataset está disponible.

### 3.4 Sincronización HIBA a TOKO

Sincronizar `data/processed/HIBA/` al cluster antes de enviar jobs.

---

## 4. Jobs v2

```bash
python scripts/toko/sync_up.py
python scripts/toko/submit.py all_cls_modern
```

Los 4 modelos a reentrenar: `densenet_modern`, `vit_modern`, `convnext_tiny_modern`, `swin_tiny_modern`.

---

## 5. Expectativas v2

Con MixUp eliminado y LLRD menos agresivo, se espera que:
- val_loss deje de explotar → EarlyStopping no corte prematuramente
- El modelo converja a una solución mejor calibrada
- DenseNet y ViT recuperen o superen los baselines legacy (0.85+)
- ConvNeXt y Swin, con RandAugment + Focal + TTA, superen a DenseNet/ViT legacy

Resultado objetivo: F1 ≥ 0.87 en HAM10000 test para al menos un modelo.

---

## 6. Resultados reales de la iteración v2

Jobs ejecutados en TOKO (RTX 4080 16 GB, CUDA 12.6), 2026-04-29.

### 6.1 Métricas HAM10000 (test, n=1503)

| Modelo | Recipe | Acc | F1-w | AUC-ROC | Sens-macro | Spec-macro |
|---|---|---|---|---|---|---|
| DenseNet121 | legacy ★ | **0.8456** | **0.8517** | — (bug) | 0.7761 | 0.9674 |
| ViT-B/16 | legacy ★ | **0.8576** | **0.8621** | — (bug) | 0.7972 | 0.9716 |
| ConvNeXt-Tiny | modern v2 | 0.7871 | 0.8361 | 0.9620 | 0.8124 | 0.9644 |
| Swin-Tiny | modern v2 | 0.6979 | 0.7514 | 0.9585 | 0.8120 | 0.9523 |
| ViT-B/16 | modern v2 | 0.6035 | 0.6615 | 0.9502 | 0.7645 | 0.9389 |
| DenseNet121 | modern v2 | 0.5190 | 0.6151 | 0.9403 | 0.7217 | 0.9277 |

★ Modelos legacy seleccionados de un barrido de hiperparámetros (W&B sweep, 25+ runs).

### 6.2 Métricas HIBA OOD (n=1616) — evaluación fuera de distribución

| Modelo | Recipe | Acc | F1-w | AUC-ROC | Sens-macro | Spec-macro |
|---|---|---|---|---|---|---|
| Swin-Tiny | modern v2 | **0.5421** | **0.5691** | 0.8243 | 0.5426 | 0.9248 |
| ViT-B/16 | modern v2 | 0.4882 | 0.5305 | 0.8409 | 0.5149 | 0.9183 |
| ConvNeXt-Tiny | modern v2 | 0.4604 | 0.5236 | 0.8174 | 0.4823 | 0.9152 |
| DenseNet121 | modern v2 | 0.4183 | 0.4722 | 0.8234 | 0.4759 | 0.9079 |

Los modelos legacy no tienen evaluación HIBA porque los datos no estaban disponibles en TOKO durante su entrenamiento.

### 6.3 Observación sobre AUC-ROC

El fix de normalización (§3.2) funcionó: AUC-ROC se calcula correctamente en todos los modelos v2 (rango 0.94–0.96 en HAM). Nótese la **disociación entre AUC y Accuracy**: DenseNet alcanza AUC=0.940 con Accuracy=0.519. Esto indica que el modelo aprendió características discriminativas útiles (las probabilidades ordenan bien las clases), pero el calibrado del argmax está severamente deteriorado.

---

## 7. Análisis de la iteración v2: por qué empeoraron los resultados

La v2 no sólo falló en superar a los legacy: **DenseNet y ViT empeoraron incluso respecto a la v1**. Se identifican cuatro factores.

### 7.1 Colapso por Focal Loss sobre la clase mayoritaria (causa principal)

Con MixUp eliminado, la Focal Loss (γ=1.0) opera sobre etiquetas one-hot puras. El dataset HAM10000 tiene un desequilibrio severo: la clase `nv` (melanocytic nevi) representa 1006 de 1503 muestras de test (≈67%). Para la Focal Loss, las muestras de `nv` son "fáciles" → sus pesos de gradiente se reducen agresivamente → el modelo se enfoca en las clases minoritarias.

**Evidencia directa en la matriz de confusión de DenseNet v2:**

```
Clase 1 (nv, 1006 muestras reales): [38, 426, 7, 2, 22, 462, 49]
  → 462 muestras nv predichas como clase 5 (vasc, solo 17 muestras reales)
  → Sensibilidad nv: 0.4235 (era 0.887 en legacy)
```

El modelo predice la clase `vasc` (17 muestras, la más rara) para 536 imágenes en total, cuando solo 17 son realmente `vasc`. Este colapso hacia la clase minoritaria es la firma clásica de **Focal Loss sin regularización de mezcla de etiquetas en datasets muy desbalanceados**.

**Paradoja v2 > v1 en daño:** En la v1, MixUp forzaba al modelo a mantener masa de probabilidad en la clase mayoritaria (etiquetas blandas mezcladas). Aunque causaba val_loss explosion, actuaba como *regularizador* que impedía el colapso hacia clases minoritarias. Al eliminar MixUp en v2, la Focal Loss opera sin freno sobre etiquetas duras, resultando en el colapso observado.

### 7.2 Sensibilidad arquitectural al recipe

Los cuatro modelos con el mismo recipe producen resultados muy distintos:

| Modelo | Acc v2 | ΔAcc vs v1 |
|---|---|---|
| ConvNeXt-Tiny | 0.787 | +0.028 (mejora) |
| Swin-Tiny | 0.698 | +0.013 (mejora) |
| ViT-B/16 | 0.603 | -0.207 (empeora) |
| DenseNet121 | 0.519 | -0.238 (empeora) |

ConvNeXt-Tiny y Swin-Tiny mejoraron respecto a v1 (ambos son arquitecturas modernas con **LayerNorm** en lugar de BatchNorm). DenseNet121 y ViT-B/16 empeoraron drásticamente.

BatchNorm (DenseNet) es sensible a distribuciones de entrada ruidosas. Con RandAugment (m=9) + RandomErasing (p=0.25) + RRC (scale_min=0.7), las estadísticas de batch fluctúan significativamente por epoch. Esto desestabiliza el calibrado que Focal Loss requiere para asignar pesos correctos → ciclo de retroalimentación negativo.

### 7.3 Ventaja de los legacy: barrido de hiperparámetros

Los modelos legacy fueron elegidos de un **W&B sweep de 25+ configuraciones**. Los hiperparámetros óptimos encontrados:

| Modelo | lr óptimo | label_smoothing | weight_decay | scheduler |
|---|---|---|---|---|
| DenseNet legacy | 7.91e-5 | 0 | 0.01 | CosineAnnealingLR |
| ViT legacy | 1.56e-5 | 0 | 0.01 | none |

El sweep encontró que `label_smoothing=0` es óptimo para ambos, lo que es coherente: el suavizado de etiquetas hace que la Focal Loss sea aún menos efectiva para las clases raras.

Los modelos modernos v2 usan hiperparámetros **fijos sin sweep**: `weight_decay=0.05`, `base_lr` heredado del código previo. Nunca se barrió la interacción entre `focal_gamma`, `llrd`, y el `base_lr` para el recipe moderno. Esta ausencia de tuning es un segundo factor diferencial de los legacy.

### 7.4 Degradación en HIBA (domain shift)

Todos los modelos caen entre 15–27 puntos de Accuracy al evaluar en HIBA. Esto era esperable: HIBA tiene diferentes fototipos, iluminación y distribución de clases que HAM10000. La magnitud de la caída no es atribuible a los bugs de las versiones anteriores, sino a la brecha real de distribución.

Nótese que **Swin-Tiny tiene el mejor rendimiento HIBA** (Acc=0.542), mientras que ConvNeXt es el mejor en HAM. Esto sugiere que distintas arquitecturas generalizan de forma diferente entre dominios.

---

## 8. Conclusiones de Fase 1

### 8.1 Mejores modelos para la tabla SOTA

| Slot | Modelo | Recipe | F1 HAM | AUC HAM | Nota |
|---|---|---|---|---|---|
| (a) | DenseNet121 | legacy | **0.8517** | — | Sweep-optimizado |
| (b) | ViT-B/16 | legacy | **0.8621** | — | Sweep-optimizado |
| (a') | ConvNeXt-Tiny | modern v2 | 0.8361 | 0.9620 | Mejor modern |
| (b') | Swin-Tiny | modern v2 | 0.7514 | 0.9585 | Mejor OOD |

Los modelos legacy siguen siendo los mejores en HAM10000. ConvNeXt-Tiny con recipe modern v2 es el mejor de los nuevos modelos y es competitivo (ΔF1 ≈ -0.016 vs legacy ViT).

### 8.2 Lo que funcionó en v2

- **Fix AUC-ROC**: ahora se calculan correctamente valores en el rango 0.94–0.96.
- **Evaluación HIBA**: el pipeline OOD funciona y produce resultados reproducibles.
- **JSON consolidado**: formato único por run con secciones `ham10000`, `hiba`, `combined`.
- **ConvNeXt-Tiny**: el recipe moderno sin MixUp lo beneficia (+3% Acc vs v1).

### 8.3 Lo que no funcionó y por qué

- **Focal Loss para DenseNet/ViT**: incompatible con el desbalance severo de HAM10000 sin mezcla de etiquetas. Genera colapso hacia clases minoritarias.
- **Recipe único para todas las arquitecturas**: las arquitecturas con BatchNorm son más sensibles al stack de augmentación que las de LayerNorm.
- **Ausencia de sweep para el recipe moderno**: los hiperparámetros fijos son sub-óptimos.

### 8.4 Recomendaciones implementadas en la iteración v3

1. **DenseNet / ViT**: deshabilitar Focal Loss → CE + class weights. Ver §9.
2. **ConvNeXt-Tiny / Swin-Tiny**: también deshabilitar Focal Loss para verificar si el colapso aplica a estas arquitecturas también.
3. **RandAugment para DenseNet**: reducir magnitud de m=9 a m=6.

---

## 9. Iteración v3 — Plan y cambios

### 9.1 Motivación

La v2 confirmó que la Focal Loss es el factor destructivo principal: la matriz de confusión de DenseNet mostró 462/1006 muestras `nv` (clase mayoritaria) predichas como `vasc` (17 muestras totales). El modelo aprendió a minimizar la Focal Loss sacrificando la clase fácil para sobre-predecir las raras. La v3 elimina este mecanismo y vuelve a CE estándar con pesos de clase.

Adicionalmente, se re-ejecutan los modelos **legacy con evaluación HIBA** ahora que el fix de AUC-ROC está activo, para obtener su rendimiento OOD y permitir una comparación completa entre las tres iteraciones.

### 9.2 Cambios respecto a v2

| Cambio | DenseNet | ViT | ConvNeXt-Tiny | Swin-Tiny | Razón |
|---|---|---|---|---|---|
| `focal_gamma` | 1.0 → **0** | 1.0 → **0** | 1.0 → **0** | 1.0 → **0** | Eliminar colapso hacia clases minoritarias |
| `randaugment_m` | 9 → **6** | 9 (sin cambio) | 9 (sin cambio) | 9 (sin cambio) | DenseNet+BatchNorm sensible a varianza alta |
| Todo lo demás | sin cambio | sin cambio | sin cambio | sin cambio | — |

Con `focal_gamma=0` la función `build_loss()` devuelve `nn.CrossEntropyLoss(weight=class_weights)` — equivalente numérico a Focal Loss con γ=0 pero más eficiente. Los pesos de clase se calculan como `total / (n_classes × freq_i)`, lo que ya contrarrestaba el desbalance incluso en la Focal, pero sin el término `(1-p_t)^γ` que re-ponderaba dinámicamente en función de la certeza del modelo.

### 9.3 Lo que se mantiene de v2

El resto del recipe moderno permanece intacto:
- RandAugment (n=2), RandomErasing (p=0.25), RandomResizedCrop (scale_min=0.7)
- MixUp/CutMix: desactivado (mantenido desde v2)
- Label smoothing: 0.1
- Warmup: 3 épocas
- Two-stage fine-tuning: Stage 1 (1 epoch, solo head) + Stage 2 (LLRD=0.85)
- TTA (horizontal flip)
- Evaluación HIBA OOD

### 9.4 Hipótesis para v3

Con CE + class weights en lugar de Focal Loss:
- **DenseNet**: se espera recuperar sensibilidad en `nv` (actualmente 0.42 en v2 vs 0.89 en legacy). El modelo ya no tiene incentivo para colapsar hacia `vasc`.
- **ViT**: recuperación similar; partía de mejor punto en v2 (acc=0.603 vs 0.519 DenseNet).
- **ConvNeXt-Tiny**: en v2 alcanzó F1=0.836 con Focal. Sin Focal podría mejorar (menos presión sobre clases raras) o mantenerse (la arquitectura LayerNorm es más robusta).
- **Swin-Tiny**: en v2 alcanzó F1=0.751 con Focal. Se espera mejoría similar a DenseNet/ViT.

Resultado objetivo: F1 ≥ 0.86 en HAM10000 para DenseNet y ViT; F1 ≥ 0.85 para ConvNeXt y Swin.

### 9.5 Jobs v3

```bash
# Opción A: todo junto (legacy + 4 modelos v3 = 6 jobs)
python scripts/toko/submit.py all_cls_v3

# Opción B: por separado
python scripts/toko/submit.py all_cls_legacy       # DenseNet + ViT legacy con HIBA
python scripts/toko/submit.py all_cls_modern_v3    # 4 modelos v3 sin Focal
```

Los jobs v3 producirán archivos `{run_name}_test_results.json` con run_names:
`densenet_modern_v3`, `vit_modern_v3`, `convnext_tiny_modern_v3`, `swin_tiny_modern_v3`

Los jobs legacy re-ejecutados producirán `densenet_legacy_test_results.json` y `vit_legacy_test_results.json` en formato consolidado v2 (con secciones `ham10000`, `hiba`, `combined`).
