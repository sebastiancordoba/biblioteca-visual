# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es esto

Una colección de arte curada: imágenes en máxima resolución de obras que ilustran grandes libros
(el Génesis, Gilgamesh, La Ilíada, el Atrahasis y el Enuma Elish), acompañadas de análisis histórico y teológico
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
├── .gitignore          ← deja las imágenes fuera de git (ver «Control de versiones»)
├── herramientas/       ← scripts de búsqueda, descarga y generación (ver abajo)
└── <Libro>/            ← una carpeta por libro (Génesis/, Gilgamesh/, Ilíada/, Atrahasis/, Enuma_Elish/)
    ├── NN_*.jpg        ← las imágenes
    ├── NN_*.md         ← fichas sueltas heredadas (solo Génesis 01-09; ya no se mantienen:
    │                     el texto vivo está en herramientas/data_<libro>.py)
    ├── README.md       ← tabla índice + galería del libro
    └── Ensayo_*.md     ← ensayos temáticos del libro
```

Todos los libros funcionan igual: sus tarjetas se generan desde `herramientas/data_<libro>.py`, no
se escriben a mano en el HTML.

### El registro de libros

La lista de libros vive en **un solo sitio**: `herramientas/libros.py` (`LIBROS`). Cada entrada da el
`id` (el de `BOOKS.<id>` y de los ids del DOM), el nombre `corto` (la etiqueta de la cronología y del
mapa), la `carpeta` de imágenes, el módulo y la variable de datos, y los rótulos de la cabecera.
`inject.py`, `readme.py`, `enlaces.py` y toda la cadena del artefacto leen de ahí; antes había una
docena de listas de tres libros escritas a mano.

`index.html` ya no necesita el marcado de cada libro: `montarLibro(id)` crea con `createElement` su
panel y su cuadrícula la primera vez que se abre. Solo Génesis, Gilgamesh e Ilíada conservan paneles
escritos en el HTML.

`build.py` y `build_mapa.py` ordenan la cronología con **la misma etiqueta** (`corto`): el mapa guarda
índices de la cronología, y si las dos ordenaciones difieren, las obras del mapa abren otra obra.
La `carpeta` solo se usa para las rutas (`Enuma_Elish` frente a «Enuma Elish»).

### Dar de alta un libro

1. Una entrada en `herramientas/libros.py`.
2. `herramientas/data_<libro>.py` con la lista de fichas, y la carpeta de imágenes.
3. Su texto de introducción en el diccionario `INTRO` de `readme.py`.
4. Su tabla en `MAPA_DE_COBERTURA.md` y en `herramientas/artefacto/datos/cob.py`.
5. Las sedes nuevas en `herramientas/artefacto/mapa.py` (`MUSEOS` y `REGLAS`) y, si la ciudad es
   nueva, en `PAIS` de `build_mapa.py`. `python3 herramientas/artefacto/mapa.py` lista las obras
   que se quedan sin sede.

Nada más: la navegación, la Biblioteca, la portada, la cronología y el mapa lo recogen solos.

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

## Las imágenes ya no se guardan en este ordenador

Desde el 28 de septiembre de 2026 **la colección no guarda copia local de las imágenes**: el sitio las
sirve desde Wikimedia Commons, y una imagen cuenta como presente si está en disco **o** si tiene su
original enlazado en `herramientas/artefacto/datos/enlaces.json` (así lo aplican `inject.py`,
`readme.py`, `build_mapa.py`, `verificar.js` y la cadena de previas). Se borraron 121 imágenes (1,4 GB),
todas con su original en Commons y recuperables con `download.py` y los manifiestos.

Solo quedan cuatro copias locales, porque son mejores que cualquier versión en Commons y el sitio
genera de ellas su propia copia: la Creación de Adán (10080 px), la Expulsión de Masaccio
(3429 × 6000), el Elohim de Blake (6072 px) y el Diluvio de Van Scorel. Y los retratos de `Autores/`.
Como la carpeta está en iCloud Drive con «Optimizar almacenamiento», esos archivos pueden aparecer
como `dataless`: siguen ahí y se descargan solos al abrirlos.

**Obras nuevas**: no se descargan. `herramientas/alta_obras.py` toma fichas ya redactadas con fuentes,
les da número, las escribe en `data_<libro>.py` (o `data_altas_<libro>.py` para los libros que ya
existían) y anota el archivo de Commons en `herramientas/altas.tsv`, de donde `enlaces.py` saca el
original. Commons solo sirve miniaturas en anchos estándar (1280, 1920, 3840…; 2560 u 8000 dan 400);
los TIFF se sirven convertidos a JPEG (`lossy-page1-…`), y los originales de más de 150 MP se abren en
el visor a 3840 px porque pesan cientos de megas.

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

### La Biblioteca, y por qué los libros no son pestañas

Una pestaña por libro no escala: con veinte libros la barra superior sería una lista. Los libros
**no son secciones de primer nivel**. Arriba hay siempre las mismas cinco entradas —Inicio,
Biblioteca, Cronología, Mapa, Cobertura— y los libros viven dentro de la Biblioteca, que se genera
sola desde los marcados con `esLibro`. Añadir un libro no toca la navegación.

Dentro de un libro aparece el enlace «Todos los libros» y sigue marcada la Biblioteca, porque el
libro ya no tiene botón propio. `switchBook` acepta que no se le pase el botón pulsado y resuelve
él cuál marcar.

El buscador de la Biblioteca solo aparece por encima de seis libros: con tres estorba.

`verificar.js` comprueba la propiedad que motivó todo esto —que ningún libro tenga botón en la
barra superior—, de modo que si algún día vuelve a colarse uno, salta.

### La portada

La pestaña de inicio no es un libro más: `BOOKS.inicio` se **construye sola** concatenando todos
los libros marcados con `esLibro: true`, así que al añadir un libro nuevo la portada lo recoge sin
tocar nada. Su banner saca una obra cualquiera de cualquier libro y la releva cada siete segundos
entrando por la derecha.

Dos detalles que no son arbitrarios:

- Se **baraja** la lista entera en vez de sortear cada vez, de modo que no repite una obra hasta
  haberlas mostrado todas. Es lo que se espera de un banner de museo.
- Cada lámina lleva **dos capas**: la misma imagen ampliada y desenfocada como fondo, y encima la
  obra entera contenida (`background-size: contain`) desplazada a la derecha. La colección va de
  una tablilla apaisada a un Cranach de 7374 × 10954; recortar a `cover` dejaba de algunas obras
  poco más que una franja.

El bucle solo corre con la portada a la vista: en otra pestaña no tiene sentido gastar fotogramas
ni adelantar obras que nadie ve.

Las flechas de anterior y siguiente recorren un **historial** (`vistas` más un puntero), no vuelven
a sortear: si no, «atrás» daba una obra nueva en vez de la que se acababa de ver. La lámina entra
por el lado del que viene, para que retroceder no se vea igual que avanzar.

El banner ocupa lo que queda de ventana. Se mide **dónde empieza el banner**, no cuánto abulta la
cabecera: entre ambos hay márgenes y una barra de secciones que cambia de alto según el libro, y
sumarlos a ojo dejaba el botón «Ver en detalle» cortado por el borde inferior.

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

## El teléfono: una aplicación, no una web encogida

Por debajo de **760 px** la página cambia de forma, no solo de tamaño (bloque «EL TELÉFONO» al final
del `<style>` de `index.html`, y el del mapa al final del CSS de `build4.py`):

- **Barra superior** fija, compacta y translúcida con el título (y la flecha de vuelta dentro de un
  libro); la etiqueta y el párrafo de la cabecera no caben ahí, y el párrafo pasa a encabezar el
  contenido (`#movilIntro`). El desenfoque va en `header::before`, no en la cabecera: un
  `backdrop-filter` en ella convertiría a la cabecera en contenedor de la barra de pestañas fija.
