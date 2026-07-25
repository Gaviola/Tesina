# Plan — P5.4: Generación consciente de la incertidumbre

**Fecha:** 2026-07-25 · **Origen:** [mejoras_resultados_p5_plan](mejoras_resultados_p5_plan_20260713.md) (P5.4) + feedback #16 (uncertainty-aware). Conecta la calibración (P0.1) con la generación.

## Motivación

Las ablaciones (P1.2/P1.3/P4.1) probaron el modo de falla del ensamble: **se compromete con el diagnóstico
del clasificador con falsa confianza**, y cuando el clasificador se equivoca, el error se propaga entero.
La calibración (P0.1) mostró que la confianza cruda no sirve. Idea: **calibrar** el clasificador y, según
su confianza, **modular el reporte**: definitivo cuando está seguro, **diferencial** (lista de candidatos)
cuando no. Es degradación elegante en vez de un diagnóstico único potencialmente equivocado.

## Diseño

> **Pivote de señal (2026-07-25).** El plan original ruteaba por **confianza softmax calibrada**
> (temperature scaling). Se implementó (`scripts/temperature_scaling.py`, T=0.53) pero **resultó un mal
> ruteador**: la confianza es \emph{no monótona} respecto de la exactitud (a conf≥0.5 el grupo "confiado"
> tenía acc 0.71 vs 0.85 del "inseguro"), porque el Swin es sub-confiado sobre todo en la clase mayoritaria
> fácil (nevo). Se pivoteó a una señal mucho mejor: el **acuerdo entre dos clasificadores especializados**
> —Swin y el kNN sobre embeddings DermLIP (la recuperación de P5.3)—.

1. **Señal de incertidumbre = acuerdo Swin ↔ kNN-DermLIP** (`scripts/build_uncertainty_agreement.py`).
   Coinciden → \emph{confiado}; difieren → \emph{inseguro}. Sobre el test: **acuerdo 74% con acc 0.944**;
   **desacuerdo 26%**, donde el gt está en {Swin,kNN} el **88%** (vs forzar Swin solo, 0.37).
2. **Ruteo:** CSV `outputs/uncertainty/uncertainty.csv` (`image_id, unc_dx, unc_candidates, unc_conf,
   unc_confident`). (Se conserva `temperature_scaling.py` porque el hallazgo "la confianza softmax no
   sirve para rutear" es un resultado en sí mismo.)
3. **Generación (cluster):** Mini-VLM, n=400, modo `--uncertainty`:
   - confiado → reporte **definitivo** (grounding noreasoning con el top-1);
   - inseguro → reporte **diferencial** con los candidatos top-k (plantilla nueva `DIFFERENTIAL_TEMPLATE`).
   SLURM `slurm/mendieta/v3/uncertainty_generation.sh` (alias `unc_gen`). Compara contra `full_swin`
   (grounding siempre-definitivo) y `full_oracle`, ya existentes.

## Criterio de éxito

- **Señal previa (clasificador, sin generar):** en el subconjunto \emph{inseguro}, el top-k debe contener
  el gt más que el top-1 (si no, el diferencial no puede ayudar).
- **Generación:** en el subconjunto \emph{inseguro}, la \emph{diagnostic consistency} de los reportes
  diferenciales ≥ la de los reportes forzados (`full_swin`) — es decir, mencionar los candidatos rescata
  casos que el grounding forzado erraba.

## Sincronización con clústeres

- El CSV de incertidumbre se genera **local** (temperature scaling en RTX 4070) y se sube por scp
  (`outputs/` excluido de `sync_up`). `sync_up.py` para el código (nuevo modo `--uncertainty`).
- Validar con un smoke corto antes de la corrida de 400 si hay dudas del prompt.
- Al volver: evaluar consistency por subconjunto (confiado/inseguro) → resul + integrar a
  `experimentacion.tex`.
