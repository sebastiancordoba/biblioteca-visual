/* Saca los datos tal como los usa la página —BOOKS y AUTORES, ya filtrados y enriquecidos
   por inject.py y build.py— para que las páginas estáticas los lean sin reimplementar
   nada: la obra 12 de una página es la obra 12 del visor.
   Uso: node herramientas/sitio/extraer_datos.js build/pre_imagenes.html > datos.json */
const fs = require('fs');
const { ejecutar } = require('../dom_falso.js');
const html = fs.readFileSync(process.argv[2], 'utf8');
const { BOOKS, AUTORES } = ejecutar(html, '{BOOKS, AUTORES}', {
  location: { hash: '' }, history: { pushState() {} }, Image: class {} });
const libros = Object.entries(BOOKS).filter(([, b]) => b.esLibro).map(([id, b]) => ({
  id, corto: b.corto, tag: b.tag, title: b.title, sub: b.sub, headings: b.headings,
  carpeta: b.carpeta, details: b.details, groups: b.groups }));
process.stdout.write(JSON.stringify({ libros, autores: AUTORES }));
