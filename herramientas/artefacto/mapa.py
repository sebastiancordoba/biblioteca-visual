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
 "britlib":    ("British Library","Londres",51.5300,-0.1270),
 "valmarana":  ("Villa Valmarana ai Nani","Vicenza",45.5364,11.5581),
 "boijmans":   ("Museum Boijmans Van Beuningen","Róterdam",51.9142,4.4731),
 "harvard":    ("Harvard Art Museums","Cambridge (Massachusetts)",42.3741,-71.1143),
 "bnpolonia":  ("Biblioteca Nacional de Polonia","Varsovia",52.2139,21.0044),
 "israelmus":  ("Museo de Israel","Givat Ram",31.7722,35.2044),
 "beirut":     ("Museo Nacional de Beirut","Beirut",33.8783,35.5147),
 "nabeul":     ("Museo de Nabeul","Nabeul",36.4561,10.7376),
 "akdamar":    ("Iglesia de la Santa Cruz de Akdamar","Lago de Van",38.341,43.035),
 "kiev":       ("Catedral de Santa Sofía","Kiev",50.4529,30.5143),
 "cleveland":  ("Cleveland Museum of Art","Cleveland",41.5089,-81.612),
 "auckland":   ("Auckland Art Gallery Toi o Tāmaki","Auckland",-36.8515,174.7659),
 "tiem":       ("Museo de Arte Turco e Islámico","Estambul",41.0063,28.9749),
 "mnba_rio":   ("Museu Nacional de Belas Artes","Río de Janeiro",-22.9087,-43.176),
 "nmwa":       ("Museo Nacional de Arte Occidental","Tokio",35.7154,139.7759),
 "virreinato": ("Museo Nacional del Virreinato","Tepotzotlán",19.7137,-99.2231),
 "rijks":      ("Rijksmuseum","Ámsterdam",52.36,4.8852),
 "ponce":      ("Museo de Arte de Ponce","Ponce",18.0036,-66.6168),
 "narga":      ("Iglesia de Narga Selassie","Lago Tana",11.902,37.287),
 "tepapa":     ("Museo Te Papa Tongarewa","Wellington",-41.2905,174.7821),
 "munal":      ("Museo Nacional de Arte (MUNAL)","Ciudad de México",19.4361,-99.1397),
 "ladylever":  ("Lady Lever Art Gallery","Port Sunlight",53.3534,-2.9985),
 "salarjung":  ("Museo Salar Jung","Hyderabad",17.3713,78.4804),
 "germigny":   ("Oratorio carolingio de Germigny-des-Prés","Germigny-des-Prés",47.8453,2.2653),
 "sinai":      ("Monasterio de Santa Catalina del Sinaí","Sinaí",28.5559,33.976),
 "edimburgo_ul": ("Biblioteca de la Universidad de Edimburgo","Edimburgo",55.9425,-3.189),
 "vincoli":    ("Basílica de San Pietro in Vincoli","Roma",41.8938,12.493),
 "sbb":        ("Staatsbibliothek zu Berlin","Berlín",52.5075,13.371),
 "nypl":       ("New York Public Library","Nueva York",40.7532,-73.9822),
 "cusco":      ("Catedral del Cusco","Cusco",-13.5165,-71.9785),
 "walters":    ("Walters Art Museum","Baltimore",39.2966,-76.6158),
 "natgal":     ("National Gallery","Londres",51.5089,-0.1283),
 "prado":      ("Museo Nacional del Prado","Madrid",40.4138,-3.6921),
 "escorial":   ("Monasterio de El Escorial","San Lorenzo de El Escorial",40.5891,-4.1475),
 "watts":      ("Watts Gallery","Compton, Surrey",51.2211,-0.6350),
 "laing":      ("Laing Art Gallery","Newcastle upon Tyne",54.9740,-1.6100),
 "escocia":    ("National Galleries of Scotland","Edimburgo",55.9500,-3.1957),
 "ashmolean":  ("Ashmolean Museum","Oxford",51.7554,-1.2600),
 "praga":      ("Galería Nacional de Praga","Praga",50.0900,14.3980),
 "hermitage":  ("Museo del Hermitage","San Petersburgo",59.9398,30.3146),
 "lavra":      ("Lavra de la Trinidad y San Sergio","Sérguiev Posad",56.3107,38.1300),
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
 "nga":        ("National Gallery of Art","Washington D.C.",38.8913,-77.0199),
 "smithsonian":("Smithsonian American Art Museum","Washington D.C.",38.8977,-77.0230),
 "kimbell":    ("Kimbell Art Museum","Fort Worth",32.7489,-97.3648),
 "yale":       ("Yale Center for British Art","New Haven",41.3083,-72.9279),
 # «Las lágrimas de Eros»
 "prehistoire":("Musée national de Préhistoire","Les Eyzies",44.9368,1.0122),
 "naturhist":  ("Naturhistorisches Museum","Viena",48.2052,16.3597),
 "man":        ("Musée d'Archéologie nationale","Saint-Germain-en-Laye",48.8985,2.0953),
 "aquitaine":  ("Musée d'Aquitaine","Burdeos",44.8354,-0.5724),
 "pigorini":   ("Museo delle Civiltà","Roma",41.8327,12.4726),
 "mhomme":     ("Musée de l'Homme","París",48.8622,2.2876),
 "lascaux":    ("Cueva de Lascaux","Montignac",45.0537,1.1686),
 "troisfreres":("Cueva de los Trois-Frères","Montesquieu-Avantès",43.0325,1.2104),
 "antiken_mu": ("Staatliche Antikensammlungen","Múnich",48.1455,11.5672),
 "munzen_mu":  ("Staatliche Münzsammlung","Múnich",48.1414,11.5790),
 "antiken_be": ("Antikensammlung, Altes Museum","Berlín",52.5195,13.3985),
 "kupfer_be":  ("Kupferstichkabinett","Berlín",52.5086,13.3672),
 "delos":      ("Santuario de Delos","Delos",37.3997,25.2682),
 "pompeya":    ("Villa de los Misterios","Pompeya",40.7536,14.4773),
 "cachtice":   ("Castillo de Čachtice","Čachtice",48.7236,17.7617),
 "beaune":     ("Hôtel-Dieu","Beaune",47.0216,4.8378),
 "hamburgo":   ("Hamburger Kunsthalle","Hamburgo",53.5555,10.0026),
 "schiavoni":  ("Scuola di San Giorgio degli Schiavoni","Venecia",45.4361,12.3445),
 "altepin":    ("Alte Pinakothek","Múnich",48.1482,11.5700),
 "stadel":     ("Städel Museum","Fráncfort del Meno",50.1031,8.6742),
 "gnm":        ("Germanisches Nationalmuseum","Núremberg",49.4480,11.0761),
 "palazzote":  ("Palazzo Te","Mantua",45.1467,10.7967),
 "oslo":       ("Nasjonalmuseet","Oslo",59.9116,10.7300),
 "borghese":   ("Galleria Borghese","Roma",41.9142,12.4921),
 "pitti":      ("Palazzo Pitti","Florencia",43.7651,11.2500),
 "ruan":       ("Musée des Beaux-Arts","Ruan",49.4453,1.0943),
 "ginebra":    ("Musée d'Art et d'Histoire","Ginebra",46.1995,6.1515),
 "sabauda":    ("Galleria Sabauda, Musei Reali","Turín",45.0729,7.6857),
 "dresde":     ("Gemäldegalerie Alte Meister","Dresde",51.0533,13.7345),
 "sanfernando":("Real Academia de Bellas Artes de San Fernando","Madrid",40.4177,-3.7005),
 "lille":      ("Palais des Beaux-Arts","Lille",50.6311,3.0621),
 "ensba":      ("Beaux-Arts de Paris","París",48.8566,2.3336),
 "lyon":       ("Musée des Beaux-Arts","Lyon",45.7669,4.8338),
 "moreau":     ("Musée Gustave Moreau","París",48.8793,2.3321),
 "high":       ("High Museum of Art","Atlanta",33.7901,-84.3855),
 "detroit":    ("Detroit Institute of Arts","Detroit",42.3594,-83.0645),
 "lacoste":    ("Castillo de Lacoste","Lacoste",43.8323,5.2737),
 "machecoul":  ("Castillo de Machecoul","Machecoul",46.9937,-1.8233),
}

