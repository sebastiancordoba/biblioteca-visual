# -*- coding: utf-8 -*-
"""Genera el catálogo publicable (artefacto) desde las mismas fichas de la colección."""
import base64, html, io, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP  = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
sys.path.insert(0, os.path.join(ROOT, "herramientas"))
os.chdir(ROOT)
from data_genesis import GENESIS
from data_gilgamesh import GILGAMESH
from data_iliada import ILIADA

ENLACES = json.load(io.open(os.path.join(TMP, "enlaces.json"), encoding="utf-8"))
e = lambda t: html.escape(str(t or ""), quote=True)

def datauri(folder, fname):
    p = os.path.join(TMP, "thumbs", folder + "__" + fname)
    if not os.path.exists(p): return None
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

LIBROS = [
 ("genesis", "Génesis", GENESIS, "Génesis", "gen",
  "Cincuenta capítulos que la pintura europea recorrió durante seis siglos. La colección se detiene "
  "en la fractura del libro: los once primeros capítulos son cósmicos y anónimos —la creación, el "
  "fratricidio, el diluvio, Babel—; a partir del doce, el relato abandona a la humanidad entera y "
  "se ocupa de una sola familia."),
 ("gilgamesh", "Gilgamesh", GILGAMESH, "Gilgamesh", "gil",
  "El poema más antiguo que se conserva casi no tiene tradición pictórica: nadie lo ilustró durante "
  "los dos mil años en que estuvo perdido bajo la arena. Su iconografía es, por tanto, arqueológica "
  "—arcilla, alabastro, lapislázuli—, y esa ausencia de pintura es precisamente lo que la hace "
  "distinta de las otras dos colecciones."),
 ("iliada", "La Ilíada", ILIADA, "Ilíada", "ili",
  "Tres estratos que se iluminan entre sí: el objeto que Homero pudo tener delante —el casco de "
  "colmillos, la máscara de oro, las murallas—, la imagen que los propios griegos se hicieron del "
  "poema en sus vasos y sus frontones, y la lectura que Europa le proyectó encima dos milenios "
  "después."),
]

