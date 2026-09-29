# Candidatos para ampliar el estado del arte (S3a)

Lista de trabajos **candidatos**; el autor decide cuáles entran. No se tocó ningún `.tex` ni el `.bib`.
Todos son de 2020–2026, no están en `Bibliography.bib` ni en `refs_pendientes.md` (revisado por título), y
cada uno se verificó con búsqueda web y, cuando fue posible, con la página del arXiv o del editor
(consulta del 2026-09-28). La marca **[no verificado]** señala un dato que no pude confirmar.

Nota de descarte: `arXiv:2405.18004` (SkinCAP) hoy es el mismo trabajo que `SkinCaRe`, que ya está en el `.bib`,
así que no se propone.

---

## Eje 1. Clasificación / diagnóstico automático de lesiones de piel con deep learning

### 1.1 A deep learning system for differential diagnosis of skin diseases
- **Autores:** Liu, Y. et al. (Google Health) — **Año:** 2020 — **Venue:** *Nature Medicine* 26:900–908 (preprint arXiv:1909.05382).
- **PDF:** https://arxiv.org/pdf/1909.05382 — **Acceso:** preprint abierto (arXiv).
- **Qué hace:** sistema de aprendizaje profundo que da un diagnóstico diferencial de 26 condiciones (~80 % del volumen en atención primaria) a partir de fotos y antecedentes; 14 021 casos de desarrollo y 3 756 de validación (partición temporal) de una práctica de teledermatología. Compara top-1/top-3 con dermatólogos, médicos de cabecera y enfermeros (top-1 0.67 frente a 0.45 y 0.41 de los generalistas). Evaluación con expertos: sí (comparación con clínicos).
- **Relevancia:** clasificador de referencia con salida top-k y comparación clínica en imágenes clínicas, contrapunto de HAM10000 (dermatoscópico, 7 clases).

### 1.2 Skin lesion classification using ensembles of multi-resolution EfficientNets with meta data
- **Autores:** Gessert, N. et al. — **Año:** 2020 — **Venue:** *MethodsX* 7:100864 (arXiv:1910.03910).
- **PDF:** https://arxiv.org/pdf/1910.03910 — **Acceso:** arXiv abierto.
- **Qué hace:** ensamble de EfficientNets a distintas resoluciones con rama de metadatos, ganador de las dos tareas del desafío ISIC 2019 (8 clases, ~25 000 imágenes); trata el desbalance con ponderación de la pérdida y la clase desconocida con un enfoque basado en datos. Métrica del desafío: exactitud balanceada. Sin expertos.
- **Relevancia:** respalda los ensambles y el manejo explícito del desbalance como estrategia de referencia en la clasificación multiclase.

### 1.3 Single Model Deep Learning on Imbalanced Small Datasets for Skin Lesion Classification
- **Autores:** Yao, P. et al. — **Año:** 2021 (publicado 2022) — **Venue:** *IEEE Transactions on Medical Imaging* 41(5):1242–1254.
- **PDF:** https://arxiv.org/pdf/2102.01284 — **Acceso:** arXiv abierto.
- **Qué hace:** propone un modelo único (sin ensamble) para conjuntos chicos y desbalanceados: regularización DropOut/DropBlock, RandAugment modificado y rebalanceo; concluye que modelos de complejidad moderada superan a los grandes. Sin expertos. (Datasets y métricas exactos: [no verificado] más allá del resumen.)
- **Relevancia:** conecta con la selección por F1 macro, con que un modelo más grande no siempre gana en HAM10000 y con el hardware de consumo.

### 1.4 Prospective validation of dermoscopy-based open-source artificial intelligence for melanoma diagnosis (PROVE-AI)
- **Autores:** Marchetti, M. A. et al. — **Año:** 2023 — **Venue:** *npj Digital Medicine*.
- **PDF:** https://www.nature.com/articles/s41746-023-00872-1.pdf (también https://pmc.ncbi.nlm.nih.gov/articles/PMC10338483/) — **Acceso:** abierto, CC BY 4.0 (verificado en PMC).
- **Qué hace:** estudio prospectivo con 435 participantes y 603 lesiones (95 melanomas) del algoritmo de código abierto ADAE, entrenado con imágenes públicas. Al umbral de 95 % de sensibilidad: sensibilidad 96.8 %, especificidad 37.4 %; el AUC de los dermatólogos sube de 0.780 a 0.816 con la IA. Con expertos: sí.
- **Relevancia:** ilustra el hueco entre validación retrospectiva y prospectiva y justifica el foco en la sensibilidad de melanoma y en la validación externa.

### 1.5 Dermatologist-like explainable AI enhances trust and confidence in diagnosing melanoma
- **Autores:** Chanda, T. et al. — **Año:** 2024 — **Venue:** *Nature Communications* 15:524.
- **PDF:** https://opus.bibliothek.uni-augsburg.de/opus4/files/114369/s41467-023-43095-4.pdf (versión editorial: https://www.nature.com/articles/s41467-023-43095-4) — **Acceso:** abierto (PDF en repositorio institucional; licencia CC BY [no verificado]).
- **Qué hace:** IA explicable que da explicaciones específicas del dominio junto con el diagnóstico diferencial melanoma/nevo; estudio de tres fases con dermatólogos que mide exactitud, confianza y confianza en el sistema. Con explicaciones aumentan la confianza y la coincidencia con las explicaciones de los expertos. Con expertos: sí. (Número exacto de lectores: [no verificado].)
- **Relevancia:** respalda que un reporte con hallazgos dermatoscópicos (no solo la etiqueta) mejora la aceptación clínica, la motivación del generador de reportes.

