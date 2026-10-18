# Ficha 3.3 — Conjuntos de datos

**Estado: aprobada por el autor como punto de partida (11/10/2026); prosa redactada en primera versión.** Archivo: `Chapters/03-Materiales-Metodos/03-datos.tex` (sale de `02-datos-particiones.tex`). Labels: `sec:met_datasets`, `sec:met_ham`, `sec:met_particiones`. Labels nuevos propuestos: `tab:met_conjuntos` (tabla de conjuntos), `tab:met_tamanos` (tamaños por clase y partición), `fig:met_ham_dist`, `fig:met_ham_lesiones`.

Las cifras de HAM10000, de la partición, de SkinCAP, de SkinCoT, de HIBA y de MM-Skin se contaron sobre los archivos locales (solo lectura, 2026-10-11) y se cruzaron con los papers del conjunto que están en `Papers/derma/`. Cada cifra dice de dónde sale.

## Hilo conductor

Pregunta que responde la sección: ¿qué conjuntos de datos se usan, con qué rol, y qué propiedades de HAM10000 obligan a decidir cómo se mide un clasificador y cómo se parte el conjunto?

Viene de: 3.1 deja las tres tareas, las siete categorías de HAM10000 con su gravedad (ahí se definen; acá solo se nombran) y la restricción de una GPU de consumo. 3.2 deja que la primera etapa del flujo son los datos, que los conjuntos no están versionados y que la partición disjunta por lesión entró al ciclo como corrección de una auditoría. (3.1 y 3.2 todavía no están aprobadas: verificar este «Viene de» al cerrarlas.)

Deja instalado: para 3.4, (a) el desbalance de HAM10000, con NV en 66.95 % de las imágenes, que vuelve engañosa la exactitud global; (b) las tres clases malignas o premalignas (MEL, BCC, AKIEC) tienen etiqueta histológica en el 100 % de sus imágenes, lo que da base para medir las confusiones de costo desigual; (c) el test es idéntico al original y la validación es agrupada por lesión, de modo que la selección no usa el test. Para 3.5–3.9: los tamaños de cada partición, el rol de cada conjunto (entrenamiento de la generación, evaluación con referencia, evaluación fuera de distribución, preentrenamiento de DermLIP) y la modalidad de cada uno (dermatoscópica o clínica).

