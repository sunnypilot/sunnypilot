// Clay car models for carview, built in code so the page needs no downloaded model files.
//
// Each car is one smooth lofted skin: a side profile gives the body's top and bottom lines (wheel arches included) and
// the cabin's roof line; at ~100 stations along the car a rounded cross-section is swept from them, full width below the
// beltline and leaning in toward the roof above it. Triangles on the cabin's sides, windscreen and rear window form the
// glass. Units are metres, the car's front points down -z and it sits on y = 0.

export const CAR_TYPES = ['crossover', 'sedan', 'suv', 'pickup'];

// Side profiles, front at +x. top: the body's outline, front bumper over the hood to the tail and back underneath
// (the wheel arches are added). cabin: the greenhouse outline, only its top edge is used. axles: wheel centres along x.
const PROFILES = {
  crossover: {
    width: 1.92, cabinRatio: 0.86, lean: 0.17, wheelR: 0.36, axles: [1.42, -1.47], sill: 0.25, archR: 0.43,
    top: [['M', 2.24, 0.27], ['Q', 2.42, 0.31, 2.41, 0.50], ['Q', 2.39, 0.70, 2.20, 0.78], ['Q', 1.55, 0.97, 0.86, 1.02],
          ['L', -1.92, 1.07], ['Q', -2.30, 1.08, -2.37, 0.90], ['Q', -2.43, 0.52, -2.31, 0.31], ['Q', -2.25, 0.27, -2.10, 0.27]],
    cabin: [['M', 0.98, 0.96], ['Q', 0.50, 1.31, 0.04, 1.54], ['Q', -0.64, 1.67, -1.30, 1.58], ['Q', -1.86, 1.47, -2.12, 1.10],
            ['L', -2.02, 0.98]],
  },
  sedan: {
    width: 1.86, cabinRatio: 0.84, lean: 0.17, wheelR: 0.34, axles: [1.44, -1.44], sill: 0.21, archR: 0.41,
    top: [['M', 2.28, 0.23], ['Q', 2.44, 0.28, 2.42, 0.47], ['Q', 2.39, 0.67, 2.18, 0.74], ['Q', 1.50, 0.88, 0.76, 0.92],
          ['L', -1.66, 0.98], ['Q', -2.12, 1.00, -2.34, 0.96], ['Q', -2.44, 0.62, -2.34, 0.29], ['Q', -2.28, 0.23, -2.12, 0.23]],
    cabin: [['M', 0.88, 0.88], ['Q', 0.38, 1.21, -0.08, 1.41], ['Q', -0.62, 1.50, -1.12, 1.43], ['Q', -1.54, 1.31, -1.80, 1.00],
            ['L', -1.70, 0.92]],
  },
  suv: {
    width: 1.98, cabinRatio: 0.90, lean: 0.12, wheelR: 0.39, axles: [1.50, -1.50], sill: 0.31, archR: 0.47,
    top: [['M', 2.36, 0.33], ['Q', 2.51, 0.39, 2.49, 0.63], ['Q', 2.47, 0.91, 2.29, 0.99], ['Q', 1.70, 1.10, 1.02, 1.13],
          ['L', -2.28, 1.17], ['Q', -2.47, 1.17, -2.48, 0.99], ['Q', -2.51, 0.59, -2.40, 0.37], ['Q', -2.34, 0.33, -2.20, 0.33]],
    cabin: [['M', 1.10, 1.08], ['Q', 0.78, 1.43, 0.40, 1.75], ['Q', -0.80, 1.83, -2.12, 1.79], ['Q', -2.38, 1.74, -2.44, 1.46],
            ['L', -2.40, 1.10]],
  },
  pickup: {
    width: 2.02, cabinRatio: 0.88, lean: 0.12, wheelR: 0.40, axles: [1.92, -1.78], sill: 0.37, archR: 0.49,
    top: [['M', 2.82, 0.41], ['Q', 2.97, 0.47, 2.95, 0.73], ['Q', 2.93, 1.03, 2.75, 1.11], ['Q', 2.10, 1.21, 1.30, 1.23],
          ['L', -2.80, 1.27], ['Q', -2.91, 1.27, -2.91, 1.10], ['Q', -2.93, 0.70, -2.84, 0.45], ['Q', -2.78, 0.41, -2.64, 0.41]],
    cabin: [['M', 1.40, 1.16], ['Q', 1.08, 1.53, 0.70, 1.91], ['Q', -0.06, 1.97, -0.80, 1.93], ['Q', -0.93, 1.89, -0.95, 1.70],
            ['L', -0.97, 1.18]],
    bed: [-1.05, -2.74],
  },
};