- **Barra de pestañas abajo** con las cinco secciones: es el `.book-switch` de siempre, recolocado.
  Los iconos se eligen por el `onclick` de cada botón, así que valen para las secciones que añade
  la cadena de construcción. Una subsección con una sola pestaña se esconde; las demás son un
  control segmentado.
- **Mapa a pantalla completa** bajo la barra translúcida, con la lista como **hoja deslizable** de
  tres alturas (asomada, media, alta). Elegir una sede la deja a media altura con la sede a la
  vista, y `encajar` centra lo elegido en la franja que se ve (`huecoArriba`/`huecoAbajo`), no
  debajo de la hoja. El panel de una ciudad entra en la hoja; el de una sede o un libro se oculta,
  porque la lista ya despliega sus obras.
- **Visor con gestos**: pellizcar amplía hacia los dedos, doble toque acerca o ajusta, deslizar
  pasa de obra y, hacia abajo, cierra; un toque muestra u oculta los controles, que con el dedo
  ya no se esconden solos. El análisis es una hoja que sube al tocar la leyenda.
- Márgenes de la muesca con `env(safe-area-inset-*)`, que solo tienen valor con
  `viewport-fit=cover`; los campos de texto a 16 px, porque iOS amplía la página al enfocar uno
  menor y no la devuelve.

