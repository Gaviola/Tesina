import json
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image

from src.data.base_dataset import BaseDataset


def _strip_dataset_prefix(path_str: str) -> str:
    """Elimina el prefijo 'dataset/' de los paths en los CSV del dataset."""
    if path_str.startswith("dataset/"):
        return path_str[len("dataset/"):]
    return path_str


class MMSkinDataset(BaseDataset):
    """Dataset MM-Skin (MM-SkinQA) para evaluación multimodal (caption + VQA).

    Estructura real del dataset:
        root_dir/
        ├── caption.csv    # columnas: image, caption, modality, sex, age, cleaned_caption
        ├── VQA.csv        # columnas: image, question, answer
        └── *.png          # ~11002 imágenes sueltas en la raíz (bkN_*.png)

    Notas:
    - Los paths en los CSV tienen prefijo 'dataset/' que se stripea automáticamente.
    - Las imágenes están directamente en root_dir, no en un subdirectorio 'images/'.
    - caption.csv tiene ~11090 filas (algunas imágenes tienen múltiples captions).
    - VQA.csv tiene ~27259 filas (~2.95 preguntas por imagen).
    """

    def __init__(
        self,
        root_dir: str,
        split: str = "train",
        transform=None,
        splits_file: Optional[str] = None,
        mode: str = "caption",  # "caption" | "vqa" | "both"
    ):
        self.splits_file = splits_file
        self.mode = mode
        super().__init__(root_dir, split, transform)

    def _load_data(self):
        root = Path(self.root_dir)

        # Cargar captions
        captions_by_image = {}
        caption_file = root / "caption.csv"
        if caption_file.exists():
            caption_df = pd.read_csv(caption_file)
            for _, row in caption_df.iterrows():
                img_name = _strip_dataset_prefix(str(row.get("image", "")))
                caption = row.get("caption", "")
                cleaned = row.get("cleaned_caption", "")
                caption = str(caption) if pd.notna(caption) else ""
                cleaned = str(cleaned) if pd.notna(cleaned) else ""
                modality = row.get("modality", "")
                if img_name not in captions_by_image:
                    captions_by_image[img_name] = {
                        "captions": [],
                        "modality": modality,
                        "sex": row.get("sex", ""),
                        "age": row.get("age", ""),
                    }
                # Preferir cleaned_caption si existe
                text = cleaned if cleaned else caption
                captions_by_image[img_name]["captions"].append(text)

        # Cargar VQA
        vqa_by_image = {}
        vqa_file = root / "VQA.csv"
        if vqa_file.exists():
            vqa_df = pd.read_csv(vqa_file)
            for _, row in vqa_df.iterrows():
                img_name = _strip_dataset_prefix(str(row.get("image", "")))
                if img_name not in vqa_by_image:
                    vqa_by_image[img_name] = []
                vqa_by_image[img_name].append({
                    "question": row.get("question", ""),
                    "answer": row.get("answer", ""),
                })

        # Construir lista de imágenes según modo
        if self.mode == "caption":
            image_names = set(captions_by_image.keys())
        elif self.mode == "vqa":
            image_names = set(vqa_by_image.keys())
        else:  # both
            image_names = set(captions_by_image.keys()) | set(vqa_by_image.keys())

        # Filtrar por split
        if self.splits_file and Path(self.splits_file).exists():
            with open(self.splits_file, encoding="utf-8") as f:
                splits = json.load(f)
            split_ids = set(splits[self.split])
            image_names = image_names & split_ids

        for img_name in sorted(image_names):
            # Las imágenes están en la raíz del directorio
            img_path = root / img_name
            if not img_path.exists():
                continue

            cap_data = captions_by_image.get(img_name, {})
            captions = cap_data.get("captions", [])

            self.samples.append({
                "image_path": str(img_path),
                "label": -1,
                "image_id": img_name,
                "caption": captions[0] if captions else "",
                "all_captions": captions,
                "qa_pairs": vqa_by_image.get(img_name, []),
                "modality": cap_data.get("modality", ""),
            })

    def __getitem__(self, idx: int) -> dict:
        sample = self.samples[idx]
        image = Image.open(sample["image_path"]).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return {
            "image": image,
            "label": sample["label"],
            "text": sample["caption"],
            "qa_pairs": sample["qa_pairs"],
            "metadata": {
                "image_id": sample["image_id"],
                "modality": sample["modality"],
                "num_captions": len(sample["all_captions"]),
                "num_qa_pairs": len(sample["qa_pairs"]),
            },
        }

    def get_class_names(self) -> list[str]:
        return []
