"""P5.1 (soporte) — Re-evaluación con TTA guardando y_prob, para el ensamble justo.

Los predictions modern_v3 guardados eran single-view. Para comparar el ensamble de forma justa
contra el Swin headline (0.887, con TTA), se re-corren Swin y ConvNeXt con TTA (original+hflip)
y se guardan las probabilidades promediadas.

Local, RTX 4070. Uso:
    python scripts/reeval_tta_probs.py
"""

import json
import logging
import sys
from pathlib import Path

import torch
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.collators import ClassificationCollator
from src.data.ham10000 import HAM10000Dataset
from src.data.transforms import get_val_transforms
from src.evaluation.tta import evaluate_with_tta
from src.models.factory import build_model
from src.utils.device import get_device, get_training_dtype
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CKPTS = {
    "swin_tiny": "outputs/checkpoints/swin_tiny_modern_v3/best_model.pt",
    "convnext_tiny": "outputs/checkpoints/convnext_tiny_modern_v3/best_model.pt",
}
OUT_DIR = Path("outputs/results/classifier_ensemble")


def main():
    set_seed(42)
    device = get_device()
    dtype = get_training_dtype()
    splits_file = "data/splits/ham10000_splits.json"
    data_root = "data/processed/HAM10000"
    # modern_v3 usa RandomResizedCrop -> val/test con center_crop=True
    tfm = get_val_transforms(size=224, center_crop=True)
    # Genera probs con TTA para test Y validación (val -> fijar umbrales / calibración).
    splits = {
        "test": HAM10000Dataset(root_dir=data_root, split="test", transform=tfm, splits_file=splits_file),
        "val": HAM10000Dataset(root_dir=data_root, split="val", transform=tfm, splits_file=splits_file),
    }
    logger.info("device=%s dtype=%s | test=%d val=%d",
                device, dtype, len(splits["test"]), len(splits["val"]))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, ckpt_path in CKPTS.items():
        model = build_model({"name": name, "num_classes": 7})
        ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
        sd = ckpt.get("model_state_dict", ckpt)
        model.load_state_dict(sd, strict=True)
        model.to(device)
        for split, ds in splits.items():
            loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0,
                                collate_fn=ClassificationCollator())
            y_pred, y_true, y_prob = evaluate_with_tta(
                model, loader, device, dtype, num_classes=7, tta_modes=("original", "hflip"))
            out = {"model": name, "run_name": f"{name}_modern_v3_tta_{split}", "split": split,
                   "y_true": list(map(int, y_true)), "y_pred": list(map(int, y_pred)),
                   "y_prob": [list(map(float, r)) for r in y_prob]}
            suffix = "" if split == "test" else f"_{split}"
            (OUT_DIR / f"{name}_tta{suffix}_predictions.json").write_text(
                json.dumps(out, ensure_ascii=False), encoding="utf-8")
            from sklearn.metrics import balanced_accuracy_score
            logger.info("%s [%s] TTA sens_macro=%.3f (guardado)", name, split,
                        balanced_accuracy_score(y_true, y_pred))
        del model
        if device.type == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
