# Ford completed-unwind correction release

Version `model-action-c1-feedback-v5` releases dominant C1 correction after a
confirmed unwind reaches the selected curvature. This fixes stored correction
continuing to request a new turn after its original unwind is complete.

Route 115 (`codex-last2`) ran v4, `6df5eabb7`. Near 2:13.2, desired and actual
steering were both near zero after a right turn, but C1 still requested about
0.1165 rad left. About 0.114 rad was accumulated unwind correction. V4's
changed-request release did not apply: the small new left request was increasing
while the measured error called for less left steering. The earlier reversal
release also did not apply because measured and requested curvature were
already on the same side.

## Rule

On a fresh steering measurement, remember an unwind direction when the selected
curvature relaxes toward zero (or crosses it), measured curvature remains on
the previous side, and measured error calls for leaving that old turn.

When measured error reaches or passes zero in that unwind direction, release
the stored correction only if all of these agree:

- The selected curvature has reached zero or crossed into the unwind direction.
- Correction points in that direction and exceeds the magnitude of base C1.
- Original model C0 and applied C0 both confirm that direction by at least the
  existing 0.01 m DBC step.

Consume the unwind marker at this first catch-up, even if the other conditions
prevent release. A steady old-side bend, neutral/conflicting C0, or a correction
smaller than base C1 retains its correction. Steady requests cannot arm the
marker. Duplicate steering publications cannot arm or consume it. Driver/PSCM
feedback inhibition and controller resets clear it; correction reversing
direction also clears it.

After retirement, the v4 command law still runs: bounded changed-request
release, reversal release, measured-error integration, PSCM arbitration, and
final C1 slew. Removing stored correction therefore does not jump the output.
There is one additional control state, `unwind_direction`; `unwind_release`
only reports the signed correction retired on the current cycle. Periodic
diagnostics may miss individual release cycles.

This is a conditional correction-reset policy, not a PSCM plant model. It adds
no strength multiplier. The existing 1:1 feedback choice, C0 mapping/overflow,
C2/C3 zeroing, amplitude/slew limits, sender cadence and input gates remain.
Toggle off still selects upstream Ford control; toggle on selects the experiment
on Ford CAN FD platforms. See [selection and restore](ford_model_action_drive_test.md).

## Exact exit replay

Frozen route 115 measurements trigger one release at **2:13.203501**. The
selected steering angle is 0.469 degrees left and measured angle is 0.500 degrees
left. The controller retires 0.114026 rad of left unwind correction. Its first
C1 output moves from 0.1165 to 0.1110 rad left, respecting the original slew.

At **2:13.594615**, old C1 is **0.1240 rad left**, versus **0.0105 rad left** in
v5. C0 is identical. The earlier unwind (2:09 through 2:13.2), comparison turn
(3:20 through 3:34), and comparison bend (5:33 through 5:45) have identical
commands throughout their windows.

The recorded wheel motion stays fixed in this replay. It does not predict a
new steering angle, prove stability, or establish that the full overshoot is
fixed. This maneuver also includes driver input and a changing C0 request;
neither its whole swing nor every hanging exit can be attributed to stored I.

## Validation

Four targeted regressions failed on v4 because correction persisted after
catch-up; all now pass. Expanded tests cover both directions, fresh/duplicate
feedback, catch-up confirmation, steady tracking/noise, old-side bends, C0
agreement, dominant correction, reset/override, limit-reached behavior and slew.
Integration exercises actual controlsd request selection/limiting for model
and maneuver sources, Float32 publication, and Ford CAN packing/checksums.

The combined suite passes **753 tests and 9,145 subtests**, with **178 inherited
or unsupported safety-test skips**. Random feedback stress covers 200,000 cycles
and their mirrors. Each cycle exactly matches v4 after only the declared new
retirement; 59 cycles retire correction. Independent zero-error checks cover
200,000 cycles and 18,138 field-boundary cases. Ruff, controller Ty and settings
compilation checks pass.

| Frozen route | Cycles | New releases | Changed C1 cycles | Largest C1 difference |
| --- | ---: | ---: | ---: | ---: |
| 114 | 61,027 | 4 | 2,849 | 0.0150 rad |
| 115 | 40,037 | 1 | 384 | 0.1140 rad |
| 112 | 108,971 | 14 | 30,036 | 0.0720 rad |
| 113 | 49,614 | 1 | 951 | 0.0050 rad |
| Historical b9 | 90,774 | 16 | 7,013 | 0.1435 rad |

All routes compare v5 against v4 with the same recorded inputs. Activation and
C0 match exactly on all 350,423 cycles. Releases also occur at smaller exits;
changed history can affect subsequent ordinary bends. These results do not
establish unchanged physical centering. Route 114's large segment-2 overshoot
does not trigger this new release, so it remains a separate unresolved case.

The five replays and two stress runs verify **768,561 Float32/CAN round trips**,
separately from the integration suite. Exact source hashes and numerical
results are in `ford_unwind_catchup_validation.json`.

## Reproduction

Use the native project Python dependencies and unchanged opendbc revision
`64aa61b9b3fd26e70a7caa915acab207ff3cd64a`. Route replay requires the full-rlog
extracts identified by validation hashes; the original logs are not modified.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
export PARAMS_ROOT=/tmp/ford-v5-test-params
export LOG_ROOT=/tmp/ford-v5-test-logs
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
python -m tools.ford_pscm_lab.feedback_replay stress --cycles 200000 --output .cache/ford_unwind_catchup/stress.json
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260913 --opendbc-revision 64aa61b9b3fd26e70a7caa915acab207ff3cd64a --output .cache/ford_unwind_catchup/zero_error.json
for route in 114 115 112 113 b9; do
  python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_route${route} --baseline 6df5eabb7e7f6bc4e206644d5ca9069df820124e --output .cache/ford_unwind_catchup/route${route}
done
```

Publication time approximates the computation clock; full SubMaster health is
not reconstructable. These route replays do not reconstruct selected maneuver
messages; integration tests cover that source. No device build, boot,
installation or physical steering test is performed offline.
