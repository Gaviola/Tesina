# Ficha del Capítulo 2 — Marco teórico

## Estructura vigente: tercera revisión del tutor (2026-10-09)

Este archivo es el contrato vigente del capítulo. El historial de las revisiones anteriores (planes del
28/09, segunda revisión y pasada del autor) está en `historial.md`; lo que de ahí sigue rigiendo está
consolidado abajo, en «Decisiones vigentes». Fuente: `feedback/cap1_2/feedback_cap1_y_2_v3.md`.

### Decisiones del autor (2026-10-10)

| Pedido o duda | Decisión |
|---|---|
| Reestructurar el capítulo en siete secciones (propuesta «IDEA» del tutor) | Se adopta. Los archivos se reorganizan al reescribir cada sección |
| «NO ponga subsecciones» | Se refiere al índice: muestra solo capítulos y secciones (`tocdepth` 1 en `tesina.tex`). Las subsecciones siguen en el texto, numeradas |
| Sección 2.9 (sesgo, robustez y generalización) | Pasa a ser la introducción de la evaluación (2.6); se revisa cómo queda al escribirla |
| Cursiva en *ImageNet* | Todos los nombres de conjuntos de datos van en cursiva (guía §3) |
| Hilo conductor entre secciones | Cada sección se escribe después de leer las anteriores del capítulo y retoma lo que dejaron (guía §1) |

### Hilo del capítulo

Pregunta que responde el capítulo: ¿qué conceptos hacen falta para entender por qué el trabajo compara
clasificadores supervisados y modelos visión–lenguaje, cómo los combina en un *pipeline* que decide cuándo
afirmar un diagnóstico y cómo evalúa el resultado?

```
Intro    Todos los modelos del trabajo son redes neuronales profundas que se entrenan con ejemplos
          ↓ necesidad: entender cómo aprende una red y qué hace que lo aprendido valga fuera del entrenamiento
2.1      Fundamentos: red → clasificación → pérdida → entrenamiento; generalización; transferencia
          ↓ limitación: la red de 2.1 trata la imagen como un vector sin estructura
2.2      Arquitecturas para imágenes: la CNN aprovecha la vecindad de los píxeles; la atención relaciona
         regiones lejanas (ViT); el Swin combina las dos ideas. Son los clasificadores del trabajo
          ↓ limitación: un clasificador devuelve una categoría pero no genera texto
2.3      Lenguaje y visión–lenguaje: el decodificador del transformer genera texto (LLM); LoRA lo adapta en
         una GPU de consumo; CLIP y los VLM generativos conectan imagen y texto
          ↓ limitación: clasificadores y VLM responden siempre, y su puntaje no dice cuánto confiar
2.4      Incertidumbre y predicción selectiva: confianza, calibración, abstención, tres salidas
          ↓ consecuencia: la decisión de cuánto afirmar condiciona un texto, que tiene fallas propias
2.5      Generación de reportes: estructura clínica, estrategias de generación, fallas, recuperación
          ↓ necesidad: categorías, textos y abstenciones se evalúan con métricas distintas, y una métrica
            sobre el test de la misma fuente no garantiza el desempeño fuera de ella
2.6      Evaluación: por qué el test no alcanza (sesgo, robustez, generalización) y métricas de clasificación,
         generación, calibración, robustez e interpretabilidad
          ↓ criterio: con qué datos y protocolo se evaluó un trabajo decide si su resultado se sostiene
2.7      Estado del arte: tres líneas agrupadas, sus limitaciones, y el posicionamiento del trabajo
```

### Secciones, contenido de origen y archivos