const PAINTS = {
  clay: { body: 0xd8dbdf, glass: 0x7f8792, roughness: 0.62, metalness: 0.0, glassRoughness: 0.22 },
  ego: { body: 0x2f3338, glass: 0x0f1115, roughness: 0.3, metalness: 0.4, glassRoughness: 0.1 },
};

const STATIONS = 104;
const CORNER = 5;  // points per rounded corner of a cross-section

function outline(THREE, cmds, p, withArches) {
  const s = new THREE.Shape();
  for (const [op, ...a] of cmds) {
    if (op === 'M') s.moveTo(a[0], a[1]);
    else if (op === 'L') s.lineTo(a[0], a[1]);
    else if (op === 'Q') s.quadraticCurveTo(a[0], a[1], a[2], a[3]);
  }
  if (withArches) {
    for (const ax of [...p.axles].sort((a, b) => a - b)) {  // underside, rear to front, over each wheel
      s.lineTo(ax - p.archR, p.sill);
      s.absarc(ax, p.wheelR, p.archR, Math.PI + Math.asin(Math.min(1, (p.wheelR - p.sill) / p.archR)), -Math.asin(Math.min(1, (p.wheelR - p.sill) / p.archR)), true);
      s.lineTo(ax + p.archR, p.sill);
    }
  }
  s.closePath();
  return s.getPoints(48);
}

// the outline split at its front- and rearmost points into an upper and a lower line, each sorted by x
function chains(points) {
  let iMax = 0, iMin = 0;
  points.forEach((q, i) => { if (q.x > points[iMax].x) iMax = i; if (q.x < points[iMin].x) iMin = i; });
  const walk = (from, to) => { const out = []; for (let i = from; ; i = (i + 1) % points.length) { out.push(points[i]); if (i === to) break; } return out; };
  const a = walk(iMax, iMin), b = walk(iMin, iMax);
  const meanY = (c) => c.reduce((s, q) => s + q.y, 0) / c.length;
  const sort = (c) => c.map(q => [q.x, q.y]).sort((u, v) => u[0] - v[0]);
  return meanY(a) > meanY(b) ? { upper: sort(a), lower: sort(b), minX: points[iMin].x, maxX: points[iMax].x }
                             : { upper: sort(b), lower: sort(a), minX: points[iMin].x, maxX: points[iMax].x };
}

function yAt(chain, x, pick = Math.max) {
  // linear between the points around x; where the line is vertical (an arch's side), pick decides
  let lo = 0, hi = chain.length - 1;
  if (x <= chain[0][0]) return chain[0][1];
  if (x >= chain[hi][0]) return chain[hi][1];
  while (hi - lo > 1) { const mid = (lo + hi) >> 1; if (chain[mid][0] <= x) lo = mid; else hi = mid; }
  const [x0, y0] = chain[lo], [x1, y1] = chain[hi];
  return x1 - x0 < 1e-6 ? pick(y0, y1) : y0 + (y1 - y0) * (x - x0) / (x1 - x0);
}

const arc = (cx, cy, r, a0, a1, out) => { for (let k = 0; k <= CORNER; k++) { const a = a0 + (a1 - a0) * k / CORNER; out.push([cx + r * Math.cos(a), cy + r * Math.sin(a)]); } };

