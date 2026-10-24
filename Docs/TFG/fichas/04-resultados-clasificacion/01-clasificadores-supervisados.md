# Ficha 4.1 — Clasificadores supervisados

**Estado (24/10/2026): borrador para aprobar.** Reemplaza la del 18/10 con la estructura aprobada del capítulo
(C11–C12): la comparación con la literatura y las pruebas entre supervisados van acá, y las funciones de pérdida y la
fuga de información son subsecciones.

Archivo: `Chapters/04-Resultados-Clasificacion/01-clasificadores-supervisados.tex`. Label: `sec:res_supervisados`.
Subsecciones: `sec:res_desbalance`, `sec:res_fuga`. Tablas: `tab:res_supervisados`, `tab:res_pruebas_supervisados`,
`tab:res_recall_clase`, `tab:res_desbalance`.

## Hilo conductor

Pregunta que responde la sección: ¿cuánto rinde un clasificador supervisado entrenado con *HAM10000* sobre lesiones
que no vio, cuánto depende de la arquitectura, de la semilla y de la función de pérdida, y cuánto se aleja ese número
del que da una partición con fuga?

Viene de: la introducción del capítulo (todo número es de la prueba de la partición por lesión, con la configuración
elegida en validación, y media ± sd con tres semillas). Del Cap. 3: los cuatro modelos y su procedimiento
(`sec:met_supervisados`), el ensamble (`sec:met_supervisados_ensamble`), la selección por F1 macro y la sensibilidad
macro como resultado principal (`sec:met_seleccion`), las referencias de la clasificación (`sec:met_referencias`), las
pruebas (`sec:met_estadistica`) y la comparación anunciada para la fuga (`sec:met_particiones`).
Deja instalado: Swin-Tiny como referencia (sensibilidad macro 0.692 ± 0.025), que la arquitectura pesa poco con el
mismo procedimiento, que el recall de MEL es el más variable, y el orden de magnitud de la sobreestimación por fuga.
4.2 parte del recall de MEL; 4.3 compara los VLM contra estos números.

