# Flujo completo: entrenar en TOKO desde Windows

## 0. Una sola vez — configurar entorno en TOKO
```
python scripts/toko_setup.py
```
Configura clave SSH (para no ingresar contraseña), crea directorios,
instala Miniconda, entorno `dermvlm` y PyTorch cu126 (RTX 4080, Ada Lovelace, CUDA 12.6).

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

## 1.5 Verificar localmente antes de enviar (dry-run)

Antes de encolar jobs, validar que el pipeline funciona correctamente con un dry-run local.
Esto ejecuta el código real pero limitado a pocos batches, verificando: carga del modelo,
datos, forward/backward, VRAM y tiempos estimados.

```
# Stage 1
python scripts/train_vlm_stage1.py --model mini_vlm --dry-run --dry-run-batches 50
python scripts/train_vlm_stage1.py --model llava_med --batch_size 4 --dry-run

# Stage 2 (si hay checkpoint de Stage 1)
python scripts/train_vlm_stage2.py --model llava_med --checkpoint outputs/checkpoints/stage1_llava_med/best_model.pt --dry-run
```

Si el dry-run falla, corregir el error antes de enviar al cluster.
Si pasa exitosamente, muestra un resumen con VRAM pico, tiempos estimados y estado.

---

## 2. Enviar jobs

```
python scripts/toko_submit.py all     # encola mini_vlm y llava_med stage1
python scripts/toko_submit.py mini    # solo mini_vlm  (~8GB,  8-16h)
python scripts/toko_submit.py llava   # solo llava_med (~10GB QLoRA, 24-48h)
```

encolados: 93312 (mini), 93313 (llava)

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
