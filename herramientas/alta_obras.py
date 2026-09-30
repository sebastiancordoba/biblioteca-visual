# -*- coding: utf-8 -*-
"""Da de alta obras nuevas a partir de fichas ya redactadas con fuentes.

Las obras nuevas no se descargan: se enlazan a su archivo de Wikimedia Commons, que es de
donde el sitio las sirve. Cada ficha llega con sus textos citados ([n]) y sus fuentes, y aquí:
  1. se valida con las mismas reglas que incorporar_obras.py (llamadas con fuente, ninguna
     fuente de Wikipedia, ninguna frase con datos sin cita) y, además, que el autor lleve la
     fecha en cifras entre paréntesis, porque la cronología se ordena por ella;
  2. recibe el número siguiente de su libro (NN) y un nombre de archivo que es solo su
     identificador, «NN_Titulo.jpg» (y «NNb_…» para la segunda vista);
  3. se escribe en herramientas/data_altas_<libro>.py, el manifiesto herramientas/altas.tsv
     (identificador → archivo de Commons, de donde enlaces.py saca el original) y
     herramientas/sitio/datos/obras_fuentes.json (el texto con sus notas y sus fuentes).
Si una ficha no pasa, no se escribe nada de ese archivo de entrada.

Uso: python3 herramientas/alta_obras.py fichas_exodo.json [fichas_….json …]
"""
import io, json, os, re, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
from incorporar_obras import frases_sin_cita
from incorporar_fuentes import numeros
from libros import POR_ID, todos

TSV = os.path.join(RAIZ, "herramientas", "altas.tsv")
FUENTES = os.path.join(RAIZ, "herramientas", "sitio", "datos", "obras_fuentes.json")
CAMPOS = ("analysis", "history", "bio")


