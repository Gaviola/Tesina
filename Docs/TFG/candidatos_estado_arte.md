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
