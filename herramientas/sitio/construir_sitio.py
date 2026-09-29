# -*- coding: utf-8 -*-
"""Construye la versión de GitHub Pages en build/sitio/.

Sale del mismo punto que el artefacto de claude.ai —build/pre_imagenes.html, que deja
build4.py justo antes de incrustar las imágenes— y solo cambia lo que en Pages sí se puede
hacer y en un artefacto no:

  · Las imágenes se piden a Wikimedia Commons en vez de ir incrustadas: miniatura de
    1280 px para cuadrículas, mapa y portada; 1920 px al abrir el visor; y el ORIGINAL
    completo en cuanto se acerca el zoom. Así el zoom a 40× vuelve a enseñar la
    resolución máxima, que es la regla de la colección.
  · Lo que no está en Commons va como archivo propio del sitio: los retratos de autor
    (ya son de 640 px) y las imágenes antiguas del Génesis cuyo origen no consta, en
    copia reducida a 2560 px. La colección en disco no se toca.
  · Cada sección tiene su dirección (#/genesis, #/mapa, #/biblioteca/autores) y el botón
    «atrás» del navegador funciona.

Uso: ./herramientas/construir_artefacto.sh && python3 herramientas/sitio/construir_sitio.py
"""
import io, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import RAIZ, BUILD, SITIO, ENL, REJILLA, VISOR, miniatura, propia, es_tiff
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
from libros import PATRON_RUTA_COMILLAS

TITULO = "Biblioteca Visual"

doc = io.open(os.path.join(BUILD, "pre_imagenes.html"), encoding="utf-8").read()
if os.path.isdir(SITIO):
    shutil.rmtree(SITIO)
os.makedirs(os.path.join(SITIO, "img"))


# ---------- rutas de imagen ----------
HD, propias, cuenta = {}, set(), {"commons": 0, "propia": 0, "retrato": 0}

def sustituir(m):
    rel = m.group(1)
    lk = ENL.get(rel)
    if lk:
        url = miniatura(lk, REJILLA)
        # Los originales gigantes (más de 150 MP: el Sueño de Jacob, la Torre de Babel, el
        # Jardín de las delicias…) pesan de 65 a 240 MB; el visor se quedaba en «HD…» minutos o
        # no llegaba a abrirlos. Para ellos el zoom usa la versión de 3840 px, que es el mayor
        # tamaño estándar que sirve Commons (8000 o 2560 dan error 400). El original entero
        # sigue a un clic con el botón «Original».
        HD[url] = {"v": miniatura(lk, VISOR),
                   "o": lk["original"] if lk["mp"] <= 150 and not es_tiff(lk) else miniatura(lk, 3840)}
        cuenta["commons"] += 1
        return f'"{url}"'
    cuenta["retrato" if rel.startswith("Autores/") else "propia"] += 1
    destino = propia(rel)
    propias.add(destino)
    return f'"{destino}"'

doc, n = re.subn(PATRON_RUTA_COMILLAS, sustituir, doc)
assert n > 100, f"solo {n} rutas de imagen: ¿cambió el patrón?"

# ---------- páginas estáticas (fase 2) ----------
from paginas import generar as generar_paginas
FICHAS = generar_paginas()

# ---------- enlaces a las páginas de autor: relativos dentro del propio sitio ----------
_b = "    const BASE_FICHAS = 'https://sebastiancordoba.github.io/biblioteca-visual/';"
assert doc.count(_b) == 1, "no encuentro BASE_FICHAS"
doc = doc.replace(_b, "    const BASE_FICHAS = '';", 1)
# ---------- y a la de cada obra: los títulos se vuelven enlaces ----------
_f = "    const FICHAS = null;"
assert doc.count(_f) == 1, "no encuentro FICHAS"
doc = doc.replace(_f, "    const FICHAS = %s;" % json.dumps(FICHAS, ensure_ascii=False), 1)

# ---------- nombre del sitio ----------
doc = re.sub(r"<title>[^<]*</title>", f"<title>{TITULO}</title>", doc, count=1)
doc = doc.replace("Los Tres Libros", "Biblioteca Visual")

