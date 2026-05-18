#!/bin/bash
#SBATCH --job-name=dermvlm_cls_llava_ft_v2
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
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

## LLaVA-Med v2: Clasificacion FT con checkpoint Stage 2 v2 (10 epochs)
## Output: outputs/results/llava_med/v2/

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export WANDB_MODE=offline

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_cls_llava_ft_v2 (JOBID: $SLURM_JOB_ID) ==="
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

## Metodo de clasificacion. Configurable via variable de entorno (generate | likelihood | cot).
METHOD="${METHOD:-generate}"
echo "Metodo de clasificacion: ${METHOD}"

## Output staging: usar dir temporal versionado para evitar colision con v1.
## Tras la corrida, mover resultados al path final outputs/results/llava_med/v2/
STAGING_DIR="outputs/_v2_staging/llava_med/${METHOD}_${SLURM_JOB_ID}"
mkdir -p "${STAGING_DIR}"

${PYTHON} scripts/train_vlm_classify.py \
    --model llava_med \
    --method "${METHOD}" \
    --checkpoint outputs/checkpoints/stage2_llava_med_v2/best_model.pt \
    --output_dir "${STAGING_DIR}" \
    --batch_size 1 \
    --seed 42 \
    --wandb

PYTHON_RC=$?

if [ $PYTHON_RC -eq 0 ]; then
    echo ""
    echo "=== Moviendo resultados a outputs/results/llava_med/v2/ ==="
    mkdir -p outputs/results/llava_med/v2
    if [ -d "${STAGING_DIR}/results" ]; then
        mv "${STAGING_DIR}/results"/*.json outputs/results/llava_med/v2/ 2>/dev/null || true
        ls -la outputs/results/llava_med/v2/
    fi
    rm -rf "${STAGING_DIR}"
else
    echo "ADVERTENCIA: el script python termino con rc=${PYTHON_RC}; staging preservado en ${STAGING_DIR}"
fi

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
