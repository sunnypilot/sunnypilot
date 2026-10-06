# sunnydrive YOLO26 viewer

`yolo_viewer.py` is the entry point; `yolo_web.py` provides the browser server and calibrated overlays.
This separate viewer runs on the Mac and listens only on localhost.

From the repository root, using the prepared Python environment:

```sh
/private/tmp/roadseg-venv/bin/python tools/yolo/yolo_viewer.py --demo --cache /private/tmp/yolo26-models
```

Open http://127.0.0.1:8768. The replay console opens in the Terminal running the command: Space pauses/resumes replay, s seeks forward 10 seconds, Shift+S seeks back 10 seconds, and q exits replay and the viewer. The browser Pause button pauses inference only. `--demo` starts the public comma demo replay locally in its own IPC namespace and stops that replay on Ctrl+C. Requires the existing built `openpilot/tools/replay/replay`, repository Python environment and msgq extension. The parked comma is not changed.

For live sunnydrive video:

```sh
/private/tmp/roadseg-venv/bin/python tools/yolo/yolo_viewer.py --comma http://10.83.106.109:8766 --token-file /private/tmp/roadseg-tokens.json --cache /private/tmp/yolo26-models
```

Choose Nano, Small, Medium, Large or Extra large, then enable Objects, Object masks and Scene segmentation independently. Object masks imply Objects. Turning everything off shows the camera without YOLO inference. Weights download from official Ultralytics assets on first use. Full scene combines detection and semantic segmentation at the selected size. Switching releases the previous models before loading the next selection. Road, wide and driver camera selection works for replay and live inputs. Area masks are saved in browser local storage separately for each camera/view. Area opacity controls their displayed shading; inference always receives fully black masked regions.

- Detection: COCO object boxes and class confidence.
- Instance masks: individual object masks and boxes.
- Scene segmentation: Cityscapes pixels including road, sky, traffic signs, vehicles, people and riders. Scene opacity applies here and in Full scene.

The viewer is observational. It does not control the vehicle. It does not read sign text, provide vehicle re-identification, or guarantee accurate distances. Replay runs at its recorded rate; the displayed processing FPS excludes the time waiting for a new replay frame. Frames are conflated so inference uses the latest available camera image rather than building a queue.

The Nano detection and segmentation models were checked for checkpoint loading and inference/rendering on the M5 GPU. Larger checkpoints are offered on demand and have not all been benchmarked locally.

Official model documentation: https://docs.ultralytics.com/models/yolo26/

Driver camera uses the inward-facing cabin feed. Its view through the windows is not a calibrated extension of the exterior road cameras. The demo launcher enables `--cabin`; existing manual replay should also include that flag.

Wide + driver sides splits the driver image vertically, places its right half to the left of wide and its left half to the right, accounting for the inward-facing camera, preserving panel aspect ratios. YOLO processes the composite. These are unaligned views, not a calibrated surround image; the latest driver frame is used only while it is under one second old.

Add blackout area lets you draw up to 16 independent polygons per camera/view. Click at least three vertices, then Finish area. Drag orange handles to reshape, including while drawing. Click an area’s X to delete it (Enter/Space also works when focused). Finish area becomes available after three points; Cancel area discards an unfinished outline. Remove area also deletes the selected polygon, or the last polygon when none is selected. Areas persist in browser local storage per view and are fully black in the model input. Area opacity adjusts their shading in the displayed output.

Only one sunnydrive web viewer may run, across all ports and both viewer scripts. A second launch exits before starting replay or loading models. Stop the existing viewer before relaunching; the OS releases the lock when it exits.

The video uses the full page width and follows the actual camera/composite aspect ratio. Left side rotation and Right side rotation sliders provide independent -180° to 180° adjustments in Wide + driver sides. Rotation occurs before inference; panel dimensions remain fixed, with black corners where rotated content falls outside the frame. Rotation settings persist in browser local storage. Side-panel areas follow camera rotation and panning automatically.

