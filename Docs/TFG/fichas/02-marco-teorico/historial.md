# Ficha del Capítulo 2 — Historial

Registro de los planes y decisiones de las revisiones del 28/09, 05/10 y 08/10/2026. **No rige**: lo vigente
está en `00-capitulo.md`. Las numeraciones de sección y las líneas citadas son las de cada momento.

Contrato de contenido de la nueva versión del capítulo. Reemplaza a la ficha anterior, cuyas decisiones y
verificaciones vigentes se conservan en la sección 9. **Nada de esto se redacta hasta que el autor apruebe
la ficha.** Fuentes de la revisión: `tareas_revision_cap1-2.md` (códigos C1–C6, F1–F5, G1–G4, E1, S1–S6, T2,
D3, M1, M4) y `feedback/feedback_cap1_y_2.md` (A1–A16, M2.1, p27–p60).

**Estado del `.tex` actual** (`Chapters/02-Marco-Teorico.tex`, 1145 líneas, páginas 9–38 del PDF: 30 páginas).
Las líneas y páginas que se citan abajo son de esa versión.

**Alcance de esta ficha.** Solo el plan. No se toca ningún `.tex`, `.bib` ni `refs_pendientes.md`. El
contenido de S3 (trabajos nuevos del estado del arte) lo prepara otra persona: en cada eje de §2.10 queda un
lugar marcado como «trabajos nuevos: pendiente de S3».

---

## 0. Índice del plan

1. Revisión del tutor (2026-09-28): qué cambia y por qué
2. Criterio de redacción del capítulo (T2)
3. Estructura nueva, longitudes y mapa de secciones
4. Introducción del capítulo (sin figura)
5. Plan por sección, 2.1 a 2.10
6. Corrección de RAG (G3)
7. Mapa de labels viejos → nuevos (M4)
8. Figuras y tablas
9. Decisiones vigentes (conservadas de la ficha anterior)
10. Referencias a proponer en `refs_pendientes.md`
11. Preguntas para el autor
12. Defectos detectados en el `.tex` actual

---

## 1. Revisión del tutor (2026-09-28)

| Código | Qué pidió el tutor | Qué cambia en el capítulo | Sección |
|---|---|---|---|
| M2.1, D3, C1 | Diez secciones con nombres fijos | Se adopta la estructura de 10 secciones. Los cinco bloques A/B/C de la ficha anterior se reparten en ellas | todas |
| p35, C2 | La intro habla del contenido, no de detalles técnicos ni de figuras | Se reescribe la intro sin `fig:marco_mapa` y sin el recorrido de un ejemplo por el *pipeline* | §4 |
| p59, A11 | El marco no se presenta sobre el pipeline sino con los conceptos que lo sostienen | Se elimina el hilo «recorrido del pipeline»; cada sección abre y cierra con los conceptos, no con «el primer componente del pipeline…» | todas |
| p35, C3 | 2.1 abre directo en aprendizaje profundo | Se elimina el párrafo «Esta sección presenta cómo una red neuronal produce…» | 2.1 |
| A5, C5 | Reducir el MLP, eliminar las recurrentes; conservar ecuaciones y definiciones necesarias | MLP a una ecuación y una idea; RNN y LSTM salen (`sec:marco_familias` se disuelve) | 2.1 |
| A6, C6 | 2.1.5 resumida en uno o dos párrafos de transición hacia CNN y Transformers | El gradiente que se desvanece pasa a `sec:marco_entrenamiento`; el resto queda en un párrafo de cierre de 2.1 | 2.1 |
| A5, F1, F2 | Transferencia de aprendizaje y ajuste fino, más desarrollados | Subsección nueva `sec:marco_transferencia` en 2.1, separada del desbalance. Se conecta con LoRA en 2.4 | 2.1, 2.4 |
| A5, p43, F3 | Balance de clases completo; sacar la distribución de HAM10000 | Subsección nueva `sec:marco_desbalance` en 2.1 (remuestreo, pesos, focal, balanced softmax, umbral, métricas). Se elimina el párrafo de HAM10000 (l. 328–331) | 2.1 |
| A5, p38, F4 | Generalización, más desarrollada; sin la partición de HAM10000 | `sec:marco_regularizacion` se amplía; se elimina la referencia a `sec:met_particiones` (l. 136–137) y queda el principio general (repetidos entre particiones) | 2.1 |
| A7, T2, C4 | Cada concepto se justifica con «¿por qué lo necesita el lector?»; cada sección enlaza con la siguiente | Cada sección cierra con un párrafo de transición (ver §5). Cada subsección declara su razón de ser en la ficha | todas |
| A8 | En 2.2–2.5 un párrafo que relacione las arquitecturas con la siguiente | Cierres de 2.2, 2.3, 2.4 y 2.5 reescritos | 2.2–2.5 |
| A9, F5 | CNN y ViT como referencia (*baseline*) de los modelos multimodales | Subsección nueva `sec:marco_baseline_visual` al final de 2.3 | 2.3 |
| A10, A11, G1 | La generación de reportes está subrepresentada | Sección nueva 2.6 con peso comparable a la clasificación (2.3 + parte de 2.1), organizada en los tres ejes | 2.6 |
| A11, G2 | Alucinaciones y *hedging* con más desarrollo: contexto, ventajas, desventajas, consecuencias de no analizarlos | Subsección nueva `sec:marco_rep_fallas` | 2.6 |
| A12, G3 | Recuperar documentos ≠ recuperar imágenes similares ≠ usar la concordancia entre predicciones | Tres subsecciones separadas y una de integración, sin adelantar la implementación | 2.6 |
| A13, G3 | La ecuación de RAG no corresponde a la implementación | Se presenta la ecuación de Lewis como formulación original y se define aparte la variante que implementa el trabajo (§6) | 2.6 |
| A11, G4 | Predicción selectiva, abstención, tres salidas, relación con la calibración | Sección nueva 2.7, de modo que la cascada aparezca como consecuencia del marco | 2.7 |
| A14, E1 | Métricas ordenadas por lo que evalúan, con la matriz de confusión primero | 2.8 se reordena: clasificación, generación, transversal. Se verifica que cada métrica se use en los resultados | 2.8 |
| A16, S1, p60 | Los datasets no van en el estado del arte | Se elimina `tab:marco_conjuntos` (Tabla 2.1) y la descripción de conjuntos (l. 978–1019). Va a Cap. 3 (M1) | 2.10 |
| p59, p60, S2 | Sin «orden del pipeline»; intro en cada subsección; no abrir con «La línea tiene dos hitos…» | Intro de §2.10 y de cada subsección reescritas | 2.10 |
| A15, A16, S4 | Síntesis al final de cada subsección (problema, arquitecturas, datos, protocolo, limitaciones) | Un párrafo de síntesis por eje | 2.10 |
| A16, S5 | Tabla comparativa | Una tabla por eje, con `tab:marco_generadores` como punto de partida | 2.10 |
| A16, S6, M2.1.10 | Cerrar mostrando que el pipeline sale de los huecos | Subsección nueva `sec:estado_arte_posicion` | 2.10 |
| A1, p38, p43 | Nada de cosas prácticas ni de decisiones propias en el marco | Se recortan las menciones de HAM10000, HIBA, SkinCaRe, particiones, GPU de consumo y «el trabajo usa…» (lista en §5) | varias |
| A1 | Ningún término se usa antes de haberlo presentado | Auditoría del orden de definición (§2, punto 6) | todas |
| T1 | Formato de siglas | Ver §11, pregunta 4: afecta a todo `\gls{}` del capítulo | todas |

---

## 2. Criterio de redacción del capítulo (T2)

