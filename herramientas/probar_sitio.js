/* Comprueba la versión de GitHub Pages (build/sitio/), que construye
   herramientas/sitio/construir_sitio.py. Ejecuta su JavaScript real con el DOM simulado. */
process.chdir(require('path').join(__dirname, '..'));
const fs = require('fs'), path = require('path');
const { ejecutar } = require('./dom_falso.js');
const SITIO = 'build/sitio';
let bad = 0; const ck = (o, m) => { console.log((o ? '  ok    ' : '  FALLA ') + m); if (!o) bad++; };
if (!fs.existsSync(SITIO + '/index.html')) { console.log('  FALLA falta build/sitio: python3 herramientas/sitio/construir_sitio.py'); process.exit(1); }
const html = fs.readFileSync(SITIO + '/index.html', 'utf8');

console.log('== documento y teléfono ==');
/* Se publicó meses sin nada de esto: sin doctype el navegador iba en modo quirks, y sin
   viewport un teléfono maquetaba la página a 980 px y la encogía, de modo que ninguna regla
   pensada para pantalla estrecha llegaba a aplicarse. */
ck(/^<!DOCTYPE html>\s*<html lang="es">\s*<head>\s*<meta charset="UTF-8">/i.test(html), 'documento completo: doctype, <html lang>, <head> y charset');
ck(/<meta name="viewport" content="[^"]*width=device-width[^"]*viewport-fit=cover/.test(html), 'viewport de teléfono, con viewport-fit=cover para la muesca');
ck((html.match(/<body>/g) || []).length === 1 && /<\/body>\s*<\/html>\s*$/.test(html), 'un solo <body>, cerrado al final');
ck(/<link rel="manifest" href="manifest.webmanifest">/.test(html) && fs.existsSync(SITIO + '/manifest.webmanifest'),
   'manifiesto de aplicación para «Añadir a pantalla de inicio»');
const man = JSON.parse(fs.readFileSync(SITIO + '/manifest.webmanifest', 'utf8'));
ck(man.display === 'standalone' && man.icons.every(i => fs.existsSync(path.join(SITIO, i.src))), 'se abre como aplicación y sus iconos existen');

console.log('\n== imágenes ==');
const refs = [...html.matchAll(/["'(]((?:\.\/)?[^"'()\s]+\.(?:jpe?g|png))["')]/gi)].map(m => m[1]);
const locales = refs.filter(r => !/^https?:/.test(r));
const rotas = locales.filter(r => !fs.existsSync(path.join(SITIO, r)));
ck(rotas.length === 0, `${locales.length} referencias a archivos del sitio, ${rotas.length} rotas` + (rotas.length ? ': ' + rotas.slice(0, 3).join(' ') : ''));
ck(!locales.some(r => /^(\.\/)?(Génesis|Gilgamesh|Ilíada|Atrahasis|Enuma_Elish)\//.test(r)), 'ninguna apunta a las carpetas de la colección, que no se publican');
/* Los créditos enlazan la página de cada archivo en Commons (…/wiki/File:x.jpg): es un enlace, no una imagen. */
const remotas = [...new Set(refs.filter(r => /^https?:/.test(r) && !r.includes('commons.wikimedia.org/wiki/')))];
ck(remotas.every(u => u.startsWith('https://upload.wikimedia.org/wikipedia/commons/')), `${remotas.length} imágenes remotas, todas de Commons`);
/* thumb/5/5b/<nombre>/1280px-<nombre>: sin el nombre repetido Commons da 404, que es como falló la primera vez. */
/* …o «1280px-thumbnail.jpg» cuando el nombre pasa de 160 bytes, como hace MediaWiki. */
const malas = remotas.filter(u => u.includes('/thumb/') && !/\/thumb\/\w\/\w\w\/([^/]+)\/(lossy-page1-)?\d+px-(\1|thumbnail\.\w+)(\.jpg)?$/.test(u));
ck(malas.length === 0, `miniaturas con el formato de Commons (${malas.length} mal formadas)` + (malas[0] ? ': ' + malas[0] : ''));

console.log('\n== el visor pide el original ==');
const hist = [];
const location = { hash: '#/genesis' };
const history = { pushState: (_, __, r) => { hist.push(r); location.hash = r; } };
class Image { set src(v) { this._src = v; Image.pedidas.push(v); } }
Image.pedidas = [];
const { HD, switchBook, pedirOriginal, prepararOriginal, inicial } =
  ejecutar(html, '{HD, switchBook, pedirOriginal, prepararOriginal, inicial: currentBook}', { location, history, Image });
ck(Object.keys(HD).length > 100, `${Object.keys(HD).length} imágenes con original en Commons`);
const [k0, e0] = Object.entries(HD).find(([, e]) => e.o !== e.v);
prepararOriginal(k0); pedirOriginal(); pedirOriginal();
ck(Image.pedidas.length === 1 && Image.pedidas[0] === e0.o, 'al acercar se pide el original, una sola vez');

console.log('\n== direcciones ==');
ck(inicial === 'genesis', `quien entra por #/genesis aterriza en el Génesis (${inicial})`);
switchBook('mapa');
ck(location.hash === '#/mapa', `cambiar de sección escribe la dirección (${location.hash})`);
switchBook('iliada');
ck(hist.slice(-2).join(' ') === '#/mapa #/iliada', 'cada cambio queda en el historial del navegador');

console.log('\n== entrar por la dirección de una obra ==');
/* «Abrir en el visor» en la página de una obra lleva a #/<libro>/obra/<n>: tiene que abrir
   esa obra, no la primera ni la de otro libro. */
{
  const loc2 = { hash: '#/iliada/obra/5' };
  const r = ejecutar(html, '{abierta: currentArtworkGroupIndex, libro: currentBook, FICHAS}',
    { location: loc2, history: { pushState() {} }, Image: class {} });
  ck(r.libro === 'iliada' && r.abierta === 5, `#/iliada/obra/5 abre la obra 5 de la Ilíada (${r.libro} ${r.abierta})`);
  ck(r.FICHAS && r.FICHAS.iliada && r.FICHAS.iliada.length > 20, 'el visor sabe la dirección de la página de cada obra');
}

console.log(bad ? `\n*** ${bad} FALLAS ***` : '\ntodo en orden'); process.exit(bad ? 1 : 0);
