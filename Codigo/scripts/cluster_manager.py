"""
cluster_manager.py — Menú interactivo para gestión de clusters TOKO y Mendieta.
Ejecutar desde Codigo/: python scripts/cluster_manager.py
"""

import os
import re
import subprocess
import sys
from datetime import datetime


# ─────────────────────────────────────────────
# Helpers de UI
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header(cluster=None):
    print("=" * 55)
    title = "GESTOR DE CLUSTERS"
    if cluster:
        title += f" — {cluster.upper()}"
    print(f"  {title}")
    print("=" * 55)


def menu(options, back_label="Volver"):
    """
    Muestra un menú numerado. Retorna el índice 0-based de la opción elegida,
    o None si el usuario elige volver/salir.
    """
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    print(f"  0. {back_label}")
    print()
    while True:
        raw = input("Elegir opción: ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print(f"  Opción inválida. Ingresá un número entre 0 y {len(options)}.")


def ask(prompt, default=None):
    """Pide un valor al usuario, mostrando el default entre corchetes."""
    if default is not None:
        display = f"{prompt} [{default}]: "
    else:
        display = f"{prompt}: "
    raw = input(display).strip()
    if raw == "" and default is not None:
        return default
    return raw


def confirm(summary_lines):
    """Muestra resumen y pide confirmación. Retorna True si el usuario confirma."""
    print()
    print("── Resumen del comando ──────────────────────────")
    for line in summary_lines:
        print(f"  {line}")
    print("─────────────────────────────────────────────────")
    ans = input("¿Ejecutar? [S/n]: ").strip().lower()
    return ans in ("", "s", "si", "sí", "y", "yes")


def run(cmd, log_submit=False, cluster=None, job_label=None):
    """Ejecuta un comando mostrando output en tiempo real.

    Si log_submit=True, captura la salida para extraer el Job ID y lo registra
    en outputs/jobs_log.txt junto con el cluster y la fecha.
    """
    print()
    print(f"▶ {' '.join(cmd)}")
    print("─" * 55)

    if log_submit:
        import threading

        output_lines = []

        proc = subprocess.Popen(
            cmd, cwd=_cwd(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )

        def stream():
            for raw_line in proc.stdout:
                line = raw_line.decode("utf-8", errors="replace")
                print(line, end="", flush=True)
                output_lines.append(line)

        t = threading.Thread(target=stream)
        t.start()
        t.join()  # esperar a que se lea todo el output antes de wait()
        proc.wait()
        returncode = proc.returncode
        full_output = "".join(output_lines)
        _log_submitted_job(full_output, cluster, job_label)
    else:
        result = subprocess.run(cmd, cwd=_cwd())
        returncode = result.returncode

    print("─" * 55)
    if returncode != 0:
        print(f"  [!] El comando finalizó con código {returncode}.")
    input("\nPresioná Enter para continuar...")


def _log_submitted_job(output, cluster, job_label):
    """Extrae Job IDs del output del submit y los escribe en outputs/jobs_log.txt.

    Patrones soportados:
      - SLURM directo:  "Submitted batch job 12345"
      - Sweep scripts:  "-> JOBID: 12345"
    """
    # Buscar solo en patrones conocidos — sin fallbacks agresivos
    raw_ids = re.findall(
        r"(?:Submitted batch job|JOBID\s*:)\s*(\d+)",
        output,
        re.IGNORECASE,
    )

    # Deduplicar manteniendo orden de aparición
    seen = set()
    job_ids = []
    for jid in raw_ids:
        if jid not in seen:
            seen.add(jid)
            job_ids.append(jid)

    if not job_ids:
        print("  [!] No se pudo extraer el Job ID del output para registrarlo.")
        print("      Revisá el output del comando para obtener el ID manualmente.")
        return

    log_path = os.path.join(_cwd(), "outputs", "jobs_log.txt")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        for job_id in job_ids:
            line = f"{timestamp} | cluster={cluster.upper():<9} | job_id={job_id:<10} | {job_label}"
            f.write(line + "\n")
            print(f"  -> Job registrado: {line}")


def _cwd():
    """Retorna la ruta a Codigo/ (directorio de trabajo esperado)."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)  # scripts/../  → Codigo/


# ─────────────────────────────────────────────
# Comandos por categoría
# ─────────────────────────────────────────────

def make_cmd(cluster, *parts):
    """Construye [sys.executable, 'scripts/<cluster>/<script>.py', ...args]."""
    return [sys.executable, f"scripts/{cluster}/{parts[0]}"] + list(parts[1:])


# ── SETUP / SYNC UP ──────────────────────────

def flow_setup(cluster):
    options = [
        "Configurar entorno (setup.py)",
        "Subir código y dependencias (sync_up.py --install-deps)",
        "Subir código sin instalar deps (sync_up.py)",
        "Subir datos MM-SkinQA + HAM10000",
        "Descargar modelos HuggingFace en el cluster (solo Mendieta)",
    ]
    while True:
        print()
        header(cluster)
        print("  SETUP / SUBIR ARCHIVOS\n")
        choice = menu(options)
        if choice is None:
            return

        if choice == 0:
            # setup — siempre tiene submenú, se confirma antes de ejecutar
            if cluster == "mendieta":
                print("\n  Opciones de setup:")
                sub = menu(["Setup completo", "Solo generar clave SSH (--setup-ssh-key)"])
                if sub is None:
                    continue
                cmd = make_cmd(cluster, "setup.py") if sub == 0 else make_cmd(cluster, "setup.py", "--setup-ssh-key")
            else:
                sub = menu(["Setup completo", "Saltar configuración SSH (--skip-ssh-key)"])
                if sub is None:
                    continue
                cmd = make_cmd(cluster, "setup.py") if sub == 0 else make_cmd(cluster, "setup.py", "--skip-ssh-key")
            run(cmd)

        elif choice == 1:
            # sync_up con --install-deps: sin parámetros adicionales, ejecutar directo
            run(make_cmd(cluster, "sync_up.py", "--install-deps"))

        elif choice == 2:
            run(make_cmd(cluster, "sync_up.py"))

        elif choice == 3:
            print("\n  Modo de subida de datos:")
            sub = menu([
                "Datos locales (sync_data.py)",
                "Descargar MM-SkinQA directo en cluster (--remote)",
                "Todos los datasets procesados (--all)",
            ])
            if sub is None:
                continue
            if sub == 0:
                run(make_cmd(cluster, "sync_data.py"))
            elif sub == 1:
                run(make_cmd(cluster, "sync_data.py", "--remote"))
            else:
                run(make_cmd(cluster, "sync_data.py", "--all"))

        elif choice == 4:
            if cluster != "mendieta":
                print("\n  [!] Esta opción solo está disponible para Mendieta.")
                input("  Enter para continuar...")
                continue
            print("\n  Modelos a descargar:")
            sub = menu(["Todos los modelos", "Solo Mini-VLM (--model mini)", "Solo LLaVA-Med (--model llava)"])
            if sub is None:
                continue
            if sub == 0:
                run(make_cmd(cluster, "download_models.py"))
            elif sub == 1:
                run(make_cmd(cluster, "download_models.py", "--model", "mini"))
            else:
                run(make_cmd(cluster, "download_models.py", "--model", "llava"))


# ── ENVIAR JOBS ──────────────────────────────

SUBMIT_OPTIONS_MENDIETA = [
    ("Todos los jobs",                    ["all"]),
    ("Solo Stage 1 (mini + llava)",       ["all_s1"]),
    ("Solo Stage 2 (mini + llava)",       ["all_s2"]),
    ("Mini-VLM Stage 1",                  ["mini_s1"]),
    ("LLaVA-Med Stage 1",                 ["llava_s1"]),
    ("Mini-VLM Stage 2",                  ["mini_s2"]),
    ("LLaVA-Med Stage 2",                 ["llava_s2"]),
    ("Clasificadores baseline (DenseNet + ViT)", ["classifier"]),
    ("Reportes LLaVA-Med",                ["gen_llava"]),
    ("Reportes Mini-VLM",                 ["gen_mini"]),
    ("Reportes MM-SkinQA ambos modelos",  ["all_gen_mmskin"]),
    ("Reportes HAM10000 ambos modelos",   ["all_gen_ham"]),
    ("Reportes ambos modelos",            ["all_gen"]),
    ("Clasificación zero-shot LLaVA-Med", ["classify_llava"]),
    ("Clasificación zero-shot Mini-VLM",  ["classify_mini"]),
    ("Clasificación zero-shot ambos",     ["all_classify"]),
    ("Clasificación Mini-VLM fine-tuned", ["classify_mini_ft"]),
    ("Clasificación LLaVA-Med fine-tuned",["classify_llava_ft"]),
    ("Clasificación fine-tuned ambos",    ["all_classify_ft"]),
]

SUBMIT_OPTIONS_TOKO = [
    ("Todos los jobs (mini + llava stage1)",         ["all"]),
    ("Solo Mini-VLM",                                ["mini"]),
    ("Solo LLaVA-Med",                               ["llava"]),
    ("Reportes LLaVA-Med",                           ["gen_llava"]),
    ("Reportes Mini-VLM",                            ["gen_mini"]),
    ("Reportes ambos modelos",                       ["all_gen"]),
    ("Clasificación zero-shot LLaVA-Med",            ["classify_llava"]),
    ("Clasificación zero-shot Mini-VLM",             ["classify_mini"]),
    ("Clasificación zero-shot ambos",                ["all_classify"]),
]

SWEEP_PHASES = ["Fase 1 (clasificadores: DenseNet / ViT)", "Fase 2 (VLMs con LoRA)"]
SWEEP_MODELS_P1 = ["Ambos modelos", "Solo DenseNet", "Solo ViT"]
SWEEP_MODELS_P2 = ["Ambos modelos", "Solo Mini-VLM", "Solo LLaVA-Med"]


def flow_submit(cluster):
    top_options = ["Enviar job SLURM", "Sweep de hiperparámetros", "Dry-run local (verificar antes de enviar)"]
    while True:
        print()
        header(cluster)
        print("  ENVIAR JOBS\n")
        top = menu(top_options)
        if top is None:
            return

        # ── Job directo ──────────────────────
        if top == 0:
            opts = SUBMIT_OPTIONS_MENDIETA if cluster == "mendieta" else SUBMIT_OPTIONS_TOKO
            labels = [o[0] for o in opts]
            print()
            choice = menu(labels)
            if choice is None:
                continue
            label, args = opts[choice]
            cmd = make_cmd(cluster, "submit.py", *args)
            # Confirmación siempre antes de enviar un job al cluster
            if confirm([f"Cluster: {cluster.upper()}", f"Job: {label}", f"Comando: {' '.join(cmd)}"]):
                run(cmd, log_submit=True, cluster=cluster, job_label=label)

        # ── Sweep ────────────────────────────
        elif top == 1:
            print()
            phase_choice = menu(SWEEP_PHASES)
            if phase_choice is None:
                continue

            if phase_choice == 0:
                # Fase 1
                print()
                model_choice = menu(SWEEP_MODELS_P1)
                if model_choice is None:
                    continue
                n_trials = ask("Número de trials", "20")
                seed     = ask("Semilla aleatoria", "42")
                dry_run  = ask("Solo preview sin enviar (dry-run)? [s/N]", "N").lower() in ("s", "si", "sí", "y")

                cmd = [sys.executable, "scripts/sweep_phase1.py", "--cluster", cluster, "--n-trials", n_trials, "--seed", seed]
                if model_choice == 1:
                    cmd += ["--model", "densenet"]
                elif model_choice == 2:
                    cmd += ["--model", "vit"]
                if dry_run:
                    cmd.append("--dry-run")

                label = f"sweep_phase1 {SWEEP_MODELS_P1[model_choice]}"
                summary = [f"Cluster: {cluster.upper()}", f"Trials: {n_trials}", f"Semilla: {seed}", f"Dry-run: {dry_run}", f"Modelo: {SWEEP_MODELS_P1[model_choice]}"]
                if confirm(summary):
                    run(cmd, log_submit=not dry_run, cluster=cluster, job_label=label)

            else:
                # Fase 2
                print()
                model_choice = menu(SWEEP_MODELS_P2)
                if model_choice is None:
                    continue
                n_trials = ask("Número de trials", "12")
                offset   = ask("Offset (retomar desde trial N)", "0")
                seed     = ask("Semilla aleatoria", "42")

                cmd = [sys.executable, "scripts/sweep_phase2.py", "--cluster", cluster, "--n-trials", n_trials, "--seed", seed]
                if model_choice == 1:
                    cmd += ["--model", "mini_vlm"]
                elif model_choice == 2:
                    cmd += ["--model", "llava_med"]
                if offset != "0":
                    cmd += ["--offset", offset]

                label = f"sweep_phase2 {SWEEP_MODELS_P2[model_choice]}"
                summary = [f"Cluster: {cluster.upper()}", f"Trials: {n_trials}", f"Offset: {offset}", f"Modelo: {SWEEP_MODELS_P2[model_choice]}"]
                if confirm(summary):
                    run(cmd, log_submit=True, cluster=cluster, job_label=label)

        # ── Dry-run ──────────────────────────
        elif top == 2:
            dry_options = [
                "Stage 1 — Mini-VLM",
                "Stage 1 — LLaVA-Med",
                "Stage 2 — LLaVA-Med",
                "Clasificación zero-shot — Mini-VLM",
                "Clasificación zero-shot — LLaVA-Med",
            ]
            print()
            dry_choice = menu(dry_options)
            if dry_choice is None:
                continue

            if dry_choice == 0:
                batches = ask("Batches de dry-run", "50")
                cmd = [sys.executable, "scripts/train_vlm_stage1.py", "--model", "mini_vlm", "--dry-run", "--dry-run-batches", batches]
            elif dry_choice == 1:
                bs = ask("Batch size", "4")
                cmd = [sys.executable, "scripts/train_vlm_stage1.py", "--model", "llava_med", "--batch_size", bs, "--dry-run"]
            elif dry_choice == 2:
                ckpt = ask("Path al checkpoint Stage 1", "outputs/checkpoints/stage1_llava_med/best_model.pt")
                cmd = [sys.executable, "scripts/train_vlm_stage2.py", "--model", "llava_med", "--checkpoint", ckpt, "--dry-run"]
            elif dry_choice == 3:
                cmd = [sys.executable, "scripts/train_vlm_classify.py", "--model", "mini_vlm", "--dry-run"]
            else:
                batches = ask("Batches de dry-run", "20")
                cmd = [sys.executable, "scripts/train_vlm_classify.py", "--model", "llava_med", "--dry-run", "--dry-run-batches", batches]

            # Dry-runs con parámetros: confirmar
            if confirm([f"Comando: {' '.join(cmd)}"]):
                run(cmd)


# ── MONITOREAR ───────────────────────────────

def flow_monitor(cluster):
    options = [
        "Ver cola de jobs",
        "Ver log de un job en tiempo real",
        "Ver estado del cluster (sinfo)",
        "Cancelar un job",
        "Eficiencia post-job (solo Mendieta)",
    ]
    while True:
        print()
        header(cluster)
        print("  MONITOREAR\n")
        choice = menu(options)
        if choice is None:
            return

        if choice == 0:
            # Sin parámetros: ejecutar directo
            run(make_cmd(cluster, "monitor.py"))

        elif choice == 1:
            job_id = ask("Job ID")
            if not job_id:
                print("  [!] Debés ingresar un Job ID.")
                input("  Enter para continuar...")
                continue
            print(f"  Siguiendo log del job {job_id} en tiempo real (Ctrl+C para detener)...")
            run(make_cmd(cluster, "monitor.py", job_id))

        elif choice == 2:
            # Sin parámetros: ejecutar directo
            run(make_cmd(cluster, "monitor.py", "status"))

        elif choice == 3:
            job_id = ask("Job ID a cancelar")
            if not job_id:
                print("  [!] Debés ingresar un Job ID.")
                input("  Enter para continuar...")
                continue
            # Cancelar job: confirmar por ser destructivo
            if confirm([f"[!] Se cancelará el job {job_id} en {cluster.upper()}"]):
                run(make_cmd(cluster, "monitor.py", "cancel", job_id))

        elif choice == 4:
            if cluster != "mendieta":
                print("\n  [!] Esta opción solo está disponible para Mendieta.")
                input("  Enter para continuar...")
                continue
            job_id = ask("Job ID")
            if not job_id:
                print("  [!] Debés ingresar un Job ID.")
                input("  Enter para continuar...")
                continue
            run(make_cmd(cluster, "monitor.py", "seff", job_id))


# ── DESCARGAR DATOS ───────────────────────────

def flow_sync_down(cluster):
    options = [
        "Métricas JSON (rápido, default)",
        "Checkpoints (modelos .pt, varios GB)",
        "Reportes generados",
        "Todo (métricas + checkpoints + reportes + logs)",
        "Log de un job específico",
        "Logs de un rango de jobs",
        "Sincronizar runs wandb offline → servidor",
    ]
    while True:
        print()
        header(cluster)
        print("  DESCARGAR DATOS\n")
        choice = menu(options)
        if choice is None:
            return

        if choice == 0:
            # Sin parámetros del usuario: ejecutar directo
            run(make_cmd(cluster, "sync_down.py"))

        elif choice == 1:
            # Sin parámetros del usuario, pero puede ser pesado — informar y ejecutar
            print("\n  Descargando checkpoints .pt (puede ser varios GB)...")
            run(make_cmd(cluster, "sync_down.py", "--checkpoints"))

        elif choice == 2:
            run(make_cmd(cluster, "sync_down.py", "--reports"))

        elif choice == 3:
            print("\n  Descargando todo incluyendo outputs/wandb/ (puede ser muy pesado)...")
            run(make_cmd(cluster, "sync_down.py", "--all"))

        elif choice == 4:
            job_id = ask("Job ID")
            if not job_id:
                print("  [!] Debés ingresar un Job ID.")
                input("  Enter para continuar...")
                continue
            run(make_cmd(cluster, "sync_down.py", "--logs", job_id))

        elif choice == 5:
            job_from = ask("Job ID inicio del rango")
            job_to   = ask("Job ID fin del rango")
            if not job_from or not job_to:
                print("  [!] Debés ingresar ambos IDs.")
                input("  Enter para continuar...")
                continue
            run(make_cmd(cluster, "sync_down.py", "--logs", job_from, job_to))

        elif choice == 6:
            print("\n  Primero descargá los runs con 'sync_down.py --all', luego se ejecutará:")
            print("  wandb sync Codigo/outputs/wandb/")
            ans = input("\n  ¿Ya bajaste los runs? Ejecutar wandb sync ahora? [s/N]: ").strip().lower()
            if ans in ("s", "si", "sí", "y"):
                run(["wandb", "sync", "outputs/wandb/"])


# ─────────────────────────────────────────────
# Flujo principal
# ─────────────────────────────────────────────

CLUSTER_OPTIONS = ["Mendieta (A30 24GB, Ampere)", "TOKO (RTX 4080 16GB, Ada Lovelace)"]
CLUSTER_KEYS    = ["mendieta", "toko"]

CATEGORY_OPTIONS = [
    "Enviar jobs al cluster",
    "Setup / subir archivos al cluster",
    "Descargar datos del cluster",
    "Monitorear estado del cluster",
]


def main():
    # Verificar que corremos desde Codigo/
    cwd = os.getcwd()
    expected = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    if os.path.normpath(cwd) != expected:
        print(f"\n[!] Ejecutá este script desde Codigo/")
        print(f"    cd \"{expected}\"")
        print(f"    python scripts/cluster_manager.py\n")
        sys.exit(1)

    cluster = None

    while True:
        clear()
        header(cluster)
        print()

        # ── Elegir cluster ───────────────────
        if cluster is None:
            print("  SELECCIONAR CLUSTER\n")
            choice = menu(CLUSTER_OPTIONS, back_label="Salir")
            if choice is None:
                print("\n  Hasta luego.\n")
                sys.exit(0)
            cluster = CLUSTER_KEYS[choice]
            continue

        # ── Categoría ────────────────────────
        print("  CATEGORÍA\n")
        cat = menu(CATEGORY_OPTIONS, back_label="Cambiar cluster")
        if cat is None:
            cluster = None
            continue

        if cat == 0:
            flow_submit(cluster)
        elif cat == 1:
            flow_setup(cluster)
        elif cat == 2:
            flow_sync_down(cluster)
        elif cat == 3:
            flow_monitor(cluster)


if __name__ == "__main__":
    main()
