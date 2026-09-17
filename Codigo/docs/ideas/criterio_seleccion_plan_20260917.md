# Plan — Criterio de selección de modelos: F1 macro en validación

**Fecha:** 2026-09-17
**Estado:** ejecutado el 2026-09-17 (TOKO 98243-98246, sin errores). Criterio de éxito cumplido: ver la entrada del 2026-09-17 en `ejecuciones.md`. Queda abierto el anclaje de la cascada, en «Fuera de alcance».
**Origen:** la tensión que quedó abierta en `ejecuciones.md` (entrada 2026-09-15): «por F1 ponderado
en val gana siempre `cwnone`, pero las corridas con pesos por clase llegan a sensM ~0.78 en test.
Decidir el criterio antes de escribir los números finales.»

## Decisión

El **trial ganador se elige por F1 macro en validación**. La **sensibilidad macro sigue siendo la
métrica principal que se reporta en test**.

El F1 ponderado quedó descartado como criterio de selección porque está dominado por NV, que es el
67 % de los datos: premia acertar la clase fácil y excluye sistemáticamente las corridas con pesos
por clase. La sensibilidad macro sola también quedó descartada: ignora los falsos positivos, así
que maximizarla elige modelos que sobre-predicen las clases minoritarias. El F1 macro es el único
de los tres que es balanceado por clase **y** penaliza los falsos positivos.

Evidencia (seed 42, con TTA como todo el barrido, 30 corridas por modelo):

| Criterio en val | Swin ganador | acc | F1m | sensM | MEL |
|---|---|---|---|---|---|
| F1 ponderado (anterior) | t06_les_cwnone | 0.847 | 0.755 | 0.716 | 0.701 |
| Sensibilidad macro | t02_les | 0.728 | 0.611 | 0.752 | 0.671 |
| **F1 macro (elegido)** | **t06_les_cwnone** | 0.847 | 0.755 | 0.716 | 0.701 |

| Criterio en val | ConvNeXt ganador | acc | F1m | sensM | MEL |
|---|---|---|---|---|---|
| F1 ponderado (anterior) | t06_les_cwnone | 0.840 | 0.711 | 0.682 | 0.503 |
| Sensibilidad macro | t07_les | 0.775 | 0.636 | 0.752 | 0.563 |
| **F1 macro (elegido)** | **t02_les_cwnone** | 0.845 | 0.727 | 0.694 | 0.599 |

Con sensibilidad macro sola, Swin perdía 12 puntos de exactitud y 14 de F1 macro. Con F1 macro,
Swin no se mueve y el ConvNeXt nuevo mejora en todas las métricas respecto del anterior, incluida
la exactitud.

## Los dos niveles de selección

Hay dos decisiones distintas que usaban la misma métrica y conviene no confundirlas:

| Nivel | Qué elige | Métrica | Estado |
|---|---|---|---|
| Época dentro de una corrida | El *checkpoint* que se guarda | `val_f1` = F1 **ponderado** (`src/training/trainer.py:188`, `configs/phase1_classification.yaml: monitor: val_f1`) | **Se deja como está** |
| Trial entre corridas | El ganador del barrido | F1 **macro** (`scripts/lesion_split_report.py`) | **Cambiado** |

El nivel de *checkpoint* no se toca porque cambiarlo obliga a **reentrenar las 60 corridas** del
barrido: las predicciones guardadas son las del mejor *checkpoint* de cada corrida y no se puede
re-seleccionar la época a posteriori. El costo no se justifica. Lo que sí hay que hacer es decirlo
con precisión en el documento: hoy `sec:met_protocolo` afirma que el criterio se aplica «también a
la pérdida y al *checkpoint*», y eso es inexacto.

## Cambios ya aplicados

- `scripts/lesion_split_report.py`: selección y ranking por `val.f1_macro` (antes `f1_weighted`);
  *docstring* actualizado.
- `scripts/toko/submit_sweep.py`: *docstring* corregido, que indicaba `val_f1_weighted` como
  criterio para identificar el mejor trial.
- `Docs/TFG/Chapters/03-Materiales-Metodos.tex`: el marcador de `sec:met_protocolo` declara el
  criterio y la distinción entre los dos niveles.
- `scripts/toko/submit_sweep.py`: nueva opción `--eval-hiba` en el camino normal de envío, que
  respeta `--lesion-split`, `--class-weights` y `--seeds`, con sufijo `_hiba` en el nombre del run
  para que quede fuera del ranking del barrido.

