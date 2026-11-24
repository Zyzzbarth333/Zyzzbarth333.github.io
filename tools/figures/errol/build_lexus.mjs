// Turn Errol's Lexus mesh (errol_description/meshes/lexus.dae, Autoware's sample_vehicle, Apache-2.0) into a
// small textured .glb for the Lichtblick replay, and a binary STL for the card icon.
//
//   node build_lexus.mjs <lexus.dae> <lexus.png> <out.glb> [--stl out.stl] [--groups dir] [--tris 30000] [--wheelbase 2.79]
//
// --groups writes one binary STL per colour group (body, glass, tyres, hubs, lamps; metres, z-up) for the card icon's
// mesh_render.py, sorted by each triangle's baked colour and height.
//
// lexus.png is the model's lexus.jpg texture re-saved as PNG (Pillow: Image.open(jpg).convert('RGB').save(png)).
// Its UVs are stored once per triangle corner, which leaves nothing for a simplifier to collapse, so the script
// welds corners by position and bakes the texture into vertex colours (flat paint, dark tyres and glass, red lamps;
// the texture's vendor logo is painted over with the body colour).
//
// The mesh is placed exactly as errol.urdf.xacro places it on base_link (rear axle centre on the ground,
// x forward, y left, z up): visual origin xyz = (wheelbase / 2, 0, 0), rpy = (pi/2, 0, pi). The .glb stores
// that frame in glTF's y-up axes, which Lichtblick turns back to z-up on load. The STL stays z-up.
// Simplification uses meshoptimizer (MIT) from the Lichtblick checkout's node_modules.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { homedir } from 'node:os';

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i < 0 ? d : args.splice(i, 2)[1]; };
const stlOut = opt('--stl', null), groupsDir = opt('--groups', null), TRIS = +opt('--tris', 30000), WB = +opt('--wheelbase', 2.79);
const [daePath, pngPath, glbOut] = args;
if (!glbOut) { console.error('usage: build_lexus.mjs <lexus.dae> <lexus.png> <out.glb> [--stl out.stl] [--tris N]'); process.exit(2); }

const req = createRequire(`${homedir()}/.local/share/portfolio-tools/lichtblick/package.json`);
const { MeshoptSimplifier } = await import(req.resolve('meshoptimizer'));
const { PNG } = req('pngjs');
await MeshoptSimplifier.ready;

// ---------- read the one textured triangle list in the COLLADA file ----------
const dae = readFileSync(daePath, 'utf8');
const arr = (id) => { const m = dae.match(new RegExp(`<float_array id="${id}"[^>]*>([^<]*)<`)); return Float64Array.from(m[1].trim().split(/\s+/), Number); };
const P = arr('shape0-lib-positions-array'), T = arr('shape0-lib-map-array');
const p = Uint32Array.from(dae.match(/<triangles[^>]*>[\s\S]*?<p>([^<]*)<\/p>/)[1].trim().split(/\s+/), Number);

// One vertex per distinct position, on base_link: (x, y, z) -> (-x + wb/2, z, y). Colour = mean texel over its corners.
const img = PNG.sync.read(readFileSync(pngPath)), W = img.width, H = img.height;
// The texture carries a vendor logo on each front door (two hexagons); paint them over with the body colour.
const LOGOS = [[400, 480, 820, 910], [660, 740, 815, 900]].map((b) => b.map((v) => v / 1280));   // x0, x1, y0, y1 as fractions
const at = (x, y) => { const o = 4 * (y * W + x); return [img.data[o], img.data[o + 1], img.data[o + 2]]; };
const BODY = at(Math.floor(0.4375 * W), Math.floor(0.672 * H));                                      // plain paint beside the logos
const texel = (u, v) => {
  const fx = u, fy = 1 - v;
  if (LOGOS.some(([x0, x1, y0, y1]) => fx >= x0 && fx < x1 && fy >= y0 && fy < y1)) return BODY;
  return at(Math.min(W - 1, Math.max(0, Math.floor(fx * W))), Math.min(H - 1, Math.max(0, Math.floor(fy * H))));
};
const key = new Map(), pos = [], csum = [], idx = new Uint32Array(p.length / 2);
for (let c = 0; c < idx.length; c++) {
  const vi = p[2 * c], ti = p[2 * c + 1];
  const k = `${P[3 * vi]},${P[3 * vi + 1]},${P[3 * vi + 2]}`;
  let v = key.get(k);
  if (v === undefined) { v = pos.length / 3; key.set(k, v); pos.push(-P[3 * vi] + WB / 2, P[3 * vi + 2], P[3 * vi + 1]); csum.push(0, 0, 0, 0); }
  const [r, g, b] = texel(T[2 * ti], T[2 * ti + 1]);
  csum[4 * v] += r; csum[4 * v + 1] += g; csum[4 * v + 2] += b; csum[4 * v + 3]++;
  idx[c] = v;
}
let positions = Float32Array.from(pos);
let colors = new Float32Array(positions.length);                         // linear-ish 0..1 for glTF COLOR_0
for (let v = 0; v < colors.length / 3; v++) for (let j = 0; j < 3; j++) colors[3 * v + j] = ((csum[4 * v + j] / csum[4 * v + 3]) / 255) ** 2.2;
const box = (a) => [0, 1, 2].map((j) => { let lo = Infinity, hi = -Infinity; for (let i = j; i < a.length; i += 3) { lo = Math.min(lo, a[i]); hi = Math.max(hi, a[i]); } return [+lo.toFixed(3), +hi.toFixed(3)]; });
console.log(`read ${idx.length / 3} triangles, ${positions.length / 3} welded vertices; base_link box x/y/z`, JSON.stringify(box(positions)));

