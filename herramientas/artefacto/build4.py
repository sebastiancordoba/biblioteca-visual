# -*- coding: utf-8 -*-
import base64, io, os, re
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))))
from libros import PATRON_RUTA_COMILLAS   # carpetas de todos los libros, del registro
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"); TH=os.path.join(TMP,"th2")
doc=io.open(os.path.join(TMP,"b3.part"),encoding="utf-8").read()

CSS = """
    /* ---- añadidos de la versión publicable ---- */
    .orig-link .mp-tag{font-family:var(--font-sans);font-size:.62rem;opacity:.72;
      font-variant-numeric:tabular-nums;margin:0 2px}
    .zoom-scale-text.sobre-previa{color:var(--accent-gold)}

    /* ---- cobertura ---- */
    .cobertura{max-width:1000px;margin:0 auto}
    .cobertura h2{font-family:var(--font-serif);color:var(--text-title);font-weight:500;
      font-size:1.35rem;letter-spacing:.5px;margin:44px 0 6px}
    .cobertura h2:first-child{margin-top:0}
    .credito{font-size:.72rem;color:var(--text-muted);margin-top:14px;line-height:1.5}
    .credito a{color:var(--text-muted);text-decoration:underline;text-underline-offset:2px}
    .credito a:hover{color:var(--accent-gold)}
    .cob-sub{color:var(--text-muted);font-size:.92rem;max-width:64ch;margin:0 0 18px;font-weight:300}
    .cob-tabla{overflow-x:auto;border:1px solid var(--border-subtle);border-radius:4px}
    .cob-tabla table{border-collapse:collapse;width:100%;min-width:620px}
    .cob-tabla th{font-family:var(--font-serif);font-size:.62rem;letter-spacing:2px;
      text-transform:uppercase;color:var(--text-muted);text-align:left;font-weight:400;
      padding:12px 16px;background:var(--bg-surface);border-bottom:1px solid var(--border-subtle)}
    .cob-tabla td{padding:11px 16px;border-bottom:1px solid rgba(255,255,255,.05);
      vertical-align:top;color:var(--text-body);font-size:.88rem}
    .cob-tabla tr:last-child td{border-bottom:0}
    .cob-tabla td:first-child{font-size:.78rem;color:var(--text-muted);white-space:nowrap;
      font-variant-numeric:tabular-nums}
    .cob-tabla td.pasaje{color:var(--text-title)}
    .pip{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:10px;vertical-align:middle}
    .pip.si{background:var(--accent-gold)}
    .pip.casi{box-shadow:inset 0 0 0 1.5px var(--accent-gold)}
    .pip.no{box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.24)}
    .cob-leyenda{display:flex;gap:24px;flex-wrap:wrap;margin:18px 0 0;font-size:.76rem;color:var(--text-muted)}

    /* ---- mapa navegable ---- */
    .mapa-wrap{display:grid;grid-template-columns:1fr 300px;gap:26px;align-items:start}
    @media (max-width:900px){.mapa-wrap{grid-template-columns:1fr}}
    .mapa-marco{position:relative;border:1px solid var(--border-subtle);border-radius:4px;
      background:#131722;overflow:hidden;aspect-ratio:16/9;cursor:grab;
      touch-action:none;user-select:none}
    .mapa-marco.arrastrando{cursor:grabbing}
    .mapa-svg{display:block;width:100%;height:100%}
    /* El color de la costa y de las fronteras NO se define aquí, sino como atributos de
       presentación en el propio SVG: el contenido que <use> clona para repetir el mundo no
       recibe las reglas de esta hoja, y confiar en ellas dejaba la tierra en negro y las
       fronteras sin trazo. Estas reglas quedan solo como respaldo, con los mismos valores. */
    .mapa-svg .ret line{stroke:rgba(255,255,255,.10)}
    .mapa-svg .tierra path{fill:#2c3444;stroke:rgba(197,160,70,.5);stroke-linejoin:round}
    .mapa-svg .fronteras path{fill:none;stroke:#c3d0e8;stroke-linecap:round}

    .sede{cursor:pointer}
    .sede .halo{fill:none;stroke:var(--accent-gold);opacity:0;transition:opacity .18s}
    .sede .pt{fill:#0b0d12;stroke:var(--accent-gold);opacity:1;transition:fill .18s,stroke .18s}
    .sede.grupo .pt{fill:rgba(197,160,70,.16)}
    .sede .pt-n{fill:var(--accent-gold);text-anchor:middle;font-family:var(--font-sans);
      font-weight:600;pointer-events:none;font-variant-numeric:tabular-nums}
    .sede:hover .pt,.sede:focus-visible .pt{fill:var(--accent-gold);stroke:var(--accent-gold-hover)}
    .sede:hover .pt-n,.sede:focus-visible .pt-n{fill:#0a0b0e}
    .sede:hover .halo,.sede:focus-visible .halo{opacity:.6}
    .sede.sel .pt{fill:var(--accent-gold)}
    .sede.sel .pt-n{fill:#0a0b0e}
    .sede.sel .halo{opacity:.85}
    .sede:focus{outline:none}

    .hilo{stroke:rgba(197,160,70,.4);vector-effect:non-scaling-stroke}
    .hilo-sede{stroke:rgba(197,160,70,.55);stroke-dasharray:3 2.5}
    /* Etiqueta de cada museo cuando una ciudad se despliega en abanico. */
    .sede-etq{fill:var(--text-body);text-anchor:middle;font-family:var(--font-sans);
      font-weight:500;pointer-events:none;paint-order:stroke;
      stroke:rgba(8,9,12,.9);stroke-width:2.5px;vector-effect:non-scaling-stroke}
    .sede-etq.der{text-anchor:start}.sede-etq.izq{text-anchor:end}
    .sede-abanico:hover .sede-etq,.sede-abanico.sel .sede-etq{fill:var(--accent-gold-hover)}
    .obra-pin{cursor:pointer}
    .obra-pin .marco{fill:none;stroke:rgba(197,160,70,.55);vector-effect:non-scaling-stroke;
      transition:stroke .18s}
    .obra-pin:hover .marco,.obra-pin:focus-visible .marco{stroke:var(--accent-gold-hover);
      stroke-width:2px}
    .obra-pin:focus{outline:none}

    .mapa-ctrl{position:absolute;top:12px;right:12px;display:flex;flex-direction:column;gap:5px;z-index:3}
    .mapa-ctrl button{background:rgba(10,11,14,.86);border:1px solid var(--border-subtle);
      color:var(--text-body);font-family:var(--font-serif);font-size:.68rem;letter-spacing:1.2px;
      padding:6px 9px;min-width:34px;cursor:pointer;border-radius:3px;transition:color .2s,border-color .2s}
    .mapa-ctrl button:hover{color:var(--accent-gold);border-color:var(--accent-gold)}
    /* Botones por continente: los que no tienen obras quedan apagados, no ocultos, para
       que se vea que la colección aún no llega allí. */
    .mapa-cont{position:absolute;top:12px;left:12px;z-index:3;display:flex;gap:4px;
      flex-wrap:wrap;max-width:calc(100% - 90px)}
    .mapa-cont button{background:rgba(10,11,14,.86);border:1px solid var(--border-subtle);
      color:var(--text-body);font-family:var(--font-serif);font-size:.64rem;letter-spacing:1.1px;
      padding:5px 9px;cursor:pointer;border-radius:3px;transition:color .2s,border-color .2s}
    .mapa-cont button:hover:not(:disabled){color:var(--accent-gold);border-color:var(--accent-gold)}
    .mapa-cont button:disabled{color:rgba(255,255,255,.16);border-color:rgba(255,255,255,.06);
      cursor:default}

    .mapa-pista{position:absolute;left:12px;bottom:11px;z-index:3;font-size:.68rem;
      color:var(--text-muted);background:rgba(10,11,14,.8);padding:5px 10px;border-radius:3px;
      pointer-events:none;letter-spacing:.2px}

    .mapa-tarjeta{position:absolute;z-index:5;pointer-events:none;max-width:230px;
      background:rgba(9,10,13,.96);border:1px solid var(--border-subtle);border-radius:4px;
      padding:10px 12px;box-shadow:0 10px 30px rgba(0,0,0,.6)}
    .mapa-tarjeta.con-imagen{padding:0;width:210px;overflow:hidden}
    .mapa-tarjeta img{display:block;width:100%;height:135px;object-fit:cover;background:#050608}
    .mapa-tarjeta .tj-txt{display:flex;flex-direction:column;gap:2px}
    .mapa-tarjeta.con-imagen .tj-txt{padding:9px 12px 11px}
    .mapa-tarjeta strong{font-family:var(--font-serif);font-size:.84rem;font-weight:500;
      color:var(--text-title);line-height:1.3}
    .mapa-tarjeta span{font-size:.74rem;color:var(--text-body)}
    .mapa-tarjeta em{font-style:normal;font-size:.68rem;color:var(--accent-gold);
      letter-spacing:.3px;font-variant-numeric:tabular-nums}

    .mapa-lado{position:sticky;top:20px}
    .mapa-h{font-family:var(--font-serif);font-size:.68rem;letter-spacing:2.4px;
      text-transform:uppercase;color:var(--accent-gold);margin:0 0 6px;font-weight:500}
    /* Alternar entre ver el mapa por sedes o filtrarlo por libro. */
    .lado-tog{display:flex;gap:0;margin:0 0 10px;border:1px solid var(--border-subtle);
      border-radius:4px;overflow:hidden}
    .tog-btn{flex:1;background:none;border:0;padding:8px 6px;cursor:pointer;
      font-family:var(--font-serif);font-size:.66rem;letter-spacing:2px;
      text-transform:uppercase;color:var(--text-muted);transition:background .2s,color .2s}
    .tog-btn:hover{color:var(--text-title)}
    .tog-btn.activo{background:var(--accent-gold);color:#0a0b0e;font-weight:600}
    /* Obras del libro elegido, desplegadas dentro de la propia lista. */
    .libro-obras{display:grid;grid-template-columns:repeat(auto-fill,minmax(78px,1fr));
      gap:8px;padding:12px 4px 16px;border-bottom:1px solid rgba(255,255,255,.05)}
    .libro-obra{display:flex;flex-direction:column;gap:4px;background:none;border:0;
      padding:0;cursor:pointer;text-align:left;color:inherit;font-family:inherit}
    .libro-obra img{width:100%;aspect-ratio:1/1;object-fit:cover;display:block;
      background:#050608;border:1px solid var(--border-subtle);transition:border-color .2s}
    .libro-obra:hover img{border-color:var(--accent-gold)}
    .libro-obra-t{font-size:.68rem;line-height:1.25;color:var(--text-title);
      display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
    .libro-obra-m{font-size:.62rem;color:var(--text-muted);font-variant-numeric:tabular-nums;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .libro-item .sede-n{color:var(--accent-gold-hover)}
    .libro-item.sel .sede-txt strong{color:var(--accent-gold-hover)}
    .mapa-nota{color:var(--text-muted);font-size:.79rem;margin:0 0 14px;font-weight:300;line-height:1.55}
    .mapa-aparte{color:var(--text-muted);font-size:.73rem;margin:0 0 14px;font-weight:300;
      line-height:1.5;padding-left:9px;border-left:1px solid var(--border-subtle)}
    .mapa-aparte em{font-style:normal;color:var(--text-body)}
    .sede-lista{list-style:none;margin:0;padding:0;max-height:520px;overflow-y:auto}
    .sede-item button{width:100%;display:flex;gap:12px;align-items:baseline;text-align:left;
      background:none;border:0;border-bottom:1px solid rgba(255,255,255,.05);
      padding:9px 4px;cursor:pointer;color:inherit;font-family:inherit}
    .sede-item button:hover{background:rgba(197,160,70,.05)}
    .sede-item.sel button{background:rgba(197,160,70,.1)}
    .sede-n{font-family:var(--font-sans);font-size:.72rem;color:var(--accent-gold);
      min-width:16px;font-variant-numeric:tabular-nums;font-weight:600}
    .sede-txt{display:flex;flex-direction:column;gap:1px;min-width:0}
    .sede-txt strong{font-size:.84rem;color:var(--text-title);font-weight:400;line-height:1.35}
    .sede-item.sel .sede-txt strong{color:var(--accent-gold-hover)}
    .sede-txt em{font-style:normal;font-size:.72rem;color:var(--text-muted)}

    .sede-detalle{margin-top:34px;border-top:1px solid var(--border-subtle);padding-top:26px}
    .sede-cab h3{font-family:var(--font-serif);font-size:1.25rem;font-weight:500;
      color:var(--text-title);margin:0 0 3px;letter-spacing:.4px}
    .sede-cab p{color:var(--text-muted);font-size:.85rem;margin:0 0 20px}
    .obra-min-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:18px}
    .obra-min{display:flex;flex-direction:column;gap:7px;background:none;border:0;padding:0;
      cursor:pointer;text-align:left;color:inherit;font-family:inherit}
    .obra-min img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;
      background:#050608;border:1px solid var(--border-subtle);transition:border-color .2s}
    .obra-min:hover img{border-color:var(--accent-gold)}
    .obra-min-t{font-size:.82rem;color:var(--text-title);line-height:1.35}
    .obra-min-m{font-size:.7rem;color:var(--text-muted);font-variant-numeric:tabular-nums}
    .ciudad-sede{margin-bottom:30px}
    .ciudad-sede h4{display:flex;align-items:baseline;gap:10px;font-family:var(--font-serif);
      font-size:.72rem;letter-spacing:2px;text-transform:uppercase;color:var(--accent-gold);
      font-weight:500;margin:0 0 14px;padding-bottom:8px;
      border-bottom:1px solid var(--border-subtle)}
    .ciudad-sede h4 span{font-family:var(--font-sans);font-size:.68rem;letter-spacing:0;
      color:var(--text-muted);text-transform:none;font-variant-numeric:tabular-nums}

    /* ---- el mapa en el teléfono ----
       El mapa ocupa la pantalla entera, por detrás de la barra translúcida de arriba, y la
       lista es una hoja que sube desde abajo (mapa_js.py la mueve). Antes el marco era una
       franja de 16/9 —unos 200 px de alto— bajo una cabecera que llenaba la pantalla, con
       los siete botones de continente tapando un tercio del mapa. */
    .mapa-hoja-asa{display:none}
    @media (max-width:760px){
      body[data-libro="mapa"]{overflow:hidden;padding-bottom:0}
      body[data-libro="mapa"] .container{margin:0}
      #mapa-gallery.active{animation:none}
      .mapa-wrap{position:fixed;left:0;right:0;top:0;bottom:var(--barra-inf);z-index:5;
        display:block;gap:0;--hoja-vis:150px}
      .mapa-marco{position:absolute;inset:0;aspect-ratio:auto;border:0;border-radius:0;background:#131722}
      .mapa-cont{top:calc(var(--alto-barra,56px) + 8px);left:0;right:0;max-width:none;
        padding:0 12px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;gap:6px}
      .mapa-cont::-webkit-scrollbar{display:none}
      .mapa-cont button{flex:0 0 auto;border-radius:999px;padding:7px 13px;font-size:.66rem;
        background:rgba(10,11,14,.78);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px)}
      .mapa-cont button:disabled{display:none}
      .mapa-ctrl{top:calc(var(--alto-barra,56px) + 52px);right:12px}
      .mapa-ctrl button{width:40px;height:40px;border-radius:10px;font-size:1rem}
      .mapa-pista{left:12px;right:12px;bottom:calc(var(--hoja-vis) + 10px);text-align:center;
        border-radius:999px;font-size:.7rem;transition:bottom .35s cubic-bezier(.2,.8,.25,1)}

      .mapa-lado{position:absolute;left:0;right:0;bottom:0;top:auto;z-index:6;
        height:calc(100% - var(--alto-barra,56px) - 6px);
        display:flex;flex-direction:column;
        background:rgba(12,13,17,.97);border-top:1px solid rgba(197,160,70,.2);
        border-radius:18px 18px 0 0;box-shadow:0 -12px 40px rgba(0,0,0,.55);
        transform:translateY(calc(100% - var(--hoja-vis)));
        transition:transform .35s cubic-bezier(.2,.8,.25,1);will-change:transform}
      .mapa-lado.siguiendo{transition:none}
      .mapa-hoja-asa{display:flex;flex-direction:column;align-items:center;gap:7px;
        padding:8px 16px 10px;cursor:grab;touch-action:none;flex:0 0 auto}
      .asa-barra{width:40px;height:5px;border-radius:3px;background:rgba(255,255,255,.26)}
      .asa-txt{font-size:.7rem;letter-spacing:.3px;color:var(--text-muted);font-variant-numeric:tabular-nums}
      .mapa-lado-cuerpo{flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;
        -webkit-overflow-scrolling:touch;padding:0 16px calc(24px + env(safe-area-inset-bottom))}
      .mapa-lado .buscador{margin-bottom:10px}
      .lado-tog{border-radius:10px;background:rgba(255,255,255,.05);border:0;padding:2px;gap:2px}
      .tog-btn{border-radius:8px;padding:8px 6px;font-family:var(--font-sans);font-size:.78rem;
        letter-spacing:.2px;text-transform:none;font-weight:500}
      .tog-btn.activo{background:rgba(197,160,70,.2);color:var(--accent-gold-hover);font-weight:600}
      .sede-lista{max-height:none;overflow:visible}
      .sede-item button{padding:12px 4px}
      .sede-txt strong{font-size:.92rem}
      .libro-obras{grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:10px}
      .libro-obra img{border-radius:8px}

      /* Dentro de la hoja solo se enseña el panel de una ciudad con varios museos: el de
         una sede o un libro repetiría lo que la lista ya despliega en su sitio. */
      .sede-detalle{margin:4px 0 14px;padding:14px 0 0}
      .sede-detalle:empty,.sede-detalle[data-tipo="sede"],.sede-detalle[data-tipo="libro"]{display:none}
      .obra-min-grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px}
      .obra-min img{border-radius:8px}

      /* La cobertura, en fichas en vez de una tabla de 620 px que obligaba a desplazarse. */
      .cob-tabla{border:0;overflow:visible}
      .cob-tabla table{min-width:0}
      .cob-tabla thead{display:none}
      .cob-tabla table,.cob-tabla tbody,.cob-tabla tr,.cob-tabla td{display:block}
      .cob-tabla tr{padding:12px 14px;margin-bottom:8px;background:var(--bg-surface);
        border:1px solid var(--border-subtle);border-radius:12px}
      .cob-tabla td{padding:0;border:0;font-size:.86rem}
      .cob-tabla td:first-child{margin-bottom:4px}
      .cob-tabla td.pasaje{margin-bottom:4px}
      .cobertura h2{font-size:1.15rem;margin-top:32px}
    }
    /* Sin ratón no hay «pasar por encima»: la tarjeta flotante se quedaba colgada tras el
       toque. Tocar ya despliega o abre, así que sobra; y los botones + y − también, porque
       se pellizca. */
    @media (hover:none) and (pointer:coarse){
      .mapa-tarjeta{display:none!important}
      .mapa-ctrl{display:none}
      .sede-item button:hover{background:none}
      .sede-item.sel button{background:rgba(197,160,70,.1)}
    }
  </style>"""
