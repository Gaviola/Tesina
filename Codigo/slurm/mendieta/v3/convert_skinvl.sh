#!/bin/bash
#SBATCH --job-name=skinvl_convert
#SBATCH --output=/home/%u/dermvlm/logs/skinvl/convert_%j.out
#SBATCH --error=/home/%u/dermvlm/logs/skinvl/convert_%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Conversión de SkinVL-MM a formato HF (P1.1) + SMOKE TEST (5 imgs) en un solo job.
## Mendieta exige >=1 GPU; se aprovecha para validar la generación end-to-end.
## Requiere el cache HF ya poblado (base chaoyinshe + zwq803/SkinVL-MM). Lee offline.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm

echo "=== convert_skinvl (JOBID: $SLURM_JOB_ID) ==="; date; free -g | head -2; nvidia-smi

echo "=== 1) CONVERSIÓN a HF ==="
${PYTHON} scripts/convert_skinvl_to_hf.py --out data/checkpoints/skinvl-mm-hf || { echo "❌ CONVERSIÓN FALLÓ"; exit 1; }
echo "--- archivos generados ---"; ls -lah data/checkpoints/skinvl-mm-hf/ | head

echo "=== 2) SMOKE TEST (5 imgs: baseline + grounding oracle) ==="
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 5"
${PYTHON} scripts/generate_report.py ${COMMON} \
    --output_dir outputs/generated_reports/skinvl/smoke_baseline
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning \
    --output_dir outputs/generated_reports/skinvl/smoke_oracle

echo "=== 3) Reportes de prueba (inspeccionar coherencia) ==="
for f in outputs/generated_reports/skinvl/smoke_*/*.json; do
    echo "--- $f ---"
    ${PYTHON} -c "import json,sys; d=json.load(open(sys.argv[1])); print('gt:',d.get('gt_label'),'| dx:',d.get('grounded_dx')); print(d.get('report','')[:300])" "$f"
done
echo "=== Job completado ==="; date