1. **Justificación.** Cada concepto responde a la pregunta «¿por qué necesita el lector esto para entender lo
   que se hizo o el resultado?». La ficha lo declara subsección por subsección («Razón de ser»). Si la
   respuesta es «para mostrar que se conoce el tema», sale.
2. **Lector general.** Tanto un informático (que se saltea 2.1–2.4) como un dermatólogo (que necesita las
   definiciones) tienen que poder seguirlo. Por eso cada métrica y cada método llevan la definición en el
   cuerpo, y los nombres de las secciones dicen qué contienen.
3. **Cada párrafo retoma el anterior y lleva al siguiente.** El primer enunciado de un párrafo usa algo
   que el anterior dejó instalado; el último deja instalado lo que necesita el siguiente. Dentro de la
   sección, los conceptos no se enumeran: se encadenan por una necesidad («la exactitud engaña con clases
   desbalanceadas → hace falta un promedio por clase → macro frente a ponderado»).
4. **Solo cuestiones teóricas.** Sin particiones, sin conjuntos concretos, sin GPU, sin «el trabajo usa…».
   Los ejemplos numéricos son hipotéticos («una clase con dos tercios de los casos»). Lo específico del
   trabajo se remite a Cap. 3 con `\ref` y sin adelantar decisiones.
5. **Transiciones entre secciones (C4).** Cada sección cierra con un párrafo de 3 a 5 líneas que dice qué
   dejó instalado y qué necesidad concreta queda abierta. No es una frase de traspaso vacía: nombra el
   concepto siguiente y por qué hace falta.
6. **Orden de definición (A1).** Auditoría de dependencias que la redacción debe respetar:
   - *logits*, softmax, entropía cruzada: 2.1.2, antes de balanced softmax (2.1.6), temperatura (2.4.1) y calibración.
   - *backbone*, *head* (cabeza de clasificación): se definen en 2.1.5, primera vez que se usan.
   - *token*: 2.2. *Embedding*: hoy se define en el ViT (l. 288); pasa a 2.2 (en la definición de token) porque
     2.2 ya habla de proyecciones y 2.5 lo usa.
   - *prompt*: se define en 2.4.1 (l. 381), antes de 2.5.1 y 2.6.4.
   - similitud coseno: se define en 2.5.1 (CLIP la usa), no en la sección de RAG como hoy (l. 584).
   - kNN: se define en 2.5.1 (uso sobre *embeddings*), se usa en 2.6.5.
   - calibración: se introduce con palabras en 2.7.3 (antes que 2.8.3, donde están ECE y las fórmulas). Debe quedar
     dicho que la definición formal está en 2.8.3.
   - «fidelidad diagnóstica» y «calidad descriptiva»: se definen en 2.6.2 y se usan en 2.8.2.
   - «detección» (binaria derivada de la multiclase): se define en 2.8.1 (A1: el Cap. 1 no la define).
   - «predicción selectiva», «cobertura», «riesgo selectivo»: 2.7.2, antes de 2.8.
7. **Sin figuras en la intro del capítulo ni de las secciones** salvo que sean imprescindibles (p27, p35).
8. **Convenciones de la guía que siguen vigentes:** fórmula de cada método o métrica que use el trabajo;
   notación $C$, $n$, $p_c$, $\mathbf{z}$, $\theta$, $\eta$, $\mathcal{L}$; cursiva de términos en inglés la
   primera vez en el capítulo; punto decimal; negrita solo en la definición de la métrica.

---

## 3. Estructura nueva, longitudes y mapa de secciones

Estimación de páginas por sección (coma decimal, como en la ficha anterior). Las páginas del `.tex` actual salen
del `tesina.toc`.

| Nueva | Título | Origen en el `.tex` actual | Páginas hoy | Páginas nuevas |
|---|---|---|---|---|
| 2.1 | Fundamentos del aprendizaje profundo | 2.1 (l. 34–201) | 5 | 6 |
| 2.2 | Transformers y mecanismos de atención | 2.2 (l. 203–239) | 1 | 1,5 |
| 2.3 | Aprendizaje profundo para clasificación visual | 2.3 sin transferencia/desbalance (l. 241–311) | 3 | 3,5 |
| 2.4 | Modelos de lenguaje y adaptación eficiente | 2.4 (l. 346–441) | 2 | 2,5 |
| 2.5 | Modelos visión–lenguaje | 2.5.1–2.5.2 (l. 443–516) | 3 | 3,5 |
| 2.6 | Generación de reportes y recuperación de información | 2.5.3–2.5.4 (l. 518–600) más contenido nuevo | 2 | 6 |
| 2.7 | Incertidumbre y predicción selectiva | nueva | 0 | 3,5 |
| 2.8 | Evaluación de modelos | 2.6 (l. 602–897) reordenada | 7 | 6,5 |
| 2.9 | Sesgo, robustez y generalización | 2.7 (l. 899–954) | 1 | 2 |
| 2.10 | Estado del arte y posicionamiento del trabajo | 2.8 (l. 956–1144) | 6 | 9–11 |
| | Introducción del capítulo | l. 23–32 | 0,5 | 0,5 |
| | **Total** | | **30** | **≈ 44–46** |

**El total supera con holgura los 25–30 páginas de la guía §5** (que el capítulo ya alcanzaba). No hay relleno
en el plan: el crecimiento viene de 2.6, 2.7 y del estado del arte, que son lo que pidió el tutor. Ver
pregunta 1 para decidir entre subir la referencia de la guía o recortar.

---

## 4. Introducción del capítulo (sin figura, sin detalle técnico)

**Reemplaza** las l. 23–32 y quita `\input{Figures/Capitulos/02-mapa-capitulo}` (l. 32) y el `fig:marco_mapa`.

**Qué dice (un párrafo de 6–8 líneas, dos si hace falta):**

1. De qué trata: el capítulo reúne los conceptos de aprendizaje profundo, de modelos visión–lenguaje, de
   generación de reportes, de incertidumbre y de evaluación que se necesitan para leer el resto del trabajo,
   y revisa los trabajos más cercanos.
2. Cómo se organiza: en diez secciones, descritas con «Este capítulo presenta…», en orden lógico y con una
   frase por grupo:
   - 2.1 a 2.3: cómo aprende una red neuronal y cómo se aplica a imágenes (fundamentos, atención,
     arquitecturas de clasificación visual);
   - 2.4 y 2.5: los modelos de lenguaje y su unión con la imagen;
   - 2.6 y 2.7: generar un reporte y decidir cuánta confianza merece cada diagnóstico;
   - 2.8 y 2.9: cómo se mide el desempeño y hasta dónde se puede confiar en lo medido;
   - 2.10: el estado del arte y la posición del trabajo.
3. No lleva cifras, siglas sin definir, nombres de modelos concretos ni el *pipeline*.

**Cierre.** Sin frase de recapitulación. Termina con la última descripción de grupo.

**Meta-texto.** La guía §3 desaconseja conectores metatextuales, pero T2 y la tesina de referencia
(`Docs/tesinamaglione_ejemplo.pdf`) piden explícitamente que la intro describa la organización. Se aplica T2
en este párrafo y en ningún otro lugar del capítulo. Ver pregunta 9.

**Comentario `%` del encabezado del `.tex`:** se reescribe (l. 3–21) para reflejar la nueva estructura y quitar
la historia de revisiones, que ya vive en esta ficha (guía §5: las extensiones y fuentes van como comentario).

---

## 5. Plan por sección

Convenciones de cada tabla: **Se reutiliza** (líneas y label del `.tex` actual), **Se recorta**, **Se elimina**,
**Nuevo**. «Razón de ser» es la respuesta a la pregunta de A7. Todas las citas de «Nuevo» que no estén en el
`.bib` figuran en la sección 10.

