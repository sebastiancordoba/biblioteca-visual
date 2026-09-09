/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Ordenar por: que reordene de verdad y que el visor siga apuntando a la obra correcta. */
const fs=require('fs');
const RUTA='/Users/sebastiancordoba/Library/Mobile Documents/com~apple~CloudDocs/Documents/Pinturas/index.html';
const html=fs.readFileSync(RUTA,'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const barras=[];
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},innerHTML:'',_ev:{},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute:noop,getAttribute:()=>null,appendChild:noop,
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;},getBoundingClientRect:()=>({})};return el;}
function botones(libro){
  return ['coleccion','cronologia','artista','titulo','sede'].map(o=>{
    const b=mk('btn-'+libro+'-'+o); b.dataset.orden=o; return b;});
}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e',t),createElementNS:(ns,t)=>mk('s',t),
 querySelectorAll(sel){
   if(sel==='.orden-bar') return barras;
   return [];},
 querySelector:()=>mk('x'),addEventListener:noop};
for(const L of ['genesis','gilgamesh','iliada']){
  const bar=mk('bar-'+L); bar.dataset.libro=L;
  const bs=botones(L);
  bar.querySelectorAll=()=>bs;
  bar._botones=bs; barras.push(bar);
}
const window={addEventListener:noop,scrollTo:noop};
const {BOOKS,renderBookGrid}=new Function('document','window','requestAnimationFrame',
  js+'\n;return {BOOKS,renderBookGrid};')(document,window,noop);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const titulos=id=>[...store[id+'-grid'].innerHTML.matchAll(/<div class="artwork-title">([^<]+)/g)].map(m=>m[1]);
const indices=id=>[...store[id+'-grid'].innerHTML.matchAll(/openZoomForArtwork\((\d+),/g)].map(m=>+m[1]);

console.log('== la barra existe en los tres libros ==');
ck(barras.length===3, `${barras.length} barras de ordenación`);
ck(html.includes('data-orden="cronologia"')&&html.includes('data-orden="sede"'),'con los cinco criterios');

for(const L of ['genesis','iliada']){
  console.log(`\n== ${L} ==`);
  renderBookGrid(L,true);
  const base=titulos(L), baseIdx=indices(L);
  ck(base.length===BOOKS[L].details.length, `orden de colección: ${base.length} obras`);
  ck(baseIdx.every((v,i)=>v===i), 'los índices van 0,1,2… en el orden de colección');

  const bar=barras.find(b=>b.dataset.libro===L);
  for(const crit of ['cronologia','artista','titulo','sede']){
    bar._botones.find(b=>b.dataset.orden===crit)._ev.click();
    const t=titulos(L), ix=indices(L);
    ck(t.length===base.length, `${crit}: siguen las ${t.length} obras`);
    ck(new Set(ix).size===ix.length, `${crit}: sin obras repetidas ni perdidas`);
    const cambio=t.some((x,i)=>x!==base[i]);
    ck(cambio || crit==='coleccion', `${crit}: el orden cambia de verdad`);
    // los índices deben seguir apuntando a la ficha correcta
    const bien=ix.every((idx,pos)=>BOOKS[L].details[idx].title===t[pos]);
    ck(bien, `${crit}: cada tarjeta abre en el visor la obra que muestra`);
    if(crit==='cronologia'){
      const anios=ix.map(i=>BOOKS[L].details[i].anio).filter(a=>a!=null);
      const asc=anios.every((a,i)=>i===0||a>=anios[i-1]);
      ck(asc, `cronología: años en orden ascendente (${anios[0]} → ${anios[anios.length-1]})`);
    }
  }
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
