# Ficha 2.7 — Estado del arte

Sección del `.tex`: `Chapters/02-Marco-Teorico/07-estado-arte.tex` (hoy `10-estado-arte.tex`).

**Estado: aprobada y redactada (2026-10-12).** El autor aprobó las cuatro decisiones recomendadas. Extensión
resultante: unas 12.5 páginas (p. 46–58 del PDF), contra 15 de la versión anterior, con seis tablas. Responde a la tercera revisión del tutor
(`feedback_cap1_y_2_v3.md`):
- **IDEA para 2.7:** «Clasificación dermatológica, VLM especializados, generación de reportes y posicionamiento de
  la propuesta».
- **Segunda recomendación del proceso de cambios:** el problema principal es la acumulación de información sobre
  trabajos individuales. El tutor pide agrupar «en casos de trabajos similares o que comparten el mismo dataset» y
  fortalecer las conexiones entre trabajos (similitudes, diferencias y aportes) para que se entienda la evolución.
  Pide también distinguir problema, método, resultados y limitaciones. Los antecedentes breves pueden quedar en un
  solo párrafo.
- **Pedido sobre 2.10.4:** registro formal. Ejemplos del tutor:
  - «Cada línea deja algo sin resolver» → «La revisión de las distintas líneas de investigación permite
    identificar limitaciones que aún no han sido abordadas de manera conjunta».
  - «De esos huecos sale el pipeline» → «A partir de las limitaciones identificadas, se propone una arquitectura
    que integra…».
  - «descansan sobre la prueba» → «La evaluación […] se ha realizado principalmente sobre…».

Hoy la sección ocupa unas 15 páginas (p. 69–83) con seis tablas, y el plan del capítulo fija 10–12. Casi todo el
texto actual sigue el patrón que el tutor señala: un párrafo por trabajo con objetivo, arquitectura, datos,
métricas, resultados, expertos, hardware y limitaciones, uno tras otro.

## Hilo conductor

Pregunta que responde la sección: ¿qué resolvieron los trabajos más cercanos en clasificación, en VLM
dermatológicos y en generación de reportes, con qué datos y con qué protocolo lo mostraron, y qué limitaciones
siguen sin abordarse de manera conjunta?

Viene de las secciones anteriores:
- **2.6** cierra con: «Con qué datos y con qué protocolo se evaluó un trabajo decide, entonces, si su resultado se
  sostiene fuera de su conjunto de origen: si se midió en otra fuente, si se desagregó por grupos y si sus
  diferencias con otros modelos se probaron estadísticamente. Ese es el criterio con el que la sección siguiente
  revisa la literatura».
- **2.2–2.5** dejan los conceptos con que se describen los trabajos sin redefinirlos: CNN, ViT, Swin, CLIP, VLM
  generativo, LoRA, las tres salidas y la concordancia, los dos requisitos del reporte, las fallas, la recuperación
  y la generación de extremo a extremo frente a la condicionada.
- **2.6** deja las métricas, la validación externa y la evaluación desagregada.

Deja instalado: las limitaciones de las tres líneas y la tabla `tab:marco_brechas`, que el Cap. 3 convierte en
tareas (`01-tareas.tex` cita `sec:estado_arte_posicion` y `tab:marco_brechas`). También deja los valores
publicados sobre *HAM10000*, que el Cap. 4 compara (`05-comparacion-sota.tex`).

Criterio de redacción para los tres ejes:
- Cada grupo de trabajos dice qué problema comparten, en qué difieren sus métodos, qué muestran sus resultados y
  qué limitación queda.
- En el texto quedan solo las cifras que sostienen el argumento. Arquitectura exacta, tamaños, hardware y
  resultados de detalle van a las tablas, que ya existen y se ajustan (decisión 2).
- Un trabajo secundario ocupa una o dos oraciones dentro de su grupo.

