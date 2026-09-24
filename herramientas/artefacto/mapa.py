# -*- coding: utf-8 -*-
"""Construye el mapa: costas recortadas a dos encuadres y museos situados.

La geometría procede de Natural Earth 50m, descargada en tiempo de construcción y
recortada, porque un artefacto no puede pedir teselas ni datos a ningún dominio externo.
"""
import io, json, math, os, re, sys, unicodedata
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TMP=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build")
sys.path.insert(0, os.path.join(ROOT,"herramientas")); os.chdir(ROOT)

# ---------- museos: coordenadas y ciudad ----------
MUSEOS = {
 "vaticano":   ("Museos Vaticanos y Capilla Sixtina","Ciudad del Vaticano",41.9064,12.4534),
 "brancacci":  ("Capilla Brancacci","Florencia",43.7679,11.2431),
 "uffizi":     ("Galleria degli Uffizi","Florencia",43.7678,11.2553),
 "salute":     ("Santa Maria della Salute","Venecia",45.4306,12.3347),
 "khm":        ("Kunsthistorisches Museum","Viena",48.2038,16.3617),
 "orsay":      ("Musée d'Orsay","París",48.8600,2.3266),
 "louvre":     ("Musée du Louvre","París",48.8606,2.3376),
 "bnf":        ("Biblioteca Nacional de Francia","París",48.8339,2.3757),
 "sulpice":    ("Saint-Sulpice","París",48.8511,2.3348),
 "tate":       ("Tate Britain","Londres",51.4911,-0.1278),
 "britishmus": ("British Museum","Londres",51.5194,-0.1270),
 "natgal":     ("National Gallery","Londres",51.5089,-0.1283),
 "prado":      ("Museo Nacional del Prado","Madrid",40.4138,-3.6921),
 "escorial":   ("Monasterio de El Escorial","San Lorenzo de El Escorial",40.5891,-4.1475),
 "watts":      ("Watts Gallery","Compton, Surrey",51.2211,-0.6350),
 "laing":      ("Laing Art Gallery","Newcastle upon Tyne",54.9740,-1.6100),
 "escocia":    ("National Galleries of Scotland","Edimburgo",55.9500,-3.1957),
 "ashmolean":  ("Ashmolean Museum","Oxford",51.7554,-1.2600),
 "praga":      ("Galería Nacional de Praga","Praga",50.0900,14.3980),
 "hermitage":  ("Museo del Hermitage","San Petersburgo",59.9398,30.3146),
 "tretiakov":  ("Galería Tretiakov","Moscú",55.7415,37.6208),
 "granet":     ("Musée Granet","Aix-en-Provence",43.5262,5.4498),
 "gliptoteca": ("Gliptoteca","Múnich",48.1462,11.5650),
 "nama":       ("Museo Arqueológico Nacional","Atenas",37.9891,23.7326),
 "achilleion": ("Palacio Achilleion","Corfú",39.5636,19.9128),
 "micenas":    ("Ciudadela de Micenas","Argólida",37.7306,22.7561),
 "troya":      ("Yacimiento de Troya","Hisarlik, Çanakkale",39.9575,26.2389),
 "bagdad":     ("Museo Nacional de Irak","Bagdad",33.3270,44.3870),
 "sulay":      ("Museo de Sulaymaniyah","Sulaymaniyah",35.5613,45.4329),
 "schwerin":   ("Staatliches Museum","Schwerin",53.6280,11.4180),
 "sanssouci":  ("Bildergalerie de Sanssouci","Potsdam",52.4009,13.0387),
 "cerveteri":  ("Museo Nacional Cerite","Cerveteri",41.9950,12.0950),
 # Norteamérica (recuadro aparte)
 "soumaya":    ("Museo Soumaya","Ciudad de México",19.4404,-99.2045),
 "puebla":     ("Catedral de Puebla, Capilla del Ochavo","Puebla",19.0433,-98.1983),
 "damasco":    ("Museo Nacional de Damasco","Damasco",33.5138,36.2765),
 "besanzon":   ("Musée des Beaux-Arts","Besanzón",47.2378,6.0241),
 "kassel":     ("Gemäldegalerie Alte Meister","Kassel",51.3130,9.4210),
 "berlin":     ("Gemäldegalerie","Berlín",52.5085,13.3650),
 "pergamo":    ("Museo de Pérgamo","Berlín",52.5212,13.3964),
 "estambul":   ("Museos Arqueológicos de Estambul","Estambul",41.0117,28.9814),
 "bagawat":    ("Necrópolis de El Bagawat","Oasis de Jarga",25.4633,30.5456),
 "darkutub":   ("Dar al-Kutub, Biblioteca Nacional de Egipto","El Cairo",30.0664,31.2311),
 "beitalfa":   ("Sinagoga de Beit Alfa","Beit Alfa",32.5186,35.4278),
 "adana":      ("Museo Arqueológico de Adana","Adana",36.9905,35.3375),
 "patrarm":    ("Patriarcado Armenio de Jerusalén","Ciudad Vieja",31.7745,35.2290),
 "mnba_ba":    ("Museo Nacional de Bellas Artes","Buenos Aires",-34.5838,-58.3929),
 "mrah":       ("Museos Reales de Arte e Historia","Bruselas",50.8400,4.3925),
 # Norteamérica
 "met":        ("Metropolitan Museum of Art","Nueva York",40.7794,-73.9632),
 "morgan":     ("Morgan Library & Museum","Nueva York",40.7492,-73.9815),
 "smithsonian":("Smithsonian American Art Museum","Washington D.C.",38.8977,-77.0230),
 "kimbell":    ("Kimbell Art Museum","Fort Worth",32.7489,-97.3648),
 "yale":       ("Yale Center for British Art","New Haven",41.3083,-72.9279),
}

