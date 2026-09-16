# Ford model geometry reference trial

`FordGeometryReference` changes the steering reference used by the existing
Ford C0/C1 feedback controller. It is default off and requires
`FordModelActionController` and a Ford CAN FD vehicle.

In Sunnylink's Ford settings, enable **Model Geometry Reference (Experimental)**
while offroad, then cycle offroad to onroad. Keep **Selected-Action Path Tracking**
enabled. Disable only the geometry toggle to compare with the previous model
action. Disable the controller toggle to restore upstream Ford control.

## Reference calculation

After modeld publishes the plan into the message builder, use its orientation
and orientation rate with the existing `get_curvature_from_plan` function:

```
curvature = 2 * heading_at_preview / (max(speed, 1) * preview)
            - initial_heading_rate / max(speed, 1)
```

The existing function stabilizes previews shorter than 0.3 seconds using the
0.3-second heading. The experiment uses the exact `lat_action_t` already supplied
to inference, including learned/fixed delay, model-specific smoothing allowance,
the Ford speed-dependent 0.4-second preview addition, and 75 ms frame/action
timing compensation. CTMV2 on the recent route has roughly 0.744 seconds of
preview below 15 mph. This is a time preview, not direct sampling at seven metres.

Apply the same model-specific lateral smoothing and standstill hold as the
original action, once per published model frame. Use the published plan itself,
without a separate Planplus multiplier. Both `modelV2.action` and
`drivingModelData.action` receive the selected curvature. Preserve the original
action's independent smoothing history and its acceleration/stop fields.

controlsd still applies its existing curvature/acceleration/jerk limits and
lateral maneuver override. Its desired curvature and desired steering angle now
describe the selected reference. The unchanged controller converts that same
reference into C0/C1 and closes the loop on measured steering. C0 distance,
C1 distance, P/I gains, driver arbitration, PSCM limit behavior, CAN cadence,
and field bounds are unchanged; C2/C3 stay zero.

Malformed/nonfinite/incomplete orientation data retains the original action
for that frame and resets geometry smoothing history. Existing model validity
and freshness gates still apply. There is no runtime mode swap during engagement;
the toggle is read at modeld startup.

## Logging

`modelDataV2SP.fordGeometryReference` records enabled/valid, associated model
publication time, original action curvature, raw geometric curvature, selected
curvature, preview, and smoothing time. `valid=false` while enabled identifies
fallback. A startup log also identifies action or geometry mode. The existing
Ford diagnostics continue to identify the unchanged v15 feedback controller.

## Offline validation

The tests cover signs/units across speed and preview, smoothing, release and
reversal, standstill, invalid geometry, message serialization, preservation of
the original action/longitudinal control, selection through actual controlsd
code, desired-angle logging, maneuver priority, and upstream fallback.

Three Lightning routes (149, 151, 157; CTMV2 and Tee Time) were replayed through
the current reference selection, upstream limiter, and controller using frozen
recorded steering/driver/PSCM measurements. Native controller cadence is retained;
every tenth command gets a CAN pack/decode check. Reference timing uses recorded
delay and the speed of the first control sample consuming each model. That speed
can differ slightly from modeld's original inference input. This is not a neural
replay or a prediction of wheel motion under modified commands.

Results and input hashes: `ford_geometry_reference_validation.json`.

```
PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/geometry_reference_validate.py \
  --output .cache/ford_geometry
```

Geometry is not uniformly earlier or stronger. The route 157 right-turn example
requests a large angle earlier; the problematic segment 9 left initially asks
for less and later asks for more. It hits command field bounds more often in
the frozen-measurement replay. Straight cohorts are defined by the original
action, so they also include disagreements about turn entry/exit. No claim of
improved physical tracking or stability follows from these offline results.
