# Resultado — Split disjunto por lesión, selección en validación y semillas

**Fecha:** 2026-09-26 · **Planes:** [split_lesion_semillas_plan](../ideas/split_lesion_semillas_plan_20260912.md),
[criterio_seleccion_plan](../ideas/criterio_seleccion_plan_20260917.md) · **Jobs:** TOKO 97933–98007,
98041–98046, 98243–98246 (ver `ejecuciones.md`, entradas del 12, 13, 15 y 17/09) + análisis locales del
2026-09-26 · **Origen:** [feedback_20260912](../feedback_20260912.md).

Fuentes: `outputs/results/lesion_split_report.json` (barrido, ganadores, desbalance, melanoma,
calibración, ruteo), `leakage_analysis.json`, `dermlip/dermlip_split_eval.json`,
`robustness/robustness_summary.json`, `statistical_tests_les.json`, `classifier_ensemble_les/`,
`interpretability_les/`.

## 1. Motivación

La auditoría del 12/09 encontró tres problemas en la clasificación: (1) **fuga por lesión**: 543 de las
1503 imágenes de test (36.1 %) comparten `lesion_id` con train, con sesgo hacia las minoritarias (MEL 63 %,
BCC 70 %); (2) el ganador de ConvNeXt se había elegido **por test**; (3) el test se evaluaba con los pesos de
la **última época**, no con el mejor *checkpoint* en validación. Este documento cierra la re-ejecución
completa con el split corregido.

## 2. Diseño (resumen)

- **Split:** test idéntico (1503 imágenes). Se descartan de train/val las 776 imágenes de lesiones que
  están en test; `StratifiedGroupKFold` por `lesion_id` → train 6447 / val 1289. Solapamiento 0.
- **Barrido:** grid v4 (15 trials) × pesos por clase {auto, none} × {Swin-Tiny, ConvNeXt-Tiny} = 60
  corridas, más legacy (DenseNet121, ViT-B/16) y la réplica del cuadro de desbalance (4 pérdidas × 3
  modelos). 74/74 corridas OK tras dos reenvíos por *crash* del DataLoader.
- **Selección:** *checkpoint* por época con F1 ponderado en val (sin cambios); **trial ganador por F1
  macro en val** (decisión del 17/09, §4). Test evaluado con `--eval-best-checkpoint`.
- **Semillas:** 42/43/44 del ganador de cada modelo. Todo con TTA.

## 3. Ganadores (media ± sd sobre 3 semillas, test n=1503)

| Modelo | Trial | Acc | F1 pond. | **F1 macro** | **Sens. macro** | Recall MEL | AUC macro |
|---|---|---|---|---|---|---|---|
| Swin-Tiny | t06, sin pesos | 0.846 ± 0.002 | 0.846 ± 0.004 | 0.733 ± 0.026 | 0.692 ± 0.025 | 0.623 ± 0.071 | 0.953 ± 0.014 |
| ConvNeXt-Tiny | t02, sin pesos | 0.843 ± 0.005 | 0.840 ± 0.005 | 0.727 ± 0.007 | 0.691 ± 0.009 | 0.553 ± 0.042 | 0.964 ± 0.001 |
| Ensamble Swin+ConvNeXt | voto suave | 0.855 ± 0.003 | 0.853 ± 0.005 | 0.747 ± 0.005 | 0.706 ± 0.002 | — | — |

Referencia anterior (partición aleatoria, con fuga, una semilla): Swin v3 acc 0.868, F1 0.882, sens.
macro **0.870**.

**Lectura:**
1. **La sensibilidad macro cae de 0.870 a 0.692.** Es más que lo que anticipaba el subconjunto limpio
   (0.804) porque se suman dos efectos: la fuga (que el subconjunto limpio aislaba) y que **el ganador
   ahora no usa pesos por clase**. Con pesos por clase la sensibilidad macro del split por lesión llega a
   0.78 (Swin *weighted* 0.783), pero a costa de exactitud (0.752) y F1 macro (0.635); el criterio en
   validación la descarta (§4). El 0.870 anterior combinaba fuga + pesos por clase.
2. **Swin y ConvNeXt quedan empatados.** Medias casi idénticas; en la semilla 42 la diferencia no es
   significativa (McNemar p = 0.87; ΔF1m +0.029 [−0.015, +0.074]; Δsens +0.022 [−0.027, +0.071]).
   Swin sí supera a DenseNet121 y ViT-B/16 (McNemar p < 0.001; ΔF1m +0.095 y +0.059, ambos con IC que no
   cruza 0).
3. **Las métricas de minoritarias no se leen con una semilla.** El recall MEL de Swin con seed 42 era
   0.701; con tres semillas, 0.623 ± 0.071. La «mejora» de melanoma de ConvNeXt t02 (+0.096 con seed 42)
   quedó en +0.018 con tres semillas, dentro del desvío.
