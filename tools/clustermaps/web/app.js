const ROUTE_COLORS = ["#00a78e", "#3578c8", "#7656c8", "#ed6a3c", "#d34a73", "#578d3b", "#b17a20"];
const TELEMETRY_KEYS = [
  "imu", "vehicle", "pose", "visualOdometry", "controls", "calibration",
  "roadVision", "radar", "sound", "magnetic", "thermal",
];
const LAYER_KEYS = [
  "route", "roughness", "impact", "hardAcceleration", "hardBraking", "bodyMotion", "gps",
  ...TELEMETRY_KEYS,
];
const TELEMETRY_COLORS = {
  imu: "#008a78",
  vehicle: "#245f97",
  pose: "#6b5bb8",
  visualOdometry: "#447caa",
  controls: "#c48428",
  calibration: "#8a659b",
  roadVision: "#3f8b54",
  radar: "#d05d42",
  sound: "#b84775",
  magnetic: "#5368a8",
  thermal: "#a55432",
};

const map = L.map("map", {
  zoomControl: false,
  preferCanvas: true,
  minZoom: 2,
  maxZoom: 20,
});
L.control.zoom({ position: "bottomright" }).addTo(map);
map.createPane("atlasGlow");
map.getPane("atlasGlow").style.zIndex = "390";
map.getPane("atlasGlow").style.pointerEvents = "none";
const glowRenderer = L.canvas({ pane: "atlasGlow", padding: 0.5 });
map.createPane("atlasBleed");
map.getPane("atlasBleed").style.zIndex = "385";
map.getPane("atlasBleed").style.pointerEvents = "none";
const bleedRenderer = L.canvas({ pane: "atlasBleed", padding: 0.5 });
map.createPane("atlasHeat");
map.getPane("atlasHeat").style.zIndex = "392";
map.getPane("atlasHeat").style.pointerEvents = "none";

const streetTiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a>",
  maxZoom: 19,
});
streetTiles.addTo(map);

const satelliteTiles = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution: "Imagery &copy; <a href=\"https://www.esri.com/\">Esri</a>",
    maxZoom: 19,
  },
);

const SensorCanvasLayer = L.GridLayer.extend({
  createTile(coords) {
    const tile = document.createElement("canvas");
    const size = this.getTileSize();
    tile.width = size.x;
    tile.height = size.y;
    tile.className = "sensor-grid-tile";
    const context = tile.getContext("2d");
    context.fillStyle = "#e8efeb";
    context.fillRect(0, 0, size.x, size.y);

    context.strokeStyle = "rgba(16, 42, 45, 0.11)";
    context.lineWidth = 1;
    for (let position = 0; position <= size.x; position += size.x / 4) {
      context.beginPath();
      context.moveTo(position, 0);
      context.lineTo(position, size.y);
      context.stroke();
      context.beginPath();
      context.moveTo(0, position);
      context.lineTo(size.x, position);
      context.stroke();
    }

    const center = map.unproject(
      L.point(coords.x * size.x + size.x / 2, coords.y * size.y + size.y / 2),
      coords.z,
    );
    context.fillStyle = "rgba(16, 42, 45, 0.48)";
    context.font = "600 10px ui-monospace, SFMono-Regular, Menlo, monospace";
    context.fillText(`${center.lat.toFixed(4)}°, ${center.lng.toFixed(4)}°`, 10, 18);
    return tile;
  },
});
const sensorCanvas = new SensorCanvasLayer({
  attribution: "Sensor data canvas",
  minZoom: 2,
  maxZoom: 20,
});

const repeatedLayer = L.layerGroup().addTo(map);
const routeLayers = new Map();
const routeVisibility = new Map();
const layerVisibility = Object.fromEntries(LAYER_KEYS.map((key) => [key, true]));
layerVisibility.bodyMotion = false;
layerVisibility.gps = false;
for (const key of TELEMETRY_KEYS) layerVisibility[key] = false;
let loadedRoutes = [];
let atlasIndex = null;
let fullBounds = null;
const VISUAL_PRESETS = {
  signal: { width: 1, intensity: 0.8, routeGlow: false, impactHalos: false, pointBleed: false, nightMap: false },
  heat: { width: 1.7, intensity: 0.92, routeGlow: false, impactHalos: true, pointBleed: true, nightMap: false },
  corridor: { width: 3, intensity: 0.58, routeGlow: false, impactHalos: false, pointBleed: true, nightMap: false },
  night: { width: 1.55, intensity: 1, routeGlow: false, impactHalos: true, pointBleed: true, nightMap: true },
};
let visualizationState = { preset: "signal", ...VISUAL_PRESETS.signal };
let visualizationFrame = null;

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];

const HEAT_FIELD_SCALE = 0.5;
const HEAT_COLOR_STOPS = [
  [0.38, [90, 154, 62]],
  [0.7, [191, 190, 50]],
  [0.98, [242, 169, 59]],
  [1.25, [237, 106, 60]],
  [1.65, [218, 59, 80]],
];

function interpolateHeatColor(score) {
  for (let index = 1; index < HEAT_COLOR_STOPS.length; index += 1) {
    const [upperScore, upperColor] = HEAT_COLOR_STOPS[index];
    const [lowerScore, lowerColor] = HEAT_COLOR_STOPS[index - 1];
    if (score > upperScore) continue;
    const mix = Math.max(0, Math.min(1, (score - lowerScore) / (upperScore - lowerScore)));
    return lowerColor.map((value, channel) => Math.round(
      value + (upperColor[channel] - value) * mix,
    ));
  }
  return HEAT_COLOR_STOPS.at(-1)[1];
}

