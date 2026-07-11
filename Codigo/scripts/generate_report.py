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
import re
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

_COT_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_cot(text: str) -> str:
    """Remove <think>...</think> blocks, keeping only the final summary."""
    return _COT_TAG_RE.sub("", text).strip()


# Instrucción alineada con Stage 2 (VLMTrainCollator.CAPTION_INSTRUCTION).
# La v1 usaba un prompt estructurado más largo que no coincidía con el training,
# generando baja superposición léxica con las referencias SkinCoT.
REPORT_PROMPT = "Describe this skin lesion."

_VRAM_REQUIRED = {"llava_med": 14.0, "mini_vlm": 10.0, "skinvl": 14.0}
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


# Templates de grounding (ensamble cascada): inyectan el diagnóstico del clasificador
# para que el VLM se comprometa con un dx en vez de hedear (ver plan ensamble).
# El pilot 1 mostró que "soft" es débil (el modelo ignora el dx ~40%); las variantes
# fuerzan el commitment (dx primero / conclusión obligada / sin diferenciales).
GROUNDED_TEMPLATES = {
    # v0 (pilot 1): débil — el modelo suele ignorar el dx.
    "soft": (
        "The most likely diagnosis for this skin lesion is {dx}. Write a structured clinical "
        "report describing the lesion's morphology, dermatoscopic features and findings "
        "consistent with this diagnosis."
    ),
    # v1: el dx PRIMERO y como apertura obligada del reporte.
    "dxfirst": (
        "Diagnosis: {dx}. Write a clinical report that begins by stating this diagnosis "
        "({dx}), then describes the dermatoscopic and morphological features that support it."
    ),
    # v2: conclusión obligada con el dx textual.
    "conclude": (
        "Write a structured clinical report for this skin lesion. You must end the report "
        "with this exact line: 'Most likely diagnosis: {dx}.'"
    ),
    # v3: dx confirmado, nombrarlo explícito, sin listar diferenciales.
    "confirmed": (
        "The confirmed diagnosis is {dx}. Write a concise clinical report that explicitly "
        "names this diagnosis ({dx}) and describes the supporting morphological and "
        "dermatoscopic features. Do not list alternative or differential diagnoses."
    ),
    # v4: prohíbe explícitamente el razonamiento/<think>; solo el reporte final comprometido.
    "noreasoning": (
        "The confirmed diagnosis is {dx}. Output ONLY the final clinical report — do NOT include "
        "any reasoning, thinking steps, or <think> blocks. The report must explicitly state the "
        "diagnosis ({dx}) and describe the supporting morphological and dermatoscopic features. "
        "Do not mention alternative or differential diagnoses."
    ),
}


def _generate_single(model, image_path: Path, max_tokens: int, prompt: str = REPORT_PROMPT,
                     no_image: bool = False) -> str:
    """Genera reporte para una imagen con el prompt dado (default: REPORT_PROMPT).

    Si no_image=True (ablación P1.2 "aporte de la imagen"), se reemplaza la imagen por
    una imagen neutra en gris: el modelo solo dispone del diagnóstico inyectado en el
    prompt, permitiendo medir cuánto sigue usando la señal visual una vez conocido el dx.
    """
    if no_image:
        image = Image.new("RGB", (336, 336), (128, 128, 128))
    else:
        image = Image.open(image_path).convert("RGB")
    reports = model.generate(
        images=[image],
        prompts=[prompt],
        max_new_tokens=max_tokens,
    )
    return reports[0]