| Nueva | Título | Contenido que reúne (numeración actual) | Archivo nuevo | Extensión orientativa |
|---|---|---|---|---|
| 2.1 | Fundamentos del aprendizaje profundo | 2.1 completa, en tres subsecciones: redes neuronales y aprendizaje supervisado (2.1.1 + 2.1.2 actuales), generalización y desafíos del aprendizaje (2.1.3), modelos preentrenados y transferencia (2.1.4) | `01-fundamentos.tex` (se conserva) | 3.5–4 p. |
| 2.2 | Arquitecturas para clasificación de imágenes | 2.2 (CNN, ConvNeXt); de 2.3, la atención, la posición y el bloque, condensados a lo que el ViT necesita; ViT; Swin; la comparación entre familias (2.3.6) | `02-arquitecturas-imagenes.tex` (reúne `02-redes-convolucionales` y `03-transformers`) | 4–5 p. |
| 2.3 | Modelos de lenguaje y modelos visión–lenguaje | 2.4 (LLM, LoRA) y 2.5 (CLIP, VLM generativos, clasificación por verosimilitud) | `03-lenguaje-vlm.tex` (reúne `04-modelos-lenguaje` y `05-vlm`) | 5 p. |
| 2.4 | Incertidumbre y predicción selectiva | 2.6 completa: confianza, calibración, abstención y políticas de decisión | `04-incertidumbre.tex` | 3 p. |
| 2.5 | Generación automática de reportes dermatológicos | 2.7 completa: estructura clínica, calidad descriptiva, fidelidad diagnóstica, estrategias de generación, errores y recuperación | `05-generacion-reportes.tex` | 4–5 p. |
| 2.6 | Evaluación de modelos | 2.9 como introducción; 2.8 (clasificación, generación, calibración, inferencia estadística, robustez, Grad-CAM) | `06-evaluacion.tex` (reúne `08-evaluacion` y `09-sesgo-robustez`) | 6–7 p. |
| 2.7 | Estado del arte | 2.10, con los trabajos agrupados por lo que comparten (guía §3) | `07-estado-arte.tex` | 10–12 p. |

Los archivos se renombran y reúnen en el commit de la sección que los reescribe, y los labels se
conservan (`sec:marco_vision`, `sec:marco_atencion`, `sec:marco_llm`, etc.), porque los usan los Caps. 3–6.
Mientras una sección no se reescribe, conserva su archivo y su número viejo.

### Dónde se define cada concepto

Cada concepto se define una sola vez (guía §3). Las secciones posteriores lo nombran con `\ref`.

| Concepto | Se define en | Se retoma en |
|---|---|---|
| Aprendizaje supervisado, red neuronal, capa, parámetros, activación | 2.1 | 2.2 |
| Clase, *logits*, softmax, confianza como probabilidad | 2.1 | 2.3 (softmax sobre el vocabulario), 2.4 |
| Entropía cruzada | 2.1 | 2.3 (pérdida por *token*), desbalance en 2.1 |
| Descenso del gradiente, retropropagación, Adam, tasa de aprendizaje | 2.1 | 2.3 (memoria de Adam como motivo de LoRA) |
| Generalización, sobreajuste, particiones, fuga de información, cambio de distribución | 2.1 | 2.4, 2.6 |
| Regularización, aumento de datos, TTA | 2.1 | Cap. 3 |
| Desbalance de clases y sus pérdidas | 2.1 | 2.6 (métricas por clase) |
| Preentrenamiento, transferencia, extracción de características, ajuste fino | 2.1 | 2.2, 2.3 (LoRA, *linear probe* de CLIP) |
| *Token*, *embedding*, atención, parche (*patch*) | 2.2 | 2.3 |
| Aprendizaje autosupervisado, LLM, LoRA, CLIP, VLM generativo | 2.3 | 2.4, 2.5 |
| Calibración (concepto), abstención, cobertura | 2.4 | 2.6 (métricas: ECE, curvas) |
| Reporte clínico, alucinación, RAG | 2.5 | 2.6 (métricas de texto) |
| Sesgo, robustez, cambio de dominio | 2.6 | 2.7 |
| Sensibilidad macro, F1 macro y las demás métricas | 2.6 | 2.7 |

### Decisiones vigentes de las revisiones anteriores

Consolidadas el 10/10/2026 a partir del historial (`historial.md`, §9, §13–§15), con la numeración nueva de
las secciones. Lo que no figura acá no rige; las reglas generales de redacción están en la guía y no se
repiten.

1. **Alcance del capítulo.** Solo conceptos. No habla del *pipeline*, de las decisiones del trabajo ni de
   conjuntos concretos: *HAM10000*, su partición y los costos asimétricos de las confusiones van al Cap. 3
   (`sec:met_ham`, `sec:met_seleccion`). Las remisiones al Cap. 3 son del tipo «los detalles están en la
   Sección~…».
2. **Técnicas de entrenamiento** (reemplaza la decisión 7 del 28/09). Toda técnica que usa la receta de
   entrenamiento (`Codigo/src/training/recipes.py`) se explica en 2.1 con una o dos oraciones y su cita.
   Las estrategias de desbalance llevan fórmula porque el Cap. 4 las compara. MixUp y CutMix no se mencionan
   (la receta las desactivó), y la pérdida por número efectivo y la predicción conforme quedan fuera.
