"""Descarga originales de Wikimedia Commons a resolución completa.
Uso: python3 download.py <manifiesto.tsv>
Formato del manifiesto (TSV):  <archivo destino>  <TAB>  <File:Titulo en Commons.jpg>
Regla del proyecto: SIEMPRE el original, nunca /thumb/. Se verifica el tamaño tras bajar.
"""
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commons import info, UA

def fetch(url, dest):
    """Descarga url en dest y devuelve el código HTTP (0 si curl falló del todo)."""
    # Ritmo cortés. Bajar decenas de archivos grandes seguidos dispara el límite de
    # Wikimedia y entonces cada archivo cuesta 600 s de espera: ir despacio sale más
    # barato que ir rápido y chocar.
    time.sleep(15)
    r = subprocess.run(
        ["curl","-sL","-m","600","--speed-limit","1000","--speed-time","45",
         "-A",UA,"-o",dest,"-w","%{http_code}",url],
        capture_output=True, text=True)
    try:
        return int(r.stdout.strip()[-3:])
    except ValueError:
        return 0

def sips_dims(path):
    r = subprocess.run(["sips","-g","pixelWidth","-g","pixelHeight",path],
                       capture_output=True, text=True)
    d = {}
    for line in r.stdout.splitlines():
        try:
            if "pixelWidth:" in line:  d["w"] = int(line.split(":")[1])
            if "pixelHeight:" in line: d["h"] = int(line.split(":")[1])
        except ValueError:
            return None, None   # sips no pudo leer el archivo (descarga corrupta)
    return d.get("w"), d.get("h")

def main(manifest):
    rows = []
    for line in open(manifest, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        dest, title = line.split("\t")
        rows.append((dest.strip(), title.strip()))

    meta = {r["title"]: r for r in info([t for _, t in rows])}
    ok = fail = 0
    for dest, title in rows:
        m = meta.get(title)
        if not m:
            print(f"  NO ENCONTRADO  {title}"); fail += 1; continue
        if "/thumb/" in m["url"]:
            print(f"  ES MINIATURA   {title}"); fail += 1; continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest) and os.path.getsize(dest) > 100000:
            print(f"  YA EXISTE      {os.path.basename(dest)}"); ok += 1; continue
        # La API devuelve la URL con parámetros de seguimiento (?utm_source=...): se quitan.
        url = m["url"].split("?")[0]

        code = fetch(url, dest)
        if code == 429:
            # Wikimedia limita la tasa y responde "retry-after: 600". Esperar menos no sirve
            # de nada: devuelve otro 429 y se pierde el intento.
            print("  429 LÍMITE DE TASA — esperando 600 s como pide el servidor", flush=True)
            if os.path.exists(dest): os.remove(dest)
            time.sleep(600)
            code = fetch(url, dest)
        if code != 200 or not os.path.exists(dest) or os.path.getsize(dest) < 100000:
            got = os.path.getsize(dest) if os.path.exists(dest) else 0
            print(f"  FALLO HTTP {code} ({got} B)  {title}")
            if os.path.exists(dest): os.remove(dest)
            fail += 1; continue
        w, h = sips_dims(dest)
        size_mb = os.path.getsize(dest) / 1e6
        if w is None:
            print(f"  ILEGIBLE       {os.path.basename(dest)} ({size_mb:.1f} MB) - se descarta")
            os.remove(dest); fail += 1; continue
        # Commons informa las dimensiones ya rotadas por EXIF; sips da las crudas.
        # Se compara el par sin orientación: lo que importa es que no sea una miniatura.
        if sorted((w, h)) != sorted((m["w"], m["h"])):
            print(f"  DIMENSIÓN ≠    {os.path.basename(dest)} bajado {w}x{h}, esperado {m['w']}x{m['h']}")
            fail += 1; continue
        sys.stdout.flush()
        print(f"  OK  {w}x{h}  {size_mb:6.1f} MB  {os.path.basename(dest)}")
        ok += 1
    sys.stdout.flush()
    print(f"\n=== {ok} descargadas/presentes, {fail} fallidas ===")
    return 0 if fail == 0 else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
