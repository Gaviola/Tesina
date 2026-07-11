"""P2.5 (plan julio-agosto) — Interpretabilidad: ¿el modelo mira la lesión?

Grad-CAM sobre Swin-Tiny (clasificador supervisado) + saliencia por gradiente sobre DermLIP
(VL classifier), superpuestos sobre la imagen. No busca mejorar resultados sino mostrar que
los modelos atienden regiones clínicamente relevantes (la lesión, no el fondo).

Local (RTX 4070). Uso:
    python scripts/interpretability.py
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
import torch.nn.functional as F
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.models.classifiers import SwinTinyClassifier
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Nombres para prompts ZS de DermLIP (orden de HAM10000_CLASSES).
DERMLIP_NAMES = ["melanoma", "melanocytic nevus", "basal cell carcinoma", "actinic keratosis",
                 "benign keratosis", "dermatofibroma", "vascular lesion"]


def _swin_gradcam(model, x):
    """Grad-CAM sobre la última etapa de features de Swin (layout B,H,W,C)."""
    acts, grads = {}, {}
    target = model.backbone.features
    h1 = target.register_forward_hook(lambda m, i, o: acts.__setitem__("a", o))
    h2 = target.register_full_backward_hook(lambda m, gi, go: grads.__setitem__("g", go[0]))
    logits = model(x)
    cls = int(logits.argmax(1))
    model.zero_grad()
    logits[0, cls].backward()
    A, G = acts["a"][0], grads["g"][0]          # (H,W,C)
    w = G.mean(dim=(0, 1))                        # (C,)
    cam = torch.relu((A * w).sum(-1))             # (H,W)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
    h1.remove(); h2.remove()
    return cam.detach().cpu().numpy(), cls


def _dermlip_saliency(dermlip, pil, gt_idx):
    """Saliencia por gradiente de la similitud imagen-texto (clase gt) respecto de la imagen."""
    pixel = dermlip.preprocess(pil).unsqueeze(0).to(dermlip.device).requires_grad_(True)
    img_feat = dermlip.model.encode_image(pixel)
    img_feat = img_feat / img_feat.norm(dim=-1, keepdim=True)
    txt = dermlip.tokenizer([f"a dermatoscopic image of {DERMLIP_NAMES[gt_idx]}"]).to(dermlip.device)
    txt_feat = dermlip.model.encode_text(txt)
    txt_feat = txt_feat / txt_feat.norm(dim=-1, keepdim=True)
    sim = (img_feat @ txt_feat.T).squeeze()
    dermlip.model.zero_grad()
    sim.backward()
    sal = pixel.grad[0].abs().max(0)[0]           # (H,W)
    sal = (sal - sal.min()) / (sal.max() - sal.min() + 1e-8)
    # suavizado leve
    sal = F.avg_pool2d(sal[None, None], 7, stride=1, padding=3)[0, 0]
    return sal.detach().cpu().numpy()


def _overlay(ax, pil, heat, title):
    img = np.asarray(pil.resize((224, 224))).astype(float) / 255.0
    h = np.asarray(plt.cm.jet(heat)[:, :, :3])
    from PIL import Image
    h = np.asarray(Image.fromarray((h * 255).astype(np.uint8)).resize((224, 224))).astype(float) / 255.0
    ax.imshow(0.55 * img + 0.45 * h)
    ax.set_title(title, fontsize=9)
    ax.axis("off")


def main():
    parser = argparse.ArgumentParser(description="P2.5 Interpretabilidad")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--swin_ckpt", type=str, default="outputs/checkpoints/swin_tiny_modern_v3/best_model.pt")
    parser.add_argument("--n_per_class", type=int, default=1, help="Imágenes por clase a mostrar.")
    parser.add_argument("--output_dir", type=str, default="outputs/results/interpretability")
    args = parser.parse_args()

    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out_dir = Path(args.output_dir); out_dir.mkdir(parents=True, exist_ok=True)

    # Modelos
    swin = SwinTinyClassifier(num_classes=7, pretrained=False, freeze_backbone=False).to(device).eval()
    ck = torch.load(args.swin_ckpt, map_location=device, weights_only=False)
    swin.load_state_dict(ck.get("model_state_dict", ck), strict=False)
    from src.models.dermlip import DermLIPClassifier
    dermlip = DermLIPClassifier(checkpoint="vit-b-16", device=device)

    tf = get_val_transforms(size=224, center_crop=False)
    ds = HAM10000Dataset(root_dir=str(Path(args.data_dir) / "processed" / "HAM10000"),
                         split="test", splits_file=str(Path(args.data_dir) / "splits" / "ham10000_splits.json"),
                         return_pil=True)

    # Elegir n_per_class imágenes por clase
    picks = []
    seen = {c: 0 for c in range(7)}
    for i in range(len(ds)):
        s = ds[i]; lbl = int(s["label"])
        if seen[lbl] < args.n_per_class:
            picks.append((s["image"].convert("RGB"), lbl))
            seen[lbl] += 1
        if all(v >= args.n_per_class for v in seen.values()):
            break

    fig, axes = plt.subplots(len(picks), 3, figsize=(7.5, 2.5 * len(picks)), squeeze=False)
    for r, (pil, lbl) in enumerate(picks):
        x = tf(pil).unsqueeze(0).to(device)
        cam, pred = _swin_gradcam(swin, x)
        sal = _dermlip_saliency(dermlip, pil, lbl)
        axes[r][0].imshow(pil.resize((224, 224))); axes[r][0].axis("off")
        axes[r][0].set_title(f"{HAM10000_CLASSES[lbl]}", fontsize=9)
        _overlay(axes[r][1], pil, cam, f"Swin Grad-CAM (pred {HAM10000_CLASSES[pred]})")
        _overlay(axes[r][2], pil, sal, "DermLIP saliencia")
    fig.suptitle("¿El modelo mira la lesión? Grad-CAM (Swin) y saliencia (DermLIP)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    png = out_dir / "interpretability.png"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    logger.info("Figura: %s", png)


if __name__ == "__main__":
    main()
