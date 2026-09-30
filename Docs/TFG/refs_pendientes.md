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
| `bray2024global` (sin usar, ver más abajo) | Bray et al., *CA: A Cancer Journal for Clinicians* 74(3):229–263, 2024 (GLOBOCAN 2022) | Incidencia y mortalidad globales |
| `loria2020cutaneous` | Loria et al., *ecancermedicalscience* 14:1017, 2020 — Registro Argentino de Melanoma Cutáneo, 10 199 casos entre 2002 y 2018 | Datos de Argentina, con diferencias regionales |
| `kittler2002diagnostic` | Kittler et al., *The Lancet Oncology* 3(3):159–165, 2002 | La dermatoscopía mejora la exactitud, pero solo en examinadores experimentados |
| `vestergaard2008dermoscopy` | Vestergaard et al., *British Journal of Dermatology* 159(3):669–676, 2008 | Meta-análisis de dermatoscopía frente a ojo desnudo en entorno clínico |
| `esteva2017dermatologistlevel` | Esteva et al., *Nature* 542(7639):115–118, 2017 | Desempeño a nivel de dermatólogo con redes profundas |
| `tschandl2019comparison` | Tschandl et al., *The Lancet Oncology* 20(7):938–947, 2019 — 511 lectores humanos frente a 139 algoritmos | Los clasificadores superan a los expertos, y la dispersión entre lectores |
| `freeman2026global` | Freeman et al., *JAMA Dermatology*, en línea el 26/08/2026 — 158 países | Densidad media de 2.66 dermatólogos por 100 000 habitantes, de 0.37 en países de ingreso bajo a 5.05 en los de ingreso alto |
| ~~`sinsky2016allocation`~~ | Sinsky et al., *Annals of Internal Medicine*, 2016 | **Reemplazada** por `arndt2017tethered` (25/09) |

**Qué quedó incompleto en esas entradas.** Nada que impida citarlas, pero conviene completarlo:

- `vestergaard2008dermoscopy` quedó sin DOI: no pude verificarlo y preferí omitirlo antes que
  arriesgar uno equivocado.
- `sinsky2016allocation` quedó sin volumen ni páginas, por la misma razón.
- `freeman2026global` es una publicación en línea anticipada y todavía no tiene volumen ni páginas.
- `tschandl2019comparison` y `freeman2026global` llevan la lista de autores truncada con
  `and others`. Como el estilo está configurado con `maxnames=1`, la bibliografía imprime igual
  «Autor et al.», así que la salida no cambia; completarla es prolijidad, no necesidad.

### Epidemiología con cifras — incorporado el 17/09/2026

Al redactar §1.1 hubo que poner números donde antes había solo afirmaciones cualitativas, y las ocho
referencias anteriores no alcanzaban. Se incorporaron dos, verificadas contra la fuente.

| Clave | Referencia | Sostiene |
|---|---|---|
| `sung2026global` | Sung et al., *CA: A Cancer Journal for Clinicians* 76(4):e70090, 2026 (GLOBOCAN 2024, 34 cánceres en 186 países) | Incidencia y mortalidad de melanoma (337 969 casos, 58 398 muertes) y de cáncer de piel no melanoma (1 138 314 casos, 58 721 muertes) |
| `nci2026melanoma` | *SEER Cancer Stat Facts: Melanoma of the Skin*, National Cancer Institute, consultado el 17/09/2026 | Supervivencia relativa a cinco años por estadio (100.0 / 76.0 / 34.0 %) y distribución de los casos por estadio al diagnóstico (77 / 10 / 5 %), sobre SEER 21 (sin Illinois), 2016--2022 |

**`bray2024global` quedó superado y ya no se cita.** Es GLOBOCAN 2022 y sus cifras difieren de las de
GLOBOCAN 2024, publicado el 08/07/2026; citar las dos ediciones para la misma afirmación sería acumular
referencias. La entrada se conserva en el `.bib` sin usar: no molesta, porque biblatex solo imprime lo
citado. Si aparece una afirmación que necesite específicamente las estimaciones de 2022, está disponible.

**`nci2026melanoma` es el único recurso en línea del `.bib`.** Es la cita habitual para la supervivencia
por estadio y es de acceso abierto; la alternativa arbitrada equivalente no existe con esa granularidad y
actualización. Lleva `urldate`, que es el único caso del archivo en el que ese campo hace falta.

**Corrección que produjo `sung2026global`.** La primera redacción de §1.1 afirmaba que el melanoma
«concentra la mayor parte de la mortalidad» por cáncer de piel. Es falso: GLOBOCAN 2024 da 58 398 muertes
por melanoma y 58 721 por el resto de los cánceres de piel, es decir casi por partes iguales. Lo que sí es
cierto, y es la afirmación que quedó en el texto, es que el melanoma es menos de una cuarta parte de los
casos y prácticamente la mitad de las muertes. La subregistración conocida del cáncer de piel no melanoma
solo refuerza esa asimetría, porque infla el denominador de la incidencia y no el de la mortalidad.

### Marco teórico del Capítulo 2 — incorporado el 22/09/2026

