# Hyundai/Kia/Genesis radar source inventory

This document separates physical radar sources from camera and fused-object
traffic. Signal-level evidence is in [SIGNALS.md](SIGNALS.md).
The copy-ready vehicle/range summary is in
[PLATFORM_MATRIX.md](PLATFORM_MATRIX.md).

## Confidence and safety rules

- **Confirmed layout** means that bit positions, scales, and behavior agree
  across multiple routes. It does not automatically prove the physical ECU.
- **Strong role** means that topology, cadence, geometry, and related messages
  support the assignment, but a controlled sensor-occlusion test is still
  desirable.
- **Candidate** means useful research data only. Candidate fields must not
  affect control or production filtering.
- Identify a source by the complete address set, payload sizes, cadence,
  checksum behavior, and logical CAN path. An address or raw bus number alone
  is not enough.
- A short copy on another bus is normally a forwarding echo. It is not a
  second sensor unless timestamps and payload differences prove independence.

## Current source families

| Source | Layout | Role | Current conclusion |
| --- | --- | --- | --- |
| `0x500–0x51F` or `0x500–0x53F` | 32 or 64 × 8 B at about 20 Hz | Front radar | Shared legacy core with a Delphi ESR extension on the 64-slot dialect. K7, older Ioniq, and Ioniq PHEV samples carry 64 slots; Niro EV, Palisade, Sonata, and Sonata Hybrid samples carry 32. Implemented as standardized `RADAR_500_53F` with an optional upper half, per-source cycle end, and runtime 32-to-64 upgrade. Corrected 0.1-degree geometry is shared; 64-slot-only ESR fields use explicit aliases for 0.05 m/s² acceleration, lateral rate, width, oncoming, grouping, bridge-object, and range mode, while 32-slot acceleration retains 0.02 m/s². |
| `0x4E0–0x4E5` | 8 B at the `500` radar cadence | Front-radar companion/status | Strong source association across every sampled `500` route. Shared `4E0` is decoded as ESR vehicle speed, yaw, curvature, 16-bit scan index, timestamp, counter, and communication health. The 64-slot radar's `4E1` matches ESR Status2; 32-slot `4E1` retains only the shared counter plus unresolved static metadata. `4E3` path IDs are shared and route-validated. The 32-slot-only `4E2`, `4E4`, and `4E5` carry BCD build metadata, protocol-derived raw ADC channels, and factory/vertical alignment status. |
| `0x602–0x617` | 8 B, two packed tracks in the implemented messages | Front radar | Implemented legacy front layout. The relationship between `602–611` and the alternate `612–617` definitions remains incomplete. |
| `0x210–0x21F` | 16 × 32 B at 20 Hz, two tracks per message | Front radar | Confirmed 32-track front layout. Detailed and compact dialects share the same core. |
| `0x3A5–0x3C4` | 32 × 24 B at 20 Hz, one track per message | Front radar | Confirmed front layout. EV9 and Ioniq 9 populate its optional object-size/orientation extension. |
| `0x235–0x248` | 20 × 32 B at about 33 Hz | **Forward-camera objects** | Corrected classification. Its first 124 bits exactly match the downloaded `FR_CMR_Obj` schema and carry camera quality, class, motion, ID, geometry, velocity, and acceleration. It is not corner radar. |
| `0x240–0x24F` + `0x270–0x277` | status + 15 × 24 B objects + 8 × 32 B scan blocks | Candidate right-front corner channel A | Strong two-sensor topology on older HDA2 Ioniq 5, Palisade 2023, and EV6 routes. A=right is route/video-inferred; tracked-object position and velocity are decoded. Compact scan semantics remain unresolved. |
| `0x278–0x28F` | status + 15 × 24 B objects + 8 × 32 B scan blocks | Candidate left-front corner channel B | Symmetric partner to channel A. B=left is route/video-inferred. The compact low field is only a distance candidate; property/auxiliary bits are unresolved. |
| `0x3D0–0x3D4` | 5 × 32 B, seven packed records per message | Front-radar auxiliary scan list | Optional companion to `3A5–3C4` on sampled EV9/Ioniq 9 routes. It has 32 usable record positions and shares the radar cycle counter, but synchronized testing falsified the former radial-speed and azimuth interpretations. The low 12 bits remain only a distance candidate. |
| `0x360–0x366` | 7 × 32 B | **Forward-camera lane/path** | Camera lane/path geometry, not radar. `362` contains lane confidence; `360/361/363/364` are active geometry, while `365/366` are often default-filled optional slots. |
| legacy `0x238–0x24F` or `0x238–0x255` | 24 or 30 × 8 B at about 32 Hz | **Candidate forward-camera perception** | All 13 checked legacy routes carry one of these exact variants. Several carry a simultaneous `500` front radar at a different cadence, arguing strongly against this being a second radar. The 30-message variant also carries synchronized `25A–25E`; exact fields remain unparsed. Do not confuse these 8-byte messages with the CAN-FD `235–248` camera layout or `240/270` corner layout. |
| CAN-FD `0x180–0x184`, `0x1B6–0x1B9`, `0x2BB–0x2BE` | 32 B at about 30 Hz | **Forward-camera auxiliary lists** | Downloaded Hyundai DBCs identify the transmitters/messages as camera traffic, and route payloads have camera-list cadence and slot behavior. Not a radar family. |
| `CCNC_0x162` | fixed lead/left/right/rear slots | Fused/cluster output | Stock ADAS/cluster output with unknown upstream fusion. Do not publish it as independent raw radar. |
| bus 9 `0x300/0x400/0x500/0x600` eight-address blocks | old prototype, eight subtracks per message | Four-corner prototype | Prior EV6 reverse-engineering mapped four blocks to FL/FR/RL/RR, but status and relative speed were unfinished and the family has not been reconfirmed in the current corpus. |

