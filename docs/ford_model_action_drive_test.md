# Ford selected-action drive-test branch

The candidate is selectable on the **Ford CAN FD F-150 Lightning** behind
its own persistent, default-off Sunnylink toggle. Version 6 uses calibrated
measured turn rate for C0's existing 150 ms vehicle-pose forecast. C1 still uses
selected, upstream-limited curvature. Raw Ford yaw remains an input-health and
diagnostic signal; calibrated motion now affects C0. This is yaw feedback whose
sensitivity depends on the existing preview time and path distance. There is no
fitted PSCM plant model, added strength multiplier, new filter or extra core state.
`calibration_approved=false`: offline checks do not establish physical tracking,
turn-exit behavior or closed-loop stability.

The current cadence experiment transmits this controller's LMC2 requests at
**20 Hz (50 ms)** while its calculation remains at **100 Hz**. See
[cadence validation](ford_model_action_cadence.md). The v6 control law and
per-second C0/C1 slew are unchanged; this is not a demonstrated tracking fix.

## Select and restore

1. Install branch `hiimisaac-dev` from
   `sunnypilot/sunnypilot` on the device using your normal branch-switch process.
   Allow its build to finish before changing the setting.
2. While offroad, open Sunnylink device settings → Vehicle → Ford and enable
   **Selected-Action Path Tracking (Experimental)** (`FordModelActionController`).
3. Complete a real offroad-to-onroad cycle. `card` snapshots the toggle into
   `CarParamsSP`; the sender and `controlsd` share that selection. Changing a
   stored toggle or disengaging alone cannot swap an active
   controller. Initial physical evaluation remains controlled testing.

The startup log event `Ford path controller selected` should report
`FordModelActionController`. Periodic `Ford C2-free path tracking` events
identify `hypothesis=model-action-measured-pose-v6`. Active events report
`pose_source=measured` when fresh calibrated motion is used, otherwise
`pose_source=requested`. They also include `pose_yaw_rate`, `pose_age`, raw host
`yaw_rate`, selected curvature and the command tuple.

Turning the new toggle off and completing another offroad-to-onroad cycle
restores **PSCM Coefficient Observer** if selected, otherwise the original
Ford path controller. The stored observer selection is preserved. The candidate
takes priority on the supported vehicle, independently of EPS firmware query
results. Other vehicles retain their existing selection.

The v8 implementation, its Sunnylink toggle and its dedicated tests are removed.
A leftover `FordVirtualAngleController=1` file cannot enable the new controller.
The shared Float32/CAN rounding helper now lives in `ford_model_action.py`;
unused v8 PSCM-feedback plumbing is removed. Historical v8 route evidence remains
in Git history and the archived validation documents.

## Wiring and validation

`Controls.__init__` selects the candidate once at startup. It shares the
existing Ford call path, selected upstream-limited curvature, service gates,
invalid-output disengagement, Float32 publication and downstream CAN builder.
C2 and C3 stay zero. The cadence experiment updates the opendbc sender and
submodule pointer. Panda safety is unchanged.

Measured-pose use requires healthy `deviceMotion` and `extrinsicsCalibration`
services, calibrated extrinsics no older than 1 s, valid angular velocity and
sensor/input flags, and finite calibrated yaw within ±3 rad/s. Both the motion
publication and its embedded filter-state timestamp must be no older than
150 ms; all three age checks allow at most 5 ms future skew. Calibration-only
updates rebuild the cached pose before the candidate uses it.
Unavailable, unhealthy or stale optional motion falls back to the v5
requested-curvature forecast without resetting C0/C1 slew. Existing base-input
failures still invalidate the command. C1, the ±5.11 m / ±0.5 rad field caps,
4 m/s / 0.5 rad/s slew rates, packing and two core states are unchanged.

Sunnylink publishes the toggle through its generated settings schema and
writes the registered Boolean through the existing parameter endpoint. The
offroad UI rule and `needs_onroad_cycle` metadata describe when it can be
changed and when it takes effect. An onroad backend write changes storage
only; the controller continues using its startup selection.

Native validation also exposed a pre-existing `params_keys_by_flag` bug:
every returned buffer referenced the same reusable string. Sunnylink backup
key enumeration could therefore return corrupted names. The bridge now
returns separate strings owned by the parameter handle. Regression tests
check distinct registered keys across flags, and toggle tests check its
persistence and backup registration using the rebuilt native library.

The current validation record is `ford_model_action_measured_pose_validation.json`.
Its runtime replay exactly matches the reviewed offline candidate across
340,757 recorded cycles and 681,514 Float32/CAN round trips. C1 and eligibility
match v5 on all four extracts. The replay checks frozen recorded inputs; it does
not simulate how the vehicle would respond to different commands.

The candidate adds C0 during the recorded weak-bend turn-rate shortfalls and
reduces it during the older overshoot example. Tight-turn C1 saturation remains.
On the 70.24-second sustained quiet-path cohort, C0 amplitude RMS decreases but
per-cycle change RMS rises about 28%; physical centering and tracking still need
evaluation. All four routes came from the same truck, so cross-PSCM performance
has not been demonstrated.

`ford_model_action_no_yaw_damping_validation.json` archives v5 checks;
the [v5 notes](ford_model_action_no_yaw_damping.md) explain the prior damping removal.
`ford_model_action_full_prediction_validation.json` archives v4 checks;
the [full-prediction notes](ford_model_action_full_prediction.md) explain cap removal
and remaining physical uncertainty. `ford_model_action_prediction_validation.json`
archives the capped v3 evaluation. `ford_model_action_damping_validation.json`
archives the preceding v2 checks at their recorded source hashes.
`ford_model_action_drive_test_validation.json` archives v1 wiring validation
at the recorded source hashes, including 284 tests and 26 subtests. Its counts
and 145-line controller size describe v1. The 469-line v8 module remains removed.

The original 133,550-cycle route reconstruction, 485,238 packing round trips
and mutation probes remain recorded separately in
`ford_model_action_validation.json` at the offline-stage source hashes.

## Reproduce deployment checks

Initialize the branch's pinned opendbc submodule with `git submodule update --init opendbc_repo`
and build the native Params library from this branch before testing.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260907 --opendbc-revision "$(git -C opendbc_repo rev-parse HEAD)" --output .cache/ford_model_action_drive_test/stress.json
```

The full hardware build and device boot are not performed by these offline
tests. Installing the branch and enabling the toggle are separate actions;
pushing the branch does not change a device's selected software or settings.
