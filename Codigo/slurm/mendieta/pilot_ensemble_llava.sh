#!/bin/bash
#SBATCH --job-name=dermvlm_pilot_ensemble_llava
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=10:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## PILOT ENSAMBLE (cascada clasificador->generador): de-risk del grounding.
## Genera ~100 reportes HAM con LLaVA-Med Stage 2 v2 bajo DOS condiciones sobre
## las MISMAS imágenes (--limit 100, orden determinístico):
##   (0) baseline : prompt actual "Describe this skin lesion." (hedea)
##   (A) oracle   : grounded con el gt_label de HAM (cota superior del grounding)
## Luego se evalúa diagnostic_consistency local y se compara el delta.
## Ver plan: docs/ideas/ensamble_clasificador_generador_plan_20260605.md

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1

cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== Iniciando pilot_ensemble_llava (JOBID: $SLURM_JOB_ID) ==="
date; echo "Nodo: $(hostname)"; nvidia-smi
echo "Python: $(${PYTHON} --version)"
echo ""

CHECKPOINT="outputs/checkpoints/stage2_llava_med_v2/best_model.pt"
LIMIT=100
DXCSV="outputs/pilot_ham_dx.csv"

# --- Construir CSV oracle (image_id -> dx completo) desde metadata HAM ---
echo "=== Construyendo CSV oracle de diagnósticos ==="
${PYTHON} -c "
import sys; sys.path.insert(0,'scripts'); sys.path.insert(0,'.')
from pathlib import Path
from enrich_reports import _build_label_map
import csv
lm=_build_label_map(Path('data/processed/HAM10000'))
import os; os.makedirs('outputs', exist_ok=True)
with open('${DXCSV}','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f); w.writerow(['image_id','diagnosis','disease'])
    for iid,dx in lm.items(): w.writerow([iid,dx,dx])
print('CSV oracle:', len(lm), 'filas')
"
echo ""

# --- (0) BASELINE: prompt actual, sin grounding ---
echo "=== (0) BASELINE — sin grounding ==="
${PYTHON} scripts/generate_report.py \
    --model llava_med \
    --checkpoint "${CHECKPOINT}" \
    --images_dir data/processed/HAM10000 \
    --label_csv "${DXCSV}" \
    --output_dir outputs/generated_reports/llava_med/pilot_baseline \
    --max_tokens 256 --limit ${LIMIT} --seed 42
echo ""

# --- (A) ORACLE: grounded con gt_label ---
echo "=== (A) ORACLE — grounded con gt_label ==="
${PYTHON} scripts/generate_report.py \
    --model llava_med \
    --checkpoint "${CHECKPOINT}" \
    --images_dir data/processed/HAM10000 \
    --label_csv "${DXCSV}" \
    --diagnosis_source "${DXCSV}" --grounded_prompt \
    --output_dir outputs/generated_reports/llava_med/pilot_oracle \
    --max_tokens 256 --limit ${LIMIT} --seed 42
echo ""

echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
