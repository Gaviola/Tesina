from torchvision import transforms

# ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_transforms(size: int = 224) -> transforms.Compose:
    """Transformaciones para entrenamiento con augmentations.

    Incluye: resize, rotación ±30°, flip horizontal, color jitter, normalización ImageNet.
    """
    return transforms.Compose([
        transforms.Resize((size, size)),
        transforms.RandomRotation(30),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transforms(size: int = 224) -> transforms.Compose:
    """Transformaciones para validación/test (sin augmentations)."""
    return transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_inverse_normalize() -> transforms.Normalize:
    """Normalización inversa para visualización de imágenes."""
    return transforms.Normalize(
        mean=[-m / s for m, s in zip(IMAGENET_MEAN, IMAGENET_STD)],
        std=[1.0 / s for s in IMAGENET_STD],
    )
