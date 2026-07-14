#!/bin/bash
#SBATCH --job-name=dermvlm_abl_llava_mini
#SBATCH --output=/home/%u/dermvlm/logs/shared/abl_%j.out
#SBATCH --error=/home/%u/dermvlm/logs/shared/abl_%j.err
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

## P4.1 (mejoras.md #9) — Extender las ablaciones imagen-vs-dx (P1.2) y dx-erróneo (P1.3) a
## LLaVA-Med y Mini-VLM, para completar la comparación (hasta ahora solo se hicieron sobre SkinVL).
## Subconjunto de 400 (para comparar con full_oracle existente de esos modelos).

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== ablations_llava_mini (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

SPLIT="--splits_file data/splits/ham10000_splits.json --split test"

for PAIR in "llava_med:stage2_llava_med_v2" "mini_vlm:stage2_mini_vlm_v2"; do
    MODEL="${PAIR%%:*}"; CKPT="outputs/checkpoints/${PAIR##*:}/best_model.pt"
    COMMON="--model ${MODEL} --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 400"

    echo "=== ${MODEL} — P1.2 imagen-vs-dx (oracle SIN imagen) ==="
    ${PYTHON} scripts/generate_report.py ${COMMON} \
        --diagnosis_source outputs/full_dx_oracle.csv --grounded_prompt --grounded_variant noreasoning \
        --no_image \
        --output_dir outputs/generated_reports/${MODEL}/full_oracle_noimage
    echo ""

    echo "=== ${MODEL} — P1.3 dx-erróneo ==="
    ${PYTHON} scripts/generate_report.py ${COMMON} \
        --diagnosis_source outputs/full_dx_wrong_swap.csv --grounded_prompt --grounded_variant noreasoning \
        --output_dir outputs/generated_reports/${MODEL}/full_wrong_swap
    echo ""
done

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
