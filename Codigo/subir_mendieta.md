# Flujo completo: entrenar en Mendieta desde Windows

## 0. Una sola vez — configurar SSH + entorno en Mendieta

### 0a. Clave SSH (solo si no conectas desde Windows)

Mendieta requiere claves **ed25519**. Si la clave SSH fue generada en MobaXterm
y no podes conectar desde Windows nativo (PowerShell/CMD), ejecuta:
```
python scripts/mendieta_setup.py --setup-ssh-key
```
Esto genera `~/.ssh/id_ed25519` en Windows. Si no puede registrar la clave
automaticamente, mostrara instrucciones para hacerlo desde MobaXterm.

Verificar manualmente:
```
ssh -i ~/.ssh/id_ed25519 fgaviola@mendieta.ccad.unc.edu.ar hostname
```

### 0b. Setup del entorno
```
python scripts/mendieta_setup.py
```
Verifica conexion SSH, crea directorios, muestra particiones (sinfo), instala Miniconda,
entorno `dermvlm` y PyTorch cu121 (A30 24GB, Ampere, CUDA 12.1).

---

## 1. Subir codigo y datos

```
python scripts/mendieta_sync_up.py --install-deps
```
Sube src/, scripts/, configs/, slurm/ e instala requirements.txt en Mendieta.

Subir datos MM-SkinQA (necesario para stage1):
```
python scripts/mendieta_sync_data.py            # si los datos estan locales
python scripts/mendieta_sync_data.py --remote   # descargar directamente en Mendieta
```

---

## 1.5 Pre-descargar modelos de HuggingFace

Los nodos de computo de Mendieta **no tienen acceso a internet**. Los modelos deben
estar en el cache de HuggingFace antes de enviar jobs:
```
python scripts/mendieta_download_models.py              # descarga todos
python scripts/mendieta_download_models.py --model mini  # solo Mini-VLM
python scripts/mendieta_download_models.py --model llava # solo LLaVA-Med
```

Esto ejecuta `huggingface_hub.snapshot_download()` en el **nodo de login** (que si tiene
internet) y guarda los modelos en `~/.cache/huggingface/hub/`. Los scripts SLURM ya
configuran `HF_HUB_OFFLINE=1` para que los compute nodes los carguen desde cache.

---

## 1.6 Verificar localmente antes de enviar (dry-run)

Antes de encolar jobs, validar que el pipeline funciona correctamente con un dry-run local.
Esto ejecuta el codigo real pero limitado a pocos batches, verificando: carga del modelo,
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
python scripts/mendieta_submit.py all        # todos los jobs
python scripts/mendieta_submit.py all_s1     # solo stage1 (mini + llava)
python scripts/mendieta_submit.py all_s2     # solo stage2 (mini + llava)
python scripts/mendieta_submit.py mini_s1    # solo mini_vlm stage1  (~8GB)
python scripts/mendieta_submit.py llava_s1   # solo llava_med stage1 (~14GB LoRA)
python scripts/mendieta_submit.py mini_s2    # solo mini_vlm stage2  (~8GB)
python scripts/mendieta_submit.py llava_s2   # solo llava_med stage2 (~14GB LoRA)
python scripts/mendieta_submit.py classifier # DenseNet + ViT baselines
```

## 3. Monitorear

mini_s1: 1145717, llava_s1: 1145718

```
python scripts/mendieta_monitor.py              # ver cola de jobs
python scripts/mendieta_monitor.py <JOBID>      # ver log en tiempo real (tail -f)
python scripts/mendieta_monitor.py status       # ver estado del cluster (sinfo)
python scripts/mendieta_monitor.py cancel <ID>  # cancelar un job
python scripts/mendieta_monitor.py seff <ID>    # eficiencia post-job (CPU/mem)
```

---

## 4. Bajar resultados

```
python scripts/mendieta_sync_down.py              # metricas JSON (rapido, default)
python scripts/mendieta_sync_down.py --checkpoints  # modelos .pt (varios GB)
python scripts/mendieta_sync_down.py --all          # todo
```

Los resultados se guardan en `Codigo/outputs/`.
Metricas en: `outputs/results/stage1_mini_vlm_metrics.json` y `stage1_llava_med_metrics.json`.

---

## Diferencias con TOKO

| Aspecto | TOKO | Mendieta |
|---------|------|----------|
| GPU | RTX 4080 16GB (Ada) | A30 24GB (Ampere) |
| CUDA PyTorch | cu126 | cu121 |
| Base remota | `~/scratch/dermvlm/` | `~/dermvlm/` (home NFS) |
| Particion | `gpu` + `--exclusive` | `gpu` + `--gres=gpu:1` |
| CPUs por job | 8 | 10 |
| Scratch | `~/scratch/` (persistente) | `/scratch/` (local, borrado al terminar) |
| Modulos | No usa | `module load cuda` |
