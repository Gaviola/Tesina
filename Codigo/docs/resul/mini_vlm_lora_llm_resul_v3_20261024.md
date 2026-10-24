# Resultado (parcial) — Mini-VLM v3: LoRA sobre el modelo de lenguaje

**Fecha:** 2026-10-24 · **Plan:** [mini_vlm_lora_llm_plan](../ideas/mini_vlm_lora_llm_plan_20261012.md) ·
**Jobs:** Mendieta 1179985 (etapa 2 v3), tramos de `short` 1180965–1181064 (`slurm/mendieta/v5/gen_short_mini_v3.sh`);
TOKO 99257 (TIMEOUT a las 12 h, oracle completo + 290 de DermLIP) y 99258 (COMPLETED, DermLIP completo;
`slurm/toko/v5/gen_mini_v3.sh`) · **Antecedentes:** [verificaciones_cap03_resul](verificaciones_cap03_resul_20261011.md)
(LoRA de v2 solo en CLIP), [rag_les_resul](rag_les_resul_20261011.md) y
[revision_experimentacion](revision_experimentacion_20261003.md) (métrica oficial).

Fuentes: `outputs/generated_reports/mini_vlm/v3/<brazo>/` (bajados el 24/10 por `tar` sobre ssh desde
`mini_vlm_v3/` de ambos clústeres) frente a `outputs/generated_reports/mini_vlm/<brazo>/` (v2).
Resultados: `outputs/results/mini_vlm/v3/consistencia_v3_parcial_20261024.json`,
`outputs/results/level1_test/skincot_test/level1_mini_vlm_results.json` y
`level1_pareado_mini_v3_vs_llava_v2.json`. Scripts de borrador fuera del repo que reusan
`diagnostic_consistency_flags(strict=True)`, `paired_bootstrap_diff_flags` y `evaluate_generation`.

## 1. Estado de los brazos

| Brazo | Reportes v3 | Estado |
|---|---|---|
| `full_oracle` | 1 503 / 1 503 | completo (TOKO) |
| `full_dermlip` | 1 503 / 1 503 | completo (TOKO) |
| `full_differential_les` | 248 / 248 | completo (Mendieta) |
| `skincot_test` (Nivel 1) | 457 / 457 | completo (Mendieta) |
| `full_swin_les` | 963 / 1 503 | 9 tramos retenidos (`user_env_retrieval_failed_requeued_held`; el último reintento falló en ivb14) |
| `full_baseline` | 372 / 1 503 | 3 tramos retenidos, `nice=500`; el resto, en `multi` 1179986 |
| RAG, ablaciones, MM-Skin test, clasificación | 0 | en `multi` (1179986–1179990, `PENDING` por prioridad) |

## 2. Diseño de la lectura

Métrica oficial: consistencia diagnóstica solo sobre el reporte (se quitan los bloques `<think>`), *matcher*
estricto. v3 frente a v2 con *bootstrap* pareado (2 000, semilla 42) sobre las imágenes que tienen reporte en ambas
versiones. Decodificación idéntica (voraz, 384 tokens, semilla 42).

## 3. Resultados

### 3.1 v3 frente a v2, por brazo

| Brazo | n | v3 | v2 | Δ [IC 95 %] | p | v3 con `<think>` |
|---|---|---|---|---|---|---|
| Oracle | 1 503 | 0.967 | 0.999 | −0.033 [−0.042, −0.023] | < 0.001 | 381 |
| DermLIP | 1 503 | 0.412 | 0.391 | +0.021 [+0.007, +0.035] | < 0.001 | 302 |
| Swin por lesión | 963 | 0.843 | 0.850 | −0.007 [−0.021, +0.006] | 0.33 | 239 |
| Sin anclaje | 372 | 0.196 | 0.185 | +0.011 [−0.043, +0.065] | 0.75 | 80 |
| Diferencial | 248 | 0.863 | 0.831 | +0.032 [−0.008, +0.077] | 0.15 | 4 |

Ningún reporte de HAM10000 queda vacío al quitar el `<think>`.

### 3.2 La caída del oracle