Lo que depende de tener ratón o dedo se decide con `(hover: none) and (pointer: coarse)`, no por el
ancho. Para probar en el ordenador: servir `build/sitio` por HTTP local y abrirlo en un `<iframe>`
de 390 px (la ventana de Chrome no baja a ancho de teléfono); los gestos se simulan con `Touch` y
`TouchEvent` dentro del iframe.

**El sitio de Pages tiene que ser un documento completo.** `build.py` quita el charset y el
viewport (el artefacto los ponía por su cuenta) y durante meses Pages se publicó así: sin doctype
iba en modo quirks, y sin viewport un teléfono maquetaba a 980 px y lo encogía todo, de modo que
ninguna regla de pantalla estrecha llegaba a aplicarse. `construir_sitio.py` reconstruye el
documento, añade el manifiesto y genera los iconos de «Añadir a pantalla de inicio» (las manos de
la Creación de Adán, recortadas de la copia local); `probar_sitio.js` lo comprueba.

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
- **`enlaces.py`** — mantiene `artefacto/datos/enlaces.json`, que dice de qué archivo de
  Commons salió cada imagen. **De esto depende el botón «Original» del visor**: si una obra
  no está ahí, el botón se esconde y no hay forma de llegar al archivo completo. Resuelve
  solo lo que falta, tomando el título de los manifiestos `*.tsv`; las imágenes anteriores a
  los manifiestos van en `artefacto/datos/titulos_extra.tsv`.
  `python3 herramientas/enlaces.py` — y ejecutarlo **después** de `inject.py`.
- **`construir_artefacto.sh`** — reconstruye la versión publicable de cabo a rabo. Se detiene en el
  primer paso que falle: antes se encadenaban silenciando la salida y un paso roto dejaba publicar
  un intermedio caducado.
- **`probar_todo.sh`** — pasa la batería entera. Todas las pruebas se sitúan solas en la raíz del
  repositorio, así que se puede invocar desde cualquier directorio.

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

### El buscador

Hay **un solo motor de búsqueda** para toda la página —los libros, la cronología, los autores
y el mapa—, de modo que la sintaxis que se aprende en un sitio vale en todos. Vive en
`index.html` (`normaliza`, `analizar`, `puntuar`, `docDeObra`, `cajaBusqueda`).

- Ignora acentos y mayúsculas: «velazquez» encuentra a Velázquez.
- Varios términos se acumulan; `"entre comillas"` busca la frase exacta; `-palabra` excluye.
- Prefijos de campo: `obra:` `autor:` `sede:` `ciudad:` `pais:` `libro:` `año:`
- Rangos: `año:<1600`, `año:1500-1600`, `año:<-500` para a.C.
- Puntúa: coincidir en el título vale más que coincidir a mitad del análisis, así que lo
  pertinente sale primero. Con consulta activa el orden por puntuación manda sobre el
  «ordenar por» elegido.

Dos cosas aprendidas escribiéndolo:

- El nombre de campo **no puede casarse con `\w`**: en JavaScript no incluye la eñe, y `año:`
  se colaba como texto suelto en vez de reconocerse como campo.
- `cajaBusqueda` se construye con `createElement`, **no con `innerHTML`**. Con `innerHTML` el
  campo no existe como nodo hasta que un navegador lo parsea, así que no había forma de
  ejercitar el buscador en las pruebas; además el manejador lee el valor del propio evento.

La caja se monta desde JS sobre cada cuadrícula (`Object.keys(BOOKS)`), no se escribe en el
marcado: así la tienen también las secciones generadas —la cronología— y los libros que se
añadan, sin tocar nada.

