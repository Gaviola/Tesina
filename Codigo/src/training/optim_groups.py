"""Construcción de param groups con Layer-wise LR Decay (LLRD).

Las capas más cercanas a la entrada reciben learning rates progresivamente
más bajos. La intuición: las capas tempranas codifican features genéricas
(de ImageNet) que no queremos perturbar mucho; las capas tardías y el head
necesitan adaptarse al nuevo dominio (dermatología).

LR de la capa i (con ``num_layers`` capas, head = capa num_layers-1):

    lr_i = base_lr * decay ** (num_layers - 1 - i)

Cuando ``decay = 1.0`` todos los grupos reciben ``base_lr`` (LLRD off).
"""

from typing import Any

import torch.nn as nn


def get_llrd_groups(
    model: nn.Module,
    model_name: str,
    base_lr: float,
    weight_decay: float,
    decay: float,
) -> list[dict[str, Any]]:
    """Construye lista de param groups con LR escalado por profundidad.

    Args:
        model: modelo (instancia de DenseNet121Classifier o ViTClassifier).
        model_name: ``"densenet"`` o ``"vit"``.
        base_lr: learning rate de la última capa (head).
        weight_decay: idéntico para todos los grupos.
        decay: factor multiplicativo entre capas consecutivas.
            1.0 = LLRD off (todos los grupos con base_lr).

    Returns:
        Lista de dicts ``{"params", "lr", "weight_decay", "name"}`` lista
        para pasar a ``AdamW``.
    """
    if decay <= 0 or decay > 1:
        raise ValueError(f"decay debe estar en (0, 1], recibido {decay}")

    if model_name == "densenet":
        layers = _densenet_layers(model)
    elif model_name == "vit":
        layers = _vit_layers(model)
    elif model_name == "convnext_tiny":
        layers = _convnext_tiny_layers(model)
    elif model_name == "swin_tiny":
        layers = _swin_tiny_layers(model)
    else:
        raise ValueError(
            f"LLRD no implementado para '{model_name}'. "
            f"Soportados: densenet, vit, convnext_tiny, swin_tiny."
        )

    n = len(layers)
    groups: list[dict[str, Any]] = []
    for idx, (name, params) in enumerate(layers):
        trainable = [p for p in params if p.requires_grad]
        if not trainable:
            continue
        lr = base_lr * (decay ** (n - 1 - idx))
        groups.append({
            "params": trainable,
            "lr": lr,
            "weight_decay": weight_decay,
            "name": name,
        })
    return groups


def _densenet_layers(model: nn.Module) -> list[tuple[str, list]]:
    """Devuelve capas de DenseNet121 ordenadas de input → head."""
    feats = model.backbone.features
    return [
        ("conv0",       list(feats.conv0.parameters())),
        ("norm0",       list(feats.norm0.parameters())),
        ("denseblock1", list(feats.denseblock1.parameters())),
        ("transition1", list(feats.transition1.parameters())),
        ("denseblock2", list(feats.denseblock2.parameters())),
        ("transition2", list(feats.transition2.parameters())),
        ("denseblock3", list(feats.denseblock3.parameters())),
        ("transition3", list(feats.transition3.parameters())),
        ("denseblock4", list(feats.denseblock4.parameters())),
        ("norm5",       list(feats.norm5.parameters())),
        ("classifier",  list(model.backbone.classifier.parameters())),
    ]


def _vit_layers(model: nn.Module) -> list[tuple[str, list]]:
    """Devuelve capas de ViT-B/16 ordenadas de input → head.

    Patch embedding + class_token + pos_embedding van juntos en ``embed``.
    Cada bloque transformer es una capa propia. Termina con LayerNorm y head.
    """
    bb = model.backbone
    embed_params = list(bb.conv_proj.parameters())
    if hasattr(bb, "class_token"):
        embed_params.append(bb.class_token)
    if hasattr(bb.encoder, "pos_embedding"):
        embed_params.append(bb.encoder.pos_embedding)

    layers: list[tuple[str, list]] = [("embed", embed_params)]
    for i, blk in enumerate(bb.encoder.layers):
        layers.append((f"block{i}", list(blk.parameters())))
    layers.append(("ln_post", list(bb.encoder.ln.parameters())))
    layers.append(("head", list(bb.heads.parameters())))
    return layers


def _convnext_tiny_layers(model: nn.Module) -> list[tuple[str, list]]:
    """Capas de ConvNeXt-Tiny ordenadas de input → head.

    8 stages en ``backbone.features`` (stem, stage1, downsample, stage2, ...,
    stage4) + 2 capas en ``backbone.classifier`` (LayerNorm + head).
    """
    feats = model.backbone.features
    cls = model.backbone.classifier
    return [
        ("stem",        list(feats[0].parameters())),
        ("stage1",      list(feats[1].parameters())),
        ("downsample1", list(feats[2].parameters())),
        ("stage2",      list(feats[3].parameters())),
        ("downsample2", list(feats[4].parameters())),
        ("stage3",      list(feats[5].parameters())),
        ("downsample3", list(feats[6].parameters())),
        ("stage4",      list(feats[7].parameters())),
        ("ln_post",     list(cls[0].parameters())),
        ("head",        list(cls[2].parameters())),  # cls[1] = Flatten (sin params)
    ]


def _swin_tiny_layers(model: nn.Module) -> list[tuple[str, list]]:
    """Capas de Swin-Tiny ordenadas de input → head.

    8 stages en ``backbone.features`` (PatchEmbed, stage1, PatchMerging,
    stage2, ..., stage4) + LayerNorm final + head.
    """
    feats = model.backbone.features
    return [
        ("patch_embed",  list(feats[0].parameters())),
        ("stage1",       list(feats[1].parameters())),
        ("downsample1",  list(feats[2].parameters())),
        ("stage2",       list(feats[3].parameters())),
        ("downsample2",  list(feats[4].parameters())),
        ("stage3",       list(feats[5].parameters())),
        ("downsample3",  list(feats[6].parameters())),
        ("stage4",       list(feats[7].parameters())),
        ("ln_post",      list(model.backbone.norm.parameters())),
        ("head",         list(model.backbone.head.parameters())),
    ]


def get_head_params(model: nn.Module, model_name: str) -> list:
    """Devuelve sólo los parámetros del head (para stage 1 de two-stage)."""
    if model_name == "densenet":
        return list(model.backbone.classifier.parameters())
    if model_name == "vit":
        return list(model.backbone.heads.parameters())
    if model_name == "convnext_tiny":
        return list(model.backbone.classifier[2].parameters())
    if model_name == "swin_tiny":
        return list(model.backbone.head.parameters())
    raise ValueError(f"head_params no implementado para '{model_name}'")


def freeze_backbone(model: nn.Module, model_name: str) -> None:
    """Congela todo excepto el head (uso: stage 1 de two-stage)."""
    head_param_ids = {id(p) for p in get_head_params(model, model_name)}
    for p in model.parameters():
        p.requires_grad = id(p) in head_param_ids


def unfreeze_all(model: nn.Module) -> None:
    """Habilita gradiente en todos los parámetros (uso: stage 2)."""
    for p in model.parameters():
        p.requires_grad = True
