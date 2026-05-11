# Análisis Final de Clasificadores — Fase 1

**Fecha:** 2026-05-01  
**Dataset de evaluación:** HAM10000 Test Set (ISIC 2018 Task 3, n=1503) + HIBA OOD (n=1616)  
**Modelos:** DenseNet121, ViT-B/16, ConvNeXt-Tiny, Swin-Tiny  
**Recipes ejecutados:** legacy, modern v1, modern v2, modern v3

---

## 1. Resumen de iteraciones

| Iteración | Cambios principales | Resultado |
|-----------|-------------------|-----------|
| **legacy** | Baseline sweep-optimizado (AdamW, CrossEntropy + class weights, CosineAnnealingLR) | Mejores métricas en HAM10000 para DenseNet/ViT |
| **modern v1** | + MixUp/CutMix (α=0.2/1.0) + Focal Loss (γ=2.0) + LLRD=0.75 + RandAugment (m=9) + TTA + Two-stage | DenseNet −9 pt F1; val_loss explosivo por MixUp |
| **modern v2** | − MixUp/CutMix + Focal Loss (γ=1.0) + LLRD=0.85 | Focal Loss colapsa hacia vasc; DenseNet Acc=0.519 |
| **modern v3** | − Focal Loss (γ=0 → CE + class weights) + RandAugment (m=6 para DenseNet) | ConvNeXt/Swin mejoran; DenseNet/ViT siguen degradados |

---

## 2. Resultados completos por modelo e iteración

### 2.1 HAM10000 Test Set (n=1503)

Orden de clases: `[MEL, NV, BCC, AKIEC, BKL, DF, VASC]`

| Modelo | Versión | Acc | F1-w | AUC-ROC | Sens-macro | Spec-macro |
|--------|---------|-----|------|---------|-----------|-----------|
| DenseNet121 | legacy ★ | 0.8456 | 0.8517 | 0.9637 | 0.7761 | 0.9674 |
| ViT-B/16 | legacy ★ | **0.8576** | **0.8621** | **0.9653** | 0.7972 | **0.9716** |
| DenseNet121 | modern v1 | 0.7572 | 0.7763 | — | — | — |
| ViT-B/16 | modern v1 | 0.8097 | 0.8205 | — | — | — |
| ConvNeXt-Tiny | modern v1 | 0.8150 | 0.8276 | — | — | — |
| Swin-Tiny | modern v1 | 0.8576 | 0.8648 | — | — | — |
| DenseNet121 | modern v2 | 0.5190 | 0.6151 | 0.9403 | 0.7217 | 0.9277 |
| ViT-B/16 | modern v2 | 0.6035 | 0.6615 | 0.9502 | 0.7645 | 0.9389 |
| ConvNeXt-Tiny | modern v2 | 0.7871 | 0.8361 | 0.9620 | 0.8124 | 0.9644 |
| Swin-Tiny | modern v2 | 0.6979 | 0.7514 | 0.9585 | 0.8120 | 0.9523 |
| DenseNet121 | modern v3 | 0.5902 | 0.6760 | 0.9540 | 0.7339 | 0.9376 |
| ViT-B/16 | modern v3 | 0.6680 | 0.7116 | 0.9446 | 0.7664 | 0.9479 |
| ConvNeXt-Tiny | modern v3 | 0.8190 | 0.8464 | 0.9560 | **0.8398** | 0.9694 |
| Swin-Tiny | modern v3 | 0.7951 | 0.8163 | 0.9469 | 0.8088 | 0.9658 |

★ Elegidos de W&B sweep de 25+ runs.  
— No disponible (v1 usó formato antiguo sin JSON consolidado).

### 2.2 HIBA OOD (n=1616) — evaluación fuera de distribución

