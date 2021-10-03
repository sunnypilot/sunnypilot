#Introduction
This page is a repository of useful how-tos as a supplement for additional information.

Table of Contents
=======================

* Enable Radar Tracks

##Enable Radar Tracks
(Last updated date: October 3rd, 2021)

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

To enable radar tracks:
(Instructions are base on `master` on 0.8.10 `d546c109ef4854322bfaea12954ad854d593554c`)
1. Ensure the car is at the `OFF` ignition position.
2. Connect your compatible comma device (EON, C2, C3) to the car. Power should be on.
3. Use a laptop or applicable device to connect to your comma device via SSH. (Tips: Instructions to SSH in [HERE](https://github.com/commaai/openpilot/wiki/SSH))
4. In the SSH terminal after successfully connected to your comma device, execute the following commands:
    i. ```killall boardd```