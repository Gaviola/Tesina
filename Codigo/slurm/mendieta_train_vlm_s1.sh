#!/bin/bash
#SBATCH --job-name=dermvlm_llava_s1
#SBATCH --output=/home/%u/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus-per-task=1
#SBATCH --time=1-00:00:00

. /etc/profile
# Opción A: entorno conda directo (si CUDA del cluster es compatible)
source activate dermvlm
# Opción B: Singularity (si se necesita CUDA empaquetado)
# singularity exec --nv /home/$USER/containers/dermvlm.sif \

nvidia-smi

# LLaVA-Med Stage 1: Alineamiento (solo MLP, ~14GB VRAM en A30 24GB)
python scripts/train_vlm_stage1.py --model llava_med --epochs 1 --lr 2e-3 --batch_size 16