```
(intro, sin subsección)
P1  Cinco conjuntos de datos con roles distintos; no todos sirven para lo mismo. HAM10000 es el único
    que entrena y evalúa los clasificadores de las siete categorías. Tabla 3.1 resume modalidad,
    tamaño, rol y origen del texto de referencia de cada uno                       define
    ↓ necesidad — HAM10000 concentra la clasificación, así que de él salen las decisiones que
      obligan a justificar la métrica y la partición

3.3.1 HAM10000: composición y análisis exploratorio (sec:met_ham)
P2  Composición: 10 015 imágenes dermatoscópicas de 7 470 lesiones, de dos centros (Viena y
    Queensland). HAM no publica id de paciente; la lesión es la agrupación más fina disponible    describe
    ↓ consecuencia — la distribución de clases es el primer hallazgo del análisis
P3  Distribución: NV 66.95 %, MEL 11.11 %, BKL 10.97 %, BCC 5.13 %, AKIEC 3.27 %, VASC 1.42 %,
    DF 1.15 %. Un clasificador que predice siempre NV acierta 66.95 %: la exactitud global no
    distingue entre modelos. Por eso se usa la sensibilidad macro y el F1 macro (decide 3.4)   justifica
    ↓ problema — la misma lesión aparece varias veces, y eso afecta cómo se parte el conjunto
P4  Imágenes repetidas: 1 956 de las 7 470 lesiones tienen más de una imagen (máximo 6); reúnen
    4 501 imágenes (44.94 %). Si las imágenes de una lesión caen en entrenamiento y en prueba, el
    modelo puede reconocer la lesión y no generalizar. La partición debe agrupar por lesión   justifica
    ↓ limitación — la referencia de algunas clases no es histológica
P5  Origen de las etiquetas: histopatología en 5 340 imágenes (53.32 %), seguimiento en 3 704
    (36.99 %, solo NV), consenso de los autores en 902 (9.01 %) y confocal en 69 (0.69 %). MEL, BCC
    y AKIEC tienen histopatología en el 100 % de sus imágenes; en NV, el 62.74 % no la tiene
    (seguimiento 55.24 %, consenso 7.50 %). La referencia es más sólida en las malignas; 3.4
    declara esa limitación para las clases benignas                                  limita

3.3.2 Partición disjunta por lesión (sec:met_particiones)
P6  El split original (70/15/15) se estratificó por imagen, no por lesión: el 36.13 % de las 1 503
    imágenes de prueba comparte lesión con entrenamiento, y en melanoma el 63.47 %. Eso es fuga de
    información entre particiones (Sección~\ref{sec:marco_generalizacion}): el test ya no mide
    imágenes nuevas                                                                 define · justifica
    ↓ necesidad — hace falta medir cuánto cambia la evaluación al corregir la partición
P7  Cómo se mide el efecto, sin cifras de desempeño: se evalúa sobre el subconjunto limpio (894
    imágenes cuya lesión no aparece en entrenamiento ni en validación) y se compara con un modelo
    que no vio HAM10000 (DermLIP en zero-shot). Los resultados van al Cap. 4              describe
    ↓ consecuencia — con la fuga medida, la partición se reconstruye sin tocar el test
P8  Construcción: el test es idéntico al original (1 503 imágenes) para mantener la comparabilidad
    con los VLM y el ruteo ya evaluados sobre él. Se descartan 776 imágenes de entrenamiento y
    validación cuya lesión está en el test; el resto (7 736 imágenes) se reparte con
    StratifiedGroupKFold (6 folds, grupos = lesión, estratos = diagnóstico, semilla 42). La validación
    es el fold cuya distribución de clases se parece más a la global: el criterio no mira desempeño.
    Resultado: 6 447 de entrenamiento y 1 289 de validación, sin lesiones compartidas   describe
    ↓ limitación — el entrenamiento queda 8 % más chico que el original (7 010)
P9  Tabla 3.2 con tamaños por clase y partición. En validación, DF (14) y VASC (18) quedan con
    menos de 20 imágenes; la métrica por clase de esas clases se lee con esa cota     explica · limita
    → Transición a 3.3.3 / 3.3.4: los conjuntos de generación y de evaluación externa no pasan por
      esta partición; cada uno tiene su propia (SkinCAP, SkinCoT) o es test completo (HIBA, MM-Skin
      con su split).

3.3.3 SkinCaRe: SkinCAP y SkinCoT
P10 SkinCaRe entrena la generación del VLM (3.7). SkinCAP: 4 000 imágenes de fotografía clínica
    (Fitzpatrick 17k y DDI) con descripciones escritas por cuatro dermatólogos en chino, traducidas
    al inglés y revisadas a mano. En el archivo local, 439 imágenes están marcadas «Do not consider
    this image» y se excluyen: quedan 3 561, partidas 70/15/15 por imagen (2 492 / 534 / 535)  describe
    ↓ contraste — SkinCoT tiene otro origen del texto, que pesa en la lectura de la generación
P11 SkinCoT: 3 041 imágenes de fotografía clínica (DermNet, 23 categorías). La observación la
    escribe un modelo de visión (Gemini 2.5 Pro) sin diagnóstico; el razonamiento lo escribe otro
    modelo (GPT-o4-mini) con la etiqueta verdadera; dermatólogos lo evalúan en seis criterios con
    puntaje 0–5 y descartan 772 de 3 813 con media < 4.5. El razonamiento se escribió conociendo el
    diagnóstico. Formato: bloques <think> entre oraciones, y el diagnóstico en la última
    (ejemplo textual en el listado de la sección)                        describe · limita

3.3.4 MM-Skin, HIBA y Derm1M
P12 MM-Skin es el conjunto de evaluación de la generación con referencia (3.7). Sus textos de
    referencia son descripciones de 15 libros de texto de dermatología; las preguntas y respuestas
    (27 259 en el archivo) las genera Llama-3.1 a partir de imagen y descripción, con validación
    automática y manual. El archivo tiene 11 090 filas y 11 015 imágenes: 7 020 clínicas, 3 028
    patológicas y 1 042 «derm» (a verificar). Se parte 70/15/15 por imagen   describe · justifica
    ↓ contraste — HIBA cambia de población y de modalidad, no de tarea
P13 HIBA es el único conjunto de población distinta (hospital de Buenos Aires): 1 616 imágenes, de
    ellas 1 270 dermatoscopias de contacto polarizado y 346 clínicas, de 1 246 lesiones y 623
    pacientes; licencia CC BY. Fototipos por imagen: I 114, II 1 085, III 275, IV 25 y sin dato 117.
    Sus diagnósticos se mapean a las siete categorías de HAM10000 (diez diagnósticos; SCC se mapea a
    AKIEC, asunto que el código documenta como limitación). Solo se usa como evaluación fuera de
    distribución: ningún modelo se entrena con HIBA. La modalidad mixta permite separar la caída por
    modalidad (3.9). La distribución difiere de HAM (MEL 15.66 %)                describe · limita
    ↓ contraste — Derm1M no se usa para entrenar ni evaluar, solo para DermLIP
P14 Derm1M (1 029 761 pares imagen–texto) es el corpus con el que se preentrenó DermLIP. Según el
    paper, sus fuentes son YouTube (45.6 %), PubMed (19.4 %), foros (15.1 %), los datasets SCIN y
    MSKCC (10.1 %) y material educativo (9.8 %); el texto se limpió y resumió con LLM y se enriqueció
    con una ontología de 390 afecciones. El trabajo usa los pesos publicados, sin reentrenar el backbone (solo cabezas o kNN sobre embeddings): el
    párrafo lo dice y 3.6 lo describe                                                  describe
→ Transición a 3.4: «Con el desbalance, las etiquetas malignas verificadas y las particiones fijadas,
  falta decidir con qué métrica se juzgan los clasificadores y contra qué se comparan (Sección~
  \ref{sec:met_protocolo}).»
```

