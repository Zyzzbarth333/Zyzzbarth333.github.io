// Drag the launch: pick a launch date and a flight time; the orrery's own Lambert solver redraws the transfer live.
// Uses the site's orrery modules (porkchop.js, orbital.js) and the vendored astronomy-engine, unchanged.
import * as A from "/assets/vendor/astronomy-engine-2.1.19/astronomy.min.js";
import { porkchopGrid, transferBetween, range } from "/assets/figures/orrery/porkchop.js";
import { propagate } from "/assets/figures/orrery/orbital.js";

const sol = document.getElementById("sol"); if (sol) {
const sx = sol.getContext("2d"), SW = sol.width, SH = sol.height;
const mini = document.getElementById("mini"), mx = mini.getContext("2d"), MW = mini.width, MH = mini.height;
const $ = (id) => document.getElementById(id), dep = $("sp-dep"), tof = $("sp-tof"), depL = $("sp-dep-l"), tofL = $("sp-tof-l"), dvL = $("sp-dv"), bar = $("sp-bar"), msg = $("sp-msg"), go = $("sp-go");
const RM = matchMedia("(prefers-reduced-motion: reduce)").matches;
const MU_SUN = 132712440018, MU_EARTH = 398600.4418, AU = 149597870.7, AUD = AU / 86400, DAY = 86400;
// start is a calendar date, month 1 to 12 (Date.UTC counts months from 0, hence the - 1 where it is read)
const DEST = { mars: { mu: 42828.39, rPeri: 3639.5000619343314, name: "Mars", year: 687.0, start: [2026, 6, 1], span: 240, step: 2, tof: [100, 450, 2], col: "#FF5102" },
               venus: { mu: 324858.6, rPeri: 6551.797441824649, name: "Venus", year: 224.7, start: [2026, 2, 1], span: 360, step: 3, tof: [70, 250, 2], col: "#E0B44A" } };
const R = A.Rotation_EQJ_ECL(), BODY = { venus: A.Body.Venus, earth: A.Body.Earth, mars: A.Body.Mars };
const stateOf = (k, d) => { const s = A.RotateState(R, A.HelioState(BODY[k], d)); return { r: [s.x * AU, s.y * AU, s.z * AU], v: [s.vx * AUD, s.vy * AUD, s.vz * AUD] }; };
const capture = (vinf, b) => Math.sqrt(vinf * vinf + 2 * b.mu / b.rPeri) - Math.sqrt(2 * b.mu / b.rPeri);
const fmt = (d) => d.toLocaleDateString("en-AU", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
let key = "mars", B, t0, depDays, tofDays, G, DV, best, rings, S, cur = null, flying = null, miniImg = null;

const P = (r) => [SW / 2 + r[0] * S, SH / 2 - r[1] * S];
const solve = (iDep, dTof) => { const d = new Date(t0 + depDays[iDep] * DAY * 1000), a = new Date(d.getTime() + dTof * DAY * 1000);
  const s1 = stateOf("earth", d), s2 = stateOf(key, a), t = transferBetween(s1, s2, dTof * DAY, MU_SUN, { mu: MU_EARTH, rPark: 6571 }, { mu: B.mu, rPark: B.rPeri, capture: false });
  return { d, a, s1, s2, t, dv: t ? t.dvDep + capture(t.vinfArr, B) : NaN, tof: dTof }; };
const ramp = (dv) => { const f = Math.max(0, Math.min(1, (dv - best.dv) / 5)); const c = [[62, 155, 95], [255, 201, 8], [255, 81, 2], [187, 7, 0]], k = Math.min(2, Math.floor(f * 3)), u = f * 3 - k;
  return `rgb(${c[k].map((v, n) => Math.round(v + (c[k + 1][n] - v) * u))})`; };

function setup() {
  B = DEST[key]; t0 = Date.UTC(B.start[0], B.start[1] - 1, B.start[2]); depDays = range(0, B.span, B.step); tofDays = range(B.tof[0], B.tof[1], B.tof[2]);
  dep.max = depDays.length - 1; tof.min = B.tof[0]; tof.max = B.tof[1]; tof.step = B.tof[2];
  msg.textContent = `Working out ${(depDays.length * tofDays.length).toLocaleString("en-AU")} transfers to ${B.name} with the orrery's solver...`;
  setTimeout(() => {
    G = porkchopGrid({ stateOf, departure: { key: "earth", mu: MU_EARTH, rPark: 6571 }, arrival: { key, mu: B.mu, rPark: B.rPeri, capture: false }, muSun: MU_SUN, depStart: new Date(t0), depDays, tofDays });
    DV = new Float64Array(G.dvDep.length); let bi = -1;
    for (let n = 0; n < DV.length; n++) { DV[n] = G.dvDep[n] + capture(G.vinfArr[n], B); if (Number.isFinite(DV[n]) && (bi < 0 || DV[n] < DV[bi])) bi = n; }
    best = { i: bi % G.nDep, j: Math.floor(bi / G.nDep), dv: DV[bi] };
    const ring = (k, days) => Array.from({ length: 121 }, (_, n) => stateOf(k, new Date(t0 + n / 120 * days * DAY * 1000)).r);
    rings = [ring("earth", 365.26), ring(key, B.year)]; S = (Math.min(SW, SH) / 2 - 30) / (Math.max(...rings.flat().map((r) => Math.hypot(r[0], r[1]))) * 1.02);
    // porkchop minimap, drawn once
    miniImg = mx.createImageData(MW, MH);
    for (let y = 0; y < MH; y++) for (let x = 0; x < MW; x++) { const i = Math.floor(x / MW * G.nDep), j = Math.floor((MH - 1 - y) / MH * G.nTof), v = DV[j * G.nDep + i], o = (y * MW + x) * 4;
      if (!Number.isFinite(v)) { miniImg.data.set([20, 18, 40, 255], o); continue; } const c = ramp(v).match(/\d+/g).map(Number); const dim = v > best.dv + 6 ? .35 : 1;
      miniImg.data.set([c[0] * dim, c[1] * dim, c[2] * dim, 255], o); }
    dep.value = Math.round(depDays.length * .25); tof.value = B.tof[0] + Math.round((B.tof[1] - B.tof[0]) * .55 / B.tof[2]) * B.tof[2];
    msg.innerHTML = `Drag the launch date and the flight time. The arc is a real Lambert solve; green is cheap. Then press <b>Launch</b>.`;
    go.disabled = false; update();
  }, 30);
}
function update() {
  if (!G || flying) return; cur = solve(+dep.value, +tof.value);
  depL.textContent = fmt(cur.d); tofL.textContent = `${cur.tof} days, arriving ${fmt(cur.a)}`;
  dvL.textContent = Number.isFinite(cur.dv) ? cur.dv.toFixed(2) : "no solution"; const f = Number.isFinite(cur.dv) ? Math.max(.03, Math.min(1, (cur.dv - best.dv + .3) / 8)) : 1;
  bar.style.width = (f * 100) + "%"; bar.style.background = Number.isFinite(cur.dv) ? ramp(cur.dv) : "#555";
  drawSol(cur, 0); drawMini();
}
function drawSol(c, k) {
  sx.clearRect(0, 0, SW, SH);
  for (let i = 0; i < 160; i++) { const a = (i * 137.5) % 360, r = ((i * 7919) % 1000) / 1000; sx.fillStyle = `rgba(255,255,255,${.15 + (i % 5) * .08})`; sx.fillRect(SW / 2 + Math.cos(a) * r * SW * .7, SH / 2 + Math.sin(a) * r * SH * .7, 1.5, 1.5); }
  sx.strokeStyle = "rgba(255,255,255,.2)"; sx.lineWidth = 2; rings.forEach((rg) => { sx.beginPath(); rg.forEach((r, n) => { const [x, y] = P(r); n ? sx.lineTo(x, y) : sx.moveTo(x, y); }); sx.closePath(); sx.stroke(); });
  sx.fillStyle = "#FFC908"; sx.beginPath(); sx.arc(SW / 2, SH / 2, 16, 0, 7); sx.fill();
  if (c.t) { const arc = Array.from({ length: 101 }, (_, n) => n ? propagate(c.s1.r, c.t.v1, c.tof * DAY * n / 100, MU_SUN).r : c.s1.r);
    sx.strokeStyle = ramp(c.dv); sx.lineWidth = 4; sx.setLineDash(k ? [] : [12, 10]); sx.beginPath(); arc.forEach((r, n) => { if (k && n / 100 > k) return; const [x, y] = P(r); n ? sx.lineTo(x, y) : sx.moveTo(x, y); }); sx.stroke(); sx.setLineDash([]);
    if (k) { const [x, y] = P(arc[Math.round(k * 100)]); sx.fillStyle = "#fff"; sx.beginPath(); sx.arc(x, y, 8, 0, 7); sx.fill(); } }
  const tNow = new Date(c.d.getTime() + k * c.tof * DAY * 1000), e = P(stateOf("earth", tNow).r), m = P(stateOf(key, tNow).r), ma = P(c.s2.r);
  if (!k) { sx.strokeStyle = B.col; sx.lineWidth = 2; sx.setLineDash([4, 6]); sx.beginPath(); sx.arc(ma[0], ma[1], 16, 0, 7); sx.stroke(); sx.setLineDash([]); }
  sx.fillStyle = "#3B82F6"; sx.beginPath(); sx.arc(e[0], e[1], 11, 0, 7); sx.fill(); sx.fillStyle = B.col; sx.beginPath(); sx.arc(m[0], m[1], 10, 0, 7); sx.fill();
  sx.font = "600 22px 'Chivo Mono', monospace"; sx.fillStyle = "#E6E1F5"; sx.fillText("Earth", e[0] + 16, e[1] - 12); sx.fillText(B.name, m[0] + 16, m[1] - 12);
  if (!k) { sx.fillStyle = "#9aa0a8"; sx.fillText(B.name + " on arrival", ma[0] + 22, ma[1] + 28); }
  sx.fillStyle = "#9aa0a8"; sx.fillText(fmt(tNow), 22, SH - 24);
}
function drawMini() {
  if (!miniImg) return; mx.putImageData(miniImg, 0, 0);
  const bx = (best.i + .5) / G.nDep * MW, by = MH - (best.j + .5) / G.nTof * MH, cx = (+dep.value + .5) / G.nDep * MW, cy = MH - ((+tof.value - B.tof[0]) / B.tof[2] + .5) / G.nTof * MH;
  mx.strokeStyle = "#fff"; mx.lineWidth = 1.5; mx.beginPath(); mx.moveTo(cx, 0); mx.lineTo(cx, MH); mx.moveTo(0, cy); mx.lineTo(MW, cy); mx.stroke();
  mx.beginPath(); mx.arc(cx, cy, 6, 0, 7); mx.stroke();
  if (flying === false) { mx.strokeStyle = "#3E9B5F"; mx.lineWidth = 3; mx.beginPath(); mx.arc(bx, by, 8, 0, 7); mx.stroke(); }
}
function launch(useBest) {
  if (!G || flying) return; if (useBest) { dep.value = best.i; tof.value = tofDays[best.j]; update(); }
  const c = cur; if (!c.t) { msg.textContent = "No transfer joins those two dates. Move a slider and try again."; return; }
  flying = true; go.disabled = true; const s0 = performance.now(), dur = RM ? 1 : 4200;
  const tick = (now) => { const k = Math.min(1, (now - s0) / dur); drawSol(c, Math.max(.001, k)); if (k < 1) requestAnimationFrame(tick); else land(c); };
  requestAnimationFrame(tick);
}
function land(c) {
  const diff = c.dv - best.dv, g = diff < .1 ? "Mission grade: right on the optimum." : diff < .4 ? "Close. A small trim burn covers it." : diff < 1.2 ? "It flies, but it costs a lot of fuel." : "The rocket equation says no.";
  msg.innerHTML = `Arrived at ${B.name} on ${fmt(c.a)} for <b>${c.dv.toFixed(2)} km/s</b>. The best in the window is <b>${best.dv.toFixed(2)} km/s</b>, leaving ${fmt(new Date(t0 + depDays[best.i] * DAY * 1000))} on a ${tofDays[best.j]}-day flight (ringed on the map). ${g}`;
  flying = false; drawMini(); flying = null; go.disabled = false;
  setTimeout(() => { if (!flying) drawSol(c, 0); }, 2500);
}
dep.addEventListener("input", update); tof.addEventListener("input", update);
go.addEventListener("click", () => launch(false)); $("sp-best").addEventListener("click", () => launch(true));
$("sp-dest").addEventListener("click", (e) => { if (flying) return; key = key === "mars" ? "venus" : "mars"; e.target.textContent = key === "mars" ? "Go to Venus instead" : "Go to Mars instead"; G = null; go.disabled = true; setup(); });
let dragging = false; const pick = (ev) => { const r = mini.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width, y = 1 - (ev.clientY - r.top) / r.height;
  dep.value = Math.round(x * (G.nDep - 1)); tof.value = B.tof[0] + Math.round(y * (G.nTof - 1)) * B.tof[2]; update(); };
mini.addEventListener("pointerdown", (ev) => { if (!G) return; dragging = true; mini.setPointerCapture(ev.pointerId); pick(ev); });
mini.addEventListener("pointermove", (ev) => { if (dragging) pick(ev); }); mini.addEventListener("pointerup", () => { dragging = false; });
let started = false; new IntersectionObserver((es) => { if (es[0].isIntersecting && !started) { started = true; setup(); } }, { rootMargin: "300px" }).observe(sol);
}
