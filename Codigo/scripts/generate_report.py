"""Inferencia: Genera reporte clínico para una imagen dermatoscópica.

Soporta modo imagen única (--image) y modo batch (--images_dir) para evaluar
un directorio completo. Los reportes batch se guardan en --output_dir como JSON.

Uso:
    # Imagen única (stdout)
    python scripts/generate_report.py --model llava_med --image path/to/image.jpg

    # Con checkpoint fine-tuned (Stage 2)
    python scripts/generate_report.py --model mini_vlm \\
        --checkpoint outputs/checkpoints/stage2_mini_vlm/best_model.pt \\
        --image path/to/image.jpg --output outputs/report.json

    # Batch sobre directorio
    python scripts/generate_report.py --model llava_med \\
        --checkpoint outputs/checkpoints/stage2_llava_med/best_model.pt \\
        --images_dir data/mm_skin --output_dir outputs/generated_reports
"""

import argparse
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PIL import Image

from src.models.factory import build_model
from src.training.lora_config import apply_lora, get_lora_config
from src.utils.device import get_vram_gb
from src.utils.io import save_results
from src.utils.logging import log_time, setup_logger
from src.utils.seed import set_seed

logger = logging.getLogger(__name__)

REPORT_PROMPT = (
    "Describe this skin lesion with a structured clinical report that includes: "
    "findings, diagnostic impression, and differential diagnosis."
)

_VRAM_REQUIRED = {"llava_med": 14.0, "mini_vlm": 10.0}
_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}


def _load_model_with_checkpoint(args):
    """Carga el modelo y opcionalmente aplica un checkpoint (con LoRA si corresponde)."""
    vram = get_vram_gb()
    quantize = vram < _VRAM_REQUIRED[args.model]
    if quantize:
        logger.info("VRAM insuficiente (%.1f GB). Activando cuantización 4-bit.", vram)

    model = build_model({"name": args.model, "quantize": quantize})
    with log_time(f"Cargando {args.model}", logger):
        model.load_components()

    if args.checkpoint:
        import torch
        ckpt_path = Path(args.checkpoint)
        if not ckpt_path.exists():
            logger.error("Checkpoint no encontrado: %s", args.checkpoint)
            sys.exit(1)

        ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)

        # Detectar si el checkpoint proviene de Stage 2 (tiene LoRA)
        lora_config_path = ckpt_path.parent / "lora_config.json"
        if lora_config_path.exists():
            with open(lora_config_path, encoding="utf-8") as f:
                lora_cfg = json.load(f)

            # Inferir r real desde shapes del checkpoint (lora_A.weight shape = [r, in_features])
            state_dict = ckpt.get("model_state_dict", {})
            lora_a_key = next((k for k in state_dict if "lora_A.default.weight" in k), None)
            if lora_a_key is not None:
                r_actual = state_dict[lora_a_key].shape[0]
                if r_actual != lora_cfg["r"]:
                    logger.warning(
                        "LoRA r en lora_config.json (%d) difiere del checkpoint (%d). Usando r=%d del checkpoint.",
                        lora_cfg["r"], r_actual, r_actual,
                    )
                    lora_cfg["r"] = r_actual

            logger.info("LoRA config detectada: r=%d, alpha=%d", lora_cfg["r"], lora_cfg["lora_alpha"])
            lora_config = get_lora_config(
                r=lora_cfg["r"],
                lora_alpha=lora_cfg["lora_alpha"],
                lora_dropout=lora_cfg.get("lora_dropout", 0.05),
                target_modules=lora_cfg.get("target_modules", ["q_proj", "v_proj"]),
            )
            model.model = apply_lora(model.model, lora_config)

        model.load_state_dict(ckpt["model_state_dict"], strict=False)
        logger.info(
            "Checkpoint cargado desde %s (época %d)",
            args.checkpoint, ckpt.get("epoch", "?"),
        )

    return model


def _generate_single(model, image_path: Path, max_tokens: int) -> str:
    """Genera reporte para una imagen."""
    image = Image.open(image_path).convert("RGB")
    reports = model.generate(
        images=[image],
        prompts=[REPORT_PROMPT],
        max_new_tokens=max_tokens,
    )
    return reports[0]


