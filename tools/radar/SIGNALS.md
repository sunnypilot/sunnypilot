# Hyundai radar, camera-object, and auxiliary signal notes

This document tracks the evidence behind the 24-byte `RADAR_3A5_3C4` layout
and its shared signal semantics with the 32-byte `RADAR_210_21F` layout.
It also records the now-identified `0x235–0x248` camera objects and the
research-only corner and raw-detection families. It deliberately separates a
signal being active from its meaning being known.
The cross-family and per-platform investigation plan lives in
[RADAR_RESEARCH.md](RADAR_RESEARCH.md).
The forum-ready platform/range summary lives in
[PLATFORM_MATRIX.md](PLATFORM_MATRIX.md).

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
- The 3A5 checksum was rechecked on all 817,852 frames and matched the HKG
  CAN-FD checksum with the CAN address as data ID, with zero failures.
- All 726 advertised 210-route segments were scanned across 20 unique routes:
  16 routes had active targets, three had complete but empty streams, and one
  non-HDA2 Telluride route had no 210 stream. The 16 active routes split evenly
  between detailed and compact dialects, with no third active layout.
- The 210 HKG checksum matched all 13,210,543 checked frames.
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
- A downloaded Hyundai DBC archive supplied two related but non-bit-compatible
  object layouts. The BN7 front-radar DBC defines a persistent global object
  ID and `0/1/2/3 = unknown/stationary/moving/stopped`; the HMVS4 object DBC
  independently defines value 3 as stopped, a 7-bit quality level, and alive
  age/lifetime. Neither DBC directly contains the 210 or 3A5 radar layout.
- The same archive's `FR_CMR_Obj` definition matches the first 124 bits of
  `0x235–0x248` exactly. Together with its 33 Hz cadence and co-location with
  `0x360–0x366`, this corrects the former corner-radar classification:
  `0x235–0x248` is a forward-camera object list.
- The repository's Delphi `ESR.dbc` exactly matches the `0x500–0x53F` target
  packing and the 64-slot radar's `0x4E0/0x4E1/0x4E3` status packing. A fresh
  six-route full-segment check covered two 64-slot and four 32-slot variants.
  `0x4E0` radar speed correlated with `carState.vEgo` at 0.9976–0.99996 with
  0.02–0.19 m/s mean absolute error. Both 64-slot variants acknowledged 64
  tracks in `0x4E1`; the four 32-slot payloads decoded as 1, proving that
  their `0x4E1` uses a different dialect.

## 500-53F legacy front-radar layout

Every eight-byte message is one target slot. The lower 32 slots
`0x500–0x51F` are required; some radar variants add an identically packed
upper bank at `0x520–0x53F`. Inter-arrival timing on all six freshly checked
full segments is about 50 ms, confirming the established 20 Hz cadence. A gap
inside these logs makes frame count divided by total segment span misleading.

| Signal | Start bit | Size | Scale / offset | Status |
| --- | ---: | ---: | --- | --- |
| `UNKNOWN_1` | 7 | 8 signed | raw | Preserve on 32-slot variants. Its low bits are active but do not behave like ESR target flags. |
| `ONCOMING_ESR` | 0 | 1 | boolean | 64-slot only. Every flagged target in both full-segment checks had negative ground-frame speed. Clear does not distinguish stationary from same-direction moving. |
| `GROUPING_CHANGED_ESR` | 1 | 1 | boolean | 64-slot ESR identity; exact tracker behavior remains to be correlated. |
| `REL_LAT_SPEED_ESR` | 7 | 6 signed | 0.25 / 0 m/s | 64-slot ESR lateral target rate. It is not published for 32-slot variants. |
| `AZIMUTH` | 12 | 10 signed | 0.1 / 0 deg | Corrected from the former 0.2-degree scale. Lateral projection now uses the angle directly rather than a compensating half-scale. |
| `STATE` | 15 | 3 | enum | Track lifecycle; values 3 and 4 are the measured/coasted valid states used by the parser. |
| `LONG_DIST` | 18 | 11 | 0.1 / 0 m | Target range. |
| `REL_ACCEL` | 33 | 10 signed | 0.02 / 0 m/s² | 32-slot dialect scale retained from route behavior. |
| `REL_ACCEL_ESR` | 33 | 10 signed | 0.05 / 0 m/s² | 64-slot ESR scale. Separate overlapping names prevent applying it to the 32-slot dialect. |
| `WIDTH_ESR` | 37 | 4 | 0.5 / 0 m | 64-slot ESR target width. It was populated on both checked 64-slot routes and identically zero on all four 32-slot routes. |
| `COUNTER` | 38 | 1 | 1 / 0 | Per-target rolling count. |
| `BRIDGE_OBJECT_ESR` | 39 | 1 | boolean | 64-slot ESR identity; exact tracker behavior remains to be correlated. |
| `REL_SPEED` | 53 | 14 signed | 0.01 / 0 m/s | Radial range rate. |
| `MED_RANGE_MODE_ESR` | 55 | 2 | enum | 64-slot ESR medium-range operating-mode field. |

