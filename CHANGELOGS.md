sunnypilot - 0.9.4.2 (2023-08-xx)
========================
* NEW❗: Wide camera view when the steering angle is more than 45°

sunnypilot - 0.9.4.1 (2023-08-11)
========================
* UPDATED: Synced with commaai's 0.9.4 release
* NEW❗: Moonrise driving model
* NEW❗: Ford upstream models support
* UPDATED: Dynamic Lane Profile selector in the "SP - Controls" menu
* REMOVED: Dynamic Lane Profile driving screen UI button
* FIXED: Disallow torque lateral control for angle control platforms (e.g. Ford, Nissan, Tesla)
  * Torque lateral control cannot be used by angle control platforms, and would cause a "Controls Unresponsive" error if Torque lateral control is enforced in settings
* REMOVED: Speed Limit Style override
* Honda Accord 2016-17 support thanks to mlocoteta!
  * Serial Steering hardware required. For more information, see https://github.com/mlocoteta/serialSteeringHardware
* mapd: utilize advisory speed limit in curves (#142) thanks to pfeiferj!

sunnypilot - 0.9.3.1 (2023-07-09)
========================
* UPDATED: Synced with commaai's 0.9.3 release
* NEW❗: Display Temperature on Sidebar toggle
  * Display Ambient temperature, memory temperature, CPU core with the highest temperature, GPU temperature, or max of Memory/CPU/GPU on the sidebar
  * Replace "Display CPU Temperature on Sidebar" toggle
* NEW❗: Hot Coffee driving model
* NEW❗: HKG CAN: Smoother Stopping Performance (Beta) toggle
  * Smoother stopping behind a stopped car or desired stopping event.
  * This is only applicable to HKG CAN platforms using openpilot longitudinal control
* NEW❗: Toyota: TSS2 longitudinal: Custom Tuning
  * Smoother longitudinal performance for Toyota/Lexus TSS2/LSS2 cars thanks to dragonpilot-community!
* NEW❗: Enable Screen Recorder toggle
  * Enable this will display a button on the onroad screen to toggle on or off real-time screen recording with UI elements.
* IMPROVED: Dynamic Lane Profile: when using Laneline planner via Laneline Mode or Auto Mode, enforce Laneless planner while traveling below 10 MPH or 16 km/h
* REMOVED: Display CPU Temperature on Sidebar

sunnypilot - 0.9.2.3 (2023-06-18)
========================
* NEW❗: Auto Lane Change: Delay with Blind Spot
  * Toggle to enable a delay timer for seamless lane changes when blind spot monitoring (BSM) detects an obstructing vehicle, ensuring safe maneuvering
* NEW❗: Driving Screen Off: Wake with Non-Critical Events
  * When Driving Screen Off Timer is not set to "Always On":
    * Enabled: Wake the brightness of the screen to display all events
    * Disabled: Wake the brightness of the screen to display critical events
  * Currently, all non-nudge modes are default to continue lane change after 1 seconds of blind spot detection
* NEW❗: Fleet Manager PIN Requirement toggle
  * User can now enable or disable PIN requirement on the comma device before accessing Fleet Manager
* NEW❗: Reset all sunnypilot settings toggle
* NEW❗: Turn signals display on screen when blinker is used
  * Green: Blinker is on
  * Red: Blinker is on, car detected in the adjacent blind spot or road edge detected
* IMPROVED: mapd: better exceptions handling when loading dependencies
* UPDATED: Green Traffic Light Chime no longer displays an orange border when executed
* FIXED: mapd: Road name flashing caused by desync with last GPS timestamp
* FIXED: Ram HD (2500/3500): Ignore paramsd sanity check
  * Live parameters have trouble with self-tuning on this platform with upstream openpilot 0.9.2
* Hyundai: Longitudinal support for CAN-based Camera SCC cars thanks to Zack1010OP's Patreon sponsor!

sunnypilot - 0.9.2.2 (2023-06-13)
========================
* NEW❗: Toyota: Allow M.A.D.S. toggling with LKAS Button (Beta)
* IMPROVED: Ram: cruise button handling

sunnypilot - 0.9.2.1 (2023-06-10)
========================
* UPDATED: Synced with commaai's 0.9.2 release
* UPDATED: feature revamp with better stability
* UPDATED:
  * M.A.D.S.
    * Path color becomes LIGHT ORANGE during Driver Steering Override
  * Gap Adjust Cruise (now known as Driving Personality in upstream openpilot 0.9.3):
    * Updated profiles and jerk changes
    * Experimental Mode support
    * Three settings: Stock, Aggressive, and Maniac
    * Stock is recommended and the default
    * In Aggressive/Maniac mode, lead follow distance is shorter and quicker gas/brake response
  * Dynamic Lane Profile
    * Display blue borders on both sides of the driving path when Laneline mode is being used in the planner
    * Auto Mode optimization
      * Permanent: Laneless during Auto Lane Change execution
  * Mapd
    * OpenStreetMap Database: new regions added
  * Developer UI (Dev UI)
    * REMOVED: 2-column design
    * NEW❗: 1-column + 1-row design
  * Custom Stock Longitudinal Control
    * NEW❗: Chrysler/Jeep/Ram support
    * NEW❗: Mazda support
    * NEW❗: Volkswagen PQ support
    * DISABLED: Hyundai/Kia/Genesis CAN-FD platforms
* NEW❗: Switch between Chill (openpilot ACC) and Experimental (E2E longitudinal) with DISTANCE button on the steering wheel
  * To switch between Chill and Experimental Mode: press and hold the DISTANCE button on the steering wheel for over 0.5 second
  * All openpilot longitudinal capable cars support
* NEW❗: Nicki Minaj driving model
* NEW❗: Nissan and Mazda upstream models support
* NEW❗: Pre-Global Subaru upstream models support
* NEW❗: Display End-to-end Longitudinal Status (Beta)
  * Display an icon that appears when the End-to-end model decides to start or stop
* NEW❗: Green Traffic Light Chime (Beta)
  * A chime will play when the traffic light you are waiting for turns green, and you have no vehicle in front of you.
* NEW❗: Lead Vehicle Departure Alert
  * Notify when the leading vehicle drives away
* NEW❗: Speedometer: Display True Speed
  * Display the true vehicle current speed from wheel speed sensors.
* NEW❗: Speedometer: Hide from Onroad Screen
* NEW❗: Auto-Hide UI Buttons
  * Hide UI buttons on driving screen after a 30-second timeout. Tap on the screen at anytime to reveal the UI buttons
  * Applicable to Dynamic Lane Profile (DLP) and Gap Adjust Cruise (GAC)
* NEW❗: Display DM Camera in Reverse Gear
  * Show Driver Monitoring camera while the car is in reverse gear
* NEW❗: Block Lane Change: Road Edge Detection (Beta)
  * Block lane change when road edge is detected on the stalk actuated side
* NEW❗: Display CPU Temperature on Sidebar
  * Display the CPU core with the highest temperature on the sidebar
* NEW❗: Display current driving model in Software settings
* NEW❗: HKG: smartMDPS automatic detection (installed with applicable firmware)
* FIXED: Unintended siren/alarm from the comma device if the vehicle is turned off too quickly in PARK gear
* FIXED: mapd: Exception handling for loading dependencies
* Fleet Manager via Browser support thanks to actuallylemoncurd, AlexandreSato, ntegan1, and royjr!
  * Access your dashcam footage, screen recordings, and error logs when the car is turned off
  * Connect to the device via Wi-Fi, mobile hotspot, or tethering on the comma device, then navigate to http://ipAddress:5050 to access.
* Honda Clarity 2018-22 support thanks to mcallbosco, vanillagorillaa and wirelessnet2!
* Ram: Steer to 0/7 MPH support thanks to vincentw56!
* Retain hotspot/tethering state across reboots thanks to rogerioaguas!

sunnypilot - Version Latest (2023-02-22)
========================
* UPDATED: Synced with commaai's master branch - 2023.02.19-04:52:00:GMT - 0.9.2
* Refactor sunnypilot features to be more stable

sunnypilot - Version Latest (2022-12-16)
========================
* UPDATED: Synced with commaai's master branch - 2022.12.16-06:31:00:GMT - 0.9.1
* NEW❗: GM:
    * NEW❗: Gap Adjust Cruise support - Chill, Normal, Aggressive
    * NEW❗: Experimental Mode: Hold DISTANCE button on the steering wheel for 0.5 second to switch between Experimental Mode and Chill Mode
* REMOVED❌: Toytoa: SnG Hack
    * This method is not recommended and may cause some cars to not behave as expected
    * SDSU is strongly recommended to enable SnG for Toyota vehicles without SnG from factory
* commaai: radard: add missing accel data for vision-only leads (commaai/openpilot#26619) - pending PR
    * VOACC performance is drastically improved when using Chill Mode
* IMPROVED: M.A.D.S. events handling
* IMPROVED: UI: screen recorder button change
* IMPROVED: OpenStreetMap Offline Database optimization
* FIXED: Toyota: vehicles' LKAS button no longer has a delay with toggling M.A.D.S.
* FIXED: Toyota: brake pedal press at standstill causing Cruise Fault
* FIXED: Volkswagen MQB: reduce Camera Malfunction occurrences (requires testing)
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-12-10)
========================
* IMPROVED: NEW❗ Developer UI design
    * Second column metrics is now moved to the bottom of the screen
        * ACC. = Acceleration
        * L.S. = Lead Speed
        * E.T. = EPS Torque
        * B.D. = Bearing Degree
        * FRI. = Friction
        * L.A. = Lateral Acceleration
        * ALT. = Altitude
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-12-07)
========================
* NEW❗: Screen Recorder support thanks to neokii and Kumar!
* NEW❗: End-to-end longitudinal start/stop status icon
    * Only appears when Experimental Mode is enabled
