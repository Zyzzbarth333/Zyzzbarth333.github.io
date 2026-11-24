// Card icons for the portfolio home page, drawn with the Anatomy kit (MIT).
// Each icon is a small isometric model whose parts carry class names the site's CSS animates on hover.
// Build: node build.mjs <out-dir>   (writes <name>-icon.svg files without embedded styles)
import { writeFileSync, mkdirSync, readFileSync, existsSync } from "node:fs";
const render = (n) => (existsSync(`models/${n}-render.json`) ? JSON.parse(readFileSync(`models/${n}-render.json`, "utf8")) : null);
import { join } from "node:path";
import { homedir } from "node:os";
// The Anatomy kit's folder comes from $ANATOMY_KIT or the private paths file (~/.config/portfolio-build/paths.json).
const KIT = process.env.ANATOMY_KIT ?? JSON.parse(readFileSync(join(process.env.PORTFOLIO_PRIVATE ?? join(homedir(), ".config/portfolio-build"), "paths.json"), "utf8")).anatomy.replace(/^~/, homedir());
const k = await import(join(KIT, "kit/iso-kit.mjs"));
const G = await import(join(KIT, "kit/lathe.mjs"));

const OUT = process.argv[2] || "out";
mkdirSync(OUT, { recursive: true });
const SIZE = 300;

function make(name, points, azimuth, draw, { pad = 34, elevation = 30, fixed = null } = {}) {
  // a mesh-rendered icon passes its render's projection so vector overlays line up with the raster layers
  const P = fixed || k.fitProjection(points, SIZE, SIZE, { pad, azimuth, elevation });
  const T = {
    P,
    at: (p) => k.iso(p, P),
    S: (paths, style) => k.solidSvg(paths, style),
    L: (d, style) => k.lineSvg(d, style),
    D: (pts, style) => k.dotsSvg(pts, style),
    slab: (plan, z, h, steps = 4, bevel = 0.4) => k.slabOf({ r: 0.8, ...plan }, z, h, P, steps, bevel),
    cyl: (x, y, r, z, h, steps = 28) => k.cylinder(x, y, r, z, h, P, steps),
    halo: (plan, z = 0) => `<path class="iso-halo" d="${k.haloOf(plan, z, 2, P)}"/>`,
    along: (v) => k.axisVector(P, v),
    depth: (p) => k.depthOf(p, P),
  };
  const body = draw(T);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" class="iso-svg" viewBox="0 0 ${SIZE} ${SIZE}" aria-hidden="true" focusable="false"><rect class="ic-bg" width="${SIZE}" height="${SIZE}"/>${body}</svg>`;
  writeFileSync(`${OUT}/${name}-icon.svg`, svg);
  return { name, P };
}
const sortBy = (T, list, key) => [...list].sort((a, b) => T.depth(key(a)) - T.depth(key(b)));
const vec = (T, v) => T.along(v).map((n) => Math.round(n * 100) / 100);
const notes = {};

// ---------- 1. Theseus V: the team's rover, rendered from its CAD meshes ----------
// Icon-sized meshes of the rover's main groups (exported read-only from Fusion, 12 Nov 2026) are drawn by
// mesh_render.py as flat-shaded layers in this icon's camera. Icon frame: x = (X - 50) * 0.07, y = Y * 0.07,
// z = (Z + 216) * 0.07. The LiDAR's scan rings are vector and pulse on hover. A stylised icon, not the team's CAD.
const R_THESEUS = render("theseus");
make("theseus", [[-46, -32, 0], [46, 32, 0], [-46, -32, 66], [46, 32, 66]], 38, (T) => {
  const out = [T.halo({ x: -42, y: -30, w: 84, d: 60, r: 10 })];
  const lid = [(-37 - 50) * 0.07, -26.4 * 0.07, (386 + 216) * 0.07];   // MID-360 top centre, from its mesh
  // autonomy on the ground: a LiDAR scan that builds a map of the real ARCh 2026 arena around the start pose
  // (craters, rocks and the e-stop wall from theseus-gcs/arena_config.yaml), then a planned path; site.js drives it
  const MPU = 7.2;                                                     // icon units per metre on the ground map
  const g0 = [lid[0], lid[1], 0], O = T.at(g0);
  const ex = T.along([MPU, 0, 0]), ey = T.along([0, MPU, 0]);
  const returns = JSON.parse(readFileSync("models/theseus-returns.json", "utf8"));
  const rpts = returns.map(([x, y, kind]) => { const q = T.at([g0[0] + x * MPU, g0[1] + y * MPU, 0]); return `<circle class="rv-ret rv-ret-${kind}" cx="${q[0].toFixed(1)}" cy="${q[1].toFixed(1)}" r="${kind === "wall" ? 1.1 : 1.3}" data-a="${Math.atan2(y, x).toFixed(3)}"/>`; }).join("");
  const goal = [3.6, 1.6];                                            // a frontier ahead and to the left, between the craters
  const path = [[0.3, 0], [1.2, 0.05], [2.2, 0.45], [3.0, 1.0], goal].map(([x, y]) => T.at([g0[0] + x * MPU, g0[1] + y * MPU, 0]));
  const pd = "M" + path.map((q) => q.map((v) => v.toFixed(1)).join(" ")).join(" L");
  const gq = path[path.length - 1];
  out.push(`<g class="rv-map" data-o="${O.map((v) => v.toFixed(2)).join(" ")}" data-ex="${ex.map((v) => v.toFixed(3)).join(" ")}" data-ey="${ey.map((v) => v.toFixed(3)).join(" ")}" data-r="6">` +
    `${rpts}<path class="rv-path" d="${pd}"/><g class="rv-goal" transform="translate(${gq[0].toFixed(1)} ${gq[1].toFixed(1)})"><ellipse rx="3.4" ry="2" /><path d="M0 -9 V0 M0 -9 L5 -7 L0 -5"/></g></g>`);
  const fwd = T.along([MPU, 0, 0]);
  const drive = [`<image href="assets/img/projects/theseus-body.webp" x="0" y="0" width="300" height="300"/>`];
  out.push(`<g class="rv-drive" data-fwd="${fwd.map((v) => v.toFixed(3)).join(" ")}" data-lid="${T.at(lid).map((v) => v.toFixed(2)).join(" ")}">${drive.join("")}</g>`);
  out.push(`<path class="rv-beam" d=""/>`);                                    // drawn over the rover: it leaves the LiDAR head
  notes.theseus = { drive: vec(T, [10, 0, 0]) };
  return out.join("");
}, { fixed: R_THESEUS && R_THESEUS.P });