# ---------- qué museo corresponde a cada ficha ----------
REGLAS = [
 ("bagawat","bagawat"),("dar al-kutub","darkutub"),("beit alfa","beitalfa"),
 ("arqueologico de adana","adana"),("patriarcado armenio","patrarm"),
 ("bellas artes, buenos aires","mnba_ba"),
 ("sixtina","vaticano"),("museos vaticanos","vaticano"),("gregoriano etrusco","vaticano"),
 ("brancacci","brancacci"),("uffizi","uffizi"),("salute","salute"),
 ("kunsthistorisches","khm"),("orsay","orsay"),("louvre","louvre"),
 ("biblioteca nacional de francia","bnf"),("saint-sulpice","sulpice"),
 ("tate britain","tate"),("british museum","britishmus"),("national gallery, londres","natgal"),
 ("national gallery","natgal"),("prado","prado"),("escorial","escorial"),
 ("watts gallery","watts"),("laing","laing"),("galleries of scotland","escocia"),
 ("ashmolean","ashmolean"),("praga","praga"),("hermitage","hermitage"),
 ("tretiakov","tretiakov"),("granet","granet"),("gliptoteca","gliptoteca"),
 ("arqueologico nacional de atenas","nama"),("achilleion","achilleion"),
 ("micenas","micenas"),("canakkale","troya"),("hisarlik","troya"),
 ("nacional de irak","bagdad"),("republica de irak","bagdad"),("sulaymaniyah","sulay"),
 ("schwerin","schwerin"),("sanssouci","sanssouci"),("cerite","cerveteri"),
 ("soumaya","soumaya"),("catedral de puebla","puebla"),("ochavo","puebla"),
 ("damasco","damasco"),("besanzon","besanzon"),("kassel","kassel"),
 ("pergamo","pergamo"),("arqueologicos de estambul","estambul"),
 ("gemaldegalerie, berlin","berlin"),("gemaldegalerie","kassel"),
 ("museos reales de arte e historia","mrah"),("bruselas","mrah"),
 ("metropolitan","met"),("morgan library","morgan"),("smithsonian","smithsonian"),
 ("kimbell","kimbell"),("yale","yale"),
]
def norm(s):
    s=unicodedata.normalize("NFD",s)
    return "".join(c for c in s if unicodedata.category(c)!="Mn").lower()

# Excepciones: fichas cuya ubicación actual no aparece en el campo meta.
# Se identifican por título Y autor, porque hay títulos repetidos entre obras
# distintas (dos «Adán y Eva», dos «El sacrificio de Isaac»…).
FORZAR = {
    ("El Anciano de los Días", "Blake"): "yale",    # Yale Center for British Art
    ("Adán y Eva", "Durero"):            "morgan",  # el grabado de 1504
}

def museo_de(item):
    for (titulo, autor), k in FORZAR.items():
        if item["title"] == titulo and autor in item["artist"]:
            return k
    t=norm(item["meta"])
    for pat,k in REGLAS:
        if pat in t: return k
    return None

if __name__ == "__main__":
    from libros import todos
    from cronologia import ordenar
    reg = todos()
    CARPETA = {l["corto"]: l["carpeta"] for l, _ in reg}
    filas=ordenar(*[(l["corto"], e) for l, e in reg if e])
    sin=[]
    cuenta={}
    for a,l,it in filas:
        if not os.path.exists(os.path.join(CARPETA[l],it["files"][0])): continue
        k=museo_de(it)
        if k is None: sin.append((l,it["title"],it["meta"].split("|")[-1].strip()))
        else: cuenta[k]=cuenta.get(k,0)+1
    print("obras sin museo asignado:",len(sin))
    for x in sin: print("   ",x)
    print(f"\n{sum(cuenta.values())} obras en {len(cuenta)} sedes:")
    for k,n in sorted(cuenta.items(),key=lambda x:-x[1]):
        print(f"  {n:>2}  {MUSEOS[k][0]}, {MUSEOS[k][1]}")
