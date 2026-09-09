# -*- coding: utf-8 -*-
import base64, html, io, os, re
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
doc=io.open(os.path.join(TMP,"step2.part"),encoding="utf-8").read()
e=lambda t: html.escape(str(t),quote=True)

COB={
 "Génesis":("50 capítulos. La colección cubría solo del 1 al 11; la historia patriarcal —el asunto del propio ensayo de la colección— estaba entera vacía.",
  "Cap.",[
  ("1","Creación; el Anciano de los Días","si","Blake"),
  ("1–2","La creación de Adán","si","Miguel Ángel"),
  ("2","La creación de Eva","no","Miguel Ángel, Sixtina — en Commons solo a 1,3 MP"),
  ("2–3","El Edén","si","El Bosco · Cranach · Durero"),
  ("3","La expulsión del Paraíso","si","Masaccio"),
  ("3","Pecado original y expulsión","no","Miguel Ángel, Sixtina — solo 1,4 MP"),
  ("4","Caín y Abel","si","Tiziano · Cormon"),
  ("6–9","El Diluvio","si","Miguel Ángel · Turner · van Scorel · Watts · Danby · Cole"),
  ("9","La embriaguez de Noé","no","Bellini — pendiente"),
  ("11","La Torre de Babel","si","Bruegel · Doré"),
  ("18","La hospitalidad de Abraham","si","Rubliov"),
  ("19","Destrucción de Sodoma","si","John Martin"),
  ("19","Lot y sus hijas","casi","Rubens, Schwerin"),
  ("21","Agar e Ismael","si","Corot"),
  ("22","El sacrificio de Isaac","si","Caravaggio · Rembrandt"),
  ("24","Eliezer y Rebeca","casi","Poussin, Louvre — 70 MP"),
  ("27","Isaac bendice a Jacob","casi","Ribera, Prado"),
  ("28","La escala de Jacob","casi","Ribera, Prado — 680 MP"),
  ("29","Jacob y Raquel en el pozo","no","Palma il Vecchio · Dyce"),
  ("32","La lucha con el ángel","si","Delacroix · Gauguin"),
  ("37","La túnica de José","si","Velázquez"),
  ("37","José vendido por sus hermanos","no","Overbeck · Flavitsky"),
  ("39","José y la mujer de Putifar","no","Rembrandt · Gentileschi"),
  ("49","Jacob bendice a Efraín y Manasés","no","Rembrandt, Kassel"),
 ]),
 "La Ilíada":("24 cantos. Están cubiertos el principio, el final y el ciclo troyano ajeno al poema; el centro —los cantos IX, XVI y XVIII— es donde más falta.",
  "Canto",[
  ("previo","El juicio de Paris","si","Rubens, National Gallery"),
  ("previo","El sacrificio de Ifigenia","si","Jacques-Louis David"),
  ("I","Tetis suplica a Zeus","si","Ingres"),
  ("I","Briseida arrebatada a Aquiles","no","Giambattista Tiepolo"),
  ("III","Helena en las murallas","no","en Commons solo a 0,2 MP"),
  ("VI","Héctor y Andrómaca","si","Jacques-Louis David"),
  ("IX","La embajada a Aquiles","no","Ingres, ENSBA — el mayor hueco del poema; en Commons a 0,8 MP"),
  ("X","La Dolonía","si","Casco de colmillos de jabalí"),
  ("XVI","Aquiles llora a Patroclo","si","Gavin Hamilton"),
  ("XVI","La muerte de Sarpedón","casi","Crátera de Eufronio — 42 MP"),
  ("XVIII","Tetis y las armas de Aquiles","casi","Van Dyck, Sanssouci — 75 MP"),
  ("XXII","El triunfo sobre Héctor","si","Franz von Matsch"),
  ("XXIV","Príamo pide el cuerpo de Héctor","si","Alexander Ivanov"),
  ("post.","El caballo de Troya","si","Giandomenico Tiepolo"),
  ("post.","Laocoonte","si","Escuela de Rodas"),
  ("—","Aquiles y Áyax juegan a los dados","si","Exekias"),
  ("arq.","Micenas y Troya","si","Máscara de Agamenón · Puerta de los Leones · Egina · Hisarlik"),
  ("arq.","La copa de Néstor","no","pendiente"),
 ]),
 "Gilgamesh":("12 tablillas. Cobertura casi completa para lo que existe materialmente: el poema apenas tiene tradición pictórica.",
  "Tablilla",[
  ("I","Las murallas de Uruk","si","Vaso de Warka · Lamassu"),
  ("I","Los sueños de Gilgamesh","si","Tablilla del Sueño"),
  ("II–V","Humbaba y el Bosque de los Cedros","si","Placa babilónica · máscara de terracota"),
  ("VI","Ishtar rechazada","si","Relieve de la Reina de la Noche"),
  ("VI","El Toro Celeste","no","placas de terracota, pendiente"),
  ("—","El héroe y las fieras","si","Relieve de Khorsabad · sello acadio"),
  ("VII–X","La muerte de Enkidu; el inframundo","no","sin obra conocida"),
  ("XI","El Diluvio","si","Tablilla XI, Biblioteca de Asurbanipal"),
 ]),
}

