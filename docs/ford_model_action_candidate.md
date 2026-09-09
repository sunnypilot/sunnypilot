# Offline Ford selected-action candidate

This document and `ford_model_action_validation.json` record the offline
stage committed as `7ca3c6e3b`. The candidate is now available behind a
separate default-off Sunnylink toggle; see
[drive-test setup and validation](ford_model_action_drive_test.md).
The counts, source hashes and selector status below describe that earlier
stage. The current experiment adds [measured-curvature C1 feedback](ford_c1_feedback.md)
to this original mapping; the historical no-feedback description below is
not the current controller specification.

The decision is `C0 = current model y(7 m)`,
`C1 = max(7 m, speed × 1 s) × selected upstream-limited desiredCurvature`,
with C2=C3=0. The 7 m station and one-second scale are engineering choices,
not identified PSCM gains. `calibration_approved=false`.

`openpilot/selfdrive/controls/lib/ford_model_action.py` contains the core
and a separate adapter compatible with the existing controlsd call.
At that stage, the production selector, v8 implementation, settings, opendbc
submodule and Panda safety remained unchanged. Tests injected the adapter
offline; there was no production setting. No hardware or CAN transmission
occurs in the lab tools.

## Construction and integration

Only the unquantized C0 and C1 slew positions persist in the core.
Each field is clipped independently (±5.11 m / ±0.5 rad), slewed independently
(4 m/s / 0.5 rad/s), then packed using the existing Float32/sign-negation
rounding contract (0.01 m / 0.0005 rad). Heading overflow is not transferred
to C0. No yaw integral, blend, additional curvature contribution, reference
filter, turn modes, or 10 m C1 cap is introduced.

The selected standalone implementation from worktree 3548 is the provenance
for this law. Its two-state packer has been moved into the library core so
the controller does not depend on experimental lab code. Invalid numeric
types, overflowing arc geometry and malformed paths reset the core instead
of throwing or retaining a command.

Arc stations use cumulative model x/y distance, not forward x. As in the
reviewed standalone core, a path ending before 7 m holds its available
endpoint instead of extrapolating. This matters: route95 contains 44 active
cycles with 5.45–6.94 m of path at 2.78–3.46 m/s. A tested strict 7 m
coverage gate would have introduced disengagements and was removed. There
is no speed-dependent C0 horizon beyond this existing endpoint behavior.

The adapter retains the existing input age allowance (−5 to +150 ms),
speed domain (0.3–55 m/s), yaw sanity bound (±3 rad/s), selected curvature
sanity bound (±1/m), and control interval (2–100 ms). It rejects backward
model/measurement timestamps and invalid services. Repeated timestamps may
continue slew, but geometry is validated again on each tick. Disengagement,
invalid inputs and timing faults clear all command and adapter timing state.
The first valid tick after reset uses 10 ms, as v8 does.

controlsd still owns reference selection, upstream curvature limiting,
service health and engagement. Tests execute its actual source-selection
and limiter code, its Ford call, Float32 publication in ControlsExt, conversion
to CarControlSP, and the pinned Ford CarController's in-memory CAN builder.
Both model-action and maneuver-planner selection are covered, including
disabling latActive after invalid output. Only the test chooses the adapter.

Yaw is not an input to the control law. The adapter checks it solely for the
inherited invalid-input policy. Driver override and optional PSCM status
do not modify the candidate base; existing engagement and downstream driver
arbitration remain responsible for authorization, as with v8's base request.

## Offline evidence

The checked-in `ford_model_action_validation.json` records the completed
checks and source hashes. Full arrays and detailed reports are generated
locally under `.cache/ford_model_action/`; original route files are read-only.

Completed validation: **264 Ford tests and 150 subtests pass**, including
120 new core/adapter/replay-validator cases. The candidate module has 100%
statement and branch coverage (78 statements, 24 branches). Ruff and Ty pass.
The 200,000-cycle numerical stress test also checks 200,000 mirrored core
updates and 18,138 field-boundary cases. Across route and stress runs,
485,238 Float32/CAN round trips pass. Eight deliberately injected faults
(heading gain/cap, erased C0, wrong C0 slew, retained invalid state, stale
model acceptance, model clock rollback and reversed C0 sign) are all caught
by the tests. Mutation runs replace code only inside isolated Python
processes; production source files are never modified by those probes.

