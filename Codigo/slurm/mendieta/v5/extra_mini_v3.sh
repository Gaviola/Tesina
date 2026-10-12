#!/bin/bash
#SBATCH --job-name=dermvlm_extra_mini_v3
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

## Brazos de recuperación y ablaciones con Mini-VLM v3 (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md).
## Sin repetition_penalty: crashea en Mini-VLM (ver slurm/mendieta/v3/rag_generation.sh).
source slurm/mendieta/v5/gen_common.sh
echo "=== extra_mini_v3 (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
[ -f "$CKPT_V3" ] || { echo "ERROR: falta ${CKPT_V3}"; exit 1; }
RAG_CSV="outputs/rag/rag_context_les.csv"
[ -f "$RAG_CSV" ] || { echo "ERROR: falta ${RAG_CSV}"; exit 1; }
OUT="outputs/generated_reports/mini_vlm_v3"
COMMON="--model mini_vlm --checkpoint ${CKPT_V3} ${HAM_TEST} --max_tokens 384 --seed 42"

echo "=== (1) RAG solo, índice por lesión (n=1503) ==="
run_arm ${OUT}/full_rag_les 1503 ${COMMON} --rag_context_csv ${RAG_CSV} --rag
echo "=== (2) Swin por lesión + RAG (n=1503) ==="
run_arm ${OUT}/full_swin_rag_les 1503 ${COMMON} --diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt --grounded_variant noreasoning --rag_context_csv ${RAG_CSV}
echo "=== (3) ablación: oracle sin imagen (n=400) ==="
run_arm ${OUT}/full_oracle_noimage 400 ${COMMON} --limit 400 --diagnosis_source outputs/full_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning --no_image
echo "=== (4) ablación: diagnóstico equivocado (n=400) ==="
run_arm ${OUT}/full_wrong_swap 400 ${COMMON} --limit 400 --diagnosis_source outputs/full_dx_wrong_swap.csv --grounded_prompt --grounded_variant noreasoning
finish
