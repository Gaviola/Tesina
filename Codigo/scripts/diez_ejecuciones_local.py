"""Corre en serie las semillas 45-51 de los cuatro supervisados en la GPU local (plan supervisados_diez_ejecuciones).

Mismos argumentos que scripts/toko/submit_sweep.py, sin --wandb. Se puede relanzar: saltea las corridas con sus tres
JSON de resultados y nunca sobrescribe una corrida completa. Una corrida fallida se informa y se sigue con la próxima,
para repetirla al relanzar. Se ejecuta desde Codigo/ con el entorno C:\\Users\\Facu\\.venvs\\dermvlm_toko.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

CONFIGS = [("swin_tiny", "t06", "7.50e-05", "0.1", "6"), ("convnext_tiny", "t02", "3.00e-05", "0.05", "9"),
           ("vit", "t06", "7.50e-05", "0.1", "6"), ("densenet", "t02", "3.00e-05", "0.05", "9")]
SEMILLAS = range(45, 52)
RES = Path("outputs/results")
LOGS = Path("outputs/logs/local_rtx4070")
LOGS.mkdir(parents=True, exist_ok=True)
env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf8", "WANDB_MODE": "disabled"}


def completa(run):
    return all((RES / f"{run}_{s}.json").exists() for s in ("test_results", "predictions", "val_predictions"))


fallidas = []
inicio = time.time()
for semilla in SEMILLAS:
    for modelo, trial, lr, wd, m in CONFIGS:
        run = f"{modelo}_sweep_{trial}_les_cwnone_s{semilla}"
        if completa(run):
            print(f"[saltea] {run}", flush=True)
            continue
        t0 = time.time()
        cmd = [sys.executable, "scripts/train_classifier.py", "--model", modelo, "--recipe", "modern", "--run-name", run,
               "--lr", lr, "--weight-decay", wd, "--randaugment-m", m, "--focal-gamma", "0", "--seed", str(semilla),
               "--class-weights", "none", "--splits-file", "data/splits/ham10000_splits_lesion.json",
               "--eval-best-checkpoint", "--save-val-predictions", "--no-freeze-backbone"]
        with open(LOGS / f"{run}.log", "w", encoding="utf8") as log:
            log.write(f"inicio {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log.flush()
            codigo = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, env=env).returncode
            log.write(f"\nfin {time.strftime('%Y-%m-%d %H:%M:%S')} codigo {codigo}\n")
        ok = codigo == 0 and completa(run)
        if not ok:
            fallidas.append(run)
        print(f"[{'ok' if ok else 'FALLA'}] {run} {(time.time() - t0) / 60:.1f} min", flush=True)

print(f"Total {(time.time() - inicio) / 3600:.2f} h. Fallidas: {fallidas or 'ninguna'}", flush=True)
sys.exit(1 if fallidas else 0)