const RoughnessHeatLayer = L.Layer.extend({
  options: { pane: "atlasHeat" },

  onAdd(mapInstance) {
    this._map = mapInstance;
    this._canvas = L.DomUtil.create("canvas", "roughness-heat-canvas");
    this.getPane().append(this._canvas);
    mapInstance.on("moveend zoomend resize", this.scheduleRedraw, this);
    this.scheduleRedraw();
  },

  onRemove(mapInstance) {
    mapInstance.off("moveend zoomend resize", this.scheduleRedraw, this);
    this._canvas.remove();
    window.cancelAnimationFrame(this._frame);
    this._canvas = null;
  },

  scheduleRedraw() {
    if (!this._canvas || this._frame) return;
    this._frame = window.requestAnimationFrame(() => {
      this._frame = null;
      this.redraw();
    });
  },

  redraw() {
    const size = this._map.getSize();
    const topLeft = this._map.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(this._canvas, topLeft);
    this._canvas.style.width = `${size.x}px`;
    this._canvas.style.height = `${size.y}px`;

    const width = Math.max(1, Math.ceil(size.x * HEAT_FIELD_SCALE));
    const height = Math.max(1, Math.ceil(size.y * HEAT_FIELD_SCALE));
    if (this._canvas.width !== width) this._canvas.width = width;
    if (this._canvas.height !== height) this._canvas.height = height;
    const context = this._canvas.getContext("2d");
    context.clearRect(0, 0, width, height);
    if (!visualizationState.pointBleed || !layerVisibility.roughness) return;

    const fieldWeight = new Float32Array(width * height);
    const fieldValue = new Float32Array(width * height);
    const radiusCss = 11 + Number(visualizationState.width) * 10;
    const radius = Math.max(5, Math.ceil(radiusCss * HEAT_FIELD_SCALE));
    const radiusSquared = radius * radius;
    const kernel = [];
    for (let y = -radius; y <= radius; y += 1) {
      for (let x = -radius; x <= radius; x += 1) {
        const distanceSquared = x * x + y * y;
        if (distanceSquared > radiusSquared) continue;
        kernel.push([x, y, Math.exp(-5 * distanceSquared / radiusSquared)]);
      }
    }

    const stamp = (centerX, centerY, score) => {
      const originX = Math.round(centerX);
      const originY = Math.round(centerY);
      for (const [offsetX, offsetY, weight] of kernel) {
        const x = originX + offsetX;
        const y = originY + offsetY;
        if (x < 0 || x >= width || y < 0 || y >= height) continue;
        const index = y * width + x;
        fieldWeight[index] += weight;
        fieldValue[index] += weight * score;
      }
    };

    for (const route of loadedRoutes) {
      if (!routeVisibility.get(route.id)) continue;
      const samples = route.layers.roughness ?? [];
      for (let index = 1; index < samples.length; index += 1) {
        const previous = samples[index - 1];
        const sample = samples[index];
        if (sample.t - previous.t > 3) continue;
        const start = this._map.latLngToContainerPoint([previous.latitude, previous.longitude])
          .multiplyBy(HEAT_FIELD_SCALE);
        const end = this._map.latLngToContainerPoint([sample.latitude, sample.longitude])
          .multiplyBy(HEAT_FIELD_SCALE);
        if (
          Math.max(start.x, end.x) < -radius || Math.min(start.x, end.x) > width + radius
          || Math.max(start.y, end.y) < -radius || Math.min(start.y, end.y) > height + radius
        ) continue;
        const distance = start.distanceTo(end);
        const steps = Math.max(1, Math.ceil(distance / Math.max(2, radius * 0.28)));
        for (let step = 0; step < steps; step += 1) {
          const fraction = (step + 0.5) / steps;
          stamp(
            start.x + (end.x - start.x) * fraction,
            start.y + (end.y - start.y) * fraction,
            previous.score + (sample.score - previous.score) * fraction,
          );
        }
      }
    }

    const image = context.createImageData(width, height);
    const intensity = Number(visualizationState.intensity);
    for (let index = 0; index < fieldWeight.length; index += 1) {
      const weight = fieldWeight[index];
      if (weight < 0.002) continue;
      const color = interpolateHeatColor(fieldValue[index] / weight);
      const pixel = index * 4;
      image.data[pixel] = color[0];
      image.data[pixel + 1] = color[1];
      image.data[pixel + 2] = color[2];
      image.data[pixel + 3] = Math.round(
        255 * intensity * 0.88 * (1 - Math.exp(-weight * 0.42)),
      );
    }
    context.putImageData(image, 0, 0);
  },
});
const roughnessHeatLayer = new RoughnessHeatLayer().addTo(map);

function formatDistance(meters) {
  const miles = meters / 1609.344;
  return miles < 10 ? `${miles.toFixed(1)} mi` : `${Math.round(miles)} mi`;
}

function formatDuration(seconds) {
  if (seconds < 90) return `${Math.round(seconds)} sec`;
  return `${Math.round(seconds / 60)} min`;
}

function formatSpeed(metersPerSecond) {
  return `${(metersPerSecond * 2.236936).toFixed(1)} mph`;
}

function titleForKind(kind) {
  return {
    impact: "Sharp impact",
    hardAcceleration: "Hard acceleration",
    hardBraking: "Hard braking",
    bodyMotion: "Excessive body motion",
    roughness: "Road roughness window",
    gps: "GPS sample",
    route: "Imported route",
    repeated: "Repeated problem location",
    imu: "Raw IMU vectors",
    vehicle: "Vehicle dynamics",
    pose: "Fused device pose",
    visualOdometry: "Visual odometry",
    controls: "Path curvature",
    calibration: "Vehicle calibration",
    roadVision: "Road-vision estimate",
    radar: "Radar lead state",
    sound: "Cabin sound pressure",
    magnetic: "Magnetic field",
    thermal: "Thermal and power state",
  }[kind] ?? kind;
}

function colorForRoughness(score) {
  if (score >= 1.25) return "#da3b50";
  if (score >= 1.0) return "#ed6a3c";
  if (score >= 0.72) return "#f2a93b";
  return "#91b63c";
}

function markerStyle(kind, severity = 1) {
  const color = {
    impact: "#ed6a3c",
    hardAcceleration: "#00a78e",
    hardBraking: "#da3b50",
    bodyMotion: "#7656c8",
    gps: "#3578c8",
  }[kind] ?? "#102a2d";
  return {
    radius: Math.min(9, 4 + severity * 2.2),
    color: "#ffffff",
    weight: 1.5,
    fillColor: color,
    fillOpacity: 0.9,
  };
}

