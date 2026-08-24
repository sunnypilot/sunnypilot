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

Enables the special lower-speed-limit decel behavior when lower map lookahead is active and there is no lead car.

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

Stops the lower-limit decel override once ego speed is within this margin above the adjusted speed-limit target. Example: with a `50 kph` target and `5.0`, the override releases at `55 kph`.

Allowed range: `0.0` to `30.0` kph

Default: `5.0`

`speedLimitMaxDecelMps2`

Caps normal no-lead SLC decel. This does not cap the special lower-limit decel modes while they are active.

Allowed range: `-2.0` to `0.0` m/s^2

Default: `-0.5`

`longitudinalNoLeadDecelMode`

Controls intentional no-lead cruise-source decel, outside emergency/lead/stop cases. It does not idle for small speed-hold corrections.

This is the broader gas-car test mode. If `"idle"` behaves well, it can replace most fixed/dynamic decel tuning for no-lead slowdowns.
Pressing accel/resume or increasing the cruise target clears idle and blocks it briefly so the controller sends an active non-idle output again.
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
