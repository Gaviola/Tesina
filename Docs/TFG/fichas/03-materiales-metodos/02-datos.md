# Ficha 3.2 — Conjuntos de datos

**Revisión del tutor (21/10/2026), aplicada el 22/10:** P1 describe los cinco conjuntos; P2 explica su uso en la experimentación y por qué *HAM10000* es el central (comentarios 8–10); la columna de la tabla pasa a «Uso». Partición reescrita: 70/15/15 explicado con palabras, la fuga en un párrafo propio, sin «así está hecha» (11–13). «Cuánto inflaba la fuga los resultados» → «cuánto sobreestimaba la fuga el desempeño» (14). *SkinCaRe*: los «dos subconjuntos con textos de distinto tipo» en lugar de «en dos partes» (15). Cierre nuevo: cómo los datos orientan la elección de los modelos (opción elegida por el autor el 22/10).

**Revisión del autor (20/10/2026):** el costo de la partición por lesión se dice en imágenes («un 8 % menos de imágenes de entrenamiento que la partición original, 6 447 frente a 7 010»; `ham10000_splits.json` tiene 7 010 en train); MM-Skin ya no da el tamaño de su prueba (1 653 contaba 3 entradas `.DS_Store`): remite a 3.3, que da 1 650; «se juzgan» → «se evalúan».

**Revisión del autor (18/10/2026):** ficha puesta al día con el `.tex`. Ahora es 3.2 (antes 3.3). Menos cifras en el texto: porcentajes de clase, fuentes de etiqueta, conteos del archivo local de MM-Skin, fototipos de HIBA y fuentes de Derm1M se resumen o se quitan; los conteos completos quedan en las tablas y figuras. Se quitan las 66 imágenes que solo comparten lesión con validación y el detalle de SKINCON.

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa reescrita el 18/10/2026 y ficha actualizada a esa versión.** Archivo: `Chapters/03-Materiales-Metodos/02-datos.tex`. Labels: `sec:met_datasets`, `sec:met_ham`, `sec:met_particiones`, `tab:met_conjuntos` (tabla de conjuntos), `tab:met_tamanos` (tamaños por clase y partición), `fig:met_ham_dist`, `fig:met_ham_lesiones`, `fig:met_ham_ejemplos`. Las subsecciones «SkinCaRe: SkinCAP y SkinCoT» y «MM-Skin, HIBA y Derm1M» no tienen label.

Las cifras de HAM10000, de la partición, de SkinCAP, de SkinCoT, de HIBA y de MM-Skin se contaron sobre los archivos locales (solo lectura, 2026-10-11) y se cruzaron con los papers del conjunto que están en `Papers/derma/`. Cada cifra dice de dónde sale. Las que ya no están en el texto figuran en «Quitado en la revisión del 18/10/2026».

## Hilo conductor

Pregunta que responde la sección: ¿qué conjuntos de datos se usan, con qué rol, y qué propiedades de HAM10000 obligan a decidir cómo se mide un clasificador y cómo se parte el conjunto?

Viene de: 3.1 deja la tarea del trabajo (definición formal), las tres tareas T1–T3, las siete categorías de *HAM10000* con su gravedad (ahí se definen; acá solo se nombran), la restricción de una GPU de consumo y el flujo de seis etapas, cuya primera etapa son los datos y la partición por lesión (el cierre de 3.1 anuncia «qué conjuntos se usan, qué papel cumple cada uno y cómo se parte el que entrena a los clasificadores»).

Deja instalado: para 3.3, (a) el desbalance de HAM10000, con NV en dos tercios de las imágenes, que vuelve engañosa la exactitud global y justifica las métricas con el mismo peso por clase; (b) las clases malignas y premalignas (MEL, BCC, AKIEC) tienen respaldo histopatológico en todas sus imágenes, la referencia benigna es más débil (NV por seguimiento o consenso); (c) el test es la prueba original completa y las particiones nuevas no comparten lesiones, de modo que la selección no usa el test. Para 3.3 y 3.8: el subconjunto limpio (894 imágenes de prueba) y el control con DermLIP sin ajuste, que se aplican en el Cap. 4. Para 3.4–3.8: los tamaños de cada partición, el rol de cada conjunto (entrenamiento de la generación, evaluación con referencia, evaluación con otra población, preentrenamiento de DermLIP) y la modalidad de cada uno.

