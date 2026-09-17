"""P2.4 (plan julio-agosto) — Robustez a condiciones de adquisición (perturbaciones).

Perturba las imágenes de test de HAM10000 (JPEG, ruido gaussiano, blur, bajada de resolución)
en niveles crecientes, re-corre el clasificador y mide la caída de sensibilidad macro / exactitud.
Responde al feedback #7: ¿qué pasa si cambian resolución/iluminación/ruido/compresión? HIBA ya
cubrió cambio de población; esto cubre calidad de imagen.

Local (RTX 4070) sobre los checkpoints ya entrenados. Corre sobre los ganadores del split disjunto
por lesión, no sobre los modelos v3 del split aleatorio: esos están entrenados con fuga de
información entre particiones y sus números no son comparables con el resto del documento.

El archivo de particiones sigue siendo ham10000_splits.json porque el test del split por lesión es
idéntico al original (mismas 1503 imágenes); lo que cambia entre ambos es train y val.

Uso:
    python scripts/robustness_perturbations.py
    python scripts/robustness_perturbations.py --limit 600
    python scripts/robustness_perturbations.py --swin-ckpt <ruta> --convnext-ckpt <ruta>
"""

import argparse
import io
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageFilter
from sklearn.metrics import accuracy_score, recall_score

from src.data.ham10000 import HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.models.classifiers import (
    ConvNeXtTinyClassifier,
    DenseNet121Classifier,
    SwinTinyClassifier,
    ViTClassifier,
)
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ganadores del barrido sobre el split disjunto por lesión, seleccionados por F1 macro en
# validación (ver docs/ideas/criterio_seleccion_plan_20260917.md). Se pueden sobrescribir por CLI.
CKPT_SWIN     = "outputs/checkpoints/swin_tiny_sweep_t06_les_cwnone/best_model.pt"
CKPT_CONVNEXT = "outputs/checkpoints/convnext_tiny_sweep_t02_les_cwnone/best_model.pt"
MODELS = {
    "Swin-Tiny":     (SwinTinyClassifier,     CKPT_SWIN),
    "ConvNeXt-Tiny": (ConvNeXtTinyClassifier, CKPT_CONVNEXT),
}

# Niveles de severidad (0 = sin perturbar). Índices 1..5 crecientes.
JPEG_Q   = {1: 70, 2: 50, 3: 30, 4: 15, 5: 5}     # calidad JPEG (menor = peor)
NOISE_S  = {1: 8, 2: 16, 3: 32, 4: 48, 5: 64}      # desvío del ruido (0-255)
BLUR_R   = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6}          # radio de blur
RES_F    = {1: 0.75, 2: 0.5, 3: 0.35, 4: 0.25, 5: 0.15}  # fracción de resolución
PERTURBATIONS = ["jpeg", "noise", "blur", "resolution"]


def _perturb(img: Image.Image, kind: str, sev: int, rng: np.random.Generator) -> Image.Image:
    if sev == 0:
        return img
    if kind == "jpeg":
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=JPEG_Q[sev])
        buf.seek(0)
        return Image.open(buf).convert("RGB")
    if kind == "noise":
        a = np.asarray(img).astype(np.float32) + rng.normal(0, NOISE_S[sev], (img.size[1], img.size[0], 3))
        return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if kind == "blur":
        return img.filter(ImageFilter.GaussianBlur(BLUR_R[sev]))
    if kind == "resolution":
        w, h = img.size
        f = RES_F[sev]
        small = img.resize((max(1, int(w * f)), max(1, int(h * f))), Image.BILINEAR)
        return small.resize((w, h), Image.BILINEAR)
    return img


def _load_model(cls, ckpt_path, device):
    m = cls(num_classes=7, pretrained=False, freeze_backbone=False).to(device).eval()
    ck = torch.load(ckpt_path, map_location=device, weights_only=False)
    sd = ck.get("model_state_dict", ck) if isinstance(ck, dict) else ck
    missing, unexpected = m.load_state_dict(sd, strict=False)
    if unexpected:
        logger.warning("  state_dict unexpected keys: %d (e.g. %s)", len(unexpected), unexpected[:2])
    return m


@torch.no_grad()
def _infer(model, pils, labels, kind, sev, tf, device, rng, batch=64):
    preds = []
    batch_t = []
    for img in pils:
        p = _perturb(img, kind, sev, rng)
        batch_t.append(tf(p))
        if len(batch_t) == batch:
            x = torch.stack(batch_t).to(device)
            preds.extend(model(x).argmax(1).cpu().tolist())
            batch_t = []
    if batch_t:
        x = torch.stack(batch_t).to(device)
        preds.extend(model(x).argmax(1).cpu().tolist())
    acc = accuracy_score(labels, preds)
    sens = recall_score(labels, preds, average="macro", zero_division=0)
    return float(acc), float(sens)


