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

## Verificación contra los PDF (24/10/2026)

Coinciden: Aboulmira (F1 macro 0.81, MEL 0.49, sin partición informada), Kim (exactitud balanceada 0.780 con Swin;
80 % al azar por clase, imágenes externas), Yao (ISIC 2018: BACC 0.875, MEL 0.819; arquitectura y aumentación elegidas
por BACC en la prueba del desafío), Marchetti (96.8 % / 37.4 %, AUC 0.857, umbral predefinido de 95 % de
sensibilidad), Jiang (1.50–13.35 % abiertos, 24.65 % GPT-4.1). Corregido: (1) Gessert 63.6 % es la prueba oficial de
ISIC 2019; la partición por lesión es de su validación cruzada. (2) Derm1M, Tabla 2: DermLIP ViT-B16 da 0.682 de
exactitud zero-shot en HAM10000 (la media de cuatro conjuntos es 0.561); se compara con esa cifra. Este trabajo
promedia cuatro plantillas (`src/models/dermlip.py`); posible causa de la diferencia, sin verificar. (3) DermFM-Zero:
0.733 frente a 0.561 es la media del «Classification Ranking» (Fig. 2c), que mezcla exactitud balanceada y AUROC, no
exactitud. (4) MM-Skin, Tabla 5: LLaVA-Med sin ajuste 5.49 % en HAM10000, SkinVL-PubMM 51.29 % (HAM no visto en el
entrenamiento); se agregan las dos filas. El Cap. 2 (línea 195 de 07-estado-arte.tex) da 0.733 frente a 0.561 sin
nombrar la métrica: no se tocó.
