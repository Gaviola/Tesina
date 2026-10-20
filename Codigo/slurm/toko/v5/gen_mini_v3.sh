#!/bin/bash
#SBATCH --job-name=dermvlm_gen_mini_v3
#SBATCH --output=/home/%u/scratch/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --exclusive

## Brazos de la cascada de Mini-VLM v3 que no corren en Mendieta (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md):
## oracle y dermlip con grounding noreasoning sobre la prueba de HAM10000 (1503), mismos argumentos que
## slurm/mendieta/v5/cascade_mini_v3.sh. Checkpoint copiado de Mendieta (job 1179985). generate_report.py saltea
## los reportes ya válidos: si el job se corta, se reenvía el mismo script. Los reportes se juntan en local con los
## de Mendieta (outputs/generated_reports/mini_vlm_v3/). La partición gpu de TOKO limita a 12 h: se encadenan dos envíos.
. /etc/profile
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/scratch/dermvlm
export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== gen_mini_v3 (JOBID: $SLURM_JOB_ID) ==="; date; hostname; nvidia-smi
CKPT="outputs/checkpoints/stage2_mini_vlm_v3/best_model.pt"
[ -f "$CKPT" ] && [ -f "$(dirname $CKPT)/lora_config.json" ] || { echo "ERROR: falta ${CKPT} o lora_config.json"; exit 1; }
OUT="outputs/generated_reports/mini_vlm_v3"
COMMON="--model mini_vlm --checkpoint ${CKPT} --images_dir data/processed/HAM10000 \
    --splits_file data/splits/ham10000_splits.json --split test --max_tokens 384 --seed 42"

FAILED=0
for COND in oracle dermlip; do
    echo "=== (${COND}) grounding noreasoning ==="; date
    ${PYTHON} scripts/generate_report.py ${COMMON} --diagnosis_source outputs/full_dx_${COND}.csv \
        --grounded_prompt --grounded_variant noreasoning --output_dir ${OUT}/full_${COND} || FAILED=1
    n=$(find ${OUT}/full_${COND} -name '*_report.json' | wc -l); echo "Reportes en ${OUT}/full_${COND}: ${n}/1503"
    [ "$n" -ge 1503 ] || FAILED=1
done
rm -rf "$TMPDIR"
[ "$FAILED" -eq 0 ] || { echo "=== Job FALLIDO ==="; date; exit 1; }
echo "=== Job completado ==="; date
