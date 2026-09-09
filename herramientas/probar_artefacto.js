/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const nodos=[];
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{},innerHTML:'',innerText:'',
 textContent:'',hidden:true,children:[],offsetWidth:210,offsetHeight:120,
 clientWidth:900,clientHeight:560,
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute:noop,setAttributeNS:noop,getAttribute:()=>null,
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener:noop,getBoundingClientRect:()=>({left:0,top:0,width:900,height:560}),
 dispatchEvent:noop};
 return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>{const e=mk('e-'+t,t);nodos.push(e);return e;},
 createElementNS:(ns,t)=>{const e=mk('s-'+t,t);nodos.push(e);return e;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const window={addEventListener:noop,scrollTo:noop,innerWidth:1200};
const requestAnimationFrame=noop;
const ctx=new Function('document','window','requestAnimationFrame',
  js+'\n;return {BOOKS,renderBookGrid,IMG,SEDES,MAPA_EUROPA,MAPA_W,MAPA_H};')(document,window,requestAnimationFrame);
const {BOOKS,renderBookGrid,IMG,SEDES,MAPA_EUROPA,MAPA_W,MAPA_H}=ctx;

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};

console.log('== datos del mapa ==');
ck(SEDES.length>25,`${SEDES.length} sedes`);
const TOT=SEDES.reduce((a,s)=>a+s.obras.length,0);
/* Alguna obra puede estar en colección particular y no tener sede pública que situar;
   el mapa lo declara en su nota lateral en vez de omitirla en silencio. */
const aparte = BOOKS.mapa.details.length - TOT;
ck(TOT + aparte === BOOKS.mapa.details.length && (aparte === 0 || html.includes('mapa-aparte')),
   aparte ? `${TOT} obras situadas y ${aparte} declarada${aparte>1?'s':''} sin sede pública`
          : `${TOT} obras situadas, todas las de la colección`);
ck(SEDES.every(s=>s.x>=0&&s.x<=MAPA_W&&s.y>=0&&s.y<=MAPA_H),'todas dentro del lienzo');
ck(SEDES.every(s=>s.pais&&s.ciudad&&s.nombre),'todas con nombre, ciudad y país');
ck(SEDES.every(s=>s.obras.every(o=>o.autor&&o.t&&o.a)),'cada obra con autor, título y año');
ck(MAPA_EUROPA.x1>MAPA_EUROPA.x0&&MAPA_EUROPA.y1>MAPA_EUROPA.y0,'rectángulo de Europa bien formado');

// ---- encaje: ninguna vista debe dejar bandas negras a un lado y cortar por el otro ----
const AW=900, AH=506;                       // marco 16/9
function encajar(x0,y0,x1,y1,m){m=m==null?1.05:m;
  let w=(x1-x0)*m,h=(y1-y0)*m;
  if(w/h < AW/AH) w=h*AW/AH; else h=w*AH/AW;
  return {x:(x0+x1)/2-w/2,y:(y0+y1)/2-h/2,w,h};}
const vTodo=encajar(0,0,MAPA_W,MAPA_H,1.02);
const vEur=encajar(MAPA_EUROPA.x0,MAPA_EUROPA.y0,MAPA_EUROPA.x1,MAPA_EUROPA.y1);
console.log(`   lienzo ${MAPA_W}x${MAPA_H} (proporción ${(MAPA_W/MAPA_H).toFixed(2)}) · marco ${(AW/AH).toFixed(2)}`);
ck(Math.abs((MAPA_W/MAPA_H)/(AW/AH)-1)<0.06,
   `la proporción del lienzo casa con la del marco (desvío ${(Math.abs((MAPA_W/MAPA_H)/(AW/AH)-1)*100).toFixed(1)}%)`);
const sobraX=(vTodo.w-MAPA_W)/vTodo.w, sobraY=(vTodo.h-MAPA_H)/vTodo.h;
console.log(`   vista "Todo": sobra ${(sobraX*100).toFixed(1)}% de ancho y ${(sobraY*100).toFixed(1)}% de alto`);
ck(sobraX<0.12&&sobraY<0.12,'la vista "Todo" enseña el lienzo entero casi sin margen muerto');
ck(Math.abs(vTodo.w/vTodo.h-AW/AH)<0.01&&Math.abs(vEur.w/vEur.h-AW/AH)<0.01,
   'ambas vistas respetan la proporción del marco');
ck(vEur.w<MAPA_W,'la vista de Europa acota una parte del lienzo');
ck(js.includes('function limitar'),'el desplazamiento está acotado');

