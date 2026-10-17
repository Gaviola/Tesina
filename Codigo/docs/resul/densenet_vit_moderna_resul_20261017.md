# Resultado — DenseNet121 y ViT-B/16 con la receta moderna (split por lesión)

**Fecha:** 2026-10-17 · **Plan:** [densenet_vit_moderna_plan](../ideas/densenet_vit_moderna_plan_20261012.md) ·
**Jobs:** TOKO 99007–99012 (ver `ejecuciones.md`, entrada del 12/10) + análisis local del 2026-10-17 ·
**Origen:** redacción del Cap. 3 (§3.5).

Fuentes: `outputs/results/{densenet_sweep_t02,vit_sweep_t06}_les_cwnone[_s43,_s44]_*.json` (bajados por `scp`
solo esos 18 archivos, para no pisar análisis locales con copias remotas), `outputs/slurm_logs/shared/990{07..12}.out`,
`outputs/results/statistical_tests_les_v2.json` (nuevo; el `_les` anterior se conserva) y
`outputs/results/densenet_vit_moderna_report.json` (`scripts/densenet_vit_moderna_report.py`).

## 1. Ejecución

Las 6 corridas terminaron el 14/10 sin errores (`Job completado`, 0 *tracebacks*). Detención temprana entre las
épocas 17 y 22 de 40; 5–7 min por corrida en la RTX 4080. Los logs confirman la receta del plan: dos etapas, LLRD
0.85, suavizado 0.1, sin MixUp/CutMix, focal γ = 0, sin pesos por clase, TTA; DenseNet121 con 6 961 031
parámetros (coincide con la Tabla 3.5 del documento). **Criterio «Completo» del plan: cumple** (6/6 con
`*_test_results.json`, predicciones de validación y de test).

## 2. Resultados en test (media ± sd, 3 semillas, n = 1503)

| Modelo | Trial | Acc | F1 pond. | **F1 macro** | **Sens. macro** | Recall MEL | AUC macro |
|---|---|---|---|---|---|---|---|
| Swin-Tiny | t06 | 0.846 ± 0.002 | 0.846 ± 0.004 | 0.733 ± 0.026 | 0.692 ± 0.025 | 0.623 ± 0.071 | 0.953 ± 0.014 |
| ConvNeXt-Tiny | t02 | 0.843 ± 0.005 | 0.840 ± 0.005 | 0.727 ± 0.007 | 0.691 ± 0.009 | 0.553 ± 0.042 | 0.964 ± 0.001 |
| **ViT-B/16** | t06 (de Swin) | 0.836 ± 0.003 | 0.836 ± 0.004 | 0.707 ± 0.025 | 0.681 ± 0.025 | 0.609 ± 0.072 | 0.956 ± 0.003 |
| **DenseNet121** | t02 (de ConvNeXt) | 0.822 ± 0.005 | 0.815 ± 0.004 | 0.655 ± 0.017 | 0.610 ± 0.020 | 0.509 ± 0.016 | 0.957 ± 0.003 |

Swin y ConvNeXt reproducen exactamente las cifras de [split_lesion_resul](split_lesion_resul_20260926.md) §3.

**Validación** (1289, media ± sd), que es donde se elige: F1 macro Swin 0.781 ± 0.018, ConvNeXt 0.740 ± 0.027,
ViT 0.740 ± 0.008, DenseNet 0.710 ± 0.011. Swin sigue siendo el mejor en validación.

## 3. Pruebas contra Swin-Tiny (semilla 42)

| Par | McNemar (solo A / solo B) | p | Holm (21 pares) | ΔF1 macro [IC 95 %] | ΔSens. macro [IC 95 %] |
|---|---|---|---|---|---|
| Swin − ConvNeXt | 73 / 70 | 0.867 | ns | +0.029 [−0.015, +0.074] | +0.022 [−0.027, +0.071] |
| Swin − ViT-B/16 | 81 / 70 | 0.416 | ns | +0.032 [−0.005, +0.070] | +0.018 [−0.019, +0.057] |
| Swin − DenseNet121 | 107 / 75 | 0.021 | **ns** (umbral 0.0083) | **+0.114 [+0.061, +0.170]** | **+0.122 [+0.069, +0.176]** |

Otros pares entre supervisados: ConvNeXt − DenseNet p = 0.026 (ns con Holm; ΔF1m +0.085 [+0.029, +0.146]),
ConvNeXt − ViT p = 0.573 (ΔF1m +0.003 [−0.048, +0.053]), DenseNet − ViT p = 0.143 (ΔF1m −0.082 [−0.148, −0.019]).

**Holm sobre la familia de 21 pares** (4 supervisados + DermLIP ZS + Mini-VLM ZS + LLaVA-Med ZS): 17 significativos
sin corrección y **15 con Holm**. Los 15 son todos los pares que involucran a un modelo *zero-shot*; ningún par entre
supervisados es significativo con Holm. Con la familia anterior (DenseNet y ViT legacy) eran 19 y 19: Swin y ConvNeXt
superaban a los dos legacy con p < 0.001.

