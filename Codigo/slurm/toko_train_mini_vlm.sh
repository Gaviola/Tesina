#!/bin/bash
#SBATCH --job-name=dermvlm_mini_vlm
#SBATCH --output=/home/%u/scratch/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --ntasks=8
#SBATCH --time=72:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=EMAIL

. /etc/profile
source activate dermvlm

cd /home/$USER/scratch/dermvlm

nvidia-smi

# Mini-VLM: CLIP ViT-B/16 + Phi-3-mini (~8GB VRAM, compatible con Titan Xp 12GB)
# Stage 1: Alineamiento
python scripts/train_vlm_stage1.py --model mini_vlm --epochs 1 --lr 2e-3

# Stage 2: LoRA fine-tuning
python scripts/train_vlm_stage2.py --model mini_vlm --epochs 3 --lr 2e-5 --lora_r 64
