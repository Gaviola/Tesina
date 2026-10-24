# Ficha 4.5 — Discusión de los resultados de clasificación

**Estado (24/10/2026): redactada sin aprobación previa.** El autor pidió escribir el resto del Cap. 4 de una pasada
y revisarlo entero al final (24/10).

Archivo: `Chapters/04-Resultados-Clasificacion/05-discusion.tex`. Label: `sec:res_clasif_discusion`. Sin tablas ni
figuras. Una página (C16).

## Hilo conductor

Pregunta que responde la sección: ¿qué responden los resultados del capítulo a la primera pregunta de investigación, y
qué consecuencia tienen para el *pipeline*?

Viene de: 4.1–4.4 (referencia supervisada, punto de operación de melanoma, VLM, evaluaciones complementarias).
Deja instalado: el diagnóstico del *pipeline* viene del clasificador supervisado; el generador no discrimina, así que
el diagnóstico le llega de afuera (Cap. 5). La discusión que cruza clasificación y generación queda para el Cap. 6.

```
P1  Respuesta a la PI1: no. Los generativos de propósito general no clasifican (≈ azar, colapso), y los controles
    descartan el desbalance y la modalidad. DermLIP muestra que la especialización aporta, pero solo con una cabeza
    entrenada se acerca y queda debajo en F1 macro; los 15 pares con un modelo sin ajuste son significativos
                                                                                          función: interpreta
    ↓ contraste: entre supervisados, la arquitectura pesa menos que el procedimiento y la decisión
P2  Entre supervisados: tres arquitecturas indistinguibles con el mismo procedimiento; lo que más cambia el resultado
    es la semilla en las clases minoritarias, la regla de decisión en melanoma (0.62 → 0.80) y la partición (≈ 0.07)
                                                                                          función: interpreta
    ↓ limitación: todo eso vale dentro de la fuente
P3  Fuera de la prueba: caída en HIBA aun en dermatoscopía, sensibilidad al ruido; calibración buena sin pesos.
    Swin-Tiny es una referencia dentro de HAM10000, no una herramienta validada en otra población  función: limita
→ Transición al Cap. 5: el diagnóstico lo fija Swin-Tiny; el generador, que no discrimina, lo recibe de afuera.
  La discusión transversal, en el Cap. 6.

Se definen acá: nada.
Se retoman de antes (\ref): las cuatro secciones del capítulo, PI1 (sec:intro_objetivos), cascada (sec:met_cascada),
Cap. 5 (cp:res_gen), Cap. 6 (cp:discusion).
Extensión: 4 párrafos, ~1 página.
```

## Decisiones tomadas

- Sin números nuevos: solo cifras ya presentadas en 4.1–4.4, una por afirmación.
- Las limitaciones transversales (una semilla en las pruebas, una sola población externa, Grad-CAM sobre siete
  imágenes) se nombran sin desarrollar; el Cap. 6 las retoma.
