# Referencias: pendientes y trazabilidad

`Bibliography/Bibliography.bib` es el archivo único y canónico de la tesina, y está **por delante**
de la biblioteca de Zotero (ver sección 5). Nunca se lo sobrescribe con una exportación: las
referencias nuevas se proponen acá y se agregan al `.bib`.

## 1. Referencias incorporadas y por incorporar

Quien redacta y necesita citar algo que no está en el `.bib` lo anota en la tabla «Por incorporar»
en lugar de inventar una clave: título, autores, año, DOI o URL, y en qué sección hace falta.

### Encuadre clínico del Capítulo 1 — incorporado el 17/09/2026

El `.bib` no tenía ninguna referencia que sostuviera el encuadre clínico y epidemiológico con el que
abre la introducción: las 72 entradas cubrían el lado de aprendizaje automático del trabajo. Se
incorporaron ocho, cada una verificada contra la página del editor.

| Clave | Referencia | Sostiene |
|---|---|---|
| `bray2024global` | Bray et al., *CA: A Cancer Journal for Clinicians* 74(3):229–263, 2024 (GLOBOCAN 2022) | Incidencia y mortalidad globales |
| `loria2020cutaneous` | Loria et al., *ecancermedicalscience* 14:1017, 2020 — Registro Argentino de Melanoma Cutáneo, 10 199 casos entre 2002 y 2018 | Datos de Argentina, con diferencias regionales |
| `kittler2002diagnostic` | Kittler et al., *The Lancet Oncology* 3(3):159–165, 2002 | La dermatoscopía mejora la exactitud, pero solo en examinadores experimentados |
| `vestergaard2008dermoscopy` | Vestergaard et al., *British Journal of Dermatology* 159(3):669–676, 2008 | Meta-análisis de dermatoscopía frente a ojo desnudo en entorno clínico |
| `esteva2017dermatologistlevel` | Esteva et al., *Nature* 542(7639):115–118, 2017 | Desempeño a nivel de dermatólogo con redes profundas |
| `tschandl2019comparison` | Tschandl et al., *The Lancet Oncology* 20(7):938–947, 2019 — 511 lectores humanos frente a 139 algoritmos | Los clasificadores superan a los expertos, y la dispersión entre lectores |
| `freeman2026global` | Freeman et al., *JAMA Dermatology*, en línea el 26/08/2026 — 158 países | Densidad media de 2.66 dermatólogos por 100 000 habitantes, de 0.37 en países de ingreso bajo a 5.05 en los de ingreso alto |
| `sinsky2016allocation` | Sinsky et al., *Annals of Internal Medicine*, 2016 | 49.2 % del tiempo de consultorio en registros y escritorio, más 1 a 2 horas fuera de horario |

**Qué quedó incompleto en esas entradas.** Nada que impida citarlas, pero conviene completarlo:

- `vestergaard2008dermoscopy` quedó sin DOI: no pude verificarlo y preferí omitirlo antes que
  arriesgar uno equivocado.
- `sinsky2016allocation` quedó sin volumen ni páginas, por la misma razón.
- `freeman2026global` es una publicación en línea anticipada y todavía no tiene volumen ni páginas.
- `tschandl2019comparison` y `freeman2026global` llevan la lista de autores truncada con
  `and others`. Como el estilo está configurado con `maxnames=1`, la bibliografía imprime igual
  «Autor et al.», así que la salida no cambia; completarla es prolijidad, no necesidad.

### Por incorporar

| Título | Autores | Año | DOI / URL | Sección que la necesita |
|---|---|---|---|---|
| *(vacío)* | | | | |

## 2. Consolidación del 17/09/2026

El `.bib` se armó fusionando cuatro archivos dispersos: `estado_del_arte/referencias.bib` (37),
`marco_teorico/referencias.bib` (33), `tabla_resultados_sota/referencias_sota.bib` (14) y la
versión previa de `Bibliography.bib` (16). De 100 entradas en bruto quedaron **72 únicas**: 28 eran
duplicados del mismo trabajo con tres convenciones de clave distintas. Se conservó siempre la
entrada con más campos bibliográficos. Con las ocho referencias de la sección 1, el archivo llegó a
**80 entradas**.

