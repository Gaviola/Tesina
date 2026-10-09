"""Busca párrafos cuya última línea quedó con una a tres palabras solas (guía de redacción, §6).

Uso, desde Docs/TFG y después de compilar:
    python -X utf8 check_huerfanas.py        # todo el documento
    python -X utf8 check_huerfanas.py 2      # solo el capítulo 2

Recorre los bloques de texto del PDF que ocupan el ancho de la caja y marca los que terminan en una línea más
corta que el 16 % de ese ancho y con tres palabras o menos. Imprime la página, el final de la línea anterior y
la línea huérfana. Los casos se corrigen reformulando la frase, no con espaciado manual. Requiere PyMuPDF
(pip install pymupdf).
"""
import sys

import pymupdf

doc = pymupdf.open("tesina.pdf")
first, last = 0, doc.page_count
if len(sys.argv) > 1:
    # Rango de páginas del capítulo según los marcadores de nivel 1 del PDF.
    chapters = [(title, page) for level, title, page in doc.get_toc() if level == 1]
    target = sys.argv[1]
    for i, (title, page) in enumerate(chapters):
        if title.split()[0].rstrip(".") == target or title.startswith(f"{target} "):
            first = page - 1
            last = chapters[i + 1][1] - 1 if i + 1 < len(chapters) else doc.page_count
            break
    else:
        sys.exit(f"No se encontró el capítulo {target} en los marcadores del PDF.")

found = 0
for n in range(first, last):
    page = doc[n]
    for block in page.get_text("dict")["blocks"]:
        lines = block.get("lines", [])
        if len(lines) < 2:
            continue
        # Encabezado y pie de página.
        if block["bbox"][1] < 60 or block["bbox"][3] > page.rect.height - 50:
            continue
        x0 = min(l["bbox"][0] for l in lines)
        x1 = max(l["bbox"][2] for l in lines)
        if x1 - x0 < 300:  # bloques angostos: celdas de tabla, epígrafes cortos, figuras
            continue
        tail = lines[-1]
        text = "".join(s["text"] for s in tail["spans"]).strip()
        # Una última línea de párrafo empieza en el margen izquierdo (las celdas de tabla y los fragmentos de
        # fórmulas no) y cierra una oración; las líneas que terminan en coma preceden a una ecuación.
        if abs(tail["bbox"][0] - x0) > 2 or not text.rstrip("]0123456789,[").endswith((".", ":", ";")):
            continue
        if tail["bbox"][2] - tail["bbox"][0] < 0.16 * (x1 - x0) and len(text.split()) <= 3:
            prev = "".join(s["text"] for s in lines[-2]["spans"]).strip()
            print(f"p{n + 1}: ...{prev[-50:]} | {text}")
            found += 1

print(f"{found} línea(s) huérfana(s).")
