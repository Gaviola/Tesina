# Ficha 5.5 — Comparación con el estado del arte

**Estado (24/10/2026): redactada sin aprobación previa** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/05-estado-del-arte.tex`. Label: `sec:res_gen_estado_arte`. Tabla:
`tab:res_gen_estado_arte` (formato de `tab:res_estado_arte`; flota con `[htbp]`, como las tablas del estado del arte).

## Hilo conductor

Pregunta: ¿dónde quedan los reportes respecto de la literatura en las métricas que tienen un equivalente?
Viene de: 5.4. Deja instalado: mismo orden de magnitud; la diferencia del trabajo es medir el aporte de cada
componente.

```
P1  Por qué no se ordenan los sistemas; tab                                                     orienta
P2  MM-Skin: BLEU-4 muy abajo, BERTScore igual → las palabras, no el contenido                  interpreta
P3  SkinGPT-4 (80.6 % por dermatólogos) frente a 0.849 automático; DermatoLlama, Chakrabarti      interpreta
P4  RULE/MMed-RAG: el contexto puede degradar; aquí la recuperación sola aprovecha mal el
    contexto, pero junto al clasificador no degrada                                             interpreta
P5  Khan: deriva sin informar cuánto; la concordancia aquí separa 9/10 de 1/2; cierre           interpreta/cierra
```

## Fuentes y verificación

- Zeng et al. (MM-Skin), Tabla 3, columna de dermatoscopía (escala 0–100), verificada en el PDF el 24/10/2026
  (`Papers/derma/MM-Skin...pdf`, p. 8): LLaVA-Med-7B BLEU-4 8.88, METEOR 33.74, ROUGE-L 34.83, BERTScore 66.60;
  SkinVL-MM 21.61, 42.76, 44.70, 71.34. Prueba de los autores (5.5k imágenes, formato de preguntas), no la nuestra.
- SkinGPT-4 80.63 %, RULE 75.79 → 67.35 % en MIMIC-CXR, Khan, Chakrabarti, DermatoLlama: tal como los resume el
  Cap. 2 (`sec:estado_arte_reportes`, `tab:marco_generadores`, `tab:marco_sota_reportes`).
- `SkinCaRe` no informa métricas de texto (revisado en el PDF), así que no hay fila de SkinCoT.

## Decisiones

- Las cifras de Zeng se pasan a la escala 0–1 (caption).
- Las comparaciones de la fila de RULE son de distinto tipo (exactitud de preguntas frente a consistencia); el texto
  lo dice y la tabla solo ubica el signo del efecto.
