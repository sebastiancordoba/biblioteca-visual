/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen. */
process.chdir(require('path').join(__dirname, '..'));
/* Ejercita el buscador general (la lupa de la barra superior) con el JavaScript real de
   index.html: que la lupa exista y sea la última de la barra, que las erratas y los
   nombres en inglés encuentren lo que deben, que los campos acoten, y —lo que de verdad
   importa— que cada resultado apunte a la obra correcta del visor, no a otra del mismo
   título. */
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const { ejecutar } = require('./dom_falso.js');
const r = ejecutar(html,
  '{BOOKS, abrir: window.abrirBuscadorGeneral, buscar: window.buscarEnColeccion}');

let fallos = 0;
const comprobar = (ok, texto) => {
  console.log(`${ok ? '  ok    ' : '  FALLA '}${texto}`);
  if (!ok) fallos++;
};

/* La lupa va detrás de todos los botones de sección, también de los que inserta la
   construcción después de la Biblioteca. */
const barra = html.match(/<div class="book-switch">([\s\S]*?)<\/div>/);
comprobar(barra && /id="lupaGeneral"[\s\S]*<\/button>\s*$/.test(barra[1]) &&
          barra[1].lastIndexOf('book-btn') < barra[1].indexOf('lupaGeneral'),
          'la lupa es el último elemento de la barra superior');
comprobar(typeof r.abrir === 'function' && typeof r.buscar === 'function',
          'el buscador general se monta');

const titulos = q => r.buscar(q).map(x => x.title);
const primero = q => titulos(q)[0] || '';

comprobar(/diluvio/i.test(primero('diluvio')), 'diluvio → una obra del Diluvio primero');
comprobar(/babel/i.test(primero('torre de babel')), 'torre de babel → la Torre de Babel primero');
comprobar(r.buscar('rembrant').length > 0 &&
          r.buscar('rembrant').length === r.buscar('rembrandt').length,
          'una errata («rembrant») da lo mismo que el nombre bien escrito');
comprobar(r.buscar('flood').length === r.buscar('diluvio').length,
          'el nombre en inglés («flood») encuentra lo mismo que en español');
comprobar(/aquiles/i.test(primero('achilles')), 'achilles → Aquiles');
comprobar(r.buscar('libro:iliada').every(x => x.libro === 'iliada') &&
          r.buscar('libro:iliada').length === r.BOOKS.iliada.details.length,
          'libro:iliada da exactamente las obras de la Ilíada');
comprobar(r.buscar('año:<-500').every(x => r.BOOKS[x.libro].details[x.i].anio < -500),
          'año:<-500 solo da obras anteriores al 500 a.C.');
const sinGrabado = r.buscar('diluvio -grabado');
comprobar(sinGrabado.length < r.buscar('diluvio').length, '-palabra excluye');
comprobar(r.buscar('xqzvwkj').length === 0, 'una consulta sin sentido no da nada');

/* Cada resultado debe abrir en el visor la obra que dice ser. */
let malos = 0, total = 0;
['a', 'e', 'o'].forEach(q => r.buscar(q).forEach(x => {
  total++;
  if (r.BOOKS[x.libro].details[x.i].title !== x.title) malos++;
}));
comprobar(total > 0 && malos === 0, `los ${total} resultados apuntan a su obra en el visor`);
comprobar(r.buscar('e').length <= r.BOOKS.inicio.details.length, 'ninguna obra sale dos veces');

/* Abrir la capa no debe romper nada, ni con el campo vacío. */
let error = null;
try { r.abrir(); } catch (e) { error = e; }
comprobar(!error, 'la capa se abre' + (error ? ': ' + error.message : ''));

console.log('\n' + (fallos === 0 ? '*** BUSCADOR GENERAL CORRECTO ***' : `*** ${fallos} FALLAS ***`));
process.exit(fallos ? 1 : 0);
