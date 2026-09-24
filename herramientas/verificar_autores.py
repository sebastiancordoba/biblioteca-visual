# -*- coding: utf-8 -*-
"""Contrasta las fechas de los autores con Wikidata.

Las biografías se escriben a mano y las fechas son lo único que se puede comprobar contra
una fuente externa de forma automática, así que se comprueba. Dos cosas que este script
cazó la primera vez que se ejecutó y que conviene recordar:

  · «William Turner» en la Wikipedia en español es un naturalista del siglo XVI, no el
    pintor: el enlace equivocado habría metido el retrato de otra persona en la ficha.
  · Wikidata da 1669 como nacimiento de Villalpando, pero la Wikipedia en español y la
    bibliografía dan «c. 1649»; se conserva 1649 y la discrepancia queda anotada aquí.

Uso:  python3 herramientas/verificar_autores.py
      (una sola pasada, con pausas: Wikimedia limita la tasa con dureza)
"""
import json, os, re, subprocess, sys, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
from data_autores import AUTORES

# clave -> artículo en la Wikipedia inglesa, que es la que resuelve sin ambigüedad
ARTICULOS = {
 "miguel_angel":"Michelangelo", "masaccio":"Masaccio", "tiziano":"Titian",
 "bruegel":"Pieter Bruegel the Elder", "cormon":"Fernand Cormon", "blake":"William Blake",
 "turner":"J. M. W. Turner", "dore":"Gustave Doré", "scorel":"Jan van Scorel",
 "watts":"George Frederic Watts", "danby":"Francis Danby", "cole":"Thomas Cole",
 "cranach":"Lucas Cranach the Elder", "durero":"Albrecht Dürer", "caravaggio":"Caravaggio",
 "rembrandt":"Rembrandt", "rubliov":"Andrei Rublev", "delacroix":"Eugène Delacroix",
 "gauguin":"Paul Gauguin", "corot":"Jean-Baptiste-Camille Corot", "velazquez":"Diego Velázquez",
 "john_martin":"John Martin (painter)", "bosco":"Hieronymus Bosch", "rubens":"Peter Paul Rubens",
 "poussin":"Nicolas Poussin", "ribera":"Jusepe de Ribera", "bellini":"Giovanni Bellini",
 "lemoyne":"François Lemoyne", "breu":"Jörg Breu the Younger",
 "villalpando":"Cristóbal de Villalpando", "exekias":"Exekias", "eufronio":"Euphronios",
 "ingres":"Jean-Auguste-Dominique Ingres", "david":"Jacques-Louis David",
 "matsch":"Franz von Matsch", "hamilton":"Gavin Hamilton (artist)",
 "ivanov":"Alexander Andreyevich Ivanov", "tiepolo_g":"Giovanni Battista Tiepolo",
 "tiepolo_d":"Giovanni Domenico Tiepolo", "van_dyck":"Anthony van Dyck",
 "vernet":"Carle Vernet",
 "behzad":"Kamāl ud-Dīn Behzād", "bouguereau":"William-Adolphe Bouguereau",
}
# Discrepancias conocidas y resueltas a favor de otra fuente. Se declaran para que no
# vuelvan a aparecer como sorpresa, no para taparlas.
ACEPTADAS = {
 "villalpando": "Wikidata dice 1669; la Wikipedia en español y la bibliografía, «c. 1649»",
 "exekias":     "Wikidata guarda un valor único sin sentido; se usa el periodo de actividad",
 "laocoonte":   "grupo escultórico, no una persona: Wikidata no tiene fechas de nacimiento",
}


def wikidata(titulos):
    fuera = {}
    for i in range(0, len(titulos), 15):
        a = ["curl", "-s", "--get", "https://www.wikidata.org/w/api.php",
             "--data-urlencode", "action=wbgetentities", "--data-urlencode", "format=json",
             "--data-urlencode", "sites=enwiki", "--data-urlencode", "props=claims|sitelinks",
             "--data-urlencode", "titles=" + "|".join(titulos[i:i + 15])]
        txt = subprocess.run(a, capture_output=True, text=True).stdout
        try:
            d = json.loads(txt)
        except ValueError:
            print("  la API no devolvió JSON (¿límite de tasa?); se espera y se reintenta")
            time.sleep(90); return wikidata(titulos)
        for ent in d.get("entities", {}).values():
            sl = (ent.get("sitelinks") or {}).get("enwiki", {}).get("title")
            if not sl: continue
            cl = ent.get("claims", {})
            def anio(pid):
                try:
                    t = cl[pid][0]["mainsnak"]["datavalue"]["value"]["time"]
                    n = int(re.match(r"[+-](\d+)", t).group(1))
                    return -n if t[0] == "-" else n
                except Exception:
                    return None
            fuera[sl] = (anio("P569"), anio("P570"))
        time.sleep(12)
    return fuera


def main():
    datos = wikidata([ARTICULOS[a["clave"]] for a in AUTORES if a["clave"] in ARTICULOS])
    ok = aceptadas = 0
    malas, sin = [], []
    for a in AUTORES:
        clave, art = a["clave"], ARTICULOS.get(a["clave"])
        if clave in ACEPTADAS:
            aceptadas += 1
            print(f"  nota  {a['nombre']}: {ACEPTADAS[clave]}")
            continue
        d = datos.get(art)
        if not d or not (d[0] and d[1]):
            sin.append(f"{a['nombre']} ({art})"); continue
        nums = [int(x) for x in re.findall(r"\d{3,4}", a["anios"])]
        if len(nums) < 2:
            sin.append(f"{a['nombre']} (fechas no numéricas)"); continue
        if "a.C." in a["anios"]: nums = [-nums[0], -nums[1]]
        if nums[0] != d[0] or nums[1] != d[1]:
            malas.append(f"{a['nombre']}: ficha «{a['anios']}» · Wikidata {d[0]} – {d[1]}")
        else:
            ok += 1

    print(f"\ncoinciden con Wikidata: {ok}")
    print(f"discrepancias aceptadas y documentadas: {aceptadas}")
    if sin:
        print(f"\nsin comparación ({len(sin)}):"); [print("  ", x) for x in sin]
    if malas:
        print(f"\nDISCREPANCIAS SIN RESOLVER ({len(malas)}):"); [print("  ", x) for x in malas]
        return 1
    print("\nninguna fecha sin explicar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