El esqueleto de `Chapters/02-Marco-Teorico.tex` exige referencias que no estaban en el `.bib`: la
clínica, la calibración, la inferencia estadística, las métricas de generación modernas y dos
arquitecturas. Se incorporaron **26 entradas**, cada una verificada contra el editor o el
repositorio oficial. El `.bib` pasó de 82 a **108 entradas**. Las claves siguen el patrón
`<apellido><año><palabra>` y quedan fijadas por esta tabla: la redacción las usa con estos
nombres. Las entradas se agregaron al final del archivo, no en orden alfabético, porque biblatex
imprime en orden de aparición.

| Clave | Referencia | Sostiene | Sección |
|---|---|---|---|
| `lecun1998gradient` | LeCun et al., *Proceedings of the IEEE* 86(11):2278–2324, 1998 | Operación de convolución y conectividad local | 2.2.1 |
| `russakovsky2015imagenet` | Russakovsky et al., *IJCV* 115(3):211–252, 2015 (ILSVRC) | Pre-entrenamiento en ImageNet | 2.2.4 |
| `lin2017focal` | Lin et al., *ICCV* 2999–3007, 2017 | Pérdida focal | 2.2.4 |
| `argenziano1998checklist` | Argenziano et al., *Arch Dermatol* 134(12):1563–1570, 1998 | Lista de 7 puntos | 2.1.3 |
| `carrera2016validity` | Carrera et al., *JAMA Dermatol* 152(7):798–806, 2016 | Concordancia entre observadores por criterio dermatoscópico | 2.1.3 |
| `kittler2016standardization` | Kittler et al., *JAAD* 74(6):1093–1106, 2016 | Terminología dermatoscópica estandarizada | 2.1.3 |
| `liu2022convnet` | Liu et al., *CVPR* 11976–11986, 2022 | ConvNeXt | 2.2.1 |
| `ren2020balanced` | Ren et al., *NeurIPS* 33:4175–4186, 2020 | *Balanced softmax* | 2.2.4 |
| `holtzman2020curious` | Holtzman et al., *ICLR*, 2020 | Muestreo de núcleo y degeneración textual | 2.3.1 |
| `khandelwal2020generalization` | Khandelwal et al., *ICLR*, 2020 | kNN-LM, base del RAG por vecinos | 2.4.4 |
| `jing2018automatic` | Jing, Xie y Xing, *ACL* 2577–2586, 2018 | Origen del *image captioning* médico | 2.4.3 |
| `chen2020generating` | Chen et al., *EMNLP* 1439–1449, 2020 | R2Gen, reportes de radiología | 2.4.3 |
| `gu2024medvh` | Gu et al., 2024, `arXiv:2407.02730` | Alucinación en VLMs médicos | 2.4.3 |
| `sun2025factaware` | Sun et al., *NAACL*, 2025 | FactMM-RAG, RAG multimodal para reportes | 2.4.4 |
| `guo2017calibration` | Guo et al., *ICML* (PMLR 70):1321–1330, 2017 | ECE, *temperature scaling*, *vector scaling* | 2.5.2 |
| `brier1950verification` | Brier, *Mon Weather Rev* 78(1):1–3, 1950 | Puntaje de Brier | 2.5.2 |
| `banerjee2005meteor` | Banerjee y Lavie, *ACL Workshop* 65–72, 2005 | METEOR | 2.5.3 |
| `vedantam2015cider` | Vedantam, Zitnick y Parikh, *CVPR* 4566–4575, 2015 | CIDEr | 2.5.3 |
| `zhang2020bertscore` | Zhang et al., *ICLR*, 2020 | BERTScore | 2.5.3 |
| `mcnemar1947note` | McNemar, *Psychometrika* 12(2):153–157, 1947 | Prueba de McNemar | 2.5.4 |
| `wilcoxon1945individual` | Wilcoxon, *Biometrics Bull* 1(6):80–83, 1945 | Prueba de Wilcoxon | 2.5.4 |
| `efron1979bootstrap` | Efron, *Ann Statist* 7(1):1–26, 1979 | *Bootstrap* | 2.5.4 |
| `selvaraju2017gradcam` | Selvaraju et al., *ICCV* 618–626, 2017 | Grad-CAM | 2.5.5 |
| `codella2019skin` | Codella et al., 2019, `arXiv:1902.03368` | Archivo y retos ISIC | 2.6 |
| `mendonca2013ph2` | Mendonça et al., *EMBC* 5437–5440, 2013 | Conjunto PH2 | 2.6 |
| `abdin2024phi3` | Abdin et al., 2024, `arXiv:2404.14219` | Phi-3.5-Vision | 2.7.2 |

**Qué quedó incompleto.** `kittler2016standardization` quedó sin DOI: se verificó el PMID
(26896294) y se registró la URL de PubMed en lugar de arriesgar un DOI equivocado. Las listas de
autores de `abdin2024phi3`, `carrera2016validity`, `codella2019skin`, `kittler2016standardization`
y `russakovsky2015imagenet` van truncadas con `and others`: el estilo imprime «Autor et al.» igual,
porque está con `maxnames=1`.

**Cómo se citan las de antes de 2020.** Todas cumplen una de las excepciones de la guía, sección 6:
fundacionales (`lecun1998gradient`, `lin2017focal`, `guo2017calibration`, `brier1950verification`,
`banerjee2005meteor`, `vedantam2015cider`, `mcnemar1947note`, `wilcoxon1945individual`,
`efron1979bootstrap`, `selvaraju2017gradcam`), recursos originales del trabajo
(`mendonca2013ph2`) o información clínica difícil de obtener (`argenziano1998checklist`,
`carrera2016validity`, `kittler2016standardization`). Se citan donde se define el concepto y nunca
como desempeño alcanzable hoy.