// ---------- 2. HAVOC-2 and COSMOS: rocket on a rail stand ----------
// site.js flies the rocket with a flight model shaped like HAVOC-2's first flight; data-up is one world unit of climb.
make("havoc2", [[-40, -40, 0], [40, 40, 0], [0, 0, 175]], 40, (T) => {
  const out = [T.halo({ x: -38, y: -38, w: 76, d: 76, r: 8 })];
  out.push(T.S(T.slab({ x: -34, y: -34, w: 68, d: 68, r: 4 }, 0, 6, 6, 0.8), { tone: "mid" }));
  out.push(T.L(k.planOutline({ x: -29, y: -29, w: 58, d: 58, r: 2 }, 6, T.P), { tone: "faint" }));
  out.push(T.D(k.corners({ x: -34, y: -34, w: 68, d: 68 }, 5).map(([x, y]) => T.at([x, y, 6])), { size: 0.9 }));
  out.push(T.S(T.slab({ x: -20, y: -3, w: 6, d: 6, r: 0.6 }, 6, 150, 2, 0.3), { tone: "lo" }));                     // launch rail
  out.push(T.S(T.slab({ x: -26, y: -8, w: 18, d: 16, r: 2 }, 6, 10, 3, 0.4), { tone: "mid" }));                       // rail foot
  const F = G.frameAlong([0, 0, 18], [0, 0, 1]);
  const fins = [0, 90, 180, 270].map((deg) => deg * Math.PI / 180);
  const finSvg = (a) => {
    const c = Math.round(Math.cos(a)), sn = Math.round(Math.sin(a));
    const plan = c !== 0 ? { x: c > 0 ? 8 : -22, y: -0.7, w: 14, d: 1.4, r: 0.3 } : { x: -0.7, y: sn > 0 ? 8 : -22, w: 1.4, d: 14, r: 0.3 };
    return T.S(T.slab(plan, 18, 20, 2, 0.2), { tone: "mid" });
  };
  const back = fins.filter((a) => T.depth([Math.cos(a) * 10, Math.sin(a) * 10, 30]) < T.depth([0, 0, 30]));
  const front = fins.filter((a) => !back.includes(a));
  const rocket = [];
  rocket.push(`<path class="rk-flame" d="M${T.at([0, 0, 18])[0] - 6} ${T.at([0, 0, 18])[1]} Q${T.at([0, 0, 18])[0]} ${T.at([0, 0, 18])[1] + 34} ${T.at([0, 0, 18])[0] + 6} ${T.at([0, 0, 18])[1]} Z"/>`);
  back.forEach((a) => rocket.push(finSvg(a)));
  rocket.push(T.S(G.lathe([[0, 6], [0, 9], [96, 9], [96, 9.4], [100, 9.4], [100, 9], [118, 8.6, 1], [134, 5, 1], [146, 0, 1]], F, T.P), { tone: "hi", lit: true }));
  rocket.push(T.L(k.sideArc(0, 0, 9, 18 + 40, T.P, 32) + k.sideArc(0, 0, 9, 18 + 70, T.P, 32), { tone: "faint" }));
  front.forEach((a) => rocket.push(finSvg(a)));
  out.push(`<g class="rk-lift" data-up="${T.along([0, 0, 1]).map((n) => n.toFixed(4)).join(" ")}">${rocket.join("")}</g>`);
  notes.havoc2 = { lift: vec(T, [0, 0, 20]) };
  return out.join("");
});

// ---------- 3. OSIRIS: the real V0 board with the Black Pill plugged in ----------
// The board and its parts come from the KiCad layout (kicad-cli GLB, glb_split.py); the sockets and the
// WeAct/DFRobot Black Pill (STM32F411, V3.0) are modelled from the footprints and the datasheet (osiris_parts.py).
// site.js lifts the module out of its sockets on a spring while hovered, drops it back with a bounce, and once
// it is seated plays the board's power-up on its seven status LEDs (positions and colours from the layout).
const R_OSIRIS = render("osiris");
make("osiris", [[-48, -54, 0], [48, 54, 0], [-48, -54, 30], [48, 54, 30]], 36, (T) => {
  const out = [T.halo({ x: -32, y: -37, w: 64, d: 74, r: 4 })];
  const img = (layer) => `<image href="assets/img/projects/osiris-${layer}.webp" x="0" y="0" width="300" height="300"/>`;
  out.push(img("body"));
  const kp = R_OSIRIS ? R_OSIRIS.keypoints : {};
  const leds = [["led_3v3", "green"], ["led_pwr", "green"], ["led_log", "amber"], ["led_radio", "amber"], ["led_hb", "blue"], ["led_arm", "red"], ["led_flt", "red"]];
  out.push(`<g class="os-leds">${leds.filter(([k]) => kp[k]).map(([k, c]) => `<circle class="os-led os-led-${c}" data-led="${k.slice(4)}" cx="${kp[k][0]}" cy="${kp[k][1]}" r="2.6"/>`).join("")}</g>`);
  const lift = T.along([0, 0, 18]).map((v) => +v.toFixed(2));
  out.push(`<g class="os-module" data-lift="${lift.join(" ")}">${img("module")}</g>`);
  return out.join("");
}, { fixed: R_OSIRIS && R_OSIRIS.P });

// ---------- 4. Digital orrery: a small mechanical orrery ----------
// site.js turns the gear train: Earth and Mars keep their real period ratio, spin up on hover and coast to a stop.
// Each planet is drawn twice, behind the mast and sun and in front of them; the back copy carries the ring's
// projected offsets (data-ring), which points are behind the mast (data-behind) and the planet's rate.
make("orrery", [[-46, -46, 0], [46, 46, 0], [0, 0, 70]], 40, (T) => {
  const out = [T.halo({ x: -40, y: -40, w: 80, d: 80, r: 40 })];
  out.push(T.S(T.cyl(0, 0, 40, 0, 6, 64), { tone: "mid" }));
  out.push(T.L(k.knurl(0, 0, 40, 0.8, 5.2, 72, T.P), { tone: "faint" }));
  out.push(T.L(k.ring(0, 0, 22, 6, T.P, 64) + k.ring(0, 0, 33, 6, T.P, 72), { tone: "lo" }));
  const ticks = k.radialTicks(0, 0, 37.5, 72, 6, 6, [1.2, 2.4], T.P);
  out.push(T.L(ticks.minor, { tone: "faint" }), T.L(ticks.major, { tone: "lo" }));
  const N = 72, centre = T.depth([0, 0, 6]);
  const planets = [[22, 4.6, "or-earth", 4], [33, 3.8, "or-mars", 7.5]].map(([R, r, cls, dur]) => {
    const ring = Array.from({ length: N + 1 }, (_, i) => { const a = (i / N) * 2 * Math.PI; return [R * Math.cos(a), R * Math.sin(a), 6]; });
    const s0 = T.at(ring[0]);
    const pts = ring.map((p) => { const q = T.at(p); return [q[0] - s0[0], q[1] - s0[1]]; });
    const behind = ring.slice(0, N).map((p) => T.depth(p) < centre);
    const body = T.S(T.cyl(R, 0, 0.9, 6, 16, 10), { tone: "mid" }) + T.S(G.sphereOf([R, 0, 6 + 16 + r], r, T.P), { tone: "hi" });
    const data = ` data-ring="${pts.slice(0, N).map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(" ")}" data-behind="${behind.map((b) => (b ? 1 : 0)).join("")}" data-rate="${(4 / dur).toFixed(4)}"`;
    const copy = (want) => `<g class="or-planet ${cls}" data-side="${want ? "back" : "front"}"${want ? data : ""} visibility="${behind[0] === want ? "visible" : "hidden"}">${body}</g>`;
    return { back: copy(true), front: copy(false) };
  });
  planets.forEach((p) => out.push(p.back));
  out.push(T.S(T.cyl(0, 0, 3, 6, 34, 20), { tone: "mid" }));
  out.push(`<g class="or-sun">${T.S(G.sphereOf([0, 0, 48], 10, T.P), { tone: "hi", lit: true })}</g>`);
  planets.forEach((p) => out.push(p.front));
  return out.join("");
});

