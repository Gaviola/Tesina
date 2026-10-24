# Ficha 4.1 — Clasificadores supervisados

**Estado (18/10/2026): borrador para aprobar; ajustado el mismo día a las reglas de la revisión del Cap. 3 (sin receta anterior ni comparación entre iteraciones).** Archivo: `Chapters/04-Resultados-Clasificacion/01-clasificadores-supervisados.tex`.
Label: `sec:res_supervisados`. Tablas: `tab:res_supervisados`, `tab:res_recall_clase`, `tab:res_desbalance`.

## Hilo conductor

Pregunta que responde la sección: ¿cuánto rinde un clasificador supervisado entrenado con *HAM10000* sin fuga, qué
tan estable es ese número y de qué depende?

Viene de: el Cap. 3 deja los cuatro modelos con un mismo procedimiento de entrenamiento (`sec:met_supervisados`), la regla de selección en
validación y la sensibilidad macro como resultado principal (`sec:met_seleccion`), las líneas base
(`sec:met_lineas_base`) y la partición por lesión con su fuga cuantificada (`sec:met_particiones`). La introducción del
capítulo deja dicho que los números son de test, con media ± sd de tres semillas.
Deja instalado: la referencia contra la que se mide a los VLM en 4.2 (Swin-Tiny, sensibilidad macro
0.692 ± 0.025, exactitud 0.846) y la idea de que con esta receta la arquitectura pesa poco y el manejo del desbalance
es un intercambio entre sensibilidad y exactitud, y una medida de cuánto infla los resultados la fuga. Para 4.6: la calibración de los modelos sin pesos por clase. Para 4.9:
el recall de melanoma con *argmax* y su desvío.

```
P1  Selección: en validación, el F1 macro elige Swin-Tiny t06 y ConvNeXt-Tiny t02, los dos sin pesos por clase;
    Swin tiene el mejor F1 macro de validación de los cuatro modelos (0.781 ± 0.018)        función: describe
    ↓ consecuencia: elegidos en validación, se miden en test
P2  Tabla principal (tab:res_supervisados). Los cuatro modelos y el ensamble, media ± sd: Swin 0.692 ± 0.025
    de sensibilidad macro y 0.846 de exactitud, contra 0.143 y 0.669 del clasificador mayoritario  función: describe
    ↓ contraste: tres de los cuatro tienen medias casi iguales; ¿hay un ganador?
P3  Con el mismo procedimiento, la arquitectura pesa poco: Swin, ConvNeXt y ViT empatan (McNemar p = 0.87 y 0.42; ΔF1m con
    IC que cruza 0). DenseNet121 queda 0.08–0.12 abajo en F1 macro y sensibilidad macro (IC bootstrap que no cruza 0),
    pero no en exactitud ni AUC, y McNemar no resiste Holm. La familia completa de pruebas está en 4.6
                                                                                            función: interpreta
    ↓ ampliación: si la diferencia de DenseNet está en las clases minoritarias, hay que mirar cada clase
P4  Recall por clase (tab:res_recall_clase): NV y BCC altos y estables; DF, AKIEC y MEL bajos y muy variables. La
    diferencia de DenseNet está en DF (0.353) y en MEL (0.509). La exactitud varía ±0.002 entre semillas y el recall
    MEL de Swin ±0.071: una semilla no alcanza                                              función: interpreta
    ↓ consecuencia: con esa varianza, combinar modelos puede estabilizar
P5  Ensamble Swin + ConvNeXt: +0.014 de F1 macro y de sensibilidad macro, y el sd de la sensibilidad macro baja de
    0.025 a 0.002. Estabiliza más de lo que mejora                                          función: interpreta
    ↓ contraste: los ganadores no usan pesos por clase; ¿mejoraría el desbalance tratarlo en la pérdida?
P6  Desbalance (tab:res_desbalance, semilla 42): las tres pérdidas para desbalance suben la sensibilidad macro (Swin
    0.707 → 0.783 con CE ponderada) a costa de exactitud (0.860 → 0.752) y de F1 macro (0.745 → 0.635); ninguna supera
    a la CE en F1 macro. Es un intercambio, no una mejora                                   función: interpreta
    ↓ ampliación: estos números se obtienen sin fuga; ¿cuánto cambian si la partición la tiene?
P7  Efecto de la fuga (la comparación que anuncia sec:met_particiones): un Swin-Tiny entrenado con la partición por
    imagen da 0.870 de sensibilidad macro sobre toda la prueba y 0.804 sobre el subconjunto limpio (894 imágenes); el
    control, DermLIP sin ajuste, no baja (0.510 → 0.527), así que la diferencia es fuga y no composición del
    subconjunto. Da el orden de magnitud del sesgo de las particiones por imagen      función: interpreta / limita
→ Transición a 4.2: Swin-Tiny queda como referencia; la pregunta es si un VLM médico general, que además genera texto,
  clasifica igual de bien.

Se definen acá (y no se vuelven a definir): el resultado de referencia del capítulo (Swin 0.692 ± 0.025).
Se retoman de antes (solo se nombran, con \ref): receta, barrido y semillas (sec:met_supervisados_*), criterio de
selección (sec:met_seleccion), clasificador mayoritario (sec:met_lineas_base), fuga y subconjunto limpio
(sec:met_particiones), voto suave (sec:met_supervisados_ensamble), McNemar, bootstrap y Holm (sec:met_estadistica).
Extensión: 7 párrafos y 3 tablas, ~4.5 páginas.
```

## Fuentes de cada número