### 4E0-4E5 companion messages

`0x4E0` has the shared ESR status layout on both 32- and 64-slot variants:

| Signal | Start bit | Size | Scale / offset |
| --- | ---: | ---: | --- |
| `DSP_TIMESTAMP` | 5 | 7 | 2 / 0 ms |
| `GROUP_COUNTER` | 6 | 2 | 1 / 0 |
| `COMM_ERROR` | 14 | 1 | boolean |
| `RADIUS_CURVATURE` | 13 | 14 signed | 1 / 0 m |
| `SCAN_INDEX` | 31 | 16 | 1 / 0 |
| `YAW_RATE` | 47 | 12 signed | 0.0625 / 0 deg/s |
| `VEHICLE_SPEED` | 50 | 11 | 0.0625 / 0 m/s |

The 64-slot variant exactly matches ESR Status2 at `0x4E1`. On 32-slot
variants only its low two-bit rolling counter is active; the other 62 bits
are platform-static and do not acknowledge 32 tracks, so the ESR Status2
names remain 64-slot-only. The `0x4E3` in-path path-ID bytes are shared across
both variants, while its low status flags, counter, range mode, and alignment
angle are confirmed only on the 64-slot variant.

| `0x4E1` 64-slot signal | Start bit | Size | Scale / offset |
| --- | ---: | ---: | --- |
| `GROUP_COUNTER` | 1 | 2 | 1 / 0 |
| `MAXIMUM_TRACKS_ACK` | 7 | 6 | 1 / 1 |
| `STEERING_ANGLE_ACK` | 10 | 11 | 1 / 0 deg |
| `RAW_DATA_MODE`, `TRANSCEIVER_OPERATIONAL`, `INTERNAL_ERROR`, `RANGE_PERFORMANCE_ERROR`, `OVERHEAT_ERROR` | 11–15 | 1 each | boolean |
| `TEMPERATURE` | 31 | 8 signed | 1 / 0 °C |
| `GROUPING_MODE` | 33 | 2 | 1 / 0 |
| `VEHICLE_SPEED_COMP_FACTOR` | 39 | 6 signed | 0.00195 / 1 |
| `YAW_RATE_BIAS` | 47 | 8 signed | 0.125 / 0 deg/s |
| `DSP_SOFTWARE_VERSION` | 55 | 16 | 1 / 0 |

| `0x4E3` signal | Start bit | Size | Scale / offset |
| --- | ---: | ---: | --- |
| `GROUP_COUNTER` | 1 | 2 | 1 / 0; 64-slot confirmed |
| `MEDIUM_LONG_RANGE_MODE` | 3 | 2 | 1 / 0; 64-slot confirmed |
| `PARTIAL_BLOCKAGE`, `SIDELOBE_BLOCKAGE`, `LONG_RANGE_GRATING_LOBE_DETECTED`, `TRUCK_TARGET_DETECTED` | 4–7 | 1 each; 64-slot confirmed |
| `ACC_MOVING_PATH_ID` | 15 | 8 | one-based target slot; shared |
| `CMBB_MOVING_PATH_ID`, `CMBB_STATIONARY_PATH_ID` | 23, 31 | 8 each | one-based target slots; shared |
| `FCW_MOVING_PATH_ID`, `FCW_STATIONARY_PATH_ID` | 39, 47 | 8 each | protocol-defined; unexercised on sampled 32-slot routes |
| `AUTO_ALIGN_ANGLE` | 55 | 8 signed | 0.0625 / 0 deg; 64-slot confirmed |
| `ACC_STATIONARY_PATH_ID` | 63 | 8 | one-based target slot; shared |

