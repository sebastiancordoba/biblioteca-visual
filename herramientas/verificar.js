/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Verifica index.html sin navegador: ejecuta su JS con un DOM simulado y comprueba
   los invariantes que de verdad se rompen al añadir obras.
   Uso:  node herramientas/verificar.js        (desde la raíz Pinturas/)          */
const fs = require('fs'), path = require('path');
const html = fs.readFileSync(require('path').join(__dirname,'..','index.html'), 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];

const { noop, ejecutar } = require('./dom_falso.js');
const { BOOKS, document, urlOriginal, openZoomForArtwork, abrirEnConjunto,
        navigateSequential, getAllViewsList, ejecutarEstado,
        renderBookGrid, consultaLibro, analizar, puntuar, docDeObra,
        autoresOrdenados, pintarAutores, verAutores } =
  ejecutar(html, '{BOOKS, urlOriginal, openZoomForArtwork, abrirEnConjunto,'
                + ' navigateSequential, getAllViewsList,'
                + ' ejecutarEstado: () => currentArtworkGroupIndex,'
                + ' renderBookGrid, consultaLibro, analizar, puntuar, docDeObra,'
                + ' autoresOrdenados, pintarAutores,'
                + ' verAutores: () => ({ orden: o => ordenAutores = o,'
                + '                      consulta: c => consultaAutores = c })}');

let fails = 0;
const check = (ok, msg) => { console.log((ok ? '  ok    ' : '  FALLA ') + msg); if (!ok) fails++; };

console.log('\n== Libros ==');
for (const [id, b] of Object.entries(BOOKS)) {
  check(b.details.length === b.groups.length,
    `${id}: ${b.details.length} fichas alineadas con ${b.groups.length} grupos de imagen`);
  check(html.includes(`id="nav-${id}"`) && html.includes(`id="${b.firstTab}"`),
    `${id}: nav y pestaña presentes en el HTML`);
}

console.log('\n== Toda imagen referenciada existe en disco ==');
let imgs = 0, missing = 0;
for (const [id, b] of Object.entries(BOOKS))
  for (const g of b.groups) for (const v of g) {
    imgs++;
    if (!fs.existsSync(decodeURIComponent(v.src))) { console.log(`  FALTA  ${v.src}`); missing++; }
  }
for (const m of html.matchAll(/(?:src|href)="(\.\/[^"]+\.jpg)"/g)) {
  imgs++;
  if (!fs.existsSync(m[1])) { console.log(`  FALTA  ${m[1]}`); missing++; }
}
check(missing === 0, `${imgs} referencias de imagen comprobadas, ${missing} rotas`);

console.log('\n== Regla de calidad máxima: ninguna imagen por debajo de 1500 px ==');
const { execSync } = require('child_process');

/* Excepciones conocidas: se comprobó en Commons y NO existe mejor reproducción
   institucional. Sustituir en cuanto aparezca una, buscando en la web del museo.
   Ver la sección "Resolución alta no es lo mismo que buena reproducción" de CLAUDE.md. */
const EXCEPCIONES = {
  './Génesis/03_Cain_y_Abel_Tiziano_1544.jpg':
    'única reproducción en Commons (WGA); el techo de la Salute está mal fotografiado',
  './Génesis/08_Sombra_y_Oscuridad_el_Diluvio_JMW_Turner_1843.jpg':
    'la mejor institucional es de 1198x1200; las de 24 MP son fotos de exposición con reflejos',
  './Génesis/11_Tras_el_Diluvio_George_Frederic_Watts_1891.jpg':
    'pendiente de buscar en la Watts Gallery',
  './Génesis/01b_La_Creacion_de_Adan_Manos_Miguel_Angel_1512.jpg':
    'recorte de detalle; puede rehacerse desde el techo de 10080x6720 ya presente',
  './Ilíada/26_Papiro_de_Oxirrinco_221_Escolios_de_la_Iliada_s_II.jpg':
    'única imagen de este papiro en Commons: su categoría tiene un solo archivo. Documento único, la alternativa era no tenerlo',
};
let small = 0;
for (const [id, b] of Object.entries(BOOKS))
  for (const g of b.groups) for (const v of g) {
    const f = decodeURIComponent(v.src);
    if (!fs.existsSync(f)) continue;
    const out = execSync(`sips -g pixelWidth -g pixelHeight ${JSON.stringify(f)} 2>/dev/null || true`).toString();
    const w = +(out.match(/pixelWidth: (\d+)/) || [])[1];
    const h = +(out.match(/pixelHeight: (\d+)/) || [])[1];
    if (!w || !h || Math.max(w, h) < 1500) {
      if (EXCEPCIONES[f]) console.log(`  aviso  ${w}x${h} ${f.split('/').pop()} — ${EXCEPCIONES[f]}`);
      else { console.log(`  PEQUEÑA ${w}x${h} ${f}`); small++; }
    }
  }
