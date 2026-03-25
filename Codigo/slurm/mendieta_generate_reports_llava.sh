#!/bin/bash
#SBATCH --job-name=dermvlm_gen_llava
#SBATCH --output=/home/%u/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/%j.err
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

## LLaVA-Med: Generacion de reportes clinicos en batch (~14GB LoRA en A30 24GB)
## Modelo: CLIP ViT-L/14 + Mistral-7B-Med (Stage 2 fine-tuned)
## Datasets: MM-SkinQA (Nivel 1 con referencias) + HAM10000 (Nivel 2 NER)

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

# Nodos de computo no tienen internet — usar modelos pre-descargados del cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_gen_llava (JOBID: $SLURM_JOB_ID) ==="
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
echo ""

# --- Paso 1: Reportes sobre MM-SkinQA (evaluacion Nivel 1 con referencias) ---
echo "=== Generando reportes MM-SkinQA (Nivel 1) ==="
${PYTHON} scripts/generate_report.py \
    --model llava_med \
    --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt \
    --images_dir data/raw/MM-SkinQA \
    --reference_csv data/raw/MM-SkinQA/caption.csv \
    --output_dir outputs/generated_reports/llava_med/mmskin \
    --max_tokens 512 \
    --seed 42

echo ""

# --- Paso 2: Reportes sobre HAM10000 (evaluacion Nivel 2 NER) ---
echo "=== Generando reportes HAM10000 (Nivel 2) ==="
${PYTHON} scripts/generate_report.py \
    --model llava_med \
    --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt \
    --images_dir data/processed/HAM10000 \
    --output_dir outputs/generated_reports/llava_med/HAM10000 \
    --max_tokens 512 \
    --seed 42

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