All 7,347 nonzero `0x4E3` path-ID observations across the four 32-slot routes
referenced an active `0x500–0x51F` target slot. IDs reached 32, proving
one-based indexing. ACC and CMBB moving selectors commonly referenced the
same slot, as did their stationary selectors.

The 32-slot variants additionally send `0x4E2`, `0x4E4`, and `0x4E5`:

- `0x4E2` consistently encodes plausible BCD build timestamps across all four
  sampled platforms.
- `0x4E4` matches the byte order and address-shifted envelope of Delphi ESR
  Status5: switched-battery, ignition, two temperature, and four supply ADC
  channels. The identities are protocol-derived and the raw ADC values are
  intentionally uncalibrated; they must not drive a health decision.
- `0x4E5` matches the similarly relocated ESR Status6 alignment payload. In
  4,698 checked frames its two factory-alignment fields used only documented
  enum values 0–3. The other flags and alignment-value bytes remained zero,
  so their identities are protocol-derived but not independently exercised.

Although generic ESR defines eight-byte input messages at `0x4F0/0x4F1`, no
such messages were present on these source buses. The observed Hyundai
`0x4F1` was four bytes on other/forwarded buses and is not assigned the ESR
input schema.

## Signal matrix

| Signal | Status | Availability and evidence |
| --- | --- | --- |
| `CHECKSUM` | Confirmed core | 16-bit HKG CAN-FD checksum using the CAN address as data ID. It matched all 817,852 checked 3A5 frames. |
| `COUNTER` | Confirmed core | Global transmit-cycle counter covering 0-255 and wrapping. |
| `STATE_ALT` | Redundant | Exact compressed mirror in all 325,110 active samples: `STATE=3 -> 2`, `STATE=4 -> 3`. |
| `MOTION_STATE` | Confirmed core | Ground-frame class: unknown, stationary, or moving. Correctly marked observed crossing traffic as moving. Related Hyundai radar data assigns the unused fourth 2-bit value to stopped, not oncoming; that bit remained zero throughout the tested 3A5 corpus. |
| `TRACK_COUNTER` | Confirmed core | Modulo-4 per-track update counter. Separate from the transmit counter. |
| `TRACK_QUALITY` | Confirmed core | Unsigned 7-bit track quality/existence score. Empty and tentative tracks are low, measured tracks are high, and coasted tracks decline with `COAST_AGE`. A related Hyundai object layout describes its 7-bit quality level as reliability, validity, or probability evidence; the radar's raw scale is not confirmed to be a percentage. |
| `AGE` | Confirmed core | Per-track alive age/lifetime count, 0-255. |
| `COAST_AGE` | Confirmed core | Zero for measured tracks and increments while a track is coasted/predicted. |
| `STATE` | Confirmed core | Track lifecycle: empty, tentative, measured, coasted, or unresolved tentative. |
| `RCS` | Confirmed core | Signed radar cross-section/return-strength value. At controlled distances its median consistently increases from small to passenger to large targets. The raw unit is not calibrated. |
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
| `ORIENTATION_ANGLE` | Optional useful | Target orientation relative to the ego axis. Ioniq 9 follows motion heading within roughly 2 degrees median; EV9 crossing traffic rotated from about -45 to -83 degrees. It is associated with dimension-bearing targets. Values near `+/-180` can represent real rearward orientation on rich tracks, while compatible non-rich platforms consistently use +180 as unavailable/default. |
| `NEW_SIGNAL_13` | Optional active unknown | Shape/geometry metadata from 0-10. It was nonzero only on dimension-bearing targets in the EV9/Ioniq 9 routes. Confidence-like behavior is plausible but not established. |
| `NEW_SIGNAL_12` | Optional active unknown | Strong geometry-age/maturity candidate. Two independent Ioniq 9 routes progressed `0 -> 1 -> 2 -> ... -> 10` and saturated at 10. It remains unnamed pending confirmation on another rich platform. |
| `NEW_SIGNAL_14` | Optional active unknown | Shape/geometry category 0-3. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_15` | Optional active unknown | Shape/geometry category 0-2. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_16` | Optional active unknown | Shape/geometry category 0-3. It is zero when the associated geometry metadata is unavailable. |
| `NEW_SIGNAL_17` | Optional active unknown | Shape/geometry category 0-2. It is zero when the associated geometry metadata is unavailable. The most common rich-layout `14/15/16/17` tuple is `2/2/2/1`. |