The confirmed `3A5–3C4` layout was checked across 21 compatible forum routes
and 817,852 checksum-valid frames. All 726 advertised segments from the 20
unique `210–21F` routes were scanned: 16 routes had active targets, three had
a complete but empty stream, and one non-HDA2 Telluride route had no 210
range. The 16 active routes split evenly between detailed and compact
dialects, and all 13,210,543 checked 210 frames passed the HKG checksum.

The forum candidates are now classified at the family level. The legacy
`238–24F` and `238–255` variants are strong forward-camera candidates but
remain unparsed. The `180/1B6/2BB` groups are CAN-FD camera auxiliary lists.
The incomplete Ioniq PHEV `500–?` observation is a complete `500–53F`
64-slot front radar. None must be conflated with the CAN-FD `235` camera or
`240/270` corner layouts merely because their addresses overlap.

The `4E0/4E1` 2-bit counters matched in all 2,552 paired frames checked across
seven routes. On the three 64-slot routes, `4E3` matched the same counter in
all 1,133 paired frames. Every one of the 2,369 distinct `4E0` 16-bit
`SCAN_INDEX` steps incremented by one. In a fresh six-route full-segment pass,
decoded `4E0` vehicle speed correlated with `carState.vEgo` at
0.9976–0.99996, with 0.02–0.19 m/s mean absolute error. Both checked 64-slot
routes held `MAXIMUM_TRACKS_ACK=64`; all four 32-slot routes decoded that ESR
field as 1, confirming a different `4E1` dialect. The four sampled 32-slot
variants carried plausible BCD build timestamps in `4E2`; their remaining
`4E1` metadata stayed platform-static. All 7,347 nonzero `4E3` path IDs
referenced active one-based target slots. The 32-slot `4E4/4E5` payloads match
Hyundai-relocated ESR Status5/6 layouts: raw ADC health channels and alignment
status. Across 4,698 `4E5` frames, both factory-alignment fields remained
within the documented 0–3 enum subset; unexercised flags and physical ADC or
misalignment scales remain research-only.

Two other consecutive lookalikes are currently excluded from radar work:
downloaded Hyundai DBCs identify `630–63D` as head-unit/amplifier traffic, and
`5ED–5EF` occurs on routes without `500` tracks and does not follow the
otherwise strong `4E0`/`500` source association.

### Outstanding forum platform queue

| Platform | Remaining candidate |
| --- | --- |
| Hyundai Ioniq PHEV / Ioniq HEV 2022 / Palisade / Kia Niro PHEV 2022 | legacy camera candidate `238–24F`, plus its synchronized `201/20A/266/26D` companion groups |
| Hyundai Custin / Elantra 2021 / Elantra HEV 2021 / Sonata / Sonata Hybrid | extended legacy camera candidate `238–255`, plus `25A–25E` and the same companion groups |
| Kia Sorento / Sorento HEV 4th gen / Genesis GV70 | confirm semantics within the classified CAN-FD camera `180/1B6/2BB` auxiliary groups |
| Legacy `500` front-radar platforms | identify static 32-slot `4E1` metadata and calibrate/actively exercise the decoded `4E4/4E5` health and alignment fields |

