# Ford large-turn entry assist

The coordinated encoder can select the same C0/C1 packet even when its angle
target increases: larger fields sometimes have the same predicted next state,
and its tie break favors the smaller fields. This does not prove that the live
PSCM responds identically. This opt-in trial adds a bounded command after that
selection, making the turn-entry experiment observable at the CAN output.

## Enable and revert

In sunnylink Ford settings, keep **Selected-Action Path Tracking** and
**Coordinated C0/C1 Steering** enabled, and **Model Geometry Reference** disabled.
Enable **Large-Turn Entry Assist (Experimental)**, then make an offroad-to-onroad
transition. The setting is default off and read once at startup. Disabling only
the new setting and cycling offroad/onroad restores the previous coordinated
controller. Disabling Selected-Action Path Tracking restores upstream Ford
control. No hot switching or added steering-loop parameter I/O.

## Exactly what changes

The original desired steering angle, inverse, target-trend preview and centering
trim remain. An additional command is weighted by three continuous ramps:

- Requested angle magnitude: zero through 30 degrees, full at 60 degrees.
- Wheel lag into that turn: zero through 25 degrees, full at 50 degrees.
- Growing filtered target rate: zero at steady/relaxing target, full at
  30 degrees/second.

Multiply the three weights. At full weight, add **0.60 m C0 and 0.04 rad C1**
in the requested turn direction, then quantize and clip to the existing DBC
bounds. These are trial tuning values, not recovered Ford constants or a
guaranteed conversion to wheel angle. The 4× label refers to the earlier offline
starting budget of 0.15 m / 0.01 rad, not a multiplication of all steering.

Only the extra term is suppressed on steeringPressed, fresh PSCM limit >=2,
or a target already limited by the existing inverse acceleration allowance.
Existing disengagement, fault and explicit override gates still govern the
whole command. C2/C3 stay zero. No new integrator, retained maneuver state or
encoder search is added. The observer continues consuming actual packed commands.

The extra goes to zero when the filtered target stops growing. **This does not
clear the consequences of earlier commands:** the observer and encoder retain
their state, so later requests can change. Normal path following and physical
wheel release are not guaranteed unchanged. Delayed unwind is an accepted trial
tradeoff, not claimed fixed.

## Why this strength

Nine recorded routes were compared: 183, 185, 17c, 166, 16a, 172, 177, 175 and
17a. Each run used 556,776 input rows, actual adapter/packer calls, frozen model
and vehicle measurements, and full available histories. Compare against the
unchanged coordinated controller at `d203a109a`.

| Extra budget | Weak right 2: max total C0/C1 difference | Changed ordinary samples |
|---|---|---|
| 0.15 m / 0.01 rad | 0.26 m / 0.0185 rad | 2,923 / 236,385 (1.24%) |
| 0.30 m / 0.02 rad | 0.41 m / 0.0285 rad | 2,071 / 236,385 (0.88%) |
| **0.60 m / 0.04 rad** | **0.71 m / 0.0485 rad** | **1,493 / 236,385 (0.63%)** |

Total differences can exceed the immediate additive budget because earlier
commands alter subsequent encoder decisions. The ordinary screen requires
requests within ±30 degrees, engaged control, no touch/limitReached, and two
seconds of continuously qualifying data on each side. It measures command
differences, not lane error. Lower counts are not proof of better centering.

The 4× trial changes 76/334 and 104/326 samples in the two weak-right windows.
Their peak absolute fields stay below 3.10 m C0 and 0.225 rad C1. Roundabout
windows reach maximum differences of 0.63–0.66 m / 0.0425–0.0445 rad.

Nine of ten marked wobble windows match exactly. In route172's bookmark, 98/396
samples change, up to 0.21 m C0 / 0.007 rad C1. Command total variation is slightly
lower (C0 5.95→5.85 m; C1 0.3605→0.3545 rad); maximum individual steps are unchanged.
This does not prove that the real wobble improves or remains equal.

Across all nine routes the trial touches a DBC field bound on 29 samples versus
12 for baseline, including a short interval on175. It never exceeds those
bounds. It changes the marked good unwind's channel split substantially:
maximum C0/C1 differences of 2.16 m / 0.058 rad. That is not a measured wheel
release delay. Larger requests reaching CAN do not establish more wheel motion.

## Verification and interpretation

Tests exercise the real Ford adapter and packer: startup/fallback, default-off
parameter, both turn signs, no extra for small requests/errors, DBC clipping,
target limits, overrides, fault gates, and clearing the added term while retaining
the observer's real history. Full-route production verification compares both
settings directly against the frozen 4× research output, including state and
transmitted commands. UI source and generated schema are checked together.

The deployment gate additionally suppresses the term when the inverse target
is acceleration-limited; no active extra in these nine research tapes coincided
with that condition. This does not introduce a new acceleration allowance.

`Ford joint path tracking` diagnostics identify the enabled experiment as
`ford-joint-turn-entry-v1`, with `turn_entry_enabled`, `turn_entry_weight`,
`turn_entry_c0`, `turn_entry_c1`, `base_wire_command` and actual `wire_sent`.
The existing `predicted_curvature` field describes the encoder prediction before
the added term; `filtered_curvature` is the observer advanced from actual sends.
Logging cadence is unchanged.

These are offline numerical checks, not a closed-loop steering validation.
166/16a retain raw-yaw sensitivity; 183 has incomplete earlier history; 185 has
log gaps. The recovered older firmware model is not proven identical to the
live truck. The physical question for this trial is whether the stronger entry
requests move the wheel farther/faster without unacceptable normal-driving
changes. Neither turn completion nor preserved driving feel is established.
