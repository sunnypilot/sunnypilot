# Geometry-assisted action reference: offline experiment

Status: the revised selector is now wired behind `FordGeometryReference`, labelled
**Model Geometry Assist (Experimental)** in Sunnylink. This supersedes the direct
path trial at `01f5d5429`. The initial offline experiment below preceded wiring.
The user authorized deployment after reviewing the numeric comparison.

The requested behavior is geometry's earlier/stronger turn request, with the
original action's ordinary driving and release behavior. This experiment uses
the earlier smoothed orientation-derived curvature as geometry, not the newest
direct-path C0/C1 mapping. That direct mapping is a separate baseline.

## Proposed selection rule

`openpilot/selfdrive/controls/lib/ford_geometry_action.py` returns a single curvature reference.
Both C0 and C1 then use the existing scalar controller, including measured-wheel
feedback. No P/I gains, driver gates, upstream curvature limits, or CAN field
bounds change.

For same-sign action `A` and geometry `G`, with `|G| > |A|`:

```
H = A + smoothstep((|G| - start) / (full - start))
        * (|A| / max(start, action_peak))**power * (G - A)
```

The smoothstep argument is clamped to [0, 1]. Otherwise the result is `A`.
Defaults: `start=0.010/m`, `full=0.020/m`, `power=2`.
These are experimental tuning choices, not Ford specifications. This is not a
claim of a gainless controller: the existing feedback gains remain, and the
reference selector introduces a curvature band and release exponent.

`action_peak` is the largest same-direction action magnitude in the current
geometry excursion. It resets when inactive, geometry becomes invalid, geometry
changes direction, or geometry drops below the start threshold. Repeated control
cycles using the same model frame do not accumulate extra assistance.

The denominator's `start` floor is essential. The first version normalized by
`action_peak` alone. On route 15b, geometry briefly fell below its gate and then
rebounded. A tiny action rebound rearmed full geometry: at 46.73 s, action's 3.2°
wheel-equivalent reference became 103°. The revised version produces 4.3°, with
C1 -0.0095 rad instead of -0.1805 rad. A minimized regression test failed in both
directions before the fix and passed afterward.

## Replay scope and results

Five routes: 149, 151, 157, 15a, 15b. 578,741 unique control cycles, approximately
55.7 minutes of active valid input. The 86 existing marked windows overlap;
they are not 86 independent turns or statistically independent observations.

Compare original action, earlier geometry, newest direct path, stronger
same-direction source, 50/50 blend, and the proposed hybrid. All use identical
recorded motion, driver input and PSCM status. Feedback is recalculated at native
control cadence; new vehicle motion is not simulated.

- On 15b's large left, hybrid/geometry/action peak references are 359°/361°/218°.
  Hybrid C0 peaks at 4.33 m versus geometry's 4.41 m and action's 1.27 m.
  Hybrid and geometry both reach C1's 0.50 rad field bound.
- The hybrid reference crosses below 25° at the action's time, 0.85 s before
  geometry. At approximately 173 s, hybrid and action C0/C1 are both
  -0.26 m / -0.0745 rad. These are commands, not measured unwind times.
- Across 76 eligible marked entry windows, median retained geometry extra demand
  is 91%, with a 10th percentile of 51%. Eligibility includes same-direction
  samples before the marked action peak, geometry above 50° wheel-equivalent and
  more than 5° stronger than action. It excludes conflicting-direction preview.
- In 83 windows with paired sustained release crossings, median added reference
  delay versus action is 0 s; maximum is 0.102 s. Route 157 event 5 disengages
  before a sustained hybrid release can be observed. First threshold crossings
  do not rule out later rebounds; final crossings and complete traces were also
  inspected. Some windows include another turn or driver intervention.
- For gentle raw sources (both below 0.010/m), the selector returns action.
  Limiter and integrator history can still differ. Pooled 95th-percentile
  C0/C1 differences are zero, but worst C1 difference is 0.0755 rad; on 15a the
  C1 95th-percentile difference is 0.002 rad.

## Limits of the design

1. A temporary action dip looks like an exit to the selector. In route 151,
   before the action later recovers, action/geometry/hybrid are approximately
   26°/122°/30°. This rule cannot prove that reducing assistance there is correct.
2. Conflicting-direction preview is discarded. On 15b event 4, the hybrid retains
   only about 5% of eligible extra geometry demand before the marked action peak.