El plan de cada sección se movió el 10/10/2026 a un archivo propio en esta carpeta, con el mismo nombre que
el `.tex` de la sección (`01-fundamentos.md` … `10-estado-arte.md`). La numeración de este plan es la del
28/09 (2.2 transformers, 2.3 clasificación visual, 2.6 reportes, 2.7 incertidumbre); los archivos siguen
el orden actual del capítulo. La corrección de RAG (§6) quedó en `07-generacion-reportes.md`.

---

## 6. Corrección de RAG

Movida a `07-generacion-reportes.md`.

---

## 7. Mapa de labels viejos → nuevos (M4)

**Referencias desde otros capítulos** (búsqueda con `grep "\ref{sec:marco_\|\ref{tab:marco_\|\ref{fig:marco_\|\ref{eq:marco_"`
en `Chapters/`, `Figures/` y `Matter/`; el resto de `Docs/TFG` solo las menciona en fichas, guía y
tareas):

| Archivo y línea | Referencia | Estado |
|---|---|---|
| `Chapters/03-Materiales-Metodos.tex:70` | `sec:marco_generalizacion` | **Se mantiene** (label conservado) |
| `Chapters/04-Resultados-Clasificacion.tex:43` | `sec:estado_arte` | **Se mantiene** |
| `Chapters/06-Discusion.tex:24` | `sec:estado_arte` | **Se mantiene** |
| `Figures/Capitulos/02-mapa-capitulo.tex:14–46` | `sec:marco_vision`, `sec:marco_vlm`, `sec:marco_llm`, `sec:marco_evaluacion`, `sec:marco_generalizacion`, `sec:marco_fundamentos`, `sec:marco_atencion` | El archivo sale del Cap. 2 (C2). Si pasa a Cap. 3, hay que reescribir los `\ref` y agregar `sec:marco_reportes` y `sec:marco_incertidumbre` |

No hay referencias externas a `tab:marco_*`, `fig:marco_*` ni `eq:marco_*` fuera de `02-Marco-Teorico.tex` y de los
archivos de figuras (que solo definen sus propios `\label`). `fig:intro_dos_tareas` (Cap. 1) se cita desde el
`.tex` del Cap. 2 (l. 552); si I2 elimina la Figura 1.1, hay que revisar esa cita (pregunta 5).

**Labels de secciones que cambian**

| Label viejo | Qué pasa | Nuevo |
|---|---|---|
| `sec:marco_fundamentos` | Se mantiene | igual |
| `sec:marco_perceptron`, `sec:marco_softmax`, `sec:marco_entrenamiento`, `sec:marco_regularizacion` | Se mantienen | iguales |
| `sec:marco_familias` | **Se elimina** (C6). Ninguna referencia externa | — (el párrafo de cierre de 2.1 no lleva label) |
| `sec:marco_transferencia` | **Cambia de significado**: era «Transferencia de aprendizaje y desbalance de clases» en visión; pasa a ser solo transferencia y ajuste fino, en 2.1.5 | `sec:marco_transferencia` (2.1.5) |
| (nuevo) | Desbalance | `sec:marco_desbalance` (2.1.6). **La referencia de l. 77 (`sec:marco_transferencia` para «desbalance de clases») debe pasar a `sec:marco_desbalance`** |
| `sec:marco_atencion` | Se mantiene | igual (2.2) |
| `sec:marco_vision` | Se mantiene (retitulada) | igual (2.3) |
| `sec:marco_cnn`, `sec:marco_vit` | Se mantienen | iguales |
| (nuevo) | Baseline visual | `sec:marco_baseline_visual` (2.3.3) |
| `sec:marco_llm`, `sec:marco_llm_grandes`, `sec:marco_llm_lora` | Se mantienen | iguales (2.4) |
| `sec:marco_vlm`, `sec:marco_vlm_clip`, `sec:marco_vlm_generativos` | Se mantienen | iguales (2.5) |
| `sec:marco_vlm_generacion` | **Se mueve de 2.5.3 a 2.6** | `sec:marco_rep_tarea` (2.6.1), `sec:marco_rep_ejes` (2.6.2) y `sec:marco_rep_fallas` (2.6.3). Referencias internas hoy: l. 537 (a `marco_eval_texto`, sale), 549, 553, 556, 818, 1066, 1140; las de eval y estado del arte apuntan a `sec:marco_rep_ejes` (fidelidad y calidad) o a `sec:marco_rep_fallas` (alucinación) según el contexto |
| `sec:marco_vlm_rag` | **Se mueve** de 2.5.4 a 2.6 y se separa en tres | `sec:marco_rag` (2.6.4), `sec:marco_recuperacion_imagenes` (2.6.5), `sec:marco_concordancia` (2.6.6). Referencias internas hoy: l. 476 (clip) → `sec:marco_recuperacion_imagenes`; l. 1058 (estado del arte) → `sec:marco_recuperacion_imagenes` |
| (nuevo) | Integración | `sec:marco_integracion` (2.6.7) |
| (nuevo) | Incertidumbre | `sec:marco_incertidumbre`, `sec:marco_incert_fuentes`, `sec:marco_pred_selectiva`, `sec:marco_senales_confianza`, `sec:marco_tres_salidas` |
| `sec:marco_evaluacion` | Se mantiene | igual (2.8) |
| `sec:marco_eval_clasif`, `sec:marco_eval_texto` | Se mantienen (reordenadas) | iguales |
| `sec:marco_eval_calib`, `sec:marco_eval_estadistica`, `sec:marco_eval_gradcam` | Se mantienen como subsubsecciones de 2.8.3 | iguales; se agrega `sec:marco_eval_transversal` y `sec:marco_eval_robustez` |
| `sec:marco_generalizacion` | Se mantiene (retitulada) | igual (2.9) |
| `sec:estado_arte`, `sec:estado_arte_diagnostico`, `sec:estado_arte_vlm`, `sec:estado_arte_reportes` | Se mantienen | iguales (2.10) |
| (nuevo) | Posicionamiento | `sec:estado_arte_posicion` |

**Tablas, figuras y ecuaciones**

| Label | Estado |
|---|---|
| `tab:marco_conjuntos` | **Se elimina del capítulo** (S1). La tabla se traslada a Cap. 3 (M1); se cambia el label a `tab:met_conjuntos` al moverla, y se elimina la única referencia (l. 979) |
| `tab:marco_generadores` | Se mantiene, ampliada (S5). Se agregan `tab:marco_sota_clasificacion` y `tab:marco_sota_vlm` |
| `fig:marco_mapa` | **Se elimina** del capítulo (C2). Ver §8 |
| `fig:marco_perceptron`, `fig:marco_atencion`, `fig:marco_convolucion`, `fig:marco_vit_patches`, `fig:marco_swin`, `fig:marco_lora`, `fig:marco_clip`, `fig:marco_llava`, `fig:marco_confiabilidad` | Se mantienen |
| `eq:marco_capa`, `eq:marco_softmax`, `eq:marco_gradiente`, `eq:marco_adam`, `eq:marco_weight_decay`, `eq:marco_atencion`, `eq:marco_lm`, `eq:marco_temperatura`, `eq:marco_lora`, `eq:marco_rag`, `eq:marco_f1`, `eq:marco_tpr_fpr`, `eq:marco_auc`, `eq:marco_ece`, `eq:marco_brier`, `eq:marco_bleu`, `eq:marco_rouge`, `eq:marco_meteor`, `eq:marco_cider`, `eq:marco_bertscore`, `eq:marco_mcnemar`, `eq:marco_wilcoxon`, `eq:marco_gradcam` | Se mantienen |
| Nuevas ecuaciones propuestas | `eq:marco_riesgo` (riesgo esperado y empírico), `eq:marco_transfer_act` (actualización de $\theta_b,\theta_h$), `eq:marco_focal`, `eq:marco_balanced_softmax`, `eq:marco_ponderada`, `eq:marco_cos` (similitud coseno), `eq:marco_knn`, `eq:marco_rag_ctx` (condicionamiento por contexto), `eq:marco_riesgo_selectivo`, `eq:marco_acc_bal`, `eq:marco_fd` (fidelidad diagnóstica), `eq:marco_cobertura_ent` |

