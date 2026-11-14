// Fade elements in as they scroll into view. The <html> element gets the
// "js" class from an inline script in the head, so nothing is hidden when
// scripts are off. Reduced-motion users get no transition (see style.css).
(function () {
    window.revealReady = true;   // tells the head's fallback timer not to unhide
    var items = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) {
        items.forEach(function (el) { el.classList.add('is-visible'); });
        return;
    }
    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                io.unobserve(entry.target);
            }
        });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
})();

// Embeds that can't work on a phone load only on wider screens (the page shows a note and a link on phones).
document.querySelectorAll('.figure-embed[data-desktop-only] iframe[data-src]').forEach(function (frame) {
    var wide = window.matchMedia('(min-width: 600px)');
    function load() { if (wide.matches && !frame.getAttribute('src')) frame.setAttribute('src', frame.dataset.src); }
    load();
    if (wide.addEventListener) wide.addEventListener('change', load);
});

// Size each embedded figure to its content (same-origin pages under assets/figures/).
document.querySelectorAll('.figure-embed iframe:not([data-fixed])').forEach(function (frame) {
    function fit() {
        try {
            var doc = frame.contentDocument;
            if (doc && doc.body) {
                // The frame takes the figure's whole height, so the figure never needs a scrollbar of its own.
                // Round up, since a fraction of a pixel left over is enough to show one.
                var root = doc.documentElement;
                root.style.overflow = 'hidden';
                var h = Math.ceil(root.getBoundingClientRect().height);
                if (root.scrollHeight > frame.clientHeight + 1) h = Math.max(h, root.scrollHeight);
                frame.style.height = h + 'px';
                frame.style.aspectRatio = 'auto';
            }
        } catch (e) { /* keep the CSS aspect ratio */ }
    }
    frame.addEventListener('load', function () {
        fit();
        try {
            var doc = frame.contentDocument, ro = new ResizeObserver(fit);
            ro.observe(doc.documentElement);
            ro.observe(doc.body);
            if (doc.fonts) doc.fonts.ready.then(fit);
        } catch (e) {}
    });
});

// Meet the board: a marker and its card light together on hover or focus.
document.querySelectorAll('.board-map').forEach(function (map) {
    var items = map.querySelectorAll('[data-part]');
    function light(id) {
        items.forEach(function (el) {
            if (id && el.getAttribute('data-part') === id) el.setAttribute('data-on', '');
            else el.removeAttribute('data-on');
        });
    }
    items.forEach(function (el) {
        var id = el.getAttribute('data-part');
        el.addEventListener('mouseenter', function () { light(id); });
        el.addEventListener('focus', function () { light(id); });
        el.addEventListener('click', function () { light(id); });
    });
    map.addEventListener('mouseleave', function () { light(null); });
    map.addEventListener('focusout', function (ev) { if (!map.contains(ev.relatedTarget)) light(null); });
});

// Card icons with SMIL motion (the ENGG1100 vehicle's spray): paused until the card is hovered or focused.
(function () {
    var still = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    document.querySelectorAll('.card').forEach(function (card) {
        var svg = card.querySelector('.icon svg');
        if (!svg || !svg.pauseAnimations) return;
        svg.pauseAnimations();
        if (still) return;
        var go = function () { svg.unpauseAnimations(); };
        var stop = function () { svg.pauseAnimations(); };
        card.addEventListener('mouseenter', go);
        card.addEventListener('mouseleave', stop);
        card.addEventListener('focusin', go);
        card.addEventListener('focusout', stop);
    });
})();