```
P1  Selección en validación. Swin-Tiny tiene el mayor F1 macro medio en validación de los cuatro (0.781 ± 0.018;
    ConvNeXt 0.740 ± 0.027, ViT 0.740 ± 0.008, DenseNet 0.710 ± 0.011). Con la semilla 42 sola, ConvNeXt queda
    apenas arriba (0.770 frente a 0.766), y por eso la elección usa la media           función: describe
    ↓ consecuencia: elegidas en validación, las configuraciones se leen en la prueba
P2  Tabla principal (tab:res_supervisados): los cuatro y el ensamble, media ± sd en la prueba (exactitud, F1
    ponderado, F1 macro, sensibilidad macro, AUC macro). Swin 0.692 ± 0.025 de sensibilidad macro y 0.846 de
    exactitud, frente a 1/7 del azar y 0.143 / 0.669 del clasificador que responde siempre NV  función: describe
    ↓ contraste: tres de los cuatro tienen medias casi iguales; ¿hay un mejor modelo?
P3  Pruebas entre supervisados (tab:res_pruebas_supervisados, semilla 42): Swin, ConvNeXt y ViT no se distinguen
    (IC del bootstrap de la diferencia de F1 macro y de sensibilidad macro que incluyen el 0; McNemar p = 0.87,
    0.42, 0.57). DenseNet121 queda 0.08–0.12 abajo en F1 macro y sensibilidad macro frente a los otros tres (IC que
    no incluyen el 0), pero no en exactitud ni AUC, y McNemar no supera el umbral de Holm (p = 0.021 y 0.026 frente
    a 0.008 y 0.010). Los seis pares son parte de la familia de 21; el resto va en 4.3    función: interpreta
    ↓ ampliación: si la diferencia de DenseNet está en las métricas macro, está en las clases minoritarias
P4  Sensibilidad por clase (tab:res_recall_clase): NV y BCC altas y estables; MEL, AKIEC y DF bajas y variables
    (DF ± 0.122 en Swin; una imagen de DF mueve 0.059). Comparación descriptiva (sec:met_estadistica): Swin mejora a
    DenseNet en 5 de 7 clases, y frente a ConvNeXt y ViT en 3 de 7. El recall de MEL de Swin va de 0.563 a 0.701
    según la semilla: una sola ejecución no alcanza                                   función: interpreta
    ↓ consecuencia: con esa variación, combinar dos modelos puede estabilizar
P5  Ensamble Swin + ConvNeXt (voto suave, soft voting; \ref): +0.014 de F1 macro y de sensibilidad macro, y el
    desvío de la sensibilidad macro baja de 0.025 a 0.002. Estabiliza más de lo que mejora; no se prueba
    estadísticamente                                                                   función: interpreta
    ↓ ampliación (literatura): ¿dónde quedan estos números frente a los trabajos del Cap. 2?
P6  Comparación con la literatura (tab:marco_sota_clasificacion del Cap. 2): Aboulmira (F1 macro 0.81, sensibilidad
    de MEL 0.49) y Kim (sensibilidad macro 0.780, F1 macro 0.793, con HAM10000 ampliado) informan valores mayores que
    los de Swin; Gessert, con particiones por lesión, informa 0.636 de sensibilidad macro en la prueba de ISIC 2019.
    Los protocolos difieren (datos, partición, clases), así que la comparación ubica el orden de magnitud. La
    partición de cada trabajo explica parte de la diferencia, y 4.1.2 la mide          función: compara / limita
    ↓ contraste: los ganadores no usan pesos por clase; ¿mejora otra función de pérdida las clases minoritarias?

4.1.1 Funciones de pérdida para el desbalance de clases (sec:res_desbalance)
P7  Tabla (tab:res_desbalance, semilla 42, hiperparámetros fijos, \ref al párrafo de 3.3): las tres pérdidas para el
    desbalance suben la sensibilidad macro en los tres modelos (Swin 0.707 → 0.783 con CE ponderada), pero bajan la
    exactitud (0.860 → 0.752) y el F1 macro (0.745 → 0.635), y ninguna supera a la CE sin pesos en F1 macro. El
    recall de MEL no sube de forma consistente (Swin focal 0.503 frente a 0.551 con CE)   función: interpreta
    ↓ consecuencia: más falsas alarmas en las clases minoritarias; por eso la configuración común usa CE sin pesos
    (sin justificar el método con el resultado: el criterio de selección ya estaba en 3.7)
    ↓ ampliación: todos estos números son sin fuga; ¿cuánto cambian con una partición que la tiene?

4.1.2 Efecto de la fuga de información (sec:res_fuga)
P8  Con la comparación de sec:met_particiones: un Swin-Tiny entrenado con la partición por imagen (configuración
    elegida en validación) da 0.870 de sensibilidad macro sobre toda la prueba, 0.804 sobre las 894 imágenes sin
    lesiones compartidas y 0.936 sobre las 543 con fuga. El control, DermLIP sin ajuste, no baja (0.510 en toda la
    prueba, 0.527 en el subconjunto), así que la diferencia se debe a la fuga y no a la composición del subconjunto
                                                                                       función: interpreta
    ↓ consecuencia: una partición por imagen sobreestima la sensibilidad macro en unas 0.07 en esta prueba
P9  Cierre: el orden de magnitud de esa sobreestimación es comparable a la distancia con los trabajos de P6 que no
    informan particiones por lesión; por eso los números de 4.1 no se comparan sin más con ellos  función: limita
→ Transición a 4.2: de las siete clases, MEL es la de mayor costo clínico y la de recall más variable con argmax;
  la sección siguiente la evalúa como tarea binaria con un umbral fijado en validación.

Se definen acá (y no se vuelven a definir): el resultado de referencia del capítulo (Swin 0.692 ± 0.025) y la magnitud
de la sobreestimación por fuga.
Se retoman de antes (solo se nombran, con \ref): modelos y procedimiento (sec:met_supervisados_arquitecturas,
sec:met_supervisados_receta), funciones de pérdida (párrafo de sec:met_supervisados_ensamble), voto suave
(sec:met_supervisados_ensamble), criterio de selección (sec:met_seleccion), referencias (sec:met_referencias),
bootstrap, McNemar y Holm (sec:met_estadistica), subconjunto sin fuga y control (sec:met_particiones).
Extensión: 9 párrafos y 4 tablas, ~6 páginas.
```

## Fuentes de cada número

Todo en `Codigo/outputs/results/` salvo indicación. Verificado el 24/10.

