#!/bin/bash
#SBATCH --job-name=dermvlm_level1_test
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

## Nivel 1 (con referencia) sobre las particiones de prueba de MM-Skin (1653) y SkinCoT (457)
## (plan docs/ideas/mini_vlm_lora_llm_plan_20261012.md). Los reportes v2 de MM-Skin cubrían el archivo completo
## cortado por tiempo. Variables: MODEL (mini_vlm | llava_med), CKPT (checkpoint de etapa 2), OUT (carpeta de salida).
source slurm/mendieta/v5/gen_common.sh
: "${MODEL:?falta MODEL}" "${CKPT:?falta CKPT}" "${OUT:?falta OUT}"
echo "=== level1_test ${MODEL} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
[ -f "$CKPT" ] || { echo "ERROR: falta ${CKPT}"; exit 1; }
COMMON="--model ${MODEL} --checkpoint ${CKPT} --max_tokens 384 --seed 42"

echo "=== (1) SkinCoT test (n=457) ==="
run_arm ${OUT}/skincot_test 457 ${COMMON} --images_dir data/raw/skincare/skincare/SkinCoT/images \
    --reference_dir data/raw/skincare/skincare/SkinCoT/EN \
    --splits_file data/splits/skincare_skincot_splits.json --split test
echo "=== (2) MM-Skin test (n=1653) ==="
run_arm ${OUT}/mmskin_test 1653 ${COMMON} --images_dir data/processed/MM-SkinQA \
    --reference_csv data/processed/MM-SkinQA/caption.csv \
    --splits_file data/splits/mmskin_splits.json --split test
finish
