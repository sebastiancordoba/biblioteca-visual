# -*- coding: utf-8 -*-
"""Baja de la Getty ULAN (Union List of Artist Names, Getty Research Institute) el registro
de cada autor y lo guarda en herramientas/sitio/datos/autores_ulan.json.

La ULAN es la lista de autoridad que usan museos y bibliotecas para identificar artistas:
es la fuente principal de las fechas y lugares que muestran las páginas de autor. Wikidata
queda como contraste, y las discrepancias entre las dos se señalan en vez de elegir una a
escondidas.

Los datos son abiertos (Linked Art, JSON) en vocab.getty.edu/ulan/<id>.json. El número de
cada autor sale de Wikidata (P245), que ya está en autores_wikidata.json.

Qué se guarda:
  nacimiento / muerte   el intervalo que da la ULAN (inicio más temprano, fin más tardío)
                        y el lugar. Un intervalo de más de un año se muestra como tal, no
                        como una fecha precisa que la fuente no afirma.
  nacionalidad, oficios las clasificaciones de la ULAN
  nota                  la nota biográfica (scope note), en inglés, redactada por el Getty

Uso:  python3 herramientas/autores_ulan.py      (después de autores_wikidata.py)
"""
import datetime, io, json, os, subprocess, time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "herramientas", "sitio", "datos")
WD = json.load(io.open(os.path.join(DATOS, "autores_wikidata.json"), encoding="utf-8"))["autores"]


def bajar(uid):
    for intento in range(4):
        r = subprocess.run(["curl", "-sL", "-H", "Accept: application/json",
                            "-A", "BibliotecaVisual/1.0 (https://github.com/sebastiancordoba/biblioteca-visual)",
                            f"https://vocab.getty.edu/ulan/{uid}.json"], capture_output=True, text=True).stdout
        try:
            return json.loads(r)
        except ValueError:
            print(f"  {uid}: sin JSON, espero 30 s", flush=True); time.sleep(30)
    return None


def anio(iso):
    """'1564-01-01T00:00:00' -> 1564; '-0550-...' -> -550."""
    if not iso: return None
    neg = iso.startswith("-")
    return int(iso.lstrip("-+").split("-")[0]) * (-1 if neg else 1)


def intervalo(ev):
    if not ev: return None
    ts = ev.get("timespan") or {}
    a, b = anio(ts.get("begin_of_the_begin")), anio(ts.get("end_of_the_end"))
    lugar = next((p.get("_label") for p in ev.get("took_place_at", []) if p.get("_label")), None)
    if a is None and b is None and not lugar: return None
    return {"desde": a, "hasta": b, "lugar": lugar}


def texto_anio(a):
    return f"{-a} a.C." if a < 0 else str(a)


def fecha(iv):
    """Texto honesto: un año si la fuente da un año; un intervalo si da un intervalo."""
    if not iv or iv["desde"] is None: return None
    a, b = iv["desde"], iv["hasta"] if iv["hasta"] is not None else iv["desde"]
    if a == b: return texto_anio(a)
    if a < 0 and b < 0: return f"entre {-a} y {-b} a.C."
    return f"entre {texto_anio(a)} y {texto_anio(b)}"


def main():
    salida = {}
    for clave, w in sorted(WD.items()):
        uid = w["ids"].get("ulan")
        if not uid: continue
        d = bajar(uid)
        if not d: print(f"  sin registro: {clave} ({uid})"); continue
        nac, mue = intervalo(d.get("born")), intervalo(d.get("died"))
        clases = [c.get("_label") for c in d.get("classified_as", []) if c.get("_label")]
        nota = next((s.get("content") for s in d.get("subject_of", [])
                     if s.get("type") == "LinguisticObject" and s.get("content")), None)
        salida[clave] = {
            "ulan": uid, "nombre": d.get("_label"),
            "url": f"https://vocab.getty.edu/page/ulan/{uid}",
            "nacimiento": nac, "muerte": mue,
            "nacimiento_texto": fecha(nac), "muerte_texto": fecha(mue),
            "clasificaciones": clases, "nota": nota,
        }
        time.sleep(1)
    json.dump({"consultado": datetime.date.today().isoformat(), "autores": salida},
              io.open(os.path.join(DATOS, "autores_ulan.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    print(f"{len(salida)} registros de la ULAN · con nota biográfica: "
          f"{sum(1 for v in salida.values() if v['nota'])} · "
          f"con lugar de nacimiento: {sum(1 for v in salida.values() if (v['nacimiento'] or {}).get('lugar'))}")


if __name__ == "__main__":
    main()