Además, tras mover cada label hay que comprobar con la compilación que no queden referencias sin resolver
(`??` en el PDF y advertencias `Reference … undefined` en `tesina.log`).

---

## 8. Figuras y tablas

| Figura o tabla | Estado | Comentario |
|---|---|---|
| `fig:marco_mapa` (`02-mapa-capitulo.tex`) | **Sale del Cap. 2** | C2. Evaluar su reutilización en Cap. 3 como esquema del *pipeline* (M1). Depende del `\ref` a las secciones del marco; se reescribe |
| `fig:marco_perceptron` | **Se mantiene, pregunta 6** | Ilustra retropropagación (2.1.3), que es concepto necesario. Si el autor prefiere el recorte fuerte del MLP, se elimina |
| `fig:marco_atencion`, `fig:marco_convolucion`, `fig:marco_vit_patches`, `fig:marco_swin`, `fig:marco_lora`, `fig:marco_clip`, `fig:marco_llava`, `fig:marco_confiabilidad` | Se mantienen | Sin cambios de contenido; revisar que los pies de figura no digan «el trabajo» |
| Figura nueva (opcional) | Los tres ejes de la generación de reportes | Un diagrama TikZ simple, con estilos de `13-Figuras.sty`, que ubique descripción visual, diagnóstico e incertidumbre. Solo si el autor lo aprueba (no es obligatoria) |
| Figura nueva (opcional) | Curva riesgo–cobertura ilustrativa | Con datos sintéticos rotulados como tales, como la de confiabilidad. Aclara 2.7.2 |
| Figura nueva (opcional) | Las tres salidas (afirmar, diferencial, derivar) sobre una escala de confianza | TikZ; ligada a 2.7.4 |
| `tab:marco_conjuntos` | **Sale** (S1) | A Cap. 3 (M1) |
| `tab:marco_generadores` | Se mantiene | Punto de partida de S5 |
| Tablas nuevas | `tab:marco_sota_clasificacion`, `tab:marco_sota_vlm`; tabla de tres mecanismos (2.6.7); tabla de tres comportamientos (2.6.3); opcional, tabla brecha → decisión (2.10.4) | `tabularx` con `booktabs`, `\filasep` |

---

## 9. Decisiones vigentes (conservadas de la ficha anterior)

Las decisiones marcadas como **anuladas** ya no rigen. Las demás se aplican a la nueva estructura. La numeración es
la de la ficha anterior.

| N.º | Estado | Contenido y cómo se aplica |
|---|---|---|
| 1 | Vigente | Las claves propuestas se nombran cuando se proponen (`refs_pendientes.md`) y no al citar |
| 2 | Vigente | Las páginas estimadas usan coma decimal |
| 3 | **Ampliada** | RNN y LSTM no se acortan a sigla; ahora salen del capítulo (C5, C6). Solo queda la limitación secuencial en una frase |
| 4 | **Anulada** (ya lo estaba por 14) | La sección clínica se eliminó |
| 5 | Vigente | Vocabulario sin palabras rebuscadas («exéresis», «glosa»…) |
| 6 | Vigente | `nvidia2023beginners` no se cita (la entrada no está hoy en el `.bib`: verificar) |
| 7 | Vigente | La figura del ViT es TikZ (`fig:marco_vit_patches`) |
| 8 | **Ampliada** | La descripción e impresión diagnóstica son las dos partes del reporte; ahora entra en 2.6.1. `kittler2016standardization` sostiene el vocabulario, no el formato del informe; **no usarla para el formato** |
| 9 | Vigente | LSTM sale (ya no hay `hochreiter1997long` en 2.1) |
| 10 | Vigente | «*Embedding*» es el término, no «embebido» (guía §4) |
| 11 | Vigente | Equivariancia, no invariancia, a traslaciones en el ViT |
| 12 | **Anulada** | AKIEC/HAM10000 salieron del capítulo (moved a `sec:met_ham`) |
| 13 | **Parcialmente anulada** | La atención en sección propia sigue vigente (`sec:marco_atencion`). El codificador–decodificador se corrige como estaba. **Se anula** la distinción «fidelidad diagnóstica / calidad del texto se instala solo en 2.4.3» → ahora en 2.6.2 (`sec:marco_rep_ejes`). La exactitud engañosa se explica solo en 2.8.1; 2.1.6 remite a ella |
| 14 | Vigente en lo que aplica | El capítulo queda solo con conceptos de computación; sin secciones clínicas ni conjuntos concretos. Costos asimétricos de las confusiones → `sec:met_seleccion` (Cap. 3). Se mantiene: HAM10000 y su partición **no** aparecen en el capítulo (F3, F4, p38, p43) |
| 15 | Vigente | *Hedging* sin cita (falla observada en la experimentación, remisión a Cap. 5; se relaciona con la literatura de abstención pero sin afirmar que la trate). Grad-CAM se cita con `adebayo2018sanity` (Grad-CAM supera sus pruebas). Las métricas sin referencia se presentan como concepto y la lista de términos va en Cap. 3 (`sec:met_protocolo`). MCE se escribe en línea (sin acrónimo). *Temperature scaling* no cambia la clase; *vector scaling* puede cambiarla. LLaVA: «los VLM generativos que usa el trabajo siguen el esquema de LLaVA» se reformula sin «el trabajo» |
| 16 | Vigente | `koh2021wilds` en el `.bib`. Las tablas del estado del arte dicen qué evalúa cada trabajo y con qué hardware, no los valores. DermaSynth son **textos** sintéticos redactados sobre imágenes reales, no imágenes por difusión. El cierre reconoce dos excepciones (Khan et al.; Chakrabarti et al.). DDI se cita sin cifras de AUC. Jones y Magalhães se citan por lo que dicen textualmente. PH² no está en la tabla (la tabla sale, pero la decisión de no citar PH² se conserva) |
| 17 | Vigente | Cada método y métrica se presenta con su fórmula (verificadas contra los PDF). Se mantienen: Adam, decaimiento de pesos, probabilidad de un LM, temperatura, RAG (Lewis), TPR/FPR y AUC, Brier, BLEU, ROUGE-L, METEOR, CIDEr, BERTScore, McNemar, Wilcoxon, Grad-CAM. El código usa McNemar exacto y el texto presenta las dos versiones (se mantiene la presentación; se elimina «el trabajo usa la exacta», pasa a Cap. 3). El corte de 2020 es criterio práctico (guía §6). HIBA: «primer conjunto público» se atribuye a sus autores. Notación: $C$ clases, $J$ referencias en CIDEr, $M$ intervalos en ECE, $N$ pares en CLIP |
| — | **Nueva (18)** | **2.1 abre directo, sin frase de presentación.** Ninguna sección abre con «Esta sección presenta…» (T2) |
| — | **Nueva (19)** | **Las transiciones entre secciones no son frases de traspaso vacías**: nombran el concepto siguiente y por qué hace falta. La ficha anterior retiró los traspasos (25/09) por vacíos; se reponen con contenido |
| — | **Nueva (20)** | **El capítulo no habla del *pipeline* ni de las decisiones del trabajo.** Solo del marco. Los `\ref` a Cap. 3 (`sec:met_*`) que sobran se eliminan; los que se mantienen son remisiones puras («los detalles están en la Sección~…») |
| — | **Nueva (21)** | La variante de RAG del trabajo se presenta como **condicionamiento por contexto con recuperación de imágenes**, no como el modelo de Lewis (§6) |

