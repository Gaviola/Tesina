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

  # Barrido sobre el split DISJUNTO POR LESIÓN (test idéntico), CE con y sin class weights,
  # evaluando el mejor checkpoint por val_f1 y guardando predicciones de validación:
  python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights both
  # Semillas extra del trial ganador (selección hecha en validación):
  python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split --class-weights none --trials t08 --seeds 43 44

  # Validación externa en HIBA del ganador del split por lesión (respeta las banderas):
  python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split       --class-weights none --trials t02 --eval-hiba

  # Re-run del mejor trial del barrido POR IMAGEN con --eval-hiba (no usa el split por lesión):
  python scripts/toko/submit_sweep.py --rerun-hiba convnext_tiny t06
  python scripts/toko/submit_sweep.py --rerun-hiba swin_tiny t08

Cada trial se ejecuta como un job independiente en la cola gpu de TOKO.
Los resultados se sincronizan localmente con:
  python scripts/toko/sync_down.py

Para comparar los trials buscar en outputs/wandb/:
  wandb sync outputs/wandb/

El mejor trial se identifica por F1 macro en validación (ver
docs/ideas/criterio_seleccion_plan_20260917.md). El val_f1 que loguea wandb es el
ponderado, que es el que monitorea el callback de checkpoint, no el criterio de
selección entre trials: ese se calcula en scripts/lesion_split_report.py.
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


_LESION_SPLIT = "data/splits/ham10000_splits_lesion.json"


def _run_name(model: str, t: str, lesion_split: bool, class_weights: str, seed: int,
               eval_hiba: bool = False) -> str:
    name = f"{model}_sweep_{t}"
    if lesion_split:
        name += "_les"
    if class_weights == "none":
        name += "_cwnone"
    if seed != 42:
        name += f"_s{seed}"
    if eval_hiba:
        # El sufijo deja la corrida fuera del ranking del barrido (ver RUN_RE en
        # scripts/lesion_split_report.py): es una re-corrida para validación externa, no un trial.
        name += "_hiba"
    return name


def _build_slurm_script(model: str, trial: dict, lesion_split: bool = False,
                        class_weights: str = "auto", seed: int = 42,
                        eval_hiba: bool = False) -> str:
    """Genera el script SLURM completo para un trial del sweep.

    Con los defaults reproduce exactamente el sweep v4 original (split por imagen, class weights, seed 42).
    """
    t = trial["trial"]
    lr = trial["lr"]
    wd = trial["weight_decay"]
    m = trial["randaugment_m"]
    run_name = _run_name(model, t, lesion_split, class_weights, seed, eval_hiba)
    extra = f"--class-weights {class_weights}"
    if lesion_split:
        extra += f" --splits-file {_LESION_SPLIT} --eval-best-checkpoint --save-val-predictions"
    if eval_hiba:
        extra += " --eval-hiba"

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
    --seed {seed} \\
    {extra} \\
    --no-freeze-backbone \\
    --wandb

echo ""
echo "=== Job completado ==="
date
rm -rf "$TMPDIR"
"""


def submit_trial(model: str, trial: dict, dry_run: bool, lesion_split: bool = False,
                 class_weights: str = "auto", seed: int = 42,
                 eval_hiba: bool = False) -> str | None:
    t = trial["trial"]
    run_name = _run_name(model, t, lesion_split, class_weights, seed, eval_hiba)
    script = _build_slurm_script(model, trial, lesion_split, class_weights, seed, eval_hiba)
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
    parser.add_argument("--lesion-split", action="store_true",
                        help=f"Usar {_LESION_SPLIT} (disjunto por lesión) + mejor checkpoint + preds de val")
    parser.add_argument("--class-weights", choices=["auto", "none", "both"], default="auto",
                        help="auto = sweep v4 original; both = duplica el grid (con y sin class weights)")
    parser.add_argument("--trials", nargs="+", default=None, help="Subconjunto de trials (ej: t08)")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42], help="Semillas (default: 42)")
    parser.add_argument("--eval-hiba", action="store_true",
                        help="Evaluar también en HIBA (validación externa). A diferencia de "
                             "--rerun-hiba, respeta --lesion-split, --class-weights y --seeds, así que "
                             "es la opción correcta para los ganadores del split por lesión. El run "
                             "lleva sufijo _hiba.")
    parser.add_argument("--print-script", action="store_true", help="Con --dry-run, imprime el script")
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
    if args.trials:
        trials = [t for t in trials if t["trial"] in set(args.trials)]
    models = config["models"] if args.all else [args.model]
    cw_values = ["auto", "none"] if args.class_weights == "both" else [args.class_weights]
    combos = [(t, cw, sd) for t in trials for cw in cw_values for sd in args.seeds]

    total_jobs = len(models) * len(combos)
    print(f"=== Sweep fase1 modern en TOKO ===")
    print(f"Modelos: {models}")
    print(f"Trials por modelo: {len(combos)}  (split por lesión: {args.lesion_split}, "
          f"class_weights: {cw_values}, seeds: {args.seeds})")
    print(f"Total jobs: {total_jobs}")
    if args.dry_run:
        print("Modo: DRY-RUN (no se envían jobs reales)")
    print()

    all_jobids = []
    for model in models:
        print(f"--- Modelo: {model} ---")
        model_jobids = []
        for trial, cw, sd in combos:
            if args.dry_run and args.print_script:
                print(_build_slurm_script(model, trial, args.lesion_split, cw, sd))
            jid = submit_trial(model, trial, dry_run=args.dry_run, lesion_split=args.lesion_split,
                               class_weights=cw, seed=sd, eval_hiba=args.eval_hiba)
            if jid:
                model_jobids.append(jid)
        all_jobids.extend(model_jobids)
        print(f"  {len(model_jobids)}/{len(combos)} trials encolados para {model}")
        print()

    if all_jobids and not args.dry_run:
        tag = "sweep_lesion_split" if args.lesion_split else "sweep_modern_v4"
        description = (f"{tag} models={','.join(models)} n={len(combos)} cw={args.class_weights} "
                       f"seeds={args.seeds} trials={args.trials or 'all'}")
        append_jobs_log(all_jobids, "toko", description)

    print("=== Sweep enviado ===")
    print(f"Monitorear:  python scripts/toko/monitor.py")
    print(f"Bajar logs:  python scripts/toko/sync_down.py")
    print(f"Sync wandb:  wandb sync outputs/wandb/")


if __name__ == "__main__":
    main()
