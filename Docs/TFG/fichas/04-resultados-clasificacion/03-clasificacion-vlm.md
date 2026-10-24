# Ficha 4.3 — Clasificación con modelos visión--lenguaje

**Estado (24/10/2026): redactada sin aprobación previa.** El autor pidió escribir el resto del Cap. 4 de una pasada
y revisarlo entero al final (24/10). Las decisiones que se habrían consultado están en «Decisiones tomadas».

Archivo: `Chapters/04-Resultados-Clasificacion/03-clasificacion-vlm.tex`. Label: `sec:res_vlm`.
Tablas: `tab:res_vlm_generativos`, `tab:res_vlm_controles`, `tab:res_dermlip`, `tab:res_dermlip_swin`,
`tab:res_pruebas_vlm`.

## Hilo conductor

Pregunta que responde la sección: ¿clasifica un VLM las lesiones dermatoscópicas tan bien como un clasificador
supervisado, y si no, se debe a la falta de especialización o a clasificar generando texto?

Viene de: 4.1 y 4.2 dejan la referencia supervisada (Swin 0.692 ± 0.025 de sensibilidad macro; 0.716 con la semilla
42; MEL 0.796 con umbral). Del Cap. 3: los modelos y las cuatro estrategias (`sec:met_vlm_generativos`,
`sec:met_vlm_estrategias`), los cuatro usos de DermLIP (`sec:met_dermlip`), los tres controles
(`sec:met_vlm_procedimiento`), las referencias (`sec:met_referencias`) y Holm sobre 21 pares (`sec:met_estadistica`).
Deja instalado: los VLM generativos no clasifican (sensibilidad macro ≤ 0.181, colapso hacia una clase), no por el
desbalance ni por la modalidad; la especialización (DermLIP) sí aporta y el efecto es de la representación; ningún VLM
iguala al supervisado en F1 macro. Por lo tanto, el diagnóstico del *pipeline* viene del clasificador (4.5, Cap. 5).

```
P1  Generativos (tab:res_vlm_generativos): diez combinaciones (2 modelos × 5: generación, verosimilitud, CoT, y las dos
    con ajuste). Sensibilidad macro entre 0.045 y 0.181, en torno al 1/7 del azar y a 0.5 de Swin. Cada
    combinación concentra sus predicciones en una clase (BCC 0.987, DF 0.780, MEL 0.874...): colapso hacia una
    clase (se define acá)                                                              función: describe
    ↓ ampliación: las métricas que parecen mejores se explican por ese colapso
P2  Exactitud engañosa y ajuste: Mini-VLM ajustado con verosimilitud llega a 0.660 de exactitud porque predice NV
    en el 99.1 %, igual que el clasificador trivial (0.669). LLaVA-Med ajustado con CoT deja 1 223 respuestas sin
    etiqueta. El ajuste con textos clínicos no cambia la sensibilidad macro (≤ 0.145)       función: interpreta
    ↓ necesidad: ¿por qué colapsan? primera explicación candidata, el desbalance
P3  No es el desbalance (C13): los modelos no se ajustaron con HAM10000, colapsan ya sin ajuste, y a clases
    distintas según modelo y estrategia (BCC, DF, MEL, VASC); solo una de diez colapsa hacia NV. Un sesgo por la
    frecuencia de NV llevaría todas hacia NV                                             función: interpreta
    ↓ consecuencia: si no es la frecuencia, ¿qué guía la predicción? control con imagen gris
P4  Imagen gris (tab:res_vlm_controles): sin imagen, los dos predicen una sola clase en el 100 % (Mini MEL, LLaVA
    DF); con imagen, las predicciones se dispersan un poco (2 y 5 clases) pero la sensibilidad macro sube solo a
    0.181 y 0.157. El prompt fija la respuesta por defecto y la imagen la desplaza poco      función: interpreta
    ↓ contraste: ¿y si el problema es la dermatoscopía, rara en los datos de estos modelos?
P5  Fotografías clínicas de SkinCAP (624): sensibilidad macro 0.176 y 0.106, no mejor que en HAM10000 (0.181 y
    0.157), y colapsan hacia DF. La dificultad no está en la modalidad                     función: interpreta
    ↓ necesidad: queda la especialización; DermLIP la aísla sin generar texto
P6  DermLIP (tab:res_dermlip): sin ajuste, 0.510 de sensibilidad macro, casi tres veces la de los generativos, sin
    haber visto HAM10000. Con cabezas: linear probe 0.729 (pero F1 macro 0.618), SVM 0.673 / F1 macro 0.705, kNN
    0.568. El linear probe supera a Swin en sensibilidad macro pero no en F1 macro: la divergencia de 3.7 por los
    pesos balanceados                                                                     función: describe / interpreta
    ↓ necesidad: ¿la mejora es de la representación o de la cabeza?
P7  Control Swin-ImageNet (tab:res_dermlip_swin): con las tres cabezas, DermLIP supera a Swin congelado por 0.15
    a 0.35 de sensibilidad macro; el efecto es de la representación dermatológica         función: interpreta
    ↓ consecuencia: ¿son significativas las distancias con los supervisados?
P8  McNemar con Holm y bootstrap (tab:res_pruebas_vlm): los 15 pares que incluyen un modelo sin ajuste son
    significativos (p < 10⁻⁹); la sensibilidad macro de los supervisados supera a DermLIP sin ajuste en 0.08–0.21 y a
    los generativos en 0.44–0.57. Entre Mini-VLM y LLaVA-Med, McNemar distingue (163 frente a 68 casos) pero el IC
    de la sensibilidad macro incluye el cero                                              función: compara
    ↓ ampliación (literatura)
P9  Literatura: DermLIP informa 0.561 de exactitud media sin ajuste en cuatro conjuntos (acá 0.377 en HAM10000);
    SkinVL es el único de su comparación que supera el 50 % en HAM10000 sin ajuste; Jiang et al., 1.50–13.35 % en
    consultas reales con modelos abiertos. El colapso de los generativos de propósito general coincide con las
    evaluaciones independientes                                                           función: compara
→ Transición a 4.4: el diagnóstico viene del supervisado; falta ver si su desempeño se sostiene fuera de la prueba.

Se definen acá: colapso hacia una clase.
Se retoman de antes (\ref): estrategias, DermLIP, controles, Holm, referencias, verosimilitud, CoT.
Extensión: 10 párrafos y 5 tablas, ~6 páginas.
```

