#!/bin/zsh
# Reconstruye la versión publicable. Cada paso se detiene si falla: antes se encadenaban
# silenciando la salida, y un paso roto dejaba publicar un intermedio caducado.
#
# Todo vive dentro del repositorio: los generadores en herramientas/artefacto/, el mapa
# base en herramientas/artefacto/datos/ y los intermedios en build/ (ignorada por git).
# Antes estaban en el directorio temporal de la sesión y se habrían perdido con ella.
set -e
RAIZ="${0:A:h:h}"
cd "$RAIZ"
# build/ es un enlace a ~/Library/Caches/biblioteca-visual/build: fuera de iCloud, que con
# «Optimizar almacenamiento» subía a la nube los intermedios y cada lectura esperaba a bajarlos.
if [[ -L build ]]; then mkdir -p "$(readlink build)"; else mkdir -p build; fi
# Sin «previas»: el artefacto de claude.ai ya no se publica y el sitio sirve todo desde Commons.
for f in build_mapa build build2 build3 build4; do
  echo "── $f"
  python3 "herramientas/artefacto/$f.py" || { echo "FALLÓ $f — se detiene la construcción"; exit 1; }
done
echo "── listo: build/los-tres-libros.html"
