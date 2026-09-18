# SLC JSON Configuration

Optional Speed Limit Control settings can be placed in:

```text
/data/sunnypilot/slc.json
```

The file is JSON, so it cannot contain comments. Restart openpilot after editing if you want the change applied immediately; the config reader also reloads when the file timestamp changes.

## Example

```json
{
  "speedLimitLowerLookaheadEnabled": true,
  "speedLimitLookaheadFactorDown": 4.0,
  "speedLimitLookaheadFactorUp": 1.0,
  "speedLimitLowerDecelControlEnabled": true,
  "speedLimitLowerDecelMode": "fixed",
  "speedLimitLowerDecelFixedAccel": -0.05,
  "speedLimitLowerDecelReleaseGapKph": 5.0,
  "speedLimitMaxDecelMps2": -0.5,
  "longitudinalNoLeadDecelMode": "idle",
  "longitudinalNoLeadIdleMinDecelMps2": -0.15,
  "longitudinalNoLeadIdleOverspeedMarginKph": 1.0,
  "longitudinalNoLeadIdleDecelCooldownS": 2.0
}
```

## Keys

`speedLimitLowerLookaheadEnabled`

Enables map lookahead for upcoming lower speed limits. This allows SLC to start reacting before the current speed limit changes.

Allowed values: `true`, `false`

Default: `false`

`speedLimitLookaheadFactorDown`

Controls how far ahead lower speed limits are considered. The distance is based on speed and this factor. Example: a factor of `4.0` at `100 kph` is roughly `400 m`.

Allowed range: `0.0` to `10.0`

Default: `0.0`

`speedLimitLookaheadFactorUp`

Controls how far ahead higher speed limits are considered. This is used for upcoming speed-limit increases.

Allowed range: `0.0` to `10.0`

Default: `0.0`

`speedLimitLowerDecelControlEnabled`

Enables the special lower-speed-limit decel behavior when lower map lookahead is active. Fixed/dynamic modes require no lead; idle mode also permits a steady, sufficiently distant lead (see below).

Allowed values: `true`, `false`

Default: `false`

`speedLimitLowerDecelMode`

Selects how SLC approaches a lower upcoming speed limit when `speedLimitLowerDecelControlEnabled` is active.

If `longitudinalNoLeadDecelMode` is set to `"idle"`, ordinary no-lead cruise decel will use idle instead of these fixed/dynamic accel requests. In that setup, this key mostly matters only for the dedicated lower-speed-limit lookahead path.

Allowed values:

- `"fixed"`: request the configured `speedLimitLowerDecelFixedAccel` until the release gap is reached.
- `"dynamic"`: calculate decel from current speed, target speed, and remaining distance.
- `"idle"`: request output-layer idle instead of negative accel while above the release gap. Currently implemented for Hyundai CAN-FD SCC output.

Default: `"fixed"`

`speedLimitLowerDecelFixedAccel`

Acceleration request used by `"fixed"` mode. Negative values slow the car. Values closer to `0.0` are gentler.

Allowed range: `-1.2` to `0.0` m/s^2

Default: `-0.05`

`speedLimitLowerDecelReleaseGapKph`

Stops the lower-limit decel override once ego speed is within this margin above the adjusted speed-limit target. Example: with a `50 kph` target and `5.0`, the override releases at `55 kph`. This is a one-time release for that target: normal speed control resumes and small speed increases do not re-enter the override. The release margin does not change the final cruise target. With a posted `50 kph` limit and a `+1 kph` speed-limit offset, the adjusted target is `51 kph`, so a `5 kph` release margin releases at `56 kph`.

Allowed range: `0.0` to `30.0` kph

Default: `5.0`

`speedLimitMaxDecelMps2`

Caps normal no-lead SLC decel. This does not cap the special lower-limit decel modes while they are active.

Allowed range: `-2.0` to `0.0` m/s^2

Default: `-0.5`

`longitudinalNoLeadDecelMode`

Controls intentional cruise-source decel, outside emergency, lead-braking, and stop cases. Despite its legacy name, idle mode also permits a qualified steady lead under the rules below. It does not idle for small speed-hold corrections.

This is the broader gas-car test mode. If `"idle"` behaves well, it can replace most fixed/dynamic decel tuning for no-lead slowdowns.
Pressing accel/resume or increasing the cruise target clears idle and blocks it briefly so the controller sends an active non-idle output again. Lowering the set speed while temporarily overriding with the accelerator preserves that slowdown target until control resumes; idle is always blocked while a pedal is pressed, and full disengagement clears the target.
If SLC is enforcing the current adjusted speed limit and the car is more than `longitudinalNoLeadIdleOverspeedMarginKph` above it, idle is blocked so normal decel/braking can control downhill overspeed. After this happens, idle stays blocked for `longitudinalNoLeadIdleDecelCooldownS` seconds to avoid rapid idle/brake toggling near the limit.

Allowed values:

- `"normal"`: keep normal planner/controller acceleration requests, including negative decel.
- `"idle"`: when SLC lowers the target or the driver manually lowers the cruise set speed, request output-layer idle instead of negative accel. Currently implemented for Hyundai CAN-FD SCC output.

Default: `"normal"`

`longitudinalNoLeadIdleMinDecelMps2`