### Por incorporar

| Título | Autores | Año | DOI / URL | Sección que la necesita |
|---|---|---|---|---|
| Una referencia clínica sobre la **estructura del informe dermatológico** (descripción, impresión diagnóstica, diagnóstico diferencial, recomendación de manejo). Candidatos: las guías de documentación de la AAD o un manual de dermatología clínica | por definir | — | — | §3.4 ¶1 (antes §2.1.3 ¶1; movido el 25/09/2026) |
| Deep Learning (MIT Press) | Goodfellow, Bengio, Courville | 2016 | https://www.deeplearningbook.org/ | §2.1 fundamentos (propuesta). Clave sugerida: `goodfellow2016deep` |
| Adam: A Method for Stochastic Optimization (ICLR 2015) | Kingma, Ba | 2015 | https://arxiv.org/abs/1412.6980 | §2.1 ¶3 y LoRA. Clave sugerida: `kingma2015adam` |
| Dropout: A Simple Way to Prevent Neural Networks from Overfitting (*JMLR* 15:1929–1958) | Srivastava, Hinton, Krizhevsky, Sutskever, Salakhutdinov | 2014 | https://jmlr.org/papers/v15/srivastava14a.html | §2.1 ¶4. Clave sugerida: `srivastava2014dropout` |
| Long Short-Term Memory (*Neural Computation* 9(8):1735–1780) | Hochreiter, Schmidhuber | 1997 | https://doi.org/10.1162/neco.1997.9.8.1735 | §2.1 ¶5. Clave sugerida: `hochreiter1997long` |
| WILDS: A Benchmark of in-the-Wild Distribution Shifts (*Proceedings of the 38th ICML*, PMLR 139) | Koh, Sagawa, Marklund et al. | 2021 | https://proceedings.mlr.press/v139/koh21a.html — verificar antes de incorporar | §2.6 ¶1, definición del cambio de distribución. Clave sugerida: `koh2021wilds` |

**Entradas listas para copiar al `.bib`** (fundamentos, §2.1, redactada el 25/09/2026). Ya se citan en el
capítulo con estas claves y figuran como indefinidas hasta que se incorporen. Conviene verificarlas contra
la página del editor antes de pegarlas.

```bibtex
@book{goodfellow2016deep,
  author    = {Goodfellow, Ian and Bengio, Yoshua and Courville, Aaron},
  title     = {Deep Learning},
  publisher = {MIT Press},
  year      = {2016},
  url       = {https://www.deeplearningbook.org/},
  langid    = {english}
}

@inproceedings{kingma2015adam,
  author    = {Kingma, Diederik P. and Ba, Jimmy},
  title     = {{Adam}: A Method for Stochastic Optimization},
  booktitle = {Proceedings of the 3rd International Conference on Learning Representations (ICLR)},
  year      = {2015},
  eprint    = {1412.6980},
  eprinttype = {arXiv},
  langid    = {english}
}

@article{srivastava2014dropout,
  author    = {Srivastava, Nitish and Hinton, Geoffrey and Krizhevsky, Alex and Sutskever, Ilya and Salakhutdinov, Ruslan},
  title     = {Dropout: A Simple Way to Prevent Neural Networks from Overfitting},
  journal   = {Journal of Machine Learning Research},
  volume    = {15},
  number    = {56},
  pages     = {1929--1958},
  year      = {2014},
  url       = {https://jmlr.org/papers/v15/srivastava14a.html},
  langid    = {english}
}

@article{hochreiter1997long,
  author    = {Hochreiter, Sepp and Schmidhuber, J{\"u}rgen},
  title     = {Long Short-Term Memory},
  journal   = {Neural Computation},
  volume    = {9},
  number    = {8},
  pages     = {1735--1780},
  year      = {1997},
  doi       = {10.1162/neco.1997.9.8.1735},
  langid    = {english}
}

@article{dinnes2018dermoscopy,
  author    = {Dinnes, Jacqueline and Deeks, Jonathan J. and Chuchu, Naomi and Ferrante di Ruffano, Lavinia and Matin, Rubeta N. and Thomson, David R. and Wong, Kai Yuen and Aldridge, Roger Benjamin and Abbott, Rachel and Fawzy, Monica and Bayliss, Susan E. and Grainge, Matthew J. and Takwoingi, Yemisi and Davenport, Clare and Godfrey, Kathie and Walter, Fiona M. and Williams, Hywel C.},
  title     = {Dermoscopy, with and without visual inspection, for diagnosing melanoma in adults},
  journal   = {Cochrane Database of Systematic Reviews},
  number    = {12},
  pages     = {CD011902},
  year      = {2018},
  doi       = {10.1002/14651858.CD011902.pub2},
  langid    = {english}
}

@article{demsar2006statistical,
  author    = {Dem{\v{s}}ar, Janez},
  title     = {Statistical Comparisons of Classifiers over Multiple Data Sets},
  journal   = {Journal of Machine Learning Research},
  volume    = {7},
  pages     = {1--30},
  year      = {2006},
  url       = {https://jmlr.org/papers/v7/demsar06a.html},
  langid    = {english}
}

@article{arndt2017tethered,
  author    = {Arndt, Brian G. and Beasley, John W. and Watkinson, Michelle D. and Temte, Jonathan L. and Tuan, Wen-Jan and Sinsky, Christine A. and Gilchrist, Valerie J.},
  title     = {Tethered to the {EHR}: Primary Care Physician Workload Assessment Using {EHR} Event Log Data and Time-Motion Observations},
  journal   = {Annals of Family Medicine},
  volume    = {15},
  number    = {5},
  pages     = {419--426},
  year      = {2017},
  doi       = {10.1370/afm.2121},
  langid    = {english}
}
```

