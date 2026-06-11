#!/bin/bash
#SBATCH --job-name=dermvlm_pilot_ens_v2_llava
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

## PILOT ENSAMBLE v2 — rediseño del prompt de grounding.
## El pilot 1 mostró que el grounding "soft" es débil (oracle solo 0.60; el modelo
## ignora el dx ~40%). Acá se prueban 3 variantes que FUERZAN el commitment, todas
## en modo oracle (gt) sobre las MISMAS 100 imágenes, para ver cuál sube el techo.
## max_tokens 384 (vs 256) para reducir truncamiento antes de enunciar el dx.
## Ver plan: docs/ideas/ensamble_clasificador_generador_plan_20260605.md

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== pilot_ensemble_v2_llava (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

CHECKPOINT="outputs/checkpoints/stage2_llava_med_v2/best_model.pt"
LIMIT=100
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

for VAR in dxfirst conclude confirmed; do
    echo "=== ORACLE variante: ${VAR} ==="
    ${PYTHON} scripts/generate_report.py \
        --model llava_med --checkpoint "${CHECKPOINT}" \
        --images_dir data/processed/HAM10000 --label_csv "${DXCSV}" \
        --diagnosis_source "${DXCSV}" --grounded_prompt --grounded_variant ${VAR} \
        --output_dir outputs/generated_reports/llava_med/pilot_v2_${VAR} \
        --max_tokens 384 --limit ${LIMIT} --seed 42
    echo ""
done

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
