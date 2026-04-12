"""Utilidades compartidas para barridos de hiperparámetros en clusters HPC.

Los nodos de cómputo de TOKO y Mendieta no tienen acceso a internet, por lo que
wandb corre en modo offline. Cada run guarda su log en outputs/wandb/ del cluster.
Sincronizar después desde local con:
    wandb sync outputs/wandb/

Flujo completo:
    1. python scripts/sweep_phase1.py --cluster toko --n-trials 20
       → lanza 20 jobs SLURM, cada uno con una combinación de hiperparámetros
    2. python scripts/toko/sync_down.py
       → baja outputs/wandb/ con todos los runs offline
    3. wandb sync Codigo/outputs/wandb/
       → sube todos los runs al servidor de wandb
"""

import math
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    raise SystemExit("ERROR: instalar PyYAML — pip install pyyaml")


# ─── Carga y muestreo de parámetros ───────────────────────────────────────────

def load_sweep_config(path: str | Path) -> dict:
    """Carga un sweep config YAML (formato wandb sweep)."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _sample_value(spec: dict, rng: random.Random) -> Any:
    """Muestrea un valor según la especificación de parámetro (wandb sweep format)."""
    if "value" in spec:
        return spec["value"]
    if "values" in spec:
        return rng.choice(spec["values"])
    dist = spec.get("distribution", "")
    if dist == "log_uniform_values":
        log_val = rng.uniform(math.log(spec["min"]), math.log(spec["max"]))
        return math.exp(log_val)
    if dist == "uniform":
        return rng.uniform(spec["min"], spec["max"])
    if dist == "int_uniform":
        return rng.randint(int(spec["min"]), int(spec["max"]))
    raise ValueError(f"Distribución no soportada: {dist!r}")


def generate_combinations(params: dict, n_trials: int, seed: int = 42) -> list[dict]:
    """Genera n_trials combinaciones aleatorias de los parámetros del sweep.

    Usa muestreo aleatorio (equivalente a method: random en wandb). Para el cluster
    esto es más práctico que grid (demasiadas combinaciones) o bayes (requiere
    servidor wandb para coordinar trials).
    """
    rng = random.Random(seed)
    return [
        {name: _sample_value(spec, rng) for name, spec in params.items()}
        for _ in range(n_trials)
    ]


def make_run_name(combo: dict, prefix: str, trial_idx: int) -> str:
    """Genera un nombre de run corto y legible para wandb.

    Ejemplo: "s1_t03_densenet_lr=2.34e-04_freeze=y"
    """
    parts = [prefix, f"t{trial_idx:02d}"]
    # Parámetros prioritarios para incluir en el nombre (el resto va solo en config)
    priority = ["model", "lora_r", "lr", "stage2_lr", "freeze_backbone",
                "gradient_accumulation_steps"]
    for k in priority:
        if k not in combo:
            continue
        v = combo[k]
        if isinstance(v, float):
            parts.append(f"{k}={v:.2e}")
        elif isinstance(v, bool):
            parts.append(f"{k}={'y' if v else 'n'}")
        else:
            parts.append(f"{k}={v}")
    return "_".join(parts)


def shell_val(v: Any) -> str:
    """Convierte un valor Python a string seguro para insertar en scripts bash.

    Los floats se escriben en notación decimal (evita problemas con 'e+' en bash).
    """
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        # %.8g da hasta 8 dígitos significativos, sin trailing zeros
        return f"{v:.8g}"
    return str(v)


# ─── Headers SLURM por cluster ────────────────────────────────────────────────

def slurm_header_toko(job_name: str, log_subdir: str, time_limit: str) -> str:
    """Genera el bloque de directivas #SBATCH para TOKO."""
    return f"""\
#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output=/home/%u/scratch/dermvlm/logs/{log_subdir}/%j.out
#SBATCH --error=/home/%u/scratch/dermvlm/logs/{log_subdir}/%j.err
#SBATCH --partition=gpu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --ntasks=8
#SBATCH --time={time_limit}
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=facundo.gaviola@gmail.com
"""


def slurm_header_mendieta(job_name: str, log_subdir: str, time_limit: str) -> str:
    """Genera el bloque de directivas #SBATCH para Mendieta."""
    return f"""\
#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output=/home/%u/dermvlm/logs/{log_subdir}/%j.out
#SBATCH --error=/home/%u/dermvlm/logs/{log_subdir}/%j.err
#SBATCH --partition=multi
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem=0
#SBATCH --gres=gpu:1
#SBATCH --time={time_limit}
#SBATCH --signal=B:SIGTERM@595
#SBATCH --mail-type=FAIL,END
#SBATCH --mail-user=facundo.gaviola@gmail.com
"""


def slurm_setup_toko(remote_base: str, wandb_run_name: str,
                     log_subdir: str, trial_idx: int, total: int,
                     combo_summary: str) -> str:
    """Genera el bloque de setup inicial del job en TOKO."""
    return f"""
. /etc/profile
source "${{HOME}}/miniconda3/etc/profile.d/conda.sh"
conda activate dermvlm

cd {remote_base}
mkdir -p logs/{log_subdir} outputs

# Sin acceso a internet en nodos de cómputo
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# wandb offline: WANDB_DIR=outputs → wandb crea outputs/wandb/offline-run-*/
# Sincronizar después con: wandb sync outputs/wandb/
export WANDB_MODE=offline
export WANDB_DIR={remote_base}/outputs
export WANDB_RUN_NAME="{wandb_run_name}"

echo "=== Sweep trial {trial_idx}/{total} (JOBID: $SLURM_JOB_ID) ==="
echo "Run name: {wandb_run_name}"
echo "Params:   {combo_summary}"
date
echo "Nodo: $(hostname)"
nvidia-smi
echo ""
"""