```
(intro, sin subsección)
P1  Cinco conjuntos de datos con roles distintos (la tabla separa SkinCAP y SkinCoT: seis filas).
    HAM10000 es el único que entrena y evalúa los clasificadores de las siete categorías, y por eso
    sus propiedades deciden la métrica y la partición. Los demás entrenan la generación, la
    evalúan contra un texto de referencia, ponen a prueba a los clasificadores con otra población o
    sirvieron para preentrenar DermLIP (`sec:met_clasif_vlm`). Tabla `tab:met_conjuntos`: modalidad,
    tamaño, papel y origen del texto de referencia                                      función: define
    ↓ necesidad — HAM10000 concentra la clasificación: hay que describir qué propiedades tiene

3.2.1 HAM10000: composición y análisis exploratorio (sec:met_ham)
P2  Composición: 10 015 imágenes dermatoscópicas de 7 470 lesiones, tomadas en Viena y Queensland
    (`tschandl2018ham10000`). No identifica pacientes: la lesión es la agrupación más fina. Anuncia tres
    propiedades que condicionan el entrenamiento y la evaluación: cómo se reparten las clases, cuántas
    imágenes tiene cada lesión y con qué respaldo se asignó cada etiqueta               función: describe
    ↓ desarrollo — la primera propiedad es el reparto de las clases
P3  Distribución de las clases (Figura `fig:met_ham_dist`): muy desigual, NV reúne dos tercios, DF y VASC
    no llegan al 1.5 % cada una. Un clasificador que respondiera siempre NV acertaría dos de cada tres
    imágenes: la exactitud global no distingue entre modelos. Por eso se usan métricas que dan a todas
    las clases el mismo peso (`sec:met_protocolo`)                                       función: justifica
    ↓ ampliación — segunda propiedad: la misma lesión aparece varias veces, y eso afecta la partición
P4  Imágenes por lesión (Figura `fig:met_ham_lesiones`): hasta seis; las 1 956 lesiones con más de una
    reúnen el 45 % del conjunto. Si las imágenes de una lesión caen en entrenamiento y prueba, el modelo
    puede reconocer la lesión en lugar de generalizar y la prueba deja de medir lo que dice medir. La
    partición tiene que agrupar por lesión                                               función: justifica
    ↓ ampliación — tercera propiedad: el respaldo de las etiquetas no es el mismo en todas las clases
P5  Respaldo de las etiquetas: la histopatología confirma algo más de la mitad de las imágenes y todas
    las de MEL, BCC y AKIEC; casi dos tercios de las NV se confirmaron por seguimiento o consenso. La
    referencia es más sólida en las clases malignas y premalignas. Figura `fig:met_ham_ejemplos`: una
    imagen por clase (la primera confirmada por histopatología de cada una; CC BY-NC 4.0)
                                                                                         función: describe · limita
    ↓ necesidad — de las propiedades salen las decisiones de partición: queda explicar cómo se partió

3.2.2 Partición disjunta por lesión (sec:met_particiones)
P6  La forma habitual de partir es estratificar por imagen, y así está hecha la partición 70/15/15 de la
    que parte el trabajo: el 36 % de las 1 503 imágenes de prueba comparte lesión con alguna de
    entrenamiento, y en melanoma el 63 %. Es una fuga de información (`sec:marco_regularizacion`): la
    prueba ya no mide el desempeño sobre lesiones nuevas y las clases minoritarias son las más
    afectadas                                                                            función: justifica
    ↓ consecuencia — para corregirla se construye una partición nueva
P7  Construcción: se conserva la prueba original completa (resultados de los VLM y del *pipeline*
    siguen comparables); se descartan 776 imágenes de entrenamiento y validación cuya lesión está en la
    prueba; el resto se reparte con `StratifiedGroupKFold` (lesión como grupo, diagnóstico como estrato,
    semilla 42). Resultado: 6 447 de entrenamiento y 1 289 de validación, sin lesiones compartidas
    (Tabla `tab:met_tamanos`). Costo: entrenamiento 8 % menor. En validación, DF y VASC quedan con menos
    de 20 imágenes: sus métricas por clase cambian mucho con pocos aciertos       función: describe · limita
    ↓ necesidad — hay que medir cuánto inflaba la fuga los resultados
P8  Cómo se dimensiona el efecto (se hace en el Cap. 4, `cp:res_clasif`): se compara la prueba completa
    con el subconjunto limpio (894 imágenes de prueba cuya lesión no aparece en entrenamiento ni
    validación); control con DermLIP sin ajuste, que no vio HAM10000 (si su desempeño también cambia,
    el cambio se debe a la composición del subconjunto y no a la fuga). Los demás conjuntos no pasan por
    esta partición: traen su propia división o se usan completos como prueba          función: describe · limita
    ↓ contraste — el resto de los conjuntos son de texto: empiezan por los que entrenan la generación

3.2.3 SkinCaRe: SkinCAP y SkinCoT
P9  SkinCaRe reúne los pares imagen–texto con que se entrena la generación (`sec:met_generacion`), en
    dos partes. SkinCAP: 4 000 imágenes clínicas de Fitzpatrick 17k y DDI
    (`groh2021neural,daneshjou2022disparities`), descripciones de cuatro dermatólogos en chino,
    traducidas al inglés y revisadas (`shen2025skincare`). Se excluyen 439 que sus anotadores
    originales marcaron como descartables por mala calidad (`daneshjou2022skincon`); las 3 561
    restantes se parten por imagen 70/15/15                                              función: describe
    ↓ contraste — SkinCoT tiene otro origen del texto, que pesa en la lectura de la generación
P10 SkinCoT: 3 041 imágenes clínicas del atlas DermNet con un razonamiento diagnóstico para cada una
    (`shen2025skincare`). Lo produce un modelo de lenguaje que recibe la etiqueta verdadera; dermatólogos
    lo revisan y descartan los de menor puntaje. Como se escribió conociendo el diagnóstico, el
    razonamiento muestra cómo se justifica una etiqueta conocida y no cómo se llega a ella desde la
    imagen: limitación al leer los resultados de generación. Formato: bloques <think> entre las
    oraciones y, al final, el diagnóstico. Fragmento en cita en bloque (caso de párpados; traducción
    propia)                                                                              función: describe · limita
    ↓ contraste — otro conjunto de texto, ahora para evaluar y no para entrenar

3.2.4 MM-Skin, HIBA y Derm1M
P11 MM-Skin: conjunto con que se evalúa la generación contra un texto de referencia; descripciones de
    quince libros de texto de dermatología, asociadas a imágenes clínicas, dermatoscópicas y
    patológicas (`zeng2025mmskin`). Las métricas con referencia se calculan sobre su partición de prueba
    (1 653 imágenes), solo con las que tienen descripción propia (`sec:met_eval_generacion`). Ninguno de
    los generadores ajustados en el trabajo vio MM-Skin; SkinVL, que sí se ajustó con él, no se evalúa
    sobre este conjunto                                                                  función: describe · justifica
    ↓ contraste — HIBA cambia de población y de modalidad, no de tarea
P12 HIBA: 1 616 imágenes de 623 pacientes de un hospital de Buenos Aires, CC BY
    (`riccilara2023dataset`). Es el único de otra población y se usa completo como prueba externa;
    ningún modelo se entrena con él (`sec:marco_generalizacion`). Cuatro de cada cinco imágenes son
    dermatoscópicas y el resto clínicas; el melanoma pesa más que en HAM10000 (16 % frente a 11 %). Sus
    diagnósticos se llevan a las siete categorías de HAM10000; el carcinoma escamoso pasa a AKIEC, una
    aproximación que agrega ruido y que se retoma en `sec:met_complementarios`      función: describe · limita
    ↓ contraste — Derm1M no se usa para entrenar ni evaluar, solo explica a DermLIP
P13 Derm1M: corpus de 1 029 761 pares imagen–texto con el que se preentrenó DermLIP
    (`yan2025derm1miccv`). Imágenes de videos, artículos, foros médicos, conjuntos públicos y material
    educativo; textos limpiados y resumidos con un LLM. Entre las fuentes declaradas no figura HAM10000,
    aunque no puede descartarse que una publicación reproduzca imágenes de ese conjunto. Se usan los
    pesos publicados sin reentrenar; Derm1M no se usa para entrenar ni evaluar        función: describe
    ↓ cierre — los datos y la partición están fijados
P14 Cierre de una oración: con los datos y la partición fijados, falta decidir con qué métricas se juzgan
    los modelos y contra qué se los compara                                              función: transición
→ Transición a 3.3: el propio P14 («Con los datos y la partición fijados, falta decidir con qué métricas
  se juzgan los modelos y contra qué se los compara.»)

Se definen acá (y no se vuelven a definir): la composición de HAM10000 (las categorías no: van en 3.1); el respaldo de las etiquetas de HAM10000; el procedimiento de la partición disjunta por lesión, con sus tamaños; el formato de razonamiento de SkinCoT (bloques `<think>`) y su limitación; el rol de cada conjunto y su modalidad.
Se retoman de antes (solo se nombran, con `\ref`): fuga de información (`sec:marco_regularizacion`); cambio de dominio (`sec:marco_generalizacion`); categorías de HAM10000 (3.1); DermLIP (`sec:met_clasif_vlm`, 3.5, remisión hacia adelante); métricas (`sec:met_protocolo`, 3.3, remisión hacia adelante); generación (`sec:met_generacion`, 3.6) y evaluación de la generación (`sec:met_eval_generacion`, 3.3); evaluación en otros escenarios (`sec:met_complementarios`, 3.8); resultados del subconjunto limpio (`cp:res_clasif`).
Extensión: 14 párrafos, 2 tablas, 3 figuras y un fragmento de texto; unas 4–4.5 páginas (el encabezado del `.tex` dice 4–4.5 p.; la ficha del capítulo preveía 5–6).
```

