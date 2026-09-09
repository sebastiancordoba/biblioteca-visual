/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Toggle Sedes/Libros, filtrado del mapa y fluidez del redibujado. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
let creados=0;
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},_html:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},
 get innerHTML(){return this._html;},set innerHTML(v){this._html=v;this.children=[];},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll(sel){const f=sel.replace('.','');
   const todos=(function w(n){return n.flatMap(c=>[c,...w(c.children||[])]);})(this.children);
   return todos.filter(x=>((x.getAttribute('class')||'')+' '+[...x.classList._s].join(' ')).split(/\s+/).includes(f));},
 querySelector(){return mk('x');},closest:()=>mk('x'),
 /* Se indexa por this.id, no por el id de creación: los botones de continente nacen
    de createElement y se les asigna el id después (mReset, mTodo). */
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>{creados++;return mk('e-'+t,t);},
 createElementNS:(ns,t)=>{creados++;return mk('s-'+t,t);},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js)(document,win,rAF,global.ResizeObserver,cAF);
OCULTO=false; RO(); drenar(300);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const tiene=(el,c)=>((el.getAttribute('class')||'')+' '+[...el.classList._s].join(' ')).split(/\s+/).includes(c);
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
const marcas=()=>aplanar(store['capaSedes'].children).filter(x=>tiene(x,'sede'));
const items=()=>store['sedeLista'].children;
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);

