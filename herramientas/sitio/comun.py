# -*- coding: utf-8 -*-
"""Lo que comparten la aplicación de GitHub Pages (construir_sitio.py) y las páginas
estáticas (paginas.py): de dónde sale cada imagen y a qué tamaño.

Las dos piden las MISMAS miniaturas de Commons (1280 px en cuadrículas, 1920 px en grande),
así que lo que el navegador ya descargó en una sirve en la otra."""
import io, json, os, shutil, subprocess, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.path.join(RAIZ, "build")
SITIO = os.path.join(BUILD, "sitio")
URL_SITIO = "https://sebastiancordoba.github.io/biblioteca-visual/"
ENL = json.load(io.open(os.path.join(RAIZ, "herramientas", "artefacto", "datos", "enlaces.json"),
                        encoding="utf-8"))
REJILLA, VISOR, LADO_PROPIO = 1280, 1920, 2560


def miniatura(lk, ancho):
    """URL de la miniatura de Commons a `ancho` px, o el original si no es más grande.
    Commons da error si se pide una miniatura mayor que el archivo."""
    if lk["w"] <= ancho:
        return lk["original"]
    base, nombre = lk["original"].rsplit("/", 1)
    # thumb/5/5b/<nombre>/1280px-<nombre>: el nombre va dos veces.
    return (base.replace("/wikipedia/commons/", "/wikipedia/commons/thumb/", 1)
            + f"/{nombre}/{ancho}px-{nombre}")


def ascii_(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()


def propia(rel):
    """Imagen que no está en Commons: se sirve como archivo del sitio. Devuelve su ruta
    relativa a la raíz del sitio y la crea si falta. Los retratos se copian tal cual (ya
    son de 640 px); las obras, en copia reducida: la colección en disco no se toca."""
    rel = rel[2:] if rel.startswith("./") else rel
    # Los retratos van a retratos/, NO a Autores/: en el Mac «Autores» y «autores» (las
    # páginas de autor) son la misma carpeta, git lo subió todo como Autores/ y en GitHub,
    # que distingue mayúsculas, /autores/behzad/ daba 404.
    destino = ("retratos/" + rel.split("/", 1)[1]) if rel.startswith("Autores/") \
        else "img/" + ascii_(rel.replace("/", "__"))
    dst = os.path.join(SITIO, destino)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel.startswith("Autores/"):
            shutil.copyfile(os.path.join(RAIZ, rel), dst)
        else:
            subprocess.run(["sips", "-Z", str(LADO_PROPIO), "-s", "format", "jpeg",
                            "-s", "formatOptions", "85", os.path.join(RAIZ, rel), "--out", dst],
                           check=True, capture_output=True)
    return destino


def imagen(rel, ancho=REJILLA):
    """(url, es_propia). La url es absoluta si viene de Commons y relativa a la raíz del
    sitio si es un archivo propio."""
    rel = rel[2:] if rel.startswith("./") else rel
    lk = ENL.get(rel)
    if lk:
        return miniatura(lk, ancho), False
    return propia(rel), True
