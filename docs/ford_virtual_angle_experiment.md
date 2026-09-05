# Ford C2-free path tracking

Hypothesis `curvature-c0-v3` uses the planner's selected desired curvature for
C0 centering and turn demand, while retaining v2's full model-path heading for
C1. C2 and C3 remain zero. The historical `ford_virtual_angle.py` filename,
controller class and setting key remain for compatibility; this is not an
angle servo or an identified C0/C1-to-wheel conversion.

## Evidence and reason for the change

Route7a ran the weak v1 controller in `7d558c065` with the experiment selected.
Before the steeringPressed flag in its first two turns, median measured to
requested curvature ratios were 0.120 and 0.263. Median absolute C1 in the
first window was only 0.0025 rad, versus roughly 0.08–0.25 rad in earlier
large-maneuver examples. These were continuous mode-2 requests with full
reported EPS capability, no reported limit or denial, matching wire commands
and zero stall events. Full reported capability does not establish unlimited
physical steering authority, and an unset steeringPressed flag does not rule
out subthreshold driver torque.

The v2 controller in `10e354d66` restored spatial turn demand, but its C0 came
from lateral displacement in a short model-path preview. A real model path
can start at the truck and gradually move toward center. That representation
may contain little short-preview displacement even while the planner requests
a correction. A synthetic path translated sideways did not reproduce this
case, so that original centering test was insufficient.

The supplied route7c was driven with the experiment **off** and is a default
controller baseline. The user's subsequent enabled-v2 report describes better
turns but drifting without centering; enabled logs are still pending. This
supports investigating the reference choice, but does not identify a measured
PSCM failure mechanism or validate this replacement on the vehicle.

## C0: planner curvature expressed as lateral demand

controlsd supplies its existing bounded `desired_curvature`: the
`lateralManeuverPlan` request when that service is valid, otherwise the
`modelV2.action` request, after the existing curvature limiter. This action
already includes the planner's centering intent. v3 uses it directly rather
than inferring centering from the near model path or building another
lane-centering loop. The selected action already receives the upstream delay
treatment; C0 does not add another response advance. C1 retains its existing
model-geometry response alignment.

The controller constructs C0 in its existing command coordinates as:

```text
L = max(8 m, speed × 1.0 s)
C0_target = clip(0.5 × desired_curvature × L², -5.11 m, +5.11 m)
```

This is a small-angle arc-displacement construction, not a prediction of
wheel response or a measurement of the truck's actual lane displacement.
For example, desired curvature 0.02/m produces 0.64 m at the 8 m floor and
1.00 m at 10 m. Curvature 0.04/m produces 1.28 m and 2.00 m respectively.
The spatial floor prevents the preview from collapsing during slow maneuvers;
it cannot restore turn intent absent from the desired-curvature reference.
The formula is bounded rather than extrapolated into an unlimited request.

The input is **absolute desired curvature**, not desired minus measured
curvature. Matching the requested curvature therefore does not erase the
turn command. This replaces v2's C0; it is not added to the previous lateral
displacement calculation, and C1 overflow is not transferred into C0.

## C1: retain full model-path heading

C1 continues to use the full model heading at `max(7 m, speed × 1.0 s)`
beyond a short predicted response interval, limited by available path
coverage. The model's heading is expressed relative to the predicted ego
heading, then bounded to ±0.5 rad. It is not reduced to a small curvature
error term when the truck catches up with the turn.

The retained model geometry is moved into the current vehicle frame every
control cycle using traveled distance and measured CAN yaw rate. New model
geometry is aligned to the same frame and arc station before its difference
from the retained path is filtered. Measured ego motion is accounted for
immediately; only model innovation is filtered. Publication age is compensated
with the current speed and yaw rate. This is a planar motion approximation,
not a PSCM model or reconstruction of camera latency.

| Parameter | Value |
|---|---:|
| C0 preview | max(8 m, speed × 1.0 s) |
| C1 preview | max(7 m, speed × 1.0 s), limited by model coverage |
| Model-innovation filter time constant for C1 | 0.30 s |
| C1 response interval | CarParams.steerActuatorDelay; 0.20 s in these routes |
| Independent host C0 / C1 slew limits | 4 m/s / 0.5 rad/s |
| C0 / C1 request bounds | ±5.11 m / ±0.5 rad |

Each channel has its own slew limit, so a heading transition does not consume
C0's centering rate allowance. Fractional wire-resolution increments accumulate
internally; published values mirror the Float32 and sign-reversed Ford CAN
packing. C0 does not pass through the model-innovation filter.

