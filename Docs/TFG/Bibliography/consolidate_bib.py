"""Consolidate the four scattered .bib files into a single normalized Bibliography.bib.

Dedupes by DOI then by normalized title. Rewrites keys as <surname><year><word>.
Drops Zotero-local fields (file, abstract, keywords, urldate).
"""
import re, sys, unicodedata
from pathlib import Path

ROOT = Path(r"C:\Users\Facu\1\Facultad\Tesina\Docs")
SOURCES = [
    ROOT / "estado_del_arte" / "referencias.bib",
    ROOT / "marco_teorico" / "referencias.bib",
    ROOT / "tabla_resultados_sota" / "referencias_sota.bib",
    ROOT / "TFG" / "Bibliography" / "Bibliography.bib",
]
KEEP = {
    "title", "shorttitle", "author", "editor", "date", "year", "month",
    "journaltitle", "journal", "booktitle", "volume", "number", "pages",
    "publisher", "institution", "organization", "series", "doi", "url",
    "issn", "isbn", "eprint", "eprinttype", "eprintclass", "langid", "note",
    "howpublished", "version", "type", "edition",
}
DROP_SILENT = {"file", "abstract", "keywords", "urldate", "shortjournal",
               "annotation", "copyright", "rights", "pmid", "pmcid", "location"}
STOP = {"a", "an", "the", "on", "of", "for", "in", "to", "and", "with", "from",
        "toward", "towards", "is", "are", "at", "via", "using", "deep", "large",
        "automated", "multimodal", "artificial", "evaluating", "creating"}
# Entradas exportadas de Zotero sin campo de fecha. Año de la publicación de
# referencia; quedan listadas en refs_pendientes.md para verificación.
# Entradas duplicadas que no colapsan por título porque el título está truncado.
MANUAL_DROP = {
    "DermLIP2025": "duplicado incompleto de yan_derm1m_2025 (título truncado, sin DOI)",
}
# Fechas incorrectas en la exportación de Zotero.
DATE_FIX = {
    "papineni_bleu_2001": "2002",  # ACL 2002, no el informe técnico de 2001
}
# Zotero tipó como @article trabajos publicados en congresos y no exportó el lugar
# de publicación. Se completa el tipo y el nombre del congreso o la revista, sin
# volumen ni páginas; quedan listados en refs_pendientes.md para verificación.
VENUE_PATCH = {
    "vaswani_attention_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "devlin_bert_nodate": ("inproceedings", "booktitle", "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics"),
    "brown_language_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "radford_learning_nodate": ("inproceedings", "booktitle", "Proceedings of the 38th International Conference on Machine Learning"),
    "lewis_retrieval-augmented_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "lin_rouge_nodate": ("inproceedings", "booktitle", "Text Summarization Branches Out"),
    "goodfellow_generative_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "ho_denoising_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "ouyang_training_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems"),
    "rezende_variational_nodate": ("inproceedings", "booktitle", "Proceedings of the 32nd International Conference on Machine Learning"),
    "moor_med-flamingo_nodate": ("inproceedings", "booktitle", "Proceedings of the 3rd Machine Learning for Health Symposium"),
    "daneshjou_skincon_nodate": ("inproceedings", "booktitle", "Advances in Neural Information Processing Systems: Datasets and Benchmarks Track"),
    "rumelhart_learning_1986": ("article", "journaltitle", "Nature"),
}
YEAR_PATCH = {
    "vaswani_attention_nodate": "2017",       # NeurIPS
    "devlin_bert_nodate": "2019",             # NAACL
    "brown_language_nodate": "2020",          # NeurIPS (GPT-3)
    "radford_learning_nodate": "2021",        # ICML (CLIP)
    "lewis_retrieval-augmented_nodate": "2020",  # NeurIPS (RAG)
    "lin_rouge_nodate": "2004",               # WAS
    "goodfellow_generative_nodate": "2014",   # NeurIPS (GAN)
    "ho_denoising_nodate": "2020",            # NeurIPS (DDPM)
    "ouyang_training_nodate": "2022",         # NeurIPS (InstructGPT)
    "rezende_variational_nodate": "2015",     # ICML (normalizing flows)
    "moor_med-flamingo_nodate": "2023",       # ML4H
    "daneshjou_skincon_nodate": "2022",       # NeurIPS Datasets & Benchmarks
}