**Hilo conductor anterior («recorrido del pipeline», ficha 25/09): anulado** (p59, A11).
**Reparto de bloques A/B/C: anulado**; el capítulo se organiza por las diez secciones de esta ficha.

**Verificaciones vigentes de la ficha anterior** que hay que conservar al redactar (todas se hicieron contra el PDF
o la fuente y no se repiten en esta ficha):

- Fórmulas de Adam, BLEU, ROUGE-L, METEOR, CIDEr, BERTScore, McNemar, Wilcoxon, Grad-CAM, ECE/MCE, Brier: no
  reescribir a mano; copiar de las ecuaciones existentes.
- Los datos que citan Dosovitskiy (escala de preentrenamiento 14–300 millones de imágenes), Guo (calibración de
  redes anchas y profundas), Adebayo (Grad-CAM supera las pruebas de aleatorización), Holtzman (*beam search* sigue
  siendo la opción para generación dirigida) y Jones (272 estudios; solo dos con poblaciones no derivadas).
- Groh 2024 (389 dermatólogos y 459 médicos de atención primaria; el apoyo mejora más de un tercio la exactitud y
  amplía la diferencia entre tonos en atención primaria): verificado. Si se lo usa en 2.7.1, releer.
- Todo número del estado del arte se verifica contra el PDF (`resumen_papers.tex` tiene errores: no es fuente).

---

## 10. Referencias a proponer en `refs_pendientes.md`

Ninguna de estas claves está en `Bibliography.bib`. No se editan `refs_pendientes.md` ni el `.bib` (guía §6). Las
claves siguen el patrón `<apellido><año><palabra>`. «Verificada» significa que el título, los autores y el año se
comprobaron contra la página oficial de arXiv o de la revista el 28/09/2026 en esta sesión. Antes de citar cada
afirmación concreta hay que leer el PDF (guía §2, punto 2).

### Necesarias (sin ellas la sección no tiene respaldo)

| Clave propuesta | Referencia | Sección | URL | Estado |
|---|---|---|---|---|
| `geifman2017selective` | Geifman, Y. y El-Yaniv, R. «Selective Classification for Deep Neural Networks». *Advances in Neural Information Processing Systems* 30 (NeurIPS 2017) | 2.7.2 | https://arxiv.org/abs/1705.08500 | Verificada |
| `elyaniv2010foundations` | El-Yaniv, R. y Wiener, Y. «On the Foundations of Noise-free Selective Classification». *Journal of Machine Learning Research* 11:1605–1641, 2010 | 2.7.2 | https://jmlr.org/papers/v11/el-yaniv10a.html | Verificada |
| `hendrycks2017baseline` | Hendrycks, D. y Gimpel, K. «A Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks». ICLR 2017 | 2.7.2 | https://arxiv.org/abs/1610.02136 | Verificada |
| `lakshminarayanan2017simple` | Lakshminarayanan, B., Pritzel, A. y Blundell, C. «Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles». NeurIPS 2017 | 2.6.6, 2.7.3 | https://arxiv.org/abs/1612.01474 | Verificada |
| `kendall2017uncertainties` | Kendall, A. y Gal, Y. «What Uncertainties Do We Need in Bayesian Deep Learning for Computer Vision?». NeurIPS 2017 | 2.7.1 | https://arxiv.org/abs/1703.04977 | Verificada |
| `ji2023survey` | Ji, Z. et al. «Survey of Hallucination in Natural Language Generation». *ACM Computing Surveys* (2022/2023) | 2.6.3 | https://arxiv.org/abs/2202.03629 | Verificada (volumen y artículo del ACM CSUR sin verificar) |
| `rohrbach2018object` | Rohrbach, A., Hendricks, L. A., Burns, K., Darrell, T. y Saenko, K. «Object Hallucination in Image Captioning». EMNLP 2018 | 2.6.3 | https://arxiv.org/abs/1809.02156 | Verificada |
| `bai2024hallucination` | Bai, Z. et al. «Hallucination of Multimodal Large Language Models: A Survey». arXiv:2404.18930, 2024 | 2.6.3 | https://arxiv.org/abs/2404.18930 | Verificada |
| `kalai2025hallucinate` | Kalai, A. T., Nachum, O., Vempala, S. S. y Zhang, E. «Why Language Models Hallucinate». arXiv:2509.04664, 2025 | 2.6.3 | https://arxiv.org/abs/2509.04664 | Verificada; preprint (comprobar si tiene versión arbitrada) |
| `yosinski2014transferable` | Yosinski, J., Clune, J., Bengio, Y. y Lipson, H. «How transferable are features in deep neural networks?». NeurIPS 2014 | 2.1.5 | https://arxiv.org/abs/1411.1792 | Verificada |
| `raghu2019transfusion` | Raghu, M., Zhang, C., Kleinberg, J. y Bengio, S. «Transfusion: Understanding Transfer Learning for Medical Imaging». NeurIPS 2019 | 2.1.5 | https://arxiv.org/abs/1902.07208 | Verificada |
| `buda2018systematic` | Buda, M., Maki, A. y Mazurowski, M. A. «A systematic study of the class imbalance problem in convolutional neural networks». *Neural Networks* 106 (2018) | 2.1.6 | https://arxiv.org/abs/1710.05381 | Verificada (revista y volumen sin verificar) |
| `hendrycks2019benchmarking` | Hendrycks, D. y Dietterich, T. «Benchmarking Neural Network Robustness to Common Corruptions and Perturbations». ICLR 2019 | 2.8.3, 2.9 | https://arxiv.org/abs/1903.12261 | Verificada |
| `ramos2023smallcap` | Ramos, R., Martins, B., Elliott, D. y Kementchedjhieva, Y. «SmallCap: Lightweight Image Captioning Prompted with Retrieval Augmentation». CVPR 2023 | 2.6.5 | https://arxiv.org/abs/2209.15323 | Verificada |

### Opcionales o de apoyo (decidir; ver preguntas 7 y 10)

| Clave propuesta | Referencia | Sección | URL | Estado |
|---|---|---|---|---|
| `kirkpatrick2017overcoming` | Kirkpatrick, J. et al. «Overcoming catastrophic forgetting in neural networks». *PNAS* 114(13), 2017 | 2.1.5 | https://arxiv.org/abs/1612.00796 | Verificada (arXiv); PNAS sin verificar |
| `cui2019classbalanced` | Cui, Y., Jia, M., Lin, T.-Y., Song, Y. y Belongie, S. «Class-Balanced Loss Based on Effective Number of Samples». CVPR 2019 | 2.1.6 | https://arxiv.org/abs/1901.05555 | Verificada |
| `gao2023retrieval` | Gao, Y. et al. «Retrieval-Augmented Generation for Large Language Models: A Survey». arXiv:2312.10997 | 2.6.4 | https://arxiv.org/abs/2312.10997 | Verificada |
| `li2023evaluating` | Li, Y. et al. «Evaluating Object Hallucination in Large Vision-Language Models». EMNLP 2023 (POPE) | 2.6.3 | https://arxiv.org/abs/2305.10355 | Verificada |
| `cover1967nearest` | Cover, T. y Hart, P. «Nearest neighbor pattern classification». *IEEE Transactions on Information Theory* 13(1):21–27, 1967 | 2.6.5 | DOI 10.1109/TIT.1967.1053964 | **Sin verificar** (de memoria) |
| `elkan2001foundations` | Elkan, C. «The Foundations of Cost-Sensitive Learning». IJCAI 2001 | 2.1.6 | sin URL | **Sin verificar** (de memoria) |
| `brodersen2010balanced` | Brodersen, K. H. et al. «The balanced accuracy and its posterior distribution». ICPR 2010 | 2.8.1 | DOI 10.1109/ICPR.2010.764 | **Sin verificar** (de memoria) |
| `sokolova2009systematic` | Sokolova, M. y Lapalme, G. «A systematic analysis of performance measures for classification tasks». *Information Processing & Management* 45(4), 2009 | 2.8.1 | DOI 10.1016/j.ipm.2009.03.002 | **Sin verificar** (de memoria) |
| `angelopoulos2021gentle` | Angelopoulos, A. N. y Bates, S. «A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification». arXiv:2107.07511 | 2.7.4 | https://arxiv.org/abs/2107.07511 | **Sin verificar** (de memoria) |

