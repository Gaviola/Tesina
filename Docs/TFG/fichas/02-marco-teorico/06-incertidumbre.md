# Ficha 2.6 — Incertidumbre y predicción selectiva

Sección del `.tex`: `Chapters/02-Marco-Teorico/06-incertidumbre.tex`.

Plan movido desde la ficha única del capítulo el 10/10/2026, sin cambios de contenido. Es la historia de la sección; las decisiones posteriores están en `historial.md` y lo vigente, en `00-capitulo.md`. El hilo conductor (§1 de la guía) se agrega arriba de este plan cuando se reescriba la sección.

---

## 2.7 Incertidumbre y predicción selectiva — `sec:marco_incertidumbre`

**Sección nueva (G4).** **Extensión: 3,5 páginas.**

**Mensaje central.** Un clasificador puede abstenerse de decidir cuando su confianza es insuficiente; existen
señales para estimar esa confianza, y la salida de un sistema clínico puede ser afirmar, ofrecer diferenciales o
derivar. Esa política es la que hace que el diseño en cascada aparezca como consecuencia del marco.

**Razón de ser.** Sin esta sección, el *pipeline* del Cap. 3 parece una construcción arbitraria (A11). Es el
puente entre las fallas de 2.6.3 y los mecanismos de 2.6.5–2.6.6.

| Subsección | Razón de ser | Se reutiliza | Nuevo |
|---|---|---|---|
| 2.7.1 Incertidumbre en la clasificación diagnóstica — `sec:marco_incert_fuentes` | Por qué un clasificador puede equivocarse con confianza y por qué importa en medicina | — | Ver abajo |
| 2.7.2 Predicción selectiva y abstención — `sec:marco_pred_selectiva` | Formaliza «no decidir» | — | Ver abajo |
| 2.7.3 Señales de confianza y calibración — `sec:marco_senales_confianza` | Cómo saber cuándo abstenerse | Se remite a `sec:marco_eval_calib` para las fórmulas | Ver abajo |
| 2.7.4 Tres salidas: afirmar, ofrecer diferenciales o derivar — `sec:marco_tres_salidas` | Generaliza el rechazo binario a la política clínica | — | Ver abajo |

### 2.7.1 ideas

1. **Dos fuentes.** Incertidumbre por ruido o ambigüedad de los datos (aleatoria) e incertidumbre por falta de
   conocimiento del modelo (epistémica), que se reduce con más datos. Cita `kendall2017uncertainties` (nueva;
   verificada: arXiv 1703.04977). Tercera fuente sin cita nueva: cambio de distribución (remite a 2.9).
2. **Por qué importa en medicina.** Los errores no cuestan igual (falsos negativos frente a falsos positivos) y
   la decisión final es humana; un sistema que reconoce su límite y deriva puede ser preferible a uno que
   siempre responde. Enunciado teórico y general, sin cifras de melanoma. Cita `groh2024learningaided`
   (ya está; el apoyo de IA mejora la exactitud pero amplía diferencias entre grupos; sirve de contexto de
   colaboración humano–IA). Verificar que respalde exactamente lo dicho antes de usarla.

### 2.7.2 ideas (con fórmulas)

1. **Clasificación con opción de rechazo.** Un clasificador selectivo es un par $(f,g)$: $f$ predice y $g$
   decide si se acepta. Se define $\text{cobertura}=\mathbb{E}[g(x)]$ y
   $\text{riesgo selectivo}=\dfrac{\mathbb{E}[\ell(f(x),y)\,g(x)]}{\mathbb{E}[g(x)]}$.
   Cita `elyaniv2010foundations` (nueva; verificada: JMLR 11:1605–1641, 2010) y `geifman2017selective`
   (nueva; verificada: arXiv 1705.08500, NeurIPS 2017).
