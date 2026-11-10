"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Dry run of the community uploads: writes exactly what the car would send, and
a map page that shows what would be shared and what stays on the car, into
<achievements root>/preview/. Nothing is sent anywhere.

  preview/daily-YYYY-MM-DD.json   daily report per driven day (last 14 days), at level 2
  preview/tiles.json              the next weekly tile batch (level 3)
  preview/delete.json             tiles the car would ask the server to delete, if any
  preview/map.html                open in a browser (copy it off the car first)

map.html shows your frequent stops, so it is for you only: don't share it.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from openpilot.sunnypilot.achievements.community import (LEVEL_DAILY, STOP_HOLD_DAYS, CommunityLog, Settings,
                                                         public_block)
from openpilot.sunnypilot.achievements.engine import State, achievements_root

PREVIEW_DAYS = 14


def preview_dir() -> Path:
  return achievements_root() / "preview"


def _write(path: Path, data) -> None:
  tmp = path.with_suffix(path.suffix + ".tmp")
  tmp.write_text(data if isinstance(data, str) else json.dumps(data, indent=2) + "\n")
  tmp.replace(path)


def build_preview(log: CommunityLog, state: State, today: dt.date, car: str | None, settings: Settings) -> dict:
  """Everything the preview shows, as plain data."""
  view = log.tile_view(today)
  profile = log.profile_update(today, car, settings)
  days = log.driven_days(since=today - dt.timedelta(days=PREVIEW_DAYS - 1))
  daily = [log.daily_report(d, state, LEVEL_DAILY, profile=profile if d == days[-1] else None,
                            include_undated=d == days[-1]) for d in days]
  region_days = log.region_days(today)
  return {
    "today": today.isoformat(),
    "level": settings.level,
    "daily": daily,
    "tiles": log.tile_batch(today),
    "delete": log.tile_deletes(today),
    "region": {"home": log.home_region(today), "shared": log.shared_region(today, settings),
               "choice": settings.region, "days": dict(region_days.most_common())},
    "map": {
      "shareable": sorted(view.shareable),
      "blocks": sorted({public_block(t) for t in view.shareable}),
      "held": view.held,
      "ring": sorted(view.ring),
      "frequent": sorted(view.frequent),
      "hidden": sorted(view.hidden & view.driven),
      "driven": len(view.driven),
    },
  }


def write_preview(log: CommunityLog, state: State, today: dt.date, car: str | None, settings: Settings,
                  out: Path | None = None) -> Path:
  out = out or preview_dir()
  out.mkdir(parents=True, exist_ok=True)
  data = build_preview(log, state, today, car, settings)

  for f in out.glob("daily-*.json"):
    f.unlink()
  for report in data["daily"]:
    _write(out / f"daily-{report['day']}.json", report)
  for name in ("tiles", "delete"):
    path = out / f"{name}.json"
    if data[name]:
      _write(path, data[name])
    elif path.exists():
      path.unlink()
  _write(out / "map.html", render_html(data))
  return out


