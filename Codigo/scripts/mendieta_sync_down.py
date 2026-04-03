"""
mendieta_sync_down.py — Descarga resultados y checkpoints desde Mendieta hacia local.

Uso:
  python scripts/mendieta_sync_down.py                   # solo metricas JSON (default)
  python scripts/mendieta_sync_down.py --results         # metricas + logs SLURM
  python scripts/mendieta_sync_down.py --checkpoints     # solo modelos .pt (varios GB)
  python scripts/mendieta_sync_down.py --reports         # reportes generados (generated_reports/)
  python scripts/mendieta_sync_down.py --all             # todo (outputs + logs + reportes)

ADVERTENCIA: --checkpoints puede descargar varios GB por modelo.
Usar --results primero para verificar que el entrenamiento termino correctamente.
"""
import sys
import subprocess
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import (
    MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS, SSH_OPTS,
    LOCAL_OUTPUTS, check_tools, has_rsync, list_remote_subdirs
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


def verify_results():
    """Verifica que los archivos de metricas de stage1 existan localmente."""
    print()
    print("--- Verificacion de resultados stage1 ---")
    for model in ["mini_vlm", "llava_med"]:
        metrics_file = LOCAL_OUTPUTS / "results" / f"stage1_{model}_metrics.json"
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
    parser.add_argument("--all", action="store_true",
                        help="Descargar todo (outputs + logs + reportes)")
    parser.add_argument("--force", action="store_true",
                        help="Forzar re-descarga completa ignorando estado local")
    args = parser.parse_args()

    # Default: solo resultados
    if not any([args.results, args.checkpoints, args.reports, args.all]):
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

        # Logs SLURM
        rc = download(REMOTE_LOGS,
                      LOCAL_OUTPUTS / "slurm_logs", "logs SLURM")
        errors += rc

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
