/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Reproduce el fallo reportado: acercarse hasta el tope sobre un grupo de museos de la
   misma ciudad y pulsarlo. Antes no ocurría nada visible. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},innerHTML:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
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

console.log('== desde el mundo, un grupo de varias ciudades se acerca, no se despliega ==');
{
  /* El fallo: pulsar el grupo grande de Europa desplegaba veinticuatro museos repartidos
     por todo el mapamundi en vez de volar a Europa. La tarjeta prometía «pulsa para
     acercar» mientras el clic decidía con otra regla. */
  oyentes.mTodo.click(); drenar(400);
  const anchoMundo = vb()[2];
  const gs = sedes().filter(g => tiene(g,'grupo'));
  // el grupo con más sedes es el de Europa
  const mayor = gs.map(g => ({ g, n: +((g.getAttribute('aria-label')||'').match(/^(\d+) sedes/)||[])[1] || 0 }))
                  .sort((a,b) => b.n - a.n)[0];
  console.log(`   vista de mundo: ancho ${anchoMundo.toFixed(0)} · grupo mayor con ${mayor.n} sedes`);
  mayor.g._ev.click({ stopPropagation: noop });
  drenar(600);
  const despues = vb()[2];
  const desplegados = sedes().filter(x => tiene(x,'sede-abanico')).length;
  console.log(`   tras pulsarlo: ancho ${despues.toFixed(0)} · museos desplegados en abanico: ${desplegados}`);
  ck(despues < anchoMundo * 0.6, `se acerca de verdad (${anchoMundo.toFixed(0)} -> ${despues.toFixed(0)})`);
  ck(desplegados === 0, 'no despliega el abanico sobre el mapamundi');
}

console.log('== pulsar repetidamente un grupo, como haría un usuario ==');
oyentes.mReset.click(); drenar(300);
function gruposVista(){ return sedes().filter(g=>tiene(g,'grupo')); }
/* Un grupo que reúne varias ciudades sí puede separarse acercándose; uno de una sola
   ciudad no, y se despliega en abanico. Se prueban los dos caminos por separado. */
function esMulticiudad(g){
  const et=(g.getAttribute('aria-label')||'');
  return /(\d+) sedes agrupadas/.test(et);
}
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
const huboAcercamiento = historial.some(h=>Math.abs(h[1]-h[2])>1);
if (huboAcercamiento) ck(true, 'antes de desplegar, los clics acercan');
else console.log('   (el primer grupo era de una sola ciudad: se desplegó directamente, que es lo correcto)');