* NEW❗: End-to-end longitudinal car chime when starting
    * Hyundai/Kia/Genesis CAN platform, Honda/Acura Bosch/Nidec, Toyota/Lexus
    * i.e. Traffic light turns green, stop sign ready to go, etc.
    * Only appears when Experimental Mode is enabled AND longitudinal control is disengaged
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-12-05)
========================
* UPDATED: Synced with commaai's master branch - 2022.12.04-22:46:00:GMT - 0.9.1
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-11-12)
========================
* UPDATED: Synced with commaai's master branch - 2022.11.12-10:02:00:GMT - 0.8.17
* FIXED: CAN Error for CAN HKG cars that do not have navigation from the factory
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-11-11)
========================
* UPDATED: Synced with commaai's master branch - 2022.11.11-21:22:00:GMT - 0.8.17
* commaai: AGNOS 6.2 (commaai/openpilot#26441)
* NEW❗: Speed Limit Control - HKG - add speed limit from car's navigation head unit
    * Compatible with certain models, trims, and model years
* DISABLED: FCA: RAM HD - steer down to 0
* FIXED: UI: End-to-end longitudinal button on driving screen synchronization
* FIXED: Honda: Longitudinal status with set cruise speed now displays properly in the car's dashboard
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-11-08)
========================
* ADDED: New Zealand offline OpenStreetMap database

