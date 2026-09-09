/* Simula el ciclo real: panel oculto -> se muestra (ResizeObserver) -> arrastre -> rueda. */
const fs=require('fs');
const html=fs.readFileSync('los-tres-libros.html','utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const creados=[];
let OCULTO=true, RO=null;
const oyentes={};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{},innerHTML:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},
 get textContent(){return this._tc;}, set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){(oyentes[id]=oyentes[id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>{const e=mk('e-'+t,t);creados.push(e);return e;},
 createElementNS:(ns,t)=>{const e=mk('s-'+t,t);creados.push(e);return e;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
global.cancelAnimationFrame=noop;
new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js)(document,win,noop,global.ResizeObserver,noop);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const vb=()=>({v:store['mapaSvg'].getAttribute('viewBox'),
               n:(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number)});
const radios=()=>creados.filter(e=>e.tag==='circle').map(c=>Number(c.getAttribute('r')));
const finitos=a=>a.every(n=>isFinite(n)&&!Number.isNaN(n));

console.log('== 1. panel oculto (marco = 0 px) ==');
ck(finitos(vb().n),'el viewBox no contiene NaN ni Infinity');
ck(finitos(radios()),`los ${radios().length} radios son finitos`);

console.log('\n== 2. la pestaña se hace visible ==');
OCULTO=false; creados.length=0; RO();
const marcadores=store['capaSedes'].children.length;
ck(marcadores>15,`${marcadores} marcadores tras hacerse visible (antes 1)`);
ck(finitos(radios())&&radios().length>0,`los ${radios().length} radios siguen siendo finitos`);
ck(finitos(vb().n),'viewBox válido');
const antes=vb().n.slice();

console.log('\n== 3. arrastre ==');
oyentes.mapaMarco.mousedown({button:0,clientX:400,clientY:250,preventDefault:noop});
creados.length=0;
for(let i=1;i<=25;i++) oyentes.window.mousemove({clientX:400-i*6,clientY:250-i*3});
const desp=vb().n;
ck(finitos(desp),'viewBox válido durante el arrastre');
ck(desp[0]>antes[0],'el mapa se desplaza en el sentido correcto');
ck(Math.abs(desp[2]-antes[2])<0.01,'la escala no cambia al desplazar');
ck(creados.filter(e=>e.tag==='circle').length===0,
   'no se reconstruyen marcadores en cada movimiento (arrastre fluido)');
oyentes.window.mouseup();

console.log('\n== 4. rueda ==');
creados.length=0;
oyentes.mapaMarco.wheel({deltaX:0,deltaY:-120,clientX:450,clientY:250,ctrlKey:false,preventDefault:noop});
ck(finitos(vb().n),'zoom con rueda: viewBox válido');
const trasZoom=vb().n.slice();
oyentes.mapaMarco.wheel({deltaX:60,deltaY:2,clientX:450,clientY:250,ctrlKey:false,preventDefault:noop});
const trasPan=vb().n;
ck(Math.abs(trasPan[2]-trasZoom[2])<0.01,'dos dedos en horizontal desplazan, no amplían');
ck(trasPan[0]>trasZoom[0],'y desplazan en el sentido correcto');

console.log('\n== 5. vuelta al mundo ==');
const W=1980;
const copias=()=>store['capaMundo'].children.length;
const sedesDibujadas=()=>store['capaSedes'].children.length;
// dar una vuelta completa arrastrando hacia el este
oyentes.mapaMarco.mousedown({button:0,clientX:400,clientY:250,preventDefault:noop});
const x0=vb().n[0]; let maxCopias=0, minSedes=1e9;
for(let i=1;i<=600;i++){
  oyentes.window.mousemove({clientX:400-i*20,clientY:250});
  maxCopias=Math.max(maxCopias,copias()); minSedes=Math.min(minSedes,sedesDibujadas());
}
oyentes.window.mouseup();
const x1=vb().n[0];
ck(finitos(vb().n),'viewBox válido tras dar la vuelta');
ck(Math.abs(x1)<W*1.6,`la posición se normaliza y no crece sin fin (x=${x1.toFixed(0)}, lienzo ${W})`);
ck(copias()>=1,`se dibujan ${copias()} copias del mundo a la vez`);
ck(sedesDibujadas()>0,'siempre hay sedes visibles durante la vuelta');
// el desplazamiento debe ser continuo: sin saltos grandes entre fotogramas
oyentes.mapaMarco.mousedown({button:0,clientX:400,clientY:250,preventDefault:noop});
let prev=vb().n[0], salto=0;
for(let i=1;i<=300;i++){
  oyentes.window.mousemove({clientX:400-i*20,clientY:250});
  const ahora=vb().n[0];
  /* Desplazar el mundo entero es la identidad visual (el mapa se repite), así que el
     salto perceptible es la diferencia módulo el ancho del lienzo. */
  let d=Math.abs(ahora-prev)%W; if(d>W/2) d=W-d;
  salto=Math.max(salto,d); prev=ahora;
}
oyentes.window.mouseup();
ck(salto<40,`sin saltos visibles al cruzar la costura (máx ${salto.toFixed(1)} px de lienzo)`);

console.log('\n== 6. límite vertical ==');
oyentes.mapaMarco.mousedown({button:0,clientX:400,clientY:250,preventDefault:noop});
for(let i=1;i<=400;i++) oyentes.window.mousemove({clientX:400,clientY:250+i*40});
const y=vb().n[1];
ck(finitos([y])&&y>-1141*0.3&&y<1141*1.3,`en vertical sí hay tope (y=${y.toFixed(0)})`);
oyentes.window.mouseup();
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
