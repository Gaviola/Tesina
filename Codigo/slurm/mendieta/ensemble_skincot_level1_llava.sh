#!/bin/bash
#SBATCH --job-name=dermvlm_skincot_l1_llava
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=1-00:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## ENSAMBLE — Nivel 1 sobre SkinCoT (que SÍ tiene reportes de referencia).
## Genera sobre el SkinCoT test split (460 imgs) bajo 2 condiciones:
##   (0) baseline : sin grounding
##   (A) oracle   : gt (clase DermNet) con prompt noreasoning
## Evaluación local: Nivel 1 (BLEU/ROUGE/BERTScore/METEOR/CIDEr) vs referencias + Nivel 2.
## Mide si el grounding/noreasoning afecta la calidad lingüística del reporte.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== skincot_l1_llava (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

CKPT="outputs/checkpoints/stage2_llava_med_v2/best_model.pt"
IMGS="data/raw/skincare/skincare/SkinCoT/images"
REFS="data/raw/skincare/skincare/SkinCoT/EN"
SPLIT="--splits_file data/splits/skincare_skincot_splits.json --split test"
COMMON="--model llava_med --checkpoint ${CKPT} --images_dir ${IMGS} --reference_dir ${REFS} ${SPLIT} --max_tokens 384 --seed 42"

echo "=== (0) BASELINE ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --output_dir outputs/generated_reports/llava_med/skincot_baseline
echo ""

echo "=== (A) ORACLE noreasoning ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/skincot_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/llava_med/skincot_oracle
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
