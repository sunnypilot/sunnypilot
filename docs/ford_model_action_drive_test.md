# Ford selected-action drive-test branch

This v14 trial increases C1's integral gain from 0.25 to **1.0**, retaining
P=0.75, [curvature-derived C0](ford_curvature_c0_v8.md), direct C0/C1 requests,
and [continuous C1 PI feedback](ford_c1_minimal_pi.md).
Only integrated tracking error accumulates correction; C0/C1 reflect the current bounded request. C0 defaults to a 7 m circular arc from selected desired curvature. An on-device toggle can instead use max(7 m, speed × 1 second).
[Base C1 overflow allocation to C0](ford_c1_overflow.md) remains.
It is selectable on **any Ford CAN FD vehicle**
through the existing persistent, default-off Sunnylink
toggle. Offline checks establish software behavior; physical tracking,
turn-exit behavior and closed-loop stability remain unvalidated.

Both base commands use selected, upstream-limited desired curvature. The +0.40 s
low-speed model preview from `b720e9f1b` remains: full offset at 15 mph and below,
tapering to zero at 30 mph. The trial multiplies each fresh integral error increment
by four, for both accumulation and retirement. P, PSCM `LimitReached` handling,
integral arithmetic, field bounds, and selection are retained.
See [I=1.0 replay results](ford_c1_i1_trial.md) for scope, tradeoffs, and reproduction.

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
identify **`hypothesis=model-action-curvature-c0-distance-pi-v14`**. They report desired and measured
curvature, base heading, proportional and accumulated correction, applied heading,
feedback timing and driver/PSCM gating. `proportional_gain=0.75` and
`integral_gain=1.0` identify the trial. `offset_overflow` reports the extra C0
target in meters before C0 amplitude limits. `calibration_approved=false`
remains. The retired request/unwind/reversal diagnostic fields are removed.

Turning the toggle off and completing another offroad-to-onroad cycle restores
**upstream Ford curvature control**: 20 Hz steering messages, limited mode on
CAN FD, zero C0/C1/C3, and upstream curvature limiting and platform-specific
overshoot handling. Stored observer or retired controller settings cannot select
a custom controller. The observer toggle is no longer exposed. The experiment
only runs on Ford CAN FD vehicles; legacy Ford uses upstream control as well.
See [toggle-off validation](ford_upstream_fallback.md).

## C0 distance toggle on comma four

With the experimental Ford controller enabled, open **Settings → toggles → C0: 1 second**.
The toggle is visible for Ford CAN FD vehicles and can be changed while disengaged.

- **Off (default):** C0 uses a fixed 7 m arc.
- **On:** C0 uses a distance of max(7 m, speed × 1 second), matching the base C1 distance.

Disengage assistance, change the toggle, and remain disengaged for at least three seconds
before reengaging. This setting uses the existing three-second runtime parameter refresh;
**no ignition cycle or controlsd restart is required**. Engaged or paused MADS and stale
engagement messages prevent applying a change. A mode change resets the PI correction and
adapter timestamps. Reapplying the same value does not reset anything.

The persistent parameter is `FordC0TimeBased`. It cannot enable the experimental controller
by itself. The existing Sunnylink controller-selection toggle still requires an onroad cycle.
C1, the gains, the 7 m heading-overflow allocation, the upstream reference limits and the CAN
field bounds are unchanged. Below 7 m/s (about 15.7 mph), both distance modes are identical.
At 20/30/60 mph the enabled distance is approximately 8.9/13.4/26.8 m, respectively; C0 can
therefore be substantially larger, especially at higher speeds. Its release still follows the
current selected curvature immediately, with no additional slew.

The `Ford C0 distance changed` event records an applied switch. Periodic tracking events
include `c0_time_based` and the actual `offset_distance` in meters, including the default mode.
Offline checks verify selection, runtime switching, resets, unchanged C1 and CAN encoding;
they do not establish which distance the PSCM follows better.

Validation on 2026-09-14: 410 tests and 25 subtests passed, plus Ruff and the local comma four
UI construction/write/refresh/visibility/render check. The 54,146-cycle maneuver-route replay
(`84865544361f55cb/0000011c--99f4537696`) matched `775012167` exactly with the new toggle off.
With it on, C0 changed in 35,668 cycles (maximum difference 0.74 m), while C1 and accumulated
correction remained identical on the same recorded motion. The two comparisons completed
216,584 controller updates and CAN round trips. No vehicle build, installation or road test
was performed for this change.

## Wiring and validation

`controlsd` supplies the selected, upstream-limited desired curvature and the
measured steering-derived curvature already used in its tracking diagnostics.
Fresh steering publications advance C1 integration. P responds to the current
error without accumulating. Repeated publications use current feedforward and P
but cannot integrate the same elapsed interval twice.
Driver override clears P and I. A fresh PSCM reached-limit flag stops
extra outward accumulation while preserving unwind and base model changes.
With fresh feedback, the part of the error increment that cancels existing I
is applied before the ordinary accumulation clamp. Any remainder must fit the
combined feedforward/P/I amplitude envelope. There is no C0 confirmation
threshold or remembered turn direction. Zero error removes P and holds I; it
does not trigger a release. Final command limits still apply.

C0 starts with the selected-distance circular arc of selected desired curvature. It does not
add independent live model-path position or heading. Valid model geometry is
still required as a health gate. When the raw base heading
exceeds ±0.5 rad, C0 additionally receives 7 m times the clipped-away heading.
Accumulated C1 feedback does not spill into C0. The extra target returns to zero
as the base heading falls below the cap. Applied C0 changes in that same update.
C2 and C3 remain zero. The
existing field bounds, 100 Hz custom sender and Float32 publication remain in
place. An explicit selection flag distinguishes upstream mode from an invalid
experimental command; invalid experimental input cannot switch to upstream.
The opendbc sender restores upstream behavior when that flag is false.

[Direct-command validation](ford_direct_path_v9.md) records the same command law introduced in v9.
[Curvature-C0](ford_curvature_c0_v8.md) and its validation JSON record v8.
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
