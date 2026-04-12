import json
from pathlib import Path
from typing import Optional

import pandas as pd

from src.data.base_dataset import BaseDataset


class SkinCaReDataset(BaseDataset):
    """Dataset SkinCaRe para generación de reportes clínicos.

    Soporta dos subsets del repositorio HuggingFace yuhos16/SkinCaRe
    descargado localmente con snapshot_download:

    subset="skincap"  — ~4,000 pares imagen-caption (alineamiento visual, Stage 1)
        root_dir/
        └── SkinCAP/
            ├── skincap_v240715.xlsx   # id, disease, caption_zh, caption_en, source
            └── skincap/
                ├── not_include/       # imágenes excluidas (se ignoran)
                └── *.png              # imágenes del dataset

    subset="skincot"  — 3,041 pares imagen-CoT EN (fine-tuning instrucciones, Stage 2)
        root_dir/
        └── SkinCoT/
            ├── EN/
            │   └── <disease_class>/
            │       └── <image_id>.jpg.txt   # texto CoT en inglés
            └── images/
                └── <disease_class>/
                    └── <image_id>.jpg

    Splits:
        Se esperan archivos JSON en splits_file con {"train": [...], "val": [...], "test": [...]}.
        Los IDs son el campo "id" del XLSX (SkinCAP) o el stem del archivo .txt (SkinCoT).
        Si no se pasa splits_file, se usan todas las muestras disponibles.
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform=None,
        splits_file: Optional[str] = None,
        subset: str = "skincap",  # "skincap" | "skincot"
    ):
        if subset not in ("skincap", "skincot"):
            raise ValueError(f"subset debe ser 'skincap' o 'skincot', recibido: '{subset}'")
        self.splits_file = splits_file
        self.subset = subset
        super().__init__(root_dir, split, transform)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_split_ids(self) -> Optional[set]:
        """Carga los IDs del split indicado. Devuelve None si no hay splits_file."""
        if not self.splits_file:
            return None
        splits_path = Path(self.splits_file)
        if not splits_path.exists():
            return None
        with open(splits_path, encoding="utf-8") as f:
            splits = json.load(f)
        return set(splits.get(self.split, []))

    # ------------------------------------------------------------------
    # Carga por subset
    # ------------------------------------------------------------------

    def _load_skincap(self):
        """Carga SkinCAP desde el XLSX y las imágenes planas en SkinCAP/skincap/."""
        root = Path(self.root_dir)
        xlsx_path = root / "SkinCAP" / "skincap_v240715.xlsx"
        if not xlsx_path.exists():
            raise FileNotFoundError(
                f"Metadata SkinCAP no encontrada: {xlsx_path}\n"
                "Descargá el dataset con: python scripts/prepare_data.py --download-skincare"
            )

        # header=1: la fila 0 es un título ("skincap_v240715"), los headers reales están en fila 1
        df = pd.read_excel(xlsx_path, engine="openpyxl", header=1)
        # Excluir imágenes marcadas como "Do not consider this image"
        if "Do not consider this image" in df.columns:
            df = df[df["Do not consider this image"] != 1]

        images_dir = root / "SkinCAP" / "skincap"
        not_include_dir = images_dir / "not_include"

        split_ids = self._load_split_ids()

        for _, row in df.iterrows():
            # skincap_file_path es el nombre real del archivo (e.g. "1.png")
            img_filename = str(row.get("skincap_file_path", "")).strip()
            caption_en = str(row.get("caption_en", "")).strip()
            disease = str(row.get("disease", "")).strip()
            img_id = Path(img_filename).stem  # "1.png" → "1"

            if not img_filename or not caption_en:
                continue

            # Filtrar por split (IDs son skincap_file_path, e.g. "1.png")
            if split_ids is not None and img_filename not in split_ids:
                continue

            # Buscar imagen directamente por nombre de archivo
            img_path = images_dir / img_filename
            if not img_path.exists() or not_include_dir in img_path.parents:
                img_path = None

            if img_path is None:
                continue

            self.samples.append({
                "image_path": str(img_path),
                "label": -1,
                "image_id": img_filename,  # e.g. "1.png" — consistente con splits
                "text": caption_en,
                "disease": disease,
                "source": "skincap",
            })

    def _load_skincot(self):
        """Carga SkinCoT EN desde los .txt organizados por clase y las imágenes correspondientes."""
        root = Path(self.root_dir)
        en_dir = root / "SkinCoT" / "EN"
        images_dir = root / "SkinCoT" / "images"

        if not en_dir.exists():
            raise FileNotFoundError(
                f"Directorio SkinCoT/EN no encontrado: {en_dir}\n"
                "Descargá el dataset con: python scripts/prepare_data.py --download-skincare"
            )

        split_ids = self._load_split_ids()

        for txt_file in sorted(en_dir.rglob("*.txt")):
            # Estructura: EN/<disease_class>/<image_id>.jpg.txt
            disease_class = txt_file.parent.name
            # image_id es el stem sin el .jpg final: "ISIC_0024306.jpg" → "ISIC_0024306"
            img_filename = txt_file.stem  # e.g. "ISIC_0024306.jpg"
            img_id = Path(img_filename).stem  # e.g. "ISIC_0024306"

            if split_ids is not None and img_id not in split_ids:
                continue

            # Buscar imagen en SkinCoT/images/<disease_class>/
            img_path = images_dir / disease_class / img_filename
            if not img_path.exists():
                # Fallback: buscar sin extensión implícita
                img_path = images_dir / disease_class / f"{img_id}.jpg"
            if not img_path.exists():
                continue

            cot_text = txt_file.read_text(encoding="utf-8").strip()
            if not cot_text:
                continue

            self.samples.append({
                "image_path": str(img_path),
                "label": -1,
                "image_id": img_id,
                "text": cot_text,
                "disease": disease_class,
                "source": "skincot",
            })

    # ------------------------------------------------------------------
    # BaseDataset interface
    # ------------------------------------------------------------------

    def _load_data(self):
        if self.subset == "skincap":
            self._load_skincap()
        else:
            self._load_skincot()

    def __getitem__(self, idx: int) -> dict:
        sample = self.samples[idx]
        image = self._open_image(sample["image_path"])

        if self.transform:
            image = self.transform(image)

        return {
            "image": image,
            "label": sample["label"],
            "text": sample["text"],
            "metadata": {
                "image_id": sample["image_id"],
                "disease": sample["disease"],
                "source": sample["source"],
            },
        }

    def get_class_names(self) -> list[str]:
        return []  # dataset de generación, no clasificación
