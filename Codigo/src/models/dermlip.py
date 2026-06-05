"""DermLIP — clasificador visión-lenguaje (CLIP-style) derm-especializado.

DermLIP (entrenado en Derm1M) es un modelo contrastivo imagen-texto: encoder de
imagen + encoder de texto alineados en un espacio compartido. NO genera texto
(no tiene decoder autoregresivo) — se usa SOLO para clasificación zero-shot /
linear-probe y retrieval, no para generación de reportes.

Tercer tipo de modelo del proyecto, distinto de:
  - los clasificadores supervisados (`classifiers.py`, forward -> logits), y
  - los VLM generativos (`vlm_base.py`, load_components + generate).

Pesos: https://huggingface.co/redlessone/DermLIP_ViT-B-16 (CC BY-NC-4.0).
Requiere `open_clip_torch` (import lazy para no romper el factory si falta).
"""

import logging

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# Variantes publicadas (Derm1M / ICCV'25)
DERMLIP_CHECKPOINTS = {
    "vit-b-16": "hf-hub:redlessone/DermLIP_ViT-B-16",
    "panderm":  "hf-hub:redlessone/DermLIP_PanDerm-base-w-PubMed-256",
}

# Templates de prompt para ensemble zero-shot (promediado de embeddings de texto
# por clase). El primero es el del repo oficial de DermLIP.
DEFAULT_TEMPLATES = (
    "This is a skin image of {c}",
    "A dermatoscopic image of {c}",
    "A clinical photograph of {c}",
    "An image showing {c}",
)


class DermLIPClassifier(nn.Module):
    """Wrapper de DermLIP para clasificación zero-shot (y, opcional, linear-probe).

    Args:
        checkpoint: alias en DERMLIP_CHECKPOINTS ("vit-b-16" | "panderm") o un
            string `hf-hub:...` directo.
        device: dispositivo torch; autodetecta CUDA si None.
        num_classes: si se pasa, agrega un cabezal lineal entrenable sobre el
            encoder de imagen (modo linear-probe / fine-tune supervisado).
    """

    def __init__(self, checkpoint: str = "vit-b-16", device=None, num_classes: int | None = None):
        super().__init__()
        try:
            import open_clip
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "DermLIPClassifier requiere `open_clip_torch`. "
                "Instalar con: pip install open_clip_torch"
            ) from exc

        self.checkpoint = DERMLIP_CHECKPOINTS.get(checkpoint, checkpoint)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        logger.info("Cargando DermLIP desde %s ...", self.checkpoint)
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(self.checkpoint)
        self.tokenizer = open_clip.get_tokenizer(self.checkpoint)
        self.model.eval().to(self.device)

        # Cabezal lineal opcional (linear-probe). Dim de embedding inferida de un
        # forward dummy de texto la primera vez que se use; se materializa acá si
        # se pide num_classes.
        self.head = None
        if num_classes is not None:
            embed_dim = getattr(self.model, "embed_dim", None) or self._infer_embed_dim()
            self.head = nn.Linear(embed_dim, num_classes).to(self.device)

    def _infer_embed_dim(self) -> int:
        with torch.no_grad():
            tok = self.tokenizer(["x"]).to(self.device)
            feat = self.model.encode_text(tok)
        return feat.shape[-1]

    @torch.no_grad()
    def _encode_text_per_class(self, class_names: list[str], templates) -> torch.Tensor:
        """Embedding de texto por clase, promediado sobre templates (ensemble ZS)."""
        templates = templates or DEFAULT_TEMPLATES
        class_embeds = []
        for c in class_names:
            prompts = [t.format(c=c) for t in templates]
            tok = self.tokenizer(prompts).to(self.device)
            feats = self.model.encode_text(tok)
            feats = feats / feats.norm(dim=-1, keepdim=True)
            mean = feats.mean(dim=0)
            mean = mean / mean.norm()
            class_embeds.append(mean)
        return torch.stack(class_embeds, dim=0)  # [C, D]

    @torch.no_grad()
    def zero_shot_logits(self, images: list, class_names: list[str], templates=None) -> torch.Tensor:
        """Logits zero-shot por similitud coseno imagen-texto.

        Args:
            images: lista de PIL.Image.
            class_names: nombres de clase EN EL ORDEN del label-space (e.g. el de
                HAM10000_CLASSES) para que argmax mapee directo al índice de clase.
            templates: iterable de templates con `{c}`; default DEFAULT_TEMPLATES.

        Returns:
            Tensor [N, C] de logits (escala 100 * cos_sim), en CPU.
        """
        text_features = self._encode_text_per_class(class_names, templates)  # [C, D]
        pixel = torch.stack([self.preprocess(im) for im in images]).to(self.device)
        image_features = self.model.encode_image(pixel)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        logits = 100.0 * image_features @ text_features.T  # [N, C]
        return logits.float().cpu()

    @torch.no_grad()
    def embed_images(self, images: list) -> torch.Tensor:
        """Embeddings normalizados de imagen (para linear-probe / retrieval).

        Args:
            images: lista de PIL.Image.
        Returns:
            Tensor [N, D] normalizado, en CPU.
        """
        pixel = torch.stack([self.preprocess(im) for im in images]).to(self.device)
        feats = self.model.encode_image(pixel)
        feats = feats / feats.norm(dim=-1, keepdim=True)
        return feats.float().cpu()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Modo linear-probe: encoder congelado + cabezal lineal -> logits.

        Espera `x` ya preprocesado con `self.preprocess` (no transforms ImageNet).
        Requiere haber instanciado con num_classes.
        """
        if self.head is None:
            raise RuntimeError(
                "forward() requiere modo linear-probe: instanciar con num_classes."
            )
        with torch.no_grad():
            feats = self.model.encode_image(x)
        return self.head(feats)