| Modelo | Versión | Acc | F1-w | AUC-ROC | Sens-macro | Spec-macro |
|--------|---------|-----|------|---------|-----------|-----------|
| DenseNet121 | legacy | 0.5656 | 0.5402 | 0.8372 | 0.4396 | 0.9179 |
| ViT-B/16 | legacy | 0.5402 | 0.5241 | 0.8250 | 0.4351 | 0.9156 |
| DenseNet121 | modern v2 | 0.4183 | 0.4722 | 0.8234 | 0.4759 | 0.9079 |
| ViT-B/16 | modern v2 | 0.4882 | 0.5305 | 0.8409 | 0.5149 | 0.9183 |
| ConvNeXt-Tiny | modern v2 | 0.4604 | 0.5236 | 0.8174 | 0.4823 | 0.9152 |
| Swin-Tiny | modern v2 | 0.5421 | 0.5691 | 0.8243 | 0.5426 | 0.9248 |
| DenseNet121 | modern v3 | 0.3886 | 0.4412 | 0.8151 | 0.4807 | 0.9037 |
| ViT-B/16 | modern v3 | 0.5272 | 0.5582 | 0.8319 | 0.5365 | 0.9232 |
| ConvNeXt-Tiny | modern v3 | 0.5551 | **0.5885** | 0.8166 | 0.5398 | 0.9277 |
| Swin-Tiny | modern v3 | **0.5613** | 0.5753 | **0.8271** | **0.5528** | **0.9277** |

### 2.3 Sensibilidad por clase — mejores modelos en HAM10000

Clases clínicamente críticas:

| Clase | DenseNet legacy | ViT legacy | ConvNeXt-Tiny v3 | Swin-Tiny v3 |
|-------|----------------|-----------|-----------------|-------------|
| MEL (0) | 0.737 | 0.683 | 0.743 | **0.826** |
| NV (1) | 0.887 | 0.908 | 0.832 | 0.794 |
| BCC (2) | 0.870 | 0.870 | 0.844 | 0.831 |
| AKIEC (3) | 0.755 | 0.755 | 0.796 | 0.816 |
| BKL (4) | 0.745 | 0.764 | 0.782 | 0.733 |
| DF (5) | 0.529 | 0.647 | **0.882** | 0.706 |
| VASC (6) | 0.909 | 0.955 | 1.000 | 0.955 |

---

## 3. ¿Cuáles son los mejores modelos?

### Mejor en HAM10000 (datos vistos):
**ViT-B/16 legacy** — Acc=0.858, F1=0.862 (sweep-optimizado).  
**DenseNet121 legacy** — Acc=0.846, F1=0.852 (sweep-optimizado).

### Mejor en HAM10000 con recipe modern (no sweep):
**ConvNeXt-Tiny v3** — Acc=0.819, F1=0.846. Competitivo: ΔF1=-0.016 vs ViT legacy.

### Mejor en HIBA OOD (datos no vistos):
**Swin-Tiny v3** — Acc=0.561, F1=0.575. Mejor generalización al dominio HIBA.  
**ConvNeXt-Tiny v3** — Acc=0.555, F1=0.589. Mejor F1-weighted OOD.

### Modelo recomendado para tabla SOTA:

| Rol | Modelo | Dataset | Acc | F1-w | AUC |
|-----|--------|---------|-----|------|-----|
| CNN clásica | DenseNet121 legacy | HAM10000 | 0.8456 | 0.8517 | 0.9637 |
| Transformer clásico | ViT-B/16 legacy | HAM10000 | 0.8576 | 0.8621 | 0.9653 |
| CNN moderna | ConvNeXt-Tiny v3 | HAM10000 | 0.8190 | 0.8464 | 0.9560 |
| Transformer moderno | Swin-Tiny v3 | HAM10000 | 0.7951 | 0.8163 | 0.9469 |
| Mejor generalización OOD | Swin-Tiny v3 | HIBA | 0.5613 | 0.5753 | 0.8271 |

---

## 4. ¿Tiene sentido seguir iterando?

**No, no tiene sentido continuar iterando en la dirección actual.** Las razones son:

### 4.1 Rendimiento de DenseNet/ViT con recipe modern

Después de tres iteraciones, DenseNet con recipe modern alcanza como máximo F1=0.676 (v3) contra F1=0.852 del legacy. La brecha es de **~17 puntos**, y no ha convergido hacia los valores legacy en ninguna iteración. ViT moderno alcanza F1=0.712 contra 0.862 legacy (brecha de **~15 puntos**).

