# Ford selected-action drive-test branch

The current experiment adds [measured-curvature C1 feedback](ford_c1_feedback.md)
and [conditional correction release](ford_c1_carryover.md) to the restored
original v1 mapping, with [base C1 overflow allocated to C0](ford_c1_overflow.md).
It is selectable on **any Ford CAN FD vehicle**
through the existing persistent, default-off Sunnylink
toggle. Offline checks establish software behavior; physical tracking,
turn-exit behavior and closed-loop stability remain unvalidated.

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
identify **`hypothesis=model-action-c1-feedback-v3`**. They report desired and
measured curvature, base heading, accumulated correction, applied heading,
feedback timing and driver/PSCM gating. `carryover_release_count` counts
conditional releases since the last controller reset; it does not control
steering. `offset_overflow` reports the extra C0 target in meters before C0
amplitude and slew limits. `calibration_approved=false` remains.

Turning the toggle off and completing another offroad-to-onroad cycle restores
**PSCM Coefficient Observer** if selected, otherwise the original Ford path
controller. The stored observer selection is preserved. The experiment takes
priority on Ford CAN FD vehicles; other vehicles retain their existing
controller. A leftover `FordVirtualAngleController` parameter has no effect.

## Wiring and validation

`controlsd` supplies the selected, upstream-limited desired curvature and the
measured steering-derived curvature already used in its tracking diagnostics.
Fresh steering publications advance C1 feedback. Repeated publications may
advance output slew but cannot integrate the same elapsed interval twice.
Driver override clears the correction. A fresh PSCM reached-limit flag stops
extra outward accumulation while preserving unwind and base model changes.
With fresh feedback, the controller can discard an opposing correction when
it prevents C1 from following the direction shared by original model C0, applied C0
and base C1, while measured curvature is still opposite. Neutral or conflicting
C0 and matched curvature preserve the correction. Final output slew still applies.

C0 starts with the original 7 m model-path mapping. When the raw base heading
exceeds ±0.5 rad, C0 additionally receives 7 m times the clipped-away heading.
Accumulated C1 feedback does not spill into C0. The extra target returns to zero
as the base heading falls below the cap; applied C0 still follows its 4 m/s slew.
C2 and C3 remain zero. The
existing output limits, 100 Hz sender, Float32 publication and CAN builder
remain in place. No opendbc submodule or Panda safety change is required.

See [the overflow specification and validation](ford_c1_overflow.md) and
`ford_c1_overflow_validation.json` for current evidence and reproduction
commands. The carryover specification and `ford_c1_carryover_validation.json`
record the previous experiment. `ford_c1_feedback_validation.json` records the initial feedback
version at `5fbb583e5`. `ford_model_action_validation.json` and
`ford_model_action_drive_test_validation.json` are historical records for the
original offline candidate and its first wiring, respectively; their counts
and coverage are not claims about the current version.

The full hardware build and device boot are not performed by these offline
checks. Pushing the branch does not install it on the device or change its
stored toggle.
