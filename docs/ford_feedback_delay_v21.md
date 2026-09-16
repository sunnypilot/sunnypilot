# Ford feedback timing follows comma's request-history pattern

The base C0/C1 mapping continues to use the latest selected curvature. C0 P,
C1 P and C1 I now calculate error from an earlier selected curvature, using
the same one-second request buffer and frame-index expression as comma's torque
controller. The buffer advances at the 100 Hz controls rate, including while
disengaged. The outgoing base request is never buffered for later transmission.

`controlsd` passes the same `lat_delay` value it passes to the upstream lateral
controller: `lateralDelay.lateralDelay + LAT_SMOOTH_SECONDS`. The existing extra
Ford model preview remains model-side; this change does not add it to feedback
delay or infer hardware delay from a turn's angle crossing. In the four replayed
routes the published delay was 0.1689463705 s and `LAT_SMOOTH_SECONDS` was zero.
Upstream's integer indexing selects the request 16 control cycles earlier,
nominally 0.16 s. The maximum lookback is 99 cycles, nominally 0.99 s.

The history is in curvature units because that is this controller's feedback
quantity. This adopts upstream's timing pattern, not its torque conversion,
acceleration gain schedule, friction/jerk feedforward or low-speed integral
freeze. Ford gains, formulas, anti-windup, integration cadence, field bounds,
upstream curvature limiting and driver/PSCM arbitration remain unchanged.
Action C0 P remains 1.0; direct-path C0 P remains 0.5; C1 P=0.75 and I=1.0.
Both Ford reference modes use the new timing.

The history starts at zero, like upstream. Ordinary disengagement clears P/I
while continuing to record requests. Existing invalid-input, timing and path
resets also clear request history, preventing invalid retained references from
surviving recovery. A nonfinite delay rejects the active command; finite delay
values use upstream's bounded frame selection. An explicit zero delay recovers
the previous command law exactly. Existing offline feedback-reference overrides
remain available; production supplies delay rather than an override.

Diagnostics identify `v21-delayed-feedback` and report the requested delay,
nominal frame delay, delayed feedback curvature/error and latest requested
curvature separately. The reported frame delay is not a measured physical delay.

## Verification and limitations

The delay-tracking regression failed against the old feedback behavior: a wheel
following a request with the configured delay still received correction. It
passes with delayed feedback through entry, reversal and release, in both turn
directions and both reference modes. A separate test executes the actual
upstream torque controller's buffer-selection expressions as an oracle.

Integration tests execute controlsd's actual delay wiring, source selection,
limiter, adapter and Float32 publication through the Ford CAN sender. A
delay-matched wheel trace generates zero P/I while the current base commands
reach CAN immediately. Persistent error still integrates; repeated measurements
do not integrate twice; driver and fresh PSCM override still clear correction
immediately. Exact suite counts are in the validation JSON.

Four native-time route replays cover 583,599 control cycles and 58,362 CAN
pack/decode checks. The baseline is the filtered-driver controller at
`baeabfaa807c7a07baf183968e570f2c1d3fd665`. Baseline commands match the archived
v20 replay exactly on all four routes. A third controller with zero delay
matches that baseline's commands and integral on every cycle. With delay,
command validity, base heading/overflow and feedback arbitration remain equal.
All commands remain bounded with C2=C3=0.

| Route | Low-speed C0 changes >0.25 m, v20 → v21 | Low-speed C1 changes >0.05 rad, v20 → v21 | C1 at field bound, v20 → v21 |
| --- | --- | --- | --- |
| 162 | 70 → 68 | 50 → 44 | 1.06 → 0.92 s |
| 157 | 137 → 110 | 59 → 51 | 6.52 → 5.94 s |
| 151 | 77 → 65 | 42 → 36 | 4.04 → 3.89 s |
| 149 | 197 → 159 | 111 → 95 | 16.08 → 13.23 s |

Low speed means below 15 mph; these counts include valid driver-interaction
periods and are command-continuity measurements, not autonomous tracking scores.
Neither baseline nor candidate was driven in these recordings; both command
streams use the same recorded requests and vehicle motion.

The change reduces transient correction. At route-162 time 302.649 s, requesting
141.4 degrees with the wheel at 87.3 degrees, replay C0 changes from -2.19 to
-1.73 m and C1 from -0.3695 to -0.3135 rad. At 307.502 s, after driver input,
opposite-direction release C0 falls from +1.52 to +1.04 m and C1 from +0.0655
to +0.0355 rad. The base request is unchanged in each example.

This can mean less correction during both entry and unwind. Fewer large command
steps do not prove reduced physical oscillation, maintained turn authority or
better release. These are frozen-motion replays, not a validated PSCM simulator.
The supplied delay has not been identified specifically for the combined C0/C1
response. The next physical evaluation must distinguish these effects; this is
not a demonstrated death-wobble fix.

Reproduce with the project's Python environment and built dependencies:

```sh
PYTHONPATH=.:opendbc_repo:.cache/ford_geometry_deps python \
  tools/ford_pscm_lab/filtered_driver_replay.py \
  --source .cache/ford_route162/full \
  --delay-intake .cache/ford_route162/intake.npz \
  --baseline baeabfaa807c7a07baf183968e570f2c1d3fd665 \
  --output .cache/ford_feedback_delay_v21/162
```

Pull and restart the software while offroad. The existing master toggle still
selects upstream Ford control when disabled. For the current action trial,
leave Model Geometry Reference and C0 one-second distance disabled.