function addPointBleed(group, latitude, longitude, color, radius = 12, strength = 1, source = "") {
  L.circleMarker([latitude, longitude], {
    renderer: bleedRenderer,
    interactive: false,
    radius,
    stroke: false,
    fillColor: color,
    fillOpacity: 0,
    atlasVizType: "pointBleed",
    atlasBaseRadius: radius,
    atlasStrength: strength,
    atlasSource: source,
  }).addTo(group);
}

function setMetricList(metrics) {
  const container = $("#inspector-metrics");
  container.replaceChildren();
  for (const [label, value] of metrics) {
    if (value === null || value === undefined) continue;
    const wrapper = document.createElement("div");
    const term = document.createElement("dt");
    const description = document.createElement("dd");
    term.textContent = label;
    description.textContent = value;
    wrapper.append(term, description);
    container.append(wrapper);
  }
}

function inspectObservation(kicker, title, copy, metrics) {
  $("#inspector-kicker").textContent = kicker;
  $("#inspector-title").textContent = title;
  $("#inspector-copy").textContent = copy;
  setMetricList(metrics);
  $("#inspector").classList.add("visible");
}

function inspectEvent(event, route) {
  const metrics = [
    ["Drive", route.label],
    ["Route time", `${event.t.toFixed(1)} s`],
    ["Severity", `${event.severity.toFixed(2)} × threshold`],
  ];
  if (event.speedMps !== undefined) metrics.push(["Vehicle speed", formatSpeed(event.speedMps)]);
  if (event.peakVerticalMps2 !== undefined) metrics.push(["Vertical peak", `${event.peakVerticalMps2.toFixed(2)} m/s²`]);
  if (event.peakAccelerationMps2 !== undefined) metrics.push(["Longitudinal peak", `${event.peakAccelerationMps2.toFixed(2)} m/s²`]);
  if (event.peakRollPitchRateRadS !== undefined) metrics.push(["Roll/pitch rate", `${event.peakRollPitchRateRadS.toFixed(3)} rad/s`]);
  if (event.durationS !== undefined) metrics.push(["Duration", `${event.durationS.toFixed(2)} s`]);

  inspectObservation(
    `Driver ${route.driverId}`,
    titleForKind(event.kind),
    event.kind === "impact"
      ? "A short vertical acceleration peak exceeded this route’s adaptive noise threshold."
      : "This interval crossed the configured screening threshold.",
    metrics,
  );
}

function inspectRoughness(sample, route) {
  inspectObservation(
    `Driver ${route.driverId}`,
    titleForKind("roughness"),
    sample.isRough
      ? "This two-second window crossed the route-adaptive roughness threshold."
      : "This point shows the local vertical-vibration baseline.",
    [
      ["Drive", route.label],
      ["Route time", `${sample.t.toFixed(1)} s`],
      ["RMS vibration", `${sample.rmsMps2.toFixed(3)} m/s²`],
      ["Peak vibration", `${sample.peakMps2.toFixed(2)} m/s²`],
      ["Relative score", `${sample.score.toFixed(2)} × threshold`],
      ["Vehicle speed", formatSpeed(sample.speedMps)],
    ],
  );
}

function inspectBodyMotion(sample, route) {
  inspectObservation(
    `Driver ${route.driverId}`,
    titleForKind("bodyMotion"),
    "Roll and pitch angular velocity summarize vehicle-body activity without counting normal yaw motion.",
    [
      ["Drive", route.label],
      ["Route time", `${sample.t.toFixed(1)} s`],
      ["RMS rate", `${sample.rmsRadS.toFixed(3)} rad/s`],
      ["Peak rate", `${sample.peakRadS.toFixed(3)} rad/s`],
      ["Relative score", `${sample.score.toFixed(2)} × threshold`],
    ],
  );
}

function inspectGps(point, route) {
  inspectObservation(
    `Driver ${route.driverId}`,
    titleForKind("gps"),
    `Location was recorded by ${route.source.locationService}; event positions between fixes are linearly interpolated.`,
    [
      ["Drive", route.label],
      ["Route time", `${point.t.toFixed(1)} s`],
      ["Speed", formatSpeed(point.speed)],
      ["Bearing", `${point.bearing.toFixed(0)}°`],
      ["Accuracy", point.horizontalAccuracy ? `${point.horizontalAccuracy.toFixed(1)} m` : "Not reported"],
      ["Vertical accuracy", point.verticalAccuracy ? `${point.verticalAccuracy.toFixed(1)} m` : "Not reported"],
      ["Speed accuracy", point.speedAccuracy ? `${point.speedAccuracy.toFixed(2)} m/s` : "Not reported"],
      ["Satellites", point.satelliteCount ?? "Not reported"],
    ],
  );
}

function humanizeKey(key) {
  return key
    .replace(/([A-Z])/g, " $1")
    .replace(/^./, (character) => character.toUpperCase())
    .replace("Mps2", "m/s²")
    .replace("Mps", "m/s")
    .replace("Rad S", "rad/s")
    .replace("Deg S", "deg/s")
    .replace("Per M", "1/m");
}

function formatTelemetryValue(value) {
  if (Array.isArray(value)) return value.map((item) => typeof item === "number" ? item.toFixed(3) : item).join(", ");
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
  return String(value);
}

function inspectTelemetry(kind, sample, route) {
  const metrics = [
    ["Drive", route.label],
    ["Route time", `${sample.t.toFixed(1)} s`],
    ["Source", sample.service],
  ];
  for (const [key, value] of Object.entries(sample)) {
    if (["t", "latitude", "longitude", "service"].includes(key)) continue;
    metrics.push([humanizeKey(key), formatTelemetryValue(value)]);
  }
  inspectObservation(
    `Driver ${route.driverId}`,
    titleForKind(kind),
    "A compact, geolocated sample from the original rlog. High-rate streams are downsampled for browser performance; full-rate analysis remains in Python.",
    metrics,
  );
}