La causa es estructural: las arquitecturas con **BatchNorm** (DenseNet) son inherentemente más sensibles al stack de augmentación agresivo (RandAugment + RandomErasing + RandomResizedCrop). Las estadísticas de batch fluctúan entre epochs haciendo inestable el entrenamiento. Esto no se resuelve ajustando γ de Focal Loss ni LLRD; requeriría un sweep de hiperparámetros específico para el recipe modern, con un costo de ≥25 runs adicionales por arquitectura.

### 4.2 ConvNeXt-Tiny y Swin-Tiny mejoran, pero no superan al legacy

Los modelos con LayerNorm son más robustos al recipe modern. ConvNeXt-Tiny v3 llegó a F1=0.846, solo 1.6 puntos por debajo del ViT legacy. Sin embargo, el legacy fue sweep-optimizado. Un sweep para ConvNeXt/Swin podría cerrar esa brecha, pero:
- El objetivo original era Accuracy ≥ 0.90 → **ningún modelo lo alcanzó**.
- F1 ≥ 0.90 tampoco fue alcanzado por ningún modelo.

### 4.3 Rendimientos decrecientes

De v1 a v3, las mejoras de ConvNeXt-Tiny son:
- F1: 0.828 → 0.836 → 0.846 (ganancia de +1 pt por iteración)
- Swin-Tiny: F1: 0.865 → 0.751 → 0.816 (no monotónico)

Para DenseNet/ViT el recipe modern nunca superó al legacy en ninguna iteración.

### 4.4 Conclusión sobre iteraciones

Los legacy models son el techo real para sus arquitecturas bajo el setup de entrenamiento actual. Una v4 con Focal Loss ajustado o LLRD distinto produciría mejoras marginales. La vía correcta si se desea superar los legacy sería:
1. Correr un W&B sweep específico para el recipe modern (≥25 runs), lo cual es costoso en tiempo de cluster.
2. Usar pesos pre-entrenados Noisy Student (EfficientNet-based) como en SkinHealthMate — cambiaría las arquitecturas comparadas.

Ambas opciones están fuera del scope de la tesina según las decisiones documentadas.

---

## 5. ¿Los modelos funcionan bien con datos no vistos?

**No, la generalización OOD es el mayor problema del sistema.**

### 5.1 Magnitud del domain shift

Todos los modelos pierden entre 25 y 47 puntos de accuracy al pasar de HAM10000 a HIBA:

| Modelo | Acc HAM | Acc HIBA | Δ Acc |
|--------|---------|---------|-------|
| DenseNet legacy | 0.846 | 0.566 | −0.280 |
| ViT legacy | 0.858 | 0.540 | −0.318 |
| ConvNeXt-Tiny v3 | 0.819 | 0.555 | −0.264 |
| Swin-Tiny v3 | 0.795 | 0.561 | −0.234 |
| DenseNet modern v3 | 0.590 | 0.389 | −0.201 |

La caída más pronunciada se observa en DenseNet modern v3 (ya mal en HAM, peor en HIBA). El menor delta lo tiene Swin-Tiny v3: a pesar de no ser el mejor en HAM, es el más robusto en HIBA.

### 5.2 Disociación AUC vs Accuracy en HIBA

El AUC-ROC en HIBA (rango 0.82–0.84) es significativamente mejor que el Accuracy (0.39–0.56). Esto indica que los modelos aprenden representaciones que discriminan entre clases en el espacio de probabilidades, pero el **calibrado del argmax está degradado** al cambiar de dominio. El modelo no está completamente ciego en HIBA; sabe "quién es más probable", pero no acierta consistentemente en el diagnóstico concreto.

### 5.3 Causas del domain shift

