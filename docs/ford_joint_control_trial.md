# Coordinated C0/C1 steering trial (v24)

This default-off trial turns the normal action-derived desired steering angle into a jointly selected C0/C1 pair. It estimates the held fields and curvature filter of an older Ford PSCM and chooses one command whose predicted next-update error is no worse than a C1-anchored alternative. Among those candidates it minimizes error over the complete return to the steady pair, including the filter tail. It does not retain a future command plan or classify turns into maneuver states.

The later [residual wheel-angle trim](ford_joint_centering_trim.md) adds a small, bounded integral correction around this nominal encoder. The original validation below describes the earlier versions; the trim has separate validation and is not gainless.

## Select and revert

In sunnylink → Vehicle → Ford Settings, while offroad:

- **Selected-Action Path Tracking (Experimental): ON**
- **Model Geometry Reference: OFF**
- **Coordinated C0/C1 Steering (Experimental): ON**

Apply with an offroad-to-onroad cycle. The new `FordPscmJointControl` parameter defaults to false. Turning it off restores v23 selected-action control. Turning the master Selected-Action setting off restores upstream Ford control, regardless of this stored setting. Geometry mode and Joystick Debug Mode keep their existing paths. C0 distance selection does not affect this trial.

The integration accepts Ford CAN FD platforms, following the existing master gate. Compatibility with each PSCM calibration is not established.

## Live integration

`controlsd` retains the normal action source, curvature limits, vehicle-model conversion, input freshness checks and steering-angle target. With the trial selected, its existing Ford adapter is a validity carrier with zero P/I gains; it supplies no additional path correction. `card` performs the joint allocation immediately before the existing Ford CAN packer. It negates the encoder's CAN-coordinate output into the OP path interface; the packer negates it back on transmission.

C2/C3 remain zero. Existing field bounds, mode 2 and immediate ramp remain unchanged. The observer advances at an estimated 8 ms firmware cadence using the decoded packets actually queued to panda. Queueing is not a PSCM acknowledgment. It retains held/filter estimates while disengaged or overridden and applies the recovered inactive slew to mode-0 packets. A fresh limitReached status does not freeze the target; the PSCM's explicit override or denial inhibits this trial's lateral command. Like upstream Ford, steeringPressed alone does not zero the path. Longitudinal controls are untouched.

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

## Route 175 follow-up

Route `00000175--9529c33e36` ran `99b3fb03e` with v24 enabled. All ten full rlogs contain no System Lagging alert. Remaining communication warnings identify deviceState and, sometimes, managerState. DeviceState publication timestamps contain gaps up to 8.06 seconds; manager polls that service and falls back to its one-second timeout. The recorded CPU samples still show card/controlsd/selfdrived close to one core in sustained sections, so further optimization is useful independently of the health-process stalls.

Two wheel pauses near 100 and 115 degrees follow short steeringPressed detections. At about 175.35 and 176.94 seconds, the existing override handling transmits mode 0 / zero C0/C1 for approximately 87 and 117 ms, then rebuilds the request. Those pauses do not show limitReached. None of the 1,710 active v24 diagnostic samples reports the inverse acceleration allowance clipping the target. The user reported small left corrections against a rightward tendency, so these detections cannot be classified as false driver input. Override behavior is unchanged.

The bookmark marks a moderately good but slightly wide left turn. It contains brief limitReached states with continued mode-2 commands, rather than a frozen command. Wheel-tracking error remains; this route is not evidence of closed-loop equivalence to another steering platform. An 8.71-second carState recording gap around 290.55–299.26 seconds, with other card streams continuing and buffered diagnostics arriving later, is excluded from tracking statistics.

The additional encoder optimization reuses the already-computed C0/C1 calibration gains, constructs the same sorted candidate grid with fewer NumPy temporaries, and decodes fixed calibration entries once. Relative to `99b3fb03e`, all nine search outputs matched exactly in 600 deterministic stress cases and 3,420 comparisons using active route-175 states at both tick counts. Another 20,000 grid-boundary comparisons matched. A 6,000-cycle adapter/CAN/observer exercise, including stop, override, reengagement, steps and reversals, produced exactly the same packed commands and observer states.

