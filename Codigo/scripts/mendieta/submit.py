"""
submit.py — Envia jobs al cluster Mendieta via sbatch.

Sincroniza el codigo automaticamente antes de enviar (usar --no-sync para saltar).

Uso:
  python scripts/mendieta/submit.py mini_s1        # Mini-VLM stage1  (~8GB)
  python scripts/mendieta/submit.py llava_s1       # LLaVA-Med stage1 (~14GB LoRA)
  python scripts/mendieta/submit.py mini_s2        # Mini-VLM stage2  (~8GB)
  python scripts/mendieta/submit.py llava_s2       # LLaVA-Med stage2 (~14GB LoRA)
  python scripts/mendieta/submit.py classifier     # DenseNet + ViT baselines
  python scripts/mendieta/submit.py gen_llava      # Generacion reportes LLaVA-Med (~12h)
  python scripts/mendieta/submit.py gen_mini       # Generacion reportes Mini-VLM (~8h)
  python scripts/mendieta/submit.py gen_llava_mmskin  # Solo MM-SkinQA con LLaVA-Med
  python scripts/mendieta/submit.py gen_mini_mmskin   # Solo MM-SkinQA con Mini-VLM
  python scripts/mendieta/submit.py gen_llava_ham     # Solo HAM10000 con LLaVA-Med
  python scripts/mendieta/submit.py gen_mini_ham      # Solo HAM10000 con Mini-VLM
  python scripts/mendieta/submit.py classify_llava    # Clasificacion zero-shot LLaVA-Med (~4h)
  python scripts/mendieta/submit.py classify_mini     # Clasificacion zero-shot Mini-VLM (~4h)
  python scripts/mendieta/submit.py classify_mini_ft  # Clasificacion fine-tuned Mini-VLM (~4h)
  python scripts/mendieta/submit.py classify_llava_ft # Clasificacion fine-tuned LLaVA-Med (~4h)
  python scripts/mendieta/submit.py all               # todos los jobs de training (default)
  python scripts/mendieta/submit.py all_s1            # solo stage1 (mini + llava)
  python scripts/mendieta/submit.py all_s2            # solo stage2 (mini + llava)
  python scripts/mendieta/submit.py all_gen           # generacion reportes (ambos modelos)
  python scripts/mendieta/submit.py all_gen_mmskin   # solo MM-SkinQA (ambos modelos)
  python scripts/mendieta/submit.py all_gen_ham      # solo HAM10000 (ambos modelos)
  python scripts/mendieta/submit.py all_classify      # clasificacion VLM zero-shot (ambos)
  python scripts/mendieta/submit.py all_classify_ft   # clasificacion VLM fine-tuned (ambos)
  python scripts/mendieta/submit.py all --no-sync     # sin sincronizar
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.mendieta.config import MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS, check_tools, ssh
from scripts.mendieta.sync_up import sync_with_rsync, sync_with_tar, has_rsync

## Cada entrada puede ser:
##   "script.sh"                          — job sin variables extra
##   ("script.sh", {"VAR": "valor"})      — job con variables de entorno extra
JOBS = {
    "mini_s1":        "slurm/mendieta/train_vlm_s1_mini.sh",
    "llava_s1":       "slurm/mendieta/train_vlm_s1_llava.sh",
    "mini_s2":        "slurm/mendieta/train_vlm_s2_mini.sh",
    "llava_s2":       "slurm/mendieta/train_vlm_s2.sh",
    "classifier":     "slurm/mendieta/train_classifier.sh",
    "gen_llava":      "slurm/mendieta/generate_reports_llava.sh",
    "gen_mini":       "slurm/mendieta/generate_reports_mini.sh",
    "gen_llava_mmskin": ("slurm/mendieta/generate_reports_llava.sh", {"DATASETS": "mmskin"}),
    "gen_mini_mmskin":  ("slurm/mendieta/generate_reports_mini.sh",  {"DATASETS": "mmskin"}),
    "gen_llava_ham":    ("slurm/mendieta/generate_reports_llava.sh", {"DATASETS": "ham10000"}),
    "gen_mini_ham":     ("slurm/mendieta/generate_reports_mini.sh",  {"DATASETS": "ham10000"}),
    "classify_llava": "slurm/mendieta/vlm_classify_llava.sh",
    "classify_mini":  "slurm/mendieta/vlm_classify_mini.sh",
    "classify_mini_ft":  "slurm/mendieta/vlm_classify_mini_ft.sh",
    "classify_llava_ft": "slurm/mendieta/vlm_classify_llava_ft.sh",
}

# Grupos de jobs para envios multiples
_TRAINING_JOBS = ["mini_s1", "llava_s1", "mini_s2", "llava_s2", "classifier"]
GROUPS = {
    "all":          _TRAINING_JOBS,
    "all_s1":       ["mini_s1", "llava_s1"],
    "all_s2":       ["mini_s2", "llava_s2"],
    "all_gen":        ["gen_llava", "gen_mini"],
    "all_gen_mmskin": ["gen_llava_mmskin", "gen_mini_mmskin"],
    "all_gen_ham":    ["gen_llava_ham", "gen_mini_ham"],
    "all_classify": ["classify_llava", "classify_mini"],
    "all_classify_ft": ["classify_mini_ft", "classify_llava_ft"],
}

# Mapeo de job name → subcarpeta de logs
def _log_subdir(name: str) -> str:
    if "llava" in name:
        return "llava_med"
    if "mini" in name:
        return "mini_vlm"
    return "shared"


def submit_job(name: str, script: str, env_vars: dict | None = None) -> str | None:
    """Envia un job con sbatch y retorna el JOBID."""
    print(f"--- Enviando: {name} ---")
    export_flag = ""
    if env_vars:
        pairs = ",".join(f'{k}="{v}"' for k, v in env_vars.items())
        export_flag = f" --export=ALL,{pairs}"
        print(f"  Variables extra: {env_vars}")
    # Crear subdirectorios de logs antes de enviar el job
    cmd = (
        f"cd {REMOTE_BASE} && "
        f"mkdir -p logs/mini_vlm logs/llava_med logs/shared && "
        f"sbatch{export_flag} {script}"
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
        print(f"  Monitor:  python scripts/mendieta/monitor.py {jobid}")
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
    def _unpack(name):
        """Retorna (script, env_vars) desde JOBS[name]."""
        entry = JOBS[name]
        if isinstance(entry, tuple):
            return entry[0], entry[1]
        return entry, None

    if args.target in GROUPS:
        targets = [(name, *_unpack(name)) for name in GROUPS[args.target]]
    else:
        targets = [(args.target, *_unpack(args.target))]

    jobids = []
    for name, script, env_vars in targets:
        jid = submit_job(name, script, env_vars)
        if jid:
            jobids.append(jid)
        print()

    if jobids:
        print("=== Jobs encolados ===")
        print(f"Ver cola:  python scripts/mendieta/monitor.py")
        for jid in jobids:
            print(f"Ver log:   python scripts/mendieta/monitor.py {jid}")
    else:
        print("ERROR: no se pudo encolar ningun job")
        sys.exit(1)


if __name__ == "__main__":
    main()