### 1.6 On Interpretability of Deep Learning based Skin Lesion Classifiers using Concept Activation Vectors
- **Autores:** Lucieri, A. et al. — **Año:** 2020 — **Venue:** IJCNN 2020 (arXiv:2005.02000).
- **PDF:** https://arxiv.org/pdf/2005.02000 — **Acceso:** arXiv abierto.
- **Qué hace:** aplica TCAV para verificar si un clasificador de tres tumores cutáneos codifica conceptos que usan los dermatólogos; datos PH2 y derm7pt; concluye que el clasificador aprende conceptos comprensibles. Sin evaluación con expertos.
- **Relevancia:** enlaza clasificación con conceptos dermatoscópicos y con la lista de 7 puntos del marco teórico.

### 1.7 TFormer: A throughout fusion transformer for multi-modal skin lesion diagnosis
- **Autores:** Zhang, Y. et al. — **Año:** 2022 (arXiv; revisión 2023) — **Venue:** arXiv:2211.11393; su versión en revista no la verifiqué **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2211.11393 — **Acceso:** arXiv abierto.
- **Qué hace:** transformer puro con fusión por etapas de imágenes dermatoscópicas y clínicas y datos no visuales (metadatos). Datasets y métricas: [no verificado].
- **Relevancia:** representante de la línea transformer/multimodal frente a las CNN en lesiones cutáneas. Es el candidato más débil del eje; conviene reemplazarlo si se encuentra un ViT/Swin con venue revisado.

### 1.8 (Condicional) Validation of AI prediction models for skin cancer diagnosis using dermoscopy images: the 2019 ISIC Grand Challenge
- **Autores:** Combalia, M. et al. — **Año:** 2022 — **Venue:** *The Lancet Digital Health* 4(5):e330–e339.
- **PDF:** https://www.thelancet.com/journals/landig/article/PIIS2589-7500(22)00021-8/fulltext — **Acceso:** **[no verificado]**; la página devolvió 403 y no encontré versión en PMC ni arXiv. Confirmar la licencia antes de incluirlo.
- **Qué hace:** desafío con 25 331 imágenes de entrenamiento (HAM10000 y BCN20000, 8 clases) y prueba con datos de Turquía, Nueva Zelanda, Suecia y Argentina; ranking por exactitud multiclase balanceada.
- **Relevancia:** validación externa multi-país que incluye Argentina; ilustra el gap de generalización.

---

## Eje 2. Modelos visión–lenguaje en dermatología

### 2.1 A Vision-Language Foundation Model for Zero-shot Clinical Collaboration and Automated Concept Discovery in Dermatology (DermFM-Zero)
- **Autores:** Yan, S. et al. — **Año:** 2026 — **Venue:** arXiv:2602.10624 (preprint, sin venue).
- **PDF:** https://arxiv.org/pdf/2602.10624 — **Acceso:** arXiv abierto.
- **Qué hace:** modelo dermatológico entrenado con >4 millones de datos multimodales (modelado latente enmascarado + contrastivo); 20 benchmarks de diagnóstico zero-shot y recuperación; autoencoders esparsos para descubrir conceptos y suprimir artefactos. Estudio de lectores con más de 1 100 clínicos: los generalistas con IA casi duplican la exactitud en 98 condiciones.
- **Relevancia:** sucesor de DermLIP/PanDerm y evidencia de zero-shot con validación clínica; base para la discusión del clasificador visión–lenguaje.

### 2.2 DermoGPT: Open Weights and Open Data for Morphology-Grounded Dermatological Reasoning MLLMs
- **Autores:** Ru, J. et al. — **Año:** 2026 — **Venue:** arXiv:2601.01868 (preprint).
- **PDF:** https://arxiv.org/pdf/2601.01868 — **Acceso:** arXiv abierto.
- **Qué hace:** DermoInstruct (211 243 imágenes, 772 675 trayectorias de razonamiento), DermoBench (11 tareas: morfología, diagnóstico, razonamiento, equidad; 3 600 casos abiertos verificados por expertos) y un MLLM entrenado con SFT y aprendizaje por refuerzo (MAVIC) que mejora sobre 16 baselines. Con expertos: sí (casos verificados y referencia humana).
- **Relevancia:** morfología → diagnóstico en un VLM generativo, análogo a la cascada clasificador→generador.