On the development Mac, recorded-state selection p95 decreased from 0.174 to 0.102 ms (1.63× aggregate speedup). Full pipeline p95 decreased from 0.199 to 0.162 ms (1.24× aggregate speedup). These local measurements do not establish comma scheduling latency, and there are scheduler outliers in both runs. No target, gain, bound, override rule, or steering command was intentionally changed.

The hardwared patch avoids redundant synchronous Params removal for hidden alerts whose unused extra text changes, and routes the Tici-support alert through the same change-only helper. Initial cleanup, visible text updates, and clearing remain synchronous; failed writes are retried. An unchanged hidden-temperature alert reproduces the unnecessary blocking operation on the previous implementation. The logs do not identify which blocking call caused every on-device stall. Slow-stage timing now records operations exceeding 100 ms to distinguish thermal/system reads, Chestnut status, startup/engagement parameters, power reads, publication, and persistence. Watchdog thresholds and health checks remain unchanged.

Validation: 524 focused controller/hardware tests passed; Ruff and `git diff --check` passed. Diagnostic artifacts, route data, and benchmarks are local under `.cache/ford_v24_followup`; the visual report is `route-175.html` in the existing report directory. No truck validation of this follow-up optimization is claimed.

## Route 175 yaw bias and touch response

The previous inverse consumed raw Ford CAN yaw. In clean near-steady small-request samples, it differs from sign-normalized calibrated `carControl.angularVelocity[2]` by a median -0.00767 rad/s. Through the recovered steady angle equation, the difference corresponds to about -3.08 degrees of steering; the observed median actual-minus-requested error was -3.36 degrees. Four continuous steady windows show observed errors of -2.09, -2.39, -3.17 and -2.95 degrees, compared with nominal yaw-source effects of -1.86, -1.90, -2.97 and -3.45 degrees. This supports an input-bias explanation; it does not establish which internal yaw signal the actual PSCM uses or prove the onroad correction.

The coordinated controller now uses negative calibrated car-frame yaw Z, matching CAN/pinion coordinates. This is the existing pose published by controlsd, without a fitted trim or additional feedback gain. The v24 validity carrier requires calibrated, valid, healthy and fresh deviceMotion; missing or invalid yaw disables the request rather than falling back to the biased raw signal. Diagnostics record both yaw inputs. Other controller selections retain their existing input behavior.

The extra v24 steeringPressed gate is removed. A light touch no longer directly forces zero C0/C1 and mode 0, and the observer retains its held state. Actual disengagement, steering faults, freshness failures, and a fresh PSCM override (limit 3) or denial still inhibit the command. This changes the software request continuity, not the PSCM's internal torque blending or safety permissions.

Regression coverage includes biased raw yaw with unchanged calibrated motion, yaw sign, missing/nonfinite/out-of-range yaw, touch continuity, retained PSCM override/denial, and execution of controlsd's motion-health gate with v24 enabled and disabled. The original eight bias/touch cases failed before the fix. All 524 focused controller tests now pass. Frozen replay compares yaw-only, touch-only, combined and baseline commands through the actual adapter and CAN packer; measurements remain recorded, so it cannot demonstrate the resulting wheel motion or smoothness. Artifacts are under `.cache/ford_v25_bias`.

All four variants completed 52,526 recorded updates each without latched prediction faults, nonzero C2/C3 or field-bound violations. The missing carState interval is treated as an independent replay boundary, not bridged or claimed as a vehicle restart. All recorded active samples had the required calibrated yaw and recorded motion-health fields. Yaw-only preserved the baseline active count; the combined change added 5,988 active updates, all during steeringPressed with lateral control otherwise permitted. Fresh PSCM override/denial remained inactive. In the 174–178 second wheel-pause window, the extra 21 mode-0 updates disappeared. No new acceleration-allowance clipping occurred. The four steady windows shifted the requested curvature leftward, consistent with correcting the measured right bias. Closed-loop bias and touch feel still require truck validation.

Replay-audit correction: the original four-variant `.cache/ford_v25_bias/replay.py` passed an extracted PSCM timestamp in seconds where the adapter expects nanoseconds. Its fresh-status branch therefore did not substantiate the override/denial claim above. The production freshness code and explicit-status unit tests were unaffected. The later [centering-trim validation](ford_joint_centering_trim.md) converts timestamps correctly and asserts inhibition on every fresh recorded override/denial sample.
