# Ford C2-free path tracking

Hypothesis `curvature-c0-c1-v4` derives both C0 and C1 from the same selected
desired-curvature request. C0 is unchanged from v3; C1 now describes the
heading of that requested arc instead of following a separate far-model-path
heading. C2 and C3 remain zero. The historical filename, class and
`FordVirtualAngleController` setting key remain for compatibility.

This is an experimental geometric request to the PSCM's own controller, not
an angle servo, fitted C0/C1-to-wheel conversion or physical tracking guarantee.

## Evidence and reason for the change

The weak v1 experiment produced very small C1 requests and poor turn response
in route7a. v2 restored substantial spatial turn demand, but the user reported
drifting without centering. Route7c had the experiment off and is a default
controller baseline; it does not validate enabled v2 behavior.

Route80 confirms enabled v3 on all nine supplied segments: commit `98662df40`,
setting enabled and hypothesis `curvature-c0-v3`. The user reported promising
turn response, but measured motion did not consistently reproduce the selected desired curvature. v3's C0
followed selected action curvature while its C1 followed filtered far-model
heading. Those two references could request different turn magnitudes.

In the route80 overshoot window at 417–420 s, the common-curvature candidate
reduces the replayed C1 request from approximately 0.5 to 0.286 rad. In the
undertracking windows at 333–339 s and 430–435 s, the candidate requests are
nearly unchanged. This supports testing reference consistency; it does not
predict that overshoot will disappear or undertracking will improve.

The PSCM also reports generic lateral-control limits in parts of route80,
including the overshoot window. The signal does not identify a torque, rate
or other specific physical mechanism. An unasserted limit does not establish
accurate tracking. Reference disagreement and PSCM
limit reports must be assessed separately.

## Common reference and command construction

controlsd supplies its existing bounded `desired_curvature`: the
`lateralManeuverPlan` request when that service is valid, otherwise
`modelV2.action`, after the existing curvature limiter. The selected action
includes the planner's centering intent and receives upstream delay treatment;
neither channel adds another response advance.

The controller computes targets in its existing command coordinates:

```text
L0 = max(8 m, speed × 1.0 s)
L1 = max(7 m, speed × 1.0 s)
C0_target = clip(0.5 × desired_curvature × L0², -5.11 m, +5.11 m)
C1_target = clip(desired_curvature × L1, -0.5 rad, +0.5 rad)
```

C0 uses a small-angle arc-displacement construction; C1 uses the arc's
heading change. Neither is a wheel-response prediction. At the preview
floors, curvature 0.04/m requests C0=1.28 m and C1=0.28 rad; curvature 0.10/m
requests C0=3.20 m and bounded C1=0.50 rad. Spatial floors keep preview
distance from collapsing during slow turns. They cannot restore turn intent
absent from the selected action.

Both channels use **absolute desired curvature**, not desired minus measured
curvature. Reaching the requested curvature therefore does not erase steady
turn demand. There is no additional centering integrator, wheel-error PID,
learned EPS gain or stall latch. C1 overflow is not transferred into C0.

| Command parameter | Value |
|---|---:|
| C0 preview | max(8 m, speed × 1.0 s) |
| C1 preview | max(7 m, speed × 1.0 s) |
| Independent C0 / C1 slew limits | 4 m/s / 0.5 rad/s |
| C0 / C1 bounds | ±5.11 m / ±0.5 rad |

The preview choices and limits are retained; v4 adds no new gain tuning.
Preview distances are still **effective gains**, because they change request
magnitude. Each channel retains its independent slew limit. Fractional wire
increments accumulate internally, and published commands mirror Float32 and
sign-reversed Ford CAN packing.

## Model comparison and tradeoffs

The existing `PathReference` remains for diagnostics and validity checks.
Measured CAN yaw and traveled distance align retained model geometry to the
current ego frame; the 0.30 s model-innovation filter and response interval
produce `model_heading_target` for comparison with the selected-action C1.
That filtered model heading and yaw-frame correction no longer contribute
to the transmitted C1 magnitude or direction. Neither C0 nor C1 commands
use an external measured-yaw feedback correction.