| P | Número | Fuente |
|---|---|---|
| P1 | F1 macro de validación, media ± sd: Swin 0.781 ± 0.018, ConvNeXt 0.740 ± 0.027, ViT 0.740 ± 0.008, DenseNet 0.710 ± 0.011; semilla 42: Swin 0.766, ConvNeXt 0.770 | `densenet_vit_moderna_report.json` (`val_media_std`); `lesion_split_report.json` (`sweep`) |
| P2 | Prueba, media ± sd. Swin: exactitud 0.846 ± 0.002, F1 pond. 0.846 ± 0.004, F1 macro 0.733 ± 0.026, sens. macro 0.692 ± 0.025, AUC 0.953 ± 0.014. ConvNeXt: 0.843 ± 0.005, 0.840 ± 0.005, 0.727 ± 0.007, 0.691 ± 0.009, 0.964 ± 0.001. ViT: 0.836 ± 0.003, 0.836 ± 0.004, 0.707 ± 0.025, 0.681 ± 0.025, 0.956 ± 0.003. DenseNet: 0.822 ± 0.005, 0.815 ± 0.004, 0.655 ± 0.017, 0.610 ± 0.020, 0.957 ± 0.003 | `densenet_vit_moderna_report.json` (`media_std`) |
| P2 | Ensamble: 0.855 ± 0.003, 0.853 ± 0.005, 0.747 ± 0.005, 0.706 ± 0.002 (sin AUC en la fuente) | `classifier_ensemble_les/ensemble_seeds.json` (`resumen`) |
| P2 | Siempre NV: 0.669 / 0.537 / 0.115 / 0.143 | `sec:met_referencias` (Cap. 3) |
| P3 | Diferencias pareadas con IC (F1 macro; sens. macro): Swin−ConvNeXt +0.029 [−0.015, 0.074]; +0.022 [−0.027, 0.071]. Swin−ViT +0.032 [−0.005, 0.070]; +0.018 [−0.019, 0.057]. ConvNeXt−ViT +0.003 [−0.048, 0.053]; −0.004 [−0.057, 0.048]. Swin−DenseNet +0.114 [0.061, 0.170]; +0.122 [0.069, 0.176]. ConvNeXt−DenseNet +0.085 [0.029, 0.146]; +0.100 [0.044, 0.156]. ViT−DenseNet +0.082 [0.019, 0.148]; +0.104 [0.039, 0.167] | `statistical_tests_les_v2.json` (`paired_bootstrap_diff`) |
| P3 | McNemar p y umbral de Holm: Swin–ConvNeXt 0.867 / 0.050; Swin–ViT 0.416 / 0.017; ConvNeXt–ViT 0.573 / 0.025; Swin–DenseNet 0.021 / 0.008; ConvNeXt–DenseNet 0.026 / 0.010; DenseNet–ViT 0.143 / 0.013. Ninguno significativo | `densenet_vit_moderna_report.json` (`holm`) |
| P4 | Sensibilidad por clase, media ± sd (tabla de abajo); recall MEL de Swin por semilla 0.701 / 0.563 / 0.605 | `*_les_cwnone{,_s43,_s44}_test_results.json`; `densenet_vit_moderna_report.json` (`semillas`) |
| P5 | Ensamble frente a Swin | `ensemble_seeds.json` |
| P6 | Aboulmira, Kim, Gessert | `tab:marco_sota_clasificacion` (Cap. 2); verificar la partición de Aboulmira y de Kim en `Papers/` antes de escribir P9 |
| P7 | Tabla de abajo | `lesion_split_report.json` (`legacy_y_desbalance`, `*_imb_*_les`) |
| P8 | Swin t08 (partición por imagen, mejor también en validación): sens. macro 0.870 / 0.804 / 0.936 (toda, 894 sin fuga, 543 con fuga); DermLIP ZS 0.510 / 0.527 / 0.477 | `leakage_analysis.json` (`Swin-Tiny (sweep t08, headline)`, `DermLIP (zero-shot)`); selección en validación: `docs/ejecuciones.md` (auditoría del 12/09) |

**Sensibilidad por clase en la prueba (media ± sd, tres semillas)**, base de `tab:res_recall_clase`:

| Modelo | MEL | NV | BCC | AKIEC | BKL | DF | VASC |
|---|---|---|---|---|---|---|---|
| Swin-Tiny | 0.623 ± 0.071 | 0.930 ± 0.016 | 0.710 ± 0.060 | 0.551 ± 0.035 | 0.756 ± 0.041 | 0.549 ± 0.122 | 0.727 ± 0.045 |
| ConvNeXt-Tiny | 0.553 ± 0.042 | 0.943 ± 0.011 | 0.736 ± 0.020 | 0.626 ± 0.051 | 0.689 ± 0.037 | 0.490 ± 0.034 | 0.803 ± 0.026 |
| ViT-B/16 | 0.609 ± 0.072 | 0.932 ± 0.009 | 0.680 ± 0.052 | 0.558 ± 0.059 | 0.677 ± 0.021 | 0.569 ± 0.090 | 0.742 ± 0.052 |
| DenseNet121 | 0.509 ± 0.016 | 0.948 ± 0.007 | 0.571 ± 0.022 | 0.571 ± 0.061 | 0.622 ± 0.031 | 0.353 ± 0.102 | 0.697 ± 0.095 |

