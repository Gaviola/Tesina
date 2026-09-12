# Resultado — Réplica del ensamble consciente de la incertidumbre con LLaVA-Med

**Fecha:** 2026-09-12 · **Job:** Mendieta 1172480 (`unc_gen_llava`, 334/334 reportes, 0 errores, terminó
2026-09-11 16:39) · **Plan:** entrada "Cierre de pendientes de Limitaciones" en `ejecuciones.md` (2026-09-08)
· **Antecedentes:** [incertidumbre_3niveles_resul](incertidumbre_3niveles_resul_20260805.md),
[analisis_pipeline_avanzado_resul](analisis_pipeline_avanzado_resul_20260908.md)

## Motivación

La validación end-to-end del ruteo de 3 niveles (afirmativo / diferencial / abstención) se había hecho solo
con Mini-VLM (0.822 → 0.940 sobre los 1445 no derivados). Quedaba abierto si la mejora es propia del
generador o del ruteo. El componente de decisión (acuerdo Swin vs kNN-DermLIP) no depende del generador,
así que la réplica solo necesitaba los 334 reportes diferenciales de LLaVA-Med.

## Diseño

- Mismas imágenes, mismo ruteo (`outputs/uncertainty/uncertainty_3tier.csv`), mismos hiperparámetros de
  generación que `full_swin` de LLaVA-Med (checkpoint `stage2_llava_med_v2`, max_tokens 384, seed 42).
- Nivel afirmativo: reutiliza `llava_med/full_swin`. Diferencial: `llava_med/full_differential` (nuevo).
  Abstención: sin reporte.
- Scripts parametrizados con `--model` (default `mini_vlm`, que reproduce exactamente sus números previos):
  `ensemble_bootstrap.py --model llava_med`, `uncertainty_analysis.py --model llava_med`.
- Salidas: `outputs/results/ensemble_bootstrap_llava_med.json`, `uncertainty_analysis_llava_med.json`.

## Resultados

### Diagnostic consistency (bootstrap pareado, 2000 remuestreos)

| Conjunto | Sistema | Mini-VLM | LLaVA-Med |
|---|---|---|---|
| No derivados (n=1445) | Grounding simple | 0.822 | 0.706 |
| | Pipeline avanzado | **0.940** | **0.831** |
| | Δ [IC 95%] | +0.118 [0.101, 0.134] | +0.125 [0.109, 0.143] |
| Diferencial (n=334) | Grounding forzado | 0.392 | 0.353 |
| | Reporte diferencial | **0.901** | **0.895** |
| | Δ [IC 95%] | +0.509 [0.452, 0.566] | +0.542 [0.485, 0.602] |
| Cohorte completa (n=1503, derivación = sin dx) | Grounding simple | 0.812 | 0.696 |
| | Pipeline avanzado | **0.904** | **0.799** |

Control: `tab:ensamble` de LLaVA-Med se reproduce exactamente (0.645 / 0.454 / 0.696 / 0.852).

### Descomposición del valor del pipeline (para interpretar el 0.94)

| Nivel | n | Qué nombra el reporte | Mini-VLM | LLaVA-Med | Exactitud de Swin en el subconjunto |
|---|---|---|---|---|---|
| Afirmativo | 1111 (77% de no derivados) | 1 diagnóstico | 0.951 | 0.812 | 0.944 |
| Diferencial | 334 (23%) | 2 candidatos (criterio tipo top-2) | 0.901 | 0.895 | 0.347 |
| Abstención | 58 | sin reporte | — | — | — |

### Taxonomía de errores consciente del nivel (n=1445 no derivadas)

| Categoría | Mini simple | Mini avanzado | LLaVA simple | LLaVA avanzado |
|---|---|---|---|---|
| ok | 555 (38.4%) | 498 (34.5%) | 514 (35.6%) | 483 (33.4%) |
| ok diferencial | — | 240 (16.6%) | — | 225 (15.6%) |
| **Correcto total** | 555 (38.4%) | **738 (51.1%)** | 514 (35.6%) | **708 (49.0%)** |
| hedging | 491 (34.0%) | 436 (30.2%) | 257 (17.8%) | 239 (16.5%) |
| dx incorrecto | 275 (19.0%) | 95 (6.6%) | 195 (13.5%) | 101 (7.0%) |
| contradicción | 120 (8.3%) | 114 (7.9%) | 257 (17.8%) | 221 (15.3%) |
| repetición | 4 (0.3%) | 62 (4.3%) | 2 (0.1%) | 5 (0.3%) |
| insuficiente | 0 | 0 | 45 (3.1%) | 25 (1.7%) |
| otros | 0 | 0 | 175 (12.1%) | 146 (10.1%) |

Abstenidas (58): bajo grounding forzado LLaVA-Med habría emitido 18 dx incorrectos (Mini-VLM: 26).
Cohorte completa, dx incorrecto: LLaVA-Med 213/1503 (14.2%) → 101/1503 (6.7%), reducción del 53%.

### Robustez al leakage lesión-nivel (subconjunto limpio del test, n=861 no derivados)

`scripts/leakage_analysis.py`: el pipeline avanzado sigue siendo significativamente mejor sobre las imágenes
cuya lesión no aparece en train ni val — Mini-VLM +0.077 [0.058, 0.095], LLaVA-Med +0.096 [0.078, 0.117].

## Análisis

1. **La mejora se replica con casi la misma magnitud absoluta** (+0.118 vs +0.125) pese a que los generadores
   parten de niveles muy distintos (0.822 vs 0.706). Es lo esperable si la ganancia se origina en la
   *decisión* de rutear, común a ambos, y no en la redacción. El nivel más bajo de LLaVA-Med es el mismo
   efecto ya visto en `tab:ensamble`: nombra el diagnóstico inyectado con menos regularidad (0.812 en el
   nivel afirmativo, donde Mini-VLM llega a 0.951 con los mismos diagnósticos).
2. **El 0.94 no es una exactitud.** Mezcla un nivel de diagnóstico único (≈ exactitud del ancla) con un
   nivel que nombra dos candidatos, y excluye el 4% más difícil. La comparación honesta es contra el
   grounding simple sobre las mismas imágenes, acompañada del valor sobre la cohorte completa (0.904).
3. **Corrige una lectura previa sobre la repetición.** Con Mini-VLM el ruteo la amplificaba (0.3% → 4.3%) y
   se había atribuido al formato diferencial. Con LLaVA-Med, mismo formato, queda marginal (0.1% → 0.3%):
   la amplificación es propia de Mini-VLM.
4. **Perfil de error distinto por generador:** LLaVA-Med hedea menos pero contradice más y deja más reportes
   sin clase (`otros`), coherente con su estilo verboso. El ruteo reduce todas las categorías de error en
   ambos, salvo la repetición en Mini-VLM.

## Conclusión (veredicto)

**CUMPLE.** El ensamble consciente de la incertidumbre mejora la fidelidad diagnóstica de forma
significativa con los dos generadores (IC que excluyen el cero), reduce a la mitad o más el diagnóstico
incorrecto y se sostiene sobre el subconjunto sin leakage. Se elimina la limitación "validado sobre un solo
generador" y se corrige la atribución de la repetición al formato diferencial.

## Aplicado al documento

`tab:incertidumbre_e2e` pasa a dos columnas (Mini-VLM / LLaVA-Med) con Δ, IC y fila de cohorte completa;
`tab:taxonomia_incert` pasa a cuatro columnas; párrafos nuevos "Réplica con el segundo generador" y
"Cómo leer el 0.94"; se corrige la frase sobre la repetición.