The forum also listed Acura MDX and Honda Clarity examples. They remain out of
this Hyundai/Kia/Genesis inventory because the Acura range was unrelated and
the Honda routes did not expose tracks.

## Confirmed and possible vehicle combinations

These are distinct source combinations supported by the corpus. “Possible”
describes protocol combinations, not a promise that every trim exposes them.

| Combination | Front tracked objects | Corner source | Camera/auxiliary source | Known examples or status |
| --- | --- | --- | --- | --- |
| Legacy front only A | `500–51F` or `500–53F` | none observed | `4E0–4E5` radar companion/status | 32- and 64-slot platform variants |
| Legacy front only B | `602–617` | none observed | none established | Kona EV 2022, Ceed PHEV candidates |
| CAN-FD front only A | `210–21F` | none observed | none established | Elantra HEV 2024 and compact-dialect Tucson/Santa Cruz/Sportage routes |
| CAN-FD front + paired front corners | `210–21F` | inferred right A `240–24F` + `270–277`; inferred left B `278–28F` | none required | Older HDA2 Ioniq 5, Palisade 2023, and EV6 observations |
| CAN-FD front only B | `3A5–3C4` | none observed | camera objects/lanes may be absent or not logged | Compatible HDA1 routes |
| CAN-FD front + camera perception | `3A5–3C4` | none established | camera objects `235–248` and lanes `360–366` | Common newer HDA2 pattern; camera traffic is not another radar |
| Rich front + camera perception + auxiliary radar scan | rich `3A5–3C4` | none established | `235–248`, `360–366`, plus radar auxiliary records `3D0–3D4` | EV9 and Ioniq 9 sampled routes |
| Front + four-corner prototype | layout depends on the old EV6 capture | bus-9 FL/FR/RL/RR blocks | unknown | Historical prototype only; not current-production support |

No current evidence proves a combination containing both the paired
`240/270` corner family and the newer `3D0` auxiliary scan family. No distinct
rear-radar tracked-object range has been confirmed in the current routes.
Rear objects shown by `CCNC_0x162` may be fused from other sensors and do not
prove a rear radar source.

## Platform observations

| Platform group | Front | Additional observed traffic |
| --- | --- | --- |
| Ioniq 5 / Palisade 2023 / EV6 older HDA2 samples | detailed `210–21F` | paired `240/270–28F` front corners; A=right and B=left strongly inferred |
| Elantra HEV 2024 | detailed `210–21F` | no corner family established |
| Santa Cruz 2025 / Tucson family / Sportage 5th gen | compact `210–21F` | no corner family established in the checked samples |
| Ioniq 6 / Kona 2 / Kona EV 2 / Santa Fe 5 / Sonata 2024 / Carnival HEV / EV6 2025 / K4 / K5 / Niro 2 | common `3A5–3C4` where compatible | platform-dependent camera `235` and `360` traffic; no decoded corner family established |
| EV9 / Ioniq 9 | rich `3A5–3C4` | camera objects `235`, camera lanes `360`, optional front-radar auxiliary scan `3D0` |
| Sportage HEV 2026 forum sample | overlapping but incompatible `3A5` bytes | excluded from the common-layout decoder |

HDA2 changes where traffic is exposed, but raw bus number is not a reliable
layout discriminator. Follow sustained logical A-CAN and reject short
forwarded copies.

## What remains to prove

1. Confirm the route/video-derived A=right and B=left assignment with a
   controlled sensor occlusion or authoritative service mapping.
2. Finish both corner status messages and the remaining 24-byte object
   fields: the stable 2-bit unknown category, persistent ID, classification,
   dimensions, and sensor-health flags. The former acceleration candidate was
   falsified and returned to raw bits. Position and longitudinal/lateral
   velocity are resolved, and `0x278` byte 3 is the confirmed pre-truncation
   channel-A object count: exported A slots equal `min(count, 15)`.
   Preserve all remaining unknown bits until they correlate with the compact
   scan bins.
3. Decode the 56 fixed-position `270–277` / `288–28F` scan candidates,
   including the low 13-bit distance candidate, seven-bit property, and
   nine-bit auxiliary fields. Direct same-cycle range association and a linear
   record-index-to-angle map both failed time-shift controls, so do not project
   these records as geometry until an independent mapping is found.
4. Decode the `3D0` auxiliary scan array without restoring the falsified
   radial-speed or azimuth names. Determine whether the low 12 bits are
   distance, identify the role and physical angular ordering of the 32 record
   positions, and decode the four flag bits plus both unknown bytes. Two rich
   routes confirm exact counter synchronization and the sentinel/zero empty
   forms, but reject range-only, candidate-geometry, and direct slot-to-slot
   associations with `3A5`. Production RadarData must continue to exclude it.