```
(sin subsección: un párrafo de entrada)
P1  Retoma el criterio con que cierra 2.6, sin repetirlo. Nombra las tres líneas que se revisan. Fija el período
    (2020–2026, con los trabajos anteriores solo como hitos fechados) y advierte que los trabajos sin revisión de
    pares se marcan                                                                      orienta
    ↓ necesidad — la primera línea es la más antigua

2.7.1 Clasificación dermatológica (sec:estado_arte_diagnostico)
P2  Problema y protocolo habitual: asignar una categoría a imágenes dermatoscópicas (desafíos ISIC, HAM10000) o
    clínicas. Con el criterio de 2.6, se mira si cada trabajo usa una métrica que no oculte las clases
    minoritarias, si separa las imágenes de una lesión entre particiones (fuga de información, 2.1), si valida en
    otra fuente y si se compara con clínicos. Remite a tab:marco_sota_clasificacion            orienta
P3  Hitos de 2017 y 2019 [esteva, tschandl]: plantearon la tarea como una comparación con el especialista
                                                                                         contextualiza
    ↓ consecuencia — los trabajos siguientes se midieron sobre todo dentro de los desafíos
P4  Grupo «desafíos ISIC y desbalance» [gessert2020skin, yao2022single]. Problema común: clases desbalanceadas,
    con la sensibilidad macro como métrica. Gessert: ensamble con ponderación inversa y partición por lesión.
    Yao: un único modelo con una pérdida que pesa más el melanoma, que eleva su sensibilidad a costa de la macro.
    Limitación común: evalúan sobre la prueba del desafío, y Yao selecciona sobre ella. Única cifra: la brecha
    de Gessert entre validación cruzada y prueba oficial                                  analiza
    ↓ contraste — salir del banco de pruebas
P5  Grupo «fuera del desafío, con clínicos» [liu2020deep, marchetti2023prospective]. Liu pasa a atención primaria
    con partición temporal por paciente y supera a los clínicos en el promedio, pero no en los tumores malignos.
    Marchetti valida de forma prospectiva, con biopsia: sensibilidad alta, especificidad baja. Limitación común:
    una partición temporal o un solo centro, sin fototipos V y VI                          analiza
    ↓ contraste — los trabajos recientes vuelven a la comparación entre redes
P6  Grupo «trabajos recientes sobre HAM10000 y afines» [kreouzi2024learning, aboulmira2024skinhealthmate,
    kim2025skinsavvy2]. Comparan arquitecturas o ensambles por exactitud, sin un protocolo común ni expertos. La
    exactitud de 93 % de Aboulmira, junto a su sensibilidad de melanoma de 0.49, muestra lo que la exactitud
    oculta (2.6.2). Kim es el único con un transformer (Swin) y amplía HAM10000 con imágenes externas
                                                                                         analiza
P7  Dos de ellos agregan un texto generado sobre la predicción [khan2025ensemble, kim2025skinsavvy2]. Khan además
    marca para revisión los casos en que su ensamble discrepa. Remite a 2.7.3 sin desarrollarlos     enlaza
P8  Síntesis, en registro formal. Evolución: de los desafíos a la clínica, y de vuelta a la comparación entre
    redes. Limitaciones pendientes: predominan las CNN; pocas particiones por lesión o por paciente; validación
    externa escasa y ninguna en población latinoamericana; los mejores sistemas son ensambles grandes; la
    abstención no se mide                                                                 sintetiza
    ↓ necesidad — los VLM agregan el texto a la clasificación

2.7.2 Modelos visión–lenguaje especializados en dermatología (sec:estado_arte_vlm)
P9  Las dos vías de 2.3: la contrastiva, que clasifica sin ajuste y recupera casos, y la generativa. Más una
    tercera línea de evaluación crítica. Remite a tab:marco_sota_vlm y tab:marco_sota_vlm_gen       orienta
P10 Contrastivos [kim2024transparent, yan2025derm1miccv, yan2025makemiccai]. La evolución es la del texto de
    entrenamiento: literatura (MONET, para auditar conceptos), un corpus de un millón de pares con ontología
    (DermLIP) y descripciones divididas por aspecto (MAKE). Comparten la evaluación *zero-shot* en conjuntos
    públicos y la falta de estudios con clínicos. Una cifra: DermLIP frente a BiomedCLIP      analiza
P11 Fundacionales visuales [yan2025vision, yan2026dermfmzero], del mismo grupo: el preentrenamiento crece a
    millones de imágenes y entran los estudios de lectura con clínicos. El costo es de cuatro H100. DermFM-Zero
    supera a DermLIP en su propio protocolo                                                analiza
    ↓ contraste — la otra vía genera texto
P12 Generativos, del propósito general a la piel [li2023llavamed, moor2023medflamingo, he2025pefomed,
    xie2025medtrinity25m, zeng2025mmskin]. LLaVA-Med y sus pares se evalúan en radiología y patología, no en
    piel. SkinVL adapta LLaVA-Med con LoRA y es el único que supera 50 % en HAM10000 *zero-shot*. Se conserva la
    aclaración sobre la variante SkinVL-MM (commit 08711d6)                                  analiza
P13 Generativos que razonan [shen2025skingptr1, ru2026dermogpt]: un orden clínico explícito (morfología,
    razonamiento, diagnóstico) y aprendizaje por refuerzo. Cuentan con dermatólogos, pero solo para evaluar las
    salidas del propio modelo, y el cómputo es alto                                        analiza
    ↓ contraste — ¿cuánto rinden fuera de los conjuntos públicos?
P14 Evaluación crítica [jiang2026multimodal], de un grupo independiente: con consultas reales y la imagen sola, la
    exactitud cae a niveles muy por debajo de la de los conjuntos públicos             analiza
P15 Síntesis. Evolución de las dos vías. Pendiente: ningún trabajo combina un clasificador supervisado con un
    generador ni recupera casos para anclar el texto; la incertidumbre aparece como limitación y no como decisión
    (2.4.4); el cómputo es alto; hay pocos estudios con clínicos                           sintetiza
    ↓ necesidad — el reporte como producto

2.7.3 Generación de reportes dermatológicos (sec:estado_arte_reportes)
P16 Retoma 2.5: cómo se produce el texto (de extremo a extremo o condicionado, 2.5.3), con qué evidencia y cómo
    se evalúa (los dos requisitos de 2.5.2). Remite a tab:marco_generadores y tab:marco_sota_reportes  orienta
P17 De extremo a extremo, con el acceso como objetivo [zhou2024pretrained, yilmaz2025resourceefficient].
    SkinGPT-4 y DermatoLlama buscan el acceso sin especialista o la ejecución local, pero difieren en cómo
    evalúan: cinco dermatólogos sobre casos reales frente a métricas con referencia sobre textos sintéticos.
    SkinVL y SkinGPT-R1 se nombran sin repetirlos                                         analiza
P18 Razonamiento en lugar de reporte [liu2025skinr1]: lo evalúa con preguntas de opción múltiple, no mide el texto
    del razonamiento, y SkinVL casi no responde con ese formato. Se relaciona con P13      analiza
    ↓ contraste — separar diagnóstico y redacción
P19 Condicionados en un clasificador [khan2025ensemble, kim2025skinsavvy2]: el modelo de lenguaje recibe la clase
    predicha y no la imagen, y redacta recomendaciones. Se evalúan con una rúbrica propia o con una encuesta, sin
    reportes clínicos de referencia                                                       analiza
P20 Destilación con plantilla clínica [chakrabarti2025skin]: pseudorreportes de GPT-4V según la lista de 7 puntos,
    con variantes de recuperación. Como la referencia la escribe el maestro, las métricas miden el parecido con
    GPT-4V; los autores lo reconocen                                                      analiza
    ↓ ampliación — dos líneas que complementan a los generadores
P21 Evaluación del texto [shen2025dermbench]: un juez con referencia y un evaluador sin referencia, comparados con
    médicos; las referencias se redactan con modelos                                       analiza
P22 Recuperación [xia2025mmedrag, xia2024rule]: recuperan reportes de texto en radiología y oftalmología, ajustan
    el generador para que use el contexto solo cuando ayuda y muestran que un contexto equivocado degrada la
    respuesta                                                                             analiza
P23 Síntesis: el texto se evalúa de tres maneras que casi no se combinan; hay pocos expertos; se recuperan textos
    y no imágenes; varios sistemas dependen de modelos cerrados o consultados por API      sintetiza
    ↓ consecuencia — las limitaciones de las tres líneas

2.7.4 Posicionamiento de la propuesta (sec:estado_arte_posicion)
P24 «La revisión de las tres líneas permite identificar limitaciones que no han sido abordadas de manera
    conjunta», una oración por línea, sin «descansan» ni «huecos»                       sintetiza
P25 «A partir de las limitaciones identificadas, se propone…»: clasificador, recuperación de casos y generador,
    con una regla de decisión que fija cuánto afirma el texto. Remite a tab:marco_brechas, con sus cuatro filas,
    porque el Cap. 3 cita «tres de las cuatro brechas». Agrega el análisis del vecino equivocado
    [xia2025mmedrag, xia2024rule]                                                         justifica
P26 Por qué DermLIP (se ejecuta en una GPU de consumo, y un mismo espacio clasifica, entrena el clasificador lineal
    y recupera) y LoRA                                                                    justifica
P27 Las dos excepciones (decisión vigente 8) y la remisión al Cap. 3                    limita
→ Fin del capítulo; no hay transición a otra sección.

Se definen acá: nada conceptual. Solo se nombran trabajos, conjuntos y modelos.
Se retoman de antes (solo se nombran, con \ref): CNN, Swin (2.2); CLIP, VLM generativo, LoRA (2.3); tres
salidas, concordancia, regla de decisión (2.4); requisitos del reporte, generación de extremo a extremo y
condicionada, recuperación (2.5); métricas, validación externa (2.6).
Extensión: 27 párrafos y seis tablas (una menos si se aprueba la decisión 3), unas 11–12 páginas.
```

