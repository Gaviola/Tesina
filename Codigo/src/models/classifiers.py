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
