# Resultado — Ablaciones imagen-vs-dx y dx-erróneo extendidas a LLaVA-Med y Mini-VLM (P4.1)

**Fecha:** 2026-07-13 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) §6.1 (P4.1) · **Job Mendieta 1160045 (COMPLETED, 6h20m).**
**Feedback:** `mejoras.md` #9 — las ablaciones del ensamble estaban solo sobre SkinVL; extenderlas a los otros generadores para una comparación completa.

## Motivación

En [skinvl_resul](skinvl_resul_20260707.md) se hicieron dos ablaciones **solo sobre SkinVL**:
- **P1.2 imagen-vs-dx:** grounding oracle (dx correcto) pero reemplazando la imagen por una neutra → ¿usa el generador la imagen una vez conocido el diagnóstico?
- **P1.3 dx-erróneo:** inyectar un diagnóstico incorrecto (clase confundible) → ¿corrige el generador el error mirando la imagen, o lo propaga?

La mejora #9 pide replicarlas sobre **LLaVA-Med** y **Mini-VLM** para confirmar que el patrón (la fidelidad la aporta el clasificador, no la visión del generador) no es exclusivo de SkinVL.

## Diseño

- **Modelos:** LLaVA-Med v1.5 y Mini-VLM (checkpoints `stage2_*_v2`), sobre el **mismo subconjunto de 400** imágenes del test split de HAM10000 con el que ya se evaluaron sus condiciones de ensamble.
- **Condiciones nuevas:** `full_oracle_noimage` (`--no_image`, imagen gris neutra) y `full_wrong_swap` (dx swap a clase confundible, `make_wrong_dx.py`). Ambas con `--grounded_prompt --grounded_variant noreasoning`.
- **Métrica:** *diagnostic consistency* (fracción de reportes que mencionan el dx GT o un sinónimo), calculada sobre el conjunto **común** de image_ids a las tres condiciones comparadas (n=400).
- **Nota de proceso:** el job no pasó `--label_csv`, así que `gt_label` salió vacío en los reportes; se parcheó localmente desde `outputs/full_dx_oracle.csv` (image_id → diagnosis). Salida: `outputs/results/ablation_llava_mini_p41.json`.

## Resultados

*Diagnostic consistency* por condición (n=400 común):

| Condición | SkinVL (n=1503) | LLaVA-Med | Mini-VLM |
|-----------|:---:|:---:|:---:|
| baseline (sin grounding) | 0.00 | 0.595 | 0.198 |
| grounding DermLIP (0.38) | — | 0.450 | 0.485 |
| grounding Swin (0.80) | — | 0.710 | 0.830 |
| **oracle (dx correcto, con imagen)** | 1.00 | 0.848 | 1.000 |
| **oracle SIN imagen (P1.2)** | 0.97 | **1.000** | 1.000 |
| **dx-erróneo swap (P1.3)** | 0.11 | 0.070 | 0.065 |

**Ablación P1.2 (imagen-vs-dx), Δ = oracle − oracle_noimage:**

| Modelo | Δ | Lectura |
|--------|:---:|---|
| SkinVL    | **+0.03** | quitar la imagen casi no cambia nada |
| LLaVA-Med | **−0.152** | quitar la imagen **sube** la consistencia: la imagen introduce duda |
| Mini-VLM  | **0.000** | idéntico con y sin imagen |

**Ablación P1.3 (dx-erróneo):** consistencia respecto del GT con un dx incorrecto inyectado: SkinVL **0.11**, LLaVA-Med **0.070**, Mini-VLM **0.065**.

## Análisis

1. **La imagen no aporta fidelidad una vez dado el diagnóstico — en los tres generadores.** El Δ imagen-vs-dx es ≈0 o *negativo*. El caso de LLaVA-Med es el más revelador: con la imagen presente la consistencia es 0.848, pero **sin** la imagen sube a 1.000. Es decir, dado el texto del diagnóstico, el modelo lo nombra siempre; la señal visual, cuando existe, a veces lo hace *dudar* y desviarse. La imagen no agrega valor diagnóstico: en el mejor caso es neutra, en LLaVA-Med resta.
2. **La propagación de error es total y universal.** Con un diagnóstico incorrecto inyectado, la consistencia respecto del GT se derrumba a 0.06–0.11 en los tres modelos: el generador **adopta el diagnóstico equivocado** que le da el clasificador y no lo corrige mirando la imagen. El ensamble hereda exactamente los errores del clasificador.
3. **El patrón de SkinVL se generaliza.** La conclusión de la tesis —*la fidelidad diagnóstica del ensamble proviene del clasificador, no de la visión del generador; el VLM es un transcriptor del diagnóstico a prosa*— se sostiene con los tres generadores, no era un artefacto del colapso de estilo de SkinVL.

## Conclusión (veredicto)

**CUMPLE.** Las dos ablaciones extendidas a LLaVA-Med y Mini-VLM reproducen (y refuerzan) el hallazgo de SkinVL: la imagen es prescindible una vez conocido el diagnóstico (Δ ≈ 0 o negativo) y el error del clasificador se propaga íntegro (consistencia 0.06–0.11 con dx erróneo). Se integra a `experimentacion.tex` §Ablaciones extendiendo la comparación a los tres generadores. Cierra la mejora #9.
