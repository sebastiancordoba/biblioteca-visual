# -*- coding: utf-8 -*-
"""Sección Mapa: un solo lienzo navegable que revela detalle al acercarse.

Ciudad -> museo -> obra. La agrupación se recalcula en el navegador según la escala,
así que el mismo dato sirve para todos los niveles de acercamiento.
"""
import html, io, json, os, sys
AQUI=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
sys.path.insert(0, os.path.join(ROOT,"herramientas")); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
from libros import todos as _libros
_REG = _libros()
from cronologia import ordenar, etiqueta
from mapa import MUSEOS, museo_de
from geo import anillos, proyectar, lineas, proyectar_lineas

# Mundo entero en Mercator, para poder darle la vuelta: el lienzo se repite en horizontal
# y el desplazamiento hacia el este continúa por el oeste sin costura. El recorte de
# latitud (-56 a 80) deja fuera la Antártida y el Ártico alto, y da al lienzo una
# proporción de 1,74, prácticamente la del marco (16/9 = 1,78): así la vista del mundo
# entero lo llena sin bandas negras.
BB=(-180,-56,180,80); K=5.5
PAIS={"Ciudad del Vaticano":"Vaticano","Florencia":"Italia","Venecia":"Italia","Vicenza":"Italia","Cerveteri":"Italia",
 "Viena":"Austria","París":"Francia","Aix-en-Provence":"Francia","Londres":"Reino Unido",
 "Compton, Surrey":"Reino Unido","Newcastle upon Tyne":"Reino Unido","Edimburgo":"Reino Unido",
 "Oxford":"Reino Unido","Madrid":"España","San Lorenzo de El Escorial":"España","Praga":"Chequia",
 "San Petersburgo":"Rusia","Moscú":"Rusia","Sérguiev Posad":"Rusia","Múnich":"Alemania","Schwerin":"Alemania",
 "Potsdam":"Alemania","Atenas":"Grecia","Corfú":"Grecia","Argólida":"Grecia",
 "Hisarlik, Çanakkale":"Turquía","Bagdad":"Irak","Sulaymaniyah":"Irak",
 "Ciudad de México":"México","Puebla":"México","Damasco":"Siria","Besanzón":"Francia","Kassel":"Alemania","Berlín":"Alemania","Estambul":"Turquía","Adana":"Turquía","Oasis de Jarga":"Egipto","El Cairo":"Egipto","Beit Alfa":"Israel",
 "Ciudad Vieja":"Jerusalén","Buenos Aires":"Argentina",
 "Bruselas":"Bélgica","Varsovia":"Polonia",
 "Nueva York":"Estados Unidos","Washington D.C.":"Estados Unidos","Fort Worth":"Estados Unidos",
 "New Haven":"Estados Unidos","Cambridge (Massachusetts)":"Estados Unidos","Róterdam":"Países Bajos"}

# El continente se deduce del país, y el mapa activa solo los botones con obras: si
# mañana entra una pieza en El Cairo, África se enciende sola.
CONTINENTE={"Vaticano":"Europa","Italia":"Europa","Austria":"Europa","Francia":"Europa",
 "Reino Unido":"Europa","España":"Europa","Chequia":"Europa","Rusia":"Europa",
 "Bélgica":"Europa","Polonia":"Europa",
 "Grecia":"Europa","Alemania":"Europa","Países Bajos":"Europa","Portugal":"Europa",
 "Irak":"Asia","Jerusalén":"Asia","Siria":"Asia","Turquía":"Asia","Israel":"Asia","Irán":"Asia",
 "Estados Unidos":"América del Norte","México":"América del Norte","Canadá":"América del Norte",
 "Brasil":"América del Sur","Argentina":"América del Sur","Perú":"América del Sur",
 "Egipto":"África","Marruecos":"África","Sudáfrica":"África","Túnez":"África",
 "Australia":"Oceanía","Nueva Zelanda":"Oceanía"}

# Misma etiqueta que build.py (el nombre corto) para que el orden, y con él los índices,
# coincidan; la carpeta solo se usa para comprobar que la imagen existe.
CARPETA = {l["corto"]: l["carpeta"] for l, ents in _REG}
filas=ordenar(*[(l["corto"], ents) for l, ents in _REG if ents])
_ENL=json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"datos","enlaces.json"),encoding="utf-8"))
# En disco o enlazada en Commons: la misma regla que inject.py.
filas=[(a,l,it) for a,l,it in filas
       if os.path.exists(os.path.join(CARPETA[l],it["files"][0])) or f'{CARPETA[l]}/{it["files"][0]}' in _ENL]

