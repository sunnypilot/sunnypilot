# Ford C2-free path tracking

This replaces the weak Virtual Angle controller in `7d558c065`. C0/C1 are
spatial path requests to the PSCM's own controller. They are not mapped to
wheel angle, torque, or acceleration through fitted channel gains. C2 and C3
are always zero while this experiment is selected.

## Why the previous controller failed

The supplied route7a ran `7d558c065` with the experimental controller selected.
In its first two turns, before the steeringPressed flag, the median measured
to requested curvature ratios were 0.120 and 0.263. The first requested wheel
angle rose from 41.1 to 79.8 degrees while measured wheel angle rose from 1.8
to 19.8 degrees. Median absolute C1 was only 0.0025 rad in that window, versus
roughly 0.08–0.25 rad in earlier large-maneuver examples.

This was not a stall-latch or CAN-packing failure. There were zero logged
stall events. Both weak-turn windows had continuous mode-2 requests, EPS
InProgress, full reported capability, no reported limit and no denial. The
wire coefficients matched the published requests. Reported full capability
does not establish unlimited physical steering authority.

The v1 acceleration conversion discarded useful path information: C0 did not
represent lane-centering displacement, and C1 was reduced to a small curvature
error correction. Making replayed commands quiet did not establish a useful
controller. The replacement explicitly retains centering and large-turn demand.

## Reference and command construction

`openpilot/selfdrive/controls/lib/ford_virtual_angle.py` retains its historical
filename, class and parameter key for compatibility. Its reference is now the
**model's full spatial path**, as in the default Ford path allocator. The
existing action/maneuver-plan curvature remains available in diagnostics but
is not the command reference. Consequently this is not an angle servo and
must not be assessed as exact tracking of the logged planned wheel angle.

The retained path is moved into the current vehicle frame on each control tick
using traveled distance and measured CAN yaw rate. New model geometry is
aligned to that same frame and arc station before its difference from the
retained path is filtered. This avoids adding the model-filter delay to the
vehicle-frame motion correction. Publication age is compensated with the
current speed and yaw rate; this is a planar motion approximation, not a
model of the PSCM or a reconstruction of camera latency.

A short predicted ego pose accounts for the response interval. Relative to
that pose, C0 is the lateral error at a 7 m preview and C1 is the full path
heading at a speed-dependent preview. The model's own initial pose is not
subtracted: a straight path displaced sideways must continue to request C0
even when desired curvature and heading are zero. Likewise, a curved path
continues to request substantial C0/C1 when measured curvature catches up.

| Parameter | Value |
|---|---:|
| Model-innovation filter time constant | 0.30 s |
| C0 spatial preview | 7 m |
| C1 spatial preview | max(7 m, speed × 1.0 s) |
| Response interval | CarParams.steerActuatorDelay; 0.20 s in these routes |
| Host C0 / C1 slew limits | 4 m/s / 0.5 rad/s |
| C0 / C1 request bounds | ±5.11 m / ±0.5 rad |

Preview distances are limited to available path coverage. Heading outside the
C1 bound contributes its remaining lateral displacement to C0, subject to the
C0 bound. C0/C1 share one slew factor so their transition is coordinated.
Fractional wire-resolution increments accumulate internally; published values
mirror the actual Float32 and sign-reversed Ford CAN packing. These are
reference-shaping parameters, not identified PSCM gains or stability margins.

There is no external wheel-error integrator, learned channel gain, or stall
latch. While lateral control remains authorized, driver input leaves the path
request present, as in the default allocator; the PSCM handles its existing
driver arbitration. The diagnostic driver_override label records the flag,
not a promise that lateral mode has been disabled.

Invalid services or geometry, inputs older than 150 ms, backward timestamps,
control intervals outside 2–100 ms, speed outside 0.3–55 m/s, or yaw-rate
magnitude above 3 rad/s clear state and invalidate the request. controlsd then
clears latActive, producing inactive Ford lateral mode. Reengagement starts
from zero slew state.

## Selection and rollback

Vehicle → Ford → **C2-Free Path Tracking (Experimental)** uses the existing
`FordVirtualAngleController` setting. An already-enabled setting selects this
replacement after updating and restarting controlsd; it has not been silently
reset. Changes to the toggle require an offroad-to-onroad cycle. New settings
remain default off.

Selection requires CAN FD, `FORD_F_150_LIGHTNING_MK1`, and EPS firmware
`RL38-14D003-AA`. It takes priority over PSCM Coefficient Observer on that
combination. Turning it off and cycling offroad/onroad restores the previous
controller selection. The obsolete `FordSharedPathController` switch remains
removed. No live device setting is changed by this commit.

## Verification and remaining uncertainty

The committed seven-episode fixture contains 3,897 control samples from
routes77, 78 and 7a, including the large left/right maneuvers, oscillation and
both weak turns. It records geometry, control signals and source hashes,
without GPS. Tests check C0 centering with zero curvature/heading, sustained
large-turn requests, motion-frame alignment, attenuation of model innovations,
fault resets, command bounds, real CAN packing, controlsd wiring, selection
and settings schema. Existing Ford path-controller tests also run.

Full-route command replay covers 138,287 control cycles from all 24 supplied
segments. There are no invalid-input or timing resets during recorded moving,
active cycles. Median absolute requests in the selected windows are:

| Recorded window | Recorded C0 / C1 | Replacement C0 / C1 |
|---|---:|---:|
| Route77 large left, 812.1–814.0 s | 0.99 m / 0.1723 rad | 1.57 m / 0.2435 rad |
| Route77 large right, 869.5–871.0 s | 0.99 m / 0.1437 rad | 1.45 m / 0.2240 rad |
| Route77 very large left, 882.9–883.32 s | 1.73 m / 0.2542 rad | 2.11 m / 0.2455 rad |
| Route77 right plateau, 967.2–968.93 s | 0.73 m / 0.0816 rad | 0.96 m / 0.1875 rad |
| Route7a first weak turn, 93.5–95.08 s | 0.15 m / 0.0025 rad | 1.27 m / 0.2400 rad |
| Route7a second weak turn, 122.5–125.2 s | 0.44 m / 0.0070 rad | 0.26 m / 0.0495 rad |

Some large-maneuver windows include driver input or follow it. These are
command-envelope comparisons, not identified actuator responses. The two
weak-turn windows precede their steeringPressed flags, which also cannot rule
out subthreshold driver torque.

**This version has not been validated on the vehicle.** Frozen-motion replay
cannot establish stability, physical centering or improved wheel tracking.
The route78 replay still contains oscillatory countercommands in response to
recorded oscillatory motion; suppressing every such command is not a valid
success criterion. The change filters model innovations while preserving
steady path demand, but the resulting closed-loop PSCM behavior remains to
be measured.

Startup logs retain the controller class name. The 5 Hz event
`Ford C2-free path tracking` identifies hypothesis `spatial-path-v2` and records
input times/ages, action/measured curvature, CAN yaw, target C0/C1, preview
horizons, filter/response times, slew factor and actual commands.

Reproduce focused checks from the repository environment:

```sh
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford_path_reference.py openpilot/selfdrive/controls/tests/test_ford_virtual_angle.py openpilot/selfdrive/controls/tests/test_ford_controlsd_logging.py openpilot/selfdrive/controls/tests/test_ford_path.py openpilot/sunnypilot/sunnylink/tests/test_settings_schema.py
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

The local analysis directory contains `replay_path_tracking.py` and the
route-specific `path_tracking_replay.json` outputs. Historical v1 recordings
and failure witnesses remain unchanged: code edits cannot repair an already
recorded drive.
