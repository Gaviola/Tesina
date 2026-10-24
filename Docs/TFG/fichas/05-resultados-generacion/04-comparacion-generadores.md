# Ficha 5.4 — Comparación entre los generadores

**Estado (24/10/2026): redactada sin aprobación previa** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/04-comparacion-generadores.tex`. Label: `sec:res_gen_comparacion`.
Subsecciones: `sec:res_gen_control_mini`, `sec:res_costo` (lo cita el Cap. 6). Figura: `fig:res_gen_resumen`
(`resumen-generadores.pdf`). Tablas: `tab:res_gen_control`, `tab:res_costo_generadores`.

## Hilo conductor

Pregunta: puestos en una misma escala, ¿qué separa a los tres generadores, cambia algo ajustar el modelo de lenguaje
de Mini-VLM y cuánto cuesta el pipeline?
Viene de: 5.3. Deja instalado: Mini-VLM es el generador de referencia; el costo del pipeline lo fija el generador.

```
P1  Retoma; fig resumen                                                                         orienta
P2  Mini = SkinVL (copian); Mini > LLaVA por 0.104, más con el oracle                           describe/interpreta
P3  SkinVL: 17 palabras, mitad de la cobertura, 59 textos distintos; la especialización no
    mejora la fidelidad y reduce la descripción; Mini es la referencia                          interpreta
5.4.1
P4  Para qué el control; tab                                                                    orienta
P5  No cambia la cascada; aprende el formato de SkinCoT; −0.033 con el oracle                   interpreta
P6  SkinCoT: 2/3 con <think>, 1/6 vacíos; por debajo de LLaVA en Nivel 1 → se mantiene v2       interpreta
5.4.2
P7  tab costo (ajuste, s/reporte, horas para la prueba, memoria de los pesos)                   describe
P8  ×1 500 frente a Swin; el kNN no cambia la cuenta; el tiempo depende de lo que escriben      interpreta
P9  Memoria por tamaño; Mini entra en 12 GB; cumple la restricción → Cap. 6                     interpreta
```

## Fuentes

- `cap5_derivados.json` (`entre_generadores`; `fallas.*.full_swin_les`: cobertura, palabras, distintos).
- `docs/resul/mini_vlm_lora_llm_resul_v3_20261024.md` §3.1 y §3.4 (control parcial).
- `cost/cost_comparison_v3.json` (s/reporte de las corridas del re-anclaje; parámetros) y los logs 1153597 (Mini, 9 h
  21 min) y 1153598 (LLaVA, 6 h 55 min) de la segunda etapa en la A30.
- Swin-Tiny 11.05 ms por imagen: `tab:res_costo_clasificadores`.

## Decisiones y preguntas

- La fila de DermLIP del control v3 (+0.021) no se incluye: usa las predicciones de DermLIP anteriores al protocolo
  oficial.
- El control tiene Swin con 963 de 1 503 y sin anclaje con 372 (tramos retenidos en Mendieta); se declara en el texto
  («solo para una parte de la prueba») y en la tabla.
- Memoria = parámetros × 2 bytes (bf16), sin la de la generación; no hay medición de memoria de los generadores
  (pregunta 4 de `00-capitulo.md`). El tiempo del kNN no se midió: se argumenta con el ViT-B/16 medido en el Cap. 4.
