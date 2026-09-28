/* Comprueba las páginas estáticas del sitio de GitHub Pages (herramientas/sitio/paginas.py). */
process.chdir(require('path').join(__dirname, '..'));
const fs = require('fs'), path = require('path');
const { ejecutar } = require('./dom_falso.js');
const SITIO = 'build/sitio';
let bad = 0; const ck = (o, m) => { console.log((o ? '  ok    ' : '  FALLA ') + m); if (!o) bad++; };
if (!fs.existsSync(SITIO + '/libros/index.html')) { console.log('  FALLA falta build/sitio: python3 herramientas/sitio/construir_sitio.py'); process.exit(1); }

const paginas = [];
(function recorrer(d) { for (const f of fs.readdirSync(d)) { const p = path.join(d, f);
  if (fs.statSync(p).isDirectory()) recorrer(p); else if (f === 'index.html' && p !== path.join(SITIO, 'index.html')) paginas.push(p); } })(SITIO);

console.log('== enlaces e imágenes ==');
let enlaces = 0; const rotos = [];
for (const p of paginas) {
  const html = fs.readFileSync(p, 'utf8');
  for (const [, u] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (/^(https?:|mailto:|#)/.test(u)) continue;
    const limpio = decodeURIComponent(u.split('#')[0]);
    if (!limpio) continue;                          // "../#/mapa": la raíz, que existe
    let dst = path.resolve(path.dirname(p), limpio);
    if (limpio.endsWith('/') || (fs.existsSync(dst) && fs.statSync(dst).isDirectory())) dst = path.join(dst, 'index.html');
    enlaces++; if (!fs.existsSync(dst)) rotos.push(`${p.slice(SITIO.length)} → ${u}`);
  }
}
ck(rotos.length === 0, `${paginas.length} páginas, ${enlaces} enlaces internos, ${rotos.length} rotos` + (rotos.length ? '\n        ' + rotos.slice(0, 5).join('\n        ') : ''));

console.log('\n== cada obra de la aplicación tiene su página ==');
const html = fs.readFileSync(SITIO + '/index.html', 'utf8');
const { BOOKS, FICHAS } = ejecutar(html, '{BOOKS, FICHAS}', { location: { hash: '' }, history: { pushState() {} }, Image: class {} });
const libros = Object.keys(BOOKS).filter(k => BOOKS[k].esLibro);
const faltan = [];
for (const l of libros) BOOKS[l].details.forEach((d, i) => {
  const r = (FICHAS[l] || [])[i];
  if (!r || !fs.existsSync(path.join(SITIO, r, 'index.html'))) faltan.push(`${l} ${i}`);
});
ck(faltan.length === 0, `${libros.reduce((n, l) => n + BOOKS[l].details.length, 0)} obras, ${faltan.length} sin página`);
/* El índice de la página tiene que ser el del visor: la obra 12 de la página abre la 12. */
const desajustes = [];
for (const l of libros) BOOKS[l].details.forEach((d, i) => {
  const p = fs.readFileSync(path.join(SITIO, FICHAS[l][i], 'index.html'), 'utf8');
  const h1 = (p.match(/<h1>([^<]*)<\/h1>/) || [])[1] || '';
  const abre = (p.match(new RegExp(`#/${l}/obra/(\\d+)"`)) || [])[1];
  const tit = d.title.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
  if (h1 !== tit || +abre !== i) desajustes.push(`${l} ${i}: «${h1}» abre ${abre}`);
});
ck(desajustes.length === 0, `título y «Abrir en el visor» coinciden con el índice del visor (${desajustes.length} desajustes)` + (desajustes[0] ? ': ' + desajustes[0] : ''));

console.log('\n== para compartir y para buscadores ==');
const obras = paginas.filter(p => p.includes('/obras/'));
const sinOg = obras.filter(p => !/<meta property="og:image" content="https:\/\/[^"]+"/.test(fs.readFileSync(p, 'utf8')));
ck(sinOg.length === 0, `todas las obras con og:image absoluta (${sinOg.length} sin ella)`);
const mapaSitio = fs.readFileSync(SITIO + '/sitemap.xml', 'utf8');
ck((mapaSitio.match(/<loc>/g) || []).length >= obras.length + libros.length, `sitemap.xml con ${(mapaSitio.match(/<loc>/g) || []).length} direcciones`);
ck(fs.existsSync(SITIO + '/404.html') && fs.existsSync(SITIO + '/robots.txt'), '404.html y robots.txt');

console.log(bad ? `\n*** ${bad} FALLAS ***` : '\ntodo en orden'); process.exit(bad ? 1 : 0);
