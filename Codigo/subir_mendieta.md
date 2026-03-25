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

Subir datos MM-SkinQA + HAM10000 (necesarios para stage1, clasificacion y generacion):
```
python scripts/mendieta_sync_data.py            # si los datos estan locales
python scripts/mendieta_sync_data.py --remote   # descargar MM-SkinQA directamente en Mendieta
python scripts/mendieta_sync_data.py --all      # todos los datasets procesados
python scripts/mendieta_sync_data.py --files <path> # subir archivos o dirs individuales 

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
python scripts/mendieta_submit.py all        # todos los jobs
python scripts/mendieta_submit.py all_s1     # solo stage1 (mini + llava)
python scripts/mendieta_submit.py all_s2     # solo stage2 (mini + llava)  (Sincronizar parametros depues con `wandb sync <run_dir>`)
python scripts/mendieta_submit.py mini_s1    # solo mini_vlm stage1  (~8GB)
python scripts/mendieta_submit.py llava_s1   # solo llava_med stage1 (~14GB LoRA)
python scripts/mendieta_submit.py mini_s2    # solo mini_vlm stage2  (~8GB)
python scripts/mendieta_submit.py llava_s2   # solo llava_med stage2 (~14GB LoRA)
python scripts/mendieta_submit.py classifier # DenseNet + ViT baselines
```

### 2b. Generacion de reportes y clasificacion VLM

```
python scripts/mendieta_submit.py gen_llava        # reportes LLaVA-Med (~12h) 1145773
python scripts/mendieta_submit.py gen_mini         # reportes Mini-VLM (~8h) 1145774
python scripts/mendieta_submit.py all_gen          # ambos modelos
python scripts/mendieta_submit.py classify_llava   # clasificacion zero-shot LLaVA-Med (~4h) 1145779
python scripts/mendieta_submit.py classify_mini    # clasificacion zero-shot Mini-VLM (~4h) 1145780
python scripts/mendieta_submit.py all_classify     # ambos modelos
```

Los jobs de generacion crean reportes sobre MM-SkinQA (Nivel 1, con referencias) y HAM10000
(Nivel 2, NER). Los reportes se guardan en `outputs/generated_reports/{modelo}/{dataset}/`.

## 3. Monitorear

mini_s1: 1145719, llava_s1: 1145720
mini_s2: 1145740, llava_s2: 1145741

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
python scripts/mendieta_sync_down.py --reports      # reportes generados
python scripts/mendieta_sync_down.py --all          # todo (metricas + checkpoints + reportes + logs)
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
