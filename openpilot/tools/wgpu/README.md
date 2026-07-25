# Wireless modeld proof of concept

This runs driving `modeld` on a laptop and returns its cereal outputs to a comma
device over the existing Wi-Fi network. It reuses the existing HEVC camera
stream, VisionIPC decoder, and cereal ZMQ bridge.

This is for controlled bench testing only. Wi-Fi has no deterministic latency
or availability guarantee. Local `modeld` remains warm during a WGPU session;
the device-side helper switches only after receiving a fresh remote model and
restores local publication if the remote model is missing for 350 ms.

## Build

Use the same commit on the laptop and comma device. Build the cereal bridge on
the device:

```sh
scons -u openpilot/cereal/messaging/bridge
```

Build and test the normal model on the laptop first:

```sh
PATH="$PWD/.venv/bin:$PATH" scons -u
```

To compile the big external-GPU model for the laptop's local tinygrad backend:

```sh
PATH="$PWD/.venv/bin:$PATH" WGPU=1 scons -u \
  openpilot/selfdrive/modeld/models/big_driving_tinygrad.pkl.chunkmanifest
```

On macOS, the build selects tinygrad's Metal backend when it is available.
On an 8-GPU-core M5 MacBook Air, the small model's compiled policy pass measured
about 6–11 ms, while the big model measured about 79–81 ms. The latter already
misses the 50 ms model cadence before network and codec latency, so start with
the small model on that class of laptop.

## Run

Find the laptop's LAN IP address that the comma device can reach. The helper can
start while onroad: it forwards camera/state while local `modeld` remains active,
then switches publication after the laptop produces a fresh valid model:

```sh
cd /data/openpilot
python3 -m openpilot.tools.wgpu.device LAPTOP_IP
```

Keep that terminal open. On the laptop, run:

```sh
cd /path/to/openpilot
python3 -m openpilot.tools.wgpu.host COMMA_IP
```

Add `--big-model` after `COMMA_IP` to use the locally compiled big model.

The first remote `carParams` packet can take up to 50 seconds. Stop either side
with Ctrl+C. A host disconnect automatically restores the warm local publisher
after a 350 ms timeout. Stop the device helper before changing branches or
rebooting.

For stationary bench testing only, model lag can be changed from a blocking
event to a live warning showing model age and dropped frames. After ignition is
on and manager is running, enable the temporary override on the device:

```sh
cd /data/openpilot
python3 -c 'from openpilot.common.params import Params; Params().put_bool("WgpuBenchMode", True)'
```

The override requires `WgpuEnabled` and clears on manager restart or the next
ignition-on transition. Disable it immediately with:

```sh
cd /data/openpilot
python3 -c 'from openpilot.common.params import Params; Params().remove("WgpuBenchMode")'
```
