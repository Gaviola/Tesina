"""Figuras del Cap. 4 (reorganización del 24/10): resumen de sensibilidad macro, matriz de confusión de Swin-Tiny,
robustez, calibración, HIBA por clase y distribución de predicciones de los VLM generativos.

Lee solo JSON de outputs/results/ (semilla 42 salvo donde se indica media ± desvío) y escribe PDF en
Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion/.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, recall_score

BASE = "C:/Users/Facu/1/Facultad/Tesina"
RES = f"{BASE}/Codigo/outputs/results"
OUT = f"{BASE}/Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion"
CLASES = ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]
AZAR = 1 / 7

# Okabe–Ito (Configurations/13-Figuras.sty)
AZUL, NARANJA, CELESTE, VERDE, AMARILLO, BERMELLON, PURPURA = (
    "#0072B2", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#D55E00", "#CC79A7")
GRIS = "#999999"
COLOR_CLASE = {"MEL": BERMELLON, "NV": AZUL, "BCC": NARANJA, "AKIEC": CELESTE, "BKL": VERDE, "DF": AMARILLO,
               "VASC": PURPURA}

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": "#888888",
                     "axes.linewidth": 0.6, "xtick.color": "#444444", "ytick.color": "#444444",
                     "axes.titlesize": 9})


def cargar(ruta):
    return json.load(open(f"{RES}/{ruta}", encoding="utf8"))


def sens_macro(y, p):
    """Sensibilidad macro con las respuestas sin etiqueta (-1) contadas como error."""
    return recall_score(y, p, labels=list(range(7)), average="macro", zero_division=0)


def limpiar(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(lw=0.4, color="#e6e6e6")
    ax.set_axisbelow(True)


VLM = [  # (modelo, estrategia, archivo); mismas fuentes que la ficha 4.3
    ("Mini-VLM", "Generación", "mini_vlm/v1/mini_vlm_predictions.json"),
    ("Mini-VLM", "Verosimilitud", "mini_vlm/v1/mini_vlm_likelihood_predictions.json"),
    ("Mini-VLM", "CoT", "mini_vlm/v1/mini_vlm_cot_predictions.json"),
    ("Mini-VLM", "Ajuste y verosimilitud", "mini_vlm/v2/mini_vlm_likelihood_finetuned_predictions.json"),
    ("Mini-VLM", "Ajuste y CoT", "mini_vlm/v2/mini_vlm_cot_finetuned_predictions.json"),
    ("LLaVA-Med", "Generación", "llava_med/v1/llava_med_predictions.json"),
    ("LLaVA-Med", "Verosimilitud", "llava_med/v1/llava_med_likelihood_predictions.json"),
    ("LLaVA-Med", "CoT", "llava_med/v1/llava_med_cot_predictions.json"),
    ("LLaVA-Med", "Ajuste y verosimilitud", "llava_med/v2/llava_med_likelihood_finetuned_predictions.json"),
    ("LLaVA-Med", "Ajuste y CoT", "llava_med/v2/llava_med_cot_finetuned_predictions.json"),
]


def fig_resumen():
    """Sensibilidad macro de todos los clasificadores, con la línea del azar."""
    ms = cargar("densenet_vit_moderna_report.json")["media_std"]
    ens = cargar("classifier_ensemble_les/ensemble_seeds.json")["por_semilla"]
    ens_v = [ens[s]["swin+convnext"]["sens_macro"] for s in ("42", "43", "44")]
    dl = cargar("dermlip/dermlip_split_eval.json")["lesion"]

    filas = []  # (etiqueta, valores, desvío, color)
    filas.append(("Ensamble Swin + ConvNeXt", [np.mean(ens_v)], np.std(ens_v), AZUL))
    for m in ("Swin-Tiny", "ConvNeXt-Tiny", "ViT-B/16", "DenseNet121"):
        filas.append((m, [ms[m]["sens_macro"]["mean"]], ms[m]["sens_macro"]["std"], AZUL))
    filas.append(("DermLIP + regresión logística", [dl["linear-probe (LogReg)"]["sens_macro"]], 0, VERDE))
    filas.append(("DermLIP + SVM", [dl["SVM-RBF"]["sens_macro"]], 0, VERDE))
    filas.append(("DermLIP + kNN", [dl["kNN (k=3)"]["sens_macro"]], 0, VERDE))
    zs = cargar("dermlip/dermlip_zeroshot_vit-b-16_oficial_predictions.json")  # protocolo oficial de Derm1M
    filas.append(("DermLIP sin ajuste", [sens_macro(zs["y_true"], zs["y_pred"])], 0, VERDE))
    for modelo in ("Mini-VLM", "LLaVA-Med"):
        vals = []
        for m, _, f in VLM:
            if m == modelo:
                p = cargar(f)
                vals.append(sens_macro(p["y_true"], p["y_pred"]))
        filas.append((f"{modelo} (5 estrategias)", vals, 0, BERMELLON))
    for et, v, _, _ in filas:
        print(f"  {et}: {', '.join(f'{x:.3f}' for x in v)}")

    fig, ax = plt.subplots(figsize=(5.6, 3.9))
    y = np.arange(len(filas))[::-1].astype(float)
    y[5:] -= 0.5
    y[9:] -= 0.5
    for yi, (et, v, sd, c) in zip(y, filas):
        if len(v) > 1:
            ax.plot([min(v), max(v)], [yi, yi], lw=1.2, color=c, alpha=0.5)
            ax.plot(v, [yi] * len(v), "o", ms=5, color=c, mec="white", mew=0.8)
        else:
            if sd:
                ax.errorbar(v[0], yi, xerr=sd, fmt="none", ecolor=c, elinewidth=1, capsize=2.5)
            ax.plot(v[0], yi, "o", ms=7, color=c, mec="white", mew=1)
    ax.axvline(AZAR, lw=0.9, ls=(0, (3, 3)), color=GRIS)
    ax.text(AZAR + 0.008, y[0] + 0.55, "azar (1/7)", fontsize=7.5, color="#555555", va="bottom")
    ax.set_yticks(y)
    ax.set_yticklabels([f[0] for f in filas])
    ax.set_xlim(0, 0.8)
    ax.set_ylim(y[-1] - 0.7, y[0] + 1.2)
    ax.set_xlabel("Sensibilidad macro en el conjunto de prueba")
    for yy, txt in ((y[0], "Supervisados"), (y[5], "DermLIP (contrastivo)"), (y[9], "Generativos")):
        ax.text(0.27, yy, txt, ha="left", va="center", fontsize=7.5, style="italic", color="#555555")
    limpiar(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/resumen-sensibilidad-macro.pdf")


def fig_confusion():
    p = cargar("swin_tiny_sweep_t06_les_cwnone_predictions.json")
    cm = confusion_matrix(p["y_true"], np.array(p["y_prob"]).argmax(1), labels=range(7))
    cmn = cm / cm.sum(1, keepdims=True)
    fig, ax = plt.subplots(figsize=(4.4, 3.9))
    im = ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
    for i in range(7):
        for j in range(7):
            if cm[i, j]:
                ax.text(j, i, f"{cmn[i, j]:.2f}" if cmn[i, j] >= 0.005 else "<0.01", ha="center", va="center", fontsize=7.5,
                        color="white" if cmn[i, j] > 0.55 else "#222222")
            else:
                ax.text(j, i, "–", ha="center", va="center", fontsize=7.5, color="#777777")
    n = cm.sum(1)
    ax.set_xticks(range(7))
    ax.set_xticklabels(CLASES, fontsize=8)
    ax.set_yticks(range(7))
    ax.set_yticklabels([f"{c} ({k})" for c, k in zip(CLASES, n)], fontsize=8)
    ax.set_xlabel("Clase predicha")
    ax.set_ylabel("Clase real (imágenes)")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(f"{OUT}/confusion-swin.pdf")
    print("  diagonal:", ", ".join(f"{c} {v:.3f}" for c, v in zip(CLASES, np.diag(cmn))))


def fig_robustez():
    r = cargar("robustness/robustness_summary.json")["modelos"]
    niveles = {"jpeg": ("Compresión JPEG (calidad)", ["orig.", 70, 50, 30, 15, 5]),
               "noise": ("Ruido gaussiano (desvío)", ["orig.", 8, 16, 32, 48, 64]),
               "blur": ("Desenfoque (radio)", ["orig.", 1, 2, 3, 4, 6]),
               "resolution": ("Resolución (escala)", ["orig.", 0.75, 0.5, 0.35, 0.25, 0.15])}
    fig, axs = plt.subplots(2, 2, figsize=(5.6, 4.0), sharey=True)
    axs = axs.ravel()
    for ax, (k, (tit, ticks)) in zip(axs, niveles.items()):
        for m, c, mk in (("Swin-Tiny", AZUL, "o"), ("ConvNeXt-Tiny", NARANJA, "s")):
            ax.plot(range(6), r[m]["curves"][k], lw=2, color=c, marker=mk, ms=4, mec="white", mew=0.6, label=m)
        ax.axhline(AZAR, lw=0.8, ls=(0, (3, 3)), color=GRIS)
        ax.set_title(tit, fontsize=8)
        ax.set_xticks(range(6))
        ax.set_xticklabels(ticks, fontsize=7)
        ax.set_ylim(0, 0.75)
        limpiar(ax)
    for ax in axs[::2]:
        ax.set_ylabel("Sensibilidad macro")
    axs[1].text(5, AZAR + 0.02, "azar", fontsize=7, color="#555555", ha="right")
    h, e = axs[0].get_legend_handles_labels()
    fig.tight_layout(h_pad=1.0, rect=(0, 0.06, 1, 1))
    fig.legend(h, e, loc="lower center", ncol=2, frameon=False, fontsize=8)
    fig.savefig(f"{OUT}/robustez-curvas.pdf")


def _confiabilidad(prob, y, bins=10):
    conf = prob.max(1)
    ok = prob.argmax(1) == y
    bordes = np.linspace(0, 1, bins + 1)
    xs, accs, ns, ece = [], [], [], 0.0
    for lo, hi in zip(bordes[:-1], bordes[1:]):
        m = (conf > lo) & (conf <= hi)
        if m.sum():
            xs.append(conf[m].mean())
            accs.append(ok[m].mean())
            ns.append(m.sum())
            ece += m.sum() / len(y) * abs(ok[m].mean() - conf[m].mean())
    return np.array(xs), np.array(accs), np.array(ns), ece, conf.mean(), ok.mean()


def fig_calibracion():
    fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.8), sharey=True)
    for ax, (f, tit) in zip(axs, (("swin_tiny_sweep_t06_les_cwnone_predictions.json", "Sin pesos por clase"),
                                  ("swin_tiny_sweep_t06_les_predictions.json", "Con pesos por clase"))):
        p = cargar(f)
        xs, accs, ns, ece, cm, acc = _confiabilidad(np.array(p["y_prob"]), np.array(p["y_true"]))
        print(f"  {tit}: ECE {ece:.3f}, confianza media {cm:.3f}, exactitud {acc:.3f}")
        ax.plot([0, 1], [0, 1], lw=0.8, ls=(0, (3, 3)), color=GRIS)
        ax.plot(xs, accs, lw=1.5, color=AZUL, zorder=2)
        ax.scatter(xs, accs, s=8 + 60 * ns / ns.max(), color=AZUL, edgecolor="white", lw=0.8, zorder=3)
        ax.set_title(f"{tit} (ECE = {ece:.3f})", fontsize=8.5)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.set_xlabel("Confianza media del intervalo")
        limpiar(ax)
    axs[0].set_ylabel("Exactitud del intervalo")
    axs[0].text(0.03, 0.80, "encima de la diagonal:\nsubconfiado", fontsize=7, color="#555555")
    axs[0].text(0.55, 0.10, "debajo de la diagonal:\nsobreconfiado", fontsize=7, color="#555555")
    fig.tight_layout()
    fig.savefig(f"{OUT}/calibracion-swin.pdf")


def fig_hiba():
    ham = cargar("swin_tiny_sweep_t06_les_cwnone_predictions.json")
    hib = cargar("swin_tiny_sweep_t06_les_cwnone_hiba_predictions_hiba.json")
    r_ham = recall_score(ham["y_true"], np.array(ham["y_prob"]).argmax(1), labels=range(7), average=None)
    r_hib = recall_score(hib["y_true"], hib["y_pred"], labels=range(7), average=None, zero_division=0)
    print("  HAM:", np.round(r_ham, 3), "macro", round(r_ham.mean(), 3))
    print("  HIBA:", np.round(r_hib, 3), "macro", round(r_hib.mean(), 3))
    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    x = np.arange(7)
    w = 0.38
    ax.bar(x - w / 2 - 0.01, r_ham, w, color=AZUL, label="Prueba de HAM10000", edgecolor="white", lw=0.6)
    ax.bar(x + w / 2 + 0.01, r_hib, w, color=NARANJA, label="HIBA", edgecolor="white", lw=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(CLASES)
    ax.set_ylabel("Sensibilidad")
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper right")
    limpiar(ax)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(f"{OUT}/hiba-por-clase-swin.pdf")


def fig_distribucion_vlm():
    y_true = np.array(cargar(VLM[0][2])["y_true"])
    filas = [("Clases reales", y_true)]
    for m, e, f in VLM:
        filas.append((f"{m}: {e[0].lower() + e[1:] if e != 'CoT' else e}", np.array(cargar(f)["y_pred"])))
    fig, ax = plt.subplots(figsize=(6.0, 3.9))
    y = np.arange(len(filas))[::-1].astype(float)
    y[1:] -= 0.5
    y[6:] -= 0.5
    for yi, (et, pred) in zip(y, filas):
        izq = 0.0
        for k, c in enumerate(CLASES + ["Sin etiqueta"]):
            frac = np.mean(pred == (k if k < 7 else -1))
            if frac:
                ax.barh(yi, frac, left=izq, height=0.72, color=COLOR_CLASE.get(c, "#DDDDDD"),
                        edgecolor="white", lw=0.6)
                if frac >= 0.12:
                    ax.text(izq + frac / 2, yi, c if c != "Sin etiqueta" else "sin etiqueta", ha="center",
                            va="center", fontsize=6.5,
                            color="white" if c in ("MEL", "NV", "VASC") else "#222222")
                izq += frac
    ax.set_yticks(y)
    ax.set_yticklabels([f[0] for f in filas], fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Proporción de las 1 503 imágenes del conjunto de prueba")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    hs = [plt.Rectangle((0, 0), 1, 1, color=COLOR_CLASE.get(c, "#DDDDDD")) for c in CLASES + ["Sin etiqueta"]]
    ax.legend(hs, CLASES + ["Sin etiqueta"], fontsize=7, frameon=False, ncol=8, loc="lower center",
              bbox_to_anchor=(0.4, 1.0), handlelength=1, columnspacing=0.8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/distribucion-vlm-generativos.pdf")


SEMILLAS = ("", "_s43", "_s44")
RUNS = {"Swin-Tiny": ("swin_tiny_sweep_t06", AZUL, "o"), "ConvNeXt-Tiny": ("convnext_tiny_sweep_t02", NARANJA, "s"),
        "ViT-B/16": ("vit_sweep_t06", VERDE, "^"), "DenseNet121": ("densenet_sweep_t02", PURPURA, "D")}


def fig_recall_semillas():
    """Sensibilidad por clase de cada semilla (puntos) y su media (raya); con tres semillas, una caja no aporta."""
    n = cargar("swin_tiny_sweep_t06_les_cwnone_predictions.json")["y_true"]
    n = np.bincount(n, minlength=7)
    fig, ax = plt.subplots(figsize=(6.2, 3.1))
    off = np.linspace(-0.3, 0.3, 4)
    for (m, (run, c, mk)), dx in zip(RUNS.items(), off):
        v = np.array([cargar(f"{run}_les_cwnone{s}_test_results.json")["ham10000"]["sensitivity_per_class"]
                      for s in SEMILLAS])
        print(f"  {m}: medias {np.round(v.mean(0), 3)}")
        for k in range(7):
            x = k + dx
            ax.plot([x, x], [v[:, k].min(), v[:, k].max()], lw=1, color=c, alpha=0.6)
            ax.plot([x - 0.06, x + 0.06], [v[:, k].mean()] * 2, lw=2, color=c)
            ax.plot([x] * 3, v[:, k], mk, ms=3.2, color=c, mec="white", mew=0.4, alpha=0.9,
                    label=m if k == 0 else None)
    for k in range(6):
        ax.axvline(k + 0.5, lw=0.4, color="#e6e6e6")
    ax.set_xticks(range(7))
    ax.set_xticklabels([f"{c}\n({k})" for c, k in zip(CLASES, n)], fontsize=8)
    ax.set_ylabel("Sensibilidad")
    ax.set_ylim(0.2, 1.0)
    ax.set_xlim(-0.5, 6.5)
    ax.legend(fontsize=7, frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", lw=0.4, color="#e6e6e6")
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f"{OUT}/recall-clase-semillas.pdf")


def fig_melanoma_semillas():
    """Sensibilidad y especificidad de melanoma de cada semilla con las dos reglas de decisión."""
    ps = cargar("lesion_split_report.json")["melanoma_semillas"]["por_semilla"]
    modelos = {"swin_tiny": "Swin", "convnext_tiny": "ConvNeXt", "ensamble": "Ensamble"}
    reglas = (("op_argmax", "Clase más probable", VERDE, -0.13), ("op_spec85", "Umbral de validación", BERMELLON, 0.13))
    fig, axs = plt.subplots(1, 2, figsize=(5.8, 2.9))
    for ax, met, tit in zip(axs, ("sens", "spec"), ("Sensibilidad", "Especificidad")):
        for i, clave in enumerate(modelos):
            for op, et, c, dx in reglas:
                v = np.array([ps[s][clave]["melanoma"][op][met] for s in ("42", "43", "44")])
                x = i + dx
                ax.plot([x, x], [v.min(), v.max()], lw=1, color=c, alpha=0.6)
                ax.plot([x - 0.07, x + 0.07], [v.mean()] * 2, lw=2, color=c)
                ax.plot([x] * 3, v, "o", ms=3.5, color=c, mec="white", mew=0.4, label=et if i == 0 else None)
        ax.set_title(tit, fontsize=8.5)
        ax.set_xticks(range(3))
        ax.set_xticklabels(list(modelos.values()), fontsize=7.5)
        ax.set_xlim(-0.5, 2.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", lw=0.4, color="#e6e6e6")
        ax.set_axisbelow(True)
    axs[0].set_ylim(0.45, 0.9)
    axs[1].set_ylim(0.82, 0.98)
    axs[1].axhline(0.85, lw=0.8, ls=":", color=GRIS)
    axs[1].text(-0.45, 0.846, "mínimo exigido en validación", fontsize=6.5, color="#555555", va="top")
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, frameon=False, loc="upper center", ncol=2)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    fig.savefig(f"{OUT}/melanoma-semillas.pdf")



if __name__ == "__main__":
    for f in (fig_resumen, fig_confusion, fig_robustez, fig_calibracion, fig_hiba, fig_distribucion_vlm,
              fig_recall_semillas, fig_melanoma_semillas):
        print(f.__name__)
        f()