### 2.3 Trustworthy and Fair SkinGPT-R1 for Democratizing Dermatological Reasoning across Diverse Ethnicities
- **Autores:** Shen, Y. et al. — **Año:** 2025 (rev. 2026) — **Venue:** arXiv:2511.15242 (preprint).
- **PDF:** https://arxiv.org/pdf/2511.15242 — **Acceso:** arXiv abierto.
- **Qué hace:** MLLM con adaptación eficiente en parámetros sobre un backbone congelado, razonamiento en cadena y mezcla de expertos consciente de la equidad; genera reportes estructurados (hallazgos, diferencial, diagnóstico). 82.50 % en clasificación de 40 clases sobre 7 datasets externos; evaluación ciega de 5 dermatólogos sobre 1 000 casos (media 3.6/5). Distinto de `Skin-R1`, ya citado.
- **Relevancia:** competidor directo del generador con adaptación ligera, con evaluación por expertos y equidad. También aplica al eje 3.

### 2.4 Are Multimodal LLMs Ready for Clinical Dermatology? A Real-World Evaluation in Dermatology
- **Autores:** Jiang, R. et al. — **Año:** 2026 — **Venue:** arXiv:2605.04098 (preprint).
- **PDF:** https://arxiv.org/pdf/2605.04098 — **Acceso:** arXiv abierto.
- **Qué hace:** evalúa cuatro MLLM abiertos (InternVL-Chat, LLaVA-Med, SkinGPT-4, MedGemma-4B) y GPT-4.1 en tres datasets públicos y una cohorte hospitalaria de 5 811 casos y 46 405 imágenes; diagnóstico diferencial y triaje. Top-3 en público: 26.55 % (mejor abierto) y 42.25 % (GPT-4.1); en el mundo real: 1.50–13.35 % y 24.65 %.
- **Relevancia:** cuantifica el colapso de los VLM generales en dermatología y el salto benchmark→clínica, alineado con el hallazgo de la tesina.

### 2.5 BiomedCLIP: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs
- **Autores:** Zhang, S. et al. — **Año:** 2023 (v3 2025) — **Venue:** arXiv:2303.00915; versión en *NEJM AI* 2025 **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2303.00915 — **Acceso:** arXiv abierto.
- **Qué hace:** CLIP biomédico general entrenado en PMC-15M (15 millones de pares imagen–texto de 4.4 millones de artículos); recuperación, clasificación y VQA. Sin expertos.
- **Relevancia:** referencia de VL biomédico general frente a los dermatológicos (DermLIP, MONET); sostiene la comparación general vs. especializado.

### 2.6 MedGemma Technical Report
- **Autores:** Sellergren, A. et al. (Google) — **Año:** 2025 (v2 2026) — **Venue:** arXiv:2507.05201.
- **PDF:** https://arxiv.org/pdf/2507.05201 — **Acceso:** arXiv abierto.
- **Qué hace:** modelos VL médicos sobre Gemma 3 (4B/27B) y el codificador MedSigLIP. Una búsqueda indica que incluye imágenes de dermatología (51 049 imágenes, 210 condiciones) y clasificación de piel; el resumen del arXiv que leí no menciona dermatología, así que ese detalle es **[no verificado]**.
- **Relevancia:** VLM médico abierto y pequeño, ajustable con LoRA en GPU de consumo; punto de comparación para SkinVL.

---

## Eje 3. Generación de reportes / descripciones dermatológicas

### 3.1 Towards Trustworthy Dermatology MLLMs: A Benchmark and Multimodal Evaluator for Diagnostic Narratives (DermBench / DermEval)
- **Autores:** Shen, Y. et al. — **Año:** 2025 (rev. 2026) — **Venue:** arXiv:2511.09195; aparece como póster de ECCV 2026 en el sitio de la conferencia **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2511.09195 — **Acceso:** arXiv abierto.
- **Qué hace:** DermBench (4 000 imágenes con narrativas certificadas por expertos, 4 500 casos de prueba) y DermEval, evaluador multimodal sin referencia que critica la narrativa contra la imagen y puntúa por dimensiones. Desvío medio frente a expertos de 0.251 (DermBench) y 0.117 (DermEval) en escala de 5. Con expertos: sí.
- **Relevancia:** ataca directamente el hueco de evaluar la fidelidad diagnóstica más allá de BLEU/ROUGE.

### 3.2 DermaVQA: A Multilingual Visual Question Answering Dataset for Dermatology
- **Autores:** Yim, W. et al. — **Año:** 2024 — **Venue:** MICCAI 2024.
- **PDF:** https://papers.miccai.org/miccai-2024/paper/2444_paper.pdf — **Acceso:** abierto (MICCAI Open Access).
- **Qué hace:** dataset de consultas de salud de consumidores con imágenes de pacientes, en inglés y chino; respuestas de dermatólogos certificados (subconjunto Reddit) y de médicos de una plataforma; evalúa GPT-4, Gemini-pro-vision y un LLaVA ajustado con métricas multi-referencia. Con expertos: sí (autoría de las respuestas).
- **Relevancia:** generación de texto clínico a partir de imágenes dermatológicas con referencias de médicos y métricas de evaluación.

