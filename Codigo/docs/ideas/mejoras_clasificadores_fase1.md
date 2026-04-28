# Mejoras a clasificadores de Fase 1 (DenseNet121 / ViT-B/16) hacia el SOTA

**Estado:** Propuesta — Fase 0 (planificación)
**Autor:** Plan elaborado en sesión interactiva (grill mode)
**Fecha:** 2026-04-27
**Modelos afectados:** DenseNet121, ViT-B/16, ConvNeXt-Tiny (nuevo), Swin-Tiny (nuevo)
**Datasets:** HAM10000 (train/val/test) + HIBA (test OOD)

---

## 1. Contexto y objetivo

### 1.1 Resultados actuales (baseline)

Modelos entrenados sobre HAM10000 (split estándar, test = ISIC 2018 Task 3 Test Set, 1511 imágenes):

| Modelo | Accuracy | F1 weighted | Sens. macro | Spec. macro |
|---|---|---|---|---|
| DenseNet121 | 0.8456 | 0.8517 | 0.7761 | 0.9674 |
| ViT-B/16 | 0.8576 | 0.8621 | 0.7972 | 0.9716 |

Clases con sensibilidad débil:
- **DF (dermatofibroma)**: 53 % DenseNet, 65 % ViT — clase minoritaria, peor recall.
- **MEL (melanoma)**: 68-74 % — clínicamente la más relevante; subóptima.
- **BKL**: 75-76 %.

### 1.2 Comparación con SOTA

La tabla `Codigo/docs/resul/tablas_estado_del_arte_v2.tex` reporta accuracy en HAM10000 entre 70 % y 95.63 %. Tres trabajos exhiben los mejores números:

| Trabajo | Acc. reportada | Tarea real | ¿Comparable? |
|---|---|---|---|
| SkinHealthMate (Aboulmira 2024) | 93 % | HAM10000, **7-clase** | **Sí (directa)** |
| Ensemble DL + LLM (Khan/Chakrabarti 2025) | 97.67 % | ISIC, **2-clase (BCC vs NV)** | **No** (binario) |
| MPXV-CNN (Thieme 2023) | AUC 0.966 | mpox vs no-mpox **2-clase** | **No** (binario, mpox) |

El gap real frente a un SOTA comparable es **~7-8 puntos** (85 % → 93 %), no 12-13. Las cifras superiores al 95 % corresponden a tareas binarias y no son fair comparison.

### 1.3 Objetivo

Acortar el gap a SkinHealthMate y aprovechar lecciones de los tres papers, **manteniendo single-model** (sin ensemble formal) y conservando las arquitecturas clásicas DenseNet121 + ViT-B/16 como pilares de la narrativa de la tesina (clásico CNN/ViT vs VLM). Se incorporan dos modelos modernos (ConvNeXt-Tiny + Swin-Tiny) como contrapartes de cada familia para enriquecer la comparación.

**Meta cuantitativa**: Accuracy ≥ 0.90 y F1-weighted ≥ 0.90 en al menos uno de los modelos modernos; mejora ≥ +3 puntos absolutos en DenseNet121 y ViT-B/16 frente al baseline.

---

## 2. Estado actual del pipeline de entrenamiento

Resumen del setup vigente (`Codigo/scripts/train_classifier.py`, `Codigo/configs/`):

