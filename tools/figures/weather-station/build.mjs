// Exploded figure of the UQ Space launch-site weather station (anatomy kit).
// Positions and sizes come from the Fusion design "Weather Station Enclosure" v18 (component bounding boxes,
// exported read-only on 12 Nov 2026). Figure frame = Fusion frame shifted by (-74, -64, +3) mm so the box is centred.
// Board details (headers, chips) follow the vendors' layouts; parts and roles from weather-station/docs/parts-and-design.md.
// Build: node build.mjs [--out <file.html>]
import { writeFileSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { homedir } from "node:os";
// The Anatomy kit's folder comes from $ANATOMY_KIT or the private paths file (~/.config/portfolio-build/paths.json).
const KIT = process.env.ANATOMY_KIT ?? JSON.parse(readFileSync(join(process.env.PORTFOLIO_PRIVATE ?? join(homedir(), ".config/portfolio-build"), "paths.json"), "utf8")).anatomy.replace(/^~/, homedir());
const k = await import(join(KIT, "kit/iso-kit.mjs"));
const { kitScript } = await import(join(KIT, "scripts/inline-kit.mjs"));

const outArg = process.argv.indexOf("--out");
const OUT = outArg > 0 ? process.argv[outArg + 1] : "weather-station-exploded.html";
const theme = "light";

const WIDTH = 640, HEIGHT = 488;
const BOX = { x: -76.5, y: -66.5, w: 153, d: 133, r: 2 };            // Fusion x -2.5..150.5, y -2.5..130.5
const WALL = 3, FLOOR = 3, TOP = 48, LID_H = 3;                       // walls to Fusion z 45; lid 45..48
const STANDOFF = 5, PCB = 1.6, BOARD_Z = FLOOR + STANDOFF, ON = BOARD_Z + PCB;   // boards at Fusion z 5
const LIFT = { lid: [-60, -60, 96], boards: [0, 0, 58] };   // lid lifts up and away to the back; boards straight up
const CLAMP = { x: 84, y: 86, r: 8.5 };                                // pole clamp at the back-right corner (Fusion ~158, 150)
const TAB = { x: BOX.x + BOX.w, y: -16, w: 20, d: 24, r: 4 };      // screw tab, bottom of the right face
const FOOT = { x: BOX.x - 15, y: -12, w: 15, d: 24, r: 4 };         // screw tab on the left face (Fusion x -17.5)
const VENT = { x: BOX.x + BOX.w, y: 16, w: 7, d: 28, r: 1.5 };      // sensor vent housing over the BME280 (right face)
const ANT = [42.2, -13.5], ANT_TOP = 69.6 + 3;                       // whip at the Heltec's back corner, up through the lid
const BME = { x: 70.4, y: 18, w: 1.6, d: 25.4, r: 0.4 };            // board stands on the right wall, parts face -x

// Frame: the assembled station sits in the middle with even margins, at the largest scale that still keeps the
// apart pose (lid up and back, boards up) inside the frame.
const circleAt = ([x, y], r, z) => k.circleRing(x, y, r, 24).map(([px, py]) => [px, py, z]);
const lifted = (points, [dx, dy, dz]) => points.map(([x, y, z]) => [x + dx, y + dy, z + dz]);
const ASSEMBLED = [
  ...k.boxCorners(BOX, 0, TOP + LID_H), ...k.boxCorners(FOOT, 0, 4), ...k.boxCorners(TAB, 0, 4), ...k.boxCorners(VENT, 12, 40),
  ...k.boxCorners({ x: BOX.x + BOX.w - 18, y: BOX.y + BOX.d - 6, w: 20, d: 16 }, 26, 46),
  ...circleAt([CLAMP.x, CLAMP.y], CLAMP.r, 24), ...circleAt([CLAMP.x, CLAMP.y], CLAMP.r, 48), ...circleAt(ANT, 1.6, ANT_TOP),
];
const APART = [
  ...lifted(k.boxCorners(BOX, TOP - 4, TOP + LID_H), LIFT.lid),
  ...lifted([...circleAt(ANT, 1.6, ANT_TOP), ...k.boxCorners(BME, 13, 13 + 25.4)], LIFT.boards),
];
function centredProjection(rest, apart, width, height, { pad, azimuth }) {
  const unit = { origin: [0, 0], scale: 1, azimuth, elevation: k.ELEVATION };
  const bounds = (points) => {
    const flat = points.map((p) => k.iso(p, unit));
    const xs = flat.map(([x]) => x), ys = flat.map(([, y]) => y);
    return [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  };
  const [l, r, t, b] = bounds(rest), [L, R, T, B] = bounds([...rest, ...apart]);
  const cx = (l + r) / 2, cy = (t + b) / 2;
  const scale = Math.min((width - 2 * pad) / (2 * Math.max(cx - L, R - cx)), (height - 2 * pad) / (2 * Math.max(cy - T, B - cy)));
  return { origin: [width / 2 - cx * scale, height / 2 - cy * scale], scale, azimuth, elevation: k.ELEVATION };
}
// with the mirror below (about the frame's centre line, so the centring holds), this is Fusion's front-right iso view
const P = centredProjection(ASSEMBLED, APART, WIDTH, HEIGHT, { pad: 18, azimuth: -50 });

const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const slab = (plan, z, h, steps = 4, bevel = 0.4) => k.slabOf({ r: 0.6, ...plan }, z, h, P, steps, bevel);
const depth = ([x, y, z = 0]) => k.depthOf([x, y, z], P);
const byDepth = (items) => [...items].sort((a, b) => depth(a.at) - depth(b.at));

// ---------- enclosure base ----------
const walls = [
  { name: "y-", plan: { x: BOX.x, y: BOX.y, w: BOX.w, d: WALL, r: 0 } },
  { name: "x-", plan: { x: BOX.x, y: BOX.y + WALL, w: WALL, d: BOX.d - 2 * WALL, r: 0 } },
  { name: "x+", plan: { x: BOX.x + BOX.w - WALL, y: BOX.y + WALL, w: WALL, d: BOX.d - 2 * WALL, r: 0 } },
  { name: "y+", plan: { x: BOX.x, y: BOX.y + BOX.d - WALL, w: BOX.w, d: WALL, r: 0 } },
].map((w) => ({ ...w, at: [w.plan.x + w.plan.w / 2, w.plan.y + w.plan.d / 2, TOP / 2] }));
const ordered = byDepth(walls);
const backWalls = ordered.slice(0, 2), frontWalls = ordered.slice(2);
const wallSvg = (w) => S(k.slabOf(w.plan, FLOOR, TOP - FLOOR, P, 1, 0), { tone: "mid" });

function baseBack() {
  const out = [`<path class="iso-halo" d="${k.haloOf(BOX, 0, 4, P)}"/>`];
  out.push(S(k.slabOf(FOOT, 0, 4, P, 6, 0.5), { tone: "mid" }));
  out.push(L(k.ring(FOOT.x + 6, FOOT.y + FOOT.d / 2, 2.4, 4, P, 20), { tone: "lo" }));
  // pole clamp: a bracket off the back-right corner and a vertical collar the pole passes through
  out.push(S(k.slabOf({ x: BOX.x + BOX.w - 18, y: BOX.y + BOX.d - 6, w: 20, d: 16, r: 2 }, 26, 20, P, 4, 0.5), { tone: "mid" }));
  out.push(S(k.cylinder(CLAMP.x, CLAMP.y, CLAMP.r, 24, 24, P, 32), { tone: "mid" }));
  out.push(L(k.ring(CLAMP.x, CLAMP.y, 5.2, 48, P, 28), { tone: "lo" }), L(k.ring(CLAMP.x, CLAMP.y, 3.6, 48, P, 24), { tone: "faint" }));
  out.push(S(k.slabOf(BOX, 0, FLOOR, P, 3, 0), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(BOX, WALL + 3), FLOOR, P), { tone: "faint" }));
  backWalls.forEach((w) => out.push(wallSvg(w)));
  return out.join("");
}
function baseFront() {
  const out = frontWalls.map(wallSvg);
  // top rim line of the walls, all round, and the corner screw bosses' pilot holes
  out.push(L(k.planOutline(k.insetPlan(BOX, WALL / 2), TOP, P), { tone: "faint" }));
  const bosses = k.corners(BOX, 6);
  out.push(L(bosses.map(([x, y]) => k.ring(x, y, 1.6, TOP, P, 14)).join(""), { tone: "lo" }));
  // USB-C opening on the front (-y) face, in line with the Heltec's port
  const front = BOX.y;
  out.push(`<g transform="${k.sideMatrix([52, front], ON + 18, P, "left")}"><rect class="iso-line" data-tone="lo" x="-6.5" y="-4" width="13" height="8" rx="2" fill="none"/><rect class="iso-line" data-tone="faint" x="-4.5" y="-1.8" width="9" height="3.6" rx="1.4" fill="none"/></g>`);
  // seam where the walls meet the floor, and print-layer bands round the visible corners
  const x0 = BOX.x, x1 = BOX.x + BOX.w, y0 = BOX.y, y1 = BOX.y + BOX.d;
  out.push(L([FLOOR, 18, 33].map((z) => k.segment([x0, y0, z], [x1, y0, z], P) + k.segment([x1, y0, z], [x1, y1, z], P)).join(""), { tone: "faint" }));
  // sensor vent housing on the right face, with louvres
  out.push(S(k.slabOf(VENT, 12, 28, P, 4, 0.5), { tone: "mid" }));
  out.push([0, 1, 2, 3, 4].map((i) => `<g transform="${k.sideMatrix([VENT.x + VENT.w, VENT.y + VENT.d / 2], 16 + i * 5, P, "right")}"><rect class="iso-line" data-tone="lo" x="-10" y="-1" width="20" height="2" rx="1" fill="none"/></g>`).join(""));
  // screw tab with its hole
  out.push(S(k.slabOf(TAB, 0, 4, P, 6, 0.5), { tone: "mid" }));
  out.push(L(k.ring(TAB.x + 11, TAB.y + TAB.d / 2, 4, 4, P, 24), { tone: "lo" }));
  out.push(L(k.ring(TAB.x + 11, TAB.y + TAB.d / 2, 2.4, 4, P, 20), { tone: "faint" }));
  return out.join("");
}

// ---------- boards ----------
const standoffs = (plan, holes) =>
  byDepth(holes.map(([dx, dy]) => ({ at: [plan.x + dx, plan.y + dy] })))
    .map(({ at: [x, y] }) => S(k.cylinder(x, y, 2.4, FLOOR, STANDOFF, P, 18), { tone: "lo" })).join("");
const board = (plan, holes, lit = false) => {
  const out = [S(slab(plan, BOARD_Z, PCB, 4, 0.3), { tone: "hi", crease: "lo", lit })];
  out.push(L(holes.map(([dx, dy]) => k.ring(plan.x + dx, plan.y + dy, 1.6, ON, P, 14)).join(""), { tone: "lo" }));
  out.push(D(holes.map(([dx, dy]) => at([plan.x + dx, plan.y + dy, ON])), { size: 0.45, tone: "mid" }));
  return out.join("");
};
const header = (x, y, n, along = "x", h = 8.5, pitch = 2.54, rows = 1) => {
  const w = along === "x" ? n * pitch : rows * pitch, d = along === "x" ? rows * pitch : n * pitch;
  const plan = { x, y, w, d, r: 0.3 };
  const holes = along === "x" ? k.dotGrid(x + pitch / 2, y + pitch / 2, n, rows, pitch, ON + h, P) : k.dotGrid(x + pitch / 2, y + pitch / 2, rows, n, pitch, ON + h, P);
  return S(slab(plan, ON, h, 2, 0.2), { tone: "lo", crease: "none" }) + D(holes, { size: 0.42, tone: "lo" });
};
const chip = (plan, h = 1.2, tone = "mid") => S(slab(plan, ON, h, 2, 0.2), { tone, crease: "none" }) + L(k.planOutline(k.insetPlan({ r: 0.3, ...plan }, 1.2), ON + h, P, 2), { tone: "faint" });

const MEGA = { x: -66.9, y: -54, w: 101.6, d: 53.3, r: 1.5 };      // Fusion x 7.1..108.7, y 10..63.3 (USB-B overhangs to -x)
const MEGA_HOLES = [[15, 2.5], [15, 50.8], [96.5, 2.5], [90, 50.8]];
function mega() {
  const p = MEGA, out = [standoffs(p, MEGA_HOLES), board(p, MEGA_HOLES, true)];   // the one red-lit part: it runs the firmware
  out.push(S(slab({ x: p.x - 6, y: p.y + 6, w: 16, d: 12 }, ON, 11, 2, 0.4), { tone: "mid" }));          // USB-B
  out.push(S(slab({ x: p.x - 2, y: p.y + 34, w: 14, d: 9 }, ON, 11, 2, 0.4), { tone: "mid" }));          // DC jack
  out.push(header(p.x + 28, p.y + 0.6, 26));                                                            // digital header (back edge)
  out.push(header(p.x + 30, p.y + p.d - 3.2, 22));                                                      // power and analog header (front edge)
  out.push(header(p.x + p.w - 6, p.y + 6, 18, "y", 8.5, 2.54, 2));                                      // double header (end)
  out.push(chip({ x: p.x + 44, y: p.y + 16, w: 14, d: 14 }));                                           // ATmega2560
  out.push(chip({ x: p.x + 16, y: p.y + 20, w: 6, d: 3.2 }, 1.4, "lo"));                                // crystal
  out.push(S(k.cylinder(p.x + 10, p.y + 44, 1.6, ON, 1.8, P, 14), { tone: "mid" }));                   // reset button
  return out.join("");
}
const CONV = { x: -70, y: 8.5, w: 76, d: 43.5, r: 1.5 };           // Fusion x 4..80, y 72.5..116
const CONV_HOLES = [[3, 3], [73, 3], [3, 40.5], [73, 40.5]];
function converter() {
  const p = CONV, out = [standoffs(p, CONV_HOLES), board(p, CONV_HOLES)];
  out.push(chip({ x: p.x + 8, y: p.y + 8, w: 10, d: 10 }));
  out.push(header(p.x + 30, p.y + 4, 6));
  // three RJ11 sockets on the front edge, openings facing +y
  [0, 1, 2].forEach((i) => {
    const s = { x: p.x + 14 + i * 19, y: p.y + p.d - 15, w: 13.5, d: 14.5, r: 0.8 };
    out.push(S(slab(s, ON, 11, 2, 0.5), { tone: "hi", crease: "lo" }));
    out.push(`<g transform="${k.sideMatrix([s.x + s.w / 2, s.y + s.d], ON + 5.5, P, "left")}"><rect class="iso-line" data-tone="lo" x="-4.6" y="-3.6" width="9.2" height="7.2" rx="0.8" fill="none"/><path class="iso-line" data-tone="faint" d="M-2.4 -3.6V-1.6M0 -3.6V-1.6M2.4 -3.6V-1.6"/></g>`);
  });
  return out.join("");
}
const HELTEC = { x: 39.6, y: -61.5, w: 25.5, d: 50.2, r: 1.2 };    // Fusion x 113.6..139, y 2.5..52.7, raised to z 20.6
const HZ = 23.6, HON = HZ + PCB;                                     // board height in the figure frame
const HELTEC_PINS = [[2.5, 6], [23, 6], [2.5, 44], [23, 44]];
function heltec() {
  const p = HELTEC, out = [];
  // header pins in Dupont housings carry the board above the Mega's level
  out.push(byDepth(HELTEC_PINS.map(([dx, dy]) => ({ at: [p.x + dx, p.y + dy] })))
    .map(({ at: [x, y] }) => S(k.slabOf({ x: x - 1.3, y: y - 1.3, w: 2.6, d: 2.6, r: 0.3 }, FLOOR, HZ - FLOOR, P, 2, 0.2), { tone: "lo" })).join(""));
  out.push(S(slab(p, HZ, PCB, 4, 0.3), { tone: "hi", crease: "lo" }));
  out.push(D(HELTEC_PINS.map(([dx, dy]) => at([p.x + dx, p.y + dy, HON])), { size: 0.45, tone: "mid" }));
  out.push(S(slab({ x: p.x + p.w / 2 - 4.5, y: p.y - 2.2, w: 9, d: 7.5, r: 2.6 }, HON, 3.2, 6, 0.3), { tone: "mid" }));   // USB-C, faces the front opening
  out.push(S(slab({ x: p.x + 7, y: p.y + 8, w: 11, d: 13 }, HON, 2.4, 2, 0.2), { tone: "mid", crease: "none" }));           // ESP32-S3 can
  // OLED on its bracket (Fusion x 117..135.6, y 15.6..48.6, top z 30.2)
  const bracket = { x: 43, y: -48.4, w: 18.6, d: 33, r: 1 };
  out.push(S(slab(bracket, HON, 33.2 - HON - 1.2, 4, 0.3), { tone: "lo" }));
  out.push(S(slab(k.insetPlan(bracket, 0.6), 33.2 - 1.2, 1.2, 2, 0.2), { tone: "mid" }));
  out.push(L(k.planOutline({ ...k.insetPlan(bracket, 2.2), r: 0.4 }, 33.2, P, 2), { tone: "lo" }));
  // whip antenna: base, sleeve and tip
  out.push(S(k.cylinder(ANT[0], ANT[1], 2.4, HON, 4, P, 18), { tone: "mid" }));
  out.push(S(k.cylinder(ANT[0], ANT[1], 1.6, HON + 4, TOP - HON - 4, P, 16), { tone: "hi" }));
  return out.join("");
}
// the part of the whip above the lid's underside, drawn after the lid so it pokes through it as in the CAD
function antennaTop() {
  return S(k.cylinder(ANT[0], ANT[1], 1.6, TOP, ANT_TOP - TOP, P, 16), { tone: "hi" })
    + L(k.ring(ANT[0], ANT[1], 1.6, 58, P, 14) + k.ring(ANT[0], ANT[1], 1.6, 66, P, 14), { tone: "faint" });
}
function bme() {
  const p = BME, z0 = 13, out = [];
  out.push(S(k.slabOf({ x: p.x + p.w, y: p.y + 4, w: 3, d: 4, r: 0.4 }, z0 + 2, 4, P, 2, 0.2), { tone: "lo" }));           // wall clip
  out.push(S(k.slabOf(p, z0, 25.4, P, 2, 0.2), { tone: "hi", crease: "lo" }));
  out.push(S(k.slabOf({ x: p.x - 0.9, y: p.y + 11.4, w: 0.9, d: 2.6, r: 0.2 }, z0 + 11.4, 2.6, P, 2, 0.1), { tone: "hi" }));  // BME280 can
  out.push(S(k.slabOf({ x: p.x - 3, y: p.y + 1.5, w: 3, d: 6, r: 0.3 }, z0 + 9.7, 4.5, P, 2, 0.2), { tone: "mid" }));        // PiicoDev connectors
  out.push(S(k.slabOf({ x: p.x - 3, y: p.y + p.d - 7.5, w: 3, d: 6, r: 0.3 }, z0 + 9.7, 4.5, P, 2, 0.2), { tone: "mid" }));
  return out.join("");
}
const SD = { x: 12, y: 5, w: 21.6, d: 17.8, r: 1.2 };              // Fusion x 86..107.6, y 69..86.8
const SD_HOLES = [[2.5, 2.5], [19.1, 2.5]];
function sd() {
  const p = SD, out = [standoffs(p, SD_HOLES), board(p, SD_HOLES)];
  out.push(chip({ x: p.x + 6, y: p.y + 4, w: 9, d: 7 }, 1.1));                                           // SD flash chip
  out.push(header(p.x + 1.5, p.y + p.d - 3.2, 7, "x", 2.6));
  return out.join("");
}

const BOARDS = [
  { id: "mega", fn: mega, plan: MEGA },
  { id: "converter", fn: converter, plan: CONV },
  { id: "heltec", fn: heltec, plan: HELTEC },
  { id: "bme", fn: bme, plan: BME },
  { id: "sd", fn: sd, plan: SD },
].map((b) => ({ ...b, at: [b.plan.x + b.plan.w / 2, b.plan.y + b.plan.d / 2] }));

// ---------- lid ----------
function lid() {
  const out = [];
  out.push(`<path class="iso-halo" d="${k.haloOf(k.insetPlan(BOX, 10), TOP - 4, 0.1, P)}" style="filter:blur(5px);opacity:.35"/>`);
  out.push(S(k.slabOf(k.insetPlan(BOX, WALL + 0.4), TOP - 4, 4, P, 8, 0.3), { tone: "lo" }));            // locating lip
  out.push(S(k.slabOf(BOX, TOP, LID_H, P, 8, 1), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(BOX, 10), TOP + LID_H, P), { tone: "faint" }));
  const screws = k.corners(BOX, 6);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.4, TOP + LID_H, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, TOP + LID_H])), { size: 0.55, tone: "mid" }));
  out.push(L(k.sideSeam(BOX, TOP + LID_H / 2, P, 8), { tone: "faint" }));
  const z = TOP + LID_H;
  const plate = { x: -48, y: -20, w: 44, d: 22, r: 1.5 };
  out.push(S(k.slabOf(plate, z, 0.8, P, 3, 0.2), { tone: "lo", crease: "none" }));
  out.push(D(k.corners(plate, 2.4).map(([x, y]) => at([x, y, z + 0.8])), { size: 0.45, tone: "mid" }));
  out.push(L([7, 11, 15].map((dy) => k.lineOnTop([plate.x + 6, plate.y + dy], [plate.x + (dy === 15 ? 26 : 38), plate.y + dy], z + 0.8, P)).join(""), { tone: "faint", free: true }));
  out.push(L(k.ring(ANT[0], ANT[1], 3.2, z, P, 20), { tone: "lo" }), L(k.ring(ANT[0], ANT[1], 2.2, z, P, 16), { tone: "faint" }));   // antenna hole
  return out.join("");
}

