# Introduction
This page is a repository of useful how-tos as a supplement for additional information.

Table of Contents
=======================

* [Enable Radar Tracks and openpilot Longitudinal Control](#Enable-Radar-Tracks-and-openpilot-Longitudinal-Control)

---

## Enable Radar Tracks and openpilot Longitudinal Control

*(Last updated date: October 3rd, 2021)*

*(Base on `master` on version 0.8.10 `d546c109ef4854322bfaea12954ad854d593554c`)*

* [Enable Radar Tracks](#-Enable-Radar_Tracks-)
* [Enable openpilot Longitudinal Control](#-Enable-openpilot-Longitudinal-Control-)

Radar tracks can now be enabled manually on applicable cars through SSH thanks to [@greghogan](https://github.com/greghogan) and [@pd0wm](https://github.com/pd0wm).

Some Hyundai radars can be reconfigured to output (debug) radar points on bus 1.
Reconfiguration is done over UDS by reading/writing to 0x0142 using the Read/Write Data By Identifier
endpoints (0x22 & 0x2E). This script checks your radar firmware version against a list of known
firmware versions. If you want to try on a new radar, make sure to note the default config value
in case it is different from the other radars and you need to revert the changes.
After changing the config the car should not show any faults when openpilot is not running.
These config changes are persistent across car reboots. You need to run this script again
to go back to the default values.

USE AT YOUR OWN RISK! Stock system safety features, like AEB and FCW, might be affected by these changes.

### 🚨 Enable Radar Tracks 🚨

***(EXPERIMENTAL, as of October 3rd, 2021)***

1. Ensure the car is at the `OFF` ignition position.
2. Connect your compatible comma device (EON, C2, C3) to the car. comma device power should be ON.
3. Use a laptop or applicable device to connect to your comma device via SSH. (Tips: Instructions to SSH in [HERE](https://github.com/commaai/openpilot/wiki/SSH))
4. In the SSH terminal after successfully connected to your comma device, execute the following commands:
    1. ```killall boardd```
    2. `python /data/openpilot/selfdrive/debug/hyundai_enable_radar_points.py`
    3. Follow the instructions in the script:
        1. `Power on the vehicle keeping the engine off (press start button twice) then type OK to continue`.
        2. If successful, the following message should appear: `[DONE]. Restart your vehicle and ensure there are no faults`.
    4. Reboot your comma device:
        1. C3: `sudo reboot`
        2. C2 or EON: `reboot`
5. Once your comma device has been rebooted, start your car with engine on (with or without comma device connected). Ensure that there are no faults from the car.
6. If there is no fault, you are done! You have successfully enabled radar tracks on your car's radar.

### 🚨 Enable openpilot Longitudinal Control 🚨

***(EXPERIMENTAL, as of October 3rd, 2021)***

1. Connect your compatible comma device (EON, C2, C3) to the car. comma device power should be ON.
    * (Note: If doing this in the car, ensure the car is at the `OFF` ignition position.)
2. Use a laptop or applicable device to connect to your comma device via SSH. (Tips: Instructions to SSH in [HERE](https://github.com/commaai/openpilot/wiki/SSH))
3. In the SSH terminal after successfully connected to your comma device, execute the following commands:
    1. ```echo -n "1" > /data/params/d/DisableRadar_Allow```
    2. Reboot your comma device:
        1. C3: `sudo reboot`
        2. C2 or EON: `reboot`
4. Once your comma device has been rebooted, a new toggle should appear:


    .
    └── Settings
        └── Toggles
            └── ***openpilot Longitudinal Control***
5. Set the toggle `openpilot Longitudinal Control` to `ON`. Reboot the comma device to ensure the take the change in effect.
6. Start the car and drive. If a chevron (triangle) appears behind a lead car, openpilot Longitudinal Control has been successfully enabled.