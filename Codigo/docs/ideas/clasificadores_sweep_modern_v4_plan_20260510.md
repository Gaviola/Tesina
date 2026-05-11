# Plan: Sweep de Hiperparámetros — Clasificadores Modern v4

**Fecha:** 2026-05-10  
**Cluster:** TOKO (RTX 4080 16GB, Ada Lovelace)  
**Modelos:** ConvNeXt-Tiny, Swin-Tiny (solo modelos con LayerNorm)  
**Script de envío:** `scripts/toko/submit_sweep.py`  
**Grid:** `configs/sweeps/phase1_modern_sweep_grid.yaml`

---

## 1. Motivación

Los modelos ConvNeXt-Tiny y Swin-Tiny con recipe modern v3 llegaron a F1=0.846 y F1=0.816 en HAM10000 respectivamente, pero no se aplicó un sweep de hiperparámetros (los legacy sí tuvieron un sweep de 25+ runs en W&B). Se espera que un sweep focalizado pueda cerrar la brecha de ~1.6 pt de F1 entre ConvNeXt-Tiny v3 y ViT legacy (0.862).

DenseNet y ViT **no se incluyen** en este sweep: su incompatibilidad con BatchNorm + augmentación agresiva fue documentada en el análisis de v1–v3 y un sweep no resolvería ese problema estructural.

---

## 2. Espacio de búsqueda

| Parámetro | Rango | Justificación |
|-----------|-------|---------------|
| `lr` | [3e-5, 5e-4] log-uniforme | Palanca principal; 1e-4 (v3 default) es solo un punto del espacio |
| `weight_decay` | [0.01, 0.05, 0.10] | LayerNorm es sensible al WD; 0.05 fue el default sin exploración |
| `randaugment_m` | [6, 9, 12] | m=9 fue fijo en v3; puede ser subóptimo para ambas arquitecturas |

**Fijos para todos los trials:**
- `epochs=40`, `seed=42`, `scheduler=CosineAnnealingLR`
- `--focal-gamma 0` (CE + class weights, sin Focal Loss)
- `label_smoothing=0.1`, `llrd=0.85`, `two_stage=True`, `TTA=True`
- Sin `--eval-hiba` durante el sweep (evaluar HIBA solo en el mejor checkpoint post-sweep)

---

## 3. Diseño del grid

15 trials por modelo = 5 valores de lr × 3 valores de weight_decay.  
`randaugment_m` se asigna en patrón rotativo (cada valor aparece 5 veces):

| Trial | lr | weight_decay | randaugment_m |
|-------|----|-------------|----------------|
| t01 | 3.0e-5 | 0.01 | 6 |
| t02 | 3.0e-5 | 0.05 | 9 |
| t03 | 3.0e-5 | 0.10 | 12 |
| t04 | 7.5e-5 | 0.01 | 9 |
| t05 | 7.5e-5 | 0.05 | 12 |
| t06 | 7.5e-5 | 0.10 | 6 |
| t07 | 1.5e-4 | 0.01 | 12 |
| t08 | 1.5e-4 | 0.05 | 6 |
| t09 | 1.5e-4 | 0.10 | 9 |
| t10 | 2.5e-4 | 0.01 | 6 |
| t11 | 2.5e-4 | 0.05 | 9 |
| t12 | 2.5e-4 | 0.10 | 12 |
| t13 | 5.0e-4 | 0.01 | 9 |
| t14 | 5.0e-4 | 0.05 | 12 |
| t15 | 5.0e-4 | 0.10 | 6 |

Total: **30 jobs SLURM** (15 ConvNeXt + 15 Swin).

---

## 4. Infraestructura

Los nodos de TOKO no tienen acceso a internet, por lo que no se puede usar un agente wandb online. Se usa **muestreo pre-definido**: cada trial es un job SLURM independiente con los parámetros hardcodeados en el script.

`submit_sweep.py` genera un script SLURM inline por trial y lo envía via SSH stdin (sin archivo temporal). wandb corre en modo offline; sincronizar después con `wandb sync outputs/wandb/`.

### Comandos de envío

```bash
# Sincronizar código local → TOKO
python scripts/toko/sync_up.py

# Enviar sweep (un modelo a la vez o ambos)
python scripts/toko/submit_sweep.py --model convnext_tiny   # 15 jobs
python scripts/toko/submit_sweep.py --model swin_tiny       # 15 jobs
python scripts/toko/submit_sweep.py --all                   # 30 jobs

# Previsualizar sin enviar
python scripts/toko/submit_sweep.py --all --dry-run

# Monitorear
python scripts/toko/monitor.py

# Bajar resultados
python scripts/toko/sync_down.py

# Sincronizar runs de wandb
wandb sync outputs/wandb/
```

### Archivos

| Archivo | Descripción |
|---------|-------------|
| `configs/sweeps/phase1_modern_sweep_grid.yaml` | Grid con los 15 trials por modelo |
| `scripts/toko/submit_sweep.py` | Script de envío (genera SLURM inline) |
| `slurm/toko/train_classifier.sh` | Script base (no se usa directamente en el sweep) |

---

## 5. Métrica objetivo

**`val_f1_weighted`** (maximizar). Consistente con todos los experimentos anteriores de Fase 1 y directamente comparable con la tabla de resultados.

---

## 6. Criterio de selección del ganador

Tras completar los 30 trials:

1. Ordenar por `val_f1_weighted` de mayor a menor.
2. Seleccionar el mejor trial de cada modelo.
3. Re-ejecutar los 2 ganadores **con `--eval-hiba`** para obtener métricas OOD.
4. Actualizar la tabla de resultados en `docs/resul/clasificadores_resul_final_*.md`.

---

## 7. Expectativas

- **ConvNeXt-Tiny:** esperamos F1 ≥ 0.856 (cerrar el gap de 1.6 pt vs ViT legacy).
- **Swin-Tiny:** esperamos F1 ≥ 0.825 (desde 0.816 en v3).
- Si ningún trial supera los valores de v3, la conclusión queda sin cambios: el legacy sigue siendo el mejor bajo el setup actual.
