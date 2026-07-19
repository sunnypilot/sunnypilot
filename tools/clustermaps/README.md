# clustermaps

clustermaps is an offline, read-only route-analysis tool for full openpilot/sunnypilot rlogs. It converts high-rate IMU, vehicle-state, pose, and GPS messages into a compact per-route JSON cache, GeoJSON exports, and a static HTML5 map.

## Quick start

From the repository root:

```bash
.venv/bin/python tools/clustermaps/build_map.py \
  0000000000000000/00000000--0000000000 \
  --label "Complete sample route · 13 segments" \
  --serve
```

Then open [http://127.0.0.1:8765](http://127.0.0.1:8765).

The page includes a local Route Manager. Paste a route, load its available segment list, select segments, and watch the checkpointed import progress. Imports survive a server restart: each completed segment is stored separately under the gitignored data directory, and the next `--serve` run resumes unfinished jobs before assembling one route-level map entry.

The identifier determines how much is imported:

- `DONGLE/ROUTE` imports every available segment in the route.
- `DONGLE/ROUTE/3` imports only segment 3.
- `DONGLE/ROUTE/0:5` imports the half-open segment range 0 through 4.

Import additional routes by passing more identifiers or by running the command again. Existing cached routes remain in the atlas, so this is how observations from multiple drives and drivers accumulate:

```bash
.venv/bin/python tools/clustermaps/build_map.py ROUTE_A ROUTE_B ROUTE_C
```

Inspect or remove local entries using their privacy-preserving cache ids:

```bash
.venv/bin/python tools/clustermaps/build_map.py --list
.venv/bin/python tools/clustermaps/build_map.py --remove CACHE_ID
```

Routes can also be removed from the webpage with the × control on each drive card. Removal only deletes the derived local JSON and GeoJSON entry; it never changes the source rlogs.

If the server is already running, import from a second terminal and refresh the browser. The server disables HTTP caching so updated route indexes and scripts are picked up immediately.

Only full rlogs are accepted. `LogReader` is explicitly configured for `ReadMode.RLOG`; it never falls back to qlogs because qlog IMU decimation is too aggressive for impact analysis.

## Cache and exports

Generated files live under `web/data/` and are intentionally gitignored because they contain precise route geometry:

- `index.json`: the multi-route manifest and cross-route repeat-location clusters.
- `routes/<id>.json`: compact track, layer, event, diagnostic, and source-coverage data.
- `geojson/<id>.geojson`: route line plus event and rough-road point features.
- `repeated_locations.geojson`: locations independently observed on at least two cached routes.

Route names are retained in the local browser cache for recognizable route management; cache ids and driver ids remain hashed, and a friendly `--label` can be supplied. Treat `web/data/` as private because route names and map geometry identify drives. The browser loads compact derived files and never downloads, decompresses, or parses rlogs itself.

## Device rlogs

To copy full rlogs from a reachable comma without modifying the device:

```bash
mkdir -p tools/clustermaps/private/device_rlogs/DEVICE
rsync -a --partial --progress \
  -e 'ssh -o BatchMode=yes -o ConnectTimeout=5' \
  --include='*/' --include='rlog.*' --exclude='*' \
  comma@DEVICE:/data/media/0/realdata/ \
  tools/clustermaps/private/device_rlogs/DEVICE/
```

The transfer is resumable and copies only rlogs—no camera files or qlogs. Analyze the copied route directories with:

```bash
.venv/bin/python tools/clustermaps/build_map.py \
  --import-device-dir tools/clustermaps/private/device_rlogs/DEVICE \
  --device-key YOUR_DEVICE_KEY
```

Device analysis also checkpoints one derived file per segment, so rerunning the command skips completed work. The copied rlogs and derived checkpoints are gitignored.

## Layers

- **Route traces:** GPS-derived path, colored per imported route.
- **Road roughness:** two-second RMS windows of high-pass-filtered vertical acceleration.
- **Sharp impacts:** route-adaptive vertical IMU peaks while the vehicle is moving.
- **Hard acceleration / braking:** sustained, low-pass-filtered `carState.aEgo` threshold crossings.
- **Body motion:** roll/pitch angular-rate activity from `livePose`, excluding normal yaw motion.
- **GPS samples:** the exact absolute-position cadence used for interpolation.
- **IMU detail:** geolocated accelerometer and gyroscope components plus magnitudes.
- **Vehicle dynamics:** speed, acceleration, pedals, steering, yaw, wheel speeds, blinkers, and blind-spot state where present.
- **Pose and visual odometry:** fused device motion and camera-derived translation/rotation.
- **Controls and calibration:** desired/estimated curvature and learned roll, steering ratio, stiffness, and angle offset.
- **Road vision:** compact lane probabilities, lane width, and model action curvature.
- **Radar:** primary lead distance, relative speed, lateral position, and track status.
- **Sound, magnetic, thermal, and power:** cabin sound pressure, magnetic field, sensor temperature, device temperature, battery, and utilization.
- **Repeated locations:** impact or roughness observations clustered within 20 meters across two or more cached routes.

The “All recorded services” panel inventories every service found in every imported rlog, including services not copied into the browser cache. High-volume or sensitive payloads such as raw CAN, raw GNSS measurements, full vision-model tensors, camera/encoder metadata, driver-monitoring output, and system logs remain inventory-only. This exposes what the source logs contain without turning the local map into a raw-log mirror.

The basemap selector offers OpenStreetMap streets, Esri World Imagery satellite tiles, and a neutral coordinate-grid data-only canvas. Streets and Satellite require a network connection; Data only leaves every local sensor overlay working without tile requests. The selected mode is remembered in the browser.

The Visuals panel includes Point bleed. Roughness samples are interpolated into one low-resolution scalar field with a Gaussian edge falloff and a continuous color ramp across every selected route; other point layers use a softly blurred density canvas. The Heat, Corridor, and Night presets enable it automatically; Signal keeps precise individual markers.

## Visualization styles

Open **Visuals** above the map to switch between:

- **Signal:** precise centerline rendering with the least visual bleed.
- **Heat:** coverage glow plus overlapping impact halos.
- **Corridor:** extra-wide road bands for area-scale coverage inspection.
- **Night:** high-contrast street tiles with bright sensor overlays.

Road width and signal intensity can be adjusted independently. Coverage glow, impact heat halos, and the high-contrast map can also be combined manually; display preferences are kept in local browser storage.

## Interpretation

The current thresholds are screening heuristics, not labeled pothole classifications. Vehicle suspension, tire pressure, device mount, road speed, and sensor generation all affect magnitude. Repeated observations across independent passes are stronger evidence than a single adaptive-threshold event.

For calibration, keep ordinary full rlogs and record ground-truth route times for known potholes, expansion joints, speed bumps, and false positives. Device or logger changes should only be considered if validation reveals clipping, missing samples, or inadequate positioning.