### 3.3 DermaVQA-DAS: Dermatology Assessment Schema (DAS) & Datasets for Closed-Ended Question Answering & Segmentation
- **Autores:** Yim, W. et al. — **Año:** 2025 — **Venue:** arXiv:2512.24340 (preprint).
- **PDF:** https://arxiv.org/pdf/2512.24340 — **Acceso:** arXiv abierto.
- **Qué hace:** esquema experto de evaluación dermatológica (36 preguntas de alto nivel y 27 finas) con benchmark de QA cerrada y segmentación; exactitud de QA de 0.729 a 0.798 (o3: 0.798); Dice 0.566 en segmentación.
- **Relevancia:** ofrece una estructura de atributos clínicos para verificar el contenido de los reportes.

### 3.4 MMed-RAG: Versatile Multimodal RAG System for Medical Vision Language Models
- **Autores:** Xia, P. et al. — **Año:** 2025 — **Venue:** ICLR 2025 (arXiv:2410.13085).
- **PDF:** https://arxiv.org/pdf/2410.13085 — **Acceso:** arXiv e ICLR abiertos.
- **Qué hace:** RAG multimodal con recuperación consciente del dominio, selección adaptativa de contextos y ajuste por preferencias; 5 datasets (radiología, oftalmología, patología), VQA y generación de reportes; +43.8 % de exactitud fáctica. No incluye dermatología.
- **Relevancia:** respalda la recuperación de casos similares para reducir alucinaciones (cercano al RAG del pipeline).

### 3.5 RULE: Reliable Multimodal RAG for Factuality in Medical Vision Language Models
- **Autores:** Xia, P. et al. — **Año:** 2024 — **Venue:** EMNLP 2024 (main) (arXiv:2407.05131).
- **PDF:** https://arxiv.org/pdf/2407.05131 (también https://aclanthology.org/2024.emnlp-main.62.pdf) — **Acceso:** abierto.
- **Qué hace:** controla el riesgo de factualidad calibrando cuántos contextos recuperar y ajusta con preferencias para evitar la sobredependencia del contexto; VQA y reportes en tres datasets; +47.4 % de exactitud fáctica.
- **Relevancia:** conecta con la elección del número de vecinos k y con el ruteo por incertidumbre y abstención.

### 3.6 CARES: A Comprehensive Benchmark of Trustworthiness in Medical Vision Language Models
- **Autores:** Xia, P. et al. — **Año:** 2024 — **Venue:** NeurIPS 2024 Datasets and Benchmarks (arXiv:2406.06007).
- **PDF:** https://arxiv.org/pdf/2406.06007 — **Acceso:** arXiv abierto.
- **Qué hace:** ~41 000 pares pregunta–respuesta, 16 modalidades y 27 regiones anatómicas; evalúa fidelidad, equidad, seguridad, privacidad y robustez; halla imprecisiones fácticas y sesgos demográficos en los VLM médicos.
- **Relevancia:** marco para la sección de alucinaciones y confiabilidad de los VLM médicos.

### 3.7 GREEN: Generative Radiology Report Evaluation and Error Notation
- **Autores:** Ostmeier, S. et al. — **Año:** 2024 — **Venue:** Findings of EMNLP 2024 (arXiv:2405.03595).
- **PDF:** https://arxiv.org/pdf/2405.03595 — **Acceso:** arXiv abierto.
- **Qué hace:** métrica basada en un modelo de lenguaje que identifica y explica errores clínicamente significativos en reportes generados; validada contra conteos de errores de 6 expertos y preferencias de 2. Es de radiología, no de dermatología.
- **Relevancia:** modelo de evaluación de fidelidad clínica a imitar en reportes dermatológicos frente a métricas léxicas.

---

## Recomendación (~4 por eje)

**Eje 1**
1. Liu 2020 (1.1): diagnóstico diferencial validado contra clínicos en *Nature Medicine*.
2. Gessert 2020 (1.2): ensamble ganador de ISIC 2019 con tratamiento explícito del desbalance.
3. Yao 2021 (1.3): modelo único regularizado en datos chicos y desbalanceados, coherente con el hardware acotado.
4. PROVE-AI 2023 (1.4): validación prospectiva de melanoma con acceso abierto verificado.

Alternativas: Chanda 2024 (1.5) para reforzar la explicabilidad; Combalia 2022 (1.8) si se confirma el acceso.

**Eje 2**
1. DermFM-Zero (2.1): estado del arte zero-shot dermatológico con estudio de lectores.
2. SkinGPT-R1 (2.3): VLM generativo ligero con evaluación por dermatólogos y equidad.
3. Jiang 2026 (2.4): cuantifica el gap entre benchmark y práctica clínica de los VLM generales.
4. DermoGPT (2.2): razonamiento morfológico con benchmark verificado por expertos.

Alternativa: BiomedCLIP (2.5) como VL general de contraste.

**Eje 3**
1. DermBench/DermEval (3.1): evaluación de fidelidad diagnóstica de narrativas dermatológicas.
2. MMed-RAG (3.4): RAG multimodal médico contra alucinaciones, análogo al pipeline de recuperación.
3. RULE (3.5): selección calibrada de contextos recuperados, ligada al ruteo por incertidumbre.
4. DermaVQA (3.2): texto clínico con respuestas de dermatólogos, MICCAI con acceso abierto.

Alternativas: GREEN (3.7) o CARES (3.6) para ampliar evaluación y confiabilidad.