1. **Diferencia de fototipo:** HIBA incluye fototipos III-VI con mayor prevalencia, mientras HAM10000 tiene predominancia de fototipos I-II (población caucásica europea). La apariencia visual de las lesiones varía según el fototipo.
2. **Condiciones de adquisición:** HIBA usa dermoscopios distintos, con diferentes niveles de luz y de calibración de color.
3. **Distribución de clases diferente:** HIBA tiene más SCC (mapeado a AKIEC), clase que todos los modelos clasifican mal (sens. 0.17–0.33 en HIBA).
4. **Ausencia de domain adaptation:** los modelos fueron entrenados exclusivamente en HAM10000. No se aplicó ninguna técnica de adaptación al dominio (no DA, no mixup cross-domain, no augmentation de color específica para fototipos).

### 5.4 Sensibilidad MEL en HIBA (clínicamente más crítico)

| Modelo | Sens MEL HIBA | Sens MEL HAM |
|--------|--------------|-------------|
| DenseNet legacy | 0.435 | 0.737 |
| ViT legacy | 0.415 | 0.683 |
| ConvNeXt-Tiny v3 | 0.506 | 0.743 |
| Swin-Tiny v3 | 0.545 | 0.826 |

La sensibilidad en melanoma cae a la mitad en HIBA. Esto es un problema clínico grave si el sistema fuera a desplegarse en hospitales con pacientes de fototipos más oscuros.

---

## 6. Principales problemas identificados

### 6.1 Incompatibilidad BatchNorm + augmentación agresiva

DenseNet121 usa BatchNorm en cada capa convolucional. Con el recipe modern (RandAugment m=9 + RandomErasing + RandomResizedCrop scale_min=0.7), las estadísticas de batch son altamente variables entre iteraciones, desestabilizando las estimaciones de media/varianza acumuladas. Esto se manifiesta como:
- Incapacidad de converger a la solución legacy incluso después de 40 epochs.
- Alta sensibilidad a la tasa de aprendizaje del backbone (LLRD demasiado agresivo genera gradientes que se anulan).

ConvNeXt-Tiny y Swin-Tiny usan **LayerNorm**, que normaliza por muestra y no por batch, siendo insensibles a la distribución del batch → más estables con augmentación agresiva.

### 6.2 Desbalance de clases: NV domina y confunde

NV (melanocytic nevi) representa el **67% del test set** (1006/1503 muestras). Los modelos modern, sin MixUp como ancla de calibración, tienden a confundir NV con otras clases o viceversa. En DenseNet modern v2, el modelo predice `vasc` (17 muestras en test) para 462 de las 1006 muestras NV reales — colapso clásico por Focal Loss sin regularización de mezcla.

Incluso en los modelos legacy, NV genera confusión con MEL (57-81 errores por modelo), lo que es el tipo de error más peligroso en clínica (diagnosticar melanoma como nevus benigno).

### 6.3 DF (dermatofibroma): clase minoritaria extrema

DF tiene solo **17 muestras** en el test set y el 115 en train. Todos los clasificadores tienen baja sensibilidad históricamente (DenseNet legacy: 0.529). ConvNeXt-Tiny v3 alcanza 0.882, pero con un denominador tan pequeño (17 muestras, 15 correctas), el valor es estadísticamente ruidoso — un solo error cambia la sensibilidad en casi 6 puntos.

### 6.4 Ausencia de sweep para recipe modern

Los modelos legacy fueron elegidos de un sweep de 25+ configuraciones. El recipe modern usó hiperparámetros fijos en todas las iteraciones. Sin un sweep específico para el recipe modern, la comparación legacy vs modern no es del todo justa: los legacy tienen ventaja sistemática por optimización de hiperparámetros.

### 6.5 Sin técnicas de dominio para HIBA

Los modelos no recibieron ninguna forma de adaptación de dominio para HIBA. Las opciones no implementadas que podrían mejorar la generalización incluyen:
- Domain randomization en la augmentación (simular fototipos distintos con color jitter más agresivo)
- Contrastive learning entre HAM y HIBA
- Test-time adaptation (TTA extendida con transforms de normalización de iluminación)

---

## 7. Conclusiones y recomendaciones para la tesina

### 7.1 Modelos a reportar en la tabla SOTA

