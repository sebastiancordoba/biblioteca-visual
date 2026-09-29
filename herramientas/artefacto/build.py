# -*- coding: utf-8 -*-
"""Construye la versión publicable a partir del index.html real.

No reescribe el visor: cambia las rutas de imagen por vistas previas incrustadas
(un artefacto no puede cargar archivos externos), y añade tres cosas que solo
tienen sentido en la versión compartida: enlace al archivo original, cronología
conjunta de todos los libros y mapa de cobertura.
"""
import base64, html, io, json, os, re, sys
AQUI=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
sys.path.insert(0, os.path.join(ROOT,"herramientas")); os.chdir(ROOT)
from libros import todos as _libros
_REG = _libros()
from cronologia import ordenar, etiqueta
e=lambda t: html.escape(str(t),quote=True)

s=io.open("index.html",encoding="utf-8").read()
head=s[s.index("<head>")+6:s.index("</head>")]
body=s[s.index("<body>")+6:s.index("</body>")]
head=re.sub(r'\s*<meta charset[^>]*>','',head)
head=re.sub(r'\s*<meta name="viewport"[^>]*>','',head)
head=head.replace("<title>Biblioteca Visual</title>","<title>Los Tres Libros</title>")
doc=head+"\n"+body

ENL=json.load(io.open(os.path.join(AQUI,"datos","enlaces.json"),encoding="utf-8"))
# Autor y licencia de cada imagen (herramientas/creditos.py): las CC BY y CC BY-SA obligan a
# citarlos, así que el visor lo muestra vista a vista.
_cr=os.path.join(AQUI,"datos","creditos.json")
CRED=json.load(io.open(_cr,encoding="utf-8")) if os.path.exists(_cr) else {}

def cierre(t,i,ab="[",ce="]"):
    d=0;j=i;instr=False;esc=False
    while j<len(t):
        c=t[j]
        if instr:
            if esc:esc=False
            elif c=="\\":esc=True
            elif c=='"':instr=False
        else:
            if c=='"':instr=True
            elif c==ab:d+=1
            elif c==ce:
                d-=1
                if d==0:return j+1
        j+=1
    raise ValueError

def leer(campo,libro):
    k=doc.index(f"BOOKS.{libro}.{campo} = [")
    lb=doc.index("[",k); return lb,cierre(doc,lb)

# ---------- 1. enlaces al original dentro de los datos ----------
DATOS={}
for libro in [l["id"] for l, ents in _REG if ents]:
    lbg,fing=leer("groups",libro); groups=json.loads(doc[lbg:fing])
    lbd,find=leer("details",libro); details=json.loads(doc[lbd:find])
    for i,d in enumerate(details):
        rel=groups[i][0]["src"][2:]
        lk=ENL.get(rel)
        if lk:
            d["orig"]=lk["original"]; d["mp"]=f'{lk["mp"]:.1f} MP'; d["px"]=f'{lk["w"]}×{lk["h"]}'
    DATOS[libro]=(details,groups)
    doc=doc[:lbd]+json.dumps(details,ensure_ascii=False,indent=2).replace("\n","\n    ")+doc[find:]
    for grp in groups:
        for v in grp:
            c=CRED.get(v["src"][2:])
            if c: v["cred"]={"a":c["autor"],"au":c["autor_url"],"l":c["licencia"],"lu":c["licencia_url"],"f":c["archivo"]}
    lbg,fing=leer("groups",libro)
    doc=doc[:lbg]+json.dumps(groups,ensure_ascii=False,indent=2).replace("\n","\n    ")+doc[fing:]

# ---------- 2. cronología conjunta ----------
# Etiqueta = nombre corto del libro. build_mapa.py usa EXACTAMENTE la misma para ordenar,
# porque el mapa guarda índices de esta cronología: si las dos listas se ordenaran distinto,
# cada sede apuntaría a obras de otra.
LIB={l["id"]:(l["corto"],ents) for l,ents in _REG if ents}
porTitulo={}
for cid,(nom,_) in LIB.items():
    det,grp=DATOS[cid]
    for i,d in enumerate(det): porTitulo.setdefault((nom,d["title"],d["artist"]),(d,grp[i]))

filas=ordenar(*[(nom,ents) for nom,ents in LIB.values()])
cd,cg=[],[]
for a,nom,it in filas:
    par=porTitulo.get((nom,it["title"],it["artist"]))
    if not par: continue
    d,g=par
    nd=dict(d); nd["epoca"]=f'{etiqueta(a)} · {nom}'
    cd.append(nd); cg.append(g)
print("cronología:",len(cd),"obras, de",etiqueta(filas[0][0]),"a",etiqueta(filas[-1][0]))

import re as _re
_m=_re.search(r"^ *let currentBook = '[a-z]+';", doc, _re.M)
assert _m, 'no se encontró la declaración de currentBook'
anc=_m.group(0)
BLOQUE=(
"    /* La cronología funde todos los libros en una sola secuencia; reutiliza las mismas\n"
"       entradas de IMG, así que no duplica ni un byte de imagen. */\n"
"    BOOKS.cronologia = {\n"
"      tag: 'Todos los libros a la vez',\n"
"      title: 'Cronología',\n"
"      sub: 'Las obras de las tres colecciones en una sola secuencia, del Vaso de Warka al Triunfo de Aquiles. Entre el Laocoonte y la Trinidad de Rubliov median casi mil quinientos años sin una sola imagen.',\n"
"      firstTab: 'cronologia-gallery',\n"
"      headings: ['Lo que hace que destaque', 'Contexto histórico', 'Autoría y procedencia'],\n"
"      details: " + json.dumps(cd,ensure_ascii=False,indent=2).replace("\n","\n      ") + ",\n"
"      groups: "  + json.dumps(cg,ensure_ascii=False,indent=2).replace("\n","\n      ") + "\n"
"    };\n\n"
"    /* La cobertura no es un libro: sin obras, su grilla no existe y el renderizador sale solo. */\n"
"    BOOKS.cobertura = {\n"
"      tag: 'Estado de la colección',\n"
"      title: 'Capítulos, cantos y tablillas',\n"
"      sub: 'Qué pasajes están representados y cuáles siguen vacíos, con el candidato concreto para cada hueco.',\n"
"      firstTab: 'cobertura-gallery', details: [], groups: []\n"
"    };\n\n")
assert anc in doc; doc=doc.replace(anc, BLOQUE+anc, 1)
io.open(os.path.join(TMP,"b1.part"),"w",encoding="utf-8").write(doc)
print("paso 1-2 ok")
