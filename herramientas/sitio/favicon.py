# -*- coding: utf-8 -*-
"""El icono de la pestaña del navegador: una «B» dorada en Cormorant Garamond, la tipografía
de los títulos, sobre el negro del sitio.

No es un recorte de una obra, a diferencia del icono de la aplicación (las manos de la
Creación de Adán, icono-192/512): se probó y a 16 px las manos son una franja clara que se
pierde en la barra de pestañas. Una letra sí se lee a ese tamaño.

Escribe herramientas/sitio/favicon.ico (16, 32 y 48 px), que va en el repositorio para que
construir no dependa de la red; construir_sitio.py lo copia a la raíz del sitio. Solo hace
falta volver a ejecutarlo si cambia el diseño. La fuente (licencia OFL) se descarga una vez
a ~/Library/Caches/biblioteca-visual/.

Uso: python3 herramientas/sitio/favicon.py
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.expanduser("~/Library/Caches/biblioteca-visual")
FUENTE = os.path.join(CACHE, "CormorantGaramond.ttf")
URL = "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf"
FONDO, ORO = (9, 10, 13, 255), (197, 160, 70, 255)     # --bg-body y --accent-gold


def dibujar(n=512):
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, n - 1, n - 1), radius=int(n * 0.18), fill=FONDO)
    f = ImageFont.truetype(FUENTE, int(n * 0.86))
    f.set_variation_by_name("Bold")          # a 16 px el trazo fino se deshace
    x0, y0, x1, y1 = d.textbbox((0, 0), "B", font=f)
    d.text(((n - (x1 - x0)) / 2 - x0, (n - (y1 - y0)) / 2 - y0), "B", font=f, fill=ORO)
    return im


if __name__ == "__main__":
    if not os.path.exists(FUENTE):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(["curl", "-sfL", "-o", FUENTE, URL], check=True)   # urllib: sin certificados
    destino = os.path.join(AQUI, "favicon.ico")
    dibujar().save(destino, sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"favicon: {destino}")
