# Ford C1 integral trial: I=1.0

Route 151 had large entry shortfalls before driver input while C1 still had
command range available. At the segment-5 right-turn shortfall, the selected
request was 125 degrees right and the wheel was at 49 degrees right. The stored
correction was only 0.015 rad and was growing at about 0.0245 rad/s. Neither the
C1 field bound nor the PSCM reached-limit flag explained that point.

This trial raises I from 0.25 to **1.0**, keeping P at **0.75**. The fresh-error
increment is four times larger for the same curvature error, speed and elapsed
measurement time. This also retires existing correction four times faster for
the same opposing error, before the existing accumulation/headroom rules apply.
It does not introduce a new state, rate limit, threshold or release heuristic.
Runtime changes are one gain constant and the diagnostic identifier
`model-action-curvature-c0-distance-pi-v14`.

C0's desired-curvature formula and distance toggle, base C1, +0.40 s low-speed
model preview, feedback measurement, driver override, PSCM arbitration, field
bounds and 100 Hz sender remain unchanged. Zero error holds I. Driver override
clears P and I. Fresh limitReached blocks outward accumulation while allowing
retirement. Accumulation cannot charge beyond the combined command's available
range. C2/C3 stay zero, and toggle-off still selects upstream Ford control.

## Why this coefficient

Compared I=0.25, 0.50, 1.0 and 2.0 with P=0.75 on routes 149 and 151, using
the production adapter and Float32/CAN path for every sample. I=1.0 gives a
substantial increase in retained correction. I=2.0 adds considerably more
opposite-direction correction on reviewed exits and approaches the C1 bound
in the route-151 right turn. I=1.0 is a fourfold experimental step, not an
offline-fitted optimum or a validated physical calibration.

Paired fixed-motion examples with I=0.25 / I=1.0:

| Route / time | Recorded situation | C1 before | C1 candidate |
| --- | --- | ---: | ---: |
| 151 / 306.891 s | 125-degree right request, 49-degree wheel | +0.3270 | +0.3725 |
| 151 / 307.999 s | Wheel remains behind on the same right turn | +0.2675 | +0.3625 |
| 151 / 2363.807 s | 137-degree left request, 64-degree wheel | -0.3410 | -0.3785 |
| 149 / 319.549 s | Right-turn entry shortfall | +0.4190 | +0.4840 |
| 149 / 850.497 s | Right-turn release | +0.0670 | +0.0010 |
| 149 / 851.331 s | Near center on that release | +0.0105 | -0.0460 |

These are same-cycle controller requests, not necessarily the preceding CAN
message at that timestamp. Positive C1 requests right steering; positive logged
wheel angle means left. Both replays use P=0.75; route 149 originally drove
P=0.50, so the old-I replay is not its historical command trace.

The exit examples show why faster retirement does not guarantee a smoother
unwind: the candidate can accumulate more correction in the opposite direction
and retain it when error reaches zero. Higher I also affects centering. On
route 151's clean requests under 10 degrees, mean absolute C1 rises from about
0.0083 to 0.0122 rad on the fixed recording; route 149 rises from 0.0077 to
0.0154 rad. The vehicle would generate different errors under the candidate.
These are command observations, not predictions of wheel motion, stability,
overshoot, or future tracking accuracy.

## Broader validation

The paired production replay covers 22 extracts: 112–117, 119, 11a, 120, 124,
125, 146, 149, 151, a0, a2, a5, a9, b8, b9, ca and Raptor 02. It processes
2,600,956 source cycles and 5,201,912 Float32/CAN round trips. Both settings have
identical eligibility, C0, P, base heading, overflow, and driver/PSCM feedback
gates on every cycle. Output remains finite and bounded; inactive commands and
C2/C3 are zero. The decoder checks fields, mode and counter on every command.

Scoring excludes driver override, inactive/invalid control, disabled feedback,
the following second, and speeds below 3 mph. There are 12,213.62 scored seconds.
C1-bound time rises from 22.67 to 25.13 seconds. Route 151 has no C1-bound samples
in that cohort under either setting. Its I=0.25 baseline matches the recorded
path output to Float32 precision: maximum C0 error 5.8e-8 m, C1 error 1.5e-8 rad.
Older routes intentionally retain their original model requests and physical
measurements, including any historical tracking errors. Their baseline command
traces need not match older controller implementations.

The existing controlsd-to-publication-to-CAN feedback test was updated before
the gain change. It failed on the old default (0.005 rad accumulated versus
0.020 rad required over its one-second error interval), then passed with the
new default. **468 tests and 25 subtests pass**, covering selection, current
references, accumulation/hold/retirement, reversals, duplicate measurements,
PSCM limits, driver overrides, downstream checksums and upstream fallback.
Ruff and `git diff --check` pass. No device build or physical evaluation is
claimed by these offline checks.

Evidence: [ford_c1_i1_validation.json](ford_c1_i1_validation.json). Local arrays
are in `.cache/ford_i1_trial`, with the four-setting comparison in
`.cache/ford_i_trial_sweep`. Reproduce a comparison:

```sh
PYTHONPATH=.:opendbc_repo PYTHONDONTWRITEBYTECODE=1 python \
  tools/ford_pscm_lab/proportional_replay.py \
  --routes 151=.cache/ford_route151/full 149=.cache/ford_route149/full \
  --settings .75:.25 .75:1.0 \
  --output .cache/ford_i1_recheck --workers 2
```

The replay tool's default P=0.50 / P=0.75 comparison with I=0.25 is preserved.
Explicit `--settings` accepts P:I pairs; the first is the baseline. Publication
timestamps approximate execution time because full process scheduling and
SubMaster state are not logged. The trial still needs physical measurement;
route 151 also changed the big model from CTMV2 to Tee Time, so its comparison
with route 149 cannot isolate the controller's physical effect.
