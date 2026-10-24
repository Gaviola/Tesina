# Ficha 4.5 — Comparación con el estado del arte

**Estado (24/10/2026): redactada sin aprobación previa**, dentro de la reorganización del Cap. 4 que pidió el autor
(ver «Reorganización» en `00-capitulo.md`). Modelo: sección 4.9 de la tesina de Maglione.

Archivo: `Chapters/04-Resultados-Clasificacion/05-estado-del-arte.tex`. Label: `sec:res_estado_arte`. Tabla:
`tab:res_estado_arte`.

## Hilo conductor

Pregunta que responde la sección: ¿dónde quedan estos resultados frente a la literatura, y qué parte de la distancia
se explica por el protocolo?

Viene de: 4.1 (fuga: la partición por imagen sobreestima ~0.07), 4.1.3 (umbral), 4.3 (VLM). Reúne las comparaciones
que antes estaban en 4.1, 4.2 y 4.3. Deja instalado: Swin-Tiny cerca de los trabajos con protocolo comparable, y el
colapso de los generativos también en la literatura.

```
P0  No hay comparación directa (datos, partición, regla de decisión); tab:res_estado_arte   función: orienta
P1  Siete clases: Aboulmira (F1 0.81, partición no informada), Kim (0.780, por imagen) por encima; Gessert (0.636,
    por lesión, ISIC 2019) por debajo; la fuga (~0.07) es del orden de la distancia      función: interpreta
P2  Melanoma: Aboulmira 0.49 con la misma regla; Yao 0.819 eligiendo sobre la prueba; Marchetti 96.8 % / 37.4 %
    sobre biopsiadas → la regla pesa tanto como el modelo                           función: interpreta
P3  VLM: DermLIP 0.561 (sus autores) vs 0.377; DermFM-Zero 0.733; Zeng (solo SkinVL > 50 %); Jiang 1.5–13.4 %
                                                                                   función: interpreta
P4  Cierre                                                                         función: concluye
```

## Claves de cita

`aboulmira2024skinhealthmate`, `kim2025skinsavvy2`, `gessert2020skin`, `yao2022single`, `marchetti2023prospective`,
`yan2025derm1miccv`, `yan2026dermfmzero`, `zeng2025mmskin`, `jiang2026multimodal` (todas ya usadas en el Cap. 2).
Cifras tomadas de `tab:marco_sota_clasificacion`, `tab:marco_sota_vlm` y `tab:marco_sota_vlm_gen`.
