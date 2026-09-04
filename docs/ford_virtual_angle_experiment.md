# Ford virtual angle controller

Replaces the failed Shared Path experiment from `daeb966d0`. That controller
fed temporal model displacement and heading directly into C0/C1 and oscillated
on route78. The replacement tracks `controlsd.desired_curvature`, after its
existing planner selection and curvature limits. Measured curvature comes from
the same vehicle model, steering angle, angle offset and roll used by
`LatControlAngle`. Zero error therefore corresponds to the same planned angle
at a given speed and calibration.

## Selection and rollback

Vehicle → Ford → **Virtual Angle Controller (Experimental)** is default off.
Selection happens at controlsd startup following an offroad-to-onroad cycle.
It requires CAN FD, `FORD_F_150_LIGHTNING_MK1`, and EPS firmware
`RL38-14D003-AA`. This combination was verified against route78's actual
CarParams. Other vehicles retain the previously selected controller.

The old `FordSharedPathController` setting, registry entry, selector, module and
UI toggle are removed. An old saved value cannot activate the replacement;
there is no migration to the new `FordVirtualAngleController` key. An obsolete
parameter file may remain until normal parameter cleanup, but is never read.

When selected, Virtual Angle takes priority over PSCM Coefficient Observer.
Turning it off and cycling offroad/onroad restores the previous default or
observer selection. No setting on a device has been enabled by this change.

## Control law and initial values

The implementation is `openpilot/selfdrive/controls/lib/ford_virtual_angle.py`.
C0 carries the planned nominal lateral acceleration (`v² × desired curvature`).
C1 carries bounded proportional, integral and measured-rate feedback. C2 and
C3 remain zero. There is no second fast input from raw model pose.

| Quantity | Initial value |
|---|---:|
| Nominal C0 per acceleration | 0.6015625 m / (m/s²) |
| Nominal C1 per corrective acceleration | 0.030078125 rad / (m/s²) |
| Proportional / integral / rate gains | 0.35 / 0.15 / 0.04 |
| Measurement-rate filter time constant | 0.15 s |
| Response interval | CarParams.steerActuatorDelay, 0.20 s on this vehicle |
| Corrective acceleration / integral bounds | ±1.5 / ±0.75 nominal m/s² |
| Host C0 / C1 slew | 1.5 m/s / 0.10 rad/s |

**These are experimental initial values, not gains identified or validated on
the Lightning.** The nominal conversion comes from ML3V-BD firmware algebra.
It does not establish RL38 channel sensitivity, available wheel authority or
stability. Host slew limits likewise make no claim about internal RL38 limits.

The reference history contains limited, Float32/CAN-quantized C0 requests.
Feedback compares the measured curvature with the reference issued one
response interval before the **measurement timestamp**. It subtracts the
nominal C1 correction still pending within that interval from the proportional
error. This is a simple delay compensation assumption, not a learned plant or
an EPS acknowledgment. The input target already includes upstream delay
handling and is not extrapolated again.

Steering rate is derived only when the measurement timestamp advances; Ford's
generic steeringRateDeg field was zero in these logs. There is no constant-rate
future-wheel projection. The integral is bounded, discharges with turn release,
and stops accumulating during command/rate limits, reported host limiting,
driver input, or a correction increase with little observed response. Driver
input clears feedback bias and slews C1 toward zero; planned C0 remains active
when the upstream system still authorizes lateral control.

Invalid/stale inputs, backward timestamps, control gaps over 100 ms, or speeds
outside 0.3–55 m/s clear state and invalidate the path. controlsd also clears
the outgoing latActive request, producing inactive Ford lateral mode instead
of an active zero path. Valid control resumes from reset slew state. The
measurement and reference freshness limit is 150 ms.

## Validation and limits

85 focused tests passed: controller state/timing, accumulated slew across cycle
rates and both turn directions, anti-windup, override and release, hypothetical
delayed plants, real Float32-to-Ford-CAN packing, actual controlsd branch wiring
and logging, native parameter defaults, settings schema and existing Ford path
controllers. Ruff and settings generation checks passed.

The route78 regression fixture covers 27–41 s and contains only steering,
reference, timing and command signals, with source and fixture hashes. Replaying
the new controller against the recorded motion reduces the 1.78-Hz command
amplitudes by **93.1% for C0 and 99.2% for C1** over 32.5–36.1 s. The regression
also checks the onset before the first steeringPressed flag. These results
show reduced command forcing, **not elimination of physical wheel oscillation**.

Route77's B7 plateau receives median C0/C1 of 0.89 m / 0.009 rad in replay,
versus recorded 0.73 m / 0.0816 rad. The correction points toward the measured
undertracking, but there is no evidence yet that physical turn authority is
preserved or improved. In another tight left, the planner target itself
understates model-path curvature; tracking it more faithfully cannot solve
that reference error. These limitations prevent calling this a proven better
controller. Hardware validation must establish damping, authority and release.

Startup logs identify the selected class. `Ford virtual angle experiment`
records reference/measurement timestamps and ages, reference/measured/delayed
curvature, P/I/D, pending correction, integrator freeze/stall state and all four
commands at 5 Hz. A short next capture containing engagement, turn-in and release
can distinguish reference error, feedback response and insufficient authority.

Reproduce focused checks from the repository environment:

```sh
python -m pytest -q openpilot/selfdrive/controls/tests/test_ford_virtual_angle.py openpilot/selfdrive/controls/tests/test_ford_controlsd_logging.py openpilot/selfdrive/controls/tests/test_ford_path.py openpilot/sunnypilot/sunnylink/tests/test_settings_schema.py
python openpilot/sunnypilot/sunnylink/tools/compile_settings_ui.py --check
```

Full local route analysis and replay are in
`analysis/controller_search_20260904/replay_virtual_angle.py`. The historical
recorded-motion failure witnesses remain failures by design: editing a
controller cannot alter an already recorded drive.
