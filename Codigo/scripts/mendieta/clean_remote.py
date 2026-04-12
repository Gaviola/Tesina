"""
clean_remote.py — Elimina archivos de outputs en Mendieta para liberar espacio.

Las flags corresponden a las mismas categorias que sync_down.py:
  --results     → outputs/results/
  --checkpoints → outputs/checkpoints/
  --reports     → outputs/generated_reports/
  --wandb       → outputs/wandb/
  --logs        → logs/ (logs SLURM)
  --all         → todo lo anterior

Uso:
  python scripts/mendieta/clean_remote.py --wandb           # borrar runs offline de wandb
  python scripts/mendieta/clean_remote.py --checkpoints     # borrar checkpoints (libera mas espacio)
  python scripts/mendieta/clean_remote.py --all             # borrar todo outputs/ + logs/
  python scripts/mendieta/clean_remote.py --all --dry-run   # ver que se borraria sin borrar
  python scripts/mendieta/clean_remote.py --checkpoints -y  # sin confirmacion interactiva
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.mendieta.config import (
    MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS,
    check_tools, ssh
)

REMOTE_OUTPUTS = f"{REMOTE_BASE}/outputs"


def remote_info(path: str) -> tuple[bool, str]:
    """Retorna (existe, tamaño) consultando el cluster en una sola llamada SSH."""
    result = ssh(f"du -sh {path} 2>/dev/null | cut -f1", capture=True)
    size = result.stdout.strip()
    return bool(size), size or "?"


def clean_remote(path: str, label: str) -> int:
    """Borra path en el cluster. Retorna 0 si OK, 1 si error."""
    exists, size = remote_info(path)
    if not exists:
        print(f"  [SKIP] {label}: no existe en el cluster")
        return 0
    print(f"  Borrando {label} ({size})...")
    result = ssh(f"rm -rf {path}")
    if result.returncode == 0:
        print(f"    OK")
    else:
        print(f"    ERROR al borrar {label}")
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Elimina archivos de outputs en Mendieta para liberar espacio"
    )
    parser.add_argument("--results", action="store_true",
                        help="Borrar metricas JSON (outputs/results/)")
    parser.add_argument("--checkpoints", action="store_true",
                        help="Borrar checkpoints .pt (outputs/checkpoints/)")
    parser.add_argument("--reports", action="store_true",
                        help="Borrar reportes generados (outputs/generated_reports/)")
    parser.add_argument("--wandb", action="store_true",
                        help="Borrar runs offline de wandb (outputs/wandb/)")
    parser.add_argument("--logs", action="store_true",
                        help="Borrar logs SLURM (logs/)")
    parser.add_argument("--all", action="store_true",
                        help="Borrar todo (outputs/ + logs/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar que se borraria sin borrar nada")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="No pedir confirmacion interactiva")
    args = parser.parse_args()

    if not any([args.results, args.checkpoints, args.reports,
                args.wandb, args.logs, args.all]):
        parser.print_help()
        print("\nERROR: especifica al menos una flag "
              "(--results, --checkpoints, --reports, --wandb, --logs, --all)")
        sys.exit(1)

    check_tools()

    # Construir lista de (path_remoto, etiqueta)
    targets: list[tuple[str, str]] = []
    if args.results or args.all:
        targets.append((f"{REMOTE_OUTPUTS}/results", "outputs/results/"))
    if args.checkpoints or args.all:
        targets.append((f"{REMOTE_OUTPUTS}/checkpoints", "outputs/checkpoints/"))
    if args.reports or args.all:
        targets.append((f"{REMOTE_OUTPUTS}/generated_reports", "outputs/generated_reports/"))
    if args.wandb or args.all:
        targets.append((f"{REMOTE_OUTPUTS}/wandb", "outputs/wandb/"))
    if args.logs or args.all:
        targets.append((REMOTE_LOGS, "logs/"))

    print(f"=== Limpieza remota en Mendieta ===")
    print(f"Cluster: {MENDIETA_USER}@{MENDIETA_HOST}")
    print(f"Base:    {REMOTE_BASE}")
    print()

    # Consultar tamaños y existencia
    print("Contenido a eliminar:")
    existing_targets = []
    for path, label in targets:
        exists, size = remote_info(path)
        if exists:
            print(f"  {label:<40}  {size:>8}   {path}")
            existing_targets.append((path, label))
        else:
            print(f"  {label:<40}  [no existe]")
    print()

    if not existing_targets:
        print("Nada que limpiar.")
        return

    if args.dry_run:
        print(f"Modo DRY-RUN: se borrarían {len(existing_targets)} directorio(s). "
              "Quitá --dry-run para ejecutar.")
        return

    if not args.yes:
        confirm = input(
            f"¿Confirmas el borrado de {len(existing_targets)} directorio(s) en Mendieta? [s/N] "
        ).strip().lower()
        if confirm not in ("s", "si", "sí", "y", "yes"):
            print("Cancelado.")
            sys.exit(0)
    print()

    errors = 0
    for path, label in existing_targets:
        errors += clean_remote(path, label)

    print()
    if errors:
        print(f"ADVERTENCIA: {errors} error(es) durante la limpieza")
    else:
        print("=== Limpieza completada ===")


if __name__ == "__main__":
    main()
