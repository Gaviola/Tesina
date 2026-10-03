# Revisión de la experimentación antes de redactar los Cap. 4 y 5

**Fecha:** 2026-10-03 · **Alcance:** todo lo que van a usar los Cap. 4 y 5 tras la migración a la partición
por lesión ([split_lesion_resul](split_lesion_resul_20260926.md),
[reanclaje_cascada_resul](reanclaje_cascada_resul_20261003.md)) · **Método:** revisión propia (cifras de los
documentos contra los JSON, cobertura de los esqueletos de los capítulos, brazos que quedaron sobre v3) más
una auditoría independiente de segunda opinión (Fable 5.1: fuga y selección en test, recálculo de titulares,
validez de la métrica de la cascada, estadística). Todo lo marcado «verificado» se recalculó localmente;
lo marcado «segunda opinión» viene solo de la auditoría.

Scripts de verificación (scratchpad, no versionados): recálculo de titulares, cascada con *matcher* estricto
y línea base mecánica, RAG por subconjunto, HIBA por modalidad. Las cifras corregidas de §2 se reproducen
con la lógica descrita en cada punto.

## 1. Qué está bien (verificado)

- **Partición por lesión:** cero lesiones e imágenes compartidas entre train/val/test; el test es el
  original; los entrenamientos usaron `ham10000_splits_lesion.json`.
- **Selección en validación:** el ganador por F1 macro de val se reproduce (30 candidatos por modelo); en
  test ninguno de los dos ganadores es el mejor (no hay selección sobre test). La CE de la réplica de
  desbalance, que en test tiene más exactitud que el ganador, pierde en val (F1m 0.750 vs 0.766).
- **Titulares** recalculados desde las predicciones (diferencias ≤ 0.001): Swin 0.846 / 0.733 / 0.692,
  ConvNeXt 0.843 / 0.727 / 0.691, ensamble 0.855 / 0.747 / 0.706; melanoma con umbral de val (Swin 0.796 ±
  0.036, ensamble 0.828 ± 0.007); calibración (T ajustada en val, ECE 0.040 → 0.027).
- **kNN/RAG por lesión** (`rag_context_les.csv`): índice solo con train, sin imágenes ni lesiones de test;
  se reproduce al 100 %. Ruteo 1204 / 248 / 51 reproducido.
- **Anclaje de los reportes:** `full_dx_swin_les.csv` = argmax de Swin semilla 42; los 3 × 1503 reportes
  `full_swin_les` traen el diagnóstico y el prompt correctos; `full_differential_les` cubre exactamente los
  248 casos con sus candidatos; sin reportes vacíos.
- **Tablas v33 y resul** contra los JSON: clasificación, melanoma, calibración, HIBA, tests estadísticos.
- `full_wrong_swap` y `full_oracle_noimage` no dependen del ancla.

## 2. Hallazgos

### 2.1 CRÍTICO — El pipeline avanzado no supera a imprimir los candidatos sin generador (H6)

*Verificado.* El nivel diferencial no recibe el top-2 de Swin sino el par {top-1 de Swin, voto kNN}
(`build_uncertainty_3tier.py:63-72`). Si el sistema simplemente escribiera el diagnóstico del nivel
afirmativo y el par del diferencial, sin generador («línea base mecánica»), la consistencia sería 0.904 sobre
las 1452 no derivadas.

| n = 1452 (solo reporte, *matcher* estricto) | Mini-VLM | LLaVA-Med |
|---|---|---|
| *Grounding* simple | 0.858 | 0.760 |
| Pipeline avanzado | 0.901 | 0.793 |
| Línea base mecánica (sin generador) | 0.904 | 0.904 |
| Pipeline − simple | +0.043 [+0.031, +0.055] | +0.034 [+0.020, +0.048] |
| **Pipeline − mecánica** | **−0.003** [−0.008, +0.002] | **−0.110** [−0.129, −0.092] |
| Nivel diferencial (n = 248): reporte / par en el prompt | 0.831 / 0.847 | 0.677 / 0.847 |

- Toda la ganancia del pipeline sobre el *grounding* simple viene de presentar dos candidatos en el nivel
  diferencial: el par contiene la clase verdadera en 0.847 de esos casos y el top-1 de Swin en 0.573. El
  generador no agrega fidelidad: Mini-VLM la conserva, LLaVA-Med la pierde (deja afuera candidatos).
- La métrica premia nombrar varias clases: los reportes diferenciales mencionan 2.62 (Mini) y 2.10 (LLaVA)
  clases en promedio, 47 % y 35 % nombran tres o más. La taxonomía consciente del nivel es asimétrica:
  nombrar varias clases es «contradicción» en el brazo simple y `ok_diferencial` en el diferencial
  (`uncertainty_analysis.py::classify_differential`).
- Ya se había visto en agosto («el 0.940 coincide con la cobertura del router 0.934», `ejecuciones.md`),
  pero no llegó a la lectura.
