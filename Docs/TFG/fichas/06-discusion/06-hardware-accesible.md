# Ficha 6.6 — Viabilidad en hardware accesible

Archivo: `Chapters/06-Discusion/06-hardware-accesible.tex`. Label: `sec:disc_hardware`.

## Hilo conductor

Pregunta: ¿cumple el pipeline la restricción de una GPU de consumo, y qué parte de la brecha con el SOTA es escala?
Viene de: 6.5. Deja instalado: lo que la restricción deja fuera (para 6.7).

```
P1  Costo medido: clasificador ms y < 0.7 GB; Mini-VLM 8.6 GB, ~16 s; ajuste 9 h en 24 GB          responde
P2  Cómputo de la literatura (8 RTX 4090, 8 RTX 3090, 8 A100, 4 H100, 70B por API)                 compara
P3  Clasificación: la brecha es del orden de la partición, no de escala; contrastivo: sí (DermFM-Zero) interpreta
P4  Generación: el tamaño no ordena la fidelidad; conjetura con el oracle                          interpreta
P5  La restricción es compatible con la fidelidad; deja fuera generadores grandes y preentrenamiento limita
```

Fuentes: `tab:res_costo_clasificadores`, `tab:res_costo_generadores`, `tab:marco_generadores`, 2.7.2 (PanDerm y
DermFM-Zero, cuatro H100; 0.733 frente a 0.561). Citas: `khan2025ensemble`, `yan2026dermfmzero`.