Minimum requested decel needed before `longitudinalNoLeadDecelMode: "idle"` activates. Small negative accel requests stay in normal control; stronger intentional no-lead decel requests use idle.

Example: with `-0.15`, a request of `-0.05` stays normal, while a request of `-0.20` uses idle.

Allowed range: `-1.2` to `0.0` m/s^2

Default: `-0.15`

`longitudinalNoLeadIdleOverspeedMarginKph`

Extra speed above the adjusted current speed limit before idle is blocked and normal decel/braking is used. This avoids switching out of idle for tiny speed noise around the target.

Allowed range: `0.0` to `10.0` kph

Default: `1.0`

`longitudinalNoLeadIdleDecelCooldownS`

How long idle stays blocked after current-limit overspeed decel is needed. Higher values reduce idle/brake flicker near the limit.

Allowed range: `0.0` to `10.0` seconds

Default: `2.0`

## Legacy Keys

The old keys are still accepted as fallbacks:

- `lookaheadLowerLimits` -> `speedLimitLowerLookaheadEnabled`
- `lookaheadSpeedFactorDown` -> `speedLimitLookaheadFactorDown`
- `lookaheadSpeedFactorUp` -> `speedLimitLookaheadFactorUp`
- `lookaheadSpeedFactor` -> fallback for both lookahead factors
- `noBrakeForSpeedLimit` -> `speedLimitLowerDecelControlEnabled`
- `noBrakeMode` -> `speedLimitLowerDecelMode`
- `noBrakeAccel` -> `speedLimitLowerDecelFixedAccel`
- `noBrakeReleaseGapKph` -> `speedLimitLowerDecelReleaseGapKph`
- `speedLimitMaxDecel` -> `speedLimitMaxDecelMps2`

Prefer the explicit keys for new configs.

## Idle with a lead and recovery

Both the dedicated lower-limit `"idle"` approach and manual set-speed reductions with `longitudinalNoLeadDecelMode: "idle"` can coast with a lead after two seconds of stable readings. Both detected leads must satisfy all of these initial conservative thresholds:

- Distance at least `95%` of the personality follow distance (`T_FOLLOW × v_ego`, minimum `6 m`), so a lead at normal following distance qualifies.
- Relative speed at least `-0.2 m/s` (no appreciable closing).
- Lead acceleration at least `-0.2 m/s²` (no appreciable slowing).
- No abrupt distance drop of more than `0.5 m` between planner updates.

Every new lead appearance restarts the two-second qualification period. A lead that simply departs no longer restarts it; the lead-planner brake gate below still blocks idle whenever the planner needs to slow down, so this avoids several seconds of braking right as a qualifying lead pulls away. A flickering lead still cannot repeatedly re-enable idle, because each reappearance resets the timer.

Unsafe lead readings must persist before they restart qualification. Brief radar noise (up to `0.25 s`) keeps the qualified state but still blocks idle on the affected frames. Hard lead-planner braking (`≤ -0.4 m/s²`) blocks idle immediately, while a smaller request (`< -0.15 m/s²`) must persist for about `0.2 s`; this keeps a stable lead's tiny gap correction from permanently suppressing coasting. Stop requests, FCW, forced deceleration, pedal input, experimental control, and invalid/stale planner inputs also block idle. Manual cruise deceleration uses the same lead checks and re-entry delay. For example, reducing cruise from `40` to `20 kph` can coast until `22 kph` with a `2 kph` release gap, then normal control finishes the slowdown; a lead that slows or closes the gap blocks idle immediately. The CAN output rechecks both raw leads without the display's lead-visibility delay.

Accel/resume cancels the current lower-limit approach until a new approach/target. The controller continues updating its engagement state during idle, and stale plans cannot keep commanding idle. These checks address software paths that can suppress acceleration; actual Hyundai SCC recovery after `ACCMode=0` still needs validation on supported hardware using recorded CAN/control data.

## Rapid limit changes and car-first selection

Car-first prefers the car's current limit, but a selected upcoming map limit can still take priority. At a map segment boundary or when an upcoming entry disappears, selection can return to the car's older limit.

Upcoming map limits are tracked before they enter the configured lookahead range. A candidate qualifies after fresh map messages span at least 1.5 seconds with the same limit and a consistent approaching boundary. Distance is checked against estimated travel between observations (15 m tolerance); a changed limit, distance jump, missing candidate, stale map, or observation gap over 2.5 seconds restarts qualification. Re-reading the same message cannot qualify it. Both increases and decreases use this check.

Once qualified, the existing lookahead and adaptation distances select the limit immediately, without an additional target delay. Brief unqualified entries ahead do not change the target. Current car and map limits apply immediately in both directions. Late upcoming entries also bypass qualification when the normal braking distance is reached or the boundary is within 1.5 seconds of travel. This preserves reaction to late restrictions, but those entries can still flicker.

The feed currently exposes only one upcoming limit and its distance, without a road or boundary ID. Distance progression is an approximation of boundary identity, and fresh publications can still contain cached upstream map data. This does not validate OSM correctness, suppress brief current-limit changes, or retain a confirmed entry after it disappears. Multiple upcoming segments, explicit boundary IDs, and upstream observation timestamps would allow stronger validation later.
