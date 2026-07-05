#!/bin/bash
#SBATCH --job-name=dermvlm_ensemble_full_mini
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
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## ENSAMBLE — corrida completa con MINI-VLM (espejo de ensemble_full_llava.sh).
## Segundo generador para la comparación cross-model. 4 condiciones, prompt noreasoning,
## subconjunto del HAM test split (~400 imgs). Mismas CSVs de grounding (model-agnostic).

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== ensemble_full_mini (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
## Sin --limit: corre el test split completo (1503). Resume defensivo saltea las 400 ya hechas.
COMMON="--model mini_vlm --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== (0) BASELINE ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --output_dir outputs/generated_reports/mini_vlm/full_baseline
echo ""

for COND in oracle swin dermlip; do
    echo "=== (${COND}) grounded noreasoning ==="
    ${PYTHON} scripts/generate_report.py ${COMMON} \
        --diagnosis_source outputs/full_dx_${COND}.csv --grounded_prompt --grounded_variant noreasoning \
        --output_dir outputs/generated_reports/mini_vlm/full_${COND}
    echo ""
done

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
