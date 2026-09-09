#!/bin/zsh
# Pasa toda la batería. Sin argumentos y desde cualquier directorio.
# verificar/probar_render/probar_orden leen index.html; el resto, build/los-tres-libros.html,
# así que conviene haber pasado antes ./herramientas/construir_artefacto.sh.
RAIZ="${0:A:h:h}"
fallos=0
for t in "$RAIZ"/herramientas/verificar.js "$RAIZ"/herramientas/probar_*.js; do
  n="${t:t:r}"
  printf '%-26s ' "$n"
  if node "$t" >/dev/null 2>&1; then echo "ok"; else echo "FALLA"; fallos=$((fallos+1)); fi
done
echo "──────────────────────────────"
[[ $fallos -eq 0 ]] && echo "todo verde" || echo "$fallos con fallos — ejecuta el que falle a solas para ver el detalle"
exit $fallos
