"""Ejemplos de imágenes con la predicción de cada modelo (ejecución de referencia), para ver dónde falla cada uno.

Selección fija, sin mirar las imágenes: en cada clase, la primera imagen, en el orden del conjunto, en la que al menos un
modelo acierta y al menos otro falla. No representan el desempeño global, sino las diferencias entre modelos.

  ejemplos-supervisados.pdf: conjunto de prueba de HAM10000, los cuatro supervisados.
  ejemplos-hiba.pdf: HIBA, Swin-Tiny y ConvNeXt-Tiny.

Se ejecuta desde Codigo/.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

from src.data.ham10000 import HAM10000_CLASSES
from src.data.hiba import HIBADataset
from src.data.transforms import get_val_transforms

RES = Path("outputs/results")
OUT = "../Docs/TFG/Figures/Capitulos/04-Resultados-Clasificacion"
AZUL, BERMELLON = "#0072B2", "#D55E00"
SUPERVISADOS = [("Swin", "swin_tiny_sweep_t06_les_cwnone"), ("ConvNeXt", "convnext_tiny_sweep_t02_les_cwnone"),
                ("ViT", "vit_sweep_t06_les_cwnone"), ("DenseNet", "densenet_sweep_t02_les_cwnone")]
HIBA = [("Swin", "swin_tiny_sweep_t06_les_cwnone_hiba_predictions_hiba"),
        ("ConvNeXt", "convnext_tiny_sweep_t02_les_cwnone_hiba_predictions_hiba")]

plt.rcParams.update({"font.family": "serif"})
vista = get_val_transforms(size=224, center_crop=True).transforms
vista = vista[:[type(t).__name__ for t in vista].index("ToTensor")]


def cargar(archivo):
    return json.load(open(RES / f"{archivo}.json", encoding="utf8"))


def seleccionar(y_true, preds):
    elegidas = {}
    for i, y in enumerate(y_true):
        aciertos = [p[i] == y for p in preds]
        if y not in elegidas and any(aciertos) and not all(aciertos):
            elegidas[y] = i
    return [elegidas[c] for c in range(7) if c in elegidas]


def figura(rutas, y_true, modelos, ruta_salida, por_fila=7):
    n = len(rutas)
    filas = (n + por_fila - 1) // por_fila
    alto_texto = 0.095 * (len(modelos) + 1)
    fig = plt.figure(figsize=(6.4, filas * (6.4 / por_fila) * (1 + alto_texto * 1.3)))
    for k, (ruta, y) in enumerate(zip(rutas, y_true)):
        ax = fig.add_subplot(filas, por_fila, k + 1)
        img = Image.open(ruta).convert("RGB")
        for t in vista:
            img = t(img)
        ax.imshow(img.resize((224, 224)))
        ax.axis("off")
        ax.set_title(HAM10000_CLASSES[y], fontsize=7.5, fontweight="bold", pad=2)
        for j, (nombre, pred) in enumerate(modelos):
            p = pred[k]
            ok = p == y
            marca = "✓" if ok else "✗"
            ax.text(0.5, -0.08 - j * 0.14, f"{nombre}: {HAM10000_CLASSES[p]} {marca}", transform=ax.transAxes,
                    ha="center", va="top", fontsize=5.6, family="DejaVu Sans", color=AZUL if ok else BERMELLON)
    fig.subplots_adjust(left=0.005, right=0.995, top=0.94, bottom=alto_texto * 0.95, wspace=0.08, hspace=0.75)
    fig.savefig(ruta_salida, bbox_inches="tight")


# HAM10000
datos = {n: cargar(f"{a}_predictions") for n, a in SUPERVISADOS}
ref = datos["Swin"]
for n, d in datos.items():
    assert d["image_ids"] == ref["image_ids"] and d["y_true"] == ref["y_true"], n
    print(n, "exactitud", sum(a == b for a, b in zip(d["y_true"], d["y_pred"])) / len(d["y_true"]))
idx = seleccionar(ref["y_true"], [datos[n]["y_pred"] for n, _ in SUPERVISADOS])
rutas = [f"data/processed/HAM10000/{ref['image_ids'][i]}.jpg" for i in idx]
modelos = [(n, [datos[n]["y_pred"][i] for i in idx]) for n, _ in SUPERVISADOS]
figura(rutas, [ref["y_true"][i] for i in idx], modelos, f"{OUT}/ejemplos-supervisados.pdf")
print("HAM10000:", [ref["image_ids"][i] for i in idx])

# HIBA: las predicciones siguen el orden de HIBADataset con el mapeo a siete clases.
ds = HIBADataset(root_dir="data/raw/HIBA", split="train", ham10000_mapping=True)
hd = {n: cargar(a) for n, a in HIBA}
y_hiba = hd["Swin"]["y_true"]
assert y_hiba == [s["label"] for s in ds.samples] == hd["ConvNeXt"]["y_true"]
idx = seleccionar(y_hiba, [hd[n]["y_pred"] for n, _ in HIBA])
rutas = [ds.samples[i]["image_path"] for i in idx]
modelos = [(n, [hd[n]["y_pred"][i] for i in idx]) for n, _ in HIBA]
figura(rutas, [y_hiba[i] for i in idx], modelos, f"{OUT}/ejemplos-hiba.pdf")
print("HIBA:", [(ds.samples[i]["image_id"], ds.samples[i]["image_type"], HAM10000_CLASSES[y_hiba[i]]) for i in idx])