const move = (dz) => k.translateAlong(P, [0, 0, dz]);
const svg = k.figureSvg({
  width: WIDTH, height: HEIGHT,
  label: "The launch-site weather station's parts, placed as in its Fusion design: a 3D-printed enclosure holding an Arduino Mega 2560, the SEN0186 weather-kit adapter behind it, a microSD breakout, a raised Heltec WiFi LoRa 32 V3 radio board whose antenna rises through the lid, and a BME280 breakout standing on the right wall behind a vent. The Arduino Mega, which runs the firmware, is the part in red. Hovering lifts the lid and then the boards out of the box.",
  // The kit's axes have the opposite handedness to Fusion's, so the drawing is mirrored left to right
  // to show the box as Fusion's front-right iso view does (USB-C face on the left, vent and clamp on the right).
  body: [
    `<g transform="translate(${WIDTH} 0) scale(-1 1)">`,
    `<g data-part="base">${baseBack()}</g>`,
    ...byDepth(BOARDS).map((b) => `<g class="ws-boards" data-part="${b.id}">${b.fn()}</g>`),
    `<g data-part="base">${baseFront()}</g>`,
    `<g class="ws-lid" data-part="lid">${lid()}</g>`,
    `<g class="ws-boards" data-part="heltec">${antennaTop()}</g>`,
    `</g>`,
  ],
});