Si el Cap. 4 usa suavizado de etiquetas, MixUp, CutMix, RandAugment, borrado aleatorio o decaimiento de tasa por
capas, faltan además sus referencias originales (Szegedy et al. 2016; Zhang et al. 2018; Yun et al. 2019;
Cubuk et al. 2020; Zhong et al. 2020; Howard y Ruder 2018). No se propusieron acá porque falta decidir si se
mencionan en el marco (pregunta 7); ninguna se verificó.

Otras referencias posibles en selectiva y clínica (Leibig et al. 2017, *Scientific Reports*, deferral en
retinopatía diabética; aprendizaje de diferir a un experto) no se pudieron verificar en esta sesión y no se
proponen.

---

## 11. Preguntas para el autor

Deben resolverse antes de aprobar la ficha.

1. **Extensión.** El plan da ≈ 44–46 páginas frente a las 25–30 de la guía §5 (hoy: 30). El aumento viene de
   2.6, 2.7 y el estado del arte. ¿Se sube la referencia de la guía o se recorta (por ejemplo, 2.8 en fórmulas
   de BLEU/ROUGE/METEOR/CIDEr si no se usan todas; 2.10 a 6–7 trabajos por eje en lugar de 8)?
2. **Estructura de 2.8.3.** ¿Calibración, inferencia estadística, robustez e interpretabilidad como
   subsubsecciones de una subsección «Evaluación transversal», o como subsecciones 2.8.3 a 2.8.6? La primera
   conserva los labels; la segunda deja una jerarquía plana.
3. **Qué métricas se usan.** El código implementa todas las de 2.8, pero no sé cuáles se reportan en los
   resultados. ¿Se confirman contra Cap. 4–5? Candidatas a salir: MCE, *vector scaling*, METEOR, CIDEr,
   Wilcoxon. Además, «exactitud balanceada» y «sensibilidad macro» son el mismo número: ¿se mantienen los dos
   nombres (como pidió el tutor, A14) o uno solo con el otro como sinónimo?
4. **Formato de siglas (T1).** Afecta a todo `\gls{}` del capítulo (no solo a esta ficha): «Modelos
   visión–lenguaje (*Vision–Language Models*, VLM)». Los términos definidos con `\gls` antes del cambio
   cambian de forma. ¿Se hace T1 antes de redactar el capítulo? Las siglas nuevas de esta ficha son: SGD
   no (se escribe en palabras); `ROC`; conviene declarar solo RAG, kNN, PEFT si se sigue usando. RAG y kNN ya están.
5. **Dependencia con el Cap. 1.** 2.6.2 retoma la Figura~\ref{fig:intro_dos_tareas} (dos condiciones de un reporte
   correcto). I2 pide revisar si la Figura 1.1 se mantiene. Si se elimina, ¿se reformula 2.6.2 sin la referencia
   o se mueve la figura al Cap. 2? Además, PI2 (fidelidad frente a calidad descriptiva) tiene que coincidir con la
   definición de 2.6.2.
6. **Figura del perceptrón** (`fig:marco_perceptron`). ¿Se mantiene, dado el pedido de recortar el MLP (A5)?
   Ilustra la retropropagación, no el perceptrón. Propuesta: mantenerla.
7. **Alcance de regularización y ajuste fino.** El código usa suavizado de etiquetas, MixUp, CutMix, RandAugment,
   borrado aleatorio, decaimiento de tasa por capas (0.85), ajuste en dos etapas y TTA. ¿Cuáles nombra el Cap. 4? Lo
   que se nombre allí tiene que estar definido en 2.1.4 o 2.1.5; lo que no, no se presenta. También:
   ¿se incluyen la pérdida por número efectivo (Cui) y la predicción conforme (2.7.4) o se dejan fuera?
8. **Fuga de información.** La guía §4 dice que se define en Materiales y métodos, pero 2.1.4 lo necesita antes
   (A1). ¿Se define en 2.1.4 y se actualiza la guía?
9. **Meta-texto en la intro.** T2 pide describir la organización del capítulo, y la guía §3 prohíbe conectores
   metatextuales. ¿Se acepta la excepción solo en el párrafo de intro?
10. **Olvido catastrófico.** ¿Se cita `kirkpatrick2017overcoming` (una referencia de aprendizaje continuo para un
    fenómeno que en ajuste fino aparece de otra manera) o se lo describe sin cita? Propuesta: sin cita si no
    aparece en el estado del arte.
11. **Profundidad del estado del arte (A16).** El tutor pide 7–8 artículos por eje con los nueve puntos y una
    carilla y media a dos por eje. ¿Los ya citados (≈ 25) se reverifican todos contra el PDF en los nueve
    puntos, o se elige un subconjunto para el tratamiento en profundidad y el resto queda en una línea y en la
    tabla?
12. **2.6.1 y los datos.** Se quita el detalle de cómo se redactó el texto de cada conjunto (SkinCAP, SkinCoT,
    MM-Skin, Derm1M) y se remite a Cap. 3. Ese detalle condiciona la validez de la referencia (decisión 17).
    ¿Se mueve completo a Cap. 3 o se conserva una versión mínima en 2.6.1?
13. **`hornik1989multilayer`, `goodfellow2014generative`, `ho2020denoising`, `kaplan2020scaling`,
    `hoffmann2022training`, etc.** Siguen en el `.bib` sin cita (decisión 16). ¿Alguna entra en 2.1 o 2.4
    (capacidad de aproximación de la red, escala de los LLM)?
14. **Calibración fuera de 2.8.3.** 2.7.3 introduce la calibración con palabras y 2.8.3 la define con fórmulas.
    ¿Se acepta ese orden (necesario para que 2.7 no use un término sin presentar), aunque duplique una oración?

---

## 12. Defectos detectados en el `.tex` actual

Independientes de la reestructuración; se corrigen al reescribir 2.8.2:

- **Líneas 806 y 808.** «La `\t`extbf{cobertura de entidades clínicas}» y «La `\t`extbf{consistencia diagnóstica}»:
  hay un carácter de tabulación donde debería estar la barra invertida de `\textbf`, así que el PDF no
  formatea esas dos definiciones en negrita y puede imprimir texto suelto (`extbf{…}`). Revisar el PDF.
- **Referencia a `fig:intro_dos_tareas` (l. 552)** depende del Cap. 1 (ver pregunta 5).
- **Línea 349–354.** La apertura de 2.4 usa «El generador de reportes del *pipeline*»: viola el criterio de
  esta ficha (T2). Se corrige al reescribir.
- **Encabezado `%` (l. 3–21)** narra la historia de revisiones, que ya vive en las fichas.

## 13. Decisiones del autor sobre las preguntas (2026-09-28)

1. **Extensión:** no hay límite. El capítulo tiene la extensión que necesite.
2. **Estructura de 2.8:** tres subsecciones que siguen el pedido del tutor (A14): evaluación de la clasificación,
   evaluación de la generación y evaluación transversal. Calibración, inferencia estadística, robustez e
   interpretabilidad van como subsubsecciones de la tercera.
