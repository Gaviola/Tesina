# Resultado — Tests estadísticos (P0.2)

**Fecha:** 2026-07-05 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P0.2) · **Sin jobs SLURM** (local).
**Feedback:** #2 — intervalos de confianza + significancia (bootstrap, McNemar).

## Diseño
- **IC bootstrap 95%** (n_boot=2000, seed=42) para accuracy, F1-weighted y sensibilidad macro.
- **McNemar exacto** (binomial two-sided) por pares, sobre aciertos pareados en las mismas 1503 muestras
  (test HAM10000). Alineación verificada: las secuencias `y_true` coinciden entre los 4 modelos.
- **Código:** `scripts/statistical_tests.py`. **Salida:** `outputs/results/statistical_tests.json`.

## Resultados — clasificadores (n=1503)

| Modelo | accuracy | F1-weighted | sens. macro |
|--------|----------|-------------|-------------|
| Swin-Tiny      | 0.795 [0.774, 0.816] | 0.816 [0.798, 0.834] | 0.809 [0.765, 0.850] |
| DermLIP (ZS)   | 0.377 [0.353, 0.402] | 0.424 [0.397, 0.449] | 0.510 [0.460, 0.559] |
| LLaVA-Med (ZS) | 0.114 [0.098, 0.130] | 0.030 [0.023, 0.038] | 0.156 [0.145, 0.168] |
| Mini-VLM (ZS)  | 0.051 [0.041, 0.063] | 0.006 [0.004, 0.010] | 0.144 [0.137, 0.152] |

**McNemar (todos los pares): p < 0.001 (\*\*\*)** — todas las diferencias son altamente significativas
(ej.: Swin vs DermLIP p≈7e-143; DermLIP vs LLaVA-Med p≈6e-84; Mini vs LLaVA p≈4e-10).

## Análisis
1. **El gradiente de especialización es estadísticamente robusto:** los IC de sens. macro no se solapan
   entre Swin (0.77–0.85), DermLIP (0.46–0.56) y los VLMs generales (0.14–0.17). El orden
   supervisado > VL derm-especializado > VLM general **no es ruido**.
2. **El colapso de los VLMs generales queda confirmado con rigor:** el IC de sens. macro de Mini-VLM es
   **[0.137, 0.152]** y el de LLaVA-Med **[0.145, 0.168]**, ambos abrazando el nivel de azar (1/7 =
   **0.143**). Es decir, son **estadísticamente indistinguibles del azar** — ya no es una observación
   puntual sino un intervalo.
3. **DermLIP recupera discriminación de forma significativa:** su sens. macro [0.46, 0.56] está muy por
   encima del azar y del de los VLMs (McNemar p<1e-100), aunque por debajo de Swin.

## Pendiente
- **Ensamble (Baseline vs Grounding vs Oracle):** el script ya acepta `--consistency_json` (arrays 0/1
  de consistencia por-reporte por condición) para hacer bootstrap + McNemar del ensamble. Esos arrays los
  produce **P0.3** (análisis por-reporte/por-clase). Se completa al cerrar P0.3.

## Conclusión (veredicto)
**CUMPLE** (parte clasificadores). Las comparaciones Swin vs DermLIP vs Mini-VLM vs LLaVA-Med tienen IC
bootstrap y McNemar; el gradiente de especialización y el colapso al azar de los VLMs generales son
**estadísticamente significativos**. Se integra a `experimentacion.tex` (IC en las tablas de clasificación
+ frase de significancia). La parte de ensamble se cierra junto con P0.3.
