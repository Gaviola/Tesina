# Ficha 6.4 — Datos, evaluación y escala como límites del desempeño

Archivo: `Chapters/06-Discusion/04-datos-evaluacion-escala.tex`. Label: `sec:disc_limites`.

## Hilo conductor

Pregunta: si el reporte hereda el desempeño del clasificador, ¿qué limita ese desempeño, y cuánto es escala?
Viene de: 6.3. Deja instalado: la restricción de cómputo es compatible con la fidelidad; qué deja fuera (para 6.5).

```
P1  La arquitectura y el tamaño pesan poco (tres arquitecturas iguales, ViT ×3 no mejora, ensamble ≈ media)
    → conjetura: el límite lo ponen los datos                                                             conjetura
P2  Las decisiones de evaluación mueven las cifras en el mismo orden: partición, regla, variación entre
    ejecuciones → condiciones para comparar con la literatura (kim, yao)                                  interpreta
P3  Al medir: McNemar y bootstrap responden preguntas distintas; texto: estilo y enumeración             interpreta
P4  Escala: costo del pipeline frente a la literatura; clasificación no, contrastivo sí (DermFM-Zero),
    generación: el tamaño no ordena la fidelidad; cota del oracle                                        interpreta
P5  La restricción es compatible con la fidelidad; deja fuera generadores grandes (no evaluados) y
    preentrenamiento contrastivo a escala                                                                limita
```

Fuentes: `sec:res_sup_arquitecturas`, `sec:res_sup_clases`, `sec:res_melanoma`, `sec:res_fuga`,
`sec:res_comparacion`, `sec:res_estado_arte`, `sec:res_gen_nivel1`, `sec:res_gen_sin_anclaje`,
`sec:res_gen_estado_arte`, `sec:res_costo_clasificadores`, `sec:res_costo`, `sec:res_gen_comparacion`,
`tab:marco_generadores`. Citas: `kim2025skinsavvy2`, `yao2022single`, `khan2025ensemble`, `yan2026dermfmzero`.
