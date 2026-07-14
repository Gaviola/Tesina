"""
submit.py — Envia jobs al cluster Mendieta via sbatch.

Sincroniza el codigo automaticamente antes de enviar (usar --no-sync para saltar).

Uso:
  python scripts/mendieta/submit.py mini_s1        # Mini-VLM stage1  (~8GB)
  python scripts/mendieta/submit.py llava_s1       # LLaVA-Med stage1 (~14GB LoRA)
  python scripts/mendieta/submit.py mini_s2        # Mini-VLM stage2  (~8GB)
  python scripts/mendieta/submit.py llava_s2       # LLaVA-Med stage2 (~14GB LoRA)
  python scripts/mendieta/submit.py mini_s2_v2     # Mini-VLM stage2 v2 — epochs=10 (~8GB)
  python scripts/mendieta/submit.py llava_s2_v2    # LLaVA-Med stage2 v2 — epochs=10 (~14GB)
  python scripts/mendieta/submit.py classifier     # DenseNet + ViT baselines
  python scripts/mendieta/submit.py gen_llava      # Generacion reportes LLaVA-Med (~12h)
  python scripts/mendieta/submit.py gen_mini       # Generacion reportes Mini-VLM (~8h)
  python scripts/mendieta/submit.py gen_llava_mmskin  # Solo MM-SkinQA con LLaVA-Med
  python scripts/mendieta/submit.py gen_mini_mmskin   # Solo MM-SkinQA con Mini-VLM
  python scripts/mendieta/submit.py gen_llava_ham     # Solo HAM10000 con LLaVA-Med
  python scripts/mendieta/submit.py gen_mini_ham      # Solo HAM10000 con Mini-VLM
  python scripts/mendieta/submit.py classify_llava    # Clasificacion generate LLaVA-Med (~4h)
  python scripts/mendieta/submit.py classify_mini     # Clasificacion generate Mini-VLM (~4h)
  python scripts/mendieta/submit.py classify_mini_ft  # Clasificacion fine-tuned Mini-VLM (~4h)
  python scripts/mendieta/submit.py classify_llava_ft # Clasificacion fine-tuned LLaVA-Med (~4h)
  python scripts/mendieta/submit.py classify_mini_lik     # Clasificacion likelihood Mini-VLM base (~4h)
  python scripts/mendieta/submit.py classify_llava_lik    # Clasificacion likelihood LLaVA-Med base (~4h)
  python scripts/mendieta/submit.py classify_mini_ft_lik  # Clasificacion likelihood Mini-VLM fine-tuned (~4h)
  python scripts/mendieta/submit.py classify_llava_ft_lik # Clasificacion likelihood LLaVA-Med fine-tuned (~4h)
  python scripts/mendieta/submit.py classify_llava_cot    # Clasificacion CoT LLaVA-Med base (~6h)
  python scripts/mendieta/submit.py classify_mini_cot     # Clasificacion CoT Mini-VLM base (~6h)
  python scripts/mendieta/submit.py classify_llava_ft_cot # Clasificacion CoT LLaVA-Med fine-tuned (~6h)
  python scripts/mendieta/submit.py classify_mini_ft_cot  # Clasificacion CoT Mini-VLM fine-tuned (~6h)
  python scripts/mendieta/submit.py all               # todos los jobs de training (default)
  python scripts/mendieta/submit.py all_s1            # solo stage1 (mini + llava)
  python scripts/mendieta/submit.py all_s2            # solo stage2 (mini + llava)
  python scripts/mendieta/submit.py all_gen           # generacion reportes (ambos modelos)
  python scripts/mendieta/submit.py all_gen_mmskin   # solo MM-SkinQA (ambos modelos)
  python scripts/mendieta/submit.py all_gen_ham      # solo HAM10000 (ambos modelos)
  python scripts/mendieta/submit.py all_classify      # clasificacion generate (ambos)
  python scripts/mendieta/submit.py all_classify_ft   # clasificacion VLM fine-tuned (ambos)
  python scripts/mendieta/submit.py all_classify_lik  # likelihood base + ft (4 jobs)
  python scripts/mendieta/submit.py all_classify_cot  # CoT base + ft (4 jobs)
  # --- v2 (Stage 2 v2 checkpoint, epochs=10): ---
  python scripts/mendieta/submit.py classify_llava_ft_v2  # FT v2 generate LLaVA-Med
  python scripts/mendieta/submit.py classify_mini_ft_v2   # FT v2 generate Mini-VLM
  python scripts/mendieta/submit.py gen_llava_v2          # Generacion v2 LLaVA-Med (3 datasets)
  python scripts/mendieta/submit.py gen_mini_v2           # Generacion v2 Mini-VLM (3 datasets)
  python scripts/mendieta/submit.py all_classify_lik_v2   # 2 jobs FT v2 likelihood
  python scripts/mendieta/submit.py all_classify_cot_v2   # 2 jobs FT v2 CoT
  python scripts/mendieta/submit.py all_gen_v2            # 2 jobs generacion v2
  python scripts/mendieta/submit.py all_vlm_v2            # 6 jobs: clasif FT + generacion (v2)
  python scripts/mendieta/submit.py all --no-sync         # sin sincronizar
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.mendieta.config import MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS, check_tools, ssh
from scripts.mendieta.sync_up import sync_with_rsync, sync_with_tar, has_rsync
from scripts.sweep_utils import append_jobs_log

## Cada entrada puede ser:
##   "script.sh"                          — job sin variables extra
##   ("script.sh", {"VAR": "valor"})      — job con variables de entorno extra
## Cluster paths para LR de cada clasificador. ConvNeXt y Swin requieren
## pesos torchvision pre-descargados en ~/.cache/torch/hub/checkpoints/.
_CLS_SCRIPT = "slurm/mendieta/train_classifier.sh"
_CLS_LR = {
    "densenet":      "7.91e-5",   # del sweep fase 1
    "vit":           "1.56e-5",   # del sweep fase 1
    "convnext_tiny": "1e-4",      # default modern (ajustable)
    "swin_tiny":     "1e-4",      # default modern (ajustable)
}
## Modelo target para ablaciones. Actualizar al ganador real tras cls_<m>_modern.
_ABL_MODEL = "convnext_tiny"

JOBS = {
    "mini_s1":        "slurm/mendieta/train_vlm_s1_mini.sh",
    "llava_s1":       "slurm/mendieta/train_vlm_s1_llava.sh",
    ## Stage 2 v1: training original (epochs=3, HPs default)
    "mini_s2":        "slurm/mendieta/v1/train_vlm_s2_mini.sh",
    "llava_s2":       "slurm/mendieta/v1/train_vlm_s2.sh",
    ## Stage 2 v2: mismos HPs del mejor trial del sweep, con epochs=10
    ## (los scripts viven en slurm/mendieta/v2/; nombres sin sufijo _v2 porque la carpeta indica version)
    "mini_s2_v2":     "slurm/mendieta/v2/train_vlm_s2_mini.sh",
    "llava_s2_v2":    "slurm/mendieta/v2/train_vlm_s2.sh",
    ## Clasificadores Fase 1 — verificación legacy (reproducir baselines)
    "cls_densenet_legacy": (_CLS_SCRIPT, {
        "MODEL": "densenet", "RECIPE": "legacy", "LR": _CLS_LR["densenet"],
    }),
    "cls_vit_legacy": (_CLS_SCRIPT, {
        "MODEL": "vit", "RECIPE": "legacy", "LR": _CLS_LR["vit"],
        "EXTRA_FLAGS": "--scheduler none",   # baseline ViT no usaba scheduler
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
    ## Ablaciones sobre el modelo ganador. Override _ABL_MODEL al inicio.
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
    ## Compat alias del registro previo (corre densenet_legacy con script genérico)
    "classifier": (_CLS_SCRIPT, {
        "MODEL": "densenet", "RECIPE": "legacy", "LR": _CLS_LR["densenet"],
    }),
    ## Generacion de reportes v1 (Stage 2 v1: epochs=3)
    "gen_llava":      "slurm/mendieta/v1/generate_reports_llava.sh",
    "gen_mini":       "slurm/mendieta/v1/generate_reports_mini.sh",
    "gen_llava_mmskin": ("slurm/mendieta/v1/generate_reports_llava.sh", {"DATASETS": "mmskin"}),
    "gen_mini_mmskin":  ("slurm/mendieta/v1/generate_reports_mini.sh",  {"DATASETS": "mmskin"}),
    "gen_llava_ham":      ("slurm/mendieta/v1/generate_reports_llava.sh", {"DATASETS": "ham10000"}),
    "gen_mini_ham":       ("slurm/mendieta/v1/generate_reports_mini.sh",  {"DATASETS": "ham10000"}),
    "gen_llava_skincare": ("slurm/mendieta/v1/generate_reports_llava.sh", {"DATASETS": "skincare"}),
    "gen_mini_skincare":  ("slurm/mendieta/v1/generate_reports_mini.sh",  {"DATASETS": "skincare"}),
    ## Generacion de reportes v2 (Stage 2 v2: epochs=10, mejores HPs del sweep)
    "gen_llava_v2":      "slurm/mendieta/v2/generate_reports_llava.sh",
    "gen_mini_v2":       "slurm/mendieta/v2/generate_reports_mini.sh",
    "gen_llava_mmskin_v2": ("slurm/mendieta/v2/generate_reports_llava.sh", {"DATASETS": "mmskin"}),
    "gen_mini_mmskin_v2":  ("slurm/mendieta/v2/generate_reports_mini.sh",  {"DATASETS": "mmskin"}),
    "gen_llava_ham_v2":      ("slurm/mendieta/v2/generate_reports_llava.sh", {"DATASETS": "ham10000"}),
    "gen_mini_ham_v2":       ("slurm/mendieta/v2/generate_reports_mini.sh",  {"DATASETS": "ham10000"}),
    "gen_llava_skincare_v2": ("slurm/mendieta/v2/generate_reports_llava.sh", {"DATASETS": "skincare"}),
    "gen_mini_skincare_v2":  ("slurm/mendieta/v2/generate_reports_mini.sh",  {"DATASETS": "skincare"}),
    ## Clasificacion VLM zero-shot (no cambia con Stage 2 v2)
    "classify_llava": "slurm/mendieta/vlm_classify_llava.sh",
    "classify_mini":  "slurm/mendieta/vlm_classify_mini.sh",
    ## Clasificacion VLM fine-tuned v1 (Stage 2 v1 checkpoint)
    "classify_mini_ft":  "slurm/mendieta/v1/vlm_classify_mini_ft.sh",
    "classify_llava_ft": "slurm/mendieta/v1/vlm_classify_llava_ft.sh",
    ## Clasificacion VLM fine-tuned v2 (Stage 2 v2 checkpoint, post-mv a outputs/results/{model}/v2/)
    "classify_mini_ft_v2":  "slurm/mendieta/v2/vlm_classify_mini_ft.sh",
    "classify_llava_ft_v2": "slurm/mendieta/v2/vlm_classify_llava_ft.sh",
    ## Variantes likelihood: reutilizan los mismos scripts SLURM y cambian
    ## el metodo via variable de entorno METHOD (ver scripts sbatch).
    "classify_llava_lik":    ("slurm/mendieta/vlm_classify_llava.sh",       {"METHOD": "likelihood"}),
    "classify_mini_lik":     ("slurm/mendieta/vlm_classify_mini.sh",        {"METHOD": "likelihood"}),
    "classify_llava_ft_lik": ("slurm/mendieta/v1/vlm_classify_llava_ft.sh", {"METHOD": "likelihood"}),
    "classify_mini_ft_lik":  ("slurm/mendieta/v1/vlm_classify_mini_ft.sh",  {"METHOD": "likelihood"}),
    ## Variantes likelihood v2 (Stage 2 v2 checkpoint)
    "classify_llava_ft_lik_v2": ("slurm/mendieta/v2/vlm_classify_llava_ft.sh", {"METHOD": "likelihood"}),
    "classify_mini_ft_lik_v2":  ("slurm/mendieta/v2/vlm_classify_mini_ft.sh",  {"METHOD": "likelihood"}),
    ## Domain gap: clasificacion ZERO-SHOT likelihood sobre FOTO CLINICA (SkinCAP -> 7 clases HAM).
    ## Los scripts hardcodean --method likelihood --eval-dataset skincap_clinical.
    "classify_llava_clinical": "slurm/mendieta/vlm_classify_llava_clinical.sh",
    "classify_mini_clinical":  "slurm/mendieta/vlm_classify_mini_clinical.sh",
    ## Ensamble cascada: pilot de grounding (baseline vs oracle, ~100 imgs HAM, LLaVA v2).
    "pilot_ensemble_llava": "slurm/mendieta/pilot_ensemble_llava.sh",
    ## Ensamble v2: re-pilot con 3 variantes de prompt que fuerzan commitment (oracle).
    "pilot_ensemble_v2_llava": "slurm/mendieta/pilot_ensemble_v2_llava.sh",
    ## Ensamble v3: variante "noreasoning" (prohíbe el razonamiento) — último lever de prompt.
    "pilot_ensemble_v3_llava": "slurm/mendieta/pilot_ensemble_v3_llava.sh",
    ## Ensamble — corrida completa 4 condiciones (baseline/oracle/swin/dermlip), noreasoning, test split.
    "ensemble_full_llava": "slurm/mendieta/ensemble_full_llava.sh",
    "ensemble_full_mini":  "slurm/mendieta/ensemble_full_mini.sh",
    ## Ola 1 (P1.1) — SkinVL derm-especializado. Orden: convert -> smoke -> ensemble.
    "convert_skinvl":   "slurm/mendieta/v3/convert_skinvl.sh",
    "smoke_skinvl":     "slurm/mendieta/v3/smoke_skinvl.sh",
    "ensemble_skinvl":  "slurm/mendieta/v3/generate_reports_skinvl.sh",
    ## P4.1 (mejoras #9) — ablaciones imagen-vs-dx / dx-erróneo para LLaVA-Med y Mini-VLM.
    "abl_llava_mini":   "slurm/mendieta/v3/ablations_llava_mini.sh",
    ## Ensamble — Nivel 1 sobre SkinCoT (con referencias): baseline vs oracle-noreasoning, LLaVA.
    "ensemble_skincot_l1_llava": "slurm/mendieta/ensemble_skincot_level1_llava.sh",
    ## Variantes CoT: mismo mecanismo de env var METHOD=cot.
    ## CoT genera respuestas largas (~200 tokens vs ~32) — puede ser ~2x mas lento.
    "classify_llava_cot":    ("slurm/mendieta/vlm_classify_llava.sh",       {"METHOD": "cot"}),
    "classify_mini_cot":     ("slurm/mendieta/vlm_classify_mini.sh",        {"METHOD": "cot"}),
    "classify_llava_ft_cot": ("slurm/mendieta/v1/vlm_classify_llava_ft.sh", {"METHOD": "cot"}),
    "classify_mini_ft_cot":  ("slurm/mendieta/v1/vlm_classify_mini_ft.sh",  {"METHOD": "cot"}),
    ## Variantes CoT v2 (Stage 2 v2 checkpoint)
    "classify_llava_ft_cot_v2": ("slurm/mendieta/v2/vlm_classify_llava_ft.sh", {"METHOD": "cot"}),
    "classify_mini_ft_cot_v2":  ("slurm/mendieta/v2/vlm_classify_mini_ft.sh",  {"METHOD": "cot"}),
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
    "all_s2_v2":    ["mini_s2_v2", "llava_s2_v2"],
    ## Fase 1 — clasificadores
    "all_cls_legacy":   _CLS_LEGACY_JOBS,    # 2 jobs verificación
    "all_cls_modern":   _CLS_MODERN_JOBS,    # 4 jobs corridas finales
    "all_cls_ablation": _CLS_ABLATION_JOBS,  # 6 jobs ablaciones (modelo en _ABL_MODEL)
    "all_cls":          _CLS_LEGACY_JOBS + _CLS_MODERN_JOBS,
    "all_cls_full":     _CLS_LEGACY_JOBS + _CLS_MODERN_JOBS + _CLS_ABLATION_JOBS,
    "all_gen":        ["gen_llava", "gen_mini"],
    "all_gen_mmskin": ["gen_llava_mmskin", "gen_mini_mmskin"],
    "all_gen_ham":      ["gen_llava_ham", "gen_mini_ham"],
    "all_gen_skincare": ["gen_llava_skincare", "gen_mini_skincare"],
    "all_gen_v2":        ["gen_llava_v2", "gen_mini_v2"],
    "all_gen_mmskin_v2": ["gen_llava_mmskin_v2", "gen_mini_mmskin_v2"],
    "all_gen_ham_v2":    ["gen_llava_ham_v2", "gen_mini_ham_v2"],
    "all_gen_skincare_v2": ["gen_llava_skincare_v2", "gen_mini_skincare_v2"],
    "all_classify": ["classify_llava", "classify_mini"],
    "all_classify_ft": ["classify_mini_ft", "classify_llava_ft"],
    "all_classify_ft_v2": ["classify_mini_ft_v2", "classify_llava_ft_v2"],
    ## Comparacion 2x2: {base, ft} x {generate, likelihood}.
    ## Este grupo corre los 4 jobs de likelihood (los de generate se corren
    ## con all_classify y all_classify_ft).
    "all_classify_lik": [
        "classify_llava_lik",
        "classify_mini_lik",
        "classify_llava_ft_lik",
        "classify_mini_ft_lik",
    ],
    ## v2: solo los 2 jobs FT con Stage 2 v2 checkpoint (ZS no cambia entre v1 y v2).
    "all_classify_lik_v2": [
        "classify_llava_ft_lik_v2",
        "classify_mini_ft_lik_v2",
    ],
    ## Domain gap: clasificacion ZS likelihood sobre foto clinica (SkinCAP), 2 jobs.
    "all_classify_clinical": [
        "classify_llava_clinical",
        "classify_mini_clinical",
    ],
    ## CoT base + ft (4 jobs).
    "all_classify_cot": [
        "classify_llava_cot",
        "classify_mini_cot",
        "classify_llava_ft_cot",
        "classify_mini_ft_cot",
    ],
    ## v2: solo los 2 jobs FT con Stage 2 v2 checkpoint.
    "all_classify_cot_v2": [
        "classify_llava_ft_cot_v2",
        "classify_mini_ft_cot_v2",
    ],
    ## Conjunto completo de evaluacion VLM v2: 4 clasificacion + 2 generacion = 6 jobs.
    "all_vlm_v2": [
        "classify_llava_ft_lik_v2",
        "classify_mini_ft_lik_v2",
        "classify_llava_ft_cot_v2",
        "classify_mini_ft_cot_v2",
        "gen_llava_v2",
        "gen_mini_v2",
    ],
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
        f"mkdir -p logs/mini_vlm logs/llava_med logs/shared logs/skinvl && "
        f"sbatch{export_flag} {script}"
    )
    result = ssh(cmd, capture=True)
    output = (result.stdout or "").strip() + (result.stderr or "").strip()
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
        append_jobs_log(jobids, "mendieta", f"submit {args.target}")
        print("=== Jobs encolados ===")
        print(f"Ver cola:  python scripts/mendieta/monitor.py")
        for jid in jobids:
            print(f"Ver log:   python scripts/mendieta/monitor.py {jid}")
    else:
        print("ERROR: no se pudo encolar ningun job")
        sys.exit(1)


if __name__ == "__main__":
    main()