## Descartados por acceso o verificación
- Tschandl et al. 2020, *Nature Medicine* (colaboración humano–computadora): la página del editor exigió autenticación y no pude confirmar acceso libre.
- Cassidy et al. 2022, *Medical Image Analysis* (duplicados en ISIC): 403 en ScienceDirect y en el repositorio MMU; acceso no confirmado.
- Daneshjou et al. 2021, *JAMA Dermatology*: no encontré texto completo libre.
- SkinCAP (arXiv:2405.18004): ya está citado como SkinCaRe.


---

## Papers ya descargados en Papers/ y no citados

Inventario del 2026-09-28 sobre `Papers/` y subcarpetas: **114 PDFs**. La comparación con `Bibliography.bib` fue por título normalizado
(más revisión manual de los de baja coincidencia). **108 archivos corresponden a entradas del `.bib`** (son 105 obras distintas: hay tres duplicados,
`Dermatologist-level classification…` dos veces, `Learning Transferable Visual Models…` en `Papers/` y en `Fundacionales/`, y `A General-Purpose
Multimodal Foundation Model for Dermatology`, que es el preprint arXiv:2410.15038 de `yan2025vision`, ya citado en su versión de *Nature Medicine*).
Los **6 restantes no están en el `.bib`**; los seis ya figuran en `refs_pendientes.md` (sección 6, «PDFs en `Papers/` sin entrada en el `.bib`») como pendientes de decidir.

| Archivo | Título | Año | Eje | Relevancia (clase) |
|---|---|---|---|---|
| `derma/Vision-language models for medical report generation and visual question answering a review.pdf` | Vision-language models for medical report generation and visual question answering: a review (Hartsock y Rasool) | 2024 (*Front. Artif. Intell.*) | 3 | (b) Revisión abierta de VLM para reportes y VQA médicos; ordena arquitecturas, datos y métricas. Buen ancla para la línea de reportes. |
| `derma/Deep Learning Algorithms in the Diagnosis of Basal Cell Carcinoma Using Dermatoscopy Systematic Review and Meta-Analysis.pdf` | Deep Learning Algorithms in the Diagnosis of Basal Cell Carcinoma Using Dermatoscopy: Systematic Review and Meta-Analysis (Liu et al.) | 2025 (*JMIR*) | 1 | (b) Meta-análisis de 15 estudios con validación interna y externa; útil para la afirmación de que hay poca validación externa. Alcance acotado a carcinoma basocelular. |
| `derma/Quilt-1M One Million Image-Text Pairs for Histopathology.pdf` | Quilt-1M: One Million Image-Text Pairs for Histopathology (Ikezogwo et al.) | 2023 (NeurIPS D&B) | 2 | (b, débil) Antecedente directo de MONET/Derm1M como corpus imagen–texto extraído de videos y literatura; es de patología, solo como contexto. |
| `Multimodal Foundation Models From Specialists to General-Purpose Assistants (119).pdf` | Multimodal Foundation Models: From Specialists to General-Purpose Assistants (Li et al.) | 2023 (arXiv:2309.10020) | 2 (general) | (c) Encuesta general de modelos multimodales; sirve de fundamento del marco teórico, no del estado del arte dermatológico. |
| `Vision-Language Models for Vision Tasks A Survey (24p).pdf` | Vision-Language Models for Vision Tasks: A Survey (Zhang et al.) | 2023 (arXiv:2304.00685; v2 2024) | 2 (general) | (c) Encuesta de VLM para tareas de visión; fundamento del marco teórico. |
| `Chain-of-Visual-Thought Teaching VLMs to See and Think Better with Continuous Visual Tokens.pdf` | Chain-of-Visual-Thought: Teaching VLMs to See and Think Better with Continuous Visual Tokens (Qin et al.) | 2025 (arXiv:2511.19418) | 2 (general) | (c) VLM general con tokens visuales continuos; sin relación con dermatología ni con medicina. |
| `derma/A General-Purpose Multimodal Foundation Model for Dermatology.pdf` | (Preprint de PanDerm) | 2024 (arXiv:2410.15038) | 2 | (a, duplicado) Es el mismo trabajo que `yan2025vision`; ya citado. Recomendable reemplazar por la versión de *Nature Medicine*. |

Resumen: 108 archivos citados (a, incluido el duplicado de PanDerm), 2 relevantes no citados (b: Hartsock 2024 y Liu 2025), 1 relevante débil (Quilt-1M), 3 no relevantes para el estado del arte (c).

---

## Candidatos por bola de nieve

Método: extraje las listas de referencias (`pdftotext`) de los trabajos del estado del arte que tienen PDF en `Papers/` (Skin-R1, SkinCaRe, MM-Skin,
Derm1M, MAKE, PanDerm, MONET, MedImageInsight, DermaSynth, SkinGEN, SkinGPT-4, Chakrabarti, Khan, SkinSavvy2, MpoxVLM, revisión de Hartsock y otros) y contabilicé qué obras
externas aparecen en varios de ellos o en sus tablas comparativas. «Aparece en» indica mención en el texto o en las referencias del PDF, que es lo que pude verificar automáticamente; no confirmé cada cita una por una.
Todos los candidatos son de 2020–2026 y no están en el `.bib`, en `refs_pendientes.md` ni en las secciones anteriores de este archivo.
Existencia y acceso se verificaron el 2026-09-28: arXiv (página abs y API), PMC/Nature, ACL Anthology, CVF. **[no verificado]** marca lo que no pude confirmar.

