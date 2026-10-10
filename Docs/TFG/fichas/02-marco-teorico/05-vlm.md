# Ficha 2.5 — Modelos visión–lenguaje

Sección del `.tex`: `Chapters/02-Marco-Teorico/05-vlm.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.5 Modelos visión–lenguaje — `sec:marco_vlm`

**Mensaje central.** Hay dos formas de unir imagen y texto: alinearlos en un espacio común (contrastivo) o
inyectar la imagen en un LLM (generativo). La primera permite clasificar y recuperar, la segunda redactar.

**Razón de ser.** Dos de los tres mecanismos de 2.6 (recuperación de imágenes y clasificación *zero-shot*)
descansan en el espacio contrastivo; el generador descansa en el esquema generativo. **Extensión: 3,5
páginas.**

**Apertura.** Se elimina «El *pipeline* usa las dos» y la mención a DermLIP como componente (l. 446–451). Se
abre con la definición de VLM y las dos formas de construirlo.

| Subsección | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| 2.5.1 Alineación contrastiva: CLIP — `sec:marco_vlm_clip` | l. 456–483; `fig:marco_clip` | **Se elimina** «Los dos modos reaparecen en el trabajo, y el segundo es además el mecanismo de recuperación de la Sección…» (l. 475–476) y «Por eso el *pipeline* usa un modelo contrastivo especializado y no el CLIP original» (l. 482–483). Se conserva `yan2025derm1m` como ejemplo de preentrenamiento de dominio | **Similitud coseno** (traída de l. 583–585 de RAG): $\cos(\mathbf{u},\mathbf{v})=\mathbf{u}^\top\mathbf{v}/(\lVert\mathbf{u}\rVert\lVert\mathbf{v}\rVert)$, con su lectura: con vectores normalizados coincide con el producto interno. Definición de *kNN* como concepto (los $k$ vecinos más cercanos en el espacio de *embeddings*) |
| 2.5.2 Modelos multimodales generativos — `sec:marco_vlm_generativos` | l. 488–516; `fig:marco_llava`, LLaVA, BLIP-2, ajuste en dos etapas, LLaVA-Med, SkinVL, Phi-3 | **Se recorta** l. 514–516 («A ese tamaño, el ajuste con LoRA… cabe en una GPU de consumo. Los generadores que compara el trabajo son variantes de este mismo diseño») | — |

**Párrafo de transición a 2.6.** Un VLM generativo produce texto, pero no cualquier texto sirve como reporte
clínico. Qué se espera de un reporte, qué puede fallar y qué información adicional puede darle al modelo
para fallar menos es el tema de 2.6.
**Citas:** `radford2021learning`, `yan2025derm1m`, `liu2023visual`, `li2023blip2`, `li2023llavamed`,
`zeng2025mmskin`, `abdin2024phi3`, `zhou2023skingpt4` solo si se nombra un VLM dermatológico más.
