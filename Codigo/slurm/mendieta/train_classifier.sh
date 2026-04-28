#!/bin/bash
#SBATCH --job-name=dermvlm_classifier
#SBATCH --output=/home/%u/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/shared/%j.err
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

## Clasificador único parametrizado por env vars (un modelo por job).
## GPU: A30 24GB (Ampere, bf16, CUDA 12.1)
## Dataset: HAM10000 (10015 imagenes, 7 categorias) + opcional HIBA (1616)
##
## Variables esperadas (ver scripts/mendieta/submit.py JOBS):
##   MODEL        densenet | vit | convnext_tiny | swin_tiny  (REQUERIDO)
##   RECIPE       legacy | modern                              (default: legacy)
##   LR           learning rate base                            (REQUERIDO)
##   SEED         entero                                        (default: 42)
##   RUN_NAME     sufijo para outputs/checkpoints               (default: ${MODEL}_${RECIPE})
##   EXTRA_FLAGS  flags CLI adicionales                         (default: vacío)

. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"

# Nodos de computo no tienen internet — usar modelos pre-descargados del cache
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd /home/$USER/dermvlm

export TMPDIR="/scratch/${SLURM_JOB_ID}"
mkdir -p "$TMPDIR" 2>/dev/null || {
    export TMPDIR="/tmp/${SLURM_JOB_ID}"
    mkdir -p "$TMPDIR"
}

# Defaults / validación
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

# Limpiar bytecode corrupto de scipy
find ${HOME}/miniconda3/envs/dermvlm -name "__pycache__" -path "*/scipy/*" -exec rm -rf {} + 2>/dev/null
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
