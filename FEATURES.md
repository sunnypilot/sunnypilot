🚗 Features
---

### All Features
* [**NEW❗ Modified Assistive Driving Safety (MADS)**](#new-modified-assistive-driving-safety-mads) - openpilot (Automatic) Lane Centering (ALC) and ACC/SCC can be engaged independently of each other
* [**NEW❗ Dynamic Lane Profile (DLP)**](#new-dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence
* Quiet Drive - Toggle to mute all notification sounds (excluding driver safety warnings)
* Force Car Recognition (FCR) - Use a selector to force your car to be recognized by openpilot

🚗 Highlight Features
---

### NEW❗ Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and ACC/SCC can be engaged independently of each other
* Dedicated button to toggle openpilot ALC:
    * Newer HKG cars: `LFA` button
    * Most HKG cars, Subaru: `CRUISE (MAIN)` button
    * Honda, Toyota (Subaru coming soon!): `LKAS` button
* `SET-` button enables ACC/SCC
* `CANCEL` button only disables ACC/SCC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC
* `GAS pedal` press will not disengage openpilot ALC or ACC/SCC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match manufacturer's stock behavior

### NEW❗ Dynamic Lane Profile (DLP)
Dynamic Lane Profile (DLP) aims to provide the best driving experience with staying within the lane confidently. Dynamic Lane Profile allows openpilot to dynamically switch between lane profiles base on lane recognition confidence level on road.

There are 3 modes to select on the onroad camera screen:
* **Auto Lane**: openpilot dynamically chooses between `Laneline` or `Laneless` model
* **Laneline**: openpilot uses Laneline model only.
* **Laneless**: openpilot uses Laneless model only.

To use Dynamic Lane Profile, do the following:
```
1. openpilot Settings -> Toggles -> Disable use of lanelines -> ON toggle
2. Reboot.
3. Before driving, on the onroad camera screen, toggle between the 3 modes by pressing on the button.
4. Drive. 
```