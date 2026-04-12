"""
sync_down.py — Descarga resultados y checkpoints desde Mendieta hacia local.

Uso:
  python scripts/mendieta/sync_down.py                   # solo metricas JSON (default)
  python scripts/mendieta/sync_down.py --results         # metricas + logs SLURM
  python scripts/mendieta/sync_down.py --checkpoints     # solo modelos .pt (varios GB)
  python scripts/mendieta/sync_down.py --reports         # reportes generados (generated_reports/)
  python scripts/mendieta/sync_down.py --wandb           # solo runs offline de wandb
  python scripts/mendieta/sync_down.py --all             # todo (outputs + logs + reportes)
  python scripts/mendieta/sync_down.py --logs 12345      # descarga solo el log del job 12345
  python scripts/mendieta/sync_down.py --logs 12345 12350  # descarga logs del rango [12345, 12350]

ADVERTENCIA: --checkpoints puede descargar varios GB por modelo.
Usar --results primero para verificar que el entrenamiento termino correctamente.
"""
import sys
import subprocess
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.mendieta.config import (
    MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS, SSH_OPTS,
    LOCAL_OUTPUTS, check_tools, has_rsync, list_remote_subdirs, ssh
)

REMOTE_OUTPUTS = f"{REMOTE_BASE}/outputs"


def download(remote: str, local: Path, label: str, skip_existing: bool = False) -> int:
    local.mkdir(parents=True, exist_ok=True)
    print(f"Descargando {label}...")
    if has_rsync():
        cmd = ["rsync", "-av", "--progress", "-e", f"ssh {' '.join(SSH_OPTS)}"]
        if skip_existing:
            cmd.append("--ignore-existing")
        cmd += [f"{MENDIETA_USER}@{MENDIETA_HOST}:{remote}/", f"{local}/"]
    else:
        cmd = ["scp", *SSH_OPTS, "-r",
               f"{MENDIETA_USER}@{MENDIETA_HOST}:{remote}", str(local.parent)]
    result = subprocess.run(cmd)
    return result.returncode


def download_differential(remote_base: str, local_base: Path, label: str) -> int:
    """Descarga diferencial: solo baja subdirectorios model/dataset/ que faltan localmente.

    Estructura esperada:
        remote_base/<model>/<dataset>/  (ej: llava_med/HAM10000/, mini_vlm/MM-Skin/)

    Los directorios que ya existen localmente con archivos se saltean.
    Los vacios o ausentes se descargan completos.
    """
    print(f"Analizando estado local vs remoto para {label}...")
    model_dirs = list_remote_subdirs(remote_base)
    if not model_dirs:
        print(f"  ADVERTENCIA: no se encontraron subdirectorios en {remote_base}")
        print(f"  Verifique la conexion SSH o que el path remoto exista.")
        return 1

    to_skip: list[tuple[str, str]] = []
    to_download: list[tuple[str, str]] = []

    for model in model_dirs:
        dataset_dirs = list_remote_subdirs(f"{remote_base}/{model}")
        if not dataset_dirs:
            print(f"  ADVERTENCIA: {model}/ no tiene subdirectorios remotos, saltando.")
            continue
        for dataset in dataset_dirs:
            local_dataset = local_base / model / dataset
            if local_dataset.exists() and any(local_dataset.iterdir()):
                to_skip.append((model, dataset))
            else:
                to_download.append((model, dataset))

    print(f"\n  Resumen diferencial — {label}:")
    for model, dataset in to_skip:
        n = sum(1 for f in (local_base / model / dataset).rglob("*") if f.is_file())
        print(f"  [SKIP]  {model}/{dataset}/  ({n} archivos locales)")
    for model, dataset in to_download:
        print(f"  [BAJAR] {model}/{dataset}/")
    if not to_download:
        print("  Todo al dia. Nada que descargar.")
        return 0
    print()

    errors = 0
    for model, dataset in to_download:
        local_dst = local_base / model
        local_dst.mkdir(parents=True, exist_ok=True)
        rc = download(f"{remote_base}/{model}/{dataset}",
                      local_dst / dataset, f"{model}/{dataset}/")
        if rc != 0:
            print(f"  ERROR: fallo la descarga de {model}/{dataset}/")
        errors += rc
    return errors


def download_logs_by_id(job_ids: list[int]) -> int:
    """Descarga .out y .err de job IDs especificos desde el cluster.

    Busca los archivos en todas las subcarpetas de logs/ (mini_vlm/, llava_med/, shared/).
    Preserva la estructura de subcarpeta en local (outputs/slurm_logs/<subdir>/).
    """
    print(f"Buscando logs para {len(job_ids)} job(s): {job_ids}")
    errors = 0
    for jobid in job_ids:
        result = ssh(f"find {REMOTE_LOGS} -name '{jobid}.*' 2>/dev/null", capture=True)
        found_files = [f.strip() for f in result.stdout.strip().splitlines() if f.strip()]
        if not found_files:
            print(f"  ADVERTENCIA: no se encontraron logs para el job {jobid}")
            continue
        for remote_file in found_files:
            # Preservar estructura de subcarpeta: logs/mini_vlm/12345.out → slurm_logs/mini_vlm/
            rel = remote_file[len(REMOTE_LOGS):].lstrip("/")
            local_dst = LOCAL_OUTPUTS / "slurm_logs" / Path(rel).parent
            local_dst.mkdir(parents=True, exist_ok=True)
            filename = Path(remote_file).name
            local_file = local_dst / filename
            print(f"  Descargando {rel}...")
            cmd = ["scp", *SSH_OPTS,
                   f"{MENDIETA_USER}@{MENDIETA_HOST}:{remote_file}", str(local_file)]
            rc = subprocess.run(cmd).returncode
            if rc != 0:
                print(f"  ERROR: fallo la descarga de {rel}")
            errors += rc
    return errors


