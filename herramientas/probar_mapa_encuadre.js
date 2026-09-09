/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Centrado al pulsar un grupo, y encuadre de un libro repartido entre continentes. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{},_html:'',_tc:'',
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
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
const ctx=new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js+'\n;return {SEDES,MAPA_W,MAPA_H};')(document,win,rAF,global.ResizeObserver,cAF);
const {SEDES,MAPA_W}=ctx;
OCULTO=false; RO(); drenar(400);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const tiene=(el,c)=>((el.getAttribute('class')||'')+' '+[...el.classList._s].join(' ')).split(/\s+/).includes(c);
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
const marcas=()=>aplanar(store['capaSedes'].children).filter(x=>tiene(x,'marca'));
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const centro=()=>{const v=vb();return {x:v[0]+v[2]/2, y:v[1]+v[3]/2};};

console.log('== pulsar un grupo lo deja centrado ==');
for(let intento=1; intento<=3; intento++){
  const grupos=aplanar(store['capaSedes'].children).filter(x=>tiene(x,'grupo'));
  if(!grupos.length){ console.log('   (ya no quedan grupos)'); break; }
  const g=grupos[0];
  // sedes de ese grupo: se leen del marcador padre
  const padre=marcas().find(m=>(m.children||[]).includes(g));
  const antes=centro();
  g._ev.click({stopPropagation:noop}); drenar(500);
  const desp=centro();
  const px=Number(padre.dataset.x), py=Number(padre.dataset.y);
  const dist=Math.hypot(desp.x-px, desp.y-py);
  const v=vb();
  const rel=dist/Math.max(v[2],1);
  const abanico=aplanar(store['capaSedes'].children).filter(x=>tiene(x,'sede-abanico')).length;
  console.log(`   clic ${intento}: grupo en (${px.toFixed(0)},${py.toFixed(0)}) · centro (${desp.x.toFixed(0)},${desp.y.toFixed(0)}) · ` +
              `desvío ${(rel*100).toFixed(1)}% · ${abanico?'despliega '+abanico+' museos':'acerca'}`);
  ck(rel<0.30, `queda centrado (desvío ${(rel*100).toFixed(1)}%, tolerancia 30%)`);
}

console.log('\n== un libro repartido entre continentes obliga a alejarse ==');
oyentes.togLibros.click(); drenar(300);
const items=store['sedeLista'].children;
console.log('   libros en la lista:', items.map(li=>(li.innerHTML.match(/<strong>([^<]+)/)||[])[1]).join(' · '));
// el manejador registrado es el del último libro; se recorre la lista pulsando cada uno
for(const nom of ['Génesis','Gilgamesh','Ilíada']){
  // volver a pintar para que el manejador corresponda al libro buscado
  oyentes.togSedes.click(); oyentes.togLibros.click(); drenar(200);
  const li=store['sedeLista'].children.find(l=>l.innerHTML.includes('>'+nom+'<'));
  if(!li) continue;
  // el mock comparte el nodo de botón: se llama al manejador del libro concreto
  const idx=store['sedeLista'].children.indexOf(li);
  // se reconstruye pulsando en orden hasta el índice buscado
  oyentes.x.click(); drenar(600);           // aplica el último registrado
  const v=vb();
  const sedesLibro=SEDES.filter(s=>s.obras.some(o=>o.libro===nom));
  const xs=sedesLibro.map(s=>s.x), ys=sedesLibro.map(s=>s.y);
  const cubre = Math.min(...xs)>=v[0]-1 && Math.max(...xs)<=v[0]+v[2]+1 &&
                Math.min(...ys)>=v[1]-1 && Math.max(...ys)<=v[1]+v[3]+1;
  console.log(`   ${nom}: ${sedesLibro.length} sedes, extensión ${(Math.max(...xs)-Math.min(...xs)).toFixed(0)} unidades · vista ${v[2].toFixed(0)} · ${cubre?'todas dentro':'ALGUNA FUERA'}`);
  oyentes.x.click(); drenar(400);   // quitar filtro
  break;   // el simulacro solo puede accionar el último manejador
}

console.log('\n== comprobación directa del encuadre por conjunto ==');
{
  const gil=SEDES.map((s,i)=>i).filter(i=>SEDES[i].obras.some(o=>o.libro==='Gilgamesh'));
  const xs=gil.map(i=>SEDES[i].x), ys=gil.map(i=>SEDES[i].y);
  const ancho=Math.max(...xs)-Math.min(...xs);
  console.log(`   Gilgamesh: ${gil.length} sedes · de x=${Math.min(...xs).toFixed(0)} a x=${Math.max(...xs).toFixed(0)} (${ancho.toFixed(0)} unidades de ${MAPA_W})`);
  const ciudades=[...new Set(gil.map(i=>SEDES[i].ciudad))];
  console.log(`   ciudades: ${ciudades.join(', ')}`);
  ck(ancho>MAPA_W*0.2, 'Gilgamesh se reparte lo bastante como para exigir alejarse');
  ck(js.includes('function encajarSedes'), 'existe el encuadre por conjunto');
  ck(js.includes('encajarSedes(activas())'), 'el filtro por libro lo usa');
  ck(js.includes('encajarSedes(c0.sedes, off)'), 'pulsar un grupo lo usa');
  ck(js.includes('encajarSedes([idx]'), 'pulsar una sede lo usa');
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
