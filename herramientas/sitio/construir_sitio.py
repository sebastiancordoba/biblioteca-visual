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
import io, json, os, re, shutil, subprocess, sys, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
from libros import PATRON_RUTA_COMILLAS

BUILD = os.path.join(RAIZ, "build")
SITIO = os.path.join(BUILD, "sitio")
ENL = json.load(io.open(os.path.join(RAIZ, "herramientas", "artefacto", "datos", "enlaces.json"),
                        encoding="utf-8"))
REJILLA, VISOR, LADO_PROPIO = 1280, 1920, 2560
TITULO = "Biblioteca Visual de los Grandes Libros"

doc = io.open(os.path.join(BUILD, "pre_imagenes.html"), encoding="utf-8").read()
if os.path.isdir(SITIO):
    shutil.rmtree(SITIO)
os.makedirs(os.path.join(SITIO, "img"))


def miniatura(lk, ancho):
    """URL de la miniatura de Commons a `ancho` px, o el original si no es más grande.
    Commons da error si se pide una miniatura mayor que el archivo."""
    if lk["w"] <= ancho:
        return lk["original"]
    base, nombre = lk["original"].rsplit("/", 1)
    # thumb/5/5b/<nombre>/1280px-<nombre>: el nombre va dos veces.
    return (base.replace("/wikipedia/commons/", "/wikipedia/commons/thumb/", 1)
            + f"/{nombre}/{ancho}px-{nombre}")


# ---------- rutas de imagen ----------
HD, propias, cuenta = {}, [], {"commons": 0, "propia": 0, "retrato": 0}

def sustituir(m):
    rel = m.group(1)
    lk = ENL.get(rel)
    if lk:
        url = miniatura(lk, REJILLA)
        HD[url] = {"v": miniatura(lk, VISOR), "o": lk["original"]}
        cuenta["commons"] += 1
        return f'"{url}"'
    if rel.startswith("Autores/"):
        destino = rel
        cuenta["retrato"] += 1
    else:
        destino = "img/" + unicodedata.normalize("NFD", rel.replace("/", "__")).encode("ascii", "ignore").decode()
        cuenta["propia"] += 1
    if destino not in propias:
        propias.append(destino)
        dst = os.path.join(SITIO, destino)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if rel.startswith("Autores/"):
            shutil.copyfile(os.path.join(RAIZ, rel), dst)
        else:
            # Copia reducida para el sitio: la imagen de la colección no se modifica.
            subprocess.run(["sips", "-Z", str(LADO_PROPIO), "-s", "format", "jpeg",
                            "-s", "formatOptions", "85", os.path.join(RAIZ, rel), "--out", dst],
                           check=True, capture_output=True)
    return f'"{destino}"'

doc, n = re.subn(PATRON_RUTA_COMILLAS, sustituir, doc)
assert n > 100, f"solo {n} rutas de imagen: ¿cambió el patrón?"

# ---------- nombre del sitio ----------
doc = re.sub(r"<title>[^<]*</title>", f"<title>{TITULO}</title>", doc, count=1)
doc = doc.replace("Los Tres Libros", "Biblioteca Visual")
doc = doc.replace("<head>", """<head>
  <meta name="description" content="Pintura, escultura, cerámica y arqueología en torno al Génesis, Gilgamesh, la Ilíada, el Atrahasis y el Enuma Elish, en la mayor resolución que existe de cada obra.">""", 1)

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
        const [libro, tab] = location.hash.replace(/^#\\/?/, '').split('/');
        if (!libro || !BOOKS[libro]) return;
        restaurando = true;
        try {
          if (libro !== currentBook) irLibro(libro);
          if (tab) {
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

peso = sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(SITIO) for f in fs) / 1e6
print(f"rutas: {cuenta['commons']} a Commons · {cuenta['retrato']} retratos · {cuenta['propia']} copias propias")
print(f"imágenes con original en Commons: {len(HD)} · archivos propios: {len(propias)}")
print(f"sitio: {peso:.1f} MB en {SITIO}")
