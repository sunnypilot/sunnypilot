# Ford changed-request correction release

The Chestnut/Tee Time routes 112 and 113 ran `17a86842f` (C1 feedback v3).
In route 113, an increasing turn request remained below its base C1 because
negative correction from an earlier oversteer episode took time to return to
zero. The existing reversal release did not apply: requested and measured
curvature were already in the same turn direction.

Version `model-action-c1-feedback-v4` retires a bounded amount of correction
when a changed request and measured error both oppose that correction. This
addresses software command delay. It does not establish improved wheel tracking
or fix all the recorded hanging exits.

## Rule

On a fresh steering measurement, evaluate the previous selected curvature and
the current selected curvature using today's existing heading reference:

```text
distance = max(7 m, speed * 1 s)
change = clip(distance * desired, -0.5, 0.5)
       - clip(distance * previous_desired, -0.5, 0.5)
error = desired - measured
```

Retirement requires all of:

- Feedback enabled and a previous feedback request available.
- Heading change at least one existing C1 DBC step (0.0005 rad).
- Change and current error agree in direction.
- Stored correction opposes that direction.
- The magnitude of `distance * error` is at least the correction magnitude.

Move the correction toward zero by at most the heading change, without crossing
zero. Then run the existing reversal release, elapsed-distance integration,
PSCM arbitration and final output slew. The mismatch requirement is an
engineering guard using the existing reference distance; it is not a fitted
PSCM response threshold or proof of stability. It protects a larger learned
correction from small target/measurement noise. There is no new tunable strength
multiplier, and the existing 1:1 feedback-strength choice remains.

The last selected curvature adds one control state. Duplicate steering samples
do not advance this history or retire correction; the next fresh sample uses
the net request change. A speed change alone cannot cause retirement because
both requests are evaluated at the same current speed. Invalid input and
disengagement reset the history. Driver override clears correction and prevents
a pending request change from being applied later.

C0 mapping and overflow, C2/C3 zeroing, amplitude/slew limits, sender cadence and
all input/driver/PSCM gates remain unchanged. Toggle off still selects upstream
Ford control on every platform. The existing default-off toggle selects v4 on
Ford CAN FD vehicles. `request_release` logs signed radians retired on that
cycle; periodic diagnostics do not capture every individual retirement.

## Evidence and limits

The regression command `python -m pytest -q -p no:cacheprovider
openpilot/selfdrive/controls/tests/test_ford_model_action_request_release.py`
initially returned **4 failed** on v3. It checks that an obsolete correction no
longer delays a changed same-direction turn or unwind after the output slew
has time to respond. Expanded cases cover small noise, matched tracking,
insufficient error, speed-only changes, clipped base requests, duplicate
measurements, override and reset. Integration tests exercise actual controlsd
selection/limiting, both model and maneuver references, Float32 publication
and Ford CAN packing.

Frozen replay compares v4 with the deployed v3 on the same recorded model,
measurement, driver and PSCM inputs:

| Route | Control cycles | Retirement cycles | Largest C1 difference |
| --- | ---: | ---: | ---: |
| 112 | 108,971 | 414 | 0.0235 rad |
| 113 | 49,614 | 119 | 0.0275 rad |
| Historical b9 | 90,774 | 440 | 0.0350 rad |

Activation and C0 are identical on every replay cycle. C2/C3 remain zero.
Retirement changes subsequent correction history, so command differences can
persist after a retirement cycle. In frozen measurements the vehicle cannot
react to those differences. Command differences occur in ordinary bends too;
these tests do not establish unchanged real-world centering or stability.

In route 113, segment 3, old opposing correction reaches zero at **3:18.630**
instead of **3:19.253**: **0.623 s earlier**. At 3:18.649, C1 magnitude is
0.319 rad instead of 0.2925 rad. The PSCM limit flag still inhibits additional
outward integration; retiring opposing correction cannot create new stored
outward demand through that gate.

The route 113 exit at 8:01.567 has **identical C1** in this replay. Route 112's
11:40.555 overshoot changes C1 by only 0.0015 rad, slightly later in the unwind
direction on the frozen history. These are material limits: the change does
not solve those exits. C0's contribution and physical PSCM response remain
unresolved. No counterfactual wheel-angle or tracking-error score is reported.

The combined suite passes **717 tests and 9,145 subtests**, with 178 inherited
or unsupported safety-test skips. Feedback stress and zero-error stress cover
200,000 cycles each; the latter also covers 18,138 field-boundary cases.
Together with the three route replays, these verify **667,497 Float32/CAN round
trips**, separately from the integration suite. Stress compares each step to
v3 after only the declared retirement and checks sign symmetry, bounds, slew,
resets, arbitration and correction direction. Ruff, the controller Ty check
and settings compilation pass. Numerical records are in
`ford_c1_request_release_validation.json`.

## Reproduction

Use the project's native Python dependencies and unchanged opendbc revision
`64aa61b9b3fd26e70a7caa915acab207ff3cd64a`. Route commands require the full-rlog
extracts (`route.npz`, `model_paths.npz`, `metadata.json`) identified by the
validation hashes. No original logs are modified.

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:opendbc_repo
# Optional writable roots for the tests' temporary parameter stores and logs:
export PARAMS_ROOT=/tmp/ford-v4-test-params
export LOG_ROOT=/tmp/ford-v4-test-logs
python -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py openpilot/sunnypilot/sunnylink/tests openpilot/common/tests/test_params.py opendbc_repo/opendbc/car/ford/tests/test_ford.py opendbc_repo/opendbc/safety/tests/test_ford.py
python -m tools.ford_pscm_lab.feedback_replay stress --cycles 200000 --output .cache/ford_v4/stress.json
python -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260912 --opendbc-revision 64aa61b9b3fd26e70a7caa915acab207ff3cd64a --output .cache/ford_v4/zero_error.json
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_route112 --baseline 17a86842f --output .cache/ford_v4/route112
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_route113 --baseline 17a86842f --output .cache/ford_v4/route113
python -m tools.ford_pscm_lab.feedback_replay route .cache/ford_routeb9 --baseline 17a86842f --output .cache/ford_v4/routeb9
```

Publication time approximates the computation clock; full SubMaster health is
not reconstructable. These routes have no selected maneuver-plan publications;
that source is covered by integration tests. No device build, boot, installation
or physical steering test is performed offline.