def verify_results():
    """Verifica que los archivos de metricas de stage1 existan localmente."""
    print()
    print("--- Verificacion de resultados stage1 ---")
    for model in ["mini_vlm", "llava_med"]:
        metrics_file = LOCAL_OUTPUTS / "results" / model / "stage1_metrics.json"
        if metrics_file.exists():
            try:
                data = json.loads(metrics_file.read_text())
                best_epoch = data.get("best_epoch", "?")
                val_loss = data.get("val_loss", "?")
                print(f"  OK  {model}: best_epoch={best_epoch}, val_loss={val_loss}")
            except Exception:
                print(f"  OK  {model}: archivo encontrado (no se pudo parsear)")
        else:
            print(f"  --  {model}: pendiente ({metrics_file.name} no encontrado)")


def main():
    parser = argparse.ArgumentParser(description="Descarga resultados desde Mendieta")
    parser.add_argument("--results", action="store_true",
                        help="Descargar metricas JSON y logs SLURM (default)")
    parser.add_argument("--checkpoints", action="store_true",
                        help="Descargar checkpoints .pt (varios GB)")
    parser.add_argument("--reports", action="store_true",
                        help="Descargar reportes generados (outputs/generated_reports)")
    parser.add_argument("--wandb", action="store_true",
                        help="Descargar solo runs offline de wandb (outputs/wandb/)")
    parser.add_argument("--all", action="store_true",
                        help="Descargar todo (outputs + logs + reportes)")
    parser.add_argument("--force", action="store_true",
                        help="Forzar re-descarga completa ignorando estado local")
    parser.add_argument("--logs", nargs="+", type=int, metavar="JOBID",
                        help="Descargar logs de job(s) especificos. "
                             "Un valor: job N. Dos valores: rango [N, M] inclusive.")
    args = parser.parse_args()

    # Validar --logs
    if args.logs is not None:
        if len(args.logs) == 1:
            job_ids = args.logs
        elif len(args.logs) == 2:
            n, m = args.logs
            if n > m:
                print(f"ERROR: el rango [{n}, {m}] es invalido (N debe ser <= M)")
                sys.exit(1)
            job_ids = list(range(n, m + 1))
        else:
            print("ERROR: --logs acepta 1 o 2 valores (job N o rango N M)")
            sys.exit(1)

        check_tools()
        print(f"=== Descargando logs desde Mendieta ===")
        print(f"Jobs: {job_ids}")
        print()
        rc = download_logs_by_id(job_ids)
        if rc:
            print(f"\nADVERTENCIA: algunos logs no se pudieron descargar")
        print("\n=== Descarga de logs completada ===")
        return

    # Default: solo resultados
    if not any([args.results, args.checkpoints, args.reports, args.wandb, args.all]):
        args.results = True

    check_tools()

    print(f"=== Descargando desde Mendieta ===")
    print(f"Remoto: {MENDIETA_USER}@{MENDIETA_HOST}:{REMOTE_OUTPUTS}/")
    print(f"Local:  {LOCAL_OUTPUTS}/")
    print()

    errors = 0

    if args.results or args.all:
        rc = download(f"{REMOTE_OUTPUTS}/results",
                      LOCAL_OUTPUTS / "results", "results/")
        errors += rc

        # Logs SLURM (todos los subdirs)
        rc = download(REMOTE_LOGS,
                      LOCAL_OUTPUTS / "slurm_logs", "logs SLURM")
        errors += rc

    if args.wandb or args.all:
        rc = download(f"{REMOTE_OUTPUTS}/wandb",
                      LOCAL_OUTPUTS / "wandb", "wandb/ (runs offline)")
        errors += rc
        if rc == 0:
            print("  -> Para subir a wandb.ai: wandb sync outputs/wandb/")

    if args.checkpoints or args.all:
        print("ADVERTENCIA: los checkpoints pueden ser varios GB. Esto puede tardar.")
        if args.force:
            rc = download(f"{REMOTE_OUTPUTS}/checkpoints",
                          LOCAL_OUTPUTS / "checkpoints", "checkpoints/")
        else:
            rc = download_differential(f"{REMOTE_OUTPUTS}/checkpoints",
                                       LOCAL_OUTPUTS / "checkpoints", "checkpoints/")
        errors += rc

    if args.reports or args.all:
        if args.force:
            rc = download(f"{REMOTE_OUTPUTS}/generated_reports",
                          LOCAL_OUTPUTS / "generated_reports", "generated_reports/")
        else:
            rc = download_differential(f"{REMOTE_OUTPUTS}/generated_reports",
                                       LOCAL_OUTPUTS / "generated_reports",
                                       "generated_reports/")
        errors += rc

    if errors:
        print(f"\nADVERTENCIA: algunos archivos no se pudieron descargar")

    verify_results()

    print()
    print("=== Descarga completada ===")


if __name__ == "__main__":
    main()