## Cross-family layout and naming findings

Both families expose 32 tracks at approximately 20 Hz per address:

| Layout | Envelope | Tracks per message | Shared core | Family-specific extension |
| --- | --- | --- | --- | --- |
| 210 detailed | `0x210-0x21F`, 32 bytes | 2 | State, motion, quality, age/coast age, RCS, range, relative velocity/acceleration | Detailed state/RCS/category are populated; compact object-ID bytes are normally zero |
| 210 compact | `0x210-0x21F`, 32 bytes | 2 | Same bit positions and scales except for the documented lateral-speed sign convention | Uses `STATE_ALT`, per-target status and persistent 6-bit `OBJECT_ID`; detailed state/RCS/category remain zero |
| 3A5 common | `0x3A5-0x3C4`, 24 bytes | 1 | Homologous first 16 bytes | Bytes 16-23 carry measurement status and optional dimensions, absolute speed, orientation, and geometry metadata |

The shared signal conclusions are:

- The old signed `NEW_SIGNAL_2` decoding was wrong. Raw values use 0-99 in the
  tested corpus, and the signed interpretation created an artificial wrap at
  63/64. The standardized name is `TRACK_QUALITY`, unsigned 7-bit.
- Detailed 210 and 3A5 `TRACK_QUALITY` distributions are nearly identical.
  Compact 210 uses a higher calibration, commonly around 70 while measured,
  that falls toward the low 20s at long coast ages. The semantic name is
  shared, but no percentage unit is assigned.
- The old `NEW_SIGNAL_8` is standardized as `RCS`. Detailed 210 and 3A5 have
  closely matching distributions, and size ordering is preserved within every
  tested distance band. 210 supplies eight signed bits; 3A5 supplies seven
  because the remaining bit extends `LONG_DIST` from 12 to 13 bits.
- `NEW_SIGNAL_4` occupies the same physical two bits and has nearly identical
  0-2 distributions in detailed 210 and 3A5, but its exact category remains
  unknown.
- Compact 210 `OBJECT_ID` remains strongly supported: it held through 99.9%
  of consecutive same-track updates and changed when a slot acquired a
  replacement target. A related Hyundai BN7 radar DBC independently defines
  `ObjectId` as a global ID that remains constant while an object is tracked.
  Sparse 3A5 `NEW_SIGNAL_5` does not behave like the same field and remains
  unknown.

## Oncoming classification

Oncoming candidates were cross-checked using fresh ego speed and
`vEgo + REL_SPEED < -3 m/s`.

| Layout | Evidence | Conclusion |
| --- | --- | --- |
| 210 compact | Motion code 4 appeared on 4,870 active rows. Synchronized code-4 rows had -13.30 m/s median ground-frame longitudinal speed, with 3,516 strong oncoming candidates. Related Hyundai BN7 radar and HMVS4 object DBCs independently label motion value 3 as stopped. | `MOTION_STATE=3` is stopped and `MOTION_STATE=4` is the compact oncoming class. |
| 210 detailed | Bit 29 never set across 317,965 active rows. Its 4,924 physics-based candidates remained in motion values 0-2. | No dedicated detailed-210 oncoming value. |
| 3A5 common | Bit 29 remained zero in all 817,852 frames. Among 6,104 physics-based candidates across 14 routes, motion was 0 for 5,792, 1 for 312, and never 2. | No dedicated 3A5 oncoming value or flag. |