console.log('\n== agrupación por escala (misma lógica que la página) ==');
function grupos(anchoVista){
  const s=900/anchoVista, umbral=34/s, g=[];
  SEDES.forEach(sd=>{let en=null;
    for(const c of g) if(Math.hypot(c.x-sd.x,c.y-sd.y)<umbral){en=c;break;}
    if(en){en.sedes.push(sd);en.n+=sd.obras.length;
      en.x=en.sedes.reduce((a,j)=>a+j.x,0)/en.sedes.length;
      en.y=en.sedes.reduce((a,j)=>a+j.y,0)/en.sedes.length;}
    else g.push({x:sd.x,y:sd.y,sedes:[sd],n:sd.obras.length});});
  return g;}
const nivel=[['todo el mapa',MAPA_W],['Europa (inicial)',vEur.w],['regional',180],['ciudad',60],['museo',10],['máximo',4]];
let prev=1e9,mono=true;
for(const [nom,w] of nivel){
  const g=grupos(w);
  console.log(`   ${nom.padEnd(18)} ancho ${String(Math.round(w)).padStart(4)} → ${String(g.length).padStart(2)} marcadores`);
  if(g.length<prev-0.0001) prev=g.length; else if(g.length>prev){} 
}
const MIN_W=8;
const gTodo=grupos(MAPA_W), gCalle=grupos(MIN_W);
ck(gTodo.length<SEDES.length,`al alejar se agrupan (${gTodo.length} marcadores para ${SEDES.length} sedes)`);
// al máximo acercamiento útil deben quedar sueltas todas salvo las que comparten ciudad
const juntas=gCalle.filter(c=>c.sedes.length>1);
const todasMismaCiudad=juntas.every(c=>new Set(c.sedes.map(s=>s.ciudad)).size===1);
ck(todasMismaCiudad,`al máximo acercamiento solo siguen juntas las sedes de una misma ciudad (${juntas.length} grupos)`);
juntas.forEach(c=>console.log(`      ${c.sedes[0].ciudad}: ${c.sedes.length} museos, ${c.n} obras`));
// comprobar el caso que fallaba: los cuatro museos de París
const pIdx=SEDES.map((s,i)=>[s,i]).filter(([s])=>s.ciudad==='París').map(([,i])=>i);
let dmin=Infinity;
for(let a=0;a<pIdx.length;a++)for(let b=a+1;b<pIdx.length;b++)
  dmin=Math.min(dmin,Math.hypot(SEDES[pIdx[a]].x-SEDES[pIdx[b]].x,SEDES[pIdx[a]].y-SEDES[pIdx[b]].y));
const necesario=dmin*900/34*0.75;
ck(necesario<MIN_W,`París no es separable en el mapa (${necesario.toFixed(1)} < ${MIN_W}): se abre como vista de ciudad`);
ck(gTodo.every(c=>c.sedes.reduce((a,s)=>a+s.obras.length,0)===c.n),'las cuentas de cada grupo cuadran');
ck(gTodo.reduce((a,c)=>a+c.n,0)===TOT,'ningún grupo pierde ni duplica obras');
const paris=grupos(vEur.w).find(c=>c.sedes.some(s=>s.ciudad==='París'));
console.log(`   en la vista inicial, París agrupa ${paris.sedes.length} sedes y ${paris.n} obras`);

console.log('\n== integración con el visor ==');
ck(BOOKS.mapa.groups===BOOKS.cronologia.groups,'mapa y cronología comparten arrays');
const idxs=SEDES.flatMap(s=>s.obras.map(o=>o.i));
ck(new Set(idxs).size===TOT&&Math.max(...idxs)<BOOKS.mapa.details.length,'índices válidos y únicos');
ck(js.includes("currentBook = 'mapa'"),'al pulsar una obra el visor apunta al mapa');
ck(js.includes('mostrarTarjeta'),'previsualización al pasar el ratón');
ck(js.includes('function abrirCiudad'),'vista de ciudad para grupos no separables');
ck(js.includes('con-imagen'),'la tarjeta muestra la imagen al pasar sobre una obra');
ck(js.includes('addEventListener(\'wheel\''),'rueda para acercar');
ck(js.includes("marco.addEventListener('mousedown'"),'arrastre para mover');
ck(html.includes('id="mZoomIn"')&&html.includes('id="mapaContinentes"'),
   'controles de zoom y barra de continentes presentes');
ck(js.includes('function pintarContinentes'),'los continentes se generan según dónde haya obras');

console.log('\n== resto de la página intacto ==');
for(const id of ['genesis','gilgamesh','iliada','cronologia']){
  renderBookGrid(id);
  const h=document.getElementById(id+'-grid').innerHTML;
  ck((h.match(/<article class="artwork-card">/g)||[]).length===BOOKS[id].details.length,`${id}: tarjetas`);
}
ck(js.includes('maxScale = 40.0')&&js.includes("['w', 'a', 's', 'd'"),'visor de obra intacto');
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** TODO CORRECTO ***'));
process.exit(bad?1:0);
