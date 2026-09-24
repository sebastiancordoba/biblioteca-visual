# -*- coding: utf-8 -*-
"""Vuelca las fichas de todos los libros del registro (herramientas/libros.py) en index.html.

Idempotente: los datos generados viven entre centinelas y se reescriben enteros en cada
pasada, de modo que se puede volver a ejecutar según se descargan más imágenes.
Solo se incluyen las obras cuyas imágenes existen realmente en disco.
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libros import todos as _libros
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

def main():
    path = os.path.join(ROOT, "index.html")
    s = io.open(path, encoding="utf-8").read()

    blocks, counts = [], {}
    DETALLES = {}          # libro -> details YA filtrados, para enlazar los autores
    # El literal `const BOOKS = {...}` de index.html queda vacío: cada libro se declara
    # ENTERO aquí, metadatos incluidos, desde el registro. Así un libro nuevo no exige
    # tocar el HTML. El salto de línea tras la llave es obligatorio: sin él, en la segunda
    # pasada el patrón casaba con el `{};` ya vaciado y se tragaba todo el código hasta el
    # siguiente `};` — la portada, librosReales y medio montarLibro.
    s = re.sub(r"const BOOKS = \{\n[\s\S]*?\n    \};", "const BOOKS = {};", s, count=1)

    for libro, entries in _libros():
        book_id, folder = libro["id"], libro["carpeta"]
        details, groups, omitted = build(entries, folder)
        counts[book_id] = len(details)
        print(f"{book_id}: {len(details)} obras, {sum(len(g) for g in groups)} imágenes"
              + (f"  (sin archivo: {', '.join(omitted)})" if omitted else ""))
        DETALLES[book_id] = details
        meta = {"esLibro": True, "corto": libro["corto"], "tag": libro["tag"],
                "title": libro["title"], "sub": libro["sub"],
                "firstTab": book_id + "-gallery", "headings": libro["headings"],
                "carpeta": folder}
        m = json.dumps(meta, ensure_ascii=False)
        d = json.dumps(details, ensure_ascii=False, indent=2).replace("\n", "\n    ")
        g = json.dumps(groups,  ensure_ascii=False, indent=2).replace("\n", "\n    ")
        blocks.append(f"    BOOKS.{book_id} = Object.assign({m},\n"
                      f"      {{ details: [], groups: [] }});\n"
                      f"    BOOKS.{book_id}.details = {d};\n    BOOKS.{book_id}.groups = {g};")

    # ---- autores ----
    # Cada autor se enlaza con sus obras por el campo `artist` de las fichas, sin listas
    # escritas a mano: al añadir una obra suya aparece aquí sola. Solo salen los autores
    # que de verdad tienen alguna obra en la colección.
    # Se enlaza por ÍNDICE sobre los details ya filtrados, nunca por título: hay títulos
    # repetidos —«El sacrificio de Isaac» es de Caravaggio y de Rembrandt, «Adán y Eva» de
    # Cranach dos veces y de Durero— y buscar por título le colgaba a un autor la obra de
    # otro. Y tiene que ser sobre los details YA filtrados, porque las obras cuya imagen
    # falta no llegan a la página y correrían todos los índices.
    porPatron = {}
    for libro, details in DETALLES.items():
        for i, d in enumerate(details):
            porPatron.setdefault(d["artist"].rsplit(" (", 1)[0].strip(), []).append(
                {"libro": libro, "i": i, "title": d["title"]})
    autores = []
    for a in _AUTORES:
        suyas = []
        for pat in a["patron"]:
            suyas += porPatron.get(pat, [])
        if not suyas: continue
        ret = os.path.join(ROOT, "Autores", a["clave"] + ".jpg")
        # Año ordenable: el primero que aparece en `anios`, negativo si lleva a.C.
        _n = re.findall(r"\d{3,4}", a["anios"])
        _nace = (int(_n[0]) * (-1 if "a.C." in a["anios"] else 1)) if _n else None
        autores.append({
            "clave": a["clave"], "nombre": a["nombre"], "anios": a["anios"], "nace": _nace,
            "oficio": a["oficio"], "bio": a["bio"],
            "retrato": ("./Autores/" + a["clave"] + ".jpg") if os.path.exists(ret) else None,
            "retratoPie": _RETRATOS.get(a["clave"], ("", ""))[1],
            "obras": suyas,
        })
    # Guardia en la construcción: cada obra colgada de un autor tiene que ser suya. Esto
    # es lo que faltaba cuando a Rembrandt le salía el Caravaggio.
    for a in autores:
        pats = [p.lower() for p in
                next(x for x in _AUTORES if x["clave"] == a["clave"])["patron"]]
        for o in a["obras"]:
            real = DETALLES[o["libro"]][o["i"]]["artist"].rsplit(" (", 1)[0].strip().lower()
            assert real in pats, (
                f'«{a["nombre"]}» tiene colgada «{o["title"]}», que es de «{real}». '
                f'Sus patrones son {pats}')

    autores.sort(key=lambda x: x["nombre"])
    print(f"autores: {len(autores)} con obra en la colección, "
          f"{sum(1 for x in autores if x['retrato'])} con retrato")
    blocks.append("    const AUTORES = " +
                  json.dumps(autores, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ";")

    generated = INI + "\n" + "\n\n".join(blocks) + "\n" + FIN

    if INI in s:
        s = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda m: generated, s, flags=re.S)
    else:
        anchor = re.search(r"^ *let currentBook = '[a-z]+';", s, re.M).group(0)
        s = s.replace(anchor, generated + "\n\n" + anchor, 1)

    for book_id, n in counts.items():
        s = re.sub(r"(switchBook\('" + book_id + r"', this\)\">[^<]*<span class=\"book-count\">)\d+(</span>)",
                   r"\g<1>" + str(n) + r"\g<2>", s)
        s = re.sub(r"(switchTab\('" + book_id + r"-gallery', this\)\">.*?Colección \()\d+(\))",
                   r"\g<1>" + str(n) + r"\g<2>", s, flags=re.S)

    io.open(path, "w", encoding="utf-8").write(s)
    print("index.html actualizado")

main()
