# -*- coding: utf-8 -*-
"""Genera el README.md de cada libro nuevo desde las mismas fichas que alimentan index.html."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from libros import todos as _libros

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # la raíz del repositorio

# Texto de introducción de cada README. El Génesis tiene el suyo propio (readme_genesis.js).
# Un libro sin introducción aquí usa el subtítulo del registro.
INTRO = {
 "gilgamesh":
   "Relieves asirios, sellos cilíndricos, tablillas cuneiformes y objetos de culto en torno a la "
   "epopeya más antigua conservada de la humanidad. A diferencia del Génesis o de la Ilíada, "
   "Gilgamesh casi no tiene tradición pictórica: su iconografía es arqueológica, y eso es "
   "precisamente lo que la hace singular.",
 "iliada":
   "Cerámica ática, escultura helenística, arqueología de Micenas y Troya, y la gran pintura "
   "neoclásica y romántica sobre la cólera de Aquiles. Tres estratos que se iluminan entre sí: "
   "el objeto que Homero pudo ver, la imagen que los griegos se hicieron del poema, y la lectura "
   "que Europa proyectó sobre él dos milenios después.",
 "atrahasis":
   "El Atrahasis se escribió hacia 1700 a.C. y cuenta, antes que ningún otro texto conservado, "
   "la creación del hombre con barro y la sangre de un dios, y un diluvio del que se salva un "
   "solo hombre en un arca. No tiene tradición pictórica: su iconografía son las propias "
   "tablillas, los sellos con Enki y sus aguas, y la arqueología de las ciudades donde se copió.",
 "enuma":
   "El Enuma Elish es el poema de la creación de Babilonia: Marduk vence a Tiamat, parte su "
   "cuerpo en dos para hacer el cielo y la tierra, y a cambio recibe el reino de los dioses. Se "
   "recitaba cada año nuevo en el templo de Esagila. Su iconografía es la de la ciudad que lo "
   "cantaba: las tablillas, los dragones de la Puerta de Ishtar y los relieves de dioses que "
   "vencen monstruos.",
}
BOOKS = {l["carpeta"]: (ents, l["tag"], INTRO.get(l["id"], l["sub"]))
         for l, ents in _libros() if l["id"] != "genesis"}

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
