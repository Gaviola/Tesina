# Ficha 4.4 — Evaluaciones complementarias de la clasificación

**Estado (24/10/2026): redactada sin aprobación previa.** El autor pidió escribir el resto del Cap. 4 de una pasada
y revisarlo entero al final (24/10). Las decisiones que se habrían consultado están en «Decisiones tomadas».

Archivo: `Chapters/04-Resultados-Clasificacion/04-evaluaciones-complementarias.tex`. Label: `sec:res_complementarios`.
Subsecciones: `sec:res_hiba`, `sec:res_robustez`, `sec:res_calibracion`, `sec:res_interpretabilidad`,
`sec:res_costo_clasificadores` (no `sec:res_costo`, que es del Cap. 5 y lo usa el Cap. 6). Tablas: `tab:res_hiba`,
`tab:res_robustez`, `tab:res_calibracion`, `tab:res_costo_clasificadores`. Figura: `fig:res_gradcam`
(`Figures/Capitulos/04-Resultados-Clasificacion/gradcam-swin.pdf`).

## Hilo conductor

Pregunta que responde la sección: ¿se sostiene el desempeño del clasificador cuando cambian la población o la
calidad de la imagen, cuánto se puede confiar en sus probabilidades, en qué se apoya y cuánto cuesta ejecutarlo?

Viene de: 4.3 cierra con que el diagnóstico lo fija un supervisado, pero todo se midió en la prueba de *HAM10000*. Del
Cap. 3: las cinco evaluaciones (`sec:met_hiba`, `sec:met_robustez`, `sec:met_calibracion`,
`sec:met_interpretabilidad`, `sec:met_costo`), los modelos de semilla 42 y el entorno (`sec:met_entorno`).
Deja instalado: la caída en otra población (≈ 0.25–0.29 de sensibilidad macro), la sensibilidad al ruido, que las
probabilidades sin pesos ya están calibradas (y que los pesos por clase las arruinan), que Grad-CAM cae sobre la lesión
en seis de siete casos, y que los clasificadores corren en menos de 1 GB y 14 ms por imagen. 4.5 los usa en la
discusión; el Cap. 5 usa la calibración en el ruteo y el costo frente al de los generadores.

