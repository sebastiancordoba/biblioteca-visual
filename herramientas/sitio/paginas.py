# -*- coding: utf-8 -*-
"""Páginas estáticas del sitio de GitHub Pages (fase 2).

La aplicación (index.html) sigue siendo la que hace lo interactivo —el visor a 40×, el
mapa, la cronología, el buscador—. Estas páginas son HTML plano, una por cosa que merece
dirección propia:

    libros/                     índice de libros
    libros/<libro>/             la colección de un libro
    obras/<libro>/<nn-titulo>/  una obra: imágenes, los tres textos, sede, enlaces
    autores/                    índice de autores
    autores/<clave>/            un autor: retrato, biografía y sus obras
    mapa/ cronologia/ cobertura/  entradas con dirección limpia a esas vistas de la app

Se cargan rápido, se leen sin JavaScript, las encuentra un buscador (sitemap.xml) y al
compartirlas muestran la imagen de la obra (Open Graph). Cada una enlaza con la vista
correspondiente de la aplicación, y la aplicación enlaza de vuelta desde el visor.

Los datos salen de la propia aplicación (extraer_datos.js), no de las fichas en crudo:
así los índices de obra son exactamente los del visor y el enlace «Abrir en el visor»
abre la obra que tiene que abrir.
"""
import ast, html, io, json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from comun import RAIZ, BUILD, SITIO, URL_SITIO, ENL, REJILLA, VISOR, imagen, ascii_
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
sys.path.insert(0, os.path.join(RAIZ, "herramientas", "artefacto"))
import mapa as _mapa          # museo_de(): la sede de cada obra, la misma que usa el mapa

NOMBRE = "Biblioteca Visual"
e = lambda s: html.escape(str(s or ""), quote=True)


def slug(s, largo=60):
    s = re.sub(r"[^a-z0-9]+", "-", ascii_(s).lower()).strip("-")
    return s[:largo].rsplit("-", 1)[0] if len(s) > largo else s


def intros():
    """Las introducciones de readme.py, leídas sin importarlo (importarlo escribe los README)."""
    arbol = ast.parse(io.open(os.path.join(RAIZ, "herramientas", "readme.py"), encoding="utf-8").read())
    for n in arbol.body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "INTRO":
            return ast.literal_eval(n.value)
    return {}


# ---------------------------------------------------------------- plantilla
def pagina(ruta, titulo, descripcion, cuerpo, imagen_og=None, datos_ld=None, seccion=""):
    """`ruta` es el directorio de la página relativo a la raíz ('' para la raíz)."""
    prof = len([p for p in ruta.split("/") if p])
    R = "../" * prof or "./"
    canon = URL_SITIO + (ruta + "/" if ruta else "")
    nav = [("Inicio", R, "inicio"), ("Libros", R + "libros/", "libros"),
           ("Autores", R + "autores/", "autores"), ("Temas", R + "temas/", "temas"),
           ("Cronología", R + "#/cronologia", "cronologia"),
           ("Mapa", R + "#/mapa", "mapa")]
    og = [f'<meta property="og:title" content="{e(titulo)}">',
          f'<meta property="og:description" content="{e(descripcion)}">',
          f'<meta property="og:url" content="{e(canon)}">',
          '<meta property="og:type" content="website">',
          f'<meta property="og:site_name" content="{NOMBRE}">',
          '<meta property="og:locale" content="es_ES">']
    if imagen_og:
        og += [f'<meta property="og:image" content="{e(imagen_og)}">',
               '<meta name="twitter:card" content="summary_large_image">']
    ld = (f'<script type="application/ld+json">{json.dumps(datos_ld, ensure_ascii=False)}</script>'
          if datos_ld else "")
    doc = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} · {NOMBRE}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="canonical" href="{e(canon)}">
{chr(10).join(og)}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Source+Serif+4:ital,opsz,wght@0,8..60,300..600;1,8..60,300..600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}estilo.css">
<meta name="theme-color" content="#07080a">
<link rel="manifest" href="{R}manifest.webmanifest">
<link rel="apple-touch-icon" href="{R}icono-180.png">
{ld}
</head>
<body>
<header class="cab">
  <a class="marca" href="{R}">{NOMBRE}</a>
  <nav>{"".join(f'<a href="{h}"{" aria-current=page" if k == seccion else ""}>{t}</a>' for t, h, k in nav)}</nav>
