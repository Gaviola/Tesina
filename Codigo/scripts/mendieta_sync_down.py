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
    LOCAL_OUTPUTS, check_tools, has_rsync
)

REMOTE_OUTPUTS = f"{REMOTE_BASE}/outputs"


def download(remote: str, local: Path, label: str):
    local.mkdir(parents=True, exist_ok=True)
    print(f"Descargando {label}...")
    if has_rsync():
        cmd = ["rsync", "-av", "--progress", "-e", f"ssh {' '.join(SSH_OPTS)}",
               f"{MENDIETA_USER}@{MENDIETA_HOST}:{remote}/", f"{local}/"]
    else:
        cmd = ["scp", *SSH_OPTS, "-r",
               f"{MENDIETA_USER}@{MENDIETA_HOST}:{remote}", str(local.parent)]
    result = subprocess.run(cmd)
    return result.returncode


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
        rc = download(f"{REMOTE_OUTPUTS}/checkpoints",
                      LOCAL_OUTPUTS / "checkpoints", "checkpoints/")
        errors += rc

    if args.reports or args.all:
        rc = download(f"{REMOTE_OUTPUTS}/generated_reports",
                      LOCAL_OUTPUTS / "generated_reports", "generated_reports/")
        errors += rc

    if errors:
        print(f"\nADVERTENCIA: algunos archivos no se pudieron descargar")

    verify_results()

    print()
    print("=== Descarga completada ===")


if __name__ == "__main__":
    main()