The last camera/view and model are saved on each selection to `~/.config/sunnydrive/yolo-viewer.json` and restored before loading a model on the next launch. Explicit `--camera` or `--model` arguments override the saved choice. `--settings-file` can use a different settings file.

When launched with `--demo`, replay shortcuts also work from the webpage: Space pauses/resumes replay, Left/Right seek 10 seconds, Shift+Left/Right seek 60 seconds, +/− change speed, and q quits. Native s/S, m/M, e, d, t, i, w and c shortcuts are also forwarded. Click the video/background first; shortcuts do not intercept typing, dropdowns, sliders or focused buttons. On-page replay buttons provide pause/play and ±10 seconds. The Terminal console remains interactive. Attaching with `--replay` does not give this script keyboard access to a separately launched replay process.


Area selection offers Black out selected areas or Keep selected areas. In Keep mode, trace the visible windows (Add keep area → Finish area); the union of those polygons is retained and everything outside is fully black for inference, with display shading controlled by Area opacity. With no keep polygons, the frame is fully masked until a window is outlined. Selection mode persists in browser local storage separately for each camera/view.

Side-panel area masks follow the camera rotation and horizontal/vertical controls. Their layout reference is saved with the outlines so it survives restarts. Areas centered on the wide camera stay fixed.

Rotation, panning, area edits, and opacity work while paused. The viewer recomposes and processes the frozen camera frames when a setting changes; unchanged paused frames do not rerun inference. This also works when replay itself is paused.

Drag a side panel directly on the preview to pan it, including while paused. Exit Edit areas first so dragging controls the camera instead of polygon points.

Masked side-camera regions and empty rotation corners reveal the camera underneath when panels overlap. YOLO receives this same composite. Area opacity applies where a masked region has no usable camera underneath.

Reset sides restores both side cameras to zero rotation and their original positions, carrying their masks back with them.

Object-capable tasks (Detection, Instance masks, Pose, Oriented detection, and the detection model in Full scene) use ByteTrack with persistent IDs displayed on boxes. Camera/model/source switches, replay seeks, and scene-layout/mask changes reset tracking. Tracking IDs are temporary associations, not vehicle re-identification. The Python environment needs `lap>=0.5.12`.

Tracked objects show cyan recent trails and yellow one-second image-motion arrows, extrapolated from recent box-center movement. This is a constant-velocity image estimate, affected by ego motion and detection jitter; it is not a world-space heading or driving trajectory. Stationary and newly detected tracks omit the arrow.

Lane lines / edges / path displays comma modelV2 curves, projected using recorded extrinsicsCalibration. The demo launcher publishes these telemetry services; it does not run a new lane-detection network. Live mode reads sunnydrive telemetry.

Road-camera object labels show approximate radial ground-plane distance (`~20 m`). The bottom-center of the box is assumed to touch the calibrated road plane, so occlusion, slopes, truncation, and box errors affect estimates. Center-view boxes in the composite can use this calibration; side-camera boxes cannot. Where meters are unavailable, the label explicitly says meters unavailable. No additional depth network is run.

Vehicle labels use the box bottom-center and the same projected lane curves drawn on screen. They compare lane boundary intersections at that bottom pixel row, requiring 30% probability for ego boundaries and 15% for outer boundaries. If an outer boundary is missing, one adjacent lane width is inferred from the ego-lane width and labeled left/right lane. Unsupported projection/contact points remain lane unknown. This estimates the contact-center lane, not the vehicle's full footprint.

Lane labels cover five positions: left left lane, left lane, ego lane, right lane, and right right lane. The second lane on either side is inferred from adjacent lane width because comma supplies only four lane boundaries. With missing outer lines, both adjacent lanes are inferred from ego-lane width. These labels indicate relative lateral positions, not proof that another drivable lane exists.

Lane overlays preserve model x/y/z coordinates and use intrinsic × view-from-device × recorded calibration rotation (plus wide-from-device for the wide camera). Replay camera frame IDs are matched to model frame IDs within three frames; the matched sample stays frozen during paused edits. Older live telemetry without modelProjection/z uses the ground-plane fallback.