En el mapa el buscador además **vuela a lo encontrado**: filtra las obras igual que el filtro
por libro, de modo que grupos, abanicos, lista y continentes se adaptan solos, y encuadra las
sedes que quedan. Si no queda ninguna, la vista se deja como estaba: alejarse a la nada
desorienta más que ayudar.

### Autores

La Biblioteca tiene una segunda pestaña, **Autores**, con los 42 artistas de nombre propio de
la colección. Solo salen ellos: los relieves de Nínive, las tablillas de Uruk, la máscara de
Micenas y los frescos de Dura Europos son anónimos, y fingir una autoría sería peor que decir
que no la hay. Cada autor se enlaza con sus obras por el campo `artist` de la ficha —sin listas
escritas a mano—, de modo que al añadir una obra suya aparece ahí solo.

El vínculo autor↔obra se hace por **índice, nunca por título**. Los títulos se repiten —«El
sacrificio de Isaac» es de Caravaggio y de Rembrandt, «Adán y Eva» de Cranach dos veces y de
Durero— y buscar por título le colgaba a un autor la obra de otro, que es como se descubrió.
El índice se calcula sobre los `details` **ya filtrados**, porque las obras cuya imagen falta
no llegan a la página y correrían todos los índices. `inject.py` lo comprueba con un `assert`
al construir: si a un autor se le cuelga algo que no es suyo, la construcción se detiene.

Las biografías están en `herramientas/data_autores.py`. **Las fechas se comprueban contra
Wikidata** con `python3 herramientas/verificar_autores.py`; hoy 39 de 42 coinciden exactamente y
las 3 restantes están declaradas como excepciones con su motivo. Ese script cazó dos errores
que no se habrían visto de otro modo:

- «William Turner» en la Wikipedia en español es un **naturalista del siglo XVI**, no el pintor.
  El enlace equivocado habría puesto el retrato de otra persona en la ficha.
- Wikidata da 1669 como nacimiento de Villalpando; la Wikipedia en español y la bibliografía
  dan «c. 1649». Se conserva 1649 y la discrepancia queda anotada.

Los retratos los baja `herramientas/retratos.py` a `Autores/`. Es una **excepción deliberada a
la regla de máxima resolución**: son ilustración de interfaz, no piezas de la colección, y se
ven a 168 px, así que se piden a Commons ya reducidos a 640 px. El pie de cada uno dice qué es
—autorretrato, retrato por otro, fotografía o efigie póstuma— porque no es lo mismo, y de cinco
artistas (Exequias, Eufronio, Villalpando, Jörg Breu y los escultores del Laocoonte) **no se
conserva retrato**: se dice, en vez de poner una obra suya haciéndola pasar por su cara.

### Temas que cruzan los libros

`herramientas/temas.py` define los temas —el Diluvio, el ser humano hecho de barro, la torre y
el templo, monstruos vencidos, el duelo—: los pasajes de cada libro que lo cuentan, con
referencia exacta (libro, capítulo, tablilla, canto, verso), y las obras que lo representan.
`paginas.py` genera `temas/` y una página por tema, y en cada obra enlaza sus temas. La
introducción de un tema solo afirma lo que dicen los pasajes citados; las lecturas de cada
obra están en su página, con sus fuentes. Las obras se nombran por el **número de su archivo**,
no por su posición, y construir falla si un tema cita una obra que no existe.

Desde la aplicación, cada tarjeta de autor enlaza con su página («Biografía completa y
fuentes»): relativa dentro del sitio (`BASE_FICHAS` vacío) y al sitio público desde el
artefacto o el `index.html` local.

### Autores con fuentes académicas

Cada página de autor muestra de dónde sale cada dato. Tres archivos en
`herramientas/sitio/datos/`, guardados en el repositorio para que construir no dependa de la
red (se actualizan volviendo a ejecutar su script):

- `autores_wikidata.json` ← `python3 herramientas/autores_wikidata.py`: fechas y lugares con la
  precisión que da Wikidata (año, década, «c.»), y los identificadores del autor en las obras de
  referencia académicas —Grove, Dizionario Biografico degli Italiani, Diccionario Biográfico
  Español, Iranica, ODNB, Benezit, Prado, Treccani, Universalis, Britannica— con la URL que
  Wikidata declara para cada una (P1630), no escrita a mano.
