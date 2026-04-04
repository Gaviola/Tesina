"""Sweep de hiperparámetros — Fase 2: VLMs con LoRA (LLaVA-Med / Mini-VLM).

Lee configs/sweeps/phase2_sweep.yaml, genera N combinaciones aleatorias de
parámetros y lanza un job SLURM por combinación en el cluster indicado.
Todos los jobs corren con WANDB_MODE=offline.

Uso:
    python scripts/sweep_phase2.py --cluster toko --n-trials 12
    python scripts/sweep_phase2.py --cluster mendieta --n-trials 12
    python scripts/sweep_phase2.py --cluster toko --n-trials 4 --dry-run
    python scripts/sweep_phase2.py --cluster toko --n-trials 12 --model mini_vlm
      (filtrar a un solo modelo, útil para explorar un modelo en profundidad)
    python scripts/sweep_phase2.py --cluster toko --n-trials 12 --offset 6
      (retomar desde el trial 7)

Sincronizar resultados con wandb:
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
        "log_subdir_llava": "llava_med",
        "log_subdir_mini":  "mini_vlm",
        "time_limit": "48:00:00",    # los VLMs necesitan más tiempo que los clasificadores
        "header_fn": slurm_header_toko,
        "setup_fn": slurm_setup_toko,
        "python_bin": "${HOME}/miniconda3/envs/dermvlm/bin/python",
    },
    "mendieta": {
        "import": "scripts.mendieta.config",
        "remote_base_attr": "REMOTE_BASE",
        "log_subdir_llava": "llava_med",
        "log_subdir_mini":  "mini_vlm",
        "time_limit": "2-00:00:00",
        "header_fn": slurm_header_mendieta,
        "setup_fn": slurm_setup_mendieta,
        "python_bin": "${HOME}/miniconda3/envs/dermvlm/bin/python",
    },
}

SWEEP_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs/sweeps/phase2_sweep.yaml"
RUN_PREFIX = "s2"


# ─── Generación del script SLURM ─────────────────────────────────────────────

def _log_subdir_for_model(model: str, cluster_cfg: dict) -> str:
    if "llava" in model:
        return cluster_cfg["log_subdir_llava"]
    return cluster_cfg["log_subdir_mini"]


def build_slurm_script(combo: dict, trial_idx: int, total: int,
                       run_name: str, cluster_cfg: dict,
                       remote_base: str, python_bin: str) -> str:
    """Construye el cuerpo completo del script SLURM para un trial fase 2."""
    model = combo["model"]
    log_subdir = _log_subdir_for_model(model, cluster_cfg)
    time_limit = cluster_cfg["time_limit"]
    header_fn = cluster_cfg["header_fn"]
    setup_fn = cluster_cfg["setup_fn"]

    # lora_alpha = lora_r * lora_alpha_multiplier
    lora_r = combo["lora_r"]
    lora_alpha = int(lora_r * combo["lora_alpha_multiplier"])

    grad_accum = combo["gradient_accumulation_steps"]
    # batch_size efectivo = 4 * grad_accum (batch_size=4 fijo por VRAM)
    effective_bs = 4 * grad_accum

    combo_summary = (
        f"model={model}  lora_r={lora_r}  alpha={lora_alpha}  "
        f"dropout={shell_val(combo['lora_dropout'])}  "
        f"s1_lr={shell_val(combo['stage1_lr'])}  "
        f"s2_lr={shell_val(combo['stage2_lr'])}  "
        f"s2_epochs={combo['stage2_epochs']}  "
        f"grad_accum={grad_accum}(eff_bs={effective_bs})"
    )

    header = header_fn(
        job_name=f"sw2_{trial_idx:02d}_{model[:4]}",
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
echo "--- Stage 1: alineamiento visual-textual ({model}) ---"
{python_bin} scripts/train_phase2.py \\
    --model {model} \\
    --stage 1 \\
    --lr {shell_val(combo["stage1_lr"])} \\
    --epochs {combo["stage1_epochs"]} \\
    --lora-r {lora_r} \\
    --lora-alpha {lora_alpha} \\
    --lora-dropout {shell_val(combo["lora_dropout"])} \\
    --seed 42

echo ""
echo "--- Stage 2: fine-tuning con LoRA ({model}) ---"
{python_bin} scripts/train_phase2.py \\
    --model {model} \\
    --stage 2 \\
    --lr {shell_val(combo["stage2_lr"])} \\
    --epochs {combo["stage2_epochs"]} \\
    --gradient-accumulation-steps {grad_accum} \\
    --lora-r {lora_r} \\
    --lora-alpha {lora_alpha} \\
    --lora-dropout {shell_val(combo["lora_dropout"])} \\
    --seed 42
"""

    footer = """
echo ""
echo "=== Trial completado ==="
date
"""
    if setup_fn == slurm_setup_mendieta:
        footer += 'rm -rf "$TMPDIR"\n'

    return header + setup + train_cmd + footer


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Lanza sweep fase 2 (VLMs con LoRA) en TOKO o Mendieta"
    )
    parser.add_argument("--cluster", choices=["toko", "mendieta"], required=True,
                        help="Cluster destino")
    parser.add_argument("--n-trials", type=int, default=12,
                        help="Cantidad de combinaciones a lanzar (default: 12)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla para muestreo aleatorio (default: 42)")
    parser.add_argument("--offset", type=int, default=0,
                        help="Índice desde el que empezar (para retomar parcialmente)")
    parser.add_argument("--model", choices=["mini_vlm", "llava_med"], default=None,
                        help="Filtrar a un solo modelo (default: ambos)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar scripts sin enviarlos al cluster")
    args = parser.parse_args()

    # Importar config del cluster
    cluster_cfg = CONFIGS[args.cluster]
    import importlib
    cfg_mod = importlib.import_module(cluster_cfg["import"])
    remote_base = getattr(cfg_mod, cluster_cfg["remote_base_attr"])
    ssh_opts = cfg_mod.SSH_OPTS
    user = (getattr(cfg_mod, "TOKO_USER", None)
            or getattr(cfg_mod, "MENDIETA_USER", None))
    host = (getattr(cfg_mod, "TOKO_HOST", None)
            or getattr(cfg_mod, "MENDIETA_HOST", None))
    python_bin = cluster_cfg["python_bin"]

    cfg_mod.check_tools()

    # Cargar sweep config y generar combinaciones
    sweep_cfg = load_sweep_config(SWEEP_CONFIG_PATH)
    params = sweep_cfg["parameters"]
    all_combos = generate_combinations(params, args.n_trials, seed=args.seed)

    # Filtrar por modelo si se especificó
    if args.model:
        all_combos = [c for c in all_combos if c["model"] == args.model]
        if not all_combos:
            print(f"ERROR: ningún trial generó model={args.model}. "
                  f"Aumentar --n-trials o cambiar --seed.")
            sys.exit(1)

    combos = all_combos[args.offset:]
    total = args.n_trials

    print(f"=== Sweep Fase 2 → {args.cluster.upper()} ===")
    print(f"Config:   {SWEEP_CONFIG_PATH}")
    print(f"Trials:   {len(combos)} (offset={args.offset}, seed={args.seed})")
    if args.model:
        print(f"Modelo:   {args.model} (filtrado)")
    print(f"Remoto:   {user}@{host}:{remote_base}")
    if args.dry_run:
        print("Modo:     DRY-RUN (no se enviarán jobs)")
    print()

    # Mostrar tabla de combinaciones
    print(f"{'#':>4}  {'Run name':<55}  Params clave")
    print("-" * 115)
    for i, combo in enumerate(combos):
        global_idx = args.offset + i + 1
        name = make_run_name(combo, RUN_PREFIX, global_idx)
        lora_alpha = int(combo["lora_r"] * combo["lora_alpha_multiplier"])
        key_params = (
            f"model={combo['model']}  "
            f"r={combo['lora_r']}/α={lora_alpha}  "
            f"s2_lr={shell_val(combo['stage2_lr'])}  "
            f"ep={combo['stage2_epochs']}  "
            f"accum={combo['gradient_accumulation_steps']}"
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