check(small === 0, `sin imágenes pequeñas nuevas (${Object.keys(EXCEPCIONES).length} excepciones conocidas y documentadas)`);

console.log('\n== Portada ==');
{
  const lienzo = document.getElementById('bannerLienzo');
  const info = document.getElementById('bannerInfo');
  const banner = document.getElementById('banner');
  check(lienzo.children.length === 1, `el banner pintó una lámina al arrancar (${lienzo.children.length})`);
  const capas = (lienzo.children[0] || {}).children || [];
  check(capas.length === 2, `la lámina lleva fondo desenfocado y obra contenida (${capas.length} capas)`);
  const urls = capas.map(c => (/url\("(.+)"\)/.exec(c.style.backgroundImage || '') || [])[1]);
  check(urls.length > 0 && urls.every(u => u && fs.existsSync(decodeURIComponent(u))),
    `las capas apuntan a una imagen que existe: ${urls[0] ? urls[0].split('/').pop() : 'ninguna'}`);
  check(/banner-titulo/.test(info.innerHTML) && /banner-ver/.test(info.innerHTML),
    'la ficha del banner trae título y botón de detalle');
  check((banner.oyentes.click || []).length === 1, 'el banner entero es clicable');
  check(/obras<\/span>/.test(document.getElementById('inicioCifras').innerHTML),
    'las cifras de la portada se generaron');
  const tarjetas = (document.getElementById('inicioLibros').innerHTML.match(/libro-card/g) || []).length;
  const reales = Object.values(BOOKS).filter(b => b.esLibro).length;
  check(tarjetas === reales, `una tarjeta por libro real (${tarjetas} de ${reales})`);
  check(BOOKS.inicio.details.length ===
        Object.values(BOOKS).filter(b => b.esLibro).reduce((n, b) => n + b.details.length, 0),
    'la portada reúne todas las obras de todos los libros');
  check(BOOKS.inicio.details.every(d => d.libro && d.libroId),
    'cada obra de la portada sabe de qué libro viene');
}

console.log('\n== Botón Original del visor ==');
{
  /* Llamaba a resetZoom(): al 100% no hacía nada visible, y encima el nombre prometía
     abrir el archivo original. Ahora lo abre de verdad. */
  check(/<a class="zoom-ctrl-btn" id="btnOriginal"[^>]*target="_blank"/.test(html),
    'el control Original es un enlace real, no un resetZoom disfrazado');
  check(/onclick="resetZoom\(\)"[^>]*>AJUSTAR</.test(html),
    'el que reajusta el zoom se llama AJUSTAR, que es lo que hace');

  let malas = 0, comprobadas = 0;
  for (const id of Object.keys(BOOKS)) {
    if (!BOOKS[id].details.length) continue;
    for (let i = 0; i < BOOKS[id].details.length; i += 7) {
      openZoomForArtwork.call(null, i, 0);
      // openZoomForArtwork usa currentBook; se fija abriendo desde ese libro
      const u = urlOriginal();
      comprobadas++;
      if (!u || (!u.startsWith('http') && !fs.existsSync(decodeURIComponent(u)))) malas++;
    }
    break;   // basta con un libro: la ruta de resolución es la misma para todos
  }
  check(malas === 0, `el original resuelve a un archivo real (${comprobadas} comprobadas, ${malas} rotas)`);
}