def main():
    parser = argparse.ArgumentParser(description="Genera reporte clínico para imagen(es)")
    parser.add_argument("--model", type=str, required=True,
                        choices=["llava_med", "mini_vlm", "skinvl"])
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
                             "<reference_dir>/A/B.jpg.txt (formato SkinCoT). "
                             "Los bloques <think>...</think> se eliminan automáticamente.")
    parser.add_argument("--label_csv", type=str, default=None,
                        help="CSV con columnas skincap_file_path/image_id y disease para "
                             "poblar gt_label. Si no hay match en el CSV, se usa el nombre "
                             "de la carpeta padre de la imagen (estructura SkinCoT).")
    parser.add_argument("--max_tokens", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    # Ensamble cascada (grounding): inyecta el dx de un clasificador en el prompt.
    parser.add_argument("--diagnosis_source", type=str, default=None,
                        help="CSV con columnas image_id,diagnosis (dx en nombre completo) para "
                             "grounding. La clave se matchea por nombre de archivo o stem.")
    parser.add_argument("--grounded_prompt", action="store_true",
                        help="Si se pasa, usa el template de grounding con el dx de "
                             "--diagnosis_source por imagen; si no hay dx, cae al REPORT_PROMPT.")
    parser.add_argument("--grounded_variant", type=str, default="soft",
                        choices=list(GROUNDED_TEMPLATES.keys()),
                        help="Variante de prompt de grounding (soft|dxfirst|conclude|confirmed).")
    parser.add_argument("--no_image", action="store_true",
                        help="Ablación P1.2: reemplaza la imagen por una neutra (gris). Con "
                             "--grounded_prompt mide cuánto aporta la imagen una vez conocido el dx.")
    parser.add_argument("--limit", type=int, default=None,
                        help="Procesar a lo sumo N imágenes (para pilots).")
    parser.add_argument("--splits_file", type=str, default=None,
                        help="JSON de splits {train,val,test:[image_ids]}. Si se pasa con --split, "
                             "restringe la generación a las imágenes de ese split.")
    parser.add_argument("--split", type=str, default=None,
                        help="Split a usar (train|val|test) si se pasa --splits_file.")
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
            report = _generate_single(model, image_path, args.max_tokens, no_image=args.no_image)

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

        if args.splits_file and args.split:
            with open(args.splits_file, encoding="utf-8") as f:
                split_ids = set(json.load(f).get(args.split, []))
            before = len(image_paths)
            image_paths = [p for p in image_paths if p.stem in split_ids]
            logger.info("Split '%s': %d/%d imágenes tras filtrar por %s",
                        args.split, len(image_paths), before, args.splits_file)

        if args.limit is not None:
            image_paths = image_paths[: args.limit]
            logger.info("Limit: procesando a lo sumo %d imágenes", len(image_paths))

        def _is_valid_report(path: Path) -> bool:
            """True si el archivo existe y tiene un reporte no vacío (resume defensivo)."""
            if not path.exists():
                return False
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                return bool(data.get("report", "").strip())
            except (json.JSONDecodeError, OSError):
                return False

        # Cargar labels desde CSV (ej: SkinCAP skincap_v240623.csv)
        label_lookup: dict[str, str] = {}
        if args.label_csv:
            import pandas as pd
            lbl_df = pd.read_csv(args.label_csv)
            id_col = "skincap_file_path" if "skincap_file_path" in lbl_df.columns else "image_id"
            for _, row in lbl_df.iterrows():
                img_id = Path(str(row.get(id_col, ""))).name
                label = str(row.get("disease", "")).strip()
                if img_id and label:
                    label_lookup[img_id] = label

        # Cargar diagnósticos para grounding (ensamble cascada): image_id -> dx_full
        diagnosis_lookup: dict[str, str] = {}
        if args.diagnosis_source:
            import pandas as pd
            dx_df = pd.read_csv(args.diagnosis_source)
            for _, row in dx_df.iterrows():
                key = str(row.get("image_id", "")).strip()
                dx = str(row.get("diagnosis", "")).strip()
                if key and dx:
                    diagnosis_lookup[key] = dx
                    diagnosis_lookup[Path(key).stem] = dx  # tolerar con/sin extensión
            logger.info("Grounding: %d diagnósticos cargados de %s",
                        len(dx_df), args.diagnosis_source)

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

        skipped = sum(
            1 for p in image_paths
            if _is_valid_report(output_dir / f"{p.stem}_report.json")
        )
        if skipped:
            logger.info(
                "Resume: %d/%d reportes ya existen y son válidos, se saltarán",
                skipped, len(image_paths),
            )

        logger.info("Generando reportes para %d imágenes...", len(image_paths))
        processed = 0
        for i, img_path in enumerate(image_paths):
            out_file = output_dir / f"{img_path.stem}_report.json"
            if _is_valid_report(out_file):
                continue
            try:
                rel = img_path.relative_to(images_dir)

                # Resolver referencia: primero reference_dir, luego reference_csv
                reference = references.get(img_path.name, "")
                if not reference and reference_dir is not None:
                    # Misma subestructura que images_dir: <reference_dir>/A/B.jpg.txt
                    txt_path = reference_dir / rel.parent / (rel.name + ".txt")
                    if txt_path.exists():
                        raw = txt_path.read_text(encoding="utf-8").strip()
                        reference = _strip_cot(raw)

                # Resolver gt_label: CSV primero, luego carpeta padre (SkinCoT)
                gt_label = label_lookup.get(img_path.name, "")
                if not gt_label and rel.parent != Path("."):
                    gt_label = rel.parent.name

                # Resolver prompt: grounded (con dx del clasificador) o el default
                prompt = REPORT_PROMPT
                grounded_dx = ""
                if args.grounded_prompt:
                    grounded_dx = (
                        diagnosis_lookup.get(img_path.name)
                        or diagnosis_lookup.get(img_path.stem, "")
                    )
                    if grounded_dx:
                        prompt = GROUNDED_TEMPLATES[args.grounded_variant].format(dx=grounded_dx)

                report = _generate_single(model, img_path, args.max_tokens, prompt=prompt,
                                          no_image=args.no_image)
                result = {
                    "image_id": img_path.name,
                    "model": args.model,
                    "checkpoint": args.checkpoint,
                    "report": report,
                    "reference": reference,
                    "gt_label": gt_label,
                    "grounded_dx": grounded_dx,
                    "prompt": prompt,
                }
                save_results(result, str(out_file))
                processed += 1

                if processed % 10 == 0 or processed == 1:
                    logger.info(
                        "Progreso: %d nuevos / %d totales (de %d imágenes)",
                        processed, processed + skipped, len(image_paths),
                    )
            except Exception as e:
                logger.warning("Error procesando %s: %s", img_path.name, e)

        logger.info(
            "Reportes guardados en %s (%d nuevos, %d ya existían)",
            output_dir, processed, skipped,
        )


if __name__ == "__main__":
    main()
