"""Figura de 3.8: cómo queda una imagen con cada perturbación de la evaluación de robustez, en los niveles 1, 3 y 5.

Usa la misma función que la evaluación (robustness_perturbations._perturb) sobre la primera imagen de melanoma del
conjunto de prueba, y muestra la vista que recibe el modelo. Se ejecuta desde Codigo/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "scripts"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import interpretability as it
import robustness_perturbations as rp
from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.data.transforms import get_val_transforms

OUT = "../Docs/TFG/Figures/Capitulos/03-Materiales-Metodos/perturbaciones-ejemplo.pdf"
FILAS = [("jpeg", "Compresión JPEG", "calidad", rp.JPEG_Q), ("noise", "Ruido gaussiano", "desvío", rp.NOISE_S),
         ("blur", "Desenfoque", "radio", rp.BLUR_R), ("resolution", "Resolución", "escala", rp.RES_F)]
NIVELES = (1, 3, 5)

tf = get_val_transforms(size=224, center_crop=True)
ds = HAM10000Dataset(root_dir="data/processed/HAM10000", split="test",
                     splits_file="data/splits/ham10000_splits.json", return_pil=True)
mel = HAM10000_CLASSES.index("MEL") if "MEL" in HAM10000_CLASSES else HAM10000_CLASSES.index("mel")
pil = next(ds[i]["image"].convert("RGB") for i in range(len(ds)) if int(ds[i]["label"]) == mel)

rng = np.random.default_rng(42)
plt.rcParams.update({"font.family": "serif", "font.size": 9})
fig, axs = plt.subplots(len(FILAS), 1 + len(NIVELES), figsize=(5.6, 5.8))
for r, (k, nombre, param, valores) in enumerate(FILAS):
    axs[r][0].imshow(it._view(pil, tf).resize((224, 224)))
    axs[r][0].set_ylabel(nombre, fontsize=9)
    axs[r][0].set_title("Sin perturbar" if r == 0 else "", fontsize=8)
    for c, n in enumerate(NIVELES, 1):
        axs[r][c].imshow(it._view(rp._perturb(pil, k, n, rng), tf).resize((224, 224)))
        axs[r][c].set_title(f"Nivel {n} ({param} {valores[n]})", fontsize=8)
    for ax in axs[r]:
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
fig.tight_layout(h_pad=0.6, w_pad=0.3)
Path(OUT).parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=170, bbox_inches="tight")
