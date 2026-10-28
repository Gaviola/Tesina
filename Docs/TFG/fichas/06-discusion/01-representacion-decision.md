# Ficha 6.1 — Especialización de la representación y decisión diagnóstica

Archivo: `Chapters/06-Discusion/01-representacion-decision.tex`. Label: `sec:disc_representacion`.

## Hilo conductor

Pregunta: ¿dónde está lo que un VLM aporta a la clasificación, y qué le falta para diagnosticar?
Viene de: la intro. Deja instalado: los generativos extraen información visual pero no la convierten en una clase
(para 6.2).

```
P1  Tres niveles (generativos, DermLIP sin ajuste, DermLIP con cabeza) → dónde está la diferencia            plantea
P2  Controles: especialización y no modalidad (sin excluirla); la respuesta generativa depende del prompt   interpreta
P3  La especialización está en la representación: congelada, se acerca a Swin ajustado (sin prueba)        interpreta
P4  «Ver no es diagnosticar»: la descripción cambia con la imagen, la clase no → cuello de botella en el
    paso a la clase; alternativa: SkinCaRe no tiene las siete clases                                       conjetura
P5  SkinVL y la literatura; la respuesta a PI1 depende del uso → el pipeline usa cada modelo donde rinde   cierra
```

Fuentes: `sec:res_vlm_controles`, `sec:res_vlm_dermlip` (`tab:res_dermlip`, `tab:res_dermlip_swin`),
`tab:res_supervisados`, `sec:res_gen_ablaciones`, `sec:res_gen_sin_anclaje`, `sec:met_generacion`. Citas:
`zeng2025mmskin`, `jiang2026multimodal`, `yan2026dermfmzero`.
