# Ford continuous PI drive trial (v7)

The selected controller follows the current, upstream-limited desired curvature
with P=0.50 and I=0.25. It replaces v6's request-change, C0-confirmation and
unwind-catchup release rules. C0 mapping, heading overflow allocation, input
health gates, driver/PSCM arbitration and final output limits remain unchanged.
Only C0, C1 and I carry control history. C2/C3 stay zero.

```text
D = max(7 m, speed × 1 s)
error = selected desired curvature − measured steering-derived curvature
base = clip(D × desired curvature, −0.5, +0.5)
P = 0.50 × D × error
increment = 0.25 × speed × error × fresh steering measurement interval
C1 target = clip(base + P + I, −0.5, +0.5)
```

After PSCM outward-accumulation arbitration, the increment first cancels up to
its own magnitude of opposing I. It cannot cross zero in that step. Any remainder
is bounded by the combined command's amplitude/slew headroom. C1 output still
slews at 0.5 rad/s. This allows old I to unwind even when the output is already
slewing. It adds no timer, request history, turn detection or position threshold.

P doubles relative to v6, and I builds at one quarter the previous rate for an
identical error and fresh measurement interval. Lower I also unwinds more slowly
for an identical existing state and error; its replay benefit comes mainly from
storing less correction. Zero error removes P and holds I. Persistent tracking
bias may need that holding correction. There is no claim that all I is unwanted.

## Evidence and limitations

Six offline settings were compared across fourteen routes and 1,578,250 source
cycles before selecting this candidate. The production selector and adapter now
exactly reproduce the selected P=0.50/I=0.25 archived commands, validity, P, I,
feedforward, C0 overflow and feedback/PSCM gates on every cycle of all fourteen
routes. These comprise Lightning 112–117, a0, a2, a5, a9, b8, b9, ca and Raptor 02.
The integration replay performs 1,578,250 actual Float32/CAN round trips.

A further 20,000 randomized cycles with mirrored and independent C0 paths perform
60,000 CAN checks on production, checking independent scalar arithmetic,
C0-independent feedback, symmetry, reset, amplitude and slew behavior.
The Ford, Sunnylink, params, sender and safety suite passes 679 tests and
9,145 subtests; 178 are skipped by the platform test suite. Removed maneuver
heuristic tests are replaced with continuous-error, cancellation, freshness,
three-state reproduction and actual controlsd-to-CAN entry/exit checks.
Historical untracked offline experiment tests are outside this deployment suite.

At a previously reviewed route-115 exit (133.595 s), the original small PI
controller requested +0.1090 rad C1; this trial requests +0.0175. That sample
includes driver context. Reviewed large entries remain similar, but commands
are not identical everywhere. In a previously well-tracked route-116 bend
(112 s), C1 falls from +0.1530 to +0.1355 rad. Lower I could weaken a persistent
bend, while higher P can increase response to measurement fluctuations.

Recorded wheel motion remains fixed in replay. These checks establish software
behavior and exact integration of the candidate; they do not establish improved
physical tracking or stability. Gains remain experimental, not an identified
universal PSCM calibration. No device build, boot or new drive is claimed.

## Selection and reproduction

Use the existing default-off Sunnylink **Selected-Action Path Tracking
(Experimental)** toggle on any Ford CAN FD, followed by a real offroad-to-onroad
cycle. Logs identify `model-action-c1-pi-v7`, `proportional_gain=0.5`,
`integral_gain=0.25`. Toggle-off selects upstream Ford control. See the
[drive instructions](ford_model_action_drive_test.md).

With the built cereal/opendbc environment and archived local extracts:

```sh
export PYTHONPATH=.:opendbc_repo:.cache/ford_v6/test_deps
export PYTHONDONTWRITEBYTECODE=1
export PARAMS_ROOT=/tmp/ford-v7-params
export LOG_ROOT=/tmp/ford-v7-logs
python -m tools.ford_pscm_lab.minimal_pi_validate --output .cache/ford_minimal_tuning/production --workers 4
python -m tools.ford_pscm_lab.minimal_pi_production_stress --cycles 20000 --output .cache/ford_minimal_tuning/production_stress.json
```

The validation JSON records route and source hashes. The archived six-setting
sweep is local evidence, not a checked-in dataset. Historical v5/v6 lab tools
load their pinned controller revisions so their baseline comparisons retain
their original meaning after production changes.