## Subsecciones

| Subsección | Título | Qué agrupa | Label |
|---|---|---|---|
| (intro) | sin título | P1, con la tabla `tab:met_conjuntos` | `sec:met_datasets` (sección) |
| 3.2.1 | HAM10000: composición y análisis exploratorio | P2–P5: composición, clases, repetición por lesión, respaldo de las etiquetas | `sec:met_ham` |
| 3.2.2 | Partición disjunta por lesión | P6–P8: fuga, construcción y tamaños, cómo se dimensiona el efecto | `sec:met_particiones` |
| 3.2.3 | SkinCaRe: SkinCAP y SkinCoT | P9–P10 | sin label |
| 3.2.4 | MM-Skin, HIBA y Derm1M | P11–P14 | sin label |

Los títulos de subsección dicen qué contienen. No hay títulos de párrafo (`\paragraph`).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas en `Bibliography.bib`) |
|---|---|---|---|
| P1 | Roles de los conjuntos; HAM10000 es el de la clasificación | Tabla `tab:met_conjuntos` (abajo). Roles: decisión del Cap. 3 (3.1, `01-tareas.md`) | — |
| P2 | Composición de HAM10000 | 10 015 imágenes; 7 470 lesiones; dos centros: columna `dataset` (vidir_molemax 3 954, vidir_modern 3 363, vienna_dias 439 → Viena 7 756; rosendahl 2 259 → Queensland). Conteo propio sobre `Codigo/data/raw/HAM10000/HAM10000_metadata`. Centros: paper, sección «Dataset description» | `tschandl2018ham10000` |
| P3 | Desbalance y consecuencia para la métrica | Conteos por `dx` del mismo metadata (NV 6 705; MEL 1 113; BKL 1 099; BCC 514; AKIEC 327; VASC 142; DF 115). Porcentajes sobre 10 015; en el texto: «dos tercios» (66.95 %) y «no llegan al 1.5 %» (DF 1.15 %, VASC 1.42 %). «Siempre NV» = 66.95 %: cota de referencia, no desempeño. Figura generada con `Codigo/scripts/plot_ham_dataset_figs.py` | `tschandl2018ham10000` (para el inventario); la noción de desbalance está en `sec:marco_desbalance` |
| P4 | Imágenes repetidas por lesión | Histograma sobre `lesion_id`: 5 514 lesiones con 1 imagen; 1 423 con 2; 490 con 3; 34 con 4; 5 con 5; 4 con 6 (figura). Lesiones con > 1 imagen: 1 956; imágenes en ellas: 4 501 (44.94 %, «45 %» en el texto). Conteo propio | `tschandl2018ham10000` (describe triples de una misma lesión) |
| P5 | Respaldo de las etiquetas | Cruce de `dx_type` con `dx` (conteo propio): histo 5 340 (53.32 %; mel 1 113, bcc 514, akiec 327, nv 2 498, bkl 766, df 55, vasc 67); follow_up 3 704 (todas nv); consensus 902; confocal 69. NV sin histo: 62.74 % → «casi dos tercios» | `tschandl2018ham10000` (define `follow_up` solo para nevus y `consensus` para benignas) |
| P6 | Fuga del split original | `Codigo/outputs/results/leakage_analysis.json` (`split.n_test` 1 503; `fugado_train` 543; `limpio` 894). Reproducido: 543 / 1 503 = 36.13 % → «36 %»; MEL 106/167 = 63.47 % → «63 %». Partición original: `scripts/prepare_data.py` líneas 30 (70/15/15) y 158–190 (estratificación por imagen) | — |
| P7 | Construcción de la partición nueva | `Codigo/scripts/make_lesion_disjoint_split.py` (descarta 776; `StratifiedGroupKFold` de scikit-learn, 6 folds, semilla 42). Salida: `Codigo/data/splits/ham10000_splits_lesion.json`. Tamaños 6 447 / 1 289 / 1 503 (conteo propio; tabla). Solapamiento cero: `assert` del script y `split_lesion_resul_20260926.md` §2. Costo: 6 447 / 7 010 = 0.92 → «8 %». DF 14 y VASC 18 en validación → «menos de 20» | — |
| P8 | Dimensión del efecto (sin desempeño) | Subconjunto limpio 894 (`leakage_analysis.json`). `Codigo/docs/ideas/split_lesion_semillas_plan_20260912.md`, sección «Motivación». DermLIP: pesos `redlessone/DermLIP_ViT-B-16` (`src/models/dermlip.py`). Que DermLIP no vio HAM10000 surge de las fuentes de Derm1M (P13) | — |
| P9 | SkinCAP | Paper `Papers/derma/SkinCaRe…pdf`: 4 000 imágenes; cuatro dermatólogos certificados, traducción y revisión manual. Local: `Codigo/data/raw/skincare/SkinCAP/skincap_v240715.xlsx`, columna «Do not consider this image» (439 con 1; 3 561 con 0). Splits `skincare_skincap_splits.json` (2 492 / 534 / 535, 70/15/15) | `shen2025skincare`, `groh2021neural` (Fitzpatrick 17k), `daneshjou2022disparities` (DDI), `daneshjou2022skincon` (marca de las 439; ver pregunta 13) |
| P10 | SkinCoT: origen del texto y formato | Paper: 3 041 pares; razonamiento generado con la etiqueta; revisión por dermatólogos. Local: 23 carpetas en `Codigo/data/raw/skincare/SkinCoT/EN/`, 3 041 `.txt`. Fragmento: `EN/Acne and Rosacea Photos/07PerioralDermEye.jpg.txt` (bloque `<think>`, dos primeras oraciones; el diagnóstico no se reproduce). Imágenes de DermNet según el paper (ver pregunta 4) | `shen2025skincare` |
| P11 | MM-Skin | Paper `Papers/derma/MM-Skin…pdf`: pares de 15 libros de texto de dermatología. Local: `Codigo/data/raw/MM-SkinQA/caption.csv` (11 090 filas, 11 015 imágenes únicas). Split `mmskin_splits.json`: prueba 1 653 imágenes. «9 369 con descripción» (tabla): cifra nueva del `.tex`, sin fuente en la ficha anterior (ver pregunta 6) | `zeng2025mmskin` |
| P12 | HIBA | `Codigo/data/raw/HIBA/metadata.csv` (1 616 filas; `image_type`: dermoscopic 1 270, clínicas 346; `patient_id` 623; `lesion_id` 1 246; `copyright_license` CC-BY). «Cuatro de cada cinco» = 1 270/1 616 = 78.6 %. «16 % frente a 11 %»: melanoma 253/1 616 = 15.66 % frente a 11.11 %. Mapeo: `src/data/hiba.py` líneas 13–24 (`HIBA_TO_HAM10000`; SCC → AKIEC) | `riccilara2023dataset` |
| P13 | Derm1M | Paper `Papers/derma/Derm1M…pdf`, §3.1 (fuentes) y Step 5 (LLM). 1 029 761 pares. Pesos: `src/models/dermlip.py` línea 12 (CC BY-NC-4.0). No está en `data/raw/` | `yan2025derm1miccv` (ICCV 2025; `yan2025derm1m` es la versión arXiv) |
| P14 | Cierre | — | — |

