# Runbook — Encolar la Ola 1 de SkinVL (P1.1)

**Plan:** [skinvl_ensemble_plan_20260705.md](skinvl_ensemble_plan_20260705.md). Pasos exactos para dejar
SkinVL corriendo en el cluster. El gate es la **conversión a HF** (paso 1).

---

## Paso 1 — Convertir SkinVL-MM a formato HF  ⛔ (el gate)
Trasplanta los pesos fine-tuneados de `zwq803/SkinVL-MM` sobre el HF base
`chaoyinshe/llava-med-v1.5-mistral-7b-hf`. **Sin GPU. Necesita ~28-32 GB de RAM** (dos copias de 7B) y
descarga ~28 GB la primera vez.

```bash
python scripts/convert_skinvl_to_hf.py        # -> data/checkpoints/skinvl-mm-hf
```
**Verificar en el log:** `trasplantados≈291`, `sin-mapear=0`, `target-no-encontrado=0`,
`shape-mismatch=0`, y que lo "conservado del base" sea **solo vision_tower**. Si aborta, el mapeo/shape
está mal (revisar el log; avisame y lo ajusto).

> ¿Dónde correrlo? Local si tenés ~32 GB de RAM. Si no, en el **nodo de login** de Mendieta (tiene
> internet para descargar) — así el checkpoint queda directo en el cluster y te ahorrás subir 14 GB.

## Paso 2 — Validar que carga (CPU, sin GPU)
```bash
python -c "from src.models.factory import build_model; m=build_model({'name':'skinvl'}); m.load_components(); print('OK carga SkinVL')"
```
Si imprime `OK carga SkinVL`, el formato quedó bien. (Carga 7B en RAM; no genera.)

## Paso 3 — Generar el CSV de dx-erróneo (P1.3, trivial)
```bash
python scripts/make_wrong_dx.py --input outputs/full_dx_oracle.csv --output outputs/full_dx_wrong_swap.csv --mode swap
```

## Paso 4 — Subir al cluster
```bash
python scripts/mendieta/sync_up.py            # sube código (skinvl.py, factory.py, generate_report.py,
                                              # make_wrong_dx.py, slurm/v3/*, submit.py)
```
- **Checkpoint (~14 GB):** si convertiste **local**, subir `data/checkpoints/skinvl-mm-hf/` a
  `~/dermvlm/data/checkpoints/` del cluster (rsync/scp; `sync_up` excluye `data/`). Si convertiste en el
  **login node**, ya está en su lugar.
- **CSV wrong_swap:** subir `outputs/full_dx_wrong_swap.csv` a `~/dermvlm/outputs/`, o generarlo en el
  cluster con el comando del Paso 3. (`full_dx_{oracle,swin,dermlip}.csv` ya están en el cluster.)

## Paso 5 — Smoke test (5 imágenes) ANTES de la ola completa
```bash
python scripts/mendieta/submit.py smoke_skinvl
# al terminar:
python scripts/mendieta/monitor.py <jobid>
python scripts/mendieta/sync_down.py --logs <jobid>
```
Revisar `logs/skinvl/smoke_*.out`: los 5 reportes deben ser **texto dermatológico coherente** (no vacío,
no repetido, menciona el dx en la condición oracle). Si se ve bien → Paso 6.

## Paso 6 — Ola completa
```bash
python scripts/mendieta/submit.py ensemble_skinvl
```
Corre baseline + grounding{oracle,swin,dermlip} + **no_image (P1.2)** + **dx-erróneo (P1.3)** sobre el
test split. Al volver:
```bash
python scripts/mendieta/sync_down.py --reports
python scripts/evaluate_reports.py ...        # Nivel 2 (consistency/recall) report-only
python scripts/per_class_ensemble.py --models skinvl ...   # comparar por clase vs LLaVA/Mini
```

## Cierre (flujo de siempre)
Registrar en `ejecuciones.md` (jobids) + escribir `docs/resul/skinvl_resul_<fecha>.md` con veredicto
(¿la especialización sube consistency / baja hedging vs LLaVA-Med/Mini-VLM?) + actualizar
`experimentacion.tex` y las tablas SOTA.
