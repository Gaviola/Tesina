#!/bin/bash
#SBATCH --job-name=dermvlm_pilot_ens_v3_llava
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
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

## PILOT ENSAMBLE v3 — último lever de prompt: prohibir el razonamiento.
## El re-pilot (v2) dio "confirmed" report-only 0.70 pero aún 53% de razonamiento.
## Acá la variante "noreasoning" prohíbe explícitamente <think>/reasoning.
## Oracle (gt) sobre las MISMAS 100 imgs, max_tokens 384.
## Ver: docs/resul/ensamble_resul_20260607.md §4

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== pilot_ensemble_v3_llava (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

CHECKPOINT="outputs/checkpoints/stage2_llava_med_v2/best_model.pt"
DXCSV="outputs/pilot_ham_dx.csv"

echo "=== CSV oracle ==="
${PYTHON} -c "
import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'.')
from pathlib import Path; from enrich_reports import _build_label_map; import csv, os
lm=_build_label_map(Path('data/processed/HAM10000')); os.makedirs('outputs',exist_ok=True)
with open('${DXCSV}','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['image_id','diagnosis','disease'])
    for iid,dx in lm.items(): w.writerow([iid,dx,dx])
print('CSV oracle:',len(lm),'filas')
"

echo "=== ORACLE variante: noreasoning ==="
${PYTHON} scripts/generate_report.py \
    --model llava_med --checkpoint "${CHECKPOINT}" \
    --images_dir data/processed/HAM10000 --label_csv "${DXCSV}" \
    --diagnosis_source "${DXCSV}" --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/llava_med/pilot_v3_noreasoning \
    --max_tokens 384 --limit 100 --seed 42

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