4. **Ensamble Swin+ConvNeXt:** sube el F1 macro (+0.014) y la sensibilidad macro (+0.014) respecto de
   Swin solo, y sobre todo **baja la varianza entre semillas** (sd de sens. macro 0.025 → 0.002). Con los
   cuatro modelos (seed 42), la mejor combinación (Swin+DenseNet+ViT, sens. 0.724) supera a Swin solo por
   +0.008, pero esa combinación se eligió mirando el test: no es un resultado reportable como ganador.

## 4. Criterio de selección: F1 macro en validación

| Criterio en val | Swin | ConvNeXt |
|---|---|---|
| F1 ponderado (anterior) | t06 sin pesos | t06 sin pesos |
| Sens. macro | t02 con pesos (acc 0.728, F1m 0.611) | t07 con pesos (acc 0.775, F1m 0.636) |
| **F1 macro (elegido)** | **t06 sin pesos** | **t02 sin pesos** |

El F1 ponderado está dominado por NV (67 %); la sensibilidad macro sola ignora los falsos positivos y
elige modelos que sobre-predicen las minoritarias. El F1 macro es balanceado por clase y penaliza falsos
positivos. Solo cambia ConvNeXt: t02 con tres semillas da F1m 0.727 ± 0.007 frente a 0.723 ± 0.013 del t06
anterior, y sens. macro 0.691 ± 0.009 frente a 0.700 ± 0.018 (−0.009, dentro del desvío anterior).
**Criterio de éxito del plan del 17/09: cumplido.**

El *checkpoint* dentro de cada corrida se sigue eligiendo por F1 ponderado (`trainer.py`, `monitor:
val_f1`); cambiarlo obligaba a reentrenar las 60 corridas. El documento debe decirlo así.

## 5. Desbalance (réplica con el split por lesión, seed 42)

| Pérdida | Swin acc / F1m / sens / MEL | ConvNeXt acc / F1m / sens / MEL | DenseNet acc / F1m / sens / MEL |
|---|---|---|---|
| CE | 0.860 / 0.745 / 0.707 / 0.551 | 0.846 / 0.753 / 0.715 / 0.605 | 0.830 / 0.664 / 0.634 / 0.485 |
| CE ponderada | 0.752 / 0.635 / **0.783** / **0.790** | 0.669 / 0.570 / 0.731 / 0.659 | 0.568 / 0.470 / 0.692 / 0.545 |
| Focal | 0.781 / 0.620 / 0.773 / 0.503 | 0.739 / 0.588 / 0.730 / 0.509 | 0.557 / 0.479 / 0.654 / 0.581 |
| Balanced softmax | 0.756 / 0.626 / 0.758 / 0.695 | 0.733 / 0.576 / 0.719 / 0.425 | 0.568 / 0.479 / 0.646 / 0.515 |

Mismo patrón que con la partición anterior: las pérdidas para desbalance cambian exactitud por
sensibilidad macro; ninguna gana en F1 macro a la CE. Legacy: DenseNet121 0.812 / 0.660 / 0.672, ViT-B/16
0.814 / 0.696 / 0.664.

## 6. DermLIP y VLM generales

- **Zero-shot no depende del split** (nunca vio HAM): DermLIP sens. macro 0.510, Mini-VLM 0.144,
  LLaVA-Med 0.156. El orden especializado supervisado ≫ DermLIP ZS ≫ VLM general se mantiene, todas las
  diferencias con IC que no cruza 0 (`statistical_tests_les.json`).
- **Métodos ajustados sobre embeddings DermLIP** (split aleatorio → por lesión): kNN 0.666 → 0.568,
  SVM-RBF 0.788 → 0.673, linear-probe 0.747 → 0.729. La inflación escala con la capacidad de memorizar
  vecinos: los métodos locales caen, el lineal casi no.
- **Experimento controlado DermLIP vs Swin-ImageNet congelado** (`embeddings/embeddings_classical_les.json`),
  sens. macro con la misma cabeza: SVM-RBF 0.673 vs 0.466, regresión logística 0.689 vs 0.538, Random
  Forest 0.515 vs 0.162. La representación especializada gana con todas las cabezas: H4 se sostiene con
  la partición por lesión.

## 7. Melanoma, calibración, ruteo, HIBA, perturbaciones e interpretabilidad

