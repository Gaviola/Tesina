# Ficha 6.3 — División de trabajo entre clasificador y generador

Archivo: `Chapters/06-Discusion/03-clasificador-generador.tex`. Label: `sec:disc_division`.

## Hilo conductor

Pregunta: ¿qué aporta cada componente y qué implica para diseñar y evaluar sistemas de generación de reportes?
Viene de: 6.2 (el diagnóstico sale de un supervisado). Deja instalado: la redacción no indica si el diagnóstico es
correcto.

```
P1  El reparto medido: consistencia = exactitud de la fuente (Swin y DermLIP), también por clase;
    sin imagen no cambia; con diagnóstico equivocado casi siempre lo afirma                       interpreta
     ↓ consecuencia
P2  Diseño: la fidelidad se mejora en el clasificador (+0.132); evaluación: medir por separado    justifica
     ↓ ampliación
P3  Ruteo = tercera tarea: 0.849 → 0.870, atribuible al ruteo; LLaVA-Med puede restar              interpreta
     ↓ consecuencia
P4  Decisiones respaldadas (ancla, Mini-VLM, control, recuperación fuera del ruteo)               justifica
     ↓ contraste
P5  Costo del reparto: el error llega verosímil → 6.4                                             limita
```

Integra 4.6 p4 y 5.6 p3–p4. «Toda la ganancia proviene» se reemplaza por «puede atribuirse».
