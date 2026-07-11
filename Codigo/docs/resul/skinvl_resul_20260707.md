# Resultado — SkinVL en el ensamble + ablaciones imagen-vs-dx / dx-erróneo (P1.1, P1.2, P1.3)

**Fecha:** 2026-07-07 · **Plan:** [skinvl_ensemble_plan](../ideas/skinvl_ensemble_plan_20260705.md) · **Job Mendieta 1159785 (COMPLETED, 10h24m).**
**Feedback:** #17,#22 (VLM derm-especializado en generación) · #4 (aporte de la imagen) · #13 (robustez a dx erróneo).

## Diseño
SkinVL-MM (LLaVA-Med-v1.5 + LoRA sobre MM-Skin) enchufado al **mismo ensamble** que LLaVA-Med/Mini-VLM,
sobre el test completo de HAM (n=1503), report-only. Condiciones: baseline (sin grounding) +
grounding {DermLIP, Swin, oracle} + **oracle sin imagen** (P1.2) + **dx-erróneo** (P1.3).
*(Nota: el SLURM no pasó `--label_csv`; el `gt_label` se completó post-hoc desde `full_dx_oracle.csv`.)*

## Resultados — Diagnostic Consistency (report-only)

| Condición | **SkinVL** (n=1503) | LLaVA-Med (n=400) | Mini-VLM (n=400) |
|-----------|:-:|:-:|:-:|
| baseline (sin grounding) | **0.00** | 0.59 | 0.20 |
| DermLIP (clasif.\ 0.38) | 0.43 | 0.45 | 0.48 |
| Swin (clasif.\ 0.80) | 0.80 | 0.70 | 0.83 |
| oracle (gt) | 1.00 | 0.84 | 1.00 |

Por clase (SkinVL): baseline $0.00$ en todas $\to$ con Swin $0.71$–$0.95$ $\to$ oracle $\approx 1.00$.

## Hallazgos
1. **Sin grounding, SkinVL colapsa TOTAL (consistency 0.00), peor que los VLM generales.** El modelo
   derm-especializado, sobre imágenes dermatoscópicas de HAM sin dx, produce una respuesta memorizada de
   su entrenamiento en MM-Skin (clínico/patología) —p.ej.\ "tinea corporis"— idéntica entre imágenes. La
   especialización sobre \emph{otra} distribución de imágenes no transfiere a HAM por sí sola.
2. **Con grounding, alcanza el nivel de Mini-VLM** (Swin $0.80$, oracle $1.00$) y supera a LLaVA-Med. La
   propagación de la calidad del clasificador es monótona (baseline$\to$DermLIP$\to$Swin$\to$oracle).
3. **SkinVL NO hace \emph{hedging}** (taxonomía: hedging $\approx 0.00$ en todas las condiciones, vs
   LLaVA $0.20$–$0.27$ y Mini $0.37$–$0.43$). La especialización lo vuelve \textbf{decisivo}: es el
   beneficio real del generador derm-especializado. Su `dx_incorrecto` sigue exactamente la calidad del
   clasificador (DermLIP $0.62$ / Swin $0.20$ / oracle $0.00$) — pura propagación.
4. **Pero sus reportes son \emph{terse}**: clinical entity recall $0.33$–$0.50$ (vs $0.75$–$0.79$ de
   LLaVA/Mini). Gana en fidelidad/decisión, pierde en riqueza morfológica —básicamente enuncia el dx.

## Ablaciones (SkinVL, n=1503)

| Ablación | Consistency | Interpretación |
|----------|:-:|----------------|
| **P1.2** oracle CON imagen | **1.00** | — |
| **P1.2** oracle SIN imagen (blank) | **0.97** | **Quitar la imagen casi no cambia nada ($\Delta=0.03$): una vez conocido el dx, la imagen aporta $\approx$ nada.** |
| **P1.3** dx-erróneo (swap) | **0.11** | SkinVL **se compromete con el dx equivocado** y no lo corrige con la imagen (propagación de error total). |

## Conclusión (veredicto)
**CUMPLE, con un hallazgo que refina la tesis.** La especialización del generador (SkinVL) **elimina el
hedging** y da alta consistencia \emph{cuando está grounded}, pero **no aporta grounding visual**: la
ablación imagen-vs-dx muestra que la imagen es casi irrelevante una vez dado el dx ($1.00\to0.97$), y con
un dx erróneo el modelo se compromete con el error ($0.11$). Es decir, **la fidelidad diagnóstica del
ensamble viene del CLASIFICADOR, no de la visión del generador** —el generador transcribe el dx a prosa—.
Junto con P2.1 (una plantilla iguala al VLM en consistency), esto sostiene que la generación con VLM
aporta \emph{estilo/fluidez}, no valor diagnóstico. **La contribución metodológica es el pipeline en
cascada; el clasificador es el que diagnostica.** Se integra a `experimentacion.tex` (Sección de ensamble
+ ablaciones).
