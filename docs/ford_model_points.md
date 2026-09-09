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

The broad run passed **585 tests and 9,146 subtests**, with 178 inherited safety
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

## Unwind comparison

The follow-up a5 comparison includes all seven clearly separated tight turns and
four completed ordinary bends identified in the full-route command plot. A fifth
bend runs into the next turn and is excluded from the summary. All scored windows
remain continuously paired-active, without control gaps over 30 ms. The tight
turns contain driver input; this compares instructions on frozen inputs, not
unassisted tracking or hypothetical truck motion.

Measure the first time each instruction falls below the same fixed level on
exit and stays below for 100 ms. All seven tight turns exceed these levels:

| Instruction | Candidate minus recorded clearance time |
| --- | --- |
| C0 below 0.5 m into the turn | 0.10 s later median; five later by 0.01–0.46 s, two unchanged |
| C1 below 0.1 rad into the turn | 0.10 s earlier median; all seven 0.04–0.17 s earlier |

These are control-publication times. Actual packet timing also includes the
20 Hz send phase; shifts of only a few tens of milliseconds should not be
interpreted as equally precise changes at the PSCM.

The report also compares half of each command's own peak: C1 reaches that level
0.25 s earlier in the median tight turn and C0 0.12 s later. Those normalized
crossings have different absolute thresholds when amplitudes differ. Comparing
half the smaller peak at an identical level instead gives C0 earlier in one
turn and later in six. No single threshold captures the whole release waveform.

For the ordinary bend around 108 s, C0 reaches half of its own peak 0.20 s later;
C1 reaches half-peak 0.24 s earlier. The larger C0 takes 0.95 s longer to fall
below the same 0.05 m threshold. On the last tight turn, C0 clears 0.05 m 0.23 s
later. Near-zero thresholds are sensitive to small residual model offsets; the
complete report retains 90%, 50%, 10%, common-level and near-zero crossings
rather than treating any one threshold as a physical success criterion.

The plotted candidate target and command largely coincide during these exits:
the longer C0 tail comes from the selected model point continuing to ask for
lateral offset, rather than a retained yaw correction. C1 can release sooner
because it now follows model orientation directly. These results do not show
that every command unwinds earlier, or that the vehicle will unwind earlier.

Ten additional end-to-end sender cases cover both signs and all five CAN send
phases. After a full-cap turn, a zero model target starts reducing both states on
the first control update and appears on the next scheduled CAN message, 0–40 ms
later at nominal 100 Hz calculation. There is no additional release hold. The
unchanged slew itself takes 1.28 s of updates to clear 5.11 m C0 and 1.00 s to
clear 0.5 rad C1, plus scheduling to transmit zero. These are software timing
checks, not measured PSCM dynamics. The [unwind report](ford_model_points_unwind.json)
records the episode timings, method and source hashes.

Older offline utilities now fail explicitly when their input lacks original
model clocks or their historical unchanged-C1 comparison cannot support v7.
This prevents missing model inputs from producing an all-invalid apparent match.

`calibration_approved=false` remains. Installation instructions and restore
behavior are in the [drive-test guide](ford_model_action_drive_test.md).
