# Resultado — Re-anclaje de la cascada al Swin de la partición por lesión

**Fecha:** 2026-10-03 · **Plan:** entrada del 2026-09-17 en `ejecuciones.md` («Re-anclaje de la cascada
al split por lesión»), dentro del plan [split_lesion_semillas_plan](../ideas/split_lesion_semillas_plan_20260912.md)
· **Jobs Mendieta:** 1177955 (SkinVL-MM), 1177953 (Mini-VLM), 1178901 (LLaVA-Med; reenvío de 1177954,
que falló sin avisar) · **Antecedente:** [split_lesion_resul](split_lesion_resul_20260926.md).

Fuentes: `outputs/results/ensemble_bootstrap{,_llava_med,_skinvl}_les.json`,
`uncertainty_analysis{,_llava_med}_les.json`, `error_taxonomy_les/{mini_vlm,llava_med,skinvl}/`.
Las versiones sin `_les` son las del anclaje anterior y no se tocaron.

> **Revisión del mismo día** ([revision_experimentacion_20261003](revision_experimentacion_20261003.md)).
> Este documento quedó parcialmente superado: (1) las cifras de LLaVA-Med cuentan texto dentro de bloques
> `<think>`, que el resto de los análisis excluye; (2) el *matcher* de consistencia busca subcadenas («mel»
> dentro de «melanocytic», «nv» dentro de «invasion»), lo que explica el «12 %» de §3.1; (3) la ganancia del
> pipeline avanzado de §3.2 no supera la cobertura mecánica del par de candidatos (imprimirlos sin
> generador). Las cifras corregidas y la lectura vigente están en la revisión.

## 1. Motivación

La cascada clasificador → generador estaba anclada al Swin de la partición por imagen (con fuga). Con el
ganador de la partición por lesión cambian 291/1503 diagnósticos del ancla (19.4 %), la exactitud del ancla
pasa de 0.795 a 0.847, y el ruteo de 3 niveles (acuerdo entre Swin y el voto kNN de DermLIP, también re-ajustado
sobre la partición por lesión) cambia: el conjunto diferencial pasa de 334 a 248 imágenes **distintas** (no
un subconjunto). Había que regenerar los reportes para que el Cap. 5 no
reporte una cascada anclada a un clasificador que el Cap. 4 ya no presenta.

## 2. Diseño

- **Brazos regenerados** (alcance «titulares», decisión del 17/09): `full_swin_les` con los tres
  generadores (1503 cada uno) y `full_differential_les` (248) con Mini-VLM y LLaVA-Med. Mismo prompt,
  mismos *checkpoints* y misma decodificación que los brazos anteriores; solo cambia el diagnóstico que
  recibe el generador.
- **Sin regenerar:** `full_baseline`, `full_dermlip`, `full_oracle`, `full_oracle_noimage` y
  `full_wrong_swap` no dependen del Swin. RAG y `full_uncertainty` quedan con el anclaje anterior
  (brazos complementarios de 400 casos).
- **Evaluación:** consistencia diagnóstica (`diagnostic_consistency_flags`) con *bootstrap* pareado por
  imagen (2000 remuestreos); taxonomía de errores consciente del nivel (`uncertainty_analysis.py`) y
  taxonomía *report-only* (`error_taxonomy.py`). Los reportes `_les` no traen `gt_label`; los scripts lo
  toman de la metadata de HAM.

## 3. Resultados

### 3.1 Consistencia diagnóstica por anclaje (n = 1503)

| Generador | Sin anclaje | DermLIP | Swin anterior | **Swin por lesión** | Oráculo | Δ por lesión − anterior [IC 95 %] |
|---|---|---|---|---|---|---|
| Mini-VLM | 0.246 | 0.497 | 0.812 | **0.864** | 0.999 | +0.052 [+0.033, +0.071] |
| LLaVA-Med | 0.645 | 0.454 | 0.696 | **0.752** | 0.852 | +0.057 [+0.039, +0.075] |
| SkinVL-MM | 0.002 | 0.432 | 0.802 | **0.847** | 0.999 | +0.045 [+0.025, +0.064] |