## Qué cambia respecto del texto actual

| Comentario o pedido | Cambio |
|---|---|
| IDEA del tutor | Títulos: «Clasificación dermatológica», «Modelos visión–lenguaje especializados en dermatología», «Generación de reportes dermatológicos» y «Posicionamiento de la propuesta». Labels sin cambios |
| Acumulación de información por trabajo | Los párrafos pasan a ser por grupo (P4, P5, P6, P10, P11, P13, P17, P19). Cada uno dice qué comparten los trabajos, en qué difieren y qué limitación queda. Arquitectura exacta, tamaños, hardware y cifras secundarias salen del texto, porque ya están en las tablas |
| Conexiones y evolución | Cada grupo abre con su relación con el anterior: contraste, consecuencia o ampliación (las flechas del hilo) |
| Registro formal en 2.10.4 | P24–P25 con las fórmulas del tutor. Salen «Cada línea deja algo sin resolver», «De esos huecos sale», «descansan» y «no redactan» (que pasa a «no generan texto») |
| Expresiones imprecisas (mensaje general) | Salen «reportan» en el sentido de informar resultados (guía §4: «reporte» es solo el informe clínico), «exactitudes altas», «rinden poco» y «más chico». Cada uno se reemplaza por la cifra o por una comparación concreta |
| Vínculo con 2.6 | La entrada de cada eje dice qué se mira con el criterio de 2.6: métrica, partición, otra fuente, clínicos |
| Trabajos que no aportan al argumento | Salen SkinGEN y MpoxVLM (decisión 3) |
| Extensión | De unas 15 páginas a 11–12 |