## Tablas y figuras

**Tabla `tab:met_conjuntos`.** Conjuntos de datos, su modalidad, su tamaño, su papel y el origen de su texto de referencia (seis filas, como en el `.tex`).

| Conjunto | Modalidad | Tamaño | Papel | Origen del texto de referencia |
|---|---|---|---|---|
| *HAM10000* | Dermatoscópica | 10 015 imágenes; 7 470 lesiones | Clasificación (entrenamiento, validación y prueba) | Sin texto; etiqueta confirmada por histopatología, seguimiento, consenso o microscopía confocal |
| *SkinCAP* (*SkinCaRe*) | Clínica (fotografía) | 3 561 imágenes | Entrenamiento de la generación | Descripciones de cuatro dermatólogos, escritas en chino y traducidas al inglés |
| *SkinCoT* (*SkinCaRe*) | Clínica (fotografía) | 3 041 imágenes | Entrenamiento de la generación (razonamiento) | Razonamiento escrito por un modelo de lenguaje con la etiqueta a la vista y revisado por dermatólogos |
| *MM-Skin* | Clínica, dermatoscópica y patológica | 11 015 imágenes; 9 369 con descripción | Evaluación de la generación con referencia | Descripciones de libros de texto de dermatología |
| *HIBA* | Dermatoscópica y clínica | 1 616 imágenes; 1 246 lesiones | Evaluación con otra población (solo prueba) | Diagnóstico de dermatólogos del hospital |
| *Derm1M* | Dermatoscópica y clínica | 1 029 761 pares imagen–texto | Preentrenamiento de DermLIP (no se usa en este trabajo) | Fuentes web, educativas y bases públicas; texto procesado con un LLM |