# ---------- un documento completo ----------
# pre_imagenes.html es cabecera y cuerpo pegados, sin <!DOCTYPE>, <html>, <head> ni <body>:
# build.py quita el charset y el viewport porque el artefacto de claude.ai los pone por su
# cuenta. Publicado tal cual en Pages, el navegador entraba en modo quirks y, sin viewport,
# un teléfono maquetaba la página a 980 px de ancho y la encogía hasta hacerla ilegible:
# nada de lo pensado para pantalla estrecha llegaba a aplicarse. Aquí se reconstruye.
corte = doc.find("\n  <header>")
assert corte > 0 and doc.count("\n  <header>") == 1, "no encuentro dónde empieza el cuerpo"
cabeza, cuerpo = doc[:corte], doc[corte:]
assert "<body" not in cabeza and "<html" not in doc, "pre_imagenes.html ya trae un documento completo"
doc = ("<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n"
       '  <meta charset="UTF-8">\n'
       '  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">\n'
       '  <meta name="description" content="Pintura, escultura, cerámica y arqueología en torno al Génesis, '
       'Gilgamesh, la Ilíada, el Atrahasis y el Enuma Elish, en la mayor resolución que existe de cada obra.">\n'
       '  <link rel="manifest" href="manifest.webmanifest">\n'
       '  <link rel="icon" href="favicon.ico" sizes="16x16 32x32 48x48">\n'
       '  <link rel="icon" type="image/png" sizes="192x192" href="icono-192.png">\n'
       '  <link rel="apple-touch-icon" href="icono-180.png">\n'
       + cabeza.strip("\n") + "\n</head>\n<body>" + cuerpo.rstrip() + "\n</body>\n</html>\n")

# ---------- visor: enlace a la página de la obra ----------
m = re.search(r'(<a id="panelWikiLink"[\s\S]*?</a>)', doc)
assert m, "no encuentro el enlace a Wikipedia del panel del visor"
doc = doc.replace(m.group(1), m.group(1) + """
        <a id="panelFichaLink" href="#" class="wiki-link-btn" title="Página propia de esta obra, para leerla o compartirla">
          Ficha de la obra</a>""", 1)

# ---------- visor: 1920 px al abrir, original al acercar ----------
abrir = "openZoomModal(item.src, item.title);"
assert doc.count(abrir) == 1, "no encuentro la llamada del visor"
doc = doc.replace(abrir, "openZoomModal((HD[item.src] || {}).v || item.src, item.title);\n"
                         "      prepararOriginal(item.src);", 1)

aviso = "      zoomScaleText.classList.toggle('sobre-previa', zoomScale > 3);"
assert doc.count(aviso) == 1, "no encuentro el aviso de previa del artefacto"
doc = doc.replace(aviso, "      if (zoomScale > 1.4) pedirOriginal();", 1)

JS = """
    /* ══════════ Solo en GitHub Pages: imágenes de Commons a resolución completa ══════════
       El visor abre con la versión de 1920 px y, en cuanto se acerca el zoom, pide el
       archivo original. No se pide antes: algunos pesan decenas de megas. */
    const HD = %s;
    let hdBase = null, hdPedido = false;
    function prepararOriginal(src) {
      hdBase = src; hdPedido = false;
      zoomScaleText.classList.remove('hd-cargando', 'hd-listo');
    }
    function pedirOriginal() {
      const e = HD[hdBase];
      if (!e || hdPedido) return;
      hdPedido = true;
      const base = hdBase;
      zoomScaleText.classList.add('hd-cargando');
      const img = new Image();
      img.onload = () => {
        if (hdBase !== base) return;          // ya se cambió de obra
        zoomTargetImg.src = e.o;
        zoomScaleText.classList.replace('hd-cargando', 'hd-listo');
      };
      img.onerror = () => zoomScaleText.classList.remove('hd-cargando');
      img.src = e.o;
    }

    /* ══════════ Solo en GitHub Pages: la página de cada obra ══════════
       FICHAS (arriba, junto a BASE_FICHAS) da la dirección de su página estática. Se busca
       por la imagen con urlObra: con FICHAS[currentBook] el botón desaparecía al abrir la
       obra desde la portada, la cronología o el mapa, que numeran a su manera. */
    (function () {
      const actualizar = updateModalImageAndArrows;
      updateModalImageAndArrows = function () {
        actualizar();
        const a = document.getElementById('panelFichaLink');
        const r = urlObra(bookGroups()[currentArtworkGroupIndex][0].src);
        if (a) { a.hidden = !r; if (r) a.href = r; }
      };
    })();

    /* ══════════ Solo en GitHub Pages: una dirección por sección ══════════
       #/genesis, #/mapa, #/biblioteca/autores… Se envuelven switchBook y switchTab, así
       que cualquier forma de cambiar de sección deja la dirección al día, y el botón
       «atrás» del navegador vuelve a la anterior. */
    (function () {
      const irLibro = switchBook, irPestana = switchTab;
      let restaurando = false;
      const escribir = () => {
        if (restaurando) return;
        const act = document.querySelector('.tab-content.active');
        const tab = act && /-gallery$/.test(act.id) && act.id !== ((BOOKS[currentBook] || {}).firstTab)
          ? act.id.replace(/-gallery$/, '') : '';
        const ruta = '#/' + currentBook + (tab ? '/' + tab : '');
        if (location.hash !== ruta) history.pushState(null, '', ruta);
      };
      switchBook = function (id, btn) { irLibro(id, btn); escribir(); };
      switchTab = function (id, btn) { irPestana(id, btn); escribir(); };
      const leer = () => {
        const [libro, tab, n, v] = location.hash.replace(/^#\\/?/, '').split('/');
        if (!libro || !BOOKS[libro]) return;
        restaurando = true;
        try {
          /* #/genesis/mapa/12: «Ver en el mapa» desde la página de una obra. Se abre el mapa,
             no el libro, y la dirección se sustituye por #/mapa (sin sumar un paso al «atrás»). */
          if (tab === 'mapa') {
            const g = BOOKS[libro].groups[+n];
            if (g && window.verObraEnMapa) {
              irLibro('mapa');
              history.replaceState(null, '', '#/mapa');
              window.verObraEnMapa(g[0].src);
              return;
            }
          }
          if (libro !== currentBook) irLibro(libro);
          /* #/genesis/obra/12[/1]: lo que abre «Abrir en el visor» desde la página de una obra. */
          if (tab === 'obra') {
            const g = +n, i = +(v || 0);
            if (BOOKS[libro].groups[g]) openZoomForArtwork(g, BOOKS[libro].groups[g][i] ? i : 0);
          } else if (tab) {
            const b = document.querySelector(`[onclick*="switchTab('${tab}-gallery'"]`);
            irPestana(tab + '-gallery', b || undefined);
          }
        } finally { restaurando = false; }
      };
      window.addEventListener('popstate', leer);
      leer();
    })();
""" % json.dumps(HD, ensure_ascii=False)
cierre = "  </script>"   # la página tiene un solo <script>, y termina en él
assert doc.count(cierre) == 1, "no encuentro el cierre del script principal"
doc = doc.replace(cierre, JS + cierre, 1)

