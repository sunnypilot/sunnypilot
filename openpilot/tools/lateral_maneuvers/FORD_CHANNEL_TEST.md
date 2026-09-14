# Ford C0 / C1 comparison

This separate diagnostic measures the wheel response to C0 and C1 pulses at **15 and 20 mph**. It requires the Ford model-action controller and a CAN FD Ford. It makes no change to normal controller tuning.

1. While offroad, enable **Settings → Developer → Ford C0 / C1 test** on comma four. This selects the test for the next onroad session and turns off the other maneuver/joystick modes.
2. Use a clear, straight test area with room for a lateral deviation. Engage ACC and lateral control, then hold the speed shown on screen. Testing requires two continuous seconds of steady, nearly straight driving without steering or pedal input. It will not start if you are manually holding the accelerator.
3. At 15 mph it runs **C0 right, C0 left, C1 right, C1 left**. Repeat those four trials at 20 mph. Each trial holds the starting commands for 0.5 seconds, pulses one field for 1 second, then restores the starting commands for 2 seconds to observe release.
4. Follow the displayed phase and target speed. Normal model tracking resumes between trials and after completion. If a trial aborts, **disengage and reengage** to retry it; clearing steering input alone does not restart the pulse. Stop if the area no longer provides room for the test.
5. After “Ford tests finished,” end the route and upload all logs. The test toggle clears when the device returns offroad or the manager restarts.

The pulse is **25% of each field's maximum magnitude**: **±1.28 m C0** (25% of 5.11 m, rounded to the 1 cm CAN step) or **±0.125 rad C1** (25% of 0.5 rad), added to the captured starting command. These are path fields, not wheel angles or percentages of steering torque. The amplitudes and duration were increased after the initial 0.03 m / 0.01 rad, 0.5-second probes produced little reported wheel movement. Equal percentages are not assumed to produce equivalent steering. The other field remains fixed. C2/C3 stay zero, and PI correction does not modify the test commands. Release returns to the captured baseline; it does not deliberately countersteer or promise that the wheel immediately centers.

Driver input, lost ACC/lateral engagement, invalid or stale inputs, PSCM denial/limit status, or excessive response abort the test. The diagnostic additionally stops requesting test control above 15° wheel movement from baseline or 1 m/s² measured lateral acceleration. A pulse may therefore abort before its full second. These thresholds trigger an abort after measured movement; they do not guarantee the physical response cannot overshoot them, model the PSCM, or change normal driving limits.

Generate the report with the existing command:

```sh
python openpilot/tools/lateral_maneuvers/generate_report.py DEVICE/ROUTE
```

The generator detects channel trials and plots **C0 sent, C1 sent, actual wheel movement and speed**. It measures thresholded movement onset from the changed CAN packet, peak movement, and residual angle at the end of release. It flags incomplete, intervened, limited, stale, or non-isolated trials for exclusion. Standard lateral maneuver reports keep their existing behavior.

One run in each direction provides a first comparison, not a reliable universal plant model. Compare timing alongside response strength: a larger response can cross a movement threshold sooner even with identical delay. These short pulses do not validate sustained intersection turns.
