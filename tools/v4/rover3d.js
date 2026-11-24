// Rover's-eye 3D inset: the same MID-360 returns as the map (window.__cloudQ), lifted to their heights, from a chase camera.
import * as THREE from "three";
import { STLLoader } from "/assets/vendor/three-0.187.0/addons/loaders/STLLoader.js";
const box = document.getElementById("eye");
if (box) (() => {
  let renderer; try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { box.hidden = true; return; }
  if (!renderer.getContext()) { box.hidden = true; return; }
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1)); box.appendChild(renderer.domElement);
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(55, 1, 0.05, 200);
  const MAX = 90000, pos = new Float32Array(MAX * 3), col = new Float32Array(MAX * 3);
  const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3)); geo.setAttribute("color", new THREE.BufferAttribute(col, 3)); geo.setDrawRange(0, 0);
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ size: 0.06, vertexColors: true, sizeAttenuation: true })); scene.add(pts);
  const grid = new THREE.GridHelper(60, 60, 0x9aa0a8, 0xd2cfc6); grid.material.transparent = true; grid.material.opacity = 0.35; scene.add(grid);
  // Theseus V from its CAD (mm, +X forward, Z up), the Theseus VI mount left out; wheel centres sit 0.15 m above the ground
  const rover = new THREE.Group(); scene.add(rover);
  const m = (c, met = .2, r = .6) => new THREE.MeshStandardMaterial({ color: c, metalness: met, roughness: r });
  const cad = new THREE.Group(); cad.rotation.x = -Math.PI / 2; cad.scale.setScalar(0.001); cad.position.y = 0.155; rover.add(cad);
  const COL = { wheels: m(0x2b2440), legs: m(0xb9bec2, .5, .4), chassis: m(0xf3f1ea), bucket: m(0xff5102, .1, .5), arm: m(0x9aa0a8, .5, .4), masts: m(0x9aa0a8, .5, .4),
                camera_bridge: m(0x1e2126), lidar: m(0xffc908), other_sensors: m(0x5d626b) };
  Object.entries(COL).forEach(([g, mat]) => new STLLoader().load(`theseus3d/${g}.stl`, (geo) => { geo.computeVertexNormals(); cad.add(new THREE.Mesh(geo, mat)); }));
  scene.add(new THREE.DirectionalLight(0xffffff, 1.4).translateX(3).translateY(6).translateZ(2));
  scene.add(new THREE.HemisphereLight(0xffffff, 0x887766, 2));
  const tmp = new THREE.Color(); let n = 0, head = 0, spin = 0;
  const parse = (c) => { const mm = c.match(/[\d.]+/g); if (!mm) return [1, 1, 1]; return [mm[0] / 255, mm[1] / 255, mm[2] / 255]; };
  const size = () => { const w = box.clientWidth, h = box.clientHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); };
  new ResizeObserver(size).observe(box); size();
  let vis = true; new IntersectionObserver((es) => { vis = es[0].isIntersecting; }).observe(box);
  const RM = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const frame = (t) => {
    if (window.__cloudReset) { window.__cloudReset = false; n = 0; head = 0; geo.setDrawRange(0, 0); }
    const Q = window.__cloudQ || [];
    for (let q = 0; q < Q.length; q++) { const [x, y, z, c] = Q[q], i = head % MAX; pos[i * 3] = x; pos[i * 3 + 1] = z; pos[i * 3 + 2] = y;   // drain in O(n), then truncate once
      const [r, g, b] = parse(c); tmp.setRGB(r, g, b, THREE.SRGBColorSpace); col[i * 3] = tmp.r; col[i * 3 + 1] = tmp.g; col[i * 3 + 2] = tmp.b; head++; n = Math.min(MAX, n + 1); }
    Q.length = 0;
    geo.attributes.position.needsUpdate = true; geo.attributes.color.needsUpdate = true; geo.setDrawRange(0, n);
    const R = window.__rover;
    if (R && vis) { rover.position.set(R.x, 0, R.y); rover.rotation.y = -R.h;
      spin = RM ? 0 : Math.sin(t / 7000) * 0.8; const back = -R.h + Math.PI + spin, d = 4.2;
      cam.position.set(R.x + Math.cos(back) * d * Math.cos(0) , 2.6, R.y - Math.sin(back) * d);
      cam.position.set(R.x - Math.cos(R.h + spin) * d, 2.6, R.y - Math.sin(R.h + spin) * d);
      cam.lookAt(R.x + Math.cos(R.h) * 2, 0.2, R.y + Math.sin(R.h) * 2); renderer.render(scene, cam); }
    requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
})();
