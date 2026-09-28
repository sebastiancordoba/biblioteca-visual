# -*- coding: utf-8 -*-
import html, io, os, re
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
doc=io.open(os.path.join(TMP,"b1.part"),encoding="utf-8").read()
e=lambda t: html.escape(str(t),quote=True)
WIKI_SVG='<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>'

# ---------- renderizador: enlace al original y etiqueta de época ----------
v="""        const wiki = d.wikiUrl ? `
                <a href="${esc(d.wikiUrl)}" target="_blank" rel="noopener" class="wiki-link-btn" title="Ver en Wikipedia">Wikipedia ${SVG_WIKI}</a>` : '';"""
n="""        const wiki = d.wikiUrl ? `
                <a href="${esc(d.wikiUrl)}" target="_blank" rel="noopener" class="wiki-link-btn" title="Ver en Wikipedia">Wikipedia ${SVG_WIKI}</a>` : '';
        // las imágenes de esta página son vistas previas: el original vive en Commons
        const orig = d.orig ? `
                <a href="${esc(d.orig)}" target="_blank" rel="noopener" class="wiki-link-btn orig-link" title="Abrir el archivo original de ${esc(d.px)} px">Original <span class="mp-tag">${esc(d.mp)}</span> ${SVG_WIKI}</a>` : '';"""
assert v in doc; doc=doc.replace(v,n,1)
doc=doc.replace("                </button>${wiki}","                </button>${wiki}${orig}",1)

vn="""                <span class="artwork-num">${criterio === 'cronologia' && d.fecha ? esc(d.fecha) : 'OBRA ' + String(i + 1).padStart(2, '0')}</span>"""
nn="""                <span class="artwork-num">${d.epoca ? esc(d.epoca) : (criterio === 'cronologia' && d.fecha ? esc(d.fecha) : 'OBRA ' + String(i + 1).padStart(2, '0'))}</span>"""
assert vn in doc; doc=doc.replace(vn,nn,1)

# ---------- visor: enlace al original junto al de Wikipedia ----------
vm='''        <a id="panelWikiLink" href="#" target="_blank" rel="noopener" class="wiki-link-btn" title="Ver en Wikipedia">'''
assert vm in doc
doc=doc.replace(vm,
 '        <a id="panelOrigLink" href="#" target="_blank" rel="noopener" class="wiki-link-btn orig-link" '
 'title="Abrir el archivo original en máxima resolución">\n'
 f'          Ver original <span class="mp-tag" id="panelOrigMp"></span> {WIKI_SVG}\n        </a>\n'
 + vm, 1)

vf="""      const wikiLinkEl = document.getElementById('panelWikiLink');
      if (details.wikiUrl) {
        wikiLinkEl.href = details.wikiUrl;
        wikiLinkEl.style.display = 'inline-flex';
      } else {
        wikiLinkEl.style.display = 'none';
      }"""
nf="""      const wikiLinkEl = document.getElementById('panelWikiLink');
      if (details.wikiUrl) {
        wikiLinkEl.href = details.wikiUrl;
        wikiLinkEl.style.display = 'inline-flex';
      } else {
        wikiLinkEl.style.display = 'none';
      }

      /* La imagen del visor es una vista previa: cuando el zoom agota su detalle,
         este enlace lleva al archivo completo en Commons. */
      const origLinkEl = document.getElementById('panelOrigLink');
      if (details.orig) {
        origLinkEl.href = details.orig;
        document.getElementById('panelOrigMp').innerText = details.mp || '';
        origLinkEl.style.display = 'inline-flex';
      } else {
        origLinkEl.style.display = 'none';
      }

      /* Crédito de la foto que se está viendo: CC BY y CC BY-SA obligan a nombrar al autor
         y la licencia. En dominio público no se nombra a nadie como fotógrafo. */
      const credEl = document.getElementById('panelCredito');
      if (credEl) {
        const c = item.cred;
        const enl = (u, t) => u ? `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(t)}</a>` : esc(t);
        credEl.innerHTML = !c ? '' :
          (c.a ? (/^(photo|foto|photograph)/i.test(c.a) ? '' : 'Foto: ') + enl(c.au, c.a) + ' · ' : '') +
          enl(c.lu, c.l || '') + ' · ' + enl(c.f, 'Wikimedia Commons');
      }"""
assert vf in doc; doc=doc.replace(vf,nf,1)

# ---------- visor: línea de crédito bajo los enlaces del panel ----------
_m=re.search(r'(<a id="panelWikiLink"[\s\S]*?</a>\s*</div>)', doc)
assert _m, "no encuentro el bloque de enlaces del panel"
doc=doc.replace(_m.group(1), _m.group(1)+'\n      <p id="panelCredito" class="credito"></p>', 1)

# ---------- avisar en el visor al superar el detalle de la previa ----------
va="""      zoomScaleText.innerText = Math.round(zoomScale * 100) + '%';"""
if va in doc:
    doc=doc.replace(va, va+"""
      // por encima de ~3x se agota el detalle de la vista previa
      zoomScaleText.classList.toggle('sobre-previa', zoomScale > 3);""",1)
    print("aviso de límite de previa: añadido")

# ---------- pestañas nuevas ----------
# El anclaje no puede llevar nada escrito a mano —ni la cuenta de obras ni el nombre de
# un libro concreto—: ambos cambian y entonces la sustitución falla y se publica un
# intermedio caducado sin que se note. Cronología y Cobertura van detrás de la Biblioteca,
# que es el último botón fijo de la barra.
m = re.search(r'<button class="book-btn" id="btnBiblioteca"[^>]*>.*?</button>', doc, re.S)
assert m, "no se encontró el botón de la Biblioteca"
anc = m.group(0)
doc=doc.replace(anc, anc+
 '\n      <button class="book-btn" onclick="switchBook(\'cronologia\', this)">Cronología</button>'
 '\n      <button class="book-btn" onclick="switchBook(\'cobertura\', this)">Cobertura</button>',1)

ICO_T='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"></circle><polyline points="12 7 12 12 15 14"></polyline></svg>'
ICO_L='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"></path></svg>'
na='    </nav>\n  </header>'
assert na in doc
doc=doc.replace(na,
 '    </nav>\n\n'
 '    <nav id="nav-cronologia" class="book-nav">\n'
 '      <button class="tab-btn active" onclick="switchTab(\'cronologia-gallery\', this)">\n'
 f'        {ICO_T}\n        3200 a.C. — 1892\n      </button>\n    </nav>\n\n'
 '    <nav id="nav-cobertura" class="book-nav">\n'
 '      <button class="tab-btn active" onclick="switchTab(\'cobertura-gallery\', this)">\n'
 f'        {ICO_L}\n        Capítulos y cantos\n      </button>\n    </nav>\n  </header>',1)

# La etiqueta con el nombre del archivo solo tiene sentido en la colección local. Aquí las
# imágenes van incrustadas como datos, así que split('/') sobre la cadena base64 dejaba un
# fragmento ilegible terminado en "9k=" bajo cada obra.
V_TAG = """            <div class="file-tag">${esc(main.src.split('/').pop())}</div>\n"""
assert V_TAG in doc, "no se encontró la etiqueta de nombre de archivo"
doc = doc.replace(V_TAG, "", 1)
print("etiqueta de nombre de archivo eliminada de la versión publicable")

io.open(os.path.join(TMP,"b2.part"),"w",encoding="utf-8").write(doc)
print("interfaz y visor parcheados")
