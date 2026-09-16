# Ford feedback continuity trial

The v16 experimental controller uses Ford CarState's existing filtered
`steeringPressed` signal to detect driver input. It no longer independently
checks the same 1 Nm threshold on each raw torque sample. Fresh PSCM driver
override (`limit == 3`) and nonfinite torque still immediately clear feedback.
Filtered driver input also still clears both P and I; nothing changes in Ford's
CarState filter or the vehicle's disengagement logic.

The full rlogs from `84865544361f55cb/0000015a--ef86556819` and
`84865544361f55cb/0000015b--22b70521d4` contain short torque crossings with
`steeringPressed == false`. At 15a +196.19 s, two samples reach 1.0625 Nm.
The old duplicate check drops proportional correction and clears the integral,
then restores proportional correction when torque falls. During the large left
in 15b, similar pulses at +168.06, +168.14, and +168.28 s repeatedly interrupt
correction. The logs establish these interruptions, not whether each pulse was
deliberate driver input. v16 follows the same driver-input classification already
used elsewhere in controls, instead of maintaining a second interpretation.

## Scope

This affects the opted-in Ford C0/C1 controller, with either action or geometry
as its reference. Disabling `FordModelActionController` still selects upstream
Ford control. No new toggle is needed. Diagnostics identify
`model-action-curvature-c0-feedback-v16-filtered-driver`.

Reference selection, preview, smoothing, gains, integration, command bounds,
PSCM limit handling, and message timing are unchanged. This is a feedback
continuity change, not a wheel-speed limiter or a general cure for abrupt
low-speed motion.

## Validation

The regression uses the actual shared `CarStateBase.update_steering_pressed`
filter with Ford's count of 5. Two-sample pulses in either direction preserve
feedback; sustained input clears it on the first filtered pressed sample.
PSCM driver override remains immediate. Before the change, 4 of the 5 new
tests failed; afterwards all 5 passed. Integration tests exercise publication
through controlsd and the real CAN sender. The related controller, path, and
geometry suites pass: **534 tests**.

The paired replay uses native control cadence and identical recorded
references, steering, speed, driver state, and PSCM status. Baseline is commit
`18ded0380045c29520cf1f690688e48ebad043d8`, with fixed 7 m C0. It replays
44,145 control cycles and checks CAN serialization of 4,415 candidate commands.
All commands remain finite and within field bounds; C2/C3 remain zero. Every
recorded filtered driver input or fresh PSCM override clears feedback.

Counts below use consecutive valid active commands below 15 mph, with sample
spacing below 30 ms (normally 10 ms). A "step" is an adjacent command change,
not a measured wheel movement or an inferred comfort threshold.

| Metric | 15a old → new | 15b old → new | Combined old → new |
|---|---:|---:|---:|
| Feedback enabled/disabled transitions | 61 → 25 | 107 → 40 | 168 → 65 |
| C0 steps larger than 0.25 m | 52 → 21 | 85 → 39 | 137 → 60 |
| C1 steps larger than 0.05 rad | 36 → 18 | 32 → 17 | 68 → 35 |

The baseline matches recorded C1 within Float32 precision on both routes.
Maximum C0 mismatch is Float32 rounding on 15a and one 0.01 m command quantum
on 15b. Logged publication time approximates the core call time, and the replay
cannot reproduce every retained-message service-health check. These limitations
are reported with the replay results, rather than assuming exact reproduction.

Preserving I can also sustain stronger commands. Time at the C1 field bound
increases from **2.57 to 3.81 s** on 15a and **6.70 to 7.12 s** on 15b.
The candidate's wheel response and unwind cannot be inferred from the recorded
motion: the physical vehicle did not receive these candidate commands.

Reproduce for each extracted route directory:

```sh
PYTHONPATH=.:opendbc_repo python tools/ford_pscm_lab/filtered_driver_replay.py \
  --source .cache/ford_route15a/rlog_full \
  --output .cache/ford_filtered_driver/15a
```

Input and controller hashes and detailed results are in
`ford_filtered_driver_validation.json`.

## Why not add preview at the same time?

The geometry and learned action are separate model outputs; code does not
require them to agree. Geometry converts previewed heading and initial heading
rate to curvature. For fixed heading perturbations, sensitivity grows as speed
falls. This can magnify frame-to-frame plan revisions at low speed; it does not
prove the resulting plan is incorrect. The model's training objectives cannot
be established from inference code alone.

A separate frozen-plan check added 0.1 or 0.2 s of geometry preview. Selected
turn exits relaxed earlier, but some low-speed reference changes got steeper.
For example, on 15b the maximum target-angle change over 0.2 s rose from about
352 degrees/s to 386 and 429 degrees/s. These are reference changes, not wheel
rates. Extra preview is therefore not included in this feedback continuity
trial. Remaining sharp requests and geometric exit rebounds need to be judged
separately from command interruptions.