| Componente | Valor actual |
|---|---|
| Backbone | DenseNet121 (torchvision, ImageNet1K_V1) o ViT-B/16 (torchvision, ImageNet1K_V1) |
| Resolución entrada | 224 × 224 |
| Augmentations train | `Resize(224)` + `RandomRotation(30)` + `RandomHorizontalFlip(0.5)` + `ColorJitter(0.2, 0.2, 0.2, 0.1)` + `Normalize(ImageNet)` |
| Augmentations val/test | `Resize(224)` + `Normalize` (sin flips, sin TTA) |
| Optimizer | AdamW (lr=7.91e-5 DenseNet / 1.56e-5 ViT, weight_decay=0.01) |
| Scheduler | CosineAnnealingLR (DenseNet) / sin scheduler (ViT) |
| Loss | `CrossEntropyLoss` con `class_weights=auto` (inverso de frecuencia, normalizado) |
| Label smoothing | 0.0 |
| Mixup / CutMix | No |
| Epochs | 30 |
| Early stopping | patience=5 sobre `val_f1` |
| Dropout en head | 0.3 |
| Backbone freeze | Configurable; default actual `freeze_backbone=False` (full fine-tuning) |
| TTA en evaluación | No |
| Stochastic Weight Averaging | No |
| Dataset entrenamiento | HAM10000 únicamente |
| Test set | HAM10000 (ISIC 2018 Task 3 Test, 1511 imgs) |
| HIBA | Disponible pero **no integrado** en pipeline de clasificación |
| Reproducibilidad | `set_seed(42)`, splits JSON fijo |

---

## 3. Análisis de los tres papers SOTA

### 3.1 SkinHealthMate (Aboulmira et al., 2024) — 93 % en HAM10000 7-clase

**Arquitectura.** Ensemble por promedio de softmax de **EfficientNetB1 + EfficientNetB5**. Cada modelo tiene head: GlobalAvgPool → Dense → Dropout → Softmax.

**Pretraining.** Pesos *Noisy Student* (no ImageNet vanilla) — escala más grande y self-training.

**Fine-tuning gradual.** Estrategia de tres etapas:
1. Congelar backbone, entrenar solo head con lr alta.
2. Unfreeze de las **últimas 20 capas** (excluyendo BatchNorm), continuar con lr menor.
3. Unfreeze gradual de capas más profundas con lr aún más baja.

**Augmentations** (en el orden reportado):
- Rotación hasta **90°** (mayor que nuestros 30°).
- Shear hasta **20°**.
- Scaling **[0.8, 1.2]**.
- **Random crop** para variar la posición del centro de la lesión.
- Hue shift en **[-0.1, 0.1]**.
- **Cutout** (parches aleatorios enmascarados — simula oclusión por pelo o artefactos).
- H/V flip aleatorio.

**Preprocessing.** **Filtro mediano** para reducir ruido sal-y-pimienta (preserva bordes mejor que Gaussiano/Wiener) + normalización (X−μ)/σ.

**Optimización.** Adam, lr=1e-4, categorical cross-entropy estándar (sin pesos por clase, sin focal), early stopping sobre val_loss.

**Resultados.** Acc 93 %, F1-macro 0.81, F1-weighted 0.93. AUC ROC: NV 0.97, BCC 1.00, MEL 0.92. F1 por clase: NV 0.98, MEL 0.55 (muy baja), AKIEC 0.67, BCC 0.84, BKL 0.76, DF 0.91 (sólo 6 muestras test), VASC 0.96.

### 3.2 Ensemble DL + LLM (Khan/Chakrabarti et al., 2025) — 97.67 % BINARIO

**Tarea.** Clasificación binaria BCC vs NV (3000 + 3000 imgs). **No HAM10000 7-clase.**

**Arquitectura.** Ensemble heterogéneo de tres CNN: **EfficientNetB3 + ResNet50 + DenseNet121**, fusión por **majority voting**. Si el voto no es unánime → flag automático para revisión por dermatólogo (mecanismo de uncertainty).

**Pretraining.** ImageNet. Congelan el 70 % inferior de las capas convolucionales; fine-tuning del 30 % superior + head.

**Augmentations.** Rotación ±30°, flip h/v, zoom [0.8, 1.2], brillo ±20 %, probabilidad 50 % por transform (Keras `ImageDataGenerator`).

**Preprocessing.** **Non-Local Means denoising** + **histogram equalization** + resize 224×224.

**Optimización.** Adam (β1=0.9, β2=0.999), lr=1e-4, batch 32, 40 epochs, dropout 0.5 en head, early stopping patience=5, categorical cross-entropy.

