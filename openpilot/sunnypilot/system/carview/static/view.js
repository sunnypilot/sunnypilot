// carview's driving scene: the model's road, lane lines and planned path, the lead cars and our own car, in three.js.
//
// The model speaks in its own frame, x forward, y right, z down, in metres from the comma's camera. The scene is
// three.js's: x right, y up, forward down -z, so a model point (x, y, z) sits at (y, -z, -x). Everything stays in the
// car's frame, as on the car's own display: our car never moves, the road bends and flows past it.
import { buildCar, studioEnvironment, supersampler } from '/cars.js';

const CAMERA_TO_FRONT = 1.52;  // m, the comma sits this far behind the front bumper (radard's RADAR_TO_CAMERA)
const BEHIND = -12;            // m of road drawn behind the camera, beyond what the model sees
const ROAD_FAR = 170;          // m, the fog has everything past this
const PATH_FAR = 90;           // m of planned path drawn
const PATH_WIDTH = 0.9;
const LINE_WIDTH = 0.15;
const DASH = 3.0, DASH_EVERY = 12.0;  // m: US lane dashes are 10 ft long with 30 ft gaps
// easing toward each new model frame, in seconds: long enough that the model's frame-to-frame noise doesn't show,
// short enough that the road still swings round with us in a turn
const EASE_S = { line: 0.22, edge: 0.45, path: 0.14, lead: 0.3 };
const SMOOTH_FROM = 15;        // m: lines and edges are averaged along their length past this, where they wobble
const EDGE_MIN = 1.6, EDGE_MAX = 8.0;  // m from the path that a road edge is kept to
const LEAD_BRAKING = -1.0;     // m/s^2, the lead's tail lights come on below this

const COLORS = {
  sky: 0xdcdde0, ground: 0xc4c7cb, road: 0xf4f4f5, line: 0x9ea3a9, blindspot: 0xe0464b,
  pathOn: 0x3e6ae1, pathSteer: 0x5b8def, pathOff: 0xa9adb3,
};

// a straight three-lane road for before the first model frame, in the model's frame
function defaultRoad(lineX) {
  const flat = (y) => [lineX.map(() => y), lineX.map(() => 0)];
  return { lines: [flat(-5.4), flat(-1.8), flat(1.8), flat(5.4)], lineProbs: [0.6, 0.9, 0.9, 0.6], edges: [flat(-7.2), flat(7.2)] };
}

const DEFAULT_X = Array.from({ length: 33 }, (_, i) => 192 * (i / 32) ** 2);

// a polyline in the model's frame, eased toward each new model frame; xs stay fixed, y and z move
class Line {
  constructor(xs) { this.setX(xs); }
  setX(xs) {
    // prepend a straight run behind the camera so lines continue past our own car
    this.xs = [BEHIND, ...xs];
    this.y = new Float32Array(this.xs.length); this.z = new Float32Array(this.xs.length);
    this.ty = new Float32Array(this.xs.length); this.tz = new Float32Array(this.xs.length);
    this.fresh = true;
  }
  target(ys, zs) {
    if (ys.length + 1 !== this.xs.length) return;
    this.ty[0] = ys[0]; this.tz[0] = zs[0];
    for (let i = 0; i < ys.length; i++) { this.ty[i + 1] = ys[i]; this.tz[i + 1] = zs[i]; }
    if (this.fresh) { this.y.set(this.ty); this.z.set(this.tz); this.fresh = false; }
  }
  ease(k) { for (let i = 0; i < this.y.length; i++) { this.y[i] += (this.ty[i] - this.y[i]) * k; this.z[i] += (this.tz[i] - this.z[i]) * k; } }
  at(x) {  // y and z at model x, linear between samples
    const xs = this.xs;
    if (x <= xs[0]) return [this.y[0], this.z[0]];
    for (let i = 1; i < xs.length; i++) {
      if (x <= xs[i]) { const f = (x - xs[i - 1]) / (xs[i] - xs[i - 1]); return [this.y[i - 1] + (this.y[i] - this.y[i - 1]) * f, this.z[i - 1] + (this.z[i] - this.z[i - 1]) * f]; }
    }
    return [this.y[xs.length - 1], this.z[xs.length - 1]];
  }
}