function createRouteLayers(route, routeIndex) {
  const color = ROUTE_COLORS[routeIndex % ROUTE_COLORS.length];
  const layers = Object.fromEntries(LAYER_KEYS.map((key) => [key, L.layerGroup()]));
  const latLngs = route.track.map((point) => [point.latitude, point.longitude]);

  const traceGlow = L.polyline(latLngs, {
    renderer: glowRenderer,
    interactive: false,
    color,
    weight: 18,
    opacity: 0,
    lineCap: "round",
    atlasVizType: "routeGlow",
  });
  traceGlow.addTo(layers.route);

  const trace = L.polyline(latLngs, {
    color,
    weight: 4,
    opacity: 0.82,
    lineCap: "round",
    atlasVizType: "routeTrace",
  }).bindTooltip(route.label, { className: "road-tooltip", sticky: true });
  trace.on("click", () => {
    inspectObservation(
      `Driver ${route.driverId}`,
      titleForKind("route"),
      `${route.source.locationService} provided the absolute position trace for this cached rlog.`,
      [
        ["Distance", formatDistance(route.summary.distanceM)],
        ["Duration", formatDuration(route.summary.durationS)],
        ["Top GPS speed", formatSpeed(route.summary.maximumSpeedMps)],
        ["Platform", route.metadata.platform || "Unknown"],
      ],
    );
  });
  trace.addTo(layers.route);

  let previousRoughness = null;
  for (const sample of route.layers.roughness) {
    if (previousRoughness && sample.t - previousRoughness.t <= 3) {
      const heatSegment = L.polyline([
        [previousRoughness.latitude, previousRoughness.longitude],
        [sample.latitude, sample.longitude],
      ], {
        color: colorForRoughness((previousRoughness.score + sample.score) / 2),
        weight: 6,
        opacity: 0.78,
        lineCap: "round",
        atlasVizType: "roughnessSegment",
        atlasScore: (previousRoughness.score + sample.score) / 2,
      });
      heatSegment.bindTooltip(`${sample.rmsMps2.toFixed(2)} m/s² RMS`, { className: "road-tooltip" });
      heatSegment.on("click", () => inspectRoughness(sample, route));
      heatSegment.addTo(layers.roughness);
    }
    previousRoughness = sample;
    if (!sample.isRough) continue;
    addPointBleed(
      layers.roughness,
      sample.latitude,
      sample.longitude,
      colorForRoughness(sample.score),
      13,
      Math.min(1.5, sample.score),
      "roughness",
    );
    const marker = L.circleMarker([sample.latitude, sample.longitude], {
      radius: 4.8,
      color: colorForRoughness(sample.score),
      weight: 2,
      opacity: 0.95,
      fillColor: colorForRoughness(sample.score),
      fillOpacity: 0.9,
      atlasVizType: "roughnessPoint",
      atlasScore: sample.score,
    });
    marker.bindTooltip(`${sample.rmsMps2.toFixed(2)} m/s² RMS`, { className: "road-tooltip" });
    marker.on("click", () => inspectRoughness(sample, route));
    marker.addTo(layers.roughness);
  }

  for (const event of route.layers.events) {
    if (!(event.kind in layers)) continue;
    const style = markerStyle(event.kind, event.severity);
    addPointBleed(
      layers[event.kind],
      event.latitude,
      event.longitude,
      style.fillColor,
      14 + Math.min(8, event.severity * 3),
      Math.min(1.6, event.severity),
    );
    if (event.kind === "impact") {
      const halo = L.circleMarker([event.latitude, event.longitude], {
        renderer: glowRenderer,
        interactive: false,
        radius: 13 + event.severity * 8,
        stroke: false,
        fillColor: style.fillColor,
        fillOpacity: 0,
        atlasVizType: "impactHalo",
        atlasSeverity: event.severity,
      });
      halo.addTo(layers.impact);
    }
    const marker = L.circleMarker([event.latitude, event.longitude], {
      ...style,
      atlasVizType: "eventPoint",
      atlasSeverity: event.severity,
    });
    marker.bindTooltip(titleForKind(event.kind), { className: "road-tooltip" });
    marker.on("click", () => inspectEvent(event, route));
    marker.addTo(layers[event.kind]);
  }

  for (const sample of route.layers.bodyMotion) {
    if (sample.score < 0.18) continue;
    addPointBleed(
      layers.bodyMotion,
      sample.latitude,
      sample.longitude,
      markerStyle("bodyMotion").fillColor,
      11,
      Math.min(1.4, 0.6 + sample.score),
    );
    const marker = L.circleMarker([sample.latitude, sample.longitude], {
      ...markerStyle("bodyMotion", sample.score),
      radius: Math.min(6.5, 2.4 + sample.score * 2),
      fillOpacity: Math.min(0.78, 0.3 + sample.score * 0.35),
      weight: sample.isExcessive ? 2 : 0.7,
      atlasVizType: "samplePoint",
      atlasBaseFillOpacity: Math.min(0.78, 0.3 + sample.score * 0.35),
      atlasBaseOpacity: 1,
    });
    marker.bindTooltip(`${sample.rmsRadS.toFixed(3)} rad/s RMS`, { className: "road-tooltip" });
    marker.on("click", () => inspectBodyMotion(sample, route));
    marker.addTo(layers.bodyMotion);
  }

  for (const point of route.track) {
    addPointBleed(layers.gps, point.latitude, point.longitude, markerStyle("gps").fillColor, 9, 0.55);
    const marker = L.circleMarker([point.latitude, point.longitude], {
      ...markerStyle("gps", 0.4),
      radius: 2.7,
      fillOpacity: 0.72,
      weight: 0.7,
      atlasVizType: "samplePoint",
      atlasBaseFillOpacity: 0.72,
      atlasBaseOpacity: 1,
    });
    marker.on("click", () => inspectGps(point, route));
    marker.addTo(layers.gps);
  }

  for (const kind of TELEMETRY_KEYS) {
    for (const sample of route.layers.telemetry?.[kind] ?? []) {
      const emphasized = kind === "radar" && sample.leadDetected;
      addPointBleed(
        layers[kind],
        sample.latitude,
        sample.longitude,
        TELEMETRY_COLORS[kind],
        emphasized ? 13 : 9,
        emphasized ? 1.3 : 0.55,
      );
      const marker = L.circleMarker([sample.latitude, sample.longitude], {
        radius: emphasized ? 4.6 : 2.8,
        color: "#ffffff",
        weight: emphasized ? 1.5 : 0.6,
        fillColor: TELEMETRY_COLORS[kind],
        fillOpacity: emphasized ? 0.9 : 0.62,
        atlasVizType: "samplePoint",
        atlasBaseFillOpacity: emphasized ? 0.9 : 0.62,
        atlasBaseOpacity: 1,
      });
      marker.bindTooltip(`${titleForKind(kind)} · ${sample.service}`, { className: "road-tooltip" });
      marker.on("click", () => inspectTelemetry(kind, sample, route));
      marker.addTo(layers[kind]);
    }
  }

  routeLayers.set(route.id, layers);
  routeVisibility.set(route.id, true);
  return color;
}

