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

## Cluster paths para LR de cada clasificador. ConvNeXt y Swin requieren
## pesos torchvision pre-descargados en ~/.cache/torch/hub/checkpoints/.
_CLS_SCRIPT = "slurm/toko/train_classifier.sh"
_CLS_LR = {
    "densenet":      "7.91e-5",
    "vit":           "1.56e-5",
    "convnext_tiny": "1e-4",
    "swin_tiny":     "1e-4",
}
_ABL_MODEL = "convnext_tiny"

## Cada entrada puede ser:
##   "script.sh"                          — job sin variables extra
##   ("script.sh", {"VAR": "valor"})      — job con variables de entorno extra
JOBS = {
    "mini_s1":        "slurm/toko/train_vlm_s1_mini.sh",
    "llava_s1":       "slurm/toko/train_vlm_s1_llava.sh",
    "mini_s2":        "slurm/toko/train_vlm_s2_mini.sh",
    "llava_s2":       "slurm/toko/train_vlm_s2_llava.sh",
    ## Clasificadores Fase 1 — verificación legacy
    "cls_densenet_legacy": (_CLS_SCRIPT, {
        "MODEL": "densenet", "RECIPE": "legacy", "LR": _CLS_LR["densenet"],
    }),
    "cls_vit_legacy": (_CLS_SCRIPT, {
        "MODEL": "vit", "RECIPE": "legacy", "LR": _CLS_LR["vit"],
        "EXTRA_FLAGS": "--scheduler none",
    }),
    ## Clasificadores Fase 1 — corridas finales modern (con HIBA OOD eval)
    "cls_densenet_modern": (_CLS_SCRIPT, {
        "MODEL": "densenet", "RECIPE": "modern", "LR": _CLS_LR["densenet"],
        "EXTRA_FLAGS": "--eval-hiba",
    }),
    "cls_vit_modern": (_CLS_SCRIPT, {
        "MODEL": "vit", "RECIPE": "modern", "LR": _CLS_LR["vit"],
        "EXTRA_FLAGS": "--eval-hiba",
    }),
    "cls_convnext_modern": (_CLS_SCRIPT, {
        "MODEL": "convnext_tiny", "RECIPE": "modern", "LR": _CLS_LR["convnext_tiny"],
        "EXTRA_FLAGS": "--eval-hiba",
    }),
    "cls_swin_modern": (_CLS_SCRIPT, {
        "MODEL": "swin_tiny", "RECIPE": "modern", "LR": _CLS_LR["swin_tiny"],
        "EXTRA_FLAGS": "--eval-hiba",
    }),
    ## Ablaciones (override _ABL_MODEL al ganador real tras corridas modern)
    "cls_abl_no_mixup": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_mixup",
        "EXTRA_FLAGS": "--mixup-alpha 0 --cutmix-alpha 0 --eval-hiba",
    }),
    "cls_abl_no_randaug": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_randaug",
        "EXTRA_FLAGS": "--no-randaugment --eval-hiba",
    }),
    "cls_abl_no_focal": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_focal",
        "EXTRA_FLAGS": "--focal-gamma 0 --eval-hiba",
    }),
    "cls_abl_no_tta": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_tta",
        "EXTRA_FLAGS": "--no-tta --eval-hiba",
    }),
    "cls_abl_no_two_stage": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_two_stage",
        "EXTRA_FLAGS": "--no-two-stage --eval-hiba",
    }),
    "cls_abl_no_label_smoothing": (_CLS_SCRIPT, {
        "MODEL": _ABL_MODEL, "RECIPE": "modern", "LR": _CLS_LR[_ABL_MODEL],
        "RUN_NAME": f"{_ABL_MODEL}_abl_no_label_smoothing",
        "EXTRA_FLAGS": "--label-smoothing 0 --eval-hiba",
    }),
    ## Compat alias: corre densenet legacy via script genérico
    "classifier": (_CLS_SCRIPT, {
        "MODEL": "densenet", "RECIPE": "legacy", "LR": _CLS_LR["densenet"],
    }),
    "gen_llava":      "slurm/toko/generate_reports_llava.sh",
    "gen_mini":       "slurm/toko/generate_reports_mini.sh",
    "classify_llava": "slurm/toko/vlm_classify_llava.sh",
    "classify_mini":  "slurm/toko/vlm_classify_mini.sh",
}

# Grupos de jobs para envios multiples
_TRAINING_JOBS = ["mini_s1", "llava_s1", "mini_s2", "llava_s2", "classifier"]
_CLS_LEGACY_JOBS = ["cls_densenet_legacy", "cls_vit_legacy"]
_CLS_MODERN_JOBS = ["cls_densenet_modern", "cls_vit_modern", "cls_convnext_modern", "cls_swin_modern"]
_CLS_ABLATION_JOBS = [
    "cls_abl_no_mixup", "cls_abl_no_randaug", "cls_abl_no_focal",
    "cls_abl_no_tta", "cls_abl_no_two_stage", "cls_abl_no_label_smoothing",
]
GROUPS = {
    "all":          _TRAINING_JOBS,
    "all_s1":       ["mini_s1", "llava_s1"],
    "all_s2":       ["mini_s2", "llava_s2"],
    "all_gen":      ["gen_llava", "gen_mini"],
    "all_classify": ["classify_llava", "classify_mini"],
    ## Fase 1 — clasificadores
    "all_cls_legacy":   _CLS_LEGACY_JOBS,
    "all_cls_modern":   _CLS_MODERN_JOBS,
    "all_cls_ablation": _CLS_ABLATION_JOBS,
    "all_cls":          _CLS_LEGACY_JOBS + _CLS_MODERN_JOBS,
    "all_cls_full":     _CLS_LEGACY_JOBS + _CLS_MODERN_JOBS + _CLS_ABLATION_JOBS,
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