# ---------- botón en el selector de libro ----------
anc='<button class="book-btn" onclick="switchBook(\'iliada\', this)">La Ilíada<span class="book-count">15</span></button>'
assert anc in doc
doc=doc.replace(anc, anc+'\n      <button class="book-btn" onclick="switchBook(\'cobertura\', this)">Cobertura</button>',1)

# ---------- nav propio ----------
ICO='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M3 12h18M3 18h18"></path></svg>'
nav_anc='    </nav>\n  </header>'
assert nav_anc in doc
doc=doc.replace(nav_anc,
 '    </nav>\n\n    <nav id="nav-cobertura" class="book-nav">\n'
 '      <button class="tab-btn active" onclick="switchTab(\'cobertura-gallery\', this)">\n'
 f'        {ICO}\n        Capítulos y cantos\n      </button>\n    </nav>\n  </header>',1)

# ---------- entrada en BOOKS ----------
anc2="    let currentBook = 'genesis';"
assert anc2 in doc
doc=doc.replace(anc2,
 """    /* La cobertura no es un libro, pero se comporta como uno: sin obras propias, su
       grilla no existe y renderBookGrid() sale sin hacer nada. */
    BOOKS.cobertura = {
      tag: 'Estado de la colección',
      title: 'Capítulos, cantos y tablillas',
      sub: 'Qué pasajes están representados y cuáles siguen vacíos, con el candidato concreto para cada hueco. La colección crece por pasajes que faltan, no por acumulación de cuadros sueltos.',
      firstTab: 'cobertura-gallery',
      details: [],
      groups: []
    };

""" + anc2, 1)

# ---------- contenido ----------
T=['    <div id="cobertura-gallery" class="tab-content">','      <div class="cobertura">']
for nom,(sub,col1,filas) in COB.items():
    T.append(f'        <h2>{e(nom)}</h2>')
    T.append(f'        <p class="cob-sub">{e(sub)}</p>')
    T.append('        <div class="cob-tabla"><table><thead><tr>'
             f'<th>{e(col1)}</th><th>Pasaje</th><th>Obra o candidato</th></tr></thead><tbody>')
    for cap,pas,st,obra in filas:
        T.append(f'          <tr><td>{e(cap)}</td><td class="pasaje">'
                 f'<span class="pip {st}"></span>{e(pas)}</td><td>{e(obra)}</td></tr>')
    T.append('        </tbody></table></div>')
T.append('        <p class="cob-leyenda"><span><span class="pip si"></span>en la colección</span>'
         '<span><span class="pip casi"></span>descargando</span>'
         '<span><span class="pip no"></span>hueco por llenar</span></p>')
