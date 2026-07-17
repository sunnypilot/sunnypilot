# Hyundai 3A5-3C4 radar signal notes

This document tracks the evidence behind the 24-byte `RADAR_3A5_3C4` layout.
It deliberately separates a signal being active from its meaning being known.
The cross-family and per-platform investigation plan lives in
[RADAR_RESEARCH.md](RADAR_RESEARCH.md).

## Status terms

- **Confirmed core**: populated across compatible platforms and its meaning is
  supported by position, motion, or lifecycle behavior.
- **Optional useful**: meaning is supported, but many platforms transmit a
  default value instead of the signal.
- **Active unknown**: the field changes consistently, but its meaning is not
  established well enough to use.
- **Redundant**: understood, but duplicates a better primary field.
- **Reserved/dead**: remained zero across the tested raw frames.

An optional field that is dead on one platform is not globally dead.

## Evidence corpus

- The original layout was checked against 817,852 frames from 21 forum routes.
- The documented route corpus was expanded to 107 route/segment entries:
  all 36 canonical Hyundai/Kia CAN-FD test routes plus the forum radar and
  consecutive-range route lists. A qlog pre-screen identified candidates
  carrying 24-byte 3A5 traffic, then full rlogs were used for layout decisions.
- The combined full-rlog pass contains 24 compatible route segments and
  492,679 active (`STATE` 3/4) observations. Fourteen segments are HDA2 and ten
  are HDA1. The compatible set covers every architecture combination:
  HDA1/HDA2 and CCNC/non-CCNC.
- Full geometry/kinematics data was populated only by EV9 and Ioniq 9. Both
  are HDA2 + CCNC, but HDA2 + CCNC Kona EV, EV6 2025, and K4 routes left those
  fields at their unavailable defaults. A second Ioniq 9 segment independently
  reproduced the rich extension.
- The 36 canonical CAN-FD test routes contributed eight compatible 3A5
  segments and 150,489 active observations. This independently reproduced the
  layout on HDA1 and HDA2 cars.
- An additional eight-segment local recording supplied 89,233 active track
  observations. Its replay fingerprint is unavailable, so it is used for
  layout/range evidence but not platform attribution.
- The known reserved bits were rechecked across 320,454 additional K5 and
  local-recording frames; all remained zero.
- The Sportage HEV 2026 forum route has an incompatible overlapping layout and
  is excluded from this matrix.

## Signal matrix