def main():
    parser = argparse.ArgumentParser(description="P2.4 Robustez por perturbación")
    parser.add_argument("--data_dir", type=str, default="data")
    parser.add_argument("--limit", type=int, default=None, help="Nº de imágenes de test (default: todas).")
    parser.add_argument("--output_dir", type=str, default="outputs/results/robustness")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-center-crop", action="store_false", dest="center_crop",
                        help="Preprocesamiento legacy (Resize cuadrado). El default, center_crop, "
                             "es el de la receta modern con la que están entrenados los modelos.")
    parser.add_argument("--swin-ckpt", type=str, default=CKPT_SWIN, dest="swin_ckpt")
    parser.add_argument("--convnext-ckpt", type=str, default=CKPT_CONVNEXT, dest="convnext_ckpt")
    args = parser.parse_args()

    set_seed(args.seed)
    MODELS["Swin-Tiny"] = (SwinTinyClassifier, args.swin_ckpt)
    MODELS["ConvNeXt-Tiny"] = (ConvNeXtTinyClassifier, args.convnext_ckpt)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # La receta `modern` entrena y evalúa con Resize(256)+CenterCrop(224)
    # (src/training/recipes.py: random_resized_crop=True, y train_classifier.py pasa ese mismo
    # valor a get_val_transforms). Evaluar acá con center_crop=False aplicaba el preprocesamiento
    # legacy y hundía el baseline: Swin daba sens_macro 0.620 en lugar de 0.716.
    tf = get_val_transforms(size=224, center_crop=args.center_crop)

    splits = str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    ds = HAM10000Dataset(root_dir=str(Path(args.data_dir) / "processed" / "HAM10000"),
                         split="test", splits_file=splits, return_pil=True)
    n = len(ds) if args.limit is None else min(args.limit, len(ds))
    logger.info("Cargando %d imágenes de test en memoria...", n)
    pils, labels = [], []
    for i in range(n):
        s = ds[i]
        pils.append(s["image"].convert("RGB"))
        labels.append(int(s["label"]))

    summary = {}
    fig, axes = plt.subplots(1, len(MODELS), figsize=(6 * len(MODELS), 4.5), squeeze=False)
    for mi, (mname, (cls, ckpt)) in enumerate(MODELS.items()):
        if not Path(ckpt).exists():
            logger.warning("SKIP %s: no existe %s", mname, ckpt)
            continue
        model = _load_model(cls, ckpt, device)
        rng = np.random.default_rng(args.seed)
        base_acc, base_sens = _infer(model, pils, labels, "jpeg", 0, tf, device, rng)
        logger.info("%s baseline: acc=%.3f sens_macro=%.3f", mname, base_acc, base_sens)
        summary[mname] = {"baseline": {"acc": base_acc, "sens_macro": base_sens}, "curves": {}}

        ax = axes[0][mi]
        sevs = [0, 1, 2, 3, 4, 5]
        for kind in PERTURBATIONS:
            sens_curve = []
            for sev in sevs:
                if sev == 0:
                    sens_curve.append(base_sens)
                    continue
                _, sens = _infer(model, pils, labels, kind, sev, tf, device, rng)
                sens_curve.append(sens)
            summary[mname]["curves"][kind] = sens_curve
            ax.plot(sevs, sens_curve, marker="o", label=kind)
            logger.info("  %s / %-10s sens_macro: %s", mname, kind,
                        [round(s, 3) for s in sens_curve])
        ax.axhline(1 / 7, ls="--", color="gray", lw=1, label="azar (1/7)")
        ax.set_xlabel("Severidad (0 = sin perturbar)")
        ax.set_ylabel("Sensibilidad macro")
        ax.set_title(f"{mname} (baseline sens={base_sens:.2f})", fontsize=10)
        ax.set_ylim(0, max(0.9, base_sens + 0.05))
        ax.legend(fontsize=8)

    fig.suptitle("Robustez a perturbaciones de adquisición (HAM10000 test)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    png = out_dir / "robustness_curves.png"
    fig.savefig(png, dpi=150)
    logger.info("Figura: %s", png)

    salida = {"checkpoints": {k: v[1] for k, v in MODELS.items()},
              "split_test": "ham10000_splits.json (idéntico al test del split por lesión)",
              "preprocesamiento": ("Resize(256)+CenterCrop(224), igual que la receta modern"
                                   if args.center_crop else "Resize(224,224) legacy"),
              "protocolo": ("vista única, sin TTA: las tablas del documento son con TTA "
                            "(original+hflip), así que el baseline de acá queda algo por debajo; "
                            "lo que mide este análisis es la caída relativa"),
              "n_imagenes": n,
              "modelos": summary}
    (out_dir / "robustness_summary.json").write_text(
        __import__("json").dumps(salida, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resumen: %s", out_dir / "robustness_summary.json")


if __name__ == "__main__":
    main()