- **Qué se sostiene:** el ruteo separa bien los casos (Swin acierta 0.915 en el nivel afirmativo, 0.573 en
  el diferencial) y, cuando hay desacuerdo, dar dos candidatos cubre más que uno (0.847 vs 0.573). Es una
  propiedad del **ruteo**, no del generador, y es coherente con la tesis «el clasificador aporta el
  diagnóstico, el VLM la descripción».
- **Abstención:** Swin acierta 29 de los 51 casos derivados (0.569, igual que en el diferencial). Decir que
  la abstención «evita ~20 diagnósticos incorrectos» omite que también descarta 29 correctos.

### 2.2 IMPORTANTE — Las cifras de LLaVA-Med cuentan texto de razonamiento

*Verificado.* `ensemble_bootstrap.py` no descartaba los bloques `<think>…</think>`; la taxonomía y el análisis
por clase sí (decisión metodológica «reporte, no razonamiento»). Solo afecta a LLaVA-Med (Mini-VLM y
SkinVL-MM no los emiten). 175 de los 248 reportes diferenciales de LLaVA-Med tienen razonamiento, y en
muchos el diagnóstico verdadero solo aparece ahí.

| LLaVA-Med | Con razonamiento (publicado) | Solo reporte |
|---|---|---|
| `full_swin_les` | 0.752 | 0.741 |
| Pipeline − simple (n = 1452) | +0.056 [+0.043, +0.070] | +0.032 [+0.018, +0.047] |
| Diferencial − forzado (n = 248) | +0.327 | +0.190 [+0.113, +0.270] |
| Ídem anclaje anterior: pipeline − simple | +0.125 | +0.092 [+0.075, +0.109] |

**Corregido en código:** `ensemble_bootstrap.py --report_only` (salida `*_report_only.json`; sin el flag
reproduce los JSON anteriores).

### 2.3 IMPORTANTE — El *matcher* de consistencia busca subcadenas

*Verificado en el código* (`src/evaluation/clinical_ner.py:35-42, 215`): `syn in report_lower` sin límite de
palabra, con sinónimos ambiguos: «mel» (dentro de «melanocytic», «melanin»), «nv» («invasion»,
«involvement»), «keratosis» suelto acredita queratosis benigna aunque diga «actinic keratosis», «vascular»
suelto acredita lesión vascular. `error_taxonomy.py:49` ya lo había advertido para «mel».

Con un *matcher* estricto (límite de palabra, sin esos sinónimos) y solo reporte:

| | Sin anclaje | Swin anterior | Swin por lesión | Oráculo | Δ por lesión − anterior |
|---|---|---|---|---|---|
| Mini-VLM | 0.166 | 0.798 | 0.849 | 0.999 | +0.051 [+0.031, +0.071] |
| LLaVA-Med | 0.585 | 0.687 | 0.749 | 0.860 | +0.062 [+0.044, +0.081] |
| SkinVL-MM | 0.001 | 0.794 | 0.846 | 0.999 | +0.052 [+0.033, +0.072] |

- Los Δ del re-anclaje casi no cambian. Sí cambian dos afirmaciones del resul del re-anclaje: Mini-VLM **no**
  supera al ancla (0.849 ≈ 0.847; con el ancla equivocada nombra la clase verdadera en 1.7 %, no 12 %), y el
  0.645 de LLaVA-Med sin anclaje viene de nombrar muchas clases (consistencia exclusiva —solo la verdadera—
  0.047). Con el *matcher* estricto el anclaje de LLaVA-Med gana +0.164 sobre no anclar (antes +0.107).

### 2.4 IMPORTANTE — RAG quedó con un índice con fuga

*Verificado.* `full_rag` y `full_swin_rag` (Mini-VLM, n = 400) usan `rag_context.csv`, construido sobre la
partición por imagen (`build_rag_index.py:69`). En los 609 casos de test cuya lesión estaba en train/val, el
voto kNN acierta 0.790 con ese índice y 0.667 con el índice por lesión; global 0.831 → 0.781.

Sobre el subconjunto limpio (n = 265 de los 400, sin lesión vista), con IC pareados:

| Comparación | Δ [IC 95 %] |
|---|---|
| RAG solo − sin anclaje | +0.608 [+0.547, +0.668] |
| RAG solo − *grounding* Swin anterior | −0.087 [−0.136, −0.038] |
| Swin + RAG − Swin anterior | +0.004 (n. s.) |
| RAG solo − *grounding* Swin por lesión | −0.155 [−0.204, −0.106] |

Lo que se sostiene: RAG rescata mucho frente a no anclar y sumarlo al clasificador no aporta. Lo que no:
«RAG solo casi iguala al clasificador». Además debe declararse como «índice con fuga», no solo «anclaje
anterior».

### 2.5 IMPORTANTE — HIBA estaba mal descrito

*Verificado.* HIBA no es solo dermoscopía: 346 de 1616 imágenes son clínicas (cámara). Exactitud de Swin
0.624 en dermoscópicas y 0.263 en clínicas (ConvNeXt 0.632 / 0.283). Los fototipos son I–IV (II = 1085), no
«III–VI». La caída OOD sí se puede separar por modalidad. **Corregido** en `tab:hiba_ood` de la v33.

