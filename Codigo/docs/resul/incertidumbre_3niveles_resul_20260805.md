# Resultado — Ensamble consciente de la incertidumbre: router de 3 niveles (D2)

**Fecha:** 2026-08-05 · **Plan:** [cierre_experimentacion_plan](../ideas/cierre_experimentacion_plan_20260805.md) (D2) · **Sin jobs SLURM** (routing local; generación de diferenciales pendiente).
**Origen:** propuesta del tutor (2026-08-05, `feedback_20260805.md` + `image.png`): ruteo por confianza con
`τ_alta`/`τ_baja` y tres niveles (afirmativo / diferencial / abstención-derivación).

## Motivación

El pipeline con grounding transmite al generador una etiqueta diagnóstica **"dura"**: si el clasificador
se equivoca, el error se propaga al reporte con falso aplomo (P1.3/P4.1). El tutor propone un ensamble
**consciente de la incertidumbre** que, según la confianza, module la salida: afirmar cuando hay confianza,
dar un **diferencial** cuando no, y **abstenerse/derivar** cuando la ambigüedad es máxima. Esto conecta la
calibración con el sistema (antes quedaba como análisis desconectado).

## Diseño (híbrido: marco del tutor + señal que funciona)

Se adopta el marco de 3 niveles del tutor, pero **no** con la softmax cruda —que ya vimos que rutea mal
(P0.1/P5.4: no monótona)—, sino con la **señal que sí separa**: el **acuerdo entre dos clasificadores
especializados baratos**, Swin (supervisado) y el **kNN sobre embeddings DermLIP** (la recuperación de
P5.3), más el consenso de los 3 vecinos recuperados. Reglas (`scripts/build_uncertainty_3tier.py`):
- **Afirmativo:** Swin $=$ voto kNN (coinciden) → reporte definitivo con ese dx.
- **Abstención:** Swin $\ne$ voto kNN **y** los 3 vecinos son todos de clases distintas (sin consenso →
  ambigüedad máxima) → **derivar a un especialista** (no se emite diagnóstico).
- **Diferencial:** Swin $\ne$ voto kNN pero hay consenso parcial → reporte diferencial con \{Swin, kNN\}.

## Resultados (test HAM10000, n=1503)

| Nivel | n (%) | Métrica de cobertura |
|-------|:-:|:-:|
| **Afirmativo** (acuerdo) | 1111 (74%) | exactitud (gt = Swin) **0.944** |
| **Diferencial** (consenso parcial) | 334 (22%) | gt $\in$ \{Swin, kNN\} **0.898** |
| **Abstención** (3 vecinos distintos) | 58 (4%) | gt $\in$ \{Swin, kNN\} 0.793 (los más difíciles) |

**Cobertura efectiva del sistema** (afirmativo acierta **o** el diferencial contiene el gt, sobre los
casos no-abstenidos): **0.934 (1349/1445)**.

## Análisis

1. **El sistema pone el diagnóstico correcto "sobre la mesa" el 93.4% de las veces** (no-abstenidos): o lo
   afirma (cuando los dos clasificadores coinciden, acierto 0.94) o lo incluye entre 2 candidatos cuando
   duda (el gt está entre ellos el 90%). Frente al grounding forzado con Swin (que emite un único dx y
   acierta $\approx$0.80 global), la formulación consciente de la incertidumbre **aumenta drásticamente la
   probabilidad de que la verdad esté presente**, en vez de comprometerse con un único diagnóstico que
   puede ser equivocado.
2. **La abstención aísla lo intratable:** el 4% que se deriva son los casos de máxima ambigüedad (los 3
   vecinos discrepan), donde incluso \{Swin, kNN\} contiene el gt solo el 79%. Derivarlos a un especialista
   es la decisión clínicamente correcta y evita el reporte confiadamente incorrecto.
3. **Conecta la incertidumbre con el sistema** (lo que pedía el tutor) usando dos clasificadores
   especializados **baratos** (Swin + recuperación DermLIP), sin softmax mal calibrada.

## Generación end-to-end (job Mendieta 1163000, COMPLETED 3h45m)

Se generaron los **334 reportes diferenciales** (plantilla `DIFFERENTIAL_TEMPLATE`, Mini-VLM). El afirmativo
reutiliza los reportes `full_swin`; la abstención no genera. *(La generación local no fue posible: el torch
de la `.venv` es CPU-only; se corrió en Mendieta al recuperarse su scheduler.)*

**En el subconjunto diferencial (n=334):**

| Reporte | menciona el gt | entity recall |
|---------|:-:|:-:|
| Grounding **forzado** (se compromete con Swin) | 0.392 | 0.687 |
| **Diferencial** (presenta \{Swin, kNN\}) | **0.901** | 0.870 |

El reporte diferencial menciona el diagnóstico correcto el **90%** vs el **39%** del grounding forzado
—justo en los casos donde el clasificador falla—, y con reportes más ricos. El texto realiza fielmente la
cobertura del router (gt $\in$ candidatos 0.898).

**Sistema completo vs grounding simple (sobre los 1445 no-abstenidos):**

| Sistema | Diagnostic consistency |
|---------|:-:|
| **Pipeline avanzado** (afirmativo=grounding + diferencial) | **0.940** (1358/1445) |
| Grounding **simple** (forzado, mismo conjunto) | 0.822 (1188/1445) |

El ensamble consciente de la incertidumbre sube la fidelidad de **0.822 a 0.940 ($+14\%$)** sobre los
no-abstenidos, \emph{y} deriva el 4% más ambiguo (que el grounding simple respondería con falso aplomo). El
$0.940$ medido sobre los reportes reales coincide con la cobertura del router ($0.934$).

## Conclusión (veredicto)

**CUMPLE (completo).** El ensamble consciente de la incertidumbre de 3 niveles —afirmar / diferencial /
abstener— sube la consistencia diagnóstica de $0.82$ (grounding simple) a $0.94$ sobre los casos no
derivados, deriva el 4% más ambiguo, y sus reportes diferenciales mencionan el gt el 90% (vs 39% del
grounding forzado) justo donde el clasificador falla. Implementa la propuesta del tutor con una señal que
funciona (acuerdo Swin↔kNN) y conecta la calibración con el sistema. Integrado a `experimentacion.tex`.
