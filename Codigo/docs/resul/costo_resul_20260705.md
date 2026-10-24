# Resultado — Comparación de costo computacional (P0.4)

**Fecha:** 2026-07-05 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P0.4) · **Sin jobs SLURM** (local + logs).
**Feedback:** #44 — falta una comparación sistemática del costo de inferencia entre alternativas.

> **Corrección (2026-10-12).** La latencia de los VLM se tomaba como la mediana de *todos* los logs del
> modelo, que mezclan condiciones (512 o 384 tokens, prompts con recuperación) y cambian al bajar logs
> nuevos (Mini-VLM pasaba a 50.3 s con el log del RAG). `measure_cost.py` usa ahora las corridas del
> re-anclaje (mismo script y plantilla, 384 tokens): **Mini-VLM 16.4 s, LLaVA-Med 26.2 s, SkinVL-MM 3.4 s**
> por reporte (SkinVL escribe reportes mucho más cortos). Salida: `outputs/results/cost/cost_comparison_v2.json`.

## Diseño
- **Clasificadores (torchvision):** parámetros + latencia medidos EN VIVO en la GPU local (RTX 4070 12GB).
- **VLMs generativos:** latencia real por-reporte **parseada de los logs SLURM** (A30, líneas "Progreso").
- **Params/VRAM de DermLIP y VLMs:** tabla de referencia (no cargan local: VRAM insuficiente / falta open_clip).
- **Código:** `scripts/measure_cost.py`. **Salida:** `outputs/results/cost/` (`cost_comparison.json`, `cost_latency.png`).

## Resultados

| Modelo | rol | params (M) | VRAM (GB) | latencia / item | hardware |
|--------|-----|:-:|:-:|:-:|:-:|
| ConvNeXt-Tiny | classifier | 28.6 | ~0.6 | **3.9 ms** /img | RTX 4070 12GB |
| ViT-B/16 | classifier | 86.6 | ~0.8 | **4.4 ms** /img | RTX 4070 12GB |
| Swin-Tiny | classifier | 28.3 | ~0.6 | **8.7 ms** /img | RTX 4070 12GB |
| DenseNet121 | classifier | 8.0 | ~0.5 | **11.5 ms** /img | RTX 4070 12GB |
| DermLIP (ViT-B/16) | VL-classifier | 150 | ~2 | (clase clasificador) | RTX 4070 |
| Mini-VLM (Phi-3.5-V) | VLM-gen | 4200 | 10 | **24.1 s** /reporte | A30 / RTX 4080 |
| LLaVA-Med v1.5 (7B) | VLM-gen | 7000 | 14 | **66.1 s** /reporte | A30 24GB |
| SkinVL-MM (7B) | VLM-gen | 7000 | 14 | (perfil de LLaVA-Med) | A30 24GB |

*(Latencia clasificadores: batch=1 en RTX 4070. Latencia VLM: s/reporte de los logs A30, max_tokens≈512.
VRAM de clasificadores: estimación por pesos + overhead. Ver `cost_latency.png`.)*

## Análisis
1. **Brecha de ~3 a 4 órdenes de magnitud:** un clasificador diagnostica en **4–12 ms** con **<1 GB** de
   VRAM en una GPU de consumo (RTX 4070); un VLM generativo tarda **24–66 s por reporte** y exige
   **10–14 GB** (GPU de datacenter, A30). LLaVA-Med (66 s/rep) es ~$6\times10^3$ veces más lento por item
   que ConvNeXt (4 ms).
2. **La tarea determina el costo del hardware:** para la **detección/diagnóstico**, hardware modesto
   alcanza (clasificador o DermLIP, VL-classifier de 150M que corre en la 4070). El costo alto aparece
   solo en la **generación del reporte** (VLM autoregresivo). Es exactamente el eje de la tesina: no hace
   falta un supermodelo para clasificar bien.
3. **Costo del ensamble = clasificador (ms, barato) + generación VLM (domina).** El grounding agrega un
   paso de clasificación despreciable frente al minuto de generación; la cuenta la paga el generador.
4. **Mini-VLM (4.2B) vs LLaVA-Med (7B):** Mini es ~2.7× más rápido (24 vs 66 s/rep) y cabe en 10 GB
   (RTX 4080), a cambio de menor consistencia sin grounding — pero con grounding alcanza al de 7B (ver
   ensamble). Es el candidato "hardware modesto" para generación.

## Cautelas
- VRAM de clasificadores es estimación por pesos (no memoria pico de activaciones). Latencia VLM proviene
  de logs con config ligeramente distinta (max_tokens ≈ 512) — es orden de magnitud, no benchmark pareado.
- DermLIP no se midió local (falta `open_clip` en el entorno); es clase clasificador (~150M, ~ms).

## Conclusión (veredicto)
**CUMPLE.** Comparación sistemática de costo (params, VRAM, latencia) que sustenta cuantitativamente el
eje "resultados vs costo" de la tesina: la clasificación es barata y corre en hardware de consumo; la
generación con VLM es ~1000–15000× más costosa y exige GPU de datacenter. Se integra a
`experimentacion.tex` (tabla de costo + figura + discusión de eficiencia).