**Resultados.** Ensemble: 97.67 % acc, F1=0.976, recall malignos=0.99 (sólo 3/300 BCC perdidos). Modelos individuales: ResNet50 93.83 %, EfficientNetB3 92.33 %, DenseNet121 92.00 %.

**Componente LLM.** LLaMA-3 70B vía Groq API para generar reportes clínicos a partir de la predicción. Irrelevante para la clasificación misma.

### 3.3 MPXV-CNN (Thieme et al., 2023) — Sens 0.91 / Spec 0.898 / AUC 0.966 BINARIO

**Tarea.** Binaria mpox vs no-mpox sobre 139 198 imágenes (676 mpox + 138 522 no-mpox de ocho repositorios). **Class imbalance extremo (≈1:200)**.

**Arquitectura.** Single model **ResNet34** (FastAI v2). Probaron también ResNet18, ResNet50, ResNet152, DenseNet169, VGG19_bn — ResNet34 ganó.

**Pretraining.** ImageNet (≈14 M imgs).

**Augmentations agresivas.** Pre-resize a **448×448**, luego **random crop & resize a 224×224** (equivale a zoom/translation aleatorio fuerte). Adicional: random h-flip, rotación hasta **360°**, zoom hasta 1.1×, **perspective warping**, brightness/contrast aleatorio, transformaciones afines aleatorias. Este pre-resize + random crop es la técnica más fuerte de los tres papers.

**Pérdida con búsqueda de pesos por clase.** Categorical cross-entropy ponderada. Realizaron **grid search sobre pesos**: probaron pares W ∈ {(1.0, 0.005), (1.0, 0.01), (1.0, 0.05), (1.0, 0.1), (1.0, 0.5), (1.0, 1.0)}. Eligieron el W que maximizaba val class-weighted accuracy.

**Two-stage fine-tune.** Una época entrenando sólo última capa, luego 20 épocas con todo desbloqueado. Batch 64, base lr 0.002.

**Validación.** 5-fold CV estratificada, 5 repeats (variancia robusta). Métrica final = media de 25 folds.

**Explainability.** SHAP values sobre imágenes de test → mapas de calor superpuestos para verificar focalización en la lesión.

**Resultados.** Validación: sens 0.83, spec 0.965, AUC 0.967. Test externo: sens 0.91, spec 0.898, AUC 0.966. Cohorte prospectiva Stanford: sens 0.89.

---

## 4. Técnicas a implementar

Decisión basada en gap real (~8 pts), enfoque single-model y compute disponible (~12 jobs SLURM).

### 4.1 Adoptadas