const PARTS = {
  lid: "Enclosure lid · 3D-printed in ASA, screwed to the base",
  base: "Enclosure base · ASA, with a pole clamp, screw tabs and a vent housing for the BME280",
  mega: "Arduino Mega 2560 · reads the weather kit and the BME280, logs every row to SD",
  converter: "SEN0186 converter · wind and rain sensors plug in by RJ11; one UART line to the Mega",
  heltec: "Heltec WiFi LoRa 32 V3 · raised on its headers; relays each row to the ground station on 915 MHz",
  bme: "BME280 breakout · on the right wall behind a vent; pressure, temperature and humidity over I2C",
  sd: "microSD breakout · the local log, written before anything is sent",
};
const ORDER = ["lid", "mega", "converter", "heltec", "bme", "sd", "base"];

const live = `
const P = ${JSON.stringify(P)};
const LIFT = ${JSON.stringify(LIFT)};
const PARTS = ${JSON.stringify(PARTS)};
const ORDER = ${JSON.stringify(ORDER)};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const lidEl = svg.querySelector(".ws-lid");
const boardEls = [...svg.querySelectorAll(".ws-boards")];
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
// one spring per assembly; the lid leaves first and comes home last
const springs = { lid: { x: 0, v: 0, goal: 0, at: 0 }, boards: { x: 0, v: 0, goal: 0, at: 0 } };
const STAGGER = 0.12, STIFF = 64, DRAG = 14.2;
// The tour: once, the first time the figure is half in view, it comes apart, holds, and goes back together, all
// settled by about 3.5 s (WCAG 2.2.2 needs a pause control only for motion that lasts more than 5 s). TOUR.limit is a hard
// stop on slow devices. Any pointer, focus or key input ends the tour for good. No tour under reduced motion.
const TOUR = { apart: 0.2, together: 2.4, limit: 4.7 };
let clock = 0, last = 0, frame = 0, visible = false, apart = false, picked = null;
let tour = null, toured = still.matches;   // tour = its start time while it runs; toured = it has run or been stopped
function setApart(on) {
  if (on === apart) return;
  apart = on;
  const first = on ? "lid" : "boards", second = on ? "boards" : "lid";
  springs[first].goal = on ? 1 : 0; springs[first].at = clock;
  springs[second].goal = on ? 1 : 0; springs[second].at = clock + STAGGER;
  run();
}
function pick(id) {
  picked = id;
  svg.querySelectorAll("[data-part]").forEach((g) => (g.dataset.part === id ? g.setAttribute("data-on", "") : g.removeAttribute("data-on")));
  if (id) svg.setAttribute("data-focus", ""); else svg.removeAttribute("data-focus");
  const text = id ? PARTS[id] : "";
  if (readout.textContent !== text) readout.textContent = text;
}
function place() {
  const l = springs.lid.x, b = springs.boards.x;
  l > 0.0005 ? lidEl.setAttribute("transform", translateAlong(P, LIFT.lid.map((v) => v * l))) : lidEl.removeAttribute("transform");
  const t = b > 0.0005 ? translateAlong(P, LIFT.boards.map((v) => v * b)) : "";
  boardEls.forEach((g) => (t ? g.setAttribute("transform", t) : g.removeAttribute("transform")));
}
function rest() {   // snap both assemblies home at once
  apart = false;
  for (const s of Object.values(springs)) { s.x = s.goal = 0; s.v = 0; s.at = clock; }
}
function tick(now) {
  // springs run on real time (sub-stepped, so a slow frame doesn't throw them); the tour runs on the wall clock
  const dt = last ? Math.min((now - last) / 1000, 0.1) : 1 / 60;
  last = now; clock += dt;
  if (tour !== null) {
    const t = (performance.now() - tour) / 1000;
    if (t >= TOUR.limit) { tour = null; rest(); }
    else if (t >= TOUR.together) setApart(false);
    else if (t >= TOUR.apart) setApart(true);
  }
  let moving = false;
  const steps = Math.max(1, Math.ceil(dt * 240)), h = dt / steps;
  for (const s of Object.values(springs)) {
    if (still.matches) { if (clock >= s.at) { s.x = s.goal; s.v = 0; } continue; }
    const aim = clock >= s.at ? s.goal : s.x;
    for (let i = 0; i < steps; i++) { s.v += ((aim - s.x) * STIFF - s.v * DRAG) * h; s.x += s.v * h; }
    if (Math.abs(aim - s.x) < 0.0005 && Math.abs(s.v) < 0.0005) { s.x = aim; s.v = 0; } else moving = true;
    if (clock < s.at) moving = true;
  }
  if (tour !== null && !apart && !moving && (performance.now() - tour) / 1000 >= TOUR.together) tour = null;   // home: done
  place();
  frame = visible && (moving || tour !== null) ? requestAnimationFrame(tick) : 0;
}
function run() { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } }
function startTour() {
  if (toured || still.matches) return;
  toured = true; tour = performance.now(); visible = true; run();
}
// Input of any kind stops the tour for good (or stops it from ever starting). Input inside the stage leaves the
// figure apart, as hovering or focusing it would; anywhere else it goes back together.
function stopTour(ev) {
  if (toured && tour === null) return;
  const running = tour !== null;
  tour = null; toured = true;
  if (running) setApart(ev.target instanceof Node && stage.contains(ev.target));
}
for (const type of ["pointerdown", "pointermove", "pointerover", "wheel", "touchstart", "keydown", "focusin"]) window.addEventListener(type, stopTour, { capture: true, passive: true });
still.addEventListener("change", () => { if (!still.matches) return; toured = true; if (tour !== null) { tour = null; rest(); place(); } });
new IntersectionObserver((e) => { visible = e[e.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "80px 0px" }).observe(stage);
new IntersectionObserver((e, seen) => {
  if (!e.some((x) => x.isIntersecting && x.intersectionRatio >= 0.5)) return;
  seen.disconnect(); startTour();
}, { threshold: 0.5 }).observe(stage);
stage.addEventListener("pointerenter", () => setApart(true));
stage.addEventListener("pointerleave", (ev) => { if (ev.pointerType === "mouse") { setApart(false); pick(null); } });   // a tap leaves the station apart and the part named
const partAt = (ev) => { const g = ev.target.closest && ev.target.closest("[data-part]"); pick(g ? g.dataset.part : null); };
stage.addEventListener("pointermove", partAt);
stage.addEventListener("pointerdown", (ev) => { if (ev.pointerType !== "mouse") { setApart(true); partAt(ev); } });   // a tap fires no pointermove on most phones
stage.addEventListener("focus", () => { setApart(true); if (!picked) pick(ORDER[0]); });
stage.addEventListener("blur", () => { setApart(false); pick(null); });
stage.addEventListener("keydown", (ev) => {
  const i = picked ? ORDER.indexOf(picked) : -1;
  if (ev.key === "ArrowRight" || ev.key === "ArrowDown") pick(ORDER[(i + 1) % ORDER.length]);
  else if (ev.key === "ArrowLeft" || ev.key === "ArrowUp") pick(ORDER[(i - 1 + ORDER.length) % ORDER.length]);
  else if (ev.key === " " || ev.key === "Enter") setApart(!apart);
  else if (ev.key === "Escape") { setApart(false); pick(null); }
  else return;
  ev.preventDefault();
});
pick(null);
place();
`;

