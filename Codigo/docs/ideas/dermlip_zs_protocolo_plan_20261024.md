# Plan — DermLIP zero-shot con el protocolo oficial (24/10/2026)

## Motivación

Al verificar la Tabla 4.13 de la tesina contra Derm1M (Yan et al., ICCV 2025, Tabla 2), DermLIP ViT-B/16 informa una
exactitud zero-shot de 0.682 en HAM10000; este trabajo obtiene 0.377 sobre la prueba por lesión (1 503 imágenes). El
código oficial (`SiyuanYan1/Derm1M`, `src/open_clip/zero_shot_metadata.py` y `src/open_clip_train/zero_shot.py`)
difiere del nuestro (`src/models/dermlip.py`, `scripts/eval_dermlip_classify.py`) en:

| | Oficial | Este trabajo |
|---|---|---|
| Plantillas | 8 (`OPENAI_SKIN_TEMPLATES`) | 4 (`DEFAULT_TEMPLATES`; solo la primera coincide) |
| Nombres de clase | «nevus», «vascular» | «melanocytic nevus», «vascular lesion» (las otras 5 iguales) |
| Prueba | `data/meta/HAM-ZS.csv` (Google Drive, partición no documentada) | partición por lesión, 1 503 |

## Hipótesis

H1: con las plantillas y los nombres oficiales, la exactitud sobre nuestra prueba sube hacia la que informan los
autores. Si sube poco, la diferencia se atribuye al conjunto de prueba, que no puede replicarse.

## Experimento (local, sin jobs)

`scripts/dermlip_zs_protocolo.py`: embeddings de imagen una sola vez y cuatro clasificadores de texto (plantillas
nuestras u oficiales × nombres nuestros u oficiales). Métricas: exactitud, sensibilidad macro, F1 macro, clase más
predicha. Salida nueva: `outputs/results/dermlip/dermlip_zs_protocolo.json` (no sobrescribe nada). La combinación
«nuestras × nuestros» debe reproducir 0.377 / 0.510 como control.

## Veredicto binario

CUMPLE si la combinación oficial llega a ≥ 0.60 de exactitud (la diferencia es de protocolo y la tesina debe usar la
cifra oficial); NO CUMPLE si queda < 0.50 (la diferencia es del conjunto de prueba, y la tesina lo dice así).

## Sincronización con clústeres

No aplica: corre en local (RTX 4070, `.venv` de la raíz) sobre `data/processed/HAM10000` y
`data/splits/ham10000_splits.json`, que no cambian. No hay `sync_up` ni `--delete`.