Preview floors and time horizons are **effective gains**: they change command
size and aggressiveness. Filtering and slew limits also change the response.
This design minimizes separate tuning mechanisms, but it is not gain-free.
There is no fitted EPS gain, external wheel-error PID, learned channel gain,
integrator or stall latch. Geometry alone does not establish adequate PSCM
authority or stability, particularly when C0 and C1 come from different
planner representations.

## Input validity, selection and rollback

C0 requires a fresh timestamp from the selected action service; C1 separately
requires a fresh valid model. controlsd checks both services plus carState,
vehicleParameters and CAN validity. Model, action and measurement age must
each be within the controller's 150 ms freshness window. The selected action
source can switch between model and maneuver plan using the same validity
choice as the existing desired-curvature calculation.

Invalid services or geometry, nonfinite inputs, stale inputs, backward model
or measurement timestamps, control intervals outside 2–100 ms, speed outside
0.3–55 m/s, or yaw-rate magnitude above 3 rad/s invalidate the request and
clear state. controlsd then clears latActive, producing inactive Ford lateral
mode. Reengagement starts from zero slew state.

While lateral control remains authorized, driver input leaves the path
request present, as in the default allocator; the PSCM retains its existing
driver arbitration. The diagnostic driver_override label records the flag,
not a promise that lateral mode has been disabled.

Vehicle → Ford → **C2-Free Path Tracking (Experimental)** uses the existing
`FordVirtualAngleController` setting. An already-enabled setting selects the
replacement after updating and restarting controlsd. New settings remain
default off. Toggle changes require an offroad-to-onroad cycle.

Selection remains limited to CAN FD, `FORD_F_150_LIGHTNING_MK1`, and EPS
firmware `RL38-14D003-AA`. It takes priority over PSCM Coefficient Observer on
that combination. Turning it off and cycling offroad/onroad restores the
previous controller selection. The obsolete `FordSharedPathController`
switch remains removed. No live device setting is changed by this commit.

## Verification and remaining uncertainty

Regression checks cover action-driven C0 even when the near model path has
little centering displacement, command growth for slow turns, sustained
steady-turn demand, retained C1 heading, motion-frame alignment, filtering,
independent slew limits, bounds, fault resets and actual CAN packing. The
controlsd tests exercise both action-source choices and independently stale
or invalid model/action services. Selection, logging and settings-schema
checks remain included.

Recorded-route fixtures include earlier large left/right maneuvers, the
oscillating experiment and v1's weak turns. Replaying these frozen inputs
checks the commands the new code would request. It does **not** replay the
vehicle's response to those changed commands. Historical v2 command-envelope
tables and replay outputs are evidence for that version only, not new v3
vehicle validation. Driver intervention also limits physical interpretation
of several large-maneuver windows.

Route7c exposes a material disagreement between action curvature and the
far model geometry during a large left turn. These active, unpressed command
windows use signed median values:

| Route7c window | Speed range | Desired curvature | Recorded C0 / C1 | v3 replay C0 / C1 |
|---|---:|---:|---:|---:|
| 482–485 s, initial near-stop turn | 0.485–3.439 m/s | +0.00174/m | −4.123 m / −0.5 rad | +0.06 m / −0.5 rad |
| 489–492 s, later in the turn | 2.213–4.777 m/s | −0.05821/m | −3.222 m / −0.5 rad | −1.86 m / −0.5 rad |

The raw model action matches desired curvature in this case. The reference
itself therefore disagrees with the far-path turn geometry; the curvature
limiter and preview-distance collapse do not explain it. C1 retains the
large turn heading, but the adequacy of the combined request is unknown.
Earlier route77 large-maneuver command checks pass; that does not establish
that v3 preserves every large maneuver, particularly this initial turn.

**v3 has not been validated on the vehicle.** Neither geometric examples nor
command replay prove centering, damping, physical steering authority or
closed-loop stability. The next enabled logs need to show the selected action,
C0/C1 requests, actual motion and interventions. They must establish whether
centering improves without losing the recovered turn response.

Startup logs retain the controller class name. The 5 Hz event
`Ford C2-free path tracking` identifies hypothesis `curvature-c0-v3` and
records the selected action service/time, input ages, desired/measured
curvature, CAN yaw, C0/C1 targets, preview horizons and actual commands.

Reproduce focused checks from the repository environment:

```sh
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford_curvature_c0.py openpilot/selfdrive/controls/tests/test_ford_path_reference.py openpilot/selfdrive/controls/tests/test_ford_virtual_angle.py openpilot/selfdrive/controls/tests/test_ford_controlsd_logging.py openpilot/selfdrive/controls/tests/test_ford_path.py openpilot/sunnypilot/sunnylink/tests/test_settings_schema.py
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```
