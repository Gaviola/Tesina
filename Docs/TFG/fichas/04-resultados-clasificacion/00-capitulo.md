# Ficha del Capítulo 4 — Resultados: clasificación diagnóstica y detección de melanoma

**Estado (18/10/2026): borrador para aprobar.** Contrato del capítulo. Ninguna sección se redacta hasta que el
autor apruebe esta ficha y la ficha de la sección (guía §1).

Sale de: la ficha de referencia del 26/09 (`fichas/04-resultados-clasificacion.md` en la rama
`doc/cap04-resultados-clasificacion`, sin aprobar), puesta al día con el Cap. 3 ya redactado y con las decisiones
posteriores (12/10 y 17/10). Lo que cambia respecto de esa ficha está en «Cambios respecto de la ficha del 26/09».

## Hilo del capítulo

Pregunta que responde el capítulo: ¿puede un VLM clasificar una lesión dermatoscópica en las siete clases de
*HAM10000* tan bien como un clasificador supervisado, y qué explica que los VLM generales no lo logren? (PI1, OE1,
y la parte del OE3 que toca a la clasificación: población externa, perturbaciones, calibración.)

Viene de: el Cap. 3 deja el protocolo completo: métricas, selección y pruebas en `sec:met_protocolo` (3.3),
configuración de los modelos en 3.4–3.6 y los análisis en otros escenarios en `sec:met_complementarios` (3.8), cuya
última oración remite a este capítulo.
Deja instalado: el clasificador de referencia (Swin-Tiny) y la conclusión de que un VLM general no aporta el
diagnóstico. El Cap. 5 los usa para justificar la cascada.

```
Intro    Qué responde el capítulo (PI1), qué hipótesis contrasta; todo número sale de la partición por lesión,
         se elige en validación y se reporta en test (media ± sd cuando hay tres semillas)
          ↓ necesidad: antes de juzgar a un VLM hace falta saber cuánto rinde un clasificador supervisado
4.1      Clasificadores supervisados: el ganador en validación, los cuatro con el mismo procedimiento, recall
         por clase y dispersión, ensamble, desbalance y efecto de la fuga
          ↓ contraste: con esa referencia, ¿clasifica igual un VLM médico general?
4.2      VLM generales: cuatro estrategias, sensibilidad macro en el nivel del azar, colapso hacia una o dos
         clases. H1 refutada
          ↓ necesidad: explicar el colapso antes de buscar una salida
4.3      Re-diagnóstico: no es el desbalance (H3 refutada); prior del lenguaje (imagen gris)
          ↓ consecuencia: si el problema es la falta de dominio, probar un modelo del dominio
4.4      DermLIP: zero-shot, cabezas sobre embeddings congelados y control con Swin-ImageNet. H4 sostenida
          ↓ necesidad: ubicar estos números frente a la literatura
4.5      Estado del arte: comparación acotada por diferencias de protocolo
          ↓ necesidad: decir qué diferencias son reales y si las probabilidades sirven para decidir
4.6      Calibración y significancia: ECE con y sin pesos por clase; McNemar con Holm (21 pares) y bootstrap
          ↓ necesidad: el test es de la misma fuente; ¿se sostiene fuera de ella?
4.7      Robustez: HIBA y perturbaciones
          ↓ ampliación: además de cuánto acierta, ¿dónde mira?
4.8      Interpretabilidad: Grad-CAM de Swin
          ↓ aplicación: la clase de mayor costo clínico, como tarea binaria
4.9      Detección de melanoma: AUC, punto de operación fijado en validación, comparación con la literatura
          ↓ cierre
4.10     Discusión: balance de hipótesis; por qué el diagnóstico del pipeline viene del clasificador
→ Cap. 5: un generador que no discrimina necesita que el diagnóstico venga de afuera.
```

## Secciones, estado de las fuentes y archivos

