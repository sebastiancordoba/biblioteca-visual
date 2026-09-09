# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es esto

Una colección de arte curada: imágenes en máxima resolución de obras que ilustran grandes libros
(el Génesis, y en expansión Gilgamesh y La Ilíada), acompañadas de análisis histórico y teológico
escrito, y un visor web para inspeccionarlas en súper detalle.

**No es un proyecto de software con build.** No hay `package.json`, dependencias, tests ni
herramientas. `index.html` es un único archivo autocontenido (HTML + CSS + JS vanilla, sin
frameworks) que se abre directamente en el navegador:

```
open index.html
```

Lo único que se carga de red son las fuentes de Google Fonts (Cinzel + Inter). Todo lo demás son
rutas relativas a archivos locales, así que el sitio funciona offline salvo la tipografía.

**Todo el contenido de cara al usuario se escribe en español.** Títulos, análisis, comentarios del
código y nombres de archivo incluidos.

## Estructura

```
Pinturas/
├── index.html          ← el visor, sirve para TODOS los libros
├── CLAUDE.md
├── herramientas/       ← scripts de búsqueda, descarga y generación (ver abajo)
└── <Libro>/            ← una carpeta por libro (Génesis/, Gilgamesh/, Ilíada/…)
    ├── NN_*.jpg        ← las imágenes
    ├── NN_*.md         ← fichas sueltas heredadas (solo Génesis 01-09; ya no se mantienen:
    │                     el texto vivo está en herramientas/data_<libro>.py)
    ├── README.md       ← tabla índice + galería del libro
    └── Ensayo_*.md     ← ensayos temáticos del libro
```

Los tres libros —**Génesis**, **Gilgamesh** e **Ilíada**— funcionan igual: sus tarjetas se generan
desde `herramientas/data_<libro>.py`, no se escriben a mano en el HTML.

`index.html` vive en la raíz precisamente para que un solo visor cubra varios libros; sus rutas de
imagen son por lo tanto `./<Libro>/NN_archivo.jpg`, nunca `./NN_archivo.jpg`.

## Convención de nombres de archivo

`NN_Titulo_En_Snake_Case_Artista_Año.jpg`, con su `.md` homónimo al lado:

- `NN` es el número de obra dentro del libro, con cero a la izquierda (`01`…`13`).
- Sufijo de letra (`01b_`, `02b_`) = vista secundaria de **la misma obra**: un detalle, la pieza
  pareada de un díptico, otra versión. No consume un número nuevo.
- Sufijo `_Wikipedia_Master` = la versión de resolución máxima descargada de Wikimedia Commons,
  usada como vista principal cuando supera a la que ya había.
- Sin acentos ni espacios en los nombres de archivo (el contenido sí los lleva).

## Regla no negociable: máxima calidad de imagen

**Siempre la mejor resolución disponible.** Es el principio rector de la colección: el visor llega a
40× de zoom y una imagen mediocre arruina la obra entera. En la práctica:

- Descargar **el archivo original** de Wikimedia Commons (la URL `.../commons/x/xx/Nombre.jpg`),
  nunca una miniatura `/thumb/…/800px-Nombre.jpg`.
- Antes de dar por buena una imagen, **comprobar sus dimensiones reales**
  (`sips -g pixelWidth -g pixelHeight archivo.jpg`). Un archivo de pocos cientos de KB casi siempre
  es una miniatura disfrazada y hay que buscar mejor fuente.
- **Nunca recomprimir, reescalar ni convertir** una imagen ya guardada. El peso no es un problema
  aquí: los archivos actuales llegan a ~20 MB y 10080 × 6720 px, y así deben quedarse.
- Si aparece una versión mejor de una obra que ya está en la colección, se **añade** con el sufijo
  `_Wikipedia_Master` y pasa a ser la vista principal, conservando la anterior como vista secundaria.
- Fuentes preferidas por orden: Wikimedia Commons en resolución completa, Google Arts & Culture,
  y los portales de imagen abierta de los propios museos (Rijksmuseum, Met, Prado, Getty).

### Resolución alta no es lo mismo que buena reproducción

Es el matiz que más se equivoca, y **manda sobre el número de megapíxeles**: muchas de las imágenes
más grandes de Commons son la foto que un visitante tomó en la sala. Salen en perspectiva, con el
reflejo del cristal, con el marco incluido y con el color de la iluminación de la galería. Una
reproducción cenital del museo de 1.200 px es mejor obra que una foto de exposición de 24 MP.

- **Pinturas y grabados (planos):** exigir siempre la reproducción institucional —Google Art
  Project, WGA, Rijksmuseum (`RP-P-`, `SK-A-`), Met (`DP`/`DT`), Prado, National Gallery—, aunque
  tenga menos resolución. Si en Commons solo hay fotos de sala, es preferible dejar la imagen
  pequeña que ya se tiene y buscar el original en la web del propio museo.
