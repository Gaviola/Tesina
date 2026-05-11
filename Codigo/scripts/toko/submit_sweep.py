"""
submit_sweep.py — Lanza el sweep de hiperparámetros de clasificadores modernos en TOKO.

Lee configs/sweeps/phase1_modern_sweep_grid.yaml y envía un job SLURM por cada
trial (15 por modelo). Los nodos de TOKO no tienen internet, por lo que se usa
muestreo pre-definido en lugar de un agente wandb online.

Uso:
  python scripts/toko/submit_sweep.py --model convnext_tiny          # 15 jobs
  python scripts/toko/submit_sweep.py --model swin_tiny              # 15 jobs
  python scripts/toko/submit_sweep.py --all                          # 30 jobs (ambos modelos)
  python scripts/toko/submit_sweep.py --all --dry-run                # previsualizar sin enviar

  # Re-run del mejor trial con --eval-hiba (OOD evaluation):
  python scripts/toko/submit_sweep.py --rerun-hiba convnext_tiny t06
  python scripts/toko/submit_sweep.py --rerun-hiba swin_tiny t08

Cada trial se ejecuta como un job independiente en la cola gpu de TOKO.
Los resultados se sincronizan localmente con:
  python scripts/toko/sync_down.py

Para comparar los trials buscar en outputs/wandb/:
  wandb sync outputs/wandb/

El mejor trial se identifica por val_f1_weighted en el log de wandb.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

try:
    import yaml
except ImportError:
    raise SystemExit("ERROR: instalar PyYAML — pip install pyyaml")

from scripts.sweep_utils import append_jobs_log, submit_script_stdin
from scripts.toko.config import (
    REMOTE_BASE, SSH_OPTS, TOKO_HOST, TOKO_USER, check_tools, unix_script,
)

_GRID_PATH = Path(__file__).resolve().parents[2] / "configs" / "sweeps" / "phase1_modern_sweep_grid.yaml"

# Tiempo máximo por trial: 12h (igual que train_classifier.sh).
# ConvNeXt/Swin ~40 epochs sobre RTX 4080 demoran ~3-5h reales.
_TIME_LIMIT = "12:00:00"


def _build_slurm_script(model: str, trial: dict) -> str:
    """Genera el script SLURM completo para un trial del sweep."""
    t = trial["trial"]
    lr = trial["lr"]
    wd = trial["weight_decay"]
    m = trial["randaugment_m"]
    run_name = f"{model}_sweep_{t}"

    # Formato legible para floats en bash (evita notación científica con 'e+')
    lr_str = f"{lr:.2e}"
    wd_str = f"{wd:.2g}"

    return f"""\
#!/bin/bash
#SBATCH --job-name=dermvlm_sweep_{t}
#SBATCH --output=/home/%u/scratch/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/shared/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time={_TIME_LIMIT}
#SBATCH --exclusive
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Sweep modern v3 — trial {t}
## model={model}  lr={lr_str}  weight_decay={wd_str}  randaugment_m={m}

. /etc/profile

PYTHON="${{HOME}}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${{HOME}}/miniconda3/envs/dermvlm/lib:${{LD_LIBRARY_PATH}}"

cd {REMOTE_BASE}

export TMPDIR="/tmp/${{SLURM_JOB_ID}}"
mkdir -p "$TMPDIR" 2>/dev/null || {{
    export TMPDIR="${{HOME}}/scratch/dermvlm/tmp/${{SLURM_JOB_ID}}"
    mkdir -p "$TMPDIR"
}}

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export WANDB_MODE=offline
export WANDB_DIR={REMOTE_BASE}/outputs

echo "=== Sweep {t} — {model} (JOBID: $SLURM_JOB_ID) ==="
echo "  lr={lr_str}  weight_decay={wd_str}  randaugment_m={m}"
date
echo "Nodo: $(hostname)"
nvidia-smi
echo ""

