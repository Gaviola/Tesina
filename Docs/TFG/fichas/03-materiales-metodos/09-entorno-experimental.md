# Ficha 3.9 — Entorno experimental y recursos computacionales

**Creada el 22/10/2026 por la revisión del tutor del 21/10** (comentarios 6, 28 y 29): reúne el hardware, las semillas y
las bibliotecas que antes estaban en 3.1, 3.3, 3.6 y 3.8. Archivo: `Chapters/03-Materiales-Metodos/09-entorno-experimental.tex`.
Label: `sec:met_entorno`.

## Hilo conductor

Pregunta que responde la sección: ¿en qué hardware y con qué software se ejecutó cada experimento?
Viene de: 3.8 (costo computacional), que remite acá las condiciones de la medición.
Deja instalado: lo necesario para reproducir los experimentos, con remisión al Apéndice E.

```
P1  Tres GPU dentro de la restricción de 3.1: RTX 4080 (TOKO, clasificadores), A30 (Mendieta, ajuste de
    VLM y generación), RTX 4070 (equipo personal, métricas de generación y costo); bf16     función: describe
    ↓ necesidad — 3.8 remite acá las condiciones de la medición del costo
P2  Costo: clasificadores en la RTX 4070 con lotes de 32; generadores con el tiempo por reporte en la A30;
    GPU distintas → solo orden de magnitud                                               función: describe · limita
    ↓ ampliación — el software y las semillas
P3  PyTorch y torchvision, transformers y peft, open_clip, scikit-learn; semilla 42 salvo las réplicas
    43 y 44; Apéndice E                                                                  función: describe
```

Sin versiones de CUDA, W&B ni herramientas internas (regla R1 del autor). Fuentes: `Codigo/CLAUDE.md`,
`Codigo/requirements.txt`, `src/models/*.py`, `scripts/measure_cost.py`.
