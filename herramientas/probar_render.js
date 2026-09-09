/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Ejecuta renderBookGrid de verdad y comprueba el HTML resultante de cada libro. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','index.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const { noop, ejecutar } = require('./dom_falso.js');
const { BOOKS, renderBookGrid, document } = ejecutar(html, '{BOOKS, renderBookGrid}');

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
  /* Inicio y Biblioteca no tienen obras propias: son índices, no colecciones, y su
     cuadrícula no existe. Comprobado que salen 0 tarjetas, no hay nada más que mirar. */
  if(n===0) continue;
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
