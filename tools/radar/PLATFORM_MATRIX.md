# Hyundai/Kia/Genesis radar range matrix

This is a forum-ready summary of the routes analyzed for the sunnypilot radar
tracks work. It describes observed protocol families, not guaranteed equipment
for every model year, market, trim, or harness. A range can be present but empty
when the radar is inactive. Raw bus number is also not a layout identifier:
follow the sustained logical A-CAN source and reject brief forwarded copies.

Status terms:

- **Confirmed**: complete range, checksum/cadence, and tracked-object layout
  were validated across route data.
- **Observed/optional**: verified on at least one qualifying route, but not
  every route or trim carrying the main front-radar family.
- **Candidate**: source association or exact semantics remain incomplete.
- **Not radar**: camera or fused-output traffic overlapping radar-like ranges.

## Platform matrix

| Platform or platform group | Front tracked-object range | Front layout | Additional radar traffic | Camera/fused traffic that is not another radar | Status and notes |
| --- | --- | --- | --- | --- | --- |
| Kia K7 2017; older Hyundai Ioniq; sampled Ioniq PHEV | `0x500–0x53F` | 64 slots, 8 B each, about 20 Hz | `0x4E0`, `0x4E1`, `0x4E3` status/path messages | Legacy `0x238–0x24F` may coexist on applicable cars | **Confirmed** 64-slot legacy/Delphi-ESR dialect. |
| Kia Niro EV first generation; legacy Hyundai Palisade; Sonata; Sonata Hybrid | `0x500–0x51F` | 32 slots, 8 B each, about 20 Hz | `0x4E0–0x4E5` status/build/health/alignment family | Legacy `0x238–0x255` or related camera candidates may coexist by platform | **Confirmed** 32-slot legacy dialect. The upper `0x520–0x53F` bank is absent. |
| Hyundai Kona EV 2022; Kia Ceed PHEV | `0x602–0x617` | Two packed tracks in implemented messages | None established | None established | **Observed/candidate** legacy front family; the relationship between `0x602–0x611` and `0x612–0x617` remains incomplete. |
| Hyundai Elantra HEV 2024 | `0x210–0x21F` | Detailed dialect, 32 tracks in 16 × 32 B messages, 20 Hz | No paired corner family established | Platform-dependent camera traffic | **Confirmed** detailed `210` front radar. |
| Hyundai Ioniq 5; Hyundai Palisade 2023; Kia EV6, older HDA2 samples | `0x210–0x21F` | Detailed dialect, 32 tracks | Right-front candidate: `0x240–0x24F` objects plus `0x270–0x277` compact records. Left-front candidate: `0x278–0x287` objects plus `0x288–0x28F` compact records. | Isolated `0x235` traffic is not a complete camera-object family | **Confirmed** front radar. Paired front corners are **observed/optional** only on qualifying routes; A=right and B=left are strongly inferred but still need physical occlusion confirmation. |
| Hyundai Santa Cruz 2025; Tucson 4th generation; Tucson HEV 2025; Kia Sportage 5th generation | `0x210–0x21F` | Compact dialect, 32 tracks | No corner family established in checked routes | Platform-dependent camera traffic | **Confirmed** compact `210` front radar. Compact and detailed `210` share core kinematics but use different lifecycle fields. |
| Hyundai Ioniq 6 | `0x3A5–0x3C4` | Common 32-track layout, 24 B each, 20 Hz | No independent corner range established | `0x235–0x248` camera objects and `0x360–0x366` camera lane/path may be present | **Confirmed** common `3A5` front radar. |
| Hyundai Kona/Kona HEV/Kona EV 2nd generation; Santa Fe HEV 5th generation; Sonata 2024 | `0x3A5–0x3C4` | Common 32-track layout | No independent corner range established | Platform-dependent `0x235`, `0x360`, and CCNC `0x162` fused traffic | **Confirmed** common `3A5` front radar. CCNC/HDA generation does not imply rich radar extensions. |
| Kia Carnival HEV 2026; EV6 2025; K4 2025; K5 2025; Niro EV/HEV 2nd generation | `0x3A5–0x3C4` | Common 32-track layout | No independent corner range established | Platform-dependent `0x235`, `0x360`, and CCNC `0x162` fused traffic | **Confirmed** common `3A5` front radar. Bus 0/1 varies by architecture; a bus-2 copy can be forwarding. |
| Kia EV9; Hyundai Ioniq 9 | `0x3A5–0x3C4` | Rich 32-track layout with optional width, length, absolute speed, and orientation | `0x3D0–0x3D4` synchronized 32-position auxiliary scan array | `0x235–0x248` camera objects; `0x360–0x366` camera lane/path; CCNC `0x162` fused traffic | **Confirmed** rich `3A5`; `3D0` is **observed/optional** radar auxiliary traffic. Former `3D0` speed/azimuth interpretations were falsified, so it is counted but not projected as geometry. |
| Kia Sportage HEV 2026 forum sample | Overlaps `0x3A5–0x3C4` addresses | Payload is incompatible with the common `3A5` layout | Unknown | Unknown | **Excluded** from the common decoder; address overlap alone is not layout compatibility. |