- **Melanoma vs resto (media ± sd de 3 semillas, umbral de esp ≥ 0.85 fijado en val;
  `lesion_split_report.json` → `melanoma_semillas`):** AUC Swin 0.921 ± 0.005 (antes 0.931), ConvNeXt
  0.909 ± 0.004, ensamble 0.926 ± 0.003. En el punto de operación: Swin sens 0.796 ± 0.036 / esp 0.862,
  ConvNeXt 0.794 ± 0.012 / 0.854, ensamble **0.828 ± 0.007** / 0.852, VPN 0.97–0.98. Con *argmax* la
  sensibilidad es 0.623 ± 0.071 (Swin): fijar el umbral en validación no solo sube la sensibilidad, también
  reduce su varianza entre semillas a la mitad (Swin) o a una décima parte (ensamble). Antes (con fuga,
  una semilla) Swin daba 0.862 / 0.858. **Maligno vs benigno** (seed 42): AUC 0.919 / 0.927 / 0.937.
- **Calibración:** sin pesos por clase el modelo ya está calibrado (ECE Swin 0.040 → TS 0.027 → VS
  0.014; T = 0.85). Antes: ECE 0.394, venía de los pesos por clase y de ajustar T sobre un val
  solapado con train. **Mecanismo verificado con la partición por lesión** (`calibration_les/`): el mismo
  trial entrenado con pesos por clase da ECE 0.376 (Swin) y 0.211 (ConvNeXt) contra 0.040 sin pesos; el
  76–79 % de sus predicciones tiene confianza < 0.5 con exactitud 0.775 / 0.599, es decir, quedan
  subconfiados. El diagrama incluye el histograma de confianza, que es lo que explica el ECE.
- **Ruteo de 3 niveles (Swin nuevo + kNN DermLIP por lesión):** afirmativo 80.1 % (cobertura 0.915),
  diferencial 16.5 % (0.847), abstención 3.4 %; cobertura de lo presentado **0.904** (antes 0.934).
  Por clase, melanoma: 62 % afirmativo, 32 % diferencial, 6 % abstención.
- **HIBA (n=1616, validación externa):** Swin 0.546 acc / 0.424 sens, ConvNeXt 0.558 / 0.447 (con
  fuga: 0.585 / 0.532 y 0.472 / 0.496). Caída de ~30 puntos de exactitud respecto de HAM; recall MEL
  0.455 y 0.435, la clase prioritaria es la que peor generaliza.
- **Perturbaciones** (bug de preprocesamiento corregido el 17/09): ruido gaussiano la más dañina,
  resolución la más benigna; ConvNeXt aguanta mejor la degradación espacial (blur sev3 0.487 vs 0.286).
  Ejemplos regenerados (`robustness_examples_les.png`): en Swin fallan primero ruido y desenfoque, y JPEG
  y resolución se toleran hasta sev4–5 (antes: ruido y JPEG primero).
- **Grad-CAM** (`interpretability_les/`, mismo bug de preprocesamiento corregido hoy, más la
  superposición sobre el recorte que ve el modelo): el Swin nuevo concentra la activación sobre la
  lesión en 6 de 7 ejemplos; el VASC de la figura ahora se predice NV, con mapa difuso. La
  **saliencia de DermLIP no es interpretable**: en ambas versiones es una grilla de puntos alineada con
  los parches del ViT (artefacto del gradiente de entrada), no una región sobre la lesión. No debe
  presentarse como evidencia de que DermLIP «mira la lesión».

## 8. Qué queda sobre la partición anterior

- **Cascada de generación:** en re-anclaje (Mendieta 1177953, 1178901; SkinVL ya terminado:
  consistencia 0.802 → **0.847**, Δ +0.045 [+0.025, +0.064]). Resultado en su propio documento.
- **RAG y `full_uncertainty`**: fuera del re-anclaje por decisión del 17/09 (brazos complementarios, 400
  casos cada uno). Se declaran como análisis con el anclaje anterior.
- **Métricas por clase, taxonomía de errores de v3, ablaciones de receta
  (sin mixup, sin TTA, etc.):** sobre la partición anterior. Son análisis de mecanismo, no de magnitud;
  se declaran como tales o se omiten.

## 9. Conclusión (veredicto)

**CUMPLE**, con un matiz.

- *Headline válido* (media ± sd de 3 semillas del ganador en validación, sin fuga): **cumple**.
- *Estabilidad* (sd de sens. macro ≤ 0.02): **cumple ConvNeXt (0.009), no cumple Swin (0.025)**. Se
  reporta igual, con el desvío, y el ensamble (sd 0.002) queda como la configuración estable.
- *Conclusiones centrales*: **se sostienen**. El orden de los enfoques no cambia, DermLIP ZS sigue
  rompiendo el colapso de los VLM generales y la cascada re-anclada mejora con el ancla nueva (SkinVL;
  Mini-VLM y LLaVA-Med pendientes).
- *Criterio de selección* (plan del 17/09): **cumple**.

**Siguiente paso:** cerrar el re-anclaje con Mini-VLM y LLaVA-Med; actualizar la tabla SOTA (v33) y
`experimentacion.tex` con los números de §3 (el headline pasa a ser 0.692 ± 0.025, no 0.870).
