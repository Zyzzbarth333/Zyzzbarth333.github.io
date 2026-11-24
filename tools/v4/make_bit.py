"""Make live4-rover-bit.js from live4-rover.js: the same autonomy, as a small bit character at v3's size (19 Nov 2026).

Isaac: the to-scale rover reads as stuck on things; either act exactly like the real one, or be a 'bit' character
like v3. This keeps v4's brain (cameras, coverage exploration, A* round a footprint, LIVO cloud, finds, eggs, the 3D
inset) and changes only how it looks and moves:
  - the world is zoomed out: 14 px cells of 0.45 m (v4: 12 px of 0.15 m), so the rover is about 30 px across like v3,
    and the cameras, footprint, rocks and blind ring keep their real proportions to it;
  - it drives like v3: quick turns on the spot, no slow arcs, a brisker pace;
  - v3's drawn rover and its two-link grabber replace the CAD sprite and bucket.
Rerun after any change to live4-rover.js:  python3 -I make_bit.py && python3 -I build7.py live4-bit live4-rover-bit.js
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
s = (HERE / 'live4-rover.js').read_text()


def swap(old, new, n=1):
    global s
    assert s.count(old) == n, (s.count(old), old[:70])
    s = s.replace(old, new)


# scale and pace
swap('const CELL = 12, MPC = 0.15, SPEED = 0.6 / MPC;', 'const CELL = 14, MPC = 0.45, SPEED = 3.6;   /* bit mode: 0.45 m cells, v3 pace */')
# reach distances were in 15 cm cells
swap("< (task.type === 'scan' ? 8 : 4.2))", "< (task.type === 'scan' ? 3 : 1.7))")
# turn on the spot while acting, like v3 (v4 arcs round, which reads as circling at this size)
swap("if (Math.abs(da) > .05) { rh += Math.sign(da) * Math.min(Math.abs(da), dt * .9); rx += Math.cos(rh) * dt * .6; ry += Math.sin(rh) * dt * .6; }   // arcs, never a spin on the spot",
     "rh += da * Math.min(1, dt * 8);   // bit mode: turns on the spot, like v3")
# path following: quick turns, no slow-down in big turns
swap("turn = Math.abs(da) > .9 ? .35 : 1;", "turn = 1;")
swap("rh += Math.sign(da) * Math.min(Math.abs(da), dt * 1.6);", "rh += Math.max(-1, Math.min(1, da)) * Math.min(1, dt * 6);")
# dust sprites at v3's pace and reach (they were tuned in 15 cm cells)
swap("const sp = (power ? 2 : 3.2) * dt", "const sp = (power ? 1.6 : 2.6) * dt")
swap("if (d < 3) { if (power)", "if (d < 1.2) { if (power)")

# the rover itself: v3's bit character and grabber in place of the CAD sprite and bucket
a = s.index('      // Theseus V from its CAD, to scale; the arm and bucket reach out for pickups\n')
b = s.index('      ctx.restore();\n', a) + len('      ctx.restore();\n')
BIT = r"""      // bit mode: v3's rover and its two-link grabber (v4's scan flash on the camera wedges is kept)
      let bx = 0, by = 0;
      if (act) { const p = (now - act.t0) / (act.type === 'pick' ? 2200 : 1100), it = act.it, ix = (it.x + .5) * CELL, iy = (it.y + .5) * CELL, ox = rx * CELL + Math.cos(rh) * 10, oy = ry * CELL + Math.sin(rh) * 10;
        if (act.type === 'bump') { const k2 = Math.sin(Math.PI * Math.min(1, p * 1.4)) * 7; bx = Math.cos(rh) * k2; by = Math.sin(rh) * k2; }
        if (act.type === 'scan') { const a2 = Math.max(0, 1 - Math.abs(p - .4) * 3); for (const c of CAM) { const cx = (rx + Math.cos(rh) * c.x - Math.sin(rh) * c.y) * CELL, cy = (ry + Math.sin(rh) * c.x + Math.cos(rh) * c.y) * CELL;
          ctx.fillStyle = `rgba(255,255,255,${a2 * .8})`; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.arc(cx, cy, CAM_R * CELL, rh - CAM_FOV / 2, rh + CAM_FOV / 2); ctx.closePath(); ctx.fill(); } }
        if (act.type === 'pick') {   // a two-link arm reaches out, grips and brings the find aboard
          const reach = p < .35 ? p / .35 : p < .5 ? 1 : Math.max(0, 1 - (p - .5) / .45), tx = ox + (ix - ox) * reach, ty = oy + (iy - oy) * reach;
          const mx = (ox + tx) / 2 - Math.sin(rh) * 12 * reach, my = (oy + ty) / 2 + Math.cos(rh) * 12 * reach;
          ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(mx, my); ctx.lineTo(tx, ty); ctx.stroke();
          ctx.strokeStyle = C.yel; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(mx, my); ctx.lineTo(tx, ty); ctx.stroke();
          ctx.fillStyle = C.ind; ctx.beginPath(); ctx.arc(mx, my, 3.5, 0, 7); ctx.fill();
          const grip = p > .3 ? 2 : 6; ctx.strokeStyle = C.ink; ctx.lineWidth = 2.5; const ang = Math.atan2(ty - my, tx - mx);
          for (const s2 of [-1, 1]) { ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(tx + Math.cos(ang + s2 * .6) * 7, ty + Math.sin(ang + s2 * .6) * 7); ctx.lineTo(tx + Math.cos(ang) * 9 + Math.cos(ang + s2 * 1.57) * grip, ty + Math.sin(ang) * 9 + Math.sin(ang + s2 * 1.57) * grip); ctx.stroke(); }
          if (p > .5) { const sc = Math.max(.2, 1 - (p - .5) * 1.6), fake = { ...it, x: tx / CELL - .5, y: ty / CELL - .5 }; ctx.save(); ctx.globalAlpha = sc;
            it.kind === 'aruco' ? drawAruco(fake, 16 * sc) : drawFind(fake, 14 * sc, now); ctx.restore(); }
          ctx.lineCap = 'butt'; } }
      ctx.save(); ctx.translate(rx * CELL + bx, ry * CELL + by); ctx.rotate(rh);
      ctx.fillStyle = C.ink; for (const [wx, wy] of [[-9, -11], [5, -11], [-9, 7], [5, 7]]) ctx.fillRect(wx, wy, 8, 4);
      ctx.fillStyle = C.ind; ctx.fillRect(-11, -8, 22, 16); ctx.fillStyle = C.yel; ctx.fillRect(4, -4, 6, 8); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-3, 0, 3, 0, 7); ctx.fill();
      ctx.restore();
"""
s = s[:a] + BIT + s[b:]
s = '/* GENERATED by make_bit.py from live4-rover.js: edit that file (or make_bit.py), then rerun. */\n' + s
(HERE / 'live4-rover-bit.js').write_text(s)
print('wrote live4-rover-bit.js')
