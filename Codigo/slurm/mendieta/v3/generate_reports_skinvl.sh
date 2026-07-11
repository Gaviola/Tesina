#!/bin/bash
#SBATCH --job-name=dermvlm_ensemble_skinvl
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

## OLA 1 (P1.1) — SkinVL-MM (VLM derm-especializado) en el ensamble cascada.
## Tercer generador para la comparación de especialización en generación.
## REQUIERE: checkpoint convertido a formato HF en data/checkpoints/skinvl-mm-hf
##           (ver docs/ideas/skinvl_ensemble_plan_20260705.md). Validar carga ANTES.
## Condiciones: baseline + grounding{oracle,swin,dermlip} + no_image (P1.2) + dx-erróneo (P1.3).

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== ensemble_skinvl (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

## SkinVL es un checkpoint FULL: se carga desde SkinVL.MODEL_NAME (sin --checkpoint LoRA).
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== (0) BASELINE (sin grounding) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --output_dir outputs/generated_reports/skinvl/full_baseline
echo ""

for COND in oracle swin dermlip; do
    echo "=== (${COND}) grounded noreasoning ==="
    ${PYTHON} scripts/generate_report.py ${COMMON} \
        --diagnosis_source outputs/full_dx_${COND}.csv --grounded_prompt --grounded_variant noreasoning \
        --output_dir outputs/generated_reports/skinvl/full_${COND}
    echo ""
done

echo "=== (P1.2) imagen-vs-dx: grounding oracle SIN imagen ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning \
    --no_image \
    --output_dir outputs/generated_reports/skinvl/full_oracle_noimage
echo ""

echo "=== (P1.3) dx-erróneo: grounding con dx confundible ==="
## Generar el CSV antes (local o en el nodo):
##   python scripts/make_wrong_dx.py --input outputs/full_dx_oracle.csv \
##       --output outputs/full_dx_wrong_swap.csv --mode swap
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_wrong_swap.csv --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/skinvl/full_wrong_swap
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
