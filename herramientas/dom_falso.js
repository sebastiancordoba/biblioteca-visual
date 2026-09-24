/* DOM simulado compartido por las comprobaciones que ejecutan el JS de index.html
   sin navegador (verificar.js, probar_render.js).

   Es deliberadamente mínimo, pero con identidad estable: getElementById devuelve
   siempre el mismo objeto para el mismo id, de modo que lo que el script construye
   —las láminas del banner, el HTML de cada cuadrícula— queda inspeccionable después.
   Estaba duplicado y a medias en cada archivo de prueba, y cada vez que la página
   usaba una función nueva del DOM la prueba se caía por el mock, no por un fallo real. */
const noop = () => {};

/* Registro de elementos por id. Un elemento queda localizable con getElementById en
   cuanto se le asigna un id, igual que en un navegador; antes el simulacro creaba uno
   nuevo para CUALQUIER id que se le pidiera, así que «¿existe ya este nav?» respondía
   siempre que sí y el código que monta secciones nuevas no montaba nada. */
let registroActual = null;

function crearEl(idInicial) {
  const hijos = [], clases = new Set(), oyentes = {};
  let _id = idInicial;
  const self = {
    get id(){ return _id; },
    set id(v){ _id = v; if (v && registroActual) registroActual.set(v, self); },
    dataset: {}, children: hijos, oyentes,
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
    /* Todo elemento tiene padre, aunque sea uno sintético: la página monta cosas con
       grid.parentNode.insertBefore(...) y sin esto la prueba se caía por el simulacro. */
    get parentNode(){ if (!self.padre) { self.padre = crearEl('padre-de-' + _id);
                                         self.padre.children.push(self); } return self.padre; },
    insertBefore: (nuevo, ref) => {
      const i = hijos.indexOf(ref);
      hijos.splice(i < 0 ? hijos.length : i, 0, nuevo);
      nuevo.padre = self; return nuevo;
    },
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
  registroActual = porId;
  /* Ids presentes en el marcado: esos existen desde el principio. */
  const enHtml = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
  /* Los oyentes de document se guardan para poder dispararlos desde las pruebas: el
     teclado de la portada se registra ahí y con un noop no habría forma de ejercitarlo. */
  const oyentesDoc = {};
  const document = {
    oyentes: oyentesDoc,
    getElementById: id => {
      if (porId.has(id)) return porId.get(id);
      if (enHtml.has(id)) { const e = crearEl(id); porId.set(id, e); return e; }
      return null;     // como un navegador: lo que no existe, no existe
    },
    createElement: () => crearEl('nuevo'),
    createTextNode: () => crearEl('texto'),
    querySelector: () => crearEl('?'),
    querySelectorAll: () => [],
    addEventListener: (ev, fn) => { (oyentesDoc[ev] = oyentesDoc[ev] || []).push(fn); },
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
