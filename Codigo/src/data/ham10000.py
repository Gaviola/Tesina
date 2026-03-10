import json
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image

from src.data.base_dataset import BaseDataset

# Mapeo de diagnósticos HAM10000 a índices
HAM10000_CLASSES = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
HAM10000_LABEL_MAP = {name: idx for idx, name in enumerate(HAM10000_CLASSES)}

# Nombres posibles para el archivo de metadata (sin extensión o con .csv)
_METADATA_NAMES = ["HAM10000_metadata.csv", "HAM10000_metadata"]

# Directorios donde buscar imágenes (el dataset viene dividido en 2 partes)
_IMAGE_DIRS = [
    "images",
    "HAM10000_images_part_1",
    "HAM10000_images_part_2",
]

# Test set del challenge ISIC 2018
_TEST_IMAGE_DIRS = [
    "ISIC2018_Task3_Test_Images/ISIC2018_Task3_Test_Images",
    "ISIC2018_Task3_Test_Images",
]
_TEST_GT_NAMES = ["ISIC2018_Task3_Test_GroundTruth.csv"]


class HAM10000Dataset(BaseDataset):
    """Dataset HAM10000 para clasificación de lesiones dermatoscópicas.

    Estructura real del dataset:
        root_dir/
        ├── HAM10000_metadata             # CSV sin extensión (o .csv)
        ├── HAM10000_images_part_1/       # ~5000 imágenes .jpg
        ├── HAM10000_images_part_2/       # ~5015 imágenes .jpg
        ├── ISIC2018_Task3_Test_GroundTruth.csv  # metadata del test set
        ├── ISIC2018_Task3_Test_Images/
        │   └── ISIC2018_Task3_Test_Images/      # ~1511 imágenes .jpg
        └── HAM10000_segmentations_lesion_tschandl/ (opcional)

    El archivo de splits (JSON) contiene: {"train": [...], "val": [...], "test": [...]}
    con listas de image_id. Si no hay splits, se usa todo el dataset.
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform=None,
        splits_file: Optional[str] = None,
        include_test_set: bool = False,
        return_pil: bool = False,
    ):
        self.splits_file = splits_file
        self.include_test_set = include_test_set
        self.return_pil = return_pil
        super().__init__(root_dir, split, transform)

    def _find_metadata(self, root: Path) -> Path:
        """Busca el archivo de metadata (con o sin extensión .csv)."""
        for name in _METADATA_NAMES:
            path = root / name
            if path.exists():
                return path
        raise FileNotFoundError(
            f"Metadata no encontrada en {root}. "
            f"Se buscó: {_METADATA_NAMES}. "
            "Asegurate de tener HAM10000_metadata en el directorio del dataset."
        )

    def _find_image_dirs(self, root: Path) -> list[Path]:
        """Encuentra todos los directorios que contienen imágenes."""
        dirs = []
        for dirname in _IMAGE_DIRS:
            path = root / dirname
            if path.exists():
                dirs.append(path)

        if self.include_test_set:
            for dirname in _TEST_IMAGE_DIRS:
                path = root / dirname
                if path.exists():
                    dirs.append(path)

        # Fallback: buscar en la raíz
        if not dirs:
            dirs.append(root)

        return dirs

    def _find_image(self, image_id: str, image_dirs: list[Path]) -> Optional[Path]:
        """Busca una imagen por su ID en múltiples directorios."""
        for d in image_dirs:
            for ext in [".jpg", ".png", ".jpeg"]:
                path = d / f"{image_id}{ext}"
                if path.exists():
                    return path
        return None

    def _load_data(self):
        root = Path(self.root_dir)

        # Cargar metadata principal
        metadata_file = self._find_metadata(root)
        df = pd.read_csv(metadata_file)

        # Opcionalmente agregar test set
        if self.include_test_set:
            for gt_name in _TEST_GT_NAMES:
                gt_file = root / gt_name
                if gt_file.exists():
                    test_df = pd.read_csv(gt_file)
                    # Unificar columnas si es necesario
                    if set(test_df.columns) == set(df.columns):
                        df = pd.concat([df, test_df], ignore_index=True)
                    break

        # Filtrar por split si existe archivo de splits
        if self.splits_file and Path(self.splits_file).exists():
            with open(self.splits_file, encoding="utf-8") as f:
                splits = json.load(f)
            split_ids = set(splits[self.split])
            df = df[df["image_id"].isin(split_ids)]

        # Encontrar directorios de imágenes
        image_dirs = self._find_image_dirs(root)

        for _, row in df.iterrows():
            image_id = row["image_id"]
            img_path = self._find_image(image_id, image_dirs)
            if img_path is None:
                continue

            dx = row["dx"].upper()
            label = HAM10000_LABEL_MAP.get(dx, -1)

            self.samples.append({
                "image_path": str(img_path),
                "label": label,
                "image_id": image_id,
                "dx": dx,
                "dx_type": row.get("dx_type", ""),
                "age": row.get("age", None),
                "sex": row.get("sex", ""),
                "localization": row.get("localization", ""),
            })

    def __getitem__(self, idx: int) -> dict:
        sample = self.samples[idx]
        image = Image.open(sample["image_path"]).convert("RGB")

        if not self.return_pil and self.transform:
            image = self.transform(image)

        return {
            "image": image,
            "label": sample["label"],
            "image_id": sample["image_id"],
            "metadata": {
                "dx": sample["dx"],
                "dx_type": sample["dx_type"],
                "age": sample["age"],
                "sex": sample["sex"],
                "localization": sample["localization"],
            },
        }

    def get_class_names(self) -> list[str]:
        return HAM10000_CLASSES