**Tabla `tab:met_tamanos`.** Imágenes por clase y partición de HAM10000; la última columna cuenta las imágenes de entrenamiento y validación originales que se descartaron porque su lesión aparece en prueba.

| Clase | Entrenamiento | Validación | Prueba | Descartadas |
|---|---|---|---|---|
| AKIEC | 207 | 41 | 49 | 30 |
| BCC | 307 | 62 | 77 | 68 |
| BKL | 682 | 137 | 165 | 115 |
| DF | 73 | 14 | 17 | 11 |
| MEL | 661 | 132 | 167 | 153 |
| NV | 4 427 | 885 | 1 006 | 387 |
| VASC | 90 | 18 | 22 | 12 |
| **Total** | **6 447** | **1 289** | **1 503** | **776** |

Cifras: entrenamiento y validación, de `ham10000_splits_lesion.json`; prueba, idéntica al original; descartadas = imágenes de entrenamiento y validación originales cuya lesión aparece en prueba (verificado: 776 sobre `ham10000_splits.json`). Los totales cuadran con 10 015. El original tenía 7 010 / 1 502 / 1 503.

**Figuras y listado**

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| `fig:met_ham_dist` | Imágenes por clase y su porcentaje sobre el total; MEL y BCC en bermellón con trama, las demás en azul | `Figures/Capitulos/03-Materiales-Metodos/ham-distribucion.pdf`, generada con `Codigo/scripts/plot_ham_dataset_figs.py` | existe |
| `fig:met_ham_lesiones` | Lesiones según el número de imágenes (una a seis) | `ham-imagenes-por-lesion.pdf`, mismo script | existe |
| `fig:met_ham_ejemplos` | Una imagen dermatoscópica por clase (MEL, NV, BCC, AKIEC, BKL, DF, VASC): la primera confirmada por histopatología de cada una; CC BY-NC 4.0 | `ham-ejemplos.pdf`, mismo script | existe |
| Fragmento de SkinCoT | Cita en bloque: bloque `<think>` de dos oraciones, de un caso de párpados, con traducción propia | `EN/Acne and Rosacea Photos/07PerioralDermEye.jpg.txt` | existe |
| `ej_skincot_human.jpg` | — | Tiene la marca «©DermNet.com» y es una foto, no texto de SkinCoT | no se usa (resuelta) |