// Weather station card: one wind model drives both instruments. Hovering or focusing the card turns the
// wind on, with gusts in speed and direction; leaving it lets the wind die away.
//  - Cup anemometer: its speed follows the wind with a lag that shrinks as the wind rises (a cup
//    anemometer's distance constant), so it spins up briskly and coasts down slowly.
//  - Wind vane: the wind's torque on the tail fin grows with speed squared and the aerodynamic damping
//    with speed, so it swings round to point into the wind, overshoots a little and settles; with no
//    wind only bearing friction acts, and it stays where it stopped.
// The icon gives each part's projected axes (ex, ey, ez), depth weights (dep) and pivot (o).
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var nums = function (el, k) { return el.getAttribute('data-' + k).split(' ').map(Number); };
    document.querySelectorAll('.card').forEach(function (card) {
        var rotor = card.querySelector('.ws-rotor'), vane = card.querySelector('.ws-vane');
        if (!rotor || !vane) return;
        // anemometer
        var rx = nums(rotor, 'ex'), ry = nums(rotor, 'ey'), rdep = nums(rotor, 'dep'), ro = nums(rotor, 'o');
        var hub = rotor.querySelector('.ws-hub'), cups = [].slice.call(rotor.querySelectorAll('.ws-cup'));
        // vane
        var vo = nums(vane, 'o'), vx = nums(vane, 'ex'), vy = nums(vane, 'ey'), vz = nums(vane, 'ez'), vdep = nums(vane, 'dep');
        var geo = JSON.parse(vane.getAttribute('data-geo'));
        var fin = vane.querySelector('.ws-fin'), shaft = vane.querySelector('.ws-shaft'), head = vane.querySelector('.ws-head'), cap = vane.querySelector('.ws-cap');
        var CUPS = 2.2 * 2 * Math.PI;                 // cup speed (rad/s) at full wind
        var STIFF = 60, AERO = 5.5, BEARING = 0.9;    // vane: torque, aerodynamic and bearing damping
        var wind = 0, windTarget = 0, base = 2.6, clock = 0;
        var spin = 0, cupAngle = 0, psi = Number(vane.getAttribute('data-psi')), rate = 0;
        var frame = 0, last = 0;
        function drawRotor() {
            var placed = cups.map(function (cup, i) {
                var a = cupAngle + i * 2 * Math.PI / 3, c = Math.cos(a), s = Math.sin(a);
                var x = rx[0] * c + ry[0] * s, y = rx[1] * c + ry[1] * s;
                cup.setAttribute('transform', 'translate(' + x.toFixed(2) + ' ' + y.toFixed(2) + ')');
                var arm = cup.querySelector('.ws-arm');
                arm.setAttribute('x1', (ro[0] - x).toFixed(2));
                arm.setAttribute('y1', (ro[1] - y).toFixed(2));
                return { cup: cup, depth: rdep[0] * c + rdep[1] * s };
            }).sort(function (p, q) { return p.depth - q.depth; });
            placed.forEach(function (p) { if (p.depth < 0) rotor.appendChild(p.cup); });
            rotor.appendChild(hub);
            placed.forEach(function (p) { if (p.depth >= 0) rotor.appendChild(p.cup); });
        }
        function at(q) {
            var c = Math.cos(psi), s = Math.sin(psi), X = q[0] * c - q[1] * s, Y = q[0] * s + q[1] * c;
            return [vo[0] + vx[0] * X + vy[0] * Y + vz[0] * q[2], vo[1] + vx[1] * X + vy[1] * Y + vz[1] * q[2]];
        }
        function path(pts) { return 'M' + pts.map(function (q) { var p = at(q); return p[0].toFixed(2) + ' ' + p[1].toFixed(2); }).join(' L') + ' Z'; }
        function drawVane() {
            fin.setAttribute('d', path(geo.fin));
            head.setAttribute('d', path(geo.head));
            var a = at(geo.shaft[0]), b = at(geo.shaft[1]);
            shaft.setAttribute('x1', a[0].toFixed(2)); shaft.setAttribute('y1', a[1].toFixed(2));
            shaft.setAttribute('x2', b[0].toFixed(2)); shaft.setAttribute('y2', b[1].toFixed(2));
            // the tail fin is drawn last when the tail is the nearer end
            var tailNear = -(vdep[0] * Math.cos(psi) + vdep[1] * Math.sin(psi)) > 0;
            if (tailNear) { vane.appendChild(shaft); vane.appendChild(head); vane.appendChild(cap); vane.appendChild(fin); }
            else { vane.appendChild(fin); vane.appendChild(shaft); vane.appendChild(head); vane.appendChild(cap); }
        }
        function step(dt) {
            clock += dt;
            var gust = windTarget ? 1 + 0.18 * Math.sin(1.3 * clock) + 0.1 * Math.sin(3.7 * clock) : 0;
            wind += (windTarget * gust - wind) * (1 - Math.exp(-dt / (windTarget ? 0.6 : 1.2)));
            var from = base + 0.22 * Math.sin(0.8 * clock) + 0.1 * Math.sin(2.3 * clock);   // gusty direction (rad)
            var lag = 0.35 / (wind + 0.12);
            spin += (CUPS * wind - spin) * (1 - Math.exp(-dt / lag));
            cupAngle -= spin * dt;
            var err = Math.atan2(Math.sin(psi - from), Math.cos(psi - from));
            var accel = -STIFF * wind * wind * Math.sin(err) - (AERO * wind + BEARING) * rate;
            rate += accel * dt;
            psi += rate * dt;
        }
        function tick(now) {
            var dt = last ? Math.min(0.05, (now - last) / 1000) : 0;
            last = now;
            for (var n = Math.max(1, Math.ceil(dt / 0.008)), i = 0; i < n; i++) step(dt / n);
            drawRotor();
            drawVane();
            if (windTarget || wind > 0.01 || spin > 0.05 || Math.abs(rate) > 0.01) frame = requestAnimationFrame(tick);
            else { frame = 0; last = 0; wind = 0; spin = 0; rate = 0; }
        }
        function set(on) {
            if (on && !windTarget) base += (Math.random() - 0.5) * 1.6;   // each new breeze comes from a slightly new direction
            windTarget = on ? 1 : 0;
            if (!frame) { last = 0; frame = requestAnimationFrame(tick); }
        }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// OSIRIS card: the Black Pill lifts out of its sockets on a spring while the card is hovered or focused and
// drops back with a small bounce when it is left. Once it is seated again the board powers up on its status
// LEDs: 3V3 and PWR come on, LOG and RADIO flicker, ARM and FLT flash once in self-test, HB blinks, then it
// all fades. Unplugging it again cuts the LEDs at once.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.card').forEach(function (card) {
        var mod = card.querySelector('.os-module');
        if (!mod) return;
        var lift = mod.getAttribute('data-lift').split(' ').map(Number);
        var leds = {};
        [].forEach.call(card.querySelectorAll('.os-led'), function (el) { leds[el.getAttribute('data-led')] = el; });
        var x = 0, v = 0, goal = 0, last = 0, frame = 0, lifted = false, timers = [];
        var STIFF = 95, DAMP = 9.5;                       // underdamped: it overshoots and settles, like a part dropped onto pins
        function led(name, on) { if (leds[name]) leds[name].classList.toggle('on', on); }
        function allOff() { timers.forEach(clearTimeout); timers = []; Object.keys(leds).forEach(function (k) { led(k, false); }); }
        function at(ms, fn) { timers.push(setTimeout(fn, ms)); }
        function boot() {
            allOff();
            at(0, function () { led('3v3', true); });
            at(120, function () { led('pwr', true); });
            at(300, function () { led('arm', true); led('flt', true); });
            at(520, function () { led('arm', false); led('flt', false); });
            [380, 460, 640, 760, 1100, 1180].forEach(function (t, i) { at(t, function () { led(i % 2 ? 'radio' : 'log', i < 4 ? i % 2 === 0 : i % 2 === 1); }); });
            [700, 1200, 1700, 2200].forEach(function (t) { at(t, function () { led('hb', true); }); at(t + 160, function () { led('hb', false); }); });
            at(2700, allOff);
        }
        function place() {
            var t = 'translate(' + (lift[0] * x).toFixed(2) + ' ' + (lift[1] * x).toFixed(2) + ')';
            Math.abs(x) > 0.002 ? mod.setAttribute('transform', t) : mod.removeAttribute('transform');
        }
        function tick(now) {
            var dt = last ? Math.min(0.033, (now - last) / 1000) : 0; last = now;
            for (var i = 0; i < 4; i++) { var a = STIFF * (goal - x) - DAMP * v; v += a * dt / 4; x += v * dt / 4; }
            if (x < 0 && goal === 0) { x = -x * 0.35; v = -v * 0.35; }   // the pins bottom out in the sockets: a small bounce
            if (x > 0.6) lifted = true;
            place();
            if (Math.abs(goal - x) < 0.002 && Math.abs(v) < 0.01) {
                x = goal; v = 0; place(); frame = 0; last = 0;
                if (goal === 0 && lifted) { lifted = false; boot(); }
                return;
            }
            frame = requestAnimationFrame(tick);
        }
        function set(on) {
            goal = on ? 1 : 0;
            if (on) allOff();
            if (!frame) { last = 0; frame = requestAnimationFrame(tick); }
        }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// Theseus card: the rover's autonomy loop. Hovering or focusing the card spins the LiDAR up; its scan sweeps
// the ground and each return (craters, rocks and the e-stop wall of the real ARCh 2026 arena around the start
// pose) appears as the beam passes, building the map. Once most of it is mapped a path to a frontier appears
// and the rover drives along it. Leaving the card spins the LiDAR down, the map fades, and the rover rolls
// back to its start. The icon gives the map's origin and its projected metre vectors (ex, ey).
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var nums = function (el, k) { return el.getAttribute('data-' + k).split(' ').map(Number); };
    document.querySelectorAll('.card').forEach(function (card) {
        var map = card.querySelector('.rv-map'), drive = card.querySelector('.rv-drive');
        if (!map || !drive) return;
        var O = nums(map, 'o'), ex = nums(map, 'ex'), ey = nums(map, 'ey'), R = Number(map.getAttribute('data-r'));
        var fwd = nums(drive, 'fwd'), lid = nums(drive, 'lid');
        var beam = card.querySelector('.rv-beam'), path = map.querySelector('.rv-path'), goal = map.querySelector('.rv-goal');
        var rets = [].slice.call(map.querySelectorAll('.rv-ret')).map(function (el) { return { el: el, a: Number(el.getAttribute('data-a')), v: 0, shown: -1 }; });
        var TAU = 2 * Math.PI, spin = 0, target = 0, ang = 0, pathAmt = 0, travel = 0, speed = 0, last = 0, frame = 0;
        var pt = function (a, r) { return [O[0] + (ex[0] * Math.cos(a) + ey[0] * Math.sin(a)) * r, O[1] + (ex[1] * Math.cos(a) + ey[1] * Math.sin(a)) * r]; };
        function tick(now) {
            var dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
            spin += (target - spin) * (1 - Math.exp(-dt / (target ? 0.45 : 1.1)));
            var prev = ang; ang += spin * TAU * 1.3 * dt;                       // up to 1.3 turns a second
            // the beam fans out from the LiDAR head (it rides on the rover) to the ground it is hitting
            var hx = lid[0] + fwd[0] * travel, hy = lid[1] + fwd[1] * travel;
            var p = 'M' + hx.toFixed(1) + ' ' + hy.toFixed(1);
            for (var i = 0; i <= 8; i++) { var q = pt(ang - 0.45 + 0.45 * i / 8, R); p += ' L' + q[0].toFixed(1) + ' ' + q[1].toFixed(1); }
            beam.setAttribute('d', p + ' Z'); beam.style.opacity = (0.85 * spin).toFixed(3);
            var seen = 0;
            rets.forEach(function (r) {
                if (target && spin > 0.2) {
                    var d = ((r.a - prev) % TAU + TAU) % TAU;
                    if (d <= ang - prev + 1e-6) r.v = 1;                        // the beam swept past it this frame
                } else if (!target) r.v *= Math.exp(-dt / 0.8);
                if (r.v > 0.5) seen++;
                if (Math.abs(r.v - r.shown) > 0.02) { r.el.style.opacity = r.v.toFixed(2); r.shown = r.v; }
            });
            var planned = target && seen > rets.length * 0.6;
            pathAmt += ((planned ? 1 : 0) - pathAmt) * (1 - Math.exp(-dt / 0.35));
            path.style.opacity = pathAmt.toFixed(2); goal.style.opacity = pathAmt.toFixed(2);
            var want = planned && pathAmt > 0.8 ? 0.45 : 0;                   // m/s along the path's first leg
            speed += (want - speed) * (1 - Math.exp(-dt / 0.5));
            travel = Math.min(1.6, travel + speed * dt);
            if (!target && spin < 0.05) travel *= Math.exp(-dt / 0.7);           // back to the start once idle
            var t = 'translate(' + (fwd[0] * travel).toFixed(2) + ' ' + (fwd[1] * travel).toFixed(2) + ')';
            travel > 0.002 ? drive.setAttribute('transform', t) : drive.removeAttribute('transform');
            var busy = target || spin > 0.01 || travel > 0.002 || rets.some(function (r) { return r.v > 0.02; });
            if (busy) frame = requestAnimationFrame(tick); else { frame = 0; last = 0; }
        }
        function set(on) { target = on ? 1 : 0; if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// HAVOC-2 card: a flight shaped like HAVOC-2's first flight (flight-data ANALYSIS.md): a short boost with the
// motor lit, a coast that slows to apogee, then a fall with no parachute, held to a steady speed by drag (about
// 13 m/s on the real flight, roughly a third of the climb's average), down to the pad. Hovering or focusing the
// card launches it and it flies again after each landing; leaving lets the flight in progress finish and land.
// Units are the icon's world units (data-up is one unit of climb on screen) and seconds.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.card').forEach(function (card) {
        var body = card.querySelector('.rk-lift'), flame = card.querySelector('.rk-flame');
        if (!body || !body.getAttribute('data-up')) return;
        var up = body.getAttribute('data-up').split(' ').map(Number);
        var G = 160, THRUST = 720, BURN = 0.25, K_UP = 0.0015, V_FALL = 22;   // nose-first going up, tumbling coming down
        var K_DOWN = G / (V_FALL * V_FALL);
        var h = 0, v = 0, burn = 0, phase = 'pad', want = false, wait = 0, last = 0, frame = 0;
        function place() {
            h > 0.01 ? body.setAttribute('transform', 'translate(' + (up[0] * h).toFixed(2) + ' ' + (up[1] * h).toFixed(2) + ')') : body.removeAttribute('transform');
            if (flame) flame.style.opacity = phase === 'boost' ? '1' : '';
        }
        function tick(now) {
            var dt = last ? Math.min(0.033, (now - last) / 1000) : 0; last = now;
            if (phase === 'pad' && want) { wait -= dt; if (wait <= 0) { phase = 'boost'; burn = 0; } }
            for (var i = 0; i < 4 && phase !== 'pad'; i++) {
                var s = dt / 4, a;
                if (phase === 'boost') { a = THRUST - G - K_UP * v * v; burn += s; if (burn >= BURN) phase = 'coast'; }
                else if (phase === 'coast') { a = -G - K_UP * v * v; if (v <= 0) phase = 'fall'; }
                else a = -G - K_DOWN * v * Math.abs(v);
                v += a * s; h += v * s;
                if (h <= 0 && phase === 'fall') { h = 0; v = 0; phase = 'pad'; wait = 0.7; }
            }
            place();
            if (phase !== 'pad' || want) frame = requestAnimationFrame(tick); else { frame = 0; last = 0; }
        }
        function set(on) { want = on; if (on && phase === 'pad') wait = Math.min(wait, 0.15); if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// Orrery card: a small motor turns the orrery's gear train while the card is hovered or focused. Earth goes round
// once in 4 s at full speed and Mars at its real rate, 1/1.88 of Earth's. Leaving cuts the motor and the train
// coasts to a stop against its bearings (viscous drag plus a little dry friction), so it slows and then stops.
// Each planet has a copy behind the mast and one in front; the copy for the planet's half of the ring is shown.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.card').forEach(function (card) {
        var backs = [].slice.call(card.querySelectorAll('.or-planet[data-ring]'));
        if (!backs.length) return;
        var planets = backs.map(function (back) {
            var cls = back.classList.contains('or-earth') ? '.or-earth' : '.or-mars';
            var xy = back.getAttribute('data-ring').split(' ').map(Number), ring = [];
            for (var i = 0; i < xy.length; i += 2) ring.push([xy[i], xy[i + 1]]);
            return { back: back, front: card.querySelector(cls + '[data-side="front"]'), ring: ring,
                     behind: back.getAttribute('data-behind'), rate: Number(back.getAttribute('data-rate')) };
        });
        var TAU = 2 * Math.PI, W = TAU / 4, RISE = 0.5, DRAG = 0.9, DRY = 0.35;
        var phi = 0, w = 0, on = false, last = 0, frame = 0;
        function place() {
            planets.forEach(function (p) {
                var N = p.ring.length, f = (((phi * p.rate) / TAU) % 1 + 1) % 1 * N;
                var i = Math.floor(f) % N, j = (i + 1) % N, u = f - Math.floor(f);
                var x = p.ring[i][0] + (p.ring[j][0] - p.ring[i][0]) * u, y = p.ring[i][1] + (p.ring[j][1] - p.ring[i][1]) * u;
                var tr = 'translate(' + x.toFixed(2) + ' ' + y.toFixed(2) + ')', behind = p.behind.charAt(Math.round(f) % N) === '1';
                p.back.setAttribute('transform', tr); p.back.setAttribute('visibility', behind ? 'visible' : 'hidden');
                if (p.front) { p.front.setAttribute('transform', tr); p.front.setAttribute('visibility', behind ? 'hidden' : 'visible'); }
            });
        }
        function tick(now) {
            var dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
            if (on) w += (W - w) * (1 - Math.exp(-dt / RISE));
            else w = Math.max(0, w - (DRAG * w + DRY) * dt);
            phi += w * dt;
            place();
            if (on || w > 0) frame = requestAnimationFrame(tick); else { frame = 0; last = 0; }
        }
        function set(v) { on = v; if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// Camera mount card: hovering or focusing makes the camera pan slowly from side to side on its ball joint, as if
// someone were aiming it; leaving lets it swing back to centre on a damped spring that overshoots a little and
// settles. The icon has the camera drawn at 13 angles 4 degrees apart; the one nearest the spring's angle shows.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.card').forEach(function (card) {
        var frames = [].slice.call(card.querySelectorAll('.cm-frame[data-deg]'));
        if (!frames.length) return;
        var degs = frames.map(function (f) { return Number(f.getAttribute('data-deg')); });
        var SWING = 22, PERIOD = 3.6;                    // pan amplitude (degrees) and period (s) while hovered
        var a = 0, v = 0, clock = 0, on = false, shown = -1, last = 0, frame = 0;
        function show() {
            var best = 0;
            degs.forEach(function (d, i) { if (Math.abs(d - a) < Math.abs(degs[best] - a)) best = i; });
            if (best === shown) return;
            frames.forEach(function (f, i) { f.setAttribute('visibility', i === best ? 'visible' : 'hidden'); });
            shown = best;
        }
        function tick(now) {
            var dt = last ? Math.min(0.033, (now - last) / 1000) : 0; last = now;
            clock += on ? dt : 0;
            var goal = on ? SWING * Math.sin(2 * Math.PI * clock / PERIOD) : 0;
            var K = on ? 30 : 26, C = on ? 9 : 4.2;      // following: well damped; letting go: underdamped (~25% overshoot)
            for (var i = 0; i < 4; i++) { var acc = K * (goal - a) - C * v; v += acc * dt / 4; a += v * dt / 4; }
            show();
            if (on || Math.abs(a) > 0.3 || Math.abs(v) > 0.5) frame = requestAnimationFrame(tick);
            else { a = 0; v = 0; show(); frame = 0; last = 0; }
        }
        function set(v2) { on = v2; if (on) clock = Math.asin(Math.max(-1, Math.min(1, a / SWING))) * PERIOD / (2 * Math.PI); if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// Airbrakes card: FHC-1's four flaps open on a spring while the card is hovered or focused, then trim slowly in and out
// the way a controller holds a rocket to its target apogee; leaving folds them shut. The icon has the flaps rendered
// from the CAD at 6 angles, 0 to 80 degrees (the design's full deflection); the angle nearest the spring's is shown.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('.card').forEach(function (card) {
        var groups = [].slice.call(card.querySelectorAll('.ab-flaps[data-deg]'));
        if (!groups.length) return;
        var degs = [];
        groups.forEach(function (g) { var d = Number(g.getAttribute('data-deg')); if (degs.indexOf(d) < 0) degs.push(d); });
        var a = 0, v = 0, clock = 0, on = false, shown = -1, last = 0, frame = 0;
        function show() {
            var best = degs.reduce(function (b, d) { return Math.abs(d - a) < Math.abs(b - a) ? d : b; }, degs[0]);
            if (best === shown) return;
            groups.forEach(function (g) { g.setAttribute('visibility', Number(g.getAttribute('data-deg')) === best ? 'visible' : 'hidden'); });
            shown = best;
        }
        function tick(now) {
            var dt = last ? Math.min(0.033, (now - last) / 1000) : 0; last = now;
            clock += on ? dt : 0;
            var goal = on ? 50 + 14 * Math.sin(2 * Math.PI * clock / 2.6) : 0;
            for (var i = 0; i < 4; i++) { var acc = 45 * (goal - a) - 11 * v; v += acc * dt / 4; a = Math.max(0, Math.min(80, a + v * dt / 4)); }
            show();
            if (on || a > 0.5 || Math.abs(v) > 0.5) frame = requestAnimationFrame(tick);
            else { a = 0; v = 0; show(); frame = 0; last = 0; }
        }
        function set(x) { on = x; if (on) clock = 0; if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

// Crank arm card: the cranks turn at an easy cadence while the card is hovered or focused, and coast to a stop when it
// is left (bearing drag plus a little dry friction). The chainring and right crank are flat, so one drawing turns by the
// matrix that rotates the bike's plane (A R A^-1, with A the screen vectors of x and z); the left arm is drawn every 45°
// and the nearest drawing is turned by the remainder; the two pedals only move, so they stay level.
(function () {
    if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var nums = function (el, k) { return el.getAttribute('data-' + k).split(' ').map(Number); };
    document.querySelectorAll('.card').forEach(function (card) {
        var root = card.querySelector('.cr');
        if (!root) return;
        var ex = nums(root, 'ex'), ez = nums(root, 'ez'), L = Number(root.getAttribute('data-l'));
        var rest = Number(root.getAttribute('data-rest')) * Math.PI / 180;
        var ring = root.querySelector('.cr-ring'), rc = nums(ring, 'c');
        var armsG = root.querySelector('.cr-arms'), ac = nums(armsG, 'c');
        var arms = [].slice.call(root.querySelectorAll('.cr-arm'));
        var pedal = root.querySelector('.cr-pedal'), pedalR = root.querySelector('.cr-pedal-r');
        var det = ex[0] * ez[1] - ez[0] * ex[1], STEP = Math.PI / 4, TAU = 2 * Math.PI;
        function rot(phi, c) {
            var co = Math.cos(phi), si = Math.sin(phi);
            var m11 = ex[0] * co + ez[0] * si, m21 = ex[1] * co + ez[1] * si, m12 = -ex[0] * si + ez[0] * co, m22 = -ex[1] * si + ez[1] * co;
            var a = (m11 * ez[1] - m12 * ex[1]) / det, b = (m21 * ez[1] - m22 * ex[1]) / det;
            var cc = (-m11 * ez[0] + m12 * ex[0]) / det, d = (-m21 * ez[0] + m22 * ex[0]) / det;
            var e = c[0] - (a * c[0] + cc * c[1]), f = c[1] - (b * c[0] + d * c[1]);
            return 'matrix(' + [a, b, cc, d, e, f].map(function (v) { return v.toFixed(4); }).join(' ') + ')';
        }
        var phi = rest, w = 0, on = false, shown = -1, last = 0, frame = 0;
        var W = -TAU / 1.7, RISE = 0.5, DRAG = 0.9, DRY = 0.6;   // forward pedalling turns the front pedal down
        function place() {
            ring.setAttribute('transform', rot(phi - rest, rc));
            var k = ((Math.round(phi / STEP) % 8) + 8) % 8;
            if (k !== shown) { arms.forEach(function (el, i) { el.setAttribute('visibility', i === k ? 'visible' : 'hidden'); }); shown = k; }
            armsG.setAttribute('transform', rot(phi - Math.round(phi / STEP) * STEP, ac));
            [[pedal, phi], [pedalR, phi + Math.PI]].forEach(function (pa) {     // each pedal rides its crank's end and stays level
                if (!pa[0]) return;
                var dx = L * Math.cos(pa[1]) - L, dz = L * Math.sin(pa[1]);
                pa[0].setAttribute('transform', 'translate(' + (ex[0] * dx + ez[0] * dz).toFixed(2) + ' ' + (ex[1] * dx + ez[1] * dz).toFixed(2) + ')');
            });
        }
        function tick(now) {
            var dt = last ? Math.min(0.05, (now - last) / 1000) : 0; last = now;
            if (on) w += (W - w) * (1 - Math.exp(-dt / RISE));
            else { var dw = (DRAG * Math.abs(w) + DRY) * dt; w = Math.abs(w) <= dw ? 0 : w - Math.sign(w) * dw; }
            phi += w * dt;
            if (phi < -TAU * 50 || phi > TAU * 50) { phi %= TAU; rest %= TAU; }
            place();
            if (on || w !== 0) frame = requestAnimationFrame(tick); else { frame = 0; last = 0; }
        }
        function set(x) { on = x; if (!frame) { last = 0; frame = requestAnimationFrame(tick); } }
        card.addEventListener('mouseenter', function () { set(true); });
        card.addEventListener('mouseleave', function () { set(false); });
        card.addEventListener('focusin', function () { set(true); });
        card.addEventListener('focusout', function () { set(false); });
    });
})();

