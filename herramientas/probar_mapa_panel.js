/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* El panel del mapa. Antes, llegar a un museo exigía una cadena de círculos —el grupo
   de 17 volaba a uno de 4, que volaba a un abanico de 3—: cuatro clics para el British
   Museum. La propiedad que se comprueba aquí es la que motivó el panel: desde el mundo,
   CUALQUIER museo está a dos clics (su círculo y su fila), y sus obras a uno más. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};const oyDoc={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},_html:'',_tc:'',
 hidden:true,children:[],offsetWidth:272,offsetHeight:28,_attrs:{},_ev:{},
 get innerHTML(){return this._html;},set innerHTML(v){this._html=v;this.children=[];},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);c.padre=this;return c;},
 get parentNode(){ if(!this.padre){ this.padre=mk('padre-'+id); this.padre.children.push(this);} return this.padre; },
 insertBefore(n,r){const i=this.children.indexOf(r);this.children.splice(i<0?this.children.length:i,0,n);n.padre=this;return n;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>null,
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),
 addEventListener(t,f){(oyDoc[t]=oyDoc[t]||[]).push(f);}};
const win={addEventListener:noop,scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js+';\nwindow.__SEDES = SEDES;')(document,win,rAF,global.ResizeObserver,cAF);
OCULTO=false; RO(); drenar(400);
const SEDES=win.__SEDES;

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
const tiene=(el,c)=>((el.getAttribute&&el.getAttribute('class')||'')+' '+(el.className||'')+' '+[...el.classList._s].join(' ')).split(/\s+/).includes(c);
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const ev={stopPropagation:noop,preventDefault:noop};
const panel=store['mapaMarco'].children.find(c=>c.id==='mapaPanel');
const enPanel=()=>aplanar(panel?panel.children:[]);
const filas=()=>enPanel().filter(e=>tiene(e,'mp-sede'));
const nombreFila=f=>(f.children.find(c=>tiene(c,'mp-nom'))||{})._tc;
const titulo=()=>{const s=enPanel().find(e=>e.tag==='strong');return s?s._tc:'';};
const miniaturas=()=>enPanel().filter(e=>tiene(e,'mp-obra'));
/* Los círculos de primer nivel: los que tienen manejador propio y no son del abanico. */
const puntos=()=>aplanar(store['capaSedes'].children)
  .filter(g=>g._ev.click&&tiene(g,'sede')&&!tiene(g,'sede-abanico'));
const activas=SEDES.filter(s=>s.obras.length);

ck(!!panel,'el panel existe dentro del marco');
ck(panel&&panel.hidden,'arranca cerrado');

console.log('== desde el mundo, cada museo a dos clics ==');
oyentes.mTodo.click(); drenar(400);
const nPuntos=puntos().length;
console.log(`   ${nPuntos} círculos en la vista del mundo`);
const alcanzadas=new Set();
for(let k=0;k<nPuntos;k++){
  oyentes.mTodo.click(); drenar(400);
  const p=puntos()[k];
  if(!p) continue;
  p._ev.click(ev); drenar(400);
  if(panel.hidden) continue;
  const fs_=filas();
  if(fs_.length) fs_.forEach(f=>alcanzadas.add(nombreFila(f)));
  else alcanzadas.add(titulo());
}
const faltan=activas.filter(s=>!alcanzadas.has(s.nombre)).map(s=>s.nombre);
ck(faltan.length===0,`las ${activas.length} sedes aparecen en el panel del círculo que las contiene`+
   (faltan.length?` — faltan: ${faltan.slice(0,5).join(', ')}`:''));

console.log('\n== un grupo de varias ciudades ==');
oyentes.mTodo.click(); drenar(400);
const anchoMundo=vb()[2];
const mayor=puntos().filter(g=>tiene(g,'grupo'))
  .map(g=>({g,n:+(((g.getAttribute('aria-label')||'').match(/^(\d+) sedes/)||[])[1]||0)}))
  .sort((a,b)=>b.n-a.n)[0];
mayor.g._ev.click(ev); drenar(600);
ck(!panel.hidden,'pulsarlo abre el panel');
ck(filas().length===mayor.n,`con una fila por museo (${filas().length} de ${mayor.n})`);
ck(enPanel().some(e=>tiene(e,'mp-ciudad')),'agrupadas por ciudad');
ck(vb()[2]<anchoMundo*0.6,'y el mapa se acerca igualmente, como contexto');
ck(miniaturas().length===0,'todavía sin obras desplegadas: solo la lista');

