# Ficha 3.9 — Diseño de los experimentos

**Creada el 26/10/2026 por la revisión del tutor de los Caps. 4–5** (audio 7, `feedback/cap4_5/feedback_cap_4_5.md`):
la configuración de los experimentos quedaba suelta al final de 3.8. Archivo:
`Chapters/03-Materiales-Metodos/09-diseno-experimental.tex`. Label: `sec:met_diseno`. Recibe de 3.8 el párrafo y la
tabla `tab:met_experimentos`; el entorno pasa a 3.10 (`10-entorno-experimental.tex`).

**Decisión (26/10/2026):** sección nueva y no una subsección de 3.8, porque la tabla reúne todos los experimentos (no
solo los complementarios) y tiene que ir después de 3.8. No agrega experimentos ni resultados: los ordena por etapas y
dice cuántas ejecuciones tiene cada configuración, que el tutor pidió y no estaba. Sin números de semilla (van en
3.10).

## Hilo conductor

Pregunta que responde la sección: ¿en qué orden se hacen los experimentos, qué usa cada uno de los anteriores y
cuántas veces se ejecuta cada configuración?
Viene de: 3.8 cierra con que quedan definidos todos los experimentos y falta ordenarlos.
Deja instalado: el orden de los Caps. 4 (imágenes) y 5 (reportes); el *pipeline* interviene solo en los reportes.

```
P1  Los experimentos se organizan por etapas en dos partes: imágenes (produce el clasificador) y reportes
    (lo usa como primer componente del pipeline)                                     define
    ↓ ampliación
L1  Imágenes, cuatro etapas: búsqueda → comparación de supervisados (ensamble, umbral) → variantes y
    evaluaciones complementarias → VLM como clasificadores                         describe
    ↓ ampliación
L2  Reportes, tres etapas: generador solo → cascada (fuentes, ablaciones, recuperación) → pipeline completo
                                                                                    describe
    ↓ necesidad — cuántas veces se ejecuta cada configuración
P2  Ejecuciones: búsqueda y pérdidas, una; supervisados, tres (media ± desvío); VLM, cabezas y generadores,
    una por configuración (deterministas); cada generador se ajusta una vez         justifica
P3  Tabla tab:met_experimentos y remisión a los Caps. 4 y 5                         cierra
```
