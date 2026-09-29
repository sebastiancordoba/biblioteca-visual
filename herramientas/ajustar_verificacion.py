# -*- coding: utf-8 -*-
"""Arreglos de forma sobre un resultado de verificación de obras, antes de incorporarlo.

Tres casos que el validador rechaza con razón pero que no son datos sin fuente:
  previa  — una conclusión («…, pues, …») que resume la frase anterior: lleva su misma cita.
  mover   — una advertencia sobre las fuentes («no se ha podido consultar…»): no es un dato de
            la obra; pasa a «discrepancias».
  siguiente — una frase sin cita dentro de un pasaje que se cita al final (una sola llamada
            para dos frases de la misma fuente, como en la citación académica): lleva la cita
            de la frase que cierra el pasaje. Se aplica a todas las frases sin cita de la obra.
  imagen  — la descripción de lo que se ve: su fuente es la propia imagen, que se añade como
            fuente enlazada a su archivo en Commons.
Uso (desde Python): ajustar(ruta_resultado, [(id, campo, comienzo_de_frase, caso), ...])
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORTE = r"(?:(?<=[.!?])|(?<=[.!?]»)|(?<=\]))(?<! [A-Z]\.)\s+(?=[A-ZÁÉÍÓÚÑ«¿¡])"


def citar_pasajes(ruta):
    """Caso «siguiente» aplicado a todo el archivo."""
    import sys
    sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
    from incorporar_obras import frases_sin_cita
    d = json.load(open(ruta, encoding="utf-8"))
    # Sirve igual para los resultados de verificación (una lista) y para las fichas de alta
    # ({"obras": [...]}).
    registros = d["obras"] if isinstance(d, dict) else d
    n = 0
    for r in registros:
        for campo in ("analysis", "history", "bio"):
            fr = re.split(CORTE, r[campo])
            sin = set(frases_sin_cita(r[campo]))
            for k, f in enumerate(fr):
                if f in sin:
                    sig = next((re.search(r"\[\d+\]", x).group(0) for x in fr[k + 1:] if re.search(r"\[\d+\]", x)), None)
                    if sig:
                        fr[k] = f.rstrip(".") + " " + sig + "."; n += 1
            r[campo] = " ".join(fr)
    json.dump(d, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"  {n} frases toman la cita de la que cierra su pasaje")


def ajustar(ruta, arreglos):
    d = json.load(open(ruta, encoding="utf-8"))
    enl = json.load(open(os.path.join(RAIZ, "herramientas/artefacto/datos/enlaces.json"), encoding="utf-8"))
    for oid, campo, inicio, caso in arreglos:
        r = next(x for x in d if x["id"] == oid)
        fr = re.split(CORTE, r[campo])
        k = next(i for i, f in enumerate(fr) if f.startswith(inicio))
        if caso == "previa":
            previas = re.findall(r"\[\d+\]", " ".join(fr[:k]))
            assert previas, f"{oid}: no hay cita previa"
            fr[k] = fr[k].rstrip(".") + " " + previas[-1] + "."
        elif caso == "mover":
            r.setdefault("discrepancias", []).append(fr.pop(k))
        elif caso == "imagen":
            libro, num = oid.split(":")
            carpeta = {"genesis": "Génesis", "gilgamesh": "Gilgamesh", "iliada": "Ilíada",
                       "atrahasis": "Atrahasis", "enuma": "Enuma_Elish"}[libro]
            url = next(v["commons"] for k2, v in enl.items() if k2.startswith(f"{carpeta}/{num}_"))
            n = next((f["n"] for f in r["fuentes"] if f["obra"] == "La propia imagen"), None)
            if n is None:
                n = max(f["n"] for f in r["fuentes"]) + 1
                r["fuentes"].append({"n": n, "obra": "La propia imagen", "autor": None, "url": url,
                                     "titulo": "Lo que se ve en la reproducción de Wikimedia Commons"})
            fr[k] = fr[k].rstrip(".") + f" [{n}]."
        r[campo] = " ".join(fr)
        print(f"  {oid} {campo}: {caso} — «{inicio[:50]}»")
    json.dump(d, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
