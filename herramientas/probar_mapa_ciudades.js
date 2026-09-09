/* Reproduce el fallo reportado: acercarse hasta el tope sobre un grupo de museos de la
   misma ciudad y pulsarlo. Antes no ocurría nada visible. */
const fs=require('fs');
const html=fs.readFileSync('los-tres-libros.html','utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{},innerHTML:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;(oyentes[id]=oyentes[id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js)(document,win,rAF,global.ResizeObserver,cAF);
OCULTO=false; RO(); drenar(200);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
/* Cada marcador vive dentro de un <g class="marca"> con la transformación de escala,
   así que las sedes y los abanicos están un nivel por debajo. */
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
const sedes=()=>aplanar(store['capaSedes'].children);
/* El código asigna las clases con setAttribute('class',...), no con classList. */
const tiene=(el,c)=>((el.getAttribute('class')||'')+' '+[...el.classList._s].join(' ')).split(/\s+/).includes(c);
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const etiquetas=()=>sedes().flatMap(g=>g.children||[]).filter(c=>c.tag==='text'&&c._tc&&isNaN(Number(c._tc))).map(c=>c._tc);
const obras=()=>sedes().filter(x=>tiene(x,'obra-pin')).length;

console.log('== pulsar repetidamente un grupo, como haría un usuario ==');
oyentes.mReset.click(); drenar(300);
function gruposVista(){ return sedes().filter(g=>tiene(g,'grupo')); }
let historial=[];
for(let paso=1; paso<=7; paso++){
  const gs=gruposVista();
  if(!gs.length) break;
  const antes={sedes:sedes().length, ancho:vb()[2], abanico:sedes().filter(x=>tiene(x,'sede-abanico')).length};
  gs[0]._ev.click({stopPropagation:noop});
  drenar(400);
  const desp={sedes:sedes().length, ancho:vb()[2], abanico:sedes().filter(x=>tiene(x,'sede-abanico')).length};
  historial.push([paso, antes.ancho, desp.ancho, desp.abanico]);
  console.log(`   clic ${paso}: ancho ${antes.ancho.toFixed(0)} -> ${desp.ancho.toFixed(0)} · museos en abanico: ${desp.abanico}`);
  if(desp.abanico>0) break;
}
const ultima=historial[historial.length-1];
ck(!!ultima && ultima[3]>0, 'pulsando el grupo se acaba desplegando el abanico de museos');
const etq=etiquetas();
ck(etq.length>0, `con etiqueta de cada museo: ${JSON.stringify(etq.slice(0,4))}`);
ck(historial.some(h=>Math.abs(h[1]-h[2])>1), 'antes de desplegar, los clics sí acercan');

console.log('\n== elegir un museo del abanico ==');
const antesObras=obras();
const aba=sedes().filter(x=>tiene(x,'sede-abanico'));
ck(aba.length>1,`${aba.length} museos desplegados`);
if(aba.length){
  aba[0]._ev.click({stopPropagation:noop}); drenar(300);
  ck(obras()>antesObras,`las obras del museo elegido aparecen: ${antesObras} -> ${obras()}`);
  ck(store['sedeDetalle'].innerHTML.includes('obra-min'),'el panel de abajo también se actualiza');
}

console.log('\n== volver a pulsar el grupo lo pliega ==');
const g2=gruposVista()[0];
if(g2){ g2._ev.click({stopPropagation:noop}); drenar(300);
  ck(sedes().filter(x=>tiene(x,'sede-abanico')).length===0,'el abanico se cierra');
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
