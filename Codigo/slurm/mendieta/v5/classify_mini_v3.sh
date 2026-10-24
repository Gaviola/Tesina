#!/bin/bash
#SBATCH --job-name=dermvlm_classify_mini_v3
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00:00
#SBATCH --signal=B:SIGTERM@595

## Clasificación con el checkpoint de generación v3 de Mini-VLM (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md),
## igual que slurm/mendieta/v2/vlm_classify_mini_ft.sh. METHOD = likelihood | cot. Resultados en
## outputs/results/mini_vlm/v3/ (v2 no se toca).
source slurm/mendieta/v5/gen_common.sh
export WANDB_MODE=offline
METHOD="${METHOD:?falta METHOD}"
echo "=== classify_mini_v3 ${METHOD} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
[ -f "$CKPT_V3" ] || { echo "ERROR: falta ${CKPT_V3}"; exit 1; }

STAGING_DIR="outputs/_v3_staging/mini_vlm/${METHOD}_${SLURM_JOB_ID}"
mkdir -p "${STAGING_DIR}"
${PYTHON} scripts/train_vlm_classify.py \
    --model mini_vlm \
    --method "${METHOD}" \
    --checkpoint "${CKPT_V3}" \
    --output_dir "${STAGING_DIR}" \
    --batch_size 1 \
    --seed 42 \
    --wandb || FAILED=1

if [ "$FAILED" -eq 0 ] && [ -d "${STAGING_DIR}/results" ]; then
    mkdir -p outputs/results/mini_vlm/v3
    mv "${STAGING_DIR}/results"/*.json outputs/results/mini_vlm/v3/
    ls -la outputs/results/mini_vlm/v3/
    rm -rf "${STAGING_DIR}"
else
    echo "ERROR: train_vlm_classify.py falló; staging preservado en ${STAGING_DIR}"; FAILED=1
fi
finish