## 4. Receta anterior frente a la moderna

| Modelo | Receta | Acc | F1 macro | Sens. macro | Recall MEL | AUC macro |
|---|---|---|---|---|---|---|
| DenseNet121 | anterior (s42, vista única, pesos por clase) | 0.812 | 0.660 | 0.672 | 0.587 | 0.940 |
| DenseNet121 | moderna (media) | 0.822 | 0.655 | 0.610 | 0.509 | 0.957 |
| ViT-B/16 | anterior (s42, vista única, pesos por clase) | 0.814 | 0.696 | 0.664 | 0.539 | 0.959 |
| ViT-B/16 | moderna (media) | 0.836 | 0.707 | 0.681 | 0.609 | 0.956 |

## 5. Lectura

1. **ViT-B/16 alcanza a los ganadores.** Con la misma receta queda a −0.026 de Swin en F1 macro (dentro de un
   desvío) y McNemar no distingue sus aciertos (p = 0.42). La ventaja que la tesina le atribuía a Swin sobre ViT
   (ΔF1m +0.059, p < 0.001) era sobre todo un efecto de la receta. Entre los cuatro supervisados, la arquitectura
   pesa menos que la receta.
2. **DenseNet121 queda por debajo, pero solo en las métricas por clase.** Su exactitud y su AUC son cercanas a las
   de los demás, pero su F1 macro y su sensibilidad macro están unos 0.08–0.12 por debajo (bootstrap con IC que no
   cruza 0). McNemar, que cuenta aciertos globales dominados por NV, no resiste Holm. La diferencia está en las
   clases minoritarias (recall MEL 0.509 ± 0.016).
3. **A DenseNet121 la receta moderna no le mejora el F1 macro** (0.660 → 0.655) y le baja la sensibilidad macro
   (0.672 → 0.610). La caída de sensibilidad es esperable, porque la anterior usaba pesos por clase (el mismo
   intercambio de §5 de `split_lesion_resul`). Que no mejore el F1 macro es compatible con el argumento del plan v4
   (BatchNorm y aumento fuerte), pero no lo prueba: los hiperparámetros son transferidos, no barridos.
4. **Hiperparámetros transferidos.** Un resultado peor indica que el modelo rinde menos con la configuración de su
   familia, no que no pueda rendir más con otra. Vale sobre todo para DenseNet121.
5. **Varianza.** La sd de ViT (0.025 en sens. macro y 0.072 en recall MEL) es del orden de la de Swin. DenseNet es
   el más estable (0.020 y 0.016), pero alrededor de valores más bajos.

## 6. Clasificador de referencia de la cascada

El plan pide revisar la elección (sin cambiarla automáticamente) si DenseNet o ViT alcanzan a los ganadores.
ViT-B/16 la alcanza en test, no la supera. **Propuesta: mantener Swin-Tiny.**

- Sigue teniendo el mejor F1 macro en validación (0.781 frente a 0.740), que es el criterio de selección.
- ViT-B/16 tiene tres veces más parámetros (85.8 M frente a 27.5 M).
- La cascada, el ruteo y la calibración del Cap. 5 ya están anclados en Swin.

El ensamble sigue siendo Swin + ConvNeXt: ViT-B/16 no salió de un barrido propio, y cambiar el par mirando el test
reabriría la selección sobre el test que la tesina evita.

## 7. Impacto en el documento

- **Cap. 3 §3.5:** se resuelve el `\pendiente` de los jobs 99007–99012; los cuatro modelos se comparan con la
  receta moderna, y la anterior queda como antecedente.
- **Cap. 3 §3.9:** la excepción «DenseNet121 y ViT-B/16 con la receta anterior, vista única, una semilla» pasa a
  aplicar solo a las corridas de antecedente; la familia de McNemar con Holm usa las corridas modernas
  (`statistical_tests_les_v2.json`).
- **Cap. 4 §4.1** (sin redactar): la tabla de supervisados usa §2; la conclusión cambia de «las modernas superan a
  las legacy» a «con la misma receta, ViT empata y DenseNet queda abajo en F1 macro».
- **Tabla SOTA:** v34 con las filas (a) y (b) en media ± sd y el hallazgo (3) reescrito.

## 8. Conclusión (veredicto)

**CUMPLE.** Las 6 corridas están completas, y los cuatro supervisados se comparan con la misma receta, la misma
partición y las mismas semillas. Resultado: ViT-B/16 queda empatado con Swin-Tiny y ConvNeXt-Tiny; DenseNet121
queda por debajo en F1 macro y sensibilidad macro. Swin-Tiny se mantiene como clasificador de referencia,
**pendiente de confirmación del autor** (§6).