Soporte en la prueba: MEL 167, NV 1006, BCC 77, AKIEC 49, BKL 165, DF 17, VASC 22.
Conteo descriptivo de clases en que cada uno supera al otro (con las medias): Swin–ConvNeXt 3–4, Swin–ViT 3–4,
Swin–DenseNet 5–2, ConvNeXt–ViT 5–2, ConvNeXt–DenseNet 6–1, ViT–DenseNet 5–2.

**Funciones de pérdida (semilla 42, hiperparámetros fijos)**, base de `tab:res_desbalance`
(exactitud / F1 macro / sensibilidad macro / recall MEL):

| Modelo | CE sin pesos | CE ponderada | Focal | Balanced softmax |
|---|---|---|---|---|
| Swin-Tiny | 0.860 / 0.745 / 0.707 / 0.551 | 0.752 / 0.635 / 0.783 / 0.790 | 0.781 / 0.620 / 0.773 / 0.503 | 0.756 / 0.626 / 0.758 / 0.695 |
| ConvNeXt-Tiny | 0.846 / 0.753 / 0.715 / 0.605 | 0.669 / 0.570 / 0.731 / 0.659 | 0.739 / 0.588 / 0.730 / 0.509 | 0.733 / 0.576 / 0.719 / 0.425 |
| DenseNet121 | 0.830 / 0.664 / 0.634 / 0.485 | 0.568 / 0.470 / 0.692 / 0.545 | 0.557 / 0.479 / 0.654 / 0.581 | 0.568 / 0.479 / 0.646 / 0.515 |

## Claves de cita

Solo para comparar (guía §6): `aboulmira2024skinhealthmate`, `kim2025skinsavvy2`, `gessert2020skin` (P6, P9). Los
modelos, la pérdida focal y *balanced softmax* se nombran con `\ref` a 3.3, sin volver a citarlos.

## Decisiones tomadas

- El ensamble va en la misma tabla que los modelos individuales; la diferencia con Swin se describe, no se prueba
  (no está en `tab:met_pruebas`).
- La comparación con la literatura va en 4.1 (C11), y su límite se cierra con la subsección de la fuga (P9).
- La fuga se presenta como medida de la sobreestimación, sin historia de iteraciones. Solo la comparación interna del
  modelo con fuga (toda la prueba frente al subconjunto), que es la que define `sec:met_particiones`; no se compara
  con el Swin de la partición por lesión, que además entrena con 776 imágenes menos.
- P7 no justifica la elección de CE sin pesos con este resultado; la configuración ya se eligió en validación (3.7).

## Qué no va

- Cómo se hizo la partición, la búsqueda y la receta (Cap. 3).
- Detección de melanoma con umbral (4.2), calibración (4.4), los 15 pares restantes de Holm (4.3).
- Las corridas con la receta anterior de DenseNet121 y ViT-B/16 (C1).

## Preguntas abiertas

1. ¿Figura con el F1 macro de validación de las 30 configuraciones de cada modelo? No existe; se puede generar desde
   `lesion_split_report.json` (`sweep`). Propuesta: no, la tabla alcanza.
2. P6 y P9 dependen de qué partición usaron Aboulmira y Kim: si no lo informan, se dice así («no informan una partición
   por lesión») y no se afirma que tengan fuga.

## Redacción (24/10/2026)

Ficha aprobada por el autor el 24/10. Decisiones al redactar:

- **Sin AUC macro** en `tab:res_supervisados`: el Cap. 3 define solo la AUC de melanoma (`tab:met_roles`). P3 dice
  «no en exactitud» en lugar de «ni en exactitud ni en AUC».
- **`tab:res_recall_clase` transpuesta** (clases en filas, con la cantidad de imágenes), para que entre en el ancho.
- **`tab:res_pruebas_supervisados`**: modelos por su familia («Swin», «ConvNeXt»…) y el IC en una segunda línea.
- **`tab:res_desbalance`** con `[!b]` y «EC» por entropía cruzada (se aclara en el epígrafe), para no dejar media
  página en blanco antes de 4.1.1.