Lane UI width (1–16 source pixels) and Lane UI opacity independently control the comma lane/edge/path overlay. Opacity also affects its path fill. Values persist in browser storage and update while paused.

A top-down canvas to the right of the preview shows comma lane curves and detected vehicles up to 70 m ahead, using the same estimated ground positions and track IDs as camera labels. Ego is blue, ego-lane cars green, adjacent-lane cars yellow, and unknown-lane cars gray. Vehicles without usable road calibration/contact positions are omitted. Vehicle icons are nominal footprints, not measured dimensions or headings. It reuses inference outputs and a small per-frame event stream; no extra camera stream or model runs.

One compact box label combines track ID, class, confidence percentage, meters, and lane position above the box (for example `id:42 car 90% | ~20 m | ego lane`).

Top-down scenes are pushed immediately with each completed inference frame. Browser rendering keeps only the newest scene per animation frame; it does not wait for status polling or queue old scenes. Its rate follows inference FPS.

Camera and top-down views sit side by side on desktop; below 900 px viewport width, the top-down panel stacks underneath.

The demo launcher starts replay at 2:00 (`--start 120`).

On startup, the server waits up to three seconds for an existing viewer tab to reconnect through its status polling. If it reconnects, no new tab opens. Updated viewer tabs automatically reload after a server restart to reconnect the camera and top-down streams. Otherwise the launcher opens a browser tab as usual. `--no-open` disables automatic opening.

Displayed meters now estimate longitudinal clearance from the front bumper: max(0, ground-contact forward distance − measured camera-to-front-bumper offset). Enter that offset in the UI; it persists in browser storage. Without an offset, meters show ?. The target box bottom remains an approximate ground-contact proxy, not a measured bumper location. Top-down longitudinal positions and lane curves shift to the same front-bumper origin when the offset is set.

In demo mode the top-right Pause/Resume button controls replay itself. Its state follows the replay console status, including Terminal spacebar and browser replay shortcuts. Live/manual-attached mode retains inference pause behavior.

Display offers Full view, Objects only — masked, and Objects only — original. Both isolated modes use instance segmentation at the current model size and retain every detected object's silhouette. Masked adds segmentation tint; Original preserves camera colors. Background is black; annotations and top-down remain. Inference still receives the regular composite. Lane lines / edges / path remains available in both isolated views when its checkbox is checked. Selecting a different task restores Full view; display selection persists in browser storage.

Box labels sit inside their four corners: type top-left, confidence top-right, track number bottom-left, and bumper distance with lane symbol bottom-right. Text uses a fixed readable size instead of shrinking with small boxes.

Labels and Bounding boxes have independent visibility toggles. Tracking, silhouettes, motion arrows, and top-down remain active. Visibility persists in browser storage and changes apply while paused.

`yolo` starts the demo at 2:00. `yolo d59ca223dca8da93/00000498--3190be1e8b/6` starts that route segment at its beginning. Add `--start N` to offset within the selected route range. `yolo --comma IP` connects live; `yolo --replay` attaches to a separately running replay.

Lights / sign text enables conservative crop-based traffic-light color checks, road-sign OCR, and experimental vehicle-lamp activity labels. Traffic-light colors need three agreeing recent frames; ambiguous/distant crops are unknown. Full scene supplies semantic traffic-sign regions for general sign text; object-capable modes can read detected stop signs. OCR runs asynchronously on CPU, at most twice per second, with bundled RapidOCR models and a latest-job queue. Explicit SPEED LIMIT/MAXIMUM text plus a plausible number is required before labeling a speed limit; units are not inferred.

Vehicle lamp activity uses per-track temporal color measurements: repeated amber on/off transitions can show left signal?, right signal?, or hazards?. Simultaneous brightening of two red rear-lamp regions can show brake lights?. Constant red tail lamps do not imply braking. These are experimental image heuristics, affected by pose, lighting, reflections, camera motion, and occlusion—not trained brake/turn-signal classifiers. They make no driving decisions.

