#!/bin/bash
#SBATCH --job-name=dermvlm_rag_les
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
#SBATCH --mail-type=ALL
#SBATCH --mail-user=facundo.gaviola@gmail.com

## RAG con el índice de la partición por lesión (plan docs/ideas/rag_les_plan_20261003.md).
## Los brazos full_rag / full_swin_rag de julio usan outputs/rag/rag_context.csv, construido sobre la
## partición por imagen (con fuga: vecinos de la misma lesión) y full_swin_rag está anclado al Swin v3.
## Acá: índice rag_context_les.csv (solo train por lesión) y ancla full_dx_swin_les.csv, test completo.
## Sin repetition_penalty: crashea en Mini-VLM (ver slurm/mendieta/v3/rag_generation.sh).
## generate_report.py tiene resume defensivo: si el job se corta, se reenvía el mismo script.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
## /scratch puede estar montado pero roto (job 1177954): se prueba escribiendo; si falla, /tmp.
export TMPDIR="/scratch/${SLURM_JOB_ID}"
if ! { mkdir -p "$TMPDIR" && touch "$TMPDIR/.probe" && rm -f "$TMPDIR/.probe"; } 2>/dev/null; then
    echo "AVISO: ${TMPDIR} no es escribible; se usa /tmp"
    export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"
fi

## Corre un brazo y verifica que dejó los reportes esperados; cualquier fallo termina el job con exit 1.
FAILED=0
run_arm() {
    local out_dir="$1" expected="$2"; shift 2
    ${PYTHON} scripts/generate_report.py "$@" --output_dir "$out_dir" \
        || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
    local n; n=$(find "$out_dir" -name '*_report.json' 2>/dev/null | wc -l)
    echo "Reportes en ${out_dir}: ${n}/${expected}"
    [ "$n" -ge "$expected" ] || { echo "ERROR: faltan reportes en ${out_dir}"; FAILED=1; }
}

echo "=== rag_les_mini_vlm (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

RAG_CSV="outputs/rag/rag_context_les.csv"
[ -f "$RAG_CSV" ] || { echo "ERROR: falta ${RAG_CSV}"; exit 1; }
CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model mini_vlm --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== (1) RAG solo, índice por lesión (n=1503) ==="
run_arm outputs/generated_reports/mini_vlm/full_rag_les 1503 ${COMMON} --rag_context_csv ${RAG_CSV} --rag
echo ""

echo "=== (2) grounding Swin por lesión + RAG por lesión (n=1503) ==="
run_arm outputs/generated_reports/mini_vlm/full_swin_rag_les 1503 ${COMMON} --diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt --grounded_variant noreasoning --rag_context_csv ${RAG_CSV}
echo ""

rm -rf "$TMPDIR"
if [ "$FAILED" -ne 0 ]; then echo "=== Job FALLIDO (ver errores arriba) ==="; date; exit 1; fi
echo "=== Job completado ==="; date
