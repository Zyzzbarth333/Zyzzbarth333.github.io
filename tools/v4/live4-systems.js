  /* ---------- airbrakes: coast with a predicted-apogee controller; the real airbrake renders open in step ---------- */
  (function airbrakes() {
    const cv = document.getElementById('ab'); if (!cv) return;
    const ctx = cv.getContext('2d'), W = cv.width, H = cv.height, frames = [...document.querySelectorAll('#ab-model .abf')];
    const out = { p: document.getElementById('ab-p'), u: document.getElementById('ab-u'), e: document.getElementById('ab-e'), d: document.getElementById('ab-d'), deg: document.getElementById('ab-deg') };
    const g = 9.81, k0 = 0.0002, kb = 1.3, h0 = 600, v0 = 290, pad = { l: 92, r: 40, t: 40, b: 96 }, T1 = 19, A0 = 500, A1 = 3300;
    let target = 2900, drag = false, scrub = null; const LOCK = 2.5;   // deployment lockout after burnout
    const X = t => pad.l + t / T1 * (W - pad.l - pad.r), Y = a => H - pad.b - (a - A0) / (A1 - A0) * (H - pad.t - pad.b);
    const Yi = y => A0 + (H - pad.b - y) / (H - pad.t - pad.b) * (A1 - A0);
    const kk = u => k0 * (1 + kb * u), predict = (h, v, u) => h + Math.log(1 + kk(u) * v * v / g) / (2 * kk(u));
    function simulate(ctrl) { let h = h0, v = v0, u = 0, t = 0; const tr = []; const dt = .02;
      while (v > 0 && t < T1) { if (ctrl && t >= LOCK) { const err = predict(h, v, u) - target; const want = Math.max(0, Math.min(1, u + err * .004)); u += Math.max(-1.5 * dt, Math.min(1.5 * dt, want - u)); }
        v += (-g - kk(u) * v * v) * dt; h += v * dt; t += dt; tr.push([t, h, u, predict(h, Math.max(v, 0), u)]); } return tr; }
    let shut = simulate(false), ctl, ev, t0 = performance.now();
    function reset() { ctl = simulate(true); t0 = performance.now();
      const open = ctl.find(p => p[2] > .02), peak = ctl.reduce((a, p) => p[2] > a[2] ? p : a, ctl[0]);
      ev = { open, peak, apo: ctl[ctl.length - 1] }; out.d.textContent = open ? 'T+' + open[0].toFixed(1) + ' s' : 'never'; }
    reset();
    function mark(t, label, col, row) { const x = X(t); ctx.strokeStyle = col; ctx.lineWidth = 2; ctx.setLineDash([4, 6]); ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, H - pad.b); ctx.stroke(); ctx.setLineDash([]);
      ctx.font = '600 19px "Chivo Mono", monospace'; const w = ctx.measureText(label).width + 14; const y = pad.t + 6 + row * 30; ctx.fillStyle = col; ctx.fillRect(x + 4, y, w, 26); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.fillText(label, x + 11, y + 19); }
    function draw(now) {
      const T = scrub != null ? scrub : RM ? 99 : Math.max(0, (now - t0) / 1000) * 2.8, idx = Math.max(0, Math.min(ctl.length - 1, Math.floor(T / .02))), cur = ctl[idx];
      ctx.clearRect(0, 0, W, H); ctx.font = '20px "Chivo Mono", monospace'; ctx.lineWidth = 1.5;
      for (let a = 500; a <= 3300; a += 500) { ctx.strokeStyle = 'rgba(30,33,38,.12)'; ctx.beginPath(); ctx.moveTo(pad.l, Y(a)); ctx.lineTo(W - pad.r, Y(a)); ctx.stroke(); ctx.fillStyle = C.mute; ctx.textAlign = 'right'; ctx.fillText(a + ' m', pad.l - 10, Y(a) + 6); }
      ctx.textAlign = 'center'; for (let t = 0; t <= 15; t += 5) ctx.fillText(t + ' s', X(t), H - pad.b + 28);
      ctx.fillStyle = 'rgba(30,33,38,.06)'; ctx.fillRect(X(0), pad.t, X(LOCK) - X(0), H - pad.b - pad.t); ctx.fillStyle = C.mute; ctx.font = '16px "Chivo Mono", monospace'; ctx.textAlign = 'left'; ctx.fillText('lockout', X(0) + 6, H - pad.b - 8); ctx.font = '20px "Chivo Mono", monospace';
      ctx.setLineDash([6, 8]); ctx.strokeStyle = C.mute; ctx.lineWidth = 3; ctx.beginPath(); shut.forEach(([t, h], i) => i ? ctx.lineTo(X(t), Y(h)) : ctx.moveTo(X(t), Y(h))); ctx.stroke(); ctx.setLineDash([]);
      const sa = shut[shut.length - 1]; ctx.fillStyle = C.mute; ctx.textAlign = 'right'; ctx.fillText('brakes shut: ' + Math.round(sa[1]) + ' m', X(sa[0]) - 8, Y(sa[1]) - 12);
      ctx.strokeStyle = C.yel; ctx.lineWidth = 5; ctx.setLineDash([14, 8]); ctx.beginPath(); ctx.moveTo(pad.l, Y(target)); ctx.lineTo(W - pad.r, Y(target)); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = C.ink; ctx.fillRect(pad.l + 10, Y(target) - 17, 210, 34); ctx.fillStyle = C.yel; ctx.textAlign = 'left'; ctx.fillText('target ' + Math.round(target) + ' m  ↕', pad.l + 22, Y(target) + 7);
      // flown so far, coloured by deployment
      for (let i = 1; i <= idx; i++) { const [ta, ha] = ctl[i - 1], [tb, hb, u] = ctl[i]; ctx.strokeStyle = u > .02 ? `rgb(${46 + 209 * u},${20 + 61 * u},${153 - 151 * u})` : C.ind; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(X(ta), Y(ha)); ctx.lineTo(X(tb), Y(hb)); ctx.stroke(); }
      // deployment strip
      const sy = H - pad.b + 46; ctx.fillStyle = 'rgba(30,33,38,.08)'; ctx.fillRect(pad.l, sy, W - pad.l - pad.r, 26);
      for (let i = 0; i <= idx; i++) { const [t, , u] = ctl[i]; ctx.fillStyle = C.org; const hh = 26 * u; ctx.fillRect(X(t), sy + 26 - hh, Math.max(1, X(.02) - X(0) + .5), hh); }
      ctx.fillStyle = C.mute; ctx.textAlign = 'left'; ctx.font = '16px "Chivo Mono", monospace'; ctx.fillText('brake deployment', pad.l + 4, sy - 6);
      if (ev.open && T >= ev.open[0]) mark(ev.open[0], 'brakes open T+' + ev.open[0].toFixed(1), C.org, 0);
      if (ev.peak && T >= ev.peak[0] && ev.peak[2] > .05) mark(ev.peak[0], 'peak ' + Math.round(ev.peak[2] * 100) + '%', C.red, 1);
      const fin = idx >= ctl.length - 1;
      if (fin) { const a = ev.apo; ctx.fillStyle = C.leaf; ctx.beginPath(); ctx.arc(X(a[0]), Y(a[1]), 10, 0, 7); ctx.fill(); mark(a[0], 'apogee ' + Math.round(a[1]) + ' m', C.leaf, 2); }
      else { ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(X(cur[0]), Y(cur[1]), 9, 0, 7); ctx.fill(); }
      // the airbrake model: nearest of the six rendered flap angles (0 to 80 degrees)
      const deg = cur[2] * 80, fi = Math.max(0, Math.min(5, Math.round(deg / 16))); frames.forEach((f, i) => f.classList.toggle('on', i === fi));
      out.deg.textContent = Math.round(deg) + '°'; if (window.AB3D) window.AB3D.set(deg, cur[1], idx ? (cur[1] - ctl[idx - 1][1]) / .02 : 290); const ha = document.getElementById('ab-hud'); if (ha) ha.textContent = `${Math.round(cur[1])} m · ${Math.round(idx ? (cur[1] - ctl[idx - 1][1]) / .02 : 290)} m/s`;
      out.p.textContent = Math.round(cur[3]) + ' m'; out.u.textContent = Math.round(cur[2] * 100) + '%';
      out.e.textContent = fin ? (Math.round(cur[1] - target) >= 0 ? '+' : '') + Math.round(cur[1] - target) + ' m' : '...';
      if (scrub != null) { const x = X(Math.min(cur[0], scrub)); ctx.strokeStyle = C.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x, pad.t); ctx.lineTo(x, H - pad.b + 72); ctx.stroke();
        ctx.font = '600 19px "Chivo Mono", monospace'; const lab = `T+${cur[0].toFixed(1)} s · ${Math.round(cur[1])} m · flaps ${Math.round(cur[2] * 80)}°`, w = ctx.measureText(lab).width + 16;
        const lx = Math.min(x + 8, W - pad.r - w); ctx.fillStyle = C.ink; ctx.fillRect(lx, H - pad.b - 40, w, 28); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.fillText(lab, lx + 8, H - pad.b - 20); }
      if (fin && !RM && scrub == null && T > ctl.length * .02 + 3) reset();
    }
    let vis = false; new IntersectionObserver(es => { vis = es[0].isIntersecting; if (vis) reset(); }).observe(cv);
    const loop = t => { if (vis) draw(t); requestAnimationFrame(loop); };
    const yAt = ev => { const r = cv.getBoundingClientRect(); return (ev.clientY - r.top) * H / r.height; };
    const onTarget = y => { const r = cv.getBoundingClientRect(); return Math.abs(y - (r.top + Y(target) * r.height / H)) < 22; };   // within 22 CSS px of the line
    cv.addEventListener('touchstart', ev => { if (ev.touches.length === 1 && onTarget(ev.touches[0].clientY)) ev.preventDefault(); }, { passive: false });
    cv.addEventListener('pointerdown', ev => { if (onTarget(ev.clientY)) { drag = true; cv.setPointerCapture(ev.pointerId); } });
    const xAt = ev => { const r = cv.getBoundingClientRect(); return (ev.clientX - r.left) * W / r.width; };
    const tAt = x => Math.max(0, Math.min(ctl[ctl.length - 1][0], (x - pad.l) / (W - pad.l - pad.r) * T1));
    cv.addEventListener('pointerleave', () => { if (scrub != null) { t0 = performance.now() - scrub / 2.8 * 1000; scrub = null; } });
    cv.addEventListener('pointermove', ev => { const nearT = onTarget(ev.clientY); cv.style.cursor = nearT ? 'ns-resize' : 'ew-resize';
      if (!drag && !nearT) { scrub = tAt(xAt(ev)); if (RM) draw(0); }
      if (drag) { target = Math.max(2400, Math.min(3080, Yi(yAt(ev)))); document.getElementById('ab-t').value = target; reset(); if (RM) draw(0); } });
    for (const e of ['pointerup', 'pointercancel', 'lostpointercapture']) cv.addEventListener(e, () => { drag = false; });
    // Keyboard: Left/Right scrub the flight (Shift for 2 s), Home/End jump, Up/Down move the target, Escape resumes.
    cv.tabIndex = 0; cv.setAttribute('role', 'slider'); cv.setAttribute('aria-valuemin', 0); cv.setAttribute('aria-valuemax', ctl[ctl.length - 1][0].toFixed(1));
    cv.setAttribute('aria-label', 'Airbrake flight replay. Left and right arrows scrub through the flight, up and down move the target apogee.');
    const resume = () => { if (scrub != null) { t0 = performance.now() - scrub / 2.8 * 1000; scrub = null; cv.removeAttribute('aria-valuetext'); } };
    cv.addEventListener('keydown', ev => {
      const end = ctl[ctl.length - 1][0], st = ev.shiftKey ? 2 : .5, cur = scrub ?? 0; let s2 = null;
      if (ev.key === 'ArrowRight') s2 = cur + st; else if (ev.key === 'ArrowLeft') s2 = cur - st;
      else if (ev.key === 'Home') s2 = 0; else if (ev.key === 'End') s2 = end;
      else if (ev.key === 'ArrowUp' || ev.key === 'ArrowDown') { target = Math.max(2400, Math.min(3080, target + (ev.key === 'ArrowUp' ? 20 : -20))); document.getElementById('ab-t').value = target; reset(); }
      else if (ev.key === 'Escape') resume(); else return;
      ev.preventDefault();
      if (s2 != null) scrub = Math.max(0, Math.min(end, s2));
      if (scrub != null) { const r = ctl[Math.max(0, Math.min(ctl.length - 1, Math.round(scrub / .02)))];
        cv.setAttribute('aria-valuenow', scrub.toFixed(1)); cv.setAttribute('aria-valuetext', `T+${scrub.toFixed(1)} s, ${Math.round(r[1])} m, flaps ${Math.round(r[2] * 80)} degrees`); }
      if (RM) draw(0); });
    cv.addEventListener('blur', resume);
    document.getElementById('ab-t').addEventListener('input', e2 => { target = +e2.target.value; reset(); if (RM) draw(0); });
    RM ? draw(0) : requestAnimationFrame(loop);
  })();

  /* ---------- OSIRIS V0 logic analyser: real buses from the V0 netlist, wire colours from the wiring standard ---------- */
  (function analyser() {
    const cv = document.getElementById('la'); if (!cv) return;
    const ctx = cv.getContext('2d'), board = document.getElementById('la-board'), cap = document.getElementById('la-cap');
    const WIRE = { BN: '#8B5A2B', WH: '#F5F4F0', VT: '#8E5BD6', OG: '#FF7A1A', YE: '#FFC908', BU: '#3B82F6', RD: '#E0282E', BK: '#5D626B' };
    const G = [
      { id: 'spi1', name: 'SPI1 · IMU (ISM330IS)', part: 1, ch: [['CS', 'BN'], ['SCK', 'WH'], ['MOSI', 'VT'], ['MISO', 'OG']] },
      { id: 'i2c1', name: 'I²C1 · barometer + power monitor (BMP581, INA228)', part: [2, 3], ch: [['SCL', 'YE'], ['SDA', 'BU']] },
      { id: 'spi2', name: 'SPI2 · microSD', part: 7, ch: [['CS', 'BN'], ['SCK', 'WH'], ['MOSI', 'VT'], ['MISO', 'OG']] },
      { id: 'uart', name: 'UART1 · JST-PH port', part: null, ch: [['TX', 'OG'], ['RX', 'YE']] },
      { id: 'pwr', name: 'Power · XT30 → INA228 shunt → arming key → buck', part: [5, 4], ch: [['VBATT', 'RD'], ['3V3', 'RDYE'], ['GND', 'BK']] },
    ];
    // transactions on a repeating 2.4 s schedule (illustrative timing; the buses and parts are the real V0 netlist)
    const PERIOD = 2.4, TX = [];
    for (let k = 0; k < 8; k++) TX.push({ g: 'spi1', t: k * .3 + .02, d: .07, label: 'read accel + gyro', part: 1 });
    for (let k = 0; k < 4; k++) TX.push({ g: 'i2c1', t: k * .6 + .12, d: .11, label: k % 2 ? 'read bus voltage · INA228' : 'read pressure · BMP581', part: k % 2 ? 3 : 2 });
    TX.push({ g: 'spi2', t: .9, d: .34, label: 'write log block', part: 7 }); TX.push({ g: 'spi2', t: 2.05, d: .2, label: 'write log block', part: 7 });
    TX.push({ g: 'uart', t: .45, d: .22, label: 'telemetry frame out', part: null }); TX.push({ g: 'uart', t: 1.65, d: .12, label: 'command in', part: null, rx: true });
    const bit = (n, i) => ((n * 2654435761 + i * 40503) >>> 7) & 1;
    function level(gid, ch, t) {   // 1 high, 0 low
      if (gid === 'pwr') return 1;
      const tm = ((t % PERIOD) + PERIOD) % PERIOD, tx = TX.find(x => x.g === gid && tm >= x.t && tm < x.t + x.d);
      const idle = { CS: 1, SCK: 0, MOSI: 0, MISO: 0, SCL: 1, SDA: 1, TX: 1, RX: 1 }[ch];
      if (!tx) return idle; const f = (tm - tx.t) / tx.d, n = Math.floor(tx.t * 1000);
      if (gid === 'uart') { if ((ch === 'RX') !== !!tx.rx) return 1; const b = Math.floor(f * 40); return b % 10 === 0 ? 0 : b % 10 === 9 ? 1 : bit(n, b); }
      if (gid === 'i2c1') { const nb = 27, q = f * nb, b = Math.floor(q), ph = q - b;
        if (ch === 'SCL') return f < .03 || f > .97 ? 1 : ph < .5 ? 0 : 1;
        if (f < .03) return f < .015 ? 1 : 0; if (f > .97) return f > .985 ? 1 : 0; return (b % 9 === 8) ? 0 : bit(n, b); }
      if (ch === 'CS') return f < .04 || f > .96 ? 1 : 0;
      const clocks = gid === 'spi2' ? 64 : 24, q = (f - .06) / .88 * clocks; if (q < 0 || q > clocks) return 0;
      if (ch === 'SCK') return (q - Math.floor(q)) < .5 ? 0 : 1;
      return bit(n + (ch === 'MISO' ? 7 : 0), Math.floor(q));
    }
    const rowsH = 26, gap = 30, lab = 150; let focus = null, t0 = performance.now();
    const layout = []; let y = 14; G.forEach(gr => { layout.push({ gr, y }); y += 22 + gr.ch.length * rowsH + gap - 20; });
    const Htot = y + 8; cv.height = Htot * 2; cv.style.aspectRatio = `${cv.width} / ${cv.height}`;
    function draw(now) {
      const W = cv.width / 2, span = 1.2, tn = RM ? 1.0 : (now - t0) / 1000 * .55; ctx.setTransform(2, 0, 0, 2, 0, 0);
      ctx.fillStyle = '#15171B'; ctx.fillRect(0, 0, W, Htot);
      const active = new Set();
      layout.forEach(({ gr, y }) => {
        const dim = focus && focus !== gr.id; ctx.globalAlpha = dim ? .25 : 1;
        ctx.fillStyle = '#9aa0a8'; ctx.font = '600 11px "Chivo Mono", monospace'; ctx.textAlign = 'left'; ctx.fillText(gr.name.toUpperCase(), 10, y + 10);
        // decoder bubble for the transaction under the cursor (right edge)
        const tm = ((tn % PERIOD) + PERIOD) % PERIOD, tx = TX.find(x => x.g === gr.id && tm >= x.t && tm < x.t + x.d + .25);
        if (tx) { ctx.font = '600 11px "Chivo Mono", monospace'; const w = ctx.measureText(tx.label).width + 14; ctx.fillStyle = '#3E9B5F'; ctx.fillRect(W - w - 10, y, w, 16); ctx.fillStyle = '#fff'; ctx.fillText(tx.label, W - w - 3, y + 12);
          if (tm < tx.t + tx.d) (Array.isArray(tx.part) ? tx.part : [tx.part]).forEach(p => p && active.add(p)); if (gr.id === 'spi1' || gr.id === 'i2c1' || gr.id === 'spi2') active.add(6); }
        gr.ch.forEach(([name, code], i) => {
          const yy = y + 22 + i * rowsH, hi = yy + 3, lo = yy + rowsH - 7;
          ctx.fillStyle = '#d9dce1'; ctx.font = '500 11px "Chivo Mono", monospace'; ctx.fillText(name, 22, lo);
          // wire swatch, striped for RDYE
          const sw = code === 'RDYE' ? ['#E0282E', '#FFC908'] : [WIRE[code]];
          ctx.fillStyle = sw[0]; ctx.fillRect(84, hi + 4, 40, 8); if (sw[1]) { ctx.fillStyle = sw[1]; for (let s = 0; s < 40; s += 10) ctx.fillRect(84 + s, hi + 4, 4, 8); }
          ctx.fillStyle = '#9aa0a8'; ctx.fillText(code, 128, lo);
          ctx.strokeStyle = sw[0]; ctx.lineWidth = 2; ctx.beginPath(); let prev = null;
          for (let x = lab; x <= W - 10; x += 1) { const t = tn - span + (x - lab) / (W - 10 - lab) * span; const v = level(gr.id, name, t), yv = v ? hi : lo;
            if (prev === null) ctx.moveTo(x, yv); else if (v !== prev) { ctx.lineTo(x, prev ? hi : lo); ctx.lineTo(x, yv); } else ctx.lineTo(x, yv); prev = v; }
          ctx.stroke();
          if (code === 'RDYE') { ctx.strokeStyle = '#FFC908'; ctx.setLineDash([6, 10]); ctx.beginPath(); ctx.moveTo(lab, hi); ctx.lineTo(W - 10, hi); ctx.stroke(); ctx.setLineDash([]); }
          if (code === 'BK') { ctx.strokeStyle = '#5D626B'; ctx.beginPath(); ctx.moveTo(lab, lo); ctx.lineTo(W - 10, lo); ctx.stroke(); }
        });
        ctx.globalAlpha = 1;
      });
      ctx.strokeStyle = 'rgba(255,201,8,.5)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(W - 10, 0); ctx.lineTo(W - 10, Htot); ctx.stroke();
      board.querySelectorAll('.pm').forEach(b => b.classList.toggle('act', active.has(+b.dataset.n) || +b.dataset.n === 5 || +b.dataset.n === 4));
    }
    DATA.parts.forEach(p => { const b = document.createElement('button'); b.type = 'button'; b.className = 'pm' + (p.under ? ' under' : ''); b.textContent = p.n; b.dataset.n = p.n;
      b.style.left = p.x + '%'; b.style.top = (p.y / 104.3 * 100) + '%'; b.setAttribute('aria-label', `${p.n}. ${p.name}: ${p.detail}`); board.appendChild(b);
      const gr = G.find(g2 => g2.part === p.n || (Array.isArray(g2.part) && g2.part.includes(p.n)));
      const on = () => { focus = gr ? gr.id : null; cap.innerHTML = `<b>${p.n} · ${p.name}</b> ${p.detail}${gr ? ` · on <b>${gr.name.split(' · ')[0]}</b>` : ''}`; if (RM) draw(0); };
      b.addEventListener('mouseenter', on); b.addEventListener('focus', on); b.addEventListener('click', on); b.addEventListener('mouseleave', () => { focus = null; if (RM) draw(0); }); });
    let vis = false; new IntersectionObserver(es => { vis = es[0].isIntersecting; }).observe(cv);
    const loop = t => { if (vis) draw(t); requestAnimationFrame(loop); };
    RM ? draw(0) : requestAnimationFrame(loop);
  })();
