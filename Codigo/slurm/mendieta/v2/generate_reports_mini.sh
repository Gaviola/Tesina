#!/bin/bash
#SBATCH --job-name=dermvlm_gen_mini_v2
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Mini-VLM v2: Generacion de reportes con checkpoint Stage 2 v2 (10 epochs)
## Datasets: MM-SkinQA + HAM10000 + SkinCoT
## Output: outputs/generated_reports/mini_vlm/v2/{dataset}/
##
## NOTA: el limite SLURM es 2 dias. Si el job se interrumpe por timeout,
## re-enviar el mismo job: generate_report.py tiene resume defensivo
## (skip reportes ya existentes) y continuara donde quedo.

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PYTHONUNBUFFERED=1

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_gen_mini_v2 (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi

GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ -n "$GPU_MEM_USED" ] && [ "$GPU_MEM_USED" -gt 500 ]; then
    echo "ADVERTENCIA: GPU ya tiene ${GPU_MEM_USED} MiB en uso por otro proceso"
    nvidia-smi --query-compute-apps=pid,used_memory --format=csv
fi

echo "Python: $(${PYTHON} --version)"

find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null

DATASETS="${DATASETS:-mmskin ham10000 skincare}"
echo "Datasets a procesar: ${DATASETS}"
echo ""

CHECKPOINT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"

if [[ "$DATASETS" == *"mmskin"* ]]; then
    echo "=== Generando reportes MM-SkinQA v2 ==="
    ${PYTHON} scripts/generate_report.py \
        --model mini_vlm \
        --checkpoint "${CHECKPOINT}" \
        --images_dir data/processed/MM-SkinQA \
        --reference_csv data/processed/MM-SkinQA/caption.csv \
        --output_dir outputs/generated_reports/mini_vlm/v2/mmskin \
        --max_tokens 512 \
        --seed 42
    echo ""
fi

if [[ "$DATASETS" == *"ham10000"* ]]; then
    echo "=== Generando reportes HAM10000 v2 ==="
    ${PYTHON} scripts/generate_report.py \
        --model mini_vlm \
        --checkpoint "${CHECKPOINT}" \
        --images_dir data/processed/HAM10000 \
        --output_dir outputs/generated_reports/mini_vlm/v2/HAM10000 \
        --max_tokens 512 \
        --seed 42
    echo ""
fi

if [[ "$DATASETS" == *"skincare"* ]]; then
    echo "=== Generando reportes SkinCoT v2 ==="
    ${PYTHON} scripts/generate_report.py \
        --model mini_vlm \
        --checkpoint "${CHECKPOINT}" \
        --images_dir data/raw/skincare/skincare/SkinCoT/images \
        --reference_dir data/raw/skincare/skincare/SkinCoT/EN \
        --output_dir outputs/generated_reports/mini_vlm/v2/skincare \
        --max_tokens 512 \
        --seed 42
    echo ""
fi

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
