#!/bin/bash
#SBATCH --job-name=dermvlm_vlm_memory
#SBATCH --output=/home/%u/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/shared/%j.err
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
## ivb02 e ivb11 fallan al arrancar con «user env retrieval failed» (19–20/10); se excluyen.
#SBATCH --exclude=ivb02,ivb11

## Memoria de GPU y parámetros de un generador, medidos en la A30 con 20 reportes de la cascada con Swin-Tiny
## (plan docs/ideas/costo_nivel1_mini_v2_plan_20261024.md). Variable: MODEL (mini_vlm | llava_med | skinvl).
source slurm/mendieta/v5/gen_common.sh
: "${MODEL:?falta MODEL}"
echo "=== vlm_memory ${MODEL} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
case "$MODEL" in
    mini_vlm)  CKPT_ARG="--checkpoint outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt" ;;
    llava_med) CKPT_ARG="--checkpoint outputs/checkpoints/stage2_llava_med_v2/best_model.pt" ;;
    skinvl)    CKPT_ARG="" ;;
    *) echo "ERROR: modelo desconocido ${MODEL}"; exit 1 ;;
esac

${PYTHON} scripts/measure_vlm_memory.py --model ${MODEL} ${CKPT_ARG} --n 20 \
    --output outputs/results/cost/vlm_memory_${MODEL}.json \
    || { echo "ERROR: measure_vlm_memory.py salió con código $?"; FAILED=1; }
finish
