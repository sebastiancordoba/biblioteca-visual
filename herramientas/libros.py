# -*- coding: utf-8 -*-
"""Registro único de libros de la colección.

Dar de alta un libro es añadir una entrada aquí y escribir su archivo de fichas
(`herramientas/<datos>.py`, con una lista llamada como `var`). Nada más: la página, la
portada, la Biblioteca, los buscadores, la cronología, el mapa, los README y las pruebas
leen de este registro. Antes había una docena de sitios con la lista de tres libros
escrita a mano, y cada libro nuevo habría obligado a encontrarlos todos.

El orden de la lista es el orden en que aparecen en la Biblioteca.
"""
import importlib, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LIBROS = [
    {
        "id": "genesis", "corto": "Génesis", "carpeta": "Génesis",
        "datos": "data_genesis", "var": "GENESIS",
        "tag": "Colección Génesis",
        "title": "Obras Maestras del Génesis",
        "sub": "Estudio visual en 3 columnas de las representaciones pictóricas del Génesis "
               "y análisis del cambio narrativo tras la Torre de Babel.",
        "headings": ["Lo que hace que destaque", "Contexto histórico", "Biografía del artista"],
    },
    {
        "id": "gilgamesh", "corto": "Gilgamesh", "carpeta": "Gilgamesh",
        "datos": "data_gilgamesh", "var": "GILGAMESH",
        "tag": "Colección Gilgamesh",
        "title": "La Epopeya de Gilgamesh",
        "sub": "Relieves asirios, sellos cilíndricos, tablillas cuneiformes y relecturas "
               "modernas del poema más antiguo conservado de la humanidad.",
        "headings": ["Lo que hace que destaque", "Contexto histórico y arqueológico", "Procedencia"],
    },
    {
        "id": "iliada", "corto": "Ilíada", "carpeta": "Ilíada",
        "datos": "data_iliada", "var": "ILIADA",
        "tag": "Colección Ilíada",
        "title": "La Ilíada de Homero",
        "sub": "Cerámica ática, escultura helenística, arqueología de Micenas y Troya, y la "
               "pintura neoclásica y romántica de la cólera de Aquiles.",
        "headings": ["Lo que hace que destaque", "Contexto histórico", "Autoría y procedencia"],
    },
    {
        "id": "atrahasis", "corto": "Atrahasis", "carpeta": "Atrahasis",
        "datos": "data_atrahasis", "var": "ATRAHASIS",
        "tag": "Colección Atrahasis",
        "title": "El poema de Atrahasis",
        "sub": "La huelga de los dioses, el hombre hecho de barro y sangre divina, y el "
               "Diluvio mil años antes del Génesis: tablillas, sellos y la arqueología "
               "de Sippar y Nippur.",
        "headings": ["Lo que hace que destaque", "Contexto histórico y arqueológico", "Procedencia"],
    },
    {
        "id": "enuma", "corto": "Enuma Elish", "carpeta": "Enuma_Elish",
        "datos": "data_enuma_elish", "var": "ENUMA_ELISH",
        "tag": "Colección Enuma Elish",
        "title": "Enuma Elish, la creación babilónica",
        "sub": "Marduk contra Tiamat, el mundo hecho con el cuerpo de un monstruo y la "
               "Babilonia que lo recitaba cada año nuevo: tablillas, relieves y la Puerta "
               "de Ishtar.",
        "headings": ["Lo que hace que destaque", "Contexto histórico y arqueológico", "Procedencia"],
    },
]

POR_ID = {l["id"]: l for l in LIBROS}
CARPETAS = [l["carpeta"] for l in LIBROS]

# Ruta de imagen de cualquier libro (o de los retratos de autor) dentro de index.html.
_ALT = "|".join(re.escape(c) for c in CARPETAS + ["Autores"])
PATRON_RUTA = r"\./((?:" + _ALT + r")/[^'\"]+\.jpg)"
PATRON_RUTA_COMILLAS = r'"\./((?:' + _ALT + r')/[^"]+\.jpg)"'


def entradas(libro):
    """Fichas de un libro. Un libro dado de alta sin su archivo de datos todavía no es
       un error: sale vacío y la página lo muestra «en preparación»."""
    try:
        mod = importlib.import_module(libro["datos"])
    except ModuleNotFoundError:
        return []
    return list(getattr(mod, libro["var"], []))


def todos():
    """[(libro, fichas)] en el orden del registro."""
    return [(l, entradas(l)) for l in LIBROS]
