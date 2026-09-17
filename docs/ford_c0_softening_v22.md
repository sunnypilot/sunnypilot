# Action-mode C0 feedback softening

Route 166 used v21 and improved normal driving, but the first two user bookmarks
showed roughly 2 Hz wheel oscillations around a smoother requested angle at
17–31 mph. The first occurred with uninterrupted feedback, small I and no
PSCM limitReached. Both C0 P and C1 P followed the error, so these recordings
do not isolate either channel's contribution to physical oscillation.

This trial changes C0 P only. With the curvature error converted into `x` metres
of C0 before applying the existing gain, the new correction is:

```text
C0 P = gain * (x - 0.125 * tanh(x / 0.25))
```

Near zero, the slope is half the old gain. It increases smoothly toward the old
gain without exceeding it. The response stays symmetric, monotonic and nonzero
for nonzero error; it introduces no time filter, deadband, cutoff or additional
state in the control law. Zero error removes P immediately, and opposite error
commands opposite P in the same cycle.

Large corrections lose at most 0.125 m times the existing C0 gain. This is a
bound on the difference from the old correction, **not a C0 command cap**.
The field bounds remain C0 ±5.11 m and C1 ±0.5 rad. The scale and minimum slope
are explicit drive-trial choices, not an identified stable PSCM calibration.
Scales 0.15, 0.25, 0.4 and 0.5 m were compared on route 166; 0.25 m preserves
about 96% of the good left's peak entry command while reducing the repeated
C0 command component in both wobbles.

The base action mapping, selected desired curvature, C1 P/I, delayed reference,
integral cadence and anti-windup, driver/PSCM arbitration, CAN cadence and
upstream limits are unchanged. The softening applies at all speeds in action
mode: the bookmarked wobbles were above the proposed 11.2 mph freeze cutoff.
Direct-path feedback retains its linear law; when it falls back to an action
reference, the action softening applies. The master toggle still selects
upstream Ford control when disabled. No new toggle is added.

Diagnostics identify v22 and include `offset_proportional_linear` alongside
the actual `offset_proportional`, so a new log can show exactly what softening
removed. The extra stored scalar is diagnostic only and resets with P.

## Validation

Five native-time route replays cover 646,178 cycles and 64,620 CAN encode/decode
checks: routes 149, 151, 157, 162 and 166. The v21 baseline matches its archived
commands and integral exactly. C1 commands, C1 P/I, reference, validity,
arbitration and base mapping remain identical on every cycle. C2/C3 remain
zero. The largest raw C0 P change is 0.125 m; after CAN quantization the
command difference is at most 0.13 m.

| Route-166 event | Repeating total C0 component, before → after | Reduction |
| --- | --- | --- |
| First wobble | 0.146 → 0.076 m peak-to-peak | 48% |
| Second wobble | 0.222 → 0.150 m peak-to-peak | 32% |
| Second wobble exit | 0.335 → 0.199 m peak-to-peak | 41% |

These use a same-frequency sine fit with quadratic trend removal. They measure
the **command**, not a predicted reduction in wheel oscillation. The good left's
peak entry C0 changes from -2.93 to -2.81 m; its mid-turn unwind peak changes
from +1.44 to +1.31 m. C1 is identical. Entry and unwind are both softened;
neither physical response is proven better by a frozen-motion replay.

Regression tests first failed against v21, then passed with v22. They exercise
small nonzero corrections, preserved large-error authority, monotonic bounded
incremental gain, immediate reversal/release, unaffected C1 and base mapping,
and the direct-path exception. Existing controls-to-CAN integration, model
selection, driver override, request-history timing and default-upstream tests
also pass. Exact counts and provenance are in
`ford_c0_softening_v22_validation.json`.

Reproduce a route comparison with the built Python dependencies:

```sh
PYTHONPATH=.:opendbc_repo:.cache/ford_geometry_deps python \
  tools/ford_pscm_lab/c0_softening_replay.py \
  --source .cache/ford_route166/full \
  --delay-intake .cache/ford_route166/intake.npz \
  --archive .cache/ford_feedback_delay_v21/166/commands.npz \
  --output .cache/ford_c0_softening_v22/166
```

For the next drive, the discriminating observations are whether small
left-right corrections settle sooner, whether centering becomes too loose,
and whether strong entry and prompt release remain. Do not interpret this
offline validation as a demonstrated physical stability fix.
