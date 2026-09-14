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

## Keyboard-triggered steps (ACC or MADS)

A laptop keyboard over SSH is enough. This mode keeps normal `controlsd` running, including ACC/MADS and the tested Ford formulas. **Do not enable stock Joystick Debug Mode:** that replaces `controlsd` and bypasses this controller. The keyboard tool selects its own transient mode and disables the automatic maneuver modes.

With the car off and openpilot offroad, SSH into the comma and run from `/data/openpilot`:

```sh
python openpilot/tools/joystick/ford_keyboard_control.py --speed 15
```

Leave that terminal connected, start the car, and engage lateral control. You may use **ACC**, or **MADS with manual accelerator input**. Hold the selected speed, 15 or 20 mph, within ±0.7 m/s (about ±1.6 mph). Braking, steering intervention, loss of lateral engagement, invalid data, or leaving the speed window aborts the current run. MADS is engaged normally; this tool does not enable it or override its engagement rules. Use a passenger to operate the keyboard while you drive in the test area.

| Key | Action |
| --- | --- |
| `1` / `2` | Select C0-only / C1-only for the next step |
| `V` | Select 15 / 20 mph for the next step |
| `+` / `-` | Adjust the next target by 0.25 m/s²; default 0.5, range 0.25–3.0 |
| `A` / `D` | Trigger one left / right step when the screen says Ready |
| `R` | Cancel the test and return to normal lateral control |
| `Q` or Ctrl-C | Cancel and exit the keyboard tool |

The strength is a **lateral-acceleration target**, not a percentage of the C0/C1 field range. The upper setting matches the existing normal lateral-acceleration limit; normal curvature/jerk limits and field bounds still apply. For a different starting strength, add `--accel 1.0` to the command. Settings changed during a run apply only to the next run.

Each keypress starts one **0.5 s baseline → 1.0 s step → 1.5 s release** sequence. The reference is the captured starting curvature plus the requested acceleration divided by current speed squared. Release returns the **target** to that baseline; it does not forcibly zero C1's normal P/I correction. The unused channel and C2/C3 remain zero throughout the sequence. Afterward, normal model following resumes with both channels. The terminal displays computed C0/C1, measured wheel angle, and PSCM limit status; the route also records actual transmitted CAN commands.

The tool requires two seconds of stable, straight driving before accepting a trigger. A keypress while unready or busy is discarded, not queued. **It never automatically starts another run or retries an interrupted one.** Losing the keyboard heartbeat for more than 0.2 s aborts the run; the normal controller also retains its independent stale-plan/run-duration checks. `R` and `Q` cancel only the test, not MADS or ACC. Disengage lateral control normally if you want it off. The keyboard mode clears when the car goes offroad or manager restarts.

If SSH disconnects or you exit the keyboard program, reconnect and run the same command. Reconnecting onroad is accepted only when keyboard mode is already selected; it does not enable a new driving mode. An interrupted step stays aborted and needs a fresh trigger.

Use the same report command above after uploading the route. Keyboard runs add a PSCM limit-status plot and markers for the baseline/step/release transitions. These test the real controller with one output selected; C1 feedback and the vehicle response are both part of the measurement.
