# -*- coding: utf-8 -*-
"""Recorta las costas a un encuadre y las proyecta a coordenadas SVG."""
import io, json, math

def sutherland_hodgman(pts, bbox):
    """Recorta un anillo contra un rectángulo (región convexa)."""
    lon0, lat0, lon1, lat1 = bbox
    def dentro(p, borde):
        x, y = p
        return {"i": x >= lon0, "d": x <= lon1, "a": y <= lat1, "b": y >= lat0}[borde]
    def corte(p, q, borde):
        (x1, y1), (x2, y2) = p, q
        if borde in ("i", "d"):
            xb = lon0 if borde == "i" else lon1
            t = (xb - x1) / (x2 - x1) if x2 != x1 else 0
            return (xb, y1 + t * (y2 - y1))
        yb = lat1 if borde == "a" else lat0
        t = (yb - y1) / (y2 - y1) if y2 != y1 else 0
        return (x1 + t * (x2 - x1), yb)
    salida = pts
    for borde in ("i", "d", "a", "b"):
        if not salida: return []
        entrada, salida = salida, []
        n = len(entrada)
        for k in range(n):
            act, ant = entrada[k], entrada[k - 1]
            da, dn = dentro(act, borde), dentro(ant, borde)
            if da:
                if not dn: salida.append(corte(ant, act, borde))
                salida.append(act)
            elif dn:
                salida.append(corte(ant, act, borde))
    return salida

def anillos(geojson_path, bbox):
    d = json.load(io.open(geojson_path, encoding="utf-8"))
    fuera = []
    for f in d["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            for ring in poly:
                pts = [(p[0], p[1]) for p in ring]
                # descartar rápido lo que no toca el encuadre
                xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
                if max(xs) < bbox[0] or min(xs) > bbox[2] or max(ys) < bbox[1] or min(ys) > bbox[3]:
                    continue
                c = sutherland_hodgman(pts, bbox)
                if len(c) >= 3: fuera.append(c)
    return fuera

def merc_y(lat):
    """Ordenada de Mercator, en radianes."""
    lat = max(-85.0, min(85.0, lat))
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))

def proyectar(anillos_ll, bbox, k, mercator=True):
    """Mercator (la proyección de los mapas navegables: las verticales y horizontales
    siguen siéndolo, y desplazarse en longitud es una traslación pura, que es lo que
    permite repetir el mundo sin costura). Con mercator=False, equirectangular."""
    lon0, lat0, lon1, lat1 = bbox
    if mercator:
        GRA = 180 / math.pi
        y1 = merc_y(lat1)
        W = (lon1 - lon0) * k
        H = (y1 - merc_y(lat0)) * GRA * k
        def xy(lon, lat):
            return ((lon - lon0) * k, (y1 - merc_y(lat)) * GRA * k)
    else:
        cos = math.cos(math.radians((lat0 + lat1) / 2))
        W = (lon1 - lon0) * k * cos
        H = (lat1 - lat0) * k
        def xy(lon, lat):
            return ((lon - lon0) * k * cos, (lat1 - lat) * k)
    paths = []
    for ring in anillos_ll:
        pts = [xy(*p) for p in ring]
        # quitar puntos consecutivos que caen en el mismo píxel
        limpio = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - limpio[-1][0]) > .35 or abs(p[1] - limpio[-1][1]) > .35:
                limpio.append(p)
        if len(limpio) < 3: continue
        d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in limpio) + "Z"
        paths.append(d)
    return paths, W, H, xy


def lineas(geojson_path, bbox):
    """Lee líneas (fronteras) y las recorta por latitud, partiéndolas al salir del marco.
    En longitud no hace falta recortar: el marco abarca el mundo entero."""
    import io as _io, json as _json
    lon0, lat0, lon1, lat1 = bbox
    d = _json.load(_io.open(geojson_path, encoding="utf-8"))
    fuera = []
    for f in d["features"]:
        g = f["geometry"]
        partes = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for parte in partes:
            actual = []
            for lon, lat in [(p[0], p[1]) for p in parte]:
                if lat0 <= lat <= lat1:
                    actual.append((lon, lat))
                else:
                    if len(actual) >= 2: fuera.append(actual)
                    actual = []
            if len(actual) >= 2: fuera.append(actual)
    return fuera


def proyectar_lineas(lineas_ll, bbox, k, umbral_px=0.35):
    """Proyecta líneas abiertas y devuelve (trazado, longitud en píxeles de lienzo)."""
    import math as _m
    lon0, lat0, lon1, lat1 = bbox
    GRA = 180 / _m.pi
    y1 = merc_y(lat1)
    def xy(lon, lat):
        return ((lon - lon0) * k, (y1 - merc_y(lat)) * GRA * k)
    salida = []
    for ln in lineas_ll:
        pts = [xy(*p) for p in ln]
        limpio = [pts[0]]
        for p in pts[1:]:
            if abs(p[0] - limpio[-1][0]) > umbral_px or abs(p[1] - limpio[-1][1]) > umbral_px:
                limpio.append(p)
        if len(limpio) < 2: continue
        largo = sum(_m.hypot(limpio[i+1][0]-limpio[i][0], limpio[i+1][1]-limpio[i][1])
                    for i in range(len(limpio)-1))
        d = "M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in limpio)
        salida.append((d, largo))
    return salida
