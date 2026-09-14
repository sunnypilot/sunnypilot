# Ford direct C0/C1 requests — v9

The v8 maneuver route `84865544361f55cb/0000011c--99f4537696` showed
commands being delayed by our extra 4 m/s C0 and 0.5 rad/s C1 slews.
Those values were controller choices, not measurements of the PSCM's limits.
For example, a C1 target reversal from +0.10 to -0.10 rad required at least
0.4 seconds in our output stage alone.

V9 sends the current bounded C0 and C1 requests on each update. There is no
additional actuator ramp, zero hold, reversal mode, or initial engagement ramp.
C0 remains the selected-curvature arc at 7 m plus base-C1 overflow. C1 remains
base heading plus proportional and integral feedback, with P=0.50 and I=0.25.
These are calculated commands, not a known inverse of the PSCM's response.

Integral cancellation happens first. New integral accumulation fits the
combined command's magnitude headroom, rather than the old slew headroom.
This removes a second dependence on the old ramp. Fresh-measurement cadence,
driver override, PSCM arbitration, stale/invalid input reset, and C2/C3=0 remain.

The default-off Sunnylink `FordModelActionController` selector still applies
to any Ford CAN FD vehicle. Toggle off restores upstream Ford control.
Logs identify `model-action-direct-c0-c1-pi-v9`.

## Remaining bounds

- Selected desired curvature still passes through upstream `clip_curvature`:
  3 m/s² lateral acceleration adjusted for roll, 5 m/s³ lateral jerk, and
  absolute curvature 0.2 m⁻¹. These bound the reference; they are not proof of
  a physical acceleration or jerk bound under custom C0/C1 feedback.
- C0 remains within ±5.11 m and C1 within ±0.50 rad. The downstream packer
  retains the actual wire ranges, preventing out-of-range values wrapping.
- Driver, CAN, timing, service health, and fault gates remain intact.
- Panda safety, the 100 Hz sender, and ramp-type selection are unchanged.

No assumption is made that extended path mode independently enforces ISO
limits. The absence of `LimitReached` is not evidence of unrestricted authority.

## Offline validation

The same-cycle reversal regression failed on v8 in both directions at 2, 10,
and 100 ms timesteps, then passed after the change. Zero-error release reaches
zero immediately. Full controlsd/publication/CAN tests check current-request
output, upstream reference selection, field packing, driver and PSCM gates,
integral cancellation and anti-windup, invalid input, and toggle-off fallback.

- 358 tests and 23 subtests passed across controller and Ford sender suites.
- 20,000 seeded randomized cases produced 60,000 controller updates and CAN
  round trips, checking independent arithmetic, symmetry, bounds and resets.
- Routes 11c, 119 and 11a supplied 461,340 input cycles: 922,680 baseline/v9
  controller updates and CAN round trips. V8 and v9 activation, feedforward,
  proportional feedback and feedback gates matched. Every active v9 output
  matched its current bounded request within wire quantization.
- Ruff passed for changed production/tests and the new replay/stress tools.

| Route | Input cycles | Maximum C0 difference | Maximum C1 difference |
|---|---:|---:|---:|
| 11c maneuver suite | 54,146 | 0.09 m | 0.1605 rad |
| 119 | 171,423 | 2.42 m | 0.4950 rad |
| 11a | 235,771 | 3.36 m | 0.3710 rad |

The maximum differences include engagement and other transitions. Removing
slews permits abrupt changes; these are not predictions of wheel motion.
Recorded motion, driver input and PSCM feedback stay fixed in replay.
Publication timestamps approximate computation time; replay is not a claim of
exact onroad command parity. Synthetic reference freshness is approximated
from valid maneuver publications. Physical tracking and stability are unvalidated.

The reproducible tools are `tools/ford_pscm_lab/direct_path_replay.py` and
`tools/ford_pscm_lab/direct_path_production_stress.py`. Machine-readable checks
are collected in `ford_direct_path_v9_validation.json`.
