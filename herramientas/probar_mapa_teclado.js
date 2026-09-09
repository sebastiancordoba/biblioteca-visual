/* Las pruebas se ejecutan desde la raíz del repositorio, sea cual sea el directorio
   desde el que se invoquen: antes solo funcionaban con el cwd correcto. */
process.chdir(require('path').join(__dirname, '..'));
/* Teclado del mapa: W A S D, + / -, 0, y que no pise al visor de obras. */
const fs=require('fs');
const html=fs.readFileSync(require('path').join(__dirname,'..','build','los-tres-libros.html'),'utf8');
const js=html.split('<script>')[1].split('</script>')[0];
const noop=()=>{};const store={};const oyDoc={};const oyWin={};
let OCULTO=true,RO=null;const cola=[];
const rAF=f=>{cola.push(f);return cola.length;};const cAF=i=>{cola[i-1]=null;};
const drenar=m=>{let n=0;while(cola.length&&n<m){const f=cola.shift();if(f)f();n++;}return n;};
function mk(id,tag){const el={id,tag:tag||'div',dataset:{},style:{setProperty(){},removeProperty(){},getPropertyValue:()=>''},_html:'',_tc:'',
 hidden:true,children:[],offsetWidth:210,offsetHeight:120,_attrs:{},_ev:{},
 get innerHTML(){return this._html;},set innerHTML(v){this._html=v;this.children=[];},
 get textContent(){return this._tc;},set textContent(v){this._tc=v;this.children=[];},
 get clientWidth(){return (id==='mapaMarco'&&OCULTO)?0:900;},
 get clientHeight(){return (id==='mapaMarco'&&OCULTO)?0:506;},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},
   contains(c){return this._s.has(c)},toggle(c,v){v?this._s.add(c):this._s.delete(c)}},
 setAttribute(k,v){this._attrs[k]=v;},setAttributeNS:noop,getAttribute(k){return this._attrs[k];},
 appendChild(c){this.children.push(c);return c;},
 querySelectorAll:()=>[],querySelector:()=>mk('x'),closest:()=>mk('x'),
 addEventListener(t,f){this._ev[t]=f;},
 getBoundingClientRect:()=>({left:0,top:0,width:900,height:506}),dispatchEvent:noop};return el;}
const document={body:mk('body'),documentElement:mk('html'),
 getElementById:id=>{if(!store[id])store[id]=mk(id);return store[id];},
 createElement:t=>mk('e-'+t,t),createElementNS:(ns,t)=>mk('s-'+t,t),
 querySelectorAll:()=>[],querySelector:()=>mk('x'),
 addEventListener(t,f){(oyDoc[t]=oyDoc[t]||[]).push(f);}};
const win={addEventListener(t,f){(oyWin[t]=oyWin[t]||[]).push(f);},scrollTo:noop};
global.ResizeObserver=class{constructor(f){this.f=f;}observe(){RO=this.f;}};
new Function('document','window','requestAnimationFrame','ResizeObserver','cancelAnimationFrame',
  js)(document,win,rAF,global.ResizeObserver,cAF);
OCULTO=false; RO(); drenar(400);

let bad=0;const ck=(o,m)=>{console.log((o?'  ok    ':'  FALLA ')+m);if(!o)bad++;};
const vb=()=>(store['mapaSvg'].getAttribute('viewBox')||'').split(/\s+/).map(Number);
const tecla=(t,k)=>{const ev={key:k,preventDefault:noop,metaKey:false,ctrlKey:false,altKey:false};
  (oyDoc[t]||[]).forEach(f=>f(ev));};
const pulsar=(k,frames)=>{tecla('keydown',k); drenar(frames||30); tecla('keyup',k); drenar(5);};

console.log('== desplazamiento con W A S D ==');
for(const [k,eje,signo,nom] of [['d',0,+1,'derecha'],['a',0,-1,'izquierda'],
                                ['s',1,+1,'abajo'],['w',1,-1,'arriba']]){
  const antes=vb(); pulsar(k,25); const desp=vb();
  const d=desp[eje]-antes[eje];
  ck(Math.sign(d)===signo && Math.abs(d)>1,
     `${k.toUpperCase()} mueve hacia ${nom} (${d>0?'+':''}${d.toFixed(0)} unidades)`);
}

console.log('\n== acercar y alejar con + y − ==');
{
  const a=vb()[2]; pulsar('+',30); const b=vb()[2];
  ck(b<a*0.95, `+ acerca (ancho ${a.toFixed(0)} -> ${b.toFixed(0)})`);
  pulsar('-',30); const c=vb()[2];
  ck(c>b*1.05, `− aleja (ancho ${b.toFixed(0)} -> ${c.toFixed(0)})`);
}

console.log('\n== 0 vuelve a la vista de Europa ==');
{
  pulsar('d',60); const movido=vb();
  tecla('keydown','0'); drenar(400); const vuelto=vb();
  ck(Math.abs(vuelto[0]-movido[0])>1 || Math.abs(vuelto[2]-movido[2])>1, 'la tecla 0 reencuadra');
  console.log(`   tras 0: ${vuelto.map(n=>n.toFixed(0)).join(' ')}`);
}

console.log('\n== movimiento continuo mientras se mantiene ==');
{
  const a=vb()[0]; tecla('keydown','d'); drenar(10); const b=vb()[0]; drenar(30); const c=vb()[0];
  tecla('keyup','d'); drenar(5);
  ck(c-b > (b-a)*1.5, `mantener la tecla sigue moviendo (10 fotogramas: ${(b-a).toFixed(0)}, 40: ${(c-a).toFixed(0)})`);
}

console.log('\n== no pisa al visor de obras ==');
{
  store['zoomModal'].classList.add('active');      // visor abierto
  const antes=vb(); pulsar('d',30); const desp=vb();
  ck(Math.abs(desp[0]-antes[0])<0.01, 'con el visor de obra abierto, W A S D no mueven el mapa');
  store['zoomModal'].classList.remove('active');
  const a2=vb(); pulsar('d',30);
  ck(Math.abs(vb()[0]-a2[0])>1, 'al cerrarlo, vuelven a funcionar');
}

console.log('\n== no actúa con la pestaña oculta ==');
{
  OCULTO=true; const antes=vb(); pulsar('d',30);
  ck(Math.abs(vb()[0]-antes[0])<0.01, 'con el mapa fuera de vista el teclado no hace nada');
  OCULTO=false;
}
console.log('\n'+(bad?`*** ${bad} FALLAS ***`:'*** SIN ERRORES ***'));
process.exit(bad?1:0);