5. Decode the active polynomial/path fields in `360/361/363/364`. Treat
   `365/366` constant payloads as unavailable lane slots, not missing radar.
6. Resolve `235–248` `UNKNOWN_1/2/3`, identify every checksum variant, and
   validate native camera classification/motion values against video. Confirm
   the camera-source assignment and forwarding path on each platform carrying
   the range.
7. Search explicitly for the old four-corner topology and for a distinct rear
   tracked-object source. Record verified absence when the correct buses and
   maneuvers were covered.
8. Resolve the static 32-slot `4E1` metadata, physically calibrate the
   protocol-derived `4E4` ADC channels, and capture alignment events to verify
   the inactive `4E5` flags and misalignment scales. Exercise the currently
   zero FCW path IDs and low `4E3` status flags on a 32-slot platform. Shared
   `4E0` and path IDs are resolved; do not transfer unsupported 64-slot
   Status2 fields onto the 32-slot payload.
9. Decode the legacy camera candidates `238–24F` and `238–255`, including
   their `201/20A/25A/266/26D` companion groups. Determine whether `250–255`
   and `25A–25E` are extra objects, path/lane data, or metadata, and correlate
   classification and geometry against video. Keep these out of production
   RadarData unless source evidence overturns the current camera assignment.
10. Complete the per-platform combination matrix across HDA1/HDA2 and
   CCNC/non-CCNC cars. Record the sustained logical CAN source, forwarded
   echoes, empty-but-present ranges, and verified absences rather than relying
   on raw bus numbers.
11. Add representative replay fixtures and debugger/on-road UI tests for each
    confirmed source combination. Promote candidate names or fields only after
    multi-route and controlled-scene validation.

## Useful work that does not require video

1. Cluster every unknown field by platform, object lifecycle, motion class,
   address/slot, and empty/default state. Stable cross-platform enums can be
   separated from platform configuration bytes.
2. Use consecutive-cycle derivatives and ego-motion compensation to test
   velocity, acceleration, yaw, and sensor-frame hypotheses. Always compare
   against opposite-channel and time-shifted controls.
3. Search counter phase and bounded latency, not merely nearest timestamps,
   when testing associations between tracked objects, compact scan arrays,
   camera objects, and status messages.
4. Build transition matrices for the corner unknown category and remaining
   flags. The first pass proved the 2-bit category is
   stable within a continuous object but is not lifecycle or validity: all four
   values occur on active targets, while empty slots use `LONG_DIST=204.7 m`.
   Continue searching the remaining fields for birth, coast, replacement, and
   deletion behavior without assuming the visual object class.
5. Compare the same physical field across detailed `210`, compact `210`,
   `3A5`, corner objects, and legacy `500` tracks after normalizing coordinates
   and lifecycle. Shared scaling should survive route and platform changes.
6. Mine downloaded and public DBC/source comments for transmitter identity and
   bit boundaries, but require route evidence before adopting physical names or
   scales.
7. Measure source dropouts, checksum/counter discontinuities, and status-bit
   transitions together. This can identify communication health, blockage,
   alignment, and reset fields without video.
8. Generate debugger capture instructions for later physical confirmation:
   cover one corner sensor at a time, use a single stationary target at a
   measured distance, and record straight approach/recede passes at known
   speed. These tests can settle side assignment and physical scan fields with
   much less ambiguity than unconstrained road scenes.

## Implementation policy

- Production RadarData contains the confirmed tracked-object layouts only.
- `235–248` remains available through RadarData as a camera-object source for
  research, with explicit source labeling and its native object-ID validity.
- The corner and `3D0` generators are research DBCs. Their unresolved fields
  are named unknown or candidate in comments and are not used for control.
- `4E0–4E5` status fields are present in the `RADAR_500_53F` DBC for research,
  and inventoried by the desktop radar debugger, but are not required for
  source detection or production track parsing.
- The on-road UI labels `235–248` as `CAM` and uses triangle markers.
- The desktop radar debugger plots confirmed production tracks, the
  debugger-only `612–617` alternate objects, and the decoded `240/278` corner
  objects. Its `SIGNALS` table exposes the compact `270/288` records, `3D0`
  records, `4E0–4E5` status, `360–366` raw camera payloads, and all six
  `CCNC_0x162` fused slots. Compact scans and `3D0` remain table-only and are
  never projected as geometry. `0x162` is explicitly labeled fused and is not
  published as an independent radar source.
