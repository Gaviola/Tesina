#!/bin/bash
#SBATCH --job-name=dermvlm_s2_llava_v2
#SBATCH --output=/home/%u/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/llava_med/%j.err
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

## LLaVA-Med Stage 2 v2: LoRA fine-tuning con más épocas (~14GB LoRA en A30 24GB)
## Mejoras respecto a v1:
##   - epochs: 3 → 10 (val_loss seguía bajando en época 5/5 del sweep)
##   - lr: 2.495e-05 (mejor trial t04 del sweep de Stage 2)
##   - lora_r=64, lora_alpha=64, lora_dropout=0.0 (mejores HPs del sweep)

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_s2_llava_v2 (JOBID: $SLURM_JOB_ID) ==="
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

export WANDB_MODE=offline

${PYTHON} scripts/train_vlm_stage2.py \
    --model llava_med \
    --checkpoint outputs/checkpoints/stage1_llava_med/best_model.pt \
    --epochs 10 \
    --lr 2.495e-5 \
    --batch_size 4 \
    --grad_accum 8 \
    --lora_r 64 \
    --lora_alpha 64 \
    --lora_dropout 0.0 \
    --run-name llava_med_s2_v2 \
    --wandb

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