// ---------- 5. Weather station: ballast base, mast, enclosure, anemometer and vane ----------
// The 3-cup rotor is turned by site.js (it spins up on hover and coasts down after), so it carries its
// screen-space axes: ex and ey are the projected 17-unit radius vectors, dep their depth weights.
make("weather-station", [[-34, -34, 0], [34, 34, 0], [0, 0, 150], [-50, 0, 142], [46, 0, 142]], 40, (T) => {
  const out = [T.halo({ x: -30, y: -30, w: 60, d: 60, r: 6 })];
  out.push(T.S(T.slab({ x: -28, y: -28, w: 56, d: 56, r: 4 }, 0, 8, 6, 0.8), { tone: "mid" }));
  out.push(T.D(k.corners({ x: -28, y: -28, w: 56, d: 56 }, 5).map(([x, y]) => T.at([x, y, 8])), { size: 0.9 }));
  out.push(T.S(T.cyl(0, 0, 2.6, 8, 52, 18), { tone: "mid" }));
  const box = { x: -14, y: 3, w: 28, d: 22, r: 2.5 };
  out.push(T.S(T.slab({ x: -3, y: 0, w: 6, d: 4, r: 0.6 }, 30, 14, 2), { tone: "lo" }));                    // clamp
  out.push(T.S(T.slab(box, 22, 30, 6, 0.6), { tone: "hi", crease: "lo" }));
  out.push(T.L(k.sideSeam(box, 46, T.P, 6), { tone: "lo" }));
  out.push(T.S(T.cyl(-6, 25.5, 2.2, 26, 0.1, 18), { tone: "lo" }));
  out.push(`<g class="ws-ant">${T.S(T.cyl(9, 14, 1.2, 52, 18, 12), { tone: "mid" })}${T.S(T.cyl(9, 14, 2.2, 70, 3, 14), { tone: "hi", lit: true })}</g>`);
  out.push(T.S(T.cyl(0, 0, 2.2, 60, 64, 18), { tone: "mid" }));
  const armZ = 124;
  out.push(T.S(T.slab({ x: -34, y: -1.2, w: 68, d: 2.4, r: 0.6 }, armZ, 2.4, 2), { tone: "lo" }));             // cross arm
  out.push(T.S(T.cyl(0, 0, 3.5, armZ + 2.4, 4, 18), { tone: "mid" }));                                         // mast cap
  // wind vane on the +x end: a static spindle, then the vane itself, which site.js turns about the spindle.
  // Its parts are given in vane coordinates (x points into the wind, z up) so the page can redraw them.
  out.push(T.S(T.cyl(30, 0, 1, armZ + 2.4, 7, 10), { tone: "mid" }));
  const vp = [30, 0, armZ + 9.4], VO = T.at(vp);
  const vx = T.along([1, 0, 0]), vy = T.along([0, 1, 0]), vz = T.along([0, 0, 1]);
  const vdep = [T.depth([1, 0, 0]) - T.depth([0, 0, 0]), T.depth([0, 1, 0]) - T.depth([0, 0, 0])];
  const geo = { shaft: [[-16, 0, 1], [12, 0, 1]], head: [[18, 0, 1], [10.5, 3.8, 1], [10.5, -3.8, 1]], fin: [[-20, 0, -0.8], [-8.5, 0, -0.8], [-8.5, 0, 8], [-20, 0, 5.6]] };
  const psi0 = 0.35;
  const vproj = ([x, y, z]) => { const c = Math.cos(psi0), s = Math.sin(psi0), X = x * c - y * s, Y = x * s + y * c; return [VO[0] + vx[0] * X + vy[0] * Y + vz[0] * z, VO[1] + vx[1] * X + vy[1] * Y + vz[1] * z].map((v) => v.toFixed(2)); };
  const poly = (pts) => "M" + pts.map((q) => vproj(q).join(" ")).join(" L") + " Z";
  const [s0, s1] = geo.shaft.map(vproj);
  const vaneSvg = `<path class="ws-fin" d="${poly(geo.fin)}"/><line class="ws-shaft" x1="${s0[0]}" y1="${s0[1]}" x2="${s1[0]}" y2="${s1[1]}"/><path class="ws-head" d="${poly(geo.head)}"/><circle class="ws-cap" cx="${VO[0].toFixed(2)}" cy="${VO[1].toFixed(2)}" r="1.6"/>`;
  const vaneData = `data-o="${VO.map((v) => v.toFixed(2)).join(" ")}" data-ex="${vx.map((v) => v.toFixed(4)).join(" ")}" data-ey="${vy.map((v) => v.toFixed(4)).join(" ")}" data-ez="${vz.map((v) => v.toFixed(4)).join(" ")}" data-dep="${vdep.map((v) => v.toFixed(4)).join(" ")}" data-psi="${psi0}" data-geo='${JSON.stringify(geo)}'`;
  // anemometer on the -x end: spindle, then the rotor (hub plus three cups on arms)
  const hx = -30, zc = armZ + 13;
  out.push(T.S(T.cyl(hx, 0, 1, armZ + 2.4, 8, 10), { tone: "mid" }));
  const R = 17, O = T.at([hx, 0, zc]);
  const ex = T.along([R, 0, 0]), ey = T.along([0, R, 0]);
  const dep = [T.depth([R, 0, 0]) - T.depth([0, 0, 0]), T.depth([0, R, 0]) - T.depth([0, 0, 0])];
  const hub = `<g class="ws-hub">${T.S(T.cyl(hx, 0, 3.6, zc - 2.6, 3.6, 18), { tone: "hi" })}</g>`;
  const cup = T.S(G.sphereOf([hx, 0, zc], 4.6, T.P), { tone: "hi", lit: true });
  const cups = [0, 1, 2].map((i) => {
    const a = (i * 2 * Math.PI) / 3, x = ex[0] * Math.cos(a) + ey[0] * Math.sin(a), y = ex[1] * Math.cos(a) + ey[1] * Math.sin(a);
    const d = dep[0] * Math.cos(a) + dep[1] * Math.sin(a);
    const g = `<g class="ws-cup" transform="translate(${x.toFixed(2)} ${y.toFixed(2)})"><line class="ws-arm" x1="${(O[0] - x).toFixed(2)}" y1="${(O[1] - y).toFixed(2)}" x2="${O[0].toFixed(2)}" y2="${O[1].toFixed(2)}"/>${cup}</g>`;
    return { d, g };
  });
  const back = cups.filter((c) => c.d < 0).map((c) => c.g).join(""), front = cups.filter((c) => c.d >= 0).map((c) => c.g).join("");
  out.push(`<g class="ws-rotor" data-ex="${ex.map((v) => v.toFixed(3)).join(" ")}" data-ey="${ey.map((v) => v.toFixed(3)).join(" ")}" data-dep="${dep.map((v) => v.toFixed(4)).join(" ")}" data-o="${O.map((v) => v.toFixed(2)).join(" ")}">${back}${hub}${front}</g>`);
  out.push(`<g class="ws-vane" ${vaneData}>${vaneSvg}</g>`);
  notes.weather = { ant: T.at([9, 14, 72]) };
  return out.join("");
}, { pad: 50 });   // extra pad keeps the rotor inside the round crop

