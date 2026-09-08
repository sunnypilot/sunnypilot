# Ford model-point candidate v7

## Decision

Use the model's own position and orientation at one shared path point. This
implements the request to follow model geometry through C0/C1, with C2/C3 zero,
without a fitted PSCM plant, new strength gain, yaw integral, or release mode.

Let `s(t)` be cumulative planar arc distance along model position. Choose:

```
station = min(path_end, max(7 metres, s(1 second)))
C0_target = model.position.y at station
C1_target = unwrapped model.orientation.z at station
C2 = C3 = 0
```

Use the published model timestamps, not `speed × 1 second`, so the point also
follows the model's predicted acceleration/braking. The seven-metre floor keeps
the existing low-speed preview distance; it can select a time beyond one second.
If the entire path is shorter, both fields hold the same endpoint. Interpolation
uses the same arc segment and weights for position and heading.

One second keeps C1 near the old one-second heading scale in ordinary driving.
Using that same point for C0 represents a meaningful change in faster bends.
This is a chosen local approximation; Ford's expected reference point and
preview are unknown. Matching metres/radians does not prove PSCM equivalence.

The former 150 ms vehicle-pose forecast is removed. C1 no longer uses
`max(7, speed) × selected desiredCurvature`. Measured yaw remains an input-health
check only; calibrated yaw has no command role. Freshness, independent slew,
packing, the shared startup toggle, 20 Hz sends, and Panda safety remain.
The upstream scalar curvature is still logged but does not limit this geometry;
C0/C1 retain their existing amplitude and slew limits. The scalar-only lateral
maneuver test reference is explicitly unsupported and disengages this candidate.

## Offline evidence

The broad run passed **572 tests and 9,146 subtests**, with 178 inherited safety
cases skipped as inapplicable. Tests of the removed yaw forecast were retired;
new tests cover actual model clocks, a nonconstant-speed trajectory, shared-point
sampling, the distance floor, endpoint holding, heading unwrap, source selection,
invalid geometry, reset, independent slew, and actual CAN delivery.

The stress run covers 200,000 random cycles plus mirrored turns, 18,138 field
boundary cases, and 218,138 Float32/CAN round trips. An independent scalar oracle
checks analytic model points and slew. No vehicle plant is simulated.

Five recorded routes (a5, a2, a0, 9b, 9e) supply **379,718 controller cycles** and
**76,294 model frames**. Original rlog hashes and position/orientation timestamps
were checked. An independently implemented segment-weight oracle matches every
sampled target and eligible slew state. Every cycle passed packing/bound checks;
all **75,947** scheduled 20 Hz requests passed the actual unchanged Panda TX hook.
This is TX acceptance with controlled eligibility, not a full Panda RX watchdog
or vehicle-response replay. The [validation manifest](ford_model_points_validation.json)
binds the results to their source and input hashes.

On a5's 61.24-second driver-clean ordinary-bend cohort, mean absolute C0 changes
from 0.075 m recorded to 0.167 m replayed; C1 changes from 0.02287 to 0.02224 rad.
Neither field target clips in that cohort. These are command differences, not
predicted changes in steering strength or tracking error.

| a5 time | Recorded C0 / C1 | Candidate C0 / C1 | Selected station / time |
| --- | --- | --- | --- |
| 107.995 s, ordinary bend | +0.20 m / +0.068 rad | +0.55 m / +0.0685 rad | 13.71 m / 1.00 s |
| 390.681 s, sustained bend | −0.52 m / −0.1235 rad | −0.75 m / −0.1215 rad | 9.37 m / 1.00 s |
| 374.889 s, tight turn | −3.76 m / −0.50 rad | −3.46 m / −0.50 rad | 7.00 m / 1.49 s |
| 17.607 s, exit overshoot | −0.01 m / −0.015 rad | −0.05 m / −0.012 rad | 7.00 m / 1.85 s |

The exit example retains more C0 into the turn than v6; physical unwind behavior
must be evaluated. Tight-turn C1 clipping remains (14.92 eligible seconds on a5).
No root cause or physical fix is proven by frozen inputs. The latest a5 road
logs used 100 Hz sends, whereas the immediately preceding code revision already
changed to 20 Hz; a comparison against that drive also includes the cadence change.

`calibration_approved=false` remains. Installation instructions and restore
behavior are in the [drive-test guide](ford_model_action_drive_test.md).
