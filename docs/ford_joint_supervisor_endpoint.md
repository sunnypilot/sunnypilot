# Ford joint endpoint: hold C0 at the supervisor saturation

The equal-arrival endpoint (`C0 = 1.5 t`, `C1 = 0.1 t`) holds 2-4 m of C0 in large
turns. In the reference ML3V-14D003-BD / ML34-14D007-EDL calibration the path
supervisor centre is

```
S(v) * (clip(0.5 * held_C0, +-0.5) + clip(10 * held_C1, +-0.349609))
```

with width `0.399994 * S + 5` below 40 km/h. Its C0 term saturates at 1.0 m, so
held C0 above that adds primary curvature but no turn-direction allowance. On
release, zero demand stays excluded until held C0 slews (1.5 m/s) below about
0.41 m while C1 is saturated, so extra C0 adds (C0 - 0.41) / 1.5 s of forced
old-direction output.

`static_pair` therefore caps its equal-arrival C0 at 1.0 m and gives the rest to
C1; the remainder returns to C0 only when C1 reaches its bound. Endpoints with
equal-arrival C0 of at most 1.0 m are unchanged. The paired selector, dynamics,
quantization, preview, gates, stop hold and DBC bounds are unchanged; it still
builds with both fields, then trades C0 for C1 at constant curvature.

Offline evidence (reference firmware, not the live RL38 calibration; no wheel,
assist or vehicle model):

- Native zero-demand supervisor probe, controlled 15/20/25 km/h large steps:
  zero excluded after release 1.48/1.88/2.17 s -> 0.39/0.39/0.48 s. The first
  50%/90% of the rise is unchanged; the last 1% can settle up to 0.5 s later.
- Native probe on replayed routes 194/195/196 packets: forced old-direction
  output in the 3 s after large releases 24.9 -> 6.4, 19.6 -> 8.4,
  15.0 -> 3.6, 16.6 -> 8.3, 11.0 -> 4.4 unit*s (one driver-involved release
  9.6 -> 9.2).
- 81,340 replay updates per policy: with no |target| >= 30 deg within 10 s,
  packets are identical on 194/196 and 98.9% identical on 195.

These are firmware-stage predictions. A physical A/B must show whether the wheel
releases large turns earlier; diagnostics report `allocation:
equal-arrival-supervisor-c0`.