// ---------- 6. Camera mount: post, printed base, ball joint and the eufyCam ----------
// The camera yaws about the ball: 13 pre-drawn angles 4 degrees apart; site.js shows the one nearest its spring's angle.
make("camera-mount", [[-44, -32, 22], [26, 32, 22], [-44, -32, 88], [26, 32, 88]], 45, (T) => {
  const out = [];
  out.push(T.S(T.slab({ x: -54, y: -26, w: 12, d: 52, r: 1 }, 18, 74, 4, 0.6), { tone: "mid" }));            // timber post
  out.push(T.D([[-42, -18, 30], [-42, 18, 30], [-42, -18, 80], [-42, 18, 80]].map((p) => T.at(p)), { size: 0.9 }));
  const Fb = G.frameAlong([-42, 0, 54], [1, 0, 0]);
  out.push(`<g class="cm-dark">${T.S(G.lathe([[0, 0], [0, 13], [5, 13], [6, 12], [8, 8], [8, 0]], Fb, T.P), { tone: "mid" })}</g>`);   // printed threaded base
  out.push(T.S(G.lathe([[8, 0], [8, 6.5], [17, 6.5], [17, 0]], Fb, T.P), { tone: "hi" }));                                          // ball-joint neck
  const ball = [-20, 0, 54];
  out.push(T.S(G.sphereOf(ball, 5.5, T.P), { tone: "hi" }));
  const rr = (w, h, r, n = 5) => {
    const pts = [];
    [[w / 2 - r, h / 2 - r, 0], [-w / 2 + r, h / 2 - r, 90], [-w / 2 + r, -h / 2 + r, 180], [w / 2 - r, -h / 2 + r, 270]].forEach(([cx, cy, a0]) => {
      for (let i = 0; i <= n; i++) { const a = ((a0 + (90 * i) / n) * Math.PI) / 180; pts.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); }
    });
    return pts;
  };
  const frame = (deg) => {
    const t = (deg * Math.PI) / 180, a = [Math.cos(t), Math.sin(t), 0];
    const F = G.frameAlong(ball, a);
    const at = (s, x, y) => F.o.map((o, i) => o + F.a[i] * s + F.u[i] * x + F.v[i] * y);
    let g = T.S(G.prismOf(F, rr(30, 46, 9), 3.5, 33, T.P), { tone: "hi", crease: "lo" });                 // body
    g += `<g class="cm-glass">${T.S(G.prismOf(F, rr(25, 41, 7), 33, 33.8, T.P), { tone: "hi" })}</g>`;      // black front glass
    const Fl = G.frameOf(at(33.8, 0, 11), F.a, F.u, F.v);
    g += T.S(G.disc(0, 0.6, 4.2, Fl, T.P), { tone: "mid", lit: true });                                    // lens
    g += T.D([at(34, -3.2, -13), at(34, 3.2, -13)].map((p) => T.at(p)), { size: 1.1, tone: "faint" });     // spotlights
    return g;
  };
  const angles = Array.from({ length: 13 }, (_, i) => -24 + 4 * i);
  angles.forEach((deg) => {
    out.push(`<g class="cm-frame" data-deg="${deg}" visibility="${deg === 0 ? "visible" : "hidden"}">${frame(deg)}</g>`);
  });
  notes.camera = { ball: T.at(ball) };
  return out.join("");
});