```
P0  Intro: el diagnóstico viene del supervisado, pero la prueba comparte fuente con el entrenamiento; las cinco
    evaluaciones cambian esa condición; Swin y ConvNeXt de semilla 42                    función: orienta
    ↓ necesidad: primero, otra población
4.4.1 HIBA
P1  tab:res_hiba: Swin 0.716 → 0.424, ConvNeXt 0.694 → 0.447 de sensibilidad macro. Dermatoscópicas 0.494 / 0.519;
    clínicas 0.236 / 0.263                                                               función: describe
    ↓ ampliación: por clase, dónde está la caída
P2  NV se sostiene (0.93); AKIEC cae a 0.113 / 0.077 (mapeo del carcinoma escamoso, declarado en 3.8); BCC 0.309 /
    0.385; MEL 0.455 / 0.435. Aun en dermatoscopía la caída es de ~0.2: no es solo la modalidad. Ningún trabajo del
    Cap. 2 evalúa en población latinoamericana                                           función: interpreta / limita
    ↓ contraste: sin cambiar de población, ¿qué pasa si empeora la imagen?
4.4.2 Robustez
P3  tab:res_robustez (caída relativa en los niveles 1, 3 y 5): leve en JPEG, desenfoque y resolución en el nivel 1
    (≤ 0.11); el ruido es la más dañina (0.18 / 0.24 ya en el nivel 1; en el 5 llega al azar). ConvNeXt soporta
    mejor la baja resolución (0.374 frente a 0.644 en el nivel 5) y el desenfoque              función: describe / interpreta
    ↓ ampliación: además de acertar, la probabilidad tiene que ser confiable
4.4.3 Calibración
P4  tab:res_calibracion: sin calibrar, ECE 0.040 en los dos y confianza media menor que la exactitud (T < 1).
    Temperature scaling baja el ECE a 0.027 sin cambiar predicciones; vector scaling lo baja a 0.014 en Swin pero
    cambia predicciones y baja la sensibilidad macro (0.716 → 0.675). Con pesos por clase, ECE 0.376 / 0.211 y
    confianza media de ~0.4 frente a exactitud 0.775 / 0.599                              función: describe / interpreta
    ↓ ampliación: de cuánto confía a en qué se apoya
4.4.4 Interpretabilidad
P5  fig:res_gradcam: en cinco de siete aciertos la activación cae sobre la lesión; el BCC confundido con MEL también
    sobre la lesión; el VASC confundido con NV, difusa sobre la piel. Inspección cualitativa (3.8)  función: interpreta
    ↓ ampliación: cuánto cuesta ejecutarlo
4.4.5 Costo
P6  tab:res_costo_clasificadores: los cuatro, menos de 1 GB y entre 4.83 y 13.19 ms por imagen; Swin 670.7 img/s
    con lotes de 32. La cantidad de parámetros no ordena el tiempo (DenseNet, el más chico, el más lento por
    imagen). Dentro de la restricción de una GPU de consumo con margen                     función: describe
→ Transición a 4.5: con la clasificación evaluada dentro y fuera de la prueba, la discusión reúne qué responden estos
  resultados.

Se definen acá: nada nuevo (todas las métricas y procedimientos están en 2.6 y 3.8).
Se retoman de antes (\ref): las cinco subsecciones de 3.8, ECE y Brier (sec:marco_eval_calib), caída relativa
(eq:marco_robustez), Grad-CAM (sec:marco_eval_gradcam), TTA, entorno (sec:met_entorno).
Extensión: 7 párrafos, 4 tablas y 1 figura, ~5 páginas.
```

## Fuentes de cada número

Todo en `Codigo/outputs/results/`.

- *HIBA*: `hiba_por_modalidad.json` (total 1 616, dermatoscópicas 1 270, clínicas 346); por clase, recalculado de
  `{swin_tiny_sweep_t06,convnext_tiny_sweep_t02}_les_cwnone_hiba_predictions_hiba.json`. F1 macro 0.419 / 0.435.
  Sensibilidad por clase Swin / ConvNeXt: MEL 0.455 / 0.435, NV 0.930 / 0.922, BCC 0.309 / 0.385, AKIEC 0.113 /
  0.077, BKL 0.432 / 0.477, DF 0.279 / 0.361, VASC 0.451 / 0.471. Referencia en *HAM10000* (semilla 42, con TTA):
  `statistical_tests_les_v2.json` (`bootstrap_ci`), 0.716 / 0.694.
- Robustez: `robustness/robustness_summary.json`; niveles de `scripts/robustness_perturbations.py` (JPEG 70, 50, 30,
  15, 5; ruido 8, 16, 32, 48, 64; desenfoque 1, 2, 3, 4, 6; resolución 0.75, 0.5, 0.35, 0.25, 0.15). Base sin TTA:
  0.700 / 0.680. Caídas relativas (niveles 1 / 3 / 5): Swin JPEG 0.081 / 0.176 / 0.748, ruido 0.184 / 0.685 / 0.796,
  desenfoque 0.102 / 0.592 / 0.713, resolución 0.046 / 0.258 / 0.644; ConvNeXt JPEG 0.065 / 0.217 / 0.769, ruido
  0.244 / 0.725 / 0.790, desenfoque 0.108 / 0.284 / 0.599, resolución 0.044 / 0.094 / 0.374.
