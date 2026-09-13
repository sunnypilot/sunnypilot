# Ford selected-action drive-test branch

This local v8 candidate uses [curvature-derived C0](ford_curvature_c0_v8.md)
and [continuous C1 PI feedback](ford_c1_minimal_pi.md)
with **P=0.50 and I=0.25**.
Only C0, C1 and accumulated error carry control history. C0 is now a 7 m circular arc from selected desired curvature.
[Base C1 overflow allocation to C0](ford_c1_overflow.md) remains.
It is selectable on **any Ford CAN FD vehicle**
through the existing persistent, default-off Sunnylink
toggle. Offline checks establish software behavior; physical tracking,
turn-exit behavior and closed-loop stability remain unvalidated.

The v8 implementation is on local branch `codex/ford-curvature-c0-trial`.
This evaluation does not push it to `hiimisaac-dev`; the deployed v7 commit is
`08b3a14ad`. The selection instructions below apply once a candidate is installed.

## Select and restore

1. Install branch `hiimisaac-dev` from `sunnypilot/sunnypilot` using the device's
   normal branch-switch process and allow its build to finish.
2. While offroad, open Sunnylink device settings → Vehicle → Ford and enable
   **Selected-Action Path Tracking (Experimental)** (`FordModelActionController`).
3. Complete a real offroad-to-onroad cycle. Selection occurs when `controlsd`
   starts; a stored toggle change or disengagement alone cannot swap an active
   controller. Initial physical evaluation remains controlled testing.

The startup event `Ford path controller selected` should report
`FordModelActionController`. Periodic `Ford C2-free path tracking` events
identify **`hypothesis=model-action-curvature-c0-pi-v8`**. They report desired and measured
curvature, base heading, proportional and accumulated correction, applied heading,
feedback timing and driver/PSCM gating. `proportional_gain=0.5` and
`integral_gain=0.25` identify the trial. `offset_overflow` reports the extra C0
target in meters before C0 amplitude and slew limits. `calibration_approved=false`
remains. The retired request/unwind/reversal diagnostic fields are removed.

Turning the toggle off and completing another offroad-to-onroad cycle restores
**upstream Ford curvature control**: 20 Hz steering messages, limited mode on
CAN FD, zero C0/C1/C3, and upstream curvature limiting and platform-specific
overshoot handling. Stored observer or retired controller settings cannot select
a custom controller. The observer toggle is no longer exposed. The experiment
only runs on Ford CAN FD vehicles; legacy Ford uses upstream control as well.
See [toggle-off validation](ford_upstream_fallback.md).

## Wiring and validation

`controlsd` supplies the selected, upstream-limited desired curvature and the
measured steering-derived curvature already used in its tracking diagnostics.
Fresh steering publications advance C1 integration. P responds to the current
error without accumulating. Repeated publications may advance P and output slew
but cannot integrate the same elapsed interval twice.
Driver override clears P and I. A fresh PSCM reached-limit flag stops
extra outward accumulation while preserving unwind and base model changes.
With fresh feedback, the part of the error increment that cancels existing I
is applied before the ordinary accumulation clamp. Any remainder must fit the
combined feedforward/P/I amplitude and slew envelope. There is no C0 confirmation
threshold or remembered turn direction. Zero error removes P and holds I; it
does not trigger a release. Final command limits still apply.

C0 starts with the 7 m circular arc of selected desired curvature. It does not
add independent live model-path position or heading. Valid model geometry is
still required as a health gate. When the raw base heading
exceeds ±0.5 rad, C0 additionally receives 7 m times the clipped-away heading.
Accumulated C1 feedback does not spill into C0. The extra target returns to zero
as the base heading falls below the cap; applied C0 still follows its 4 m/s slew.
C2 and C3 remain zero. The
existing output limits, 100 Hz custom sender and Float32 publication remain in
place. An explicit selection flag distinguishes upstream mode from an invalid
experimental command; invalid experimental input cannot switch to upstream.
The opendbc sender restores upstream behavior when that flag is false.

See [curvature-C0 trial and validation](ford_curvature_c0_v8.md) and
`ford_curvature_c0_v8_validation.json` for this candidate.
[Continuous PI](ford_c1_minimal_pi.md) and its validation JSON record v7.
[Proportional feedback](ford_c1_pi.md) and its validation JSON record v6.
[Completed-unwind release](ford_unwind_catchup.md) and
`ford_unwind_catchup_validation.json` record v5. [Changed-request release](ford_c1_request_release.md) and its
validation JSON record v4. The [overflow specification](ford_c1_overflow.md) and
`ford_c1_overflow_validation.json` record v3. The carryover specification and `ford_c1_carryover_validation.json`
record the previous experiment. `ford_c1_feedback_validation.json` records the initial feedback
version at `5fbb583e5`. `ford_model_action_validation.json` and
`ford_model_action_drive_test_validation.json` are historical records for the
original offline candidate and its first wiring, respectively; their counts
and coverage are not claims about the current version.

The full hardware build and device boot are not performed by these offline
checks. Pushing the branch does not install it on the device or change its
stored toggle.