${{PYTHON}} scripts/train_classifier.py \\
    --model {model} \\
    --recipe modern \\
    --run-name {run_name} \\
    --lr {lr_str} \\
    --weight-decay {wd_str} \\
    --randaugment-m {m} \\
    --focal-gamma 0 \\
    --seed 42 \\
    --no-freeze-backbone \\
    --wandb

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
"""


def submit_trial(model: str, trial: dict, dry_run: bool) -> str | None:
    t = trial["trial"]
    run_name = f"{model}_sweep_{t}"
    script = _build_slurm_script(model, trial)
    print(f"  Enviando {run_name} "
          f"(lr={trial['lr']:.2e}, wd={trial['weight_decay']}, m={trial['randaugment_m']})...")

    if dry_run:
        print(f"  [dry-run] Script generado ({len(script)} chars)")
        return "DRY_RUN"

    jobid = submit_script_stdin(
        script_body=script,
        ssh_opts=SSH_OPTS,
        user=TOKO_USER,
        host=TOKO_HOST,
        remote_base=REMOTE_BASE,
        dry_run=False,
    )
    if jobid:
        print(f"  JOBID: {jobid}  |  log: logs/shared/{jobid}.out")
    else:
        print(f"  ERROR: no se pudo enviar {run_name}")
    return jobid


def _build_slurm_hiba_script(model: str, trial: dict) -> str:
    """Genera script SLURM para re-entrenar el mejor trial con --eval-hiba."""
    t = trial["trial"]
    lr = trial["lr"]
    wd = trial["weight_decay"]
    m = trial["randaugment_m"]
    run_name = f"{model}_sweep_{t}_hiba"

    lr_str = f"{lr:.2e}"
    wd_str = f"{wd:.2g}"

    return f"""\
#!/bin/bash
#SBATCH --job-name=dermvlm_hiba_{t}
#SBATCH --output=/home/%u/scratch/dermvlm/logs/shared/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/shared/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time={_TIME_LIMIT}
#SBATCH --exclusive
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=facundo.gaviola@gmail.com

## Sweep modern v4 — HIBA re-run trial {t}
## model={model}  lr={lr_str}  weight_decay={wd_str}  randaugment_m={m}

. /etc/profile

PYTHON="${{HOME}}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${{HOME}}/miniconda3/envs/dermvlm/lib:${{LD_LIBRARY_PATH}}"

cd {REMOTE_BASE}

export TMPDIR="/tmp/${{SLURM_JOB_ID}}"
mkdir -p "$TMPDIR" 2>/dev/null || {{
    export TMPDIR="${{HOME}}/scratch/dermvlm/tmp/${{SLURM_JOB_ID}}"
    mkdir -p "$TMPDIR"
}}

export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export WANDB_MODE=offline
export WANDB_DIR={REMOTE_BASE}/outputs

echo "=== HIBA re-run {t} — {model} (JOBID: $SLURM_JOB_ID) ==="
echo "  lr={lr_str}  weight_decay={wd_str}  randaugment_m={m}"
date
echo "Nodo: $(hostname)"
nvidia-smi
echo ""

