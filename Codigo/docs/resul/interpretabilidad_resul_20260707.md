# Resultado — Interpretabilidad: ¿el modelo mira la lesión? (P2.5)

**Fecha:** 2026-07-07 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.5) · **Sin jobs SLURM** (local, RTX 4070).
**Feedback:** #11 — Grad-CAM / attention para mostrar que el modelo observa regiones clínicas relevantes.

## Diseño
- **Grad-CAM** sobre la última etapa de features de **Swin-Tiny** (clasificador supervisado) +
  **saliencia por gradiente** sobre **DermLIP** (VL classifier; gradiente de la similitud imagen-texto de
  la clase gt respecto de la imagen). Superpuestos sobre la imagen original.
- Una imagen por clase (7). **Código:** `scripts/interpretability.py`. **Salida:**
  `outputs/results/interpretability/interpretability.png`.

## Resultados (Figura `P25_interpretability`)
1. **Ambos modelos atienden la lesión, no el fondo.** El Grad-CAM de Swin se concentra sobre la lesión en
   casi todas las clases (BKL, DF, MEL, BCC, NV, AKIEC); la saliencia de DermLIP —más ruidosa por ser
   gradiente puro— también queda centrada en la lesión. No se activan sobre piel sana ni artefactos.
2. **Swin produce mapas más focalizados y limpios** que la saliencia de DermLIP (esperable: Grad-CAM sobre
   feature maps vs gradiente sobre el input).
3. **Caso honesto de error:** en el basocarcinoma (BCC), Swin \emph{atiende la región correcta} (la lesión)
   pero la \emph{clasifica} como melanoma. El modelo mira lo correcto y aun así confunde clases visualmente
   similares —un error de discriminación, no de atención—.

## Conclusión (veredicto)
**CUMPLE.** La interpretabilidad confirma que los modelos basan su decisión en la \emph{lesión} y no en
señales espurias del fondo, lo que da respaldo cualitativo a su validez clínica. No mejora las métricas
(no es su objetivo) pero fortalece la confianza en el clasificador. Se integra a `experimentacion.tex`
(§Interpretabilidad).