COBERTURA = {
 "Génesis": {
  "sub": "50 capítulos. La colección original cubría solo del 1 al 11; la historia patriarcal, que es el asunto del propio ensayo de la colección, estaba entera vacía.",
  "cols": ["Cap.", "Pasaje", "Obra o candidato"],
  "filas": [
   ("1",  "Creación; el Anciano de los Días", "si", "Blake"),
   ("1–2","La creación de Adán", "si", "Miguel Ángel"),
   ("2",  "La creación de Eva", "no", "Miguel Ángel, Sixtina — en Commons solo a 1,3 MP"),
   ("2–3","El Edén", "si", "El Bosco · Cranach · Durero"),
   ("3",  "La expulsión del Paraíso", "si", "Masaccio"),
   ("3",  "Pecado original y expulsión", "no", "Miguel Ángel, Sixtina — solo 1,4 MP"),
   ("4",  "Caín y Abel", "si", "Tiziano · Cormon"),
   ("6–9","El Diluvio", "si", "Miguel Ángel · Turner · van Scorel · Watts · Danby · Cole"),
   ("9",  "La embriaguez de Noé", "no", "Bellini — pendiente"),
   ("11", "La Torre de Babel", "si", "Bruegel · Doré"),
   ("18", "La hospitalidad de Abraham", "si", "Rubliov"),
   ("19", "Destrucción de Sodoma", "si", "John Martin"),
   ("19", "Lot y sus hijas", "casi", "Rubens, Schwerin — descargando"),
   ("21", "Agar e Ismael", "si", "Corot"),
   ("22", "El sacrificio de Isaac", "si", "Caravaggio · Rembrandt"),
   ("24", "Eliezer y Rebeca", "casi", "Poussin, Louvre, 70 MP — descargando"),
   ("27", "Isaac bendice a Jacob", "casi", "Ribera — descargando"),
   ("28", "La escala de Jacob", "casi", "Ribera, Prado, 680 MP — descargando"),
   ("29", "Jacob y Raquel en el pozo", "no", "Palma il Vecchio · Dyce"),
   ("32", "La lucha con el ángel", "si", "Delacroix · Gauguin"),
   ("37", "La túnica de José", "si", "Velázquez"),
   ("37", "José vendido por sus hermanos", "no", "Overbeck · Flavitsky"),
   ("39", "José y la mujer de Putifar", "no", "Rembrandt · Gentileschi"),
   ("49", "Jacob bendice a Efraín y Manasés", "no", "Rembrandt, Kassel"),
  ]},
 "La Ilíada": {
  "sub": "24 cantos. Están cubiertos el principio, el final y el ciclo troyano ajeno al poema; el centro —los cantos IX, XVI y XVIII— es donde falta más.",
  "cols": ["Canto", "Pasaje", "Obra o candidato"],
  "filas": [
   ("previo","El juicio de Paris", "si", "Rubens, National Gallery"),
   ("previo","El sacrificio de Ifigenia", "si", "Jacques-Louis David"),
   ("I",  "Tetis suplica a Zeus", "si", "Ingres"),
   ("I",  "Briseida arrebatada a Aquiles", "no", "Giambattista Tiepolo"),
   ("III","Helena en las murallas", "no", "En Commons solo a 0,2 MP"),
   ("VI", "Héctor y Andrómaca", "si", "Jacques-Louis David"),
   ("IX", "La embajada a Aquiles", "no", "Ingres, ENSBA — el mayor hueco del poema; en Commons a 0,8 MP"),
   ("X",  "La Dolonía", "si", "Casco de colmillos de jabalí"),
   ("XVI","Aquiles llora a Patroclo", "si", "Gavin Hamilton"),
   ("XVI","La muerte de Sarpedón", "casi", "Crátera de Eufronio, 42 MP — descargando"),
   ("XVIII","Tetis y las armas de Aquiles", "casi", "Van Dyck, Sanssouci, 75 MP — descargando"),
   ("XXII","El triunfo sobre Héctor", "si", "Franz von Matsch"),
   ("XXIV","Príamo pide el cuerpo de Héctor", "si", "Alexander Ivanov"),
   ("post","El caballo de Troya", "si", "Giandomenico Tiepolo"),
   ("post","Laocoonte", "si", "Escuela de Rodas"),
   ("—",  "Aquiles y Áyax juegan a los dados", "si", "Exekias"),
   ("arq.","Micenas y Troya", "si", "Máscara de Agamenón · Puerta de los Leones · Egina · Hisarlik"),
   ("arq.","La copa de Néstor", "no", "pendiente"),
  ]},
 "Gilgamesh": {
  "sub": "12 tablillas. Cobertura casi completa para lo que existe materialmente.",
  "cols": ["Tablilla", "Pasaje", "Obra o candidato"],
  "filas": [
   ("I",   "Las murallas de Uruk", "si", "Vaso de Warka · Lamassu"),
   ("I",   "Los sueños de Gilgamesh", "si", "Tablilla del Sueño"),
   ("II–V","Humbaba y el Bosque de los Cedros", "si", "Placa babilónica · máscara de terracota"),
   ("VI",  "Ishtar rechazada", "si", "Relieve de la Reina de la Noche"),
   ("VI",  "El Toro Celeste", "no", "placas de terracota, pendiente"),
   ("—",   "El héroe y las fieras", "si", "Relieve de Khorsabad · sello acadio"),
   ("VII–X","La muerte de Enkidu; el inframundo", "no", "sin obra conocida"),
   ("XI",  "El Diluvio", "si", "Tablilla XI, Biblioteca de Asurbanipal"),
  ]},
}