Se definen acá (y no se vuelven a definir): la composición de HAM10000 (las categorías no: van en 3.1); el origen de las etiquetas de HAM10000; el procedimiento de la partición disjunta por lesión, con sus tamaños; el formato de razonamiento de SkinCoT (bloques `<think>`); el rol de cada conjunto y su modalidad.

Se retoman de antes (solo se nombran, con `\ref`): fuga de información (`sec:marco_regularizacion`); particiones y conjunto de validación (`sec:marco_fundamentos`); desbalance de clases (`sec:marco_desbalance`); cambio de dominio (`sec:marco_generalizacion`); categorías de HAM10000 (`sec:met_tareas`, 3.1); DermLIP y clasificación por verosimilitud (`sec:met_clasif_vlm`, 3.6, remisión hacia adelante); métricas (`sec:met_seleccion`, 3.4, remisión hacia adelante).

Extensión: 14 párrafos, 3 tablas o listados y 2 figuras nuevas; unas 5–6 páginas, dentro de lo que fija la ficha del capítulo.

## Subsecciones

| Subsección | Título propuesto | Qué agrupa | Label |
|---|---|---|---|
| (intro) | sin título | P1, con la tabla 3.1 | `sec:met_datasets` (sección) |
| 3.3.1 | HAM10000: composición y análisis exploratorio | P2–P5: composición, clases, repetición por lesión, origen de las etiquetas | `sec:met_ham` |
| 3.3.2 | Partición disjunta por lesión | P6–P9: fuga, cómo se mide, construcción, tamaños | `sec:met_particiones` |
| 3.3.3 | SkinCaRe: SkinCAP y SkinCoT | P10–P11 | sin label nuevo |
| 3.3.4 | MM-Skin, HIBA y Derm1M | P12–P14 | sin label nuevo |

Los títulos de subsección dicen qué contienen. No hay títulos de párrafo (`\paragraph`).

## Contenido por párrafo

