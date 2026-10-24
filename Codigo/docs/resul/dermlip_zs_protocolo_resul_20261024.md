# Resultado — DermLIP zero-shot con el protocolo oficial (24/10/2026)

Plan: [dermlip_zs_protocolo_plan_20261024.md](../ideas/dermlip_zs_protocolo_plan_20261024.md). Script:
`scripts/dermlip_zs_protocolo.py` (local, RTX 4070, `.venv` de la raíz). Salida:
`outputs/results/dermlip/dermlip_zs_protocolo.json`. Prueba por lesión, 1 503 imágenes.

| Plantillas × nombres | Exactitud | Sens. macro | F1 macro | Clase más predicha |
|---|---|---|---|---|
| propias × propios (control) | 0.377 | 0.510 | 0.363 | MEL (0.526) |
| propias × oficiales | 0.679 | 0.506 | 0.447 | NV (0.588) |
| oficiales × propios | 0.422 | 0.546 | 0.347 | MEL (0.433) |
| oficiales × oficiales | **0.716** | **0.544** | **0.475** | NV (0.655) |

Sensibilidad por clase (MEL, NV, BCC, AKIEC, BKL, DF, VASC): control 0.760 / 0.328 / 0.403 / 0.735 / 0.103 / 0.471 /
0.773; oficial 0.503 / 0.887 / 0.377 / 0.796 / 0.048 / 0.471 / 0.727.

## Lectura

- El control reproduce la evaluación de la tesina (0.377 / 0.510; F1 0.363 frente a 0.364 por redondeo).
- La diferencia con Derm1M (0.682) es de **protocolo**, no del conjunto de prueba: con las plantillas y los nombres
  oficiales, sobre nuestra prueba DermLIP llega a 0.716 de exactitud.
- La causa principal es el nombre de clase: «melanocytic nevus» hace que los nevos se clasifiquen como MEL (sens. de
  NV 0.328); con «nevus», NV sube a 0.887 y la exactitud se duplica. Las plantillas oficiales suman unos 0.04.
- La sensibilidad macro casi no cambia (0.510 → 0.544): el colapso parcial hacia MEL se reemplaza por uno hacia NV, y
  MEL baja de 0.760 a 0.503. Las conclusiones de la tesina (DermLIP sin ajuste muy por encima de los generativos y por
  debajo de los supervisados) no cambian.

## Veredicto

**CUMPLE** (≥ 0.60): la diferencia con la cifra publicada se explica por el protocolo de texto. Decisión del autor
(24/10/2026): la tesina pasa al protocolo oficial. Recalculado en local: *SkinCAP* 0.397 / 0.460; pruebas en
`statistical_tests_les_v3.json` (DenseNet − DermLIP en sens. macro deja de ser significativa); fuga: DermLIP 0.544 en
toda la prueba y 0.575 en el grupo sin fuga (`dermlip/dermlip_oficial_derivados.json`). Pendiente: la condición
`full_dermlip` de la cascada (Cap. 5) usa las predicciones anteriores (`outputs/full_dx_dermlip.csv`).
