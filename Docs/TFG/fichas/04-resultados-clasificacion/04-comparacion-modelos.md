# Ficha 4.4 — Comparación entre los clasificadores

**Estado (24/10/2026): redactada sin aprobación previa**, dentro de la reorganización del Cap. 4 que pidió el autor
(ver «Reorganización» en `00-capitulo.md`).

Archivo: `Chapters/04-Resultados-Clasificacion/04-comparacion-modelos.tex`. Label: `sec:res_comparacion`. Subsección:
`sec:res_costo_clasificadores` (no `sec:res_costo`, que es del Cap. 5). Figura: `fig:res_resumen`
(`resumen-sensibilidad-macro.pdf`). Tablas: `tab:res_pruebas_vlm` (venía de 4.3), `tab:res_costo_clasificadores`
(venía de 4.4).

## Hilo conductor

Pregunta que responde la sección: puestas en una misma escala, ¿qué separa a las tres familias, es significativo, y
cuánto cuesta ejecutar el clasificador?

Viene de: 4.3 cierra con que ningún VLM sin ajuste se acerca a los supervisados. Deja instalado: los tres niveles
(supervisados, DermLIP, generativos en el azar), los 15 pares significativos y el costo bajo de los clasificadores.

```
P1  fig:res_resumen: tres niveles (supervisados 0.6–0.7; DermLIP 0.5 → nivel supervisado con cabeza; generativos
    en el azar)                                                                  función: describe
    ↓ necesidad: ¿exceden la variación de la muestra?
P2  15 pares con modelo sin ajuste significativos con Holm; tab:res_pruebas_vlm (0.08–0.21 frente a DermLIP, ~0.5
    frente a generativos); 768 / 62; IC de los generativos incluye 1/7; Mini–LLaVA: McNemar sí, IC no
                                                                                 función: describe / interpreta
P3  DermLIP con cabeza: deja de ser sin ajuste y no da el diagnóstico desde el generador   función: interpreta
4.4.1 Costo
P4  tab:res_costo_clasificadores: ≤ 20 ms, < 0.7 GB con lote de 32; parámetros no ordenan el tiempo; TTA duplica
    pasadas; el costo del pipeline lo fija el generador (Cap. 5)                  función: describe
```

## Fuentes

Las de la ficha 4.3 («Pruebas») y la ficha 4.2 («Costo»): `statistical_tests_les_v2.json`,
`densenet_vit_moderna_report.json` (`holm`), `cost/cost_comparison_v3.json`. La figura recalcula la sensibilidad
macro de los generativos con «desconocido» como error y coincide con `tab:res_vlm_generativos`.

## DermLIP con el protocolo oficial (24/10/2026)

`statistical_tests_les_v3.json` (mismo comando que v2, con las predicciones oficiales de DermLIP; con las anteriores
reproduce v2 exactamente). Supervisado − DermLIP en sens. macro: Swin 0.172 [0.116, 0.233], ConvNeXt 0.150 [0.092,
0.211], ViT 0.154 [0.105, 0.209], DenseNet 0.050 [−0.016, 0.120] (n. s.; McNemar 250 / 85, sí). Swin − DermLIP
McNemar 286 / 89. Holm: siguen 15 de 21 significativos (`dermlip/dermlip_oficial_derivados.json`).
