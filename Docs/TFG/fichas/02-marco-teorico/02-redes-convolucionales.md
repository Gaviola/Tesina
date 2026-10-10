# Ficha 2.2 — Redes convolucionales

Sección del `.tex`: `Chapters/02-Marco-Teorico/02-redes-convolucionales.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.3 Aprendizaje profundo para clasificación visual — `sec:marco_vision`

**Mensaje central.** Dos familias de arquitectura, convolucionales y transformers visuales, resuelven la
clasificación de imágenes y son la referencia contra la que se evalúa el desempeño de los modelos
multimodales.

**Razón de ser.** Sin conocer las dos familias no se entiende la comparación central del trabajo ni por qué un
VLM tiene que superarlas para justificarse. **Extensión: 3,5 páginas.**

**Apertura.** Se elimina «El primer componente del pipeline recibe la imagen…» (l. 244–250) y las remisiones a
DenseNet, ConvNeXt y `cp:res_clasif`. Se abre diciendo qué problema resuelven estas familias (clasificar una
imagen en una de $C$ categorías: entrada imagen, salida $p_c$) y qué se necesita de una arquitectura para ello.

| Subsección | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| 2.3.1 Redes convolucionales — `sec:marco_cnn` | l. 255–282; `fig:marco_convolucion`, VGG, ResNet, DenseNet, ConvNeXt | **Se recorta** en DenseNet la mención a «conjuntos del orden de diez mil imágenes, como HAM10000» (l. 274) y en ConvNeXt «En el comparativo, ConvNeXt representa…» (l. 280–282): son decisiones propias (Cap. 3) | Una oración: las conexiones residuales permiten entrenar redes muy profundas (retoma el gradiente de 2.1.3); ya está en l. 190–191 |
| 2.3.2 Vision Transformer y Swin Transformer — `sec:marco_vit` | l. 287–311; `fig:marco_vit_patches`, `fig:marco_swin` | Se quita el *embedding* del ViT (pasa a 2.2). Se mantiene la escala del preentrenamiento como variable (l. 297–302) | — |
| 2.3.3 CNN y transformers visuales como referencia de comparación — `sec:marco_baseline_visual` | — | — | **Nuevo, 2–3 párrafos (F5, A9).** Ver abajo |

### 2.3.3 (F5, A9) — ideas

1. **Qué es una línea base** (*baseline*): una arquitectura de referencia con protocolo fijo contra la que
   se mide otra. Definición general, sin nombres del trabajo.
2. **Por qué CNN y ViT lo son.** Son las arquitecturas establecidas para clasificar imágenes, con recetas de
   entrenamiento maduras y supervisión completa; un modelo multimodal solo justifica su costo si supera a
   estas referencias o si aporta algo que ellas no pueden (texto, explicación, uso sin ajuste). Los
   codificadores visuales de los VLM son a su vez ViT (por eso las dos familias se explican antes).
3. **Qué hace comparable una comparación**: mismos datos, misma partición y mismas métricas; y diferencia
   entre comparar arquitecturas (2.3.1 frente a 2.3.2) y comparar familias de modelos (supervisados frente a
   VLM), que es lo que interesa. Cita: `dosovitskiy2021image`, `liu2022convnet` (el caso de ConvNeXt como CNN
   contemporánea del ViT, l. 277–282: es hecho de la literatura y se puede conservar).

**Párrafo de transición a 2.4 (C4).** El clasificador entrega una probabilidad por clase y ningún texto.
Producir un texto exige un modelo que genere secuencias. El mismo transformer, usado como decodificador,
lo hace (2.4). Se elimina «Con esto el clasificador queda completo» (l. 342) por ser la fórmula del *pipeline*.
**Citas:** `lecun1998gradient`, `simonyan2015very`, `he2015residual`, `huang2018densely`, `liu2022convnet`,
`dosovitskiy2021image`, `liu2021swin`, `vaswani2017attention`; `tan2020efficientnet` solo si se lo nombra.
