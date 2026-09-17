#!/bin/bash
#SBATCH --job-name=dermvlm_reanchor_skinvl
#SBATCH --output=/home/%u/dermvlm/logs/skinvl/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/skinvl/%j.err
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

## RE-ANCLAJE de la cascada al clasificador del split disjunto por lesión, para SkinVL.
## Solo el brazo full_swin: SkinVL no participa del ruteo de 3 niveles.
## SkinVL es un checkpoint FULL, se carga desde SkinVL.MODEL_NAME (sin --checkpoint LoRA).
## Ver docs/ideas/criterio_seleccion_plan_20260917.md.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== reanchor_skinvl (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== grounding Swin del split por lesión, noreasoning (n=1503) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/skinvl/full_swin_les
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
