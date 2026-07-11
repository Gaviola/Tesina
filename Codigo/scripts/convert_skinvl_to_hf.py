"""P1.1 — Convierte SkinVL-MM (formato original LLaVA-Med) a formato HF.

SkinVL-MM (`zwq803/SkinVL-MM`) trae SOLO los pesos fine-tuneados (LM Mistral + mm_projector),
sin el vision tower (295 tensores). Estrategia robusta: cargar el HF base
`chaoyinshe/llava-med-v1.5-mistral-7b-hf` (que YA funciona en nuestro pipeline, incluye el
vision tower CLIP congelado) y **trasplantarle** los pesos de SkinVL renombrados al schema HF.

Salida: `data/checkpoints/skinvl-mm-hf` (a donde apunta SkinVL.MODEL_NAME).

Requiere ~28-32 GB de RAM (dos copias de 7B). Si falta RAM, correr en un nodo del cluster.
Sin GPU (todo en CPU). Uso:
    python scripts/convert_skinvl_to_hf.py
    python scripts/convert_skinvl_to_hf.py --out data/checkpoints/skinvl-mm-hf
"""

import argparse
import glob
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file
from transformers import LlavaForConditionalGeneration

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE = "chaoyinshe/llava-med-v1.5-mistral-7b-hf"
SKINVL = "zwq803/SkinVL-MM"


def _rename(k: str) -> str | None:
    """Nombre original de SkinVL -> clave del state_dict HF (LlavaForConditionalGeneration)."""
    if k == "lm_head.weight":
        return "language_model.lm_head.weight"
    if k.startswith("model.mm_projector.0."):
        return "multi_modal_projector.linear_1." + k[len("model.mm_projector.0."):]
    if k.startswith("model.mm_projector.2."):
        return "multi_modal_projector.linear_2." + k[len("model.mm_projector.2."):]
    if k.startswith("model."):  # embed_tokens, norm, layers.*
        return "language_model.model." + k[len("model."):]
    return None


def main():
    parser = argparse.ArgumentParser(description="Convertir SkinVL-MM a formato HF")
    parser.add_argument("--out", type=str, default="data/checkpoints/skinvl-mm-hf")
    parser.add_argument("--base", type=str, default=BASE)
    parser.add_argument("--skinvl", type=str, default=SKINVL)
    args = parser.parse_args()

    dtype = torch.bfloat16

    logger.info("1/5 Cargando HF base (%s) en CPU... (descarga ~14 GB la primera vez)", args.base)
    model = LlavaForConditionalGeneration.from_pretrained(
        args.base, torch_dtype=dtype, low_cpu_mem_usage=True,
    )
    hf_sd = model.state_dict()
    hf_keys = set(hf_sd.keys())

    logger.info("2/5 Descargando pesos de SkinVL (%s)...", args.skinvl)
    skinvl_dir = snapshot_download(args.skinvl, allow_patterns=["*.safetensors", "*.json", "*.model", "*.txt"])

    logger.info("3/5 Renombrando y trasplantando pesos (in-place, frugal en RAM)...")
    mapped, unmapped, missing_target, shape_mismatch, partial = 0, [], [], [], []
    transplanted = set()
    # hf_sd son referencias a los parámetros del modelo -> copy_() escribe in-place, sin duplicar RAM.
    for shard in sorted(glob.glob(os.path.join(skinvl_dir, "*.safetensors"))):
        tensors = load_file(shard)
        for k, v in tensors.items():
            nk = _rename(k)
            if nk is None:
                unmapped.append(k)
                continue
            if nk not in hf_keys:
                missing_target.append(nk)
                continue
            if hf_sd[nk].shape != v.shape:
                # Caso vocab: el base HF está padded (p.ej. 32064) y SkinVL usa el vocab real
                # (32000). Las filas extra del base son el token de imagen + padding, que SkinVL
                # NO fine-tunea (usa el placeholder IMAGE_TOKEN_INDEX). Se copian las filas reales
                # de SkinVL en las primeras y se conservan las extra del base.
                same_rest = v.shape[1:] == hf_sd[nk].shape[1:]
                if v.ndim == hf_sd[nk].ndim and same_rest and v.shape[0] < hf_sd[nk].shape[0]:
                    with torch.no_grad():
                        hf_sd[nk][:v.shape[0]].copy_(v.to(dtype))
                    transplanted.add(nk)
                    partial.append((nk, v.shape[0], hf_sd[nk].shape[0]))
                    mapped += 1
                else:
                    shape_mismatch.append((nk, tuple(v.shape), tuple(hf_sd[nk].shape)))
                continue
            with torch.no_grad():
                hf_sd[nk].copy_(v.to(dtype))
            transplanted.add(nk)
            mapped += 1
        del tensors

    logger.info("   trasplantados=%d (parciales=%d)  sin-mapear(SkinVL)=%d  target-no-encontrado=%d  shape-mismatch=%d",
                mapped, len(partial), len(unmapped), len(missing_target), len(shape_mismatch))
    if partial:
        logger.info("   copias parciales (vocab base padded, se conservan filas extra): %s",
                    [(k, f"{a}->{b}") for k, a, b in partial])
    if unmapped:
        logger.warning("   claves SkinVL sin mapear (revisar): %s", unmapped[:5])
    if missing_target:
        logger.error("   targets HF no encontrados (mapeo incorrecto): %s", missing_target[:5])
    if shape_mismatch:
        logger.error("   shape mismatch: %s", shape_mismatch[:5])
    if missing_target or shape_mismatch:
        raise SystemExit("Conversión ABORTADA: revisar mapeo/shapes arriba.")

    # Los únicos tensores del base que NO se sobreescriben deben ser el vision_tower (congelado).
    untouched = [k for k in hf_keys if k not in transplanted]
    non_vision = [k for k in untouched if not k.startswith("vision_tower")]
    logger.info("4/5 Tensores del base conservados: %d (vision_tower). No-vision conservados: %d",
                len(untouched) - len(non_vision), len(non_vision))
    if non_vision:
        logger.warning("   conservados no-vision (revisar si es esperado): %s", non_vision[:8])
    # (Los pesos ya se copiaron in-place en el modelo; no hace falta load_state_dict.)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logger.info("5/5 Guardando en %s ...", out)
    model.save_pretrained(str(out), safe_serialization=True)

    # Copiar los archivos de tokenizer/processor del base SIN cargarlos: el tokenizer.json (fast)
    # puede no parsear con la versión de `tokenizers` del entorno ("did not match ... ModelWrapper");
    # los archivos crudos sí sirven, y llava_med.py carga el tokenizer lento como fallback.
    import shutil
    base_dir = snapshot_download(args.base)
    copied = []
    for fn in sorted(os.listdir(base_dir)):
        if fn in ("config.json", "generation_config.json"):        # ya escritos por save_pretrained
            continue
        if fn.endswith(".safetensors") or fn.endswith(".index.json"):
            continue
        src = os.path.join(base_dir, fn)
        if os.path.isfile(src):
            shutil.copy2(src, out / fn)
            copied.append(fn)
    logger.info("   tokenizer/processor copiados del base: %s", copied)
    logger.info("LISTO. Validá la carga con:")
    logger.info("   python -c \"from src.models.factory import build_model; "
                "m=build_model({'name':'skinvl'}); m.load_components(); print('OK carga SkinVL')\"")


if __name__ == "__main__":
    main()
