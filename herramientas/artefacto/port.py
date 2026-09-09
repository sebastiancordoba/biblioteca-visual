# -*- coding: utf-8 -*-
"""Porta index.html tal cual al formato de artefacto.

No se reescribe el visor: se toma el archivo real y solo se cambian las rutas de imagen
por vistas previas incrustadas, porque un artefacto no puede cargar archivos externos.
Así la cuadrícula, el zoom, el desplazamiento con WASD y la navegación quedan idénticos.
"""
import base64, io, json, os, re, urllib.parse

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP  = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
TH   = os.path.join(TMP, "th2")
os.chdir(ROOT)

s = io.open("index.html", encoding="utf-8").read()

# ---- 1. quedarse con la cabecera útil (título, fuentes, estilos) y el cuerpo ----
head = s[s.index("<head>")+6 : s.index("</head>")]
body = s[s.index("<body>")+6 : s.index("</body>")]
head = re.sub(r'\s*<meta charset[^>]*>', '', head)          # los pone el propio artefacto
head = re.sub(r'\s*<meta name="viewport"[^>]*>', '', head)
head = head.replace("Pinturas: Biblioteca Visual de los Grandes Libros", "Los Tres Libros")

doc = head + "\n" + body

# ---- 2. rutas de imagen -> vistas previas incrustadas ----
cache = {}
def uri(rel):
    if rel in cache: return cache[rel]
    p = os.path.join(TH, rel.replace("/", "__"))
    if not os.path.exists(p): return None
    cache[rel] = "data:image/jpeg;base64," + base64.b64encode(open(p,"rb").read()).decode()
    return cache[rel]

faltan = []
def sub(m):
    rel = m.group(1)
    u = uri(rel)
    if u is None:
        faltan.append(rel); return m.group(0)
    return u

doc, n = re.subn(r'\./((?:Génesis|Gilgamesh|Ilíada)/[^\'"]+\.jpg)', sub, doc)
print(f"rutas sustituidas: {n} · distintas: {len(cache)} · sin previa: {len(set(faltan))}")

io.open(os.path.join(TMP,"doc.part"),"w",encoding="utf-8").write(doc)
print(f"parcial: {os.path.getsize(os.path.join(TMP,'doc.part'))/1e6:.1f} MB")
