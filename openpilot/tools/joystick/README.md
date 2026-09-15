# Joystick

**Hardware needed**: device running openpilot, laptop, joystick (optional)

With joystick_control, you can connect your laptop to your comma device over the network and debug controls using a joystick or keyboard.
joystick_control uses [inputs](https://pypi.org/project/inputs) which supports many common gamepads and joysticks.

## Usage

The car must be off, and openpilot must be offroad before starting `joystick_control`.

### Using a keyboard

SSH into your comma device and start joystick_control with the following command:

```shell
openpilot/tools/joystick/joystick_control.py --keyboard
```

The available buttons and axes will print showing their key mappings. In general, the WASD keys control gas and brakes and steering torque in 5% increments.

Keep this terminal running when you start the car. The automatic onroad gamepad process waits while this local input tool is running; a second manual instance exits without replacing it. Stop the tool with `Ctrl+C` before starting another instance. Starting the tool enables `JoystickDebugMode` automatically. To disable the mode, go offroad, stop the tool, and turn off **Joystick Debug Mode** in Settings.

### Ford C0 / C1 independently

Use the existing **Settings → Developer → Joystick Debug Mode** toggle, while offroad. On a CAN FD Ford, start the existing keyboard tool with an explicit channel:

```shell
python openpilot/tools/joystick/joystick_control.py --keyboard --ford-channel c0
```

`1` selects C0 only, `2` selects C1 only, and `0` returns to standard joystick steering. Switching zeros the steering axis. The comma screen shows **Joystick Mode — C0 only** or **C1 only**, the commanded field value, and measured wheel angle. The terminal also names the selected channel.

`A`/`D` retain their normal 5% steering-axis increments. Full scale directly commands ±5.11 metres of C0 or ±0.5 radians of C1; one increment is approximately 0.26 m or 0.025 rad. The other path fields, including C2/C3, are zero. `R` resets the axes. Gas/brake keys and joystick engagement remain unchanged. With a gamepad, use the same `--ford-channel` option without `--keyboard`.

There is no target-speed check or timed waveform. This includes zero speed if normal joystick engagement and the vehicle permit it. These are direct field commands, not desired wheel angles or the model-following controller's formulas. No MADS engagement or brake behavior is added. The existing hardware safety checks remain in force.

Start with the steering axis centered. After a channel change, disengagement, or lost/invalid input, the receiver requires a fresh centered input before applying another command. A lost joystick stream removes the Ford steering request after the existing 0.2 s timeout; a held nonzero command cannot restart on reconnection. `R` resets commands; it does not disengage joystick mode.

Without `--ford-channel`, the original keyboard/gamepad behavior remains the default. The normal lateral maneuver tools are unchanged.

### Joystick on your comma three

Plug the joystick into your comma three aux USB-C port. Then, SSH into the device and start `joystick_control.py`.

### Joystick on your laptop

In order to use a joystick over the network, we need to run joystick_control locally from your laptop and have it send `testJoystick` packets over the network to the comma device.

1. Connect a joystick to your PC.
2. Connect your laptop to your comma device's hotspot and open a new SSH shell. Since joystick_control is being run on your laptop, we need to write a parameter to let controlsd know to start in joystick debug mode:
   ```shell
   # on your comma device
   echo -n "1" > /data/params/d/JoystickDebugMode
   ```
3. Run bridge with your laptop's IP address. This republishes the `testJoystick` packets sent from your laptop so that openpilot can receive them:
   ```shell
   # on your comma device
   openpilot/cereal/messaging/bridge {LAPTOP_IP} testJoystick
   ```
4. Start joystick_control on your laptop in ZMQ mode.
   ```shell
   # on your laptop
   export ZMQ=1
   openpilot/tools/joystick/joystick_control.py
   ```

---
Now start your car and openpilot should go into joystick mode with an alert on startup! The status of the axes will display on the alert, while button statuses print in the shell.

Make sure the conditions are met in the panda to allow controls (e.g. cruise control engaged). You can also make a modification to the panda code to always allow controls.

![](https://github.com/commaai/openpilot/assets/8762862/e640cbca-cb7a-4dcb-abce-b23b036ad8e7)
