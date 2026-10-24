#!/bin/bash
#SBATCH --job-name=dermvlm_s2_mini_v3
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00:00
#SBATCH --signal=B:SIGTERM@595

## Mini-VLM Stage 2 v3 (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md).
## Igual que v2 salvo los módulos LoRA: Phi-3.5-vision fusiona la atención del LLM en qkv_proj, así que con
## q_proj/v_proj (v2) solo se adaptaba el codificador CLIP. Acá: qkv_proj (LLM) + q_proj/v_proj (CLIP).
## Esperado en el log: trainable params 31,457,280.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1 WANDB_MODE=offline
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"
if ! { mkdir -p "$TMPDIR" && touch "$TMPDIR/.probe" && rm -f "$TMPDIR/.probe"; } 2>/dev/null; then
    echo "AVISO: ${TMPDIR} no es escribible; se usa /tmp"
    export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"
fi

echo "=== train_vlm_s2_mini_v3 (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

S1="outputs/checkpoints/stage1_mini_vlm/best_model.pt"
[ -f "$S1" ] || { echo "ERROR: falta ${S1}"; exit 1; }

${PYTHON} scripts/train_vlm_stage2.py \
    --model mini_vlm \
    --checkpoint "${S1}" \
    --epochs 10 \
    --lr 2.495e-5 \
    --batch_size 4 \
    --grad_accum 8 \
    --lora_r 64 \
    --lora_alpha 64 \
    --lora_dropout 0.0 \
    --lora_target_modules qkv_proj q_proj v_proj \
    --run-name v3 \
    --wandb
RC=$?

CKPT="outputs/checkpoints/stage2_mini_vlm_v3/best_model.pt"
rm -rf "$TMPDIR"
if [ $RC -ne 0 ] || [ ! -f "$CKPT" ]; then echo "=== Job FALLIDO (rc=${RC}, checkpoint: ${CKPT}) ==="; date; exit 1; fi
cat outputs/checkpoints/stage2_mini_vlm_v3/lora_config.json
echo "=== Job completado ==="; date