Independent Standards and Spec reviews reported zero findings. The full
suite's Params setting test uses an existing local native library from
worktree 3548 after checking relevant source files are byte-identical;
its hash and provenance are in the manifest. That library is an ignored
test dependency, not part of this change. This is the full relevant Ford
suite, not the hardware-dependent test suite for every openpilot subsystem.

The replay has two separate passes:

* Core compatibility uses the archived eligibility mask and requires exact
  equality with the independently implemented `action_heading` commands.
* Adapter reconstruction derives eligibility from recorded service streams
  independently of the archived output mask. It retains original timestamps,
  gaps and consumed model frames. Controls publication time proxies the
  unlogged computation clock, and complete SubMaster health is unavailable.

All 54,738 route95 and 78,812 route90 core cycles match exactly, including
37,614 and 73,055 active cycles. The adapter preserves those active counts.
Its 59 / 19 changed commands arise solely from the fresh 10 ms engagement
tick instead of the archived harness's preceding publication interval;
the replay checks that attribution on every cycle. Maximum differences are
0.01 m / 0.001 rad (95) and 0.02 m / 0.002 rad (90).

Every core and adapter replay output is round-tripped through Float32 and
the real CAN packer/parser, including zero C2/C3, signs, mode and counter.
Continuous field slew and quantization allowance are checked separately
from immediate invalid-command resets. The original driver-clean cohorts,
speed strata and command RMS are reproduced without redoing the encoder search.

The numerical stress harness uses analytic rotated paths, scalar slew
arithmetic, mirrored requests, irregular intervals and invalid-input resets.
It also sweeps every representable host field value and the Float32 values
immediately below, at and above every half-quantum boundary. Direct CAN
packing of the continuous state must agree with the host's quantized output.
The unit tests cover releases, reversals, clipping, service freshness,
clock resets, malformed inputs, endpoint fallback and actual integration.

## Limits of the result

On turns at ≥15 m/s, candidate C0 RMS is 79%/81% below v8 on routes95/90,
while C1 is 33%/41% higher. Those are command changes, not evidence of
equivalent steering authority. The PSCM's independent C0/C1 response remains
unknown. Replay cannot establish physical model following, strong turns,
centering, overshoot, oscillation or closed-loop stability.

The release probe is intentionally explicit: a model bend can increase
while selected curvature decreases. At 20 m/s, one synthetic probe changes
C0/C1 from 0.24 m / 0.10 rad to 0.49 m / 0.08 rad. Zero selected curvature
sets the C1 target to zero but does not erase a nonzero current model C0.
Removing a yaw-integral tail does not prove that physical overshoot is solved.
No additional release policy or unsupported plant model is added to hide
that uncertainty.

## Reproduce

From this worktree, use the logged construction dependency explicitly:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:/Users/ibpersonal/.codex/worktrees/b926/sunnypilot/opendbc_repo
PY=/Users/ibpersonal/dev/sunnypilot/.venv/bin/python
EVIDENCE=/Users/ibpersonal/.codex/worktrees/3548/sunnypilot/analysis/controller_search_20260904
$PY -m pytest -q -p no:cacheprovider openpilot/selfdrive/controls/tests/test_ford_*.py tools/ford_pscm_lab openpilot/selfdrive/car/tests/test_ford_pscm_status.py
$PY -m tools.ford_pscm_lab.model_action_replay "$EVIDENCE/route95" --output .cache/ford_model_action/route95
$PY -m tools.ford_pscm_lab.model_action_replay "$EVIDENCE/route90" --output .cache/ford_model_action/route90
$PY -m tools.ford_pscm_lab.stress_model_action --cycles 200000 --seed 20260907 --output .cache/ford_model_action/stress.json
```

The route replay refuses an opendbc revision other than
`72a775d35e54c21ff5c5798acef22016eedcc0a7`. Stress defaults to this pin and
also accepts an explicitly required commit with `--opendbc-revision` for
deployment checks. A mismatch still fails. This historical pin reproduces
logged construction; it does not change the merge's submodule pointer.
