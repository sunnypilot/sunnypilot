# Ford C0 proportional feedback trial

This describes the original P=0.5 trial. The subsequent
[action-mode gain trial](ford_action_c0_gain_v19.md) raises action C0 P to 1.0;
direct-path mode retains P=0.5.

The existing controller sends its tracking correction through C1 only. Offline
identification on the Lightning suggests that stronger C1 requests can stop
producing faster wheel movement while additional C0 may still help. This trial
adds proportional correction to C0. It does not change the selected curvature,
C0 base geometry, C1 PI calculation, transmission rate or existing opt-in selection.

## Command

With host-sign road curvature error `e = reference - measured`:

```
scale = VM.get_steer_from_curvature(1, speed, 0) / (CP.steerRatio * CP.wheelbase)
C0_response = 0.010717679293424373 + 0.018122981795212647 / max(speed, 1.34)^2
C0_P = 0.5 * e * scale / C0_response
C0 = clip(existing_bounded_C0_base + C0_P, -5.11, 5.11)
```

The response coefficients are an offline fit to isolated C0 commands on route
`84865544361f55cb/00000145--5d9f02fee7`. They express **geometric steering curvature
per metre of C0**, not road curvature or an instantaneous wheel response. The
existing vehicle model converts the error into those units; its road-roll and
steering-angle offsets cancel in the error. No plant identification, observer or
dynamic plant simulation runs on the device.

`0.5` is an explicit trial feedback gain, not a fitted optimum. Before field
clipping, the extra C0 has a fitted steady effect equal to half the current
wheel-angle error. This does not mean 50% of the C0 field. The 1.34 m/s term
holds the fitted conversion below the identification dataset's minimum speed;
it does not disable steering or add a maneuver state.

C0 correction is recomputed every update, including updates that have no fresh
integration interval. It has no integrator, request-change state, deadband, or
additional slew limit. It becomes zero at zero error and changes sign on
overshoot. Existing driver override and PSCM arbitration disable it together
with other feedback. PSCM limit-reached continues to inhibit outward C1
integration; it does not freeze either proportional command. C1 remains
P=0.75, I=1.0. C2/C3 remain zero.

The existing `FordModelActionController` Sunnylink toggle still selects this
controller for CAN FD. With the toggle off, startup selects upstream Ford
control. No new UI or lateral-maneuver changes are included.

## Offline validation

The native-time replay compares the candidate against production commit
`d425b3260b0785b22096d130702b54a2e0761c36`, with recorded measurements, requests,
model health, driver input, service timestamps and PSCM arbitration held fixed.

- Ten Lightning routes: a9, b9, 112, 113, 117, 11c, 125, 146, 149 and 151.
- 1,170,113 cycles; 117,016 in-memory Float32/CAN encode/decode checks.
- Identical C1 output, C1 integral and command validity on every compared cycle.
- All outputs finite, inside field bounds, with C2/C3 zero.
- C0 exactly matches the old command whenever its new correction is zero or
  feedback is disabled.
- Across eligible samples with at least 30 degrees of wheel-angle error, the
  median C0 change is 0.65 m and the 95th percentile is 1.47 m.
- Across eligible requests below 5 degrees, the median change is 0.01 m and
  the 95th percentile is 0.05 m. This cohort includes turn exits with a still
  turned wheel; its largest correction is consequently much larger.
- At route 151 time 306.89 s, the replay changes C0 from 0.75 to 1.68 m for
  approximately 76 degrees of tracking error. Both replays send the same C1.

The test suite covers immediate correction, no accumulation, reversal, catch-up,
invalid inputs, real vehicle-model units across stiffness/speed/roll changes,
driver/PSCM arbitration, upstream fallback, and actual controlsd publication
through the 100 Hz CAN sender. The machine-readable route replay summary is
`ford_c0_feedback_v15_validation.json`.

```
PYTHONPATH=.:opendbc_repo python -m pytest -q \
  openpilot/selfdrive/controls/tests/test_ford_model_action*.py \
  openpilot/selfdrive/controls/tests/test_ford_path.py

PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/c0_feedback_validate.py \
  --output .cache/ford_c0_feedback_v15 --workers 4
```

The replay requires the existing local rlog extracts. Input hashes are recorded
in its validation JSON. It does not assume the truck follows modified commands.

## What is still experimental

The earlier fitted plant overpredicted one second of wheel movement by about
16 degrees in the route 151 example. It also misses the phase of a low-speed
oscillation in route 125. Independent C0/C1 response contributions are an
approximation; a shared PSCM limit could prevent the extra movement predicted
from C0.

An additional four-second fitted-plant simulation, with controller feedback
recomputed against simulated wheel angle, showed no regression for the tested
0.5 gain in its turn, unwind and near-straight cohorts. Route 149 had 27 eligible
turn windows; route 151 had no four-second turn windows surviving the strict
intervention/status mask. Future reference and speed were frozen, and the model
does not reproduce the route 125 failure faithfully. These results are a
sanity check, not validation of road tracking or an optimized gain.

Actual acceptance is better desired-versus-actual wheel tracking on turn entry,
without added oscillation, overshoot or delayed unwind. The software behavior
is validated; the physical improvement remains to be measured.

Diagnostics identify `model-action-curvature-c0-feedback-v15` and record
`offset_proportional`, `c0_proportional_gain`, and `curvature_scale` alongside
the existing heading/feedforward/integral signals.
