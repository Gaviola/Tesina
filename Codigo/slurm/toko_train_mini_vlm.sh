#!/bin/bash
#SBATCH --job-name=dermvlm_mini_vlm
#SBATCH --output=/home/%u/scratch/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=72:00:00
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

. /etc/profile
source activate dermvlm

cd /home/$USER/scratch/dermvlm

# Usar almacenamiento local para archivos temporales; fallback a scratch si /tmp está lleno
export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

nvidia-smi

# Verificar que la GPU no esté ocupada por otro proceso
GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ -n "$GPU_MEM_USED" ] && [ "$GPU_MEM_USED" -gt 500 ]; then
    echo "ADVERTENCIA: GPU ya tiene ${GPU_MEM_USED} MiB en uso por otro proceso"
    nvidia-smi --query-compute-apps=pid,used_memory --format=csv
fi

# Mini-VLM: CLIP ViT-B/16 + Phi-3-mini (~8GB VRAM, RTX 4080 16GB)
# Stage 1: Alineamiento
python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1 --lr 2e-3

# Stage 2: LoRA fine-tuning
python scripts/train_vlm_stage2.py --model mini_vlm --epochs 3 --lr 2e-5 --lora_r 64

rm -rf "$TMPDIR"
