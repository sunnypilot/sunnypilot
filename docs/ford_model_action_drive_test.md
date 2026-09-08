# Ford model-point drive-test branch

The default-off **Selected-Action Path Tracking (Experimental)** Sunnylink toggle
now selects the v7 model-point candidate on the **Ford CAN FD F-150 Lightning**.
The stored key remains `FordModelActionController`; an already enabled setting
selects this revision after updating and completing an offroad-to-onroad cycle.

The controller reads **model lateral position and model heading at the same
point**. Start with the model's predicted distance at one second, enforce the
existing seven-metre minimum, and hold the available endpoint when necessary.
C0 is that point's lateral position in metres; C1 is its unwrapped heading in
radians. C2 and C3 stay zero. The 150 ms yaw-based forecast and the reconstruction
of heading from selected curvature are removed.

This point choice is an engineering guess, not an identified Ford reference or
PSCM calibration. `calibration_approved=false`: offline tests do not establish
physical tracking, turn-exit behavior, or stability across different PSCMs.
See [the model-point decision and validation](ford_model_points.md).

## Select and restore

1. Install branch `hiimisaac-dev` from `sunnypilot/sunnypilot` and allow the build
   to finish.
2. While offroad, open Sunnylink device settings → Vehicle → Ford. Keep or enable
   **Selected-Action Path Tracking (Experimental)**.
3. Complete a real offroad-to-onroad cycle. `card` snapshots the toggle into
   `CarParamsSP`; the sender and `controlsd` share that selection. Changing a
   stored toggle or disengaging alone cannot swap an active controller.

The startup event `Ford path controller selected` reports
`FordModelActionController`. Periodic `Ford C2-free path tracking` events report
`hypothesis=model-pose-one-second-v7`, `pose_source=model`, `preview_time_s=1.0`
and `minimum_station_m=7.0`, plus input ages, slew state and the command tuple.
Selected desired curvature is still logged, but no longer constructs C0/C1.

Turning the toggle off and completing another offroad-to-onroad cycle restores
**PSCM Coefficient Observer** if selected, otherwise the original Ford path
controller. Other vehicles keep their previous selection. The retired v8 toggle
cannot select this candidate.

## Wiring and limits

Both model fields must have matching, finite, strictly increasing time arrays
starting at zero. Malformed geometry, stale required services, invalid timing,
or disengagement resets both actuator states. Freshness still requires model,
car-state and reference publications no older than 150 ms, with at most 5 ms
future skew. The valid control timestep remains 2–100 ms.

Only the two unquantized C0/C1 slew positions persist in the core. Field caps are
±5.11 m / ±0.5 rad and slew rates are 4 m/s / 0.5 rad/s. Calculation stays at
100 Hz; the existing [cadence experiment](ford_model_action_cadence.md) sends this
candidate at 20 Hz. Float32 publication, host-to-wire negation, packing and
Panda safety are unchanged. The opendbc pin remains
`87ca78e6e641eefb2d654f260a6ab08df3058bd5`.

Normal operation uses the model's point directly. The upstream scalar curvature
and its clipping still exist for logging/other controllers, but no longer bound
this candidate's heading target. Its C0/C1 field caps and slew still apply;
passing Panda TX checks does not establish an actual vehicle acceleration bound.
Lateral maneuver test mode supplies only a scalar curvature, not a model pose.
It explicitly invalidates/disengages this candidate as `unsupported_reference`.
Optional measured motion is no longer a command input.

## Reproduce offline checks

Initialize the pinned submodule and build the project's native Python dependencies:

```sh
git submodule update --init opendbc_repo
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford*.py tools/ford_pscm_lab opendbc_repo/opendbc/car/ford/tests/test_ford.py openpilot/sunnypilot/sunnylink/tests openpilot/sunnypilot/mads/tests openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/common/tests/test_params.py opendbc_repo/opendbc/safety/tests/test_ford.py
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260908 --opendbc-revision 87ca78e6e641eefb2d654f260a6ab08df3058bd5 --output .cache/ford_model_points/stress.json
```

Historical v1–v6 validation files retain their original source hashes and apply
to those revisions. In particular, `ford_model_action_measured_pose_validation.json`
describes v6, not the current model-point mapping. The hardware build and device
boot are not performed by these offline checks. Pushing a branch does not update
a device or change its stored settings.
