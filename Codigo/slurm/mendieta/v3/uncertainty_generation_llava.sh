#!/bin/bash
#SBATCH --job-name=dermvlm_unc_gen_llava
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Replica del ensamble consciente de la incertidumbre con el SEGUNDO generador (LLaVA-Med).
## Cierra la limitacion "validado sobre un solo generador": el nivel afirmativo reutiliza full_swin
## de LLaVA (ya existente, 1503) y el de abstencion no genera; solo faltan los 334 reportes del
## nivel DIFERENCIAL. Mismos hiperparametros que la corrida de Mini-VLM y que full_swin de LLaVA
## (checkpoint v2, max_tokens 384, seed 42) para que la comparacion sea pareada.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== uncertainty_generation_llava (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

MODEL="llava_med"; CKPT="outputs/checkpoints/stage2_llava_med_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model ${MODEL} --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== LLaVA-Med: reportes DIFERENCIALES del ruteo de 3 niveles (n=334) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --uncertainty_csv outputs/uncertainty/uncertainty_differential.csv --uncertainty \
    --only_ids_csv outputs/uncertainty/uncertainty_differential.csv \
    --output_dir outputs/generated_reports/${MODEL}/full_differential
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
