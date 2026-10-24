# Ficha 5.1 — Generación de reportes sin diagnóstico

**Estado (24/10/2026): redactada sin aprobación previa** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/01-generacion-directa.tex`. Label: `sec:res_gen_directa`. Subsecciones:
`sec:res_gen_nivel1`, `sec:res_gen_sin_anclaje`. Tablas: `tab:res_gen_nivel1`, `tab:res_gen_sin_anclaje`.

## Hilo conductor

Pregunta: sin recibir un diagnóstico, ¿qué escriben los generadores ajustados?
Viene de: Cap. 4, los VLM generativos no clasifican. Deja instalado: ningún generador afirma solo la clase; tres
maneras de fallar (enumerar, elegir mal, texto fijo).

```
P1  Retoma el Cap. 4; los generadores ajustados escriben con forma de reporte; dos niveles     función: orienta
5.1.1
P2  tab:res_gen_nivel1: el parecido depende del conjunto (SkinCoT ~0.80 BERTScore; MM-Skin casi cero en
    solapamiento)                                                                               describe
P3  Es el estilo de la referencia, no la calidad; Mini vs LLaVA sobre subconjuntos distintos; no elige
    modelos                                                                                     interpreta
\pendiente  Nivel 1 de Mini-VLM principal en SkinCoT
5.1.2
P4  tab:res_gen_sin_anclaje + «solo la clase verdadera»                                         describe
P5  LLaVA enumera (2.17 clases, 1 de 20 exclusiva); Mini elige mal; ambos describen             interpreta
P6  SkinVL: 72 textos distintos, 7 de 10 iguales («tinea corporis»)                             interpreta
P7  Bloques <think> casi ausentes (11 en LLaVA, 0 en Mini) → transición a la cascada            cierra
```

## Fuentes

- Nivel 1 LLaVA-Med v2: `outputs/results/level1_test/{skincot_test,mmskin_test}/level1_llava_med_results.json`
  (426 y 1 414 pares; `ejecuciones.md`, 19/10).
- Nivel 1 Mini-VLM v2 en MM-Skin: `level1_mmskin_recalc.json`, clave `test` (n = 1 022: imágenes de la partición de
  prueba dentro de la corrida sobre el archivo completo; nota en `reportes_resul_v2_20260517.md` §4.1).
- Sin anclaje: `ensemble_bootstrap*_les_report_only_strict.json` (`full_baseline`) y `cap5_derivados.json`
  (`sin_anclaje`: exclusiva, clases por reporte, distintos, palabras, `<think>`).

## Decisiones y preguntas

- No hay Nivel 1 de Mini-VLM v2 en SkinCoT (`mini_vlm_lora_llm_resul_v3` §3.4): queda `\pendiente` con lo que
  haría falta generar. Pregunta 2 de `00-capitulo.md`.
- La comparación Mini–LLaVA en MM-Skin no se interpreta porque los subconjuntos difieren (1 022 frente a 1 414).
- La explicación del colapso de SkinVL se limita a lo observado (texto ajeno a las siete clases, independiente de la
  imagen); el experimento de instrucciones alternativas (`skinvl_prompts_p42_resul`) no está en el Cap. 3 y no se usa.