- `autores_ulan.json` ← `python3 herramientas/autores_ulan.py`: el registro de la **Getty ULAN**
  (fechas como intervalo, lugares, nota biográfica del Getty). Es la fuente principal de las
  fechas; Wikidata es el contraste.
- `autores_fuentes.json` ← `python3 herramientas/incorporar_fuentes.py resultado*.json`: la
  biografía **contrastada con bibliografía académica**, con una llamada `[n]` tras cada
  afirmación, sus fuentes, y lo que se retiró y por qué. El script rechaza un registro si una
  llamada no tiene fuente, si una fuente es Wikipedia o si una frase con datos no cita nada, y
  copia el texto sin llamadas a `data_autores.py` para que la aplicación muestre lo mismo.

Las fuentes discrepan más de lo que parece, y la página lo enseña en vez de elegir a
escondidas: la ULAN pone a Behzad nacido en Tabriz en 1445, cuando la Encyclopaedia Iranica
dice que su nacimiento es desconocido y que Tabriz es donde murió; Wikidata da «c. 1669» para
Villalpando, que es el año de su boda. La verificación de 2026 corrigió además errores de las
biografías escritas a mano: Blake no murió en la pobreza, en la Sixtina sí hay arquitectura
pintada, Tiziano sí salió de Venecia, Watts rechazó un título de *baronet*, no de barón.

### Fichas de obra con fuentes

Las 100 fichas se contrastaron en 2026 con la ficha de cada obra en la web de su museo y con
bibliografía académica (400 citas, 342 fuentes distintas). El registro verificado está en
`herramientas/sitio/datos/obras_fuentes.json`, por `libro:número de archivo` (`genesis:42`), y
la página de cada obra muestra los tres textos con sus llamadas a nota, las discrepancias entre
fuentes y la lista de fuentes.

- `python3 herramientas/incorporar_obras.py resultado*.json` valida (las mismas reglas que las
  biografías) y copia el texto sin llamadas, y la línea `meta` corregida, a los `data_*.py`.
  **Avisa si la `meta` nueva cambia la sede del mapa**: así se cazaron «Capilla Sistina» (el mapa
  solo conocía «Sixtina») y la National Gallery of Art de Washington, que la regla «national
  gallery» mandaba a Londres.
- `herramientas/ajustar_verificacion.py` arregla la forma sin tocar el fondo: una conclusión que
  resume la frase anterior toma su cita; una advertencia sobre las fuentes pasa a
  «discrepancias»; la descripción de lo que se ve cita «La propia imagen»; y dos frases de un
  pasaje citado al final toman esa misma cita. Una sección sin nada verificable dice
  «Sin datos verificados: …» en vez de rellenarse.

Lo que destapó, además de cientos de datos corregidos: **imágenes que eran otra obra** (el
David era el dibujo preparatorio del Petit Palais, no el óleo del Louvre; el Danby es *The
Deluge*, no *La disminución de las aguas*; el Exekias es el ánfora B209, no la B210), **una
copia retocada** (el Doré, recortado y con el contraste subido: se sustituyó por la página
entera escaneada por la Biblioteca Nacional de Polonia), **atribuciones** (Taller de
Rembrandt, Círculo de Van Scorel, «atribuido a» Breu) y **obras que cambiaron de sede** (la
Trinidad de Rubliov está desde 2024 en la Lavra de la Trinidad y San Sergio). Una obra sin
confirmar en ninguna fuente (el Vernet de los juegos fúnebres) lo dice en su propia ficha.

### Crédito de cada foto

`python3 herramientas/creditos.py` baja de Commons autor y licencia de cada imagen a
`herramientas/artefacto/datos/creditos.json`. 42 de las 114 son CC BY o CC BY-SA, que **obligan**
a citar autor y licencia: el visor (artefacto y Pages) y cada página de obra lo muestran bajo
cada vista. Se usa el campo `Attribution` de Commons si existe (es el texto con el que el autor
pide ser citado) y si no `Artist`; en dominio público no se nombra fotógrafo, porque ahí `Artist`
es el autor de la obra. `probar_paginas.js` comprueba que ninguna vista de Commons quede sin él.

### Miniaturas de Commons

`python3 herramientas/sitio/verificar_miniaturas.py` compara cada URL de miniatura que construye
`comun.py` con la que da la API de Commons (tres peticiones, sin descargar imágenes: una ráfaga de
descargas a upload.wikimedia.org da 429 enseguida). Cuando el nombre del archivo pasa de 160
bytes, MediaWiki llama a la miniatura `1280px-thumbnail.jpg`.