def render_html(data: dict) -> str:
  blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
  return HTML.replace("__DATA__", blob).replace("__HOLD_DAYS__", str(STOP_HOLD_DAYS))


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>What your car would share</title>
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">
<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script src="https://unpkg.com/h3-js@4.1.0/dist/h3-js.umd.js"></script>
<style>
  :root { --ink:#1f2328; --muted:#59636e; --line:#d1d9e0; --bg:#f6f8fa; --send:#2563eb; --held:#9ca3af;
          --never:#dc2626; --hidden:#7c3aed; }
  * { box-sizing: border-box; }
  body { margin:0; font:15px/1.5 Inter, system-ui, sans-serif; color:var(--ink); background:#fff; }
  header { padding:20px 24px 8px; }
  h1 { font-size:22px; margin:0 0 4px; }
  .warn { background:#fff8c5; border:1px solid #d4a72c66; border-radius:8px; padding:8px 12px; margin:8px 0 0; color:#3b2300; }
  .stats { display:flex; flex-wrap:wrap; gap:8px; padding:8px 24px; }
  .stat { border:1px solid var(--line); border-radius:8px; padding:8px 12px; min-width:150px; }
  .stat b { display:block; font-size:20px; }
  .dot { display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:middle; }
  .bar { display:flex; flex-wrap:wrap; gap:8px; align-items:center; padding:8px 24px; }
  button { font:inherit; border:1px solid var(--line); background:#fff; border-radius:6px; padding:6px 12px; cursor:pointer; }
  button.on { background:var(--ink); color:#fff; border-color:var(--ink); }
  #map { height:62vh; min-height:360px; margin:0 24px; border:1px solid var(--line); border-radius:8px; }
  main { padding:8px 24px 40px; display:grid; align-items:start; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:16px; }
  section { border:1px solid var(--line); border-radius:8px; padding:12px 16px; }
  h2 { font-size:16px; margin:0 0 6px; }
  p { margin:4px 0; color:var(--muted); }
  pre { background:var(--bg); border-radius:6px; padding:10px; overflow:auto; font-size:12px; max-height:340px; }
</style>
</head>
<body>
<header>
  <h1>What your car would share</h1>
  <div id="sub"></div>
  <div class="warn">Dry run: nothing has been sent. This page marks your frequent stops, so keep it to yourself.</div>
</header>
<div class="stats" id="stats"></div>
<div class="bar">
  <button id="mine" class="on">Your map (6 km tiles)</button>
  <button id="others">What others see (45 km blocks)</button>
  <label><input type="checkbox" id="kept" checked> Show what stays on the car</label>
</div>
<div id="map"></div>
<main>
  <section><h2>Home region</h2><div id="region"></div></section>
  <section><h2>Latest daily report</h2>
    <p>Level 1 sends <code>unlocks</code> and <code>totals</code>. Level 2 adds <code>daily</code> and <code>profile</code>.</p>
    <pre id="daily"></pre></section>
  <section><h2>Next weekly tile batch (level 3)</h2>
    <p>Sorted tile ids, no dates, sent separately from the daily report.</p><pre id="tiles"></pre></section>
  <section><h2>Delete requests</h2>
    <p>Tiles already sent that became private later (moved house, new job, hidden).</p><pre id="delete"></pre></section>
</main>
<script>
const D = __DATA__;
const M = D.map;
const held = Object.keys(M.held);
const never = M.ring;
document.getElementById('sub').textContent =
  `As of ${D.today}. Sharing level on this car: ${D.level} (0 = off). The preview always shows level 3.`;
const stat = (color, n, label) =>
  `<div class="stat"><b>${n}</b><span class="dot" style="background:${color}"></span>${label}</div>`;
document.getElementById('stats').innerHTML =
  stat('#6e7781', M.driven, 'tiles driven') +
  stat('var(--send)', M.shareable.length, 'would be shared') +
  stat('var(--held)', held.length, 'drive start/end tiles waiting __HOLD_DAYS__ days') +
  stat('var(--never)', never.length, `never leave the car (${M.frequent.length} frequent stops + the tiles around them)`) +
  stat('var(--hidden)', M.hidden.length, 'hidden by you') +
  stat('var(--send)', M.blocks.length, '45 km blocks others would see');

const r = D.region;
const days = Object.entries(r.days).map(([k, v]) => `${k}: ${v} day${v === 1 ? '' : 's'}`).join(', ') || 'no engaged days yet';
document.getElementById('region').innerHTML =
  `<p>Detected: <b>${r.home || 'none yet'}</b> (${days}, last 90 days).</p>` +
  `<p>Would be shared as: <b>${r.shared || 'nothing'}</b> (setting: ${r.choice}).</p>`;
const latest = D.daily.length ? D.daily[D.daily.length - 1] : null;
document.getElementById('daily').textContent = latest ? JSON.stringify(latest, null, 2) : 'No driving yet.';
const t = D.tiles;
document.getElementById('tiles').textContent = t ?
  JSON.stringify({...t, tiles: t.tiles.slice(0, 12).concat(t.tiles.length > 12 ? [`... ${t.tiles.length - 12} more`] : [])}, null, 2) :
  'Nothing new to send.';
document.getElementById('delete').textContent = D.delete ? JSON.stringify(D.delete, null, 2) : 'None.';

const fc = (cells, kind) => ({type: 'FeatureCollection', features: cells.map(c => {
  const ring = h3.cellToBoundary(c, true); ring.push(ring[0]);
  return {type: 'Feature', properties: {kind, cell: c, until: M.held[c] || ''}, geometry: {type: 'Polygon', coordinates: [ring]}};
})});
const all = [...M.shareable, ...held, ...never, ...M.hidden];
const map = new maplibregl.Map({
  container: 'map',
  style: {version: 8, sources: {osm: {type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
          tileSize: 256, attribution: '&copy; OpenStreetMap contributors'}},
          layers: [{id: 'osm', type: 'raster', source: 'osm', paint: {'raster-saturation': -0.8, 'raster-opacity': 0.8}}]},
  center: [-83, 40], zoom: 5,
});
map.on('load', () => {
  const add = (id, data, color, fill, dash) => {
    map.addSource(id, {type: 'geojson', data});
    map.addLayer({id: id + '-fill', type: 'fill', source: id, paint: {'fill-color': color, 'fill-opacity': fill}});
    map.addLayer({id: id + '-line', type: 'line', source: id,
                  paint: {'line-color': color, 'line-width': 1.2, ...(dash ? {'line-dasharray': [2, 2]} : {})}});
  };
  add('blocks', fc(M.blocks, 'block'), '#2563eb', 0.35);
  add('mine', fc(M.shareable, 'shared'), '#2563eb', 0.35);
  add('held', fc(held, 'held'), '#9ca3af', 0.45, true);
  add('never', fc(never, 'never'), '#dc2626', 0.25, true);
  add('hidden', fc(M.hidden, 'hidden'), '#7c3aed', 0.3, true);
  const kept = ['held', 'never', 'hidden'];
  const show = (id, on) => ['-fill', '-line'].forEach(s => map.setLayoutProperty(id + s, 'visibility', on ? 'visible' : 'none'));
  const fit = cells => {
    if (!cells.length) return;
    const pts = cells.flatMap(c => h3.cellToBoundary(c));
    const lats = pts.map(p => p[0]), lngs = pts.map(p => p[1]);
    map.fitBounds([[Math.min(...lngs), Math.min(...lats)], [Math.max(...lngs), Math.max(...lats)]], {padding: 40, duration: 0});
  };
  let mode = 'mine';
  const refresh = () => {
    show('mine', mode === 'mine'); show('blocks', mode === 'others');
    const k = document.getElementById('kept').checked && mode === 'mine';
    kept.forEach(id => show(id, k));
    document.getElementById('mine').classList.toggle('on', mode === 'mine');
    document.getElementById('others').classList.toggle('on', mode === 'others');
  };
  document.getElementById('mine').onclick = () => { mode = 'mine'; refresh(); fit(all); };
  document.getElementById('others').onclick = () => { mode = 'others'; refresh(); fit(M.blocks); };
  document.getElementById('kept').onchange = refresh;
  refresh();
  fit(all);
  const label = {shared: 'Would be shared', held: 'Waiting until', never: 'Never leaves the car', hidden: 'Hidden by you',
                 block: 'What others see'};
  map.on('click', e => {
    const f = map.queryRenderedFeatures(e.point).find(x => x.properties.kind);
    if (!f) return;
    new maplibregl.Popup().setLngLat(e.lngLat)
      .setHTML(`${label[f.properties.kind]} ${f.properties.until}<br><code>${f.properties.cell}</code>`).addTo(map);
  });
});
</script>
</body>
</html>
"""
