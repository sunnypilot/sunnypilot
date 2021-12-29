🚗 Features
---

### All Features
* [**Modified Assistive Driving Safety (MADS)**](#modified-assistive-driving-safety-mads) - openpilot Automatic Lane Centering (ALC) and Adaptive Cruise Control (ACC) / Smart Cruise Control (SCC) can be engaged independently of each other
* [**Dynamic Lane Profile (DLP)**](#dynamic-lane-profile-dlp) - dynamically switch lane profile base on lane recognition confidence
* Quiet Drive 🤫 - Toggle to mute all notification sounds (excluding driver safety warnings)
* Force Car Recognition (FCR) - Use a selector to force your car to be recognized by openpilot
* [**OpenStreetMap (OSM) Speed Limit Control**](#openstreetmap-osm-speed-limit-control) - Utilizes data from OpenStreetMap to achieve dynamic speed limit control without user's intervention. Only available to openpilot longitudinal capable cars

🚗 Highlight Features
---

### Modified Assistive Driving Safety (MADS)
The goal of Modified Assistive Driving Safety (MADS) is to enhance the user driving experience with modified behaviors of openpilot engagements. This feature complies with comma.ai's safety rules as accurately as possible with the following changes:
* openpilot ALC and ACC/SCC can be engaged independently of each other
* Dedicated button to toggle openpilot ALC:
  * `LFA` button: Newer HKG cars
  * `CRUISE (MAIN)` button: Most HKG cars, Subaru (Global and Pre Global)
  * `LKAS` button: Honda, Toyota
* `SET-` button enables ACC/SCC
* `CANCEL` button only disables ACC/SCC
* `CRUISE (MAIN)` button disables openpilot completely when `OFF` (strictly enforced in panda safety code)
* `BRAKE pedal` press will pause openpilot ALC; `BRAKE pedal` release will resume openpilot ALC; `BRAKE pedal` release will NOT resume ACC/SCC without an explicit entry
* `GAS pedal` press will not disengage openpilot ALC or ACC/SCC
* `TURN SIGNALS` (`Left` or `Right`) will pause openpilot ALC if the vehicle speed is below the threshold for openpilot Automatic Lane Change
* Event audible alerts are more relaxed to match manufacturer's stock behavior

### Dynamic Lane Profile (DLP)
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

### OpenStreetMap (OSM) Speed Limit Control
OpenStreetMap (OSM) allows openpilot-longitudinal-capable cars to dynamically adjust the longitudinal plan based on the fetched map data. Big thanks to the Move Fast team for the amazing implementation!

Certain features are only available with an active data connection, via:
* [comma Prime](https://comma.ai/prime) - Intuitive service provided directly by comma, or;
* Personal Hotspot - From your mobile device, or a dedicated hotspot from a cellular carrier.

Features:
* [Vision-based Turn Control]: Use vision path predictions to estimate the appropriate speed to drive through turns ahead - i.e., slowing down for curves
* [Map-Data-based Turn Control]: Use curvature information from map data to define speed limits to take turns ahead - i.e., slowing down for curves
  * **Note: Require data connection**
* [Speed Limit Control]: Use speed limit signs information from map data and car interface to automatically adapt cruise speed to road limits
  * **Note: Require data connection**
    * [Speed Limit Offset]: When Speed Limit Control is enabled, set speed limit slightly higher than the actual speed limit for a more natural drive
      * **Note: Require data connection**
* [Hands on Wheel Monitoring]" Monitor and alert when driver is not keeping the hands on the steering wheel

Instruction (WIP)