def split_entries(text):
    """Yield (type, key, body) for each @entry, brace-matched."""
    out = []
    for m in re.finditer(r"@(\w+)\s*(\{)\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(3)
        # start at the entry's own opening brace so nested field braces balance out
        i, depth = m.start(2), 0
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append((etype, key, text[m.end():i]))
    return out


def parse_fields(body):
    """Split an entry body into {name: value} preserving inner braces."""
    fields, i, n = {}, 0, len(body)
    while i < n:
        m = re.compile(r"\s*([A-Za-z]+)\s*=\s*").match(body, i)
        if not m:
            i += 1
            continue
        name, i = m.group(1).lower(), m.end()
        if i < n and body[i] == "{":
            depth, start = 0, i
            while i < n:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            val = body[start + 1:i - 1]
        elif i < n and body[i] == '"':
            start = i + 1
            i += 1
            while i < n and body[i] != '"':
                i += 1
            val = body[start:i]
            i += 1
        else:
            start = i
            while i < n and body[i] not in ",\n":
                i += 1
            val = body[start:i].strip()
        fields[name] = " ".join(val.split())
        while i < n and body[i] in " ,\n\t":
            i += 1
    return fields


def ascii_slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def norm_title(t):
    t = re.sub(r"[{}\\$]", "", t or "")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t.lower())


def first_surname(author):
    if not author:
        return "anon"
    first = re.split(r"\s+and\s+", author)[0].strip()
    first = re.sub(r"[{}]", "", first)
    if "," in first:
        return ascii_slug(first.split(",")[0]) or "anon"
    parts = first.split()
    return ascii_slug(parts[-1]) if parts else "anon"


def get_year(f):
    for k in ("date", "year", "eprint"):
        m = re.search(r"(19|20)\d{2}", f.get(k, ""))
        if m:
            return m.group(0)
    return "nd"


def short_word(f):
    fallback = None
    for src in (f.get("shorttitle"), f.get("title")):
        if not src:
            continue
        clean = re.sub(r"[{}\\$]", "", src)
        for chunk in (re.split(r"[:.\u2014]", clean)[0], clean):
            for w in chunk.split():
                sw = ascii_slug(w)
                if not sw or len(sw) < 2:
                    continue
                if sw not in STOP:
                    return sw
                fallback = fallback or sw
    return fallback or "ref"


# --- load and dedupe -------------------------------------------------------
entries, by_doi, by_title, log = [], {}, {}, []
for src in SOURCES:
    raw = src.read_text(encoding="utf-8", errors="replace")
    for etype, key, body in split_entries(raw):
        if key in MANUAL_DROP:
            log.append(f"  = dup {src.name}:{key} descartado a mano ({MANUAL_DROP[key]})")
            continue
        f = parse_fields(body)
        if key in DATE_FIX:
            f["date"] = DATE_FIX[key]
            log.append(f"  ~ {src.name}:{key} fecha corregida a {f['date']}")
        if not f.get("title") and f.get("shorttitle"):
            f["title"] = f["shorttitle"]
            log.append(f"  ! {src.name}:{key} sin title, se usa shorttitle")
        if key in YEAR_PATCH and not re.search(r"(19|20)\d{2}", f.get("date", "") + f.get("year", "")):
            f["date"] = YEAR_PATCH[key]
            log.append(f"  + {src.name}:{key} sin fecha, se completa con {f['date']} (verificar)")
        if key in VENUE_PATCH:
            newtype, field, value = VENUE_PATCH[key]
            if not f.get(field):
                etype, f[field] = newtype, value
                log.append(f"  + {src.name}:{key} sin lugar de publicacion, se completa "
                           f"como @{newtype} en «{value}» (verificar)")
        doi = (f.get("doi") or "").lower().replace("https://doi.org/", "").strip()
        nt = norm_title(f.get("title", ""))
        dup_of = None
        if doi and doi in by_doi:
            dup_of = by_doi[doi]
        elif nt and nt in by_title:
            dup_of = by_title[nt]
        if dup_of is not None:
            keep, cand = dup_of, {"type": etype, "key": key, "f": f, "src": src.name}
            # keep whichever entry carries more bibliographic fields
            if len([k for k in f if k in KEEP]) > len([k for k in keep["f"] if k in KEEP]):
                keep["type"], keep["f"], keep["src"] = etype, f, src.name
                log.append(f"  = dup {src.name}:{key} reemplaza a {cand['key']} (mas campos)")
            else:
                log.append(f"  = dup {src.name}:{key} descartado (ya esta como {keep['key']})")
            keep.setdefault("aliases", []).append(f"{src.name}:{key}")
            continue
        e = {"type": etype, "key": key, "f": f, "src": src.name, "aliases": []}
        entries.append(e)
        if doi:
            by_doi[doi] = e
        if nt:
            by_title[nt] = e

