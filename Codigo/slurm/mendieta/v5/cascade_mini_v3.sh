#!/bin/bash
#SBATCH --job-name=dermvlm_cascade_mini_v3
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

## Cascada con Mini-VLM v3 (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md): los mismos brazos que v2 sobre el
## test por lesión. generate_report.py tiene resume defensivo: si el job se corta, se reenvía el mismo script.
source slurm/mendieta/v5/gen_common.sh
echo "=== cascade_mini_v3 (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
[ -f "$CKPT_V3" ] || { echo "ERROR: falta ${CKPT_V3}"; exit 1; }
OUT="outputs/generated_reports/mini_vlm_v3"
COMMON="--model mini_vlm --checkpoint ${CKPT_V3} ${HAM_TEST} --max_tokens 384 --seed 42"

echo "=== (1) sin anclaje ==="
run_arm ${OUT}/full_baseline 1503 ${COMMON}
for COND in swin_les oracle dermlip; do
    echo "=== (${COND}) grounding noreasoning ==="
    run_arm ${OUT}/full_${COND} 1503 ${COMMON} --diagnosis_source outputs/full_dx_${COND}.csv --grounded_prompt --grounded_variant noreasoning
done
echo "=== nivel diferencial del ruteo por lesión (n=248) ==="
run_arm ${OUT}/full_differential_les 248 ${COMMON} --uncertainty_csv outputs/uncertainty/uncertainty_differential_les.csv --uncertainty --only_ids_csv outputs/uncertainty/uncertainty_differential_les.csv
finish
