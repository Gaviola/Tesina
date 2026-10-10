# Ficha 2.8 — Evaluación de modelos

Sección del `.tex`: `Chapters/02-Marco-Teorico/08-evaluacion.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.8 Evaluación de modelos — `sec:marco_evaluacion`

**Mensaje central.** Cada salida se evalúa con métricas que ven una parte y no otra: la clasificación, la
generación y las propiedades transversales (calibración, significancia, robustez, interpretabilidad).

**Razón de ser.** El lector (dermatólogo o informático) necesita saber qué mide cada número que aparece en los
resultados y qué no mide. **Extensión: 6,5 páginas** (baja 0,5 respecto de hoy por el recorte de lo aplicado).

**Apertura.** Se elimina «Cada componente del *pipeline* entrega una salida distinta…» (l. 605–610). Se abre
diciendo que las métricas se agrupan por lo que evalúan.

**Verificar que se use (E1).** Cada métrica presentada debe aparecer en los resultados; la que no, sale. El código
implementa las siguientes: matriz, AUC, sensibilidad/especificidad, exactitud balanceada, F1, ECE, MCE, Brier,
BLEU, ROUGE, METEOR, CIDEr, BERTScore, McNemar, Wilcoxon, *temperature scaling* y *vector scaling*, Grad-CAM,
robustez por perturbaciones, entidades clínicas. El autor confirma con los resultados de Cap. 4–5 y se saca lo
que no se reporte (pregunta 3). Los candidatos más probables de no estar en los resultados son MCE,
*vector scaling*, METEOR y CIDEr.

| Subsección | Se reutiliza | Se recorta / elimina | Nuevo |
|---|---|---|---|
| 2.8.1 Evaluación de la clasificación — `sec:marco_eval_clasif` | l. 615–666, `eq:marco_f1`, `eq:marco_tpr_fpr`, `eq:marco_auc` | **Se elimina** la exactitud «alrededor de dos tercios» de HAM10000 (l. 622–625); se sustituye por un ejemplo hipotético. Se elimina «el trabajo no selecciona modelos por exactitud» y «el trabajo usa el promedio simple… F1 macro» (l. 624–625, 664–666: decisiones propias, van a `sec:met_seleccion`) | **Reordenar (A14):** ver abajo. Se agrega la **exactitud balanceada** (definida) |
| 2.8.2 Evaluación de la generación — `sec:marco_eval_texto` | l. 718–819, ecuaciones BLEU, ROUGE-L, METEOR, CIDEr, BERTScore (l. 725–785) | **Se recorta** l. 806–812, donde el `.tex` describe «El trabajo usa dos métricas de este tipo». Se convierten en concepto (entidades y consistencia diagnóstica) sin «el trabajo». **Se elimina** el vocabulario finito de l. 798–804 si se traslada a 2.6.2 (queda una remisión) | Tres familias explícitas: textuales, diagnósticas, descriptivas. Ver abajo |
| 2.8.3 Evaluación transversal — `sec:marco_eval_transversal` (nueva; agrupa 4 sub-temas) | Calibración l. 671–713 (`sec:marco_eval_calib`); inferencia estadística l. 824–868 (`sec:marco_eval_estadistica`); Grad-CAM l. 873–897 (`sec:marco_eval_gradcam`) | La introducción de calibración se acorta porque 2.7.3 ya la presentó. Se elimina «Para el *pipeline* la calibración importa porque…» (l. 712–713). Se elimina «el trabajo usa la versión exacta» (l. 850) y «El trabajo la aplica con las siete clases…» (l. 867–868) → Cap. 3. Se elimina «Su uso en el trabajo es detectar…» (l. 895–897) | **Robustez** (subsección nueva corta): ver abajo. Cierre con remisión a riesgo–cobertura (2.7.2) |

Nota de estructura: 2.8.3 se puede implementar como subsección con cuatro `\subsubsection`
(`calibración`, `inferencia estadística`, `robustez`, `interpretabilidad`) conservando los labels viejos
(`sec:marco_eval_calib`, `sec:marco_eval_estadistica`, `sec:marco_eval_gradcam`) y agregando
`sec:marco_eval_robustez`. Así los `\ref` internos no cambian. Pregunta 2.

### 2.8.1 reordenación (A14) — ideas por párrafo

1. **Matriz de confusión primero.** Definir $M\in\mathbb{N}^{C\times C}$, $M_{ij}$ = imágenes de clase real
   $i$ predichas $j$; de ella salen todas las métricas. Caso binario con TP, FN, FP, TN (reutiliza l. 615–619).
   Razón de ser: es lo que el lector inspecciona para ver qué se confunde con qué.
2. **Sensibilidad y especificidad por clase.** $R_c=M_{cc}/\sum_j M_{cj}$; especificidad de una clase respecto del
   resto. Tienen una interpretación clínica directa (fracción de casos que se detectan / que se descartan).
   Definición de **detección**: colapsar la salida multiclase a binaria (clase de interés frente al resto, con
   $s=p_c$ o $\sum$ de las clases de interés); precisa A1.
3. **Exactitud y su límite.** Definir exactitud $=\sum_c M_{cc}/n$ y mostrar con un ejemplo hipotético por qué
   engaña con clases desbalanceadas (retoma 2.1.6 sin repetirlo).
4. **Exactitud balanceada.** $\text{BA}=\frac1C\sum_c R_c$. Nota: coincide con la sensibilidad macro; se elige
   un solo nombre según la guía §4 («sensibilidad macro») y se menciona el otro como sinónimo (pregunta 3).
   Cita `brodersen2010balanced` (nueva; sin verificar) o `sokolova2009systematic`.
5. **Precisión, F1 y promedios macro y ponderado** (reutiliza l. 627–639, `eq:marco_f1`). Cita
   `sokolova2009systematic` para la distinción de promedios (nueva; sin verificar; opcional).
6. **Umbral, ROC y AUC** (reutiliza l. 641–666: `eq:marco_tpr_fpr`, `eq:marco_auc`). El AUC multiclase por
   clase y su promedio macro; se elimina la justificación de la elección.

### 2.8.2 estructura por familia (A14)

- **Métricas textuales** (con referencia): BLEU, ROUGE-L, METEOR, CIDEr, BERTScore (reutiliza l. 718–788). Se
  mantiene el límite de las métricas con referencia por la variabilidad entre observadores (l. 790–796,
  `carrera2016validity`).
- **Métricas diagnósticas** (sin referencia): **consistencia diagnóstica** (la categoría que nombra el texto es la
  correcta o un sinónimo reconocido; equivale a la fidelidad diagnóstica de 2.6.2). Fórmula:
  $\text{FD}=\frac1n\sum_i\mathbf{1}[\text{dx}(g_i)=y_i]$, donde $\text{dx}(\cdot)$ extrae la categoría nombrada.
- **Métricas descriptivas** (sin referencia): **cobertura de entidades clínicas**, la proporción de las
  categorías del vocabulario (color, patrón, estructura) que el texto menciona. Fórmula:
  $\text{cob}(g)=\frac{|\{k:\exists\,e\in V_k,\ e\text{ aparece en } g\}|}{K}$, con $V_k$ el conjunto de
  términos de la categoría $k$ y $K$ el número de categorías. Se remite a Cap. 3 para la lista y las reglas.
- **Revisión por especialistas.** Ninguna métrica automática detecta un hallazgo inventado; el estándar de
  referencia es la lectura de un especialista sobre una rúbrica (concepto general; la rúbrica concreta va
  en Cap. 3). Sin cita nueva si se dice así; si se afirma algo sobre el método, referenciar.

### 2.8.3 robustez — ideas (nueva)

1. **Definición.** Cuánto cambia una métrica $m$ cuando la entrada se perturba de forma que no altera su
   contenido clínico (desenfoque, cambios de brillo o compresión, ruido). Se mide como caída
   $\Delta m=m_{\text{original}}-m_{\text{perturbada}}$ o su cociente.
2. **Para qué sirve.** Permite anticipar el comportamiento ante variaciones de adquisición (2.9) sin tener otro
   conjunto. Cita `hendrycks2019benchmarking` (nueva; verificada: arXiv 1903.12261).
3. **Qué no es**: robustez adversarial.

**Párrafo de transición a 2.9.** Las métricas de esta sección describen el desempeño sobre la distribución
del test; queda por saber hasta dónde valen fuera de ella.
**Citas de 2.8:** existentes: `fawcett2006introduction`, `guo2017calibration`, `brier1950verification`,
`papineni2002bleu`, `lin2004rouge`, `banerjee2005meteor`, `vedantam2015cider`, `zhang2020bertscore`,
`carrera2016validity`, `efron1979bootstrap`, `mcnemar1947note`, `wilcoxon1945individual`, `demsar2006statistical`,
`selvaraju2017gradcam`, `adebayo2018sanity`. Nuevas: `hendrycks2019benchmarking`, y opcionales
`brodersen2010balanced`, `sokolova2009systematic`.
