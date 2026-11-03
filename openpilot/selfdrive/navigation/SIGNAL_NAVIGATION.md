# Signal navigation experiment

The physical turn signal selects a short real route through the next supported
street. The route and maneuver instructions condition a navigation-trained
driving network continuously. This replaces the earlier map-timed turn-cue
experiment when a compatible model is selected; it does not add steering angles.
The automatic candidate begins with a pending signal and may prefetch a route
at any speed. Pending discovery does not send navigation inputs or suppress the
existing lane-change checks. The first emitted host lane-change request commits
lane-change mode and cancels the candidate route. Otherwise, a fresh validated
street approach below the configured turn speed (19 mph by default) may commit
turn mode. An early fast signal can therefore prepare a route and later become
a turn, provided no lane-change request has already started. LC wins a same-frame
tie. After either commitment, the role is fixed until cancel/opposite.

Only a committed turn suppresses competing lane-change pulses. Map conditioning
requires a validated connected street, matching position and heading, and a
coherent fresh route. Pending intent cannot feed navigation.
This arbitration still cannot reliably identify every early fast turn signal or
slow lane change. A nearby legal street does not establish the driver's intended street.
Predicted missing lane lines must not be treated as proof that no adjacent lane
exists. These ambiguity cases remain validation limitations, not solved intent.

A causal host audit of the saved recordings gives this candidate navigation
eligibility on 23 of 39 street-turn requests; nine encounter a lane-change
request first and seven remain pending. All four recorded lane-change contexts
retain lane-change mode. These are selection proxies, not neural turn successes;
map-target identity is a separate check and can still select the wrong street.
An earlier speed-at-signal classifier was rejected because 18 street-turn
requests began above 20 mph. The automatic selector is not dependable enough to
claim road-test readiness from these results.

## Model requirement

CTV3 and the small fallback have no navigation input sockets. A route on the
screen cannot make those models follow navigation. The runtime checks actual
`nav_map` and `navigation` tensors, and publishes `NavModelState` separately from
route availability. The UI distinguishes **Route ready** from **Navigation active**.

The basis is commaai/openpilot `nav-model-integration`, pinned at
`afbf2e547e9319e2eb9f515e1e4330af63705cec`. The available BIG ONNX is the earlier
RL navigation checkpoint `80eedcdd/12864`, SHA256
`1d18c42ea4cd95c8bffab4635844b78b8e2d4e25b9de44a9c5ac2e0961371a2e`.
The pinned commit's newer N16 compiled PKL is a different artifact; running the
ONNX is not evidence of running those N16 weights. Official LFS downloads for
the latest three compiled navigation artifacts returned object-not-found.

The ONNX was downloaded through a third-party mirror and independently matched
against comma's exact LFS pointer. A Chestnut-compatible plain artifact still
requires the target compilation and verification step. A Mac CPU ONNX smoke is
not a verified device build. No model is automatically swapped when signaling.

## Route ownership and input coherence

Manual destinations take priority. Automatic routes do not overwrite
`NavDestination`. Each physical signal has an identifier; a held indicator does
not repeatedly select turns. Cancellation before entry retires the route;
already-entered turns may retain guidance through the receiving road, after
which it is cleared. A missed turn is retired rather than rerouted back to the
short endpoint.

Map frames carry the exact rendered `navRoute.logMonoTime` as their stream EOF
generation; SOF remains the GPS publication time. The driving process requires
a matching route generation, fresh map/instructions and the current signal
session (or explicitly retained exit guidance). Stale/opposite/canceled route
inputs are zeroed. A route preview alone never establishes active model input.

## Scope and validation

The feature is opt-in under **Signal Navigation (Experimental)**. It needs
online Directions requests, a Mapbox public token, and automatically fetched
road-map tiles. Existing steering, cooperative steering, action conversion and
the restored 1.6 m/s low-speed handling are preserved.

Recorded-camera model replay can test whether real route inputs change the
model's plan. It cannot establish physical curb clearance or a successful driven
turn, because the camera views remain the recorded ones. Model runtime checks,
software fixture checks and recorded-sequence results must be reported separately.
