# Ficha 3.2 — Flujo de trabajo

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/02-flujo-trabajo.tex` (absorbe `01-metodologia.tex` y `08-infraestructura.tex`). Labels: `sec:met_metodologia` (la sección) y `sec:met_infra` (la subsección 3.2.2). Figura: `fig:met_flujo`. Tabla: `tab:met_entorno`.

## Hilo conductor

Pregunta que responde la sección: ¿cómo se avanzó de la definición de las tareas a los experimentos, con qué registro y en qué entorno, y por qué los Caps. 4 y 5 presentan los resultados en ese orden?

Viene de: 3.1 define las tres tareas (clasificación en siete clases, detección binaria de melanoma derivada de la clasificación, generación del reporte), sus entradas y salidas, las preguntas PI1 y PI2 y la restricción de una GPU de consumo. *La ficha 3.1 todavía no existe: lo tomado es el hilo del capítulo (`00-capitulo.md`); verificar al aprobar 3.1.*

Deja instalado: para 3.3, (a) que los datos son la primera etapa del flujo; (b) que la partición disjunta por lesión entró al ciclo como corrección de una auditoría, y que los resultados se rehicieron sobre ella; (c) que los conjuntos no están versionados en el repositorio: se descargan a mano y se procesan con scripts. Para 3.4–3.9: el registro de cada corrida (plan, ejecución, resultado con veredicto) y la numeración de versiones (`v1`, `v2`…) a la que remiten las fichas.

```
3.2.1  Recorrido iterativo y registro de experimentos
P1  El trabajo fue un ciclo iterativo: cada resultado define el siguiente experimento y varias decisiones
    nacieron de refutar la hipótesis anterior. La figura muestra ese recorrido. Los Caps. 4 y 5 presentan
    los resultados en el orden de estas decisiones                        función: define
    ↓ necesidad — para que el ciclo sea comprobable, cada paso deja un registro escrito
P2  Cada iteración tiene tres documentos: plan antes de enviar jobs, registro de cada corrida y resultado
    con veredicto cumple / no cumple que decide el paso siguiente. Si no cumple, se abre una iteración nueva
    sin sobrescribir la anterior                                          función: define
    ↓ consecuencia — cada decisión queda asociada a un criterio escrito antes de conocer el resultado
P3  Tramo 1. Los clasificadores supervisados fijan la línea base. Los VLM generales colapsan en
    clasificación. La hipótesis inicial fue el desbalance de clases: no se sostuvo, porque el colapso aparece
    también sin entrenamiento y cada modelo colapsa en una clase distinta. Refutada, la hipótesis cambió el
    rumbo hacia la especialización de dominio                            función: describe
    ↓ contraste — el mismo problema, con otro diagnóstico y otro modelo
P4  Tramo 2. Un VLM especializado en dermatología (DermLIP) recupera la capacidad de discriminar. La
    generación de reportes no alcanza fidelidad diagnóstica por sí sola, y de ahí surge la cascada: el
    clasificador fija el diagnóstico y el generador redacta a partir de él. El ruteo por incertidumbre en tres
    niveles cierra el recorrido de decisiones                             función: describe
    ↓ problema — la evaluación de la cascada expuso una fuga entre particiones
P5  Corrección. La revisión del tutor (12/09/2026) pidió verificar que una misma lesión no cayera en
    entrenamiento y prueba. La auditoría lo confirmó: el recorrido anterior se hizo con particiones por
    imagen. Se migró a la partición disjunta por lesión, se re-ancló la cascada y se regeneró la recuperación
    (RAG). Los análisis complementarios (calibración, robustez, interpretabilidad, costo) van al final de cada
    capítulo porque se aplican a modelos ya presentados                   función: justifica · limita

3.2.2  Infraestructura y reproducibilidad
P6  Tres entornos. La GPU local (RTX 4070, 12 GB) sirve para depurar, correr pruebas rápidas y análisis.
    TOKO (RTX 4080, 16 GB) tiene cola corta y se usa para clasificadores y barridos. Mendieta (A30, 24 GB)
    tiene cola de varios días y se usa para el ajuste y la generación de los VLM. Los trabajos se envían con
    SLURM desde un mismo gestor, cada envío queda en un registro, y los barridos guardan sus corridas en
    wandb sin conexión (tabla `tab:met_entorno`)                          función: describe
    ↓ necesidad — los resultados solo son comparables si se sabe con qué semilla, código y dependencias se obtuvieron
