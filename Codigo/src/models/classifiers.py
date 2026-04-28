import torch
import torch.nn as nn
import torchvision.models as models


class DenseNet121Classifier(nn.Module):
    """DenseNet121 para clasificación de lesiones dermatoscópicas.

    Transfer learning desde ImageNet con head de clasificación configurable.
    Soporta congelamiento del backbone y unfreezing gradual.
    """

    def __init__(self, num_classes: int = 7, pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__()
        weights = models.DenseNet121_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.densenet121(weights=weights)

        # Reemplazar classifier head
        in_features = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self._freeze_backbone()

    def _freeze_backbone(self):
        """Congela todas las capas excepto el classifier head."""
        for name, param in self.backbone.named_parameters():
            if "classifier" not in name:
                param.requires_grad = False

    def unfreeze_layers(self, layer_names: list[str]):
        """Descongela capas específicas para fine-tuning gradual.

        Args:
            layer_names: e.g. ["denseblock4", "transition3"]
        """
        for name, param in self.backbone.named_parameters():
            if any(layer in name for layer in layer_names):
                param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


class ConvNeXtTinyClassifier(nn.Module):
    """ConvNeXt-Tiny para clasificación de lesiones dermatoscópicas.

    Sucesor moderno (CNN) de DenseNet/ResNet con bloques inspirados en
    Transformers (LayerNorm, GELU, depthwise conv).
    """

    def __init__(self, num_classes: int = 7, pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__()
        weights = models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.convnext_tiny(weights=weights)

        # classifier original: Sequential(LayerNorm2d, Flatten, Linear(768, 1000))
        # Reemplazamos solo el último Linear preservando LayerNorm + Flatten.
        in_features = self.backbone.classifier[2].in_features
        self.backbone.classifier[2] = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self._freeze_backbone()

    def _freeze_backbone(self):
        """Congela todo excepto la última capa del classifier (head)."""
        # backbone.features.* + classifier[0..1] frozen; classifier[2] (head) trainable.
        for p in self.backbone.features.parameters():
            p.requires_grad = False
        for p in self.backbone.classifier[0].parameters():
            p.requires_grad = False
        for p in self.backbone.classifier[1].parameters():
            p.requires_grad = False

    def unfreeze_layers(self, layer_names: list[str]):
        """Descongela bloques específicos de features (ej: ['7'] para el último stage)."""
        for name, param in self.backbone.features.named_parameters():
            if any(layer in name for layer in layer_names):
                param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


class SwinTinyClassifier(nn.Module):
    """Swin-Tiny para clasificación de lesiones dermatoscópicas.

    Transformer jerárquico con shifted windows. Sucesor natural de ViT
    para tareas de visión, con mejor escalabilidad y eficiencia.
    """

    def __init__(self, num_classes: int = 7, pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__()
        weights = models.Swin_T_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.swin_t(weights=weights)

        in_features = self.backbone.head.in_features
        self.backbone.head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self._freeze_backbone()

    def _freeze_backbone(self):
        """Congela todo excepto el head."""
        for name, param in self.backbone.named_parameters():
            if not name.startswith("head"):
                param.requires_grad = False

    def unfreeze_layers(self, layer_names: list[str]):
        """Descongela bloques específicos de features (ej: ['7'] para el último stage)."""
        for name, param in self.backbone.features.named_parameters():
            if any(layer in name for layer in layer_names):
                param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)


class ViTClassifier(nn.Module):
    """ViT-B/16 para clasificación de lesiones dermatoscópicas.

    Transfer learning desde ImageNet con head de clasificación configurable.
    """

    def __init__(self, num_classes: int = 7, pretrained: bool = True, freeze_backbone: bool = True):
        super().__init__()
        weights = models.ViT_B_16_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.vit_b_16(weights=weights)

        # Reemplazar head
        in_features = self.backbone.heads.head.in_features
        self.backbone.heads.head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_features, num_classes),
        )

        if freeze_backbone:
            self._freeze_backbone()

    def _freeze_backbone(self):
        """Congela todo excepto el head."""
        for name, param in self.backbone.named_parameters():
            if "heads" not in name:
                param.requires_grad = False

    def unfreeze_layers(self, layer_names: list[str]):
        """Descongela capas específicas del encoder."""
        for name, param in self.backbone.named_parameters():
            if any(layer in name for layer in layer_names):
                param.requires_grad = True

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)