| Sec. | Título | Archivo | Label | Ext. | Fuentes | ¿Se puede escribir? |
|---|---|---|---|---|---|---|
| Intro | — | `00-capitulo.tex` | `cp:res_clasif` | 0.5 p. | — | Sí |
| 4.1 | Clasificadores supervisados | `01-clasificadores-supervisados.tex` | `sec:res_supervisados` | 5 p. | `split_lesion_resul_20260926.md`, `densenet_vit_moderna_resul_20261017.md` | **Sí** (ficha lista para aprobar) |
| 4.2 | VLM generales | `02-vlm-generales.tex` | `sec:res_vlm_generales` | 3 p. | `vlm_clasificacion_resul_v3_20260517.md`, `statistical_tests_les_v2.json` | **En parte.** Faltan las filas de Mini-VLM ajustado (v3: jobs 1179988 y 1179989, en cola; inicio estimado 20/10). Las de *zero-shot* y LLaVA-Med no cambian |
| 4.3 | Re-diagnóstico del colapso | `03-rediagnostico-colapso.tex` | `sec:res_rediagnostico` | 3 p. | `vlm_domain_gap_clinica_resul_20260604.md`, `prior_lenguaje_noimage_resul_20260824.md` (modelos base, *zero-shot*) | Sí |
| 4.4 | Especialización de dominio | `04-especializacion-dominio.tex` | `sec:res_dermlip` | 3.5 p. | `dermlip_split_eval.json`, `embeddings_classical_les.json`, `classification_summary_les.png` | Sí; la figura por enfoque se regenera cuando esté Mini-VLM v3 |
| 4.5 | Estado del arte | `05-comparacion-sota.tex` | `sec:res_sota_clasif` | 2 p. | `tablas_comparativas_sota_v34.tex` | Sí |
| 4.6 | Calibración y significancia | `06-calibracion-significancia.tex` | `sec:res_calib_stats` | 2.5 p. | `lesion_split_report.json` (`calibracion`), `calibration_les/`, `statistical_tests_les_v2.json`, `densenet_vit_moderna_report.json` | Sí; la familia de 21 pares incluye Mini-VLM ZS, que no cambia con v3 |
| 4.7 | Robustez | `07-robustez.tex` | `sec:res_robustez` | 3 p. | `lesion_split_report.json`, `robustness_summary.json`, `robustness_examples_les.png` | Sí |
| 4.8 | Interpretabilidad | `08-interpretabilidad.tex` | `sec:res_interpretabilidad` | 1–1.5 p. | `interpretability_les/interpretability_swin.png` | Sí |
| 4.9 | Detección de melanoma | `09-deteccion-melanoma.tex` | `sec:res_melanoma` | 2–3 p. | `lesion_split_report.json` (`melanoma_semillas`) | Sí |
| 4.10 | Discusión | `10-discusion.tex` | `sec:res_clasif_discusion` | 1–1.5 p. | secciones anteriores | Al final |

Total orientativo: 24–26 páginas.

## Cambios respecto de la ficha del 26/09

