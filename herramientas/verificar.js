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
const { BOOKS, document } = ejecutar(html, '{BOOKS}');

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
