# -*- coding: utf-8 -*-
JS = r"""
    /* ══════════════════ MAPA NAVEGABLE ══════════════════
       Un solo lienzo que resuelve detalle por niveles: a poca escala las sedes cercanas
       se agrupan en un disco con su cuenta; al acercarse el grupo se abre en sedes, y
       una sede sola despliega sus obras en abanico alrededor del punto.
       La agrupación se recalcula en cada cambio de escala: el umbral está en píxeles de
       pantalla, no en grados, que es lo que hace que el mapa "se aclare" al ampliar. */
    (function(){
      const svg = document.getElementById('mapaSvg');
      const marco = document.getElementById('mapaMarco');
      if (!svg || !marco) return;

      const capaMundo = document.getElementById('capaMundo');
      const frPrin = document.getElementById('frPrin');
      const frSec  = document.getElementById('frSec');
      const capaTierra = document.getElementById('capaTierra');
      const capaRet = document.getElementById('capaRet');
      const capaSedes = document.getElementById('capaSedes');
      const capaObras = document.getElementById('capaObras');
      const capaEnlaces = document.getElementById('capaEnlaces');
      const lista = document.getElementById('sedeLista');
      const detalle = document.getElementById('sedeDetalle');
      const tarjeta = document.getElementById('mapaTarjeta');
      const pista = document.getElementById('mapaPista');
      const NS = 'http://www.w3.org/2000/svg';

      /* Varias sedes comparten ciudad —cuatro en París, tres en Londres— y sus puntos
         distan décimas de unidad. El tope de acercamiento debe bajar lo bastante para
         que el umbral de agrupación (34 px) quepa entre ellas; si no, pulsar un grupo
         no lo separaría nunca. */
      /* Por debajo de ~8 unidades (unos 45 km de ancho) el mapa ya no aporta: los museos
         de una misma ciudad distan décimas de unidad y separarlos exigiría acercarse a
         escala de calle sobre una costa dibujada a 1:50M, es decir, al vacío. Ahí el
         grupo deja de ser geográfico y se abre como lista de museos de la ciudad. */
      /* Tope de acercamiento. Estaba en 8, y con ese tope los museos de una misma ciudad
         no llegaban nunca a separarse: el Louvre y el Museo de Orsay están a 0,061 px de
         lienzo, que exige un ancho de vista de 1,6 para verse aparte. Bajándolo, al
         acercarse del todo cada museo aparece en su sitio real y el abanico deja de hacer
         falta; sigue estando para los acercamientos intermedios. */
      const MIN_W = 1.2;
      /* Los marcadores se dibujan a tamaño constante en pantalla (escala 1/s). Muy
         acercado eso los dejaba diminutos en un espacio vacío enorme, así que a partir de
         la vista de Europa se les deja crecer de forma logarítmica hasta algo más del
         doble: aprovecha el sitio sin que a escala mundial tapen el mapa. */
      const S_REF = 1.7;
      const factorMarca = s => clamp(1 + Math.log2(Math.max(s, S_REF) / S_REF) * 0.23, 1, 2.4);
      const SEP_PX = 34;
      const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
      /* El panel del mapa nace dentro de una pestaña oculta, así que el marco mide 0 px
         hasta que se muestra. Sin esta guarda la escala sería 0, el umbral de agrupación
         infinito y los radios Infinity: SVG inválido. */
      const anchoMarco = () => marco.clientWidth || 900;
      const altoMarco  = () => marco.clientHeight || 506;
      const visible = () => marco.clientWidth > 0;
      const escala = () => anchoMarco() / vista.w;   // px de pantalla por unidad de lienzo

      /* Ajusta un rectángulo del lienzo al marco respetando SU proporción: se amplía la
         dimensión que falte, nunca se recorta. Así ninguna vista deja bandas negras a un
         lado y contenido cortado al otro. */
      function encajar(x0, y0, x1, y1, margen){
        const m = margen == null ? 1.05 : margen;
        const aw = anchoMarco(), ah = altoMarco();
        let w = (x1 - x0) * m, h = (y1 - y0) * m;
        if (w / h < aw / ah) w = h * aw / ah; else h = w * ah / aw;
        return { x: (x0 + x1) / 2 - w / 2, y: (y0 + y1) / 2 - h / 2, w: w, h: h };
      }
      /* La vista inicial y el botón Europa son lo mismo: el encuadre de las sedes
         europeas, no un rectángulo fijo. Así al arrancar caben todas y volver a Europa
         devuelve exactamente a donde se empezó. El rectángulo queda como reserva por si
         algún día no hubiera ninguna sede en Europa. */
      const vistaEuropa = () => {
        const idxs = SEDES.map((_, i) => i).filter(i => SEDES[i].cont === 'Europa');
        return idxs.length ? encajarSedes(idxs)
                           : encajar(MAPA_EUROPA.x0, MAPA_EUROPA.y0, MAPA_EUROPA.x1, MAPA_EUROPA.y1);
      };
      const vistaTodo   = () => encajar(0, 0, MAPA_W, MAPA_H, 1.0);

      /* Encuadra un conjunto de sedes: en vez de volar a un punto y fijar un nivel de
         acercamiento, se ajusta la vista a la caja que las contiene. Así lo que pulsas
         queda centrado de verdad, y un libro repartido entre Bagdad y Nueva York obliga
         al mapa a alejarse hasta que caben todas sus sedes. */
      function encajarSedes(idxs, off){
        off = off || 0;
        if (!idxs || !idxs.length) return vistaEuropa();
        const xs = idxs.map(i => SEDES[i].x + off), ys = idxs.map(i => SEDES[i].y);
        /* Caja mínima. Una sede suelta no tiene geometría interna que enseñar, así que
           se encuadra en un cuadro regional: no tiene sentido caer encima de un punto.
           Varias sedes sí la tienen, y se encuadran más apretado, a escala metropolitana.
           No se baja de ahí a propósito: los museos de una ciudad se separarían del todo
           hacia un ancho de 2, y a esa escala el mapa base no tiene ya nada que dibujar
           —ni costa ni frontera—, así que se llegaría a un rectángulo vacío con dos
           puntos. Quien quiera bajar más lo hace acercándose a mano. */
        const minCaja = idxs.length > 1 ? 8 : 42;
        const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
        const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
        const w = Math.max(Math.max(...xs) - Math.min(...xs), minCaja);
        const h = Math.max(Math.max(...ys) - Math.min(...ys), minCaja * 0.55);
        return encajar(cx - w/2, cy - h/2, cx + w/2, cy + h/2, 1.3);
      }

      /* vista = ventana del lienzo que se ve; se anima hacia vistaObj */
      /* Se abre en el mundo entero: con obras en tres continentes, empezar en Europa
         escondía media colección. El botón Europa sigue estando para acercarse. */
      let vista = vistaTodo();
      let vistaObj = Object.assign({}, vista);
      let anim = null, arrastrando = false, movido = false, sedeSel = -1, grupoAbierto = -1;
      /* Clave del grupo de ciudad desplegado. Cuando varias sedes comparten ciudad no se
         pueden separar sobre el mapa, así que se abren en abanico alrededor del punto:
         el mismo gesto que usan las obras, un nivel más arriba. */
      let ciudadAbierta = null;
      /* Filtro por libro: cuando está activo, el mapa muestra solo las sedes que guardan
         obras de ese libro, y las cuentas reflejan únicamente esas obras. */
      let libroFiltro = null;
      const LIBROS = ['Génesis', 'Gilgamesh', 'Ilíada'];
      /* Buscador del mapa. Filtra las obras igual que el filtro por libro, así que todo
         lo demás —los grupos, los abanicos, la lista, los continentes— se adapta solo:
         una sede sin obras que cumplan deja de existir para el mapa. */
      let consultaMapa = '', terminosMapa = [];

      /* Documento de una obra del mapa. Se cachea por índice: `dibujar` puede llamar a
         obrasDe cientos de veces por fotograma y normalizar texto no es gratis. */
      const cacheDoc = {};
      function docObraMapa(o, sd){
        if (cacheDoc[o.i]) return cacheDoc[o.i];
        const d = BOOKS.mapa.details[o.i] || {};
        return (cacheDoc[o.i] = {
          obra: normaliza(o.t), autor: normaliza(o.autor || d.artist),
          sede: normaliza(sd.nombre), ciudad: normaliza(sd.ciudad),
          pais: normaliza(sd.pais), libro: normaliza(o.libro),
          texto: normaliza([sd.nombre, sd.ciudad, sd.pais, o.a, d.snippet].join(' ')),
          anio: d.anio,
        });
      }

      const obrasDe = sd => {
        let os = libroFiltro ? sd.obras.filter(o => o.libro === libroFiltro) : sd.obras;
        if (terminosMapa.length)
          os = os.filter(o => puntuar(docObraMapa(o, sd), terminosMapa) >= 0);
        return os;
      };
      const activas = () => SEDES.map((s, i) => i).filter(i => obrasDe(SEDES[i]).length > 0);
      const claveGrupo = c => c.sedes.slice().sort((a, b) => a - b).join(',');
      const nombreCorto = n => {
        let t = n.replace(/^(Museo|Musée|Museos|Galería|Galleria|Monasterio de|Palacio|Ciudadela de|Yacimiento de)\s+(Nacional\s+)?(del?\s+|de\s+|d[eu]\s+)?/i, '')
                 .replace(/\s*\(.*$/, '').trim();
        if (t.length <= 22) return t;
        const corte = t.lastIndexOf(' ', 22);       // cortar por palabra, no a mitad
        return (corte > 8 ? t.slice(0, corte) : t.slice(0, 22)) + '…';
      };

      /* En horizontal no hay tope: el mundo se repite y se le puede dar la vuelta. Solo
         se normaliza la posición para que no crezca sin fin con el uso prolongado.
         En vertical sí hay tope: la Tierra no se repite de polo a polo. */
      function limitar(v){
        while (v.x >  MAPA_W * 1.5) v.x -= MAPA_W;
        while (v.x < -MAPA_W * 1.5) v.x += MAPA_W;
        const my = MAPA_H * 0.12;
        v.y = (v.h > MAPA_H + 2 * my) ? (MAPA_H - v.h) / 2
                                      : clamp(v.y, -my, MAPA_H + my - v.h);
        return v;
      }

      /* Copias del mundo que tocan la vista actual. Solo las que se ven de verdad:
         acercado hay una sola, y al cruzar el antimeridiano dos. */
      function vueltas(){
        const a = Math.floor(vista.x / MAPA_W);
        const b = Math.floor((vista.x + vista.w) / MAPA_W);
        const out = [];
        for (let k = a; k <= b; k++) out.push(k * MAPA_W);
        return out;
      }

      /* Copia del mundo en la que un punto queda más cerca del centro de la vista:
         al volar a una sede se elige la vuelta más próxima, no siempre la canónica. */
      function xCercano(x){
        const c = vista.x + vista.w / 2;
        let mejor = x, d = Infinity;
        for (let k = -2; k <= 2; k++) {
          const xx = x + k * MAPA_W;
          if (Math.abs(xx - c) < d) { d = Math.abs(xx - c); mejor = xx; }
        }
        return mejor;
      }

      /* Al desplazarse solo cambia el encuadre; la agrupación depende únicamente de la
         escala. Redibujar los marcadores en cada movimiento del ratón reconstruía decenas
         de nodos SVG por fotograma y hacía el arrastre a trompicones. */
      /* Reconstruir marcadores solo cuando cambia QUÉ hay que dibujar. Mientras se
         acerca o se desplaza, la disposición suele ser la misma y basta con reescalar,
         que es una transformación por marcador en vez de decenas de nodos nuevos. */
      let firmaDibujo = '';
      function aplicar(forzar){
        limitar(vista);
        svg.setAttribute('viewBox', `${vista.x} ${vista.y} ${vista.w} ${vista.h}`);
        const f = grupos().map(c => c.sedes.join('.')).join('|') + '@' + vueltas().join(',')
                + '#' + (ciudadAbierta || '') + '#' + grupoAbierto + '#' + sedeSel
                + '#' + (vista.w < 90);
        if (forzar || f !== firmaDibujo) { firmaDibujo = f; dibujar(); }
        else reescalar();
      }

      /* Vuela hasta un punto con un ancho de vista dado. */
      function irA(x, y, w, suave){
        const ancho = clamp(w, MIN_W, MAPA_W * 1.3);
        const alto = ancho * altoMarco() / anchoMarco();
        irAVista({ x: x - ancho / 2, y: y - alto / 2, w: ancho, h: alto }, suave);
      }

      /* Vuela hasta una vista ya calculada (la usan los botones Europa y Mundo). */
      function irAVista(v, suave){
        vistaObj = limitar(Object.assign({}, v));
        if (!suave) { vista = Object.assign({}, vistaObj); aplicar(true); return; }
        if (!anim) anim = requestAnimationFrame(paso);
      }

      /* Interpolación con umbral relativo al tamaño de la vista: con un umbral fijo, muy
         acercado la animación se cortaba de golpe y muy alejado se arrastraba.
         k gobierna lo rápido que el mapa alcanza su destino: subirlo acelera por igual la
         rueda, el pellizco, los botones y los vuelos al pulsar un grupo, sin tocar el
         tamaño de cada paso, que es lo que mantiene el movimiento suave. */
      function paso(){
        const k = 0.22;
        const eps = Math.max(vista.w, vista.h) * 0.0004;
        let quieto = true;
        for (const p of ['x','y','w','h']) {
          const d = vistaObj[p] - vista[p];
          if (Math.abs(d) > eps) { vista[p] += d * k; quieto = false; }
          else vista[p] = vistaObj[p];
        }
        aplicar();
        anim = quieto ? null : requestAnimationFrame(paso);
      }

      function zoomEn(cx, cy, factor){
        const w = clamp(vista.w / factor, MIN_W, MAPA_W * 1.3);
        const h = w * vista.h / vista.w;
        // mantener el punto (cx,cy) donde estaba
        const rx = (cx - vista.x) / vista.w, ry = (cy - vista.y) / vista.h;
        vistaObj = limitar({ x: cx - rx * w, y: cy - ry * h, w: w, h: h });
        if (!anim) anim = requestAnimationFrame(paso);
      }

      /* ---------- agrupación dependiente de la escala ---------- */
      function grupos(){
        const s = escala();
        const umbral = SEP_PX / s;        // separación mínima en píxeles de pantalla
        const g = [];
        activas().forEach(i => {
          const sd = SEDES[i];
          let en = null;
          for (const c of g) {
            if (Math.hypot(c.x - sd.x, c.y - sd.y) < umbral) { en = c; break; }
          }
          if (en) { en.sedes.push(i); en.n += obrasDe(sd).length;
                    en.x = en.sedes.reduce((a,j)=>a+SEDES[j].x,0)/en.sedes.length;
                    en.y = en.sedes.reduce((a,j)=>a+SEDES[j].y,0)/en.sedes.length; }
          else g.push({ x: sd.x, y: sd.y, sedes: [i], n: obrasDe(sd).length });
        });
        return g;
      }

      const R = n => 5 + Math.sqrt(n) * 2.6;

      function nodo(tag, attrs){
        const el = document.createElementNS(NS, tag);
        for (const k in attrs) el.setAttribute(k, attrs[k]);
        return el;
      }

      /* ---------- dibujo ---------- */
      /* Abrir una obra en el mismo visor de zoom que el resto de la página: BOOKS.mapa
         comparte los arrays de la cronología, así que el índice vale tal cual. */
      /* Al abrir desde el mapa, las flechas del visor recorren solo el conjunto del que
         se viene —el museo, la ciudad o el libro—, no la colección entera. `obras` son
         índices dentro de BOOKS.mapa, que comparte los arrays de la cronología. */
      function abrirObra(i, nombre, obras){
        currentBook = 'mapa';
        if (nombre && obras && obras.length > 1)
          openZoomForArtwork(i, 0, { nombre, obras: obras.map(x => ({ libro:'mapa', i:x })) });
        else openZoomForArtwork(i, 0);
      }
      const indices = os => os.map(o => o.i);

      /* ── DIBUJO ──────────────────────────────────────────────────────────────
         Cada marcador vive dentro de un <g transform="translate(x,y) scale(1/s)">, así
         que TODO lo que contiene —radios, tipografía, abanicos, miniaturas— se escribe en
         píxeles de pantalla y no cambia al ampliar. La ventaja es que acercar solo exige
         reescribir una transformación por marcador (reescalar), en vez de reconstruir
         decenas de nodos por fotograma, que es lo que hacía el zoom a trompicones. */

      function marca(x, y, inv){
        const g = nodo('g', { class: 'marca', transform: `translate(${x},${y}) scale(${inv})` });
        g.dataset.x = x; g.dataset.y = y;
        return g;
      }

      /* Solo cambia la escala: no se reconstruye nada. */
      function reescalar(){
        const s = escala(), inv = factorMarca(s) / s;
        capaSedes.querySelectorAll('.marca').forEach(g => {
          g.setAttribute('transform', `translate(${g.dataset.x},${g.dataset.y}) scale(${inv})`);
        });
        const fino = 1 / s;   // costa y fronteras sí mantienen grosor constante
        if (capaTierra) capaTierra.setAttribute('stroke-width', (0.7 * fino).toFixed(3));
        [frPrin, frSec].forEach(g => { if (!g) return;
          g.setAttribute('stroke-width', (1.2 * fino).toFixed(3));
          g.setAttribute('stroke-dasharray', `${(3 * fino).toFixed(2)} ${(2.6 * fino).toFixed(2)}`);
        });
        if (frPrin) frPrin.setAttribute('opacity', clamp(0.45 + (s - 0.4) * 0.30, 0.45, 0.9).toFixed(3));
        if (frSec)  frSec.setAttribute('opacity', (clamp((s - 0.9) / 2.1, 0, 1) * 0.7).toFixed(3));
      }

      function dibujar(){
        const s = escala(), inv = factorMarca(s) / s;
        capaSedes.textContent = ''; capaMundo.textContent = '';
        const vv = vueltas();

        vv.forEach(off => {
          const u = nodo('use', { x: off, y: 0 });
          u.setAttribute('href', '#mundoDef');
          u.setAttributeNS('http://www.w3.org/1999/xlink', 'href', '#mundoDef');
          capaMundo.appendChild(u);
        });

        const gs = grupos();
        /* Al acercarse, cada sede despliega sus obras sola. Con dos sedes próximas eso
           hacía que sus miniaturas se montaran unas sobre otras, así que solo se
           despliegan solas las que tienen sitio; la que se elige a mano se despliega
           siempre, porque eso lo ha pedido el usuario. */
        const holgura = c0 => {
          let d = Infinity;
          for (const o of gs) if (o !== c0) d = Math.min(d, Math.hypot(o.x - c0.x, o.y - c0.y));
          return d * s;          // s es la escala que ya calculó dibujar
        };

        gs.forEach(c0 => { vv.forEach(off => {
          const c = { x: c0.x + off, y: c0.y, sedes: c0.sedes, n: c0.n };
          const solo = c.sedes.length === 1;
          const sd = SEDES[c.sedes[0]];
          const g = marca(c.x, c.y, inv);

          const radioObras = solo ? radioFan(obrasDe(sd).length, 30, 34) : 0;
          const cabe = solo && holgura(c0) > radioObras * 2 + 14;
          const abanicoObras = solo && (grupoAbierto === c.sedes[0] || (vista.w < 90 && cabe));
          if (abanicoObras) fanObras(g, sd);
          if (!solo && ciudadAbierta === claveGrupo(c0)) fanSedes(g, c);

          const cls = 'sede' + (solo ? '' : ' grupo') + (solo && sedeSel === c.sedes[0] ? ' sel' : '');
          const p = punto(cls, 0, 0, c.n, solo
            ? `${sd.nombre}, ${sd.ciudad}: ${obrasDe(sd).length} obra${obrasDe(sd).length>1?'s':''}`
            : `${c.sedes.length} sedes agrupadas, ${c.n} obras`,
            ev => {
              ev.stopPropagation();
              if (solo) { elegirSede(c.sedes[0], true); return; }
              /* La tarjeta promete «pulsa para acercar» salvo cuando todos los museos
                 comparten ciudad, y el clic tiene que hacer exactamente eso. Antes
                 decidía con otra regla —el ancho al que el grupo se parte—, que daba por
                 indesplegable cualquier grupo muy extenso: pulsar el de 38 desplegaba
                 veinticuatro museos repartidos por todo el mapamundi en vez de volar a
                 Europa y dejar que se separaran solos al acercarse. */
              const ciudades = new Set(c.sedes.map(i => SEDES[i].ciudad));
              const destino = encajarSedes(c0.sedes, off);

              if (ciudades.size > 1) {
                ciudadAbierta = null;
                irAVista(destino, true);
                return;
              }

              /* Museos de una misma ciudad: por mucho que se acerque uno caen en el mismo
                 punto, así que se abren en abanico. Se vuela igualmente al encuadre de la
                 ciudad, que le da al abanico el sitio y la escala que necesita. */
              const k = claveGrupo(c0);
              const abriendo = ciudadAbierta !== k;
              ciudadAbierta = abriendo ? k : null;
              sedeSel = -1; abrirCiudad(c); dibujar();
              if (abriendo) irAVista(destino, true);
            },
            () => mostrarTarjeta(solo ? { sede: sd } : { grupo: c }));

          /* Al acercarse hasta ver cada museo en su sitio real desaparecía el abanico y
             con él los rótulos, así que el mapa dejaba de decir cuál era cuál. Con sitio
             de sobra alrededor, cada sede lleva su nombre debajo. */
          if (solo && holgura(c0) > 96) {
            const etq = nodo('text', { class:'sede-etq', x:0,
              y: (abanicoObras ? radioObras + 14 : R(c.n) + 12), 'font-size':8.5 });
            etq.textContent = nombreCorto(sd.nombre);
            p.appendChild(etq);
          }
          g.appendChild(p);
          capaSedes.appendChild(g);
        }); });

        reescalar();
        pista.textContent = gs.length === SEDES.length
          ? 'W A S D para moverte · + y − para acercar · pulsa un punto para desplegarlo'
          : `${gs.length} grupos · acércate o pulsa uno para separarlo`;
      }

      /* Punto de sede o de grupo, en unidades de pantalla. */
      function punto(cls, x, y, n, etiqueta, alPulsar, alEntrar){
        const r = R(n);
        const g = nodo('g', { class: cls, tabindex: '0', role: 'button' });
        g.setAttribute('aria-label', etiqueta);
        g.appendChild(nodo('circle', { class:'halo', cx:x, cy:y, r:r + 6, 'stroke-width':1.2 }));
        g.appendChild(nodo('circle', { class:'pt', cx:x, cy:y, r:r, 'stroke-width':1.1 }));
        const t = nodo('text', { class:'pt-n', x:x, y:y + 3.4, 'font-size':9 });
        t.textContent = n;
        g.appendChild(t);
        g.addEventListener('click', alPulsar);
        g.addEventListener('keydown', ev => {
          if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); alPulsar(ev); }
        });
        g.addEventListener('mouseenter', alEntrar);
        g.addEventListener('mouseleave', ocultarTarjeta);
        return g;
      }

      /* Abanico de obras alrededor de una sede, en unidades de pantalla. */
      function fanObras(cont, sd, cx = 0, cy = 0){
        const lista = obrasDe(sd);
        const n = lista.length;
        /* 30 px de separación para miniaturas de 22: con el radio anterior (26 + 3n) el
           arco era más corto que la propia miniatura y se solapaban entre ellas. */
        const rad = n <= 1 ? 34 : radioFan(n, 30, 34);
        lista.forEach((o, j) => {
          const ang = (-Math.PI / 2) + (n === 1 ? 0 : j * (2 * Math.PI / n));
          const ox = cx + Math.cos(ang) * rad, oy = cy + Math.sin(ang) * rad;
          cont.appendChild(nodo('line', { class:'hilo', x1:cx, y1:cy, x2:ox, y2:oy, 'stroke-width':0.8 }));
          const lado = 22;
          const g = nodo('g', { class:'obra-pin', tabindex:'0', role:'button' });
          g.setAttribute('aria-label', `${o.t}, ${o.a}`);
          const im = nodo('image', { x:ox - lado/2, y:oy - lado/2, width:lado, height:lado,
                                     preserveAspectRatio:'xMidYMid slice' });
          im.setAttributeNS('http://www.w3.org/1999/xlink', 'href', BOOKS.mapa.groups[o.i][0].src);
          im.setAttribute('href', BOOKS.mapa.groups[o.i][0].src);
          g.appendChild(im);
          g.appendChild(nodo('rect', { class:'marco', x:ox - lado/2, y:oy - lado/2,
                                       width:lado, height:lado, 'stroke-width':1.1 }));
          g.addEventListener('mouseenter', () => mostrarTarjeta({ obra:o, sede:sd }));
          g.addEventListener('mouseleave', ocultarTarjeta);
          g.addEventListener('click', ev => { ev.stopPropagation();
            abrirObra(o.i, sd.nombre, indices(obrasDe(sd))); });
          g.addEventListener('keydown', ev => {
            if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault();
              abrirObra(o.i, sd.nombre, indices(obrasDe(sd))); }
          });
          cont.appendChild(g);
        });
      }

      /* Radio necesario para repartir n elementos por una circunferencia dejando al menos
         `sep` píxeles entre vecinos. El abanico crece con lo que tiene que contener en vez
         de amontonarlo: con un radio fijo, cinco museos de París se pisaban unos a otros. */
      const radioFan = (n, sep, minimo) => Math.max(minimo, (sep * n) / (2 * Math.PI));

      /* Etiqueta que sale hacia fuera del nodo, no siempre por debajo. Dos rótulos vecinos
         se solapaban («SainBiblioteca Nacional de…») porque ambos caían bajo su punto;
         irradiando desde el centro, cada uno se aleja del otro por construcción. */
      function etiquetaRadial(g, texto, sx, sy, rr, dx, dy){
        let x = sx, y = sy + rr + 11, cls = 'sede-etq';
        if (Math.abs(dx) > 0.35) {                       // costados: el texto se ancla al lado
          cls += dx > 0 ? ' der' : ' izq';
          x = sx + dx * (rr + 7); y = sy + 3;
        } else {                                         // arriba y abajo: centrado
          y = sy + (dy < 0 ? -(rr + 7) : rr + 12);
        }
        const etq = nodo('text', { class: cls, x, y, 'font-size':8.5 });
        etq.textContent = texto;
        g.appendChild(etq);
      }

      /* Abanico de museos de una ciudad. Las posiciones son sintéticas: a esta escala la
         geografía ya no distingue el Louvre de Saint-Sulpice. Se reparten por toda la
         circunferencia, no por un arco de 115° encima del punto, que es donde se
         apelotonaban. */
      function fanSedes(cont, c){
        const n = c.sedes.length;
        /* Dentro del abanico de una ciudad, el museo elegido NO despliega sus obras sobre
           el mapa. No cabe: sus miniaturas piden 123 px alrededor, y el Louvre y Orsay
           están en la misma dirección desde el centro de París, así que no hay forma de
           separarlos tanto sin sacar a la Biblioteca Nacional fuera del marco. Se veía en
           la práctica: las obras del Louvre acababan por encima de los botones de
           continente. Las obras del museo elegido salen en la lista de la derecha, que se
           despliega al pulsarlo, y en el panel de debajo del mapa. */
        const radObras = 0;
        const sep = 34;
        const rad = n <= 1 ? 46 : radioFan(n, sep, 52);

        /* Disposición verdadera, no un círculo inventado. A la escala a la que una ciudad
           cabe en pantalla sus museos están a centésimas de píxel de lienzo unos de otros
           —el Louvre y Orsay, a 0,061—, así que colocarlos tal cual los apila. Ampliarlos
           conservando las distancias exactas tampoco cabe: en París el museo más lejano
           está veinte veces más lejos que el par más cercano, y estirar hasta separar ese
           par manda al otro fuera del marco.

           Se conserva entonces lo que de verdad informa a esta ampliación: el RUMBO exacto
           de cada museo respecto al centro de la ciudad —quién está al norte, quién al
           este— y el ORDEN de las distancias. Los radios se reparten por rango entre un
           mínimo legible y el borde del marco. Es una ampliación, no un plano a escala, y
           como tal dice la verdad sobre la disposición sin mentir sobre la métrica. */
        const esc = escala();
        const cx = c.sedes.reduce((a,i)=>a+SEDES[i].x,0)/n;
        const cy = c.sedes.reduce((a,i)=>a+SEDES[i].y,0)/n;

        const rumbos = c.sedes.map(i => {
          const ex = SEDES[i].x - cx, ey = SEDES[i].y - cy;
          return { i, ex, ey, r: Math.hypot(ex, ey) };
        });
        const orden = rumbos.slice().sort((a, b) => a.r - b.r);
        /* Todo el reparto se calcula en PÍXELES DE PANTALLA y se convierte al final. El
           abanico vive dentro de un grupo que a mucho zoom se agranda hasta 2,4 veces
           (factorMarca), así que un radio de 164 unidades son 394 px reales: midiendo en
           unidades, el abanico de París se salía del marco —la Biblioteca Nacional en la
           esquina con el rótulo cortado, y las obras del Louvre por encima de los botones
           de continente—. En píxeles de pantalla el marco sí acota de verdad. */
        const fm = factorMarca(esc);
        const radioMayor = Math.max(...c.sedes.map(i => R(obrasDe(SEDES[i]).length))) * fm;
        const sepPx = Math.max(2 * radioMayor + 18, radObras * fm + radioMayor + 18);
        const radioMinPx = Math.max(78, sepPx);
        const radioMaxPx = Math.max(radioMinPx, radioMinPx + 46 * (n - 1));
        const radioMin = radioMinPx / fm, radioMax = radioMaxPx / fm;
        const radioDe = {};
        orden.forEach((o, k) => {
          radioDe[o.i] = n <= 1 ? radioMin
            : radioMin + (radioMax - radioMin) * (k / (n - 1));
        });

        const sitio = rumbos.map(o => {
          const m = o.r || 1;
          return { x: (o.ex / m) * radioDe[o.i], y: (o.ey / m) * radioDe[o.i] };
        });

        /* Ajuste al marco eje por eje. Acotar por el lado corto desperdiciaba el ancho, que
           en un marco 16:9 es justo por donde el abanico se extiende. Al medir se cuenta
           también el radio de las obras del museo abierto y el sitio del rótulo: lo que se
           salía por arriba en París eran precisamente esas miniaturas. */
        const bordeX = radObras * fm + 60, bordeY = radObras * fm + 26;
        const maxX = Math.max(...sitio.map(p => Math.abs(p.x))) * fm + bordeX;
        const maxY = Math.max(...sitio.map(p => Math.abs(p.y))) * fm + bordeY;
        const cabe = Math.min(anchoMarco() * 0.46 / Math.max(maxX, 1),
                              altoMarco()  * 0.46 / Math.max(maxY, 1), 2.6);
        if (isFinite(cabe) && cabe > 0) sitio.forEach(p => { p.x *= cabe; p.y *= cabe; });

        /* Con todos los rumbos distintos esto separa bien; si dos museos coinciden en
           dirección y en rango quedarían pegados, y entonces el círculo es preferible. */
        let juntos = 0;
        for (let i = 0; i < n; i++)
          for (let j = i + 1; j < n; j++)
            if (Math.hypot(sitio[i].x - sitio[j].x, sitio[i].y - sitio[j].y) * fm < sepPx) juntos++;
        const real = n > 1 && rumbos.every(o => o.r > 0) && juntos === 0;

        c.sedes.forEach((idx, j) => {
          const sd = SEDES[idx];
          let sx, sy, dx, dy;
          if (real) {
            sx = sitio[j].x; sy = sitio[j].y;
            const m = Math.hypot(sx, sy) || 1;
            dx = sx / m; dy = sy / m;
          } else {
            const ang = (-Math.PI / 2) + (n === 1 ? 0 : j * (2 * Math.PI / n));
            dx = Math.cos(ang); dy = Math.sin(ang);
            sx = dx * rad; sy = dy * rad;
          }
          cont.appendChild(nodo('line', { class:'hilo hilo-sede', x1:0, y1:0, x2:sx, y2:sy, 'stroke-width':0.9 }));
          const k = obrasDe(sd).length;
          const g = punto('sede sede-abanico' + (sedeSel === idx ? ' sel' : ''), sx, sy,
            k, `${sd.nombre}: ${k} obra${k>1?'s':''}`,
            ev => { ev.stopPropagation(); elegirEnCiudad(idx); },
            () => mostrarTarjeta({ sede: sd }));
          etiquetaRadial(g, nombreCorto(sd.nombre), sx, sy, R(k), dx, dy);
          cont.appendChild(g);
        });
      }

      /* Elegir un museo dentro del abanico de una ciudad. Sus obras NO caben alrededor del
         punto —ver el comentario de fanSedes—, así que aparecen en la lista de la derecha,
         que se despliega, y en el panel de debajo. Antes solo se repintaba el mapa y el
         efecto era que pulsar un museo no hacía nada visible. */
      function elegirEnCiudad(idx){
        sedeSel = idx;
        grupoAbierto = idx;
        if (modo === 'sedes') pintarLista(); else
          document.querySelectorAll('.sede-item').forEach(el =>
            el.classList.toggle('sel', +el.dataset.i === idx));
        pintarDetalle(SEDES[idx]);
        dibujar();
      }

      /* ---------- tarjeta flotante ---------- */
      let ultimoRaton = {x:0, y:0};
      marco.addEventListener('mousemove', ev => {
        const r = marco.getBoundingClientRect();
        ultimoRaton = { x: ev.clientX - r.left, y: ev.clientY - r.top };
        if (!tarjeta.hidden) situarTarjeta();
      });
      function situarTarjeta(){
        const w = tarjeta.offsetWidth || 210, h = tarjeta.offsetHeight || 120;
        let x = ultimoRaton.x + 16, y = ultimoRaton.y + 16;
        if (x + w > marco.clientWidth - 8) x = ultimoRaton.x - w - 16;
        if (y + h > marco.clientHeight - 8) y = ultimoRaton.y - h - 16;
        tarjeta.style.left = Math.max(8, x) + 'px';
        tarjeta.style.top = Math.max(8, y) + 'px';
      }
      function mostrarTarjeta(q){
        if (q.obra) {
          tarjeta.innerHTML =
            `<img src="${BOOKS.mapa.groups[q.obra.i][0].src}" alt="">` +
            `<div class="tj-txt"><strong>${esc(q.obra.t)}</strong>` +
            `<span>${esc(q.obra.autor)}</span>` +
            `<em>${esc(q.obra.a)} · ${esc(q.obra.libro)}</em></div>`;
          tarjeta.className = 'mapa-tarjeta con-imagen';
        } else if (q.sede) {
          const n = q.sede.obras.length;
          tarjeta.innerHTML =
            `<div class="tj-txt"><strong>${esc(q.sede.nombre)}</strong>` +
            `<span>${esc(q.sede.ciudad)}, ${esc(q.sede.pais)}</span>` +
            `<em>${n} obra${n>1?'s':''} · pulsa para verlas</em></div>`;
          tarjeta.className = 'mapa-tarjeta';
        } else {
          const c = q.grupo;
          const ciudades = [...new Set(c.sedes.map(i => SEDES[i].ciudad))];
          const unaCiudad = ciudades.length === 1;
          tarjeta.innerHTML =
            `<div class="tj-txt"><strong>${c.n} obra${c.n>1?'s':''}</strong>` +
            `<span>${c.sedes.length} museos · ${esc(ciudades.slice(0,3).join(', '))}` +
            `${ciudades.length>3 ? '…' : ''}</span>` +
            `<em>${unaCiudad ? (ciudadAbierta === claveGrupo(c) ? 'pulsa para plegar'
                                                                 : 'pulsa para desplegar los museos')
                              : 'pulsa para acercar'}</em></div>`;
          tarjeta.className = 'mapa-tarjeta';
        }
        tarjeta.hidden = false;
        situarTarjeta();
      }
      function ocultarTarjeta(){ tarjeta.hidden = true; }

      /* ---------- lista lateral: sedes o libros ---------- */
      const nota = document.getElementById('mapaNota');
      const togSedes = document.getElementById('togSedes');
      const togLibros = document.getElementById('togLibros');
      let modo = 'sedes';

      function pintarLista(){
        lista.textContent = '';
        if (modo === 'sedes') {
          nota.textContent = consultaMapa.trim()
            ? `Solo lo que coincide con «${consultaMapa.trim()}». Vacía la búsqueda para verlo todo.`
            : libroFiltro
            ? `Solo las sedes con obras de ${libroFiltro}. Al elegir una, el mapa vuela hasta ella.`
            : 'Ordenadas por número de obras. Al elegir una, el mapa vuela hasta ella y despliega lo que guarda.';
          const idxs = activas().sort((a, b) =>
            obrasDe(SEDES[b]).length - obrasDe(SEDES[a]).length ||
            SEDES[a].ciudad.localeCompare(SEDES[b].ciudad));
          idxs.forEach(idx => {
            const sd = SEDES[idx];
            const li = document.createElement('li');
            li.className = 'sede-item' + (sedeSel === idx ? ' sel' : '');
            li.dataset.i = idx;
            li.innerHTML = `<button type="button"><span class="sede-n">${obrasDe(sd).length}</span>` +
              `<span class="sede-txt"><strong>${esc(sd.nombre)}</strong>` +
              `<em>${esc(sd.ciudad)} · ${esc(sd.pais)}</em></span></button>`;
            /* Vuelve a pulsarla y se repliega, como los libros: si no, la única forma de
               cerrar el desplegable sería elegir otra sede. */
            li.querySelector('button').addEventListener('click', () => {
              if (sedeSel === idx) {
                sedeSel = -1; grupoAbierto = -1;
                detalle.innerHTML = '';
                pintarLista(); dibujar();
              } else elegirSede(idx, true);
            });
            lista.appendChild(li);
            /* La sede elegida despliega aquí mismo lo que guarda, igual que los libros. */
            if (sedeSel === idx) lista.appendChild(obrasDeSede(idx));
          });
        } else {
          nota.textContent = 'Elige un libro para ver solo dónde está su arte. Vuelve a pulsarlo para verlos todos.';
          LIBROS.forEach(nom => {
            const obras = SEDES.reduce((a, s) => a + s.obras.filter(o => o.libro === nom).length, 0);
            const sedes = SEDES.filter(s => s.obras.some(o => o.libro === nom)).length;
            const paises = new Set(SEDES.filter(s => s.obras.some(o => o.libro === nom)).map(s => s.pais)).size;
            const li = document.createElement('li');
            li.className = 'sede-item libro-item' + (libroFiltro === nom ? ' sel' : '');
            li.innerHTML = `<button type="button"><span class="sede-n">${obras}</span>` +
              `<span class="sede-txt"><strong>${esc(nom)}</strong>` +
              `<em>${sedes} sedes · ${paises} países</em></span></button>`;
            li.querySelector('button').addEventListener('click', () => {
              libroFiltro = (libroFiltro === nom) ? null : nom;
              sedeSel = -1; grupoAbierto = -1; ciudadAbierta = null;
              pintarLista();
              pintarContinentes();   // un libro puede no tener obras en algún continente
              detalle.innerHTML = libroFiltro ? resumenLibro(libroFiltro) : '';
              aplicar(true);
              // encuadrar todas las sedes del libro: si las hay en América, se aleja
              irAVista(libroFiltro ? encajarSedes(activas()) : vistaEuropa(), true);
            });
            lista.appendChild(li);
            /* El libro elegido despliega sus obras aquí mismo, con su miniatura: antes
               solo aparecían en el panel de debajo del mapa, que queda fuera de la vista
               y obliga a desplazarse para saber qué contiene el libro recién pulsado.
               Cada una abre en el visor. */
            if (libroFiltro === nom) lista.appendChild(obrasDelLibro(nom));
          });
        }
      }

      /* Qué guarda cada sede de un libro, para el panel de abajo. */
      function resumenLibro(nom){
        // el conjunto de navegación del visor: todas las obras del libro
        const delLibro = SEDES.flatMap(s => s.obras.filter(o => o.libro === nom)).map(o => o.i);
        const bloques = SEDES
          .filter(s => s.obras.some(o => o.libro === nom))
          .sort((a, b) => b.obras.filter(o => o.libro === nom).length - a.obras.filter(o => o.libro === nom).length)
          .map(s => {
            const os = s.obras.filter(o => o.libro === nom);
            const min = os.map(o =>
              `<button class="obra-min" type="button" data-obra="${o.i}" title="${esc(o.t)}">` +
              `<img src="${BOOKS.mapa.groups[o.i][0].src}" alt="${esc(o.t)}" loading="lazy">` +
              `<span class="obra-min-t">${esc(o.t)}</span>` +
              `<span class="obra-min-m">${esc(o.a)} · ${esc(s.ciudad)}</span></button>`).join('');
            return `<div class="ciudad-sede"><h4>${esc(s.nombre)}<span>${os.length}</span></h4>` +
                   `<div class="obra-min-grid">${min}</div></div>`;
          }).join('');
        const tot = SEDES.reduce((a, s) => a + s.obras.filter(o => o.libro === nom).length, 0);
        const html = `<div class="sede-cab"><h3>${esc(nom)}</h3>` +
          `<p>${tot} obras repartidas en ${SEDES.filter(s => s.obras.some(o => o.libro === nom)).length} sedes</p></div>` + bloques;
        setTimeout(() => detalle.querySelectorAll('.obra-min').forEach(b =>
          b.addEventListener('click', () => abrirObra(+b.dataset.obra, nom, delLibro))), 0);
        return html;
      }

      /* Desplegable de obras con miniatura, el mismo para un libro y para una sede: al
         pulsar cualquiera de los dos en la lista se ve ahí mismo lo que contiene, sin
         tener que bajar al panel de debajo del mapa. */
      function obrasDelLibro(nom){
        const vistas = new Set();
        const obras = [];
        SEDES.forEach(sd => sd.obras.forEach(o => {
          if (o.libro !== nom || vistas.has(o.i)) return;
          vistas.add(o.i);
          obras.push({ o: o, sede: sd });
        }));
        obras.sort((a, b) => a.o.i - b.o.i);
        return desplegable(obras, nom);
      }

      function obrasDeSede(idx){
        const sd = SEDES[idx];
        return desplegable(sd.obras.slice().sort((a, b) => a.i - b.i)
                             .map(o => ({ o: o, sede: sd })), sd.nombre);
      }

      function desplegable(obras, nombre){
        const li = document.createElement('li');
        li.className = 'libro-obras';
        li.innerHTML = obras.map(({ o, sede }) =>
          `<button class="libro-obra" type="button" data-obra="${o.i}" title="${esc(o.t)} — ${esc(sede.nombre)}">` +
          `<img src="${BOOKS.mapa.groups[o.i][0].src}" alt="${esc(o.t)}" loading="lazy">` +
          `<span class="libro-obra-t">${esc(o.t)}</span>` +
          `<span class="libro-obra-m">${esc(o.a)} · ${esc(o.libro)}</span></button>`).join('');
        li.querySelectorAll('.libro-obra').forEach(b => {
          b.addEventListener('click', ev => { ev.stopPropagation();
            abrirObra(+b.dataset.obra, nombre, obras.map(x => x.o.i)); });
          b.addEventListener('mouseenter', () => {
            const par = obras.find(x => x.o.i === +b.dataset.obra);
            if (par) mostrarTarjeta({ obra: par.o, sede: par.sede });
          });
          b.addEventListener('mouseleave', ocultarTarjeta);
        });
        return li;
      }

      function cambiarModo(m){
        modo = m;
        togSedes.classList.toggle('activo', m === 'sedes');
        togLibros.classList.toggle('activo', m === 'libros');
        togSedes.setAttribute('aria-selected', m === 'sedes');
        togLibros.setAttribute('aria-selected', m === 'libros');
        pintarLista();
      }
      /* Buscar en el mapa. Además de filtrar, VUELA a lo encontrado: buscar «Rembrandt»
         y quedarte mirando el mundo entero no sirve de nada. Si no queda ninguna sede se
         deja la vista como estaba, que alejarse a la nada desorienta más que ayudar. */
      const contBuscMapa = document.getElementById('mapaBuscador');
      if (contBuscMapa) contBuscMapa.appendChild(cajaBusqueda('buscar-mapa',
        'Buscar obra, autor, museo, ciudad…',
        texto => {
          consultaMapa = texto;
          terminosMapa = texto.trim() ? analizar(texto) : [];
          sedeSel = -1; grupoAbierto = -1; ciudadAbierta = null;
          const quedan = activas();
          const cuenta = document.getElementById('buscar-mapa-cuenta');
          const totalObras = SEDES.reduce((a, sd) => a + obrasDe(sd).length, 0);
          if (cuenta) cuenta.innerText = texto.trim()
            ? `${totalObras} obra${totalObras === 1 ? '' : 's'} · ${quedan.length} sede${quedan.length === 1 ? '' : 's'}`
            : '';
          pintarLista(); pintarContinentes();
          detalle.innerHTML = '';
          aplicar(true);
          if (quedan.length) irAVista(encajarSedes(quedan), true);
        }));

      togSedes.addEventListener('click', () => cambiarModo('sedes'));
      togLibros.addEventListener('click', () => cambiarModo('libros'));
      pintarLista();

      function elegirSede(idx, volar){
        sedeSel = idx; grupoAbierto = idx; ciudadAbierta = null;
        const s = SEDES[idx];
        if (modo === 'sedes') pintarLista();
        if (volar) irAVista(encajarSedes([idx], xCercano(s.x) - s.x), true); else dibujar();
        pintarDetalle(s);
      }

      /* Un grupo que no se puede separar sobre el mapa se despliega como lista de
         museos de esa ciudad, cada uno con sus obras. */
      function abrirCiudad(c){
        grupoAbierto = -1;
        document.querySelectorAll('.sede-item').forEach(el => el.classList.remove('sel'));
        const ciudad = SEDES[c.sedes[0]].ciudad, pais = SEDES[c.sedes[0]].pais;
        const bloques = c.sedes.map(i => {
          const s = SEDES[i];
          const obras = s.obras.map(o =>
            `<button class="obra-min" type="button" data-obra="${o.i}" title="${esc(o.t)}">` +
            `<img src="${BOOKS.mapa.groups[o.i][0].src}" alt="${esc(o.t)}" loading="lazy">` +
            `<span class="obra-min-t">${esc(o.t)}</span>` +
            `<span class="obra-min-m">${esc(o.a)} · ${esc(o.libro)}</span></button>`).join('');
          return `<div class="ciudad-sede"><h4>${esc(s.nombre)}` +
                 `<span>${s.obras.length}</span></h4>` +
                 `<div class="obra-min-grid">${obras}</div></div>`;
        }).join('');
        detalle.innerHTML =
          `<div class="sede-cab"><h3>${esc(ciudad)}</h3>` +
          `<p>${esc(pais)} · ${c.sedes.length} museos · ${c.n} obras de la colección</p></div>` +
          bloques;
        detalle.querySelectorAll('.obra-min').forEach(b =>
          b.addEventListener('click', () => {
            const sd = SEDES.find(x => x.obras.some(o => o.i === +b.dataset.obra));
            abrirObra(+b.dataset.obra, sd ? sd.nombre : '', sd ? indices(sd.obras) : []);
          }));
      }

      function pintarDetalle(s){
        const obras = s.obras.map(o =>
          `<button class="obra-min" type="button" data-obra="${o.i}" title="${esc(o.t)}">` +
          `<img src="${BOOKS.mapa.groups[o.i][0].src}" alt="${esc(o.t)}" loading="lazy">` +
          `<span class="obra-min-t">${esc(o.t)}</span>` +
          `<span class="obra-min-m">${esc(o.a)} · ${esc(o.libro)}</span></button>`).join('');
        detalle.innerHTML = `<div class="sede-cab"><h3>${esc(s.nombre)}</h3>` +
          `<p>${esc(s.ciudad)}, ${esc(s.pais)} · ${s.obras.length} obra${s.obras.length>1?'s':''} de la colección</p></div>` +
          `<div class="obra-min-grid">${obras}</div>`;
        detalle.querySelectorAll('.obra-min').forEach(b =>
          b.addEventListener('click', () => {
            const sd = SEDES.find(x => x.obras.some(o => o.i === +b.dataset.obra));
            abrirObra(+b.dataset.obra, sd ? sd.nombre : '', sd ? indices(sd.obras) : []);
          }));
      }

      /* ---------- arrastre y rueda ---------- */
      let p0 = null;
      function empezarArrastre(cx, cy){
        if (anim) { cancelAnimationFrame(anim); anim = null; }   // no pelear con el vuelo
        vistaObj = Object.assign({}, vista);
        vel = { x: 0, y: 0 };
        arrastrando = true; movido = false;
        p0 = { x: cx, y: cy, vx: vista.x, vy: vista.y };
        marco.classList.add('arrastrando');
        ocultarTarjeta();
      }
      function moverArrastre(cx, cy){
        const s = escala();
        if (Math.abs(cx - p0.x) + Math.abs(cy - p0.y) > 4) movido = true;  // umbral en píxeles
        const nx = p0.vx - (cx - p0.x) / s, ny = p0.vy - (cy - p0.y) / s;
        vel = { x: (vista.x - nx) * 0.6 + vel.x * 0.4, y: (vista.y - ny) * 0.6 + vel.y * 0.4 };
        ultimoMov = Date.now();
        vista.x = nx; vista.y = ny;
        aplicar();
        vistaObj = Object.assign({}, vista);
      }
      /* Al soltar, el mapa sigue un poco en la dirección del gesto y frena: da la
         sensación de peso y evita el corte seco. */
      let vel = { x: 0, y: 0 }, ultimoMov = 0;
      function finArrastre(){
        if (!arrastrando) return;
        arrastrando = false; marco.classList.remove('arrastrando');
        if (Date.now() - ultimoMov < 90 && Math.hypot(vel.x, vel.y) > 0.4) {
          if (!anim) anim = requestAnimationFrame(deslizar);
        }
      }
      function deslizar(){
        vel.x *= 0.935; vel.y *= 0.935;
        if (arrastrando || Math.hypot(vel.x, vel.y) < 0.05) { anim = null; return; }
        vista.x -= vel.x; vista.y -= vel.y;
        aplicar();
        vistaObj = Object.assign({}, vista);
        anim = requestAnimationFrame(deslizar);
      }

      marco.addEventListener('mousedown', ev => {
        if (ev.button !== 0) return;
        ev.preventDefault();
        empezarArrastre(ev.clientX, ev.clientY);
      });
      window.addEventListener('mousemove', ev => { if (arrastrando) moverArrastre(ev.clientX, ev.clientY); });
      window.addEventListener('mouseup', finArrastre);
      window.addEventListener('blur', finArrastre);

      /* Táctil: un dedo desplaza, dos dedos acercan. */
      let pinza = null;
      const dist = t => Math.hypot(t[0].clientX - t[1].clientX, t[0].clientY - t[1].clientY);
      marco.addEventListener('touchstart', ev => {
        if (ev.touches.length === 1) empezarArrastre(ev.touches[0].clientX, ev.touches[0].clientY);
        else if (ev.touches.length === 2) { finArrastre(); pinza = dist(ev.touches); }
      }, { passive: true });
      marco.addEventListener('touchmove', ev => {
        if (ev.touches.length === 2 && pinza) {
          ev.preventDefault();
          const d = dist(ev.touches);
          if (d > 0) {
            const r = marco.getBoundingClientRect();
            const mx = (ev.touches[0].clientX + ev.touches[1].clientX) / 2 - r.left;
            const my = (ev.touches[0].clientY + ev.touches[1].clientY) / 2 - r.top;
            /* Mismo recorrido que el pellizco del trackpad: se acota el salto por
               fotograma para que el gesto se sienta igual de fluido en los dos sitios. */
            zoomEn(vista.x + (mx / r.width) * vista.w, vista.y + (my / r.height) * vista.h,
                   clamp(d / pinza, 0.78, 1.28));
            pinza = d;
          }
        } else if (arrastrando && ev.touches.length === 1) {
          ev.preventDefault();
          moverArrastre(ev.touches[0].clientX, ev.touches[0].clientY);
        }
      }, { passive: false });
      marco.addEventListener('touchend', () => { finArrastre(); pinza = null; });
      /* En un trackpad, deslizar dos dedos genera eventos de rueda con deltaX: si todo
         se interpretara como zoom, intentar desplazar daría saltos erráticos. El gesto de
         pellizco llega marcado con ctrlKey. */
      marco.addEventListener('wheel', ev => {
        ev.preventDefault();
        if (anim) { cancelAnimationFrame(anim); anim = null; }
        const r = marco.getBoundingClientRect();
        const pellizco = ev.ctrlKey;
        const desplaza = !pellizco && Math.abs(ev.deltaX) > Math.abs(ev.deltaY) * 0.8;
        if (desplaza) {
          const s = escala();
          vista.x += ev.deltaX / s; vista.y += ev.deltaY / s;
          aplicar(); vistaObj = Object.assign({}, vista);
          return;
        }
        const cx = vista.x + ((ev.clientX - r.left) / r.width) * vista.w;
        const cy = vista.y + ((ev.clientY - r.top) / r.height) * vista.h;
        if (pellizco) {
          /* El pellizco llega como rueda con ctrlKey, pero con incrementos de unidades
             donde la rueda da centenares. Con el divisor de la rueda se quedaba clavado
             en el paso mínimo y el gesto parecía no responder. La exponencial es la
             relación natural del gesto: separar los dedos el doble acerca el doble. */
          zoomEn(cx, cy, clamp(Math.exp(-ev.deltaY / 70), 0.78, 1.28));
          return;
        }
        const paso = clamp(Math.abs(ev.deltaY) / 300, 0.03, 0.16);   // pasos finos: acumulan suave
        zoomEn(cx, cy, ev.deltaY < 0 ? 1 + paso : 1 / (1 + paso));
      }, { passive: false });
      marco.addEventListener('click', () => { if (!movido) ocultarTarjeta(); });

      const centro = () => ({ x: vista.x + vista.w/2, y: vista.y + vista.h/2 });
      document.getElementById('mZoomIn').addEventListener('click', () => { const c=centro(); zoomEn(c.x,c.y,1.7); });
      document.getElementById('mZoomOut').addEventListener('click', () => { const c=centro(); zoomEn(c.x,c.y,1/1.7); });

      /* ---------- botones por continente ----------
         Se construyen a partir de las sedes, así que un continente se activa solo cuando
         la colección tiene alguna obra allí: si mañana entra una pieza en El Cairo,
         África deja de estar apagada sin tocar el código. */
      const CONTINENTES = ['Europa', 'Asia', 'América del Norte', 'América del Sur', 'África', 'Oceanía'];
      const CORTO = { 'América del Norte': 'N. América', 'América del Sur': 'S. América' };
      const contBar = document.getElementById('mapaContinentes');

      function sedesDe(cont){ return activas().filter(i => SEDES[i].cont === cont); }

      function pintarContinentes(){
        if (!contBar) return;
        contBar.textContent = '';
        const mundo = document.createElement('button');
        mundo.type = 'button'; mundo.id = 'mTodo'; mundo.textContent = 'Mundo';
        mundo.setAttribute('aria-label', 'Ver el mundo entero');
        mundo.addEventListener('click', () => { grupoAbierto = -1; irAVista(vistaTodo(), true); });
        contBar.appendChild(mundo);

        CONTINENTES.forEach(nom => {
          const idxs = sedesDe(nom);
          const b = document.createElement('button');
          b.type = 'button';
          if (nom === 'Europa') b.id = 'mReset';       // encuadre inicial
          b.textContent = CORTO[nom] || nom;
          const n = idxs.reduce((a, i) => a + obrasDe(SEDES[i]).length, 0);
          if (!idxs.length) {
            b.disabled = true;
            b.title = `Sin obras en ${nom}`;
            b.setAttribute('aria-disabled', 'true');
          } else {
            b.title = `${n} obra${n > 1 ? 's' : ''} en ${idxs.length} sede${idxs.length > 1 ? 's' : ''}`;
            b.addEventListener('click', () => {
              grupoAbierto = -1;
              irAVista(encajarSedes(idxs), true);
            });
          }
          contBar.appendChild(b);
        });
      }
      pintarContinentes();

      /* La pestaña arranca oculta: en cuanto el marco recibe tamaño real hay que rehacer
         el encuadre y redibujar, porque lo calculado a 0 px no vale. */
      let medido = false;
      function remedir(){
        if (!visible()) return;
        if (!medido) { medido = true; vista = vistaTodo(); vistaObj = Object.assign({}, vista); }
        else { vista.h = vista.w * altoMarco() / anchoMarco(); vistaObj = Object.assign({}, vista); }
        aplicar(true);
      }
      if (typeof ResizeObserver === 'function') new ResizeObserver(remedir).observe(marco);
      window.addEventListener('resize', remedir);

      /* ---------- teclado: las mismas teclas que el visor de obras ----------
         W A S D desplazan y + / - acercan, de forma continua mientras se mantienen.
         Solo actúan con la pestaña del mapa a la vista y con el visor de obra cerrado,
         porque allí esas teclas ya significan otra cosa. */
      const modal = document.getElementById('zoomModal');
      const visorAbierto = () => modal && modal.classList.contains('active');
      const TECLAS = ['w', 'a', 's', 'd', '+', '=', '-', '_'];
      const pulsadas = {};
      let animTeclas = null, ultimoT = 0;

      /* El avance se calcula por tiempo transcurrido, no por fotograma: así el mapa se
         mueve a la misma velocidad en una pantalla de 60 Hz y en una de 120. */
      function pasoTeclas(t){
        if (!visible() || visorAbierto()) { animTeclas = null; ultimoT = 0; return; }
        const s = escala();
        const dt = (t && ultimoT) ? clamp((t - ultimoT) / 16.67, 0.2, 3) : 1;
        ultimoT = t || 0;
        const desplaza = 5.5 * dt / s;      // ~330 px de pantalla por segundo
        let activo = false;
        if (pulsadas['a']) { vista.x -= desplaza; activo = true; }
        if (pulsadas['d']) { vista.x += desplaza; activo = true; }
        if (pulsadas['w']) { vista.y -= desplaza; activo = true; }
        if (pulsadas['s']) { vista.y += desplaza; activo = true; }
        const mas = pulsadas['+'] || pulsadas['='];
        const menos = pulsadas['-'] || pulsadas['_'];
        if (mas !== menos) {
          const base = Math.pow(1.016, dt);
          const f = mas ? base : 1 / base;
          const cx = vista.x + vista.w / 2, cy = vista.y + vista.h / 2;
          const w = clamp(vista.w / f, MIN_W, MAPA_W * 1.3);
          const h = w * vista.h / vista.w;
          vista.x = cx - w / 2; vista.y = cy - h / 2; vista.w = w; vista.h = h;
          activo = true;
        }
        if (activo) { aplicar(); vistaObj = Object.assign({}, vista); }
        if (!activo) ultimoT = 0;
        animTeclas = activo ? requestAnimationFrame(pasoTeclas) : null;
      }

      document.addEventListener('keydown', ev => {
        if (!visible() || visorAbierto()) return;
        if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
        const k = ev.key.toLowerCase();
        if (k === '0') { ev.preventDefault(); irAVista(vistaEuropa(), true); return; }
        if (!TECLAS.includes(k)) return;
        ev.preventDefault();
        if (anim) { cancelAnimationFrame(anim); anim = null; }   // el teclado manda
        pulsadas[k] = true;
        if (!animTeclas) animTeclas = requestAnimationFrame(pasoTeclas);
      });
      document.addEventListener('keyup', ev => { pulsadas[ev.key.toLowerCase()] = false; });
      window.addEventListener('blur', () => { for (const k in pulsadas) pulsadas[k] = false; });

      // estado inicial: Europa, con la sede mayor ya elegida en la lista y el detalle
      vista = vistaTodo(); vistaObj = Object.assign({}, vista);
      aplicar();
      sedeSel = 0;
      pintarLista();
      pintarDetalle(SEDES[0]);
    })();
"""