- **Escultura, relieve, cerámica y arqueología (tridimensionales):** aquí ocurre lo contrario. No
  existe «reproducción plana» posible, así que una buena fotografía es la única opción: se elige
  por resolución, encuadre frontal y luz.

`commons.py` aplica esta distinción automáticamente. Clasifica cada candidato como
`institucional`, `foto de sala` o `?` a partir del nombre del archivo (detecta nombres de cámara
sin renombrar del tipo `DSC2249`, `IMG_0412`, `P1170972`, y las marcas de exposición), y por
defecto **antepone la reproducción institucional a los megapíxeles**. Para un objeto
tridimensional se añade `objeto` al final del comando y entonces ordena solo por resolución:

```sh
python3 herramientas/commons.py search "Rubens Judgement of Paris" 8           # pintura
python3 herramientas/commons.py search "Lamassu Khorsabad Louvre" 8 objeto     # escultura
```

La heurística mira el nombre del archivo, así que no es infalible: ante la duda, conviene abrir la
página del archivo en Commons y ver de dónde procede.

## Cómo se arma la página

`index.html` **no contiene las tarjetas**: contiene la cáscara (cabecera, selector de libro,
pestañas, visor modal) y una función `renderBookGrid(libro)` que las dibuja desde los datos. Cada
libro tiene una grilla vacía —`<div class="grid-3col" id="<libro>-grid">`— que se rellena la
primera vez que se abre ese libro.

Esto quiere decir que **una obra se escribe en un solo sitio**: su entrada en
`herramientas/data_<libro>.py`. Antes vivía duplicada en tres (dos arrays de JS y el marcado de la
tarjeta), que es de donde salían los descuadres de índices.

Los ids se separan por libro (`thumb-iliada-3`, `drawer-genesis-7`) para que no choquen entre
colecciones.

## El visor de zoom

`openZoomForArtwork(grupoIdx, subVistaIdx)` abre el modal. Su comportamiento, útil al depurar:

- **Zoom** 1× a 40×, con interpolación suave (`lerp` 0.18) hacia `targetZoomScale`; la rueda hace
  zoom hacia el cursor, no al centro.
- **Teclado** (solo con el modal abierto): `W A S D` desplazan, `+` / `-` acercan y alejan de forma
  continua vía `requestAnimationFrame`, `0` resetea, `F` pantalla completa, `Esc` cierra,
  `←` / `→` navegan.
- Las **flechas recorren `getAllViewsList()`**, que aplana `artworkGroups` en una sola secuencia: la
  vista siguiente puede ser otro detalle de la misma obra, no necesariamente la obra siguiente.
- La interfaz se auto-oculta por inactividad; el panel de texto y la leyenda cancelan ese temporizador
  al pasar el ratón por encima.

## Estilo visual

Todo el tema vive en variables CSS de `:root`, al inicio del `<style>`: fondo casi negro
(`--bg-body: #07080a`), acento dorado (`--accent-gold: #c5a046`), Cinzel para títulos y Inter para
texto. Cambiar el tema es cambiar esas variables, no reglas sueltas. Los íconos son SVG en línea
(trazo `currentColor`), sin librería de iconos.

## Herramientas (`herramientas/`)

Buscar y descargar arte es el trabajo recurrente de este proyecto, así que está automatizado.
Todos los scripts se ejecutan **desde la raíz `Pinturas/`** y usan `curl` por debajo, porque el
Python 3.9 del sistema no tiene certificados CA y `urllib` falla con `CERTIFICATE_VERIFY_FAILED`.

- **`commons.py`** — consulta la API de Wikimedia Commons.
  `python3 herramientas/commons.py search "Rubens Judgement of Paris" 8` lista los candidatos
  **ordenados por megapíxeles**, que es el criterio de selección del proyecto.
  `python3 herramientas/commons.py info "File:Algo.jpg"` da el tamaño de un archivo concreto.
- **`download.py`** — baja los originales a resolución completa desde un manifiesto TSV
  (`<ruta destino>` TAB `<File:Título en Commons.jpg>`). Rechaza miniaturas y respuestas de error,
  y **verifica con `sips` que las dimensiones bajadas coinciden con las que anuncia Commons**.
  `python3 herramientas/download.py herramientas/iliada.tsv`
- **`data_<libro>.py`** — las fichas de cada libro (título, ficha técnica, análisis, contexto,
  procedencia y la lista de archivos e imágenes). **Aquí es donde se escribe una obra nueva.**
- **`inject.py`** — vuelca esas fichas en `index.html`. Es idempotente y puede reejecutarse.
- **`readme.py`** — regenera el `README.md` de cada libro desde las mismas fichas.

Ambos generadores **solo incluyen las obras cuyas imágenes existen en disco**, de modo que se
pueden ejecutar con una descarga a medias y la página queda coherente.

### Notas sobre la red