### Identificar de qué archivo salió una imagen antigua

Las primeras obras del Génesis se guardaron antes de que existieran los manifiestos, así que
no consta su origen. Adivinar por el nombre es justo lo que produce las atribuciones falsas
que documenta este archivo. Lo que sí es fiable: **buscar en Commons y quedarse con el
candidato cuyo ancho y alto coincidan exactamente** con los del archivo local
(`sips -g pixelWidth -g pixelHeight`). Mismas dimensiones al píxel es el mismo archivo.
El resultado se anota en `artefacto/datos/titulos_extra.tsv`.

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

8. Resolver el enlace al archivo original, del que depende el botón «Original» del visor:

```sh
python3 herramientas/enlaces.py            # añade lo que falte desde los TSV
```

El bloque de `index.html` delimitado por
`/* ==== DATOS GENERADOS POR inject.py — NO EDITAR A MANO ==== */` se reescribe entero en cada
pasada: **cualquier edición manual dentro de él se pierde**.

### Sobre la verificación

No hay framework de tests, pero sí una batería propia (`./herramientas/probar_todo.sh`), y conviene
usarla porque el navegador no siempre está disponible: servir el sitio por HTTP local puede estar
bloqueado según el entorno, y Chrome rechaza las URL `file://`. Las pruebas ejecutan el JavaScript
**real** de la página con un DOM simulado, así que detectan tanto un error de sintaxis como una ruta
de imagen rota, una tarjeta que no se dibuja o un botón del mapa sin manejador.

`verificar.js`, `probar_render.js` y `probar_orden.js` leen `index.html`; el resto lee
`build/los-tres-libros.html`, así que conviene construir antes.

El DOM simulado está en **`herramientas/dom_falso.js`**, compartido. Estaba duplicado y a medias en
cada archivo de prueba, y cada vez que la página usaba una función del DOM que el simulacro no
tenía, la prueba se caía por el simulacro y no por un fallo real. Cuando una prueba reviente,
**mirar primero si falta algo en el simulacro**: es la causa más frecuente con diferencia. El
simulacro da identidad estable a `getElementById`, de modo que lo que la página construye queda
inspeccionable después. Y devuelve **`null`** para un id que ni está en el HTML ni ha asignado la
página, como un navegador: antes devolvía siempre un elemento, así que `montarLibro` creía que el
panel ya existía y nunca lo montaba, sin que ninguna prueba lo notara.

Un detalle que ha mordido dos veces: los oyentes hay que indexarlos por **`this.id`**, no por el id
con el que se creó el elemento. Los botones de continente nacen de `createElement` y reciben su id
(`mReset`, `mTodo`) justo después.

## Contenido escrito

Cada obra lleva análisis en tres registros que se repiten en el `.md`, en el cajón desplegable de la
tarjeta y en el panel del visor: **qué la hace destacar** (lectura formal y simbólica), **contexto
histórico** (encargo, restauraciones, procedencia, anécdotas) y **biografía del artista**. El tono es
ensayístico y específico —datos concretos, fechas, dimensiones, número de inventario cuando existe—,
no descripción genérica.

## Control de versiones (git)

El repositorio versiona **el texto y el código, no las imágenes**. Son 724 KB de fichas,
generadores, comprobadores, ensayos y manifiestos frente a 871 MB de JPEG, y meter los másteres
en el historial no aportaría nada: la regla del proyecto es que una imagen guardada **no se
modifica nunca** —ni se recomprime ni se reescala—, así que no tienen versiones que seguir, y
iCloud ya las respalda. `.gitignore` excluye `*.jpg`, `*.jpeg`, `*.png`, `.DS_Store` y
`__pycache__/`.

Lo que sí protege el historial es precisamente lo frágil: las fichas de `data_<libro>.py`, el
visor, y el bloque generado de `index.html` que se reescribe entero en cada pasada de `inject.py`.

**Punto pendiente:** de las 72 imágenes, 54 se pueden volver a bajar desde los TSV de
`herramientas/` con `download.py`; las 18 restantes —las primeras del Génesis, `01`–`13`, previas
a los manifiestos— no están en ningún TSV, así que hoy solo existen en disco. Conviene añadirles
su manifiesto para que la colección sea reproducible desde el repositorio.

