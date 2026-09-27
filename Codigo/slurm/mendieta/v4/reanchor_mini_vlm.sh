#!/bin/bash
#SBATCH --job-name=dermvlm_reanchor_mini_vlm
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

## RE-ANCLAJE de la cascada al clasificador del split disjunto por lesión.
## Los brazos full_swin y full_differential existentes están anclados en swin_tiny_modern_v3,
## entrenado con la partición aleatoria (con fuga entre particiones). Se regeneran contra
## swin_tiny_sweep_t06_les_cwnone: cambian 291 de 1503 diagnósticos (19.4%) y el anclaje pasa de
## 0.795 a 0.847 de exactitud. Ver docs/ideas/criterio_seleccion_plan_20260917.md.
##
## El archivo de particiones no cambia porque el test del split por lesión es idéntico al original
## (mismas 1503 imágenes); lo que difiere entre los dos splits es train y val.
## generate_report.py tiene resume defensivo: si el job se corta, se reenvía el mismo script.

. /etc/profile
module load cuda 2>/dev/null || true
PYTHON="${HOME}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${HOME}/miniconda3/envs/dermvlm/lib:${LD_LIBRARY_PATH}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONUNBUFFERED=1
cd /home/$USER/dermvlm
## /scratch puede estar montado pero roto (job 1177954: OSError EIO al crear temporales, y SLURM lo
## marcó COMPLETED). Se prueba escribiendo, no solo con mkdir; si falla se usa /tmp.
export TMPDIR="/scratch/${SLURM_JOB_ID}"
if ! { mkdir -p "$TMPDIR" && touch "$TMPDIR/.probe" && rm -f "$TMPDIR/.probe"; } 2>/dev/null; then
    echo "AVISO: ${TMPDIR} no es escribible; se usa /tmp"
    export TMPDIR="/tmp/${SLURM_JOB_ID}"; mkdir -p "$TMPDIR"
fi

## Corre un brazo de generación y verifica que dejó los reportes esperados. Cualquier fallo marca el
## job como FAILED (exit 1) al final, en vez de terminar con código 0.
FAILED=0
run_arm() {
    local out_dir="$1" expected="$2"; shift 2
    ${PYTHON} scripts/generate_report.py "$@" --output_dir "$out_dir"         || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
    local n; n=$(find "$out_dir" -name '*_report.json' 2>/dev/null | wc -l)
    echo "Reportes en ${out_dir}: ${n}/${expected}"
    [ "$n" -ge "$expected" ] || { echo "ERROR: faltan reportes en ${out_dir}"; FAILED=1; }
}

echo "=== reanchor_mini_vlm (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

CKPT="outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt"
SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model mini_vlm --checkpoint ${CKPT} --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== (1) grounding Swin del split por lesión, noreasoning (n=1503) ==="
run_arm outputs/generated_reports/mini_vlm/full_swin_les 1503 ${COMMON} --diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt --grounded_variant noreasoning
echo ""

## Nivel DIFERENCIAL del ruteo de 3 niveles, rearmado con el Swin nuevo + kNN-DermLIP del split por
## lesión: 248 imágenes (antes 334, con otro conjunto de imágenes). El nivel afirmativo reutiliza
## full_swin_les y el de abstención no genera.
echo "=== (2) reportes DIFERENCIALES del ruteo nuevo (n=248) ==="
run_arm outputs/generated_reports/mini_vlm/full_differential_les 248 ${COMMON} --uncertainty_csv outputs/uncertainty/uncertainty_differential_les.csv --uncertainty --only_ids_csv outputs/uncertainty/uncertainty_differential_les.csv
echo ""

rm -rf "$TMPDIR"
if [ "$FAILED" -ne 0 ]; then echo "=== Job FALLIDO (ver errores arriba) ==="; date; exit 1; fi
echo "=== Job completado ==="; date
