# Hyundai/Kia/Genesis radar research roadmap

This document tracks which object sources exist on each platform, what role
they appear to serve, and what must still be proved. Detailed signal evidence
for the best-understood family is kept in [SIGNALS.md](SIGNALS.md).

The intended end state is an inventory for every platform with four slots:

1. **Front** — the forward long-range radar used for longitudinal driving.
2. **Corner** — one CAN message family representing the car's corner-radar
   system. A family may contain two or four physical sensors; "one corner
   source" does not mean one sensor.
3. **Extras/fused** — ADAS or cluster object outputs that may combine radar,
   camera, and other inputs. These must not be called raw radar without proof.
4. **Rear** — a distinct rear-facing track source, if the car exposes one.
   Rear tracks may instead be part of the corner family.

Each slot should eventually name a confirmed source or say **verified absent**.
The inventory must not assume that every platform has every type of hardware.

## Confidence labels

- **Confirmed** — decoded geometry and behavior agree across multiple routes
  or controlled observations.
- **Implemented** — a runtime layout exists and produces plausible tracks, but
  its physical role or platform coverage still needs systematic confirmation.
- **Candidate** — a route/post/code clue identifies a likely source, but its
  role or layout is not yet established.
- **Prototype** — useful prior reverse-engineering evidence from code that was
  never merged or completed.
- **Unknown** — detected traffic with no reliable role yet.
- **Incompatible** — the address range overlaps a known family but its bytes
  do not use that layout.
- **Verified absent** — the relevant buses were observed under suitable
  conditions and no source exists.

## Research order

### 1. Finish the front-radar inventory

Front radar comes first because it is the source that can affect openpilot
driving. For each existing layout, validate its bus, message size, cadence,
track lifecycle, distance, lateral position, relative velocity, and duplicate
forwarding behavior across multiple platforms.

Then investigate the unimplemented route families in this order:

1. `0x238–0x24F`
2. `0x238–0x255`
3. the combined `0x180–0x184`, `0x1B6–0x1B9`, and `0x2BB–0x2BF` sets
4. the incomplete `0x500–?` Ioniq PHEV 2019 observation

These are front-radar candidates because of how they were grouped in the
supplied route post, not because their physical role has been proved.

A front source should show forward-centred geometry, useful range ahead of the
car, longitudinal relative speed, stable lead-vehicle continuity, and the
expected response when ego speed changes. Video alignment and route maneuvers
must confirm that it is not a corner or fused-object source.

### 2. Identify corner-radar systems

There are two separate clues and they must not be conflated:

- The supplied route post labels `0x235–0x248` as "corner radar available on
  some HDA2 vehicles." The branch already has a one-track-per-message decoder
  for this range, but its physical coverage still needs route-level proof.