Todas las diferencias con p < 0.001. Distancia al oráculo con el ancla nueva: Mini −0.135, LLaVA −0.099,
SkinVL −0.152 (antes −0.187, −0.156, −0.197).

**Lectura:**
1. **La mejora del ancla se traslada a los tres generadores con magnitud casi igual** (+0.045 a +0.057,
   frente a +0.052 de exactitud del ancla). La cascada sigue siendo, en esencia, un canal que copia el
   diagnóstico del clasificador.
2. **SkinVL-MM copia exacto**: consistencia 0.847 = exactitud del ancla (con ancla correcta 0.999, con
   ancla equivocada 0.004). Mini-VLM queda **por encima** del ancla (0.864): copia el diagnóstico correcto
   (0.999) y, cuando el ancla se equivoca (n = 230), el 12 % de sus reportes igual nombra la clase verdadera.
   LLaVA-Med queda **por debajo** (0.752): con ancla correcta solo la menciona en el 86 % de los reportes
   (con el oráculo, 0.852), es decir, pierde el diagnóstico que recibe en ~14 % de los casos; con ancla
   equivocada nombra la verdadera en el 16 %.
3. **El orden de las fuentes no cambia**: Swin ≫ DermLIP para los tres; sin anclaje, solo LLaVA-Med nombra
   diagnósticos con alguna frecuencia (0.645), y el anclaje al Swin nuevo lo supera por +0.107
   [+0.073, +0.140] (antes +0.051).

### 3.2 Pipeline avanzado (ruteo de 3 niveles)

| | Mini-VLM | LLaVA-Med |
|---|---|---|
| No derivadas (n = 1452): *grounding* simple → pipeline | 0.873 → **0.916** | 0.760 → **0.816** |
| Δ [IC 95 %] (anterior, n = 1445) | **+0.043** [+0.031, +0.054] (+0.118) | **+0.056** [+0.043, +0.070] (+0.125) |
| Nivel diferencial (n = 248): forzado → diferencial | 0.605 → 0.855 | 0.516 → 0.843 |
| Δ [IC 95 %] (anterior, n = 334) | +0.250 [+0.190, +0.310] (+0.509) | +0.327 [+0.262, +0.395] (+0.542) |

**El pipeline sigue mejorando la fidelidad con ambos generadores, pero la ganancia es entre un tercio y la
mitad de la anterior.** No es un deterioro del pipeline sino del margen que tiene para actuar: con el
clasificador y el kNN nuevos hay menos desacuerdos entre ambos (334 → 248 casos diferenciales), y en los que quedan
el Swin acierta más a menudo, así que el *grounding* simple ya los resuelve mejor (`dx_incorrecto` del
*grounding* simple dentro del subconjunto diferencial: Mini 64 % → 40 %, LLaVA-Med 46 % → 28 %; §3.3). El
estimado del subconjunto limpio del plan del 12/09 (+0.077 Mini, +0.096 LLaVA) también sobrestimaba: usaba
la lista diferencial anterior.

### 3.3 Taxonomía de errores

**Consciente del nivel** (no derivadas; `dx_incorrecto`, *grounding* simple → pipeline):

| | Anterior | Por lesión |
|---|---|---|
| Mini-VLM | 19.0 % → 6.6 % | 13.6 % → 9.0 % |
| LLaVA-Med | 13.5 % → 7.0 % | 9.5 % → 9.0 % |

Desglose dentro del nivel diferencial (n = 248, `dx_incorrecto` simple → diferencial): Mini 100 → 33,
LLaVA 69 → 61 (antes, n = 334: 214 → 34 y 155 → 61).