3. **Métricas.** Se mantienen todas las que usa la experimentación, incluidas MCE, Wilcoxon, METEOR, CIDEr y
   *vector scaling*. «Sensibilidad macro» es el único nombre, y su definición menciona una vez que también se
   la llama exactitud balanceada. MCE se escribe en línea, sin acrónimo.
4. **Fórmulas verificadas.** Las de atención, LoRA, CLIP, probabilidad de un modelo de lenguaje, temperatura,
   RAG, TPR/FPR y AUC, ECE/MCE, Brier, BLEU, ROUGE-L, METEOR, CIDEr, BERTScore, McNemar, Wilcoxon y Grad-CAM se
   verificaron contra los artículos. Al reescribir, se copian de las ecuaciones existentes y no se reescriben
   a mano. Notación: $C$ clases, $J$ referencias en CIDEr, $M$ intervalos en ECE, $N$ pares en CLIP. Adam y el
   decaimiento de pesos ya no llevan fórmula.
5. **RAG.** La variante del trabajo se presenta como condicionamiento por contexto con recuperación de
   imágenes (kNN), no como el modelo de Lewis.
6. **Incertidumbre y evaluación.** El *hedging* va sin cita: es una falla observada en la experimentación y
   remite al Cap. 5. *Temperature scaling* no cambia la clase predicha y *vector scaling* sí. McNemar se
   presenta en sus dos versiones, y cuál usa el código lo dice el Cap. 3. Grad-CAM se cita con
   `adebayo2018sanity`, porque supera sus pruebas de aleatorización.
7. **Reporte clínico.** Sus dos partes son la descripción y la impresión diagnóstica.
   `kittler2016standardization` respalda el vocabulario, no el formato del informe. 2.5 dice quién escribió
   el texto de referencia, porque eso condiciona su validez, y el detalle va al Cap. 3.
8. **Estado del arte.**
   - Las tablas dicen qué evalúa cada trabajo y con qué hardware, no los valores.
   - DermaSynth son textos sintéticos redactados sobre imágenes reales.
   - El cierre reconoce dos excepciones: Khan et al. y Chakrabarti et al.
   - *DDI* se cita sin cifras de AUC, y Jones y Magalhães, por lo que dicen textualmente.
   - *PH²* y `nvidia2023beginners` no se citan.
   - En *HIBA*, «primer conjunto público» se atribuye a sus autores.
   - Todo número se verifica contra el PDF; `resumen_papers.tex` no es fuente.
9. **Vocabulario.** «*Embedding*», no «embebido». Equivariancia, no invariancia, a traslaciones en el ViT. Sin
   palabras rebuscadas («exéresis», «glosa»). RNN y LSTM no aparecen.
10. **Figuras y tablas.**
    - Se mantienen la del perceptrón y la del ViT en TikZ.
    - La antigua Figura 1.1 (`planteo-problema.tex`) va en 2.5.
    - `mapa-capitulo.tex` no se usa en el capítulo; queda para evaluar si sirve en el Cap. 3.
    - Hay que separar las etiquetas de la figura de la convolución (tutor, p36).
    - Encabezados de tabla en negrita.
11. **Introducción del capítulo.** Se reescribe al final con la estructura nueva, en el estilo del texto que
    propuso el tutor en la segunda revisión (`historial.md`, §14).

### Datos ya verificados

Ya se comprobaron contra la fuente. Si se usan, se copian; no se vuelven a verificar:
- Dosovitskiy: escala de preentrenamiento de 14 a 300 millones de imágenes.
- Guo: calibración de redes anchas y profundas.
- Adebayo: Grad-CAM supera las pruebas de aleatorización.
- Holtzman: *beam search* sigue siendo la opción para la generación dirigida.
- Jones: 272 estudios, solo dos con poblaciones no derivadas.
- Groh 2024: 389 dermatólogos y 459 médicos de atención primaria. Según la ficha del 28/09, «el apoyo mejora más de un tercio la exactitud y amplía la diferencia entre tonos de piel en atención primaria»; releer antes de usarlo.

### Orden de trabajo

2.1 → 2.2 → … → 2.7, de a una, cada una con su ficha y su hilo aprobados antes de redactar (guía §1).
La introducción del capítulo (`00-capitulo.tex`) se reescribe al final, cuando la estructura esté cerrada.
