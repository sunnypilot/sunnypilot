# Ford C2-free path tracking with measured feedback

Hypothesis `curvature-c0-c1-feedback-v5` retains v4's absolute desired-curvature
C0/C1 requests and adds a bounded yaw-error integral to C1. Persistent measured
shortfall can increase the request without requiring the planner to keep
increasing curvature; excess turning can reduce it. C0 and its centering
input are unchanged. C2/C3 remain zero.

This is an experimental outer feedback loop around the multivariable PSCM.
It is not an angle servo or a calibrated C0/C1-to-wheel mapping. Its feedback
scale and response interval are not road-validated.

## Evidence and scope

Route80 ran v3 (`98662df40`) and contains both sustained under-response and
over-response. Representative eligible windows had median CAN response/request
ratios of 0.78, 1.77 and 0.69 with a declared 0.2-second comparison interval.
These are descriptive ratios, not gains or percentages of a maneuver completed.
Wheel-model curvature agrees on the directions of these discrepancies.

V4 (`0ace0b051`) replaced separate model-heading C1 with the selected curvature
reference and reduced C1 in several large maneuvers. The user then reported
steering repeatedly stopping near 85 degrees. No recording of that new symptom
was available during implementation. Older logs contain much larger wheel
angles. The inspected host path has no fixed 85-degree wheel stop, but an
upstream speed-dependent curvature limit remains.

Restoring larger C1 everywhere also restores excess demand in known
overshoot cases and barely changes some sustained shortfalls. V5 tests whether
measured correction can distinguish them. Replaying old motion verifies
command construction, not the truck's counterfactual response or a fix for
the unrecorded plateau.

## Base request and feedback

controlsd uses valid `lateralManeuverPlan.desiredCurvature`, otherwise
`modelV2.action.desiredCurvature`, after the existing curvature limiter:

```text
L0 = max(8 m, speed × 1 s)
L1 = max(7 m, speed × 1 s)
C0_target = clip(0.5 × desired_curvature × L0², ±5.11 m)
C1_base = clip(desired_curvature × L1, ±0.5 rad)

past_request = selected curvature held at or before (measurement_time − delay)
yaw_error = measured_speed × past_request − measured_yaw_rate
bias_trial = released_bias + feedback_gain × yaw_error × measurement_dt
C1_target = clip(C1_base + accepted_bias, ±0.5 rad)
```

Measured yaw is negated Ford CAN yaw rate, matching the control sign convention.
The historical request uses zero-order hold, never interpolation toward a
command published later. Nominal delay is `CP.steerActuatorDelay` (0.2 s on
the source vehicle). This delays only the error comparison; it does not
advance the already delay-aware current action again.

The integration scale is **1.0**. Integrating compatible rad/s and rad units
does not make it gain-free or establish stability. Preview distances are also
effective gains. No adaptive wheel-response gain is identified.

| Quantity | Value |
|---|---:|
| C0 / C1 bounds | ±5.11 m / ±0.5 rad |
| Independent C0 / C1 slew | 4 m/s / 0.5 rad/s |
| New feedback scale | 1.0 |
| Feedback minimum speed | 2 m/s |
| Maximum PSCM status age | 150 ms |
| Allowed timestamp lead | 5 ms |
| Release comparison tolerance | one C1 wire quantum, 0.0005 rad |

Zero yaw error retains the acquired bias and absolute base. Reaching the target
does not remove the additional demand that may be sustaining the turn.

## Release and limits

When the clipped base magnitude decreases, bias decreases in the same ratio.
Using the clipped base avoids increasing total C1 by shrinking a negative bias
while the base stays saturated. Zero request or reversal clears bias and
requires fresh reference history. Existing output slew still applies.

Integration is inhibited if the delayed request has the old sign or exceeds
the current request by more than one heading quantum after multiplying the
curvature difference by L1. This prevents old demand from rebuilding correction
during release while tolerating sub-quantum planner changes.