Wikimedia **limita la tasa de descarga con dureza**, y el síntoma es engañoso: `upload.wikimedia.org`
responde **HTTP 429 con una página HTML de 2.280 bytes** y la cabecera `retry-after: 600`. Si no se
comprueba el código, esa página se guarda como si fuera un `.jpg` y parece una descarga correcta.
Lo aprendido:

- Ejecutar los scripts **de uno en uno**. Varias descargas o búsquedas en paralelo disparan el
  límite y las búsquedas empiezan a devolver `(sin resultados)` sin error visible.
- La API devuelve la URL del archivo con parámetros de seguimiento (`?utm_source=…`). **Hay que
  quitarlos**; `download.py` ya lo hace.
- Esperar menos de los 600 s que pide el servidor no sirve de nada: devuelve otro 429.
- `download.py` comprueba el código HTTP, respeta el `retry-after`, aborta transferencias
  estancadas (`--speed-limit`/`--speed-time`), rechaza cualquier archivo menor de 100 KB y espera
  tres segundos entre descargas. Los manifiestos son **reejecutables**: lo ya descargado se salta,
  así que ante un corte basta con volver a lanzarlos.
- Verifica siempre el resultado con `node herramientas/verificar.js`.

### Comprobar antes de escribir la ficha

Dos errores reales cometidos en este proyecto, ambos evitables consultando la página del archivo
en Commons antes de redactar:

- Un archivo titulado *Rubens - Judgement of Paris* resultó ser la versión de la **National
  Gallery** (NG194), no la del Prado que se estaba describiendo.
- `File:Jacob worstelt met de engel Rijksmuseum SK-A-1724.jpeg` **no es de Rembrandt** sino de
  Bartholomeus Breenbergh; el Rembrandt está en Berlín.

Antes de dar por buena una obra conviene leer los campos `artist`, `institution`, `dimensions` y
`date` de la página del archivo, y desconfiar de los títulos que contengan «Detail» o cuya
proporción no cuadre con las medidas reales del cuadro. También hay que mirar el campo `source`:
si dice `Pinterest` o similar, se descarta.

## Qué buscar a continuación

`MAPA_DE_COBERTURA.md` lleva la cuenta de qué **capítulos del Génesis, cantos de la Ilíada y
tablillas de Gilgamesh** están representados y cuáles siguen vacíos, con un candidato concreto para
cada hueco. **Consúltalo antes de buscar obras nuevas**: la colección crece por pasajes que faltan,
no por acumulación de cuadros sueltos. Al añadir una obra, marca su fila.

## Flujo para añadir obras a cualquier libro

1. Mirar `MAPA_DE_COBERTURA.md` y elegir un **pasaje** que falte, no un cuadro suelto.
2. Buscar candidatos con `commons.py search`; para pintura, quedarse con la reproducción
   institucional aunque tenga menos megapíxeles.
3. **Abrir la página del archivo en Commons y comprobar autor, institución, medidas y fecha**
   antes de escribir nada (ver más arriba por qué).
4. Añadir la línea al TSV del libro y ejecutar `download.py`.
5. Escribir la ficha en `herramientas/data_<libro>.py` — los campos `files` y `views` van
   emparejados en el mismo orden.
6. Regenerar y comprobar:

```sh
python3 herramientas/inject.py          # vuelca las fichas en index.html
python3 herramientas/readme.py          # README de Gilgamesh e Ilíada
node herramientas/readme_genesis.js     # README del Génesis
node herramientas/verificar.js          # rutas rotas, alineación, imágenes pequeñas
node herramientas/probar_render.js      # ejecuta el renderizador y revisa el HTML producido
```

7. Marcar la fila en `MAPA_DE_COBERTURA.md`.

El bloque de `index.html` delimitado por
`/* ==== DATOS GENERADOS POR inject.py — NO EDITAR A MANO ==== */` se reescribe entero en cada
pasada: **cualquier edición manual dentro de él se pierde**.

### Sobre la verificación

No hay framework de tests, pero sí dos comprobadores propios, y conviene usarlos porque el
navegador no siempre está disponible: servir el sitio por HTTP local puede estar bloqueado según
el entorno, y Chrome rechaza las URL `file://`. `verificar.js` y `probar_render.js` ejecutan el
JavaScript real de la página con un DOM simulado, así que detectan tanto un error de sintaxis como
una ruta de imagen rota o una tarjeta que no se dibuja.

## Contenido escrito

Cada obra lleva análisis en tres registros que se repiten en el `.md`, en el cajón desplegable de la
tarjeta y en el panel del visor: **qué la hace destacar** (lectura formal y simbólica), **contexto
histórico** (encargo, restauraciones, procedencia, anécdotas) y **biografía del artista**. El tono es
ensayístico y específico —datos concretos, fechas, dimensiones, número de inventario cuando existe—,
no descripción genérica.