def main():
    parser = argparse.ArgumentParser(description="Genera reporte clínico para imagen(es)")
    parser.add_argument("--model", type=str, required=True, choices=["llava_med", "mini_vlm"])
    parser.add_argument("--checkpoint", type=str, default=None, help="Path al checkpoint")
    # Modo imagen única
    parser.add_argument("--image", type=str, default=None, help="Path a imagen única")
    parser.add_argument("--output", type=str, default=None, help="Archivo JSON de salida")
    # Modo batch
    parser.add_argument("--images_dir", type=str, default=None, help="Directorio de imágenes")
    parser.add_argument("--output_dir", type=str, default="outputs/generated_reports")
    parser.add_argument("--reference_csv", type=str, default=None,
                        help="CSV con columnas image_id y caption/report para referencias")
    parser.add_argument("--reference_dir", type=str, default=None,
                        help="Directorio con archivos .txt de referencia en estructura paralela "
                             "a --images_dir. Para cada imagen <images_dir>/A/B.jpg busca "
                             "<reference_dir>/A/B.jpg.txt (formato SkinCoT).")
    parser.add_argument("--max_tokens", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.image is None and args.images_dir is None:
        parser.error("Se requiere --image o --images_dir.")

    set_seed(args.seed)
    setup_logger("generate_report")

    model = _load_model_with_checkpoint(args)

    # ---- Modo imagen única ----
    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            logger.error("Imagen no encontrada: %s", args.image)
            sys.exit(1)

        with log_time("Generando reporte", logger):
            report = _generate_single(model, image_path, args.max_tokens)

        result = {
            "image": str(image_path),
            "model": args.model,
            "checkpoint": args.checkpoint,
            "prompt": REPORT_PROMPT,
            "report": report,
        }

        if args.output:
            save_results(result, args.output)
            logger.info("Reporte guardado en %s", args.output)
        else:
            print("\n" + "=" * 60)
            print("REPORTE CLÍNICO GENERADO")
            print("=" * 60)
            print(report)
            print("=" * 60)

    # ---- Modo batch ----
    else:
        images_dir = Path(args.images_dir)
        if not images_dir.exists():
            logger.error("Directorio no encontrado: %s", args.images_dir)
            sys.exit(1)

        image_paths = sorted(
            p for p in images_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in _IMAGE_EXTENSIONS
        )
        if not image_paths:
            logger.error("No se encontraron imágenes en %s", args.images_dir)
            sys.exit(1)

        # Cargar referencias opcionales desde CSV (ej: MM-SkinQA)
        references = {}
        if args.reference_csv:
            import pandas as pd
            ref_df = pd.read_csv(args.reference_csv)
            ref_col = "cleaned_caption" if "cleaned_caption" in ref_df.columns else "caption"
            for _, row in ref_df.iterrows():
                img_id = Path(str(row.get("image", ""))).name.replace("dataset/", "")
                text = row.get(ref_col, "")
                if img_id and text:
                    references[img_id] = str(text)

        # Directorio de referencias en estructura paralela (ej: SkinCoT EN/)
        reference_dir = Path(args.reference_dir) if args.reference_dir else None
        if reference_dir and not reference_dir.exists():
            logger.error("Directorio de referencias no encontrado: %s", args.reference_dir)
            sys.exit(1)

        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Generando reportes para %d imágenes...", len(image_paths))
        for i, img_path in enumerate(image_paths):
            try:
                # Resolver referencia: primero reference_dir, luego reference_csv
                reference = references.get(img_path.name, "")
                if not reference and reference_dir is not None:
                    # Misma subestructura que images_dir: <reference_dir>/A/B.jpg.txt
                    rel = img_path.relative_to(images_dir)
                    txt_path = reference_dir / rel.parent / (rel.name + ".txt")
                    if txt_path.exists():
                        reference = txt_path.read_text(encoding="utf-8").strip()

                report = _generate_single(model, img_path, args.max_tokens)
                result = {
                    "image_id": img_path.name,
                    "model": args.model,
                    "checkpoint": args.checkpoint,
                    "report": report,
                    "reference": reference,
                    "gt_label": "",
                }
                out_file = output_dir / f"{img_path.stem}_report.json"
                save_results(result, str(out_file))

                if (i + 1) % 50 == 0 or i == 0:
                    logger.info("Progreso: %d/%d imágenes procesadas", i + 1, len(image_paths))
            except Exception as e:
                logger.warning("Error procesando %s: %s", img_path.name, e)

        logger.info("Reportes guardados en %s (%d archivos)", output_dir, len(image_paths))


if __name__ == "__main__":
    main()
