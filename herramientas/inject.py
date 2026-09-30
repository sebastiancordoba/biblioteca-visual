# -*- coding: utf-8 -*-
"""Vuelca las fichas de todos los libros del registro (herramientas/libros.py) en index.html.

Idempotente: los datos generados viven entre centinelas y se reescriben enteros en cada
pasada, de modo que se puede volver a ejecutar según se descargan más imágenes.
Solo se incluyen las obras cuyas imágenes existen realmente en disco.
"""
import io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libros import todos as _libros, sin_imagen as _sin_imagen
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "artefacto"))
_cwd = os.getcwd()
from mapa import museo_de as _museo_de, MUSEOS as _MUSEOS     # mapa.py cambia de directorio al importarse
os.chdir(_cwd)
from cronologia import año as _anio, etiqueta as _etq
from data_autores import AUTORES as _AUTORES
from retratos import RETRATOS as _RETRATOS, SIN_RETRATO as _SIN_RETRATO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # la raíz del repositorio
INI = "    /* ==== DATOS GENERADOS POR inject.py — NO EDITAR A MANO ==== */"
FIN = "    /* ==== FIN DATOS GENERADOS ==== */"

# Una imagen cuenta como presente si está en disco o si tiene su original enlazado en Commons
# (enlaces.json): el sitio la sirve desde Commons y la copia local ya no hace falta.
_ENL = json.load(io.open(os.path.join(ROOT, "herramientas", "artefacto", "datos", "enlaces.json"), encoding="utf-8"))
_RUTA_REFS = os.path.join(ROOT, "herramientas", "referencias.json")
_REFS = json.load(io.open(_RUTA_REFS, encoding="utf-8")) if os.path.exists(_RUTA_REFS) else {}

def disponible(folder, f):
    return os.path.exists(os.path.join(ROOT, folder, f)) or f"{folder}/{f}" in _ENL