- Calibración: `lesion_split_report.json` (`calibracion`) y `calibration_les/calibration_summary.json` (con pesos).
  Swin sin calibrar ECE 0.040, Brier 0.233, sens. m 0.716; TS 0.027 / 0.234 / 0.716 (T = 0.850); VS 0.014 / 0.216 /
  0.675. ConvNeXt 0.040 / 0.231 / 0.694; TS 0.027 / 0.231 / 0.694 (T = 0.859); VS 0.033 / 0.226 / 0.687. Con pesos:
  Swin 0.376 / 0.609, sens. m 0.770, exactitud 0.775, confianza media 0.414; ConvNeXt 0.211 / 0.636, 0.742, 0.599,
  0.389. Sin pesos: confianza media 0.820 / 0.809 frente a exactitud 0.847 / 0.845.
- Interpretabilidad: `interpretability_les/interpretability_swin.png` (Swin semilla 42, la primera imagen de cada clase
  en la prueba; `scripts/interpretability.py`). Se recortó el título interno.
- Costo: `cost/cost_comparison_v2.json` (RTX 4070, lote 1 para la latencia y 32 para el rendimiento, una pasada sin
  TTA).

## Claves de cita

Ninguna nueva. La comparación con la literatura en *HIBA* es con la síntesis del Cap. 2 (`sec:estado_arte_diagnostico`),
sin cita.

## Decisiones tomadas

- **Sin figura de robustez**: la tabla con los niveles 1, 3 y 5 alcanza; `robustness_curves.png` es de septiembre y
  trae los cinco niveles.
- **Sin diagrama de confiabilidad**: `reliability_diagrams.png` existe, pero la tabla y la confianza media alcanzan.
- **Figura de Grad-CAM tal como la genera el script**, con el título recortado. Los rótulos de los paneles dicen
  «Swin Grad-CAM (pred X)», en inglés abreviado; ver pregunta 1.
- **Costo solo de los clasificadores** (C17); los generadores van al Cap. 5.
- El costo no se compara con números de la literatura: el Cap. 2 da el hardware de entrenamiento, no tiempos de
  inferencia. Se remite a `tab:marco_brechas` solo en el Cap. 5.

## Preguntas abiertas

1. ¿Regenerar la figura de Grad-CAM con rótulos en castellano («predicción: BKL»)? Requiere correr
   `scripts/interpretability.py` con el *checkpoint* de Swin (funciona en CPU).

## Revisión del autor (24/10/2026)

- Pregunta 1 resuelta: la figura de Grad-CAM se regeneró con rótulos en castellano
  (`Codigo/scripts/figura_gradcam_tesina.py`, mismas imágenes y mapas que `interpretability_swin.png`).
- **Costo remedido (24/10, `cost/cost_comparison_v3.json`).** `measure_cost.py` estimaba la memoria (parámetros × 4
  bytes + 0.5 GB) e instanciaba los modelos de torchvision con la cabeza de 1 000 clases, en fp32 (DenseNet 8.0 M en
  lugar de 6.96 M). Los logs de los jobs no registran el pico de memoria: solo un `nvidia-smi` al arrancar, con la GPU
  vacía. Ahora el script usa las clases del proyecto (cabeza de 7 salidas; los parámetros coinciden con
  `tab:met_modelos_sup`), autocast bf16 como `tta.py`, y mide el pico con `torch.cuda.max_memory_allocated` con una
  imagen y con lotes de 32. Una segunda corrida (`cost_comparison_v3_rep.json`) da la misma memoria y tiempos entre
  5 % y 15 % distintos; se informa la primera. Se agregó la memoria a 3.8 y la precisión a 3.9.
- **HIBA:** 158 de las 221 imágenes de AKIEC son carcinomas escamosos (`data/raw/HIBA/metadata.csv`), dato que
  también da `experimentacion.tex`. El cuerpo de ese documento dice que las 1 616 imágenes son dermatoscópicas; según
  `hiba_por_modalidad.json` son 1 270 dermatoscópicas y 346 clínicas, como dice 3.8.
- Verificación del resto contra la tabla «Vigente» de `experimentacion.tex`: HIBA 0.546 / 0.424, ECE 0.040 y caída
  por ruido como la más dañina coinciden.
