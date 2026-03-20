import json
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image

from src.data.base_dataset import BaseDataset


class HIBADataset(BaseDataset):
    """Dataset HIBA para evaluación de sesgo por fototipo.

    Estructura real del dataset:
        root_dir/
        ├── metadata.csv     # 21 columnas: isic_id, diagnosis, fitzpatrick_skin_type, ...
        ├── images/          # 1616 imágenes .jpg (ISIC_XXXXXXX.jpg)
        ├── attribution.txt
        └── licenses/

    Columnas principales del metadata.csv:
        isic_id, age_approx, anatom_site_general, benign_malignant,
        diagnosis, diagnosis_1, diagnosis_2, diagnosis_3,
        fitzpatrick_skin_type, image_type, sex
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform=None,
        splits_file: Optional[str] = None,
    ):
        self.splits_file = splits_file
        self._class_names = []
        super().__init__(root_dir, split, transform)

    def _load_data(self):
        root = Path(self.root_dir)
        metadata_file = root / "metadata.csv"

        if not metadata_file.exists():
            raise FileNotFoundError(
                f"Metadata no encontrada: {metadata_file}. "
                "Asegurate de tener metadata.csv en el directorio del dataset."
            )

        df = pd.read_csv(metadata_file)

        # La columna de ID se llama "isic_id" en este dataset
        id_col = "isic_id" if "isic_id" in df.columns else "image_id"

        # Filtrar por split
        if self.splits_file and Path(self.splits_file).exists():
            with open(self.splits_file, encoding="utf-8") as f:
                splits = json.load(f)
            split_ids = set(splits[self.split])
            df = df[df[id_col].isin(split_ids)]

        # Construir mapeo de diagnósticos a índices
        unique_dx = sorted(df["diagnosis"].dropna().unique())
        self._class_names = unique_dx
        dx_to_label = {dx: i for i, dx in enumerate(unique_dx)}

        images_dir = root / "images"

        for _, row in df.iterrows():
            image_id = row[id_col]
            img_path = images_dir / f"{image_id}.jpg"
            if not img_path.exists():
                img_path = images_dir / f"{image_id}.png"
            if not img_path.exists():
                continue

            diagnosis = row.get("diagnosis", "")
            phototype = row.get("fitzpatrick_skin_type", "")
            if pd.isna(phototype):
                phototype = ""

            self.samples.append({
                "image_path": str(img_path),
                "label": dx_to_label.get(diagnosis, -1),
                "image_id": image_id,
                "diagnosis": diagnosis,
                "phototype": str(phototype),
                "benign_malignant": row.get("benign_malignant", ""),
                "age": row.get("age_approx", None),
                "sex": row.get("sex", ""),
                "anatom_site": row.get("anatom_site_general", ""),
                "image_type": row.get("image_type", ""),
            })

    def __getitem__(self, idx: int) -> dict:
        sample = self.samples[idx]
        image = self._open_image(sample["image_path"])

        if self.transform:
            image = self.transform(image)

        return {
            "image": image,
            "label": sample["label"],
            "metadata": {
                "image_id": sample["image_id"],
                "diagnosis": sample["diagnosis"],
                "phototype": sample["phototype"],
                "benign_malignant": sample["benign_malignant"],
                "age": sample["age"],
                "sex": sample["sex"],
                "anatom_site": sample["anatom_site"],
                "image_type": sample["image_type"],
            },
        }

    def get_class_names(self) -> list[str]:
        return self._class_names
