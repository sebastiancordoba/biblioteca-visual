# -*- coding: utf-8 -*-
"""Vuelca las fichas de Gilgamesh y La Ilíada en index.html.

Idempotente: los datos generados viven entre centinelas y se reescriben enteros en cada
pasada, de modo que se puede volver a ejecutar según se descargan más imágenes.
Solo se incluyen las obras cuyas imágenes existen realmente en disco.
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_genesis import GENESIS
from data_gilgamesh import GILGAMESH
from data_iliada import ILIADA
from cronologia import año as _anio, etiqueta as _etq
from data_autores import AUTORES as _AUTORES
from retratos import RETRATOS as _RETRATOS, SIN_RETRATO as _SIN_RETRATO

ROOT = "/Users/sebastiancordoba/Library/Mobile Documents/com~apple~CloudDocs/Documents/Pinturas"
INI = "    /* ==== DATOS GENERADOS POR inject.py — NO EDITAR A MANO ==== */"
FIN = "    /* ==== FIN DATOS GENERADOS ==== */"

def build(entries, folder):
    details, groups, omitted = [], [], []
    for e in entries:
        views = [(f, t) for f, t in zip(e["files"], e["views"])
                 if os.path.exists(os.path.join(ROOT, folder, f))]
        if not views:
            omitted.append(e["title"]); continue
        d = {k: e[k] for k in
             ("title","artist","meta","wikiUrl","snippet","analysis","history","bio")}
        # El año permite ordenar la galería cronológicamente sin recalcularlo en el navegador.
        a = _anio(e)
        if a is not None:
            d["anio"] = a
            d["fecha"] = _etq(a)
        details.append(d)
        groups.append([{"src": f"./{folder}/{f}", "title": t} for f, t in views])
    return details, groups, omitted

def match_bracket(s, i):
    """Devuelve el índice tras el ] que cierra el [ que empieza en i (ignora corchetes en cadenas)."""
    depth, j, instr, esc = 0, i, False, False
    while j < len(s):
        c = s[j]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        else:
            if c == '"': instr = True
            elif c == "[": depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0: return j + 1
        j += 1
    raise ValueError("corchete sin cerrar")

def normalize(s, book_id):
    """Devuelve los arrays de ese libro dentro de BOOKS a [] para poder regenerar."""
    b = s.find(book_id + ":")
    if b < 0: return s
    for key in ("details", "groups"):
        k = s.find(key + ":", b)
        if k < 0: continue
        lb = s.find("[", k)
        end = match_bracket(s, lb)
        s = s[:lb] + "[]" + s[end:]
    return s

def main():
    path = os.path.join(ROOT, "index.html")
    s = io.open(path, encoding="utf-8").read()

    blocks, counts = [], {}
    for book_id, entries, folder in (("genesis", GENESIS, "Génesis"),
                                     ("gilgamesh", GILGAMESH, "Gilgamesh"),
                                     ("iliada", ILIADA, "Ilíada")):
        s = normalize(s, book_id)
        details, groups, omitted = build(entries, folder)
        counts[book_id] = len(details)
        print(f"{book_id}: {len(details)} obras, {sum(len(g) for g in groups)} imágenes"
              + (f"  (sin archivo: {', '.join(omitted)})" if omitted else ""))
        if not details: continue
        d = json.dumps(details, ensure_ascii=False, indent=2).replace("\n", "\n    ")
        g = json.dumps(groups,  ensure_ascii=False, indent=2).replace("\n", "\n    ")
        blocks.append(f"    BOOKS.{book_id}.details = {d};\n    BOOKS.{book_id}.groups = {g};")

    # ---- autores ----
    # Cada autor se enlaza con sus obras por el campo `artist` de las fichas, sin listas
    # escritas a mano: al añadir una obra suya aparece aquí sola. Solo salen los autores
    # que de verdad tienen alguna obra en la colección.
    porPatron = {}
    for libro, arr in (("genesis", GENESIS), ("gilgamesh", GILGAMESH), ("iliada", ILIADA)):
        for i, e in enumerate(arr):
            porPatron.setdefault(e["artist"].rsplit(" (", 1)[0].strip(), []).append(
                {"libro": libro, "title": e["title"]})
    autores = []
    for a in _AUTORES:
        suyas = []
        for pat in a["patron"]:
            suyas += porPatron.get(pat, [])
        if not suyas: continue
        ret = os.path.join(ROOT, "Autores", a["clave"] + ".jpg")
        autores.append({
            "clave": a["clave"], "nombre": a["nombre"], "anios": a["anios"],
            "oficio": a["oficio"], "bio": a["bio"],
            "retrato": ("./Autores/" + a["clave"] + ".jpg") if os.path.exists(ret) else None,
            "retratoPie": _RETRATOS.get(a["clave"], ("", ""))[1],
            "obras": suyas,
        })
    autores.sort(key=lambda x: x["nombre"])
    print(f"autores: {len(autores)} con obra en la colección, "
          f"{sum(1 for x in autores if x['retrato'])} con retrato")
    blocks.append("    const AUTORES = " +
                  json.dumps(autores, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ";")

    generated = INI + "\n" + "\n\n".join(blocks) + "\n" + FIN

    if INI in s:
        s = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda m: generated, s, flags=re.S)
    else:
        anchor = "    let currentBook = 'genesis';"
        assert anchor in s
        s = s.replace(anchor, generated + "\n\n" + anchor, 1)

    for book_id, n in counts.items():
        s = re.sub(r"(switchBook\('" + book_id + r"', this\)\">[^<]*<span class=\"book-count\">)\d+(</span>)",
                   r"\g<1>" + str(n) + r"\g<2>", s)
        s = re.sub(r"(switchTab\('" + book_id + r"-gallery', this\)\">.*?Colección \()\d+(\))",
                   r"\g<1>" + str(n) + r"\g<2>", s, flags=re.S)

    io.open(path, "w", encoding="utf-8").write(s)
    print("index.html actualizado")

main()
