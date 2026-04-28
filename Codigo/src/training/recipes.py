"""Recipes de entrenamiento para clasificadores de Fase 1.

Un recipe agrupa un conjunto coherente de hiperparámetros y técnicas
(label smoothing, warmup, augmentations, mixup, focal loss, TTA, etc.).
Esto permite a los scripts elegir un preset con una sola flag y
sobreescribir flags individuales para ablaciones.

- ``legacy``  reproduce bit-a-bit el comportamiento previo a la
  introducción de los recipes (baseline de la Fase 1 pre-mejoras).
- ``modern``  activa el pack de técnicas descritas en
  ``Codigo/docs/ideas/mejoras_clasificadores_fase1.md``.

En esta etapa (Fase 1) sólo están implementados los campos
``label_smoothing``, ``warmup_epochs`` y ``epochs``. El resto de campos
están definidos para permitir que las Fases 2-3 los conecten sin tocar
los call sites.
"""

from dataclasses import dataclass, field, fields
from typing import Any


@dataclass
class Recipe:
    """Hiperparámetros agrupados por recipe.

    Los campos None significan "no fijado por el recipe" — el script
    debe usar el default de su flag o el valor que ya tenía.
    """

    name: str
    epochs: int | None = None
    label_smoothing: float = 0.0
    warmup_epochs: int = 0

    # Campos reservados para Fases 2-3 (no implementados todavía).
    randaugment: bool = False
    randaugment_n: int = 2
    randaugment_m: int = 9
    random_erasing: float = 0.0
    random_resized_crop: bool = False
    rrc_scale_min: float = 1.0
    mixup_alpha: float = 0.0
    cutmix_alpha: float = 0.0
    mixup_prob: float = 0.5
    focal_gamma: float = 0.0
    two_stage: bool = False
    llrd: float = 1.0
    tta: bool = False
    weight_decay: float | None = None

    def overrides(self) -> dict[str, Any]:
        """Devuelve sólo los campos no-None / distintos del default base."""
        base = Recipe(name=self.name)
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name != "name" and getattr(self, f.name) != getattr(base, f.name)
        }


RECIPES: dict[str, Recipe] = {
    "legacy": Recipe(
        name="legacy",
        epochs=30,
        label_smoothing=0.0,
        warmup_epochs=0,
    ),
    "modern": Recipe(
        name="modern",
        epochs=40,
        label_smoothing=0.1,
        warmup_epochs=3,
        randaugment=True,
        random_erasing=0.25,
        random_resized_crop=True,
        rrc_scale_min=0.7,
        mixup_alpha=0.2,
        cutmix_alpha=1.0,
        mixup_prob=0.5,
        focal_gamma=2.0,
        two_stage=True,
        llrd=0.75,
        tta=True,
        weight_decay=0.05,
    ),
}


def get_recipe(name: str) -> Recipe:
    """Devuelve el Recipe asociado al nombre.

    Lanza ValueError si ``name`` no está registrado.
    """
    if name not in RECIPES:
        raise ValueError(
            f"Recipe '{name}' desconocido. Disponibles: {list(RECIPES)}"
        )
    return RECIPES[name]


_SENTINEL = object()


def resolve_field(recipe: Recipe, cli_value: Any, field_name: str) -> Any:
    """Override individual: si CLI pasó valor explícito (≠ sentinel), gana CLI; si no, gana recipe.

    Patrón de uso desde el script::

        ls = resolve_field(recipe, args.label_smoothing, "label_smoothing")

    Donde ``args.label_smoothing`` es ``None`` si el usuario no pasó la flag
    (ver ``ResolveAction`` en utilidades de argparse de los scripts).
    """
    if cli_value is _SENTINEL or cli_value is None:
        return getattr(recipe, field_name)
    return cli_value
