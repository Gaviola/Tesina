## Bloque común de los jobs de generación de v5 (se incluye con `source`). Define PYTHON, TMPDIR y run_arm.
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

## Corre un brazo y verifica que dejó los reportes esperados; cualquier fallo marca el job como fallido.
FAILED=0
run_arm() {
    local out_dir="$1" expected="$2"; shift 2
    ${PYTHON} scripts/generate_report.py "$@" --output_dir "$out_dir" \
        || { echo "ERROR: generate_report.py salió con código $?"; FAILED=1; }
    local n; n=$(find "$out_dir" -name '*_report.json' 2>/dev/null | wc -l)
    echo "Reportes en ${out_dir}: ${n}/${expected}"
    [ "$n" -ge "$expected" ] || { echo "ERROR: faltan reportes en ${out_dir}"; FAILED=1; }
}

finish() {
    rm -rf "$TMPDIR"
    if [ "$FAILED" -ne 0 ]; then echo "=== Job FALLIDO (ver errores arriba) ==="; date; exit 1; fi
    echo "=== Job completado ==="; date
}

CKPT_V3="outputs/checkpoints/stage2_mini_vlm_v3/best_model.pt"
HAM_TEST="--images_dir data/processed/HAM10000 --splits_file data/splits/ham10000_splits.json --split test"
