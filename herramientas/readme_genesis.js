/* Regenera Génesis/README.md desde los datos que ya viven en index.html, de modo que la
   tabla del libro no se desincronice del visor. Uso: node herramientas/readme_genesis.js */
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const js = html.split('<script>')[1].split('</script>')[0];
const noop = () => {};
const el = new Proxy({}, { get: (t,p) => {
  if (p === 'classList') return {add:noop, remove:noop, contains:()=>false, toggle:noop};
  if (p === 'querySelectorAll') return () => ({forEach:noop});
  if (p === 'querySelector' || p === 'closest') return () => el;
  if (p === 'dataset' || p === 'style') return {};
  if (p === 'getBoundingClientRect') return () => ({});
  return noop; }});
const { BOOKS } = new Function('document','window','requestAnimationFrame',
  js + '\n;return {BOOKS};')(
  {getElementById:()=>el, querySelectorAll:()=>({forEach:noop}), querySelector:()=>el, addEventListener:noop},
  {addEventListener:noop, scrollTo:noop}, noop);

const { details, groups } = BOOKS.genesis;
const L = [
 '# Colección Obras Maestras del Génesis', '',
 'Las representaciones pictóricas más icónicas del Libro del Génesis y su significado artístico,',
 'teológico y filosófico. El visor de la colección vive ahora en la raíz del proyecto:',
 'abre [`../index.html`](../index.html) y elige **Génesis** en el selector de libros.', '',
 '---', '', `## 🎨 Galería de la Colección (${details.length} obras)`, '',
 '| N° | Obra | Artista | Ubicación | Wikipedia | Archivo de Imagen |',
 '|---|---|---|---|---|---|'];

details.forEach((d, i) => {
  const ubic = d.meta.split('|').pop().trim();
  const main = groups[i][0].src.split('/').pop();
  L.push(`| ${i+1} | **${d.title}** | ${d.artist} | ${ubic} | [Wikipedia](${d.wikiUrl}) | [\`${main}\`](./${main}) |`);
});

L.push('', '---', '', '## 🖼️ Análisis Detallado de las Obras', '');
details.forEach((d, i) => {
  L.push(`### ${i+1}. ${d.title} — ${d.artist}`, '');
  groups[i].forEach(v => L.push(`![${d.title}](./${v.src.split('/').pop()})`, `*${v.title}*`, ''));
  L.push('**Ficha técnica:** ' + d.meta, '',
         '#### Lo que hace que destaque', '', d.analysis, '',
         '#### Contexto histórico', '', d.history, '',
         '#### Sobre el artista', '', d.bio, '', '---', '');
});

L.push('## 📜 Estudio Teológico y Literario', '',
 '### ¿Por qué el Génesis cambia tan radicalmente después de la Torre de Babel?',
 '*(Ensayo completo en [Ensayo_Genesis_Post_Babel.md](./Ensayo_Genesis_Post_Babel.md);',
 'también disponible como pestaña dentro del visor.)*', '');

fs.writeFileSync('Génesis/README.md', L.join('\n'));
console.log(`Génesis/README.md regenerado con ${details.length} obras`);