- **Partición de los trabajos citados (pregunta 2)**, verificada en `Papers/`: Aboulmira no informa cómo divide; Kim
  separa al azar el 80 % de las imágenes de cada clase sobre su conjunto ampliado. P9 compara con Kim (0.088) y no
  afirma que ninguno tenga fuga.
- P9 quedó separado en dos párrafos: el límite de la comparación y la transición a 4.2.
- Pregunta 1 (figura del barrido): no se hizo.

## Reorganización (24/10/2026)

El autor encontró el capítulo difícil de seguir por la cantidad de cifras y porque cada subsección recorría los
cuatro modelos. Se acordó: (1) las cuatro arquitecturas se comparan una vez y el análisis sigue con Swin-Tiny,
nombrando a las demás solo donde se comportan distinto; (2) como regla, una cifra clave por párrafo y el resto en
tablas y figuras (seis figuras nuevas, `Codigo/scripts/figuras_cap4.py`); (3) una sola sección de comparación con
la literatura (4.5) y una de comparación entre familias con el costo (4.4). Estructura nueva: 4.1 supervisados
(con melanoma), 4.2 evaluaciones complementarias, 4.3 VLM, 4.4 comparación entre clasificadores, 4.5 estado del
arte, 4.6 discusión.

En esta sección: subsecciones `sec:res_sup_arquitecturas`, `sec:res_sup_clases`, `sec:res_melanoma`,
`sec:res_desbalance`, `sec:res_fuga`; figura nueva `fig:res_confusion_swin`. La comparación con Aboulmira, Kim y
Gessert pasó a 4.5. Abajo, la ficha de la antigua 4.2 (melanoma), que ahora es la subsección 4.1.3.

---

# (Antigua) Ficha 4.2 — Detección de melanoma

**Estado (24/10/2026): redactada sin aprobación previa.** El autor pidió escribir el resto del Cap. 4 de una pasada
y revisarlo entero al final (24/10). Las decisiones que se habrían consultado están en «Decisiones tomadas».

Archivo: `Chapters/04-Resultados-Clasificacion/02-deteccion-melanoma.tex`. Label: `sec:res_melanoma`.
Tabla: `tab:res_melanoma`.

## Hilo conductor

Pregunta que responde la sección: ¿cuántos melanomas detecta el clasificador cuando la decisión usa un umbral fijado
en validación, y qué cuesta en falsas alarmas?

Viene de: 4.1 deja la sensibilidad de MEL con argmax como una de las más variables (Swin 0.563–0.701 según la
semilla). Del Cap. 3: la tarea T2 (`sec:met_tareas`), el umbral de mayor sensibilidad con especificidad ≥ 0.850 en
validación y la AUC como resumen (`sec:met_seleccion`), el ensamble (`sec:met_supervisados_ensamble`).
Deja instalado: el punto de operación para melanoma (Swin 0.796 ± 0.036 / 0.862; ensamble 0.828 ± 0.007) y que la
discriminación (AUC) es estable aunque la decisión por argmax no lo sea. 4.3 lo usa como contraste; 4.4 (calibración)
retoma que los umbrales quedan lejos de 0.5.

```
P1  Discriminación: AUC de MEL 0.921 ± 0.005 en Swin, 0.909 ± 0.004 en ConvNeXt, 0.926 ± 0.003 en el ensamble.
    El AUC casi no varía entre semillas, mientras que la sensibilidad con argmax va de 0.563 a 0.701: el modelo
    ordena igual los casos y lo que cambia es dónde cae el corte implícito de la clase más probable  función: interpreta
    ↓ consecuencia: si el orden es estable, fijar el corte en validación debería estabilizar la decisión
P2  Tabla (tab:res_melanoma): argmax frente al umbral de validación. Swin pasa de 0.623 ± 0.071 a 0.796 ± 0.036 de
    sensibilidad y la especificidad baja de 0.944 a 0.862; ConvNeXt de 0.553 a 0.794; ensamble de 0.605 a 0.828.
    La especificidad en la prueba queda entre 0.844 y 0.862 en todas las ejecuciones: el umbral fijado en
    validación se sostiene en la prueba                                                   función: describe
    ↓ ampliación: qué significa en casos, con la ejecución de semilla 42
P3  Semilla 42 de Swin: el umbral 0.211 detecta 130 de 167 melanomas (117 con argmax) a cambio de 185 falsas alarmas
    (104). Los umbrales de las nueve ejecuciones quedan entre 0.109 y 0.211, lejos del 0.5: con una prevalencia de
    0.111, la probabilidad de MEL rara vez supera a la de NV. El ensamble tiene la mayor sensibilidad y el menor
    desvío (0.828 ± 0.007), sin prueba estadística                                       función: interpreta
    ↓ ampliación (literatura)
P4  Literatura (tab:marco_sota_clasificacion): Aboulmira, sensibilidad de MEL 0.49 con la clase más probable, por
    debajo del 0.623 de Swin con argmax; Yao 0.819 en ISIC 2018 (con selección sobre la prueba, Cap. 2); Marchetti,
    96.8 % / 37.4 % y AUC 0.857 sobre lesiones biopsiadas, otro punto de operación y otra población. La comparación
    muestra que el punto de operación cambia la sensibilidad más que el modelo                función: compara / limita
→ Transición a 4.3: con la referencia supervisada fijada para las siete clases y para MEL, la pregunta es si un VLM
  clasifica igual.

Se definen acá: el punto de operación para melanoma.
Se retoman de antes (\ref): T2 (sec:met_tareas), umbral y AUC (sec:met_seleccion), ensamble
(sec:met_supervisados_ensamble), sensibilidad de MEL con argmax (sec:res_supervisados).
Extensión: 4 párrafos y una tabla, ~2 páginas.
```

