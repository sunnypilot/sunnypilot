sunnypilot - Version 0.8.12-4 (2022-04-09)
========================
* NEW❗: Roll Compensation and SteerRatio fix from comma's 0.8.13
* NEW❗: Dev UI to display different metrics on screen
  * Click on the "MAX" box on the top left of the openpilot display to toggle different metrics display
  * Lead car relative distance; Lead car relative speed; Actual steering degree; Desired steering degree; Driven Distance; Longitudinal acceleration; Lead car actual speed; EPS torque; Current altitude; Compass direction
* NEW❗: Stand Still Timer to display time spent at a stop with M.A.D.S engaged (i.e., stop lights, stop signs, traffic congestions)
* NEW❗: Current car speed text turns red when the car is braking
* NEW❗: Export GPS tracks into GPX files and upload to OSM thanks to eFini!
* NEW❗: Enable ACC and M.A.D.S with a single press of the RES+/SET- button
* NEW❗: Dedicated icon to show the status of M.A.D.S.
* NEW❗: No Offroad Fix for non-official devices that cannot shut down after the car is turned off
* NEW❗: AGNOS 4
* IMPROVED: Add B Gear to extraGear filter to prevent from disengaging openpilot
* IMPROVED: Update Toyota car list in Force Car Recognition (#18) thanks to FrogAi!
* IMPROVED: Enforce the white LKAS icon to be OFF when the car starts with openpilot
  * This is to ensure that the LKAS icon does not confuse M.A.D.S. engagement/disengagement
* IMPROVED: Green LKAS icon when M.A.D.S. is engaged
* FIXED: M.A.D.S. behavior with LKAS button press now fixed for all Toyota car models
* FIXED: Controls Mismatch error when pressing the LKAS button to engage M.A.D.S.
* FIXED: Add sentry logging
* FIXED: Disable errors due to non-comma-three hardware limitation
* HOTFIX🛠: Logging: Bugs and Fixes

sunnypilot - Version 0.8.12-3
========================
* NEW❗: Bypass "System Malfunction" alert toggle
  * Prevent openpilot from returning the "System Malfunction" alert that hinders the ability use openpilot

sunnypilot - Version 0.8.12-2
========================
* HOTFIX: Fix double stalk engage lateral and longitudinal control
* NEW❗: Disable M.A.D.S. toggle to disable the beloved M.A.D.S. feature
  * Enable Stock openpilot engagement/disengagement
* ADJUST: Initialize Driving Screen Off Brightness at 50%

sunnypilot - Version 0.8.12-1
========================
* sunnypilot 0.8.12 release - based on openpilot 0.8.12 devel
* Dedicated Toyota branch support
* NEW❗: OpenStreetMap integration thanks to the Move Fast team!
  * NEW❗: Vision-based Turn Control
  * NEW❗: Map-Data-based Turn Control
  * NEW❗: Speed Limit Control w/ optional Speed Limit Offset
  * NEW❗: OpenStreetMap integration debug UI
  * Only available to openpilot longitudinal enabled cars
* NEW❗: Hands on Wheel Monitoring according to EU r079r4e regulation
* NEW❗: Disable Onroad Uploads for data-limited Wi-Fi hotspots when using OpenStreetMap related features
* NEW❗: Fast Boot (Prebuilt)
* NEW❗: Auto Lane Change Timer
* NEW❗: Screen Brightness Control (Global)
* NEW❗: Driving Screen Off Timer
* NEW❗: Driving Screen Off Brightness (%)
* NEW❗: Max Time Offroad
* Improved user feedback with M.A.D.S. operations thanks to Spektor56!
  * Lane Path
    * Green🟢 (Laneful), Red🔴 (Laneless): M.A.D.S. engaged
    * White⚪: M.A.D.S. suspended or disengaged
    * Black⚫: M.A.D.S. engaged, steering is being manually override by user
  * Screen border now only illuminates Green when SCC/ACC is engaged

sunnypilot - Version 0.8.10-1 (Unreleased)
========================
* sunnypilot 0.8.10 release - based on openpilot 0.8.10 `devel`
* Add Toyota cars to Force Car Recognition

sunnypilot - Version 0.8.9-4
========================
* Hyundai: Fix Ioniq Hybrid signals

sunnypilot - Version 0.8.9-3
========================
* Update home screen brand and version structure

sunnypilot - Version 0.8.9-2
========================
* Added additional Sonata Hybrid Firmware Versions
* Features
    * Modified Assistive Driving Safety (MADS) Mode
    * Dynamic Lane Profile (DLP)
    * Quiet Drive 🤫
    * Force Car Recognition (FCR)
    * PID Controller: add kd into the stock PID controller

sunnypilot - Version 0.8.9-1
========================
* First changelog!
* Features
    * Modified Assistive Driving Safety (MADS) Mode
    * Dynamic Lane Profile (DLP)
    * Quiet Drive 🤫
    * Force Car Recognition (FCR)
    * PID Controller: add kd into the stock PID controller