sunnypilot - Version Latest (2022-11-04)
========================
* UPDATED: Synced with commaai's master branch - 2022.11.05-01:44:00:GMT - 0.8.17
* RE-ENABLED: Dynamic Lane Profile - preserves lanelines
    * Can be found in "SP - Controls" menu
* NEW❗: DLP: switch to laneless for current/future curves thanks to @twilsonco!
    * Can be found in "SP - Controls" menu
* NEW❗: UI: Road Camera Selector
    * Enable this will display a button on the driving screen to select the driving camera
    * Can be found in "SP - Visuals" menu
* NEW❗: Controls: Camera & Path Custom Offsets
    * Only applicable to laneline mode when using Dynamic Lane Profile
* NEW❗: Buttons on driving screen are now sorted based on priority and availability
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-28)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.28-03:53:00:GMT - 0.8.17
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-26)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.26-06:20:00:GMT - 0.8.17
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-25)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.25-23:53:00:GMT - 0.8.17
* Pre-Global Subaru support thanks to @martinl!
* NEW❗: Speed Limit values turn red when current speed is higher than posted speed limit
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-23)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.22-23:15:00:GMT - 0.8.17
* IMPROVED: Custom Stock Longitudinal Control - HKG - only allow engagement on user button press
* IMPROVED: Custom Stock Longitudinal Control - Volkswagen MQB & PQ - more consistent set speed change
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-21)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.21-17:33:00:GMT - 0.8.17
* IMPROVED: Custom Stock Longitudinal Control - Volkswagen MQB & PQ - more predictable button send logic
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-20)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.20-20:25:00:GMT - 0.8.17
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-19)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.19-08:31:00:GMT - 0.8.17
* IMPROVED: Controls: Speed Limit Control - accelerator press only disengage if "Disengage on Accelerator Pedal" is enabled
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-18)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.18-04:44:00:GMT - 0.8.17
* RE-ENABLED: Volkswagen MQB & PQ with Custom Stock Longitudinal Control
* NEW❗: Steering Rate Cost Live Tune
    * Enables live tune for Steering Rate Cost. Lower value allows steering wheel to move more freely at low speed
    * Can be found in "SP - Controls" menu