2. **Compromiso riesgo–cobertura.** Al aumentar el umbral de confianza baja la cobertura y baja el riesgo
   selectivo (si la señal es informativa). La curva riesgo–cobertura resume el compromiso; su forma es la
   medida de calidad de la señal. Se define con palabras y una fórmula: $g(x)=\mathbf{1}[\kappa(x)\ge\tau]$,
   con $\kappa$ la señal de confianza.
3. **La señal más simple: la máxima probabilidad softmax** $\kappa(x)=\max_c p_c$, línea base para detectar errores
   (`hendrycks2017baseline`, nueva; verificada: arXiv 1610.02136).

### 2.7.3 ideas

1. **Calibración, definición con palabras.** Un modelo está calibrado si sus probabilidades coinciden con
   sus frecuencias de acierto; las redes profundas tienden a ser sobreconfiadas (`guo2017calibration`, ya
   está). Las fórmulas (ECE, MCE, Brier, *temperature scaling*) están en 2.8.3. **Este párrafo reemplaza la
   introducción de calibración que hoy abre `sec:marco_eval_calib`** (l. 671–676), que se conserva allí como
   definición formal.
2. **Tres señales de confianza**, en `enumerate`:
   - probabilidad softmax (barata, pero puede estar mal calibrada y no ser monótona respecto del error si hay
     cambio de distribución);
   - concordancia entre predictores (2.6.6);
   - consenso entre vecinos recuperados, es decir, el voto y su unanimidad ($\hat p_{\text{kNN}}$, 2.6.5).
   Se señalan las limitaciones de cada una: la primera confunde confianza con exactitud, la segunda requiere dos
   modelos, la tercera depende de la cobertura de la base.
3. **Combinación.** La calibración mejora una señal, pero no crea información que la señal no contiene: una
   confianza calibrada sigue sin separar los casos difíciles si el modelo no los distingue. Se mide con
   riesgo–cobertura (2.7.2) y no solo con ECE.

### 2.7.4 ideas — tres salidas y la cascada como consecuencia

1. **De rechazar a tres salidas.** En la práctica clínica no basta aceptar o rechazar. Tres salidas posibles:
   **afirmar** un diagnóstico, **ofrecer diferenciales** (un conjunto de candidatos) o **derivar** si no se
   alcanza la confianza. Formalizar: una política $\pi(x)\in\{\text{afirmar},\text{diferencial},\text{derivar}\}$
   que depende de las señales $\kappa(x)$.
2. **La salida diferencial es predicción por conjuntos**: $C(x)\subseteq\{1,\dots,C\}$, y $|C(x)|=1$ es afirmar.
   Se puede citar la predicción conforme como marco teórico (`angelopoulos2021gentle`, nueva; sin verificar;
   opcional, pregunta 7); si no, sin cita.
3. **Costos.** Cada salida tiene un costo distinto en el reporte: afirmar arriesga un error; diferencial
   informa menos pero cubre más; derivar no produce diagnóstico. La política óptima depende de cuánto pesa cada
   costo (idea de riesgo con opción de rechazo).
4. **Consecuencia para la generación (retoma eje 3 de 2.6.2).** Cada salida corresponde a un tipo de reporte: uno
   afirmativo, uno diferencial y ninguno con derivación. Así, un sistema en cascada que primero estima la
   confianza y después redacta según el resultado es **consecuencia** del problema y no un diseño arbitrario.
   **No se describe** el *pipeline* concreto ni se nombran modelos (Cap. 3).

**Párrafo de transición a 2.8.** Decidir con confianza, comparar modelos y detectar fallas exige medir bien:
qué métricas evalúan la clasificación, cuáles la generación y cuáles el comportamiento de ambas de forma
transversal (calibración, significancia, robustez, interpretabilidad).
**Citas de 2.7:** existentes: `guo2017calibration`, `groh2024learningaided`. Nuevas: `elyaniv2010foundations`,
`geifman2017selective`, `hendrycks2017baseline`, `kendall2017uncertainties`, `lakshminarayanan2017simple`
(compartida con 2.6), `angelopoulos2021gentle` (opcional).
