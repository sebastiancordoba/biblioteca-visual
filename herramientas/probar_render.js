/* Ejecuta renderBookGrid de verdad y comprueba el HTML resultante de cada libro. */
const fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};
const grids={};                       // id -> {innerHTML, dataset}
function mkEl(id){ return {id, dataset:{}, innerHTML:'', style:{},
  classList:{add:noop,remove:noop,contains:()=>false,toggle:noop},
  querySelectorAll:()=>({forEach:noop}), querySelector:()=>mkEl('x'),
  closest:()=>mkEl('x'), addEventListener:noop, getBoundingClientRect:()=>({})}; }
const store={};
const document={ getElementById:(id)=>{ if(!store[id]) store[id]=mkEl(id); return store[id]; },
  querySelectorAll:()=>({forEach:noop}), querySelector:()=>mkEl('x'), addEventListener:noop };
const window={addEventListener:noop, scrollTo:noop};
const {BOOKS, renderBookGrid}=new Function('document','window','requestAnimationFrame',
  js+'\n;return {BOOKS, renderBookGrid};')(document,window,noop);

let fails=0;
for(const id of Object.keys(BOOKS)){
  renderBookGrid(id);
  const grid=document.getElementById(id+'-grid');
  const h=grid.innerHTML;
  const cards=(h.match(/<article class="artwork-card">/g)||[]).length;
  const n=BOOKS[id].details.length;
  const ok = cards===n;
  console.log(`${ok?'  ok    ':'  FALLA '}${id}: ${cards} tarjetas generadas para ${n} obras`);
  if(!ok) fails++;
  // toda tarjeta debe traer imagen, título, drawer y enlace de zoom
  for(const campo of ['<img src="./','artwork-title','id="drawer-'+id+'-0"','openZoomForArtwork(0']){
    const tiene=h.includes(campo);
    if(!tiene){ console.log(`  FALLA ${id}: falta ${campo}`); fails++; }
  }
  // ningún literal de plantilla sin resolver
  if(h.includes('${')){ console.log(`  FALLA ${id}: quedan plantillas sin interpolar`); fails++; }
  // encabezados propios del libro
  const hd=BOOKS[id].headings||[];
  if(hd.length && !h.includes(hd[2])){ console.log(`  FALLA ${id}: falta el encabezado "${hd[2]}"`); fails++; }
}
console.log('\n== muestra de la primera tarjeta de Génesis ==');
console.log(document.getElementById('genesis-grid').innerHTML.slice(0,700));
console.log('\n'+(fails===0?'*** RENDERIZADO CORRECTO ***':`*** ${fails} FALLAS ***`));
process.exit(fails?1:0);