## Prosa ya escrita que se conserva

- El párrafo de las siete categorías y su gravedad está en 3.1 (P2); en 3.2 no se repite. La remisión a `sec:met_tareas` ya no está en 3.2: las categorías se nombran en la tabla y en los párrafos (MEL, BCC, AKIEC, NV, DF, VASC con `\gls{}` donde corresponde).
- La remisión a `sec:marco_generalizacion` del antiguo `\pendiente` de SkinCaRe, MM-Skin y HIBA se conserva en P12.
- El `\subsection{Preprocesamiento y aumento de datos}` no está en 3.2: va a 3.4 (D7 de la ficha del capítulo).
- El label `sec:met_ham` se queda en 3.2 sobre el análisis de HAM10000.

## Lo que va al apéndice

Apéndice F (`Chapters/Apendices/F-Fichas-Datasets-Modelos.tex`), una ficha por conjunto: fuente y versión de cada archivo; estructura de carpetas; licencia (HAM10000, SkinCaRe, MM-Skin, HIBA CC BY, DermLIP CC BY-NC-4.0); tabla completa del mapeo HIBA → HAM10000 (`src/data/hiba.py`); fuentes de Derm1M con sus porcentajes; la fuga por clase completa; el detalle de los splits (`ham10000_splits*.json`, `skincare_*`, `mmskin_splits.json`, `hiba_splits.json`); el listado de excepciones de SkinCAP.

## Lo que NO va en esta sección (y dónde está)

- Las siete categorías, su gravedad y las tres tareas: 3.1 (`sec:met_tareas`).
- Preprocesamiento (resolución, normalización), aumento de datos y TTA: 3.4 (`sec:met_supervisados`).
- Efecto de la fuga sobre las métricas (sensibilidad macro con la partición anterior y la nueva, subconjunto limpio, DermLIP sobre cada subconjunto): Cap. 4 (el Cap. 3 no presenta desempeños).
- Métricas, líneas base, umbral de melanoma, criterio de selección: 3.3 (`sec:met_protocolo`, `sec:met_seleccion`).
- Resultados de HIBA por modalidad: Caps. 4–5 (3.8 define el protocolo).
- Definiciones de fuga de información, partición, desbalance, dominio y generalización: Cap. 2 (solo se nombran con `\ref`).
- Grillas de hiperparámetros, LoRA y el ajuste en dos etapas: 3.4 y 3.6.
- Los resultados de RAG y de la cascada y las cifras de la revisión del 03/10 sobre la métrica oficial: Caps. 4–5.
- Histopatología fuera de alcance: 3.1 (P5).

## Preguntas abiertas para el autor

Se marca el estado respecto de la revisión del 18/10/2026.

