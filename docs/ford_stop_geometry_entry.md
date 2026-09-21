# Stop request continuity and geometry entry

The joint controller previously marked the path invalid below 0.3 m/s in both
controlsd's validity carrier and card. The sender then transmitted inactive mode
0 with zero C0/C1. The new joint path stays active through a stop while engagement,
freshness, CAN, motion, and steering-fault checks permit it.

Below 0.3 m/s, card repeats the last transmitted active C0/C1 packet. The observer
continues advancing at actual speed; no fictitious speed is supplied to the
inverse, which divides by speed squared. Trim is retained, the latest action
target is remembered, and the trend rate is zero while holding. At 0.3 m/s and
above, normal allocation resumes using the current action. Disengagement, stale
inputs, steering faults, and explicit PSCM override/denial still release the
request. Starting or reengaging at rest after an inactive packet begins with a
neutral active packet; it does not restore an old turn command.

This preserves the transmitted request, not a proven physical wheel angle. A
different model action on restart can still request straighter steering. The
legacy non-joint adapter's speed gate and master-off upstream path are unchanged.

## Geometry candidate

The existing **Signaled-Turn Preview (Experimental)** toggle now also enables the
offline `boot08` candidate. Keep Selected-Action Path Tracking, Coordinated C0/C1
Steering, and Large-Turn Entry Assist enabled, with Model Geometry Reference off.
Apply settings offroad and start a new onroad session.

On each new model message, controlsd measures local heading change over a complete
2 m path interval centered at speed times 0.8 seconds (start clamped to zero).
It converts this curvature through the existing VehicleModel, roll and angle
offset. Geometry and vehicle parameters must be valid; insufficient path disables
only the independent addition. The angle travels as additive carControlSP metadata.

The 7/14 m headings and exactly one matching signal must agree on a sharp turn.
The independent addition is capped at 90 wheel degrees, fades during action unwind,
and fades from full strength at 30 action degrees to zero at 90. Strong opposing
action suppresses it. Card selects the larger of this addition and the existing
bounded action-rate preview, rather than adding both. The action base, trim,
encoder, acceleration allowance, C0/C1 field bounds and zero C2/C3 remain.

The geometry calculation uses speed and vehicle parameters available when the
new model message is processed. The archived offline experiment sampled their
latest recorded values at the model timestamp. Transport timing can therefore
cause small input differences; installation parity uses identical sampled inputs.

## Validation

Nine new stop-continuity regression cases failed before the fix and pass with
active packets through the stop, retained commands/trim, and fault/disengagement
release without reviving old commands. The real Ford CAN packer is exercised.

The prior frozen experiment covered 12 routes (828,178 controller samples per
candidate). Installation checks match its geometry calculation on 4,854 sampled
paths across all 12 routes, its policy on 20,000 random cases, and its transmitted
commands and observer state on 3,000 continuous moving updates. Separate tests
cover flat-action entry through real model messages and Cap'n Proto transport,
takeover fade, health and signal gates, and toggle-off behavior.

The earlier experiment advanced several nominal entry crossings by roughly
0.07–0.39 seconds; some turns were unchanged. Nine of ten wobble windows retained
identical packets, and the known unwind's 90/60/30-degree reference crossings were
unchanged. A near-stop entry reference was busier. These are frozen command and
older-firmware reference comparisons, not a new physical wheel response, proof
of stability, or truck validation of the combined changes.