CSS = """
<title>Los Tres Libros</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Sala de museo: la colección vive sobre negro, como los cuadros que reproduce.
   Compromiso deliberado con un solo tema; todo color se pinta explícitamente. */
:root{
  --ground:#08090c; --surface:#101218; --surface-2:#161923; --sunken:#050608;
  --text:#eceef2; --dim:#9aa2b0; --mute:#6a7382;
  --line:rgba(255,255,255,.09); --line-warm:rgba(197,160,70,.22);
  --gold:#c5a046; --gold-lit:#dcbb64;
  --lapis:#5d88c4; --oxide:#c15236;
  --accent:var(--gold); --accent-lit:var(--gold-lit);
  --serif:'Cinzel',Georgia,serif;
  --body:'EB Garamond','Iowan Old Style',Georgia,serif;
  --mono:'IBM Plex Mono',ui-monospace,Menlo,monospace;
  --measure:66ch;
}
[data-libro="gilgamesh"]{--accent:var(--lapis);--accent-lit:#83a8dc}
[data-libro="iliada"]{--accent:var(--oxide);--accent-lit:#dd7355}

*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--text);
     font-family:var(--body);font-size:19px;line-height:1.62;
     -webkit-font-smoothing:antialiased}
a{color:var(--accent-lit);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.18)}
a:hover{border-bottom-color:currentColor}
:focus-visible{outline:2px solid var(--accent-lit);outline-offset:3px;border-radius:2px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

.wrap{max-width:1140px;margin:0 auto;padding:0 28px}

/* ---- cabecera ---- */
header{padding:64px 0 0;border-bottom:1px solid var(--line);
       background:linear-gradient(180deg,#0b0d12 0%,var(--ground) 100%)}
.eyebrow{font-family:var(--serif);font-size:.7rem;letter-spacing:.42em;
         text-transform:uppercase;color:var(--gold);margin:0 0 18px}
h1{font-family:var(--serif);font-weight:500;font-size:clamp(2.1rem,5.2vw,3.5rem);
   line-height:1.08;letter-spacing:.02em;margin:0 0 20px;text-wrap:balance}
.lede{max-width:var(--measure);color:var(--dim);font-size:1.12rem;margin:0 0 30px}
.lede em{color:var(--text);font-style:italic}

.cifras{display:flex;flex-wrap:wrap;gap:0;border-top:1px solid var(--line);
        margin-top:34px}
.cifra{flex:1 1 130px;padding:16px 20px 18px;border-right:1px solid var(--line)}
.cifra:last-child{border-right:0}
.cifra b{display:block;font-family:var(--mono);font-size:1.5rem;font-weight:500;
         color:var(--text);font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.cifra span{font-family:var(--serif);font-size:.62rem;letter-spacing:.2em;
            text-transform:uppercase;color:var(--mute)}

/* ---- navegación ---- */
nav{display:flex;gap:6px;flex-wrap:wrap;padding:26px 0 0}
.tab{background:none;border:0;border-bottom:2px solid transparent;
     color:var(--mute);font-family:var(--serif);font-size:.86rem;
     letter-spacing:.16em;text-transform:uppercase;padding:10px 16px 14px;
     cursor:pointer;transition:color .2s,border-color .2s}
.tab:hover{color:var(--text)}
.tab[aria-selected="true"]{color:var(--accent-lit);border-bottom-color:var(--accent-lit)}
.tab .n{font-family:var(--mono);font-size:.62rem;opacity:.6;margin-left:7px;
        font-variant-numeric:tabular-nums}

/* ---- panel de libro ---- */
.panel{display:none;padding:52px 0 90px}
.panel.on{display:block}
.intro{max-width:var(--measure);color:var(--dim);font-size:1.08rem;
       padding-left:20px;border-left:2px solid var(--accent);margin:0 0 54px}

/* ---- una obra ---- */
.obra{display:grid;grid-template-columns:340px 1fr;gap:38px;
      padding:38px 0;border-top:1px solid var(--line)}
.obra:first-of-type{border-top:0;padding-top:0}
@media (max-width:800px){.obra{grid-template-columns:1fr;gap:24px}}

.lamina{margin:0}
.lamina img{width:100%;height:auto;display:block;background:var(--sunken);
            border:1px solid var(--line)}
.lamina figcaption{font-family:var(--mono);font-size:.66rem;color:var(--mute);
                   margin-top:9px;line-height:1.5;word-break:break-word}

.num{font-family:var(--mono);font-size:.68rem;color:var(--accent);
     letter-spacing:.12em;display:block;margin-bottom:7px}
h3{font-family:var(--serif);font-weight:500;font-size:1.42rem;line-height:1.2;
   margin:0 0 4px;text-wrap:balance}
.autor{color:var(--dim);font-size:1.02rem;font-style:italic;margin:0 0 14px}
.ficha{font-family:var(--mono);font-size:.72rem;color:var(--mute);
       line-height:1.75;margin:0 0 16px;padding-bottom:16px;
       border-bottom:1px solid var(--line)}
.gancho{margin:0 0 18px;max-width:var(--measure)}

.acciones{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.btn{background:none;border:1px solid var(--line-warm);color:var(--dim);
     font-family:var(--serif);font-size:.7rem;letter-spacing:.14em;
     text-transform:uppercase;padding:8px 15px;cursor:pointer;
     transition:color .2s,border-color .2s}
.btn:hover{color:var(--accent-lit);border-color:var(--accent-lit)}
.ext{font-family:var(--serif);font-size:.7rem;letter-spacing:.14em;
     text-transform:uppercase;border:0;color:var(--mute);padding:8px 4px}
.ext:hover{color:var(--accent-lit)}
.ext .mp{font-family:var(--mono);letter-spacing:0;text-transform:none;
         font-size:.68rem;opacity:.75;margin-left:5px}

.mas{display:none;margin-top:24px;padding-top:22px;border-top:1px solid var(--line)}
.mas.on{display:block}
.mas h4{font-family:var(--serif);font-weight:500;font-size:.74rem;
        letter-spacing:.2em;text-transform:uppercase;color:var(--accent);
        margin:0 0 8px}
.mas p{margin:0 0 22px;max-width:var(--measure);color:#dcdfe6}
.mas p:last-child{margin-bottom:0}

/* ---- cobertura ---- */
.cob h2{font-family:var(--serif);font-weight:500;font-size:1.5rem;
        margin:52px 0 6px;letter-spacing:.02em}
.cob h2:first-child{margin-top:0}
.cob .sub{color:var(--dim);max-width:var(--measure);margin:0 0 22px;font-size:1.02rem}
.tabla{overflow-x:auto;border:1px solid var(--line)}
table{border-collapse:collapse;width:100%;min-width:600px;font-size:.94rem}
th{font-family:var(--serif);font-size:.64rem;letter-spacing:.18em;
   text-transform:uppercase;color:var(--mute);text-align:left;font-weight:400;
   padding:12px 16px;border-bottom:1px solid var(--line);background:var(--surface)}
td{padding:11px 16px;border-bottom:1px solid rgba(255,255,255,.05);
   vertical-align:top;color:var(--dim)}
tr:last-child td{border-bottom:0}
td:first-child{font-family:var(--mono);font-size:.78rem;color:var(--mute);
               white-space:nowrap;font-variant-numeric:tabular-nums}
td.pasaje{color:var(--text)}
.pip{display:inline-block;width:7px;height:7px;border-radius:50%;
     margin-right:9px;vertical-align:middle}
.pip.si{background:var(--accent)}
.pip.casi{background:none;box-shadow:inset 0 0 0 1.5px var(--accent)}
.pip.no{background:none;box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.22)}
.leyenda{display:flex;gap:22px;flex-wrap:wrap;font-family:var(--mono);
         font-size:.72rem;color:var(--mute);margin:16px 0 0}

/* ---- pie ---- */
footer{border-top:1px solid var(--line);background:var(--sunken);
       padding:44px 0 66px;color:var(--mute);font-size:.94rem}
footer p{max-width:var(--measure);margin:0 0 14px}
footer strong{color:var(--dim);font-weight:500}
</style>
"""

