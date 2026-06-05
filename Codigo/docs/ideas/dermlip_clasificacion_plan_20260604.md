# Plan: Agregar DermLIP — clasificador VL derm-especializado (Fase 1)

**Fecha:** 2026-06-04
**Modelo:** DermLIP (CLIP-style, entrenado en Derm1M) — `redlessone/DermLIP_ViT-B-16`
**Clusters:** corre **local** (RTX 4070) para ZS; fine-tune en TOKO/Mendieta si hace falta.
**Referencias:**
- [vlm_domain_gap_clinica_resul_20260604.md](../resul/vlm_domain_gap_clinica_resul_20260604.md) (los VLMs generales no resuelven la clasificación de grano fino)
- Memoria: `project_vlm_collapse_domain_not_imbalance`
- DermLIP/Derm1M: [HF](https://huggingface.co/redlessone/DermLIP_ViT-B-16) · [GitHub](https://github.com/SiyuanYan1/Derm1M) (ICCV'25)

---

## 1. Motivación

Los VLMs **médicos generales** (LLaVA-Med, Mini-VLM) no resuelven la clasificación dermatológica
de grano fino — colapsan en HAM (dermatoscopía) y en foto clínica. **Hipótesis:** un VL model
**derm-especializado** (DermLIP, pre-entrenado en Derm1M: 1M pares, incluye dermatoscopía + la
ontología que cubre HAM) **sí** discrimina las 7 clases. Confirmarlo convierte el resultado negativo
en una contribución afirmativa:

> *"El problema no es 'los VLMs', sino que LLaVA-Med/Mini-VLM son VLMs médicos generales; un VL model
> derm-especializado (DermLIP) sí resuelve la clasificación dermatoscópica."*

Esto enriquece la comparación central de la tesina (Fase 1: ¿aporta el VLM frente a modelos puramente
visuales?) con un matiz fuerte: **general → no; derm-especializado → sí**.

## 2. Alcance (respuesta a una pregunta clave)

**DermLIP es CLIP-style: SOLO clasificación/retrieval, NO generación de reportes.** Tiene encoder de
imagen + encoder de texto alineados, sin decoder autoregresivo. Por lo tanto:
- **Fase 1 (clasificación):** DermLIP entra acá.
- **Fase 2 (generación):** sigue del lado de los VLM generativos (LLaVA-Med/Mini-VLM actuales; a
  futuro SkinVL/DermatoLlama). DermLIP **no** participa en generación.
- (Matiz fuera de alcance: el *encoder* de DermLIP/PanDerm podría usarse como vision encoder de un VLM
  generativo, pero es un cambio de arquitectura mayor, no parte de este plan.)

---

## 3. Diseño experimental

Comparación apples-to-apples sobre **el mismo HAM10000 test (7 clases, n=1503)** usado para
LLaVA-Med/Mini-VLM y los CNN supervisados.

### 3.1 Fase A — Zero-shot (barato, prioritario)
- Cargar DermLIP vía `open_clip`, scorear las 7 clases HAM por **similitud coseno imagen-texto**
  (softmax). Argmax directo (sin UNKNOWN, sin el collapse del método `generate`).
- Template de prompt: `"This is a skin image of {clase}"` (el del repo), con los nombres completos de
  las 7 clases HAM (melanoma, melanocytic nevus, basal cell carcinoma, actinic keratosis, benign
  keratosis, dermatofibroma, vascular lesion) + ensemble opcional de templates.
- **Corre local** (ViT-B/16 ~150M, ~1500 imgs) en minutos. No requiere cluster.

### 3.2 Fase B — Fine-tune / linear-probe (comparación justa vs CNN)
- Linear-probe: congelar el encoder de imagen de DermLIP + cabezal lineal de 7 clases, entrenar sobre
  el train split de HAM (igual protocolo que los CNN). Compara "encoder derm-especializado + head" vs
  "CNN supervisado" en igualdad de condiciones.
- Opcional: fine-tune del encoder (no solo linear-probe) si el linear-probe es prometedor.

### 3.3 Variantes a evaluar
- `DermLIP_ViT-B-16` (ViT-B/16 + GPT2) — principal, liviano.
- `DermLIP_PanDerm-base-w-PubMed-256` (encoder PanDerm-B) — más fuerte, si la principal anda bien.

### 3.4 Baselines de comparación (ya disponibles)
| Enfoque | sens_macro HAM | F1 |
|---|---|---|
| Swin-Tiny supervisado (v4) | — | **0.882** |
| LLaVA-Med FT lik v2 | 0.137 | 0.198 |
| Mini-VLM FT lik v2 | 0.141 | 0.532 |
| **DermLIP ZS** | *(este plan)* | — |

---

## 4. Criterios de éxito

1. **Primario:** DermLIP ZS rompe el collapse — `sens_macro > 0.30` (idealmente >0.50) sobre HAM,
   muy por encima del ≈0.14 de los VLM generales. Confirma que la especialización de dominio resuelve
   la tarea.
2. **Secundario (Fase B):** DermLIP linear-probe se acerca o iguala a los CNN supervisados (F1 ~0.8+).
3. **Veredicto binario:**
   - Cumple → evidencia afirmativa del argumento "general vs especializado"; se integra a la
     comparación de Fase 1 de la tesis.
   - No cumple → ni siquiera un VL model derm-especializado resuelve la tarea ZS → refuerza que la
     clasificación dermatoscópica fina requiere supervisión dedicada (CNN). También es honesto.

---

## 5. Integración técnica (estructura del proyecto)

DermLIP es un **tercer tipo de modelo**: *VL classifier CLIP-style*, distinto de los classifiers
supervisados (`classifiers.py`, forward→logits) y de los VLM generativos (`vlm_base.py`, generate).

1. **Nuevo wrapper** `src/models/dermlip.py`:
   - `DermLIPClassifier(nn.Module)` que en `__init__` hace
     `open_clip.create_model_and_transforms('hf-hub:redlessone/DermLIP_ViT-B-16')` + tokenizer.
   - Método `zero_shot_classify(images, class_names, templates)` → logits por similitud coseno.
   - (Fase B) modo linear-probe: exponer `encode_image` + cabezal `nn.Linear(dim, 7)` para
     `forward(x)→logits`, compatible con el loop de `train_classifier.py`.
2. **Registrar** en `src/models/factory.py`: `MODEL_REGISTRY["dermlip"] = DermLIPClassifier`.
3. **Dependencia nueva:** `open_clip_torch` en `requirements.txt` (+ instalar en envs de cluster).
4. **Eval ZS:** path dedicado (no reusar el likelihood de VLM, que es log-prob de completion del LLM;
   DermLIP usa similitud CLIP). Opciones: (a) branch `--model dermlip` en `train_vlm_classify.py`
   con una función `run_clip_zeroshot_eval`, o (b) script nuevo `scripts/eval_dermlip_classify.py`.
   **Recomendado:** (a) para reusar el guardado de predicciones/métricas y la comparación.
5. **Fine-tune (Fase B):** reusar `scripts/train_classifier.py` tratando el encoder DermLIP como
   backbone (preprocess propio 224×224 de open_clip, no las transforms ImageNet).
6. **SLURM/aliases:** solo si se corre en cluster (la Fase A ZS corre local). Si se usa cluster:
   `slurm/{toko,mendieta}/dermlip_*.sh` + aliases en `submit.py`.

---

## 6. Documentación y estructura a actualizar (al implementar)

Al agregar el wrapper hay que mantener la consistencia documental del proyecto:

| Documento | Cambio |
|-----------|--------|
| `Codigo/CLAUDE.md` | Tabla **Modelos** (agregar fila DermLIP — tipo "VL classifier CLIP-style"); Stack (agregar `open_clip_torch`); aclarar la nueva categoría de modelo (ni classifier supervisado ni VLM generativo); nota de que es solo clasificación |
| `Codigo/docs/plan_implementacion.md` | Decisión de arquitectura: tercer tipo de modelo + dónde vive en `src/models/` |
| `Codigo/docs/USAGE.md` | Comandos para correr DermLIP ZS y fine-tune |
| `Codigo/requirements.txt` | `open_clip_torch` |
| `Docs/tabla_resultados_sota/tablas_comparativas_sota_v*.tex` | Fila DermLIP en la tabla de clasificación (al cerrar resultados) |
| `Codigo/docs/ejecuciones.md` | Entrada de la corrida + veredicto |
| `Codigo/docs/resul/dermlip_clasificacion_resul_<fecha>.md` | Crear con resultados + análisis |
| `Docs/estado_del_arte/` | (opcional) ya tiene DermLIP/Derm1M en `resumen_papers.tex`; eventual nota en marco teórico sobre VL classifiers vs VLM generativos |

**Estructura del repo:** no hace falta carpeta nueva; `src/models/dermlip.py` + registro alcanza.
Sí conviene documentar en CLAUDE.md la **distinción conceptual de los 3 tipos de modelo** (CNN/ViT
supervisado · VLM generativo · VL classifier CLIP-style) para que el proyecto quede navegable.

---

## 7. Sincronización con clústeres

- **Fase A (ZS): corre LOCAL** (RTX 4070, ViT-B/16, ~1500 imgs) — no requiere cluster ni sync. Esto
  es una ventaja: feedback inmediato sin cola.
- **Descarga de pesos:** `open_clip` baja el checkpoint de HF la primera vez → requiere internet. En
  **nodos de cómputo sin internet** (Mendieta/TOKO usan `HF_HUB_OFFLINE=1`), **pre-descargar el
  checkpoint localmente y subirlo** con `sync_up` al cache HF del cluster, igual que se hace con los
  otros modelos. Validar la ruta de cache antes de enviar.
- **Fase B (fine-tune) en cluster (si se decide):** `sync_up` del código nuevo (wrapper + script +
  requirements) **sin `--delete`** (solo agrega). Instalar `open_clip_torch` en el env del cluster
  (`sync_up.py --install-deps` o pip manual). Bajar resultados con `sync_down --results`.
- **Validación local vs cluster:** el wrapper y el sanity check (cargar modelo + ZS sobre 5 imgs) se
  prueban **localmente** antes de cualquier envío. La paridad de versiones de `open_clip_torch`
  local/cluster debe verificarse (mismo checkpoint).

---

## 8. Riesgos y mitigaciones

| Riesgo | Prob. | Mitigación |
|--------|-------|------------|
| Licencia CC BY-NC-4.0 (no comercial) | Baja | Uso académico/tesis OK; citar y no usar comercialmente |
| `open_clip_torch` incompatible con el env actual (torch/transformers) | Media | Probar local primero; fijar versión compatible |
| Pre-descarga de pesos en cluster offline | Media | Pre-bajar local + `sync_up` al cache HF (patrón ya usado) |
| DermLIP también falla en HAM ZS | Baja-Media | Es resultado honesto igual; refuerza necesidad de supervisión |
| Mismatch de preprocess (open_clip vs ImageNet) | Media | Usar el `preprocess` que devuelve open_clip, no las transforms del repo |

---

## 9. Estimación de costo

| Fase | Dónde | Tiempo |
|------|-------|--------|
| A — ZS (2 variantes) | Local RTX 4070 | minutos-1h |
| B — linear-probe vs CNN | Local o TOKO | ~horas |

Mucho más barato que cualquier iteración VLM previa. La Fase A da el resultado clave casi inmediato.

---

## 10. Plan de ejecución

1. Implementar `src/models/dermlip.py` + registro + `open_clip_torch` en requirements.
2. **Sanity check local:** cargar DermLIP, ZS sobre 5 imgs HAM, verificar que produce las 7 clases.
3. Eval ZS completa sobre HAM test (local) → `sens_macro`, F1, matriz de confusión, distribución de
   predicciones (¿colapsa o discrimina?).
4. (Si ZS prometedor) Fase B linear-probe vs CNN.
5. **Actualizar toda la documentación de §6.**
6. Documentar en `docs/resul/dermlip_clasificacion_resul_<fecha>.md` con veredicto; actualizar
   `ejecuciones.md` y tablas SOTA.
