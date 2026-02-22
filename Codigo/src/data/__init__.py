from src.data.ham10000 import HAM10000Dataset
from src.data.skincare import SkinCaReDataset
from src.data.mmskin import MMSkinDataset
from src.data.hiba import HIBADataset
from src.data.transforms import get_train_transforms, get_val_transforms

DATASET_REGISTRY = {
    "ham10000": HAM10000Dataset,
    "skincare": SkinCaReDataset,
    "mmskin": MMSkinDataset,
    "mm-skinqa": MMSkinDataset,  # alias
    "hiba": HIBADataset,
}


def build_dataset(name: str, **kwargs):
    """Instancia un dataset por nombre."""
    if name not in DATASET_REGISTRY:
        raise ValueError(f"Dataset '{name}' no registrado. Disponibles: {list(DATASET_REGISTRY.keys())}")
    return DATASET_REGISTRY[name](**kwargs)
