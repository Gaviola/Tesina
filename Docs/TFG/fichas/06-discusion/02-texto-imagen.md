# Ficha 6.2 — El peso del texto frente a la imagen en los generadores

Archivo: `Chapters/06-Discusion/02-texto-imagen.tex`. Label: `sec:disc_texto_imagen`.

## Hilo conductor

Pregunta: ¿por qué el generador afirma lo que recibe en el texto aunque la imagen diga otra cosa, y qué implica?
Viene de: 6.1 (no convierte la imagen en clase). Deja instalado: la señal de confianza debe venir de fuera del
generador (para 6.3).

```
P1  Patrón común a los dos capítulos: prompt (imagen gris), diagnóstico inyectado (sin imagen, equivocado),
    vecinos (recuperación) → jerarquía diagnóstico > vecinos > imagen                                      interpreta
P2  Origen: el ajuste nunca vio diagnósticos en la instrucción y Mini-VLM no ajusta su LM → viene del
    modelo de lenguaje base (rohrbach, bai); alternativa: ceder es razonable para quien no clasifica       conjetura
P3  Diseño y evaluación: la fidelidad se compra en el clasificador; el generador solo puede restarla
    (LLaVA-Med); los sistemas integrados deben medirse por componente                                     implica
P4  Clínica: no es segunda opinión; la descripción se adapta al diagnóstico (prototipo de clase sin imagen;
    melanoma «homogéneo») → la verosimilitud no indica corrección                                         implica
```

Fuentes: `sec:res_vlm_controles`, `sec:res_gen_sin_anclaje`, `sec:res_gen_fuentes`, `sec:res_gen_ablaciones`,
`sec:res_gen_rag`, `sec:res_gen_comparacion`, `sec:res_gen_cualitativos`, `sec:res_gen_estado_arte`,
`sec:met_generacion`, `sec:marco_rep_fallas`. Citas: `rohrbach2018object`, `bai2024hallucination`.
