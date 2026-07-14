#!/bin/bash
#SBATCH --job-name=dermvlm_skinvl_prompts
#SBATCH --output=/home/%u/dermvlm/logs/skinvl/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/skinvl/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## P4.2 (mejoras.md #8) — SkinVL baseline con prompts alternativos.
## El baseline por defecto ("Describe this skin lesion.") colapsa a modo (72% reportes idénticos
## = "tinea corporis"). Se prueba si un fraseo distinto —más cercano al formato QA de MM-Skin, o
## que fuerce un diagnóstico— des-colapsa el modo. Si NINGUNO lo hace, se confirma que el colapso
## es mismatch de distribución MM-Skin->HAM y no del prompt. Subconjunto de 400.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== skinvl_baseline_prompts (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 400"

echo "=== (A) prompt diagnóstico directo ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --baseline_prompt "What is the most likely diagnosis for this skin lesion? Describe its key features." \
    --output_dir outputs/generated_reports/skinvl/prompt_diag
echo ""

echo "=== (B) prompt rol clínico ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --baseline_prompt "You are a dermatologist. Analyze this dermatoscopic image and give a diagnosis with supporting findings." \
    --output_dir outputs/generated_reports/skinvl/prompt_clinical
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