Advertencias de calidad de las fuentes: en el PDF de Chakrabarti et al. hay una referencia claramente errónea (`Hohloch, «Homoclinic Floer homology…», arXiv:2402.12345`) y el identificador de XrayGPT
que da (arXiv:2306.00923) corresponde en realidad a otro trabajo (Sonicverse); el correcto es arXiv:2306.07971. Las referencias del PDF de Khan et al. incluyen títulos que no pude ubicar (por ejemplo «SkinIO», «DermHelper»); no tomé nada de ahí.

### Eje 1. Clasificación / diagnóstico de lesiones de piel

#### S1.1 PAD-UFES-20: a skin lesion dataset composed of patient data and clinical images collected from smartphones
- **Autores:** Pacheco, A. G. C. et al. — **Año:** 2020 — **Venue:** *Data in Brief* 32:106221 (arXiv:2007.00478).
- **PDF:** https://arxiv.org/pdf/2007.00478 (abs verificada; editor: https://www.sciencedirect.com/science/article/pii/S235234092031115X) — **Acceso:** abierto en arXiv.
- **Aparece en:** Derm1M, MAKE, MM-Skin, PanDerm (`yan2025vision`), MedImageInsight, DermaSynth (`yilmaz2025resourceefficient`), Skin-R1, SkinCaRe.
- **Qué hace:** 2 298 imágenes clínicas de 1 641 lesiones de 1 373 pacientes en Brasil, con seis diagnósticos (tres cánceres y tres enfermedades) y hasta 22 variables clínicas; 58.4 % confirmado por biopsia, 100 % de los cánceres.
- **Por qué entra:** es el conjunto clínico de teléfono más usado como prueba externa en los VLM dermatológicos (ocho de nuestros papers); da un contrapunto latinoamericano a HAM10000 y a HIBA.

#### S1.2 BCN20000: Dermoscopic Lesions in the Wild
- **Autores:** Hernández-Pérez, C., Combalia, M. et al. — **Año:** 2024 (preprint 2019, arXiv:1908.02288) — **Venue:** *Scientific Data* 11:641.
- **PDF:** https://pmc.ncbi.nlm.nih.gov/articles/PMC11183228/ (Nature: https://www.nature.com/articles/s41597-024-03387-w; preprint https://arxiv.org/pdf/1908.02288) — **Acceso:** abierto (PMC; página de Nature cargó con código 200).
- **Aparece en:** PanDerm, MM-Skin, MedImageInsight, DermaSynth, Skin-R1, SkinCaRe, MONET.
- **Qué hace:** 18 946 imágenes dermatoscópicas de 5 583 lesiones del Hospital Clínic de Barcelona, ocho categorías diagnósticas más una clase fuera de distribución en el test; incluye lesiones difíciles (uñas, mucosas, grandes, hipopigmentadas).
- **Por qué entra:** junto con HAM10000 formó el entrenamiento de ISIC 2019; es el otro gran conjunto dermatoscópico de referencia y una fuente natural de prueba externa europea.

#### S1.3 A patient-centric dataset of images and metadata for identifying melanomas using clinical context (SIIM-ISIC 2020)
- **Autores:** Rotemberg, V. et al. — **Año:** 2021 — **Venue:** *Scientific Data* 8:34.
- **PDF:** https://www.nature.com/articles/s41597-021-00815-z — **Acceso:** página cargó con código 200 (revista de acceso abierto); licencia CC BY **[no verificado]**.
- **Aparece en:** Chandna et al. 2024 (`chandna2024skin`, ya citado).
- **Qué hace:** dataset del desafío SIIM-ISIC 2020 con 2 056 pacientes de tres continentes (20.8 % con al menos un melanoma) e identificadores de paciente que permiten mapear lesiones del mismo individuo.
- **Por qué entra:** ilustra que los identificadores de paciente/lesión permiten particiones sin fuga, la misma preocupación que motiva la partición por lesión de la tesina.

#### S1.4 Towards Trustable Skin Cancer Diagnosis via Rewriting Model's Decision
- **Autores:** Yan, S. et al. — **Año:** 2023 — **Venue:** CVPR 2023 (arXiv:2303.00885).
- **PDF:** https://arxiv.org/pdf/2303.00885 (también CVF: https://openaccess.thecvf.com/content/CVPR2023/papers/Yan_Towards_Trustable_Skin_Cancer_Diagnosis_via_Rewriting_Models_Decision_CVPR_2023_paper.pdf, código 200) — **Acceso:** abierto.
- **Aparece en:** Derm1M.
- **Qué hace:** detecta sesgos espurios (confusores) en clasificadores de cáncer de piel y reescribe la decisión del modelo con anotaciones de conceptos, reduciendo la dependencia de artefactos. Datasets y métricas: **[no verificado]** más allá del resumen.
- **Por qué entra:** conecta el clasificador con conceptos clínicos y con la robustez frente a artefactos, un punto de la sección de generalización.

