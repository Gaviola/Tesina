#!/bin/bash
#SBATCH --job-name=dermvlm_s1_mini
#SBATCH --output=/home/%u/scratch/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --ntasks=8
#SBATCH --time=12:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Mini-VLM Stage 1: Alineamiento visual-textual (MLP projection)
## Modelo: CLIP ViT-B/16 + Phi-3-mini
## GPU: RTX 4080 16GB (Ampere, bf16, CUDA 12.6)
## Dataset: MM-Skin captions (~11k pares imagen-texto)

. /etc/profile

# Usar ruta absoluta al entorno conda (source activate no funciona en SLURM)
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"

cd /home/$USER/scratch/dermvlm

echo "=== Iniciando dermvlm_s1_mini (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi
echo "Python: $(${PYTHON} --version)"
echo ""

${PYTHON} scripts/train_vlm_stage1.py \
    --model mini_vlm \
    --epochs 1 \
    --lr 2e-3 \
    --batch_size 8 \
    --seed 42

echo ""
echo "=== Job completado ==="
date
