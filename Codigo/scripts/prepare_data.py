"""Fase 0: Preparación de datos.

Preprocesamiento, generación de splits y estadísticas básicas.

Uso:
    python scripts/prepare_data.py --data_dir data --seed 42 --image_size 224
"""

import argparse
import json
import logging
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.utils.seed import set_seed

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

# Constantes
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
IMAGE_SIZE = 224
RANDOM_SEED = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def verify_dataset_exists(dataset_name: str, raw_dir: Path) -> bool:
    """Verifica que el directorio del dataset raw existe y no está vacío."""
    if not raw_dir.exists():
        logger.warning("Dataset '%s' no encontrado en %s", dataset_name, raw_dir)
        return False
    files = list(raw_dir.iterdir())
    if not files:
        logger.warning("Dataset '%s' está vacío: %s", dataset_name, raw_dir)
        return False
    logger.info("Dataset '%s' encontrado: %d archivos/carpetas", dataset_name, len(files))
    return True


def _find_image_files(directory: Path) -> list[Path]:
    """Encuentra archivos de imagen recursivamente, ignorando __MACOSX."""
    results = []
    for f in directory.rglob("*"):
        if "__MACOSX" in str(f):
            continue
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:
            results.append(f)
    return results


def _find_ham10000_image_dirs(raw_dir: Path) -> list[Path]:
    """Encuentra los directorios de imágenes de HAM10000 (part_1 + part_2 o images/)."""
    dirs = []
    for name in ["HAM10000_images_part_1", "HAM10000_images_part_2", "images"]:
        d = raw_dir / name
        if d.exists():
            dirs.append(d)
    if not dirs:
        dirs.append(raw_dir)
    return dirs


def _find_ham10000_metadata(raw_dir: Path) -> Path | None:
    """Busca el archivo de metadata de HAM10000 (con o sin extensión .csv)."""
    for name in ["HAM10000_metadata.csv", "HAM10000_metadata"]:
        p = raw_dir / name
        if p.exists():
            return p
    return None


