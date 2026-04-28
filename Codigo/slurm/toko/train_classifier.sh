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

## Clasificador único parametrizado por env vars (un modelo por job).
## GPU: RTX 4080 16GB (Ada Lovelace, bf16, CUDA 12.6)
## Dataset: HAM10000 (10015 imagenes, 7 categorias) + opcional HIBA (1616)
##
## Variables esperadas (ver scripts/toko/submit.py JOBS):
##   MODEL        densenet | vit | convnext_tiny | swin_tiny  (REQUERIDO)
##   RECIPE       legacy | modern                              (default: legacy)
##   LR           learning rate base                            (REQUERIDO)
##   SEED         entero                                        (default: 42)
##   RUN_NAME     sufijo para outputs/checkpoints               (default: ${MODEL}_${RECIPE})
##   EXTRA_FLAGS  flags CLI adicionales                         (default: vacío)

. /etc/profile

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

cd /home/$USER/scratch/dermvlm

export TMPDIR="/tmp/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="${HOME}/scratch/dermvlm/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

: "${MODEL:?MODEL env var requerido (densenet|vit|convnext_tiny|swin_tiny)}"
: "${LR:?LR env var requerido}"
RECIPE="${RECIPE:-legacy}"
SEED="${SEED:-42}"
RUN_NAME="${RUN_NAME:-${MODEL}_${RECIPE}}"
EXTRA_FLAGS="${EXTRA_FLAGS:-}"

echo "=== Iniciando dermvlm_classifier (JOBID: $SLURM_JOB_ID) ==="
echo "  MODEL       : $MODEL"
echo "  RECIPE      : $RECIPE"
echo "  LR          : $LR"
echo "  SEED        : $SEED"
echo "  RUN_NAME    : $RUN_NAME"
echo "  EXTRA_FLAGS : $EXTRA_FLAGS"
date
echo "Nodo: $(hostname)"
nvidia-smi
echo "Python: $(${PYTHON} --version)"
echo ""

echo "--- Entrenando ${MODEL} (recipe=${RECIPE}) ---"
${PYTHON} scripts/train_classifier.py \
    --model "$MODEL" \
    --recipe "$RECIPE" \
    --run-name "$RUN_NAME" \
    --lr "$LR" \
    --seed "$SEED" \
    --no-freeze-backbone \
    $EXTRA_FLAGS

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