</header>
<main>
{cuerpo}
</main>
<footer class="pie">
  <p>Imágenes de <a href="https://commons.wikimedia.org/">Wikimedia Commons</a>, cada una con su licencia en la página de su archivo.
  Análisis y fichas: <a href="https://github.com/sebastiancordoba/biblioteca-visual">biblioteca-visual</a>.</p>
</footer>
</body>
</html>
"""
    dst = os.path.join(SITIO, ruta, "index.html")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    io.open(dst, "w", encoding="utf-8").write(doc)
    return canon


def src(rel, R, ancho=REJILLA):
    url, es_propia = imagen(rel, ancho)
    return (R + url) if es_propia else url


def absoluta(rel, ancho=REJILLA):
    url, es_propia = imagen(rel, ancho)
    return (URL_SITIO + url) if es_propia else url


def con_notas(texto_):
    """Escapa el texto y convierte [1], [2, 3] en llamadas a las notas."""
    return re.sub(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]",
                  lambda m: "".join(f'<sup><a href="#f{n}">{n}</a></sup>' for n in re.findall(r"\d+", m.group(1))),
                  e(texto_))


def dominio(url):
    return re.sub(r"^https?://(www\.)?", "", url).split("/")[0]


def sin_notas(t):
    return re.sub(r"\s*\[[\d,\s–-]+\]", "", t)


def lista_fuentes(fuentes, titulo="Fuentes"):
    if not fuentes: return ""
    return (f'<section class="bloque"><h2>{e(titulo)}</h2><ol class="fuentes">'
            + "".join(f'<li id="f{f["n"]}" value="{f["n"]}"><span>{e(f["obra"])}</span>'
                      f'{(" — «" + e(f["titulo"]) + "»") if f.get("titulo") else ""}'
                      f'{(", " + e(f["autor"])) if f.get("autor") else ""}. '
                      f'<a href="{e(f["url"])}">{e(dominio(f["url"]))}</a></li>'
                      for f in sorted(fuentes, key=lambda x: x["n"]))
            + '</ol></section>')


def credito(c):
    """Autor y licencia de la foto: CC BY y CC BY-SA obligan a darlos. En dominio público no
    se nombra fotógrafo (el campo de Commons sería el autor de la obra)."""
    if not c: return ""
    enl = lambda u, t: f'<a href="{e(u)}">{e(t)}</a>' if u else e(t)
    partes = []
    if c.get("a"):
        pre = "" if re.match(r"(?i)(photo|foto|photograph)", c["a"]) else "Foto: "
        partes.append(pre + enl(c.get("au"), c["a"]))
    partes.append(enl(c.get("lu"), c.get("l") or ""))
    partes.append(enl(c.get("f"), "Wikimedia Commons"))
    return f'<span class="credito">{" · ".join(p for p in partes if p)}</span>'


def tarjeta(href, img, antetitulo, titulo, sub, R, texto=""):
    return (f'<a class="tarjeta" href="{e(href)}">'
            f'<span class="tarjeta-img"><img src="{e(img)}" alt="" loading="lazy" decoding="async"></span>'
            f'<span class="tarjeta-txt"><small>{e(antetitulo)}</small><strong>{e(titulo)}</strong>'
            f'<em>{e(sub)}</em>{f"<span>{e(texto)}</span>" if texto else ""}</span></a>')


# ---------------------------------------------------------------- generación
def generar():
    salida = subprocess.run(["node", os.path.join(AQUI, "extraer_datos.js"),
                             os.path.join(BUILD, "pre_imagenes.html")],
                            capture_output=True, text=True, check=True).stdout
    datos = json.loads(salida)
    libros, autores = datos["libros"], datos["autores"]
    INTRO = intros()
    urls = []

    # dirección de cada obra: libro -> [ruta por índice de grupo]
    FICHAS, POR_NUM, NUM_DE = {}, {}, {}
    _of = os.path.join(AQUI, "datos", "obras_fuentes.json")          # incorporar_obras.py
    OF = json.load(io.open(_of, encoding="utf-8")) if os.path.exists(_of) else {}
    for L in libros:
        rutas, usados = [], set()
        for g, d in enumerate(L["details"]):
            num = re.match(r"\d+", os.path.basename(L["groups"][g][0]["src"])).group(0)
            POR_NUM[(L["id"], num)] = g
            NUM_DE[(L["id"], g)] = num
            s = f"{num}-{slug(d['title'])}"
            while s in usados: s += "-b"
            usados.add(s)
            rutas.append(f"obras/{L['id']}/{s}")
        FICHAS[L["id"]] = rutas
    from temas import TEMAS
    TEMAS_DE = {}                      # (libro, i) -> [tema]
    for t in TEMAS:
        for lb, num in t["obras"]:
            assert (lb, num) in POR_NUM, f"el tema «{t['titulo']}» cita la obra {lb} {num}, que no existe"
            TEMAS_DE.setdefault((lb, POR_NUM[(lb, num)]), []).append(t)
    autor_de = {}                      # (libro, i) -> autor
    for a in autores:
        for o in a["obras"]:
            autor_de[(o["libro"], o["i"])] = a

    # ---- una página por obra
    for L in libros:
        n = len(L["details"])
        for g, d in enumerate(L["details"]):
            ruta = FICHAS[L["id"]][g]
            R = "../../../"
            vistas = L["groups"][g]
            principal = vistas[0]["src"]
            k = _mapa.museo_de(d)
            sede = _mapa.MUSEOS[k] if k else None
            a = autor_de.get((L["id"], g))
            app = f"{R}#/{L['id']}/obra/{g}"
            ant = FICHAS[L["id"]][g - 1] if g > 0 else None
            sig = FICHAS[L["id"]][g + 1] if g < n - 1 else None
            lk = ENL.get(principal[2:])
            otras = "".join(
                f'<figure><a href="{e(app)}/{v}"><img src="{e(src(x["src"], R))}" alt="{e(x["title"])}" loading="lazy"></a>'
                f'<figcaption>{e(x["title"])}{credito(x.get("cred"))}</figcaption></figure>' for v, x in enumerate(vistas) if v)
            enlaces = [f'<a class="boton oro" href="{e(app)}">Abrir en el visor · zoom 40×</a>']
            if lk:
                enlaces.append(f'<a class="boton" href="{e(lk["commons"])}" rel="noopener">Archivo original en Commons · '
                               f'{lk["w"]}×{lk["h"]} px</a>')
            if d.get("wikiUrl"):
                enlaces.append(f'<a class="boton" href="{e(d["wikiUrl"])}" rel="noopener">Wikipedia</a>')
            # a su sede en el mapa de la aplicación: #/<libro>/mapa/<n> vuela a ella
            mapa_url = f"{R}#/{L['id']}/mapa/{g}" if sede else None
            if mapa_url:
                enlaces.insert(1, f'<a class="boton" href="{e(mapa_url)}">Ver en el mapa</a>')
            h1, h2, h3 = L["headings"]
            of = OF.get(f"{L['id']}:{NUM_DE[(L['id'], g)]}")
            t1, t2, t3 = ((con_notas(of["analysis"]), con_notas(of["history"]), con_notas(of["bio"])) if of
                          else (e(d["analysis"]), e(d["history"]), e(d["bio"])))
            pie_fuentes = ((("".join(f'<p class="discrepancia">{e(x)}</p>' for x in of.get("discrepancias") or [])
                             and f'<section class="bloque"><h2>Discrepancias entre fuentes</h2>'
                                 f'{"".join(f"<p class=discrepancia>{e(x)}</p>" for x in of.get("discrepancias") or [])}</section>')
                            + lista_fuentes(of.get("fuentes"))) if of else
                           '<p class="discrepancia">Ficha pendiente de contrastar con fuentes académicas.</p>')
            cuerpo = f"""