1. **Licencia de HAM10000 y ejemplos por clase (resuelta).** El `.tex` incluye la figura `fig:met_ham_ejemplos` con la licencia CC BY-NC 4.0 en el epígrafe. Falta verificar la licencia de la versión descargada en Harvard Dataverse (la tabla 1 del paper indica CC BY-NC 4.0 para la mayoría de sus fuentes y CC-0 para una).
2. **`ej_skincot_human.jpg` (resuelta).** No se usa; el ejemplo de SkinCoT es un fragmento de texto.
3. **Traducción del ejemplo de SkinCoT (resuelta).** Se cita en inglés con traducción propia marcada como tal.
4. **Origen de las imágenes de SkinCoT (resuelta, 18/10).** El paper dice «images sourced from the public DermNet atlas» (§2.3) y aclara que SkinCAP y SkinCoT no comparten imágenes; Fitzpatrick 17k, DDI y SKINCON son el origen de SkinCAP. La Tabla 4 del paper agrupa SkinCoT en 23 grupos de enfermedades (3.6 dice «23 grupos»).
5. **Licencia y uso de SkinCaRe (abierta).** El README tiene dos licencias (CC-BY-4.0 en el cuerpo, cc-by-nc-sa-4.0 en el YAML); el acuerdo exige investigación no comercial y prohíbe redistribuir copias. El fragmento de SkinCoT es una cita corta.
6. **MM-Skin (resuelta, 18/10).** La Tabla 2 del paper da 11 039 imágenes y 9 369 pares imagen–texto (1 039 dermatoscópicas, 3 016 patológicas, 6 984 clínicas); la tabla del `.tex` usa ahora esas cifras del paper. El archivo local tiene 11 015 imágenes únicas; la prueba de 1 653 es del split local.
7. **MM-Skin, partición (resuelta).** La evaluación con referencia usa el test de `mmskin_splits.json` (1 653 imágenes), solo con las imágenes que tienen descripción propia.
8. **HIBA, cuántas imágenes (resuelta).** El `.tex` usa las 1 616 completas como prueba externa. `hiba_splits.json` (243 de prueba) y `phase0_data.yaml` no se mencionan.
9. **HIBA, fototipos (obsoleta tras la revisión del 18/10).** El `.tex` ya no reporta fototipos.
10. **HIBA, mapeo (resuelta).** El `.tex` declara que SCC pasa a AKIEC como aproximación que agrega ruido, y remite a 3.8 (`sec:met_complementarios`). Falta confirmar si también se declara en la tabla SOTA.
11. **Derm1M no está en el repo (abierta).** Las cifras son del paper (1 029 761 pares). Verificar la variante de DermLIP que usa 3.5 (`vit-b-16` según `dermlip.py`).
12. **«DermLIP nunca vio HAM10000» (resuelta).** El `.tex` redacta «entre las fuentes declaradas no figura HAM10000, aunque no puede descartarse…».
13. **SkinCAP, las 439 marcas (resuelta, 18/10).** SkinCon §2.2: «A label of "Do not use" was allowed to remove any images that were poor quality». La columna local «Do not consider this image» la hereda; el `.tex` lo dice así.
14. **Referencias que faltan (obsoleta tras la revisión del 18/10).** Gemini 2.5 Pro, GPT-o4-mini y Llama-3.1 ya no se nombran en el texto; DermNet se nombra sin cita.
15. **Clave de HIBA (resuelta).** `riccilara2023dataset`.
16. **Clave de Derm1M (resuelta).** `yan2025derm1miccv`.
17. **Figura de distribución (resuelta).** Regenerada con `plot_ham_dataset_figs.py`.
18. **Formato numérico (resuelta).** Espacio fino (`10\,015`), porcentajes con `\,\%`; en el texto se redondea a enteros.
19. **Siglas de las categorías (resuelta).** `\gls{}` en la primera aparición, que es 3.1.
20. **Dependencia de 3.1 (resuelta).** El «Viene de» y P1 se alinean con la 3.1 reescrita.
21. **Derm1M, fuentes en la tabla (obsoleta tras la revisión del 18/10).** Los porcentajes de fuentes se quitaron; queda una lista cualitativa.

## Decisiones tomadas por cuenta propia

- **D1. Test fijo y partición sin lesiones compartidas.** El test es el original completo (1 503). El texto ya no explica cómo se eligió el fold de validación (ver «Quitado»); el criterio sigue siendo el de `make_lesion_disjoint_split.py` (fold cuya distribución de clases se parece más a la global, sin mirar desempeño, `split_lesion_resul_20260926.md` §2).
- **D2. Fuga contada por subconjunto de entrenamiento.** El número principal es 543/1 503 (36 %), que corresponde a lesiones de entrenamiento, como en `leakage_analysis.json`. El subconjunto limpio (894) coincide con el del script. Los 66 de validación ya no se mencionan.
- **D3. Sin desempeño en 3.2.** Ninguna cifra de sensibilidad, exactitud o AUC aparece en la sección. El efecto de la fuga se describe como método (P8), no como resultado.
- **D4. DermLIP como control,** con la formulación «entre las fuentes declaradas no figura HAM10000».
- **D5. Limitación de la referencia benigna.** Se declara en P5 como limitación (no como decisión de diseño), sin cifras: su tratamiento corresponde a 3.3.
- **D6. Títulos de subsección.** Cuatro subsecciones con títulos descriptivos y ningún título de párrafo, según la guía §3.
- **D7. Atribución de la afirmación de HIBA.** La frase «primera base de imágenes clínicas y dermatoscópicas en Hispanoamérica» ya no aparece; la sección dice «un hospital de Buenos Aires».
- **D8. Generadores de SkinCoT sin nombre.** El `.tex` dice «un modelo de lenguaje», sin nombrar Gemini 2.5 Pro ni GPT-o4-mini (por eso no hacen falta referencias nuevas).
- **D9. «Reporte» no aparece en 3.2** como texto de referencia: se usa «texto de referencia» o «descripción» (guía §4).
- **D10. Preprocesamiento fuera de 3.2.** Va a 3.4 (D7 del capítulo).
- **D11. Tablas numeradas con `\label`.** El `.tex` toma el número de la etiqueta.
- **D12. Cifras redondeadas en el texto.** Las cifras de P3–P5 y P12 se redondean (dos tercios, 1.5 %, 45 %, 36 %, 63 %, 16 % frente a 11 %); los valores exactos con dos decimales quedan en la columna de fuentes. Seguimiento en HAM10000: 3 704 / 10 015 = 36.98 % (la ficha anterior decía 36.99 %).
- **D13. Columna «Descartadas».** Cuenta, por clase, las imágenes de entrenamiento y validación originales cuya lesión aparece en prueba (el epígrafe del `.tex` dice lo mismo).
- **D14. Ejemplo de SkinCoT.** Se cita el bloque `<think>` de las dos primeras oraciones del archivo; el diagnóstico no se reproduce.
- **D15. Figura de HAM10000.** En `ham-distribucion.pdf` solo MEL y BCC están en bermellón con trama; AKIEC, que P5 trata como premaligna con histopatología completa, sale en azul. El epígrafe lo describe tal cual; el autor decide si AKIEC debe destacarse.

