# Plan — Ola 1: SkinVL en el ensamble (P1.1 + ablaciones P1.2/P1.3)

**Fecha:** 2026-07-05 · **Plan maestro:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P1) · **Feedback:** #17,#22,#19,#4,#13.
**Cluster:** Mendieta (A30, generación). Es la **apuesta #1** y el palo largo (cola + integración).

## Motivación
Ya mostramos que la especialización de dominio rescató la *clasificación* (DermLIP). ¿Se traslada a la
*generación*? Un generador derm-especializado (SkinVL-MM) debería hedge menos, alucinar menos y subir la
consistencia diagnóstica. Se lo enchufa al **mismo ensamble** (baseline + grounding *noreasoning*) y se
compara contra LLaVA-Med/Mini-VLM.

## De-risk (hecho, sin gastar ola)
Inspección de `zwq803/SkinVL-MM` (HF):
- **Pesos FULL** (3 shards safetensors, ~14 GB), **no LoRA** → sin complejidad de merge de adapter.
- Formato **ORIGINAL de LLaVA-Med**: `architectures=['LlavaMistralForCausalLM']`, `model_type=llava_mistral`,
  base `llava-med-v1.5-mistral-7b`.
- **Problema:** nuestro `src/models/llava_med.py` carga formato **HF** (`LlavaForConditionalGeneration`,
  `chaoyinshe/...-hf`). SkinVL-MM **no carga directo** con ese runtime. No existe versión HF publicada
  (solo zwq803 en formato original) y `transformers 5.2` ya no trae el conversor.

## Decisión de integración
- **Primario — convertir a HF:** una vez convertido a `LlavaForConditionalGeneration`, el wrapper es un
  subclass fino (`src/models/skinvl.py`, ya creado) que reusa TODO el pipeline (generate/forward/ensamble)
  y no cambia el entorno del cluster. **Recomendado.**
- **Backup — loader original:** si la conversión falla, usar el builder del repo LLaVA-Med
  (`load_pretrained_model`) instalando el paquete `llava` en el env `dermvlm`. Más dependencias.
- **Fallback final:** plantilla clínica (P2.1, local) — ya cubre el ángulo de costo.

## Pasos (gating = conseguir un checkpoint que cargue)
1. **Descargar** `zwq803/SkinVL-MM` local (~14 GB).
2. **Validar el checkpoint** con el loader original de LLaVA-Med (clonar `microsoft/LLaVA-Med`,
   `load_pretrained_model`) generando sobre 2-3 imágenes derma → confirmar que está sano y coherente.
3. **Convertir a HF** (`LlavaForConditionalGeneration`) → guardar en `data/checkpoints/skinvl-mm-hf`
   (path que ya apunta `SkinVL.MODEL_NAME`). Referencia de conversión: script `convert_llava_weights_to_hf`
   de transformers (versión histórica) / export HF del repo LLaVA-Med.
4. **Validar carga HF local** (CPU, sin generar full): `build_model({"name":"skinvl"}).load_components()`
   arranca sin error → el wrapper carga. **Antes de enviar la ola.**
5. **Subir** `data/checkpoints/skinvl-mm-hf` al cache HF del cluster (offline).
6. `sync_up` + `submit` de `slurm/mendieta/v3/generate_reports_skinvl.sh`.

## Diseño de la ola (condiciones — todas en el mismo job)
Reusa los CSV de grounding model-agnostic (`outputs/full_dx_{oracle,swin,dermlip}.csv`):
- **baseline** (sin grounding) · **oracle/swin/dermlip** (grounding *noreasoning*) — igual que LLaVA/Mini.
- **P1.2 imagen-vs-dx** (`--no_image` + grounding oracle): imagen neutra, solo dx en el prompt.
- **P1.3 dx-erróneo** (`--diagnosis_source outputs/full_dx_wrong_swap.csv`): dx confundible
  (generar con `scripts/make_wrong_dx.py --input outputs/full_dx_oracle.csv --mode swap`).
- **Extra ZS clasificador (feedback #19):** SkinVL como clasificador zero-shot (casi gratis).

## Criterio de éxito (veredicto en el resul)
- SkinVL vs LLaVA-Med/Mini-VLM en Diagnostic Consistency (report-only) y Clinical Entity Recall sobre HAM;
  Nivel 1 sobre SkinCoT/MM-Skin. **¿La especialización sube la consistencia / baja el hedging?**
- Ablaciones: Δconsistencia con vs sin imagen (P1.2); caída/contradicciones con dx erróneo (P1.3).

## Sincronización con clústeres
- **Pre-descarga offline:** bajar SkinVL-MM (o el convertido) local → subir a `~/.cache/huggingface` del
  cluster (`HF_HUB_OFFLINE=1`), patrón ya usado. **Validar carga local ANTES de enviar** (evita quemar una
  ola de 5 días por formato).
- `sync_up.py` del wrapper (`skinvl.py`), `factory.py`, `generate_report.py` (flag `--no_image`),
  `make_wrong_dx.py` y los CSV de dx. `--delete` para huérfanos si corresponde.
- **Resume defensivo:** `generate_report.py` saltea reportes ya escritos; ante timeout, re-enviar.
- Al volver: `sync_down.py --logs <jobids>` + `--reports`. Evaluar local con `evaluate_reports.py`.