// ---------- 7. ENGG1100: the team's firefighting vehicle, from its Fusion "Final Design" ----------
// Proportions from the CAD's component boxes (exported read-only, 12 Nov 2026), scaled by 0.25 and turned so the
// vehicle's front (CAD y = 0) faces +x: icon x = (175 - Y) * s, y = (X - 80) * s, z = (Z + 44) * s.
// Two chassis plates with a sloped upper deck, a clear tank with the pump inside, a hose looping up to a
// pan-tilt nozzle turret, four wheels with yellow hubs. Drawn by me as an icon; no team CAD is published.
const R_ENGG = render("engg1100");
make("engg1100", [[-52, -27, 0], [96, 27, 0], [-52, -27, 76], [96, 27, 76]], 36, (T) => {
  const s = 0.25, X = (Y) => (175 - Y) * s, Yc = (x) => (x - 80) * s, Z = (z) => (z + 44) * s;
  const out = [T.halo({ x: -46, y: -26, w: 92, d: 52, r: 6 })];
  const img = (layer, cls = "") => `<image${cls ? ` class="${cls}"` : ""} href="assets/img/projects/engg1100-${layer}.webp" x="0" y="0" width="300" height="300"/>`;
  // the real vehicle, rendered from its CAD meshes (mesh_render.py), with the tank's water drawn between the
  // opaque parts and the glass so it reads as inside the tank, and drains while spraying
  // wheels: drawn in vector at the CAD's wheel positions until the re-exported wheel meshes arrive
  const wheel = (x, y, side) => {
    const F = G.frameAlong([x, y, Z(-11)], [0, side, 0]);
    return `<g class="ev-tyre">${T.S(G.disc(0, 7, 8.25, F, T.P), { tone: "mid" })}</g>` + `<g class="ev-hub">${T.S(G.disc(7, 7.6, 4.6, F, T.P), { tone: "lo" })}</g>`;
  };
  const wx = [X(33), X(312)], wy = 24.25 + 3.5;
  const meshWheels = R_ENGG && R_ENGG.groups && R_ENGG.groups.includes("wheels");
  const veh = [];
  if (!meshWheels) wx.forEach((x) => veh.push(wheel(x, -wy, -1)));                // far wheels, behind the body
  veh.push(img("body"));
  veh.push(`<g class="ev-water">${T.S(T.slab({ x: X(262), y: Yc(17), w: 183 * s, d: 125 * s, r: 2.4 }, Z(73), 70 * s, 6, 0.4), { tone: "lo" })}</g>`);
  veh.push(img("glass"));
  if (!meshWheels) wx.forEach((x) => veh.push(wheel(x, wy, 1)));                   // near wheels, in front
  out.push(`<g class="ev-drive">${veh.join("")}</g>`);
  // The target is what the brief describes: a heat source high up on a resort "building" on the test rig,
  // so the jet runs almost flat from the raised nozzle and only droops near the end, as a pressurised stream does.
  const CAN = [82, 0, 58];                                                     // heat-source can on top of the tower
  const nz = R_ENGG ? R_ENGG.keypoints.nozzle_tip : T.at([X(118) + 9, Yc(97), Z(236)]), hit = T.at([CAN[0] - 2, CAN[1], CAN[2] + 3]);
  const top = T.at([(X(118) + 9 + CAN[0]) / 2, Yc(97) / 2, Math.max(Z(236), CAN[2]) + 4]);
  const ctrl = [2 * top[0] - (nz[0] + hit[0]) / 2, 2 * top[1] - (nz[1] + hit[1]) / 2];
  const f = (v) => v.toFixed(1);
  const arc = (dc = [0, 0], de = [0, 0]) => `M${f(nz[0])} ${f(nz[1])} Q${f(ctrl[0] + dc[0])} ${f(ctrl[1] + dc[1])} ${f(hit[0] + de[0])} ${f(hit[1] + de[1])}`;
  const jet = arc();
  const spray = [];
  spray.push(`<path class="ev-jet-core" d="${jet}"/><path class="ev-jet-flow" d="${jet}"/>`);
  // the stream breaks up into droplets over its last third
  const jitter = [[0, 0, 0, 0], [1.2, -0.8, 1.5, 1], [-1.2, 0.8, -1.5, 0.5], [0.6, 1.2, 1, -1], [-0.6, -1, -1, 1.2], [1.6, 0.4, 2.2, 0], [-1.6, -0.4, -2, -0.5], [0.4, -1.6, 0.5, 1.6]];
  jitter.forEach(([cx, cy, ex, ey], i) => {
    spray.push(`<circle class="ev-drop" r="${(0.9 + (i % 3) * 0.25).toFixed(2)}"><animateMotion dur="0.5s" begin="${(i * 0.062).toFixed(3)}s" repeatCount="indefinite" calcMode="spline" keyTimes="0;1" keyPoints="0.55;1" keySplines="0.3 0 0.8 0.7" path="${arc([cx, cy], [ex, ey])}"/></circle>`);
  });
  // splash off the can, falling down the tower's face
  [[-5, -7, -8, 9], [-2, -9, -4, 12], [3, -8, 5, 10], [6, -5, 9, 8], [0, -11, 1, 14], [-7, -3, -10, 7]].forEach(([qx, qy, ex, ey], i) => {
    spray.push(`<circle class="ev-splash" r="${(0.8 + (i % 2) * 0.3).toFixed(2)}"><animateMotion dur="0.55s" begin="${(0.04 + i * 0.08).toFixed(2)}s" repeatCount="indefinite" path="M${f(hit[0])} ${f(hit[1])} Q${f(hit[0] + qx)} ${f(hit[1] + qy)} ${f(hit[0] + ex)} ${f(hit[1] + ey)}"/></circle>`);
  });
  // test-rig floor and the target tower: a small "resort building" with windows, a roof lip and the heat-source can
  out.push(T.S(T.slab({ x: 70, y: -14, w: 26, d: 28, r: 1.5 }, 0, 1.2, 3, 0.2), { tone: "lo" }));
  const tower = { x: 76, y: -6, w: 12, d: 12, r: 1 };
  out.push(T.S(T.slab(tower, 1.2, CAN[2] - 2 - 1.2, 4, 0.5), { tone: "mid" }));
  out.push([14, 26, 38, 50].map((z) => `<g transform="${k.sideMatrix([tower.x + 6, tower.y], z, T.P, "left")}"><rect class="iso-line" data-tone="lo" x="-3" y="-2.2" width="6" height="4.4" rx="0.6" fill="none"/></g>`).join(""));
  out.push(T.S(T.slab({ x: tower.x - 1, y: tower.y - 1, w: tower.w + 2, d: tower.d + 2, r: 1.2 }, CAN[2] - 2, 2, 4, 0.3), { tone: "hi" }));
  out.push(T.S(T.cyl(CAN[0], CAN[1], 3, CAN[2], 4, 20), { tone: "hi", lit: true }));                                 // heat-source can
  const fl = T.at([CAN[0], CAN[1], CAN[2] + 4]);
  out.push(`<g class="ev-fire"><path class="ev-flame" d="M${fl[0] - 5} ${fl[1]} C ${fl[0] - 7} ${fl[1] - 9} ${fl[0] - 2} ${fl[1] - 12} ${fl[0]} ${fl[1] - 19} C ${fl[0] + 2} ${fl[1] - 12} ${fl[0] + 7} ${fl[1] - 9} ${fl[0] + 5} ${fl[1]} Z"/><path class="ev-flame-in" d="M${fl[0] - 2.5} ${fl[1]} C ${fl[0] - 3.5} ${fl[1] - 5} ${fl[0] - 1} ${fl[1] - 7} ${fl[0]} ${fl[1] - 10} C ${fl[0] + 1} ${fl[1] - 7} ${fl[0] + 3.5} ${fl[1] - 5} ${fl[0] + 2.5} ${fl[1]} Z"/></g>`);
  out.push(`<g class="ev-spray">${spray.join("")}</g>`);
  // steam once the flame is out: puffs that rise and spread
  out.push(`<g class="ev-steam">${[[-3, 0, 2.6], [2, -2, 2.2], [0, -4, 3]].map(([dx, dy, r], i) => `<circle class="ev-puff ev-puff-${i}" cx="${f(fl[0] + dx)}" cy="${f(fl[1] - 4 + dy)}" r="${r}"/>`).join("")}</g>`);
  notes.engg = { back: vec(T, [-14, 0, 0]) };
  return out.join("");
}, { fixed: R_ENGG && R_ENGG.P });


// ---------- 8. Airbrakes: Isaac's FHC-1 airbrake module, rendered from its CAD meshes ----------
// The bay body, aft plate and interface rings, and the four forward-hinged flaps at 6 opening angles (0 to 80 deg), come
// from the meshes cad/airbrake_module.py exports (airbrakes_parts.py groups them; mesh_render.py draws them, the flaps
// masked wherever the body is nearer). site.js shows the flap layer nearest its spring's angle. FHC-1 is not built.
const R_AIRBRAKES = render("airbrakes");
make("airbrakes", [[-80, -80, 0], [80, 80, 0], [0, 0, 222]], 30, (T) => {
  const img = (layer) => `<image href="assets/img/projects/airbrakes-${layer}.webp" x="0" y="0" width="300" height="300"/>`;
  const ANGLES = [0, 16, 32, 48, 64, 80];
  const out = [T.halo({ x: -78, y: -78, w: 156, d: 156, r: 78 }), img("body")];
  ANGLES.forEach((d, i) => out.push(`<g class="ab-flaps" data-i="${i}" data-deg="${d}" visibility="${d === 0 ? "visible" : "hidden"}">${img("f" + d)}</g>`));
  notes.airbrakes = { angles: ANGLES };
  return out.join("");
}, { fixed: R_AIRBRAKES && R_AIRBRAKES.P });

