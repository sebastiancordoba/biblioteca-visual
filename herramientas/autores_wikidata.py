# -*- coding: utf-8 -*-
"""Baja de Wikidata los datos comprobables de cada autor y los guarda en
herramientas/sitio/datos/autores_wikidata.json, que las páginas de autor muestran con un
enlace a la fuente de cada dato.

Se guarda en el repositorio en vez de pedirse al construir: la construcción no depende de
la red ni del límite de tasa de Wikimedia, y un cambio en Wikidata se ve como un cambio en
git antes de publicarse. Para actualizar, se vuelve a ejecutar.

Qué se toma y de dónde (propiedades de Wikidata):
  P569/P19  nacimiento: fecha y lugar      P570/P20  muerte: fecha y lugar
  P135      movimiento                     P106      ocupación
  P245      Getty ULAN                     P214      VIAF
  P244      Library of Congress            P373      categoría de Commons
Las fechas respetan la precisión con que Wikidata las da (día, mes, año, década, siglo) y el
calificador «circa» (P1480): no se inventa un día donde solo consta el año.

Uso:  python3 herramientas/autores_wikidata.py
"""
import datetime, io, json, os, re, subprocess, sys, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
from data_autores import AUTORES
from verificar_autores import ARTICULOS

SALIDA = os.path.join(RAIZ, "herramientas", "sitio", "datos", "autores_wikidata.json")
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]
CIRCA = "Q5727902"

# Obras de referencia académicas, por orden de peso. Wikidata guarda el identificador de la
# entrada de cada autor en ellas; la URL se construye con el formato que la propia Wikidata
# declara para cada propiedad (P1630), que se pide en cada ejecución: no se escribe a mano.
REFERENCIAS = [
 ("P8406", "Grove Art Online (Oxford)"),
 ("P1986", "Dizionario Biografico degli Italiani (Treccani)"),
 ("P4459", "Diccionario Biográfico Español (Real Academia de la Historia)"),
 ("P3021", "Encyclopaedia Iranica"),
 ("P7902", "Deutsche Biographie (NDB/ADB)"),
 ("P1415", "Oxford Dictionary of National Biography"),
 ("P650",  "RKD, Instituto Neerlandés de Historia del Arte"),
 ("P2843", "Benezit Dictionary of Artists (Oxford)"),
 ("P5321", "Enciclopedia del Museo del Prado"),
 ("P3365", "Enciclopedia Treccani"),
 ("P3219", "Encyclopædia Universalis"),
 ("P1417", "Encyclopædia Britannica"),
]


def api(**p):
    args = ["curl", "-s", "--get", "https://www.wikidata.org/w/api.php",
            "-A", "BibliotecaVisual/1.0 (https://github.com/sebastiancordoba/biblioteca-visual)"]
    for k, v in dict(format="json", **p).items():
        args += ["--data-urlencode", f"{k}={v}"]
    for intento in range(4):
        txt = subprocess.run(args, capture_output=True, text=True).stdout
        try:
            return json.loads(txt)
        except ValueError:
            print("  Wikidata no devolvió JSON (¿límite de tasa?); espero 60 s", flush=True)
            time.sleep(60)
    raise SystemExit("Wikidata no responde")


def fecha(snak_claim):
    """Texto en español con la precisión que da Wikidata."""
    try:
        v = snak_claim["mainsnak"]["datavalue"]["value"]
    except (KeyError, TypeError):
        return None
    m = re.match(r"([+-])(\d+)-(\d\d)-(\d\d)", v["time"])
    signo, a, mes, dia = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    p = v.get("precision", 9)
    if p >= 11:
        t = f"{dia} de {MESES[mes - 1]} de {a}"
    elif p == 10:
        t = f"{MESES[mes - 1]} de {a}"
    elif p == 9:
        t = str(a)
    elif p == 8:
        t = f"década de {a // 10 * 10}"
    elif p == 7:
        n = (a - 1) // 100 + 1
        t = f"siglo {romano(n)}"
    else:
        return None
    if signo == "-":
        t += " a.C."
    circa = any(q.get("datavalue", {}).get("value", {}).get("id") == CIRCA
                for q in snak_claim.get("qualifiers", {}).get("P1480", []))
    return ("c. " + t) if circa else t