<nav class="migas"><a href="{R}libros/">Libros</a> › <a href="{R}libros/{L['id']}/">{e(L['corto'])}</a> › Obra {g + 1:02d}</nav>
<article class="obra">
  <header class="obra-cab">
    <p class="ante">{e(L['corto'])} · Obra {g + 1:02d} de {n}</p>
    <h1>{e(d['title'])}</h1>
    <p class="autor">{f'<a href="{R}autores/{a["clave"]}/">{e(d["artist"])}</a>' if a else e(d['artist'])}</p>
    <p class="meta">{e(d['meta'])}</p>
  </header>
  <figure class="principal">
    <a href="{e(app)}" title="Abrir en el visor"><img src="{e(src(principal, R, VISOR))}" alt="{e(vistas[0]['title'])}" fetchpriority="high"></a>
    <figcaption>{e(vistas[0]['title'])}{credito(vistas[0].get('cred'))}</figcaption>
  </figure>
  <div class="acciones">{"".join(enlaces)}</div>
  <p class="entradilla">{e(d['snippet'])}</p>
  <div class="columnas">
    <div class="textos">
      <section><h2>{e(h1)}</h2><p>{t1}</p></section>
      <section><h2>{e(h2)}</h2><p>{t2}</p></section>
      <section><h2>{e(h3)}</h2><p>{t3}</p></section>
      <div class="autor-datos">{pie_fuentes}</div>
    </div>
    <aside class="ficha">
      <dl>
        {f"<dt>Fecha</dt><dd>{e(d['fecha'])}</dd>" if d.get('fecha') else ""}
        {f"<dt>Dónde está</dt><dd><a href='{e(mapa_url)}' title='Ver en el mapa'>{e(sede[0])}</a><br><span>{e(sede[1])}</span></dd>" if sede else ""}
        {f"<dt>Imagen</dt><dd>{e(d.get('px', ''))} · {e(d.get('mp', ''))}</dd>" if d.get('px') else ""}
        <dt>Libro</dt><dd><a href="{R}libros/{L['id']}/">{e(L['title'])}</a></dd>
        {("<dt>Temas</dt><dd>" + "<br>".join(f'<a href="{R}temas/{t["clave"]}/">{e(t["titulo"])}</a>' for t in TEMAS_DE.get((L["id"], g), [])) + "</dd>") if TEMAS_DE.get((L["id"], g)) else ""}
      </dl>
      {f'''<a class="autor-mini" href="{R}autores/{a['clave']}/">{f'<img src="{R}{e(imagen(a["retrato"])[0])}" alt="">' if a.get('retrato') else ''}<span><small>Autor</small>{e(a['nombre'])}<em>{e(a['anios'])}</em></span></a>''' if a else ""}
    </aside>
  </div>
  {f'<section class="otras"><h2>Otras vistas</h2><div class="rejilla-vistas">{otras}</div></section>' if otras else ""}
  <nav class="paso">
    {f'<a href="{R}{ant}/">‹ {e(L["details"][g - 1]["title"])}</a>' if ant else '<span></span>'}
    {f'<a href="{R}{sig}/">{e(L["details"][g + 1]["title"])} ›</a>' if sig else '<span></span>'}
  </nav>
