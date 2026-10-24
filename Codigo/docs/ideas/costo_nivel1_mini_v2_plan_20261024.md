# Plan — Nivel 1 de Mini-VLM v2 en SkinCoT y memoria medida de los generadores (24/10/2026)

## Motivación

Dos huecos del Cap. 5 (decisión del autor del 24/10, preguntas 2 y 4 de `fichas/05-resultados-generacion/00-capitulo.md`):

1. **Nivel 1 de Mini-VLM v2 en la prueba de SkinCoT.** No existe: la configuración principal solo tiene Nivel 1 en
   MM-Skin, y en SkinCoT solo LLaVA-Med v2 y el control Mini-VLM v3
   ([resul v3](../resul/mini_vlm_lora_llm_resul_v3_20261024.md) §3.4). `tab:res_gen_nivel1` queda incompleta.
2. **Memoria de los generadores.** `tab:res_costo_generadores` la estima como parámetros × 2 bytes (bf16), sin la que
   ocupa la generación, y los parámetros de LLaVA-Med y SkinVL están redondeados a 7 000 millones. El Cap. 4 midió la
   de los clasificadores con `torch.cuda.max_memory_allocated` (`measure_cost.py`); se hace lo mismo con los
   generadores.

## Experimento

**(1) Nivel 1.** `slurm/mendieta/v5/gen_short_level1_mini_v2.sh` (nuevo, `SHARD`): mismos argumentos que el brazo
`skincot_test` de `gen_short_mini_v3.sh` con el checkpoint `stage2_mini_vlm_v2` (instrucción de base, 384 tokens,
semilla 42). Salida `outputs/generated_reports/mini_vlm/v2/skincot_test/` (no existe; no pisa nada). Cuatro tramos de
una hora en `short` (~115 reportes por tramo; sin ancla los reportes son más largos que los 16.4 s de la cascada).
Evaluación al bajar, igual que la de v3 y LLaVA-Med:

```
python scripts/evaluate_reports.py --model mini_vlm --level 1 --dataset v2/skincot_test --strip-reasoning --output_dir outputs/results/level1_test/skincot_test
```

**(2) Memoria.** `scripts/measure_vlm_memory.py` (nuevo) carga el generador con `_load_model_with_checkpoint` de
`generate_report.py` (bf16, mismo checkpoint y LoRA), cuenta los parámetros y mide `max_memory_allocated` al cargar y
durante 20 reportes de la cascada con Swin-Tiny (plantilla `noreasoning`, 384 tokens, primeras 20 imágenes de la
prueba). `slurm/mendieta/v5/measure_vlm_memory.sh` (`MODEL`), un job por generador en `short`. Salida
`outputs/results/cost/vlm_memory_<modelo>.json`.

## Hipótesis y veredicto

- H1: en SkinCoT, Mini-VLM v2 queda en el orden de LLaVA-Med v2 (BERTScore ~0.78–0.80), y sin bloques `<think>`
  (v2 no los abre en HAM10000). CUMPLE si hay ≥ 420 pares evaluados y BERTScore ∈ [0.75, 0.82].
- H2: la memoria medida al cargar queda cerca de la estimación (Mini ~8 GB, LLaVA-Med y SkinVL ~14 GB) y el pico de
  generación suma menos de 1 GB. CUMPLE si los tres jobs terminan y Mini-VLM queda por debajo de 12 GB en el pico
  (lo que sostiene la frase de que entra en una RTX 4070); si no, se corrige el texto.

## Sincronización con clústeres

Se suben por `scp` solo los tres archivos nuevos (`measure_vlm_memory.py` y los dos `.sh`), con md5 verificado; no se
usa `sync_up --delete`. `generate_report.py`, `src/models/*` y `src/training/lora_config.py` remotos son idénticos a
los locales (md5 sin finales de línea, 24/10). Los reportes se bajan por `tar` sobre ssh a
`outputs/generated_reports/mini_vlm/v2/skincot_test/` y los JSON de memoria por `scp` a `outputs/results/cost/`.
