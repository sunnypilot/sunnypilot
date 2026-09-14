# Ford lateral maneuvers, one output channel at a time

Enable **Settings → Developer → Ford C0 / C1 test** on comma four while offroad. The Ford model-action controller must be enabled on a CAN FD Ford. This runs the existing lateral maneuver tool with a single output channel selected.

The suite uses the **normal lateral-acceleration targets**, converted to desired curvature by the normal maneuver tool. That request goes through the existing curvature/jerk limits and the normal Ford controller. **C0-only sends its normal C0 output with C1 zero. C1-only sends its normal C1 output, including P/I feedback, with C0 zero.** C2/C3 stay zero. The diagnostic does not replace the controller mapping, freeze a starting command, reset feedback, or inject a percentage of the field range.

At **15 mph**, it runs the standard step right, step left, 0.5 Hz sine and jitter through C0, then through C1. It repeats the same sequence at **20 mph**. Each maneuver retains the standard three runs: **48 completed runs total**.

The step includes the normal opposite-direction command; the sine and jitter keep the existing action arrays and timing. These tests therefore exercise turn-in and reversal through the real controller. Equal desired acceleration does not guarantee that either channel alone can achieve it. This measures the controller and vehicle together with one output selected, not the PSCM channel in isolation from controller feedback.

Use the same clear, straight test area as the regular lateral maneuver suite. Set ACC to the displayed speed and engage lateral control. The normal maneuver readiness/countdown checks apply. Driver input, disengagement or invalid inputs stop the attempted run. **Completed runs remain completed; the interrupted run retries when the standard readiness conditions recover.** After steering intervention alone, another disengagement is not required. Brake/ACC disengagement requires reengaging ACC and lateral control.

The former pulse-specific 15° wheel and 1 m/s² aborts are gone. They would cut off normal maneuvers. Normal controller limits, vehicle fault handling, field bounds, driver intervention and a stale-plan watchdog remain. PSCM limit-reached uses the normal controller behavior, including its integral anti-windup, rather than terminating the maneuver.

When “Maneuvers Finished” appears, finish the route and upload all logs. Going offroad or restarting clears the test toggle and resets suite progress.

Generate the report as usual:

```sh
python openpilot/tools/lateral_maneuvers/generate_report.py DEVICE/ROUTE
```

Channel runs use the standard lateral maneuver report, grouped by maneuver, speed and channel. It shows desired versus measured lateral acceleration, actual wheel angle, speed/jerk/roll, and decoded C0/C1 CAN commands. The report checks that the unused field remained zero. Archived raw-pulse routes still use their original report.