Object labels appear on one line outside their boxes, with leader lines pointing to the objects. Placement avoids other labels and keeps a fixed readable font; crowded scenes use the least occupied available position. Sign text uses the same layout.

Lights/sign text uses JC Traffic Sign Detection YOLO26 Small on raw sign crops in the background CPU worker (21 US sign classes, including speed limits 15–85). Weights are downloaded once into the model cache from pinned Hugging Face revision `2cb01e6788b82d904a1d1e35646e171a1b622fe7`. OCR remains a fallback for general sign text and missed detections. The model predicts sign values directly; it does not establish which sign applies to the vehicle's lane.

Sign recognition now uses only the dedicated JC YOLO26 US-sign model; OCR is disabled. Pending, unrecognized, and failed sign reads produce no label. Sign IDs and unknown traffic-light labels are hidden.

The size and feature choices are remembered together. Changing features releases previous models before loading the selected combination. Objects-only display automatically enables object masks while preserving the scene selection. Labels, bounding boxes, arrows/trails, lights/signs and lane overlays retain their separate visibility controls.

Performance: inference results are cached for the current frame and input geometry/masks. Labels, sign results, opacity, lanes and display toggles redraw without rerunning YOLO or advancing tracking. Changing the camera input, camera layout, mask geometry or model invalidates the cache. Annotation tensors transfer to CPU once per inference, scene colors use an equivalent OpenCV lookup, and video uses TCP_NODELAY. Sign crops remain serial because measured batching was slower; CPU inference uses one Torch thread, the fastest measured setting on this Mac. Status exposes inference, rendering, encoding and total processing times; FPS includes JPEG encoding and stays unchanged on cached redraws.

Tracking trails and arrows now use calibrated ground-contact positions with ego speed and available yaw-rate compensation. Past positions are transformed into the current vehicle frame, then object velocity is fitted over the recent track. Low-speed residuals are suppressed. Recorded model timestamps are used for replay, independent of playback speed. Signs/lights and uncalibrated camera regions get no motion arrows. Overhead rotations use the same compensated velocity. Live sunnydrive already supplies speed; yaw compensation additionally uses the new `car.yawRateRps` telemetry field when available. No comma service was restarted or deployed by this viewer change.

Enable Scene segmentation, then choose YOLO segmentation or comma10k segmentation. The source is persisted alongside model size and features; switches release the previous model combination. comma10k runs at 512×384 on Metal and does not have Nano/Small variants—the size selector controls the YOLO object model. It colors road, lane markings, vehicles/people and your car, leaving background untinted. YOLO object masks/tracking remain independent. With comma10k, the existing background US-sign model scans raw frames because comma10k does not locate signs. No OCR is used.

Radar overlay
-------------
The **Radar / sensor tracks** checkbox shows sensor markers on the camera and overhead view. Magenta diamonds are radar; cyan markers are camera-reported objects; amber marks candidate radar sources. Radar markers remain visible independently. A connector is drawn only after a clear one-to-one match persists across three distinct frames, with longitudinal/lateral gates, relative-motion checks when available, and ambiguity rejection. Matched camera labels use `R` for radar distance and show relative speed; matched overhead objects use radar positions. Radar source provenance is preserved. Radar distances are from the front bumper; camera projection uses the configured camera-to-bumper offset and ground-plane calibration. Marker labels include longitudinal distance and longitudinal relative speed in m/s. Stale data older than 200 ms is omitted.

For Hyundai replay recordings whose logged `radarTracks` are empty, the viewer decodes the confirmed 24-byte `0x3A5–0x3C4` CAN family on buses 0–2. The DBC generator is copied from the local `hyundai-radar-tracks` branch; no driving branch checkout or vehicle service change is needed. This fallback supports that family only. Its IDs identify CAN target slots, not persistent object identities. The supplied segment `d59ca223dca8da93/00000498--3190be1e8b/4` contains the full family on bus 1 at 20 Hz and produces nonempty decoded tracks.