// ---------- 9. Crank arm: the hollow Ti-6Al-4V arm, fitted to a bike ----------
// A drivetrain close-up: the bottom-bracket shell and frame tubes, the chainring and right crank on the far side, and the
// left crank arm (my design: Ø36 and Ø28 bosses 170 apart, a 13-deep web) with a platform pedal on the near side. World
// units are mm; x points forward, z up, y across the bike. site.js turns the cranks on hover and lets them coast to a stop:
//  - the chainring and right crank are flat, so one drawing rotates exactly by an affine matrix (data-ex, data-ez);
//  - the arm is drawn at 8 angles 45° apart, and the nearest is rotated by the small remainder, so its faces stay right;
//  - the pedal only translates, so it stays level, as a real pedal does.
const CR = { L: 170, rest: -45 };                                     // crank length; rest angle (forward and down)
// fit to the pedal's whole sweep (both faces of the pedal), so it stays inside the round card at every angle
const CR_FIT = Array.from({ length: 24 }, (_, i) => { const a = (i / 24) * 2 * Math.PI; return [[218 * Math.cos(a), 150, 218 * Math.sin(a)], [218 * Math.cos(a), -160, 218 * Math.sin(a)]]; }).flat();
make("crank-arm", CR_FIT, 110, (T) => {        // a three-quarter side view, so the crank circle reads
  const P = T.P, at = (p) => T.at(p), f = (n) => n.toFixed(2);
  const n = T.depth([0, -10, 0]) > T.depth([0, 10, 0]) ? -1 : 1;     // the camera's side of the bike
  const poly = (pts3) => "M" + pts3.map((q) => { const s = at(q); return f(s[0]) + " " + f(s[1]); }).join(" L") + " Z";
  const flat = (dpath, { shade = 2, tone = "mid" } = {}) => T.S({ fill: dpath, top: "", outline: dpath, crease: "", shades: [0, 1, 2, 3].map((k2) => (k2 === shade ? dpath : "")) }, { tone });
  const tube = (start, dir, len, r, tone = "mid") => T.S(G.lathe([[0, 0], [0, r], [len, r], [len, 0]], G.frameAlong(start, dir), P), { tone });
  const out = [];
  // far side, farthest first: the right pedal on the right crank's end (opposite the left), level like the near one
  const ypr = -n * 60, rest0 = CR.rest * Math.PI / 180 + Math.PI;
  const pedalR = T.S(G.lathe([[0, 0], [0, 6], [14, 6], [14, 0]], G.frameAlong([CR.L, ypr, 0], [0, -n, 0]), P), { tone: "mid" }) +
    T.S(T.slab({ x: CR.L - 48, y: n > 0 ? ypr - 12 - 84 : ypr + 12, w: 96, d: 84, r: 6 }, -9, 18, 4, 0.6), { tone: "mid" });
  const dr = T.along([CR.L * Math.cos(rest0) - CR.L, 0, CR.L * Math.sin(rest0)]).map((v) => v.toFixed(2));
  out.push(`<g class="cr-pedal-r" transform="translate(${dr[0]} ${dr[1]})">${pedalR}</g>`);
  // far side: chainring (44 teeth, 5-arm spider) and the right crank, one flat group that site.js rotates
  const yR = -n * 46, yA = -n * 56, rad = (deg) => deg * Math.PI / 180, rest = rad(CR.rest);
  const ringPts = Array.from({ length: 88 }, (_, i) => { const a = (i / 88) * 2 * Math.PI, r = i % 2 ? 84 : 90; return [r * Math.cos(a), yR, r * Math.sin(a)]; });
  const inner = Array.from({ length: 48 }, (_, i) => { const a = (i / 48) * 2 * Math.PI; return [72 * Math.cos(a), yR, 72 * Math.sin(a)]; });
  const spider = Array.from({ length: 5 }, (_, k2) => { const a = rad(72 * k2 + 18), c = Math.cos(a), s = Math.sin(a), w = 7; return poly([[22 * c - w * s, yR, 22 * s + w * c], [76 * c - w * s, yR, 76 * s + w * c], [76 * c + w * s, yR, 76 * s - w * c], [22 * c + w * s, yR, 22 * s - w * c]]); }).join(" ");
  const hub = poly(Array.from({ length: 24 }, (_, i) => { const a = (i / 24) * 2 * Math.PI; return [26 * Math.cos(a), yR, 26 * Math.sin(a)]; }));
  const ra = rest + Math.PI, c = Math.cos(ra), s = Math.sin(ra);
  const rightArm = poly([[-12 * s, yA, 12 * c], [CR.L * c - 9 * s, yA, CR.L * s + 9 * c], [CR.L * c + 9 * s, yA, CR.L * s - 9 * c], [12 * s, yA, -12 * c]]);
  const ringD = poly(ringPts) + " " + poly(inner);
  const ringSvg = `<g class="iso-solid"><path class="iso-fill" fill-rule="evenodd" d="${ringD}"/><path class="iso-shade" data-shade="1" fill-rule="evenodd" d="${ringD}"/><path class="iso-line iso-edge" data-tone="mid" d="${ringD}"/></g>`;
  const cR = at([0, yR, 0]).map(f), ex = T.along([1, 0, 0]).map(f), ez = T.along([0, 0, 1]).map(f);
  out.push(`<g class="cr-ring" data-c="${cR.join(" ")}">${flat(rightArm, { shade: 1 })}${ringSvg}${flat(spider, { shade: 2 })}${flat(hub, { shade: 2 })}</g>`);
  // frame: far chainstay, seat tube, down tube, the bottom-bracket shell, near chainstay
  out.push(tube([-14, -n * 22, 4], [-0.99, 0, 0.13], 260, 9));
  out.push(tube([-6, 0, 14], [-0.27, 0, 0.96], 240, 16));
  out.push(tube([10, 0, 10], [0.81, 0, 0.59], 260, 20));
  out.push(T.S(G.lathe([[0, 0], [0, 21], [70, 21], [70, 0]], G.frameAlong([0, -35, 0], [0, 1, 0]), P), { tone: "hi" }));
  out.push(tube([-14, n * 22, 4], [-0.99, 0, 0.13], 260, 9));
  // the left crank arm: 8 drawings, 45° apart
  const y0 = n * 38;
  const circle = (cx, r, m = 18) => Array.from({ length: m }, (_, i) => { const a = (i / m) * 2 * Math.PI; return [cx + r * Math.cos(a), r * Math.sin(a)]; });
  const hull = [...Array.from({ length: 13 }, (_, i) => { const a = -Math.PI / 2 + Math.PI * i / 12; return [CR.L + 14 * Math.cos(a), 14 * Math.sin(a)]; }),
                ...Array.from({ length: 13 }, (_, i) => { const a = Math.PI / 2 + Math.PI * i / 12; return [18 * Math.cos(a), 18 * Math.sin(a)]; })];
  const ANG = Array.from({ length: 8 }, (_, k2) => k2 * 45);
  const arms = ANG.map((deg) => {
    const th = rad(deg), u = [Math.cos(th), 0, Math.sin(th)], v = [-Math.sin(th), 0, Math.cos(th)];
    const F = G.frameOf([0, y0, 0], [0, n, 0], u, v);
    const g = T.S(G.prismOf(F, hull, 0, 13, P), { tone: "hi", lit: true }) +
              T.S(G.prismOf(F, circle(0, 18), 0, 20, P), { tone: "hi" }) +
              T.S(G.prismOf(F, circle(CR.L, 14), 0, 17, P), { tone: "hi" });
    const near = ((deg - ((CR.rest % 360) + 360) % 360) + 360) % 360 === 0;
    return `<g class="cr-arm" data-deg="${deg}" visibility="${near ? "visible" : "hidden"}">${g}</g>`;
  });
  out.push(`<g class="cr-arms" data-c="${at([0, y0 + n * 10, 0]).map(f).join(" ")}">${arms.join("")}</g>`);
  // the pedal: axle and a platform, drawn at angle 0 and moved to the rest angle; it stays level as the cranks turn
  const yp = n * 55, pedal = T.S(G.lathe([[0, 0], [0, 6], [14, 6], [14, 0]], G.frameAlong([CR.L, yp, 0], [0, n, 0]), P), { tone: "mid" }) +
    T.S(T.slab({ x: CR.L - 48, y: n > 0 ? yp + 12 : yp - 12 - 84, w: 96, d: 84, r: 6 }, -9, 18, 4, 0.6), { tone: "mid" });
  const d0 = T.along([CR.L * Math.cos(rest) - CR.L, 0, CR.L * Math.sin(rest)]).map(f);
  out.push(`<g class="cr-pedal" transform="translate(${d0[0]} ${d0[1]})">${pedal}</g>`);
  notes.crank = { side: n };
  return `<g class="cr" data-ex="${ex.join(" ")}" data-ez="${ez.join(" ")}" data-l="${CR.L}" data-rest="${CR.rest}">${out.join("")}</g>`;
}, { pad: 10, elevation: 20 });