</article>"""
            ld = {"@context": "https://schema.org", "@type": "VisualArtwork", "name": d["title"],
                  "description": d["snippet"], "image": absoluta(principal, VISOR),
                  "url": URL_SITIO + ruta + "/", "isPartOf": {"@type": "Collection", "name": L["title"]}}
            if a: ld["creator"] = {"@type": "Person", "name": a["nombre"]}
            if d.get("fecha"): ld["dateCreated"] = d["fecha"]
            urls.append(pagina(ruta, d["title"], d["snippet"], cuerpo, absoluta(principal), ld, "libros"))

    # ---- un libro
    for L in libros:
        R = "../../"
        cartas = "".join(
            tarjeta(f"{R}{FICHAS[L['id']][g]}/", src(L["groups"][g][0]["src"], R),
                    f"Obra {g + 1:02d}", d["title"], d["artist"], R, d["snippet"])
            for g, d in enumerate(L["details"]))
        intro = INTRO.get(L["id"], L["sub"])
        cuerpo = f"""
<nav class="migas"><a href="{R}libros/">Libros</a> › {e(L['corto'])}</nav>
<header class="portada-libro">
  <p class="ante">{e(L['tag'])}</p>
  <h1>{e(L['title'])}</h1>
  <p class="intro">{e(intro)}</p>
  <div class="acciones"><a class="boton oro" href="{R}#/{L['id']}">Explorar en la aplicación: ordenar, buscar y visor</a></div>