P7  Reproducibilidad: semilla fija (42) y algoritmos deterministas en GPUs Ampere o posteriores; los
    hiperparámetros están solo en los YAML; los resultados se versionan sin sobrescribir; los datos se
    descargan a mano y los nodos de Mendieta, sin internet, usan modelos precargados. Límites: las
    dependencias se declaran con rangos y cada clúster usa una versión distinta de CUDA, así que las cifras
    no son reproducibles bit a bit entre clústeres. El detalle, en el Apéndice~\ref{ap:reproducibilidad}
                                                                          función: justifica · limita
→ Transición a la sección siguiente: «La primera etapa del flujo son los datos: qué conjuntos se usan, qué
  rol cumple cada uno y con qué partición se evalúa todo lo que sigue.»

Se definen acá (y no se vuelven a definir): ciclo iterativo (hipótesis → ejecución → análisis → decisión),
plan, registro de ejecuciones y veredicto de cumplimiento; versión de iteración (`vN`); figura del recorrido;
los tres entornos y su rol.
Se retoman de antes (solo se nombran, con \ref): tareas y restricción de cómputo (3.1); desbalance
(`sec:marco_desbalance`); VLM y clasificación por verosimilitud (`sec:marco_vlm`); LoRA (`sec:marco_llm_lora`);
fuga de información (`sec:marco_regularizacion`); RAG (`sec:marco_rag`); incertidumbre (`sec:marco_incertidumbre`).
Extensión: 7 párrafos, con figura (media página aprox.) y tabla (un tercio aprox.): unas 2.5–3 páginas. Excede
en media página la estimación de `00-capitulo.md` (2–2.5); si hace falta, la tabla pasa al Apéndice E.
```

## Subsecciones

- **3.2.1 Recorrido iterativo y registro de experimentos.** P1–P5 y la figura. Explica el ciclo, el orden de las decisiones y la corrección por fuga.
- **3.2.2 Infraestructura y reproducibilidad.** P6–P7 y la tabla de entornos. Lleva `sec:met_infra`. Mismo título que el andamiaje (`08-infraestructura.tex`).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas o `\ref`) |
|---|---|---|---|
| P1 | Ciclo iterativo; las decisiones siguen a los resultados; el orden de los Caps. 4 y 5 es el de las decisiones | `Codigo/docs/ejecuciones.md`: 67 entradas, desde el 1 de mayo de 2026. `Codigo/docs/ideas/`: 23 planes, el primero del 24 de abril (`vlm_clasificacion_v1_plan_20260424.md`). El orden de los caps: `Chapters/04-Resultados-Clasificacion/00-capitulo.tex` (intro: «en el orden en que se tomaron las decisiones»). | — |
| P2 | Tres documentos por iteración: plan antes del envío (motivación, diseño, hiperparámetros, criterio cuantitativo); una entrada en el registro por corrida, también las locales (marcadas «Sin jobs SLURM»); resultado con veredicto; `vN+1` sin sobrescribir | `Codigo/CLAUDE.md`, sección «Metodología de Experimentación» y «Reglas para Claude». `Codigo/docs/resul/`: 35 archivos `.md`; 6 sin sección de veredicto (ver pregunta 1). Versionado: `outputs/` y `slurm/{cluster}/v1…v4` (Mendieta). | — |
| P3 | Línea base supervisada; VLM generales colapsan; hipótesis del desbalance; refutación el 3 de junio de 2026 (plan anulado: su premisa era falsa, el colapso aparece en zero-shot y cada modelo colapsa en una clase distinta); cambio de rumbo hacia la especialización de dominio | `resul/clasificadores_resul_iteraciones_20260429.md`, `resul/clasificadores_resul_final_20260501.md`; `resul/vlm_clasificacion_resul_v3_20260517.md` (§5.4, «NO CUMPLE criterio gating»); `ideas/reportes_mejoras_v3_class_weights_plan_20260525.md` (encabezado «PLAN ANULADO (2026-06-03)»); `ejecuciones.md`, entrada 2026-06-03 «Re-diagnóstico del class collapse». La hipótesis se volvió a probar: `resul/desbalance_resul_20260707.md`, `resul/desbalance_multimodelo_resul_20260725.md`. **Sin cifras en la ficha.** | `sec:marco_desbalance`, `sec:marco_vlm` |
| P4 | DermLIP recupera la discriminación (test de la hipótesis de dominio); la generación v2 no mejora la consistencia frente a v1; el análisis mostró un problema de fidelidad diagnóstica; cascada clasificador → generador con grounding; ruteo en tres niveles | `resul/vlm_domain_gap_clinica_resul_20260604.md`; `resul/dermlip_clasificacion_resul_20260605.md`; `resul/reportes_resul_v2_20260517.md` («NO CUMPLE GATING»); `resul/ensamble_resul_20260607.md`; `resul/incertidumbre_3niveles_resul_20260805.md`; `resul/analisis_pipeline_avanzado_resul_20260908.md`. El problema de fidelidad: `Docs/experimentacion/experimentacion.tex`, introducción (solo como argumento; sus cifras son de la partición vieja). | `sec:marco_vlm`, `sec:marco_incertidumbre`, `sec:marco_rag` |
| P5 | Revisión del tutor (12/09/2026) sobre la fuga entre train y test y la selección en validación; auditoría; migración a partición disjunta por lesión; re-anclaje de la cascada y regeneración de RAG; revisión del 03/10 (métrica oficial y decisiones); análisis complementarios al final | `ideas/split_lesion_semillas_plan_20260912.md` (origen: `Codigo/docs/feedback_20260912.md`; auditoría: `scripts/leakage_analysis.py`); `resul/split_lesion_resul_20260926.md` (CUMPLE con matiz); `resul/reanclaje_cascada_resul_20261003.md`; `resul/revision_experimentacion_20261003.md` (§4–5). Las cifras de la fuga van en 3.3. | `sec:met_particiones` (3.3, todavía sin escribir) |
| P6 | Tres entornos (local, TOKO, Mendieta) con su GPU, cola y uso; envío con SLURM desde `cluster_manager.py`; registro de envíos; seguimiento con wandb sin conexión | `Codigo/CLAUDE.md` (secciones «Stack», «Clusters HPC», «Hardware y Precisión»); `Codigo/subir_toko.md`; `Codigo/subir_mendieta.md` (tabla «Diferencias con TOKO»); `scripts/cluster_manager.py` (`CLUSTER_OPTIONS`); `jobs_log.txt` (escrito por `scripts/mendieta/submit.py`, según `CLAUDE.md`); `Codigo/configs/base.yaml` (`wandb.enabled: false`); `subir_toko.md` §2c (`WANDB_MODE=offline`). | — |
| P7 | Semilla 42 y determinismo en Ampere o posteriores; YAML como única fuente de hiperparámetros; versiones sin sobrescribir; datos manuales; Mendieta sin internet (modelos precargados, `HF_HUB_OFFLINE=1`); límites: dependencias con rangos y CUDA distinto por clúster | `Codigo/configs/base.yaml` (`seed: 42`); `src/utils/seed.py` (`set_seed`, `CUBLAS_WORKSPACE_CONFIG`, algoritmos deterministas en SM ≥ 8.0); `Codigo/requirements.txt` (rangos, p. ej. `transformers>=4.40.0,<4.44.0`); `Codigo/docs/USAGE.md` §1.2 (CUDA 12.8 para la GPU local) y §2 (datos manuales; SkinCaRe gated con `HF_TOKEN`); `subir_mendieta.md` §1.5 (modelos precargados). Versiones de CUDA: cu121 (Mendieta), cu126 (TOKO), cu128 (local, a verificar). | `\ref{ap:reproducibilidad}` |

## Figuras y tablas

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Figura `fig:met_flujo` (3.2.1) | Recorrido iterativo, con los bucles de refutación y de auditoría, e inset del ciclo de cada iteración. Sin cifras ni fechas (ver D2). | Decisiones del Hilo conductor; estilos de `Configurations/13-Figuras.sty` | a dibujar, en `Figures/Capitulos/03-Materiales-Metodos/flujo_trabajo.tex` |
| Tabla `tab:met_entorno` (3.2.2) | Tres filas: local, TOKO, Mendieta. Columnas: GPU y memoria, arquitectura y CUDA, cola, uso en el trabajo. | `Codigo/CLAUDE.md`; `subir_toko.md`; `subir_mendieta.md`; `USAGE.md` §1.2 | a armar |

**Especificación de la figura** (TikZ, un archivo, flotante completo con `[H]`; colores de la paleta Okabe–Ito del archivo, legibles en blanco y negro):

```
Fila 1 (izq. a der.):  N1 Baseline supervisado → N2 VLM generales: colapso → N3 Hipótesis: desbalance
                                                                             ⇣ «refutada» (bermellón, discontinua)
                                                       R  Refutada: el colapso aparece sin entrenamiento
                                                                             ⇣ «rumbo: dominio»