| # | Cambio | Motivo |
|---|---|---|
| C1 | DenseNet121 y ViT-B/16 entran a 4.1 **con la configuración de su familia y tres semillas**. Las corridas con la receta anterior no aparecen en el capítulo (revisión del autor del 18/10, D-B y R2 de la ficha del Cap. 3); sus números siguen en `densenet_vit_moderna_resul_20261017.md` §4 | Decisión del 12/10; TOKO 99007–99012 |
| C2 | La conclusión «Swin y ConvNeXt superan a DenseNet y ViT» pasa a «con el mismo procedimiento, ViT-B/16 empata con Swin y ConvNeXt, y DenseNet121 queda abajo en F1 macro y sensibilidad macro (bootstrap), sin diferencia en McNemar con Holm» | ídem, §5 |
| C3 | Se quita Wilcoxon de 4.6. El recall por clase se compara de forma descriptiva, contando en cuántas clases mejora cada modelo, y McNemar se corrige con Holm sobre 21 pares | Decisión del 12/10; así lo fija 3.3 (`sec:met_estadistica`) |
| C4 | Se quita maligno-vs-benigno de 4.9 | Decisión del 12/10 («sin maligno/benigno»); 3.1 define la detección solo como MEL frente al resto |
| C5 | 4.2: **los VLM generales no se ajustaron sobre *HAM10000***. La estrategia «ajuste fino» evalúa el *checkpoint* de generación de la etapa 2, entrenado con *SkinCaRe*. No hay fuga que declarar; la nota «Declarar» de la ficha vieja era falsa | Corrección del 11/10 (ficha 3.0, punto 6) |
| C6 | 4.2: Mini-VLM ajustado se reporta con **v3** (LoRA sobre el modelo de lenguaje). El *checkpoint* v2 tenía el adaptador solo en CLIP; el texto de 3.6 describe solo la configuración v3 | Decisión del 12/10; job 1179985 completo el 18/10 |
| C7 | 4.6: con la familia nueva, 15 de 21 pares son significativos con Holm, todos los que incluyen un modelo *zero-shot*; ningún par entre supervisados lo es | `densenet_vit_moderna_resul_20261017.md` §3 |
| C8 | Las fichas pasan a una por sección (`fichas/04-resultados-clasificacion/NN-seccion.md`) | Guía §1, desde el 10/10 |
| C9 | Rigen las reglas R1–R5 de la revisión del Cap. 3 (18/10): sin fechas, revisiones del tutor ni iteraciones viejas; solo resultados finales con su justificación; teoría y método se nombran con `\ref` | Pedido del autor: valen también para los Caps. 4 y 5 |

## Alcance y decisiones heredadas

1. **Fuente única: la partición disjunta por lesión.** La partición aleatoria aparece solo en 4.1 (efecto de la
   fuga) y en 4.4 (inflación de los métodos locales sobre DermLIP). `experimentacion.tex` sirve para el argumento,
   no para los números.
2. **El Cap. 4 no explica cómo se obtuvo nada.** Receta, barrido, umbral, protocolo de cada número y pruebas se
   nombran con `\ref` al Cap. 3 (las tablas de protocolo por resultado se quitaron en la revisión del 18/10; si un
   número necesita su regla, se dice en una oración con `\ref` a la sección del Cap. 3 que la define).
3. **Media ± sd de tres semillas** cuando existen (los cuatro supervisados y el ensamble). Desbalance y VLM
   tienen una semilla y se reportan sin desvío.
4. **Selección en validación, lectura en test.** Ninguna conclusión elige un modelo mirando el test; cuando un
   número de test motivó algo, ya está declarado una vez en 3.3 (`sec:met_seleccion`) y no se repite.
5. **Swin-Tiny es el clasificador de referencia** (confirmado por el autor el 17/10): mejor F1 macro en validación,
   un tercio de los parámetros de ViT-B/16 y la cascada ya anclada en él. El ensamble sigue siendo Swin + ConvNeXt.
6. **Terminología** (guía §4): «exactitud», no «precisión»; «reporte» solo para el informe clínico; decimales con
   punto.

## Pendientes de experimentación que tocan al capítulo

| Qué | Para | Estado |
|---|---|---|
| Clasificación de Mini-VLM v3 por verosimilitud y CoT | 4.2 (filas de ajuste fino), figura por enfoque de 4.4 | Mendieta 1179988–1179989, en cola |
| Ablaciones de la receta (sin MixUp, sin RandAugment, sin focal, etc.) | — | **Resuelto (18/10):** sin resultados ni local ni en TOKO; se quitó de 3.4 la oración que las prometía (D-E de la ficha del Cap. 3). No van al Cap. 4 |

## Preguntas abiertas

1. **Extensión:** ¿24–26 páginas o las 25–30 de la guía?
2. ~~Ablaciones de la receta~~ (resuelta el 18/10: se quitaron de 3.4).
