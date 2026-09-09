/* DOM simulado compartido por las comprobaciones que ejecutan el JS de index.html
   sin navegador (verificar.js, probar_render.js).

   Es deliberadamente mínimo, pero con identidad estable: getElementById devuelve
   siempre el mismo objeto para el mismo id, de modo que lo que el script construye
   —las láminas del banner, el HTML de cada cuadrícula— queda inspeccionable después.
   Estaba duplicado y a medias en cada archivo de prueba, y cada vez que la página
   usaba una función nueva del DOM la prueba se caía por el mock, no por un fallo real. */
const noop = () => {};

function crearEl(id) {
  const hijos = [], clases = new Set(), oyentes = {};
  const self = {
    id, dataset: {}, children: hijos, oyentes,
    /* style con setProperty: la página fija variables CSS (--alto-cabecera) y con un
       objeto pelado la prueba reventaba por el simulacro, no por un fallo real. */
    style: { setProperty(){}, removeProperty(){}, getPropertyValue: () => '' },
    innerHTML: '', innerText: '', textContent: '', className: '',
    classList: {
      add: (...c) => c.forEach(x => clases.add(x)),
      remove: (...c) => c.forEach(x => clases.delete(x)),
      contains: c => clases.has(c),
      toggle: (c, f) => (f === undefined ? (clases.has(c) ? clases.delete(c) : clases.add(c))
                                         : (f ? clases.add(c) : clases.delete(c))),
    },
    appendChild: n => { hijos.push(n); n.padre = self; return n; },
    removeChild: n => { const i = hijos.indexOf(n); if (i >= 0) hijos.splice(i, 1); return n; },
    remove: () => { if (self.padre) self.padre.removeChild(self); },
    addEventListener: (ev, fn) => { (oyentes[ev] = oyentes[ev] || []).push(fn); },
    removeEventListener: noop,
    querySelector: () => crearEl('?'),
    querySelectorAll: () => [],
    closest: () => crearEl('?'),
    getAttribute: () => null,
    setAttribute: noop,
    getBoundingClientRect: () => ({ width: 0, height: 0, left: 0, top: 0 }),
    focus: noop, blur: noop, click: noop, scrollIntoView: noop,
  };
  return self;
}

/* Ejecuta el <script> de un documento y devuelve lo que pida `devuelve`
   (una expresión JS, p. ej. '{BOOKS, renderBookGrid}'). Los temporizadores van
   inertes: ni el banner ni el mapa deben adelantar nada durante la comprobación. */
function ejecutar(html, devuelve) {
  const js = html.split('<script>')[1].split('</script>')[0];
  const porId = new Map();
  const document = {
    getElementById: id => { if (!porId.has(id)) porId.set(id, crearEl(id)); return porId.get(id); },
    createElement: () => crearEl('nuevo'),
    createTextNode: () => crearEl('texto'),
    querySelector: () => crearEl('?'),
    querySelectorAll: () => [],
    addEventListener: noop,
    body: crearEl('body'),
    documentElement: crearEl('html'),
  };
  const window = { addEventListener: noop, scrollTo: noop, innerWidth: 1280, innerHeight: 800 };
  const salida = new Function('document', 'window', 'requestAnimationFrame',
    'cancelAnimationFrame', 'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval',
    js + '\n;return ' + devuelve + ';')(document, window, noop, noop, noop, noop, noop, noop);
  return { document, window, ...salida };
}

module.exports = { noop, crearEl, ejecutar };
