# Referencias: pendientes y trazabilidad

`Bibliography/Bibliography.bib` es el archivo único y canónico de la tesina, y está **por delante**
de la biblioteca de Zotero (ver sección 5). Nunca se lo sobrescribe con una exportación: las
referencias nuevas se proponen acá y se agregan al `.bib`.

## 1. Referencias por incorporar

Quien redacta y necesita citar algo que no está en el `.bib` lo anota en esta tabla en lugar de
inventar una clave. Formato: título, autores, año, DOI o URL, y en qué sección hace falta.

| Título | Autores | Año | DOI / URL | Sección que la necesita |
|---|---|---|---|---|
| *(vacío)* | | | | |

## 2. Consolidación del 17/09/2026

El `.bib` se armó fusionando cuatro archivos dispersos: `estado_del_arte/referencias.bib` (37),
`marco_teorico/referencias.bib` (33), `tabla_resultados_sota/referencias_sota.bib` (14) y la
versión previa de `Bibliography.bib` (16). De 100 entradas en bruto quedaron **72 únicas**: 28 eran
duplicados del mismo trabajo con tres convenciones de clave distintas. Se conservó siempre la
entrada con más campos bibliográficos.

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

Contrastando las 72 entradas del `.bib` contra la biblioteca:

| | Entradas |
|---|---|
| Vivas en Zotero | 31 |
| **Solo en la papelera de Zotero** | **36** |
| Nunca estuvieron en Zotero (agregadas a mano al `.bib`) | 5 |

Las 5 que no están en Zotero son `tschandl2018ham10000` (HAM10000), `liu2021swin` (Swin
Transformer), `shen2025skincare` (SkinCaRe), `nvidia2023beginners` y
`atkinsonabutridy2025language`.

**Conviene recuperar de la papelera las 36 entradas antes de vaciarla**, porque son referencias que
el documento usa y ahí están sus PDF y sus metadatos. Mientras esa diferencia exista, una
exportación de Zotero sobre `Bibliography.bib` borraría 41 de las 72 referencias.