C1 consequently follows changes in the selected action more directly than
v3. The upstream curvature limiter and existing slew limit remain, but the
model-innovation filter no longer smooths its command. This can reduce excess
far-path heading demand, but can also expose action noise or remove helpful
preview. The new logs must distinguish those outcomes.

An earlier route7c near-stop turn already exposed a reference limitation:
at 482–485 s, selected curvature was only about +0.00174/m while the default
controller requested C1 near −0.5 rad from far-path geometry. v4 follows the
selected action for both channels; it cannot recover that missing or opposing
turn intent from the model path. Passing the supplied large-maneuver fixtures
does not establish preservation of every possible maneuver.

## Validity, selection and rollback

Freshness and service gates remain unchanged. Both command channels require
the selected action timestamp; model geometry remains required for the
comparison and existing validity gate. controlsd checks modelV2, the selected
action service, carState, vehicleParameters and CAN validity. Model, action
and measurement age must each be within the 150 ms freshness window. Action
source selection can switch between model and maneuver plan using the same
validity choice as the existing desired-curvature calculation.

Invalid services or geometry, nonfinite or stale inputs, backward model or
measurement timestamps, control intervals outside 2–100 ms, speed outside
0.3–55 m/s, or yaw-rate magnitude above 3 rad/s invalidate the request and
clear state. controlsd clears latActive, producing inactive Ford lateral
mode. Reengagement starts from zero slew state.

While lateral control remains authorized, driver input leaves the request
present, as in the default allocator. The PSCM retains its driver arbitration.
The diagnostic driver_override label records the steeringPressed flag; it
does not promise that lateral mode has been disabled.

Vehicle → Ford → **C2-Free Path Tracking (Experimental)** retains the existing
key and default-off setting. An already-enabled setting selects this version
after updating and restarting controlsd. Toggle changes require an
offroad-to-onroad cycle. Selection remains limited to CAN FD,
`FORD_F_150_LIGHTNING_MK1`, and EPS firmware `RL38-14D003-AA`.

The experiment takes priority over PSCM Coefficient Observer on that
combination. Turning it off and cycling offroad/onroad restores the previous
controller selection. The obsolete `FordSharedPathController` switch remains
removed. No live device setting is changed by this commit.

## Verification and remaining uncertainty

Regression checks cover the common-curvature C0/C1 construction, retained
large-turn command envelopes, steady-turn demand, independent slew limits,
fault resets, actual CAN packing, source selection, diagnostic logging and
settings schema. Recorded fixtures retain earlier large turns and route80's
overshoot and undertracking cases.

Command replay holds recorded motion and planner outputs fixed. It can show
what v4 would request, but cannot show how the truck or subsequent planner
output would change in response. **v4 has not been validated on the vehicle.**
The next enabled logs must establish whether reference consistency reduces
overshoot without adding oscillation or weakening turns. The nearly unchanged
undertracking requests remain a specific unresolved limitation.

Startup logs retain the controller class name. The 5 Hz event
`Ford C2-free path tracking` identifies `curvature-c0-c1-v4` and records the
selected action service/time, input ages, desired/measured curvature, CAN
yaw, C0/C1 targets, the diagnostic model heading, preview horizons and actual
commands.

Reproduce focused checks from the repository environment:

```sh
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford_curvature_heading.py openpilot/selfdrive/controls/tests/test_ford_curvature_heading_routes.py openpilot/selfdrive/controls/tests/test_ford_curvature_c0.py openpilot/selfdrive/controls/tests/test_ford_path_reference.py openpilot/selfdrive/controls/tests/test_ford_virtual_angle.py openpilot/selfdrive/controls/tests/test_ford_controlsd_logging.py openpilot/selfdrive/controls/tests/test_ford_path.py openpilot/sunnypilot/sunnylink/tests/test_settings_schema.py
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```
