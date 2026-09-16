# Action controller: stronger proportional C0 correction

The model action remains the steering target. Increase action-mode C0 P from
0.5 to 1.0 so an existing tracking error produces twice the immediate C0
correction, before command clipping. This is a trial gain, not an identified
optimum or a claim of twice the wheel response.

C0 base mapping, distances, C1 P=0.75, C1 I=1.0, command bounds, upstream request
limits, driver arbitration and CAN cadence are unchanged. Direct-path mode
retains C0 P=0.5. Explicit gain overrides remain available for offline analysis.

The C0 correction has no integral state. It vanishes at zero error and changes
sign on overshoot; the base command and existing C1 integral still remain. A
higher P can amplify noise or oscillation through delayed vehicle response.
Command replay does not establish physical stability, faster tracking or better
unwinding.

## Selecting the trial

In Sunnylink, while offroad:

- Enable **Selected-Action Path Tracking (Experimental)**.
- Disable **Model Geometry Reference (Experimental)** to select the original
  model action. Leaving it enabled keeps the unchanged direct-path controller.
- Keep **C0 one-second distance** disabled for the fixed 7 m configuration.

Restart the updated software while offroad before testing. The controller and
reference selection are latched at startup. Disengagement alone does not switch
the reference. Turning the master controller toggle off restores upstream Ford.

Action-mode diagnostics now identify `model-action-curvature-c0-feedback-v19`
and record `c0_proportional_gain=1.0`. Direct path remains
`model-path-direct-feedback-v17`, with its gain at 0.5.

## Verification

Baseline: `0020c0c41940fe1f4b33dd23297def77a0a67e92`.

The Ford controller, startup selection, controlsd publication/CAN, geometry and
Sunnylink settings suites pass: 648 tests and 2 subtests. Coverage includes
catch-up, opposite correction on overshoot, zero-reference unwind, unchanged C1
state, upstream fallback and preservation of the direct-path gain.

Native-time replay over ten older Lightning routes checks every control cycle
and performs a CAN pack/decode check every tenth cycle. The baseline receives
the same curvature conversion as the new controller. C1 commands, proportional
terms, integrals and command validity are identical; C0 proportional correction
is exactly doubled within numerical tolerance, and commands retain field bounds.
There is no C0 change when feedback is disabled or the correction is zero.

```sh
PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/c0_feedback_validate.py \
  --baseline 0020c0c41940fe1f4b33dd23297def77a0a67e92 \
  --output .cache/ford_action_c0_gain_v19 --workers 4
```

Three recent routes (157, 15a, 15b) additionally compare original model action
and direct-path modes against the same baseline, preserving recorded motion.
Original action is taken from the intake on 157 and timestamp-matched telemetry
on 15a/15b. All direct-path commands and their accumulated state remain identical.
The supplementary harness and per-cycle inputs are in the local replay cache.
Combined validation totals and route results are in
`ford_action_c0_gain_v19_validation.json`.

On the recorded measurements, a clean route-157 example requesting 174 degrees
with the wheel at 74 degrees changes C0 magnitude from 2.23 to 3.42 m while C1
remains at 0.5 rad. A route-15b example requesting 206 degrees with the wheel at
239 degrees reduces the remaining into-turn C0 magnitude from 0.85 to 0.46 m.
These are different commands on frozen measurements, not predicted wheel motion.