**Reemplazo de Sinsky (25/09/2026).** `sinsky2016allocation` resultó cerrada y solo aportaba un dato de
contexto en §1.1. La reemplaza `arndt2017tethered` (*Annals of Family Medicine*, acceso abierto), que mide
lo mismo en atención primaria con registros de uso de la historia clínica electrónica validados por
observación directa: 5.9 horas de una jornada de 11.4, 1.4 fuera de horario, 44.2 % en tareas
administrativas y de registro. La entrada vieja queda en el `.bib` sin citar.

**Reemplazos por fuentes abiertas (25/09/2026).** `dinnes2018dermoscopy` (revisión Cochrane, libre en
PMC 6517096) reemplaza a `kittler2002diagnostic` y `vestergaard2008dermoscopy`, que eran cerradas. Dinnes
no afirma que sin entrenamiento la dermatoscopía no aporte ventaja, como decía Kittler: concluye que la
mejora se da sobre todo en usuarios experimentados y que faltan datos en atención primaria. La
introducción (§1.1) se reescribió con esa formulación. En §2.7 se le suma `kittler2016standardization`
para las estructuras que muestra la dermatoscopía. `demsar2006statistical` (JMLR, abierta) se usará junto
a `wilcoxon1945individual` en §2.6.4 para justificar Wilcoxon en la comparación de clasificadores.
Las dos entradas viejas quedan en el `.bib` sin citar; retirarlas es decisión del autor, igual que
`atkinsonabutridy2025language` y `nvidia2023beginners`, que tampoco se citan.

`goodfellow2016deep`, `srivastava2014dropout` y `hochreiter1997long` son anteriores a 2020: entran por
la condición 1 de la guía (fundacionales, definen el concepto). `rumelhart1986learning` ya estaba en el
`.bib` con el mismo encuadre.

**Por qué falta esta.** §2.1.3 ¶1 enunciaba las cuatro partes del informe citando
`kittler2016standardization`, pero ese trabajo es el consenso de la ISD sobre **terminología
dermatoscópica** y no dice nada sobre el formato del informe. Ninguna entrada del `.bib` lo cubre.
El párrafo se reescribió para enunciar solo las dos partes de las que el trabajo se ocupa
—descripción e impresión diagnóstica—, que sí se sostienen con `shen2025skincare`, y para dejar el
diferencial y la recomendación como lo que queda fuera del alcance. Si aparece una fuente clínica
adecuada, se puede recuperar la enumeración completa; mientras tanto el párrafo no afirma nada que
no tenga respaldo.

**`kittler2016standardization` se sigue usando, con su alcance real.** Queda en §2.1.3 ¶2, que es
la afirmación que sí sostiene: el vocabulario dermatoscópico estandarizado por consenso.

**Falta una referencia de LSTM.** §2.3.1 ¶1 mencionaba las redes de memoria a corto y largo plazo
citando `elman1990finding`, que es de 1990 y describe la red recurrente simple. Hochreiter y
Schmidhuber 1997 no está en el `.bib`. Como la ficha del Capítulo 2 ya había decidido dejar LSTM en
una mención mínima, **se eliminó la cláusula** en lugar de proponer la referencia. Si el marco
teórico llegara a necesitar LSTM con desarrollo, hay que incorporarla primero.

### Estado del arte de §2.10 — incorporado el 29/09/2026

Surgen de la revisión del tutor, que pidió ampliar el estado del arte con trabajos de 2020 a 2026. Cada
trabajo se leyó completo y se verificó contra el PDF. Las fichas de lectura, con las cifras citables y
la página de cada una, quedan en `lecturas_estado_arte_eje{1,2,3}.md`, que es un documento temporal y no
se versiona. Ninguna clave choca con las del `.bib`.

| Clave | Referencia | Eje / sección | Reserva |
|---|---|---|---|
| `liu2020deep` | Liu et al., *Nature Medicine* 26(6):900–908, 2020 | Eje 1, clasificadores | — |
| `gessert2020skin` | Gessert et al., *MethodsX* 7:100864, 2020 | Eje 1 | Es el método ganador de ISIC 2019; no hay artículo arbitrado principal |
| `yao2022single` | Yao et al., *IEEE TMI* 41(5):1242–1254, 2022 | Eje 1 | Desbalance con modelo único |
| `marchetti2023prospective` | Marchetti et al., *npj Digital Medicine* 6:127, 2023 (PROVE-AI) | Eje 1 | — |
| `yan2023towards` | Yan et al., CVPR 2023, pp. 11568–11577 | Sesgo y generalización, no eje 1 | Trata de artefactos y robustez |
| `yan2026dermfmzero` | Yan et al., arXiv 2602.10624, 2026 (DermFM-Zero) | Eje 2, VLM | Preimpresión; mismo grupo que Derm1M |
| `shen2025skingptr1` | Shen et al., arXiv 2511.15242, 2025 (SkinGPT-R1) | Eje 2 | Preimpresión; el 82.5 % es solo Derm12345 |
| `ru2026dermogpt` | Ru et al., arXiv 2601.01868, 2026 (DermoGPT) | Eje 2 | Preimpresión; evaluación con expertos acotada |
| `jiang2026multimodal` | Jiang et al., arXiv 2605.04098, 2026 | Eje 2 | Preimpresión; grupo independiente del de Monash |
| `shen2025dermbench` | Shen et al., arXiv 2511.09195, 2025 (DermBench) | Eje 3, reportes | Póster en ECCV 2026; pasar a `@inproceedings` cuando salgan las actas |
| `xia2025mmedrag` | Xia et al., ICLR 2025 (MMed-RAG) | Eje 3, RAG | Citar junto con RULE |
| `xia2024rule` | Xia et al., EMNLP 2024, pp. 1081–1093 (RULE) | Eje 3, RAG | Citar junto con MMed-RAG |
| `hartsock2024vision` | Hartsock y Rasool, *Frontiers in AI* 7:1430984, 2024 | Marco teórico, §2.6 | Revisión, no estado del arte |

