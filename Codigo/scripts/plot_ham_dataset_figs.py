"""Figuras del análisis exploratorio de HAM10000 para la Sección 3.3 de la tesina.

Genera tres PDF a partir de los metadatos de HAM10000 (no usa resultados de ningún modelo):

  - ``ham-distribucion.pdf``: imágenes por clase, con su porcentaje; las malignas (MEL, BCC) en bermellón
    y con trama, para distinguirlas también en blanco y negro.
  - ``ham-imagenes-por-lesion.pdf``: cantidad de lesiones según cuántas imágenes tiene cada una.
  - ``ham-ejemplos.pdf``: una imagen dermatoscópica por clase (la primera, por ``image_id``, entre las
    confirmadas por histopatología). HAM10000 se distribuye con licencia CC BY-NC 4.0: el epígrafe de la
    figura lleva la atribución.

Colores de la paleta Okabe–Ito (``Docs/TFG/Configurations/13-Figuras.sty``).

100% local. Uso (desde ``Codigo/``):
    python scripts/plot_ham_dataset_figs.py --out ../Docs/TFG/Figures/Capitulos/03-Materiales-Metodos
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image

AZUL = "#0072B2"
BERMELLON = "#D55E00"
CLASES = ["mel", "nv", "bcc", "akiec", "bkl", "df", "vasc"]
MALIGNAS = {"mel", "bcc"}

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["TeX Gyre Pagella", "Palatino Linotype", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "pdf.fonttype": 42,
    "hatch.linewidth": 0.5,
})


def miles(n):
    """Separador de miles con espacio fino, como en el texto de la tesina."""
    return f"{n:,}".replace(",", " ")


def fig_distribucion(meta, out):
    conteo = meta["dx"].value_counts()
    orden = conteo.sort_values().index
    total = conteo.sum()
    fig, ax = plt.subplots(figsize=(5.6, 2.8))
    colores = [BERMELLON if c in MALIGNAS else AZUL for c in orden]
    barras = ax.barh([c.upper() for c in orden], conteo[orden], color=colores,
                     edgecolor="black", linewidth=0.4)
    for b, c in zip(barras, orden):
        if c in MALIGNAS:
            b.set_hatch("///")
    for b, c in zip(barras, orden):
        n = conteo[c]
        ax.text(b.get_width() + total * 0.008, b.get_y() + b.get_height() / 2,
                f"{miles(n)} ({100 * n / total:.2f} %)", va="center", fontsize=9)
    ax.set_xlabel("Imágenes")
    ax.set_xlim(0, conteo.max() * 1.32)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: miles(int(x))))
    fig.tight_layout()
    fig.savefig(out / "ham-distribucion.pdf")
    plt.close(fig)
    return conteo


def fig_imagenes_por_lesion(meta, out):
    por_lesion = meta.groupby("lesion_id").size()
    dist = por_lesion.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    barras = ax.bar(dist.index.astype(str), dist.values, color=AZUL, edgecolor="black", linewidth=0.4)
    for b, n in zip(barras, dist.values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + dist.max() * 0.015, miles(n),
                ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Imágenes por lesión")
    ax.set_ylabel("Lesiones")
    ax.set_ylim(0, dist.max() * 1.15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: miles(int(x))))
    fig.tight_layout()
    fig.savefig(out / "ham-imagenes-por-lesion.pdf")
    plt.close(fig)
    return dist


def buscar_imagen(data_dir, image_id):
    for parte in ("HAM10000_images_part_1", "HAM10000_images_part_2"):
        p = data_dir / parte / f"{image_id}.jpg"
        if p.exists():
            return p
    raise FileNotFoundError(image_id)


def fig_ejemplos(meta, data_dir, out):
    elegidas = {}
    fig, axes = plt.subplots(1, len(CLASES), figsize=(6.3, 1.35))
    for ax, c in zip(axes, CLASES):
        sub = meta[(meta["dx"] == c) & (meta["dx_type"] == "histo")].sort_values("image_id")
        image_id = sub["image_id"].iloc[0]
        elegidas[c] = image_id
        img = Image.open(buscar_imagen(data_dir, image_id)).convert("RGB")
        w, h = img.size
        lado = min(w, h)
        img = img.crop(((w - lado) // 2, (h - lado) // 2, (w + lado) // 2, (h + lado) // 2))
        img = img.resize((300, 300), Image.LANCZOS)
        ax.imshow(img)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_title(c.upper(), fontsize=9, pad=3)
    fig.subplots_adjust(left=0.005, right=0.995, top=0.84, bottom=0.01, wspace=0.06)
    fig.savefig(out / "ham-ejemplos.pdf", dpi=200)
    plt.close(fig)
    return elegidas


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", type=Path, default=Path("data/raw/HAM10000"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    meta = pd.read_csv(args.data_dir / "HAM10000_metadata")
    args.out.mkdir(parents=True, exist_ok=True)

    conteo = fig_distribucion(meta, args.out)
    dist = fig_imagenes_por_lesion(meta, args.out)
    elegidas = fig_ejemplos(meta, args.data_dir, args.out)

    print(f"Imágenes: {len(meta)}; lesiones: {meta['lesion_id'].nunique()}")
    print("Por clase:", conteo.to_dict())
    print("Lesiones según imágenes por lesión:", dist.to_dict())
    print("Ejemplos:", elegidas)


if __name__ == "__main__":
    main()
