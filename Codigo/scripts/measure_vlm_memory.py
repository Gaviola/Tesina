"""Memoria de GPU y parámetros de los generadores, medidos en la GPU del clúster.

Completa la tabla de costo de los generadores (Cap. 5, sec:res_costo), que antes estimaba la memoria como
parámetros x 2 bytes (REFERENCE de measure_cost.py). Carga el generador igual que generate_report.py (bf16, mismo
checkpoint y LoRA), cuenta los parámetros y mide con torch.cuda.max_memory_allocated:
  - después de cargar (pesos + LoRA en la GPU);
  - el pico durante la generación de N reportes de la cascada con Swin-Tiny (plantilla noreasoning, 384 tokens),
    las mismas condiciones que la tabla de tiempos.
Los reportes no se guardan: solo se registra su largo y el tiempo de cada uno.

Uso (en un nodo con GPU):
    python scripts/measure_vlm_memory.py --model mini_vlm \\
        --checkpoint outputs/checkpoints/stage2_mini_vlm_v2/best_model.pt --n 20
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import torch

from generate_report import GROUNDED_TEMPLATES, _generate_single, _load_model_with_checkpoint
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GIB = 2**30


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, choices=["llava_med", "mini_vlm", "skinvl"])
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--n", type=int, default=20, help="Reportes a generar para el pico de memoria")
    parser.add_argument("--images_dir", default="data/processed/HAM10000")
    parser.add_argument("--splits_file", default="data/splits/ham10000_splits.json")
    parser.add_argument("--diagnosis_source", default="outputs/full_dx_swin_les.csv")
    parser.add_argument("--max_tokens", type=int, default=384)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=None, help="JSON de salida (por defecto outputs/results/cost/)")
    args = parser.parse_args()

    if not torch.cuda.is_available():
        logger.error("Hace falta una GPU: la medición no tiene sentido en CPU.")
        sys.exit(1)
    set_seed(args.seed)
    torch.cuda.reset_peak_memory_stats()

    model = _load_model_with_checkpoint(args)
    torch.cuda.synchronize()
    mem_load = torch.cuda.max_memory_allocated() / GIB
    reserved_load = torch.cuda.memory_reserved() / GIB
    params = sum(p.numel() for p in model.model.parameters())
    trainable = sum(p.numel() for n, p in model.model.named_parameters() if "lora_" in n)
    dtypes = sorted({str(p.dtype) for p in model.model.parameters()})
    logger.info("Cargado: %.3f GiB asignados, %.3f GiB reservados, %d parámetros (%d de LoRA), dtypes %s",
                mem_load, reserved_load, params, trainable, dtypes)

    # Las primeras N imágenes de la prueba, en el orden de generate_report.py (sorted), con el ancla de Swin-Tiny.
    with open(args.splits_file, encoding="utf-8") as f:
        test_ids = set(json.load(f)["test"])
    images = sorted(p for p in Path(args.images_dir).rglob("*.jpg") if p.stem in test_ids)[: args.n]
    dx = dict(pd.read_csv(args.diagnosis_source)[["image_id", "diagnosis"]].values)

    torch.cuda.reset_peak_memory_stats()
    times, words = [], []
    for img in images:
        prompt = GROUNDED_TEMPLATES["noreasoning"].format(dx=dx[img.stem])
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        report = _generate_single(model, img, args.max_tokens, prompt=prompt)
        torch.cuda.synchronize()
        times.append(time.perf_counter() - t0)
        words.append(len(report.split()))
    mem_gen = torch.cuda.max_memory_allocated() / GIB
    reserved_gen = torch.cuda.max_memory_reserved() / GIB

    gpu = torch.cuda.get_device_name(0)
    result = {
        "model": args.model,
        "checkpoint": args.checkpoint,
        "gpu": gpu,
        "torch": torch.__version__,
        "dtypes": dtypes,
        "params": params,
        "params_lora": trainable,
        "mem_carga_gib": round(mem_load, 3),
        "mem_reservada_carga_gib": round(reserved_load, 3),
        "mem_pico_generacion_gib": round(mem_gen, 3),
        "mem_reservada_pico_gib": round(reserved_gen, 3),
        "n_reportes": len(images),
        "seg_por_reporte_mediana": round(float(pd.Series(times).median()), 2),
        "palabras_mediana": float(pd.Series(words).median()),
        "condicion": f"cascada Swin-Tiny, noreasoning, {args.max_tokens} tokens, primeras {len(images)} de la prueba",
        "fuente": f"medido ({gpu}), torch.cuda.max_memory_allocated",
        "fecha": datetime.now().isoformat(timespec="seconds"),
    }
    out = Path(args.output or f"outputs/results/cost/vlm_memory_{args.model}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Resultado en %s:\n%s", out, json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
