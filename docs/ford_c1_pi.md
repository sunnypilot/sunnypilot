# Ford C1 proportional feedback trial

V6 adds **P = 0.25** to the selected-action controller. It responds to a steering
shortfall immediately and subtracts demand immediately when the wheel exceeds
the selected request. V5 accumulated correction over traveled distance. P has
no stored correction to release when its error disappears.

This is an initial drive-trial gain, not an identified PSCM calibration or a
claim of improved physical tracking. Six Lightning routes establish command
behavior across recorded scenarios. They cannot identify the best stable gain
without observing the vehicle responding to the changed commands.

## Command law

With curvature in inverse meters, speed in meters per second and heading in radians:

```text
D = max(7 m, speed × 1 s)
error = selected_limited_curvature - measured_steering_curvature
base_C1 = clip(D × selected_limited_curvature, -0.5, +0.5)
P = 0.25 × D × error
I_increment = speed × error × fresh_measurement_elapsed_time
C1 = amplitude_and_slew_limit(base_C1 + P + I)
```

P is 25% of the heading-equivalent tracking error, not a 25% multiplier on the
model request. At matched curvature it is zero. It is stateless and can change
with a new request even if a steering publication repeats; repeated steering
publications still cannot integrate I twice. Driver override and fresh PSCM
denied/inactive states clear both feedback terms. Fresh `limit=2` inhibits
outward I accumulation while permitting unwind; P remains available inside the
existing combined output envelope.

The existing C1 amplitude limit (±0.5 rad) and slew (0.5 rad/s) apply to the sum.
Anti-windup includes P when calculating I's available headroom. P can consume
a slew interval that previously allowed I accumulation. The conditional I
release rules, including [completed-unwind release](ford_unwind_catchup.md),
remain. C0 retains the same 7 m mapping, base-heading overflow, cap and slew;
neither P nor I spills into C0. C2/C3 stay zero. No plant, gain schedule or
automatic gain learning is introduced.

Onroad selection explicitly supplies `C1_PROPORTIONAL_GAIN = 0.25`. Direct
`FordModelActionController()` and `ModelActionController()` construction defaults
to zero P for v5 reference/replay compatibility. The existing default-off
Sunnylink toggle selects v6 on any Ford CAN FD. Toggle off still selects
upstream Ford control. See [installation and selection](ford_model_action_drive_test.md).

## Lightning replay findings

Routes `112`, `113`, `114`, `115`, `b9` and `ca` supplied 677,871 control cycles.
Each was replayed with P gains 0, 0.1, 0.25 and 0.5, paired with diagnostic
feedback delays 0, 0.2 and 0.4 s: 12 combinations and 8,134,452 candidate updates.
Recorded model, driver, steering and PSCM inputs stayed fixed.

Both command columns are replayed C1 in radians with left positive. The angle
pair is the single recorded desired/actual wheel measurement, not a predicted
outcome for either candidate.

| Example | Desired / actual angle | V5 C1 | P=0.25 C1 |
| --- | ---: | ---: | ---: |
| 115, 207.908 s: late left entry | 94.2° / 51.2° | +0.1685 | +0.1825 |
| 115, 208.099 s: entry continues | 111.0° / 72.8° | +0.2105 | +0.2245 |
| 114, 473.086 s: well-tracked bend | 57.3° / 56.3° | +0.1855 | +0.1850 |
| 113, 481.567 s: hanging right exit | −7.6° / −94.4° | +0.0645 | +0.0875 |
| 115, 133.595 s: completed unwind | 6.0° / 29.9° | +0.0105 | 0.0000 |

The completed-unwind example is excluded by the original quality/driver clean
mask. It is useful for checking command release, not autonomous tracking
attribution. Large-turn windows often contain interventions and require review
of driver input before assigning a tracking result to the controller.

Across 2,740.44 seconds of valid, feedback-enabled, clean samples with desired
wheel angle below 30°, the duration-weighted mean absolute C1 change is
0.001001 rad at P=0.25, versus 0.001961 at P=0.5. Per-route 95th-percentile
changes at P=0.25 are 0.0025–0.0070 rad; the largest ordinary-cohort change is
0.0350 rad. Small average command changes do not establish unchanged centering
or stability.

