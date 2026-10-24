"""Figura de Grad-CAM de 4.4 con rótulos en castellano.

Reutiliza las funciones de Codigo/scripts/interpretability.py y la misma selección (la primera imagen de cada clase en
la prueba de la partición por lesión, Swin-Tiny t06 semilla 42). Solo cambian los rótulos y que no hay título interno.
Se ejecuta desde Codigo/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "scripts"))

import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import interpretability as it
from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.models.classifiers import SwinTinyClassifier
from src.utils.seed import set_seed

OUT = "../Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion/gradcam-swin.pdf"
CKPT = "outputs/checkpoints/swin_tiny_sweep_t06_les_cwnone/best_model.pt"

set_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
swin = SwinTinyClassifier(num_classes=7, pretrained=False, freeze_backbone=False).to(device).eval()
ck = torch.load(CKPT, map_location=device, weights_only=False)
swin.load_state_dict(ck.get("model_state_dict", ck), strict=True)
tf = get_val_transforms(size=224, center_crop=True)
ds = HAM10000Dataset(root_dir="data/processed/HAM10000", split="test",
                     splits_file="data/splits/ham10000_splits.json", return_pil=True)

picks, seen = [], {c: 0 for c in range(7)}
for i in range(len(ds)):
    s = ds[i]; lbl = int(s["label"])
    if seen[lbl] < 1:
        picks.append((s["image"].convert("RGB"), lbl)); seen[lbl] += 1
    if all(seen.values()):
        break

plt.rcParams.update({"font.family": "serif"})
fig, axes = plt.subplots(4, 4, figsize=(8.6, 9.2), squeeze=False)
for row in axes:
    for ax in row:
        ax.axis("off")
for idx, (pil, lbl) in enumerate(picks):
    r, cb = idx // 2, (idx % 2) * 2
    cam, pred = it._swin_gradcam(swin, tf(pil).unsqueeze(0).to(device))
    view = it._view(pil, tf)
    axes[r][cb].imshow(view.resize((224, 224)))
    axes[r][cb].set_title(f"Clase verdadera: {HAM10000_CLASSES[lbl]}", fontsize=10)
    it._overlay(axes[r][cb + 1], view, cam, f"Predicción: {HAM10000_CLASSES[pred]}")
    axes[r][cb + 1].title.set_fontsize(10)
    print(HAM10000_CLASSES[lbl], "->", HAM10000_CLASSES[pred])
fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