| P | Qué dice | Datos y su fuente exacta | Citas (claves verificadas en `Bibliography.bib`) |
|---|---|---|---|
| P1 | Roles de los cinco conjuntos; HAM10000 es el de la clasificación | Tabla 3.1 (abajo). Roles: decisión del Cap. 3 (3.1 P1, `01-tareas.md`) | — |
| P2 | Composición de HAM10000 | 10 015 imágenes; 7 470 lesiones; dos centros: columna `dataset` (vidir_molemax 3 954, vidir_modern 3 363, vienna_dias 439 → Viena 7 756; rosendahl 2 259 → Queensland). Conteo propio sobre `Codigo/data/raw/HAM10000/HAM10000_metadata`. Centros: paper, sección «Dataset description» | `tschandl2018ham10000` |
| P3 | Desbalance y consecuencia para la métrica | Conteos por `dx` del mismo metadata (NV 6 705; MEL 1 113; BKL 1 099; BCC 514; AKIEC 327; VASC 142; DF 115). Porcentajes sobre 10 015. «Siempre NV» = 66.95 %: cota de referencia, no desempeño. Coincide con `Docs/experimentacion/imagenes/F0_ham_dist.png` (mismos conteos) | `tschandl2018ham10000` (para el inventario); la noción de desbalance ya está en `sec:marco_desbalance` |
| P4 | Imágenes repetidas por lesión | Histograma sobre `lesion_id`: 5 514 lesiones con 1 imagen; 1 423 con 2; 490 con 3; 34 con 4; 5 con 5; 4 con 6. Lesiones con > 1 imagen: 1 956; imágenes en ellas: 4 501 (44.94 %). Conteo propio. El paper describe triples de una misma lesión (series ViDIR) | `tschandl2018ham10000` |
| P5 | Origen de las etiquetas y su consecuencia | Cruce de `dx_type` con `dx` (conteo propio): histo 5 340 (mel 1 113, bcc 514, akiec 327, nv 2 498, bkl 766, df 55, vasc 67); follow_up 3 704 (todas nv); consensus 902 (nv 503, bkl 264, df 60, vasc 75); confocal 69 (bkl). NV con histo = 2 498 de 6 705 (37.26 %) | `tschandl2018ham10000` (define `follow_up` solo para nevus y `consensus` para benignas) |
| P6 | Fuga del split original | `Codigo/outputs/results/leakage_analysis.json` (`split.n_test` 1 503; `fugado_train` 543; `limpio` 894; `fugado_por_clase`). Reproducido con conteo propio sobre `ham10000_splits.json`: 543 / 1 503 = 36.13 %; MEL 106/167 = 63.47 %; BCC 54/77 = 70.13 %; NV 268/1 006 = 26.64 %. Partición original: `scripts/prepare_data.py` líneas 30 (70/15/15) y 158–190 (estratificación por imagen). Conteo de solo entrenamiento: 543 (no 609; los 66 restantes están solo en validación) | `tschandl2018ham10000` |
| P7 | Medición del efecto (sin desempeño) | `Codigo/docs/ideas/split_lesion_semillas_plan_20260912.md`, sección «Motivación» (subconjunto limpio y control con DermLIP zero-shot). DermLIP: pesos `redlessone/DermLIP_ViT-B-16` (`src/models/dermlip.py`). Que DermLIP no vio HAM10000 surge de la lista de fuentes de Derm1M (ver P14; ver pregunta 12) | `yan2025derm1miccv` |
| P8 | Construcción de la partición nueva | `Codigo/scripts/make_lesion_disjoint_split.py` (descarta 776; StratifiedGroupKFold, 6 folds, semilla 42, val = fold más parecido a la distribución global). Salida: `Codigo/data/splits/ham10000_splits_lesion.json`. Tamaños 6 447 / 1 289 / 1 503 (conteo propio). Solapamiento cero: `assert` del script y `split_lesion_resul_20260926.md` §2. Costo: 6 447 / 7 010 = 0.92 | — (la validación cruzada agrupada, `StratifiedGroupKFold`, es de scikit-learn; sin cita propia) |
| P9 | Tamaños por clase y partición | Tabla 3.2 (abajo): conteo propio sobre los dos archivos `ham10000_splits*.json` y el metadata | — |
| P10 | SkinCAP | Paper `Papers/derma/SkinCaRe…pdf`: 4 000 imágenes; «four board-certified dermatologists», traducción con Google Translate y revisión manual; Fitzpatrick I–VI. Local: `Codigo/data/raw/skincare/SkinCAP/skincap_v240715.xlsx`, columna «Do not consider this image» (4 000 filas; 439 con 1; 3 561 con 0). Función de generación de splits de SkinCaRe en `scripts/prepare_data.py` (bloque de SkinCAP). Splits `skincare_skincap_splits.json` 2 492 / 534 / 535 | `shen2025skincare`, `groh2021neural` (Fitzpatrick 17k), `daneshjou2022disparities` (DDI) |
| P11 | SkinCoT: origen del texto y formato | Paper: 3 041 pares; observación con Gemini 2.5 Pro; razonamiento con GPT-o4-mini a partir de la etiqueta; seis criterios 0–5; umbral de media < 4.5; 4 002 enviados, 3 813 pasan el control inicial, 772 descartados. Local: 23 carpetas en `Codigo/data/raw/skincare/SkinCoT/EN/`, 3 041 `.txt`; splits 2 128 / 456 / 457. Formato: `EN/Acne and Rosacea Photos/07PerioralDermEye.jpg.txt` (bloques `<think>`; el diagnóstico en la última oración, en negrita). Imágenes: fotografía de DermNet según el paper (ver pregunta 4) | `shen2025skincare` |
| P12 | MM-Skin | Paper `Papers/derma/MM-Skin…pdf`: «nearly 10,000 image-text pairs» de 15 libros de texto de dermatología; «over 27k» VQA; Llama-3.1 como generador de VQA. Local: `Codigo/data/raw/MM-SkinQA/caption.csv` (11 090 filas, 11 015 imágenes únicas; modalidad: skin 7 020, pathology 3 028, derm 1 042), `VQA.csv` (27 259 filas, 9 236 imágenes). Split `mmskin_splits.json`: 7 710 / 1 652 / 1 653 imágenes | `zeng2025mmskin` |
| P13 | HIBA | `Codigo/data/raw/HIBA/metadata.csv` (1 616 filas; `image_type`: dermoscopic 1 270, clinical overview 340, clinical close-up 6; `fitzpatrick_skin_type`: I 114, II 1 085, III 275, IV 25, vacío 117; `lesion_id` 1 246; `patient_id` 623; `copyright_license` CC-BY). Mapeo: `src/data/hiba.py` líneas 13–24 (`HIBA_TO_HAM10000`). Diagnósticos: nevus 602, BCC 340, melanoma 253, SCC 158, SK 68, AK 63, DF 61, vascular 51, solar lentigo 18, lichenoid 2. Paper `Papers/derma/A dataset of skin lesion images…pdf`: 1 616 imágenes, 1 246 lesiones, 623 pacientes; «first database … Hispanic America» (atribuir a los autores) | `riccilara2023dataset` |
| P14 | Derm1M | Paper `Papers/derma/Derm1M…pdf`, §3.1 (fuentes con porcentajes, Fig. 1a) y §3.1 Step 5 (LLM y ontología); 1 029 761 pares. Pesos: `src/models/dermlip.py` línea 12 (CC BY-NC-4.0). No está en `data/raw/` | `yan2025derm1miccv` (publicado en ICCV 2025); `yan2025derm1m` es la versión arXiv |

