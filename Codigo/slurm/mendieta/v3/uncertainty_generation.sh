#!/bin/bash
#SBATCH --job-name=dermvlm_unc_gen
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## P5.4 (incertidumbre) — Mini-VLM, n=400.
## Genera con el modo consciente de incertidumbre: si el clasificador (Swin calibrado con temperature
## scaling) está SEGURO -> reporte definitivo con su top-1; si NO -> reporte DIFERENCIAL con los
## candidatos top-k. CSV precomputado local (scripts/temperature_scaling.py -> outputs/uncertainty/).
## Se compara contra full_swin (grounding siempre-definitivo) y full_oracle, ya existentes.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== uncertainty_generation (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

MODEL="mini_vlm"; CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model ${MODEL} --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 400"

echo "=== uncertainty-aware (definitivo si seguro, diferencial si no) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --uncertainty_csv outputs/uncertainty/uncertainty.csv --uncertainty \
    --output_dir outputs/generated_reports/${MODEL}/full_uncertainty
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
