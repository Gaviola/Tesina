"""
mendieta_submit.py — Envia jobs al cluster Mendieta via sbatch.

Sincroniza el codigo automaticamente antes de enviar (usar --no-sync para saltar).

Uso:
  python scripts/mendieta_submit.py mini_s1      # Mini-VLM stage1  (~8GB)
  python scripts/mendieta_submit.py llava_s1     # LLaVA-Med stage1 (~14GB LoRA)
  python scripts/mendieta_submit.py mini_s2      # Mini-VLM stage2  (~8GB)
  python scripts/mendieta_submit.py llava_s2     # LLaVA-Med stage2 (~14GB LoRA)
  python scripts/mendieta_submit.py classifier   # DenseNet + ViT baselines
  python scripts/mendieta_submit.py all          # todos los jobs (default)
  python scripts/mendieta_submit.py all_s1       # solo stage1 (mini + llava)
  python scripts/mendieta_submit.py all_s2       # solo stage2 (mini + llava)
  python scripts/mendieta_submit.py all --no-sync  # sin sincronizar
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, check_tools, ssh
from scripts.mendieta_sync_up import sync_with_rsync, sync_with_tar, has_rsync

JOBS = {
    "mini_s1":    "slurm/mendieta_train_vlm_s1_mini.sh",
    "llava_s1":   "slurm/mendieta_train_vlm_s1_llava.sh",
    "mini_s2":    "slurm/mendieta_train_vlm_s2_mini.sh",
    "llava_s2":   "slurm/mendieta_train_vlm_s2.sh",
    "classifier": "slurm/mendieta_train_classifier.sh",
}

# Grupos de jobs para envios multiples
GROUPS = {
    "all":    list(JOBS.keys()),
    "all_s1": ["mini_s1", "llava_s1"],
    "all_s2": ["mini_s2", "llava_s2"],
}


def submit_job(name: str, script: str) -> str | None:
    """Envia un job con sbatch y retorna el JOBID."""
    print(f"--- Enviando: {name} ---")
    cmd = f"cd {REMOTE_BASE} && sbatch {script}"
    result = ssh(cmd, capture=True)
    output = result.stdout.strip() + result.stderr.strip()
    print(f"  {output}")

    # Extraer JOBID del mensaje "Submitted batch job XXXXX"
    import re
    match = re.search(r"\d+", output)
    if match:
        jobid = match.group()
        print(f"  JOBID:    {jobid}")
        print(f"  Log:      {REMOTE_BASE}/logs/{jobid}.out")
        print(f"  Monitor:  python scripts/mendieta_monitor.py {jobid}")
        return jobid
    else:
        print("  ADVERTENCIA: no se pudo extraer el JOBID")
        return None


def sync_code() -> None:
    """Sincroniza el codigo local hacia Mendieta antes de enviar jobs."""
    print("=== Sincronizando codigo hacia Mendieta ===")
    if has_rsync():
        rc = sync_with_rsync()
    else:
        rc = sync_with_tar()
    if rc != 0:
        print(f"\nERROR: sincronizacion fallo (codigo {rc})")
        sys.exit(rc)
    print("=== Codigo sincronizado ===\n")


def main():
    valid_choices = list(JOBS.keys()) + list(GROUPS.keys())
    parser = argparse.ArgumentParser(description="Envia jobs a Mendieta")
    parser.add_argument(
        "target", nargs="?", default="all",
        choices=valid_choices,
        help="Job o grupo a encolar (default: all)"
    )
    parser.add_argument(
        "--no-sync", action="store_true",
        help="No sincronizar codigo antes de enviar (usar si ya se sincronizo)"
    )
    args = parser.parse_args()

    check_tools()

    if not args.no_sync:
        sync_code()

    print(f"=== Enviando jobs a Mendieta (target: {args.target}) ===")
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
        print("=== Jobs encolados ===")
        print(f"Ver cola:  python scripts/mendieta_monitor.py")
        for jid in jobids:
            print(f"Ver log:   python scripts/mendieta_monitor.py {jid}")
    else:
        print("ERROR: no se pudo encolar ningun job")
        sys.exit(1)


if __name__ == "__main__":
    main()
