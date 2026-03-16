# Flujo completo: entrenar en TOKO desde Windows

## 0. Una sola vez — configurar entorno en TOKO
```
python scripts/toko_setup.py
```
Configura clave SSH (para no ingresar contraseña), crea directorios,
instala Miniconda, entorno `dermvlm` y PyTorch cu118 (compatible Pascal Titan Xp).

Si la clave SSH ya esta configurada:
```
python scripts/toko_setup.py --skip-ssh-key
```

---

## 1. Subir código y datos

```
python scripts/toko_sync_up.py --install-deps
```
Sube src/, scripts/, configs/, slurm/ e instala requirements.txt en TOKO.

Subir datos MM-SkinQA (necesario para stage1):
```
python scripts/toko_sync_data.py            # si los datos estan locales
python scripts/toko_sync_data.py --remote   # descargar directamente en TOKO
```

---

## 2. Enviar jobs

```
python scripts/toko_submit.py all     # encola mini_vlm y llava_med stage1
python scripts/toko_submit.py mini    # solo mini_vlm  (~8GB,  8-16h)
python scripts/toko_submit.py llava   # solo llava_med (~10GB QLoRA, 24-48h)
```

---

=== Enviando jobs a TOKO (target: mini) ===

--- Enviando: mini ---
  Submitted batch job 93045
  JOBID:    93045
  Log:      /home/fgaviola/scratch/dermvlm/logs/93045.out
  Monitor:  python scripts/toko_monitor.py 93045

=== Jobs encolados ===
Ver cola:  python scripts/toko_monitor.py
Ver log:   python scripts/toko_monitor.py 93045

## 3. Monitorear

```
python scripts/toko_monitor.py              # ver cola de jobs
python scripts/toko_monitor.py <JOBID>      # ver log en tiempo real (tail -f)
python scripts/toko_monitor.py status       # ver estado del cluster (sinfo)
python scripts/toko_monitor.py cancel <ID>  # cancelar un job
```

---

## 4. Bajar resultados

```
python scripts/toko_sync_down.py              # metricas JSON (rapido, default)
python scripts/toko_sync_down.py --checkpoints  # modelos .pt (varios GB)
python scripts/toko_sync_down.py --all          # todo
```

Los resultados se guardan en `Codigo/outputs/`.
Metricas en: `outputs/results/stage1_mini_vlm_metrics.json` y `stage1_llava_med_metrics.json`.
