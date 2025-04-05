# :satellite: Radar Tracks

Unlock the potential of sunnypilot by enabling radar tracks manually on applicable Hyundai/Kia/Genesis cars. Thanks to
[@greghogan](https://github.com/greghogan) and [@pd0wm](https://github.com/pd0wm), this feature is now accessible via SSH.

!!! info "How Radar Points Can Be Used Along With Vision"
    Current openpilot policy is to identify with vision first and match it to a radar point. If vision sees nothing,
    you get a false negative and no lead car detection. (Source: [Hubblesphere#7894 from comma.ai community Discord](https://discord.com/channels/469524606043160576/872899198738104330/872913890793635872))

!!! caution
    **USE AT YOUR OWN RISK!** Stock system safety features, such as AEB and FCW, may be affected by these changes.

## 1. Prerequisites

Ensure the car is in the `OFF` ignition position and connect your comma 3/3X to the car.

## 2. SSH connection

Connect to your comma 3/3X via [SSH](https://github.com/commaai/openpilot/wiki/SSH).

## 3. Execute commands

In the SSH terminal, execute the following commands:

```bash
pkill -f openpilot
python /data/openpilot/selfdrive/debug/hyundai_enable_radar_points.py
```
Follow the script instructions and ensure no faults appear.

## 4. Reboot

Reboot your comma 3/3X. Once rebotoed, start your car and ensure there is no fault caused by enabling the radar tracks.

## 5. Test drive

Go for a quick drive, drive behind a lead car, and allow the drive to upload its raw logs in [comma Connect](https://connect.comma.ai).

## 6. Verify in Cabana

Load the test route in [Cabana](https://github.com/sunnypilot/sunnypilot/tree/master/tools/cabana), load `hyundai_kia_mando_front_radar.dbc`, search `RADAR_TRACK_50x`,
and check `LONG_DIST`.

## 7. Confirmation

If the radar tracks data is relevant, you've successfully enabled radar tracks.

!!! tip
    Having issues or need assistance? Reach out to the community in the `hyundai-kia-genesis` channel in
    [sunnypilot Discord](https://discord.sunnypilot.ai) or [commaai community Discord](https://discord.comma.ai).