P = []
def w(s): P.append(s)

w(CSS)

# ---------- CABECERA ----------
tot_obras = sum(len(x) for _,_,x,_,_,_ in LIBROS)
con_img = 0
for _,_,ents,folder,_,_ in LIBROS:
    con_img += sum(1 for x in ents if os.path.exists(os.path.join(folder, x["files"][0])))
peso = sum(os.path.getsize(os.path.join(f, y))
           for _,_,ents,f,_,_ in LIBROS for x in ents for y in x["files"]
           if os.path.exists(os.path.join(f, y)))
mayor = max((ENLACES[k]["mp"] for k in ENLACES), default=0)

w(f"""
<header><div class="wrap">
  <p class="eyebrow">Catálogo de la colección</p>
  <h1>Los Tres Libros</h1>
  <p class="lede">Una colección de arte reunida en torno al <em>Génesis</em>, la <em>Epopeya de
  Gilgamesh</em> y la <em>Ilíada</em>: pintura, escultura, cerámica y arqueología, elegidas obra a
  obra y en la mayor resolución que existe de cada una. Esto es el catálogo — el texto y la ficha
  de cada pieza, con enlace al archivo original. Los másteres viven en local, algunos por encima de
  los doscientos megabytes.</p>
  <div class="cifras">
    <div class="cifra"><b>{con_img}</b><span>obras catalogadas</span></div>
    <div class="cifra"><b>3</b><span>libros</span></div>
    <div class="cifra"><b>{peso/1e6:.0f}&thinsp;MB</b><span>de originales</span></div>
    <div class="cifra"><b>{mayor:.0f}&thinsp;MP</b><span>la mayor imagen</span></div>
  </div>
  <nav role="tablist">""")