</header>
<div class="rejilla">{cartas}</div>"""
        urls.append(pagina(f"libros/{L['id']}", L["title"], intro[:300],
                           cuerpo, absoluta(L["groups"][0][0]["src"]), None, "libros"))

    # ---- temas que cruzan los libros (herramientas/temas.py)
    nombre_libro = {L["id"]: L["corto"] for L in libros}
    orden_libro = {L["id"]: k for k, L in enumerate(libros)}
    for t in TEMAS:
        R = "../../"
        pas = "".join(f'<li><strong>{e(ref)}</strong><span>{e(txt)}</span></li>' for _, ref, txt in t["pasajes"])
        grupos = {}
        for lb, num in t["obras"]:
            grupos.setdefault(lb, []).append(POR_NUM[(lb, num)])
        bloques = ""
        for lb in sorted(grupos, key=lambda x: orden_libro[x]):
            L = next(x for x in libros if x["id"] == lb)
            cartas = "".join(tarjeta(f"{R}{FICHAS[lb][g]}/", src(L["groups"][g][0]["src"], R),
                                     f"Obra {g + 1:02d}", L["details"][g]["title"], L["details"][g]["artist"], R)
                             for g in grupos[lb])
            bloques += f'<h2 class="seccion">{e(nombre_libro[lb])}</h2><div class="rejilla">{cartas}</div>'
        sin_obra = [nombre_libro[lb] for lb, _, _ in t["pasajes"] if lb not in grupos]
        cuerpo = f"""
<nav class="migas"><a href="{R}temas/">Temas</a> › {e(t['titulo'])}</nav>
<header class="portada-libro">
  <p class="ante">Tema · {" · ".join(dict.fromkeys(nombre_libro[lb] for lb, _, _ in t["pasajes"]))}</p>
  <h1>{e(t['titulo'])}</h1>
  <p class="intro">{e(t['intro'])}</p>
</header>
<section class="bloque"><h2>Los textos</h2><ul class="pasajes">{pas}</ul>
<p class="atribucion">Las referencias remiten al texto de cada obra y se pueden comprobar en cualquier edición.</p></section>
{bloques}"""
        primera = next(iter(grupos))
        urls.append(pagina(f"temas/{t['clave']}", t["titulo"], t["lema"], cuerpo,
                           absoluta(next(x for x in libros if x["id"] == primera)["groups"][grupos[primera][0]][0]["src"]),
                           None, "temas"))
    R = "../"
    cartas = []
    for t in TEMAS:
        lb, num = t["obras"][0]
        L = next(x for x in libros if x["id"] == lb)
        libros_t = " · ".join(dict.fromkeys(nombre_libro[x] for x, _, _ in t["pasajes"]))
        cartas.append(tarjeta(f"{R}temas/{t['clave']}/", src(L["groups"][POR_NUM[(lb, num)]][0]["src"], R),
                              libros_t, t["titulo"], f"{len(t['obras'])} obras", R, t["lema"]))
    cuerpo = f"""