## Tablas y figuras

**Tabla 3.1 (`tab:met_conjuntos`)**. Conjuntos de datos y su rol. Columnas: conjunto, modalidad, tamaño, rol, origen del texto de referencia.

| Conjunto | Modalidad | Tamaño | Rol | Origen del texto de referencia |
|---|---|---|---|---|
| *HAM10000* | Dermatoscópica | 10 015 imágenes; 7 470 lesiones | Clasificación (entrenamiento, validación y prueba) | Sin texto. Etiqueta por histopatología (53.32 %), seguimiento (36.99 %, solo nevus), consenso (9.01 %) o confocal (0.69 %) |
| *SkinCaRe*: SkinCAP | Clínica (Fitzpatrick 17k, DDI) | 4 000 en el paper; 3 561 usadas | Entrenamiento de la generación | Descripciones escritas por cuatro dermatólogos (en chino, traducidas al inglés) |
| *SkinCaRe*: SkinCoT | Clínica (DermNet, ver pregunta 4) | 3 041 | Entrenamiento de la generación (razonamiento) | Observación por Gemini 2.5 Pro; razonamiento por GPT-o4-mini con la etiqueta; certificado por dermatólogos |
| *MM-Skin* | Clínica, patológica y «derm» (a verificar) | 11 015 imágenes; 27 259 pares VQA | Evaluación de la generación con referencia | Descripciones de libros de texto; VQA generadas con Llama-3.1 y validadas |
| *HIBA* | Dermatoscópica (1 270) y clínica (346) | 1 616 imágenes; 1 246 lesiones | Evaluación fuera de distribución (solo prueba) | Diagnóstico de dermatólogos del hospital; histopatología en 1 036 imágenes |
| *Derm1M* | Dermatoscópica y clínica (según el paper) | 1 029 761 pares | Preentrenamiento de DermLIP (no se entrena ni se evalúa aquí) | YouTube, PubMed, foros, material educativo, SCIN y MSKCC; texto procesado con LLM y ontología |

**Tabla 3.2 (`tab:met_tamanos`)**. Imágenes por clase y partición, en HAM10000. Columnas: clase, entrenamiento, validación, prueba (las tres particiones de la nueva), descartadas (las 776 del test original que estaban en entrenamiento o validación).

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

Cifras: entrenamiento y validación, de `ham10000_splits_lesion.json`; prueba, idéntica al original; descartadas = diferencia con el original. Los totales cuadran con 10 015. Para el texto, el original tenía 7 010 / 1 502 / 1 503.

**Listado 3.x (SkinCoT, ejemplo de formato).** Fragmento en inglés del archivo `EN/Acne and Rosacea Photos/07PerioralDermEye.jpg.txt`, con traducción propia al español si el autor la acepta (pregunta 3). Solo dos o tres oraciones, con el bloque `<think>`, y la oración final con el diagnóstico.

**Figuras y tablas previstas**

