# -*- coding: utf-8 -*-
"""El icono de la pestaña del navegador: el Ángel músico de Rosso Fiorentino (c. 1521,
Galleria degli Uffizi), recortado a la cabeza y las dos alas.

De la obra se toma la reproducción de la Web Gallery of Art en Commons
(File:Rosso Fiorentino - Musician Angel - WGA20116.jpg, 1196 × 1000, dominio público). Había
una foto de sala mayor, pero con licencia CC BY-SA, que obligaría a citar al fotógrafo hasta
en el icono; y para 48 px la resolución sobra.

El recorte se eligió probándolo a 16, 32 y 48 px sobre barras claras y oscuras: la cabeza
sola se deshace en una mancha parda; con las alas rojas a los lados la silueta se sigue
leyendo. Es ilustración de interfaz, como los retratos de autor, así que aquí sí se
reescala y se le sube un poco la nitidez; la colección no se toca.

Escribe herramientas/sitio/favicon.ico (16, 32 y 48 px), que va en el repositorio para que
construir no dependa de la red; construir_sitio.py lo copia a la raíz del sitio. La imagen
se descarga una vez a ~/Library/Caches/biblioteca-visual/.

Uso: python3 herramientas/sitio/favicon.py
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.expanduser("~/Library/Caches/biblioteca-visual")
OBRA = os.path.join(CACHE, "angel_rosso.jpg")
URL = "https://upload.wikimedia.org/wikipedia/commons/3/39/Rosso_Fiorentino_-_Musician_Angel_-_WGA20116.jpg"
CENTRO, LADO = (600, 420), 760          # cabeza y alas, en píxeles del original de 1196 × 1000


def dibujar(n=256):
    im = Image.open(OBRA).convert("RGB")
    assert im.size == (1196, 1000), f"no es el archivo esperado: {im.size}"
    cx, cy = CENTRO
    c = im.crop((cx - LADO // 2, cy - LADO // 2, cx + LADO // 2, cy + LADO // 2))
    c = c.resize((n, n), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    mascara = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, n - 1, n - 1), radius=int(n * 0.14), fill=255)
    c.putalpha(mascara)
    return c


if __name__ == "__main__":
    if not os.path.exists(OBRA):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(["curl", "-sfL", "-o", OBRA, URL], check=True)   # urllib: sin certificados
    destino = os.path.join(AQUI, "favicon.ico")
    dibujar().save(destino, sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"favicon: {destino}")
