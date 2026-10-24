"""DermLIP zero-shot con las plantillas y los nombres de clase oficiales de Derm1M frente a los de este trabajo.

Plan: docs/ideas/dermlip_zs_protocolo_plan_20261024.md. Calcula los embeddings de imagen de la prueba por lesión una
sola vez y los compara con cuatro clasificadores de texto (plantillas × nombres). La combinación propia reproduce
dermlip_zeroshot_vit-b-16_predictions.json como control.

Uso (desde Codigo/):
    ../.venv/Scripts/python.exe scripts/dermlip_zs_protocolo.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, recall_score

from src.data.ham10000 import HAM10000_CLASSES, HAM10000Dataset
from src.models.dermlip import DEFAULT_TEMPLATES, DermLIPClassifier

# Orden de HAM10000_CLASSES: MEL, NV, BCC, AKIEC, BKL, DF, VASC
NOMBRES_PROPIOS = ["melanoma", "melanocytic nevus", "basal cell carcinoma", "actinic keratosis", "benign keratosis",
                   "dermatofibroma", "vascular lesion"]
# HAM_CLASSNAMES de Derm1M (src/open_clip/zero_shot_metadata.py), reordenados al orden de HAM10000_CLASSES
NOMBRES_OFICIALES = ["melanoma", "nevus", "basal cell carcinoma", "actinic keratosis", "benign keratosis",
                     "dermatofibroma", "vascular"]
# OPENAI_SKIN_TEMPLATES de Derm1M
PLANTILLAS_OFICIALES = (
    "This is a skin image of {c}",
    "This is a skin image of {c}.",
    "A skin image of {c}.",
    "An image of {c}, a skin condition.",
    "{c}, a skin disorder, is shown in this image.",
    "The skin lesion depicted is {c}.",
    "The skin cancer in this image is {c}.",
    "This image depicts {c}, a type of skin cancer.",
)


def main():
    torch.manual_seed(42)
    model = DermLIPClassifier(checkpoint="vit-b-16")
    ds = HAM10000Dataset(root_dir="data/processed/HAM10000", split="test",
                         splits_file="data/splits/ham10000_splits.json", return_pil=True)
    feats, y = [], []
    lote = []
    for i in range(len(ds)):
        s = ds[i]
        lote.append(s["image"])
        y.append(int(s["label"]))
        if len(lote) == 64 or i == len(ds) - 1:
            feats.append(model.embed_images(lote))
            lote = []
    img = torch.cat(feats)
    y = np.array(y)
    print(f"{len(y)} imágenes")

    out = {"n": int(len(y)), "combinaciones": {}}
    for et_p, plant in (("propias", DEFAULT_TEMPLATES), ("oficiales", PLANTILLAS_OFICIALES)):
        for et_n, nombres in (("propios", NOMBRES_PROPIOS), ("oficiales", NOMBRES_OFICIALES)):
            txt = model._encode_text_per_class(nombres, plant).float().cpu()
            pred = (100.0 * img @ txt.T).argmax(1).numpy()
            cuenta = Counter(pred.tolist())
            k, v = cuenta.most_common(1)[0]
            r = {"exactitud": accuracy_score(y, pred),
                 "sens_macro": recall_score(y, pred, labels=range(7), average="macro", zero_division=0),
                 "f1_macro": f1_score(y, pred, labels=range(7), average="macro", zero_division=0),
                 "sens_por_clase": recall_score(y, pred, labels=range(7), average=None, zero_division=0).tolist(),
                 "clase_mas_predicha": [HAM10000_CLASSES[k], v / len(y)]}
            clave = f"plantillas_{et_p}__nombres_{et_n}"
            out["combinaciones"][clave] = r
            print(f"{clave}: exactitud {r['exactitud']:.3f}, sens. macro {r['sens_macro']:.3f}, "
                  f"F1 macro {r['f1_macro']:.3f}, más predicha {r['clase_mas_predicha'][0]} "
                  f"({r['clase_mas_predicha'][1]:.3f})")
    dest = Path("outputs/results/dermlip/dermlip_zs_protocolo.json")
    assert not dest.exists(), f"{dest} ya existe: no se sobrescribe"
    dest.write_text(json.dumps(out, indent=2), encoding="utf8")
    print(f"Guardado en {dest}")


if __name__ == "__main__":
    main()
