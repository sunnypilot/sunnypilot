# **Modified Assistive Driving Safety (M.A.D.S.)**

Modified Assistive Driving Safety (MADS) aims to elevate the user's driving experience by modifying the behaviors of driving assist engagements.

!!! note
    This feature aligns closely with comma.ai's safety rules.

## Independent Engagement
MADS allows users to engage sunnypilot Automatic Lane Centering (ALC) for lateral control and Adaptive Cruise Control (ACC) or Smart Cruise Control (SCC) for longitudinal control independently.

??? note "Why This Feature Exists"
    While newer car models allow for independent engagement of lateral (steering) and longitudinal (speed) control, many older models and stock openpilot enforce engaging both controls together. MADS introduces this modern convenience to older models, effectively backporting a feature found in newer cars and providing users more flexibility.

## Dedicated Buttons
**Toggle for sunnypilot ALC**:

  - `CRUISE (MAIN)` button: Available on all supported cars on sunnypilot.
  - `LFA` button: Available on newer HKG cars.
  - `LKAS` button: Available on Honda, Toyota, and Global Subaru.

**Engagement**:

  - `SET-` button: Enables ACC/SCC.
  - `CANCEL` button: Disables ACC/SCC only.
  - `CRUISE (MAIN)` must be `ON` to use ACC/SCC.

!!! info
    The `CRUISE (MAIN)` button disables sunnypilot completely when `OFF`. This is strictly enforced in the panda safety code.

## Lateral Control on Brake Pedal
Dedicated toggle to handle Lateral state on brake pedal press and release:

- **ON**: Pressing the `BRAKE pedal` will pause Automatic Lane Centering.
