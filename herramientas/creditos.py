# -*- coding: utf-8 -*-
"""Baja de Commons el autor y la licencia de cada imagen de la colección y los guarda en
herramientas/artefacto/datos/creditos.json, del que salen las líneas de crédito del visor
y de las páginas de obra.

Muchas imágenes son fotografías bajo CC BY-SA, que OBLIGA a citar al autor y la licencia:
un «cada una con su licencia en Commons» genérico en el pie no basta. Commons lo da en los
metadatos de cada archivo (extmetadata):
  Attribution         el texto con que el autor pide ser citado, si lo fija
  Artist              quién hizo la foto (o, en obras de dominio público, el pintor)
  LicenseShortName    la licencia, y LicenseUrl su texto
  AttributionRequired si la licencia exige atribución
En dominio público no se nombra a nadie como autor de la foto: el campo Artist es entonces
el autor de la obra, y ponerlo como fotógrafo sería falso.

Uso: python3 herramientas/creditos.py        (después de enlaces.py; vuelve a bajarlo todo)
"""
import html, io, json, os, re, subprocess, time, urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "herramientas", "artefacto", "datos")
ENL = json.load(io.open(os.path.join(DATOS, "enlaces.json"), encoding="utf-8"))


def texto(h):
    t = html.unescape(re.sub(r"<[^>]+>", " ", h or ""))
    return re.sub(r"\s+", " ", t).strip()


def primer_enlace(h):
    m = re.search(r'href="([^"]+)"', h or "")
    if not m: return None
    u = html.unescape(m.group(1))
    return ("https:" + u) if u.startswith("//") else u


def credito_fijo(titulo):
    """Crédito para archivos que exigen atribución y no la declaran en Commons. La Wellcome
       Collection sube con CC BY 4.0 y pide ser citada así, pero deja vacío el campo Artist."""
    if re.search(r"Wellcome [LMV]\d{7}", titulo): return "Wellcome Collection"
    return None


def main():
    # Un mismo archivo de Commons puede servir a varias imágenes de la colección —el Júpiter y
    # Tetis de Ingres está en la Ilíada y en Las lágrimas de Eros—, así que cada título lleva la
    # lista de sus imágenes. Con un diccionario de uno a uno, la Ilíada se quedaba sin crédito.
    titulo_de = {}
    for rel, lk in ENL.items():
        titulo_de.setdefault("File:" + urllib.parse.unquote(lk["original"].rsplit("/", 1)[1]).replace("_", " "), []).append(rel)
    ts, salida = sorted(titulo_de), {}
    for i in range(0, len(ts), 50):
        args = ["curl", "-s", "--get", "https://commons.wikimedia.org/w/api.php",
                "-A", "BibliotecaVisual/1.0 (https://github.com/sebastiancordoba/biblioteca-visual)"]
        for k, v in dict(action="query", format="json", prop="imageinfo", iiprop="extmetadata",
                         iiextmetadatafilter="Artist|Attribution|LicenseShortName|LicenseUrl|AttributionRequired|UsageTerms",
                         titles="|".join(ts[i:i + 50])).items():
            args += ["--data-urlencode", f"{k}={v}"]
        d = json.loads(subprocess.run(args, capture_output=True, text=True).stdout)
        norm = {n["to"]: n["from"] for n in d["query"].get("normalized", [])}
        for p in d["query"]["pages"].values():
            t = norm.get(p["title"], p["title"])
            em = {k: v.get("value") for k, v in p["imageinfo"][0].get("extmetadata", {}).items()}
            lic = texto(em.get("LicenseShortName")) or texto(em.get("UsageTerms"))
            dp = bool(re.search(r"public domain|dominio público|^PD|CC0", lic or "", re.I))
            for rel in titulo_de[t]:
              salida[rel] = {
                # «Attribution» es el texto con el que el autor pide que se le cite; si no
                # lo hay, el campo Artist.
                "autor": None if dp else ((texto(em.get("Attribution")) or texto(em.get("Artist")))[:90]
                                          or credito_fijo(t)),
                "autor_url": None if dp else primer_enlace(em.get("Artist")),
                "licencia": "Dominio público" if dp and not re.search("CC0", lic or "") else lic,
                "licencia_url": em.get("LicenseUrl"),
                "atribucion": str(em.get("AttributionRequired")).lower() == "true",
                "archivo": ENL[rel]["commons"],
            }
        time.sleep(3)
    json.dump(salida, io.open(os.path.join(DATOS, "creditos.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    import collections
    c = collections.Counter(v["licencia"] for v in salida.values())
    print(f"{len(salida)} imágenes · exigen atribución: {sum(v['atribucion'] for v in salida.values())}")
    print("licencias:", " · ".join(f"{k} {n}" for k, n in c.most_common()))
    sin = [r for r, v in salida.items() if v["atribucion"] and not v["autor"]]
    if sin: print("EXIGEN ATRIBUCIÓN Y NO CONSTA AUTOR:", *sin, sep="\n   ")


if __name__ == "__main__":
    main()
