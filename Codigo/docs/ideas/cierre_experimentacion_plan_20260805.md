# Plan — Cierre de experimentación (agosto 2026)

**Fecha:** 2026-08-05
**Origen:** feedback del tutor sobre `experimentacion.tex` ([feedback_20260805.md](../feedback_20260805.md))
+ objetivo de agosto: **cerrar la etapa de experimentación y validación clínica** e **intentar mejorar los
resultados del ensamble** para competir con el SOTA. Decisiones tomadas en una sesión de grilling (ver §2).

---

## 1. Marco (decisiones resueltas)

1. **Meta raíz:** robustecer la experimentación para el TFG (todo el feedback resuelto) es lo primario.
   "Competir con SOTA" se **acota** a (a) detección de melanoma y (b) calidad de reportes, **siempre medido
   en relación al hardware accesible** (eje de la tesis). No se persigue batir el 0.93 F1 de 7-clases.
2. **Sistema propuesto final = pipeline avanzado:** clasificador → grounding + **ruteo consciente de
   incertidumbre** (afirmativo / diferencial / abstención-derivación) + **RAG** + fix de repetición. El
   grounding simple pasa a baseline/ablación.
3. **Ruteo de incertidumbre (híbrido):** se adopta el marco de **3 niveles** del tutor
   (`max P ≥ τ_alta` → afirmativo; `τ_baja ≤ max P < τ_alta` → diferencial; `max P < τ_baja` →
   abstención/derivación), pero alimentado por la **señal que funciona** (confianza calibrada + acuerdo
   Swin↔kNN-DermLIP). El hallazgo "la softmax cruda rutea mal" (P0.1/P5.4) es la **motivación** del diseño.
   Esto conecta la calibración con el sistema (lo que pedía el tutor).
4. **Validación clínica:** construir la **rúbrica formal** (5 criterios del tutor) + muestra n≈30; buscar
   especialista en paralelo. **No bloquea** — queda como protocolo listo + proxies automáticos.
5. **Melanoma:** optimizar el **punto de operación** (bajar la tasa de falsos negativos) + **ensamble de
   clasificadores** (Swin+ConvNeXt+DermLIP). Local, sobre probs ya guardadas.
6. **Completar 1503:** las 1503 ya están generadas en Mendieta → **bajar + re-evaluar** Mini-VLM y LLaVA en
   las condiciones centrales (baseline/DermLIP/Swin/oracle). La tabla del ensamble pasa a ser toda 1503.
7. **Generación faltante (diferenciales del ensamble incierto, ~390):** correr en **TOKO** (Mendieta con el
   scheduler caído). Requiere subir checkpoint Mini-VLM + datos + CSV al scratch.
8. **Gap "detección → clasificación" (detalle del tutor):** justificar el desfase entre el título de la
   tesina ("detección") y lo desarrollado ("clasificación"). Justificación:
   - *Detección como **localización*** (¿dónde está la lesión?): las imágenes de HAM10000/HIBA son
     **dermatoscópicas ya recortadas y centradas en una única lesión**; la localización viene dada por el
     protocolo de adquisición (no hay múltiples lesiones que localizar) → esa etapa es trivial y el trabajo
     se concentra en el **diagnóstico**.
   - *Detección como **screening*** (¿hay melanoma?): **sí** es parte del trabajo, operacionalizada como la
     **clasificación binaria melanoma-vs-resto** (Workstream B). "Detección de melanoma" = ese binario.
   - Conclusión: no hay contradicción; el binario de melanoma **cierra el gap terminológico**.

---

## 2. Workstreams

### A — Pulido del documento (LOCAL) · cierra el feedback de forma/claridad
- **A1** Cuadro 3 (`tab:sota_clasif`) y Cuadro 9 (`tab:skinvl`): achicar; mover la referencia a paréntesis
  en la 2.ª columna y eliminar la 1.ª (poco informativa); **marcar el mejor** en Acc/F1.
- **A2** **Marcar en negrita el mejor valor** en todas las tablas de métricas.
- **A3** §Cambio de calidad de imagen: explicar mejor el protocolo de perturbaciones (¿un filtro por vez o
  todos?, ¿cómo se eligen las severidades?, ¿5 datasets nuevos?) — **con un gráfico/esquema**.
- **A4** Reencuadrar Grad-CAM/saliencia como **análisis cualitativo complementario de atención espacial**,
  no como prueba de validez clínica (eso lo da un especialista).
- **A5** Aclarar HAM↔HIBA: qué clases son comunes, cómo se mapearon (SCC→AKIEC, 158 imgs), si se eliminaron
  clases no compartidas, si la comparación es bajo el mismo espacio diagnóstico; y que la caída puede venir
  de **población y/o anotación/composición de clases**.
- **A6** Justificar el gap **detección → clasificación** (§1.8), ligado al binario de B.

### B — Evaluación clínica/melanoma (LOCAL, sobre `y_prob` existentes)
- **B1** **Binario melanoma-vs-resto** y **maligno-vs-benigno** (maligno = {MEL, BCC, AKIEC}; benigno =
  {NV, BKL, DF, VASC} — *confirmar mapeo con el tutor*). Suite: sensibilidad, especificidad, VPN, AUC-ROC,
  PR-AUC, **tasa de falsos negativos de melanoma**, macro-AUC-OvR, AUC/PR-AUC específicas de melanoma.
