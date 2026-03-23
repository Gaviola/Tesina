#!/bin/bash
#SBATCH --job-name=dermvlm_classifier
#SBATCH --output=/home/%u/dermvlm/logs/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Clasificadores baseline: DenseNet121 + ViT-B/16
## GPU: A30 24GB (Ampere, bf16, CUDA 12.1)
## Dataset: HAM10000 (10015 imagenes, 7 categorias)

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_classifier (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi
echo "Python: $(${PYTHON} --version)"

# Limpiar bytecode corrupto de scipy
find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
echo ""

# Train DenseNet121
echo "--- Entrenando DenseNet121 ---"
${PYTHON} scripts/train_classifier.py --model densenet --epochs 30 --seed 42

echo ""

# Train ViT-B/16
echo "--- Entrenando ViT-B/16 ---"
${PYTHON} scripts/train_classifier.py --model vit --epochs 30 --seed 42

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
