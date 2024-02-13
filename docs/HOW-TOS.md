# How Tos
This page is a repository of useful how-tos as a supplement for additional information.

Table of Contents
=======================

* [Radar Tracks](#Radar-Tracks)
    * [Enable Radar Tracks](#-Enable-Radar-Tracks)
* [Enable Mapbox Navigation](#-Enable-Mapbox-Navigation)

---

<details><summary><h3>📡 Radar Tracks</h3></summary>

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

### 🚨 Enable Radar Tracks

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
</details>

<details><summary><h3>🗺 Enable Mapbox Navigation</h3></summary>

1) Create a free mapbox account. Account will ask for a credit card for verification. You will not be charged for the free tier.
2) On the Dashboard, you will see a section called Access Tokens. Click `Create a Token`. Name it whatever you like. Set the scopes to allow everything for both Public and Secret. Copy both of these keys. **YOU WON'T BE ABLE TO ACCESS THE SECRET KEY AFTER THIS WINDOW.**
3) Once rebooted, connect your C3 to a network with internet access and find the C3’s IP address.
4) In a browser, navigate to that IP with **port 8082** (i.e 192.168.1.69:8082). You should be greeted with the Comma logo and a public key input field.
5) Paste your Public token (pk.xx), click enter, paste your Secret key (sk.xx), click enter. You can now search for places. This page will be available at your devices’s IP address/port 8082 to search for destinations.
6) To set Home and Work addresses, search for a place, select Home/Work from the dropdown and click Navigate. For non-Home/Work destinations, select Recent Places.<br>*At this time, it is not possible to search directly on the C3.*

**TIPS:**
- If your C3 is showing a black screen that says “Map Loading”, performing a reboot via the UI should fix it.
- If your phone can create a Hotspot, you are able to connect the C3 to your phone hotspot and use your phone browser to search for places.
- In the Navigation panel on the C3, you can select Home, Work, and from a list of Recent Places you have navigated to without needing a browser (assuming the C3 is connected to the internet.)

**IMPORTANT NOTE:** Your C3 will require an active internet connection to download map data, generate driving directions, and ETA. Once map data and directions are downloaded, it *is* possible to use it offline, however nothing will update (such as new driving direction after a missed turn, updated ETA, map data further into your drive etc.)

***NAVIGATION NOTE:** At this time, mapbox does not support alphanumeric addresses (i.e W123N1234 Main St). There is currently no known workaround for this.*
</details>
