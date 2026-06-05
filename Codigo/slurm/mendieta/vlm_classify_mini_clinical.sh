#!/bin/bash
#SBATCH --job-name=dermvlm_cls_mini_clinical
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=06:00:00
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Mini-VLM: Clasificacion ZERO-SHOT likelihood sobre FOTO CLINICA (SkinCAP -> 7 clases HAM).
## Confirmacion del domain gap: comparar sens_macro clinica vs HAM (dermatoscopia).
## Zero-shot (sin checkpoint) para evitar circularidad (SkinCAP se uso en Stage 1).

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

echo "=== Iniciando dermvlm_cls_mini_clinical (JOBID: $SLURM_JOB_ID) ==="
date
echo "Nodo: $(hostname)"
nvidia-smi
echo "Python: $(${PYTHON} --version)"

find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
echo ""

## Mini-VLM (Phi-3.5-vision) procesa cada imagen secuencialmente -> el script fuerza batch_size=1.
${PYTHON} scripts/train_vlm_classify.py \
    --model mini_vlm \
    --method likelihood \
    --eval-dataset skincap_clinical \
    --batch_size 1 \
    --seed 42

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
