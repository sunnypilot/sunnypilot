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
existing downstream curvature and Panda checks are changed by this experiment.
No new per-vehicle tuning table or online learner is added.

## One request, then allocation

The controller keeps three decisions separate:

1. **Hold request.** Use a single 7 m remaining-model preview for offset and
   heading. Advance the reference by the existing 0.1 s nominal prediction
   interval. Keep a bounded gentle C2 contribution, and add only the model pose
   beyond the existing 0.006 /m gentle envelope. That excess grows linearly for
   a circular-path fixture; it is not the old blend share multiplied by pose.
2. **Correction.** Compare model pose at the prediction interval with a
   constant-curvature projection from measured steering-derived curvature.
   Express offset/heading error in the predicted vehicle frame. Apply its
   normalized contribution **after** hold-request saturation so a large raw
   preview cannot swallow an unwind correction. At the modeled arc, this
   correction is zero while the holding request remains. No noisy measured
   curvature derivative or integral accumulation is used. If the model path
   straightens while measured curvature is still large, recovery keeps the
   opposing pose correction active until actual motion returns to the gentle
   envelope; the reference alone cannot switch that correction off.
3. **Allocation.** Independently supply that total with reachable C0/C1/C2
   states. Channel preference cannot change the requested total. C2 is preferred
   for settled gentle driving, reduced across the existing 0.006–0.012 /m band,
   and requested zero for large maneuvers or a still-large measured turn.
   Unreachable fast demand is reported,
   not used as permission to refill C2. C3 remains zero.

The allocator scores candidate packets against every nominal 4 ms tick in the
next 100 Hz period, not just its endpoint. It considers neighboring wire
quantizations. First minimize total-contribution error beyond half-LSB encoding
uncertainty, then favor the C2 endpoint and coordinated C0/C1 preference. Avoid
unnecessary latent coefficient accumulation beyond nominal contribution caps.

## Explicit assumptions and limitations

The contribution/slew model comes from decoded **ML3V-14D003-BD**, not verified
Lightning RL38-14D003-AA or logged Raptor BC firmware. Factoring out its common
speed gain leaves:

- `q0 = clip(0.5*C0_state, ±0.5)`
- `q1 = clip(10*C1_state, ±0.349609375)`
- `q2 = clip(0.30078125*vRaw²*C2_state, ±0.5)`

These are nominal internal contributions, **not steering angle, torque, yaw, or
curvature**. They are fixed response assumptions, not a newly identified plant.
The hold request is bounded to nominal fast-channel authority before adding
bounded feedback. This sacrifices excess raw coefficient windup under the BD
hypothesis; if that hypothesis is wrong, actual maneuver authority may be weaker.

Primary states use the decoded 4 ms slew steps; inactive states drain at their
separate finite rates. Startup/gaps start with uncertainty intervals rather than
assumed zero. Before nominal history initializes, the prior default encoder is
used with output continuity. Missing/invalid model or motion input ramps the
requested path toward zero through existing limits rather than inventing error
correction. Packet prediction includes Float32 serialization, the existing
downstream C2 rate limiter, and sign-reversed DBC rounding. It does not have
PSCM execution acknowledgments or a verified delivery
delay model. Unmodeled firmware shaping remains unmodeled.

The 0.1 s prediction is inherited as a short nominal horizon; it is **not a
verified learned lateral delay**. Wheel-derived curvature is not a complete
vehicle-motion measurement. This is not a claim of universal Ford stability or
servo-like tracking. Unchanged safety checks do not by themselves certify the
new control law. Offline replay holds actual motion/model replanning fixed and
cannot predict changed intervention rates or prove a physical steering cure.

## Diagnostics and validation

`Ford path controller selected` records the class at startup. When selected,
`Ford shared path experiment` records the nominal hypothesis, status, consumed
model timestamp, holding request, feedback, total, pose errors, state intervals,
predicted contribution error and shortfall at 5 Hz. Existing rlogs retain the
actual outgoing path/CAN commands at their original rate. `active` means the
experimental allocator is selected with initialized nominal history, not that
the model has been validated against the PSCM.

Unit tests cover hold-versus-correction behavior, both transfer directions,
unknown history, inactive drain, intermediate ticks, quantization, saturation,
S-shaped preferences, invalid input, timing gaps, unchanged downstream limits,
and default-off selection. Replay includes interventions; it is a command audit,
not a new simulated vehicle trajectory. Hardware validation must separately
assess authority, oscillation, tracking, overrides, and availability in a
controlled test environment before treating this as a driving improvement.