| # | Técnica | Inspiración | Justificación | Costo impl. |
|---|---|---|---|---|
| T1 | **Label smoothing** ε=0.1 | Práctica moderna estándar | Regulariza, mejora calibración, ayuda en clases minoritarias. Trivial. | Bajo (1 línea) |
| T2 | **RandAugment** (n=2, m=9) | Generaliza el enfoque de SkinHealthMate (rot 90°, shear, hue, cutout) | Reemplaza nuestro `RandomRotation(30) + ColorJitter` por una política más fuerte y diversa. | Bajo (5 líneas) |
| T3 | **Random Erasing** (p=0.25) | Cutout de SkinHealthMate | Simula oclusión por pelo/artefactos clínicos comunes en HAM10000. | Bajo (built-in torchvision) |
| T4 | **Pre-resize + RandomResizedCrop** | MPXV-CNN (Thieme): 448 → 224 | El crop aleatorio variando posición/escala es augmentación fuerte sin costo de inferencia. Reemplaza `Resize(224)` plano. | Bajo |
| T5 | **MixUp + CutMix** (α=0.2 / 1.0, alternados con p=0.5) | No está en los tres papers; práctica moderna estándar HAM10000 | Regularización fuerte, +1-2 pt típico en HAM10000-like. Mitiga sobreajuste a NV (clase mayoritaria). | Medio (collator + loss adaptado) |
| T6 | **Focal Loss** (γ=2.0) | Alternativa al class-weighting de Thieme | Ataca directo el peor caso DF (53 % sens). Re-pondera ejemplos difíciles, complementario al class weighting. | Medio (clase loss nueva) |
| T7 | **Warmup lineal** (3 ep) + cosine decay | Práctica estándar para Transformers (ViT, Swin) | Estabiliza inicio, especialmente crítico en ViT/Swin con lr bajo. | Bajo (scheduler combinado) |
| T8 | **TTA en evaluación** (h-flip + 5-crop, promediado) | No está explícito en los tres papers, pero es práctica estándar | Gain "gratis" en inference (0.5-1.5 pt). Compatible con HIBA OOD eval. | Medio (función eval nueva) |
| T9 | **Two-stage fine-tune** (head 1 ep → unfreeze + LLRD) | MPXV-CNN (Thieme) y SkinHealthMate (gradual) | Mejora estabilidad de fine-tuning. LLRD = layer-wise lr decay (factor 0.75) — útil para ConvNeXt/Swin/ViT. | Medio |
| T10 | **Backbones modernos** ConvNeXt-Tiny + Swin-Tiny | No SOTA dermatología pero referencia visión moderna | ConvNeXt = sucesor natural CNN clásica; Swin = sucesor natural ViT. Mismo paradigma, recipe moderno. Techo +2-5 pt vs DenseNet/ViT. | Medio (nuevas clases en factory + YAMLs) |
| T11 | **HIBA como test OOD** | Coherente con propósito original HIBA (sesgo fototipo) | Mide generalización fuera de HAM10000. Mapping HIBA→7-clase es 1:1 (1616/1616 muestras mapean). | Medio (script eval cross-dataset) |

### 4.2 Descartadas (con justificación)

| # | Técnica | Origen | Razón de descarte |
|---|---|---|---|
| D1 | Ensemble multi-modelo (avg softmax / majority vote) | SkinHealthMate, Khan/Chakrabarti | Fuera de scope. Tesina compara arquitecturas individuales; un ensemble cambiaría la unidad de comparación. Posible adición futura, no en este sprint. |
| D2 | Filtro mediano preprocesado | SkinHealthMate | Gain marginal en HAM10000 (las imágenes ya son dermatoscópicas limpias, no clínicas con sal-y-pimienta). Costo I/O extra. |
| D3 | Non-Local Means denoising + histogram equalization | Khan/Chakrabarti | NLM es costoso CPU. Histogram equalization puede destruir información cromática diagnóstica (color es feature en MEL/BCC). Rechazo por riesgo > gain esperado. |
| D4 | Pesos *Noisy Student* | SkinHealthMate | Requiere descarga de checkpoint específico; rompe la línea base "ImageNet pretrained" que la tabla SOTA documenta. Posible ablación futura. |
| D5 | 5-fold CV con 5 repeats | MPXV-CNN | 25× compute. Inviable para tesina con cuatro modelos. Reportamos un solo split fijo (estándar HAM10000) con seed determinista. |
| D6 | Mecanismo "flag para revisión humana" | Khan/Chakrabarti | Sentido clínico, no aplicable a tesina (no hay loop con dermatólogo en el experimento). |
| D7 | Stochastic Weight Averaging (SWA) | Práctica moderna | Postergado; gain marginal (~0.3-1 pt) y aumenta complejidad de la pipeline. Si T1-T10 no alcanzan la meta, considerar en una segunda iteración. |
| D8 | Resolución mayor (288 / 384) | Práctica moderna | Aumenta VRAM significativamente para Swin/ViT. Postergado; primero validar gain con 224 y los demás cambios. |
| D9 | Oversampling con `WeightedRandomSampler` | Alternativa al class weighting | Redundante con Focal Loss + class weights. Riesgo de duplicar el efecto y desestabilizar entrenamiento. |
| D10 | Búsqueda manual de pesos por clase (grid de Thieme) | MPXV-CNN | Diseñado para imbalance extremo binario (1:200). Nuestro caso es 7-clase con imbalance moderado; el inverse-frequency automático cubre el caso. |

