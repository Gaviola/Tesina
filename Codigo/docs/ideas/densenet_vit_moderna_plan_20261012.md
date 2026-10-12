# Plan — DenseNet121 y ViT-B/16 con la receta moderna (split por lesión)

**Fecha:** 2026-10-12
**Origen:** redacción del Cap. 3 (§3.5). El barrido moderno cubre solo Swin-Tiny y ConvNeXt-Tiny; DenseNet121 y
ViT-B/16 quedaron con la receta legacy. El plan del barrido justificó excluir DenseNet121 por la interacción entre
BatchNorm y el aumento agresivo, pero ese argumento no alcanza a ViT-B/16 (LayerNorm), y la comparación entre los
cuatro modelos mezcla protocolos (receta, TTA, semillas). **Decisión del autor (2026-10-12):** entrenarlos con la
receta moderna en TOKO en vez de declarar la exclusión.

## Hipótesis / pregunta

Con la misma receta, partición y protocolo de semillas que los ganadores, ¿la ventaja de Swin-Tiny y ConvNeXt-Tiny
sobre DenseNet121 y ViT-B/16 (ΔF1m +0.095 y +0.059 frente a legacy) se mantiene, o era en parte un efecto de la
receta? Cualquier resultado es reportable: el objetivo es que los cuatro modelos se comparen en igualdad de
condiciones.

## Diseño

- **Sin barrido propio:** cada modelo toma el trial ganador (F1 macro en validación) de su familia en el barrido del
  split por lesión, sin pesos por clase:
  - DenseNet121 ← ConvNeXt-Tiny **t02** (lr 3.0e-5, wd 0.05, RandAugment m 9).
  - ViT-B/16 ← Swin-Tiny **t06** (lr 7.5e-5, wd 0.10, RandAugment m 6).
- Receta moderna completa (dos etapas, MixUp/CutMix, label smoothing 0.1, 40 épocas, coseno con *warmup* 3, TTA),
  `--focal-gamma 0 --class-weights none`, `--splits-file data/splits/ham10000_splits_lesion.json
  --eval-best-checkpoint --save-val-predictions`. Lote 32 (DenseNet) y 16 (ViT), como en `train_classifier.py`.
- **Semillas 42, 43 y 44** por modelo (6 corridas), igual que los ganadores.
- Envío: `scripts/toko/submit_sweep.py --model {densenet|vit} --lesion-split --class-weights none --trials
  {t02|t06} --seeds 42 43 44`. `--model` acepta ahora `densenet` y `vit`; las corridas
  (`densenet_sweep_t02_les_cwnone[_sNN]`, `vit_sweep_t06_les_cwnone[_sNN]`) no entran en el ranking de
  `lesion_split_report.py`.

## Criterios de éxito / interpretación

- **Completo:** 6 corridas con `*_test_results.json` y predicciones de validación y test.
- **Lectura:** media ± desvío de 3 semillas (acc, F1 macro, sensibilidad macro, recall MEL, AUC macro) junto a los
  ganadores, y McNemar de cada uno frente a Swin (semilla 42), como en `split_lesion_resul` §3.
  - Si Swin y ConvNeXt siguen por encima, la tesina presenta los cuatro con la receta moderna y la conclusión no
    cambia; el legacy queda como antecedente.
  - Si DenseNet o ViT alcanzan a los ganadores, se reporta y se revisa la elección del clasificador de referencia de
    la cascada (Swin), sin cambiarla automáticamente: el Cap. 5 ya está anclado en Swin.
- Hiperparámetros transferidos, no barridos: un resultado peor no prueba que el modelo sea peor, solo que lo es con
  la configuración de su familia. Se declara así.

## Sincronización con clústeres

- No hay jobs corriendo en TOKO.
- El código de entrenamiento remoto es idéntico al local (md5 sin CRLF de `train_classifier.py`,
  `src/models/classifiers.py`, `src/training/recipes.py`); `ham10000_splits_lesion.json` ya está en el clúster.
  `submit_sweep.py` corre local y manda el script por stdin, así que no hace falta `sync_up`.
- **Validación local:** `--dry-run --print-script` antes de enviar. ViT con la receta moderna ya corrió en TOKO
  (job 95116), así que los pesos están en caché.

## Costo estimado

ViT-B/16 moderno: ~20 s por época en la RTX 4080 (job 95116, 6 min en total con detención temprana). DenseNet, del
mismo orden. Total < 2 h de GPU; la cola de TOKO es la que manda.
