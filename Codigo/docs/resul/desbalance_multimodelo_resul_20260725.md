# Resultado — Desbalance extendido a más arquitecturas (mejora #2, 2.ª tanda)

**Fecha:** 2026-07-25 · **Plan:** [desbalance_multimodelo_plan](../ideas/desbalance_multimodelo_plan_20260721.md) · **Jobs Mendieta 1161112–1161115 (ConvNeXt, COMPLETED); DenseNet 1161532–1161535 (re-enviados, ver nota).**

## Motivación

P2.2 mostró —**solo sobre Swin-Tiny**— que el manejo explícito del desbalance no mejora a la CE-plano. La
mejora #1 (2.ª tanda de `mejoras.md`) pide replicarlo en más arquitecturas para que la conclusión no
dependa de un solo modelo. Se corrió el mismo diseño (mismo recipe `modern`, varía solo la loss, eval con
TTA) sobre **ConvNeXt-Tiny** (CNN moderno) y **DenseNet121** (CNN clásico).

## Resultados — ConvNeXt-Tiny (test HAM10000, n=1503, con TTA)

| Variante | Acc | F1-w | Sens.\ macro | Sens.\ por clase (MEL,NV,BCC,AKIEC,BKL,DF,VASC) |
|----------|:-:|:-:|:-:|:-:|
| **CE-plano (sin manejo)** | **0.912** | **0.910** | 0.824 | 0.76, 0.97, 0.83, 0.73, 0.81, 0.71, 0.95 |
| CE + class-weights | 0.691 | 0.753 | 0.808 | 0.72, 0.65, 0.86, 0.78, 0.76, 0.94, 0.95 |
| Focal γ=2 | 0.803 | 0.840 | **0.842** | 0.66, 0.81, 0.94, 0.80, 0.81, 0.88, 1.00 |
| Balanced Softmax | 0.783 | 0.826 | 0.834 | 0.77, 0.78, 0.83, 0.84, 0.74, 0.88, 1.00 |

**Recordatorio — Swin-Tiny (P2.2):** CE-plano acc **0.923** / f1-w **0.923** / sens.\ macro **0.887**
(mejor en las tres); class-weights $0.795$, Focal $0.857$, Balanced Softmax $0.857$.

## Análisis

1. **La CE-plano vuelve a ser la mejor opción global.** En ConvNeXt domina claramente en \emph{exactitud}
   ($0.912$) y \emph{F1-w} ($0.910$), muy por encima de todas las variantes de re-balanceo. Igual que en
   Swin, no hace falta manejo explícito del desbalance para tener un clasificador fuerte y equilibrado.
2. **Las \emph{class-weights} degradan en ambas arquitecturas.** Swin $0.923\to0.795$ acc; ConvNeXt
   $0.912\to0.691$ acc: sobre-corregir la frecuencia empuja las predicciones lejos de la clase mayoritaria
   más de lo conveniente. Patrón consistente.
3. **El único matiz: en ConvNeXt, Focal sube apenas la sensibilidad macro** ($0.824\to0.842$, $+0.018$),
   pero \emph{a un costo grande de exactitud} ($0.912\to0.803$, $-0.109$). No es un almuerzo gratis: la
   pequeña mejora en la métrica balanceada se paga con $11$ puntos de exactitud. En Swin ni siquiera había
   esa mejora (CE ganaba las tres métricas).
4. **Conclusión transversal a las dos arquitecturas (transformer + CNN):** el manejo explícito del
   desbalance no compensa —o directamente empeora—; el clasificador con recipe \emph{modern} ya aprende
   bien las clases minoritarias. El desbalance de HAM \textbf{no es el cuello de botella}, no importa la
   arquitectura.

## Resultados — DenseNet121 (test HAM10000, n=1503, con TTA)

| Variante | Acc | F1-w | Sens.\ macro | Sens.\ por clase (MEL,NV,BCC,AKIEC,BKL,DF,VASC) |
|----------|:-:|:-:|:-:|:-:|
| **CE-plano (sin manejo)** | **0.876** | **0.870** | **0.738** | 0.55, 0.97, 0.70, 0.73, 0.77, 0.71, 0.73 |
| Balanced Softmax | 0.629 | 0.701 | 0.735 | 0.63, 0.61, 0.75, 0.82, 0.53, 0.88, 0.91 |
| CE + class-weights | 0.563 | 0.652 | 0.735 | 0.63, 0.48, 0.77, 0.69, 0.78, 0.88, 0.91 |
| Focal γ=2 | 0.564 | 0.658 | 0.725 | 0.59, 0.50, 0.70, 0.73, 0.70, 0.88, 0.95 |

**Nota de proceso:** los 4 jobs de DenseNet fallaron en Mendieta (nodos offline → torchvision no pudo bajar
los pesos ImageNet, `Network is unreachable`). Se re-enviaron a **TOKO** (jobs 97086–97089, COMPLETED), que
ya tenía los pesos cacheados.

**DenseNet es el caso más limpio:** la CE-plano **gana las tres métricas** (acc 0.876, f1-w 0.870, sens
macro 0.738), y el re-balanceo **desploma la exactitud** (0.876 → 0.56–0.63) a cambio de **cero** ganancia
en sensibilidad macro (0.738 → 0.725–0.735).

## Conclusión (veredicto)

**CUMPLE (completo, 3 de 3 arquitecturas).** El hallazgo se sostiene en las tres familias:
- **Swin (transformer):** CE-plano gana las tres métricas (sens 0.887).
- **ConvNeXt (CNN moderno):** CE-plano gana acc/F1; Focal sube la sens macro apenas (+0.018) a costa de −11
  pts de exactitud.
- **DenseNet (CNN clásico):** CE-plano gana las tres; el re-balanceo destroza la exactitud por ~0 de sens.

En las tres, **el manejo explícito del desbalance no compensa** (class-weights siempre degrada; Focal, en
el mejor caso, un intercambio desfavorable). El clasificador con recipe moderno ya aprende bien las clases
minoritarias: **el desbalance de HAM no es el cuello de botella, sin importar la arquitectura.** Se integra
a `experimentacion.tex` (Cuadro `tab:desbalance` extendido a las 3 arquitecturas).