// a flat ribbon along points [[X, Y, Z], ...] in scene space, written into a preallocated geometry
function writeRibbon(geo, pts, width, lift, alphaAt = null) {
  const pos = geo.attributes.position.array, col = geo.attributes.color ? geo.attributes.color.array : null;
  const n = pts.length;
  for (let i = 0; i < n; i++) {
    const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)];
    let tx = b[0] - a[0], tz = b[2] - a[2];
    const len = Math.hypot(tx, tz) || 1; tx /= len; tz /= len;
    const nx = -tz * width / 2, nz = tx * width / 2;  // sideways in the road plane
    const [X, Y, Z] = pts[i];
    pos.set([X - nx, Y + lift, Z - nz, X + nx, Y + lift, Z + nz], i * 6);
    if (col) { const al = alphaAt ? alphaAt(i, n) : 1; col.set([1, 1, 1, al, 1, 1, 1, al], i * 8); }
  }
  geo.setDrawRange(0, Math.max(0, (n - 1) * 6));
  geo.attributes.position.needsUpdate = true;
  if (col) geo.attributes.color.needsUpdate = true;
}

// two triangles per step along a strip of [left, right] vertex pairs, wound to face up
const stripIndex = (out, a) => out.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);

function ribbonGeometry(THREE, maxPoints, { alpha = false, lit = false } = {}) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(maxPoints * 2 * 3), 3));
  if (alpha) g.setAttribute('color', new THREE.BufferAttribute(new Float32Array(maxPoints * 2 * 4), 4));
  if (lit) g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(maxPoints * 2 * 3).map((_, i) => (i % 3 === 1 ? 1 : 0)), 3));
  const idx = [];
  for (let i = 0; i < maxPoints - 1; i++) stripIndex(idx, 2 * i);
  g.setIndex(idx);
  return g;
}

// a strip between two lines, the road surface
function writeStrip(geo, left, right, lift) {
  const pos = geo.attributes.position.array, n = left.length;
  for (let i = 0; i < n; i++) pos.set([left[i][0], left[i][1] + lift, left[i][2], right[i][0], right[i][1] + lift, right[i][2]], i * 6);
  geo.setDrawRange(0, (n - 1) * 6);
  geo.attributes.position.needsUpdate = true;
}

// meshes whose vertices move every frame: never culled, so their bounds needn't be kept up
const live = (THREE, geo, mat) => { const m = new THREE.Mesh(geo, mat); m.frustumCulled = false; return m; };

const toScene = (x, y, z) => [y, -z, -x];

// a 5-point running average along a line, only past SMOOTH_FROM: near the car the model is sharp and steady
function steady(xs, ys) {
  return ys.map((y, i) => {
    if (xs[i] < SMOOTH_FROM) return y;
    let sum = 0, n = 0;
    for (let j = Math.max(0, i - 2); j <= Math.min(ys.length - 1, i + 2); j++) { sum += ys[j]; n++; }
    return sum / n;
  });
}

// the path's sideways offset at model x, from its [xs, ys, zs]; held at its ends, and only ever read forward, since a
// stopped car's path folds back on itself
function alongPath(path) {
  if (!path || !path[0].length) return () => 0;
  const xs = [], ys = [];
  path[0].forEach((x, i) => { if (!xs.length || x > xs[xs.length - 1]) { xs.push(x); ys.push(path[1][i]); } });
  return (x) => {
    if (x <= xs[0]) return ys[0];
    for (let i = 1; i < xs.length; i++) if (x <= xs[i]) return ys[i - 1] + (ys[i] - ys[i - 1]) * (x - xs[i - 1]) / (xs[i] - xs[i - 1]);
    return ys[ys.length - 1];
  };
}

