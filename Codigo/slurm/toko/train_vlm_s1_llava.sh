#!/bin/bash
#SBATCH --job-name=dermvlm_s1_llava
#SBATCH --output=/home/%u/scratch/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/llava_med/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## LLaVA-Med Stage 1: Alineamiento visual-textual (MLP projection)
## Modelo: CLIP ViT-L/14 + Mistral-7B-Med
## GPU: RTX 4080 16GB (Ampere, bf16, CUDA 12.6) — 16GB VRAM suficiente para LoRA
## Dataset: MM-Skin captions (~11k pares imagen-texto)

. /etc/profile

# Usar ruta absoluta al entorno conda (source activate no funciona en SLURM)
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"

# bitsandbytes necesita libcusparse de CUDA — apuntar a las libs del entorno conda
# (PyTorch cu118 incluye estas libs en el prefijo de conda)
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

cd /home/$USER/scratch/dermvlm

# Usar almacenamiento local para archivos temporales; fallback a scratch si /tmp está lleno
export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_s1_llava (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi

# Verificar que la GPU no esté ocupada por otro proceso
GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ -n "$GPU_MEM_USED" ] && [ "$GPU_MEM_USED" -gt 500 ]; then
    echo "ADVERTENCIA: GPU ya tiene ${GPU_MEM_USED} MiB en uso por otro proceso"
    nvidia-smi --query-compute-apps=pid,used_memory --format=csv
fi

# Limpiar bytecode corrupto de scipy (UnicodeDecodeError en _tanhsinh.pyc)
find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
echo ""

${PYTHON} scripts/train_vlm_stage1.py \
    --model llava_med \
    --epochs 1 \
    --lr 2e-3 \
    --batch_size 4 \
    --num_workers 0 \
    --seed 42

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