// ---------- 10. Errol: the School's Lexus RX 450h with its roof sensor rack ----------
// The car is rendered from the Lexus mesh in ~/errol/src/errol_description (Autoware's sample vehicle, Apache-2.0):
// ../errol/build_lexus.mjs --groups splits it by colour, mesh_render.py draws models/errol.json. Sensors sit at their
// mounts in ~/errol/src/errol_description/config/sensor_mounts.yaml (Isaac: the real positions on the rack), on base_link
// (rear axle centre on the ground, x forward): Ouster OS1-128 at (1.40, 0, 2.00), the one lit part; RoboSense BP32 below it
// at (1.40, 0, 1.80); NovAtel antenna at (0, 0, 1.90); four u-blox antennas at (+-0.5, +-0.5, 1.90). Positions are exact;
// the sensors are drawn about 3x real size to read at 300 px. Scale 18.4 units per metre, rear axle at x = -24.
// On hover, scan rings ripple out across the ground from directly under the Ouster.
const R_ERROL = render("errol");
make("errol", [[-44, -24, 0], [49, 24, 0], [-44, -24, 44], [49, 24, 44]], 36, (T) => {
  const M = 18.4, AX = -24, at = (x, y, z) => [AX + x * M, y * M, z * M];
  const out = [T.halo({ x: -42, y: -20, w: 90, d: 40, r: 8 })];
  const f = (v) => v.toFixed(1);
  // ground scan rings, centred under the Ouster; drawn first so the car hides the far side of each
  const C0 = at(1.40, 0, 0), cpx = T.at(C0);
  const ring = (r) => { let d = ""; for (let i = 0; i <= 48; i++) { const a = i / 48 * 2 * Math.PI, q = T.at([C0[0] + r * Math.cos(a), C0[1] + r * Math.sin(a), 0]); d += (i ? "L" : "M") + f(q[0]) + " " + f(q[1]); } return d + "Z"; };
  out.push(`<g class="er-scan">${[0, 1, 2].map((i) => `<path class="er-ring er-ring-${i}" style="transform-origin: ${f(cpx[0])}px ${f(cpx[1])}px" d="${ring(46)}"/>`).join("")}</g>`);
  out.push(`<image href="assets/img/projects/errol-body.webp" x="0" y="0" width="300" height="300"/>`);
  // roof rack: four feet on the flat of the roof (its height from the mesh: 1.47-1.50 m at x = 0 and 1.45 m), two side
  // rails and three crossbars (rear pair under the u-blox antennas, front one for the LiDARs)
  const RZ = 1.80 * M;                                                     // rack top
  const feet = [[0, 0.55, 1.47], [0, -0.55, 1.47], [1.45, 0.55, 1.50], [1.45, -0.55, 1.50]];
  out.push(sortBy(T, feet, ([x, y]) => at(x, y, 1.6)).map(([x, y, z]) => { const [fx, fy] = at(x, y, 0); return T.S(T.cyl(fx, fy, 0.9, z * M, RZ - 1.4 - z * M, 10), { tone: "lo" }); }).join(""));
  [-0.55, 0.55].forEach((y) => out.push(T.S(T.slab({ x: at(-0.65, 0, 0)[0], y: y * M - 0.8, w: 2.15 * M, d: 1.6, r: 0.5 }, RZ - 1.4, 1.4, 3, 0.2), { tone: "lo" })));
  [-0.5, 0.5, 1.4].forEach((x) => out.push(T.S(T.slab({ x: at(x, 0, 0)[0] - 1.2, y: -0.62 * M, w: 2.4, d: 1.24 * M, r: 0.5 }, RZ - 1.4, 1.4, 3, 0.2), { tone: "lo" })));
  // GNSS antennas: the NovAtel master over the rear axle and the four u-blox 0.5 m around it, tops at 1.90 m
  const pucks = [[0, 0], [-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]];
  out.push(sortBy(T, pucks, ([x, y]) => at(x, y, 1.9)).map(([x, y], i) => {
    const [cx, cy] = at(x, y, 0);
    return `<g class="er-gnss${i === 0 ? " er-master" : ""}">${T.S(T.cyl(cx, cy, i === 0 ? 2.4 : 1.8, RZ, 1.90 * M - RZ, 18), { tone: "mid" })}</g>`;
  }).join(""));
  // RoboSense BP32 (optical centre 1.80 m) on the front bar, the Ouster above it on a short mast, base plate at 2.00 m
  const [ox, oy] = at(1.40, 0, 0);
  out.push(`<g class="er-dome">${T.S(T.cyl(ox, oy, 2.6, RZ, 1.4, 20), { tone: "lo" })}</g>`);
  out.push(T.S(T.cyl(ox, oy, 0.9, RZ + 1.4, 2.00 * M - RZ - 1.4, 12), { tone: "lo" }));
  out.push(`<g class="er-lidar">${T.S(T.cyl(ox, oy, 2.6, 2.00 * M, 3.4, 28), { tone: "hi", lit: true })}</g>`);
  const w0 = T.at([ox + 2.6, oy, 2.00 * M + 1.7]);
  out.push(`<circle class="er-lidar-dot" cx="${f(w0[0])}" cy="${f(w0[1])}" r="0.9"/>`);
  return out.join("");
}, { fixed: R_ERROL && R_ERROL.P });

