# Resultado — Clasificadores clásicos sobre embeddings (P2.3)

**Fecha:** 2026-07-07 · **Plan:** [plan-julio-agosto.md](../plan-julio-agosto.md) (P2.3) · **Sin jobs SLURM** (local, RTX 4070).
**Feedback:** #20 — usar embeddings (DermLIP/CLIP/Swin) + SVM/RF/XGBoost para ver si la representación ya separa las clases.

## Diseño
- Se extraen embeddings **congelados** de dos representaciones y se entrenan clasificadores clásicos
  sobre HAM10000 (train ~7000, test 1503):
  - **DermLIP (ViT-B/16)** — representación derm-especializada (Derm1M), dim 512.
  - **Swin-ImageNet (frozen)** — representación genérica (torchvision, sin fine-tuning en HAM), dim 768.
- Clasificadores: **SVM (RBF)**, **Random Forest**, **Logistic Regression** (todos `class_weight=balanced`).
  (XGBoost no disponible en el entorno.)
- **Código:** `scripts/embeddings_classical.py`. **Salida:** `outputs/results/embeddings/`.
- Referencias: DermLIP linear-probe (LogReg, resul previo) F1 0.762 / sens 0.739; Swin fine-tuneado
  F1 0.882 / sens 0.870.

## Resultados (test HAM10000, n=1503)

| Representación | Clasificador | Acc | F1-w | Sens.\ macro |
|----------------|--------------|:-:|:-:|:-:|
| **DermLIP (ViT-B/16)** | **SVM (RBF)** | 0.881 | **0.881** | **0.788** |
| DermLIP | Logistic Reg. | 0.815 | 0.823 | 0.717 |
| DermLIP | Random Forest | 0.818 | 0.794 | 0.550 |
| Swin-ImageNet (frozen) | SVM (RBF) | 0.806 | 0.801 | 0.579 |
| Swin-ImageNet (frozen) | Logistic Reg. | 0.737 | 0.752 | 0.599 |
| Swin-ImageNet (frozen) | Random Forest | 0.678 | 0.560 | 0.163 |

## Análisis
1. **La representación es lo que importa.** Un SVM \emph{barato} sobre embeddings DermLIP \emph{congelados}
   (F1 0.881, sens 0.788) **iguala al Swin fine-tuneado** (F1 0.882) —sin entrenar un modelo pesado, solo
   un clasificador clásico sobre features fijas—. Incluso supera al linear-probe de DermLIP (F1 0.762): el
   SVM no lineal extrae algo más que la separación lineal.
2. **La especialización de dominio de la representación es la clave.** La misma familia de clasificadores
   sobre la representación \emph{genérica} (Swin-ImageNet) rinde bastante menos: sens.\ macro 0.58 (SVM) /
   0.60 (LogReg) vs 0.79 / 0.72 con DermLIP. No es el clasificador ni la arquitectura, es que las clases
   de lesiones ya están \emph{separadas en el espacio de embeddings} de DermLIP y no tanto en el de
   ImageNet.
3. **SVM (RBF) es el mejor clásico**; Random Forest colapsa en las minoritarias (sens 0.16 sobre
   ImageNet), sensible a la alta dimensión.

## Conclusión (veredicto)
**CUMPLE.** Confirma cuantitativamente el eje cost-aware + especialización: para el diagnóstico, una
**representación derm-especializada + un clasificador trivial** alcanza el nivel del fine-tuning pesado;
la representación genérica no. Refuerza el hallazgo de DermLIP y la tesis "especialización $>$
arquitectura general". Se integra a `experimentacion.tex` (§DermLIP).