console.log('\n== Flechas del banner ==');
{
  const lienzo = document.getElementById('bannerLienzo');
  const antes = document.getElementById('bannerAntes');
  const despues = document.getElementById('bannerDespues');
  const fondoDe = l => ((/url\("(.+)"\)/.exec(((l.children||[])[0]||{style:{}}).style.backgroundImage || '') || [])[1]);
  const actual = () => fondoDe(lienzo.children[lienzo.children.length - 1]);

  check((antes.oyentes.click || []).length === 1 && (despues.oyentes.click || []).length === 1,
    'las dos flechas tienen manejador');

  check(antes.hidden === true, 'en la primera obra no se enseña la flecha de atrás');

  const primera = actual();
  despues.oyentes.click[0]({ stopPropagation(){} });
  const segunda = actual();
  check(segunda && segunda !== primera, 'la flecha de después pasa a otra obra');

  check(antes.hidden === false, 'a partir de la segunda obra sí aparece');

  antes.oyentes.click[0]({ stopPropagation(){} });
  check(actual() === primera, 'la flecha de antes vuelve exactamente a la anterior');
  check(antes.hidden === true, 'al volver a la primera se esconde de nuevo');

  /* En la primera obra no hay nada detrás: la flecha no debe repintar ni sortear. */
  const cuantas = lienzo.children.length;
  antes.oyentes.click[0]({ stopPropagation(){} });
  check(lienzo.children.length === cuantas && actual() === primera,
    'en la primera obra la flecha de antes no hace nada');
}

console.log('\n== Flechas del teclado en el banner ==');
{
  const lienzo = document.getElementById('bannerLienzo');
  const fondoDe = l => ((/url\("(.+)"\)/.exec(((l.children||[])[0]||{style:{}}).style.backgroundImage || '') || [])[1]);
  const actual = () => fondoDe(lienzo.children[lienzo.children.length - 1]);
  const teclas = document.oyentes.keydown || [];
  const pulsar = k => teclas.forEach(f => f({ key:k, preventDefault(){}, metaKey:false, ctrlKey:false, altKey:false }));

  check(teclas.length > 0, 'hay un oyente de teclado');

  /* Con el visor de obra abierto, las flechas son suyas: navegan entre obras. */
  document.getElementById('inicio-gallery').classList.add('active');
  document.getElementById('zoomModal').classList.add('active');
  const conVisor = actual();
  pulsar('ArrowRight');
  check(actual() === conVisor, 'con el visor abierto las flechas no tocan el banner');

  document.getElementById('zoomModal').classList.remove('active');
  const primera = actual();
  pulsar('ArrowRight');
  const segunda = actual();
  check(segunda && segunda !== primera, 'la flecha derecha pasa a la obra siguiente');
  pulsar('ArrowLeft');
  check(actual() === primera, 'la flecha izquierda vuelve a la anterior');

  /* Fuera de la portada tampoco deben actuar. */
  document.getElementById('inicio-gallery').classList.remove('active');
  const fuera = actual();
  pulsar('ArrowRight');
  check(actual() === fuera, 'fuera de la portada las flechas no hacen nada');
  document.getElementById('inicio-gallery').classList.add('active');
}

console.log('\n== Autores: orden y búsqueda ==');
{
  const A = verAutores();
  const nombres = () => autoresOrdenados().map(x => x.nombre);

  A.consulta(''); A.orden('nombre');
  const porNombre = nombres();
  check(porNombre.length > 0, `${porNombre.length} autores`);
  check(porNombre.join('|') === porNombre.slice().sort((a,b)=>a.localeCompare(b,'es')).join('|'),
    'por nombre salen en orden alfabético español');

  A.orden('cronologia');
  const crono = autoresOrdenados().map(x => x.nace ?? 9999);
  check(crono.every((v, i) => i === 0 || crono[i-1] <= v),
    `por cronología van de más antiguo a más moderno (${crono[0]} … ${crono[crono.length-1]})`);

  A.orden('obras');
  const cuantas = autoresOrdenados().map(x => x.obras.length);
  check(cuantas.every((v, i) => i === 0 || cuantas[i-1] >= v),
    `por número de obras van de más a menos (${cuantas[0]} … ${cuantas[cuantas.length-1]})`);

  A.orden('nombre');
  const acota = (q, msg) => { A.consulta(q); const n = nombres();
    console.log(`   «${q}» → ${n.length}: ${n.slice(0,3).join(', ')}`);
    check(n.length > 0 && n.length < porNombre.length, msg + ` (${n.length})`); return n; };

  acota('rembrandt', 'busca por nombre de autor');
  acota('veneciano', 'busca dentro del oficio y la biografía');
  acota('sede:louvre', 'busca por la sede de sus obras');
  acota('libro:iliada', 'busca por el libro en el que tienen obra');
  acota('año:<1500', 'acota por año de nacimiento');
  const bab = acota('babel', 'busca por el título de sus obras');
  check(bab.some(n => /Bruegel/.test(n)), 'y «babel» da con Bruegel, que la pintó');

  A.consulta('qwertyuiop');
  check(nombres().length === 0, 'una consulta sin resultados no devuelve nadie');
  A.consulta('');
  check(nombres().length === porNombre.length, 'vaciar la búsqueda los devuelve todos');
}