## Other observed ranges

| Range | Applicable examples | Classification |
| --- | --- | --- |
| `0x235–0x248`, 32 B at about 33 Hz | Newer CAN-FD platforms, including rich EV9/Ioniq 9 captures | **Not radar:** forward-camera object list with class, motion, ID, geometry, velocity, and acceleration. |
| `0x360–0x366`, 32 B | Newer CAN-FD platforms carrying camera lane/path output | **Not radar:** forward-camera lane/path family. |
| `0x180–0x184`, `0x1B6–0x1B9`, `0x2BB–0x2BE` | Sampled Kia Sorento/Sorento HEV and Genesis GV70 candidates | **Not radar:** forward-camera auxiliary lists according to downloaded Hyundai DBCs. |
| `0x238–0x24F`, 8 B | Ioniq PHEV/HEV 2022, legacy Palisade, Niro PHEV candidates | **Not established as radar:** strong legacy forward-camera-perception candidate. |
| `0x238–0x255`, 8 B, often with `0x25A–0x25E` | Custin, Elantra/Elantra HEV 2021, Sonata/Sonata Hybrid candidates | **Not established as radar:** extended legacy forward-camera-perception candidate. |
| `CCNC_0x162` | CCNC platforms | **Not raw radar:** stock fused/cluster lead, side, and rear slots with unknown upstream fusion. |
| Bus-9 `0x300/0x400/0x500/0x600` blocks | Historical EV6 prototype capture | **Historical candidate:** four-corner FL/FR/RL/RR prototype; not reconfirmed in the current production-route corpus. |

## Supported combinations observed in the corpus

| Combination | Front | Corners or radar auxiliary |
| --- | --- | --- |
| Legacy front, 32 slots | `0x500–0x51F` | `0x4E0–0x4E5` companion/status |
| Legacy front, 64 slots | `0x500–0x53F` | `0x4E0`, `0x4E1`, `0x4E3` companion/status |
| Legacy alternate front | `0x602–0x617` | None established |
| CAN-FD detailed front only | `0x210–0x21F` | None established |
| CAN-FD detailed front plus paired front corners | `0x210–0x21F` | A/right candidate `0x240/0x270` families plus B/left candidate `0x278/0x288` families |
| CAN-FD compact front only | `0x210–0x21F` | None established |
| CAN-FD common front | `0x3A5–0x3C4` | Camera/fused families may coexist but are not independent radar tracks |
| CAN-FD rich front plus auxiliary scan | `0x3A5–0x3C4` | Optional `0x3D0–0x3D4` auxiliary radar array |

No checked route proves a combination containing both the paired
`0x240/0x270–0x28F` corner family and `0x3D0–0x3D4`. No distinct production
rear-radar tracked-object range has been confirmed. Rear objects in
`CCNC_0x162` are fused outputs and do not prove a raw rear-radar range.