`NEW_SIGNAL_4` and `NEW_SIGNAL_18` also failed to isolate the 3A5 oncoming
candidates. Do not widen 3A5 `MOTION_STATE` to three bits. If oncoming
classification is needed for 3A5 or detailed 210, derive it from ego-relative
kinematics with persistence, hysteresis, and lane plausibility.

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

## 235-248 forward-camera object layout

Each 32-byte message is one camera-object slot. `OBJECT_ID=0` is unused in the
observed routes. The production parser normalizes the native camera motion
enum to the shared `unknown/stationary/moving` display enum, but preserves the
raw DBC value.

| Signal | Start bit | Size | Scale / offset | Status |
| --- | ---: | ---: | --- | --- |
| `CHECKSUM` | 0 | 16 | 1 / 0 | Checksum field; platform variants exist, so the generator does not force the standard HKG algorithm. |
| `COUNTER` | 16 | 8 | 1 / 0 | Transmit-cycle counter. |
| `QUALITY` | 24 | 7 | 1 / 0 | Camera-object quality/reliability level. |
| `AGE` | 32 | 8 | 1 / 0 | Object alive age. |
| `MOTION_STATE` | 40 | 4 | 1 / 0 | Native camera motion class. |
| `OBJECT_ID` | 44 | 7 | 1 / 0 | Persistent object ID; zero is unused. |
| `WIDTH` | 52 | 7 | 0.05 / 0 m | Estimated width. |
| `CLASSIFICATION` | 60 | 3 | 1 / 0 | Unknown, truck, car, motorcycle, bicycle, pedestrian, undecided. |
| `LONG_DIST` | 64 | 13 | 0.05 / 0 m | Longitudinal relative position. |
| `LAT_DIST` | 78 | 12 | 0.05 / -102.4 m | Lateral relative position. |
| `REL_SPEED` | 91 | 12 | 0.05 / -100 m/s | Longitudinal relative velocity. |
| `REL_LAT_SPEED` | 104 | 10 | 0.05 / -25 m/s | Lateral relative velocity. |
| `REL_ACCEL` | 115 | 9 signed | 0.05 / 0 m/s² | Longitudinal relative acceleration. |
| `UNKNOWN_1` | 125 | 12 | raw | Active extension; semantics unknown. |
| `UNKNOWN_2` | 138 | 12 | raw | Active extension; semantics unknown. |
| `UNKNOWN_3` | 151 | 10 | raw | Active extension; semantics unknown. |
| `AZIMUTH` | 176 | 14 | 360/16384 / -180 deg | Route-validated high-resolution object azimuth. |

Native motion values are: 0 undefined, 1 standing, 2 parked, 3 stopped,
4 unknown movable, 5 moving, 6 stopped oncoming, 7 unknown oncoming,
8 moving oncoming, and 9 crossing bicycle. This is the only newly decoded
family with explicit oncoming moving and stopped-oncoming values.

## 240/270-28F candidate corner-radar layout

The address sizes and symmetry form two complete sensor channels:

| Channel | Inferred physical side | Status | Object slots | Compact scan records |
| --- | --- | --- | --- | --- |
| A | right front | `240`, 16 B | `241–24F`, 15 × 24 B | `270–277`, 8 × 32 B, seven records each |
| B | left front | `278`, 8 B | `279–287`, 15 × 24 B | `288–28F`, 8 × 32 B, seven records each |

Both channels run at about 20 Hz and validate with the HKG CAN-FD checksum in
the sampled Ioniq 5, Palisade 2023, and EV6 data. All 288,021 checked frames
from five complete segment samples passed. A synchronized Palisade
parking-garage sweep strongly assigns A to the right-front sensor and B to
the left-front sensor: A alone retained close objects at large negative
lateral position, while B alone retained the corresponding positive-side
objects. This is strong route/video evidence, but a controlled sensor
occlusion remains the final physical confirmation.

