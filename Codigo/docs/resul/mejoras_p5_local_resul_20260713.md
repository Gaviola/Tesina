# Resultado — P5.1 Ensamble de clasificadores + P5.2 Wilcoxon (locales)

**Fecha:** 2026-07-13 · **Plan:** [mejoras_resultados_p5_plan](../ideas/mejoras_resultados_p5_plan_20260713.md) · **Sin jobs SLURM** (local, RTX 4070).

## P5.1 — Ensamble de clasificadores (voto suave)

**Diseño:** promedio de probabilidades de clasificadores modern_v3 sobre el mismo test HAM (n=1503).
Dos comparaciones: (a) sobre los `y_prob` single-view ya guardados; (b) **auto-consistente**, re-corriendo
Swin y ConvNeXt **con TTA** (original+hflip) localmente para comparar el ensamble contra el individual bajo
el mismo protocolo (`scripts/reeval_tta_probs.py`; los headline 0.887 usan el checkpoint sweep_v4 de TOKO,
que no está local — por eso se re-mide todo con el checkpoint modern_v3 local, para una comparación limpia).
Código: `scripts/classifier_ensemble.py`. Salida: `outputs/results/classifier_ensemble/`.

**Resultado (TTA, checkpoints modern_v3, n=1503):**

| Modelo | Acc | F1-w | Sens. macro |
|--------|:---:|:---:|:---:|
| Swin-Tiny (TTA) | 0.802 | 0.818 | 0.793 |
| ConvNeXt-Tiny (TTA) | 0.826 | 0.852 | 0.827 |
| **Ensamble Swin+ConvNeXt** | **0.843** | **0.856** | **0.846** |

- Δ sens. macro ensamble vs mejor individual = **+0.019** (single-view daba el mismo signo, +0.022).
- La ganancia se concentra en **sensibilidad macro** (clases minoritarias), no tanto en F1-w (+0.004).
- **Costo:** el ensamble duplica la inferencia (2 modelos) por +2 puntos de sens. macro.

**Lectura para la tesina:** combinar dos clasificadores chicos mejora la discriminación balanceada de forma
modesta pero real, coherente con la idea de "estructura eficiente". El costo (2×) por +0.02 sugiere que,
para este dataset ya casi saturado in-distribution, TTA sobre un único modelo especializado es una palanca
más barata que apilar modelos. El verdadero cuello de botella no es la métrica in-distribution sino la
generalización OOD (HIBA), que un ensamble homogéneo no ataca.

## P5.2 — Test de Wilcoxon (rangos con signo) por clase

**Diseño:** completar el trío bootstrap+McNemar+**Wilcoxon** (feedback). Wilcoxon sobre el **recall por
clase** (7 pares) entre clasificadores pareados — complementa a McNemar (por-muestra global) preguntando si
un modelo mejora la discriminación *clase a clase* de forma sistemática. Código: `scripts/statistical_tests.py`
(extendido).

**Resultado:**

| Comparación | p (Wilcoxon) | mediana Δrecall |
|-------------|:---:|:---:|
| Swin vs DermLIP (ZS) | 0.016 * | +0.235 |
| Swin vs Mini-VLM (ZS) | 0.031 * | +0.794 |
| Swin vs LLaVA-Med (ZS) | 0.031 * | +0.733 |
| DermLIP vs Mini-VLM (ZS) | 0.109 ns | +0.471 |
| DermLIP vs LLaVA-Med (ZS) | 0.047 * | +0.329 |
| Mini-VLM vs LLaVA-Med (ZS) | 1.000 ns | +0.000 |

- Swin domina a **todos** clase a clase (p<0.05). DermLIP supera a los VLMs generales (vs LLaVA p=0.047;
  vs Mini p=0.109 ns solo por baja potencia con n=7 clases, la mediana Δ es +0.47).
- Los **dos VLMs generales son estadísticamente indistinguibles entre sí** (p=1.0, mediana Δ=0): ambos
  colapsan al azar por igual. Refuerza que el problema es de dominio, no de un modelo en particular.

## Conclusión (veredicto)

**CUMPLE (ambas).** P5.1: el ensamble Swin+ConvNeXt mejora la sens. macro en +0.019 (modesto, a 2× costo).
P5.2: Wilcoxon por clase agrega la tercera prueba estadística pedida y confirma el gradiente de
especialización a nivel de clase. Ambas se integran a `experimentacion.tex` (§Robustez/estadística y una
mención al ensamble de clasificadores en la conclusión de clasificación).