- The closed [EV6 corner-radar prototype PR](https://github.com/commaai/openpilot/pull/24221)
  used bus 9 and four eight-address blocks: `0x300–0x307`,
  `0x400–0x407`, `0x500–0x507`, and `0x600–0x607`. Each frame contained
  eight subtracks. The code mapped the four blocks to front-left, front-right,
  rear-left, and rear-right sensors, but relative speed and status decoding
  were unfinished.

The EV6 prototype is evidence for a four-corner architecture, not evidence
that every HDA2 car or every `0x235–0x248` source uses that architecture.

Corner confirmation should use scenes with passing traffic, blind-spot
occupancy, cross traffic, and targets moving around the car. Expected evidence
includes short-to-medium range, strong lateral coverage, stable left/right
sectors, and — if rear corners are included — tracks behind the rear axle.
Bus/address blocks should be correlated with individual sectors and physical
sensor occlusion where possible.

### 3. Trace extras and fused objects

Stock `CCNC_0x162` lead, left, right, and rear tofu slots are a separate fused
cluster/ADAS output. Existing route evidence shows that these slots can be
active when the optional `3A5–3C4` geometry fields are unavailable, so they
cannot be reconstructed by treating the rich `3A5` bytes as extra tracks.

The next step is to locate the inputs upstream of `CCNC_0x162`, correlate each
slot with front and corner tracks, and determine whether the output is radar,
camera, or multi-sensor fusion. Unknown extra address groups and unknown DBC
fields come after the front and corner inventories because their behavior is
easier to interpret once the physical radar sources are known.

Fused outputs may be useful for cluster visualization, but they must not be
fed into driving as independent radar measurements unless duplication,
latency, lifecycle, and provenance are understood.

### 4. Confirm a rear source only when tracks exist

Do not create a separate rear-radar category merely because the cluster has
rear tofu slots. Record a rear source only when a distinct message family
outputs repeatable rear-facing tracks. If the rear tracks come from the same
four-corner family, document that under **Corner** and mark **Rear** as
contained in that family.

## Known and candidate source families

| Source | Runtime layout | Current role | Status and next proof |
| --- | --- | --- | --- |
| `0x3A5–0x3C4` | 32 × 24-byte messages at 20 Hz | Front | Confirmed across 21 common-layout routes and 817,852 checksum-valid frames. `TRACK_QUALITY`, `RCS`, lifecycle, kinematics, and the optional rich extension are decoded. No dedicated oncoming value was found. Sportage HEV 2026 has an incompatible overlapping layout. |
| `0x210–0x21F` | 16 × 32-byte messages at 20 Hz; two tracks per message | Front | Confirmed across 16 active routes and two dialects. Detailed and compact layouts share the core; compact adds persistent object IDs and uses motion code 3 for stopped and 4 for oncoming, while detailed has no dedicated oncoming value. Three additional streams were empty and one non-HDA2 Telluride route had no 210 range. |
| `0x500–0x51F` | 32 × 8-byte messages at 20 Hz | Likely front | Implemented. Confirm special behavior around `0x501/0x502` and validate lateral conversion from azimuth. |
| `0x602–0x617` | Generator has double-track `0x602–0x611` and alternate single-track `0x612–0x617` formats | Likely front | Partially implemented: runtime currently consumes only `0x602–0x611`. Confirm whether `0x612–0x617` is the same objects, an alternate view, or a separate output before expanding it. |
| `0x235–0x248` | 20 × 32-byte messages at 33 Hz; one track per message | Corner candidate | Implemented geometry, but the post's corner classification still needs HDA2 route/video confirmation. |
| `0x238–0x24F` | Not implemented | Front candidate | Reverse layout and confirm physical role on the four listed platforms. It overlaps `0x235–0x248`, so detection must use the complete range, size, and layout rather than address membership alone. |
| `0x238–0x255` | Not implemented | Front candidate | Reverse layout and distinguish it from both `0x238–0x24F` and `0x235–0x248`. |
| `0x180–0x184`, `0x1B6–0x1B9`, `0x2BB–0x2BF` | Not implemented | Unknown multi-range source | Determine whether the three blocks are one radar protocol, multiple sensors, or fused/metadata outputs before assigning a role. |
| bus 9: `0x300/0x400/0x500/0x600` eight-address blocks | Old EV6 prototype; eight subtracks per message | Four-corner prototype | Search HDA2 logs for the same topology and finish status/relative-speed decoding if found. Do not confuse its `0x500` block with the legacy front `0x500–0x51F` family on another bus/layout. |
| `CCNC_0x162` | Fixed cluster-object slots | Extras/fused | Confirmed as a separate stock output, but its upstream sensor inputs are unknown. |

## Platform inventory

This is the investigation queue transcribed from the supplied route post and
augmented only where current branch evidence is explicit. "HDA2 candidate"
means to check both the `0x235–0x248` clue and the older four-block EV6
topology; it does not claim that either is present.

### Platforms with `0x3A5–0x3C4`

| Platform | Front | Corner | Extras/fused | Rear |
| --- | --- | --- | --- | --- |
| Hyundai Ioniq 6 | `3A5–3C4` confirmed | HDA2 candidate | Unknown | Unknown |
| Hyundai Kona 2nd gen | `3A5–3C4` confirmed | Unknown | Check CCNC fused output | Unknown |
| Hyundai Kona EV 2nd gen | `3A5–3C4` confirmed | HDA2 candidate | `CCNC_0x162` observed on sampled CCNC routes | Unknown |
| Hyundai Kona HEV 2nd gen | `3A5–3C4` confirmed | Unknown | Check CCNC fused output | Unknown |
| Hyundai Santa Fe HEV 5th gen | `3A5–3C4` confirmed | Unknown | Check CCNC fused output | Unknown |
| Hyundai Sonata 2024 | `3A5–3C4` confirmed | Unknown | Check CCNC fused output | Unknown |
| Kia Carnival HEV 4th gen (2026) | `3A5–3C4` confirmed | Unknown | Unknown | Unknown |
| Kia EV6 2025 | `3A5–3C4` confirmed | HDA2 candidate | Check CCNC fused output | Unknown |
| Kia EV9 | `3A5–3C4` confirmed; rich extension | HDA2/corner candidate | Check `CCNC_0x162` and upstream inputs | Unknown |
| Kia K4 2025 | `3A5–3C4` confirmed | Check HDA2 routes | Check CCNC fused output | Unknown |
| Kia K5 2025 | `3A5–3C4` confirmed | Unknown | Check CCNC fused output | Unknown |
| Kia Niro EV 2nd gen | `3A5–3C4` confirmed | Check HDA2 routes | Unknown | Unknown |
| Kia Niro HEV 2nd gen | `3A5–3C4` confirmed | Unknown | Unknown | Unknown |
| Kia Sportage HEV 2026 | **Incompatible overlapping layout** | Unknown | Unknown | Unknown |
| Hyundai Ioniq 9 | `3A5–3C4` confirmed; rich extension | HDA2 candidate | Check `CCNC_0x162` and upstream inputs | Unknown |

### Platforms with `0x210–0x21F`

| Platform | Front | Corner | Extras/fused | Rear |
| --- | --- | --- | --- | --- |
| Hyundai Elantra HEV 2024 | `210–21F` detailed confirmed | Unknown | Unknown | Unknown |
| Hyundai Ioniq 5 | `210–21F` detailed confirmed on two active routes; one route empty | HDA2 candidate | Unknown | Unknown |
| Hyundai Palisade 2023 | `210–21F` detailed confirmed on one active route; one route empty | HDA2 candidate | Unknown | Unknown |
| Kia EV6 | `210–21F` detailed confirmed on four active routes; one route empty | Four-block prototype candidate | Unknown | Prototype family may include rear corners |
| Kia K8 HEV 1st gen | Historical supplied route empty; outside the 20-route validation set | Unknown | Unknown | Unknown |
| Hyundai Santa Cruz 2025 | `210–21F` compact confirmed | Unknown | Unknown | Unknown |
| Hyundai Tucson 4th gen | `210–21F` compact confirmed on four routes | Unknown | Unknown | Unknown |
| Hyundai Tucson HEV 2025 | `210–21F` compact confirmed | Unknown | Unknown | Unknown |
| Kia Sportage 5th gen | `210–21F` compact confirmed on two routes | Unknown | Unknown | Unknown |

### Platforms with legacy implemented layouts

| Platform | Front | Corner | Extras/fused | Rear |
| --- | --- | --- | --- | --- |
| Hyundai Ioniq | `500–51F` implemented; verify | Unknown | Unknown | Unknown |
| Kia K7 2017 | `500–51F` implemented; verify | Unknown | Unknown | Unknown |
| Kia Niro EV | `500–51F` implemented; verify | Unknown | Unknown | Unknown |
| Hyundai Kona EV 2022 | `602–617` partially implemented; verify | Unknown | Unknown | Unknown |
| Kia Ceed PHEV | `602–617` partially implemented; verify | Unknown | Unknown | Unknown |

### Unimplemented front candidates

| Platform | Candidate front source | Corner | Extras/fused | Rear |
| --- | --- | --- | --- | --- |
| Hyundai Ioniq PHEV | `238–24F` | Unknown | Unknown | Unknown |
| Kia Niro PHEV 2022 | `238–24F` | Unknown | Unknown | Unknown |
| Hyundai Palisade | `238–24F` | Unknown | Unknown | Unknown |
| Hyundai Ioniq HEV 2022 | `238–24F` | Unknown | Unknown | Unknown |
| Hyundai Custin 1st gen | `238–255` | Unknown | Unknown | Unknown |
| Hyundai Elantra 2021 | `238–255` | Unknown | Unknown | Unknown |
| Hyundai Sonata | `238–255` | Unknown | Unknown | Unknown |
| Hyundai Sonata Hybrid | `238–255` | Unknown | Unknown | Unknown |
| Hyundai Elantra HEV 2021 | `238–255` | Unknown | Unknown | Unknown |
| Kia Sorento 4th gen | `180/1B6/2BB` groups; role unproved | Unknown | Unknown | Unknown |
| Kia Sorento HEV 4th gen | `180/1B6/2BB` groups; role unproved | Unknown | Unknown | Unknown |
| Genesis GV70 1st gen | `180/1B6/2BB` groups; role unproved | Unknown | Unknown | Unknown |
| Hyundai Ioniq PHEV 2019 | Incomplete `500–?` observation | Unknown | Unknown | Unknown |

The post also included Acura MDX and Honda Clarity examples. They are excluded
from this Hyundai/Kia/Genesis roadmap: the Acura range was unrelated, and the
Honda routes showed no tracks.

## Definition of done for one platform

A platform row is complete only after the following are recorded:

- exact fingerprint, trim/architecture flags, route segments, and test scenes;
- source bus, address range, payload size, cadence, and counter behavior;
- whether duplicate copies on other buses are forwarding or independent
  sensors;
- physical coverage: front, front corners, rear corners, or rear;
- track lifecycle and validity states;
- longitudinal/lateral position, relative velocities, acceleration, and
  motion classification when available;
- behavior for moving, stationary, crossing, oncoming, overtaking, cut-in,
  and curved-road targets;
- correlation with road/wide camera and, for fused outputs, with every known
  raw source;
- explicit control-versus-visualization policy;
- DBC comments, parser tests, representative replay tests, and known
  unavailable/default signal values.

## Safety and implementation rules

- A consecutive address range is not sufficient identification. Match the
  complete range, bus, payload length, cadence, and decoded invariants.
- Do not merge two buses into two radars until byte/timestamp comparison rules
  out forwarding.
- Do not use an unknown signal for filtering or control.
- Do not send fused cluster objects to driving as if they were independent raw
  tracks.
- Keep all discovered sources available to `tools/radar/ui.py` for research,
  even when the production radar interface deliberately filters what is sent
  to openpilot.
- Record negative results. A verified absence is more useful than leaving a
  platform perpetually marked unknown.
