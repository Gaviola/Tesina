# Plan — Cascada con diagnóstico de DermLIP oficial (24/10/2026)

## Motivación

La tesina pasó el zero-shot de DermLIP al protocolo oficial de Derm1M
([resul](../resul/dermlip_zs_protocolo_resul_20261024.md)): exactitud 0.716 en lugar de 0.377. La condición
`full_dermlip` de la cascada (Cap. 5) usa los diagnósticos anteriores (`outputs/full_dx_dermlip.csv`, exactitud 0.38).
Se regenera con los nuevos para que el Cap. 5 describa el mismo DermLIP que el Cap. 4.

## Experimento

- Diagnósticos: `outputs/full_dx_dermlip_oficial.csv` (`make_dx_csv.py` sobre
  `dermlip_zeroshot_vit-b-16_oficial_predictions.json`; 1 503 filas, 0.716 de acuerdo con el oráculo).
- Brazo nuevo `full_dermlip_oficial` para los tres generadores, con los mismos argumentos que `full_swin_les` y el
  `full_dermlip` anterior: `--grounded_prompt --grounded_variant noreasoning --max_tokens 384 --seed 42`, checkpoints
  `stage2_mini_vlm_v2` y `stage2_llava_med_v2`, SkinVL completo. Salida en
  `outputs/generated_reports/{mini_vlm,llava_med,skinvl}/full_dermlip_oficial/` (no pisa nada).
- Partición `short` (1 h), `slurm/mendieta/v5/gen_short_dermlip_oficial.sh` con `MODEL` y `SHARD`. Tramos según el
  tiempo por reporte medido (Mini 16.4 s, LLaVA 26.2 s, SkinVL 3.4 s): Mini 10, LLaVA 15, SkinVL 3 (28 jobs, ~20 h
  de GPU). Un tramo cortado se completa reenviándolo (se saltean los reportes válidos).
- Al bajar: métrica oficial (solo reporte, matcher estricto) con `ensemble_bootstrap.py`, comparando
  `full_dermlip_oficial` con `full_swin_les`, `full_oracle` y `full_baseline`.

## Hipótesis y veredicto

H: con un diagnóstico de exactitud 0.716 (entre el anterior 0.38 y Swin 0.847), la consistencia del reporte queda
entre la del `full_dermlip` anterior y la de `full_swin_les`. CUMPLE si los tres generadores terminan las 1 503 y la
consistencia queda en ese intervalo; si no, se describe lo que se observe. Plazo: si el 27/10 no terminó, el Cap. 5
usa la condición anterior como control de clasificador débil (decisión del autor del 24/10).

## Sincronización con clústeres

Se suben por `scp` solo `outputs/full_dx_dermlip_oficial.csv` y el script nuevo (md5 verificado); no se usa
`sync_up --delete`. El código de generación no cambia (`generate_report.py` remoto tiene `--shard`). Los reportes se
bajan por `tar` sobre ssh a `outputs/generated_reports/<modelo>/full_dermlip_oficial/`.
