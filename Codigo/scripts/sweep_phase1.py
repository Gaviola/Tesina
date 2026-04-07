"""Sweep de hiperparámetros — Fase 1: Clasificadores (DenseNet / ViT).

Lee configs/sweeps/phase1_sweep.yaml, genera N combinaciones aleatorias de
parámetros y lanza un job SLURM por combinación en el cluster indicado.
Todos los jobs corren con WANDB_MODE=offline.

Uso:
    python scripts/sweep_phase1.py --cluster toko --n-trials 20
    python scripts/sweep_phase1.py --cluster mendieta --n-trials 20
    python scripts/sweep_phase1.py --cluster toko --n-trials 5 --dry-run
    python scripts/sweep_phase1.py --cluster toko --n-trials 20 --seed 123
    python scripts/sweep_phase1.py --cluster toko --n-trials 20 --offset 10
      (retoma desde el trial 11, útil si los primeros ya corrieron)

Después de bajar los resultados con sync_down.py, sincronizar con wandb:
    wandb sync Codigo/outputs/wandb/
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.sweep_utils import (
    load_sweep_config,
    generate_combinations,
    make_run_name,
    shell_val,
    slurm_header_toko,
    slurm_header_mendieta,
    slurm_setup_toko,
    slurm_setup_mendieta,
    submit_script_stdin,
)

# ─── Configuración por cluster ────────────────────────────────────────────────

CONFIGS = {
    "toko": {
        "import": "scripts.toko.config",
        "remote_base_attr": "REMOTE_BASE",
        "log_subdir": "sweeps/phase1",
        "time_limit": "10:00:00",
        "header_fn": slurm_header_toko,
        "setup_fn": slurm_setup_toko,
        "python_bin": "${HOME}/miniconda3/envs/dermvlm/bin/python",
    },
    "mendieta": {
        "import": "scripts.mendieta.config",
        "remote_base_attr": "REMOTE_BASE",
        "log_subdir": "sweeps/phase1",
        "time_limit": "10:00:00",
        "header_fn": slurm_header_mendieta,
        "setup_fn": slurm_setup_mendieta,
        "python_bin": "${HOME}/miniconda3/envs/dermvlm/bin/python",
    },
}

SWEEP_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs/sweeps/phase1_sweep.yaml"
RUN_PREFIX = "s1"


# ─── Generación del script SLURM ─────────────────────────────────────────────

def _batch_size_for_model(model: str) -> int:
    """DenseNet cabe con bs=32, ViT con bs=16 (límite de VRAM)."""
    return 16 if model == "vit" else 32


def build_slurm_script(combo: dict, trial_idx: int, total: int,
                       run_name: str, cluster_cfg: dict,
                       remote_base: str, python_bin: str) -> str:
    """Construye el cuerpo completo del script SLURM para un trial."""
    log_subdir = cluster_cfg["log_subdir"]
    time_limit = cluster_cfg["time_limit"]
    header_fn = cluster_cfg["header_fn"]
    setup_fn = cluster_cfg["setup_fn"]

    model = combo["model"]
    batch_size = _batch_size_for_model(model)
    scheduler = combo.get("scheduler", "CosineAnnealingLR")

    # Resumen de params para el log del job
    combo_summary = "  ".join(
        f"{k}={shell_val(v)}" for k, v in combo.items()
    )

    # Construir flag --no-freeze si freeze_backbone=false
    freeze_flag = "--freeze-backbone" if combo.get("freeze_backbone", True) else "--no-freeze-backbone"

    # scheduler=none → omitir el argumento
    scheduler_arg = (f"--scheduler {scheduler}"
                     if scheduler != "none" else "--scheduler none")

    header = header_fn(
        job_name=f"sw1_{trial_idx:02d}_{model[:3]}",
        log_subdir=log_subdir,
        time_limit=time_limit,
    )
    setup = setup_fn(
        remote_base=remote_base,
        wandb_run_name=run_name,
        log_subdir=log_subdir,
        trial_idx=trial_idx,
        total=total,
        combo_summary=combo_summary,
    )

    train_cmd = f"""\
echo "--- Entrenando {model} ---"
{python_bin} scripts/train_classifier.py \\
    --model {model} \\
    --lr {shell_val(combo["lr"])} \\
    --weight-decay {shell_val(combo["weight_decay"])} \\
    {scheduler_arg} \\
    --label-smoothing {shell_val(combo["label_smoothing"])} \\
    {freeze_flag} \\
    --epochs {combo["epochs"]} \\
    --batch-size {batch_size} \\
    --seed 42
"""

    footer = """