| P | Número | Fuente |
|---|---|---|
| P1 | Ganadores t06 y t02 sin pesos; 30 corridas por modelo; F1 macro de validación Swin 0.781 ± 0.018, ConvNeXt 0.740 ± 0.027, ViT 0.740 ± 0.008, DenseNet 0.710 ± 0.011 | `lesion_split_report.json` (`ganadores`, `val_media_std`); `densenet_vit_moderna_resul_20261017.md` §2 |
| P2 | Tabla de test de los cuatro modelos (exactitud, F1 ponderado, F1 macro, sensibilidad macro, recall MEL, AUC macro) | `densenet_vit_moderna_resul_20261017.md` §2 (`densenet_vit_moderna_report.json`) |
| P2 | Ensamble: exactitud 0.855 ± 0.003, F1 ponderado 0.853 ± 0.005, F1 macro 0.747 ± 0.005, sensibilidad macro 0.706 ± 0.002 | `classifier_ensemble_les/ensemble_seeds.json`; `split_lesion_resul_20260926.md` §3 |
| P2 | Clasificador mayoritario 0.669 / 0.143 | 3.3 (`03-criterios-evaluacion.tex`, `sec:met_seleccion`) |
| P3 | McNemar y ΔF1m, Δsens con IC (pares de supervisados, semilla 42); Holm sobre 21 pares | `statistical_tests_les_v2.json`; `densenet_vit_moderna_resul_20261017.md` §3 |
| P4 | Recall por clase, media ± sd (abajo) | `*_les_cwnone{,_s43,_s44}_test_results.json` → `ham10000.sensitivity_per_class` (orden MEL, NV, BCC, AKIEC, BKL, DF, VASC, verificado con los totales de la matriz de confusión) |
| P4 | Swin: recall MEL 0.701 con la semilla 42 frente a 0.623 ± 0.071 con tres | `lesion_split_report.json` (`test_por_semilla`) |
| P5 | Ensamble frente a Swin solo | `ensemble_seeds.json` |
| P6 | Tabla de desbalance, 4 pérdidas × 3 modelos | `lesion_split_report.json` (`legacy_y_desbalance`, `*_imb_*_les`); `split_lesion_resul_20260926.md` §5 |
| P7 | 0.870 (toda la prueba) y 0.804 (subconjunto limpio, 894 imágenes) del Swin-Tiny entrenado con la partición por imagen (t08); DermLIP ZS 0.510 → 0.527 | `leakage_analysis.json` (`Swin-Tiny (sweep t08, headline)`, `DermLIP (zero-shot)`) |

**Recall por clase en test (media ± sd, 3 semillas)** — base de `tab:res_recall_clase`:

| Modelo | MEL | NV | BCC | AKIEC | BKL | DF | VASC |
|---|---|---|---|---|---|---|---|
| Swin-Tiny | 0.623 ± 0.071 | 0.930 ± 0.016 | 0.710 ± 0.060 | 0.551 ± 0.035 | 0.756 ± 0.041 | 0.549 ± 0.122 | 0.727 ± 0.045 |
| ConvNeXt-Tiny | 0.553 ± 0.042 | 0.943 ± 0.011 | 0.736 ± 0.020 | 0.626 ± 0.051 | 0.689 ± 0.037 | 0.490 ± 0.034 | 0.803 ± 0.026 |
| ViT-B/16 | 0.609 ± 0.072 | 0.932 ± 0.009 | 0.680 ± 0.052 | 0.558 ± 0.059 | 0.677 ± 0.021 | 0.569 ± 0.090 | 0.742 ± 0.052 |
| DenseNet121 | 0.509 ± 0.016 | 0.948 ± 0.007 | 0.571 ± 0.022 | 0.571 ± 0.061 | 0.622 ± 0.031 | 0.353 ± 0.102 | 0.697 ± 0.095 |

Soporte en test: MEL 167, NV 1006, BCC 77, AKIEC 49, BKL 165, DF 17, VASC 22. Con 17 imágenes de DF, una imagen mueve
el recall 0.059; se dice al presentar la tabla.

## Claves de cita

`liu2021swin`, `liu2022convnet`, `huang2018densely`, `dosovitskiy2021image` (al nombrar los modelos en P1, solo si la
sección no los nombra solo con `\ref` a 3.4); `lin2017focal`, `ren2020balanced` (P6). Las pruebas no se citan: se
remite a `sec:met_estadistica`. Todas existen en el `.bib`.

## Decisiones tomadas

- El ensamble va en la misma tabla que los modelos individuales (decisión de la ficha del 26/09).
- Sin la receta anterior de DenseNet121 y ViT-B/16 ni la comparación con el 0.870 «anterior» como iteración (revisión del autor del 18/10, reglas R1–R2 de la ficha del Cap. 3). La fuga se presenta como medida del sesgo (P7), no como historia. Los números de la receta anterior siguen en `densenet_vit_moderna_resul_20261017.md` §4.
- La comparación de pares en P3 se limita a los supervisados; la familia de 21 pares con Holm, a 4.6.

## Qué no va

- Cómo se hizo la partición, cómo se midió la fuga, la receta y el barrido (Cap. 3).
- Lo que la fuga implica para la literatura (4.5 y Cap. 6).
- La calibración (4.6) y la detección de melanoma con umbral (4.9).
- Las ablaciones de la receta: sin fuente; quitadas también de 3.4 (D-E de la ficha del Cap. 3).
- Las corridas de la receta anterior (D-B de la ficha del Cap. 3).

## Preguntas abiertas

1. ¿Va una figura con el F1 macro de validación de las 30 corridas de cada modelo, para mostrar cuánto separa el
   barrido al ganador? Hoy no existe; se puede generar desde `lesion_split_report.json` (`sweep`).
