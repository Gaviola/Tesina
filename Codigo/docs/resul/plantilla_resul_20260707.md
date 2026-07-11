# Resultado — Baseline de generación por plantilla clínica (P2.1)

**Fecha:** 2026-07-07 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.1) · **Sin jobs SLURM** (local).
**Feedback:** #23 — generación por plantilla (clasificador → atributos → plantilla) como baseline fuerte.

## Motivación
¿Hace falta un VLM generativo pesado, o una **plantilla trivial** sobre el clasificador ya asegura la
fidelidad diagnóstica del reporte? Es el baseline de costo de la generación (complementa P0.4 y la
comparación con SkinVL).

## Diseño
- **Plantilla:** clasificador → dx → texto fijo con morfología típica de la clase
  (*"Diagnosis: the lesion is consistent with {dx}. On examination it shows {morfología}\ldots"*). Costo
  de generación **cero** (sin VLM).
- Se evalúa con el **mismo NER** (diagnostic consistency + clinical entity recall) que los VLM, sobre las
  **mismas imágenes** (se reusa `image_id`/`gt`/`grounded_dx` de los reportes ya generados), grounding
  Swin y oracle.
- **Código:** `scripts/generate_template_report.py`. **Salida:** `outputs/results/template/`.

## Resultados (n=400)

| Condición | Sistema | Diagnostic Consistency | Clinical Entity Recall |
|-----------|---------|:-:|:-:|
| Swin-grounded | **plantilla** | **0.828** | 0.435 |
| | LLaVA-Med | 0.703 | 0.754 |
| | Mini-VLM | 0.830 | 0.766 |
| Oracle (gt) | **plantilla** | **1.000** | 0.412 |
| | LLaVA-Med | 0.845 | 0.762 |
| | Mini-VLM | 1.000 | 0.787 |

## Análisis
1. **En fidelidad diagnóstica (consistency), la plantilla iguala o supera a los VLM, a costo cero.** Con
   grounding Swin, la plantilla ($0.828$) supera a LLaVA-Med ($0.703$) y empata a Mini-VLM ($0.830$); con
   oracle llega a $1.000$ (como Mini, por encima de LLaVA $0.845$). La consistencia de la plantilla ≈
   exactitud del clasificador, porque el reporte siempre afirma el dx provisto —los VLM, en cambio, a
   veces \emph{no} lo afirman aunque se les entregue (el hedging/contradicción residual de P0.5).
2. **La plantilla pierde en riqueza (recall $\approx 0.42$ vs $0.75$--$0.79$).** Su morfología es fija y
   cubre menos categorías clínicas; los VLM producen descripciones más ricas y variadas.
3. **El aporte del VLM es la riqueza/fluidez, NO la fidelidad diagnóstica.** Combinado con el costo
   (P0.4: VLM $24$--$66$ s/reporte vs plantilla instantánea), esto acota el costo/beneficio: si lo único
   que importa es afirmar el diagnóstico correcto, una plantilla sobre el clasificador basta; el VLM se
   justifica solo si se valora la narrativa morfológica.

## Conclusión (veredicto)
**CUMPLE.** La plantilla es un baseline de costo fuerte: **misma o mejor fidelidad diagnóstica que los
VLM, a costo de generación nulo**, sacrificando riqueza morfológica. Es el piso de costo contra el cual
se mide cualquier generador (incluido SkinVL, ola en curso). Se integra a `experimentacion.tex`
(sección de costo / generación).