// ---------- simplify, weighing colour so paint boundaries stay put ----------
let [out, err] = MeshoptSimplifier.simplifyWithAttributes(idx, positions, 3, colors, 3, [1, 1, 1], null, TRIS * 3, 0.01, []);
const [remap, nv] = MeshoptSimplifier.compactMesh(out);   // drops unused vertices, rewrites `out` in place
const P2 = new Float32Array(nv * 3), C2 = new Float32Array(nv * 3);
for (let i = 0; i < remap.length; i++) if (remap[i] !== 0xffffffff) { P2.set(positions.subarray(3 * i, 3 * i + 3), 3 * remap[i]); C2.set(colors.subarray(3 * i, 3 * i + 3), 3 * remap[i]); }
positions = P2; colors = C2;
console.log(`simplified to ${out.length / 3} triangles, ${nv} vertices (error ${err.toFixed(4)})`);

// ---------- smooth normals, shared across uv seams ----------
const N = new Float32Array(nv * 3), group = MeshoptSimplifier.generatePositionRemap(positions, 3), acc = new Float32Array(nv * 3);
for (let t = 0; t < out.length; t += 3) {
  const [a, b, c] = [out[t], out[t + 1], out[t + 2]].map((i) => positions.subarray(3 * i, 3 * i + 3));
  const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], w = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
  const n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];   // area-weighted
  for (const i of [out[t], out[t + 1], out[t + 2]]) for (let j = 0; j < 3; j++) acc[3 * group[i] + j] += n[j];
}
for (let i = 0; i < nv; i++) { const g = group[i], l = Math.hypot(acc[3 * g], acc[3 * g + 1], acc[3 * g + 2]) || 1; for (let j = 0; j < 3; j++) N[3 * i + j] = acc[3 * g + j] / l; }

// ---------- binary STL, z-up, for the icon renderer ----------
if (stlOut) {
  const nt = out.length / 3, b = Buffer.alloc(84 + nt * 50); b.writeUInt32LE(nt, 80);
  for (let t = 0; t < nt; t++) {
    const o = 84 + t * 50;
    for (let k = 0; k < 3; k++) for (let j = 0; j < 3; j++) b.writeFloatLE(positions[3 * out[3 * t + k] + j], o + 12 + 12 * k + 4 * j);
  }
  writeFileSync(stlOut, b); console.log(`wrote ${stlOut} (${(b.length / 1e6).toFixed(2)} MB)`);
}

