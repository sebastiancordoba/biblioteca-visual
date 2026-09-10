/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Crecimiento de los marcadores al acercarse, y botones por continente. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyentes={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},_html:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},disabled:false,title:'',
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
 querySelectorAll(sel){
   /* Buscar de verdad por clase: sin esto la vía de reescalado no encontraba nada y las
      transformaciones solo se actualizaban al redibujar, falseando la medición. */
   const f=sel.replace('.','');
   const todos=(function w(n){return n.flatMap(c=>[c,...w(c.children||[])]);})(this.children);
   return todos.filter(x=>((x.getAttribute('class')||'')+' '+[...x.classList._s].join(' ')).split(/\s+/).includes(f));},
 querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;(oyentes[this.id]=oyentes[this.id]||{})[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),addEventListener:noop};
const win={addEventListener(t,f){(oyentes.window=oyentes.window||{})[t]=f;},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
const ctx=new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js+'\n;return {SEDES};')(document,win,rAF,global.ResizeObserver,cAF);
const {SEDES}=ctx;
OCULTO=false; RO(); drenar(400);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const aplanar=n=>n.flatMap(c=>[c,...aplanar(c.children||[])]);
/* La escala del marcador va en su transform: translate(x,y) scale(k) */
function escalasMarca(){
  return aplanar(store['capaSedes'].children)
    .map(g=>{const t=g.getAttribute('transform')||''; const m=t.match(/scale\(([\d.]+)\)/); return m?+m[1]:null;})
    .filter(v=>v!=null);
}
function radioEnPantalla(){
  const ks=escalasMarca(); if(!ks.length) return null;
  const s=900/vb()[2];              // px de pantalla por unidad de lienzo
  console.log(`      [k=${ks[0].toFixed(4)} · escalas distintas=${new Set(ks.map(x=>x.toFixed(4))).size} · s=${s.toFixed(2)}]`);
  return ks[0]*s;                    // 1 unidad del marcador en px de pantalla
}

console.log('== los marcadores crecen al acercarse ==');
oyentes.mReset.click(); drenar(500);
const rEuropa=radioEnPantalla();
console.log(`   vista de Europa: 1 unidad de marcador = ${rEuropa.toFixed(2)} px`);
for(let i=0;i<10;i++){oyentes.mZoomIn.click(); drenar(300);}
const rCerca=radioEnPantalla();
console.log(`   muy acercado:    1 unidad de marcador = ${rCerca.toFixed(2)} px (ancho de vista ${vb()[2].toFixed(0)})`);
ck(rCerca>rEuropa*1.5, `los círculos crecen al acercarse (${(rCerca/rEuropa).toFixed(2)}x, antes se quedaban en 1,00x)`);
ck(rCerca<rEuropa*3, `pero sin desbordarse (tope 2,4x)`);
oyentes.mTodo.click(); drenar(500);
const rMundo=radioEnPantalla();
console.log(`   mundo entero:    1 unidad de marcador = ${rMundo.toFixed(2)} px`);
ck(Math.abs(rMundo-rEuropa)<0.35, 'a escala mundial no se agrandan y siguen sin tapar el mapa');

console.log('\n== botones por continente ==');
const bar=store['mapaContinentes'];
const btns=bar.children;
console.log('   botones:', btns.map(b=>`${b.textContent}${b.disabled?' (apagado)':''}`).join(' · '));
ck(btns.length===7, `${btns.length} botones: Mundo más seis continentes`);
const conts=[...new Set(SEDES.map(s=>s.cont))];
console.log('   continentes con obras:', conts.join(', '));
for(const b of btns){
  if(b.textContent==='Mundo') continue;
  const nombre={'N. América':'América del Norte','S. América':'América del Sur'}[b.textContent]||b.textContent;
  const hay=SEDES.some(s=>s.cont===nombre);
  ck(b.disabled===!hay, `${b.textContent}: ${hay?'activo porque hay obras':'apagado porque no hay ninguna'}`);
}
console.log('\n== encuadrar un continente ==');
const bAsia=btns.find(b=>b.textContent==='Asia');
if(bAsia && !bAsia.disabled){
  bAsia._ev.click(); drenar(600);
  const v=vb();
  const asia=SEDES.filter(s=>s.cont==='Asia');
  const dentro=asia.every(s=>s.x>=v[0]-1&&s.x<=v[0]+v[2]+1&&s.y>=v[1]-1&&s.y<=v[1]+v[3]+1);
  console.log(`   Asia: ${asia.length} sedes (${asia.map(s=>s.ciudad).join(', ')})`);
  ck(dentro, 'todas las sedes de Asia caben en la vista');
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