// right half of a cross-section, bottom centre to roof centre, as [z, y]; glassFrom/glassTo index the cabin's side
function section(b, t, r, hw, cwBase, cwTop) {
  const pts = [[0, b]];
  const h = Math.max(t - b, 1e-4);
  const rb = Math.min(0.10, h / 3, hw / 3), rs = Math.min(0.13, h / 3, hw / 3);
  arc(hw - rb, b + rb, rb, -Math.PI / 2, 0, pts);
  arc(hw - rs, t - rs, rs, 0, Math.PI / 2, pts);
  const glassFrom = pts.length;
  const cabinH = Math.max(r - t, 0);
  const rr = Math.min(0.17, cabinH * 0.45, cwTop / 3);
  pts.push([Math.min(cwBase, hw - rs), t]);
  for (const f of [0.08, 0.5]) pts.push([cwBase + (cwTop - cwBase) * f, t + (cabinH - rr) * f]);
  arc(cwTop - rr, r - rr, rr, 0, Math.PI / 2, pts);
  const glassTo = pts.length - CORNER + 1;  // the roof corner's lower part is still glass
  pts.push([0, r]);
  return { pts, glassFrom, glassTo };
}

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

function skin(THREE, p) {
  const body = chains(outline(THREE, p.top, p, true));
  const cabin = chains(outline(THREE, p.cabin, p, false));
  const half = (body.maxX - body.minX) / 2, xc = (body.maxX + body.minX) / 2;
  const planWidth = (x) => { const u = Math.min(1, Math.abs(x - xc) / (half * 1.015)); return Math.pow(1 - Math.pow(u, 5), 1 / 5); };
  const roofAt = (x) => (x > cabin.minX && x < cabin.maxX) ? yAt(cabin.upper, x) : -1;

  const positions = [], glass = [], paintTris = [], glassTris = [];
  let ring = 0;
  for (let i = 0; i < STATIONS; i++) {
    // denser toward the ends, where the shape turns fastest
    const s = i / (STATIONS - 1), x = xc - half * Math.cos(Math.PI * s) * 0.999;
    const b = yAt(body.lower, x, Math.max), t = yAt(body.upper, x);
    const r = Math.max(t, roofAt(x));
    const hw = (p.width / 2) * planWidth(x);
    const cwBase = hw * p.cabinRatio, cwTop = cwBase * (1 - p.lean);
    const { pts, glassFrom, glassTo } = section(b, t, r, hw, cwBase, cwTop);
    if (i === 0) ring = pts.length * 2 - 2;
    const dr = (Math.max(t, roofAt(x + 0.05)) - Math.max(t, roofAt(x - 0.05))) / 0.1;  // roof slope: windscreen or rear window
    const cabinH = r - t;
    const flags = [];
    const loop = [...pts, ...pts.slice(1, -1).reverse().map(([z, y]) => [-z, y])];
    const idx = (j) => (j < pts.length ? j : pts.length - 1 - (j - pts.length + 1));  // loop index to half index
    loop.forEach(([z, y], j) => {
      positions.push(x, y, z);
      const k = idx(j);
      const side = k >= glassFrom + 1 && k < glassTo;
      const top = k >= glassTo && Math.abs(dr) > 0.42;
      flags.push(cabinH > 0.12 && (side || top) && Math.abs(x - xc) < half - 0.12);
    });
    glass.push(flags);
  }
  // quads between stations, split into paint and glass triangles
  for (let i = 0; i < STATIONS - 1; i++) {
    for (let j = 0; j < ring; j++) {
      const j1 = (j + 1) % ring;
      const a = i * ring + j, bq = i * ring + j1, c = (i + 1) * ring + j, d = (i + 1) * ring + j1;
      const isGlass = glass[i][j] && glass[i][j1] && glass[i + 1][j] && glass[i + 1][j1];
      (isGlass ? glassTris : paintTris).push(a, c, bq, bq, c, d);
    }
  }
  // close both ends with a fan around each end ring's centre, facing out: -x at the tail, +x at the nose
  for (const [i, nose] of [[0, false], [STATIONS - 1, true]]) {
    let cx = 0, cy = 0, cz = 0;
    for (let j = 0; j < ring; j++) { cx += positions[(i * ring + j) * 3]; cy += positions[(i * ring + j) * 3 + 1]; cz += positions[(i * ring + j) * 3 + 2]; }
    const centre = positions.length / 3;
    positions.push(cx / ring, cy / ring, cz / ring);
    for (let j = 0; j < ring; j++) {
      const a = i * ring + j, bq = i * ring + (j + 1) % ring;
      if (nose) paintTris.push(centre, bq, a); else paintTris.push(centre, a, bq);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  g.setIndex([...paintTris, ...glassTris]);
  g.addGroup(0, paintTris.length, 0);
  g.addGroup(paintTris.length, glassTris.length, 1);
  g.computeVertexNormals();
  return { g, beltlineAt: (x) => yAt(body.upper, x), halfWidthAt: (x) => (p.width / 2) * planWidth(x), cabinFront: cabin.maxX,
           rearX: body.minX };
}

let shadowTexture = null;
function contactShadow(THREE, length, width) {
  if (!shadowTexture) {
    const c = document.createElement('canvas'); c.width = c.height = 128;
    const ctx = c.getContext('2d');
    const grd = ctx.createRadialGradient(64, 64, 6, 64, 64, 64);
    grd.addColorStop(0, 'rgba(0,0,0,0.5)'); grd.addColorStop(0.5, 'rgba(0,0,0,0.26)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grd; ctx.fillRect(0, 0, 128, 128);
    shadowTexture = new THREE.CanvasTexture(c);
  }
  const m = new THREE.Mesh(new THREE.PlaneGeometry(width * 1.5, length * 1.18),
                           new THREE.MeshBasicMaterial({ map: shadowTexture, transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.012; m.renderOrder = -1;
  return m;
}

const materialCache = new Map();
function materials(THREE, paintName) {
  if (!materialCache.has(paintName)) {
    const p = PAINTS[paintName] || PAINTS.clay;
    materialCache.set(paintName, {
      body: new THREE.MeshStandardMaterial({ color: p.body, roughness: p.roughness, metalness: p.metalness }),
      glass: new THREE.MeshStandardMaterial({ color: p.glass, roughness: p.glassRoughness, metalness: 0.1 }),
      tire: new THREE.MeshStandardMaterial({ color: 0x26282c, roughness: 0.85 }),
      hub: new THREE.MeshStandardMaterial({ color: paintName === 'ego' ? 0x9097a0 : 0xcdd0d5, roughness: 0.45, metalness: 0.3 }),
      bed: new THREE.MeshStandardMaterial({ color: 0x55595f, roughness: 0.9 }),
    });
  }
  return materialCache.get(paintName);
}

const partsCache = new Map();
function parts(THREE, type) {
  if (!partsCache.has(type)) {
    const p = PROFILES[type];
    const s = skin(THREE, p);
    const tire = new THREE.CylinderGeometry(p.wheelR, p.wheelR, 0.25, 40, 1);
    tire.rotateX(Math.PI / 2);
    const hub = new THREE.CylinderGeometry(p.wheelR * 0.64, p.wheelR * 0.64, 0.02, 40, 1);
    hub.rotateX(Math.PI / 2);
    const mirror = new THREE.SphereGeometry(0.1, 20, 14);
    mirror.scale(1.15, 0.85, 1.25);
    partsCache.set(type, { ...s, tire, hub, mirror });
  }
  return partsCache.get(type);
}

// A car as a THREE.Group, front toward -z. paint: 'clay' for other traffic, 'ego' for our own car.
export function buildCar(THREE, type = 'crossover', paint = 'clay') {
  type = PROFILES[type] ? type : 'crossover';
  const p = PROFILES[type], g = parts(THREE, type), mat = materials(THREE, paint);
  const car = new THREE.Group();   // what the caller moves around
  const model = new THREE.Group(); // the profile's +x turned to -z
  model.rotation.y = Math.PI / 2;
  car.add(model);

  const skinMesh = new THREE.Mesh(g.g, [mat.body, mat.glass]);
  model.add(skinMesh);
  if (p.bed) {
    const [x0, x1] = p.bed, y = g.beltlineAt((x0 + x1) / 2);
    const bed = new THREE.Mesh(new THREE.BoxGeometry(x0 - x1, 0.02, 2 * g.halfWidthAt((x0 + x1) / 2) - 0.3), mat.bed);
    bed.position.set((x0 + x1) / 2, y + 0.006, 0);
    model.add(bed);
  }
  // mirrors sit on the door tops just behind the windscreen's base, dug into the shoulder so they never float
  const mx = g.cabinFront - 0.22, my = g.beltlineAt(mx) + 0.03, mz = g.halfWidthAt(mx) - 0.01;
  for (const side of [-1, 1]) {
    const m = new THREE.Mesh(g.mirror, mat.body);
    m.position.set(mx, my, side * mz);
    model.add(m);
  }
  const zWheel = p.width / 2 - 0.17;
  for (const ax of p.axles) {
    for (const side of [-1, 1]) {
      const tire = new THREE.Mesh(g.tire, mat.tire);
      tire.position.set(ax, p.wheelR, side * zWheel);
      model.add(tire);
      const hub = new THREE.Mesh(g.hub, mat.hub);
      hub.position.set(ax, p.wheelR, side * (zWheel + 0.13));
      model.add(hub);
    }
  }
  // a tail light bar across the back, dark until car.userData.setBraking(true)
  const lx = g.rearX + 0.07, ly = g.beltlineAt(lx + 0.15) - 0.12;
  const lights = new THREE.MeshStandardMaterial({ color: 0x4a2124, roughness: 0.4, emissive: 0xff2b2b, emissiveIntensity: 0 });
  const bar = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.07, 2 * g.halfWidthAt(lx) * 0.92), lights);
  bar.position.set(lx, ly, 0);
  model.add(bar);

  const length = Math.max(...p.top.map(c => c[c.length - 2])) - Math.min(...p.top.map(c => c[c.length - 2]));
  car.add(contactShadow(THREE, length, p.width));
  car.userData = {
    type, length, width: p.width,
    setBraking: (on) => { lights.emissiveIntensity = on ? 2.4 : 0; lights.color.setHex(on ? 0xc92a2a : 0x4a2124); },
  };
  return car;
}

// Supersampling on top of the renderer's own multisampling: draw at 1.5-3x the screen's pixels and let the browser
// scale it down, so edges stay smooth even on a 1x screen. Steps down a quarter at a time while the frame rate is under
// minFps for two seconds running, never below 1x. Call tick(now) once per frame; it returns the pixel ratio in use.
export function supersampler(renderer, { minFps = 45, start = null } = {}) {
  const dpr = window.devicePixelRatio || 1;
  let ratio = start ?? Math.min(3, Math.max(1.5, dpr * 1.5));
  renderer.setPixelRatio(ratio);
  let frames = 0, since = performance.now(), slowWindows = 0;
  return {
    get ratio() { return ratio; },
    tick(now) {
      frames++;
      if (now - since < 1000) return ratio;
      const fps = frames * 1000 / (now - since);
      frames = 0; since = now;
      // under ~8 fps the browser is throttling a hidden page, not struggling to draw: leave the resolution alone
      slowWindows = fps >= 8 && fps < minFps ? slowWindows + 1 : 0;
      if (slowWindows >= 2 && ratio > 1) {
        ratio = Math.max(1, ratio - 0.25); slowWindows = 0;
        renderer.setPixelRatio(ratio);
        renderer.setSize(renderer.domElement.clientWidth, renderer.domElement.clientHeight, false);
      }
      return ratio;
    },
  };
}

// Soft studio light for the clay look: a pre-filtered environment from a few glowing panels around a grey room.
export function studioEnvironment(THREE, renderer) {
  const room = new THREE.Scene();
  room.background = new THREE.Color(0x8e9197);
  const panel = (w, h, x, y, z, intensity) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(intensity, intensity, intensity), side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); room.add(m);
  };
  panel(16, 16, 0, 12, 0, 3.0);    // big overhead softbox
  panel(12, 5, 0, 4, -13, 1.6);    // front strip
  panel(12, 5, 13, 3, 0, 1.1);     // side fills
  panel(12, 5, -13, 3, 0, 0.9);
  panel(12, 5, 0, 3, 13, 1.2);     // behind
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.MeshBasicMaterial({ color: 0x5e6166 }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -2; room.add(floor);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const env = pmrem.fromScene(room, 0.035).texture;
  pmrem.dispose();
  return env;
}
