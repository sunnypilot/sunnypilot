# Live UI

View a comma device's live sunnypilot UI over Wi-Fi. Replay, ADB, and USB are
not used.

| Mode | Output | Device bridge |
| --- | --- | --- |
| Mimic (default) | Local UI rendered from live device data | Required |
| Exact (`--exact`) | Actual pixels shown on the device | Not required |

Mimic mode does not directly require SSH, but the device bridge must be started
somehow; the examples use SSH. Exact mode, touch control, and `--stop-exact`
require key-based SSH access.

Choose **mimic** when developing or inspecting the local UI with live device
data. Choose **exact** when you need to see or control what is physically shown
on the device.

## Before the first run

1. Replace `192.168.43.1` in the examples if your device uses a different IP.
2. Connect the computer and device to networks that can reach each other.
3. Run local commands from the sunnypilot repository root.
4. For exact mode, verify non-interactive SSH access:

   ```bash
   ssh -o BatchMode=yes comma@192.168.43.1 true
   ```

The script automatically switches to the repository's `.venv` when present.

## Mimic UI

Mimic mode receives live cereal messages and encoded road-camera frames, then
renders a new UI instance on the computer. It resembles the device UI but is
not a pixel-for-pixel screen mirror.

Build the messaging bridge once on the computer:

```bash
scons -u cereal/messaging/bridge
```

Use two terminals. In the first, start the bridge on the device and leave it
running:

```bash
ssh comma@192.168.43.1
./cereal/messaging/bridge
```

In the second terminal, start the local UI:

```bash
BIG=0 ./openpilot/tools/live/ui.py 192.168.43.1
```

`BIG` is inherited from your environment and is not forced by the tool.

## Exact device screen

Exact mode streams the actual device display. It does not need either
messaging bridge:

```bash
./openpilot/tools/live/ui.py --exact 192.168.43.1
```

The tool runs a temporary capture helper through SSH using AGNOS's existing
DRM broker. It does not install software or modify openpilot source on the
device. Exact mode requires a compatible AGNOS DRM writeback connector and
captures the post-processed display output when that mode is available.

Exact mode is experimental. Some Qualcomm/AGNOS combinations can time out
during DRM writeback, freezing both the mirrored window and physical device UI.
This can happen without `--control`; mouse, keyboard, and shortcut forwarding
are not required to trigger the capture failure.
The tool stops its verified helper when capture stalls, but the kernel display
state may require a full device reboot before exact mode can be tried again.
Restarting openpilot alone does not reset the display driver.

Set the capture rate from 1 to 60 FPS; the default is 15:

```bash
./openpilot/tools/live/ui.py --exact --exact-fps 30 192.168.43.1
./openpilot/tools/live/ui.py --exact --exact-fps 60 192.168.43.1
```

Start with 15 or 30 FPS. Higher rates use more device CPU and Wi-Fi bandwidth.

Use `SCALE` to resize the local window:

```bash
SCALE=2 ./openpilot/tools/live/ui.py --exact 192.168.43.1
```

Only one exact session can run at a time.

## Touch control

Touch control is available only with exact mode:

```bash
./openpilot/tools/live/ui.py --exact --control 192.168.43.1
```

Left-clicks and drags are forwarded to the physical touchscreen over SSH.
These inputs affect the real device, including settings and confirmation
buttons.

When the device's on-screen keyboard is visible, type with the computer
keyboard. Letters, numbers, symbols, Space, Backspace, and Return are converted
to taps on the device keyboard.

Exact control also provides simulator-style shortcuts:

| Shortcut | Action |
| --- | --- |
| `↓` | Go back with a swipe-down gesture |
| `←` | Swipe right |
| `→` | Swipe left |
| `Command`+`K` (macOS) or `Ctrl`+`K` (Linux/Windows) | Force keyboard forwarding on, or return to automatic detection |

Hold an arrow key to repeat its gesture until the key is released.

Escape has no action and does not close the program; use `Ctrl-C` or the window
close button to exit. `Command`+`K`/`Ctrl`+`K` enables manual keyboard forwarding
regardless of exact-screen resolution; touch locations scale to the captured
screen. Automatic keyboard detection targets the 536x240 mici UI. Turn forced
forwarding back off after typing so ordinary keys cannot produce unintended
taps on incompatible keyboard layouts.

## Connection status

Status appears in the window title and terminal:

- `connected`: mimic telemetry and camera frames, or exact screen frames, are
  arriving.
- `keyboard`: exact-mode keyboard forwarding is currently active. This appears
  only while the device keyboard is detected or forwarding is forced on.
- `no camera`: mimic telemetry is arriving, but road-camera frames are not.
- `disconnected`: expected mimic-mode live data has stopped.

At the default capture rate, exact mode reports a stopped screen stream in
about one second. Lower `--exact-fps` values allow more time between frames.
If Qualcomm DRM writeback stalls, exact mode immediately stops its verified
device helper and exits to avoid leaving the physical display frozen.

## Stop and clean up

Press `Ctrl-C` or close the window. If an exact helper remains orphaned, run:

```bash
./openpilot/tools/live/ui.py --stop-exact 192.168.43.1
```

`--kill-exact` is an alias. Stop exact mode before restarting or rebuilding
openpilot to avoid blocking the physical UI during a display transition.

## Options

```text
--exact                 Show the actual device screen
--control               Forward mouse and keyboard input; requires --exact
--exact-fps FPS         Exact capture rate, 1-60 (default: 15)
--stop-exact            Stop orphaned exact helpers
--kill-exact            Alias for --stop-exact
--ip ADDRESS            Alternative to the positional address
```

See the complete command help:

```bash
./openpilot/tools/live/ui.py --help
```

## Troubleshooting

- **`cereal/messaging/bridge` is not built:** Run:

  ```bash
  scons -u cereal/messaging/bridge
  ```

- **Mimic is disconnected:** Confirm the device bridge is still running and
  the IP is reachable.
- **Mimic reports no camera:** Confirm the device is publishing
  `roadEncodeData`. Camera display may also wait briefly for the next keyframe.
- **Exact says another session is running:** Close the other exact window. If
  none is open, run `--stop-exact`.
- **Exact cannot connect:** Recheck key-based SSH and the device IP using the
  command in "Before the first run."
- **Exact stalls or the physical UI freezes:** Stop the exact window and run
  `--stop-exact`. If the device UI remains unstable or exact immediately stalls
  again, fully reboot the device; restarting openpilot is not sufficient. If
  the problem returns after reboot, use mimic mode because continuous DRM
  writeback is not reliable on that device/AGNOS combination. Removing
  `--control` does not address this capture-layer failure.
