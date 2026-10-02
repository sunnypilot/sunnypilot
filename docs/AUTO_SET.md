# Map-based Auto SET (proposal)

Auto adds an opt-in mode after Assist in **Settings > Cruise > Speed Limit**.
It updates the cruise SET to the current mapped road limit plus the configured
offset, instead of retaining a fixed SET while another planner drives slower.
The non-PCM cruise path also updates `carState.vCruiseCluster`; controls passes
this to `hudControl.setSpeed`, and the existing Honda `ACC_HUD.CRUISE_SPEED`
message sends the SET to the **instrument cluster**. No new Honda CAN message
or simulated cruise button is introduced. Physical display validation is pending.

The intended benefits are fewer manual SET changes and a visible instrument-
cluster SET that follows the requested cruise target. Actual speed can remain
below the SET because of traffic, the driving model, or other existing controls.
This does not guarantee compliance with posted speed limits: map data can be
missing, outdated, or matched to the wrong road.

## Scope and behavior

- Only `HONDA_CITY_7G`, openpilot longitudinal control, non-PCM cruise, and
  neither passive nor dashcam-only operation are eligible. No other platform
  is enabled by this proposal. Existing modes 0–3 retain their meaning.
- Auto uses only the current mapped limit, not last-valid, ahead, or dashboard
  limits. Existing fixed/percentage offsets apply, including positive offsets.
- GPS, map envelope, and the mapd input token must be valid/recent within 3 s;
  distinct input tokens must retain the same target for at least 2 s.
- The plan and carControl must be fresh within 0.5 s, with active longitudinal
  control, no override/overlapping Assist, valid CAN, available cruise and an
  initialized SET. No engagement, resume or RES command is generated.
- After engagement, Auto waits for 0.5 s without held buttons. Manual +/-
  adjustments, Cancel and pedals suspend updates until cruise is disengaged
  and engaged again. Driver controls retain priority.
- Targets outside the existing minimum/145 km/h range are rejected rather
  than raised to the minimum. The evidence's double-precision limit avoids
  Float32 transport rounding at that boundary.
- Missing/stale/incompatible evidence stops new SET updates and retains the
  already applied SET. Existing longitudinal control may still accelerate
  toward that SET; source loss does not cancel cruise or command a slowdown.

## Mapd dependency and validation

The bundled mapd is rebuilt from v1.12.0 / commit
`46cd71ade6f630f1564c83bf1763f9d949a9ff30` plus
`openpilot/third_party/mapd_pfeiferj/auto_set.patch`; see the adjacent README
for the source/build recipe. The JSON sidecar `MapSpeedLimitEvidence` v1 binds
the result to the consumed position's `logMonoTime`. Atomic writes prevent
partial JSON; after an I/O failure, a previous result can survive until its
token expires. This sidecar is not recorded in native route logs.

The installer recognizes the repository's pinned bundled hash even when
MapdVersion is absent. Its legacy download fallback still retrieves the stock
v1.12.0 producer: if the bundled file is missing/replaced and that fallback is
used, Auto stays inactive without a compatible sidecar. Restore the pinned
repository binary to recover the producer; this is not automatic recovery.

This is a draft proposal. Offline tests do not establish physical operation,
full process integration, replay compatibility, or vehicle acceptance. No
device installation or driving validation is part of preparing this PR.
