#!/bin/bash
#SBATCH --job-name=dermvlm_short_l1_mini_v2
#SBATCH --output=/home/%u/dermvlm/logs/mini_vlm/short/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/mini_vlm/short/%j.err
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH --gres=gpu:1
#SBATCH --time=01:00:00
## ivb02 e ivb11 fallan al arrancar con «user env retrieval failed» (19–20/10); se excluyen.
#SBATCH --exclude=ivb02,ivb11

## Un tramo del Nivel 1 de Mini-VLM v2 (configuración principal) sobre la prueba de SkinCoT (457 imágenes), que no
## existía (plan docs/ideas/costo_nivel1_mini_v2_plan_20261024.md). Mismos argumentos que el brazo skincot_test de
## gen_short_mini_v3.sh con el checkpoint de v2. generate_report.py saltea los reportes ya válidos, así que un tramo
## cortado a la hora se completa reenviándolo. Variable: SHARD (K/N, K desde 0).
source slurm/mendieta/v5/gen_common.sh
: "${SHARD:?falta SHARD}"
echo "=== short_level1_mini_v2 skincot_test shard ${SHARD} (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi
CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
[ -f "$CKPT" ] || { echo "ERROR: falta ${CKPT}"; exit 1; }
OUT="outputs/generated_reports/mini_vlm/v2/skincot_test"

${PYTHON} scripts/generate_report.py --model mini_vlm --checkpoint ${CKPT} --max_tokens 384 --seed 42 \
    --shard ${SHARD} --images_dir data/raw/skincare/skincare/SkinCoT/images \
    --reference_dir data/raw/skincare/skincare/SkinCoT/EN \
    --splits_file data/splits/skincare_skincot_splits.json --split test --output_dir "${OUT}" \
    || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
echo "Reportes en ${OUT}: $(find "${OUT}" -name '*_report.json' 2>/dev/null | wc -l) (todos los tramos)"
finish