const css = `
html{color-scheme:light!important;background:transparent!important}body{background:transparent!important}
/* the site's card-icon palette (style.css, .card .icon.iso): white faces, a lavender ramp, indigo outlines, one red accent */
body.iso[data-theme="light"]{
  --anatomy-card:#ffffff;--anatomy-paper:#ffffff;--anatomy-face:#ffffff;--anatomy-top:#ffffff;
  --anatomy-shade-0:#cfc7ec;--anatomy-shade-1:#ddd7f2;--anatomy-shade-2:#e9e5f7;--anatomy-shade-3:#f4f2fb;
  --anatomy-lit-top:#fff3f0;--anatomy-lit-shade:#f6d8d2;
  --anatomy-hi:#2E1499;--anatomy-mid:#6E5CC4;--anatomy-lo:#A99EDB;--anatomy-faint:#D9D3F0;--anatomy-lit:#BB0700;
  --anatomy-halo:#2E1499;--anatomy-halo-opacity:.22;--anatomy-dot:#2E1499;
  --anatomy-text:#2E1499;--anatomy-muted:#5E4FA8}
.iso-page{width:100%!important;margin:0!important}
/* the plate is the whole frame: no outline rule and no margin round it (the kit's would show as grey rules in the iframe) */
.iso-figure{margin:0}
.iso-plate{padding:44px 24px;border-radius:12px;box-shadow:none}
.iso-plate-corners{inset:16px 22px}
/* a picked part: indigo-deep edges on a lavender fill; the rest steps well back. Red stays on the Mega alone. */
.iso-svg [data-part][data-on]{
  --anatomy-paper:#f1eefb;--anatomy-top:#e4dff6;
  --anatomy-shade-0:#b4a8e1;--anatomy-shade-1:#c4bae8;--anatomy-shade-2:#d3cbef;--anatomy-shade-3:#e0daf4;
  --anatomy-hi:#220E73;--anatomy-mid:#4A36B0;--anatomy-lo:#6E5CC4;--anatomy-faint:#A99EDB;--anatomy-dot:#220E73;--anatomy-weight:.9px}
.iso-svg [data-part][data-on] .iso-solid:not([data-lit])>.iso-edge{stroke:#220E73}
.iso-svg[data-focus] [data-part]:not([data-on]){
  --anatomy-top:#ffffff;--anatomy-shade-0:#eeebf8;--anatomy-shade-1:#f2f0fa;--anatomy-shade-2:#f6f4fc;--anatomy-shade-3:#faf9fd;
  --anatomy-hi:#cec6eb;--anatomy-mid:#d9d3f0;--anatomy-lo:#e3dff4;--anatomy-faint:#efecf8;--anatomy-dot:#c4bbe8;
  --anatomy-lit:#e6aaa2;--anatomy-lit-top:#fffaf9;--anatomy-lit-shade:#fbeeeb;--anatomy-halo-opacity:.06}
.iso-stage{outline:none;cursor:default}
.iso-stage:focus-visible{box-shadow:0 0 0 3px #2E1499;border-radius:10px}
@font-face{font-family:"Sanchez";src:url("../fonts/sanchez-400-latin.woff2") format("woff2");font-display:swap}
.iso-plate-corner,.iso-plate-corner[data-corner]{font-family:"Sanchez",Georgia,serif;font-size:12.5px;line-height:1.3;letter-spacing:0;text-transform:none}
.iso-plate-corner[data-corner="fig"],.iso-plate-corner[data-corner="title"]{display:none}
/* the hint reads first, top left; the readout names the picked part along the bottom and wraps when it must */
.iso-plate-corner[data-corner="hint"]{top:0;bottom:auto;left:0}
.iso-plate-corner[data-corner="readout"]{top:auto;bottom:0;left:0;right:0;text-align:right;white-space:normal;text-wrap:balance}
@media (max-width:600px){
  .iso-plate{padding:46px 8px}
  .iso-plate-corners{inset:12px 12px}
  .iso-plate-corner[data-corner="hint"]{bottom:auto}
  .iso-plate-corner,.iso-plate-corner[data-corner]{font-size:11.5px}}
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "",
  hint: "Hover or tap a part, or tab in and use the arrow keys",
  readout: "",
  keys: [],
  caption: "",
  body: `<div class="iso-stage" tabindex="0" role="group" aria-label="Weather station parts. Focus to take it apart; arrow keys name each part; Space puts it back together.">${svg}</div>`,
});

const page = k.pageHtml({ title: "Weather station, apart", theme, body, script: kitScript() + live })
  .replace("</style>", css + "</style>")
  .replace("<head>", "<head><!-- Drawn with the Anatomy kit (MIT License, Copyright (c) 2026 Ryan): see LICENSE-anatomy-kit.txt beside this file. -->");
writeFileSync(OUT, page);
console.log("wrote", OUT, (page.length / 1024).toFixed(0), "KB");