## Fuentes de cada número

Todo en `Codigo/outputs/results/`. Las métricas de los generativos se recalcularon sobre las 1 503 imágenes, con las
respuestas sin etiqueta contadas como error (3.4: cuentan como «desconocido»). Los `*_test_results.json` de CoT
calculan sobre las respuestas válidas y no se usan (LLaVA-Med ajustado con CoT da 0.179 sobre 280 válidas y 0.045
sobre 1 503).

| Combinación | Fuente | Exact. | F1 m | Sens. m | Desc. | Clase más predicha |
|---|---|---|---|---|---|---|
| Mini, generación | `mini_vlm/v1/mini_vlm_predictions.json` | 0.051 | 0.019 | 0.144 | 0 | BCC 0.987 |
| Mini, verosimilitud | `mini_vlm/v1/mini_vlm_likelihood_predictions.json` | 0.189 | 0.061 | 0.181 | 0 | DF 0.780 |
| Mini, CoT | `mini_vlm/v1/mini_vlm_cot_predictions.json` | 0.092 | 0.030 | 0.123 | 7 | MEL 0.874 |
| Mini, ajuste + verosim. | `mini_vlm/v2/..._likelihood_finetuned_predictions.json` | 0.660 | 0.114 | 0.141 | 0 | NV 0.991 |
| Mini, ajuste + CoT | `mini_vlm/v2/..._cot_finetuned_predictions.json` | 0.111 | 0.036 | 0.145 | 1 | MEL 0.971 |
| LLaVA, generación | `llava_med/v1/llava_med_predictions.json` | 0.114 | 0.049 | 0.156 | 0 | MEL 0.967 |
| LLaVA, verosimilitud | `llava_med/v1/llava_med_likelihood_predictions.json` | 0.037 | 0.036 | 0.157 | 0 | VASC 0.365 |
| LLaVA, CoT | `llava_med/v1/llava_med_cot_predictions.json` | 0.087 | 0.026 | 0.112 | 223 | MEL 0.852 |
| LLaVA, ajuste + verosim. | `llava_med/v2/..._likelihood_finetuned_predictions.json` | 0.179 | 0.079 | 0.137 | 0 | MEL 0.586 |
| LLaVA, ajuste + CoT | `llava_med/v2/..._cot_finetuned_predictions.json` | 0.031 | 0.042 | 0.045 | 1 223 | MEL 0.154 |

Controles (verosimilitud sin ajuste): imagen gris `*_likelihood_noimage_predictions.json` (Mini 0.111 / 0.143 / MEL
1.000; LLaVA 0.011 / 0.143 / DF 1.000); *SkinCAP* `*_likelihood_clinical_predictions.json`, 624 imágenes (Mini 0.181
/ 0.176 / DF 0.635; LLaVA 0.071 / 0.106 / DF 0.428). Distribución con imagen: Mini 2 clases, LLaVA 5
(`prior_lenguaje_noimage_resul_20260824.md`).