Las claves quedaron normalizadas como `<apellido><año><palabra>`. Como ningún capítulo tenía citas
todavía, el renombre no rompió nada. Validación: `biber --tool --validate-datamodel` pasa con 0
errores y 0 advertencias.

Se descartaron los campos locales de Zotero (`file` con rutas del disco personal, `abstract`,
`keywords`, `urldate`), se quitaron `publisher = {arXiv}` y `number = {arXiv:...}` de los
preprints —la información ya está en `eprint`/`eprinttype`— y se normalizaron los ISSN que Zotero
exportaba sin guion o duplicados.

## 3. Datos completados a mano: verificar en Zotero

Zotero exportó estas entradas sin fecha y/o sin lugar de publicación, y tipadas como `@article`
aunque son trabajos de congreso. Se completaron con el año y el congreso de la publicación de
referencia, sin volumen ni páginas. El dato quedó corregido en el `.bib`; corregirlo también en
Zotero es opcional y sirve para que la biblioteca no quede con metadatos peores que el documento.

| Clave | Año | Lugar de publicación asignado |
|---|---|---|
| `vaswani2017attention` | 2017 | Advances in Neural Information Processing Systems |
| `devlin2019bert` | 2019 | Proceedings of the 2019 Conference of the NAACL |
| `brown2020language` | 2020 | Advances in Neural Information Processing Systems |
| `radford2021learning` | 2021 | Proceedings of the 38th ICML |
| `lewis2020retrievalaugmented` | 2020 | Advances in Neural Information Processing Systems |
| `lin2004rouge` | 2004 | Text Summarization Branches Out |
| `goodfellow2014generative` | 2014 | Advances in Neural Information Processing Systems |
| `ho2020denoising` | 2020 | Advances in Neural Information Processing Systems |
| `ouyang2022training` | 2022 | Advances in Neural Information Processing Systems |
| `rezende2015variational` | 2015 | Proceedings of the 32nd ICML |
| `moor2023medflamingo` | 2023 | Proceedings of the 3rd Machine Learning for Health Symposium |
| `daneshjou2022skincon` | 2022 | Advances in NeurIPS: Datasets and Benchmarks Track |
| `rumelhart1986learning` | 1986 | Nature (queda como `@article`) |

Dos correcciones más:

- `papineni2002bleu`: Zotero fechaba el trabajo en 2001 (el informe técnico de IBM). El DOI
  registrado corresponde a la publicación de ACL 2002, que es la que se cita habitualmente.
- La entrada `liu_deep_2025` de `estado_del_arte/referencias.bib` estaba mal atribuida (el primer
  autor es Yan, no Liu) y sin campo `title`. Es el mismo trabajo que `yan2025derm1m`, con el que se
  fusionó. La entrada `DermLIP2025` de `referencias_sota.bib` era otra copia del mismo trabajo, con
  el título truncado y sin DOI; se descartó.

## 4. Entradas sin revisar

