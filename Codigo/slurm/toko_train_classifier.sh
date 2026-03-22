#!/bin/bash
#SBATCH --job-name=dermvlm_classifier
#SBATCH --output=/home/%u/scratch/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --ntasks=8
#SBATCH --time=48:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

. /etc/profile
source activate dermvlm

cd /home/$USER/scratch/dermvlm

# Verificar GPU
nvidia-smi
echo "CUDA version: $(nvcc --version | tail -1)"

# Entrenar DenseNet121
python scripts/train_classifier.py --model densenet --epochs 30 --seed 42

# Entrenar ViT-B/16
python scripts/train_classifier.py --model vit --epochs 30 --seed 42
