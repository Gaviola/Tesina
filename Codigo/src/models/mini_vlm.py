import torch
import torch.nn as nn

from src.models.vlm_base import VLMBase


class MiniVLM(VLMBase):
    """Mini-VLM: CLIP ViT-B/16 + MLP proyección + Phi-3-mini.

    Modelo más ligero (~4B parámetros) para comparación con LLaVA-Med.
    VRAM estimada: ~8GB con LoRA.

    Componentes:
    - vision_encoder: CLIP ViT-B/16 (congelado)
    - projection: MLP que mapea dim 768 → dim embedding de Phi-3
    - llm: Phi-3-mini-4k-instruct (se aplica LoRA en Fase 2)
    """

    def __init__(
        self,
        vision_encoder_name: str = "openai/clip-vit-base-patch16",
        llm_name: str = "microsoft/Phi-3-mini-4k-instruct",
        projection_dim: int = 768,
        max_new_tokens: int = 512,
    ):
        super().__init__()
        self.vision_encoder_name = vision_encoder_name
        self.llm_name = llm_name
        self.projection_dim = projection_dim
        self.max_new_tokens = max_new_tokens

        self.vision_encoder = None
        self.projection = None
        self.llm = None
        self.tokenizer = None

    def load_components(self):
        """Carga los componentes del modelo desde HuggingFace."""
        from transformers import AutoModelForCausalLM, AutoTokenizer, CLIPVisionModel

        self.vision_encoder = CLIPVisionModel.from_pretrained(self.vision_encoder_name)
        self.vision_encoder.eval()
        for p in self.vision_encoder.parameters():
            p.requires_grad = False

        vision_hidden_size = self.vision_encoder.config.hidden_size  # 768 para ViT-B/16

        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.llm = AutoModelForCausalLM.from_pretrained(
            self.llm_name,
            torch_dtype=torch.float16,
            trust_remote_code=True,
        )

        # MLP: CLIP dim → Phi-3 embedding dim
        llm_hidden_size = self.llm.config.hidden_size
        self.projection = nn.Sequential(
            nn.Linear(vision_hidden_size, llm_hidden_size),
            nn.GELU(),
            nn.Linear(llm_hidden_size, llm_hidden_size),
        )

    def encode_image(self, images: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            vision_outputs = self.vision_encoder(images)
        image_features = vision_outputs.last_hidden_state
        projected = self.projection(image_features)
        return projected

    @torch.no_grad()
    def generate(
        self,
        images: torch.Tensor,
        prompts: list[str],
        max_new_tokens: int = 512,
        **kwargs,
    ) -> list[str]:
        """Genera texto dado imágenes y prompts.

        Concatena embeddings visuales con embeddings de texto y genera
        con el LLM usando inputs_embeds.
        """
        device = images.device

        # 1. Codificar imágenes → (B, num_patches, llm_hidden)
        image_embeds = self.encode_image(images)

        # 2. Tokenizar prompts
        text_inputs = self.tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=256,
        ).to(device)

        # 3. Obtener embeddings de texto
        text_embeds = self.llm.get_input_embeddings()(text_inputs.input_ids)

        # 4. Concatenar: [image_embeds, text_embeds] a lo largo de seq_len
        combined_embeds = torch.cat([image_embeds, text_embeds], dim=1)

        # 5. Construir attention_mask extendida
        image_attn = torch.ones(
            image_embeds.shape[0], image_embeds.shape[1],
            dtype=text_inputs.attention_mask.dtype, device=device,
        )
        combined_attn = torch.cat([image_attn, text_inputs.attention_mask], dim=1)

        # 6. Generar con el LLM
        gen_kwargs = {
            "inputs_embeds": combined_embeds,
            "attention_mask": combined_attn,
            "max_new_tokens": max_new_tokens,
            "do_sample": kwargs.get("do_sample", False),
            "temperature": kwargs.get("temperature", 1.0),
            "top_p": kwargs.get("top_p", 1.0),
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }
        output_ids = self.llm.generate(**gen_kwargs)

        # 7. Decodificar tokens generados
        generated_texts = self.tokenizer.batch_decode(
            output_ids, skip_special_tokens=True,
        )

        return generated_texts

    def forward(self, images, input_ids, attention_mask, labels) -> dict:
        image_embeds = self.encode_image(images)
        # TODO: Implementar forward completo con loss en Fase 2
        raise NotImplementedError("forward() se implementa completo en Fase 2")
