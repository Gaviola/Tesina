"""Figuras del Cap. 5: cascada por fuente de diagnóstico, cascada por clase, fallas de los reportes, ruteo por nivel
y resumen de los generadores.

Lee solo JSON de outputs/results/ (métrica oficial: solo el reporte, matcher estricto; cap5_derivados.json sale de
scripts/cap5_derivados.py) y escribe PDF en Docs/TFG/Figures/Capitulos/05-Resultados-Generacion/. Mismo estilo que
figuras_cap4.py.
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = "C:/Users/Facu/1/Facultad/Tesina"
RES = f"{BASE}/Codigo/outputs/results"
OUT = f"{BASE}/Docs/TFG/Figures/Capitulos/05-Resultados-Generacion"
CLASES = ["melanoma", "nevus", "basal cell carcinoma", "actinic keratosis", "benign keratosis", "dermatofibroma",
          "vascular lesion"]
SIGLA = dict(zip(CLASES, ["MEL", "NV", "BCC", "AKIEC", "BKL", "DF", "VASC"]))
GEN = [("mini_vlm", "Mini-VLM"), ("llava_med", "LLaVA-Med"), ("skinvl", "SkinVL")]
BOOT = {"mini_vlm": "ensemble_bootstrap_les_report_only_strict.json",
        "llava_med": "ensemble_bootstrap_llava_med_les_report_only_strict.json",
        "skinvl": "ensemble_bootstrap_skinvl_les_report_only_strict.json"}

# Okabe–Ito (Configurations/13-Figuras.sty)
AZUL, NARANJA, CELESTE, VERDE, AMARILLO, BERMELLON, PURPURA = (
    "#0072B2", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#D55E00", "#CC79A7")
GRIS = "#999999"
COLOR_GEN = {"mini_vlm": AZUL, "llava_med": NARANJA, "skinvl": VERDE}
MARCA_GEN = {"mini_vlm": "o", "llava_med": "s", "skinvl": "^"}

plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": "#888888",
                     "axes.linewidth": 0.6, "xtick.color": "#444444", "ytick.color": "#444444",
                     "axes.titlesize": 9})


def cargar(ruta):
    return json.load(open(f"{RES}/{ruta}", encoding="utf8"))


def limpiar(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(lw=0.4, color="#e6e6e6")
    ax.set_axisbelow(True)


def fig_cascada():
    """Consistencia diagnóstica de cada generador según la fuente del diagnóstico."""
    fuentes = [("full_baseline", "Sin anclaje", GRIS, "o"), ("full_dermlip_oficial", "DermLIP sin ajuste", VERDE, "D"),
               ("full_swin_les", "Swin-Tiny", AZUL, "s"), ("full_oracle", "Oracle", BERMELLON, "^")]
    der = cargar("cap5_derivados.json")
    exact = der["por_clase"]["exactitud_swin"]
    fig, ax = plt.subplots(figsize=(6.0, 2.3))
    for fila, (g, nombre) in enumerate(GEN):
        c = cargar(BOOT[g])["consistencia"]
        dl = f"{RES}/cascada_dermlip_oficial_{g}.json"  # se agrega cuando terminen los reportes
        if os.path.exists(dl):
            c["full_dermlip_oficial"] = json.load(open(dl, encoding="utf8"))["consistencia"]
        xs = [c[f] for f, *_ in fuentes if f in c]
        ax.plot([min(xs), max(xs)], [fila, fila], color="#d0d0d0", lw=1.2, zorder=1)
        for f, etiqueta, color, marca in fuentes:
            if f in c:
                ax.scatter(c[f], fila, color=color, marker=marca, s=40, zorder=3, edgecolor="white", lw=0.6,
                           label=etiqueta if fila == 0 else None)
    ax.axvline(exact, color=AZUL, ls="--", lw=0.8)
    ax.text(exact - 0.01, -0.62, f"exactitud de Swin-Tiny ({exact:.3f})", fontsize=7.5, color=AZUL, ha="right")
    ax.set_yticks(range(len(GEN)), [n for _, n in GEN])
    ax.set_ylim(2.5, -0.8)
    ax.set_xlim(0, 1.02)
    ax.set_xlabel("Consistencia diagnóstica")
    limpiar(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=4, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/cascada-fuentes.pdf", bbox_inches="tight")


def fig_por_clase():
    """Sensibilidad de Swin-Tiny por clase frente a la consistencia de la cascada por clase."""
    pc = cargar("cap5_derivados.json")["por_clase"]
    fig, ax = plt.subplots(figsize=(4.4, 3.6))
    ax.plot([0, 1], [0, 1], color=GRIS, lw=0.8, ls="--", zorder=1)
    for g, nombre in GEN:
        xs = [pc["sensibilidad_swin"][c] for c in CLASES]
        ys = [pc[g][c] for c in CLASES]
        ax.scatter(xs, ys, color=COLOR_GEN[g], marker=MARCA_GEN[g], s=34, zorder=3, edgecolor="white", lw=0.5,
                   label=nombre)
    for c in CLASES:
        x, y = pc["sensibilidad_swin"][c], pc["mini_vlm"][c]
        dx = {"vascular lesion": -0.075, "dermatofibroma": -0.065, "melanoma": 0.02, "basal cell carcinoma": 0.02
              }.get(c, 0.015)
        dy = {"vascular lesion": 0.03, "dermatofibroma": 0.02, "melanoma": 0.0, "basal cell carcinoma": -0.04
              }.get(c, -0.045)
        ax.text(x + dx, y + dy, SIGLA[c], fontsize=7.5, color="#333333")
    ax.set_xlim(0.2, 1.0)
    ax.set_ylim(0.2, 1.0)
    ax.set_aspect("equal")
    ax.set_xlabel("Sensibilidad de Swin-Tiny en la clase")
    ax.set_ylabel("Consistencia de la cascada en la clase")
    limpiar(ax)
    ax.legend(loc="upper left", frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/cascada-por-clase.pdf", bbox_inches="tight")


FALLAS = [("correcto", "Diagnóstico correcto", AZUL), ("correcto_con_reserva", "Correcto, con reservas", CELESTE),
          ("hedging", "Hedging", AMARILLO), ("contradiccion", "Contradicción", PURPURA),
          ("dx_incorrecto", "Diagnóstico incorrecto", BERMELLON), ("resto", "Sin diagnóstico u otros", GRIS)]


def fig_fallas():
    """Falla principal de cada reporte por generador y fuente del diagnóstico."""
    fa = cargar("cap5_derivados.json")["fallas"]
    brazos = [("full_baseline", "sin anclaje"), ("full_swin_les", "Swin-Tiny"), ("full_oracle", "oracle")]
    filas, etiquetas = [], []
    for g, nombre in GEN:
        for b, nb in brazos:
            f = fa[g][b]["fallas"]
            fila = {k: f.get(k, 0.0) for k, *_ in FALLAS[:-1]}
            fila["resto"] = 1 - sum(fila.values())
            filas.append(fila)
            etiquetas.append(f"{nombre}, {nb}")
    fig, ax = plt.subplots(figsize=(6.0, 3.3))
    y = np.arange(len(filas))[::-1] + np.repeat([0.6, 0.3, 0.0], 3)
    izq = np.zeros(len(filas))
    for k, etiqueta, color in FALLAS:
        v = np.array([f[k] for f in filas])
        ax.barh(y, v, left=izq, color=color, height=0.78, edgecolor="white", lw=0.6, label=etiqueta,
                hatch="//" if k == "dx_incorrecto" else None)
        izq += v
    ax.set_yticks(y, etiquetas, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fracción de los reportes")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.17), ncol=3, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(f"{OUT}/fallas-reportes.pdf", bbox_inches="tight")


def fig_ruteo():
    """(a) Acierto de Swin-Tiny y cobertura del par por nivel; (b) nivel asignado a cada clase."""
    ru = cargar("cap5_derivados.json")["ruteo"]
    niveles = [("affirmative", "Afirmativo"), ("differential", "Diferencial"), ("abstention", "Derivación")]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.4, 2.6), gridspec_kw={"width_ratios": [1.15, 1.5]})
    x = np.arange(3)
    sw = [ru["niveles"][n]["swin"] for n, _ in niveles]
    par = [ru["niveles"][n]["par"] for n, _ in niveles]
    a.bar(x - 0.19, sw, 0.36, color=AZUL, label="Swin-Tiny acierta")
    a.bar(x + 0.19, par, 0.36, color=CELESTE, label="El par contiene la clase", hatch="//", edgecolor="white", lw=0.5)
    for i, n in enumerate(niveles):
        a.text(i, 1.03, f"n = {ru['niveles'][n[0]]['n']}", ha="center", fontsize=7.5, color="#444444")
    a.set_xticks(x, [e for _, e in niveles], fontsize=7.5)
    a.set_ylim(0, 1.1)
    a.set_ylabel("Fracción de los casos")
    a.set_title("(a) Acierto por nivel")
    limpiar(a)
    a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), frameon=False, fontsize=7.5, ncol=1)
    clases = sorted(CLASES, key=lambda c: -ru["por_clase"][c]["affirmative"] / sum(ru["por_clase"][c].values()))
    izq = np.zeros(len(clases))
    yy = np.arange(len(clases))[::-1]
    for (n, e), color, h in zip(niveles, [AZUL, NARANJA, BERMELLON], [None, "//", ".."]):
        v = np.array([ru["por_clase"][c][n] / sum(ru["por_clase"][c].values()) for c in clases])
        b.barh(yy, v, left=izq, color=color, height=0.75, edgecolor="white", lw=0.5, label=e, hatch=h)
        izq += v
    b.set_yticks(yy, [f"{SIGLA[c]} ({sum(ru['por_clase'][c].values())})" for c in clases], fontsize=8)
    b.set_xlim(0, 1)
    b.set_xlabel("Fracción de la clase")
    b.set_title("(b) Nivel por clase")
    b.spines[["top", "right"]].set_visible(False)
    b.legend(loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=3, frameon=False, fontsize=7.5)
    fig.tight_layout()
    fig.savefig(f"{OUT}/ruteo-niveles.pdf", bbox_inches="tight")


def fig_resumen():
    """Consistencia con Swin-Tiny y con el oracle, cobertura de entidades y tiempo por reporte de los tres
    generadores."""
    der = cargar("cap5_derivados.json")["fallas"]
    costo = {d["modelo"]: d["gen_s_por_reporte"] for d in cargar("cost/cost_comparison_v3.json")
             if d.get("gen_s_por_reporte")}
    seg = {"mini_vlm": costo["Mini-VLM (Phi-3.5-V)"], "llava_med": costo["LLaVA-Med v1.5 (7B)"],
           "skinvl": costo["SkinVL-MM (7B)"]}
    fig, axs = plt.subplots(1, 3, figsize=(6.4, 2.1), sharey=True)
    y = np.arange(len(GEN))[::-1]
    # Los dos paneles con marca del oracle llevan el valor de la barra por dentro y el del oracle por fuera.
    texto_barra = {"mini_vlm": "white", "llava_med": "#222222", "skinvl": "white"}
    for i, (g, _) in enumerate(GEN):
        c = cargar(BOOT[g])["consistencia"]
        pares = ((axs[0], c["full_swin_les"], c["full_oracle"]),
                 (axs[1], der[g]["full_swin_les"]["cobertura_entidades"], der[g]["full_oracle"]["cobertura_entidades"]))
        for ax, swin, oraculo in pares:
            ax.barh(y[i], swin, color=COLOR_GEN[g], height=0.6)
            ax.scatter(oraculo, y[i] + 0.0, marker="|", s=120, color="#222222", zorder=3,
                       label="Con el oracle" if i == 0 else None)
            ax.text(swin - 0.02, y[i], f"{swin:.3f}", va="center", ha="right", fontsize=7, color=texto_barra[g])
            ax.text(max(swin, oraculo) + 0.03, y[i], f"{oraculo:.3f}", va="center", fontsize=7, color="#222222")
        axs[2].barh(y[i], seg[g], color=COLOR_GEN[g], height=0.6)
        axs[2].text(seg[g] + 0.5, y[i], f"{seg[g]:.1f}", va="center", fontsize=7)
    axs[0].set_yticks(y, [n for _, n in GEN])
    axs[0].set_xlim(0, 1.3)
    axs[0].set_xticks([0, 0.5, 1])
    axs[0].set_xlabel("Consistencia diagnóstica")
    h, e = axs[0].get_legend_handles_labels()
    fig.legend(h, e, loc="upper center", bbox_to_anchor=(0.36, 1.08), frameon=False, fontsize=7.5, handletextpad=0.2)
    axs[1].set_xlim(0, 1.3)
    axs[1].set_xticks([0, 0.5, 1])
    axs[1].set_xlabel("Cobertura de entidades")
    axs[2].set_xlim(0, 32)
    axs[2].set_xlabel("Segundos por reporte")
    for ax in axs:
        limpiar(ax)
    fig.tight_layout()
    fig.savefig(f"{OUT}/resumen-generadores.pdf", bbox_inches="tight")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig_cascada, fig_por_clase, fig_fallas, fig_ruteo, fig_resumen):
        f()
        print("ok", f.__name__)
