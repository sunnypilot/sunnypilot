# Coordinated controller: residual wheel-angle correction

Route 17a contains sustained small wheel-angle errors without PSCM limitReached. At 230–250 seconds the request is about -1.55 degrees while the wheel remains near zero. Other steady bends miss in either direction. The nominal inverse/encoder already closely meets its own internal curvature target, so precise encoding alone does not eliminate the observed residual. Actual PSCM calibration, load and unobserved state remain possible sources; a fixed directional offset would not fit the observations.

The coordinated controller now adds a bounded integral trim to the angle passed into its inverse. The model/action target remains the reference and remains unchanged in carControl. Both C0 and C1 are still allocated together. This is steering-angle feedback, not a lateral-position measurement, and cannot correct a model target that places the truck on a line.

## Tuning and lifecycle

- Integral gain: **0.2 / second**. This is new tuning, not a recovered firmware constant and not gainless control.
- Trim limit: **±2 steering-wheel degrees**. Clipping the integration error to ±2 degrees limits normal accumulation to **0.4 degrees/second**.
- Learn only with error ≤5 degrees, wheel speed ≤5 degrees/second, and vehicle speed ≥2 m/s. These trial thresholds focus adaptation on small, slow tracking instead of turn-entry lag.
- Ford does not populate `steeringRateDeg`. Wheel speed is derived from successive measured angles with a 0.1-second filter to suppress quantization. This filter only guards trim learning/release; it does not filter the normal angle request.
- Freeze growth at the inverse acceleration limit, either command field bound, or fresh PSCM limitReached. Opposing error may reduce trim toward zero.
- Outside the small/slow tracking region, an opposing error clears old trim **before** allocation. This prevents learned correction from opposing a fast unwind or large reversal. Resetting can remove up to 2 degrees immediately; the accumulation-rate limit does not apply to this reset.
- steeringPressed freezes trim without cutting the base request. Actual disengagement, invalid inputs, faults, or fresh PSCM override/denial reset it with the normal inactive request.
- No new proportional correction. No persistent learning across engagements. Diagnostics add requested angle, trimmed inverse input, applied trim, and whether learning is permitted.

The 2-degree bound covers the roughly 1–1.6-degree steady residuals motivating this experiment. The slow gain and small-error/motion conditions deliberately limit adaptation during transients. They are an initial experimental calibration, not universal Ford tuning or a proof of stability.

The existing default-off Coordinated C0/C1 gate remains the selector. Upstream fallback, v23, geometry and joystick selections are unchanged. Existing field bounds, acceleration allowance, mode, packet cadence, driver override and fault handling remain in force.

## Validation and limitations

The new regression drives the production adapter and Ford CAN packer with a persistent ±1.5-degree error. It fails on baseline `6aa35bc1f` because the command never builds residual correction, and passes after this change. A synthetic first-order wheel response with a known additive mismatch also tests convergence through the packed-command observer and nominal angle stage. That deliberately simple plant is a software regression, not an identified PSCM model or evidence of onroad smoothness.

538 focused controller tests pass. They cover selection and upstream fallback, corrected yaw, message-reader integration, actual packet observation, command bounds, persistent errors of both signs, no learning from large lag/fast motion/crawl, trim bounds, driver touch, override/disengagement reset, acceleration/PSCM anti-windup, and prompt removal of opposing trim during reversal/unwind. Ruff and whitespace checks pass.

Frozen replays compare this change with `6aa35bc1f` on routes 172, 175, 177 and 17a using their logged calibrated carControl yaw. Additional archived 166/16a wobble/turn sensitivity runs use retained raw CAN yaw in **both** variants: their original calibrated vectors were unavailable locally, so these are not exact replays of the current yaw-corrected controller. No production raw-yaw fallback is introduced. Missing history starts an independent replay interval; it is not bridged or represented as a vehicle restart. PSCM timestamps are converted from extracted seconds back into nanoseconds before freshness checks.

The four calibrated-yaw routes cover 206,019 adapter/packer updates per variant; the two sensitivity routes bring the total to 372,927 per variant. Activation matched baseline throughout, with no latched prediction faults, nonzero C2/C3, field-bound violations, or added acceleration-limit clipping. All fresh override/denial samples remained inactive. Across ten archived wobble windows the largest increase in fitted nominal internal-angle oscillation was 0.021 degrees peak-to-peak; this is a command-model proxy, not measured new wheel motion. Across 141 nominal 25/50/100-degree crossing comparisons, the largest later entry was 11.4 ms and later exit 19.8 ms. Changed angle levels can move threshold crossings; these are not measurements of a new plant delay. Candidate pipeline p95 on the development Mac was 0.125–0.140 ms across the four full routes, about 0.001–0.002 ms above their paired baselines. Comma timing is unmeasured.

The first candidate was rejected for retaining correction through reversal. A subsequent replay exposed that the Ford steering-rate field was unpopulated; the final code and regression derive rate from actual angle samples. All metrics above use that final implementation.

Artifacts and runnable local scripts are under `.cache/ford_joint_trim`. Measurements and model outputs stay frozen. A trim reaching its bound on that tape does not demonstrate that the truck would need the full trim: the recorded wheel cannot respond to the changed commands. Command/proxy comparisons can reject obvious regressions; they do not predict a new lane position, steering feel, or closed-loop stability. The next drive must establish whether residual wheel error and lane placement improve without reintroducing wobble or hanging exits.
