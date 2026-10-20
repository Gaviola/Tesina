#!/bin/bash
#SBATCH --job-name=dermvlm_short_mini_v3
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/short/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/short/%j.err
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
## ivb11 falla al arrancar con «user env retrieval failed» (19/10); se excluye.
#SBATCH --exclude=ivb11

## Un tramo de un brazo de generación de Mini-VLM v3 en la partición short (1 h), para entrar por backfill mientras
## los jobs de multi siguen en cola. Mismos argumentos que cascade/extra/level1_test de v5; generate_report.py
## saltea los reportes ya válidos, así que un tramo cortado a la hora se completa reenviándolo, y el job de multi
## que arranque después solo genera lo que falte. Mini-VLM usa ~25 GB de RAM (jobs 1177953, 1179315).
## Variables: ARM (nombre del brazo, ver el case) y SHARD (K/N, K desde 0).
source slurm/mendieta/v5/gen_common.sh
: "${ARM:?falta ARM}" "${SHARD:?falta SHARD}"
echo "=== short_mini_v3 ${ARM} shard ${SHARD} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
[ -f "$CKPT_V3" ] || { echo "ERROR: falta ${CKPT_V3}"; exit 1; }
OUT="outputs/generated_reports/mini_vlm_v3"
RAG_CSV="outputs/rag/rag_context_les.csv"
COMMON="--model mini_vlm --checkpoint ${CKPT_V3} --max_tokens 384 --seed 42 --shard ${SHARD}"
GROUND="--grounded_prompt --grounded_variant noreasoning"
SKINCOT="--images_dir data/raw/skincare/skincare/SkinCoT/images --reference_dir data/raw/skincare/skincare/SkinCoT/EN \
    --splits_file data/splits/skincare_skincot_splits.json --split test"
MMSKIN="--images_dir data/processed/MM-SkinQA --reference_csv data/processed/MM-SkinQA/caption.csv \
    --splits_file data/splits/mmskin_splits.json --split test"

case "$ARM" in
    full_baseline)         ARGS="${HAM_TEST}" ;;
    full_swin_les|full_oracle|full_dermlip)
                           ARGS="${HAM_TEST} --diagnosis_source outputs/full_dx_${ARM#full_}.csv ${GROUND}" ;;
    full_differential_les) ARGS="${HAM_TEST} --uncertainty_csv outputs/uncertainty/uncertainty_differential_les.csv \
                               --uncertainty --only_ids_csv outputs/uncertainty/uncertainty_differential_les.csv" ;;
    full_rag_les)          ARGS="${HAM_TEST} --rag_context_csv ${RAG_CSV} --rag" ;;
    full_swin_rag_les)     ARGS="${HAM_TEST} --diagnosis_source outputs/full_dx_swin_les.csv ${GROUND} \
                               --rag_context_csv ${RAG_CSV}" ;;
    full_oracle_noimage)   ARGS="${HAM_TEST} --limit 400 --diagnosis_source outputs/full_dx_oracle.csv ${GROUND} --no_image" ;;
    full_wrong_swap)       ARGS="${HAM_TEST} --limit 400 --diagnosis_source outputs/full_dx_wrong_swap.csv ${GROUND}" ;;
    skincot_test)          ARGS="${SKINCOT}" ;;
    mmskin_test)           ARGS="${MMSKIN}" ;;
    *) echo "ERROR: brazo desconocido ${ARM}"; exit 1 ;;
esac

${PYTHON} scripts/generate_report.py ${COMMON} ${ARGS} --output_dir "${OUT}/${ARM}" \
    || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
echo "Reportes en ${OUT}/${ARM}: $(find "${OUT}/${ARM}" -name '*_report.json' 2>/dev/null | wc -l) (todos los tramos)"
finish