Nota: Cassidy et al. 2022, «Analysis of the ISIC image datasets» (*Medical Image Analysis* 75:102305), sigue sin acceso verificado: ScienceDirect no respondió, el repositorio MMU (https://e-space.mmu.ac.uk/631025/) redirige y no encontré versión en arXiv **[no verificado]**. Lo mencionan Chandna 2024 y Badhon 2025 (ambos ya en el `.bib`) y MONET. Confirmar acceso antes de proponerlo.

### Eje 2. Modelos visión–lenguaje en dermatología / médicos

#### S2.1 Qwen2.5-VL Technical Report
- **Autores:** Bai, S. et al. (Qwen) — **Año:** 2025 — **Venue:** arXiv:2502.13923 (informe técnico).
- **PDF:** https://arxiv.org/pdf/2502.13923 — **Acceso:** arXiv abierto.
- **Aparece en:** Skin-R1 (base del modelo y baseline de 7B y 32B), MM-Skin.
- **Qué hace:** VLM general abierto con codificador visual de resolución nativa y buen desempeño documental y de agente.
- **Por qué entra:** es el backbone de Skin-R1 y el VLM general abierto más usado como línea base; sirve para justificar la elección de VLM generales pequeños.

#### S2.2 HuatuoGPT-Vision: Towards Injecting Medical Visual Knowledge into Multimodal LLMs at Scale
- **Autores:** Chen, J. et al. — **Año:** 2024 — **Venue:** arXiv:2406.19280 (v4); venue de conferencia **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2406.19280 — **Acceso:** arXiv abierto.
- **Aparece en:** Skin-R1 (baseline médico junto a LLaVA-Med y MedGemma).
- **Qué hace:** inyecta conocimiento visual médico en un MLLM con un conjunto grande de VQA médico; VLM médico abierto de 7B. Detalle del corpus y cifras: **[no verificado]**.
- **Por qué entra:** tercer VLM médico de referencia (con LLaVA-Med y MedGemma) en la comparación de Skin-R1, que como la tesina mide VLM médicos en clasificación dermatológica.

#### S2.3 MedVLM-R1: Incentivizing Medical Reasoning Capability of Vision-Language Models (VLMs) via Reinforcement Learning
- **Autores:** Pan, J. et al. — **Año:** 2025 — **Venue:** arXiv:2502.19634 (v2); venue **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2502.19634 — **Acceso:** arXiv abierto.
- **Aparece en:** Skin-R1.
- **Qué hace:** entrena un VLM médico con aprendizaje por refuerzo (GRPO) para razonar sin supervisión explícita de la cadena de pensamiento; mejora la generalización fuera de distribución (según Skin-R1).
- **Por qué entra:** contexto para el bloque «razonamiento con RL» (Skin-R1, DermoGPT).

#### S2.4 Med-R1: Reinforcement Learning for Generalizable Medical Reasoning in Vision-Language Models
- **Autores:** Lai, Y. et al. — **Año:** 2025 — **Venue:** arXiv:2503.13939 (v5); venue **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2503.13939 — **Acceso:** arXiv abierto.
- **Aparece en:** Skin-R1.
- **Qué hace:** RL sobre VLM médicos en varias modalidades y tareas; según Skin-R1, muestra que el ajuste supervisado puede memorizar atajos y que el RL generaliza mejor.
- **Por qué entra:** par de S2.3; ambos son la referencia de RL médico contra la que Skin-R1 se define.

#### S2.5 MedCLIP: Contrastive Learning from Unpaired Medical Images and Text
- **Autores:** Wang, Z. et al. — **Año:** 2022 — **Venue:** EMNLP 2022 (main).
- **PDF:** https://aclanthology.org/2022.emnlp-main.256.pdf (título verificado en el PDF) — **Acceso:** abierto (ACL Anthology).
- **Aparece en:** PanDerm, Derm1M, MAKE, MM-Skin, LLaVA-Med, Med-Flamingo, MedImageInsight, MedTrinity-25M, Skin-R1, SkinGEN, MONET, Chakrabarti y Hartsock.
- **Qué hace:** preentrenamiento contrastivo imagen–texto médico con imágenes y textos no emparejados, usando conocimiento clínico para el emparejamiento; clasificación zero-shot y recuperación (sobre todo radiografías).
- **Por qué entra:** es el VL médico contrastivo más citado (13 de nuestros papers); antecede a los modelos dermatológicos (MONET, DermLIP) y respalda la comparación general vs. especializado.

#### S2.6 A generalist vision–language foundation model for diverse biomedical tasks (BiomedGPT)
- **Autores:** Zhang, K. et al. — **Año:** 2023 (arXiv:2305.17100); versión de *Nature Medicine* 2024 (https://www.nature.com/articles/s41591-024-03185-2; el título de la página coincide) — **Venue:** *Nature Medicine* (volumen y páginas: **[no verificado]**).
- **PDF:** https://arxiv.org/pdf/2305.17100 — **Acceso:** arXiv abierto; acceso libre del editor **[no verificado]**.
- **Aparece en:** PanDerm, Derm1M, MedImageInsight, PeFoMed, Skin-R1.
- **Qué hace:** transformador generalista unificado que resuelve tareas de visión, lenguaje y multimodales biomédicas (VQA, captioning, clasificación) con un solo modelo.
- **Por qué entra:** referencia de generalista médico que los trabajos dermatológicos usan como comparación; refuerza la tesis de que lo general médico no alcanza en piel.

#### S2.7 Assessing the Utility of Multimodal LLMs (GPT-4 Vision and LLaVA) in Identifying Melanoma Across Different Skin Tones
- **Autores:** Cirone, K. et al. — **Año:** 2024 — **Venue:** *JMIR Dermatology* (doi 10.2196/55508).
- **PDF:** https://derma.jmir.org/2024/1/e55508 — **Acceso:** abierto (JMIR, página cargó con código 202); licencia **[no verificado]**.
- **Aparece en:** DermaSynth (`yilmaz2025resourceefficient`), SkinGEN.
- **Qué hace:** evalúa GPT-4V y LLaVA para distinguir melanoma de lesiones benignas en distintos fototipos; concluyen que pueden diferenciar benignas de melanoma. Tamaño de la muestra y cifras: **[no verificado]**.
- **Por qué entra:** una de las pocas mediciones publicadas de VLM generales sobre melanoma; contrasta con el colapso de VLM generales que halla la tesina.

Alternativa no incluida: PMC-CLIP (arXiv:2303.07240, existencia verificada; aparece en 5 de nuestros papers).

### Eje 3. Generación de reportes dermatológicos / médicos

#### S3.1 XrayGPT: Chest Radiographs Summarization using Medical Vision-Language Models
- **Autores:** Thawakar, O. et al. — **Año:** 2023 — **Venue:** arXiv:2306.07971 (v2); venue (BioNLP en ACL 2024) **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2306.07971 — **Acceso:** arXiv abierto.
- **Aparece en:** Chakrabarti, MM-Skin, Skin-R1, SkinGEN, Hartsock.
- **Qué hace:** alinea un codificador visual médico con un LLM para resumir radiografías de tórax y responder preguntas. Detalles de datos: **[no verificado]**.
- **Por qué entra:** es el VLM de reportes médicos más citado por los trabajos de reportes dermatológicos (cinco de nuestros papers); contexto del enfoque «un VLM redacta el reporte».

#### S3.2 RaDialog: A Large Vision-Language Model for Radiology Report Generation and Conversational Assistance
- **Autores:** Pellegrini, C. et al. — **Año:** 2023 (v3) — **Venue:** arXiv:2311.18681; venue **[no verificado]**.
- **PDF:** https://arxiv.org/pdf/2311.18681 — **Acceso:** arXiv abierto.
- **Aparece en:** Chakrabarti.
- **Qué hace:** VLM que combina hallazgos estructurados de un clasificador de imagen con un LLM para generar el reporte y sostener diálogo. Cifras: **[no verificado]**.
- **Por qué entra:** contraparte radiológica de la cascada clasificador→generador de la tesina (hallazgos del clasificador como insumo del texto).

#### S3.3 Customizing General-Purpose Foundation Models for Medical Report Generation
- **Autores:** Yang, B. et al. — **Año:** 2023 — **Venue:** arXiv:2306.05642 (preprint).
- **PDF:** https://arxiv.org/pdf/2306.05642 — **Acceso:** arXiv abierto.
- **Aparece en:** Chakrabarti.
- **Qué hace:** adapta modelos fundacionales generales al reporte médico con pocos parámetros entrenables. Datasets y resultados: **[no verificado]**.
- **Por qué entra:** respalda la adaptación ligera de modelos generales a reportes, como hace la tesina con SkinVL y LoRA.

#### S3.4 AGNet: Automatic generation network for skin imaging reports
- **Autores:** Wu, F. et al. — **Año:** 2022 — **Venue:** *Computers in Biology and Medicine* 141:105037.
- **PDF:** no encontré versión libre; solo el resumen en https://pubmed.ncbi.nlm.nih.gov/34809964/ y la página de ScienceDirect — **Acceso:** cerrado o **[no verificado]**.
- **Aparece en:** Chakrabarti.
- **Qué hace:** marco de captioning con clasificador de imagen, modelo de lenguaje y módulo de atención para generar reportes de imágenes de piel (existencia y descripción del resumen confirmadas por PubMed).
- **Por qué entra:** antecedente más directo de reportes de piel previo a los VLM; entra solo si se consigue el texto completo.

### Recomendación de la bola de nieve
- **Eje 1:** PAD-UFES-20 (S1.1) y BCN20000 (S1.2) por acceso abierto verificado y uso en 7–8 de nuestros papers; Rotemberg 2021 (S1.3) para la partición por paciente/lesión.
- **Eje 2:** MedCLIP (S2.5) y Qwen2.5-VL (S2.1) como los más citados y de acceso pleno; HuatuoGPT-Vision (S2.2) para completar los VLM médicos medidos; Cirone 2024 (S2.7) por el eje melanoma con VLM generales.
- **Eje 3:** XrayGPT (S3.1) y RaDialog (S3.2); AGNet (S3.4) solo si se logra el PDF.
