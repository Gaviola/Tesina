# Ficha 5.2 — Cascada clasificador–generador

**Estado (24/10/2026): redactada sin aprobación previa** (ver `00-capitulo.md`).

Archivo: `Chapters/05-Resultados-Generacion/02-cascada.tex`. Label: `sec:res_gen_cascada`. Subsecciones:
`sec:res_gen_fuentes`, `sec:res_gen_clases`, `sec:res_gen_ablaciones`, `sec:res_gen_errores`, `sec:res_gen_rag`.
Figuras: `fig:res_gen_cascada` (`cascada-fuentes.pdf`), `fig:res_gen_clases` (`cascada-por-clase.pdf`),
`fig:res_gen_errores` (`fallas-reportes.pdf`). Tablas: `tab:res_gen_cascada`, `tab:res_gen_ablaciones`,
`tab:res_gen_rag`.

## Hilo conductor

Pregunta: con el diagnóstico del clasificador en la instrucción, ¿el reporte afirma la clase correcta, y qué aportan
la imagen y los vecinos?
Viene de: 5.1, ningún generador afirma solo la clase. Deja instalado: la fidelidad del reporte es la exactitud del
clasificador, con sus errores; ni la imagen ni los vecinos los corrigen.

```
P1  Retoma 5.1; orden de la sección                                                             orienta
5.2.1
P2  fig: Mini y SkinVL = 0.847; LLaVA una décima abajo; oracle: Mini/SkinVL todo menos uno,
    LLaVA omite 1 de 7                                                                          describe
P3  tab: diferencias significativas; ×5 en Mini; distancia al oracle = errores de Swin          describe
P4  Copia: Mini nombra el ancla en 1 501/1 503; 1 272/1 273 si acierta, 4/230 si no             interpreta
P5  LLaVA: omisiones (describe sin diagnóstico; textos breves/vacíos), en NV, BKL, AKIEC        interpreta
P5b DermLIP sin ajuste (0.716): Mini/SkinVL nombran su dx salvo 1 y 2 reportes; consistencia = exactitud  interpreta
P5c Swin − DermLIP +0.132 [0.107, 0.158] (Mini); LLaVA apenas sobre sin anclaje; se ancla en Swin   cierra
5.2.2
P6  fig por clase: Mini/SkinVL sobre la diagonal; LLaVA abajo, AKIEC a la mitad                 describe
P7  Consecuencia: 3 de 10 melanomas sin melanoma en el reporte; mejorar el reporte = mejorar el
    ancla                                                                                       interpreta
5.2.3
P8  Método de las ablaciones (imagen gris; clase confundible), tab                              describe
P9  La imagen no cambia el diagnóstico; con diagnóstico equivocado → 0                          interpreta
P10 La imagen cambia la descripción (7 textos sin imagen; cobertura de Mini a la mitad; LLaVA no) interpreta
5.2.4
P11 Regla de la taxonomía (categorías del marco) y fig                                          define/describe
P12 Sin anclaje: LLaVA contradicción, Mini hedging + incorrecto, SkinVL nada                    interpreta
P13 Con anclaje: hedging desaparece; con oracle quedan las fallas del generador                 interpreta
5.2.5
P14 tab recuperación                                                                            describe
P15 Recuperación sola < Swin y < voto impreso                                                   interpreta
P16 Swin + RAG +0.013 por nombrar más; vecino equivocado no degrada (171), rescata 1/6 (72)       interpreta
P17 Síntesis → transición al ruteo                                                              cierra
```

## Fuentes

- `ensemble_bootstrap{,_llava_med,_skinvl}_les_report_only_strict.json` (consistencias e IC).
- `cap5_derivados.json` (`scripts/cap5_derivados.py`, nuevo): `por_clase`, `ablaciones` (recalculadas con la métrica
  oficial sobre las 400 imágenes comunes de `full_oracle`, `full_oracle_noimage` y `full_wrong_swap`; SkinVL 1 503),
  `fallas`, `recuperacion`.
- `rag_les_eval.json` y `docs/resul/rag_les_resul_20261011.md` (tabla de recuperación).

## Decisiones y preguntas

- Las ablaciones de julio usaban el matcher anterior y el texto completo; con la métrica oficial cambian poco
  (LLaVA-Med: 0.848 → 0.863 con imagen, 1.000 → 0.893 sin imagen, ahora sin diferencia significativa). Se usan las
  nuevas. La lectura «sin imagen LLaVA-Med sube a 1.000» de la experimentación ya no se sostiene.
- `make_wrong_dx.py` usa pares confundibles fijos (MEL → NV, NV → MEL, BKL → MEL, BCC → NV, AKIEC → BKL, DF → NV,
  VASC → MEL); el texto da el ejemplo MEL por NV.
- El método de las ablaciones y de la taxonomía no está en el Cap. 3 (pregunta 1 de `00-capitulo.md`).
- La cobertura de entidades de LLaVA-Med no baja sin la imagen: se dice tal cual, sin generalizar la afirmación de la
  experimentación («la imagen sostiene la riqueza»), que solo vale para Mini-VLM.
