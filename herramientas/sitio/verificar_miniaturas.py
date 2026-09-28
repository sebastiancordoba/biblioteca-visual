# -*- coding: utf-8 -*-
"""Compara cada URL de miniatura que construye comun.py con la que da la API de Commons.

Se pregunta a la API en vez de descargar las imágenes: son tres peticiones en lugar de
cientos, y upload.wikimedia.org responde 429 enseguida a una ráfaga de descargas.
La API sugiere el servidor thumb.wikimedia.org; upload.wikimedia.org sirve las mismas
miniaturas, así que el servidor no cuenta como diferencia.

Uso: python3 herramientas/sitio/verificar_miniaturas.py
"""
import json, os, re, subprocess, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import ENL, REJILLA, VISOR, miniatura

limpia = lambda u: re.sub(r"[?&]utm_.*$", "", urllib.parse.unquote(u)).replace(
    "https://thumb.wikimedia.org/", "https://upload.wikimedia.org/")
titulos = {"File:" + urllib.parse.unquote(lk["original"].rsplit("/", 1)[1]).replace("_", " "): lk
           for lk in ENL.values()}
ts, malas, bien = sorted(titulos), [], 0
for ancho in (REJILLA, VISOR):
    for i in range(0, len(ts), 50):
        args = ["curl", "-s", "--get", "https://commons.wikimedia.org/w/api.php", "-A", "BibliotecaVisual/1.0"]
        for k, v in dict(action="query", format="json", prop="imageinfo", iiprop="url|size",
                         iiurlwidth=ancho, titles="|".join(ts[i:i + 50])).items():
            args += ["--data-urlencode", f"{k}={v}"]
        d = json.loads(subprocess.run(args, capture_output=True, text=True).stdout)
        norm = {n["to"]: n["from"] for n in d["query"].get("normalized", [])}
        for p in d["query"]["pages"].values():
            t = norm.get(p["title"], p["title"])
            if "imageinfo" not in p:
                malas.append(f"no existe en Commons: {t}"); continue
            ii = p["imageinfo"][0]
            suya = ii.get("thumburl") if ii["width"] > ancho else ii["url"]
            if limpia(miniatura(titulos[t], ancho)) != limpia(suya):
                malas.append(f"{ancho}px {t}\n      nuestra {miniatura(titulos[t], ancho)}\n      API     {limpia(suya)}")
            else:
                bien += 1
        time.sleep(3)
print(f"{len(ts)} archivos · {bien} de {2 * len(ts)} URL coinciden con la API de Commons")
for m in malas: print("  ", m)
sys.exit(1 if malas else 0)
