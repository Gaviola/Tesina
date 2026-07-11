#!/bin/bash
#SBATCH --job-name=dermvlm_smoke_skinvl
#SBATCH --output=/home/%u/dermvlm/logs/skinvl/smoke_%j.out
#SBATCH --error=/home/%u/dermvlm/logs/skinvl/smoke_%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=02:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## SMOKE TEST SkinVL (P1.1) — 5 imágenes, baseline + grounding oracle.
## Valida que el checkpoint convertido CARGA y GENERA reportes coherentes ANTES de la ola completa.
## Requiere: data/checkpoints/skinvl-mm-hf (convertido) subido al cluster.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm

echo "=== SMOKE SkinVL (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 5"

echo "=== baseline (5 imgs) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --output_dir outputs/generated_reports/skinvl/smoke_baseline

echo "=== grounding oracle noreasoning (5 imgs) ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/skinvl/smoke_oracle

echo "=== Reportes generados (inspeccionar coherencia) ==="
for f in outputs/generated_reports/skinvl/smoke_*/*.json; do
    echo "--- $f ---"; ${PYTHON} -c "import json,sys; d=json.load(open(sys.argv[1])); print('gt:',d.get('gt_label'),'| dx:',d.get('grounded_dx')); print(d.get('report','')[:300])" "$f"
done
echo "=== Smoke completado ==="; date