- **Con LLaVA-Med el pipeline casi no reduce los `dx_incorrecto` (−8 casos).** El reporte diferencial de
  LLaVA-Med deja afuera el diagnóstico verdadero en 61 de 248 casos —la misma cifra absoluta que antes—,
  mientras que el *grounding* simple ahora se equivoca en menos casos de ese subconjunto (155 → 69). Mini-VLM
  sí mantiene la reducción (100 → 33). La mejora de LLaVA-Med en consistencia (+0.327) viene sobre todo de
  convertir *hedging*, contradicciones y reportes sin diagnóstico en diferenciales correctos, no de corregir
  diagnósticos equivocados. (La taxonomía usa un diccionario de clases más estricto que la métrica de
  consistencia, por eso 61/248 no equivale a 1 − 0.843.)
- **Abstención:** de las 51 derivadas, bajo *grounding* simple habrían sido `dx_incorrecto` 20 (Mini) y 19
  (LLaVA-Med); antes, 26 y 18 de 58.
- **Repetición:** sigue siendo propia de Mini-VLM en el nivel diferencial (0.5 % → 3.3 %; LLaVA-Med 0.1 % →
  0.2 %).

***Report-only*** (n = 1503, `dx_incorrecto` Swin anterior → Swin por lesión): Mini 0.20 → 0.15, LLaVA-Med
0.14 → 0.10, SkinVL-MM 0.20 → 0.15; `ok` sube en los tres (0.38 → 0.40, 0.35 → 0.38, 0.79 → 0.85).

## 4. Qué cambia para la tesina

- **Cap. 5:** los números de la cascada pasan a ser los de §3.1 (anclaje por lesión). La tesis central —el
  anclaje a un clasificador especializado es lo que da fidelidad diagnóstica, y el generador la copia— se
  refuerza: tres generadores, mismo Δ que el ancla.
- **Pipeline avanzado:** el titular pasa de «+0.12» a «+0.04/+0.06». Sigue siendo significativo con los dos
  generadores, pero hay que presentarlo como una mejora modesta cuyo tamaño depende de cuántos casos
  inciertos deja el clasificador. La reducción de errores graves es robusta con Mini-VLM y casi nula con
  LLaVA-Med; la abstención evita ~20 diagnósticos incorrectos con ambos.
- **Declarados sobre el anclaje anterior** (sin cambios respecto de §8 del resul del 26/09): RAG,
  `full_uncertainty`, `full_oracle_noimage`/`full_wrong_swap` (no dependen del ancla), taxonomía v3 por clase.
- **Tabla SOTA v33:** tabla nueva `tab:cascada` con §3.1–3.2; `tab:posicionamiento` actualizada con la
  partición por lesión (todavía tenía los números con fuga).

## 5. Conclusión (veredicto)

**CUMPLE.**

- *Re-anclaje completo:* 3 × 1503 + 2 × 248 reportes, sin faltantes (el fallo silencioso de 1177954 quedó
  detectado y el reenvío verifica códigos de salida y conteos): **cumple**.
- *Conclusiones centrales* (criterio del plan del 12/09: se sostienen si el orden de los enfoques no
  cambia): el anclaje al Swin supera a DermLIP y a la generación sin anclaje con los tres generadores, y el
  pipeline avanzado supera al *grounding* simple con IC que no cruza 0 en ambos generadores: **cumple**.
- *Magnitud del pipeline avanzado:* **baja** (+0.118/+0.125 → +0.043/+0.056) y su efecto sobre
  `dx_incorrecto` con LLaVA-Med casi desaparece. No invalida la conclusión, pero cambia cómo se presenta.

**Siguiente paso:** con esto la experimentación de los Cap. 4 y 5 queda cerrada sobre la partición por
lesión. Pendiente de redacción, no de experimentación: corregir los números de `experimentacion.tex` si
vuelve a leerlo el tutor, y redactar los Cap. 4 y 5 desde las fichas.