function syncLayers() {
  for (const [routeId, layers] of routeLayers) {
    const routeIsVisible = routeVisibility.get(routeId);
    for (const key of LAYER_KEYS) {
      const shouldShow = routeIsVisible && layerVisibility[key];
      if (shouldShow && !map.hasLayer(layers[key])) {
        layers[key].addTo(map);
      } else if (!shouldShow && map.hasLayer(layers[key])) {
        map.removeLayer(layers[key]);
      }
    }
  }

  const repeatedEnabled = $("[data-layer=\"repeated\"]").checked;
  if (repeatedEnabled && !map.hasLayer(repeatedLayer)) repeatedLayer.addTo(map);
  if (!repeatedEnabled && map.hasLayer(repeatedLayer)) map.removeLayer(repeatedLayer);
  roughnessHeatLayer.scheduleRedraw();
}

function applyVisualizationStyles(save = true) {
  const width = Number(visualizationState.width);
  const intensity = Number(visualizationState.intensity);
  for (const layers of routeLayers.values()) {
    for (const group of Object.values(layers)) {
      group.eachLayer((layer) => {
        const vizType = layer.options?.atlasVizType;
        if (!vizType || typeof layer.setStyle !== "function") return;
        if (vizType === "routeTrace") {
          layer.setStyle({
            weight: 4 * width,
            opacity: Math.min(1, 0.35 + intensity * 0.6),
          });
        } else if (vizType === "routeGlow") {
          layer.setStyle({
            weight: 18 * width,
            opacity: visualizationState.routeGlow ? 0.2 * intensity : 0,
          });
        } else if (vizType === "roughnessSegment") {
          layer.setStyle({
            weight: 6 * width,
            opacity: visualizationState.pointBleed
              ? 0
              : Math.min(1, 0.18 + intensity * 0.72),
            lineCap: "round",
          });
        } else if (vizType === "roughnessPoint") {
          layer.setRadius(4.8 * Math.sqrt(width));
          layer.setStyle({
            opacity: visualizationState.pointBleed ? 0 : 0.95,
            fillOpacity: visualizationState.pointBleed ? 0 : Math.min(1, 0.28 + intensity * 0.72),
          });
        } else if (vizType === "pointBleed") {
          const baseRadius = Number(layer.options.atlasBaseRadius ?? 12);
          const strength = Number(layer.options.atlasStrength ?? 1);
          layer.setRadius(baseRadius * Math.sqrt(width));
          layer.setStyle({
            fillOpacity: visualizationState.pointBleed && layer.options.atlasSource !== "roughness"
              ? Math.min(0.22, 0.08 * intensity * strength)
              : 0,
          });
        } else if (vizType === "samplePoint") {
          layer.setStyle({
            opacity: visualizationState.pointBleed
              ? 0
              : Number(layer.options.atlasBaseOpacity ?? 1),
            fillOpacity: visualizationState.pointBleed
              ? 0
              : Number(layer.options.atlasBaseFillOpacity ?? 0.7),
          });
        } else if (vizType === "impactHalo") {
          const severity = Number(layer.options.atlasSeverity ?? 1);
          layer.setRadius((13 + severity * 8) * Math.sqrt(width));
          layer.setStyle({ fillOpacity: visualizationState.impactHalos ? 0.13 * intensity : 0 });
        } else if (vizType === "eventPoint") {
          const severity = Number(layer.options.atlasSeverity ?? 1);
          layer.setRadius(Math.min(12, (4 + severity * 2.2) * Math.sqrt(width)));
          layer.setStyle({
            opacity: visualizationState.pointBleed ? 0 : 1,
            fillOpacity: visualizationState.pointBleed ? 0 : Math.min(1, 0.34 + intensity * 0.66),
          });
        }
      });
    }
  }

  $(".map-panel").classList.toggle("viz-night", visualizationState.nightMap);
  roughnessHeatLayer.scheduleRedraw();
  $("#visual-width").value = String(width);
  $("#visual-intensity").value = String(intensity);
  $("#visual-width-value").textContent = `${width.toFixed(1)}×`;
  $("#visual-intensity-value").textContent = `${Math.round(intensity * 100)}%`;
  $("#route-glow-toggle").checked = visualizationState.routeGlow;
  $("#impact-halo-toggle").checked = visualizationState.impactHalos;
  $("#point-bleed-toggle").checked = visualizationState.pointBleed;
  $("#night-map-toggle").checked = visualizationState.nightMap;
  $$("[data-viz-preset]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.vizPreset === visualizationState.preset));
  });
  if (save) {
    window.localStorage.setItem("clusterMapsVisualization", JSON.stringify(visualizationState));
  }
}

function chooseVisualizationPreset(name) {
  const preset = VISUAL_PRESETS[name];
  if (!preset) return;
  visualizationState = { preset: name, ...preset };
  applyVisualizationStyles();
}