### 2.6 IMPORTANTE — El ruteo estaba mal descrito

*Verificado.* El ruteo no usa la confianza calibrada ni τ: es acuerdo Swin ↔ kNN. Eran falsas «confianza
calibrada baja», «los dos candidatos principales» y «con un clasificador mejor calibrado hay menos casos
inciertos». **Corregido** en `tab:cascada` (v33) y en el resul del re-anclaje. *Segunda opinión, no
re-verificado:* el pivote desde la confianza softmax se decidió en julio con la calibración que tenía el bug
(T = 0.53); con la calibración correcta, una regla τ = 0.68 daría 198 inciertos con cobertura top-2 0.869.
Atenuante (segunda opinión): la regla del acuerdo da proporciones casi iguales en val (80.1 / 16.0 / 3.9 %),
sin señal de sobreajuste a test.

### 2.7 Para la presentación — La mejora del ancla nueva viene de nevus

*Verificado* (`per_class_ensemble.py` adaptado a los reportes `_les`; salida `outputs/results/per_class_les/`).
Por clase, con Mini-VLM: nevus 0.81 → 0.93, pero melanoma 0.83 → 0.79, BCC 0.83 → 0.68, AK 0.82 → 0.53,
vascular 0.95 → 0.82 (SkinVL-MM igual; melanoma 0.83 → 0.70). La cascada hereda la sensibilidad por clase del
ancla, y el ancla nueva no usa pesos por clase. Además usa solo la semilla 42, que está por encima de la media
(sens. macro 0.716 vs 0.692; recall MEL 0.701 vs 0.623): hay que declararlo.

### 2.8 MENOR

- **Criterio de selección cambiado con el test a la vista** (segunda opinión): el paso a F1 macro se justificó
  con métricas de test y la condición «no empeora sens. macro» no se cumplió (ConvNeXt 0.700 → 0.691), aunque
  se declaró cumplida. Sin sesgo optimista: con el criterio viejo el ensamble daría más (0.861 / 0.767 /
  0.727). Basta con documentarlo así.
- **Estadística** (segunda opinión): con n = 3 semillas, «la varianza baja a una décima» no se sostiene (IC
  95 % del desvío [0.013, 0.157] vs [0.001, 0.013]); el ensamble no supera a Swin con significancia en ninguna
  semilla. *Verificado:* Swin vs DenseNet en sens. macro, +0.044 [−0.012, +0.100], no significativo (sí en F1
  macro y McNemar). El *bootstrap* remuestrea imágenes, no lesiones (1503 imágenes, 1429 lesiones).
- **La lista diferencial v3** (`uncertainty_differential.csv`) quedó pisada el 17/09; se reconstruye desde
  `uncertainty_3tier.csv` si hace falta. Ya estaba anotado.
- **HIBA, «primera evaluación sistemática sobre población argentina»** (`tab:hiba_ood`, obs. 5): verificar
  contra el artículo del dataset antes de afirmarlo.
- **No verificable localmente:** que DermLIP «nunca vio HAM» (habría que revisar las fuentes de Derm1M).

## 3. Decisiones que necesita el autor

1. **Métrica oficial de la cascada:** pasar a *solo reporte* + *matcher* estricto y recalcular todas las
   cifras del Cap. 5 (recomendado: la primera ya es la convención declarada y la segunda corrige un error).
2. **Lectura de H6** (`01-Introduccion.tex:183`: «incorporar la incertidumbre del clasificador […] mejora la
   fidelidad diagnóstica sobre los casos no derivados»). Tal como está escrita se cumple frente al
   *grounding* simple (+0.043 Mini, +0.032 LLaVA, solo reporte). Lo que hay que cambiar es la lectura en el
   Cap. 5: la mejora es del ruteo (dar dos candidatos cuando clasificador y kNN discrepan), se reporta junto
   a la línea base mecánica y se dice explícitamente que el generador la conserva (Mini) o la degrada
   (LLaVA), no que la produce. Opcional: agregar una métrica que penalice nombrar varias clases.
3. **RAG:** reportarlo sobre el subconjunto limpio (local, ya calculado) o regenerar `full_rag` y
   `full_swin_rag` con el índice por lesión (800 reportes de Mini-VLM).
4. **Abstención y ancla:** si la cascada debería anclarse en un punto de operación que proteja las clases
   malignas (p. ej., el ensamble o el umbral de melanoma fijado en val) o se declara la limitación.

## 4. Conclusión (veredicto)

**CUMPLE con correcciones.** La clasificación, la partición, la selección y las cifras principales son
correctas y reproducibles; no hay fuga ni selección sobre test. H6 se sostiene en su enunciado, pero su
lectura debe cambiar: la ganancia es del ruteo, no del generador, y no supera a la línea base mecánica. Las
cifras de LLaVA-Med (razonamiento) y el *matcher* requieren recalcular el Cap. 5 con la métrica corregida.
RAG, HIBA y la descripción del ruteo tenían errores de hecho; los de HIBA y el ruteo ya están corregidos en
la tabla v33 y el resul.