**Verificaciones hechas el 29/09/2026.**

- Todos los DOI resuelven. La URL de `yao2022single` que se había deducido del DOI estaba mal: el DOI
  redirige al documento 9656127 de IEEE Xplore, no al 9663087. Ya está corregida abajo.
- La URL de `gessert2020skin` coincide con la redirección del DOI.
- En `yan2023towards`, Crossref y el PDF dan «Peter Soyer», y así queda. En `yan2026dermfmzero`
  figura «H. Peter Soyer» porque así lo lista arXiv. Es la misma persona; la bibliografía imprime
  solo el primer autor, así que la diferencia no se ve.
- Las cuatro preimpresiones de arXiv siguen la convención de `liu2025skinr1`, con `@misc`,
  `eprint = {id [cs]}` y `eprinttype = {arxiv}`. DermBench también, en lugar del `@online` que
  proponía la ficha.
- MedCLIP (`wang2022medclip`) quedó afuera: trata solo radiografía de tórax.

```bibtex
@article{liu2020deep,
  author = {Liu, Yuan and Jain, Ayush and Eng, Clara and Way, David H. and Lee, Kang and Bui, Peggy and Kanada, Kimberly and de Oliveira Marinho, Guilherme and Gallegos, Jessica and Gabriele, Sara and Gupta, Vishakha and Singh, Nalini and Natarajan, Vivek and Hofmann-Wellenhof, Rainer and Corrado, Greg S. and Peng, Lily H. and Webster, Dale R. and Ai, Dennis and Huang, Susan and Liu, Yun and Dunn, R. Carter and Coz, David},
  title = {A deep learning system for differential diagnosis of skin diseases},
  date = {2020-06},
  journaltitle = {Nature Medicine},
  volume = {26},
  number = {6},
  pages = {900--908},
  doi = {10.1038/s41591-020-0842-3},
  url = {https://www.nature.com/articles/s41591-020-0842-3},
  langid = {english},
}

@article{gessert2020skin,
  author = {Gessert, Nils and Nielsen, Maximilian and Shaikh, Mohsin and Werner, Ren{\'e} and Schlaefer, Alexander},
  title = {Skin lesion classification using ensembles of multi-resolution {EfficientNets} with meta data},
  date = {2020},
  journaltitle = {MethodsX},
  volume = {7},
  pages = {100864},
  doi = {10.1016/j.mex.2020.100864},
  url = {https://linkinghub.elsevier.com/retrieve/pii/S2215016120300832},
  langid = {english},
}

@article{yao2022single,
  author = {Yao, Peng and Shen, Shuwei and Xu, Mengjuan and Liu, Peng and Zhang, Fan and Xing, Jinyu and Shao, Pengfei and Kaffenberger, Benjamin and Xu, Ronald X.},
  title = {Single Model Deep Learning on Imbalanced Small Datasets for Skin Lesion Classification},
  date = {2022-05},
  journaltitle = {{IEEE} Transactions on Medical Imaging},
  volume = {41},
  number = {5},
  pages = {1242--1254},
  doi = {10.1109/TMI.2021.3136682},
  url = {https://ieeexplore.ieee.org/document/9656127},
  langid = {english},
}

@article{marchetti2023prospective,
  author = {Marchetti, Michael A. and Cowen, Emily A. and Kurtansky, Nicholas R. and Weber, Jochen and Dauscher, Megan and DeFazio, Jennifer and Deng, Liang and Dusza, Stephen W. and Haliasos, Helen and Halpern, Allan C. and Hosein, Sharif and Nazir, Zaeem H. and Marghoob, Ashfaq A. and Quigley, Elizabeth A. and Salvador, Trina and Rotemberg, Veronica M.},
  title = {Prospective validation of dermoscopy-based open-source artificial intelligence for melanoma diagnosis ({PROVE-AI} study)},
  date = {2023-07-12},
  journaltitle = {npj Digital Medicine},
  volume = {6},
  number = {1},
  pages = {127},
  doi = {10.1038/s41746-023-00872-1},
  url = {https://www.nature.com/articles/s41746-023-00872-1},
  langid = {english},
}

@inproceedings{yan2023towards,
  author = {Yan, Siyuan and Yu, Zhen and Zhang, Xuelin and Mahapatra, Dwarikanath and Chandra, Shekhar S. and Janda, Monika and Soyer, Peter and Ge, Zongyuan},
  title = {Towards Trustable Skin Cancer Diagnosis via Rewriting Model's Decision},
  date = {2023-06},
  booktitle = {Proceedings of the {IEEE}/{CVF} Conference on Computer Vision and Pattern Recognition ({CVPR})},
  pages = {11568--11577},
  doi = {10.1109/CVPR52729.2023.01113},
  url = {https://openaccess.thecvf.com/content/CVPR2023/papers/Yan_Towards_Trustable_Skin_Cancer_Diagnosis_via_Rewriting_Models_Decision_CVPR_2023_paper.pdf},
  langid = {english},
}

@misc{yan2026dermfmzero,
  author = {Yan, Siyuan and Li, Xieji and Mo, Dan and Tschandl, Philipp and Jiang, Yiwen and Wang, Zhonghua and Hu, Ming and Ju, Lie and Vico-Alonso, Cristina and Zheng, Yizhen and Liu, Jiahe and Zhou, Juexiao and Chello, Camilla and Cheung, Jen G. and Anriot, Julien and Thomas, Luc and Primiero, Clare and Tan, Gin and Ng, Aik Beng and See, Simon and Tang, Xiaoying and Ip, Albert and Liao, Xiaoyang and Bowling, Adrian and Haskett, Martin and Zhao, Shuang and Janda, Monika and Soyer, H. Peter and Mar, Victoria and Kittler, Harald and Ge, Zongyuan},
  title = {A Vision-Language Foundation Model for Zero-shot Clinical Collaboration and Automated Concept Discovery in Dermatology},
  shorttitle = {{DermFM-Zero}},
  date = {2026-02-11},
  doi = {10.48550/arXiv.2602.10624},
  url = {http://arxiv.org/abs/2602.10624},
  eprint = {2602.10624 [cs]},
  eprinttype = {arxiv},
  langid = {english},
}

@misc{shen2025skingptr1,
  author = {Shen, Yuhao and Chen, Zhangtianyi and He, Yuanhao and Xu, Yan and Zhang, Shuping and Sun, Liyuan and Wang, Zijian and Zhu, Yinghao and Yang, Yuyuan and Qian, Jiahe and Wang, Ziwen and Zhang, Xinyuan and Liu, Wenbin and Ge, Zongyuan and Lu, Tao and Yan, Siyuan and Zhou, Juexiao},
  title = {Trustworthy and Fair {SkinGPT-R1} for Democratizing Dermatological Reasoning across Diverse Ethnicities},
  shorttitle = {{SkinGPT-R1}},
  date = {2025-11-19},
  doi = {10.48550/arXiv.2511.15242},
  url = {http://arxiv.org/abs/2511.15242},
  eprint = {2511.15242 [cs]},
  eprinttype = {arxiv},
  note = {Versión 2 del 18 de febrero de 2026. La versión 1 se tituló «SkinGPT-R1: Adapter-Only Dual Distillation for Efficient Dermatology Reasoning».},
  langid = {english},
}

@misc{ru2026dermogpt,
  author = {Ru, Jinghan and Yan, Siyuan and Yin, Yuguo and Zou, Yuexian and Ge, Zongyuan},
  title = {{DermoGPT}: Open Weights and Open Data for Morphology-Grounded Dermatological Reasoning {MLLMs}},
  shorttitle = {{DermoGPT}},
  date = {2026-01-05},
  doi = {10.48550/arXiv.2601.01868},
  url = {http://arxiv.org/abs/2601.01868},
  eprint = {2601.01868 [cs]},
  eprinttype = {arxiv},
  langid = {english},
}

@misc{jiang2026multimodal,
  author = {Jiang, Roy and Kim, Hyunjae and Qin, Zhenyue and Lee, Morten and MacGibeny, Margaret and Hanly, Ailish and Sadlowski, Angela and Chowdhury, Shanin and Ai, Xuguang and Gehlhausen, Jeffrey and Chen, Qingyu},
  title = {Are Multimodal {LLMs} Ready for Clinical Dermatology? A Real-World Evaluation in Dermatology},
  shorttitle = {Are Multimodal {LLMs} Ready for Clinical Dermatology?},
  date = {2026-05-01},
  doi = {10.48550/arXiv.2605.04098},
  url = {http://arxiv.org/abs/2605.04098},
  eprint = {2605.04098 [cs]},
  eprinttype = {arxiv},
  langid = {english},
}

@misc{shen2025dermbench,
  author = {Shen, Yuhao and Qian, Jiahe and Zhang, Shuping and Chen, Zhangtianyi and Lu, Tao and Zhou, Juexiao},
  title = {Towards Trustworthy Dermatology {MLLMs}: A Benchmark and Multimodal Evaluator for Diagnostic Narratives},
  shorttitle = {{DermBench}},
  date = {2025-11-12},
  doi = {10.48550/arXiv.2511.09195},
  url = {http://arxiv.org/abs/2511.09195},
  eprint = {2511.09195 [cs]},
  eprinttype = {arxiv},
  note = {Versión 2 del 12 de enero de 2026. Póster en ECCV 2026.},
  langid = {english},
}

@inproceedings{xia2025mmedrag,
  author = {Xia, Peng and Zhu, Kangyu and Li, Haoran and Wang, Tianze and Shi, Weijia and Wang, Sheng and Zhang, Linjun and Zou, James and Yao, Huaxiu},
  title = {{MMed-RAG}: Versatile Multimodal {RAG} System for Medical Vision Language Models},
  booktitle = {International Conference on Learning Representations ({ICLR})},
  date = {2025},
  doi = {10.48550/arXiv.2410.13085},
  url = {http://arxiv.org/abs/2410.13085},
  eprint = {2410.13085 [cs]},
  eprinttype = {arxiv},
  langid = {english},
}

@inproceedings{xia2024rule,
  author = {Xia, Peng and Zhu, Kangyu and Li, Haoran and Zhu, Hongtu and Li, Yun and Li, Gang and Zhang, Linjun and Yao, Huaxiu},
  title = {{RULE}: Reliable Multimodal {RAG} for Factuality in Medical Vision Language Models},
  booktitle = {Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing},
  date = {2024-11},
  pages = {1081--1093},
  publisher = {Association for Computational Linguistics},
  doi = {10.18653/v1/2024.emnlp-main.62},
  url = {https://aclanthology.org/2024.emnlp-main.62/},
  langid = {english},
}

@article{hartsock2024vision,
  author = {Hartsock, Iryna and Rasool, Ghulam},
  title = {Vision-language models for medical report generation and visual question answering: a review},
  date = {2024-11-19},
  journaltitle = {Frontiers in Artificial Intelligence},
  volume = {7},
  pages = {1430984},
  doi = {10.3389/frai.2024.1430984},
  url = {https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2024.1430984/full},
  langid = {english},
}
```

