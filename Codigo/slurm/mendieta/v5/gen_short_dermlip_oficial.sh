#!/bin/bash
#SBATCH --job-name=dermvlm_short_dermlip_of
#SBATCH --output=/home/%u/dermvlm/logs/dermlip_oficial/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/dermlip_oficial/%j.err
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
## ivb02 e ivb11 fallan al arrancar con «user env retrieval failed» (19–20/10); se excluyen.
#SBATCH --exclude=ivb02,ivb11

## Un tramo del brazo full_dermlip_oficial: la cascada con el diagnóstico de DermLIP zero-shot según el protocolo
## oficial de Derm1M (docs/ideas/cascada_dermlip_oficial_plan_20261024.md). Mismos argumentos que full_swin_les
## (slurm/mendieta/v4/reanchor_*.sh). generate_report.py saltea los reportes ya válidos, así que un tramo cortado a la
## hora se completa reenviándolo.
## Variables: MODEL (mini_vlm | llava_med | skinvl) y SHARD (K/N, K desde 0).
source slurm/mendieta/v5/gen_common.sh
: "${MODEL:?falta MODEL}" "${SHARD:?falta SHARD}"
echo "=== short_dermlip_oficial ${MODEL} shard ${SHARD} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
case "$MODEL" in
    mini_vlm)  CKPT_ARG="--checkpoint outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt" ;;
    llava_med) CKPT_ARG="--checkpoint outputs/checkpoints/stage2_llava_med_v2/best_model.pt" ;;
    skinvl)    CKPT_ARG="" ;;
    *) echo "ERROR: modelo desconocido ${MODEL}"; exit 1 ;;
esac
DX="outputs/full_dx_dermlip_oficial.csv"
[ -f "$DX" ] || { echo "ERROR: falta ${DX}"; exit 1; }
OUT="outputs/generated_reports/${MODEL}/full_dermlip_oficial"

${PYTHON} scripts/generate_report.py --model ${MODEL} ${CKPT_ARG} ${HAM_TEST} --max_tokens 384 --seed 42 \
    --shard ${SHARD} --diagnosis_source ${DX} --grounded_prompt --grounded_variant noreasoning --output_dir "${OUT}" \
    || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
echo "Reportes en ${OUT}: $(find "${OUT}" -name '*_report.json' 2>/dev/null | wc -l) (todos los tramos)"
finish
