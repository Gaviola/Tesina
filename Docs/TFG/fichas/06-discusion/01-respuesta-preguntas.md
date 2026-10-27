# Ficha 6.1 — Respuesta a las preguntas de investigación

Archivo: `Chapters/06-Discusion/01-respuesta-preguntas.tex`. Label: `sec:disc_preguntas`. Sin números nuevos.

## Hilo conductor

Pregunta: ¿cuál es la respuesta a PI1 y PI2 con la evidencia de los dos capítulos?
Viene de: los balances 4.6 y 5.6. Deja instalado: las dos respuestas y su encadenamiento.

```
P1  PI1: ningún VLM sin cabeza entrenada alcanza a los supervisados; generativos al azar; DermLIP
    0.15–0.18 debajo (bootstrap excluye 0); melanoma: DermLIP la mitad, Swin 3/5 y 4/5           responde
     ↓ contraste
P2  Matiz: DermLIP con cabeza se acerca, pero ya es un supervisado con otra representación       limita
     ↓ adición
P3  PI2: sin anclaje no; cascada = exactitud (0.849); ruteo 0.870; descripción verificada en parte responde
     ↓ consecuencia
P4  Las respuestas se encadenan: PI1 negativa → diagnóstico del clasificador → PI2 en su medida   interpreta
→ Transición: qué explica la primera, qué implica la segunda, hasta dónde llegan las métricas.
```

Fuentes: `sec:res_comparacion` (`tab:res_pruebas_vlm`), `tab:res_dermlip`, `tab:res_estado_arte` (sensibilidad de
melanoma de Swin-Tiny: 0.623 y 0.796), `tab:res_gen_cascada`, `tab:res_gen_pipeline`, `sec:res_gen_ablaciones`.