paths,W,H,xy = proyectar(anillos(os.path.join(AQUI,"datos","land50.geojson"),BB), BB, K)

# Fronteras en dos niveles. En los Balcanes o el Benelux hay decenas de tramos cortos
# que a escala mundial se convierten en un garabato ilegible, mientras que en Siberia
# los tramos son largos y no estorban. Separarlos por longitud quita el 94% del ruido
# donde molesta y conserva casi todo donde no: los cortos solo aparecen al acercarse.
UMBRAL_FRONTERA = 35
fr = proyectar_lineas(lineas(os.path.join(AQUI,"datos","fronteras50.geojson"), BB), BB, K)
fr_principales = [d for d,l in fr if l >= UMBRAL_FRONTERA]
fr_secundarias = [d for d,l in fr if l <  UMBRAL_FRONTERA]
print(f"fronteras: {len(fr_principales)} principales + {len(fr_secundarias)} secundarias · "
      f"{sum(len(d) for d in fr_principales+fr_secundarias)/1000:.0f} KB")

sedes={}
sin_sede=[]   # obras en colección particular: no hay sede pública que situar
for i,(a,l,it) in enumerate(filas):
    k=museo_de(it)
    if not k:
        sin_sede.append(it["title"]); continue
    if k not in sedes:
        nom,ciu,lat,lon=MUSEOS[k]
        x,y=xy(lon,lat)
        sedes[k]={"k":k,"nombre":nom,"ciudad":ciu,"pais":PAIS[ciu],
                  "cont":CONTINENTE.get(PAIS[ciu],"Otros"),
                  # Cuatro decimales, no uno: los museos de una misma ciudad distan centésimas de píxel
                  # de lienzo (el Louvre y Orsay, 0,061), así que redondear a 0,1 los apilaba en el
                  # mismo punto y hacía imposible respetar su disposición real.
                  "x":round(x,4),"y":round(y,4),"obras":[]}
    sedes[k]["obras"].append({"i":i,"t":it["title"],"a":etiqueta(a),"libro":l,
                              "autor":it["artist"]})
lista=sorted(sedes.values(),key=lambda s:(-len(s["obras"]),s["ciudad"]))
paises=len({s["pais"] for s in lista})
print(f"{sum(len(s['obras']) for s in lista)} obras · {len(lista)} sedes · {paises} países")
# Las cifras que se escriben en los rótulos salen de aquí, no a mano: antes estaban
# copiadas en build3.py y se quedaron en 34 sedes cuando ya había 41.
io.open(os.path.join(TMP,'cifras_mapa.py'),'w',encoding='utf-8').write(repr(
    {'obras': sum(len(s['obras']) for s in lista), 'sedes': len(lista), 'paises': paises}))
print(f"lienzo {W:.0f}×{H:.0f} px · {len(paths)} anillos de costa")

# rectángulo de Europa y Próximo Oriente, donde está la mayoría; el navegador lo
# encaja en el marco según su proporción real
ex0,ey0=xy(-12,63); ex1,ey1=xy(50,30)
EUROPA={"x0":round(ex0,1),"y0":round(ey0,1),"x1":round(ex1,1),"y1":round(ey1,1)}

def ret():
    out=[]
    lo=BB[0]-BB[0]%10+10
    while lo<BB[2]:
        a,b=xy(lo,BB[3]); c,d=xy(lo,BB[1])
        out.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c:.0f}" y2="{d:.0f}"/>'); lo+=10
    la=BB[1]-BB[1]%10+10
    while la<BB[3]:
        a,b=xy(BB[0],la); c,d=xy(BB[2],la)
        out.append(f'<line x1="{a:.0f}" y1="{b:.0f}" x2="{c:.0f}" y2="{d:.0f}"/>'); la+=10
    return "".join(out)

