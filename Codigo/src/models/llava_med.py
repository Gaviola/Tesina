import torch
import torch.nn as nn

from src.models.vlm_base import VLMBase


class LLaVAMed(VLMBase):
    """LLaVA-Med 7B: CLIP ViT-L/14 + MLP proyección + LLaMA-2 7B.

    Componentes:
    - vision_encoder: CLIP ViT-L/14 (congelado)
    - projection: MLP que mapea embeddings visuales al espacio del LLM
    - llm: LLaMA-2 7B (se aplica LoRA en Fase 2)
    """

    def __init__(
        self,
        vision_encoder_name: str = "openai/clip-vit-large-patch14",
        llm_name: str = "meta-llama/Llama-2-7b-chat-hf",
        projection_dim: int = 1024,
        max_new_tokens: int = 512,
    ):
        super().__init__()
        self.vision_encoder_name = vision_encoder_name
        self.llm_name = llm_name
        self.projection_dim = projection_dim
        self.max_new_tokens = max_new_tokens

        # Los componentes se inicializan como None y se cargan con load_components()
        self.vision_encoder = None
        self.projection = None
        self.llm = None
        self.tokenizer = None

    def load_components(self):
        """Carga los componentes del modelo desde HuggingFace.

        Requiere: transformers, CUDA con VRAM suficiente (~14GB LoRA, ~10GB QLoRA).
        """
        from transformers import AutoModelForCausalLM, AutoTokenizer, CLIPVisionModel

        self.vision_encoder = CLIPVisionModel.from_pretrained(self.vision_encoder_name)
        self.vision_encoder.eval()
        for p in self.vision_encoder.parameters():
            p.requires_grad = False

        vision_hidden_size = self.vision_encoder.config.hidden_size  # 1024

        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.llm = AutoModelForCausalLM.from_pretrained(
            self.llm_name,
            torch_dtype=torch.float16,
        )

        # MLP: CLIP dim → LLM embedding dim
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