DermLIP, partición por lesión (`dermlip/dermlip_split_eval.json`, `lesion`; zero-shot de
`classification_summary_les.json` y del recálculo): exactitud / F1 macro / sens. macro / sens. MEL — zero-shot 0.377
/ 0.364 / 0.510 / 0.760; linear probe 0.738 / 0.618 / 0.729 / 0.593; kNN 0.781 / 0.601 / 0.568 / 0.437; SVM 0.832 /
0.705 / 0.673 / 0.569.

Control con Swin (`embeddings/embeddings_classical_les.json`), F1 macro / sens. macro: DermLIP SVM 0.705 / 0.673,
LogReg 0.671 / 0.689, RF 0.577 / 0.515; Swin-ImageNet SVM 0.517 / 0.466, LogReg 0.519 / 0.538, RF 0.150 / 0.162.

Pruebas (`statistical_tests_les_v2.json`, `densenet_vit_moderna_report.json` `holm`): los generativos son los de
*zero-shot* por generación (`statistical_tests.py` usa `mini_vlm_predictions.json` y `llava_med_predictions.json`).
Diferencias de sensibilidad macro con IC: Swin−DermLIP 0.206 [0.148, 0.266], −Mini 0.572 [0.522, 0.622], −LLaVA 0.560
[0.510, 0.610]; ConvNeXt 0.184 [0.126, 0.244], 0.550 [0.501, 0.600], 0.538 [0.488, 0.590]; ViT 0.188 [0.136, 0.242],
0.554 [0.503, 0.606], 0.542 [0.490, 0.595]; DenseNet 0.084 [0.020, 0.150], 0.450 [0.398, 0.508], 0.438 [0.385,
0.495]. DermLIP−Mini 0.367 [0.315, 0.415]; DermLIP−LLaVA 0.354 [0.303, 0.404]; Mini−LLaVA −0.012 [−0.025, 0.001].
McNemar: Swin−DermLIP 768 / 62; Mini−LLaVA 68 / 163, p = 3.5 × 10⁻¹⁰ (umbral 0.0071). Los 15 pares con un modelo sin
ajuste: p ≤ 3.5 × 10⁻¹⁰, todos bajo su umbral.

## Claves de cita

Solo para comparar: `yan2025derm1miccv`, `zeng2025mmskin`, `jiang2026multimodal`, `yan2026dermfmzero` (valores de
`tab:marco_sota_vlm` y `tab:marco_sota_vlm_gen` y del texto de `sec:estado_arte_vlm`).

## Decisiones tomadas

- **Sin la figura `classification_summary_les.png`** (pregunta 1 de la ficha del capítulo): solo tiene los
  modelos sin ajuste, sin Mini-VLM v2. Las tablas la reemplazan.
- **Métricas de los generativos sobre las 1 503 imágenes**, con «desconocido» como error, de acuerdo con 3.4.
- **Holm con los generativos por generación**, que es lo que se calculó; se dice en el texto.
- **DermLIP sobre fotografías clínicas** (sensibilidad macro 0.454, existe en `dermlip/`) no entra: el control de 3.4
  es solo para los generativos. Ver pregunta 1.
- La regresión logística del control (0.689) no coincide con el linear probe (0.729) porque usa *embeddings*
  estandarizados en lugar de normalizados (3.4); se aclara en una oración.
- Sin Wilcoxon (C3).

## Preguntas abiertas

1. ¿Agregar DermLIP sobre *SkinCAP* (0.454) como contraste del control clínico? Reforzaría que las fotografías
   clínicas sí se pueden clasificar, pero exige agregar una oración a 3.4.

## Revisión del autor (24/10/2026)

- Pregunta 1 resuelta: DermLIP sobre *SkinCAP* entra como contraste en `tab:res_vlm_controles` y en el párrafo del
  control clínico (exactitud 0.386, sensibilidad macro 0.454, `dermlip/dermlip_zeroshot_vit-b-16_clinical_predictions.json`;
  coincide con `tab:dermlip_dominio` de `experimentacion.tex`). Se agregó una oración en 3.4 (commit aparte).
- Se agregó el IC de *bootstrap* de la sensibilidad macro de los generativos por generación ([0.137, 0.152] y
  [0.145, 0.168], `statistical_tests_les_v2.json`), que incluye 1/7, como en `experimentacion.tex` (§ calibración y
  significancia).
- Verificación contra `experimentacion.tex`: la figura de colapso de ese documento atribuye a LLaVA-Med con CoT un
  colapso hacia VASC del 81 %. En las predicciones, ese 81 % son respuestas sin etiqueta (código −1); el rótulo VASC
  sale de indexar la lista de clases con −1. La sección usa el recálculo (1 223 sin etiqueta, MEL 0.154).
- El «F1» de `tab:clasificacion` de `experimentacion.tex` es el F1 ponderado (DermLIP sin ajuste 0.424); la sección
  informa el F1 macro (0.364).