export function createView(THREE, canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.toneMapping = THREE.NeutralToneMapping;
  const ss = supersampler(renderer);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(COLORS.sky);
  scene.fog = new THREE.Fog(COLORS.sky, 60, ROAD_FAR);
  scene.environment = studioEnvironment(THREE, renderer);
  scene.environmentIntensity = 0.75;
  scene.add(new THREE.HemisphereLight(0xffffff, 0xa9abaf, 0.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.5); sun.position.set(-5, 9, 6); scene.add(sun);
  const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 400);

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(800, 800), new THREE.MeshStandardMaterial({ color: COLORS.ground, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.position.set(0, -0.05, -150); scene.add(ground);

  // model state, eased
  const lines = [0, 1, 2, 3].map(() => new Line(DEFAULT_X));
  const edges = [0, 1].map(() => new Line(DEFAULT_X));
  const lineProbs = [0.6, 0.9, 0.9, 0.6], probTarget = [...lineProbs];
  let path = null, pathTarget = null;  // [[x, y, z], ...] in the model's frame
  const road = defaultRoad(DEFAULT_X);
  road.lines.forEach((l, i) => lines[i].target(...l));
  road.edges.forEach((e, i) => edges[i].target(...e));

  // meshes
  const roadMat = new THREE.MeshStandardMaterial({ color: COLORS.road, roughness: 1, polygonOffset: true, polygonOffsetFactor: -1 });
  const roadGeo = ribbonGeometry(THREE, 40, { lit: true });
  scene.add(live(THREE, roadGeo, roadMat));

  const lineMats = lines.map(() => new THREE.MeshBasicMaterial({ color: COLORS.line, transparent: true, opacity: 0.8, depthWrite: false }));
  const solidGeos = [0, 3].map(() => ribbonGeometry(THREE, 40));
  scene.add(live(THREE, solidGeos[0], lineMats[0]), live(THREE, solidGeos[1], lineMats[3]));
  const MAX_DASHES = 20, DASH_POINTS = 3;
  const dashGeos = [1, 2].map(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(MAX_DASHES * DASH_POINTS * 2 * 3), 3));
    const idx = [];
    for (let d = 0; d < MAX_DASHES; d++) for (let i = 0; i < DASH_POINTS - 1; i++) stripIndex(idx, (d * DASH_POINTS + i) * 2);
    g.setIndex(idx);
    return g;
  });
  scene.add(live(THREE, dashGeos[0], lineMats[1]), live(THREE, dashGeos[1], lineMats[2]));

  const pathMat = new THREE.MeshBasicMaterial({ color: COLORS.pathOff, vertexColors: true, transparent: true, depthWrite: false });
  const pathGeo = ribbonGeometry(THREE, 34, { alpha: true });
  scene.add(live(THREE, pathGeo, pathMat));

  const ego = buildCar(THREE, 'crossover', 'ego');
  ego.position.set(0, 0, -CAMERA_TO_FRONT + ego.userData.length / 2);
  scene.add(ego);
  const leadCars = [buildCar(THREE, 'suv', 'clay'), buildCar(THREE, 'sedan', 'clay')];
  const leadState = leadCars.map(() => ({ on: false, x: 0, z: 0 }));
  leadCars.forEach(c => { c.visible = false; scene.add(c); });

  let car = {}, distance = 0, v = 0, camBack = 12;

  function resize() {
    const w = canvas.clientWidth || window.innerWidth, h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize); resize();

  function update(state) {
    car = state || {};
    const m = car.model;
    if (!m) return;
    if (m.lineX && m.lineX.length && m.lineX.length + 1 !== lines[0].xs.length) [...lines, ...edges].forEach(l => l.setX(m.lineX));
    // The road is drawn flat, as on the car's own display. Seen live: lane lines and road edges come with z from a
    // camera tilted against the road (15 cm higher on the right across the lane, half a metre higher 100 m out), and the
    // path's own z swings by metres 60 m out from one frame to the next, enough to hide the road behind a crest.
    const lx = m.lineX || [], flat = lx.map(() => 0);
    const pathY = alongPath(m.path);
    (m.lines || []).forEach((l, i) => lines[i] && lines[i].target(steady(lx, l[0]), flat));
    // road edges the model is unsure of wander and even cross the path: keep each on its own side, within reach
    (m.edges || []).forEach((e, i) => {
      if (!edges[i]) return;
      const side = i === 0 ? -1 : 1;
      edges[i].target(steady(lx, e[0].map((y, j) => {
        const p = pathY(lx[j]), off = Math.min(EDGE_MAX, Math.max(EDGE_MIN, side * (y - p)));
        return p + side * off;
      })), flat);
    });
    (m.lineProbs || []).forEach((p, i) => { probTarget[i] = p; });
    if (m.path && m.path[0].length) {
      pathTarget = m.path[0].map((x, i) => [x, m.path[1][i], 0]);  // flat, like the road
      if (!path || path.length !== pathTarget.length) path = pathTarget.map(p => [...p]);
    }
  }

  const sample = (line, x) => { const [y, z] = line.at(x); return toScene(x, y, z); };

  function frame(now, dt) {
    ss.tick(now);
    const ease = (s) => 1 - Math.exp(-dt / s);
    const k = ease(EASE_S.line), kp = ease(EASE_S.path), kl = ease(EASE_S.lead);
    lines.forEach(l => l.ease(k));
    edges.forEach(l => l.ease(ease(EASE_S.edge)));
    for (let i = 0; i < 4; i++) lineProbs[i] += (probTarget[i] - lineProbs[i]) * k;
    if (path && pathTarget) for (let i = 0; i < path.length; i++) for (let j = 0; j < 3; j++) path[i][j] += (pathTarget[i][j] - path[i][j]) * kp;

    v += ((car.vEgo || 0) - v) * Math.min(1, dt * 4);
    distance += v * dt;

    // road surface between the edges, out to the fog
    const xs = lines[0].xs.filter(x => x <= ROAD_FAR);
    writeStrip(roadGeo, xs.map(x => sample(edges[0], x)), xs.map(x => sample(edges[1], x)), 0.0);

    // outer lines solid, the lines either side of our lane dashed and flowing past
    [0, 3].forEach((li, j) => writeRibbon(solidGeos[j], xs.map(x => sample(lines[li], x)), LINE_WIDTH, 0.02));
    [1, 2].forEach((li, j) => {
      const g = dashGeos[j], pos = g.attributes.position.array;
      let d = 0;
      for (let s = BEHIND - (distance % DASH_EVERY); s < ROAD_FAR && d < MAX_DASHES; s += DASH_EVERY) {
        const pts = [];
        for (let i = 0; i < DASH_POINTS; i++) pts.push(sample(lines[li], s + DASH * i / (DASH_POINTS - 1)));
        for (let i = 0; i < DASH_POINTS; i++) {
          const a = pts[Math.max(0, i - 1)], b = pts[Math.min(DASH_POINTS - 1, i + 1)];
          let tx = b[0] - a[0], tz = b[2] - a[2]; const len = Math.hypot(tx, tz) || 1; tx /= len; tz /= len;
          const nx = -tz * LINE_WIDTH / 2, nz = tx * LINE_WIDTH / 2, [X, Y, Z] = pts[i];
          pos.set([X - nx, Y + 0.02, Z - nz, X + nx, Y + 0.02, Z + nz], (d * DASH_POINTS + i) * 6);
        }
        d++;
      }
      g.setDrawRange(0, d * (DASH_POINTS - 1) * 6);
      g.attributes.position.needsUpdate = true;
    });
    lineMats.forEach((mat, i) => {
      const blind = (i === 1 && car.leftBlindspot) || (i === 2 && car.rightBlindspot);
      mat.color.setHex(blind ? COLORS.blindspot : COLORS.line);
      mat.opacity = blind ? 1 : Math.max(0.08, Math.min(1, lineProbs[i])) * (i === 0 || i === 3 ? 0.7 : 0.95);
    });

    // the planned path from our front bumper, fading out ahead
    if (path) {
      const pts = path.filter(p => p[0] >= CAMERA_TO_FRONT - 0.5 && p[0] <= PATH_FAR).map(p => toScene(...p));
      if (pts.length > 1) writeRibbon(pathGeo, pts, PATH_WIDTH, 0.03, (i, n) => 0.9 * (1 - (i / (n - 1)) ** 2));
    }
    pathMat.color.setHex(car.engaged ? COLORS.pathOn : car.mads ? COLORS.pathSteer : COLORS.pathOff);
    pathMat.opacity = car.engaged || car.mads ? 1 : 0.55;

    // leads: dRel from our front bumper, yRel to the left. The second lead is often the first one again (seen live:
    // both at 8.2 m), which drew two cars in one spot, so it only counts when it's clearly another car.
    const all = car.leads || [];
    const leads = all.filter((l, i) => i === 0 || Math.abs(l.d - all[0].d) > 4 || Math.abs(l.y - all[0].y) > 1.5);
    leadCars.forEach((lc, i) => {
      const lead = leads[i], st = leadState[i];
      if (!lead) { lc.visible = false; st.on = false; return; }
      const x = CAMERA_TO_FRONT + lead.d + lc.userData.length / 2;
      const tx = -Math.max(-8, Math.min(8, lead.y)), tz = -x;
      if (!st.on) { st.x = tx; st.z = tz; st.on = true; }
      st.x += (tx - st.x) * kl; st.z += (tz - st.z) * kl;
      lc.position.set(st.x, 0, st.z);
      lc.visible = true;
      lc.userData.setBraking(lead.a < LEAD_BRAKING);
    });

    // chase camera: closer in town, further back and higher at speed
    camBack += (Math.min(16, 9 + v * 0.3) - camBack) * Math.min(1, dt * 1.5);
    camera.position.set(0, 3.6 + camBack * 0.22, ego.position.z + camBack);
    camera.lookAt(0, 0, ego.position.z - 26);
    renderer.render(scene, camera);
  }

  return { update, frame, resize, get pixelRatio() { return ss.ratio; } };
}
