# Ford feedback: use filtered driver input

Route 162 ran action mode at C0 P=1.0. Raw torque crossings above 1 Nm
repeatedly removed C0/C1 feedback even while Ford's `steeringPressed` remained
false. The controller duplicated the torque threshold without Ford's existing
filter, so short crossings discarded the integral and abruptly removed P.

The adapter now uses `steeringPressed` for this decision. The existing Ford
threshold and filter are unchanged. From a zero counter, sustained torque
crosses that filter on the sixth sample. Fresh PSCM driver override (limit=3)
and invalid torque still clear feedback immediately. PSCM denial/inactive
status, freshness checks and input validity retain their previous behavior.
Clearing feedback removes correction; the base path request remains.

This applies to action and direct-path modes. Gains, reference selection,
distances, bounds, integration/unwind math, upstream request limits and CAN
cadence are unchanged. Action C0 P remains 1.0; direct-path C0 P remains 0.5.
Diagnostic names end in `v20-filtered-driver` so the next drive can confirm the
new arbitration actually ran.

## Validation

The short-torque-pulse regression failed against the old adapter before the
change. Afterward, the Ford controller, integration/CAN, geometry and Sunnylink
suites passed: 658 tests and 2 subtests. Tests exercise the actual shared Ford
filter, both torque signs, both reference modes, immediate PSCM override and
invalid torque. Ruff and `git diff --check` passed.

Native-time replay compares the new adapter with
`4900c0a40c87c72000b7168a6cf4fe6dd98ea6d0`, supplying identical recorded selected
curvature, vehicle measurements, driver flags and PSCM status. Four routes
cover 583,599 control cycles and 58,362 CAN pack/decode checks. Every command
stays in its field bounds with C2=C3=0, and filtered driver input or fresh PSCM
override clears all feedback.

Route 162's baseline reproduces recorded C0/C1 to Float32 precision (maximum
errors 1.15e-7 m and 1.48e-8 rad). Older routes were driven with earlier gains;
their comparisons below are two counterfactual command streams on the same
recorded motion, not a reproduction of those older deployed controllers.

| Route | C0 changes >0.25 m below 15 mph, old → new | C1 changes >0.05 rad below 15 mph, old → new | C1 at field bound, old → new |
| --- | --- | --- | --- |
| 162 | 152 → 70 | 83 → 50 | 0.97 → 1.06 s |
| 157 | 229 → 137 | 105 → 59 | 5.83 → 6.52 s |
| 151 | 142 → 77 | 86 → 42 | 3.39 → 4.04 s |
| 149 | 375 → 197 | 226 → 111 | 10.44 → 16.08 s |

For route 162, feedback on/off transitions fall from 538 to 218. At raw-torque
threshold crossings with unchanged model frame, nearly unchanged target and
no filtered driver/PSCM override, large C0 changes fall from 99 to zero.
Remaining transitions include legitimate driver input and PSCM status changes.

Retained correction changes C1 after a brief torque crossing has ended. This
can increase holding and time at the field limit, especially on route 149.
Replay proves command continuity and override behavior on frozen measurements;
it cannot establish improved physical tracking, stability or unwinding. Route
162 also had lag without any torque-triggered reset, which this change alone
does not explain.

Detailed metrics, source hashes and controller provenance are in
`ford_filtered_driver_v20_validation.json`. Reproduce a route with:

```sh
PYTHONPATH=.:opendbc_repo:.cache/ford_geometry_deps \
  /Users/ibpersonal/dev/sunnypilot/.venv/bin/python \
  tools/ford_pscm_lab/filtered_driver_replay.py \
  --source .cache/ford_route162/full --output .cache/ford_filtered_driver_v20/162
```

## Deployment

Pull and restart the updated software while offroad. Keep Selected-Action Path
Tracking enabled, Model Geometry Reference disabled and C0 one-second distance
disabled for the current action/fixed-7-m trial. Turning the master controller
toggle off continues to select upstream Ford control.
