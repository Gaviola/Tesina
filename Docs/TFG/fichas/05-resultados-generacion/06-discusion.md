# Ficha 5.6 — Discusión de los resultados de generación

**Estado (25/10/2026): reescrita alrededor del pipeline con la revisión del autor del 25/10** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/06-discusion.tex`. Label: `sec:res_gen_discusion`. Tabla nueva:
`tab:res_gen_aportes`. Sin números nuevos.

## Hilo conductor

Pregunta: ¿qué responden los resultados sobre la PI2 y qué aporta el pipeline, el aporte principal del trabajo?
Viene de: 5.1–5.5, que agregaron un componente por vez. Deja instalado (para el Cap. 6): qué aporta y qué no cada
componente; las decisiones respaldadas; lo que queda abierto (errores compartidos, umbral de melanoma en el ancla,
sin especialistas, una semilla en el ancla).

```
P1  PI2 en sus dos partes, breve: diagnóstico (sin anclaje no; con cascada = exactitud de Swin);
    descripción (varía con la imagen, sin verificar; se adapta al diagnóstico)                   responde
P2  Cada sección agregó un componente → tab:res_gen_aportes (aporta / no aporta / secciones)       organiza
P3  El reparto es el aporte: separa qué afirmar de si afirmarlo; 0.849 → 0.870 sobre 1 503, toda la
    ganancia del ruteo (pipeline = línea base sin generador); medible por separado, a diferencia
    de la literatura                                                                              interpreta
P4  Decisiones respaldadas: ancla Swin (F1 val, confirmada por −0.132 de DermLIP); Mini-VLM
    (fidelidad, descripción, 12 GB); control → principal se mantiene; recuperación fuera del ruteo  justifica
P5  Lo mejorable: plantilla diferencial y LLaVA-Med; ancla sin el umbral de melanoma (3 de 10)     abre
P6  Lo que no resuelve: errores compartidos (casi 1/4 de MEL), derivación; → Cap. 6               cierra
```

## Decisiones (25/10/2026)

- Las consecuencias para el diseño que estaban en 5.2.1 (ancla), 5.2.2 (umbral de melanoma), 5.4 (generador de
  referencia) y 5.4.1 (la configuración principal se mantiene) se reúnen aquí (P4–P5).
- La cifra sobre la prueba completa (0.870) se usa como la del sistema entero; está en `tab:res_gen_pipeline`.
- Como en el Cap. 4, la discusión transversal (clasificación y generación juntas) queda en el Cap. 6.