CSS = """
    /* Solo en GitHub Pages: estado del original en el visor. */
    #zoomScaleText.hd-cargando::after{content:' · HD…';opacity:.6;animation:hdlat 1.2s infinite}
    #zoomScaleText.hd-listo::after{content:' · HD';color:var(--accent-gold)}
    @keyframes hdlat{50%{opacity:.25}}
  </style>"""
doc = doc.replace("  </style>", CSS, 1)

io.open(os.path.join(SITIO, "index.html"), "w", encoding="utf-8").write(doc)
io.open(os.path.join(SITIO, ".nojekyll"), "w").write("")
# el icono de la pestaña del navegador (lo dibuja favicon.py)
shutil.copyfile(os.path.join(os.path.dirname(os.path.abspath(__file__)), "favicon.ico"), os.path.join(SITIO, "favicon.ico"))

# ---------- aplicación instalable ----------
# Con el manifiesto, «Añadir a pantalla de inicio» deja un icono que abre el sitio a
# pantalla completa, sin la barra del navegador, como una aplicación. El icono son las
# manos de la Creación de Adán, recortadas de la copia local de 10080 px: es ilustración
# de interfaz, como los retratos de autor, no una pieza de la colección, y la copia de la
# colección no se toca. Sin esa copia en disco el sitio se construye igual, sin icono.
json.dump({
    "name": TITULO, "short_name": "Biblioteca", "lang": "es",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#07080a", "theme_color": "#07080a",
    "icons": [{"src": f"icono-{n}.png", "sizes": f"{n}x{n}", "type": "image/png", "purpose": "any"}
              for n in (192, 512)],
}, io.open(os.path.join(SITIO, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
FRESCO = os.path.join(RAIZ, "Génesis", "01_La_Creacion_de_Adan_Miguel_Angel_1512.jpg")
try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    with Image.open(FRESCO) as im:
        w, h = im.size
        # las manos, en proporción del fresco: así vale aunque cambie la resolución del archivo
        cx, cy, lado = round(w * 0.4665), round(h * 0.4700), round(w * 0.125)
        manos = im.convert("RGB").crop((cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2))
        for n in (180, 192, 512):
            manos.resize((n, n), Image.LANCZOS).save(os.path.join(SITIO, f"icono-{n}.png"), optimize=True)
    print("iconos de la aplicación: 180, 192 y 512 px")
except Exception as e:     # sin Pillow o sin la copia local: el sitio sigue funcionando
    print(f"AVISO: sin iconos de la aplicación ({e})")

peso = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(SITIO) for f in fs) / 1e6
print(f"rutas: {cuenta['commons']} a Commons · {cuenta['retrato']} retratos · {cuenta['propia']} copias propias")
print(f"imágenes con original en Commons: {len(HD)} · archivos propios: {len(propias)}")
print(f"sitio: {peso:.1f} MB en {SITIO}")
