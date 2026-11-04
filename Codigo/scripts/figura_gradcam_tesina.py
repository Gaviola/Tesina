"""Figuras de Grad-CAM de 4.2 con rótulos en castellano.

gradcam-swin.pdf: la primera imagen de cada clase en el conjunto de prueba de la partición por lesión (Swin-Tiny t06,
ejecución de referencia), con los pares separados y el último centrado.

gradcam-swin-errores.pdf: dos errores seleccionados, no representativos. Candidatos: los errores del modelo con una
vista, ordenados de menor a mayor proporción de activación en el cuadrado central de la imagen (donde HAM10000 suele
ubicar la lesión). Entre los primeros se eligen por inspección visual los dos de ERRORES, cuya activación cae fuera de la
lesión. La lista de candidatos se guarda en outputs/results/interpretability_les/candidatos_errores.json.

Reutiliza las funciones de Codigo/scripts/interpretability.py. Se ejecuta desde Codigo/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "scripts"))

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import interpretability as it
from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.models.classifiers import SwinTinyClassifier
from src.utils.seed import set_seed

DIR = "../Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion"
CKPT = "outputs/checkpoints/swin_tiny_sweep_t06_les_cwnone/best_model.pt"
CANDIDATOS = Path("outputs/results/interpretability_les/candidatos_errores.json")
# Posiciones en el conjunto de prueba; se fijan después de inspeccionar los candidatos.
ERRORES = [int(a) for a in sys.argv[1:]]

set_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
swin = SwinTinyClassifier(num_classes=7, pretrained=False, freeze_backbone=False).to(device).eval()
ck = torch.load(CKPT, map_location=device, weights_only=False)
swin.load_state_dict(ck.get("model_state_dict", ck), strict=True)
tf = get_val_transforms(size=224, center_crop=True)
ds = HAM10000Dataset(root_dir="data/processed/HAM10000", split="test",
                     splits_file="data/splits/ham10000_splits.json", return_pil=True)
plt.rcParams.update({"font.family": "serif"})


def par(fig, rect, pil, lbl):
    """Dibuja imagen y mapa uno al lado del otro; rect = (x, y, ancho de cada panel, alto)."""
    x, y, w, h = rect
    cam, pred = it._swin_gradcam(swin, tf(pil).unsqueeze(0).to(device))
    view = it._view(pil, tf)
    a = fig.add_axes((x, y, w, h))
    a.imshow(view.resize((224, 224)))
    a.set_title(f"Clase verdadera: {HAM10000_CLASSES[lbl]}", fontsize=9)
    a.axis("off")
    b = fig.add_axes((x + w + 0.008, y, w, h))
    it._overlay(b, view, cam, f"Predicción: {HAM10000_CLASSES[pred]}")
    b.title.set_fontsize(9)
    print(HAM10000_CLASSES[lbl], "->", HAM10000_CLASSES[pred])


def fig_primeras():
    picks, seen = [], set()
    for i in range(len(ds)):
        s = ds[i]
        lbl = int(s["label"])
        if lbl not in seen:
            picks.append((s["image"].convert("RGB"), lbl))
            seen.add(lbl)
        if len(seen) == 7:
            break
    w = 0.215  # ancho de un panel; el espacio entre pares separa las columnas
    fig = plt.figure(figsize=(8.6, 9.2))
    h = w * 8.6 / 9.2
    alto = 0.25
    for idx, (pil, lbl) in enumerate(picks):
        fila, col = idx // 2, idx % 2
        x = 0.02 + col * 0.51
        if idx == 6:  # el último par queda solo: va centrado
            x = 0.5 - w - 0.004
        par(fig, (x, 1 - (fila + 1) * alto + 0.02, w, h), pil, lbl)
    fig.savefig(f"{DIR}/gradcam-swin.pdf", dpi=150, bbox_inches="tight")


def candidatos():
    filas = []
    for i in range(len(ds)):
        s = ds[i]
        lbl = int(s["label"])
        cam, pred = it._swin_gradcam(swin, tf(s["image"].convert("RGB")).unsqueeze(0).to(device))
        if pred == lbl:
            continue
        h, w = cam.shape
        central = cam[h // 4:h - h // 4, w // 4:w - w // 4].sum() / (cam.sum() + 1e-8)
        filas.append({"pos": i, "verdadera": HAM10000_CLASSES[lbl], "pred": HAM10000_CLASSES[pred],
                      "central": float(central)})
    filas.sort(key=lambda f: f["central"])
    CANDIDATOS.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATOS.write_text(json.dumps(filas, indent=1), encoding="utf8")
    print(len(filas), "errores; mediana de activación central", np.median([f["central"] for f in filas]))
    return filas


def montaje(filas, ruta, n=12):
    """Vista de trabajo de los primeros candidatos, para elegir por inspección."""
    fig, axs = plt.subplots(n // 2, 4, figsize=(10, 2.5 * (n // 2)))
    for ax in axs.ravel():
        ax.axis("off")
    for k, f in enumerate(filas[:n]):
        s = ds[f["pos"]]
        pil = s["image"].convert("RGB")
        cam, _ = it._swin_gradcam(swin, tf(pil).unsqueeze(0).to(device))
        view = it._view(pil, tf)
        fila, col = k // 2, (k % 2) * 2
        axs[fila][col].imshow(view.resize((224, 224)))
        axs[fila][col].set_title(f"#{f['pos']} {f['verdadera']} → {f['pred']}", fontsize=8)
        it._overlay(axs[fila][col + 1], view, cam, f"central {f['central']:.2f}")
    fig.tight_layout()
    fig.savefig(ruta, dpi=75)


def fig_errores():
    w = 0.235
    fig = plt.figure(figsize=(8.6, 2.5))
    h = w * 8.6 / 2.5
    for k, pos in enumerate(ERRORES):
        s = ds[pos]
        par(fig, (0.01 + k * 0.51, 0.03, w, min(h, 0.82)), s["image"].convert("RGB"), int(s["label"]))
    fig.savefig(f"{DIR}/gradcam-swin-errores.pdf", dpi=150, bbox_inches="tight")


if ERRORES:
    fig_primeras()
    fig_errores()
else:
    montaje(candidatos(), CANDIDATOS.parent / "montaje_errores.png")
