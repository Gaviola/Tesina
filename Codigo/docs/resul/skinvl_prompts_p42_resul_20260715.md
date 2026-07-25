# Resultado — P4.2: SkinVL baseline con prompts alternativos (mejora #8)

**Fecha:** 2026-07-15 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) §6.1 (P4.2) · **Job Mendieta 1160208 (COMPLETED, 1h03m).**

## Motivación

El baseline de SkinVL (sin grounding, prompt `"Describe this skin lesion."`) **colapsa a modo**: 72% de
los reportes son idénticos ("tinea corporis") y la consistencia diagnóstica es ≈0. La mejora #8 pregunta si
esto es un artefacto del **prompt** o un **mismatch de distribución** (SkinVL se entrenó sobre MM-Skin,
fotos clínicas; se evalúa sobre HAM10000, dermatoscopía). Se probaron dos prompts alternativos sobre 400
imágenes: uno de **diagnóstico directo** y uno de **rol clínico**.

## Resultados

| Prompt | n | reportes únicos | reporte dominante | consistency |
|--------|:-:|:-:|:-:|:-:|
| `"Describe this skin lesion."` (baseline) | 1503 | 72 | **72%** "tinea corporis" | 0.002 |
| diagnóstico directo (`prompt_diag`) | 400 | 36 | 33% "lichen planus pigmentosus" | 0.025 |
| rol clínico (`prompt_clinical`) | 400 | 20 | **56%** "lichen planus pigmentosus" | 0.177 |

- Reporte dominante baseline: *"...likely caused by a fungal infection called tinea corporis."*
- Reporte dominante con prompts nuevos: *"...I would diagnose this as a case of lichen planus pigmentosus."*

## Análisis

1. **Cambiar el prompt NO des-colapsa: solo cambia el atractor.** El baseline colapsa a "tinea corporis";
   los dos prompts nuevos colapsan a **"lichen planus pigmentosus"** (33–56% de reportes idénticos). El
   modelo sigue emitiendo un único diagnóstico dominante, apenas cambia cuál.
2. **La evidencia decisiva:** tanto "tinea corporis" como "lichen planus pigmentosus" **no pertenecen a las
   7 clases de HAM10000**. SkinVL produce diagnósticos de la **distribución de MM-Skin** (su corpus de
   entrenamiento) prácticamente sin mirar la imagen dermatoscópica de HAM. Esto confirma que el colapso es
   un **mismatch de distribución (MM-Skin → HAM)**, no un problema de fraseo del prompt.
3. La consistencia sube marginalmente (0.002 → 0.177) con el prompt de rol clínico, pero sigue siendo muy
   pobre: el 56% "lichen planus pigmentosus" no aporta a la consistencia (no es clase HAM), y el resto rara
   vez acierta el gt.
4. **Refuerza la conclusión del ensamble:** SkinVL solo es útil *con grounding* — cuando el clasificador le
   dicta el diagnóstico (P1.1). Por sí solo, ni siquiera el prompt correcto lo salva del mismatch de dominio.

## Conclusión (veredicto)

**CUMPLE.** Cierra la mejora #8: el colapso del baseline de SkinVL es **mismatch de distribución
MM-Skin→HAM, no del prompt** (dos prompts distintos colapsan a un diagnóstico distinto pero igualmente
fuera de HAM). Confirma y refuerza el re-enmarcado D8 en `experimentacion.tex`. Se agrega esta evidencia a
la subsección SkinVL.