## Quitado en la revisión del 18/10/2026

Una línea por ítem; las fuentes de cada cifra se conservan para el apéndice o el Cap. 4.

- Porcentajes por clase de HAM10000 (NV 66.95 %, MEL 11.11 %, BKL 10.97 %, BCC 5.13 %, AKIEC 3.27 %, VASC 1.42 %, DF 1.15 %): se resumen como «dos tercios» y «no llegan al 1.5 %»; los conteos quedan en la figura (R1, R3: menos cifras en el texto).
- Cantidad de lesiones con 1 a 6 imágenes (5 514 / 1 423 / 490 / 34 / 5 / 4) y las 4 501 imágenes (44.94 %): quedan en la figura y se dice «45 %».
- Fuentes de etiqueta con porcentajes (histopatología 5 340, 53.32 %; seguimiento 3 704, 36.98 %, solo NV; consenso 902, 9.01 %; confocal 69, 0.69 %) y los detalles NV 62.74 % sin histopatología (seguimiento 55.24 %, consenso 7.50 %): se resumen en «algo más de la mitad» y «casi dos tercios» (menos cifras).
- Fuga con decimales y por clase (36.13 %, MEL 63.47 %, BCC 70.13 %, NV 26.64 %): quedan 36 % y 63 %; la fuga por clase va al Apéndice F.
- Las 66 imágenes que solo comparten lesión con validación (609 en total contra 543 de entrenamiento): se quitó el detalle (pedido del autor).
- Criterio de elección del fold de validación (el que más se parece a la distribución global; no mira desempeño) y `StratifiedGroupKFold` con 6 folds: el texto conserva el método, sin el número de folds ni el criterio (R4 vale para métricas y umbrales; se conserva en `make_lesion_disjoint_split.py`).
- Tamaño de DF (14) y VASC (18) en validación: queda «menos de 20 imágenes»; las cifras exactas están en la tabla.
- Nombres de los generadores de SkinCoT (Gemini 2.5 Pro para la observación, GPT-o4-mini para el razonamiento), los seis criterios de evaluación con puntaje 0–5, el umbral de media < 4.5 y los 772 descartados de 3 813: se resumen como «dermatólogos lo revisan y descartan los de menor puntaje» (menos cifras; también evita referencias nuevas).
- 23 categorías de DermNet y los splits de SkinCoT (2 128 / 456 / 457) y de SkinCAP (2 492 / 534 / 535): quedan «70/15/15» y los tamaños totales en la tabla.
- Fototipos de Fitzpatrick de SkinCAP (I–VI) y de HIBA (I 114, II 1 085, III 275, IV 25, sin dato 117): fuera del texto.
- Detalle de SKINCON y de por qué se excluyen las 439 imágenes: se resume en una oración (pedido del autor).
- Conteo del archivo local de MM-Skin: 11 090 filas, 7 020 clínicas, 3 028 patológicas, 1 042 «derm»; 27 259 pares de preguntas y respuestas (VQA) generados con Llama-3.1; split 7 710 / 1 652 / 1 653: se quedan 11 015 imágenes y 9 369 con descripción (tabla) y la prueba de 1 653 (texto).
- HIBA: 1 270 dermatoscopias de contacto polarizado y 346 clínicas, 1 246 lesiones y 623 pacientes, diez diagnósticos con SCC → AKIEC, melanoma 15.66 %, histopatología en 1 036 imágenes, «modalidad mixta permite separar la caída por modalidad»: se resumen como «cuatro de cada cinco imágenes» y «16 % frente a 11 %».
- Afirmación de los autores de HIBA como «primera base de imágenes clínicas y dermatoscópicas en Hispanoamérica» (D7 anterior): ya no se usa.
- Derm1M: porcentajes de fuentes (YouTube 45.6 %, PubMed 19.4 %, foros 15.1 %, SCIN y MSKCC 10.1 %, educativo 9.8 %) y la ontología de 390 afecciones: se resumen como lista cualitativa de fuentes.
- Remisión desde HIBA a «3.9» y desde Derm1M a «3.6»: ahora apuntan a 3.8 (`sec:met_complementarios`) y 3.5 (`sec:met_clasif_vlm`).
- Transición original a 3.4 («Con el desbalance, las etiquetas malignas verificadas y las particiones fijadas, falta decidir…»): reemplazada por la oración final del `.tex` (P14).
- Subsección «Preprocesamiento y aumento de datos» (ya fuera desde la ficha del capítulo, D7): va a 3.4.
- Mención del ciclo de iteración y de la auditoría que originó la partición disjunta (3.2 antigua, «Viene de»): R1, historia del proceso.