Restart the viewer, then run:

```
yolo d59ca223dca8da93/00000498--3190be1e8b/4
```

Live sensor markers require the updated sunnydrive telemetry code and `tools/yolo/yolo_radar.py` plus its schema on the comma. This change does not deploy them or restart the comma. `/status` exposes a scene snapshot with separate vision and sensor tracks; uncertainty and occupancy remain unknown, and `control_ready` is false.

Qcam is available in the camera selector for routes/demo launched by the viewer. It decodes the low-resolution qcamera recording separately, synchronized by recorded encode indices, so Road/Qcam switches do not restart replay. Road-camera calibration scales to the Qcam resolution. Qcam is unavailable for live input or externally attached replay without a route.

Use the Replay / Live car selector in the top bar to switch inputs. Live defaults to `http://10.83.106.109:8766`; edit Comma address and press Connect for another address (for example `100.100.139.123`). Approve pairing on the comma if requested. A source change replaces the local viewer process and stops its owned replay; the existing browser reconnects without opening another tab. Switching back uses the previous route, or the demo if none was supplied.

Running `yolo` without arguments opens an idle browser UI. The default demo field is `d59ca223dca8da93/00000498--3190be1e8b/6`; press Connect to start it at 0 seconds, or choose Live car and connect a comma address. No video or inference starts until Connect. Explicit route arguments and `--demo` still start playback immediately.

Radar associations are heuristic and are exposed in `/status` under `scene.radar_associations`, with match costs (not calibrated probabilities). Unknown/camera/candidate sensor sources do not provide radar distances. Missing tracks, source-slot age resets, replay seeks, and camera/model/mask changes drop association history. Validation currently covers synthetic motion and ambiguity cases; recorded-scene accuracy still needs measurement before using associations for decisions.

Action preview
--------------
The **Actions / paths** toggle displays observational Gas/Brake/Stop/Go hypotheses and dashed candidate paths in the camera and overhead views. Red lights and stop signs produce stop/hold previews; yellow/mixed lights and yield signs produce brake previews. The display defaults to Go? when no stop/brake cue is observed. This is a display default; missing signals, unobserved road, and unknown right of way do not establish permission or clearance. Radar-backed and ground-positioned camera objects can mark candidate corridors blocked. Recognized no-left/no-right-turn signs mark the corresponding candidate blocked.

Enable Road / sky segmentation and supply the camera-to-bumper offset for grounded paths. Turn hypotheses sample a 1.8 m footprint over the existing calibrated ground segmentation, require a connected road exit and observed non-road before the opening, and reject a uniformly wide road as intersection evidence. Candidate geometry is not a maneuver plan: intersection topology, which signal/sign applies to a lane, permissions, stop-line distance, road elevation, and crossing traffic remain unverified. Dashed turns can still be wrong. This preview sends no controls; `scene.action_preview.control_ready` remains false.

Candidate paths are generated solely from the calibrated segmentation grid, with no use of comma model.position/path or lane lines as trajectory inputs. Calibration still comes from comma. The comma trajectory ribbon and center path are no longer rendered; lane-line/road-edge overlays remain independently selectable.

Straight preview candidates prioritize avoiding detected objects, then road coverage and avoiding yellow painted separators. Yellow is sampled from the original camera image on segmented road; it is a color heuristic, not a dedicated lane-marking classifier. Unknown ground never provides road support.

Our lanes / edges uses native segmentation pixels to trace open road-facing boundaries, with a continuous painted-divider trace and segmented cars excluded. Camera and top-down render the same curves (inverse camera calibration supplies ground coordinates). The coarse ground-grid contour and polynomial edge fitting implementations were removed. Path ranking also considers the midpoint between overlapping traced boundaries, in addition to obstacle-avoiding candidates; it does not use comma trajectories. Camera geometry, unknown visibility, and segmentation quality still limit accuracy.