## La versión de GitHub Pages

El sitio público vive en **`sebastiancordoba.github.io/biblioteca-visual/`**, repositorio
`sebastiancordoba/biblioteca-visual`. El código fuente va en `main`; el sitio construido, en la
rama **`gh-pages`**, que es la que sirve GitHub. Se publica con un solo comando:

```sh
./herramientas/sitio/publicar_sitio.sh     # construye, prueba y sube gh-pages
```

No es un tercer sitio que mantener: `construir_sitio.py` parte de **`build/pre_imagenes.html`**,
que `build4.py` deja justo antes de incrustar las previas, así que lleva todo lo del artefacto
—mapa, cronología, cobertura, botón «Original»— y solo cambia lo que en Pages sí se puede hacer:

- **Las imágenes se piden a Wikimedia Commons**, con las URL de `enlaces.json`: miniatura de
  1280 px en cuadrículas, mapa y portada; 1920 px al abrir el visor, para que llene la pantalla
  y el cambio al original no dé un salto; y el **archivo original** en cuanto el zoom pasa de
  1,4×. No antes: hay originales de decenas de megas. Junto al porcentaje de zoom aparece «HD».
- El formato de miniatura de Commons es `thumb/5/5b/<nombre>/1280px-<nombre>`, con el nombre
  **dos veces**; sin la repetición da 404 (así falló la primera construcción). Y no se puede
  pedir una miniatura mayor que el original: en ese caso se usa el original.
- Lo que no está en Commons va como archivo del sitio: los retratos de `Autores/` y las 6
  imágenes antiguas del Génesis sin origen conocido, en copia reducida a 2560 px. Al
  identificarlas en `titulos_extra.tsv` pasan solas a servirse desde Commons.
- **Una dirección por sección**: `#/genesis`, `#/mapa`, `#/biblioteca/autores`. Se envuelven
  `switchBook` y `switchTab`, y el botón «atrás» del navegador funciona.

`probar_sitio.js` ejecuta el JavaScript real del sitio con el DOM simulado (al que se le pasan
`location`, `history` e `Image` como globales extra de `ejecutar`) y comprueba que ninguna
imagen apunte a las carpetas de la colección, que las miniaturas tengan el formato de Commons,
que el original se pida una sola vez y que las direcciones se escriban.

### Páginas estáticas

Además de la aplicación, `paginas.py` genera HTML plano para lo que merece dirección propia:
`libros/`, `libros/<libro>/`, **`obras/<libro>/<nn-título>/`** (una por obra), `autores/` y
`autores/<clave>/`, más `sitemap.xml`, `robots.txt` y `404.html`. Se leen sin JavaScript, las
indexan los buscadores y al compartirlas muestran la imagen (Open Graph y JSON-LD). Lo
interactivo —visor, mapa, cronología, buscador— se queda en la aplicación: cada página enlaza
con ella («Abrir en el visor» lleva a `#/<libro>/obra/<n>`) y el visor enlaza de vuelta con
«Ficha de la obra». `mapa/`, `cronologia/` y `cobertura/` son solo entradas con dirección
limpia que redirigen a esas vistas.

- **Los datos salen de la propia aplicación**, no de las fichas en crudo:
  `extraer_datos.js` ejecuta la página con el DOM simulado y devuelve `BOOKS` y `AUTORES`
  ya filtrados. Así la obra 12 de una página es la obra 12 del visor; reimplementar el
  filtrado en Python habría sido abrir la puerta a que se desalinearan.
- `comun.py` decide de dónde sale cada imagen, para la aplicación y para las páginas: las
  dos piden las mismas miniaturas de Commons y el navegador las reaprovecha.
- La dirección de una obra lleva el número de su archivo (`42-las-capillas-…`), no su
  posición: renumerar la colección no rompe enlaces ya compartidos.
- `estilo.css` repite las variables de la aplicación; si cambia el tema, cambian las dos.

`probar_paginas.js` recorre todas las páginas y comprueba que ningún enlace interno esté
roto, que cada obra de la aplicación tenga página y que su título y su «Abrir en el visor»
correspondan al mismo índice que usa el visor.

## La versión publicada (artefacto)

