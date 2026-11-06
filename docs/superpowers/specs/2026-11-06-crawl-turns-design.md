# Crawl turns: go past the corner, turn harder, shaped by the route

## Status: steering removed (routes 93-96)

The turn steering below (items 1 and 2, and the route scaling in 3) is gone. Turn steering is back to the first turn
plan floor: the command never falls below 0.75x the model's plan toward the turn, at every turn speed, with no speed
fade and no gate on the model's own turn state. The corner speed (item 3, openpilot longitudinal only) and navd finding
the turn for any model stay.

Why, from routes 93, 94 and 96 (CD210, f6a08afbf), with no crashes, model drops or params errors:

- The hold cut a turn already under way. "Wait for the turn" sent the cue only once the model's turn prediction
  reached 0.35, by then the car had turned ~80 deg on its own, and the hold read the corner as just reached and held it
  for 1.5 m: the wheel unwound and the driver took over (route 93, 58.6 s).
- The model forgets the turn 6.5-6.6 s after the cue, every time it was still waiting or turning (routes 92-96). The
  desire reaches it as a one-frame pulse and its desire and feature history is ~5 s. After a cue at a red light, it
  had lost the turn by the time the car pulled away, and the turn-state gate then switched the floor off too (route 96,
  8 s), so the car went straight.
- The hold used up that window: at a crawl, the corner plus 1.5 m came as the model forgot (route 96, released at
  705.3 s with the turn state falling from 1.0 to 0.19 the same frame).

Without the gate, the early turn-in pulling away from a stop that it was added for (routes 85/89) can come back.

## Problem

Routes 85 and 89 (19 engaged turns, Light Speed 2): above ~4 m/s the car makes 90-98% of the model's planned turn and
the driver barely touches the wheel. Below 4 m/s it makes 47-75%, and the driver pushes against the turn 5-21% of the
time. The pushback comes at turn-in (median 12% of the turn done, the plan's corner 1.4-3.5 m ahead of the camera). The
driver confirmed it turns in too early, and wants it like FSD: well past the entrance, then a harder turn so both wheels
clear.

## Design (modeld_v2/turn_shaping.py)

Only during a signalled turn (turn desire), and only at a crawl: full under 4 m/s, gone from 6 m/s.

1. **Turn-in hold.** The plan's corner is where its heading has turned 5 deg toward the turn, measured along the plan's
   positions from the front bumper (camera + 1.52 m). While the plan has a corner ahead, steering toward the turn is
   held to the road's curvature from before the corner (the plan's curvature under the car, last taken while the corner
   was still 3 m or more away), so a curving approach is still followed. Once the corner reaches the bumper, the hold
   lasts another 2 m of travel, counted by speed (a car held at the corner gets a plan that turns right where it is),
   letting go over the last metre. Then it's off for that turn. Steering away from the turn is never touched; a plan
   with no corner is never held; waiting at a stop doesn't count; creeping toward a corner counts for 8 s at most; past
   the corner it lasts 2.5 s at most.
2. **Harder turn with look-ahead.** The turn plan floor is the full plan (1.0x at <=4 m/s, fading to 0 by 8 m/s, up from
   0.75x), read 0.3 s further ahead at <=4 m/s (fading out by 8 m/s) so the rate-limited wheel arrives on time. It's off
   while the hold is on, and the model's own turn state gates it as before.
3. **Route shape and corner speed.** navd's signal route (`MapboxNextTurnEnabled`, no destination needed) publishes the
   turn's entry and exit bearings and the distance to the junction in `MapboxTurnContext`. navd now finds the turn for
   any model; map inputs to the model itself stay gated on `modelSupportsNavigation`, which the context now carries. The
   turn still to go is the exit heading error once in the junction, the bearing change before it. When it exceeds the
   plan's own heading change over its horizon by more than 10 deg, the floor's plan curvature is scaled by up to 1.3x.
   The route never times anything. With openpilot longitudinal, plannerd caps the cruise target to a corner speed by turn
   angle (4.5 m/s for 90 deg), approached at 1 m/s^2 within 100 m of the junction, held through it; only below the
   lane-turn speed (a blinker above it is a lane change) and only ever lower.

Hard limits on the floor: |curvature| <= 0.2 1/m and lateral acceleration <= 3 m/s^2.

## Replay of routes 85/89 (open loop)

The first version, released when the corner came within 1 m, didn't move the turn-in at all (median 0.0 m; 69 of 71
pushback frames after release). The built version holds 55 of 71 pushback frames under 4 m/s, delays the turn-in a
median 2.0 m (0-7.5 m), and holds back 0.04-0.10 1/m at crawl turn-ins; faster turns are untouched.

## Logging

modelDataV2SP: turnInHold, turnBendDistance, turnLead, turnRouteRemainingDeg, turnRouteFactor.
longitudinalPlanSP: source turnSpeed while the corner speed sets the target.
