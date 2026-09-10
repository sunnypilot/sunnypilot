# Ford base-heading overflow experiment

The Lightning ca route recorded controller `959ae3d6e`. Its large turns included
flat C1 requests at ±0.5 rad while C0 still had available range. Those were
nonzero, active commands, but increasing base heading above the C1 limit was
discarded. Other apparent pauses followed reductions in the selected model
request; this change continues to follow those reductions.

The new experiment allocates clipped-away **base heading** to C0 using the
existing 7 m reference. It does not allocate the accumulated feedback correction.
This is a hypothesis about command allocation, not a measured improvement in
PSCM response or a claim that C0 and C1 are physically interchangeable.

## Command rule

Using the selected, upstream-limited desired curvature:

```text
raw_base_c1 = max(7 m, speed × 1 s) × desired_curvature
base_c1 = clip(raw_base_c1, -0.5 rad, +0.5 rad)
extra_c0 = 7 m × (raw_base_c1 - base_c1)
c0_target = clip(model_y_at_7m + extra_c0, -5.11 m, +5.11 m)
```

The combined C0 target still passes through the existing 4 m/s slew limit.
C1 retains its existing feedback, ±0.5 rad amplitude and 0.5 rad/s slew limits.
C2 and C3 remain zero. Short model paths retain their existing endpoint hold.

Before amplitude/slew limits, the allocation preserves the linear reference
`C0 + 7*C1` for the base request. This is a single-reference identity; it does
not preserve the entire path or predict steering torque. The 7 m reference is
an existing engineering choice. No fitted plant, new tunable strength multiplier,
timer or stored overflow is added. The existing 1:1 feedback strength remains.

Extra C0 falls with raw base heading and its target becomes zero at the C1 cap.
The output can take longer to return because of its existing slew state. There
is no guarantee that increasing C0 makes every PSCM turn better or release sooner.

## Preserved integration

The conditional correction release still requires **original model C0** and
applied C0 to confirm base C1's direction. Added overflow cannot itself substitute
for model confirmation. Changed applied C0 can nevertheless affect release
timing in some histories. Driver/PSCM arbitration, service freshness, resets,
upstream curvature limiting, Float32 publication and the 100 Hz sender remain.
No opendbc dependency or Panda safety change is made.

The existing default-off Sunnylink toggle selects this version on any Ford
CAN FD vehicle. Diagnostic identity is `model-action-c1-feedback-v3`.
`offset_overflow` records extra target meters before C0 amplitude and slew;
`offset_request` continues to record the actual continuous C0 state.
See the [drive-test instructions](ford_model_action_drive_test.md).

## Offline evidence

The focused overflow regressions initially produced 28 failures and 18 passes
against the prior controller. They now pass. They cover both signs, several
speeds, the heading threshold, combined C0 clipping, short paths, release,
feedback-only saturation, driver/PSCM feedback gates and independent model
confirmation. Twelve integration cases send 4,800 frames through actual
controlsd selection/limiting, Float32 publication and Ford CAN packing on all
six listed Ford CAN FD platforms, checking counters and checksums.

The combined suite passes **670 tests and 9,146 subtests**, with 178 inherited
or unsupported safety-test skips. Both 200,000-cycle randomized runs pass,
including mirrored inputs, independent scalar target/slew checks, feedback
invariants, comparison with the exact prior controller from cloned states,
and 18,138 exhaustive field/Float32 boundary cases. These checks and the ca
replay total **745,586 Float32/CAN round trips**, in addition to integration tests.

Frozen ca replay covers 327,448 control cycles across all 55 extracted segments.
Activation is identical; C1, C2 and C3 are identical on every cycle. C0 differs
for 855 cycles (8.607 s), concentrated in the large turns and their slew tails.
The extra target is present for 7.359 s. Before the first overflow, every command
matches the prior controller. All disabled cycles have zero commands.

At the same recorded peak-request timestamps, absolute packed C0 changes as follows:

| Segment | Previous C0 | Candidate C0 | C1 magnitude, both |
| --- | ---: | ---: | ---: |
| 10 | 3.90 m | 5.11 m | 0.50 rad |
| 31 | 2.85 m | 3.08 m | 0.50 rad |
| 35 | 3.67 m | 5.11 m | 0.50 rad |
| 52 | 3.11 m | 3.42 m | 0.50 rad |

The candidate reaches the existing C0 cap for 2.054 s. These are reconstructed
commands on original inputs, not newly transmitted commands or predicted wheel
angles. Segment 52's output is still slewing at the selected timestamp.

Every overflow episode returns to the previous C0 output without a reset or
another overflow interrupting the comparison. After overflow first becomes
zero, the longest output tails are **0.475 s in segment 10** and **0.712 s in
segment 35**. This is the added slew tail relative to the prior command, not
the truck's physical release delay. It is a material behavior to inspect during
controlled evaluation: more pull through capped turns may also add hanging
on exit. Ordinary requests below the cap retain the original target mapping.

The recorded model, vehicle motion, driver input and PSCM flags remain fixed.
Replay cannot establish resulting tracking, centering, torque or stability.
The route has no maneuver-plan messages; the replay uses the consumed model
reference and recorded selected curvature. Computation time is approximated
by control publication time, and full SubMaster health checks are unavailable.
No device build, boot or installation is performed offline.

## Reproduction

Numeric results and source hashes are in `ford_c1_overflow_validation.json`.
Use native project dependencies and pinned opendbc
`c21a9013700734dd20b09e05aa68329ad8cc20f9`. The ca replay requires the existing
full-rlog extract (`route.npz`, `model_paths.npz`, `metadata.json`).
The following commands apply to this version; earlier validation documents
record their named historical controllers.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
python -m tools.ford_pscm_lab.feedback_replay stress --cycles 200000 --output .cache/ford_c1_overflow/stress.json
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260910 --opendbc-revision c21a9013700734dd20b09e05aa68329ad8cc20f9 --output .cache/ford_c1_overflow/zero_error_stress.json
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_routeca --baseline 959ae3d6e76c479f48e081c060b0f3569a6f15f4 --output .cache/ford_c1_overflow/routeca
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

For slew-tail analysis, in the replay's `commands.npz` find each nonzero run of
`offset_overflow`. From its first zero sample, measure until packed candidate
and baseline C0 agree within 1e-8 m, stopping separately at another overflow or
inactive cycle. Sum sample durations capped at 30 ms for weighted time totals.
