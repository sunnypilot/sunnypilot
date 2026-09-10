# Ford C1 correction carryover experiment

The feedback controller at `5fbb583e5` can retain a correction from an earlier
turn that outweighs the new base C1. The measured curvature can already be
opposite the desired curvature, yet total C1 continues to request the old
direction while the integral works back toward zero.

This experiment keeps the existing 1:1 feedback strength and adds a conditional
reset of that correction. It is a command-policy experiment, not a demonstrated
improvement in physical steering response.

## Release rule

All of the following must be true on a valid, active cycle:

- Feedback is enabled and a fresh steering publication advances measurement time.
- Base C1 is nonzero by at least one DBC step (0.0005 rad).
- Both target C0 and the slewed C0 request agree with base C1's direction,
  by at least one DBC step (0.01 m).
- Measured steering-derived curvature points opposite the desired curvature.
- The accumulated correction prevents total C1 from requesting the base direction:
  the sum of base C1 and correction is zero or opposite base C1.

The stored correction is then set to zero before the usual feedback increment.
The final C1 command still passes through its existing ±0.5 rad amplitude and
0.5 rad/s slew limits. The reset cannot directly jump the transmitted command.
The DBC steps reject requests smaller than one representable step; they are
not new strength multipliers. This reset policy is itself an engineering choice.

There is no reset simply because steering error crosses zero, or because C1
and its correction have opposite signs. Matched curvature, neutral/conflicting
C0, a correction that does not outweigh base C1, and repeated measurements all
preserve normal integration. The condition can apply to small steering
corrections as well as large turns; it has no turn-size or speed threshold.

No previous-turn direction or timer is stored. Agreement between current path
requests and disagreement with measured curvature are the confirmation. This
does not establish which part of the combined C0/C1 request a PSCM physically
needs. In particular, when C0 still points into the previous turn, this rule
deliberately leaves the integral alone.

## Preserved behavior and diagnostics

C0's 7 m mapping, its limits, the base C1 mapping, upstream curvature limiting,
the original integral strength, driver/PSCM arbitration, C2=C3=0 and the 100 Hz
sender are unchanged. No fitted PSCM model, proportional term or gain schedule
is added. There are still three values used by the command law: C0, C1 and
the correction. A diagnostic-only `carryover_release_count` is added and resets
with the controller. It is included in the existing periodic diagnostic event.

The same default-off Sunnylink toggle selects this version. Its diagnostic
identity is `model-action-c1-feedback-v2`. See the [drive-test instructions](ford_model_action_drive_test.md).

## Offline evidence

The two mirrored command-regression tests failed before the change. After
building correction through actual feedback, the old controller still requested
the old C1 direction 0.4 s into a reversal. Both tests now pass with the original
output slew. Additional tests cover holding a steady curve, small error
crossings, neutral and conflicting C0, representable command boundaries,
freshness, driver override and PSCM limits. Integration tests execute the actual
controlsd selection and upstream limiter, Float32 publication and Ford CAN
builder, using both model and maneuver-plan requests and both turn directions.

The combined suite passes **567 tests and 9,146 subtests**, with the same 178
inherited/unsupported safety-test skips as the original feedback validation.
The randomized checks include mirrored inputs, zero-error compatibility, and
comparison against the exact previous controller from cloned pre-update states.

Frozen b8 replay triggers 11 releases; b9 triggers 14. Activation and C0 match
the previous controller exactly on every reconstructed cycle. In b9, most
releases concern small corrections; one follows the large turn around 13:28.
The C0/C1 disagreement at 14:36 is preserved. Numerical details and source
hashes are in `ford_c1_carryover_validation.json`.

At the release around 13:28, the candidate C1 crosses into the requested
direction 0.255 s earlier than the previous controller on identical frozen
inputs. This is a command zero-crossing comparison, not a measured improvement
in the truck's steering response. The lab checks total 669,343 Float32/CAN
round trips, in addition to the integration tests.

Replay preserves recorded model requests and measured motion. A difference
between candidate and baseline commands can persist because the recorded
steering does not respond to the changed command. Replay cannot predict wheel
angles, centering, oscillation, or how much earlier the vehicle would unwind.
No device build, boot, installation or physical validation was performed.

## Reproduction

Use the branch's native dependencies and pinned opendbc revision
`c21a9013700734dd20b09e05aa68329ad8cc20f9`. The route commands require the existing
full-rlog b8/b9 extracts and the baseline Git revision. Run:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
python -m tools.ford_pscm_lab.feedback_replay stress --cycles 200000 --output .cache/ford_c1_carryover/stress.json
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260907 --opendbc-revision c21a9013700734dd20b09e05aa68329ad8cc20f9 --output .cache/ford_c1_carryover/zero_error_stress.json
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_routeb8 --baseline 5fbb583e592d30de266f8160a5d6b9c620c97f56 --output .cache/ford_c1_carryover/routeb8
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_routeb9 --baseline 5fbb583e592d30de266f8160a5d6b9c620c97f56 --output .cache/ford_c1_carryover/routeb9
```