console.log('\n== Las flechas del visor respetan el conjunto ==');
{
  /* Al abrir una obra desde un autor o desde un museo, «siguiente» debe llevar a lo
     siguiente de ESE conjunto, no a lo siguiente del libro entero. */
  const g = BOOKS.genesis;
  /* Un conjunto de una sola obra no crea contexto: sirve para fijar el libro activo y
     medir el recorrido completo de ese mismo libro, sin comparar libros distintos. */
  const sinConjunto = () => {
    abrirEnConjunto('', [{ libro: 'genesis', i: 0 }], 'genesis', 0);
    return getAllViewsList().length;
  };
  const total = sinConjunto();
  check(total > 10, `sin conjunto se recorre el libro entero (${total} vistas)`);

  /* Un conjunto de tres obras sueltas del Génesis. */
  const tres = [0, 5, 9].map(i => ({ libro: 'genesis', i }));
  abrirEnConjunto('Prueba', tres, 'genesis', 0);
  const lista = getAllViewsList();
  const esperadas = tres.reduce((n, o) => n + BOOKS[o.libro].groups[o.i].length, 0);
  check(lista.length === esperadas,
    `con conjunto solo se recorren sus obras (${lista.length} vistas de ${esperadas}, no ${total})`);
  check(lista.every(v => tres.some(o => o.i === v.groupIdx)),
    'ninguna vista ajena al conjunto se cuela');

  /* Recorrerlo entero devuelve al punto de partida y nunca sale del conjunto. */
  const dentro = new Set(tres.map(o => o.i));
  let fuera = 0;
  for (let k = 0; k < lista.length; k++) {
    navigateSequential(1);
    const est = ejecutarEstado();
    if (!dentro.has(est)) fuera++;
  }
  check(fuera === 0, `dando la vuelta entera nunca se sale del conjunto (${fuera} salidas)`);

  /* Y un conjunto que cruza libros: un autor puede tener obra en dos. */
  const cruzado = [{ libro: 'genesis', i: 0 }, { libro: 'iliada', i: 0 }];
  abrirEnConjunto('Cruzado', cruzado, 'genesis', 0);
  const l2 = getAllViewsList();
  check(new Set(l2.map(v => v.libro)).size === 2, 'un conjunto puede cruzar libros');

  /* Abrir sin conjunto vuelve a recorrer el libro entero: no se queda pegado. */
  check(sinConjunto() === total, 'abrir desde la cuadrícula limpia el conjunto');
}

console.log('\n== Buscador ==');
{
  const grid = document.getElementById('genesis-grid');
  const tarjetas = () => (grid.innerHTML.match(/<article class="artwork-card">/g) || []).length;
  const buscar = q => { consultaLibro.genesis = q; renderBookGrid('genesis', true); return tarjetas(); };

  const todas = buscar('');
  check(todas === BOOKS.genesis.details.length, `sin consulta salen las ${todas} obras`);

  const reduce = (q, msg) => { const n = buscar(q); console.log(`   «${q}» → ${n}`);
    check(n > 0 && n < todas, msg + ` (${n} de ${todas})`); return n; };

  reduce('rembrandt', 'busca por autor sin escribir el campo');
  reduce('autor:rembrandt', 'el prefijo autor: acota al autor');
  reduce('velazquez', 'ignora los acentos: «velazquez» encuentra a Velázquez');
  reduce('"torre de babel"', 'las comillas buscan la frase exacta');
  reduce('sede:prado', 'el prefijo sede: acota al museo');
  reduce('año:<1500', 'el rango de año funciona con la eñe');
  reduce('ano:<1500', 'y también escrito sin ella');

  const conGrabado = buscar('diluvio');
  const sinGrabado = buscar('diluvio -grabado');
  check(sinGrabado <= conGrabado, `el guion excluye (${conGrabado} → ${sinGrabado})`);

  check(buscar('qwertyuiop') === 0, 'una consulta sin resultados no deja tarjetas');
  check(grid.innerHTML.includes('sin-resultados'), 'y lo dice en vez de dejarlo en blanco');

  check(buscar('') === todas, 'vaciar la búsqueda devuelve todas');

  /* La cronología y cada libro montan su propia caja. */
  const conCaja = Object.keys(BOOKS).filter(id =>
    document.getElementById('buscar-' + id) && BOOKS[id].details.length);
  check(conCaja.length >= 4,
    `hay buscador en cada sección con obras (${conCaja.join(', ')})`);
}

