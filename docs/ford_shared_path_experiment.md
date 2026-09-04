# Ford shared path controller experiment

Default off. This is an opt-in **live steering** experiment, not shadow mode and
not a demonstrated hunting/overshoot fix. It has not been validated on a vehicle.

## Selection and recovery

Sunnylink → Vehicle → Ford → **Shared Path Controller (Experimental)**.
The persistent boolean is `FordSharedPathController`. Change it offroad; the
selection is read when controlsd starts on the next offroad-to-onroad cycle.
It takes precedence over the older `FordPscmObserver` option on Ford CAN FD only.
Turning it off restores the prior selection, including the older observer if
that option was already enabled. No mid-drive controller switching is added.

Neither the CAN frequency (100 Hz for LMC2), driver/fault enablement, nor the
existing Panda checks are changed by this experiment. No per-vehicle tuning
table, online learner, host-side slew, or coefficient handoff is added.

## C2-free request

The controller samples one model pose at a firmware-derived temporal horizon:

```text
H  = sqrt(0.30078125 / 0.25) = 1.096870548 seconds
C0 = model lateral displacement at H
C1 = wrap(model heading change at H - measured curvature * model arc to H)
C2 = 0
C3 = 0
```

The model endpoint is translated and rotated from the model's first pose before
encoding. `position.y[0]` is not used because the rolling model begins at ego.
C0 carries the ordinary arc and centering request. C1 carries only the heading
that the current measured curvature is not predicted to cover: it adds when the
vehicle is behind, approaches zero on an aligned arc, and reverses when measured
curvature is ahead of the model.

The horizon comes from the decoded ML3V-14D003-BD normalized contributions:

```text
q0 = clip(0.5*C0_state, ±0.5)
q2 = clip(0.30078125*v²*C2_state, ±0.5)
```

For a constant-curvature path, `y(H) ≈ 0.5*curvature*(vH)²`. Equating its C0
contribution with C2 gives the horizon above. This is a field conversion from
one decoded firmware, not a fitted Lightning response gain.

C0/C1 retain the full symmetric DBC-safe ranges (±5.11 m and ±0.5 rad). The
smaller contribution plateaus decoded from Raptor BD are not treated as proven
Lightning command limits; earlier physical testing found that doing so weakened
turn authority. The downstream CAN packer still quantizes the fields, and the
PSCM still owns any internal coefficient slew.

## Explicit limitations

The coefficient relationship has not been confirmed in Lightning RL38 firmware
or across Ford models. Model output updates at approximately 20 Hz even though
the latest command is repeated at 100 Hz. Wheel-derived curvature is not a
complete vehicle-motion measurement, and its multiplication by the model arc
can reintroduce a heading correction when model and measured motion are not
latency-aligned. Offline route analysis found no systematic high-speed early
entry and retained the large fast request at selected failed turns, but one
recorded hunting window became better and another became worse.

Missing or invalid model input sends a valid zero-coefficient path while lateral
control remains active; it never falls back to a C2-producing controller. On
inactive lateral control the path is invalid and the existing car controller
sends zero coefficients. This experiment cannot prove physical tracking from
offline replay because the PSCM's inner controller and vehicle response remain
black boxes.

## Diagnostics and validation

`Ford path controller selected` records the class at startup. When selected,
`Ford shared path experiment` records the hypothesis, status, consumed model
timestamp, temporal horizon, model offset/heading, predicted heading, heading
residual, model arc, and output fields at 5 Hz. Existing rlogs retain the actual
outgoing path/CAN commands at their original rate.

Unit tests cover temporal interpolation, coordinate transforms, constant-curve
equivalence, under/aligned/overtracking C1 behavior, direct sign reversal,
C2/C3 exclusion, invalid input, DBC bounds, logging, and default-off selection.
Hardware validation must separately assess turn authority, oscillation,
tracking, overrides, and availability in a controlled test environment.
