"""P2.4 (mejora #2) — Figura ilustrativa de las perturbaciones de robustez.

Toma UNA imagen de test, la degrada en los 5 niveles de cada perturbación (JPEG, ruido, blur,
resolución) y muestra, panel por panel, la imagen degradada + la predicción de Swin-Tiny. Permite
al lector visualizar el impacto de cada perturbación y su severidad. Local (RTX 4070).

Uso:
    python scripts/robustness_examples.py                 # elige una imagen automáticamente
    python scripts/robustness_examples.py --image_id ISIC_0034524
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data.ham10000 import HAM10000Dataset, HAM10000_CLASSES
from src.data.transforms import get_val_transforms
from src.models.classifiers import SwinTinyClassifier
from src.utils.seed import set_seed

# Reutiliza perturbaciones y niveles del script de robustez.
from scripts.robustness_perturbations import _perturb, _load_model, JPEG_Q, NOISE_S, BLUR_R, RES_F

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PERTURBS = [
    ("jpeg", "JPEG (calidad)", JPEG_Q),
    ("noise", "Ruido ($\\sigma$)", NOISE_S),
    ("blur", "Desenfoque (radio)", BLUR_R),
    ("resolution", "Resolución (factor)", RES_F),
]


@torch.no_grad()
def _predict(model, pil, tf, device):
    x = tf(pil).unsqueeze(0).to(device)
    return int(model(x).argmax(1).item())


def main():
    parser = argparse.ArgumentParser(description="Figura ilustrativa de perturbaciones")
    parser.add_argument("--image_id", type=str, default=None)
    parser.add_argument("--data-dir", type=str, default="data")
    parser.add_argument("--output", type=str, default="outputs/results/robustness/robustness_examples.png")
    args = parser.parse_args()

    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rng = np.random.default_rng(42)
    tf = get_val_transforms(size=224, center_crop=True)
    ds = HAM10000Dataset(root_dir=str(Path(args.data_dir) / "processed" / "HAM10000"),
                         split="test", splits_file=str(Path(args.data_dir) / "splits" / "ham10000_splits.json"),
                         return_pil=True)
    model = _load_model(SwinTinyClassifier, "outputs/checkpoints/swin_tiny_modern_v3/best_model.pt", device)

    # Elegir imagen: la pedida, o la primera que Swin clasifica bien sin perturbar (para ver la caída).
    pick = None
    for i in range(len(ds)):
        s = ds[i]
        iid = s["image_id"]
        if args.image_id and iid != args.image_id:
            continue
        pil = s["image"].convert("RGB"); lbl = int(s["label"])
        if args.image_id or _predict(model, pil, tf, device) == lbl:
            pick = (pil, lbl, iid)
            break
    if pick is None:
        logger.error("No se encontró imagen adecuada."); return
    pil, gt, iid = pick
    logger.info("Imagen %s (gt=%s)", iid, HAM10000_CLASSES[gt])

    n_cols = 6  # original + 5 severidades
    fig, axes = plt.subplots(len(PERTURBS), n_cols, figsize=(2.0 * n_cols, 2.35 * len(PERTURBS)),
                             squeeze=False)
    for r, (kind, label, levels) in enumerate(PERTURBS):
        for c in range(n_cols):
            ax = axes[r][c]; ax.axis("off")
            sev = c  # col 0 = original (sev 0)
            img = _perturb(pil, kind, sev, rng)
            pred = _predict(model, img, tf, device)
            ax.imshow(img.resize((224, 224)))
            ok = (pred == gt)
            if c == 0:
                title = f"original\npred: {HAM10000_CLASSES[pred]}"
            else:
                val = levels[sev]
                title = f"sev{sev} ({val})\npred: {HAM10000_CLASSES[pred]}"
            ax.set_title(title, fontsize=8, color=("#2E7D32" if ok else "#C62828"))
        axes[r][0].set_ylabel(label, fontsize=9)
        # Etiqueta de fila a la izquierda (con axis off usamos text)
        axes[r][0].text(-0.15, 0.5, label, transform=axes[r][0].transAxes, rotation=90,
                        va="center", ha="center", fontsize=10, fontweight="bold")
    fig.suptitle(f"Impacto de las perturbaciones — imagen {iid} (gt: {HAM10000_CLASSES[gt]}). "
                 f"Verde = predicción correcta, rojo = incorrecta.", fontsize=11)
    fig.tight_layout(rect=[0.02, 0, 1, 0.96])
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    logger.info("Figura: %s", out)


if __name__ == "__main__":
    main()
