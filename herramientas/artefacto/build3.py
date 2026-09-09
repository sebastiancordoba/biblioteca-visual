# -*- coding: utf-8 -*-
import base64, html, io, os, re, sys
AQUI=os.path.dirname(os.path.abspath(__file__))
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mapa_js import JS as MAPA_JS
doc=io.open(os.path.join(TMP,"b2.part"),encoding="utf-8").read()
e=lambda t: html.escape(str(t),quote=True)

CIF = eval(io.open(os.path.join(TMP,"cifras_mapa.py"),encoding="utf-8").read())

COB = eval(io.open(os.path.join(AQUI,"datos","cob.py"),encoding="utf-8").read())

# ---------- botón y nav del mapa ----------
anc='<button class="book-btn" onclick="switchBook(\'cronologia\', this)">Cronología</button>'
assert anc in doc
doc=doc.replace(anc, anc+'\n      <button class="book-btn" onclick="switchBook(\'mapa\', this)">Mapa</button>',1)

ICO_M='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 6v16l7-4 8 4 7-4V2l-7 4-8-4-7 4z"></path><path d="M8 2v16M16 6v16"></path></svg>'
na='    <nav id="nav-cobertura" class="book-nav">'
assert na in doc
doc=doc.replace(na,
 '    <nav id="nav-mapa" class="book-nav">\n'
 '      <button class="tab-btn active" onclick="switchTab(\'mapa-gallery\', this)">\n'
 f'        {ICO_M}\n        {CIF["sedes"]} sedes en {CIF["paises"]} países\n      </button>\n    </nav>\n\n'+na,1)

# ---------- BOOKS.mapa comparte los arrays de la cronología ----------
_m2=re.search(r"^ *let currentBook = '[a-z]+';", doc, re.M)
assert _m2, 'no se encontró la declaración de currentBook'
anc2=_m2.group(0)
doc=doc.replace(anc2,
 "    /* El mapa reutiliza las mismas fichas e imágenes que la cronología: comparte los\n"
 "       arrays por referencia, así que el visor funciona igual sin duplicar nada. */\n"
 "    BOOKS.mapa = Object.assign({}, BOOKS.cronologia, {\n"
 "      tag: 'Dónde están hoy',\n"
 "      title: 'Mapa de la colección',\n"
 f"      sub: 'Las {CIF['obras']} obras repartidas en {CIF['sedes']} sedes de {CIF['paises']} países. Elige un punto del mapa o una sede de la lista para ver qué guarda; cada obra abre en el mismo visor.',\n"
 "      firstTab: 'mapa-gallery'\n"
 "    });\n\n"+anc2,1)

# ---------- paneles ----------
T=['    <div id="cronologia-gallery" class="tab-content">',
   '      <div class="grid-3col" id="cronologia-grid"></div>','    </div>','']
T.append(io.open(os.path.join(TMP,"mapa_panel.html"),encoding="utf-8").read())
T+=['    <div id="cobertura-gallery" class="tab-content">','      <div class="cobertura">']
for nom,(sub,c1,filas) in COB.items():
    T+=[f'        <h2>{e(nom)}</h2>',f'        <p class="cob-sub">{e(sub)}</p>',
        f'        <div class="cob-tabla"><table><thead><tr><th>{e(c1)}</th><th>Pasaje</th><th>Obra o candidato</th></tr></thead><tbody>']
    for cap,pas,st,ob in filas:
        T.append(f'          <tr><td>{e(cap)}</td><td class="pasaje"><span class="pip {st}"></span>{e(pas)}</td><td>{e(ob)}</td></tr>')
    T.append('        </tbody></table></div>')
T+=['        <p class="cob-leyenda"><span><span class="pip si"></span>en la colección</span>'
    '<span><span class="pip casi"></span>descargando</span>'
    '<span><span class="pip no"></span>hueco por llenar</span></p>','      </div>','    </div>']
anc3='  </div>\n\n  <!-- VISOR MODAL'
assert anc3 in doc; doc=doc.replace(anc3,"\n".join(T)+"\n\n"+anc3,1)

# ---------- JS del mapa, al final del script ----------
anc4="  </script>"
assert anc4 in doc; doc=doc.replace(anc4, MAPA_JS+"\n"+anc4, 1)
datos=io.open(os.path.join(TMP,"mapa_datos.js"),encoding="utf-8").read()
doc=doc.replace("  <script>\n","  <script>\n"+datos,1)

io.open(os.path.join(TMP,"b3.part"),"w",encoding="utf-8").write(doc)
print("mapa integrado ·", f"{len(doc)/1000:.0f} KB")
