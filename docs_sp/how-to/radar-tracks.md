---
title: 📡 Radar Tracks
---

Unlock the potential of your sunnypilot 🚗 by enabling Radar Tracks manually on applicable cars. Thanks to [@greghogan](https://github.com/greghogan) and [@pd0wm](https://github.com/pd0wm), this feature is now accessible through SSH.

:::info
**How Radar Points Can Be Used Along With Vision:**  
Current Openpilot policy is to identify with vision first and match it to a radar point. If vision sees nothing, you get a false negative and no lead car detection. (Source: [Hubblesphere#7894 from comma.ai community Discord](https://discord.com/channels/469524606043160576/872899198738104330/872913890793635872))
:::

### 🚨 Enable Radar Tracks (Experimental)

***(As of January 1st, 2022)***  
***(Applicable to some Hyundai, Kia, and Genesis cars)***  
***(Based on version 0.8.12 [`devel`](https://github.com/commaai/openpilot/tree/devel))***

:::caution
**USE AT YOUR OWN RISK!** Stock system safety features, like AEB and FCW, might be affected by these changes.
:::

#### **Steps to Enable Radar Tracks:**
1. **Preparation**:  
   Ensure the car is in the `OFF` ignition position and connect your compatible comma device (EON, C2, C3) to the car.

2. **SSH Connection**:  
   Connect to your comma device via SSH. (Instructions [HERE](https://github.com/commaai/openpilot/wiki/SSH))

3. **Execute Commands**:  
   In the SSH terminal, execute the following commands:
   ```bash
   pkill -f openpilot
   python /data/openpilot/selfdrive/debug/hyundai_enable_radar_points.py
   ```
   Follow the script instructions and ensure no faults appear.

4. **Reboot**:  
   Reboot your comma device and start your car ensuring no faults.

5. **Test Drive**:  
   Go for a quick drive, drive behind a lead car, and allow the drive to upload its `rlogs` in [comma Connect](https://connect.comma.ai).

6. **Verify in Cabana**:  
   Open the drive in Cabana from [comma Connect](https://connect.comma.ai), load `hyundai_kia_mando_front_radar.dbc`, search `RADAR_TRACK_50x`, and check `LONG_DIST`.

7. **Confirmation**:  
   If the radar tracks data is relevant, you've successfully enabled radar tracks.

:::tip
Having issues or need assistance? Reach out to the community in [Sunnyhaibin's Openpilot Discord Server](https://discord.gg/wRW3meAgtx) or `#hyundai-kia-genesis channel` on [commaai community Discord Server](https://discord.comma.ai).
:::