## 2. Consolidación del 17/09/2026

El `.bib` se armó fusionando cuatro archivos dispersos: `estado_del_arte/referencias.bib` (37),
`marco_teorico/referencias.bib` (33), `tabla_resultados_sota/referencias_sota.bib` (14) y la
versión previa de `Bibliography.bib` (16). De 100 entradas en bruto quedaron **72 únicas**: 28 eran
duplicados del mismo trabajo con tres convenciones de clave distintas. Se conservó siempre la
entrada con más campos bibliográficos. Con las ocho referencias de la sección 1, el archivo llegó a
80 entradas, y con las dos de epidemiología con cifras, a **82 entradas**.

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
`atkinsonabutridy2025language`. Las diez de la sección 1 tampoco están, porque se agregaron
directamente al `.bib`: en total son 15 referencias que solo existen en el documento.

**Conviene recuperar de la papelera las 36 entradas antes de vaciarla**, porque son referencias que
el documento usa y ahí están sus PDF y sus metadatos. Mientras esa diferencia exista, una
exportación de Zotero sobre `Bibliography.bib` borraría 77 de las 108 referencias: las 36 de la
papelera, las 15 que solo existen en el documento y las 26 de la tanda del 22/09/2026, que tampoco
están en Zotero.

## 6. Auditoría por año