console.log('\n== Autores ==');
{
  const m = /const AUTORES = (\[[\s\S]*?\n    \]);/.exec(html);
  check(!!m, 'los autores están inyectados en la página');
  if (m) {
    const A = JSON.parse(m[1]);
    check(A.length > 0, `${A.length} autores con obra en la colección`);
    check(A.every(a => a.nombre && a.anios && a.oficio && a.bio),
      'todos tienen nombre, fechas, oficio y biografía');
    check(A.every(a => a.bio.length > 120), 'ninguna biografía es un relleno de una línea');

    /* Cada autor tiene que enlazar con obras que existan de verdad: el vínculo se hace por
       el campo `artist` de la ficha, y si alguien cambia ese texto el autor se quedaría
       colgado sin que se note. */
    let colgados = [], sinObra = [];
    for (const a of A) {
      if (!a.obras.length) { sinObra.push(a.nombre); continue; }
      for (const o of a.obras) {
        const b = BOOKS[o.libro];
        if (!b || !b.details.some(d => d.title === o.title)) colgados.push(`${a.nombre} → ${o.title}`);
      }
    }
    if (colgados.length) console.log('   ' + colgados.join('\n   '));
    check(colgados.length === 0, 'todas las obras enlazadas desde un autor existen');
    check(sinObra.length === 0, `ningún autor sin obra (${sinObra.join(', ') || 'ninguno'})`);

    const conRetrato = A.filter(a => a.retrato);
    const rotos = conRetrato.filter(a => !fs.existsSync(decodeURIComponent(a.retrato)));
    check(rotos.length === 0, `los ${conRetrato.length} retratos existen en disco`);
    check(conRetrato.every(a => a.retratoPie),
      'cada retrato dice qué es: autorretrato, retrato de otro, fotografía o efigie póstuma');

    /* Nadie anónimo debe colarse: la sección es de autores con nombre propio. */
    const anonimos = A.filter(a => /Nínive|Micenas|Uruk|Dura Europos|Babilon|Palacio|Templo|Hisarlik/i.test(a.nombre));
    check(anonimos.length === 0, 'no hay atribuciones culturales coladas como autores');

    check(html.includes("switchTab('autores-gallery'"), 'la pestaña Autores está en la Biblioteca');
  }
}

console.log('\n== Nomenclatura de las obras ==');
{
  /* Una obra se llama como se llama. Cuando dos comparten título —hay dos «Adán y Eva» de
     Cranach— la desambiguación va en el autor, la fecha y la sede, que ya se muestran
     debajo; meterla en el título entre paréntesis inventa un nombre que no existe. Se
     detecta comprobando que el paréntesis del título no repita nada de su propia ficha
     técnica, que es exactamente lo que pasaba con «Adán y Eva (Soumaya)». */
  const malos = [];
  for (const id of Object.keys(BOOKS)) {
    if (!BOOKS[id].esLibro) continue;
    for (const d of BOOKS[id].details) {
      const m = /\(([^)]+)\)\s*$/.exec(d.title || '');
      if (!m) continue;
      const dentro = m[1].toLowerCase();
      const ficha = `${d.artist || ''} ${d.meta || ''}`.toLowerCase();
      if (ficha.includes(dentro)) malos.push(`${d.title}  ←  «${m[1]}» ya está en la ficha`);
    }
  }
  if (malos.length) console.log('   ' + malos.join('\n   '));
  check(malos.length === 0,
    'ningún título lleva entre paréntesis un desambiguador que ya está en su ficha técnica');
}

