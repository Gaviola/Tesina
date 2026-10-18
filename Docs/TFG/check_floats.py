"""Chequea que cada figura y tabla aparezca cerca de donde el texto la menciona.

Uso, desde Docs/TFG y después de compilar:
    python check_floats.py            # todo el documento
    python check_floats.py 2          # solo el capítulo 2

Para cada «Figura X.Y» / «Tabla X.Y» compara la página de su epígrafe con la página de la primera mención en
el cuerpo. Marca con «!!» los flotantes que quedan en una página distinta de su primera mención, y con «??» los
que nunca se mencionan. Requiere pdftotext (Git Bash lo trae en /mingw64/bin).
"""
import re
import subprocess
import sys

pdf = "tesina.pdf"
txt = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf, "-"], capture_output=True).stdout.decode("utf-8", errors="replace")
pages = txt.split("\f")
cap_filter = sys.argv[1] if len(sys.argv) > 1 else None

pat = re.compile(r"(Figura|Tabla)\s+(\d+)\.(\d+)(?![\d.]\d)(\s*:)?")
caption, mention = {}, {}
plural = re.compile(r"(Figura|Tabla)s\s+((?:\d+\.\d+[a-z]?(?:\s*,\s*|\s+y\s+)?)+)")
for n, page in enumerate(pages, start=1):
    for m in plural.finditer(page):
        for c, k in re.findall(r"(\d+)\.(\d+)", m.group(2)):
            mention.setdefault((m.group(1), int(c), int(k)), n)
    for m in pat.finditer(page):
        key = (m.group(1), int(m.group(2)), int(m.group(3)))
        if m.group(4):
            caption.setdefault(key, n)
        else:
            mention.setdefault(key, n)

problems = 0
for key in sorted(caption, key=lambda k: (k[1], k[0], k[2])):
    kind, ch, num = key
    if cap_filter and str(ch) != cap_filter:
        continue
    cp, mp = caption[key], mention.get(key)
    if mp is None:
        flag = "??"
    elif cp != mp:
        flag = "!!"
    else:
        flag = "  "
    if flag != "  ":
        problems += 1
    print(f"{flag} {kind} {ch}.{num}: epígrafe en pág. {cp}, primera mención en pág. {mp}")
print(f"\n{problems} flotantes fuera de la página de su primera mención o sin mencionar.")