def romano(n):
    r = ""
    for v, s in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                 (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            r += s; n -= v
    return r


def item(c):
    try:
        return c["mainsnak"]["datavalue"]["value"]["id"]
    except (KeyError, TypeError):
        return None


def texto(c):
    try:
        return c["mainsnak"]["datavalue"]["value"]
    except (KeyError, TypeError):
        return None


def preferidos(lista):
    """Las declaraciones con rango preferido si las hay; si no, las normales. Las
    desaprobadas nunca."""
    pref = [c for c in lista if c.get("rank") == "preferred"]
    return pref or [c for c in lista if c.get("rank") != "deprecated"]


def main():
    claves = [a["clave"] for a in AUTORES if a["clave"] in ARTICULOS]
    ents = {}
    for i in range(0, len(claves), 20):
        grupo = claves[i:i + 20]
        d = api(action="wbgetentities", sites="enwiki", props="claims|sitelinks|labels",
                languages="es|en", titles="|".join(ARTICULOS[c] for c in grupo))
        por_titulo = {e.get("sitelinks", {}).get("enwiki", {}).get("title"): e
                      for e in d.get("entities", {}).values() if "id" in e}
        for c in grupo:
            e = por_titulo.get(ARTICULOS[c])
            if e: ents[c] = e
            else: print(f"  sin entidad: {c} ({ARTICULOS[c]})")
        time.sleep(4)

    # formato de URL de cada obra de referencia
    d = api(action="wbgetentities", ids="|".join(p for p, _ in REFERENCIAS), props="claims")
    FORMATO = {}
    for pid, e in d["entities"].items():
        f = [texto(c) for c in preferidos(e.get("claims", {}).get("P1630", [])) if texto(c)]
        if f: FORMATO[pid] = f[0]
    time.sleep(4)

    # etiquetas en español de lugares, movimientos y ocupaciones
    refs = set()
    for e in ents.values():
        cl = e.get("claims", {})
        for pid in ("P19", "P20", "P135", "P106"):
            refs |= {item(c) for c in preferidos(cl.get(pid, [])) if item(c)}
    etiquetas = {}
    refs = sorted(refs)
    for i in range(0, len(refs), 50):
        d = api(action="wbgetentities", ids="|".join(refs[i:i + 50]), props="labels", languages="es|en")
        for q, e in d.get("entities", {}).items():
            lb = e.get("labels", {})
            etiquetas[q] = (lb.get("es") or lb.get("en") or {}).get("value", q)
        time.sleep(4)

    def lugar(cl, pid):
        q = next((item(c) for c in preferidos(cl.get(pid, [])) if item(c)), None)
        return {"texto": etiquetas.get(q, q), "qid": q} if q else None

    salida = {}
    for c, e in ents.items():
        cl = e.get("claims", {})
        sl = e.get("sitelinks", {})
        ids = {}
        for pid, k in (("P245", "ulan"), ("P214", "viaf"), ("P244", "loc")):
            v = next((texto(x) for x in preferidos(cl.get(pid, [])) if texto(x)), None)
            if v: ids[k] = v
        salida[c] = {
            "qid": e["id"],
            "etiqueta": (e.get("labels", {}).get("es") or e.get("labels", {}).get("en") or {}).get("value"),
            "nacimiento": {"fecha": next((fecha(x) for x in preferidos(cl.get("P569", [])) if fecha(x)), None),
                           "lugar": lugar(cl, "P19")},
            "muerte": {"fecha": next((fecha(x) for x in preferidos(cl.get("P570", [])) if fecha(x)), None),
                       "lugar": lugar(cl, "P20")},
            "movimientos": [{"texto": etiquetas.get(q, q), "qid": q}
                            for q in dict.fromkeys(item(x) for x in preferidos(cl.get("P135", [])) if item(x))][:4],
            "ocupaciones": [{"texto": etiquetas.get(q, q), "qid": q}
                            for q in dict.fromkeys(item(x) for x in preferidos(cl.get("P106", [])) if item(x))][:5],
            "ids": ids,
            "referencias": [
                {"obra": nombre, "url": FORMATO[pid].replace("$1", v), "pid": pid}
                for pid, nombre in REFERENCIAS if pid in FORMATO
                for v in [next((texto(x) for x in preferidos(cl.get(pid, [])) if texto(x)), None)] if v],
            "commons": next((texto(x) for x in cl.get("P373", []) if texto(x)), None),
            "eswiki": sl.get("eswiki", {}).get("title"),
            "enwiki": sl.get("enwiki", {}).get("title"),
        }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump({"consultado": datetime.date.today().isoformat(), "autores": salida},
              io.open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    sin = [a["clave"] for a in AUTORES if a["clave"] not in salida]
    print(f"{len(salida)} autores con datos de Wikidata · sin registro: {', '.join(sin) or 'ninguno'}")
    print(f"con ULAN: {sum(1 for v in salida.values() if 'ulan' in v['ids'])} · "
          f"con VIAF: {sum(1 for v in salida.values() if 'viaf' in v['ids'])} · "
          f"con artículo en español: {sum(1 for v in salida.values() if v['eswiki'])}")
    import collections
    cuenta = collections.Counter(r["obra"] for v in salida.values() for r in v["referencias"])
    print("obras de referencia:", " · ".join(f"{k.split(' (')[0]} {n}" for k, n in cuenta.most_common()))


if __name__ == "__main__":
    main()
