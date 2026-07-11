"""P0.4 (plan julio-agosto) — Comparación de costo computacional.

Compara los modelos por parámetros, memoria y latencia de inferencia. Es el eje "costo"
de la tesina: ¿qué se puede correr en hardware modesto (RTX 4070 12GB) vs qué exige un A30?

- Clasificadores (torchvision): parámetros + latencia medidos EN VIVO en la GPU local.
- VLMs generativos: latencia real por-reporte parseada de los logs SLURM del cluster (A30).
- Params/VRAM de VLMs y DermLIP: tabla de referencia (no cargan local: falta VRAM / open_clip).

Uso:
    python scripts/measure_cost.py
"""

import argparse
import glob
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch
import torchvision.models as tvm

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Clasificadores torchvision (instancian local sin descargar pesos: weights=None).
CLASSIFIERS = {
    "DenseNet121": tvm.densenet121,
    "ViT-B/16": tvm.vit_b_16,
    "ConvNeXt-Tiny": tvm.convnext_tiny,
    "Swin-Tiny": tvm.swin_t,
}

# Referencia para modelos que no cargan local (params en M, VRAM inferencia bf16 en GB).
REFERENCE = {
    "DermLIP (ViT-B/16)": {"params_m": 150, "vram_gb": 2, "hw": "RTX 4070", "role": "VL-classifier"},
    "Mini-VLM (Phi-3.5-V)": {"params_m": 4200, "vram_gb": 10, "hw": "A30 / RTX 4080", "role": "VLM-gen"},
    "LLaVA-Med v1.5 (7B)": {"params_m": 7000, "vram_gb": 14, "hw": "A30 24GB", "role": "VLM-gen"},
    "SkinVL-MM (7B)": {"params_m": 7000, "vram_gb": 14, "hw": "A30 24GB", "role": "VLM-gen"},
}

# Logs SLURM de generación para extraer s/reporte (A30).
GEN_LOGS = {
    "LLaVA-Med v1.5 (7B)": "outputs/slurm_logs/llava_med/*.out",
    "Mini-VLM (Phi-3.5-V)": "outputs/slurm_logs/mini_vlm/*.out",
}
_PROG_RE = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\].*Progreso:\s*\d+\s*nuevos?\s*/\s*(\d+)\s*totales")


@torch.no_grad()
def _bench_classifier(ctor, device, img=224, warmup=5, iters=20):
    model = ctor(weights=None).to(device).eval()
    n_params = sum(p.numel() for p in model.parameters())
    lat = {}
    for bs in (1, 32):
        x = torch.randn(bs, 3, img, img, device=device)
        for _ in range(warmup):
            model(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        for _ in range(iters):
            model(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
        dt = (time.perf_counter() - t0) / iters
        lat[bs] = dt
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return n_params, lat


def _gen_latency_from_logs(glob_pat: str) -> float | None:
    """s/reporte estimado a partir de las líneas 'Progreso' de los logs (mediana entre logs)."""
    rates = []
    for lf in glob.glob(glob_pat):
        pts = []
        for line in Path(lf).read_text(encoding="utf-8", errors="ignore").splitlines():
            m = _PROG_RE.search(line)
            if m:
                t = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                pts.append((t, int(m.group(2))))
        if len(pts) >= 2:
            (t0, n0), (t1, n1) = pts[0], pts[-1]
            if n1 > n0:
                rates.append((t1 - t0).total_seconds() / (n1 - n0))
    if not rates:
        return None
    rates.sort()
    return rates[len(rates) // 2]


def main():
    parser = argparse.ArgumentParser(description="P0.4 Comparación de costo")
    parser.add_argument("--output", type=str, default="outputs/results/cost/cost_comparison.json")
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gpu = torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU"
    logger.info("Midiendo latencia de clasificadores en: %s", gpu)

    rows = []

    # Clasificadores (medidos en vivo)
    for name, ctor in CLASSIFIERS.items():
        try:
            n_params, lat = _bench_classifier(ctor, device)
            rows.append({
                "modelo": name, "role": "classifier",
                "params_m": round(n_params / 1e6, 1),
                "vram_gb": round(n_params * 4 / 1e9 + 0.5, 1),  # fp32 aprox + overhead
                "latency_ms_bs1": round(lat[1] * 1000, 2),
                "throughput_img_s_bs32": round(32 / lat[32], 1),
                "hw": "RTX 4070 12GB",
                "fuente": f"medido ({gpu})",
            })
            logger.info("%-16s params=%.1fM  bs1=%.2fms  thr(bs32)=%.0f img/s",
                        name, n_params / 1e6, lat[1] * 1000, 32 / lat[32])
        except Exception as e:
            logger.warning("No se pudo medir %s: %s", name, e)

    # Modelos de referencia (no cargan local) + latencia de generación desde logs
    for name, ref in REFERENCE.items():
        gen_s = _gen_latency_from_logs(GEN_LOGS[name]) if name in GEN_LOGS else None
        rows.append({
            "modelo": name, "role": ref["role"],
            "params_m": ref["params_m"],
            "vram_gb": ref["vram_gb"],
            "latency_ms_bs1": None,
            "throughput_img_s_bs32": None,
            "gen_s_por_reporte": round(gen_s, 1) if gen_s else None,
            "hw": ref["hw"],
            "fuente": "log A30" if gen_s else "referencia",
        })
        if gen_s:
            logger.info("%-16s ~%.1f s/reporte (A30, de logs)", name, gen_s)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    # Figura: latencia por item (ms, escala log) — muestra los ~4 órdenes de magnitud de brecha.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    labels, vals, colors = [], [], []
    role_color = {"classifier": "#4CAF50", "VL-classifier": "#1565C0", "VLM-gen": "#C62828"}
    for r in rows:
        ms = (r["gen_s_por_reporte"] * 1000) if r.get("gen_s_por_reporte") else r.get("latency_ms_bs1")
        if ms:
            labels.append(r["modelo"])
            vals.append(ms)
            colors.append(role_color.get(r["role"], "gray"))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(labels, vals, color=colors)
    ax.set_xscale("log")
    ax.set_xlabel("Latencia por item (ms, escala log) — clasificador: /imagen · VLM: /reporte")
    ax.set_title("Costo de inferencia: clasificadores (RTX 4070) vs VLMs generativos (A30)")
    for i, v in enumerate(vals):
        ax.text(v * 1.1, i, f"{v:.0f} ms" if v < 1000 else f"{v/1000:.0f} s", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(out.parent / "cost_latency.png", dpi=150)
    logger.info("Figura: %s", out.parent / "cost_latency.png")

    # Tabla a stdout
    print("\n=== Comparacion de costo ===")
    print(f"{'Modelo':<22}{'rol':<14}{'params(M)':>10}{'VRAM(GB)':>9}{'lat/item':>14}{'hardware':>16}")
    for r in rows:
        if r.get("gen_s_por_reporte"):
            lat = f"{r['gen_s_por_reporte']:.1f} s/rep"
        elif r.get("latency_ms_bs1"):
            lat = f"{r['latency_ms_bs1']:.1f} ms"
        else:
            lat = "-"
        print(f"{r['modelo']:<22}{r['role']:<14}{r['params_m']:>10}{r['vram_gb']:>9}{lat:>14}{r['hw']:>16}")
    logger.info("Guardado en %s", out)


if __name__ == "__main__":
    main()
