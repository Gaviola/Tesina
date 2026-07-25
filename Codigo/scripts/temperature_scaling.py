"""P5.4 (soporte) — Temperature scaling + CSV de incertidumbre para el generador.

Calibra el clasificador Swin con temperature scaling ajustado en el split de VALIDACIÓN, y produce
un CSV por imagen de test con: top-k diagnósticos, confianza calibrada del top-1, y una bandera
`confident` (confianza > umbral τ). El umbral se elige en validación como el punto de operación de
alta precisión (exactitud del subconjunto "confiado" ≥ objetivo).

El generador (generate_report.py --uncertainty_csv) usará esto para producir un reporte DEFINITIVO
cuando el clasificador está seguro, o un reporte DIFERENCIAL (lista de candidatos) cuando no lo está.

Local (RTX 4070). Uso:
    python scripts/temperature_scaling.py --target-acc 0.90
"""

import argparse
import csv
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from torch.utils.data import DataLoader

from src.data.collators import ClassificationCollator
from src.data.ham10000 import HAM10000Dataset, HAM10000_CLASSES
from src.data.transforms import get_val_transforms
from src.evaluation.tta import evaluate_with_tta
from src.models.factory import build_model
from src.utils.device import get_device, get_training_dtype
from src.utils.seed import set_seed

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DX_FULL = {
    "MEL": "melanoma", "NV": "nevus", "BCC": "basal cell carcinoma",
    "AKIEC": "actinic keratosis", "BKL": "benign keratosis",
    "DF": "dermatofibroma", "VASC": "vascular lesion",
}
CKPT = "outputs/checkpoints/swin_tiny_modern_v3/best_model.pt"


def _probs_for_split(model, split, device, dtype, splits_file, data_root):
    tfm = get_val_transforms(size=224, center_crop=True)
    ds = HAM10000Dataset(root_dir=data_root, split=split, transform=tfm, splits_file=splits_file)
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0,
                        collate_fn=ClassificationCollator())
    _, y_true, y_prob = evaluate_with_tta(model, loader, device, dtype, num_classes=7,
                                          tta_modes=("original", "hflip"))
    ids = [s["image_id"] for s in ds.samples]
    return np.asarray(ids), np.asarray(y_true), np.asarray(y_prob, dtype=float)