PANEL=f'''    <div id="mapa-gallery" class="tab-content">
      <div class="mapa-wrap">
        <div class="mapa-marco" id="mapaMarco">
          <svg class="mapa-svg" id="mapaSvg" viewBox="0 0 {W:.0f} {H:.0f}"
               role="application" aria-label="Mapa navegable de las sedes de la colección">
            <defs>
              <!-- El mundo se define una sola vez; cada vuelta es un <use> desplazado. -->
              <!-- Color y trazo van como atributos de presentación, no por CSS: el
                   contenido que <use> clona no recibe las reglas de la hoja de estilos,
                   y sin ellos los trazados salen con el relleno negro por defecto de SVG
                   y sin contorno. El grosor lo ajusta el guion según la escala. -->
              <g id="mundoDef">
                <g class="tierra" id="capaTierra" fill="#2c3444" stroke="rgba(197,160,70,.5)"
                   stroke-linejoin="round">{"".join(f'<path d="{d}"/>' for d in paths)}</g>
                <g class="fronteras" id="frPrin" fill="none" stroke="#c3d0e8"
                   stroke-linecap="round">{"".join(f'<path d="{d}"/>' for d in fr_principales)}</g>
                <g class="fronteras" id="frSec" fill="none" stroke="#c3d0e8"
                   stroke-linecap="round">{"".join(f'<path d="{d}"/>' for d in fr_secundarias)}</g>
              </g>
            </defs>
            <g id="capaMundo"></g>
            <g id="capaEnlaces"></g>
            <g id="capaObras"></g>
            <g id="capaSedes"></g>
          </svg>
          <div class="mapa-ctrl">
            <button type="button" id="mZoomIn"  aria-label="Acercar">+</button>
            <button type="button" id="mZoomOut" aria-label="Alejar">&minus;</button>
          </div>
          <div class="mapa-cont" id="mapaContinentes" role="group" aria-label="Encuadrar un continente"></div>
          <div class="mapa-pista" id="mapaPista">Arrastra o usa W A S D · rueda o + / − para acercar · 0 vuelve a Europa</div>
          <div class="mapa-tarjeta" id="mapaTarjeta" hidden></div>
        </div>
        <aside class="mapa-lado">
          <div id="mapaBuscador"></div>
          <div class="lado-tog" role="tablist" aria-label="Ver por">
            <button type="button" class="tog-btn activo" id="togSedes" role="tab" aria-selected="true">Sedes</button>
            <button type="button" class="tog-btn" id="togLibros" role="tab" aria-selected="false">Libros</button>
          </div>
          <p class="mapa-nota" id="mapaNota">Ordenadas por número de obras. Al elegir una, el mapa vuela hasta ella y despliega lo que guarda.</p>
          {{NOTA_SIN_SEDE}}
          <ol class="sede-lista" id="sedeLista"></ol>
        </aside>
      </div>
      <div class="sede-detalle" id="sedeDetalle"></div>
    </div>
'''
NOTA_SIN_SEDE = ("" if not sin_sede else
  '<p class="mapa-aparte">' +
  ("1 obra está" if len(sin_sede)==1 else f"{len(sin_sede)} obras están") +
  " en colección particular, sin sede pública que situar en el mapa: " +
  ", ".join(f"<em>{x}</em>" for x in sin_sede) + ".</p>")
PANEL = PANEL.replace("{NOTA_SIN_SEDE}", NOTA_SIN_SEDE)

DATOS=("    const SEDES = "+json.dumps(lista,ensure_ascii=False)+";\n"
       # el orden del registro, para que la lista de libros del mapa no dependa de las sedes
       +"    const ORDEN_LIBROS = "+json.dumps([l["corto"] for l,_ in _REG],ensure_ascii=False)+";\n"
       "    const MAPA_EUROPA = "+json.dumps(EUROPA)+";\n"
       f"    const MAPA_W = {W:.0f}, MAPA_H = {H:.0f};\n")
io.open(TMP+"/mapa_panel.html","w",encoding="utf-8").write(PANEL)
io.open(TMP+"/mapa_datos.js","w",encoding="utf-8").write(DATOS)
io.open(TMP+"/paises.txt","w").write(str(paises))
io.open(TMP+"/sin_sede.txt","w",encoding="utf-8").write("\n".join(sin_sede))
if sin_sede: print("en colección particular, sin sede pública:", ", ".join(sin_sede))
print(f"panel {len(PANEL)/1000:.0f} KB · datos {len(DATOS)/1000:.0f} KB")
