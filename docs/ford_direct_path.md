# Direct model-path C0/C1 trial

This trial takes priority over the untested filtered-driver change. Driver
arbitration is restored to the last driven baseline, `18ded0380`: a raw torque
crossing above 1 Nm, filtered driver input, or fresh PSCM driver override still
clears feedback. The filtered-driver experiment remains available in history at
`4f7d2b8d2` and is not included in this trial.

Keep **Selected-Action Path Tracking** and **Model Geometry Reference** enabled
in Sunnylink. The existing geometry toggle now selects direct-path mapping at
controlsd startup. Keep **C0 one-second distance** off for fixed 7 m C0. Apply an
offroad-to-onroad cycle after updating. Geometry off restores the original
model-action controller; the master controller toggle off restores upstream
Ford control. Joystick and lateral-maneuver overrides retain their priority.

## Mapping

The path is parameterized by accumulated arc length in the model frame. C0
samples model lateral position at 7 m, or max(7 m, speed × 1 s) when the existing
C0 distance setting is enabled. C1 samples model orientation at max(7 m,
speed × 1 s). A shorter path holds its endpoint; invalid paths disable the
experimental command. Both distances are 7 m below about 15.7 mph. These are
engineering choices, not identified Ford reference points.

C0 and C1 are independent base requests. C0 is no longer reconstructed as a
circular arc from the curvature used for C1. C2/C3 remain zero, so this still
does not transmit the model's entire curved path to the PSCM.

For the existing request limits and feedback, heading is divided by its sample
distance to form a heading-equivalent curvature. controlsd applies its normal
curvature limits to that value, logs it, and uses it for desired steering angle
and feedback. Multiplication by the same distance recovers the model heading
when unconstrained. C0 independently uses 2 × offset / distance² to apply the
same request-limit function, then reverses that normalization. This does not
infer C0 from C1. These envelopes constrain base requests; they are not proof of
physical lateral acceleration or jerk under the unknown PSCM response.

P/I gains, measured-steering feedback, C1 anti-windup, C1-overflow allocation to
C0, field bounds, driver arbitration, and CAN cadence retain the driven
baseline behavior. There is no new C0/C1 actuator slew limiter. The independent
C0 envelope adds one previous-reference state, reset with the controller.

This changes preview semantics: direct commands use the distance stations
above, rather than the prior modeld curvature preview (about 0.744 s at low
speed on these drives). The raw model points do not pass through the old
curvature reference's 0.1 s smoother. Existing request limits still apply.

## Logging

Controller diagnostics identify `model-path-direct-feedback-v17`, with
`direct_path=true` only when the model path is in control. A valid maneuver
reference uses the original curvature-to-arc mapping and logs
`direct_path=false`. `offset_reference` records the independently limited C0
normalization. Desired curvature and desired steering angle describe the C1
feedback target, not an independent measure of lateral path position.

modeld's geometry-reference telemetry is retained for comparison. Its
`selectedCurvature` and published model action are not the direct controller's
selected reference; use controlsState and the Ford controller diagnostics.

## Offline results

The replay compares the driven baseline against the direct-path candidate on
identical recorded model frames and frozen vehicle measurements from full
rlogs 15a and 15b. It covers 44,145 control cycles and 4,415 candidate CAN
serialization checks. All commands remain finite and within field bounds;
C2/C3 remain zero and driver/PSCM override behavior matches the baseline.
The baseline reproduces recorded C1 to Float32 precision; C0 differs by at
most one 0.01 m command quantum on 15b.

| Metric | 15a baseline → direct | 15b baseline → direct |
|---|---:|---:|
| C1 field-bound time | 2.57 → 6.77 s | 6.70 → 7.54 s |
| Low-speed C0 steps > 0.25 m | 52 → 52 | 85 → 129 |
| Low-speed C1 steps > 0.05 rad | 36 → 46 | 32 → 57 |

Low-speed counts use valid consecutive commands below 15 mph, normally 10 ms
apart. They are descriptive command changes, not physical wheel jerk. The
direct mapping changes requests substantially and does **not** establish a
smoothness improvement: abrupt command changes and C1 field-bound time can
increase. Fixed recorded measurements cannot predict the resulting wheel
response, centering, or unwind. No on-road improvement is claimed.

**593 tests pass** (547 controller/path/geometry tests and 46 settings tests).
The tests cover independent position/heading commands, distances, endpoint
handling, invalid input resets, request limits through reversals, feedback,
baseline driver overrides, toggle selection, maneuver priority, publication,
and CAN encoding. Reproduce replay with:

```sh
PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/direct_model_path_replay.py \
  --source .cache/ford_route15a/rlog_full --output .cache/ford_direct_path/15a
```

Detailed measurements and source hashes: `ford_direct_path_validation.json`.
