# Ford C1 early-release experiment

The a9 recording contains holds followed by rapid steering release while C0/C1
requests were already decreasing. Several occur without a PSCM limit flag or
detected driver input. The experiment changes C1 alone to ask for less turning
when the model's path straightens ahead. It does not establish which internal
PSCM mechanism caused those holds.

## Request mapping

Keep the v7 sample station `s`: model arc distance at one second, with the
existing seven-metre minimum and endpoint hold. Let `psi` be unwrapped model
heading at that station and `psi0` its initial heading. Using the same model
segment enclosing that point:

```
terminal_curvature = change in heading / change in arc distance
release_heading = psi0 + s * terminal_curvature
C0_target = model lateral position at s
C1_target = release_heading bounded between zero and psi
C2 = C3 = 0
```

The C1 interval respects the sign of `psi`. The correction cannot amplify the
raw heading target or manufacture an opposite-direction target. A real model
sign reversal continues through the normal slew. At an exact model knot the
incoming segment supplies the slope. A duplicate selected station, zero span,
or nonfinite derived slope retains the original heading.

Heading linear in the sampled cumulative arc distance, and constant heading,
retain the original mapping. Arc distance uses model-point chords, so even a
true circle can differ slightly under uneven sampling; exact preservation is
a statement about the discrete heading slope, not every sampled physical arc.
When the terminal curvature is gentler than the average over the preview, C1
can decrease sooner; it can reach zero even while the future pose still has a
nonzero heading. C0 continues requesting that future lateral position.

There is no temporal turn-mode latch, new strength multiplier, measured-yaw
correction, fitted PSCM model, or foreign firmware command cap. Only the two
existing C0/C1 slew positions persist. Limits remain ±5.11 m / ±0.5 rad and
4 m/s / 0.5 rad/s; transmission remains 20 Hz.

## Physical question and tradeoff

The question is whether unloading C1 sooner makes the measured wheel release
sooner, without unacceptable loss of turning authority. Constant discrete
heading slope is preserved; not every real turn-in is guaranteed unchanged. A model
point can already lie on the straight after a corner while the truck still
needs heading change to reach it. This rule can then remove useful C1. C0 and
the PSCM's physical response determine the result, which passive replay cannot
establish.

The prior ML3V firmware's internal contribution limits are not treated as
Lightning limits. `LimitReached` is not used as a release trigger. No claim is
made that this fixes the a9 hang, tracking error, or stability across PSCMs.
`calibration_approved=false` remains.

## Recorded command comparison

The a9 comparison uses 7,199 original-clock models and 35,775 control cycles
from six recorded segments. Candidate C0 is exactly equal to baseline C0 at
raw target, publication, and sampled send times. Raw C1 never exceeds the
original heading magnitude or invents a reversal. Independent slew histories
can let the candidate reach a genuine opposite-direction target sooner, so
published C1 magnitude is not universally smaller on reversal.

Entry and plateau changes are included, rather than scoring only exits:

| Recorded window | Baseline mean absolute C1 | Candidate mean absolute C1 |
| --- | ---: | ---: |
| Right entry, 38:47–38:50 | 0.13643 rad | 0.12561 rad |
| Large left entry, 40:01–40:05 | unchanged | unchanged |
| Right plateau, 45:26–45:28.4 | 0.11442 rad | 0.10506 rad |
| Left entry, 45:34–45:36 | 0.16580 rad | 0.15962 rad |

C1 crosses a common 0.1 rad level about 0.80–0.85 seconds earlier in three
selected exits. The level is a comparison marker, not a PSCM limit. On the
right exits near 38:51 and 45:29, it stops requesting the original turn
direction 0.454 and 0.356 seconds earlier. These are proposed command times
on frozen inputs, not measured improvements in wheel release.

The baseline replay agrees with recorded publication within one wire quantum
after cache-boundary warmup; logged publication times do not provide every
internal controller-entry time. Original clocks, eligibility, and that
reconstruction tolerance are retained in the validation record.

## Selection and verification

Use the existing default-off Sunnylink **Selected-Action Path Tracking
(Experimental)** toggle (`FordModelActionController`). An already enabled
setting selects this revision after updating and an offroad-to-onroad cycle.
The diagnostic identity is `model-pose-terminal-c1-v1`; active diagnostics also
report `c1_release=terminal_spatial_curvature`. Turning the toggle off restores
the previous nonexperimental selection after another offroad-to-onroad cycle.

See the [drive-test guide](ford_model_action_drive_test.md) and the
[validation record](ford_model_release_validation.json). Unit/integration checks
cover command construction, bounds, reset, sender cadence, and encoding. Route
comparisons report changes in commands, including entry attenuation; they do
not predict wheel motion under the changed commands. The next recording must
compare desired versus actual steering and release timing on the actual PSCM.