${{PYTHON}} scripts/train_classifier.py \\
    --model {model} \\
    --recipe modern \\
    --run-name {run_name} \\
    --lr {lr_str} \\
    --weight-decay {wd_str} \\
    --randaugment-m {m} \\
    --focal-gamma 0 \\
    --seed 42 \\
    --no-freeze-backbone \\
    --eval-hiba \\
    --wandb

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
"""


def submit_hiba_rerun(model: str, trial_id: str, dry_run: bool) -> str | None:
    """Envía un job de re-entrenamiento con --eval-hiba para el trial ganador."""
    if not _GRID_PATH.exists():
        print(f"ERROR: grid no encontrado en {_GRID_PATH}")
        sys.exit(1)

    with open(_GRID_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    trial = next((t for t in config["trials"] if t["trial"] == trial_id), None)
    if trial is None:
        print(f"ERROR: trial '{trial_id}' no encontrado en el grid")
        sys.exit(1)

    run_name = f"{model}_sweep_{trial_id}_hiba"
    script = _build_slurm_hiba_script(model, trial)
    print(f"  Enviando {run_name} con --eval-hiba "
          f"(lr={trial['lr']:.2e}, wd={trial['weight_decay']}, m={trial['randaugment_m']})...")

    if dry_run:
        print(f"  [dry-run] Script generado ({len(script)} chars)")
        return "DRY_RUN"

    jobid = submit_script_stdin(
        script_body=script,
        ssh_opts=SSH_OPTS,
        user=TOKO_USER,
        host=TOKO_HOST,
        remote_base=REMOTE_BASE,
        dry_run=False,
    )
    if jobid:
        print(f"  JOBID: {jobid}  |  log: logs/shared/{jobid}.out")
    else:
        print(f"  ERROR: no se pudo enviar {run_name}")
    return jobid


def main():
    parser = argparse.ArgumentParser(description="Sweep clasificadores modernos en TOKO")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--model", choices=["convnext_tiny", "swin_tiny"],
                       help="Modelo a sweepear (15 jobs)")
    group.add_argument("--all", action="store_true",
                       help="Sweepear ambos modelos (30 jobs)")
    group.add_argument("--rerun-hiba", nargs=2, metavar=("MODEL", "TRIAL"),
                       help="Re-entrenar el trial ganador con --eval-hiba. "
                            "Ej: --rerun-hiba convnext_tiny t06")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar scripts sin enviar al cluster")
    args = parser.parse_args()

    check_tools()

    # Modo re-run HIBA
    if args.rerun_hiba:
        model, trial_id = args.rerun_hiba
        if model not in ["convnext_tiny", "swin_tiny"]:
            print(f"ERROR: modelo '{model}' no válido. Usar convnext_tiny o swin_tiny.")
            sys.exit(1)
        print(f"=== HIBA re-run en TOKO ===")
        print(f"Modelo: {model}  Trial: {trial_id}")
        if args.dry_run:
            print("Modo: DRY-RUN")
        print()
        jobid = submit_hiba_rerun(model, trial_id, dry_run=args.dry_run)
        if jobid and not args.dry_run:
            description = f"sweep_modern_v4 hiba_rerun model={model} trial={trial_id}"
            append_jobs_log([jobid], "toko", description)
        print("\n=== Job enviado ===")
        return

    if not _GRID_PATH.exists():
        print(f"ERROR: grid no encontrado en {_GRID_PATH}")
        sys.exit(1)

    with open(_GRID_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    trials = config["trials"]
    models = config["models"] if args.all else [args.model]

    total_jobs = len(models) * len(trials)
    print(f"=== Sweep fase1 modern en TOKO ===")
    print(f"Modelos: {models}")
    print(f"Trials por modelo: {len(trials)}")
    print(f"Total jobs: {total_jobs}")
    if args.dry_run:
        print("Modo: DRY-RUN (no se envían jobs reales)")
    print()

    all_jobids = []
    for model in models:
        print(f"--- Modelo: {model} ---")
        model_jobids = []
        for trial in trials:
            jid = submit_trial(model, trial, dry_run=args.dry_run)
            if jid:
                model_jobids.append(jid)
        all_jobids.extend(model_jobids)
        print(f"  {len(model_jobids)}/{len(trials)} trials encolados para {model}")
        print()

    if all_jobids and not args.dry_run:
        description = f"sweep_modern_v4 models={','.join(models)} n={len(trials)}"
        append_jobs_log(all_jobids, "toko", description)

    print("=== Sweep enviado ===")
    print(f"Monitorear:  python scripts/toko/monitor.py")
    print(f"Bajar logs:  python scripts/toko/sync_down.py")
    print(f"Sync wandb:  wandb sync outputs/wandb/")


if __name__ == "__main__":
    main()