- **B2** **Fix estadístico:** McNemar se conserva **solo** para acierto pareado (para lo que es válido); se
  **agrega bootstrap pareado** para F1-macro, sens-macro y para las diferencias de **generación** entre
  condiciones sobre las **mismas imágenes** (baseline vs grounding vs oracle).
- Código: extender `scripts/statistical_tests.py` y `src/evaluation/classification.py`; nuevo
  `scripts/melanoma_detection.py`. Salida: `outputs/results/melanoma/`.

### C — Completar la comparación central a 1503 (LOCAL: sync + re-eval)
- **C1** `sync_down` de los reportes `full_{baseline,dermlip,swin,oracle}` de Mini-VLM y LLaVA (1503,
  ya en Mendieta; el login funciona). Re-evaluar consistency + entity recall + taxonomía sobre 1503.
- **C2** Actualizar `tab:ensamble` (y por-clase, taxonomía) a **1503**; quitar el *caveat* de 400 de las
  condiciones centrales (las ablaciones finas quedan en 400 con nota).

### D — Mejorar resultados (LOCAL + TOKO)
- **D1 (melanoma, local):** optimizar el umbral del melanoma (maximizar sensibilidad a especificidad
  objetivo) + **ensamble de clasificadores** (voto suave Swin+ConvNeXt+DermLIP); reportar la suite de B en
  el mejor punto de operación, siempre con la lente de **costo/hardware**.
- **D2 (reportes, TOKO):** consolidar el **pipeline avanzado** e implementar el ruteo de 3 niveles
  (`generate_report.py` ya tiene `--uncertainty`; agregar la capa de **abstención** y el CSV híbrido
  calibración+acuerdo). Generar los ~390 diferenciales en TOKO. Evaluar end-to-end: fidelidad, cobertura,
  y **reducción de "dx incorrecto con falso aplomo"** (la abstención evita el error propagado).
- **D3** Medir el sistema avanzado vs grounding-simple (ablación) end-to-end sobre 1503.

### E — Validación clínica (LOCAL, no bloqueante)
- **E1** Construir la **rúbrica** (claridad, afirmaciones peligrosas/no sustentadas, omisiones, reducción de
  tiempo, utilidad en flujo real/simulado) + planilla + muestra n≈30 de reportes representativos.
- **E2** Proxies automáticos que ya tenemos (diagnostic consistency, entity recall, taxonomía de errores)
  como validación cuantitativa parcial, explicitando que **no reemplazan** a un especialista.
- **E3** Buscar dermatólogo en paralelo; si aparece, ejecutar; si no, dejar como protocolo listo + trabajo
  futuro.

---

## 3. Secuenciación

| Fase | LOCAL (arranca ya) | Cluster |
|------|--------------------|---------|
| **1** | A (pulido), B (melanoma+stats), C (sync+re-eval 1503) | — |
| **2** | D1 (umbral+ensamble melanoma), E1 (rúbrica) | Preparar setup TOKO para D2 |
| **3** | D3 (eval end-to-end), integrar todo al `.tex` + tablas SOTA | D2 generación en TOKO |
| **4** | Escritura/pulido final; E si aparece especialista | Buffer |

**Crítico:** A/B/C y D1 no dependen de ningún cluster → arrancan de inmediato. La única dependencia de
cluster es D2 (generación en TOKO). Mendieta caído **no bloquea** (los reportes existentes se bajan por el
login, que funciona).

---

## 4. Criterios de éxito

- **Feedback cerrado:** los 10 ítems de `feedback_20260805.md` resueltos en el `.tex` (compila).
- **Melanoma:** suite clínica completa reportada + punto de operación optimizado; posicionamiento honesto
  vs SOTA (probablemente "competitivo a bajo costo").
- **1503:** comparación central del ensamble toda sobre 1503 (sin asimetría 400/1503).
- **Sistema avanzado:** pipeline con incertidumbre+RAG+abstención medido end-to-end; abstención reduce el
  error propagado con falso aplomo.
- **Validación clínica:** rúbrica + muestra listas (ejecutadas si hay especialista).
- Todo con la **lente de hardware accesible** explícita.

---

## 5. Sincronización con clústeres

- **Mendieta:** el **scheduler (`slurmctld`) está caído** (no se puede submit/scancel), pero el **login +
  filesystem + `sacct` funcionan** → se puede `sync_down` de reportes/resultados existentes (Workstream C).
  No enviar jobs a Mendieta hasta que CCAD restablezca el scheduler.
- **TOKO (para D2):** `sync_up.py`; **subir al scratch** el checkpoint `stage2_mini_vlm_v2`, los datos
  `data/processed/HAM10000` y el CSV de incertidumbre (scratch es no persistente → job self-contained).
  Adaptar un SLURM de generación para TOKO (partición `gpu`, paths de scratch). **Validar carga local**
  antes de enviar. Usar `sync_up.py` sin `--delete` para no borrar artefactos remotos.
- **Regla de oro:** casi todo el análisis es **local** sobre artefactos existentes; el cluster (TOKO) se
  reserva solo para la generación de los ~390 diferenciales.
- Cada submit se registra en `jobs_log.txt` (auto) + `ejecuciones.md`; cada tarea cerrada con su resul doc.