| Elemento | Qué muestra | De dónde sale | Estado |
|---|---|---|---|
| Tabla 3.1 `tab:met_conjuntos` | Conjuntos, modalidad, tamaño, rol y origen del texto | `Docs/experimentacion/experimentacion.tex` (`tab:datasets`, líneas 189–222), corregida: HIBA con fototipos I–IV, no III–VI; tamaños nuevos | a adaptar |
| Tabla 3.2 `tab:met_tamanos` | Tamaños por clase y partición, con descartadas | `Codigo/data/splits/ham10000_splits_lesion.json` + metadata | a armar (conteos hechos; falta el script) |
| Figura `fig:met_ham_dist` | Distribución de las 7 clases, con porcentajes | `Docs/experimentacion/imagenes/F0_ham_dist.png` tiene los mismos conteos, pero usa una paleta que no es Okabe–Ito y el título no tiene tildes | a regenerar (Okabe–Ito, PDF vectorial) |
| Figura `fig:met_ham_lesiones` | Histograma de imágenes por lesión (5 514 / 1 423 / 490 / 34 / 5 / 4) | Metadata de HAM10000 | a generar (script en `Codigo/scripts/`, según el orden de trabajo del capítulo) |
| Ejemplos por clase (opcional) | Una imagen por clase de HAM10000 | `Codigo/data/raw/HAM10000/` | a generar solo si la licencia lo permite (pregunta 1) |
| Listado SkinCoT | Formato `<think>` con la oración final | Archivo `.txt` del conjunto | a armar (cita corta, pregunta 3) |
| `ej_skincot_human.jpg` | — | Tiene la marca «©DermNet.com» y es una foto, no texto de SkinCoT | no usar (pregunta 2) |

## Prosa ya escrita que se conserva

- El párrafo de las siete categorías y su gravedad (`02-datos-particiones.tex`, líneas 7–12) **se mueve a 3.1** (P3 de `01-tareas.md`), no se conserva en 3.3. En 3.3 queda una sola oración de remisión a `sec:met_tareas`. La frase final de ese párrafo («esa gradación determina cuánto cuesta cada confusión…») pasa a 3.4.
- El `\pendiente` de composición y distribución (línea 14) y el de la partición (líneas 18–27) se reemplazan con la prosa de P2–P9; los números de ese pendiente (36 %, 63 %) se corrigen a dos decimales con su fuente (P6).
- El `\pendiente` de SkinCaRe, MM-Skin y HIBA (líneas 30–33) se reemplaza por 3.3.3 y 3.3.4. Su remisión a `sec:marco_generalizacion` se conserva.
- El `\subsection{Preprocesamiento y aumento de datos}` (líneas 35–36) **sale de 3.3**: va a 3.5 (D7 de la ficha del capítulo).
- El label `sec:met_ham` se queda en 3.3 sobre el análisis de HAM10000, como fija `01-tareas.md` (D5).

## Lo que va al apéndice

Apéndice F (`Chapters/Apendices/F-Fichas-Datasets-Modelos.tex`), una ficha por conjunto: fuente y versión de cada archivo; estructura de carpetas; licencia (HAM10000, SkinCaRe, MM-Skin, HIBA CC BY, DermLIP CC BY-NC-4.0); tabla completa del mapeo HIBA → HAM10000 (`src/data/hiba.py`); porcentajes de fuentes de Derm1M; la fuga por clase completa (si la tabla no entra en el cuerpo); el detalle de los splits (`ham10000_splits*.json`, `skincare_*`, `mmskin_splits.json`, `hiba_splits.json`); el listado de excepciones de SkinCAP.

## Lo que NO va en esta sección (y dónde está)

- Las siete categorías, su gravedad y las tres tareas: 3.1 (`sec:met_tareas`).
- Preprocesamiento (resolución, normalización), aumento de datos y TTA: 3.5 (`sec:met_supervisados`).
- Efecto de la fuga sobre las métricas (cifras de sensibilidad macro con la partición anterior y la nueva, subconjunto limpio, DermLIP sobre cada subconjunto): Cap. 4 (los números no se dan en 3.3, por la regla de que el Cap. 3 no presenta desempeños).
- Métricas, líneas base, umbral de melanoma, criterio de selección: 3.4 (`sec:met_protocolo`, `sec:met_seleccion`).
- Resultados de HIBA por modalidad y fototipo: Caps. 4–5 (3.9 define el protocolo).
- Definiciones de fuga de información, partición, desbalance, dominio y generalización: Cap. 2 (solo se nombran con `\ref`).
- Grillas de hiperparámetros, LoRA y el ajuste en dos etapas: 3.5 y 3.7.
- Los resultados de RAG y de la cascada, y las cifras de la revisión del 03/10 sobre la métrica oficial: Caps. 4–5.
- Histopatología fuera de alcance: Cap. 1 (ya acordado).

