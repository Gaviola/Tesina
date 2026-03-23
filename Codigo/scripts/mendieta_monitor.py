"""
mendieta_monitor.py — Monitorea jobs en Mendieta y muestra logs en tiempo real.

Uso:
  python scripts/mendieta_monitor.py              # muestra la cola del usuario
  python scripts/mendieta_monitor.py <JOBID>      # tail -f del log del job
  python scripts/mendieta_monitor.py status       # sinfo del cluster
  python scripts/mendieta_monitor.py cancel <ID>  # cancela un job
  python scripts/mendieta_monitor.py seff <ID>    # eficiencia post-job (CPU/mem)
"""
import sys
import subprocess
import argparse
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.mendieta_config import MENDIETA_USER, MENDIETA_HOST, REMOTE_BASE, REMOTE_LOGS, check_tools, ssh

POLL_INTERVAL = 10  # segundos entre refreshes en modo tail


def show_queue():
    print(f"=== Cola de jobs ({MENDIETA_USER}@{MENDIETA_HOST}) ===")
    ssh(f"squeue -u {MENDIETA_USER} --format='%.10i %.18j %.8T %.10M %.6D %R'")
    print()
    print("--- Espacio en home ---")
    ssh(f"du -sh /home/{MENDIETA_USER}/dermvlm/outputs/ 2>/dev/null || echo 'outputs/ vacio'")


def show_status():
    print("=== Estado del cluster Mendieta ===")
    ssh("sinfo")
    print()
    print("--- Tiempo estimado de inicio ---")
    ssh(f"squeue -u {MENDIETA_USER} --start 2>/dev/null || squeue -u {MENDIETA_USER}")


def tail_log(jobid: str):
    log_out = f"{REMOTE_LOGS}/{jobid}.out"
    log_err = f"{REMOTE_LOGS}/{jobid}.err"

    # Verificar estado del job
    result = ssh(f"squeue -j {jobid} -h -o '%T' 2>/dev/null || echo 'DONE'", capture=True)
    status = result.stdout.strip() or "DONE"

    print(f"=== Log del job {jobid} — estado: {status} ===")
    print(f"Archivo: {log_out}")
    print()

    if status in ("RUNNING", "R", "COMPLETING"):
        print("[Job en ejecucion — mostrando en tiempo real. Ctrl+C para salir]")
        print()
        try:
            # SSH con tail -f (streaming en tiempo real)
            subprocess.run(
                ["ssh", f"{MENDIETA_USER}@{MENDIETA_HOST}", f"tail -f {log_out}"]
            )
        except KeyboardInterrupt:
            print("\n[Monitoreo interrumpido]")
    else:
        # Job terminado o pendiente: mostrar log completo
        print("[Job no esta corriendo — mostrando log completo]")
        ssh(f"cat {log_out} 2>/dev/null || echo '(log no disponible aun)'")
        print()
        print("--- Errores (stderr) ---")
        ssh(f"cat {log_err} 2>/dev/null || echo '(sin errores registrados)'")


def cancel_job(jobid: str):
    print(f"Cancelando job {jobid}...")
    result = ssh(f"scancel {jobid}", capture=True)
    if result.returncode == 0:
        print(f"OK: job {jobid} cancelado")
    else:
        print(f"ERROR: {result.stderr.strip()}")


def show_efficiency(jobid: str):
    """Muestra eficiencia post-job con seff (CPU, memoria, tiempo)."""
    print(f"=== Eficiencia del job {jobid} ===")
    ssh(f"seff {jobid}")


def main():
    parser = argparse.ArgumentParser(description="Monitorea jobs en Mendieta")
    parser.add_argument("action", nargs="?", default="",
                        help="JOBID, 'status', 'cancel <JOBID>', o 'seff <JOBID>'")
    parser.add_argument("jobid_for_action", nargs="?",
                        help="JOBID al usar 'cancel' o 'seff'")
    args = parser.parse_args()

    check_tools()

    action = args.action

    if not action:
        show_queue()
    elif action == "status":
        show_status()
    elif action == "cancel":
        if not args.jobid_for_action:
            print("Uso: python scripts/mendieta_monitor.py cancel <JOBID>")
            sys.exit(1)
        cancel_job(args.jobid_for_action)
    elif action == "seff":
        if not args.jobid_for_action:
            print("Uso: python scripts/mendieta_monitor.py seff <JOBID>")
            sys.exit(1)
        show_efficiency(args.jobid_for_action)
    elif action.isdigit():
        tail_log(action)
    else:
        print(f"Argumento no reconocido: '{action}'")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
