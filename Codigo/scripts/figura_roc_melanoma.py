"""Curva ROC de melanoma frente al resto, Swin-Tiny semilla 42, con los dos puntos de operación de 4.2."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

BASE = "C:/Users/Facu/1/Facultad/Tesina"
p = json.load(open(f"{BASE}/Codigo/outputs/results/swin_tiny_sweep_t06_les_cwnone_predictions.json", encoding="utf8"))
y = np.array(p["y_true"]) == 0                      # MEL = índice 0
prob = np.array(p["y_prob"])
s = prob[:, 0]
pred = prob.argmax(1) == 0
THR = 0.211                                          # umbral fijado en validación (lesion_split_report.json)

fpr, tpr, _ = roc_curve(y, s)
auc = roc_auc_score(y, s)
op_arg = (1 - (~y & ~pred).sum() / (~y).sum(), (y & pred).sum() / y.sum())
op_thr = (1 - (~y & (s < THR)).sum() / (~y).sum(), (y & (s >= THR)).sum() / y.sum())
print(f"AUC {auc:.3f}; argmax sens {op_arg[1]:.3f} esp {1-op_arg[0]:.3f}; umbral sens {op_thr[1]:.3f} esp {1-op_thr[0]:.3f}")

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": "#888888",
                     "axes.linewidth": 0.6, "xtick.color": "#444444", "ytick.color": "#444444"})
fig, ax = plt.subplots(figsize=(4.2, 3.6))
ax.plot([0, 1], [0, 1], ls=(0, (3, 3)), lw=0.8, color="#999999")
ax.plot(fpr, tpr, lw=2, color="#0072B2")
ax.axvline(0.15, lw=0.8, ls=":", color="#999999")
ax.text(0.155, 0.04, "especificidad 0.85", fontsize=7.5, color="#555555")
ax.plot(*op_arg, "o", ms=8, color="#009E73", mec="white", mew=1.2, zorder=5)
ax.plot(*op_thr, "s", ms=8, color="#D55E00", mec="white", mew=1.2, zorder=5)
ax.annotate(f"Clase más probable\n(sens. {op_arg[1]:.3f}, esp. {1-op_arg[0]:.3f})", op_arg,
            xytext=(0.20, 0.50), fontsize=8, color="#222222",
            arrowprops=dict(arrowstyle="-", lw=0.6, color="#666666"))
ax.annotate(f"Umbral de validación\n(sens. {op_thr[1]:.3f}, esp. {1-op_thr[0]:.3f})", op_thr,
            xytext=(0.30, 0.68), fontsize=8, color="#222222",
            arrowprops=dict(arrowstyle="-", lw=0.6, color="#666666"))
ax.text(0.97, 0.08, f"AUC = {auc:.3f}", ha="right", fontsize=8.5, color="#222222")
ax.set_xlabel("1 $-$ especificidad")
ax.set_ylabel("Sensibilidad")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.01)
ax.grid(lw=0.4, color="#e6e6e6")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
out = f"{BASE}/Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion/roc-melanoma-swin.pdf"
fig.savefig(out)