> **Desde el 28 de septiembre de 2026 el artefacto de claude.ai ya no se mantiene ni se vuelve a
> publicar: la versión pública es solo la de GitHub Pages.** La cadena de `herramientas/artefacto/`
> sigue haciendo falta, porque el sitio sale del HTML que genera (`build/pre_imagenes.html`, con el
> mapa, la cronología y la cobertura); lo que dejó de hacerse es subir `build/los-tres-libros.html`
> a claude.ai. Lo que sigue describe cómo se construía.


Además del `index.html` local hay una versión compartible publicada como artefacto,
**Los Tres Libros** (`claude.ai/code/artifact/9cce8cc2-80fd-429b-88f8-bf8d0eb8605d`). No es un
archivo distinto que haya que mantener a mano: se construye **desde el `index.html` real** y solo
cambia lo que el formato obliga o lo que solo tiene sentido al compartir.

- Una página publicada debe caber entera en 16 MB y no puede cargar imágenes de dominios externos
  —tampoco de Wikimedia—, así que las imágenes van incrustadas en base64 a 900 px, una sola copia
  referenciada por índice desde un array `IMG`.
- El visor no se reescribe: la cuadrícula, el zoom a 40×, `W A S D` y las flechas quedan idénticos.
- Se añaden tres cosas que solo existen en la versión compartida: el botón **Ver original** de cada
  obra (que abre el archivo completo en Commons), la cronología conjunta de los tres libros, y el
  mapa navegable de sedes.

### Cómo se construye

`./herramientas/construir_artefacto.sh` — seis pasos, en orden, deteniéndose en el primero que
falle:

| paso | qué hace |
|---|---|
| `previas.py` | genera las vistas previas de 820 px que se incrustan; solo trabaja sobre lo que falta o ha cambiado |
| `build_mapa.py` | proyecta el mapa (Mercator), agrupa sedes y escribe el panel |
| `build.py` | extrae cabecera y cuerpo del `index.html` real, añade enlaces a Commons y la cronología |
| `build2.py` | parchea el visor y las pestañas |
| `build3.py` | integra el mapa y las tablas de cobertura |
| `build4.py` | estilos y deduplicación de las imágenes en el array `IMG` |

Los generadores viven en **`herramientas/artefacto/`** y sus datos de partida (mapa base de Natural
Earth, `enlaces.json`, `cob.py`) en `herramientas/artefacto/datos/`. Los intermedios van a `build/`,
que git ignora. Todo esto estuvo un tiempo en el directorio temporal de la sesión, donde se habría
perdido con ella: si algo del artefacto no se puede reconstruir desde el repositorio, está mal
colocado.

**Nada de anclas literales frágiles.** Los pasos localizan dónde insertar con expresiones regulares
y un `assert`. Se llegó a ello por las malas dos veces: un `book-count">15` que se quedó obsoleto al
llegar a 17 obras, y un `let currentBook = 'genesis'` que dejó de existir al añadir la portada. En
ambos casos el paso falló en silencio y se publicó un intermedio caducado. Por lo mismo, **las
cifras que se escriben en los rótulos se derivan de los datos**, nunca se copian a mano: el mapa
anunció «34 sedes en 13 países» cuando ya iban 43 en 15.

**El peso importa más de lo que parece.** El artefacto cabe de sobra en los 16 MB, pero eso no es
el límite real: a 10,7 MB la página se quedaba en blanco más de treinta segundos en el visor y no
llegaba a ser usable. Bajar las previas de 900 px / calidad 46 a 820 px / calidad 42 la dejó en
8,4 MB y en unos diez segundos; al llegar la Ilíada a 27 obras volvió a rozar los 9,7 MB y se
bajó otra vez, a 760 px / calidad 40, que la dejó en 8,2 MB. Con el Atrahasis y el Enuma Elish
llegó a 9,5 MB y se bajó a **700 px / calidad 38**: 8,2 MB otra vez. Si vuelve a acercarse a los 10 MB, lo primero que hay que tocar son
`LADO` y `CALIDAD` de `previas.py` —cambiarlos invalida las previas ya generadas y las rehace
todas—, no el número de obras.

**El aviso de «estas imágenes son vistas previas» no va en la página.** Se probó y sobra: ocupa la
cabecera con una explicación técnica antes de que se vea una sola obra, y el botón *Ver original*
ya lleva a la resolución completa. Si hay que explicar la diferencia, se explica al compartir el
enlace, no dentro del artefacto.
