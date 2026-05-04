#!/bin/bash
#SBATCH --job-name=dermvlm_cls_llava_ft
#SBATCH --output=/home/%u/scratch/dermvlm/logs/llava_med/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/llava_med/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=10:00:00
#SBATCH --exclusive
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## LLaVA-Med: Clasificacion fine-tuned en HAM10000 test (~14GB, RTX 4080 16GB)
## Modelo: CLIP ViT-L/14 + Mistral-7B-Med (fine-tuned Stage 2 con LoRA)
## Metodo configurable via variable de entorno METHOD (generate | likelihood | cot)

. /etc/profile

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

cd /home/$USER/scratch/dermvlm

export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

echo "=== Iniciando dermvlm_cls_llava_ft (JOBID: $SLURM_JOB_ID) ==="
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

## Metodo de clasificacion. Configurable via variable de entorno para permitir
## reutilizar el mismo script sbatch en todos los metodos (generate | likelihood | cot).
METHOD="${METHOD:-generate}"
echo "Metodo de clasificacion: ${METHOD}"

${PYTHON} scripts/train_vlm_classify.py \
    --model llava_med \
    --method "${METHOD}" \
    --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt \
    --batch_size 1 \
    --seed 42 \
    --wandb

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
