# Resultado — Test directo del "prior del lenguaje" (P(clase | prompt) sin imagen)

**Fecha:** 2026-08-24 · **Plan:** [prior_lenguaje_noimage_plan](../ideas/prior_lenguaje_noimage_plan_20260823.md)
· **Jobs:** TOKO 97463 (Mini-VLM), 97464 (LLaVA-Med) · **Ítem:** #2 del cierre de experimentación.

## Motivación

Probar de forma **directa** la conjetura de `sec:rediag`: que las predicciones de los VLM generales están
guiadas por el prior del lenguaje más que por el contenido visual. Se mide $P(\text{clase} \mid \text{prompt})$
reemplazando cada imagen por una **gris neutra** (sin contenido visual), con el mismo likelihood scoring de
`tab:clasificacion`.

## Diseño

- Likelihood scoring (ensemble de 4 prompts + sinónimos), HAM10000 test completo ($n=1503$), zero-shot.
- Flag `--no_image` (imagen gris 224×224 RGB 128). Se mantiene un tensor de imagen válido (Mini-VLM exige
  tokens de imagen) pero sin información visual.
- Comparación contra la corrida **con imagen** ya existente (`outputs/results/{model}/v1/*_likelihood_predictions.json`).

## Resultados

| Modelo | Condición | Exactitud | Clases distintas predichas | Distribución de predicciones |
|---|---|---|---|---|
| Mini-VLM | con imagen | 0.189 | 2 / 7 | DF 78 %, NV 22 % |
| Mini-VLM | **sin imagen** | 0.111 | **1 / 7** | **MEL 100 %** |
| LLaVA-Med | con imagen | 0.037 | 5 / 7 | VASC 36 %, DF 35 %, BCC 18 %, MEL 9 %, NV 1 % |
| LLaVA-Med | **sin imagen** | 0.011 | **1 / 7** | **DF 100 %** |

- Sin imagen, **ambos modelos colapsan al 100 % en una única clase fija** (Mini→MEL, LLaVA→DF) y **nunca se
  abstienen**: emiten una clase con aplomo aun sin ninguna evidencia visual. La exactitud iguala exactamente
  la prevalencia de esa clase (MEL $\approx 0.11$, DF $\approx 0.01$), es decir, aciertan solo por azar de
  base.
- La clase de colapso **depende del modelo** (MEL vs DF), consistente con un default determinado por el
  prompt/pesos del lenguaje, no por la imagen.
- Con imagen, las predicciones se **dispersan levemente** (Mini 1→2 clases, $+0.078$ de exactitud; LLaVA
  1→5 clases) pero siguen fuertemente sesgadas y con exactitud muy por debajo de un clasificador útil.

## Conclusión (veredicto)

**CUMPLE — confirma la conjetura, con matiz.** El test directo demuestra que los VLM generales, privados de
la imagen, siguen prediciendo y **colapsan a una clase fija**: existe un prior de lenguaje dominante. La
imagen aporta señal (desplaza y dispersa algo las predicciones), pero **demasiado débil para discriminar**:
el prior pesa más que el contenido visual. Esto sostiene la afirmación de `sec:rediag`, que puede pasar de
"conjetura / trabajo futuro" a **resultado directo**.

**Alcance / cautelas:** es una condición controlada (imagen neutra como ablación del canal visual); mide el
sesgo del default, no que la imagen sea completamente ignorada (con imagen sí hay dispersión). No cambia
ninguna conclusión previa: refuerza el argumento de que la clasificación requiere un modelo especializado.

## Aplicado al documento

`sec:rediag`: la conjetura del prior del lenguaje se reescribe como resultado directo con estos números
(colapso 100 % a una clase sin imagen; dispersión leve con imagen). Se elimina el "queda como trabajo futuro".
