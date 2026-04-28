from torchvision import transforms

# ImageNet normalization
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_train_transforms(
    size: int = 224,
    randaugment: bool = False,
    randaugment_n: int = 2,
    randaugment_m: int = 9,
    random_erasing: float = 0.0,
    random_resized_crop: bool = False,
    rrc_scale_min: float = 0.7,
) -> transforms.Compose:
    """Transformaciones para entrenamiento con augmentations.

    Defaults reproducen el comportamiento legacy:
    Resize → Rotation 30° → HFlip → ColorJitter → ToTensor → Normalize.

    Cuando ``randaugment=True`` se reemplaza Rotation+ColorJitter por
    RandAugment(n, m). ``random_erasing > 0`` añade RandomErasing al
    final con esa probabilidad. ``random_resized_crop=True`` reemplaza
    Resize por RandomResizedCrop con escala [rrc_scale_min, 1.0].
    """
    ops: list = []

    if random_resized_crop:
        ops.append(transforms.RandomResizedCrop(size, scale=(rrc_scale_min, 1.0)))
    else:
        ops.append(transforms.Resize((size, size)))

    if randaugment:
        ops.extend([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandAugment(num_ops=randaugment_n, magnitude=randaugment_m),
        ])
    else:
        ops.extend([
            transforms.RandomRotation(30),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        ])

    ops.extend([
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    if random_erasing > 0.0:
        ops.append(transforms.RandomErasing(p=random_erasing))

    return transforms.Compose(ops)


def get_val_transforms(size: int = 224, center_crop: bool = False) -> transforms.Compose:
    """Transformaciones para validación/test (sin augmentations).

    Si ``center_crop=True`` aplica Resize(int(size*256/224)) + CenterCrop(size),
    estilo recipe modern. Default reproduce el comportamiento legacy:
    Resize cuadrado directo a (size, size).
    """
    if center_crop:
        resize_size = int(round(size * 256 / 224))
        ops = [
            transforms.Resize(resize_size),
            transforms.CenterCrop(size),
        ]
    else:
        ops = [transforms.Resize((size, size))]

    ops.extend([
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])

    return transforms.Compose(ops)


def get_inverse_normalize() -> transforms.Normalize:
    """Normalización inversa para visualización de imágenes."""
    return transforms.Normalize(
        mean=[-m / s for m, s in zip(IMAGENET_MEAN, IMAGENET_STD)],
        std=[1.0 / s for s in IMAGENET_STD],
    )
