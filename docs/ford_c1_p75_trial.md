# Ford C1 proportional trial: P=0.75

Route 149 contains large steering shortfalls before driver intervention while
the selected curvature matches the model and neither C1's bound nor the PSCM
reached-limit flag explains the shortfall. This trial raises the immediate C1
error correction from P=0.50 to P=0.75. I remains 0.25. Runtime changes are the
gain constant and the diagnostic version, `model-action-curvature-c0-distance-pi-v13`.

The intended effect is more correction while behind and more release correction
when measured steering exceeds the request. Increasing P does not establish a
faster physical response: it can also amplify measurement fluctuations and
produce oscillation. This is a trial coefficient, not a learned calibration.

The selected model action, +0.40 s low-speed preview, C0 distance setting and
formula, integral arithmetic, PSCM arbitration, field bounds, and 100 Hz sender
remain unchanged. C2/C3 stay zero. The existing default-off Sunnylink toggle
still selects the experiment on Ford CAN FD; toggle-off selects upstream Ford.

## Paired production replay

Compared explicit P=0.50 and P=0.75 production adapters with I=0.25 and fixed-7 m
C0 across 21 route extracts: 112–117, 119, 11a, 120, 124, 125, 146, 149, a0, a2,
a5, a9, b8, b9, ca, and Raptor 02. The passes cover 2,275,248 source cycles and
4,550,496 real Float32-to-CAN encode/decode round trips.

Both passes use the same recorded selected curvature, measured motion, model
geometry, input timestamps, and driver/PSCM flags. Older routes retain their
original model requests; their neural inference is not rerun with the new delay.
This compares commands, not predicted wheel motion or tracking accuracy.

Checks passed on every cycle: identical C0, eligibility, feedforward, overflow,
and feedback/driver/PSCM gates; finite and bounded output; inactive zero output;
zero C2/C3; exact decoded fields, mode and counter; and the expected 1.5 ratio
between proportional terms. Integration tests separately check the selected
defaults, downstream checksums, reference selection, reversals, driver override,
reached-limit behavior, duplicate measurements, and toggle-off upstream behavior.

On route 149, the P=0.50 replay agrees with the recorded path commands over the
clean scoring cohort to Float32 precision: maximum C0 difference 5.8e-8 m and C1
difference 1.5e-8 rad. Full SubMaster health and exact control execution clocks
are not in the extract; publication timestamps approximate them. Historical
versions used different command laws, so their recorded commands are not
expected to match this baseline.

Clean scoring excludes driver steering, unavailable feedback, inactive/invalid
control, the following second, and speed below 3 mph. It contains 11,128.80 s.
Durations use original timestamps, clipping gaps to 30 ms. Percentiles are
sample-based. Request-angle categories do not identify road geometry.

| Recorded request magnitude | Scored seconds | Mean absolute C1 change | P95 C1 change |
| --- | ---: | ---: | ---: |
| Under 10 degrees | 9,051.37 | 0.00088 rad | 0.00250 rad |
| 10–45 degrees | 1,631.68 | 0.00250 rad | 0.00900 rad |
| At least 45 degrees | 445.75 | 0.00829 rad | 0.03100 rad |

C1 bound exposure increases from 21.30 to 22.67 s over the clean cohort. Mean
absolute stored I changes from 0.005987 to 0.005984 rad; a larger P term changes
the remaining accumulation headroom even though I's gain is unchanged.

The largest small-request C1 difference is 0.093 rad on route 117, where the
recorded request is +4.6 degrees and the wheel is still at -210 degrees. This is
a large release error, not ordinary centering. Restricting both requested and
actual wheel angle to within 10 degrees leaves 8,788.38 s: mean absolute C1
change 0.00073 rad, P95 0.00200 rad, maximum 0.01250 rad. These measurements do not
establish preserved centering or closed-loop stability.

In route 149, the candidate increases the C1 request at the reviewed entry
misses and reduces the remaining turn command during the clean segment-14
release. Its clean C1 bound exposure rises from 0.23 to 0.61 s. The paired I
traces remain nearly identical. The local report includes five entry, reversal,
and exit comparisons with the recorded wheel trace clearly distinguished from
replayed command traces.

## Validation and reproduction

455 tests and 25 subtests pass, including Ford controller/adapter/selection,
C0 distance settings, diagnostic logging, delay helpers, and Ford CAN tests.
The actual controlsd-to-CAN integration test failed at the old proportional
output before changing the default, then passed at the new setting. Ruff and
`git diff --check` pass. A device build, installation, and physical evaluation
are not part of these offline checks.

The compact evidence record is [ford_c1_p75_validation.json](ford_c1_p75_validation.json).
Full command arrays and per-route reports are in `.cache/ford_p75_trial` locally.
Reproduce one route using the built cereal/opendbc environment:

```sh
PYTHONPATH=.:opendbc_repo PYTHONDONTWRITEBYTECODE=1 python \
  tools/ford_pscm_lab/proportional_replay.py \
  --routes 149=.cache/ford_route149/full \
  --output .cache/ford_p75_recheck --workers 1
```

Additional `label=extract-directory` pairs replay independently. Each directory
must contain `route.npz`, `model_paths.npz`, and `metadata.json`; injection routes
are rejected. The input hashes are recorded in each result. The new test is
worth evaluating as a bounded change, but improved entry and preserved smooth
release still require measured vehicle response.
