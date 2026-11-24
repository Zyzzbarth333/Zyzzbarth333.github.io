/* Live prototype engine: rover exploration, scroll flight, hover previews, orrery transfers. Plain JS, no deps. */
(() => {
  const DATA = JSON.parse(document.getElementById('data').textContent);
  const PROJ = DATA.projects, BY = Object.fromEntries(PROJ.map(p => [p.slug, p]));
  const RM = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const C = { ink: css('--ink'), ind: css('--ind'), red: css('--red'), org: css('--org'), yel: css('--yel'), leaf: css('--leaf') || '#3E9B5F',
              paper: css('--paper'), mute: css('--mute') };

  /* ---------- shared: full-size project dialog ---------- */
  const dlg = document.querySelector('dialog.full');
  function openProject(slug) {
    const p = BY[slug]; if (!p) return;
    document.getElementById('f-m').textContent = p.meta;
    document.getElementById('f-t').textContent = p.title;
    document.getElementById('f-r').textContent = p.result;
    document.getElementById('f-o').textContent = p.outcome;
    document.getElementById('f-f').innerHTML = '<dl>' + p.facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join('') + '</dl>';
    document.getElementById('f-h').href = p.href;
    document.getElementById('f-l').innerHTML = p.figure ? `<iframe src="${p.figure}" title="Live figure: ${p.title}"></iframe>` : (p.image ? `<img src="${p.image}" alt="">` : `<div class="nofig card">${(document.getElementById('ic-' + p.slug) || {}).innerHTML || ''}</div>`);   // no figure yet: show the project's model
    dlg.showModal();
  }
  document.getElementById('f-x').onclick = () => dlg.close();
  dlg.addEventListener('close', () => { document.getElementById('f-l').innerHTML = ''; });
  dlg.addEventListener('click', ev => { if (ev.target === dlg) dlg.close(); });
  document.addEventListener('click', ev => { const b = ev.target.closest('[data-open]'); if (b) openProject(b.dataset.open); });

  /* ---------- 1. rover: frontier exploration + A* on an occupancy grid ---------- */
  (function rover() {
    const cv = document.getElementById('arena'), ctx = cv.getContext('2d');
    const sec = document.getElementById('explore'), layer = document.getElementById('placards');
    const st = document.getElementById('st'), stbar = document.getElementById('stbar');
    const CELL = 14, SENSE = 8;
    let W, H, cols, rows, occ, known, rx, ry, rh = 0, path = [], goal = null, userGoal = false, placards = [], done = false, dpr = 1, rays = [];
    // deterministic noise
    let seed = 20260712; const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
    const id = (x, y) => y * cols + x;
    const inside = (x, y) => x >= 0 && y >= 0 && x < cols && y < rows;

    function build() {
      dpr = Math.min(2, devicePixelRatio || 1);
      W = sec.clientWidth; H = sec.clientHeight;
      cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.floor(W / CELL); rows = Math.floor(H / CELL);
      occ = new Uint8Array(cols * rows); known = new Uint8Array(cols * rows); // 0 unknown, 1 free, 2 occupied
      seed = 20260712;
      // craters and rocks
      const keep = keepOut();
      const blobs = Math.round(cols * rows / 260);
      for (let i = 0; i < blobs; i++) {
        const cx = rnd() * cols, cy = rnd() * rows, r = 1.2 + rnd() * (i % 4 === 0 ? 4.5 : 2.2), ring = i % 4 === 0;
        for (let y = Math.floor(cy - r - 1); y <= cy + r + 1; y++) for (let x = Math.floor(cx - r - 1); x <= cx + r + 1; x++) {
          if (!inside(x, y)) continue; const d = Math.hypot(x - cx, y - cy);
          if (ring ? (d <= r && d >= r - 1.3) : d <= r) occ[id(x, y)] = 1;
        }
      }
      // arena walls with two gaps
      for (let x = 0; x < cols; x++) { occ[id(x, 0)] = 1; occ[id(x, rows - 1)] = 1; }
      for (let y = 0; y < rows; y++) { occ[id(0, y)] = 1; occ[id(cols - 1, y)] = 1; }
      // keep the text area clear of obstacles (so it stays readable) but drivable
      for (let y = keep.y0; y <= keep.y1; y++) for (let x = keep.x0; x <= keep.x1; x++) if (inside(x, y) && x > 0 && y > 0 && x < cols - 1 && y < rows - 1) occ[id(x, y)] = 0;
      // start bottom-right-ish, clear around it
      rx = Math.floor(cols * 0.72) + .5; ry = Math.floor(rows * 0.7) + .5;
      clear(Math.floor(rx), Math.floor(ry), 3);
      // placards: projects hidden in the arena, away from text and start
      layer.innerHTML = ''; placards = [];
      const n = DATA.found.length;
      DATA.found.forEach((slug, i) => {
        let px, py, tries = 0;
        do {
          px = 3 + Math.floor(rnd() * (cols - 6)); py = 4 + Math.floor(rnd() * (rows - 7)); tries++;
        } while (tries < 400 && (occ[id(px, py)] || inKeep(px, py, keep, 2) || Math.hypot(px - rx, py - ry) < 10 ||
                 placards.some(q => Math.hypot(q.x - px, q.y - py) < Math.max(9, cols / (n + 1)))));
        clear(px, py, 1);
        const el = document.createElement('button');
        el.type = 'button'; el.className = 'placard'; el.dataset.open = slug; el.tabIndex = -1;
        el.innerHTML = `<b>${BY[slug].title}</b><span>${BY[slug].result}</span>`;
        el.style.left = (px + .5) * CELL + 'px'; el.style.top = (py + .5) * CELL + 'px';
        layer.appendChild(el);
        placards.push({ slug, x: px, y: py, el, found: false });
      });
      path = []; goal = null; userGoal = false; done = false;
      sense();
    }
    function keepOut() {
      const hc = document.querySelector('.hero-copy').getBoundingClientRect(), s = sec.getBoundingClientRect();
      return { x0: Math.floor((hc.left - s.left) / CELL) - 1, y0: Math.floor((hc.top - s.top) / CELL) - 1,
               x1: Math.ceil((hc.right - s.left) / CELL) + 1, y1: Math.ceil((hc.bottom - s.top) / CELL) + 1 };
    }
    const inKeep = (x, y, k, m) => x >= k.x0 - m && x <= k.x1 + m && y >= k.y0 - m && y <= k.y1 + m;
    function clear(cx, cy, r) { for (let y = cy - r; y <= cy + r; y++) for (let x = cx - r; x <= cx + r; x++) if (inside(x, y) && x > 0 && y > 0 && x < cols - 1 && y < rows - 1) occ[id(x, y)] = 0; }

    // LiDAR: 90 rays, stop at the first occupied cell
    function sense() {
      const x0 = rx, y0 = ry; rays = [];
      for (let k = 0; k < 90; k++) {
        const a = k / 90 * Math.PI * 2, dx = Math.cos(a), dy = Math.sin(a); let ex = x0, ey = y0;
        for (let s = 0; s <= SENSE; s += .5) {
          const x = Math.floor(x0 + dx * s), y = Math.floor(y0 + dy * s); if (!inside(x, y)) break;
          ex = x0 + dx * s; ey = y0 + dy * s;
          if (occ[id(x, y)]) { known[id(x, y)] = 2; break; }
          known[id(x, y)] = 1;
        }
        rays.push([ex, ey]);
      }
      let n = 0;
      placards.forEach(p => {
        if (!p.found && known[id(p.x, p.y)] === 1 && Math.hypot(p.x + .5 - rx, p.y + .5 - ry) < SENSE) { p.found = true; reveal(p); }
        if (p.found) n++;
      });
      st.innerHTML = `${done ? 'arena mapped' : userGoal ? 'driving to goal' : 'exploring'} · <b>${n}/${placards.length}</b> projects found`;
      stbar.style.width = (n / placards.length * 100) + '%';
    }
    function reveal(p) { p.found = true; p.el.tabIndex = 0; requestAnimationFrame(() => p.el.classList.add('on')); }

    // A* on 8-connected grid; unknown cells are treated as free (optimistic), occupied known cells block
    function astar(sx, sy, gx, gy) {
      const N = cols * rows, g = new Float32Array(N).fill(Infinity), came = new Int32Array(N).fill(-1), closed = new Uint8Array(N);
      const open = [[0, id(sx, sy)]]; g[id(sx, sy)] = 0;
      const h = (x, y) => { const dx = Math.abs(x - gx), dy = Math.abs(y - gy); return (dx + dy) + (Math.SQRT2 - 2) * Math.min(dx, dy); };
      const blocked = (x, y) => !inside(x, y) || known[id(x, y)] === 2 || (known[id(x, y)] === 1 ? false : false);
      let it = 0;
      while (open.length && it++ < 40000) {
        let bi = 0; for (let i = 1; i < open.length; i++) if (open[i][0] < open[bi][0]) bi = i;
        const [, cur] = open.splice(bi, 1)[0]; if (closed[cur]) continue; closed[cur] = 1;
        const cx = cur % cols, cy = (cur / cols) | 0;
        if (cx === gx && cy === gy) { const out = []; let c = cur; while (c >= 0) { out.push([c % cols + .5, ((c / cols) | 0) + .5]); c = came[c]; } return out.reverse(); }
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          if (!dx && !dy) continue; const nx = cx + dx, ny = cy + dy; if (blocked(nx, ny)) continue;
          if (dx && dy && (blocked(cx + dx, cy) || blocked(cx, cy + dy))) continue;
          // keep a little clearance from known obstacles
          let pen = 0; for (let oy = -1; oy <= 1; oy++) for (let ox = -1; ox <= 1; ox++) if (inside(nx + ox, ny + oy) && known[id(nx + ox, ny + oy)] === 2) pen += .6;
          const ng = g[cur] + (dx && dy ? Math.SQRT2 : 1) + pen, ni = id(nx, ny);
          if (ng < g[ni]) { g[ni] = ng; came[ni] = cur; open.push([ng + h(nx, ny), ni]); }
        }
      }
      return null;
    }
    // frontier: known-free cells next to unknown; choose the cheapest by BFS distance, biased toward unfound placards' regions
    let frontier = [];
    function findFrontier() {
      frontier = [];
      for (let y = 1; y < rows - 1; y++) for (let x = 1; x < cols - 1; x++) {
        if (known[id(x, y)] !== 1) continue;
        if (known[id(x + 1, y)] === 0 || known[id(x - 1, y)] === 0 || known[id(x, y + 1)] === 0 || known[id(x, y - 1)] === 0) frontier.push([x, y]);
      }
      if (!frontier.length) return null;
      // BFS distances through known free cells
      const dist = new Int32Array(cols * rows).fill(-1), q = [id(Math.floor(rx), Math.floor(ry))]; dist[q[0]] = 0;
      for (let h = 0; h < q.length; h++) {
        const c = q[h], cx = c % cols, cy = (c / cols) | 0;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const nx = cx + dx, ny = cy + dy, ni = id(nx, ny);
          if (inside(nx, ny) && dist[ni] < 0 && known[ni] === 1) { dist[ni] = dist[c] + 1; q.push(ni); } }
      }
      let best = null, bs = Infinity;
      for (const [x, y] of frontier) {
        const d = dist[id(x, y)]; if (d < 0) continue;
        let gain = 0; for (let oy = -3; oy <= 3; oy++) for (let ox = -3; ox <= 3; ox++) if (inside(x + ox, y + oy) && known[id(x + ox, y + oy)] === 0) gain++;
        const score = d - gain * .45 + (d < 3 ? 20 : 0);
        if (score < bs) { bs = score; best = [x, y]; }
      }
      return best;
    }
    function plan() {
      if (!goal) {
        const f = findFrontier();
        if (!f) { done = true; sense(); return; }
        goal = f;
      }
      path = astar(Math.floor(rx), Math.floor(ry), goal[0], goal[1]) || [];
      if (!path.length) { goal = null; userGoal = false; }
    }
    function step(dt) {
      if (done && !userGoal) return;
      if (!path.length) { plan(); return; }
      const [tx, ty] = path[0];
      const ang = Math.atan2(ty - ry, tx - rx); let da = ((ang - rh + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
      rh += Math.max(-1, Math.min(1, da)) * Math.min(1, dt * 8);
      const sp = 7 * dt, d = Math.hypot(tx - rx, ty - ry);
      if (d <= sp) { rx = tx; ry = ty; path.shift(); sense();
        // replan if the next step is now known to be blocked, or periodically to use new map info
        if (path.length && known[id(Math.floor(path[0][0]), Math.floor(path[0][1]))] === 2) { path = []; }
        if (!path.length) { if (userGoal) { userGoal = false; } goal = null; }
      } else { rx += (tx - rx) / d * sp; ry += (ty - ry) / d * sp; }
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      // greenhouse glazing: faint panel grid every 6 cells
      ctx.strokeStyle = 'rgba(62,155,95,.10)'; ctx.lineWidth = 1;
      for (let x = 0; x <= cols; x += 6) { ctx.beginPath(); ctx.moveTo(x * CELL + .5, 0); ctx.lineTo(x * CELL + .5, H); ctx.stroke(); }
      for (let y = 0; y <= rows; y += 6) { ctx.beginPath(); ctx.moveTo(0, y * CELL + .5); ctx.lineTo(W, y * CELL + .5); ctx.stroke(); }
      for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
        const k = known[id(x, y)];
        if (k === 0) { ctx.fillStyle = 'rgba(30,33,38,.13)'; ctx.fillRect(x * CELL + CELL / 2 - 1, y * CELL + CELL / 2 - 1, 2, 2); }
        else if (k === 2) { ctx.fillStyle = C.ink; ctx.fillRect(x * CELL + 1, y * CELL + 1, CELL - 2, CELL - 2); }
        else { ctx.fillStyle = 'rgba(62,155,95,.07)'; ctx.fillRect(x * CELL, y * CELL, CELL, CELL); }
      }
      ctx.fillStyle = C.org; for (const [x, y] of frontier) ctx.fillRect(x * CELL + CELL / 2 - 2, y * CELL + CELL / 2 - 2, 4, 4);
      // lidar
      ctx.strokeStyle = 'rgba(46,20,153,.10)'; ctx.lineWidth = 1;
      for (const [ex, ey] of rays) { ctx.beginPath(); ctx.moveTo(rx * CELL, ry * CELL); ctx.lineTo(ex * CELL, ey * CELL); ctx.stroke(); }
      // path
      if (path.length) { ctx.strokeStyle = C.red; ctx.lineWidth = 2.5; ctx.setLineDash([7, 5]); ctx.beginPath(); ctx.moveTo(rx * CELL, ry * CELL);
        for (const [x, y] of path) ctx.lineTo(x * CELL, y * CELL); ctx.stroke(); ctx.setLineDash([]); }
      if (goal) { ctx.strokeStyle = C.red; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc((goal[0] + .5) * CELL, (goal[1] + .5) * CELL, 7, 0, 7); ctx.stroke(); }
      // placard markers
      for (const p of placards) { ctx.fillStyle = p.found ? C.yel : 'rgba(0,0,0,0)'; ctx.strokeStyle = p.found ? C.ink : 'rgba(0,0,0,0)';
        ctx.beginPath(); ctx.arc((p.x + .5) * CELL, (p.y + .5) * CELL, 6, 0, 7); ctx.fill(); ctx.stroke(); }
      // rover (top-down skid steer)
      ctx.save(); ctx.translate(rx * CELL, ry * CELL); ctx.rotate(rh);
      ctx.fillStyle = C.ink; for (const [wx, wy] of [[-9, -11], [5, -11], [-9, 7], [5, 7]]) ctx.fillRect(wx, wy, 8, 4);
      ctx.fillStyle = C.ind; ctx.fillRect(-11, -8, 22, 16); ctx.fillStyle = C.yel; ctx.fillRect(4, -4, 6, 8);
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-3, 0, 3, 0, 7); ctx.fill();
      ctx.restore();
    }
    let last = 0, running = true, vis = true;
    function loop(t) {
      const dt = Math.min(.05, (t - last) / 1000 || 0); last = t;
      if (vis && running) { for (let i = 0; i < 2; i++) step(dt / 2); draw(); }
      requestAnimationFrame(loop);
    }
    new IntersectionObserver(es => { vis = es[0].isIntersecting; }).observe(sec);
    cv.addEventListener('click', ev => {
      const r = cv.getBoundingClientRect(), gx = Math.floor((ev.clientX - r.left) / CELL), gy = Math.floor((ev.clientY - r.top) / CELL);
      if (!inside(gx, gy) || known[id(gx, gy)] === 2) return;
      goal = [gx, gy]; userGoal = true; done = false; path = astar(Math.floor(rx), Math.floor(ry), gx, gy) || [];
      if (!path.length) { goal = null; userGoal = false; } sense();
    });
    document.getElementById('showall').onclick = () => { placards.forEach(p => { if (!p.found) reveal(p); }); known.fill(1); for (let i = 0; i < occ.length; i++) if (occ[i]) known[i] = 2; frontier = []; done = true; sense(); draw(); };
    let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { build(); if (RM) document.getElementById('showall').click(); draw(); }, 200); });
    build();
    if (RM) { document.getElementById('showall').click(); draw(); } else requestAnimationFrame(loop);
  })();

  /* ---------- 2. scroll-driven HAVOC-2 flight ---------- */
  (function flight() {
    const F = DATA.flight, ev = F.ev, cv = document.getElementById('alt'), ctx = cv.getContext('2d');
    const W = cv.width, H = cv.height, pad = { l: 90, r: 30, t: 40, b: 70 }, t0 = -1, t1 = 48, amax = 600;
    const X = t => pad.l + (t - t0) / (t1 - t0) * (W - pad.l - pad.r), Y = a => H - pad.b - Math.max(0, a) / amax * (H - pad.t - pad.b);
    const pts = [...F.asc.filter(p => p[0] >= t0), ...F.dsc];
    const altAt = t => { if (t <= 0) return ev.pad; if (t > ev.brownout && t < ev.resume) return null;
      for (let i = 1; i < pts.length; i++) if (pts[i][0] >= t) { const [ta, aa] = pts[i - 1], [tb, ab] = pts[i]; return tb > ev.resume && ta < ev.brownout ? null : aa + (ab - aa) * (t - ta) / (tb - ta || 1); }
      return 0; };
    const phase = t => t <= 0 ? 'PAD' : t < ev.burnout ? 'BOOST' : t < ev.apogee_t ? 'COAST' : t < ev.brownout ? 'APOGEE' : t < ev.resume ? 'NO LOG' : t < ev.land ? 'DESCENT' : 'LANDED';
    const steps = [...document.querySelectorAll('.step')];
    function draw(T) {
      ctx.clearRect(0, 0, W, H);
      ctx.font = '22px "Chivo Mono", monospace'; ctx.fillStyle = C.mute; ctx.strokeStyle = 'rgba(30,33,38,.14)'; ctx.lineWidth = 1.5;
      for (const a of [0, 100, 200, 300, 400, 500, 600]) { ctx.beginPath(); ctx.moveTo(pad.l, Y(a)); ctx.lineTo(W - pad.r, Y(a)); ctx.stroke(); ctx.textAlign = 'right'; ctx.fillText(a + ' m', pad.l - 12, Y(a) + 7); }
      ctx.textAlign = 'center'; for (const t of [0, 10, 20, 30, 40]) ctx.fillText(t + ' s', X(t), H - pad.b + 34);
      // brownout band
      ctx.fillStyle = 'rgba(255,81,2,.10)'; ctx.fillRect(X(ev.brownout), pad.t, X(ev.resume) - X(ev.brownout), H - pad.t - pad.b);
      ctx.fillStyle = C.org; ctx.textAlign = 'left'; ctx.fillText('no log', X(ev.brownout) + 10, pad.t + 26);
      // flown so far
      ctx.lineWidth = 5; ctx.lineJoin = 'round';
      const seg = (list, col) => { ctx.strokeStyle = col; ctx.beginPath(); let s = false; for (const [t, a] of list) { if (t > T) break; s ? ctx.lineTo(X(t), Y(a)) : ctx.moveTo(X(t), Y(a)); s = true; } ctx.stroke(); };
      seg(F.asc, C.ind); seg(F.dsc, C.red);
      if (T > ev.brownout) { ctx.setLineDash([10, 10]); ctx.lineWidth = 3; ctx.strokeStyle = C.mute; const a0 = F.asc[F.asc.length - 1], b0 = F.dsc[0];
        const tt = Math.min(T, b0[0]); ctx.beginPath(); ctx.moveTo(X(a0[0]), Y(a0[1])); ctx.lineTo(X(tt), Y(a0[1] + (b0[1] - a0[1]) * (tt - a0[0]) / (b0[0] - a0[0]))); ctx.stroke(); ctx.setLineDash([]); }
      // markers
      const mk = (t, a, label) => { if (T < t) return; ctx.fillStyle = C.yel; ctx.strokeStyle = C.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(X(t), Y(a), 10, 0, 7); ctx.fill(); ctx.stroke();
        ctx.fillStyle = C.ink; ctx.textAlign = 'left'; ctx.fillText(label, X(t) + 18, Y(a) - 12); };
      mk(ev.burnout, altAt(ev.burnout) || 0, 'burnout 11.65 g'); mk(ev.apogee_t, ev.apogee_m, 'apogee ~540 m');
      if (T >= ev.land) mk(ev.land, F.dsc[F.dsc.length - 1][1], 'landed');
      // craft
      const a = altAt(T); if (a != null && T > 0 && T < ev.land) { ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(X(T), Y(a), 12, 0, 7); ctx.fill(); }
      document.getElementById('ro-t').textContent = 'T+' + Math.max(0, T).toFixed(1);
      document.getElementById('ro-a').textContent = a == null ? '----' : Math.round(a);
      document.getElementById('ro-p').textContent = phase(T);
    }
    function onScroll() {
      const s = steps.map(el => el.getBoundingClientRect()), mid = innerHeight * .55;
      let T = 0;
      for (let i = 0; i < steps.length; i++) {
        const ta = +steps[i].dataset.t, tb = i + 1 < steps.length ? +steps[i + 1].dataset.t : ev.land + 1.5;
        const c = s[i].top + s[i].height / 2;
        if (c <= mid) { const nc = i + 1 < steps.length ? s[i + 1].top + s[i + 1].height / 2 : c + s[i].height; T = ta + (tb - ta) * Math.min(1, (mid - c) / (nc - c)); }
        steps[i].classList.toggle('on', Math.abs(c - mid) < s[i].height * .55);
      }
      if (s[0].top + s[0].height / 2 > mid) T = Math.min(0, -1 + (1 - Math.min(1, (s[0].top + s[0].height / 2 - mid) / innerHeight)));
      draw(T);
    }
    if (RM) { steps.forEach(s => s.classList.add('on')); draw(ev.land + 1); }
    else { let queued = false; addEventListener('scroll', () => { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; onScroll(); }); }, { passive: true }); onScroll(); }
  })();

  /* ---------- 3. projects wake on hover ---------- */
  (function wake() {
    const pv = document.getElementById('pv'), t = document.getElementById('pv-t'), s = document.getElementById('pv-s'), open = document.getElementById('pv-open');
    const cache = new Map(); let cur = null, timer;
    function show(slug) {
      if (slug === cur) return; cur = slug; const p = BY[slug];
      document.querySelectorAll('.prow').forEach(r => r.classList.toggle('on', r.dataset.slug === slug));
      t.textContent = p.title; s.textContent = p.result + ' · ' + p.summary; open.hidden = false; open.onclick = () => openProject(slug);
      let el = cache.get(slug);
      if (!el) {
        el = p.figure ? Object.assign(document.createElement('iframe'), { src: p.figure, title: 'Live figure: ' + p.title, loading: 'eager' })
                      : Object.assign(document.createElement('img'), { src: p.image || '', alt: '' });
        el.addEventListener('load', () => { if (cur === slug) el.classList.add('on'); });
        pv.appendChild(el); cache.set(slug, el);
        if (cache.size > 4) { const [k, old] = cache.entries().next().value; if (k !== slug) { old.remove(); cache.delete(k); } }
      }
      pv.querySelectorAll('iframe,img,.ph').forEach(x => x.classList.toggle('on', x === el && (x.complete || x.tagName === 'IFRAME' && x.dataset.ok)));
      if (el.tagName === 'IFRAME') { el.addEventListener('load', () => { el.dataset.ok = 1; if (cur === slug) el.classList.add('on'); }, { once: true }); if (el.dataset.ok) el.classList.add('on'); }
      else if (el.complete) el.classList.add('on');
      const ph = pv.querySelector('.ph'); if (ph) ph.remove();
    }
    document.querySelectorAll('.prow').forEach(r => {
      const go = () => { clearTimeout(timer); timer = setTimeout(() => show(r.dataset.slug), 140); };
      r.addEventListener('mouseenter', go); r.addEventListener('focusin', go);
    });
    show(PROJ[0].slug);
  })();

  /* ---------- 4. orrery: Hohmann transfers between project orbits ---------- */
  (function orrery() {
    const cv = document.getElementById('sky'), ctx = cv.getContext('2d'), W = cv.width, H = cv.height, cx = W / 2, cy = H / 2;
    const msg = document.getElementById('mission'), btns = [...document.querySelectorAll('[data-fly]')];
    const mu = 4e6, n = PROJ.length, R0 = 90, RS = (Math.min(W, H) / 2 - 40 - R0) / n;
    const bodies = PROJ.map((p, i) => ({ slug: p.slug, title: p.title, r: R0 + RS * (i + 1), th: i * 2.39996, col: [C.yel, C.org, C.red, C.ind, C.leaf][i % 5] }));
    bodies.forEach(b => b.w = Math.sqrt(mu / b.r ** 3));
    const ship = { r: R0, th: 0, w: Math.sqrt(mu / R0 ** 3), mode: 'park', at: null };
    let target = null, tr = null, warp = 1, hover = null;
    const ang = a => ((a % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
    function request(slug) {
      if (tr) return; target = bodies.find(b => b.slug === slug); if (!target) return;
      btns.forEach(b => b.classList.toggle('on', b.dataset.fly === slug));
      if (ship.at === target) { openProject(slug); return; }
      const r1 = ship.r, r2 = target.r, a = (r1 + r2) / 2, T = Math.PI * Math.sqrt(a ** 3 / mu);
      const need = ang(Math.PI - target.w * T * (r2 > r1 ? 1 : 1));
      ship.mode = 'wait'; ship.T = T; ship.need = need; ship.a = a;
      msg.textContent = `Destination ${target.title}. Transfer ${(T).toFixed(1)} s, Δv ${dv(r1, r2).toFixed(0)} units. Waiting for a ${(need * 180 / Math.PI).toFixed(0)}° phase angle...`;
    }
    const dv = (r1, r2) => { const a = (r1 + r2) / 2; const v1 = Math.sqrt(mu / r1), va = Math.sqrt(mu * (2 / r1 - 1 / a)), vb = Math.sqrt(mu * (2 / r2 - 1 / a)), v2 = Math.sqrt(mu / r2); return Math.abs(va - v1) + Math.abs(v2 - vb); };
    function tick(dt) {
      warp = ship.mode === 'wait' ? 12 : 1; const h = dt * warp;
      bodies.forEach(b => b.th += b.w * h);
      if (ship.mode === 'park') { if (ship.at) { ship.th = ship.at.th; } else ship.th += ship.w * h; }
      else if (ship.mode === 'wait') {
        if (ship.at) ship.th = ship.at.th; else ship.th += ship.w * h;
        const phi = ang(target.th - ship.th);
        if (Math.abs(phi - ship.need) < ship.w * h * 1.5 + target.w * h * 1.5 + .004) {
          tr = { r1: ship.r, r2: target.r, th0: ship.th, t: 0, T: ship.T, a: ship.a, e: Math.abs(target.r - ship.r) / (target.r + ship.r) };
          ship.mode = 'fly'; ship.at = null; msg.textContent = `Burn. Coasting to ${target.title}...`;
        }
      } else if (ship.mode === 'fly') {
        tr.t += h; const f = Math.min(1, tr.t / tr.T);
        // position on the transfer ellipse: solve Kepler for mean anomaly M = pi*f (periapsis at the inner radius)
        const out = tr.r2 > tr.r1, e = tr.e, M = Math.PI * f; let E = M; for (let i = 0; i < 8; i++) E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
        let nu = 2 * Math.atan2(Math.sqrt(1 + e) * Math.sin(E / 2), Math.sqrt(1 - e) * Math.cos(E / 2));
        const r = tr.a * (1 - e * Math.cos(E));
        if (!out) { /* inward: start at apoapsis */ const E2 = Math.PI + E; nu = 2 * Math.atan2(Math.sqrt(1 + e) * Math.sin(E2 / 2), Math.sqrt(1 - e) * Math.cos(E2 / 2)) - Math.PI; }
        ship.r = out ? r : tr.a * (1 + e * Math.cos(E)); ship.th = tr.th0 + (out ? nu : ang(nu + 2 * Math.PI) );
        if (f >= 1) { ship.r = target.r; ship.at = target; ship.mode = 'park'; tr = null; msg.textContent = `Arrived at ${target.title}. Opening the file.`; setTimeout(() => openProject(target.slug), 450); }
      }
    }
    function draw() {
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = C.yel; ctx.beginPath(); ctx.arc(cx, cy, 26, 0, 7); ctx.fill();
      ctx.font = '600 20px "Chivo Mono", monospace'; ctx.fillStyle = '#15102b'; ctx.textAlign = 'center'; ctx.fillText('IJZ', cx, cy + 7);
      ctx.strokeStyle = 'rgba(255,255,255,.12)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(cx, cy, R0, 0, 7); ctx.stroke();
      bodies.forEach(b => { ctx.strokeStyle = b === hover || b === target ? 'rgba(255,201,8,.6)' : 'rgba(255,255,255,.12)'; ctx.beginPath(); ctx.arc(cx, cy, b.r, 0, 7); ctx.stroke(); });
      if (ship.mode === 'wait' || tr) { // predicted transfer arc
        const r1 = tr ? tr.r1 : ship.r, r2 = target.r, a = (r1 + r2) / 2, e = Math.abs(r2 - r1) / (r1 + r2), th0 = tr ? tr.th0 : ship.th, out = r2 > r1;
        ctx.setLineDash([8, 8]); ctx.strokeStyle = C.org; ctx.lineWidth = 2.5; ctx.beginPath();
        for (let k = 0; k <= 60; k++) { const nu = Math.PI * k / 60, r = out ? a * (1 - e * e) / (1 + e * Math.cos(nu)) : a * (1 - e * e) / (1 - e * Math.cos(nu));
          const x = cx + r * Math.cos(th0 + nu), y = cy + r * Math.sin(th0 + nu); k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
        ctx.stroke(); ctx.setLineDash([]);
      }
      bodies.forEach(b => { const x = cx + b.r * Math.cos(b.th), y = cy + b.r * Math.sin(b.th);
        ctx.fillStyle = b.col; ctx.beginPath(); ctx.arc(x, y, b === hover || b === target ? 13 : 9, 0, 7); ctx.fill();
        if (b === hover || b === target) { ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.font = '500 22px "Chivo Mono", monospace'; ctx.fillText(b.title, x + 18, y + 7); } });
      const sx = cx + ship.r * Math.cos(ship.th), sy = cy + ship.r * Math.sin(ship.th);
      ctx.save(); ctx.translate(sx, sy); ctx.rotate(ship.th + Math.PI / 2 * (ship.mode === 'fly' ? 1 : 1));
      ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(0, -11); ctx.lineTo(7, 8); ctx.lineTo(-7, 8); ctx.closePath(); ctx.fill();
      if (ship.mode === 'fly' && tr && tr.t < .4) { ctx.fillStyle = C.org; ctx.beginPath(); ctx.moveTo(-4, 9); ctx.lineTo(0, 22); ctx.lineTo(4, 9); ctx.fill(); }
      ctx.restore();
    }
    let last = 0, vis = false;
    function loop(t) { const dt = Math.min(.05, (t - last) / 1000 || 0); last = t; if (vis) { tick(dt); draw(); } requestAnimationFrame(loop); }
    new IntersectionObserver(es => { vis = es[0].isIntersecting; }).observe(cv);
    const pick = ev => { const r = cv.getBoundingClientRect(), k = W / r.width, x = (ev.clientX - r.left) * k, y = (ev.clientY - r.top) * k;
      let best = null, bd = 40 * k; bodies.forEach(b => { const d = Math.hypot(cx + b.r * Math.cos(b.th) - x, cy + b.r * Math.sin(b.th) - y); if (d < bd) { bd = d; best = b; } }); return best; };
    cv.addEventListener('mousemove', ev => { hover = pick(ev); cv.style.cursor = hover ? 'pointer' : 'default'; });
    cv.addEventListener('click', ev => { const b = pick(ev); if (b) request(b.slug); });
    btns.forEach(b => b.addEventListener('click', () => request(b.dataset.fly)));
    if (RM) { draw(); btns.forEach(b => b.onclick = () => openProject(b.dataset.fly)); cv.onclick = ev => { const b = pick(ev); if (b) openProject(b.slug); }; }
    else requestAnimationFrame(loop);
  })();

  /* nav highlight */
  const links = [...document.querySelectorAll('header.top nav a')];
  const io = new IntersectionObserver(es => es.forEach(x => { if (x.isIntersecting) links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + x.target.id)); }), { rootMargin: '-45% 0px -50% 0px' });
  links.forEach(a => { const s = document.querySelector(a.getAttribute('href')); if (s) io.observe(s); });
})();