3. **Métricas:** se verificó contra `Codigo/docs/` que todas se usan en la experimentación, así que ninguna sale:
   - MCE, en `resul/calibracion_resul_20260705.md`;
   - Wilcoxon, en `resul/mejoras_p5_local_resul_20260713.md`, P5.2;
   - METEOR y CIDEr, en `resul/ensamble_resul_20260607.md`, sobre SkinCoT;
   - *vector scaling*, en `ejecuciones.md`, calibración post hoc.

   Para la exactitud balanceada y la sensibilidad macro se usa **un solo nombre, «sensibilidad macro»** (guía
   §4). La definición menciona una vez que en la literatura también se la llama exactitud balanceada.
4. **Siglas:** T1 ya está hecho (`06-Glossary.sty`, `\acronimo`).
5. **Figura 1.1:** pasa a §2.6.2 (se mueve el archivo y el label desde el Cap. 1).
6. **`fig:marco_perceptron`:** se mantiene.
7. **Técnicas de entrenamiento:** en 2.1 se definen solo las que se analizan en los resultados, como las
   estrategias de pérdida para el desbalance. El resto (suavizado de etiquetas, MixUp, CutMix, RandAugment,
   borrado aleatorio, decaimiento por capas, ajuste en dos etapas, TTA) se nombra en el Cap. 3 con su cita y sin
   desarrollo teórico. La pérdida por número efectivo (Cui) y la predicción conforme quedan fuera.
8. **Fuga de información:** se define en 2.1.4 como concepto general, y la guía §4 se actualiza.
9. **Meta-texto en la intro:** se acepta la excepción en el párrafo de introducción (guía §3, ya actualizada).
10. **Olvido catastrófico:** se describe sin cita.
11. **Estado del arte:** primero se revisa `Papers/` y se buscan trabajos en las referencias de los ya citados.
    La profundidad se aplica a un subconjunto, no a los ~25 trabajos; el resto queda en una línea y en la tabla.
12. **2.6.1 y los datos:** queda una versión mínima en 2.6.1, que dice quién escribió el texto de referencia
    porque eso condiciona su validez. El detalle completo pasa al Cap. 3.
13. **Referencias del `.bib` sin cita:** no se agregan salvo que el texto las necesite.
14. **Calibración en 2.7 antes de 2.8:** se acepta el orden.

## 14. Segunda revisión del tutor (2026-10-05)

Fuente: `feedback/feedback_cap1_y_2_v2.md` y los comentarios de
`feedback/TFG-GAVIOLA-cap1-2-corregidosV2_05_10_26.pdf` (p. 26–35). Reemplaza el plan de §5 para 2.1.

| Pedido | Decisión |
|---|---|
| §2.1 demasiado introductoria; reducirla a unas tres páginas | Pasa de seis subsecciones (~6 páginas) a cuatro (~3.7 páginas) |
| Uno o dos párrafos introductorios sobre aprendizaje profundo | Dos párrafos antes de 2.1.1: aprendizaje supervisado y aprendizaje de la representación (`goodfellow2016deep`) |
| 2.1.1 Redes neuronales y aprendizaje supervisado | Neurona y MLP reducidos (sale la aproximación universal y `hornik1989multilayer`); descenso del gradiente, retropropagación y Adam en un párrafo cada uno, sin la ecuación de Adam (`eq:marco_adam` sale); predicción (inferencia). Etiqueta nueva `sec:marco_redes`; `sec:marco_perceptron` y `sec:marco_entrenamiento` desaparecen |
| Gradientes que se desvanecen o explotan: sacar | Sale el párrafo. En 2.2, la degradación de ResNet se justifica con «el problema no es el sobreajuste» |
| 2.1.2 Clasificación y funciones de pérdida; empezar por qué es un problema de clasificación y qué son las clases | Abre con la definición de clasificación y de clase, después logits, softmax y entropía cruzada (`eq:marco_entropia`, nueva), y la lectura de $p_c$ como confianza (remite a calibración, 2.6.3) y a la softmax del LLM (2.4.1) |
| 2.1.3 Generalización y desafíos; regularización: reducir | Sobreajuste, particiones y fuga de información, regularización en un párrafo (sale la formalización del riesgo, `eq:marco_riesgo`, y el párrafo de sesgo y varianza), y desbalance de clases con las tres pérdidas en fórmulas en línea. `sec:marco_desbalance` queda como etiqueta dentro de 2.1.3 |
| 2.1.4 Modelos preentrenados y adaptación | Transferencia, congelamiento y ajuste fino en dos párrafos (sale `eq:marco_transfer_act`). Olvido catastrófico con el término en inglés |
| Introducción del capítulo | Se adopta el texto que propone el tutor |
| Encabezados de tablas en negrita | Todas las tablas de los capítulos 1 y 2 |

## 15. Revisión del autor sobre la segunda revisión (2026-10-08)

| Pedido | Decisión |
|---|---|
| Los dos párrafos introductorios parecen exclusivos de imágenes; la definición de aprendizaje automático y la de supervisado son flojas; no se entiende qué distingue al aprendizaje profundo | Definición por experiencia y desempeño (Mitchell, vía `goodfellow2016deep`); supervisado, no supervisado y autosupervisado (este último remite a 2.4.1); ejemplos de imagen y de texto; la diferencia es qué se aprende: también la representación, no solo la decisión |
| 2.1.1: decir qué es una red neuronal | Una oración de definición antes de la neurona |
| La ecuación del descenso del gradiente corta la oración | La regla se enuncia completa en prosa y la ecuación cierra la oración |
| «una categoría de un conjunto finito y cada categoría es una clase» | «asignar cada entrada a una clase de un conjunto finito» |
| Relación de la entropía cruzada con las salidas | Párrafo nuevo: distribución de la etiqueta $\mathbf{q}$, máxima verosimilitud, gradiente $p_c - q_c$ sobre los logits, misma pérdida en los modelos de lenguaje |
| Negrita en «sobreajuste» y «regularización» | Hecho |
| $\frac{\lambda}{2}\lVert\theta\rVert_2^2$ se ve raro | Es correcto (penalización L2); se escribe $(\lambda/2)\sum_i \theta_i^2$ y se aclara que con Adam no equivale al decaimiento de pesos (AdamW, `loshchilov2019decoupled`) |
| Explicar las variables de las tres pérdidas para desbalance | Se definen $n$, $n_c$, $y$; cada ítem explica su fórmula y el balanced softmax muestra la softmax modificada |
| Nombrar la sensibilidad macro junto al F1 macro | Hecho, con qué mide cada una |
| ¿«Olvido catastrófico» es la traducción correcta? | Sí, es la usual en español (también «interferencia catastrófica»); se conserva |
| 2.1.4 corta; agregar uno o dos párrafos, fórmula o figura | Dos párrafos: ajuste en dos etapas (`kumar2022finetuning`) y tasa de aprendizaje por capa con fórmula (`eq:marco_llrd`, `howard2018universal`); y la extracción de características como medida del preentrenamiento (linear probe, remite a DermLIP) |
| Explicar lo que usan el código y los experimentos | Se agregan: calentamiento y coseno (2.1.1), AdamW, suavizado de etiquetas, RandAugment, borrado aleatorio y TTA (2.1.3), dos etapas y LLRD (2.1.4), clasificación de un VLM por verosimilitud (2.5.2), voto suave del ensamble (2.6.3). Diez referencias nuevas (`refs_pendientes.md`) |
| Menos «cómo funcionan las redes», más «por qué» | Sale la ecuación sinusoidal de posición (2.3.2), que no usa ningún modelo del trabajo; se agrega cómo codifican la posición el ViT y el Swin |
| Palabras huérfanas | `check_huerfanas.py` en `Docs/TFG/`, citado en la guía §6; 0 en los capítulos 1 y 2 |