The 24-byte tracked-object record is:

| Signal | Bit | Size | Scale / offset | Status |
| --- | ---: | ---: | --- | --- |
| `UNKNOWN_CATEGORY` | 24 | 2 | raw | Stable within continuous same-slot tracks and changes mainly when a spatially different target replaces the slot. All values 0–3 occur on active objects, so this is not lifecycle or validity. |
| `RCS` | 56 | 7 signed | 1 / 0 | Strong shared-core identification; raw unit uncalibrated. |
| `LONG_DIST` | 63 | 13 | 0.05 / 0 m | Confirmed vehicle-frame longitudinal position. |
| `LAT_DIST` | 76 | 11 signed | 0.05 / 0 m | Confirmed vehicle-frame lateral position. |
| `UNKNOWN_BIT_87` | 87 | 1 | raw | Active unknown. |
| `REL_SPEED` | 88 | 10 signed | 0.2 / 0 m/s | Confirmed longitudinal relative velocity. Four held-out Palisade samples exercised bit 97 independently of bit 96 at 351–357 m; consecutive distance changes matched approximately -52 m/s rather than the false positive speed produced by the former 9-bit decode. |
| `REL_LAT_SPEED` | 98 | 10 signed | 0.05 / 0 m/s | Confirmed lateral relative velocity. |
| `UNKNOWN_BITS_108_117` | 108 | 10 | raw | Former centered acceleration candidate. Its correlations with consecutive `REL_SPEED` derivatives were -0.445, -0.043, -0.009, -0.111, and -0.124 across five Ioniq 5, Palisade, and EV6 samples, so the physical name and scale were falsified. |

Empty object slots use the exact `LONG_DIST=204.7 m` (`0xFFE`) sentinel;
`UNKNOWN_CATEGORY=0` must not be used as an empty test. This correction was
validated on five Ioniq 5, Palisade 2023, and EV6 samples. Including
category-zero objects produced longitudinal position-derivative correlations
of 0.949, 0.603, 0.962, 0.948, and 0.967 across those samples.

The position decode was independently checked against simultaneous
`210–21F` front-radar targets. The 116 unambiguous A matches and 86 B matches
had longitudinal/lateral correlations of 0.999/0.991 and 0.999/0.993,
respectively, with about 0.3 m mean absolute error. Across 14,939 consecutive
same-slot updates, decoded longitudinal and lateral velocity correlated with
position derivatives at 0.964 and 0.944. No lifecycle field has been
identified, and the former acceleration candidate failed derivative checks.
The remaining header, classification, dimension, ID, and health fields stay
bit-preserved rather than borrowing names from the related front-radar core.

The first payload byte after the counter in `0x278` is
`CHANNEL_A_OBJECT_COUNT`. Across 5,999 synchronized cycles on five Ioniq 5,
Palisade, and EV6 samples, the number of non-sentinel `0x241–0x24F` slots equaled
`min(CHANNEL_A_OBJECT_COUNT, 15)` exactly. It ranged from 0–22; values above
15 prove it is the pre-truncation internal candidate count rather than merely
the number of exported slots. The `0x240` status payload remains unresolved;
notably, it was entirely zero after checksum/counter on one Palisade and one
EV6 sample while being active on the other three routes.

The compact arrays are not alternate encodings of that object count. Depending
on route and channel, 11–55 of their 56 bins were non-sentinel in a cycle,
versus at most 15 exported tracked objects; count correlations ranged from
weak to moderate and were never exact.

The compact 32-bit scan record is:

| Record field | Relative bit | Size | Scale | Status |
| --- | ---: | ---: | --- | --- |
| `DISTANCE_CANDIDATE` | 0 | 13 | 0.05 m | Range-like distribution and 400 m endpoint; no synchronized object association, so physical distance is not confirmed. |
| `RESERVED` | 13 | 3 | raw | Preserve. |
| `PROPERTY` | 16 | 7 | raw | Active categorical unknown; sampled values were quantized. |
| `AUX` | 23 | 9 | raw | Active unknown; velocity and split flag/state hypotheses were falsified. |