* FIXED: MADS: GM - include Regen Paddle logic thanks to @twilsonco!
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-17)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.17-23:54:00:GMT+1 - 0.8.17
* ENABLED: "Custom Stock Longitudinal Control" toggle for CAN-FD cars
* FIXED: HKG CAN-FD: Could not engage when openpilot longitudinal is enabled
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-13)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.13-19:43:00:GMT+1 - 0.8.17
* ADDED: Live Tmux toggle
    * Can be found in "SP - General" menu
* IMPROVED: OpenStreetMap Database Update - only check for database update with explicit user decision
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-11)
========================
* ADDED: Hyundai openpilot longitudinal improvements - huge thanks to @aragon7777!
* ADDED: Check for OpenStreetMap Database Update button
* UPDATED: commaai: Low speed lateral control improvements (commaai:openpilot#26022, bbcd448) - pending PR
* FIXED: MUTCD speed limit spacing adjusts dynamically when no subtext is shown (i.e., speed limit offset, distance to next speed limit)
* FIXED: MADS: Intermittent CAN Error when engaging for Toyota Prius TSS-P
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-09)
========================
* ADDED: commaai: Low speed lateral control improvements (commaai:openpilot#26022, bca288bb) - pending PR
* FIXED: MADS: Intermittent CAN Error when engaging for Toyota Prius TSS-P
* IMPROVED: mapd: stop signs and other supported traffic_calming tags are now slowing/stopping as expected
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-08)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.08-12:07:00:GMT+1 - 0.8.17
* FIXED: MADS: Intermittent CAN Error when engaging for Toyota Prius TSS-P
* IMPROVED: mapd: Speed Humps are now set at 20 MPH or 32 km/h
* IMPROVED: OpenStreetMap Offline Database download experience
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-10-07)
========================
* UPDATED: Synced with commaai's master branch - 2022.10.07-08:16:00:GMT - 0.8.17
* NEW❗: OpenStreetMap database can now be downloaded locally for offline use
    * Now offering US South, US West, US Northeast, US Florida, Taiwan, and South Africa
    * Databases updated - 2022.10.05-03:30:00:GMT
* NEW❗: mapd: Stop Sign, Yield, Speed Bump, Speed Hump, Sharp Curve support - huge thanks to @move-fast and @dragonpilot-community!
    * Go to https://openstreetmap.org and start mapping out your area!
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-09-30)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.30-22:43:00:GMT - 0.8.17
* RE-ADDED: Torque Lateral Controller Live Tune Menu
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-09-23)
========================
* ADDED: Developer UI: latAccelFactorFiltered & frictionCoefficientFiltered values displays in green if Torque is using live params
* Bug fixes and performance improvements

sunnypilot - Version Latest (2022-09-22)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.19-22:19:00:GMT - 0.8.17
* NEW❗: Toggle to explicitly enable Custom Stock Longitudinal Control
    * Applicable cars only: Honda, Hyundai/Kia/Genesis
    * Settings -> Toggles menu

sunnypilot - Version Latest (2022-09-21)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.19-22:19:00:GMT - 0.8.17
* ADDED: Toggle to enable Live Torque (self/auto tune) with Torque lateral controller
    * To enable, first enable "Enforce Torque Lateral Controller" toggle
