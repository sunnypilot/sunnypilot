🚗 Features
---

### All Features
* [**NEW❗ Modified Assistive Driving Safety (MADS)**](#new-modified-assistive-driving-safety-mads) - openpilot ALC and Hyundai SCC can be engaged independently of each other
* [**NEW❗ Dynamic Lane Profile (DLP)**](#new-dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence
* Quiet Drive - Toggle to mute all notification sounds (excluding driver safety warnings)
* Force Car Recognition - Use a selector to force your car to be recognized by Openpilot

🚗 Highlight Features
---

### NEW❗ Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and Hyundai SCC/ACC can be engaged independently of each other
* `LFA` button (only on newer HKG vehicles) or `CRUISE (MAIN)` button toggles openpilot ALC
* `SET-` button enables Hyundai SCC/ACC
* `CANCEL` button only disables Hyundai SCC/ACC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC
* `GAS pedal` press will not disengage openpilot ALC or Hyundai SCC/ACC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match Hyundai stock behavior

### NEW❗ Dynamic Lane Profile (DLP)
Dynamic Lane Profile (DLP) aims to provide the best driving experience with staying within the lane confidently. Dynamic Lane Profile allows openpilot to dynamically switch between lane profiles base on lane recognition confidence level on road.