function updateVisualizationSetting(key, value) {
  visualizationState = { ...visualizationState, preset: "custom", [key]: value };
  if (visualizationFrame !== null) return;
  visualizationFrame = window.requestAnimationFrame(() => {
    visualizationFrame = null;
    applyVisualizationStyles();
  });
}

function restoreVisualizationState() {
  try {
    const stored = JSON.parse(window.localStorage.getItem("clusterMapsVisualization"));
    if (!stored || typeof stored !== "object") return;
    if (stored.preset in VISUAL_PRESETS) {
      visualizationState = { preset: stored.preset, ...VISUAL_PRESETS[stored.preset] };
      return;
    }
    visualizationState = {
      preset: typeof stored.preset === "string" ? stored.preset : "custom",
      width: Math.min(3.5, Math.max(0.7, Number(stored.width) || 1)),
      intensity: Math.min(1, Math.max(0.25, Number(stored.intensity) || 0.8)),
      routeGlow: Boolean(stored.routeGlow),
      impactHalos: Boolean(stored.impactHalos),
      pointBleed: Boolean(stored.pointBleed),
      nightMap: Boolean(stored.nightMap),
    };
  } catch {
    window.localStorage.removeItem("clusterMapsVisualization");
  }
}

function createRouteCard(route, color) {
  const card = document.createElement("div");
  card.className = "route-card";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = routeVisibility.get(route.id);
  checkbox.dataset.routeId = route.id;
  checkbox.setAttribute("aria-label", `Show ${route.label}`);
  checkbox.addEventListener("change", () => {
    routeVisibility.set(route.id, checkbox.checked);
    syncLayers();
  });

  const swatch = document.createElement("span");
  swatch.className = "route-swatch";
  swatch.style.background = color;

  const copy = document.createElement("button");
  copy.type = "button";
  copy.className = "route-copy";
  const title = document.createElement("strong");
  const routeName = route.routeName || route.label;
  title.textContent = routeName;
  const details = document.createElement("small");
  const segmentText = route.metadata.segmentCount ? `${route.metadata.segmentCount} segments · ` : "";
  const labelText = route.label !== routeName ? `${route.label} · ` : "";
  const hasRoadMotion = route.summary.maximumSpeedMps >= 2.5 && route.summary.distanceM >= 100;
  const motionText = hasRoadMotion ? "" : "stationary session · ";
  details.textContent = `${labelText}Driver ${route.driverId} · ${segmentText}${motionText}${formatDistance(route.summary.distanceM)} · ${route.summary.eventCounts.impact} impacts`;
  copy.append(title, details);
  copy.addEventListener("click", () => {
    const bounds = L.latLngBounds(route.track.map((point) => [point.latitude, point.longitude]));
    map.fitBounds(bounds, { padding: [45, 45], maxZoom: 17 });
  });

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "route-delete";
  remove.textContent = "×";
  remove.setAttribute("aria-label", `Delete ${routeName}`);
  remove.addEventListener("click", async () => {
    if (!window.confirm(`Delete ${routeName} from this local atlas? The source rlogs are not changed.`)) return;
    remove.disabled = true;
    try {
      const response = await fetch("/api/remove", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Road-Quality-Request": "1",
        },
        body: JSON.stringify({ cacheId: route.id }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || `Delete returned ${response.status}`);
      window.location.reload();
    } catch (error) {
      remove.disabled = false;
      $("#route-manager-status").textContent = error.message;
    }
  });

  card.append(checkbox, swatch, copy, remove);
  return card;
}

function renderRepeatedLocations(clusters) {
  repeatedLayer.clearLayers();
  for (const cluster of clusters) {
    const marker = L.circleMarker([cluster.latitude, cluster.longitude], {
      radius: Math.min(14, 7 + cluster.routeCount),
      color: "#da3b50",
      weight: 3,
      fillColor: "#ffffff",
      fillOpacity: 0.76,
      dashArray: "2 3",
    });
    marker.bindTooltip(`${cluster.routeCount} routes · ${cluster.observationCount} observations`, { className: "road-tooltip" });
    marker.on("click", () => {
      inspectObservation(
        `${cluster.driverCount} independent driver${cluster.driverCount === 1 ? "" : "s"}`,
        titleForKind("repeated"),
        "Nearby impact or roughness observations were clustered across independently imported routes.",
        [
          ["Routes", String(cluster.routeCount)],
          ["Drivers", String(cluster.driverCount)],
          ["Observations", String(cluster.observationCount)],
          ["Signal types", cluster.problemTypes.join(", ")],
          ["Max severity", `${cluster.maximumSeverity.toFixed(2)} × threshold`],
        ],
      );
    });
    marker.addTo(repeatedLayer);
  }
}

function updateCounts(index, routes) {
  const totalDistance = routes.reduce((sum, route) => sum + route.summary.distanceM, 0);
  const eventCounts = Object.fromEntries(LAYER_KEYS.map((key) => [key, 0]));
  eventCounts.route = routes.length;
  eventCounts.gps = routes.reduce((sum, route) => sum + route.track.length, 0);

  let roughObservations = 0;
  for (const route of routes) {
    roughObservations += route.layers.roughness.length;
    for (const event of route.layers.events) {
      if (event.kind !== "bodyMotion") eventCounts[event.kind] += 1;
    }
    eventCounts.bodyMotion += route.layers.bodyMotion.filter((point) => point.isExcessive).length;
    for (const key of TELEMETRY_KEYS) {
      eventCounts[key] += route.layers.telemetry?.[key]?.length ?? 0;
    }
  }
  eventCounts.roughness = roughObservations;

  $("#route-count").textContent = String(index.routeCount);
  $("#driver-count").textContent = String(index.driverCount);
  $("#distance-total").textContent = formatDistance(totalDistance);
  $("#observation-count").textContent = String(
    eventCounts.roughness + eventCounts.impact + eventCounts.hardAcceleration
    + eventCounts.hardBraking + eventCounts.bodyMotion,
  );
  for (const [key, count] of Object.entries(eventCounts)) {
    const output = $(`[data-count="${key}"]`);
    if (output) output.textContent = String(count);
  }
  $("[data-count=\"repeated\"]").textContent = String(index.repeatedLocations.length);
}