<header class="portada-libro"><p class="ante">La colección</p><h1>Temas</h1>
<p class="intro">El mismo pasaje contado en libros distintos: el Diluvio en el Génesis, Gilgamesh y el Atrahasis; el hombre hecho de barro; la torre de Babel y el templo de Marduk. Cada tema reúne las obras de todos los libros que lo representan, con la referencia exacta de cada texto.</p></header>
<div class="rejilla libros">{"".join(cartas)}</div>"""
    urls.append(pagina("temas", "Temas", "Pasajes que se repiten entre el Génesis, Gilgamesh, la Ilíada, el Atrahasis y el Enuma Elish.",
                       cuerpo, None, None, "temas"))

    # ---- índice de libros
    R = "../"
    cartas = "".join(tarjeta(f"{R}libros/{L['id']}/", src(L["groups"][0][0]["src"], R), L["tag"], L["title"],
                             f"{len(L['details'])} obras", R, L["sub"]) for L in libros)
    cuerpo = f"""
<header class="portada-libro"><p class="ante">La colección</p><h1>Libros</h1>
<p class="intro">Cada libro con sus obras: pintura, escultura, cerámica y arqueología, en la mayor resolución que existe de cada una.</p></header>
<div class="rejilla libros">{cartas}</div>"""
    urls.append(pagina("libros", "Libros", "Los libros de la colección y sus obras.", cuerpo,
                       absoluta(libros[0]["groups"][0][0]["src"]), None, "libros"))

    # ---- un autor
    # Cada dato con su fuente: la biografía con sus notas, qué dice cada fuente sobre el
    # nacimiento y la muerte (y dónde discrepan), la nota del Getty, las obras de referencia
    # académicas y los registros de autoridad. Ver herramientas/autores_wikidata.py,
    # autores_ulan.py y el campo «fuentes» de data_autores.py.
    _fa = os.path.join(AQUI, "datos", "autores_fuentes.json")     # incorporar_fuentes.py
    FA = json.load(io.open(_fa, encoding="utf-8")) if os.path.exists(_fa) else {}
    WD = json.load(io.open(os.path.join(AQUI, "datos", "autores_wikidata.json"), encoding="utf-8"))["autores"]
    UL = json.load(io.open(os.path.join(AQUI, "datos", "autores_ulan.json"), encoding="utf-8"))["autores"]
    PAGO = {"P8406", "P2843", "P1415", "P3219"}
    AUTORIDAD = {"P650", "P7902"}

    def celda(f, lugar):
        partes = [x for x in (f, lugar) if x]
        return e(", ".join(partes)) if partes else '<span class="nd">no consta</span>'

    for a in autores:
        R = "../../"
        fa, wd, ul = FA.get(a["clave"], {}), WD.get(a["clave"]), UL.get(a["clave"])
        obras = "".join(
            tarjeta(f"{R}{FICHAS[o['libro']][o['i']]}/",
                    src(next(L for L in libros if L["id"] == o["libro"])["groups"][o["i"]][0]["src"], R),
                    next(L["corto"] for L in libros if L["id"] == o["libro"]), o["title"], "", R)
            for o in a["obras"])
        retrato = (f'<figure class="retrato"><img src="{R}{e(imagen(a["retrato"])[0])}" alt="{e(a["nombre"])}">'
                   f'<figcaption>{e(a.get("retratoPie", ""))}</figcaption></figure>' if a.get("retrato")
                   else '<figure class="retrato vacio"><span>No se conserva retrato</span></figure>')
        fuentes = fa.get("fuentes") or []
        bio = con_notas(fa.get("bio") or a["bio"])

        # qué dice cada fuente
        filas = []
        vida = fa.get("vida") or {}
        if vida:
            nac, mue = vida.get("nacimiento") or {}, vida.get("muerte") or {}
            ref = lambda d: (f' <sup><a href="#f{d["fuente"]}">{d["fuente"]}</a></sup>' if d.get("fuente") else "")
            filas.append(f'<tr><th>Bibliografía académica</th><td>{celda(nac.get("fecha"), nac.get("lugar"))}{ref(nac)}</td>'
                         f'<td>{celda(mue.get("fecha"), mue.get("lugar"))}{ref(mue)}</td></tr>')
        if ul:
            filas.append(f'<tr><th><a href="{e(ul["url"])}">Getty ULAN</a></th>'
                         f'<td>{celda(ul["nacimiento_texto"], (ul["nacimiento"] or {}).get("lugar"))}</td>'
                         f'<td>{celda(ul["muerte_texto"], (ul["muerte"] or {}).get("lugar"))}</td></tr>')
        if wd:
            filas.append(f'<tr><th><a href="https://www.wikidata.org/wiki/{e(wd["qid"])}">Wikidata</a></th>'
                         f'<td>{celda(wd["nacimiento"]["fecha"], (wd["nacimiento"]["lugar"] or {}).get("texto"))}</td>'
                         f'<td>{celda(wd["muerte"]["fecha"], (wd["muerte"]["lugar"] or {}).get("texto"))}</td></tr>')
        tabla = (f'<section class="bloque"><h2>Qué dice cada fuente</h2><div class="tabla"><table>'
                 f'<thead><tr><th></th><th>Nacimiento</th><th>Muerte</th></tr></thead><tbody>{"".join(filas)}</tbody></table></div>'
                 + ("".join(f'<p class="discrepancia">{e(x)}</p>' for x in fa.get("discrepancias") or []))
                 + '</section>') if filas else ""

        nota = (f'<section class="bloque"><h2>Nota biográfica del Getty</h2>'
                f'<blockquote lang="en">{e(ul["nota"])}</blockquote>'
                f'<p class="atribucion">Getty Research Institute, <a href="{e(ul["url"])}">Union List of Artist Names</a>, '
                f'registro {e(ul["ulan"])}. Datos abiertos bajo licencia ODC-By 1.0.</p></section>'
                if ul and ul.get("nota") and len(ul["nota"]) > 80 else "")
        fuentes_html = (lista_fuentes(fuentes, "Fuentes de la biografía") if fuentes else
                         '<p class="discrepancia">Esta biografía todavía no está contrastada con fuentes académicas.</p>')
        refs = [r for r in (wd or {}).get("referencias", []) if r["pid"] not in AUTORIDAD]
        leer = (f'<section class="bloque"><h2>Para leer más</h2><ul class="refs">'
                + "".join(f'<li><a href="{e(r["url"])}">{e(r["obra"])}</a>'
                          f'{" <small>requiere suscripción</small>" if r["pid"] in PAGO else ""}</li>' for r in refs)
                + '</ul></section>') if refs else ""
        aut = []
        if ul: aut.append(("Getty ULAN", ul["url"]))
        ids = (wd or {}).get("ids", {})
        if ids.get("viaf"): aut.append(("VIAF", f"https://viaf.org/viaf/{ids['viaf']}/"))
        if ids.get("loc"): aut.append(("Library of Congress", f"https://id.loc.gov/authorities/names/{ids['loc']}.html"))
        for r in (wd or {}).get("referencias", []):
            if r["pid"] in AUTORIDAD: aut.append((r["obra"].split(",")[0].split(" (")[0], r["url"]))
        if wd: aut.append(("Wikidata", f"https://www.wikidata.org/wiki/{wd['qid']}"))
        autoridad = (f'<section class="bloque"><h2>Registros de autoridad</h2><p class="autoridad">'
                     + " · ".join(f'<a href="{e(u)}">{e(t)}</a>' for t, u in aut) + '</p></section>') if aut else ""
        sin_registro = ("" if (wd or ul) else
                        '<p class="discrepancia">No tiene registro en la Getty ULAN ni en Wikidata: lo que se sabe de '
                        'estos autores procede de sus firmas y de las fuentes antiguas citadas.</p>')

        cuerpo = f"""
