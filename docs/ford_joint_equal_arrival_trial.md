# Ford coordinated allocation trial

The existing `FordModelActionController` + `FordPscmJointControl` gate now uses
the recovered normal C0/C1 slew rates to choose its steady endpoint split:

```
t = desired_internal_curvature / (g0 * c0_rate + g1 * c1_rate)
c0 = t * c0_rate
c1 = t * c1_rate
```

When a field clips, allocate its missing contribution to the other field's
remaining capacity. The existing dynamic selector still handles held state,
heading-dependent filtering, target preview and release. No new gain, control
mode, search horizon or native-library ABI is added. DBC bounds and C2=C3=0 remain.
The normal upstream controller is unchanged with the existing master toggle off.

This is the exact endpoint policy tested against ML3V-14D003-BD /
ML34-14D007-EDL instructions. At 18 mph, the approximately 204-degree internal
target settles within 2.5 degrees in 2.864 rather than 3.384 seconds. The first
90% of its rise is unchanged. The approximately 25-degree release takes .624
rather than .456 seconds to settle: this is a known trial tradeoff, not a proven
improvement in all driving. These are internal target results, not wheel-motion
or closed-loop smoothness predictions. Actual steering feedback must assess both
large turns and ordinary correction/release.

For stopping, controlsd and card share the same normalization: a filtered speed
between -0.3 and 0 m/s counts as zero only when raw speed is in [0, 0.3) m/s and
reverse is not selected. This prevents small speed-filter undershoot from
invalidating and clearing the last active packet. Larger/inconsistent negative
speeds, reverse, stale inputs, faults, override and disengagement still release.
No global CarState speed or PSCM speed message is altered. Retaining the request
does not bypass the firmware's separate near-zero-speed output gate.

Validation: 926 Ford tests and two subtests passed; lint and diff checks passed.
The shipped encoder reproduces all 9,000 saved candidate command samples from
the native-verified step/release fixture (maximum difference 8.89e-16). Native
instruction validation and the underlying fixtures are recorded in the local
PSCM authority report. Diagnostics include `allocation: equal-arrival`.