* UPDATED: New metrics in Developer UI (when Live Torque is enabled)
    * REMOVED: latAccelFactorRaw & frictionCoefficientRaw from torqued
    * ADDED: latAccelFactorFiltered & frictionCoefficientFiltered from torqued
* REMOVED: Temporary remove Torque Lateral Controller Live Tune Menu

sunnypilot - Version Latest (2022-09-20)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.19-22:19:00:GMT - 0.8.17
* ADDED: Toggle to enable Live Torque (self/auto tune) with Torque lateral controller
    * To enable, first enable "Enforce Torque Lateral Controller" toggle
* REMOVED: Temporary remove Torque Lateral Controller Live Tune Menu

sunnypilot - Version Latest (2022-09-18)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.17-11:23:00:GMT - 0.8.17
* ADDED: Kia Forte Non-SCC 2019 support for @askalice
* FIXED: Torque Lateral Control Live Tune now syncs with commaai:openpilot#25822
* FIXED: mapd dependencies no longer need to be re-downloaded after unknown reboots

sunnypilot - Version Latest (2022-09-17)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.17-11:23:00:GMT - 0.8.17
* NEW❗: Non SCC HKG support
    * Custom Stock Longitudinal Control
    * ❗No❗ openpilot longitudinal control
* FIXED: Honda Bosch random low-value set speed changes

sunnypilot - Version Latest (2022-09-16)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.16-20:23:00:GMT - 0.8.17

sunnypilot - Version Latest (2022-09-15)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.16-02:00:00:GMT - 0.8.17
* FIXED: Block additional auto lane change actions if blinker stays on after the first lane change
* REVERTED: Some Toyota with LKAS button no longer requires double press to engage/disengage M.A.D.S.

sunnypilot - Version Latest (2022-09-14)u
========================
* UPDATED: Synced with commaai's master branch - 2022.09.11-02:47:00:GMT - 0.8.17
* NEW❗: GM models supported in Force Car Recognition (FCR)
    * Under "SP - Vehicles"
* NEW❗: Prompt to select car in "SP - Vehicles" if car unrecognized on startup
* FIXED: Some Toyota with LKAS button no longer requires double press to engage/disengage M.A.D.S.
* UPDATED: ESCC: Use radar tracks from radar if available

sunnypilot - Version Latest (2022-09-13)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.11-02:47:00:GMT - 0.8.17
* NEW❗: New metric in Developer UI
    * Actual Lateral Acceleration (Roll Compensated)

sunnypilot - Version Latest (2022-09-12)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.11-02:47:00:GMT - 0.8.17
* FIXED: Honda Nidec models not gaining speed when longitudinal engaged

sunnypilot - Version Latest (2022-09-11)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.11-02:47:00:GMT - 0.8.17
* NEW❗: Hyundai Enhanced SCC now forwards FCW and AEB signals and commands from radar to car
* RE-ENABLED: MADS Status Icon toggle

sunnypilot - Version Latest (2022-09-10)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.11-02:47:00:GMT - 0.8.17
* NEW❗: RAM improvement implementation thanks to realfast!
* DISABLED: Chrysler/Jeep/Ram with Custom Stock Longitudinal Control
* DISABLED: Volkswagen MQB & PQ with Custom Stock Longitudinal Control

sunnypilot - Version Latest (2022-09-09)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.09-07:35:00:GMT - 0.8.17
* NEW❗: MADS now supporting General Motors (GM)
* ADDED: Custom Stock Longitudinal Control - Volkswagen
    * MQB & PQ
* ADDED: Reverse ACC Change
    * ACC +/-: Short=5, Long=1
* ADDED: Custom Stock Longitudinal Control
    * Hyundai/Kia/Genesis
    * Honda Bosch
