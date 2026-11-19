// 3D airbrake view: Isaac's FHC-1 module meshes (bay body, interface rings, four flaps on their real hinges) inside a
// the 30kAB layout C airframe from its OpenRocket model. window.AB3D.set(deg) opens the flaps; the 2D renders stay as fallback.
import * as THREE from "three";
import { STLLoader } from "/assets/vendor/three-0.187.0/addons/loaders/STLLoader.js";
import { OrbitControls } from "/assets/vendor/three-0.187.0/addons/controls/OrbitControls.js";

const box = document.getElementById("ab-model");
if (box) (async () => {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true }); } catch (e) { return; }
  if (!renderer.getContext()) return;
  const meta = await (await fetch("/assets/models/ab3d/meta.json")).json();
  const RM = matchMedia("(prefers-reduced-motion: reduce)").matches;
  renderer.setPixelRatio(Math.min(2, devicePixelRatio || 1)); renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.domElement.className = "ab3d"; box.appendChild(renderer.domElement); box.classList.add("gl");
  const scene = new THREE.Scene(), cam = new THREE.PerspectiveCamera(30, 1, 10, 20000);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9a9488, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 2.2); sun.position.set(600, 900, 700); scene.add(sun);
  const rim = new THREE.DirectionalLight(0xbfd4ff, 0.8); rim.position.set(-700, 200, -600); scene.add(rim);

  const M = (c, m = 0.1, r = 0.55) => new THREE.MeshStandardMaterial({ color: c, metalness: m, roughness: r });
  const white = M(0xf3f1ea), ink = M(0x2e1499, 0.4, 0.4), orange = M(0xff5102, 0.05, 0.5), grey = M(0x9aa0a8, 0.6, 0.35), dark = M(0x1e2126, 0.3, 0.6);
  const rocket = new THREE.Group(); scene.add(rocket);

  // the module, in its own frame (mm, z along the axis, forward at low z): turn so forward points up (+y)
  const mod = new THREE.Group(); mod.rotation.x = Math.PI / 2; rocket.add(mod);
  const load = (n) => new Promise((ok) => new STLLoader().load(`/assets/models/ab3d/${n}.stl`, (g) => { g.computeVertexNormals(); ok(g); }));
  const [gBody, gRings, gFlap] = await Promise.all([load("body"), load("rings"), load("flap")]);
  mod.add(new THREE.Mesh(gBody, grey)); mod.add(new THREE.Mesh(gRings, ink));
  const hinge = new THREE.Vector3(...meta.hinge), axis = new THREE.Vector3(...meta.axis).normalize(), pivots = [];
  for (let k = 0; k < 4; k++) {
    const turn = new THREE.Group(); turn.rotation.z = k * Math.PI / 2; mod.add(turn);
    const pivot = new THREE.Group(); pivot.position.copy(hinge); turn.add(pivot);
    const flap = new THREE.Mesh(gFlap, orange); flap.position.copy(hinge).multiplyScalar(-1); pivot.add(flap); pivots.push(pivot);
  }
  // airframe from the 30kAB layout C OpenRocket model (stations in mm from the nose tip; FHC-1 from 1574 to 1734 mm)
  // world y = 1574 - station, so the module frame (z = station - 1574) lines up with the CAD
  const R = 77.5, seg = 72, Y = (s) => 1574 - s;
  const tube = (s0, s1, mat) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(R, R, s1 - s0, seg, 1, true), mat); m.position.y = Y((s0 + s1) / 2); rocket.add(m); };
  tube(950, 1569, white); tube(1739, 3029, white);
  [[1569, 1574], [1734, 1739]].forEach(([a0, a1]) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(R + .4, R + .4, a1 - a0, seg, 1, true), ink); m.position.y = Y((a0 + a1) / 2); rocket.add(m); });
  [1060, 1270, 1480, 2329, 2339].forEach((st) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(R + .3, R + .3, 3, seg, 1, true), grey); m.position.y = Y(st); rocket.add(m); });   // tube joints
  const L = 950, nose = [];   // Haack series, C = 0 (Von Karman)
  for (let i = 0; i <= 60; i++) { const x = L * (i / 60) ** 1.6, th = Math.acos(1 - 2 * x / L); nose.push(new THREE.Vector2(R / Math.sqrt(Math.PI) * Math.sqrt(th - Math.sin(2 * th) / 2), Y(x))); }
  nose.reverse(); rocket.add(new THREE.Mesh(new THREE.LatheGeometry(nose, seg), white));
  [["#FFC908", 0], ["#FF5102", 1], ["#BB0700", 2], ["#2E1499", 3], ["#3E9B5F", 4]].forEach(([c, k]) => {   // the site's colour stripe as livery
    const m = new THREE.Mesh(new THREE.CylinderGeometry(R + .5, R + .5, 22, seg, 1, true), M(c, .05, .5)); m.position.y = Y(1010 + k * 22); rocket.add(m); });
  const tip = []; for (let i = 0; i <= 12; i++) { const x = 140 * i / 12, th = Math.acos(1 - 2 * x / L); tip.push(new THREE.Vector2(R / Math.sqrt(Math.PI) * Math.sqrt(th - Math.sin(2 * th) / 2) + .6, Y(x))); }
  tip.reverse(); rocket.add(new THREE.Mesh(new THREE.LatheGeometry(tip, seg), M("#BB0700", .1, .4)));
  const tail = new THREE.Mesh(new THREE.CylinderGeometry(R, 52.5, 250, seg, 1, true), white); tail.position.y = Y(3029 + 125); rocket.add(tail);
  const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(42, 46, 30, seg), dark); nozzle.position.y = Y(3279 + 15); rocket.add(nozzle);
  // four freeform fins: OpenRocket points (0,0) (347,130) (377,130) (397,-24) mm, aft end 10 mm before the boattail's end
  const sLE = 3279 - 10 - 397, rAt = (st) => st <= 3029 ? R : R - 25 * (st - 3029) / 250;
  const fin = new THREE.Shape([[rAt(sLE), Y(sLE)], [R + 130, Y(sLE + 347)], [R + 130, Y(sLE + 377)], [rAt(sLE + 397), Y(sLE + 397)], [R, Y(3029)]].map(([u, v]) => new THREE.Vector2(u - 1, v)));
  const finGeo = new THREE.ExtrudeGeometry(fin, { depth: 4, bevelEnabled: false }); finGeo.translate(0, 0, -2);
  for (let k = 0; k < 4; k++) { const g = new THREE.Group(); g.add(new THREE.Mesh(finGeo, ink)); g.rotation.y = -k * Math.PI / 2; rocket.add(g); }

  // flight: sky colour by altitude, clouds and streaks moving past at the rocket's speed, air streaming off the flaps
  const skyLo = new THREE.Color("#BFE0F7"), skyHi = new THREE.Color("#25407E"), sky = new THREE.Color(); scene.background = sky;
  const cloudMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .9 }), clouds = [];
  for (let i = 0; i < 16; i++) { const g = new THREE.Group(), a = i * 2.4, r = 1400 + (i * 733) % 2600;
    for (let k = 0; k < 4; k++) { const b = new THREE.Mesh(new THREE.SphereGeometry(140 + (k * 97 + i * 31) % 170, 14, 10), cloudMat); b.position.set(k * 150 - 220, (k % 2) * 60, (k * 53) % 90); b.scale.y = .55; g.add(b); }
    g.position.set(Math.cos(a) * r, -6000 + (i * 811) % 12000, Math.sin(a) * r); scene.add(g); clouds.push(g); }
  const NS = 70, streakPos = new Float32Array(NS * 6), streaks = [];
  for (let i = 0; i < NS; i++) { const a = i * 2.39996, r = 180 + (i * 389) % 900; streaks.push({ x: Math.cos(a) * r, z: Math.sin(a) * r, y: -2500 + (i * 977) % 5000 }); }
  const sGeo = new THREE.BufferGeometry(); sGeo.setAttribute("position", new THREE.BufferAttribute(streakPos, 3));
  const sLines = new THREE.LineSegments(sGeo, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: .55 })); scene.add(sLines);
  const NF = 4 * 46, flowPos = new Float32Array(NF * 3), flow = Array.from({ length: NF }, (_, i) => ({ k: i % 4, life: (i * 0.137) % 1 }));
  const fGeo = new THREE.BufferGeometry(); fGeo.setAttribute("position", new THREE.BufferAttribute(flowPos, 3));
  const fPts = new THREE.Points(fGeo, new THREE.PointsMaterial({ color: 0x9fe3ff, size: 9, transparent: true, opacity: .85, sizeAttenuation: true })); scene.add(fPts);
  let alt = 600, vel = 290, last = performance.now();
  // camera on the module, with the rocket running out of frame; slow orbit, drag to look
  const controls = new OrbitControls(cam, renderer.domElement); controls.target.set(0, -60, 0); controls.enableZoom = true; controls.minDistance = 420; controls.maxDistance = 3200;
  controls.enablePan = false; controls.autoRotate = !RM; controls.autoRotateSpeed = 0.9; controls.enableDamping = true;
  cam.position.set(1050, 380, 1450);
  const size = () => { const w = box.clientWidth, h = box.clientHeight; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); };
  new ResizeObserver(size).observe(box); size();
  let deg = 0, shown = -1, vis = true;
  new IntersectionObserver((es) => { vis = es[0].isIntersecting; }).observe(box);
  window.AB3D = { set(d, a, v) { deg = d; if (a != null) alt = a; if (v != null) vel = Math.max(0, v); } };
  const q = new THREE.Quaternion();
  const frame = (now) => { const dt = Math.min(.05, (now - last) / 1000 || 0); last = now;
    if (vis) { const s = shown < 0 ? deg : shown + (deg - shown) * 0.25; shown = s;
      pivots.forEach((p) => p.quaternion.copy(q.setFromAxisAngle(axis, THREE.MathUtils.degToRad(s))));
      sky.copy(skyLo).lerp(skyHi, Math.max(0, Math.min(1, (alt - 600) / 2600)));
      const run = RM ? 0 : vel * 28 * dt;
      clouds.forEach((c) => { c.position.y -= run; if (c.position.y < -6500) c.position.y += 13000; });
      streaks.forEach((st, i) => { st.y -= run * 1.6; if (st.y < -2500) st.y += 5000; const len = 40 + vel * 2.2;
        streakPos.set([st.x, st.y, st.z, st.x, st.y + len, st.z], i * 6); });
      sGeo.attributes.position.needsUpdate = true; sLines.material.opacity = Math.min(.6, vel / 400);
      const open = THREE.MathUtils.degToRad(s), hz = meta.hinge[2];
      flow.forEach((f, i) => { f.life += dt * (0.6 + vel / 250); if (f.life > 1) f.life -= 1;
        const az = THREE.MathUtils.degToRad(meta.flapAz0 + f.k * 90), rr = R + 105 * Math.sin(open) + f.life * 160 * Math.sin(open), yy = -hz - 105 * Math.cos(open) - f.life * (500 + vel * 3);
        flowPos.set([Math.cos(az) * rr, yy, Math.sin(az) * rr], i * 3); });
      fGeo.attributes.position.needsUpdate = true; fPts.material.opacity = s > 3 ? Math.min(.9, s / 30) * Math.min(1, vel / 60) : 0;
      if (!RM) { rocket.rotation.z = Math.sin(now / 900) * .012; rocket.rotation.x = Math.sin(now / 1300) * .008; }
      controls.update(); renderer.render(scene, cam); } requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
})();
