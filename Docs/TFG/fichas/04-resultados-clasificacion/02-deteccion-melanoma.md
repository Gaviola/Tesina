# Ficha 4.2 — Detección de melanoma

**Estado (24/10/2026): redactada sin aprobación previa.** El autor pidió escribir el resto del Cap. 4 de una pasada
y revisarlo entero al final (24/10). Las decisiones que se habrían consultado están en «Decisiones tomadas».

Archivo: `Chapters/04-Resultados-Clasificacion/02-deteccion-melanoma.tex`. Label: `sec:res_melanoma`.
Tabla: `tab:res_melanoma`.

## Hilo conductor

Pregunta que responde la sección: ¿cuántos melanomas detecta el clasificador cuando la decisión usa un umbral fijado
en validación, y qué cuesta en falsas alarmas?

Viene de: 4.1 deja la sensibilidad de MEL con argmax como una de las más variables (Swin 0.563–0.701 según la
semilla). Del Cap. 3: la tarea T2 (`sec:met_tareas`), el umbral de mayor sensibilidad con especificidad ≥ 0.850 en
validación y la AUC como resumen (`sec:met_seleccion`), el ensamble (`sec:met_supervisados_ensamble`).
Deja instalado: el punto de operación para melanoma (Swin 0.796 ± 0.036 / 0.862; ensamble 0.828 ± 0.007) y que la
discriminación (AUC) es estable aunque la decisión por argmax no lo sea. 4.3 lo usa como contraste; 4.4 (calibración)
retoma que los umbrales quedan lejos de 0.5.

```
P1  Discriminación: AUC de MEL 0.921 ± 0.005 en Swin, 0.909 ± 0.004 en ConvNeXt, 0.926 ± 0.003 en el ensamble.
    El AUC casi no varía entre semillas, mientras que la sensibilidad con argmax va de 0.563 a 0.701: el modelo
    ordena igual los casos y lo que cambia es dónde cae el corte implícito de la clase más probable  función: interpreta
    ↓ consecuencia: si el orden es estable, fijar el corte en validación debería estabilizar la decisión
P2  Tabla (tab:res_melanoma): argmax frente al umbral de validación. Swin pasa de 0.623 ± 0.071 a 0.796 ± 0.036 de
    sensibilidad y la especificidad baja de 0.944 a 0.862; ConvNeXt de 0.553 a 0.794; ensamble de 0.605 a 0.828.
    La especificidad en la prueba queda entre 0.844 y 0.862 en todas las ejecuciones: el umbral fijado en
    validación se sostiene en la prueba                                                   función: describe
    ↓ ampliación: qué significa en casos, con la ejecución de semilla 42
P3  Semilla 42 de Swin: el umbral 0.211 detecta 130 de 167 melanomas (117 con argmax) a cambio de 185 falsas alarmas
    (104). Los umbrales de las nueve ejecuciones quedan entre 0.109 y 0.211, lejos del 0.5: con una prevalencia de
    0.111, la probabilidad de MEL rara vez supera a la de NV. El ensamble tiene la mayor sensibilidad y el menor
    desvío (0.828 ± 0.007), sin prueba estadística                                       función: interpreta
    ↓ ampliación (literatura)
P4  Literatura (tab:marco_sota_clasificacion): Aboulmira, sensibilidad de MEL 0.49 con la clase más probable, por
    debajo del 0.623 de Swin con argmax; Yao 0.819 en ISIC 2018 (con selección sobre la prueba, Cap. 2); Marchetti,
    96.8 % / 37.4 % y AUC 0.857 sobre lesiones biopsiadas, otro punto de operación y otra población. La comparación
    muestra que el punto de operación cambia la sensibilidad más que el modelo                función: compara / limita
→ Transición a 4.3: con la referencia supervisada fijada para las siete clases y para MEL, la pregunta es si un VLM
  clasifica igual.

Se definen acá: el punto de operación para melanoma.
Se retoman de antes (\ref): T2 (sec:met_tareas), umbral y AUC (sec:met_seleccion), ensamble
(sec:met_supervisados_ensamble), sensibilidad de MEL con argmax (sec:res_supervisados).
Extensión: 4 párrafos y una tabla, ~2 páginas.
```

## Fuentes de cada número

`Codigo/outputs/results/lesion_split_report.json`, claves `melanoma_semillas` (`por_semilla`, `media_std`) y
`melanoma` (semilla 42). Solo Swin-Tiny, ConvNeXt-Tiny y el ensamble tienen la detección con umbral: son los modelos
de la búsqueda y su combinación (3.3).

| Modelo | AUC | Sens. argmax | Esp. argmax | Sens. umbral | Esp. umbral | Umbrales (42/43/44) |
|---|---|---|---|---|---|---|
| Swin-Tiny | 0.921 ± 0.005 | 0.623 ± 0.071 | 0.944 ± 0.022 | 0.796 ± 0.036 | 0.862 ± 0.000 | 0.211 / 0.120 / 0.152 |
| ConvNeXt-Tiny | 0.909 ± 0.004 | 0.553 ± 0.043 | 0.953 ± 0.007 | 0.794 ± 0.012 | 0.854 ± 0.009 | 0.120 / 0.109 / 0.112 |
| Ensamble | 0.926 ± 0.003 | 0.605 ± 0.057 | 0.952 ± 0.012 | 0.828 ± 0.007 | 0.852 ± 0.006 | 0.177 / 0.110 / 0.144 |

Semilla 42, Swin: umbral 0.211, VP 130, FN 37, FP 185 (argmax: VP 117, FN 50, FP 104). Especificidad en la prueba
por ejecución: mínima 0.844 (ConvNeXt, 42), máxima 0.862.

## Claves de cita

Solo para comparar: `aboulmira2024skinhealthmate`, `yao2022single`, `marchetti2023prospective` (valores de
`tab:marco_sota_clasificacion`).

## Decisiones tomadas

- **Sin ViT-B/16 ni DenseNet121**: la detección con umbral se calculó para los modelos de la búsqueda y el ensamble.
  Se dice en una oración.
- **Sin PR-AUC ni VPN**, aunque están en la fuente: el Cap. 3 no las define (`tab:met_roles`).
- **Sin maligno frente a benigno** (C4).
- La diferencia entre Swin y el ensamble se describe, no se prueba (`tab:met_pruebas` no la incluye).
- El umbral bajo se explica por la prevalencia, sin adelantar la calibración (4.4 la retoma).

## Preguntas abiertas

1. ¿Agregar la curva ROC de Swin con los dos puntos de operación? No existe la figura; se puede generar con las
   probabilidades de la semilla 42. Por ahora, la tabla alcanza.

## Revisión del autor (24/10/2026)

- Pregunta 1 resuelta: se agregó `fig:res_roc_melanoma` (`Figures/Capitulos/04-Resultados-Clasificacion/roc-melanoma-swin.pdf`,
  generada con `Codigo/scripts/figura_roc_melanoma.py`), con los dos puntos de operación de la semilla 42. Recalcula
  AUC 0.919, 0.701 / 0.922 y 0.778 / 0.862, iguales a `lesion_split_report.json`.
- Verificación contra `Docs/experimentacion/experimentacion.tex`: coincide con la tabla «Vigente» (Swin 0.921 / 0.796;
  ensamble 0.926 / 0.828). El cuerpo de ese documento usa la partición por imagen y no se toma.
