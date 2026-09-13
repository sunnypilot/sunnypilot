# Desired-curvature C0 on continuous PI

This local candidate changes C0's reference from the live model path's lateral
position at 7 m to a circular arc of the selected, upstream-limited desired
curvature. It is based on v7 (`08b3a14ad`), with the same P=0.50/I=0.25 controller.
No new gain, state, release condition, reference delay or output limit is added.
The candidate is on `codex/ford-curvature-c0-trial`; this evaluation does not
publish it over the v7 onroad branch.

For selected curvature k and the existing 7 m reference distance:

```text
arc C0 = (1 − cos(7 × k)) / k, or 0 when k = 0
       ≈ 24.5 × k for small curvature
C0 target = clip(arc C0 + 7 × clipped-away base C1, −5.11, +5.11)
```

The implementation uses the equivalent squared-sinc expression to avoid
subtracting nearly equal floating-point numbers near zero. C0 keeps its 4 m/s
output slew and Float32/CAN quantization. C1 keeps the existing mapping and PI
law, ±0.5 rad bound and 0.5 rad/s slew. C2 and C3 stay zero.

This is a geometric reference choice, not a model of the PSCM. The arc starts
at zero lateral position and heading. Independent live model-path position and
heading are omitted, while selected curvature can still include the model's
centering decision. Valid live model geometry remains a health gate. Short valid
paths do not shorten the synthetic 7 m arc. Both C0 and C1 use the selected
request, including the maneuver source when selected by controlsd.

## What the recorded routes show

All fourteen previous routes were replayed with v7 and this C0 replacement:
Lightning 112–117, a0, a2, a5, a9, b8, b9, ca and Raptor 02. On all 1,578,250
control cycles, C1, P, I, activation, feedforward, overflow and feedback/PSCM
gates match exactly. The v7 baseline also reproduces its archived commands
exactly. C0 matches the earlier isolated geometry experiment, but C1 no longer
has the release rules that coupled it to C0 in that experiment.

Duration-weighted clean samples, grouped by requested steering-wheel angle:

| Absolute requested wheel angle | v7 mean absolute C0 | Curvature C0 | Reduction |
| --- | ---: | ---: | ---: |
| Under 5° | 0.0136 m | 0.0072 m | 46.7% |
| 5–30° | 0.0965 m | 0.0608 m | 37.0% |
| 30–90° | 0.5064 m | 0.2916 m | 42.4% |
| At least 90° | 2.6314 m | 1.5282 m | 41.9% |

The clean cohort is 6,654.52 s with the existing quality/driver mask and margins,
speed at least 2 m/s and replay feedback enabled. Only 36.20 s have a requested
wheel angle of at least 90°. These are command magnitudes, not torque or tracking
scores, and do not classify driver interventions as controller failures.

At route 117, 128.272 s (right entry), C0 changes from −2.51 m to −1.35 m while
C1 remains −0.427 rad. At 142.670 s (request relaxing/reversing), C0 changes from
+0.18 m to −0.02 m while C1 remains −0.0425 rad. Both comparisons are replayed
on the same recorded vehicle motion. The new C0 follows the selected request
more directly, but it supplies less C0 during the entry as well as the exit.

## Validation and interpretation

- 694 Ford/controlsd, tracked PSCM lab, Sunnylink, params, sender and safety
  tests pass; 9,145 subtests pass and 178 platform tests skip. Historical
  untracked offline experiment tests are outside this deployment suite.
- The isolated two-controller replay performs 3,156,500 Float32/CAN checks.
- Production selection/adapter replay exactly reproduces the isolated candidate
  on every route cycle, adding 1,578,250 Float32/CAN checks.
- A 20,000-cycle scalar geometry/PI stress with mirrored and unrelated model
  paths adds 60,000 checks. Total: 4,794,750 CAN round trips.
- Tests cover zero/tiny curvature, signs, circular geometry, short/malformed
  paths, selected maneuver requests, overflow, unwind, duplicate measurements,
  model/driver/PSCM gates, caps/slew and toggle-off upstream Ford fallback.
- Ruff, production Ty and diff whitespace checks pass.

Software C1 parity does not guarantee identical physical unwind: changing C0
changes the PSCM's input and therefore the vehicle response and future feedback.
Smaller C0 is not established as better or worse tracking. No device build,
boot or drive of this candidate is claimed. Collecting the promising v7 drive's
logs before replacing it would preserve a useful comparison.

## Reproduction

Use the built cereal/opendbc environment and the same local route extracts:

```sh
export PYTHONPATH=.:opendbc_repo:.cache/ford_v6/test_deps
export PYTHONDONTWRITEBYTECODE=1
export PARAMS_ROOT=/tmp/ford-c0-params
export LOG_ROOT=/tmp/ford-c0-logs
python -m tools.ford_pscm_lab.curvature_c0_v7_replay .cache/ford_route117 --output .cache/ford_curvature_c0_v7/117
python -m tools.ford_pscm_lab.curvature_c0_validate --output .cache/ford_curvature_c0_v7/production --workers 4
python -m tools.ford_pscm_lab.curvature_c0_production_stress --cycles 20000 --output .cache/ford_curvature_c0_v7/production_stress.json
```

Repeat the first command for each label before validating all routes. Raptor
uses input `.cache/ford_raptor_route02` and output label `raptor02`. The first
replay loads isolated copies of pinned v7; the second tests this checkout's
actual selector and adapter. The validation JSON records source and extract
hashes, settings, example points and both sets of route reports. Older v7-only
production validation commands should run from the v7 commit.