De los 50 reportes del oracle que no nombran la clase, 47 tienen `<think>`. En 31 la clase está dentro del
razonamiento: v3 imita el formato de SkinCoT (descripción → `<think>` → diferencial → diagnóstico) y con 384 tokens
el diagnóstico final no llega a escribirse fuera del bloque. En los otros 19 la clase no aparece ni en el
razonamiento; en los que se revisaron el texto se aparta del ancla (p. ej. «benign vascular lesion» con el ancla
*nevus*). Las clases afectadas son queratosis benigna (27), nevo (19), dermatofibroma (3) y queratosis actínica (1). v2 no abre `<think>` y repetía el ancla casi siempre (0.999).

### 3.3 Cascada v3 (parcial)

Sobre las 242 imágenes con los cuatro brazos de v3: oracle 0.983, Swin por lesión 0.826, DermLIP 0.471, sin
anclaje 0.202. Swin − oracle −0.157 [−0.207, −0.112]; DermLIP − Swin −0.355 [−0.434, −0.281]; sin anclaje − Swin
−0.624 [−0.694, −0.550]. El orden y las distancias son los de v2 en el test completo (−0.150, −0.458, −0.686); la
de DermLIP es menor en este subconjunto, que no es representativo del test.

Diferencial v3 (n = 248): 0.863, frente al par de candidatos impreso sin generador 0.847, Δ +0.016
[−0.020, +0.052], p = 0.42 (en v2: 0.831, por debajo del par). Frente al Swin forzado sobre las 163 imágenes
diferenciales que ya tienen reporte de Swin v3: 0.859 frente a 0.577, Δ +0.282 [+0.202, +0.362] (v2, n = 248:
+0.250). El *pipeline* completo frente al *grounding* simple necesita el Swin v3 entero (falta).

### 3.4 Nivel 1 en SkinCoT test (solo el reporte)

| Generador | Con `<think>` | Vacíos al quitarlo | Pares evaluados |
|---|---|---|---|
| Mini-VLM v3 | 291 / 457 | 80 (17.5 %) | 349 |
| LLaVA-Med v2 | 11 / 457 | 0 | 426 |

Sobre los 349 pares comunes (referencia y reporte no vacío en ambos):

| Generador | BLEU-4 | ROUGE-L | METEOR | CIDEr | BERTScore F1 |
|---|---|---|---|---|---|
| Mini-VLM v3 | 0.065 | 0.145 | 0.235 | 0.040 | 0.781 |
| LLaVA-Med v2 | 0.102 | 0.191 | 0.330 | 0.053 | 0.797 |

No hay Nivel 1 de Mini-VLM v2 sobre la partición de prueba de SkinCoT, así que la comparación v3–v2 en Nivel 1 no
se puede hacer.

## 4. Lectura

1. **El ajuste del LLM no cambia la cascada con Swin.** Swin por lesión −0.007 (n.s., 64 % del test) y el
   diferencial +0.032 (n.s.): la fidelidad viene del clasificador, como preveía el plan.
2. **v3 aprendió el formato de SkinCoT, y eso tiene un costo con 384 tokens.** Abre `<think>` en ~25 % de los
   reportes de HAM10000 y en 64 % de SkinCoT; en SkinCoT 17.5 % quedan vacíos y en el oracle la consistencia baja
   3.3 puntos porque el diagnóstico queda dentro del razonamiento. Es un efecto del presupuesto de tokens y de la
   métrica de solo el reporte, no de un peor diagnóstico.
3. **Con referencia, v3 queda por debajo de LLaVA-Med en las cinco métricas.**
4. **DermLIP v3 +0.021:** pequeño y significativo; sin la consistencia exclusiva no se sabe si viene de nombrar
   más candidatos.

## 5. Conclusión (veredicto)

**NO CUMPLE (incompleto).** El criterio «todos los brazos con sus conteos» no se cumple: faltan 540 reportes de
Swin por lesión, 1 131 de la línea base sin anclaje, RAG, ablaciones, MM-Skin test y la clasificación. Con lo
disponible, la conclusión del plan para el Cap. 5 se mantiene (v3 no cambia la cascada con Swin); queda por
decidir (autor) si las tablas pasan a v3, sabiendo que v3 baja el oracle a 0.967 y deja reportes vacíos en SkinCoT
por el `<think>`. Para cerrar: liberar los 12 tramos retenidos de `short` excluyendo ivb14 y recalcular con
`ensemble_bootstrap.py` una vez completo Swin por lesión.