for i,(cid,nom,ents,folder,_,_) in enumerate(LIBROS):
    n = sum(1 for x in ents if os.path.exists(os.path.join(folder, x["files"][0])))
    w(f'<button class="tab" role="tab" id="t-{cid}" aria-controls="p-{cid}" '
      f'aria-selected="{"true" if i==0 else "false"}" data-t="{cid}">{e(nom)}'
      f'<span class="n">{n}</span></button>')
w('<button class="tab" role="tab" id="t-cob" aria-controls="p-cob" aria-selected="false" '
  'data-t="cob">Cobertura</button>')
w('</nav></div></header><main class="wrap">')

# ---------- LIBROS ----------
for i,(cid,nom,ents,folder,pre,intro) in enumerate(LIBROS):
    w(f'<section class="panel{" on" if i==0 else ""}" id="p-{cid}" role="tabpanel" '
      f'aria-labelledby="t-{cid}" data-libro="{cid}">')
    w(f'<p class="intro">{e(intro)}</p>')
    n = 0
    for it in ents:
        f0 = it["files"][0]
        if not os.path.exists(os.path.join(folder, f0)): continue
        n += 1
        uri = datauri(folder, f0)
        key = f"{folder}/{f0}"
        lk  = ENLACES.get(key)
        w('<article class="obra">')
        w('<figure class="lamina">')
        if uri: w(f'<img src="{uri}" alt="{e(it["title"])} — {e(it["artist"])}" loading="lazy">')
        w(f'<figcaption>{e(f0)}</figcaption></figure>')
        w('<div>')
        w(f'<span class="num">{pre.upper()} {n:02d}</span>')
        w(f'<h3>{e(it["title"])}</h3>')
        w(f'<p class="autor">{e(it["artist"])}</p>')
        w(f'<p class="ficha">{e(it["meta"])}</p>')
        w(f'<p class="gancho">{e(it.get("snippet") or it["analysis"][:200])}</p>')
        w('<div class="acciones">')
        w(f'<button class="btn" data-mas="{cid}-{n}">Análisis completo</button>')
        if it.get("wikiUrl"):
            w(f'<a class="ext" href="{e(it["wikiUrl"])}" target="_blank" rel="noopener">Wikipedia</a>')
        if lk:
            w(f'<a class="ext" href="{e(lk["commons"])}" target="_blank" rel="noopener">Commons'
              f'<span class="mp">{lk["w"]}&times;{lk["h"]}</span></a>')
            w(f'<a class="ext" href="{e(lk["original"])}" target="_blank" rel="noopener">'
              f'Original<span class="mp">{lk["mp"]:.1f} MP</span></a>')
        w('</div>')
        w(f'<div class="mas" id="mas-{cid}-{n}">')
        for h, k in (("Lo que hace que destaque","analysis"),
                     ("Contexto histórico","history"),
                     ("Autoría y procedencia","bio")):
            if it.get(k): w(f'<h4>{h}</h4><p>{e(it[k])}</p>')
        w('</div></div></article>')
    w('</section>')

