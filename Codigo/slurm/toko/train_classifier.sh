#!/bin/bash
#SBATCH --job-name=dermvlm_classifier
#SBATCH --output=/home/%u/scratch/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/shared/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=12:00:00
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Clasificadores baseline: DenseNet121 + ViT-B/16
## GPU: RTX 4080 16GB (Ada Lovelace, bf16, CUDA 12.6)
## Dataset: HAM10000 (10015 imagenes, 7 categorias)

. /etc/profile

# Usar ruta absoluta al entorno conda (source activate no funciona en SLURM)
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

cd /home/$USER/scratch/dermvlm

export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_classifier (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi
echo "Python: $(${PYTHON} --version)"
echo ""

# Entrenar DenseNet121 — mejores hiperparametros del sweep fase1
# val_acc=0.877 | lr=7.91e-5, scheduler=CosineAnnealingLR, weight_decay=0.01, label_smoothing=0, freeze=false
echo "--- Entrenando DenseNet121 ---"
${PYTHON} scripts/train_classifier.py \
    --model densenet \
    --epochs 30 \
    --seed 42 \
    --lr 7.91e-5 \
    --weight-decay 0.01 \
    --scheduler CosineAnnealingLR \
    --label-smoothing 0.0 \
    --no-freeze-backbone

echo ""

# Entrenar ViT-B/16 — mejores hiperparametros del sweep fase1
# val_acc=0.857 | lr=1.56e-5, scheduler=none, weight_decay=0.01, label_smoothing=0, freeze=false
echo "--- Entrenando ViT-B/16 ---"
${PYTHON} scripts/train_classifier.py \
    --model vit \
    --epochs 30 \
    --seed 42 \
    --lr 1.56e-5 \
    --weight-decay 0.01 \
    --scheduler none \
    --label-smoothing 0.0 \
    --no-freeze-backbone

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