## Preguntas abiertas para el autor

1. **Licencia de HAM10000 y ejemplos por clase.** La tabla 1 del paper de HAM10000 indica CC BY-NC 4.0 para la mayoría de sus fuentes (y CC-0 para una). ¿Se reproducen ejemplos por clase en la tesina? Si la respuesta es no, se omite la figura opcional. Verificar la licencia de la versión descargada en Harvard Dataverse.
2. **`ej_skincot_human.jpg`.** Es una foto de DermNet con la marca «©DermNet.com» y no un texto de SkinCoT, como decía la ficha del capítulo. Propongo no usarla. ¿Se usa? Si se usara, requiere permiso de DermNet.
3. **Traducción del ejemplo de SkinCoT.** El texto está en inglés. ¿Se cita en inglés o se traduce? Propongo traducción propia marcada como tal (una o dos oraciones con el bloque `<think>`).
4. **Origen de las imágenes de SkinCoT.** El paper dice que provienen de DermNet. El README y el acuerdo de uso de SkinCaRe mencionan Fitzpatrick 17k, DDI y SKINCON como fuentes de las imágenes. Verificar antes de describirlo.
5. **Licencia y uso de SkinCaRe.** El README tiene dos licencias: el cuerpo dice CC-BY-4.0 y el encabezado YAML dice cc-by-nc-sa-4.0. El acuerdo de uso exige investigación no comercial y prohíbe redistribuir copias. Decidir cómo se cita y si los textos de ejemplo cumplen con el acuerdo (propongo citas cortas).
6. **MM-Skin.** El archivo local tiene 11 090 filas (11 015 imágenes), y el paper dice «casi 10 000» pares. ¿Qué versión se usa? ¿«derm» en la columna `modality` es dermatoscopia? Verificar.
7. **MM-Skin, partición.** ¿La evaluación de generación usa el test de `mmskin_splits.json` (1 653 imágenes) o el archivo completo?
8. **HIBA, cuántas imágenes.** La revisión del 03/10 usa las 1 616. El archivo `hiba_splits.json` tiene 243 de prueba (1 131 / 242 / 243) y `phase0_data.yaml` lo referencia. La ficha asume las 1 616 completas. Confirmar.
9. **HIBA, fototipos.** El CSV cuenta por imagen (I 114, II 1 085, III 275, IV 25, vacío 117). El paper cuenta por paciente sobre 566 pacientes (I 44, II 451, III 66, IV 5). ¿Qué se reporta? Propongo por imagen, con la nota.
10. **HIBA, mapeo.** SCC → AKIEC (`src/data/hiba.py`, comentario de caveat). ¿Se declara como limitación en 3.9 y en la tabla SOTA? Propongo que sí.
11. **Derm1M no está en el repo.** Las cifras son del paper (1 029 761 pares y los porcentajes de fuentes). Verificar la variante de DermLIP que usa el trabajo en 3.6 (`vit-b-16` según `dermlip.py`).
12. **«DermLIP nunca vio HAM10000».** Según la lista de fuentes del paper de Derm1M, no hay HAM10000 (sus datasets públicos son SCIN y MSKCC). Pero no se puede descartar que figuras de PubMed o de material educativo reproduzcan imágenes de HAM. La ficha lo redacta como «según las fuentes declaradas». ¿Se acepta esa formulación?
13. **SkinCAP, las 439 marcas.** El archivo las marca «Do not consider this image». El código las excluye, pero el motivo no está documentado en el repo. ¿Se conoce? La tesina debería decirlo en una frase.
14. **Referencias que faltan.** DermNet (sitio web), Gemini 2.5 Pro y GPT-o4-mini (solo si se citan los generadores de SkinCoT; si no, se atribuye a SkinCaRe), Llama-3.1 (solo si se cita). Se proponen para `refs_pendientes.md` con título, autores, año y URL.
15. **Clave de HIBA.** El encargo pedía `riccilara2023hiba`; la clave que existe es `riccilara2023dataset`. Uso esa.
16. **Clave de Derm1M.** Propongo `yan2025derm1miccv` (publicado) y no la arXiv `yan2025derm1m`. ¿Conviene la misma para todo el documento? (Chequear en 3.6.)
17. **Figura de distribución.** `F0_ham_dist.png` no sigue la paleta Okabe–Ito. Propongo regenerarla con un script en `Codigo/scripts/` para que los números queden reproducibles.
18. **Formato numérico.** La guía fija punto decimal; no fija el separador de miles. `experimentacion.tex` escribe «10.015», que se lee como decimal. Propongo espacio fino (`10\,015`) y dos decimales en porcentajes (guía §4).
19. **Siglas de las categorías.** Las siglas (MEL, NV…) se declaran con `\gls` en la primera aparición del documento, que es 3.1 si el Cap. 2 no las usa antes. Verificar con `grep` sobre `Chapters/02-Marco-Teorico`.
20. **Dependencia de 3.1 y 3.2.** Esta ficha asume las decisiones de `01-tareas.md` (D5, labels) y de `02-flujo-trabajo.md`. Si cambian, el «Viene de» y la P1 se ajustan.
21. **Derm1M, fuentes en la tabla.** Los porcentajes son de la Fig. 1a del paper y no de un conteo local. Si el autor prefiere, se reduce a «la mayor parte de texto de YouTube y PubMed».