def slurm_setup_mendieta(remote_base: str, wandb_run_name: str,
                         log_subdir: str, trial_idx: int, total: int,
                         combo_summary: str) -> str:
    """Genera el bloque de setup inicial del job en Mendieta."""
    return f"""
. /etc/profile
module load cuda 2>/dev/null || true

PYTHON="${{HOME}}/miniconda3/envs/dermvlm/bin/python"
export LD_LIBRARY_PATH="${{HOME}}/miniconda3/envs/dermvlm/lib:${{LD_LIBRARY_PATH}}"

cd {remote_base}
mkdir -p logs/{log_subdir} outputs

export TMPDIR="/scratch/${{SLURM_JOB_ID}}"
mkdir -p "$TMPDIR" 2>/dev/null || {{ export TMPDIR="/tmp/${{SLURM_JOB_ID}}"; mkdir -p "$TMPDIR"; }}

# Sin acceso a internet en nodos de cómputo
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# wandb offline: WANDB_DIR=outputs → wandb crea outputs/wandb/offline-run-*/
# Sincronizar después con: wandb sync outputs/wandb/
export WANDB_MODE=offline
export WANDB_DIR={remote_base}/outputs
export WANDB_RUN_NAME="{wandb_run_name}"

echo "=== Sweep trial {trial_idx}/{total} (JOBID: $SLURM_JOB_ID) ==="
echo "Run name: {wandb_run_name}"
echo "Params:   {combo_summary}"
date
echo "Nodo: $(hostname)"
nvidia-smi
echo ""
"""


# ─── Registro local de jobs enviados ─────────────────────────────────────────

def append_jobs_log(job_ids: list[str], cluster: str, description: str) -> None:
    """Registra jobs enviados en outputs/jobs_log.txt.

    Formato de cada línea:
        2026-04-11 14:32  toko        93638-93657      sweep_phase1 n=20 seed=42
        2026-04-11 15:01  mendieta    1145719          submit mini_s1

    Si los IDs son enteros consecutivos se escribe como rango (N-M).
    Ignora IDs "DRY_RUN" o vacíos.
    """
    from datetime import datetime

    ids = [jid for jid in job_ids if jid and jid != "DRY_RUN"]
    if not ids:
        return

    # Formatear IDs: rango si son consecutivos, sino separados por coma
    try:
        numeric = sorted(int(j) for j in ids)
        if len(numeric) == 1:
            id_str = str(numeric[0])
        elif numeric[-1] - numeric[0] == len(numeric) - 1:
            id_str = f"{numeric[0]}-{numeric[-1]}"
        else:
            id_str = ",".join(str(j) for j in numeric)
    except ValueError:
        id_str = ",".join(ids)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"{timestamp}  {cluster:<12} {id_str:<22} {description}\n"

    log_path = Path(__file__).resolve().parent.parent / "outputs" / "jobs_log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"  -> Registrado en outputs/jobs_log.txt  ({id_str})")


# ─── Envío de jobs ────────────────────────────────────────────────────────────

def submit_script_stdin(script_body: str, ssh_opts: list[str],
                        user: str, host: str, remote_base: str,
                        dry_run: bool = False) -> str | None:
    """Envía un script SLURM al cluster mediante sbatch via stdin (sin archivo temporal).

    Retorna el JOBID si tuvo éxito, None si falló.
    """
    if dry_run:
        print("  [dry-run] Script que se enviaría:")
        print("  " + "\n  ".join(script_body.splitlines()))
        return "DRY_RUN"

    # Normalizar a LF (necesario en Windows)
    script_bytes = script_body.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")

    cmd = ["ssh", *ssh_opts, f"{user}@{host}",
           f". /etc/profile; cd {remote_base} && sbatch"]
    result = subprocess.run(cmd, input=script_bytes, capture_output=True)

    output = (result.stdout + result.stderr).decode("utf-8", errors="replace").strip()
    if result.returncode != 0:
        print(f"  ERROR SSH/sbatch: {output}")
        return None

    import re
    match = re.search(r"\d+", output)
    if match:
        return match.group()
    print(f"  ADVERTENCIA: no se extrajo JOBID. Salida: {output}")
    return None


def print_combo_table(combos: list[dict], prefix: str) -> None:
    """Imprime tabla de combinaciones a lanzar."""
    print(f"\n{'#':>4}  {'Run name':<50}  Params")
    print("-" * 100)
    for i, combo in enumerate(combos):
        name = make_run_name(combo, prefix, i + 1)
        params = "  ".join(f"{k}={shell_val(v)}" for k, v in combo.items()
                           if spec_is_variable(combo, k))
        print(f"  {i+1:>2}  {name:<50}  {params}")
    print()


def spec_is_variable(combo: dict, key: str) -> bool:
    """True si el parámetro varía entre combinaciones (no es un valor fijo)."""
    # Heurística: si el key termina en 'epochs' y es un int simple, es fijo
    # Para la tabla, mostramos solo los que son interesantes
    return True  # mostrar todo por claridad