# ---------- qué museo corresponde a cada ficha ----------
REGLAS = [
 # «Las lágrimas de Eros». Van primero: varias fichas nombran también otro museo (un depósito,
 # un segundo ejemplar) y la regla genérica se las llevaba —el Bouts de Lille al Louvre, el
 # Vermeer de Dresde a la «gemaldegalerie» de Kassel—.
 ("palais des beaux-arts, lille","lille"),("dresde","dresde"),("dresden","dresde"),
 ("staatliche munzsammlung","munzen_mu"),("staatliche antikensammlungen","antiken_mu"),
 ("antikensammlung, staatliche museen zu berlin","antiken_be"),("kupferstichkabinett, staatliche museen zu berlin","kupfer_be"),
 ("kupferstichkabinett berlin","kupfer_be"),("hamburger kunsthalle","hamburgo"),
 ("prehistoire, les eyzies","prehistoire"),("naturhistorisches","naturhist"),("archeologie nationale","man"),
 ("musee d'aquitaine","aquitaine"),("museo delle civilta","pigorini"),("musee de l'homme","mhomme"),
 ("lascaux","lascaux"),("trois-freres","troisfreres"),("delos","delos"),("villa de los misterios","pompeya"),
 ("cachtice","cachtice"),("hotel-dieu","beaune"),("schiavoni","schiavoni"),("alte pinakothek","altepin"),
 ("stadel","stadel"),("germanisches nationalmuseum","gnm"),("palazzo te","palazzote"),("nasjonalmuseet","oslo"),
 ("borghese","borghese"),("palazzo pitti","pitti"),("beaux-arts, ruan","ruan"),("art et d'histoire, ginebra","ginebra"),
 ("sabauda","sabauda"),("san fernando","sanfernando"),("beaux-arts de paris","ensba"),
 ("ecole nationale superieure des beaux-arts","ensba"),("beaux-arts, lyon","lyon"),("gustave moreau","moreau"),
 ("high museum","high"),("detroit institute","detroit"),("lacoste","lacoste"),("machecoul","machecoul"),
 ("germigny","germigny"),("santa catalina, sinai","sinai"),("universidad de edimburgo","edimburgo_ul"),("san pietro in vincoli","vincoli"),("staatsbibliothek zu berlin","sbb"),("new york public library","nypl"),("asuncion, cusco","cusco"),("walters art museum","walters"),
 ("museo de israel","israelmus"),("museo nacional de beirut","beirut"),("museo de nabeul","nabeul"),("akdamar","akdamar"),("santa sofia, kiev","kiev"),("cleveland museum","cleveland"),("auckland art gallery","auckland"),("arte turco e islamico","tiem"),("belas artes, rio de janeiro","mnba_rio"),("arte occidental, tokio","nmwa"),("virreinato","virreinato"),("rijksmuseum","rijks"),("arte de ponce","ponce"),("narga selassie","narga"),("te papa","tepapa"),("munal","munal"),("lady lever","ladylever"),("salar jung","salarjung"),("bibliotheque nationale de france","bnf"),
 ("bagawat","bagawat"),("dar al-kutub","darkutub"),("beit alfa","beitalfa"),
 ("arqueologico de adana","adana"),("patriarcado armenio","patrarm"),
 ("bellas artes, buenos aires","mnba_ba"),
 ("sixtina","vaticano"),("sistina","vaticano"),("trinidad y san sergio","lavra"),("museos vaticanos","vaticano"),("gregoriano etrusco","vaticano"),
 ("brancacci","brancacci"),("uffizi","uffizi"),("salute","salute"),
 ("kunsthistorisches","khm"),("orsay","orsay"),("louvre","louvre"),
 ("biblioteca nacional de francia","bnf"),("saint-sulpice","sulpice"),
 ("tate britain","tate"),("british museum","britishmus"),("biblioteca nacional de polonia","bnpolonia"),("boijmans","boijmans"),("harvard art museums","harvard"),("british library","britlib"),("valmarana","valmarana"),("national gallery of art","nga"),   # antes que «national gallery»: si no, Washington caía en Londres
 ("national gallery, londres","natgal"),
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
    _ENL = json.load(io.open(os.path.join(ROOT,"herramientas","artefacto","datos","enlaces.json"),encoding="utf-8"))
    reg = todos()
    CARPETA = {l["corto"]: l["carpeta"] for l, _ in reg}
    filas=ordenar(*[(l["corto"], e) for l, e in reg if e])
    sin=[]
    cuenta={}
    for a,l,it in filas:
        # En disco o enlazada en Commons (la misma regla que inject.py).
        if not (os.path.exists(os.path.join(CARPETA[l],it["files"][0]))
                or f'{CARPETA[l]}/{it["files"][0]}' in _ENL): continue
        k=museo_de(it)
        if k is None: sin.append((l,it["title"],it["meta"].split("|")[-1].strip()))
        else: cuenta[k]=cuenta.get(k,0)+1
    print("obras sin museo asignado:",len(sin))
    for x in sin: print("   ",x)
    print(f"\n{sum(cuenta.values())} obras en {len(cuenta)} sedes:")
    for k,n in sorted(cuenta.items(),key=lambda x:-x[1]):
        print(f"  {n:>2}  {MUSEOS[k][0]}, {MUSEOS[k][1]}")