def build(entries, folder):
    details, groups, omitted = [], [], []
    for e in entries:
        views = [(f, t) for f, t in zip(e["files"], e["views"])
                 if disponible(folder, f)]
        if not views:
            omitted.append(e["title"]); continue
        d = {k: e[k] for k in
             ("title","artist","meta","wikiUrl","snippet","analysis","history","bio")}
        # De qué libro viene la obra, dónde y, si lo hay, qué dice el autor de ella.
        if e.get("referencias"):
            d["referencias"] = e["referencias"]
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
    DETALLES, GRUPOS = {}, {}   # libro -> details y groups YA filtrados (autores y temas)
    # El literal `const BOOKS = {...}` de index.html queda vacío: cada libro se declara
    # ENTERO aquí, metadatos incluidos, desde el registro. Así un libro nuevo no exige
    # tocar el HTML. El salto de línea tras la llave es obligatorio: sin él, en la segunda
    # pasada el patrón casaba con el `{};` ya vaciado y se tragaba todo el código hasta el
    # siguiente `};` — la portada, librosReales y medio montarLibro.
    s = re.sub(r"const BOOKS = \{\n[\s\S]*?\n    \};", "const BOOKS = {};", s, count=1)

    for libro, entries in _libros():
        book_id, folder = libro["id"], libro["carpeta"]
        details, groups, omitted = build(entries, folder)
        # La sede canónica de cada obra —«Museo del Prado, Madrid»—, con las mismas reglas que
        # el mapa: la portada la muestra y cuenta las sedes con ella. Contar el último tramo de
        # «meta» daba 99 «sedes», porque cada número de inventario lo hacía distinto.
        for d in details:
            k = _museo_de(d)
            d["sede"] = f"{_MUSEOS[k][0]}, {_MUSEOS[k][1]}" if k else None
        # El pasaje de cada obra en los libros de la colección (referencias.json, por el número
        # de su archivo): se suma a las referencias que ya traiga la ficha.
        for d, g in zip(details, groups):
            num = re.match(r"\d+", os.path.basename(g[0]["src"])).group(0)
            for r in _REFS.get(f"{book_id}:{num}", []):
                d.setdefault("referencias", [])
                if r not in d["referencias"]: d["referencias"].append(r)
        counts[book_id] = len(details)
        print(f"{book_id}: {len(details)} obras, {sum(len(g) for g in groups)} imágenes"
              + (f"  (sin archivo: {', '.join(omitted)})" if omitted else ""))
        DETALLES[book_id], GRUPOS[book_id] = details, groups
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
        # Láminas sin imagen propia: no entran en details ni en groups, de modo que el visor,
        # la portada, la cronología y el mapa —que parten de la imagen— no se enteran.
        si = _sin_imagen(libro)
        if si:
            campos = ("title", "artist", "meta", "texto", "motivo", "enlace", "pagina", "cita")
            j = json.dumps([{k: x.get(k) for k in campos} for x in si], ensure_ascii=False, indent=2).replace("\n", "\n    ")
            blocks.append(f"    BOOKS.{book_id}.sinImagen = {j};")
            print(f"{book_id}: {len(si)} láminas sin imagen")

    # ---- la misma obra en varios libros ----
    # Dos fichas son la misma obra si su vista principal sale del mismo original de Commons.
    # Cada una enlaza con las demás («También en») y todas juntan sus referencias: el Júpiter y
    # Tetis de Ingres está en la Ilíada y en Las lágrimas de Eros.
    from urllib.parse import unquote
    from libros import POR_ID as _LIB
    def _original(libro, i):
        src = GRUPOS[libro][i][0]["src"][2:]
        x = _ENL.get(src)
        return unquote(x["original"]) if x else None
    misma = {}
    for libro in DETALLES:
        for i in range(len(DETALLES[libro])):
            k = _original(libro, i)
            if k: misma.setdefault(k, []).append((libro, i))
    for copias in misma.values():
        if len(copias) < 2: continue
        refs = []
        for libro, i in copias:
            for r in DETALLES[libro][i].get("referencias") or []:
                if r not in refs: refs.append(r)
        for libro, i in copias:
            d = DETALLES[libro][i]
            d["tambienEn"] = [{"libro": l, "i": j, "corto": _LIB[l]["corto"]} for l, j in copias if l != libro]
            if refs: d["referencias"] = refs
    print(f"obras en más de un libro: {sum(1 for c in misma.values() if len(c) > 1)}")
    # Los details ya están volcados en blocks: se reescriben los de los libros afectados.
    for libro in {l for c in misma.values() if len(c) > 1 for l, _ in c}:
        d = json.dumps(DETALLES[libro], ensure_ascii=False, indent=2).replace("\n", "\n    ")
        pre = f"    BOOKS.{libro}.details = "
        k = next(n for n, b in enumerate(blocks) if pre in b)
        cab, resto = blocks[k].split(pre, 1)
        blocks[k] = cab + pre + d + ";\n    BOOKS." + libro + ".groups = " + resto.split(f";\n    BOOKS.{libro}.groups = ", 1)[1]

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

    # Temas, para la pestaña Temas de la Biblioteca. Las obras vienen por el número de su
    # archivo; aquí se traducen al índice de los details YA filtrados, que es el del visor
    # (en el sitio publicado la ruta de la imagen cambia a Commons y el número se pierde).
    from temas import TEMAS as _TEMAS
    from libros import POR_ID as _POR_ID
    temas = []
    for t in _TEMAS:
        obras = []
        for lb, num in t["obras"]:
            idx = next((i for i, g in enumerate(GRUPOS.get(lb, []))
                        if os.path.basename(g[0]["src"]).startswith(num + "_")), None)
            if idx is not None: obras.append({"libro": lb, "i": idx})
        if not obras: continue
        temas.append({"clave": t["clave"], "titulo": t["titulo"], "lema": t["lema"],
                      "libros": list(dict.fromkeys(_POR_ID[lb]["corto"] for lb, _, _ in t["pasajes"])),
                      "obras": obras})
    print(f"temas: {len(temas)}")
    blocks.append("    const TEMAS = " +
                  json.dumps(temas, ensure_ascii=False, indent=2).replace("\n", "\n    ") + ";")

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