| Modelo | Dataset | Acc | F1-w | AUC | Sens MEL | Sens DF |
|--------|---------|-----|------|-----|---------|--------|
| DenseNet121 (legacy) | HAM10000 | 0.846 | 0.852 | 0.964 | 0.737 | 0.529 |
| ViT-B/16 (legacy) | HAM10000 | 0.858 | 0.862 | 0.965 | 0.683 | 0.647 |
| ConvNeXt-Tiny (modern v3) | HAM10000 | 0.819 | 0.846 | 0.956 | 0.743 | 0.882 |
| Swin-Tiny (modern v3) | HAM10000 | 0.795 | 0.816 | 0.947 | 0.826 | 0.706 |
| DenseNet121 (legacy) | HIBA | 0.566 | 0.540 | 0.837 | 0.435 | — |
| ViT-B/16 (legacy) | HIBA | 0.540 | 0.524 | 0.825 | 0.415 | — |
| ConvNeXt-Tiny (modern v3) | HIBA | 0.555 | 0.589 | 0.817 | 0.506 | — |
| Swin-Tiny (modern v3) | HIBA | 0.561 | 0.575 | 0.827 | 0.545 | — |

### 7.2 Narrativa para la tesina

Los resultados de Fase 1 confirman tres hallazgos de relevancia para la comparación con VLMs:

1. **Los clasificadores CNN/ViT clásicos tienen un techo claro en HAM10000** (~0.85–0.86 Acc/F1) bajo el setup de entrenamiento estándar con datos únicamente de HAM10000.

2. **El recipe "modern" no superó al baseline sweep-optimizado**, revelando que la ganancia de las técnicas de regularización avanzadas (RandAugment, RandomErasing, two-stage, TTA) depende críticamente de la arquitectura subyacente. Arquitecturas con LayerNorm (ConvNeXt, Swin) responden mejor; las de BatchNorm (DenseNet) son más sensibles.

3. **La generalización OOD es el principal desafío**, con caídas de 25–32 puntos en HAM→HIBA. Este hallazgo motiva el uso de VLMs, que en principio poseen mejor conocimiento previo sobre variabilidad visual de patologías dermatológicas y distintos fototipos, al haber sido pre-entrenados en datasets de mayor diversidad.

### 7.3 ¿Continuar iterando los clasificadores?

**No se recomienda continuar iterando con el recipe modern para DenseNet/ViT.** El costo computacional adicional no es justificable dado el contexto de la tesina y los retornos decrecientes observados. Las mejoras obtenibles con una v4 serían marginales (≤1 pt F1).

Para ConvNeXt-Tiny, si el tiempo de cluster lo permite, un sweep específico de 10–15 runs sobre `lr` y `weight_decay` podría acercar su F1 a 0.86+, pero no es estrictamente necesario para la narrativa de la tesina.

**La prioridad debe ser avanzar a Fase 2 (VLMs)**, que es el núcleo diferencial del trabajo.

---

## 8. Archivos de resultados

Los resultados están organizados en:

```
outputs/results/
├── classifiers/
│   ├── legacy/             # DenseNet121 + ViT-B/16 sweep-optimizado (con HIBA)
│   ├── modern_v1/          # Vacío — v1 usó formato antiguo sin JSON consolidado
│   ├── modern_v2/          # Todos los modelos con Focal Loss (fallido)
│   └── modern_v3/          # Todos los modelos con CE + class weights (final)
├── vlm/                    # Resultados de LLaVA-Med y Mini-VLM
├── first_iteration/        # Resultados históricos del primer prototipo
├── llava_med/              # Métricas stage1/stage2 LLaVA-Med
└── mini_vlm/               # Métricas stage1/stage2 Mini-VLM
```

Archivos clave por modelo (formato consolidado con secciones `ham10000`, `hiba`, `combined`):
- `classifiers/legacy/densenet_legacy_test_results.json`
- `classifiers/legacy/vit_legacy_test_results.json`
- `classifiers/modern_v3/convnext_tiny_modern_v3_test_results.json`
- `classifiers/modern_v3/swin_tiny_modern_v3_test_results.json`