Fila 1 (cont.):        N4 Hipótesis: falta de especialización de dominio → N5 DermLIP: discrimina
Fila 2 (der. a izq.):  N6 Generación de reportes (fidelidad) ← N5 (baja)
                       N7 Cascada: clasificador → generador con grounding ← N6
                       N8 Ruteo por incertidumbre (tres niveles) ← N7
Bucle punteado:        N9 Auditoría de fuga: partición por lesión ⇢ «re-anclaje» hacia N7
Inset (figgrupo «Cada iteración»): Plan (docs/ideas) → Ejecución (ejecuciones.md) → Resultado con veredicto (docs/resul) → Decisión; retorno «no cumple: vN+1»
```

Estilos: hipótesis, `figentrada` (azul); VLM, generación, cascada y DermLIP, `figtarea` (naranja); ruteo, `figsalida` (verde, discontinua); refutación y su flecha, `figbermellon` con trazo discontinuo y `figetiqueta`; auditoría, `figceleste`; inset, `figgrupo`. Las etiquetas no tocan recuadros ni flechas (guía §7).

## Prosa ya escrita que se conserva

Ninguna. `01-metodologia.tex` y `08-infraestructura.tex` contienen solo `\pendiente{}`. Su texto pendiente sirve de guía y se cumple: ciclo hipótesis → ejecución → análisis → decisión, plan con criterio de éxito, veredicto binario, orden de los capítulos según las decisiones, GPU local, TOKO y Mendieta, SLURM, seguimiento de experimentos y remisión a `ap:reproducibilidad`.

## Lo que va al apéndice

Apéndice E (`Chapters/Apendices/E-Reproducibilidad.tex`, hoy solo `\pendiente{}`): estructura del repositorio; versiones de software por entorno; formato de la entrada en `ejecuciones.md` con un ejemplo; convención de `slurm/{cluster}/vN` y `outputs/` versionado; alias de envío y comandos de sincronización (`submit`, `sync_up`, `sync_down`, `monitor`, `clean_remote`); comandos para reproducir cada tabla; diferencias entre clústeres (partición, CUDA, scratch). Si hace falta espacio en 3.2, también la tabla `tab:met_entorno`.

## Lo que NO va en esta sección (y dónde está)

- Resultados, cifras de desempeño y de costo: Caps. 4 y 5 (costo en 5.10).
- Definición de las tareas y de las siete clases: 3.1.
- Conjuntos, tamaños, fuga cuantificada, partición y `StratifiedGroupKFold`: 3.3.
- Métricas, criterio de selección, líneas base y umbral de melanoma: 3.4.
- Hiperparámetros explorados y receta: 3.5; grillas completas en el Apéndice A (`ap:hiperparametros`).
- Prompts y plantillas: Apéndice B (`ap:prompts`).
- Detalle de cada iteración (hipótesis, configuración, causas de fallo): la sección de cada resultado en los Caps. 4 y 5.
- Historial de decisiones de la ficha de referencia (D1–D8 de la ficha del capítulo): no es contenido de la tesina.

## Preguntas abiertas para el autor

1. **Veredicto binario.** Seis de los 35 archivos de `Codigo/docs/resul/` no tienen sección de veredicto: `INFORME_TECNICO.md`, `clasificadores_resul_iteraciones_20260429.md`, `clasificadores_resul_final_20260501.md`, `clasificadores_resul_sweep_v4_20260510.md`, `reportes_resul_v1_20260503.md`, `vlm_clasificacion_resul_v2_20260510.md`. Otros cierran con veredicto condicionado: «CUMPLE con correcciones» (`revision_experimentacion_20261003.md`) y «CUMPLE, con un matiz» (`split_lesion_resul_20260926.md`). ¿La sección dice «cumple / no cumple» como regla y los matices van dentro del resul? ¿Se completan los seis antes de citarlos?
2. **Roles de clúster.** `plan-julio-agosto.md` dice «TOKO solo clasificadores», pero el registro muestra VLM en TOKO (jobs 97463 y 97464, prior del lenguaje; LLaVA-Med stage 1). Propuesta para 3.2: TOKO para clasificadores, barridos y algunos VLM de primera etapa; Mendieta para el ajuste de larga duración, la generación y el re-anclaje. ¿Confirmar?
3. **Scratch de TOKO.** `CLAUDE.md` dice «no persistente entre jobs»; `subir_mendieta.md` dice «`~/scratch/` (persistente)». Verificar antes de escribir la tabla.
4. **Clúster de Mini-VLM en el costo.** `costo_resul_20260705.md` marca Mini-VLM como «A30 / RTX 4080» y toma la latencia de logs A30. ¿En qué clúster corrió la generación de Mini-VLM? Dato para 3.2 y 5.10; no es un resultado.
5. **Partición en el recorrido.** Los tramos 1 y 2 se recorrieron con particiones por imagen. ¿3.2 lo dice (con la fecha de la migración, como en P5) o lo deja a 3.3?
6. **Auditoría externa del 03/10/2026.** El registro menciona una segunda opinión de otro modelo. ¿Se menciona en la metodología por trazabilidad?
7. **Nombre del resul `plantilla_resul_20260707.md`.** Es el resultado de la plantilla clínica (baseline de generación), no una plantilla de resultados. Con la plantilla UMU y las plantillas clínicas de 5.x puede confundir. No se renombró; proponer nombre si se quiere.
8. **Versiones de dependencias.** `requirements.txt` declara rangos y no versiones exactas. ¿Se listan las versiones instaladas en cada entorno (salida de `pip freeze`) en el Apéndice E? Verificar cuáles.
9. **Referencia sobre reproducibilidad.** Ninguna clave del `.bib` trata el tema. Candidata para `refs_pendientes.md`: Pineau et al., «Improving Reproducibility in Machine Learning Research» (JMLR, 2021). Datos completos (volumen, número, DOI) a verificar antes de proponerla. Sin ella, 3.2 no lleva ninguna cita.
10. **Siglas.** `Matter/05-Acronyms.tex` no declara SLURM, GPU ni CUDA. Si se usan con `\gls{}`, hay que declararlas con `\acronimo`.
11. **Figura y fuga.** ¿El bucle de la auditoría (12/09) va en la figura, como se propone (N9), o solo en el texto?
12. **Extensión.** Si la sección excede las 2.5 páginas, ¿la tabla de entornos pasa al Apéndice E?
13. **Numeración.** La figura será la primera del capítulo si 3.1 no lleva figura; confirmar cuando se escriba 3.1 (para el `\ref` y el número).
14. **Apéndice E.** Hoy es solo `\pendiente{}`. 3.2 lo remite, así que debe existir antes de cerrar la sección.
15. **Alcance de «el orden de las decisiones».** P1 afirma que los Caps. 4 y 5 siguen el orden de las decisiones, pero los análisis complementarios (4.6–4.9 y 5.10) son de julio y agosto y se aplican a modelos ya presentados; no son decisiones tomadas a partir de un resultado previo. ¿La frase se limita a 4.1–4.4, 5.1–5.3 y 5.7–5.8?

## Decisiones tomadas por cuenta propia

- **D1. Dos subsecciones.** 3.2.1 «Recorrido iterativo y registro de experimentos» y 3.2.2 «Infraestructura y reproducibilidad». `sec:met_metodologia` queda en la sección y `sec:met_infra` en 3.2.2, que es lo que describe el archivo 08 hoy.
- **D2. La figura sigue el orden del argumento, no el calendario.** Sin fechas en la figura, porque la generación de reportes corrió en paralelo desde mayo y en la figura aparece en el tramo 2 por lógica. Las dos fechas que cambian el rumbo van en el texto: la refutación del 3 de junio de 2026 y la revisión del 12 de septiembre de 2026.
- **D3. Entornos en tabla.** `tab:met_entorno` con tres filas, para que 3.5–3.8 remitan a ella sin repetir hardware.
- **D4. Veredicto binario.** El texto dice «cumple / no cumple», como `CLAUDE.md` y la guía. Los matices no se mencionan en 3.2 hasta resolver la pregunta 1.
- **D5. Sin citas.** La sección no cita claves del `.bib`; no hay una de reproducibilidad (pregunta 9).
- **D6. Términos.** «Registro de ejecuciones» (no «log») y «veredicto» (no «conclusión»). «Pipeline» para la arquitectura completa, como fija la guía §4. «Conjunto de datos» para los datos. «Clasificación por verosimilitud» (no «scoring»). Se evita «sistema» salvo en usos genéricos.
- **D7. Los números de la sección son de configuración o de datos.** Solo aparecen: 12 GB, 16 GB, 24 GB, semilla 42, cola de varios días, y las fechas. Sin desempeño ni costo.
