# Ficha 6.3 — La concordancia como predicción selectiva

Archivo: `Chapters/06-Discusion/03-concordancia-selectiva.tex`. Label: `sec:disc_concordancia`.

## Hilo conductor

Pregunta: ¿por qué funciona la concordancia como señal de confianza, dónde falla y qué significa para el uso clínico?
Viene de: 6.2 (la señal tiene que venir de fuera del generador). Deja instalado: el pipeline ordena la atención del
especialista, no la reemplaza.

```
P1  Ruteo = clasificador selectivo (2.4): cobertura 0.80, riesgo 0.085 frente a 0.153, sin umbral en la prueba interpreta
P2  Por qué funciona: predictores de sesgo distinto; 72 y 171 desacuerdos útiles                              interpreta
P3  Pero coinciden en el error: 158 imágenes frente a ~50 si fueran independientes; comparten los 6 447
    casos de entrenamiento → conjetura; una señal más independiente no se evaluó                            conjetura
P4  Tensión clínica: la consistencia hereda la exactitud (domina NV); melanoma: 38 afirmados como otra
    clase; el umbral no se usa en el ancla                                                                 implica
P5  Derivación y diferencial convierten errores en duda explícita; valor según el costo relativo →
    apoyo, no reemplazo (jiang); khan deriva sin informar cobertura                                       cierra
```

Fuentes: `sec:marco_pred_selectiva`, `sec:marco_concordancia`, `sec:met_ruteo`, `sec:res_gen_concordancia`,
`sec:res_gen_rag`, `sec:res_gen_pipeline`, `sec:res_melanoma`, `sec:res_calibracion`, `sec:res_gen_estado_arte`.
Citas: `geifman2017selective`, `jiang2026multimodal`, `khan2025ensemble`.
