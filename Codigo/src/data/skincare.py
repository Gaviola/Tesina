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

    def _resolve_root(self) -> Path:
        """Resuelve la raíz real del dataset, tolerando un subdirectorio 'skincare/' extra.

        snapshot_download a veces crea root_dir/skincare/{SkinCAP,SkinCoT} en vez de
        root_dir/{SkinCAP,SkinCoT}. Se prueba la ruta directa primero; si no existe,
        se intenta con el subdirectorio extra.
        """
        root = Path(self.root_dir)
        anchor = "SkinCAP" if self.subset == "skincap" else "SkinCoT"
        if (root / anchor).exists():
            return root
        nested = root / "skincare"
        if (nested / anchor).exists():
            return nested
        return root  # dejar que falle con el path original para el mensaje de error correcto

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
        root = self._resolve_root()
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
        root = self._resolve_root()
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


# ----------------------------------------------------------------------------
# Adaptador: SkinCAP como clasificación de 7 clases HAM (confirmación domain gap)
# ----------------------------------------------------------------------------

# Mapeo CURADO de las etiquetas finas de SkinCAP (foto clínica) a las 7 clases de
# HAM10000. Listas explícitas (NO substring) para evitar falsos positivos:
#   - 'epidermal-nevus'/'nevus sebaceous' NO son nv melanocítico.
#   - 'porokeratosis actinic' NO es akiec.
#   - 'seborrheic dermatitis' NO es bkl.
#   - SCC invasivo no tiene clase HAM equivalente (solo SCC in-situ = Bowen → akiec).
# Las claves se comparan en minúsculas (.strip().lower()).
SKINCAP_TO_HAM = {
    # NV — nevos melanocíticos benignos comunes
    "melanocytic-nevi": "NV", "nevocytic nevus": "NV", "congenital nevus": "NV",
    "halo nevus": "NV", "blue-nevus": "NV",
    # MEL — melanoma (todas las variantes)
    "malignant melanoma": "MEL", "melanoma": "MEL", "melanoma-acral-lentiginous": "MEL",
    "melanoma-in-situ": "MEL", "nodular-melanoma-(nm)": "MEL",
    "superficial spreading melanoma ssm": "MEL",
    # BCC — carcinoma basocelular
    "basal cell carcinoma": "BCC", "basal cell carcinoma morpheiform": "BCC",
    "solid cystic basal cell carcinoma": "BCC",
    # AKIEC — queratosis actínica + carcinoma intraepitelial (Bowen = SCC in-situ)
    "actinic keratosis": "AKIEC", "actinic-keratosis": "AKIEC",
    "squamous-cell-carcinoma-in-situ": "AKIEC",
    # BKL — queratosis benignas (seborreica, lichenoide)
    "seborrheic keratosis": "BKL", "seborrheic-keratosis": "BKL",
    "seborrheic-keratosis-irritated": "BKL", "benign-keratosis": "BKL",
    "lichenoid-keratosis": "BKL",
    # DF — dermatofibroma
    "dermatofibroma": "DF",
    # VASC — lesiones vasculares (angiomas, granuloma piógeno)
    "angioma": "VASC", "arteriovenous-hemangioma": "VASC", "glomangioma": "VASC",
    "pyogenic granuloma": "VASC", "granuloma pyogenic": "VASC", "pyogenic-granuloma": "VASC",
}


class SkinCAPClassificationDataset:
    """SkinCAP (foto clínica) como tarea de clasificación de 7 clases HAM, para zero-shot.

    Adaptador para confirmar el domain gap (dermatoscopía vs foto clínica): corre la MISMA
    clasificación de 7 clases que `HAM10000Dataset` pero sobre fotos clínicas. Reusa
    `SkinCaReDataset(subset='skincap')` y filtra/remapea las etiquetas finas de SkinCAP a las
    7 clases HAM vía `SKINCAP_TO_HAM` (las no mapeables se descartan).

    `__getitem__` respeta el mismo contrato que `HAM10000Dataset(return_pil=True)` consumido por
    `train_vlm_classify.py` / `score_image`:
        {"image": PIL, "label": int(0..6), "image_id": str, "metadata": {...}}

    Args:
        root_dir: raíz de SkinCaRe (la misma que usa SkinCaReDataset, e.g. data/raw/skincare).
        splits_file: opcional. Solo se aplica si `split` no es None.
        split: "train"|"val"|"test" para filtrar, o None para usar TODO SkinCAP (recomendado en
            zero-shot: maximiza n por clase y no hay circularidad porque el modelo es base).
        transform: transform opcional (los VLMs usan PIL crudo, dejar None).
    """

    def __init__(self, root_dir, splits_file=None, split=None, transform=None):
        from src.data.ham10000 import HAM10000_LABEL_MAP

        self._base = SkinCaReDataset(
            root_dir=root_dir,
            split=split or "train",
            transform=transform,
            splits_file=splits_file if split else None,
            subset="skincap",
        )
        self.items = []
        for s in self._base.samples:
            ham = SKINCAP_TO_HAM.get(str(s.get("disease", "")).strip().lower())
            if ham is None:
                continue
            self.items.append({
                "image_path": s["image_path"],
                "label": HAM10000_LABEL_MAP[ham],
                "image_id": s["image_id"],
                "disease": s["disease"],
                "ham_class": ham,
            })

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, idx: int) -> dict:
        it = self.items[idx]
        image = self._base._open_image(it["image_path"])
        if self._base.transform:
            image = self._base.transform(image)
        return {
            "image": image,
            "label": it["label"],
            "image_id": it["image_id"],
            "metadata": {
                "image_id": it["image_id"],
                "disease": it["disease"],
                "ham_class": it["ham_class"],
                "source": "skincap",
            },
        }

    def class_distribution(self) -> dict:
        """Histograma {clase_HAM: n} de las muestras incluidas (para sanity check)."""
        from collections import Counter
        return dict(Counter(it["ham_class"] for it in self.items))
