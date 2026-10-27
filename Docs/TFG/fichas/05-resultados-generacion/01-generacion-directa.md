# Ficha 5.1 — Generación de reportes sin diagnóstico

**Estado (25/10/2026): reescrita con la revisión del autor del 25/10** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/01-generacion-directa.tex`. Label: `sec:res_gen_directa`. Subsecciones:
`sec:res_gen_nivel1`, `sec:res_gen_sin_anclaje`. Tablas: `tab:res_gen_nivel1`, `tab:res_gen_sin_anclaje`.

## Hilo conductor

Pregunta: sin recibir un diagnóstico, ¿qué escriben los generadores ajustados?
Viene de: Cap. 4, los VLM generativos no clasifican. Deja instalado: el reporte tiene dos partes (descripción y
diagnóstico) que se miden por separado y sin verificar la descripción; ningún generador afirma solo la clase; tres
maneras de fallar (enumerar, elegir mal, texto fijo).

```
P1  Retoma el Cap. 4; los generadores ajustados escriben con forma de reporte, con descripción y
    diagnóstico; diseño: generador aislado, instrucción del entrenamiento, un reporte por imagen   orienta
P2  Qué mide cada nivel: Nivel 1 la descripción frente a una referencia, Nivel 2 el diagnóstico;
    ninguno verifica la descripción (especialista, Cap. 6)                                       delimita
5.1.1
P3  Diseño: SkinCoT y MM-Skin, Mini y LLaVA, MM-Skin pareado (1 022); SkinVL fuera (MM-Skin es su
    ajuste)                                                                                       describe
P4  tab:res_gen_nivel1: el parecido depende del conjunto                                          describe
P5  Es el estilo de la referencia, no la calidad                                                  interpreta
P6  SkinCoT: Mini < LLaVA en las cinco (0.770 vs 0.797); explicación única del LLM sin ajustar
    de Mini-VLM (qkv_proj)                                                                        interpreta
P7  MM-Skin pareado: el orden se invierte (+0.039 [0.038, 0.041]); el Nivel 1 mide el ajuste de la
    redacción y no elige modelos                                                                  interpreta
5.1.2
P8  Diseño (HAM10000, 1 503, tres generadores) + tab:res_gen_sin_anclaje + «solo la clase verdadera»
P9  LLaVA enumera (2.17 clases, 1 de 20 exclusiva); Mini elige mal                                interpreta
P10 SkinVL: 72 textos distintos, 7 de 10 iguales («tinea corporis», explicada)                    interpreta
P11 Bloques <think> casi ausentes (remite a P6) → transición a la cascada                        cierra
```

## Fuentes

- Nivel 1 LLaVA-Med v2 en SkinCoT: `outputs/results/level1_test/skincot_test/level1_llava_med_results.json` (426).
- Nivel 1 Mini-VLM v2 en SkinCoT: `level1_test/skincot_test_mini_v2/level1_mini_vlm_results.json` (425;
  `costo_nivel1_mini_v2_resul_20261025.md`).
- Nivel 1 en MM-Skin, pareado: `level1_test/mmskin_test/level1_pareado_mini_v2_llava_v2.json` (1 022 pares comunes;
  `level1_mmskin_pareado_resul_20261025.md`). Mini-VLM viene de la corrida sobre el archivo completo, cortada por
  tiempo; sus 1 107 imágenes de prueba están dentro de las 1 650 de LLaVA-Med.
- Sin anclaje: `ensemble_bootstrap*_les_report_only_strict.json` (`full_baseline`) y `cap5_derivados.json`
  (`sin_anclaje`: exclusiva, clases por reporte, distintos, palabras, `<think>`).

## Decisiones (revisión del autor, 25/10/2026)

- La sección abre con las dos partes del reporte y qué mide cada nivel; la falta de verificación de la descripción se
  dice de entrada y se remite al Cap. 6.
- MM-Skin se compara pareado; desaparece «la diferencia no se interpreta». La cifra de LLaVA-Med en MM-Skin pasa de
  0.669 (1 414 pares) a 0.674 (1 022), también en `tab:res_gen_estado_arte`.
- El LLM sin ajustar de Mini-VLM se explica una sola vez (P6); P11 y 5.4.1 remiten.
- SkinVL fuera del Nivel 1, con el motivo.
- La explicación del colapso de SkinVL se limita a lo observado; el experimento de instrucciones alternativas
  (`skinvl_prompts_p42_resul`) no está en el Cap. 3 y no se usa.
