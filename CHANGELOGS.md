sunnypilot - Version 0.8.12-1
========================
* sunnypilot 0.8.12 release - based on openpilot 0.8.12 devel
* Dedicated Volkswagen MQB branch support
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
* NEW❗: Disable M.A.D.S. toggle to disable the beloved M.A.D.S. feature
  * Enable Stock openpilot engagement/disengagement
* ADJUST: Initialize Driving Screen Off Brightness at 50%
* NEW❗: Bypass "System Malfunction" alert toggle
  * Prevent openpilot from returning the "System Malfunction" alert that hinders the ability use openpilot
* NEW❗: Custom Stock Longitudinal Control by setting the target speed via openpilot's "MAX" speed thanks to multikyd!
  * Speed Limit Control
  * Vision-based Turn Control
  * Map-based Turn Control
* NEW❗: Roll Compensation and SteerRatio fix from comma's 0.8.13
* NEW❗: Dev UI to display different metrics on screen
  * Click on the "MAX" box on the top left of the openpilot display to toggle different metrics display
  * Lead car relative distance; Lead car relative speed; Actual steering degree; Desired steering degree; Distance Driven; Longitudinal acceleration; Lead car actual speed; EPS torque; Current altitude; Compass direction
* NEW❗: Stand Still Timer to display time spent at a stop with M.A.D.S engaged (i.e., stop lights, stop signs, traffic congestions)
* NEW❗: Current car speed text turns red when the car is braking
* NEW❗: Export GPS tracks into GPX files and upload to OSM thanks to eFini!
* NEW❗: Enable ACC and M.A.D.S with a single press of the RES+/SET- button
* NEW❗: ACC +/-: Short=5, Long=1
  * Change the ACC +/- buttons behavior with cruise speed change in openpilot
  * Disabled (Stock):  Short=1, Long=5
  * Enabled:  Short=5, Long=1
* NEW❗: Speed Limit Value Offset (not %)*
  * Set speed limit higher or lower than actual speed limit for a more personalized drive.
  * *To use this feature, turn off "Enable Speed Limit % Offset"*
* NEW❗: Dedicated icon to show the status of M.A.D.S.
* NEW❗: No Offroad Fix for non-official devices that cannot shut down after the car is turned off
* NEW❗: Stop N' Go Resume Alternative
  * Offer alternative behavior to auto resume when stopped behind a lead car using stock SCC/ACC. This feature removes the repeating prompt chime when stopped and/or allows some cars to use auto resume (i.e., Genesis)
* IMPROVED: Show the lead car icon in the car's dashboard when a lead car is detected by openpilot's camera vision
* FIXED: MADS button unintentionally set MAX when using stock longitudinal control thanks to Spektor56!
* HOTFIX🛠: Add sentry logging
* HOTFIX🛠: Disable errors due to non-comma-three hardware limitation
* HOTFIX🛠: Logging: Bugs and Fixes