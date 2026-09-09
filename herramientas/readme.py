# -*- coding: utf-8 -*-
"""Genera el README.md de cada libro nuevo desde las mismas fichas que alimentan index.html."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_gilgamesh import GILGAMESH
from data_iliada import ILIADA

ROOT = "/Users/sebastiancordoba/Library/Mobile Documents/com~apple~CloudDocs/Documents/Pinturas"

BOOKS = {
 "Gilgamesh": (GILGAMESH, "Colección Gilgamesh",
   "Relieves asirios, sellos cilíndricos, tablillas cuneiformes y objetos de culto en torno a la "
   "epopeya más antigua conservada de la humanidad. A diferencia del Génesis o de la Ilíada, "
   "Gilgamesh casi no tiene tradición pictórica: su iconografía es arqueológica, y eso es "
   "precisamente lo que la hace singular."),
 "Ilíada": (ILIADA, "Colección Ilíada",
   "Cerámica ática, escultura helenística, arqueología de Micenas y Troya, y la gran pintura "
   "neoclásica y romántica sobre la cólera de Aquiles. Tres estratos que se iluminan entre sí: "
   "el objeto que Homero pudo ver, la imagen que los griegos se hicieron del poema, y la lectura "
   "que Europa proyectó sobre él dos milenios después."),
}

for folder, (entries, tag, intro) in BOOKS.items():
    live = [e for e in entries
            if any(os.path.exists(os.path.join(ROOT, folder, f)) for f in e["files"])]
    if not live: 
        print(f"{folder}: sin imágenes todavía, README omitido"); continue

    L = [f"# {tag}", "", intro, "", "---", "",
         f"## 🏛️ Galería de la Colección ({len(live)} obras)", "",
         "| N° | Obra | Autoría / Procedencia | Ubicación | Wikipedia | Archivo |",
         "|---|---|---|---|---|---|"]
    for i, e in enumerate(live, 1):
        ubic = e["meta"].split("|")[-1].strip()
        main = e["files"][0]
        L.append(f"| {i} | **{e['title']}** | {e['artist']} | {ubic} | "
                 f"[Wikipedia]({e['wikiUrl']}) | [`{main}`](./{main}) |")

    L += ["", "---", "", "## 🖼️ Análisis Detallado de las Obras", ""]
    for i, e in enumerate(live, 1):
        L += [f"### {i}. {e['title']} — {e['artist']}", ""]
        for f, t in zip(e["files"], e["views"]):
            if os.path.exists(os.path.join(ROOT, folder, f)):
                L += [f"![{e['title']}](./{f})", f"*{t}*", ""]
        L += ["#### Ficha Técnica", ""]
        for part in e["meta"].split("|"):
            L.append(f"- {part.strip()}")
        L += ["", "#### Lo que hace que destaque", "", e["analysis"], "",
              "#### Contexto Histórico y Arqueológico", "", e["history"], "",
              "#### Autoría y Procedencia", "", e["bio"], "", "---", ""]

    path = os.path.join(ROOT, folder, "README.md")
    io.open(path, "w", encoding="utf-8").write("\n".join(L))
    print(f"{folder}/README.md escrito ({len(live)} obras)")
