"""P2.4 / S6-E2 — Figura ilustrativa de las perturbaciones de robustez.

Muestra VARIOS ejemplos (no una sola imagen) degradados en los 5 niveles de cada perturbación
(JPEG, ruido, blur, resolución), con la predicción de Swin-Tiny por panel. Las imágenes se eligen
de forma que el patrón de fallo (primera severidad en la que la predicción se vuelve incorrecta)
sea representativo de la tendencia agregada de `fig:robustez`: Ruido y JPEG fallan antes
que Desenfoque y Resolución. Solo se aceptan ejemplos que efectivamente exhiben esa tendencia
(ruido o JPEG fallan dentro de sev1-5, y antes que desenfoque/resolución). Local (CPU si no hay GPU).

Uso:
    python scripts/robustness_examples.py                    # elige N imágenes automáticamente
    python scripts/robustness_examples.py --image_ids ISIC_0034524 ISIC_0031234
    python scripts/robustness_examples.py --n_examples 3
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
FAST_KINDS = {"noise", "jpeg"}  # tendencia agregada (fig:robustez): fallan antes
SLOW_KINDS = {"resolution", "blur"}  # más tolerados


@torch.no_grad()
def _predict(model, pil, tf, device):
    x = tf(pil).unsqueeze(0).to(device)
    return int(model(x).argmax(1).item())


def _first_fail_severity(model, pil, gt, tf, device, kind, levels, rng):
    """Menor severidad (1-5) en la que la predicción deja de ser correcta; None si nunca falla."""
    for sev in range(1, 6):
        img = _perturb(pil, kind, sev, rng)
        if _predict(model, img, tf, device) != gt:
            return sev
    return None


def _trend_score(first_fail: dict) -> float:
    """Menor es mejor: fast_kinds deben fallar antes (severidad más baja) que slow_kinds."""
    def val(kind):
        v = first_fail.get(kind)
        return v if v is not None else 6  # nunca falla = "sobrevive todo"
    fast_min = min(val(k) for k in FAST_KINDS)
    slow_min = min(val(k) for k in SLOW_KINDS)
    return fast_min - slow_min  # negativo = fast falla antes (deseado)


def _exhibits_trend(first_fail: dict) -> bool:
    """True si el ejemplo cumple el caption por-ejemplo: TANTO ruido como JPEG fallan dentro de
    sev1-5 y ambos antes que desenfoque y resolucion (la primera falla de cualquier `fast`
    ocurre a severidad menor que la primera falla de cualquier `slow`)."""
    def val(kind):
        v = first_fail.get(kind)
        return v if v is not None else 6
    fast_max = max(val(k) for k in FAST_KINDS)   # ambos fast deben fallar (y lo antes posible)
    slow_min = min(val(k) for k in SLOW_KINDS)   # ninguna slow debe fallar antes que las fast
    return fast_max < slow_min


def _select_examples(ds, model, tf, device, rng, n_examples, explicit_ids=None, max_scan=400):
    """Elige n_examples imágenes correctamente clasificadas cuyo patrón de fallo por-perturbación
    exhibe la tendencia agregada (ruido/JPEG fallan antes que desenfoque/resolución). Para el modo
    automático se descartan las que no la exhiben; para --image_ids se muestran las pedidas tal cual."""
    candidates = []
    scanned = 0
    pool_target = max(6, n_examples * 3)  # basta un pool chico para elegir los mejores sin escanear todo
    for i in range(len(ds)):
        s = ds[i]
        iid = s["image_id"]
        if explicit_ids and iid not in explicit_ids:
            continue
        pil = s["image"].convert("RGB")
        gt = int(s["label"])
        if _predict(model, pil, tf, device) != gt:
            continue
        first_fail = {kind: _first_fail_severity(model, pil, gt, tf, device, kind, levels, rng)
                      for kind, _, levels in PERTURBS}
        score = _trend_score(first_fail)
        # En modo automático, solo aceptar ejemplos que realmente exhiben la tendencia.
        if not explicit_ids and not _exhibits_trend(first_fail):
            scanned += 1
            if scanned >= max_scan:
                break
            continue
        candidates.append((score, iid, pil, gt, first_fail))
        scanned += 1
        if not explicit_ids and (len(candidates) >= pool_target or scanned >= max_scan):
            break
        if explicit_ids and len(candidates) >= len(explicit_ids):
            break

    if not candidates:
        raise RuntimeError("No se encontraron imágenes candidatas que exhiban la tendencia agregada.")

    candidates.sort(key=lambda c: c[0])  # score más negativo = mejor alineado con la tendencia
    picked = candidates[:n_examples] if not explicit_ids else candidates
    for score, iid, _, gt, ff in picked:
        logger.info("Elegida %s (gt=%s, score=%+d, first_fail=%s)",
                    iid, HAM10000_CLASSES[gt], score, ff)
    return picked


def main():
    parser = argparse.ArgumentParser(description="Figura ilustrativa de perturbaciones (multi-ejemplo)")
    parser.add_argument("--image_ids", type=str, nargs="*", default=None)
    parser.add_argument("--n_examples", type=int, default=2)
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

    explicit_ids = set(args.image_ids) if args.image_ids else None
    picked = _select_examples(ds, model, tf, device, rng, args.n_examples, explicit_ids)

    n_cols = 6  # original + 5 severidades
    n_rows = len(PERTURBS) * len(picked)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(2.0 * n_cols, 2.15 * n_rows), squeeze=False)

    for ex_idx, (score, iid, pil, gt, first_fail) in enumerate(picked):
        for p_idx, (kind, label, levels) in enumerate(PERTURBS):
            r = ex_idx * len(PERTURBS) + p_idx
            for c in range(n_cols):
                ax = axes[r][c]; ax.axis("off")
                sev = c
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
            axes[r][0].text(-0.18, 0.5, f"{label}\n[{iid}]" if p_idx == 0 else label,
                            transform=axes[r][0].transAxes, rotation=90,
                            va="center", ha="center", fontsize=9, fontweight="bold")

    fig.suptitle("Impacto de las perturbaciones en " + str(len(picked)) + " ejemplos "
                 "(Swin-Tiny). Verde = predicción correcta, rojo = incorrecta. Consistente con la "
                 "tendencia agregada: Ruido y JPEG degradan la predicción antes que "
                 "Desenfoque y Resolución.", fontsize=10)
    fig.tight_layout(rect=[0.02, 0, 1, 0.96])
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    logger.info("Figura: %s", out)


if __name__ == "__main__":
    main()