* ADDED: Hyundai: 2015-16 Genesis resume from standstill fix (commaai:openpilot#25579) - pending PR
* Vision Turn Speed Control re-enabled
* Disable Onroad Uploads toggle re-enabled

sunnypilot - Version Latest (2022-09-08)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.08-04:05:00:GMT - 0.8.17
* NEW❗: Block lane change initiation while brake is pressed

sunnypilot - Version Latest (2022-09-07)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.08-04:05:00:GMT - 0.8.17
* NEW❗: Display End-to-end longitudinal 🌮 on screen
    * NEW❗: Hold DISTANCE button on the steering wheel for 1 second to switch between E2E Long and ACC mode
    * Enable toggle on the driving screen to switch between modes with End-to-end longitudinal
    * Only applicable to cars with openpilot longitudinal control
* NEW❗: Block lane change initiation while brake is pressed
* REMOVED: Dynamic Lane Profile - upstream laneless model is now on by default
* REMOVED: hyundai: consistent start from stop (commaai:openpilot#25672) - pending PR

sunnypilot - Version Latest (2022-09-06)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.06 - 0.8.17
* NEW❗: Display useful metrics above the chevron that tracks the lead car
    * Under "SP - Visuals" menu
    * Only applicable to cars with openpilot longitudinal control
* ADDED: hyundai: consistent start from stop (commaai:openpilot#25672) - pending PR
* FIXED: Vienna speed limit interface now scales properly with the outer box
* REMOVED: Hyundai long improvements (commaai:openpilot#25604) - closed PR

sunnypilot - Version Latest (2022-09-05)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.03 - 0.8.17
* NEW❗: Speed Limit Control (SLC) interface integrated with upstream
* NEW❗: Speed limit from active navigation is now prioritized for Speed Limit Control
* NEW❗: MUTCD (U.S.) or Vienna (E.U.) speed limit interfaces can now be selected under "SP - Controls"

sunnypilot - Version Latest (2022-09-04)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.03 - 0.8.17
* FIXED: Gap Adjust Cruise status now displays properly on screen
* FIXED: mapd - missing index in list caused mapd to crash
* REMOVED: Temporary removed Vision Turn Speed Control

sunnypilot - Version Latest (2022-09-03)
========================
* UPDATED: Synced with commaai's master branch - 2022.09.03 - 0.8.17
* ADDED: New border colors for different operation engagements
* ADDED: UI: Show barrier when car detected in blind spot
    * Only applicable to cars that have BSM detection with openpilot
* FIXED: Cruise Cancel button no longer display prompt if cruise not engaged
* TWEAKED: Update changelogs on startup in Settings -> Software -> Version
* REMOVED: Upload Raw Logs and Full Resolution Videos toggles

sunnypilot - Version Latest (2022-08-31)
========================
* UPDATED: Synced with commaai's master branch - 2022.08.31 - 0.8.17
* ADDED: New border colors for different operation engagements
* ADDED: UI: Show barrier when car detected in blind spot
    * Only applicable to cars that have BSM detection with openpilot
* FIXED: Cruise Cancel button no longer display prompt if cruise not engaged
* REMOVED: Upload Raw Logs and Full Resolution Videos toggles

sunnypilot - Version 0.8.16 (2022-07-16)
========================
* Sync with commaai's master branches
* NEW❗: Add toggle to pause lateral actuation below 30 MPH / 50 KM/H
* IMPROVED: Better controls mismatch handling
* IMPROVED: Less frequent Low Memory alert
* IMPROVED: Only allow lateral control when in forward gears
* IMPROVED: Better alerts handling on gear changes

sunnypilot - Version 0.8.14-1.3 (2022-06-29)
========================
* Hyundai/Kia/Genesis
    * NEW❗: MADS: Add GAP/Distance button on the steering wheel to engage/disengage
        * To engage/disengage MADS: Hold the button for 0.5 second
* NEW❗: Dynamic Lane Profile: Add toggle to enable "Laneless for Curves in Auto Lane"
* HOTFIX🛠: Improve Torque lateral control and reduce ping pong for some Toyota cars
    * Torque control: higher low speed gains and better steering angle deadzone logic
* Developer UI: Remove Distance Traveled, replace with Memory Usage %
    * This may have a potential to fix the Low Memory alert that may appear

sunnypilot - Version 0.8.14-1 (2022-06-27)
========================
* HOTFIX🛠: Honda, Toyota, Volkswagen now initialized correctly with Torque Lateral Live Tune

sunnypilot - Version 0.8.14-1 (2022-06-27)
========================
* NEW❗: Added toggle to enable updates for sunnypilot
* HOTFIX🛠: Volkswagen car list now displays properly in Force Car Recognition menu
* REVERTED: Honda - temporary removes CRUISE (MAIN) for MADS engagement
    * LKAS button continues to be used for MADS engagement/disengagement

sunnypilot - Version 0.8.14-1 (2022-06-26)
========================
Visit https://bit.ly/sunnyreadme for more details
* sunnypilot 0.8.14 release - based on openpilot 0.8.14 devel
* "0.8.14-prod-c3" branch only supports comma three
    * If you have a comma two, EON, or other devices than a comma three, visit sunnyhaibin's discord server for more details: https://discord.gg/wRW3meAgtx
* Mono-branch support
    * Honda/Acura
    * Hyundai/Kia/Genesis
    * Toyota/Lexus
    * Volkswagen MQB
* Modified Assistive Driving Safety (MADS) Mode
    * NEW❗: CRUISE (MAIN) now engages MADS for all supported car makes
    * NEW❗: Added toggle to disable disengaging Automatic Lane Centering (ALC) on the brake pedal
* Dynamic Lane Profile (DLP)
* NEW❗: Gap Adjust Cruise (GAC)
    * openpilot longitudinal cars can now adjust between the lead car's following distance gap via 3 modes:
        * Steering Wheel (SW) | User Interface (UI) | Steering Wheel + User Interface (SW+UI)
* NEW❗: Custom Camera & Path Offsets
* NEW❗: Torque Lateral Control from openpilot 0.8.15 master (as of 2022-06-15)
* NEW❗: Torque Lateral Control Live Tune Menu
* NEW❗: Speed Limit Sign from openpilot 0.8.15 master (as of 2022-06-22)
* NEW❗: Mapbox Speed Limit data will now be utilized in Speed Limit Control (SLC)
    * Speed limit data will be utilized in the following availability:
        * Mapbox (active navigation) -> OpenStreetMap -> Car Interface (Toyota's TSR)
* Custom Stock Longitudinal Control
    * NEW❗: Volkswagen MQB
    * Honda
    * Hyundai/Kia/Genesis
* NEW❗: Mapbox navigation support for non-Prime users
    * Visit sunnyhaibin's discord server for more details: https://discord.gg/wRW3meAgtx
* Hyundai/Kia/Genesis
    * NEW❗: Enhanced SCC (ESCC) Support
        * Requires hardware modification. Visit sunnyhaibin's discord server for more details: https://discord.gg/wRW3meAgtx
    * NEW❗: Smart MDPS (SMDPS) Support - Auto-detection
        * Requires hardware modification and custom firmware for the SMDPS. Visit sunnyhaibin's discord server for more details: https://discord.gg/wRW3meAgtx
* Toyota/Lexus
    * NEW❗: Added toggle to enforce stock longitudinal control

sunnypilot - Version 0.8.12-4
========================
* NEW❗: Custom Stock Longitudinal Control by setting the target speed via openpilot's "MAX" speed thanks to multikyd!
    * Speed Limit Control
    * Vision-based Turn Control
    * Map-based Turn Control
* NEW❗: HDA status integration with Custom Stock Longitudinal Control on applicable HKG cars only
* NEW❗: Roll Compensation and SteerRatio fix from comma's 0.8.13
* NEW❗: Dev UI to display different metrics on screen
    * Click on the "MAX" box on the top left of the openpilot display to toggle different metrics display
    * Lead car relative distance; Lead car relative speed; Actual steering degree; Desired steering degree; Engine RPM; Longitudinal acceleration; Lead car actual speed; EPS torque; Current altitude; Compass direction
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

sunnypilot - Version 0.8.12-3
========================
* NEW❗: Bypass "System Malfunction" alert toggle
    * Prevent openpilot from returning the "System Malfunction" alert that hinders the ability use openpilot
* FIXED: Hyundai/Kia/Genesis Brake Hold Active now outputs the correct events on screen with M.A.D.S. engaged

sunnypilot - Version 0.8.12-2
========================
* NEW❗: Disable M.A.D.S. toggle to disable the beloved M.A.D.S. feature
    * Enable Stock openpilot engagement/disengagement
* ADJUST: Initialize Driving Screen Off Brightness at 50%

sunnypilot - Version 0.8.12-1
========================
* sunnypilot 0.8.12 release - based on openpilot 0.8.12 devel
* Dedicated Hyundai/Kia/Genesis branch support
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