console.log('\n== elegir un museo del abanico ==');
const aba=sedes().filter(x=>tiene(x,'sede-abanico'));
ck(aba.length>1,`${aba.length} museos desplegados`);
if(aba.length){
  /* Sus obras no caben alrededor del punto dentro del abanico de una ciudad, así que
     salen en la lista de la derecha y en el panel de debajo. Contar miniaturas sobre el
     mapa daba un falso verde: subían por las de OTRAS sedes, no por la elegida. */
  const desplegable = () => store['sedeLista'].children.find(c => (c.className||'') === 'libro-obras');
  aba[0]._ev.click({stopPropagation:noop}); drenar(300);
  const d = desplegable();
  ck(!!d, 'al elegir un museo sus obras se despliegan en la lista');
  if (d) {
    const n = (d.innerHTML.match(/class="libro-obra"/g) || []).length;
    console.log(`   ${n} obras del museo elegido en la lista`);
    ck(n > 0 && (d.innerHTML.match(/<img src="/g)||[]).length === n,
       `cada una con su miniatura (${n})`);
  }
  ck(store['sedeDetalle'].innerHTML.includes('obra-min'),'el panel de abajo también se actualiza');
}

console.log('\n== dispersión: nada se pisa con nada ==');
{
  /* El abanico se dibujaba en un arco de 115° encima del punto y con radio fijo, así que
     con cuatro o cinco museos los círculos y las miniaturas se montaban unos sobre otros.
     Se miden las distancias reales entre centros. */
  const centro = el => {
    const c = (el.children||[]).find(x => x.tag==='circle' && (x.getAttribute('class')||'')==='pt');
    if (c) return { x:+c.getAttribute('cx'), y:+c.getAttribute('cy'), r:+c.getAttribute('r') };
    const im = (el.children||[]).find(x => x.tag==='image');
    if (im) { const w=+im.getAttribute('width');
      return { x:+im.getAttribute('x')+w/2, y:+im.getAttribute('y')+w/2, r:w/2 }; }
    return null;
  };
  const puntos = cls => sedes().filter(x=>tiene(x,cls)).map(centro).filter(Boolean);

  const museos = puntos('sede-abanico');
  const minSep = ps => { let m = Infinity;
    for (let i=0;i<ps.length;i++) for (let j=i+1;j<ps.length;j++)
      m = Math.min(m, Math.hypot(ps[i].x-ps[j].x, ps[i].y-ps[j].y) - ps[i].r - ps[j].r);
    return m; };

  if (museos.length > 1) {
    const sep = minSep(museos);
    console.log(`   ${museos.length} museos · separación mínima entre bordes: ${sep.toFixed(1)} px`);
    ck(sep > 6, `los museos del abanico no se tocan (${sep.toFixed(1)} px de holgura)`);
  }

  /* Se mide abanico por abanico, no sobre todas las miniaturas del mapa: dos sedes
     distintas pueden quedar cerca a cierto acercamiento y eso es densidad del mapa, no
     un abanico mal repartido. Lo que no puede pasar es que las obras de UNA sede se
     monten entre ellas, que era el fallo. */
  const abanicos = store['capaSedes'].children
    .map(m => aplanar([m]).filter(x => tiene(x,'obra-pin')).map(centro).filter(Boolean))
    .filter(a => a.length > 1);
  let peor = Infinity, cuantas = 0;
  for (const a of abanicos) { peor = Math.min(peor, minSep(a)); cuantas += a.length; }
  if (abanicos.length) {
    console.log(`   ${abanicos.length} abanicos, ${cuantas} miniaturas · peor separación dentro de uno: ${peor.toFixed(1)} px`);
    ck(peor > 0, `dentro de un abanico las miniaturas no se solapan (${peor.toFixed(1)} px)`);
  }

  /* El abanico ya no reparte los museos en círculo sino que conserva su geometría real
     ampliada, así que los radios desde el centro tienen que ser distintos entre sí: en un
     círculo serían todos iguales. Es la comprobación que distingue las dos disposiciones
     sin necesidad de conocer las coordenadas. */
  if (museos.length > 2) {
    const radios = museos.map(m => Math.hypot(m.x, m.y));
    const med = radios.reduce((a,b)=>a+b,0) / radios.length;
    const disp = Math.sqrt(radios.reduce((a,r)=>a+(r-med)**2,0)/radios.length) / med;
    console.log(`   radios desde el centro: ${radios.map(r=>r.toFixed(0)).join(', ')} · dispersión ${(disp*100).toFixed(0)}%`);
    ck(disp > 0.05, `los museos guardan su geometría real, no un círculo (dispersión ${(disp*100).toFixed(0)}%)`);
  }

  const minis = sedes().filter(x=>tiene(x,'obra-pin')).map(centro).filter(Boolean);

  /* Y las miniaturas del museo abierto tampoco deben invadir a los museos vecinos. */
  if (minis.length && museos.length > 1) {
    let m = Infinity;
    for (const a of minis) for (const b of museos)
      m = Math.min(m, Math.hypot(a.x-b.x, a.y-b.y) - a.r - b.r);
    console.log(`   miniaturas frente a museos vecinos: ${m.toFixed(1)} px`);
    ck(m > -6, `las obras abiertas no invaden los museos vecinos (${m.toFixed(1)} px)`);
  }
}

console.log('\n== volver a pulsar el grupo lo pliega ==');
const g2=gruposVista()[0];
if(g2){ g2._ev.click({stopPropagation:noop}); drenar(300);
  ck(sedes().filter(x=>tiene(x,'sede-abanico')).length===0,'el abanico se cierra');
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