def ascii_(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


def nombre_archivo(num, sufijo, titulo):
    base = re.sub(r"[^A-Za-z0-9]+", "_", ascii_(titulo)).strip("_")
    return f"{num}{sufijo}_{base[:60].rstrip('_')}.jpg"


def problemas(o):
    p = []
    if o.get("libro") not in POR_ID: p.append(f"libro desconocido {o.get('libro')!r}")
    for c in ("title", "artist", "meta", "snippet"):
        if not (o.get(c) or "").strip(): p.append(f"falta «{c}»")
    if not re.search(r"\([^)]*\d{3,4}[^)]*\)", o.get("artist") or ""):
        p.append(f"el autor no lleva la fecha en cifras entre paréntesis: {o.get('artist')!r}")
    arch, vis = o.get("archivos") or [], o.get("views") or []
    if not arch or len(arch) != len(vis): p.append("«archivos» y «views» no emparejan")
    if any(not a.startswith("File:") for a in arch): p.append("un archivo no empieza por «File:»")
    fs = o.get("fuentes") or []
    nums = {f.get("n") for f in fs}
    citados = set()
    for c in CAMPOS:
        t = o.get(c) or ""
        if not t.strip(): p.append(f"«{c}» vacío")
        citados |= numeros(t)
        for f in frases_sin_cita(t): p.append(f"{c}: frase sin fuente: «{f[:70]}…»")
    for x in o.get("discrepancias") or []: citados |= numeros(x)
    if citados - nums: p.append(f"llamadas sin fuente: {sorted(citados - nums)}")
    for f in fs:
        u = f.get("url") or ""
        if not re.match(r"https?://[^/\s]+\.[^/\s]+", u): p.append(f"fuente {f.get('n')} sin URL válida")
        if "wikipedia.org" in u: p.append(f"fuente {f.get('n')} es Wikipedia")
    return p


def siguiente_numero(libro):
    mx = 0
    for l, ents in todos():
        if l["id"] == libro:
            for e in ents:
                m = re.match(r"(\d+)", e["files"][0])
                if m: mx = max(mx, int(m.group(1)))
    return mx + 1


def main(entradas):
    todas, errores, descartadas = [], {}, []
    for f in entradas:
        d = json.load(io.open(f, encoding="utf-8"))
        descartadas += d.get("descartadas", [])
        for o in d.get("obras", []):
            pr = problemas(o)
            if pr: errores[o.get("title")] = pr
            else: todas.append(o)
    for t, pr in errores.items():
        print(f"RECHAZADA «{t}»:"); [print("    ", x) for x in pr]
    if errores:
        print(f"\n{len(errores)} fichas con problemas: no se escribe nada."); return 1

    fuentes = json.load(io.open(FUENTES, encoding="utf-8"))
    tsv = io.open(TSV, "a", encoding="utf-8")
    porlibro = {}
    contador = {}
    for o in todas:
        lb = o["libro"]
        n = contador.get(lb) or siguiente_numero(lb)
        contador[lb] = n + 1
        num = f"{n:02d}"
        carpeta = POR_ID[lb]["carpeta"]
        files = [nombre_archivo(num, "" if i == 0 else chr(97 + i), o["title"]) for i in range(len(o["archivos"]))]
        for fn, arch in zip(files, o["archivos"]):
            tsv.write(f"{carpeta}/{fn}\t{arch}\n")
        limpia = lambda t: re.sub(r"\s*\[\d+(?:\s*[,–-]\s*\d+)*\]", "", t).strip()
        porlibro.setdefault(lb, []).append({
            "files": files, "views": o["views"], "title": o["title"], "artist": o["artist"],
            "meta": o["meta"], "wikiUrl": o.get("wikiUrl"), "snippet": o["snippet"],
            **{c: limpia(o[c]) for c in CAMPOS},
            **({"referencias": o["referencias"]} if o.get("referencias") else {})})
        fuentes[f"{lb}:{num}"] = {"id": f"{lb}:{num}", "meta": o["meta"],
                                  **{c: o[c] for c in CAMPOS},
                                  "fuentes": o["fuentes"], "discrepancias": o.get("discrepancias", []),
                                  "retirado": [], "notas": o.get("notas", "")}
        print(f"  + {lb}:{num}  {o['title'][:60]}")
    tsv.close()
    json.dump(fuentes, io.open(FUENTES, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)

    for lb, obras in porlibro.items():
        var = POR_ID[lb]["var"]
        propio = POR_ID[lb]["datos"] == f"data_{lb}" and not os.path.exists(os.path.join(RAIZ, "herramientas", f"data_{lb}.py"))
        ruta = os.path.join(RAIZ, "herramientas", (f"data_{lb}.py" if propio else f"data_altas_{lb}.py"))
        nombre_var = var if propio else f"ALTAS_{var}"
        previas = []
        if os.path.exists(ruta):
            ns = {}; exec(io.open(ruta, encoding="utf-8").read(), ns); previas = ns.get(nombre_var, [])
        io.open(ruta, "w", encoding="utf-8").write(
            "# -*- coding: utf-8 -*-\n# Obras dadas de alta con alta_obras.py, desde fichas redactadas con fuentes.\n"
            "# El texto con sus notas y fuentes está en herramientas/sitio/datos/obras_fuentes.json.\n"
            f"{nombre_var} = " + json.dumps(previas + obras, ensure_ascii=False, indent=1) + "\n")
        if not propio:
            base = os.path.join(RAIZ, "herramientas", POR_ID[lb]["datos"] + ".py")
            src = io.open(base, encoding="utf-8").read()
            enganche = f"from data_altas_{lb} import ALTAS_{var}"
            if enganche not in src:
                io.open(base, "a", encoding="utf-8").write(
                    f"\n# Altas con fuentes (alta_obras.py).\n{enganche}\n{var} = {var} + ALTAS_{var}\n")
        print(f"{lb}: {len(obras)} obras en {os.path.basename(ruta)}")
    if descartadas:
        print("\nDescartadas por quien redactó las fichas:")
        for x in descartadas: print(f"   «{x.get('titulo')}»: {x.get('motivo')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