<nav class="migas"><a href="{R}autores/">Autores</a> › {e(a['nombre'])}</nav>
<article class="autor-pag">
  {retrato}
  <div>
    <p class="ante">{e(a['oficio'])}</p>
    <h1>{e(a['nombre'])}</h1>
    <p class="autor">{e(a['anios'])}</p>
    <p class="bio">{bio}</p>
  </div>
</article>
<div class="autor-datos">
  {tabla}{sin_registro}
  {fuentes_html}
  {nota}
  {leer}
  {autoridad}
</div>
<h2 class="seccion">{len(a['obras'])} obra{'s' if len(a['obras']) > 1 else ''} en la colección</h2>
<div class="rejilla">{obras}</div>"""
        img_og = (URL_SITIO + imagen(a["retrato"])[0]) if a.get("retrato") else None
        ld = {"@context": "https://schema.org", "@type": "Person", "name": a["nombre"],
              "url": URL_SITIO + f"autores/{a['clave']}/",
              "sameAs": [u for _, u in aut]}
        if img_og: ld["image"] = img_og
        urls.append(pagina(f"autores/{a['clave']}", a["nombre"], sin_notas(fa.get("bio") or a["bio"])[:300],
                           cuerpo, img_og, ld, "autores"))

    # ---- índice de autores
    R = "../"
    cartas = "".join(
        f'<a class="autor-carta" href="{R}autores/{a["clave"]}/">'
        + (f'<img src="{R}{e(imagen(a["retrato"])[0])}" alt="" loading="lazy">' if a.get("retrato") else '<span class="sin"></span>')
        + f'<strong>{e(a["nombre"])}</strong><em>{e(a["anios"])} · {len(a["obras"])} obra{"s" if len(a["obras"]) > 1 else ""}</em></a>'
        for a in sorted(autores, key=lambda x: (x["nace"] is None, x["nace"] or 0)))
    cuerpo = f"""