function renderServiceCatalog(routes) {
  const services = new Map();
  for (const route of routes) {
    for (const entry of route.source.serviceCatalog ?? []) {
      const aggregate = services.get(entry.service) ?? {
        ...entry,
        count: 0,
        rateHz: 0,
        routeCount: 0,
      };
      aggregate.count += entry.count;
      aggregate.rateHz = Math.max(aggregate.rateHz, entry.rateHz);
      aggregate.routeCount += 1;
      aggregate.browserExported ||= entry.browserExported;
      services.set(entry.service, aggregate);
    }
  }

  const entries = [...services.values()].sort((a, b) => {
    if (a.browserExported !== b.browserExported) return a.browserExported ? -1 : 1;
    return a.service.localeCompare(b.service);
  });
  $("#service-count").textContent = String(entries.length);
  const list = $("#service-list");
  list.replaceChildren();
  for (const entry of entries) {
    const item = document.createElement("div");
    item.className = "service-item";
    const name = document.createElement("strong");
    name.textContent = entry.service;
    const rate = document.createElement("output");
    rate.textContent = entry.rateHz > 0 ? `${entry.rateHz.toFixed(1)} Hz` : `${entry.count} msg`;
    const description = document.createElement("span");
    description.textContent = `${entry.description} · `;
    const state = document.createElement("em");
    state.textContent = entry.browserExported ? `mapped as ${entry.mapLayer}` : "inventory only";
    description.append(state);
    item.append(name, rate, description);
    list.append(item);
  }
}

function fitAll() {
  if (fullBounds?.isValid()) {
    map.fitBounds(fullBounds, { padding: [42, 42], maxZoom: 16 });
  }
}

function setAllRouteVisibility(visible) {
  for (const route of loadedRoutes) routeVisibility.set(route.id, visible);
  $$("#route-list input[data-route-id]").forEach((checkbox) => {
    checkbox.checked = visible;
  });
  syncLayers();
}