### 4.3 Resumen del nuevo recipe ("modern")

```yaml
recipe: modern
data:
  train_transforms:
    - RandomResizedCrop(224, scale=(0.7, 1.0))
    - RandomHorizontalFlip(0.5)
    - RandAugment(n=2, m=9)
    - ToTensor + Normalize(ImageNet)
    - RandomErasing(p=0.25)
  val_transforms: Resize(256) + CenterCrop(224) + Normalize
training:
  optimizer: AdamW
  lr: <model-specific>  # mantener sweep previo como base
  weight_decay: 0.05    # subir levemente con augs más fuertes
  scheduler: warmup_cosine (warmup_epochs=3)
  loss: FocalLoss(gamma=2.0, weight=auto, label_smoothing=0.1)
  mixup: alpha=0.2
  cutmix: alpha=1.0
  mixup_prob: 0.5       # alterna mixup/cutmix
  freeze_strategy: two_stage  # head 1 ep → full + LLRD(0.75)
  epochs: 40            # subimos de 30 por la regularización extra
evaluation:
  tta: hflip+5crop      # solo en test/HIBA
```

---

## 5. Backward compatibility — diseño de flags

Toda corrida sin flags nuevas reproduce el comportamiento actual bit-a-bit.

**Flag principal:**
```bash
--recipe {legacy,modern}   # default: legacy
```

**Flags individuales** (override del recipe; aplicables a cualquiera):
```bash
--label-smoothing FLOAT
--randaugment / --no-randaugment
--random-erasing FLOAT       # probabilidad, 0 = off
--mixup-alpha FLOAT          # 0 = off
--cutmix-alpha FLOAT         # 0 = off
--focal-gamma FLOAT          # 0 = CE estándar
--warmup-epochs INT
--two-stage / --no-two-stage
--llrd FLOAT                 # layer-wise lr decay, 1.0 = off
--tta / --no-tta
--eval-hiba                  # añade evaluación cross-dataset
```

**Defaults por recipe:**

| Flag | legacy | modern |
|---|---|---|
| label_smoothing | 0.0 | 0.1 |
| randaugment | off | on (n=2, m=9) |
| random_erasing | 0.0 | 0.25 |
| mixup_alpha | 0.0 | 0.2 |
| cutmix_alpha | 0.0 | 1.0 |
| focal_gamma | 0.0 | 2.0 |
| warmup_epochs | 0 | 3 |
| two_stage | off | on |
| llrd | 1.0 | 0.75 |
| tta | off | on |
| epochs | 30 | 40 |

Las ablaciones se loguean a wandb con el campo `recipe` + flags individuales para trazabilidad.

---

## 6. Plan de ejecución por fases

| Fase | Estado | Entregable | Validación | Modelos afectados |
|---|---|---|---|---|
| **0** | ✓ Completada | Este documento | Revisado por usuario | — |
| **1** | ✓ Completada | Recipe infra (`--recipe` + flags) + label smoothing + warmup | `--recipe legacy` reproduce 84.6 % DenseNet ± 0.5 pt | DenseNet121, ViT-B/16 |
| **2** | ✓ Completada | RandAugment + Random Erasing + RandomResizedCrop + Focal Loss + MixUp/CutMix | `--recipe modern` mejora ≥ +2 pt sobre legacy | DenseNet121, ViT-B/16 |
| **3** | ✓ Completada | TTA + Two-stage + LLRD + script eval HIBA OOD | TTA aporta gain; HIBA eval reporta métricas separadas | DenseNet121, ViT-B/16 |
| **4** | ✓ Completada | Factory ext: ConvNeXt-Tiny + Swin-Tiny + YAMLs + SLURM genérico + 12 entradas en submit.py | Smoke tests pasados; 12 jobs SLURM listos | Todos |
| **5** | ✓ Completada | Tabla SOTA actualizada con filas (a$'$)(b$'$) + script `aggregate_classifier_results.py` | Aggregator emite Markdown + filas LaTeX desde JSON | — |