| Signal | Status | Availability and evidence |
| --- | --- | --- |
| `CHECKSUM` | Active unknown | A 16-bit per-track checksum. Useful once its algorithm and data ID are known. |
| `COUNTER` | Confirmed core | Global transmit-cycle counter covering 0-255 and wrapping. |
| `STATE_ALT` | Redundant | Exact compressed mirror in all 325,110 active samples: `STATE=3 -> 2`, `STATE=4 -> 3`. |
| `MOTION_STATE` | Confirmed core | Ground-frame class: unknown, stationary, or moving. Correctly marked observed crossing traffic as moving. |
| `TRACK_COUNTER` | Confirmed core | Modulo-4 per-track update counter. Separate from the transmit counter. |
| `NEW_SIGNAL_2` | Active unknown | Signed value from -64 to 63. Active on every sampled platform, but correlations with age, distance, and velocity are inconsistent. |
| `AGE` | Confirmed core | Per-track update age, 0-255. |
| `COAST_AGE` | Confirmed core | Zero for measured tracks and increments while a track is coasted/predicted. |
| `STATE` | Confirmed core | Track lifecycle: empty, tentative, measured, coasted, or unresolved tentative. |
| `NEW_SIGNAL_8` | Active unknown | Smooth signed attribute observed from -33 to 43. Return-strength/RCS-like behavior remains plausible but unproven. |
| `LONG_DIST` | Confirmed core | Longitudinal target distance in meters. |
| `LAT_DIST` | Confirmed core | Lateral target position relative to the ego axis in meters. |
| `REL_SPEED` | Confirmed core | Longitudinal target speed relative to ego. |
| `NEW_SIGNAL_4` | Active unknown | Category 0-2. Nonzero in about 25% of moving samples, 10% of stationary samples, and 6% of unknown samples; it is related to target state but is not another motion class. |
| `REL_LAT_SPEED` | Confirmed core | Lateral target speed relative to the ego axis. A live crossing target showed `+6.78 m/s` lateral versus `-0.51 m/s` forward. An EV9 route independently supplied hundreds of perpendicular-motion samples. |
| `REL_ACCEL` | Confirmed core | Longitudinal target acceleration relative to ego. |
| `NEW_SIGNAL_18` | Optional active unknown | A lifecycle/measurement-status attribute on rich layouts. In the public EV9/Ioniq 9 data, values 1/2 occur almost exclusively while `STATE=3` is measured and 0 while `STATE=4` is coasted; one anomalous coasted sample retained 2. The distinction between 1 and 2 is unknown. Most platforms always send 0, and a compatible long recording contains the rare value 3. |
| `NEW_SIGNAL_5` | Optional active unknown | Sparse value observed from 0 to 32 on both HDA1 and HDA2 routes, including platforms without rich geometry. No stable correlation is known. |
| `WIDTH` | Optional useful | Target width in 0.1 m units. Populated on EV9/Ioniq 9; passenger-car values cluster around 1.8-2.0 m. Zero means unavailable on other sampled platforms. Every address in 3A5-3C4 can carry it, so it does not identify a separate track bank. |
| `LENGTH` | Optional useful | Target length in 0.1 m units. Passenger cars cluster around 4 m and long vehicles reach roughly 13-15.5 m. It is available on the same target samples as `WIDTH`. |
| `ABS_SPEED` | Optional useful | Absolute target-speed magnitude. On Ioniq 9 it matches `hypot(vEgo + REL_SPEED, REL_LAT_SPEED)` with about 0.08-0.15 m/s median error. It was populated for 28,735/28,860 active Ioniq 9 samples and 23,252/27,339 EV9 samples, including many targets without dimensions. Zero is the platform default when unsupported. |
| `ORIENTATION_ANGLE` | Optional useful | Target orientation relative to the ego axis. Ioniq 9 follows motion heading within roughly 2 degrees median; EV9 crossing traffic rotated from about -45 to -83 degrees. It is associated with dimension-bearing targets. `+/-180` is unavailable/default; compatible non-rich platforms consistently use +180. |
| `NEW_SIGNAL_13` | Optional active unknown | Shape/geometry metadata from 0-10. It was nonzero only on dimension-bearing targets in the EV9/Ioniq 9 routes. Confidence-like behavior is plausible but not established. |
| `NEW_SIGNAL_12` | Optional active unknown | Shape/geometry metadata from 0-10. It was nonzero only on dimension-bearing targets; values 10 and 0 dominate. Exact meaning is unknown. |
| `NEW_SIGNAL_14` | Optional active unknown | Shape/geometry category 0-3. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_15` | Optional active unknown | Shape/geometry category 0-2. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_16` | Optional active unknown | Shape/geometry category 0-3. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_17` | Optional active unknown | Shape/geometry category 0-2. It is zero when the associated geometry metadata is unavailable. The most common rich-layout `14/15/16/17` tuple is `2/2/2/1`. |

## Platform and cluster conclusions

| Architecture | Compatible examples | Rich geometry |
| --- | --- | --- |
| HDA2 + CCNC | Kona EV 2, EV6 2025, K4, EV9, Ioniq 9 | EV9 and Ioniq 9 only |
| HDA2 + non-CCNC | Ioniq 6, Niro EV 2, Carnival HEV | None observed |
| HDA1 + CCNC | Kona 2/HEV, Sonata/HEV, K4, K5, Santa Fe 5 | None observed |
| HDA1 + non-CCNC | Niro EV 2/HEV | None observed |

- HDA2 changes the normal 3A5 bus from bus 1 to bus 0, but does not imply
  rich extension support.
- EV6 2025 carried a complete 3A5 range on buses 0 and 2. The bus-2 subset was
  a 99.6% exact byte-for-byte subset of bus 0, consistent with forwarding
  rather than a second radar. The runtime selects one active bus per range.
- The optional bytes are attributes on the same 32 addresses, not extra
  objects. Dimension-bearing targets appeared throughout 3A5-3C4 rather than
  in a dedicated address subset.
- Stock `CCNC_0x162` is a separate fused cluster-object output. Two HDA2 +
  CCNC Kona EV routes exercised lead, left/right, and both rear slots while
  every 3A5 width/length/absolute-speed/shape field remained unavailable.
  Rear-slot distance capped at 20 m and the stock lateral value was fixed at
  3.0 m. `LEAD_ALT` remained hidden in both sampled segments.
- Therefore, the additional cluster tofus are real stock CCNC/ADAS outputs,
  but they cannot be reconstructed merely by reading the 3A5 rich extension.
  Rear tofus in particular need a source beyond the forward 3A5 radar.

## Reserved/dead bits

Bits `26`, `29`, `39`, `55`, `117`, `136-137`, `143`, `171`, and
`188-191` remain zero. No new signal location was found in the follow-up
routes.

## Parser guidance

- Detect support per radar source instead of treating extension defaults as
  real measurements.
- Treat zero dimensions and `+/-180` orientation as unavailable.
- Do not use any `NEW_SIGNAL_*` field for control or filtering until its
  meaning is independently validated.
- `REL_LAT_SPEED` is suitable for debugging cross traffic, but a production
  cross-traffic filter still needs lane-change validation and track history.
