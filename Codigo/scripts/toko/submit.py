"""
submit.py — Envia jobs VLM al cluster TOKO via sbatch.

Uso:
  python scripts/toko/submit.py mini_s1        # Mini-VLM stage1  (~8GB)
  python scripts/toko/submit.py llava_s1       # LLaVA-Med stage1 (~10GB QLoRA)
  python scripts/toko/submit.py mini_s2        # Mini-VLM stage2  (~8GB)
  python scripts/toko/submit.py llava_s2       # LLaVA-Med stage2 (~10GB QLoRA)
  python scripts/toko/submit.py classifier     # DenseNet + ViT baselines
  python scripts/toko/submit.py gen_llava      # Generacion reportes LLaVA-Med
  python scripts/toko/submit.py gen_mini       # Generacion reportes Mini-VLM
  python scripts/toko/submit.py classify_llava # Clasificacion zero-shot LLaVA-Med
  python scripts/toko/submit.py classify_mini  # Clasificacion zero-shot Mini-VLM
  python scripts/toko/submit.py all            # todos los jobs de training (default)
  python scripts/toko/submit.py all_s1         # solo stage1 (mini + llava)
  python scripts/toko/submit.py all_s2         # solo stage2 (mini + llava)
  python scripts/toko/submit.py all_gen        # generacion reportes (ambos modelos)
  python scripts/toko/submit.py all_classify   # clasificacion VLM (ambos modelos)
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.toko.config import TOKO_USER, TOKO_HOST, REMOTE_BASE, REMOTE_LOGS, check_tools, ssh
from scripts.sweep_utils import append_jobs_log

JOBS = {
    "mini_s1":        "slurm/toko/train_vlm_s1_mini.sh",
    "llava_s1":       "slurm/toko/train_vlm_s1_llava.sh",
    "mini_s2":        "slurm/toko/train_vlm_s2_mini.sh",
    "llava_s2":       "slurm/toko/train_vlm_s2_llava.sh",
    "classifier":     "slurm/toko/train_classifier.sh",
    "gen_llava":      "slurm/toko/generate_reports_llava.sh",
    "gen_mini":       "slurm/toko/generate_reports_mini.sh",
    "classify_llava": "slurm/toko/vlm_classify_llava.sh",
    "classify_mini":  "slurm/toko/vlm_classify_mini.sh",
}

# Grupos de jobs para envios multiples
_TRAINING_JOBS = ["mini_s1", "llava_s1", "mini_s2", "llava_s2", "classifier"]
GROUPS = {
    "all":          _TRAINING_JOBS,
    "all_s1":       ["mini_s1", "llava_s1"],
    "all_s2":       ["mini_s2", "llava_s2"],
    "all_gen":      ["gen_llava", "gen_mini"],
    "all_classify": ["classify_llava", "classify_mini"],
}

# Mapeo de job name → subcarpeta de logs
def _log_subdir(name: str) -> str:
    if "llava" in name:
        return "llava_med"
    if "mini" in name:
        return "mini_vlm"
    return "shared"


def submit_job(name: str, script: str) -> str | None:
    """Envia un job con sbatch y retorna el JOBID."""
    print(f"--- Enviando: {name} ---")
    # Crear subdirectorios de logs antes de enviar el job
    cmd = (
        f"cd {REMOTE_BASE} && "
        f"mkdir -p logs/mini_vlm logs/llava_med logs/shared && "
        f"sbatch {script}"
    )
    result = ssh(cmd, capture=True)
    output = result.stdout.strip() + result.stderr.strip()
    print(f"  {output}")

    # Extraer JOBID del mensaje "Submitted batch job XXXXX"
    import re
    match = re.search(r"\d+", output)
    if match:
        jobid = match.group()
        log_dir = f"{REMOTE_LOGS}/{_log_subdir(name)}"
        print(f"  JOBID:    {jobid}")
        print(f"  Log:      {log_dir}/{jobid}.out")
        print(f"  Monitor:  python scripts/toko/monitor.py {jobid}")
        return jobid
    else:
        print("  ADVERTENCIA: no se pudo extraer el JOBID")
        return None


def main():
    valid_choices = list(JOBS.keys()) + list(GROUPS.keys())
    parser = argparse.ArgumentParser(description="Envia jobs a TOKO")
    parser.add_argument(
        "target", nargs="?", default="all",
        choices=valid_choices,
        help="Job o grupo a encolar (default: all)"
    )
    args = parser.parse_args()

    check_tools()

    print(f"=== Enviando jobs a TOKO (target: {args.target}) ===")
    print()

    # Resolver grupo o job individual
    if args.target in GROUPS:
        targets = [(name, JOBS[name]) for name in GROUPS[args.target]]
    else:
        targets = [(args.target, JOBS[args.target])]

    jobids = []
    for name, script in targets:
        jid = submit_job(name, script)
        if jid:
            jobids.append(jid)
        print()

    if jobids:
        append_jobs_log(jobids, "toko", f"submit {args.target}")
        print("=== Jobs encolados ===")
        print(f"Ver cola:  python scripts/toko/monitor.py")
        for jid in jobids:
            print(f"Ver log:   python scripts/toko/monitor.py {jid}")
    else:
        print("ERROR: no se pudo encolar ningun job")
        sys.exit(1)


if __name__ == "__main__":
    main()
