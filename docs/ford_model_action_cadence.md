# Selected-action 20 Hz cadence experiment

The selected-action controller now sends LateralMotionControl2 every fifth
100 Hz update (20 Hz, nominally 50 ms). Each send uses the latest published
C0/C1. The v6 controller module is byte-identical to `c70a9ee84`: its geometry,
150 ms forecast, caps, two states, and 4 m/s / 0.5 rad/s slew are unchanged.
C2 and C3 remain zero. This tests transport cadence, not a new strength gain.

The existing default-off `FordModelActionController` Sunnylink setting is
snapshotted by `card` into `CarParamsSP.flags` on the supported CAN FD Lightning.
Both controller selection and send cadence use that snapshot. An onroad setting
write cannot switch either one. Complete an offroad-to-onroad cycle after updating.
The diagnostic hypothesis remains `model-action-measured-pose-v6`; the build
commit, CarParamsSP flag, and measured send cadence distinguish this experiment.

With the toggle off, existing CAN FD controllers retain 100 Hz transmission.
Legacy CAN stays at 20 Hz. Panda safety is byte-identical to `c21a9013`.
The sender retains Panda's existing per-message C2 slew bound even on the
20 Hz path; this controller does not use C2. No safety limit is relaxed.
Counters advance once per transmitted request, including wrap from 15 to 0.
Invalid paths zero the next scheduled request; disengagement sends mode 0 on
that request, without a new ramp-out sequence. Relative to a 100 Hz sender,
a change can wait up to four more control ticks (nominally 40 ms).

## Evidence and limits

On route `84865544361f55cb_000000a5--d0f935d323`, the camera's observed inactive
LMC2 stream ran at 19.993 Hz (7,952 messages, median 50.051 ms). Our sender ran
at 99.321 Hz (38,496 messages, median 9.938 ms). The camera data does not establish
the factory's active-mode cadence. All supplied v1–v6 drives already used
100 Hz; cadence has not been established as the cause of weak tracking.

The [transport replay record](ford_model_action_cadence_validation.json) covers
38,496 recorded send cycles at each of five possible scheduling phases:
192,480 sender updates and 38,496 transmitted requests in total. Every emitted
C0/C1 exactly matched the corresponding recorded request; C2/C3 stayed zero;
mode, counter and checksum checks passed. Every request passed the unchanged,
compiled Panda TX hook with controls eligibility set from the recorded mode.
This tests TX bounds, not a full Panda RX watchdog, vehicle response, or device boot.

Targeted tests additionally cover exact send intervals, latest-sample delivery,
counter wrap, every disengagement/invalid-input phase, unchanged fallback cadence,
100 Hz core slew, and a shared selection snapshot surviving serialization and
subsequent stored-toggle changes. The broader offline run passed 689 tests and
9,146 subtests; 178 inherited safety cases were skipped as inapplicable.
Ruff and typechecking of the touched production modules passed.

No physical tracking improvement is claimed. The next drive must establish
whether the lower cadence helps ordinary bends and turn exits, while checking
for added turn-in delay. Offline replay cannot predict that closed-loop response.

## Reproduce

Initialize the pinned submodule and use the project's built Python/native environment:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford*.py tools/ford_pscm_lab opendbc_repo/opendbc/car/ford/tests/test_ford.py openpilot/sunnypilot/sunnylink/tests openpilot/sunnypilot/mads/tests openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/common/tests/test_params.py opendbc_repo/opendbc/safety/tests/test_ford.py
```