echo ""
echo "=== Trial completado ==="
date
"""
    # Mendieta necesita limpiar TMPDIR
    if "mendieta" in log_subdir or setup_fn == slurm_setup_mendieta:
        footer += 'rm -rf "$TMPDIR"\n'

    return header + setup + train_cmd + footer


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Lanza sweep fase 1 (clasificadores) en TOKO o Mendieta"
    )
    parser.add_argument("--cluster", choices=["toko", "mendieta"], required=True,
                        help="Cluster destino")
    parser.add_argument("--n-trials", type=int, default=20,
                        help="Cantidad de combinaciones a lanzar (default: 20)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla para muestreo aleatorio de parámetros (default: 42)")
    parser.add_argument("--offset", type=int, default=0,
                        help="Índice desde el que empezar (para retomar parcialmente)")
    parser.add_argument("--model", choices=["densenet", "vit"],
                        help="Filtrar trials a un único modelo (opcional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar scripts sin enviarlos al cluster")
    args = parser.parse_args()

    # Importar config del cluster
    cluster_cfg = CONFIGS[args.cluster]
    import importlib
    cfg_mod = importlib.import_module(cluster_cfg["import"])
    remote_base = getattr(cfg_mod, cluster_cfg["remote_base_attr"])
    ssh_opts = cfg_mod.SSH_OPTS
    user = getattr(cfg_mod, f"{args.cluster.upper()}_USER",
                   getattr(cfg_mod, "MENDIETA_USER", None)
                   or getattr(cfg_mod, "TOKO_USER", None))
    host = getattr(cfg_mod, f"{args.cluster.upper()}_HOST",
                   getattr(cfg_mod, "MENDIETA_HOST", None)
                   or getattr(cfg_mod, "TOKO_HOST", None))
    python_bin = cluster_cfg["python_bin"]

    cfg_mod.check_tools()

    # Cargar sweep config y generar combinaciones
    sweep_cfg = load_sweep_config(SWEEP_CONFIG_PATH)
    params = sweep_cfg["parameters"]

    # Si se filtra por modelo, generar un pool mayor para asegurar n_trials resultados
    pool_size = args.n_trials * 10 if args.model else args.n_trials
    all_combos = generate_combinations(params, pool_size, seed=args.seed)

    # Filtrar por modelo si se especificó y recortar a n_trials
    if args.model:
        all_combos = [c for c in all_combos if c["model"] == args.model]
    all_combos = all_combos[:args.n_trials]

    # Aplicar offset (útil para retomar sweeps parciales)
    combos = all_combos[args.offset:]
    total = len(all_combos)

    print(f"=== Sweep Fase 1 → {args.cluster.upper()} ===")
    print(f"Config:   {SWEEP_CONFIG_PATH}")
    model_str = f", model={args.model}" if args.model else ""
    print(f"Trials:   {len(combos)} (offset={args.offset}, seed={args.seed}{model_str})")
    print(f"Remoto:   {user}@{host}:{remote_base}")
    if args.dry_run:
        print("Modo:     DRY-RUN (no se enviarán jobs)")
    print()

    # Mostrar tabla de combinaciones
    print(f"{'#':>4}  {'Run name':<55}  Params clave")
    print("-" * 110)
    for i, combo in enumerate(combos):
        global_idx = args.offset + i + 1
        name = make_run_name(combo, RUN_PREFIX, global_idx)
        key_params = (
            f"model={combo['model']}  "
            f"lr={shell_val(combo['lr'])}  "
            f"wd={shell_val(combo['weight_decay'])}  "
            f"sched={combo.get('scheduler','?')}  "
            f"freeze={shell_val(combo.get('freeze_backbone', True))}"
        )
        print(f"  {global_idx:>2}  {name:<55}  {key_params}")
    print()

    if not args.dry_run:
        confirm = input(f"¿Enviar {len(combos)} jobs a {args.cluster.upper()}? [s/N] ").strip().lower()
        if confirm not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            sys.exit(0)
        print()

    # Lanzar jobs
    submitted = []
    failed = []
    for i, combo in enumerate(combos):
        global_idx = args.offset + i + 1
        run_name = make_run_name(combo, RUN_PREFIX, global_idx)
        script = build_slurm_script(
            combo=combo,
            trial_idx=global_idx,
            total=total,
            run_name=run_name,
            cluster_cfg=cluster_cfg,
            remote_base=remote_base,
            python_bin=python_bin,
        )

        print(f"  Trial {global_idx:>2}/{total}  {run_name}")
        jobid = submit_script_stdin(
            script_body=script,
            ssh_opts=ssh_opts,
            user=user,
            host=host,
            remote_base=remote_base,
            dry_run=args.dry_run,
        )
        if jobid:
            print(f"    → JOBID: {jobid}")
            submitted.append((global_idx, run_name, jobid))
        else:
            print(f"    → ERROR al enviar")
            failed.append(global_idx)

    # Resumen
    print()
    print(f"=== Resumen ===")
    print(f"  Enviados: {len(submitted)}/{len(combos)}")
    if failed:
        print(f"  Fallidos: {failed}")
    if submitted and not args.dry_run:
        print()
        print("Comandos útiles:")
        print(f"  python scripts/{args.cluster}/monitor.py          # ver cola")
        print(f"  python scripts/{args.cluster}/sync_down.py        # bajar resultados")
        print(f"  wandb sync Codigo/outputs/wandb/                  # subir runs a wandb")


if __name__ == "__main__":
    main()
