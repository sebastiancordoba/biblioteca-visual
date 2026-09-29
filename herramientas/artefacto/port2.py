# -*- coding: utf-8 -*-
import base64, io, json, os, re, sys, urllib.parse
AQUI=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
os.chdir(ROOT)
s=io.open("index.html",encoding="utf-8").read()

head=s[s.index("<head>")+6:s.index("</head>")]
body=s[s.index("<body>")+6:s.index("</body>")]
head=re.sub(r'\s*<meta charset[^>]*>','',head)
head=re.sub(r'\s*<meta name="viewport"[^>]*>','',head)
head=head.replace("Biblioteca Visual","Los Tres Libros")
doc=head+"\n"+body

# ---------- 1. enlaces al original, dentro de los datos de cada obra ----------
ENL=json.load(io.open(os.path.join(AQUI,"datos","enlaces.json"),encoding="utf-8"))

def corchete(t,i):
    d=0;j=i;instr=False;esc=False
    while j<len(t):
        c=t[j]
        if instr:
            if esc:esc=False
            elif c=="\\":esc=True
            elif c=='"':instr=False
        else:
            if c=='"':instr=True
            elif c=="[":d+=1
            elif c=="]":
                d-=1
                if d==0:return j+1
        j+=1
    raise ValueError

def leer(libro,campo):
    k=doc.index(f"BOOKS.{libro}.{campo} = [")
    lb=doc.index("[",k); fin=corchete(doc,lb)
    return lb,fin,json.loads(doc[lb:fin])

añadidos=0
for libro in ("genesis","gilgamesh","iliada"):
    _,_,groups=leer(libro,"groups")
    lb,fin,details=leer(libro,"details")
    for i,d in enumerate(details):
        src=groups[i][0]["src"]              # ./Libro/archivo.jpg
        rel=src[2:]
        lk=ENL.get(rel)
        if lk:
            d["commons"]=lk["commons"]; d["orig"]=lk["original"]
            d["mp"]=f'{lk["mp"]:.1f} MP'; d["px"]=f'{lk["w"]}×{lk["h"]}'
            añadidos+=1
    doc=doc[:lb]+json.dumps(details,ensure_ascii=False,indent=2).replace("\n","\n    ")+doc[fin:]
print("obras con enlace al original:",añadidos)

# ---------- 2. el renderizador emite esos enlaces ----------
viejo="""        const wiki = d.wikiUrl ? `
                <a href="${esc(d.wikiUrl)}" target="_blank" rel="noopener" class="wiki-link-btn" title="Ver en Wikipedia">Wikipedia ${SVG_WIKI}</a>` : '';"""
nuevo="""        const wiki = d.wikiUrl ? `
                <a href="${esc(d.wikiUrl)}" target="_blank" rel="noopener" class="wiki-link-btn" title="Ver en Wikipedia">Wikipedia ${SVG_WIKI}</a>` : '';
        // enlace al archivo original en Commons: la vista de esta página es una previa
        const orig = d.orig ? `
                <a href="${esc(d.orig)}" target="_blank" rel="noopener" class="wiki-link-btn orig-link" title="Archivo original ${esc(d.px)} en Wikimedia Commons">Original <span class="mp-tag">${esc(d.mp)}</span> ${SVG_WIKI}</a>` : '';"""
assert viejo in doc; doc=doc.replace(viejo,nuevo,1)
doc=doc.replace("""                </button>${wiki}""","""                </button>${wiki}${orig}""",1)
print("renderizador parcheado")
io.open(os.path.join(TMP,"step2.part"),"w",encoding="utf-8").write(doc)