## Verificación

- Las cifras que quedan ya están en el texto actual, que se verificó contra los PDF (decisión vigente 8). No entra
  ninguna cifra nueva; solo se quitan o se pasan a las tablas.
- Hay referencias desde otros capítulos:
  - el Cap. 3, en la otra rama, cita `sec:estado_arte_posicion` y `tab:marco_brechas` («tres de las cuatro
    brechas»);
  - el Cap. 4 (`05-comparacion-sota.tex`, pendiente) y el Cap. 6 (`02-dominio-modalidad.tex`) citan
    `sec:estado_arte`.

  Se conservan los labels y las cuatro filas de la tabla de brechas.

## Archivos y labels

- `git mv 10-estado-arte.tex 07-estado-arte.tex`, y `00-capitulo.tex` cambia ese `\input`. La ficha vieja
  `10-estado-arte.md` pasa a `historial.md`.
- Se conservan los labels de sección `sec:estado_arte`, `sec:estado_arte_diagnostico`, `sec:estado_arte_vlm`,
  `sec:estado_arte_reportes` y `sec:estado_arte_posicion`.
- Tablas: `tab:marco_sota_clasificacion`, `tab:marco_sota_vlm`, `tab:marco_sota_vlm_gen`, `tab:marco_generadores`,
  `tab:marco_sota_reportes` y `tab:marco_brechas`. La fila de MpoxVLM sale de `tab:marco_generadores` (decisión 3).