console.log('\n== una fila de museo que comparte ciudad ==');
/* Londres o París: un museo que comparte ciudad quedaba escondido dentro del grupo de
   su ciudad al encuadrarlo solo. Ahora se vuela a la ciudad con el abanico abierto. */
const ciudadDe=n=>(SEDES.find(s=>s.nombre===n)||{}).ciudad;
const cuenta=c=>activas.filter(s=>s.ciudad===c).length;
const fila=filas().find(f=>cuenta(ciudadDe(nombreFila(f)))>1)||filas()[0];
const nom=nombreFila(fila), sd=SEDES.find(s=>s.nombre===nom);
console.log(`   ${nom} (${sd.ciudad})`);
fila._ev.click(ev); drenar(600);
ck(miniaturas().length===sd.obras.length,`despliega sus ${sd.obras.length} obras en el panel`);
ck(filas().length===mayor.n,'sin perder el resto de la lista');
ck(filas().filter(f=>tiene(f,'abierta')).length===1,'marcada como abierta');
if(cuenta(sd.ciudad)>1){
  const aba=aplanar(store['capaSedes'].children).filter(g=>tiene(g,'sede-abanico'));
  ck(aba.length===cuenta(sd.ciudad),`el mapa abre el abanico de ${sd.ciudad} (${aba.length} museos)`);
  ck(aba.filter(g=>tiene(g,'sel')).length===1,'con el museo elegido marcado');
}
const antes=miniaturas().length;
fila._ev.click(ev); drenar(200);
const filaOtra=filas().find(f=>nombreFila(f)===nom);
ck(miniaturas().length===0&&antes>0,'pulsarla otra vez la pliega');
filaOtra._ev.click(ev); drenar(600);

console.log('\n== una obra del panel abre el visor ==');
let abierta=null;
const orig=win.__abrir;
try{
  const m=miniaturas()[0];
  m._ev.click(ev);
  abierta=store['zoomModal']&&store['zoomModal'].classList.contains('active');
  ck(true,'pulsar la miniatura no lanza');
}catch(e){ ck(false,'pulsar la miniatura lanza: '+e.message); }
if(abierta!==null) console.log(`   visor activo: ${abierta}`);
store['zoomModal']&&store['zoomModal'].classList.remove('active');

console.log('\n== cerrar ==');
const cerrar=enPanel().find(e=>tiene(e,'mp-cerrar'));
cerrar._ev.click(ev);
ck(panel.hidden,'la × lo cierra');
ck(!tiene(store['mapaMarco'],'con-panel'),'y devuelve la pista al mapa');
mayor.g._ev&&oyentes.mTodo.click(); drenar(400);
puntos().filter(g=>tiene(g,'grupo'))[0]._ev.click(ev); drenar(400);
ck(!panel.hidden,'reabierto');
(oyDoc.keydown||[]).forEach(f=>f({key:'Escape',preventDefault:noop,metaKey:false,ctrlKey:false,altKey:false}));
ck(panel.hidden,'Esc lo cierra');
puntos().filter(g=>tiene(g,'grupo'))[0]._ev.click(ev); drenar(400);
oyentes.mapaMarco.click({target:{closest:()=>null}});
ck(panel.hidden,'pulsar el mapa vacío lo cierra');
puntos().filter(g=>tiene(g,'grupo'))[0]._ev.click(ev); drenar(400);
oyentes.mapaMarco.click({target:{closest:()=>({})}});
ck(!panel.hidden,'los botones del mapa (acercar, continentes) no lo cierran al burbujear');

console.log('\n== el encuadre deja sitio al panel ==');
{
  /* Lo pulsado debe caer en la parte libre, a la derecha del panel, no debajo de él. */
  oyentes.mTodo.click(); drenar(400);
  const solo=puntos().find(g=>!tiene(g,'grupo'));
  solo._ev.click(ev); drenar(600);
  const nomS=titulo();
  const s=SEDES.find(x=>x.nombre===nomS)||SEDES.find(x=>filas().some(f=>nombreFila(f)===x.nombre));
  const v=vb();
  const px=(((s.x-v[0])%1980+1980)%1980)/v[2]*900;
  console.log(`   ${s.nombre}: a ${px.toFixed(0)} px del borde izquierdo (panel hasta ${272+12} px)`);
  ck(px>272+12,'la sede queda fuera del panel');
}

console.log(bad?`\n*** ${bad} FALLAS ***`:'\n*** SIN ERRORES ***');
process.exit(bad?1:0);
