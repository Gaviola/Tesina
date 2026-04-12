
USAR: python scripts/cluster_manager.py

# Flujo completo: entrenar en TOKO desde Windows

## 0. Una sola vez — configurar entorno en TOKO
```
python scripts/toko/setup.py
```
Configura clave SSH (para no ingresar contraseña), crea directorios,
instala Miniconda, entorno `dermvlm` y PyTorch cu126 (RTX 4080, Ada Lovelace, CUDA 12.6).

Si la clave SSH ya esta configurada:
```
python scripts/toko/setup.py --skip-ssh-key
```

---

## 1. Subir código y datos

```
python scripts/toko/sync_up.py --install-deps
```
Sube src/, scripts/, configs/, slurm/ e instala requirements.txt en TOKO.

Subir datos MM-SkinQA + HAM10000 (necesarios para stage1, clasificacion y generacion):
```
python scripts/toko/sync_data.py            # si los datos estan locales
python scripts/toko/sync_data.py --remote   # descargar MM-SkinQA directamente en TOKO
python scripts/toko/sync_data.py --all      # todos los datasets procesados
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

### Dry-run para clasificacion VLM

Verificar que la clasificacion zero-shot funciona correctamente antes de enviar al cluster.
Esto detecta problemas como 100% UNKNOWN (respuestas no parseables):

```
python scripts/train_vlm_classify.py --model mini_vlm --dry-run
python scripts/train_vlm_classify.py --model llava_med --dry-run --dry-run-batches 20
```

El resumen muestra las primeras respuestas parseadas, % UNKNOWN, VRAM y velocidad estimada.

---

## 2. Enviar jobs

```
python scripts/toko/submit.py all     # encola mini_vlm y llava_med stage1
python scripts/toko/submit.py mini    # solo mini_vlm  (~8GB,  8-16h)
python scripts/toko/submit.py llava   # solo llava_med (~10GB QLoRA, 24-48h)
```

encolados: 93312 (mini), 93313 (llava)

### 2b. Generacion de reportes y clasificacion VLM

```
python scripts/toko/submit.py gen_llava        # reportes LLaVA-Med  93325
python scripts/toko/submit.py gen_mini         # reportes Mini-VLM   93326
python scripts/toko/submit.py all_gen          # ambos modelos
python scripts/toko/submit.py classify_llava   # clasificacion zero-shot LLaVA-Med  93327
python scripts/toko/submit.py classify_mini    # clasificacion zero-shot Mini-VLM  93328
python scripts/toko/submit.py all_classify     # ambos modelos
```

Los jobs de generacion crean reportes sobre MM-SkinQA (Nivel 1, con referencias) y HAM10000
(Nivel 2, NER). Los reportes se guardan en `outputs/generated_reports/{modelo}/{dataset}/`.

### 2c. Sweep de hiperparámetros

Lanza un job SLURM por cada combinación de parámetros. Los parámetros se muestrean aleatoriamente
desde `configs/sweeps/phase1_sweep.yaml` o `phase2_sweep.yaml`. Cada job corre con
`WANDB_MODE=offline` y guarda su run en `outputs/wandb/`. Para subir los runs a wandb
ver paso 4.

```
# Fase 1: clasificadores (DenseNet / ViT) — varía lr, wd, scheduler, freeze, etc.
python scripts/sweep_phase1.py --cluster toko --n-trials 20 --dry-run   # preview sin enviar
python scripts/sweep_phase1.py --cluster toko --n-trials 20             # lanza 20 jobs 93638-93667

# Fase 2: VLMs con LoRA — varía lora_r, lora_alpha, lr, epochs, grad_accum, etc.
python scripts/sweep_phase2.py --cluster toko --n-trials 12
python scripts/sweep_phase2.py --cluster toko --n-trials 12 --model mini_vlm  # solo un modelo  93668-93682
python scripts/sweep_phase2.py --cluster toko --n-trials 12 --offset 6        # retomar desde trial 7

# Semilla distinta → combinaciones distintas (para ampliar el sweep)
python scripts/sweep_phase1.py --cluster toko --n-trials 10 --seed 123
```

## 3. Monitorear

```
python scripts/toko/monitor.py              # ver cola de jobs
python scripts/toko/monitor.py <JOBID>      # ver log en tiempo real (tail -f)
python scripts/toko/monitor.py status       # ver estado del cluster (sinfo)
python scripts/toko/monitor.py cancel <ID>  # cancelar un job
```

---

## 4. Bajar resultados

```
python scripts/toko/sync_down.py                     # metricas JSON (rapido, default)
python scripts/toko/sync_down.py --checkpoints       # modelos .pt (varios GB)
python scripts/toko/sync_down.py --reports           # reportes generados
python scripts/toko/sync_down.py --all               # todo (metricas + checkpoints + reportes + logs)
python scripts/toko/sync_down.py --wandb             # runs offline de wandb (para subir a wandb.ai)
python scripts/toko/sync_down.py --logs 12345        # bajar solo el log del job 12345
python scripts/toko/sync_down.py --logs 12345 12350  # bajar rango [12345, 12350]
```

## 5. Limpiar outputs en el cluster

Liberar espacio en TOKO borrando lo que ya fue descargado localmente.
Siempre bajar primero con `sync_down.py` antes de limpiar.

```
python scripts/toko/clean_remote.py --dry-run        # ver que se borraria (sin borrar)
python scripts/toko/clean_remote.py --wandb          # borrar runs offline de wandb
python scripts/toko/clean_remote.py --checkpoints    # borrar checkpoints .pt (varios GB)
python scripts/toko/clean_remote.py --reports        # borrar reportes generados
python scripts/toko/clean_remote.py --results        # borrar metricas JSON
python scripts/toko/clean_remote.py --logs           # borrar logs SLURM
python scripts/toko/clean_remote.py --all            # borrar todo (outputs/ + logs/)
python scripts/toko/clean_remote.py --checkpoints -y # sin confirmacion interactiva
```

Flujo tipico post-sweep:
```
python scripts/toko/sync_down.py --wandb --checkpoints   # 1. bajar
python scripts/toko/clean_remote.py --wandb --checkpoints # 2. limpiar
```

Los resultados se guardan en `Codigo/outputs/`.
Metricas en: `outputs/results/mini_vlm/stage1_metrics.json` y `outputs/results/llava_med/stage1_metrics.json`.

### 4b. Sincronizar runs de wandb

Después de bajar los resultados, subir los runs offline al servidor de wandb.
`--all` incluye `outputs/wandb/` donde se guardaron los runs del sweep.

```
python scripts/toko/sync_down.py --wandb         # baja outputs/wandb/
wandb sync Codigo/outputs/wandb/                 # sube todos los runs offline a wandb
```
