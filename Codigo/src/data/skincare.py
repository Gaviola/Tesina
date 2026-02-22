import json
from pathlib import Path
from typing import Optional

from PIL import Image

from src.data.base_dataset import BaseDataset


class SkinCaReDataset(BaseDataset):
    """Dataset SkinCaRe (SkinCAP + SkinCoT) para generación de reportes clínicos.

    Estructura esperada en root_dir:
        root_dir/
        ├── images/          # imágenes
        └── annotations.json # lista de {"image": "filename", "caption": "...", "report": "...", "source": "skincap|skincot"}

    El campo "caption" contiene descripciones cortas (SkinCAP).
    El campo "report" contiene reportes CoT estructurados (SkinCoT).
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform=None,
        splits_file: Optional[str] = None,
        subset: Optional[str] = None,  # "skincap" | "skincot" | None (ambos)
    ):
        self.splits_file = splits_file
        self.subset = subset
        super().__init__(root_dir, split, transform)

    def _load_data(self):
        root = Path(self.root_dir)
        annotations_file = root / "annotations.json"

        if not annotations_file.exists():
            raise FileNotFoundError(
                f"Anotaciones no encontradas: {annotations_file}. "
                "Asegurate de tener annotations.json en el directorio del dataset."
            )

        with open(annotations_file, encoding="utf-8") as f:
            annotations = json.load(f)

        # Filtrar por split
        if self.splits_file and Path(self.splits_file).exists():
            with open(self.splits_file, encoding="utf-8") as f:
                splits = json.load(f)
            split_ids = set(splits[self.split])
            annotations = [a for a in annotations if a.get("image", a.get("image_id", "")) in split_ids]

        # Filtrar por subset si se especifica
        if self.subset:
            annotations = [a for a in annotations if a.get("source", "") == self.subset]

        images_dir = root / "images"

        for ann in annotations:
            img_name = ann.get("image", ann.get("image_id", ""))
            img_path = images_dir / img_name
            if not img_path.exists():
                continue

            self.samples.append({
                "image_path": str(img_path),
                "label": -1,  # no hay clasificación en este dataset
                "caption": ann.get("caption", ""),
                "report": ann.get("report", ""),
                "source": ann.get("source", ""),
                "image_id": img_name,
            })

    def __getitem__(self, idx: int) -> dict:
        sample = self.samples[idx]
        image = Image.open(sample["image_path"]).convert("RGB")

        if self.transform:
            image = self.transform(image)

        text = sample["report"] if sample["report"] else sample["caption"]

        return {
            "image": image,
            "label": sample["label"],
            "text": text,
            "caption": sample["caption"],
            "report": sample["report"],
            "metadata": {
                "source": sample["source"],
                "image_id": sample["image_id"],
            },
        }

    def get_class_names(self) -> list[str]:
        return []  # dataset de generación, no clasificación
