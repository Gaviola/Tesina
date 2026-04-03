#!/bin/bash
#SBATCH --job-name=dermvlm_s1_mini
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=4:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Mini-VLM Stage 1: Alineamiento visual-textual (MLP projection)
## Modelo: CLIP ViT-B/16 + Phi-3-mini
## GPU: A30 24GB (Ampere, bf16, CUDA 12.1)
## Dataset: MM-Skin captions (~11k pares imagen-texto)

. /etc/profile
module load cuda 2>/dev/null || true

# Usar ruta absoluta al entorno conda (source activate no funciona en SLURM)
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"

# bitsandbytes necesita libcusparse de CUDA — apuntar a las libs del entorno conda
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

# Nodos de computo no tienen internet — usar modelos pre-descargados del cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd /home/$USER/dermvlm

# Usar almacenamiento local para archivos temporales
# En Mendieta /scratch es local al nodo y se borra al terminar el job
export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_s1_mini (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi

# Verificar que la GPU no este ocupada por otro proceso
GPU_MEM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ -n "$GPU_MEM_USED" ] && [ "$GPU_MEM_USED" -gt 500 ]; then
    echo "ADVERTENCIA: GPU ya tiene ${GPU_MEM_USED} MiB en uso por otro proceso"
    nvidia-smi --query-compute-apps=pid,used_memory --format=csv
fi

echo "Python: $(${PYTHON} --version)"

# Limpiar bytecode corrupto de scipy (UnicodeDecodeError en _tanhsinh.pyc)
find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
echo ""

${PYTHON} scripts/train_vlm_stage1.py \
    --model mini_vlm \
    --epochs 5 \
    --lr 1e-3 \
    --batch_size 8 \
    --grad_accum 1 \
    --early_stopping_patience 2 \
    --num_workers 4 \
    --seed 42

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