**Recuento vigente (22/09/2026): de las 108 entradas del `.bib`, 68 están dentro de la ventana
2020–2026 y 40 son anteriores.** La tanda del 22/09 sumó 26 entradas, de las cuales 17 son
anteriores a 2020 —casi todas definiciones de métricas y de pruebas estadísticas, que son
fundacionales por naturaleza—, y por eso la proporción se movió tanto.

El recuento anterior (17/09/2026) era de 82 entradas, 59 dentro de la ventana y 23 anteriores. La
tabla que sigue es de esa fecha y **no incluye las 17 anteriores a 2020 que entraron después**:
`wilcoxon1945individual`, `mcnemar1947note`, `brier1950verification`, `efron1979bootstrap`,
`argenziano1998checklist`, `lecun1998gradient`, `kittler2002diagnostic`, `banerjee2005meteor`,
`fawcett2006introduction`, `mendonca2013ph2`, `russakovsky2015imagenet`, `vedantam2015cider`,
`carrera2016validity`, `kittler2016standardization`, `guo2017calibration`, `lin2017focal`,
`selvaraju2017gradcam`. Todas entran por la excepción 1 —definen una métrica, una prueba, una
arquitectura o un criterio clínico— y ninguna se usa para sostener una afirmación sobre el
desempeño alcanzable hoy. **Falta completar la tabla con ellas.**

Las 23 originales cumplen alguna de las excepciones, así que ninguna se descarta, pero conviene
tener escrito por qué está cada una: la razón determina *cómo* se la cita.

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

## 6. PDFs en `Papers/` y referencias por conseguir (relevamiento del 25/09/2026)

Cruce de las 108 entradas del `.bib` y las cinco propuestas (cuatro de fundamentos y WILDS) contra los
77 PDFs de `Papers/`. El acceso se consultó en OpenAlex y se corrigió a mano donde OpenAlex marca
«cerrado» un trabajo que tiene versión abierta en arXiv o en el Open Access de CVF. ★ = ya se cita en el
documento.

**Ya en `Papers/`: 69 de las 108 entradas del `.bib`.** Todas las de `Fundacionales/` y `derma/` tienen su entrada, salvo los
PDFs que no están en el `.bib` (ver al final). `yan2025vision` (PanDerm) está como preprint («A
General-Purpose Multimodal Foundation Model for Dermatology»); conviene bajar la versión publicada en
*Nature Medicine*.

### Por conseguir, con acceso libre (34)

