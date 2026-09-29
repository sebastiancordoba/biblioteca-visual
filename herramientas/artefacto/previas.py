# -*- coding: utf-8 -*-
"""Genera las vistas previas de 900 px que se incrustan en el artefacto.

Antes esto se hacía a mano con sips y, al entrar obras nuevas, build4 se caía buscando
una previa que nadie había generado. Ahora es un paso más de la cadena: solo trabaja
sobre lo que falta o ha cambiado, así que repetirlo no cuesta nada.
"""
import io, os, re, subprocess
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from libros import PATRON_RUTA   # carpetas de todos los libros, del registro

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP  = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
TH   = os.path.join(TMP, "th2")
LADO, CALIDAD = 700, 38
# Los retratos de autor ilustran una tarjeta de 168 px de alto: a 820 px pesarían
# treinta y siete veces más de lo que hace falta.
LADO_AUTOR = 400
os.chdir(ROOT); os.makedirs(TH, exist_ok=True)

# Si cambian el lado o la calidad hay que rehacerlas todas: si no, quedan mezcladas
# unas con los ajustes viejos y otras con los nuevos, y el peso no baja.
sello = os.path.join(TH, ".ajustes")
firma = f"{LADO}x{CALIDAD}"
ajustes_cambiaron = (not os.path.exists(sello)) or io.open(sello).read().strip() != firma

doc = io.open("index.html", encoding="utf-8").read()
rutas = sorted({m.group(1) for m in
                re.finditer(PATRON_RUTA, doc)})

nuevas = saltadas = 0
for rel in rutas:
    origen = os.path.join(ROOT, rel)
    destino = os.path.join(TH, rel.replace("/", "__"))
    if not os.path.exists(origen):
        continue          # sin copia local: si está enlazada en Commons, el sitio la sirve de allí
    if (not ajustes_cambiaron
            and os.path.exists(destino)
            and os.path.getmtime(destino) >= os.path.getmtime(origen)):
        saltadas += 1; continue
    lado = LADO_AUTOR if rel.startswith("Autores/") else LADO
    subprocess.run(["sips", "-Z", str(lado), "-s", "format", "jpeg",
                    "-s", "formatOptions", str(CALIDAD),
                    origen, "--out", destino],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    nuevas += 1

io.open(sello, "w").write(firma)
print(f"previas: {nuevas} generadas · {saltadas} ya al día · {len(rutas)} en total "
      f"({LADO} px, calidad {CALIDAD})")
# Sin vista previa solo puede quedar lo que no está en disco pero sí enlazado en Commons: el
# sitio lo sirve desde allí. Una imagen que no está en ninguno de los dos sitios es un error.
import json as _json
_enl = _json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "enlaces.json"), encoding="utf-8"))
faltan = [r for r in rutas if not os.path.exists(os.path.join(TH, r.replace('/', '__')))]
solo_commons = [r for r in faltan if r in _enl]
if solo_commons: print(f"previas: {len(solo_commons)} sin copia local, se sirven desde Commons")
faltan = [r for r in faltan if r not in _enl]
assert not faltan, "sin vista previa ni enlace a Commons: " + ", ".join(faltan)
