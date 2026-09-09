# -*- coding: utf-8 -*-
"""Mantiene datos/enlaces.json: la URL del archivo original de cada imagen.

El artefacto incrusta vistas previas, así que el botón «Original» del visor depende de
este fichero. Si una obra no está aquí, el botón se esconde y no hay forma de llegar al
archivo completo, que es justo lo que pasó con las primeras obras del Génesis.

Fuentes, por orden:
  1. los manifiestos herramientas/*.tsv, que ya dicen de qué archivo de Commons vino cada
     imagen — es la fuente fiable y no hay que adivinar nada;
  2. datos/titulos_extra.tsv, para las imágenes anteriores a los manifiestos, cuyo título
     de Commons se averiguó a mano y se comprobó comparando las dimensiones exactas.

Uso:  python3 herramientas/enlaces.py            (solo añade lo que falta)
      python3 herramientas/enlaces.py --revisar  (además dice qué sigue sin enlace)
"""
import glob, io, json, os, re, subprocess, sys, time, urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "herramientas", "artefacto", "datos")
ENLACES = os.path.join(DATOS, "enlaces.json")
EXTRA = os.path.join(DATOS, "titulos_extra.tsv")
os.chdir(RAIZ)

API = "https://commons.wikimedia.org/w/api.php"


def consulta(titulos):
    """imageinfo de hasta 50 títulos por llamada. curl porque el Python del sistema no
       tiene certificados CA y urllib falla con CERTIFICATE_VERIFY_FAILED."""
    args = ["curl", "-s", "--get", API,
            "--data-urlencode", "action=query", "--data-urlencode", "format=json",
            "--data-urlencode", "prop=imageinfo",
            "--data-urlencode", "iiprop=size|url",
            "--data-urlencode", "titles=" + "|".join(titulos)]
    salida = subprocess.run(args, capture_output=True, text=True).stdout
    try:
        d = json.loads(salida)
    except ValueError:
        print("  respuesta no válida (¿límite de tasa?); se reintenta en 60 s")
        time.sleep(60)
        return consulta(titulos)
    fuera = {}
    # normalized: la API corrige guiones bajos y mayúsculas; hay que deshacer el cambio
    alias = {n["to"]: n["from"] for n in d.get("query", {}).get("normalized", [])}
    for p in d.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii.get("url"):
            continue
        clave = alias.get(p["title"], p["title"])
        w, h = ii["width"], ii["height"]
        fuera[clave] = {
            "commons": ii.get("descriptionurl", ""),
            "original": ii["url"].split("?")[0],   # la API cuelga parámetros utm_*
            "w": w, "h": h, "mp": round(w * h / 1e6, 1),
        }
    return fuera


def titulos_conocidos():
    """destino en disco -> título en Commons, de los manifiestos y de los extras."""
    m = {}
    for p in sorted(glob.glob("herramientas/*.tsv")) + ([EXTRA] if os.path.exists(EXTRA) else []):
        for linea in io.open(p, encoding="utf-8"):
            if "\t" not in linea:
                continue
            partes = linea.rstrip("\n").split("\t")
            if len(partes) >= 2 and partes[1].startswith("File:"):
                m[partes[0]] = partes[1]
    return m


def referenciadas():
    """Las imágenes que la página usa de verdad, en el orden en que aparecen."""
    doc = io.open("index.html", encoding="utf-8").read()
    vistas = []
    for m in re.finditer(r'"src":\s*"\./((?:Génesis|Gilgamesh|Ilíada)/[^"]+\.jpg)"', doc):
        if m.group(1) not in vistas:
            vistas.append(m.group(1))
    return vistas


def main():
    enl = json.load(io.open(ENLACES, encoding="utf-8"))
    conocidos = titulos_conocidos()
    usadas = referenciadas()

    pendientes = [r for r in usadas if r not in enl and r in conocidos]
    print(f"{len(usadas)} imágenes en la página · {len(enl)} ya con enlace · "
          f"{len(pendientes)} por resolver")

    nuevos = 0
    for i in range(0, len(pendientes), 40):
        lote = pendientes[i:i + 40]
        info = consulta([conocidos[r] for r in lote])
        for r in lote:
            dato = info.get(conocidos[r])
            if dato:
                enl[r] = dato; nuevos += 1
                print(f"  + {dato['mp']:5.1f} MP  {r.split('/')[-1]}")
            else:
                print(f"  ?         no resuelto: {conocidos[r]}")
        if i + 40 < len(pendientes):
            time.sleep(4)

    if nuevos:
        io.open(ENLACES, "w", encoding="utf-8").write(
            json.dumps(enl, ensure_ascii=False, indent=1, sort_keys=True))
    print(f"{nuevos} enlaces añadidos")

    sin = [r for r in usadas if r not in enl]
    if sin:
        print(f"\nSiguen sin enlace ({len(sin)}). Añade su título de Commons a "
              f"{os.path.relpath(EXTRA, RAIZ)} y vuelve a ejecutar:")
        for r in sin:
            print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
