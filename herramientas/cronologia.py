# -*- coding: utf-8 -*-
"""Año de ordenación de cada obra, deducido del campo `artist` de su ficha.

Devuelve un entero: negativo para a.C., positivo para d.C. Ante un intervalo
("c. 1490–1500", "3200–3000 a.C.") se toma el extremo más antiguo, que es el
inicio de ejecución de la obra.
"""
import re

# Casos que el texto libre no resuelve: siglos romanos, cifras de dos dígitos,
# o piezas cuya fecha está en la ficha técnica y no en el campo de autoría.
EXCEPCIONES = {
    "Tablilla XI: el Diluvio": -650,          # s. VII a.C., biblioteca de Asurbanipal
    "Laocoonte y sus hijos": -40,             # c. 40 a.C., dos cifras
    "Las murallas de Troya": -2500,           # Troya II; el yacimiento arranca antes
}

def año(item):
    if item.get("title") in EXCEPCIONES:
        return EXCEPCIONES[item["title"]]
    m = re.search(r"\(([^)]*)\)", item.get("artist") or "")
    if not m:
        return None
    s = m.group(1)
    ac = "a.C" in s or "a. C" in s or "aC" in s
    nums = [int(x) for x in re.findall(r"\d{2,4}", s)]
    if not nums:
        return None
    return -max(nums) if ac else min(nums)

def etiqueta(a):
    return f"{-a} a.C." if a < 0 else str(a)

def ordenar(*colecciones):
    """Funde varias colecciones en una sola lista cronológica.
    Cada elemento sale como (año, nombre del libro, ficha)."""
    filas = []
    for libro, ents in colecciones:
        for it in ents:
            a = año(it)
            if a is not None:
                filas.append((a, libro, it))
    filas.sort(key=lambda r: (r[0], r[1]))
    return filas