# --- normalize keys --------------------------------------------------------
used, mapping = {}, []
for e in entries:
    base = f"{first_surname(e['f'].get('author', ''))}{get_year(e['f'])}{short_word(e['f'])}"
    newkey = base
    if base in used:
        suffix = ord("b")
        while f"{base}{chr(suffix)}" in used:
            suffix += 1
        newkey = f"{base}{chr(suffix)}"
    used[newkey] = e
    mapping.append((newkey, e["key"], e["src"], e["aliases"]))
    e["newkey"] = newkey

# --- emit ------------------------------------------------------------------
order = ["author", "editor", "title", "shorttitle", "date", "year", "month",
         "journaltitle", "journal", "booktitle", "series", "volume", "number",
         "pages", "publisher", "institution", "organization", "edition",
         "version", "type", "doi", "url", "eprint", "eprinttype", "eprintclass",
         "issn", "isbn", "howpublished", "langid", "note"]
lines = [
    "% Bibliografía de la tesina — archivo único y canónico.",
    "% Consolida estado_del_arte/referencias.bib, marco_teorico/referencias.bib,",
    "% tabla_resultados_sota/referencias_sota.bib y la versión previa de este archivo.",
    "% Claves normalizadas como <apellido><año><palabra>. No editar a mano sin",
    "% respetar esa convención; las referencias nuevas se proponen en refs_pendientes.md.",
    "",
]
for e in sorted(entries, key=lambda x: x["newkey"]):
    f = e["f"]
    # Zotero exporta los preprints de arXiv como @misc con publisher/number, campos
    # que biblatex no admite en ese tipo; la información ya está en eprint/eprinttype.
    is_arxiv = "arxiv" in (f.get("eprinttype", "") + f.get("publisher", "")).lower()
    if is_arxiv and e["type"] == "misc":
        f.pop("publisher", None)
        if "arxiv" in f.get("number", "").lower():
            f.pop("number", None)
    # Normaliza el ISSN: Zotero a veces exporta dos (papel y online) o sin guion.
    if "issn" in f:
        first = f["issn"].split(",")[0].strip()
        if re.fullmatch(r"\d{7}[\dX]", first):
            first = f"{first[:4]}-{first[4:]}"
        f["issn"] = first if re.fullmatch(r"\d{4}-\d{3}[\dX]", first) else ""
        if not f["issn"]:
            del f["issn"]
            log.append(f"  - {e['newkey']}: issn invalido, se descarta")
    lines.append(f"@{e['type']}{{{e['newkey']},")
    for k in order:
        if k in f and f[k]:
            lines.append(f"  {k} = {{{f[k]}}},")
    extra = sorted(k for k in f if k not in order and k not in DROP_SILENT and k in KEEP)
    for k in extra:
        lines.append(f"  {k} = {{{f[k]}}},")
    lines.append("}")
    lines.append("")

out = ROOT / "TFG" / "Bibliography" / "Bibliography.bib"
out.write_text("\n".join(lines), encoding="utf-8")

# --- report ----------------------------------------------------------------
rep = [f"Entradas unicas: {len(entries)}", ""]
rep += ["MAPA DE CLAVES (nueva <- original)", ""]
for newkey, old, src, aliases in sorted(mapping):
    al = f"   [+ {', '.join(aliases)}]" if aliases else ""
    rep.append(f"  {newkey:<32} <- {src}:{old}{al}")
rep += ["", "NOTAS", ""] + (log or ["  (sin incidencias)"])
Path(sys.argv[1] if len(sys.argv) > 1 else "report.txt").write_text(
    "\n".join(rep), encoding="utf-8")
print("\n".join(rep[:2]))
print(f"escrito: {out}")
