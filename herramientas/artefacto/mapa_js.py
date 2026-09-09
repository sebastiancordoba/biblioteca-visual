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
      const MIN_W = 8;
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
        const MIN_CAJA = 42;   // evita acercarse en exceso a una sede suelta
        const cx = (Math.min(...xs) + Math.max(...xs)) / 2;
        const cy = (Math.min(...ys) + Math.max(...ys)) / 2;
        const w = Math.max(Math.max(...xs) - Math.min(...xs), MIN_CAJA);
        const h = Math.max(Math.max(...ys) - Math.min(...ys), MIN_CAJA * 0.55);
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
      const obrasDe = sd => libroFiltro ? sd.obras.filter(o => o.libro === libroFiltro) : sd.obras;
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
         acercado la animación se cortaba de golpe y muy alejado se arrastraba. */
      function paso(){
        const k = 0.15;
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

      /* Ancho de vista con el que un grupo se parte en dos.
         Lo decide el diámetro del grupo (la pareja más lejana), no la más cercana: un
         grupo que junta Roma, Florencia y Venecia debe poder separarse aunque dos de sus
         museos compartan ciudad. Usar la distancia mínima daba por inseparable el grupo
         entero en cuanto dos sedes estaban pegadas. */
      function anchoParaSeparar(idxs){
        let dmax = 0;
        for (let i = 0; i < idxs.length; i++)
          for (let j = i + 1; j < idxs.length; j++)
            dmax = Math.max(dmax, Math.hypot(SEDES[idxs[i]].x - SEDES[idxs[j]].x,
                                             SEDES[idxs[i]].y - SEDES[idxs[j]].y));
        if (dmax === 0) return MIN_W;
        return Math.max(dmax * anchoMarco() / SEP_PX * 0.6, MIN_W);
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
      function abrirObra(i){ currentBook = 'mapa'; openZoomForArtwork(i, 0); }

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
        gs.forEach(c0 => { vv.forEach(off => {
          const c = { x: c0.x + off, y: c0.y, sedes: c0.sedes, n: c0.n };
          const solo = c.sedes.length === 1;
          const sd = SEDES[c.sedes[0]];
          const g = marca(c.x, c.y, inv);

          if (solo && (grupoAbierto === c.sedes[0] || vista.w < 90)) fanObras(g, sd);
          if (!solo && ciudadAbierta === claveGrupo(c0)) fanSedes(g, c);

          const cls = 'sede' + (solo ? '' : ' grupo') + (solo && sedeSel === c.sedes[0] ? ' sel' : '');
          g.appendChild(punto(cls, 0, 0, c.n, solo
            ? `${sd.nombre}, ${sd.ciudad}: ${obrasDe(sd).length} obra${obrasDe(sd).length>1?'s':''}`
            : `${c.sedes.length} sedes agrupadas, ${c.n} obras`,
            ev => {
              ev.stopPropagation();
              if (solo) { elegirSede(c.sedes[0], true); return; }
              const w = anchoParaSeparar(c.sedes);
              if (w > MIN_W * 1.05 && w < vista.w * 0.92) irAVista(encajarSedes(c0.sedes, off), true);
              else {
                const k = claveGrupo(c0);
                const abriendo = ciudadAbierta !== k;
                ciudadAbierta = abriendo ? k : null;
                sedeSel = -1; abrirCiudad(c); dibujar();
                // centrar sin cambiar la escala: el abanico necesita sitio alrededor
                if (abriendo) irA(c.x, c.y, vista.w, true);
              }
            },
            () => mostrarTarjeta(solo ? { sede: sd } : { grupo: c })));
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
        const rad = 26 + n * 3;
        lista.forEach((o, j) => {
          const ang = (-Math.PI / 2) + (j - (n - 1) / 2) * (n === 1 ? 0 : Math.min(1.05, 2.4 / n));
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
          g.addEventListener('click', ev => { ev.stopPropagation(); abrirObra(o.i); });
          g.addEventListener('keydown', ev => {
            if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); abrirObra(o.i); }
          });
          cont.appendChild(g);
        });
      }

      /* Abanico de museos de una ciudad. Las posiciones son sintéticas: a esta escala la
         geografía ya no distingue el Louvre de Saint-Sulpice. */
      function fanSedes(cont, c){
        const n = c.sedes.length, rad = 30 + n * 7;
        c.sedes.forEach((idx, j) => {
          const sd = SEDES[idx];
          const ang = (-Math.PI / 2) + (j - (n - 1) / 2) * (n === 1 ? 0 : Math.min(1.15, 2.5 / n));
          const sx = Math.cos(ang) * rad, sy = Math.sin(ang) * rad;
          cont.appendChild(nodo('line', { class:'hilo hilo-sede', x1:0, y1:0, x2:sx, y2:sy, 'stroke-width':0.9 }));
          if (sedeSel === idx) fanObras(cont, sd, sx, sy);
          const g = punto('sede sede-abanico' + (sedeSel === idx ? ' sel' : ''), sx, sy,
            obrasDe(sd).length, `${sd.nombre}: ${obrasDe(sd).length} obra${obrasDe(sd).length>1?'s':''}`,
            ev => { ev.stopPropagation(); elegirEnCiudad(idx); },
            () => mostrarTarjeta({ sede: sd }));
          const etq = nodo('text', { class:'sede-etq', x:sx, y:sy + R(obrasDe(sd).length) + 11, 'font-size':8.5 });
          etq.textContent = nombreCorto(sd.nombre);
          g.appendChild(etq);
          cont.appendChild(g);
        });
      }

      function elegirEnCiudad(idx){
        sedeSel = idx;
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
            `<em>${n} obra${n>1?'s':''} · pulsa para desplegar</em></div>`;
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
          nota.textContent = libroFiltro
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
            li.querySelector('button').addEventListener('click', () => elegirSede(idx, true));
            lista.appendChild(li);
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
          });
        }
      }

      /* Qué guarda cada sede de un libro, para el panel de abajo. */
      function resumenLibro(nom){
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
          b.addEventListener('click', () => abrirObra(+b.dataset.obra))), 0);
        return html;
      }

      function cambiarModo(m){
        modo = m;
        togSedes.classList.toggle('activo', m === 'sedes');
        togLibros.classList.toggle('activo', m === 'libros');
        togSedes.setAttribute('aria-selected', m === 'sedes');
        togLibros.setAttribute('aria-selected', m === 'libros');
        pintarLista();
      }
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
          b.addEventListener('click', () => abrirObra(+b.dataset.obra)));
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
          b.addEventListener('click', () => abrirObra(+b.dataset.obra)));
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
            zoomEn(vista.x + (mx / r.width) * vista.w, vista.y + (my / r.height) * vista.h, d / pinza);
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
        const paso = clamp(Math.abs(ev.deltaY) / 430, 0.022, 0.12);  // pasos finos: acumulan suave
        zoomEn(cx, cy, ev.deltaY < 0 ? 1 + paso : 1 / (1 + paso));
      }, { passive: false });
      marco.addEventListener('click', () => { if (!movido) ocultarTarjeta(); });

      const centro = () => ({ x: vista.x + vista.w/2, y: vista.y + vista.h/2 });
      document.getElementById('mZoomIn').addEventListener('click', () => { const c=centro(); zoomEn(c.x,c.y,1.45); });
      document.getElementById('mZoomOut').addEventListener('click', () => { const c=centro(); zoomEn(c.x,c.y,1/1.45); });

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
          const base = Math.pow(1.011, dt);
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