T.append('      </div>\n    </div>')
anc3='  </div>\n\n  <!-- VISOR MODAL'
assert anc3 in doc
doc=doc.replace(anc3, "\n".join(T)+"\n\n"+anc3, 1)

# ---------- estilos añadidos ----------
CSS="""
    /* ---- añadidos de la versión publicable ---- */
    .aviso-previa{
      max-width:760px;margin:0 auto 26px;padding:13px 18px;
      border:1px solid var(--border-subtle);border-radius:4px;
      background:rgba(197,160,70,.05);color:var(--text-body);
      font-size:.82rem;line-height:1.6;text-align:left;
    }
    .aviso-previa strong{color:var(--accent-gold);font-weight:600}
    .orig-link .mp-tag{
      font-family:var(--font-sans);font-size:.62rem;opacity:.7;
      font-variant-numeric:tabular-nums;
    }
    .cobertura{max-width:1000px;margin:0 auto}
    .cobertura h2{
      font-family:var(--font-serif);color:var(--text-title);font-weight:500;
      font-size:1.35rem;letter-spacing:.5px;margin:44px 0 6px;
    }
    .cobertura h2:first-child{margin-top:0}
    .cob-sub{color:var(--text-muted);font-size:.92rem;max-width:64ch;margin:0 0 18px;font-weight:300}
    .cob-tabla{overflow-x:auto;border:1px solid var(--border-subtle);border-radius:4px}
    .cob-tabla table{border-collapse:collapse;width:100%;min-width:620px}
    .cob-tabla th{
      font-family:var(--font-serif);font-size:.62rem;letter-spacing:2px;
      text-transform:uppercase;color:var(--text-muted);text-align:left;
      font-weight:400;padding:12px 16px;background:var(--bg-surface);
      border-bottom:1px solid var(--border-subtle);
    }
    .cob-tabla td{
      padding:11px 16px;border-bottom:1px solid rgba(255,255,255,.05);
      vertical-align:top;color:var(--text-body);font-size:.88rem;
    }
    .cob-tabla tr:last-child td{border-bottom:0}
    .cob-tabla td:first-child{
      font-size:.78rem;color:var(--text-muted);white-space:nowrap;
      font-variant-numeric:tabular-nums;
    }
    .cob-tabla td.pasaje{color:var(--text-title)}
    .pip{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:10px;vertical-align:middle}
    .pip.si{background:var(--accent-gold)}
    .pip.casi{box-shadow:inset 0 0 0 1.5px var(--accent-gold)}
    .pip.no{box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.24)}
    .cob-leyenda{display:flex;gap:24px;flex-wrap:wrap;margin:18px 0 0;
      font-size:.76rem;color:var(--text-muted)}
  </style>"""
doc=doc.replace("  </style>", CSS, 1)

# ---------- aviso de vista previa, bajo la cabecera ----------
anc4='    <!-- SELECTOR DE LIBRO -->'
assert anc4 in doc
doc=doc.replace(anc4,
 '    <p class="aviso-previa"><strong>Estas imágenes son vistas previas.</strong> '
 'Una página publicada debe caber entera en 16&nbsp;MB y no puede cargar imágenes de dominios '
 'externos, así que van incrustadas y reducidas a 1050&nbsp;px. El zoom, el desplazamiento con '
 'W&nbsp;A&nbsp;S&nbsp;D y la navegación funcionan igual que en la colección local, pero el '
 'detalle real está en el enlace <em>Original</em> de cada obra — hasta 30.000&nbsp;×&nbsp;17.078 '
 'px en <em>El jardín de las delicias</em>. Los másteres, 650&nbsp;MB en total, viven en local.</p>\n\n'
 + anc4, 1)

io.open(os.path.join(TMP,"step3.part"),"w",encoding="utf-8").write(doc)
print("cobertura, estilos y aviso añadidos ·", f"{len(doc)/1e6:.1f} MB")