console.log('== toggle Sedes / Libros ==');
ck(!!(oyentes.togSedes&&oyentes.togSedes.click),'el botón Sedes existe');
ck(!!(oyentes.togLibros&&oyentes.togLibros.click),'el botón Libros existe');
const nSedes=items().length;
ck(nSedes>25,`modo Sedes: ${nSedes} entradas`);
oyentes.togLibros.click();
const libros=items().map(li=>li.innerHTML);
ck(items().length===3,`modo Libros: ${items().length} entradas`);
console.log('   '+libros.map(h=>(h.match(/<strong>([^<]+)/)||[])[1]+' ('+(h.match(/sede-n">(\d+)/)||[])[1]+')').join(' · '));
oyentes.togSedes.click();
ck(items().length===nSedes,'volver a Sedes restaura la lista');

console.log('\n== filtrar el mapa por libro ==');
oyentes.togLibros.click(); drenar(300);
const sinFiltro=marcas().length;
const obrasTodas=marcas().reduce((t,m)=>{
  const n=(m.children||[]).find(c=>c.tag==='text');
  return t+(Number(n&&n._tc)||0);},0);
/* En el simulacro, querySelector('button') devuelve siempre el mismo nodo, así que el
   último manejador registrado es el del tercer libro: La Ilíada. */
ck(!!(oyentes.x&&oyentes.x.click),'las entradas de libro tienen manejador');
oyentes.x.click(); drenar(500);
const conFiltro=marcas().length;
console.log(`   marcadores: ${sinFiltro} sin filtro -> ${conFiltro} filtrando por un libro`);
ck(conFiltro>0 && conFiltro<sinFiltro,'filtrar por libro reduce las sedes del mapa');
ck(store['sedeDetalle'].innerHTML.includes('obra-min'),'el panel de abajo muestra las obras de ese libro');
oyentes.x.click(); drenar(500);
/* El número de círculos depende de la escala, y filtrar mueve el encuadre: al quitar el
   filtro el mapa no vuelve al mismo sitio, así que contar marcadores da falsos fallos.
   Lo que sí tiene que volver es la suma de obras representadas. */
const obrasEnMapa = () => marcas().reduce((t,m) => {
  const n = (m.children||[]).find(c => c.tag === 'text');
  return t + (Number(n && n._tc) || 0);
}, 0);
/* Y hay que medir en el mismo encuadre: en la vista del mundo el lienzo se repite en
   horizontal, así que las mismas sedes se cuentan una vez por copia visible. */
oyentes.mTodo.click(); drenar(400);
console.log(`   obras en el mapa: ${obrasTodas} sin filtro · ${obrasEnMapa()} tras quitar el filtro`);
ck(obrasEnMapa()===obrasTodas,'volver a pulsarlo restaura todas las sedes');
oyentes.togSedes.click();

console.log('\n== fluidez: acercar no reconstruye marcadores ==');
oyentes.mReset.click(); drenar(400);
const antesNodos=creados;
oyentes.mZoomIn.click(); drenar(400);
const nuevos=creados-antesNodos;
/* Rehacer los marcadores en cada fotograma costaría del orden de 85 nodos x ~53
   fotogramas. Redibujar solo al cruzar un umbral de agrupación debe quedar muy por
   debajo de eso. */
const porFotograma=85*53;
console.log(`   nodos creados al acercar: ${nuevos} (rehacer cada fotograma costaría ~${porFotograma})`);
ck(nuevos < porFotograma*0.35,
   `acercar reutiliza los marcadores: ${nuevos} nodos, un ${Math.round(nuevos/porFotograma*100)}% del coste de rehacerlos`);
ck(js.includes('function reescalar'),'existe la vía ligera de reescalado');
ck(js.includes('firmaDibujo'),'solo se redibuja cuando cambia la disposición');

console.log('\n== inercia y suavidad ==');
ck(js.includes('function deslizar'),'el arrastre tiene inercia al soltar');
{
  /* No se comprueba una cifra concreta sino el criterio: cada muesca de rueda debe
     mover el zoom poco, para que la suavidad la ponga la interpolación y no el salto.
     Los márgenes se ensancharon al pedir «un poco más rápido»: la velocidad subió, pero
     el criterio de que ninguna muesca dé un salto grande sigue vigente. */
  const m = js.match(/Math\.abs\(ev\.deltaY\)\s*\/\s*(\d+)/);
  const tope = js.match(/clamp\(Math\.abs\(ev\.deltaY\)\s*\/\s*\d+\s*,\s*[\d.]+\s*,\s*([\d.]+)\)/);
  const div = m ? +m[1] : 0, max = tope ? +tope[1] : 1;
  console.log(`   divisor de rueda ${div} · salto máximo por muesca ${(max*100).toFixed(0)}%`);
  ck(div >= 250 && max <= 0.2, `los pasos de rueda son finos (divisor ${div}, tope ${(max*100).toFixed(0)}%)`);
}

console.log('\n== la sede elegida también despliega sus obras ==');
{
  const bloque = () => store['sedeLista'].children.find(c => (c.className||'') === 'libro-obras');
  oyentes.togSedes.click(); drenar(300);
  ck(!bloque(), 'sin sede elegida no hay desplegable');

  const primera = store['sedeLista'].children.find(c => (c.className||'').includes('sede-item'));
  ck(!!primera, 'la lista de sedes tiene entradas');
  if (primera) {
    primera._ev && primera._ev.click ? primera._ev.click() : null;
    // el manejador vive en el botón interior, que el simulacro no crea desde innerHTML:
    // se dispara el que quedó registrado por querySelector('button')
    if (oyentes.x && oyentes.x.click) oyentes.x.click();
    drenar(500);
    const b = bloque();
    ck(!!b, 'al pulsar una sede se despliegan sus obras');
    if (b) {
      const h = b.innerHTML;
      const n = (h.match(/class="libro-obra"/g) || []).length;
      const imgs = (h.match(/<img src="/g) || []).length;
      console.log(`   ${n} obras de la sede, ${imgs} con miniatura`);
      ck(n > 0 && imgs === n, `cada obra con su miniatura (${n})`);
      ck((h.match(/data-obra="\d+"/g) || []).length === n, 'cada una sabe qué obra abrir');
    }
    if (oyentes.x && oyentes.x.click) oyentes.x.click();
    drenar(400);
    ck(!bloque(), 'volver a pulsarla la repliega');
  }
}

console.log('\n== pellizco ==');
{
  /* El pellizco del trackpad llega como rueda con ctrlKey, pero con incrementos de
     unidades donde la rueda da centenares: con el divisor de la rueda se quedaba clavado
     en el paso mínimo. Se comprueba que tiene su propio camino y que el gesto responde. */
  ck(/if \(pellizco\) \{/.test(js), 'el pellizco tiene su propio tratamiento, no el de la rueda');
  ck(/Math\.exp\(-ev\.deltaY/.test(js), 'usa la relación exponencial propia del gesto');
  ck(/touchmove/.test(js) && /ev\.touches\.length === 2/.test(js), 'el pellizco táctil sigue ahí');

  const antes = vb()[2];
  oyentes.mapaMarco.wheel({ ctrlKey:true, deltaY:-12, deltaX:0, clientX:450, clientY:250,
                            preventDefault:noop });
  drenar(400);
  const tras = vb()[2];
  console.log(`   pellizco de -12: ancho ${antes.toFixed(0)} -> ${tras.toFixed(0)}`);
  ck(tras < antes * 0.995, `un pellizco pequeño ya acerca (${antes.toFixed(0)} -> ${tras.toFixed(0)})`);
}

console.log('\n== el libro elegido despliega sus obras ==');
{
  /* El desplegable se construye con innerHTML, que el simulacro guarda como texto sin
     parsear, así que se comprueba sobre el marcado generado y no sobre nodos. */
  const bloque = () => store['sedeLista'].children.find(c => (c.className||'') === 'libro-obras');
  oyentes.togLibros.click(); drenar(300);
  ck(!bloque(), 'sin libro elegido no hay desplegable');

  oyentes.x.click(); drenar(500);
  const b = bloque();
  ck(!!b, 'al pulsar un libro se despliega su lista de obras');
  if (b) {
    const h = b.innerHTML;
    const n = (h.match(/class="libro-obra"/g) || []).length;
    const imgs = (h.match(/<img src="/g) || []).length;
    console.log(`   ${n} obras desplegadas, ${imgs} con miniatura`);
    ck(n > 0, `salen las obras del libro (${n})`);
    ck(imgs === n, 'cada obra lleva su miniatura');
    ck((h.match(/data-obra="\d+"/g) || []).length === n, 'cada una sabe qué obra abrir');
    ck(!h.includes('${'), 'sin plantillas sin interpolar');
  }

  oyentes.x.click(); drenar(400);
  ck(!bloque(), 'volver a pulsarlo las repliega');
  oyentes.togSedes.click(); drenar(200);
  ck(!bloque(), 'al volver a Sedes tampoco queda el desplegable');
}

ck(!html.includes('id="capaRet"'),'la retícula del mar se ha eliminado');
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
