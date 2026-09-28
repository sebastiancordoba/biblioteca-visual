# -*- coding: utf-8 -*-
"""Incorpora las fichas de obra contrastadas con fuentes de museo y académicas.

Entrada: JSON con la verificación de cada obra, identificada por «libro:número de archivo»
(p. ej. "genesis:42"). Salida:
  · herramientas/sitio/datos/obras_fuentes.json — el registro verificado: los tres textos con
    sus llamadas a nota, las fuentes, las discrepancias y lo que se retiró.
  · las fichas de herramientas/data_*.py — «meta», «analysis», «history» y «bio» pasan a ser
    el texto verificado, sin llamadas, para que la aplicación muestre lo mismo que la página.

No escribe nada si algún registro falla las comprobaciones (las mismas que las biografías de
autor: toda llamada con su fuente, ninguna fuente de Wikipedia, ninguna frase con datos sin
cita). Y avisa si la «meta» corregida cambia la sede en la que el mapa sitúa la obra.

Formato de cada obra:
  {"id", "meta", "analysis", "history", "bio", "fuentes": [{"n", "obra", "titulo", "autor", "url"}],
   "discrepancias": [...], "retirado": [...], "notas": "..."}

Uso: python3 herramientas/incorporar_obras.py resultado_obras1.json ...
"""
import glob, io, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
sys.path.insert(0, os.path.join(RAIZ, "herramientas", "artefacto"))
from incorporar_fuentes import numeros, LLAMADA
from libros import todos
import mapa as _mapa

SALIDA = os.path.join(RAIZ, "herramientas", "sitio", "datos", "obras_fuentes.json")
CAMPOS = ("analysis", "history", "bio")


def frases_sin_cita(t):
    """Frases con contenido que no llevan ninguna llamada. No se corta dentro de «…»: las
    firmas se citan con sus puntos («BRVEGEL. FE. M.D.LXIII») y no son finales de frase."""
    oculto = re.sub(r"«[^»]*»", lambda m: m.group(0).replace(".", "\x00").replace("?", "\x01"), t)
    trozos = re.split(r"(?:(?<=[.!?])|(?<=[.!?]»))(?<! [A-Z]\.)\s+(?=[A-ZÁÉÍÓÚÑ«¿¡])", oculto)
    # «Sin datos verificados: …» es una nota de la colección, no un dato: no lleva cita.
    return [f.replace("\x00", ".").replace("\x01", "?") for f in trozos
            if len(f) > 25 and not LLAMADA.search(f) and not f.startswith("Sin datos verificados")]


def problemas(r, ids):
    p = []
    if r.get("id") not in ids: p.append(f"id desconocido {r.get('id')!r}")
    fs = r.get("fuentes") or []
    nums = {f.get("n") for f in fs}
    citados = set()
    for c in CAMPOS:
        t = r.get(c) or ""
        if not t.strip(): p.append(f"«{c}» vacío")
        citados |= numeros(t)
        for f in frases_sin_cita(t): p.append(f"{c}: frase sin fuente: «{f[:70]}…»")
    for x in r.get("discrepancias") or []: citados |= numeros(x)
    citados |= numeros(r.get("meta") or "")
    if citados - nums: p.append(f"llamadas sin fuente: {sorted(citados - nums)}")
    ctx = " ".join((r.get("discrepancias") or []) + [r.get("notas") or ""]).lower()
    sueltas = [f["n"] for f in fs if f.get("n") not in citados
               and not any(w in ctx for w in re.findall(r"[a-záéíóúñ]{4,}", (f.get("obra") or "").lower())[:3])]
    if sueltas: p.append(f"fuentes que no se citan ni se nombran: {sueltas}")
    for f in fs:
        u = f.get("url") or ""
        if not re.match(r"https?://[^/\s]+\.[^/\s]+", u): p.append(f"fuente {f.get('n')} sin URL válida: {u!r}")
        if "wikipedia.org" in u: p.append(f"fuente {f.get('n')} es Wikipedia")
    if not (r.get("meta") or "").strip(): p.append("meta vacía")
    return p


def entradas():
    """id -> (ficha actual, archivo de datos que la contiene, primer archivo de imagen)."""
    fuera = {}
    for libro, ents in todos():
        for d in ents:
            num = re.match(r"\d+", d["files"][0]).group(0)
            fuera[f"{libro['id']}:{num}"] = d
    return fuera


def sustituir_en_datos(archivo_img, campos):
    """Cambia los campos de la ficha cuyo primer archivo es `archivo_img`, en el data_*.py
    que la contenga. La ficha va del «"files": [» hasta el cierre «\n}»."""
    for ruta in glob.glob(os.path.join(RAIZ, "herramientas", "data_*.py")):
        src = io.open(ruta, encoding="utf-8").read()
        i = src.find('"' + archivo_img + '"')
        if i < 0: continue
        ini = src.rfind("{", 0, i)
        fin = src.find("\n}", i)
        trozo = src[ini:fin]
        for campo, valor in campos.items():
            pat = re.compile(r'(\n\s*"' + campo + r'":\s*)"(?:[^"\\]|\\.)*"')
            trozo, n = pat.subn(lambda m: m.group(1) + json.dumps(valor, ensure_ascii=False), trozo, count=1)
            assert n == 1, f"no encuentro «{campo}» en la ficha de {archivo_img} ({os.path.basename(ruta)})"
        io.open(ruta, "w", encoding="utf-8").write(src[:ini] + trozo + src[fin:])
        return os.path.basename(ruta)
    raise AssertionError(f"no encuentro la ficha de {archivo_img} en ningún data_*.py")


def main(archivos):
    fichas = entradas()
    nuevos, errores = {}, {}
    for f in archivos:
        for r in json.load(io.open(f, encoding="utf-8")):
            pr = problemas(r, fichas)
            (errores.__setitem__(r.get("id"), pr) if pr else nuevos.__setitem__(r["id"], r))
    for i, pr in errores.items():
        print(f"RECHAZADA {i}:"); [print("    ", x) for x in pr]
    if errores:
        print(f"\n{len(errores)} obras con problemas: no se escribe nada."); return 1

    limpia = lambda t: re.sub(r"\s*" + LLAMADA.pattern, "", t).strip()
    cambios_sede = []
    for i, r in nuevos.items():
        d = fichas[i]
        antes = _mapa.museo_de(d)
        despues = _mapa.museo_de(dict(d, meta=limpia(r["meta"])))
        if antes != despues:
            cambios_sede.append(f"{i}: {antes} → {despues}   ({limpia(r['meta'])[-70:]})")
        sustituir_en_datos(d["files"][0], {"meta": limpia(r["meta"]),
                                           **{c: limpia(r[c]) for c in CAMPOS}})
    previo = json.load(io.open(SALIDA, encoding="utf-8")) if os.path.exists(SALIDA) else {}
    todo = {**previo, **nuevos}
    json.dump(todo, io.open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(f"{len(nuevos)} obras incorporadas · {len(todo)} en total en obras_fuentes.json · "
          f"{sum(len(r['fuentes']) for r in nuevos.values())} citas")
    if cambios_sede:
        print("\nATENCIÓN, la sede del mapa cambia:"); [print("   ", x) for x in cambios_sede]
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