def preprocess_images_ham10000(raw_dir: Path, processed_dir: Path, size: int = IMAGE_SIZE):
    """Preprocesa imágenes HAM10000 desde múltiples directorios."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    image_dirs = _find_ham10000_image_dirs(raw_dir)
    count = 0

    for img_dir in image_dirs:
        for img_path in img_dir.iterdir():
            if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            try:
                img = Image.open(img_path).convert("RGB")
                img = img.resize((size, size), Image.LANCZOS)
                output_path = processed_dir / img_path.name
                img.save(output_path, quality=95)
                count += 1
            except Exception as e:
                logger.warning("Error procesando %s: %s", img_path.name, e)

    logger.info("HAM10000: preprocesadas %d imágenes → %s", count, processed_dir)
    return count


def preprocess_images_generic(raw_dir: Path, processed_dir: Path, size: int = IMAGE_SIZE):
    """Preprocesa imágenes buscando en images/ o en la raíz del directorio."""
    processed_dir.mkdir(parents=True, exist_ok=True)
    images_dir = raw_dir / "images" if (raw_dir / "images").exists() else raw_dir

    count = 0
    for img_path in images_dir.iterdir():
        if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            img = Image.open(img_path).convert("RGB")
            img = img.resize((size, size), Image.LANCZOS)
            output_path = processed_dir / img_path.name
            img.save(output_path, quality=95)
            count += 1
        except Exception as e:
            logger.warning("Error procesando %s: %s", img_path.name, e)

    logger.info("Preprocesadas %d imágenes → %s", count, processed_dir)
    return count


def _safe_stratified_split(ids, labels, test_size: float, random_state: int, context: str = ""):
    """Split estratificado con fallback aleatorio si alguna clase tiene < 2 miembros en el subconjunto."""
    try:
        return train_test_split(
            ids, labels,
            test_size=test_size,
            stratify=labels,
            random_state=random_state,
        )
    except ValueError as e:
        logger.warning(
            "Split estratificado falló%s: %s. Usando split aleatorio sin estratificación.",
            f" ({context})" if context else "",
            str(e).split("\n")[0],
        )
        return train_test_split(
            ids, labels,
            test_size=test_size,
            stratify=None,
            random_state=random_state,
        )


def generate_splits_ham10000(raw_dir: Path, splits_dir: Path, seed: int = RANDOM_SEED):
    """Genera splits estratificados para HAM10000."""
    metadata_file = _find_ham10000_metadata(raw_dir)
    if metadata_file is None:
        logger.error("HAM10000_metadata no encontrado en %s", raw_dir)
        return

    df = pd.read_csv(metadata_file)
    logger.info("HAM10000: %d samples, %d diagnósticos únicos", len(df), df["dx"].nunique())
    logger.info("  Distribución: %s", df["dx"].value_counts().to_dict())

    # Split estratificado por diagnóstico
    # .to_numpy() garantiza numpy.ndarray independientemente del backend (PyArrow, etc.)
    image_ids = df["image_id"].to_numpy()
    labels = df["dx"].to_numpy()

    train_ids, temp_ids, train_labels, temp_labels = train_test_split(
        image_ids, labels,
        test_size=(SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"]),
        stratify=labels,
        random_state=seed,
    )

    val_ratio = SPLIT_RATIOS["val"] / (SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"])
    val_ids, test_ids, _, _ = _safe_stratified_split(
        temp_ids, temp_labels,
        test_size=(1 - val_ratio),
        random_state=seed,
        context="HAM10000 val/test",
    )

    splits = {
        "train": train_ids.tolist(),
        "val": val_ids.tolist(),
        "test": test_ids.tolist(),
    }

    splits_dir.mkdir(parents=True, exist_ok=True)
    splits_file = splits_dir / "ham10000_splits.json"
    with open(splits_file, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    logger.info(
        "HAM10000 splits: train=%d, val=%d, test=%d → %s",
        len(splits["train"]), len(splits["val"]), len(splits["test"]), splits_file,
    )

    for split_name, ids in splits.items():
        split_df = df[df["image_id"].isin(ids)]
        dist = split_df["dx"].value_counts().to_dict()
        logger.info("  %s: %s", split_name, dist)


def generate_splits_hiba(raw_dir: Path, splits_dir: Path, seed: int = RANDOM_SEED):
    """Genera splits estratificados para HIBA (por diagnóstico)."""
    metadata_file = raw_dir / "metadata.csv"
    if not metadata_file.exists():
        logger.warning("metadata.csv no encontrado en %s", raw_dir)
        return

    df = pd.read_csv(metadata_file)
    id_col = "isic_id" if "isic_id" in df.columns else df.columns[0]
    logger.info("HIBA: %d samples, columna ID: %s", len(df), id_col)

    ids = df[id_col].to_numpy()
    labels = df["diagnosis"].to_numpy()

    train_ids, temp_ids, train_labels, temp_labels = train_test_split(
        ids, labels,
        test_size=(SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"]),
        stratify=labels,
        random_state=seed,
    )

    val_ratio = SPLIT_RATIOS["val"] / (SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"])
    val_ids, test_ids, _, _ = _safe_stratified_split(
        temp_ids, temp_labels,
        test_size=(1 - val_ratio),
        random_state=seed,
        context="HIBA val/test",
    )

    splits = {
        "train": train_ids.tolist(),
        "val": val_ids.tolist(),
        "test": test_ids.tolist(),
    }

    splits_dir.mkdir(parents=True, exist_ok=True)
    splits_file = splits_dir / "hiba_splits.json"
    with open(splits_file, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    logger.info(
        "HIBA splits: train=%d, val=%d, test=%d → %s",
        len(splits["train"]), len(splits["val"]), len(splits["test"]), splits_file,
    )


def generate_splits_mmskin(raw_dir: Path, splits_dir: Path, seed: int = RANDOM_SEED):
    """Genera splits para MM-SkinQA basándose en las imágenes del caption.csv."""
    caption_file = raw_dir / "caption.csv"
    if not caption_file.exists():
        logger.warning("caption.csv no encontrado en %s", raw_dir)
        return

    df = pd.read_csv(caption_file)
    # Los paths tienen prefijo 'dataset/', extraer solo el nombre del archivo
    image_names = df["image"].apply(
        lambda x: x.replace("dataset/", "") if isinstance(x, str) and x.startswith("dataset/") else x
    )
    unique_images = sorted(image_names.unique())
    logger.info("MM-SkinQA: %d imágenes únicas en caption.csv", len(unique_images))

    ids = np.array(unique_images)
    train_ids, temp_ids = train_test_split(
        ids,
        test_size=(SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"]),
        random_state=seed,
    )
    val_ratio = SPLIT_RATIOS["val"] / (SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"])
    val_ids, test_ids = train_test_split(
        temp_ids, test_size=(1 - val_ratio), random_state=seed,
    )

    splits = {
        "train": train_ids.tolist(),
        "val": val_ids.tolist(),
        "test": test_ids.tolist(),
    }

    splits_dir.mkdir(parents=True, exist_ok=True)
    splits_file = splits_dir / "mmskin_splits.json"
    with open(splits_file, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    logger.info(
        "MM-SkinQA splits: train=%d, val=%d, test=%d → %s",
        len(splits["train"]), len(splits["val"]), len(splits["test"]), splits_file,
    )


def generate_splits_skincare(raw_dir: Path, splits_dir: Path, seed: int = RANDOM_SEED):
    """Genera splits para SkinCaRe (si el dataset fue descargado)."""
    annotations_file = raw_dir / "annotations.json"
    if not annotations_file.exists():
        logger.warning("annotations.json no encontrado en %s", raw_dir)
        return

    with open(annotations_file, encoding="utf-8") as f:
        data = json.load(f)
    ids = [item.get("image", item.get("image_id", f"sample_{i}")) for i, item in enumerate(data)]
    unique_ids = sorted(set(ids))
    logger.info("SkinCaRe: %d samples, %d imágenes únicas", len(data), len(unique_ids))

    ids = np.array(unique_ids)
    train_ids, temp_ids = train_test_split(
        ids,
        test_size=(SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"]),
        random_state=seed,
    )
    val_ratio = SPLIT_RATIOS["val"] / (SPLIT_RATIOS["val"] + SPLIT_RATIOS["test"])
    val_ids, test_ids = train_test_split(
        temp_ids, test_size=(1 - val_ratio), random_state=seed,
    )

    splits = {
        "train": train_ids.tolist(),
        "val": val_ids.tolist(),
        "test": test_ids.tolist(),
    }

    splits_dir.mkdir(parents=True, exist_ok=True)
    splits_file = splits_dir / "skincare_splits.json"
    with open(splits_file, "w", encoding="utf-8") as f:
        json.dump(splits, f, indent=2)

    logger.info(
        "SkinCaRe splits: train=%d, val=%d, test=%d → %s",
        len(splits["train"]), len(splits["val"]), len(splits["test"]), splits_file,
    )


def print_dataset_stats(raw_dir: Path, dataset_name: str):
    """Imprime estadísticas básicas de un dataset."""
    # Buscar imágenes en múltiples ubicaciones posibles
    if dataset_name == "HAM10000":
        image_dirs = _find_ham10000_image_dirs(raw_dir)
        image_files = []
        for d in image_dirs:
            image_files.extend(
                f for f in d.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS
            )
    else:
        images_dir = raw_dir / "images" if (raw_dir / "images").exists() else raw_dir
        image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS]

    if not image_files:
        logger.info("%s: sin imágenes encontradas", dataset_name)
        return

    logger.info("%s: %d imágenes", dataset_name, len(image_files))

    # Muestrear tamaños
    sizes = []
    for img_path in image_files[:100]:
        try:
            img = Image.open(img_path)
            sizes.append(img.size)
        except Exception:
            pass

    if sizes:
        widths, heights = zip(*sizes)
        logger.info(
            "  Tamaños (muestra %d): width=[%d-%d], height=[%d-%d]",
            len(sizes), min(widths), max(widths), min(heights), max(heights),
        )


def main():
    parser = argparse.ArgumentParser(description="Fase 0: Preparación de datos")
    parser.add_argument("--data_dir", type=str, default="data", help="Directorio de datos")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Semilla para splits")
    parser.add_argument("--image_size", type=int, default=IMAGE_SIZE, help="Tamaño de imagen")
    parser.add_argument(
        "--skip_preprocess", action="store_true",
        help="Omitir preprocesamiento de imágenes",
    )
    args = parser.parse_args()

    set_seed(args.seed)

    data_dir = Path(args.data_dir)
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    splits_dir = data_dir / "splits"

    # Nombres reales de las carpetas en data/raw/
    datasets = {
        "HAM10000": raw_dir / "HAM10000",
        "skincare": raw_dir / "skincare",
        "MM-SkinQA": raw_dir / "MM-SkinQA",
        "HIBA": raw_dir / "HIBA",
    }

    # 1. Verificar datasets
    logger.info("=" * 60)
    logger.info("Verificando datasets...")
    available = {}
    for name, path in datasets.items():
        available[name] = verify_dataset_exists(name, path)

    if not any(available.values()):
        logger.error(
            "No se encontró ningún dataset en %s. "
            "Descargá los datasets y ubicalos en data/raw/{nombre}/",
            raw_dir,
        )
        return

    # 2. Estadísticas de datasets raw
    logger.info("=" * 60)
    logger.info("Estadísticas de datasets raw:")
    for name, path in datasets.items():
        if available[name]:
            print_dataset_stats(path, name)

    # 3. Preprocesamiento
    if not args.skip_preprocess:
        logger.info("=" * 60)
        logger.info("Preprocesando imágenes (resize a %dx%d)...", args.image_size, args.image_size)

        if available.get("HAM10000"):
            preprocess_images_ham10000(
                datasets["HAM10000"], processed_dir / "HAM10000", args.image_size,
            )
        for name in ["skincare", "MM-SkinQA", "HIBA"]:
            if available.get(name):
                preprocess_images_generic(
                    datasets[name], processed_dir / name, args.image_size,
                )

        # Copiar CSVs de MM-SkinQA al directorio procesado (MMSkinDataset los necesita)
        if available.get("MM-SkinQA"):
            for csv_name in ("caption.csv", "VQA.csv"):
                src = datasets["MM-SkinQA"] / csv_name
                dst = processed_dir / "MM-SkinQA" / csv_name
                if src.exists() and not dst.exists():
                    shutil.copy2(src, dst)
                    logger.info("Copiado %s → %s", csv_name, dst)

    # 4. Generar splits
    logger.info("=" * 60)
    logger.info("Generando splits...")

    if available.get("HAM10000"):
        generate_splits_ham10000(datasets["HAM10000"], splits_dir, args.seed)

    if available.get("HIBA"):
        generate_splits_hiba(datasets["HIBA"], splits_dir, args.seed)

    if available.get("MM-SkinQA"):
        generate_splits_mmskin(datasets["MM-SkinQA"], splits_dir, args.seed)

    if available.get("skincare"):
        generate_splits_skincare(datasets["skincare"], splits_dir, args.seed)

    logger.info("=" * 60)
    logger.info("Preparación de datos completada.")


if __name__ == "__main__":
    main()
