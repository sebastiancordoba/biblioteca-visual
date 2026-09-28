# -*- coding: utf-8 -*-
"""Incorpora las biografías contrastadas con fuentes académicas.

Entrada: uno o varios JSON con la verificación de cada autor (formato de abajo). Salida:
  · herramientas/sitio/datos/autores_fuentes.json — el registro verificado: biografía con
    sus llamadas a nota, fuentes, nacimiento y muerte, discrepancias y lo que se retiró.
  · data_autores.py — el campo «bio» de cada autor pasa a ser el texto verificado, sin las
    llamadas a nota, para que la aplicación muestre lo mismo que la página.

Antes de aceptar nada comprueba cada registro, y si algo falla no escribe:
  · toda llamada [n] del texto tiene su fuente n, y toda fuente se cita al menos una vez;
  · ninguna fuente es Wikipedia ni sin URL completa;
  · toda frase con contenido lleva al menos una llamada.

Formato de cada autor:
  {"clave", "bio", "fuentes": [{"n", "obra", "titulo", "autor", "url"}],
   "vida": {"nacimiento": {"fecha", "lugar", "fuente"}, "muerte": {...}},
   "discrepancias": [...], "retirado": [...], "notas": "..."}

Uso: python3 herramientas/incorporar_fuentes.py resultado1.json resultado2.json ...
"""
import io, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "herramientas", "sitio", "datos", "autores_fuentes.json")
DATA = os.path.join(RAIZ, "herramientas", "data_autores.py")
LLAMADA = re.compile(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]")


def numeros(bio):
    ns = set()
    for m in LLAMADA.finditer(bio):
        grupo = m.group(1)
        rango = re.match(r"(\d+)\s*[–-]\s*(\d+)$", grupo)
        if rango:
            ns |= set(range(int(rango.group(1)), int(rango.group(2)) + 1))
        else:
            ns |= {int(x) for x in re.findall(r"\d+", grupo)}
    return ns


def problemas(r, claves):
    p = []
    if r.get("clave") not in claves: p.append(f"clave desconocida {r.get('clave')!r}")
    bio, fs = r.get("bio") or "", r.get("fuentes") or []
    if not bio.strip(): p.append("sin biografía")
    nums = {f.get("n") for f in fs}
    citados = numeros(bio)
    # también cuentan las llamadas de las discrepancias («la ULAN da 1640 [5]»)
    for x in r.get("discrepancias") or []:
        citados |= numeros(x)
    for v in ("nacimiento", "muerte"):
        n = ((r.get("vida") or {}).get(v) or {}).get("fuente")
        if n: citados.add(n)
    if citados - nums: p.append(f"llamadas sin fuente: {sorted(citados - nums)}")
    # Una fuente sin llamada vale si las discrepancias o las notas la nombran («la ULAN da
    # 1640», «la RAH dice…»): se leyó y respalda lo que ahí se afirma.
    contexto = " ".join((r.get("discrepancias") or []) + [r.get("notas") or ""]).lower()
    SIGLAS = {"ulan": ["ulan", "getty"], "real academia": ["rah", "real academia"],
              "dizionario biografico": ["dbi", "dizionario"], "britannica": ["britannica"],
              "prado": ["prado"], "treccani": ["treccani"], "iranica": ["iranica"]}
    def nombrada(f):
        t = (f.get("obra", "") + " " + (f.get("titulo") or "")).lower()
        claves_ = [v for k, vs in SIGLAS.items() if k in t for v in vs] or [t.split()[0]] if t else []
        return any(c in contexto for c in claves_)
    sueltas = sorted(n for n in nums - citados
                     if not nombrada(next(f for f in fs if f.get("n") == n)))
    if sueltas: p.append(f"fuentes que no se citan ni se nombran: {sueltas}")
    for f in fs:
        u = f.get("url") or ""
        if not re.match(r"https?://[^/\s]+\.[^/\s]+", u): p.append(f"fuente {f.get('n')} sin URL válida: {u!r}")
        if "wikipedia.org" in u: p.append(f"fuente {f.get('n')} es Wikipedia")
        if not f.get("obra"): p.append(f"fuente {f.get('n')} sin nombre de obra")
    # cada frase con contenido lleva una llamada
    # no se corta en iniciales: «E. L. Sukenik» es un nombre, no dos frases
    for frase in re.split(r"(?<=[.!?»])(?<! [A-Z]\.)\s+(?=[A-ZÁÉÍÓÚÑ«¿¡])", bio):
        if len(frase) > 25 and not LLAMADA.search(frase):
            p.append(f"frase sin fuente: «{frase[:70]}…»")
    return p


def main(archivos):
    sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
    from data_autores import AUTORES
    claves = {a["clave"] for a in AUTORES}
    previo = {}
    if os.path.exists(SALIDA):
        previo = json.load(io.open(SALIDA, encoding="utf-8"))
    nuevos, errores = {}, {}
    for f in archivos:
        for r in json.load(io.open(f, encoding="utf-8")):
            pr = problemas(r, claves)
            if pr: errores[r.get("clave")] = pr
            else: nuevos[r["clave"]] = r
    for c, pr in errores.items():
        print(f"RECHAZADO {c}:"); [print("    ", x) for x in pr]
    if errores:
        print(f"\n{len(errores)} autores con problemas: no se escribe nada. Corrige y vuelve a ejecutar.")
        return 1
    todo = {**previo, **nuevos}
    json.dump(todo, io.open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)

    # data_autores.py: el texto verificado, sin llamadas, en el campo bio de cada autor
    src = io.open(DATA, encoding="utf-8").read()
    for c, r in nuevos.items():
        limpio = re.sub(r"\s*" + LLAMADA.pattern, "", r["bio"]).strip()
        patron = re.compile(r'("clave": "' + re.escape(c) + r'"[\s\S]*?\n "bio": )"(?:[^"\\]|\\.)*"')
        src, n = patron.subn(lambda m: m.group(1) + json.dumps(limpio, ensure_ascii=False), src, count=1)
        assert n == 1, f"no encuentro el campo bio de {c} en data_autores.py"
    io.open(DATA, "w", encoding="utf-8").write(src)
    print(f"{len(nuevos)} biografías incorporadas · {len(todo)} en total en autores_fuentes.json · "
          f"{sum(len(r['fuentes']) for r in nuevos.values())} citas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
