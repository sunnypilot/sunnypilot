# How Tos
This page is a repository of useful how-tos as a supplement for additional information.

Table of Contents
=======================

* [Radar Tracks](#Radar-Tracks)
    * [Enable Radar Tracks](#-Enable-Radar-Tracks-)
* [Enable openpilot Longitudinal Control](#-Enable-openpilot-Longitudinal-Control-)

---

## Radar Tracks

Radar tracks can now be enabled manually on applicable cars through SSH thanks to [@greghogan](https://github.com/greghogan) and [@pd0wm](https://github.com/pd0wm).

Some Hyundai radars can be reconfigured to output (debug) radar points on bus 1.
Reconfiguration is done over UDS by reading/writing to 0x0142 using the Read/Write Data By Identifier
endpoints (0x22 & 0x2E). This script checks your radar firmware version against a list of known
firmware versions. If you want to try on a new radar, make sure to note the default config value
in case it is different from the other radars and you need to revert the changes.
After changing the config the car should not show any faults when openpilot is not running.
These config changes are persistent across car reboots. You need to run this script again
to go back to the default values.

**USE AT YOUR OWN RISK!** Stock system safety features, like AEB and FCW, might be affected by these changes.

**How radar points can be used along with vision:**
* Current OP long policy is identify with vision first, if vision sees a vehicle match it to a radar point. If vision sees nothing you get a false negative and no lead car detection. (Source: [Hubblesphere#7894 from comma.ai community Discord](https://discord.com/channels/469524606043160576/872899198738104330/872913890793635872))

### 🚨 Enable Radar Tracks 🚨

***(EXPERIMENTAL, as of January 1st, 2022)***

***(Only applicable to some Hyundai, Kia, and Genesis cars, as of January 1st, 2022)***

*(Base on version 0.8.12 [`devel`](https://github.com/commaai/openpilot/tree/devel))*

**USE AT YOUR OWN RISK!** Stock system safety features, like AEB and FCW, might be affected by these changes.

1. Ensure the car is at the `OFF` ignition position.
2. Connect your compatible comma device (EON, C2, C3) to the car. comma device power should be ON.
3. Use a laptop or applicable device to connect to your comma device via SSH. (Tips: Instructions to SSH in [HERE](https://github.com/commaai/openpilot/wiki/SSH))
4. In the SSH terminal after successfully connected to your comma device, execute the following commands:
    1. `pkill -f openpilot`
    2. `python /data/openpilot/selfdrive/debug/hyundai_enable_radar_points.py`
    3. Follow the instructions in the script:
       * `Power on the vehicle keeping the engine off (press start button twice) then type OK to continue`.
           * If successful, the following message should appear: `[DONE]. Restart your vehicle and ensure there are no faults`.
           * If the script did not run successfully, reach out to the community in [Sunnyhaibin's Openpilot Discord Server](https://discord.gg/wRW3meAgtx) or `#hyundai-kia-genesis channel` on [commaai community Discord Server](https://discord.comma.ai) for assistance.
    4. Reboot your comma device:
        1. C3: `sudo reboot`
        2. C2 or EON: `reboot`
5. Once your comma device is rebooted, start your car with engine on (with or without comma device connected). Ensure that there are no faults from the car. If there are faults, reach out to the community in [Sunnyhaibin's Openpilot Discord Server](https://discord.gg/wRW3meAgtx) or `#hyundai-kia-genesis channel` on [commaai community Discord Server](https://discord.comma.ai) for assistance.
6. Go for a quick drive and drive behind a lead car with varied follow distance. Then, come back and allow the drive to upload its `rlogs` in [comma Connect](https://connect.comma.ai).
7. With all `rlogs` uploaded, open the drive in Cabana from [comma Connect](https://connect.comma.ai). Load DBC -> `hyundai_kia_mando_front_radar.dbc`, then search `RADAR_TRACK_50x` (`x` could be anything), open any of them, and look at `LONG_DIST`.
8. If the radar tracks data is relevant with the lead car you drove behind, you are done! Your car now have radar tracks enabled.

### 🚨 Enable openpilot Longitudinal Control 🚨

***(EXPERIMENTAL, as of January 9th, 2022)***

*(Base on version 0.8.12 [`devel`](https://github.com/commaai/openpilot/tree/devel))*

**USE AT YOUR OWN RISK!** Stock system safety features, like AEB and FCW, might be affected by these changes.

1. Connect your compatible comma device (EON, C2, C3) to the car. comma device power should be ON.
    * (Note: If doing this in the car, ensure the car is at the `OFF` ignition position.)
2. Use a laptop or applicable device to connect to your comma device via SSH. (Tips: Instructions to SSH in [HERE](https://github.com/commaai/openpilot/wiki/SSH))
3. In the SSH terminal after successfully connected to your comma device, execute the following commands:
    1. ```echo -n "1" > /data/params/d/DisableRadar_Allow```
        * Note: It will automatically create the file `DisableRadar_Allow` under `/data/params/d` after executing the command.
    2. Reboot your comma device:
        1. C3: `sudo reboot`
        2. C2 or EON: `reboot`
4. Once your comma device is rebooted, a new toggle should appear:
---
            .
            └── Settings
                └── Toggles
                    └── ***openpilot Longitudinal Control***

5. Set the toggle `openpilot Longitudinal Control` to `ON`. (Note: If this step is done while the car is at the `ON` ignition position, turn off the car to take the change in effect.)
6. Start the car. Drive and check for the following:
   1. Is there a chevron (triangle) appear behind a lead car?
   2. Are you able to engage openpilot with no fault?
   3. (Optional, PROCEED WITH EXTREME CAUTION AND BE READY TO MANUALLY TAKE OVER AT ALL TIMES) With the car engaged with openpilot and cruising at or below `35 MPH` or `56 KM/H` in good road conditions, is your car able to detect and slow down / stop behind a stopped car?
7. If you answered `YES` to all the above questions in Step 6, you have successfully enabled openpilot Longitudinal Control.

❗Note❗: Some Hyundai/Kia/Genesis car models may not see the chevron behind a lead car after enabling `openpilot Longitudinal Control`. This could cause by the affected car models being listed in the `LEGACY_SAFETY_MODE_CAR` blacklist in `selfdrive/car/hyundai/values.py` and openpilot Longitudinal Control may not have been tested/confirmed by comma or the community.
* If you would like to test whether openpilot Longitudinal Control would work for your car model, ensure that your car model is removed from the blacklist in the following statement in `selfdrive/car/hyundai/values.py`:
```
    ## As of January 9th, 2022 ##
    LEGACY_SAFETY_MODE_CAR = set([CAR.HYUNDAI_GENESIS, CAR.IONIQ_EV_2020, CAR.IONIQ_EV_LTD, CAR.IONIQ_PHEV, CAR.IONIQ, CAR.KONA_EV, CAR.KIA_SORENTO, CAR.SONATA_LF, CAR.KIA_NIRO_EV, CAR.KIA_OPTIMA, CAR.VELOSTER, CAR.KIA_STINGER, CAR.GENESIS_G70, CAR.GENESIS_G80, CAR.KIA_CEED, CAR.ELANTRA, CAR.IONIQ_HEV_2022])
```
