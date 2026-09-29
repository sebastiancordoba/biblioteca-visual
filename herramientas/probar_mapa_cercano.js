/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen. */
process.chdir(require('path').join(__dirname, '..'));
/* Reproduce el fallo reportado en Ciudad de México: acercarse con la rueda hasta que el
   MUNAL (2 obras) y el Museo Soumaya (1) se separan, y pulsar el Soumaya. Antes el clic
   volaba al cuadro regional de 42 unidades que encajarSedes da a una sede suelta: el mapa
   se alejaba, los museos se volvían a agrupar en el «4» y parecía que el clic devolvía a
   la vista general. Además se separaban con los discos todavía montados uno encima del
   otro, porque el umbral de agrupación no crecía con los marcadores. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const ANCHO=900, ALTO=506;
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},_html:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},
 get innerHTML(){return this._html;},set innerHTML(v){this._html=v;this.children=[];},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:ANCHO;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:ALTO;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);c.padre=this;return c;},
 get parentNode(){ if(!this.padre){ this.padre=mk('padre-'+id); this.padre.children.push(this);} return this.padre; },
 insertBefore(n,r){const i=this.children.indexOf(r);this.children.splice(i<0?this.children.length:i,0,n);n.padre=this;return n;},
 querySelectorAll(sel){const f=sel.replace('.','');
   const todos=(function w(n){return n.flatMap(c=>[c,...w(c.children||[])]);})(this.children);
   return todos.filter(x=>((x.getAttribute('class')||'')+' '+[...x.classList._s].join(' ')).split(/\s+/).includes(f));},
 querySelector(){return mk('x');},closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:ANCHO,height:ALTO}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
const {SEDES}=new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js+'\n;return {SEDES};')(document,win,rAF,global.ResizeObserver,cAF);
OCULTO=false; RO(); drenar(400);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
const tiene=(el,c)=>((el.getAttribute('class')||'')+' '+[...el.classList._s].join(' ')).split(/\s+/).includes(c);
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const marcas=()=>aplanar(store['capaSedes'].children).filter(x=>tiene(x,'marca'));
/* El punto de una sede suelta (no grupo ni museo dentro de un abanico) por su nombre. */
const puntoDe=nombre=>{
  for (const m of marcas()) {
    const p=(m.children||[]).find(c=>tiene(c,'sede')&&!tiene(c,'grupo')&&
      (c.getAttribute('aria-label')||'').startsWith(nombre+','));
    if (p) return { marca:m, p };
  }
  return null;
};

const munal=SEDES.findIndex(s=>/MUNAL/.test(s.nombre));
const soumaya=SEDES.findIndex(s=>/Soumaya/.test(s.nombre));
ck(munal>=0 && soumaya>=0, 'el MUNAL y el Museo Soumaya están en el mapa');
if (munal<0 || soumaya<0) process.exit(1);
const M=SEDES[munal], S=SEDES[soumaya];

console.log('== acercarse con la rueda sobre Ciudad de México ==');
/* Rueda hacia el punto medio de los dos museos, recalculando su posición en pantalla a
   cada paso, hasta que los dos aparecen como sedes sueltas o se llega al tope. */
const cx=(M.x+S.x)/2, cy=(M.y+S.y)/2;
let suelto=null, pasos=0;
while (pasos<400) {
  const v=vb();
  oyentes.mapaMarco.wheel({ preventDefault:noop, deltaY:-300, deltaX:0, ctrlKey:false,
    clientX:(cx-v[0])/v[2]*ANCHO, clientY:(cy-v[1])/v[3]*ALTO });
  drenar(400); pasos++;
  suelto=puntoDe('Museo Soumaya') && puntoDe('Museo Nacional de Arte (MUNAL)');
  if (suelto) break;
  if (Math.abs(vb()[2]-v[2])<1e-6) break;               // tope de acercamiento
}
const ancho=vb()[2];
console.log(`   ${pasos} pasos de rueda · ancho de vista ${ancho.toFixed(2)}`);

if (suelto) {
  /* Discos en pantalla: centro por la traslación de la marca; radio, el del círculo por
     la escala de la marca, que ya incluye factorMarca. */
  const s=ANCHO/ancho;
  const disco=nom=>{ const {marca,p}=puntoDe(nom);
    const inv=+marca.getAttribute('transform').match(/scale\(([^)]+)\)/)[1];
    const r=+p.children.find(c=>tiene(c,'pt')).getAttribute('r');
    return { x:+marca.dataset.x*s, y:+marca.dataset.y*s, r:r*inv*s }; };
  const a=disco('Museo Nacional de Arte (MUNAL)'), b=disco('Museo Soumaya');
  const d=Math.hypot(a.x-b.x,a.y-b.y);
  console.log(`   separados: ${d.toFixed(1)} px entre centros · radios ${a.r.toFixed(1)} + ${b.r.toFixed(1)}`);
  ck(d>=a.r+b.r, 'al separarse, los discos del MUNAL y el Soumaya no se montan');

  console.log('== pulsar el MUNAL y luego el Soumaya ==');
  puntoDe('Museo Nacional de Arte (MUNAL)').p._ev.click({ stopPropagation:noop }); drenar(600);
  const tras1=vb()[2];
  ck(tras1<=ancho*1.01, `pulsar el MUNAL no aleja (${ancho.toFixed(2)} -> ${tras1.toFixed(2)})`);
  const sm=puntoDe('Museo Soumaya');
  ck(!!sm, 'el Soumaya sigue siendo una sede suelta y se puede pulsar');
  if (sm) {
    sm.p._ev.click({ stopPropagation:noop }); drenar(600);
    const tras2=vb()[2];
    ck(tras2<=tras1*1.01, `pulsar el Soumaya no aleja (${tras1.toFixed(2)} -> ${tras2.toFixed(2)})`);
    ck(!!puntoDe('Museo Soumaya'), 'tras el clic el Soumaya no se ha vuelto a agrupar');
    const obras=aplanar(store['capaSedes'].children).filter(x=>tiene(x,'obra-pin'))
      .map(x=>x.getAttribute('aria-label'));
    ck(obras.some(t=>S.obras.some(o=>t.startsWith(o.t))), 'despliega la obra del Soumaya');
    const v=vb(), c={x:v[0]+v[2]/2, y:v[1]+v[3]/2};
    ck(Math.hypot(c.x-S.x,c.y-S.y)<v[2]*0.05, 'y queda centrado en él');
  }
} else {
  /* En el tope siguen juntos: entonces el grupo tiene que abrirse en abanico. */
  const g=marcas().flatMap(m=>m.children||[]).find(c=>tiene(c,'grupo'));
  ck(!!g, 'en el tope queda un grupo que pulsar');
}

console.log(bad ? `\n${bad} fallos` : '\ntodo en orden');
process.exit(bad ? 1 : 0);