async function loadAtlas() {
  try {
    const indexResponse = await fetch("data/index.json", { cache: "no-store" });
    if (!indexResponse.ok) throw new Error(`index.json returned ${indexResponse.status}`);
    atlasIndex = await indexResponse.json();
    if (atlasIndex.schemaVersion !== 2) throw new Error("Unsupported cache schema");

    const routeResponses = await Promise.all(atlasIndex.routes.map(async (routeEntry) => {
      const response = await fetch(`data/${routeEntry.file}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`${routeEntry.file} returned ${response.status}`);
      return response.json();
    }));
    loadedRoutes = routeResponses;

    const list = $("#route-list");
    list.replaceChildren();
    fullBounds = L.latLngBounds([]);
    loadedRoutes.forEach((route, index) => {
      const color = createRouteLayers(route, index);
      list.append(createRouteCard(route, color));
      if (routeVisibility.get(route.id)) {
        for (const point of route.track) fullBounds.extend([point.latitude, point.longitude]);
      }
    });
    if (!fullBounds.isValid()) {
      for (const route of loadedRoutes) {
        for (const point of route.track) fullBounds.extend([point.latitude, point.longitude]);
      }
    }
    renderRepeatedLocations(atlasIndex.repeatedLocations);
    updateCounts(atlasIndex, loadedRoutes);
    renderServiceCatalog(loadedRoutes);
    applyVisualizationStyles(false);
    syncLayers();
    fitAll();

    $(".data-state").classList.add("ready");
    $("#data-status").textContent = `Cache ready · ${new Date(atlasIndex.generatedAt).toLocaleString()}`;
    if (loadedRoutes.length === 0) {
      $("#map-message").hidden = false;
      $("#map-message strong").textContent = "No routes imported yet";
    }
  } catch (error) {
    console.error(error);
    $(".data-state").classList.add("error");
    $("#data-status").textContent = "Cache unavailable";
    $("#map-message").hidden = false;
    $("#map-message span").textContent = `The local cache could not be loaded: ${error.message}`;
    map.setView([39.5, -98.35], 4);
  }
}

function selectedSegments() {
  return $$("#segment-list input:checked").map((input) => Number(input.value));
}

async function discoverSegments(event) {
  event.preventDefault();
  const route = $("#route-input").value.trim();
  if (!route) return;
  $("#discover-route").disabled = true;
  $("#route-manager-status").textContent = "Looking up available segments…";
  try {
    const response = await fetch(`/api/segments?route=${encodeURIComponent(route)}`, { cache: "no-store" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `Segment lookup returned ${response.status}`);
    $("#route-input").value = payload.route;
    const list = $("#segment-list");
    list.replaceChildren();
    for (const segment of payload.segments) {
      const option = document.createElement("label");
      option.className = "segment-option";
      const input = document.createElement("input");
      input.type = "checkbox";
      input.value = String(segment.index);
      input.checked = true;
      const text = document.createElement("span");
      text.textContent = String(segment.index);
      option.append(input, text);
      list.append(option);
    }
    $("#segment-summary").textContent = `${payload.segmentCount} available segments`;
    $("#segment-picker").hidden = false;
    $("#route-manager-status").textContent = "Choose segments, then start the local import.";
  } catch (error) {
    $("#segment-picker").hidden = true;
    $("#route-manager-status").textContent = error.message;
  } finally {
    $("#discover-route").disabled = false;
  }
}

async function pollImport(jobId) {
  const response = await fetch(`/api/jobs/${jobId}`, { cache: "no-store" });
  const job = await response.json();
  if (!response.ok) {
    if (response.status === 404) {
      window.localStorage.removeItem("roadQualityImportJob");
      $("#import-progress").hidden = true;
    }
    throw new Error(job.error || `Progress check returned ${response.status}`);
  }
  $("#progress-bar").value = job.percent;
  $("#progress-bar").textContent = `${job.percent}%`;
  $("#progress-percent").textContent = `${job.percent}%`;
  $("#progress-stage").textContent = job.stage;
  $("#progress-detail").textContent = job.totalSegments
    ? `${job.completedSegments} of ${job.totalSegments} segments parsed`
    : "Preparing full-rlog analysis";
  if (job.status === "complete") {
    window.localStorage.removeItem("roadQualityImportJob");
    $("#route-manager-status").textContent = "Import complete. Refreshing the atlas…";
    window.setTimeout(() => window.location.reload(), 650);
    return;
  }
  if (job.status === "error") throw new Error(job.error || "Import failed");
  window.setTimeout(() => pollImport(jobId).catch(showImportError), 500);
}

function showImportError(error) {
  $("#route-manager-status").textContent = error.message;
  $("#progress-stage").textContent = "Import failed";
  $("#import-selected").disabled = false;
}

async function importSelectedSegments() {
  const segments = selectedSegments();
  if (!segments.length) {
    $("#route-manager-status").textContent = "Select at least one segment.";
    return;
  }
  $("#import-selected").disabled = true;
  $("#import-progress").hidden = false;
  $("#progress-bar").value = 0;
  $("#progress-percent").textContent = "0%";
  $("#progress-stage").textContent = "Queuing import";
  $("#route-manager-status").textContent = "The page can stay open while full rlogs are processed.";
  try {
    const response = await fetch("/api/import", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Road-Quality-Request": "1",
      },
      body: JSON.stringify({
        route: $("#route-input").value.trim(),
        label: $("#route-label").value.trim(),
        segments,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || `Import request returned ${response.status}`);
    window.localStorage.setItem("roadQualityImportJob", payload.jobId);
    await pollImport(payload.jobId);
  } catch (error) {
    showImportError(error);
  }
}

$$("[data-layer]").forEach((input) => {
  input.addEventListener("change", () => {
    if (input.dataset.layer !== "repeated") layerVisibility[input.dataset.layer] = input.checked;
    syncLayers();
  });
});

const BASEMAPS = {
  streets: {
    layer: streetTiles,
    note: "OpenStreetMap streets · sensor overlays remain interactive.",
  },
  satellite: {
    layer: satelliteTiles,
    note: "Esri World Imagery · sensor overlays remain interactive.",
  },
  data: {
    layer: sensorCanvas,
    note: "Basemap hidden · coordinate grid and sensor overlays only.",
  },
};

function setBasemap(mode, save = true) {
  const selectedMode = mode in BASEMAPS ? mode : "streets";
  for (const { layer } of Object.values(BASEMAPS)) {
    if (map.hasLayer(layer)) map.removeLayer(layer);
  }
  BASEMAPS[selectedMode].layer.addTo(map);
  $("#map").classList.toggle("sensor-canvas", selectedMode === "data");
  $("#map-scale-note").textContent = BASEMAPS[selectedMode].note;
  $$("[data-basemap]").forEach((button) => {
    button.setAttribute("aria-pressed", String(button.dataset.basemap === selectedMode));
  });
  if (save) window.localStorage.setItem("clusterMapsBasemap", selectedMode);
}

$$("[data-basemap]").forEach((button) => {
  button.addEventListener("click", () => setBasemap(button.dataset.basemap));
});
$("#fit-all").addEventListener("click", fitAll);
$("#select-all-routes").addEventListener("click", () => setAllRouteVisibility(true));
$("#unselect-all-routes").addEventListener("click", () => setAllRouteVisibility(false));
$("#reset-view").addEventListener("click", fitAll);
$("#visuals-toggle").addEventListener("click", () => {
  const panel = $("#visuals-panel");
  panel.hidden = !panel.hidden;
  $("#visuals-toggle").setAttribute("aria-expanded", String(!panel.hidden));
});
$("#visuals-close").addEventListener("click", () => {
  $("#visuals-panel").hidden = true;
  $("#visuals-toggle").setAttribute("aria-expanded", "false");
});
$$("[data-viz-preset]").forEach((button) => {
  button.addEventListener("click", () => chooseVisualizationPreset(button.dataset.vizPreset));
});
$("#visual-width").addEventListener("input", (event) => {
  updateVisualizationSetting("width", Number(event.target.value));
});
$("#visual-intensity").addEventListener("input", (event) => {
  updateVisualizationSetting("intensity", Number(event.target.value));
});
$("#route-glow-toggle").addEventListener("change", (event) => {
  updateVisualizationSetting("routeGlow", event.target.checked);
});
$("#impact-halo-toggle").addEventListener("change", (event) => {
  updateVisualizationSetting("impactHalos", event.target.checked);
});
$("#point-bleed-toggle").addEventListener("change", (event) => {
  updateVisualizationSetting("pointBleed", event.target.checked);
});
$("#night-map-toggle").addEventListener("change", (event) => {
  updateVisualizationSetting("nightMap", event.target.checked);
});
$("#inspector-close").addEventListener("click", () => $("#inspector").classList.remove("visible"));
$("#route-manager").addEventListener("submit", discoverSegments);
$("#select-all-segments").addEventListener("click", () => {
  $$("#segment-list input").forEach((input) => { input.checked = true; });
});
$("#select-no-segments").addEventListener("click", () => {
  $$("#segment-list input").forEach((input) => { input.checked = false; });
});
$("#import-selected").addEventListener("click", importSelectedSegments);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    $("#inspector").classList.remove("visible");
    $("#visuals-panel").hidden = true;
    $("#visuals-toggle").setAttribute("aria-expanded", "false");
  }
});

restoreVisualizationState();
applyVisualizationStyles(false);
setBasemap(window.localStorage.getItem("clusterMapsBasemap") || "streets", false);
loadAtlas();

const resumableJobId = window.localStorage.getItem("roadQualityImportJob");
if (resumableJobId) {
  $("#import-progress").hidden = false;
  $("#route-manager-status").textContent = "Reconnecting to the saved import job…";
  pollImport(resumableJobId).catch(showImportError);
}
