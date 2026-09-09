# -*- coding: utf-8 -*-
import base64, io, os, re
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
doc=io.open(os.path.join(TMP,"step3.part"),encoding="utf-8").read()
cache={}; faltan=set()
def sub(m):
    rel=m.group(1)
    if rel not in cache:
        p=os.path.join(TH, rel.replace("/","__"))
        if not os.path.exists(p):
            faltan.add(rel); return m.group(0)
        cache[rel]="data:image/jpeg;base64,"+base64.b64encode(open(p,"rb").read()).decode()
    return cache[rel]
doc,n=re.subn(r'\./((?:Génesis|Gilgamesh|Ilíada)/[^\'"]+\.jpg)', sub, doc)
out=os.path.join(TMP,"los-tres-libros.html")
io.open(out,"w",encoding="utf-8").write(doc)
mb=os.path.getsize(out)/1e6
print(f"rutas sustituidas: {n} · distintas: {len(cache)} · sin previa: {sorted(faltan) or 'ninguna'}")
print(f"archivo final: {mb:.1f} MB  ({'OK, cabe en 16 MB' if mb<15 else 'DEMASIADO GRANDE'})")
