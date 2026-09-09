# Ford C1 feedback experiment

The restored original v1 can leave a steering error while C0 and C1 still have
room. Its command law does not directly correct measured steering error. This
experiment keeps that mapping and adds one accumulated C1 correction:

```text
error = selected_limited_desired_curvature - measured_curvature
correction += error * speed * elapsed_measurement_time
C1_target = original_model_C1 + correction
```

Curvature (1/m) multiplied by traveled distance (m) gives heading mismatch in
radians. Applying that mismatch to C1 at **1:1 is an explicit feedback-strength
choice**. Dimensional consistency does not prove that every PSCM responds
correctly to that strength. There is no fitted PSCM response model or new
tunable multiplier.

For example, at 20 m/s, a constant curvature shortfall of 0.001/m adds 0.02 rad
to C1 over one second when the output can accept it. When measured curvature
matches the request, the correction holds. If the vehicle turns more than
requested, the correction moves in the unwind direction. Changing the model
request still changes the base immediately, subject to the existing slew.

## Preserved mapping and limits

- C0 is the current model path's lateral offset at 7 m of arc distance, holding
  the available endpoint for shorter paths; its limits remain ±5.11 m and 4 m/s.
- Base C1 is `max(7 m, speed × 1 s) × selected_limited_desired_curvature`, clipped
  to ±0.5 rad. Final C1 uses the same ±0.5 rad and 0.5 rad/s limits as v1.
- C2 and C3 are zero. Sign conversion, Float32/CAN rounding, upstream curvature
  limiting and the 100 Hz sender retain their existing behavior.

The core holds three values: unquantized C0, unquantized C1 and the correction.
Zero error from a reset leaves the correction at zero and preserves the old
command arithmetic exactly. There is no separate percentage or distance cap
on the correction.

## Feedback measurement, timing and limits

The measurement is `controlsd.curvature`, computed from measured steering
angle with the existing live vehicle parameters. It matches the curvature
used for the desired-versus-actual steering comparison. It is not an independent
measurement of tire slip or the vehicle's actual ground path. CAN yaw remains
an input-health gate and does not drive this feedback.

The adapter integrates only elapsed time between fresh `carState` publications.
The first publication after reset integrates zero time. Duplicate timestamps
integrate zero; a fresh timestamp accounts for the elapsed measurement interval.
Output slew continues on valid control cycles. Existing service-age, speed,
model-geometry and clock-order gates remain, with the same finite/range check
also applied to measured curvature. Disengagement or invalid input clears all
three core states.

The correction cannot accumulate farther into an unavailable C1 amplitude or
slew request. Increments that move back toward the available output remain
allowed. Moving the base request does not itself rewrite the correction.

Fresh PSCM status means a valid message whose original CAN receipt timestamp
is within the existing −5 to +150 ms age allowance. Reached-limit status (2)
prevents extra accumulation in the measured turn direction. An old correction
opposing that direction can return to zero; it cannot be trapped below the
base request by the limit flag. Unwind and base model changes remain available.
Close-to-limit status (1) does not block feedback. Missing or stale status
does not gate it; local amplitude and slew anti-windup still apply.

Driver steering-pressed, torque above the existing 1 Nm allowance, nonfinite
torque, or fresh driver-limit status (3) clears the correction. Fresh denied
or inactive PSCM status also clears it. The base model request continues
through existing engagement and driver arbitration; clearing the correction
does not bypass the final output slew.

## Offline evidence and reproduction

`ford_c1_feedback_validation.json` records the source hashes and completed
checks. Tests exercise build, hold, unwind, saturation, limit flags, immediate
driver input, stale and repeated measurements, invalid inputs and both signs.
Integration tests execute actual controlsd selection and limiting, Float32
publication, CarControlSP conversion and the Ford CarController CAN builder.
Randomized runs check feedback invariants separately from zero-error
compatibility with the original independent scalar oracle.

The combined suite passes **511 tests and 9,146 subtests**. Its 178 skips are
in inherited safety base classes or unsupported safety-test variants. Ruff,
the controller's Ty check and settings compilation pass. Feedback stress,
zero-error stress and the b8 replay total **578,569 Float32/CAN round trips**;
the integration test separately verifies 1,010 transmitted packet constructions,
including every counter and checksum. No packets are sent to hardware.

The b8 replay retains recorded desired/measured curvature, model publications,
driver input and PSCM flags. It compares candidate commands with the restored
v1 at `a7d70e2b0890184636827351e4789d866f2a7c97`. All 160,431 reconstructed
activation decisions and C0 commands match. C1 changes on 58,106 cycles.
At 4:12.493, for example, reconstructed host C1 changes from −0.1625 to
−0.2035 rad; at 3:56.250 it changes from −0.1280 to −0.1080 rad. These are
changes to commands on frozen measurements, not predicted wheel angles.

Controls publication time proxies the unlogged computation clock, and the
full SubMaster health state cannot be reconstructed. This route uses the
consumed model publication as its reference and has no maneuver-plan messages.
Replay cannot show whether this feedback fixes weak turns, hanging turns or
oscillation. A new drive is needed to measure those outcomes.

Use the branch's native dependencies and pinned opendbc revision
`c21a9013700734dd20b09e05aa68329ad8cc20f9`:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
python -m tools.ford_pscm_lab.feedback_replay stress --cycles 200000 --output .cache/ford_c1_feedback/feedback_stress.json
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260907 --opendbc-revision c21a9013700734dd20b09e05aa68329ad8cc20f9 --output .cache/ford_c1_feedback/zero_error_stress.json
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_routeb8 --output .cache/ford_c1_feedback/routeb8
```

The last command requires the existing full-rlog b8 extract (`route.npz`,
`model_paths.npz`, `metadata.json`), identified by hashes in the validation
record. The historical route90/95 replay deliberately sets measured curvature
equal to requested curvature to check zero-error compatibility; it does not
exercise recorded steering feedback.

Enable using the [existing Sunnylink toggle](ford_model_action_drive_test.md).
The diagnostic identity is `model-action-c1-feedback-v1`.