`nvidia2023beginners` («A Beginner's Guide to Large Language Models: Part 1») es un *ebook* de
divulgación de NVIDIA, sin URL ni revisión por pares. Habría que decidir si se cita en el marco
teórico o si se reemplaza por una fuente arbitrada; si se conserva, hace falta agregarle la URL.

## 5. Estado de la biblioteca de Zotero (17/09/2026)

Zotero 7.0.32, biblioteca local en `C:\Users\Facu\Zotero`, 216 elementos en total. De ellos, solo
**31 son referencias bibliográficas vivas** (16 artículos, 14 *preprints*, 1 trabajo de congreso);
el resto son adjuntos y notas, y **65 elementos están en la papelera**.

Contrastando contra la biblioteca las 72 entradas que el `.bib` tenía antes de las incorporaciones
del 17/09/2026:

| | Entradas |
|---|---|
| Vivas en Zotero | 31 |
| **Solo en la papelera de Zotero** | **36** |
| Nunca estuvieron en Zotero (agregadas a mano al `.bib`) | 5 |

Las 5 que no están en Zotero son `tschandl2018ham10000` (HAM10000), `liu2021swin` (Swin
Transformer), `shen2025skincare` (SkinCaRe), `nvidia2023beginners` y
`atkinsonabutridy2025language`. Las ocho de la sección 1 tampoco están, porque se agregaron
directamente al `.bib`: en total son 13 referencias que solo existen en el documento.

**Conviene recuperar de la papelera las 36 entradas antes de vaciarla**, porque son referencias que
el documento usa y ahí están sus PDF y sus metadatos. Mientras esa diferencia exista, una
exportación de Zotero sobre `Bibliography.bib` borraría 49 de las 80 referencias.

## 6. Auditoría por año (17/09/2026)

La ventana de referencia fijada en la guía es 2020–2026. De las 80 entradas del `.bib`, **57 están
dentro de la ventana y 23 son anteriores**. Las 23 cumplen alguna de las excepciones, así que
ninguna se descarta, pero conviene tener escrito por qué está cada una: la razón determina *cómo*
se la cita.

### Fundacionales: se citan por lo que definen, no como estado del arte

| Clave | Año | Se cita para |
|---|---|---|
| `rumelhart1986learning` | 1986 | Retropropagación |
| `hornik1989multilayer` | 1989 | Aproximación universal |
| `elman1990finding` | 1990 | Redes recurrentes |
| `papineni2002bleu` | 2002 | Definición de BLEU |
| `lin2004rouge` | 2004 | Definición de ROUGE |
| `fawcett2006introduction` | 2006 | Análisis ROC y AUC |
| `pan2010survey` | 2010 | Transferencia de aprendizaje |
| `mikolov2013efficient` | 2013 | Representaciones distribuidas de palabras |
| `goodfellow2014generative` | 2014 | Redes generativas adversarias |
| `he2015residual` | 2015 | ResNet y conexiones residuales |
| `hinton2015distilling` | 2015 | Destilación de conocimiento |
| `rezende2015variational` | 2015 | Flujos normalizantes |
| `simonyan2015very` | 2015 | VGG |
| `vaswani2017attention` | 2017 | El *transformer* y la atención: **es el corte mismo** |
| `huang2018densely` | 2018 | DenseNet, arquitectura usada en el trabajo |
| `devlin2019bert` | 2019 | Pre-entrenamiento bidireccional |
| `shorten2019survey` | 2019 | Aumento de datos |

Ninguna de estas se usa para sostener una afirmación sobre el desempeño alcanzable hoy. Se citan
donde se define el concepto —marco teórico, mayormente— y no en el estado del arte.

### Información difícil de conseguir o recurso propio del trabajo

| Clave | Año | Por qué entra |
|---|---|---|
| `kittler2002diagnostic` | 2002 | Meta-análisis de la exactitud de la dermatoscopía; es la referencia canónica y no hay reemplazo reciente equivalente |
| `vestergaard2008dermoscopy` | 2008 | Meta-análisis de dermatoscopía frente a ojo desnudo en entorno clínico |
| `sinsky2016allocation` | 2016 | Medición del tiempo clínico dedicado a documentación; dato difícil de obtener |
| `tschandl2018ham10000` | 2018 | Artículo original de HAM10000, el conjunto de datos del trabajo |

### Hitos del período anterior al cambio de paradigma

| Clave | Año | Cómo se cita |
|---|---|---|
| `esteva2017dermatologistlevel` | 2017 | Hito de la era de las CNN: establece que el aprendizaje profundo alcanzó desempeño de especialista. Se presenta fechado y como punto de partida, no como estado del arte |
| `tschandl2019comparison` | 2019 | Estudio de lectores previo a los *transformers*; aporta la comparación con humanos y la dispersión entre lectores, que no cambian con la arquitectura |

### Acceso

Las 23 entradas de arXiv del `.bib` son de acceso abierto por construcción. De las ocho
incorporadas para el Capítulo 1, se verificó texto completo libre en `loria2020cutaneous` (en PMC) y
`sinsky2016allocation` (PDF público). Las de revistas clínicas —*Lancet Oncology*, *British Journal
of Dermatology*, *JAMA Dermatology*, *Nature*— habría que revisarlas una por una; en esos casos
suele no haber alternativa abierta equivalente y la excepción de la guía aplica.