## Fuentes de cada número

`Codigo/outputs/results/lesion_split_report.json`, claves `melanoma_semillas` (`por_semilla`, `media_std`) y
`melanoma` (semilla 42). Solo Swin-Tiny, ConvNeXt-Tiny y el ensamble tienen la detección con umbral: son los modelos
de la búsqueda y su combinación (3.3).

| Modelo | AUC | Sens. argmax | Esp. argmax | Sens. umbral | Esp. umbral | Umbrales (42/43/44) |
|---|---|---|---|---|---|---|
| Swin-Tiny | 0.921 ± 0.005 | 0.623 ± 0.071 | 0.944 ± 0.022 | 0.796 ± 0.036 | 0.862 ± 0.000 | 0.211 / 0.120 / 0.152 |
| ConvNeXt-Tiny | 0.909 ± 0.004 | 0.553 ± 0.043 | 0.953 ± 0.007 | 0.794 ± 0.012 | 0.854 ± 0.009 | 0.120 / 0.109 / 0.112 |
| Ensamble | 0.926 ± 0.003 | 0.605 ± 0.057 | 0.952 ± 0.012 | 0.828 ± 0.007 | 0.852 ± 0.006 | 0.177 / 0.110 / 0.144 |

Semilla 42, Swin: umbral 0.211, VP 130, FN 37, FP 185 (argmax: VP 117, FN 50, FP 104). Especificidad en la prueba
por ejecución: mínima 0.844 (ConvNeXt, 42), máxima 0.862.

## Claves de cita

Solo para comparar: `aboulmira2024skinhealthmate`, `yao2022single`, `marchetti2023prospective` (valores de
`tab:marco_sota_clasificacion`).

## Decisiones tomadas

- **Sin ViT-B/16 ni DenseNet121**: la detección con umbral se calculó para los modelos de la búsqueda y el ensamble.
  Se dice en una oración.
- **Sin PR-AUC ni VPN**, aunque están en la fuente: el Cap. 3 no las define (`tab:met_roles`).
- **Sin maligno frente a benigno** (C4).
- La diferencia entre Swin y el ensamble se describe, no se prueba (`tab:met_pruebas` no la incluye).
- El umbral bajo se explica por la prevalencia, sin adelantar la calibración (4.4 la retoma).

## Preguntas abiertas

1. ¿Agregar la curva ROC de Swin con los dos puntos de operación? No existe la figura; se puede generar con las
   probabilidades de la semilla 42. Por ahora, la tabla alcanza.

## Revisión del autor (24/10/2026)

- Pregunta 1 resuelta: se agregó `fig:res_roc_melanoma` (`Figures/Capitulos/04-Resultados-Clasificacion/roc-melanoma-swin.pdf`,
  generada con `Codigo/scripts/figura_roc_melanoma.py`), con los dos puntos de operación de la semilla 42. Recalcula
  AUC 0.919, 0.701 / 0.922 y 0.778 / 0.862, iguales a `lesion_split_report.json`.
- Verificación contra `Docs/experimentacion/experimentacion.tex`: coincide con la tabla «Vigente» (Swin 0.921 / 0.796;
  ensamble 0.926 / 0.828). El cuerpo de ese documento usa la partición por imagen y no se toma.