## Decisiones tomadas por cuenta propia

- **D1. Test fijo y validación por distribución.** El test es el original (1 503). La validación es el fold de `StratifiedGroupKFold` cuya distribución de clases se parece más a la global. Ese criterio no usa desempeño, así que no contamina la selección (`split_lesion_resul_20260926.md` §2 lo describe igual).
- **D2. Fuga contada por subconjunto de entrenamiento.** El número principal es 543 (36.13 %), que corresponde a lesiones de entrenamiento, como en `leakage_analysis.json`. Los 66 de validación se mencionan aparte. Así el subconjunto limpio (894) coincide con el del script.
- **D3. Sin desempeño en 3.3.** Ninguna cifra de sensibilidad, exactitud o AUC aparece en esta sección. El efecto de la fuga se describe como método, no como resultado.
- **D4. DermLIP como control, con la atribución de la lista de fuentes.** Se mantiene el control del plan de 2026-09-12, con la formulación de la pregunta 12.
- **D5. Limitación de la referencia benigna.** El 62.74 % de NV no tiene histopatología. Se incluye en P5 como limitación (no como decisión de diseño), porque no cambia la partición. Su tratamiento corresponde a 3.4.
- **D6. Títulos de subsección.** Cuatro subsecciones con títulos descriptivos y ningún título de párrafo, según la guía §3.
- **D7. Atribución de la afirmación de HIBA.** «Primera base de imágenes clínicas y dermatoscópicas en Hispanoamérica» se atribuye a los autores del dataset («que sus autores presentan como…»), porque la guía §3 prohíbe afirmar «el primero» sin fuente. La afirmación «primera evaluación sistemática» de la revisión del 03/10 (§2.8) no se usa en 3.3.
- **D8. Atribución de los generadores de SkinCoT.** Los nombres de los modelos (Gemini 2.5 Pro, GPT-o4-mini) se dan como los reporta el paper de SkinCaRe, sin citas nuevas, mientras no se decida la pregunta 14.
- **D9. «Reporte» no aparece en 3.3.** Las descripciones de MM-Skin y de SkinCAP se llaman «textos de referencia» o «descripciones», porque «reporte» designa solo el informe clínico (guía §4).
- **D10. Preprocesamiento fuera de 3.3.** El subtítulo «Preprocesamiento y aumento de datos» sale de 3.3 y va a 3.5 (D7 del capítulo).
- **D11. Tablas numeradas en el texto.** Los números de las tablas (3.1, 3.2) son provisionales y dependen de la numeración de la sección; el `.tex` los toma de `\label`.
- **D12. Corrección de cifra.** Seguimiento en HAM10000: 3 704 / 10 015 = 36.98 % (la ficha decía 36.99 %; el resto de las cifras de P5 cuadra con 100 % en 36.98).
- **D13. Columna «Descartadas» (tabla 3.2).** Cuenta, por clase, las imágenes de entrenamiento y validación originales cuya lesión aparece en prueba. El total (776) se verificó con esa regla sobre `ham10000_splits.json`. La ficha decía «del test original»; la descripción correcta es la del epígrafe del `.tex`.
- **D14. Ejemplo de SkinCoT.** Se cita el bloque `<think>` de las dos primeras oraciones del archivo y se dice en el texto que la última enuncia el diagnóstico en negrita; el diagnóstico no se reproduce.
- **D15. Figura de HAM10000.** Las figuras de datos vienen del coordinador (`plot_ham_dataset_figs.py`). En `ham-distribucion.pdf` solo MEL y BCC están en bermellón con trama; AKIEC, que P5 llama malignas o premalignas con histopatología completa, sale en azul. El epígrafe describe el color tal cual; el autor decide si AKIEC debe destacarse.