| Clave | Dónde |
|---|---|
| ★ `esteva2017dermatologistlevel` | PMC 8382232 (versión del autor) |
| ★ `freeman2026global` | JAMA Dermatology, acceso abierto |
| ★ `liu2021swin` | arXiv 2103.14030 / CVF Open Access |
| ★ `loria2020cutaneous` | ecancer.org (gold) |
| ~~`sinsky2016allocation`~~ | Era cerrada (la verificación del 17/09 fue errónea); **reemplazada** por `arndt2017tethered`, libre en PMC 5593724 |
| ★ `sung2026global` | *CA: A Cancer Journal for Clinicians*, gratuita (OpenAlex aún no la indexa) |
| ★ `tschandl2019comparison` | PMC 8237239 (versión del autor) |
| ★ `carrera2016validity` | JAMA Dermatology, lectura libre |
| ★ `holtzman2020curious` | arXiv 1904.09751 |
| ★ `kittler2016standardization` | PMC 5551974 |
| ★ `lecun1998gradient` | HAL hal-03926082 |
| ★ `lin2017focal` | arXiv 1708.02002 / CVF Open Access |
| ★ `liu2022convnet` | arXiv 2201.03545 / CVF Open Access |
| ★ `ren2020balanced` | arXiv 2007.10740 |
| ★ `russakovsky2015imagenet` | arXiv 1409.0575 |
| ★ `goodfellow2016deep` | deeplearningbook.org (lectura en línea, sin PDF) |
| ★ `kingma2015adam` | arXiv 1412.6980 |
| ★ `srivastava2014dropout` | JMLR, siempre abierta |
| ★ `nci2026melanoma` | página web de SEER |
| `bray2024global` | Wiley, gold (no se cita; reemplazada por `sung2026global`) |
| `abdin2024phi3` | arXiv 2404.14219 |
| `banerjee2005meteor` | ACL Anthology W05-0909 |
| `chen2020generating` | ACL Anthology |
| `codella2019skin` | arXiv 1902.03368 |
| `efron1979bootstrap` | Project Euclid, lectura libre |
| `gu2024medvh` | arXiv 2407.02730 |
| `guo2017calibration` | arXiv 1706.04599 |
| `jing2018automatic` | ACL Anthology |
| `khandelwal2020generalization` | arXiv 1911.00172 |
| `selvaraju2017gradcam` | arXiv 1610.02391 / CVF Open Access |
| `sun2025factaware` | ACL Anthology |
| `vedantam2015cider` | arXiv 1411.5726 / CVF Open Access |
| `zhang2020bertscore` | arXiv 1904.09675 |
| `koh2021wilds` (propuesta) | arXiv 2012.07421 |

### Por conseguir, sin acceso libre (10)

| Clave | Editorial | Cómo conseguirla |
|---|---|---|
| ~~`kittler2002diagnostic`~~ | *Lancet Oncology* (Elsevier) | **reemplazada** por `dinnes2018dermoscopy` (25/09) |
| ~~`vestergaard2008dermoscopy`~~ | *British Journal of Dermatology* (Wiley / OUP) | **reemplazada** por `dinnes2018dermoscopy` (25/09) |
| ★ `argenziano1998checklist` | *Archives of Dermatology* (JAMA Network) | biblioteca UNCuyo |
| ★ `hochreiter1997long` | *Neural Computation* (MIT Press) | copia del autor en el sitio del JKU Linz, o biblioteca |
| `brier1950verification` | *Monthly Weather Review* (AMS) | revisar journals.ametsoc.org: el archivo antiguo de la AMS suele estar libre |
| `mcnemar1947note` | *Psychometrika* (Springer) | biblioteca |
| `wilcoxon1945individual` | *Biometrics Bulletin* (JSTOR) | JSTOR institucional |
| `mendonca2013ph2` | IEEE EMBC | IEEE Xplore institucional |
| `atkinsonabutridy2025language` | libro, CRC Press | compra o biblioteca (no se cita) |
| `nvidia2023beginners` | *ebook* de NVIDIA, con registro | no se cita; decisión 6 de la ficha del Cap. 2 |

Las tres estadísticas clásicas (McNemar, Wilcoxon, Brier) son fundacionales y se citan por la definición;
no hace falta leerlas enteras, pero conviene tener el PDF para verificar la notación.

### PDFs en `Papers/` sin entrada en el `.bib`

- *Chain-of-Visual-Thought: Teaching VLMs to See and Think Better with Continuous Visual Tokens*
- *Multimodal Foundation Models: From Specialists to General-Purpose Assistants*
- *Vision-Language Models for Vision Tasks: A Survey*
- *Deep Learning Algorithms in the Diagnosis of Basal Cell Carcinoma Using Dermatoscopy* (Liu et al.
  2025, citado en el plan de trabajo)
- *Vision-language models for medical report generation and visual question answering: a review*
  (Hartsock y Rasool 2024, citado en el plan de trabajo)
- *Quilt-1M: One Million Image-Text Pairs for Histopathology*

Las dos del plan son candidatas naturales para el estado del arte (§2.8); las otras cuatro, solo si una
sección las necesita.

**Limpieza del `.bib` (25/09/2026).** Se eliminaron las entradas sin citar `mendonca2013ph2`,
`sinsky2016allocation`, `kittler2002diagnostic`, `vestergaard2008dermoscopy`,
`atkinsonabutridy2025language` y `nvidia2023beginners` (autor). Las menciones anteriores a esas claves
en este archivo quedan como registro histórico.
