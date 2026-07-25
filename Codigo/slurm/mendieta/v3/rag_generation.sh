#!/bin/bash
#SBATCH --job-name=dermvlm_rag_gen
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/%j.err
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

## P5.3 (RAG) — Mini-VLM, n=400.
## Contexto RAG precomputado local con embeddings DermLIP (outputs/rag/rag_context.csv).
## NOTA: la primera corrida (job 1160209) con repetition_penalty/no_repeat_ngram (P5.5) crasheó con
## CUDA device-side assert: en Mini-VLM (Phi-3.5) los input_ids llevan tokens de imagen fuera del rango
## del vocabulario, y el logits-processor de repetición hace gather fuera de límites. Se quita P5.5 acá
## (se probará por separado en LLaVA-Med). Condiciones:
##   (1) rag                -> RAG-only: recuperación como contexto, sin clasificador.
##   (2) grounded_swin_rag  -> grounding Swin + RAG (¿la recuperación agrega sobre el clasificador?).
## El baseline sin RAG y el grounding-Swin sin RAG ya existen (full_baseline / full_swin del ensamble).

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
export TMPDIR="/scratch/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR" 2>/dev/null || { export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"; }

echo "=== rag_generation (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

MODEL="mini_vlm"; CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model ${MODEL} --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42 --limit 400"

echo "=== (1) RAG-only ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --rag_context_csv outputs/rag/rag_context.csv --rag \
    --output_dir outputs/generated_reports/${MODEL}/full_rag
echo ""

echo "=== (2) grounding Swin + RAG ==="
${PYTHON} scripts/generate_report.py ${COMMON} \
    --diagnosis_source outputs/full_dx_swin.csv --grounded_prompt --grounded_variant noreasoning \
    --rag_context_csv outputs/rag/rag_context.csv \
    --output_dir outputs/generated_reports/${MODEL}/full_swin_rag
echo ""

echo "=== Job completado ==="; date; rm -rf "$TMPDIR"
