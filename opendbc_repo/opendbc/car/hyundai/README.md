# About Angle Steering, Baseline Model, and ISO Safety Limits

## Overview

The baseline vehicle model serves as our safety reference point for establishing universal control parameters across our entire vehicle fleet. This approach ensures that all vehicles operate within ISO safety standards regardless of their individual physics characteristics.

## How It Works

For any given speed and driving conditions, we query each vehicle model with the question: "What's the maximum steering angle I can apply right now while staying below the ISO standard limits for lateral acceleration and jerk?"

Each vehicle model responds differently based on its unique physics characteristics:
- **Baseline Vehicle Model**: Has the most restrictive limits - requires the smallest steering angles to stay within ISO safety thresholds
- **Current Vehicle Model**: May be able to handle larger steering angles while remaining within the same ISO safety standards, depending on its physical characteristics

## Safety Logic

Both the baseline and current vehicle models target the same ISO safety limits. The key difference is that the baseline vehicle's physics require more conservative steering inputs to stay within those standards.

By applying the baseline vehicle's more restrictive steering limits to all vehicles in the fleet:
- Every model stays well within ISO safety thresholds
- No vehicle will breach safety standards regardless of its individual characteristics
- We maintain a consistent safety margin across the entire fleet

If we instead used a less restrictive model as our baseline, any naturally more restrictive vehicles in the fleet would exceed ISO standards and create unsafe driving conditions.

## Implementation Details

### Two-Layer Validation Process

We use a two-layer validation approach to balance vehicle-specific optimization with baseline safety:

1. **Current Vehicle Model Calculation**: We first calculate the optimal steering limits from the current vehicle model, which determines the best steering angle based on that vehicle's physical characteristics and desired maneuver.

2. **Baseline Model Validation**: We then pass the current vehicle's requested steering command through the baseline model as a final safety filter.

This two-layer approach is essential because while the current vehicle model may generally be more capable, it might sometimes request smaller jerk or lateral acceleration values to achieve specific driving goals. The baseline validation ensures that regardless of what the current vehicle requests, we never exceed the safety limits of our most restrictive vehicle.

### Special Case: Driving the Baseline Vehicle

When actually driving the baseline vehicle itself (e.g., Santa Fe), we apply an additional 80% ISO cap since that vehicle would otherwise operate right at the ISO safety threshold. This extra margin ensures safe operation even for our most restrictive vehicle model.

## Example Implementation

### Baseline Vehicle: Hyundai Santa Fe
Due to its physics characteristics, the Santa Fe requires smaller steering angles to remain within ISO safety limits.

### Current Vehicle: Ioniq 5 PE
Due to different physical characteristics, the Ioniq 5 PE can handle larger steering angles while still remaining within the same ISO safety standards.

By using the Santa Fe's conservative limits across all vehicles, we ensure the Ioniq 5 PE operates well within its capabilities, while preventing the Santa Fe from exceeding its safety thresholds.