// ---------- 11. METR4810: Isaac's steered cutter pod, and what happened at the final demonstration ----------
// A cutaway: three foam blocks in a row, their tops cut away at the tunnel's height so the bores show as grooves. The
// dashed red line is the planned tunnel (straight through the end blocks, a bend in the middle one). Pass 1, with the real
// pod from Fusion v195 (metr4810_parts.py, mesh_render.py, four steps in one camera), bores in from the near end and
// steers too little in the bend, so its groove runs wide; pass 2 bores in from the far end; a red cross marks the miss
// (facts.yaml metr4810: both end blocks bored, the passes did not meet, an under-torqued servo). At rest the icon shows
// that outcome with the pod parked at the first face; on hover it replays pass 1 (mt-p0..3 pod, mt-g1..3 grooves). Seen
// from the bend's side, looking down, so the grooves read. Only Isaac's parts are drawn; angles are illustrative.
const R_METR = render("metr4810-f0");
make("metr4810", [[-278, -30, 0], [35, 14, 0], [-278, -30, 29.2], [35, 14, 29.2]], 300, (T) => {
  const f = (v) => v.toFixed(1), BX = -47.3, BW = 70, GAP = 10, Y0 = -30, D = 44, H = 29.2, ZC = 14.6, R = 5.2;
  const X0 = [0, 1, 2].map((k) => BX - (k + 1) * BW - k * GAP);                  // each block's far (-x) face
  const TIPS = [[-46.7, 0], [-81.9, 0], [-126.4, -5.7], [-161.9, -9.5]];            // pass 1's cutter at each step
  const PLAN = [[-47.3, 0], [-127.3, 0], [-139, -1.2], [-150, -4.5], [-161, -10], [-172, -15.5], [-183, -19.5], [-195, -21.5], [-277.3, -22]];
  const PASS2 = [[-277.3, -22], [-201, -22]];
  // dense samples of a polyline, kept to the blocks (a groove only exists where there is foam)
  const dense = (pts) => { const o = []; for (let i = 1; i < pts.length; i++) { const [x0, y0] = pts[i - 1], [x1, y1] = pts[i], n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 0.5));
    for (let j = 0; j < n; j++) o.push([x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n]); } o.push(pts[pts.length - 1]); return o; };
  const inBlock = (x) => X0.some((x0) => x >= x0 && x <= x0 + BW);
  const groove = (pts) => { const d = dense(pts), runs = []; let cur = [];
    d.forEach((q) => { if (inBlock(q[0])) cur.push(q); else if (cur.length) { runs.push(cur); cur = []; } }); if (cur.length) runs.push(cur);
    return runs.filter((r) => r.length > 1).map((r) => { const L = [], Rt = [];
      r.forEach((q, i) => { const n = r[Math.min(i + 1, r.length - 1)], pv = r[Math.max(i - 1, 0)], tx = n[0] - pv[0], ty = n[1] - pv[1], m = Math.hypot(tx, ty) || 1;
        L.push(T.at([q[0] - ty / m * R, q[1] + tx / m * R, ZC])); Rt.push(T.at([q[0] + ty / m * R, q[1] - tx / m * R, ZC])); });
      return `<path d="M${[...L, ...Rt.reverse()].map((q) => f(q[0]) + " " + f(q[1])).join(" L")}Z" fill="#2E1499" fill-opacity="0.68"/>`; }).join(""); };
  const line = (pts) => pts.map(([x, y]) => T.at([x, y, ZC])).map((q, i) => (i ? " L" : "M") + f(q[0]) + " " + f(q[1])).join("");
  const out = [T.halo({ x: -279, y: -31, w: 316, d: 46, r: 8 })];
  // the blocks below the cut, the grooves on the cut face, and the plan
  out.push(X0.map((x0) => T.S(T.slab({ x: x0, y: Y0, w: BW, d: D, r: 0.6 }, 0, ZC, 4, 0.4), { tone: "lo" })).join(""));
  [1, 2, 3].forEach((i) => out.push(`<g class="mt-g mt-g${i}">${groove([[BX, 0], ...TIPS.slice(1, i + 1)])}${i === 3 ? groove(PASS2) : ""}</g>`));
  out.push(`<path class="mt-bore" d="${line(PLAN)}"/>`);
  // the pod, four steps
  [0, 1, 2, 3].forEach((i) => out.push(`<g class="mt-p mt-p${i}"><image href="assets/img/projects/metr4810-f${i}-body.webp" x="0" y="0" width="300" height="300"/></g>`));
  // foam chips spraying off the cutter while it bores (hover replay only; CSS mt-chip)
  const CHIPS = [[-26, -38, 0], [-40, -14, .09], [-8, -46, .18], [-44, -30, .27], [-20, -24, .36], [12, -40, .45], [-34, -48, .54], [6, -26, .63], [-48, -6, .72], [-14, -52, .81]];
  [1, 2, 3].forEach((i) => { const c = T.at([TIPS[i][0] - 2, TIPS[i][1], ZC + 3]);
    out.push(`<g class="mt-p mt-p${i}">${CHIPS.map(([dx, dy, dl], k) => `<rect class="mt-chip" x="${f(c[0] - 5)}" y="${f(c[1] - 5)}" width="${k % 3 ? 9 : 12}" height="${k % 2 ? 8 : 10}" rx="2" fill="${k % 2 ? '#FFF7DA' : '#E9E5F7'}" stroke="#2E1499" stroke-width="1.4" style="--dx:${dx}px;--dy:${dy}px;--dl:${dl}s"/>`).join("")}</g>`); });
  // the near walls again, in front of the pod where it is inside a block
  out.push(X0.map((x0) => T.S(T.slab({ x: x0, y: Y0, w: BW, d: 0.6, r: 0 }, 0, ZC, 1, 0), { tone: "lo" })).join(""));
  // the cut-away tops, ghosted
  out.push(`<g opacity="0.16">${X0.map((x0) => T.S(T.slab({ x: x0, y: Y0, w: BW, d: D, r: 0.6 }, ZC, H - ZC, 4, 0.4), { tone: "lo" })).join("")}</g>`);
  // the miss: between pass 1's last cut and pass 2's
  const a = T.at([TIPS[3][0] - R * 0.6, TIPS[3][1], ZC]), c = T.at([PASS2[1][0] + R * 0.6, PASS2[1][1], ZC]), m = [(a[0] + c[0]) / 2, (a[1] + c[1]) / 2];
  out.push(`<g class="mt-g mt-g3"><path d="M${f(a[0])} ${f(a[1])} L${f(c[0])} ${f(c[1])}" fill="none" stroke="#BB0700" stroke-width="1.4" stroke-dasharray="2 2"/>` +
           `<path d="M${f(m[0] - 4.5)} ${f(m[1] - 4.5)} L${f(m[0] + 4.5)} ${f(m[1] + 4.5)} M${f(m[0] + 4.5)} ${f(m[1] - 4.5)} L${f(m[0] - 4.5)} ${f(m[1] + 4.5)}" fill="none" stroke="#BB0700" stroke-width="2.6" stroke-linecap="round"/></g>`);
  return out.join("");
}, { fixed: R_METR && R_METR.P, pad: 18 });

// Held icons (not for publication) are drawn by a private module outside the repo, when it is present.
const PRIV = join(process.env.PORTFOLIO_PRIVATE ?? join(homedir(), ".config/portfolio-build"), "icons_private.mjs");
if (existsSync(PRIV)) (await import(PRIV)).default({ make, G });

writeFileSync(`${OUT}/icons-motion.json`, JSON.stringify(notes, null, 2));
console.log("wrote icons to", OUT, JSON.stringify(notes));
