# Coordinated C0/C1 steering trial (v24)

This default-off trial turns the normal action-derived desired steering angle into a jointly selected C0/C1 pair. It estimates the held fields and curvature filter of an older Ford PSCM and chooses one command whose predicted next-update error is no worse than a C1-anchored alternative. Among those candidates it minimizes error over the complete return to the steady pair, including the filter tail. It does not retain a future command plan or classify turns into maneuver states.

## Select and revert

In sunnylink → Vehicle → Ford Settings, while offroad:

- **Selected-Action Path Tracking (Experimental): ON**
- **Model Geometry Reference: OFF**
- **Coordinated C0/C1 Steering (Experimental): ON**

Apply with an offroad-to-onroad cycle. The new `FordPscmJointControl` parameter defaults to false. Turning it off restores v23 selected-action control. Turning the master Selected-Action setting off restores upstream Ford control, regardless of this stored setting. Geometry mode and Joystick Debug Mode keep their existing paths. C0 distance selection does not affect this trial.

The integration accepts Ford CAN FD platforms, following the existing master gate. Compatibility with each PSCM calibration is not established.

## Live integration

`controlsd` retains the normal action source, curvature limits, vehicle-model conversion, input freshness checks and steering-angle target. With the trial selected, its existing Ford adapter is a validity carrier with zero P/I gains; it supplies no additional path correction. `card` performs the joint allocation immediately before the existing Ford CAN packer. It negates the encoder's CAN-coordinate output into the OP path interface; the packer negates it back on transmission.

C2/C3 remain zero. Existing field bounds, mode 2 and immediate ramp remain unchanged. The observer advances at an estimated 8 ms firmware cadence using the decoded packets actually queued to panda. Queueing is not a PSCM acknowledgment. It retains held/filter estimates while disengaged or overridden and applies the recovered inactive slew to mode-0 packets. A fresh limitReached status does not freeze the target; driver override or denial inhibits this trial's lateral command. Longitudinal controls are untouched.

A command-history gap over 100 ms, nonmonotonic clock or invalid prediction latches the trial inactive until the next onroad process start. The normal steering-fault alert reports the latched fault. There is no mid-turn switch to another controller. Diagnostics use `Ford joint path tracking` / `ford-joint-v24` and distinguish requested angle, reachable angle, estimated held state, proposed pair and packed pair.

## What the estimate does and does not know

Packaged numerical calibration comes from ML3V-14D003-BD / ML34-14D007-EDL. No executable firmware or private firmware image is shipped. Equivalence to the Lightning's RL38 firmware remains unverified. Internal integral is assumed initially zero and frozen; interaction is nominally 1.0; acceleration uses measured yaw × speed (no measured bank input); vehicle geometry comes from CarParams. These are explicit assumptions, not measured PSCM RAM. The model's 3 m/s² acceleration allowance is retained. It estimates an internal angle target before subsequent PSCM filtering/torque stages, not the future wheel angle.

## Validation

The production Python/C++ port reproduces every C0/C1 sample of the audited prototype in seven frozen windows from routes 166 and 16a. Held fields and filtered curvature also match; the largest angle-stage numerical difference is below 6e-14 degrees.

A separate replay executes the actual 100 Hz adapter and Ford CAN packer with the reconstructed response ticking at 125 Hz. Mean internal-target error, degrees:

| Window | Audited prototype | Actual 100 Hz adapter |
|---|---:|---:|
| 16a wobble 1 | 0.520 | 0.521 |
| 16a wobble 2 | 0.240 | 0.248 |
| 16a exit | 3.509 | 3.503 |
| 16a turn | 9.762 | 9.981 |
| 166 wobble 1 | 3.491 | 3.545 |
| 166 wobble 2 | 0.530 | 0.587 |
| 166 good left | 4.124 | 4.222 |

These are frozen measurements and nominal active-mode reconstruction, not observed improvements on the truck. The actual adapter made 12,031 packed command updates without a latched fault. The slowest per-window 99th-percentile cycle was 0.95 ms on the development Mac; comma hardware timing is unmeasured. Firmware-rate/calibration uncertainty remains material.

The focused suite exercises default-off selection, rollback, zero second PI, CAN signs/bounds/cadence, inactive state retention, interventions, limitReached, stale/nonfinite inputs, timing faults, real card hooks, parameter/schema registration, and inverse/forward numerical agreement.

The first enabled on-device trial exposed a message-type crash: the adapter returned a Cap'n Proto builder, while Ford's sender expects a reader and copies its actuator fields with `as_builder()`. The adapter now returns a reader. Regression coverage passes its output unchanged through `CarInterfaceBase.apply` and the production Ford sender, including the actual card hook with active, inactive and driver-override inputs. The earlier harness converted the output to a reader itself and hid this integration error. The regression also checks that the incoming message is not mutated and all fields other than the selected lateral-active state are preserved.

Run:

```sh
python -m pytest openpilot/selfdrive/car/tests/test_ford_joint_control.py \
  openpilot/selfdrive/car/tests/test_ford_pscm_status.py \
  openpilot/selfdrive/controls/tests/test_ford_model_action*.py \
  openpilot/sunnypilot/sunnylink/tests/test_settings_schema.py
```

Build the native kernel through SCons. On the development checkout, its real SConscript and native parameter library were compiled successfully. A complete root build could not run because the checkout lacks the msgq/rednose SCons tool submodules. No on-device build or road validation is claimed.

The trial's question is whether coordinating both channels preserves entry while reducing unnecessary correction during release. Offline results justify the opt-in comparison; they cannot establish smoothness or closed-loop stability.

## Runtime optimization after route 174

Route 174 ran v24 on `528ed3615` and recorded System Lagging during turns. Full rlogs show card using about 63% of one CPU core during the first alert; card, controlsd and selfdrived share that core and priority, and their combined measured load was about 101%. This supports CPU contention, not a PSCM limit, as the explanation for this alert. Comma timing must still be checked after the optimization.

The search now rejects candidates that fail its existing immediate-error constraint before evaluating their full return. Within each selection it also reuses return costs for identical predicted states and prefix costs. No cache survives the selection, and the candidate set, full-return policy, scoring, tie breaks and command cadence are unchanged.

Compared with the original native library built at the same optimization level, all nine outputs matched exactly in 600 deterministic stress cases and 720 comparisons using the 360 active logged states from route 174 at both firmware tick counts. On the development Mac, the recorded-state benchmark's 95th-percentile selection time fell from 0.317 ms to 0.090 ms; aggregate speedup was 1.47×. The broader stress benchmark improved 5.41× in aggregate. These are local encoder timings, not measured post-fix comma CPU utilization or a guarantee of system scheduling latency. Frozen pre-optimization commands and costs are also covered by the regression suite.