def _fit_temperature(probs, y_true):
    """Ajusta T (escalar) minimizando NLL. Usa logits proxy = log(prob) (softmax es invariante al
    corrimiento, así que log(p) recupera los logits salvo constante por fila)."""
    logits = np.log(np.clip(probs, 1e-12, 1.0))
    lt = torch.tensor(logits, dtype=torch.float64)
    yt = torch.tensor(y_true, dtype=torch.long)
    logT = torch.zeros(1, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([logT], lr=0.1, max_iter=100)
    nll = torch.nn.CrossEntropyLoss()

    def closure():
        opt.zero_grad()
        loss = nll(lt / torch.exp(logT), yt)
        loss.backward()
        return loss
    opt.step(closure)
    return float(torch.exp(logT).item())


def _apply_T(probs, T):
    logits = np.log(np.clip(probs, 1e-12, 1.0)) / T
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def _ece(probs, y_true, n_bins=10):
    conf = probs.max(1); pred = probs.argmax(1); acc = (pred == y_true).astype(float)
    bins = np.linspace(0, 1, n_bins + 1); ece = 0.0
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.any():
            ece += m.mean() * abs(acc[m].mean() - conf[m].mean())
    return ece


def main():
    parser = argparse.ArgumentParser(description="P5.4 Temperature scaling + CSV de incertidumbre")
    parser.add_argument("--target-acc", type=float, default=0.90,
                        help="Exactitud objetivo del subconjunto 'confiado' para elegir τ en val.")
    parser.add_argument("--topk", type=int, default=3)
    parser.add_argument("--data-dir", type=str, default="data")
    parser.add_argument("--output", type=str, default="outputs/uncertainty/uncertainty.csv")
    args = parser.parse_args()

    set_seed(42)
    device = get_device(); dtype = get_training_dtype()
    splits_file = str(Path(args.data_dir) / "splits" / "ham10000_splits.json")
    data_root = str(Path(args.data_dir) / "processed" / "HAM10000")
    model = build_model({"name": "swin_tiny", "num_classes": 7})
    ck = torch.load(CKPT, map_location="cpu", weights_only=False)
    model.load_state_dict(ck.get("model_state_dict", ck), strict=True)
    model.to(device)

    logger.info("Infiriendo VAL...")
    _, yv, pv = _probs_for_split(model, "val", device, dtype, splits_file, data_root)
    logger.info("Infiriendo TEST...")
    ids_te, yte, pte = _probs_for_split(model, "test", device, dtype, splits_file, data_root)

    T = _fit_temperature(pv, yv)
    pv_cal = _apply_T(pv, T); pte_cal = _apply_T(pte, T)
    # Guardar probs calibradas para tunear τ sin re-inferir.
    np.savez("outputs/uncertainty/cal_probs.npz", ids_te=ids_te, yte=yte, pte_cal=pte_cal,
             yv=yv, pv_cal=pv_cal, T=T)
    logger.info("T=%.3f | ECE val %.3f->%.3f | ECE test %.3f->%.3f", T,
                _ece(pv, yv), _ece(pv_cal, yv), _ece(pte, yte), _ece(pte_cal, yte))

    # Elegir τ en VALIDACIÓN: el menor umbral tal que la exactitud de los "confiados" >= target.
    conf_v = pv_cal.max(1); pred_v = pv_cal.argmax(1)
    tau, best = 0.5, None
    for t in np.linspace(0.2, 0.95, 76):
        m = conf_v >= t
        if m.sum() >= 30 and (pred_v[m] == yv[m]).mean() >= args.target_acc:
            tau = float(t); best = (m.mean(), (pred_v[m] == yv[m]).mean()); break
    cov = (conf_v >= tau).mean()
    logger.info("τ=%.3f (val: cobertura %.2f, exactitud confiados %.3f)", tau,
                cov, best[1] if best else float("nan"))

    # Métrica clave en TEST: en los INCONFIADOS, ¿el top-k contiene el gt más que el top-1?
    conf_te = pte_cal.max(1); unc = conf_te < tau
    top1 = pte_cal.argmax(1)
    topk_idx = np.argsort(-pte_cal, axis=1)[:, :args.topk]
    top1_recall_unc = (top1[unc] == yte[unc]).mean() if unc.any() else float("nan")
    topk_recall_unc = np.mean([yte[i] in topk_idx[i] for i in np.where(unc)[0]]) if unc.any() else float("nan")
    logger.info("TEST inconfiados: %d/%d (%.0f%%). top1 recall %.3f -> top%d recall %.3f",
                unc.sum(), len(yte), 100 * unc.mean(), top1_recall_unc, args.topk, topk_recall_unc)

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image_id", "unc_dx", "unc_candidates", "unc_conf", "unc_confident"])
        for i, iid in enumerate(ids_te):
            cand = [DX_FULL[HAM10000_CLASSES[j]] for j in topk_idx[i]]
            w.writerow([iid, cand[0], "; ".join(cand), f"{conf_te[i]:.3f}",
                        int(conf_te[i] >= tau)])
    logger.info("CSV: %s (n=%d, τ=%.3f, T=%.3f)", out, len(ids_te), tau, T)

    # Guardar metadatos para el resul.
    import json
    Path("outputs/uncertainty/meta.json").write_text(json.dumps({
        "T": T, "tau": tau, "coverage_test": float((conf_te >= tau).mean()),
        "n_uncertain_test": int(unc.sum()),
        "top1_recall_uncertain": float(top1_recall_unc),
        "topk_recall_uncertain": float(topk_recall_unc),
        "ece_test_raw": float(_ece(pte, yte)), "ece_test_cal": float(_ece(pte_cal, yte)),
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
