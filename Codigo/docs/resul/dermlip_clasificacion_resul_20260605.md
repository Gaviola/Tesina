# DermLIP — Resultados clasificación zero-shot (VL classifier derm-especializado)

**Fecha:** 2026-06-05
**Dónde:** local (RTX 4070), sin cluster — ViT-B/16 ~150M, 1503 imgs en ~1m44s.
**Modelo:** `redlessone/DermLIP_ViT-B-16` (CLIP-style, entrenado en Derm1M)
**Plan:** [dermlip_clasificacion_plan_20260604.md](../ideas/dermlip_clasificacion_plan_20260604.md)

---

## 1. Motivación

Confirmar afirmativamente que un VL model **derm-especializado** (DermLIP) resuelve la clasificación
de 7 clases donde los VLMs médicos **generales** (LLaVA-Med, Mini-VLM) colapsan
([vlm_domain_gap_clinica_resul](vlm_domain_gap_clinica_resul_20260604.md)).

## 2. Diseño

Zero-shot por similitud coseno imagen-texto sobre **el mismo HAM10000 test (7 clases, n=1503)**.
Template ensemble (`"This is a skin image of {c}"` + variantes). Argmax directo (sin UNKNOWN, sin el
collapse del método `generate`). Mismo schema de métricas/predicciones que `train_vlm_classify.py`.

## 3. Resultados

| Modelo (HAM test) | Tipo / modo | **sens_macro** | Accuracy | F1 | spec_macro |
|-------------------|-------------|----------------|----------|-----|-----------|
| LLaVA-Med likelihood | VLM médico general (ZS) | 0.157 | 0.037 | 0.028 | — |
| Mini-VLM likelihood | VLM médico general (ZS) | 0.181 | 0.189 | 0.268 | — |
| **DermLIP** | **VL derm-especializado — ZS** | **0.510** | 0.377 | 0.424 | 0.900 |
| **DermLIP** | **VL derm-especializado — linear-probe** | **0.739** | **0.741** | **0.762** | 0.954 |
| Swin-Tiny v4 | CNN/ViT supervisado (full FT) | — | 0.827 | **0.882** | — |

**Linear-probe** (encoder DermLIP congelado + LogisticRegression `class_weight=balanced` sobre HAM
train, n=7010; embeddings cacheados, CPU, ~9min): sens por clase **balanceada** (MEL 0.57, NV 0.79,
BCC 0.74, AKIEC 0.74, BKL 0.61, DF 0.82, VASC 0.91). Con solo un cabezal lineal alcanza F1 0.76 —
**cerca del Swin supervisado (0.88)** y muy por encima de los VLM generales.

**Foto clínica (SkinCAP, n=624, ZS):** DermLIP sens_macro **0.454**, acc 0.386, F1 0.375, spec 0.901.
DermLIP discrimina en **ambos dominios** (~0.45–0.51), donde los VLM generales colapsan en ambos
(0.11–0.18). La especialización de dominio es el factor decisivo, no la modalidad de imagen.

**Sensibilidad por clase (DermLIP ZS):** MEL 0.760, VASC 0.773, AKIEC 0.735, DF 0.471, BCC 0.403,
NV 0.329, BKL 0.103.

**Distribución de predicciones:** MEL 52%, NV 22%, AKIEC 14%, BCC/VASC/DF/BKL 2% c/u. **Predice las
7 clases (no colapsa).**

## 4. Análisis

1. **DermLIP rompe el collapse: sens_macro 0.510 vs ~0.14 de los VLM generales (+0.37 absoluto),
   ≈3.6×.** Discriminación real de las 7 clases, **en zero-shot** (sin entrenar en HAM).
2. **No colapsa:** predice las 7 clases; spec_macro 0.90. Contrasta con el collapse a una clase
   arbitraria de LLaVA-Med/Mini-VLM.
3. **Sesgo clínicamente seguro:** sobre-predice melanoma (52%) → **alta sensibilidad a MEL (0.76)**,
   la clase más importante. Esto **baja la accuracy** (0.377) porque HAM es 67% NV y DermLIP
   sub-predice NV (sens NV 0.33), pero es el trade-off deseable en screening (no perder melanomas).
4. **vs supervisado:** Swin-Tiny (F1 0.88, entrenado en HAM) sigue ganando en accuracy absoluta —
   esperable, es supervisado in-distribution. DermLIP es **zero-shot**.

**Lectura para la tesis:** el resultado negativo de la clasificación VLM se reencuadra
definitivamente. No es "los VLMs no sirven para clasificar"; es:
> **VLM médico general (LLaVA-Med/Mini-VLM) → colapsa (≈azar). VL model derm-especializado (DermLIP)
> → discrimina las 7 clases en zero-shot (sens_macro 0.51). Clasificador supervisado (Swin) → mejor
> accuracy absoluta.** La especialización de dominio es el factor decisivo, no la modalidad "VLM".

## 5. Caveats

- **Accuracy del ZS baja por el sesgo a MEL** + desbalance de HAM (67% NV). El **linear-probe** (con
  `class_weight=balanced`) corrige esto: acc 0.741, sens balanceada. sens_macro/F1 son más informativos
  que accuracy en ZS.
- **Variante `DermLIP_PanDerm` pendiente:** no carga con open_clip 3.3.0 estándar (config custom
  `pretrain_path` del repo Derm1M; requiere registrar su modelo / pinear versión). El ViT-B/16 es el
  resultado principal.
- **Linear-probe = solo cabezal lineal sobre encoder congelado.** Un fine-tune completo del encoder
  podría acercarse más al Swin (0.88), pero el linear-probe ya demuestra la calidad del encoder.

## 6. Veredicto y siguiente paso

**Veredicto: CUMPLE ambos criterios.** Primario (ZS sens_macro 0.51 > 0.30) y secundario
(linear-probe F1 0.76, cerca del Swin 0.88). Evidencia afirmativa sólida de que un VL model
derm-especializado resuelve la clasificación que los VLMs generales no — **en zero-shot y con
linear-probe**, en dermatoscopía **y** foto clínica.

**Hecho (2026-06-05):** ZS HAM + ZS clínica + linear-probe HAM. **Pendiente (opcional):**
- Variante `DermLIP_PanDerm` (bloqueada por config custom de open_clip; baja prioridad).
- Fine-tune completo del encoder (vs solo linear-probe).
- Integrado a tablas SOTA (filas DermLIP). Marco teórico: la distinción VL classifier vs VLM generativo.

## 7. Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `src/models/dermlip.py` | Wrapper `DermLIPClassifier` (ZS + linear-probe opcional) |
| `scripts/eval_dermlip_classify.py` | Eval ZS, guarda en schema comparable |
| `outputs/results/dermlip/dermlip_zeroshot_vit-b-16_{predictions,test_results}.json` | Resultados |
| `src/models/factory.py` | Registro `"dermlip"` |
