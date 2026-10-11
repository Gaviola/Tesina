#!/bin/bash
#SBATCH --job-name=dermvlm_reanchor_skinvl
#SBATCH --output=/home/%u/dermvlm/logs/skinvl/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/skinvl/%j.err
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

## RE-ANCLAJE de la cascada al clasificador del split disjunto por lesión, para SkinVL.
## Solo el brazo full_swin: SkinVL no participa del ruteo de 3 niveles.
## SkinVL es un checkpoint FULL, se carga desde SkinVL.MODEL_NAME (sin --checkpoint LoRA).
## Ver docs/ideas/criterio_seleccion_plan_20260917.md.

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

echo "=== reanchor_skinvl (JOBID: $SLURM_JOB_ID) ==="; date; nvidia-smi

SPLIT="--splits_file data/splits/ham10000_splits.json --split test"
COMMON="--model skinvl --images_dir data/processed/HAM10000 ${SPLIT} --max_tokens 384 --seed 42"

echo "=== grounding Swin del split por lesión, noreasoning (n=1503) ==="
run_arm outputs/generated_reports/skinvl/full_swin_les 1503 ${COMMON} \ --diagnosis_source outputs/full_dx_swin_les.csv --grounded_prompt --grounded_variant noreasoning \
echo ""

rm -rf "$TMPDIR"
if [ "$FAILED" -ne 0 ]; then echo "=== Job FALLIDO (ver errores arriba) ==="; date; exit 1; fi
echo "=== Job completado ==="; date