if (groupsDir) {
  mkdirSync(groupsDir, { recursive: true });
  const srgb = (c) => 255 * Math.max(0, c) ** (1 / 2.2);
  const groups = { body: [], glass: [], tyres: [], hubs: [], lamps: [] };
  for (let t = 0; t < out.length; t += 3) {
    const ids = [out[t], out[t + 1], out[t + 2]];
    const [r, g, b] = [0, 1, 2].map((j) => ids.reduce((a, i) => a + srgb(colors[3 * i + j]), 0) / 3);
    const z = ids.reduce((a, i) => a + positions[3 * i + 2], 0) / 3, lum = (r + g + b) / 3;
    const k = r > 150 && g < 110 && b < 110 ? 'lamps'
      : b > r + 25 ? 'glass'                                                  // headlamp glass
      : lum < 95 ? (z < 0.8 ? 'tyres' : 'glass')
      : lum < 205 && z < 0.8 ? 'hubs' : 'body';
    groups[k].push(t);
  }
  for (const [name, list] of Object.entries(groups)) {
    const bb = Buffer.alloc(84 + list.length * 50); bb.writeUInt32LE(list.length, 80);
    list.forEach((t, n) => { for (let kk = 0; kk < 3; kk++) for (let j = 0; j < 3; j++) bb.writeFloatLE(positions[3 * out[t + kk] + j], 84 + n * 50 + 12 + 12 * kk + 4 * j); });
    writeFileSync(`${groupsDir}/${name}.stl`, bb);
  }
  console.log('groups:', Object.entries(groups).map(([n, l]) => `${n} ${l.length}`).join(', '));
}

// ---------- glTF binary: z-up base_link -> y-up (x, z, -y) ----------
const G = new Float32Array(nv * 3), GN = new Float32Array(nv * 3);
for (let i = 0; i < nv; i++) {
  G[3 * i] = positions[3 * i]; G[3 * i + 1] = positions[3 * i + 2]; G[3 * i + 2] = -positions[3 * i + 1];
  GN[3 * i] = N[3 * i]; GN[3 * i + 1] = N[3 * i + 2]; GN[3 * i + 2] = -N[3 * i + 1];
}
const ind = nv < 65536 ? Uint16Array.from(out) : out;
const parts = [G, GN, colors, ind].map((a) => Buffer.from(a.buffer ? new Uint8Array(a.buffer, a.byteOffset, a.byteLength) : a));
const views = [], chunks = []; let off = 0;
for (const [i, b] of parts.entries()) {
  views.push({ buffer: 0, byteOffset: off, byteLength: b.length, ...(i < 3 ? { target: 34962 } : { target: 34963 }) });
  const pad = (4 - (b.length % 4)) % 4; chunks.push(b, Buffer.alloc(pad)); off += b.length + pad;
}
const minmax = (a) => { const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity]; for (let i = 0; i < a.length; i++) { lo[i % 3] = Math.min(lo[i % 3], a[i]); hi[i % 3] = Math.max(hi[i % 3], a[i]); } return { min: lo, max: hi }; };
const gltf = {
  asset: { version: '2.0', generator: 'build_lexus.mjs', copyright: 'Lexus model from Autoware sample_vehicle, Apache-2.0' },
  scene: 0, scenes: [{ nodes: [0] }], nodes: [{ mesh: 0, name: 'errol' }],
  meshes: [{ primitives: [{ attributes: { POSITION: 0, NORMAL: 1, COLOR_0: 2 }, indices: 3, material: 0 }] }],
  materials: [{ pbrMetallicRoughness: { metallicFactor: 0, roughnessFactor: 0.7 } }],
  accessors: [
    { bufferView: 0, componentType: 5126, count: nv, type: 'VEC3', ...minmax(G) },
    { bufferView: 1, componentType: 5126, count: nv, type: 'VEC3' },
    { bufferView: 2, componentType: 5126, count: nv, type: 'VEC3' },
    { bufferView: 3, componentType: ind instanceof Uint16Array ? 5123 : 5125, count: ind.length, type: 'SCALAR' },
  ],
  bufferViews: views, buffers: [{ byteLength: off }],
};
let json = Buffer.from(JSON.stringify(gltf)); json = Buffer.concat([json, Buffer.alloc((4 - (json.length % 4)) % 4, 0x20)]);
const bin = Buffer.concat(chunks), head = Buffer.alloc(12), jh = Buffer.alloc(8), bh = Buffer.alloc(8);
head.writeUInt32LE(0x46546c67, 0); head.writeUInt32LE(2, 4); head.writeUInt32LE(12 + 8 + json.length + 8 + bin.length, 8);
jh.writeUInt32LE(json.length, 0); jh.writeUInt32LE(0x4e4f534a, 4); bh.writeUInt32LE(bin.length, 0); bh.writeUInt32LE(0x004e4942, 4);
writeFileSync(glbOut, Buffer.concat([head, jh, json, bh, bin]));
console.log(`wrote ${glbOut} (${((12 + 16 + json.length + bin.length) / 1e6).toFixed(2)} MB)`);