**Nota de reorganización:** Two-stage finetune + LLRD (T9) se movió de Fase 2 a Fase 3 para agrupar mejor con TTA (ambos son tweaks de procedure de entrenamiento/evaluación). Esto no afecta el contenido del recipe `modern`, sólo el orden de implementación.

Cada fase produce un commit reviewable. El usuario puede cortar en cualquier fase si el tiempo aprieta.

### 6.1 Lista concreta de jobs SLURM

| # | Modelo | Recipe | Flags adicionales | Propósito |
|---|---|---|---|---|
| 1 | densenet | legacy | — | Verificación de no-regresión (debe dar 84.6 %) |
| 2 | densenet | modern | — | Resultado final DenseNet121 |
| 3 | vit | legacy | — | Verificación de no-regresión (debe dar 85.8 %) |
| 4 | vit | modern | — | Resultado final ViT-B/16 |
| 5 | convnext_tiny | modern | — | Resultado final ConvNeXt-Tiny |
| 6 | swin_tiny | modern | — | Resultado final Swin-Tiny |
| 7 | <mejor> | modern | `--no-mixup --cutmix-alpha 0` | Ablación: efecto de MixUp/CutMix |
| 8 | <mejor> | modern | `--no-randaugment` | Ablación: efecto de RandAugment |
| 9 | <mejor> | modern | `--focal-gamma 0` | Ablación: Focal vs CE+class_weights |
| 10 | <mejor> | modern | `--no-tta` | Ablación: efecto de TTA |
| 11 | <mejor> | modern | `--no-two-stage` | Ablación: efecto del two-stage finetune |
| 12 | <mejor> | modern | `--label-smoothing 0` | Ablación: efecto de label smoothing |

`<mejor>` = el modelo con mejor resultado en jobs 2/4/5/6.

---

## 7. Métricas objetivo y criterios de éxito

**Métrica principal:** Accuracy y F1-weighted sobre HAM10000 test set (ISIC 2018 Task 3 Test, 1511 imágenes).

**Métricas secundarias:**
- Sensibilidad / especificidad por clase (con foco en MEL y DF).
- AUC-ROC macro (actualmente `null` en results, hay que arreglarlo en `evaluate_classification`).
- Métricas en HIBA (1616 imgs) para evaluar generalización OOD.

**Criterios de éxito:**

| Criterio | Mínimo aceptable | Meta |
|---|---|---|
| Accuracy DenseNet121 (modern) | ≥ 0.87 | ≥ 0.89 |
| Accuracy ViT-B/16 (modern) | ≥ 0.88 | ≥ 0.90 |
| Accuracy ConvNeXt-Tiny / Swin-Tiny (mejor) | ≥ 0.90 | ≥ 0.92 |
| F1-weighted del mejor modelo | ≥ 0.90 | ≥ 0.92 |
| Sens. MEL del mejor modelo | ≥ 0.78 | ≥ 0.82 |
| Sens. DF del mejor modelo | ≥ 0.65 | ≥ 0.75 |
| Recipe legacy reproduce baseline ± 0.5 pt | obligatorio | — |

---

## 8. Riesgos y limitaciones

