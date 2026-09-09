# Plan — Test directo del "prior del lenguaje" (P(clase | prompt) sin imagen)

**Fecha:** 2026-08-23 · **Cluster:** TOKO (RTX 4080, cola corta) · **Ítem:** #2 del cierre de experimentación.

## Motivación

El documento (`sec:rediag`) sostiene como **conjetura** que el bajo desempeño de los VLM generales en
clasificación dermatológica se debe a que sus predicciones están guiadas por el **prior del lenguaje**
(qué clase es más "esperable" dado el prompt) más que por el contenido visual. Un revisor señaló que el
**test directo** de esa conjetura es medir $P(\text{clase} \mid \text{prompt})$ **sin imagen**. Si el VLM,
privado de información visual, sigue prediciendo (y colapsa a una clase), queda demostrado que el prompt/
prior domina sobre la imagen. Hoy la afirmación está suavizada a "sugiere… queda como trabajo futuro"; este
experimento la convierte en evidencia directa.

## Diseño experimental

- **Modelos:** Mini-VLM (Phi-3.5-vision, 4.2B) y LLaVA-Med v1.5 (7B), zero-shot (sin fine-tuning).
- **Método:** likelihood scoring existente (`vlm_scoring.score_image`, ensemble de 4 prompts, sinónimos),
  idéntico al de `tab:clasificacion`, pero **reemplazando cada imagen por una imagen gris neutra**
  (224×224, RGB 128) mediante el nuevo flag `--no_image`. Se mantiene un tensor de imagen válido (Mini-VLM
  exige tokens de imagen), pero **sin contenido visual**, aislando el prior del lenguaje.
- **Datos:** HAM10000 test completo (1503) para comparabilidad directa con la corrida con-imagen.
- **Salidas:** `outputs/results/{model}/mini_vlm_likelihood_noimage_predictions.json` y
  `llava_med_likelihood_noimage_predictions.json` (+ `_test_results.json`).

## Criterios de éxito / interpretación

- **Confirma la conjetura si:** sin imagen el modelo (a) sigue emitiendo una clase (no se abstiene) y
  (b) su distribución de predicciones **colapsa** a una/pocas clases, con exactitud ≈ la de la corrida
  con-imagen (o cercana a la prevalencia de la clase mayoritaria). Es decir, quitar la imagen **no** degrada
  sustancialmente la (ya pobre) discriminación → el prompt domina.
- **Refuta / matiza si:** la exactitud cae marcadamente al quitar la imagen → el modelo sí usaba señal
  visual y la conjetura debe reformularse.

## Ejecución (TOKO)

```bash
python scripts/toko/sync_up.py
python scripts/toko/submit.py classify_mini_noimg     # Mini-VLM, likelihood, --no_image
python scripts/toko/submit.py classify_llava_noimg    # LLaVA-Med, likelihood, --no_image
python scripts/toko/monitor.py
python scripts/toko/sync_down.py
```

## Sincronización con clústeres

- **sync_up** del código modificado (`train_vlm_classify.py` con `--no_image`, scripts SLURM con
  `EXTRA_ARGS`, aliases en `submit.py`) antes de enviar. No requiere `--delete` (no se borran archivos).
- Datos HAM10000 y pesos de los VLM ya están cacheados en TOKO (se usaron para `tab:clasificacion`).
- **Validación local imposible:** el `.venv` local es torch CPU-only; el test corre solo en cluster.
  El flag y la lógica se verifican por syntax-check (`py_compile`) antes del envío.
- **sync_down** de `outputs/results/*/*_noimage_*.json` al terminar; análisis y `resul` local.

## Costo estimado

Igual a la corrida likelihood con-imagen (mismo nº de forward passes): ~1–2 h en RTX 4080 por modelo,
holgadamente dentro del límite de 8 h de TOKO. Cola corta.