P=0.25 is an engineering choice between the tested smaller and larger responses,
not an optimization result. At the late-entry example, adding a fixed 0.4 s
feedback delay instead gives C1 +0.1420 rad. Across the ordinary cohort, that
delayed P=0.25 variant changes C1 by 0.011255 rad on average. V6 therefore
retains v5's feedback timing to isolate P. This does not identify or disprove
the vehicle's physical delay. The diagnostic delay variants change only P and
I integration targets; request-release decisions still use the current request.

## Tuning and next-drive evidence

Comma's [torque controller](https://github.com/commaai/openpilot/blob/master/openpilot/selfdrive/controls/lib/latcontrol_torque.py)
separates feedforward, P and I and aligns its torque feedback reference with
steering delay. Its [angle PID controller](https://github.com/commaai/openpilot/blob/master/openpilot/selfdrive/controls/lib/latcontrol_pid.py)
uses desired-minus-measured steering angle directly. These different paths do
not imply one delay setting should be copied into Ford C1.

Use the same discipline: explicit parameters, separate term logging, fixed
request conditions and measured response. Comma's
[lateral maneuver report](https://blog.comma.ai/0111release/#lateral-maneuver-report)
uses repeatable step/sine maneuvers to assess response. C1 is a path-heading
request to another controller, not normalized steering torque; numerical torque
gains and torque calibration cannot be copied across.

For the next controlled evaluation, compare similar speeds and model requests:
entry delay/shortfall, overshoot as the request relaxes, correction after catch-up,
ordinary-bend centering and oscillation. Keep desired/actual tracking on original
timestamps. Check C0/C1 caps, slew, driver input and fresh PSCM flags separately.
More gain cannot remove hardware limits and can introduce oscillation. These
logs all come from a Lightning; the gain is not yet validated across other
PSCMs. No scripted maneuver mode is enabled by this change.

Periodic `Ford C2-free path tracking` events identify
`hypothesis=model-action-c1-pi-v6` and expose `heading_proportional`,
`proportional_gain`, `feedback_curvature` and `feedback_error` alongside
`heading_feedforward`, `heading_correction`, command and release diagnostics.
`calibration_approved=false` remains.

## Validation and reproduction

The final selected path exactly matches the sweep's P=0.25, zero-delay variant
on all six routes, including C0/C1, P, I and activation. Zero-P/zero-delay matches
v5 exactly on every cycle. All variants preserve C0 and activation. Another
200,000 seeded stress cycles check PI arithmetic, anti-windup, mirror symmetry,
driver/PSCM arbitration, resets, amplitude/slew and zero-P parity. Sweep,
selected replay and stress total **9,012,323 Float32/CAN round trips**.
Encoding checks do not test vehicle motion.

**776 tests and 9,145 subtests passed; 178 were skipped.** Coverage includes
actual startup selection, controlsd request source/limiting, Float32 publication,
100 Hz CAN encoding, checksums, both turn signs, integral release, Sunnylink
persistence, toggle-off upstream behavior and Ford safety tests. Ruff,
controller Ty and settings compilation passed. A hardware build/device boot
and physical response tests have not been performed.

Use the project's Python environment and built cereal/opendbc dependencies:

```sh
export PYTHONPATH=.:opendbc_repo:.cache/ford_v6/test_deps
export PYTHONDONTWRITEBYTECODE=1
export PARAMS_ROOT=/tmp/ford-pi-test-params
export LOG_ROOT=/tmp/ford-pi-test-logs
python -m tools.ford_pscm_lab.pi_replay .cache/ford_route115 --output .cache/ford_pi_sweep/route115
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_route115 --baseline 22d188776cb557acea459a1fca70812bdb2df46c --output .cache/ford_pi_sweep/selected115
python -m tools.ford_pscm_lab.pi_stress --cycles 200000 --gain .25 --output .cache/ford_pi_sweep/stress.json
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
```

Repeat both replay commands for the other five extracts. The machine-readable
[validation record](ford_c1_pi_validation.json) records counts, source hashes,
cohort definitions and sampled command changes. Publication time proxies the
computation clock; full SubMaster state and selected maneuver-plan publications
are not reconstructed. Real maneuver source selection is exercised in integration
tests. Historical controller reports retain their original version scope.