- Las tablas pasan de `[!t]` a `[H]` o se colocan donde las cita el texto, para que queden en la página de su
  mención (hoy `check_floats` marca las tablas 2.3 a 2.8 fuera de lugar).

## Citas

Se mantienen todas, salvo `lin2025skingen` y `cao2024mpoxvlm` (decisión 3). No hay citas nuevas.

## Respuestas del autor (2026-10-12)

Las cuatro aprobadas como se recomendaron. La decisión 2 reemplaza, en lo que hace a los valores, la decisión
vigente 8 de `00-capitulo.md`.

Ajustes de la redacción que no estaban en la propuesta:
- Los nombres de conjuntos de datos van en cursiva también dentro de las tablas, y «18 lectores» pasa a «18
  participantes» (guía §4).
- P5 menciona que el ensamble de Marchetti suma 90 redes por imagen, porque la tabla de brechas lo cita.
- Las tablas son flotantes `[!htb]`. Con `[H]`, como estaban en la propuesta de «Archivos y labels», dejaban
  media página en blanco, porque casi todas ocupan entre media página y una página entera. Como flotantes,
  cinco de las seis quedan en la página siguiente a su mención, que es lo esperable para tablas de ese
  tamaño; `check_floats` las marca igual.

Decisiones (texto de la propuesta):

1. **Reorganizar por grupos con los títulos del tutor** (recomendado). Es el pedido central de la revisión. En
   clasificación, los grupos son los desafíos ISIC, los trabajos fuera del desafío con clínicos y los trabajos
   recientes sobre *HAM10000*. En VLM: contrastivos, fundacionales visuales, generativos adaptados, generativos
   que razonan y evaluación crítica. En reportes: de extremo a extremo, condicionados en un clasificador,
   destilación, evaluación y recuperación.
2. **Conservar los valores en las tablas** (recomendado). El texto queda con las cifras que sostienen el
   argumento, y las tablas guardan el resultado principal de cada trabajo, que el Cap. 4 necesita para comparar
   sobre *HAM10000*. Esto corrige la decisión vigente 8 («las tablas dicen qué evalúa cada trabajo y con qué
   hardware, no los valores»), que las tablas actuales ya no cumplen. Alternativa: sacar la columna «Resultado
   principal» y dejar las cifras solo en el texto.
3. **Sacar SkinGEN y MpoxVLM** (recomendado). Uno genera imágenes de referencia por difusión y el otro diagnostica
   una sola enfermedad. Ninguno interviene en la síntesis ni en el posicionamiento, y hoy ocupan una oración sin
   análisis. Alternativa: dejarlos en una oración como hoy.
4. **Sin trabajos nuevos en esta pasada** (recomendado). Hay 8 trabajos en clasificación, 10 en VLM y unos 9 en
   reportes; el tutor pedía 6–8 por eje. Agregar trabajos exige verificar cada uno contra el PDF. Si la otra
   persona que preparaba los trabajos de S3 los tiene listos, se incorporan en una pasada aparte.
