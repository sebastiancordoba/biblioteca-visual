import json, subprocess, sys, urllib.parse

UA = "PinturasArtCollection/1.0 (personal art study collection)"

import time
def api(params):
    params["format"] = "json"
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        r = subprocess.run(["curl","-sL","-m","90","-A",UA,url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return {}

def search(term, limit=12):
    d = api({"action":"query","list":"search","srsearch":f"{term} filetype:bitmap",
             "srnamespace":"6","srlimit":limit})
    return [r["title"] for r in d.get("query",{}).get("search",[])]

def info(titles):
    out=[]
    titles = [t for t in titles if t]
    if not titles: return out
    for i in range(0,len(titles),20):
        d = api({"action":"query","titles":"|".join(titles[i:i+20]),
                 "prop":"imageinfo","iiprop":"url|size|mime"})
        for pg in d.get("query",{}).get("pages",{}).values():
            ii = (pg.get("imageinfo") or [None])[0]
            if not ii: continue
            out.append({"title":pg["title"],"w":ii["width"],"h":ii["height"],
                        "mp":round(ii["width"]*ii["height"]/1e6,1),
                        "url":ii["url"],"mime":ii["mime"]})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CALIDAD DE FUENTE
# Más megapíxeles no es mejor si la imagen es la foto que alguien tomó en la sala:
# sale en perspectiva, con reflejos del cristal, con el marco y con el color de la
# iluminación de la galería. Para una PINTURA siempre es preferible la reproducción
# plana de la institución, aunque tenga menos resolución.
# Para escultura, relieve o arqueología ocurre lo contrario: no existe "reproducción
# plana" y una buena fotografía es la única opción posible.
# ─────────────────────────────────────────────────────────────────────────────

# Marcas de reproducción institucional (fotografía cenital, sin marco ni reflejos)
BUENAS = ["google art project", "wga", "rijksmuseum", "rp-p-", "rp-f-", "sk-a-",
          "met dp", "met dt", "prado", "-mba-", "national gallery", "lacma",
          "nationalmuseum", "hermitage", "artic", "yale center", "getty"]

# Marcas de fotografía de visitante o de sala
MALAS = ["panoramio", "geograph", "flickr", "exposition", "exhibition", "ausstellung",
         "display case", "inside a display", "vista de sala", "wikivoyage banner",
         "journée", "concert", "villa ", "photographed by", "on october", "on june"]

# Nombres de archivo de cámara sin renombrar: DSC2249, IMG_0412, P1170972, _28423089016
import re as _re
CAMARA = _re.compile(r"(dsc[_ -]?\d|dscn\d|img[_ -]?\d|_mg_\d|p\d{7}|\(\d{9,}\)|\d{10,})",
                     _re.I)

def source_grade(title):
    """Devuelve ('institucional'|'foto de sala'|'?') según el nombre del archivo.

    No es infalible —es una heurística sobre el nombre—, pero separa bien la
    reproducción cenital del museo de la foto que alguien tomó en la sala."""
    t = title.lower()
    if any(k in t for k in BUENAS): return "institucional"
    if any(k in t for k in MALAS) or CAMARA.search(t): return "foto de sala"
    return "?"

def report(titles, kind="pintura"):
    """kind='pintura' antepone la reproducción institucional a los megapíxeles.
       kind='objeto' (escultura, relieve, cerámica, arqueología) ordena solo por resolución."""
    rows = info(titles)
    for r in rows:
        r["grade"] = source_grade(r["title"])
    if kind == "pintura":
        rank = {"institucional": 0, "?": 1, "foto de sala": 2}
        rows.sort(key=lambda r: (rank[r["grade"]], -r["mp"]))
    else:
        rows.sort(key=lambda r: -r["mp"])
    for r in rows:
        print(f'{r["mp"]:>7} MP  {r["w"]}x{r["h"]}  [{r["grade"]:<14}] {r["title"]}')

if __name__ == "__main__":
    mode = sys.argv[1]
    # último argumento opcional: "objeto" para escultura/arqueología (ordena solo por resolución)
    kind = "objeto" if sys.argv[-1] == "objeto" else "pintura"
    args = sys.argv[:-1] if sys.argv[-1] == "objeto" else sys.argv
    if mode == "search":
        report(search(args[2], int(args[3]) if len(args) > 3 else 12), kind)
    elif mode == "info":
        report(args[2:], kind)