Record 0 starts at message bit 24, message bit 56 is a frame-status byte, and
records 1–6 start at bits 64, 96, 128, 160, 192, and 224. Unused records
commonly contain `0x010D1F40`, with AUX variants such as `0x018D1F40`; its
low-field component is the 400 m endpoint. Contemporaneous range matching was no
better than the opposite channel or a 500 ms-shifted control. Each of the 56
record positions instead has a characteristic occupancy/range profile, making
this a strong fixed scan/bin-array candidate rather than 56 freely assigned
tracked detections. A direct linear record-index-to-angle search on Ioniq 5
and Palisade data also performed no better than a 500 ms-shifted control.
Decoding the low field, physical ordering, `PROPERTY`, and `AUX` remains open.

## 3D0-3D4 front-radar auxiliary scan records

This optional list accompanies `3A5–3C4` on sampled EV9 and Ioniq 9 routes.
Five 32-byte messages contain seven record positions each; the final three
positions of `3D4` are outside the 32-position list. The repeated
`0xC8782EE0` value and, on EV9, zero are unused records. All 12,090 checked
message frames passed the HKG CAN-FD checksum and carried the same cycle
counter as `3A5–3C4`.

| Record field | Relative bit | Size | Scale / offset | Status |
| --- | ---: | ---: | --- | --- |
| `DISTANCE_CANDIDATE` | 0 | 12 | 0.05 / 0 m | Range-like distribution and endpoint, but no synchronized tracked-object match; not confirmed. |
| `FLAGS_UNKNOWN` | 12 | 4 | raw | Active values 0–2 in the sampled routes; semantics unknown. |
| `UNKNOWN_BYTE_16` | 16 | 8 | raw | Former radial-speed candidate was falsified. |
| `UNKNOWN_BYTE_24` | 24 | 8 | raw | Former azimuth candidate was falsified. |

Packing positions match the corner scan records: record 0 at message bit 24,
one alignment byte at bit 56, then records 1–6 at bits 64 through 224. However,
the exact corner `13/3/7/9` field split is not transferred onto this
`12/4/8/8` layout without evidence.

The stronger synchronized test falsified three tempting interpretations:

- Range-only, candidate polar-geometry, and direct record-index-to-track-index
  associations were no better than opposite or 500 ms-shifted controls.
- `UNKNOWN_BYTE_16` had essentially zero correlation with `3A5` longitudinal
  or radial relative speed.
- `UNKNOWN_BYTE_24` had essentially zero correlation with `3A5` target angle.

The 32 positions do show stable position-dependent occupancy and low-field
profiles, so a fixed scan/bin or intermediate radar-array role remains
plausible. They are not independent tracked objects, remain excluded from
production RadarData, and are shown only as raw records in the debugger's
`SIGNALS` table, never projected as geometry.

## 360-366 forward-camera lane/path family

These seven 32-byte messages belong to the forward camera. `362` already
contains left/right lane-line confidence. `360`, `361`, `363`, and `364`
carry changing lane/path polynomial-like geometry; their field boundaries are
not yet decoded. `365` and `366` are commonly constant/default-filled,
consistent with unavailable extra lane slots. Their presence or emptiness
must not be interpreted as a radar hardware combination.

## Reserved/dead bits

Bits `26`, `29`, `39`, `55`, `117`, `136-137`, `143`, `171`, and
`188-191` remain zero. No new signal location was found in the follow-up
routes.

## Parser guidance

- Detect support per radar source instead of treating extension defaults as
  real measurements.
- Treat zero dimensions as unavailable. Treat +180 as unavailable on non-rich
  platforms, but do not discard near-180 rich tracks without checking their
  other geometry and lifecycle fields.
- Do not use any `NEW_SIGNAL_*` field for control or filtering until its
  meaning is independently validated.
- `TRACK_QUALITY` and `RCS` are decoded for research and diagnostics, but
  neither has a calibrated physical/percentage scale suitable for control.
- `REL_LAT_SPEED` is suitable for debugging cross traffic, but a production
  cross-traffic filter still needs lane-change validation and track history.