<header class="portada-libro"><p class="ante">La colección</p><h1>Autores</h1>
<p class="intro">Solo los artistas de nombre propio, por orden de nacimiento. Los relieves, las tablillas y los mosaicos anónimos no aparecen aquí: fingir una autoría sería peor que decir que no la hay.</p></header>
<div class="autores">{cartas}</div>"""
    urls.append(pagina("autores", "Autores", "Los artistas de la colección, con su biografía y sus obras.",
                       cuerpo, None, None, "autores"))

    # ---- entradas con dirección limpia a las vistas de la aplicación
    for k, t in (("mapa", "Mapa"), ("cronologia", "Cronología"), ("cobertura", "Cobertura")):
        dst = os.path.join(SITIO, k, "index.html")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        io.open(dst, "w", encoding="utf-8").write(
            f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>{t} · {NOMBRE}</title>'
            f'<meta http-equiv="refresh" content="0; url=../#/{k}"><link rel="canonical" href="{URL_SITIO}#/{k}">'
            f'</head><body><p><a href="../#/{k}">{t}</a></p></body></html>')

    # ---- 404, sitemap, robots, estilos
    io.open(os.path.join(SITIO, "404.html"), "w", encoding="utf-8").write(
        f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>No encontrada · {NOMBRE}</title><link rel="stylesheet" href="{URL_SITIO}estilo.css"></head><body>'
        f'<main class="no-hay"><p class="ante">404</p><h1>Esta página no existe</h1>'
        f'<p>Puede que la obra haya cambiado de número. <a href="{URL_SITIO}libros/">Ver los libros</a> · '
        f'<a href="{URL_SITIO}">Ir al inicio</a></p></main></body></html>')
    todas = [URL_SITIO] + sorted(set(urls))
    io.open(os.path.join(SITIO, "sitemap.xml"), "w", encoding="utf-8").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in todas) + "</urlset>\n")
    io.open(os.path.join(SITIO, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {URL_SITIO}sitemap.xml\n")
    io.open(os.path.join(SITIO, "estilo.css"), "w", encoding="utf-8").write(
        io.open(os.path.join(AQUI, "estilo.css"), encoding="utf-8").read())

    print(f"páginas: {sum(len(v) for v in FICHAS.values())} obras · {len(libros)} libros · "
          f"{len(autores)} autores · {len(todas)} direcciones en sitemap.xml")
    return FICHAS


if __name__ == "__main__":
    generar()
