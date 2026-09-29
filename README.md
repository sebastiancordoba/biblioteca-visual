# Biblioteca Visual de los Grandes Libros

**[sebastiancordoba.github.io/biblioteca-visual](https://sebastiancordoba.github.io/biblioteca-visual/)**

Pintura, escultura, cerámica y arqueología reunidas en torno a siete libros fundacionales
—el **Génesis**, el **Éxodo**, el **Levítico**, **Gilgamesh**, la **Ilíada**, el **Atrahasis** y el
**Enuma Elish**—, cada
obra en la mayor resolución que existe y con un análisis escrito en tres registros: qué la
hace destacar, su contexto histórico y quién la hizo.

- **141 obras** en 84 sedes de 32 países, de una tablilla de Uruk del 3200 a.C. a una escultura
  de 1902, cada una con sus textos citados a fuentes de museo y bibliografía académica.
- **Visor con zoom a 40×** sobre el archivo original de Wikimedia Commons: la miniatura se
  cambia por el original en cuanto se acerca la imagen.
- **Mapa** de dónde está cada obra, **cronología** conjunta de los cinco libros y
  **cobertura** por capítulos, cantos y tablillas, y **temas** que cruzan los libros.
- Una página propia por [libro](https://sebastiancordoba.github.io/biblioteca-visual/libros/),
  por obra y por [autor](https://sebastiancordoba.github.io/biblioteca-visual/autores/).

Todo el contenido está en español.

## Criterio

La regla que manda sobre todas las demás es la **calidad de la reproducción**: el original
completo, nunca una miniatura, y para pintura la reproducción institucional del museo antes
que una foto de sala con más megapíxeles pero con reflejos y perspectiva. Cada atribución
se comprueba en la página del archivo en Commons —autor, institución, medidas y fecha—
antes de escribir la ficha, y las fechas de los autores se contrastan con Wikidata.

## Cómo está hecho

No hay framework ni dependencias: HTML, CSS y JavaScript sin librerías, y scripts de Python
que generan todo desde las fichas.

```
index.html                  la aplicación (visor, mapa, cronología, buscador)
herramientas/libros.py      el registro de libros
herramientas/data_*.py      las fichas: aquí se escribe una obra nueva
herramientas/inject.py      vuelca las fichas en index.html
herramientas/sitio/         la versión de GitHub Pages y las páginas estáticas
herramientas/artefacto/     la versión autocontenida para claude.ai, mapa incluido
herramientas/probar_*.js    la batería de pruebas
MAPA_DE_COBERTURA.md        qué pasajes de cada libro están representados
```

Las imágenes **no están en el repositorio ni hace falta tenerlas**: el sitio las pide directamente
a Commons, y los manifiestos `herramientas/*.tsv` dicen de qué archivo sale cada una.

```sh
python3 herramientas/download.py herramientas/atrahasis.tsv   # bajar las imágenes de un libro
python3 herramientas/inject.py                                # regenerar index.html
./herramientas/probar_todo.sh                                 # pasar las pruebas
./herramientas/sitio/publicar_sitio.sh                        # construir y publicar el sitio
```

`CLAUDE.md` explica el proyecto a fondo: las convenciones, las decisiones y los errores que
ya se cometieron y cómo se evitan.

## Imágenes

Todas proceden de [Wikimedia Commons](https://commons.wikimedia.org/) y conservan la
licencia de su archivo, enlazado desde cada obra con el botón «Original».