Extensión: los agregados llevaron §2.1 a ~6 páginas; un recorte posterior (2026-10-09) la deja en ~5.2. Sale el párrafo del `linear probe` de 2.1.4 (ya está en 2.5.1; queda una oración sobre DermLIP), el gradiente de la entropía cruzada pasa a prosa ($p_c - q_c$, sin el lado izquierdo, que se veía mal en línea) y la Ecuación 2.4 muestra la suma completa; se condensan la introducción, el sobreajuste, la regularización y las pérdidas para desbalance.

---

# Fichas anteriores de 2.2 y 2.3 (reunidas en `02-arquitecturas-imagenes.md`, 2026-10-11)

## Ficha 2.2 — Redes convolucionales

Sección del `.tex`: `Chapters/02-Marco-Teorico/02-redes-convolucionales.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

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

## Ficha 2.3 — Transformers y mecanismos de atención

Sección del `.tex`: `Chapters/02-Marco-Teorico/03-transformers.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.2 Transformers y mecanismos de atención — `sec:marco_atencion`

**Mensaje central.** La atención compara directamente todas las posiciones y sustituye la recurrencia; el
transformer se construye sobre ella y sus dos módulos dan lugar a modelos visuales y de lenguaje distintos.

**Razón de ser.** Todo lo que sigue (ViT, Swin, LLM, VLM) usa esta operación. **Extensión: 1,5 páginas.**

| Contenido | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| Idea de la atención, *tokens* | l. 206–213 | Se elimina «reemplaza el recorrido paso a paso de las redes recurrentes» tal como está (las RNN no se presentaron); se reformula como «frente al procesamiento secuencial de 2.1» | Definición de *embedding* (traída de l. 288–290) al introducir la proyección del token: es la primera vez que se necesita |
| Atención escalada por producto punto | l. 215–225, `eq:marco_atencion`, `fig:marco_atencion` | — | — |
| Atención multi-cabeza | l. 229–232 | — | — |
| Codificador y decodificador | l. 234–239 | Se elimina la oración con referencias adelante a `sec:marco_vit` y `sec:marco_llm_grandes` si sobra (se mantienen: es la transición) | Una oración: **codificación de la posición** (la atención no distingue el orden; se suma un *embedding* de posición), que hoy solo aparece en el ViT (l. 290) |

**Párrafo de transición (C4).** Ideas: la atención es una operación sobre secuencias de *tokens*; según qué
módulo se conserve (codificador o decodificador) y qué se tokenice (parches o palabras), sale una familia
distinta. Se empieza por las imágenes (2.3), donde conviven con las convolucionales.
**Citas:** `vaswani2017attention`, `dosovitskiy2021image`, `brown2020language`.

---

# Fichas anteriores de 2.4 y 2.5 (reunidas en `03-lenguaje-vlm.md`, 2026-10-11)

## Ficha 2.4 — Modelos de lenguaje y adaptación eficiente

Sección del `.tex`: `Chapters/02-Marco-Teorico/04-modelos-lenguaje.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.4 Modelos de lenguaje y adaptación eficiente — `sec:marco_llm`

**Mensaje central.** Un LLM es un predictor del siguiente *token* preentrenado a gran escala; se lo
condiciona con texto y se lo adapta con métodos que actualizan pocos parámetros.

**Razón de ser.** El generador de reportes es un LLM con entrada visual; sin este marco no se entienden la
decodificación, el *prompt* ni LoRA. **Extensión: 2,5 páginas.**

**Apertura.** Se elimina «El generador de reportes del pipeline es un modelo de este tipo…» (l. 349–354).
Abre diciendo qué es un modelo de lenguaje y qué necesita saber el lector: cómo se obtiene, cómo genera texto y
cómo se lo adapta.

| Subsección | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| 2.4.1 Grandes modelos de lenguaje — `sec:marco_llm_grandes` | l. 359–406; `eq:marco_lm`, `eq:marco_temperatura` | **Se elimina** en el último párrafo «se fija y se documenta como un hiperparámetro más del generador» (l. 404–406) o se generaliza | **Contexto y *prompt* (necesario para G3):** un párrafo. El modelo condiciona la salida en el texto que recibe; una instrucción y ejemplos incluidos en el *prompt* orientan el comportamiento sin cambiar los pesos (*in-context learning*, `brown2020language`). Se define *prompt* y se establece que **agregar información al contexto es una forma de condicionar la generación**. Es la base de la variante de RAG de §6 |
| 2.4.2 Ajuste eficiente de parámetros: LoRA — `sec:marco_llm_lora` | l. 411–434; `eq:marco_lora`, `fig:marco_lora` | **Se elimina** l. 436–438 («Uno de los objetivos del trabajo es… y por eso los modelos generativos se adaptan con LoRA…»): decisión propia | **Un párrafo inicial de conexión con 2.1.5:** el ajuste fino completo de 2.1.5 es costoso en memoria; los métodos de ajuste eficiente en parámetros (*parameter-efficient fine-tuning*, PEFT) congelan el modelo y entrenan pocos parámetros nuevos. Se nombra la familia (con `\gls{peft}` si se mantiene la sigla) antes de LoRA |

**Párrafo de transición a 2.5.** Se elimina l. 440–441 tal como está («Un modelo de lenguaje, sin embargo, solo
recibe texto») y se reescribe: hasta acá el modelo procesa texto y el clasificador procesa imágenes; unir los
dos exige una forma de llevar los rasgos de la imagen al espacio de *tokens* del LLM, o de alinear ambas
modalidades en un espacio común. Eso es un modelo visión–lenguaje.
**Citas:** `brown2020language`, `touvron2023llama`, `devlin2019bert`, `ouyang2022training`, `holtzman2020curious`,
`hu2021lora`, `yilmaz2025resourceefficient` (solo si respalda la afirmación sobre costos; se puede pasar al estado del arte).

## Ficha 2.5 — Modelos visión–lenguaje

Sección del `.tex`: `Chapters/02-Marco-Teorico/05-vlm.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

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

## Decisión del autor (2026-10-12): Wilcoxon fuera del marco

Con la corrección de Holm sobre 21 pares, Wilcoxon sobre siete clases nunca alcanza el umbral corregido
(p mínimo 0.016 frente a 0.0024), así que el Cap. 3 (3.9) compara la sensibilidad por clase de forma
descriptiva y no usa la prueba. Por la regla E1 (cada método presentado se usa en los resultados), se quita
de 2.8 el párrafo y la ecuación `eq:marco_wilcoxon`; `wilcoxon1945individual` y `demsar2006statistical`
quedan sin citar.

## Decisión del autor (2026-10-12): corrección de Holm en el marco

3.9 corrige los p de McNemar con Holm sobre 21 pares, así que 2.8 la define después de McNemar, con su
ecuación (`eq:marco_holm`) y la relación con Bonferroni. La cita `holm1979simple` no estaba en el `.bib`: se
propuso en `refs_pendientes.md` y queda indefinida hasta que el autor la incorpore.

## Revisión del autor (2026-10-12): 2.3

- El aprendizaje autosupervisado queda en 2.3, donde aparece su primer ejemplo, y se contrasta con el
  supervisado de 2.1.
- Los modelos de lenguaje preentrenados se presentan como dos tipos (solo decodificador y solo codificador);
  LLM sigue designando al de solo decodificador a gran escala, que es como lo usa el resto del capítulo.
- Sale de P4 la mención a Mistral 7B, LLaVA-Med 1.5 y Phi-3-mini: los modelos se presentan en el Cap. 3.
  «Pesos abiertos» abre 2.3.2.
- 2.3.3 abre conectado con el cierre de 2.3.2, y *zero-shot* se define explícitamente en P12.