3. Large geometry requests can be inherited, including approximately 807° on an
   older route. Similar command numbers do not establish correct path following.
4. Rapid low-speed commands remain. Across these routes, at below 15 mph,
   hybrid has 1,054 adjacent C0 changes over 0.25 m and 583 C1 changes over
   0.05 rad, versus geometry's 972/558 and action's 658/478. These include recorded
   driver-gate transitions and are not a physical comfort measurement.
5. The selector has peak memory. Closely spaced same-direction turns can inherit
   the earlier action peak until geometry crosses the reset condition.

This is a promising numeric division of work, not evidence of improved physical
tracking. No PSCM model, neural-model rerun, or camera replay was used. The recent
routes log action and geometry separately and join by exact model timestamp.
Older geometry is reconstructed with recorded delay/model smoothing; speed is
approximated by the first control sample consuming the model frame.

## Validation and artifacts

Production integration carries the geometry reference inside the same `modelV2`
message as the original action. Neither `modelV2.action` nor
`drivingModelData.action` is overwritten. controlsd selects the hybrid at control
cadence before the existing curvature limiter; desired curvature/steering angle,
C0/C1 and measured-wheel feedback all use that combined reference. Missing,
invalid or mismatched geometry falls back to action and clears selector memory.
Inactive/invalid controller inputs and lateral-maneuver priority also clear it.
Diagnostics identify `geometry-assisted-action-feedback-v18` and include geometry
assistance weight and the stored action peak. Geometry telemetry's selected field
now describes the smoothed geometry source, not the final controlsd target.

Keep **Selected-Action Path Tracking** and **Model Geometry Assist** enabled for
the hybrid. The stored geometry key is unchanged, so an enabled direct-path trial
becomes this hybrid after updating and restarting. Geometry assist off selects
action-only; the main controller toggle off selects upstream Ford control even
if the geometry key remains enabled. Settings apply after an offroad/onroad cycle.

The production adapter was replayed over all five routes again. Every value in
every output column exactly matches the approved offline candidate, including
reference, C0/C1, correction state and validity. See
`ford_geometry_action_hybrid_validation.json` for counts, source hashes and
the equality check. Real serialized messages are additionally tested through
the actual controlsd selection/limiter/feedback branch and real CAN packing.

- 20 prototype tests, including finite inputs/configuration, repeated frames,
  direction changes, causality and the real exit-rebound regression.
- Six-variant replay checked finite outputs, field bounds, zero C2/C3 and driver
  feedback suppression; real CAN packing/unpacking every tenth control cycle
  supplied 347,256 checks. The revised hybrid added 57,876 checks.
- Unchanged baseline columns can be reused when iterating the selector. A complete
  fresh revised 15a run exactly matched every output in the cached-baseline run.
- Twelve reference settings on each recent route: start 0.006/0.010/0.015 per m,
  full twice start, release power 1/2/4/8. These alternatives check references
  only; the selected configuration also has complete C0/C1 replay. Larger powers
  sacrifice more entry demand and can increase command discontinuities.

Outputs are under `.cache/ford_hybrid` (first version),
`.cache/ford_hybrid_guarded` (revised), and `.cache/ford_hybrid_verify/15a`
(fresh replay equivalence check). Per-route JSON records runtime source hashes;
older first-version hashes intentionally differ from the revised source. HTML
and six plots are in the existing report server directory, at
`http://127.0.0.1:52447/geometry-action-hybrid.html`.

Reproduce using the configured Python environment and existing cached route data:

```sh
PYTHONPATH=.:opendbc_repo python -m pytest -q -p no:cacheprovider \
  openpilot/selfdrive/controls/tests/test_ford_geometry_action.py

PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/hybrid_reference_replay.py \
  --route 15a --output .cache/ford_hybrid_fresh

PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/hybrid_reference_sweep.py \
  --route 15a --output .cache/ford_hybrid_fresh

PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/hybrid_reference_report.py \
  --root .cache/ford_hybrid_guarded --initial-root .cache/ford_hybrid \
  --output /path/to/report/directory
```

Repeat full replay for the other route labels and sensitivity for 15b. The report
includes both favorable and unfavorable examples; it does not tune to a single
turn or claim the replayed feedback trajectory would survive changed actuation.