Host anti-windup considers both field and slew limits on the combined base
and trial bias. It admits only reachable correction in the intended increment
direction when an outward update hits a host limit, and permits inward
unwinding. A large error must not stall correction merely because its entire
increment cannot fit within one tick. Retained bias is bounded by available
C1 field headroom. No overflow goes into C0; no safety limit is raised.

Actual PSCM LimitReached freezes all new integration while base-driven
release continues. C1 sign is not interpreted as motor-effort direction.
Host bounds and generic status cannot identify internal PSCM dynamics or
guarantee prevention of downstream windup.

## PSCM status and driver handling

card publishes the existing Ford parser's `Lane_Assist_Data3_FD1` status in
`carStateSP.fordPscmStatus`, using its original CAN receipt timestamp.
Republishing carStateSP or receiving unrelated CAN frames cannot refresh it.
The opendbc submodule is unchanged.

Feedback requires valid fresh status, InProgress lateral state (2), capability
LimitedModeAvailable or ExtendedModeAvailable (1 or 2), and no denial.
Missing, malformed, stale, backward-timestamped, denied or unavailable status
clears feedback bias/history. Base control keeps its existing validity rules.
LimitReached (2) freezes integration; LimitWithDriverActive (3) clears feedback.

`steeringPressed`, raw torque above the existing Ford driver allowance, or
nonfinite torque also clear feedback immediately. The baseline request retains
its existing PSCM driver-arbitration behavior while lateral control remains
authorized. An unset override flag cannot exclude subthreshold driver influence.
A fresh reference interval is required after override.

Below 2 m/s feedback clears; base C0/C1 keep their original speed gates.
The correction does not learn a persistent zero-request bias. It is not a
complete zero-yaw or lane-centering servo; centering intent continues to enter
through selected desired curvature and C0.

## Existing gates and selection

Core model/action/car-state freshness, finite-value, clock and speed checks
are unchanged. Invalid core inputs reset both commands and clear latActive.
Model geometry remains for diagnostics and its existing validity gate; its
filtered heading does not command C1.

Vehicle → Ford → **C2-Free Path Tracking (Experimental)** retains the existing
`FordVirtualAngleController` key and default-off setting. An already-enabled
setting selects v5 after updating and restarting controlsd. Selection remains
limited to Ford CAN FD, `FORD_F_150_LIGHTNING_MK1`, and EPS firmware
`RL38-14D003-AA`. It takes priority over PSCM Coefficient Observer. Turning it
off and cycling offroad/onroad restores the previous controller selection.
No live device setting is changed by this commit.

## Diagnostics and verification

The 5 Hz `Ford C2-free path tracking` event identifies v5 and records the
selected reference, measured curvature/yaw, base and corrected C1 targets,
bias, integration status, historical request/time, yaw error, raw torque and
PSCM freshness/status. `angleState.saturated` is not an EPS-limit substitute:
it describes tracking error on this path.

Checks cover deficit/excess response, retained turn demand, release/reversal,
driver/status resets, delayed history, repeated measurements, host/PSCM limits,
unchanged C0, C2/C3 zero, telemetry timestamps, CAN packing and recorded
maneuvers. Missing-status behavior preserves v4 commands. Replay holds recorded
motion and planner outputs fixed and cannot establish physical improvement
or closed-loop stability.

The final v5 replay covered 52,273 route80 cycles with reconstructed causal
PSCM status and raw driver torque. C0 and output-validity gates were unchanged;
C2/C3 stayed zero and command bounds, slew and reference causality passed.
Median eligible C1 magnitude changed from 0.144 to 0.178 rad in the 333–339 s
shortfall and 0.190 to 0.267 rad in the 430–435 s shortfall. The 417–420 s
over-response window stayed at 0.286 rad: 102 of its 105 eligible samples
reported LimitReached, suppressing new integration. This is a known limitation
of the guarded candidate, not a demonstrated overshoot improvement.
The separate no-status replay preserved v4 C1 and old C0/gates exactly over
246,961 cycles across all 43 supplied segments.

The next enabled logs must show whether tracking error diminishes without
oscillation, excess release overshoot or increased intervention. A shortfall
when the selected reference or available commands are already limited remains
a separate case. This feedback cannot create new physical authority.