console.log('\n== Barra espaciadora: pausar el banner ==');
{
  const banner = document.getElementById('banner');
  const aviso = document.getElementById('bannerAviso');
  const teclas = document.oyentes.keydown || [];
  let impedido = 0;
  const pulsar = k => teclas.forEach(f => f({
    key: k, metaKey:false, ctrlKey:false, altKey:false,
    preventDefault(){ impedido++; }
  }));

  document.getElementById('inicio-gallery').classList.add('active');
  document.getElementById('zoomModal').classList.remove('active');

  check(banner.classList.contains('pausado') === false, 'arranca sin pausa');
  pulsar(' ');
  check(banner.classList.contains('pausado') === true, 'la barra espaciadora pausa');
  check(aviso.hidden === false, 'y se avisa en pantalla de que está en pausa');
  pulsar(' ');
  check(banner.classList.contains('pausado') === false, 'volver a pulsarla reanuda');
  check(aviso.hidden === true, 'el aviso desaparece al reanudar');

  /* La barra espaciadora desplaza la página por defecto: hay que impedirlo cuando la
     usamos nosotros, o pausar el banner daría además un salto de scroll. */
  check(impedido >= 2, 'se impide el desplazamiento por defecto de la página');

  /* Con el visor de obra abierto la tecla es suya, no del banner. */
  document.getElementById('zoomModal').classList.add('active');
  pulsar(' ');
  check(banner.classList.contains('pausado') === false,
    'con el visor abierto la barra espaciadora no toca el banner');
  document.getElementById('zoomModal').classList.remove('active');

  check(html.includes('banner-atajos'), 'la pista del atajo está en la página');

  /* Al reanudar hay que devolverle a t0 el tiempo que estuvo parado; si no, la obra
     saltaría de golpe por todo el rato de la pausa. El reloj del simulacro no avanza,
     así que esto no se puede probar por comportamiento: se comprueba que la compensación
     sigue en el código, para que no se borre por descuido. */
  check(/t0 \+= Date\.now\(\) - pausadoEn/.test(html),
    'al reanudar se compensa el tiempo detenido');
}

console.log('\n== Biblioteca ==');
{
  const reales = Object.keys(BOOKS).filter(k => BOOKS[k].esLibro);
  const botones = [...html.matchAll(/class="book-btn[^"]*"[^>]*onclick="switchBook\('([a-z]+)'/g)].map(m => m[1]);

  /* Esta es la propiedad que se pidió: que añadir libros no alargue la barra de arriba.
     Si algún día vuelve a colarse un botón por libro, esto lo caza. */
  const conLibro = botones.filter(b => reales.includes(b));
  check(conLibro.length === 0,
    `ningún libro tiene botón propio en la barra superior (${botones.join(', ')})`);
  check(botones.includes('biblioteca'), 'la Biblioteca sí está en la barra');

  const rejilla = document.getElementById('bibliotecaLibros');
  const tarjetas = (rejilla.innerHTML.match(/biblio-card/g) || []).length;
  check(tarjetas === reales.length, `una tarjeta por libro (${tarjetas} de ${reales.length})`);
  check(reales.every(id => rejilla.innerHTML.includes(`data-libro="${id}"`)),
    'cada libro es alcanzable desde la Biblioteca');
  const portadas = [...rejilla.innerHTML.matchAll(/biblio-portada" style="background-image:url\('([^']+)'\)/g)]
    .map(m => decodeURIComponent(m[1]));
  check(portadas.length === reales.length && portadas.every(u => fs.existsSync(u)),
    `cada tarjeta lleva portada existente (${portadas.length})`);

  /* El buscador solo tiene sentido cuando la lista deja de leerse de un vistazo. */
  check(document.getElementById('biblioFiltro').hidden === (reales.length <= 6),
    `el buscador aparece solo con más de 6 libros (ahora ${reales.length}, oculto=${document.getElementById('biblioFiltro').hidden})`);

  check(BOOKS.biblioteca && BOOKS.biblioteca.firstTab === 'biblioteca-gallery',
    'la Biblioteca es una sección de primer nivel');
}

console.log('\n== Índices del marcado de Génesis (tarjetas a mano) ==');
for (const m of html.matchAll(/swapCardThumb\('thumb-(\d+)',\s*'([^']+)',\s*this,\s*(\d+),\s*(\d+)\)/g)) {
  const [, n, src, g, s] = m;
  const e = BOOKS.genesis.groups[+g] && BOOKS.genesis.groups[+g][+s];
  check(!!e && e.src === src && +n - 1 === +g, `thumb-${n} -> groups[${g}][${s}] ${src.split('/').pop()}`);
}
for (const n of new Set([...html.matchAll(/toggleCardDrawer\((\d+)/g)].map(m => m[1])))
  check(html.includes(`id="drawer-${n}"`), `toggleCardDrawer(${n}) tiene su drawer`);

console.log('\n' + (fails === 0 ? '*** TODO CORRECTO ***' : `*** ${fails} FALLAS ***`));
process.exit(fails === 0 ? 0 : 1);