| Riesgo | Mitigación |
|---|---|
| MixUp/CutMix puede degradar clases minoritarias muy escasas (DF=115 train) | Ablación 7 lo aísla; si degrada, alternar con menor probabilidad o descartar |
| TTA puede no aportar si las flips horizontales son ya insensibles para lesiones simétricas | Ablación 10 lo aísla |
| Two-stage + LLRD puede colapsar gradientes si lr base es muy alta | Empezar con lr base = 0.5× lr legacy y ajustar |
| ConvNeXt-Tiny / Swin-Tiny disponibilidad de pesos en torchvision (versión instalada) | Verificar en Fase 4 antes de SLURM |
| Mapping HIBA → 7-clase introduce ruido en SCC→AKIEC (158 imgs afectadas) | Reportar como limitación en doc final; en HIBA test eval, opcional separar SCC |
| Tabla SOTA queda con dataset distinto entre filas si HIBA solo es test | Cambiar columna a "HAM10000 (train) / HAM+HIBA (eval)" o agregar nota al pie |
| Incremento de tiempo de entreno (40 ep vs 30 + augs más caras) | Estimación: +30 % wall-clock; cabe holgado en presupuesto |

---

## 9. Correspondencia técnica → paper de origen

| Técnica adoptada | Paper de origen / inspiración |
|---|---|
| RandAugment / Random Erasing / RandomResizedCrop | SkinHealthMate (rot 90°, shear, hue, cutout) + MPXV-CNN (pre-resize + crop) |
| Two-stage fine-tune + LLRD | MPXV-CNN (head 1 ep → full 20 ep) + SkinHealthMate (gradual unfreeze) |
| Focal Loss | Generalización del grid-search de pesos en MPXV-CNN |
| Label smoothing, MixUp, CutMix, warmup, TTA | Práctica moderna estándar (no son del SOTA dermatológico revisado) |
| ConvNeXt-Tiny / Swin-Tiny | Sucesores arquitectónicos modernos de DenseNet / ViT (no derma-específico) |
| HIBA OOD eval | Coherente con propósito original del dataset (sesgo fototipo) |

---

## 10. Próximos pasos

Implementación completa. Pendiente de ejecución por el usuario:

1. **Verificación legacy (Mendieta):** `python scripts/mendieta/submit.py all_cls_legacy` — debe reproducir DenseNet 84.6 % y ViT 85.8 % ± 0.5 pt.
2. **Corridas finales modern (Mendieta):** `python scripts/mendieta/submit.py all_cls_modern` — 4 jobs (DenseNet, ViT, ConvNeXt-Tiny, Swin-Tiny) con recipe modern + HIBA eval.
3. **Identificar ganador** entre los 4 modern. Editar `_ABL_MODEL` en `scripts/mendieta/submit.py` y `scripts/toko/submit.py` con el modelo ganador.
4. **Ablaciones:** `python scripts/mendieta/submit.py all_cls_ablation` — 6 jobs sobre el modelo ganador para aislar contribución de cada técnica.
5. **Agregar resultados:** `python scripts/aggregate_classifier_results.py > docs/resul/resumen_fase1.md` y pegar las filas LaTeX en la tabla SOTA.
6. **(Opcional)** Pre-descargar pesos torchvision en cluster antes de correr ConvNeXt/Swin (los nodos compute están offline):

   ```bash
   # En el nodo de submit (con internet), correr:
   python -c "import torchvision.models as M; M.convnext_tiny(weights='IMAGENET1K_V1'); M.swin_t(weights='IMAGENET1K_V1')"
   ```

   Esto los descarga a `~/.cache/torch/hub/checkpoints/` que los nodos compute pueden leer.

## 11. Referencias

- Aboulmira, A., Lachgar, M., Hrimech, H., Camara, A., Elbahja, C., Elmansouri, A., & Hassini, Y. (2024). *SkinHealthMate app: An AI-powered digital platform for skin disease diagnosis*. Systems and Soft Computing, 6, 200166.
- Khan, S., Muhammad, R., Hussain, A., Sajjad, M., & Rashid, M. (2025). *Ensemble Deep Learning and LLM-Assisted Reporting for Automated Skin Lesion Diagnosis*. arXiv:2510.06260.
- Thieme, A. H., Zheng, Y., Machiraju, G., et al. (2023). *A deep-learning algorithm to classify skin lesions from mpox virus infection*. Nature Medicine, 29, 738-747.
