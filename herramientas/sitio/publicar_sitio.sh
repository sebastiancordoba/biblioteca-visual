#!/bin/zsh
# Construye la versión de GitHub Pages y la sube a la rama gh-pages, que es la que sirve
# GitHub. El código fuente vive en main; gh-pages solo tiene el sitio construido, en un
# worktree aparte (build/gh-pages) para no mezclar ramas en la copia de trabajo.
# Se detiene en el primer paso que falle: nada se publica si una prueba no pasa.
set -e
RAIZ="${0:A:h:h:h}"
cd "$RAIZ"

echo "── artefacto (el sitio sale del mismo punto)"; ./herramientas/construir_artefacto.sh >/dev/null
echo "── sitio";  python3 herramientas/sitio/construir_sitio.py
echo "── prueba"; node herramientas/probar_sitio.js >/dev/null && echo "probar_sitio ok"

GP="$RAIZ/build/gh-pages"
# Si la carpeta del worktree desapareció (build/ se puede borrar entero), git lo sigue
# teniendo registrado: prune lo olvida. La comparación va por --porcelain y línea exacta,
# porque la ruta lleva espacios («Mobile Documents») y un grep suelto no la encuentra.
git worktree prune
if ! git worktree list --porcelain | grep -qxF "worktree $GP"; then
  rm -rf "$GP"
  if git show-ref --quiet --verify refs/heads/gh-pages; then
    git worktree add "$GP" gh-pages
  elif git ls-remote --exit-code --heads origin gh-pages >/dev/null 2>&1; then
    git fetch origin gh-pages
    git worktree add --track -b gh-pages "$GP" origin/gh-pages
  else
    git worktree add --orphan -b gh-pages "$GP"
  fi
fi

rsync -a --delete --exclude .git "$RAIZ/build/sitio/" "$GP/"
cd "$GP"
git add -A
if git diff --cached --quiet; then
  echo "── sin cambios en el sitio"
else
  git commit -q -m "Sitio construido desde main $(git -C "$RAIZ" rev-parse --short HEAD)"
  echo "── commit en gh-pages: $(git rev-parse --short HEAD)"
fi
git push -q origin gh-pages
echo "── publicado: https://sebastiancordoba.github.io/biblioteca-visual/"