doc=doc.replace("  </style>",CSS,1)


# La versión de GitHub Pages sale de este mismo punto: todo igual salvo las imágenes, que
# allí se piden a Commons en vez de incrustarse (herramientas/sitio/construir_sitio.py).
io.open(os.path.join(TMP,"pre_imagenes.html"),"w",encoding="utf-8").write(doc)

# ---------- imágenes: una sola copia, referenciada por índice ----------
orden=[]; datos={}
def idx(rel):
    if rel not in datos:
        p=os.path.join(TH, rel.replace("/","__"))
        if os.path.exists(p):
            datos[rel]="data:image/jpeg;base64,"+base64.b64encode(open(p,"rb").read()).decode()
        else:
            # Sin copia local no hay vista previa que incrustar: la miniatura de Commons. El
            # artefacto de claude.ai ya no se publica; esto solo evita que la cadena se pare.
            _sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sitio"))
            from comun import imagen
            datos[rel]=imagen(rel)[0]
        orden.append(rel)
    return orden.index(rel)
doc,n=re.subn(PATRON_RUTA_COMILLAS,
              lambda m: f'IMG[{idx(m.group(1))}]', doc)
mapa=("    /* Las vistas previas, una sola vez: cronología y mapa reutilizan estas entradas. */\n"
      "    const IMG = [\n" + ",\n".join(f'      "{datos[r]}"' for r in orden) + "\n    ];\n\n")
doc=doc.replace("  <script>\n","  <script>\n"+mapa,1)

out=os.path.join(TMP,"los-tres-libros.html")
io.open(out,"w",encoding="utf-8").write(doc)
mb=os.path.getsize(out)/1e6
print(f"referencias: {n} · imágenes únicas: {len(orden)}")
print(f"archivo final: {mb:.1f} MB  ({'cabe en 16 MB' if mb<15 else 'DEMASIADO GRANDE'})")