# ---------- COBERTURA ----------
w('<section class="panel cob" id="p-cob" role="tabpanel" aria-labelledby="t-cob">')
w('<p class="intro">La colección crece por pasajes que faltan, no por acumulación de cuadros '
  'sueltos. Esta es la cuenta de qué capítulos, cantos y tablillas están representados y cuáles '
  'siguen vacíos — con el candidato concreto para cada hueco.</p>')
for nom, d in COBERTURA.items():
    w(f'<h2>{e(nom)}</h2><p class="sub">{e(d["sub"])}</p><div class="tabla"><table><thead><tr>')
    for c in d["cols"]: w(f'<th>{e(c)}</th>')
    w('</tr></thead><tbody>')
    for cap, pas, st, obra in d["filas"]:
        w(f'<tr><td>{e(cap)}</td><td class="pasaje"><span class="pip {st}"></span>{e(pas)}</td>'
          f'<td>{e(obra)}</td></tr>')
    w('</tbody></table></div>')
w('<p class="leyenda"><span><span class="pip si"></span>en la colección</span>'
  '<span><span class="pip casi"></span>descargando</span>'
  '<span><span class="pip no"></span>hueco</span></p>')
w('</section>')

w('</main><footer><div class="wrap">')
w('<p><strong>Sobre las imágenes.</strong> Las que ves aquí son vistas previas: un artefacto debe '
  'caber entero en 16&nbsp;MB y no puede cargar imágenes de dominios externos, así que van '
  'incrustadas y reducidas. El enlace <em>Original</em> de cada obra lleva al archivo completo en '
  'Wikimedia Commons — hasta 30.000&nbsp;×&nbsp;17.078&nbsp;px en el caso de <em>El jardín de las '
  'delicias</em>.</p>')
w('<p><strong>Criterio de selección.</strong> Para una pintura se prefiere siempre la reproducción '
  'cenital del museo aunque tenga menos resolución que la foto que alguien tomó en la sala; para '
  'escultura y arqueología ocurre lo contrario, porque ahí la fotografía es la única opción posible.</p>')
w('</div></footer>')

w("""
<script>
(function(){
  var tabs=[].slice.call(document.querySelectorAll('.tab'));
  function ir(id){
    tabs.forEach(function(t){
      var on=t.dataset.t===id;
      t.setAttribute('aria-selected',on?'true':'false');
      var p=document.getElementById('p-'+t.dataset.t);
      if(p)p.classList.toggle('on',on);
    });
    document.documentElement.dataset.libro=(id==='cob'?'genesis':id);
    window.scrollTo({top:0,behavior:'smooth'});
  }
  tabs.forEach(function(t){t.addEventListener('click',function(){ir(t.dataset.t);});});
  document.addEventListener('click',function(ev){
    var b=ev.target.closest('.btn[data-mas]'); if(!b)return;
    var m=document.getElementById('mas-'+b.dataset.mas); if(!m)return;
    var on=m.classList.toggle('on');
    b.textContent=on?'Ocultar análisis':'Análisis completo';
  });
})();
</script>
""")

out = os.path.join(TMP, "los-tres-libros.html")
io.open(out,"w",encoding="utf-8").write("\n".join(P))
print(f"escrito {out}  ·  {os.path.getsize(out)/1e6:.1f} MB  ·  {con_img} obras")