## Re-corridas necesarias

Solo cambia ConvNeXt. Swin conserva el ganador y sus tres semillas, así que no se re-corre nada de
Swin.

1. **Semillas 43/44 del ganador nuevo de ConvNeXt** (TOKO, 2 jobs, ~12 h de límite cada uno):

       python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split \
           --class-weights none --trials t02 --seeds 43 44

2. **Validación externa en HIBA** (TOKO, 2 jobs). Hace falta para **los dos** modelos, no solo para
   ConvNeXt: las únicas corridas con HIBA que existían eran `convnext_tiny_sweep_t06_hiba` y
   `swin_tiny_sweep_t08_hiba`, ambas del barrido por imagen. `--rerun-hiba` no sirve, porque
   reentrena sin `--lesion-split` ni `--class-weights`; se agregó `--eval-hiba` al camino normal,
   que respeta las banderas:

       python scripts/toko/submit_sweep.py --model convnext_tiny --lesion-split            --class-weights none --trials t02 --eval-hiba
       python scripts/toko/submit_sweep.py --model swin_tiny --lesion-split            --class-weights none --trials t06 --eval-hiba

3. **Re-derivaciones locales, sin clúster**, una vez bajadas las semillas. Las recalcula
   `scripts/lesion_split_report.py` en la misma corrida: media ± desvío del ganador, detección de
   melanoma con umbral de especificidad ≥ 0.85 fijado en validación, **ensamble** (promedia las
   probabilidades de los dos modelos, así que cambia al cambiar ConvNeXt), calibración y ruteo de
   tres niveles.

## Sincronización con clústeres

- **Subida:** el cambio es de selección, no de entrenamiento, así que el código que corre en el nodo
  no cambia. Igual conviene `python scripts/toko/sync_up.py` antes de enviar, para que el repositorio
  remoto no quede atrás. **Sin `--delete`**: el remoto tiene los *checkpoints* del barrido, que no
  están en local y no hay que borrar.
- **Bajada:** `python scripts/toko/sync_down.py` trae predicciones, métricas y logs. Después
  `python scripts/lesion_split_report.py` **desde `Codigo/`** (el script usa rutas relativas y falla
  si se lo corre desde la raíz del repositorio).
- **Validación local antes de enviar:** no hace falta, porque el trial t02 de ConvNeXt ya corrió con
  semilla 42 en ese mismo entorno. El único riesgo conocido es el *crash* del DataLoader que apareció
  con `class_weights=auto`, y este ganador es `cwnone`.

## Criterio de éxito

Binario: el ganador de ConvNeXt con las tres semillas mantiene el F1 macro en test por encima del
ganador anterior (0.723 ± 0.013 de `t06_les_cwnone`) y no empeora la sensibilidad macro
(0.700 ± 0.018). Si con las semillas 43/44 el nuevo cae por debajo de esos valores, la mejora de la
semilla 42 era ruido y hay que reportar el criterio con el resultado que dé, no revisar el criterio
para que gane.

## Fuera de alcance de este plan

Dos inconsistencias encontradas al revisar esto. La segunda resultó ser un error mío. La primera es
real y se trata aparte de la decisión del criterio:

1. **Varios análisis siguen corriendo sobre los modelos `v3`**, entrenados con la partición
   aleatoria anterior a la partición por lesión: `scripts/robustness_perturbations.py` tiene
   codificados los *checkpoints* `swin_tiny_modern_v3` y `convnext_tiny_modern_v3`, y el ensamble
   que ancla la cascada (`outputs/results/classifier_ensemble/`) usa las predicciones de esos
   mismos modelos.
2. ~~El informe consolidado mezcla números con y sin TTA.~~ **Descartado el 2026-09-17: no era
   cierto.** `train_classifier.py` calcula las predicciones con TTA una sola vez
   (`evaluate_with_tta`, línea 487) y de esa misma inferencia salen `*_predictions.json` y
   `*_test_results.json`; verificado además comparando las métricas de los dos archivos en cinco
   corridas, que coinciden hasta el cuarto decimal. Todo el barrido es con TTA, incluidas las
   predicciones de validación que se usan para seleccionar. El error vino de un script descartable
   que mezclaba los archivos de semillas 43/44 en las filas de la semilla 42.
